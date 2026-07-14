import math

import pytest

from experiments.ds_reroute.fixed_gate import (
    FIXED_ASSIGNMENTS,
    FixedNoOpManager,
    apply_fixed_assignments,
    evaluate_gate,
)
from experiments.ds_reroute.run import (
    Recorder,
    TARGET_WORKER,
    _preferences,
    build_schedule,
)
from experiments.ds_reroute.scenario import (
    COORDINATOR_TOOL_IDS,
    CORE_TOOL_IDS,
    ROBUST_TOOL_IDS,
    SCREENING_TOOL_IDS,
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
        first.reference["income"] is batch["income"]
        for batch in first.batches.values()
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
    assert all(task.assigned_agent_id is None for task in scenario.workflow.tasks.values())


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
    robust_config, robust_tools = build_worker(
        scenario, "portfolio_analyst", "robust"
    )
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
    assert robust_config.max_turns == screening_config.max_turns == 15
    assert coordinator_config.max_turns == 15
    assert {tool.name for tool in robust_tools} == set(ROBUST_TOOL_IDS)
    assert {tool.name for tool in screening_tools} == set(SCREENING_TOOL_IDS)
    assert {tool.name for tool in coordinator_tools} == set(COORDINATOR_TOOL_IDS)
    assert "portfolio_profile" not in {tool.name for tool in coordinator_tools}
    assert "analyze_audit_artifacts" in {tool.name for tool in coordinator_tools}


@pytest.mark.parametrize("condition", ["silent", "partial", "full"])
def test_primary_perturbation_changes_one_worker_and_preserves_core_tools(condition):
    schedule = build_schedule(condition, swap_timestep=3)
    manifest = schedule.manifest()

    assert manifest["num_perturbations"] == 1
    change = manifest["perturbations"][0]
    assert change["agent_id"] == TARGET_WORKER
    assert change["new_tool_ids"] == list(SCREENING_TOOL_IDS)
    assert set(CORE_TOOL_IDS) <= set(change["new_tool_ids"])
    assert change["announce"] is (condition != "silent")


def test_control_has_no_perturbation():
    assert build_schedule("control", 3).manifest()["num_perturbations"] == 0


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
        applied[scenario.task_specs[key].name] == TARGET_WORKER
        for key in ("audit_a_robust", "audit_b_robust", "audit_c_robust")
    )


def test_fixed_manager_is_constructible_and_has_no_adaptive_state():
    manager = FixedNoOpManager(_preferences())
    manager.reset()
    assert manager.get_action_buffer() == []


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
