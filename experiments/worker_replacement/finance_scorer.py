"""S4 — truth functions, scorer, oracle/worst, and DECOMPOSED regret.

No LLM judge appears anywhere in this layer, by construction: every quantity here
is a deterministic function of the instance and the reported numbers.

THE DECOMPOSITION, which is the point of this module. For a run:

    allocation_loss = oracle(I)              − score(I, allocation)
    execution_loss  = score(I, allocation)   − achieved(I, allocation, reports)
    ------------------------------------------------------------------
    total regret    = oracle(I)              − achieved(...)

The middle term `score(I, allocation)` — what the chosen assignees WOULD attain
under faithful execution — cancels, so the two components sum to total regret
*identically*, not approximately. That is deliberate: conflating them would
attribute worker failure to the manager, and the decomposition is also the
instrument that would detect a fabricating-worker regime (S10), where execution
loss goes large and uncontrolled while allocation loss stays small.

EXECUTION LOSS IS SIGNED, AND CAN BE NEGATIVE. Found while building S4's
hand-checked case, and it is a property of the instrument rather than a defect:
a worker that deviates from faithful execution can land CLOSER to the truth than
faithful execution would have. Concretely, a worker misrouted onto an
IRB-applicable segment faithfully reports the SA fallback, which here overstates
the IRB truth by ~35%; if it then under-reports by 20% it moves toward the truth
and scores BETTER than faithful execution, giving execution_loss < 0.

Two consequences worth stating rather than discovering later:
  * "loss" is a misnomer for that term in the negative regime — it is a signed
    deviation, and reporting it as a loss without the sign would be misleading;
  * it BOUNDS what the decomposition can do for S10. A fabricating worker whose
    invented number happens to fall nearer the truth than its own SA fallback
    registers as negative execution loss, i.e. fabrication is not detectable from
    the sign of this term alone. S10's value/trace/absence detectors are the
    instrument for that; this decomposition attributes, it does not detect.

SINGLE SOURCE. The IRB capital function is imported from the S1-validated module
by identity; the SA table and lookup come from S3's generator. There is no third
copy of either, and the acceptance test asserts that by object identity.
"""

from __future__ import annotations

from itertools import product
from typing import Any, Iterable

from manager_agent_gym.core.common.run_trace import record_run_event
from .finance_generator import TIE_EPS, irb_risk_weight_for, sa_risk_weight

# Reported numbers are compared to truth with a relative tolerance. Below it, a
# report counts as exact; above it, the score degrades linearly to zero at 100%
# relative error. The tolerance exists because a worker reporting a correctly
# computed number may round it.
REPORT_TOLERANCE = 1e-6


def applicable_approach(segment: dict[str, Any]) -> str:
    """Which approach APPLIES to this segment. A property of the segment."""
    return "IRB" if segment["irb_approved"] else "SA"


def sa_rwa(segment: dict[str, Any]) -> float:
    """RWA under the standardised approach. Needs only the public rating."""
    return segment["ead"] * sa_risk_weight(segment["asset_class"], segment["rating"])


def irb_rwa(segment: dict[str, Any], worker: dict[str, Any]) -> float | None:
    """RWA under IRB, or None if this worker lacks the calibration for the class."""
    risk_weight = irb_risk_weight_for(segment, worker)
    return None if risk_weight is None else segment["ead"] * risk_weight


def correct_rwa(segment: dict[str, Any],
                calibration: dict[str, dict[str, float]]) -> float:
    """The right answer for this segment: the APPLICABLE approach, computed correctly.

    Note this is worker-independent — it is the truth, not anyone's attainment. For
    an IRB-approved segment the IRB number is correct even for a worker that cannot
    produce it; that worker's SA fallback is then a wrong answer *for this segment*,
    which is the real compliance failure being modelled.
    """
    if applicable_approach(segment) == "SA":
        return sa_rwa(segment)
    return segment["ead"] * _irb_risk_weight_unrestricted(segment, calibration)


def _irb_risk_weight_unrestricted(
        segment: dict[str, Any],
        calibration: dict[str, dict[str, float]]) -> float:
    """IRB risk weight ignoring coverage — used only to define TRUTH, never attainment."""
    from .test_basel_reference import capital_requirement

    return 12.5 * capital_requirement(
        calibration[segment["asset_class"]][segment["rating"]],
        segment["lgd"], segment["maturity"],
    )


def score_report(segment: dict[str, Any], reported: float | None,
                 calibration: dict[str, dict[str, float]]) -> float:
    """Score a reported RWA against the segment's truth. 1.0 = exact, 0.0 = useless.

    Graded rather than binary so that a wrong-approach answer is penalised in
    PROPORTION to how wrong it is — which is what makes the spread depend on the
    real SA/IRB divergence rather than on a step function.
    """
    if reported is None:
        return 0.0
    truth = correct_rwa(segment, calibration)
    if truth == 0.0:
        # Sovereign AAA under SA has RW 0%, so relative error is undefined. Exact
        # agreement scores 1, anything else scores 0 — there is no meaningful
        # gradation against a zero denominator.
        return 1.0 if abs(reported) <= REPORT_TOLERANCE else 0.0
    relative_error = abs(reported - truth) / abs(truth)
    if relative_error <= REPORT_TOLERANCE:
        return 1.0
    return 1.0 - min(1.0, relative_error)


def attainable_report(segment: dict[str, Any], worker: dict[str, Any]) -> float:
    """What this worker reports under FAITHFUL execution.

    Three cases, exactly as pinned:
      * applicable is IRB and the worker holds the calibration -> the IRB number;
      * applicable is IRB and it does not                      -> the SA fallback;
      * applicable is SA                                       -> the SA number,
        which every worker can produce (universal fallback, so nobody is switched
        off and SA-applicable segments contribute zero spread).
    """
    if applicable_approach(segment) == "SA":
        return sa_rwa(segment)
    covered = irb_rwa(segment, worker)
    return covered if covered is not None else sa_rwa(segment)


def s(segment: dict[str, Any], worker: dict[str, Any],
      calibration: dict[str, dict[str, float]]) -> float:
    """s(seg, w) — the score w ATTAINS on seg under faithful execution."""
    return score_report(segment, attainable_report(segment, worker), calibration)


def _resolve_roster(
    instance: dict[str, Any], workers: list[dict] | None, phase: str
) -> list[dict]:
    """Resolve the active roster, REJECTING an explicit list that is not one.

    Passing an arbitrary worker subset used to yield a plausible number with no
    warning — RR handed in a pre-swap subset and got 8.2031, which is meaningless
    for a post-swap oracle and indistinguishable from a real one. A caller doing
    cell-U reporting must get a FAILURE, not a number (RR F3; the S2-F2
    fail-closed discipline applied at this boundary).
    """
    if workers is None:
        return roster_workers(instance, phase)
    given = {w["worker_id"] for w in workers}
    for candidate in ("post_swap", "pre_swap"):
        if given == set(instance["event"][f"roster_{candidate}"]):
            return workers
    raise ValueError(
        f"explicit workers {sorted(given)} match neither declared roster "
        f"(pre={sorted(instance['event']['roster_pre_swap'])}, "
        f"post={sorted(instance['event']['roster_post_swap'])}); pass `phase=` "
        "instead of an ad-hoc subset — an arbitrary subset scores a team that "
        "never existed"
    )


def roster_workers(instance: dict[str, Any], phase: str = "post_swap") -> list[dict]:
    """The ACTIVE roster's workers — never the pool.

    The pool (`instance["workers"]`) contains BOTH the predecessor and the
    successor, and that roster never exists: they are never simultaneously
    routable. Scoring the pool scores a team that cannot be assembled, and it
    silently inflates the oracle, because a segment only the predecessor covers
    looks attainable post-swap. Default is post-swap, the primary; pass
    "pre_swap" for cell-U reporting (HARNESS_SPEC_v2 §4.1 ROSTER-CORRECT).
    """
    ids = set(instance["event"][f"roster_{phase}"])
    return [w for w in instance["workers"] if w["worker_id"] in ids]


def score(instance: dict[str, Any], allocation: dict[str, str]) -> float:
    """Σ_seg s(seg, assignee(seg)) — the allocation's score under faithful execution."""
    cal = instance["class_calibration"]
    workers = {w["worker_id"]: w for w in instance["workers"]}
    return sum(
        s(segment, workers[allocation[segment["segment_id"]]], cal)
        for segment in instance["segments"]
    )


def validate_reports(
    instance: dict[str, Any],
    allocation: dict[str, str],
    reports: dict[str, float | None],
) -> list[str]:
    """Check `reports` against `allocation`; return the ALLOCATED-but-unreported ids.

    Raises on an EXTRANEOUS key — a report for a segment this allocation never
    assigned means the reports dict belongs to a different run or a different
    allocation, and every number computed from it would be meaningless while
    looking perfectly well-formed.

    A MISSING key is not raised on, because "the worker produced nothing" is a real
    outcome that must stay scoreable. But it is never silent: it scores 0 *and* the
    segment is returned here, surfaced in `decompose_regret`'s output, and recorded
    as a run event. Without that, a missing key and a legitimately zero-scoring
    report are indistinguishable in the output (RR finding F4, P10 class).
    """
    allocated = {segment["segment_id"] for segment in instance["segments"]}
    if not allocated <= set(allocation):
        raise ValueError(
            f"allocation does not cover every segment; missing "
            f"{sorted(allocated - set(allocation))}"
        )
    extraneous = sorted(set(reports) - allocated)
    if extraneous:
        raise ValueError(
            f"reports contain keys not in this instance's allocation: {extraneous} "
            "— the reports dict does not belong to this run"
        )
    missing = sorted(seg_id for seg_id in allocated if seg_id not in reports)
    if missing:
        record_run_event(
            "scorer_missing_reports",
            {"missing_segments": missing, "n_allocated": len(allocated)},
            actor_type="scorer",
        )
    return missing


def achieved(
    instance: dict[str, Any],
    allocation: dict[str, str],
    reports: dict[str, float | None],
) -> float:
    """Σ_seg score(seg, what the assignee ACTUALLY reported).

    Validates first: an extraneous key raises, a missing one scores 0 and is
    surfaced by `validate_reports`.
    """
    cal = instance["class_calibration"]
    validate_reports(instance, allocation, reports)
    return sum(
        score_report(segment, reports.get(segment["segment_id"]), cal)
        for segment in instance["segments"]
    )


def oracle(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap",
) -> float:
    """Σ_seg max_w s(seg, w) — the best attainable score.

    Ranges over the ACTIVE ROSTER (post-swap by default), never the pool — the
    pool includes both the predecessor and the successor and can never exist.

    PRECONDITION: capacity is non-binding, i.e. no worker is prevented from taking
    every segment it is best at. S5 asserts this per instance. If capacity ever
    binds, this per-segment maximum is an upper bound rather than the oracle and the
    true oracle becomes an optimal assignment — still exact and still zero model
    calls, but no longer a one-line maximum. Stated here rather than assumed
    silently (HARNESS_SPEC_v2 §4.3).
    """
    cal = instance["class_calibration"]
    active = _resolve_roster(instance, workers, phase)
    return sum(
        max(s(segment, worker, cal) for worker in active)
        for segment in instance["segments"]
    )


def worst(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap",
) -> float:
    """Σ_seg min_w s(seg, w) — the floor the sensitivity gate measures against."""
    cal = instance["class_calibration"]
    active = _resolve_roster(instance, workers, phase)
    return sum(
        min(s(segment, worker, cal) for worker in active)
        for segment in instance["segments"]
    )


def oracle_allocation(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap",
) -> dict[str, str]:
    """An allocation attaining the oracle. Ties broken by worker id, so it is stable."""
    cal = instance["class_calibration"]
    active = _resolve_roster(instance, workers, phase)
    return {
        segment["segment_id"]: max(
            sorted(active, key=lambda w: w["worker_id"]),
            key=lambda w: s(segment, w, cal),
        )["worker_id"]
        for segment in instance["segments"]
    }


def decompose_regret(
    instance: dict[str, Any],
    allocation: dict[str, str],
    reports: dict[str, float | None],
) -> dict[str, float]:
    """Total regret split into allocation loss and execution loss.

    The two sum to total regret identically — `score(I, allocation)` appears with
    opposite signs in the two terms and cancels. The acceptance test asserts the
    identity numerically anyway, because an algebraic guarantee that nobody checks
    is how a refactor introduces an approximation.
    """
    missing = validate_reports(instance, allocation, reports)
    oracle_score = oracle(instance)
    faithful = score(instance, allocation)
    achieved_score = achieved(instance, allocation, reports)
    return {
        "oracle": oracle_score,
        "faithful_score": faithful,
        "achieved_score": achieved_score,
        "allocation_loss": oracle_score - faithful,
        "execution_loss": faithful - achieved_score,
        "total_regret": oracle_score - achieved_score,
        # Never omitted, even when empty: a reader must be able to tell "every
        # allocated segment was reported" from "this field was not populated".
        "missing_segments": missing,
    }


def faithful_reports(
    instance: dict[str, Any], allocation: dict[str, str]
) -> dict[str, float]:
    """The reports a fully faithful team would produce under this allocation."""
    workers = {w["worker_id"]: w for w in instance["workers"]}
    return {
        segment["segment_id"]: attainable_report(
            segment, workers[allocation[segment["segment_id"]]]
        )
        for segment in instance["segments"]
    }


def all_allocations(instance: dict[str, Any]) -> Iterable[dict[str, str]]:
    """Every assignment of segments to workers. Enumerable at study sizes."""
    segment_ids = [seg["segment_id"] for seg in instance["segments"]]
    # The ACTIVE roster, not the pool: enumerating pool allocations would include
    # teams containing both the predecessor and the successor, which never exist,
    # and the enumeration's maximum would then exceed the roster-correct oracle.
    worker_ids = [w["worker_id"] for w in roster_workers(instance)]

    def walk(index: int, partial: dict[str, str]):
        if index == len(segment_ids):
            yield dict(partial)
            return
        for worker_id in worker_ids:
            partial[segment_ids[index]] = worker_id
            yield from walk(index + 1, partial)

    yield from walk(0, {})


# ---------------------------------------------------------------------------
# CAPACITY-CONSTRAINED SCORING (S7 ruling). Capacity BINDS: the per-worker cap is
# what gives the task allocation difficulty at all. With capacity non-binding,
# greedy per-segment matching is optimal by definition and a card-matching script
# attains the oracle exactly (measured: shortfall 0.0000 on 20/20 instances).
#
# The oracle is now an exact capacity-constrained ASSIGNMENT, computed by DP over
# (segment index x remaining-capacity vector). At 3 workers and cap 4 that is
# <= 5^3 = 125 states x 9 segments — deterministic, stdlib only, zero model calls.
# Sigma-max is retained as an asserted UPPER BOUND, not as the oracle.
# ---------------------------------------------------------------------------

# THE YARDSTICK FOLLOWS THE WORLD (L14-b, researcher ruling 2026-08-10).
#
# This was 3, and the runtime enforced 3 to match. The researcher removed the
# per-worker segment allowance (L14), so THE RUNTIME NOW ENFORCES NOTHING -- a
# manager may send all nine segments to one worker and the environment will let it.
# Scoring against cap 3 while the world enforces no cap prices re-routing around a
# constraint nobody ever meets, and lets a realised allocation beat its own oracle.
#
# `None` means UNCAPPED, resolved per instance to its segment count -- which is the
# largest load any single worker could physically take, so the constraint is
# present in form and never binds. Derived rather than hardcoded to 9 because not
# every instance has nine segments (records/S4 holds an eight-segment one).
#
# THE PARAMETER IS DELIBERATELY KEPT. Passing `cap=3` still constrains, and the K6
# sweeps depend on exactly that. What is retired is the ASSUMPTION that the shipped
# cell is scored under a cap.
#
# WHAT THIS COST, recorded because it is not free: the cap was the only thing
# making the greedy label-matching script sub-optimal. Uncapped it attains the
# oracle EXACTLY on both shipped seeds, so the task's difficulty is now entirely
# INFORMATIONAL -- obtain the successor's labels -- with no constrained-allocation
# step behind it. See ALLOCATION_DIFFICULTY_RETIRED in finance_generator.
UNCAPPED = None
DEFAULT_CAP = UNCAPPED


def resolve_cap(instance: dict[str, Any], cap: int | None) -> int:
    """`None` -> the instance's own segment count, i.e. a cap that cannot bind.

    Every public scorer entry point resolves here, so there is ONE definition of
    what uncapped means rather than a `or 9` at each call site.
    """
    return len(instance["segments"]) if cap is None else cap


def _assignment_extreme(
    instance: dict[str, Any], workers: list[dict], cap: int, maximise: bool
) -> float:
    """Exact capacity-constrained best/worst total score.

    A segment may be left UNASSIGNED only when no worker has remaining capacity,
    and an unassigned segment scores 0 (an unstaffed unit produces no output). The
    "only when nothing remains" rule matters for the minimisation: without it the
    worst assignment would leave everything unassigned and score 0 trivially,
    which measures nothing.
    """
    cal = instance["class_calibration"]
    segments = instance["segments"]
    n_workers = len(workers)
    scores = [[s(segment, worker, cal) for worker in workers]
              for segment in segments]

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def best(index: int, remaining: tuple[int, ...]) -> float:
        if index == len(segments):
            return 0.0
        options = []
        for w in range(n_workers):
            if remaining[w] > 0:
                nxt = list(remaining)
                nxt[w] -= 1
                options.append(scores[index][w] + best(index + 1, tuple(nxt)))
        if maximise:
            # Skipping is allowed FREELY here. It never helps when capacity exists,
            # because every score is >= 0, so the maximiser skips exactly when
            # forced — and crucially it is then free to drop the LEAST VALUABLE
            # segment rather than whichever happens to come last in order.
            #
            # An earlier version allowed skipping only once capacity was exhausted,
            # which forced the drop onto the final segments and UNDERSTATED the
            # oracle-without-successor (6.2269 against the lead's 6.3880 on the
            # committed instance). The bound was still an oracle of something — just
            # not of the assignment problem being posed.
            options.append(best(index + 1, remaining))
            return max(options)
        if not options:  # nothing left anywhere: this segment goes unstaffed
            return best(index + 1, remaining)
        # The MINIMISER may not skip while capacity remains: free skipping would
        # leave everything unstaffed and score 0 trivially, which measures nothing.
        return min(options)

    cap = resolve_cap(instance, cap)  # None -> cannot bind (L14-b)
    return best(0, tuple([cap] * n_workers))


def oracle_allocation_capacitated(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap", cap: int = DEFAULT_CAP,
) -> dict[str, str | None]:
    """The CAPACITATED oracle's per-segment assignment (None where it drops one).

    `oracle_allocation` is the per-segment argmax and ignores capacity, so it
    cannot attribute the oracle's TOTAL to segments once the cap binds. The
    three-way regret split needs per-segment oracle contributions, so this
    reconstructs the DP's choices rather than re-deriving them by a rule that
    might disagree with the DP's own total.
    """
    from functools import lru_cache

    cal = instance["class_calibration"]
    active = _resolve_roster(instance, workers, phase)
    segments = instance["segments"]
    n_workers = len(active)
    scores = [[s(segment, worker, cal) for worker in active]
              for segment in segments]

    @lru_cache(maxsize=None)
    def best(index: int, remaining: tuple[int, ...]) -> float:
        if index == len(segments):
            return 0.0
        options = [best(index + 1, remaining)]
        for w in range(n_workers):
            if remaining[w] > 0:
                nxt = list(remaining)
                nxt[w] -= 1
                options.append(scores[index][w] + best(index + 1, tuple(nxt)))
        return max(options)

    allocation: dict[str, str | None] = {}
    cap = resolve_cap(instance, cap)  # None -> cannot bind (L14-b)
    remaining = tuple([cap] * n_workers)
    for index, segment in enumerate(segments):
        target = best(index, remaining)
        chosen = None
        # Ties broken by worker order so the reconstruction is deterministic.
        for w in range(n_workers):
            if remaining[w] <= 0:
                continue
            nxt = list(remaining)
            nxt[w] -= 1
            if abs(scores[index][w] + best(index + 1, tuple(nxt)) - target) < 1e-12:
                chosen = w
                break
        if chosen is None:
            allocation[segment["segment_id"]] = None      # the oracle drops it
        else:
            allocation[segment["segment_id"]] = active[chosen]["worker_id"]
            nxt = list(remaining)
            nxt[chosen] -= 1
            remaining = tuple(nxt)
    return allocation


def oracle_capacitated(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap", cap: int = DEFAULT_CAP,
) -> float:
    active = _resolve_roster(instance, workers, phase)
    return _assignment_extreme(instance, active, cap, maximise=True)


def worst_capacitated(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap", cap: int = DEFAULT_CAP,
) -> float:
    active = _resolve_roster(instance, workers, phase)
    return _assignment_extreme(instance, active, cap, maximise=False)


def oracle_without_successor(
    instance: dict[str, Any], cap: int = DEFAULT_CAP
) -> float:
    """The oracle the post-swap roster attains WITHOUT the successor.

    Capacity makes the successor load-bearing STRUCTURALLY rather than by
    tie-breaking: with 2 workers at cap 4 and 9 segments, 8 < 9, so at least one
    segment goes unstaffed and scores 0 no matter how the rest are routed.
    """
    remaining = [
        w for w in roster_workers(instance)
        if w["worker_id"] != instance["event"]["successor_id"]
    ]
    return _assignment_extreme(instance, remaining, cap, maximise=True)


def scripted_label_baseline(instance: dict[str, Any]) -> dict[str, str]:
    """The deterministic label-matching allocation (spec in finance_admission).

    Lives here so the GENERATOR's capacity assertion and the ADMISSION pipeline
    share one definition: assertion 2(b) requires the cap to bind against this
    exact greedy load, and a second copy could drift from the baseline the gate
    actually runs.
    """
    workers = sorted(
        roster_workers(instance),
        key=lambda w: "|".join(w.get("card_capabilities", ())),
    )
    allocation: dict[str, str] = {}
    for segment in instance["segments"]:
        asset_class = segment["asset_class"]
        match = next(
            (
                w for w in workers
                if any(line.strip().endswith(asset_class)
                       for line in w.get("card_capabilities", ()))
            ),
            workers[0],
        )
        allocation[segment["segment_id"]] = match["worker_id"]
    return allocation




def greedy_card_match_load(instance: dict[str, Any]) -> int:
    """Largest number of segments the greedy card-match sends to one worker.

    Assertion 2(b) requires the per-worker cap to be strictly BELOW this, which is
    what makes the greedy match infeasible and gives the task allocation
    difficulty. Measured, never assumed.
    """
    from collections import Counter

    return max(Counter(scripted_label_baseline(instance).values()).values())


def scripted_label_baseline_capped(
    instance: dict[str, Any], cap: int = DEFAULT_CAP
) -> dict[str, str]:
    """Greedy card-matching UNDER the per-worker cap (S7 ruling item 5).

    When the preferred worker is full the script must overflow somewhere, and the
    OPTIMAL overflow needs each segment's fallback penalty — which lives in the
    private calibrations. Overflow here goes to the first worker with capacity, in
    card order.

    ★ THE CLAIM THAT USED TO END THIS DOCSTRING IS RETIRED (L14-b). It read: "So no
    script over public information attains the oracle: the non-triviality is
    INFORMATION-THEORETIC, not a matter of obfuscating labels." THAT IS NOW FALSE AT
    THE DEFAULT CAP. Measured, uncapped, on both shipped seeds:

        seed 56   script 8.5430   oracle 8.5430   gap 0.0000
        seed 37   8.9168          8.9168          gap 0.0000

    The overflow argument held only while the cap FORCED an overflow. With no cap
    the preferred worker is never full, nothing overflows, and greedy card-matching
    IS optimal.

    WHAT SURVIVES, and it is the part the study rests on: the labels this script
    reads are the SUCCESSOR'S TRUE ONES. Under the stale-card manipulation the
    manager does not have them, so this is an UPPER-INFORMATION baseline that no
    manager in cell 0 can execute. The task's difficulty is now entirely
    informational — obtain the labels — with no allocation step behind it.
    """
    cap = resolve_cap(instance, cap)  # None -> cannot bind (L14-b)
    workers = sorted(
        roster_workers(instance),
        key=lambda w: "|".join(w.get("card_capabilities", ())),
    )
    used = {w["worker_id"]: 0 for w in workers}
    allocation: dict[str, str] = {}
    for segment in instance["segments"]:
        asset_class = segment["asset_class"]
        preferred = [
            w for w in workers
            if any(line.strip().endswith(asset_class)
                   for line in w.get("card_capabilities", ()))
        ]
        chosen = next(
            (w for w in preferred + workers if used[w["worker_id"]] < cap), None
        )
        if chosen is None:
            continue  # every worker full: this segment goes unstaffed, scoring 0
        used[chosen["worker_id"]] += 1
        allocation[segment["segment_id"]] = chosen["worker_id"]
    return allocation


# ---------------------------------------------------------------------------
# CHANNEL EFFECT CEILING (v3). The quantity the MDE is applied to.
#
# HISTORY, kept because each retirement has a reason worth not repeating:
#   v1  sum over strictly-required segments of (successor's score - best other).
#       Tie-sensitive, and it counted segments the tie-break happened to award.
#   v2  M = oracle - oracle_without_successor. Assignment-correct and tie-robust,
#       but ~80% of it is CAPACITY, not information: removing the successor removes
#       3 units of capacity and forces segments unstaffed. Worse, its counterfactual
#       is realised by NO CELL in the grid — every cell has the successor, and the
#       channels move WHICH segments it gets, never WHETHER it exists.
#   v3  oracle - E[ignorant capacity-respecting assignment]. The counterfactual is
#       a manager that HAS the successor and the same capacity but no coverage
#       information — which is what the no-channel cell actually is. The gap is
#       therefore attributable to information, which is what the study measures.
# ---------------------------------------------------------------------------

# Monte-Carlo draw count for the ignorant baseline. 10,000, raised from 300.
#
# WHY IT WAS RAISED (RR S7 round-3): at 300 draws the estimator's OWN noise moves
# the published ceiling by up to ~0.02 between MC streams. That is tolerable for a
# diagnostic and NOT tolerable for a THRESHOLDED quantity — an instance sitting
# near the eventual MDE could be admitted or flagged by the draw seed alone, which
# is the S5 tie-break-luck failure relocated from the generator into the estimator.
# At 10,000 it stabilises to ~5e-4, and the cost is milliseconds per instance, so
# there is no tradeoff to weigh.
#
# The achieved standard error is PUBLISHED PER ROW rather than assumed from this
# constant: a draw count is a promise about precision, the SE is the measurement.
IGNORANT_DRAWS = 10_000


def ignorant_stats(
    instance: dict[str, Any], cap: int = DEFAULT_CAP, draws: int = IGNORANT_DRAWS,
    stream: int = 0,
) -> dict[str, float]:
    """Per-draw scores of a coverage-BLIND, capacity-RESPECTING assignment.

    Returns the mean, the per-draw sd, and the ACHIEVED standard error of the mean
    (sd/sqrt(draws)) — the estimator's own noise, measured rather than promised.

    Monte-Carlo because the exact expectation over capacity-feasible assignments is
    a permanent-style sum; the stream is seeded from the instance so the estimate is
    reproducible, and the draw count enters the seed so a count change is a visible
    stream change rather than a silent refinement of the same one.
    """
    cal = instance["class_calibration"]
    import random as _random
    import statistics as _stats

    segments = instance["segments"]
    workers = roster_workers(instance)
    # `stream` selects an INDEPENDENT Monte-Carlo stream at the same draw count.
    # Production default 0; the acceptance drives stream 0..k-1 to check that the
    # ACHIEVED SE actually predicts the cross-stream spread, rather than trusting
    # sd/sqrt(n) on an estimator whose draws are not obviously independent.
    # RESOLVED BEFORE THE SEED IS BUILT, and the order matters. The stream identity
    # embeds `cap`; resolving after this line would put the literal "None" in the
    # seed, so every uncapped instance would share a stream keyed on a non-value and
    # the cap would stop being part of the stream's identity at all.
    cap = resolve_cap(instance, cap)  # None -> cannot bind (L14-b)
    rng = _random.Random(f"ignorant::{instance['seed']}::{cap}::{draws}::{stream}")
    scores = [[s(segment, worker, cal) for worker in workers]
              for segment in segments]

    runs = []
    for _ in range(draws):
        remaining = [cap] * len(workers)
        order = list(range(len(segments)))
        rng.shuffle(order)
        run = 0.0
        for index in order:
            choices = [w for w in range(len(workers)) if remaining[w] > 0]
            if not choices:
                continue  # unstaffed, scores 0
            pick = rng.choice(choices)
            remaining[pick] -= 1
            run += scores[index][pick]
        runs.append(run)

    mean = _stats.fmean(runs)
    sd = _stats.stdev(runs) if len(runs) > 1 else 0.0
    return {"mean": mean, "sd": sd, "se": sd / (len(runs) ** 0.5), "draws": draws}


def expected_ignorant_score(
    instance: dict[str, Any], cap: int = DEFAULT_CAP, draws: int = IGNORANT_DRAWS,
    stream: int = 0,
) -> float:
    """E[score] of a coverage-BLIND but capacity-RESPECTING assignment."""
    return ignorant_stats(instance, cap=cap, draws=draws, stream=stream)["mean"]


# ---------------------------------------------------------------------------
# CEILINGS. A ceiling is oracle MINUS A BASELINE, and it is meaningless without
# naming the baseline — so every ceiling function here says which one it uses.
#
# THIS PROJECT SHIPPED A DEFECT BECAUSE THAT WAS NOT TRUE. `ceiling_vs_ignorant`
# used the IGNORANT baseline and was used as the admission and instance-selection
# criterion, but the study's manager is never ignorant — it always holds the
# predecessor's card. Measured over 12 seeds the two baselines differ by 10.9x, and
# they disagree about which instances are alive: 6 of 12 have a stale-card ceiling
# of EXACTLY ZERO while their ignorant ceiling is healthy. Selection ranked on the
# ignorant one and picked two dead instances out of three. See
# records/L4/DIRECTIONS_LS.md.
#
#   ceiling_vs_ignorant    oracle - E[random coverage-blind assignment]
#                          "what is coverage information worth against ignorance?"
#                          NOT the study's counterfactual. Do not gate on it.
#   ceiling_vs_stale_card  oracle - optimal play believing the predecessor's card
#                          "what is CORRECT information worth against the card the
#                          manager actually holds?" THIS is the study's question.
# ---------------------------------------------------------------------------


def ceiling_vs_ignorant(
    instance: dict[str, Any], cap: int = DEFAULT_CAP, draws: int = IGNORANT_DRAWS,
    stream: int = 0,
) -> float:
    """oracle - E[ignorant assignment]. NOT an admission criterion — see above."""
    return ceiling_vs_ignorant_stats(
        instance, cap=cap, draws=draws, stream=stream)["ceiling"]


def ceiling_vs_stale_card(
    instance: dict[str, Any], cap: int = DEFAULT_CAP,
) -> dict[str, Any]:
    """oracle - optimal play under the PREDECESSOR'S CARD, scored under truth.

    The study's counterfactual: the manager holds a card describing the worker
    that left, so the question is what CORRECTING that belief is worth — not what
    coverage information is worth against knowing nothing.

    Exact: capacitated optimum by enumeration under each belief, then the
    card-believing allocation is re-scored in the TRUE world.

    THIS FUNCTION HAS NOW BEEN WRONG TWICE ABOUT WHICH QUESTION IT ASKS, so it
    states both answers rather than one. First the BASELINE: it ranked selection
    against a random-blind manager when the study's counterfactual is the stale
    card (fixed by splitting `ceiling_vs_ignorant` out). Then the BELIEF, fixed
    here.

    THE CARD IS A REPLACEMENT DESCRIPTION, NOT AN ADDITION TO A TRUE ONE. It has
    TWO errors, and the earlier version modelled one:

      * the LIE      — it claims coverage the successor lacks;
      * the OMISSION — it is silent about coverage the successor has.

    The earlier `believed_score` granted 1.0 where the card claimed coverage and
    otherwise FELL THROUGH TO THE TRUE SCORE, so wherever the card was silent
    about a class the successor really covered, the manager was credited with
    knowing it anyway. Under the current template that costs nothing — the silent
    class is always incumbent-covered (0/30 seeds have a costly omission, and the
    two models agree 30/30) — which is exactly why it survived: it was invisible
    on the only population it was ever validated against.

    It stops being invisible the moment the successor SOLE-HOLDS a silent class,
    which is what the L9 candidate lattices are built to create. Measured on the
    disjoint candidate: lie-only prices 0.37% of oracle where the whole card
    prices 8.51%, so the old model missed 96% of the effect — and 4320 of the
    6480 admissible size-3 templates carry that property. Choosing a lattice with
    the lie-only model would have scored every one of them as though it lacked
    the very thing it was chosen for.

    Belief is about ATTAINMENT, not about a worker's private calibration, which
    the manager cannot see either way. `check_card_belief_model.py` is the
    acceptance, and it asserts BOTH halves: agreement where the omission is
    harmless, divergence where it is not.
    """
    event = instance["event"]
    successor = event["successor_id"]
    calibration = instance["class_calibration"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    workers = [by_id[w] for w in event["roster_post_swap"]]
    segments = instance["segments"]
    card_claims = tuple(by_id[event["predecessor_id"]]["irb_coverage"])

    # The successor AS THE CARD DESCRIBES IT: coverage replaced by the card's
    # claims, entire. Building a worker rather than special-casing the score is
    # what makes the omission cost something — there is no branch left that can
    # fall through to the truth.
    successor_as_carded = dict(by_id[successor])
    successor_as_carded["irb_coverage"] = card_claims
    # No `if c in calibration` guard: the calibration is class-level and covers
    # every asset class, so such a guard could never fire — and a silent guard
    # over a total mapping is the defaults pattern that hid the previous fault.
    # A card naming a class the instance does not have is a real error; let it
    # raise here rather than quietly pricing that class at nothing.
    successor_as_carded["private_pd_calibration"] = {
        c: calibration[c] for c in card_claims}

    # THE ISOLATION OF THIS MODEL DEPENDS ON CALIBRATION BEING CLASS-LEVEL, so it
    # is asserted rather than remembered (RR).
    #
    # RR verified segment-by-segment that this model and the superseded lie-only
    # one differ ONLY where the card is SILENT — 162 of 810 cells — and NEVER
    # where it CLAIMS: 0 of 810. That holds because the superseded model returned
    # a hardcoded 1.0 on a claimed IRB class while this one returns
    # `s(segment, successor_as_carded, ...)`, and the two coincide only if the
    # score really is 1.0 there. It is, because calibration is class-level (R1):
    # the carded successor holds the TRUE table entry, so `irb_rwa ==
    # correct_rwa` exactly.
    #
    # Reintroduce per-worker calibration noise and the two models begin diverging
    # on CLAIMED classes as well — silently, and in the direction that makes the
    # belief-model effect look LARGER than it is, since attainment granted on the
    # lie would be counted as belief. That is the failure this guards.
    for asset_class, table in by_id[successor]["private_pd_calibration"].items():
        if table != calibration[asset_class]:
            raise ValueError(
                f"worker calibration for {asset_class!r} differs from the class "
                f"calibration. This model's separation of the card's LIE from its "
                f"OMISSION is exact only while calibration is CLASS-LEVEL (R1); "
                f"with per-worker tables the lie also grants attainment and the "
                f"two effects are no longer distinguishable"
            )

    def true_score(segment, worker):
        return s(segment, worker, calibration)

    def believed_score(segment, worker):
        if worker["worker_id"] != successor:
            return s(segment, worker, calibration)
        return s(segment, successor_as_carded, calibration)

    # Score matrices, so the enumeration sums cached floats. Also makes the tie
    # comparison exact: the same float is compared against itself rather than
    # recomputed down a possibly different path.
    true_m = [[true_score(sg, w) for w in workers] for sg in segments]
    believed_m = [[believed_score(sg, w) for w in workers] for sg in segments]

    # Resolved OUTSIDE the closure: assigning to `cap` inside `feasible` made it a
    # local and shadowed the enclosing binding (UnboundLocalError). Also correct to
    # hoist it -- it is loop-invariant and was being recomputed per combination.
    resolved_cap = resolve_cap(instance, cap)  # None -> cannot bind (L14-b)

    def feasible():
        for combo in product(range(len(workers)), repeat=len(segments)):
            if all(combo.count(i) <= resolved_cap for i in range(len(workers))):
                yield combo

    def best(matrix):
        best_value, best_alloc = -1.0, ()
        for combo in feasible():
            value = sum(matrix[j][w] for j, w in enumerate(combo))
            if value > best_value:
                best_value, best_alloc = value, combo
        return best_value, best_alloc

    true_value, true_alloc = best(true_m)
    believed_value, believed_alloc = best(believed_m)

    # TIE-BREAK: EXPECTATION OVER THE BELIEVED-OPTIMAL SET (D19).
    #
    # The believed optimum is routinely NOT UNIQUE, and its members are equal only
    # UNDER THE CARD — re-scored under TRUTH they differ. So which one is returned
    # decides the ceiling, and `best()` returns whichever `product()` visited
    # first, i.e. Python list order. Measured on a six-class clone lattice: up to
    # FOUR different ceilings for one instance across eight segment orderings,
    # spanning 14.10% — larger than the effect being measured (check_tie_rate.py).
    #
    # Expectation, because under the card those allocations are INDISTINGUISHABLE
    # TO THE MANAGER: it holds no information that separates them, so any
    # deterministic rule (first-visited, best, worst) credits it with a
    # discrimination it cannot make.
    #
    # EXPECTATION IS NOT AN UPPER BOUND. A manager that tie-breaks worse than
    # chance realises less, and the true ceiling is then ABOVE this figure. That
    # is why `ceiling_min`/`ceiling_max` are returned beside it and are not
    # decoration: reporting the point alone restates a range as a point.
    #
    # At five classes the spread is EXACTLY ZERO on 20/20 seeds, so this changes
    # no previously reported number.
    realised_over_ties = [
        sum(true_m[j][w] for j, w in enumerate(combo))
        for combo in feasible()
        if abs(sum(believed_m[j][w] for j, w in enumerate(combo))
               - believed_value) <= TIE_EPS
    ]
    realised = sum(realised_over_ties) / len(realised_over_ties)

    # A CEILING IS NON-NEGATIVE BY CONSTRUCTION — the true optimum cannot be beaten
    # by play under a false belief — so a negative one is either float noise or a
    # broken enumeration, and the two must not be confused. Noise at the scale of
    # accumulated float error is snapped to zero; anything larger RAISES, because
    # at that size it means the believed allocation outscored the optimum, which
    # is a defect in `best()` and not a small number.
    #
    # Observed: -2e-17 on 4 of 30 seeds for a genuinely zero-ceiling template (RR).
    # Printing that as a negative share also violates the plausible-range rule.
    ceiling = true_value - realised
    if ceiling < 0.0:
        if ceiling < -1e-9:
            raise ValueError(
                f"negative ceiling {ceiling!r}: play under the card outscored the "
                f"true optimum, which is impossible unless the capacitated "
                f"enumeration is wrong"
            )
        ceiling = 0.0

    # min/max over the tie set. NOT decoration: expectation is not an upper bound,
    # so a point estimate without these restates a range as a point.
    ceiling_hi = max(0.0, true_value - min(realised_over_ties))
    ceiling_lo = max(0.0, true_value - max(realised_over_ties))

    return {
        "ceiling": ceiling,
        "ceiling_share": ceiling / true_value if true_value else None,
        "ceiling_min": ceiling_lo,
        "ceiling_max": ceiling_hi,
        "ceiling_share_min": ceiling_lo / true_value if true_value else None,
        "ceiling_share_max": ceiling_hi / true_value if true_value else None,
        "n_believed_optima": len(realised_over_ties),
        "oracle": true_value,
        "card_believing_play_realises": realised,
        "allocation_differs": true_alloc != believed_alloc,
        # THE THREE THINGS THAT SILENTLY DECIDED THIS NUMBER, each added only
        # after it was caught doing so. Declared on every result so a reader never
        # has to know which version produced a figure.
        "baseline": ("stale card — oracle minus optimal play under the "
                     "predecessor's card. NOT the ignorant baseline"),
        "belief_model": ("the card as a REPLACEMENT description of the successor: "
                         "its OMISSION costs as well as its LIE (D1)"),
        "tie_break": ("EXPECTATION over the believed-optimal set, which is not an "
                      "upper bound — read ceiling_min/ceiling_max with it (D19)"),
    }


def ceiling_vs_ignorant_stats(
    instance: dict[str, Any], cap: int = DEFAULT_CAP, draws: int = IGNORANT_DRAWS,
    stream: int = 0,
) -> dict[str, float]:
    """oracle - E[ignorant assignment], WITH its Monte-Carlo standard error.

    The oracle term is exact (a DP), so all of the estimator noise sits in the
    ignorant term and the ceiling's SE is that term's SE unchanged.
    """
    oracle_value = oracle_capacitated(instance, cap=cap)
    stats = ignorant_stats(instance, cap=cap, draws=draws, stream=stream)
    ceiling = oracle_value - stats["mean"]
    return {
        "ceiling": ceiling,
        "ceiling_se": stats["se"],
        "ceiling_share": ceiling / oracle_value if oracle_value else None,
        "ceiling_share_se": stats["se"] / oracle_value if oracle_value else None,
        "oracle": oracle_value,
        "expected_ignorant": stats["mean"],
        "per_draw_sd": stats["sd"],
        "draws": draws,
    }


def oracle_without_incumbent(
    instance: dict[str, Any], cap: int = DEFAULT_CAP
) -> float:
    """Best oracle attainable after dropping the BEST-CASE incumbent instead.

    The comparator that splits M: dropping any post-swap worker costs the same 3
    units of capacity, so M_successor - M_incumbent removes the capacity term and
    leaves the COVERAGE-attributable part.
    """
    post = roster_workers(instance)
    successor_id = instance["event"]["successor_id"]
    incumbents = [w for w in post if w["worker_id"] != successor_id]
    return max(
        _assignment_extreme(
            instance, [w for w in post if w["worker_id"] != drop["worker_id"]],
            cap, maximise=True)
        for drop in incumbents
    )


# ---------------------------------------------------------------------------
# S9 — REALISED-AUTHORITATIVE SCORING (spec §4.1)
# ---------------------------------------------------------------------------
UNSTAFFED = "__unstaffed__"


def realised_allocation(
    intended: dict[str, str],
    deferred_segments: Iterable[str],
) -> dict[str, str]:
    """The allocation that ACTUALLY held slots, from the intended one and the log.

    Under binding capacity the manager assigned all k and the ENGINE realised a
    subset it did not choose, by task-registry insertion order. Scoring is
    realised-authoritative: what held a slot is what gets scored, and a deferred
    segment scores 0 in the faithful term, which puts its loss in ALLOCATION loss
    where an infeasible intent belongs.

    The engine never selects a best feasible subset — that would be oracle
    knowledge in the harness. The retired set-level reading credited the manager
    with an optimisation neither the manager nor the engine performed, and
    execution loss would have absorbed the engine's ordering as fake worker
    underperformance.
    """
    deferred = set(deferred_segments)
    return {segment_id: (UNSTAFFED if segment_id in deferred else worker_id)
            for segment_id, worker_id in intended.items()}


def realised_faithful_score(
    instance: dict[str, Any],
    realised: dict[str, str],
) -> float:
    """Faithful-execution score under the REALISED allocation.

    A segment nobody holds contributes 0 — not "the best a worker could have
    done", which is the credit the retired reading gave away for free.
    """
    cal = instance["class_calibration"]
    workers = {w["worker_id"]: w for w in instance["workers"]}
    total = 0.0
    for segment in instance["segments"]:
        worker_id = realised.get(segment["segment_id"])
        worker = workers.get(worker_id) if worker_id else None
        if worker is None:
            continue
        total += s(segment, worker, cal)
    return total


def realised_report(
    instance: dict[str, Any],
    intended: dict[str, str],
    deferred_segments: Iterable[str],
    reports: dict[str, float | None],
    cap: int = DEFAULT_CAP,
) -> dict[str, Any]:
    """The full realised-authoritative picture: scored, with diagnostics beside it.

    The INTENDED allocation and the DEFERRED set travel with the score as
    diagnostics rather than being discarded — an infeasible intent is a
    management fact worth seeing, and only the intended allocation shows it.
    """
    # `n_over_cap_workers` below counts against the RESOLVED cap. At the default it
    # is now structurally 0 -- no allocation can exceed the segment count -- which
    # is the honest reading: the runtime enforces nothing, so nothing is "over".
    # It stays because passing an explicit `cap` still makes it meaningful, and
    # because a non-zero here on a shipped run would mean the cap came back.
    cap = resolve_cap(instance, cap)  # None -> cannot bind (L14-b)
    deferred = sorted(set(deferred_segments))
    realised = realised_allocation(intended, deferred)
    faithful = realised_faithful_score(instance, realised)
    oracle_value = oracle_capacitated(instance, cap=cap)
    achieved_value = achieved(instance, realised, reports)

    over_assigned: dict[str, int] = {}
    for worker_id in intended.values():
        if worker_id and worker_id != UNSTAFFED:
            over_assigned[worker_id] = over_assigned.get(worker_id, 0) + 1

    return {
        "realised_allocation": realised,
        "intended_allocation": dict(intended),
        "deferred_segments": deferred,
        "n_deferred": len(deferred),
        "faithful_under_realised": faithful,
        "achieved": achieved_value,
        "oracle_capacitated": oracle_value,
        "regret": oracle_value - achieved_value,
        # THE DECOMPOSITION. Allocation loss carries the deferrals, because a
        # deferred segment is the deterministic consequence of an infeasible
        # intent. Execution loss is the SIGNED deviation of what was reported from
        # what faithful execution of the REALISED assignment would have produced.
        "allocation_loss": oracle_value - faithful,
        "execution_loss_signed": faithful - achieved_value,
        "intended_load_per_worker": over_assigned,
        "n_over_cap_workers": sum(1 for n in over_assigned.values() if n > cap),
    }


def discriminating_segments(
    instance: dict[str, Any], workers: list[dict] | None = None,
    phase: str = "post_swap",
) -> dict[str, Any]:
    """On how many units does WHO YOU ROUTE TO change the score?

    THE GAP IN OUR OWN INSTRUMENT SUITE, found by asking why a zero was zero. We
    built K1, K3, K4, K6, an admission pipeline and a Monte-Carlo ignorant
    baseline, and never once measured the fraction of units where the routing
    choice matters at all. The ceiling captures it only in AGGREGATE — a large
    ceiling can come from a few high-stakes units or many small ones, and those
    are different designs.

    It is the quantity that decides whether "the manager never mis-routes" is a
    finding about managers or about the instance: on a unit where every active
    worker scores identically there is nothing for any channel to inform, and no
    allocation error is possible.

    A unit DISCRIMINATES when the best active worker beats the second-best by more
    than TIE_EPS — the same threshold the successor-routing count uses, so the two
    disclosures cannot disagree about what a tie is.
    """
    # Same tie threshold the successor-routing count uses, imported rather than
    # redefined so the two disclosures cannot disagree about what a tie is.
    from .finance_generator import TIE_EPS

    cal = instance["class_calibration"]
    active = _resolve_roster(instance, workers, phase)
    rows = []
    for segment in instance["segments"]:
        values = sorted((s(segment, worker, cal) for worker in active),
                        reverse=True)
        gap = values[0] - values[1] if len(values) > 1 else 0.0
        rows.append({
            "segment_id": segment["segment_id"],
            "best": values[0],
            "second_best": values[1] if len(values) > 1 else None,
            "gap": gap,
            "discriminates": gap > TIE_EPS,
        })
    discriminating = [r for r in rows if r["discriminates"]]
    gaps = [r["gap"] for r in discriminating]
    return {
        "phase": phase,
        "n_segments": len(rows),
        "n_discriminating": len(discriminating),
        "discriminating_fraction": len(discriminating) / len(rows) if rows else 0.0,
        "gap_median": (sorted(gaps)[len(gaps) // 2] if gaps else None),
        "gap_max": max(gaps) if gaps else None,
        "segments": rows,
        "note": ("on a NON-discriminating unit every active worker scores the "
                 "same, so no allocation error is possible and no channel can "
                 "inform the choice — those units cannot populate the "
                 "channel-sensitive term at all"),
    }
