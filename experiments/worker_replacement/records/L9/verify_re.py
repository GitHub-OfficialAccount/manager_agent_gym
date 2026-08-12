"""Two checks RE asked for, plus a control on my own reimplementation.

CHECK A — is `ceiling_replacement` isolated from `ceiling_vs_stale_card` in ONE
place only? RE's aggregate control (30/30 agreement under the current template) is
consistent with isolation but does not prove it: two belief models can differ per
segment and still pick the same allocation. So compare the two believed_score
functions SEGMENT BY SEGMENT and classify every difference.

The suspicion worth testing: the shipped model returns a hardcoded 1.0 where the
card claims IRB coverage, while the replacement model returns s(seg, succ_as_carded).
Those coincide only if s() is exactly 1.0 there. If it is not, the two models differ
in TWO places — the omission AND the attainment granted on the lie — and the 8.13%
gap is not attributable to the belief model alone.

CHECK B — RE disputes my "nA=0 is IDENTICAL to the current template". Reproduce
their table independently.
"""
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
SIGMA = 0.0768

# With 9 segments, 3 workers and cap 3, every assignment of all segments is
# exactly 3/3/3 — so the feasible set is the 1680 multiset permutations, and
# enumerating them is EXACT, not a sample. (This is the same fact as the
# "exactly one feasible load shape" reliability finding.)
FEASIBLE = sorted(set(permutations([0, 0, 0, 1, 1, 1, 2, 2, 2])))
assert len(FEASIBLE) == 1680


def build(instance, template, perm=None):
    """Substitute coverage. `perm` maps template letters a..e to asset classes;
    None recovers the seed's own permutation, as check_template_pricing does."""
    lab = labels_of(instance)
    roles = ["_pred", "_succ", "_w2", "_w3"]
    if perm is None:
        letter = {ch: lab[ch] for ch in "abcde"}
    else:
        letter = perm
    calibration = instance["class_calibration"]
    real = {w["worker_id"]: w for w in instance["workers"]}
    coverage = {lab[r]: tuple(letter[ch] for ch in spec)
                for r, spec in zip(roles, template)}
    by_id = {}
    for r in roles:
        wid = lab[r]
        row = dict(real[wid])
        row["irb_coverage"] = coverage[wid]
        row["private_pd_calibration"] = {c: calibration[c] for c in coverage[wid]}
        by_id[wid] = row
    return lab, by_id, coverage, calibration


def price(instance, template, perm=None, model="replacement"):
    lab, by_id, coverage, calibration = build(instance, template, perm)
    predecessor, successor = lab["_pred"], lab["_succ"]
    roster = [by_id[lab[r]] for r in ("_succ", "_w2", "_w3")]
    segments = instance["segments"]
    card_claims = set(coverage[predecessor])

    succ_as_carded = dict(by_id[successor])
    succ_as_carded["irb_coverage"] = tuple(card_claims)
    succ_as_carded["private_pd_calibration"] = {c: calibration[c] for c in card_claims}

    def true_score(sg, w):
        return sc.s(sg, w, calibration)

    def believed(sg, w):
        if w["worker_id"] != successor:
            return sc.s(sg, w, calibration)
        if model == "replacement":
            return sc.s(sg, succ_as_carded, calibration)
        # shipped: hardcoded 1.0 on a claimed IRB class, else fall through to TRUTH
        if sc.applicable_approach(sg) == "IRB" and sg["asset_class"] in card_claims:
            return 1.0
        return sc.s(sg, w, calibration)

    T = [[true_score(sg, w) for w in roster] for sg in segments]
    B = [[believed(sg, w) for w in roster] for sg in segments]

    def best(M):
        bv, ba = -1.0, None
        for combo in FEASIBLE:
            v = M[0][combo[0]] + M[1][combo[1]] + M[2][combo[2]] + M[3][combo[3]] \
                + M[4][combo[4]] + M[5][combo[5]] + M[6][combo[6]] + M[7][combo[7]] \
                + M[8][combo[8]]
            if v > bv:
                bv, ba = v, combo
        return bv, ba

    oracle, _ = best(T)
    _, alloc = best(B)
    realised = sum(T[i][alloc[i]] for i in range(len(segments)))
    return (oracle - realised) / oracle, oracle


# ---------------------------------------------------------------------------
print("=" * 78)
print("CONTROL ON MY OWN REIMPLEMENTATION — must match check_template_pricing")
print("  (published: current 0.85%, proposed_disjoint 8.51%, partial_overlap 0.00%)")
print("=" * 78)
for name, tpl in TEMPLATES.items():
    shares = [price(gen.generate(s), tpl, model="replacement")[0] for s in range(30)]
    print(f"  {name:<20} {st.mean(shares):>8.2%}")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("CHECK A — the two belief models, compared SEGMENT BY SEGMENT")
print("=" * 78)
diff_on_claimed = 0
diff_on_silent = 0
agree = 0
claimed_not_one = []
for name, tpl in TEMPLATES.items():
    for seed in range(30):
        instance = gen.generate(seed)
        lab, by_id, coverage, calibration = build(instance, tpl)
        predecessor, successor = lab["_pred"], lab["_succ"]
        card_claims = set(coverage[predecessor])
        true_cov = set(coverage[successor])
        succ_as_carded = dict(by_id[successor])
        succ_as_carded["irb_coverage"] = tuple(card_claims)
        succ_as_carded["private_pd_calibration"] = {
            c: calibration[c] for c in card_claims}
        for sg in instance["segments"]:
            cls = sg["asset_class"]
            irb = sc.applicable_approach(sg) == "IRB"
            rep = sc.s(sg, succ_as_carded, calibration)
            if irb and cls in card_claims:
                ship = 1.0
            else:
                ship = sc.s(sg, by_id[successor], calibration)
            if abs(rep - ship) > 1e-12:
                if cls in card_claims:
                    diff_on_claimed += 1
                    claimed_not_one.append((name, seed, cls, ship, rep))
                else:
                    diff_on_silent += 1
            else:
                agree += 1

print(f"  segment-worker cells compared        : "
      f"{agree + diff_on_claimed + diff_on_silent}")
print(f"  models AGREE                         : {agree}")
print(f"  differ on a class the card is SILENT about (the INTENDED difference): "
      f"{diff_on_silent}")
print(f"  differ on a class the card CLAIMS    (an UNINTENDED second difference): "
      f"{diff_on_claimed}")
if claimed_not_one:
    print("\n  examples where the shipped 1.0 and the replacement score DISAGREE")
    print("  on a CLAIMED class (i.e. s() is not exactly 1.0 there):")
    for row in claimed_not_one[:8]:
        print(f"     {row[0]:<18} seed {row[1]:<3} {row[2]:<10} "
              f"shipped={row[3]:.6f} replacement={row[4]:.6f}")
print(f"\n  -> isolation is {'CLEAN' if not claimed_not_one else 'NOT CLEAN'}: "
      f"the models differ in "
      f"{'one place only' if not claimed_not_one else 'TWO places'}")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("CHECK B — the nA table, reproduced independently")
print("  RE: current 0.03/0.06/0.07, disjoint 0.18/0.45/1.11 sigma at nA=0/1/4")
print("=" * 78)
CLASSES = list(gen.ASSET_CLASSES)
rows = {"current": {}, "proposed_disjoint": {}}
for seed in range(10):
    instance = gen.generate(seed)
    for p in permutations(CLASSES):
        perm = dict(zip("abcde", p))
        nA = sum(1 for sg in instance["segments"]
                 if sg["asset_class"] == perm["a"]
                 and sc.applicable_approach(sg) == "IRB")
        for name in rows:
            share, _ = price(instance, TEMPLATES[name], perm=perm,
                             model="replacement")
            rows[name].setdefault(nA, []).append(share)

allnA = sorted(set(rows["current"]) | set(rows["proposed_disjoint"]))
header = "  ".join(f"nA={k}" for k in allnA)
print(f"  {'template':<20} {header}      pooled")
for name in rows:
    cells = []
    for k in allnA:
        v = rows[name].get(k)
        cells.append(f"{st.mean(v) / SIGMA:>5.2f}" if v else "   - ")
    pooled = [x for v in rows[name].values() for x in v]
    print(f"  {name:<20} " + "  ".join(cells) +
          f"      {st.mean(pooled) / SIGMA:.2f}")
counts = {k: len(rows['current'].get(k, [])) for k in allnA}
total = sum(counts.values())
print(f"  {'cell share':<20} " +
      "  ".join(f"{counts[k] / total:>4.0%}" for k in allnA))
print("\n  ratio disjoint/current at each nA:")
for k in allnA:
    a = rows["proposed_disjoint"].get(k)
    b = rows["current"].get(k)
    if a and b and st.mean(b) > 0:
        print(f"     nA={k}: {st.mean(a) / st.mean(b):.1f}x")
