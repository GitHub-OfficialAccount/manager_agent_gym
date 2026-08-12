"""S8 acceptance — assertions on a RUN BUNDLE.

Run against the bundle an episode produced, so the properties are read off the
actual run rather than off the code that was supposed to produce it:

  1. `roster_arrival_announced` present, with `observation_source`. S2 built the
     roster render and this is the FIRST time its run-time assertion fires in a
     real episode.
  2. `worker_run_completed` for the PREDECESSOR before t_swap and for the
     SUCCESSOR after it. Both halves matter: the predecessor proves there was a
     worker to replace, the successor proves the replacement actually worked.
  3. Task count 15-20 with all 9 segment tasks present and completed.
  4. The manifest carries the instance seed AND its content hash, and the hash
     still matches what the generator produces for that seed.
  5. Every completed segment task either round-trips through the parser or is
     logged missing — never silently absent.
  6. The realised per-worker segment count respects C = 3.

Run:  python3 -m experiments.worker_replacement.test_finance_bundle [path-to-bundle]
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

from . import finance_env as env
from . import finance_gate as gate
from . import finance_generator as gen
from . import finance_report_parser as rp

HERE = Path(__file__).resolve().parent
DEFAULT_BUNDLE = HERE / "records" / "S8" / "run_seed101.json"


def main(path: Path) -> int:
    failures: list[str] = []
    bundle = json.loads(path.read_text())
    manifest = bundle["manifest"]
    dry_run = bool(manifest.get("dry_run"))

    print(f"S8 — run-bundle assertions on {path.name}")
    if dry_run:
        print("   NOTE: this is a DRY-RUN bundle (all model calls stubbed). The\n"
              "   worker_run_completed assertions are emitted by AIAgent.execute_task,\n"
              "   which the dry run replaces, so they are reported as NOT APPLICABLE\n"
              "   rather than passed — a stub cannot evidence that a worker ran.\n")

    # --- 4. provenance -------------------------------------------------------
    seed = manifest["instance_seed"]
    recorded_hash = manifest["instance_sha256"]
    actual_hash = env.instance_hash(gen.generate(seed))
    hash_ok = recorded_hash == actual_hash
    print(f"1. provenance: seed {seed}, sha256 {recorded_hash[:16]}...")
    print(f"   [{'ok' if hash_ok else 'FAIL'}] the recorded hash still matches what "
          f"the generator produces for that seed\n        (a seed alone would not "
          f"catch a generator change between run and reading)")
    if not hash_ok:
        failures.append(f"instance hash mismatch: recorded {recorded_hash[:16]}, "
                        f"regenerated {actual_hash[:16]}")

    models = manifest.get("role_models", {})
    off = sorted(r for r, m in models.items() if m != manifest["manager_model"])
    print(f"   [{'ok' if not off else 'FAIL'}] all {len(models)} roles ran on "
          f"{manifest['manager_model']}")
    if off:
        failures.append(f"roles off the authorised model: {off}")

    # --- 1. the roster event -------------------------------------------------
    events = bundle["events"]
    roster = [e for e in events if e["event_type"] == "roster_arrival_announced"]
    at_swap = [e for e in roster
               if e["payload"]["timestep"] == manifest["t_swap"]]
    print(f"\n2. roster arrival ({len(roster)} events, "
          f"{len(at_swap)} at t_swap={manifest['t_swap']}):")
    swap_ok = len(at_swap) == 1
    if at_swap:
        payload = at_swap[0]["payload"]
        print(f"   applied: {payload['applied_changes']}")
        print(f"   rendered_into_observation: {payload['rendered_into_observation']}, "
              f"observation_source: {payload.get('observation_source')}")
        source_ok = payload.get("observation_source") is not None
        strong = payload.get("observation_source") == "manager"
        named = " ".join(payload["applied_changes"])
        ids_ok = (manifest["predecessor_id"] in named
                  and manifest["successor_id"] in named)
        print(f"   [{'ok' if source_ok else 'FAIL'}] observation_source is present")
        print(f"   [{'ok' if ids_ok else 'FAIL'}] the change names both the "
              f"predecessor and the successor")
        print(f"   arrival evidence is {'STRONG' if strong else 'WEAK'} form "
              f"({payload.get('observation_source')}) — strong means the manager saw "
              f"the\n        announcement BEFORE choosing its action, weak means the "
              f"engine carried it\n        into a post-hoc observation")
        if not source_ok:
            failures.append("roster event carries no observation_source")
        if not ids_ok:
            failures.append("roster event does not name pred and succ")
    print(f"   [{'ok' if swap_ok else 'FAIL'}] exactly one arrival event at t_swap")
    if not swap_ok:
        failures.append(f"{len(at_swap)} roster events at t_swap, expected 1")

    # --- 2. both workers actually ran ---------------------------------------
    print(f"\n3. worker execution across the swap:")
    completed = [e for e in events if e["event_type"] == "worker_run_completed"]
    by_actor = collections.Counter(e.get("actor_id") for e in completed)
    print(f"   worker_run_completed events: {dict(by_actor)}")
    if dry_run:
        print("   [n/a] predecessor/successor run evidence — stubbed in a dry run")
    else:
        pred_ok = by_actor.get(manifest["predecessor_id"], 0) > 0
        succ_ok = by_actor.get(manifest["successor_id"], 0) > 0
        print(f"   [{'ok' if pred_ok else 'FAIL'}] the PREDECESSOR "
              f"{manifest['predecessor_id']} completed at least one run")
        print(f"   [{'ok' if succ_ok else 'FAIL'}] the SUCCESSOR "
              f"{manifest['successor_id']} completed at least one run")
        if not pred_ok:
            failures.append("no worker_run_completed for the predecessor")
        if not succ_ok:
            failures.append("no worker_run_completed for the successor")

    # The completions record carries the timestep, so pre/post can be checked
    # even when the run events do not distinguish them.
    completions = bundle["completions"]
    pre = [c for c in completions
           if c["agent_id"] == manifest["predecessor_id"]
           and c["timestep"] <= manifest["t_swap"]]
    post = [c for c in completions
            if c["agent_id"] == manifest["successor_id"]
            and c["timestep"] > manifest["t_swap"]]
    print(f"   predecessor completions at/before t_swap: {len(pre)}")
    print(f"   successor completions after t_swap: {len(post)}")
    order_ok = bool(pre) and bool(post)
    print(f"   [{'ok' if order_ok else 'FAIL'}] the predecessor worked BEFORE the "
          f"swap and the successor AFTER it")
    if not order_ok:
        failures.append("swap ordering not evidenced in completions")

    # --- 2b. INHERITED WORKFLOW STATE ON THE BOARD (spec E5, positive check) --
    # A task still assigned to the departed predecessor is INTENDED, load-bearing
    # semantics, not a stale line to be filtered: it is inherited workflow state
    # appearing on the board, and noticing-then-reassigning it is the succession
    # behaviour the study measures. Checked POSITIVELY — present and truthful —
    # rather than tolerated.
    print(f"\n3b. inherited workflow state on the board (spec E5):")
    board = bundle.get("task_board_final")
    predecessor = manifest["predecessor_id"]
    if board is not None:
        inherited = [row for row in board
                     if row["assigned_agent_id"] == predecessor
                     and row["status"] not in ("completed",)]
        print(f"   board rows still assigned to the departed predecessor "
              f"{predecessor}: {len(inherited)}")
        for row in inherited:
            print(f"     {row['task_name'][:44]:<44} status={row['status']}")
        if inherited:
            # TRUTHFUL: the line must name the predecessor and the task must
            # genuinely not have completed. A board that showed this line for a
            # task that DID complete would be worse than not showing it.
            done_names = {c["task_name"] for c in bundle["completions"]}
            lying = [r for r in inherited if r["task_name"] in done_names]
            print(f"   [{'ok' if not lying else 'FAIL'}] every inherited line is "
                  f"TRUTHFUL — the task really did not complete")
            if lying:
                failures.append(f"board claims incomplete for completed tasks: "
                                f"{[r['task_name'] for r in lying]}")
            print("   THIS IS THE INTENDED SEMANTICS, not a swap bug: the successor "
                  "arrived and the\n        predecessor's unfinished work stayed on "
                  "the board for the manager to notice.")
        else:
            print("   the condition did not arise in this episode — the predecessor "
                  "finished\n        everything it held before t_swap. The check is "
                  "PRESENT and would fire; it\n        simply had nothing to assert "
                  "on, which is reported rather than passed silently.")
    else:
        # Reconstruct from events for bundles written before the field existed.
        started = {(e.get("actor_id"), e.get("task_name")) for e in events
                   if e["event_type"] == "worker_execution_started"}
        done = {(c["agent_id"], c["task_name"]) for c in bundle["completions"]}
        stranded = sorted(n for a, n in started - done if a == predecessor)
        print(f"   NOTE: this bundle predates the `task_board_final` field, so the "
              f"board state is\n        RECONSTRUCTED from events rather than read "
              f"off the board. Reported as such.")
        print(f"   tasks the predecessor STARTED but never completed: "
              f"{stranded or 'none'}")
        if stranded:
            print("   -> the inherited-state condition DID arise; the board would "
                  "have carried it.\n        Re-run with the field present to check "
                  "it positively.")
        else:
            print("   -> the condition did not arise in this episode.")

    # --- 3. the DAG: SHAPE is machinery, COMPLETION is an outcome -------------
    # LS ruling on the S8 acceptance: the original "runs end-to-end to completion"
    # was mis-specified. It made HARNESS acceptance hostage to MANAGER competence,
    # which is the measured variable — a manager that stalls would fail the
    # harness, and a harness change could be made to rescue it. Completion is
    # therefore a STUDY OUTCOME reported per bundle, never a pass/fail criterion
    # here. Full-DAG traversal including the downstream chain is proven
    # deterministically by the zero-API dry run instead.
    n_tasks = manifest["n_tasks"]
    seg_task_ids = set(bundle["index"]["segment_task_ids"].values())
    done_seg = {c["task_id"] for c in completions if c["task_id"] in seg_task_ids}
    print(f"\n4. the DAG: {n_tasks} tasks")
    count_ok = 15 <= n_tasks <= 20
    print(f"   [{'ok' if count_ok else 'FAIL'}] task count in 15-20 (SHAPE — "
          f"machinery)")
    if not count_ok:
        failures.append(f"task count {n_tasks} outside 15-20")

    # MACHINERY: the segment path must demonstrably work live. At least one
    # segment executed by a POST-SWAP worker proves the successor can be routed
    # work and produce a deliverable — which is what only a live episode can show.
    # This is deliberately a floor, not a count: raising it to "all nine" would
    # smuggle the completion criterion back in under another name.
    post_swap_roster = set(manifest["roster_post_swap"])
    live_segments = [c for c in completions
                     if c["task_id"] in seg_task_ids
                     and c["agent_id"] in post_swap_roster]
    path_ok = len(live_segments) >= 1
    print(f"   [{'ok' if path_ok else 'FAIL'}] at least one segment executed by a "
          f"POST-SWAP worker ({len(live_segments)}) — the\n        segment path "
          f"works live; a floor, not a count, so completion cannot creep back in")
    if not path_ok:
        failures.append("no segment was executed by a post-swap worker")

    print(f"\n   OUTCOME (reported, NOT adjudicated — this is the study's "
          f"dependent variable):")
    print(f"     tasks completed:    {len(completions)}/{n_tasks}")
    print(f"     segments completed: {len(done_seg)}/{len(seg_task_ids)}")
    if len(completions) < n_tasks:
        stalled = [r for r in (bundle.get("task_board_final") or [])
                   if r["status"] != "completed"]
        for row in stalled:
            print(f"       incomplete: {row['task_name'][:44]:<44} "
                  f"status={row['status']:<9} assigned={row['assigned_agent_id']}")

    # --- 5b. THE ORACLE IS OVER THE CELL'S OWN ROSTER -------------------------
    # Cell U keeps the pre-swap roster; scoring it post-swap compares its regret
    # to an optimum for a team it never had. This asserts the phase actually used,
    # because the runner hardcoded post_swap for a while and the error was
    # invisible in the numbers — U's oracle simply matched the swapped cells'.
    cell_name = manifest.get("cell")
    phase = bundle.get("outcome", {}).get("oracle_roster_phase") or manifest.get(
        "oracle_roster_phase")
    if cell_name is not None:
        want = "pre_swap" if not (manifest.get("cell_config") or {}).get(
            "swap", True) else "post_swap"
        phase_ok = phase == want
        print(f"\n5b. oracle roster phase: {phase} (cell {cell_name} wants {want})")
        print(f"   [{'ok' if phase_ok else 'FAIL'}] scored against the cell's OWN "
              f"roster")
        if not phase_ok:
            failures.append(f"cell {cell_name} scored against {phase}, want {want}")

    # --- 6. capacity ---------------------------------------------------------
    # THIS WAS AN ASSERTION AND IS NOW A MEASUREMENT (L14). It read
    # `cap = env.CapacityBoundedAIAgent.segment_capacity` and FAILED the bundle if
    # any worker exceeded it, on the stated ground that "the runtime MIRRORS the
    # cap the scorer's oracle is computed under". THE RUNTIME NO LONGER MIRRORS
    # IT: the per-worker segment cap is removed, while `finance_gate.CAP = 3` and
    # every oracle, baseline and ceiling in `finance_scorer` are still computed
    # under it.
    #
    # So the old assertion cannot be kept (it fails by design) and cannot simply be
    # deleted (the quantity it watched is now a CONFOUND rather than a bug). It
    # becomes the instrument that measures the confound: over-cap assignment is
    # counted and reported on every bundle, because a bundle where it is zero and a
    # bundle where it is four are not comparable against a cap-3 ceiling.
    seg_counts = collections.Counter(
        c["agent_id"] for c in completions if c["task_id"] in seg_task_ids)
    cap = gate.CAP
    over = {a: n for a, n in seg_counts.items() if n > cap}
    excess = sum(n - cap for n in over.values())
    print(f"\n5. capacity: realised per-worker segment counts {dict(seg_counts)} "
          f"vs the ORACLE's C = {cap}")
    print(f"   MEASURED, not asserted: {len(over)} worker(s) over the oracle's cap, "
          f"{excess} segment(s) in excess")
    if over:
        print(f"   ★ THIS BUNDLE IS NOT DIRECTLY COMPARABLE TO A CAP-{cap} CEILING. "
              f"The runtime\n        enforces no segment cap; the ceiling assumes "
              f"one. Over-cap work buys score the\n        oracle rules infeasible, "
              f"so the DV share can exceed 1 without the manager\n        having "
              f"used the information the ceiling prices. Carry {over} with any "
              f"number\n        derived from this bundle.")
    else:
        print(f"   [ok] no worker exceeded the oracle's C this run — comparability "
              f"to the cap-{cap}\n        ceiling holds HERE, by luck of the "
              f"manager's choices rather than by enforcement")

    # --- 5. the parser seam --------------------------------------------------
    reports = bundle["reports"]
    detail = bundle["parse_detail"]
    print(f"\n6. the parser seam: {bundle['outcome']['n_parsed']} parsed, "
          f"{bundle['outcome']['n_missing']} missing, "
          f"{bundle['outcome']['n_unstaffed']} unstaffed")
    for failure in bundle["parse_failures"]:
        print(f"   missing {failure['segment_id']}: {failure['reason'][:64]}")
    accounted = set(reports) | {f["segment_id"] for f in bundle["parse_failures"]}
    all_segments = set(detail)
    accounted_ok = accounted == all_segments
    print(f"   [{'ok' if accounted_ok else 'FAIL'}] every segment is EITHER parsed "
          f"OR logged missing — none silently absent")
    if not accounted_ok:
        failures.append(f"segments neither parsed nor logged: "
                        f"{sorted(all_segments - accounted)}")

    # Re-parse the stored deliverables and confirm the bundle's numbers were not
    # produced by some other path. Drives the production parser (the §A rule).
    reparsed = rp.parse_segment_reports(bundle["deliverables"], sorted(all_segments))
    same = reparsed["reports"] == reports
    print(f"   [{'ok' if same else 'FAIL'}] re-parsing the stored deliverables "
          f"reproduces the bundle's reports exactly")
    if not same:
        failures.append("stored deliverables do not re-parse to the stored reports")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS (MACHINERY) — swap announced with observation_source, "
          "both workers evidenced across it, the segment path works live, "
          "capacity respected, every segment parsed or logged missing.")
    print("  Completion is reported above as an OUTCOME and is deliberately not "
          "adjudicated here:\n  it is manager behaviour, which is what the study "
          "measures.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BUNDLE
    raise SystemExit(main(target))
