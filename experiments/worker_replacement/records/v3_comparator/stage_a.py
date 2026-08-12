"""Stage A: does the short+plain prompt manufacture FALSE CONTRADICTIONS?

The zero-tolerance gate criterion is "false contradictions on competent
no-change scopes = 0". A terser prompt whose most emphatic sentence is "never
supports_fit for an inconsistent claim" could bias toward contradicts_fit, so
this measures the 28 gate-diagnostic judgments whose ground truth is
supports_fit, before spending Stage B on a configuration we might not ship.

Round-robined across judgments so wall-clock drift cannot align with any one of
them, and the serving backend is recorded on every call.
"""
import asyncio, collections, glob, json, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    JudgmentVerdict, RelationPacket, _INCONSISTENCY_RULE, judgments_for,
)
from experiments.worker_replacement.probe_judgment_stability import _gate_patterns, _is_gate_diagnostic
from manager_agent_gym.core.common.llm_interface import (
    _last_serving_backend, generate_structured_response,
)

SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
TRUTH = json.load(open(f"{SCRATCH}/gate_truth.json"))
SHORT_PROMPT = ("Judge whether the artifact's stated method satisfies the requirement "
                "clause. Answer supports_fit, contradicts_fit, or neutral. "
                + _INCONSISTENCY_RULE)

found = {}
for path in sorted(glob.glob("/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym/"
                             "experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    cell = path.split("/")[-2]
    pats = _gate_patterns(cell)
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        packet = RelationPacket.model_validate(entry["packet"])
        titles = [r.text for r in packet.requirements if r.kind == "task_title"]
        for j in judgments_for(packet):
            if _is_gate_diagnostic(j, titles, pats):
                found[j.fingerprint()] = j

targets = [(k, j) for k, j in sorted(found.items()) if TRUTH.get(k) == "supports_fit"]
OUT = Path(f"{SCRATCH}/stage_a.json")

async def main(n=20):
    print(f"Stage A: {len(targets)} genuine-support judgments x n={n} "
          f"= {len(targets) * n} calls, interleaved", flush=True)
    records = {k: {"samples": [], "providers": []} for k, _ in targets}
    for i in range(n):
        for k, j in targets:
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
        OUT.write_text(json.dumps(records, indent=1))
        print(f"  round {i+1}/{n}", flush=True)

    print(f"\n{'judgment':10s} {'modal':16s} {'share':>6s} {'FALSE CONTRA':>13s}  distribution")
    false_contra = total = 0
    for k, _ in targets:
        samples = [s for s in records[k]["samples"] if not s.startswith("ERR:")]
        counts = collections.Counter(samples)
        modal, top = counts.most_common(1)[0]
        bad = counts.get("contradicts_fit", 0)
        false_contra += bad
        total += len(samples)
        flag = f"{bad}/{len(samples)}" if bad else "-"
        print(f"{k[:8]:10s} {modal:16s} {top/len(samples):6.2f} {flag:>13s}  {dict(counts)}")
    print(f"\nfalse contradictions: {false_contra}/{total} calls = {false_contra/total:.2%}")
    print(f"judgments with ANY false contradiction: "
          f"{sum(1 for k,_ in targets if 'contradicts_fit' in records[k]['samples'])}/{len(targets)}")

asyncio.run(main())
