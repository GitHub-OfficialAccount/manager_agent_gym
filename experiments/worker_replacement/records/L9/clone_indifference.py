"""Is the clone's MANUFACTURED INDIFFERENCE signable — or is it an artefact with no
counterpart in the design being priced?

LS's question. The economic bias I already signed (a clone inherits its source's
SA/IRB divergence, so it understates a real high-divergence class). This is the OTHER
bias: the clone is EXACT, which manufactures believed-side ties whose re-scoring
under truth spreads the ceiling by 7% mean / 14% max — the same order as the effect.

THE TEST THAT ANSWERS IT, and it is not a tie-break rule. A REAL sixth class has
economics DISTINCT from all five. So register a sixth class and PERTURB its SA table
by delta, making it economically distinct exactly as a real class would be, and ask
whether the ambiguity survives. Sweep delta through both signs and several orders of
magnitude:

  * if the ambiguity dies at tiny delta, the degeneracy is KNIFE-EDGE — it exists
    only at delta EXACTLY zero, so no real sixth class has it, and the 7% band is an
    artefact of the instrument rather than uncertainty about the design;
  * where the perturbed ceilings LAND inside the exact clone's [min, max] says
    whether expectation over the tie set is unbiased (they scatter around the mean)
    or whether the tie-break is signed (they pile on one endpoint);
  * if the two SIGNS of delta give different limits, the perturbation direction is a
    free parameter -- which is the confound LS asked about.
"""
import statistics as st
import sys
from itertools import permutations

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")

from experiments.worker_replacement import finance_generator as gen  # noqa: E402
from experiments.worker_replacement import finance_scorer as sc  # noqa: E402

CAP = 3
SEEDS = range(10)
TIE_EPS = 1e-12
FEASIBLE = sorted(set(permutations([0, 0, 0, 1, 1, 1, 2, 2, 2])))

CLONE = gen.register_synthetic_clone("corporate_clone", "corporate")
SIX = gen.ASSET_CLASSES + (CLONE,)
# RE's size-3 partial-overlap template, unchanged so the comparison is theirs.
TEMPLATE = [("sovereign", "bank", "corporate"),
            ("sovereign", "retail", "mdb"),
            ("corporate", "retail", CLONE),
            ("mdb", CLONE, "bank")]
PRISTINE = dict(gen.SA_TABLES[CLONE])


def set_delta(delta):
    """Make the sixth class economically DISTINCT by scaling its SA weights."""
    gen.SA_TABLES[CLONE] = {k: v * (1.0 + delta) for k, v in PRISTINE.items()}


def ceilings_over_tieset(instance):
    """Every ceiling the instance could report, one per believed-optimal allocation."""
    event = instance["event"]
    calibration = instance["class_calibration"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    roster = [by_id[w] for w in event["roster_post_swap"]]
    segments = instance["segments"]
    successor = event["successor_id"]
    card = tuple(by_id[event["predecessor_id"]]["irb_coverage"])
    carded = dict(by_id[successor])
    carded["irb_coverage"] = card
    carded["private_pd_calibration"] = {c: calibration[c] for c in card if c in calibration}

    true_m = [[sc.s(sg, w, calibration) for w in roster] for sg in segments]
    believed_m = [
        [sc.s(sg, carded, calibration) if roster[i]["worker_id"] == successor
         else true_m[j][i] for i in range(len(roster))]
        for j, sg in enumerate(segments)]

    tv = [sum(true_m[j][w] for j, w in enumerate(c)) for c in FEASIBLE]
    bv = [sum(believed_m[j][w] for j, w in enumerate(c)) for c in FEASIBLE]
    true_value = max(tv)
    best_b = max(bv)
    realised = [tv[i] for i in range(len(FEASIBLE)) if abs(bv[i] - best_b) <= TIE_EPS]
    return [(true_value - r) / true_value for r in realised], true_value


def measure(delta):
    set_delta(delta)
    n_tied, spreads, mins, maxs, means = [], [], [], [], []
    for seed in SEEDS:
        inst = gen.generate(seed, coverage_override=TEMPLATE, asset_classes=SIX)
        cs, _ = ceilings_over_tieset(inst)
        n_tied.append(len(cs))
        spreads.append(max(cs) - min(cs))
        mins.append(min(cs)); maxs.append(max(cs)); means.append(st.mean(cs))
    return dict(delta=delta, tied=st.mean(n_tied), spread=st.mean(spreads),
                spread_max=max(spreads),
                ambiguous=sum(1 for s in spreads if s > 1e-9),
                cmin=st.mean(mins), cmax=st.mean(maxs), cmean=st.mean(means))


print("=" * 88)
print("CONTROL — the exact clone (delta = 0) must reproduce RE's numbers")
print("  RE: ceiling spread 7.00% mean / 14.10% max, ambiguous 20/20")
print("=" * 88)
base = measure(0.0)
print(f"  believed-optimal tie set size (mean) : {base['tied']:.2f}")
print(f"  ceiling spread  mean {base['spread']:.2%}   max {base['spread_max']:.2%}"
      f"   ambiguous {base['ambiguous']}/{len(SEEDS)}")
print(f"  ceiling  min {base['cmin']:.2%}   mean {base['cmean']:.2%}   "
      f"max {base['cmax']:.2%}")

print()
print("=" * 88)
print("THE SWEEP — a sixth class made economically DISTINCT, as a real one would be")
print("=" * 88)
print(f"{'delta':>10} {'tie set':>9} {'spread':>9} {'ambig':>7} "
      f"{'ceiling (unique or mean)':>25}")
rows = []
for delta in (-0.20, -0.05, -0.01, -1e-3, -1e-6, -1e-9, 0.0,
              1e-9, 1e-6, 1e-3, 0.01, 0.05, 0.20):
    r = measure(delta)
    rows.append(r)
    tag = "  <== EXACT CLONE" if delta == 0.0 else ""
    print(f"{delta:>10.0e} {r['tied']:>9.2f} {r['spread']:>9.2%} "
          f"{r['ambiguous']:>4}/{len(SEEDS)} {r['cmean']:>24.2%}{tag}")

set_delta(0.0)
print()
print("WHERE THE PERTURBED CEILINGS LAND relative to the exact clone's tie set:")
print(f"  exact clone tie set spans  [{base['cmin']:.2%}, {base['cmax']:.2%}]"
      f"   mean {base['cmean']:.2%}")
for r in rows:
    if r["delta"] == 0.0 or abs(r["delta"]) > 1e-3:
        continue
    span = base["cmax"] - base["cmin"]
    pos = (r["cmean"] - base["cmin"]) / span if span else 0.0
    print(f"  delta={r['delta']:>9.0e}  ceiling {r['cmean']:.2%}   "
          f"position in [min,max] = {pos:.2f}  "
          f"({'min end' if pos < 0.25 else 'max end' if pos > 0.75 else 'interior'})")
