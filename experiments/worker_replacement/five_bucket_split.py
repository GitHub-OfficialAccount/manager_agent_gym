"""The FIVE-BUCKET reading of `finance_split`'s eight states.

Built BEFORE the bundle it will be applied to exists, deliberately: the mapping is
what decides whether a non-completion is the thing we are measuring, the thing we
did to the workflow, or a property of the harness, and a mapping chosen after
seeing the counts is a choice about the answer.

The mapping was settled in the L2a ruling and until now lived ONLY IN PROSE -- in
the cron prompt and the backlog. Prose is not an instrument. Nothing may be
reported under these bucket names that did not come through this file.

WHAT THIS DOES NOT DO: it never sums across buckets, and it never reports a
"non-completion rate". The whole point of the ruling is that the eight states do
not share a denominator's meaning -- a segment the manager never staffed and a
segment the horizon cut off are both "incomplete" and answer different questions.
`total` appears nowhere in the output.

Run:
    python -m experiments.worker_replacement.five_bucket_split [bundle.json ...]

with no arguments it reports the committed corpus baseline.
"""

from __future__ import annotations

import glob
import json
import sys
from typing import Any

try:  # package import -- the form every other module here uses
    from .finance_split import STATE_PREDICATES, split
except ImportError:  # direct-script invocation, which the docstring documents
    from finance_split import STATE_PREDICATES, split

# Ruling of 2026-08-09, corrected from a two-way split. The correction that
# matters and the reason the mapping is worth a file: `refused_unavailable` was
# going to be pooled with the removable states. It is CAUSED BY THE ROSTER CHANGE
# -- which is our manipulation -- so discarding it as noise would have deleted the
# manipulation's own footprint from the measurement.
BUCKETS: dict[str, tuple[str, ...]] = {
    "DV": ("never_assigned", "refused_allotment", "executed_and_declined"),
    "MANIPULATION": ("refused_unavailable",),
    "BUDGET_HORIZON": ("refused_concurrency", "unexecuted_no_refusal"),
    "DEFECT": ("executed_but_unparseable",),
    "MEASUREMENT": ("executed_and_parsed",),
}

# A KNOWN POOLING, recorded rather than silently carried (RR). `executed_and_declined`
# is ONE state covering TWO causes that belong in different buckets:
#
#   declined a segment in a class the assignee does NOT cover  -> the manager
#       mis-assigned -> an allocation outcome -> DV, correctly.
#   declined a segment in a class the assignee DOES cover      -> the worker's own
#       judgement -> NOT an allocation outcome -> does not belong in DV.
#
# It stays in DV because the first case is the one the study is about and declines are
# expected to be rare, so the pooling probably costs nothing numerically. But it IS the
# same pooling defect the five-bucket ruling was written to remove, one level down,
# and it is named here so nobody rediscovers it as a surprise. The discriminator
# already exists -- was the assignee covered for that segment's class -- so this is
# splittable the moment a bundle shows an in-coverage decline.
KNOWN_POOLING = ("executed_and_declined",)

# ---------------------------------------------------------------------------
# MANIPULATION_UNREACHABLE (found by RR, verified at source by LS, 2026-08-09)
#
# `refused_unavailable` CANNOT FIRE. Traced end to end:
#
#   interface.py:82   self.is_available: bool = True     declared True
#   telemetry.py:58   is_available: bool = Field(True)   declared True
#   every other occurrence in the repo is a READ. There is no write, and none of
#   the three model_copy(update=...) sites touches it -- RR flagged a dynamic
#   setattr as an unclosed residual and it is now closed by inspection.
#   registry.py:405   the swap calls remove_agent(...)   REMOVES, never marks
#
# So the branch at interface.py:105 (`if not self.is_available`) is dead code, and
# a swap produces removal rather than unavailability.
#
# AND THE FOOTPRINT IS NOT MERELY IN A DIFFERENT BUCKET -- IT IS NOWHERE. An
# attempt to assign a segment to the departed worker after the swap:
#   * returns early at manager_actions.py:227 ("Agent ... not found"), success=False,
#     BEFORE record_assignment, so no `task_assigned` event exists;
#   * never reaches can_handle_task, so no deferral and no refusal code exists;
#   * never mutates `assigned_agent_id`, so `intended_allocation` -- which reads that
#     field -- is unchanged.
# The segment ends `never_assigned`, INDISTINGUISHABLE FROM A MANAGER THAT NEVER TRIED.
#
# WHAT THIS DOES AND DOES NOT COST. The brief's "allocating as if the predecessor
# remained" has two halves. Failing to REASSIGN inherited tasks still on the board is
# OBSERVABLE (`task_board_final`) and is untouched -- it is the study's novelty
# property 2 and it works. Actively assigning NEW work to a departed worker is
# currently INVISIBLE. We can measure one half.
#
# THE FIX IS A RECORDING CHANGE, NOT A DESIGN CHANGE. Marking the predecessor
# "unavailable" instead of removing it would make this bucket fill, and it FAILS the
# standing production-grade test: a real orchestrator deregisters a departed worker
# and rejects assignment to an unknown id. Keeping a ghost in the roster so it can be
# assigned to is the artificial choice. Recording the REJECTED ACTION is what a real
# orchestrator does anyway, and it puts the footprint where it actually is.
MANIPULATION_UNREACHABLE = True

BUCKET_MEANS: dict[str, str] = {
    "DV": "an allocation outcome. This is the thing the study measures. TWO "
          "CAVEATS TRAVEL WITH IT. (1) `executed_and_declined` pools a manager "
          "mis-assignment with a worker's own in-coverage judgement -- see "
          "KNOWN_POOLING. (2) `refused_allotment` IS STRUCTURALLY UNREACHABLE as "
          "the harness stands (L14) -- its zero is UNINFORMATIVE, see "
          "finance_split.ALLOTMENT_UNREACHABLE. It was the only DV state ever "
          "observed to fire, so this bucket now rests entirely on "
          "`never_assigned` and `executed_and_declined`.",
    "MANIPULATION": "STRUCTURALLY EMPTY AS THE HARNESS STANDS -- a count of 0 here "
                    "is UNINFORMATIVE, not a finding. See MANIPULATION_UNREACHABLE. "
                    "The bucket is kept because the state exists and the partition "
                    "must be total; it is not kept because it can fill.",
    "BUDGET_HORIZON": "the episode ran out of timesteps or slots. A property of "
                      "the run's budget, not of the manager's judgement.",
    "DEFECT": "the harness or the worker produced something unreadable. A bug "
              "to fix, never a finding.",
    "MEASUREMENT": "executed and yielded a value. The scorer's business from here.",
}

# `never removed` in the ruling's prose is NOT a ninth state and NOT a bundle-level
# condition. It is a HANDLING DIRECTIVE attached to the MANIPULATION bucket -- "this
# bucket must never be discarded as noise" -- and it is discharged in full by
# BUCKET_MEANS["MANIPULATION"] above.
#
# An earlier version of this file listed it as prose-only "asserted separately by the
# runner", reading it as a claim that the swap did not happen. RR, who wrote the
# annotation, corrected the referent: that reading would send a future reader looking
# for a runner assertion that was never intended to exist. A wrong reason for a right
# call is still a defect when it manufactures an obligation.


def _check_partition() -> None:
    """Every state lands in exactly one bucket, and no bucket names a state that
    does not exist. A mapping that silently drops a state would under-report the
    bucket it belonged in and no residual would catch it."""
    mapped = [s for states in BUCKETS.values() for s in states]
    if len(mapped) != len(set(mapped)):
        dupes = sorted({s for s in mapped if mapped.count(s) > 1})
        raise AssertionError(f"states in more than one bucket: {dupes}")
    missing = sorted(set(STATE_PREDICATES) - set(mapped))
    invented = sorted(set(mapped) - set(STATE_PREDICATES))
    if missing or invented:
        raise AssertionError(
            f"mapping does not partition the eight states. "
            f"unmapped: {missing}  invented: {invented}"
        )


def five_bucket(bundle: dict[str, Any]) -> dict[str, Any]:
    """Bucket counts, each carrying the states it is made of and any state whose
    predicate does not hold for this bundle."""
    _check_partition()
    result = split(bundle)
    counts = result["counts"]
    uninterpretable = set(result.get("uninterpretable_states") or ())

    out: dict[str, Any] = {}
    for bucket, states in BUCKETS.items():
        flagged = sorted(uninterpretable.intersection(states))
        out[bucket] = {
            "count": sum(counts.get(s, 0) for s in states),
            "by_state": {s: counts.get(s, 0) for s in states},
            "means": BUCKET_MEANS[bucket],
            # A bucket inherits its states' non-interpretability. Without this the
            # flag set on a state would be lost the moment it was aggregated.
            "uninterpretable_states": flagged,
            "reason": result.get("uninterpretable_reason") if flagged else None,
        }
    # A ZERO THAT CANNOT BE OTHERWISE IS NOT A MEASUREMENT. Carried on the data
    # structure, not in a printed banner, because every consumer reads `buckets`
    # and a banner is dropped by the first summariser that reformats the output.
    if MANIPULATION_UNREACHABLE:
        out["MANIPULATION"]["uninformative"] = True
        out["MANIPULATION"]["reason"] = (
            "refused_unavailable cannot fire: nothing in the repo sets "
            "is_available=False and the swap REMOVES the agent. A count of 0 is "
            "structural, not behavioural, and must not be reported as evidence "
            "that the manager never mis-assigned to the departed worker."
        )
    return {
        "buckets": out,
        "n_segments": result["n_segments"],
        "residual": result["residual"],
        "comparator": "the segment denominator for this episode",
        "establishes": "which QUESTION each incomplete segment belongs to",
        "does_not_establish":
            "any non-completion RATE. The buckets answer different questions and "
            "are never summed; a total over them would be a number with no "
            "population.",
    }


def coverage(paths: list[str]) -> tuple[list[str], dict[str, str]]:
    """Which bundles this split can actually be COMPUTED on.

    Reported rather than raised, because the answer turned out to be zero and that
    is a finding about the corpus, not a crash. `finance_split` refuses any bundle
    whose deferrals carry no `refusal_codes` -- correctly, since classifying those
    by substring over the prose is how an availability refusal came to be recorded
    as a concurrency one. Every bundle committed before the structured-code fix is
    therefore permanently unclassifiable, and no re-analysis recovers it.
    """
    ok, refused = [], {}
    for p in paths:
        try:
            five_bucket(json.load(open(p)))
            ok.append(p)
        except Exception as exc:  # noqa: BLE001 -- the reason is the result
            refused[p] = str(exc)
    return ok, refused


def main(paths: list[str]) -> None:
    _check_partition()
    if not paths:
        paths = sorted(
            f for f in glob.glob("experiments/worker_replacement/records/*/run_*.json")
            if "_FAILED" not in f and "_INCOMPLETE" not in f
        )
        print(f"_corpus baseline: {len(paths)} committed bundles_\n")
    if not paths:
        raise SystemExit("no bundles -- refusing to report an empty baseline")

    paths, refused = coverage(paths)
    if refused:
        print(f"NOT CLASSIFIABLE: {len(refused)} bundle(s). The split cannot be computed on them.")
        for reason in sorted({r.split(";")[-1].strip()[:110] for r in refused.values()}):
            print(f"  reason: ...{reason}")
        print()
    if not paths:
        print("NO BUNDLE IN THE CORPUS CAN BE FIVE-BUCKET SPLIT.")
        print("There is no baseline for this mapping and none can be recovered:")
        print("  the refusal CAUSES are absent from the record, not merely unparsed.")
        print("The first classifiable bundle will be the first ever computed.")
        return

    totals = {b: {s: 0 for s in states} for b, states in BUCKETS.items()}
    segments = 0
    flagged_bundles = 0
    for p in paths:
        r = five_bucket(json.load(open(p)))
        if r["residual"]:
            raise SystemExit(f"{p}: residual {r['residual']} -- states do not partition segments")
        segments += r["n_segments"]
        if any(v["uninterpretable_states"] for v in r["buckets"].values()):
            flagged_bundles += 1
        for b, v in r["buckets"].items():
            for s, n in v["by_state"].items():
                totals[b][s] += n

    print(f"{'bucket':16s} {'count':>6}  {'share of segments':>17}   states")
    for b, states in totals.items():
        n = sum(states.values())
        detail = "  ".join(f"{s}={c}" for s, c in states.items() if c)
        print(f"{b:16s} {n:>6}  {100*n/segments:>16.1f}%   {detail or '-'}")
    print(f"\n{segments} segments over {len(paths)} bundles. "
          f"{flagged_bundles} bundle(s) carry a state whose predicate does not hold.")
    print("NOT SUMMED and no rate reported: the buckets answer different questions.")
    print(f"KNOWN POOLING, splittable when a bundle shows one: {KNOWN_POOLING}")
    if MANIPULATION_UNREACHABLE:
        print("MANIPULATION IS STRUCTURALLY EMPTY: refused_unavailable cannot fire. "
              "A 0 there is uninformative, not a finding.")


if __name__ == "__main__":
    main(sys.argv[1:])
