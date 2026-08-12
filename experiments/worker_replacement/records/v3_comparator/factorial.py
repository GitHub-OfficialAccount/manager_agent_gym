"""2x2 factorial: payload (minimal+rule vs production) x cache (as-is vs nonce-busted).

Holds payload constant while manipulating cache, which the L0-prime vs production
comparison cannot do -- there, short-prompt and low-cache-exposure are confounded.
The critical cell is production+nonce: full bookkeeping, caching defeated.
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
WIRE = "deepseek/deepseek-v4-flash"

d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]
want = {"e31": "A", "e42": "B", "e52": "C"}
CASE = {}
for b in batch_relation_packets(packets):
    for p in b.packets:
        for e in p.evidence:
            if e.evidence_id in want:
                aid = next(c["constraint_id"] for c in p.constraint_checks()
                           if c["requirement_exact_excerpt"].startswith("Apply the robust"))
                CASE[want[e.evidence_id]] = {
                    "clause": next(c["requirement_exact_excerpt"] for c in p.constraint_checks()
                                   if c["constraint_id"] == aid),
                    "method": b.prompt_payload()["packets"][0]["method_claims"][0]["fact"],
                    "payload": json.dumps(b.prompt_payload(), ensure_ascii=False),
                    "apply_id": aid,
                }

RULE = (
    "If the artifact's stated method text names two different, mutually inconsistent "
    "procedures at once (for example claiming one standard by name while its own "
    "description performs a different one), that must never be judged supports_fit -- "
    "treat it as contradicts_fit if the described procedure plainly departs from the "
    "clause, or neutral if it is genuinely ambiguous which procedure was actually used."
)
MINIMAL_SYSTEM = (
    "Judge whether the artifact's stated method satisfies the requirement clause. "
    "Answer supports_fit, contradicts_fit, or neutral. " + RULE
)
FLAT_SCHEMA = {"type": "object",
               "properties": {"stance": {"type": "string",
                              "enum": ["supports_fit", "contradicts_fit", "neutral"]}},
               "required": ["stance"], "additionalProperties": False}


async def run_cell(client, payload_kind, bust, letter, n):
    case, recs = CASE[letter], []
    for i in range(n):
        # Nonce goes at the very START of the system prompt so no prefix is reusable.
        nonce = f"[request {uuid.uuid4()}] " if bust else ""
        if payload_kind == "minimal":
            system, user = nonce + MINIMAL_SYSTEM, (
                f"Requirement clause: {case['clause']}\n"
                f"Artifact's stated method: {case['method']}")
            schema, name, strict = FLAT_SCHEMA, "J", True
        else:
            system, user = nonce + RELATION_SYSTEM_PROMPT, case["payload"]
            schema, name, strict = _strict_schema(RelationBatchResponse), "R", True
        try:
            r = await client.post(URL,
                headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                json={"model": WIRE, "temperature": 0, "seed": 101,
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user", "content": user}],
                      "response_format": {"type": "json_schema", "json_schema":
                          {"name": name, "strict": strict, "schema": schema}}})
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            if not content:
                raise ValueError(f"empty content; finish={data['choices'][0].get('finish_reason')}")
            if payload_kind == "minimal":
                stance = json.loads(content)["stance"]
            else:
                parsed = RelationBatchResponse.model_validate_json(content)
                stance = next((x.stance for res in parsed.results
                               for x in res.evidence_comparisons
                               if x.constraint_id == case["apply_id"]), "<missing>")
            u = data.get("usage") or {}
            recs.append({"payload": payload_kind, "cache": "busted" if bust else "asis",
                         "batch": letter, "index": i, "stance": stance,
                         "provider": data.get("provider", "?"),
                         "cached": int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0),
                         "prompt_tokens": int(u.get("prompt_tokens") or 0)})
        except Exception as e:
            recs.append({"payload": payload_kind, "cache": "busted" if bust else "asis",
                         "batch": letter, "index": i, "stance": f"ERR:{type(e).__name__}",
                         "provider": "?", "cached": 0, "prompt_tokens": 0})
    return recs


async def main(n):
    records = []
    async with httpx.AsyncClient(timeout=300.0) as client:
        for payload_kind in ("minimal", "production"):
            for bust in (True,):          # as-is cells already measured
                for letter in "ABC":
                    records += await run_cell(client, payload_kind, bust, letter, n)
                    print(f"done {payload_kind}/{'busted' if bust else 'asis'}/{letter}", flush=True)
    json.dump(records, open(f"{OUT}/factorial.json", "w"), indent=1)

    print(f"\n{'payload':11s} {'cache':7s} {'batch':6s} {'n':>3s} {'contra':>7s}  "
          f"{'distribution':46s} {'hits':>5s} {'med_prompt_tok':>15s}")
    for key in dict.fromkeys((r["payload"], r["cache"], r["batch"]) for r in records):
        rows = [r for r in records if (r["payload"], r["cache"], r["batch"]) == key]
        counts = collections.Counter(r["stance"] for r in rows)
        hits = sum(1 for r in rows if r["cached"])
        toks = sorted(r["prompt_tokens"] for r in rows)
        print(f"{key[0]:11s} {key[1]:7s} {key[2]:6s} {len(rows):3d} "
              f"{counts.get('contradicts_fit',0):7d}  {str(dict(counts)):46s} {hits:5d} "
              f"{toks[len(toks)//2]:15d}")
    print("\n  NONCE CHECK -- cached_tokens must be 0 on busted calls")
    for key in dict.fromkeys((r["payload"], r["cache"]) for r in records):
        rows = [r for r in records if (r["payload"], r["cache"]) == key]
        print(f"    {key[0]:11s} {key[1]:7s} calls={len(rows):3d} "
              f"with cached_tokens>0: {sum(1 for r in rows if r['cached'])}")


ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=20)
a = ap.parse_args()
asyncio.run(main(a.n))
