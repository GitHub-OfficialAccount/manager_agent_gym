"""Linchpin gate: does holding the calc tool create a checkable correctness gap?

Same worker/model/prompt, with vs without the calc tool, on the quant tasks.
Correctness is exact-match (no LLM judge). GO if calc-holder >> non-holder,
especially on the hard (compounding) tasks, and both complete reliably.

  uv run python -m experiments.calc_reroute.linchpin --n 2
"""

import argparse
import asyncio
import os

from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core.tasks import Task

from .scenario import QUANT_TASKS, build_worker, extract_answer, is_correct

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")


async def run_condition(has_calc: bool, n: int) -> None:
    cfg, tools = build_worker("quant_analyst", has_calc=has_calc)
    agent = AIAgent(config=cfg, tools=tools)
    label = "WITH-calc" if has_calc else "NO-calc  "
    by_diff: dict[str, list[bool]] = {}
    for name, desc, truth, diff in QUANT_TASKS:
        task = Task(name=name, description=desc)
        for _ in range(n):
            try:
                res = await agent.execute_task(task, [])
                content = res.output_resources[0].content if (
                    res.success and res.output_resources) else ""
            except Exception:
                content = ""
            ans = extract_answer(content)
            ok = is_correct(ans, truth)
            by_diff.setdefault(diff, []).append(ok)
            print(f"  {label} {name:<16} [{diff:<4}] truth={truth:<10.4f} "
                  f"got={ans} {'✓' if ok else '✗'}", flush=True)
    tot = [ok for v in by_diff.values() for ok in v]
    print(f"  => {label}: correct {sum(tot)}/{len(tot)} | "
          + " ".join(f"{d}={sum(v)}/{len(v)}" for d, v in sorted(by_diff.items())))


async def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n", type=int, default=2, help="attempts per task per condition")
    args = p.parse_args()
    print("=== WITH calc tool ===")
    await run_condition(True, args.n)
    print("=== WITHOUT calc tool ===")
    await run_condition(False, args.n)
    print("\nGO if WITH >> WITHOUT, especially on hard tasks.")


if __name__ == "__main__":
    asyncio.run(main())
