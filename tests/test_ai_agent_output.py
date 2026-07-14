from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from agents import function_tool
from agents.extensions.models.litellm_model import LitellmModel

from manager_agent_gym.core.workflow_agents.ai_agent import (
    AIAgent,
    _parse_plain_text_output,
)
from manager_agent_gym.core.common.run_trace import RunTraceRecorder
from manager_agent_gym.schemas.core import Task
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig, AITaskOutput


def _config(model_name: str) -> AIAgentConfig:
    return AIAgentConfig(
        agent_id="worker",
        agent_type="ai",
        system_prompt="Use the available tools to complete the assigned task.",
        model_name=model_name,
        agent_description="Test worker",
        agent_capabilities=["analysis"],
    )


@function_tool
def _analysis_tool(value: int) -> str:
    """Return the supplied value."""
    return str(value)


def test_openrouter_agent_keeps_litellm_and_tools_without_output_schema() -> None:
    agent = AIAgent(
        _config("openrouter/deepseek/deepseek-v4-flash"), tools=[_analysis_tool]
    )

    assert isinstance(agent.openai_agent.model, LitellmModel)
    assert agent.openai_agent.output_type is None
    assert {tool.name for tool in agent.openai_agent.tools} == {
        "_analysis_tool",
        "send_message",
        "broadcast_message",
        "get_recent_messages",
    }


def test_non_openrouter_agent_keeps_structured_output() -> None:
    agent = AIAgent(_config("openai/gpt-4o-mini"), tools=[])

    assert isinstance(agent.openai_agent.model, LitellmModel)
    assert agent.openai_agent.output_type is AITaskOutput


def test_ai_agent_config_preserves_sdk_turn_default_unless_overridden() -> None:
    assert _config("openai/gpt-4o-mini").max_turns is None
    assert _config("openai/gpt-4o-mini").model_copy(update={"max_turns": 15}).max_turns == 15


@pytest.mark.asyncio
@pytest.mark.parametrize("max_turns", [None, 15])
async def test_execute_task_only_overrides_turn_limit_when_configured(
    monkeypatch, max_turns: int | None
) -> None:
    config = _config("openrouter/deepseek/deepseek-v4-flash").model_copy(
        update={"max_turns": max_turns}
    )
    agent = AIAgent(config, tools=[])
    run = AsyncMock(return_value=SimpleNamespace(
        final_output=(
            '{"reasoning":"done","resources":[{"name":"answer",'
            '"description":"result","content":"metric: 1",'
            '"content_type":"text/plain"}],"confidence":1,'
            '"execution_notes":[]}'
        )
    ))
    monkeypatch.setattr(
        "manager_agent_gym.core.workflow_agents.ai_agent.Runner.run", run
    )
    monkeypatch.setattr(agent, "_calculate_accurate_cost", lambda _result: 0.0)

    result = await agent.execute_task(
        Task(name="Report metric", description="Report the requested metric."), []
    )

    assert result.success is True
    if max_turns is None:
        assert "max_turns" not in run.await_args.kwargs
    else:
        assert run.await_args.kwargs["max_turns"] == max_turns


@pytest.mark.asyncio
async def test_execute_task_trace_preserves_prompts_and_sdk_history(monkeypatch) -> None:
    agent = AIAgent(_config("openrouter/deepseek/deepseek-v4-flash"), tools=[])
    history = [
        {"role": "user", "content": "task prompt"},
        {"type": "function_call", "name": "example_tool", "arguments": "{}"},
        {"type": "function_call_output", "output": "metric: 1"},
    ]
    sdk_result = SimpleNamespace(
        final_output=(
            '{"reasoning":"done","resources":[{"name":"answer",'
            '"description":"result","content":"metric: 1",'
            '"content_type":"text/plain"}],"confidence":1,'
            '"execution_notes":[]}'
        ),
        to_input_list=lambda: history,
        raw_responses=[],
        last_response_id="response-1",
        last_agent=SimpleNamespace(name="worker"),
    )
    run = AsyncMock(return_value=sdk_result)
    monkeypatch.setattr(
        "manager_agent_gym.core.workflow_agents.ai_agent.Runner.run", run
    )
    monkeypatch.setattr(agent, "_calculate_accurate_cost", lambda _result: 0.0)
    recorder = RunTraceRecorder()

    with recorder.activate():
        result = await agent.execute_task(
            Task(name="Report metric", description="Report the requested metric."), []
        )

    assert result.success is True
    started, sdk_completed, completed = recorder.events
    assert started["event_type"] == "worker_execution_started"
    assert "FINAL OUTPUT FORMAT" in started["payload"]["system_prompt"]
    assert "TASK: Report metric" in started["payload"]["task_prompt"]
    assert sdk_completed["event_type"] == "worker_run_completed"
    assert sdk_completed["payload"]["history"] == history
    assert sdk_completed["payload"]["last_response_id"] == "response-1"
    assert completed["event_type"] == "worker_execution_completed"
    assert completed["payload"]["output_resources"][0]["content"] == "metric: 1"


@pytest.mark.asyncio
async def test_execute_task_recovers_once_from_empty_openrouter_output(
    monkeypatch,
) -> None:
    config = _config("openrouter/deepseek/deepseek-v4-flash").model_copy(
        update={"max_turns": 15}
    )
    agent = AIAgent(config, tools=[])
    empty_result = SimpleNamespace(
        final_output="",
        to_input_list=lambda: [{"role": "user", "content": "original task"}],
    )
    recovered_result = SimpleNamespace(
        final_output=(
            '{"reasoning":"done","resources":[{"name":"answer",'
            '"description":"result","content":"metric: 1",'
            '"content_type":"text/plain"}],"confidence":1,'
            '"execution_notes":[]}'
        )
    )
    run = AsyncMock(side_effect=[empty_result, recovered_result])
    monkeypatch.setattr(
        "manager_agent_gym.core.workflow_agents.ai_agent.Runner.run", run
    )
    monkeypatch.setattr(agent, "_calculate_accurate_cost", lambda _result: 0.0)

    result = await agent.execute_task(
        Task(name="Report metric", description="Report the requested metric."), []
    )

    assert result.success is True
    assert run.await_count == 2
    recovery_input = run.await_args_list[1].args[1]
    recovery_agent = run.await_args_list[1].args[0]
    assert recovery_input[-1]["role"] == "user"
    assert "previous response was empty" in recovery_input[-1]["content"]
    assert recovery_agent.tools == []
    assert agent.openai_agent.tools != []
    assert run.await_args_list[1].kwargs["max_turns"] == 15


@pytest.mark.asyncio
async def test_execute_task_fails_after_two_empty_openrouter_outputs(monkeypatch) -> None:
    agent = AIAgent(_config("openrouter/deepseek/deepseek-v4-flash"), tools=[])
    empty_result = SimpleNamespace(
        final_output="",
        to_input_list=lambda: [{"role": "user", "content": "original task"}],
    )
    run = AsyncMock(side_effect=[empty_result, empty_result])
    monkeypatch.setattr(
        "manager_agent_gym.core.workflow_agents.ai_agent.Runner.run", run
    )

    result = await agent.execute_task(
        Task(name="Report metric", description="Report the requested metric."), []
    )

    assert result.success is False
    assert run.await_count == 2
    assert "empty final output after recovery" in str(result.error_message)


def test_task_prompt_requests_brief_output_without_unused_quality_score() -> None:
    agent = AIAgent(_config("openrouter/deepseek/deepseek-v4-flash"), tools=[])
    prompt = agent._create_task_prompt(
        Task(name="Report metric", description="Report the requested metric."), []
    )

    assert "reasonable verification" in prompt
    assert "brief rationale" in prompt
    assert "quality" not in prompt.lower()


def test_plain_text_parser_accepts_fences_alias_and_scalar_resource() -> None:
    task = Task(name="Outlier count", description="Report the outlier count.")
    output = _parse_plain_text_output(
        """```json
        {"reasoning":"Used the tool", "generated_resources":
         {"name":"answer", "content":"91"}, "confidence":1,
         "execution_notes":"complete"}
        ```""",
        task,
    )

    assert output.resources[0].content == "91"
    assert output.execution_notes == ["complete"]
    assert output.confidence == 1.0


def test_plain_text_parser_never_raises_and_preserves_malformed_reply() -> None:
    task = Task(name="Outlier count", description="Report the outlier count.")

    scalar_notes = _parse_plain_text_output(
        '{"resources":[{"content":"14"}],"execution_notes":7}', task
    )
    malformed = _parse_plain_text_output("not valid JSON", task)
    nonfinite = _parse_plain_text_output(
        '{"resources":[{"content":"25"}],"confidence":NaN}', task
    )

    assert scalar_notes.execution_notes == ["7"]
    assert malformed.resources[0].content == "not valid JSON"
    assert nonfinite.confidence == 0.5


def test_plain_text_parser_preserves_reply_when_resource_content_is_blank() -> None:
    task = Task(name="Outlier count", description="Report the outlier count.")
    reply = (
        '{"reasoning":"done","resources":[{"name":"metric: 30",'
        '"description":"reconciliation result","content":""}],'
        '"confidence":1,"execution_notes":[]}'
    )

    output = _parse_plain_text_output(reply, task)

    assert output.resources[0].content == reply
    assert "Unstructured model output" in output.reasoning
