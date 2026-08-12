# Metric, sensitivity gate, and run budget — three-candidate spec

**Status:** specification and estimation only. No code, no runs. Answers §122's RE tasks
1–5. Implements the outcome-primary inversion: deterministic score + oracle regret as the
primary metric, allocation share demoted to mechanism, LLM judges banned from the primary.

**Two findings up front, because they change the three-way comparison:**

1. **The sensitivity gate is pure arithmetic in eDiscovery and finance, and is NOT
   available in SWE.** In the first two, `score(unit, method)` is fixed by construction, so
   oracle-vs-worst spread is computable with zero model calls — exactly the researcher's
   demand. In SWE the score is a *behavioural* outcome of an agent on an issue; it cannot
   be known before measuring it. SWE's gate therefore requires calibration runs, which also
   creates the oracle-fitting hazard (§3c).
2. **Finance is the only candidate whose method-fit variation is a documented property of
   the domain rather than our construction.** eDiscovery's per-custodian suitability is
   labelled "our construction, plausible but unsourced" (§121). Basel SA-vs-IRB divergence
   is portfolio-dependent *in the framework itself* — verified numerically in §3b.

---

## 1. Metric definitions per candidate

Common shape. For instance `I` with units `u ∈ U` and methods `m ∈ {A, B}`:

```
score(I, allocation)  = Σ_u  s(u, method_of(assignee(u)))       # deterministic, no judge
oracle(I)             = max over allocations = Σ_u max_m s(u, m)   # per-unit independence
worst(I)              = Σ_u min_m s(u, m)
regret(I, allocation) = oracle(I) − score(I, allocation)        # the PRIMARY metric
spread(I)             = oracle(I) − worst(I)                    # the SENSITIVITY GATE
```

Per-unit independence is what makes the oracle a maximum rather than a search: each unit's
score depends only on that unit and its assignee's method. It holds in all three candidates
because units (custodians / portfolio segments / issues) are scored separately. **Where it
fails — if a downstream join makes unit scores interdependent — the oracle becomes a
combinatorial optimum and must be stated as such.** It does not fail in any design below,
because the join (QC / reconciliation / integration test) is deliberately excluded from the
primary score and kept as mechanism evidence.

### 1a. eDiscovery

Units = custodians. Methods = keyword (A) vs classifier-based concept review (B).
From the sketch's truth functions:

```
returned(u, m)  = the document set method m returns for custodian u
s(u, m)         = F1( returned(u, m), {d ∈ u : label(d) = responsive} )
```

F1 rather than recall alone, because recall alone is maximised by returning everything and
the corpus's third document class (term-bearing non-responsive) exists precisely to
penalise that. All three quantities are closed-form on the labelled corpus.

**Oracle allocation:** each custodian to the reviewer whose method has higher F1 on it —
computable from the corpus alone. **Regret:** F1 points lost relative to that assignment.

### 1b. Finance / ICAAP — real formula structure, not a re-skin

Units = portfolio segments. Methods = **Standardised Approach (SA)** vs
**Internal Ratings-Based (IRB)**. These are structurally different objects, not two
parameterisations of one:

- **SA**: `RWA(seg) = Σ_i EAD_i × RW(rating_i, asset_class_i)` — a supervisory *lookup
  table* over external ratings.
- **IRB**: `RWA(seg) = 12.5 × Σ_i EAD_i × K_i` — a *continuous function* of PD/LGD/M via
  the asymptotic single-risk-factor model:

```
R(PD)  = 0.12·(1−e^−50·PD)/(1−e^−50) + 0.24·[1 − (1−e^−50·PD)/(1−e^−50)]
b(PD)  = (0.11852 − 0.05478·ln PD)²
MA     = (1 + (M − 2.5)·b) / (1 − 1.5·b)
K      = LGD · [ Φ( (Φ⁻¹(PD) + √R · Φ⁻¹(0.999)) / √(1−R) ) − PD ] · MA
```

**Dependency check, done rather than assumed: this needs no scipy.** `statistics.NormalDist`
in the stdlib provides `cdf` and `inv_cdf`. I implemented and ran the formula; numbers in
§3b. So truth computation is **not** heavier than the eDiscovery sketch in dependencies —
it is heavier in *validation*, which is the real cost (§4).

**What "truth" is here, since both approaches are legitimate.** There is no true capital
number, so the score is not "which approach is right". It is **correct application of the
approach that APPLIES to that segment**: IRB requires supervisory approval and data
sufficiency per portfolio; where absent, SA applies. So:

```
applicable(seg) ∈ {SA, IRB}          # a property of the segment, set at construction
correct(seg)    = RWA computed under applicable(seg), correctly
s(seg, m)       = 1 if m = applicable(seg) and the reported number matches correct(seg)
                  within tolerance, else 0        (or graded: 1 − min(1, |err| / correct))
```

A worker applying SA to an IRB-approved segment produces a number that is wrong *for that
segment* — a real compliance failure, in-scene, not manufactured.

### 1c. SWE

Units = issues. Truth = **hidden per-issue tests**. `s(issue, worker) = fraction of hidden
tests passing`. Sharpest determinism of the three — and the score is a property of the
*agent's output*, not of a designed method, which is what breaks the sensitivity gate (§2c)
and exposes the oracle (§3c).

**Oracle:** assign each issue to the worker with the highest expected pass rate for that
issue's type. **This requires per-(worker, task-type) calibration**, i.e. measurement.

---

## 2. The sensitivity gate — computation shape per env

The gate answers the researcher's "I foresee the scores won't differ" with a number
computed before anything runs. **What it bounds is the design's headroom, not the achieved
effect**: it assumes each worker faithfully executes its method. Whether the agent actually
does is the linchpin check, already gated separately. A large spread does not promise a
result; a small spread proves there cannot be one.

### 2a. eDiscovery — arithmetic, zero model calls

```
for each custodian u:      s(u, keyword), s(u, concept)  ← F1 on the labelled corpus
spread(I) = Σ_u [ max(s(u,A), s(u,B)) − min(s(u,A), s(u,B)) ]
```
Every term is a set operation on documents whose labels we assigned. **Zero model calls,
confirmed.** Tunable before any episode: if the spread is small, change the class mix per
custodian and recompute — a loop of seconds.

### 2b. Finance — arithmetic, zero model calls, and the divergence is real

```
for each segment: correct(seg) under applicable(seg); the other approach's number
spread(I) = Σ_seg [ s(seg, applicable) − s(seg, other) ]   = number of segments (binary form)
```
Binary scoring makes the spread trivially maximal, so the **graded** form is the
informative one, and it is where the real formula earns its place. Computed from the IRB
function above at LGD 0.45, M 2.5, against SA corporate RW 100%:

| segment PD | IRB risk weight | SA risk weight | IRB/SA |
|---|---|---|---|
| 0.1% | 29.7% | 100% | **0.30** |
| 1.0% | 92.3% | 100% | 0.92 |
| 5.0% | 149.9% | 100% | **1.50** |
| 15.0% | 221.5% | 100% | **2.22** |

Applying the wrong approach misstates capital by **−70% to +122%** depending on segment
quality, crossing over near PD ≈ 1.2%. That is a large, segment-dependent, *documented*
divergence — the reason banks seek IRB approval for high-quality books. **Unlike
eDiscovery, the allocation lever here is not our construction**; it is the framework's own
behaviour, which is the strongest realism argument available to any of the three.

### 2c. SWE — the gate is NOT arithmetic, and this is the decisive difference

`s(issue, worker)` is the fraction of hidden tests an agent passes. It is not fixed by
construction; it must be measured. Consequences:

- **The spread cannot be checked before episodes.** The researcher's central demand —
  spread pre-checked, small spread → redesign at no cost — is unavailable here.
- Making it arithmetic would require deterministic strength differences (e.g. withholding a
  tool), which is the artificial-capability-gap the core-tool rule forbids and which the
  calculator no-go already convicted. Prompt-level strengths do not produce deterministic
  pass/fail.
- **The gate becomes a calibration run**: k executions per (worker, task-type) cell, on
  instances held out from evaluation (§3c).

This is not an argument that SWE is a bad environment — its realism and determinism are the
best of the three. It is an argument that **SWE cannot satisfy the gate as specified**, and
the researcher should decide that trade knowingly rather than discover it.

---

## 3. SWE environment costing from scratch

No stock skeleton. Everything below is new build.

| item | estimate |
|---|---|
| repo design: a small codebase with genuine subsystems, plus N issues of designed types | 2–2.5d |
| hidden test harness: per-issue tests, isolated execution, pass-fraction scoring | 1.5d |
| workers as coding agents with prompt-level designed strengths (e.g. by subsystem or issue type) | 0.5d |
| manager-facing task/DAG wiring, issue assignment, trace = diffs and test logs | 0.5–1d |
| DV/scorer, four logging records, comparability assertions | 0.5d |
| **oracle calibration harness + held-out split** (§3c) | 1d |
| **calibration RUNS** (not build: see budget) | — |
| linchpin validation: do the designed strengths actually produce differential pass rates | 1–1.5d |
| **total build** | **7–8.5d** |

**Against the eDiscovery sketch's 5.5–7.0d: SWE is ~1.5d more expensive to build and
carries a calibration cost that eDiscovery does not have at all.**

**Episode length — the number that should worry us most.** Coding agents make many tool
calls with long outputs; a single issue attempt is realistically 3–10× a DS worker task. At
8–12 issues per episode plus manager turns, I estimate **60–120 min/SSR on flash**, against
25–35 for eDiscovery. That is a 2–4× multiplier on every downstream budget line in §5.

**Riskiest item:** not the harness — the **strength design**. We need coding agents that
are genuinely better and worse at *different* issue types, produced by prompt alone, with a
gap large enough to move pass rates and stable enough to calibrate. Every previous attempt
in this project to manufacture a competence gap by prompt alone failed (the v3-prompt
degradation no-go; "act dumb" ignored). The gap that finally worked was tool-tiering, which
here would violate the core-tool rule. **I would rate this the highest-risk item in any of
the three candidates**, and it is not discovered until 1–1.5d of linchpin work.

### 3c. The oracle is exposed, and the fix is a split

SWE's oracle needs per-(worker, task-type) expected pass rates. If those are estimated on
the same instances used for evaluation, the oracle is fitted to the evaluation data and
regret is biased downward by construction — the S8 free-parameter lesson, arriving through
the oracle instead of the baseline.

**Required design:** calibration on a **held-out instance set**, disjoint from the
evaluation suite, with the split defined and reported before any evaluation episode. Cost:
`workers × task-types × k` task executions — at 2 × 3 × 5 = **30 executions**, plus the
harness. These are single-task runs, not full episodes, so cheaper than an SSR, but they
are model calls and must be budgeted.

eDiscovery and finance need none of this: their oracles are arithmetic.

---

## 4. Finance re-cost on real-formula truth

From the `icap` skeleton (`examples/end_to_end_examples/icap/`, workflow + team + 663-line
preferences, no tools — same as every stock scenario).

| item | estimate |
|---|---|
| portfolio generator: segments with EAD/PD/LGD/M/rating/asset-class and `applicable` flag | 1d |
| SA lookup table + IRB formula, stdlib only | 0.5d |
| **validation against published worked examples** — see riskiest item | 0.5–1d |
| tool pair (`compute_rwa_sa`, `compute_rwa_irb`) + shared core tools | 0.75d |
| DAG adaptation from the icap spine + cut list | 0.5–1d |
| cards, prompts, declaration convention | 0.5d |
| scorer, logging records, assertions, sensitivity gate script | 0.5d |
| linchpin validation | 0.5–1d |
| **total** | **4.75–6.25d** |

**Cheaper than eDiscovery (5.5–7.0d) and much cheaper than SWE (7–8.5d)** — because the
truth is a formula rather than a corpus. No documents to write, no labels to assign, and
**no planting-artefact risk at all**, since nothing is planted: the portfolio is data, not
prose that an agent might notice as synthetic.

**Riskiest item: formula correctness.** A wrong Basel implementation is a wrong benchmark,
and it would be wrong in a way that looks entirely plausible — the numbers would still be
numbers. I am not a Basel practitioner. This must be validated against published worked
examples (BCBS documents carry them) before any use, and the validation is a deliverable,
not a code comment. That is what the 0.5–1d validation line buys.

Second risk, smaller: **`applicable(seg)` is our construction** in the same sense
eDiscovery's suitability was — the *divergence* is a documented framework property, but
which segments have IRB approval is something we assign. Label it as design, exactly as
§121 required for custodian suitability.

---

## 5. Instance generation and run budget — real numbers

**Power is not the binding constraint; coverage is.** CHECK-2 established that outcome DVs
are far quieter than behavioural ones (`mean_r_check` n≈8 for equivalence at a 10% margin,
against 175–12000 for behavioural counts). With the inversion to an outcome-primary metric,
detection of a large regret gap needs roughly **4–6 instances per track**. Instance counts
above that buy generalisation claims for the benchmark, not significance.

**Structure.** Tracks = information conditions, main-effects only: `control/no-channel`,
`card`, `declaration`, `ask` (4). Baselines: **oracle costs zero episodes** (arithmetic);
**no-information = the control track** (no extra episodes); **random allocation** needs
episodes but `RandomManagerAgent` already exists (`random_manager.py:83`).

```
episodes = instances × tracks  +  instances (random baseline)  +  2 (gate pair)
```

| tier | instances | tracks | episodes | eDiscovery @30min | finance @30min | SWE @90min |
|---|---|---|---|---|---|---|
| minimum defensible | 6 | 2 (control + one channel) | 20 | **10 h** | 10 h | 30 h |
| **first release** | **10** | **4** | **52** | **26 h** | 26 h | **78 h** |
| full suite | 15 | 5 | 92 | 46 h | 46 h | 138 h |

Add for SWE only: ~30 calibration task-executions (§3c), well under an episode each.

**What I would put to the researcher for authorisation: the first-release row — 52
episodes, ~26 hours wall-clock on eDiscovery or finance.** It supports 4 information
tracks at 10 instances, comfortably above the power floor, with the oracle free and the
random baseline included. On SWE the same design is 78 hours, which is the multiplier the
choice actually turns on.

**Instance-suite generation** varies, per §122's packaging: unit mixes (which units favour
which method), swap timing `t_swap`, and method pair where an env supports more than one.
All three are constructed parameters, so instance generation is arithmetic in eDiscovery
and finance and requires re-calibration in SWE whenever the issue mix changes.

---

## 6. What this spec does not establish

- **No linchpin evidence anywhere.** Every number assumes workers execute their assigned
  method faithfully. The sensitivity gate bounds design headroom; it says nothing about
  achieved effects. For SWE the gap between the two is largest, because its "method" is a
  prompt-level disposition rather than a tool.
- **The Basel formula is implemented and run, not validated.** The numbers in §2b came from
  my own implementation. They are internally consistent and match the qualitative shape
  practitioners describe, but published-example validation has not been done and is a
  precondition for use.
- Build days are single-point judgement, no spread; the linchpin lines are where estimates
  have historically slipped.
- Episode lengths are extrapolated from task counts and agent-behaviour priors. **No stock
  scenario and no coding agent has been run under our harness**; the 60–120 min SWE figure
  is the least anchored number in this document.
- The run budget assumes per-unit independence holds so the oracle is a per-unit maximum.
  If a design later scores the join, that assumption breaks and the oracle needs restating.
