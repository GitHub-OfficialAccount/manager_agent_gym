"""
Manager agent interface and related types.

Defines the interface for manager agents that can observe workflow
state and take actions to influence execution.
"""

from collections import deque
from typing import TYPE_CHECKING, Protocol
from abc import ABC, abstractmethod

from pydantic import ValidationError

from ...schemas.execution import AgentLoad, ManagerObservation
from ...schemas.execution.manager_actions import BaseManagerAction, ActionResult
from ...schemas.execution.observation_policy import ObservationPolicy
from ...schemas.preferences.preference import PreferenceWeights
from ...schemas.core.base import TaskStatus
from ...schemas.workflow_agents.stakeholder import StakeholderPublicProfile

if TYPE_CHECKING:
    from ...schemas.core.workflow import Workflow
    from ...schemas.execution.state import ExecutionState
    from ..communication.service import CommunicationService


class ManagerAgent(ABC):
    """Abstract interface for manager agents.

    Implementations observe the workflow, choose an action each timestep,
    and maintain a compact action history for downstream evaluation.

    Args:
        agent_id (str): Unique identifier for the manager agent.
        preferences (PreferenceWeights): Initial normalized preference weights.

    Attributes:
        agent_id (str): Identifier for logging and communications.
        preferences (PreferenceWeights): Current preference weights.
        _action_buffer (deque[ActionResult]): Recent actions (maxlen 50).

    Example:
        ```python
        class MyManager(ManagerAgent):
            async def step(self, workflow, execution_state, stakeholder_profile,
                           current_timestep, running_tasks, completed_task_ids,
                           failed_task_ids, communication_service=None,
                           previous_reward=0.0, done=False) -> BaseManagerAction:
                # decide an action...
                return NoOpAction(reasoning="Observing")
        ```
    """

    def __init__(self, agent_id: str, preferences: PreferenceWeights):
        self.agent_id = agent_id
        self.preferences = preferences
        self._action_buffer: deque[ActionResult] = deque(maxlen=50)
        # Execution horizon awareness (optional; set by engine)
        self._max_timesteps: int | None = None
        # Seed configured by engine (if any)
        self._seed: int = 42
        # Observation contract (set by engine; defaults to redacted baseline)
        self._observation_policy: ObservationPolicy = ObservationPolicy()
        self._last_decision_observation: ManagerObservation | None = None
        # Roster changes applied by the engine at the current timestep, set just
        # before step(). A SETTER rather than a step() parameter, deliberately:
        # step() is a public abstract method and adding a keyword to it breaks every
        # existing subclass with an explicit signature (measured: 27 test failures).
        # This matches the idiom already used for max_timesteps, seed, observation
        # policy and aid builder, and keeps the fork's divergence purely additive.
        self._pending_roster_changes: list[str] = []
        # Assignment refusals since this manager last acted (L1). Same setter
        # idiom and the same overwrite invariant as the roster changes above, for
        # the same reason: step() is a public abstract method.
        self._pending_assignment_refusals: list[str] = []

    def set_pending_assignment_refusals(self, refusals: list[str] | None) -> None:
        """Engine hook: assignments refused since the manager last acted (L1).

        SAME INVARIANT AS `set_pending_roster_changes` — overwritten, never
        consumed, and the engine must call it UNCONDITIONALLY before every
        `step()`. A conditional call would leave last timestep's refusal standing
        in a timestep where nothing was refused, and the manager would re-route
        work that is now running: a stale signal is worse than no signal, because
        it is acted on.
        """
        self._pending_assignment_refusals = list(refusals or [])

    def set_pending_roster_changes(self, changes: list[str] | None) -> None:
        """Engine hook: roster changes applied at the timestep about to be stepped.

        INVARIANT — overwritten, never consumed. The reader does not clear this
        field; it is replaced wholesale on every call. That is safe ONLY because
        the engine calls this unconditionally before every `step()`, so a quiet
        timestep overwrites with an empty list rather than inheriting the previous
        one. If a caller ever sets it conditionally, a stale announcement will
        persist into later timesteps — which is exactly the ghost-repeat defect
        found in review on the registry side of this same path.

        Public surface on a public abstract class: recorded in CHANGED.md.
        """
        self._pending_roster_changes = list(changes or [])

    def configure_seed(self, seed: int) -> None:
        """Configure deterministic seed for this manager (overridable)."""
        self._seed = seed

    def record_action(self, brief: ActionResult) -> None:
        self._action_buffer.append(brief)

    def get_action_buffer(
        self, number_most_recent_actions: int | None = None
    ) -> list[ActionResult]:
        if number_most_recent_actions is None or number_most_recent_actions <= 0:
            return list(self._action_buffer)

        return list(self._action_buffer)[-number_most_recent_actions:]

    def set_max_timesteps(self, max_timesteps: int | None) -> None:
        """Set the maximum timesteps for the current execution (set by engine)."""
        self._max_timesteps = (
            max_timesteps if (max_timesteps is None or max_timesteps >= 0) else None
        )

    def set_observation_policy(self, policy: ObservationPolicy) -> None:
        """Set the observation contract for this execution (set by engine)."""
        self._observation_policy = policy

    def clear_last_decision_observation(self) -> None:
        """Clear the per-step capture before a manager decision begins."""
        self._last_decision_observation = None

    def capture_decision_observation(self, observation: ManagerObservation) -> None:
        """Retain the exact pre-action observation values used for a decision."""
        self._last_decision_observation = observation.model_copy(deep=True)

    def get_last_decision_observation(self) -> ManagerObservation | None:
        """Return an isolated copy of the latest pre-action observation."""
        if self._last_decision_observation is None:
            return None
        return self._last_decision_observation.model_copy(deep=True)

    async def create_observation(
        self,
        workflow: "Workflow",
        execution_state: "ExecutionState",
        stakeholder_profile: StakeholderPublicProfile,
        current_timestep: int,
        running_tasks: dict,
        completed_task_ids: set,
        failed_task_ids: set,
        communication_service: "CommunicationService | None" = None,
        roster_changes: list[str] | None = None,
    ) -> ManagerObservation:
        """
        Create manager observation from workflow state.

        Subclasses can override this to customize what they observe.

        Args:
            workflow: Current workflow state
            execution_state: Current execution state
            current_timestep: Current timestep number
            running_tasks: Currently executing tasks
            completed_task_ids: Set of completed task IDs
            failed_task_ids: Set of failed task IDs
            communication_service: Optional communication service for messages

        Returns:
            ManagerObservation with workflow state data
        """
        # Get task status summary
        task_statuses = {}
        for status in TaskStatus:
            task_statuses[status.value] = sum(
                1 for task in workflow.tasks.values() if task.status == status
            )

        # Get ready tasks
        ready_tasks = workflow.get_ready_tasks()

        # Get available agents
        available_agents = workflow.get_available_agents()

        # LOAD (L1). Built over workflow.agents — the PRESENT roster — not over
        # `available_agents`. The two differ exactly where it matters: a worker
        # that is full is the one the manager most needs to see, and filtering by
        # availability would drop it from the board at the moment it starts
        # refusing work. Each row is the agent's OWN report, so a subclass whose
        # binding constraint is not concurrency reports the limit that binds.
        agent_load: list[AgentLoad] = []
        for agent in workflow.agents.values():
            # The stakeholder is in `workflow.agents` but is not a worker and
            # cannot be assigned to. Its row would be a true statement about
            # something the manager cannot act on, which on a board that exists to
            # drive re-routing is noise at best.
            if getattr(agent, "agent_type", "") == "stakeholder":
                continue
            # SCHEMA DRIFT IS NOT CAUGHT HERE, DELIBERATELY (LS review, finding 2).
            # A `ValidationError` means this agent's `load_report()` and the schema
            # disagree — a deterministic programming error that every episode would
            # hit identically, and that the acceptance script hits before any run
            # costs anything. Swallowing it would reproduce the exact defect the
            # strict schema was added to remove: a silent degradation to an empty
            # row, invisible to every check that tests the block's PRESENCE. The
            # instrument failing loudly beats a bundle that looks fine.
            try:
                agent_load.append(AgentLoad(**agent.load_report()))
            except ValidationError:
                raise
            except Exception as exc:
                # Anything else — a custom agent raising at runtime — is reported
                # rather than omitted. Omission reads as "no such worker", which is
                # a different and false statement, and the row says plainly that
                # the load is unknown rather than implying it is zero.
                agent_id = getattr(agent, "agent_id", "(unknown)")
                agent_load.append(
                    AgentLoad(agent_id=f"{agent_id} [LOAD REPORTING FAILED: "
                                       f"{type(exc).__name__}]",
                              available=bool(getattr(agent, "is_available", False)),
                              dimensions=[])
                )
        agent_load.sort(key=lambda row: row.agent_id)

        # Get recent messages from communication service if available
        policy = self._observation_policy
        recent_messages = []
        if communication_service:
            all_comm_messages = communication_service.get_all_messages()
            recent_messages = all_comm_messages[: policy.message_window]
        else:
            # Fallback to workflow messages for backward compatibility
            # (guard: [-0:] would return the whole list)
            recent_messages = (
                workflow.messages[-policy.message_window :]
                if policy.message_window > 0
                else []
            )


        # Compute timeline awareness fields if configured
        max_ts = self._max_timesteps
        ts_remaining = None
        time_progress = None
        if isinstance(max_ts, int) and max_ts > 0:
            ts_remaining = max(0, max_ts - current_timestep - 1)
            # Clamp progress in [0,1]
            time_progress = min(1.0, max(0.0, float(current_timestep) / float(max_ts)))

        observation = ManagerObservation(
            workflow_summary=workflow.pretty_print(),
            timestep=current_timestep,
            workflow_id=workflow.id,
            execution_state=execution_state,
            task_status_counts=task_statuses,
            ready_task_ids=[task.id for task in ready_tasks],
            running_task_ids=list(running_tasks.keys()),
            completed_task_ids=list(completed_task_ids),
            failed_task_ids=list(failed_task_ids),
            available_agent_metadata=[
                policy.redact_agent_config(agent.config) for agent in available_agents
            ],
            recent_messages=recent_messages,
            roster_changes=list(
                roster_changes
                if roster_changes is not None
                else self._pending_roster_changes
            ),
            agent_load=agent_load,
            assignment_refusals=list(self._pending_assignment_refusals),
            workflow_progress=len(completed_task_ids) / len(workflow.tasks)
            if workflow.tasks
            else 0.0,
            max_timesteps=max_ts,
            timesteps_remaining=ts_remaining,
            time_progress=time_progress,
            constraints=workflow.constraints,
            task_ids=list(workflow.tasks.keys()),
            resource_ids=list(workflow.resources.keys()),
            agent_ids=list(workflow.agents.keys()),
            stakeholder_profile=stakeholder_profile,
        )
        self.capture_decision_observation(observation)
        return observation

    # Note: take_action(observation) has been removed from the abstract interface in favor of step(...).

    @abstractmethod
    async def step(
        self,
        workflow: "Workflow",
        execution_state: "ExecutionState",
        stakeholder_profile: StakeholderPublicProfile,
        current_timestep: int,
        running_tasks: dict,
        completed_task_ids: set,
        failed_task_ids: set,
        communication_service: "CommunicationService | None" = None,
        previous_reward: float = 0.0,
        done: bool = False,
    ) -> BaseManagerAction:
        """
        One-call RL-friendly step: build observation and return an action.
        """
        raise NotImplementedError

    def on_action_executed(
        self,
        timestep: int,
        action: BaseManagerAction,
        action_result: ActionResult | None,
    ) -> None:
        """
        Hook invoked by the engine after a manager action has been executed.

        Default implementation records a compact action brief, including a short
        outcome summary when available. Manager implementations can override
        this to customize how actions are logged or persisted.
        """
        reasoning = action.reasoning
        if action_result and action_result.summary:
            reasoning += f" | Outcome of action: {action_result.summary}"

        self.record_action(
            ActionResult(
                kind=action_result.kind if action_result else "unknown",
                timestep=timestep,
                action_type=action.action_type,  # type: ignore[attr-defined]
                summary=action_result.summary
                if action_result
                else "Could not find summary of result, action may have been attempted, but failed to run.",
                data={},
                success=action_result.success if action_result else False,
            )
        )

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the manager agent state for a new workflow execution.
        """
        self._action_buffer.clear()
