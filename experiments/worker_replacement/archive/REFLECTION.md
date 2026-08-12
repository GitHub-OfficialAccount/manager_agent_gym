# Reflection: why the direction was challenged, and where it left us

_Written 2026-07-28 at the researcher's request. Covers the period from the first challenge to the
tool-change framing through to the conclusion that the AHT mechanism needs a revamp faithful to the Manager
Agent formulation. **Supersedes `RETHINK.md`, which is deleted** — its five-item redesign was overtaken by
measurement. Detailed traces live in `BRAINSTORM.md` §7–34 and `CONSUMPTION_BOTTLENECK.md`._

**Reading rule for this document: every number is measured and cited to a condition. Anything not measured is
marked as a hypothesis. Claims that were withdrawn are listed in §8 rather than quietly dropped.**

---

## 1. What we were doing, and why it stopped

**The direction was a belief layer**: extract requirement–artifact relations, aggregate them per
(worker × task-scope), render the result to the manager, and expect rerouting. Seven arms —
`native`, `summary`, `summary_log`, `ledger`, `arm3i_noq`, `arm3i_q`, `arm3t` — all null.

**The researcher's challenge:** the study only detects a *tool* change, which is too restricted to be
meaningful, and may not scale to behaviour change.

**It was correct, and worse than stated.** The artifact prints its own method:

```
method: reference mean-plus-two-standard-deviation (z-score) outlier detection
```

**81% of degraded-worker robust audits (71 of 88, silent family) name the actual method accurately.** So
detection is a string comparison against the task requirement — **there is no latent variable to infer, which
is why every format of belief layer was inert.** A belief layer infers a hidden state; the state was printed.

---

## 2. The aid was also broken, and that had to be cleared before anything could be concluded

Extracting the verbatim manager prompt exposed defects nobody had looked for:

| **all 9 relation IDs the aid cited were dangling** | `[r34]` and eight others each appear **exactly once** in the 30,543-char prompt — in the row citing them. The ledger holds `e`-prefixed evidence IDs; the aid emitted `r`-prefixed relation IDs. **The manager could not check the claim it was asked to reroute on** |
|---|---|
| the two facts were never adjacent | requirement at char **11,706**, delivered method at **20,138** — 8,432 apart, different sections |
| the schema forbade stating the fact | `ManagerFacingWorkerState` had `extra="forbid"` and every evidence field was a list of IDs. **No rendering could print a fact** |
| 7 of 8 rows were identical boilerplate | and `declared_fit` read `supported` in **8 of 8**, including the row saying the opposite |

**Consequence: the seven-arm null could not be attributed to the manager until the aid was fixed.** That is
why the next five runs happened.

---

## 3. Five interventions, and the one variable that separates them

Each fixed a defect and asked whether routing changed. **The `silent` baseline is `r_check` 0.732–0.859, with
the first robust audit going to the degraded worker in 37 of 37 runs across 10 seeds.**

| wrote to | intervention | what it said | `r_check` | routing |
|---|---|---|---|---|
| observation aid | `prose` | *"These do not match"* — plain, verifiable, adjacent | **0.7317** | unchanged |
| observation aid | `prose_nocost` | + *"rerouting does not delay the workflow"* (verified true) | **0.7317** | unchanged |
| observation aid | `prose_capability` | *"NOT currently qualified: 0 conforming artifacts"* | **0.7317** | unchanged |
| observation aid | `prose_event` | a derived change **event** from the worker's own artifacts | **0.7317** | **instrument never fired** |
| manager model | `deepseek-v4-pro` | — | **0.7317** | unchanged, and **worse** than flash |
| **agent capability metadata** | **`silent_declared`** | declaration revised, **nothing announced** | **0.879–0.888** | **3 of 3 correct** |
| agent capability metadata | `silent_false_declared` | a **false** `99th-percentile` declaration | **0.7317** | reverts |

> **Informing the manager never worked. Writing to the field its assignments correlate with did — 3 of 3
> against 0 of 37, seed-matched.**

_No p-value quoted: Fisher exact would assume 40 independent
observations, and the 37 are runs across 10 seeds and several arms on ONE scenario, so same-seed runs are not
independent. The contrast carries the claim without it._

**And it is coarse.** A declaration that is *false but names the right method family* passes: the manager wrote
*"Batch A Robust Audit uses **95th-percentile** outlier screening, which **matches** portfolio_analyst's
capabilities"* while the declaration read **99th-percentile**. **The match is keyed on a method family and is
blind to the parameter inside it.** Whether that is lexical overlap or family-level semantics is
**undetermined** — the discriminating test is specified in `BRAINSTORM.md` §30b and unbuilt.

**Two things this revised:**

- **`full` vs `silent` confounds two variables.** `capability_projection` and `announce` move together in all
  four original conditions. Measured at t=8: under `full` the worker declares `mean-plus-two-SD` and **no
  percentile**; under `silent` it still declares percentile. **So the headline "observability gap" is
  substantially a capability-declaration effect**, and *"observability"* is the wrong construct name for what
  the conditions vary.
- **"The gate" is a bad name.** `AssignTaskAction.execute` validates only that the task and agent exist.
  **Nothing enforces capability eligibility.** What is measured is a **strong, reproducible, leaky, coarse
  preference** — `full` is 11 of 13; `silent_declared` routes 2 of 3 per run.

---

## 4. The disclosure trilemma, closed on all three horns by measurement

The researcher's framing: axis 2's setup is *too easy if faithful and correct*, *meaningless if unfaithful*,
and *collapses to drift detection if faithful and wrong*.

| horn | status |
|---|---|
| **faithful and correct** | **81%** of artifacts. Detection is string comparison. **Too easy — confirmed** |
| **unfaithful** (suppress the method) | `--artifact-reporting no_method` exists, **never run**, and **withdrawn as a direction**: a faithful worker reports its method, so hiding it manufactures the problem |
| **faithful and wrong** | **18%** (16 of 88). Proposed as the escape and **closed by frequency, not by collapse** — an 18% behaviour cannot be the setting, and forcing it up means engineering the worker into misdescribing itself, which is horn two |

**The faithful-and-wrong artifacts are real and endogenous** — *"zscore (reference mean+2\*SD robust
95th-percentile-**EQUIVALENT** cutoffs)"* — the worker has mean+2·SD tools and a percentile instruction and
reconciles them by asserting equivalence. **We did not engineer that.** But at 18% it is **noise on an
otherwise clean confession**, not a barrier to detection.

**The correction-transfer test built to probe it failed on its own premise:** Batch A's method line was
already accurate, so the injected correction asserted something false. **Two defects, both ours** — injected
unconditionally into a stochastic premise, and it asked for reporting fidelity rather than method compliance.

---

## 5. Why every formulation collapsed, and it is not about the lever

**Two structural causes, in order of depth.**

**(a) Substitutes make adaptation a lookup.** `portfolio_analyst` and `risk_analyst` hold **identical
capability lists**. So *"adapt to the teammate"* reduces to *detect → swap*, and **detection becomes the
entire problem** — which is monitoring with a reflex attached. **We guaranteed that before any experiment ran.**

**(b) Deeper: delegation is not coordination.** `ManagerAgent.pdf` §3.3 gives the manager
observability-increasing, graph-modifying and delegation actions. **It never acts in the workers' space.** So
it cannot act in the workers' space — **and the one route by which it could complement them,
restructuring the work, it never used** (`decompose_task`, 0 of 966). _Weakened on the reviewer's objection:
shaping the work IS a form of complementing, so the original phrasing contradicted §9's identification of
that route as the open question._ Classical AHT is non-collapsing
because the ego agent **cannot replace its teammate** and must change its own policy; remove substitutes here
and you still have `assign → receive → evaluate`, which is supervision, and **supervision under uncertainty is
monitoring.**

> **MAG §4.3 calls it "Coordination in Ad Hoc Teams" but what it describes — infer capabilities, then delegate
> accordingly — has a different structure from PLASTIC, AATEAM, ODITS or ConvCPD, all of which concern an agent
> adjusting its own policy in a shared action space. The term is imported.** That import is what kept pulling
> the work toward drift detection, because drift detection is what the structure supports.

---

## 6. What actually characterises the problem — measured

**Grounded in 966 manager actions across 34 silent episodes.**

**Observation side:**

```
per episode:  16.0 artifacts
               3.0 robust audits   <- observations bearing on the changed capability
```

- **Products, not behaviour.** Every axis-2 mechanism reads an action stream; a manager reads a finished
  artifact. The inference is **policy-from-output**.
- **Sparse.** Three observations, not a stream. **Few-shot inference from rich sparse observations**, where
  classical AHT is online inference from thin dense ones.

**Two consequences that retro-explain the project:**

1. **The belief machinery had no problem to solve.** Accumulation, decay, posterior responsiveness —
   Albrecht's additive-vs-multiplicative distinction, `arm3t`'s recency weighting — **are all machinery for
   dense streams. With three observations there is nothing to accumulate.** Better than *"the manager ignores
   it."*
2. **Drift metrics are structurally inapplicable, not competing.** Rath's ASI (`papers/Agent Drift.pdf`) needs
   **rolling 50-interaction windows, three consecutive below threshold**; a manager gets **three
   CAPABILITY-RELEVANT observations** per episode (16 artifacts, ~28 actions in total). _Stated in that unit
   on the reviewer's objection: the paper does not say whether its windows count agent interactions or
   capability-relevant ones, so 3-against-50 is defensible only on the latter reading._ **Sparsity also forces detection to be decidable on one observation — an invariant violation
   is, a rate is not.**

**Response side:**

```
966 actions:  assign_task 58.2% · noop 12.7% · get_available_agents 9.3% · inspect_task 8.6%
              graph-modifying 2.5% total  ·  decompose_task 0.0%
```

**"Enabled to respond" splits in two, and the data separates them:** the manager **has** the action
(`DecomposeTaskAction`, unused in 966) but **lacks the input that triggers one** — the only field its
assignments respond to is **capability metadata it cannot write.**

> **AHT in a manager agent: few-shot inference of a teammate's changed capability from sparse finished
> products, responded to by restructuring work rather than changing one's own policy, conditioned on metadata
> the manager does not author.**

---

## 7. What the schema records — verified by reading the code

```
TaskStatus = PENDING | READY | RUNNING | COMPLETED | FAILED | UNKNOWN
```

**There is no state for "completed but non-conforming."** A wrong-method artifact is `COMPLETED`, and
`RetryTaskAction` requires `FAILED` — so the affordance gap hit repeatedly is a **type-system** gap, not a
scenario defect.

**Conformance does have a slot in the state.** `Task` is in the graph **G**, and:

```
Task.quality_score:     float | None   "Quality assessment [0,1]"                  tasks.py:80
Task.effective_status:  str   | None   "Derived, reporting-only composite status"   tasks.py:92
acceptance_criteria:    str            "Specific, measurable criteria to verify completion"
```

**Every line below was verified against the code:**

| `quality_score` | **never computed or set during execution.** Its only writers are two restore paths (`engine.py:243`, `state_restorer.py:88`) and one that sets it to `None` (`manager_actions.py:257`) |
|---|---|
| `quality_score` | **never rendered to the manager** — no occurrence in any observation, prompt or summary path |
| `effective_status` | **is** computed, but from `node.status.value` (`engine.py:896-903`), so it **inherits the enum's gap** and adds no conformance information |
| `acceptance_criteria` | states what conformance *would* mean and provides **nowhere to record whether it was met** |
| `TaskStatus.FAILED` | set in **exactly two places** — `engine.py:722` (an unsuccessful execution result) and `:746` (a caught exception). **Nothing can mark a task non-conforming after a successful completion** |
| conformance validator | **does not exist** — zero matches anywhere in `core/` |

> **The state provides a slot for conformance and the implementation leaves it empty and unrendered.**

**Tasks reach the manager as identifiers only.** `ManagerObservation` carries five task fields, all
`list[UUID]`. So a field on `Task` **does not ride along**, and filling `quality_score` changes nothing
observable until something carries it.

> **ANNOTATION 2026-07-29 (BRAINSTORM §79–80): the paragraph above is false as stated, and the specific
> false step is this.** `ManagerObservation.workflow_summary` is `workflow.pretty_print()`, which renders
> every task's name, status and description AND a 300-char content preview of every artifact — including the
> workers' `metric:` and `method:` lines (92% of 1,170 artifacts; verified in 30/32 manager prompts of a real
> run) — into the manager's prompt each timestep. The ID-list fields are IDs; the summary field is not.
> **What survives, narrowed:** `quality_score` and `effective_status` specifically do not ride along, because
> `Task.pretty_print` does not render them — so the carrying gap is real for exactly the fields pretty_print
> omits, and the remedy row below ("requires a new `ManagerObservation` field") is wrong: a one-line
> `Task.pretty_print` addition would carry them, since the summary already flows to the prompt. Downstream:
> the §8 reading of `q` t=20 ("the manager reached for `inspect_task` and got a pointer") described a manager
> that already had the audit metric in ambient view; what Inspect denied it was nothing the summary had not
> already shown.

**That makes two gaps, not one, and each needs a different remedy:**

| gap | what is missing | remedy |
|---|---|---|
| **filling** | `quality_score` is never written during execution | a few lines in the recorder — **but written from `truth` it is an ORACLE**, so this cannot be the manager-visible path |
| **carrying** | nothing conveys task attributes into the observation | **requires a new `ManagerObservation` field and a `_prepare_context` change.** Not a schema addition to `Task` |
| **affordance** | no action exists for completed-but-wrong | `retry_task` requires `FAILED`, and no status expresses non-conformance. **Needs a status value or an alternative action route** |

**The enum observation belongs to the third gap**, which is why it survives independently of the quality slot
existing.

---

## 8. The state-predicate account — and why two independent lines converge on it

**§7 was derived by reading the code: enum values, field writers, render paths. What follows was derived by
comparing seven interventions: which channels moved routing. Different methods, different evidence, arrived at
separately — and they meet.** That convergence is the argument of this section; neither line alone would
support it.

**Start with the comparison.** Laying the seven conditions of §3 on structure × entity-indexing:

| | **prose** | **typed field** |
|---|---|---|
| **worker-indexed** | `prose_capability` — *"NOT currently qualified"* → **0.7317 FAIL** | `silent_declared` → **0.879–0.888 WORK** |
| **task-indexed** | `prose`, `prose_nocost`, `prose_event`, `ledger`, `summary` → **0.7317 FAIL** | **EMPTY** |

**Two candidate accounts, both refuted.** *Entity indexing* fails because `prose_capability` was
worker-indexed **and** pre-aggregated to exactly the worker-level fitness conclusion, and produced the floor.
*Structure* fails for a reason found by inspecting the schema rather than the results: **there are four typed
per-entity channels, and two of them are flattened into prose before the manager sees them.**

```
available_agent_metadata  list[AgentConfig]              read at the ASSIGNMENT DECISION
recent_messages           list[Message]        ->  interpolated as a text block  structured_manager.py:274,366
constraints               list[Constraint]     ->  interpolated as a text block  structured_manager.py:250,366
stakeholder_profile       StakeholderPublicProfile
```

**So "typed" was never the axis.** Everything except `AgentConfig` arrives in the prompt as text regardless of
its schema type, and two typed channels are therefore **as inert as the aids by construction.** The `typed`
column of that 2×2 contains exactly one channel that behaves differently from prose, and its distinguishing
property is not its type.

**What distinguishes it is that something reads it at a decision point.** The same pattern sorts the actions:

```
assign_task     triggered by a STATE PREDICATE -- a task is READY            used
retry_task      triggered by a STATE PREDICATE -- status is FAILED           never fires (never FAILED)
decompose_task  requires an UNPROMPTED JUDGMENT                              0 of 966
```

> **The operative variable is whether information is WIRED INTO A DECISION PROCEDURE or merely PRESENT in
> context.** `AgentConfig` is not special for being typed or for being worker-indexed — it is **read at the
> point of the assignment decision.** Prose is read by nothing.

**The account is confirmed on a single action, in both directions, for free — and the refusing case was
OBSERVED rather than inferred.** `retry_task` appears **38 times across 16 runs** in the corpus:

| predicate **holds** (task genuinely `FAILED`) | **37 uses, all `success=True`.** Mostly stakeholder tasks; three name `screening_analyst` or `risk_analyst` |
|---|---|
| predicate **fails** (wrong-method artifact at `COMPLETED`) | **1 attempt, refused by the environment** — `amendment_fav` t=11, with the engine's text *"has status completed; only failed tasks can be retried"* reaching the manager at t=12 and after |

**The refused attempt is the important one, and it is not a null result.** The manager **diagnosed the defect,
named the correct remedy, and reasoned about downstream damage**: *"incorrectly used mean+2SD method (rapid
screen) instead of the required 95th percentile robust audit… Retrying with risk_analyst… will correct this
error before reconciliation tasks depend on it."* **Belief formed, correct action selected, environment
refused.** So the affordance gap is **an observed event with a reasoning trace**, not a deduction from the enum
— and **at least one arm-3 null is attributable to the refusal rather than to non-consumption.** (Recorded
2026-07-27; `manager_actions.json` logged only `null`, which is why the first reading of that run drew the
wrong inference — see `CHANGED.md`.)

**And the account must be pinned before it is tested, or it is unfalsifiable.** `inspect_task` (169 uses) and
`get_available_agents` (282) invite a post-hoc predicate for anything — *"a task is RUNNING"*, *"agents may be
free"* — and once any state fact can be named as a trigger, **nothing could fail the account.**

> **Definition, fixed in advance: a predicate is TRIGGERING iff THE ACTION'S OWN PRECONDITION REFERENCES IT.**
> `retry_task` requires `FAILED`; `assign_task` requires `READY`. `inspect_task` and `get_available_agents`
> have **no preconditions** and are therefore **outside the account's scope by construction**, not by
> exception.

**The cost of that definition is a data point we were using, and it should be paid.** `decompose_task` has no
precondition either, **so the account predicts nothing about it and its 0 of 966 is no longer evidence for
it** — it returns to being an open question. **Better to lose the data point than to keep it by a construal
that makes the claim untestable.**

**Two falsifiers, stated on reachability rather than on routing:**

| **the account is WRONG if** | a state predicate exists, an action is conditioned on it, and **the manager still does not use that action** — what the coupled experiment tests |
|---|---|
| **the account is WRONG if** | a **purely present** channel moves behaviour — five prose channels have failed to |

_Routing is a step beyond reachability: in the coupled experiment the manager might retry rather than reroute,
which would confirm the account while leaving `r_check` unchanged. The falsifier must be about which actions
become reachable._

**Scope of the claim, stated in it: precondition-gated actions, one scenario, one manager model.**

**This explains all seven conditions and why six channels of better information changed nothing** — and it reframes §3's *"informing never worked; writing to the field its assignments
correlate with did"* from a quirk of the manager's attention into a property of the interface.

**Here is where the two lines meet, and it is a schema fact doing work in the design argument.** A tool error
**does not fail the task** — the agent catches it and reports, which is **the same mechanism by which the
wrong-method artifact completes in the first place.** So the non-conformance we are trying to detect and the
absence of a state predicate for it **have one cause.** That is not a coincidence between two findings; it is
one fact visible from both directions.

**Which is why the empty cell cannot be filled cheaply.** Every typed, task-scoped candidate fails a
requirement: `quality_score` is unrendered (the carrying gap); `effective_status` inherits the enum gap;
`acceptance_criteria` is set before execution and carries no verdict; artifact content is task-scoped and
rendered but its channel is **prose**, which is the *failed* cell rather than the empty one. **There is no
typed, task-scoped, manager-rendered conformance carrier.**

> **The gap in the design space and the gap in the state space are THE SAME GAP.** The 2×2's empty cell is not
> missing experiment coverage — **it is §7's finding showing up as one.**

**So the core plumbing change buys IDENTIFICATION, not one more data point.** Absent it, the strongest
available statement stays *"wired versus present"* **with the alternative never having been testable.** The
experiment it implies is **one** experiment: populate a conformance field **and** condition an action on it —
`retry_task` accepting a `COMPLETED` task below threshold. A null there is **far heavier** than the four aid
nulls, because the manager would have a state fact *and* an action enabled by it, removing both explanations
we have alternated between.

**One defect that must be fixed before it is built.** The recorder computes quality from `truth`, so gating an
action on it makes the environment **light up the answer** — testing whether the manager pulls a lit lever,
not whether it adapts. **The oracle-free writer is the comparator our belief layer already contains**: the
artifact prints its method, the requirement states it, no ground truth needed. **That moves the same
computation from the prose channel into the state, which is the variable under test rather than a confound in
it.** _The oracle objection is what produced this version of the design._

**A measurement channel that is not an observation channel.** Tool calls are fully attributable on the
existing corpus — `events` carries 89 with name, arguments, output and `actor_id`. But **no tool-call data
appears in `ManagerObservation` at all** (zero matches), so this is an **instrument for us**, not a channel the
manager could use; rendering it would be another instance of the carrying gap.

**Two things it produced, and only one survived.** The degraded worker's tool *selection* changes at the swap —
but the perturbation **is** a toolset swap, so that is close to a readout of the injected change rather than an
inferred behavioural signal, and it is kept only as a ground-truth-free detector baseline. **A within-worker
call-volume signal was found and then withdrawn:** `screening_analyst` made 36% fewer calls on a
byte-identical task set with an untouched toolset, which looked like propagation until the matched-cell
distribution was computed —

```
>=20% change on matched task sets:   screening_analyst 6 of 7 cells     audit_coordinator 5 of 6
screening_analyst deltas: -7 -5 -5 -3 -3 +1 +3        (two INCREASES)
audit_coordinator deltas: +1 +11 +13 +14 +14 +14      (roughly doubling)
```

**Both workers move in most cells and the downstream one moves harder.** The original reading came from the one
cell where `audit_coordinator` happens not to move. **Withdrawn as variance.**

**What survived is smaller and independent of the volume claim: the DAG does not bound what a worker sees.**
`screening_analyst` reached `Batch C Robust Audit` — the degraded worker's artifact, **outside its declared
dependencies** (`scenario.py:340`, screen tasks depend on `calibration_review` only) — via
`list_audit_artifacts` → `read_audit_artifact`, substituting it for four of its five `portfolio_profile` calls.
**It did not do less; it did something different.** Relevant to any future propagation claim, and invisible
without argument-level data.

## 9. Claims withdrawn during this period

**Recorded because the record is only useful if the retractions are in it.**

| claim | why it fell |
|---|---|
| *"structure is the operative variable — typed fields beat prose"* | **mine.** Four typed per-entity channels exist and **two are flattened into prose** before the manager sees them (`structured_manager.py:250,274,366`). `AgentConfig` is not distinguished by its type. §8 |
| *"entity indexing is the operative variable — worker-indexed beats task-indexed"* | **the reviewer's.** `prose_capability` was worker-indexed **and** pre-aggregated to the fitness conclusion, and produced the floor. §8 |
| *"the fix is a status value or a conformance field on X"* | a formalism change proposed before checking that the state already had the slot. The carrying gap, not the schema, is the obstacle. §7 |
| *"`tool_calls.json` records arguments only — drift measurement is blocked"* | the data was never lost. `events` carries all 89 calls with arguments, output and `actor_id`; **no re-run needed** |
| *"shape 1 (make reconciliation FAIL) is implementable without plumbing"* | `FAILED` is set only from an execution error or a caught exception, and **no conformance validator exists** |
| *"work quality is in R_M and not in S; unobservable by construction"* | **false — the strongest sentence in the document.** `Task.quality_score` is a field on `Task`, which is in **G**. The true claim is narrower: **the slot exists, is never written and is never rendered.** Corrected inline in §7 |
| *"the null survives with every known presentation defect removed"* | the amendment fixed four presentation choices and left the two largest, which were unknown then |
| *"the aid at 93.6% depth is a defect"* | the aid is the **last** substantive block, which is a strong position. The real problem was 72% of the aid block being ledger JSON before the readable table |
| *"pro detected the anomaly and engineered around it"* | registering that three values are **equal** is not registering that they are **impossible**; absence check clean across all 24 turns |
| *"a stated preference: throughput over correctness, acted on consistently"* | **n=1** explicit trade with **one counter-instance** |
| *"the manager reads completion as evidence of capability"* | too broad — completion is neither necessary (t=8, `completion_evidence_ids=[]`) nor scope-transferable (`screening_analyst` 56 completions / 0 robust audits) |
| *"orchestrators string-match capability text"* | *"orchestrators"* → **this manager**; and *"string-match"* → **coarse-token match, lexical-vs-semantic undetermined** |
| *"our negatives are evidence against Rath's drift-aware routing"* | **category error.** Every one signalled a *tool change*; his mitigation targets *endogenous drift*. And routing *did* respond, via metadata |
| *"the graph is missing a check"* | it is not — reconciliation is a perfect discriminator whose **success and failure signatures are swapped** |
| **manager-as-experimenter** | _the empirical leg of this rejection is **FALSIFIED**; the cost and confidence-versus-doubt legs stand._ The **0 of 33** was **33 of 169** `inspect_task` turns, an unstated and non-random fifth. Over the full 169 there are **4 inspections in 3 runs** driven by a suspected method or capability defect, two naming capability explicitly: *"the portfolio_analyst broadcasted a method change to mean-plus-two-SD, **which may indicate a capability shift**"* (`full_t3_seed43` t=17) and *"determine if this is a data issue, **agent capability mismatch**, or transient error"* (`control_t3_seed43` t=10). **The manager does express competence doubt and does inspect to discriminate hypotheses — 4 of 169 (2.4%), 3 of 41 runs.** See `BRAINSTORM.md` §20a |
| **capability decay** | decay is symmetric and the alternative is idle, so it would favour the *active* degraded worker |
| **`no_method` as a direction** | a faithful worker reports its method; hiding it manufactures the problem |

**And one process failure worth keeping:** applying `description_override` on the `current` projection
silently redefined `full` (13 existing runs) and `silent_declared` (3) — **same condition name, different
intervention**, committed an hour after documenting the previous instance of that class. Caught within the
hour; `revise_description` is now a condition flag.

**Nine measurement errors between two people in one evening.** The two general rules worth carrying:
**a filter keyed on an artifact only the treated arm produces silently deletes the comparison arm**, and
**a check evaluated over a union is satisfied by any member, so a per-member failure is invisible.**

---

## 10. What survives, and what it is worth

**Measured and unclaimed elsewhere:**

- **The channel finding.** Four informational interventions failed; writing to capability metadata moved
  routing 3/3 against 0/37. **Where a signal is written matters more than what it says.**
- **The coarse-family match.** A false-but-plausible declaration naming the right family passes — **worse than
  a stale agent card, because a card can be precise and wrong.**
- **A confound in the project's own anchor comparison**, and the construct-name correction that follows.
- **Corrupt success inside an orchestrator's observation stream** — the self-overwrite, a wrong-method artifact
  cited as proof of competence, across 3 runs and 2 models. Cao and Advani grade from outside; nobody has
  placed it inside a monitoring agent.
- **The conformance slot is empty.** `Task.quality_score` exists, is **never written during execution and
  never rendered to the manager** — so every belief layer we built was representing a proposition the
  environment **had a field for and never filled**. §7.
- **The state-predicate account, and the fact that two independent lines reach it.** Reading the schema and
  comparing seven interventions were separate exercises that converge: **information the manager acts on is
  wired into a decision procedure; information merely present in context is inert, whatever its type.** §8.
  **This is the one item on this list that is mechanism-shaped rather than diagnostic** — and it is the only
  one that predicts the direction of a future intervention instead of describing a past one.
- **`METHODOLOGY_FINDINGS.md`** — the 18-instance mismatch family — independent of the science and probably
  the most transferable material here.

**The honest problem: every item is diagnostic rather than mechanistic.** The one intervention that moved
routing works for a shallow reason, and the five that failed are informative rather than useful.

**The cheapest unanswered question:** `decompose_task` is **0 of 966**. If the manager cannot conceive of
restructuring work as an adaptation, that is a mechanism-shaped finding about orchestrators. If our scenario
simply never demanded it, that is our design. **The corpus cannot distinguish them.** **And since §5 was
weakened, this is no longer a loose end — it is the direct test of §5's revised claim:** §5 used to say
complementing was structurally unavailable, and now says the route existed and went unused, which is only a
finding if the scenario ever called for it.
