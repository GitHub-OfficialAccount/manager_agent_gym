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

from .judgment_protocol import JudgmentProtocol, load_protocol
from .shadow_probe import DEFAULT_POINTS, context_fingerprint, find_probe_points


TASK_HEADER_RE = re.compile(r"Task: (.+?) \(ID: ([0-9a-fA-F-]+)\)")
MATCHER_VERSION = "serialization-normalization-v1"
QUOTED_FIELD_RE = re.compile(
    r'''(?P<quote>["'])(?P<field>[A-Za-z_][A-Za-z0-9_-]*)(?P=quote)\s*:'''
)
Z_SCORE_VARIANT_RE = re.compile(r"\bz[\s‐‑‒–—-]*score\b", re.IGNORECASE)


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


def _normalize_fact_serialization(fact: str) -> str:
    """Normalize orthographic variants without changing evidence semantics."""
    normalized = QUOTED_FIELD_RE.sub(
        lambda match: f"{match.group('field')}:", fact
    )
    return Z_SCORE_VARIANT_RE.sub("zscore", normalized)


def _matches_fact_pattern(pattern: str, fact: str) -> bool:
    return bool(
        re.search(pattern, fact, re.IGNORECASE)
        or re.search(
            pattern, _normalize_fact_serialization(fact), re.IGNORECASE
        )
    )


def _matches(label: dict[str, Any], *, fact: str, worker: Any, task: Any) -> bool:
    if label.get("worker") and label["worker"] != worker:
        return False
    if label.get("task_pattern") and not re.search(
        label["task_pattern"], str(task or ""), re.IGNORECASE
    ):
        return False
    return _matches_fact_pattern(label["fact_pattern"], fact)


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
                and _matches_fact_pattern(label["fact_pattern"], fact)
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
        "matcher_version": MATCHER_VERSION,
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


def audit_relations(
    protocol: JudgmentProtocol, recall: dict[str, Any]
) -> dict[str, Any]:
    labels = {row["label_id"]: row for row in recall["labels"]}
    rows = []
    for relation in protocol.relations:
        sources = [labels[source_id] for source_id in relation.source_label_ids]
        first_visible = (
            max(row["first_visible_timestep"] for row in sources)
            if all(row["first_visible_timestep"] is not None for row in sources)
            else None
        )
        first_ledger = (
            max(row["first_ledger_timestep"] for row in sources)
            if all(row["first_ledger_timestep"] is not None for row in sources)
            else None
        )
        rows.append(
            {
                **relation.model_dump(mode="json"),
                "visible_in_native_context": first_visible is not None,
                "recalled_in_ledger": first_ledger is not None,
                "first_visible_timestep": first_visible,
                "first_ledger_timestep": first_ledger,
            }
        )
    return {
        "protocol_version": protocol.protocol_version,
        "protocol_sha256": protocol.fingerprint(),
        "relations": rows,
    }


def _routing_vector(
    trace: dict[str, Any], requests: list[tuple[int, str]], protocol: JudgmentProtocol
) -> list[dict[str, Any]]:
    names_by_id = _task_names(requests)
    rows = []
    for action_row in trace.get("manager_actions", []):
        action = action_row.get("action") or {}
        if action.get("action_type") != "assign_task":
            continue
        task_name = names_by_id.get(str(action.get("task_id")))
        if task_name is None or not re.fullmatch(
            r"Batch [ABC] Robust Audit", task_name
        ):
            continue
        rows.append(
            {
                "task_name": task_name,
                "timestep": int(action_row["timestep"]),
                "assigned_agent": action.get("agent_id"),
                "correct_route": action.get("agent_id")
                in protocol.expected_correct_agents,
            }
        )
    return sorted(rows, key=lambda row: row["task_name"])


def audit_decision_points(
    trace: dict[str, Any],
    requests: list[tuple[int, str]],
    protocol: JudgmentProtocol,
    relations: dict[str, Any],
    shadow_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    points = find_probe_points(trace, DEFAULT_POINTS)
    shadow_by_task = {
        row["task_name"]: row for row in (shadow_payload or {}).get("results", [])
    }
    relation_rows = relations["relations"]
    audited = []
    for point in points:
        text = f"{point['system']}\n{point['user']}"
        timestep = int(point["timestep"])
        visible_relations = [
            relation
            for relation in relation_rows
            if relation["first_visible_timestep"] is not None
            and relation["first_visible_timestep"] <= timestep
        ]
        diagnostic = [
            relation["relation_id"]
            for relation in visible_relations
            if relation["polarity"] == "diagnostic"
        ]
        audited.append(
            {
                "task_name": point["task_name"],
                "timestep": timestep,
                "assigned_agent": point["assigned_agent"],
                "correct_route": point["assigned_agent"]
                in protocol.expected_correct_agents,
                "informative_evidence_available": bool(diagnostic),
                "visible_diagnostic_relations": diagnostic,
                "visible_exonerating_relations": [
                    relation["relation_id"]
                    for relation in visible_relations
                    if relation["polarity"] == "exonerating"
                ],
                "prompt_utf8_bytes": len(text.encode("utf-8")),
                "prompt_whitespace_tokens": len(text.split()),
                "context_sha256": context_fingerprint(point),
                "shadow_probe": (
                    shadow_by_task.get(point["task_name"])
                    if shadow_by_task.get(point["task_name"], {}).get("context_sha256")
                    == context_fingerprint(point)
                    else None
                ),
            }
        )
    routing = _routing_vector(trace, requests, protocol)
    for route in routing:
        visible_diagnostic = any(
            relation["polarity"] == "diagnostic"
            and relation["first_visible_timestep"] is not None
            and relation["first_visible_timestep"] <= route["timestep"]
            for relation in relation_rows
        )
        route["informative_evidence_available"] = visible_diagnostic
        route["correction_opportunity"] = visible_diagnostic
    opportunities = [row for row in routing if row["correction_opportunity"]]
    return {
        "points": audited,
        "robust_audit_routing_vector": routing,
        "corrective_routes": sum(row["correct_route"] for row in opportunities),
        "correction_opportunities": len(opportunities),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    protocol = None
    label_rows = []
    if args.labels:
        protocol = load_protocol(args.labels)
        label_rows = protocol.labels

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
            recall = audit_recall(label_rows, requests, ledger)
            relations = audit_relations(protocol, recall)
            shadow_path = run_dir / "shadow_probes.json"
            shadow_payload = (
                json.loads(shadow_path.read_text()) if shadow_path.exists() else None
            )
            if (
                shadow_payload is not None
                and shadow_payload.get("protocol_sha256") != protocol.fingerprint()
            ):
                raise ValueError(f"Shadow-probe protocol mismatch in {shadow_path}")
            report["evidence_recall"] = recall
            report["relation_judgments"] = relations
            report["decision_audit"] = audit_decision_points(
                trace, requests, protocol, relations, shadow_payload
            )
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
        if protocol is not None:
            baseline_points = {
                row["task_name"]: row for row in reports[0]["decision_audit"]["points"]
            }
            for comparison_row, report in zip(
                comparison["runs"], reports[1:], strict=True
            ):
                point_rows = []
                for point in report["decision_audit"]["points"]:
                    baseline_point = baseline_points[point["task_name"]]
                    ratio = (
                        point["prompt_utf8_bytes"] / baseline_point["prompt_utf8_bytes"]
                    )
                    point_rows.append(
                        {
                            "task_name": point["task_name"],
                            "byte_ratio": ratio,
                            "within_10_percent": abs(ratio - 1.0) <= 0.10,
                        }
                    )
                max_ratio = (
                    report["context"]["prompt_utf8_bytes"]["max"] / baseline["max"]
                    if baseline["max"]
                    else None
                )
                comparison_row["decision_points"] = point_rows
                comparison_row["max_byte_ratio"] = max_ratio
                comparison_row["max_within_10_percent"] = (
                    max_ratio is not None and abs(max_ratio - 1.0) <= 0.10
                )
                comparison_row["passes_ladder_budget_gate"] = (
                    comparison_row["within_10_percent"]
                    and comparison_row["max_within_10_percent"]
                    and all(row["within_10_percent"] for row in point_rows)
                )
    payload = {"runs": reports, "context_comparison": comparison}
    rendered = json.dumps(payload, indent=2)
    if args.out:
        args.out.write_text(rendered)
    print(rendered)


if __name__ == "__main__":
    main()
