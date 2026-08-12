"""L7 — `rerouted_share`, the brief's PRIMARY DV, over the ruled definition.

`STUDY1_FOUNDATION.md` §5 names this DV and it was built, orphaned by the revamp,
and left absent while the regret decomposition stood in for it. That substitution
is what produced a week of un-mixing failures: **regret is an OUTCOME that blends
allocation with execution quality, coverage structure and capacity; the DV is
BEHAVIOUR — did the manager move work off the newcomer.** An outcome aggregate
cannot be made to yield allocation behaviour, and each attempt failed differently.

DEFINITION AS RULED (LS b5744e4; `records/L7/rerouted_share_definition_v1.md`):

  DENOMINATOR — segment tasks that, at the moment of a manager action, were
  assigned to an agent STILL ON THE ROSTER and NOT YET TERMINAL. The set where
  leaving the work alone was a legal option. Work held by a departed agent is
  excluded because moving it is not a choice; unassigned work because there is
  nothing to reroute; terminal work because it cannot move.

  NUMERATOR — tasks in that set with at least one DISCRETIONARY move.

  UNIT — THE TASK, COUNTED ONCE. Move counts are reported separately and never
  divided by a task denominator: the first pass at this corpus produced 29 and 33
  for the same data because one counted tasks-with-a-change and the other counted
  moves. Both correct, different predicates, and a share mixing them exceeds 1.

  TASK denominator, not opportunity — an opportunity denominator is CONFOUNDED
  WITH EXECUTION SPEED, since work that finishes quickly offers fewer chances to
  move. That would reintroduce precisely the execution-into-allocation mixing this
  DV exists to remove.

  TWO POPULATIONS, NEVER SUMMED. FORCED (source agent has left the roster) is not
  a choice and is not in the share — but is NOT discarded: its DESTINATION is a
  decision, and handing the departed worker's queue wholesale to the newcomer is
  the brief's §7 failure mode #1, "allocating as if the predecessor remained".
  DISCRETIONARY (both agents present) carries the share.

  PRIMARY SHARE IS CONDITIONED ON >=2 CAPACITY-LEGAL DESTINATIONS. A move with one
  legal destination is not a choice and cannot evidence channel use. The
  unconditional share is descriptive beside it.

  APPLIED, not requested. A request the engine skipped did not change the
  allocation — but `applied=False` rows are reported, because a manager that tried
  and was skipped is behaviourally different from one that never tried.

WHAT THIS DV DOES NOT ESTABLISH, kept verbatim from the ruled definition because a
DV replacing an outcome aggregate must not inherit its overreach:

  * THAT A MOVE WAS CORRECT. Behaviour, not outcome. A manager can reroute heavily
    and lose score, or reroute nothing and lose more. The regret decomposition
    stays as the outcome measure; neither substitutes for the other.
  * ANYTHING AT 2-3 EPISODES PER CELL. No contrast verdict in either direction.
  * THAT THE MANAGER USED A CHANNEL. A move is consistent with using the card, the
    declaration, the ask, the trace, or none of them. Attribution needs the
    channel-pull record, separately.

PRE-L1 BUNDLES ARE NOT A BASELINE FOR EITHER POPULATION (LS ruling on Q4). Every
move in the 18 scope bundles occurred while refusals were firing invisibly, so no
clean pre-L1 sub-population exists — including the forced one. Those numbers are a
DESCRIPTIVE record of what the broken environment produced, never a "before".
"""

from __future__ import annotations

from typing import Any

SEGMENT_TASK_CLASS = "segment"


def _payloads(bundle: dict[str, Any], event_type: str) -> list[dict[str, Any]]:
    return [(e.get("payload") or {}) for e in bundle.get("events", [])
            if e.get("event_type") == event_type]


def _events_with_timestep(bundle: dict[str, Any],
                          event_type: str) -> list[tuple[int, dict[str, Any]]]:
    """(timestep, payload) pairs, with the timestep READ, never inferred.

    THE DEFECT THIS REPLACES (LS review, L7 blocker). The first version mapped the
    Nth applied assignment to the Nth timestep — correct only if exactly one
    assignment happens per timestep. **The manager bulk-assigns: the corpus shows
    nine assignments applied in a single timestep, which were attributed to nine
    consecutive ones.** The docstring said "timesteps are not on the assignment
    event; order is" and then used order AS the timestep — an INDEX used as a name
    for a predicate, which is this project's recurring shape. It corrupted the
    capacity view each move was judged against (the >=2-legal-destinations share
    ruled PRIMARY) and the roster each source was tested against, so the
    FORCED/DISCRETIONARY split itself could be misclassified.

    Fixed AT EMISSION: the engine wraps each timestep in `trace_scope(timestep=...)`
    so every event carries it. A wall-clock bracket against `timestep_completed`
    would also have worked and was rejected — it is reconstruction where the
    emitting site holds the fact, the same class of fragility removed from the
    choice sets one commit earlier.

    A missing timestep RAISES. Falling back to position would silently restore the
    defect on exactly the bundles that lack the field.
    """
    out: list[tuple[int, dict[str, Any]]] = []
    for event in bundle.get("events", []):
        if event.get("event_type") != event_type:
            continue
        if "timestep" not in event:
            raise ValueError(
                f"{event_type} event carries no timestep. This bundle predates the "
                f"emission-side fix (L7); its assignments cannot be placed in time "
                f"and the DV must not be computed on it."
            )
        out.append((int(event["timestep"]), event.get("payload") or {}))
    return out


def load_timeline(bundle: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Timestep -> the manager's load view, from L1's `manager_load_feedback`.

    LOGGED, NOT RECONSTRUCTED, and that is the point. Before L1 no per-timestep
    capacity state existed, so choice-set size had to be inferred by attributing
    execution starts to the nearest preceding observation — which moved a count by
    one whenever attribution slipped, making a 1-versus-2 legal set the fragile
    case, exactly where the discretionary population sits. Here the manager's own
    load view is the record.
    """
    timeline: dict[int, dict[str, Any]] = {}
    for payload in _payloads(bundle, "manager_load_feedback"):
        timestep = payload.get("timestep")
        if timestep is None:
            continue
        timeline[int(timestep)] = {
            row["agent_id"]: row for row in (payload.get("load") or [])
        }
    return timeline


def legal_destinations(view: dict[str, Any], exclude: str | None) -> list[str]:
    """Workers on the roster with room, per the manager's own load view.

    A worker is legal when EVERY capacity dimension it reports has room. Checking
    only the binding one would call a worker legal on its allotment while it is
    concurrency-blocked, which is the same class of error as reporting load against
    a limit that never binds.
    """
    out = []
    for agent_id, row in view.items():
        if agent_id == exclude:
            continue
        dimensions = row.get("dimensions") or []
        if dimensions and all(d["held"] < d["capacity"] for d in dimensions):
            out.append(agent_id)
    return sorted(out)


def moves(bundle: dict[str, Any]) -> dict[str, Any]:
    """Every assignment the manager made, split into the two populations.

    Roster membership is taken from the load timeline rather than from the
    manifest's rosters: the manifest says who was scheduled, the timeline says who
    was actually present when the manager acted, and cell U's `roster_post_swap`
    is counterfactual — a field that is correct in five cells and false in the
    control, which has already cost this project one retracted claim.
    """
    timeline = load_timeline(bundle)
    applied: list[tuple[int, dict[str, Any]]] = []
    requested_not_applied: list[dict[str, Any]] = []

    for step, payload in _events_with_timestep(bundle, "task_assigned"):
        if payload.get("applied"):
            applied.append((step, dict(payload)))
        else:
            requested_not_applied.append(dict(payload))

    forced: list[dict[str, Any]] = []
    discretionary: list[dict[str, Any]] = []
    first_assignment = 0
    for step, row in applied:
        if not row.get("is_reassignment"):
            first_assignment += 1
            continue
        # The capacity view the manager ACTUALLY held when it made this move.
        #
        # A MISSING VIEW MUST NOT DEFAULT TO A POPULATION. With `timeline.get(step,
        # {})` an absent view makes every agent look absent, so the source looks
        # departed and the move is silently filed as FORCED — absence and evidence
        # rendered identical, in the classification the entire DV rests on. Caught
        # when the acceptance moved a task at a timestep with no recorded view and
        # the module reported a forced move rather than complaining.
        if step not in timeline:
            raise ValueError(
                f"assignment at timestep {step} has no manager load view in this "
                f"bundle, so who was present cannot be established and the "
                f"forced/discretionary split is not computable for it"
            )
        view = timeline[step]
        source_present = row["from_agent_id"] in view
        move = {
            **row,
            "timestep": step,
            "source_present": source_present,
            "n_legal_destinations": len(
                legal_destinations(view, row["from_agent_id"])),
            "legal_destinations": legal_destinations(view, row["from_agent_id"]),
        }
        # FORCED = the source has left. Not a judgement about the newcomer; the
        # work cannot run where it is, so moving it is the only legal action.
        (discretionary if source_present else forced).append(move)

    return {
        "n_first_assignments": first_assignment,
        "forced": forced,
        "discretionary": discretionary,
        "requested_not_applied": requested_not_applied,
    }


def eligible_tasks(bundle: dict[str, Any]) -> set[str]:
    """The DENOMINATOR predicate, applied.

    A segment task is eligible once it has been assigned to an agent who is still
    present at a LATER manager decision while the task is not terminal — the
    moment at which leaving it where it was became a legal option. A task assigned
    only at the final decision was never left alone by choice and is excluded.
    """
    timeline = load_timeline(bundle)
    ordered_steps = sorted(timeline)

    # TERMINALITY IS EVALUATED AT THE STEP, NOT OVER THE EPISODE (RR blocker 1).
    # The first version tested `task_id not in terminal` against an EPISODE-WIDE
    # completion set inside a per-step loop — a condition that does not vary with
    # the loop variable, so it reduced to **"any task that ever completed is never
    # eligible"**. The ruled predicate is "not yet terminal AT THE MOMENT OF THE
    # MANAGER ACTION": a task movable at t5 that completed at t20 was eligible at
    # t5. Measured on the corpus, 140 of 162 segment tasks eventually complete, so
    # the defect kept ~14% of the denominator and, a small denominator inflating a
    # share, biased the DV upward by roughly 7x.
    #
    # It could not fire on the machinery episode, which has ZERO segment
    # completions — the one input on which an episode-wide completion set and a
    # per-step one are the same set.
    completed_at: dict[str, int] = {}
    for completion in bundle.get("completions", []):
        task_id = str(completion["task_id"])
        step = completion.get("timestep")
        if step is None:
            raise ValueError(
                f"completion for {task_id} carries no timestep, so terminality "
                f"cannot be evaluated per step and the denominator is not "
                f"computable for this bundle"
            )
        completed_at[task_id] = min(completed_at.get(task_id, int(step)), int(step))

    eligible: set[str] = set()
    for step, row in _events_with_timestep(bundle, "task_assigned"):
        if not row.get("applied") or row.get("task_class") != SEGMENT_TASK_CLASS:
            continue
        task_id = str(row.get("task_id"))
        assignee = row.get("to_agent_id")
        # "A LATER manager decision" is later IN TIME, not later in the stream.
        # The denominator carried the same positional defect as the split.
        for later_step in [s for s in ordered_steps if s > step]:
            if (assignee in timeline[later_step]
                    and completed_at.get(task_id, later_step + 1) > later_step):
                eligible.add(task_id)
                break
    return eligible


def _uncovered_to_successor(bundle: dict[str, Any],
                            forced: list[dict[str, Any]]) -> dict[str, Any]:
    """Forced moves onto the successor for work the successor CANNOT do.

    The discriminating form of failure mode #1. Coverage comes from the instance's
    own `irb_coverage`, so this needs an instance in the bundle; where it is
    absent the quantity reports UNCOMPUTABLE rather than 0, because a zero here
    would read as "the manager never did this" when it means "we could not look".
    """
    instance = bundle.get("instance") or {}
    workers = {w["worker_id"]: w for w in instance.get("workers", [])}
    segments = {s["segment_id"]: s for s in instance.get("segments", [])}
    index = (bundle.get("index") or {}).get("segment_task_ids") or {}
    task_to_segment = {str(v): k for k, v in index.items()}
    successor = bundle["manifest"].get("successor_id")

    if not workers or not segments or not task_to_segment:
        return {"computable": False,
                "why": ("the bundle carries no instance/index, so segment class "
                        "and worker coverage cannot be resolved"),
                "n_uncovered": None, "n_forced_to_successor": None}

    uncovered = 0
    to_successor = 0
    for move in forced:
        if move["to_agent_id"] != successor:
            continue
        to_successor += 1
        segment = segments.get(task_to_segment.get(str(move["task_id"]), ""))
        worker = workers.get(successor)
        if segment is None or worker is None:
            continue
        # Only IRB-approved segments can be "uncovered": an SA segment is
        # computable by anyone, so routing it anywhere is never a coverage error.
        if segment.get("irb_approved") and (
                segment.get("asset_class") not in (worker.get("irb_coverage") or ())):
            uncovered += 1

    return {
        "computable": True,
        "n_forced_to_successor": to_successor,
        "n_uncovered": uncovered,
        "population": ("forced moves whose destination is the successor, "
                       "restricted to IRB-approved segments whose asset class is "
                       "outside the successor's approval scope"),
        "comparator": ("forced moves to the successor overall — the unrestricted "
                       "count, which capacity-optimal play alone explains"),
    }


def rerouted_share(bundle: dict[str, Any]) -> dict[str, Any]:
    """The DV, with both shares and every population stated as a PREDICATE."""
    # A HOLLOW LOAD TIMELINE MUST NOT YIELD A NUMBER (RR limitation).
    # `legal_destinations` correctly refuses to count a row with no dimensions —
    # but if EVERY row is hollow, `n_legal_destinations` is 0 everywhere, the
    # conditioned set is empty, and the primary share returns a confident `0.0`.
    # A share of zero and an unmeasurable share are different statements and this
    # is the third place in this project where they were rendered identically.
    timeline = load_timeline(bundle)
    substantive = any(row.get("dimensions") for view in timeline.values()
                      for row in view.values())
    if timeline and not substantive:
        raise ValueError(
            "no timestep in this bundle carries a load row with capacity "
            "dimensions, so no destination can be shown legal and the conditioned "
            "share would be 0.0 for want of data rather than for want of moves"
        )

    split = moves(bundle)
    eligible = eligible_tasks(bundle)

    disc_segments = [m for m in split["discretionary"]
                     if m.get("task_class") == SEGMENT_TASK_CLASS]
    moved = {str(m["task_id"]) for m in disc_segments} & eligible
    chose = {str(m["task_id"]) for m in disc_segments
             if m["n_legal_destinations"] >= 2} & eligible

    def share(numerator: set[str]) -> float | None:
        return len(numerator) / len(eligible) if eligible else None

    forced_segments = [m for m in split["forced"]
                       if m.get("task_class") == SEGMENT_TASK_CLASS]

    return {
        # PRIMARY. A move with one legal destination is not a choice and cannot
        # evidence channel use.
        "rerouted_share_conditioned": share(chose),
        "rerouted_share_unconditional": share(moved),
        "denominator_predicate": (
            "segment tasks assigned to an agent still on the roster at a later "
            "manager decision while not terminal — the set where leaving the work "
            "alone was a legal option"
        ),
        "n_eligible": len(eligible),
        "n_moved": len(moved),
        "n_moved_with_real_choice": len(chose),
        "numerator_predicate_conditioned": (
            "eligible tasks with >=2 capacity-legal destinations at the move"),
        "n_discretionary_moves": len(disc_segments),
        "n_forced_moves": len(forced_segments),
        # Forced moves are analysed on DESTINATION, never folded into the share.
        "forced_destinations": {
            "to_successor": sum(
                1 for m in forced_segments
                if m["to_agent_id"] == (bundle["manifest"].get("successor_id"))),
            "to_incumbent": sum(
                1 for m in forced_segments
                if m["to_agent_id"] != (bundle["manifest"].get("successor_id"))),
        },
        # THE RESTRICTED QUANTITY, which is the one that can discriminate (LS,
        # after RR killed the unrestricted version). Forced-to-successor is
        # recommended by BOTH failure mode #1 ("allocating as if the predecessor
        # remained") AND by capacity-optimal play, because the arriving successor
        # is simply the emptiest destination — so the raw split would have been
        # "confirmed" by the repair merely working, and discriminates nothing.
        #
        # Restricting to segments the successor does NOT cover removes the
        # capacity-optimal reading: moving work to a worker who cannot do it is
        # not explicable as good scheduling. **Without this, failure mode #1 is
        # unfalsifiable in the direction that matters.**
        "forced_to_successor_uncovered": _uncovered_to_successor(
            bundle, forced_segments),
        "n_requested_not_applied": len(split["requested_not_applied"]),
        "establishes": "manager allocation BEHAVIOUR on this episode",
        "does_not_establish": (
            "that any move was correct, that any channel was used, or any "
            "contrast at 2-3 episodes per cell"
        ),
    }
