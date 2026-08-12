"""2x2 again, INTERLEAVED — blocked designs confound condition with wall-clock.

A byte-identical request scored 19/20 in one block and 5/20 forty minutes later,
so any blocked comparison here is confounded with drift. Conditions are now
round-robined so a time trend cannot align with a condition, and the per-half
split lets the drift itself be measured.
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
    "short+plain": (L0P_PROMPT, PLAIN),
    "v3.0 +plain": (ARTIFACT_CLAUSE_PROMPT, PLAIN),
    "short+json ": (L0P_PROMPT, JSON_PAYLOAD),
    "v3.0 +json ": (ARTIFACT_CLAUSE_PROMPT, JSON_PAYLOAD),
}

async def main(n=20):
    tally = {k: collections.Counter() for k in CONDITIONS}
    halves = {k: [collections.Counter(), collections.Counter()] for k in CONDITIONS}
    for i in range(n):
        for label, (system, user) in CONDITIONS.items():
            try:
                v = await generate_structured_response(
                    system_prompt=system, user_prompt=user,
                    response_type=JudgmentVerdict,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                stance = v.stance
            except Exception as e:
                stance = f"ERR:{type(e).__name__}"
            tally[label][stance] += 1
            halves[label][0 if i < n // 2 else 1][stance] += 1
        if (i + 1) % 5 == 0:
            print(f"  round {i+1}/{n}", flush=True)
    print(f"\n{'condition':13s} {'contradicts':>12s}  {'1st half':>9s} {'2nd half':>9s}  distribution")
    for label in CONDITIONS:
        c = tally[label]
        h1, h2 = halves[label]
        print(f"{label:13s} {c.get('contradicts_fit',0):9d}/{n}  "
              f"{h1.get('contradicts_fit',0):9d} {h2.get('contradicts_fit',0):9d}  {dict(c)}")

asyncio.run(main())
