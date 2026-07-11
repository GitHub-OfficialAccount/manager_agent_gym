"""
Score reroute micro-experiment runs and report the reroute effect.

For every artifact: quality (generic) + groundedness (vs the task type's source
pack). Then, for CAPITAL tasks started AFTER the swap, compare quality/
groundedness across control / silent / oracle. The reroute hurts if
silent << control; the manager recovers if it re-routes capital tasks to the
new holder (junior_analyst). Regret = oracle - silent.

  uv run python -m experiments.micro_reroute.score
"""

import argparse
import asyncio
import json
import statistics
from pathlib import Path

from pydantic import BaseModel, Field

from manager_agent_gym.core.common.llm_interface import generate_structured_response
from .scenario import SOURCE_BY_TYPE

JUDGE_MODEL = "openrouter/openai/gpt-4o-mini"


class QualityScore(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    reasoning: str = Field(default="")


class GroundednessScore(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    reasoning: str = Field(default="")


QUALITY_PROMPT = (
    "You are a strict quality reviewer. Score the artifact 0-10 on overall "
    "quality for its task: completeness, specificity, structure, consistency. "
    "Confident tone does not count as quality."
)
GROUNDEDNESS_PROMPT = (
    "You are a fact-checking auditor given a SOURCE of ground-truth figures and "
    "an ARTIFACT. Score 0-10 how well the artifact's specific figures are "
    "grounded in the SOURCE (10=all present and matching; 0=fabricated or "
    "contradicting). Confident but UNSUPPORTED numbers must score LOW."
)


async def _score(model_cls, system, user, seed=1):
    try:
        return await generate_structured_response(
            system_prompt=system, user_prompt=user, response_type=model_cls,
            seed=seed, model=JUDGE_MODEL, temperature=0, max_retries=2)
    except Exception:
        return None


async def score_artifact(a: dict) -> dict:
    content = a.get("content") or ""
    q = await _score(QualityScore, QUALITY_PROMPT,
                     f"TASK: {a['task_name']}\n\nARTIFACT:\n{content}")
    source = SOURCE_BY_TYPE.get(a["task_type"])
    g = None
    if source:
        g = await _score(GroundednessScore, GROUNDEDNESS_PROMPT,
                         f"SOURCE:\n{source}\n\nARTIFACT:\n{content}")
    return {
        "task_name": a["task_name"], "task_type": a["task_type"],
        "agent_id": a["agent_id"], "started_timestep": a.get("started_timestep"),
        "quality": q.score if q else None,
        "groundedness": g.score if g else None,
    }


async def score_run(run_dir: Path) -> list[dict]:
    artifacts = json.loads((run_dir / "artifacts.json").read_text())
    scores = list(await asyncio.gather(*(score_artifact(a) for a in artifacts)))
    (run_dir / "artifact_scores.json").write_text(json.dumps(scores, indent=2))
    return scores


def _mean(vals: list) -> str:
    v = [x for x in vals if x is not None]
    return f"{statistics.mean(v):.2f} (n={len(v)})" if v else "n/a"


def report(run_dir: Path, scores: list[dict]) -> dict:
    m = json.loads((run_dir / "manifest.json").read_text())
    swap_t = m["swap_timestep"]

    def post_capital(scores):
        return [s for s in scores if s["task_type"] == "capital"
                and (s["started_timestep"] or 0) >= swap_t]

    pc = post_capital(scores)
    q = _mean([s["quality"] for s in pc])
    g = _mean([s["groundedness"] for s in pc])
    who = {}
    for s in pc:
        who[s["agent_id"]] = who.get(s["agent_id"], 0) + 1
    print(f"\n== {run_dir.name} (condition={m['condition']}) ==")
    print(f"  post-swap CAPITAL tasks: quality={q} groundedness={g}")
    print(f"  routed to: {who}  (optimal after reroute: {m['reroute_to']})")
    qv = [s["quality"] for s in pc if s["quality"] is not None]
    gv = [s["groundedness"] for s in pc if s["groundedness"] is not None]
    return {"condition": m["condition"],
            "post_capital_quality": statistics.mean(qv) if qv else None,
            "post_capital_groundedness": statistics.mean(gv) if gv else None}


async def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", type=Path, default=Path("experiments/micro_reroute/outputs"))
    args = p.parse_args()
    dirs = sorted(d for d in args.runs.iterdir()
                  if d.is_dir() and (d / "artifacts.json").exists())
    summ = {}
    for d in dirs:
        scores = await score_run(d)
        r = report(d, scores)
        summ[r["condition"]] = r
    if "oracle" in summ and "silent" in summ:
        for metric in ("post_capital_quality", "post_capital_groundedness"):
            o, s = summ["oracle"].get(metric), summ["silent"].get(metric)
            if o is not None and s is not None:
                print(f"\nregret ({metric}) = oracle - silent = {o - s:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
