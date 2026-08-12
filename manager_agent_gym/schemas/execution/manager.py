"""
Manager agent observation and action data models.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from ...schemas.core import Message
from ...schemas.preferences.constraints import Constraint
from ...schemas.workflow_agents.stakeholder import StakeholderPublicProfile
from ...schemas.workflow_agents.config import AgentConfig


class LoadDimension(BaseModel):
    """One capacity a worker is measured against, WITH its release semantics.

    RELEASE SEMANTICS TRAVEL WITH THE NUMBER (L1 criterion (b)). Two capacities
    here behave oppositely: concurrency frees when a task finishes, a per-episode
    allotment never does. Rendered as bare `3/3` they are indistinguishable, and a
    reader applies the universal scheduler convention — finish one, get another —
    which is true of the first and false of the second. So the semantics are
    rendered, not merely correct in the code.
    """

    # STRICT (LS review, finding 2). `extra='ignore'` — pydantic's default — makes
    # any drift between a worker's `load_report()` keys and these fields degrade
    # SILENTLY to an empty row rendering as "(load unavailable)". That is exactly
    # how the fixture in this step's own acceptance broke: it supplied the old
    # `held`/`capacity`/`unit` keys, all three were dropped, and the constancy
    # check compared "(load unavailable)" to itself six times and passed. The same
    # mechanism sits under the LIVE path, where a worker whose load block quietly
    # emptied would satisfy every check that tests the block's PRESENCE.
    model_config = ConfigDict(extra="forbid")

    name: str
    held: int
    capacity: int
    releases_on_completion: bool = True

    @property
    def exhausted(self) -> bool:
        return self.capacity > 0 and self.held >= self.capacity

    def render(self) -> str:
        # The parenthetical describes the COUNTER, not the current value: at 0/3
        # "SPENT FOR THE EPISODE" read as though something had been spent when
        # nothing had (LS review, minor).
        note = ("frees when a task finishes" if self.releases_on_completion
                else "used this episode; does NOT reset when a task finishes")
        state = " [EXHAUSTED]" if self.exhausted else ""
        return f"{self.name} {self.held}/{self.capacity} ({note}){state}"


class AgentLoad(BaseModel):
    """One worker's load, as the worker itself reports it.

    L1 (researcher ruling, 2026-08-08). CONSTANT ACROSS EVERY CELL and not a
    manipulated channel: this is the manager seeing whether its own instructions
    took effect, which is a different information failure from anything the study
    varies. Carries NO capability, coverage or description content — a load row is
    about how full a worker is, never about what it can do. That restriction is
    load-bearing: a descriptor rendered beside the id would reintroduce successor
    capability into the cells whose card is deliberately stale.
    """

    model_config = ConfigDict(extra="forbid")  # see LoadDimension

    agent_id: str
    available: bool = True
    dimensions: list[LoadDimension] = Field(default_factory=list)

    def render(self) -> str:
        if not self.dimensions:
            return f"- {self.agent_id}: (load unavailable)"
        body = " · ".join(d.render() for d in self.dimensions)
        return f"- {self.agent_id}: {body}"


class ManagerObservation(BaseModel):
    """Observation provided to manager agent at each timestep."""

    # Allow non-Pydantic types like AgentInterface in fields
    model_config = ConfigDict(arbitrary_types_allowed=True)
    workflow_summary: str
    timestep: int = Field(..., description="Current timestep number")
    workflow_id: UUID = Field(..., description="ID of the workflow being executed")
    execution_state: str = Field(..., description="Current execution state")
    task_status_counts: dict[str, int] = Field(
        default_factory=dict, description="Count of tasks by status"
    )
    ready_task_ids: list[UUID] = Field(
        default_factory=list, description="Tasks ready to start"
    )
    running_task_ids: list[UUID] = Field(
        default_factory=list, description="Currently running tasks"
    )
    completed_task_ids: list[UUID] = Field(
        default_factory=list, description="Completed task IDs"
    )
    failed_task_ids: list[UUID] = Field(
        default_factory=list, description="Failed task IDs"
    )
    available_agent_metadata: list[AgentConfig] = Field(
        default_factory=list, description="Available agent metadata"
    )
    recent_messages: list[Message] = Field(
        default_factory=list, description="Recent communications"
    )
    workflow_progress: float = Field(
        ..., ge=0.0, le=1.0, description="Completion percentage"
    )
    observation_timestamp: datetime = Field(default_factory=datetime.now)
    roster_changes: list[str] = Field(
        default_factory=list,
        description=(
            "Roster changes applied at THIS timestep, as minimal factual lines "
            "(verb + agent id). Empty when no change occurred, and the prompt "
            "omits the block entirely in that case so unswapped prompts stay "
            "byte-comparable to pre-swap ones. Deliberately carries no reason "
            "text and no capability claim: this is the arrival-announcement "
            "channel and anything more would leak what the card channel controls."
        ),
    )

    agent_load: list[AgentLoad] = Field(
        default_factory=list,
        description=(
            "Per-worker load against capacity for every worker PRESENT on the "
            "roster, not merely the available ones — a worker that is full is "
            "exactly the one the manager needs to see. Always rendered, including "
            "when nothing is loaded: absence and zero looking identical is the "
            "defect class this signal exists to remove."
        ),
    )
    assignment_refusals: list[str] = Field(
        default_factory=list,
        description=(
            "Assignments the engine could not start since the manager last acted, "
            "one factual line each. Signalled BECAUSE THE MANAGER IS THE ONLY "
            "PARTY THAT CAN RE-ROUTE: in the scope run 580 refusals fired with no "
            "manager-visible signal at all, and the work sat assigned to a full "
            "worker until the horizon. Reported at the manager's next decision "
            "point, which is the earliest moment it can act on them."
        ),
    )

    observation_aid: str | None = Field(
        default=None,
        description=(
            "Optional derived representation of evidence already visible elsewhere "
            "in this observation. It must not contain hidden environment state."
        ),
    )

    # Optional timeline awareness
    max_timesteps: int | None = Field(
        default=None, description="Configured maximum timesteps for this run"
    )
    timesteps_remaining: int | None = Field(
        default=None, description="Remaining timesteps before reaching the limit"
    )
    time_progress: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fraction of timestep budget consumed (0..1)",
    )

    # Constraints visibility
    constraints: list[Constraint] = Field(
        default_factory=list, description="Workflow constraints (hard/soft/etc.)"
    )

    # Dynamic ID universes for schema-constrained action generation
    # These allow the manager agents to constrain IDs to valid values at generation time
    task_ids: list[UUID] = Field(
        default_factory=list, description="All task IDs currently in the workflow"
    )
    resource_ids: list[UUID] = Field(
        default_factory=list, description="All resource IDs currently in the workflow"
    )
    agent_ids: list[str] = Field(
        default_factory=list, description="All agent IDs registered in the workflow"
    )

    stakeholder_profile: StakeholderPublicProfile = Field(
        description="Public stakeholder profile",
    )
