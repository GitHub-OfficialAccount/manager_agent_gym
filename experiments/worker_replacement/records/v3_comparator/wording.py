"""Candidate wordings for the false-contradiction bar, measured interleaved.

Voting is off, so the bar has to be met by calling convention. Two leads from
the Stage B data, neither requiring an ontology:

  (a) paraphrase   -- a procedure restated in fewer/different words still
                      satisfies the clause. `f9cd0aa2` ("95th-percentile
                      reference cutoff" vs a clause naming the same standard)
                      went modal-neutral with 2/20 contradictions.
  (b) thin text    -- guidance for a method claim that is a bare term rather
                      than a description. `0921e778` / `80a52b5f` are the single
                      word "percentile" at accuracy 0.49 / 0.38.

Both sets are measured for every candidate: a wording that cuts false
contradictions but moves recall off 319/319 is disqualified.
"""
import asyncio, collections, glob, json, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    ARTIFACT_CLAUSE_PROMPT, JudgmentVerdict, RelationPacket, judgments_for,
)
from experiments.worker_replacement.probe_judgment_stability import _gate_patterns, _is_gate_diagnostic
from manager_agent_gym.core.common.llm_interface import generate_structured_response

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"
SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
TRUTH = json.loads(Path(f"{SCRATCH}/gate_truth.json").read_text())

_PARAPHRASE = (
    " The same procedure described in different or fewer words still satisfies "
    "the clause; judge the procedure, not the wording."
)
_THIN = (
    " A method claim may be a single term rather than a description; judge it on "
    "the procedure that term names."
)
CANDIDATES = {
    "current      ": ARTIFACT_CLAUSE_PROMPT,
    "a paraphrase ": ARTIFACT_CLAUSE_PROMPT + _PARAPHRASE,
    "b thin-text  ": ARTIFACT_CLAUSE_PROMPT + _THIN,
    "a+b combined ": ARTIFACT_CLAUSE_PROMPT + _PARAPHRASE + _THIN,
}

gate = {}
for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    pats = _gate_patterns(path.split("/")[-2])
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        packet = RelationPacket.model_validate(entry["packet"])
        titles = [r.text for r in packet.requirements if r.kind == "task_title"]
        for j in judgments_for(packet):
            if _is_gate_diagnostic(j, titles, pats):
                gate[j.fingerprint()] = j

supports = [(k, j) for k, j in sorted(gate.items()) if TRUTH.get(k) == "supports_fit"]
contras = [(k, j) for k, j in sorted(gate.items()) if TRUTH.get(k) == "contradicts_fit"]

async def main(n=8):
    total = len(CANDIDATES) * (len(supports) + len(contras)) * n
    print(f"{len(CANDIDATES)} wordings x {len(supports)} supports + {len(contras)} "
          f"contradictions x n={n} = {total} calls, interleaved", flush=True)
    rec = {c: {k: [] for k, _ in supports + contras} for c in CANDIDATES}
    for i in range(n):
        for k, j in supports + contras:
            for label, prompt in CANDIDATES.items():   # interleaved across wordings
                try:
                    v = await generate_structured_response(
                        system_prompt=prompt, user_prompt=j.user_prompt(),
                        response_type=JudgmentVerdict,
                        model="openrouter/deepseek/deepseek-v4-flash",
                        seed=101, temperature=0, max_completion_tokens=0)
                    rec[label][k].append(v.stance)
                except Exception as e:
                    rec[label][k].append(f"ERR:{type(e).__name__}")
        Path(f"{SCRATCH}/wording.json").write_text(json.dumps(rec, indent=1))
        print(f"  round {i+1}/{n}", flush=True)

    print(f"\n{'wording':14s} {'FALSE CONTRA (28 supports)':>27s} {'RECALL (8 contradictions)':>26s}")
    for label in CANDIDATES:
        sup = [x for k, _ in supports for x in rec[label][k] if not x.startswith("ERR:")]
        con = [x for k, _ in contras for x in rec[label][k] if not x.startswith("ERR:")]
        fc = sup.count("contradicts_fit")
        rc = con.count("contradicts_fit")
        print(f"{label:14s} {fc:6d}/{len(sup):<5d} = {fc/len(sup):7.2%}      "
              f"{rc:5d}/{len(con):<5d} = {rc/len(con):7.2%}")
    print("\n  any wording that moves recall off 100% is disqualified regardless of "
          "its false-contradiction rate.")

asyncio.run(main())
