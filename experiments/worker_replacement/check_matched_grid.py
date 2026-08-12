"""Carrier group x mix, fully crossed, with forcing on the SUCCESSOR-UNIQUE class.

WHY THE FORCED CLASS CHANGED (D51). The amplifiers were targeted at the SHARED
class. In `_lattice_from_template` the shared class IS the successor-unique class —
`w1` sole-holds A once `w0` leaves — so in the five-class arm the two names pick out
the same class and nothing distinguished them. At six classes they come apart, and
targeting the NAME rather than the MECHANISM locked carrier group to mix: the shared
class is the successor-unique one exactly when carriers=1, so carrier-1 templates
could only be measured at nA=4 and carrier-2 ones at nA<=1.

That lock is why the earlier "inversion" existed. It was a mix comparison wearing a
carrier label, and no ratio to a common reference removed it — the nA response is
not a common multiplicative factor across templates.

Forcing the SUCCESSOR-UNIQUE class instead matches the five-class arm by mechanism
rather than by label, and breaks the lock: nA becomes settable independently of
carrier group, so `carriers=1 @ nA=1` — the cell the ordering claim lives in —
becomes reachable.

MIX IS SET BY `shared_class_segments`, so nA is a REQUESTED parameter here. It is
still MEASURED per cell and the achieved distribution is printed, because a forced
parameter that lands on one value in every cell is a constant being reported as a
variable — which is how the original nA=4 forcing went unnoticed for a phase.

THREE THINGS DECLARED ON EVERY CEILING: baseline (stale card), belief model (whole
card, D1), tie-break (expectation over the believed-optimal set, D19).

THESE ARE LATTICE COMPARISONS. The sixth class does not exist; its weights are
copied and carry no BCBS transcription. No sigma appears and nothing here is an
episodes/arm budget. If a sentence about these numbers still reads sensibly with
"ceiling" replaced by "effect", it is wrong.

Run:  python3 -m experiments.worker_replacement.check_matched_grid
"""

from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from itertools import permutations
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc
from .check_size3_pricing import (CLONE_SOURCES, SEEDS, size3_templates,
                                  successor_unique)

HERE = Path(__file__).resolve().parent
CAP = 3
SEGMENT_COUNTS = (1, 4)          # nA=1 is the realistic mix; nA=4 the upper bound
DISJOINT = ("de", "ab", "ce", "cb")
DISJOINT_UNIQUE = (set(DISJOINT[1]) - set(DISJOINT[2]) - set(DISJOINT[3])).pop()
# Composition of the admissible size-3 partial-overlap space, for the pooled row.
CARRIER_WEIGHTS = {1: 2160, 2: 4320}


def build_six(template, clone_source: str, seed: int, n_segments: int):
    clone = gen.register_synthetic_clone(f"{clone_source}_clone", clone_source)
    classes = gen.ASSET_CLASSES + (clone,)
    labels = dict(zip("abcdef", classes))
    coverage = [tuple(labels[c] for c in sorted(s)) for s in template]
    try:
        instance = gen.generate(
            seed, coverage_override=coverage, asset_classes=classes,
            force_mix_class=labels[successor_unique(template)],
            shared_class_segments=n_segments)
    except gen.InstanceAssertionError:
        return None, labels
    return instance, labels


def achieved_n_a(instance: dict[str, Any], unique_class: str) -> int:
    return sum(1 for s in instance["segments"]
               if s["irb_approved"] and s["asset_class"] == unique_class)


def main() -> int:
    print("Carrier group x mix, forcing the SUCCESSOR-UNIQUE class (D51)")
    print("baseline: stale card | belief: whole card | tie-break: expectation\n")

    groups = size3_templates()
    # Paired across BOTH clone sources AND BOTH mixes, so every comparison in the
    # grid is on one population. Dropping each arm's own failures would compare
    # arms on different populations — the fault that corrupted the clone bracket.
    usable = {
        n: [(t, s) for t in templates for s in SEEDS
            if all(build_six(t, c, s, k)[0] is not None
                   for c in CLONE_SOURCES for k in SEGMENT_COUNTS)]
        for n, templates in groups.items()}
    dropped = {n: len(groups[n]) * len(list(SEEDS)) - len(v) for n, v in usable.items()}
    print(f"paired population: " + ", ".join(
        f"carriers={n} {len(v)} cells ({dropped[n]} dropped)" for n, v in usable.items()))

    print(f"\n{'clone':<11}{'carriers':>9}{'segs':>6}{'cells':>7}{'nA achieved':>14}"
          f"{'mean share':>12}")
    six: dict[str, Any] = {}
    for clone_source in CLONE_SOURCES:
        for n_carriers in groups:
            for k in SEGMENT_COUNTS:
                shares, achieved = [], defaultdict(int)
                for template, seed in usable[n_carriers]:
                    instance, labels = build_six(template, clone_source, seed, k)
                    achieved[achieved_n_a(
                        instance, labels[successor_unique(template)])] += 1
                    shares.append(sc.ceiling_vs_stale_card(
                        instance, cap=CAP)["ceiling_share"] or 0.0)
                six[f"{clone_source}|{n_carriers}|{k}"] = {
                    "mean_share": st.mean(shares), "cells": len(shares),
                    "n_a_achieved": dict(sorted(achieved.items()))}
                print(f"{clone_source:<11}{n_carriers:>9}{k:>6}{len(shares):>7}"
                      f"{str(dict(achieved)):>14}{st.mean(shares):>11.2%}")

    # --- the reference, forced THE SAME WAY through THE SAME PATH ---------------
    print(f"\n{'reference':<11}{'segs':>6}{'cells':>7}{'nA achieved':>14}{'mean share':>12}")
    reference: dict[int, float] = {}
    for k in SEGMENT_COUNTS:
        by_na = defaultdict(list)
        for seed in SEEDS:
            for labeling in permutations(gen.ASSET_CLASSES):
                labels = dict(zip("abcde", labeling))
                coverage = [tuple(labels[c] for c in spec) for spec in DISJOINT]
                try:
                    instance = gen.generate(
                        seed, coverage_override=coverage,
                        force_mix_class=labels[DISJOINT_UNIQUE],
                        shared_class_segments=k)
                except gen.InstanceAssertionError:
                    continue
                by_na[achieved_n_a(instance, labels[DISJOINT_UNIQUE])].append(
                    sc.ceiling_vs_stale_card(instance, cap=CAP)["ceiling_share"] or 0.0)
        values = [v for vs in by_na.values() for v in vs]
        reference[k] = st.mean(values)
        print(f"{'disjoint':<11}{k:>6}{len(values):>7}"
              f"{str({a: len(v) for a, v in sorted(by_na.items())}):>14}"
              f"{st.mean(values):>11.2%}")

    print("\nRATIO TO DISJOINT AT THE SAME FORCED COUNT, and the pooled row uses")
    print("size-3's TRUE composition (2160 carrier-1, 4320 carrier-2), because a")
    print("plain mean over the two groups is not a property of the design:")
    ratios: dict[str, Any] = {}
    for k in SEGMENT_COUNTS:
        print(f"  segs={k}  (disjoint {reference[k]:.2%})")
        for clone_source in CLONE_SOURCES:
            one = six[f"{clone_source}|1|{k}"]["mean_share"]
            two = six[f"{clone_source}|2|{k}"]["mean_share"]
            pooled = ((CARRIER_WEIGHTS[1] * one + CARRIER_WEIGHTS[2] * two)
                      / sum(CARRIER_WEIGHTS.values()))
            ratios[f"{clone_source}|{k}"] = {
                "carriers_1": one, "carriers_2": two, "pooled": pooled,
                "ratio_1": one / reference[k], "ratio_2": two / reference[k],
                "ratio_pooled": pooled / reference[k],
                "two_over_one": two / one if one else None}
            print(f"    {clone_source:<10} card-NAMES {one:.2%} ({one / reference[k]:.2f}x)"
                  f"   card-SILENT {two:.2%} ({two / reference[k]:.2f}x)"
                  f"   POOLED {pooled:.2%} ({pooled / reference[k]:.2f}x)"
                  f"   silent/names {two / one:.2f}x")

    print("""
READING, and every clause names its subpopulation:
  * CARD-SILENT beats CARD-NAMES at BOTH mixes, and the gap WIDENS with nA. That
    is the omission cost scaling with nA while the lie's does not — the mechanism
    the cap sweep suggested, which was untestable while carrier group and mix were
    locked together.
  * The CARD-SILENT half reaches PARITY with the disjoint template at nA=4 and
    ~0.9x at nA=1.
  * SIZE-3 AS A WHOLE, pooled over its true composition, is ~0.70-0.73x. `0.9x`
    and `parity` are CARRIER-2 figures and must not be quoted as size-3 figures.
""")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "matched_grid.json").write_text(json.dumps({
        "declares": {
            "baseline": "stale card",
            "belief_model": "whole card (D1)",
            "tie_break": "expectation over the believed-optimal set (D19)",
            "forced_class": "SUCCESSOR-UNIQUE, matching the five-class arm by "
                            "mechanism rather than by label (D51)",
        },
        "six_class": six,
        "reference_disjoint": reference,
        "ratios": ratios,
        "carrier_weights": CARRIER_WEIGHTS,
        "paired_cells": {n: len(v) for n, v in usable.items()},
        "dropped_cells": dropped,
        "caveats": [
            "the sixth class DOES NOT EXIST: copied risk weights, no BCBS "
            "transcription, kept off study paths by assert_no_synthetic_classes",
            "RATIOS ONLY — no sigma, and no figure here is an episodes/arm budget",
            "nA is REQUESTED via shared_class_segments and MEASURED per cell; the "
            "achieved distribution is printed because a forced parameter landing "
            "on one value in every cell is a constant reported as a variable",
            "a CEILING under exact optimal play; it does not say any manager "
            "realises it",
            "templates are a deterministic evenly spaced sample of each carrier "
            "group, not the full 6480, so group means are sample means",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"written: {out / 'matched_grid.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
