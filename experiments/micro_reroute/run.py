"""
Step-2 reroute micro-experiment runner.

Runs the reroute_micro scenario under control / silent / oracle and records, for
every completed task: which worker did it, the task type, when it started (the
agent's policy binds at task start), and its output — so we can measure whether
capital-task quality/grounding is preserved after the capital pack moves.

  uv run python -m experiments.micro_reroute.run \
      --conditions control silent oracle --seeds 42 --max-timesteps 16 --swap-timestep 3
  uv run python -m experiments.micro_reroute.score
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

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
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.evaluation.detection_probe import DetectionProbe
from manager_agent_gym.schemas.execution.callbacks import TimestepEndContext
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.preferences.preference import (
    Preference,
    PreferenceWeights,
)
from manager_agent_gym.schemas.preferences.evaluator import (
    AggregationStrategy,
    Evaluator,
)

from .scenario import (
    REROUTE_FROM,
    REROUTE_TO,
    TASK_TYPE_BY_NAME,
    build_reroute_schedule,
    build_team,
    build_workflow,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


def basic_preferences() -> PreferenceWeights:
    return PreferenceWeights(
        preferences=[
            Preference(
                name="quality", weight=1.0, description="High-quality deliverables",
                evaluator=Evaluator(
                    name="q", description="placeholder",
                    aggregation=AggregationStrategy.WEIGHTED_AVERAGE, rubrics=[],
                ),
            )
        ]
    )


class Recorder:
    """Records completions with worker, task type, and start timestep."""

    def __init__(self) -> None:
        self.completions: list[dict] = []
        self._start: dict[str, int] = {}

    async def callback(self, ctx: TimestepEndContext) -> None:
        for tid in ctx.tasks_started:
            self._start.setdefault(str(tid), ctx.timestep)
        for tid in ctx.tasks_completed:
            task = ctx.workflow.tasks.get(tid)
            if task is None:
                continue
            self.completions.append({
                "timestep": ctx.timestep,
                "started_timestep": self._start.get(str(tid)),
                "task_name": task.name,
                "task_type": TASK_TYPE_BY_NAME.get(task.name, "?"),
                "agent_id": task.assigned_agent_id,
                "output_resource_ids": [str(r) for r in task.output_resource_ids],
            })


async def run_one(
    condition: str, seed: int, max_timesteps: int, swap_timestep: int, out_root: Path
) -> Path:
    run_dir = out_root / f"{condition}_t{swap_timestep}_seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print(f"🧪 REROUTE MICRO | condition={condition} seed={seed} "
          f"swap_t={swap_timestep} reroute: capital pack {REROUTE_FROM}->{REROUTE_TO}")
    print("=" * 60)

    workflow = build_workflow()
    team = build_team()
    prefs = basic_preferences()

    registry = AgentRegistry()
    for cfg in team.values():
        registry.schedule_agent_add(0, cfg, "initial team")
    schedule = build_reroute_schedule(condition, swap_timestep)
    schedule.register(registry)

    manager = ChainOfThoughtManagerAgent(preferences=prefs)
    stakeholder = create_stakeholder_agent(persona="balanced", preferences=prefs)
    probe = DetectionProbe(seed=seed)
    recorder = Recorder()

    engine = WorkflowExecutionEngine(
        workflow=workflow, agent_registry=registry, stakeholder_agent=stakeholder,
        manager_agent=manager, communication_service=CommunicationService(),
        max_timesteps=max_timesteps, enable_timestep_logging=True,
        enable_final_metrics_logging=False,
        timestep_end_callbacks=[*default_timestep_callbacks(), probe.callback,
                                recorder.callback],
        observation_policy=ObservationPolicy(), seed=seed,
    )
    started = datetime.now().isoformat()
    await engine.run_full_execution(save_outputs=False)

    resources = {str(r): res for r, res in workflow.resources.items()}
    artifacts = []
    for c in recorder.completions:
        for rid in c["output_resource_ids"]:
            res = resources.get(rid)
            if res is None:
                continue
            artifacts.append({**c, "resource_id": rid, "name": res.name,
                              "content": res.content})

    manifest = {
        "condition": condition, "seed": seed, "max_timesteps": max_timesteps,
        "swap_timestep": swap_timestep, "reroute_from": REROUTE_FROM,
        "reroute_to": REROUTE_TO, "started_at": started,
        "finished_at": datetime.now().isoformat(),
        "final_prompts": {
            aid: workflow.agents[aid].config.system_prompt[:60]
            for aid in team if aid in workflow.agents
        },
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (run_dir / "completions.json").write_text(json.dumps(recorder.completions, indent=2))
    (run_dir / "artifacts.json").write_text(json.dumps(artifacts, indent=2))
    (run_dir / "probe_reports.json").write_text(json.dumps(probe.reports, indent=2))
    print(f"✅ {condition}: {len(recorder.completions)} completions, "
          f"{len(artifacts)} artifacts -> {run_dir}")
    return run_dir


async def main() -> None:
    disable_agents_tracing_if_proxied()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--conditions", nargs="+", default=["control", "silent", "oracle"],
                   choices=["control", "silent", "oracle"])
    p.add_argument("--seeds", nargs="+", type=int, default=[42])
    p.add_argument("--max-timesteps", type=int, default=16)
    p.add_argument("--swap-timestep", type=int, default=3)
    p.add_argument("--out", type=Path, default=Path("experiments/micro_reroute/outputs"))
    args = p.parse_args()
    for seed in args.seeds:
        for condition in args.conditions:
            await run_one(condition, seed, args.max_timesteps, args.swap_timestep,
                          args.out)


if __name__ == "__main__":
    asyncio.run(main())
