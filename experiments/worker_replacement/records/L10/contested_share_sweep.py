"""The contested-share sweep, committed so the figures can be re-run (RR).

Reproducible: identical under PYTHONHASHSEED 0,1,2,3 and on repeated in-process runs.
Supersedes uncommitted inline runs whose figures were ~7-14% higher and which cannot
be reproduced.
"""
import random
import statistics as st
import sys

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")

from experiments.worker_replacement import finance_generator as gen  # noqa: E402
from experiments.worker_replacement import finance_scorer as sc  # noqa: E402


def roles(instance):
    event = instance["event"]
    by = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
    pred, succ = by[event["predecessor_id"]], by[event["successor_id"]]
    return sorted(pred & succ)[0], sorted(pred - succ)[0]


def cell(seed, frac, force_role, segs=1):
    probe = gen.generate(seed, lattice="partial")
    shared, lied = roles(probe)
    target = shared if force_role == "shared" else lied
    instance = gen.generate(seed, lattice="partial", force_mix_class=target,
                            shared_class_segments=segs,
                            irb_applicable_fraction=frac)
    r = sc.ceiling_vs_stale_card(instance, cap=3)
    event, cal = instance["event"], instance["class_calibration"]
    by = {w["worker_id"]: w for w in instance["workers"]}
    roster = [by[w] for w in event["roster_post_swap"]]
    segments = instance["segments"]
    matrix = [[sc.s(sg, w, cal) for w in roster] for sg in segments]
    rng = random.Random(f"ignorant::{seed}::{frac}::{force_role}::{segs}")
    runs = []
    for _ in range(1000):
        remaining, order, value = [3] * 3, list(range(len(segments))), 0.0
        rng.shuffle(order)
        for i in order:
            choices = [w for w in range(3) if remaining[w] > 0]
            pick = rng.choice(choices)
            remaining[pick] -= 1
            value += matrix[i][pick]
        runs.append(value)
    contested = sum(
        1 for sg in segments
        if len({round(sc.s(sg, w, cal), 12) for w in roster}) > 1)
    return (r["ceiling_share"] or 0.0,
            r["card_believing_play_realises"] - st.fmean(runs),
            contested)


if __name__ == "__main__":
    print(f"{'force':<8}{'irb_frac':>9}{'n':>4}{'ceiling':>10}"
          f"{'card-ignorant':>15}{'contested':>11}")
    for force in ("shared", "lied"):
        for frac in (0.44, 0.67, 0.89):
            rows = []
            for seed in range(20):
                try:
                    rows.append(cell(seed, frac, force))
                except Exception:
                    continue
            if rows:
                print(f"{force:<8}{frac:>9.2f}{len(rows):>4}"
                      f"{st.mean(r[0] for r in rows):>9.4%}"
                      f"{st.mean(r[1] for r in rows):>+15.4f}"
                      f"{st.mean(r[2] for r in rows):>11.2f}")
