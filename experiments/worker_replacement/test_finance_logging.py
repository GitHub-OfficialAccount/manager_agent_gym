"""S9 acceptance — the four logging records, the denominator, and realised scoring.

Each record exists because a specific claim is unrecoverable without it, so each
check here asks whether the claim is actually supported — not merely whether a
dict came back.

The check that matters most is section 1's non-vacuity guard. The first version of
record 1 used GUESSED tool names that no tool has, and reported ZERO pulls on a
bundle containing 32 real tool calls. Zero pulls is not an error message; it is a
finding ("the target never pulled"). A wrong list does not fail, it quietly
answers the research question with a default. So the record is asserted against
the LIVE tool factory, and against a real bundle known to contain pulls.

Run:  python3 -m experiments.worker_replacement.test_finance_logging
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from . import finance_comparability as cmp
from . import finance_generator as gen
from . import finance_logging as flog
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records" / "S9"
BUNDLES = HERE / "records" / "S8"


def main() -> int:
    failures: list[str] = []
    print("S9 — logging records, denominator, realised-authoritative scoring\n")

    live_path = BUNDLES / "run_seed101.json"
    dry_path = BUNDLES / "dry_run_seed101.json"
    live = json.loads(live_path.read_text()) if live_path.exists() else None
    dry = json.loads(dry_path.read_text()) if dry_path.exists() else None
    if live is None or dry is None:
        print("RESULT: FAIL — need both an S8 live and dry-run bundle")
        return 1

    # --- 1. RECORD 1, with the non-vacuity guard -----------------------------
    print("1. record 1 — channel pulls (and the guard against the bug that hid them):")
    pulls = flog.record_channel_pulls(live)
    check = pulls["classification_check"]
    print(f"   live comms tools: {check['live_tools']}")
    print(f"   counted as PULLS: {pulls['tools_counted']}")
    print(f"   counted as pushes (excluded): {pulls['pushes_not_counted']}")
    covers = check["holds"]
    print(f"   [{'ok' if covers else 'FAIL'}] the pull/push classification spans "
          f"every LIVE comms tool (unclassified: "
          f"{check['unclassified_live_tools']})")
    if not covers:
        failures.append(f"tools not classified: {check['unclassified_live_tools']}")

    # NON-VACUITY: this bundle is known to contain communication tool calls, so a
    # zero here means the extractor is broken, not that nobody pulled.
    has_calls = sum(len(v) for v in flog.tool_calls_by_task(live).values())
    print(f"   bundle contains {has_calls} tool calls; extractor found "
          f"{pulls['n_pulls']} pulls, by agent {pulls['pulls_by_agent']}")
    nonvacuous = has_calls > 0 and pulls["n_pulls"] > 0
    print(f"   [{'ok' if nonvacuous else 'FAIL'}] NON-VACUOUS — a bundle with real "
          f"tool calls yields pulls\n        (the earlier guessed-names bug "
          f"produced 0 here and looked like a finding)")
    if not nonvacuous:
        failures.append("record 1 is vacuous on a bundle containing tool calls")

    print(f"   first-pull index by agent: {pulls['first_pull_index_by_agent']} "
          f"— this is what makes the\n        P2 before/after split possible")

    # --- 2. RECORD 2 — refine before/after -----------------------------------
    print("\n2. record 2 — refine events carry BEFORE/AFTER text, not a count:")
    synthetic = copy.deepcopy(dry)
    synthetic["events"] = list(synthetic.get("events", [])) + [{
        "sequence": 9001, "event_type": "task_refined", "actor_type": "manager",
        "payload": {"task_id": "t-1", "task_name": "Risk-weighted assets — seg_00",
                    "description_before": "compute RWA for seg_00",
                    "description_after": "compute RWA for seg_00 using SA"},
    }]
    refined = flog.record_refine_events(synthetic)
    text_ok = (refined["n_refines"] == 1
               and refined["refines"][0]["description_before"] != flog.ABSENT
               and refined["refines"][0]["description_after"] != flog.ABSENT)
    print(f"   [{'ok' if text_ok else 'FAIL'}] a logged refine yields both texts "
          f"— attributable={refined['attributable']}")
    if not text_ok:
        failures.append("refine record did not carry before/after text")

    # A refine visible only as a manager ACTION is UNATTRIBUTABLE and must say so.
    # The committed live bundle is exactly this case: it predates the instrument.
    live_refines = flog.record_refine_events(live)
    # THE LIVE BUNDLE'S STATE DEPENDS ON WHEN IT WAS RUN, so this asserts the
    # PROPERTY rather than a state. Pre-instrument bundles show refine ACTIONS
    # with no text and must be reported unattributable; post-instrument bundles
    # show refines WITH text and must be attributable. What is never acceptable is
    # a bundle where refines happened and the record says "0 refines".
    actions = live_refines["n_refine_actions_seen"]
    with_text = live_refines["n_refines"]
    untexted = live_refines["n_refines_without_text_record"]
    print(f"   live bundle: {actions} refine action(s) seen, {with_text} with "
          f"before/after text, {untexted} without")
    if actions == 0 and with_text == 0:
        consistent = True
        print("   [ok] no refines occurred in this bundle — nothing to attribute, "
              "and the record\n        says so rather than implying a measurement")
    elif untexted > 0:
        consistent = not live_refines["attributable"]
        print(f"   [{'ok' if consistent else 'FAIL'}] refines WITHOUT text are "
              f"reported as NOT attributable, never as '0 refines'")
    else:
        consistent = live_refines["attributable"]
        print(f"   [{'ok' if consistent else 'FAIL'}] every refine carries its "
              f"before/after text — attributable")
    if not consistent:
        failures.append("refine attributability is misreported for the live bundle")

    # And the unattributable PATH itself is exercised on a constructed bundle, so
    # it is tested whether or not the live run happens to contain one.
    untexted_bundle = copy.deepcopy(dry)
    untexted_bundle["events"] = list(untexted_bundle.get("events", [])) + [{
        "sequence": 9200, "event_type": "structured_llm_response",
        "payload": {"parsed_response": {"action": {"action_type": "refine_task"}}},
    }]
    constructed = flog.record_refine_events(untexted_bundle)
    path_ok = (constructed["n_refine_actions_seen"] >= 1
               and constructed["n_refines_without_text_record"] >= 1
               and not constructed["attributable"])
    print(f"   [{'ok' if path_ok else 'FAIL'}] and a refine visible only as an "
          f"ACTION is surfaced as unattributable\n        (constructed, so the "
          f"path is covered regardless of what the live run did)")
    if not path_ok:
        failures.append("a refine without text was not surfaced as unattributable")

    # --- 3. RECORD 3 — visibility is not addressing --------------------------
    print("\n3. record 3 — RENDERED window, which is not the same as addressed:")
    vis_bundle = copy.deepcopy(dry)
    vis_bundle["events"] = list(vis_bundle.get("events", [])) + [
        {"sequence": 9100, "event_type": "message_sent", "payload": {
            "message_id": "m-seen", "sender_id": "w_1",
            "to_agent_as_written": "structured_manager", "message_type": "direct"}},
        {"sequence": 9101, "event_type": "message_sent", "payload": {
            "message_id": "m-unseen", "sender_id": "w_2",
            "to_agent_as_written": "structured_manager", "message_type": "direct"}},
        {"sequence": 9102, "event_type": "manager_message_window", "payload": {
            "timestep": 4, "message_window": 1, "n_messages_available": 2,
            "rendered_message_ids": ["m-seen"]}},
    ]
    vis = flog.record_message_visibility(vis_bundle)
    seen = next(m for m in vis["messages"] if m["message_id"] == "m-seen")
    unseen = next(m for m in vis["messages"] if m["message_id"] == "m-unseen")
    vis_ok = seen["entered_rendered_window"] and not unseen["entered_rendered_window"]
    print(f"   two messages, both addressed to the manager; window size 1")
    print(f"   [{'ok' if vis_ok else 'FAIL'}] one entered the rendered window and "
          f"one did NOT — identical addressing,\n        different visibility, "
          f"which is the whole point of the record")
    if not vis_ok:
        failures.append("visibility record does not distinguish rendered from addressed")

    # --- 4. RECORD 4 — reply addressing --------------------------------------
    print("\n4. record 4 — reply addressing, as written:")
    addr_bundle = copy.deepcopy(vis_bundle)
    addr_bundle["events"].append({
        "sequence": 9103, "event_type": "message_sent", "payload": {
            "message_id": "m-misaddressed", "sender_id": "w_3",
            "to_agent_as_written": "project_manager", "message_type": "direct"}})
    addressing = flog.record_reply_addressing(addr_bundle)
    naming = {r["message_id"]: r["names_manager"] for r in addressing["replies"]}
    addr_ok = (naming.get("m-seen") is True
               and naming.get("m-misaddressed") is False)
    print(f"   replies: {naming}")
    print(f"   [{'ok' if addr_ok else 'FAIL'}] a reply addressed to a NON-EXISTENT "
          f"id is recorded as not naming\n        the manager (the corpus measured "
          f"48 of 56 worker sends addressed to ids that\n        do not exist, so "
          f"this cannot be assumed)")
    if not addr_ok:
        failures.append("reply addressing did not distinguish manager-addressed")

    # --- 5. the deferral log and the denominator -----------------------------
    print("\n5. the deferral log and the OBSERVED denominator:")
    deferrals = flog.record_deferrals(dry)
    print(f"   deferrals logged in the dry run: {deferrals['n_deferrals']} "
          f"across {len(deferrals['tasks_ever_deferred'])} task(s)")
    defer_ok = deferrals["n_deferrals"] > 0
    print(f"   [{'ok' if defer_ok else 'FAIL'}] refusals are LOGGED, so "
          f"realised-vs-intended is reconstructible\n        rather than inferred "
          f"from what happens to be missing")
    if not defer_ok:
        failures.append("no deferral events logged in a capacity-bound run")

    denominator = flog.observed_denominator(dry)
    print(f"   denominator: {denominator['n_observed_tasks']} observed vs "
          f"{denominator['n_planned_tasks']} planned; by origin "
          f"{denominator['by_origin']}")
    denom_ok = (denominator["n_observed_tasks"] > 0
                and denominator["segment_denominator"] == 9)
    print(f"   [{'ok' if denom_ok else 'FAIL'}] computed from the OBSERVED task "
          f"set, with every task stamped\n        pre/post-swap origin")
    if not denom_ok:
        failures.append("denominator not computed from the observed task set")

    unstaffed = flog.unstaffed_segment_count(live)
    print(f"   unstaffed segments (first-class field): {unstaffed['n_unstaffed']} "
          f"{unstaffed['unstaffed_segments']}")

    # --- 6. REALISED-AUTHORITATIVE SCORING -----------------------------------
    # The property under test: a deferred segment's loss lands in ALLOCATION loss,
    # not execution loss. Under the retired set-level reading it would have been
    # absorbed as fake worker underperformance.
    print("\n6. realised-authoritative scoring (spec §4.1):")
    instance = gen.generate(101)
    workers = sc.roster_workers(instance)
    segment_ids = [s["segment_id"] for s in instance["segments"]]
    # An INFEASIBLE intent: four segments on one worker against a cap of three.
    intended = {sid: workers[0]["worker_id"] for sid in segment_ids[:4]}
    for index, sid in enumerate(segment_ids[4:]):
        intended[sid] = workers[1 + index % (len(workers) - 1)]["worker_id"]
    deferred = [segment_ids[3]]

    reports = {}
    for sid in segment_ids:
        if sid in deferred:
            continue
        segment = next(s for s in instance["segments"] if s["segment_id"] == sid)
        worker = next(w for w in instance["workers"]
                      if w["worker_id"] == intended[sid])
        reports[sid] = sc.attainable_report(segment, worker)

    report = sc.realised_report(instance, intended, deferred, reports)
    print(f"   intended load per worker: {report['intended_load_per_worker']} "
          f"({report['n_over_cap_workers']} worker over cap)")
    print(f"   deferred: {report['deferred_segments']}")
    print(f"   oracle {report['oracle_capacitated']:.4f}  achieved "
          f"{report['achieved']:.4f}  regret {report['regret']:.4f}")
    print(f"   allocation loss {report['allocation_loss']:.4f}   "
          f"execution loss (signed) {report['execution_loss_signed']:.4f}")

    # The deferred segment is scored 0 in the faithful term, so its loss is in
    # ALLOCATION. Execution loss should be ~0 here: every segment that RAN was
    # reported faithfully.
    alloc_carries = report["allocation_loss"] > 0
    exec_clean = abs(report["execution_loss_signed"]) < 1e-9
    print(f"   [{'ok' if alloc_carries else 'FAIL'}] the deferral's loss is in "
          f"ALLOCATION loss")
    print(f"   [{'ok' if exec_clean else 'FAIL'}] and execution loss stays ~0 — "
          f"the engine's ordering is NOT absorbed\n        as fake worker "
          f"underperformance (the retired set-level reading's failure)")
    if not alloc_carries:
        failures.append("deferral loss did not land in allocation loss")
    if not exec_clean:
        failures.append("deferral leaked into execution loss")

    intact = report["intended_allocation"] == intended
    print(f"   [{'ok' if intact else 'FAIL'}] the INTENDED allocation survives as "
          f"a diagnostic — an infeasible\n        intent is a management fact and "
          f"only the intent shows it")
    if not intact:
        failures.append("intended allocation not preserved as a diagnostic")

    # --- 7. comparability: records must be PRESENT ---------------------------
    print("\n7. comparability — a bundle without the records cannot enter analysis:")
    present = cmp.assert_records_present({"live": live, "dry": dry})
    print(f"   [{'ok' if present['analysable'] else 'FAIL'}] both bundles carry "
          f"every required record")
    if not present["analysable"]:
        failures.append(f"records missing: {present['missing']}")
    # NEGATIVE: a bundle stripped of its index still YIELDS records (the
    # extractors are defensive), so "present" alone is not analysability. This
    # case is why the check also requires a non-zero denominator — the first
    # version printed analysable=True beside segment_denominator=0.
    stripped = copy.deepcopy(dry)
    stripped.pop("index", None)
    stripped.pop("task_board_final", None)
    degraded = cmp.assert_records_present({"live": live, "broken": stripped})
    denom_reported = degraded["per_cell"]["broken"].get("segment_denominator")
    negative_ok = not degraded["analysable"] and any(
        m["record"] == "denominator" for m in degraded["missing"])
    print(f"   a bundle stripped of its index/board: analysable="
          f"{degraded['analysable']}, segment_denominator={denom_reported}")
    print(f"   [{'ok' if negative_ok else 'FAIL'}] REJECTED with a named cause — "
          f"records being present is not the\n        same as there being "
          f"anything to analyse")
    if not negative_ok:
        failures.append("a bundle with a zero denominator was called analysable")

    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / "logging_records.json").write_text(json.dumps({
        "live_bundle": live_path.name,
        "channel_pulls": {k: v for k, v in pulls.items() if k != "pulls"},
        "refine_live": live_refines,
        "deferrals_dry": {k: v for k, v in deferrals.items() if k != "deferrals"},
        "denominator_dry": {k: v for k, v in denominator.items() if k != "rows"},
        "unstaffed_live": unstaffed,
        "realised_report": {k: v for k, v in report.items()
                            if k not in ("realised_allocation",
                                         "intended_allocation")},
        "records_present": present,
    }, indent=2, sort_keys=True, default=str) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — all four records extract non-vacuously; visibility is "
          "distinguished from addressing; deferrals are logged and their loss "
          "lands in allocation, not execution; the denominator is computed from "
          "the observed task set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
