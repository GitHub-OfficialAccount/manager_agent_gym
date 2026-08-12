"""
Agent coordination schemas for scheduled agent team changes.

Provides data structures for managing dynamic agent addition and removal
during workflow execution, supporting the Ad Hoc Team Coordination research challenge.
"""

from datetime import datetime
from typing import Literal, Any
from pydantic import BaseModel, Field


class ScheduledAgentChange(BaseModel):
    """A scheduled agent change at a specific timestep.

    `replace` models an EXOGENOUS REPLACEMENT: an event the manager did not choose
    substitutes a different worker for one already on the roster — a model upgrade
    or a restaffing — reusing the outgoing worker's `agent_id` so the roster size
    and the task graph are undisturbed.

    It is NOT a worker changing its own behaviour mid-episode. That reading is
    scoped out (see CLAUDE.md): workers here get changed, they do not change. The
    id reuse is a mechanism for holding everything except the worker constant, not
    a claim that the same agent persists.
    """

    timestep: int = Field(..., description="Timestep when change should occur")
    action: Literal["add", "remove", "replace"] = Field(
        ...,
        description="Add or remove an agent, or replace one in place — same id, "
        "different worker",
    )
    agent_config: Any = Field(default=None, description="Agent config for addition")
    agent_id: str | None = Field(
        default=None, description="Agent ID for removal or replacement"
    )
    new_system_prompt: str | None = Field(
        default=None,
        description="Replacement system prompt for 'replace' — the incoming worker's "
        "policy, carried on the outgoing worker's id",
    )
    new_model_name: str | None = Field(
        default=None,
        description="Replacement model name for 'replace' — e.g. a model upgrade, "
        "carried on the outgoing worker's id",
    )
    new_tool_ids: list[str] | None = Field(
        default=None,
        description="Replacement task-tool ids for 'replace', resolved via the "
        "registry's tool registry — the incoming worker's toolset",
    )
    new_agent_capabilities: list[str] | None = Field(
        default=None,
        description="Optional replacement for manager-visible declared capabilities. "
        "Leaving this unset is what makes the manager's registry card go STALE "
        "across a replacement",
    )
    announce: bool = Field(
        default=False,
        description=(
            "For 'replace': broadcast the change to all agents. False = the manager "
            "is not told, so it must find out from the newcomer's own information "
            "interface (card, declaration, ask, trace) or not at all."
        ),
    )
    reason: str = Field(..., description="Reason for this agent change")
    # Note: tools will be handled separately, not stored in schema

    def model_post_init(self, __context) -> None:
        """Validate change configuration."""
        if self.action == "add" and not self.agent_config:
            raise ValueError("agent_config is required for 'add' action")
        if self.action == "remove" and not self.agent_id:
            raise ValueError("agent_id is required for 'remove' action")
        if self.action == "replace" and not (
            self.agent_id
            and (
                self.new_system_prompt
                or self.new_model_name
                or self.new_tool_ids is not None
                or self.new_agent_capabilities is not None
            )
        ):
            raise ValueError(
                "agent_id and at least one of new_system_prompt / new_model_name "
                "/ new_tool_ids / new_agent_capabilities are required for "
                "'replace' action"
            )


class AgentCoordinationConfig(BaseModel):
    """Configuration for scheduled agent coordination changes."""

    scheduled_changes: dict[int, list[ScheduledAgentChange]] = Field(
        default_factory=dict, description="Scheduled agent changes by timestep"
    )


class AgentCoordinationEvent(BaseModel):
    """An agent coordination change event that occurred during execution."""

    event_id: str = Field(..., description="Unique event identifier")
    timestep: int = Field(..., description="Timestep when event occurred")
    action: Literal["add", "remove"] = Field(..., description="Type of change")
    agent_id: str = Field(..., description="ID of affected agent")
    agent_type: str | None = Field(default=None, description="Type of affected agent")
    reason: str = Field(..., description="Reason for this change")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When event occurred"
    )
    success: bool = Field(default=True, description="Whether the change succeeded")
    error_message: str | None = Field(
        default=None, description="Error message if change failed"
    )
