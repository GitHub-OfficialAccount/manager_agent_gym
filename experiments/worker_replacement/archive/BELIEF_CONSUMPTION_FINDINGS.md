# Belief-layer consumption: what the manager does with the aid

> **STATUS 2026-07-27 — EVIDENCE LOG. Superseded as a summary by `CONSUMPTION_BOTTLENECK.md`.**
> Keep for the per-section measurements, which are not duplicated anywhere: §4 `noq` completion
> cancellation, §5a reward ceiling and propagation, §5d the authorised same-cell re-run.
> **Do not cite this file for the headline or for any rate.** Two things in it are now scoped or
> superseded: §5b's *"never read"* holds for flash only (pro reads the channel), and its articulation
> figures were correct when written but the corpus figure is **3 of 12 silent runs**. Both are annotated
> in place.


> **Provenance note added 2026-07-27.** The label **`v2.6`** is **ambiguous** and must not be used as a
> run identifier. Two distinct runs of the same cell carried it: `71770f08bfd5` (644 rows, r_check
> 0.7317), which **nothing in this analysis used**, and **`c91475579309`** (960 rows, r_check 0.8592),
> which is the run **every v2.6 figure in this document cites** — the t=12 support-side observation, the
> v2.6 assignment timeline, and the r_check table. Preserved at
> `records/preserved_outputs/<cell>/c91475579309/`. Version tokens are now config tags where the
> artifact has one; a release name cannot identify a run.


Read-only analysis over existing run artifacts. **Zero API calls; no run was executed
to produce anything here.** Every figure below is reproducible from
`experiments/worker_replacement/outputs/**/arm3_state.json`, `manager_actions.json` and
`run.json`.

Scope note: one scenario (`toolset_to_screening`), one seed (101), five runs
(v2.6 `smoke101_5b19b5b` x4, v3.0 x1). Nothing here is a rate over a population.

---

## 1. The aid's default state is an endorsement

Rendered rows in the v3.0 run (`silent_arm3i_q`), n = 1004:

| score | category | rows | share |
|---|---|---:|---:|
| +1.5 | supported | 102 | 10.2% |
| **+0.5** | **supported** | **784** | **78.1%** |
| +0.0 | uncertain | 96 | 9.6% |
| -0.5 / -1.5 / -2.5 | contradicted | 22 | 2.2% |

`PROFILE_PRIOR = 0.5` and `_fit_category` uses `value >= 0.5 -> supported`
(`arm3_belief.py`), so the bare prior lands **exactly** on the positive threshold.
Both boundaries are inclusive **by specification** (`ARM3_SPEC.md:255-257`), not by
implementation accident.

Decomposition of the 784 rows at exactly +0.5:

- **694 (69.1% of all rows)** — no relation of any kind, and no completions.
- **90 (9.0%)** — neutral relations only, and **all 90 carry completions**.

Three figures, three denominators. Two of them round to 78% and are *not* the same
measurement:

- **78.1%** = 784/1004, rows on the +0.5 boundary
- **69.1%** = 694/1004, rows with zero evidence
- **78.3%** = 694/886, zero-evidence share of *supported* rows

### Fairness qualifier (required)

The conflation is in the **aggregate column only**. `observed_fit` reads `untested`
on the 694 and `inconclusive` on the 90. The defensible claim is:

> the aggregate the aid computes to supersede its components discards the
> distinction its components preserve

A claim that the aid *conceals* the distinction is refuted by one column.

### Neutrals score as endorsements

`neutral_ids` is computed and stored but never enters `fit_score`
(`arm3_belief.py:170-175`) — weight zero. All 90 neutral-only rows render
`supported`. The comparator did the work, returned "insufficient", and the
aggregate scored it identically to a clean record.

`ARM3_SPEC §368` justifies the thresholds from the negative knife-edge
(`0.5 - 1.0 = -0.5`, one contradiction renders `contradicted`) and is **silent on
the positive one**, which is 78.1% of the rendered surface.

---

## 2. Routing does not read the score

Decisions with >= 2 tier-eligible candidates (`WORKER_TIERS`, `run.py:61`) rendered
at **different** scores, across all five runs:

| variant | t | chose | at | candidates | score==max |
|---|---:|---|---:|---|---|
| arm3i_q (v2.6) | 12 | portfolio_analyst | +1.5 | portfolio +1.5, risk +0.5 | yes |
| arm3i_q (v2.6) | 16 | portfolio_analyst | +2.5 | portfolio +2.5, risk +0.5 | yes |
| arm3t  (v2.6) | 11 | portfolio_analyst | +1.5 | portfolio +1.5, risk +0.5 | yes |
| arm3t  (v2.6) | 14 | portfolio_analyst | +2.0 | portfolio +2.0, risk +0.5 | yes |
| **arm3i_q (v2.6)** | **12** | **portfolio_analyst** | **+0.5** | **portfolio +0.5, risk +1.5** | **no** |
| **arm3i_q (v3.0)** | **10** | **portfolio_analyst** | **-0.5** | **portfolio -0.5, risk +0.5** | **no** |
| **arm3i_q (v3.0)** | **15** | **portfolio_analyst** | **-1.5** | **portfolio -1.5, risk +0.5** | **no** |

**The load-bearing denominator is 3, not 7.** In the four `yes` rows the
higher-scored worker is also the incumbent, so score and incumbency point the same
way and cannot be separated. **The evidence is the 3 conflict cases, where
incumbency won 3/3.**

`portfolio_analyst` was chosen in 7 of 7, at +2.5, +2.0, +1.5, +1.5, +0.5, -0.5 and
-1.5 — but "invariant to score" and "always picks portfolio_analyst" are the same
observation in this scenario and are **not** separated by these traces.

### The cleanest single observation: v2.6, t=12

`risk_analyst` — **idle** (Batch B Robust Audit ran t=9->10; verified from
`run.json` completions, not from the manager's assertion), rendered **+1.5 with a
verified support relation** — lost to `portfolio_analyst` at **+0.5, the bare
prior**. The manager's own reasoning names both as idle. No eligibility confound, no
availability confound, and the belief pointed at the worker not chosen.

Cleaner than t=15, where the alternative carried only an untested prior.

### Collinearity: with incumbency, not with tier eligibility

Positive evidence accrues only to a worker that produced an artifact in that scope,
which in these traces means the worker the manager had already chosen. This is a
property of **this manager's routing**, not of the design — v2.6 t=12 is a direct
counterexample with two eligible workers at different scores. By-construction
collinearity would be unfixable; via-incumbency could differ under another manager.

---

## 3. Binding failure: what is established and what is not

- **2 post-flip opportunities** to route away from a `contradicted` worker (v3.0
  t=10 and t=15). Both taken. Zero declined.
- **These are the SAME EVENTS as two of §2's three conflict cases.** Distinct
  observations of routing-against-the-belief across all runs: **three** — v2.6 t=12
  (support side), v3.0 t=10 and t=15 (contradiction side). Do not add §2's 3 to §3's 2.
- **1 observation** bearing on *mechanism* (t=15). Different denominator — "two"
  must not attach to both.
- t=8 is **not** mechanism evidence: the aid rendered `supported` and the manager
  cited it accurately. **Aid defect, not consumption failure.**
- Ordering is settled in code, not inferred: `structured_manager.py:174-181` builds
  the aid (which appends the row for `t`) and only then calls `take_action`. The
  `state_history` row at `t` is what the manager was shown at `t`.
- The v2.6 cell contributes **zero** opportunities: all three Robust Audits were
  assigned by t=12, first `contradicted` render at t=14. **Work exhaustion.**
- `control_arm3i_q`, `silent_arm3i_noq`, `silent_arm3t` render **no `contradicted`
  cell at any timestep**.

**The extraction fix created the opportunities.** v2.6 detected at t=14, after the
last robust task; v3.0 at t=10, with two remaining. PREREG §5's phenomenon was
unobservable in v2.6 *by construction* — the correct disposition is neither retract
nor confirm, but "unsupported by the evidence available when written, supported by
evidence generated afterwards."

---

## 4. `noq` completion cancellation

v3.0, `portfolio_analyst` / Robust Audit, t=17: sup=0, con=3, completions=3.

```
arm3i_q   (weight 0.0):  0.5 + 0 - 3 + 0.0(3) = -2.5  contradicted
arm3i_noq (weight 1.0):  0.5 + 0 - 3 + 1.0(3) = +0.5  supported
```

The comparator got all three contradictions right, so the cancellation is entirely
the updater's: **the arm fails when the comparator succeeds**, which is what makes
quarantine load-bearing rather than incidental.

`silent_arm3i_noq` renders **zero `contradicted` cells run-wide**. This is the
arithmetic's **prediction confirmed**, not independent corroboration — one line of
evidence and its consequence.

### 4a. The quarantine is ARITHMETIC, not presentational — a limit on H2's interpretation

`COMPLETION_FIT_WEIGHT["arm3i_q"] = 0.0` removes completions from `fit_score`. But
`execution_completions` remains a **rendered column**, non-zero on **214 of 1004 rows
(21%)**, and the manager reads it: the v3.0 t=10 reasoning cites *"has completed the
Batch A Robust Audit successfully"* as its ground.

So the quarantine prevents completions from entering the **score** and does nothing to
prevent them entering the **decision**. Consequences:

- **A null `arm3i_noq` ↔ `arm3i_q` difference is consistent with a *partial*
  quarantine**, not with quarantine being ineffective — the arms differ arithmetically
  and are identical presentationally.
- **H2's ordering tests the arithmetic quarantine only.** A confirmatory result must
  not be read as testing whether the manager can be prevented from treating completion
  as competence; it cannot be, on this aid.

Precise form: *completions remain visible despite an explicit instruction not to treat
them as fit* — the Terms block states "execution evidence only, not observed quality or
fit". **"Leak silently" would be refuted by that block.**

---

## 5. Guards fixed BEFORE any confirmatory spend

1. **`arm3t` at t=10 is extraction-latency dependent.** Simulated on the v3.0
   relation stream: `arm3t` renders `contradicted` from t=10 (-0.5), t=12 (-1.0),
   t=17 (-1.25), so both openings are live. But at the *first* event
   `displacement = 0` (score initialised to prior, `arm3_belief.py:277-279`), so
   decay does not act and the value is `0.5 - 1.0 = -0.5` exactly. Ordering within a
   timestep cannot move it (`sum()` is commutative); grouping *across* timesteps can.
   **Only failure mode: the first contradiction extracted later than t=10.** More
   early contradictions make t=10 *more* robust. t=15 is robust at -1.0.
2. **See §4a — the quarantine is arithmetic, not presentational.** Elevated out of
   the guards because it constrains how H2 may be interpreted, not merely how a run
   should be read.
3. **The score-tracking test is confounded in the v3.0 trace alone** (2 of 14
   decisions informative, both `Rapid Screen`, both with a single tool-eligible
   candidate). The corpus-wide sweep in §2 is the one that answers it.

---

## 5a. Reward ceiling, and the propagation mechanism

`r_check` is a **mean over 16 tasks** (`run.py:227-238`), uncompleted scored 0.0.
`score(answer, truth) = max(0, 1 − |answer−truth|/max(|truth|,1))` (`scenario.py:893`)
is **a function of the answer alone** — `agent_id` never enters it — so substituting
a corrected answer *is* the reroute manipulation, not an approximation of it.

**The three `Method Reconciliation` tasks scoring exactly 0.0000 are not a scoring
bug.** The reconciliation task differences the robust count against the screen count.
The degraded worker ran the screening method, so it returned the screening number,
so the discrepancy the task exists to detect was erased upstream:

```
Batch B Robust Audit   71.0   truth 89.0
Batch B Rapid Screen   71.0   truth 71.0
Batch B Reconciliation  0.0   truth 18.0     |89−71| = 18
```

Reconciliation truth is *defined* as `|true robust − screen|` (verified: 5, 18, 17
against |64−59|, |89−71|, |97−80|), so a correct robust audit makes the dependent
reconciliation correct **by construction** — a tighter upper bound than the usual
optimistic kind.

**Ceiling, counting downstream propagation:**

| | r_check | delta |
|---|---:|---:|
| actual | 0.7317 | |
| robust audits only (**wrong** — first computed) | 0.7553 | +0.0236 |
| **incl. dependent reconciliations** | **0.8803** | **+0.1486** |

+0.1486 is **92.3%** of the observability-gap CI width (0.161), **71.8%** of its point
estimate (0.207), and **116.5%** of the between-aid spread (0.1275). **The reward
endpoint is not too small to measure.** One mis-routed audit costs ~2 tasks, so the
effective dilution factor is 8, not 16.

Batch A's reconciliation stays at 0.0 in the ceiling: A was assigned at t=8, pre-flip,
so a perfect belief layer would not have rerouted it.

Corrected with it: *"the perturbation is mild"* was wrong — mild on the audit metric
(0.798) and **total** on the dependent task (0.0000). A severity judgement made on the
directly-affected task and not on its dependents.

---

## 5b. A numeric detection channel exists, is computed, and is never read *by flash*

> **Scope correction 2026-07-27.** The title said *never read*. That holds for `deepseek-v4-flash`
> (**0 of 332 turns**, 11 runs) and is **false in general**: the `deepseek-v4-pro` manager cites
> reconciliation values at t=18, t=19 and t=20 — and used them as grounds for `noop`. So the channel
> is **legible and misread**, not unread. See `CONSUMPTION_BOTTLENECK.md`, model-confound section.
> The measurement below is unchanged and correct for the runs it covers.

The reconciliation artifact states the discrepancy in plain arithmetic. Two facts:

- **The comparator judges these artifacts and returns `neutral` on all of them**
  (r42/r43/r54, `requirement_artifact_consistency`). Per §1 a neutral renders
  `combined_category: supported`. The relations cite `e52/e57/e73` — the **`method:`
  lines** — while the numbers sit in `e53/e58/e74` and were never the object of a
  judgment. The method line *is* correct (`reconcile` matches a reconciliation
  requirement). **`requirement_artifact_consistency` compares a method claim to a
  requirement clause; it is structurally blind to numeric errors, by the relation
  kind's definition, not by defect.**
- **No manager turn in any run cites a reconciliation value, a zero difference, or
  matched counts — 0 of 332 turns, 11 runs.** (A loose pattern returns 108 hits, all
  scheduling; the tightened pattern returns zero.)

So there are two detection opportunities per batch: the audit's **method line**
(caught in 2 of 8 runs) and the reconciliation's **number** (never). The channel that
is ignored is the unambiguous one.

---

## 5c. Unaided detection: base rate, and one airtight consumption failure

**Exposure denominator** — manager turns at which a degraded robust-audit artifact
already existed. Built by rejecting two wrong denominators first: 41 turns naming the
screening method (most legitimate — `mean+2*SD` *is* the screening standard), then 19
near a robust-audit reference (17 of which are **pre-completion routing talk**, with
nothing yet to flag).

```
run                     1st bad   exposed turns   flags
silent_append_only          10          14          0
silent_arm3i_noq             9          23          1
silent_arm3i_q  (v2.6)       9          23          1
silent_arm3t                 9          23          0
silent_atomic_ledger         9          23          0
silent_generic_summary       9          18          0
silent (no aid)              9          23          0
silent_arm3i_q  (v3.0)       9          23          0
                                       170          2
```

**Quote 2 of 8 runs (~25%), not 2 of 170 turns (1.18%)** _[figures in this section are as-measured
on the runs then available; the current corpus-wide figure is **3 of 12 silent runs** — see
`CONSUMPTION_BOTTLENECK.md` "Articulation, measured". The rate is unchanged at ~25%.]_ — turns are not independent,
since a manager that flags at t=10 has changed its own context for t=11.

**Limitation, unavoidable rather than fixable:** the eight runs differ in aid
condition, so pooling assumes the aid does not affect articulation — the very thing a
reader would want tested. At 8 runs and 2 events no stratification is possible. 2/8 is
the best available **and cannot distinguish aid conditions.** Slicing it 2/4 aided
against 0/4 unaided would be manufacturing a finding.

**Detection-side finding:** the manager fails to articulate a plainly-stated wrong
method in ~3 runs out of 4, and non-articulation occurs in **every** aid condition —
including aid-free, temporal, atomic-ledger and append-only.

**`silent_arm3i_noq` t=10 — the one airtight consumption failure.** The manager wrote,
unprompted, from raw artifact text:

> *"the artifact shows it used the mean-plus-two-SD method instead of the intended
> 95th-percentile method. This could corrupt the reconciliation and prioritization
> downstream."*

— correctly naming the method **and predicting the propagation mechanism of §5a.** The
aid at that timestep:

```
t=10  portfolio_analyst  comp=1 sup=0 con=1  score=+0.5  supported
      risk_analyst       comp=0 sup=0 con=0  score=+0.5  supported
```

`0.5 + 0 − 1 + 1.0(1) = +0.5`. The contradiction is **rendered** (`contradicts=1`);
the aggregate says `supported`. So the manager held three things — its own correct
written diagnosis, the aid's evidence column showing a contradiction, and the aid's
aggregate — **and followed the aggregate over both.** Third independent appearance of
the aggregate-versus-component structure, and the only one overriding a correct
diagnosis the manager had already produced.

`risk_analyst` was assigned **once**, at t=3, and was idle from t=5 to the end —
robust-tier, rendered `+0.5`, unoccupied. The manager then assigned **two further
robust audits to the diagnosed worker**, t=13 and t=15. These are fresh assignments,
not retries, so no affordance is required to have chosen otherwise.

**n=1, and the base rate says n=1 is what eight runs should produce.** Not to be
stated as a property of the unquarantined arm.

**Withdrawn:** *"the arms fail differently."* v3.0's zero flags in 23 exposed turns has
probability ≈0.76 at the observed base rate — the modal outcome. Its silence is
evidence of nothing. Also withdrawn: `silent_arm3i_q` t=20 as a consumption failure —
detection came after all three robust audits were assigned. Work exhaustion.

`inspect_task` returns **metadata and a resource ID, not artifact content**, so it
could not inform the decision — but the manager already had the content, which is
where it detected the mismatch.

---

## 5d. Same-cell re-run (authorised spend, 120 calls)

`silent_arm3i_q`, seed 101, v3.0, `reasoning` NOT wired in, `extractor_config`
asserted `a4ba33dab82b` before launch. Both runs preserved under
`records/preserved_outputs/v3.0_silent_arm3i_q_seed101` and
`records/preserved_outputs/v3.0_noisefloor_r2`.

```
run 1   r_check 0.7317   16/16   0 failed   60 relations
run 2   r_check 0.8206   16/16   0 failed   55 relations
|Δ|             0.0889
```

**Thirteen of sixteen tasks bit-identical.** The three that differ all trace to one
assignment — Batch C Robust Audit went to `risk_analyst` at t=11 and returned **97
against truth 97**:

```
Batch C Robust Audit           0.8247 -> 1.0000   +0.1753
Batch C Method Reconciliation  0.0000 -> 1.0000   +1.0000
Plan Manual Review Capacity    0.6629 -> 0.9101   +0.2472
```

**The propagation mechanism of §5a is now directly observed, not inferred.**

**It is NOT a belief-driven reroute.** At t=11 `portfolio_analyst` was busy running
Batch B; the reasoning reads *"start the remaining robust audit now **while the
running Batch B Robust Audit completes**. Risk_analyst is **idle** and capable."* The
`−0.5 contradicted` rendering is never mentioned. **Routing invariance survives.**

**The pre-committed noise bands do not apply.** They assume a stochastic error term;
here the remainder is bit-identical and the difference has one identified cause. The
correct statement: *two identical-configuration runs differed by 0.0889, entirely
from a single routing decision that differed for throughput reasons* — i.e. **the
endpoint is sensitive to precisely the variable under study.** One draw, not a
variance estimate.

**Byproducts:** articulation none (**2 of 9 runs**); **binding replication confirmed**
— Batch B assigned to `portfolio_analyst` at t=10 with the aid at `−0.5 contradicted`,
taking that observation to **n=2**; Batch A's contradiction lands at **t=10** in both
runs, with only two contradictions in run 2 because C was done correctly; A and B
reconciliation zeros reproduce, C is 1.0000.

**Ceiling undercounted a third time.** `Plan Manual Review Capacity` also consumes the
robust-audit artifact, so **one reroute moves three tasks, not two**. Measured
single-reroute effect **+0.0889**; projected both-reroutes ceiling **+0.1640** against
the earlier +0.1486.

**Call count is measured, not reconciled to the plan** — `draws_by_judgment_kind`,
`samples_per_judgment = 1`, `structural_neutrals_no_call = 0`:

```
run 1   manager 32 + workers 16 + comparator 88 = 136
run 2   manager 23 + workers 16 + comparator 81 = 120
```

**The same routing decision produced both the reward difference and the 16-call
difference** — the reroute ended the episode in 23 turns instead of 32. **Call count
is not a per-cell constant**; it is behaviour-dependent, and asymmetric: faster runs
cost less, stalled runs cost more. Zero failures in every class across 169 comparator
draws.

### Harness defect — blocks the confirmatory matrix

A first launch produced `r_check = 0.000` with **all 32 manager turns
`failed_action`** and **exit code 0**. Cause was environmental (`uv run` rebuilt
`.venv`, dropping the `agents` and `openai` dependency groups); zero API calls were
spent, the failure being a local import before any HTTP request.

**A totally failed run is indistinguishable from a successful one to anything checking
exit status, and its all-zeros output lands in `outputs/`, which every sweep globs.**
At matrix scale one silently failed cell in fifty would spend its calls and corrupt
the `r_check` spread, the articulation denominator and the contradicted-cell sweep,
invisibly. Guard: exit nonzero when zero manager actions succeed. Shared harness code,
so it needs a `CHANGED.md` entry. **Not authorised, not made.**

---

## 6. Procedural finding

Nine instances this session of *a query whose unit, vocabulary or scope did not match
the claim it was answering*, each returning a clean negative that looked like an
answer: truncated key; single-format regex; pooled denominator; wrong-timestep `con`;
per-worker vs per-scope; a field name absent from the schema (`declared_fit` is not a
row field — `profile_prior` is); free-text substring vs structured `assignee`;
eligibility applied per-case but not to the pooled aggregate; and **a search scoped to
one polarity of a two-polarity claim** (a contradiction-scoped sweep could not see the
support-side instance at v2.6 t=12).

Rules adopted:

- Assert a key exists before reading its values — a uniform `None` from `.get()` is
  not evidence of a null field.
- Match on the field that carries the claim, never on a serialisation that happens to
  contain the word.
- Re-run an eligibility check at **every level the claim is aggregated to**; a
  denominator valid per-case is not automatically valid pooled.
- Report the number that carries the claim, with its denominator named.
- **One rule, two domains** — the eligibility rule applies to observations as well as
  actions, and both fail identically when the denominator is "how often the topic came
  up" rather than "how often the answer was there to be had":
  - *actions* — a delay is only a failure if action was available and the agent eligible
  - *observations* — a non-detection is only a failure if the signal was already present
- Check whether two reported denominators **intersect** before a reader can add them.
- **When a check is adopted mid-investigation, sweep the prior record with it** — a
  conclusion that predates a check will never be flagged by it. This caught the
  widest error here and is a fifth detection mechanism alongside the four already
  catalogued.

---

## 7. Open, unauthorised, and named with cost

- Affirmation floor **0.582**, measured on 12 match items **before the determinability
  standard existed**. Its denominator has never been audited against the standard that
  would exclude items from it. Free to do; largest unswept item.
- Whether `supported` carrying no evidential content invalidates interpretations that
  assumed it did — a re-audit of conclusions, not figures.
- A scenario where the incumbent is **not** the tier-natural choice would separate
  "invariant to score" from "always picks the incumbent". **Does not exist in any
  trace; manufacturing it is a scenario change, not a read.**
- Making the positive comparison strict would move `combined_category` on 78.1% of
  rows — a different rendering, not a threshold tweak, and §5.3 freezes thresholds.
  A preregistration change.
- **Pending spends are recorded in `RISKS_AND_DIRECTIONS.md` §0, not here**: the
  corpus measurement, the `silent_arm3t` trace with `reasoning` wired in, and the
  `declared_fit` ablation — which §1 shows is weaker than scoped, since
  `combined_category` still reads `supported` from the prior on 78.1% of rows.
