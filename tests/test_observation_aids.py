from __future__ import annotations

import json
from uuid import uuid4

import pytest

from manager_agent_gym.core.common.llm_interface import LLMInferenceTruncationError
from manager_agent_gym.core.manager_agent.observation_aids import (
    DETERMINISTIC_LEDGER_SPEC_SHA256,
    AppendOnlySummaryLogObservationAid,
    AtomicEvidenceEntry,
    AtomicEvidenceLedgerObservationAid,
    GenericSummaryObservationAid,
    GenericSummaryResponse,
)
from manager_agent_gym.schemas.core.communication import Message
from manager_agent_gym.schemas.execution.manager import ManagerObservation
from manager_agent_gym.schemas.workflow_agents.config import AgentConfig


def _agent(agent_id: str, agent_type: str = "ai") -> AgentConfig:
    return AgentConfig(
        agent_id=agent_id,
        agent_type=agent_type,
        system_prompt="test system prompt",
        model_name="test-model",
        agent_description="test agent",
        agent_capabilities=[],
    )


def _observation(
    *, timestep: int, workflow_summary: str = "", messages: list[Message] | None = None
) -> ManagerObservation:
    return ManagerObservation.model_construct(
        timestep=timestep,
        workflow_summary=workflow_summary,
        recent_messages=messages or [],
        available_agent_metadata=[
            _agent("portfolio_analyst"),
            _agent("stakeholder_balanced", "stakeholder"),
        ],
    )


@pytest.mark.asyncio
async def test_generic_summary_caches_identical_visible_context(monkeypatch) -> None:
    calls = []

    async def fake_generate_structured_response(**kwargs):
        calls.append(kwargs)
        return GenericSummaryResponse(summary=" cached neutral summary ")

    monkeypatch.setattr(
        "manager_agent_gym.core.manager_agent.observation_aids.generate_structured_response",
        fake_generate_structured_response,
    )
    builder = GenericSummaryObservationAid(model="test-model", seed=7)
    observation = _observation(timestep=3)

    first = await builder.build(
        source_text="same visible context", observation=observation
    )
    second = await builder.build(
        source_text="same visible context", observation=observation
    )

    assert first == second == "cached neutral summary"
    assert len(calls) == 1
    assert calls[0]["temperature"] == 0
    assert calls[0]["max_completion_tokens"] == 0


@pytest.mark.asyncio
async def test_generic_summary_failure_returns_empty_aid(monkeypatch) -> None:
    async def fail_generation(**kwargs):
        raise LLMInferenceTruncationError("truncated")

    monkeypatch.setattr(
        "manager_agent_gym.core.manager_agent.observation_aids.generate_structured_response",
        fail_generation,
    )
    result = await GenericSummaryObservationAid(model="test-model", seed=7).build(
        source_text="visible context", observation=_observation(timestep=3)
    )
    assert result == ""


@pytest.mark.asyncio
async def test_summary_log_is_persistence_only_and_append_only(monkeypatch) -> None:
    summaries = iter(["first summary", "second summary"])

    async def fake_generate_structured_response(**kwargs):
        return GenericSummaryResponse(summary=next(summaries))

    monkeypatch.setattr(
        "manager_agent_gym.core.manager_agent.observation_aids.generate_structured_response",
        fake_generate_structured_response,
    )
    builder = AppendOnlySummaryLogObservationAid(model="test-model", seed=7)
    await builder.build(source_text="one", observation=_observation(timestep=1))
    rendered = await builder.build(
        source_text="two", observation=_observation(timestep=2)
    )

    assert json.loads(rendered) == [
        {"timestep": 1, "summary": "first summary"},
        {"timestep": 2, "summary": "second summary"},
    ]
    assert builder.diagnostics()["summary_entries"] == 2


def _completed_summary(task_id: str, resource_id: str, fact: str) -> str:
    return f"""Tasks:
  • Task: Batch A Robust Audit (ID: {task_id})
    Status: completed
    Description: hidden task requirement must not enter the ledger
    Output resources: ['{resource_id}']

Resources:
Resource: result (ID: {resource_id}, type=text/plain)
  Description: Worker-authored result description
  Content stats: words=3, chars=20
  Content preview:
    {fact}
"""


def test_atomic_ledger_schema_is_dimension_free_and_versioned() -> None:
    forbidden = {
        "dimension",
        "polarity",
        "strength",
        "confidence",
        "verification_tier",
        "expected",
        "recommendation",
    }
    assert forbidden.isdisjoint(AtomicEvidenceEntry.model_json_schema()["properties"])
    assert len(DETERMINISTIC_LEDGER_SPEC_SHA256) == 64


@pytest.mark.asyncio
async def test_atomic_ledger_enumerates_all_eligible_lines_without_llm_or_cap(
    monkeypatch,
) -> None:
    async def unexpected_call(**kwargs):  # pragma: no cover
        raise AssertionError("Arm 2 must not call an extractor LLM")

    monkeypatch.setattr(
        "manager_agent_gym.core.manager_agent.observation_aids.generate_structured_response",
        unexpected_call,
    )
    task_id, resource_id = str(uuid4()), str(uuid4())
    lines = "\n    ".join(f"fact-{index}" for index in range(12))
    summary = _completed_summary(task_id, resource_id, lines)
    source = f"Assigned task {task_id} to portfolio_analyst"
    builder = AtomicEvidenceLedgerObservationAid(model="ignored", seed=11)

    rendered = await builder.build(
        source_text=source,
        observation=_observation(timestep=4, workflow_summary=summary),
    )
    entries = json.loads(rendered)

    assert len(entries) == 14  # status + resource description + twelve preview lines
    assert all(entry["worker"] == "portfolio_analyst" for entry in entries)
    assert "hidden task requirement" not in rendered
    assert "Content stats" not in rendered
    diagnostics = builder.diagnostics()
    assert diagnostics["selection_cap"] is None
    assert diagnostics["omitted_facts"] == 0
    assert diagnostics["generation_failures"] == 0


@pytest.mark.asyncio
async def test_atomic_ledger_detects_changes_inside_existing_resource() -> None:
    task_id, resource_id = str(uuid4()), str(uuid4())
    builder = AtomicEvidenceLedgerObservationAid()
    source = f"Assigned task {task_id} to portfolio_analyst"
    await builder.build(
        source_text=source,
        observation=_observation(
            timestep=4,
            workflow_summary=_completed_summary(task_id, resource_id, "metric: 59"),
        ),
    )
    rendered = await builder.build(
        source_text=source,
        observation=_observation(
            timestep=5,
            workflow_summary=_completed_summary(
                task_id, resource_id, "metric: 59\n    details: newly visible"
            ),
        ),
    )

    assert "newly visible" in rendered
    assert builder.snapshot()[-1]["first_observed_timestep"] == 5


@pytest.mark.asyncio
async def test_atomic_ledger_reads_worker_messages_but_not_stakeholder_messages() -> (
    None
):
    builder = AtomicEvidenceLedgerObservationAid()
    task_id = uuid4()
    messages = [
        Message(
            sender_id="portfolio_analyst",
            content="worker evidence",
            related_task_id=task_id,
        ),
        Message(sender_id="stakeholder_balanced", content="stakeholder instruction"),
    ]
    rendered = await builder.build(
        source_text="", observation=_observation(timestep=2, messages=messages)
    )

    assert "worker evidence" in rendered
    assert "stakeholder instruction" not in rendered


@pytest.mark.asyncio
async def test_workflow_summary_content_change_triggers_enumeration() -> None:
    builder = AtomicEvidenceLedgerObservationAid()
    task_id, resource_id = str(uuid4()), str(uuid4())
    await builder.build(
        source_text="",
        observation=_observation(
            timestep=1,
            workflow_summary=_completed_summary(task_id, resource_id, "metric: 1"),
        ),
    )
    await builder.build(
        source_text="",
        observation=_observation(
            timestep=2,
            workflow_summary=_completed_summary(task_id, resource_id, "metric: 2"),
        ),
    )
    assert builder.diagnostics()["enumeration_passes"] == 2
    assert {entry["fact"] for entry in builder.snapshot()} >= {"metric: 1", "metric: 2"}
