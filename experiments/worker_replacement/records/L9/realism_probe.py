"""Is the disjoint template's effect INFORMATION, or is it POISON REMOVAL?

The study claims to measure what information ABOUT THE NEWCOMER is worth. Under a
disjoint template every claim on the stale card is false, so a manager that simply
DISTRUSTED the card wholesale would recover much of the effect without learning
anything newcomer-specific. If that is what is happening, the disjoint design
cannot separate "the manager learned about the successor" from "the manager
stopped believing a maximally wrong prior" — and those are different findings.

The test is a three-way comparison, all exact/offline:

    oracle                  perfect knowledge
    stale-card play         optimal play BELIEVING the card         <- study's baseline
    ignorant play           E[coverage-blind capacity-respecting]   <- knows nothing

If stale-card play scores BELOW ignorant play, the card is worse than useless and
part of the measured channel is poison removal, available to blanket distrust.
"""
import random
import statistics as st
import sys
from itertools import product

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")

from experiments.worker_replacement import finance_generator as gen  # noqa: E402
from experiments.worker_replacement import finance_scorer as sc  # noqa: E402
from experiments.worker_replacement.check_template_pricing import (  # noqa: E402
    labels_of,
)

CAP = 3
SEEDS = range(30)
DRAWS = 4000

TEMPLATES = {
    "current":           ("ae", "ab", "bc", "cd"),
    "proposed_disjoint": ("de", "ab", "ce", "cb"),
    "partial_overlap":   ("ae", "ab", "ce", "cb"),
}


def three_way(seed, template):
    instance = gen.generate(seed)
    lab = labels_of(instance)
    calibration = instance["class_calibration"]
    segments = instance["segments"]
    roles = ["_pred", "_succ", "_w2", "_w3"]
    coverage = {lab[r]: tuple(lab[ch] for ch in spec)
                for r, spec in zip(roles, template)}
    real = {w["worker_id"]: w for w in instance["workers"]}
    by_id = {}
    for r in roles:
        wid = lab[r]
        row = dict(real[wid])
        row["irb_coverage"] = coverage[wid]
        row["private_pd_calibration"] = {c: calibration[c] for c in coverage[wid]}
        by_id[wid] = row

    predecessor, successor = lab["_pred"], lab["_succ"]
    roster = [by_id[lab[r]] for r in ("_succ", "_w2", "_w3")]
    card_claims = set(coverage[predecessor])

    def true_score(sg, w):
        return sc.s(sg, w, calibration)

    succ_as_believed = dict(by_id[successor])
    succ_as_believed["irb_coverage"] = tuple(card_claims)
    succ_as_believed["private_pd_calibration"] = {c: calibration[c] for c in card_claims}

    def believed(sg, w):
        if w["worker_id"] != successor:
            return sc.s(sg, w, calibration)
        return sc.s(sg, succ_as_believed, calibration)

    def best(scoref):
        bv, ba = -1.0, ()
        for combo in product(range(len(roster)), repeat=len(segments)):
            if any(combo.count(i) > CAP for i in range(len(roster))):
                continue
            v = sum(scoref(sg, roster[w]) for sg, w in zip(segments, combo))
            if v > bv:
                bv, ba = v, combo
        return bv, ba

    oracle, _ = best(true_score)
    _, card_alloc = best(believed)
    card_realised = sum(true_score(sg, roster[w])
                        for sg, w in zip(segments, card_alloc))

    # the ignorant baseline, replicating finance_scorer.ignorant_stats' procedure
    # exactly (shuffle segment order; uniform pick among workers with capacity)
    scores = [[true_score(sg, w) for w in roster] for sg in segments]
    rng = random.Random(f"ignorant::{seed}::{CAP}::{DRAWS}::0")
    runs = []
    for _ in range(DRAWS):
        remaining = [CAP] * len(roster)
        order = list(range(len(segments)))
        rng.shuffle(order)
        run = 0.0
        for i in order:
            choices = [w for w in range(len(roster)) if remaining[w] > 0]
            if not choices:
                continue
            pick = rng.choice(choices)
            remaining[pick] -= 1
            run += scores[i][pick]
        runs.append(run)
    ignorant = st.fmean(runs)
    se = st.stdev(runs) / (DRAWS ** 0.5)

    return {
        "oracle": oracle,
        "card": card_realised,
        "ignorant": ignorant,
        "ignorant_se": se,
        "card_minus_ignorant": card_realised - ignorant,
        "vs_stale_card_share": (oracle - card_realised) / oracle,
        "vs_ignorant_share": (oracle - ignorant) / oracle,
    }


print(f"{'template':<20} {'ceil vs card':>13} {'ceil vs ignorant':>17} "
      f"{'card-ignorant':>14} {'card WORSE':>11}")
print("-" * 80)
for name, tpl in TEMPLATES.items():
    rows = [three_way(s, tpl) for s in SEEDS]
    c = st.fmean(r["vs_stale_card_share"] for r in rows)
    i = st.fmean(r["vs_ignorant_share"] for r in rows)
    d = st.fmean(r["card_minus_ignorant"] for r in rows)
    worse = sum(1 for r in rows
                if r["card"] < r["ignorant"] - 2 * r["ignorant_se"])
    print(f"{name:<20} {c:>12.2%} {i:>16.2%} {d:>+14.4f} {worse:>8}/{len(rows)}")

print()
print("READING: 'card-ignorant' is how much the stale card is worth ON NET against")
print("knowing nothing. NEGATIVE means believing the card is WORSE than ignorance,")
print("so part of the channel's measured value is available to blanket distrust")
print("and is not newcomer-specific information at all.")
