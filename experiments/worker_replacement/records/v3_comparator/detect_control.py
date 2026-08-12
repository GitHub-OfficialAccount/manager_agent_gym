"""Detector control on the ONLY population it can encounter.

A fallback packet is by construction one where `extract_method_text` found
nothing. So the detector must answer YES on method-bearing text in formats the
extractor does not recognise -- which is exactly the population the inversion
exists to protect, and exactly the formats invented for the scope test.

Feeding it explicit-path atoms would be off-population: those contain `method:`
lines, so production would have extracted them and they would never reach the
detector at all. Feeding it an extracted field value ("percentile") is a
different question again, and produced a misleading 10.62% on a first pass.

Inputs come from `judgments_for`, not assembled by hand: the probe derives its
input from the production code path.
"""

import asyncio
import collections
import json
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (  # noqa: E402
    RelationPacket,
    TaskConstraint,
    judgments_for,
)
from manager_agent_gym.core.common.llm_interface import (  # noqa: E402
    generate_structured_response,
)
from manager_agent_gym.core.manager_agent.observation_aids import (  # noqa: E402
    AtomicEvidenceEntry,
)

SCRATCH = (
    "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/"
    "38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
)


class MethodPresence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    states_method: bool


DETECT_PROMPT = (
    "Does the supplied text state a method or approach for how the work was "
    "done? Answer only whether a method is stated, not whether it is correct."
)

# Method-bearing text in formats the extractor does not recognise. This is the
# population the inversion exists to protect, so control and purpose coincide.
UNRECOGNISED = {
    "yaml_block": "approach:\n  standard: percentile\n  window: 90d",
    "markdown_table": "| step | method |\n|------|--------|\n| 1 | percentile cutoff |",
    "prose": "We went ahead and used the usual robust cutoff for this batch.",
    "prose_explicit": "The team applied a mean plus two standard deviations rule.",
}
# Negative control: the real failure notices from the corpus.
FAILURE_NOTICES = {
    "failed_task": "- Failed: Stakeholder failed to complete task",
    "failed_none": "- Failed: None",
    "failed_retry": (
        "- Failed: Stakeholder failed to complete task\n"
        "- Retry requested by manager"
    ),
}


def build(fact: str) -> str:
    """Input taken from judgments_for, never reconstructed."""
    packet = RelationPacket(
        packet_kind="requirement_artifact",
        first_observed_timestep=4,
        worker="w",
        task_id="t",
        task_scope="s",
        trigger_source_pointer="r",
        evidence=[
            AtomicEvidenceEntry(
                evidence_id="e1",
                first_observed_timestep=4,
                worker="w",
                task="T",
                fact=fact,
                source_pointer="r",
            )
        ],
        requirements=[],
        task_constraints=[
            TaskConstraint(
                constraint_id="c1",
                task_id="t",
                requirement_source_id="q1",
                exact_excerpt="Apply the robust standard.",
            )
        ],
    )
    judgments = judgments_for(packet)
    assert judgments, f"expected a fallback judgment for {fact!r}"
    assert judgments[0].payload["method_extraction"] == "full_text_fallback", (
        f"{fact!r} was recognised by the extractor -- off-population"
    )
    return "\n".join(
        str(claim["stated_method"])
        for claim in judgments[0].payload["artifact_stated_method"]
    )


async def main(n: int = 20) -> None:
    cases = [(f"YES {k}", build(v), True) for k, v in UNRECOGNISED.items()] + [
        (f"NO  {k}", build(v), False) for k, v in FAILURE_NOTICES.items()
    ]
    print(f"{len(cases)} cases x n={n} = {len(cases) * n} calls, interleaved", flush=True)
    rec: dict[str, list] = collections.defaultdict(list)
    for index in range(n):
        for label, text, _ in cases:
            try:
                verdict = await generate_structured_response(
                    system_prompt=DETECT_PROMPT,
                    user_prompt=text,
                    response_type=MethodPresence,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101,
                    temperature=0,
                    max_completion_tokens=0,
                )
                rec[label].append(verdict.states_method)
            except Exception as error:
                rec[label].append(f"ERR:{type(error).__name__}")
        Path(f"{SCRATCH}/detect_control.json").write_text(
            json.dumps(dict(rec), indent=1)
        )
        print(f"  round {index + 1}/{n}", flush=True)

    print(f"\n{'case':24s} {'correct':>10s}  text")
    ok = tot = 0
    for label, text, truth in cases:
        vals = [v for v in rec[label] if not isinstance(v, str)]
        correct = sum(1 for v in vals if v is truth)
        ok += correct
        tot += len(vals)
        print(f"{label:24s} {correct:4d}/{len(vals):<5d}  {text[:50]!r}")
    print(f"\ndetector accuracy on-population: {ok}/{tot} = {ok / tot:.2%}")


asyncio.run(main())
