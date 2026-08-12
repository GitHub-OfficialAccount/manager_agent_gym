"""L0-prime and the order-reversal test, with per-call index/cache/backend logging."""
import argparse, asyncio, collections, json, os, sys
import httpx
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    RELATION_SYSTEM_PROMPT, RelationBatchResponse, RelationPacket, batch_relation_packets,
)

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
                clause = next(c["requirement_exact_excerpt"] for c in p.constraint_checks()
                              if c["requirement_exact_excerpt"].startswith("Apply the robust"))
                CASE[want[e.evidence_id]] = {
                    "clause": clause,
                    "method": b.prompt_payload()["packets"][0]["method_claims"][0]["fact"],
                    "batch": b,
                    "apply_id": next(c["constraint_id"] for c in p.constraint_checks()
                                     if c["requirement_exact_excerpt"].startswith("Apply the robust")),
                }

# The one sentence from RELATION_SYSTEM_PROMPT that IS the discrimination.
RULE = (
    "If the artifact's stated method text names two different, mutually inconsistent "
    "procedures at once (for example claiming one standard by name while its own "
    "description performs a different one), that must never be judged supports_fit -- "
    "treat it as contradicts_fit if the described procedure plainly departs from the "
    "clause, or neutral if it is genuinely ambiguous which procedure was actually used."
)
L0P_SYSTEM = (
    "Judge whether the artifact's stated method satisfies the requirement clause. "
    "Answer supports_fit, contradicts_fit, or neutral. " + RULE
)
FLAT_SCHEMA = {
    "type": "object",
    "properties": {"stance": {"type": "string",
                              "enum": ["supports_fit", "contradicts_fit", "neutral"]}},
    "required": ["stance"], "additionalProperties": False,
}


async def post(body):
    async with httpx.AsyncClient(timeout=300.0) as c:
        r = await c.post(URL, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                         json=body)
        r.raise_for_status()
        return r.json()


async def call_flat(system, user):
    data = await post({
        "model": WIRE, "temperature": 0, "seed": 101,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "J", "strict": True, "schema": FLAT_SCHEMA}},
    })
    u = data.get("usage") or {}
    return (json.loads(data["choices"][0]["message"]["content"])["stance"],
            data.get("provider", "?"),
            int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0))


async def call_production(letter):
    """Full production payload + RELATION_SYSTEM_PROMPT, via raw HTTP so usage is visible."""
    c = CASE[letter]
    data = await post({
        "model": WIRE, "temperature": 0, "seed": 101,
        "messages": [{"role": "system", "content": RELATION_SYSTEM_PROMPT},
                     {"role": "user", "content": json.dumps(c["batch"].prompt_payload(),
                                                            ensure_ascii=False)}],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "RelationBatchResponse", "strict": False,
            "schema": RelationBatchResponse.model_json_schema()}},
    })
    u = data.get("usage") or {}
    parsed = RelationBatchResponse.model_validate_json(data["choices"][0]["message"]["content"])
    stance = next((x.stance for res in parsed.results for x in res.evidence_comparisons
                   if x.constraint_id == c["apply_id"]), "<missing>")
    return (stance, data.get("provider", "?"),
            int((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0))


def report(records, title):
    print(f"\n=== {title}")
    print(f"{'cond':22s} {'n':>3s} {'contra':>7s}  {'distribution':44s} {'hits':>5s}")
    for cond in dict.fromkeys(r["cond"] for r in records):
        rows = [r for r in records if r["cond"] == cond]
        counts = collections.Counter(r["stance"] for r in rows)
        hits = sum(1 for r in rows if r["cached"])
        print(f"{cond:22s} {len(rows):3d} {counts.get('contradicts_fit',0):7d}  "
              f"{str(dict(counts)):44s} {hits:5d}")
    print("\n  verdict by CALL INDEX (separates cache-warmth from any time-varying effect)")
    for cond in dict.fromkeys(r["cond"] for r in records):
        rows = sorted((r for r in records if r["cond"] == cond), key=lambda r: r["index"])
        seq = "".join("C" if r["stance"] == "contradicts_fit" else
                      "s" if r["stance"] == "supports_fit" else "n" for r in rows)
        cch = "".join("H" if r["cached"] else "." for r in rows)
        print(f"    {cond:22s} verdict={seq}")
        print(f"    {'':22s} cache  ={cch}")
    print("\n  verdict x cache x backend")
    tab = collections.defaultdict(collections.Counter)
    for r in records:
        tab[(r["cond"], bool(r["cached"]), r["provider"])][r["stance"]] += 1
    for k in sorted(tab, key=str):
        print(f"    {k[0]:22s} cache={'HIT ' if k[1] else 'MISS'} {k[2]:12s} {dict(tab[k])}")


async def main(mode, n):
    records = []
    if mode == "l0prime":
        for letter in "ABC":
            c = CASE[letter]
            user = f"Requirement clause: {c['clause']}\nArtifact's stated method: {c['method']}"
            for i in range(n):
                s, p, ch = await call_flat(L0P_SYSTEM, user)
                records.append({"cond": f"L0prime-{letter}", "index": i, "stance": s,
                                "provider": p, "cached": ch})
            print(f"done L0prime-{letter}", flush=True)
        report(records, "L0-PRIME: minimal payload + the inconsistency rule only")
    else:
        # Order reversal: C, then B, then A -- production payload unchanged.
        for letter in "CBA":
            for i in range(n):
                s, p, ch = await call_production(letter)
                records.append({"cond": f"reversed-{letter}", "index": i, "stance": s,
                                "provider": p, "cached": ch})
            print(f"done reversed-{letter}", flush=True)
        report(records, "ORDER REVERSAL: production payload, judged C -> B -> A")
    json.dump(records, open(f"{OUT}/ladder2_{mode}.json", "w"), indent=1)


ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["l0prime", "reversed"])
ap.add_argument("--n", type=int, default=20)
a = ap.parse_args()
asyncio.run(main(a.mode, a.n))
