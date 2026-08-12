"""The agreed read order for the first classifiable bundle, and the prediction scoring.

Written BEFORE the bundle exists. This is the third instrument today built ahead of its
subject, for the same reason as the other two: the first five-bucket split in the study's
history should not be analysed ad hoc, and a prediction scored after seeing the answer is
not a prediction.

READ ORDER, agreed with RE and RR and not reorderable here:

    1. five_bucket_split   -- nobody touches non-completion until it says which bucket
    2. worker runs vs 966s -- the observed healthy ceiling; `partial` is a different
                              portfolio, so this is the number most likely to move
    3. agent_available     -- now only to confirm the field is decorative

Zero model calls. Run:

    python -m experiments.worker_replacement.analyse_first_bundle <bundle.json>
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from typing import Any

from .five_bucket_split import BUCKETS, MANIPULATION_UNREACHABLE, five_bucket

# The observed healthy ceiling on worker runs, from measure_episode_baseline.py over the
# 20 committed bundles: max 966s, exact pairing on (actor_id, task_id), 0 unmatched.
HEALTHY_WORKER_CEILING_S = 966.0
RAISED_TIMEOUT_S = 1200.0

# THE THREE PREDICTIONS, committed before the bundle existed. Recorded here verbatim so
# scoring cannot drift toward whatever happened.
PREDICTIONS: dict[str, dict[str, Any]] = {
    "LS": {"largest_non_measurement": "BUDGET_HORIZON", "manipulation": "0 or 1"},
    "RE": {"largest_non_measurement": "DV", "manipulation": "0"},
    "RR": {"largest_non_measurement": "DV", "manipulation": "0"},
}


def _ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def worker_runs(bundle: dict[str, Any]) -> tuple[list[float], int]:
    """Exact pairing on (actor_id, task_id). Unmatched must be 0 or the number is void."""
    ev = sorted((e for e in bundle.get("events") or [] if e.get("timestamp")),
                key=lambda e: e["timestamp"])
    open_: dict[tuple, list[dt.datetime]] = {}
    durs: list[float] = []
    unmatched = 0
    for e in ev:
        key = (e.get("actor_id"), e.get("task_id"))
        t = e.get("event_type")
        if t == "worker_execution_started":
            open_.setdefault(key, []).append(_ts(e["timestamp"]))
        elif t in ("worker_execution_completed", "worker_execution_failed"):
            if open_.get(key):
                durs.append((_ts(e["timestamp"]) - open_[key].pop(0)).total_seconds())
            else:
                unmatched += 1
    unmatched += sum(len(v) for v in open_.values())
    return sorted(durs), unmatched


def availability(bundle: dict[str, Any]) -> tuple[int, int]:
    """How often `agent_available` is present, and how often it is False."""
    seen = false = 0
    for e in bundle.get("events") or []:
        payload = e.get("payload") or {}
        if "agent_available" in payload:
            seen += 1
            false += payload["agent_available"] is False
    return seen, false


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("usage: analyse_first_bundle.py <bundle.json>")
    path = argv[0]
    bundle = json.load(open(path))
    print(f"# First classifiable bundle: {path}\n")

    # ---- 1. THE SPLIT, FIRST AND WITHOUT EXCEPTION -------------------------------
    print("## 1. Five-bucket split")
    try:
        result = five_bucket(bundle)
    except ValueError as exc:
        # A bundle that CANNOT be split stops the analysis here, deliberately. Every
        # later section would still compute -- worker durations and agent_available do
        # not need refusal codes -- and printing them under the heading "first
        # classifiable bundle" would present a pre-fix bundle as analysed. The standing
        # rule is that nobody touches non-completion until the split says which bucket;
        # so if the split cannot speak, nothing after it is reported either.
        print(f"  REFUSED: {exc}")
        print("\n  This bundle is NOT classifiable and the analysis stops here.")
        print("  Sections 2-4 are suppressed: they would compute fine and would be read")
        print("  as an analysis of a bundle the split could not speak for.")
        return 2
    
    if result["residual"]:
        raise SystemExit(f"residual {result['residual']} -- states do not partition segments")
    counts = {b: v["count"] for b, v in result["buckets"].items()}
    for b in BUCKETS:
        v = result["buckets"][b]
        states = "  ".join(f"{s}={n}" for s, n in v["by_state"].items() if n)
        flag = "  [UNINFORMATIVE]" if v.get("uninformative") else ""
        print(f"  {b:<16} {v['count']:>3}   {states or '-'}{flag}")
    print(f"  {result['n_segments']} segments. NOT summed and no rate reported.")

    # ---- 2. THE PREDICTIONS, SCORED AGAINST WHAT WAS COMMITTED --------------------
    print("\n## 2. Predictions, committed before the bundle existed")
    ranked = sorted((c for b, c in counts.items() if b != "MEASUREMENT"), reverse=True)
    largest = max((b for b in counts if b != "MEASUREMENT"), key=lambda b: counts[b])
    tied = [b for b in counts if b != "MEASUREMENT" and counts[b] == counts[largest]]
    print(f"  largest non-MEASUREMENT bucket: {largest}"
          + (f"  (TIED with {tied})" if len(tied) > 1 else ""))
    for who, pred in PREDICTIONS.items():
        hit = pred["largest_non_measurement"] == largest and len(tied) == 1
        print(f"    {who}: predicted {pred['largest_non_measurement']:<14} "
              f"-> {'HIT' if hit else 'MISS'}")
    print(f"    MANIPULATION predictions ({', '.join(p['manipulation'] for p in PREDICTIONS.values())})"
          f" -> VOID for all three" if MANIPULATION_UNREACHABLE else "")
    if MANIPULATION_UNREACHABLE:
        print("      refused_unavailable cannot fire in this harness, so the quantity "
              "could not have\n      come out otherwise. A prediction about a quantity "
              "that cannot vary is not a prediction.")

    # ---- 3. THE WORKER CEILING ---------------------------------------------------
    print("\n## 3. Worker runs against the observed healthy ceiling")
    durs, unmatched = worker_runs(bundle)
    if unmatched:
        print(f"  {unmatched} unmatched events -- pairing is not exact, durations VOID")
    elif not durs:
        print("  no worker runs in this bundle")
    else:
        over = [d for d in durs if d > HEALTHY_WORKER_CEILING_S]
        print(f"  n={len(durs)}  median {durs[len(durs)//2]:.0f}s  max {max(durs):.0f}s")
        print(f"  over the 966s healthy ceiling: {len(over)}")
        if over:
            print(f"  ** {len(over)} run(s) exceed every worker run observed in the corpus. "
                  f"1200s is no longer\n     clear of the workload and the bound moves before "
                  f"anyone builds on these numbers. **")
        print(f"  over the raised 1200s timeout: {len([d for d in durs if d > RAISED_TIMEOUT_S])}")

    # ---- 4. THE DECORATIVE FIELD -------------------------------------------------
    print("\n## 4. agent_available")
    seen, false = availability(bundle)
    print(f"  present on {seen} events, False on {false}")
    if seen and not false:
        print("  still constant -- the field discriminates nothing and should be fixed "
              "or removed\n  rather than left to mislead the next elimination.")

    print("\n## What this does NOT establish")
    print("  Nothing about effect size. This instance is the suite minimum at the settled")
    print("  cell and was selected at a cell the study does not ship; its value is the")
    print("  HARNESS measurement only. The split is one episode and carries no interval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
