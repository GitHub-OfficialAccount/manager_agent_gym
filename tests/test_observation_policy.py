import pytest
from uuid import uuid4

from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.manager_agent.interface import ManagerAgent
from manager_agent_gym.core.workflow_agents.interface import AgentInterface
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.execution.manager import ManagerObservation
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.execution.state import ExecutionState
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from manager_agent_gym.schemas.workflow_agents import AgentConfig
from manager_agent_gym.schemas.workflow_agents.stakeholder import (
    StakeholderPublicProfile,
)


class _Worker(AgentInterface[AgentConfig]):
    def __init__(self, aid: str) -> None:
        super().__init__(
            AgentConfig(
                agent_id=aid,
                agent_type="ai",
                system_prompt="SECRET WORKER POLICY",
                model_name="gpt-4o",
                agent_description="a diligent analyst",
                agent_capabilities=["analysis", "drafting"],
            )
        )

    async def execute_task(self, task, resources):  # pragma: no cover
        raise NotImplementedError


class _Mgr(ManagerAgent):
    def __init__(self):
        super().__init__(agent_id="m", preferences=PreferenceWeights(preferences=[]))

    async def take_action(self, observation: ManagerObservation):  # pragma: no cover
        raise NotImplementedError

    async def step(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError

    def reset(self) -> None:
        pass


async def _observe(mgr: _Mgr, workflow: Workflow, svc=None) -> ManagerObservation:
    return await mgr.create_observation(
        workflow=workflow,
        execution_state=ExecutionState.RUNNING,
        stakeholder_profile=StakeholderPublicProfile(
            display_name="S", role="Owner", preference_summary=""
        ),
        current_timestep=0,
        running_tasks={},
        completed_task_ids=set(),
        failed_task_ids=set(),
        communication_service=svc,
    )


@pytest.mark.asyncio
async def test_system_prompts_redacted_by_default() -> None:
    w = Workflow(name="w", workflow_goal="g", owner_id=uuid4())
    w.add_agent(_Worker("w1"))
    obs = await _observe(_Mgr(), w)

    assert len(obs.available_agent_metadata) == 1
    cfg = obs.available_agent_metadata[0]
    assert cfg.system_prompt == "[REDACTED]"
    # capability metadata preserved at default level
    assert cfg.agent_description == "a diligent analyst"
    assert cfg.agent_capabilities == ["analysis", "drafting"]


@pytest.mark.asyncio
async def test_expose_system_prompts_opt_in() -> None:
    w = Workflow(name="w", workflow_goal="g", owner_id=uuid4())
    w.add_agent(_Worker("w1"))
    mgr = _Mgr()
    mgr.set_observation_policy(ObservationPolicy(expose_worker_system_prompts=True))
    obs = await _observe(mgr, w)
    assert obs.available_agent_metadata[0].system_prompt == "SECRET WORKER POLICY"


@pytest.mark.asyncio
async def test_id_only_metadata_level() -> None:
    w = Workflow(name="w", workflow_goal="g", owner_id=uuid4())
    w.add_agent(_Worker("w1"))
    mgr = _Mgr()
    mgr.set_observation_policy(ObservationPolicy(worker_metadata="id_only"))
    obs = await _observe(mgr, w)
    cfg = obs.available_agent_metadata[0]
    assert cfg.agent_id == "w1"
    assert cfg.agent_description == ""
    assert cfg.agent_capabilities == []
    assert cfg.system_prompt == "[REDACTED]"


@pytest.mark.asyncio
async def test_message_window_applied() -> None:
    w = Workflow(name="w", workflow_goal="g", owner_id=uuid4())
    svc = CommunicationService()
    for i in range(5):
        await svc.send_direct_message("a", "m", f"msg-{i}")

    mgr = _Mgr()
    mgr.set_observation_policy(ObservationPolicy(message_window=2))
    obs = await _observe(mgr, w, svc=svc)
    assert len(obs.recent_messages) == 2
    # newest-first: the latest message must be included
    assert obs.recent_messages[0].content == "msg-4"

    mgr.set_observation_policy(ObservationPolicy(message_window=0))
    obs = await _observe(mgr, w, svc=svc)
    assert obs.recent_messages == []


def test_redaction_does_not_mutate_original() -> None:
    worker = _Worker("w1")
    policy = ObservationPolicy()
    redacted = policy.redact_agent_config(worker.config)
    assert redacted.system_prompt == "[REDACTED]"
    assert worker.config.system_prompt == "SECRET WORKER POLICY"
