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
        "segment allotment — permanently barred, since the allotment never "
        "releases within an episode",
    "refused_unavailable":
        "assigned, never executed, and a refusal named the assignee as "
        "UNAVAILABLE — which a roster change can cause, so this is the state a "
        "swap run must be able to see separately",
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


def split(bundle: dict[str, Any]) -> dict[str, Any]:
    """Per-segment state, plus counts, plus a residual that must be zero."""
    by_segment = segment_task_ids(bundle)
    if not by_segment:
        raise ValueError(
            "bundle carries no segment index, so segment identity cannot be "
            "established; a split computed by name would reintroduce the "
            "predicate criterion (e) removed"
        )

    assigned: set[str] = set()
    for payload in _payloads(bundle, "task_assigned"):
        if payload.get("applied") and payload.get("task_class") == SEGMENT_TASK_CLASS:
            assigned.add(str(payload.get("task_id")))

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
        parsed = detail.get(segment_id) or {}
        if task_id in executed:
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
    # THE BUCKETS PARTITION THE SEGMENTS. A residual is a defect, not a
    # measurement — the same discipline as the regret decomposition's.
    residual = len(by_segment) - sum(counts.values())
    if residual:
        raise ValueError(
            f"the split does not partition: {len(by_segment)} segments, "
            f"{sum(counts.values())} classified, residual {residual}"
        )

    return {
        "states": states,
        "counts": counts,
        "predicates": dict(STATE_PREDICATES),
        "n_segments": len(by_segment),
        "residual": residual,
        "comparator": "the segment denominator for this episode",
        "establishes": "where each segment ENDED UP, by cause",
        "does_not_establish": (
            "how much regret each state cost — that is the scorer's "
            "decomposition, and a count is not a loss"
        ),
    }
