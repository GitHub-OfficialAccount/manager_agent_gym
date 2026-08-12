"""Is the CARD channel inert by construction? — the capacity path LS asked RR about.

LS's L4 finding: across 60 generator seeds the class the stale card LIES about is
always one nobody covers, and the class it is SILENT about is always one an
incumbent also covers — so **no segment exists where knowing the successor's true
coverage yields a better ASSIGNEE.** If that made the card inert, L3 would be
measuring contrasts across cells whose channels cannot move the DV.

THE COVERAGE STRUCTURE REPRODUCES EXACTLY. 60/60 instances, always exactly one
lied-about and one silent-about class, lied-about covered by nobody else,
silent-about covered by an incumbent. Zero counterexamples.

**BUT THE CONCLUSION DOES NOT FOLLOW, BECAUSE CAPACITY BINDS EXACTLY.** Nine
segments, three workers, C=3: every slot is spoken for. Believing the card, the
manager spends a SUCCESSOR SLOT on the lied-about segment — worth the same to
everybody, since nobody covers it — and that displaces a segment the successor
genuinely covers onto a worse worker. The loss is not a coverage mistake on the
lied segment; it is the DISPLACEMENT the wasted slot causes.

Worked, seed 3 (successor `w_e350ed`, lied-about class `mdb`):

    seg_07 (mdb, IRB)   TRUE -> w_6aaa50      CARD -> w_e350ed   the wasted slot
    seg_03 (bank, IRB)  TRUE -> w_e350ed      CARD -> w_552723   displaced
    seg_04 (sovereign)  TRUE -> w_552723      CARD -> w_6aaa50   cascade

Successor slot count is 3 under both. **The card does not change how much the
successor does; it changes WHICH work it does, and under an exactly-binding cap
that is enough.**

WHAT THIS MEASURES: a CEILING. Optimal play under the truth minus optimal play
under the card, scored in the true world. It establishes the channel is not inert
BY CONSTRUCTION. It does not establish that any manager realises it — a real
manager plays neither optimum, and the ceiling is an upper bound on what the
channel could be worth to a perfect user of it.

Run:  python3 -m experiments.worker_replacement.check_card_ceiling
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any, Callable

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
CAP = 3
STUDY_SEEDS = (3, 23, 36)


def card_ceiling(seed: int) -> dict[str, Any]:
    """Optimal play under the truth vs optimal play under the STALE CARD.

    ONE DEFINITION, in the scorer. This script used to carry its own enumeration;
    a second copy of a quantity is how this project got two ceilings that ranked
    instances differently. Verified identical to the previous local version on 12
    seeds before the switch.
    """
    instance = gen.generate(seed)
    out = sc.ceiling_vs_stale_card(instance, cap=CAP)
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    event = instance["event"]
    return {
        "seed": seed,
        "true_optimum": out["oracle"],
        "card_believing_play_realises": out["card_believing_play_realises"],
        "ceiling": out["ceiling"],
        "ceiling_share_of_oracle": out["ceiling_share"],
        "allocation_differs": out["allocation_differs"],
        "lied_about_class": sorted(
            set(by_id[event["predecessor_id"]]["irb_coverage"])
            - set(by_id[event["successor_id"]]["irb_coverage"])),
        "silent_about_class": sorted(
            set(by_id[event["successor_id"]]["irb_coverage"])
            - set(by_id[event["predecessor_id"]]["irb_coverage"])),
    }

def main() -> int:
    print("Is the CARD channel inert by construction? — the CAPACITY path\n")

    print("1. the coverage structure LS found, re-derived (60 seeds)")
    lied_sole = silent_shared = instances = 0
    for seed in range(60):
        instance = gen.generate(seed)
        event = instance["event"]
        cover = {w["worker_id"]: set(w["irb_coverage"])
                 for w in instance["workers"]}
        pre, suc = event["predecessor_id"], event["successor_id"]
        others = set().union(*[cover[w] for w in event["roster_post_swap"]
                               if w != suc])
        instances += 1
        lied_sole += all(c not in others for c in cover[pre] - cover[suc])
        silent_shared += all(c in others for c in cover[suc] - cover[pre])
    print(f"   {lied_sole}/{instances} — the LIED-about class is covered by nobody else")
    print(f"   {silent_shared}/{instances} — the SILENT-about class IS covered by "
          f"an incumbent")
    print("   => on COVERAGE alone, knowing the truth never yields a better "
          "assignee. LS's structure holds.")

    print("\n2. but capacity binds EXACTLY (9 segments, 3 workers, C=3), so the "
          "wasted\n   slot displaces work the successor genuinely covers")
    rows = [card_ceiling(seed) for seed in range(30)]
    moved = [r for r in rows if r["allocation_differs"]]
    costly = [r for r in rows if r["ceiling"] > 1e-9]
    mean = sum(r["ceiling"] for r in rows) / len(rows)
    print(f"   believing the card CHANGES the optimal allocation in "
          f"{len(moved)}/{len(rows)} instances")
    print(f"   ...and COSTS score in {len(costly)}/{len(rows)}")
    print(f"   mean ceiling {mean:.4f}  max {max(r['ceiling'] for r in rows):.4f}"
          f"  ({mean / (sum(r['true_optimum'] for r in rows) / len(rows)):.2%} of "
          f"the oracle)")
    print("   => the card channel is NOT inert by construction. It moves "
          "allocation through\n      CAPACITY DISPLACEMENT rather than through "
          "coverage.")

    print("\n3. AND THE PART THAT DECIDES L3 — the three instances the study "
          "actually uses")
    study = [card_ceiling(seed) for seed in STUDY_SEEDS]
    for row in study:
        print(f"   seed {row['seed']:>3}: ceiling {row['ceiling']:.4f} "
              f"({row['ceiling_share_of_oracle']:.2%} of oracle)"
              f"{'' if row['ceiling'] > 1e-9 else '   <-- EXACTLY ZERO'}")
    zero = [r for r in study if r["ceiling"] <= 1e-9]
    print(f"   {len(zero)} of {len(study)} selected instances have a card ceiling "
          f"of EXACTLY ZERO.")
    print("   So the inertness claim is FALSE of the generator and TRUE of most of\n"
          "   the SELECTED SET — which is a selection property, and therefore "
          "fixable\n   by the instance-selection rule rather than fatal to the "
          "design.")

    out = HERE / "records" / "L4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "card_ceiling.json").write_text(json.dumps({
        "establishes": ("the card channel is not inert by construction; it moves "
                        "allocation via capacity displacement under an "
                        "exactly-binding cap"),
        "does_not_establish": ("that any manager realises this — the ceiling is "
                               "optimal-play-under-truth minus "
                               "optimal-play-under-card, an upper bound"),
        "coverage_structure_holds": {"n": instances, "lied_sole": lied_sole,
                                     "silent_shared": silent_shared},
        "sweep_30_seeds": rows,
        "study_instances": study,
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'card_ceiling.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
