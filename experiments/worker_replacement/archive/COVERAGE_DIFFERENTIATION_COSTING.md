# Structural-differentiation costing — complementary tool coverage in the finance env

**Status:** estimation only. No code, no runs. Step-2 finalization input.

Costs the worker design where fit is multi-dimensional via **complementary coverage**, the
team is **larger than the swap**, and **O3 achievability** is computed at instance generation
over the actual post-swap roster.

---

## 1. What coverage has to mean here, given the core-tool rule

**Coverage cannot be implemented by withholding tools.** The repository rule is explicit —
removing a core tool switches a worker off rather than grading it — and this project's own
record adds the sharper finding: a manufactured gap only holds if it denies the worker
something a capable model **cannot do itself**. Tool-withholding failed (the calculator
no-go: the no-calc worker scored 15/16 by doing the arithmetic in-head). What worked was
**unavailable information**.

So coverage must be **possession of information, with tools shared by everyone**:

- Every worker holds `compute_rwa_sa()` and `compute_rwa_irb(params)`. No tool is withheld.
- **SA is the universal fallback** — the lookup table needs no private input, so every
  worker can always produce a defensible number for every segment. That is the
  "incumbents retain the table method" requirement, satisfied structurally.
- **IRB coverage = holding the validated model parameters for an asset class** (the
  calibrated PD/LGD/correlation inputs), delivered as private data in that worker's prompt.
  A worker without the parameters for retail cannot produce the retail IRB number and
  correctly falls back to SA.

This is not an analogy to real practice — it *is* the practice. IRB approval means having a
validated model for that portfolio. A quant team approved for corporate but not retail is an
ordinary institutional fact, which makes the mechanism realistic and the story sourceable in
a way that a withheld tool never could be.

## 2. The coverage lattice, and why non-nestedness is load-bearing

Coverage is a set over `(approach × asset_class)` cells. With four workers:

```
W1 (incumbent):  SA[all] + IRB[corporate]
W2 (incumbent):  SA[all] + IRB[retail]
W3 (predecessor):SA[all] + IRB[corporate, sovereign]     ← removed at t_swap
W4 (successor):  SA[all] + IRB[retail, securitisation]   ← added at t_swap
```

No worker's coverage contains another's. **That constraint is not hygiene — it is the single
condition under which the sensitivity gate and difference-not-deficiency hold at the same
time**, and I want that stated because it unifies two requirements that have been tracked
separately:

- **If coverage nests** (A ⊂ B), then B is right everywhere A is right and right in more
  places. B dominates. That is deficiency, *and* it collapses the oracle to "always use B",
  so oracle-vs-worst spread degenerates to a single-worker question. Both gates fail
  together.
- **If coverage is complementary**, no allocation dominates on an instance carrying both
  asset classes; the spread is non-zero by construction; and every worker is fully
  operational everywhere via SA. Both gates hold together.

So "not a superset" is the same constraint as CBS, expressed on coverage sets rather than
item classes. **It should be a validated assertion at generation time, not a design
intention** — a pairwise subset check over the roster, failing loudly.

## 3. Does coverage break the sensitivity-gate arithmetic? No — with three caveats

The gate needs `score(unit, assignee)` pre-run. Under coverage:

```
score(seg, w) = 1                              if applicable(seg) ∈ coverage(w) and computed correctly
              = 1 − min(1, |SA(seg) − correct(seg)| / correct(seg))   if w falls back to SA
oracle(I)  = Σ_seg max_w score(seg, w)
worst(I)   = Σ_seg min_w score(seg, w)
```

Still a deterministic function of `(segment, coverage set)`. **Zero model calls; the gate
survives.** Three caveats, in descending order of how much they matter:

**(a) Spread dilution — the one that bites.** Segments where `applicable = SA` score
perfectly under *every* allocation, because everyone holds SA. They contribute **zero**
spread. So `spread ∝ fraction of segments that are IRB-applicable AND not universally
covered`. Push that fraction up to widen the spread and the low-coverage workers start
looking wrong nearly everywhere — deficiency again. **Complementary coverage is what
resolves the tension**: with W1/W2-style complementarity, a high IRB-applicable fraction
widens the spread *without* making anyone globally worse, because each worker is the right
answer for its own asset class. Nested coverage has no such escape. The generator must
target the IRB-applicable fraction explicitly and the gate sweep must report it.

**(b) Capacity turns the oracle from a max into an assignment problem.** `oracle = Σ max_w`
assumes a worker can take every segment it is best at. If episode sizing makes workers
capacity-bound (more segments than worker-timesteps), the oracle becomes an optimal
assignment. That is still exact and still zero model calls — Hungarian on a 10×4 matrix is
instantaneous — but the *claim* changes, and §1 of METRIC_AND_SENSITIVITY_SPEC currently
says "per-unit independence makes the oracle a maximum". **Either size episodes so capacity
does not bind and assert it, or restate the oracle as an assignment problem.** I would
assert non-binding capacity: it keeps the oracle explainable in one line, which matters for
a benchmark others must trust.

**(c) O3 guarantees attainability, not discoverability.** The achievability check confirms
that for every segment some post-swap worker has the needed coverage. It says nothing about
whether the manager can *find* that worker — and the gap between attainable and found is
precisely the regret the study measures. Worth stating explicitly so a passed O3 is never
read as "the manager can succeed here".

## 4. O3 achievability at instance generation

For each segment: `∃ w ∈ roster_post_swap : applicable(seg) ∈ coverage(w)`. Set-cover
feasibility, `O(N_segments × W)`, milliseconds.

Two requirements beyond the literal ask:

- **Check both rosters.** Achievability must hold pre-swap as well, or early segments are
  unachievable for reasons unrelated to the event.
- **Check the successor is load-bearing.** If every post-swap segment is servable without
  the successor, the replacement carries no allocation consequence and the instance is inert.

  **CORRECTED (§132).** I first wrote this as "≥k segments achievable ONLY via the
  successor". That is **vacuous under SA-universal-fallback**: every worker can act on every
  segment, so no segment is achievable only via anyone, and the condition can never be
  satisfied. Binding form:

  > **≥k segments whose ORACLE allocation routes through the successor** — successor
  > coverage strictly required to attain the oracle score.

  Same intent, mechanically checkable. It also follows that under a universal fallback the
  set-cover half of O3 is **trivially true**, so this oracle-routing condition is O3's entire
  content in this design — the feasibility check is bookkeeping and the load-bearing test is
  this one.

## 5. Build estimate — delta over the two-method finance base

The base finance env (SA/IRB binary, 2 workers) was costed at **4.75–6.25d**. This is the
additional structure.

| component | days | note |
|---|---|---|
| coverage model: per-worker `(approach × asset_class)` sets, config, **non-nestedness validator** | 0.5 | the validator is the load-bearing part |
| parameter provisioning: private calibration data per worker, shared tools consuming it | 0.75 | the unavailable-information mechanism; replaces nothing in the base |
| larger team: 4 workers, cards reflecting approval scope, timeline wiring for remove+add | 0.25 | registry scheduling already exists |
| generator changes: asset-class mix, approval assignment, coverage assignment, IRB-applicable-fraction targeting | 0.5 | (a) above makes the fraction a first-class knob |
| gate generalised from 2 methods to W workers + sweep reports the applicable fraction | 0.5 | |
| O3 achievability + successor-load-bearing assertions, both rosters | 0.25 | |
| logging/assertions: coverage as rendered card content, achievability, non-nestedness | 0.25 | |
| **linchpin: fallback fidelity** (§6) | 0.5–1.0 | the new risk, not present in the binary design |
| **delta** | **+1.75–2.5d** | |
| **total finance env with coverage differentiation** | **6.5–8.75d** | includes the outstanding 0.5–1d Basel validation |

## 6. The new failure mode this design introduces

**Fabrication instead of fallback.** In the binary design a worker either had the method or
did not. Under coverage, a worker lacking retail parameters is asked to compute a retail
capital number and holds a tool that *would* produce it given parameters. The failure mode
is that it **invents plausible parameters** rather than falling back to SA — and the output
would look entirely well-formed: a number, with a method line, in the right format.

This is not hypothetical for this project. The junior worker in the DS linchpin relayed the
z-rule number every time with zero self-correction (14/25/91/92 against a truth of 100),
which is the same shape: confident, well-formed, wrong. Two consequences:

- **It must be the first linchpin check**, before anything downstream is built on it. The
  check is cheap: give a worker a segment outside its coverage and see whether it falls back
  to SA, refuses, or fabricates.
- **It is detectable in the trace even if it happens**, because the tool call carries its
  arguments: fabricated parameters appear as arguments never provisioned to that worker.
  That is a usable integrity assertion, not just a hope — and it is worth building as a
  logged check regardless of how the linchpin goes.

## 7. What this costing does not establish

- No linchpin evidence. The fallback-fidelity risk in §6 is named, not measured.
- Build days are single-point judgement; the linchpin line is where they have slipped before.
- The Basel implementation is still unvalidated against published worked examples (0.5–1d,
  carried in the total).
- §3(b)'s capacity claim assumes episode sizing keeps workers unconstrained; that is an
  assertion to make and check at generation, not a fact I have verified against a sized
  instance.
