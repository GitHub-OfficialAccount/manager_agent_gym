"""
M1 de-risking run: does a silent competence swap show up in the quality stream?

Runs the icaap workflow in two conditions:
  - control: no perturbation
  - swap:    documentation_lead's system prompt is silently replaced with a
             degraded one at --swap-timestep

Per run, records:
  - manifest.json          ground truth: condition, seed, observation policy,
                           perturbation schedule
  - probe_reports.json     out-of-band detection probe judgments per timestep
  - task_completions.json  (timestep, task, worker) for every completion
  - artifacts.json         every output resource with worker + timestep
                           attribution — input to score_artifacts.py

Usage:
  uv run python -m experiments.m1_derisk.run --conditions control swap \
      --seeds 42 --max-timesteps 20 --swap-timestep 8
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from examples.common_stakeholders import create_stakeholder_agent
from examples.scenarios import SCENARIOS
from manager_agent_gym import (
    AgentRegistry,
    ChainOfThoughtManagerAgent,
    WorkflowExecutionEngine,
)
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.common.model_provider import (
    disable_agents_tracing_if_proxied,
)
from manager_agent_gym.core.evaluation.detection_probe import DetectionProbe
from manager_agent_gym.schemas.execution.callbacks import TimestepEndContext
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.execution.perturbations import (
    PerturbationSchedule,
    PromptSwap,
)
from manager_agent_gym.schemas.workflow_agents import AgentConfig

from .prompts import DEGRADED_DOCUMENTATION_LEAD_PROMPT

WORKFLOW_NAME = "icaap"
TARGET_AGENT = "documentation_lead"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


class CompletionRecorder:
    """Timestep-end callback capturing (timestep, task, worker) attributions.

    Records BOTH start and completion timesteps: the agent instance (and thus
    pre/post-swap policy) is resolved when a task STARTS, so perturbation
    analysis must attribute artifacts by start timestep — work in flight at
    the swap was produced by the old policy even if it completes later.
    """

    def __init__(self) -> None:
        self.completions: list[dict] = []
        self._start_timesteps: dict[str, int] = {}

    async def callback(self, ctx: TimestepEndContext) -> None:
        for task_id in ctx.tasks_started:
            self._start_timesteps.setdefault(str(task_id), ctx.timestep)
        for task_id in ctx.tasks_completed:
            task = ctx.workflow.tasks.get(task_id)
            if task is None:
                continue
            self.completions.append(
                {
                    "timestep": ctx.timestep,
                    "started_timestep": self._start_timesteps.get(str(task_id)),
                    "task_id": str(task_id),
                    "task_name": task.name,
                    "agent_id": task.assigned_agent_id,
                    "output_resource_ids": [
                        str(r) for r in task.output_resource_ids
                    ],
                }
            )


def build_schedule(condition: str, swap_timestep: int) -> PerturbationSchedule:
    if condition == "control":
        return PerturbationSchedule()
    return PerturbationSchedule(
        perturbations=[
            PromptSwap(
                timestep=swap_timestep,
                agent_id=TARGET_AGENT,
                new_system_prompt=DEGRADED_DOCUMENTATION_LEAD_PROMPT,
                announce=False,
                label="competence_degradation",
            )
        ]
    )


async def run_one(
    condition: str, seed: int, max_timesteps: int, swap_timestep: int, out_root: Path
) -> Path:
    run_dir = out_root / f"{condition}_t{swap_timestep}_seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    spec = SCENARIOS[WORKFLOW_NAME]
    workflow = spec.create_workflow()
    preferences = spec.create_preferences()

    agent_registry = AgentRegistry()
    for t, changes in spec.create_team_timeline().items():
        for action, payload, reason in changes:
            if action == "add":
                agent_registry.schedule_agent_add(t, payload, reason)
            elif action == "remove":
                agent_id = (
                    payload.agent_id if isinstance(payload, AgentConfig) else payload
                )
                agent_registry.schedule_agent_remove(t, agent_id, reason)

    schedule = build_schedule(condition, swap_timestep)
    schedule.register(agent_registry)

    observation_policy = ObservationPolicy()  # redacted baseline contract
    manager = ChainOfThoughtManagerAgent(preferences=preferences)
    # NOTE: preference weight-update dynamics deliberately NOT applied — this
    # de-risking run isolates the worker perturbation from other
    # non-stationarities (those return in the M3 attribution experiment).
    stakeholder = create_stakeholder_agent(persona="balanced", preferences=preferences)

    probe = DetectionProbe(seed=seed)
    recorder = CompletionRecorder()

    engine = WorkflowExecutionEngine(
        workflow=workflow,
        agent_registry=agent_registry,
        stakeholder_agent=stakeholder,
        manager_agent=manager,
        communication_service=CommunicationService(),
        max_timesteps=max_timesteps,
        enable_timestep_logging=True,
        enable_final_metrics_logging=False,
        timestep_end_callbacks=[probe.callback, recorder.callback],
        observation_policy=observation_policy,
        seed=seed,
    )

    started_at = datetime.now().isoformat()
    await engine.run_full_execution(save_outputs=False)

    manifest = {
        "workflow": WORKFLOW_NAME,
        "condition": condition,
        "seed": seed,
        "max_timesteps": max_timesteps,
        # For control runs the swap timestep is ignored by the episode but kept
        # as the analysis boundary, so control artifacts get the same matched
        # pre/post split as the paired swap run.
        "reference_boundary": swap_timestep,
        "target_agent": TARGET_AGENT,
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(),
        "observation_policy": observation_policy.model_dump(),
        "perturbation_schedule": schedule.manifest(),
        "manager_model": manager.model_name,
        # self-check: proves whether the swap was live in the workflow mirror
        "target_agent_final_prompt_prefix": (
            workflow.agents[TARGET_AGENT].config.system_prompt[:80]
            if TARGET_AGENT in workflow.agents
            else None
        ),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (run_dir / "probe_reports.json").write_text(json.dumps(probe.reports, indent=2))
    (run_dir / "task_completions.json").write_text(
        json.dumps(recorder.completions, indent=2)
    )

    resource_index = {str(r_id): res for r_id, res in workflow.resources.items()}
    artifacts = []
    for completion in recorder.completions:
        for r_id in completion["output_resource_ids"]:
            res = resource_index.get(r_id)
            if res is None:
                continue
            artifacts.append(
                {
                    "resource_id": r_id,
                    "task_id": completion["task_id"],
                    "task_name": completion["task_name"],
                    "agent_id": completion["agent_id"],
                    "timestep": completion["timestep"],
                    "started_timestep": completion["started_timestep"],
                    "name": res.name,
                    "description": res.description,
                    "content": res.content,
                }
            )
    (run_dir / "artifacts.json").write_text(json.dumps(artifacts, indent=2))

    print(f"✅ {condition} seed={seed}: {len(artifacts)} artifacts -> {run_dir}")
    return run_dir


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditions", nargs="+", default=["control", "swap"],
        choices=["control", "swap"],
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=[42])
    parser.add_argument("--max-timesteps", type=int, default=20)
    parser.add_argument("--swap-timestep", type=int, default=8)
    parser.add_argument(
        "--out", type=Path, default=Path("experiments/m1_derisk/outputs")
    )
    args = parser.parse_args()

    for seed in args.seeds:
        for condition in args.conditions:
            await run_one(
                condition=condition,
                seed=seed,
                max_timesteps=args.max_timesteps,
                swap_timestep=args.swap_timestep,
                out_root=args.out,
            )


if __name__ == "__main__":
    asyncio.run(main())
