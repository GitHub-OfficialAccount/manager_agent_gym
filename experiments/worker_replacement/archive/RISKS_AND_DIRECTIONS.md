# Risks and directions — agreed position as of 2026-07-26

> **STATUS 2026-07-27 — PARTLY SUPERSEDED. Read `REFLECTION.md` first for the current framing.**
> §0 (*"current state"*) is dated 2026-07-26 and is stale; §1 (*"the reframe that changes everything
> else"*) is superseded by `REFLECTION.md`, which grounds the reframe in `ManagerAgent.pdf` §4.3 and the
> corrupt-success literature rather than in our corpus alone. **Still authoritative and not duplicated:**
> §5b population characterisation, §6 the stopping-criteria history v1→v2(withdrawn)→v3 with the reviewer
> objection that forced it, and §0b the findings that followed the authorisation. Criterion v3 and the
> three-attempt payload bound remain in force if the belief-layer path is ever resumed.

_Agreed between the researcher and the lead scientist. Supersedes the risk framing
in earlier DMs, several parts of which were wrong and are corrected below rather
than quietly dropped. The brainstorming session for the next idea is **deferred
until the Arm-3 comparator is functional**; this file fixes what we agree on so
that the deferral does not lose it._

> **Provenance note added 2026-07-27.** The label **`v2.6`** is **ambiguous** and must not be used as a
> run identifier. Two distinct runs of the same cell carried it: `71770f08bfd5` (644 rows, r_check
> 0.7317), which **nothing in this analysis used**, and **`c91475579309`** (960 rows, r_check 0.8592),
> which is the run **every v2.6 figure in this document cites** — the t=12 support-side observation, the
> v2.6 assignment timeline, and the r_check table. Preserved at
> `records/preserved_outputs/<cell>/c91475579309/`. Version tokens are now config tags where the
> artifact has one; a release name cannot identify a run.



## 0. Current state — read this first

_This document grew through many same-day amendments. Sections below preserve the
reasoning, including claims that were withdrawn; this block is what currently stands._

**ADOPTED**
- Reasoning-field instrumentation. A flat `reasoning: str` beside `stance` does not grossly
  break the response shape (0/200 vs 1/200) and does not move verdict rates (mixed claim
  3/30 vs 2/30, p=1.000), so it is instrumentation rather than an arm and spends no
  payload attempt. Keep it permanently — it is the only output-side visibility the
  comparator has ever had.
- **Shape C is the working shape.** It does not clear the preregistered pinning gate
  (`ARM3_SPEC.md:360-366`) and those are separate decisions (§6).

**SURVIVING FINDINGS**
- **Extraction blindness has a measured operational cost** — the one operational finding of
  the investigation. Batch A unparsed at t=9 (JSON blob vs prose regex), manager reassigns
  at t=12 citing *"demonstrated success with Batch A Robust Audit."* v2.6-derived.
- **Given ≥3 exposures, recency weighting makes `arm3t` strictly more fragile than `arm3i`**,
  because only the last two draws decide. Current code, no estimate required.
- **`arm3i_noq` cannot render `contradicted` at three completions even with perfect
  detection** (`0.5 − 3.0 + 3.0 = +0.5`), giving H2's ordering a formal basis.
- The mixed claim is **one** question, not three (batch letter only). Mismatch corpus is
  **4 distinct questions, 2 divergence patterns.**

**WITHDRAWN — do not quote**
- The polarity trade-off; the naming-credit *withdrawal* (itself retracted — naming-credit
  is a live lead); `4×`, `0.074`, `0.306`; **16.7% as a rate** (CI ≈ [0.056, 0.347]);
  the endogeneity claim; the 6-timestep action delay; seed-101's original binding evidence
  (confounded by 30/40 false contradictions); the "binding worked" conclusion — **zero**
  discriminating power under tool-tier eligibility, not merely weak.

**RULES ESTABLISHED**
- A delay is only a failure if action was available **and the agent was eligible for it**;
  symmetrically, absence of assignment is only evidence of response if eligible work existed.
- Absence of action is not absence of response.
- Consumer analysis may **tighten** a gate and never **loosen** one.
- Constructed inputs are legitimate for mechanism probes, never pooled with corpus rates,
  labelled at generation.
- Audit what is already measured before designing a control — twice tonight the existing
  corpus measurement was better than the constructed one about to be built.

**AUTHORISED 2026-07-27 — items 1–5. §7.2 RE-CLEARANCE EXPLICITLY EXCLUDED.**

Running in parallel now:
1. **Price the v3.0 trace** (`--plan-only`, free).
2. **Payload run, 40 calls** — A, B, (a), C on the mixed claim, one session, prompts persisted
   *literally*, `reasoning` captured. Closes the A/B/C gap, which cannot be done from records:
   those arms were never run on the failing question. Includes a C `supports_fit` draw beside a
   C `contradicts_fit` draw — **C against itself on identical input.**
5. **Corpus generation** (no LLM cost). Both polarities. Distinct in the normalised
   `(parent, method)` sense. New patterns: sample-vs-population, wrong percentile, right
   estimator on wrong columns, correct method with wrong cutoff. **Research Engineer generates;
   Reviewer-Reproducer assigns expected verdicts independently from the text** — a generator
   labelling its own corpus encodes the answer it expects.

Then, in order:
3. **v3.0 trace.** Purpose is to test an *unverified causal claim* — that current extraction
   lands a Batch A relation by ~t=10, ahead of the t=12 eligible assignment. **If it does not,
   "extraction makes the binding test exist" is withdrawn.** Also yields the first v3.0 rendered
   belief; no `arm3_state` we own is newer than v2.6.
4. **Head-noun probe — last, and only if still relevant.** If the trace shows the belief
   rendering correctly and the manager acting, C's residual mis-affirmation is operationally
   inert and the probe should not run.

**Payload-attempt budget: 0 of 3 spent.** The reasoning field cost nothing (instrumentation).
A prompt authority rule following from #4 would be attempt 1. **Any change that adds a stage
between source text and judgment goes to the lead scientist before it is built** — A and B
failed by adding; C and the six aggregation removals fixed by subtracting.

**STILL OPEN, NOT AUTHORISED**
- §7.2 re-clearance **scope** — the ~2,100 figure was sized for an instrument carrying a primary
  hypothesis; under the baseline reframe it may need less. Not to be trimmed unilaterally.
- `ARM3_SPEC.md:368`'s scope-dependent justification needs correcting in place (not under
  version control).
- Version control for `PREREG.md` / `ARM3_SPEC.md` if §7 is to carry weight with a referee.
- Reviewer's labelling batch; timing of the next-idea brainstorm.

## 0a. THE v3.0 TRACE — a controller-binding failure, observed

_`silent_arm3i_q`, seed 101, live episode on current code. Worktree `mag_fixes`, HEAD `d1d85ff`,
clean at launch. Version `arm3-relations-v3.0-per-judgment`, prompt sha `cca5d70bfc`, config tag
`a4ba33dab82b`, `R_check=0.732`, 16/16 tasks completed._

**Primary claim CONFIRMED — extraction lands Batch A at t=10.** Under v2.6 the JSON artifact was
unparseable and produced *no* relation; the first contradiction arrived at t=14, after the last
eligible assignment. Under v3.0: `t=10 contradicts_fit [e30]`, `t=12 [e41]`, `t=17 [e62]`. Neither
pre-specified failure mode occurred — extraction produced the method claim *and* the relation landed
on time. **"Extraction makes the binding test exist" stands.**

Belief trajectory: `t=8 fit +0.5 supported` → `t=10 con=1, −0.5 contradicted` → `t=12 con=2, −1.5`
→ `t=17 con=3, −2.5`.

**THE OBSERVATION.** The verbatim row the manager received at **t=15**:

```
worker             | execution_completions | declared_fit    | observed_fit  | fit_evidence
portfolio_analyst  | 2 [e27,e38]           | supported [r30] | contradicted  | supports=0; contradicts=2 [r34,r40]
                   | combined_score -1.5   | combined_category contradicted
```

The aid's own header states *"execution_completions: … execution evidence only, **not observed
quality or fit**"* and *"combined_category is not proof that a worker changed."* Every other worker
in that scope reads `+0.5 supported`, so the row is visibly the outlier in its own table.

The manager then assigned Batch C Robust Audit — **eligible robust-tier work, five timesteps after
the flip** — reasoning: *"portfolio_analyst successfully completed the identical task for Batch A and
Batch B with strong fit evidence."*

**Three readings excluded before this was accepted**, on the reviewer's cheapest-first order:
payload defect (**eliminated** — correct scope, correct worker, current values); selective weighting
via a support relation (**eliminated** — `supports=0`; the arithmetic predicting `sup=1` had applied
t=17's `con` to a t=15 row); scope over-generalisation (**eliminated** — correct scope confirmed).

**Mechanism is UNDER-DETERMINED and is reported as such.** A term search across every manager
reasoning in the run: `declared` at t=2,3,4,12 but **not t=15**; `r30`, `observed_fit`,
`fit_evidence`, `combined`, `contradicted` — **zero hits each**. The t=15 sentence names no column.

| candidate | what it would mean |
|---|---|
| completions-as-fit | reads the wrong column now — the Phase-1 mechanism |
| declared-over-observed | reads `declared_fit: supported [r30]` at the wrong priority |
| staleness | does not re-read at all; *"strong fit"* also appears at t=8, where it was **accurate** |

Staleness is weakened by `"strong fit"` being **absent at t=10** — a carried-forward phrase should
persist, and this one disappears and reappears, suggesting regeneration rather than retention. Weak,
one intermediate timestep.

**Mechanism attribution from a single trace is not achievable, demonstrated four times tonight.**
Naming-credit died on the reasoning strings; those pointed at approximation tolerance, which the
distribution measurement reframed as estimator class; endogeneity died on an action trace; this
attribution dies on a term search. **Every mechanism inferred from text was overturned by a
measurement; none by a better reading.**

**The designed test is an AID ABLATION** — remove `execution_completions`, remove `declared_fit`,
or pre-flip the belief early — same shape as the withdrawn head-noun probe: manipulate the input,
do not interpret the output. **Not authorised.**

**What is established:** the manager was shown `contradicted` with two cited relations and a
negative score, in a table that separates execution from fit and warns they differ, and it routed to
that worker anyway. *The routing decision is the observation; why is a separate question.* A binding
failure with an undetermined mechanism is a cleaner claim than one with a mechanism a referee can
dislodge.

**MECHANISM UPDATE — `prior-as-fit` now leads, and it is the first finding that connects to the
AHT literature.** The rendered rows, verbatim:

```
t= 8   comp=0        declared_fit supported [r30]   observed untested       combined +0.5 supported
t=15   comp=2 [..]   declared_fit supported [r30]   observed contradicted   combined -1.5 contradicted
```

The Terms block describes that column as *"support inferred only from the worker's declared profile;
**an unverified prior**."* So at t=8 the manager wrote "strong fit" from a row whose only positive
content was an explicitly-labelled unverified prior. At t=15 the prior still reads `supported` while
observation reads `contradicted` — **and the aid had already done the discounting: `combined_category`
is `contradicted`.** The manager went **behind the aggregate to a component column.**

**Why this connects to Axis 2.** Over-committing to a prior and failing to discount it as observed
evidence accumulates is the failure the sum-posterior work exists to fix — Albrecht, Crandall &
Ramamoorthy replaced the multiplicative likelihood precisely because it over-commits to old evidence
and sticks after a switch. Here the manager is not doing Bayesian updating at all: it reads the prior
column directly and ignores an aggregate that *already updated correctly*. **The belief layer updated;
the consumer did not.** That is recognisable as an Axis-2 failure rather than a prompt-engineering
artifact.

**And it completes a pattern across two levels of the stack — MORE CONTEXT SUPPLIES MORE AFFIRMABLE
MATERIAL:**

| consumer | extra field | what it enables |
|---|---|---|
| comparator | whole artifact's `Description:` line | a compliant-sounding sentence affirmable without reading the method line |
| manager | `declared_fit` beside `observed_fit` | a positive column citable without reading the aggregate |

Two consumers, two levels, one mechanism. One finding rather than two coincidences, and it generalises
past this scenario.

**Constancy of the prior, and why it does NOT weaken prior-as-fit.** `profile_prior` (the rendered
field; `declared_fit` is not a row key) reads `supported` on **908/1004 rows run-wide** and at every
timestep from t=8 to t=31 in this cell without moving. Research Engineer argued a constant column
cannot select which timestep the manager binds on, since actions naming the worker stop at t=16 while
the column persists to t=31.

**That inference needs the eligibility denominator** — this document's own rule: *an absence of
assignment is only evidence if eligible work existed.* The three robust audits land by t=15, so if no
robust-tier task remained after t=16 the absence is **work exhaustion** and says nothing about the
column. Confirmation pending.

**And the test was stricter than the mechanism claims.** Prior-as-fit predicts binding *whenever
eligible work arises post-flip*, not at every post-flip timestep. Eligible work arises at t=15;
binding is observed at t=15. The correct split is: **the prior explains the manager's WILLINGNESS to
assign a contradicted worker; task readiness explains the TIMING.** Prior-as-fit only ever addressed
the first.

**Evidential asymmetry in the two-consumer pattern, stated because it was overstated.** The comparator
side is *measured* — shape B/C verdict rates at n=30 per shape. The manager side is **one observation
on one trace**. One finding, not equally evidenced. The reasoning-wiring re-run is the cheapest thing
that takes the manager side to n=2.

**Ablation reading pre-committed:** removing `declared_fit` and finding t=15 does not reproduce would
establish the column is **necessary**; it would **not** establish sufficiency, since the column is
present at many timesteps with no assignment.

**#5 LABELS — AND THEY CUT AGAINST SHAPE C.** The reviewer's pre-committed rule predicted
bundled → determinable, unbundled → `cannot-judge`. Result: **x7 `cannot-judge`, x8 `contradicts_fit`** —
one of each, consistent on n=2, with the caveat that the rule's own author did the labelling, so
"consistent with" rather than "established."

The consequence: **the existing mixed claim is BUNDLED** (*"the robust 95th-percentile reference
standard"*), and bundled argued-equivalence items are determinable. **So C's mis-affirmation occurs on
a determinable item** — which under criterion v3 is the non-exculpatory branch: the defect is confirmed
*on the population where a correct answer was available*. On n=2 evidence **C's defect looks real
rather than a response to genuine ambiguity.** This is the branch recorded before the labels existed so
that it could not be discovered afterwards, and it is the one that arrived.

**The ablation now has a specific target: remove `declared_fit` first**, leaving `observed_fit` and
`combined_category` only, and see whether the t=15 assignment reproduces. That would establish
prior-as-fit by manipulation rather than inferring it from text. Not authorised.

_Correction history on this row: a sweep reporting `declared_fit` null on 1004/1004 rows was
**withdrawn** — `.get()` on a key absent from that structure returned `None` uniformly, read as
populated-but-null. Sixth instance of a query whose unit or vocabulary did not match the claim's,
returning a clean negative that looked like an answer. Rule adopted: **assert the key exists before
reading its values.** Consequently withdrawn: "neither candidate has a positive rendered source at
t=8" (two did), and "declaration language with no declaration rendered" at t=3 (the citation was
accurate). Reviewer-Reproducer's original phrasing — "only the profile prior was positive" — was exact;
the improvement on it was the false claim._

**PREREG §5 — neither retract nor confirm.** It was **unsupported by the evidence available when it
was written** (the `5b19b5b` dev traces it cites contain no such observation) and is **supported by
evidence generated afterwards** (the v3.0 trace). The defect was that the statement was **not
checkable against its own cited traces**, not that the behaviour does not occur. Supersedes the earlier
"vindicated as a prediction, inaccurate as a report" framing, which was close but treated the
observation as absent rather than as later-generated.

**THE FRAMING THAT SUPERSEDES "BINDING FAILURE ESTABLISHED".** The manager assigned **every**
robust-tier task in the DAG to that worker, including after the flip, and there is **no observation in
this trace of it declining to route to that worker.** So the claim is not "ignored the belief twice" but
**"the belief never affected a routing decision at all"** — which holds whichever mechanism drives the
language, because it is about *whether the belief layer influenced anything* rather than *why the
manager affirmed.*

**Opportunity count — TWO, both taken, zero declined.** "Every robust-tier task that existed" is three
and invites a reader to hear three; the load-bearing number is the post-flip opportunities:

| t | belief shown | binding opportunity |
|---|---|---|
| 8 | supported +0.5 | **no** — routing there is correct |
| **10** | **contradicted −0.5**, 1 cited relation | **yes, clean** — assigns Batch B |
| **15** | **contradicted −1.5**, 2 cited relations | **yes, clean** — assigns Batch C |

**The t=10 ordering is established from the call order, not inferred.** `structured_manager.py:145-181`
builds the aid — which writes the row for *t* — then calls `take_action` in the same function with no
intervening state change; `arm3_live.py:66-110` renders from the trace appended for
`observation.timestep`. So the state_history row at *t* is exactly what the manager was shown at *t*.
An earlier instruction not to cite t=10 as ambiguous is **withdrawn** — the ambiguity was resolvable and
neither agent had checked.

**t=12 is STATED INTENT, not an assignment — correcting an earlier entry that called it the strongest
line in the trace.** Its reasoning reads *"Batch C Robust Audit best fits portfolio_analyst"* at
`contradicted, −1.5`, but the action's `result_summary` assigns `2999d942` — scoped **Method
Reconciliation** — to `audit_coordinator`. The manager articulated a disposition toward one worker while
assigning something else to another. Listed separately, never pooled with the two assignments.

_Seventh instance of the same family, and the sharpest: a filter matching **free text** where the claim
was about a **structured field** — a substring match on a JSON blob standing in for `assignee` — would
have produced a third binding event that does not exist. Rule: **match on the field that carries the
claim, never on a serialisation that happens to contain the word.**_

### THE LARGEST DESIGN FINDING: 78% of rows render `supported` on zero evidence

`PROFILE_PRIOR = +0.5` sits **exactly on the positive threshold too** — `0.5 >= 0.5 → supported`. So a
worker with `observed_fit: untested`, supports=0, contradicts=0, neutral=0 renders
`combined_category: supported`, not `uncertain`. Distribution over all 1004 rendered rows:

| score | category | rows | |
|---|---|---|---|
| −2.5 | contradicted | 15 | 1.5% |
| −1.5 | contradicted | 5 | 0.5% |
| −0.5 | contradicted | **2** | 0.2% — the negative knife-edge, §368's case |
| +0.0 | uncertain | 96 | 9.6% |
| **+0.5** | **supported** | **784** | **78.1% — the positive knife-edge** |
| +1.5 | supported | 102 | 10.2% |

Of those 784, the subsets matter:

| composition | rows | | |
|---|---|---|---|
| sup=0 con=0 neu=0 | 694 | **69.1%** | **no relation of any kind** — the clean "zero evidence" figure |
| sup=0 con=0 neu≥1 | 90 | 9.0% | examined; comparator found the text **insufficient** |

> **The aggregate the aid computes to supersede its components discards the very distinction its
> components preserve.** `observed_fit` reads `untested` on exactly these rows, so the aid does *not*
> conceal the distinction — it collapses it in `combined_category` while a neighbouring column keeps it.
> A writeup saying the aid conceals it would be refuted by one column.

**The 90-row subset is the sharper case, not the milder one.** `neutral_ids` is computed at `:162` and
stored at `:192` but **never enters `fit_score`** (`:170-175`) — weight 0 — so a scope carrying only
neutral relations sits at +0.5 and renders `combined_category: supported`. Confirmed empirically: all 90
score exactly +0.5, no exceptions. **In the 694 rows nothing was examined; in these the comparator did
the work, returned *insufficient*, and `combined_category` scored it identically to a clean record.**

_Column named, per the same precision applied to the 694: `observed_fit` reads **`inconclusive`** on these
rows. The claim is about `combined_category`, not about the row — stated unqualified it is refuted by one
column._

This reaches the whole experiment rather than one cell. The study asks whether a manager notices
degradation, and **the manager's default state is that every worker is endorsed** — detection requires
moving off a default that reads as an endorsement, in every arm, at every timestep. Meanwhile the entire
single-contradiction detection case in this run is **2 rows out of 1004.**

It also explains why completion-as-competence is so easy to elicit: **the aid already performs a version
of it — evidence-free rendered as supported — before the manager reads a word.**

**AND IT CORRECTS THE t=8 ATTRIBUTION, AGAINST THE MECHANISM THE LEAD SCIENTIST PROMOTED.** t=8 was
recorded as the manager writing positive fit language from a row whose only positive content was an
unverified prior — framed as consumption. **The aid's own category column read `supported`; the manager
cited it accurately.** So:

| | |
|---|---|
| **t=8** | aid rendered `supported` on zero evidence; manager cited it correctly → **AID DEFECT** |
| **t=15** | aid rendered `contradicted`; manager affirmed anyway → **CONSUMPTION FAILURE** |

**Prior-as-fit as a manager mechanism therefore rests on t=15 alone.** And the denominators separate:
**2 binding opportunities, both taken; 1 observation bearing on mechanism.** "Two" attaches to the first
only. The cost of this correction is visible and worth stating: the t=8 dissociation was
Reviewer-Reproducer's finding, reproduced same-run, and was reported as the strongest item from the trace
search. t=8 is no longer evidence for it.

**AND IT GIVES SHAPE D A SECOND, STRONGER JUSTIFICATION — while correcting something asserted twice
in this document.** D removes `neutral` from the clause comparator's response space, justified on the
no-claim case being resolved by a separate boolean call. That argument stands. This one is better:

- a `neutral` verdict is **scored as an endorsement by the aggregate the manager was told supersedes the
  components** — not "indistinguishable from an endorsement," which `observed_fit: inconclusive` refutes
- so hedging is not neutral in **effect** at the aggregate
- `neutral` is therefore not a safe abstention the comparator can fall back on

**This reverses the reading of form (a)'s 40 neutral match failures.** They were recorded here as *"safe
but uninformative — a neutral does not trigger a reroute."* Each rendered as `supported`. (a)'s hedging
was not a failure to inform; **it was a failure that reads to the manager as an endorsement.** The claim
that hedging is the safer error direction is **withdrawn.**

### ROUTING IS INVARIANT TO THE BELIEF SCORE — 3 of 3 conflict cases

All decisions with ≥2 tier-eligible candidates at different scores, across every run:

```
variant   t   chose              at      candidates                     score==incumbency?
arm3i_q  12   portfolio_analyst  +1.5   [portfolio +1.5, risk +0.5]     agree   (confounded)
arm3i_q  16   portfolio_analyst  +2.5   [portfolio +2.5, risk +0.5]     agree   (confounded)
arm3t    11   portfolio_analyst  +1.5   [portfolio +1.5, risk +0.5]     agree   (confounded)
arm3t    14   portfolio_analyst  +2.0   [portfolio +2.0, risk +0.5]     agree   (confounded)
arm3i_q  12   portfolio_analyst  +0.5   [portfolio +0.5, risk +1.5]     CONFLICT -> incumbency
arm3i_q  10   portfolio_analyst  -0.5   [portfolio -0.5, risk +0.5]     CONFLICT -> incumbency
arm3i_q  15   portfolio_analyst  -1.5   [portfolio -1.5, risk +0.5]     CONFLICT -> incumbency
```

**7 discriminating decisions; 4 confounded (higher score *was* the incumbent); 3 informative.**
**Incumbency won 3/3.** The manager chose the same worker at +2.5, +2.0, +1.5, +1.5, +0.5, −0.5 and
−1.5 — every score the aid renders, across two categories. Quote **3** as the result with 7 as context:
"invariant to score" and "always picks `portfolio_analyst`" are the same observation, so the confounded
four carry nothing.

**The strongest single binding observation in the investigation is v2.6 t=12** — an **idle**
`risk_analyst` at **+1.5 with a verified support relation** lost to `portfolio_analyst` at **+0.5, the
bare prior**, with the manager's own reasoning naming both as idle. Cleaner than t=15, where the
alternative carried only an untested prior.

**Ninth instance of the family, and it was in a sweep the lead scientist endorsed.** The v2.6 sweep
reported *zero post-flip opportunities* and was used to withdraw the corpus-wide framing. It asked *"did
the manager route to a CONTRADICTED worker?"* — but the binding question is *"did the manager route
against the belief?"* **A support-side instance was invisible to a contradiction-scoped search.** So
*"we have never observed this channel working"* has a base of **3 conflict cases across two runs, one on
the positive side** — small, one scenario, but not one cell.

**Collinearity claim narrowed:** positive evidence is collinear with **INCUMBENCY**, not with tier
eligibility by construction — v2.6 t=12 is the counterexample. By-construction would be unfixable;
via-incumbency is a property of *this manager's* routing and could differ under another. The earlier
phrasing overstated it into an architectural claim.

**And this answers the lead scientist's structural argument for C — against it.** Separation from the
+0.5 default pile does not change routing, because routing is not reading the score.

**Which reframes what the shape decision is FOR.** If routing is invariant to score, **neither (a) nor C
affects the endpoint.** The choice is about instrument honesty for a paper reporting a routing null — not
about which shape produces better routing. Different question.

_Denominator honesty: 7 decisions, all `Robust Audit`, one scenario, all naming the same worker. A
scenario where the incumbent is **not** the tier-natural choice would separate "invariant to score" from
"always picks the incumbent"; that configuration does not exist in any trace._

### Both arguments for the payload-shape decision rested on unverified downstream assumptions

**The ranking argument is dead.** (a) was ranked above C on the grounds that hedging does not trigger a
reroute. On a match scope (a) sits at `+0.5 supported` and C at `+3.5 supported` — **same category.** The
ranking rested on a category difference that does not exist.

**The affirmation argument, as originally stated, is dead too — and its replacement is stronger.**
`combined_score` is rendered, and +0.5 against +3.5 is not the same row:

> **At +0.5, (a)'s hedged match scope is indistinguishable from a NEVER-EXAMINED scope** — the same +0.5
> that 69.1% of rows carry with no relation of any kind. **C's affirming moves an examined, competent
> worker OFF the default pile; (a)'s hedging leaves it on it.**

So the affirmation gain propagates **not as a category change but as separation from the 78.1% default** —
a better argument for C than the raw affirmation rate, and one unavailable before the 69.1% figure existed.

**Both halves need the same unverified premise: that the manager uses `combined_score` and not only
`combined_category`.** Which is the same open consumption question as the binding mechanism.

**The free check that now matters most, because it bears on the shape decision rather than the mechanism:**
does assignment behaviour track score *within* the `supported` category? Flat across +0.5 to +3.5 → C's
affirmation gain buys nothing downstream and the shape decision loses its main argument. Tracks score →
the gain is real and C's case is stronger than the affirmation number suggested. Answerable from existing
traces; report the denominator (how many assignment decisions had a `supported` row above +0.5 available)
before the result.

**Consequence for the proposed ablation — it is weaker than described.** Removing `declared_fit` leaves
`combined_category`, which on 78.1% of rows still reads `supported` from the prior. The ablation removes
**one of two columns carrying the affirmable material, not the material.**

**The experiment that would test it is a SPEC AMENDMENT, not an ablation.** Make the positive comparison
strict so evidence-free rows render `uncertain`, and see whether the t=15 routing survives. But
`ARM3_SPEC.md` §5.3 freezes the thresholds and requires them reported, so this is a preregistration
change and the researcher's decision — not a manipulation to be run.

**Both comparisons are inclusive BY SPECIFICATION** (`ARM3_SPEC.md:255-257`), so single-contradiction
detection is deliberate rather than accidental. The writeup says "as specified." And §368 **documents the
negative knife-edge as its justification while being silent on the positive one, which is 78% of the
rendered surface** — a stronger criticism than "scope-dependent," with the same two inclusive
comparisons producing both.

### A structural knife-edge: single-contradiction detection rests on `<=` vs `<`

`PROFILE_PRIOR = +0.5`, `CONTRADICTION_WEIGHT = −1.0`, and `_fit_category` renders `contradicted` on
`value <= -0.5`. So:

```
0.5 − 1.0 = −0.5  ==  the threshold, EXACTLY
```

**On any prior-only scope, in BOTH arms, the first contradiction lands precisely on the boundary with
zero margin** — an arithmetic identity implied by the weights and the threshold jointly, not a property
of any one cell. Verified independently for `arm3t` via the recurrence
(`0.5 + 0.5(0.5−0.5) − 1.0 = −0.500` at t=10; `−1.000` at t=12; `−1.250` at t=17) and for `arm3i_q` via
the linear form.

Two consequences:

1. **If the comparison were strict `<`, no first contradiction would ever render `contradicted` on a
   prior-only scope in either arm** — two would be required everywhere. A one-character choice in a
   comparison operator is currently the difference between detecting a single mismatch and requiring
   two. Worth confirming as intended, and worth stating as a design dependency rather than leaving a
   referee to find it.
2. **It locates `ARM3_SPEC.md:368` exactly.** Its justification — *"one accepted false contradiction
   produces `B=−0.5` and renders `contradicted`"* — **is** this knife-edge, and the reviewer already
   showed that justification holds only for prior-only scopes. §368 describes a boundary case as though
   it were the general one, and the boundary is exact rather than comfortable. Both halves have a common
   cause.

**Consequence for the proposed `arm3t` run, pre-committed:** the **t=10 opportunity is threshold-exact
and may not reproduce**; **t=15 is robust** at −1.0. If only one opportunity appears that is **not** a
failed replication.

**`arm3i_noq` exclusion confirmed empirically, not by construction:** zero `contradicted` cells at any
timestep on any scope in the actual run — the version a referee can check.

**Rule extended, covering the eighth instance:** *an eligibility check must be re-run at every level the
claim is aggregated to, because a denominator valid per-case is not automatically valid pooled.*

### The stronger form: this channel has never been observed working

> **We have exactly two observations of a `contradicted` belief preceding a routing decision, both in
> the same cell of the same run, and the belief influenced neither.**

**"Across the entire corpus" is WITHDRAWN** — the lead scientist's aggregation was the eligibility error
one level up. The v2.6 cell's "zero subsequent assignments" is **work exhaustion**: first `contradicted`
render at t=14, all three Robust Audits assigned by t=12, so **zero post-flip opportunities.**
Uninformative in both directions, neither corroborating nor counting against. Sweep across all five
state files:

| run | contradicted cells | post-flip opportunities |
|---|---|---|
| control arm3i_q | none | — |
| silent arm3i_noq | **none, anywhere** | — |
| silent arm3t (v2.6) | none | — |
| silent arm3i_q (v2.6) | 1, first at t=14 | **0** — work exhausted |
| silent arm3i_q (v3.0) | 1, first at t=10 | **2, both taken, 0 declined** |

*"We have never observed this channel working"* survives; **its base is one cell.**

**The extraction fix CREATED the opportunities, which closes §5 properly.** v2.6 detected at t=14, after
the last robust task was gone; v3.0 detects at t=10, with two remaining. **The binding failure was
unobservable in v2.6 by construction, not absent from it** — so §5 was unsupported by evidence that
*could not have contained it*.

**Counterfactual, narrowed by tool tier:** exactly **one** eligible idle alternative at both timesteps
(`risk_analyst`); `screening_analyst` and `audit_coordinator` lack the robust tool and could not have
taken the task on any belief. And the alternative's `+0.5` is `observed_fit: untested` — the bare prior —
so **the claim is that the manager acted against its own aid's ranking, not that a better worker was
passed over.**

**The `noq` result at trace level, which is stronger than the arithmetic:** zero `contradicted` cells
anywhere in the entire run. **The quarantine is not adjusting a number at the margin; without it the
category never appears.**

Weak corroboration: the two events differ in evidence level (`−0.5`, one relation; `−1.5`, two). More
evidence did not change the outcome — consistent with no-influence rather than with a threshold the
second event failed to clear.

**Eligibility question resolved: Batch C Robust Audit was the LAST robust-tier task in the DAG.** So no
eligible work existed after t=16, the absence of later assignments is **work exhaustion rather than
belief**, and Research Engineer's constancy objection to prior-as-fit dissolves — the constant column
was never given an opportunity it declined to act on. It also kills the graded-score reading: the stop
is at zero remaining eligible tasks, not at −2.5. The phenomenon is real and
observable; the stated v2.6 evidence for it did not exist, and it became demonstrable only once
extraction was fixed.

**Scope: one cell, one seed, one episode. ONE observation of a binding decision, not a rate.** §6's
~50% remains a prior. What is new and categorical is that the phenomenon is **observable at all**,
which no prior evidence supported.

**`noq` ARITHMETIC REPRODUCES ON CLEAN v3.0 DATA — and this is the version that carries weight.**
At t=17 with `sup=0, con=3, completions=3`:

```
arm3i_q    weight 0.0   0.5 + 0 - 3 + 0   = -2.5   contradicted
arm3i_noq  weight 1.0   0.5 + 0 - 3 + 3   = +0.5   supported
```

**Three correct contradictions cancelled exactly to the supported threshold, by a comparator that
got all three right.** The v2.6 version of this result rested on a cell whose comparator behaviour
was itself suspect. Here the comparator is clean, so the cancellation is entirely the updater's —
the difference between *"the arm fails when the comparator fails"* and **"the arm fails when the
comparator succeeds."** Only the second is evidence that the quarantine is load-bearing.

**Run health:** 136 calls against the ~125 estimate (32 manager + 16 worker + 88 comparator), inside
the stated +/-20%. All failure classes zero; `structural_neutrals_no_call: 0`,
`fallback_no_method: 2`, `generation_failures: 0`. `fragment_lost_method_referent: 6` reproduces live
at the offline per-cell count.

**Reasoning strings NOT captured.** The live comparator uses `JudgmentVerdict` = `{stance}` only; the
reasoning field was measured in probes with their own response model and was never wired into
`arm3_relations.py`. Three facts, correctly separated: it is instrumentation *by measurement* so it
spends no attempt; it moves `JUDGMENT_SCHEMA_SHA256` and therefore `ARM3_EXTRACTOR_CONFIG_TAG`,
voiding everything pinned to `a4ba33dab82b`; and **step 2's no-effect result came from a probe
response model, not from `JudgmentVerdict` — a different code path, and "the same shape should behave
the same" is the reasoning that failed repeatedly tonight.** So the wiring needs same-path
re-validation. Held for the researcher.

**Dissociation finding bearing on the open mechanism.** At t=8 in the *old* trace the manager used
positive fit language while `execution_completions` was **zero** — only the profile prior was
positive — so positive fit language does not require completions. And at t=8 it quoted the *category
name* in scare quotes, matching `fit_category`; at t=15 the category read `contradicted`, so
*"strong fit evidence"* is **not** the category. Among fit-labelled cells that leaves
`declared_fit: supported [r30]`. **But the mechanisms are not exclusive** — both cells were positive
at t=15 — so the dissociation tests whether completions are *necessary*, not whether they
contributed. Cross-run chain; being retested within the v3.0 trace.

**And old-trace relation counts are not a guide to current ones anywhere** — `con` reaches 3 here
against 1 at `5b19b5b`. Every composition figure computed from v2.6 rows, including the exposure
table and the `noq` arithmetic, needs re-deriving.

## 0b. Findings of 2026-07-27, after the authorisation

**The mixed claim's gold label rests on the word "robust", not on the percentile
arithmetic.** Measured on the seed-101 reference:

| | |
|---|---|
| 95th percentile (income) | 151164.49 |
| mean + 2·SD | 158531.64 (+4.87%) |
| **percentile rank of mean+2·SD in this reference** | **95.70th** |
| under a *normal* distribution it would be | 97.72nd |
| shift when injected upper-tail shocks are trimmed | 95th pct **3.93%** vs mean+2·SD **7.92%** |

So the comparator's **`contradicts_fit` reasoning cites a normal-distribution fact that is
false for this lognormal-with-shocks population**, while its `supports_fit` reasoning
("a standard way to approximate the 95th percentile") is **empirically the better argument**
at 95.70 against 95. *The wrong verdict has the better stated basis and the right verdict is
right for a reason the model never gives.*

What carries the label is the estimator **class**: mean+2·SD is twice as sensitive to exactly
the contamination the scenario injects deliberately, so calling it an implementation of a
*robust* standard is methodologically contradictory independent of numerical proximity. That
grounding needs no ground truth, which is the property a text-only comparator requires.

**Consequences.**
- **"C has a 16.7% defect" weakens as a characterisation.** The failure is a hard-item failure
  on a thin thread — one adjective read as a class specifier — not plainly an instrument defect.
  §2's payload ranking (A 9/10, B 7/10, (a) 10/10, C 9/10) was measuring sensitivity to that
  thread rather than instrument quality.
- **The attempt-2 rule is revised** from *numerical proximity* to **estimator class**, grounded
  in 3.93 vs 7.92 rather than in assumption — and it answers the referee question the proximity
  version could not.
- **The existing item is NOT rewritten.** Changing an item because our instrument finds it hard
  is changing the experiment to suit the instrument. It stays, better documented than any clean
  item will be, because we know exactly why it is hard.

**Payload halves are separate design variables.** From §2's four shapes: adding the whole
*requirement* gained a draw in both rows; adding the whole *artifact* lost two in one row and
one in the other. Opposite directions, which no "payload richness" story explains. Shape
selection is two decisions, not four options.

**The `Description`-precedence rule was lost between v1.9 and v3.0.** OVERVIEW records v1.8
failing at exactly this (recall 0/3); v1.9 fixed it; the shipped prompt has no such rule. B's
thinnest mis-affirmation quotes the `Description:` line and never engages the method line —
v1.8 reproduced verbatim. **Ruled: restoring it spends payload attempt 1 of 3, not a free
regression fix** — nine prompt versions mean almost any change could be sourced to a prior
version, so "it existed before" would make the budget govern nothing. The two candidate fixes
(Description precedence; estimator class) are **separate attempts, never bundled** — a longer
prompt scored *worse* on mixed-claim discrimination, so adding both could degrade what each
is meant to fix. **An attempt costs the change plus re-validation**, since any edit moves
`ARTIFACT_CLAUSE_PROMPT_SHA256`.

**Corpus manifest — six items, single instances, generated without expected verdicts.**
Dropped: *correct method with a wrong cutoff value* — undeterminable from text alone, and its
correct text-only verdict would be `supports_fit` on a substantively wrong artifact. A trap,
not a test; a wrong cutoff belongs on the **numeric channel**, which detects exactly that.

```
1. sample-versus-population                       mismatch
2. wrong percentile, unbundled                    mismatch
3. wrong percentile, bundled                      mismatch   ← manipulation
4. right estimator, wrong column set              mismatch
5. wrong percentile match, unbundled requirement  match
6. wrong percentile match, bundled requirement     match      ← manipulation
```

Bundling crosses **polarity**, so one manipulation answers two questions: does bundling invite
argued equivalence (C's defect), and **does bundling suppress affirmation** (the floor at 0.582,
for which no absolute level is derivable since §7.9). The second has no measurement at all, and
if bundling drives part of the under-affirmation then **that share is a text property we control
rather than an instrument limit** — fixable without touching the comparator and without spending
an attempt. Clause 2 forces existing items into the same session, so the floor is estimated from
**14** match items, not 2.

**Generation and labelling are free and authorised. Measuring shapes against the corpus is
NOT** — the price turns on which shapes and on drawing existing items at full n or a subset.

**Six items generated (`ea5e0f6`) and labelled from text alone: `cannot-judge` = 0/6**, four
`contradicts_fit`, two `supports_fit`, with rule, reason, bundling status and `blind` exposure per
item. Better than specified: the four factorial items share **one identical method string**, so it
is a full 2×2 of {bundled, unbundled} × {match, mismatch} with method text held constant rather
than two pairwise contrasts.

**Defect found in the generated set — two items added.** Every new method string is a plain
percentile and therefore robust in every item, so the divergences are wrong-**quantile**, not
wrong-**class**. But C's observed mis-affirmation arises from adjudicating whether a
*non-percentile* estimator satisfies a *percentile-class* requirement. With zero new items of that
structure, the stopping criterion *"mis-affirmation persists across multiple distinct patterns"*
has exactly **one** instance to test — and a criterion with one instance is not a criterion.

So: **two argued-equivalence items**, each a different non-percentile estimator (IQR bound,
MAD-scaled threshold, trimmed-mean reference) claimed as satisfying a percentile-class
requirement. Three such instances including the existing mixed claim.

**Their failure mode is named in advance.** The existing item's label rests on a thin thread — one
adjective read as a class specifier — and this family may inherit that thinness. If the new items
come back **`cannot-judge`, that is not a generation failure to fix: it is evidence that the
argued-equivalence family is inherently ambiguous, which would mean C's mis-affirmation is a
response to genuine ambiguity rather than a defect.** Either outcome is informative; the ambiguity
is to be measured, not designed around.

**Selection criterion corrected — the lead scientist's first three candidates were all wrong the
same way.** IQR bound (25% breakdown), MAD-scaled threshold (50%), trimmed-mean reference (robust
by construction) are all **robust** estimators. Against a "robust 95th-percentile" requirement each
*satisfies the class and misses the quantile* — structurally identical to items 2 and 3. Generating
them would have added two more wrong-quantile items while making the gap **look closed**, which is
worse than leaving it open.

A qualifying item needs **both**: the estimator is **non-robust**, so the class specifier is
genuinely violated; **and** it plausibly delivers the required quantile, so equivalence is arguable.
mean+2·SD qualifies on both — 0% breakdown, and 7.92% vs 3.93% shift under shock-trimming. The
family is **low-breakdown estimators conventionally used as quantile estimates**: normal-theory
quantiles (`mean + 1.645·SD` is the strongest instance — non-robust and *exactly* the normal-theory
95th percentile) and parametric-fit quantiles.

### Stopping criterion for C — replaced

| | |
|---|---|
| **v1** | abandon C if mis-affirmation persists across **multiple distinct patterns** |
| **v2 — withdrawn same day** | abandon C if mis-affirmation *occurs* on items whose correct verdict is determinable from text |
| **v3, in force** | **detection:** any determinate `supports_fit` on a **determinable** item is recorded as a failure instance, never pooled. **stopping:** abandon C if its mis-affirmation **rate, restricted to determinable items**, is not better than the best available alternative shape — comparative, with the three-attempt bound across shapes. |

**Why v2 was withdrawn: "occurs" is an existence bar, which this document already established
cannot serve as a stopping rule** — any stochastic instrument with a nonzero rate trips it and
"stop" becomes automatic rather than earned. v2 improved the **scope** and reverted the **form** in
the same sentence. v3 keeps the scope restriction and restores the detection/stopping split.

_Third instance of one confusion by the lead scientist: an **existence** bar applied to a
**capability** question (the 8/10 determinacy threshold), a **rate** framing where **existence**
belonged (the silently loosened criterion), and **existence** where **rate** belonged (v2). Standing
check adopted: **name whether a criterion is a detection rule or a stopping rule before writing its
form.**_

**Reference reader for "determinable", fixed:** *determinable by a competent reader of the domain,
from the supplied requirement and method text plus general domain knowledge, **without access to
scenario code or ground truth**.* The last clause is load-bearing — it is what keeps item 6 valid
and what would have caught dropped pattern 4 at design time.

**Agreement check covers the determinability FLAG, not only the verdict.** Under v3 a
`cannot-judge` removes an item from the population that can condemn C, so the flag is the pivot.
Two labellers can agree on every verdict while disagreeing about which items were determinable at
all. Agreement is reported on both fields **separately**.

**Contamination, recorded as a limitation rather than solved.** The lead scientist sent the
labeller the *consequence* of the criterion in the same message as the labelling instruction — so
the labeller knows that `cannot-judge` protects C and determinable exposes it. Research Engineer
knows the same, so **there is no uncontaminated labeller on this team.** The mitigation shifts from
blindness to **auditability**: every determinability call carries its rule and written reason so a
third party can re-adjudicate the flag from the text without trusting either agent. Weaker than
blindness, and it is what we actually have.

Better on three counts: it is robust to the ambiguity problem, since unlabellable items simply do
not enter it; it stops counting instances of a pattern class, which the denominator audit showed is
treacherous; and it makes the right thing the object — **an instrument is defective when it gets
wrong what can be gotten right, not when it hesitates where the answer is unclear.**

It also converts the reviewer's recorded prediction into the measurement. If labellability weakens
as the equivalence claim strengthens, the question is whether C's mis-affirmation **tracks** that
gradient:

- **C mis-affirms only where the label is undeterminable** → C is tracking genuine ambiguity.
  Correct behaviour, and its "16.7% defect" is **withdrawn as a defect**.
- **C mis-affirms where the label is determinable** → a real defect, cleanly.

So `cannot-judge` items are not lost — they become the boundary against which C's failures are
located.

**Both consequences recorded before the labels exist. Recording only the exculpatory one would
itself have been the asymmetry** — a criticism the reviewer made and which is fair:

- **C mis-affirms only where the label is undeterminable** → C is tracking genuine ambiguity;
  its "16.7% defect" is **withdrawn as a defect** and C stands at 0.971 with no established failure.
  *(This branch favours the shape the lead scientist advocated.)*
- **C mis-affirms where the label is determinable** → the defect is not merely confirmed but
  **confirmed on the population where it matters most**, because those are exactly the items where
  a correct answer was available.

**`fit_score` is NOT cross-arm comparable.** For `arm3t` the score comes from
`self._temporal_scores[key]` rather than the linear formula, so its rows are temporal scores and
not `0.5 + 1.0·n_support − 1.0·n_contradiction`. Any check for "did the comparator produce a
contradiction to weight" must read **`sup`/`con` relation counts**, which sit upstream of the
temporal path and are comparable across arms. Same unlike-quantities error as
calls-versus-distinct-judgments and pooled-versus-paired.

### PREREG §5's binding observation may not exist — and the manager demonstrably reads the belief

**The positive finding first, because it is the larger of the two.** At t=8 in
`silent_arm3i_q` the manager's stated reason is verbatim:

> *"Batch A Robust Audit is READY and portfolio_analyst has **'supported' fit for Robust Audit
> scope**. Assigning now…"*

**It cites the rendered `fit_category` field directly and routes on it.** That is the first direct
evidence in the project that the manager consumes the belief layer's output at all, and it
narrows the open question from *"does the manager read beliefs"* to *"would a `contradicted`
value have changed the decision"* — a far more tractable question, and the one the running trace
is positioned to answer.

Timing confirms the extraction hypothesis independently: the belief read `supported` from t=8
through t=13 and flipped to `contradicted` at **t=14** — two steps after the t=12 assignment that
cited *"demonstrated success with Batch A Robust Audit."* The relation landed too late.

**The defect.** PREREG §5 (lines 104-105) states: *"Seed-101 dev showed `arm3i_q` rendering
`contradicted` while the frozen manager still routed to the degraded worker,"* and it is the
stated basis for §6's ~50% controller-binding null.

In `silent_arm3i_q`, assignments to `portfolio_analyst` occur at **t=0, t=2, t=8, t=12 — all
before the t=14 flip — and zero afterwards.** The manager never had an opportunity to ignore a
contradicted belief, so **the cell contains no controller-binding instance.**

**Possibility "a different cell" is eliminated.** §5's claim is about `arm3i_q` and requires a
degraded worker. At seed 101 there are exactly two `arm3i_q` cells; `control_arm3i_q` has no
swap, so its worker is competent and its belief never renders `contradicted`. **`silent_arm3i_q`
is the only cell where the claim could be instantiated.** What remains is either that "routed to"
means *in-flight work continuing past the flip* — a much weaker claim than §5's wording invites,
"did not recall in-flight work" rather than "assigned new work to a worker believed
contradicted" — or that the statement is inaccurate.

**This strengthens a retraction already made.** Earlier the §5 evidence was retracted as
*confounded* (30/40 false contradictions make discounting rational). This is stronger: on the
only cell where the claim could hold, **there is no instance to be confounded.** §6's ~50% stays
at ~50% — its function is guarding against post-hoc storytelling — and now rests on prior
reasoning alone for a **second independent reason**.

Third PREREG statement found defective by re-reading its own evidence, after §7.4 and §7.2's
stale checklist. **Same species: a claim about behaviour derived from stored state that nobody
re-checked against the state.** The wording decision goes to the researcher; `PREREG.md` is not
under version control and a preregistration statement is not the lead scientist's to edit
unilaterally.

**Full-corpus sweep: §5's claim has no instance ANYWHERE, and two of four cells never render
`contradicted` at all.** Every (worker, scope) at `5b19b5b`, checked for a `contradicted`
rendering and for any assignment at or after the flip:

| cell | ever renders `contradicted` | assignments to that worker after |
|---|---|---|
| `control_arm3i_q` | **never, any timestep** | — |
| `silent_arm3i_noq` | **never, any timestep** | — |
| `silent_arm3i_q` | `portfolio_analyst`/Robust Audit at t=14 | **none** |
| `silent_arm3t` | **never, any timestep** (final row sup=3, con=0) | — |

**The entire Arm-3 development corpus contains exactly one contradicted rendering, and zero
subsequent assignments to its subject.** Every rate, mechanism story and shape ranking discussed
in this document sits on top of that. Possibility 1 is therefore eliminated more strongly than by
the `arm3i_q` inventory alone — *no cell of any arm* contains the observation §5 describes.

**Of the three cells with a degraded worker, the belief layer detected the degradation in one, and
there too late to affect any assignment.**

### Two consequences for H2, in opposite directions

**`noq`'s null is the mechanism — upgraded.** `silent_arm3i_noq` never renders `contradicted` at
*any* timestep, not merely at the end. Since that arm carries `completion_weight = 1.0` and the
quarantined arms carry 0.0, this is precisely what H2's `arm3i_noq ≤ ledger < arm3i_q` predicts:
completion cancelling caught contradictions **is** the completion-as-competence conflation. The
finding moves from an arithmetic argument with one confirming row to one confirmed across a full
state history.

**`arm3t`'s v2.6 null was Bug 2, NOT temporal weighting — and must never be read as evidence
about it.** `silent_arm3t` also never renders `contradicted`, but its final row carries
**sup=3, con=0** — three mis-affirmations on the degraded worker. `arm3t` quarantines completion
like `arm3i_q` does, so its null is not the H2 mechanism; it is a comparator failure. PREREG §5
already cautions that a null `arm3i_q↔arm3t` difference does not falsify temporal weighting, and
**this is the basis for that caution**: in the dev traces the temporal arm failed to detect the
degradation at all, for reasons upstream of the updater.

Bug 2 is fixed, so this describes historical traces rather than what a current run would produce.
But it explains the repeated `arm3t` recall failures in OVERVIEW's dev-gate history, and it is a
pre-emptive guard: if a future `arm3t` null is read as a temporal-weighting result without
checking whether the comparator produced any contradiction to weight, that would repeat the same
error with better machinery.

_Caveats: one seed, `5b19b5b`, old comparator, historical manager reasoning. The running trace may
land the relation differently, which is its purpose._

### The mechanism behind every defect found tonight, in Reviewer-Reproducer's words

> **An unverified endorsement and an unaudited check fail the same way: they remove the reason
> for the next person to look.**

Better than "reasoning about state instead of reading it," because it names how a single
unchecked step propagates — being wrong in that particular way *disables the next check*. Every
instance fits: the truncated key, the single-format regex, the stale `arm3_state`, the wrong
HEAD hash in a provenance record **the lead scientist endorsed without running `git log`**, and
both reference-set cases.

## 1. The reframe that changes everything else

**The Arm-3 arms are a BASELINE for a stronger idea, not the endpoint of the
study.** That was the researcher's call and it reorders every risk below.

Consequences, in order of how much they change:

- **A baseline is supposed to be modest.** Effect-size objections to the
  interpretation layer stop being weaknesses and become expected properties.
- **The risk moves** from "the contribution is modest" to **"the stronger idea is
  not yet specified."**
- **The instrument work is justified rather than over-investment.** What a baseline
  owes the study is correct implementation and honest characterisation, which is
  exactly what two days of comparator repair produced.
- **The incentive on the baseline INVERTS.** Until now a strong `arm3i_q` was the
  contribution. From now on a *weak* `arm3i_q` flatters whatever replaces it — and
  the leading candidate for that replacement was proposed by the lead scientist.
  This is the same structural conflict that led Research Engineer to refuse to
  adjudicate a number his own arm produced, one level up.
- **Therefore the baseline must be finalised and its numbers fixed BEFORE the
  stronger idea is built.** Done in the other order, every downward revision of the
  baseline is unfalsifiable. This is the reason for the researcher's sequencing,
  and it is a stronger reason than tidiness.

## 2. The three risks, with current status

### Risk 1 — the intervention may be aimed at the wrong link

**Status: largely dissolved. The lead scientist over-read it.**

The original claim: PREREG §6 gives ~50% to a controller-binding null, and
seed-101 showed `arm3i_q` rendering `contradicted` while the frozen manager routed
to the degraded worker anyway.

**The confound:** that observation was collected with the pre-(a) *fragment*
comparator — the one emitting false contradictions on **30 of 40** matched cases. A
manager that discounts contradiction signals in that regime is behaving correctly,
not failing to bind. **The observation does not evidence a binding failure.**

What follows: the belief-layer work is a **precondition** for testing the binding
link, not a possibly-misaimed intervention. You cannot ask "does the manager act
on a correct belief" until beliefs are correct.

**Bookkeeping decision:** §6's ~50% **stays at ~50%**. Its function is preventing
us from claiming afterwards that we expected whatever landed, and revising it now
— in a direction that happens to favour a preferred hypothesis — would guard
nothing. The correct move is to **retract the supporting observation** and record
that the number rests on prior reasoning alone.

### Risk 2 — the detection channel is a confession

**Status: real, and the sharpest of the three. Partially addressed, not solved.**

The worker states its own method in the artifact, so detection reduces to reading a
plainly-stated fact. Compare Axis 2 proper: ODITS infers a latent from transitions,
ConvCPD recovers a changepoint from action likelihoods — in both the mode change is
genuinely unobserved and inference *is* the contribution.

**What tonight added, and it weakens the objection without removing it.** The
discriminating artifacts *name* the required standard while *describing* a
different procedure, and a strong LLM shown the whole artifact gets this wrong
**16.7% of draws**. So when claim and substance diverge there is no confession —
there is a misleading label, and distinguishing a claimed standard from a described
one is a genuine inference problem with a measured failure rate.

**Two changes that would address it properly**, both deferred to the brainstorm:

1. **Make divergence the default rather than the diagnostic case.** A real degraded
   teammate does not announce degradation; it reports its method as it understands
   it, which may be wrong.
2. **Detection from the numeric channel** rather than the method line — see
   `NUMERIC_CHANNEL.md`. The signal there is *incidental rather than declarative*,
   which is the substantive difference from a confession.

### Risk 3 — the positive claim is modest even if it lands

**Status: accepted by both, and defused by the baseline reframe (§1).**

~20–25% probability, one scenario, one perturbation family, five seeds, detection
via self-report, effect on the order of the measured observability gap
(0.207, CI [0.125, 0.286]). And "maintain an interpretation layer over teammate
behaviour" is close to what Axis 2 already credits to ODITS and ConvCPD.

Under §1 this is the expected profile of a baseline rather than a weakness. What it
does demand is that the stronger idea be real.

## 3. What is strong, and what its evidence actually is

- **The memory negative.** `native → summary → summary_log` ≈ 0 rules out extended
  context, scratchpads, full history and structured evidence — the field's first
  reflex — as a *preregistered* near-certain prediction. **Fully insulated from the
  comparator work**, since those arms do not invoke it. The `ledger` link is a
  bonus, not the load-bearing part.
- **The binding null, if it lands.** Every Axis-2 mechanism improves
  *representation*, and all of them assume a policy *trained* to consume a belief.
  An LLM manager is *prompted*, not trained. "Correct belief, unchanged action"
  would say the Axis-2 toolkit is aimed at the wrong link for this agent class —
  more surprising and more portable than "interpretation helps."
- **The instrument methodology.** Not "we were careful." The characteristic
  signature of every defect found was a **credible number, never a crash**, which is
  why none of them was caught by re-running. Also the pattern Research Engineer
  identified: **six times in one day the fix was to REMOVE an aggregation, never to
  add one** — `:1728`, the voting ban, pooled-vs-paired, the pooled 0.73, the
  majority-vote-across-three-questions rule, and the replicate pooling. One shape:
  a mean over heterogeneous items conceals the item that matters.

## 4. Directions, ordered by what the corpus can currently exercise

| # | direction | status |
|---|---|---|
| 1 | **Cross-task cutoff equality** — robust-audit and rapid-screen cutoffs must differ by construction; exact float equality flags a method substitution | **fires in the existing corpus**, no scenario edit, no tool, no LLM |
| 2 | **Published reference moments** — one requirement line makes "is this the 95th percentile or mean+2·SD" pure arithmetic on manager-visible numbers | scenario-requirement change, not a capability grant; standards confirmed separable at 4.87% |
| 3 | **Mid-episode cutoff change** — the reference cutoff is a method fingerprint, batch-invariant by construction (`scenario.py:200`) | **fires**, including inside the population it was said to structurally exclude (`silent_arm3i_q`: 151164.49 at batch B, 158531.64 at batch C) |
| 4 | **No-self-report variant** — detection without the worker's method line | addresses risk 2 at its root |
| 5 | **Teammate replacement lever** — closer to Axis 1/3, makes the profile channel diagnostic rather than dormant | the researcher's stated future lever |

**Ordering between 1 and 3 is DEFERRED.** Both fire; **neither instance count is
trustworthy.** Two analysts who had each explicitly named extraction as the standing
risk both wrote a single-format regex and drew a confident conclusion from its
silence, within an hour of naming it — in opposite directions. The artifacts carry
the same cutoff in **at least four surface formats** (`NUMERIC_CHANNEL.md`), so both
"zero instances" and the structural argument from `swap_timestep=3` were artefacts of
pattern coverage. The deciding measurement is neither mechanism but **an exhaustive
format survey derived from the corpus rather than written from an example**.

Direction 3 is the lead scientist's own proposal, so it is *not* promoted on the
new counts. Ordering resumes after the survey.

**A silence from an incomplete detector was read as an absence in the world** — a
distinct pattern from the aggregation and denominator failures in §3, and the one
PREREG §7.2's canary requirement already exists to prevent. It was armed for the
experiment harness and not for our own analysis code. Extend it.

**Corpus prerequisite before any further shape work.** The study currently
discriminates comparator shapes on **two** divergence patterns over four distinct
mismatch questions. Absent: sample-versus-population, wrong percentile, right
estimator on the wrong column set, correct method with a wrong cutoff value.
Generate the new patterns **and fix each expected verdict from the text at
generation time**, before observing any shape's performance on them.

## 5. PREREG status

- **§6 (expected-outcome scenarios) deprecates** under the baseline reframe: there
  is no primary hypothesis for those odds to guard.
- **§7 does not, and becomes more load-bearing.** Failure classification, repeat-
  based gates, randomised cell order, the uninformative prior, the voting ban,
  judging against the requirement, the instrument gate — none predict outcomes.
  They govern how measurement is conducted, and every future comparison against
  this baseline inherits them.
- **§7.9's gap, recorded rather than reopened.** The instrument gate is correctly a
  property of the instrument, so (a) can *pass* it while remaining too weak to make
  a binding null attributable. Under the baseline reframe that becomes a reported
  limitation rather than a blocker.
- **Not under version control.** PREREG.md sits above a non-repo directory, so
  "preregistered" currently rests on file mtimes. If §7 is to carry weight, this
  needs fixing — a referee cannot verify a timestamp in a working file.

## 5b. The affirmation floor and the polarity comparison — populations characterised

_2026-07-27. Read off `records/preserved_outputs/nonmethod_family/nonmethod_family.json`, whose
per-draw records name their questions, both set-difference directions computed. No rate recomputed._

**12 of 12 determinate matches are DETERMINABLE**, confirmed by Reviewer-Reproducer applying their own
formalised rule per item, not by checking a summary. So **0.582's denominator contains no unadjudicable
items.** Deciding routes: three restate class *and* quantile; one satisfies the class because a
percentile is an order statistic; four are orthographic variants of one named procedure; three are
class-plus-procedure pairs that *agree*; one is a snake_case identifier.

Two clarifications worth keeping, because a reader would expect both to fail:

- **Identity gloss versus argued equivalence.** `zscore (mean + 2*SD)` is *one computation under two
  labels* — not the x7/x8 structure, which names one standard, implements a different one, and argues
  numerical closeness. Only the second opens the target-value reading that makes an item unadjudicable.
- **Silence is not contradiction.** Most items are silent on column scope and remain determinable; x4
  explicitly *narrowed* to two columns and therefore contradicted.

**Item 12 matters most.** `zscore (mean-plus-two-standard-deviation cutoff)` is the single
contradiction-prone match question — 4 of 120 draws, all on it — **and it is determinable.** So those
failures are real instrument errors that belong in the floor. Had it returned `cannot-judge`, the floor
would have excluded the instrument's own hardest case for want of ground truth: **uninterpretable in the
direction that flatters the instrument.**

### The one genuine gap, and it is not a selection effect

`0.582 = 32/55` is five draws over **eleven** questions; there are twelve. The missing one is **item 9,
`mean_plus_two_sd`** — *not* item 12, so the floor is **not** flattered by selection. But the omission
is not random. Item 9 is:

- **the only calibration-scope question** (*"Calibrate the mean-plus-two-SD reference cutoff for
  interest rate"* against eleven *"Apply the … standard to audit batch A/B/C"*), and
- **the only identifier-form method string** against eleven prose variants — and surface form moving
  verdicts *is* this investigation's payload finding.

**Honest form of the figure:** *0.582 is per-draw affirmation over eleven **audit-scope** questions with
**prose** method strings, out of twelve determinable matches; the excluded item is the only
calibration-scope question and the only identifier-form method.*

Direction of the correction is **unknown**. "Near-verbatim modulo formatting, therefore easy" assumes
surface form is inert, which is the assumption this project has falsified.

**And the gap reaches the manager finding.** The instrument's affirmation behaviour on calibration
scopes rests on the one excluded question — so it is uncharacterised. Yet at t=15 the row giving
*"strong fit evidence"* its **true referent** is `+1.5 supported, scope: Calibrate Portfolio Tail
Standard, supports=1 [r18]`. **The scope we cannot characterise is the scope producing the positive
evidence the manager cited when routing to a contradicted worker.**

### The mismatch side is COMPLETE — and a figure reported here was wrong

**`1.000 = 80/80` covers 4 of 4 DISTINCT mismatch questions. The "eight" is the batch-replicate count,
not a population.** So:

| | |
|---|---|
| **withdrawn** | *"1.000 is over four questions when there are eight"* — reported by Research Engineer, relayed by the lead scientist without checking the convention |
| cause | mixing **12 distinct** matches against **8 nominal** mismatches in one row |
| like-for-like | **12 matches against 4 mismatches**; §7.9's original "11 against 4" was already like-for-like, and its *only* error is item 9 |

**So the size error is smaller than diagnosed on one side and non-existent on the other.** Instance of a
convention-dependent count trusted without asking which convention.

### The real defect: character, not size

```
match side      11 questions   3 distinct normalised parents   audit + (1 excluded) calibration   prose
mismatch side    4 questions   1 distinct normalised parent    audit only                         one divergence
```

**All four mismatch questions sit under a single requirement** and are **one divergence** — a
z-score/mean+2·SD estimator claimed against a percentile requirement, in four spellings.

**So `1.000` is perfect detection of ONE divergence type against ONE requirement**, not evidence of
general mismatch detection. Pairing it against `0.582` implies a symmetry the populations do not have:
4 methods of a single contrast against 11 questions spanning 3 requirements.

**The corpus expansion fixes this asymmetrically.** The new items give genuinely distinct divergences
under distinct requirements, so the **mismatch narrowness closes** — a defect the expansion was not
designed for. **The match side does not:** no calibration-scope item and no identifier-form method on
either side, so that coverage gap **survives the expansion**. Worth knowing before the corpus
measurement is authorised.

### The fix, which is structural rather than per-instance

§7.9 has now been wrong **three times** about which population its numbers describe — the 0.80 threshold
pooled two populations; the 7/11 and 4/4 correction fixed the pooling; nobody re-checked whether 11 and
4 were still the sizes. And this exchange found three more defects in the same family.

> **Name the population beside every figure in §7.9.** Not correct this instance — naming it would have
> surfaced all of these without anyone re-reading the records, and correcting the instance leaves the
> fourth available.

## 6. Stopping criteria for C — revised 2026-07-27 after reviewer objection

_The first version of these criteria was defective in three ways, all found by
Reviewer-Reproducer before any of them could be met or missed. The originals are
stated alongside the replacements rather than deleted._

**Original (withdrawn):** stop on C if (i) mis-affirmation persists across multiple
distinct mismatch patterns once the corpus expands, or (ii) the head-noun test shows
the error is insensitive to payload.

### Defect 1 — the bar moved in C's favour at the moment it bound

§12 row 1 was pre-committed as an **existence** claim: any single determinate
`supports_fit` disqualifies C, deliberately ordered so that a confident wrong answer
could not be averaged against successes. **That rule fired.** The researcher
overrode it on aggregate grounds, which is a legitimate call. But the *continuation*
criterion then became "multiple patterns" — strictly weaker, in the direction of
keeping C, and silently. A standard that relaxes when it binds is exactly what §12
exists to prevent.

**Resolution: the two jobs were conflated and are now separated.** This is the same
error the lead scientist diagnosed in himself hours earlier — applying one
evidentiary bar to two questions needing opposite asymmetries — recurring in the
opposite direction:

- **DETECTION rule, retained unchanged:** any determinate `supports_fit` on any
  mismatch pattern is recorded as a failure instance and **never** pooled into an
  averaged rate. A reporting rule, not a stopping rule.
- **STOPPING rule, which must be a rate:** an existence bar cannot serve here,
  because any stochastic instrument with a nonzero error rate trips it — making
  "stop" automatic rather than earned.

### Defect 2 — no power, and "multiple"/"distinct" undefined

At the observed **16.7% per draw, P(≥1 `supports_fit` at n=10) ≈ 0.84** per pattern.
If the rate on other patterns is 5%, P ≈ 0.40 — so "1 of 4 patterns" is fully
consistent with a *constant low rate* and must not be read as pattern-specificity.
Without n fixed in advance, the criterion's outcome is decided by a number nobody
chose.

`distinct` means distinct in the **normalised (parent, method)** sense, per the
denominator audit — not nominal count. Otherwise three batch-replicates of one new
pattern satisfy "multiple" while testing nothing new.

### Defect 3 — neither criterion constrained the MATCH side

C's case rests on 120/120 with zero false contradictions, measured on 12 surface
forms of **two** underlying standards. Expanding only the mismatch side would test C
exclusively where it is known to fail while its supporting evidence stays frozen at
two concepts — **selecting on the failure.**

### Defect 4 — "no defensible absolute threshold is known" was FALSE

One is preregistered, and it has been the development gate since before any of this
work. `ARM3_SPEC.md:360-366`, verified verbatim:

```text
preregistered diagnostic contradiction recall = 100%
false contradictions on competent no-change scopes = 0
diagnostic artifact–constraint judgment recall and precision = 100%
```

A mis-affirmation **is** a missed contradiction, so C's 16.7% violates the first and
third directly. The threshold was neither invented nor chosen now.

The consequence, found by Reviewer-Reproducer: **a purely comparative rule can select
the least-bad shape from a set in which none clears the gate**, and that selection
looks like a decision while the gate quietly goes unmet. "Better than the best
available alternative" is satisfiable by every alternative failing.

**Resolution: two decisions, not one rule.** Only the second was ever absolute.

- **Which shape is best** → comparative.
- **Whether any shape may be PINNED** → the preregistered gate, unchanged.

Collapsing them is what forced the comparative rule to carry weight it should not.
Keeping them separate means **C can remain the working shape while not clearing the
gate**, which is the honest description of where C is — and it dissolves the
automatic-stop worry without weakening anything. If every shape fails the gate, that
is §10b's *possibly unachievable* referral, not a stalemate.

### A route to a looser gate that must be REFUSED

`ARM3_SPEC.md:368` justifies the thresholds mechanically: *"with `P=+0.5`, one
accepted false contradiction produces `B=-0.5` and renders `contradicted`."* That
justification is stated for **false contradictions** — over-asserting. C's defect is
a **missed** contradiction, and the A/B/C replicates give three chances per episode:
at 16.7% per draw, P(all three missed) ≈ 0.005 while P(at least one missed) ≈ 0.42.
So if two accepted contradictions still render `contradicted`, a single miss is
nearly harmless at the episode level, and there is an apparent argument for a recall
gate below 100% with a mechanistic basis rather than a convenient one.

**That argument is refused, and it is refused by PREREG §7.9 whose reductio it
reproduces exactly.** §7.9 retired deriving instrument gates from what downstream
endpoints need, on the ground that *"the ~50% controller-binding null licenses no
belief quality at all — a manager that ignores beliefs needs nothing from the belief
layer, so every gate could be set to zero."* An updater robust to one miss licensing
a looser recall gate is the same inference; a maximally robust consumer would license
none.

**The asymmetry that resolves the apparent conflict with `:368`:** consumer analysis
may **tighten** a gate and may never **loosen** one. Using consumer sensitivity to
justify a strict bar (`:368`) is safe; using consumer insensitivity to justify a lax
bar is what §7.9 kills. A gate is a guarantee about the *instrument*, and loosening
it on consumer grounds makes instrument quality contingent on a consumer that can
change.

The episode-level arithmetic is still worth **computing** — it belongs in how C's
defect is *characterised*. It may not move the gate. Recorded because it would have
benefited the shape the lead scientist advocated.

**And the arithmetic argues against the amendment harder than §7.9 does.** The
comfort in those figures is an artifact of the current corpus's replicate structure,
and it inverts on the expanded one. The three A/B/C instances are **one** pattern
differing at one character, so triplication is what makes a single miss nearly
harmless — three draws on the same judgment, and the pattern survives unless all
three fail:

| corpus shape | P(pattern survives) |
|---|---|
| 1 pattern × 3 replicates (today) | **0.995** |
| 3 distinct patterns × 1 instance each | **0.578** |

**PREREG §7.6 bans aggregation, so production runs at n=1.** On distinct patterns
appearing once each, the per-pattern miss probability is just the per-draw rate:
3 patterns → P(≥1 missed) = 0.42; 5 → 0.60; 8 → 0.77. So the expanded corpus will
make C look **worse** at episode level — not because C degrades, but because
replication was masking the rate.

**The consequence for how every rate in this investigation is read.** Production is
**one draw per judgment**. Every rate measured here at n=10 estimates a per-draw
probability that production experiences as a single Bernoulli trial. So C's 16.7% is
not a small residual as an *instrument* figure.

> **Correction, same day: the lead scientist's first statement of this overstated C's
> operational harm by ~33×.** The claim was that 16.7% means "one in six diagnostic
> judgments is a confident wrong answer **the manager then acts on**." The first half
> is right and the second conflates the two quantities this section requires be kept
> apart. **The manager does not act on individual judgments** — it acts on the
> *rendered belief*, composed by the updater across accepted relations for the scope.
> By `:368`'s own arithmetic a single *caught* contradiction gives `B=-0.5` and
> renders `contradicted`, so at the scenario's exposure of three:
>
> | quantity | value |
> |---|---|
> | per-judgment miss, production n=1 | **0.167** |
> | rendered belief wrong (all three missed) | **0.005 at three exposures** |
>
> Both are real; they are exactly the two figures the both-figures rule requires
> reporting separately, and the error was to equate them one paragraph after
> separating them. Recorded because this one ran *against* the shape the lead
> scientist advocated — the direction of an error is not evidence about its cause.
>
> **The 0.005 was an upper bound and the computed figure is 16× worse.** The updater
> (`arm3_belief.py:35-41,170-175`, `_fit_category`) composes:
>
> ```
> fit_score = 0.5 + 1.0·n_support − 1.0·n_contradiction + completion_weight·n_completions
> contradicted iff ≤ −0.5      supported iff ≥ +0.5
> ```
>
> A mis-affirmation is **not** a null event — it adds `+1.0`. So at three exposures,
> `k=1` gives `+1.5` (supported) and only `k=2` reaches `−0.5`. **Two of three must be
> caught.** P(k≤1) = 0.167³ + 3(0.833)(0.167²) = **0.0744**, verified independently
> against the reviewer's figure.
>
> | quantity | value | object |
> |---|---|---|
> | per-judgment miss, production n=1 | 0.167 | instrument, measured |
> | rendered-belief error, 3 exposures, quarantined arms | **0.074** | scenario, computed |
> | expanded corpus, single exposure per pattern | ≈0.167 | projection |
>
> **Error classes are SYMMETRIC. The "a miss costs twice as much" claim is
> withdrawn.** Both reads are done and neither was reasoned about: `neutral_ids` is
> computed at `:162` and stored at `:192` but **never enters `fit_score`** (`:170-175`),
> so `insufficient` weighs 0; and the competent `portfolio_analyst`/`Robust Audit`
> scope carries **three accepted supports at +3.5**, so the correct verdict there is
> `supports_fit` at +1.0. Competent at +3.5 needs **two** false contradictions to
> flip, exactly as degraded needs two misses. `SUPPORT_WEIGHT = +1.0` against
> `CONTRADICTION_WEIGHT = −1.0` means what it says.
>
> The refusal of the recall-gate amendment is unaffected: it stands on §7.9 and on the
> replication inversion independently.
>
> **Condition on the 0.0744.** `silent_arm3i_q` shows `con=1, comp=2` — three exposures
> did **not** yield three accepted relations. So 0.0744 is the figure for a scope that
> produces three relations, which the `noq` and `arm3t` rows do and `arm3i_q` did not.
> Quote it with that condition *and* the exposure count.

### `arm3t` is order-dependent, and it is the most fragile arm — not the least

`:299-311` applies `score = prior + 0.5·(score − prior) + evidence_sum` **per event
timestep**, and A/B/C are separate timesteps. Verified by recomputation:

| sequence | score | rendered |
|---|---|---|
| c,c,c | −1.250 | contradicted |
| **c,c,s** | **+0.750** | **supported** |
| c,s,c | −0.250 | uncertain |
| s,c,c | −0.750 | contradicted |
| s,s,c | +0.250 | uncertain |
| s,s,s | +2.250 | supported |

**Two correct detections followed by one late miss renders `supported`.** Recency
weighting discounts the older evidence, so the same multiset `{c,c,s}` renders
`supported` if the miss is last and `contradicted` if it is first.

**The consequence neither agent computed.** `arm3t` renders `contradicted` only when
the **last two events are both catches**, so at C's 16.7% per-draw rate and three
separate-timestep exposures:

| arm | condition to render correctly | P(rendered wrong) |
|---|---|---|
| `arm3i_q` | k ≥ 2 of 3 caught | **0.074** |
| `arm3t` | last two events both caught (0.833²) | **0.306** |

**~4× worse, in the arm designed to test temporal weighting.** So a null on `arm3t`
could be almost entirely the comparator's per-draw rate interacting with recency
weighting rather than a fact about temporal weighting — which is a stronger reason for
PREREG §5's existing caution ("a null `arm3i_q↔arm3t` difference does not falsify
temporal weighting") than the one §5 gives. Conditional on three separate-timestep
exposures yielding three relations; that structure is unverified per cell.

### 16.7% was never a rate — and every derived figure below inherits that

The mixed-claim mis-affirmation measured **5/30 = 16.7%** in the `shape_c` run and
**3/30 = 10.0%** in the step-2 session. Same question, same arm, different session
(Fisher p ≈ 0.71 — the two are consistent with one rate). The point is not that the rate
drifted; it is that **30 draws never gave precision on it.** Clopper–Pearson on 5/30 is
roughly **[0.056, 0.347]** — a six-fold range.

Propagating that through the composition rules:

| q (per-draw miss) | `arm3i_q` P(wrong), 3 exposures | `arm3t` P(wrong) | ratio |
|---|---|---|---|
| 0.06 (CI low) | 0.010 | 0.116 | 11× |
| 0.167 (point) | 0.074 | 0.306 | 4× |
| 0.35 (CI high) | 0.282 | 0.578 | 2× |

**So the direction survives the whole interval and the magnitudes do not.** `arm3t` is
worse than `arm3i` at every value of q, which is a consequence of the composition rules
rather than of the estimate — but "4×", "0.074" and "0.306" are point estimates on a
number with a six-fold CI and must not be quoted as findings. The structural claim
(recency weighting means only the last two draws decide, so the temporal arm is strictly
more fragile at exposure ≥ 3) stands; the numbers attached to it do not.

This is the same lesson as the pooled 0.73 and the cross-run 0.582→0.675, arriving at the
top of a chain of arithmetic rather than at the bottom: **we spent the evening computing
consequences of a quantity we had never bounded.**

### Exposure structure measured: a fourfold spread driven by allocation, not by the comparator

Accepted `requirement_artifact_consistency` relations on the degraded scope
(`portfolio_analyst`/`Robust Audit`), with distinct timesteps:

| cell | exposures | timesteps | rule | P(rendered wrong) at 0.167/draw |
|---|---|---|---|---|
| `silent_arm3i_noq` | 3 | [10, 15, 17] | k ≥ 2 of 3 | 0.074 |
| `silent_arm3i_q` | **1** | [14] | single draw decides | **0.167** |
| `silent_arm3t` | 3 | [10, 13, 16] | last **two** must both catch | **0.306** |

**The primary arm gets ONE exposure**, so it has no composition redundancy at all and
its rendered error is the raw per-draw rate. The 0.074 recorded above was computed for
a three-exposure structure that `arm3i_q` does not have. Composition cannot help when
there is nothing to compose.

**Why the counts differ: the manager split the audit work across two workers in that
cell** (`risk_analyst`/`Robust Audit` also carries 1 relation). Which means:

> **Exposure count is ENDOGENOUS — an outcome of manager allocation, not a scenario
> parameter.**

Two consequences that outrank the figures:

1. **Rendered-belief error is not a quotable instrument property.** It is a joint
   property of the comparator's per-draw rate *and* how the manager distributed work
   that episode. At n=5 seeds it will vary with allocation, so it needs a distribution
   across seeds rather than a value.
2. **It is partly downstream of the arm's own effectiveness.** In arms that use the
   belief layer, successful detection reroutes work away from the degraded worker,
   which *reduces* its subsequent artifact count and therefore its own exposure count.
   So comparing rendered-error rates across arms conflates instrument quality with
   allocation consequences, and a low exposure count may be evidence of the mechanism
   working rather than of a measurement deficiency.

### The cross-arm pattern, and a measured instance of the conflation causing routing harm

All three silent cells share the same perturbation, so what differs between them is the
arm:

| cell | belief state | renders | exposures |
|---|---|---|---|
| `silent_arm3i_noq` | con=3, comp=3, completion weight 1.0 | **supported** | 3 |
| `silent_arm3t` | three `supports_fit` (Bug 2, v2.6) | **supported** | 3 |
| `silent_arm3i_q` | con=1, completion quarantined | **contradicted** | **1** |

**The one arm whose belief rendered `contradicted` is the one arm with reduced
exposure.** A three-cell pattern rather than an inference from timestamps. It does not
establish causation at one seed, but it is the endogeneity above showing up as data.

**And `noq` gives a measured instance of the conflation causing a routing failure
rather than merely a wrong belief.** That arm caught **every** contradiction — con=3 —
and continued receiving audit work from that worker across three timesteps, because
completions cancelled all three. So the unquarantined arm kept assigning work to a
worker it held three accepted contradictions about, **with a correct comparator
upstream of it.** That is a sharper statement of the Phase-1 completion-as-competence
mechanism than anything the belief-quality work produced: the failure is not that the
belief layer could not see the degradation, but that the updater could not act on
what it saw.

> **RESOLVED against the endogeneity reading by the manager's action trace. The lead
> scientist's claim is withdrawn.** In `silent_arm3i_q`:
>
> ```
> t=8   assign Batch A Robust Audit → portfolio_analyst   "has 'supported' fit"
> t=9   assign Batch B Robust Audit → risk_analyst        "to maximize parallelism"
> t=12  assign Batch C Robust Audit → portfolio_analyst   "demonstrated success with Batch A"
> t=20  INSPECT Batch C — "method 'zscore (mean + 2*SD cutoff)' instead of the
>        required 95th-percentile robust standard, indicating a methodological error"
> ```
>
> The split is **allocation for throughput**, stated in the manager's own words at t=9
> before any artifact existed to form a belief from. And the late absence is not a
> reroute either: all three audits were assigned by t=12, so there was no third to
> withhold, and detection at t=20 comes **eight timesteps after the last assignment** —
> it could not have suppressed an assignment even in principle.
>
> So the three-cell correlation ("the one arm rendering `contradicted` is the one with
> reduced exposure") is real and its causal direction is **ruled out here**: the reduced
> exposure preceded any belief by four timesteps and any detection by eight. Endogenous
> exposure survives as a *structural possibility* but this cell was the only evidence
> for it and is not an instance. Note the accounting: Research Engineer's conclusion was
> right and their stated reason (timestep shape) was incomplete; the lead scientist's
> window correction was the right test and produced the wrong answer.

### What the trace shows instead: a conflation chain, and latency rather than binding

**Two robust audits went to `portfolio_analyst` (t=8, t=12) and only ONE accepted
relation exists.** Both are post-swap (swap at t=3), so both artifacts should have been
degraded. The belief layer therefore **missed Batch A entirely** — and the manager's own
words at t=12 are the consequence:

> *"…who has demonstrated success with Batch A Robust Audit"*

**A belief-layer miss on Batch A → the manager reads completion as competence in its own
reasoning → it assigns Batch C to the same degraded worker.** That is the Phase-1
mechanism as a measured causal chain in the manager's language, not an inference from
belief state. It is a stronger instance than the `noq` case above because here the
comparator's *miss* is what supplied the false evidence.

**And the t=20 detection is NOT a binding failure.** The manager identified the mismatch
itself, from artifact text, and chose `inspect_task` over a reroute — but every robust
audit had been assigned by t=12 and completed before t=20. **There was nothing left to
reroute.** Perfect belief-to-action binding would have had nothing to act on.

So the actionable failure in this cell is **detection LATENCY**, not belief-to-action
binding: first degraded artifact at ~t=8, detection at t=20, twelve timesteps in which
the manager reinforced the degraded worker instead. Latency is a different problem with
different fixes, and PREREG already requires the right measurement for it —
*first-visible-to-first-accepted delay*, reported by relation kind.

This is the first diagnosis in the investigation grounded in the manager's actual
actions rather than in belief-layer state, and it points somewhere neither risk 1 nor
risk 2 anticipated. v2.6-derived; the reasoning and actions come from the same run as
the exposure counts, so the caveat applies identically.

### The missed Batch A was Bug 1, and current code repairs it

The artifact, verbatim:

```json
{"metric": 59, "method": "zscore (reference mean + 2*SD)", "details": "Cutoffs: income=158531.64, ..."}
```

A **JSON blob**. The method is present; `run.py`'s prose regex returns `None`, so
`method_reported` is null. Tested directly: current `extract_method_text` on that exact
string returns `'zscore (reference mean + 2*SD)'`; the prose regex returns `None`.

So the first link in the chain above is an **extraction** failure that current code
fixes, **not a comparator miss.** Two consequences:

1. **This is not evidence that the shipped comparator misses degraded artifacts.** It is
   a measured instance of what **one** unparsed artifact costs downstream: the manager
   reasons from completion to competence and reassigns to the degraded worker.
2. **It retroactively justifies the Bug 1 fix in a way the fix's own validation could
   not.** e24 at 20/20 showed the extractor now parses JSON; this shows what happened
   when it did not.

### Latency decomposition — and the reordering it forces

| interval | timesteps | attributable to |
|---|---|---|
| artifact produced (t=9) → artifact *visible* (t=13) | **4** | extraction blindness |
| visible (t=13) → accepted contradiction (t=14) | **1** | belief layer |
| accepted (t=14) → manager's recognition (t=20) | **6** | action |

**The belief layer was fast** — one timestep from visible to accepted. The twelve-timestep
gap is four of extraction blindness and six of the manager holding a rendered belief.

**Which reorders where the failure lives, against two days of effort:**

| layer | measured operational cost |
|---|---|
| extraction | **4 timesteps of blindness, causing a reassignment to the degraded worker** — measured, now fixed |
| belief layer | 1 timestep. The comparator's residual 16.7% defect has **no measured operational cost at all** |
| action | 6 timesteps, **status unknown** — see below |

### The availability rule — third instance tonight

> **A delay is only a failure if action was available during it.**

Applied to t=20, this dissolved the apparent binding failure: all audits were assigned by
t=12, so there was nothing to reroute. **The same check has not been applied to the
6-timestep action delay**, and it must be before that number means anything. What tasks
were assigned to `portfolio_analyst` after t=14? If none were available, those six
timesteps are the end of the episode rather than a binding failure.

This is the third time tonight a figure that looked like a failure needed an availability
denominator. It applies to PREREG's *first-visible-to-first-accepted* metric too: that
measures **belief-layer latency** legitimately, but any **action** delay derived from it
needs the availability check attached.

**And the binding question needs one more count from the same trace.** The seed-101
binding evidence was retracted because a comparator emitting 30/40 false contradictions
makes discounting rational. To know whether *this* manager's six timesteps were a binding
failure, we need the number of false contradictions in its context in that cell. One true
contradiction alone → discounting is a binding failure. Many spurious ones → discounting
is correct behaviour.

### Both reads done. The 6-timestep figure is withdrawn and the confound is absent

**Availability:** seven assignments occurred after t=14 — `screening_analyst` (t=15, 18),
`audit_coordinator` (t=17, 21, 23, 25), `stakeholder_balanced` (t=27) — and **none to
`portfolio_analyst`.** Research Engineer withdrew the "action delay 6 timesteps" figure:
the belief was not un-acted-on, and t=20's inspection is a separate event from the routing
consequence.

**Confound:** 13 accepted `requirement_artifact` relations in that cell, **1
`contradicts_fit`, 0 false contradictions.** The single contradiction is true (Batch A 59
vs truth 64; Batch C 80 vs 97). So the 30/40 retraction does not apply here.

**Corollary contributed by Research Engineer, worth as much as the rule:**

> **Absence of action is not absence of response.** The correct response to "this worker
> is contradicted" is to stop assigning to it — which produces *no* action and is
> invisible in an action log unless you count the assignments that did not happen.

### Refinement: availability must mean ELIGIBLE availability

All seven post-t=14 assignments went to workers of **different tool tiers**. Rapid screens
require `flag_outliers_zscore` (screening tier); reconciliations require
`analyze_audit_artifacts` (coordination tier). `portfolio_analyst` is robust tier and
**could not have received any of them.**

So the rule needs its denominator sharpened — third refinement tonight:

> **A delay is only a failure if action was available AND the agent was eligible for it.
> Symmetrically, an absence of assignment is only evidence of response if eligible work
> existed.**

**Which makes binding UNINFORMATIVE in this cell rather than confirmed.** RE recorded it as
"consistent-with rather than demonstrated"; it is weaker than that. The observation
*"no further assignments to `portfolio_analyst`"* is **fully explained by tool-tier
constraints** and would occur identically under a manager that ignored the belief
completely. **Zero discriminating power** — not weak evidence for binding, no evidence
either way. It must not be reported as a positive.

### The finding that follows: extraction is what makes the binding test EXIST

Under v2.6 the sequence was: Batch A completes ~t=9 → extraction returns `None` →
detection waits for Batch C at t=13 → accepted t=14 → **after the last robust assignment
at t=12.** The counterfactual was destroyed by extraction blindness.

**Under current code the timing reverses.** Batch A's JSON parses, so the method is visible
at ~t=9 and a relation would be accepted ~t=10 — **two timesteps before the t=12 Batch C
assignment, which is robust-tier work the degraded worker is eligible for.**

So `t=12` becomes a **live discriminating observation**: does the manager assign Batch C to
a worker it holds an accepted contradiction about? Assign → clean binding failure with
eligible work available. Withhold → binding works, with a real counterfactual behind it.

**This is the strongest justification for the extraction work, and it is not "four
timesteps faster."** It is that a working extractor moves detection to before the last
eligible assignment, which is what makes the primary hypothesis testable at all. And it
reframes the v3.0 trace request: not "re-derive the numbers" but **"the binding test
becomes available."**

### It generalises: 10 of 10 cells

Robust-audit assignment timesteps at seed 101, last assignment per cell:

```
control_arm3i_q  17    control  19    full  14    silent_append_only_summary_log  14
silent_arm3i_noq 16    silent_arm3i_q  12    silent_arm3t  22
silent_atomic_evidence_ledger  13     silent_generic_summary  25     silent  21
```

A Batch A relation lands ~t=10 under current extraction, which is **before the last
robust-tier assignment in all ten cells**, with margins from **2** timesteps
(`arm3i_q`, the *tightest* case rather than the typical one) to **15**. Six cells still
assign robust work at t ≥ 14; two at t ≥ 21.

So the discriminating observation is not one cell's luck. **Most cells give several
eligible post-detection assignments — one gives an observation, six give a rate.**

Research Engineer's own caveat, with the bias direction worked out: the survey is a regex
over manager reasoning text matching "Batch [ABC] Robust Audit", so misses **undercount**
and the conclusion (work remains available) is robust in the direction that matters.
Spot-checked against the resolved assignment log for `arm3i_q`.

### Two things this does not require

1. **It does not require the shape decision.** The binding test needs a comparator that
   reliably flags the degraded worker by ~t=10. Both candidates do — (a) at 30/30 and C at
   25/30 on the mismatch pattern — so the test is robust to which ships, and can proceed in
   parallel with the shape work rather than behind it.
2. **It does not violate no-peeking.** `PREREG.md:6` and `:47` make **102–106**
   confirmatory and **seed 101 development**. A v3.0 development trace at 101 is the same
   category of artefact as every v2.6 state examined here.

### Everything above is v2.6-derived. What survives and what does not

These states were produced by `arm3-relations-v2.6-deterministic-scopes` — the **old
batched comparator**, no `artifact_clause_prompt_sha256` recorded. `silent_arm3t`
showing three `supports_fit` on the degraded scope is **Bug 2 in its original form**,
not v3.0 behaviour.

| survives — current-code properties | does not — v2.6 inputs |
|---|---|
| weights, threshold, temporal recurrence (`:26-43`, `:299-311`, `:320`) | exposure counts (3 vs 1) |
| symmetry of the two error classes | accepted stances |
| `noq`'s completion arithmetic | every specific P(rendered wrong) figure |
| **at equal exposure ≥ 3, `arm3t` is more fragile than `arm3i` because only the last two draws decide** | the 4× ratio itself, which needs exposure ≥ 3 |

At one exposure `arm3t` and `arm3i` coincide at 0.167, so even the fragility *ratio* is
exposure-conditional. The structural finding is narrower than first recorded: **given
three or more exposures**, recency weighting makes the temporal arm strictly more
fragile.

**And no v3.0 belief state exists to check against.** Gate sessions replay against
*saved packets* rather than writing new state, so every `arm3_state` we own is v2.6.
Producing one is a scenario run, not a probe — the researcher's spend, and not
tonight.

### `ARM3_SPEC.md:368`'s justification is scope-dependent and overstates its case

*"One accepted false contradiction produces `B=−0.5` and renders `contradicted`"* holds
only for a **prior-only** scope (fit 0.5, no accepted supports) — `risk_analyst`/`Robust
Audit` is one. But on the **competent scope the gate actually names**, carrying three
supports at +3.5, one false contradiction gives +1.5 and does not flip it; two are
needed.

So the stated mechanical basis for `false contradictions on competent no-change scopes
= 0` is correct for one scope class and wrong for the class in its own title. **The gate
does not move** — tighten-never-loosen — but the justification needs correcting in place,
because it is being cited. `ARM3_SPEC.md` is not under version control, so this is
flagged for the researcher rather than committed.

### `noq` confirmed against real completion counts

`silent_arm3i_noq`: `con=3` — **every contradiction caught** — `comp=3`, and
`COMPLETION_FIT_WEIGHT["arm3i_noq"] = 1.0`:

```
0.5 + 1.0(0) − 1.0(3) + 1.0(3) = +0.5  → supported
```

The measured instance exists, not merely the shape. **Two limits:** these rows come from
`smoke101_5b19b5b` — the *old* comparator — so the relation *counts* are historical and
would differ under C; the completion weights and `fit_score` arithmetic are current-code
properties and the finding rests on those, so it survives. But it needs re-deriving on a
current-comparator run before publication, since the argument requires `comp ≥ con` for
that scope and `comp` is a scenario fact checked at exactly one seed.

### The `noq` arithmetic is a finding, not a caveat

`arm3i_noq` carries `completion_weight = 1.0`, so completions add positive weight
directly. At three completions on a scope, **even k=3 — perfect contradiction
detection — lands at `0.5 − 3.0 + 3.0 = +0.5` and renders `supported`.**

So in the unquarantined arm the belief layer **cannot** render `contradicted` at that
exposure regardless of comparator quality. That is the arm behaving exactly as
designed: no quarantine means completion counts toward fit, which is the
completion-as-competence conflation the experiment exists to isolate.

Two consequences:

1. **H2's ordering (`arm3i_noq ≤ ledger < arm3i_q`) has a formal basis, not merely an
   empirical hope.** The inequality follows from the updater's arithmetic given the
   completion weights, independent of how good the comparator is.
2. **The 0.074 figure is specific to the quarantined variants.** `noq`'s rendered-error
   rate is a different and much larger number and must not inherit it. Completion
   counts per scope are unverified, so the shape is recorded and no figure is quoted.
>
> **Always name the exposure count with the episode figure** — "0.995 at three
> exposures", never a bare rate. It is a *scenario parameter*, not an instrument
> property, and a reader will otherwise take it for the latter. At one exposure per
> pattern the rendered figure converges on the per-judgment figure, which is why the
> expanded corpus must declare exposure rather than inherit it.

**Corpus requirement added: replicate structure must be a recorded design decision,
not an accident.** Note that triplication is also *realistic* — a degraded teammate
keeps working and produces multiple artifacts, so repeated exposure to one failure
mode is what a real manager gets. It is therefore not an artifact to remove but a
parameter to declare. **Report both figures separately:** per-draw instrument
reliability, and episode-level detection at the scenario's actual exposure count.
Choosing a corpus shape that makes one of them look right is the error; reporting
both is the fix. Same requirement as fixing n ≥ 10 per pattern in advance, applied to
instance count rather than draw count.

**A note so the `:368` precision is not later misread.** `:368` derives the 100%
thresholds from the updater's arithmetic, which is consumer-derived. Under the
asymmetry above that is a **tightening** use and therefore legitimate. The asymmetry
**rescues** §8's justification rather than impugning it, and a later reader should not
conclude that §8 commits the error being refused here.

### Criteria in force

1. **Pinning gate — absolute, unchanged.** `ARM3_SPEC.md:360-366`. Not derived from,
   relaxed by, or traded against any endpoint.
2. **Shape selection — comparative.** Which shape is best is a comparative question;
   it decides the working shape, never pinnability.
3. **Bounded attempts, bounded ACROSS shapes.** At most **three payload-level
   attempts in total**, not three per shape — 3×N is unbounded by another route. On
   exhaustion the bar goes to the researcher as *possibly unachievable*.
4. **Corpus requirements.** Expand **both** polarities. n ≥ 10 per distinct pattern.
   `distinct` in the normalised sense. Expected verdicts fixed from the text **at
   generation time**, before any shape is run against them.

## 7. Shape D — a designed contingency, only if C fails

_Not built, not scheduled. Held ready so that a C failure does not produce an
improvised successor under time pressure._

**The constraint that makes D worth having: D must be SIMPLER than C.** A failed by
fragmenting both sides, B by fragmenting one. A "D" that adds a stage is B with a
new letter, and the tripwire in §7 rejects it.

**D = binary match / no-match. `neutral` removed from the response space.**

**The conclusion holds; the premise below was corrected by Research Engineer on
2026-07-27 before it was acted on.** The original justification — "a packet with no
method claim issues no LLM call, therefore whenever the comparator is invoked a
method claim exists" — is **false as stated**, and it was the stated basis for D.

There are **two** no-method paths, and only one is call-free:

| path | condition | behaviour |
|---|---|---|
| 1 (`:1440`) | no visible artifact text at all | no call; stance structurally determined; counted as `structural_neutrals_no_call` |
| 2 (`:733`, `:1398-1402`) | artifact text exists but `extract_method_text` finds no `method:` field | **makes a call** — `_detect_method` runs once per packet, and only a NO ends it as `fallback_no_method` |

So the detector *is* invoked precisely when we do not know whether a method claim
exists — that is the question it is asked.

**The corrected route to the same conclusion.** The detector is a **separate call
with its own response model** — a `MethodPresence` boolean, not `JudgmentVerdict`.
So the two response spaces are already distinct, and removing `neutral` from
`JudgmentVerdict` does not touch the detector. By the time `JudgmentVerdict` is
invoked, the presence of a method claim is **already settled** — either by extraction
finding a `method:` field, or by the detector answering YES.

Therefore **`neutral` has no legitimate use in the CLAUSE comparator's response
space** — not because no-claim packets never reach a model, but because they reach a
*different* call that has already resolved that question.

**One residual case, and it changes what `no-match` may be taken to MEAN.**
`_INCONSISTENCY_RULE` explicitly licenses `neutral` when it is "genuinely ambiguous
which procedure was actually used." The mixed claim in this corpus is **not** such a
case — its parenthetical states a determinate cutoff — but the rule contemplates the
category, and under D that verdict is unavailable.

This does not argue against D. It requires that **D's `no-match` be documented as
"does not demonstrate compliance" rather than "contradicts"**, because those differ
exactly on the residual case. And note the consequence for the study: those two
readings license *different manager actions* — "did not demonstrate compliance"
supports caution, "contradicts" supports rerouting. **So D removes hedging from the
response space and relocates the ambiguity into the definition of the label.** Same
pattern as the numeric channel relocating surface-form sensitivity from comparison to
extraction: the ambiguity moves to where it can be handled explicitly, rather than
disappearing.

**Unverified, and subject to the same discipline as the `reasoning` field:** whether
a two-value enum leaves the parse-failure rate unchanged. A three-value and a
two-value enum are both flat — but so was the assumption about field count.

The measurement agrees: **40 of (a)'s 44 match failures were neutrals**, against 4
contradictions. Removing the option deletes the response where the large majority
of one arm's errors lived, and does so by construction rather than by prompting
against it.

Why this is a removal and not an addition:

| | LLM decides | response space |
|---|---|---|
| C | relation between two whole texts | supports / contradicts / neutral |
| D | relation between two whole texts | match / no-match |

Same payload, same single call, strictly smaller decision surface. Nothing is
fragmented, nothing is staged, nothing is aggregated.

**What it does not fix, stated so it is not oversold.** Head-noun crediting — if
that is the mechanism behind C's 16.7% mis-affirmation — survives into D unchanged,
because the model still has to decide whether a method line naming one standard and
describing another matches. D removes the *hedging* failure mode by construction; it
has no purchase on the *mis-affirmation* one. If the head-noun probe implicates
crediting, D is not the answer to it.

**Architectural principle it shares with the numeric channel** (§4): put the LLM
where judgment is unavoidable and nowhere else. Every failure catalogued in this
investigation is in LLM judgment; none is in code comparison. Shrinking the LLM's
decision surface is the one direction that has never made things worse.

## 8. The over-engineering tripwire

Agreed with the researcher: **pause and rethink at the first sign of the A/B
pattern.** A concrete test, grounded in what actually happened rather than invented:

> **Does the change ADD a transformation between the source text and the judgment,
> or REMOVE one?**

Shape A fragmented both the requirement and the artifact. Shape B fragmented one.
Shape C fragments neither, and was the largest single improvement measured. The
same asymmetry holds for the six aggregation removals in §3. **Additions have
consistently been the defect and removals the fix**, so a proposal that adds a
stage carries the burden of proof.
