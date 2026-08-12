"""Stage B: gate-diagnostic set to n=40, plus a random clean sample at n=10.

Stage A's 20 samples per support judgment count toward the 40 -- staging cost a
round trip, not calls. Interleaved across judgments so wall-clock drift cannot
align with any one of them; serving backend recorded on every call.
"""
import asyncio, collections, glob, json, random, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    JudgmentVerdict, RelationPacket, _INCONSISTENCY_RULE, judgments_for,
)
from experiments.worker_replacement.probe_judgment_stability import _gate_patterns, _is_gate_diagnostic
from manager_agent_gym.core.common.llm_interface import (
    _last_serving_backend, generate_structured_response,
)

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"
SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
TRUTH = json.loads(Path(f"{SCRATCH}/gate_truth.json").read_text())
SHORT_PROMPT = ("Judge whether the artifact's stated method satisfies the requirement "
                "clause. Answer supports_fit, contradicts_fit, or neutral. "
                + _INCONSISTENCY_RULE)
OUT = Path(f"{SCRATCH}/stage_b.json")
CLEAN_SAMPLE_SEED = 20260725

everything, gate = {}, {}
for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    pats = _gate_patterns(path.split("/")[-2])
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        packet = RelationPacket.model_validate(entry["packet"])
        titles = [r.text for r in packet.requirements if r.kind == "task_title"]
        for j in judgments_for(packet):
            everything[j.fingerprint()] = j
            if _is_gate_diagnostic(j, titles, pats):
                gate[j.fingerprint()] = j

clean_pool = sorted(k for k in everything if k not in gate)
rng = random.Random(CLEAN_SAMPLE_SEED)
clean_sample = sorted(rng.sample(clean_pool, 35))   # random, recorded, not hand-picked

# Stage A's samples count toward Stage B's 40.
prior = json.loads(Path(f"{SCRATCH}/stage_a.json").read_text())
records = {k: {"samples": list(v["samples"]), "providers": list(v["providers"]),
               "set": "gate", "truth": TRUTH.get(k)}
           for k, v in prior.items()}
for k in gate:
    records.setdefault(k, {"samples": [], "providers": [], "set": "gate",
                           "truth": TRUTH.get(k)})
for k in clean_sample:
    records.setdefault(k, {"samples": [], "providers": [], "set": "clean", "truth": None})

TARGET = {"gate": 40, "clean": 10}

async def one(j, k):
    try:
        v = await generate_structured_response(
            system_prompt=SHORT_PROMPT, user_prompt=j.user_prompt(),
            response_type=JudgmentVerdict,
            model="openrouter/deepseek/deepseek-v4-flash",
            seed=101, temperature=0, max_completion_tokens=0)
        stance = v.stance
    except Exception as e:
        stance = f"ERR:{type(e).__name__}"
    backend = _last_serving_backend.get() or {}
    records[k]["samples"].append(stance)
    records[k]["providers"].append(backend.get("provider"))

async def main():
    todo = {k: TARGET[records[k]["set"]] - len(records[k]["samples"]) for k in records}
    total = sum(max(0, v) for v in todo.values())
    print(f"gate set {len(gate)} -> n=40, clean sample {len(clean_sample)} -> n=10 "
          f"(clean seed {CLEAN_SAMPLE_SEED}); {total} calls remaining", flush=True)
    Path(f"{SCRATCH}/stage_b_clean_sample.json").write_text(json.dumps(clean_sample, indent=1))
    for rnd in range(max(todo.values())):
        pending = [k for k in records if len(records[k]["samples"]) < TARGET[records[k]["set"]]]
        if not pending:
            break
        for k in pending:
            source = gate.get(k) or everything[k]
            await one(source, k)
        OUT.write_text(json.dumps(records, indent=1))
        print(f"  round {rnd+1}: {len(pending)} judgments sampled", flush=True)
    print("STAGE_B_DONE", flush=True)

asyncio.run(main())
