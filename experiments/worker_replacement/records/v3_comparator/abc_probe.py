"""Same mixed claim, three batch letters: does the comparator answer consistently?"""
import asyncio, collections, json, sys
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    RELATION_SYSTEM_PROMPT, RelationBatchResponse, RelationPacket, batch_relation_packets,
)
from manager_agent_gym.core.common.llm_interface import generate_structured_response

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/replay_reps"
d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]

targets = {}
for batch in batch_relation_packets(packets):
    ids = {e.evidence_id for p in batch.packets for e in p.evidence}
    for ev, letter in (("e31", "A"), ("e42", "B"), ("e52", "C")):
        if ev in ids:
            targets[letter] = (batch, ev)

async def main(n=20):
    counts = collections.defaultdict(collections.Counter)
    for letter, (batch, ev) in sorted(targets.items()):
        prompt = json.dumps(batch.prompt_payload(), ensure_ascii=False)
        apply_id = next(
            c["constraint_id"] for p in batch.packets for c in p.constraint_checks()
            if c["requirement_exact_excerpt"].startswith("Apply the robust")
        )
        for _ in range(n):
            try:
                r = await generate_structured_response(
                    system_prompt=RELATION_SYSTEM_PROMPT, user_prompt=prompt,
                    response_type=RelationBatchResponse, model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                stance = next(
                    (c.stance for res in r.results for c in res.evidence_comparisons
                     if c.constraint_id == apply_id), "<missing>")
            except Exception as e:
                stance = f"ERR:{type(e).__name__}"
            counts[letter][stance] += 1
        print(f"Batch {letter} ({ev}) 'Apply the robust 95th-percentile...' n={n}: {dict(counts[letter])}", flush=True)

asyncio.run(main())
