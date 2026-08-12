"""LS review of S4: reproduce the signed-execution-loss mechanism via the real API."""
import json
from experiments.worker_replacement.finance_scorer import (
    decompose_regret, faithful_reports, attainable_report, correct_rwa,
)

inst = json.load(open("experiments/worker_replacement/records/S4/instance_seed101_8seg.json"))
workers = {w["worker_id"]: w for w in inst["workers"]}

case = None
for seg in inst["segments"]:
    if not seg["irb_approved"]:
        continue
    truth = correct_rwa(seg)
    for wid, w in workers.items():
        if seg["asset_class"] in w["irb_coverage"]:
            continue  # want an UNCOVERED (misrouted) worker
        faithful = attainable_report(seg, w)  # its SA fallback value
        if faithful > truth:
            case = (seg, wid, truth, faithful)
            break
    if case:
        break

assert case, "no SA-overstates segment found"
seg, wid, truth, faithful = case
print(f"segment {seg['segment_id']} ({seg['asset_class']}): IRB truth {truth:.4f}; "
      f"uncovered {wid} faithful SA {faithful:.4f} (overstates by {faithful/truth-1:+.1%})")

allocation = {}
for s_ in inst["segments"]:
    if s_["segment_id"] == seg["segment_id"]:
        allocation[s_["segment_id"]] = wid  # misroute
    else:
        cov = [w2 for w2, ww in workers.items() if s_["asset_class"] in ww["irb_coverage"]]
        allocation[s_["segment_id"]] = cov[0] if cov else wid

reports = faithful_reports(inst, allocation)
reports[seg["segment_id"]] = 0.8 * faithful  # under-report: moves TOWARD truth

d = decompose_regret(inst, allocation, reports)
print({k: round(v, 6) for k, v in d.items()})
assert d["execution_loss"] < 0, "expected NEGATIVE execution loss"
assert abs(d["allocation_loss"] + d["execution_loss"] - d["total_regret"]) < 1e-9
print("CONFIRMED: under-reporting toward truth yields NEGATIVE execution loss; sum identity holds")
