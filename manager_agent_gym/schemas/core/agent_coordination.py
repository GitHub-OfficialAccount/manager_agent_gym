"""
Agent coordination schemas for scheduled agent team changes.

Provides data structures for managing dynamic agent addition and removal
during workflow execution, supporting the Ad Hoc Team Coordination research challenge.
"""

from datetime import datetime
from typing import Literal, Any
from pydantic import BaseModel, Field


class ScheduledAgentChange(BaseModel):
    """A scheduled agent change at a specific timestep."""

    timestep: int = Field(..., description="Timestep when change should occur")
    action: Literal["add", "remove", "replace"] = Field(
        ..., description="Add, remove, or replace (in-place mutation) an agent"
    )
    agent_config: Any = Field(default=None, description="Agent config for addition")
    agent_id: str | None = Field(
        default=None, description="Agent ID for removal or replacement"
    )
    new_system_prompt: str | None = Field(
        default=None,
        description="Replacement system prompt for 'replace' (same id, new policy)",
    )
    new_model_name: str | None = Field(
        default=None,
        description="Replacement model name for 'replace' (same id, new capability)",
    )
    announce: bool = Field(
        default=False,
        description=(
            "For 'replace': broadcast the change to all agents. False = silent "
            "swap (behavior changes with no observable announcement)."
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
            self.agent_id and (self.new_system_prompt or self.new_model_name)
        ):
            raise ValueError(
                "agent_id and at least one of new_system_prompt / new_model_name "
                "are required for 'replace' action"
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
