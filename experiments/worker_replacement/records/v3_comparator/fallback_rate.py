"""Measure the full_text_fallback population directly: 12 judgments x n=20.

Stage A/B measured only `explicit` judgments -- these packets were skipped then.
The concern is over-interpretation: an artifact stating no method now arrives as
content to judge, and reading a method into `metric`/`details`/failure text is
how a false contradiction on a competent scope would appear.
"""
import asyncio, collections, glob, json, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    JudgmentVerdict, RelationPacket, _INCONSISTENCY_RULE, judgments_for,
)
from manager_agent_gym.core.common.llm_interface import (
    _last_serving_backend, generate_structured_response,
)

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"
SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
from experiments.worker_replacement.arm3_relations import ARTIFACT_CLAUSE_PROMPT
SHORT_PROMPT = ARTIFACT_CLAUSE_PROMPT   # now the shipped, validated prompt

targets = {}
for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        for j in judgments_for(RelationPacket.model_validate(entry["packet"])):
            if j.payload.get("method_extraction") == "full_text_fallback":
                targets[j.fingerprint()] = j

async def main(n=20):
    print(f"{len(targets)} fallback judgments x n={n} = {len(targets)*n} calls, interleaved",
          flush=True)
    rec = {k: {"samples": [], "providers": []} for k in targets}
    for i in range(n):
        for k, j in sorted(targets.items()):
            try:
                v = await generate_structured_response(
                    system_prompt=SHORT_PROMPT, user_prompt=j.user_prompt(),
                    response_type=JudgmentVerdict,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                stance = v.stance
            except Exception as e:
                stance = f"ERR:{type(e).__name__}"
            rec[k]["samples"].append(stance)
            rec[k]["providers"].append((_last_serving_backend.get() or {}).get("provider"))
        Path(f"{SCRATCH}/fallback_rate_v2.json").write_text(json.dumps(rec, indent=1))
    print(f"\n{'judgment':10s} {'modal':16s} {'share':>6s} {'FALSE CONTRA':>13s}  distribution")
    fc = tot = 0
    for k in sorted(rec):
        s = [x for x in rec[k]["samples"] if not x.startswith("ERR:")]
        c = collections.Counter(s)
        modal, top = c.most_common(1)[0]
        bad = c.get("contradicts_fit", 0)
        fc += bad; tot += len(s)
        print(f"{k[:8]:10s} {modal:16s} {top/len(s):6.2f} "
              f"{(f'{bad}/{len(s)}' if bad else '-'):>13s}  {dict(c)}")
    print(f"\nfallback false-contradiction rate: {fc}/{tot} = {fc/tot:.2%}")
    print(f"  (before the wording fix: 177/238 = 74.37%)")
    print(f"  (explicit population, Stage B: 12/1117 = 1.07%)")
asyncio.run(main())
