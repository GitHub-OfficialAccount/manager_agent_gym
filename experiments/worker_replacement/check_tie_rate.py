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

THREE THINGS ARE MEASURED, because the first two can both pass while the hazard is
fully present:

  1. TIE COUNT — how many capacity-feasible allocations attain the optimum. This
     is the obvious measurement and it is the least informative: five-class
     instances already carry ~12 tied optima and are completely safe.
  2. CEILING SPREAD across the believed-optimal tie set — the range of answers one
     instance could give depending on which tied allocation is returned. This is
     what decides whether ties matter, and it separates the two cases cleanly:
     0.00% at five classes, 7.00% mean with the clone.
  3. DETERMINISM UNDER A REORDERED SEGMENT LIST (RR) — because enumeration order
     IS the hazard, a stable tie rate measured under one fixed order would look
     like a pass. Permuting segments cannot change the optimum's VALUE, so any
     spread across orderings is tie-break luck and nothing else.

Run:  python3 -m experiments.worker_replacement.check_tie_rate
"""

from __future__ import annotations

import json
import random
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

    # --- RR's requirement: DETERMINISM UNDER A REORDERED SEGMENT LIST -----------
    # A stable tie RATE measured under one fixed order would look like a pass while
    # the hazard was fully present, because enumeration order IS the hazard. This
    # runs the shipped ceiling on permuted segment lists and reports the spread of
    # the answers. Permuting segments is a relabelling: it cannot change the
    # optimum's VALUE, so any spread here is tie-break luck and nothing else.
    print("\nDETERMINISM UNDER A REORDERED SEGMENT LIST (RR). Permuting segments")
    print("cannot change the optimum's value, so any spread is tie-break luck:")
    print(f"{'instance set':<18} {'distinct ceilings':>18} {'spread':>9} {'unstable':>10}")
    reorder = {}
    for name, builder in (
            ("five_class", lambda s: gen.generate(s)),
            ("six_class_clone", lambda s: gen.generate(
                s, coverage_override=six_template, asset_classes=six_classes))):
        worst_spread, unstable, max_distinct = 0.0, 0, 1
        for seed in SEEDS:
            instance = builder(seed)
            rng = random.Random(f"segment-order::{seed}")
            values = []
            for _ in range(8):
                order = list(instance["segments"])
                rng.shuffle(order)
                values.append(sc.ceiling_vs_stale_card(
                    {**instance, "segments": order}, cap=CAP)["ceiling_share"] or 0.0)
            spread = max(values) - min(values)
            max_distinct = max(max_distinct, len({round(v, 12) for v in values}))
            worst_spread = max(worst_spread, spread)
            unstable += spread > 1e-9
        reorder[name] = {"max_distinct_ceilings": max_distinct,
                         "worst_spread": worst_spread,
                         "seeds_unstable": unstable, "orders_per_seed": 8}
        print(f"{name:<18} {max_distinct:>18} {worst_spread:>8.2%} "
              f"{unstable:>7}/{len(list(SEEDS))}")
    summary["reordering"] = reorder

    five, six = summary["five_class"], summary["six_class_clone"]
    rose = (six["mean_optima_true"] > five["mean_optima_true"] + 1e-9
            or six["seeds_with_tie_true"] > five["seeds_with_tie_true"])
    print()
    # The two halves say DIFFERENT things and both must hold. The tie set is a
    # property of the LATTICE and the clone genuinely enlarges it — that does not
    # go away and should not be reported as if it had. What the D19 tie-break
    # removes is the EXPOSURE: the shipped ceiling no longer depends on which
    # member of that set the enumeration happens to reach first.
    stable = all(r["seeds_unstable"] == 0 for r in reorder.values())
    if rose:
        print("THE HAZARD IS REAL: the clone enlarges the believed-optimal tie set")
        print(f"({five['mean_optima_true']:.1f} -> {six['mean_optima_true']:.1f} mean "
              f"optima) and the ceiling spread ACROSS that set is")
        print(f"{six['ceiling_spread_mean']:.2%} mean / {six['ceiling_spread_max']:.2%} "
              f"max — the same order as the effect being measured.")
    else:
        print("The clone does not enlarge the tie set on these seeds.")
    print()
    if stable:
        print("AND THE EXPOSURE IS CLOSED: under the D19 expectation tie-break the")
        print("shipped ceiling is IDENTICAL across every segment ordering, on both")
        print("class counts. The tie set remains; the arbitrariness does not.")
    else:
        print("EXPOSURE STILL OPEN: the shipped ceiling changes with segment order,")
        print("so a size-3 figure would be decided by list order. Do not quote one.")
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
    return 0 if stable else 1


if __name__ == "__main__":
    raise SystemExit(main())
