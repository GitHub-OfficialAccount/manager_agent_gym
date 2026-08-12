"""Does the six-class CLONE manufacture exact ties in the allocation optimum?

THE HAZARD, and it is created by us rather than found. A clone class has economics
IDENTICAL to its source, so a segment of the clone and a segment of the source score
EXACTLY equal under any worker covering both — and two allocations that differ only
by swapping them have bit-identical totals. The optimum is then not unique, and
which one `best()` returns is decided by the order `product()` happens to visit,
which is an artefact of enumeration order and of nothing scientific.

WHY THAT MATTERS HERE SPECIFICALLY. The ceiling is a DIFFERENCE between two
optima — the true one and the card-believing one. If either is drawn from a tie set
by visit order, the difference inherits that arbitrariness, and it does so INSIDE
the quantity the template decision is made on. Tie-break luck is the reason this
project permutes class labels at all; manufacturing ties ourselves, in the optimum
that produces the headline, would be the same fault deliberately introduced.

WHAT IS MEASURED: among all capacity-feasible allocations, how many attain the
optimum. A rate of 1 means the optimum is unique. Six-class clone instances are
compared against five-class ones on the same seeds.

Run:  python3 -m experiments.worker_replacement.check_tie_rate
"""

from __future__ import annotations

import json
import statistics as st
from itertools import product
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(20)
TIE_EPS = 1e-12          # the project's tie epsilon; equal scores are bit-identical


def optimum_multiplicity(instance: dict[str, Any]) -> dict[str, Any]:
    """How many capacity-feasible allocations attain the optimum, under each belief."""
    event = instance["event"]
    calibration = instance["class_calibration"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    roster = [by_id[w] for w in event["roster_post_swap"]]
    segments = instance["segments"]
    successor = event["successor_id"]
    card_claims = tuple(by_id[event["predecessor_id"]]["irb_coverage"])

    carded = dict(by_id[successor])
    carded["irb_coverage"] = card_claims
    carded["private_pd_calibration"] = {c: calibration[c] for c in card_claims}

    true_m = [[sc.s(sg, w, calibration) for w in roster] for sg in segments]
    believed_m = [[sc.s(sg, carded, calibration) if i == 0 else true_m[j][i]
                   for i in range(len(roster))]
                  for j, sg in enumerate(segments)]

    def multiplicity(matrix) -> tuple[int, int]:
        best_value, count, feasible = -1.0, 0, 0
        for combo in product(range(len(roster)), repeat=len(segments)):
            if any(combo.count(i) > CAP for i in range(len(roster))):
                continue
            feasible += 1
            value = sum(matrix[j][w] for j, w in enumerate(combo))
            if value > best_value + TIE_EPS:
                best_value, count = value, 1
            elif abs(value - best_value) <= TIE_EPS:
                count += 1
        return count, feasible

    true_ties, feasible = multiplicity(true_m)
    believed_ties, _ = multiplicity(believed_m)

    # THE QUANTITY THAT ACTUALLY DECIDES WHETHER TIES MATTER, and counting them
    # does not answer it. Ties in the TRUE optimum are harmless: every tied
    # allocation has the same value by definition, so `true_value` is unique
    # regardless of which one is returned.
    #
    # The exposure is on the BELIEVED side. All believed-optimal allocations are
    # equal UNDER THE CARD, and they are then RE-SCORED UNDER TRUTH — where they
    # need not be equal at all. So the ceiling depends on WHICH member of the tie
    # set `best()` happens to return, i.e. on enumeration order. This measures the
    # SPREAD of the ceiling across that tie set: the range of answers the same
    # instance could have given.
    best_believed = max(
        sum(believed_m[j][w] for j, w in enumerate(combo))
        for combo in _feasible(len(roster), len(segments)))
    realised = [
        sum(true_m[j][w] for j, w in enumerate(combo))
        for combo in _feasible(len(roster), len(segments))
        if abs(sum(believed_m[j][w] for j, w in enumerate(combo))
               - best_believed) <= TIE_EPS]
    true_value = max(
        sum(true_m[j][w] for j, w in enumerate(combo))
        for combo in _feasible(len(roster), len(segments)))
    ceilings = [(true_value - r) / true_value if true_value else 0.0
                for r in realised]
    return {"true_optima": true_ties, "believed_optima": believed_ties,
            "feasible": feasible,
            "ceiling_min": min(ceilings), "ceiling_max": max(ceilings),
            "ceiling_spread": max(ceilings) - min(ceilings)}


def _feasible(n_workers: int, n_segments: int):
    for combo in product(range(n_workers), repeat=n_segments):
        if all(combo.count(i) <= CAP for i in range(n_workers)):
            yield combo


def main() -> int:
    print("Exact-tie rate among optimal allocations: six-class CLONE vs five-class\n")

    clone = gen.register_synthetic_clone("corporate_clone", "corporate")
    six_classes = gen.ASSET_CLASSES + (clone,)
    # A size-3 partial-overlap template over six classes: w0 and w1 share
    # `sovereign`, w0 sole-holds `bank`, and the clone sits on the incumbents so
    # source and clone segments are both live and can tie against each other.
    six_template = [("sovereign", "bank", "corporate"),
                    ("sovereign", "retail", "mdb"),
                    ("corporate", "retail", clone),
                    ("mdb", clone, "bank")]

    rows: dict[str, list[dict[str, Any]]] = {"five_class": [], "six_class_clone": []}
    for seed in SEEDS:
        rows["five_class"].append(optimum_multiplicity(gen.generate(seed)))
        rows["six_class_clone"].append(optimum_multiplicity(
            gen.generate(seed, coverage_override=six_template,
                         asset_classes=six_classes)))

    summary = {}
    print(f"{'instance set':<18} {'mean |argmax| (true)':>21} {'max':>5} "
          f"{'seeds with a tie':>18}")
    for name, out in rows.items():
        true_counts = [r["true_optima"] for r in out]
        tied = sum(1 for c in true_counts if c > 1)
        summary[name] = {
            "mean_optima_true": st.mean(true_counts),
            "max_optima_true": max(true_counts),
            "seeds_with_tie_true": tied,
            "mean_optima_believed": st.mean(r["believed_optima"] for r in out),
            "max_optima_believed": max(r["believed_optima"] for r in out),
            "seeds_with_tie_believed": sum(
                1 for r in out if r["believed_optima"] > 1),
            "feasible_allocations": out[0]["feasible"],
            "ceiling_spread_mean": st.mean(r["ceiling_spread"] for r in out),
            "ceiling_spread_max": max(r["ceiling_spread"] for r in out),
            "seeds_with_ambiguous_ceiling": sum(
                1 for r in out if r["ceiling_spread"] > 1e-9),
        }
        print(f"{name:<18} {st.mean(true_counts):>21.2f} {max(true_counts):>5} "
              f"{tied:>15}/{len(out)}")

    print(f"\n{'instance set':<18} {'ceiling spread mean':>21} {'max':>9} "
          f"{'ambiguous':>12}")
    for name in rows:
        s = summary[name]
        print(f"{name:<18} {s['ceiling_spread_mean']:>20.2%} "
              f"{s['ceiling_spread_max']:>8.2%} "
              f"{s['seeds_with_ambiguous_ceiling']:>9}/{len(rows[name])}")

    five, six = summary["five_class"], summary["six_class_clone"]
    rose = (six["mean_optima_true"] > five["mean_optima_true"] + 1e-9
            or six["seeds_with_tie_true"] > five["seeds_with_tie_true"])
    print()
    if rose:
        print("TIE RATE RISES WITH THE CLONE. The optimum is not unique, so which")
        print("allocation `best()` returns is decided by enumeration order — inside")
        print("the ceiling the template decision rests on. THE TIE-BREAK MUST BE")
        print("MADE EXPLICIT before any size-3 figure is quoted.")
    else:
        print("Tie rate does NOT rise with the clone. The ceiling is not exposed to")
        print("enumeration order by the sixth class.")
    print("\nNOTE ON WHAT A NULL HERE DOES AND DOES NOT LICENCE: it says THIS")
    print("template on THESE seeds does not manufacture ties. It is not a property")
    print("of clones in general — a template placing source and clone on the SAME")
    print("worker, or a segment mix putting more weight on both, could still do it.")

    out_dir = HERE / "records" / "L9"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tie_rate.json").write_text(json.dumps({
        "summary": summary,
        "tie_rate_rises_with_clone": rose,
        "clone_source": gen.SYNTHETIC_CLASSES[clone],
        "six_class_template": [list(c) for c in six_template],
        "seeds": list(SEEDS),
        "tie_eps": TIE_EPS,
        "caveats": [
            "measured on ONE size-3 template; not a property of clones in general",
            "ties are counted with the project's TIE_EPS against bit-identical "
            "scores, so this counts EXACT ties, not near-ties that a different "
            "float path could turn into ties",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out_dir / 'tie_rate.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
