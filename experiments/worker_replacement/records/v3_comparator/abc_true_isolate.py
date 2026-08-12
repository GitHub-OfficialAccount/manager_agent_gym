"""True single-clause isolation: strip the OTHER clauses from the packet record too.

The earlier `isolated` condition only trimmed constraint_checks; packet.task_constraints
still listed all three clauses, so the model still saw them. This removes both.
"""
import asyncio, collections, json, sys
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    RELATION_SYSTEM_PROMPT, RelationBatchResponse, RelationPacket, batch_relation_packets,
)
from manager_agent_gym.core.common.llm_interface import generate_structured_response

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/replay_reps"
d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]
want = {"e31": "A", "e42": "B", "e52": "C"}
base = {}
for b in batch_relation_packets(packets):
    for p in b.packets:
        for e in p.evidence:
            if e.evidence_id in want:
                base[want[e.evidence_id]] = b

def true_isolated(letter):
    batch = base[letter]
    payload = batch.prompt_payload()
    entry = payload["packets"][0]
    aid = next(c["constraint_id"] for c in entry["constraint_checks"]
               if c["requirement_exact_excerpt"].startswith("Apply the robust"))
    entry["constraint_checks"] = [c for c in entry["constraint_checks"]
                                  if c["constraint_id"] == aid]
    entry["packet"]["task_constraints"] = [c for c in entry["packet"]["task_constraints"]
                                           if c["constraint_id"] == aid]
    return payload, aid

async def main(n=20):
    for letter in "ABC":
        payload, aid = true_isolated(letter)
        counts = collections.Counter()
        for _ in range(n):
            try:
                r = await generate_structured_response(
                    system_prompt=RELATION_SYSTEM_PROMPT,
                    user_prompt=json.dumps(payload, ensure_ascii=False),
                    response_type=RelationBatchResponse,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                counts[next((c.stance for res in r.results
                             for c in res.evidence_comparisons
                             if c.constraint_id == aid), "<missing>")] += 1
            except Exception as e:
                counts[f"ERR:{type(e).__name__}"] += 1
        print(f"Batch {letter} TRUE-isolated n={n}  "
              f"contradicts={counts.get('contradicts_fit',0):2d}/{n}  {dict(counts)}", flush=True)

asyncio.run(main())
