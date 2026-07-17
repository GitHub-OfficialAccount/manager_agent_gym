"""Aggregate deterministic metrics from ds_reroute runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def analyze_run(run_dir: Path) -> dict[str, Any]:
    manifest = json.loads((run_dir / "manifest.json").read_text())
    completions = json.loads((run_dir / "completions.json").read_text())
    actions = json.loads((run_dir / "manager_actions.json").read_text())
    tool_calls = json.loads((run_dir / "tool_calls.json").read_text())
    swap_timestep = manifest["swap_timestep"]

    post_change = [
        row for row in completions
        if (row.get("started_timestep") or 0) >= swap_timestep
    ]
    post_robust = [
        row for row in post_change
        if row.get("stage") == "audit" and row.get("method") == "percentile"
    ]
    routes = Counter(row.get("agent_id") for row in post_robust)
    action_mix = Counter(
        row["action"].get("action_type")
        for row in actions
        if row.get("action")
    )
    result = {
        "condition": manifest["condition"],
        "seed": manifest["seed"],
        "r_check": manifest["r_check"],
        "completed": manifest["completed_predefined"],
        "post_change_r_check": (
            mean(row["r_check"] for row in post_change) if post_change else None
        ),
        "post_robust_routes": dict(routes),
        "tool_calls": dict(Counter(row["tool"] for row in tool_calls)),
        "action_mix": dict(action_mix),
    }
    print(f"\n== {run_dir.name} ==")
    print(
        f"  R_check={result['r_check']:.3f} "
        f"completed={result['completed']}/{manifest['total_predefined']}"
    )
    print(
        f"  post-change R_check={result['post_change_r_check']} "
        f"robust audit routes={result['post_robust_routes']}"
    )
    print(f"  action mix={result['action_mix']}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs", type=Path, default=Path("experiments/ds_reroute/outputs")
    )
    args = parser.parse_args()
    run_dirs = sorted(
        path for path in args.runs.iterdir()
        if path.is_dir() and (path / "manifest.json").exists()
    )
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run_dir in run_dirs:
        row = analyze_run(run_dir)
        by_condition[row["condition"]].append(row)

    if by_condition:
        print("\n== condition means ==")
    condition_means: dict[str, float] = {}
    for condition, rows in sorted(by_condition.items()):
        condition_means[condition] = mean(row["r_check"] for row in rows)
        print(
            f"  {condition:<8} R_check={condition_means[condition]:.3f} "
            f"n={len(rows)}"
        )
    if "full" in condition_means and "silent" in condition_means:
        print(
            "\n  adaptation gap (full - silent) = "
            f"{condition_means['full'] - condition_means['silent']:.3f}"
        )


if __name__ == "__main__":
    main()
