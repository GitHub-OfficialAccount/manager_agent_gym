"""Pricing the BOOK-SIZE lever — buying detectability without spending realism.

LS asked what a realistic-niche book at 2x and 4x the segment count buys, and where the
DP cost becomes binding.

THE DP IS NOT THE BINDING CONSTRAINT, and that is the first finding. The capacitated
optimum is a transportation problem, not something that needs enumerating over
3^n allocations. With three workers it is an exact DP over (used_0, used_1) — O(n * cap^2)
— so 36 or 360 segments is as cheap as 9. The 1,680-allocation enumeration is an
implementation choice that has been read as a mathematical limit.

METHOD. Scale a real instance by REPLICATING each segment k times and scaling cap to 3k.
That holds the class mix, the concentration and the niche share EXACTLY constant while
changing only book size — which is the manipulation being priced. It is a scaling
analysis of the existing books, not a new generator.
"""
import random
import statistics as st
import sys
from itertools import permutations

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")

from experiments.worker_replacement import finance_generator as gen  # noqa: E402
from experiments.worker_replacement import finance_scorer as sc  # noqa: E402

FEASIBLE9 = sorted(set(permutations([0, 0, 0, 1, 1, 1, 2, 2, 2])))


def best_dp(matrix, cap):
    """Exact capacitated optimum by DP over (used_0, used_1). Three workers."""
    n = len(matrix)
    cur = {(0, 0): 0.0}
    for j in range(n):
        nxt = {}
        row = matrix[j]
        for (c0, c1), v in cur.items():
            for w in (0, 1, 2):
                d0, d1 = c0 + (w == 0), c1 + (w == 1)
                c2 = (j + 1) - d0 - d1
                if d0 > cap or d1 > cap or c2 > cap:
                    continue
                key = (d0, d1)
                val = v + row[w]
                if nxt.get(key, -1e18) < val:
                    nxt[key] = val
        cur = nxt
    return max(cur.values())


def best_enum9(matrix):
    return max(sum(matrix[j][w] for j, w in enumerate(c)) for c in FEASIBLE9)


def matrices(instance, k):
    """Score matrices for a k-replicated book, plus the card-believing variant."""
    e = instance["event"]
    cal = instance["class_calibration"]
    by = {w["worker_id"]: w for w in instance["workers"]}
    roster = [by[w] for w in e["roster_post_swap"]]
    succ = e["successor_id"]
    card = tuple(by[e["predecessor_id"]]["irb_coverage"])
    carded = dict(by[succ])
    carded["irb_coverage"] = card
    carded["private_pd_calibration"] = {c: cal[c] for c in card if c in cal}
    segs = list(instance["segments"]) * k
    true_m = [[sc.s(sg, w, cal) for w in roster] for sg in segs]
    bel_m = [[sc.s(sg, carded, cal) if roster[i]["worker_id"] == succ else true_m[j][i]
              for i in range(3)] for j, sg in enumerate(segs)]
    return true_m, bel_m


# ---------------------------------------------------------------------------
print("=" * 76)
print("POSITIVE CONTROL — the DP must equal the 1,680-allocation enumeration at k=1")
print("=" * 76)
worst = 0.0
for seed in range(10):
    inst = gen.generate(seed)
    t, b = matrices(inst, 1)
    worst = max(worst, abs(best_dp(t, 3) - best_enum9(t)),
                abs(best_dp(b, 3) - best_enum9(b)))
print(f"  max |DP - enumeration| over 10 seeds x both beliefs : {worst:.2e}")
print(f"  -> {'IDENTICAL' if worst < 1e-9 else 'MISMATCH — do not trust the DP'}")

# ---------------------------------------------------------------------------
print()
print("=" * 76)
print("THE BOOK-SIZE SWEEP — class mix, concentration and niche share held constant")
print("=" * 76)
print(f"{'k':>3} {'segments':>9} {'cap':>5} {'ceiling share':>14} {'sd_alloc/oracle':>16} "
      f"{'effect/sd':>10} {'n/arm':>8}")
rows = []
for k in (1, 2, 4, 8):
    shares, sds = [], []
    for seed in range(10):
        inst = gen.generate(seed)
        t, b = matrices(inst, k)
        cap = 3 * k
        oracle = best_dp(t, cap)
        # the card-believing allocation, then re-scored under truth. The DP returns a
        # value, not an argmax, so recover a believed-optimal allocation greedily
        # under the believed matrix with capacity, then score it under truth.
        # (Exactness of the ARGMAX is not needed for a scaling analysis; the point is
        # how the quantities move with k, and both are computed the same way at every k.)
        remaining = [cap] * 3
        order = sorted(range(len(b)), key=lambda j: -max(b[j]))
        alloc = [None] * len(b)
        for j in order:
            w = max((w for w in range(3) if remaining[w] > 0), key=lambda w: b[j][w])
            remaining[w] -= 1
            alloc[j] = w
        realised = sum(t[j][alloc[j]] for j in range(len(t)))
        shares.append((oracle - realised) / oracle)
        # allocation-variance proxy: blind capacity-respecting assignment
        rng = random.Random(f"bs::{seed}::{k}")
        runs = []
        for _ in range(400):
            rem = [cap] * 3
            idx = list(range(len(t)))
            rng.shuffle(idx)
            v = 0.0
            for j in idx:
                ch = [w for w in range(3) if rem[w] > 0]
                w = rng.choice(ch)
                rem[w] -= 1
                v += t[j][w]
            runs.append(v)
        sds.append(st.stdev(runs) / oracle)
    eff, sd = st.mean(shares), st.mean(sds)
    rows.append((k, eff, sd))
    print(f"{k:>3} {9 * k:>9} {3 * k:>5} {eff:>13.2%} {sd:>16.4f} "
          f"{eff / sd:>10.2f} {16 / (eff / sd) ** 2:>8.0f}")

print()
e1, s1 = rows[0][1], rows[0][2]
print("scaling, relative to k=1:")
for k, eff, sd in rows:
    print(f"  k={k}: effect share x{eff / e1:.3f}   sd x{sd / s1:.3f}   "
          f"(1/sqrt(k) = {k ** -0.5:.3f})   effect/sd x{(eff / sd) / (e1 / s1):.2f}")
