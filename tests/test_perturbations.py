import pytest
from agents import function_tool

from manager_agent_gym.core.workflow_agents.registry import AgentRegistry
from manager_agent_gym.schemas.execution.perturbations import (
    ModelSwap,
    PerturbationSchedule,
    PromptSwap,
)
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig


def _worker_config(agent_id: str = "w1", prompt: str = "original policy") -> AIAgentConfig:
    return AIAgentConfig(
        agent_id=agent_id,
        agent_type="ai",
        system_prompt=prompt,
        model_name="gpt-4o",
        agent_description="a diligent analyst",
        agent_capabilities=["analysis"],
    )


@function_tool
def _noop_tool() -> str:
    """Placeholder tool so tests avoid the default (network-dependent) toolset."""
    return "ok"


@pytest.mark.asyncio
async def test_prompt_swap_replaces_agent_in_place() -> None:
    reg = AgentRegistry()
    reg.register_ai_agent(_worker_config(), additional_tools=[_noop_tool])
    original_instance = reg.get_agent("w1")

    reg.schedule_prompt_swap(
        timestep=3, agent_id="w1", new_system_prompt="degraded policy"
    )
    # nothing happens before the scheduled timestep
    changes = await reg.apply_scheduled_changes_for_timestep(2)
    assert changes == []
    assert reg.get_agent("w1").config.system_prompt == "original policy"

    changes = await reg.apply_scheduled_changes_for_timestep(3)
    assert len(changes) == 1
    assert "Replaced w1" in changes[0]
    assert "(silent)" in changes[0]

    agent = reg.get_agent("w1")
    assert agent is not None
    assert agent.config.system_prompt == "degraded policy"
    # same id, new instance (the underlying SDK agent caches the prompt)
    assert agent is not original_instance
    # visible metadata unchanged — the swap is silent
    assert agent.config.agent_description == "a diligent analyst"
    assert agent.config.agent_capabilities == ["analysis"]
    assert len(reg.list_agents()) == 1


@pytest.mark.asyncio
async def test_model_swap_replaces_model_in_place() -> None:
    reg = AgentRegistry()
    reg.register_ai_agent(_worker_config(), additional_tools=[_noop_tool])

    reg.schedule_model_swap(
        timestep=2, agent_id="w1", new_model_name="openrouter/weak/model"
    )
    changes = await reg.apply_scheduled_changes_for_timestep(2)
    assert len(changes) == 1
    assert "Replaced w1 [model_name]" in changes[0]

    agent = reg.get_agent("w1")
    assert agent is not None
    # model changed, but policy and visible metadata untouched
    assert agent.config.model_name == "openrouter/weak/model"
    assert agent.config.system_prompt == "original policy"
    assert agent.config.agent_description == "a diligent analyst"


@pytest.mark.asyncio
async def test_tool_swap_replaces_toolset() -> None:
    from agents import function_tool

    @function_tool
    def basic() -> str:
        return "b"

    reg = AgentRegistry()
    reg.register_tool("basic", basic)
    reg.register_ai_agent(_worker_config(), additional_tools=[_noop_tool])
    assert any(t.name == "_noop_tool" for t in reg.get_agent("w1").tools)

    reg.schedule_tool_swap(timestep=1, agent_id="w1", new_tool_ids=["basic"])
    changes = await reg.apply_scheduled_changes_for_timestep(1)
    assert "Replaced w1 [tools]" in changes[0]
    names = [t.name for t in reg.get_agent("w1").tools]
    assert "basic" in names and "_noop_tool" not in names  # swapped, not kept


@pytest.mark.asyncio
async def test_prompt_swap_unknown_agent_reports_failure() -> None:
    reg = AgentRegistry()
    reg.schedule_prompt_swap(timestep=0, agent_id="ghost", new_system_prompt="x")
    changes = await reg.apply_scheduled_changes_for_timestep(0)
    assert len(changes) == 1
    assert "Could not replace ghost" in changes[0]


def test_schedule_registers_and_manifests() -> None:
    swap = PromptSwap(
        timestep=8,
        agent_id="documentation_lead",
        new_system_prompt="degraded",
        label="competence_degradation",
    )
    schedule = PerturbationSchedule(perturbations=[swap])

    reg = AgentRegistry()
    schedule.register(reg)
    assert 8 in reg._scheduled_changes
    change = reg._scheduled_changes[8][0]
    assert change.action == "replace"
    assert change.agent_id == "documentation_lead"
    assert change.announce is False

    manifest = schedule.manifest()
    assert manifest["num_perturbations"] == 1
    entry = manifest["perturbations"][0]
    assert entry["kind"] == "prompt_swap"
    assert entry["timestep"] == 8
    assert entry["new_system_prompt"] == "degraded"
    assert entry["label"] == "competence_degradation"


def test_schedule_accepts_mixed_perturbations_and_dispatches() -> None:
    schedule = PerturbationSchedule(
        perturbations=[
            PromptSwap(timestep=5, agent_id="a", new_system_prompt="p"),
            ModelSwap(timestep=8, agent_id="b", new_model_name="openrouter/weak/model",
                      label="capability_degradation"),
        ]
    )
    reg = AgentRegistry()
    schedule.register(reg)
    assert reg._scheduled_changes[5][0].new_system_prompt == "p"
    assert reg._scheduled_changes[5][0].new_model_name is None
    assert reg._scheduled_changes[8][0].new_model_name == "openrouter/weak/model"
    assert reg._scheduled_changes[8][0].new_system_prompt is None

    manifest = schedule.manifest()
    assert manifest["num_perturbations"] == 2
    kinds = {p["kind"] for p in manifest["perturbations"]}
    assert kinds == {"prompt_swap", "model_swap"}


def test_empty_schedule_manifest() -> None:
    manifest = PerturbationSchedule().manifest()
    assert manifest == {"num_perturbations": 0, "perturbations": []}
