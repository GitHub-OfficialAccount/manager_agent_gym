"""Is the A/B/C inconsistency a formulation problem or a capability problem?

Three conditions on the SAME mixed-claim judgment, n=20 each:
  asis      -- the payload production sends today
  reordered -- Batch B/C constraint list permuted to Batch A's order
  isolated  -- only the mixed-claim clause in constraint_checks (decomposition)
"""
import asyncio, collections, copy, json, sys
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
for batch in batch_relation_packets(packets):
    for p in batch.packets:
        for e in p.evidence:
            if e.evidence_id in want:
                base[want[e.evidence_id]] = batch

def apply_id(payload):
    return next(c["constraint_id"] for c in payload["packets"][0]["constraint_checks"]
                if c["requirement_exact_excerpt"].startswith("Apply the robust"))

def variants(letter):
    payload = base[letter].prompt_payload()
    out = {"asis": copy.deepcopy(payload)}
    checks = payload["packets"][0]["constraint_checks"]
    key = lambda c: (0 if c["requirement_exact_excerpt"].startswith("Apply") else
                     1 if c["requirement_exact_excerpt"].startswith("The outlier") else 2)
    reordered = copy.deepcopy(payload)
    reordered["packets"][0]["constraint_checks"] = sorted(checks, key=key)
    out["reordered"] = reordered
    isolated = copy.deepcopy(payload)
    aid = apply_id(payload)
    isolated["packets"][0]["constraint_checks"] = [c for c in checks if c["constraint_id"] == aid]
    out["isolated"] = isolated
    return out

async def main(n=20):
    for letter in "ABC":
        for name, payload in variants(letter).items():
            aid = apply_id(payload)
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
            contra = counts.get("contradicts_fit", 0)
            print(f"Batch {letter} {name:10s} n={n}  contradicts={contra:2d}/{n}  {dict(counts)}", flush=True)

asyncio.run(main())
