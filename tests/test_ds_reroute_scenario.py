import math
from dataclasses import replace

import pytest

from manager_agent_gym import AgentRegistry
from manager_agent_gym.core.workflow_agents.prompts.ai_agent_prompts import (
    AI_AGENT_TASK_TEMPLATE,
)

from experiments.ds_reroute.fixed_gate import (
    FIXED_ASSIGNMENTS,
    RECOVERY_ASSIGNMENTS,
    FixedNoOpManager,
    FixedRetryManager,
    apply_fixed_assignments,
    evaluate_gate,
    evaluate_recovery_gate,
)
from experiments.ds_reroute.perturbations import (
    DEGRADED_JUDGMENT_PROMPT,
    MODEL_PROMPT_JUDGMENT,
    PRIMARY_TARGET_WORKER,
    TOOLSET_TO_SCREENING,
    build_schedule,
    get_perturbation,
)
from experiments.ds_reroute.run import Recorder, _preferences
from experiments.ds_reroute.scenario import (
    COORDINATOR_TOOL_IDS,
    CORE_TOOL_IDS,
    ROBUST_TOOL_IDS,
    SCREENING_TOOL_IDS,
    WORKER_PROMPT,
    build_scenario,
    build_worker,
    extract_metric,
    score,
)


def test_scenario_is_deterministic_and_uses_held_out_batches():
    first = build_scenario(42)
    second = build_scenario(42)
    other = build_scenario(43)

    assert first.task_answers == second.task_answers
    assert first.task_answers != other.task_answers
    assert len(first.reference["income"]) == 2000
    assert all(len(batch["income"]) == 400 for batch in first.batches.values())
    assert not any(
        first.reference["income"] is batch["income"] for batch in first.batches.values()
    )


def test_task_dag_has_parallel_forks_and_downstream_joins():
    scenario = build_scenario(42)
    specs = scenario.task_specs

    calibration = [spec for spec in specs.values() if spec.stage == "calibration"]
    audits = [spec for spec in specs.values() if spec.stage == "audit"]
    reconciliations = [
        spec for spec in specs.values() if spec.stage == "reconciliation"
    ]

    assert len(specs) == 16
    assert len(calibration) == 3
    assert all(spec.dependencies == ("profile",) for spec in calibration)
    assert len(audits) == 6
    assert all(spec.dependencies == ("calibration_review",) for spec in audits)
    assert len(reconciliations) == 3
    assert all(len(spec.dependencies) == 2 for spec in reconciliations)
    assert len(specs["prioritize"].dependencies) == 3
    assert all(
        task.assigned_agent_id is None for task in scenario.workflow.tasks.values()
    )


def test_tool_tiers_share_core_access_but_are_not_supersets():
    robust = set(ROBUST_TOOL_IDS)
    screening = set(SCREENING_TOOL_IDS)

    assert set(CORE_TOOL_IDS) <= robust & screening
    assert "portfolio_profile" in robust & screening
    assert "analyze_audit_artifacts" not in robust | screening
    assert "flag_outliers_percentile" in robust - screening
    assert "flag_outliers_zscore" in screening - robust
    assert not robust < screening
    assert not screening < robust


def test_workers_use_same_model_and_prompt_with_alternative_tools():
    scenario = build_scenario(42)
    robust_config, robust_tools = build_worker(scenario, "portfolio_analyst", "robust")
    screening_config, screening_tools = build_worker(
        scenario, "screening_analyst", "screening"
    )
    coordinator_config, coordinator_tools = build_worker(
        scenario, "audit_coordinator", "coordination"
    )

    assert robust_config.model_name == screening_config.model_name
    assert robust_config.model_name == coordinator_config.model_name
    assert robust_config.system_prompt == screening_config.system_prompt
    assert robust_config.system_prompt == coordinator_config.system_prompt
    assert robust_config.max_turns == screening_config.max_turns == 30
    assert coordinator_config.max_turns == 30
    assert {tool.name for tool in robust_tools} == set(ROBUST_TOOL_IDS)
    assert {tool.name for tool in screening_tools} == set(SCREENING_TOOL_IDS)
    assert {tool.name for tool in coordinator_tools} == set(COORDINATOR_TOOL_IDS)
    assert "portfolio_profile" not in {tool.name for tool in coordinator_tools}
    assert "analyze_audit_artifacts" in {tool.name for tool in coordinator_tools}

    robust_by_name = {tool.name: tool for tool in robust_tools}
    screening_by_name = {tool.name: tool for tool in screening_tools}
    coordinator_by_name = {tool.name: tool for tool in coordinator_tools}
    robust_description = " ".join(
        robust_by_name["flag_outliers_percentile"].description.lower().split()
    )
    screening_description = " ".join(
        screening_by_name["flag_outliers_zscore"].description.lower().split()
    )
    coordinator_description = " ".join(
        coordinator_by_name["analyze_audit_artifacts"].description.lower().split()
    )
    assert "identical for batch a, b, or c" in robust_description
    assert "complete four-column result" in screening_description
    assert "repeating the same operation" in coordinator_description


def test_worker_prompt_preserves_tool_choice_and_defines_a_stopping_policy():
    prompt = WORKER_PROMPT.lower()

    assert "may decide not to use them" in prompt
    assert "do not change over time" in prompt
    assert "completed workflow artifacts are immutable" in prompt
    assert "at most one additional verification" in prompt
    assert "default action" in prompt and "finalize immediately" in prompt
    assert "identical deterministic tool call is not verification" in prompt
    assert "must never be repeated" in prompt
    assert "do not use tools merely to increase confidence" in prompt
    assert "final resource is the completion signal" in prompt
    assert "return it immediately" in prompt


def test_shared_task_prompt_does_not_invite_open_ended_verification():
    prompt = AI_AGENT_TASK_TEMPLATE.lower()

    assert "use available tools when useful" in prompt
    assert "reasonable verification" not in prompt
    assert "once you are satisfied" not in prompt


def test_worker_profiles_expose_faithful_primary_and_method_baseline():
    scenario = build_scenario(42)
    portfolio, _ = build_worker(scenario, "portfolio_analyst", "robust")
    risk, _ = build_worker(scenario, "risk_analyst", "robust")
    screening, _ = build_worker(scenario, "screening_analyst", "screening")

    assert portfolio.agent_description.startswith("Primary:")
    assert risk.agent_description.startswith("Primary:")
    assert screening.agent_description.startswith("Primary:")
    assert "Methods: percentile outlier screening" in portfolio.agent_capabilities
    assert "Methods: percentile outlier screening" in risk.agent_capabilities
    assert "Methods: mean-plus-two-SD screening" in screening.agent_capabilities


@pytest.mark.parametrize(
    ("condition", "visible_method"),
    [
        ("silent", None),
        ("partial", "Methods: changed; current outlier-screening method unknown"),
        ("full", "Methods: mean-plus-two-SD screening"),
    ],
)
def test_primary_perturbation_changes_one_worker_and_preserves_core_tools(
    condition, visible_method
):
    schedule = build_schedule(condition, swap_timestep=3)
    manifest = schedule.manifest()

    assert manifest["num_perturbations"] == 1
    change = manifest["perturbations"][0]
    assert change["agent_id"] == PRIMARY_TARGET_WORKER
    assert change["new_tool_ids"] == list(SCREENING_TOOL_IDS)
    assert set(CORE_TOOL_IDS) <= set(change["new_tool_ids"])
    assert change["announce"] is (condition != "silent")
    capabilities = change["new_agent_capabilities"]
    if visible_method is None:
        assert capabilities is None
    else:
        assert visible_method in capabilities
        assert "Methods: portfolio profiling" in capabilities


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("condition", "expected_method"),
    [
        ("silent", "Methods: percentile outlier screening"),
        ("partial", "Methods: changed; current outlier-screening method unknown"),
        ("full", "Methods: mean-plus-two-SD screening"),
    ],
)
async def test_primary_perturbation_applies_condition_visible_capabilities(
    condition, expected_method
):
    scenario = build_scenario(42)
    config, tools = build_worker(scenario, PRIMARY_TARGET_WORKER, "robust")
    registry = AgentRegistry()
    for tool_id, tool in scenario.tools.items():
        registry.register_tool(tool_id, tool)
    registry.register_ai_agent(config, tools)
    schedule = build_schedule(condition, swap_timestep=3)
    schedule.register(registry)

    await registry.apply_scheduled_changes_for_timestep(3)

    changed = registry.get_agent(PRIMARY_TARGET_WORKER)
    assert changed is not None
    assert expected_method in changed.config.agent_capabilities
    assert changed.config.agent_description == config.agent_description


def test_control_has_no_perturbation():
    assert build_schedule("control", 3).manifest()["num_perturbations"] == 0


@pytest.mark.parametrize("condition", ["silent", "partial", "full"])
def test_judgment_perturbation_bundles_model_and_prompt_without_tool_swap(condition):
    approved_model = "openrouter/explicitly-approved/test-model"
    definition = replace(
        get_perturbation(MODEL_PROMPT_JUDGMENT),
        replacement_model=approved_model,
    )
    manifest = definition.build_schedule(condition, 3).manifest()

    assert manifest["num_perturbations"] == 2
    model_change, prompt_change = manifest["perturbations"]
    assert model_change["kind"] == "model_swap"
    assert model_change["agent_id"] == PRIMARY_TARGET_WORKER
    assert model_change["new_model_name"] == approved_model
    assert model_change["announce"] is False
    assert prompt_change["kind"] == "prompt_swap"
    assert prompt_change["agent_id"] == PRIMARY_TARGET_WORKER
    assert prompt_change["new_system_prompt"] == DEGRADED_JUDGMENT_PROMPT
    assert prompt_change["announce"] is (condition != "silent")


@pytest.mark.asyncio
async def test_judgment_perturbation_preserves_full_robust_tool_access():
    approved_model = "openrouter/explicitly-approved/test-model"
    scenario = build_scenario(42)
    config, tools = build_worker(scenario, PRIMARY_TARGET_WORKER, "robust")
    registry = AgentRegistry()
    for tool_id, tool in scenario.tools.items():
        registry.register_tool(tool_id, tool)
    registry.register_ai_agent(config, tools)
    definition = replace(
        get_perturbation(MODEL_PROMPT_JUDGMENT),
        replacement_model=approved_model,
    )
    definition.build_schedule("silent", 3).register(registry)

    await registry.apply_scheduled_changes_for_timestep(3)

    changed = registry.get_agent(PRIMARY_TARGET_WORKER)
    assert changed is not None
    assert changed.config.model_name == approved_model
    assert changed.config.system_prompt == DEGRADED_JUDGMENT_PROMPT
    assert changed.config.agent_capabilities == config.agent_capabilities
    changed_tool_names = {tool.name for tool in changed.tools}
    assert set(ROBUST_TOOL_IDS) <= changed_tool_names
    assert set(CORE_TOOL_IDS) <= changed_tool_names


def test_judgment_perturbation_requires_an_explicitly_approved_model():
    with pytest.raises(ValueError, match="explicitly approved"):
        build_schedule("silent", 3, perturbation=MODEL_PROMPT_JUDGMENT)


def test_named_perturbation_centralizes_target_and_lever_metadata():
    toolset = get_perturbation(TOOLSET_TO_SCREENING)
    judgment = get_perturbation(MODEL_PROMPT_JUDGMENT)

    assert toolset.target_worker == judgment.target_worker == PRIMARY_TARGET_WORKER
    assert toolset.lever == "toolset"
    assert judgment.lever == "judgment"
    assert toolset.swap_timestep == 3
    assert toolset.max_timesteps == 32
    assert toolset.fixed_gate_max_timesteps == 32
    assert judgment.replacement_model is None


def test_schedule_uses_definition_swap_timestep_by_default():
    manifest = build_schedule("silent").manifest()

    assert manifest["perturbations"][0]["timestep"] == 3


def test_held_out_methods_produce_a_graded_gap():
    scenario = build_scenario(42)
    for batch_id in ("a", "b", "c"):
        robust = scenario.task_specs[f"audit_{batch_id}_robust"].truth
        screening = scenario.task_specs[f"audit_{batch_id}_screen"].truth
        degraded_score = score(screening, robust)
        assert robust != screening
        assert 0.0 < degraded_score < 1.0


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("metric: 17\nmethod: percentile", 17.0),
        ('{"metric": 102, "method": "percentile"}', 102.0),
        ("{'metric': 132, 'method': 'percentile'}", 132.0),
        ("**metric**: 74", 74.0),
        ("`metric`: 99", 99.0),
        ("metric: 30\ndetails: robust count=143, screening count=113", 30.0),
        ("answer = 1,234.5", 1234.5),
        ("42", 42.0),
        ("metric: NaN", None),
        ("no numeric result", None),
    ],
)
def test_metric_parser(text, expected):
    assert extract_metric(text) == expected


def test_grader_is_finite_and_missing_predefined_tasks_score_zero():
    scenario = build_scenario(42)
    recorder = Recorder(scenario.task_answers, scenario.task_meta)
    summary = recorder.score_summary()

    assert summary["r_check"] == 0.0
    assert summary["completed_predefined"] == 0
    assert summary["total_predefined"] == 16
    assert score(None, 10.0) == 0.0
    assert score(math.nan, 10.0) == 0.0
    assert score(10.0, 10.0) == 1.0


def test_fixed_gate_assigns_every_task_without_prescribing_a_runtime_recovery():
    scenario = build_scenario(42)
    applied = apply_fixed_assignments(scenario)

    assert len(applied) == len(scenario.task_specs) == len(FIXED_ASSIGNMENTS)
    assert all(task.assigned_agent_id for task in scenario.workflow.tasks.values())
    assert all(
        applied[scenario.task_specs[key].name] == PRIMARY_TARGET_WORKER
        for key in ("audit_a_robust", "audit_b_robust", "audit_c_robust")
    )


def test_scripted_recovery_routes_only_affected_audits_to_stable_worker():
    changed_keys = {
        key
        for key in FIXED_ASSIGNMENTS
        if FIXED_ASSIGNMENTS[key] != RECOVERY_ASSIGNMENTS[key]
    }
    assert changed_keys == {"audit_a_robust", "audit_b_robust", "audit_c_robust"}
    assert all(RECOVERY_ASSIGNMENTS[key] == "risk_analyst" for key in changed_keys)


def test_fixed_manager_is_constructible_and_has_no_adaptive_state():
    manager = FixedNoOpManager(_preferences())
    manager.reset()
    assert manager.get_action_buffer() == []


@pytest.mark.asyncio
async def test_fixed_retry_manager_retries_without_reassignment():
    scenario = build_scenario(42)
    task_id = next(iter(scenario.workflow.tasks))
    action = await FixedRetryManager(_preferences()).step(failed_task_ids={task_id})

    assert action.action_type == "retry_task"
    assert action.task_id == task_id
    assert action.agent_id is None


def test_gate_evaluation_requires_immediate_and_downstream_loss():
    assignments = {"task": "worker"}
    control = {
        "assignments": assignments,
        "completed_predefined": 16,
        "total_predefined": 16,
        "robust_audit_only_r_check": 1.0,
        "downstream_r_check": 1.0,
        "r_check": 1.0,
        "completions": [{"content": "metric: 1"}] * 16,
    }
    degradation = {
        "assignments": assignments,
        "completed_predefined": 16,
        "total_predefined": 16,
        "robust_audit_only_r_check": 0.75,
        "downstream_r_check": 0.4,
        "r_check": 0.7,
        "swap_timestep": 3,
        "completions": [{"content": "metric: 1"}] * 16,
        "robust_audits": [
            {"answer": 74.0, "started_timestep": 3},
            {"answer": 113.0, "started_timestep": 3},
            {"answer": 99.0, "started_timestep": 3},
        ],
    }

    result = evaluate_gate(control, degradation)

    assert result["passed"] is True
    assert result["robust_audit_loss"] == pytest.approx(0.25)
    assert result["downstream_loss"] == pytest.approx(0.6)
    assert result["checks"]["completed_outputs_are_nonempty"] is True


def test_recovery_gate_requires_near_control_quality_and_risk_routing():
    assignments = {"task": "worker"}
    control = {
        "assignments": assignments,
        "completed_predefined": 16,
        "total_predefined": 16,
        "robust_audit_only_r_check": 1.0,
        "downstream_r_check": 1.0,
        "r_check": 1.0,
        "completions": [{"content": "metric: 1"}] * 16,
    }
    degradation = {
        "assignments": assignments,
        "completed_predefined": 16,
        "total_predefined": 16,
        "robust_audit_only_r_check": 0.75,
        "downstream_r_check": 0.4,
        "r_check": 0.7,
        "swap_timestep": 3,
        "completions": [{"content": "metric: 1"}] * 16,
        "robust_audits": [
            {"answer": 74.0, "started_timestep": 3},
            {"answer": 113.0, "started_timestep": 3},
            {"answer": 99.0, "started_timestep": 3},
        ],
    }
    recovery = {
        "completed_predefined": 16,
        "total_predefined": 16,
        "robust_audit_only_r_check": 1.0,
        "downstream_r_check": 1.0,
        "r_check": 1.0,
        "swap_timestep": 3,
        "robust_audits": [
            {"agent_id": "risk_analyst", "started_timestep": 5},
            {"agent_id": "risk_analyst", "started_timestep": 5},
            {"agent_id": "risk_analyst", "started_timestep": 5},
        ],
    }

    result = evaluate_recovery_gate(control, degradation, recovery)

    assert result["passed"] is True
    assert all(result["checks"].values())
