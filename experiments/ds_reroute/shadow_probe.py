"""Run non-intervening belief probes on saved pre-action manager contexts.

This command never resumes or changes an episode. It finds the exact manager
request immediately before selected assignment decisions, makes two independent
structured calls against that saved context, and writes the measurements beside
the run artifacts.

Example:
    uv run python -m experiments.ds_reroute.shadow_probe \
      experiments/ds_reroute/outputs/...seed101 \
      --protocol experiments/ds_reroute/evidence_labels/toolset_seed101.json
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from manager_agent_gym.core.common.llm_interface import generate_structured_response

from .judgment_protocol import (
    CHANGE_PROBE_QUESTION,
    EVIDENCE_PROBE_QUESTION,
    PROBE_SPEC_VERSION,
    SHADOW_SYSTEM_SUFFIX,
    ChangeProbeResponse,
    EvidenceProbeResponse,
    code_probe_outcome,
    load_protocol,
    probe_spec_fingerprint,
)


DEFAULT_POINTS = ("Batch B Robust Audit", "Batch C Robust Audit")
TASK_HEADER_RE = re.compile(r"Task: (.+?) \(ID: ([0-9a-fA-F-]+)\)")


def _manager_request_records(trace: dict[str, Any]) -> dict[int, dict[str, Any]]:
    records: dict[int, dict[str, Any]] = {}
    for event in trace.get("events", []):
        if event.get("event_type") != "structured_llm_request":
            continue
        if event.get("actor_type") != "manager":
            continue
        messages = event.get("payload", {}).get("messages", [])
        system = "\n".join(
            str(message.get("content", ""))
            for message in messages
            if message.get("role") == "system"
        )
        user = "\n".join(
            str(message.get("content", ""))
            for message in messages
            if message.get("role") == "user"
        )
        timestep = int(event.get("timestep") or 0)
        records[timestep] = {
            "timestep": timestep,
            "system": system,
            "user": user,
            "model": event.get("payload", {}).get("model"),
        }
    return records


def _task_names(records: dict[int, dict[str, Any]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for record in records.values():
        for name, task_id in TASK_HEADER_RE.findall(record["user"]):
            names[task_id] = name
    return names


def find_probe_points(
    trace: dict[str, Any], task_names: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Resolve selected assignment actions to their exact saved manager request."""
    records = _manager_request_records(trace)
    names_by_id = _task_names(records)
    selected: dict[str, dict[str, Any]] = {}
    for row in trace.get("manager_actions", []):
        action = row.get("action") or {}
        if action.get("action_type") != "assign_task":
            continue
        task_name = names_by_id.get(str(action.get("task_id")))
        if task_name not in task_names:
            continue
        timestep = int(row["timestep"])
        if timestep not in records:
            raise ValueError(f"No saved manager request for timestep {timestep}")
        selected[task_name] = {
            **records[timestep],
            "task_name": task_name,
            "task_id": str(action.get("task_id")),
            "assigned_agent": action.get("agent_id"),
        }
    missing = [task_name for task_name in task_names if task_name not in selected]
    if missing:
        raise ValueError(f"Could not resolve assignment points: {missing}")
    return [selected[task_name] for task_name in task_names]


def context_fingerprint(record: dict[str, Any]) -> str:
    encoded = json.dumps(
        {"system": record["system"], "user": record["user"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


async def run_shadow_probes(
    *,
    run_dir: Path,
    protocol_path: Path,
    task_names: tuple[str, ...] = DEFAULT_POINTS,
    model_override: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    trace = json.loads((run_dir / "run.json").read_text())
    manifest = json.loads((run_dir / "manifest.json").read_text())
    protocol = load_protocol(protocol_path)
    if protocol.seed != int(manifest["seed"]):
        raise ValueError(
            f"Protocol seed {protocol.seed} does not match run seed {manifest['seed']}"
        )
    points = find_probe_points(trace, task_names)
    target_worker = str(manifest["target_worker"])
    seed = int(manifest["seed"])
    rows = []
    for point in points:
        model = model_override or point["model"] or manifest["final_target_model"]
        base = {
            "task_name": point["task_name"],
            "task_id": point["task_id"],
            "timestep": point["timestep"],
            "assigned_agent": point["assigned_agent"],
            "model": model,
            "seed": seed,
            "context_sha256": context_fingerprint(point),
        }
        if dry_run:
            rows.append({**base, "dry_run": True})
            continue

        system_prompt = f"{point['system']}\n\n{SHADOW_SYSTEM_SUFFIX}"
        change_response = await generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=f"{point['user']}\n\n{CHANGE_PROBE_QUESTION}",
            response_type=ChangeProbeResponse,
            model=model,
            seed=seed,
            temperature=0,
            max_completion_tokens=0,
        )
        # Independent call: same stored context, no response from the first call.
        evidence_response = await generate_structured_response(
            system_prompt=system_prompt,
            user_prompt=f"{point['user']}\n\n{EVIDENCE_PROBE_QUESTION}",
            response_type=EvidenceProbeResponse,
            model=model,
            seed=seed,
            temperature=0,
            max_completion_tokens=0,
        )
        outcome = code_probe_outcome(
            target_worker=target_worker,
            assigned_agent=str(point["assigned_agent"]),
            expected_correct_agents=protocol.expected_correct_agents,
            engagement_patterns=protocol.engagement_patterns,
            change_response=change_response,
            evidence_response=evidence_response,
        )
        rows.append(
            {
                **base,
                "dry_run": False,
                "change_probe": change_response.model_dump(mode="json"),
                "evidence_probe": evidence_response.model_dump(mode="json"),
                "coded_outcome": outcome,
            }
        )

    return {
        "mode": "offline_shadow_probe",
        "non_intervening": True,
        "run_dir": str(run_dir),
        "protocol_path": str(protocol_path),
        "protocol_sha256": protocol.fingerprint(),
        "probe_spec_version": PROBE_SPEC_VERSION,
        "probe_spec_sha256": probe_spec_fingerprint(),
        "probe_points": list(task_names),
        "results": rows,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--points", nargs="+", default=list(DEFAULT_POINTS))
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = await run_shadow_probes(
        run_dir=args.run_dir,
        protocol_path=args.protocol,
        task_names=tuple(args.points),
        model_override=args.model,
        dry_run=args.dry_run,
    )
    out = args.out or args.run_dir / "shadow_probes.json"
    out.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
