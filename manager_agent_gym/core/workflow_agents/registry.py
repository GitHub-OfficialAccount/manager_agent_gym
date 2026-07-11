"""
Agent registry for managing available agents in the system.

Provides a centralized way to register, discover, and instantiate agents
for task execution in the workflow system.
"""

from typing import Type, TYPE_CHECKING
from agents import Tool
from ...schemas.workflow_agents import (
    AgentConfig,
    AIAgentConfig,
    HumanAgentConfig,
)
from ...schemas.core.agent_coordination import ScheduledAgentChange
from ..workflow_agents.interface import AgentInterface
from ..workflow_agents.ai_agent import AIAgent
from ..workflow_agents.human_agent import MockHumanAgent
from ..workflow_agents.tool_factory import ToolFactory

if TYPE_CHECKING:
    from ..communication.service import CommunicationService
    from ..workflow_agents.tool_factory import ToolFactory as ToolFactoryType


class AgentRegistry:
    """Dynamic registry for agents participating in a workflow run.

    Maintains agent instances, allows late binding of agent classes, and
    optionally schedules agents to join/leave at specific timesteps.

    Example:
        ```python
        reg = AgentRegistry()
        reg.register_agent_class("ai", AIAgent)
        reg.register_agent_class("human_mock", MockHumanAgent)
        reg.register_ai_agent(AIAgentConfig(agent_id="ai_analyst"), [])
        ```
    """

    def __init__(self):
        self._agents: dict[str, AgentInterface] = {}
        self._agent_classes: dict[str, Type[AgentInterface]] = {}
        # Optional: simple built-in scheduler for adding/removing agents at timesteps
        self._scheduled_changes: dict[int, list[ScheduledAgentChange]] = {}
        self._executed_change_timesteps: set[int] = set()
        # Named tools, so serializable schedules can reference tool objects by id
        # (used by tool-swap perturbations).
        self._tool_registry: dict[str, object] = {}

    def register_tool(self, tool_id: str, tool: object) -> None:
        """Register a task-tool object under an id for tool-swap resolution."""
        self._tool_registry[tool_id] = tool

    def register_agent_class(
        self, agent_type: str, agent_class: Type[AgentInterface]
    ) -> None:
        """
        Register an agent class for a specific agent type.

        Args:
            agent_type: The type identifier for the agent
            agent_class: The agent class to register
        """
        self._agent_classes[agent_type] = agent_class

    def create_agent(self, config: AgentConfig) -> AgentInterface:
        """
        Create an agent instance from configuration.

        Args:
            config: Agent configuration

        Returns:
            Agent instance

        Raises:
            ValueError: If agent type is not registered
        """
        if config.agent_type not in self._agent_classes:
            raise ValueError(f"Unknown agent type: {config.agent_type}")

        agent_class = self._agent_classes[config.agent_type]
        agent = agent_class(config)
        self._agents[config.agent_id] = agent
        return agent

    def register_agent(self, agent: AgentInterface) -> None:
        """
        Register an existing agent instance.

        Args:
            agent: The agent instance to register
        """
        self._agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> AgentInterface | None:
        """
        Get an agent by ID.

        Args:
            agent_id: The agent's unique identifier

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)

    def list_agents(self) -> list[AgentInterface]:
        """
        Get all registered agents.

        Returns:
            List of all agent instances
        """
        return list(self._agents.values())

    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the registry.

        Args:
            agent_id: The agent's unique identifier

        Returns:
            True if agent was removed, False if not found
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered agents."""
        self._agents.clear()

    def get_agent_stats(self) -> dict[str, int]:
        """
        Get statistics about registered agents.

        Returns:
            Dictionary with agent type counts
        """
        stats: dict[str, int] = {}
        for agent in self._agents.values():
            agent_type = agent.agent_type
            stats[agent_type] = stats.get(agent_type, 0) + 1
        return stats

    def register_ai_agent(
        self, config: AgentConfig | AIAgentConfig, additional_tools: list[Tool]
    ) -> None:
        """
        Create and register an AI agent.

        Args:
            config: Agent configuration
            additional_tools: List of tools for the agent

        Returns:
            Created AI agent instance
        """
        if not additional_tools:
            additional_tools = ToolFactory.create_ai_tools()

        if not isinstance(config, AIAgentConfig):
            raise ValueError(
                "config must be an AIAgentConfig, received: " + str(type(config))
            )

        agent = AIAgent(config=config, tools=additional_tools)
        self.register_agent(agent)

    def register_human_agent(
        self,
        config: HumanAgentConfig,
        additional_tools: list[Tool],
    ) -> None:
        """
        Create and register a human mock agent.

        Args:
            config: Human agent configuration (includes persona and noise settings)
            additional_tools: List of tools for the agent

        Returns:
            Created human mock agent instance
        """
        if not additional_tools:
            additional_tools = ToolFactory.create_human_tools()

        agent = MockHumanAgent(config, additional_tools)
        self.register_agent(agent)

    # --- Optional simple scheduling API (can replace AgentCoordinationEngine) ---
    def schedule_agent_add(
        self,
        timestep: int,
        config: AIAgentConfig | HumanAgentConfig,
        reason: str = "",
    ) -> None:
        change = ScheduledAgentChange(
            timestep=timestep,
            action="add",
            agent_config=config,
            reason=reason,
        )
        self._scheduled_changes.setdefault(timestep, []).append(change)

    def schedule_agent_remove(
        self, timestep: int, agent_id: str, reason: str = ""
    ) -> None:
        change = ScheduledAgentChange(
            timestep=timestep,
            action="remove",
            agent_id=agent_id,
            reason=reason,
        )
        self._scheduled_changes.setdefault(timestep, []).append(change)

    def schedule_prompt_swap(
        self,
        timestep: int,
        agent_id: str,
        new_system_prompt: str,
        announce: bool = False,
        reason: str = "",
    ) -> None:
        """Schedule an in-place policy change: same agent id, new system prompt.

        The agent instance is rebuilt from its current config with the new
        prompt at the target timestep (configs cache the underlying SDK agent,
        so mutation alone is not enough). With announce=False nothing about
        the change is observable except the agent's subsequent behavior.
        """
        change = ScheduledAgentChange(
            timestep=timestep,
            action="replace",
            agent_id=agent_id,
            new_system_prompt=new_system_prompt,
            announce=announce,
            reason=reason,
        )
        self._scheduled_changes.setdefault(timestep, []).append(change)

    def schedule_model_swap(
        self,
        timestep: int,
        agent_id: str,
        new_model_name: str,
        announce: bool = False,
        reason: str = "",
    ) -> None:
        """Schedule an in-place capability change: same agent id, new model.

        Rebuilds the agent from its current config with a different underlying
        LLM (e.g. a weaker model) at the target timestep. With announce=False
        nothing about the change is observable except subsequent behavior.
        """
        change = ScheduledAgentChange(
            timestep=timestep,
            action="replace",
            agent_id=agent_id,
            new_model_name=new_model_name,
            announce=announce,
            reason=reason,
        )
        self._scheduled_changes.setdefault(timestep, []).append(change)

    def schedule_tool_swap(
        self,
        timestep: int,
        agent_id: str,
        new_tool_ids: list[str],
        announce: bool = False,
        reason: str = "",
    ) -> None:
        """Schedule an in-place toolset change (e.g. downgrade advanced->basic).

        Tool ids are resolved against the registry's tool registry at apply time.
        """
        change = ScheduledAgentChange(
            timestep=timestep,
            action="replace",
            agent_id=agent_id,
            new_tool_ids=new_tool_ids,
            announce=announce,
            reason=reason,
        )
        self._scheduled_changes.setdefault(timestep, []).append(change)

    async def apply_scheduled_changes_for_timestep(
        self,
        timestep: int,
        communication_service: "CommunicationService | None" = None,
        tool_factory: "ToolFactoryType | None" = None,
    ) -> list[str]:
        """
        Apply any scheduled add/remove operations for the given timestep.

        Returns a list of human-readable change descriptions.
        """
        if (
            timestep not in self._scheduled_changes
            or timestep in self._executed_change_timesteps
        ):
            return []

        changes: list[str] = []
        for change in self._scheduled_changes.get(timestep, []):
            if change.action == "add" and change.agent_config is not None:
                # Prepare tools and register based on type
                tools: list[Tool] = []
                if tool_factory is not None and communication_service is not None:
                    tools = tool_factory.add_communication_tools(
                        tools, communication_service, change.agent_config.agent_id
                    )

                if isinstance(change.agent_config, AIAgentConfig):
                    self.register_ai_agent(change.agent_config, tools)
                elif isinstance(change.agent_config, HumanAgentConfig):
                    self.register_human_agent(change.agent_config, tools)
                else:
                    changes.append(
                        f"Unsupported agent type for add: {type(change.agent_config)}"
                    )
                    continue

                # Inject comms if provided
                if communication_service is not None:
                    agent = self.get_agent(change.agent_config.agent_id)
                    if agent is not None:
                        agent.communication_service = communication_service

                changes.append(f"Added {change.agent_config.agent_id}: {change.reason}")

            elif change.action == "remove" and change.agent_id is not None:
                removed = self.remove_agent(change.agent_id)
                if removed:
                    changes.append(f"Removed {change.agent_id}: {change.reason}")
                else:
                    changes.append(
                        f"Could not remove {change.agent_id}: {change.reason}"
                    )
            elif (
                change.action == "replace"
                and change.agent_id is not None
                and (
                    change.new_system_prompt is not None
                    or change.new_model_name is not None
                    or change.new_tool_ids is not None
                )
            ):
                existing = self.get_agent(change.agent_id)
                if existing is None:
                    changes.append(
                        f"Could not replace {change.agent_id}: agent not registered"
                    )
                    continue
                # Apply whichever config fields the change specifies; unset
                # fields are left untouched (prompt swap, model swap, or both).
                config_updates: dict[str, object] = {}
                if change.new_system_prompt is not None:
                    config_updates["system_prompt"] = change.new_system_prompt
                if change.new_model_name is not None:
                    config_updates["model_name"] = change.new_model_name
                new_config = existing.config.model_copy(update=config_updates)
                # Tool swap: resolve new task-tools by id (communication tools are
                # re-added by the agent). Otherwise keep the existing toolset (a
                # prompt/model swap changes policy/capability, not tools).
                if change.new_tool_ids is not None:
                    tools = [
                        self._tool_registry[tid]
                        for tid in change.new_tool_ids
                        if tid in self._tool_registry
                    ]
                else:
                    tools = list(getattr(existing, "tools", []) or [])
                    if not tools and tool_factory is not None and communication_service is not None:
                        tools = tool_factory.add_communication_tools(
                            tools, communication_service, change.agent_id
                        )
                if isinstance(new_config, AIAgentConfig):
                    self.register_ai_agent(new_config, tools)
                elif isinstance(new_config, HumanAgentConfig):
                    self.register_human_agent(new_config, tools)
                else:
                    changes.append(
                        f"Unsupported agent type for replace: {type(new_config)}"
                    )
                    continue
                if communication_service is not None:
                    agent = self.get_agent(change.agent_id)
                    if agent is not None:
                        agent.communication_service = communication_service
                if change.announce and communication_service is not None:
                    await communication_service.broadcast_message(
                        from_agent=change.agent_id,
                        content=(
                            f"Notice: agent '{change.agent_id}' has been updated"
                            + (f" — {change.reason}" if change.reason else "")
                        ),
                    )
                swapped_fields = [
                    k for k in ("system_prompt", "model_name") if k in config_updates
                ]
                if change.new_tool_ids is not None:
                    swapped_fields.append("tools")
                swapped = "+".join(swapped_fields)
                changes.append(
                    f"Replaced {change.agent_id} [{swapped}]"
                    + (" (announced)" if change.announce else " (silent)")
                    + (f": {change.reason}" if change.reason else "")
                )
            else:
                changes.append("Invalid scheduled change entry")

        self._executed_change_timesteps.add(timestep)
        return changes
