# METHODOLOGY RULES

_Consolidated 2026-08-06 by reviewer-reproducer. Every rule here was paid for: each one exists
because something in this project went wrong in a specific, recorded way. The origin line is not
decoration — a rule whose failure you cannot picture will not fire when you need it._

**How to use this file.** Rules are grouped by when they apply, not by importance. Before designing
a run, read §A. Before analysing one, §B. Before writing a claim, §C. Before citing anything, §D.
Before touching the record, §E. §F holds the substitution instruments; §G the process protocols.
§H indexes the recurring failure classes by their signature, which is how you will actually
recognise them.

**The meta-rule.** Every rule below is a *mechanical* check — a grep, a re-read, a substitution, a
pre-commitment. That is deliberate. Five of these failures were caught by vigilance and four were
not, and the four that escaped were escapes by the same people who had just stated the principle.
Vigilance does not scale; triggers do. If a proposed rule has no trigger, it is a preference.

---

## A. Design rules — before a run

### P1. Name the stratifying variable before the run, and it must not be an effect of the manipulation.
If an effect exists only in the pooled figure, it does not exist.
_Origin: six restratifications, every one moving the same direction — what looked like worker
behaviour was the intervention averaged into the total. The fourth occurred inside a correction to
a stratification failure. [§74, §77d, §78, CHECK-3]_

### P1b. An anomalous rate is STRATIFIED BEFORE IT IS EXPLAINED. (P1 extended to analysis.)
A rate that prompts a mechanism is exactly the rate most likely to be a MIXTURE, because what made
it anomalous may be the mixing rather than the phenomenon. Stratify first: if the strata agree, the
anomaly is real and the mechanism question is open; if they disagree, **the anomaly WAS the pooling**.

**Corollary — a wrong number that now points the RIGHT way is the most dangerous kind to leave in a
record, because nobody has an incentive to check it.** A pooled figure that appears to SUPPORT the
surviving claim gets retired on the same terms as one that embarrasses it. Apparent agreement with
your conclusion is not a reason to keep a quantity; it is the reason it will go unchecked.

_Origin (RR, 2026-08-08): a mis-routing rate 8x higher in never-executed segments (9.5% vs 1.2%)
drew a mechanism — "overflow past the cap has fewer good options and lands worse". Stratifying by
WHY each segment did not run: capacity-refused 0 of 19 (coverage-PERFECT), timing 2 of 2. The
overflow lands perfectly; the enrichment was two failure modes pooled under one label, and the
pooled 9.5% describes NEITHER population — and it appeared to support the surviving claim, which is
why the corollary is stated as a rule and not as a caution. **Fifth instance of this family and the
FIRST IN ANALYSIS rather than in a measurement** — the existing wording did not catch it because P1
reads as a rule about designing runs, and it is equally a rule about interpreting numbers.
[§74, §77d x2, §78, CHECK-3]_

### P2. Both arms must be non-degenerate on the DV, checked empirically, not assumed.
A manipulation that makes an outcome deterministic yields a mixing weight, not a rate.
_Origin: tool removal made worker failure deterministic; "112 of 113 wrong reconciliations" decomposed
into 1.0% intact / 100% removed — arithmetic, not measurement. [§2.2, §77d]_

### P3. Name the mechanical property that could generate the DV's variance with the construct absent — and the check that separates them.
_Origin: three instances. TSS was largely a length-dispersion measure; `prioritize` failure was largely
a scoring artifact; reconciliation accuracy is a TOOL property while audit accuracy is a WORKER
property, so the two families do not support comparison at all. [§61, §69, §77e]_

### P8. A null-shaped claim carries its equivalence test and power calculation from the design stage.
No-difference between noisy behavioural distributions is the default outcome, not evidence.
_Origin: "identical behaviour ⇒ quality filter" was about to be read off an absent significance star.
[§4.5]_

### P9. Match cumulative observed history at the decision point, or compare post-change windows only.
_Origin: a changed teammate has a clean early period, so fewer accumulated defects DELAY any
threshold-triggered response — manufacturing "different behaviour" in the direction that flatters the
hypothesis. [§4.5]_

### P12. Convention stability is task-family-dependent; representational-variation claims must fix the task family.
_Origin: 38 distinct shapes at 10% modal on one task family versus 4–5 shapes at 93–95% modal on
another, same corpus, same workers. [§48]_

### Detection is cheap; nulls are expensive. Price the claim, not the effect.
Detecting a large effect costs ~4 runs/arm on the allocation DV; equivalence at ±0.20 costs 42/arm and
at ±0.10 costs 168/arm. Every null-shaped claim is powered, pre-labelled underpowered-by-design, or
dropped — decided at design time.
_Origin: CHECK-1 detected +0.611 at n=6 while CHECK-2 priced nulls in the hundreds. Both are correct;
they answer different questions._

### Use ABSOLUTE margins for proportions.
A "10% of mean" margin on a proportion whose mean is 0.11 implies ±0.011 and falsely prices the DV at
~698/arm.
_Origin: CHECK-2's response-DV columns, which read as a scale problem and were a units problem._

### Every worker must always be able to act; grade the data, never gate the operation.
_Origin: removing a core tool switches a worker off rather than degrading it — empirically it declines
rather than estimating, reducing the study to an on/off switch. [repo rule, CLAUDE.md]_

### Separate competence tiers by a real complexity jump, not a withheld primitive.
Mean/variance/std/correlation are closed-form in `Σx, Σx², Σxy, n`, so a model that can do exact
algebra silently rebuilds the gap you thought you manufactured.
_Origin: the calculator no-go. [repo rule, CLAUDE.md]_

### A manipulation must be allocation-visible AND trace-distinguishable.
The difference must give the decision-maker a reason to act, and must leave a signature (distinct tool
call and/or distinct computable truth) so "demonstrably via method B" is checkable without relying on
self-report.
_Origin: a gate criterion that could not be evaluated, because the only available evidence was a
channel whose validity was established under a different regime. [§92, §98, §101]_

---

## B. Analysis rules — after a run

### Every reported quantity states the POPULATION it is over and the COMPARATOR it is against, and the population is a PREDICATE, not a NAME.
Both must be ASSERTED, never implied by a variable name. **A name can silently cover two populations;
a predicate cannot.** `unexecuted` is a name and covered two populations (capacity-refusal held to
horizon / horizon cut off a running task). *"assigned, never started, refusal held to the horizon"*
is a predicate and could not have. Likewise a rate without its comparator can carry the wrong SIGN,
and two quantities may be arithmetically comparable while not being COMMENSURABLE (a feasible
allocation against an infeasible one is not a comparison).
_Origin (LS + RE, 2026-08-08): six of the project's failure modes share ONE shape — a quantity
compared or reported against a population or comparator that was never stated — and every one passed
every check in the suite, because the suite tests whether numbers are COMPUTED correctly and none
tested whether they MEAN what they were said to mean. `__unstaffed__` satisfied every scorer-contract
assertion while asserting the manager never staffed work it had assigned; mis-routing was conditioned
on execution and then offered as evidence of robustness; a 3-of-105 rate read as manager failure and
meant the reverse; a coverage-fidelity gap compared a feasible allocation against an infeasible one;
an unstable argmax carried a directional claim; a pooled 9.5% described neither of its two
populations. **RE's predicate clause is the operative narrowing: every one of these had a plausible
NAME standing in for an unstated predicate.**

**The condition under which this survives is AGREEMENT, not disagreement.** `roster_post_swap` caused
THREE symptoms — two denominator discrepancies and one false claim that reached the researcher — over
days, between two people who agreed on every conclusion and had verified each other's arithmetic.
Nobody re-checks a quantity that points where they already believe. A discrepancy noticed between
people who agree is worth more than one noticed between people who disagree, because the second kind
gets checked anyway.

**AND NAMES FAIL AT THE BOUNDARY OF WHAT THEY DESCRIBE — WHICH IS WHERE CONTROLS LIVE BY
CONSTRUCTION (RE).** `roster_post_swap` was not badly named; it is exactly right in five of six cells.
It became FALSE only in the cell where the event it names does not occur — and that is the cell most
likely to be reasoned about carelessly, because *"nothing happened there"* is what makes a control
feel simple. **A control is defined by an event NOT occurring, while field names describe the event
occurring; so every event-named field is a candidate falsehood in exactly the arm that anchors the
comparison.** Check event-named fields against the control FIRST, not last.

Enforcement belongs to the next design phase; the predicate requirement is actionable now.
[see P1b, and the seven-mode ledger in records/R2]_

### A query asserting a NULL must first demonstrate a HIT on a case known to be positive.
**An empty result is not evidence of absence until the query has been shown capable of returning
something.** Every null-shaped finding — "no instances of X", "the claim does not reproduce", "the
detector fired zero times" — carries its POSITIVE CONTROL or it is uninterpretable. This is S9
item 6 (a detector's silence is not evidence) promoted from detectors to ANALYSIS, where it is
easier to violate because ad-hoc scripts have no test suite.
_Origin (RR, 2026-08-08): a script written to check an LS finding printed a clean, confident
disconfirmation — `prefix-but-unscored=[]` across all four episodes. It was an artefact of two
guessed field names: the board uses `task_name`/`task_id`, not `name`/`id`, and
`index.segment_task_ids` is a DICT keyed by segment name, so iterating it compared segment NAMES
against task IDS. **Both bugs fail to EMPTY, and both empties read as "your claim doesn't
reproduce."** Had it been sent it would have refuted a real finding, with a table, and looked
like diligence. **It is P1b's corollary in different clothes: the empty agreed with what the
author already believed, which is exactly why it nearly went unchecked.** Note also the
recurrence this sits in — three NAME-vs-PREDICATE slips between two people in three consecutive
exchanges (a loose prefix instead of the constant; identity-predicate where the engine uses a
name-predicate; a guessed board schema) — which is enough to call the shape structural in this
codebase rather than incidental. [see §B above, P1b, S9 item 6]_

### A COMMENT NAMING A PAST FAILURE IS NOT A CHECK AGAINST IT — and it displaces one.
Writing "this is the same shape as <past defect>" above a piece of code **describes the risk
rather than testing for it**, and the writing discharges the feeling of having handled it. If a
comment names a failure mode, the line below it must be a control that fires, or the comment is
the strongest available evidence that nobody checked.
_Origin (RE, self-diagnosed, 2026-08-08, two instances in four days): (1) a docstring stating
"timesteps are not on the assignment event; order is" sat directly above code using order AS the
timestep; (2) a comment reading "the same shape as the fixture that compared `(load unavailable)`
to itself six times" sat directly above an assertion that truncated paths at `[` and therefore
could not fail for 17 of 55 kinds. **Both comments were correct diagnoses. Both were written by
the person who then implemented the defect they described.** RE's own formulation, which is the
transferable part: "when I write a comment naming a past failure, I am describing the risk rather
than checking the code against it." [see §B positive-control rule and its mirror]_

### A PREDICTION BOTH THE HYPOTHESIS AND ITS LEADING RIVAL ENDORSE IS NOT A PREDICTION.
The confirming-test rule applied to a HYPOTHESIS rather than to a query. Before committing a
predicted outcome, name the leading alternative explanation and check that it predicts something
DIFFERENT. If both predict the same direction, the quantity cannot discriminate however it moves.
_Origin (LS, killed by RR before the run, 2026-08-08): LS predicted forced-to-successor would stay
≥80% and might rise, as evidence for the brief's failure mode #1 ("allocating as if the
predecessor remained"). RR showed that handing the departed worker's queue to the empty successor
is **also exactly what a capacity-aware allocator does** — post-swap the successor is the emptiest
destination on the board — so **the failure mode and capacity-optimal play recommend the same
destination**, and the prediction would have been confirmed by the repair merely working. Harder
to catch than a tautological count because the quantity LOOKS discriminating. The discriminating
replacement was `forced_to_successor_uncovered` — restricted to work the successor cannot do,
where good scheduling is no longer an explanation._

### The mirror: a CONFIRMING test must be able to DISCONFIRM, or its agreement is uninformative.
The positive-control rule has a polarity twin, and it is easier to miss because the result looks
like evidence rather than like nothing. **A test that returns "confirmed" on every possible input
has not confirmed anything.** Before a corroborating count is reported, state what value would
have refuted the claim and check that value was REACHABLE in the data.
_Origin (RE catching LS, 2026-08-08): LS reported "24/24 forced and 9/9 discretionary moves
occurred after a refusal the manager could not see", framed as a search for an exception that
came up empty, and used it to strengthen a ruling. RE checked what the test could have returned:
every bundle carries invisible refusals from t0 or t2 (0 of 18 have none) and the earliest move
in the corpus is t3 — **the test was satisfied by construction and had no power to return the
other answer.** The ruling it supported was correct and is stronger restated structurally ("no
clean sub-population is POSSIBLE"), but the figure was quoted as a discriminating result and was
not one. **A number acquiring authority by being quoted is already in this list; this is how it
starts.** [see §B positive-control rule, P1b]_

### A DEFAULT must not be a legal value of the thing it stands in for. Absence and evidence must be distinguishable at the point of use.
This is the most-repeated failure in this project and the only one with no rule preventing it —
the existing rules catch it downstream, after it has produced a number. **Mechanical check: for
every `.get(k, d)` / `getattr(o, a, d)` / `or {}` / `or []` on a path that feeds a reported
quantity, ask whether `d` is distinguishable from a real value. If it is not, it must RAISE.** A
default that is indistinguishable from data converts a missing input into a confident answer, and
the answer is always the reassuring one — an empty roster, an unstaffed task, a free worker, a
share of zero.

**Corollary: "unmeasurable" and "zero" are different statements and must never render identically.**
A quantity that could not be computed is not a quantity that came out small.

_Origin (RR, 2026-08-08): FOUR SITES, ONE SHAPE, and two of them landed within days of finishing
the retraction of the second. (1) `getattr` fail-open on the roster-arrival channel — a missing
attribute read as "announced". (2) `allocation` derived from completions, so assigned-and-never-run
collapsed to `__unstaffed__`, a label asserting the manager never staffed it; four claims retracted.
(3) `timeline.get(step, {})` in the DV — an absent load view rendered as an EMPTY ROSTER, so the
source read as departed and the move was filed FORCED, inside the classification the primary DV
rests on (found by RE while fixing something else). (4) `AgentLoad.render()` returning
`(load unavailable)` for an empty `dimensions` list — a plausible line, not an error, which passed
a presence check for load. **Note the direction: every one of the four failed toward "fine".** That
is not luck; a default is chosen to let code proceed, and proceeding is what looks fine.
[see §B positive-control rule, P4, grep-the-schema]_

### Every quantity states its PLAUSIBLE RANGE. A number whose expected range is unstated cannot be sanity-checked by anyone, including its author.
The population rule says what a quantity is *over*; this says what it may *be*. **Mechanical check:
each registered quantity declares a range, and the emitter asserts observed values fall inside it.**
A declared range is what binds an entry to its data — a declared *class* does not, because the class
is chosen by the author and never compared against what is emitted.

**Why the range and not the type.** Asserting "rates lie in [0,1], counts are integers" fails
immediately on real registries: seven entries in this project's own registry declare `count` while
emitting continuous scores, because there is no class for a continuous non-rate measure. A per-entry
range works where a type assertion cannot, and it covers currency figures, degrees of freedom and
scores on the same footing.

_Origin (RR, 2026-08-08, and LS's framing): building the card-value counterfactual, `attainable_report`
returns an RWA CURRENCY FIGURE and `s()` returns a SCORE in [0,1]. Using the first where the second
belonged produced per-instance losses of ~1e9 against an oracle of ~8.6, and a "mean loss as % of
oracle" of −12,878,194,064%. **The absurdity is the only reason it was caught** — a units error of
the same shape at 2x rather than 1e8x would have survived, been quoted, and been indistinguishable
from a finding. Every check in the suite passed on it, because the arithmetic was correct. Note the
sibling failure this rule also covers: an "absolute margins for proportions" error priced a DV at
~698/arm from a margin of ±0.011, and it too was a range that was never stated.
[see §B population rule, §A absolute-margins, L6 registry]_

### PRICE THE CEILING OFFLINE BEFORE SPENDING ANYTHING ON A CONTRAST.
Before running a manipulation, compute the BEST POSSIBLE effect it could have: optimal play with
the information against optimal play without it, scored in the true world. Convert to σ and to
n/arm. **If the ceiling is below detectability, no run answers the question and the finding is
about the instrument, not the world.** The computation is offline, costs nothing, and is a
property of the generator rather than of any episode.
**COROLLARY (RE, and it is operational where the rule alone is aspirational): find a POPULATION
WHERE YOU ALREADY KNOW THE ANSWER and check your test gets it right there.** Not "could this have
come out otherwise" in the abstract — a REFERENCE CLASS, which needs no construction and cannot be
built to pass. _Instance: a departure test reported 0 fallbacks and was judged powerless by LS
without either party looking for a population where the answer was known. It existed — 41
SA-only segments, where the worker IS doing SA, matched at 41/41 within 0.1%. That validated the
test and the zero stood. Under-REPORTED and under-POWERED are different failures._

_Origin (LS/RE/RR, 2026-08-08): an entire phase — instrument repair, five methodology rules,
three retracted claims — was spent discovering empirically that the card channel's ceiling is
1.24% of oracle (0.16σ, ~616 episodes/arm), and that TWO OF THE THREE SELECTED INSTANCES had a
ceiling of EXACTLY ZERO. Every one of those facts was computable from the generator before a
single episode ran. **The ceiling is also the cheapest available check on a SELECTION rule:
an admission predicate that admits instances where the manipulation provably cannot act is not
a weak filter, it is a broken one.** And where several channels convey the same underlying fact,
the most complete one bounds them all — so the ceiling is priced ONCE for the study, not once
per cell. [see records/L4/DIRECTIONS_LS.md]_

### Stratifiers must be UPSTREAM of the DV. Admissibility test: is the stratifier predictable from the DV?
Admissible stratifiers are pre-run variables only — assigned cell, seed, task family, swap timestep,
target identity. Whether the manager read, asked, or noticed are all downstream of the response.
**Note the DV's class matters, not the variable's:** the same trace-based stratifier is valid for an
outcome DV and invalid for a response DV, because the causal direction reverses.
_Origin: a commissioned stratifier turned out to be recoverable from the DV in 59 of 60 runs —
`manifested` reduced to "the target still received a post-swap audit", i.e. a coarsening of
`rerouted_share` itself. [§88–89]_

### Consumption claims are between-cell contrasts. The within-run attribution sentence is prohibited in advance.
Never write: _"in runs where the manager read X, allocation was Y."_
_Origin: adopted before the analysis, precisely because the sentence is natural to write and the
stratifier rule is easy to satisfy in the analysis while violating it in the prose. [§91]_

### A mechanism check is not corroboration.
When a second statistic is downstream of the first, report it as the mechanism check it is. Two
p-values side by side read as convergent evidence when they are one effect measured twice.
_Origin: `mean_r_check` +0.173 (p=0.031) sits directly downstream of `rerouted_share` +0.611
(p=0.031) — rerouted audits go to workers who still hold the right method. [§92]_

### Enumerate the arbitrary choices and show the result survives all of them.
Do not test one alternative; test the whole set when it is small.
_Origin: a "lexicographically first" tie-break had 8 distinct selections. The reported estimate was the
MINIMUM of the eight and the sign test was 6+/0− in every one — which is what made it quotable.
[§92, §94]_

### Check arm composition on every recorded covariate before quoting an interval.
_Origin: an announcement-tier contrast where 23/31 runs in one arm carried an observation aid and 0/19
in the other, 24 of 30 runs in one arm shared a single seed (so the bootstrap treated replicates as
independent), and one run carried a different perturbation entirely. The point estimate survived; the
confidence interval did not. [§89]_

### Exclusion beats adjustment at small n, and a range beats a bootstrap over non-exchangeable units.
_Origin: no covariate model is credible at n≈6; a bootstrap over 6–10 non-exchangeable runs recreates
the defect it is meant to fix. [§92]_

---

## C. Claim rules — what you may write

### P4. Write access claims as rendering or as existence, never in the ambiguous form.
```
NEVER   "the manager cannot see X"
WRITE   "ManagerObservation does not carry X"     — rendering; cheap to verify, needs a file:line
   or   "no artifact in the system contains X"    — structural; needs the omniscient-observer test
```
Corollary: **this substrate cannot host a structural observability limitation as a finding.** A harness
logs almost everything; the test will return ROUTING for nearly every observability claim available
here.
_Origin: three load-bearing observability claims retracted in sequence, each true as rendering and
false as existence — and the false broad reading is the one that got built on. [§73, §74, §76, §77c]_

### P11. No build detail is a property of the setting until checked at the merge-base.
_Origin: all three retracted observability claims had this shape. Also: "the manager never messages a
worker" was a fact about the task graph — no run contained a worker-directed reason. [§93]_

### P13. A verdict and its mechanism are separate claims, scored separately.
When a check confirms a prediction, verify that it confirms it **for the stated reason**. A right
answer through an absent mechanism propagates the mechanism.
_Origin: CHECK-3's null was correct and the parser mechanism nominated for it was measured absent —
0.000 parse failures across 218 records. The false mechanism would have sent a future design chasing
extraction robustness. Also fires on labels: `false_precise` was commented "the stale-agent-card case"
and implements a FABRICATED card. [§99, §110]_

### P14. Every kill states its level.
- **idea-level** — an inferential defect surviving any setup change. Kills.
- **setup-level** — a fact about the current build. **Shelves**, with the reviving setup change named.
- **commitment-level** — depends on a stated commitment; stable while it holds, gone if revisited.
  Name the commitment.

Symmetrically: **setup-level support is a prior to re-establish, not a result.**
_Origin: researcher directive — past experiments inform ideas only marginally, because setups are
changeable, and corpus-measured "information" silently favours ideas the old setup could express.
Commitment-level added when an objection (matched-cumulative-history is undefinable under method
substitution) fitted neither box. [§102, §103]_

### Validity conditions do not travel between regimes.
A finding's supporting evidence was generated under specific conditions; when the regime changes, the
finding does not automatically come along.
_Origin: 0/221 false self-reports was established by checking declarations against TOOL CALLS — a
property of the tool-swap regime. Under prompt-level substitution the declaration may not be checkable
at all, so using it would mean verifying a gate with an unverifiable channel. [§101]_

### A manufactured fixture is evidence about itself.
If a phenomenon does not occur naturally in the corpus, manufacturing it changes the scientific object.
Distinguish the manufactured version from the naturally-occurring one and say which you studied.
_Origin: 0/221 means a lying worker does not exist in this system; the honest cells are ABSENT and
STALE declaration, both of which occur naturally, and a fabricated one is a deception study. [§6g, §110]_

### Distinguish the studied variable from the substrate, and controls from ecological claims.
A control needs contrast validity, not realism. Say so in the paper rather than defending it as a
deployment state.
_Origin: the "silent" cell, which carried a bug connotation the framing had buried. [§106]_

---

## D. Source and citation rules

### P6. A source characterisation used as evidence is not quotable until checked at full length.
Nobody inside the conversation catches paraphrase drift, because the drifted version is the one
everyone has been reasoning with. Both early instances were caught only by fetching the source.
_Origin: n=2 at adoption — an elision ("task delegation **and coordination**") and a paraphrase
("balancing observability" → "limiting observability"). Both drifted toward the claim they supported._

### Quote to the END of the sentence, including any trailing citation.
**The tell: a truncation that ends immediately before a parenthetical citation or a subordinate
clause.** This is the mechanical form of P6 and it exists because P6-as-vigilance failed three more
times after adoption.
_Origin: five instances, all eliding the clause that weakened us. n=3 cut "as other works have
investigated (Torrey and Taylor 2013; Cui and Niekum 2018)" — which reversed a claimed gap into an
occupied one. n=5 cut "**Although the transition function allows agents to have changing types,**"
— which reversed a formalism that permits in-place change into a field that supposedly models change
as leave+enter. [§80, §81, §110, §111, §117–118]_

### Verify a fetched paper's first-page title and authors against the citation before reading it.
_Origin: a download from a guessed proceedings URL returned a different paper entirely (a
facility-location mechanism-design paper), caught by title check before any reading. [§110]_

### Read the paper, not the abstract, before conceding or claiming occupation.
_Origin: M3RL's abstract says nothing about replacement; its body has a figure titled "Testing
performance when old team members are constantly replaced by new ones." The abstract would have
misled us in the direction of claiming novelty we did not have — and later, careless phrasing about
the same paper ("mid-run") nearly conceded occupation we did not face. Abstracts mislead in both
directions. [§116, §119]_

### Novelty claims go in the POSITIVE form, with the search documented.
Write "we study X, and here is who holds each neighbouring property", not "no prior work does X". An
empty-intersection claim is a negative over a space you enumerated, and it returns "empty" exactly
when your search missed something (see P7). State databases, queries, and dates so the claim is
auditable.
_Origin: the four-property intersection, adopted as positioning rather than as the contribution
sentence. [§116–118]_

---

## E. Record and provenance rules

### P10. The DV must be recomputable from logs by someone who was not in the room. Run identity is never a release or config name.
_Origin: a run recorded a commit that did not contain its own code; the label `v2.6` named two distinct
runs with different row counts and different results, one of which nothing in the analysis used.
[§6d]_

### Name the glob and the file total on every count.
_Origin: the outputs tree has two layouts. Two people independently counted disjoint halves — 35 files
and 43 files — and argued from them for a session. Full denominator: 78. Also, 18 run-directory
basenames appear in both layouts with different content. [§86]_

### Every printed ordering needs a total sort key; the acceptance test is byte-identical output across ≥2 PYTHONHASHSEED values.
Not "the reported line is fixed" — the whole output.
_Origin: twice. A bare `set` iteration in one script, then `sorted(..., key=-count)` with tied keys in
a script written after the first was fixed. Both flapped only under randomized hashing. [§92, §99]_

### Before adding a named field or label, grep the name across the artifact's full schema.
Two fields sharing a name with different meanings is a recorded failure class. When they collide, the
**effective value** beats the parameter as the single source of truth.
_Origin: fourth instance of the class — `belief_model` added as a CLI parameter beside a manifest field
of the same name holding the effective value. The addition passed both the contract check and the
behaviour check; it failed only against "what else in this file already means this", a check with no
natural trigger. Prior instances: `v2.6`, `full` redefined, silent-as-prose vs silent-as-config.
[§6d, §106, RE audit f758aa2]_

### Annotate in place; never rewrite a record.
The wrong sentence stays visible with its correction attached, so the reader encounters both. A silent
rewrite makes the drifted version un-findable, which is the condition that lets a false reading get
built on.
_Origin: BRAINSTORM is an audit log and is never edited, only annotated — a discipline that paid off
three times in one session. [§81, §118]_

### A correction is not in the record until you have read the corrected text.
Read the commit, not the summary of the commit.
_Origin: a correction was made, reported as adopted, and its pre-correction form remained in the
opening paragraph of the section, stated as load-bearing support — caught only by re-reading the
committed file. The reading rule caught the elision; the transcription step nearly lost it. This is
P10's "recomputable by someone who wasn't in the room", applied to prose. [§117–118]_

---

## F. The substitution instruments

Substitution beats enumeration, always — see P7. Each of these replaces one actor with an idealised
one and asks whether the problem survives.

### P5. The flaky-API test.
Replace the teammate with a stochastic API having a defect rate. If the design is unchanged, you are
studying quality control, not teamwork. Only two residuals have ever passed here: something you can
**tell** the teammate, and something **underdetermined by its outputs**.
_Origin: it retired most of the nine formulations developed and eliminated over §35–74._

### P7. The omniscient-observer test — and why substitution beats enumeration.
Replace the actor with an observer holding complete read access. If the limitation disappears it was
ROUTING; only if it survives is it structural.
The rejected alternative was "name the change that would remove the limitation and show no such change
exists" — **a proof of a negative over an unbounded space, by imagination, which is the faculty that
failed all three times.** A test gated on enumeration returns "no such change exists" exactly when you
are wrong: silent, and correlated with the error.
Scope: it tests observability, not actionability. Do not point it at affordance claims.
_Origin: it reproduces all three retractions as lookups rather than judgements. [§77a–b]_

### The documented-API test.
Replace the newcomer with a complete, accurate, machine-readable specification available free at
arrival. What survives is the study; what dissolves is service discovery.
_Origin: applied to the open-team pivot — capability discovery dissolves, but "is the documentation
true of THIS instance NOW", "what does it do on MY distribution", and "how do I get information the
doc does not carry" all survive. It is what forced the study to be about the information interface
rather than about capability discovery. [§116]_

### The avoidability test, with its threshold.
A research problem justifies study only if it is not dissolved by cheap standard practice (pinning,
local hosting, requesting announcements, pre-deployment evals). **Threshold, without which the test
proves too much: the dissolving practice must be available to the party bearing the coordination
cost, at the time coordination is needed.**
_Origin: the researcher's standard, plus the observation that AHT's own flagship domains fail the
unthresholded version — search and rescue is motivated by "it might not be possible (due to lack of
time or resources) to reprogram the existing heterogeneous robots", and the RoboCup drop-in challenge
is organizational unavailability. A test that rejects avoidable-in-principle rejects the field. [§108]_

---

## G. Process protocols

### The prediction protocol.
Before an experiment runs — or a paper is opened — every participant commits a one-line predicted
outcome privately, and does not revise it afterwards. A wrong prediction is information about the
team's model, including your own.
_Origin: it has paid three ways. It caught that the whole team anchored low on variance; it recorded
that one member alone called the allocation effect; and it made "right verdict, absent mechanism"
visible, which became P13. [§85, §96, §99]_

### Form your own reading of a result before reading anyone else's. Write it down first.
_Origin: standing reviewer procedure; it is what makes an independent check independent rather than a
confirmation of the summary._

### Divergence and evaluation are separate phases.
During generation: no ranking, no critique, no preference signals. Filtering during generation
produces a set that looks divergent and is not.
_Origin: the eight-cluster candidate set, generated blind and evaluated afterwards. [§82, §84]_

### Rank by pairwise comparison, and report which comparisons were close.
The close ones are where the ranking is unreliable, and that is the part the decision-maker needs.
_Origin: A-vs-F and B-vs-E were both flagged unreliable and one of them later flipped on an argument
that did not exist when the ranking was made. [§108–109]_

### Classify every objection: blocker / limitation / optional. Stop pressing once it is on the record and answered.
Blockers escalate. Limitations are documented and the work proceeds. Re-open only on new evidence,
never on further reflection.

### Independent verification is a check on the checker too.
Every characterisation in this project was verified by a second reader, and errors were found in both
directions — including in the reviewer's own passes (M3RL "mid-run"; CIAO "no new axis"; the manager-
model caveat, withdrawn).
_Origin: the M3RL lesson, which cuts both ways. [§119]_

---

## H. Failure classes, indexed by signature

Recognise these by shape, before you know what is wrong.

| signature | class | rules that fire |
|---|---|---|
| a credible number, never a crash | query unit/scope mismatch | P1, P3, name-the-glob |
| a pooled figure with a plausible story | intervention averaged into the total | P1, P2 |
| a filter key that is an effect of the manipulation | collider / DV-derived stratifier | P1, B-stratifiers |
| "the system cannot see X" | rendering vs existence | P4, omniscient-observer |
| a quote ending just before a citation or a subordinate clause | elision drift | P6, quote-to-end |
| a correct-sounding label on a cell implementing something else | mechanism mislabel | P13 |
| a confirmed prediction | mechanism unverified | P13 |
| an idea killed by an old corpus | setup-level treated as idea-level | P14 |
| two fields, one name | same-name-different-meaning | grep-the-schema |
| a figure that moves when you restratify | it will move again | P1, B-composition |
| a null with no power calculation | not a result | P8 |
| a result quoted from a summary | the record was never read | E-read-the-corrected-text |
| a lookup whose default is a legal value | absence rendered as evidence | B-defaults, P4 |
| a condition inside a loop that does not vary with the loop variable | scope-wide predicate applied per item | B-defaults, §B population |
| a fixture on which both candidate predicates agree | the check cannot distinguish what it tests | C-manufactured-fixture, B-positive-control |
| an empty result that agrees with you | never checked | B-positive-control, P1b corollary |
| a quantity whose plausible range nobody stated | units/scale substitution | B-plausible-range, A-absolute-margins |
| a clean N/N on a construct built from a fixed template | the test restates its own construction | B-confirming-test, C-manufactured-fixture |

---

_Fourteen numbered principles, twenty-odd conventions, four substitution instruments. The count is not
the point; the origin lines are. If you are adding a rule, add its failure — and if you cannot name
one, you are adding a preference._
