"""Analyze ds_reroute runs — pure aggregation (correctness is exact-match, no LLM).

For post-swap ADVANCED tasks: correctness and routing per condition, plus the
manager's action mix (task-graph edits). Regret = oracle - silent.

  uv run python -m experiments.ds_reroute.analyze
"""

import argparse
import json
from collections import Counter
from pathlib import Path


def analyze_run(run_dir: Path) -> dict:
    m = json.loads((run_dir / "manifest.json").read_text())
    comps = json.loads((run_dir / "completions.json").read_text())
    actions = json.loads((run_dir / "manager_actions.json").read_text())
    swap_t = m["swap_timestep"]
    new_holder = m["new_holder"]

    post_adv = [c for c in comps if c["needs_advanced"]
                and (c["started_timestep"] or 0) >= swap_t]
    n = len(post_adv)
    correct = sum(c["correct"] for c in post_adv)
    routed = Counter(c["agent_id"] for c in post_adv)
    to_new = routed.get(new_holder, 0)
    print(f"\n== {run_dir.name} (condition={m['condition']}) ==")
    print(f"  post-swap ADVANCED tasks: {correct}/{n} correct")
    print(f"  routed to: {dict(routed)}  (correct holder after swap: {new_holder})")
    print(f"  manager action mix: {dict(Counter(a['action_type'] for a in actions))}")
    return {"condition": m["condition"], "n": n, "correct": correct,
            "acc": correct / n if n else None, "to_new_holder": to_new}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", type=Path, default=Path("experiments/ds_reroute/outputs"))
    args = p.parse_args()
    dirs = sorted(d for d in args.runs.iterdir()
                  if d.is_dir() and (d / "completions.json").exists())
    summ = {r["condition"]: r for r in (analyze_run(d) for d in dirs)}
    if "oracle" in summ and "silent" in summ:
        o, s = summ["oracle"]["acc"], summ["silent"]["acc"]
        if o is not None and s is not None:
            print(f"\nregret (advanced-task accuracy) = oracle - silent = {o - s:.2f}")


if __name__ == "__main__":
    main()
