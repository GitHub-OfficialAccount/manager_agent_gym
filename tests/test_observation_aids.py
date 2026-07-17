from __future__ import annotations

import pytest

from manager_agent_gym.core.manager_agent.observation_aids import (
    GenericSummaryObservationAid,
    GenericSummaryResponse,
)
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
