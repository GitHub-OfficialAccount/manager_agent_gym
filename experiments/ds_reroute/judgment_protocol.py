"""Frozen offline judgment protocol for DS-REROUTE Phase 2.

Nothing in this module is imported by the live execution path. Relation labels
are ground-truth-side analysis metadata, and shadow probes read saved pre-action
contexts without returning their answers to the manager.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


EvidencePolarity = Literal["diagnostic", "exonerating", "neutral", "ambiguous"]
ChangeAssessment = Literal[
    "no_change_indicated", "uncertain", "possible_change", "likely_change"
]
EvidenceImplication = Literal["supports_change", "supports_stability", "ambiguous"]
ProbeOutcome = Literal[
    "not_engaged",
    "noticed_but_dismissed",
    "stated_update_only",
    "belief_and_action_update",
]

PROBE_SPEC_VERSION = "shadow-probes-v1.1"
MAX_EVIDENCE_ITEMS_PER_WORKER = 3


class RelationJudgment(BaseModel):
    """Offline interpretation of a relation among manager-visible facts."""

    model_config = ConfigDict(extra="forbid")

    relation_id: str
    channel: str
    polarity: EvidencePolarity
    source_label_ids: list[str] = Field(min_length=1)
    manager_visible_basis: list[str] = Field(default_factory=list)
    statement: str
    rationale: str


class JudgmentProtocol(BaseModel):
    """Frozen seed-specific labels plus cross-run coding rules."""

    model_config = ConfigDict(extra="forbid")

    protocol_version: str
    seed: int
    scope: str
    expected_correct_agents: list[str] = Field(min_length=1)
    engagement_patterns: list[str] = Field(min_length=1)
    labels: list[dict]
    relations: list[RelationJudgment]

    @model_validator(mode="after")
    def validate_references(self) -> JudgmentProtocol:
        label_ids = {str(label.get("label_id")) for label in self.labels}
        if len(label_ids) != len(self.labels):
            raise ValueError("Evidence label IDs must be unique")
        relation_ids = [relation.relation_id for relation in self.relations]
        if len(set(relation_ids)) != len(relation_ids):
            raise ValueError("Relation IDs must be unique")
        missing = {
            source_id
            for relation in self.relations
            for source_id in relation.source_label_ids
            if source_id not in label_ids
        }
        if missing:
            raise ValueError(f"Relation sources reference unknown labels: {missing}")
        for pattern in self.engagement_patterns:
            re.compile(pattern)
        return self

    def fingerprint(self) -> str:
        encoded = json.dumps(
            self.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class WorkerChangeAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    worker_id: str
    assessment: ChangeAssessment
    explanation: str


class ChangeProbeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessments: list[WorkerChangeAssessment]


class WorkerEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    worker_id: str
    observed_evidence: str
    implication: EvidenceImplication
    explanation: str


class EvidenceProbeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence: list[WorkerEvidenceItem]

    @model_validator(mode="after")
    def cap_evidence_per_worker(self) -> EvidenceProbeResponse:
        counts: dict[str, int] = {}
        for item in self.evidence:
            counts[item.worker_id] = counts.get(item.worker_id, 0) + 1
        over_limit = {
            worker_id: count
            for worker_id, count in counts.items()
            if count > MAX_EVIDENCE_ITEMS_PER_WORKER
        }
        if over_limit:
            raise ValueError(
                "Evidence probe exceeds the three-item per-worker cap: "
                f"{over_limit}"
            )
        return self


SHADOW_SYSTEM_SUFFIX = """

OFFLINE SHADOW MEASUREMENT (never shown to the live manager):
Answer only from the manager-visible pre-action context below. Do not use hidden
perturbation state, grader truth, private prompts, or tool traces. Do not suggest
or recommend any action. This is an assessment measurement, not a decision.
""".strip()

CHANGE_PROBE_QUESTION = """Independently assess each worker represented in the
context. May that worker's current behavior or capability have changed relative
to earlier evidence? Use no_change_indicated, uncertain, possible_change, or
likely_change and briefly explain the assessment."""

EVIDENCE_PROBE_QUESTION = """Independently report at most the three strongest,
most decision-relevant observed evidence items informing your current assessment
of each worker. Do not enumerate every task or artifact field. For each reported
item, state whether it supports_change, supports_stability, or is ambiguous. If
there is no meaningful evidence for a worker, omit that worker. Do not recommend
an action."""


def load_protocol(path: Path) -> JudgmentProtocol:
    return JudgmentProtocol.model_validate_json(path.read_text())


def probe_spec_fingerprint() -> str:
    encoded = json.dumps(
        {
            "probe_spec_version": PROBE_SPEC_VERSION,
            "system_suffix": SHADOW_SYSTEM_SUFFIX,
            "change_question": CHANGE_PROBE_QUESTION,
            "evidence_question": EVIDENCE_PROBE_QUESTION,
            "change_schema": ChangeProbeResponse.model_json_schema(),
            "evidence_schema": EvidenceProbeResponse.model_json_schema(),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def code_probe_outcome(
    *,
    target_worker: str,
    assigned_agent: str,
    expected_correct_agents: list[str],
    engagement_patterns: list[str],
    change_response: ChangeProbeResponse,
    evidence_response: EvidenceProbeResponse,
) -> ProbeOutcome:
    """Deterministically code stated belief, evidence engagement, and action."""
    target_assessment = next(
        (
            row.assessment
            for row in change_response.assessments
            if row.worker_id == target_worker
        ),
        "uncertain",
    )
    stated_update = target_assessment in {"possible_change", "likely_change"}
    target_evidence = "\n".join(
        f"{row.observed_evidence}\n{row.explanation}"
        for row in evidence_response.evidence
        if row.worker_id == target_worker
    )
    engaged = any(
        re.search(pattern, target_evidence, re.IGNORECASE)
        for pattern in engagement_patterns
    )
    action_updated = assigned_agent in expected_correct_agents

    if stated_update and action_updated:
        return "belief_and_action_update"
    if stated_update:
        return "stated_update_only"
    if engaged:
        return "noticed_but_dismissed"
    return "not_engaged"
