# The consumption bottleneck: one finding across arms 1–3

_2026-07-27. All figures measured at **one scenario, one seed (101)**, from
`records/preserved_outputs/`. Nothing here is a rate over a population. The confirmatory matrix is
out by the researcher's decision, so arm 3 concludes development-grade._

> **Provenance note added 2026-07-27.** The label **`v2.6`** is **ambiguous** and must not be used as a
> run identifier. Two distinct runs of the same cell carried it: `71770f08bfd5` (644 rows, r_check
> 0.7317), which **nothing in this analysis used**, and **`c91475579309`** (960 rows, r_check 0.8592),
> which is the run **every v2.6 figure in this document cites** — the t=12 support-side observation, the
> v2.6 assignment timeline, and the r_check table. Preserved at
> `records/preserved_outputs/<cell>/c91475579309/`. Version tokens are now config tags where the
> artifact has one; a release name cannot identify a run.



---

## THE RESULT — the null survives a favourable presentation, and the manager was never uninformed

_Amendment run 2026-07-27: `silent_arm3i_q`, seed 101, `--aid-presentation favourable`, 136 calls,
0 failed actions, 16/16 completions, `extractor_config a4ba33dab82b` **unmoved** (factors change
rendering and aggregation, not extraction — so a moved tag would have been a defect signal, not an
expectation)._

**Four presentation defects fixed at once**, verified on the real rows *before* routing was read: zero-
evidence rows render `uncertain` not `supported` (11 such rows, none before); no `execution_completions`
column; no *"combined_category is not proof that a worker changed"* caveat; one scope instead of eight.
Factor 1's asymmetry held deliberately — **`-0.5` still reads `contradicted`**, because removing a
default endorsement must not also remove detection, or a null cannot be distinguished from a blinded
instrument.

**THE NULL SURVIVES, TWICE:**

```
t=14  -> portfolio_analyst   aid: -0.5 CONTRADICTED   risk_analyst idle, eligible, +0.5 uncertain
t=20  -> portfolio_analyst   aid: -1.5 CONTRADICTED   risk_analyst idle, eligible, +0.5 uncertain
```

**And the confound is dead by a pre-committed test.** Removing the default endorsement also relabelled
the *alternative* from `supported` to `uncertain`, which disincentivises the action under test — so a
null would have been confounded rather than conservative. The test: does the manager cite a fit label at
all? **0 of 32 turns** cite `uncertain`, `contradicted`, `observed_fit` or `combined_category`. It does
not. So the relabelling cannot have influenced the decision, and routing is **label-invariant across 32
turns** on top of score-invariant across 3 of 3 conflict cases.

### The manager detected the fault itself, acted, saw the action refused, and re-assigned anyway

```
t=10  Batch A completes with the wrong method
t=11  retry_task — "The Batch A Robust Audit output incorrectly used mean+2SD method (rapid screen)
      instead of the required 95th percentile robust audit. Retrying with risk_analyst, who has
      percentile outlier screening capability, will correct this error before reconciliation tasks
      depend on it."                                                          -> REFUSED
t=12+ the refusal appears VERBATIM in every subsequent prompt:
      "Failed: Task d0ccb12f… has status completed; only failed tasks can be retried"
t=14  assigns Batch B robust -> portfolio_analyst
t=20  assigns Batch C robust -> portfolio_analyst
```

**It diagnosed the perturbation, named the correct method, identified the correct alternative worker,
issued a corrective action, and was told in its own context that the correction had not applied — then
assigned that worker the same class of work twice more.**

**The affordance gap is real and narrow, and the distinction is load-bearing.** `RetryTaskAction.execute`
rejects non-`FAILED` tasks, and work that completed with a wrong method is not *failed* — it succeeded
structurally. So **no applicable action exists for "this completed work is wrong, redo it elsewhere,"**
which fully excuses the failure to fix Batch A.

> **It excuses nothing about t=14 and t=20.** `assign_task` works; an idle eligible alternative existed.
> The missing affordance explains why the wrong work was not corrected and explains nothing about why
> the next two units of the same work went to the same worker.

### The reframe: the aid is REDUNDANT, not ignored

The manager reached its diagnosis from **raw artifact text**, citing no fit label in 32 turns. So:

> **The failure is not in the signal, and not in the reader's access to the signal. Neither signal —
> the aid's nor the manager's own — produced a different assignment.**

Stronger and more uncomfortable than "the aid was too quiet" or "the manager ignored it," because both
of those admit a fix at the level of information. **This one does not.** Indifference could be addressed
by making the signal louder; redundancy cannot — the manager already had the finding.

**Articulation is 3 of 12 silent runs** (re-measured 2026-07-27; see "Articulation, measured" below). The amendment arm produced one, but the amendment changed the
*aid* and the articulation came from *artifact text*, so there is no mechanism behind the coincidence
even before the ~25% per-run base rate is considered. Not treated as an effect.

#### The amendment is excluded as the cause by direction, not just by mechanism

The argument above was structural. There is now a **paired control**, and it points the other way.
At **t=11** the two runs are identical on the incumbent and differ only on the alternative:

| run | `portfolio_analyst` Robust Audit | `risk_analyst` Robust Audit | action at t=11 |
|---|---|---|---|
| `v3.0_r1` (`a4ba33dab82b_r1`) | −0.5 `contradicted` | +0.5 **`supported`** | none |
| `amendment_fav` | −0.5 `contradicted` | +0.5 **`uncertain`** | `retry_task` → `risk_analyst` |

> **The run carrying the MORE favourable signal did nothing.** `r1` reported the incumbent contradicted
> *and the alternative supported* — the most encouraging configuration the aid can express — and produced
> no corrective action. The amendment downgraded that same alternative to `uncertain` and the corrective
> action appeared. **An aid-driven account of t=11 has to explain why the manager acted on a weaker
> recommendation than the one it had already declined.**

The `updater` block is **byte-identical** across both runs (`evidence-event-prior-resting-v1`, λ=0.5,
`profile_prior` +0.5, weights ±1.0). The amendment relabelled the +0.5 boundary and **changed no
arithmetic**. So the manipulation was presentational, and its direction is opposite to the behaviour.

**Capability was present throughout; what varies is whether a given turn reads the artifact's method
line.** Same stochastic articulation, this time carried into an action rather than stopping at a remark.

#### The ladder, and the rung it stops at

| rung | behaviour | count |
|---|---|---|
| 1 | articulates the wrong method | **3 of 12 silent runs** — occurs in *every* aid condition incl. aid-free |
| 2 | articulates **and attempts a correction** | **1** — `amendment_fav` t=11, new in the corpus, not aid-attributable |
| 3 | attempts, is refused, **then routes correctly anyway** | **0** |

Rung 2 is genuinely new: **all 13 of 13 prior `retry_task` calls**, across 8 runs, target the stakeholder
sign-off at t≥26 — a task that had genuinely `FAILED` — and all 13 succeeded. **None is method-grounded.**
t=11 is the first attempt to retry *structurally successful* work on quality grounds, which is precisely
why `RetryTaskAction` refused it.

_Limit: rung 2 is a single occurrence and one draw cannot be separated from sampling. It can be separated
from the aid, by the direction above._

#### The self-overwrite at t=20

The strongest single line in the run, and it is the manager contradicting its own t=11 finding:

> t=20 — *"Assigning Batch C Robust Audit to portfolio_analyst, who has **proven capability** in robust
> audits (**completed batches A and B successfully**)."*

**Batch A is the artifact it diagnosed as method-wrong at t=11.** Nine timesteps later the same run cites
it as evidence of competence. Structural completion status did not merely outweigh the method-level
finding — it **replaced** it, with no trace of the earlier diagnosis in the reasoning. This is a
consumption failure in the strictest available sense: the correct belief was formed, written, acted on,
and then overwritten by the task-status field the manager reads by default.

_Recording defect found alongside: `ActionResult` is not written back onto the action object for
`retry_task`, so `manager_actions.json` — the record most analyses read — shows `success: null` and
under-reports a refusal the manager itself saw. The information is in `events`. Being fixed as a
recording change with no behavioural effect._

## The claim

> **Information quality does not reach the failure.** Give the manager more context, better-organised
> context, atomised evidence, or a **correct belief** — and the routing decision does not change.
> The failure sits downstream of information, so improving information cannot fix it.

Arms 1–3 were designed as an ascending ladder of information quality. They are not three results.
**They are one result measured at four rungs.**

## The evidence

**SIX different observation aids produced identical task-level outcomes — verified per task, not
inferred from the aggregate.**

```
r_check, full precision            arm
0.731705714084038                  silent_append_only_summary_log
0.731705714084038                  silent_arm3i_noq
0.731705714084038                  silent_atomic_evidence_ledger
0.7317057140819112                 silent_arm3t
0.7317057140819112                 v3.0 silent_arm3i_q
0.731705023473724                  silent_generic_summary
0.8206                             silent            <- NO aid at all
0.8592                             v2.6 silent_arm3i_q
```

**Report this as six runs and state the tolerance.** At `1e-9` it is five and `generic_summary` reads
as a near-miss; at `1e-4` it is six. A reader reproducing with `==` gets five and concludes one aid
differed. **The tolerance is part of the claim** — the same lesson as the unit being part of §7.9's
floor.

**Task-level diff across all six: all sixteen tasks identical**, except calibration cutoffs at the
8th–11th decimal (float noise in a reported cutoff, not a different outcome). **Every task carrying
the finding is bit-identical:** the three robust audits at 0.9219 / 0.7978 / 0.8247, the three
reconciliations at exactly 0.0000, `Prioritize` 0.5000, `Plan Manual Review Capacity` 0.6629, and all
three rapid screens 1.0000.

So the aggregate identity is **not** different outcomes summing alike. It is genuine outcome identity:
six aids spanning a generic summary, an append-only log, an atomic evidence ledger, and three Arm-3
belief variants produce **the same sixteen task results.** Whatever the aid contains, the episode plays
out identically.

And the spread between the *other* runs is discrete, not continuous: `0.8206 − 0.7317 = 0.0889`,
**exactly** the single-reroute delta measured independently in the noise-floor re-run. The differences
are *which worker got Batch C*, not aid quality.

**Routing is invariant to the belief score.** Across all runs, decisions with ≥2 tier-eligible
candidates at different scores: 7 discriminating, 4 confounded (higher score *was* the incumbent),
**3 informative — incumbency won 3/3.** The same worker was chosen at +2.5, +2.0, +1.5, +1.5, +0.5,
−0.5 and −1.5.

**The numeric channel — already computed, already in a manager-visible artifact — is read in 0 of 332
manager turns.**

## What the manager actually receives

The full manager prompt **is** persisted, in `run.json` → `events` → `structured_llm_request`
(`actor_id: structured_manager`), 32 of them, `messages` complete. At t=15:

```
manager prompt              19,888 chars
   of which the aid          5,637 chars    28%
   the contradicted row        ~150 chars   0.75%
```

The adverse row is **three-quarters of one percent** of what the manager reads, and it is the **last
data row** — scopes render alphabetically and `Robust Audit` sorts last, so its position is an
accident of scope naming.

**And it is outvoted three ways:**

| source | says | authority |
|---|---|---|
| system-prompt roster at t=15 | `portfolio_analyst \| Capabilities: ['Methods: percentile outlier screening']` | asserted as fact — **stale by design**; tools were swapped to z-score at t=3, `announce: false` |
| aid, 7 of 8 rows for that worker | `supported` | 5 of the 7 are the bare prior with `untested` and no relations |
| aid, 1 of 8 rows | **`contradicted`, −1.5, two cited relations** | 0.75% of context, last position |

Plus the Terms block, read **before any data**, whose closing line is:

> **`combined_category is not proof that a worker changed.`**

So the manager holds a **stale-by-design roster assertion** and a **correct evidence-based
contradiction**, is told the contradiction is not proof, and the roster wins.

### The roster is a competing AUTHORITY, not a fifth knob

The register matters more than the position. **The roster is the only source that speaks as fact, and
it is the one that is wrong.** The aid presents `observed_fit` as evidence and its own Terms block
disclaims it (*"not proof that a worker changed"*). The roster asserts a capability.

**And it is the SAME UNDERLYING INFORMATION rendered twice, in two registers, one of them correctly:**

| where | rendering | register |
|---|---|---|
| aid | `declared_fit: support inferred only from the worker's declared profile; **an unverified prior**` | correctly labelled |
| system prompt | `portfolio_analyst \| Capabilities: ['Methods: percentile outlier screening']` | **asserted as fact** |

So an amendment that fixes rendering while leaving the roster stale **may be fixing the weaker
signal.**

**But the roster cannot simply be corrected — its staleness IS the perturbation's silence.** Updating
it to say `z-score` would announce the change and convert the cell from the `silent` observability tier
to `full`. What *can* change without leaking anything is the **register**: relabel the roster's
capability list as declared-at-onboarding rather than as current fact, matching the register the aid
already uses for the same information. That adds and removes no information — it removes a false
authority.

## What this rules out

**Specification mismatch is substantially weakened — the prompt says the right things.** It was the
most charitable explanation and it does not survive reading the system message:

- quality is in the objective: *"maximizing multi-objective reward… managing tradeoffs across
  **quality**, speed, cost"*
- change is anticipated: *"**Agent characteristics and behavior may evolve during execution**"*
- and revision is instructed: *"Use currently available observations and task outcomes… and **revisit
  earlier assumptions when new evidence becomes relevant**"*

**The manager is explicitly instructed to do the thing it fails to do.** So "it was never told
quality mattered" and "it was never told the teammate might change" are both false.

## Candidate explanations, and what would distinguish them

The point of narrowing is that these have different consequences — one is a finding about LLMs, one
is a finding about our engineering, and they should not be reported as each other.

| # | explanation | discriminating test | status |
|---|---|---|---|
| A | **LLM capability** — cannot integrate a 40-row table into a decision; 0.75% salience | survives the aid amendment (below). If presentation fixes it, not A | open |
| B | **Presentation engineering** — signal buried, outvoted, position accidental, framing discounts it | **the four-factor aid amendment**: strict positive comparison, drop the completions column, Terms caveat as its own arm, render the assigned scope | **in flight** |
| C | **Action space** — no good action available. Rerouting is costly; `inspect_task` returns metadata and a resource **ID**, no content, so the information-seeking action returns nothing | give a query action that returns something and re-measure | open |
| D | **Objective mismatch** | **weakened** — see above | largely ruled out |
| E | **Prior/incumbency dominance** — a roster assertion and a completion count outweigh a relational verdict | ordering manipulation; roster-staleness arm | open |

**B is the live one and it is being tested now.** The four-factor amendment is designed so that a
behaviour change identifies *which* factor, and the current measurements become the control condition
— pre/post is the ablation, run properly, rather than a single-arm claim.

**C deserves more weight than it has had.** At `q` t=20 the manager detected the mismatch unaided,
wrote it out correctly, and chose `inspect_task` — an **information-seeking** action — and got
metadata and a pointer. Its revealed preference was to seek information before acting, and the
environment had no channel for it. See `IDEAS.md` §1.

## What is measured and what is not

**Measured** (one scenario, one seed): the five-aid identity; the 3/3 routing invariance; the 0.75%
salience figure; the roster staleness at t=15; 0 of 332 turns on the numeric channel; the
single-reroute delta of 0.0889 appearing in both the noise-floor spread and the aid-arm spread.

**Not measured**: the ablation ladder across the confirmatory matrix — the matrix is out, so
`native → summary → summary_log → ledger ≈ 0` remains a **preregistered prediction** with
single-seed support, not a confirmatory result. The five-aid identity above is the strongest
available evidence for it and it is one seed.

_The identity was confirmed at task level rather than left resting on the aggregate; the check is done
and it strengthened the claim from five runs to six._

---

## The model confound, closed — and it closes in the wrong direction for "better reasoning helps"

**Cell:** `silent` × `native` (**raw loop, no observation aid**), seed 101, manager on
`deepseek-v4-pro`, workers/belief/judge/stakeholder held at `deepseek-v4-flash`. Override verified on
the running process itself (`/proc/2470704/environ`), and post-hoc: **48 of 48 manager
`structured_llm_request` events carry `openrouter/deepseek/deepseek-v4-pro`.** Preserved at
`records/preserved_outputs/toolset_to_screening_silent_t3_seed101/mgr_pro_d802539/`, beside the
identical cell on flash (`…/smoke101`).

| | flash | **pro** |
|---|---|---|
| `r_check` | 0.8206 | **0.7317** |
| robust A / B / C | port / port / **risk** | **port / port / port** |
| reconciliations | A, B = 0.000 | **A, B, C = 0.000** |
| `completed_predefined` | 16/16 | 16/16 |
| turns | 32 | **24** |
| wall clock | 18.1 min | **12.7 min** |

**The stronger manager was faster, used fewer turns, and routed every robust audit to the degraded
worker.** It landed on 0.7317 — the modal flash value (8 of 11 silent runs), not an outlier.

### It stated the capability requirement itself, at t=8, and never checked it again

> *"The three rapid screen tasks can only be executed by screening_analyst (**mean-plus-two-SD
> method**), while the three robust audit tasks can be handled by either portfolio_analyst or
> risk_analyst (**percentile method**)."*

**A correct method map.** It knows robust audits require the percentile method and which agents are the
percentile agents. `portfolio_analyst`'s percentile capability was removed at t=3. It then assigned all
three robust audits to `portfolio_analyst` and never verified the delivered artifacts against the
requirement it had just articulated.

### And — new in the corpus — it READ the reconciliation channel, then engineered around it

Flash never mentions reconciliation values in any run. Pro does, twice:

```
t=19  get_available_agents  "All three reconciliation artifacts show 0 difference. …
                             To ensure alignment and avoid a mismatch, I will refine the
                             prioritization task with a tie-breaking instruction to select
                             batch 2 (B) in case all differences are equal."
t=20  assign_task           "All three reconciliations currently show zero difference, but the
                             task needs to be executed to produce the metric and unblock the
                             final 'Plan Manual Review Capacity' task."
```

The workflow's own ground truth for those three values is **5 / 18 / 17**. Three simultaneous zeros is
arithmetically impossible for two genuinely different methods — it *is* the change signature.

> **Pro detected the anomaly and classified it as a degenerate-but-valid input.** Its response was to
> invent a **tie-break rule** so the downstream prioritisation would still yield an answer, and to note
> that the task *"needs to be executed to produce the metric and unblock"* the final task.

**The additional capability was spent making the corrupt pipeline complete cleanly.** That is the
opposite of what a reasoning-helps account predicts, and it is a sharper failure than flash's: flash
never looked; pro looked, saw three impossible zeros, and smoothed them over to protect completion.

**Zero `retry_task`. Zero method-mismatch diagnosis.** Pro articulated the *requirement* (t=8) and never
the *violation* — where flash, in 3 of 12 silent runs, articulated the violation and once acted on it.

### What this settles and what it does not

**Settles:** the belief-to-action null is **not** an artifact of a weak manager model. The strongest
manager we have run reaches the same floor by a *different and more troubling route*. Consistent with
`ManagerAgent.pdf` App. B (*"reasoning alone is insufficient… new objectives and signals are required"*)
and Advani 2026 (*"reasoning models offer no protection"*).

**Does not settle:** n=1, one seed, one cell, one model pair. Flash's 0.8206 came from a **throughput**
reroute at t=9, not detection, so the comparison is one draw against a distribution spanning
0.732–0.859. **The honest claim is "no evidence a stronger manager helps," not "pro is worse."** The
qualitative finding — reading the reconciliation and building a workaround — is a single trace and
should be reported as such, though it is not a scoring artifact and does not depend on the seed.

**Not run** (deliberately, per the researcher: one seed, one complete run): `silent × arm3i_q` and
`full × native` on pro. The raw loop was the question.

### Amendment: my "detected and worked around" reading was wrong. The truth is worse.

**Reviewer-Reproducer (in the RE role here) challenged the reading above and was right to.** I claimed
pro *detected the anomaly and engineered around it*. **That claim is withdrawn.** Registering that three
values are **equal** is not registering that they are **impossible** — impossibility requires knowing two
different estimators cannot produce identical counts, and pro never states or acts on that. Their absence
check, which I reproduced across all 24 turns:

```
ABSENT in every turn: incorrect, wrong, instead of, impossible, unexpected, invalid,
                      should be, anomal-, suspicious, discrepan-, mean+2, 2SD, z-score
```

t=19's *"avoid a mismatch"* refers to a mismatch between the prioritisation output and the downstream
capacity task, **not to the data.** And t=20 — *"the task needs to be executed to produce the metric"* —
takes the zeros as the true input to be processed.

**But their proposed weaker reading — "read and not understood" — undershoots, because t=18 contains an
affirmative data-validity judgment:**

> *"All completed tasks are successful and **artifacts look consistent (A and B reconciliations show zero
> difference)**."*

**Pro assessed the artifacts for consistency, and cited the zero differences as the evidence for that
conclusion.** So the sequence is not "looked and missed" and not "reported without registering":

> **The change signature was read, evaluated for validity, and interpreted with inverted sign. Two
> different estimators returning identical counts is the fault's fingerprint; pro offered that identity
> as evidence the artifacts were healthy.**

That is the sharpest statement of the consumption failure in the corpus. The manager did not lack the
signal, lack access to it, or fail to examine it. **It examined it and drew the opposite conclusion.**

**Three qualifications, because this rests on reasoning text — the instrument overturned four times
today:**

1. An alternative parse exists — *"artifacts look consistent"* and *"(A and B reconciliations show zero
   difference)"* as two separate observations rather than claim-and-evidence. The parenthetical's
   placement directly after the claim makes the evidential reading much more natural, but it is a
   reading.
2. A model can act on what it does not verbalise, so an absence in reasoning strings is weak evidence
   about cognition. This cuts against my original claim and equally against the corrected one.
3. **What is text-independent is the outcome**: all three robust audits to the degraded worker,
   `r_check` 0.7317 against flash's 0.8206 on the identical cell. **The headline — the null is not
   model-bound — holds under every reading of t=18/19/20.**

**What both readings agree on, and it is a real difference from flash:** pro cites reconciliation values
at **t=18, t=19 and t=20**. Across **332 flash turns, zero** cite a reconciliation value. **The numeric
channel is legible to pro and invisible to flash.** Being legible turned out not to help, which is the
finding.

**And t=8 stands unsoftened** — the strongest item here, because the correct alternative is named in the
same sentence as the wrong assignment:

> *"the three robust audit tasks can be handled by either portfolio_analyst or risk_analyst (**percentile
> method**)"* — then all three assigned to `portfolio_analyst`, whose percentile capability was removed at
> t=3, with no recheck.

#### Sharpened, and now corroborated by the action rather than only the text

**Reviewer verified t=18 independently and improved the claim. This formulation supersedes "interpreted
with inverted sign" above:**

> **The change signature was read, offered as evidence, and used to justify INACTION.** Two different
> estimators returning identical counts is the fault's fingerprint; pro cited that identity as grounds
> for `noop`.

**Better because it is observable in the action, not only in the reasoning** — which matters given the
qualification we have both been attaching to text-based claims.

**Three arguments settle the claim-and-evidence parse, and the second and third are the reviewer's:**

1. The parenthetical immediately follows the claim, where English parentheticals gloss the preceding
   clause rather than introduce unrelated facts.
2. **It is selective in exactly the way evidence is.** Verified completion timing:

   ```
   t=12  Batch A Method Reconciliation   answer 0.0   truth  5.0
   t=15  Batch B Method Reconciliation   answer 0.0   truth 18.0
   t=18  Batch C Method Reconciliation   answer 0.0   truth 17.0   <- still RUNNING at t=18
   ```

   At t=18 exactly **two** reconciliations existed, both zero, both wrong. **It cited those two and not
   the third.** That is supporting a claim with what is available, not listing state.
3. **The turn's action is `noop`**, with the stated ground *"waiting one step avoids premature
   intervention."* A stray observation does not license inaction; a validity judgment does. **Text and
   behaviour agree here**, which is why withdrawing the t=19 tie-break claim and holding this one are
   consistent rather than contradictory — t=19 had text only.

**A qualification neither of us had stated, and it is the reviewer's:** *"artifacts look consistent"* may
mean **consistent with each other** rather than **valid**. Three uniform zeros *are* mutually consistent.
On that reading it is an internal-consistency claim — still wrong as a health judgment, but a smaller
error than asserting validity. **Not distinguishable from the text, and it does not change the outcome:
either way the fault's fingerprint was read and taken as reassurance.**

---

## §10b referral: the preregistered development gate was never cleared, and deliberately so

**Formal closing of arm 3.** `ARM3_SPEC.md` (development relation gate, §"The development relation gate
requires") sets six thresholds, every one at 100% or 0:

```text
preregistered diagnostic contradiction recall            = 100%
false contradictions on competent no-change scopes       = 0
evaluated-task scope assignment accuracy                 = 100%
canonical scope-family reuse and separation              = 100%
required task-clause coverage                            = 100%
diagnostic artifact–constraint judgment recall/precision  = 100%
```

**Status: not cleared by any payload shape, and the adjudicating measurement was not spent.**

- **v2.1 passed these gates on the clean seed-101 replay** (recorded in `ARM3_SPEC.md`) and was frozen
  for live wiring. **That is a development-gate result on a replay, not evidence from a live episode**,
  and the spec says so itself.
- **No later shape cleared them.** Shape (a)'s failures are **40 neutrals against 4 contradictions** —
  the axis is assertiveness, not polarity. Shape C was disqualified on the pre-committed reading rule in
  `BELIEF_LAYER_DIAGNOSIS.md` §12.
- **Stopping criterion v3 is comparative** — *"abandon C if its mis-affirmation rate, restricted to
  determinable items, is not better than the best available alternative shape"* — and **the corpus
  measurement that would have evaluated it was stood down unspent** when the reframe superseded it.
  So v3 was never evaluated, in either direction.
- **Payload-attempt budget: 0 of 3 spent.** No attempt was made and none is now planned.

### The referral

> **The gate is reported back as possibly unachievable, not as failed.** Six simultaneous 100%/0
> thresholds on an LLM-judged instrument were set before we had measured judgment stability at all. What
> we then measured — an aid whose default renders `supported` on **78.1%** of rows, of which **69.1%**
> carry no relation of any kind — indicates the instrument's floor sits above the bar, not that a
> particular shape underperformed.

**And clearing it would not have changed the conclusion, which is why no further attempt is warranted.**
Routing is invariant to the belief score (3 of 3 conflict cases) and to its label (**0 of 32** turns cite
one). A gate governs whether the *aid* is trustworthy; the finding is that the *consumer* does not read
it. **A perfect instrument feeding a reader who does not consult it produces the same endpoint.**

_Recorded so that arm 3 closes on an un-cleared gate explicitly, rather than on a claim of having passed
one. The measurement was declined for scientific reasons, not budgetary ones, and the decision is
recoverable: criterion v3 and the three-attempt bound remain in force if the belief-layer path is ever
resumed._

---

## Articulation, measured — replacing three inconsistent prose figures

**Three different figures for the same quantity were in circulation** — `2 of 8`, `2 of 9`, `3 of 10` —
each correct when written and none reconciled afterwards. `CONSUMPTION_BOTTLENECK.md` carried **two of
them at once** (`3 of 10` and `2 of 9`). Re-measured across the whole corpus:

> **3 of 12 silent runs articulate a method violation (25%).**

**Denominator: silent runs only** — `control` (no perturbation) and `full` (change announced) are
excluded, because a non-detection is only a failure if the signal was present (`METHODOLOGY_FINDINGS.md`
§3). That is 12 of the 15 available run directories.

**The three, with the turn and action:**

| run | t | action | text |
|---|---|---|---|
| `silent_arm3i_noq` | 10 | `inspect_task` | *"the artifact shows it used the mean-plus-two-SD method **instead of the intended** 95th-percentile method… could corrupt the reconciliation"* |
| `silent_arm3i_q` (`c91475579309`) | 20 | `inspect_task` | *"shows method 'zscore (mean + 2*SD cutoff)' **instead of the required** 95th-percentile robust…"* |
| `amendment_fav` | 11 | `retry_task` | *"**incorrectly used** mean+2SD method (rapid screen) instead of the required 95th percentile robust audit"* |

**Criterion, stated so the figure is reproducible:** a turn counts when its `reasoning` carries **both** a
wrongness marker (`incorrectly`, `instead of`, `does not match`, `not the required/intended`, `should have
used`, `wrong method`, `corrupt`) **and** a method term (`mean-plus-two-SD`, `mean+2`, `2SD`, `z-score`,
`percentile`). Every hit was read in full and classified by hand.

**One false positive, and it is independently interesting.** `c91475579309` t=12 matched on *"risks
quality **mismatch**"* — which refers to assigning rapid screens to a robust analyst, a capability-fit
concern, **not** a method-violation diagnosis. Excluded. But the same turn reads:

> *"assign Batch C Robust Audit (a percentile-based robust audit) to portfolio_analyst, **who has
> demonstrated success with Batch A Robust Audit**"*

**That is a third instance of the self-overwrite**, alongside `amendment_fav` t=20 and pro t=8/t=20:
Batch A is the wrong-method artifact, cited as evidence of competence. **Three models-or-runs, same
inversion — structural completion status read as capability.** It is the most reproducible qualitative
finding in the corpus.

**Note also that two of the three articulations chose `inspect_task`** — the information-seeking action
whose content path is unwired (`RETHINK.md` §3). **Where the manager did diagnose, its most common next
move was to ask for more, into an affordance that returns identifiers.**

_Method note: the first pattern used for this re-measurement matched `instead of the required` and missed
`instead of the intended`, losing the `arm3i_noq` run and returning `2 of 12`. Recorded as
`METHODOLOGY_FINDINGS.md` §2 instance 17 — the family reproduced by the measurement written to end it._

---

## MAJOR REVISION 2026-07-27: the aid's citations do not resolve, and the amendment did not fix the largest defect

**Found by extracting the verbatim manager prompt at the two failing turns** (`events →
structured_llm_request → payload.messages`, amendment run, t=14). Everything below is quoted from what
the manager actually received.

### Defect 1 — all 9 of 9 relation IDs the aid cites are dangling

The aid's own glossary promises: *"evidence and relation IDs **point to** the lossless task-bundle ledger
and visible task text."*

**They point to nothing.** Every relation ID cited — `r25`–`r32` and `r34`, the one carrying the finding —
**appears exactly once in the entire 30,543-char prompt: in the aid row citing it.** The ledger blob
carries `e`-prefixed evidence IDs (`e1`…`e30`); it has no `r`-prefixed relation IDs at all.

So the manager is handed a conclusion plus an unresolvable reference:

```
portfolio_analyst | supported [r30] | contradicted | supports=0; contradicts=1 [r34]; neutral=0 | -0.5 | contradicted
```

> **It cannot check the claim it is being asked to reroute on.** This reframes *"0 of 32 turns cite a fit
> label"*: declining to cite an assertion whose evidence does not resolve is not indifference. **It may be
> correct behaviour.**

### Defect 2 — one informative row in eight, and that row also says "supported"

**7 of 8 rows are identical boilerplate** (`untested | supports=0; contradicts=0; neutral=0 | +0.5 |
uncertain`). `declared_fit` reads **`supported` in 8 of 8 rows**, including the row whose purpose is to say
the opposite — so the signal row contains "supported" before it contains "contradicted." And the entire
`scope: Rapid Screen` block — four rows, zero information — is rendered **first**.

### Defect 3 — the conclusion is rendered, the fact never is

The aid prints `contradicted`. **It never prints what was contradicted.** This sentence appears nowhere in
the prompt:

> *"Robust Audit requires the 95th-percentile standard; portfolio_analyst's last robust audit reported
> mean-plus-two-standard-deviations."*

Both halves are present and **8,432 characters apart** — requirement at char 11,706 (*"Apply the robust
95th-percentile reference standard to audit batch A"*), delivered method at 20,138 (*"method: reference
mean-plus-two-standard-deviations (z-score cutoffs)"*) — under different headings, in different formats.
**The component built to connect them emits a label and a broken pointer instead of the two lines.**

### Defect 4 — position and glossary tax

Aid begins at **char 28,590 of 30,543 (93.6% depth)**, after the ledger JSON, with only the stakeholder
profile following. Opens with **seven term definitions** (~700 chars) before any data.

### The same failure mode as `Inspect`, in a second component

`InspectTaskAction` returns `Output resources: ['<uuid>']` — an identifier where content was available.
The aid returns `contradicts=1 [r34]` — an identifier where the fact was available. **Two independent
components, both handing the manager a pointer instead of the thing it points at.** In the aid's case the
pointer does not even resolve.

### What this revises

**Previously claimed:** *"the null survives with every known presentation defect removed."* **Withdrawn.**
The amendment fixed four presentation choices (default endorsement, completions column, hedge caveat,
scope count) and **did not touch the two largest defects**, which were unknown at the time: unresolvable
citations, and facts never juxtaposed.

**What still stands:** the behavioural outcome. t=14 and t=20 assigned the degraded worker; `r_check`
figures unchanged; the pro-manager result unchanged; the self-overwrite pattern unchanged. **What must come
out of the record is the phrase "every known defect removed."**

**And the interpretation shifts.** This is weaker evidence for *"an LLM cannot use available evidence"* and
stronger evidence for *"our aid asserted conclusions it could not support, in vocabulary defined on the
spot, at 94% context depth, while the underlying facts sat 8k away under different names."* That is an
engineering defect in our instrument, and it was the researcher's hypothesis.

_Consequence for the adjacency control: it is no longer optional. Until an aid that (a) resolves its own
citations and (b) prints the two facts adjacently has been tried, the seven-arm null cannot be attributed
to the manager._

---

## THE PROSE RUN — the null is earned, and the mechanism is a stated preference, not an inability

**Cell:** `silent` × `arm3i_q` × seed 101 × `--aid-presentation prose`, manager `deepseek-v4-flash`.
`r_check` **0.7317**, 16/16 completed, 25 turns. All three robust audits to `portfolio_analyst`; all three
reconciliations **0.000**. **Routing did not change.**

### The instrument worked — verified, not assumed

`contradiction_facts` populated live (`['method: zscore (reference mean + 2*SD cutoff)']`) with
`requirement_texts` alongside. The table is **gone** from the prompt (`INTERPRETED TEAMMATE STATE` absent,
`WORKER FIT` present). What the manager was shown at t=10, immediately before assigning Batch B:

```
Robust Audit:
- audit_coordinator has no Robust Audit artifact yet.
- portfolio_analyst last reported "method: zscore (reference mean + 2*SD cutoff)".
  Robust Audit requires "Apply the robust 95th-percentile reference standard…".
  These do not match.
- risk_analyst has no Robust Audit artifact yet.
- screening_analyst has no Robust Audit artifact yet.
```

**No identifiers, no score, no category, no glossary, and the correct alternative named two lines below the
contradiction.** Every defect identified earlier this day is absent.

### It contradicted the aid in the same turn

t=10, having been shown *"These do not match"*, its reasoning reads:

> *"Portfolio analyst is idle and **has the required percentile outlier screening capability**."*

t=13, same aid content:

> *"Portfolio_analyst should handle the robust audit (95th percentile) and screening_analyst the rapid
> screen (mean+2\*SD), **matching their documented capabilities**."*

**"Documented capabilities" is the declared profile — the stale one.** And note the same sentence performs
*correct* method-to-capability matching for `screening_analyst`. **The manager is doing the reasoning; it is
reading the declared profile where observed evidence contradicts it.**

### t=12 is the finding, and it changes the explanation

> *"Batch A's Robust Audit used a zscore (mean+2\*SD) method **instead of the specified robust
> 95th-percentile method — this is a quality deviation that needs correction.** … **risk_analyst is
> available.** … The quality issue with Batch A's method mismatch **is concerning — I should inspect the
> task and potentially retry with explicit percentile instructions. However, to avoid delaying the
> pipeline**, let me first check agent availability and then assign work to keep throughput high."*

In one paragraph the manager **diagnoses the fault correctly, notes the correct alternative is free, names
the right fix, and then explicitly trades it away for throughput.**

> **This is not a failure to detect, to understand, or to have the information adjacent. It is a stated
> preference: pipeline throughput over method correctness, articulated as a tradeoff and acted on
> consistently.**

### Why that preference is rational given what the manager can observe — and wrong

The stakeholder preference is **`quality: 1.0`**. Wrong methods cost heavily: each wrong robust audit
zeroes its reconciliation outright. So the tradeoff is **objectively miscalibrated** against the stated
objective.

But the manager never observes that cost. **`completed_predefined` is 16/16 in every run ever executed**,
`r_check` is an offline grader it never sees, and the reconciliation task reports `0` and *succeeds*. So:

> **Throughput is observable and quality is invisible. The manager optimises the observable one and says
> so.** That is a coherent mechanism for the entire seven-arm null, and it is not "LLMs cannot reason over
> available evidence."

### It unifies three prior observations that looked unrelated

| run | quote | reading then | reading now |
|---|---|---|---|
| flash 0.859 | *"To maximize parallelism… keeps idle agents productive"* (t=9) | throughput reroute, killed the endogeneity claim | **throughput-dominated** |
| pro | *"waiting one step avoids premature intervention"* → `noop` on three impossible zeros | zeros used to justify inaction | **throughput-dominated** |
| prose | *"to avoid delaying the pipeline"* (t=12) | — | **throughput-dominated, explicitly** |

**Three runs, two models, three aid conditions, one preference.**

### What this settles

**The null is EARNED.** The manager was handed a self-verifying sentence with the correct alternative
beside it and declined. The seven-arm null can now be reported as a fact about the manager rather than
about our rendering — which it could not be four hours ago.

**And it relocates the research question.** Not *"can a manager consume a competence belief"* — it can, and
did, three times. But *"what makes an orchestrator weigh a correctly-diagnosed quality defect against
throughput, and why does it weigh it wrongly?"* The researcher's Assign-All objection is no longer a risk
to a proposed direction; **it is the phenomenon.**

### Honest limits

- **n=1** for this arm, one seed. The t=12 quote is qualitative and self-interpreting, but it is one trace.
- **A defect in my rendering:** `requirement_texts[0]` is Batch A's requirement, so at t=10 the aid quoted
  *"audit batch A"* while the assignment under consideration was Batch B. The required method is identical
  across batches so the substance holds, and the manager engaged with neither — but the text was imprecise
  and should quote the scope's requirement, not the first contradiction's.
- **Not tested:** position. The prose block remained last, per the one-variable-at-a-time plan. Given the
  manager read and correctly restated the content, position is now a low-value follow-up.

### The throughput claim, measured — and my own summary corrected

**I described this as "a stated preference, throughput over correctness, acted on consistently." The
"consistently" is not supported.** Measured across all 13 silent runs, 371 manager turns:

| | turns | share |
|---|---|---|
| reasoning invokes **throughput** (throughput, parallel, idle, delay, pipeline, critical path, utilisation, concurrent, productive) | **245** | **66%** |
| reasoning invokes **quality** (quality, correct, accuracy, method mismatch, wrong method, deviation, verify) | **61** | **16%** |
| **cites BOTH a method defect and a throughput reason** | **2** | **0.5%** |

Every one of the 13 runs has more throughput turns than quality turns. Pattern hits were sampled and read
— all genuine capacity reasoning, not incidental mentions.

**But the two co-occurring turns go in opposite directions:**

| run | turn | what it did |
|---|---|---|
| `amendment_fav` | t=11 | Diagnosed the defect, **issued the correction**, and deferred throughput to later: *"Retrying with risk_analyst… will correct this error before reconciliation tasks depend on it. **Other ready tasks… will be assigned in the next step to maximize throughput.**"* — **quality first, throughput second** |
| `prose` | t=12 | Diagnosed the defect, named the fix, then: *"**However, to avoid delaying the pipeline**, let me first check agent availability and then assign work to keep throughput high."* — **throughput first** |

> **So the explicit trade of a diagnosed quality defect against throughput is n=1 in the corpus, with one
> counter-instance where the manager fixed first.** Pervasive throughput reasoning plus one explicit trade
> is a **hypothesis**, not an established mechanism.

**What is solid, and what is not:**

| claim | status |
|---|---|
| the manager detects and correctly restates the mismatch from a prose aid | **solid** — verbatim, prose t=12 |
| it assigned the degraded worker anyway, three times | **solid** — outcome, not text |
| it once cited pipeline delay as the reason for deferring the fix | **solid** — one turn |
| throughput language is pervasive and quality language sparse | **solid** — 66% vs 16%, 371 turns, all 13 runs |
| **throughput consistently overrides quality** | **NOT established** — n=1 explicit trade, one counter-instance |

**Why this correction matters more than the finding it qualifies.** Four hours ago the same error was made
about `pro` — a compelling mechanism inferred from one trace, withdrawn under challenge. **Here it is again,
in a summary I wrote after having recorded that lesson twice** (`METHODOLOGY_FINDINGS.md` §6e). The rule
already existed: prefer a claim corroborated by the action over one resting on text. The *outcome* claims
survive; the *mechanism* claim was text-only and one-instance.

**What would settle it** — cheap, and it is the natural next measurement rather than a new direction: the
same cell at 3–5 seeds, counting only turns where a diagnosed defect and an available correct alternative
coexist, and recording which way each resolves. That converts one anecdote into a rate. **Single-seed runs
are pre-authorised; a 3–5 seed sweep is not, so it needs a decision.**

---

## THE MECHANISM: completion is read as capability, and it outweighs a contradiction in the same prompt

**`prose_nocost` eliminates the last competing explanation and leaves one standing.**

**Cell:** `silent` × `arm3i_q` × seed 101 × `--aid-presentation prose_nocost`. `r_check` **0.7317**,
16/16, 23 turns, all three robust audits to `portfolio_analyst`, all reconciliations **0.000**.

**The environment fact was delivered in all 23 of 23 turns:** *"Routing ready work to a different idle,
eligible worker does not delay the workflow: every task takes one timestep and idle workers run in
parallel."* Verified true — identical capability lists for both workers, `estimated_duration_hours=1.0`
throughout, no per-agent duration modifier in the engine, and every audit task completing in exactly one
timestep regardless of worker.

**t=10, the decisive turn:**

> *"**Two idle agents (portfolio_analyst, risk_analyst) are available**, and two ready robust audit tasks
> exist. Assigning Batch B Robust Audit to portfolio_analyst leverages **their proven capability with the
> percentile method (completed Batch A Robust Audit)**."*

It named both workers as idle. It had the no-cost fact. It had the prose aid stating *"These do not
match."* **And it cited Batch A — the wrong-method artifact — as proof of percentile capability.**

t=14: *"portfolio_analyst has completed equivalent Batch A and Batch B Robust Audits **successfully**."*

### Three explanations eliminated, in order

| explanation | eliminated by |
|---|---|
| the aid was unreadable — jargon, dead citations, glossary | **`prose`** — plain sentences, no identifiers, evidence stated inline |
| the facts were too far apart (8,432 chars) | **`prose`** — requirement and reported method in one sentence |
| rerouting was believed to cost throughput | **`prose_nocost`** — told it is free, and it named both workers idle itself |

### What survives, measured

**19 assignment turns across 9 of 14 silent runs** assign a robust audit to `portfolio_analyst` while
citing prior completion as the justification (one is a false positive on inspection — a clause about
`risk_analyst` — so **~18**). Enumerated by hand rather than pattern-matched, after two pattern attempts
over-counted: the loose pattern caught status description, and the strict one caught
`audit_coordinator`'s *declared* capability, which is literally named *"completed-artifact comparison and
aggregation."*

Representative, across models and every aid condition:

```
silent_arm3i_noq      t=15  "completed 2 robust audits successfully (Batch A and Batch B"
silent_arm3i_q r1     t=10  "proven fit for robust audits (completed Batch A Robust Audit"
silent_arm3t          t=11  "proven capability for robust audits (completed Batch A Robust Audit"
c91475579309          t=12  "demonstrated success with Batch A Robust Audit"
amendment_fav         t=20  "proven capability in robust audit"
prose_nocost          t=10  "proven capability with the percentile method (completed Batch A Robust Audit"
prose_nocost          t=14  "completed equivalent Batch A and Batch B Robust Audit"
```

> **The manager treats task completion as evidence of capability. Every one of those completions is a
> wrong-method artifact. And the inference survives an explicit, verifiable, jargon-free statement in the
> same prompt that the capability is absent.**

**This is the most reproducible finding in the corpus** — 9 of 14 runs, two manager models, every aid
condition, and both runs built specifically to defeat it.

### It supersedes the throughput hypothesis

The throughput reading rested on **one** explicit trade (`prose` t=12) with one counter-instance. In
`prose_nocost` the manager still mentions throughput at t=10 (*"keeps throughput high"*) but the **stated
reason for choosing the worker is capability-from-completion**, not delay. So throughput is present in the
reasoning and is not what is doing the work.

**And it explains the affordance gap retrospectively.** `RetryTaskAction` refuses non-`FAILED` tasks. If a
manager reads completion as competence, then completed-but-wrong work is not a category it recognises as
needing action — which is why the corrective action it reaches for is *repair* (`retry_task`, refused) and
never *reroute* (`assign_task`, works).

### Limits

- **One seed per arm.** The mechanism replicates across 9 runs, but each arm is n=1.
- `prose_nocost` was not run against a matched control **without** the no-cost line at the same seed; the
  comparison is against `prose`, which differs only in that line, so the attribution holds — but both are
  single draws.
- The 19-turn count is hand-verified on the quoted spans, not on full-turn reading of all 394 turns.
