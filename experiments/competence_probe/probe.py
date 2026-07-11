"""
Linchpin check: can information access create a genuine, measurable competence gap?

This is the go/no-go gate for the whole capability-profile experiment. It tests
two claims, in the most controlled setting possible (a direct worker call, no
workflow):

1. A worker GIVEN a data resource produces more GROUNDED output than the same
   worker (same model, same prompt) WITHOUT it — because the info-poor worker
   must confabulate the specifics.
2. A groundedness-aware judge (given the source) detects that gap, while a
   plain quality judge does NOT (both outputs are fluent) — confirming
   groundedness is the right instrument and quality alone is blind to it.

Success = info-rich >> info-poor on groundedness, ~tie on quality, both
conditions complete reliably. Failure (gap absent, or confabulation so good
groundedness can't tell) → pivot the competence axis before building Step 2.

Run:
  uv run python -m experiments.competence_probe.probe --n 3
"""

import argparse
import asyncio
import json
import statistics
from pathlib import Path

from pydantic import BaseModel, Field

from manager_agent_gym.core.common.llm_interface import generate_structured_response
from manager_agent_gym.core.workflow_agents.ai_agent import AIAgent
from manager_agent_gym.schemas.core.resources import Resource
from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

# Reliable worker (deepseek fails structured output too often in isolation to
# test the gap cleanly); the info-access effect is model-general.
WORKER_MODEL = "openrouter/openai/gpt-oss-20b"
# Reliable judge, different from the worker to avoid self-judging.
JUDGE_MODEL = "openrouter/openai/gpt-4o-mini"

# --- The controlled stimulus: a source with specific, checkable facts ---
SOURCE = Resource(
    name="Bank Capital Data Pack — Q4 2025",
    description="Ground-truth capital, leverage, and liquidity figures.",
    content=(
        "CAPITAL & LIQUIDITY DATA PACK — Meridian Bank plc — Q4 2025\n"
        "- CET1 ratio: 13.7% (regulatory minimum incl. buffers: 10.4%)\n"
        "- Tier 1 capital ratio: 15.1%\n"
        "- Total capital ratio: 18.6%\n"
        "- Tier 1 leverage ratio: 5.2%\n"
        "- Total risk-weighted assets (RWA): EUR 48.3bn\n"
        "  - Credit risk RWA: EUR 39.1bn; Market risk RWA: EUR 3.4bn; "
        "Operational risk RWA: EUR 5.8bn\n"
        "- Liquidity Coverage Ratio (LCR): 142%\n"
        "- Net Stable Funding Ratio (NSFR): 118%\n"
        "- CET1 capital: EUR 6.62bn; Total capital: EUR 8.98bn\n"
        "- Largest single-name concentration: 8.3% of Tier 1 capital\n"
        "- Management buffer above CET1 minimum: 330 bps\n"
    ),
    content_type="text/plain",
)

TASK = Task(
    name="Capital Adequacy Summary",
    description=(
        "Write a concise capital adequacy summary for the ICAAP covering the "
        "bank's CET1, Tier 1 leverage, and liquidity (LCR/NSFR) position, "
        "citing the specific ratios and RWA figures."
    ),
)

WORKER_CONFIG = AIAgentConfig(
    agent_id="analyst",
    agent_type="ai",
    system_prompt=(
        "You are a banking capital analyst. Write precise capital adequacy "
        "documentation. Base every figure STRICTLY on the materials provided "
        "to you in the task; never use figures from memory or general "
        "knowledge. If a required figure is not in the provided materials, "
        "write '[not available]' rather than estimating it."
    ),
    model_name=WORKER_MODEL,
    agent_description="Capital adequacy analyst",
    agent_capabilities=["capital analysis", "regulatory documentation"],
)


class QualityScore(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    reasoning: str = Field(default="")


class GroundednessScore(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    unsupported_claims: list[str] = Field(
        default_factory=list,
        description="Specific figures/claims in the artifact NOT supported by the source",
    )
    reasoning: str = Field(default="")


QUALITY_PROMPT = (
    "You are a strict quality reviewer. Score the artifact 0-10 on overall "
    "quality for its task: completeness, specificity, structure, and internal "
    "consistency. Confident tone does not count as quality."
)

GROUNDEDNESS_PROMPT = (
    "You are a fact-checking auditor. You are given a SOURCE of ground-truth "
    "figures and an ARTIFACT. Score 0-10 how well the artifact's specific "
    "factual claims (ratios, amounts, statistics) are grounded in the SOURCE:\n"
    "- 10: every specific figure appears in and matches the source; nothing fabricated.\n"
    "- 5: some figures match, others are absent from or inconsistent with the source.\n"
    "- 0: the specific figures are fabricated or contradict the source.\n"
    "A fluent artifact full of confident but UNSUPPORTED numbers must score LOW. "
    "List the unsupported/contradicting figures."
)


async def score_quality(content: str, seed: int) -> QualityScore | None:
    try:
        return await generate_structured_response(
            system_prompt=QUALITY_PROMPT,
            user_prompt=f"TASK: {TASK.name}\n\nARTIFACT:\n{content}",
            response_type=QualityScore, seed=seed, model=JUDGE_MODEL,
            temperature=0, max_retries=2,
        )
    except Exception:
        return None


async def score_groundedness(content: str, seed: int) -> GroundednessScore | None:
    try:
        return await generate_structured_response(
            system_prompt=GROUNDEDNESS_PROMPT,
            user_prompt=(
                f"SOURCE:\n{SOURCE.content}\n\nARTIFACT:\n{content}"
            ),
            response_type=GroundednessScore, seed=seed, model=JUDGE_MODEL,
            temperature=0, max_retries=2,
        )
    except Exception:
        return None


async def run_condition(info_rich: bool, n: int) -> list[dict]:
    agent = AIAgent(config=WORKER_CONFIG, tools=[])
    resources = [SOURCE] if info_rich else []
    rows: list[dict] = []
    label = "info_rich" if info_rich else "info_poor"
    for i in range(n):
        try:
            res = await agent.execute_task(TASK, resources)
        except Exception as e:  # noqa: BLE001
            rows.append({"attempt": i, "ok": False, "error": str(e)[:120]})
            print(f"  {label} {i + 1}: CRASH {str(e)[:70]}", flush=True)
            continue
        if not res.success:
            rows.append({"attempt": i, "ok": False, "error": res.error_message})
            print(f"  {label} {i + 1}: FAILED", flush=True)
            continue
        content = res.output_resources[0].content if res.output_resources else ""
        q = await score_quality(content, seed=1)
        g = await score_groundedness(content, seed=1)
        rows.append({
            "attempt": i, "ok": True, "len": len(content),
            "quality": q.score if q else None,
            "groundedness": g.score if g else None,
            "unsupported": g.unsupported_claims if g else None,
            "content": content,
        })
        print(f"  {label} {i + 1}: OK len={len(content)} "
              f"quality={q.score if q else '?'} "
              f"groundedness={g.score if g else '?'}", flush=True)
    return rows


def summarize(name: str, rows: list[dict]) -> None:
    ok = [r for r in rows if r["ok"]]

    def mean(key: str) -> str:
        vals = [r[key] for r in ok if r.get(key) is not None]
        return f"{statistics.mean(vals):.2f} (n={len(vals)})" if vals else "n/a"

    print(f"  {name}: completed {len(ok)}/{len(rows)} | "
          f"quality={mean('quality')} groundedness={mean('groundedness')}")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=3, help="attempts per condition")
    parser.add_argument(
        "--out", type=Path, default=Path("experiments/competence_probe/outputs")
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"worker={WORKER_MODEL}  judge={JUDGE_MODEL}\n")
    print("=== info_rich (given the data pack) ===")
    rich = await run_condition(info_rich=True, n=args.n)
    print("=== info_poor (no data pack) ===")
    poor = await run_condition(info_rich=False, n=args.n)

    (args.out / "results.json").write_text(
        json.dumps({"info_rich": rich, "info_poor": poor}, indent=2)
    )
    print("\n--- SUMMARY ---")
    summarize("info_rich", rich)
    summarize("info_poor", poor)
    print("\nGO if: groundedness(info_rich) >> groundedness(info_poor), "
          "quality ~tie, both complete.")


if __name__ == "__main__":
    asyncio.run(main())
