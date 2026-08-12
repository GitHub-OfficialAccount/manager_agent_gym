"""Two questions LS asked before the number exists.

Q1 — IS THE ECONOMIC CLONE'S BIAS SIGNABLE? The ceiling is built from misallocation,
and the cost of ONE misallocated segment is the score lost when a coverage gap forces
the SA fallback instead of the applicable IRB treatment. That cost is a property of
the CLASS — its SA/IRB divergence. A clone inherits its SOURCE class's divergence
exactly. So the bias against a real sixth class is the gap between the source's
divergence and the real class's, and its SIZE is bounded by how much divergence
varies across classes. Measure that spread.

Q2 — ARE TEMPLATE RATIOS INVARIANT TO WHICH SIGMA WE USE? Arithmetically a shared
sigma cancels from a ratio. But detectability is effect/sigma_OF_THAT_DESIGN, and a
template that changes the coverage lattice changes the outcome distribution too. If
sigma differs by template, the ratio of detectabilities is NOT the ratio of ceilings.
Measure a structural proxy for per-template outcome spread.
"""
import random
import statistics as st
import sys
from itertools import permutations

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")

from experiments.worker_replacement import finance_generator as gen  # noqa: E402
from experiments.worker_replacement import finance_scorer as sc  # noqa: E402
from experiments.worker_replacement.check_template_pricing import (  # noqa: E402
    TEMPLATES, labels_of,
)

CAP = 3
SEEDS = range(30)
FEASIBLE = sorted(set(permutations([0, 0, 0, 1, 1, 1, 2, 2, 2])))

# ---------------------------------------------------------------------------
# Q1 — per-class cost of a coverage gap
# ---------------------------------------------------------------------------
print("=" * 78)
print("Q1 — THE COST OF A COVERAGE GAP, BY ASSET CLASS")
print("=" * 78)
print("For each IRB-APPLICABLE segment: the score lost when a coverage gap forces")
print("the SA fallback. This is the per-segment currency the ceiling is paid in,")
print("and a clone inherits its source class's value EXACTLY.\n")

per_class = {}
applicable = {}
total = {}
for seed in SEEDS:
    instance = gen.generate(seed)
    calibration = instance["class_calibration"]
    for sg in instance["segments"]:
        cls = sg["asset_class"]
        total[cls] = total.get(cls, 0) + 1
        if sc.applicable_approach(sg) != "IRB":
            continue
        applicable[cls] = applicable.get(cls, 0) + 1
        # covered: the IRB number under the true class calibration -> exactly 1.0
        # uncovered: the SA fallback, scored against the IRB truth
        sa_score = sc.score_report(sg, sc.sa_rwa(sg), calibration)
        per_class.setdefault(cls, []).append(1.0 - sa_score)

print(f"{'class':<12} {'segments':>9} {'IRB-applic':>11} {'mean gap cost':>14} "
      f"{'sd':>7} {'min':>6} {'max':>6}")
for cls in sorted(per_class, key=lambda c: -st.mean(per_class[c])):
    v = per_class[cls]
    print(f"{cls:<12} {total[cls]:>9} {applicable[cls]:>11} "
          f"{st.mean(v):>14.4f} {st.stdev(v) if len(v) > 1 else 0:>7.4f} "
          f"{min(v):>6.3f} {max(v):>6.3f}")

means = {c: st.mean(v) for c, v in per_class.items()}
lo, hi = min(means.values()), max(means.values())
print(f"\nspread across classes: {lo:.4f} .. {hi:.4f}  "
      f"= a factor of {hi / lo if lo else float('inf'):.1f}")
print(f"unweighted mean across classes: {st.mean(list(means.values())):.4f}")

# ---------------------------------------------------------------------------
# Q2 — per-template outcome spread
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("Q2 — DOES THE OUTCOME SPREAD DEPEND ON THE TEMPLATE?")
print("=" * 78)
print("Proxy: the per-draw SD of a coverage-blind capacity-respecting assignment,")
print("as a share of oracle — the spread of outcomes the DESIGN admits. If this")
print("moves with the template, one shared sigma cannot serve all templates.\n")


def build(instance, template):
    lab = labels_of(instance)
    roles = ["_pred", "_succ", "_w2", "_w3"]
    calibration = instance["class_calibration"]
    real = {w["worker_id"]: w for w in instance["workers"]}
    coverage = {lab[r]: tuple(lab[ch] for ch in spec)
                for r, spec in zip(roles, template)}
    by_id = {}
    for r in roles:
        wid = lab[r]
        row = dict(real[wid])
        row["irb_coverage"] = coverage[wid]
        row["private_pd_calibration"] = {c: calibration[c] for c in coverage[wid]}
        by_id[wid] = row
    return lab, by_id, coverage, calibration


print(f"{'template':<20} {'oracle':>8} {'blind SD':>10} {'SD/oracle':>11} "
      f"{'feasible SD':>13} {'ceiling':>9}")
rows = {}
for name, tpl in TEMPLATES.items():
    sds, fsds, oracles, ceilings = [], [], [], []
    for seed in SEEDS:
        instance = gen.generate(seed)
        lab, by_id, coverage, calibration = build(instance, tpl)
        roster = [by_id[lab[r]] for r in ("_succ", "_w2", "_w3")]
        segments = instance["segments"]
        T = [[sc.s(sg, w, calibration) for w in roster] for sg in segments]
        vals = [sum(T[i][c[i]] for i in range(9)) for c in FEASIBLE]
        oracle = max(vals)
        oracles.append(oracle)
        # SD over ALL feasible allocations — the full outcome space of the design
        fsds.append(st.stdev(vals) / oracle)
        # SD of the blind sequential procedure, matching ignorant_stats
        rng = random.Random(f"sd::{seed}::{name}")
        runs = []
        for _ in range(2000):
            remaining = [CAP] * 3
            order = list(range(9))
            rng.shuffle(order)
            run = 0.0
            for i in order:
                ch = [w for w in range(3) if remaining[w] > 0]
                pick = rng.choice(ch)
                remaining[pick] -= 1
                run += T[i][pick]
            runs.append(run)
        sds.append(st.stdev(runs) / oracle)
    rows[name] = (st.mean(oracles), st.mean(sds), st.mean(fsds))
    print(f"{name:<20} {st.mean(oracles):>8.3f} "
          f"{st.mean(sds) * st.mean(oracles):>10.4f} {st.mean(sds):>11.4f} "
          f"{st.mean(fsds):>13.4f}")

base = rows["current"][1]
print(f"\nblind SD/oracle, relative to the current template:")
for name, (o, s, f) in rows.items():
    print(f"   {name:<20} {s / base:>5.2f}x")
print(f"\nsigma actually used in every published figure: 0.0768")
print("If the design's own spread rises with the template, dividing every")
print("template by ONE sigma overstates whichever template widened the spread.")
