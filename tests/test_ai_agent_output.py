from agents import function_tool
from agents.extensions.models.litellm_model import LitellmModel

from manager_agent_gym.core.workflow_agents.ai_agent import (
    AIAgent,
    _parse_plain_text_output,
)
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
