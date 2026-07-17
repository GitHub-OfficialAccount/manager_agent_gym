"""Run the loan-audit teammate-change experiment.

Example:
    uv run python -m experiments.ds_reroute.run \
        --perturbation toolset_to_screening \
        --conditions control silent partial full --seeds 42
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from examples.common_stakeholders import create_stakeholder_agent
from manager_agent_gym import (
    AgentRegistry,
    ChainOfThoughtManagerAgent,
    WorkflowExecutionEngine,
)
from manager_agent_gym.core.common.callbacks import default_timestep_callbacks
from manager_agent_gym.core.common.model_provider import (
    disable_agents_tracing_if_proxied,
)
from manager_agent_gym.core.common.run_trace import RunTraceRecorder
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.manager_agent.observation_aids import (
    GenericSummaryObservationAid,
)
from manager_agent_gym.schemas.execution.callbacks import TimestepEndContext
from manager_agent_gym.schemas.preferences.preference import (
    Preference,
    PreferenceWeights,
)

from .perturbations import (
    DEFAULT_PERTURBATION,
    PERTURBATIONS,
    build_schedule,
    get_perturbation,
)
from .observability import build_observation_policy, get_observability
from .scenario import build_scenario, build_worker, extract_metric, is_correct, score

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

WORKER_TIERS = {
    "portfolio_analyst": "robust",
    "risk_analyst": "robust",
    "screening_analyst": "screening",
    "audit_coordinator": "coordination",
}
_METHOD_RE = re.compile(r"method\s*[:=]\s*([a-zA-Z0-9_+\- ]+)", re.IGNORECASE)


def _preferences() -> PreferenceWeights:
    return PreferenceWeights(
        preferences=[
            Preference(
                name="quality",
                weight=1.0,
                description="Complete and defensible portfolio audit",
            )
        ]
    )


class Recorder:
    def __init__(
        self, task_answers: dict[str, float], task_meta: dict[str, dict[str, Any]]
    ) -> None:
        self.task_answers = task_answers
        self.task_meta = task_meta
        self.completions: list[dict[str, Any]] = []
        self.actions: list[dict[str, Any]] = []
        self._start: dict[str, int] = {}

    async def callback(self, ctx: TimestepEndContext) -> None:
        action = ctx.manager_action
        self.actions.append(
            {
                "timestep": ctx.timestep,
                "action": action.model_dump(mode="json")
                if action is not None
                else None,
            }
        )
        for task_id in ctx.tasks_started:
            self._start.setdefault(str(task_id), ctx.timestep)
        for task_id in ctx.tasks_completed:
            task = ctx.workflow.tasks.get(task_id)
            if task is None or task.name not in self.task_answers:
                continue
            content = ""
            for resource_id in task.output_resource_ids:
                resource = ctx.workflow.resources.get(resource_id)
                if resource is not None and resource.content:
                    content = resource.content
                    break
            truth = self.task_answers[task.name]
            answer = extract_metric(content)
            method_match = _METHOD_RE.search(content)
            self.completions.append(
                {
                    "timestep": ctx.timestep,
                    "started_timestep": self._start.get(str(task_id)),
                    "task_name": task.name,
                    **self.task_meta[task.name],
                    "agent_id": task.assigned_agent_id,
                    "content": content,
                    "answer": answer,
                    "truth": truth,
                    "method_reported": method_match.group(1).strip()
                    if method_match
                    else None,
                    "correct": is_correct(answer, truth),
                    "r_check": score(answer, truth),
                }
            )

    def score_summary(self) -> dict[str, Any]:
        by_name = {row["task_name"]: row for row in self.completions}
        task_scores = {
            name: by_name[name]["r_check"] if name in by_name else 0.0
            for name in self.task_answers
        }
        return {
            "r_check": sum(task_scores.values()) / len(task_scores),
            "completed_predefined": len(by_name),
            "total_predefined": len(self.task_answers),
            "task_scores": task_scores,
        }


async def run_one(
    condition: str,
    seed: int,
    max_timesteps: int | None,
    swap_timestep: int | None,
    out_root: Path,
    perturbation: str = DEFAULT_PERTURBATION,
    observation_aid: str = "none",
) -> Path:
    definition = get_perturbation(perturbation)
    max_timesteps = definition.max_timesteps if max_timesteps is None else max_timesteps
    swap_timestep = definition.swap_timestep if swap_timestep is None else swap_timestep
    aid_suffix = "" if observation_aid == "none" else f"_{observation_aid}"
    run_dir = out_root / (
        f"{perturbation}_{condition}{aid_suffix}_t{swap_timestep}_seed{seed}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    print(
        f"DS-REROUTE perturbation={perturbation} condition={condition} seed={seed} "
        f"swap_t={swap_timestep} target={definition.target_worker}",
        flush=True,
    )

    scenario = build_scenario(seed)
    preferences = _preferences()
    registry = AgentRegistry()
    for tool_id, tool in scenario.tools.items():
        registry.register_tool(tool_id, tool)
    for agent_id, tier in WORKER_TIERS.items():
        config, tools = build_worker(scenario, agent_id, tier)
        registry.register_ai_agent(config, tools)

    schedule = build_schedule(
        condition,
        swap_timestep,
        perturbation=perturbation,
    )
    schedule.register(registry)
    observation_policy = build_observation_policy(
        condition,
        definition,
        swap_timestep,
        observation_aid=observation_aid,
    )
    manager = ChainOfThoughtManagerAgent(preferences=preferences)
    if observation_aid == "generic_summary":
        manager.set_observation_aid_builder(
            GenericSummaryObservationAid(model=manager.model_name, seed=seed)
        )
    stakeholder = create_stakeholder_agent(persona="balanced", preferences=preferences)
    recorder = Recorder(scenario.task_answers, scenario.task_meta)
    trace_recorder = RunTraceRecorder(
        metadata={
            "experiment": "ds_reroute",
            "perturbation_name": perturbation,
            "lever": definition.lever,
            "condition": condition,
            "seed": seed,
            "swap_timestep": swap_timestep,
            "max_timesteps": max_timesteps,
            "target_worker": definition.target_worker,
            "observability": get_observability(condition).manifest(),
            "observation_aid": observation_aid,
        }
    )
    engine = WorkflowExecutionEngine(
        workflow=scenario.workflow,
        agent_registry=registry,
        stakeholder_agent=stakeholder,
        manager_agent=manager,
        communication_service=CommunicationService(),
        max_timesteps=max_timesteps,
        enable_timestep_logging=True,
        enable_final_metrics_logging=False,
        timestep_end_callbacks=[
            *default_timestep_callbacks(),
            recorder.callback,
            trace_recorder.timestep_callback,
        ],
        observation_policy=observation_policy,
        seed=seed,
    )
    started_at = datetime.now().isoformat()
    try:
        with trace_recorder.activate():
            await engine.run_full_execution(save_outputs=False)
    except Exception as error:
        trace_recorder.record(
            "episode_failed",
            {
                "error_type": type(error).__name__,
                "error": str(error),
            },
            actor_type="environment",
            actor_id="workflow_engine",
        )
        trace_recorder.write_json(
            run_dir / "run.json",
            failure={
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
        raise

    score_summary = recorder.score_summary()
    manifest = {
        "condition": condition,
        "perturbation_name": perturbation,
        "lever": definition.lever,
        "seed": seed,
        "swap_timestep": swap_timestep,
        "max_timesteps": max_timesteps,
        "target_worker": definition.target_worker,
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(),
        "observation_policy": observation_policy.model_dump(mode="json"),
        "observability": get_observability(condition).manifest(),
        "perturbation": schedule.manifest(),
        "final_tools": {
            agent_id: [tool.name for tool in registry.get_agent(agent_id).tools]
            for agent_id in WORKER_TIERS
            if registry.get_agent(agent_id) is not None
        },
        "final_target_model": registry.get_agent(
            definition.target_worker
        ).config.model_name,
        **score_summary,
    }
    artifacts = {
        "manifest.json": manifest,
        "completions.json": recorder.completions,
        "manager_actions.json": recorder.actions,
        "tool_calls.json": scenario.tool_calls,
        "task_ground_truth.json": {
            key: {
                "name": spec.name,
                "stage": spec.stage,
                "truth": spec.truth,
                "method": spec.method,
                "dependencies": list(spec.dependencies),
            }
            for key, spec in scenario.task_specs.items()
        },
    }
    for filename, payload in artifacts.items():
        (run_dir / filename).write_text(json.dumps(payload, indent=2))
    trace_recorder.write_json(
        run_dir / "run.json",
        manifest=manifest,
        completions=recorder.completions,
        manager_actions=recorder.actions,
        tool_calls=scenario.tool_calls,
        task_ground_truth=artifacts["task_ground_truth.json"],
    )
    print(
        f"{condition}: R_check={score_summary['r_check']:.3f} "
        f"completed={score_summary['completed_predefined']}/"
        f"{score_summary['total_predefined']} -> {run_dir}",
        flush=True,
    )
    return run_dir


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=["control", "silent", "partial", "full"],
        choices=["control", "silent", "partial", "full"],
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=[42])
    parser.add_argument(
        "--max-timesteps",
        type=int,
        default=None,
        help="Override the selected perturbation's manager-run horizon.",
    )
    parser.add_argument(
        "--swap-timestep",
        type=int,
        default=None,
        help="Override the selected perturbation's default change timestep.",
    )
    parser.add_argument(
        "--perturbation",
        choices=sorted(PERTURBATIONS),
        default=DEFAULT_PERTURBATION,
    )
    parser.add_argument(
        "--out", type=Path, default=Path("experiments/ds_reroute/outputs")
    )
    parser.add_argument(
        "--observation-aid",
        choices=["none", "generic_summary"],
        default="none",
        help="Phase-2 representation arm; 'none' preserves the native baseline.",
    )
    args = parser.parse_args()
    for seed in args.seeds:
        for condition in args.conditions:
            await run_one(
                condition,
                seed,
                args.max_timesteps,
                args.swap_timestep,
                args.out,
                args.perturbation,
                args.observation_aid,
            )


if __name__ == "__main__":
    asyncio.run(main())
