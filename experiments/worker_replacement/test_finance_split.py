"""L2a acceptance — the split against the repaired schema, on a real episode.

Zero model calls. Every state is exercised on an input where the answer is known,
and every refusal-to-compute is shown FIRING, because a split that silently
mislabels is worse than one that stops.

Run:  python3 -m experiments.worker_replacement.test_finance_split
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import finance_split as fs
from .check_load_feedback import SEED, run_machinery_episode

HERE = Path(__file__).resolve().parent


def _bundle(events: list[dict[str, Any]], index: dict[str, str],
            completions: list[dict[str, Any]] | None = None,
            detail: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"events": events, "index": {"segment_task_ids": index},
            "completions": completions or [], "parse_detail": detail or {}}


def _assigned(task: str, applied: bool = True) -> dict[str, Any]:
    return {"event_type": "task_assigned", "timestep": 0, "payload": {
        "task_id": task, "task_class": "segment", "applied": applied,
        "from_agent_id": None, "to_agent_id": "w_a", "is_reassignment": False}}


def _deferred(task: str, codes: list[str]) -> dict[str, Any]:
    """A deferral carrying CODES. Prose is for the manager; codes are for us."""
    return {"event_type": "assignment_deferred", "timestep": 1, "payload": {
        "task_id": task, "agent_id": "w_a", "refusal_codes": codes,
        "refusal_reasons": [f"<prose for {c}>" for c in codes]}}


def main() -> int:
    failures: list[str] = []
    print("L2a acceptance — segment split against the repaired instrument\n")

    # ------------------------------------------------------------------ 1 ---
    print("1. a REAL machinery episode (cell 0, zero model calls)")
    manager, engine, bundle = run_machinery_episode("0")
    bundle["completions"] = [{"task_id": t, "timestep": s}
                             for t, s in manager.completed_at.items()]
    bundle["parse_detail"] = {}
    result = fs.split(bundle)
    print(f"   {result['n_segments']} segments, residual {result['residual']}")
    for state, n in sorted(result["counts"].items()):
        if n:
            print(f"     {n:>2}  {state}")
    partitions = result["residual"] == 0
    print(f"   [{'ok' if partitions else 'FAIL'}] the buckets PARTITION the "
          f"segments (residual must be 0)")
    if not partitions:
        failures.append(f"split residual {result['residual']}")

    # THE EPISODE MUST EXERCISE THE REFUSAL PATH, or the interesting half of the
    # split is untested. This episode piles nine segments on one C=3 worker, so
    # allotment refusals are guaranteed by construction.
    refused = (result["counts"]["refused_allotment"]
               + result["counts"]["refused_concurrency"])
    print(f"   [{'ok' if refused else 'FAIL'}] and it exercises the REFUSAL states "
          f"({refused} refused), not only the happy path")
    if not refused:
        failures.append("no refused segment in the machinery episode; the "
                        "refusal branch is untested")

    # ------------------------------------------------------------------ 2 ---
    # THE SPLIT THAT MATTERS. `assigned_but_unexecuted` was one bucket and hid two
    # populations with opposite meanings: permanently barred versus transiently
    # blocked. Demonstrated on inputs where the answer is known.
    print("\n2. the two refusal populations SEPARATE (they were one bucket)")
    idx = {"seg_a": "t_a", "seg_b": "t_b", "seg_c": "t_c", "seg_d": "t_d",
           "seg_e": "t_e"}
    cases = _bundle([
        _assigned("t_a"), _deferred("t_a", ["segment_allotment"]),
        _assigned("t_b"), _deferred("t_b", ["concurrency"]),
        _assigned("t_c"),                      # assigned, never refused, never ran
        _assigned("t_e"), _deferred("t_e", ["unavailable"]),
        # t_d never assigned at all
    ], idx)
    states = fs.split(cases)["states"]
    # seg_e is the case LS found MISCLASSIFIED: the base class's availability
    # refusal contains no "allotment", so the substring classifier dropped it into
    # `refused_concurrency`. Availability is what a roster change touches, and L3
    # is the roster-change run.
    expected = {"seg_a": "refused_allotment", "seg_b": "refused_concurrency",
                "seg_c": "unexecuted_no_refusal", "seg_d": "never_assigned",
                "seg_e": "refused_unavailable"}
    for segment, want in expected.items():
        got = states[segment]
        print(f"   [{'ok' if got == want else 'FAIL'}] {segment}: {got}")
        if got != want:
            failures.append(f"{segment} classified {got}, expected {want}")

    # A worker BOTH busy and out of allotment must read as ALLOTMENT — the
    # permanent cause wins, because that is the one that changes what the manager
    # should do. This is the masking case: the concurrency branch used to
    # short-circuit and report the transient cause for a permanently-barred task.
    both = _bundle([_assigned("t_a"),
                    _deferred("t_a", ["concurrency", "segment_allotment"])],
                   {"seg_a": "t_a"})
    got = fs.split(both)["states"]["seg_a"]
    print(f"   [{'ok' if got == 'refused_allotment' else 'FAIL'}] a task refused "
          f"for BOTH causes reads as ALLOTMENT, not concurrency ({got})")
    if got != "refused_allotment":
        failures.append(f"masking case classified {got}")

    # ------------------------------------------------------------------ 3 ---
    print("\n3. executed states separate DECLINE from UNREADABLE (both score 0)")
    executed = _bundle(
        [_assigned("t_a"), _assigned("t_b"), _assigned("t_c")],
        {"seg_a": "t_a", "seg_b": "t_b", "seg_c": "t_c"},
        completions=[{"task_id": "t_a", "timestep": 2},
                     {"task_id": "t_b", "timestep": 2},
                     {"task_id": "t_c", "timestep": 2}],
        detail={"seg_a": {"rwa": 1.0, "declined": False},
                "seg_b": {"rwa": None, "declined": True},
                "seg_c": {"rwa": None, "declined": False}})
    states = fs.split(executed)["states"]
    want = {"seg_a": "executed_and_parsed", "seg_b": "executed_and_declined",
            "seg_c": "executed_but_unparseable"}
    for segment, expect in want.items():
        got = states[segment]
        print(f"   [{'ok' if got == expect else 'FAIL'}] {segment}: {got}")
        if got != expect:
            failures.append(f"{segment} classified {got}, expected {expect}")

    # ------------------------------------------------------------------ 4 ---
    print("\n4. REFUSALS TO COMPUTE, each shown firing — a wrong label is worse "
          "than a stop")
    controls: list[tuple[str, bool]] = []

    try:
        fs.split(_bundle([], {}))
        controls.append(("no segment index -> refuses (a name-based split would "
                         "reintroduce the criterion (e) predicate)", False))
    except ValueError:
        controls.append(("no segment index -> refuses (a name-based split would "
                         "reintroduce the criterion (e) predicate)", True))

    stale = _bundle([_assigned("t_a"),
                     {"event_type": "assignment_deferred", "timestep": 1,
                      "payload": {"task_id": "t_a", "agent_id": "w_a",
                                  "refusal_reasons": ["some prose"]}}],
                    {"seg_a": "t_a"})
    try:
        fs.split(stale)
        controls.append(("a deferral with PROSE but no codes -> refuses (the "
                         "substring classifier is gone, not fallen back to)",
                         False))
    except ValueError:
        controls.append(("a deferral with PROSE but no codes -> refuses (the "
                         "substring classifier is gone, not fallen back to)",
                         True))

    # AN UNKNOWN CODE MUST RAISE, not land in a bucket. The old `elif reasons:`
    # was a catch-all, so a refusal branch added later would have been recorded
    # as concurrency with the partition intact and the residual zero.
    try:
        fs.split(_bundle([_assigned("t_a"),
                          _deferred("t_a", ["some_new_branch"])],
                         {"seg_a": "t_a"}))
        controls.append(("an UNKNOWN refusal code -> refuses rather than "
                         "falling into a bucket", False))
    except ValueError:
        controls.append(("an UNKNOWN refusal code -> refuses rather than "
                         "falling into a bucket", True))

    # And the other direction: a well-formed bundle does NOT refuse.
    try:
        fs.split(cases)
        controls.append(("and a well-formed bundle computes (other direction)",
                         True))
    except ValueError:
        controls.append(("and a well-formed bundle computes (other direction)",
                         False))

    for label, fired in controls:
        print(f"   [{'ok' if fired else 'FAIL'}] {label}")
        if not fired:
            failures.append(f"CONTROL FAILED — {label}")

    out = HERE / "records" / "L2a"
    out.mkdir(parents=True, exist_ok=True)
    (out / "split_acceptance.json").write_text(json.dumps({
        "machinery_episode_cell0": {"counts": result["counts"],
                                    "n_segments": result["n_segments"],
                                    "residual": result["residual"]},
        "predicates": fs.STATE_PREDICATES,
        "controls": [{"control": lab, "fired": ok} for lab, ok in controls],
        "failures": failures,
    }, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — the split partitions, the two refusal populations "
          "separate, decline and unreadable are distinct, and every refusal to "
          "compute fires on a bundle that cannot support the claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
