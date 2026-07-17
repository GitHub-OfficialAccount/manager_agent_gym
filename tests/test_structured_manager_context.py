from __future__ import annotations

import pytest

from uuid import uuid4

from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.manager_agent.structured_manager import (
    ChainOfThoughtManagerAgent,
)
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from manager_agent_gym.schemas.execution.state import ExecutionState
from manager_agent_gym.schemas.execution.manager import ManagerObservation
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.execution.manager_actions import NoOpAction
from manager_agent_gym.schemas.workflow_agents.stakeholder import (
    StakeholderPublicProfile,
)
from manager_agent_gym.core.manager_agent.prompts.structured_manager_prompts import (
    STRUCTURED_MANAGER_SYSTEM_PROMPT_TEMPLATE,
)


def test_structured_manager_prompt_has_strategy_neutral_change_prior() -> None:
    assert "Agent characteristics and behavior may evolve" in (
        STRUCTURED_MANAGER_SYSTEM_PROMPT_TEMPLATE
    )
    assert "revisit earlier assumptions when new evidence becomes relevant" in (
        STRUCTURED_MANAGER_SYSTEM_PROMPT_TEMPLATE
    )


class _FakeObservationAidBuilder:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def build(self, *, source_text, observation) -> str:
        self.calls.append(source_text)
        return "neutral visible-evidence summary"


async def _run_manager_step_with_aid(mode: str):
    workflow = Workflow(name="w", workflow_goal="g", owner_id=uuid4())
    manager = ChainOfThoughtManagerAgent(preferences=PreferenceWeights(preferences=[]))
    manager.set_observation_policy(ObservationPolicy(observation_aid=mode))
    builder = _FakeObservationAidBuilder()
    manager.set_observation_aid_builder(builder)
    acted_on = []

    async def fake_take_action(observation):
        acted_on.append(observation)
        return NoOpAction(reasoning="test", success=True, result_summary="test")

    manager.take_action = fake_take_action
    await manager.step(
        workflow=workflow,
        execution_state=ExecutionState.WAITING_FOR_MANAGER,
        stakeholder_profile=StakeholderPublicProfile(
            display_name="S", role="Owner", preference_summary=""
        ),
        current_timestep=0,
        running_tasks={},
        completed_task_ids=set(),
        failed_task_ids=set(),
    )
    return manager, builder, acted_on[0]


@pytest.mark.asyncio
async def test_generic_summary_runs_only_when_selected() -> None:
    _, none_builder, native_observation = await _run_manager_step_with_aid("none")
    assert none_builder.calls == []
    assert native_observation.observation_aid is None

    manager, summary_builder, aided_observation = await _run_manager_step_with_aid(
        "generic_summary"
    )
    assert len(summary_builder.calls) == 1
    assert "Execution Snapshot" in summary_builder.calls[0]
    assert aided_observation.observation_aid == "neutral visible-evidence summary"
    assert manager.get_last_decision_observation() == aided_observation


def test_observation_aid_is_rendered_for_manager() -> None:
    manager = ChainOfThoughtManagerAgent(preferences=PreferenceWeights(preferences=[]))
    # Exercise the rendering contract without invoking an LLM.
    observation = ManagerObservation.model_construct(
        timestep=2,
        workflow_id=uuid4(),
        workflow_summary="workflow",
        execution_state="waiting_for_manager",
        workflow_progress=0.0,
        ready_task_ids=[],
        running_task_ids=[],
        completed_task_ids=[],
        failed_task_ids=[],
        available_agent_metadata=[],
        recent_messages=[],
        constraints=[],
        task_ids=[],
        resource_ids=[],
        agent_ids=[],
        stakeholder_profile=StakeholderPublicProfile(
            display_name="S", role="Owner", preference_summary=""
        ),
        observation_aid="arm-one-summary",
    )
    assert "arm-one-summary" in manager._prepare_context(observation)


@pytest.mark.asyncio
async def test_structured_manager_prompt_includes_stakeholder_messages() -> None:
    # Arrange: minimal workflow and communication service
    workflow = Workflow(
        name="w",
        workflow_goal="g",
        owner_id=uuid4(),
        tasks={},
        resources={},
        agents={},
        messages=[],
    )
    comms = CommunicationService()

    # Manager under test
    manager = ChainOfThoughtManagerAgent(preferences=PreferenceWeights(preferences=[]))

    # Simulate stakeholder sending a direct message to this manager's agent_id
    stake_id = "stakeholder_1"
    target_manager_id = manager.agent_id  # "structured_manager"
    message_text = "stake_msg_123_included"
    await comms.send_direct_message(
        from_agent=stake_id, to_agent=target_manager_id, content=message_text
    )

    # Act: build observation and prepare context prompt
    observation = await manager.create_observation(
        workflow=workflow,
        execution_state=ExecutionState.RUNNING,
        current_timestep=0,
        running_tasks={},
        completed_task_ids=set(),
        failed_task_ids=set(),
        communication_service=comms,
        stakeholder_profile=StakeholderPublicProfile(
            display_name="Test Stakeholder", role="Owner", preference_summary=""
        ),
    )
    observation.max_timesteps = 10

    prompt = manager._prepare_context(
        observation
    )  # Access internal to inspect prompt content
    # Assert: stakeholder message appears in the "Recent Communications (sample)" section
    assert stake_id in prompt
    assert target_manager_id in prompt
    assert message_text in prompt
    # remove debug assertion
