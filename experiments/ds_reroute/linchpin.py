"""Linchpin gate: does the data-query tool create a robust correctness gap?

Same worker/model/prompt, with vs without `query_data`, on statistics over a
hidden 2,000-row dataset. Correctness is exact-match numeric (no LLM judge).
GO if WITH >> WITHOUT (expected: without has no data access → fabricates).

  uv run python -m experiments.ds_reroute.linchpin --n 2
"""

import argparse
import asyncio
import os

from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core.tasks import Task

from .scenario import TASKS, build_worker, extract_answer, is_correct

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")


async def run_condition(tier: str, n: int) -> None:
    cfg, tools = build_worker("senior_analyst", tier=tier)
    agent = AIAgent(config=cfg, tools=tools)
    label = f"{tier:<8}"
    results = []
    for name, q, _op, _c, _c2, truth in TASKS:
        task = Task(name=name, description=q)
        for _ in range(n):
            try:
                res = await agent.execute_task(task, [])
                content = res.output_resources[0].content if (
                    res.success and res.output_resources) else ""
            except Exception:
                content = ""
            ans = extract_answer(content)
            ok = is_correct(ans, truth)
            results.append(ok)
            print(f"  {label} {name:<20} truth={truth:<12.4f} got={ans} "
                  f"{'✓' if ok else '✗'}", flush=True)
    print(f"  => {label}: correct {sum(results)}/{len(results)}")


async def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, default=2)
    args = p.parse_args()
    print("=== ADVANCED tier (full analytics) ===")
    await run_condition("advanced", args.n)
    print("=== BASIC tier (data access only) ===")
    await run_condition("basic", args.n)
    print("\nGO if advanced ~full and basic ~partial (graded, not 0).")


if __name__ == "__main__":
    asyncio.run(main())
