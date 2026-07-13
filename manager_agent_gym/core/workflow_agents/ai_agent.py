"""
AI Agent implementation using OpenAI Agents SDK.

Provides real LLM-powered agents that can execute tasks using
system prompts and tools via the OpenAI Agents framework.
"""

import json
import math
import os
import re
import time
import traceback
from typing import TYPE_CHECKING

try:
    from agents import Agent, Runner, Tool, RunResult  # type: ignore
    from agents.extensions.models.litellm_model import LitellmModel  # type: ignore
except Exception:
    Agent = None  # type: ignore
    Runner = None  # type: ignore
    Tool = None  # type: ignore
    RunResult = None  # type: ignore
    LitellmModel = None  # type: ignore
from ...config import settings
try:
    from litellm.cost_calculator import cost_per_token  # type: ignore
except Exception:  # pragma: no cover - optional dependency guard
    def cost_per_token(**kwargs):  # type: ignore
        return 0.0, 0.0

from ...schemas.core import Resource, Task
from ...schemas.workflow_agents import (
    AIAgentConfig,
    AITaskOutput,
)
from ...schemas.unified_results import ExecutionResult, create_task_result
from ..workflow_agents.interface import AgentInterface

from ..common.llm_interface import build_litellm_model_id
from ..common.logging import logger

if TYPE_CHECKING:
    pass


from ..workflow_agents.prompts.ai_agent_prompts import (
    AI_AGENT_TASK_TEMPLATE,
    NO_RESOURCES_MESSAGE,
)


# Appended to the system prompt for models where we cannot use the SDK's
# structured-output mechanism (see comment in AIAgent.__init__). Mirrors the
# AITaskOutput schema so the final text answer can be parsed back into it.
PLAIN_TEXT_OUTPUT_CONTRACT = (
    "\n\nFINAL OUTPUT FORMAT: after any tool use, reply with a single JSON "
    'object (no markdown fences, no text before or after it) with exactly '
    'these keys: "reasoning" (string), "resources" (array of objects, each '
    'with "name", "description", "content", "content_type"; at least one), '
    '"confidence" (number between 0 and 1), "execution_notes" (array of '
    "strings). Put your actual final answer in the resources' content fields."
)

# Key aliases models drift to when the schema is only prompt-specified.
_RESOURCE_LIST_KEYS = ("resources", "generated_resources", "output_resources")


def _parse_plain_text_output(text: str, task: Task) -> AITaskOutput:
    """Best-effort parse of a plain-text final answer into AITaskOutput.

    Tolerates markdown fences, surrounding prose, drifted key names, and
    scalar-vs-list mismatches. Never raises: an unparseable reply is wrapped
    verbatim in a single resource so the worker always produces output.
    """
    fallback = AITaskOutput(
        reasoning="Unstructured model output; raw reply preserved as resource content.",
        resources=[
            Resource(
                name=f"Output: {task.name}",
                description=f"Raw model reply for task: {task.name}",
                content=text,
                content_type="text/plain",
            )
        ],
        confidence=0.5,
        execution_notes=["Final reply did not parse as structured JSON."],
    )
    stripped = re.sub(r"```[a-zA-Z]*", "", text).strip()
    start, end = stripped.find("{"), stripped.rfind("}")
    if start == -1 or end <= start:
        return fallback
    try:
        obj = json.loads(stripped[start : end + 1])
    except Exception:
        return fallback
    if not isinstance(obj, dict):
        return fallback

    raw_resources = None
    for key in _RESOURCE_LIST_KEYS:
        candidate = obj.get(key)
        if isinstance(candidate, list) and candidate:
            raw_resources = candidate
            break
        if isinstance(candidate, dict):
            raw_resources = [candidate]
            break
    resources: list[Resource] = []
    for item in raw_resources or []:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        resources.append(
            Resource(
                name=str(item.get("name") or f"Output: {task.name}"),
                description=str(item.get("description") or "Model-generated output."),
                content=None if content is None else str(content),
                content_type=str(item.get("content_type") or "text/plain"),
            )
        )
    if not resources:
        return fallback

    notes = obj.get("execution_notes") or obj.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]
    elif not isinstance(notes, list):
        notes = [notes]
    try:
        confidence = float(obj.get("confidence", obj.get("confidence_level", 0.5)))
    except (TypeError, ValueError):
        confidence = 0.5
    if not math.isfinite(confidence):
        confidence = 0.5
    confidence = min(1.0, max(0.0, confidence))
    return AITaskOutput(
        reasoning=str(obj.get("reasoning") or ""),
        resources=resources,
        confidence=confidence,
        execution_notes=[str(n) for n in notes if n is not None],
    )


class AIAgent(AgentInterface[AIAgentConfig]):
    """
    AI agent implementation using OpenAI Agents SDK.

    Executes tasks using real LLM inference with system prompts
    and structured tools.
    """

    def __init__(
        self,
        config: AIAgentConfig,
        tools: list[Tool],
    ):
        if Agent is None or LitellmModel is None or Runner is None:
            raise ImportError(
                "openai-agents SDK is not installed. Install with `uv sync --group agents`."
            )
        super().__init__(config)

        # Ensure OpenAI API key is available in environment
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "na":
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

        # Include communication tools via late import to avoid circular imports
        from ..workflow_agents.tools.communication_di import COMMUNICATION_TOOLS
        from ..execution.context import AgentExecutionContext

        self.tools = tools + COMMUNICATION_TOOLS
        # The SDK's output_type sends a strict json_schema response_format on
        # EVERY request, including turns where a tool call is expected. Most
        # OpenRouter backends grammar-enforce that schema, which makes emitting
        # a tool call literally impossible — the model is forced to fabricate a
        # final answer on turn 1 (see CHANGED.md: with response_format 0/9 tool
        # calls across 10 providers; without it 12/12, byte-identical bodies).
        # So for OpenRouter models we skip output_type, specify the schema in
        # the prompt instead, and parse the plain-text reply leniently.
        self._plain_text_output = config.model_name.startswith("openrouter/")
        instructions = config.system_prompt
        if self._plain_text_output:
            instructions = config.system_prompt + PLAIN_TEXT_OUTPUT_CONTRACT
        self.openai_agent: Agent[AgentExecutionContext] = Agent(
            model=LitellmModel(model=build_litellm_model_id(config.model_name)),
            name=config.agent_id,
            instructions=instructions,
            tools=self.tools,
            **({} if self._plain_text_output else {"output_type": AITaskOutput}),
        )

    async def execute_task(
        self, task: Task, resources: list[Resource]
    ) -> ExecutionResult:
        """
        Execute a task using the OpenAI Agent.

        Args:
            task: The task to execute
            resources: Available input resources (optional)

        Returns:
            ExecutionResult with AI-generated outputs
        """
        start_time = time.time()

        try:
            # Create execution context for dependency injection
            from ..execution.context import AgentExecutionContext

            if self.communication_service:
                context = AgentExecutionContext(
                    communication_service=self.communication_service,
                    agent_id=self.config.agent_id,
                    current_task_id=task.id,
                    tool_event_sink=self.record_tool_use_event,
                )
            else:
                # Create a minimal context if no communication service
                from ..communication.service import (
                    CommunicationService,
                )

                context = AgentExecutionContext(
                    communication_service=CommunicationService(),  # Empty service
                    agent_id=self.config.agent_id,
                    current_task_id=task.id,
                    tool_event_sink=self.record_tool_use_event,
                )

            # Prepare the task prompt
            task_prompt = self._create_task_prompt(task, resources or [])

            # Execute using OpenAI Agent with DI context
            result: RunResult = await Runner.run(
                self.openai_agent,
                task_prompt,
                context=context,  # 🎯 DI magic happens here!
            )

            # Extract structured output
            output = result.final_output
            if self._plain_text_output and isinstance(output, str):
                output = _parse_plain_text_output(output, task)
            if not isinstance(output, AITaskOutput):
                raise ValueError("Output is not an AITaskOutput")

            # Calculate execution metrics
            execution_time = time.time() - start_time
            output_resources = output.resources

            # If no resources were created, create a default one
            if not output_resources:
                output_resources.append(
                    Resource(
                        name=f"Completed: {task.name}",
                        description=f"AI agent completed task: {task.description}",
                        content=str(result),
                        content_type="text/plain",
                    )
                )

            return create_task_result(
                task_id=task.id,
                agent_id=self.config.agent_id,
                success=True,
                execution_time=execution_time,
                resources=output_resources,
                simulated_duration_hours=(execution_time / 3600.0),
                cost=self._calculate_accurate_cost(result),
                execution_notes=output.execution_notes,
                reasoning=output.reasoning,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return create_task_result(
                task_id=task.id,
                agent_id=self.config.agent_id,
                success=False,
                execution_time=execution_time,
                simulated_duration_hours=(execution_time / 3600.0),
                error=traceback.format_exc(),
                resources=[],
                cost=0.0,
                execution_notes=[
                    f"Task execution failed: {traceback.format_exc()}",
                    f"Model: {self.config.model_name}",
                    f"Tools available: {len(self.tools)}",
                    f"Error details: {str(e)}",
                ],
            )

    def _create_task_prompt(self, task: Task, resources: list[Resource]) -> str:
        """Create a detailed prompt for the AI agent."""

        input_resources = (
            self._format_resources(resources) if resources else NO_RESOURCES_MESSAGE
        )

        return AI_AGENT_TASK_TEMPLATE.format(
            task_name=task.name,
            task_description=task.description,
            input_resources=input_resources,
        )

    def _format_resources(self, resources: list[Resource]) -> str:
        """Format resources for inclusion in the prompt."""
        formatted = []
        for resource in resources:
            content_preview = (
                (resource.content[:200] + "...")
                if resource.content and len(resource.content) > 200
                else (resource.content or "")
            )
            formatted.append(
                f"- {resource.name}: {resource.description}\n  Content: {content_preview}"
            )
        return "\n".join(formatted)

    def _calculate_accurate_cost(self, result: RunResult) -> float:
        """Calculate accurate cost using LiteLLM's cost_per_token function."""
        # Extract token usage details from result
        usage = result.context_wrapper.usage

        # Extract cache token info if available (newer API versions)
        cache_creation_tokens = 0
        cached_tokens = 0
        try:
            if (
                usage.input_tokens_details
                and usage.input_tokens_details.cached_tokens is not None
            ):
                cached_tokens = usage.input_tokens_details.cached_tokens or 0
                cache_creation_tokens = usage.input_tokens - cached_tokens
        except AttributeError:
            # Handle cases where input_tokens_details or cached_tokens don't exist
            pass

        # Calculate cost using LiteLLM; models missing from its price map raise,
        # and cost bookkeeping must never fail the task itself.
        try:
            prompt_cost, completion_cost = cost_per_token(
                model=self.config.model_name,
                prompt_tokens=usage.input_tokens,
                completion_tokens=usage.output_tokens,
                cache_read_input_tokens=cached_tokens,
                cache_creation_input_tokens=cache_creation_tokens,
            )
        except Exception as e:
            logger.warning(
                "Cost lookup failed for model %s (%s); recording $0 for this call",
                self.config.model_name,
                e.__class__.__name__,
            )
            return 0.0

        return prompt_cost + completion_cost
