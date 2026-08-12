"""L9 step 4 — pricing size-3 PARTIAL-OVERLAP lattices against the size-2 disjoint one.

WHAT IS BEING DECIDED. Partial predecessor/successor overlap is the realistic
succession — an upgraded model, not a different specialist — and it is IMPOSSIBLE
at COVERAGE_SIZE=2 for any number of classes. At size 3 it needs a SIXTH asset
class, which at five classes is structurally empty (check_lattice_enumeration.py).
So the question is what the sixth class buys.

EVERY FIGURE HERE IS A RATIO, AND THAT IS DELIBERATE (D11). Absolute sigma figures
divide by the PRE-L1 measurement, which was ruled out for sizing anything, and an
absolute detectability verdict needs a post-L1 sigma that only L3 can give. Effect
RATIOS and their SQUARES (required-n scales as the square) never touch sigma at
all, so they are outside that dependency by construction rather than surviving it.
No figure here is an episodes/arm budget and none should be quoted as one.

THREE THINGS DECIDE A CEILING AND ALL THREE ARE DECLARED, because each was caught
silently deciding a number before it was declared:
  * BASELINE     — the stale card, not an ignorant manager;
  * BELIEF MODEL — the card as a REPLACEMENT description, so its OMISSION costs
                   as well as its LIE (D1);
  * TIE-BREAK    — expectation over the believed-optimal set, which is NOT an
                   upper bound, so the [min, max] interval travels with it (D19).

TWO STRATIFICATIONS, NEITHER OPTIONAL:
  * CARRIER COUNT (RR). Every admissible template has a LIE carrier; 4320 of 6480
    also have an OMISSION carrier — a class the card is silent about that the
    successor sole-holds. 2160 have only the lie and structurally resemble the
    CURRENT, undetectable template. A pooled "size 3" headline averages the two
    groups and is the nA artefact arriving by a different door.
  * MIX (nA), the IRB-applicable segments in the successor-unique class. A
    template does not have an effect size; a template AND a mix do.

THE CLONE IS BRACKETED, NOT CHOSEN (D13). The sixth class has the economics of an
existing one, so the price isolates the LATTICE. It inherits its source's SA/IRB
divergence exactly, and that varies by class — so the whole comparison is run
under `corporate` (low divergence) and `mdb` (high), and both are reported. Every
figure names its clone source.

WHAT THIS CANNOT ESTABLISH. The sixth class does not exist. Its weights are copied
and carry no BCBS transcription, and `assert_no_synthetic_classes` keeps it off
study paths. The clone also MANUFACTURES INDIFFERENCE: identical economics create
exact ties, whose effect on the ceiling the D19 tie-break makes deterministic but
whose SIGN is not known (check_tie_rate.py). So these are lattice comparisons, two
removes from anything the study measures, and are not effect sizes.

Run:  python3 -m experiments.worker_replacement.check_size3_pricing
"""

from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from itertools import combinations, permutations
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc
from .check_lattice_enumeration import admissible, omission_carriers
from .check_template_pricing import labels_of

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(10)
TEMPLATES_PER_GROUP = 12
CLONE_SOURCES = ("corporate", "mdb")
DISJOINT_SIZE2 = ("de", "ab", "ce", "cb")


def size3_templates() -> dict[int, list[tuple[frozenset[str], ...]]]:
    """Admissible six-class size-3 partial-overlap templates, by carrier count.

    Deterministic sampling: the admissible set is sorted into a canonical order and
    evenly spaced picks are taken. No RNG, so the sample cannot be re-rolled until
    it looks better, and it is reproducible without recording a draw seed.
    """
    classes = tuple("abcdef")
    subsets = [frozenset(s) for s in combinations(classes, 3)]
    by_carriers: dict[int, list[Any]] = defaultdict(list)
    for template in permutations(subsets, 4):
        if not admissible(template, classes) or not (template[0] & template[1]):
            continue
        by_carriers[1 + omission_carriers(template, classes)].append(template)
    out = {}
    for n_carriers, pool in by_carriers.items():
        pool.sort(key=lambda t: tuple("".join(sorted(s)) for s in t))
        step = max(1, len(pool) // TEMPLATES_PER_GROUP)
        out[n_carriers] = pool[::step][:TEMPLATES_PER_GROUP]
    return dict(sorted(out.items()))


def successor_unique(template) -> str:
    w1, w2, w3 = set(template[1]), set(template[2]), set(template[3])
    unique = sorted(w1 - w2 - w3)
    if len(unique) != 1:
        raise ValueError(f"{template} has {len(unique)} successor-unique classes")
    return unique[0]


def build_size3(template, clone_source: str, seed: int) -> dict[str, Any] | None:
    """Generate one six-class instance, or None if the generator refuses it.

    ASSERTION 4 (both rosters serviceable) fires on a few cells: at six classes a
    segment can land in the uncovered class with an SA fallback so wrong it scores
    zero for EVERY post-swap worker, which makes the segment worthless to the whole
    roster. That is the generator correctly refusing an instance, not a bug here.
    """
    clone = gen.register_synthetic_clone(f"{clone_source}_clone", clone_source)
    real = gen.ASSET_CLASSES + (clone,)
    label_map = dict(zip("abcdef", real))
    coverage = [tuple(label_map[c] for c in sorted(s)) for s in template]
    try:
        return gen.generate(seed, coverage_override=coverage, asset_classes=real)
    except gen.InstanceAssertionError:
        return None


def price_size3(template, clone_source: str, seed: int) -> dict[str, Any]:
    """One (template, clone source, seed) cell, on a GENERATED six-class instance."""
    clone = f"{clone_source}_clone"
    label_map = dict(zip("abcdef", gen.ASSET_CLASSES + (clone,)))
    instance = build_size3(template, clone_source, seed)
    out = sc.ceiling_vs_stale_card(instance, cap=CAP)
    unique_class = label_map[successor_unique(template)]
    n_a = sum(1 for sg in instance["segments"]
              if sg["irb_approved"] and sg["asset_class"] == unique_class)
    return {"share": out["ceiling_share"] or 0.0, "n_a": n_a,
            "share_min": out["ceiling_share_min"] or 0.0,
            "share_max": out["ceiling_share_max"] or 0.0,
            "n_believed_optima": out["n_believed_optima"]}


def price_disjoint_size2() -> dict[int, list[float]]:
    """The REFERENCE: the size-2 disjoint template, by nA, over all 120 labelings.

    Priced through the same shipped `ceiling_vs_stale_card` as the size-3 cells, so
    the comparison is not between two implementations.
    """
    by_na: dict[int, list[float]] = defaultdict(list)
    unique = successor_unique(tuple(frozenset(s) for s in DISJOINT_SIZE2))
    for seed in SEEDS:
        base = gen.generate(seed)
        lab = labels_of(base)
        roles = ["_pred", "_succ", "_w2", "_w3"]
        for labeling in permutations(gen.ASSET_CLASSES):
            label_map = dict(zip("abcde", labeling))
            workers = []
            for worker in base["workers"]:
                row = dict(worker)
                for role, spec in zip(roles, DISJOINT_SIZE2):
                    if worker["worker_id"] == lab[role]:
                        cover = tuple(label_map[c] for c in spec)
                        row["irb_coverage"] = cover
                        row["private_pd_calibration"] = {
                            c: base["class_calibration"][c] for c in cover}
                workers.append(row)
            instance = {**base, "workers": workers}
            n_a = sum(1 for sg in base["segments"]
                      if sg["irb_approved"]
                      and sg["asset_class"] == label_map[unique])
            by_na[n_a].append(
                sc.ceiling_vs_stale_card(instance, cap=CAP)["ceiling_share"] or 0.0)
    return dict(sorted(by_na.items()))


def main() -> int:
    print("L9 step 4 — size-3 partial overlap vs the size-2 disjoint reference")
    print("baseline: stale card | belief: whole card (D1) | tie-break: "
          "expectation (D19)\n")

    reference = price_disjoint_size2()
    ref_pooled = st.mean([v for vs in reference.values() for v in vs])
    print("REFERENCE — size-2 disjoint, five classes, by mix:")
    for n_a, shares in reference.items():
        print(f"   nA={n_a}  n={len(shares):>4}  mean ceiling share {st.mean(shares):.2%}")
    print(f"   pooled over all 120 labelings: {ref_pooled:.2%}\n")

    groups = size3_templates()

    # PAIRED EXCLUSION. A few cells fail ASSERTION 4, and they fail under ONE clone
    # source and not the other — so dropping each arm's own failures would compare
    # the two arms on DIFFERENT populations, and the clone bracket is exactly the
    # comparison that would corrupt. Only cells that generate under BOTH sources
    # are priced, under both.
    usable: dict[int, list[tuple[Any, int]]] = {}
    dropped: dict[int, int] = {}
    for n_carriers, templates in groups.items():
        keep, drop = [], 0
        for template in templates:
            for seed in SEEDS:
                if all(build_size3(template, c, seed) is not None
                       for c in CLONE_SOURCES):
                    keep.append((template, seed))
                else:
                    drop += 1
        usable[n_carriers], dropped[n_carriers] = keep, drop
    total_drop = sum(dropped.values())
    total_cells = sum(len(v) for v in usable.values()) + total_drop
    print(f"PAIRED EXCLUSION: {total_drop} of {total_cells} (template, seed) cells "
          f"fail the generator's")
    print("serviceability assertion under at least one clone source and are dropped")
    print("from BOTH arms, so the bracket compares the same population.\n")

    results: dict[str, Any] = {}
    print("SIZE 3, SIX CLASSES — by clone source and carrier count:")
    print(f"{'clone':<12} {'carriers':>9} {'cells':>6} {'mean share':>11} "
          f"{'by mix (nA: mean)':>34}")
    for clone_source in CLONE_SOURCES:
        for n_carriers in groups:
            rows = [price_size3(t, clone_source, s)
                    for t, s in usable[n_carriers]]
            shares = [r["share"] for r in rows]
            by_na: dict[int, list[float]] = defaultdict(list)
            for r in rows:
                by_na[r["n_a"]].append(r["share"])
            mix_txt = "  ".join(f"{k}:{st.mean(v):.2%}" for k, v in sorted(by_na.items()))
            key = f"{clone_source}|{n_carriers}"
            results[key] = {
                "clone_source": clone_source, "n_carriers": n_carriers,
                "cells": len(rows), "mean_share": st.mean(shares),
                "by_n_a": {k: {"n": len(v), "mean_share": st.mean(v)}
                           for k, v in sorted(by_na.items())},
                "mean_believed_optima": st.mean(r["n_believed_optima"] for r in rows),
                "interval_mean_width": st.mean(
                    r["share_max"] - r["share_min"] for r in rows),
            }
            print(f"{clone_source:<12} {n_carriers:>9} {len(rows):>6} "
                  f"{st.mean(shares):>10.2%} {mix_txt:>34}")

    # --- RATIOS, which is what survives having no post-L1 sigma -----------------
    print("\nEFFECT RATIO to the size-2 disjoint reference at MATCHED MIX, and its")
    print("SQUARE (required n scales as the square). No sigma appears in either.")
    print(f"{'clone':<12} {'carriers':>9} {'nA':>4} {'ratio':>8} {'ratio^2':>9}")
    ratios: dict[str, Any] = {}
    for key, row in results.items():
        for n_a, cell in row["by_n_a"].items():
            if n_a not in reference:
                continue
            ref = st.mean(reference[n_a])
            if ref <= 0:
                continue
            ratio = cell["mean_share"] / ref
            ratios[f"{key}|nA={n_a}"] = {"ratio": ratio, "ratio_squared": ratio ** 2,
                                         "n_a": n_a, "reference_share": ref}
            print(f"{row['clone_source']:<12} {row['n_carriers']:>9} {n_a:>4} "
                  f"{ratio:>7.2f}x {ratio ** 2:>8.1f}x")

    clone_bracket = {}
    for n_carriers in groups:
        vals = [results[f"{c}|{n_carriers}"]["mean_share"] for c in CLONE_SOURCES]
        clone_bracket[n_carriers] = {"min": min(vals), "max": max(vals),
                                     "spread_factor": max(vals) / min(vals) if min(vals) else None}
    print("\nCLONE BRACKET — the sixth class's economics are a COPY, and which class")
    print("was copied moves the answer. Reported as an interval, never a point:")
    for n_carriers, band in clone_bracket.items():
        print(f"   {n_carriers} carrier(s): {band['min']:.2%} - {band['max']:.2%}")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "size3_pricing.json").write_text(json.dumps({
        "declares": {
            "baseline": "stale card",
            "belief_model": "whole card — the OMISSION costs as well as the LIE (D1)",
            "tie_break": "expectation over the believed-optimal set; NOT an upper "
                         "bound, so intervals travel with it (D19)",
        },
        "reference_size2_disjoint_by_n_a": {
            k: {"n": len(v), "mean_share": st.mean(v)} for k, v in reference.items()},
        "reference_pooled_mean_share": ref_pooled,
        "size3_results": results,
        "effect_ratios": ratios,
        "clone_bracket": clone_bracket,
        "templates_per_group": TEMPLATES_PER_GROUP,
        "paired_exclusion": {"dropped_cells_by_carrier": dropped,
                             "total_dropped": total_drop,
                             "total_cells": total_cells},
        "seeds": list(SEEDS),
        "caveats": [
            "RATIOS ONLY. No sigma appears anywhere and no figure here is an "
            "episodes/arm budget. An absolute detectability verdict needs a "
            "post-L1 sigma, which only L3 can supply (D11).",
            "the sixth class DOES NOT EXIST: its risk weights are copied from an "
            "existing class and carry no BCBS transcription",
            "the clone MANUFACTURES INDIFFERENCE — identical economics create exact "
            "ties. D19 makes the ceiling deterministic across them; the SIGN of "
            "their effect on the level is not known and is not asserted",
            "templates are an evenly spaced deterministic sample of each carrier "
            "group, not the full 6480, so group means are sample means",
            "a CEILING under exact optimal play; it does not say any manager "
            "realises it",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'size3_pricing.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
