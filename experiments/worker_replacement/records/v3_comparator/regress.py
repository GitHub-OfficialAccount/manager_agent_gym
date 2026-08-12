"""Why does the shipped rebuild lose the L0-prime discrimination?

Two differences between L0-prime and v3.0: the system prompt gained text beyond
the rule, and the user payload became JSON instead of two plain lines. 2x2, n=20.
"""
import asyncio, collections, json, sys
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    ARTIFACT_CLAUSE_PROMPT, JudgmentVerdict, _INCONSISTENCY_RULE,
)
from manager_agent_gym.core.common.llm_interface import generate_structured_response

CLAUSE = ("Apply the robust 95th-percentile reference standard to audit batch A "
          "for all four columns.")
METHOD = ("robust 95th-percentile reference standard (mean+2*SD cutoff from "
          "reference population)")

L0P_PROMPT = ("Judge whether the artifact's stated method satisfies the requirement "
              "clause. Answer supports_fit, contradicts_fit, or neutral. "
              + _INCONSISTENCY_RULE)
PLAIN = f"Requirement clause: {CLAUSE}\nArtifact's stated method: {METHOD}"
JSON_PAYLOAD = json.dumps(
    {"requirement_clause": CLAUSE,
     "artifact_stated_method": [{"evidence_id": "e31", "stated_method": METHOD}]},
    ensure_ascii=False, sort_keys=True)

CONDITIONS = {
    "L0prime  (short prompt + plain)": (L0P_PROMPT, PLAIN),
    "shipped  (v3.0 prompt + JSON) ": (ARTIFACT_CLAUSE_PROMPT, JSON_PAYLOAD),
    "prompt-only change            ": (ARTIFACT_CLAUSE_PROMPT, PLAIN),
    "payload-only change           ": (L0P_PROMPT, JSON_PAYLOAD),
}

async def main(n=20):
    for label, (system, user) in CONDITIONS.items():
        counts = collections.Counter()
        for _ in range(n):
            try:
                v = await generate_structured_response(
                    system_prompt=system, user_prompt=user,
                    response_type=JudgmentVerdict,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                counts[v.stance] += 1
            except Exception as e:
                counts[f"ERR:{type(e).__name__}"] += 1
        print(f"{label} contradicts={counts.get('contradicts_fit',0):2d}/{n}  {dict(counts)}", flush=True)

asyncio.run(main())
