"""Live manipulation gate for robust and screening audit toolsets.

This probe uses the final experimental-style prompt and held-out batch tasks.
It does not force tool calls.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from statistics import mean

from manager_agent_gym.core.common.model_provider import disable_agents_tracing_if_proxied
from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core.tasks import Task

from .scenario import BATCH_IDS, build_scenario, build_worker, extract_metric, score

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")


async def run_tier(tier: str, repetitions: int) -> list[float]:
    scenario = build_scenario(42)
    agent_id = "portfolio_analyst" if tier == "robust" else "screening_analyst"
    config, tools = build_worker(scenario, agent_id, tier)
    agent = AIAgent(config, tools)
    scores = []
    for batch_id in BATCH_IDS:
        spec = scenario.task_specs[f"audit_{batch_id.lower()}_robust"]
        for _ in range(repetitions):
            result = await agent.execute_task(
                Task(name=spec.name, description=spec.description), []
            )
            content = (
                result.output_resources[0].content
                if result.success and result.output_resources
                else ""
            )
            answer = extract_metric(content or "")
            task_score = score(answer, spec.truth)
            scores.append(task_score)
            print(
                f"{tier:<10} batch={batch_id} truth={spec.truth:.0f} "
                f"answer={answer} score={task_score:.3f}",
                flush=True,
            )
    return scores


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=1)
    args = parser.parse_args()
    for tier in ("robust", "screening"):
        scores = await run_tier(tier, args.n)
        print(f"{tier} mean score={mean(scores):.3f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
