"""Stage B analysis: accuracy vs method-text length, and voting depth vs total variance."""
import collections, json, math, statistics, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import RelationPacket, judgments_for
import glob

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"
SCRATCH = "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad"
rec = json.loads(Path(f"{SCRATCH}/stage_b.json").read_text())

lookup = {}
for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
    for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
        for j in judgments_for(RelationPacket.model_validate(entry["packet"])):
            lookup[j.fingerprint()] = j

def clean(v):
    return [s for s in v["samples"] if not s.startswith("ERR:")]

# ---- gate set: accuracy, modal correctness
print("=== GATE-DIAGNOSTIC SET (n=40)\n")
print(f"{'judgment':10s} {'truth':16s} {'modal':16s} {'share':>6s} {'acc':>6s} {'wrong-dir':>10s} {'len':>5s}")
rows = []
for k, v in sorted(rec.items()):
    if v["set"] != "gate":
        continue
    s = clean(v)
    if not s:
        continue
    counts = collections.Counter(s)
    modal, top = counts.most_common(1)[0]
    truth = v["truth"]
    acc = counts.get(truth, 0) / len(s)
    # "wrong direction" = the error the zero-tolerance bars care about
    wrong = counts.get("contradicts_fit", 0) if truth == "supports_fit" else counts.get("supports_fit", 0)
    j = lookup.get(k)
    length = len(j.payload["artifact_stated_method"][0]["stated_method"]) if j else 0
    rows.append((k, truth, modal, top / len(s), acc, wrong / len(s), length, len(s)))
    flag = "  <-- MODAL WRONG" if modal != truth else ""
    print(f"{k[:8]:10s} {truth:16s} {modal:16s} {top/len(s):6.2f} {acc:6.2f} "
          f"{wrong/len(s):10.3f} {length:5d}{flag}")

modal_ok = sum(1 for r in rows if r[2] == r[1])
print(f"\nmodal correct: {modal_ok}/{len(rows)}")
a = statistics.mean(r[4] for r in rows)
print(f"mean per-call accuracy a = {a:.4f}   a^9 = {a**9:.3f}")

# ---- length correlation
print("\n=== ACCURACY vs METHOD-TEXT LENGTH")
xs = [r[6] for r in rows]
ys = [r[4] for r in rows]
n = len(xs)
mx, my = statistics.mean(xs), statistics.mean(ys)
num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
r_val = num / den if den else float("nan")
print(f"  Pearson r = {r_val:+.3f} over n={n} judgments")
buckets = collections.defaultdict(list)
for row in rows:
    b = "<=15 chars" if row[6] <= 15 else "16-40" if row[6] <= 40 else ">40"
    buckets[b].append(row[4])
for b in ("<=15 chars", "16-40", ">40"):
    if buckets[b]:
        print(f"  {b:12s} n={len(buckets[b]):2d}  mean accuracy {statistics.mean(buckets[b]):.3f}")
for k, *_ in rows:
    if k[:8] in ("f9cd0aa2", "0921e778"):
        row = next(r for r in rows if r[0] == k)
        print(f"  FLAGGED {k[:8]}: len={row[6]} acc={row[4]:.2f} modal={row[2]}")

# ---- voting depth
print("\n=== VOTING DEPTH")
def majority_error(p_err, n_draws):
    """P(majority of n draws lands on the wrong-direction verdict)."""
    need = n_draws // 2 + 1
    return sum(math.comb(n_draws, i) * p_err**i * (1 - p_err) ** (n_draws - i)
               for i in range(need, n_draws + 1))

within = statistics.mean(r[5] for r in rows)
print(f"  within-run wrong-direction rate: {within:.4f}")
# Between-run component: byte-identical requests have been observed swinging
# widely, so inflate the rate by the observed between-run factor as a bound.
for label, p in (("within-run", within), ("total (3x inflated)", min(0.5, within * 3))):
    print(f"  {label}: p={p:.4f}")
    for depth in (1, 3, 5, 7, 9):
        per = majority_error(p, depth) if depth > 1 else p
        cell = (1 - per) ** 9
        print(f"      n={depth}: per-judgment {per:.2e}  P(cell clean, 9 judgments) {cell:.4f}")
