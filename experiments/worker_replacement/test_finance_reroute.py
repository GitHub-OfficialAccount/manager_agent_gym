"""L7 acceptance — the primary DV computes, and every null-shaped check FIRES.

Driven through REAL machinery episodes (zero model calls) rather than fixtures, so
the DV is exercised against the events the runner actually writes. The last time a
fixture stood in for the production path here it described a schema that had been
replaced two commits earlier and passed against an empty rendering.

Every check that asserts a null carries a positive control (METHODOLOGY_RULES §B):
a query asserting a NULL must first demonstrate a HIT on a known-positive case.

Run:  python3 -m experiments.worker_replacement.test_finance_reroute
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import finance_reroute as rr
from .check_load_feedback import SEED, run_machinery_episode

HERE = Path(__file__).resolve().parent


def _bundle_with(events: list[dict[str, Any]], manifest: dict[str, Any] | None = None,
                 completions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"events": events, "manifest": manifest or {"successor_id": "w_new"},
            "completions": completions or []}


def _load_event(timestep: int, rows: list[tuple[str, int, int]]) -> dict[str, Any]:
    return {"event_type": "manager_load_feedback", "payload": {
        "timestep": timestep,
        "load": [{"agent_id": a, "available": True, "dimensions": [
            {"name": "segment allotment", "held": h, "capacity": c,
             "releases_on_completion": False}]} for a, h, c in rows]}}


def _assign_event(task: str, to: str, frm: str | None, applied: bool = True,
                  task_class: str | None = "segment",
                  timestep: int = 1) -> dict[str, Any]:
    return {"event_type": "task_assigned", "timestep": timestep, "payload": {
        "task_id": task, "task_name": task, "task_class": task_class,
        "from_agent_id": frm, "to_agent_id": to,
        "is_reassignment": bool(frm and to and frm != to),
        "action_type": "assign_tasks_to_agents", "applied": applied,
        "reason": "", "task_status_before": "ready"}}


def main() -> int:
    failures: list[str] = []
    print("L7 acceptance — `rerouted_share` over the ruled definition\n")

    # ------------------------------------------------------------------ 1 ---
    print("1. the DV computes on a REAL machinery episode (cell 0, zero model "
          "calls)")
    _manager, _engine, bundle = run_machinery_episode("0")
    bundle["manifest"] = {"successor_id": "w_new", "cell": "0",
                          "instance_seed": SEED}
    # REAL COMPLETIONS, WITH THEIR TIMESTEPS. The first version passed `[]` here,
    # and an empty completion set is the one input on which an episode-wide
    # terminality test and a per-step one agree — so the denominator defect RR
    # found could not fire. A machinery episode that completes work is the input
    # that exercises it.
    bundle["completions"] = [
        {"task_id": task_id, "timestep": step}
        for task_id, step in _manager.completed_at.items()
    ]
    result = rr.rerouted_share(bundle)
    n_assign = len([e for e in bundle["events"]
                    if e["event_type"] == "task_assigned"])
    print(f"   {n_assign} task_assigned events; eligible={result['n_eligible']}, "
          f"moved={result['n_moved']}, forced={result['n_forced_moves']}")
    if n_assign == 0:
        failures.append("the machinery episode produced NO assignment events — "
                        "the DV would be computed on nothing")
    print(f"   [{'ok' if n_assign else 'FAIL'}] the runner emits assignment events "
          f"at all (this is the record that did not exist before L7)")

    # THE DENOMINATOR IS NON-EMPTY OR THE SHARE IS MEANINGLESS. A share over an
    # empty denominator is None, and a check that accepted None would pass on an
    # episode where nothing was eligible — constant-because-empty, again.
    print(f"   [{'ok' if result['n_eligible'] else 'FAIL'}] the denominator is "
          f"non-empty ({result['n_eligible']} eligible tasks)")
    if not result["n_eligible"]:
        failures.append("denominator empty; the share cannot mean anything")

    # THE COMPLETION PATH IS NON-VACUOUS. A denominator check on an episode with
    # no completions cannot distinguish per-step terminality from episode-wide
    # terminality — which is exactly how RR's blocker 1 survived the first
    # acceptance. Asserted rather than assumed.
    n_completed_segments = len({c["task_id"] for c in bundle["completions"]}
                               & {str(e["payload"]["task_id"])
                                  for e in bundle["events"]
                                  if e["event_type"] == "task_assigned"
                                  and e["payload"].get("task_class") == "segment"})
    print(f"   [{'ok' if n_completed_segments else 'FAIL'}] and segments actually "
          f"COMPLETE in this episode ({n_completed_segments}), so per-step and "
          f"episode-wide terminality are distinguishable here")
    if not n_completed_segments:
        failures.append("no segment completed, so the terminality predicate is "
                        "untested — the input on which the defect cannot fire")

    # THE DEFECT ITSELF, as a direct comparison. Episode-wide terminality would
    # drop every completed task from the denominator; per-step keeps those that
    # were movable before they finished.
    episode_wide = {t for t in rr.eligible_tasks(bundle)
                    if t not in {c["task_id"] for c in bundle["completions"]}}
    per_step = rr.eligible_tasks(bundle)
    differs = len(per_step) > len(episode_wide)
    print(f"   [{'ok' if differs else 'FAIL'}] per-step terminality keeps "
          f"{len(per_step)} eligible where episode-wide would keep "
          f"{len(episode_wide)} — the ~7x denominator bias RR measured")
    if not differs:
        failures.append("per-step and episode-wide terminality gave the same "
                        "denominator; the fix is untested on this input")

    # ------------------------------------------------------------------ 2 ---
    # THE NUMERATOR MUST BE EXERCISED ON REAL EVENTS TOO. The machinery manager
    # assigns once and never revisits, so the episode above drives the DENOMINATOR
    # and nothing else — `moved=0` there is a property of the stub, not a result.
    # A DV whose numerator path had only ever run on constructed dictionaries
    # would be a fixture test wearing an end-to-end label.
    print("\n1b. the NUMERATOR on real events — a genuine reassignment through "
          "the production action")
    import asyncio
    from manager_agent_gym.core.common.run_trace import RunTraceRecorder
    from manager_agent_gym.schemas.execution.manager_actions import (
        AssignmentPair, AssignTasksToAgentsAction)
    from . import finance_env as env

    workflow = _engine.workflow
    # THE TARGET MUST BE ONE THE ACTION WILL ACTUALLY APPLY. The first version of
    # this check picked the first assigned segment and the first other agent id
    # seen on the board — and got `applied=False`, because the action skips
    # terminal tasks and agents no longer on the roster (the predecessor is gone
    # by the end of a swap episode). The DV was right and the test was wrong,
    # which is worth keeping: it is the requested-vs-applied split doing its job.
    from manager_agent_gym.schemas.core.base import TaskStatus as _TS
    segments = [t for t in workflow.tasks.values()
                if env.CapacityBoundedAIAgent.is_metered(t) and t.assigned_agent_id
                and t.status not in (_TS.COMPLETED, _TS.FAILED)]
    present = sorted(a for a in workflow.agents if a.startswith("w_"))
    if not segments or len(present) < 2:
        failures.append("no non-terminal assigned segment and two present agents "
                        "to move it between; the numerator path is untested")
        segments, present = segments or [None], present + ["", ""]
    holder = segments[0].assigned_agent_id
    others = [a for a in present if a != holder]
    tracer = RunTraceRecorder()
    from manager_agent_gym.core.common.run_trace import trace_scope
    # The engine wraps every timestep in `trace_scope(timestep=...)`; a caller
    # invoking the action outside one gets an event with no timestep, and the DV
    # RAISES rather than falling back to position. That fired on this very line
    # the first time it ran — correct behaviour, and the reason the fallback was
    # removed rather than made lenient.
    # A timestep the manager actually observed. Using max+1 puts the move at a
    # timestep with no load view, which the module now REFUSES to classify rather
    # than silently filing as FORCED — that refusal is asserted separately below.
    last_step = max(rr.load_timeline(bundle))
    with tracer.activate(), trace_scope(timestep=last_step):
        asyncio.run(AssignTasksToAgentsAction(
            reasoning="move one segment to a different worker",
            assignments=[AssignmentPair(task_id=segments[0].id,
                                        agent_id=others[0])]).execute(workflow))
    live = {"events": bundle["events"] + tracer.events,
            "manifest": bundle["manifest"], "completions": bundle["completions"]}
    live_result = rr.rerouted_share(live)
    real_move = live_result["n_discretionary_moves"] >= 1
    print(f"   moved one segment {holder} -> {others[0]} through the real action")
    print(f"   [{'ok' if real_move else 'FAIL'}] the DV sees it as a DISCRETIONARY "
          f"move on real events ({live_result['n_discretionary_moves']} moves, "
          f"unconditional share {live_result['rerouted_share_unconditional']})")
    if not real_move:
        failures.append("a real reassignment through the production action did "
                        "not register in the DV")

    # ------------------------------------------------------------------ 1c ---
    # THE BATCHING REGRESSION (LS blocker). The manager BULK-ASSIGNS — the corpus
    # shows nine assignments applied in one timestep — and the first version of
    # this module mapped the Nth assignment to the Nth timestep, so those nine
    # were attributed to nine consecutive ones. A single-move test cannot expose
    # that; this one has TWO moves in ONE timestep and would fail against the old
    # mapping, which would place the second at t2 and judge it against a capacity
    # view and roster the manager never held.
    print("\n1c. BATCHING — two moves in ONE timestep must both be judged against "
          "THAT timestep")
    batched = _bundle_with([
        _load_event(0, [("w_a", 0, 3), ("w_b", 0, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_a", None, timestep=0),
        _assign_event("t2", "w_a", None, timestep=0),
        # Both moves happen at t1, where every worker still has room.
        _load_event(1, [("w_a", 2, 3), ("w_b", 0, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_b", "w_a", timestep=1),
        _assign_event("t2", "w_c", "w_a", timestep=1),
        # t2 is where the OLD positional mapping would have placed the second
        # move: w_a has left, so it would have been misread as FORCED.
        _load_event(2, [("w_b", 1, 3), ("w_c", 1, 3)]),
    ])
    batch = rr.moves(batched)
    steps = sorted(m["timestep"] for m in batch["discretionary"])
    ok = (len(batch["discretionary"]) == 2 and not batch["forced"]
          and steps == [1, 1])
    print(f"   [{'ok' if ok else 'FAIL'}] both moves are DISCRETIONARY at t1 "
          f"({len(batch['discretionary'])} disc, {len(batch['forced'])} forced, "
          f"timesteps {steps})")
    if not ok:
        failures.append(f"batched moves misattributed: {len(batch['forced'])} "
                        f"forced, timesteps {steps} — the positional mapping "
                        f"would give [1, 2] and misclassify the second as FORCED")

    # A move at a timestep with NO load view must refuse to classify rather than
    # defaulting. Absence of a roster view is not evidence that the source left.
    try:
        rr.moves(_bundle_with([
            _load_event(0, [("w_a", 0, 3), ("w_b", 0, 3)]),
            _assign_event("t1", "w_a", None, timestep=0),
            _assign_event("t1", "w_b", "w_a", timestep=99),
        ]))
        refused = False
    except ValueError:
        refused = True
    print(f"   [{'ok' if refused else 'FAIL'}] a move at a timestep with NO load "
          f"view REFUSES to classify (it would otherwise read as FORCED)")
    if not refused:
        failures.append("a move with no roster view was silently classified; "
                        "absence would be read as the source having departed")

    # And the raise, rather than a silent fallback, on an event with no timestep.
    try:
        rr.moves(_bundle_with([{"event_type": "task_assigned", "payload": {}}]))
        raised = False
    except ValueError:
        raised = True
    print(f"   [{'ok' if raised else 'FAIL'}] an assignment event with NO timestep "
          f"RAISES rather than falling back to position")
    if not raised:
        failures.append("a timestep-less event did not raise; the positional "
                        "defect can silently return on older bundles")

    print("\n2. FORCED vs DISCRETIONARY — split on cases with a known answer")
    # THE POPULATION SPLIT, on constructed cases where the answer is known. This
    # is the definition's load-bearing distinction and it must be demonstrated
    # rather than asserted: a bug that classified everything as one population
    # would still produce a plausible-looking number.
    forced_case = _bundle_with([
        _load_event(0, [("w_old", 1, 3), ("w_a", 0, 3)]),
        _assign_event("t1", "w_old", None, timestep=0),
        # w_old has LEFT: it is absent from the timestep-1 view.
        _load_event(1, [("w_a", 0, 3), ("w_new", 0, 3)]),
        _assign_event("t1", "w_new", "w_old", timestep=1),
    ])
    split = rr.moves(forced_case)
    ok = len(split["forced"]) == 1 and not split["discretionary"]
    print(f"   [{'ok' if ok else 'FAIL'}] source absent from the roster -> FORCED "
          f"({len(split['forced'])} forced, {len(split['discretionary'])} disc)")
    if not ok:
        failures.append(f"forced case classified as {split}")

    disc_case = _bundle_with([
        _load_event(0, [("w_a", 0, 3), ("w_b", 0, 3)]),
        _assign_event("t1", "w_a", None, timestep=0),
        _load_event(1, [("w_a", 1, 3), ("w_b", 0, 3)]),
        _assign_event("t1", "w_b", "w_a", timestep=1),
    ])
    split = rr.moves(disc_case)
    ok = len(split["discretionary"]) == 1 and not split["forced"]
    print(f"   [{'ok' if ok else 'FAIL'}] source still present -> DISCRETIONARY "
          f"({len(split['forced'])} forced, {len(split['discretionary'])} disc)")
    if not ok:
        failures.append(f"discretionary case classified as {split}")

    # ------------------------------------------------------------------ 3 ---
    print("\n3. the conditioned share EXCLUDES moves that were not choices")
    # One eligible task, moved, but the only other worker is full -> no choice.
    no_choice = _bundle_with([
        _load_event(0, [("w_a", 0, 3), ("w_b", 3, 3)]),
        _assign_event("t1", "w_a", None, timestep=0),
        _load_event(1, [("w_a", 1, 3), ("w_b", 3, 3)]),
        _assign_event("t1", "w_b", "w_a", timestep=1),
        _load_event(2, [("w_a", 1, 3), ("w_b", 3, 3)]),
    ])
    result_nc = rr.rerouted_share(no_choice)
    ok = (result_nc["n_moved"] == 1 and result_nc["n_moved_with_real_choice"] == 0)
    print(f"   [{'ok' if ok else 'FAIL'}] a move with <2 legal destinations counts "
          f"in the unconditional share ({result_nc['n_moved']}) but NOT the "
          f"conditioned one ({result_nc['n_moved_with_real_choice']})")
    if not ok:
        failures.append(f"conditioning did not exclude the forced-hand move: "
                        f"{result_nc}")

    # POSITIVE CONTROL on that exclusion: the same shape WITH room must count.
    with_choice = _bundle_with([
        _load_event(0, [("w_a", 0, 3), ("w_b", 0, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_a", None, timestep=0),
        _load_event(1, [("w_a", 1, 3), ("w_b", 0, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_b", "w_a", timestep=1),
        _load_event(2, [("w_a", 1, 3), ("w_b", 1, 3), ("w_c", 0, 3)]),
    ])
    result_wc = rr.rerouted_share(with_choice)
    ok = result_wc["n_moved_with_real_choice"] == 1
    print(f"   [{'ok' if ok else 'FAIL'}] POSITIVE CONTROL — the same move WITH "
          f"two legal destinations DOES count ({result_wc['n_moved_with_real_choice']})")
    if not ok:
        failures.append(f"conditioned share excluded a real choice: {result_wc}")

    # ------------------------------------------------------------------ 4 ---
    print("\n4. the unit is the TASK, counted once — a share cannot exceed 1")
    twice = _bundle_with([
        _load_event(0, [("w_a", 0, 3), ("w_b", 0, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_a", None, timestep=0),
        _load_event(1, [("w_a", 1, 3), ("w_b", 0, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_b", "w_a", timestep=1),
        _load_event(2, [("w_a", 1, 3), ("w_b", 1, 3), ("w_c", 0, 3)]),
        _assign_event("t1", "w_c", "w_b", timestep=2),
        _load_event(3, [("w_a", 1, 3), ("w_b", 1, 3), ("w_c", 1, 3)]),
    ])
    result_twice = rr.rerouted_share(twice)
    ok = (result_twice["n_discretionary_moves"] == 2
          and result_twice["n_moved"] == 1
          and (result_twice["rerouted_share_unconditional"] or 0) <= 1.0)
    print(f"   [{'ok' if ok else 'FAIL'}] one task moved twice = 2 MOVES but 1 "
          f"task ({result_twice['n_discretionary_moves']} moves, "
          f"{result_twice['n_moved']} tasks, share "
          f"{result_twice['rerouted_share_unconditional']})")
    if not ok:
        failures.append(f"task/move unit confusion: {result_twice}")

    # ------------------------------------------------------------------ 5 ---
    print("\n5. non-segment work is NOT in the DV, and requested-but-skipped is "
          "reported")
    mixed = _bundle_with([
        _load_event(0, [("w_a", 0, 3), ("w_b", 0, 3)]),
        _assign_event("x1", "w_a", None, task_class=None, timestep=0),
        _load_event(1, [("w_a", 0, 3), ("w_b", 0, 3)]),
        _assign_event("x1", "w_b", "w_a", task_class=None, timestep=1),
        _assign_event("t9", "w_b", "w_a", applied=False, timestep=1),
        _load_event(2, [("w_a", 0, 3), ("w_b", 0, 3)]),
    ])
    result_mixed = rr.rerouted_share(mixed)
    ok = (result_mixed["n_discretionary_moves"] == 0
          and result_mixed["n_requested_not_applied"] == 1)
    print(f"   [{'ok' if ok else 'FAIL'}] a non-segment reassignment is excluded "
          f"({result_mixed['n_discretionary_moves']} counted) and the skipped "
          f"request is reported ({result_mixed['n_requested_not_applied']})")
    if not ok:
        failures.append(f"class filter or skip reporting wrong: {result_mixed}")

    # ------------------------------------------------------------------ 6 ---
    # ------------------------------------------------------------------ 5b ---
    # THE RESTRICTED QUANTITY (LS, after RR killed the unrestricted one).
    # Forced-to-successor is recommended by BOTH failure mode #1 and by
    # capacity-optimal play, so it discriminates nothing on its own. Restricted to
    # segments the successor CANNOT do, only the failure-mode reading survives.
    # Controlled in three directions, because a quantity that only ever returns 0
    # is indistinguishable from one that is broken.
    print("\n5b. forced-to-successor RESTRICTED to work the successor cannot do")
    cov_instance = {
        "workers": [{"worker_id": "w_new", "irb_coverage": ("corporate",)}],
        "segments": [{"segment_id": "seg_a", "irb_approved": True,
                      "asset_class": "bank"},          # OUTSIDE the scope
                     {"segment_id": "seg_b", "irb_approved": True,
                      "asset_class": "corporate"},     # inside
                     {"segment_id": "seg_c", "irb_approved": False,
                      "asset_class": "bank"}],         # SA: never a coverage error
    }
    cov_bundle = _bundle_with(
        [_load_event(0, [("w_old", 0, 3), ("w_new", 0, 3)]),
         _assign_event("seg_a", "w_old", None, timestep=0),
         _assign_event("seg_b", "w_old", None, timestep=0),
         _assign_event("seg_c", "w_old", None, timestep=0),
         _load_event(1, [("w_new", 0, 3)]),           # w_old has departed
         _assign_event("seg_a", "w_new", "w_old", timestep=1),
         _assign_event("seg_b", "w_new", "w_old", timestep=1),
         _assign_event("seg_c", "w_new", "w_old", timestep=1)],
        manifest={"successor_id": "w_new"})
    cov_bundle["instance"] = cov_instance
    cov_bundle["index"] = {"segment_task_ids": {s: s for s in
                                                ("seg_a", "seg_b", "seg_c")}}
    cov = rr.rerouted_share(cov_bundle)["forced_to_successor_uncovered"]
    ok = (cov["computable"] and cov["n_forced_to_successor"] == 3
          and cov["n_uncovered"] == 1)
    print(f"   [{'ok' if ok else 'FAIL'}] 3 forced to the successor, exactly 1 "
          f"UNCOVERED — the in-scope IRB segment and the SA segment are not "
          f"coverage errors (got {cov['n_uncovered']} of "
          f"{cov['n_forced_to_successor']})")
    if not ok:
        failures.append(f"restricted quantity wrong: {cov}")

    no_instance = dict(cov_bundle)
    no_instance.pop("instance")
    absent = rr.rerouted_share(no_instance)["forced_to_successor_uncovered"]
    ok_absent = absent["computable"] is False and absent["n_uncovered"] is None
    print(f"   [{'ok' if ok_absent else 'FAIL'}] and a bundle without an instance "
          f"reports UNCOMPUTABLE rather than 0 — a zero would read as 'the "
          f"manager never did this'")
    if not ok_absent:
        failures.append(f"missing instance produced a number: {absent}")

    print("\n6. positive controls — every null-shaped assertion, shown FIRING")
    controls = [
        ("split check fires when a FORCED move is misclassified",
         len(rr.moves(forced_case)["forced"]) != len(rr.moves(disc_case)["forced"])),
        ("denominator check fires on a bundle with no eligible task",
         rr.rerouted_share(_bundle_with([_load_event(0, [("w_a", 0, 3)])]))
         ["n_eligible"] == 0),
        ("class filter fires — segment and non-segment give different counts",
         result_mixed["n_discretionary_moves"] != result_wc["n_discretionary_moves"]),
        ("legality check fires — a FULL worker is not a legal destination",
         rr.legal_destinations(
             {"w_b": {"agent_id": "w_b",
                      "dimensions": [{"name": "a", "held": 3, "capacity": 3}]}},
             None) == []),
        ("and a worker WITH room IS legal (the other direction)",
         rr.legal_destinations(
             {"w_b": {"agent_id": "w_b",
                      "dimensions": [{"name": "a", "held": 1, "capacity": 3}]}},
             None) == ["w_b"]),
    ]
    for label, fired in controls:
        print(f"   [{'ok' if fired else 'FAIL'}] {label}")
        if not fired:
            failures.append(f"POSITIVE CONTROL FAILED — {label}; the "
                            f"corresponding green is worthless")

    out = HERE / "records" / "L7"
    out.mkdir(parents=True, exist_ok=True)
    (out / "reroute_acceptance.json").write_text(json.dumps({
        # BOTH the denominator-only episode AND the episode with a real move.
        # The previous record carried only the first, in which every numerator
        # quantity is 0 — a DV returning zero on real data with no positive
        # control on real data is uninterpretable (RR blocker 3). The zeros are a
        # property of a stub manager that never revisits an assignment; the
        # non-zero result below is the same episode after one real reassignment
        # through the production action.
        "machinery_episode_cell0_no_moves": result,
        "machinery_episode_cell0_after_one_real_move": live_result,
        "note_on_zeros": (
            "n_moved=0 in the first is a property of the machinery manager, which "
            "assigns once and never revisits. The second is the positive control "
            "on real events."),
        "controls": [{"control": lab, "fired": ok} for lab, ok in controls],
        "failures": failures,
    }, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — the DV computes on real events, the two populations "
          "split correctly, the conditioned share excludes non-choices, the unit "
          "is the task, and every null-shaped check fires on a known positive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
