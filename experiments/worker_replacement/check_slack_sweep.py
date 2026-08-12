"""Does SLACK open the coverage channel? Card ceiling swept over cap. Offline, no run."""
import sys, statistics
from itertools import product
sys.path.insert(0, '/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym')
from experiments.worker_replacement import finance_generator as gen
from experiments.worker_replacement import finance_scorer as sc


def best(scoref, segments, workers, cap):
    bv, ba = -1.0, ()
    for combo in product(range(len(workers)), repeat=len(segments)):
        if any(combo.count(i) > cap for i in range(len(workers))):
            continue
        v = sum(scoref(sg, workers[w]) for sg, w in zip(segments, combo))
        if v > bv:
            bv, ba = v, combo
    return bv, ba


def card_ceiling_at_cap(seed, cap):
    """The STALE-CARD ceiling at a given capacity. One definition, in the scorer.

    Named for its baseline: a bare `ceiling` is what let an ignorant-baseline
    quantity become this study's admission criterion.
    """
    out = sc.ceiling_vs_stale_card(gen.generate(seed), cap=cap)
    return out["oracle"], out["ceiling_share"]

SIGMA = 0.0768
SEEDS = list(range(30))
print("DOES SLACK OPEN THE COVERAGE CHANNEL? card ceiling by cap, 30 seeds, offline")
print()
print(f"{'cap':>4} {'shapes':>7} {'nonzero':>8} {'mean%':>8} {'nonzero%':>9} {'sigma':>7} {'n/arm':>8}")
for cap in (3, 4, 5):
    shapes = {tuple(sorted(s, reverse=True)) for s in product(range(cap + 1), repeat=3)
              if sum(s) == 9}
    fr = [card_ceiling_at_cap(s, cap)[1] for s in SEEDS]
    nz = [f for f in fr if f > 1e-12]
    m, mnz = statistics.mean(fr), (statistics.mean(nz) if nz else 0.0)
    eff = mnz / SIGMA
    n = 16 / eff ** 2 if eff > 0 else float('inf')
    print(f"{cap:>4} {len(shapes):>7} {len(nz):>4}/{len(fr):<3} {m*100:>7.2f}% "
          f"{mnz*100:>8.2f}% {eff:>7.2f} {n:>8.0f}")
