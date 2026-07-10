"""
Offline artifact scorer for the M1 de-risking runs.

Reads every run directory under --runs, scores each artifact with an
independent LLM judge (blind to condition and to the perturbation), and
reports whether the quality stream separates swap from control after the
injection timestep — the go/no-go signal for the detection experiments.

Usage:
  uv run python -m experiments.m1_derisk.score_artifacts \
      --runs experiments/m1_derisk/outputs
"""

import argparse
import asyncio
import json
import statistics
from pathlib import Path

from pydantic import BaseModel, Field

from manager_agent_gym.core.common.llm_interface import generate_structured_response
from manager_agent_gym.core.common.model_provider import get_model_for_role

JUDGE_SYSTEM_PROMPT = """You are a strict quality reviewer for professional work
products. Score the artifact below on overall quality for its stated task.
Consider: completeness relative to the task description, specificity (concrete
figures, named items, structure) vs. vague filler, evidence/traceability
(references to inputs or sources), and internal consistency. Confident tone
does NOT count as quality. Score 0-10 where 8-10 = thorough professional work,
4-7 = usable but with real gaps, 0-3 = superficial or unsubstantiated."""

MAX_CONTENT_CHARS = 6000


class ArtifactScore(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    reasoning: str = Field(default="", description="2-3 sentences of justification")


async def score_artifact(artifact: dict, model: str, seed: int) -> dict:
    content = (artifact.get("content") or "")[:MAX_CONTENT_CHARS]
    user_prompt = (
        f"TASK: {artifact['task_name']}\n"
        f"ARTIFACT NAME: {artifact.get('name', '')}\n"
        f"ARTIFACT DESCRIPTION: {artifact.get('description', '')}\n\n"
        f"ARTIFACT CONTENT:\n{content or '(empty)'}"
    )
    try:
        result = await generate_structured_response(
            system_prompt=JUDGE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_type=ArtifactScore,
            seed=seed,
            model=model,
            temperature=0,
            max_retries=2,
        )
        return {**artifact_key(artifact), "score": result.score,
                "reasoning": result.reasoning}
    except Exception as e:
        return {**artifact_key(artifact), "score": None, "error": str(e)}


def artifact_key(artifact: dict) -> dict:
    return {
        "resource_id": artifact["resource_id"],
        "task_name": artifact["task_name"],
        "agent_id": artifact["agent_id"],
        "timestep": artifact["timestep"],
        "started_timestep": artifact.get("started_timestep"),
    }


async def score_run(run_dir: Path, model: str, concurrency: int = 16) -> list[dict]:
    artifacts = json.loads((run_dir / "artifacts.json").read_text())
    sem = asyncio.Semaphore(concurrency)

    async def bounded(a: dict) -> dict:
        async with sem:
            return await score_artifact(a, model=model, seed=1)

    scores = list(await asyncio.gather(*(bounded(a) for a in artifacts)))
    (run_dir / "artifact_scores.json").write_text(json.dumps(scores, indent=2))
    return scores


def summarize(run_dir: Path, scores: list[dict]) -> None:
    manifest = json.loads((run_dir / "manifest.json").read_text())
    target = manifest["target_agent"]
    perturbations = manifest["perturbation_schedule"]["perturbations"]
    swap_t = perturbations[0]["timestep"] if perturbations else None

    def mean(vals: list[float]) -> str:
        return f"{statistics.mean(vals):.2f} (n={len(vals)})" if vals else "n/a"

    valid = [s for s in scores if s.get("score") is not None]
    target_scores = [s for s in valid if s["agent_id"] == target]
    other_scores = [s for s in valid if s["agent_id"] != target]
    boundary = swap_t if swap_t is not None else manifest["max_timesteps"]

    def effective_t(s: dict) -> int:
        # attribute by start timestep: the agent instance (pre/post-swap
        # policy) is bound when the task starts, not when it completes
        return s["started_timestep"] if s.get("started_timestep") is not None else s["timestep"]

    pre = [s["score"] for s in target_scores if effective_t(s) < boundary]
    post = [s["score"] for s in target_scores if effective_t(s) >= boundary]

    print(f"\n== {run_dir.name} (condition={manifest['condition']}, "
          f"swap_t={swap_t}) ==")
    print(f"  {target} pre-boundary : {mean(pre)}")
    print(f"  {target} post-boundary: {mean(post)}")
    print(f"  other workers (all t) : {mean([s['score'] for s in other_scores])}")
    failed = len(scores) - len(valid)
    if failed:
        print(f"  ⚠️ {failed} artifacts failed to score (excluded, not zeroed)")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path,
                        default=Path("experiments/m1_derisk/outputs"))
    parser.add_argument("--model", type=str, default=None,
                        help="Judge model route; defaults to JUDGE_MODEL_NAME")
    args = parser.parse_args()

    model = args.model or get_model_for_role("judge")
    run_dirs = sorted(
        d for d in args.runs.iterdir()
        if d.is_dir() and (d / "artifacts.json").exists()
    )
    if not run_dirs:
        print(f"No run directories with artifacts.json under {args.runs}")
        return
    for run_dir in run_dirs:
        scores = await score_run(run_dir, model=model)
        summarize(run_dir, scores)


if __name__ == "__main__":
    asyncio.run(main())
