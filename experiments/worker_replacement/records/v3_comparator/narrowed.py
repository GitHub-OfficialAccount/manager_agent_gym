"""Narrowed attribution test: production payload, pinned backend, cached vs nonce-busted.

Backend is held CONSTANT so the contrast isolates cache state -- OpenRouter routes
cache-warm requests to the backend holding the prefix, so an unpinned nonce would
vary backend and cache together.
"""
import argparse, asyncio, collections, json, os, sys, uuid
import httpx
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    RELATION_SYSTEM_PROMPT, RelationBatchResponse, RelationPacket, batch_relation_packets,
)
from experiments.worker_replacement.probe_extraction import _strict_schema

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/replay_reps"
OUT = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
URL = "https://openrouter.ai/api/v1/chat/completions"
SCHEMA = _strict_schema(RelationBatchResponse)

d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]
want = {"e31": "A", "e42": "B", "e52": "C"}
CASE = {}
for b in batch_relation_packets(packets):
    for p in b.packets:
        for e in p.evidence:
            if e.evidence_id in want:
                CASE[want[e.evidence_id]] = {
                    "payload": json.dumps(b.prompt_payload(), ensure_ascii=False),
                    "apply_id": next(c["constraint_id"] for c in p.constraint_checks()
                                     if c["requirement_exact_excerpt"].startswith("Apply the robust"))}


async def call(client, pin, letter, bust):
    case = CASE[letter]
    nonce = f"[request {uuid.uuid4()}] " if bust else ""
    body = {"model": "deepseek/deepseek-v4-flash", "temperature": 0, "seed": 101,
            "messages": [{"role": "system", "content": nonce + RELATION_SYSTEM_PROMPT},
                         {"role": "user", "content": case["payload"]}],
            "response_format": {"type": "json_schema", "json_schema":
                {"name": "R", "strict": True, "schema": SCHEMA}}}
    if pin:
        body["provider"] = {"order": [pin], "allow_fallbacks": False}
    r = await client.post(URL, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                          json=body)
    data = r.json()
    if "error" in data:
        return {"stance": f"ERR:{str(data['error'])[:40]}", "cached": 0, "provider": "?"}
    content = data["choices"][0]["message"]["content"]
    u = data.get("usage") or {}
    rec = {"cached": int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0),
           "provider": data.get("provider", "?")}
    if not content:
        rec["stance"] = "ERR:empty"
        return rec
    parsed = RelationBatchResponse.model_validate_json(content)
    rec["stance"] = next((x.stance for res in parsed.results for x in res.evidence_comparisons
                          if x.constraint_id == case["apply_id"]), "<missing>")
    return rec


async def main(pin, letters, n):
    records = []
    async with httpx.AsyncClient(timeout=180.0) as client:
        for letter in letters:
            for bust in (False, True):
                for i in range(n):
                    try:
                        rec = await call(client, pin, letter, bust)
                    except Exception as e:
                        rec = {"stance": f"ERR:{type(e).__name__}", "cached": 0, "provider": "?"}
                    rec.update({"batch": letter, "cache": "busted" if bust else "asis", "index": i})
                    records.append(rec)
                print(f"done {letter}/{'busted' if bust else 'asis'}", flush=True)
    json.dump(records, open(f"{OUT}/narrowed_{pin}.json", "w"), indent=1)

    print(f"\nPRODUCTION payload, pinned {pin}")
    print(f"{'batch':6s} {'cache':7s} {'n':>3s} {'contra':>7s}  {'distribution':44s} "
          f"{'cache-hit calls':>15s}")
    for key in dict.fromkeys((r["batch"], r["cache"]) for r in records):
        rows = [r for r in records if (r["batch"], r["cache"]) == key]
        counts = collections.Counter(r["stance"] for r in rows)
        print(f"{key[0]:6s} {key[1]:7s} {len(rows):3d} {counts.get('contradicts_fit',0):7d}  "
              f"{str(dict(counts)):44s} {sum(1 for r in rows if r['cached']):15d}")
    print("\n  MANIPULATION CHECK (cached_tokens by call index)")
    for key in dict.fromkeys((r["batch"], r["cache"]) for r in records):
        rows = sorted((r for r in records if (r["batch"], r["cache"]) == key),
                      key=lambda r: r["index"])
        print(f"    {key[0]} {key[1]:7s} cached={[r['cached'] for r in rows]}")
        print(f"    {'':2s} {'':7s} served={sorted(set(r['provider'] for r in rows))}")


ap = argparse.ArgumentParser()
ap.add_argument("--pin", default="Morph")
ap.add_argument("--letters", default="B")
ap.add_argument("--n", type=int, default=20)
a = ap.parse_args()
asyncio.run(main(a.pin, list(a.letters), a.n))
