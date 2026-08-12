"""
Base agent interface for Manager Agent Gym.

Defines the core abstractions for agents that execute tasks
and produce resources in the workflow system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Generic, TYPE_CHECKING
from uuid import UUID

from ...schemas.workflow_agents import AgentConfig, StakeholderConfig
from ...schemas.preferences.preference import PreferenceWeights, PreferenceChange
from ...schemas.preferences.weight_update import (
    PreferenceWeightUpdateRequest,
)
from ...schemas.core import Task, Resource
from ...schemas.unified_results import ExecutionResult
from ...schemas.workflow_agents.stakeholder import (
    StakeholderPublicProfile,
)
from ..communication.service import COMMUNICATION_SERVICE_SINGLETON
from ...schemas.workflow_agents.telemetry import AgentToolUseEvent

if TYPE_CHECKING:
    pass

ConfigType = TypeVar("ConfigType", bound=AgentConfig)


# REFUSAL CODES — the ANALYSIS's handle on why work did not start.
#
# The first version returned formatted English sentences only, and the segment
# split then classified permanent-versus-transient by testing whether the
# substring "allotment" appeared in the prose. That is the display-name predicate
# one level down: **identity derived from text meant for a human reader.** It was
# already misclassifying — the base class's availability refusal contains no
# "allotment", so it fell through a catch-all and was recorded as a CONCURRENCY
# refusal, and availability is exactly what a roster change touches.
#
# So each reason carries BOTH: a stable CODE the analysis classifies on, and the
# sentence the manager reads. The sentence keeps its interpolated numbers — it is
# the human-readable signal L1 exists to deliver. **The sentence informs, the code
# classifies.**
REFUSAL_UNAVAILABLE = "unavailable"
REFUSAL_CONCURRENCY = "concurrency"
REFUSAL_SEGMENT_ALLOTMENT = "segment_allotment"


@dataclass(frozen=True)
class RefusalReason:
    """One reason an assignment could not start: a code, and prose for the manager."""

    code: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


class AgentInterface(ABC, Generic[ConfigType]):
    """
    Abstract base class for all agents in the system.

    Agents execute tasks and form the core workforce in workflows.
    They combine execution capabilities with business logic like
    availability and capacity management.
    """

    def __init__(
        self,
        config: ConfigType,
    ):
        self.config = config
        self.communication_service = COMMUNICATION_SERVICE_SINGLETON
        self._seed: int | None = None

        self.name: str = config.agent_id
        self.description: str
        self.is_available: bool = True
        self.max_concurrent_tasks: int = 1  # Humans limited, AI can override
        self.current_task_ids: list[UUID] = []

        # Performance tracking
        self.tasks_completed: int = 0
        self.joined_at: datetime = datetime.now()
        # Tool usage buffer keyed by task id
        self.tool_usage_by_task: dict[UUID, list[AgentToolUseEvent]] = {}

    def configure_seed(self, seed: int) -> None:
        """Configure deterministic seed for this agent (overridable)."""
        self._seed = seed

    @property
    def agent_id(self) -> str:
        """Get the agent's unique identifier."""
        return self.config.agent_id

    @property
    def agent_type(self) -> str:
        """Get the agent's type."""
        return self.config.agent_type

    def refusal_reasons(self, task: Task) -> list["RefusalReason"]:
        """EVERY reason this agent cannot start this task, not the first one (L1).

        WHY ALL OF THEM, AND WHY THIS IS THE SOURCE OF TRUTH RATHER THAN A
        REPORTING HELPER. The previous `can_handle_task` returned on the first
        failing branch, so an agent that was BOTH busy and out of its work
        allotment refused for a reason recorded as transient while being
        permanently barred — and no combination of the logged fields could recover
        which it was, even in principle. Short-circuiting is fine for a boolean and
        fatal for a reason, so the reason is computed here and the boolean is
        derived from it, rather than the reverse.

        Subclasses that add a refusal condition override THIS, not
        `can_handle_task`, and append rather than replace.
        """
        reasons: list[RefusalReason] = []
        if not self.is_available:
            reasons.append(RefusalReason(
                REFUSAL_UNAVAILABLE,
                "the worker is not available"))
        if len(self.current_task_ids) >= self.max_concurrent_tasks:
            reasons.append(RefusalReason(
                REFUSAL_CONCURRENCY,
                f"concurrency limit reached ({len(self.current_task_ids)}/"
                f"{self.max_concurrent_tasks} concurrent tasks; frees when a "
                f"running task finishes)"))
        return reasons

    def can_handle_task(self, task: Task) -> bool:
        """Check if agent can handle a given task based on availability."""
        return not self.refusal_reasons(task)

    def load_report(self) -> dict:
        """This agent's load, one row per capacity DIMENSION (L1).

        THE AGENT OWNS THE DEFINITION OF ITS OWN LOAD, deliberately. The engine
        cannot compute it: `can_handle_task` is overridable, and a subclass whose
        real constraint is something other than concurrent-task count (see
        `CapacityBoundedAIAgent`, bounded on SEGMENT tasks over the whole episode)
        would have its load reported against a limit that never binds. Reporting
        the wrong denominator is worse than reporting nothing: it would show 1/1
        beside a worker refusing everything, and the manager would have no way to
        tell an honest board from a broken one.

        MULTIPLE DIMENSIONS, AND RELEASE SEMANTICS CARRIED WITH EACH. Concurrency
        frees when a task finishes; a per-episode allotment does not. Both rendered
        as `3/3` would inherit the universal scheduler convention that finishing
        earns another slot, which for an allotment is false — so
        `releases_on_completion` travels with the number and is rendered, not left
        true-in-the-code.

        The default is the base-class constraint, which is what `can_handle_task`
        enforces here. Any subclass that overrides `refusal_reasons` should
        override this too — the pairing is the contract.
        """
        return {
            "agent_id": self.agent_id,
            "available": self.is_available,
            "dimensions": [
                {
                    "name": "concurrent tasks",
                    "held": len(self.current_task_ids),
                    "capacity": self.max_concurrent_tasks,
                    "releases_on_completion": True,
                }
            ],
        }

    def record_tool_use_event(self, event: AgentToolUseEvent) -> None:
        """Record a tool usage event under the current task bucket."""
        task_id = event.task_id
        if task_id is None:
            return
        self.tool_usage_by_task.setdefault(task_id, []).append(event)

    def get_tool_usage_by_task(self) -> dict[UUID, list[AgentToolUseEvent]]:
        """Return a copy of per-task tool usage events for this agent."""
        return {k: list(v) for k, v in self.tool_usage_by_task.items()}

    @abstractmethod
    async def execute_task(
        self, task: Task, resources: list[Resource]
    ) -> ExecutionResult:
        """
        Execute a task given the task and available resources.

        Args:
            task: The task to execute
            resources: Available input resources (optional)

        Returns:
            ExecutionResult with outputs and metadata

        Raises:
            Exception: If execution fails in an unrecoverable way
        """
        pass


class StakeholderBase(AgentInterface[StakeholderConfig], ABC):
    """Abstract base for stakeholder agents.

    Defines the required policy step and preference ownership API so the engine
    can interact without concrete type knowledge.
    """

    def __init__(self, config: StakeholderConfig):
        super().__init__(config)
        self.public_profile: StakeholderPublicProfile = StakeholderPublicProfile(
            display_name=self.config.name,
            role=self.config.role,
            preference_summary=self.config.initial_preferences.get_preference_summary(),
        )

    @abstractmethod
    async def policy_step(
        self,
        current_timestep: int,
    ) -> None: ...

    @abstractmethod
    def get_preferences_for_timestep(self, timestep: int) -> PreferenceWeights: ...

    @abstractmethod
    def apply_preference_change(
        self,
        timestep: int,
        new_weights: PreferenceWeights,
        change_event: PreferenceChange | None,
    ) -> None: ...

    @abstractmethod
    def apply_weight_update(
        self,
        request: PreferenceWeightUpdateRequest,
    ) -> PreferenceChange: ...

    @abstractmethod
    def apply_weight_updates(
        self,
        requests: list[PreferenceWeightUpdateRequest],
    ) -> list[PreferenceChange]: ...
