"""Fixed-assignment manipulation and scripted-recovery gate for ds_reroute.

The reference manager cannot adapt: all predefined tasks are assigned before
execution and it only observes or retries incidental failures under the same
assignment. This isolates whether the scheduled worker change causes a graded
immediate and downstream loss. A third arm routes the affected robust audits to
the stable percentile-capable worker, proving that recovery is feasible without
changing the environment or workers.

Run:
    uv run python -m experiments.ds_reroute.fixed_gate --seed 42
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from statistics import mean
from typing import Any

from examples.common_stakeholders import create_stakeholder_agent
from manager_agent_gym import AgentRegistry, WorkflowExecutionEngine
from manager_agent_gym.core.common.model_provider import (
    disable_agents_tracing_if_proxied,
)
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.manager_agent.interface import ManagerAgent
from manager_agent_gym.schemas.execution.manager_actions import (
    BaseManagerAction,
    NoOpAction,
    RetryTaskAction,
)
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy

from .run import Recorder, TARGET_WORKER, WORKER_TIERS, _preferences, build_schedule
from .scenario import JUDGMENT_WORKER_MODEL, Scenario, build_scenario, build_worker

FIXED_ASSIGNMENTS = {
    "profile": TARGET_WORKER,
    "calibrate_portfolio": TARGET_WORKER,
    "calibrate_risk": "risk_analyst",
    "calibrate_screen": "screening_analyst",
    "calibration_review": "audit_coordinator",
    "audit_a_robust": TARGET_WORKER,
    "audit_b_robust": TARGET_WORKER,
    "audit_c_robust": TARGET_WORKER,
    "audit_a_screen": "screening_analyst",
    "audit_b_screen": "screening_analyst",
    "audit_c_screen": "screening_analyst",
    "reconcile_a": "audit_coordinator",
    "reconcile_b": "audit_coordinator",
    "reconcile_c": "audit_coordinator",
    "prioritize": "audit_coordinator",
    "capacity": "audit_coordinator",
}

RECOVERY_ASSIGNMENTS = {
    **FIXED_ASSIGNMENTS,
    "audit_a_robust": "risk_analyst",
    "audit_b_robust": "risk_analyst",
    "audit_c_robust": "risk_analyst",
}


class FixedNoOpManager(ManagerAgent):
    """Native manager reference policy with no adaptive actions."""

    def __init__(self, preferences):
        super().__init__(agent_id="fixed_noop_manager", preferences=preferences)

    def reset(self) -> None:
        self._action_buffer.clear()

    async def step(self, **_kwargs) -> BaseManagerAction:
        return NoOpAction(reasoning="Fixed-assignment manipulation check.")


class FixedRetryManager(FixedNoOpManager):
    """Fixed routing with native same-agent retries for incidental run failures."""

    async def step(self, **kwargs) -> BaseManagerAction:
        failed_task_ids = kwargs.get("failed_task_ids") or set()
        if failed_task_ids:
            task_id = sorted(failed_task_ids, key=str)[0]
            return RetryTaskAction(
                reasoning=(
                    "Retrying an incidental worker-run failure without changing "
                    "the fixed assignment policy."
                ),
                task_id=task_id,
            )
        return await super().step(**kwargs)


def apply_fixed_assignments(
    scenario: Scenario,
    assignments: dict[str, str] | None = None,
) -> dict[str, str]:
    assignments = assignments or FIXED_ASSIGNMENTS
    by_name = {task.name: task for task in scenario.workflow.tasks.values()}
    applied = {}
    for key, agent_id in assignments.items():
        task_name = scenario.task_specs[key].name
        by_name[task_name].assigned_agent_id = agent_id
        applied[task_name] = agent_id
    return applied


def _stage_mean(completions: list[dict[str, Any]], stages: set[str]) -> float:
    values = [row["r_check"] for row in completions if row["stage"] in stages]
    return mean(values) if values else 0.0


async def run_fixed(
    condition: str,
    seed: int,
    swap_timestep: int,
    max_timesteps: int,
    out_root: Path,
    lever: str = "toolset",
    weak_model: str = JUDGMENT_WORKER_MODEL,
) -> dict[str, Any]:
    scenario = build_scenario(seed)
    assignment_policy = (
        RECOVERY_ASSIGNMENTS if condition == "recovery" else FIXED_ASSIGNMENTS
    )
    assignments = apply_fixed_assignments(scenario, assignment_policy)
    preferences = _preferences()
    registry = AgentRegistry()
    for tool_id, tool in scenario.tools.items():
        registry.register_tool(tool_id, tool)
    for agent_id, tier in WORKER_TIERS.items():
        config, tools = build_worker(scenario, agent_id, tier)
        registry.register_ai_agent(config, tools)

    schedule = build_schedule(
        "control" if condition == "control" else "silent",
        swap_timestep,
        lever=lever,
        weak_model=weak_model,
    )
    schedule.register(registry)
    recorder = Recorder(scenario.task_answers, scenario.task_meta)
    observation_policy = ObservationPolicy(
        expose_worker_system_prompts=False,
        worker_metadata="capabilities",
        quality_digest="none",
    )
    engine = WorkflowExecutionEngine(
        workflow=scenario.workflow,
        agent_registry=registry,
        stakeholder_agent=create_stakeholder_agent(
            persona="balanced", preferences=preferences
        ),
        manager_agent=FixedRetryManager(preferences),
        communication_service=CommunicationService(),
        max_timesteps=max_timesteps,
        enable_timestep_logging=False,
        enable_final_metrics_logging=False,
        timestep_end_callbacks=[recorder.callback],
        observation_policy=observation_policy,
        seed=seed,
    )
    await engine.run_full_execution(save_outputs=False)

    score_summary = recorder.score_summary()
    robust_audits = [
        row
        for row in recorder.completions
        if row["stage"] == "audit" and row["method"] == "percentile"
    ]
    downstream_stages = {"reconciliation", "prioritization", "capacity"}
    result = {
        "condition": condition,
        "lever": lever,
        "seed": seed,
        "swap_timestep": swap_timestep,
        "assignments": assignments,
        "perturbation": schedule.manifest(),
        "r_check": score_summary["r_check"],
        "completed_predefined": score_summary["completed_predefined"],
        "total_predefined": score_summary["total_predefined"],
        "robust_audit_r_check": _stage_mean(recorder.completions, {"audit"})
        if robust_audits
        else 0.0,
        "robust_audit_only_r_check": mean(row["r_check"] for row in robust_audits)
        if robust_audits
        else 0.0,
        "downstream_r_check": _stage_mean(recorder.completions, downstream_stages),
        "robust_audits": robust_audits,
        "completions": recorder.completions,
        "tool_calls": scenario.tool_calls,
        "native_reward_final": engine.validation_engine.most_recent_reward,
        "native_reward_vector": engine.validation_engine.reward_vector,
        "task_states": {
            task.name: {
                "status": task.status.value,
                "execution_notes": task.execution_notes,
            }
            for task in scenario.workflow.tasks.values()
        },
        "final_target_tools": [
            tool.name for tool in registry.get_agent(TARGET_WORKER).tools
        ],
        "final_target_model": registry.get_agent(TARGET_WORKER).config.model_name,
    }
    run_dir = out_root / f"fixed_{lever}_{condition}_t{swap_timestep}_seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "result.json").write_text(json.dumps(result, indent=2))
    print(
        f"fixed {condition}: R_check={result['r_check']:.3f} "
        f"robust={result['robust_audit_only_r_check']:.3f} "
        f"downstream={result['downstream_r_check']:.3f} "
        f"completed={result['completed_predefined']}/{result['total_predefined']}",
        flush=True,
    )
    return result


def evaluate_gate(
    control: dict[str, Any], degradation: dict[str, Any]
) -> dict[str, Any]:
    degraded_audits = degradation["robust_audits"]
    downstream_loss = control["downstream_r_check"] - degradation["downstream_r_check"]
    all_completions = control["completions"] + degradation["completions"]
    checks = {
        "same_assignments": control["assignments"] == degradation["assignments"],
        "both_complete": (
            control["completed_predefined"] == control["total_predefined"]
            and degradation["completed_predefined"] == degradation["total_predefined"]
        ),
        "control_robust_at_least_0_95": control["robust_audit_only_r_check"] >= 0.95,
        "robust_loss_at_least_0_15": (
            control["robust_audit_only_r_check"]
            - degradation["robust_audit_only_r_check"]
        )
        >= 0.15,
        "degraded_outputs_remain_numeric": (
            len(degraded_audits) == 3
            and all(row["answer"] is not None for row in degraded_audits)
        ),
        "audits_start_after_change": (
            len(degraded_audits) == 3
            and all(
                row["started_timestep"] >= degradation["swap_timestep"]
                for row in degraded_audits
            )
        ),
        "completed_outputs_are_nonempty": (
            len(all_completions)
            == control["total_predefined"] + degradation["total_predefined"]
            and all(str(row["content"] or "").strip() for row in all_completions)
        ),
        "downstream_loss_is_observable": downstream_loss > 0.0,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "robust_audit_loss": (
            control["robust_audit_only_r_check"]
            - degradation["robust_audit_only_r_check"]
        ),
        "downstream_loss": downstream_loss,
        "episode_loss": control["r_check"] - degradation["r_check"],
    }


def evaluate_recovery_gate(
    control: dict[str, Any],
    degradation: dict[str, Any],
    recovery: dict[str, Any],
) -> dict[str, Any]:
    manipulation = evaluate_gate(control, degradation)
    recovered_audits = recovery["robust_audits"]
    checks = {
        "manipulation_gate_passed": manipulation["passed"],
        "recovery_complete": (
            recovery["completed_predefined"] == recovery["total_predefined"]
        ),
        "affected_audits_rerouted_to_risk": (
            len(recovered_audits) == 3
            and all(row["agent_id"] == "risk_analyst" for row in recovered_audits)
        ),
        "recovered_audits_start_after_change": (
            len(recovered_audits) == 3
            and all(
                row["started_timestep"] >= recovery["swap_timestep"]
                for row in recovered_audits
            )
        ),
        "robust_quality_near_control": (
            recovery["robust_audit_only_r_check"]
            >= control["robust_audit_only_r_check"] - 0.05
        ),
        "downstream_quality_near_control": (
            recovery["downstream_r_check"] >= control["downstream_r_check"] - 0.05
        ),
        "episode_quality_near_control": (
            recovery["r_check"] >= control["r_check"] - 0.05
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "manipulation": manipulation,
        "recovery_vs_control": {
            "episode_gap": control["r_check"] - recovery["r_check"],
            "robust_audit_gap": (
                control["robust_audit_only_r_check"]
                - recovery["robust_audit_only_r_check"]
            ),
            "downstream_gap": (
                control["downstream_r_check"] - recovery["downstream_r_check"]
            ),
        },
    }


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--swap-timestep", type=int, default=3)
    parser.add_argument("--max-timesteps", type=int, default=32)
    parser.add_argument("--lever", choices=["toolset", "judgment"], default="toolset")
    parser.add_argument(
        "--weak-model",
        default=JUDGMENT_WORKER_MODEL,
        help="Replacement model used by the judgment lever.",
    )
    parser.add_argument(
        "--out", type=Path, default=Path("experiments/ds_reroute/outputs/fixed_gate")
    )
    args = parser.parse_args()
    control = await run_fixed(
        "control",
        args.seed,
        args.swap_timestep,
        args.max_timesteps,
        args.out,
        args.lever,
        args.weak_model,
    )
    degradation = await run_fixed(
        "degradation",
        args.seed,
        args.swap_timestep,
        args.max_timesteps,
        args.out,
        args.lever,
        args.weak_model,
    )
    recovery = await run_fixed(
        "recovery",
        args.seed,
        args.swap_timestep,
        args.max_timesteps,
        args.out,
        args.lever,
        args.weak_model,
    )
    gate = evaluate_recovery_gate(control, degradation, recovery)
    (
        args.out / f"gate_{args.lever}_t{args.swap_timestep}_seed{args.seed}.json"
    ).write_text(json.dumps(gate, indent=2))
    print(json.dumps(gate, indent=2), flush=True)
    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
