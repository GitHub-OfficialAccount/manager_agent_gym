"""
AI Agent implementation using OpenAI Agents SDK.

Provides real LLM-powered agents that can execute tasks using
system prompts and tools via the OpenAI Agents framework.
"""

import asyncio
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

# ---------------------------------------------------------------------------
# WORKER REQUEST TIMEOUT AND RETRY BOUND.
#
# THE WORKER PATH HAD NO EFFECTIVE TIMEOUT. `Runner.run` drives `LitellmModel`,
# whose constructor takes only (model, base_url, api_key) -- so the only knob is
# litellm's GLOBAL `request_timeout`, and its default is **6000 seconds**: 100
# minutes, which is not a timeout, it is a workday.
#
# The MANAGER/JUDGE path is unaffected and always was: `llm_interface` builds its
# own `AsyncOpenAI` with `timeout=300.0`. So the setting existed on one path and
# not the parallel one -- the same shape as the lattice parameter, the mix
# amplifiers, the totality repair and the rng stream. Fifth instance this phase.
#
# OBSERVED: a six-episode run sat for 20:47 with fourteen ESTABLISHED sockets,
# 899 bytes read in 60 seconds, the event loop idle in `ep_poll`, and ZERO
# episodes completed. It would have kept waiting for another eighty minutes.
#
# A TIMEOUT THAT TRIGGERS UNBOUNDED RETRY IS NOT A TIMEOUT (LS), so the retry
# bound is set here too rather than left at litellm's default of `None`, which
# resolves to the provider SDK's own policy and is not ours to reason about.
# THE FIRST VALUES -- 180s and 2 retries -- CAME FROM NOWHERE AND WOULD HAVE
# SABOTAGED THE RUN. I asserted twice that "a bound that never fires costs
# nothing"; it was false, because the bound did not sit above the workload, it sat
# INSIDE it. Measured over the committed corpus (464 paired request/response
# events, re-derived independently of LS's script):
#
#   SUCCEEDED calls:  median 39s   p90 149s   p99 554s   max 876s
#
#   bound  180s kills 32/464 (6.9%) of calls that SUCCEEDED  <- the original
#   bound  630s kills  4/464 (0.9%)                          <- the original backstop
#   bound  900s kills  0/464
#   bound 1200s kills  0/464 (+324s of headroom over the observed max)
#
# The longest healthy silence in the corpus is a single request/response pair of
# ~876s -- an episode that RETURNED and is in our committed results. A 180s bound
# with two retries behind it would have burned 3x180s and then failed, and the
# failure would have looked exactly like the stall we spent three runs misreading.
#
# 1200 with ONE retry: no observed successful call is killed, and a genuine stall
# still terminates in ~41 minutes rather than never.
WORKER_REQUEST_TIMEOUT_S = float(os.getenv("MAG_WORKER_REQUEST_TIMEOUT_S", "1200"))
WORKER_MAX_RETRIES = int(os.getenv("MAG_WORKER_MAX_RETRIES", "1"))
def _apply_worker_request_limits() -> dict[str, float | int]:
    """Bound the worker path's request time. Returns what was applied, for the record."""
    try:
        import litellm  # type: ignore

        litellm.request_timeout = WORKER_REQUEST_TIMEOUT_S
        litellm.num_retries = WORKER_MAX_RETRIES
    except Exception:  # pragma: no cover - litellm ships with the agents extra
        pass
    return {"worker_request_timeout_s": WORKER_REQUEST_TIMEOUT_S,
            "worker_max_retries": WORKER_MAX_RETRIES}


_apply_worker_request_limits()

# THE BACKSTOP, deliberately GENEROUS so it never fires on a working call. The
# client timeout above is the correct fix and sits where the observed failure was;
# this catches the case that neither of us has seen -- a call that hangs somewhere
# the client timeout does not reach. With `asyncio.gather`, ONE hung episode holds
# the WHOLE batch, so the fragility is worth covering independently of its cause.
#
# Sized as (timeout + margin) x (retries + 1): a call that legitimately exhausts
# its retries must finish INSIDE this, or the backstop would mask the very retries
# it is meant to outlive.
# RAISED TO 3600 AS A DECISION, NOT A SURVIVAL (L13).
#
# The derived value (1200+30)x2 = 2460 held on the first `partial` episode -- 0 of
# 15 worker runs exceeded it -- but the margin over the longest legitimate run
# collapsed from +155% (against the corpus max of 966s) to +14% (against 2160s).
# A margin that survives by 300 seconds on n=15 is not a bound anyone chose.
#
#   corpus, current arrangement   n=266   median  81s   max  966s
#   partial, new arrangement      n= 15   median 177s   max 2160s
#
# THE COST IS ASYMMETRIC AND THAT DECIDES IT. A backstop that fires WRONGLY kills a
# task and, with capacity binding exactly, can burn the segment's allotment and
# cost the episode -- ~100 minutes of wall clock. A backstop that is too GENEROUS
# only delays detection of a hang the heartbeat already catches. So it should sit
# well clear of legitimate work, not close to it.
#
# 3600s: +67% over the longest legitimate run ever observed, kills 0 of 281 runs
# across both arrangements, and still bounds a hung task to one hour.
#
# STATED LIMITATION: with legitimate runs reaching 36 minutes, NO per-run bound
# separates "slow" from "hung" cleanly. The heartbeat does that and this does not
# pretend to. This is a last-resort ceiling.
#
# AND `WORKER_REQUEST_TIMEOUT_S` BOUNDS A QUANTITY WE CANNOT OBSERVE: the worker
# path emits ZERO per-request events (0 worker-attributed `structured_llm_*` in
# the new bundle; all 22 are the manager's), so no bundle can price it. It is
# retained because litellm's 6000s default is indefensible, but it is unverified
# and should be labelled as such wherever it is quoted.
WORKER_RUN_BACKSTOP_S = float(os.getenv("MAG_WORKER_RUN_BACKSTOP_S", "3600"))


class WorkerRunTimeout(TimeoutError):
    """A worker run exceeded the backstop.

    Distinct from a provider timeout: this one means the request-level bound did
    not contain it, which is a harness fault worth telling apart from a slow
    provider -- the distinction the hung run could not make.
    """

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
from ..common.run_trace import record_run_event

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
EMPTY_OUTPUT_RECOVERY_PROMPT = (
    "Your previous response was empty. Using the evidence already gathered, "
    "return the final task result now in the required final output format."
)

# Key aliases models drift to when the schema is only prompt-specified.
_RESOURCE_LIST_KEYS = ("resources", "generated_resources", "output_resources")


def _run_trace_payload(result: RunResult) -> dict[str, object]:
    """Retain the SDK-visible model/tool exchange before RunResult is discarded."""
    to_input_list = getattr(result, "to_input_list", None)
    last_agent = getattr(result, "last_agent", None)
    return {
        "history": to_input_list() if callable(to_input_list) else [],
        "raw_responses": getattr(result, "raw_responses", []),
        "final_output": result.final_output,
        "last_response_id": getattr(result, "last_response_id", None),
        "last_agent": getattr(last_agent, "name", None),
    }


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
        if content is None or not str(content).strip():
            continue
        resources.append(
            Resource(
                name=str(item.get("name") or f"Output: {task.name}"),
                description=str(item.get("description") or "Model-generated output."),
                content=str(content),
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
        self._effective_instructions = instructions
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

            trace_fields = {
                "actor_type": "worker",
                "actor_id": self.config.agent_id,
                "task_id": str(task.id),
                "task_name": task.name,
            }
            record_run_event(
                "worker_execution_started",
                {
                    "model": self.config.model_name,
                    "system_prompt": self._effective_instructions,
                    "task_prompt": task_prompt,
                    "input_resources": resources or [],
                    "tools": [tool.name for tool in self.tools],
                    "max_turns": self.config.max_turns,
                },
                **trace_fields,
            )

            # Execute using OpenAI Agent with DI context
            run_options = (
                {"max_turns": self.config.max_turns}
                if self.config.max_turns is not None
                else {}
            )
            try:
                result: RunResult = await asyncio.wait_for(
                    Runner.run(
                        self.openai_agent,
                        task_prompt,
                        context=context,  # 🎯 DI magic happens here!
                        **run_options,
                    ),
                    timeout=WORKER_RUN_BACKSTOP_S,
                )
            except asyncio.TimeoutError as exc:
                raise WorkerRunTimeout(
                    f"worker run exceeded the {WORKER_RUN_BACKSTOP_S:.0f}s backstop "
                    f"for task {getattr(task, 'id', '?')}; the request-level bound "
                    f"({WORKER_REQUEST_TIMEOUT_S:.0f}s x {WORKER_MAX_RETRIES + 1}) "
                    f"did not contain it"
                ) from exc
            run_results = [result]
            record_run_event(
                "worker_run_completed",
                _run_trace_payload(result),
                run_index=0,
                **trace_fields,
            )

            if (
                self._plain_text_output
                and isinstance(result.final_output, str)
                and not result.final_output.strip()
            ):
                logger.warning(
                    "Worker %s returned empty final output; requesting finalization once",
                    self.config.agent_id,
                )
                record_run_event(
                    "worker_empty_output_recovery_started",
                    {"prompt": EMPTY_OUTPUT_RECOVERY_PROMPT},
                    **trace_fields,
                )
                recovery_input = result.to_input_list()
                recovery_input.append({
                    "role": "user",
                    "content": EMPTY_OUTPUT_RECOVERY_PROMPT,
                })
                # The original run has already finished. Recovery exists only
                # to serialize its gathered evidence, so exposing tools here
                # can restart the task and create another tool loop.
                recovery_agent = self.openai_agent.clone(tools=[])
                result = await asyncio.wait_for(
                    Runner.run(
                        recovery_agent,
                        recovery_input,
                        context=context,
                        **run_options,
                    ),
                    timeout=WORKER_RUN_BACKSTOP_S,
                )
                run_results.append(result)
                record_run_event(
                    "worker_run_completed",
                    _run_trace_payload(result),
                    run_index=1,
                    recovery=True,
                    **trace_fields,
                )
                if isinstance(result.final_output, str) and not result.final_output.strip():
                    raise ValueError("Model returned empty final output after recovery")

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

            record_run_event(
                "worker_execution_completed",
                {
                    "reasoning": output.reasoning,
                    "confidence": output.confidence,
                    "execution_notes": output.execution_notes,
                    "output_resources": output_resources,
                },
                **trace_fields,
            )

            return create_task_result(
                task_id=task.id,
                agent_id=self.config.agent_id,
                success=True,
                execution_time=execution_time,
                resources=output_resources,
                simulated_duration_hours=(execution_time / 3600.0),
                cost=sum(self._calculate_accurate_cost(item) for item in run_results),
                execution_notes=output.execution_notes,
                reasoning=output.reasoning,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            record_run_event(
                "worker_execution_failed",
                {
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                actor_type="worker",
                actor_id=self.config.agent_id,
                task_id=str(task.id),
                task_name=task.name,
            )

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
