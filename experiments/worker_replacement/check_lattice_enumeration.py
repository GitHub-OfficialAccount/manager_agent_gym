"""Enumerating admissible lattice templates over (n_classes x coverage_size).

WHY THIS EXISTS. The claim "partial overlap costs a SIXTH ASSET CLASS" is carried
in a print statement in `check_template_pricing.py` with no enumeration behind it,
and the cell that would make the sixth class unnecessary — COVERAGE_SIZE=3 at FIVE
classes — was never enumerated. A sixth asset class is not free: `SA_TABLES` has
four entries for five classes already (retail has none), so a sixth needs either
transcribed BCBS weights or a documented zero-SA-fallback. That is a real cost
being quoted from an unchecked premise, so it is checked here.

THE PREDICATE. Taken from `_lattice_from_template`'s four stated properties, with
ONE GENERALISATION and ONE ADDITION, both marked below. Roles are DECLARED
positionally (w0=predecessor, w1=successor, w2, w3), never derived from coverage.

  P1  four distinct equal-size subsets            -> non-nested by construction
  P2' the successor is the ONLY post-swap holder of some class
  P3  some class is held by the predecessor ALONE -> post-swap uncovered
  P4  every class has a holder in the pool        -> no dead class
  P5  some LIED class is covered by exactly one incumbent

P2 IS GENERALISED, AND THE ORIGINAL WOULD HAVE DECIDED THE ANSWER BY ITSELF.
`_lattice_from_template` states it as "class A has exactly two holders, the swap
pair". That phrasing PRESUMES a shared class, so a disjoint template fails it
definitionally — enumerating under it would return "disjoint is inadmissible"
as a fact about the requirement rather than about the lattice. What O3 actually
needs is that the successor be strictly required post-swap, which a
successor-ONLY class satisfies just as well as a shared one. P2' is that.

P5 IS NEW — it is the property the L9 proposal adds, not one the current template
has. Under the current lattice the card's lie is pure DISPLACEMENT: the lied class
is the sole-held one, so the manager mis-routes but loses nothing it could have
had. P5 asks the lie to cost COVERAGE, which needs a lied class someone else still
covers. It is what forces the predecessor to have two non-shared slots, and it is
therefore the whole reason coverage size 2 is tight.

Run:  python3 -m experiments.worker_replacement.check_lattice_enumeration
"""

from __future__ import annotations

import json
from itertools import combinations, permutations
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def admissible(template: tuple[frozenset[str], ...], classes: tuple[str, ...]) -> bool:
    """The five properties, evaluated on ONE positional role assignment."""
    w0, w1, w2, w3 = template
    post = (w1, w2, w3)

    # P1 — distinct (equal size is guaranteed by construction of the candidates)
    if len({w0, w1, w2, w3}) != 4:
        return False
    # P4 — every class has a holder somewhere in the pool
    if set().union(w0, w1, w2, w3) != set(classes):
        return False
    # P2' — the successor is the sole post-swap holder of something
    if not any(c in w1 and c not in w2 and c not in w3 for c in classes):
        return False
    # P3 — the predecessor holds something nobody post-swap holds
    if not any(c in w0 and not any(c in w for w in post) for c in classes):
        return False
    # P5 — a LIED class (predecessor's, not the successor's) covered by exactly one
    #      incumbent. Not `>= 1`: at exactly one the lie removes the only remaining
    #      holder, which is what makes it a coverage error rather than displacement.
    if not any(
        c in w0 and c not in w1 and sum(c in w for w in (w2, w3)) == 1
        for c in classes
    ):
        return False
    return True


def omission_carriers(template: tuple[frozenset[str], ...],
                      classes: tuple[str, ...]) -> int:
    """Classes the card is SILENT about that the successor SOLE-HOLDS post-swap.

    THE SECOND CARRIER, and it is the one the shipped belief model cannot see.
    Every admissible template has exactly one LIE carrier (P5, a lied class with
    one remaining coverer). Whether it has a second depends on whether the
    successor sole-holds something the predecessor's card never mentioned — and
    `finance_scorer.ceiling_vs_stale_card` falls through to the TRUE score exactly
    there, so it prices this carrier at ZERO (see check_card_belief_model.py).

    Consequence for the choice: pricing the size-3 pool with the shipped model
    would score every two-carrier template as though it were single-carrier, which
    collapses this stratification by construction rather than by measurement.
    """
    w0, w1, w2, w3 = template
    return sum(1 for c in classes
               if c in w1 and c not in w0 and c not in w2 and c not in w3)


def enumerate_cell(n_classes: int, coverage_size: int) -> dict[str, Any]:
    classes = tuple("abcdefg"[:n_classes])
    subsets = [frozenset(s) for s in combinations(classes, coverage_size)]
    disjoint, partial = [], []
    carriers: dict[int, int] = {}
    for template in permutations(subsets, 4):
        if not admissible(template, classes):
            continue
        overlap = len(template[0] & template[1])
        (partial if overlap else disjoint).append(template)
        if overlap:
            n = 1 + omission_carriers(template, classes)
            carriers[n] = carriers.get(n, 0) + 1
    return {
        "partial_by_carrier_count": dict(sorted(carriers.items())),
        "n_classes": n_classes,
        "coverage_size": coverage_size,
        "n_subsets": len(subsets),
        "n_admissible": len(disjoint) + len(partial),
        "n_disjoint": len(disjoint),
        "n_partial_overlap": len(partial),
        "example_partial": ["".join(sorted(s)) for s in partial[0]] if partial else None,
        "example_disjoint": ["".join(sorted(s)) for s in disjoint[0]] if disjoint else None,
    }


def main() -> int:
    print("Admissible lattice templates by (n_classes x coverage_size)\n")
    print("P1 distinct  P2' successor uniquely required post-swap")
    print("P3 predecessor-sole-held  P4 no dead class  P5 lied class singly covered\n")
    print(f"{'classes':>8} {'size':>5} {'subsets':>8} {'admissible':>11} "
          f"{'disjoint':>9} {'partial':>8}")
    cells = []
    for n_classes in (5, 6, 7):
        for coverage_size in (2, 3):
            cell = enumerate_cell(n_classes, coverage_size)
            cells.append(cell)
            print(f"{n_classes:>8} {coverage_size:>5} {cell['n_subsets']:>8} "
                  f"{cell['n_admissible']:>11} {cell['n_disjoint']:>9} "
                  f"{cell['n_partial_overlap']:>8}")

    five_three = next(c for c in cells if c["n_classes"] == 5 and c["coverage_size"] == 3)
    print("\nTHE CELL THAT WAS NEVER ENUMERATED — five classes, coverage size 3:")
    if five_three["n_partial_overlap"]:
        print(f"   {five_three['n_partial_overlap']} partial-overlap templates.")
        print(f"   example: {five_three['example_partial']}")
        print("   PARTIAL OVERLAP DOES NOT COST A SIXTH ASSET CLASS. It costs a")
        print("   coverage-size change, which needs no new SA weights, no new PD")
        print("   floor and no new BCBS transcription — every class already exists.")
    else:
        print("   none — the sixth class is genuinely the price.")
        print("   Structurally, not by accident: three 3-subsets of the four")
        print("   remaining classes cover every one of them at least twice, so the")
        print("   successor can never be the sole post-swap holder and P2' fails")
        print("   for every template in the cell.")

    six_three = next(c for c in cells if c["n_classes"] == 6 and c["coverage_size"] == 3)
    print("\nCARRIER SPLIT — six classes, size 3, partial overlap "
          f"({six_three['n_partial_overlap']} templates):")
    for n_carriers, count in six_three["partial_by_carrier_count"].items():
        print(f"   {n_carriers} carrier(s): {count}")
    print("   The LIE carrier is present in every admissible template (P5). The")
    print("   second, where it exists, is the card's OMISSION — a class the")
    print("   successor sole-holds that the card never mentions. Pricing this pool")
    print("   with ceiling_vs_stale_card would score every two-carrier template as")
    print("   single-carrier, collapsing the split by construction.")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "lattice_enumeration.json").write_text(json.dumps({
        "cells": cells,
        "predicate": {
            "P1": "four distinct equal-size subsets",
            "P2prime": "successor is the sole post-swap holder of some class "
                       "(GENERALISED from '_lattice_from_template''s 'A has exactly "
                       "two holders', which presumes a shared class and would rule "
                       "disjoint templates out definitionally)",
            "P3": "some class held by the predecessor alone",
            "P4": "every class has a holder in the pool",
            "P5": "some lied class is covered by exactly one incumbent (NEW — the "
                  "property the L9 proposal adds; the current template does not "
                  "have it)",
        },
        "caveats": [
            "ADMISSIBILITY IS NOT A CEILING. These counts say a template satisfies "
            "the five structural properties, NOT that its card channel is "
            "detectable. Every count here must be priced before it means anything.",
            "roles are DECLARED positionally; the generator's _designate_swap_pair "
            "derives them instead and is NOT on the template path",
            "P5 is imposed on all cells including coverage size 2, so the size-2 "
            "counts are not the counts for the CURRENT lattice, which lacks P5",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'lattice_enumeration.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
