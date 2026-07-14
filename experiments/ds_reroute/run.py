"""Run the loan-audit teammate-change experiment.

Example:
    uv run python -m experiments.ds_reroute.run \
        --conditions control silent partial full --seeds 42 --swap-timestep 3
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
from manager_agent_gym.schemas.execution.callbacks import TimestepEndContext
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.execution.perturbations import (
    ModelSwap,
    PerturbationSchedule,
    PromptSwap,
    ToolSwap,
)
from manager_agent_gym.schemas.preferences.evaluator import (
    AggregationStrategy,
    Evaluator,
)
from manager_agent_gym.schemas.preferences.preference import (
    Preference,
    PreferenceWeights,
)
from manager_agent_gym.schemas.preferences.rubric import RunCondition, WorkflowRubric

from .scenario import (
    DEGRADED_JUDGMENT_PROMPT,
    JUDGMENT_WORKER_MODEL,
    SCREENING_TOOL_IDS,
    build_scenario,
    build_worker,
    extract_metric,
    is_correct,
    score,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

TARGET_WORKER = "portfolio_analyst"
PARTIAL_TARGET_CAPABILITIES = [
    "Methods: changed; current outlier-screening method unknown",
    "Methods: portfolio profiling",
]
FULL_TARGET_CAPABILITIES = [
    "Methods: mean-plus-two-SD screening",
    "Methods: portfolio profiling",
]
WORKER_TIERS = {
    TARGET_WORKER: "robust",
    "risk_analyst": "robust",
    "screening_analyst": "screening",
    "audit_coordinator": "coordination",
}
_METHOD_RE = re.compile(r"method\s*[:=]\s*([a-zA-Z0-9_+\- ]+)", re.IGNORECASE)


def _preferences() -> PreferenceWeights:
    rubric = WorkflowRubric(
        name="loan_audit_pack_quality",
        llm_prompt=(
            "Assess the completed loan-audit pack for analytical completeness, "
            "method transparency, reconciliation of robust and rapid screens, "
            "and an actionable capacity estimate. Use only evidence in workflow "
            "artifacts. Return a score from 0 to 10."
        ),
        max_score=10.0,
        run_condition=RunCondition.ON_COMPLETION,
    )
    return PreferenceWeights(
        preferences=[
            Preference(
                name="quality",
                weight=1.0,
                description="Complete and defensible portfolio audit",
                evaluator=Evaluator(
                    name="loan_audit_quality",
                    description="Native LLM evaluation of the audit pack",
                    aggregation=AggregationStrategy.WEIGHTED_AVERAGE,
                    rubrics=[rubric],
                ),
            )
        ]
    )


def build_schedule(
    condition: str,
    swap_timestep: int,
    *,
    lever: str = "toolset",
    weak_model: str = JUDGMENT_WORKER_MODEL,
) -> PerturbationSchedule:
    if condition == "control":
        return PerturbationSchedule()
    if condition not in {"silent", "partial", "full"}:
        raise ValueError(f"Unknown condition: {condition}")
    if lever == "judgment":
        labels = {
            "silent": "internal judgment update",
            "partial": "the analyst's behavior changed",
            "full": (
                "the analyst's model and analytical judgment changed; it now "
                "has limited multi-part integration ability"
            ),
        }
        return PerturbationSchedule(
            perturbations=[
                ModelSwap(
                    timestep=swap_timestep,
                    agent_id=TARGET_WORKER,
                    new_model_name=weak_model,
                    announce=False,
                    label="judgment_change_model",
                ),
                PromptSwap(
                    timestep=swap_timestep,
                    agent_id=TARGET_WORKER,
                    new_system_prompt=DEGRADED_JUDGMENT_PROMPT,
                    announce=condition in {"partial", "full"},
                    label=labels[condition],
                ),
            ]
        )
    if lever != "toolset":
        raise ValueError(f"Unknown lever: {lever}")
    labels = {
        "silent": "internal capability update",
        "partial": "the analyst's capability profile changed",
        "full": "robust percentile analysis changed to mean-plus-two-SD screening",
    }
    visible_capabilities = {
        "silent": None,
        "partial": PARTIAL_TARGET_CAPABILITIES,
        "full": FULL_TARGET_CAPABILITIES,
    }
    return PerturbationSchedule(
        perturbations=[
            ToolSwap(
                timestep=swap_timestep,
                agent_id=TARGET_WORKER,
                new_tool_ids=list(SCREENING_TOOL_IDS),
                new_agent_capabilities=visible_capabilities[condition],
                announce=condition in {"partial", "full"},
                label=labels[condition],
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
    max_timesteps: int,
    swap_timestep: int,
    out_root: Path,
    lever: str = "toolset",
    weak_model: str = JUDGMENT_WORKER_MODEL,
) -> Path:
    prefix = "" if lever == "toolset" else f"{lever}_"
    run_dir = out_root / f"{prefix}{condition}_t{swap_timestep}_seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(
        f"DS-REROUTE lever={lever} condition={condition} seed={seed} "
        f"swap_t={swap_timestep} target={TARGET_WORKER}",
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
        condition, swap_timestep, lever=lever, weak_model=weak_model
    )
    schedule.register(registry)
    observation_policy = ObservationPolicy(
        expose_worker_system_prompts=False,
        worker_metadata="capabilities",
        quality_digest="none",
    )
    manager = ChainOfThoughtManagerAgent(preferences=preferences)
    stakeholder = create_stakeholder_agent(persona="balanced", preferences=preferences)
    recorder = Recorder(scenario.task_answers, scenario.task_meta)
    trace_recorder = RunTraceRecorder(
        metadata={
            "experiment": "ds_reroute",
            "lever": lever,
            "condition": condition,
            "seed": seed,
            "swap_timestep": swap_timestep,
            "target_worker": TARGET_WORKER,
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
        "lever": lever,
        "seed": seed,
        "swap_timestep": swap_timestep,
        "target_worker": TARGET_WORKER,
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(),
        "observation_policy": observation_policy.model_dump(mode="json"),
        "perturbation": schedule.manifest(),
        "final_tools": {
            agent_id: [tool.name for tool in registry.get_agent(agent_id).tools]
            for agent_id in WORKER_TIERS
            if registry.get_agent(agent_id) is not None
        },
        "final_target_model": registry.get_agent(TARGET_WORKER).config.model_name,
        "native_reward_vector": engine.validation_engine.reward_vector,
        "native_reward_final": engine.validation_engine.most_recent_reward,
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
    parser.add_argument("--max-timesteps", type=int, default=16)
    parser.add_argument("--swap-timestep", type=int, default=3)
    parser.add_argument("--lever", choices=["toolset", "judgment"], default="toolset")
    parser.add_argument(
        "--weak-model",
        default=JUDGMENT_WORKER_MODEL,
        help="Replacement model used by the judgment lever.",
    )
    parser.add_argument(
        "--out", type=Path, default=Path("experiments/ds_reroute/outputs")
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
                args.lever,
                args.weak_model,
            )


if __name__ == "__main__":
    asyncio.run(main())
