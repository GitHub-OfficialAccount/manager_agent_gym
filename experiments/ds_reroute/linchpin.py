"""Linchpin gate: does tiered tooling create a GRADED (not binary) competence gap?

Same worker/model/prompt, ADVANCED (full analytics tool) vs BASIC (simple
aggregates only), over the shared 2,000-row dataset. The worker is told to
ESTIMATE rather than refuse when it lacks the exact tool, and we score by
graded relative error (deterministic, no LLM judge). GO if the gap is graded:
advanced ~1 everywhere; basic ~1 on basics, mid on median/std (estimable),
low on corr (not estimable from marginals).

  uv run python -m experiments.ds_reroute.linchpin --n 2
"""

import argparse
import asyncio
import os
from collections import defaultdict

from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core.tasks import Task

from .scenario import TASKS, build_worker, extract_answer, rel_error, score

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")


async def run_condition(tier: str, n: int) -> dict[str, list[float]]:
    cfg, tools = build_worker("senior_analyst", tier=tier)
    agent = AIAgent(config=cfg, tools=tools)
    by_op: dict[str, list[float]] = defaultdict(list)
    for name, q, op, _c, _c2, truth in TASKS:
        task = Task(name=name, description=q)
        for _ in range(n):
            try:
                res = await agent.execute_task(task, [])
                content = res.output_resources[0].content if (
                    res.success and res.output_resources) else ""
            except Exception:
                content = ""
            ans = extract_answer(content)
            s = score(ans, truth, op)
            by_op[op].append(s)
            re = rel_error(ans, truth)
            re_str = "  n/a" if re is None else f"{re:5.1%}"
            print(f"  {tier:<8} {name:<20} truth={truth:<11.4f} got={ans} "
                  f"relerr={re_str} score={s:.2f}", flush=True)
    return by_op


def summarize(tier: str, by_op: dict[str, list[float]]) -> None:
    print(f"\n  -- {tier} per-operation mean score --")
    allv = []
    for op in ("mean", "std", "median", "q90", "corr"):
        vs = by_op.get(op, [])
        if vs:
            allv += vs
            print(f"     {op:<7} {sum(vs) / len(vs):.2f}  (n={len(vs)})")
    if allv:
        print(f"     {'ALL':<7} {sum(allv) / len(allv):.2f}")


async def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, default=2)
    args = p.parse_args()
    print("=== ADVANCED tier (full analytics) ===")
    adv = await run_condition("advanced", args.n)
    print("=== BASIC tier (aggregates only, estimates the rest) ===")
    bas = await run_condition("basic", args.n)
    summarize("advanced", adv)
    summarize("basic", bas)
    print("\nGO if graded: basic ~1 on mean, mid on std/median/q90, low on corr;"
          " advanced ~1 across the board.")


if __name__ == "__main__":
    asyncio.run(main())
