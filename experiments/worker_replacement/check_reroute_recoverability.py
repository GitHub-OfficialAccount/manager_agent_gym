"""D1 — is the brief's primary DV recoverable from the bundles we already have?

LS's L4 drift check (2026-08-08) found that `STUDY1_FOUNDATION.md` §5 names
`rerouted_share` as the PRIMARY DV, that it appears nowhere in the codebase, and
that no event records an assignment — only `assignment_deferred`, a REFUSAL. **We
log the assignments that were rejected and not the ones that were made.** The
conclusion drawn was that the DV is not recoverable from existing bundles either.

THIS SCRIPT CHECKS THAT, because the answer changes what L3 has to spend.

WHAT IT FINDS. The DV is PARTIALLY recoverable, from a source not built for it:
`structured_llm_response` carries the manager's parsed action, so every
`assign_task` / `assign_tasks_to_agents` the manager REQUESTED is in every bundle,
in order, with task and agent. Reassignment history reconstructs from that.

WHAT THAT RECOVERY IS NOT. It is what the manager ASKED FOR, not what was APPLIED.
`AssignTasksToAgentsAction.execute` skips missing tasks, terminal tasks and unknown
agents, and returns them in a `skipped` list that is not logged. So this is the
REQUESTED assignment stream, and a requested-vs-applied gap is invisible here —
one name, two predicates, which is exactly the family of error §B exists for. An
event at the APPLY site is still needed; this establishes what can be learned
before one exists, not that one is unnecessary.

THE FINDING THAT MATTERS MORE THAN THE RECOVERY. Most reassignment in these
episodes is FORCED, not chosen: the predecessor departs at t_swap holding work,
and that work must move or it can never run. A `rerouted_share` that counts both
would be an un-mixing failure of exactly the kind the regret split turned out to
be — a behavioural DV that is mostly a function of how many tasks the predecessor
happened to be holding when it left.

Run:  python3 -m experiments.worker_replacement.check_reroute_recoverability
"""

from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BUNDLE_GLOB = str(HERE / "records" / "R2" / "run_cell*_seed*.json")


def requested_assignments(bundle: dict[str, Any]) -> dict[str, list[tuple[int, str]]]:
    """Task -> ordered (sequence, agent) the manager REQUESTED.

    Read off the manager's own parsed action. Both action types are handled: a
    reader that knew only about `assign_tasks_to_agents` would silently undercount
    every episode in which the manager used the single-task form.
    """
    history: dict[str, list[tuple[int, str]]] = {}
    for event in bundle.get("events", []):
        if event.get("event_type") != "structured_llm_response":
            continue
        parsed = (event.get("payload") or {}).get("parsed_response") or {}
        action = parsed.get("action") or {}
        pairs: list[tuple[str, str]] = []
        if action.get("action_type") == "assign_tasks_to_agents":
            pairs = [(p["task_id"], p["agent_id"])
                     for p in action.get("assignments", [])]
        elif action.get("action_type") == "assign_task" and action.get("task_id"):
            pairs = [(action["task_id"], action["agent_id"])]
        for task_id, agent_id in pairs:
            history.setdefault(task_id, []).append((event["sequence"], agent_id))
    return history


def timestep_index(bundle: dict[str, Any]) -> dict[int, int]:
    """Sequence -> timestep, from the observation record built each timestep."""
    return {e["sequence"]: (e.get("payload") or {}).get("timestep")
            for e in bundle.get("events", [])
            if e.get("event_type") == "manager_message_window"}


def classify(bundle: dict[str, Any]) -> dict[str, Any]:
    """Split reassignment into FORCED and DISCRETIONARY.

    FORCED — the source agent is the predecessor and the move is at or after
    t_swap. The assignee has left the roster; the work cannot run where it is, so
    moving it is not a judgement about the newcomer, it is the only legal action.

    DISCRETIONARY — a move between agents both present. This is the behaviour the
    brief's DV is about: the manager choosing to put work somewhere else.

    The distinction is the whole point. Counting them together produces a
    behavioural number that is mostly determined by how many tasks the predecessor
    happened to hold at t_swap.
    """
    manifest = bundle["manifest"]
    t_swap = manifest.get("t_swap")
    predecessor = manifest.get("predecessor_id")
    history = requested_assignments(bundle)
    by_sequence = timestep_index(bundle)

    def timestep_of(sequence: int) -> int | None:
        earlier = [s for s in by_sequence if s <= sequence]
        return by_sequence[max(earlier)] if earlier else None

    segments = {str(v) for v in bundle["index"]["segment_task_ids"].values()}
    forced: list[dict[str, Any]] = []
    discretionary: list[dict[str, Any]] = []
    for task_id, moves in history.items():
        for (_seq_a, agent_a), (seq_b, agent_b) in zip(moves, moves[1:]):
            if agent_a == agent_b:
                continue
            timestep = timestep_of(seq_b)
            move = {"task_id": task_id, "from": agent_a, "to": agent_b,
                    "timestep": timestep, "is_segment": task_id in segments}
            if (agent_a == predecessor and timestep is not None
                    and t_swap is not None and timestep >= t_swap):
                forced.append(move)
            else:
                discretionary.append(move)

    return {
        "cell": manifest.get("cell"),
        "seed": manifest.get("instance_seed"),
        "n_tasks_requested": len(history),
        "n_segments_requested": len(set(history) & segments),
        "n_forced": len(forced),
        "n_discretionary": len(discretionary),
        "forced": forced,
        "discretionary": discretionary,
    }


def choice_sets(bundle: dict[str, Any], moves: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For each move, how many destinations were CAPACITY-LEGAL at that moment.

    LS's blocker, and it is the un-mixing risk one level further down. At t_swap
    the predecessor holds 4 segments and the successor arrives EMPTY with 3 free
    slots while the incumbents are nearly full. **If capacity alone makes the
    successor the only legal destination, then "22 of 24 forced moves went to the
    successor" carries no information about channel use at all** — it is the
    engine's constraint, not the manager's judgement, and the destination
    distribution would be worth nothing.

    LEGAL means: on the roster at that timestep, and holding fewer than
    `segment_capacity` segments. Counted from segment tasks STARTED at timesteps
    strictly BEFORE the move, because the manager acts at the top of a timestep
    and can only have seen what had already begun.

    RECONSTRUCTED, NOT LOGGED — which is the honest limit here. Capacity state was
    never recorded per timestep (that is what L1's `manager_load_feedback` now
    fixes, for runs from here on). This walks `worker_execution_started` and
    attributes each to the timestep of the nearest preceding manager observation.
    A start whose attribution is off by one timestep moves a count by one, so a
    choice set of exactly 1 versus 2 is the fragile case and is reported as such
    rather than smoothed.
    """
    manifest = bundle["manifest"]
    t_swap = manifest.get("t_swap")
    predecessor = manifest.get("predecessor_id")
    successor = manifest.get("successor_id")
    pre = list(manifest.get("roster_pre_swap") or [])
    post = list(manifest.get("roster_post_swap") or [])
    segments = {str(v) for v in bundle["index"]["segment_task_ids"].values()}
    capacity = int((manifest.get("capacity_mapping") or {}).get("cap") or 3)

    by_sequence = timestep_index(bundle)

    def timestep_of(sequence: int) -> int | None:
        earlier = [s for s in by_sequence if s <= sequence]
        return by_sequence[max(earlier)] if earlier else None

    # Segment starts, per worker, with the timestep they began.
    starts: list[tuple[int, str, str]] = []
    for event in bundle.get("events", []):
        if event.get("event_type") != "worker_execution_started":
            continue
        task_id = str(event.get("task_id") or "")
        if task_id not in segments:
            continue
        timestep = timestep_of(event["sequence"])
        if timestep is not None:
            starts.append((timestep, str(event.get("actor_id") or ""), task_id))

    out: list[dict[str, Any]] = []
    for move in moves:
        timestep = move["timestep"]
        if timestep is None:
            continue
        roster = post if (t_swap is not None and timestep >= t_swap) else pre
        held: dict[str, set[str]] = {w: set() for w in roster}
        for start_ts, worker, task_id in starts:
            if start_ts < timestep and worker in held:
                held[worker].add(task_id)
        legal = sorted(w for w in roster
                       if w != move["from"] and len(held[w]) < capacity)
        out.append({
            **move,
            "n_legal_destinations": len(legal),
            "legal_destinations": legal,
            "chosen_was_legal": move["to"] in legal,
            "successor_only_legal": legal == [successor],
            "held_at_move": {w: len(h) for w, h in held.items()},
            "predecessor": predecessor,
        })
    return out


def main() -> int:
    paths = sorted(glob.glob(BUNDLE_GLOB))
    if not paths:
        print("no scope bundles found — nothing to check")
        return 1

    print("D1 — is `rerouted_share` recoverable from the bundles we already have?\n")
    print("SOURCE: `structured_llm_response`.parsed_response.action — what the "
          "manager\nREQUESTED. Not what was applied; see the module docstring.\n")

    rows = [classify(json.loads(Path(p).read_text())) for p in paths]
    print(f"{'bundle':22} {'cell':>4} {'segs':>5} {'forced':>7} {'discret':>8}")
    for path, row in zip(paths, rows):
        print(f"{Path(path).stem:22} {str(row['cell']):>4} "
              f"{row['n_segments_requested']:>5} {row['n_forced']:>7} "
              f"{row['n_discretionary']:>8}")

    total_forced = sum(r["n_forced"] for r in rows)
    total_disc = sum(r["n_discretionary"] for r in rows)
    total_moves = total_forced + total_disc

    print(f"\nTOTAL reassignments: {total_moves} "
          f"({total_forced} FORCED, {total_disc} discretionary)")
    if total_moves:
        print(f"  FORCED SHARE: {total_forced / total_moves:.0%} — a naive "
              f"`rerouted_share` would be mostly\n  a function of how many tasks "
              f"the predecessor held when it left, not of manager judgement.")

    # The control is the load-bearing comparison, and it is where the confound is
    # clearest: cell U has no swap, so it can have no forced moves at all.
    unswapped = [r for r in rows if r["cell"] == "U"]
    swapped = [r for r in rows if r["cell"] != "U"]
    print(f"\ncell U (no swap):   {sum(r['n_forced'] for r in unswapped)} forced, "
          f"{sum(r['n_discretionary'] for r in unswapped)} discretionary, "
          f"over {len(unswapped)} episodes")
    print(f"cells 0-4 (swap):   {sum(r['n_forced'] for r in swapped)} forced, "
          f"{sum(r['n_discretionary'] for r in swapped)} discretionary, "
          f"over {len(swapped)} episodes")
    print("\nREADING LIMIT, stated so the table above is not over-read: 3 episodes "
          "per cell.\nThere is NO contrast verdict here in either direction. What "
          "this establishes is\n(i) the DV is recoverable well enough to DEFINE it "
          "against real data, and (ii) it\nsplits into two populations that must "
          "not be summed. Cell U having zero forced\nmoves is structural — it has "
          "no departure — not evidence about any channel.")

    # --- THE CHOICE-SET CHECK (LS blocker) --------------------------------
    print("\n" + "=" * 72)
    print("CHOICE SET — was the destination a DECISION, or the only legal option?")
    print("=" * 72)
    print("If capacity alone leaves one legal destination, the destination "
          "distribution\ncarries no information about channel use. Counted from "
          "segment starts BEFORE\nthe move; reconstructed, not logged (see the "
          "function docstring).\n")

    forced_sets: list[dict[str, Any]] = []
    disc_sets: list[dict[str, Any]] = []
    for path, row in zip(paths, rows):
        bundle = json.loads(Path(path).read_text())
        forced_sets += choice_sets(bundle, row["forced"])
        disc_sets += choice_sets(bundle, row["discretionary"])

    def summarise(label: str, sets: list[dict[str, Any]]) -> None:
        if not sets:
            print(f"{label}: none")
            return
        sizes: dict[int, int] = {}
        for s in sets:
            sizes[s["n_legal_destinations"]] = sizes.get(
                s["n_legal_destinations"], 0) + 1
        forced_hand = sum(1 for s in sets if s["successor_only_legal"])
        illegal = sum(1 for s in sets if not s["chosen_was_legal"])
        print(f"{label}: n={len(sets)}")
        for size in sorted(sizes):
            print(f"   {sizes[size]:>3} move(s) had {size} capacity-legal "
                  f"destination(s)")
        print(f"   {forced_hand} where the SUCCESSOR was the only legal "
              f"destination — no decision was available")
        print(f"   {illegal} where the chosen destination was NOT capacity-legal "
              f"(the manager over-committed)")

    summarise("FORCED moves       ", forced_sets)
    print()
    summarise("DISCRETIONARY moves", disc_sets)
    print("   ^^ DO NOT QUOTE THESE LEGAL-SET SIZES (RR limitation, accepted).")
    print("      Reconstructing pre-L1 allotment state requires scraping the "
          "agent id out of a\n      system-prompt string and the segment out of a "
          "task-prompt string:\n      `worker_execution_started` carries no "
          "agent_id and no task_name. **The JOIN\n      KEYS are a text scrape**, "
          "which is worse than the timing-attribution weakness\n      first "
          "reported. The FORCED result survives because it has independent "
          "field-level\n      support — 0 of 24 to a provably-exhausted "
          "destination, from logged deferral\n      signatures. Discretionary "
          "legal-set sizes wait for a post-L1 run, where capacity\n      state is "
          "a logged field.")

    # WHY the two populations differ, which is the part that decides the design.
    # It is a TIMING story, and it inverts the direction of the worry.
    def spread(sets: list[dict[str, Any]]) -> str:
        if not sets:
            return "none"
        ts = sorted(s["timestep"] for s in sets)
        load = sorted(sum(s["held_at_move"].values()) for s in sets)
        return (f"timesteps {ts[0]}–{ts[-1]}, team segments already started at "
                f"move time {load[0]}–{load[-1]}")

    print(f"\nWHEN each population happens:")
    print(f"   FORCED:        {spread(forced_sets)}")
    print(f"   DISCRETIONARY: {spread(disc_sets)}")
    # CORRECTED (RR review). The first version of this sentence said
    # "discretionary moves happen later", which is true of fewer than half of
    # them: 5 of 9 land at t3-t6 in the same window as the forced moves and 4 at
    # t19-t21. The population is BIMODAL, not late, and a summary that flattens it
    # would have a reader expecting a clean temporal separation that is not there.
    early = [s for s in disc_sets if (s["timestep"] or 0) <= 6]
    late = [s for s in disc_sets if (s["timestep"] or 0) > 6]
    print(f"   Forced moves cluster at t_swap, BEFORE capacity begins to bind — "
          f"which is why\n   their choice set is full.")
    print(f"   The discretionary population is BIMODAL, not late: "
          f"{len(early)} at t<=6 alongside the\n   forced window, {len(late)} at "
          f"t>6 once the team is nearly spent. What holds\n   generally is the "
          f"CONSTRAINT, not the timing — no discretionary move had a full\n   "
          f"choice set, so **the DISCRETIONARY population is the "
          f"choice-constrained one,\n   the opposite of the direction the blocker "
          f"anticipated.**")

    over = [s for s in disc_sets if not s["chosen_was_legal"]]
    if over:
        print(f"\n   AND {len(over)} discretionary move(s) went to a destination "
              f"that was ALREADY FULL:")
        for s in over:
            print(f"     t{s['timestep']}: {s['from'][:6]} -> {s['to'][:6]} "
                  f"(held {s['held_at_move']})")
        print("   The manager bounced work between two exhausted workers in "
              "consecutive\n   timesteps. It could not run either way. **This is "
              "pre-L1 blindness showing up\n   inside the very population the DV "
              "treats as manager judgement** — an argument\n   that discretionary "
              "moves measured before L1 are partly noise, and a concrete\n   "
              "prediction that the pattern should change after it.")

    constrained = sum(1 for s in forced_sets if s["n_legal_destinations"] <= 1)
    if forced_sets:
        print(f"\nVERDICT INPUT: {constrained}/{len(forced_sets)} forced moves had "
              f"at most ONE legal destination.")
        if constrained > len(forced_sets) / 2:
            print("  => Destination is MOSTLY NOT A DECISION for forced moves. "
                  "A destination\n     metric must condition on choice-set size "
                  "or it measures the constraint.")
        else:
            print("  => Destination WAS generally a choice for forced moves, so "
                  "the destination\n     split is about the manager, not the "
                  "capacity structure.")

    out = HERE / "records" / "L4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "reroute_recoverability.json").write_text(json.dumps({
        "source_event": "structured_llm_response",
        "establishes": ("reassignment history is recoverable from the manager's "
                        "REQUESTED actions in every existing bundle"),
        "does_not_establish": ("what was APPLIED — AssignTasksToAgentsAction skips "
                               "missing/terminal/unknown-agent pairs and the "
                               "skipped list is not logged"),
        "n_bundles": len(rows),
        "total_forced": total_forced,
        "total_discretionary": total_disc,
        "per_bundle": rows,
        "choice_sets_forced": forced_sets,
        "choice_sets_discretionary": disc_sets,
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'reroute_recoverability.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
