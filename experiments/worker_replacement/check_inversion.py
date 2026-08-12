"""Why does the TWO-carrier group price BELOW the one-carrier group?

THE OBSERVATION (step 4). Size-3 partial-overlap templates with two card-error
carriers price ~25% LOWER than those with one, under both clone sources. That is
backwards: the second carrier is the card's OMISSION, and adding an independent
source of card error should raise the ceiling.

FIRST, THE CONTRAST IS NOT WHAT ITS NAME SAYS. Proved over all 6480 admissible
partial templates, 0 counterexamples:

    carriers = 1  <=>  the successor-unique class IS the shared class
    carriers = 2  <=>  the successor-unique class is one the card never mentions

Forced, not incidental: the successor-unique class is in w1 by definition, and if
it is also in w0 it lies in w0 & w1, which every admissible partial template has of
size exactly one. So no sampling design separates the two properties.

TWO HYPOTHESES (LS), each with a stated falsifier, and this module runs both.

  H1 CAPACITY SATURATION — two silent sole-held classes make more segments require
     the successor, cap binds, the ORACLE already pays the penalty and the gap to
     card-believing play compresses.
     Falsified if: raising cap does not remove the inversion.

  H2 DENOMINATOR ARTEFACT — ceiling SHARE divides by oracle; a larger oracle on
     two-carrier templates gives the same absolute loss a smaller share.
     Falsified if: ABSOLUTE ceilings invert the same way.

Run:  python3 -m experiments.worker_replacement.check_inversion
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc
from .check_size3_pricing import (CLONE_SOURCES, SEEDS, build_size3,
                                  size3_templates, successor_unique)

HERE = Path(__file__).resolve().parent
CAPS = (3, 4, 5, 9)      # 9 segments over 3 workers, so cap 9 is NO constraint


def usable_cells() -> dict[int, list[tuple[Any, int]]]:
    """Cells that generate under BOTH clone sources — the paired population."""
    return {n: [(t, s) for t in templates for s in SEEDS
                if all(build_size3(t, c, s) is not None for c in CLONE_SOURCES)]
            for n, templates in size3_templates().items()}


def main() -> int:
    print("The two-carrier inversion: testing H1 (capacity) and H2 (denominator)\n")
    cells = usable_cells()
    results: dict[str, Any] = {}

    # --- H2: absolute ceilings ------------------------------------------------
    print("H2 — DENOMINATOR ARTEFACT. If the inversion is the oracle in the")
    print("denominator, ABSOLUTE ceilings should not invert:")
    print(f"{'clone':<11} {'carriers':>9} {'share':>8} {'absolute':>10} {'oracle':>9}")
    absolute: dict[str, Any] = {}
    for source in CLONE_SOURCES:
        for n_carriers, pairs in cells.items():
            out = [sc.ceiling_vs_stale_card(build_size3(t, source, s), cap=3)
                   for t, s in pairs]
            row = {"share": st.mean(o["ceiling_share"] or 0.0 for o in out),
                   "absolute": st.mean(o["ceiling"] for o in out),
                   "oracle": st.mean(o["oracle"] for o in out)}
            absolute[f"{source}|{n_carriers}"] = row
            print(f"{source:<11} {n_carriers:>9} {row['share']:>7.2%} "
                  f"{row['absolute']:>10.4f} {row['oracle']:>9.4f}")
    h2_dead = all(
        absolute[f"{s}|2"]["absolute"] < absolute[f"{s}|1"]["absolute"]
        for s in CLONE_SOURCES)
    print(f"\n   -> H2 {'FALSIFIED' if h2_dead else 'SURVIVES'}: absolute ceilings "
          f"{'invert the same way' if h2_dead else 'do not invert'}")
    results["h2"] = {"by_group": absolute, "falsified": h2_dead}

    # --- H1: cap sweep --------------------------------------------------------
    print("\nH1 — CAPACITY SATURATION. If cap binding compresses the two-carrier")
    print("gap, the inversion should weaken or reverse as cap rises:")
    print(f"{'cap':>4} {'clone':<11} {'1 carrier':>11} {'2 carriers':>11} {'inverted':>9}")
    sweep: dict[str, Any] = {}
    for cap in CAPS:
        for source in CLONE_SOURCES:
            means = {
                n: st.mean(
                    sc.ceiling_vs_stale_card(build_size3(t, source, s),
                                             cap=cap)["ceiling_share"] or 0.0
                    for t, s in pairs)
                for n, pairs in cells.items()}
            inverted = means[2] < means[1]
            sweep[f"cap{cap}|{source}"] = {
                "one_carrier": means[1], "two_carriers": means[2],
                "inverted": inverted, "gap": means[1] - means[2]}
            print(f"{cap:>4} {source:<11} {means[1]:>10.2%} {means[2]:>10.2%} "
                  f"{'YES' if inverted else 'no':>9}")
    h1_dead = all(v["inverted"] for v in sweep.values())
    print(f"\n   -> H1 {'FALSIFIED' if h1_dead else 'SURVIVES'}: the inversion "
          f"{'persists at every cap, including cap=9 (no constraint at all)' if h1_dead else 'clears when cap is relaxed'}")
    results["h1"] = {"sweep": sweep, "falsified": h1_dead}

    # --- what the sweep shows instead -----------------------------------------
    print("\nWHAT THE SWEEP SHOWS INSTEAD, and it was not either hypothesis.")
    print("The TWO-carrier group is FLAT in cap; the ONE-carrier group RISES:")
    for source in CLONE_SOURCES:
        one = [sweep[f"cap{c}|{source}"]["one_carrier"] for c in CAPS]
        two = [sweep[f"cap{c}|{source}"]["two_carriers"] for c in CAPS]
        print(f"   {source:<10} 1 carrier: {' -> '.join(f'{v:.2%}' for v in one)}")
        print(f"   {'':<10} 2 carriers: {' -> '.join(f'{v:.2%}' for v in two)}")
    print("""
So capacity is not compressing the two-carrier group; it is AMPLIFYING the
one-carrier group. Reading the confound with that:

  * ONE carrier — the successor-unique class IS the shared class, which the card
    CLAIMS correctly. The manager believes the successor serves three classes and
    piles segments onto it up to cap; two of those claims are false, so the loss
    SCALES WITH CAP. Relax cap and it over-assigns more.
  * TWO carriers — the successor's required class is one the card never mentions.
    That loss is the un-routed omitted class, which at nA=1 is ONE segment, and it
    is capacity-INDEPENDENT. Hence flat.

PREDICTION THIS MAKES, AND IT IS TESTABLE: the omission cost scales with nA while
the lie's capacity amplification does not, so THE INVERSION SHOULD REVERSE AT
HIGHER nA. Every size-3 cell here is nA=1 — not because six classes forbid more,
but because `shared_class_segments` forcing is disabled on the coverage_override
path (`shared_class = ... if coverage_override is None else None`), which is the
only path that can generate six classes. So the regime that would test this has
not been built, and 'size 3 is weaker' is established ONLY at nA=1.
""")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "inversion_diagnosis.json").write_text(json.dumps({
        "results": results,
        "both_falsified": h1_dead and h2_dead,
        "caps": list(CAPS),
        "caveats": [
            "every cell here is nA=1; the mix forcing that produced nA=4 at five "
            "classes is DISABLED on the coverage_override path, so this says "
            "nothing about size-3 at a forced mix",
            "the carrier contrast is confounded by construction with whether the "
            "successor-unique class is the shared one (6480 templates, 0 "
            "counterexamples), so neither variable is isolated here",
            "a mechanism consistent with the sweep is not a mechanism demonstrated "
            "by it",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"written: {out / 'inversion_diagnosis.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
