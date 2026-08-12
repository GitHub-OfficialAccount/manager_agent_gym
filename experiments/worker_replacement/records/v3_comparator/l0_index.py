"""Re-run L0 logging call index, so cache-warmth and time-varying effects separate."""
import asyncio, collections, json, os, sys
import httpx
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import RelationPacket, batch_relation_packets

BASE = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/replay_reps"
d = json.load(open(f"{BASE}/toolset_to_screening_silent_arm3t_t3_seed101__rep2.json"))
packets = [RelationPacket.model_validate(a["packet"]) for a in d["extraction"]["packet_audit"]]
want = {"e31": "A", "e42": "B", "e52": "C"}
CASE = {}
for b in batch_relation_packets(packets):
    for p in b.packets:
        for e in p.evidence:
            if e.evidence_id in want:
                CASE[want[e.evidence_id]] = {
                    "clause": next(c["requirement_exact_excerpt"] for c in p.constraint_checks()
                                   if c["requirement_exact_excerpt"].startswith("Apply the robust")),
                    "method": b.prompt_payload()["packets"][0]["method_claims"][0]["fact"]}

SYS = ("Judge whether the artifact's stated method satisfies the requirement clause. "
       "Answer supports_fit, contradicts_fit, or neutral.")
SCH = {"type": "object", "properties": {"stance": {"type": "string",
       "enum": ["supports_fit", "contradicts_fit", "neutral"]}},
       "required": ["stance"], "additionalProperties": False}

async def main(n=20):
    recs = []
    async with httpx.AsyncClient(timeout=300.0) as c:
        for letter in "ABC":
            case = CASE[letter]
            user = f"Requirement clause: {case['clause']}\nArtifact's stated method: {case['method']}"
            for i in range(n):
                r = await c.post("https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                    json={"model": "deepseek/deepseek-v4-flash", "temperature": 0, "seed": 101,
                          "messages": [{"role": "system", "content": SYS},
                                       {"role": "user", "content": user}],
                          "response_format": {"type": "json_schema", "json_schema":
                              {"name": "J", "strict": True, "schema": SCH}}})
                data = r.json()
                u = data.get("usage") or {}
                recs.append({"batch": letter, "index": i,
                             "stance": json.loads(data["choices"][0]["message"]["content"])["stance"],
                             "provider": data.get("provider", "?"),
                             "cached": int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0)})
    json.dump(recs, open("/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/l0_index.json", "w"), indent=1)
    for letter in "ABC":
        rows = [r for r in recs if r["batch"] == letter]
        print(f"Batch {letter}")
        print("   verdict=" + "".join("C" if r["stance"]=="contradicts_fit" else "s" if r["stance"]=="supports_fit" else "n" for r in rows))
        print("   cache  =" + "".join("H" if r["cached"] else "." for r in rows))
        tab = collections.defaultdict(collections.Counter)
        for r in rows: tab[(bool(r["cached"]), r["provider"])][r["stance"]] += 1
        for k in sorted(tab, key=str): print(f"     cache={'HIT ' if k[0] else 'MISS'} {k[1]:12s} {dict(tab[k])}")
asyncio.run(main())
