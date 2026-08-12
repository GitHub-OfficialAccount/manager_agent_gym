import asyncio, collections, json, sys
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    JudgmentVerdict, RelationPacket, judgments_for,
)
from manager_agent_gym.core.common.llm_interface import generate_structured_response

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/replay_reps"
d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
targets = []
for a in d["extraction"]["packet_audit"]:
    p = RelationPacket.model_validate(a["packet"])
    for j in judgments_for(p):
        if j.constraint_id and str(j.payload.get("requirement_clause", "")).startswith("Apply the robust"):
            targets.append(j)

async def main(n=20):
    for j in targets:
        counts = collections.Counter()
        for _ in range(n):
            try:
                v = await generate_structured_response(
                    system_prompt=j.system_prompt(), user_prompt=j.user_prompt(),
                    response_type=JudgmentVerdict,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                counts[v.stance] += 1
            except Exception as e:
                counts[f"ERR:{type(e).__name__}"] += 1
        batch = str(j.payload["requirement_clause"]).split("batch ")[1][0]
        print(f"batch {batch}: contradicts={counts.get('contradicts_fit',0):2d}/{n}  {dict(counts)}", flush=True)

asyncio.run(main())
