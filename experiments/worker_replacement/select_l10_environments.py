"""The L10 environment draw — researcher-approved rule, 2026-08-09.

Supersedes `records/R2/instance_selection_partial_segs1.json`, which was a valid
stratification of a population the study does not ship: it was drawn at a cell with
`generate()`'s defaults (irb_frac 0.67, both amplifiers True) and, re-measured at the
settled cell, its intended low/mid/high became low/LOW/high.

THE RULE, as approved:

    1  pool     admitted at the settled cell, SEED RANGE STATED
    2  floor    ceiling >= pool median
    3  usable   sole-need classes with MORE THAN ONE candidate above the floor
    4  draw     two DISTINCT classes at random from the usable set,
                draw seed fixed and recorded BEFORE the draw
    5  pick     within each drawn class, the largest ceiling above the floor
    6  assert   the two differ on class; each class had >1 candidate

WHY THE AXIS IS ASSET CLASS AND NOT GAP SIZE. The sensitivity ladder was retired
because `card - ignorant` falls monotonically as the ceiling rises ACROSS
arrangements, so ordering instances by gap ranks manager policies. Selecting on
structure sidesteps that rather than stratifying around it. Measured within `partial`
at the settled cell the coupling is absent (r = -0.137 LS / -0.016 RE / +0.094 RR,
all indistinguishable from zero), so the FLOOR does not reintroduce it -- but the
floor is a threshold, never a ranking, and the classes are fixed before magnitude is
consulted so the rule cannot drift toward "pick the two biggest".

Zero model calls. Run:

    python -m experiments.worker_replacement.select_l10_environments
"""

from __future__ import annotations

import json
import random
import statistics as st
from pathlib import Path
from typing import Any

from . import finance_admission as adm
from . import finance_generator as gen
from . import finance_scorer as sc
from .check_l10_properties import CAP, SHIPPED, successor_unique_class

#: Fixed and recorded BEFORE the draw, so the draw cannot be re-rolled toward a
#: preferred outcome. The predecessor record used 20260807 for the same reason.
DRAW_SEED = 20260809

SUITE = range(60)
OUT = Path(__file__).resolve().parent / "records/L10/environment_selection_v1.json"


def pool() -> list[dict[str, Any]]:
    rows = []
    for seed in SUITE:
        try:
            if not adm.admit(seed, **SHIPPED)["admitted"]:
                continue
            inst = gen.generate(seed, **SHIPPED)
        except (gen.InstanceAssertionError, ValueError):
            continue
        rows.append({
            "seed": seed,
            "ceiling_share": sc.ceiling_vs_stale_card(inst, cap=CAP)["ceiling_share"] or 0.0,
            "sole_need_class": successor_unique_class(inst),
        })
    return rows


def main() -> int:
    rows = pool()
    if not rows:
        raise SystemExit("empty pool -- refusing to draw")
    ceilings = sorted(r["ceiling_share"] for r in rows)
    floor = st.median(ceilings)
    above = [r for r in rows if r["ceiling_share"] >= floor]

    by_class: dict[str, list[dict[str, Any]]] = {}
    for r in above:
        by_class.setdefault(r["sole_need_class"], []).append(r)
    usable = sorted(c for c, v in by_class.items() if len(v) > 1)

    print(f"pool: {len(rows)} admitted over seeds {SUITE.start}-{SUITE.stop - 1}")
    print(f"floor (pool median): {floor * 100:.2f}%   {len(above)} at or above\n")
    print("  class        above floor   usable (>1)?")
    for cls in sorted(by_class, key=lambda c: -len(by_class[c])):
        n = len(by_class[cls])
        print(f"  {cls:<12} {n:>11}   {'yes' if n > 1 else 'NO -- only one candidate'}")
    if len(usable) < 2:
        raise SystemExit(f"only {len(usable)} usable class(es) -- the rule cannot be satisfied")

    # THE DRAW. Seeded and printed, so it is reproducible and was not re-rolled.
    rng = random.Random(DRAW_SEED)
    drawn = sorted(rng.sample(usable, 2))
    chosen = [max(by_class[c], key=lambda r: r["ceiling_share"]) for c in drawn]

    print(f"\n  usable classes: {usable}")
    print(f"  draw seed {DRAW_SEED} (fixed before the draw) -> classes {drawn}\n")
    print("  chosen  seed  class        ceiling   candidates in class")
    for c, r in zip(drawn, chosen):
        print(f"          {r['seed']:>4}  {c:<12} {r['ceiling_share'] * 100:>6.2f}%"
              f"   {len(by_class[c])}")

    # (6) ASSERTED, not hoped for.
    assert chosen[0]["sole_need_class"] != chosen[1]["sole_need_class"], \
        "the two environments share a sole-need class"
    for c in drawn:
        assert len(by_class[c]) > 1, f"class {c} had only one candidate above the floor"
    assert all(r["ceiling_share"] >= floor for r in chosen), "a chosen instance is below the floor"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "rule": "structure decides WHICH TWO (sole-need asset class); magnitude decides "
                "WHICH INSTANCE of each. Classes fixed before magnitude is consulted.",
        "approved_by": "researcher, 2026-08-09",
        "supersedes": "records/R2/instance_selection_partial_segs1.json — drawn at a cell "
                      "the study does not ship; its low/mid/high became low/LOW/high when "
                      "re-measured at the settled cell",
        "setting": SHIPPED, "cap": CAP,
        "suite_seeds": [SUITE.start, SUITE.stop - 1],
        "n_admitted": len(rows),
        "floor_rule": "pool median of ceiling_share",
        "floor_value": floor,
        "n_above_floor": len(above),
        "candidates_per_class_above_floor": {c: len(v) for c, v in sorted(by_class.items())},
        "usable_classes": usable,
        "draw_seed": DRAW_SEED,
        "draw_seed_fixed_before_draw": True,
        "drawn_classes": drawn,
        "chosen": chosen,
        "recorded_before_any_episode": True,
        "does_not_establish":
            "anything about effect size. The floor is a threshold, never a ranking, and "
            "two instances differing on ONE structural axis is a weak generalisation "
            "claim however they are chosen — a limitation of the two-environment design "
            "(RE), carried to the researcher when the rule was approved.",
        "pool": rows,
    }, indent=1, default=str) + "\n")
    print(f"\n  written: {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
