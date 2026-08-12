"""L2a — the segment-state split, re-derived against the REPAIRED instrument.

The four-way split was built to answer "where did the regret go", and every
version of it inherited a defect from the record it read.

  V1 derived state from `allocation`, which is built by walking COMPLETIONS. Work
  the manager assigned and the engine never ran could not be represented, so it
  collapsed into `__unstaffed__` — a label asserting the manager never staffed
  work it had staffed. That produced "non-routing, 48.3% of regret", which was
  false and is retracted.

  V2 (`finance_scope_report.segment_states`) fixed that by reading the ASSIGNMENT
  record — but read it from `task_board_final`, a TERMINAL SNAPSHOT in which a
  task assigned once and a task reassigned three times are indistinguishable, and
  matched segments by DISPLAY NAME (`"Risk-weighted assets — {id}"`), the exact
  predicate criterion (e) removed from the metering path for silently killing a
  manager remediation.

  V3, HERE, reads the records L1 and L7 added: `task_assigned` for the assignment
  history with timesteps, the logged refusal REASON enum for why work did not
  run, and explicit `task_class` for segment identity. Nothing is inferred from a
  name or from a terminal snapshot.

WHAT CHANGES SUBSTANTIVELY, not just in provenance: `assigned_but_unexecuted` was
one bucket and is now THREE, because the scope run showed it was two populations
with opposite meanings — 20 segments permanently barred by a spent allotment and
2 cut off by the horizon. Pooling them produced a rate that could not carry a
sign. The reason comes from the logged enum computed at the refusal site, NOT
from the concurrency-field signature, which asserts a permanently-barred worker
is idle and available on 58% of refusals.

THIS MODULE COMPUTES CODE, NOT NUMBERS. It is acceptance-tested on a zero-API
machinery episode. The split's VALUES on real episodes are part of L3's analysis,
on L3's bundles — L2 as originally written was circular, since the repaired
instrument only produces bundles once L3 runs.
"""

from __future__ import annotations

from typing import Any

from manager_agent_gym.core.workflow_agents.interface import (
    REFUSAL_CONCURRENCY, REFUSAL_SEGMENT_ALLOTMENT, REFUSAL_UNAVAILABLE)

SEGMENT_TASK_CLASS = "segment"

# ---------------------------------------------------------------------------
# ALLOTMENT_UNREACHABLE (researcher ruling L14, implemented 2026-08-09)
#
# `refused_allotment` CANNOT FIRE. `REFUSAL_SEGMENT_ALLOTMENT` had exactly one
# emission site — the allotment branch in `CapacityBoundedAIAgent.refusal_reasons`
# — and that branch, `segment_capacity`, `segment_task_ids` and the `execute_task`
# consumption are all removed. The code constant survives in `interface.py` and is
# still classified here so an old bundle replays into the same bucket it was
# scored into; nothing NEW can produce it.
#
# THIS IS THE THIRD MEMBER OF THE SAME FAMILY, and the family is worth naming:
# `MANIPULATION_UNREACHABLE` (refused_unavailable), `KNOWN_POOLING`
# (executed_and_declined), and now this. In every case the STATE IS KEPT so the
# partition stays total, and the ZERO IS MARKED so it is never read as evidence.
#
# WHY IT WAS REMOVED, since a bare "unreachable" invites re-adding it: the
# allotment charged a slot BEFORE the work ran and released nothing on failure, so
# a failed execution permanently burned capacity and the refusals that followed
# scored as ALLOCATION outcomes. On the one classifiable bundle that contamination
# WAS the entire DV. I argued for keeping it and lost on exactly this consequence.
#
# THE COST, STATED: this retires the only DV state we had ever observed fire. The
# DV now rests on `never_assigned` and `executed_and_declined`, and if a future
# bundle shows both at zero that is a MEASUREMENT problem to raise, not a null.
ALLOTMENT_UNREACHABLE = True

# The codes this split knows how to classify. An unknown code RAISES: a new
# refusal branch must be given a meaning here rather than silently inheriting one.
KNOWN_REFUSAL_CODES: frozenset[str] = frozenset({
    REFUSAL_UNAVAILABLE, REFUSAL_CONCURRENCY, REFUSAL_SEGMENT_ALLOTMENT})

# Every state is a PREDICATE, not a name (§B). The names below are labels for
# these sentences, and where the two ever disagree the sentence wins.
STATE_PREDICATES: dict[str, str] = {
    "never_assigned":
        "no APPLIED assignment event names this segment — the manager never "
        "staffed it. NOT 'it did not run': that was the v1 defect.",
    "refused_allotment":
        "assigned, never executed, and at least one refusal on it names the "
        "segment allotment. STRUCTURALLY UNREACHABLE AS THE HARNESS STANDS — a "
        "count of 0 here is UNINFORMATIVE, not a finding. See "
        "ALLOTMENT_UNREACHABLE.",
    # ★ THE SECOND CLAUSE IS RETRACTED (2026-08-09, RR found it, LS verified at
    # source). It asserted a capability the harness does not have, and it was
    # quoted twice as the authority for a ruling.
    #
    # A ROSTER CHANGE CANNOT CAUSE THIS STATE. Nothing in the repo ever sets
    # `is_available = False` — it is declared True at interface.py:82 and
    # telemetry.py:58 and every other occurrence is a read — and the swap calls
    # `remove_agent`, which REMOVES the worker rather than marking it unavailable.
    # The branch at interface.py:105 is dead code, so a swap run CANNOT see this
    # state separately; it cannot see it at all.
    #
    # The predicate's FIRST clause still describes what the state would mean if it
    # could fire, so it is kept and the state stays in the partition. The claim
    # about what a swap run can observe is withdrawn. See
    # `five_bucket_split.MANIPULATION_UNREACHABLE` for the trace and for where an
    # assignment to a departed worker actually goes, which is nowhere.
    "refused_unavailable":
        "assigned, never executed, and a refusal named the assignee as "
        "UNAVAILABLE. RETRACTED: 'which a roster change can cause, so this is the "
        "state a swap run must be able to see separately' — UNREACHABLE as "
        "implemented; a count of 0 here is structural, not behavioural",
    "refused_concurrency":
        "assigned, never executed, and every refusal on it names only "
        "concurrency — transient, and it would have run given more timesteps",
    "unexecuted_no_refusal":
        "assigned, never executed, and NO refusal fired on it — the horizon "
        "ended first, or it never became ready",
    "executed_but_unparseable":
        "executed, but the deliverable yielded no rwa value and was not a "
        "permitted decline",
    "executed_and_declined":
        "executed, and the worker returned the permitted decline form — a "
        "legitimate outcome, distinct from an unreadable deliverable although "
        "both score zero",
    "executed_and_parsed":
        "executed and yielded an rwa value, correct or not — correctness is the "
        "scorer's business, not this split's",
}


def _payloads(bundle: dict[str, Any], event_type: str) -> list[dict[str, Any]]:
    return [(e.get("payload") or {}) for e in bundle.get("events", [])
            if e.get("event_type") == event_type]


def segment_task_ids(bundle: dict[str, Any]) -> dict[str, str]:
    """segment_id -> task_id, from the INDEX. Never from the task's name.

    The name predicate is what charged a manager-created remediation to an
    allotment and refused it thirteen times without saying so. It is not used
    here for the same reason it is not used there.
    """
    index = (bundle.get("index") or {}).get("segment_task_ids") or {}
    return {segment_id: str(task_id) for segment_id, task_id in index.items()}


def interpretable_counts(result: dict[str, Any]) -> dict[str, int]:
    """`counts`, but it RAISES rather than hand back a number that asserts
    something the bundle cannot support.

    WHY THIS EXISTS RATHER THAN A FIELD (RR). `split()` already reports
    `uninterpretable_states`, and that is strictly better than the printed banner
    it replaced — but **the argument against the banner applies to a field too.**
    `counts` still carries an ordinary-looking integer for a state whose PREDICATE
    does not hold, and a consumer that reads `counts` and ignores the flag
    reproduces exactly the claim the flag exists to prevent. A default one level
    up: the safe read is the one that requires an extra step, so the unsafe read
    is the one that happens.

    So the guard is a CODE PATH, not a rule for readers. Anything reporting these
    counts calls this; anything needing the raw partition (residual, arithmetic)
    reads `counts` directly and knowingly.

    THE LIMITATION THAT REMAINS, stated rather than papered over: nothing PREVENTS
    a consumer reading `result["counts"]`. Removing the state from `counts` would
    break the partition — the one thing here reviewed twice and passed — so the
    residual risk is accepted, and this makes the safe path the easy one rather
    than the only one.
    """
    blocked = result.get("uninterpretable_states") or []
    if blocked:
        raise ValueError(
            f"{blocked} cannot be interpreted for this bundle: "
            f"{result.get('uninterpretable_reason')} "
            f"Read `counts` directly if you need the partition arithmetic, but do "
            f"not report these states' predicates for this bundle."
        )
    return dict(result["counts"])


def split(bundle: dict[str, Any]) -> dict[str, Any]:
    """Per-segment state, plus counts, plus a residual that must be zero."""
    by_segment = segment_task_ids(bundle)
    if not by_segment:
        raise ValueError(
            "bundle carries no segment index, so segment identity cannot be "
            "established; a split computed by name would reintroduce the "
            "predicate criterion (e) removed"
        )

    # THE DEFAULT-MUST-NOT-BE-A-LEGAL-VALUE RULE, VIOLATED IN THIS MODULE'S OWN
    # NEW CODE (RR). `payload.get("applied")` and `payload.get("task_class")` both
    # returned None on a MISSING field, which is falsy — so the task fell out of
    # `assigned` and its segment was classified **never_assigned**.
    #
    # That is not a conservative default. `never_assigned` ASSERTS THE MANAGER
    # NEVER STAFFED THE SEGMENT — the exact false claim v1 made and that this
    # module exists to stop making — and it was reachable by a payload merely
    # lacking a field. Demonstrated on constructed bundles with every existing
    # check still passing.
    #
    # Absence is now an ERROR, not a state. A bundle that cannot say whether an
    # assignment was applied cannot be split, and saying so beats inventing the
    # most damaging answer.
    assigned: set[str] = set()
    for payload in _payloads(bundle, "task_assigned"):
        task_id = str(payload.get("task_id"))
        for field in ("applied", "task_class"):
            if field not in payload:
                raise ValueError(
                    f"task_assigned on {task_id} carries no {field!r}. A missing "
                    f"{field!r} used to fall through to `never_assigned`, which "
                    f"asserts the manager never staffed the segment — a stronger "
                    f"claim than the data supports and the one this split exists "
                    f"to stop making"
                )
        if payload["applied"] and payload["task_class"] == SEGMENT_TASK_CLASS:
            assigned.add(task_id)

    # THE REASON COMES FROM THE LOGGED ENUM, computed at the refusal site.
    # Deriving it from `agent_current_task_count` / `agent_max_concurrent` would
    # assert that a permanently-barred worker is idle and below cap, which is what
    # those fields say on 58% of refusals.
    refusals: dict[str, list[str]] = {}
    for payload in _payloads(bundle, "assignment_deferred"):
        task_id = str(payload.get("task_id"))
        codes = payload.get("refusal_codes")
        if codes is None:
            raise ValueError(
                f"deferral on {task_id} carries no refusal_codes; this bundle "
                f"predates the structured-code fix and its refusal causes are not "
                f"recoverable — classifying by substring over the prose is how "
                f"an availability refusal came to be recorded as a concurrency one"
            )
        unknown = [c for c in codes if c not in KNOWN_REFUSAL_CODES]
        if unknown:
            # AN UNKNOWN CODE RAISES rather than falling into a bucket. The
            # previous `elif reasons:` was a catch-all, so any refusal branch added
            # later would have landed in `refused_concurrency` silently, with the
            # partition intact and the residual zero.
            raise ValueError(
                f"deferral on {task_id} carries unknown refusal code(s) "
                f"{unknown}; a new refusal branch has been added and this split "
                f"has not been told what it means"
            )
        refusals.setdefault(task_id, []).extend(codes)

    executed = {str(c["task_id"]) for c in bundle.get("completions", [])}
    detail = bundle.get("parse_detail") or {}

    states: dict[str, str] = {}
    for segment_id, task_id in by_segment.items():
        if task_id in executed:
            # ABSENT FROM `parse_detail` IS NOT THE SAME AS PRESENT-AND-UNPARSEABLE
            # (RR). `detail.get(segment_id) or {}` collapsed the two: a segment the
            # parser never saw got `rwa is None` and was classified
            # **executed_but_unparseable**, which asserts the WORKER produced
            # something unreadable. The real condition is that our own parser has
            # no record of a segment that demonstrably executed — a defect in the
            # analysis path, not an observation about the worker.
            #
            # SCOPED TO A **PARTIAL** parse_detail, which is the condition RR
            # demonstrated. An ENTIRELY EMPTY parse_detail is a different and
            # legitimate thing: no parsing pass was run at all, which is how a
            # MACHINERY episode arrives (zero model calls, so there are no
            # deliverables to parse). Raising on that would reject a bundle whose
            # only fault is having no worker output, and the L2a acceptance's own
            # case 1 is exactly it.
            #
            # LIMITATION, STATED RATHER THAN FIXED: with an empty parse_detail the
            # executed segments still land in `executed_but_unparseable`, whose
            # predicate says "the DELIVERABLE yielded no rwa value" — a claim about
            # the worker that a machinery run does not support. The count is right
            # and the sentence over-claims. Fixing it needs a ninth state
            # (`executed_not_parsed`) or an explicit `parsing_performed` flag, and
            # that changes the partition, which is outside what these blockers
            # authorise.
            if detail and segment_id not in detail:
                raise ValueError(
                    f"segment {segment_id} executed (task {task_id}) but is absent "
                    f"from a NON-EMPTY parse_detail. That used to be recorded as "
                    f"`executed_but_unparseable`, which blames the worker for a "
                    f"gap in our own parsing; the two are different conditions and "
                    f"only one of them is a finding"
                )
            # `.get` is safe ONLY because the partial-gap case raised above: the
            # sole way to reach here without an entry is a wholly empty
            # parse_detail, i.e. no parsing pass.
            parsed = detail.get(segment_id) or {}
            if parsed.get("declined"):
                states[segment_id] = "executed_and_declined"
            elif parsed.get("rwa") is None:
                states[segment_id] = "executed_but_unparseable"
            else:
                states[segment_id] = "executed_and_parsed"
        elif task_id not in assigned:
            states[segment_id] = "never_assigned"
        else:
            codes = set(refusals.get(task_id, []))
            # CLASSIFIED ON THE CODE, never on the prose. The previous version
            # tested `"allotment" in r` over a formatted English sentence — the
            # display-name predicate one level down. It was already wrong: the
            # base class's availability refusal contains no "allotment", so it
            # fell through the catch-all and was recorded as CONCURRENCY. That
            # never fired in the scope run because every deferral had
            # available=True — and availability is exactly what a roster change
            # touches, which is what L3 is.
            #
            # Ordered by PERMANENCE, and stated rather than left to branch order:
            # an allotment never releases within an episode, unavailability may,
            # concurrency certainly does. The most permanent cause is the one
            # that changes what the manager should do.
            if REFUSAL_SEGMENT_ALLOTMENT in codes:
                states[segment_id] = "refused_allotment"
            elif REFUSAL_UNAVAILABLE in codes:
                states[segment_id] = "refused_unavailable"
            elif REFUSAL_CONCURRENCY in codes:
                states[segment_id] = "refused_concurrency"
            else:
                states[segment_id] = "unexecuted_no_refusal"

    counts = {state: sum(1 for s in states.values() if s == state)
              for state in STATE_PREDICATES}

    # THE RESIDUAL CHECK COULD NOT FIRE ON ANY DATA, AND THAT IS WORSE THAN NOT
    # HAVING IT (RR). `states` is only ever assigned one of the eight literals that
    # `counts` sums over, so `sum(counts) == len(states) == len(by_segment)` holds
    # BY CONSTRUCTION. Verified zero on well-formed input and on all three
    # malformed bundles above — a check that cannot fail on data is documentation
    # wearing an assertion's clothes, and it was the thing standing where a real
    # guard should have been while all three defects above passed silently.
    #
    # It is kept as an INVARIANT (it should hold, and a code change that breaks it
    # is a bug) but it is no longer the partition guard.
    residual = len(by_segment) - sum(counts.values())
    if residual:
        raise AssertionError(
            f"internal invariant broken: {len(by_segment)} segments, "
            f"{sum(counts.values())} classified, residual {residual}. This cannot "
            f"be caused by bundle data — every state is one of the eight literals "
            f"counts sums over — so it means the classifier and STATE_PREDICATES "
            f"have diverged"
        )

    # THE GUARD THAT ACTUALLY CHECKS THE DATA (RR's replacement): every segment
    # task the bundle says was ASSIGNED must appear in the segment index. If it
    # does not, the index and the event stream disagree about which tasks are
    # segments — a real, silent index/event divergence that the residual could
    # never have caught, and which would put the DV's denominator and its numerator
    # on different populations.
    indexed = set(by_segment.values())
    orphans = sorted(assigned - indexed)
    if orphans:
        raise ValueError(
            f"{len(orphans)} task(s) logged as assigned segment tasks are absent "
            f"from the segment index: {orphans[:5]}. The index and the event "
            f"stream disagree about which tasks are segments, so the split's "
            f"denominator and the assignment evidence describe different "
            f"populations"
        )

    # A QUANTITY WHOSE PREDICATE DOES NOT HOLD FOR A POPULATION REFUSES TO BE
    # INTERPRETED FOR IT, rather than the partition being rebuilt around the gap.
    #
    # `executed_but_unparseable` is predicated on "the DELIVERABLE yielded no rwa
    # value" — a claim about the WORKER. With no parsing pass at all (a machinery
    # run: zero model calls, so no deliverables exist) the COUNT is right and the
    # SENTENCE does not hold. The eight predicates and the partition are untouched;
    # what changes is that the bucket declines to be read for this bundle.
    #
    # CARRIED IN THE RECORD, NOT ONLY IN A PRINTED BANNER. A banner is dropped by
    # the first summariser that reformats the output, and every consumer of this
    # split reads `counts` — so the non-interpretability travels with the data
    # structure the numbers travel in.
    parsing_performed = bool(detail)
    uninterpretable = [] if parsing_performed else ["executed_but_unparseable"]

    return {
        "states": states,
        "counts": counts,
        "predicates": dict(STATE_PREDICATES),
        "n_segments": len(by_segment),
        "residual": residual,
        "parsing_performed": parsing_performed,
        "uninterpretable_states": uninterpretable,
        "uninterpretable_reason": (
            None if parsing_performed else
            "NO PARSING PASS RAN on this bundle (parse_detail is empty), so "
            "`executed_but_unparseable` counts segments that executed and were "
            "never parsed. Its predicate — 'the DELIVERABLE yielded no rwa "
            "value' — is a claim about the WORKER and is NOT SUPPORTED here. The "
            "count is correct; the state's sentence must not be quoted for this "
            "bundle."
        ),
        "comparator": "the segment denominator for this episode",
        "establishes": "where each segment ENDED UP, by cause",
        "does_not_establish": (
            "how much regret each state cost — that is the scorer's "
            "decomposition, and a count is not a loss"
        ),
    }
