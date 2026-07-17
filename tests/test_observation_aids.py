from __future__ import annotations

import pytest

from manager_agent_gym.core.manager_agent.observation_aids import (
    GenericSummaryObservationAid,
    GenericSummaryResponse,
)
from manager_agent_gym.core.common.llm_interface import LLMInferenceTruncationError
from manager_agent_gym.schemas.execution.manager import ManagerObservation


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
    observation = ManagerObservation.model_construct(timestep=3)

    first = await builder.build(
        source_text="same visible context", observation=observation
    )
    second = await builder.build(
        source_text="same visible context", observation=observation
    )

    assert first == second == "cached neutral summary"
    assert len(calls) == 1
    assert calls[0]["model"] == "test-model"
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
    builder = GenericSummaryObservationAid(model="test-model", seed=7)

    result = await builder.build(
        source_text="visible context",
        observation=ManagerObservation.model_construct(timestep=3),
    )

    assert result == ""
