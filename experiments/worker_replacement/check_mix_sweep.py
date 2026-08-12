"""Ceiling as a function of TEMPLATE x MIX, because template alone is not a number.

WHY. `check_template_pricing` reported 8.51% / 1.11 sigma for the disjoint
candidate as though it were a property of the template. It is the property of one
MIX. `labels_of()` recovers `a` as the current template's shared class,
`shared_class_segments = 4` forces four segments into it, and the disjoint
candidate's successor-unique class IS `a` — so nA = 4 in 30 of 30 seeds, the most
favourable point in the range. Reporting the maximum of a range as the range's
value is the error this module exists to stop repeating.

nA — the number of IRB-APPLICABLE segments in the SUCCESSOR-UNIQUE class — is what
the effect scales with, because those are the segments only the successor can serve
post-swap. It is the mix parameter, so every figure here carries it.

HOW THE MIX IS VARIED WITHOUT A GENERATOR CHANGE. Not by re-recovering each
instance's own permutation and perturbing it — that inherits the forcing being
measured. Instead ALL 120 label permutations are applied to each instance, so the
template's roles land on every possible set of real asset classes. nA is then
MEASURED per cell rather than requested, and cells are grouped by it. This is RR's
probe generalised: same construction, both candidate templates, and the corrected
belief model.

THE BELIEF MODEL IS THE REPLACEMENT ONE, NOT `ceiling_vs_stale_card`. The shipped
function models the card's lie and not its omission, and on the disjoint template
that is 96% of the effect — see `check_card_belief_model.py`, which measures the
gap against a passing positive control. Pricing a mix sweep with it would flatten
exactly the cells the sweep exists to distinguish.

WHAT THIS DOES NOT PRICE. Only COVERAGE_SIZE=2 templates over the five existing
classes. Size-3 partial overlap needs a sixth asset class and therefore GENERATED
instances — permuting labels cannot invent segments for a class no instance has.

Run:  python3 -m experiments.worker_replacement.check_mix_sweep
"""

from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from itertools import permutations, product
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(10)          # 10 seeds x 120 labelings = 1200 cells, as RR's probe
SIGMA = 0.0768             # PRE-L1 and stale: scales the comparison, never sizes a suite

# Roles are DECLARED positionally: predecessor, successor, incumbent, incumbent.
TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    "current": ("ae", "ab", "bc", "cd"),
    "proposed_disjoint": ("de", "ab", "ce", "cb"),
}


def successor_unique_class(template: tuple[str, str, str, str]) -> str:
    """The class the successor ALONE holds post-swap, in template labels.

    Derived from the template rather than assumed to be `a`: the two candidates
    happen to agree on `a`, and hardcoding it would break silently on the third.
    """
    w1, w2, w3 = set(template[1]), set(template[2]), set(template[3])
    unique = sorted(w1 - w2 - w3)
    if len(unique) != 1:
        raise ValueError(
            f"template {template} has {len(unique)} successor-unique classes "
            f"({unique}); nA is defined only when there is exactly one")
    return unique[0]


def ceiling_under_mix(instance: dict[str, Any],
                      template: tuple[str, str, str, str],
                      labeling: tuple[str, ...]) -> dict[str, Any]:
    """Ceiling for one (instance, template, labeling), under the REPLACEMENT card.

    Score matrices are precomputed per (segment, worker) so the capacitated
    enumeration sums cached floats instead of re-deriving Basel numbers 19683
    times. The optimum is unchanged — this is caching, not approximation.
    """
    event = instance["event"]
    calibration = instance["class_calibration"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    predecessor, successor = event["predecessor_id"], event["successor_id"]
    incumbents = [w for w in event["roster_post_swap"] if w != successor]
    role_ids = [predecessor, successor, incumbents[0], incumbents[1]]

    label_map = dict(zip("abcde", labeling))
    coverage = {wid: tuple(label_map[ch] for ch in spec)
                for wid, spec in zip(role_ids, template)}

    def as_worker(wid: str, cover: tuple[str, ...]) -> dict[str, Any]:
        row = dict(by_id[wid])
        row["irb_coverage"] = cover
        row["private_pd_calibration"] = {c: calibration[c] for c in cover}
        return row

    roster = [as_worker(wid, coverage[wid]) for wid in role_ids[1:]]
    # The card describes the SUCCESSOR as the PREDECESSOR was: it claims what the
    # predecessor covered, entire. False claims grant coverage the successor lacks
    # AND omissions withhold coverage it has.
    carded = as_worker(successor, coverage[predecessor])

    segments = instance["segments"]
    true_m = [[sc.s(sg, w, calibration) for w in roster] for sg in segments]
    believed_m = [[sc.s(sg, carded, calibration) if i == 0 else true_m[j][i]
                   for i in range(len(roster))]
                  for j, sg in enumerate(segments)]

    def best(matrix):
        best_value, best_alloc = -1.0, ()
        for combo in product(range(len(roster)), repeat=len(segments)):
            if any(combo.count(i) > CAP for i in range(len(roster))):
                continue
            value = sum(matrix[j][w] for j, w in enumerate(combo))
            if value > best_value:
                best_value, best_alloc = value, combo
        return best_value, best_alloc

    true_value, _ = best(true_m)
    _, believed_alloc = best(believed_m)
    realised = sum(true_m[j][w] for j, w in enumerate(believed_alloc))

    unique_class = label_map[successor_unique_class(template)]
    n_a = sum(1 for sg in segments
              if sg["irb_approved"] and sg["asset_class"] == unique_class)
    return {"n_a": n_a, "share": (true_value - realised) / true_value if true_value else 0.0}


def main() -> int:
    print("Ceiling by TEMPLATE x MIX. nA = IRB-applicable segments in the")
    print("successor-unique class — the mix parameter the effect scales with.\n")
    print("Belief model: the card as a REPLACEMENT description (whole card).")
    print(f"Sigma {SIGMA} is PRE-L1 and stale: it scales, it does not size.\n")

    labelings = list(permutations(gen.ASSET_CLASSES))
    out_rows: dict[str, Any] = {}
    for name, template in TEMPLATES.items():
        by_na: dict[int, list[float]] = defaultdict(list)
        for seed in SEEDS:
            instance = gen.generate(seed)
            for labeling in labelings:
                row = ceiling_under_mix(instance, template, labeling)
                by_na[row["n_a"]].append(row["share"])
        total = sum(len(v) for v in by_na.values())
        print(f"{name}")
        print(f"   {'nA':>3} {'cells':>7} {'% of cells':>11} {'mean share':>11} {'~sigma':>8}")
        rows = {}
        for n_a in sorted(by_na):
            shares = by_na[n_a]
            mean = st.mean(shares)
            rows[n_a] = {"cells": len(shares), "share_of_cells": len(shares) / total,
                         "mean_share": mean, "sigma_units": mean / SIGMA,
                         "sd_share": st.pstdev(shares)}
            print(f"   {n_a:>3} {len(shares):>7} {len(shares) / total:>10.1%} "
                  f"{mean:>10.2%} {mean / SIGMA:>7.2f}")
        pooled = [s for v in by_na.values() for s in v]
        print(f"   pooled over the natural label distribution: "
              f"{st.mean(pooled):.2%} / {st.mean(pooled) / SIGMA:.2f} sigma\n")
        out_rows[name] = {"by_n_a": rows, "pooled_mean_share": st.mean(pooled),
                          "pooled_sigma_units": st.mean(pooled) / SIGMA}

    print("READ THIS BEFORE QUOTING ANY FIGURE ABOVE. A template does not have a")
    print("sigma; a template AND A MIX have one. The forced mix that produced the")
    print("8.51% / 1.11 sigma headline is the nA=4 row, and it is a minority of the")
    print("label space. Choosing the mix chooses the answer, so it is a design")
    print("decision that has to be made and recorded, not inherited by default.")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "mix_sweep.json").write_text(json.dumps({
        "templates": {k: list(v) for k, v in TEMPLATES.items()},
        "results": out_rows,
        "n_seeds": len(list(SEEDS)),
        "n_labelings": len(labelings),
        "sigma_used": SIGMA,
        "belief_model": "the card as a REPLACEMENT description of the successor",
        "caveats": [
            "COVERAGE_SIZE=2 over the five existing classes ONLY. Size-3 partial "
            "overlap needs a sixth asset class and therefore GENERATED instances: "
            "permuting labels cannot invent segments for a class no instance has.",
            "a CEILING — optimal play under truth minus optimal play under the "
            "card, scored in the true world. It does not say any manager realises "
            "it.",
            "sigma is the PRE-L1 measurement and must not size a suite",
            "the pooled row weights every labeling equally, which is the label "
            "space and NOT the mix any generator would produce. It is the "
            "no-forcing reference point, not a prediction.",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'mix_sweep.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
