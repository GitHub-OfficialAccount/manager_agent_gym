"""PREREG §7.2 step 3, recomputed from Stage B (short+plain) rates.

Gate-diagnostic judgments use DIRECTLY MEASURED per-judgment rates (n=40).
Non-diagnostic judgments are ESTIMATED from the 35-judgment random clean sample
(n=10 each) -- a sample, not a census, as approved. Labelled accordingly.

Diagnostic and non-diagnostic are reported separately and never summed.
"""
import collections, glob, json, math, statistics, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import RelationPacket, judgments_for
from experiments.worker_replacement.probe_judgment_stability import _gate_patterns, _is_gate_diagnostic

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"
SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
rec = json.loads(Path(f"{SCRATCH}/stage_b.json").read_text())

def clean(v): return [s for s in v["samples"] if not s.startswith("ERR:")]

def majority_error(p, n):
    if n == 1: return p
    need = n // 2 + 1
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(need, n + 1))

# measured wrong-DIRECTION rate per gate judgment (the zero-tolerance quantity)
wrong_dir = {}
for k, v in rec.items():
    if v["set"] != "gate": continue
    s = clean(v)
    bad = "contradicts_fit" if v["truth"] == "supports_fit" else "supports_fit"
    wrong_dir[k] = s.count(bad) / len(s)

# deviation-from-mode rate for the clean sample -> estimate for non-diagnostics
clean_dev = []
for k, v in rec.items():
    if v["set"] != "clean": continue
    s = clean(v)
    clean_dev.append(1 - collections.Counter(s).most_common(1)[0][1] / len(s))
est = statistics.mean(clean_dev)

print(f"non-diagnostic deviation rate ESTIMATED from a 35-judgment random sample "
      f"(n=10 each): {est:.3f}\n")
print(f"{'cell':34s} {'gateJ':>5s} {'E[wrong gate n=1]':>17s} {'E[wrong gate n=5]':>17s} "
      f"{'E[dev non-diag]*':>17s}")
for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    cell = path.split("/")[-2]
    pats = _gate_patterns(cell)
    g1 = g5 = nd = 0.0
    gate_n = other_n = 0
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        packet = RelationPacket.model_validate(entry["packet"])
        titles = [r.text for r in packet.requirements if r.kind == "task_title"]
        for j in judgments_for(packet):
            k = j.fingerprint()
            if _is_gate_diagnostic(j, titles, pats):
                gate_n += 1
                p = wrong_dir.get(k, 0.0)
                g1 += p
                g5 += majority_error(p, 5)
            else:
                other_n += 1
                nd += est
    print(f"{cell.replace('toolset_to_screening_',''):34s} {gate_n:5d} {g1:17.3f} "
          f"{g5:17.5f} {nd:17.2f}")
print("\n  * non-diagnostic column is an ESTIMATE from a sample, not a census, and is")
print("    a deviation-from-mode rate (precision), not a zero-tolerance quantity.")
print("  gate columns are directly measured wrong-DIRECTION rates at n=40.")
print("  the two are different costs and are NOT summed.")
