"""Re-check the pinned-Morph positive control, INTERLEAVED.

The original ran as blocks (cached arm to completion, then nonce arm), so
condition was confounded with wall-clock. The packaging attribution leans on
this control reproducing B's failure, so it is re-run round-robined.
"""
import asyncio, collections, json, os, sys, uuid
import httpx
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    RELATION_SYSTEM_PROMPT, RelationBatchResponse, RelationPacket, batch_relation_packets,
)
from experiments.worker_replacement.probe_extraction import _strict_schema

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
URL = "https://openrouter.ai/api/v1/chat/completions"
SCHEMA = _strict_schema(RelationBatchResponse)
d = json.load(open(f"{BASE}/replay_reps/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]
case = None
for b in batch_relation_packets(packets):
    for p in b.packets:
        for e in p.evidence:
            if e.evidence_id == "e42":          # batch B, the cleanest failure
                case = {"payload": json.dumps(b.prompt_payload(), ensure_ascii=False),
                        "apply_id": next(c["constraint_id"] for c in p.constraint_checks()
                                         if c["requirement_exact_excerpt"].startswith("Apply the robust"))}

async def call(client, bust):
    nonce = f"[request {uuid.uuid4()}] " if bust else ""
    body = {"model": "deepseek/deepseek-v4-flash", "temperature": 0, "seed": 101,
            "messages": [{"role": "system", "content": nonce + RELATION_SYSTEM_PROMPT},
                         {"role": "user", "content": case["payload"]}],
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "R", "strict": True, "schema": SCHEMA}},
            "provider": {"order": ["Morph"], "allow_fallbacks": False}}
    r = await client.post(URL, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                          json=body)
    data = r.json()
    if "error" in data:
        return f"ERR:{str(data['error'])[:30]}", 0, "?"
    content = data["choices"][0]["message"]["content"]
    u = data.get("usage") or {}
    cached = int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0)
    if not content:
        return "ERR:empty", cached, data.get("provider", "?")
    parsed = RelationBatchResponse.model_validate_json(content)
    return (next((x.stance for res in parsed.results for x in res.evidence_comparisons
                  if x.constraint_id == case["apply_id"]), "<missing>"),
            cached, data.get("provider", "?"))

async def main(n=20):
    tally = {False: collections.Counter(), True: collections.Counter()}
    cache = {False: [], True: []}
    provs = set()
    async with httpx.AsyncClient(timeout=180.0) as client:
        for i in range(n):
            for bust in (False, True):        # interleaved, not blocked
                try:
                    stance, cached, prov = await call(client, bust)
                except Exception as e:
                    stance, cached, prov = f"ERR:{type(e).__name__}", 0, "?"
                tally[bust][stance] += 1
                cache[bust].append(cached)
                provs.add(prov)
            if (i + 1) % 5 == 0:
                print(f"  round {i+1}/{n}", flush=True)
    print("\nPINNED MORPH, production payload, INTERLEAVED")
    for bust in (False, True):
        label = "nonce-busted" if bust else "cached"
        c = tally[bust]
        warm = sum(1 for x in cache[bust] if x)
        print(f"  {label:13s} contradicts={c.get('contradicts_fit',0):2d}/{n}  "
              f"cache-warm calls={warm:2d}/{n}  {dict(c)}")
    print(f"  providers served: {sorted(provs)}")

asyncio.run(main())
