"""Ablation ladder: how much of the A/B/C failure is scaffolding, not capability?

L0 BARE is the researcher's number -- the model's raw capability on this one
comparison, with every piece of our bookkeeping removed.
"""
import argparse, asyncio, collections, json, os, sys
import httpx
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import RelationPacket, batch_relation_packets

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/replay_reps"
URL = "https://openrouter.ai/api/v1/chat/completions"
WIRE = "deepseek/deepseek-v4-flash"

d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]
want = {"e31": "A", "e42": "B", "e52": "C"}
CASE = {}
for b in batch_relation_packets(packets):
    for p in b.packets:
        for e in p.evidence:
            if e.evidence_id in want:
                clause = next(c["requirement_exact_excerpt"] for c in p.constraint_checks()
                              if c["requirement_exact_excerpt"].startswith("Apply the robust"))
                method = next(x["fact"] for x in b.prompt_payload()["packets"][0]["method_claims"])
                CASE[want[e.evidence_id]] = {"clause": clause, "method": method}

L0_SYSTEM = (
    "Judge whether the artifact's stated method satisfies the requirement clause. "
    "Answer supports_fit, contradicts_fit, or neutral."
)
L0_SCHEMA = {
    "type": "object",
    "properties": {"stance": {"type": "string",
                              "enum": ["supports_fit", "contradicts_fit", "neutral"]}},
    "required": ["stance"],
    "additionalProperties": False,
}


async def call(system, user, schema, nonce=""):
    body = {
        "model": WIRE,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": (nonce + user) if nonce else user}],
        "temperature": 0, "seed": 101,
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "J", "strict": True, "schema": schema}},
    }
    async with httpx.AsyncClient(timeout=300.0) as c:
        r = await c.post(URL, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                         json=body)
        r.raise_for_status()
        data = r.json()
    usage = data.get("usage") or {}
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
    return (json.loads(data["choices"][0]["message"]["content"])["stance"],
            data.get("provider", "?"), int(cached or 0))


async def main(n, nonce_test):
    print(f"{'rung':6s} {'batch':6s} {'n':>3s} {'contradicts':>12s}  {'distribution':38s} "
          f"{'cache-hit calls':>15s}  providers")
    for letter in "ABC":
        c = CASE[letter]
        user = f"Requirement clause: {c['clause']}\nArtifact's stated method: {c['method']}"
        counts, provs, hits = collections.Counter(), collections.Counter(), 0
        by_cache = collections.defaultdict(collections.Counter)
        for _ in range(n):
            try:
                stance, prov, cached = await call(L0_SYSTEM, user, L0_SCHEMA)
                counts[stance] += 1
                provs[prov] += 1
                hits += 1 if cached else 0
                by_cache[bool(cached)][stance] += 1
            except Exception as e:
                counts[f"ERR:{type(e).__name__}"] += 1
        print(f"{'L0':6s} {letter:6s} {n:3d} {counts.get('contradicts_fit',0):12d}  "
              f"{str(dict(counts)):38s} {hits:15d}  {dict(provs)}")
        if len(by_cache) > 1:
            print(f"       by cache-hit: {{hit: {dict(by_cache[True])}, miss: {dict(by_cache[False])}}}")

    if nonce_test:
        import uuid
        c = CASE["B"]
        user = f"Requirement clause: {c['clause']}\nArtifact's stated method: {c['method']}"
        counts = collections.Counter()
        for _ in range(n):
            stance, _, _ = await call(L0_SYSTEM, user, L0_SCHEMA,
                                      nonce=f"[req {uuid.uuid4()}]\n")
            counts[stance] += 1
        print(f"{'L0+nonce':6s} {'B':6s} {n:3d} {counts.get('contradicts_fit',0):12d}  {dict(counts)}")


p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=20)
p.add_argument("--nonce", action="store_true")
a = p.parse_args()
asyncio.run(main(a.n, a.nonce))
