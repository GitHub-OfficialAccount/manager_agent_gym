"""Check voluntary tool selection on the held-out audit tasks.

The worker is never instructed to call a tool. Run a small gate with:

    uv run python -m experiments.ds_reroute.natural_choice_probe --n 1
"""

from __future__ import annotations

import argparse
import asyncio
import os

from manager_agent_gym.core.common.model_provider import disable_agents_tracing_if_proxied
from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core.tasks import Task

from .scenario import BATCH_IDS, build_scenario, build_worker, extract_metric, score

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")


async def run_tier(tier: str, batches: list[str], repetitions: int) -> list[dict]:
    scenario = build_scenario(42)
    agent_id = "portfolio_analyst" if tier == "robust" else "screening_analyst"
    config, tools = build_worker(scenario, agent_id, tier)
    agent = AIAgent(config, tools)
    rows = []
    for batch_id in batches:
        spec = scenario.task_specs[f"audit_{batch_id.lower()}_robust"]
        for repetition in range(repetitions):
            before = len(scenario.tool_calls)
            result = await agent.execute_task(
                Task(name=spec.name, description=spec.description), []
            )
            content = (
                result.output_resources[0].content
                if result.success and result.output_resources
                else ""
            )
            calls = scenario.tool_calls[before:]
            answer = extract_metric(content or "")
            row = {
                "tier": tier,
                "batch": batch_id,
                "repetition": repetition,
                "success": result.success,
                "tool_calls": [call["tool"] for call in calls],
                "answer": answer,
                "truth": spec.truth,
                "score": score(answer, spec.truth),
            }
            rows.append(row)
            print(row, flush=True)
    return rows


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument(
        "--tiers", nargs="+", choices=("robust", "screening"),
        default=("robust", "screening"),
    )
    parser.add_argument("--batches", nargs="+", choices=BATCH_IDS, default=BATCH_IDS)
    args = parser.parse_args()

    rows = []
    for tier in args.tiers:
        rows.extend(await run_tier(tier, args.batches, args.n))
    succeeded = sum(row["success"] for row in rows)
    voluntarily_called = sum(bool(row["tool_calls"]) for row in rows)
    print(
        f"SUMMARY success={succeeded}/{len(rows)} "
        f"voluntary_tool_use={voluntarily_called}/{len(rows)}",
        flush=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
