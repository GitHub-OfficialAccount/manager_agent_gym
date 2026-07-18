"""Information-preserving representations of manager-visible observations."""

from __future__ import annotations

import hashlib
import json
import re
from ast import literal_eval
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ...schemas.execution import ManagerObservation
from ..common.llm_interface import (
    LLMInferenceTruncationError,
    generate_structured_response,
)
from ..common.run_trace import record_run_event, trace_scope


GENERIC_SUMMARY_SYSTEM_PROMPT = """You are a neutral workflow summarizer.
Summarize only evidence present in the supplied manager-visible text. Preserve
concrete outcomes, reported methods, disagreements, failures, and recent changes.
Do not assess worker competence, assign suspicion, infer an intervention or hidden
change, recommend an action, or introduce facts. Missing or absent events may not
be invented. Keep the summary concise (at most 250 words)."""


class GenericSummaryResponse(BaseModel):
    summary: str = Field(description="Neutral summary of the supplied visible evidence")


class GenericSummaryObservationAid:
    """Generic Arm-1 summarizer with exact-input caching and trace records."""

    def __init__(self, *, model: str, seed: int) -> None:
        self.model = model
        self.seed = seed
        self._cache: dict[str, str] = {}

    async def build(self, *, source_text: str, observation: ManagerObservation) -> str:
        fingerprint = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        cached = self._cache.get(fingerprint)
        if cached is not None:
            record_run_event(
                "observation_aid_cache_hit",
                {
                    "mode": "generic_summary",
                    "source_fingerprint": fingerprint,
                    "summary": cached,
                },
                timestep=observation.timestep,
                actor_type="observation_aid",
                actor_id="generic_summary",
            )
            return cached

        try:
            with trace_scope(
                timestep=observation.timestep,
                actor_type="observation_aid",
                actor_id="generic_summary",
                operation="summarize_visible_evidence",
            ):
                response = await generate_structured_response(
                    system_prompt=GENERIC_SUMMARY_SYSTEM_PROMPT,
                    user_prompt=source_text,
                    response_type=GenericSummaryResponse,
                    model=self.model,
                    seed=self.seed,
                    temperature=0,
                    max_completion_tokens=0,
                )
        except LLMInferenceTruncationError as error:
            record_run_event(
                "observation_aid_failed",
                {
                    "mode": "generic_summary",
                    "model": self.model,
                    "source_fingerprint": fingerprint,
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "invalidates_arm": True,
                },
                timestep=observation.timestep,
                actor_type="observation_aid",
                actor_id="generic_summary",
            )
            return ""
        summary = response.summary.strip()
        self._cache[fingerprint] = summary
        record_run_event(
            "observation_aid_generated",
            {
                "mode": "generic_summary",
                "model": self.model,
                "source_fingerprint": fingerprint,
                "source_text": source_text,
                "summary": summary,
            },
            timestep=observation.timestep,
            actor_type="observation_aid",
            actor_id="generic_summary",
        )
        return summary


class SummaryLogEntry(BaseModel):
    """One free-form summary retained by the persistence-only comparison arm."""

    model_config = ConfigDict(extra="forbid")

    timestep: int
    summary: str


class AppendOnlySummaryLogObservationAid:
    """Persistence-only control: append every Arm-1 summary without atomization."""

    def __init__(self, *, model: str, seed: int) -> None:
        self.model = model
        self.seed = seed
        self._entries: list[SummaryLogEntry] = []
        self._failures = 0
        self._max_rendered_chars = 0

    def snapshot(self) -> list[dict[str, Any]]:
        return [entry.model_dump(mode="json") for entry in self._entries]

    def _render(self) -> str:
        rendered = json.dumps(
            self.snapshot(), separators=(",", ":"), ensure_ascii=False
        )
        self._max_rendered_chars = max(self._max_rendered_chars, len(rendered))
        return rendered

    def diagnostics(self) -> dict[str, Any]:
        return {
            "mode": "append_only_summary_log",
            "model": self.model,
            "summary_entries": len(self._entries),
            "generation_failures": self._failures,
            "max_rendered_chars": self._max_rendered_chars,
            "invalidates_arm": self._failures > 0,
        }

    async def build(self, *, source_text: str, observation: ManagerObservation) -> str:
        try:
            with trace_scope(
                timestep=observation.timestep,
                actor_type="observation_aid",
                actor_id="append_only_summary_log",
                operation="summarize_visible_evidence",
            ):
                response = await generate_structured_response(
                    system_prompt=GENERIC_SUMMARY_SYSTEM_PROMPT,
                    user_prompt=source_text,
                    response_type=GenericSummaryResponse,
                    model=self.model,
                    seed=self.seed,
                    temperature=0,
                    max_completion_tokens=0,
                )
        except LLMInferenceTruncationError as error:
            self._failures += 1
            record_run_event(
                "observation_aid_failed",
                {
                    "mode": "append_only_summary_log",
                    "model": self.model,
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "invalidates_arm": True,
                },
                timestep=observation.timestep,
                actor_type="observation_aid",
                actor_id="append_only_summary_log",
            )
            return self._render()

        entry = SummaryLogEntry(
            timestep=observation.timestep,
            summary=response.summary.strip(),
        )
        self._entries.append(entry)
        record_run_event(
            "observation_aid_summary_log_updated",
            {
                "mode": "append_only_summary_log",
                "entry": entry,
                "entry_count": len(self._entries),
            },
            timestep=observation.timestep,
            actor_type="observation_aid",
            actor_id="append_only_summary_log",
        )
        return self._render()


DETERMINISTIC_LEDGER_SPEC = """atomic-lines-v2
Candidate universe:
1. completion/failure status for newly observed completed or failed tasks;
2. description and every visible content-preview line of every worker-produced
   resource, including newly visible lines when an existing resource block changes;
3. the manager-visible 140-character preview of every new worker message.
Excluded: task requirements/descriptions, workflow budget/progress, manager and
stakeholder behavior, resource statistics, and any inferred absence/comparison.
Every candidate is appended. There is no selector, ranking, classifier, or cap.
"""
DETERMINISTIC_LEDGER_VERSION = "atomic-lines-v2"
DETERMINISTIC_LEDGER_SPEC_SHA256 = hashlib.sha256(
    DETERMINISTIC_LEDGER_SPEC.encode("utf-8")
).hexdigest()


class AtomicEvidenceEntry(BaseModel):
    """Immutable dimension-free record; ``fact`` is verbatim visible text."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    first_observed_timestep: int
    worker: str | None = None
    task: str | None = None
    fact: str
    source_pointer: str


class _TaskView(BaseModel):
    task_id: str
    task_name: str
    status: str | None = None
    output_resource_ids: list[str] = Field(default_factory=list)
    failure_facts: list[str] = Field(default_factory=list)


class _ResourceView(BaseModel):
    resource_id: str
    facts: list[str] = Field(default_factory=list)


_TASK_HEADER_RE = re.compile(r"^\s*• Task: (.+) \(ID: ([^)]+)\)\s*$")
_RESOURCE_HEADER_RE = re.compile(r"^Resource: .+ \(ID: ([^,]+), type=.*\)\s*$")
_ASSIGNMENT_RE = re.compile(r"Assigned task ([0-9a-fA-F-]+) to ([A-Za-z0-9_.-]+)")


def _parse_list(text: str) -> list[str]:
    try:
        value = literal_eval(text)
    except (SyntaxError, ValueError):
        return []
    return [str(item) for item in value] if isinstance(value, list) else []


def _parse_workflow_summary(
    workflow_summary: str,
) -> tuple[dict[str, _TaskView], dict[str, _ResourceView]]:
    """Parse only fields rendered in the native manager workflow summary."""
    lines = workflow_summary.splitlines()
    tasks: dict[str, _TaskView] = {}
    resources: dict[str, _ResourceView] = {}

    current_task: _TaskView | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        task_match = _TASK_HEADER_RE.match(line)
        if task_match:
            current_task = _TaskView(
                task_name=task_match.group(1), task_id=task_match.group(2)
            )
            tasks[current_task.task_id] = current_task
            index += 1
            continue
        if line.strip() == "Resources:":
            current_task = None
        if current_task is not None:
            stripped = line.strip()
            if stripped.startswith("Status:"):
                current_task.status = stripped.removeprefix("Status:").strip()
            elif stripped.startswith("Output resources:"):
                current_task.output_resource_ids = _parse_list(
                    stripped.removeprefix("Output resources:").strip()
                )
            elif stripped.startswith("Failure notes"):
                note_index = index + 1
                while note_index < len(lines):
                    note = lines[note_index].strip()
                    if not note.startswith("-"):
                        break
                    current_task.failure_facts.append(note)
                    note_index += 1

        resource_match = _RESOURCE_HEADER_RE.match(line)
        if resource_match:
            resource_id = resource_match.group(1)
            resource = _ResourceView(resource_id=resource_id)
            resources[resource_id] = resource
            index += 1
            while index < len(lines):
                resource_line = lines[index]
                if _RESOURCE_HEADER_RE.match(resource_line):
                    index -= 1
                    break
                stripped = resource_line.strip()
                if stripped.startswith("Description:"):
                    resource.facts.append(stripped)
                elif stripped == "Content preview:":
                    index += 1
                    while index < len(lines):
                        content_line = lines[index]
                        if _RESOURCE_HEADER_RE.match(content_line):
                            index -= 1
                            break
                        # Resource previews are indented by four spaces. A line
                        # without that indent belongs to the outer prompt.
                        if not content_line.startswith("    "):
                            index -= 1
                            break
                        fact = content_line.strip()
                        if fact:
                            resource.facts.append(fact)
                        index += 1
                index += 1
        index += 1
    return tasks, resources


class AtomicEvidenceLedgerObservationAid:
    """Deterministic append-only Arm-2 ledger with a complete candidate audit."""

    def __init__(self, *, model: str | None = None, seed: int | None = None) -> None:
        # Accepted for a stable runner interface; no model is invoked by Arm 2.
        self.model = model
        self.seed = seed
        self._ledger: list[AtomicEvidenceEntry] = []
        self._evidence_keys: set[tuple[str, str, str | None, str | None]] = set()
        self._task_workers: dict[str, str] = {}
        self._seen_message_ids: set[str] = set()
        self._last_fingerprint: str | None = None
        self._enumeration_passes = 0
        self._candidate_count = 0
        self._max_rendered_chars = 0

    def snapshot(self) -> list[dict[str, Any]]:
        return [entry.model_dump(mode="json") for entry in self._ledger]

    def diagnostics(self) -> dict[str, Any]:
        return {
            "mode": "atomic_evidence_ledger",
            "extractor_version": DETERMINISTIC_LEDGER_VERSION,
            "extractor_spec_sha256": DETERMINISTIC_LEDGER_SPEC_SHA256,
            "ledger_entries": len(self._ledger),
            "enumeration_passes": self._enumeration_passes,
            "candidate_facts": self._candidate_count,
            "omitted_facts": 0,
            "selection_cap": None,
            "generation_failures": 0,
            "grounding_rejections": 0,
            "max_rendered_chars": self._max_rendered_chars,
            "invalidates_arm": False,
        }

    def _render(self) -> str:
        compact = [
            {
                "id": entry.evidence_id,
                "t": entry.first_observed_timestep,
                "worker": entry.worker,
                "task": entry.task,
                "source": entry.source_pointer,
                "fact": entry.fact,
            }
            for entry in self._ledger
        ]
        rendered = json.dumps(compact, separators=(",", ":"), ensure_ascii=False)
        self._max_rendered_chars = max(self._max_rendered_chars, len(rendered))
        return rendered

    @staticmethod
    def _fingerprint(observation: ManagerObservation) -> str:
        # Hash the entire second ambient channel plus visible messages. Parsing
        # remains restricted to the declared candidate universe below.
        payload = {
            "workflow_summary": observation.workflow_summary,
            "recent_messages": [
                message.model_dump(mode="json")
                for message in observation.recent_messages
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _append(
        self,
        *,
        timestep: int,
        worker: str | None,
        task: str | None,
        fact: str,
        source_pointer: str,
    ) -> AtomicEvidenceEntry | None:
        key = (source_pointer, fact, worker, task)
        if key in self._evidence_keys:
            return None
        entry = AtomicEvidenceEntry(
            evidence_id=f"e{len(self._ledger) + 1}",
            first_observed_timestep=timestep,
            worker=worker,
            task=task,
            fact=fact,
            source_pointer=source_pointer,
        )
        self._evidence_keys.add(key)
        self._ledger.append(entry)
        return entry

    async def build(self, *, source_text: str, observation: ManagerObservation) -> str:
        fingerprint = self._fingerprint(observation)
        for task_id, worker in _ASSIGNMENT_RE.findall(source_text):
            self._task_workers[task_id] = worker

        if fingerprint == self._last_fingerprint:
            record_run_event(
                "observation_aid_ledger_unchanged",
                {
                    "mode": "atomic_evidence_ledger",
                    "fingerprint": fingerprint,
                    "ledger_size": len(self._ledger),
                },
                timestep=observation.timestep,
                actor_type="observation_aid",
                actor_id="atomic_evidence_ledger",
            )
            return self._render()

        self._enumeration_passes += 1
        tasks, resources = _parse_workflow_summary(observation.workflow_summary)
        resource_to_task: dict[str, _TaskView] = {}
        candidates: list[dict[str, Any]] = []
        for task in tasks.values():
            for resource_id in task.output_resource_ids:
                resource_to_task[resource_id] = task
            if task.status in {"completed", "failed"}:
                candidates.append(
                    {
                        "worker": self._task_workers.get(task.task_id),
                        "task": task.task_name,
                        "fact": f"Status: {task.status}",
                        "source_pointer": task.task_id,
                    }
                )
            if task.status == "failed":
                for fact in task.failure_facts:
                    candidates.append(
                        {
                            "worker": self._task_workers.get(task.task_id),
                            "task": task.task_name,
                            "fact": fact,
                            "source_pointer": task.task_id,
                        }
                    )

        for resource in resources.values():
            task = resource_to_task.get(resource.resource_id)
            task_id = task.task_id if task is not None else None
            for fact in resource.facts:
                candidates.append(
                    {
                        "worker": self._task_workers.get(task_id) if task_id else None,
                        "task": task.task_name if task is not None else None,
                        "fact": fact,
                        "source_pointer": resource.resource_id,
                    }
                )

        worker_ids = {
            config.agent_id
            for config in observation.available_agent_metadata
            if config.agent_type != "stakeholder"
        }
        for message in observation.recent_messages:
            message_id = str(message.message_id)
            if (
                message_id in self._seen_message_ids
                or message.sender_id not in worker_ids
            ):
                continue
            self._seen_message_ids.add(message_id)
            fact = (
                message.content[:140] + "…"
                if len(message.content) > 140
                else message.content
            )
            candidates.append(
                {
                    "worker": message.sender_id,
                    "task": (
                        tasks[str(message.related_task_id)].task_name
                        if message.related_task_id is not None
                        and str(message.related_task_id) in tasks
                        else (
                            str(message.related_task_id)
                            if message.related_task_id is not None
                            else None
                        )
                    ),
                    "fact": fact,
                    "source_pointer": message_id,
                }
            )

        accepted: list[AtomicEvidenceEntry] = []
        for candidate in candidates:
            entry = self._append(timestep=observation.timestep, **candidate)
            if entry is not None:
                accepted.append(entry)
        self._candidate_count += len(candidates)
        self._last_fingerprint = fingerprint
        record_run_event(
            "observation_aid_ledger_updated",
            {
                "mode": "atomic_evidence_ledger",
                "extractor_version": DETERMINISTIC_LEDGER_VERSION,
                "extractor_spec_sha256": DETERMINISTIC_LEDGER_SPEC_SHA256,
                "fingerprint": fingerprint,
                "candidate_count": len(candidates),
                "candidates": candidates,
                "accepted": accepted,
                "duplicates": len(candidates) - len(accepted),
                "omitted": [],
                "selection_cap": None,
                "ledger_size": len(self._ledger),
                "invalidates_arm": False,
            },
            timestep=observation.timestep,
            actor_type="observation_aid",
            actor_id="atomic_evidence_ledger",
        )
        return self._render()
