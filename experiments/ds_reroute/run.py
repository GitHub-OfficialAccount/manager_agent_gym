"""ds_reroute experiment runner.

3 workers: senior_analyst starts with the ADVANCED analytics tool; credit_analyst
and junior_analyst have only BASIC. The perturbation moves the advanced tool
senior->junior (a downgrade of senior + upgrade of junior). Advanced-tasks
should then re-route to junior. Conditions: control / silent / oracle.

  uv run python -m experiments.ds_reroute.run \
      --conditions control silent oracle --seeds 42 --max-timesteps 16 --swap-timestep 3
  uv run python -m experiments.ds_reroute.score
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
from manager_agent_gym.core.common.model_provider import disable_agents_tracing_if_proxied
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.schemas.execution.callbacks import TimestepEndContext
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.execution.perturbations import (
    PerturbationSchedule,
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

from .scenario import (
    TASK_ANSWERS,
    TASK_META,
    advanced_stats,
    basic_stats,
    build_worker,
    build_workflow,
    extract_answer,
    is_correct,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

ADVANCED_HOLDER = "senior_analyst"
NEW_HOLDER = "junior_analyst"


def _prefs() -> PreferenceWeights:
    return PreferenceWeights(preferences=[Preference(
        name="quality", weight=1.0, description="Correct analysis",
        evaluator=Evaluator(name="q", description="p",
                            aggregation=AggregationStrategy.WEIGHTED_AVERAGE, rubrics=[]))])


def build_schedule(condition: str, swap_t: int) -> PerturbationSchedule:
    if condition == "control":
        return PerturbationSchedule()
    announce = condition == "oracle"
    return PerturbationSchedule(perturbations=[
        ToolSwap(timestep=swap_t, agent_id=ADVANCED_HOLDER, new_tool_ids=["basic"],
                 announce=announce,
                 label=(f"{ADVANCED_HOLDER} lost advanced analytics" if announce
                        else "internal update")),
        ToolSwap(timestep=swap_t, agent_id=NEW_HOLDER, new_tool_ids=["advanced"],
                 announce=announce,
                 label=(f"{NEW_HOLDER} now holds advanced analytics" if announce
                        else "internal update")),
    ])


class Recorder:
    def __init__(self) -> None:
        self.completions: list[dict] = []
        self.actions: list[dict] = []
        self._start: dict[str, int] = {}

    async def callback(self, ctx: TimestepEndContext) -> None:
        a = ctx.manager_action
        self.actions.append({
            "timestep": ctx.timestep,
            "action_type": getattr(a, "action_type", None) if a else None,
            "task_id": str(getattr(a, "task_id", "")) or None,
            "agent_id": getattr(a, "agent_id", None),
        })
        for tid in ctx.tasks_started:
            self._start.setdefault(str(tid), ctx.timestep)
        for tid in ctx.tasks_completed:
            task = ctx.workflow.tasks.get(tid)
            if task is None:
                continue
            content = ""
            for rid in task.output_resource_ids:
                res = ctx.workflow.resources.get(rid)
                if res is not None:
                    content = res.content or ""
                    break
            meta = TASK_META.get(task.name, {})
            truth = TASK_ANSWERS.get(task.name)
            ans = extract_answer(content)
            self.completions.append({
                "timestep": ctx.timestep,
                "started_timestep": self._start.get(str(tid)),
                "task_name": task.name,
                "task_op": meta.get("op"),
                "needs_advanced": meta.get("op") in {"std", "median", "q90", "corr"},
                "agent_id": task.assigned_agent_id,
                "answer": ans,
                "correct": bool(truth is not None and is_correct(ans, truth)),
            })


async def run_one(condition, seed, max_timesteps, swap_timestep, out_root) -> Path:
    run_dir = out_root / f"{condition}_t{swap_timestep}_seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print(f"🧪 DS-REROUTE | condition={condition} seed={seed} swap_t={swap_timestep} "
          f"| advanced moves {ADVANCED_HOLDER}->{NEW_HOLDER}")
    print("=" * 60)

    workflow = build_workflow()
    prefs = _prefs()
    registry = AgentRegistry()
    registry.register_tool("advanced", advanced_stats)
    registry.register_tool("basic", basic_stats)
    for aid, tier in [(ADVANCED_HOLDER, "advanced"), ("credit_analyst", "basic"),
                      (NEW_HOLDER, "basic")]:
        cfg, tools = build_worker(aid, tier)
        registry.register_ai_agent(cfg, tools)

    schedule = build_schedule(condition, swap_timestep)
    schedule.register(registry)

    manager = ChainOfThoughtManagerAgent(preferences=prefs)
    stakeholder = create_stakeholder_agent(persona="balanced", preferences=prefs)
    recorder = Recorder()
    engine = WorkflowExecutionEngine(
        workflow=workflow, agent_registry=registry, stakeholder_agent=stakeholder,
        manager_agent=manager, communication_service=CommunicationService(),
        max_timesteps=max_timesteps, enable_timestep_logging=True,
        enable_final_metrics_logging=False,
        timestep_end_callbacks=[*default_timestep_callbacks(), recorder.callback],
        observation_policy=ObservationPolicy(), seed=seed,
    )
    started = datetime.now().isoformat()
    await engine.run_full_execution(save_outputs=False)

    manifest = {
        "condition": condition, "seed": seed, "swap_timestep": swap_timestep,
        "advanced_holder_initial": ADVANCED_HOLDER, "new_holder": NEW_HOLDER,
        "started_at": started, "finished_at": datetime.now().isoformat(),
        "perturbation": schedule.manifest(),
        "final_tools": {aid: [t.name for t in registry.get_agent(aid).tools]
                        for aid in [ADVANCED_HOLDER, "credit_analyst", NEW_HOLDER]
                        if registry.get_agent(aid)},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (run_dir / "completions.json").write_text(json.dumps(recorder.completions, indent=2))
    (run_dir / "manager_actions.json").write_text(json.dumps(recorder.actions, indent=2))
    print(f"✅ {condition}: {len(recorder.completions)} completions -> {run_dir}")
    return run_dir


async def main() -> None:
    disable_agents_tracing_if_proxied()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--conditions", nargs="+", default=["control", "silent", "oracle"],
                   choices=["control", "silent", "oracle"])
    p.add_argument("--seeds", nargs="+", type=int, default=[42])
    p.add_argument("--max-timesteps", type=int, default=16)
    p.add_argument("--swap-timestep", type=int, default=3)
    p.add_argument("--out", type=Path, default=Path("experiments/ds_reroute/outputs"))
    args = p.parse_args()
    for seed in args.seeds:
        for c in args.conditions:
            await run_one(c, seed, args.max_timesteps, args.swap_timestep, args.out)


if __name__ == "__main__":
    asyncio.run(main())
