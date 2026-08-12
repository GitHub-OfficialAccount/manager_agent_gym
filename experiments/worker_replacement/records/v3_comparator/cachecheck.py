import asyncio, os, uuid, httpx, sys
sys.path.insert(0,'/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym')
from experiments.worker_replacement.arm3_relations import RELATION_SYSTEM_PROMPT
URL="https://openrouter.ai/api/v1/chat/completions"
SCH={"type":"object","properties":{"stance":{"type":"string","enum":["supports_fit","contradicts_fit","neutral"]}},"required":["stance"],"additionalProperties":False}
user="Requirement clause: X\nArtifact's stated method: Y"

async def one(c, pin, bust):
    n=f"[request {uuid.uuid4()}] " if bust else ""
    body={"model":"deepseek/deepseek-v4-flash","temperature":0,"seed":101,
          "messages":[{"role":"system","content":n+RELATION_SYSTEM_PROMPT},{"role":"user","content":user}],
          "response_format":{"type":"json_schema","json_schema":{"name":"J","strict":True,"schema":SCH}},
          "provider":{"order":[pin],"allow_fallbacks":False}}
    try:
        r=await c.post(URL, headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"]}, json=body)
        d=r.json()
        if "error" in d: return None
        u=d.get("usage") or {}
        return int((u.get("prompt_tokens_details") or {}).get("cached_tokens",0) or 0)
    except Exception:
        return None

async def main():
    async with httpx.AsyncClient(timeout=90.0) as c:
        print(f"{'provider':14s} {'repeated':22s} {'nonced':22s} clean?", flush=True)
        for pin in ["DeepInfra","Parasail","AkashML","Alibaba","Fireworks","Morph","AtlasCloud","Ambient","Ionstream","CoreWeave"]:
            rep=[await one(c,pin,False) for _ in range(3)]
            bus=[await one(c,pin,True) for _ in range(3)]
            if any(v is None for v in rep+bus):
                print(f"{pin:14s} unavailable/error", flush=True); continue
            clean = all(v>0 for v in rep) and all(v==0 for v in bus)
            print(f"{pin:14s} {str(rep):22s} {str(bus):22s} {'YES' if clean else 'no'}", flush=True)
asyncio.run(main())
