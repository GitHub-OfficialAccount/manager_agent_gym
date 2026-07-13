"""Check natural tool selection for the outlier competence tiers.

Unlike the plumbing smoke test, this probe does not require a tool call. The
worker sees its available tool and decides whether using it is useful.

Run with:
    uv run python -m experiments.ds_reroute.natural_choice_probe
"""

import argparse
import asyncio
import os

import numpy as np
from agents import function_tool

from manager_agent_gym.core.common.model_provider import (
    disable_agents_tracing_if_proxied,
)
from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core import Task
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

from .scenario import WORKER_MODEL, _DATA, extract_answer

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")

COLUMNS = ("income", "amount", "dti", "rate")
TRUTH = {column: 100 for column in COLUMNS}
TOOL_CALLS = {"percentile": 0, "zscore": 0}


@function_tool
def flag_outliers_percentile(column: str) -> str:
    """Count high-end outliers using the portfolio's robust percentile method.

    column: one of income, amount, dti, rate.
    """
    TOOL_CALLS["percentile"] += 1
    values = _DATA[column]
    cutoff = np.percentile(values, 95)
    return str(int((values > cutoff).sum()))


@function_tool
def flag_outliers_zscore(column: str) -> str:
    """Count high-end outliers using a fast mean-plus-two-SD heuristic.

    column: one of income, amount, dti, rate.
    """
    TOOL_CALLS["zscore"] += 1
    values = _DATA[column]
    cutoff = values.mean() + 2 * values.std()
    return str(int((values > cutoff).sum()))


SYSTEM_PROMPT = (
    "You are a portfolio data analyst. Complete each assigned task accurately "
    "using your professional judgment. You may use your available tools when "
    "they are useful. Return exactly one output resource whose content is your "
    "final answer as a single bare integer."
)


def build_agent(tier: str) -> AIAgent:
    tool = flag_outliers_percentile if tier == "percentile" else flag_outliers_zscore
    config = AIAgentConfig(
        agent_id=f"{tier}_analyst",
        agent_type="ai",
        system_prompt=SYSTEM_PROMPT,
        model_name=WORKER_MODEL,
        agent_description="Portfolio data analyst",
        agent_capabilities=["outlier analysis"],
    )
    return AIAgent(config, [tool])


async def run_tier(tier: str, columns: list[str], repetitions: int) -> list[dict]:
    agent = build_agent(tier)
    rows = []
    for column in columns:
        for repetition in range(repetitions):
            before = TOOL_CALLS[tier]
            task = Task(
                name=f"{column.title()} outlier count",
                description=(
                    f"Estimate how many high-end outliers are present in the "
                    f"portfolio's {column} column. Report one integer."
                ),
            )
            result = await agent.execute_task(task, [])
            content = (
                result.output_resources[0].content
                if result.success and result.output_resources
                else ""
            )
            answer = extract_answer(content or "")
            called = TOOL_CALLS[tier] > before
            truth = TRUTH[column]
            score = (
                max(0.0, 1.0 - abs(answer - truth) / truth)
                if answer is not None
                else 0.0
            )
            row = {
                "tier": tier,
                "column": column,
                "repetition": repetition,
                "success": result.success,
                "tool_called": called,
                "answer": answer,
                "truth": truth,
                "score": score,
            }
            rows.append(row)
            print(row, flush=True)
    return rows


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=1, help="Repetitions per cell")
    parser.add_argument(
        "--tiers",
        nargs="+",
        choices=("percentile", "zscore"),
        default=("percentile", "zscore"),
    )
    parser.add_argument("--columns", nargs="+", choices=COLUMNS, default=COLUMNS)
    args = parser.parse_args()

    rows = []
    for tier in args.tiers:
        rows.extend(await run_tier(tier, args.columns, args.n))

    called = sum(row["tool_called"] for row in rows)
    succeeded = sum(row["success"] for row in rows)
    print(
        f"SUMMARY success={succeeded}/{len(rows)} "
        f"tool_calls={called}/{len(rows)}",
        flush=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
