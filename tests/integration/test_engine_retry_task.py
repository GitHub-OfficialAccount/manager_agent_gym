from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from manager_agent_gym.core.execution.engine import WorkflowExecutionEngine
from manager_agent_gym.core.manager_agent.interface import ManagerAgent
from manager_agent_gym.core.workflow_agents.interface import AgentInterface
from manager_agent_gym.core.workflow_agents.registry import AgentRegistry
from manager_agent_gym.schemas.core.base import TaskStatus
from manager_agent_gym.schemas.core.resources import Resource
from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.execution.manager_actions import (
    NoOpAction,
    RetryTaskAction,
)
from manager_agent_gym.schemas.execution.state import ExecutionState
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from manager_agent_gym.schemas.unified_results import create_task_result
from manager_agent_gym.schemas.workflow_agents import AgentConfig
from manager_agent_gym.schemas.workflow_agents.stakeholder import (
    StakeholderPublicProfile,
)
from tests.helpers.stubs import StakeholderStub


class _FailOnceAgent(AgentInterface[AgentConfig]):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                agent_id="fail_once",
                agent_type="ai",
                system_prompt="Fail once, then succeed.",
                model_name="none",
                agent_description="Retry test worker",
                agent_capabilities=["retry test"],
            )
        )
        self.calls = 0

    async def execute_task(self, task: Task, resources: list[Resource]):
        self.calls += 1
        return create_task_result(
            task_id=task.id,
            agent_id=self.agent_id,
            success=self.calls > 1,
            execution_time=0.0,
            resources=[],
            error="first attempt failed" if self.calls == 1 else None,
        )


class _RetryFailedManager(ManagerAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_id="retry_manager",
            preferences=PreferenceWeights(preferences=[]),
        )

    async def step(
        self,
        workflow: Workflow,
        execution_state: ExecutionState,
        stakeholder_profile: StakeholderPublicProfile,
        current_timestep: int,
        running_tasks: dict,
        completed_task_ids: set[UUID],
        failed_task_ids: set[UUID],
        communication_service=None,
        previous_reward: float = 0.0,
        done: bool = False,
    ):
        if failed_task_ids:
            return RetryTaskAction(
                reasoning="Retry the transient failure under the same node.",
                task_id=next(iter(failed_task_ids)),
            )
        return NoOpAction(reasoning="Wait for execution.")

    def reset(self) -> None:
        pass


@pytest.mark.asyncio
async def test_engine_retries_failed_task_with_same_id() -> None:
    workflow = Workflow(name="retry", workflow_goal="retry", owner_id=uuid4())
    worker = _FailOnceAgent()
    workflow.add_agent(worker)
    task = Task(
        name="Transient task",
        description="Fail once.",
        assigned_agent_id=worker.agent_id,
    )
    workflow.add_task(task)

    engine = WorkflowExecutionEngine(
        workflow=workflow,
        agent_registry=AgentRegistry(),
        stakeholder_agent=StakeholderStub(),
        manager_agent=_RetryFailedManager(),
        seed=7,
        max_timesteps=6,
        enable_timestep_logging=False,
        enable_final_metrics_logging=False,
    )

    results = await engine.run_full_execution(save_outputs=False)

    assert set(workflow.tasks) == {task.id}
    assert workflow.tasks[task.id].status == TaskStatus.COMPLETED
    assert worker.calls == 2
    assert task.id in engine.completed_task_ids
    assert task.id not in engine.failed_task_ids
    assert workflow.tasks[task.id].execution_notes == [
        "Failed: first attempt failed",
        "Retry requested by manager",
    ]
    retry_steps = [
        result
        for result in results
        if result.metadata.get("manager_action", {}).get("action_type") == "retry_task"
    ]
    assert len(retry_steps) == 1
    assert retry_steps[0].metadata["tasks_started"] == [str(task.id)]
