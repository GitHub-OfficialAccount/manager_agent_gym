"""R2 — the instance selection rule. RECORDED BEFORE ANY EPISODE RUNS.

Three instances, used across ALL SIX CELLS, so every contrast is paired on
(instance, segment) rather than confounded with which instances a cell happened
to draw.

WHY STRATIFIED AND NOT RANDOM. A plain random draw of three from the admitted
suite can land on three similar instances. Between-instance effect heterogeneity
is one of the four quantities this run exists to measure (measured prior: ceiling
sd 0.0254, CV 23%), and a clustered draw would understate it — the run would
report a heterogeneity estimate whose smallness was an artifact of the draw.

WHY THE BAND AND NOT THE FAVOURABLE END. The C2 obligation: selection must never
be CONDITIONED on `ceiling_vs_ignorant` toward the high end, or sigma is
measured on a sample chosen by the quantity it will threshold. Terciles balance
across the band — one instance from the low third, one from the middle, one from
the high — which is not the same as picking the best three and is deliberately
not as favourable.

The rule, the tercile bounds and the draw seed are committed BEFORE any episode.
That is the whole point of the obligation: a selection rule written afterwards is
indistinguishable from one fitted to the results.

  uv run python -m experiments.worker_replacement.select_study_instances
"""

from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path

from . import finance_admission as adm
from . import finance_gate as gate
from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records" / "R2"

# Fixed BEFORE the draw and recorded here so the draw is reproducible and cannot
# be re-rolled until it looks better.
DRAW_SEED = 20260807
SUITE_SEEDS = range(40)


def main() -> int:
    suite = adm.admit_suite(SUITE_SEEDS)
    admitted = [row["seed"] for row in suite["rows"] if row["admitted"]]

    # STRATIFY ON THE STUDY'S OWN COUNTERFACTUAL, not on the ignorant baseline.
    # The previous version ranked on `ceiling_vs_ignorant`, which asks what
    # coverage information is worth against knowing NOTHING. The manager is never
    # ignorant — it holds the predecessor's card — so that quantity ranked
    # instances by a question the study does not ask. Over 12 seeds the two
    # baselines differ by 10.9x and disagree about which instances are alive:
    # 6 of 12 have a stale-card ceiling of EXACTLY ZERO with a healthy ignorant
    # one. It selected two dead instances out of three, seed 36 among them with
    # the HIGHEST ignorant ceiling of the set. See records/L4/DIRECTIONS_LS.md.
    ceilings = {}
    for seed in admitted:
        instance = gen.generate(seed)
        ceilings[seed] = sc.ceiling_vs_stale_card(
            instance, cap=gate.CAP)["ceiling_share"]

    # An instance whose stale-card ceiling is ZERO cannot exhibit a card effect
    # however many episodes it is given. Admitting one is not a weak filter, it
    # is a broken one — so they are excluded before stratifying rather than
    # ranked into the low tercile.
    dead = sorted(s for s in admitted if ceilings[s] <= 0.0)
    admitted = [s for s in admitted if ceilings[s] > 0.0]
    if not admitted:
        raise ValueError(
            "no admitted instance has a non-zero stale-card ceiling; the "
            "manipulation cannot act on this suite and no run will change that"
        )

    ordered = sorted(admitted, key=lambda s: ceilings[s])
    n = len(ordered)
    # Terciles by RANK, not by value: equal-count strata, so a skewed band cannot
    # leave a stratum with one member.
    bounds = [n // 3, 2 * n // 3]
    strata = {
        "low": ordered[:bounds[0]],
        "mid": ordered[bounds[0]:bounds[1]],
        "high": ordered[bounds[1]:],
    }

    rng = random.Random(DRAW_SEED)
    chosen = {name: rng.choice(seeds) for name, seeds in strata.items()}

    values = [ceilings[s] for s in admitted]
    payload = {
        "ceiling_baseline": (
            "stale card — oracle minus optimal play believing the predecessor's "
            "card. NOT the ignorant baseline; see finance_scorer's ceiling section"
        ),
        "excluded_zero_ceiling_seeds": dead,
        # The rank-tercile is over `ceiling_vs_stale_card`, which is what the code
        # above computes. This string said `ceiling_vs_ignorant` after the
        # baseline was changed underneath it — documentation naming a source that
        # did not produce the value, which is the fault the baseline change
        # existed to fix, surviving in the record OF that fix.
        "rule": ("three instances used across ALL six cells; one drawn at random "
                 "from each rank-tercile of ceiling_vs_stale_card over the "
                 "admitted suite; draw seed fixed and recorded before the draw"),
        "belief_model": (
            "WHOLE CARD (D1) — the successor is scored throughout as the "
            "predecessor's card describes it, so the card's OMISSION costs as "
            "well as its LIE. Selections recorded before D1 ranked on the "
            "lie-only model and are NOT comparable seed-for-seed"),
        "recorded_before_any_episode": True,
        "draw_seed": DRAW_SEED,
        "suite_seeds": list(SUITE_SEEDS),
        "n_admitted": n,
        "ceiling_band": {
            "min": min(values), "median": st.median(values), "max": max(values),
            "sd": st.stdev(values),
        },
        "tercile_bounds_by_rank": {
            "low": [0, bounds[0]], "mid": bounds, "high": [bounds[1], n],
        },
        "tercile_ceiling_ranges": {
            name: {"n": len(seeds),
                   "min": min(ceilings[s] for s in seeds),
                   "max": max(ceilings[s] for s in seeds)}
            for name, seeds in strata.items()
        },
        "strata_seeds": strata,
        "chosen": {name: {"seed": seed, "ceiling_share": ceilings[seed]}
                   for name, seed in chosen.items()},
        "chosen_seeds": sorted(chosen.values()),
        "ceilings_by_seed": ceilings,
    }

    # TWO PROPERTIES OF THIS DRAW that travel with every number it produces.
    # Properties of the RULE and this realisation of it, not results — and they
    # bias in a direction a reader must know about, so they are fields in the
    # record rather than a footnote a summariser can drop.
    chosen_shares = [ceilings[s] for s in chosen.values()]
    payload["sampling_caveats"] = {
        "chosen_mean": st.fmean(chosen_shares),
        "admitted_median": st.median(values),
        "admitted_mean": st.fmean(values),
        "low_pick_is_suite_minimum": min(chosen_shares) == min(values),
        "effect_magnitudes_sit_below_the_suite": (
            st.fmean(chosen_shares) < st.fmean(values)),
        "caveat_1": ("THE LOW PICK IS THE SUITE MINIMUM. Seed 23 at "
                     f"{min(chosen_shares):.4f} is the minimum of the whole "
                     "admitted suite — a legitimate 1-in-11 draw, not a "
                     "take-first artefact (draw indices 0/5/5 within strata). "
                     "Consequence: the chosen mean sits BELOW the admitted mean, "
                     "so the pilot's EFFECT MAGNITUDES are below the suite's by "
                     "construction."),
        "caveat_2": ("IT COMPOUNDS WITH THE STRATIFICATION INFLATION. The rule "
                     "widens sigma_between BY DESIGN and this particular draw "
                     "shifts the centre DOWN. Harmless for sigma — that is noise, "
                     "not effect — and NOT harmless for anything reading effect "
                     "magnitudes. Both must be named wherever the pilot's numbers "
                     "appear."),
    }

    # A NEW FILENAME, NOT AN OVERWRITE. The pre-D1 selection was made under the
    # lie-only belief model and three episodes were already run against its
    # seeds; overwriting it would leave those runs pointing at a selection record
    # that no longer describes how their seeds were chosen.
    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / "instance_selection_v2_wholecard.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print("R2 — instance selection (recorded BEFORE any episode)\n")
    print(f"admitted suite: {n} of {len(list(SUITE_SEEDS))} seeds")
    print(f"ceiling band: min {min(values):.4f}  median {st.median(values):.4f}  "
          f"max {max(values):.4f}  sd {st.stdev(values):.4f}")
    print(f"draw seed: {DRAW_SEED}\n")
    for name in ("low", "mid", "high"):
        rng_lo = payload["tercile_ceiling_ranges"][name]
        print(f"  {name:<5} tercile  n={rng_lo['n']:<3} ceiling "
              f"{rng_lo['min']:.4f}-{rng_lo['max']:.4f}  -> chose seed "
              f"{chosen[name]:<3} at {ceilings[chosen[name]]:.4f}")
    print(f"\nchosen seeds: {sorted(chosen.values())}")
    print("used across ALL SIX cells, so contrasts are paired on (instance, segment)")
    caveats = payload["sampling_caveats"]
    print(f"\nTWO PROPERTIES OF THIS DRAW — carry BOTH wherever the pilot's "
          f"numbers appear:")
    print(f"  1. the low pick IS the suite minimum "
          f"({min(chosen_shares):.4f}); chosen mean "
          f"{caveats['chosen_mean']:.4f} vs admitted mean "
          f"{caveats['admitted_mean']:.4f}\n     -> EFFECT MAGNITUDES SIT BELOW "
          f"THE SUITE'S BY CONSTRUCTION")
    print(f"  2. it compounds with the stratification inflation: the rule widens "
          f"sigma_between by\n     design AND this draw shifts the centre down. "
          f"Harmless for sigma, NOT harmless for\n     effect magnitudes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
