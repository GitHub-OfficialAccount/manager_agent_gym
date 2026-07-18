"""Audit Arm-2 evidence recall and realized manager-context size.

Labels are manager-visible, change-relevant facts—not hidden perturbation state.
The audit reports whether each labeled fact reached the ledger and how long after
first visibility it arrived. It also reports the actual prompt text sent to the
manager (UTF-8 bytes and whitespace-token counts) for budget matching.

Example:
    uv run python -m experiments.ds_reroute.audit_arm2 \
      --labels experiments/ds_reroute/evidence_labels/toolset_seed101.json \
      experiments/ds_reroute/outputs/...seed101
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from manager_agent_gym.core.manager_agent.observation_aids import (
    _parse_workflow_summary,
)


TASK_HEADER_RE = re.compile(r"Task: (.+?) \(ID: ([0-9a-fA-F-]+)\)")


def _load_run(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    trace = json.loads((run_dir / "run.json").read_text())
    ledger_path = run_dir / "evidence_ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    return trace, ledger


def _manager_requests(trace: dict[str, Any]) -> list[tuple[int, str]]:
    requests = []
    for event in trace.get("events", []):
        if event.get("event_type") != "structured_llm_request":
            continue
        if event.get("actor_type") != "manager":
            continue
        messages = event.get("payload", {}).get("messages", [])
        text = "\n".join(str(message.get("content", "")) for message in messages)
        requests.append((int(event.get("timestep") or 0), text))
    return requests


def _task_names(requests: list[tuple[int, str]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for _, text in requests:
        for name, task_id in TASK_HEADER_RE.findall(text):
            names[task_id] = name
    return names


def _visible_resource_facts(text: str) -> list[tuple[str | None, str]]:
    marker = "- current_workflow_summary: "
    start = text.find(marker)
    if start < 0:
        return []
    start += len(marker)
    end = text.find("\n- execution_state:", start)
    summary = text[start:] if end < 0 else text[start:end]
    tasks, resources = _parse_workflow_summary(summary)
    resource_tasks = {
        resource_id: task.task_name
        for task in tasks.values()
        for resource_id in task.output_resource_ids
    }
    visible = []
    for resource_id, resource in resources.items():
        visible.extend(
            (resource_tasks.get(resource_id), fact) for fact in resource.facts
        )
    for task in tasks.values():
        if task.status in {"completed", "failed"}:
            visible.append((task.task_name, f"Status: {task.status}"))
        visible.extend((task.task_name, fact) for fact in task.failure_facts)
    return visible


def _normalize_ledger(
    ledger: list[dict[str, Any]], task_names: dict[str, str]
) -> list[dict[str, Any]]:
    normalized = []
    for entry in ledger:
        row = dict(entry)
        task = row.get("task")
        row["task_name"] = task_names.get(str(task), task)
        normalized.append(row)
    return normalized


def _matches(label: dict[str, Any], *, fact: str, worker: Any, task: Any) -> bool:
    if label.get("worker") and label["worker"] != worker:
        return False
    if label.get("task_pattern") and not re.search(
        label["task_pattern"], str(task or ""), re.IGNORECASE
    ):
        return False
    return bool(re.search(label["fact_pattern"], fact, re.IGNORECASE))


def audit_recall(
    labels: list[dict[str, Any]],
    requests: list[tuple[int, str]],
    ledger: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = []
    task_names = _task_names(requests)
    normalized = _normalize_ledger(ledger, task_names)
    for label in labels:
        hits = [
            entry
            for entry in normalized
            if _matches(
                label,
                fact=str(entry.get("fact", "")),
                worker=entry.get("worker"),
                task=entry.get("task_name"),
            )
        ]
        first_ledger = min(
            (int(hit["first_observed_timestep"]) for hit in hits), default=None
        )
        first_visible = None
        for timestep, text in requests:
            visible = _visible_resource_facts(text)
            if any(
                (
                    not label.get("task_pattern")
                    or re.search(label["task_pattern"], str(task or ""), re.IGNORECASE)
                )
                and re.search(label["fact_pattern"], fact, re.IGNORECASE)
                for task, fact in visible
            ):
                first_visible = timestep
                break
        rows.append(
            {
                "label_id": label["label_id"],
                "channel": label["channel"],
                "recalled": bool(hits),
                "first_visible_timestep": first_visible,
                "first_ledger_timestep": first_ledger,
                "delay": (
                    first_ledger - first_visible
                    if first_ledger is not None and first_visible is not None
                    else None
                ),
                "matching_evidence_ids": [hit.get("evidence_id") for hit in hits],
            }
        )

    by_channel: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        by_channel[row["channel"]].append(row["recalled"])
    return {
        "labeled_facts": len(rows),
        "recalled_facts": sum(row["recalled"] for row in rows),
        "recall": (sum(row["recalled"] for row in rows) / len(rows) if rows else None),
        "recall_by_channel": {
            channel: sum(values) / len(values) for channel, values in by_channel.items()
        },
        "labels": rows,
    }


def audit_context(requests: list[tuple[int, str]]) -> dict[str, Any]:
    byte_counts = [len(text.encode("utf-8")) for _, text in requests]
    word_counts = [len(text.split()) for _, text in requests]
    return {
        "manager_requests": len(requests),
        "prompt_utf8_bytes": {
            "total": sum(byte_counts),
            "mean": mean(byte_counts) if byte_counts else 0,
            "max": max(byte_counts, default=0),
        },
        "prompt_whitespace_tokens": {
            "total": sum(word_counts),
            "mean": mean(word_counts) if word_counts else 0,
            "max": max(word_counts, default=0),
        },
        "note": (
            "These are realized prompt-text measures, not DeepSeek tokenizer counts; "
            "use the same measure and a preregistered tolerance across arms."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    label_rows = []
    if args.labels:
        label_rows = json.loads(args.labels.read_text())["labels"]

    reports = []
    for run_dir in args.run_dirs:
        trace, ledger = _load_run(run_dir)
        requests = _manager_requests(trace)
        report = {
            "run_dir": str(run_dir),
            "context": audit_context(requests),
            "selection_audit": trace.get("manifest", {}).get(
                "observation_aid_diagnostics"
            ),
        }
        if label_rows:
            report["evidence_recall"] = audit_recall(label_rows, requests, ledger)
        reports.append(report)

    comparison = None
    if len(reports) > 1:
        baseline = reports[0]["context"]["prompt_utf8_bytes"]
        comparison = {
            "baseline": reports[0]["run_dir"],
            "tolerance": 0.10,
            "runs": [],
        }
        for report in reports[1:]:
            current = report["context"]["prompt_utf8_bytes"]
            mean_ratio = (
                current["mean"] / baseline["mean"] if baseline["mean"] else None
            )
            comparison["runs"].append(
                {
                    "run_dir": report["run_dir"],
                    "mean_byte_ratio": mean_ratio,
                    "within_10_percent": (
                        mean_ratio is not None and abs(mean_ratio - 1.0) <= 0.10
                    ),
                }
            )
    payload = {"runs": reports, "context_comparison": comparison}
    rendered = json.dumps(payload, indent=2)
    if args.out:
        args.out.write_text(rendered)
    print(rendered)


if __name__ == "__main__":
    main()
