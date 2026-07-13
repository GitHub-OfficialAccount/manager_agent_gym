import math

import pytest

from experiments.ds_reroute.run import Recorder, TARGET_WORKER, build_schedule
from experiments.ds_reroute.scenario import (
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

    assert robust_config.model_name == screening_config.model_name
    assert robust_config.system_prompt == screening_config.system_prompt
    assert {tool.name for tool in robust_tools} == set(ROBUST_TOOL_IDS)
    assert {tool.name for tool in screening_tools} == set(SCREENING_TOOL_IDS)


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
