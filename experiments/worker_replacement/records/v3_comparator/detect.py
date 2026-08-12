"""Option (iii): ask the MODEL whether the text states a method, before asking
whether that method is consistent with the clause.

Same decomposition principle as one-question-per-call, one level down: today a
single call is asked a consistency question whose prerequisite -- is there a
method here at all -- has been settled by pattern matching, whose blind spot to
unknown formats is why the default was inverted.

Failure modes are bounded by behaviours we already have. A false "no" reproduces
the pre-inversion skip (the correct verdict for these texts). A false "yes"
routes to the consistency question, which is what happens today.

Ground truth for all 12 fallback judgments: NO method stated (task-failure
notices). Measured on the SUPPORT side too, as a control -- the detector must
not deny methods that plainly exist.
"""
import asyncio, collections, glob, json, sys
from pathlib import Path
from pydantic import BaseModel, ConfigDict
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import RelationPacket, judgments_for
from experiments.worker_replacement.probe_judgment_stability import _gate_patterns, _is_gate_diagnostic
from manager_agent_gym.core.common.llm_interface import generate_structured_response

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"
SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"

class MethodPresence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    states_method: bool

DETECT_PROMPT = (
    "Does the supplied text state a method or approach for how the work was "
    "done? Answer only whether a method is stated, not whether it is correct."
)

fallback, gate_support = {}, {}
for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    pats = _gate_patterns(path.split("/")[-2])
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        packet = RelationPacket.model_validate(entry["packet"])
        titles = [r.text for r in packet.requirements if r.kind == "task_title"]
        for j in judgments_for(packet):
            if j.judgment_kind != "requirement_artifact":
                continue
            # CONTROL MUST MATCH THE PRODUCTION INPUT. In production the
            # detector only ever sees a FALLBACK packet's full artifact text --
            # it never runs on the explicit path, which already found a
            # `method:` field. A first pass fed the control the EXTRACTED value
            # ("percentile") instead of the full artifact atoms, which is a
            # different and much harder question: a bare noun does not "state
            # how the work was done". That produced 10.62% and would have read
            # as a broken detector.
            if j.payload.get("method_extraction") == "full_text_fallback":
                fallback[j.fingerprint()] = "\n".join(
                    c["stated_method"] for c in j.payload["artifact_stated_method"]
                )
            elif _is_gate_diagnostic(j, titles, pats):
                gate_support[j.fingerprint()] = "\n".join(
                    sorted(e.fact for e in packet.evidence)
                )

# JOIN ASSERTION: a lookup that matches nothing is indistinguishable from a
# population with no errors, so the sizes are checked before any calls.
assert fallback, "fallback population empty -- join failed, not a clean result"
assert gate_support, "gate population empty -- join failed, not a clean result"

async def main(n=20):
    control = dict(list(gate_support.items())[:8])
    print(f"detector: {len(fallback)} fallback (truth=no method) + {len(control)} "
          f"explicit controls (truth=method present) x n={n} = "
          f"{(len(fallback)+len(control))*n} calls, interleaved", flush=True)
    rec = collections.defaultdict(list)
    items = [(k, t, False) for k, t in sorted(fallback.items())] + \
            [(k, t, True) for k, t in sorted(control.items())]
    for i in range(n):
        for k, text, truth in items:
            try:
                v = await generate_structured_response(
                    system_prompt=DETECT_PROMPT, user_prompt=text,
                    response_type=MethodPresence,
                    model="openrouter/deepseek/deepseek-v4-flash",
                    seed=101, temperature=0, max_completion_tokens=0)
                rec[k].append(v.states_method)
            except Exception as e:
                rec[k].append(f"ERR:{type(e).__name__}")
        Path(f"{SCRATCH}/detect_v2.json").write_text(json.dumps({k: v for k, v in rec.items()}, indent=1))
        print(f"  round {i+1}/{n}", flush=True)

    for label, group, truth in (("FALLBACK (no method)", fallback, False),
                                ("EXPLICIT (method present)", control, True)):
        ok = tot = 0
        print(f"\n{label}")
        for k in sorted(group):
            vals = [v for v in rec[k] if not isinstance(v, str)]
            correct = sum(1 for v in vals if v is truth)
            ok += correct; tot += len(vals)
            print(f"  {k[:8]}  {correct:2d}/{len(vals):<2d}  {group[k][:58]!r}")
        print(f"  detection accuracy: {ok}/{tot} = {ok/tot:.2%}")

asyncio.run(main())
