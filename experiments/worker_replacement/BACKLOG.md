# BACKLOG — post-scope-run phase (opened 2026-08-08)

_The build backlog (S1–S11) is closed and archived at
`archive/BACKLOG_build_S1-S11_closed_20260808.md`. It is superseded, not deleted._

**How to use this file.** Flat ordered list. Work the topmost step that is not `[x]` and whose
`Depends` are all `[x]`. Update the marker in place and commit. **Do not reorder** — the order
is by DECISIVENESS (what invalidates the most work if it fails), not convenience.

`[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked (say why on the line)

---

## Standing rules for every step in this file

**1. THE PRODUCTION-GRADE TEST (researcher directive, 2026-08-08). Before building anything,
ask what a production-grade system would do — so we do not manufacture a problem and then
solve it.** If a real scheduler, queue, or orchestrator would never ship the behaviour we are
about to model, we are studying an artefact of our own construction. If a real system WOULD
have the behaviour, it is fair game. **Write the answer on the step line.** This directive
exists because the dominant loss in the scope run turned out to be a silent permanent
assignment refusal with a status field that reported the work as "ready" — something no
production scheduler would ship, and which cost a week of wrong statements.

**2. NO DRIFT. Re-read the core research problem before starting any step, and say whether
the step serves it.** The question is: **when a worker is REPLACED mid-workflow by an event
the manager did not choose, which sources of information about the newcomer change the
manager's allocation decisions?** The four channels are registry card, the newcomer's
by-product self-descriptions, asking it, and its trace. **A step that improves the
environment but does not serve that question is a detour** — record it and move on. The
authoritative brief is `STUDY1_FOUNDATION.md`; methodology in `METHODOLOGY_RULES.md`.

**3. WHEN AMBIGUOUS, OPEN A TEAM DISCUSSION BEFORE IMPLEMENTING.** Two peers, both expected
to disagree. Ambiguity in a spec is a finding, not an obstacle to route around.

**4. ESCALATE TO THE RESEARCHER** when a commitment is expensive or hard to reverse, when
evidence supports multiple readings the team cannot separate, when what the paper would claim
changes, or when work is being prepared for submission. Not for routine disagreements.

**5. EVERY REPORTED QUANTITY STATES ITS POPULATION AND COMPARATOR, and the population is a
PREDICATE, not a NAME** (`METHODOLOGY_RULES.md` §B). Six failure modes this project shares one
shape and all passed a suite that tests arithmetic rather than meaning.

**6. RUN SCOPE.** 2–3 episodes per cell at this stage; always parallel; `deepseek-v4-flash-0731`
pinned for all roles. Runs only when really necessary — corpus-first. Larger runs need
researcher authorisation.

**7. DUAL REVIEW.** RE implements, LS and RR both review. `[x]` requires the acceptance-check
output plus both reviews under `records/`.

---

## L10 — TWO DESIGNED ENVIRONMENTS, replacing the random pool `[~] BOTH RESEARCHER DECISIONS MADE 2026-08-09. ENVIRONMENTS DRAWN: seed 56 (bank, 5.29%) and seed 37 (corporate, 6.61%) — approved rule, draw seed 20260809 recorded before drawing, both PASS all six properties, all eight controls fire (`records/L10/environment_selection_v1.json`, `select_l10_environments.py`, `check_l10_properties.py`). REMAINING, with RE: remove the segment allowance (ruled — it is ours, not upstream; the gap survives its removal, measured 4.76%/7.11% at cap 9 against 5.29%/6.61% at cap 3), and RESTATE PROPERTIES 2 AND 4, which the removal makes vacuous. Standing checks answered below.`
**Depends:** L9 `[x]` · **Owner:** RE builds, RR attacks the design, LS specs · **Cost: no model
spend to design; the step-2 run is separately authorised.**

**RESEARCHER RULING 2026-08-09: the end product is TWO WELL-DESIGNED ENVIRONMENTS. Two is enough
for quick initial testing.**

> **THE ARGUMENT, and the project already accepted it for one dimension and abandoned it for the
> rest.** `_lattice_from_template` **CONSTRUCTS** the certification table — all 210 possibilities
> enumerated, construction chosen deliberately. **Then the segment mix, ratings and exposures are
> DRAWN per seed.** We hand-designed the part we understood and rolled dice for the part that turned
> out to decide everything.
>
> **An environment is a MEASURING INSTRUMENT, not a sample from a population of interest.** An
> instance with no gap reads zero whatever the manager does — a broken instrument reading, not data.
> **Randomising and then filtering is a wasteful way to get what can be built directly:** admission
> currently discards **25 of 40** for structural reasons unrelated to the gap.
>
> **WHY THE OBVIOUS OBJECTION DOES NOT APPLY.** Designing so a particular MANAGER scores well would
> be fitting the result. **Designing so the GAP EXISTS is calibrating the instrument** — the gap is
> computed with **no manager in the loop** (best possible allocation minus best allocation under a
> wrong belief, both solved exactly), so **there is nothing to fit to.** A thermometer built to have
> range is not a rigged thermometer.
>
> **AND THE TARGET HAS MOVED: zero gaps were the OLD arrangement's problem.** Under partial overlap
> all 60 draws are non-zero (0.03%–6%). **The problem now is that most draws are SMALL** — median
> 2%, long tail toward nothing. **Randomising spends the design freedom on producing weak instances
> and then averaging them.**

**MUST HOLD BY CONSTRUCTION IN BOTH, asserted rather than hoped for:**
1. **Non-zero gap by construction**, not by draw.
2. **`nA < cap`** — the successor keeps a free slot, which is the condition the covered-lie regime
   needs (L9 mechanism).
3. **The card's lie lands on a class an incumbent still covers.** This is what makes the lie cost
   anything at all.
4. **Capacity binds exactly.**
5. **Basel weights untouched.** Realism is the one thing that cannot be traded for sensitivity.
6. **Admission passes — as a POST-CONDITION, not a filter.** It stops being a sieve over draws and
   becomes an assertion that the built instance has the properties it was built to have.

**★ THE SENSITIVITY LADDER BELOW IS SUPERSEDED 2026-08-09 on RR's MEASURED evidence. Retained as
a record; DO NOT BUILD IT.** `card − ignorant` falls monotonically as the ceiling rises (+0.80 →
+0.58 → +0.33), **so ordering instances BY GAP ranks manager policies — maximising the gap makes
IGNORING the card a better policy, and ENV-A would have been the most CONTAMINATED arm rather than
the decisive one.** LS's premise (the gap computation contains no manager) was true; the inference
(therefore ordering by gap is manager-neutral) was false.

**★ AND THE REPLACEMENT AXIS — card-informativeness — IS NOT BEING BUILT AS A CONTRAST EITHER.**
Contested share raises **both** arms together, so the matched-gap span collapses to ~0.05. **That
contrast separates two explanations for an effect we have not established EXISTS, and separating
explanations before establishing the phenomenon is the wrong order.** **Deferred as a STANDING
LIMITATION, not solved.**

**★ SETTLED BUILD SETTING, re-measured in the configuration that will actually ship:**

    arrangement              partial
    amplify_count            ON, targeting the SHARED class
    amplify_divergence       OFF     <- realism is FREE here: both quantities RISE without it
    amplify_irb_priority     OFF
    irb_applicable_fraction  0.89    <- 1.00 rejected: partial use is real AND generation fails
    shared_class_segments    1       <- outside the generability band (segs=3 is worst, 16/20)

    ceiling 3.21%   card − ignorant +0.0810 as a share (~+0.68 absolute)   generation 40/40
    TWO INDEPENDENT PATHS AGREE — RE 3.21% at 40 seeds, RR 3.17% at 20

**THE TWO ARE TWO CONSEQUENTIAL INSTANCES, NOT A CONTRAST** — both realistic, both with a real gap,
**differing enough that a finding on both is not instance-specific.** Which asset class sits in the
sole-need position is the natural axis.

**PRE-COMMITTED AND BINDING: if the effect is undetectable at these settings, that is a FINDING and
NOT a reason to widen anything.**

_(Superseded ladder follows.)_

**THE TWO, AND WHAT THEY DIFFER ON — a sensitivity ladder, not two samples:**
- **ENV-A — maximum gap.** The instrument at full sensitivity. **If a manager shows no effect here,
  that is decisive and ENV-B need not run.**
- **ENV-B — realistic gap.** What an honest study would actually use. **An effect on A but not on B
  is a POWER statement, not a null.**

**★ THE SIX PROPERTIES AS CHECKABLE PREDICATES (LS, 2026-08-09) — prose is not assertable, and
RR's condition is that each must be shown to FAIL before it is trusted to pass. Each row names the
predicate AND the fixture that violates it.**

| # | predicate, computable from the instance | fixture that must make it FAIL |
|---|---|---|
| 1 | `ceiling_vs_stale_card(inst)["ceiling_share"] > 0` | the `current` arrangement at nA=1 — measured 0.000% on 60/60 |
| 2 | `nA < cap`, where nA = IRB-approved segments in the successor-unique class | force `shared_class_segments = cap` |
| 3 | the LIED class has ≥1 post-swap holder **other than the successor** | `current`, where the lied class is the departed worker's sole class |
| 4 | `len(segments) == len(roster_post_swap) * cap` | 8 segments against 3 workers × cap 3 |
| 5 | SA weights and PD floors byte-identical to the committed Basel tables, **and `amplify_divergence` is False** | a perturbed SA table, or the switch left on |
| 6 | `admit(seed, **kwargs)["admitted"] is True` | an instance failing any one of admission's three conditions |

**★ PROPERTY 5's PREDICATE IS RIGHT AND ITS GLOSS WAS WRONG — measured, and the correction is to the
sentence, not the check.** *"Basel untouched"* reads as *the portfolio is untouched*, and it is not.
At the adopted cell, 20 seeds, `amplify_count` on vs off:

    max segments in one class      2.00 vs 2.00   <- NOT concentrated
    identical segment-class order   0/20          <- but the mix IS rearranged

**At `segs=1` the count amplifier does NOT concentrate the book** — forcing one segment into the
shared class is what a round-robin would do anyway. **What it does is REORDER which classes the
segments land in**, because the remaining slots round-robin over `others` with the shared class
excluded rather than over all five.

**ACCURATE FORM, adopted into the spec: THE RISK WEIGHTS ARE UNTOUCHED AND THE PORTFOLIO COMPOSITION
IS ARRANGED.** Far easier to defend than *"Basel untouched"* — **a bank's portfolio composition is a
fact about that bank, not about the framework.**
**And stated positively rather than left to be assumed: the concentration objection that dogged
nA=4 DOES NOT APPLY HERE. Max 2 of 9 segments in any class is an ordinary book.**

**★ PROPERTY 3 CARRIES THE DESIGN, AND RE NAMED WHY IT IS EASY TO GET WRONG: IT IS THE ONLY ONE OF
THE SIX THAT IS A PROPERTY OF A RELATIONSHIP BETWEEN TWO THINGS** — the lied class and the post-swap
roster — **rather than of a single object.** Every other property is checkable from one field.
**Three requires knowing which class the card lies about AND who still holds it, and `current`
satisfies every neighbouring property while failing exactly this one.**

**THE GENERALISATION, and it explains two weeks of blindness structurally: the properties that
DISTINGUISH two designs are more likely to be RELATIONAL than ATOMIC, so a checklist of single-field
properties will not tell two designs apart.** `current` and `partial` are identical on every atomic
property in this table and differ on the one relational one.


_(Superseded by the two paragraphs above; retained as the first form of the point.)_ **Property 3 is the one that carries the design and the easiest to satisfy accidentally** — it is
what makes the lie cost anything at all, and `current` fails it while looking structurally similar.
**Property 5 has two halves and the switch half is the one that would drift**, since it is a
parameter rather than a table.

**THE FIXTURES ARE THE ACCEPTANCE, not an addition to it.** Six passing assertions over a
construction that guarantees its own premises is the structurally-zero residual in a new costume;
**six assertions each demonstrated failing on a named fixture is a post-condition.**


**Acceptance:** both built, both asserted against (1)–(6), gaps reported with their intervals, and
**a stated reason for each design choice that is not "it came out that way."** Both peers' reviews
under `records/L10/`.

**Standing checks, answered.** **(1) PRODUCTION TEST — PASSES.** Every benchmark, fixture and
integration test in production software is **constructed**. Sampling-and-filtering is what you do
when you cannot construct; we can. **We are removing a practice production would not ship.**
**(2) NO DRIFT — it IS the instrument that measures the question.** **(3) AMBIGUITY — the spec above
is the resolution; team discussion is open on the two designs.**

## L9 — THE TEMPLATE DECISION: price partial overlap, then choose `[x] SETTLED 2026-08-09 by the researcher: PARTIAL OVERLAP. Perturbation recorded as a CAPABILITY difference; gate criterion (i) rewritten and runnable again; pool re-derived at records/R2/instance_selection_partial_segs1.json, seeds 26/39/37. Ships UNAMPLIFIED. L3 and L5 unblock.`
**Depends:** none · **Owner:** LS (RE prices, RR attacks the enumeration) · **Cost: no model spend,
but NOT free — it needs a generator change (step 3) that the first version of this step assumed
away.** · **Production test: n/a (design choice).** · **Serves the question: DIRECTLY** — it
decides what "the newcomer is qualified for different things" means, which is the manipulation.

> **PLACED AT THE TOP DELIBERATELY, and this is not a reorder of the existing list.** The order
> in this file is by DECISIVENESS. **L3 and L5 are both `[!]` blocked on this decision**, and L8's
> `_designate_swap_pair` cleanup changes shape depending on which template wins. Nothing below
> this line can be finished before it. Every step below keeps its relative order.

**The researcher delegated this to the team on 2026-08-08**, with guidance rather than an answer:
*keep in mind what problem we are solving and how realistic our setup is.* Their stated preference
is **partial overlap**, explicitly allowing that it may be wrong.

**THE REFRAMING, which the three-way framing in `RESEARCH-CRON-STATUS.md` §1 buried: options 2 and
3 are the SAME option at two different coverage sizes.** Partial overlap is combinatorially
impossible at `COVERAGE_SIZE = 2` (verified by enumeration at 5, 6 and 7 classes). At **3** it is
available in **6,480** admissible templates. **So the preferred design is not ruled out — a sixth
asset class is its price.** *(LS's enumerations have been wrong twice this phase; RR was asked to
attack the 6,480 specifically before anything is built on it.)*

**★ THE WORK BELOW WAS REWRITTEN 2026-08-08 after both peers refuted step 1 as first specified —
its INSTRUMENT and its METHOD were both wrong. Decisions in `records/L9/L9_decisions_LS.md`;
findings at the bottom of this file. The original three steps are preserved there.**

**THE WORK, in this order — the order is a finding, not a convenience:**
1. **Fix the belief model in `ceiling_vs_stale_card`.** It grants the manager the TRUE score on
   any class the card is SILENT about, so it prices the card's lie and not its omission. A card
   is a REPLACEMENT description of a worker. **Acceptance asserts both halves: agreement on the
   current template (30/30, so no published number moves) and divergence on disjoint (0.37% vs
   8.51%).**
2. **Re-derive the admissible set** — two independent reasons now: the ignorant-baseline fault,
   and the fact that selection excludes zero-ceiling instances using the model fixed in step 1,
   which would silently exclude any template whose value lies in the card's omission.
3. **Add the sixth asset class TO THE GENERATOR** — a documented economic clone of an existing
   class (same SA weights, PD floor, rating pool), marked synthetic, **not** the shipping version,
   **no BCBS citation because nothing is transcribed**. Generation raises if a template names a
   class with no segments. **Coverage substitution cannot price six classes** — every instance has
   9 segments over 5, so a sixth class prices free.
4. **Price the size-3 partial-overlap templates on GENERATED instances**, split on carrier count
   (2,160 single / 4,320 two), every σ carrying its mix parameter.
5. **Decide ON RATIO PLUS REALISM — not on an absolute σ.** Disjoint is the FALLBACK: under it
   the stale card retains 23% of its partial-overlap value and is worse than coverage-blind random
   on 7 of 30 seeds — a different specialist, not the same job done by someone else. **On
   detectability disjoint is 10× the current template at matched mix**, so the case against it is
   the validity finding alone.

> **★ SECOND CIRCULAR DEPENDENCY, found 2026-08-08 before it bit (`L9_decisions_LS.md` D11).**
> Every σ quoted here divides by **σ = 0.0768, the PRE-L1 measurement, which must not size a
> suite**. So "does it clear detectability?" needs an absolute σ → which needs L3's bundles →
> **and L3 is blocked on L9.** Same shape as `L2 -> L3 -> L2`.
> **Broken by deciding L9 on the RATIO to disjoint-at-matched-mix, which survives a change of σ,
> and moving the absolute detectability verdict to a step after L3.** Nobody says "clears
> detectability", in either direction, until a post-L1 σ exists.

**Acceptance:** a priced comparison table (template × mix × carrier count → σ and episodes/arm)
under `records/L9/`, a stated decision with its realism argument, and both peers' reviews. **A σ
number without its mix parameter is not an acceptable output of this step**, and neither is a
pooled "size 3" figure that does not split on carrier count.

**ESCALATION TRIGGER, restated for D11 — it must NOT be phrased as "clears detectability", which
is the verdict this step cannot reach:** if the size-3 two-carrier group prices at a small
FRACTION of disjoint-at-matched-mix, the team is choosing between a realistic template with a weak
effect and a strong template that models a different specialist. **That is a trade the researcher
owns, not the team** — it changes what
the paper can claim.

**Do not unblock L3 before this lands.** Pricing costs no model spend and building on an unpriced
template is the failure this whole phase exists to stop — but pricing is **not** free, and saying
it was is what produced the dead step 1 (see the cost line above).

---

## L1 — Load feedback: make the environment stop lying `[x]`
> Acceptance + `L1_review_LS.md` + `L1_review_RR.md` all committed. RR verdict PASS after one
> blocker (criterion (i) passing on a hollow live-path load block) raised and fixed at `5fded1c`.
> **MARKER CORRECTED BY LS, 2026-08-08.** This line read `[x]` against commit `49e5d45`, which
> landed BEFORE the blocking criteria reached RE's inbox — a race, not a claim, and RE flagged
> it themselves. **Against (a)–(e): (a) PARTIAL, (b) NOT MET, (c) NOT MET, (d) PARTIAL,
> (e) NOT MET.** Two independent reasons it cannot be `[x]`: the criteria below are unmet, and
> standing rule 7 requires the acceptance output plus BOTH reviews under `records/`, none of
> which exist. **Do not review 49e5d45 and do not start L2 against it** — L2 re-derives the
> split against the repaired instrument, and an L2 built on a partial L1 measures neither the
> old environment nor the new one.
**Depends:** none · **Owner:** RE · **Production test: PASSES — every one of these is table
stakes in production.** No scheduler ships a status field that reports permanently-refused
work as assigned-and-ready; rejection is signalled to the caller because the caller is the
only party that can re-route; load is observable state.

**Researcher ruling (2026-08-08): give the manager ALL THREE, CONSTANT ACROSS EVERY CELL.**
Not as a manipulated channel. Rationale is study-integrity rather than realism: our question
is whether information about a NEWCOMER changes allocation, and a manager that also cannot see
whether its own instructions took effect is a SECOND, unrelated information failure that
blends into every measurement. No number of episodes separates them.

1. **Truthful execution state on the board** — `not started / running / done`, replacing a
   `ready` that currently asserts a falsehood for work that can never run.
2. **Load visible** — per-worker count of segments held against capacity.
3. **Refusal signalled** — when an assignment is refused, the manager is told, at the time.

**Acceptance (mechanical):** (i) a script asserts the manager's rendered context contains
execution state, per-worker load, and any refusal that fired, for every timestep of a machinery
episode; (ii) the same script asserts the three are **present in identical form across all six
cells** — a load signal that varies by cell is an uncontrolled channel correlated with
over-concentration, which correlated with regret at r=0.93 in the scope run; (iii) the
comparability module gains the assertion.

**Expected consequence, stated in advance so it is not read as a surprise:** the dominant
loss term should SHRINK, possibly a lot. That is the point. What remains is a smaller, cleaner
allocation problem that the four channels actually address.

### L1 BLOCKING CRITERIA — pre-registered by RR before the code exists, LS-verified
_On the record before implementation so neither the criterion nor the build can be written
around the other. (a) verified independently by LS with two corrections noted._

**(a) DO NOT BUILD THE REFUSAL SIGNAL FROM THE EXISTING EVENT FIELDS — THEY SAY THE OPPOSITE
OF THE TRUTH.** `assignment_deferred` (`engine.py:862`) carries `agent_current_task_count`,
`agent_max_concurrent`, `agent_available` — all CONCURRENCY quantities. The dominant refusal
cause is the SEGMENT ALLOTMENT, which none of them describes. Measured over all 580 events in
the 18 R2 bundles:

```
(count=0, max=1, available=True)  335   <- ALLOTMENT refusals by elimination (the permanent ones)
(count=1, max=1, available=True)  245   <- concurrency refusals (transient)
```

`can_handle_task` has exactly three refusal branches — unavailable / concurrency / allotment;
`available=True` rules out the first and `0 < 1` rules out the second. **So at the moment of a
PERMANENT refusal the event asserts the worker is idle, available and below cap. A signal read
through from these fields tells the manager the exact reverse, on 58% of refusals and on all
the ones that matter.** The repair must carry the ALLOTMENT state (`segments_used /
segment_capacity`) and an explicit refusal-REASON enum.
_LS corrections to RR's figures, substance unchanged and slightly strengthened: the 335 are
322 segment + 13 non-segment tasks (not all segment); the most-repeated triple is 20 refusals
(`run_cellU_seed23`, `w_4f4d0d`), not 14. The 23-triples-at-≥5 figure reproduces exactly._

**(b) TWO CAPACITIES WITH OPPOSITE RELEASE SEMANTICS MUST NOT SHARE ONE DISPLAY.**
`max_concurrent_tasks_per_worker=1` RELEASES on completion; `segment_capacity=3` NEVER releases
(`segment_task_ids` is added to in `execute_task` and never pruned — a per-episode lifetime
allotment). A line reading `w_X: 3/3` carries the universal scheduler convention that finishing
frees a slot, which is false here. **Both numbers present, distinguishable, and non-release
visible in the RENDERING, not merely true in the code.**
_Production test, split per RR: PASSES for the MECHANIC — a fixed per-person allotment inside
an engagement is ordinary (WIP budgets, per-reviewer caps) and finishing one does not earn a
fourth. FAILS for the naive DISPLAY. The rule does not bless whatever renders the allotment._

**(c) `not started` MUST NOT ABSORB `refused`.** Post-deferral the engine sets `agent = None`
and the task stays READY, so under a `not started / running / done` vocabulary a permanently
refused task renders as `not started` — true, and indistinguishable from never-assigned. If
refusal is only a point-in-time notification, a manager reading state at t+5 is back where it
started. **Refused-and-awaiting-reroute must be PERSISTENT BOARD STATE.**

**(d) ACCEPTANCE (ii) IS NECESSARY, NOT SUFFICIENT.** Two ways it passes while being wrong:
(1) **capability re-leak** — if the load or refusal line renders any worker descriptor beside
the id it reintroduces successor capability into cells where the card is stale (second
occurrence of the semantic-agent-id leak); check identity AFTER agent-id substitution and
require NO capability text at all. (2) **the stripper trap** — cell U legitimately differs, and
a checker stripped enough to stop flagging U is stripped enough to hide a real difference;
**publish the strip list with the result**, as in R2 items 6/7.

**(e) THE ALLOTMENT PREDICATE IS NAME-BASED, AND IT SILENTLY KILLED A MANAGER REMEDIATION.
Found by resolving an LS/RR disagreement in which BOTH classifications were correct.**
RR classified deferrals by `task.name.startswith(SEGMENT_TASK_PREFIX)`; LS classified by
membership in the bundle's `index.segment_task_ids`. RR got 335 segment deferrals, LS got
322 + 13. **Both are right — for different predicates — and the 13 that separate them are one
task:**

```
'Risk-weighted assets — seg_08 standardised recalculation'
  manifest n_tasks=16, board=17  ->  MANAGER-CREATED during the episode
  NOT among the 9 scored segments (absent from index.segment_task_ids)
  name matches SEGMENT_TASK_PREFIX -> can_handle_task (finance_env.py:161) charges it
  to segment_capacity anyway
  assigned to w_b391c0, who had already spent its 3  ->  REFUSED 13 TIMES, never ran
```

**So the manager attempted a remediation — a standardised recalculation of a segment — and the
environment permanently refused it because of how the task was NAMED, and never said so.**
That is a manager ADAPTATION defeated invisibly, which is closer to the study's subject than
anything the allotment mechanism was built for. Manager task-creation occurs in **4 of 18
episodes**; exactly 1 collided with the prefix, so this is rare, real, and cheap to fix.

**THE NATURAL EXPERIMENT (RR, LS-verified) — the same act, two names, opposite outcomes.**
Two of the four created tasks are the SAME remediation: the manager judging a segment wrong and
ordering a recomputation.

```
cell0_seed23  'Risk-weighted assets — seg_08 standardised recalculation'  prefix=True   REFUSED 13x, never ran
cell0_seed36  'Recompute RWA: seg_02 (bank IRB) and seg_07 (mdb IRB)'     prefix=False  COMPLETED
```

Nothing about the work differed; **the environment's response was determined by the display
string.** This is stronger than the refused case alone because it rules out "the remediation was
ill-formed" — the identical act succeeded one seed over.

**SCORING IS CLEAN — NO RETRACTION IS OWED ON ANY EXISTING FIGURE (verified).** `parse_detail`,
`allocation`, `reports` and `deliverables` are all keyed off `index.segment_task_ids` (9 entries
in every bundle), so a manager-created task cannot be read as a segment answer whatever it is
called. **METERING is the inconsistent part:** the prefix-matching remediation would have been
charged to segment allotment had it run; the one that DID run was charged nothing.

**LATENT HARM — did not fire here, one seed away, and L1 makes it MORE likely (RR).** A
prefix-matching created task assigned to a worker with a SPARE slot would execute and consume
one of the three the oracle assumes — shrinking the worker's feasible set below the oracle's
model, so regret is charged against an optimum for a problem the manager was not solving. **That
is verbatim what the C=3 docstring says the mechanism exists to prevent, arriving through the
opposite door.** It did not fire only because the single collision landed on a worker already at
3/3 and was refused. **And L1 raises the rate of the triggering behaviour: a manager that can
finally see load, execution state and refusals is better equipped to REACT, and task creation is
what reacting looks like. So (e) must land WITH L1, not after it.**

**Production test: FAILS.** No production system meters a work budget by string-matching a
task's display name — task class is an explicit field, because names are display text and get
edited. **L1 must make segment identity EXPLICIT rather than inferred from the name**, or, if
the prefix rule is kept, the manager must be told that a task it creates counts against the
allotment. Note this also means the ENGINE's notion of "segment" and the SCORER's differ
today, which is its own latent defect regardless of L1.

**RR objection CHECKED AND DROPPED, recorded because it constrains the design:** refusal
signalling does NOT leak coverage. `can_handle_task` refuses only on availability, concurrency
and allotment — an out-of-scope segment is ACCEPTED and answered badly (SA fallback), never
refused — and `segment_capacity` has no per-worker override, so predecessor and successor are
identical and refusal cannot distinguish them. Load is genuinely information about the
manager's own actions, not a fifth channel about the newcomer.

**LIMITATION — σ IS STALE AND MUST NOT SIZE ANYTHING (RR).** `σ = 0.0768 (df=12) → n ≈ 8–12/cell`
was measured on the PRE-repair distribution, which L1 is designed to destroy. Removing a large
common loss term can cut σ or leave a smaller mean with comparable spread — it is not
conservative in a known direction. **Re-estimate σ post-repair before it authorises any suite
size, and carry the χ² interval with it (df=12 is roughly a 5.3× span on n).**

---

## L7 — Manager ACTION STREAM + the behavioural DV, defined over assignments `[x]`
> Acceptance + both reviews committed; RR verdict LIFTED after three blockers. **B.1 was a ~7x
> upward bias in the primary DV that MY review passed** — an episode-wide terminal set tested
> inside a per-step loop, invisible on a machinery episode with zero segment completions.
> Fixed at `22a1604`; the acceptance now runs on an episode where segments DO complete.
**Depends:** none · **Owner:** RE · **LANDS WITH L1** (RE's argument, accepted: L1 makes the
manager more able to ACT, action is what we would be newly logging, and shipping separately
buys a round of episodes where the manager reacts more and we still cannot see it).
**Production test: FAILS today** — no orchestration system logs rejected assignments and not
accepted ones; the assignment is the primary audit record. **Serves the question:** directly —
four of the brief's five failure modes are manager behaviours and are currently UNMEASURABLE.

**LS RULING on RE's three conditions (all accepted) plus two corrections and one new blocker.**

1. **ACCEPTED — separate FORCED from DISCRETIONARY, committed before implementation.** Verified
   independently: **33 moves, 24 forced (73%), 9 discretionary**; per-bundle forced is exactly
   {0, 4}; cell U is 0/0 and that is STRUCTURAL (no departure), not a finding. A naive
   `rerouted_share` over both would be an un-mixing failure inside the metric proposed to
   replace one.
2. **ACCEPTED — the denominator predicate is written first.** Sharpened: *segment tasks that,
   at the moment of the manager's action, were assigned to an agent STILL ON THE ROSTER and not
   yet terminal* — the set where leaving it alone was a legal option. Excludes work held by a
   departed agent, initial assignments (not reroutes), and completed work.
3. **ACCEPTED — the apply-site event records REQUESTED and APPLIED.** `AssignTasksToAgentsAction`
   skips missing/terminal/unknown-agent pairs into a `skipped` list nobody logs; without both,
   requested-vs-applied becomes the next un-mixing failure.

**CORRECTION 1 — RE's "`rerouted_share`: zero hits, confirmed" is FALSE, and it is my error
reproduced.** Positive-controlled recursive grep: **19 hits across FOUR files** —
`check_variance.py`, `check_announcement.py`, `check_announcement_clean.py`, and RE's own new
<!-- citation-check: superseded --> _(those three were deleted in the 2026-08-08 cleanup; named here as the historical record of where the DV went.)_
`check_reroute_recoverability.py`. RE confirmed my false claim independently, which makes this
the **third** null-without-positive-control in one week and the first where the error
PROPAGATED between us. The true finding stands and is worse: the DV, its variance estimate and
a `!! PRIMARY DV ABSENT` banner were all built, then dropped by the revamp — the alarm lives in
the pipeline nobody runs.

**CORRECTION 2 — DO NOT DISCARD FORCED MOVES. Their DESTINATION is a routing decision, and it
carries the most brief-relevant signal we hold.** Measured:

```
FORCED         -> successor 22 · -> an incumbent  2
DISCRETIONARY  -> successor  1 · -> an incumbent  8
```

**Near-opposite distributions.** Handing the departed worker's queue wholesale to the newcomer
IS the brief's §7 failure mode #1 — *allocating as if the predecessor remained* — and
discarding forced moves would discard 24 of 33 decision points, plausibly the most
channel-sensitive ones. Keep both populations; analyse forced moves on DESTINATION, never sum
them with discretionary.
_Checked and cleared: the manager is NOT told to do this. The swap message is neutral
("removed w_8fcf6e / added w_e350ed") and no reassign/inherit/replace instruction appears in
its context. So the 22/24 is a manager choice, not instruction-following._

**NEW BLOCKER — THE CHOICE-SET CHECK, before any destination claim is trusted.** At t_swap the
predecessor holds 4 segments; the successor arrives EMPTY with 3 free slots while incumbents
hold ~5 of 6 capacity. **So capacity alone may make the successor the only legal destination
for most forced moves, and 22/24 would then carry no information about channel use.** Required
before the DV is used: **for each forced move, the number of CAPACITY-LEGAL destinations at
that timestep.** If it is usually 1, destination is not a decision and the metric must
condition on choice-set size. Corpus-first, zero run spend, answerable from the 18 bundles.

**CHOICE-SET BLOCKER — ANSWERED AND CLEARED (RE `4d7137e`, LS-verified). The worry INVERTS.**
**All 24 forced moves had 3 capacity-legal destinations; ZERO had the successor as the only
option.** So destination was a genuine decision and correction 2 stands. **But the reason is
TIMING, not generosity:** forced moves cluster at t3–t6 *before capacity binds*; discretionary
moves run to t21 once the team is nearly spent, with legal sets of **1 or 2, never 3**.
**So choice-set conditioning is required on the DISCRETIONARY side, not the forced side where I
expected it.**

**THE FINDING UNDERNEATH, and it is the cleanest illustration of what L1 repairs.** Verified:
in `cell1_seed23`, task `…979cb8e6` was moved `w_3330c6 → w_b391c0` at **t19** and
`w_b391c0 → w_3330c6` at **t20** — bounced back to where it started, in consecutive timesteps,
**between two workers both at their segment allotment, while `w_0e59e6` sat with a free slot**
(final board: 4 / 3 / 2). It could not run either way. **That is pre-L1 blindness appearing
INSIDE the population the DV treats as manager judgement — so discretionary moves measured
before L1 are partly noise.**

**RE'S PRE-REGISTERED PREDICTION, on the record before L3:** the bounce pattern changes after
L1. Falsifiable, and it is a prediction rather than a hope. LS and RR predictions to be
committed under the standing protocol before L3 runs.

**LIMIT, RE's, reported rather than smoothed:** choice sets are **RECONSTRUCTED, not logged** —
capacity state per timestep was never recorded pre-L1, and start-timestep attribution is
nearest-preceding-observation, so a one-timestep misattribution moves a count by one. **That
makes 1-vs-2 the fragile case, which is exactly where the discretionary population sits.** The
forced result (all 3) is robust to it; the discretionary legal-set sizes are not. From L3 on
the reconstruction is unnecessary.

**LS RULINGS on the DV definition v1 (`records/L7/rerouted_share_definition_v1.md`).**

- **Q1 — TASK denominator, not task-timestep.** RE's reading is right and the reason is stronger
  than plainness: an OPPORTUNITY denominator is confounded with EXECUTION SPEED — a task that
  completes quickly offers fewer chances to move — which reintroduces exactly the
  execution-into-allocation mixing this DV exists to remove.
- **Q2 — accepted as proposed.** A task with both a forced and a discretionary move: in the
  denominator, numerator for the discretionary move only, and separately present in the forced
  destination table. One task in two analyses, never summed across them.
- **Q3 — both computed; the ≥2-legal-destinations one is PRIMARY for any channel claim**, since
  a move with one legal destination is not a choice and cannot evidence channel use. The
  unconditional share is descriptive. **At n=9 discretionary (6 after conditioning) NEITHER
  supports a claim, and that sentence travels with the numbers wherever they appear.**
- **Q4 — ACCEPTED, and stronger than the argument RE made for it. Pre-L1 bundles are NOT a
  baseline for EITHER population.** RE argued from a 22% bounce contamination of the
  discretionary moves. I tested whether the argument spares the forced population and
  reported **24/24 and 9/9 moves occurring after a refusal the manager could not see, framed as
  a search for an exception that came up empty. RE CORRECTED THAT REASONING AND THEY ARE RIGHT:
  the test COULD NOT HAVE FAILED.** Every bundle has invisible refusals from t0 or t2 (0 of 18
  bundles have none) and the earliest move anywhere in the corpus is t3 — **so the test is
  satisfied BY CONSTRUCTION and the 24/24 figure has no discriminating power. It must not be
  quoted as evidence.** The RULING is unchanged and the correct statement is STRUCTURAL rather
  than empirical: **in this corpus no clean pre-L1 sub-population is POSSIBLE**, not merely none
  observed. **Consequence for my own
  earlier framing: the 22/24 forced-to-successor pattern stays a DESCRIPTIVE record of what the
  broken environment produced — it is not a "before" measurement**, and I called it our most
  brief-relevant signal before checking that.

**Accepted from the doc without change:** unit is the task counted once (so 29-vs-33 cannot
recur as a share above 1); forced moves stay in, analysed on destination; choice-set
conditioning on the discretionary side; DV computed on APPLIED with requested-but-skipped
reported beside it; cell U's structural zero carries its sentence wherever the table appears.
**And §7's limit is right and load-bearing: this measures BEHAVIOUR, not correctness, a move is
consistent with using any channel or none, and attribution still needs the channel-pull record.
The regret decomposition stays as the outcome measure; neither substitutes for the other.**

**Reading limit, standing:** 3 episodes per cell. No contrast verdict in either direction.
Cell 3's zero moves across three seeds is not a result.

## L2a — the split CODE against the repaired schema `[x] (all three blockers closed and RR's verdict LIFTED after re-running all six sub-cases. B2 resolved BETTER than the blocker asked: an EMPTY parse_detail is not raised on -- a machinery run has no deliverables -- but is marked uninterpretable in the record, and interpretable_counts() raises for any consumer that reports those counts. One recorded limitation in the review file.)`
**Depends:** L1 · **Owner:** RE · **Production test: n/a (analysis).**

> **★ CIRCULAR DEPENDENCY IN MY OWN BACKLOG, found 2026-08-08 and fixed here.** L2 says
> "re-derive the split against the REPAIRED instrument"; L3 says `Depends: L2`. **But the
> repaired instrument only produces bundles once L3 RUNS — so L2 as scoped cannot be done
> before the thing that depends on it.** The next cron firing would have hit this. Split:
>
> - **L2a — the split CODE, re-derived against the repaired schema, acceptance-tested on a
>   zero-API machinery episode.** Buildable now, no run spend, same pattern as L1/L6/L7.
>   **This is what `Depends: L2` on L3 actually needs.**
> - **L2b — the split NUMBERS.** Not a separate step: it is part of L3's analysis, computed on
>   L3's bundles. Folded into L3 and removed as an independent gate.
>
> L3's dependency is hereby **L2a**, not L2.

The four-way split (`never-assigned / assigned-but-unexecuted / executed-but-unparseable /
parsed-and-wrong`) is now measured against an environment where the manager can see the
constraint. Re-derive it, and state each population as a PREDICATE per standing rule 5.

**Acceptance:** the split prints with an explicit predicate per bucket and its comparator;
`assigned-but-unexecuted` is expected near zero and a non-zero value is a finding, not noise.

---

## L8 — Retire the display-name join, and log renames `[x] (all four sites converted; null holds 18/18 and the control was BUILT FIRST and fired against the code as it stood, 9 hits -> 8. Standing rule 7 satisfied: acceptance output + L8_review_RR.md + L8_review_LS.md. One non-blocking finding open: task_renamed fires on new_name being SET rather than on the name CHANGING.)`
**Depends:** none · **Owner:** RE · **Production test: FAILS today** — no system keys a join on a
mutable display string, and none mutates a name without recording the previous value.
**Serves the question:** indirectly — it protects joins that every published number passes through.

Four sites still join on `f"Risk-weighted assets — {sid}"`. **The manager demonstrably renames
tasks** (8 of 9 `refine_task` requests set `new_name`), and one observed rename —
*"Aggregate risk-weighted assets"* — is one editorial decision from matching the segment prefix.
**Correct for 18 episodes by luck**: no rename has yet hit a segment.

1. **Three ANALYSIS sites → `index.segment_task_ids`** (`finance_scope_report.py:204,:332`,
   `finance_logging.py:472`, `finance_fabrication.py:230`). These run over bundles we publish
   from — highest priority.
2. **`RefineTaskAction` records `name_before`/`name_after`, emitted on the NAME change.** Today
   `record_run_event("task_refined")` sits inside `if self.new_description:` while the name
   mutates outside it, **so a rename that changes no description emits NO EVENT AT ALL** — the
   thing that would tell us a join silently missed is the thing that is not logged.
3. **The dry-run site last** (`run_finance_episode.py:133`) — machinery only, never a live run.

**Not a blocker on anything:** no display-name site executes during a live episode.

> **★ STANDING CHECKS, answered 2026-08-09 as required before implementing.**
>
> **1. PRODUCTION-GRADE TEST — FAILS TODAY, so the fix is warranted and we are NOT manufacturing a
> problem.** No production system keys a join on a mutable display string, and none mutates a name
> without recording the previous value. A real orchestrator joins on IDs and emits a rename event
> carrying both values. **We are removing a behaviour production would never ship, not adding one.**
>
> **2. NO DRIFT — it serves the question by PROTECTING THE MEASUREMENT, not by improving the
> environment.** The primary DV is defined over ASSIGNMENTS, and these four joins are how segments
> are matched to tasks in every analysis path we publish from. **A silent join miss corrupts the DV
> directly.** That is inside the rule rather than the detour it warns about.
>
> **3. AMBIGUITY — none.** The three analysis sites go to `index.segment_task_ids`
> (`finance_split.py:90`, already present); `RefineTaskAction` records `name_before`/`name_after`;
> the dry-run site last. No team discussion needed.
>
> **VERIFIED STILL LIVE 2026-08-09** — the four sites survived the rebuild and the renames:
> `finance_scope_report.py:204,:332` · `finance_logging.py:472` · `finance_fabrication.py:230` ·
> `run_finance_episode.py:133`.
>
> **★ ONE ADDITION: item 2 touches a CORE file** (`schemas/execution/manager_actions.py`), **so it
> needs a `CHANGED.md` entry with it** — not after it. That file is the deviation record and it has
> already been caught trailing the code once this phase.

---

## L3 — Re-measure at scope: does an effect appear once the instrument is honest? `[!] BLOCKER MOVED, NOT CLEARED (LS, 2026-08-09) — now blocked on L10, which is blocked on the researcher. The ORIGINAL blocker is satisfied.`
> **ORIGINAL BLOCK (RR, accepted by LS), NOW SATISFIED — retained as the record, not as the
> current state.** As scoped this re-measures the same regret aggregate that produced four
> retractions, without the behavioural DV. *"Unblocks when the manager action stream and the
> assignment-defined DV land with L1."*
>
> **★ THAT CONDITION IS MET: L1 `[x]` and L7 `[x]`, each with its acceptance file and BOTH peer
> reviews committed under `records/` — verified, not read off the markers.** The marker sat stale
> until 2026-08-09, asserting a blocker that had been cleared.
>
> **THE CURRENT BLOCKER IS DIFFERENT: this step costs 6 cells x 2–3 seeds and needs the two
> DESIGNED ENVIRONMENTS from L10, which is blocked on two researcher decisions (the selection rule,
> and the allotment contamination).** A stale marker naming the wrong blocker is worse than no
> marker: it tells the next reader to go and check something already done.
**Depends:** L2 · **Owner:** RE · **Cost:** 6 cells × 2–3 seeds, flash · **Production test: n/a.**

**Prediction protocol before this runs (standing rule, spec §5):** LS commits a one-line
predicted outcome, then RE and RR each DM theirs privately. Compare only once all three are
in. If all three agree, state what the run adds beyond confirmation — if there is no good
answer, shrink it to a smoke test.

**Acceptance:** bundles committed under `records/L3/`; the split from L2; per-cell descriptives
with the NO-ORDERING rule attached (the scope run's cell ordering was confounded with
completion rate at r=0.93 and with a concurrency block).

**Reading limit:** at 2–3 episodes per cell there is NO contrast verdict in either direction.
This measures whether the DV has become measurable, not whether a channel works.

---

## L4 — Drift check against the core research problem `[x]`
> Both reviews committed. RR verdict: the check is sound, its two new findings are real, and
> D1's headline evidence was corrected (see the findings log).
**Production test:** n/a (analysis). **Serves the question:** it IS the drift check.
**LS reading committed: `records/L4/drift_check_LS.md`.** Two findings NOT previously raised by
anyone: **D1 — the brief's PRIMARY DV (`rerouted_share`) is neither implemented nor loggable**
(no event records an assignment; only refusals are logged; we measure a regret decomposition
instead), and **D2 — the measurement vocabulary has drifted from the brief's five-mode manager
FAILURE taxonomy to an EXECUTION-STATUS taxonomy**, none of whose categories appear in §7.
**Depends:** none — run it EARLY and again before any writing · **Owner:** LS

Re-read `STUDY1_FOUNDATION.md` against what the study now measures and write the delta.
Specific things to check: (i) does the four-property novelty intersection still hold; (ii) is
the load-feedback repair inside or outside the studied object; (iii) has the DV drifted from
"allocation decisions" toward "instrument health"; (iv) does the surviving claim still answer
the question the brief asks.

**Acceptance:** `records/L4/drift_check_LS.md`, reviewed by RR. A drift finding is not a
failure — an unrecorded drift is.

---

## L5 — S10 and S11: reassess, do not resume blind `[~] REASSESSED 2026-08-09. The `[!]` was STALE: it said "blocked pending L1" and L1 is `[x]`. S10 is NOT retirable -- it is the VALIDITY CONDITION for the whole current design, and its blocking objection ("PERMISSION-not-INFORMATION") is now the ADOPTED framing. Answered corpus-first at n=3, 3/3 fallback, zero spend -- see the findings log. S11 stays blocked: depends on S10 at n>=20 and needs run authorisation.`
**Blocked pending L1.** S10 (fabrication linchpin probe) was blocked on the coverage-repair
ruling, which R1 resolved; S11 (gate pair) never started. **Both were specified against an
environment that lied to the manager.** Do not resume either from the archived backlog without
re-reading its acceptance criterion against the repaired environment. Reassess when L1 lands.

---

## L6 — §B enforcement: population predicates in reported quantities `[x] (verdict WAS lifted in RR's file -- RESOLUTION section, both blockers checked against code, "L6 passes". The file's HEADER still said "TWO BLOCKERS", so it contradicted itself depending on where a reader stopped; fixed by a pointer at the top rather than a rewrite, 2026-08-09.)`
> _Marker corrected 2026-08-08: this line still read "NOT implemented" after the build, the LS
> review and the blocker fix — the same stale-marker class as the L1 race. The design discussion
> below is retained as the record of how the spec was settled._

**Production test: PASSES, strongly.** Every production metrics system requires a metric name
plus labels; an unlabelled counter is treated as a defect, not a style question. Enforcing that
a reported quantity names its population is standard observability, not an invention of ours.

**Serves the question — INDIRECTLY, and stated honestly:** L6 does not measure whether channels
change allocation. It protects every quantity that will answer that. **Six failure modes and
four retracted claims in this project share exactly this shape**, and all of them passed a
suite that tests whether numbers are COMPUTED right. Not a detour under rule 2 — the rule's
"improves the environment but does not serve the question" case is about environment features;
this prevents false answers rather than adding capability.

**AMBIGUITY — REAL, so this is circulated rather than implemented (standing check 3).**
Measured against the committed `records/R2/scope_report.json`:

```
RATE-shaped quantities   56 emitted values / 22 distinct KINDS   54 of 56 have NO population or comparator beside them
COUNT-shaped quantities 357 emitted values / 106 distinct KINDS  348 of 357 have none
```

**LS PROPOSAL, for RE and RR to accept, amend or reject:**
1. **Enforce at the KIND level, once per quantity kind — not per emitted value.** 22 vs 56 for
   rates; 106 vs 357 for counts. A predicate attached to each of 18 identical `regret_share`
   values is noise; attached once to the kind it is a contract.
2. **Rates and shares: population predicate AND comparator both MANDATORY.** A rate without its
   comparator can carry the wrong SIGN — already paid for, when 3-of-105 read as manager
   failure and meant the reverse.
3. **Counts: population predicate MANDATORY, comparator explicitly nullable WITH a reason.**
   Counts cannot be exempt: `n_unreadable` was a COUNT whose population was wrong, and it is
   the defect that opened this phase.
4. **Mechanism: a registry keyed by quantity kind; the emitter REFUSES to serialize a numeric
   leaf whose key does not resolve to a registered kind.** Fails loudly, same discipline as
   `extra='forbid'`.
5. **Positive control REQUIRED** — the check shown FIRING on a report containing an
   unregistered quantity, per §B's own null rule.

**THE OPEN QUESTION I AM NOT SETTLING ALONE: scope of the first pass.** All 106 count kinds is
a substantially bigger job than 22 rate kinds. **My recommendation: rates first, counts second —
EXCEPT that any count already implicated in a retraction (`n_unstaffed`, `n_unreadable`) lands
in the first pass regardless.** RE owns the cost estimate; RR owns whether a partial pass is
worth having at all, since a half-enforced rule may read as a fully-enforced one.
**Depends:** none · **Owner:** RE · **Production test: PASSES — labelled metrics with explicit
denominators are standard observability practice.**

Make the rule mechanical rather than aspirational: every quantity a report prints carries its
population predicate and its comparator. `__unstaffed__` would have failed this on day one.

**Acceptance:** the scope-report emitter refuses to print a rate without both fields.

---

## Findings log — append here, newest last

_Everything the phase establishes goes here as it happens, so the researcher can read one file
on return. One line per finding, with the commit. Retractions stay in the record as
retractions._

**From the scope run and the review chain that followed it (2026-08-07/08):**

- **The scope run's headline conclusion was WITHDRAWN.** "Design fails on effect / the movable
  quantity ≈ 0" was computed on a broken metric. Correct statement: **it has not been
  measured.** (`fc34919`)
- **The defect:** `allocation` was derived from COMPLETIONS, so work the manager assigned and
  the engine never ran collapsed to `__unstaffed__` — a label asserting the manager never
  staffed it. One line of derivation; everything downstream inherited it. (`2dbac1d`)
- **What the 22 "unrouted" segments actually were:** assigned to real workers, then
  PERMANENTLY REFUSED — 20 consecutive refusals to the horizon — because the assignee had
  spent its C=3 capacity. The horizon was never binding (last completion t5–t15 of H=22).
  580 `assignment_deferred` events; ZERO manager-visible signal. (`f64cc2f`, `397a377`)
- **The manager routes BY COVERAGE and pays in capacity.** 54 of 58 IRB segments piled on
  over-loaded workers are ones that worker covers; of the capacity-refused segments,
  **0 of 19 coverage-relevant ones are mis-routed.** The capacitated optimum accepts ~1
  avoidable coverage mismatch per instance as the price of feasibility; the manager accepts
  0.17 and breaks the cap instead. (`e88efb0`)
- **Surviving claim (RR's wording + RE's regime qualifier):** *In a regime where capacity binds
  exactly, coverage information alone cannot address the dominant allocation error, and
  coverage-optimal play would itself violate capacity. The channels are ORTHOGONAL to the
  dominant loss term, and the input that would address it — LOAD — is carried by none of them.*
- **Withdrawn along the way, kept as retractions:** LS's anti-correlation claim (an argmax
  establishes a CONFLICT, not a DIRECTION); LS's "6× more coverage-faithful" (compares a
  feasible allocation against an infeasible one); LS's "a rostered worker got zero segments"
  (false — that worker was never in the run; `roster_post_swap` is counterfactual in cell U);
  RR's parse-failure mechanism and 13.6% figure; RR's pooled 9.5% enrichment (two populations).
- **σ measured 0.0768 (df=12)** — the design is NOT noise-limited; n≈8–12/cell is affordable.
- **L4 DRIFT CHECK — CORRECTED (LS finding, RR correction, LS-verified).** My headline
  evidence was FALSE: I wrote that `rerouted_share` appears nowhere (zero hits) from a
  non-recursive grep whose every visible hit was `worker_replacement` in import paths. It has **19
  hits**. **I asserted a null with no positive control — the rule RR wrote and I committed to
  §B two days earlier.** The true finding is worse: `rerouted_share`, its variance estimate,
  AND a loud `!! PRIMARY DV ABSENT` banner were all BUILT, then dropped by the finance revamp —
  **the alarm never fired because it lives in the pipeline nobody runs.** A silent regression
  past our own tripwire. Restoring it as-is would reinstate the root cause: the old DV is
  COMPLETION-DERIVED, so target work that never executes leaves both numerator and denominator
  and the share is biased UPWARD exactly in the capacity-refusal regime — the same defect as
  the `allocation`-from-completions bug. **My "the aggregate explains the week" story is
  RETRACTED as over-fitted**: RR tested it against all six retractions and only one is
  DV-shaped, and that one would have happened identically under the brief's DV. The common
  cause is name-vs-predicate, checked late. **D1 and D2 MERGE into RR's stronger version: the
  manager's behaviour is not recorded ANYWHERE — no action stream, `create_task` unlogged, the
  only assignment-shaped event a refusal — so everything we hold is the environment's RESPONSE
  to the manager.** Four of the brief's five failure modes are manager behaviours and are
  therefore UNMEASURABLE, not merely unmeasured. _(superseded original:_ the brief's primary DV
  `rerouted_share` is **neither implemented nor recoverable from the bundles** — the manager
  holds `assign_task`/`assign_tasks_to_agents` but **no event records an assignment**, only
  `assignment_deferred` refusals, so a task assigned once and one reassigned three times are
  indistinguishable. We measure a regret decomposition instead, which mixes allocation with
  execution and capacity — **plausibly the reason four un-mixing attempts each produced a
  retraction.** Second finding: our four-way split is an execution-status taxonomy and none of
  the brief's five manager-failure modes is reported by any cell. Novelty intersection HOLDS on
  all four properties; the surviving claim is a BOUNDARY CONDITION, not an answer to the
  brief's question, and must not become the headline._ **ADOPTED PLAN (RR's, replacing mine):**
  log the manager ACTION STREAM; define the behavioural DV over ASSIGNMENTS from scratch; land
  it WITH L1; reinstate the `PRIMARY DV ABSENT` banner in the finance pipeline. **RR's blocker
  on L3-as-scoped is accepted** — re-measuring the same aggregate without the behavioural DV
  spends episodes to learn whether the instrument improved.
- **Two new methodology rules:** `P1b` (an anomalous rate is stratified before it is explained)
  and `§B` (every quantity states its population and comparator; the population is a PREDICATE,
  not a NAME). (`e1c9fd9`, `eb84e92`, `5ae197b`)

### Since the drift check — the repair phase (L1, L7, L6), all corpus-first except where noted

- **L1 SHIPPED — the environment stops lying to the manager** (`220bbfb`, `dba6644`, `5fded1c`;
  `[x]`, both reviews). Truthful execution state, per-worker load with each capacity dimension's
  RELEASE SEMANTICS, and refusals signalled at the time. **Refusal reasons are computed at the
  site and `can_handle_task` is DERIVED from them**, so the transient concurrency cause can never
  again mask the permanent allotment one. **Segment identity is now DECLARED, not inferred from
  the task NAME** — the old rule meant a manager-created remediation was refused 13× for being
  called the wrong thing, while the identical act named differently ran to completion.
- **Three defects found in L1 by review, all the same shape.** The cross-cell constancy check was
  HOLLOW — it compared `(load unavailable)` to itself six times, and would have passed had the
  feature never been built (LS). The same silent-degrade sat under the LIVE path (LS) — fixed with
  a strict schema. And criterion (i) passed on a hollow live render (RR).
- **L7 SHIPPED — the manager ACTION STREAM and the behavioural DV** (`5e1c076`, `3f58315`,
  `22a1604`; `[x]`, both reviews). Assignments are logged at all four mutation sites, requested
  AND applied, with the previous assignee read BEFORE the mutation. **`rerouted_share` is redefined
  over ASSIGNMENTS** — the pre-revamp version was completion-derived and biased upward exactly in
  the capacity-refusal regime.
- **Three blockers in L7, one of which MY REVIEW PASSED.** Timestep attribution was POSITIONAL
  (LS) — the Nth assignment mapped to the Nth timestep, wrong whenever the manager bulk-assigns,
  which corrupts the forced/discretionary split. An absent load view rendered as an EMPTY ROSTER
  and silently filed moves as FORCED (RE, found while fixing the first). And **terminality was
  evaluated episode-wide inside a per-step loop — a ~7× upward bias in the primary DV that I
  explicitly cleared** (RR).
- **THE BEHAVIOURAL PICTURE, from the pre-repair corpus (descriptive only, no contrast):** 33
  reassignment moves, **24 forced (73%)** — the source had departed, so moving was the only legal
  action. **Forced moves go 22/24 to the SUCCESSOR; discretionary moves go 8/9 to INCUMBENTS** —
  near-opposite distributions. The manager is NOT told to do this. **All 24 forced moves had 3
  capacity-legal destinations**, so destination was a real decision — but because forced moves
  precede capacity binding, not because capacity is generous; **the constrained population is the
  DISCRETIONARY one.**
- **The clearest single illustration of what L1 repairs:** a task moved `A→B` at t19 and `B→A` at
  t20, between two workers both at their allotment, while a third had a free slot. It could not
  run either way. **Pre-L1 discretionary moves are therefore partly noise, and pre-L1 bundles are
  NOT a baseline for either population** — every one of the 33 moves occurred after a refusal the
  manager could not see.
- **L6 BUILT — the quantity registry** (`557d495`, `de32dff`). 52 declared kinds covering
  431/431 emitted values; rates cannot construct without a comparator; the emitter REFUSES to
  write an unregistered quantity and the escape STAMPS the artifact. **LS blocker: the
  committed-list assertion was blind over a third of the list** (truncating at `[` made every
  `episodes[]` entry unfalsifiable). σ entries now carry `MEASURED PRE-L1 — must not size any
  suite` on the quantity itself.
- **PREDICTIONS COMMITTED AND COMPARED BEFORE ANY RUN** (`a9cfaff`, `eecb092`, `d8afeb2`,
  `6516947`). **My sharpest prediction was killed before the run**: forced-to-successor is
  recommended by BOTH the brief's failure mode #1 and capacity-optimal play, so it would have
  been confirmed by the repair merely working. Replaced by `forced_to_successor_uncovered`.
  **And my comparison document itself had a UNIT MISMATCH** — an event rate against a task count,
  15.2:1 apart — caught by RR. The real disagreement is a binary: does ANY stuck task survive.
- **A CIRCULAR DEPENDENCY IN MY OWN BACKLOG** (`c0aedbd`): L2 re-derived against bundles that only
  exist once L3 runs, while L3 depended on L2. Split into L2a (code, zero-API) and L2b (folded
  into L3).
- **THE BRIEF IS AMENDED** (`a4ea708`): load feedback is part of the SETTING and constant across
  cells (framed as PARITY with the nearest neighbour, which already reads workload — not
  innovation); the central claim carries the **exactly-binding capacity** scope condition; and the
  primary DV is redefined over assignments, with CHECK-1's +0.611 barred from citation as
  channel evidence.
- **FIVE further methodology rules, every one paid for this phase:** a query asserting a NULL must
  demonstrate a HIT on a known positive; **its mirror — a CONFIRMING test must be able to
  disconfirm** (fired on me two days after I committed the first); **a DEFAULT must not be a legal
  value of the thing it stands in for** — four sites, all failing toward "fine" (RR); **a comment
  naming a past failure is not a check against it, and displaces one** (RE, self-diagnosed, two
  instances in four days); and **a prediction both the hypothesis and its leading rival endorse is
  not a prediction**.
- **STATE: nothing has run since the original scope run.** No model spend this phase. L3 is gated
  on L2a (analysis code, zero-API); when it runs, **RR's degeneracy check is read FIRST** — if
  fewer than half the episodes show a discretionary move with ≥2 legal destinations, the primary
  DV is degenerate at this scope and that is what L3 establishes.

> **⚠ COMMIT HASHES IN THIS FILE AND IN `records/` NO LONGER RESOLVE, AND THE OLD HISTORY IS
> GONE.** The branch was condensed on 2026-08-08 from 636 commits to 6 thematic ones and the
> backup was deleted on the researcher's confirmation that nothing needed it. **The records are
> unaffected in substance — a hash is now decoration; cite the RECORD FILE.** Every claim in this
> log names its record, and `records/<step>/` is the authoritative evidence.

### The CEILING arc — the phase's main result, all offline, zero run spend

- **THE CEILING RULE, and it is the phase's lesson:** before spending on a contrast, compute the
  BEST POSSIBLE effect it could have — optimal play with the information against optimal play
  without it — convert to σ and n/arm. **If the ceiling is below detectability, no run answers the
  question.** Every fact that ended this phase was computable from the generator before a single
  episode ran. Corollary (RE): *find a population where the correct answer is fixed OUTSIDE the
  system under test* — a reference class cannot be built to pass, which a synthetic control can.
- **THE CARD CHANNEL WAS PRICED AT 1.24% of oracle = 0.16σ ≈ 616 episodes/arm** — real, and
  undetectable at any affordable n. **Two of the three instances the study actually used had a
  ceiling of EXACTLY ZERO** (RE), so the planned run would have measured a provable zero on
  two-thirds of its card contrast. *(`1625fc4`, `d80ddf1`, `403be77`, `7fefa05`)*
- **ONE CEILING BOUNDS ALL FOUR CELLS.** An updated card names exactly `irb_coverage` (240/240),
  so it is the maximal coverage-information channel; declaration, ask and trace convey the same
  fact less reliably or later. **"Drop the card cell and rely on the others" is unavailable.**
  Departure from coverage-optimal method is bounded at 0–2 of 82, validated against a reference
  class of 41 SA-only segments matching at 41/41. *(`8676134`, `31e814c`)*
- **RELIABILITY PRICES AT ~0 AND THE REASON IS STRUCTURAL.** 9 segments, 3 workers, cap 3 admits
  **exactly ONE feasible load shape (3/3/3)** — the manager chooses WHICH work, never HOW MUCH,
  so quality information cannot change anyone's load. *(`b9f33f9`)*
- **SLACK CLOSES THE COVERAGE CHANNEL — LS's promotion of it RETRACTED.** Card ceiling by cap:
  0.22σ at 3, 0.14σ at 4, **EXACTLY ZERO at 5**. With slack the successor takes its covered work
  AND the lied-about segment, so nothing is displaced and the lie costs nothing. **Coverage needs
  SCARCITY, reliability needs SLACK — direct tension, no single setting opens both.** *(`3072470`)*
- **THE LATTICE REPAIR IS PRICED AND IT WORKS: 1.11σ, ~13 episodes/arm, NONZERO ON 30/30** — ~10×
  the current ceiling, and it also removes the zero-ceiling instances. **LS's partial-overlap
  variant prices at EXACTLY ZERO and is COMBINATORIALLY IMPOSSIBLE at coverage size 2** (0 valid
  templates at 5, 6 or 7 classes; 6,480 at size 3 with six classes). **Detectability or partial
  overlap, not both — buying both costs a sixth asset class with transcribed SA weights.**
  *(`ac16d83`)*
- **RETRACTIONS THIS ARC, all LS's, all kept:** "the card channel is structurally inert" (refuted
  by RR's counterfactual — the mechanism is capacity displacement, which I ranked first and did
  not follow through); "the departure check has no power" (RE supplied a reference class I did not
  think to ask for); "slack is the primary lever" (priced, and it is the opposite). **Three
  can't-fail confirmations were produced in one round — LS's template 60/60, RE's 30-seed
  subsample, RE's untoleranced departure count.**
- **AWAITING THE RESEARCHER: a three-way choice** — the disjoint template (1.11σ now, but a TOTAL
  capability change); partial overlap (not available at this coverage size); or coverage size 3
  with a sixth asset class (realism AND detectability, at the cost of a new class and its
  citation). **Nothing is implemented and nothing has run.**

### 2026-08-08 — the lattice decision is the TEAM's, and options 2 and 3 are one option

- **Researcher delegated the decision** with guidance rather than an answer: *keep in mind what
  problem we are solving and how realistic our setup is.* Their preference is PARTIAL OVERLAP,
  stated as a preference that may be wrong.
- **THE REFRAMING: option 2 and option 3 are the SAME option at different coverage sizes.**
  Partial overlap is impossible at COVERAGE_SIZE=2 (enumerated: 0 valid templates at 5, 6 and 7
  classes) and available at COVERAGE_SIZE=3 in **6,480** admissible templates. **The preferred
  design is not ruled out; a sixth asset class is its price.**
- **Next work, all offline:** price the size-3 partial-overlap templates with
  `ceiling_vs_stale_card`; compare with the disjoint template on detectability AND realism; set
  the segment-mix parameter with whichever wins.
- **The ceiling-baseline defect and its fix** are recorded in `records/L4/DIRECTIONS_LS.md` and
  `RESEARCH-CRON-STATUS.md` §1: admission and selection ranked on `ceiling_vs_ignorant`
  (oracle minus a RANDOM blind assignment) when the study's manager always holds the card.
  10.9x apart; 6 of 12 seeds disagree on whether the instance is alive at all. **Every admission
  and stratification figure predating the fix ranked instances by a quantity the study does not
  measure.**
- **Standing:** runs stay small (2–3 episodes/cell, corpus-first); price the ceiling offline
  before spending on any contrast; document here as work proceeds.

### 2026-08-08 — L9 step 1 was defective in its INSTRUMENT and its METHOD; both peers caught it

Record: `records/L9/L9_decisions_LS.md`, `records/L9/card_belief_model.json` (RE),
`records/L9/L9_review_RR.md` + `realism_probe.py` (RR). No model spend.

- **THE BELIEF MODEL PRICED HALF THE CARD.** `ceiling_vs_stale_card` grants the manager the TRUE
  score on any class the card is SILENT about — so it modelled the card's lie and not its
  omission, crediting the manager with knowledge that has no source. **A card is a replacement
  description of a worker, not an addition to a true one.** Verified in source at
  `finance_scorer.py:740`. **Current-template numbers are unaffected** (both models agree 30/30 —
  the successor's silent class is always incumbent-covered there), **but on a disjoint candidate
  the shipped model misses 96% of the effect: 0.37% vs 8.51%.**
- **SECOND TIME THIS ONE FUNCTION HAS BEEN WRONG ABOUT WHICH QUESTION IT ASKS** — first the
  baseline (oracle − random, when the manager always holds a card), now the belief. Both were
  arithmetically right and semantically wrong. **A ceiling now states its baseline AND its belief
  model, and is tested where the candidate beliefs must diverge.**
- **ORDER CORRECTED: fix the belief model → re-derive the admitted set → price.** Selection
  excludes zero-ceiling instances using the defective model, so **a template whose value lies in
  the card's omission would be scored zero and silently excluded before it was ever priced.**
- **THE PRICING METHOD IS DEAD.** Coverage substitution cannot price six classes: every instance
  has 9 segments over exactly 5 classes, so a template naming a sixth prices its **five-class
  projection** under the six-class name — the sixth class comes out free, which is backwards.
  **The `partial_overlap` row reading 0.00% is that artefact and is not a price.** Step 1 is
  therefore NOT "offline, zero spend" as scoped.
- **The sixth class goes in the GENERATOR**, as a documented economic clone of an existing class
  (no BCBS transcription, marked synthetic, not the shipping version), with generation raising if
  a template names a class with no segments. **Priced-but-never-generated is now three-for-three
  as this project's failure mode** — RE's own proposed template raises `IndexError` in
  `swap_shared_class` and had never been generated.
- **REALISM, MEASURED RATHER THAN ARGUED (RR).** Under the disjoint template the stale card
  retains **23% of its partial-overlap value** and is **worse than coverage-blind random on 7 of
  30 seeds**. That is not *the same job done by someone else*; it is a different specialist.
  **Disjoint drops to fallback on validity grounds regardless of its σ**, and the decision
  reshapes: *does a realistic template clear detectability?* **If size-3 does not, the study has
  no manipulation that is both valid and measurable — which goes to the researcher, because it
  changes what the paper can claim.**
- **RETRACTION (LS): my 6,480 was right for a predicate I never stated.** 12,960 ordered; 6,480
  up to incumbent symmetry; 6,480 ordered with O3; **3,240 admissible AND generator-legal up to
  symmetry.** Two different counts coincide, and I quoted the number without saying which.
  "It reproduced" is not what happened.
- **CONFIRMED, both peers, each having gone looking to refute it: five classes at size 3 admits
  ZERO templates, structurally** — three 3-subsets of four classes cover each at least twice, so
  the successor can never sole-hold anything. **The sixth asset class is a real cost.**
- **Predictions logged before the number exists** (protocol): LS — the pool splits on carrier
  count, two-carrier subfamily in disjoint's band, single-carrier near zero. RR — 2–5% pooled,
  below disjoint, on a redundancy mechanism. **We disagree by ~2x on the two-carrier subfamily,
  which is the quantity the decision turns on.** RE's is pending and RR's has not been relayed.
  **Every size-3 number is reported SPLIT ON CARRIER COUNT** (2,160 single / 4,320 two) and every
  σ carries its mix parameter.
- **Open reconciliations:** RR's 0.85% vs the published 1.24% headline — different populations,
  neither quoted with its population as a predicate (standing rule 5); the 57.1% free-draw
  docstring figure does not reproduce (RR gets 90.5%); `lattice_template_proposal.md` carries the
  wrong `_designate_swap_pair` dependency claim.

### 2026-08-08 (same day, later) — matched mix, the carrier test, and a second circular dependency

Record: `records/L9/L9_decisions_LS.md` (addendum, D8–D12), RE's `check_mix_sweep.py`.

- **MATCHED-MIX CORRECTION, and it goes against the retraction as it has been read.** Measuring nA
  per cell over 120 label permutations × 10 seeds under the corrected belief model: **disjoint
  beats the current template 6–7× at EVERY nA, including nA=0, and 10× pooled** (current 0.05σ,
  disjoint 0.50σ). **The forcing inflated the ABSOLUTE LEVEL; it did not manufacture the template
  DIFFERENCE.**
- **RETRACTION (LS, propagated from RR): "nA=0 is IDENTICAL to the current template" is a
  comparator error.** It compares disjoint-at-nA=0 against **current-AS-SHIPPED**, which carries
  its own `shared_class_segments=4` forcing — not against current-at-nA=0, which is 0.03σ. I
  accepted it without checking and put it in the record. **Same §B shape as the six earlier
  failures: right arithmetic, different comparator.** Consequence: **on detectability the disjoint
  template is far stronger than the ceiling arc concluded, and its demotion to fallback rests on
  the realism finding alone.**
- **The carrier split and the belief-model defect are ONE problem.** Four candidate definitions of
  "carrier" tested against the 2,160/4,320 split; three are constant at 1 across all 6,480 and
  exactly one reproduces it: **classes the card is SILENT about that the successor SOLE-HOLDS.**
  **The second carrier IS the omission** — the half the shipped model prices at zero — so pricing
  with it would **collapse the stratification by construction** and report "carrier count doesn't
  matter", the opposite of the truth.
- **★ SECOND CIRCULAR DEPENDENCY, same shape as L2/L3, caught before it bit.** Every σ here
  divides by the **pre-L1 σ = 0.0768, which must not size a suite**; an absolute σ needs L3;
  **L3 is blocked on L9.** **Broken by deciding L9 on RATIO plus REALISM and moving the absolute
  detectability verdict to a step after L3.** No one says "clears detectability" in either
  direction until a post-L1 σ exists — **including the conclusion "neither candidate is
  detectable and the sixth class was spent finding out."**
- **Sixth class: CLONE for the decision, transcribed only if it ships**, carrying a marker that
  **raises on a live study path**. Defensible for a ceiling comparison, indefensible in a reported
  result.
- **PREDICTIONS, all three logged before the number exists.** LS: split hard, two-carrier within
  2× of disjoint. RE: two-carrier ~0.35σ, single ~0.12σ, pooled ~0.25σ, split ~3×. RR: 2–5%
  pooled, below disjoint, bimodal. **As a ratio to disjoint-at-matched-mix: RE ≈0.78, LS ≥0.5,
  RR <0.5 — not the same prediction, so the exercise is not confirmatory.**
  **LS's is the badly formed one and is recorded as such**: a factor-of-2 band that contains RE's
  point estimate cannot be refuted by the result. **RE's positive control is adopted: a split near
  1.0 is the belief-model fix failing to take, not a finding.**

### 2026-08-08 (same day, later still) — both of LS's open questions measured; the clone is bracketed

Record: `records/L9/L9_clone_and_sigma_RR.md` (RR), `records/L9/L9_decisions_LS.md` D13–D16.

- **THE σ-INVARIANCE BREAK HOLDS, and RR tested the premise rather than the arithmetic.** "σ cancels
  from a ratio" was never the risk; **"there is one σ" was** — a template that changes the lattice
  changes the outcome distribution. Measured over all 1,680 feasible allocations: SD/oracle is
  0.0410 (current) vs 0.0431 (both candidates) — **1.05×, against ratios of 6–16×.**
  - **The residual is SIGNED and points AGAINST the fallback**: a shared σ **overstates disjoint by
    ~5%.**
  - The proxy omits across-episode manager variability — a property of **the manager, not the
    lattice**, so no mechanism makes it differ by template.
  - **★ SCOPE CONDITION, now standing: the break is valid HERE, measured, not as a principle.** It
    fails for any template that **changes the number of uncovered classes**, which every admissible
    template so far fixes at exactly one. **A candidate that changes it re-opens the question.**
- **CLONE BIAS IS SIGNABLE, so the SOURCE stops being an implementation detail.** The ceiling is
  paid in one currency — score lost when a coverage gap forces SA fallback — which is a property of
  the class and which a clone inherits exactly. Divergence: mdb 0.3564, retail 0.3509, sovereign
  0.3333, bank 0.2575, corporate 0.2393; mean 0.3075. **Cloning corporate/bank understates ~20%;
  mdb/retail/sovereign overstates ~14–16%; 1.5× end to end cannot flip a 6–16× ranking.**
  - **DECIDED: do not choose a source — price under `corporate` AND `mdb` and report the BRACKET.**
    Seconds of compute, and it converts a judgement call into a stated interval. Every reported
    figure names its clone source.
  - **Held weakly, mechanism named, not measured:** the five transcribed classes sit at the
    low-divergence end and plausible real sixth classes (equity, real estate, specialised lending)
    at the high end, so **a clone most likely UNDERSTATES a real sixth class.**
- **WITHIN-CLASS VARIATION DWARFS BETWEEN-CLASS** — SD ~0.18 inside each class (range 0.002–0.754)
  against a 0.12 spread between them. **Which segments land in the class matters far more than
  which class is cloned**, putting the clone behind the segment mix. **A clone-priced figure is
  adequate for RATIOS and inadequate for ABSOLUTE n** — D11's split, arrived at from a second
  direction.
- **★ MANUFACTURED TIES: a REQUIRED check, upgraded from RR's "optional".** Two classes with
  identical economics and different coverage make cross-assignments score **exactly** equal,
  **manufacturing exact ties in the allocation optimum**, resolved by enumeration order. **Tie-break
  luck is why label permutation exists in this project**, and here the ties would be ours by
  construction, inside the optimum that produces the headline. **With the six-class generator:
  exact-tie rate six-class vs five-class; if it rises, the tie-break becomes explicit.**
- **RR withdrew the nA=0 line themselves** and proved the belief-model isolation per segment — 810
  cells across three templates × 30 seeds, **162 differ, all on classes the card is SILENT about,
  ZERO on classes it CLAIMS** — so the 8.13% gap is the belief model's alone, conditional on
  calibration remaining class-level. **This leaves the realism probe as the sole case against the
  disjoint template**, which RR accepts and will defend on that footing.
- **STILL NOT QUOTABLE: "~494/arm at nA=0, ~64 pooled, ~13 at nA=4."** They divide by the pre-L1 σ
  (D11). **The SWING across the mix survives and is the substantive half — and it is 38.2×, not 27× (corrected below)** — the mix is a
  declared design choice, not an inherited one.

- **★ CORRECTION: the mix swing is 38.2×, not 27×** (RR self-corrected; verified here from raw
  shares). Effect ratios on the disjoint template — nA=4/nA=0 = **6.18×**, nA=4/pooled = 2.24× —
  and required-n swings **38.2× / 5.0× / 7.7×**. **27× was arithmetic, not rounding.** **LS quoted
  it twice into the record before checking it**, the same failure as adopting the
  "identical-to-current" line. **Written as `(effect ratio)²` the swing never touches σ, so it is
  OUTSIDE D11 by construction rather than merely surviving it** — the σ-free form was available
  all along and is the stronger statement. **One design parameter moves required sample size by a
  factor of 38.**
- **Tie check gains one requirement (RR):** confirm the tie-break is deterministic under a
  **REORDERING of the segment list**, not just that the tie rate is stable — enumeration order is
  the thing at risk, so a stable rate under one fixed order would look like a pass.

### 2026-08-08 — D1 and D2 land; and a latent validity exposure in every pre-fix bundle

Records: `records/L9/D1_D2_implementation.md` (RE), `CHANGED.md` entries 1–7 (RR, parent directory).

- **D1 PASSES.** `ceiling_vs_stale_card` now scores the successor throughout as the card describes
  it. **The acceptance asserts BOTH halves and fails on either** — control (current template: 0/30
  costly omissions, 30/30 models agree) and divergence (disjoint: 30/30 costly, 0.37% → 8.51%).
  **The superseded model is kept inside the acceptance as a frozen copy**, because an acceptance
  running only the current implementation cannot show the divergence, and the divergence is the
  half the fix exists to produce. RR's two assertions land with it: calibration must be
  class-level, and a ceiling is non-negative.
- **D2: admitted 34 → 21, chosen [3,23,36] → [7,20,30] — AND NONE OF IT IS D1's.** **D1 changes
  the ceiling on 0 of 34 admitted seeds**, exactly as the control predicted; both belief models
  agree on which 13 are dead. **The entire move is the earlier ignorant → stale-card BASELINE fix,
  whose `records/R2/instance_selection.json` had never been regenerated** — so the selection record
  on disk described a rule nobody was running. **Reported as an isolation rather than a delta;
  otherwise D1 would have been credited with another fix's effect.**
- **Independent confirmation of the selection diagnosis from the other end: seeds 23 and 36 — two
  of the three instances the pilot actually ran — have a stale-card ceiling of EXACTLY ZERO.**
- **The `"rule"` string in the selection record said `ceiling_vs_ignorant` while the code ranked on
  stale card** — documentation naming a source that did not produce the value, **inside the record
  of the fix for exactly that defect.**
- **★ LATENT VALIDITY EXPOSURE, found in the `CHANGED.md` backfill and NOT YET RESOLVED.**
  `end_workflow` was in `COMMUNICATION_TOOLS`, **handed to every worker and the stakeholder**,
  against its own docstring ("should only ever be called by the manager agent"). Observed failure
  on record: **an episode killed one timestep before a scheduled event.** **A run truncated before
  its swap is not a short run — it is a run of a different experiment**, and this whole phase has
  been corpus-first over 18 pre-existing bundles. **CHECK COMMISSIONED (RR, read-only): for each
  bundle, did the run reach its scheduled swap timestep and terminate at the horizon?** If any
  truncated, findings derived from it are re-derived or withdrawn **and it goes to the researcher**,
  because it changes what can be claimed.
- **Two §B defaults violations recorded, second-order for us** (no LLM judge feeds our primary
  metrics): `LLMScoredResponse.score` **silently coerces** `"pass"`→True and numeric strings→float
  on a path feeding a reported quantity, making a model that answers `"pass"` indistinguishable
  from one that answers `True`; and a judge rubric parse failure retries twice then records a hard
  **`0.0`, which is a LEGAL rubric value** — the default-must-not-be-a-legal-value shape exactly.
- **A documentation trap:** `ScheduledAgentChange`'s `"replace"` fields still describe the RETIRED
  framing — `announce=False` as *"silent swap (behavior changes with no observable announcement)"*
  — i.e. the silent-behavioural-change direction abandoned 2026-08-04 and scoped out in
  `CLAUDE.md`. Code correct, prose describing a study we are not running. **Being fixed.**
- **`detection_probe.py`: 98 lines of core code nothing references.** **Decided: RETAIN and
  DOCUMENT** as the learning-teammate horizon, not delete — the deletion authorisation was scoped
  to the extension directory and this is a core path. **Delete-or-keep goes to the researcher as a
  one-liner.**
- **PROCESS: `git add -A` swept RE's in-flight tree into LS's commit `f78ae94`**, whose subject
  describes work it does not contain. **LS's command; rule adopted — all three agents stage
  explicit paths.** Not an argument for a branch: the one-branch rule is correct and this is the
  smaller problem. **The mixed commit is recorded rather than rewritten.**
- **`CHANGED.md` has no version control.** The document `CLAUDE.md` names as the deviation record
  lives in the parent directory, which is not a git repository — **no history, no blame, no
  recovery if truncated.** Recorded as a fact about the record; **surfaced to the researcher**, as
  the layout is theirs.
- **Lesson worth keeping (RR): diff line count is a bad proxy for significance.** `communication_di.py`
  at +9/−1 was the most significant item in the batch and a size filter excluded it.

### 2026-08-08 — the tie check blocked step 4; tie-break by expectation

Record: `records/L9/tie_rate.json` (RE), `records/L9/L9_decisions_LS.md` D19–D22.

- **★ THE REQUIRED TIE CHECK BLOCKED STEP 4** — the largest finding this phase after the belief
  model, and it was raised as "optional".
- **The tie RATE is not the quantity; CEILING SPREAD ACROSS THE BELIEVED-OPTIMAL SET is.** Ties in
  the TRUE optimum are harmless — every tied allocation has the same value by definition. **The
  exposure is entirely on the BELIEVED side**: allocations tied under the card are re-scored under
  truth, where they are not tied, so the ceiling is decided by `product()`'s visit order.

      five_class        11.70 tied optima   spread 0.00% mean / 0.00% max    0/20 ambiguous
      six_class_clone   29.45 tied optima   spread 7.00% mean / 14.10% max  20/20 ambiguous

- **Five-class already carried ~12 tied optima and a spread of EXACTLY ZERO on 20/20 seeds, so
  nothing published moves — including 8.51%.** The check discriminates: null where ties are
  harmless, large where they are not, which is what makes the non-null credible.
- **With the clone the spread is the same order as the entire effect being measured.**
- **DECIDED: tie-break by EXPECTATION over the believed-optimal set, with [min, max] alongside.**
  Under the card those allocations are indistinguishable to the manager, so any deterministic rule
  (first-visited, best, worst) **attributes a discrimination it cannot make**. **Expectation is NOT
  an upper bound** — a manager tie-breaking worse than chance puts the true ceiling above it — so
  the interval is load-bearing. Coincides exactly with current behaviour at five classes.
- **REJECTED: perturbing the clone's economics to break ties.** It would work and would silently
  reintroduce the between-class bias the bracket exists to handle.
- **★ A CEILING NOW DECLARES THREE THINGS: BASELINE, BELIEF MODEL, TIE-BREAK RULE.** Each was added
  after it silently decided a number. General form: **wherever a reported quantity depends on a
  choice the code makes for us, the choice is named in the function or the number is not
  reportable.**
- **D14 NARROWED (LS): the clone's bias is signable on ECONOMICS, UNSIGNED OVERALL.** The tie rate
  is a consequence of the clone being EXACT — **its virtue and this hazard are the same property** —
  and RR's divergence argument does not cover the manufactured indifference. **An ε-perturbation is
  offered as an optional DIAGNOSTIC to sign it; the exact clone remains the instrument.**
- **D3 otherwise complete:** `register_synthetic_clone` clones SA table, PD floor and rating pool;
  `assert_no_synthetic_classes` raises on a study path; a `coverage_override` naming a class with
  no segments now raises. **Retail refused as a clone source** — its SA weight is reached by a name
  test rather than a table lookup, so a clone of it would silently get different SA treatment and
  stop being a clone. Five-class path verified unchanged.
- **★ THIRD INSTANCE OF ONE DEFECT — a provenance field naming a source that did not produce the
  value:** the selection record's `"rule": "ceiling_vs_ignorant"` while the code ranked on stale
  card; `parameters.coverage_size` recording the module constant so a size-3 instance reported 2;
  and the original §B family. **Candidate rule raised for `METHODOLOGY_RULES.md`: a provenance
  field is asserted against its source at emission, or it is not written.**

### 2026-08-08 — the `end_workflow` exposure was LATENT, never realised; audit clean

Record: `records/L9/truncation_audit_RR.md` (RR, `63dff6c`). **No bundle ended before its swap.
Nothing is re-derived or withdrawn, and this does NOT go to the researcher.**

    all 18 study bundles (R2, 6 cells x 3 seeds):
      horizon 22, timesteps 0..21, n(timestep_completed) = 22 on all 18
      t_swap = 3, reached by all 18; swap event at exactly t=3 in 15/15 swap cells
      cellU carries no swap BY DESIGN (unswapped control)
    end_workflow across all 36 run bundles on disk:  0 occurrences
    control from the SAME tool list: send_message 2,605 across the 18

- **This is a measurement, not a comfortable null, for two reasons.** The check rests on a count
  that would be **LOWER under truncation** (`n(timestep_completed)`), not on the absence of a
  termination event — **so it can fail.** And the zero on `end_workflow` sits beside thousands of
  calls to sibling tools **from the same list**, so tool activity is demonstrably recorded.
  The swap detector was validated on a known-positive case first.
- **The one short run is a legitimate finish** — `S8/run_seed7.json`, 18/22 timesteps, 16/16 tasks
  completed, `n_missing 0`, `n_unstaffed 0`, last timestep `success=True`.
- **★ WHAT THE AUDIT CANNOT ESTABLISH, stated by RR rather than left implicit:** whether
  `end_workflow` was **absent from the toolset** or **present and never called**. Both give 0
  invocations, because **bundles record tool CALLS, not tool INVENTORIES.** The verdict holds
  either way — no run truncated — but the tool can only be certified unused, not unavailable.
  **Forward-looking: anyone re-running on a pre-fix checkout is still exposed.**
- **DECIDED (LS): recording each agent's TOOL INVENTORY at setup is REQUIRED, not optional** —
  though it does **not** block step 4. One line in the bundle writer. **This study's whole subject
  is what the manager can and cannot access**, so an inventory is provenance for our own design,
  not merely for this audit. It converts a permanently unanswerable question into a recorded fact.
- **Entry 4 fixed:** `ScheduledAgentChange` now documents `replace` as an exogenous replacement the
  manager did not choose, with id reuse as the mechanism for holding everything but the worker
  constant, and self-change explicitly scoped out. **Made explicit what was only implicit: leaving
  `new_agent_capabilities` unset is what makes the registry card go stale.**
- **Entry 7 retained and documented** — header records that it is kept for the learning-teammate
  horizon and that `core/evaluation/` implies no detection measure in the current study.
- **★ FOURTH OCCURRENCE of the empty-collector failure**, in this audit's own first pass: a
  collector returned `None` on all 18 rows and the verdict printed `all passed t_swap: False`.
  **What caught it was that the emptiness was VISIBLE ON SCREEN — not that anyone was suspicious.**
  **Candidate rule for `METHODOLOGY_RULES.md`: print the intermediate quantity a verdict is
  computed from, not only the verdict.** A positive control catches this only if someone thinks to
  run one; a printed intermediate catches it passively.
- **PROCESS: a second `git add -A` collision**, RR's this time, sweeping RE's in-flight
  `finance_scorer.py` and `tie_rate.json`. **Disclosed, attribution amended rather than history
  rewritten, and RE asked to confirm the captured state was not mid-edit.** Explicit-path staging
  is now stated by all three agents. **Twice in one session is the rule earning itself.**

### 2026-08-08 — STEP 4 PRICED: size-3 partial overlap is 0.35–0.49× the disjoint template

Record: `records/L9/size3_pricing.json` (RE), `records/L9/L9_decisions_LS.md` D23–D26.
**27s of CPU. No model spend.**

    reference: size-2 disjoint, five classes
       nA=0  2.02%   nA=1  3.84%   nA=4  9.03%   pooled 4.30%

    size 3, six classes  (nA=1 in EVERY cell)
       clone      carriers   mean share   ratio to disjoint@nA=1
       corporate      1        1.89%          0.49x
       corporate      2        1.58%          0.41x
       mdb            1        1.84%          0.48x
       mdb            2        1.35%          0.35x

- **Ratios and squares only — no σ anywhere, per D11 and the two-removes constraint.** These are a
  **LATTICE COMPARISON, not an effect size.**
- **PREDICTIONS SCORED. RR's is the only one the result confirms** (<0.5; pooled 2–5%). **RE
  directionally right with the right mechanism, ~2× optimistic** (≈0.78 predicted vs 0.35–0.41).
  **LS WRONG ON BOTH AXES** — predicted two-carrier within a factor of 2 of disjoint (it is
  0.35–0.41×) and single-carrier near zero (it is 1.84–1.89% and **higher** than two-carrier).
  **The loosest of the three predictions, and it still failed.**
- **The clone bracket is NARROW — 1.84 vs 1.89, 1.35 vs 1.58 — so the clone SOURCE is not where the
  uncertainty lives**, as RR's within-vs-between-class variance predicted. **A control that turns
  out not to matter is the right outcome for a control.**
- **★ THE TWO-CARRIER INVERSION, UNEXPLAINED, AND IT BLOCKS THE READING.** Two carriers price
  **LOWER** than one — the **opposite** of the stratification's prediction, since the second
  carrier IS the card's omission and should ADD effect. **Not a mix confound: nA=1 in every cell of
  both groups.** Three candidate explanations on the record:
  - **H1 capacity saturation** — more segments need the successor, `cap=3` binds, **the ORACLE
    already pays the penalty** and the gap compresses. *Predicts the inversion weakens or reverses
    at higher cap.* **(LS declares a bias: this is the same capacity-displacement mechanism as the
    original card-channel finding, so it is the one LS is most likely to believe for bad reasons.)**
  - **H2 denominator artefact** — ceiling SHARE divides by oracle. *Predicts the inversion vanishes
    on ABSOLUTE ceilings.* **Cheapest test; a re-read of existing numbers, no new pricing.**
  - **H3 the labels are wrong** — the carrier definition was chosen by testing four candidates
    against RR's COUNTS, which establishes it matches the counts, **not that it matches the
    concept.** If the labels are subtly wrong, H1 and H2 answer the wrong question.
- **★ AND THE QUESTION THAT DECIDES WHETHER THE COMPARISON IS FAIR: is `nA=1` in every size-3 cell
  a fact about SIX CLASSES or a fact about the CURRENT GENERATOR?** `shared_class_segments = 4`
  forced four segments into one class at five classes; nothing obviously prevents it at six.
  **If forcing is merely unimplemented, we compared disjoint across its whole mix range against
  size-3 at a single point of its own.** **NO READING SHIPS UNTIL THIS IS SETTLED** — it is the
  difference between *"partial overlap costs half the channel"* and *"costs half the channel at the
  one mix we happened to price."*
- **★ 8.51% BECOMES 9.03%, and "D19 changes no reported number" was wrong.** The claim held for the
  natural five-class template (0.00% spread, 20/20 — what the tie check measured) and **not for the
  SUBSTITUTED disjoint template, which was never tested.** Cause: **`check_template_pricing`
  computes the ceiling with its OWN local enumeration instead of calling the shipped scorer**, so
  it never saw D19 — **two sources of truth for one quantity, now visibly disagreeing.**
  **Delegation approved; the correction sweep is part of that change, not a follow-up.** 8.51%
  appears in D1's acceptance, D5's realism table, RR's realism probe and both ledgers.
- **Paired exclusion handled correctly:** 6 of 240 (template, seed) cells fail serviceability under
  `corporate` and not `mdb`; **dropped from BOTH arms**, since dropping each arm's own failures
  would compare the arms on different populations and corrupt the bracket the two sources exist to
  provide.
- **WHAT THIS DOES NOT ESTABLISH:** no detectability verdict (ratios by construction); "size 3 is
  worse" holds **only at the mix six classes naturally produce**; and the sixth class does not
  exist — its weights are copied and the clone manufactures indifference whose sign is unasserted.

### 2026-08-08 — the inversion is LOCATED, the clone is EXONERATED, and the band is sized

Records: RE's carrier proof; RR's `records/L9/clone_indifference_RR.md`;
`records/L9/L9_decisions_LS.md` D27–D31.

- **★ THE "CARRIER COUNT" LABEL IS RETIRED. It asserts a decomposition the design cannot support.**
  Proved exhaustively over all 6,480 admissible templates, **0 counterexamples**, and **forced
  rather than sampled** — `|w0 ∩ w1| = 1` in every admissible partial template, so:

      carriers = 1  <=>  the successor-unique class IS the shared class      (card NAMES it)
      carriers = 2  <=>  the successor-unique class is one the card never mentions (card SILENT)

  **No sampling design can separate them, because they are the same property.** **Of LS's three
  rivals, H3 lands** — the labels do not mean what their name says, and **H1/H2 were asked about a
  variable that does not exist as stated.** Contrast renamed: *does the card NAME the class the
  successor is uniquely required for, or is it SILENT about it?* **RE cleared their own sampling
  first (12/12 match on five structural properties).** It also makes RR's "the single-carrier group
  has the current template's structure" **provable rather than descriptive**.
- **THE INVERSION IS LOCATED, NOT EXPLAINED — and it is MORE counterintuitive after renaming: the
  case where the card CORRECTLY names the critical class prices HIGHER.** Both groups carry the
  same number of false claims (2), so "more card error" is not it. **RE's capacity guess is the
  surviving mechanism and is flagged as a guess**, not a finding.
- **★ THE CLONE IS EXONERATED: COVERAGE SIZE 3 manufactures the indifference, not the clone.**

      size 2, 5 classes (shipped)     spread 0.00%    0/10 ambiguous
      size 3, 5 classes, NO CLONE     spread 3.94%   10/10 ambiguous
      size 3, 6 classes with CLONE    spread 7.36%   10/10 ambiguous

  A ±20% perturbation of the sixth class's SA table leaves the tie set unchanged at 30.00, **with a
  live-knob control** (50% does move an SA number), so the invariance is a result, not a dead
  parameter. **LS's ε-diagnostic is INERT, not confounded — RE told not to spend on it.**
  **D21 is CORRECTED: "virtue and hazard are the same property" is wrong; D14 returns to
  signable-and-bounded on economics.**
- **★ THE TIE-BREAK IS PERMANENT, NOT SCAFFOLDING.** Expectation-plus-interval was adopted as a fix
  for a clone artefact. **It is not one — any size-3 design carries it, including a real
  transcribed sixth class. D19 ships with the study.**
- **RR's limitation on their own control, stated unprompted:** their five-class size-3 template puts
  `sovereign` in all four workers (102 tied optima vs the clone arm's 30), so **the 2× amplification
  3.94% → 7.36% cannot be attributed to the clone rather than to lattice structure.**
- **THE AMBIGUITY BAND, SIZED (LS) rather than repeated. It is RELATIVE to the ceiling — 7.00% mean,
  14.10% max — not percentage points of oracle** (a 14-point absolute spread on a ~1.5-point ceiling
  is impossible; the units settle it). Conservatively applying the per-instance band undiminished to
  a group mean:

      size-3 vs disjoint@nA=1        gap 2.44x    band ±0.03 / ±0.07 max   separated overwhelmingly
      within size-3, named vs silent gap 1.365x   band ±0.03 / ±0.07 max   separated MARGINALLY
                                     (mdb 0.478 vs 0.350; max-band 0.411 vs 0.399)

  **The band does NOT threaten the headline; RR's caveat stands where they aimed it, at a
  near-threshold call, and the headline is 2.44× from threshold.** It DOES make the renamed
  within-size-3 contrast thin — **it must be reported with the band attached.** **The band remains a
  real, previously unaccounted COST of size 3**: ambiguity about *what the ceiling is*, an offline
  design quantity, not extra noise in what a run would measure.
- **Two methodology rules landed in `METHODOLOGY_RULES.md` §E and §G, both sharpened past LS's
  proposal.** Provenance: **a wrong VALUE is caught because it has a plausible range and people
  examine it; a wrong PROVENANCE FIELD is caught only by re-deriving the value from scratch — the
  exact work the field exists to save.** Where it cannot be derived or asserted, **omit it**: a
  missing field sends the reader to the code, a wrong one stops them looking. Verdicts: **a
  reduction over an empty or all-`None` collection must never render as an ordinary verdict** —
  `all([])` is `True`, `any([])` is `False`, and both are lies about a measurement that did not
  happen.
- **★ D26 IS THE SOLE REMAINING BLOCKER ON L9**, unanswered by either peer: **is `nA=1` in every
  size-3 cell a fact about SIX CLASSES or a fact about the CURRENT GENERATOR?** If forcing is
  merely unwired, the trade-off compares disjoint across its whole mix range against size-3 at one
  point of its own. **Nothing goes to the researcher until it is settled.**

### 2026-08-08 — both inversion hypotheses falsified; the mechanism found; blocker 2 resolves AGAINST us

Records: `records/L9/inversion_diagnosis.json` (RE), `records/L9/L9_decisions_LS.md` D32–D35.

- **H2 (denominator artefact) FALSIFIED** — absolute ceilings invert identically (corporate
  0.1678 → 0.1419; mdb 0.1634 → 0.1211) and **oracles differ by 0.8% against a ceiling gap of
  15–26%**, so there is nothing for the denominator to do.
- **H1 (capacity saturation) FALSIFIED by its own falsifier** — the inversion persists at **cap=9**,
  no constraint at all on 9 segments over 3 workers.
- **★ THE CAP SWEEP FOUND THE MECHANISM, AND IT IS H1'S MIRROR: capacity AMPLIFIES the card-names
  group rather than compressing the card-silent one.**

      corporate  card-names   1.89% -> 2.10% -> 2.21% -> 2.22%   (cap 3, 4, 5, 9)
                 card-silent  1.58% -> 1.58% -> 1.58% -> 1.58%   EXACTLY FLAT
      mdb        card-names   1.84% -> 2.03% -> 2.13% -> 2.15%
                 card-silent  1.35% -> 1.35% -> 1.35% -> 1.35%   EXACTLY FLAT

  **Flat in cap means the loss is ONE un-routed segment and nothing else.** The rise on the other
  group is the manager piling onto a successor it believes serves three classes, **two of the
  claims false, damage scaling in how much it can pile.**
- **LS's declared bias, scored:** LS flagged H1 as *the one I am most likely to believe for bad
  reasons*. **H1 as stated is FALSE — and capacity-displacement is nevertheless the live mechanism,
  acting on the other group.** Right about the ingredient, wrong about the direction; **the
  pre-committed falsifier is the only reason that cost nothing.**
- **★ BLOCKER 2 (D26) RESOLVES AGAINST US: `nA=1` is a fact about the GENERATOR, not six classes.**
  `shared_class = _template_shared_class(chosen) if coverage_override is None else None` — **mix
  forcing is switched off on the `coverage_override` path, the only path that can generate six
  classes.** `shared_class_segments` is ignored there; **nA=4 has never been reachable.**
  **CONSEQUENCE: the matched-cell ratio (0.35–0.49× at nA=1) STANDS as a fair cell-to-cell
  comparison. Any statement of the form "size 3 is weaker" DOES NOT** — it is established at one
  point of size-3's mix range against disjoint across all of its own.
- **APPROVED: mix forcing on the override path.** The mechanism predicts **the omission cost scales
  with nA while the lie's capacity amplification does not, so the inversion should REVERSE at
  higher nA** — and **the regime that tests the inversion is the same regime that tests fairness.**
  Two open questions collapse into one offline measurement.
- **PREDICTION PROTOCOL RUNNING** (this could flip a design decision, which is the case the rule
  exists for). RE's and LS's are committed; RR's requested privately, neither relayed.
  **LS: the inversion reverses decisively; card-silent rises ≥3× its nA=1 value; card-names rises
  <1.5× and may FALL; size-3-at-nA=4 vs disjoint-at-nA=4 lands ≥0.7. Falsifier: card-silent rises
  <2×, or the ordering does not reverse.**
- **BUILD REQUIREMENT carried from the five-class trap: MEASURE nA per cell rather than requesting
  it**, and report the achieved distribution beside the price. `shared_class_segments` produced
  nA=4 in 30/30 seeds and **a forced parameter landing on one value in every cell is a constant
  being reported as a variable.**
- **★ AND FORCING RE-OPENS THE REALISM AXIS PARTIAL OVERLAP WAS CHOSEN FOR.** Forcing the mix is
  **deliberately choosing the favourable value of the parameter we criticised for being silently
  inherited.** Legitimate only if declared and defended. **Is 4 of 9 segments in one asset class a
  realistic portfolio?** Weak prior yes — real Basel books are concentrated — **but it must be
  argued, not assumed. Put to RR as a lattice-realism question. If the size-3 verdict rests on
  nA=4, the REALISM of nA=4 goes to the researcher WITH the number, not after it.**

### 2026-08-08 — the zero best case, a peer contradiction, and the ratio SUSPENDED

Records: `records/L9/step4_audit_RR.md` (RR), `records/L9/L9_decisions_LS.md` D36–D40.

- **★ THE SIZE-3 BEST-CASE CEILING IS EXACTLY 0.00%** on every sampled instance, in both groups —
  the believed-optimal tie set **always contains an allocation that is also truth-optimal**.
  **LS CORRECTION TO THE READING:** *"a manager can reach the true optimum knowing nothing, provided
  it breaks ties favourably"* **overstates it — the proviso requires exactly the information under
  study**, so it is a BOUND, not a scenario a card-believing manager can occupy.
  **What it DOES establish is a qualitative difference worth keeping in the paper whichever
  template wins: at size 3 the stale card NEVER RULES OUT the true optimum — the manager is never
  forced into a worse allocation, it just cannot tell which member of the tie set is right, so the
  whole effect is FAILURE-TO-DISCRIMINATE. At size 2 the card can force a genuinely worse
  allocation — it EXCLUDES rather than fails to guide.**
- **★ LS REFRAMING, against the option LS and the researcher both prefer: the 0.35–0.49× ratio
  UNDERSTATES size-3's cost.** Required n scales with (effect/σ)², and **size 3 adds a σ that size
  2 does not have** — tie-break dispersion (best 0.00%, expectation ~2.2–2.4%, worst ~5.0%) is
  variance in the DV **driven by something other than the manipulation**, and the shipped size-2
  lattice has NONE of it. **Not a reason to drop size 3 — the variance is bounded and D19's
  interval carries it — but the interval now travels with every size-3 number and is not summarised
  away.**
- **★ THE TWO PEERS CONTRADICT EACH OTHER ON THE SAME QUANTITY UNDER THE SAME RULE.**

      RE, D19 expectation:  card-silent LOWER  (1.35-1.58% vs 1.84-1.89%)   inverted
      RR, D19 expectation:  card-silent HIGHER (2.43% vs 2.17%)             NOT inverted

  RR's four-rule table shows **the inversion appears under worst-case ONLY** — not under D19, not
  under bare visit order. **So there may be no stable inversion, and LS's H1/H2 may have been
  falsified against something that does not exist.** **Neither peer claims the other has a bug and
  LS is not adjudicating by preference. Resolution is mechanical: ONE shared sample — same
  templates, same seeds — both implementations, under D19.** **Until then the inversion is NOT a
  finding and is not reported as one.**
- **★ THE MATCHED-CELL RATIO IS SUSPENDED — RR upheld over RE.** The `coverage_override` path
  disables **BOTH** mix amplifiers, not just `shared_class_segments`; the divergence-selection
  branch never fires either. **So even at matched nA=1 the five-class arm carries an amplifier the
  six-class arm does not.** RR's same-lattice demonstration is better evidence than either
  code-read: seed 0's own natural template handed back through the override path prices
  **0.00% vs 3.50%**. **ONE TEST RESTORES OR KILLS IT: five-class at nA=1 with divergence selection
  OFF.**
- **ORDER OF OPERATIONS, adopted from RR, superseding the previous approval:** (1) fix the forcing
  defect — **for a partial override the shared class is UNIQUE (`w0 ∩ w1` has size exactly 1), so
  DERIVE it; handle the empty case for disjoint rather than disabling the parameter for every
  override**; (2) re-price BOTH arms with the amplifiers on for each; (3) reconcile RE and RR on
  one shared sample under D19; (4) **only then** ask whether the inversion exists.
- **All three nA=4 predictions are committed and unrelayed** — LS, RE and RR all predict reversal,
  differing on magnitude. **The measurement's JOB has changed: it is no longer a prediction test,
  it must settle a contradiction between two peers and a suspended ratio.** That is a better reason
  to run it than the one originally given.
- **RR declared a bias unprompted and against their own ranking** — the zero-best-case cuts against
  the option they ranked first, and they found it while testing LS's H2 rather than while defending
  their position. **Second declared-then-scored bias on the record this phase.**

### 2026-08-08 — SIX-CLASS FIGURES INVALIDATED. The debt list predicted this exact failure

Records: RE's round-trip test; RR's `records/L9/nA4_realism_RR.md`;
`records/L9/L9_decisions_LS.md` D41–D44.

- **★ THE WARNING WAS IN THE RECORD, WITH ITS TRIGGER, AND NOBODY RE-READ IT.**
  `RESEARCH-CRON-STATUS.md` §5, written before any six-class work: *"`_designate_swap_pair` is a
  second source of truth for roles the template already declares. It agrees today only by
  construction. **It must be retired if the lattice changes.**"* **The lattice changed. It was not
  retired.** `coverage_override` routed to it, and **it SEARCHES for a two-holder class instead of
  reading declared positions:**

      natural    pred=w0, succ=w1, shared=retail      ceiling 0.00%
      override   pred=w1, succ=w2, shared=corporate   ceiling 7.08%

  Same lattice, different roles. **Every L9 size-3 template declares roles POSITIONALLY and the
  carrier stratification is DEFINED on those positions — so the templates being priced were not the
  templates being described, and nA was measured against the wrong class.**
  **RULE RAISED for `METHODOLOGY_RULES.md`: when a step changes something the technical-debt list
  conditions on, the debt list is RE-READ as part of that step.** A conditional warning with no
  trigger attached fires after the damage.
- **INVALIDATED pending re-run:** the step-4 table, the carrier means, the inversion, the cap sweep,
  the forced-mix sweep, and the D26 forcing result. **SURVIVES:** the carrier confound proof (pure
  enumeration), the belief-model fix and its acceptance, the tie-break, **and everything
  five-class** — the natural path never entered that function.
- **THIS LIKELY DISSOLVES THE PEER CONTRADICTION RATHER THAN RESOLVING IT.** If RR assigns roles
  positionally and RE did not, that alone explains card-silent LOW for one and HIGH for the other
  under the same tie-break. **The inversion may never have needed H1 or H2 — it may be an artefact
  of role assignment, which is H3, raised and then not pressed.** RE states RR's figures are the
  ones more likely to be right.
- **RE's own note, kept because it is the useful part:** the function they had written up in
  `records/L9` as *"dead code, not on the template path"* **was true of the template path and false
  of the override path — the one they then built every six-class figure on. The correction they
  wrote for that record is the source of the error.** Third time this phase of generalising from
  the population in front of them; **found by a round-trip test they did not have to run.**
- **RULING 1 — ALIGN THE RNG STREAM; THE RE-RUN IS PAIRED.** `rng.shuffle` consumes the stream on
  the natural path and not the override path. **Consume identical draws on both, discarding where
  unused — common random numbers, not tuning: the arms then differ in THE LATTICE AND NOTHING
  ELSE.** **Assert the alignment at generation.** This is the third silent divergence between those
  paths (forcing, roles, RNG) and the next one should raise.
- **RULING 2 — SURVIVORSHIP IS CHARACTERISED, NOT REPORTED.** **28 of 60 seeds fail generation on
  the override path and none on the natural path**, and it is already known not to be benign
  (forced-mix survivors 2.68% vs 1.89% for the full population). (1) **Compare on the INTERSECTION,
  paired**, stating the drop. (2) **Diagnose on the arm where the dropped seeds ARE measurable** —
  natural-path ceilings, 28 failing vs 32 surviving. **No difference → benign and say so;
  difference → every six-class figure is conditional on a biased subpopulation and carries that.**
  (3) **Say which assertion fails and why.**
- **★ RR's REALISM RESULT SURVIVES AND REFRAMES THE DECISION.** They granted the prior and refused
  the inference: 44% of a book in one class is ordinary (Pillar 2 exists because it is the norm),
  **but the design needs the book concentrated IN THE CLASS WHERE THE STAFFING CHANGE BITES** —
  a different proposition. **STAFFING FOLLOWS VOLUME:** the dominant exposure is the BEST-covered;
  sole coverage attaches to **niches**, where one approved reviewer is normal because volume does
  not justify two. **Concentration and thin coverage are NEGATIVELY correlated in practice and the
  design needs them maximally POSITIVELY correlated. The realistic nA is 1.**
- **THREE amplifiers, not one** (RE's count confirming RR's two): segment count, divergence
  selection on that class's ratings, **and IRB-approval priority** — all gated on `shared_class`.
  **"4 of 9 segments in one class" understates it: the ratings inside the concentrated class are
  selected adversarially and its segments are approved for IRB first.**
- **★ AND IT IS A CONDITION ON A SHARED HEADLINE, NOT AN ARGUMENT BETWEEN THE OPTIONS:**

      disjoint, nA=4 (forced)     0.0851 of oracle   1.11 sigma   ~13 episodes/arm
      disjoint, nA=1 (realistic)  0.0347 of oracle   0.45 sigma   ~64 episodes/arm

  **Realism costs the DISJOINT template 2.4× in effect and ~6× in n — same mechanism and magnitude
  as it costs size 3.** *"13 episodes per arm"* is a statement about a book whose dominant business
  line has one qualified reviewer. **ADOPTED: nA=1 PRIMARY, nA=4 a DECLARED UPPER BOUND, all three
  amplifiers declared whenever a forced figure is quoted.**
- **NEW LEVER, COMMISSIONED: buy detectability with BOOK SIZE rather than CONCENTRATION.** The
  effect as a share of oracle is scale-invariant while the allocation component of σ falls ~1/√n,
  **so a bigger book at a realistic niche concentration gains sensitivity WITHOUT touching the
  mix.** RR bounds it themselves: only the allocation component shrinks (~0.041 of a published
  0.0768), so the gain is **sub-√n**, and bigger books cost episode length and a more expensive
  exact DP. **First proposal this phase that buys sensitivity without spending realism.**
- **LOAD-BEARING JUDGEMENT, LABELLED AS ONE:** *"staffing follows volume, so sole coverage attaches
  to niches"* is a judgement about how institutions staff, **not a measurement.** RR holds it
  firmly, LS holds it too, and **it goes to the researcher AS A JUDGEMENT rather than folded into
  the numbers around it.**

### 2026-08-08 — the inversion DISSOLVES; the headline moves toward partial overlap but is misstated

Record: `records/L9/L9_decisions_LS.md` D45–D50; RE's path-alignment fix and re-price.

- **FOUR PATH DIVERGENCES, ALL ONE DEFECT CLASS: `if coverage_override is None` guards on logic
  that has nothing to do with where the lattice came from** — mix forcing, role assignment, the RNG
  label draw, and **the TOTALITY REPAIR (sole-class rating re-draw)**. **General form: a guard keyed
  on the PROVENANCE of an input, applied to logic that does not depend on provenance.**
- **★ RULING 2 DISSOLVES rather than needing its diagnosis. The 28-of-60 survivorship filter was
  NOT a design fact about six classes — it was a repair switched off for every instance six classes
  can be built from.** Round-trip 32/60 with 6 of 10 ceilings mismatching → **60/60 with ZERO
  divergent fields**; paired exclusion 6/240 → 1/240.
- **The checkpoint is read from `getstate()` rather than by drawing a probe** — a probe would
  advance the stream and **silently move every five-class figure already reported**, making the
  alignment check the cause of the next divergence. **`check_path_alignment.py` is the acceptance:
  a fifth divergence now FAILS A CHECK instead of being found while fixing the fourth.**
  **RULE (RE's, adopted): when an input path is first used to produce a REPORTED number,
  round-trip it.** All four would have been caught by that test.
- **★ THE INVERSION IS NOT A PHENOMENON — it was the MIX, and it follows from the carrier confound
  already proved.** The amplifier forces the SHARED class; **for carrier-1 templates the shared
  class IS the successor-unique class (so nA=4 automatically), for carrier-2 it is not (nA stays 0
  or 1).** The groups **never shared a mix**. **So H1 and H2 were falsified against something that
  did not exist and H3 accounts for the whole of it** — the carrier confound and the inversion are
  ONE fact. **RR's failure to reproduce it was the correct result, not a sampling difference.**
- **★ BUT THE CORRECTED TABLE DOES NOT SUPPORT ITS OWN ORDERING CLAIM — same confound, one level
  up.**

      carriers=1 @ nA=4   0.18x     carriers=2 @ nA=1   0.72x     carriers=2 @ nA=0   0.55x

  **"Matched mix" matches each size-3 cell to DISJOINT at the same nA. It does NOT match the two
  CARRIER GROUPS to each other — 0.72× is at nA=1 and 0.18× is at nA=4.** Normalising by
  disjoint@nA neutralises the mix only if the nA-response is a common multiplicative factor, and
  **it demonstrably is not: forcing HALVES size-3 while roughly TRIPLING disjoint**
  (0.0347 → 0.0851). **RULING: no ordering claim between the carrier groups until both are measured
  AT THE SAME nA. The missing cell is `carriers=1 @ nA=1`, and it is reachable.**
- **★ THE HEADLINE IS REAL AND MISSTATED: 0.72× is a CARRIER-2 figure, not a size-3 figure.**
  Size-3 is **2,160 carrier-1 and 4,320 carrier-2**, so a pooled number is a weighted mix and sits
  **below 0.72× if carrier-1 at nA=1 is lower.** Correct sentence today: *at the realistic mix, the
  CARD-SILENT HALF of the size-3 design reaches 0.72× the disjoint channel.* **The direction is
  genuinely good — the trade-off may be a quarter of the channel rather than two-thirds — but the
  number that would say so does not exist yet.** **Third time this phase a group mean has been
  quoted as a design property; the fix is to name the subpopulation in the sentence.**
- **PREDICTIONS: none cleanly confirmed; NOT reported as a prediction test.** **LS REFUTED by a
  factor of four** (predicted ≥0.7 for size-3-at-nA=4 vs disjoint-at-nA=4; the cell is 0.18×).
  **RE** lands near 0.72 and **declines to claim it** — predicted for the wrong mechanism, with an
  intervening "refuted" verdict computed on void figures. **RR** holds at nA=4 and fails at nA=1.
  The measurement's value was settling a contradiction and an invalidation, which it did.
- **ORDER TO THE PACKAGE: (1) the missing `carriers=1 @ nA=1` cell; (2) D40 — five-class at nA=1
  with divergence selection OFF, on positional roles and aligned streams; (3) then the researcher.**
- **Five-class regression across all of it: NOTHING MOVED.** Pricing 0.85/9.57/0.00, selection 21
  seeds [7, 20, 30], belief acceptance PASS/PASS, tie-break exposure closed, tests 3 passed.

### 2026-08-08 — book-size lever priced DOWN by its proposer; the DP cost does not bind; D47 unblocks

Record: `records/L9/booksize_lever_RR.md` (RR); `records/L9/L9_decisions_LS.md` D51–D54.

- **★ THE DP COST DOES NOT BIND, AND THIS SURVIVES UNCONDITIONALLY.** The capacitated optimum is a
  **transportation problem** — with three workers, an exact DP over `(used_0, used_1)` in
  **O(n·cap²)**. Positive-controlled against the shipped 1,680-allocation enumeration on 10 seeds ×
  both belief models: **max difference 1.78e-15.** **72 segments cost the same as 9.**
  **The enumeration has been read as a mathematical limit on book size and it is an IMPLEMENTATION
  CHOICE** — book size is not compute-bounded anywhere in this study.
- **THE LEVER ITSELF DOES NOT CHANGE THE OPTION SET.** Effect share is scale-invariant and
  `sd_alloc` falls as ~1/√k (0.33 at k=8 vs 1/√8 = 0.354) — **both exactly as predicted, and both
  irrelevant, because the allocation component is 25% of the variance:**

      sigma_total 0.0768 (published)   sigma_alloc 0.0384 (measured)   sigma_manager 0.0665
      8x book, manager variance PER-EPISODE   -> detectability x1.01, n/arm x0.98   NO GAIN
      8x book, manager variance PER-DECISION  -> detectability x2.56, n/arm x0.15
- **RR CORRECTED THEIR OWN PROPOSAL: "real but sub-√n" becomes "may be ZERO"**, and named the error
  — **pitched on the component they could measure without weighting it against the one they could
  not.** Same shape as the episode-count error, from the other direction, **caught by the proposer.**
- **THE CATCH-22, named because it recurs: pricing the lever requires the measurement it exists to
  make affordable.** Separating per-decision from per-episode manager variance needs σ at two book
  sizes, which needs runs. **The corpus cannot settle it** — all 18 bundles are 9-segment.
  **STANDING RIDER: if any run is authorised, ONE cell at 2× book size goes with it** (at k=2 the
  bounds are 1.08 vs 1.43, so a single cell discriminates). **Goes to the researcher inside the run
  package, not as a separate ask.**
- **★ D47 UNBLOCKS: FORCING TARGETS THE SUCCESSOR-UNIQUE CLASS, NOT THE SHARED CLASS.** Verified
  20/20 — **in `_lattice_from_template` the shared class IS the successor-unique class post-swap**
  (`w1` sole-holds A once `w0` leaves, by construction), so `"shared_class"` is a name that merely
  **coincides** with "successor-unique" in that one template. **Targeting successor-unique directly
  is therefore NOT a departure from the five-class arm — it is what the five-class arm ALREADY
  does, matched by MECHANISM instead of by LABEL.** And it **breaks the carrier/nA lock without a
  new asymmetry**, so **`carriers=1 @ nA=1` is reachable and D47's missing cell can be measured.**
  **A case where matching the NAME across arms would have been the error.**
- **RR's AMENDMENT TO THE DEBT-LIST RULE, adopted over LS's version: the trigger must be
  MECHANICAL, or the rule is the same class as "run a positive control" and fires only when someone
  remembers.** Their form: **the debt entry names its CONDITION in a form a step can CHECK.**
  **This is exactly what voided the six-class figures** — §5's *"must be retired if the lattice
  changes"* was a correct condition, in prose, checkable by nobody.
- **ORDER, now unblocked:** (1) `carriers=1 @ nA=1`, forcing on successor-unique; (2) D40 —
  five-class at nA=1 with divergence selection OFF, positional roles, aligned streams; (3) package
  to the researcher.

### 2026-08-08 — THE MATCHED-CELL RATIO EXISTS; and the six-class path is rebuilt BEFORE the package

Record: `records/L9/L9_decisions_LS.md` D55–D57; RE's L9-aa/ab/ac.

- **★ THE RATIO, at genuinely matched mix, on ONE path, nA=1, unamplified throughout:**

      disjoint size-2 @ nA=1               4.76%
      size-3 carriers=1 (card NAMES)       1.31%    0.28x
      size-3 carriers=2 (card SILENT)      4.24%    0.89x
      size-3 POOLED (4320:2160)            3.26%    0.69x

  **Card-SILENT is 3.2× card-NAMES — RR's direction. The inversion was ENTIRELY the mix**, and the
  mechanism is clean: **amplifying pulls segments INTO the shared class, which for card-silent is
  NOT the successor-unique one, draining nA from 1 to 0 in 103 of 119 cells. The amplifier actively
  HARMS the group whose value lies in the omission.**
- **`amplify_mix=False` is DELIBERATE, SYMMETRIC absence — a different object from the silent
  asymmetry it replaces.** And **the reference was matched too**, closing the error one level up:
  the old 3.84% came from substitution onto instances amplified on the FIVE-class template's shared
  class; regenerated through the same path it is **4.76%**. **Free consistency check: amplified and
  unamplified are IDENTICAL for the disjoint template, which has no shared class for the amplifier
  to act on.**
- **THE DEFENSIBLE SENTENCE, subpopulation named: *at the realistic mix the CARD-SILENT HALF of the
  size-3 design reaches 0.89× the disjoint channel; size-3 AS A WHOLE reaches 0.69×.*
  This SUPERSEDES both 0.72× and 0.35–0.49×.** LS's expectation that carrier-1 would drag the pool
  down holds — **0.28×**.
- **§B FLAG: the disjoint reference appears as 4.76% AND 5.03% in one message** (presumably nA=1 vs
  all-cells). **Two values for one named quantity is what §B exists for — the package names the
  population for each or quotes neither.**
- **★ RULING (D56): REBUILD THE SIX-CLASS PATH BEFORE THE PACKAGE.** RR's structural challenge, and
  LS's approval of `check_path_alignment` did not see it: **a parity check that can only run where a
  natural counterpart EXISTS cannot certify the case that has NONE.** It proves parity for
  five-class lattices and **cannot test a six-class lattice at all.** **The blind spot is exactly
  where the risk is.** Base rate: **the path is documented as *"never used by study instances"* — an
  S5 negative-case fixture — and has leaked FOUR mechanisms. Four found is not evidence the list is
  complete.**
  **Fix: extend `ASSET_CLASSES` and build the six-class lattice through `_lattice_from_template`
  the way the five-class one is built, so every mechanism applies BY DEFAULT and nothing must be
  remembered.**
  **Why before: we would hand the researcher a decision that COSTS A SIXTH ASSET CLASS, resting on
  a path not meant for study use, which has leaked four mechanisms, and which cannot be checked for
  a fifth by the acceptance we have. "Do not build on an unverified instrument" is the rule this
  phase exists to enforce — sending the package first breaks it at the last step.**
  **Cheap, and it carries its own test:** five-class figures untouched (they never used that path);
  the `rng.shuffle` asymmetry removed **structurally** rather than by a discard patch;
  `check_path_alignment` becomes **meaningful** for six classes; and **the re-price IS the
  acceptance — it either reproduces 0.69×/0.89× or it does not.** **Scope is the generator path
  only**; decisions, belief model, tie-break, realism analysis and enumeration all stand.
- **D40 MAY ALREADY BE ANSWERED — one question settles it: does `amplify_mix=False` disable ALL
  THREE amplifiers (segment count, divergence selection, IRB approval priority) or only the count?**
  **All three → the 4.76% reference IS the divergence-selection-off number, D40 is answered, and
  D39's SUSPENSION OF THE MATCHED-CELL RATIO LIFTS.** Count only → D40 runs after the rebuild.
- **STANDING PRINCIPLE (RR, second time today): on a path documented as never used by study
  instances, FOUND FAULTS BOUND NOTHING.** First raised on the truncation audit's limits.

### 2026-08-08 — ★ RETRACTION: the 0.69× table. And the carrier contrast leaves the decision path

Record: `records/L9/matched_mix_check_RR.md` (RR); `records/L9/L9_decisions_LS.md` D58–D63.

- **★ RETRACTED IN FULL: 0.28× / 0.89× / 0.69× and "card-silent is 3.2× card-names".** RR measured
  nA through **RE's own `build_size3`**, on RE's templates and seeds:

      carriers=1 (n=120)   nA = 4 in 100% of cells
      carriers=2 (n=119)   nA = 0 in 87% (103/119), nA = 1 in 13%

  **RE reported nA=1 in 100% of BOTH groups. It is 4 versus 0 — opposite extremes**, not merely
  different. **And 103/119 is exactly RE's own figure for amplification draining nA to zero, so the
  path presented as `amplify_mix=False` appears STILL TO BE AMPLIFYING.** LS's D47 objection was
  right and **understated** — argued as "different mixes", actually the two ends of the range.
- **★ THIRD CONSECUTIVE WITHDRAWAL OF THIS NUMBER** (0.35–0.49×, then 0.72×, now 0.69×) — **and all
  three came from someone checking a COMPARATOR rather than an arithmetic step. Not one was an
  arithmetic error.** That is this project's failure mode, stated as plainly as it can be.
- **A SECOND GAP, and it is NOT the tie-break: 4.24% is outside the entire achievable range.**

      tie-break      carriers=1   carriers=2          RR's code matches the shipped scorer to
      best-case          1.59%        0.00%           every printed digit on a NAMED CELL:
      expectation        1.59%        1.33%           share 0.008846, oracle 8.188185,
      visit order        1.59%        0.57%           tie set 350, min 0.0, max 0.022115
      worst-case         1.59%        2.95%
      RE reported        1.31%        4.24%    <- outside 0.00-2.95%

  **That cell is in the record as a DIFF TARGET so this is localised rather than two people trading
  aggregates.**
- **★ A CONFOUND THE REBUILD WILL NOT FIX: the tie-break rule moves ONE group and not the other.**
  **Carrier-2's believed-optimal tie set averages 235.4 allocations against carrier-1's 12.7 —
  19×.** **Carrier-1's ceiling is 1.59% under ALL FOUR rules** (harmless tie set: every member
  scores identically under truth); **carrier-2's spans 0.00%–2.95%.** Independent of mix and of the
  builder, and **not a clone artefact** — coverage size 3 alone produces the indifference.
- **★ RULING (D61): THE CARRIER CONTRAST LEAVES THE DECISION PATH.** **The decision needs POOLED
  size-3 vs disjoint at a realistic mix. It has NEVER needed carrier-1 vs carrier-2.** That contrast
  produced the inversion, H1/H2/H3, the definitional confound, the mix mismatch and now the tie-set
  asymmetry — **it entered as a guard against a pooled average hiding structure, a good instinct,
  and became the thing generating the structure.**
  **DELIVERABLE: pooled size-3 vs disjoint, at nA=1, with intervals.** The carrier split is reported
  **descriptively, with its tie-set asymmetry stated and NO ordering claim between the groups.**
  **D47's missing cell (`carriers=1 @ nA=1`) is NO LONGER A BLOCKER** — it was needed only for a
  contrast no longer being made.
- **★ THE REBUILD IS NOW THE ONLY ROUTE, NOT A PRECAUTION (D62).** **Five rounds of "fixed, and here
  is the next thing that was silently off": forcing, roles, RNG, totality repair, and now the
  amplification state itself.** **NOTHING FURTHER IS PRICED ON THE OVERRIDE PATH.**
- **RR's caveat on their own record, adopted:** their nA figures are measured **through the builder
  as it stands**, so they read *"as of the current builder"* rather than as a property of the
  templates. **They get re-measured after the rebuild — including the ones that just withdrew the
  table.**
- **PREDICTIONS FINAL: LS REFUTED; RE unclaimed (right number, wrong mechanism, void figures in
  between); RR NO-VERDICT** — theirs was conditioned on the inversion being real, **the premise
  dissolved rather than the prediction failing, and they declined a hit at nA=4 that was
  available.**

### 2026-08-08 — the grid completes (PROVISIONAL); the rebuild's scope DOUBLES to both arms

Records: `records/L9/matched_grid.json` (RE), `records/L9/reference_audit_RR.md` (RR);
`records/L9/L9_decisions_LS.md` D64–D69.

- **THE CARRIER/nA LOCK IS BROKEN** (forcing targets the successor-unique class, D53) **and the
  full grid exists:**

      RATIO TO DISJOINT AT THE SAME FORCED COUNT
         card-NAMES     0.33x @ nA=1     0.17x @ nA=4
         card-SILENT    0.88-0.92x       1.01-1.07x   <- PARITY at nA=4
         POOLED         0.70-0.73x       0.73-0.77x

  **Card-silent beats card-names at BOTH mixes and the gap WIDENS with nA** — 2.6–2.8× at nA=1,
  5.9–6.2× at nA=4. **Card-names is nearly flat in nA (1.33 → 1.59); card-silent scales strongly
  (3.51 → 9.35).**
- **★ THAT IS THE MECHANISM RE PROPOSED AND THEN WITHDREW ON CONFOUNDED EVIDENCE. It was right.**
  The mix lock made it untestable and the apparently-refuting run carried the same lock.
  **RECORDED AS ITS OWN FAILURE MODE: a RETRACTION can be as unfounded as the claim.** This project
  has been careful about adopting claims and not at all careful about withdrawing them.
- **★ THE GRID IS PROVISIONAL AND IS NOT CALLED DEFENSIBLE.** It is measured on the override path —
  wrong five times, sixth fault unbounded. **0.35–0.49× → 0.72× → 0.69× → 0.70–0.77×: the
  QUALITATIVE story has held across all four and the MAGNITUDE has moved every time.** Three
  independent constructions now agree on ~0.7× pooled, which makes it the best current estimate.
  **It is not what goes to the researcher.**
- **★ THE REBUILD'S SCOPE DOUBLES: THE DENOMINATOR IS ON THE OVERRIDE PATH TOO.** RE regenerated the
  disjoint reference through `coverage_override` to escape the substitution asymmetry — **putting
  the ratio's denominator on the path nothing may be priced on. The disjoint arm is NOT safe for
  being five-class.** And there is no native escape: **`_lattice_from_template` only ever produces
  `{A,E},{A,B},{B,C},{C,D}`, so NO candidate template can be built natively.**
  **RULING: the rebuild makes the LATTICE A FIRST-CLASS GENERATOR PARAMETER, with the current
  five-class template as one VALUE of it. No override path, no privileged path, NO PROVENANCE FOR A
  GUARD TO KEY ON** — all five faults were `if coverage_override is None`, and this **deletes the
  condition rather than auditing its uses**, which is the only fix that does not require having
  found the last fault.
- **★ DISJOINT'S AFFORDABILITY CASE IS AN ARTEFACT OF SUBSTITUTION.** Generated natively and
  unamplified, disjoint spans **nA ∈ {1,2} and tops out at 6.09%**. **The 9.03% at nA=4 requires the
  NATURAL template's amplified shared class to coincide, BY LABELING, with the DISJOINT template's
  successor-unique class** — and that is where the ~1.11σ / **~13-episodes-per-arm** figure lives.
  **Combined with the realism result, disjoint's best case is BOTH anti-realistic AND a construction
  artefact. Stop quoting 13 episodes/arm.**
  **Pattern worth noting: the comparison has moved toward size 3 three times, and every time by
  removing an advantage disjoint never had rather than by finding one size 3 does.**
- **★ RR's SHARPENING OF THE COMPARATOR OBSERVATION, ADOPTED — and it applies to the rule they
  already wrote.** All withdrawn numbers failed the same specific way: **a population named by the
  property being MATCHED ON while the CONSTRUCTION that produced it went UNNAMED** — substitution vs
  generation, amplified vs not, derived vs declared roles, five-class-natural vs six-class-override.
  **Four instances.** RR wrote the provenance rule about record FIELDS while the same failure was
  live in the COMPARATORS. **NEW RULE: a comparator NAMES ITS CONSTRUCTION PATH, or the comparison
  is not reportable.** The population requirement gains a field — **"nA=1" is 576 substituted cells
  at 3.84% AND 960 generated cells at 4.76%: one name, two populations.**
- **CLOSED: `irb_approved` and `applicable_approach` are the same predicate, agreeing 270/270**, so
  the nA=4-vs-nA=0 discrepancy is NOT a predicate difference and stays with RE's single-cell diff.
- **D40 runs NOW, on the safe path** — five-class natural, never touched by the override fault,
  regression-locked bit-identical. **Its answer survives the rebuild.**

### 2026-08-08 — ★ CORRECTION TO LS's SUMMARY: the two columns are not commensurable

Record: `records/L9/L9_decisions_LS.md` D70–D71. **A correction to a SENTENCE rather than a number,
raised by RR, accepted in full — and the sentence had already reached the researcher.**

- **LS wrote: *"the comparison has moved toward size 3 three times, every time by removing an
  advantage disjoint never had."* TRUE OF THE POINT ESTIMATE, FALSE OF THE TOTAL EVIDENCE.**

      TOWARD size 3 -- all three MOVE THE ESTIMATE
        the mix confound (0.35-0.49x understated it)
        the override path's disabled amplifiers (size-3 priced unamplified)
        the nA=4 substitution artefact (disjoint's best case is not native)

      AGAINST size 3 -- all three UNDERMINE WHETHER AN ESTIMATE EXISTS
        the tie-break band, +/-4-7%, where size-2 is EXACTLY 0.00% spread on 10/10
        the ZERO BEST-CASE on every sampled instance -- no guaranteed positive ceiling
        the 19x tie-set asymmetry -- size-3's ceiling is rule-dependent, size-2's is not

  **They must not be netted. "0.88×" and "the ratioed quantity spans zero to 5% depending on a
  tie-break rule" are not two facts to average — the second is a CONDITION ON the first.**
- **THE SENTENCE THAT REPLACES IT (RR's), in the record and in the package: *the POINT ESTIMATE has
  moved toward size 3 three times; the case that size 3 HAS a well-defined point estimate at all
  has weakened three times.***
- **★ AND THE REALISM FINDING IS NOT A MARK AGAINST DISJOINT.** It costs disjoint 2.4× in effect and
  ~6× in n — **the same mechanism and magnitude it costs size 3** — so it belongs in the *condition
  both options share* column. **LS put it in the disjoint-loses column by MERGING it with the
  substitution artefact, which IS asymmetric.** Two findings, one symmetric; the merge favoured the
  option LS and the researcher both prefer.
- **RECORDED AS A BIAS INSTANCE ON LS. No figure was wrong; the FRAMING was — and framings are what
  survive into a package.** RR's stated reason for raising it: *"the evidence keeps favouring size 3
  is exactly the shape of thing that becomes a prior nobody re-examines — and I'd be the one who let
  it, having supplied most of both halves."*
- **LS refinement, offered as a refinement and cutting both ways: counting findings is a weak way to
  weigh evidence here.** The three "against" are three consequences of ONE mechanism (coverage size
  3 producing massive believed-indifference); the three "toward" are three consequences of ONE
  mechanism (the override path's asymmetries). **Neither column is three independent facts;
  "three each" is not load-bearing in either direction.** RR's commensurability point carries the
  correction regardless.
- **RR's RANKING REACHES THE RESEARCHER AS ORDERING PLUS CONDITION, never the ordering alone.**
  They still rank partial-overlap-at-3 above disjoint-at-2, **but the contingency attached at the
  outset has GROWN rather than resolved: it was conditional on size-3 clearing detectability, and
  we may not be able to TELL whether it does, because the interval's lower end is ZERO.**

### 2026-08-08 — ★ THE RETRACTION IS WITHDRAWN: RE and RR ran DIFFERENT BUILDERS

Record: `records/L9/L9_decisions_LS.md` D72–D75.

- **NOBODY WAS WRONG.** RR's diff-target cell reproduces on RE's machine **to every digit** — on
  `check_size3_pricing.build_size3`, the **OLD** builder (share 0.008846, oracle 8.188185, ties 350).
  **RR's nA=4/nA=0 is builder A's mix, and it is exactly what `check_size3_pricing` printed in its
  own output. 4.24% lies outside builder A's achievable range BECAUSE IT IS NOT A BUILDER A
  NUMBER.**
- **RE's share:** they sent RR *"seeds `range(10)`, `size3_templates()`"* and **never said the
  BUILDER had changed** — same template list, different generator call. **Naming the population and
  not the instrument, in the one place §B had been applied all day.**
- **★ LS's share is worse: D64 recorded that "a retraction can be as unfounded as the claim",
  generalising from RE withdrawing a correct mechanism — and D58, LS's retraction of D55, is an
  instance of exactly that, committed ONE ADDENDUM EARLIER without noticing.** Neither LS nor RR
  checked which builder produced the numbers before acting on the mismatch.
- **RULING: D58's RETRACTION IS WITHDRAWN. D55 stands as SUPERSEDED, not wrong** — D64's grid is a
  fuller measurement of the same thing and the provisional status applies to both. **The record must
  not say RE published a wrong number, because they did not.**
- **THE COMPARATOR RULE TAKES ITS FIFTH INSTANCE WITH A WIDENED SCOPE: "construction path" includes
  THE BUILDER FUNCTION, not only the generator path.** *(And putting a NAMED CELL in the record as a
  diff target, rather than trading aggregates, is what made this a two-minute check instead of a
  day. Repeat it by default.)*
- **D40 ANSWERED, D39's SUSPENSION LIFTS. Measured, not read:** `amplify_mix=False` sets
  `shared_class = None` and **all three amplifiers gate on it** — count goes round-robin, divergence
  flag False, IRB priority one-per-class with no ordering. **So the 4.76% reference IS the
  divergence-selection-off number.** RE is running D40 explicitly anyway rather than arguing from a
  related result.
- **★ RE CUT THEIR OWN REFERENCE OUT FROM UNDER THEMSELVES:** *"if natively-generated unamplified
  disjoint tops out at 6.09%, the denominator in every ratio I have quoted is inflated, and the
  ratios are correspondingly understated."* They could have defended the numerator against a doubted
  denominator and did not.
- **★ RR's OPPOSITE-FUTURES ARGUMENT, adopted, and it changes the DELIVERABLE.** The two mechanisms
  behind the two evidence columns have opposite futures: **the override path is being DELETED, so
  its findings are SPENT and already banked; coverage-size-3 believed-indifference is INTRINSIC and
  the rebuild does not touch it** — a worker covering 3 of 6 classes makes more allocations
  indistinguishable under the card than one covering 2 of 5, **arithmetic about the lattice, not the
  code path**, measured on a five-class size-3 template with no clone (3.94% spread, 10/10).
  **So *"the qualitative story held every time and the magnitude moved every time"* is EXPECTED, not
  reassuring: the magnitude moved because the override path injected error; the direction held
  because it was never downstream of that path. THE FOURTH VERSION BEING RIGHT ABOUT DIRECTION IS NO
  EVIDENCE THE FIFTH IS RIGHT ABOUT SIZE.**
- **★ THE DELIVERABLE'S SHAPE CHANGES, adopted: an INTERVAL PLUS A STATEMENT OF WHAT DECIDES WHERE
  YOU LAND IN IT — not a number with error bars.** RE is to build toward that object from the start
  rather than converting at the end.
- **PREDICTIONS ON THE REBUILD, both committed before it lands, and they DISAGREE:**
  **RR — the point estimate moves LESS than the last three revisions and the interval does not
  narrow at all** (falsifier, theirs: a materially narrowing interval refutes their account of the
  ambiguity's source).
  **LS — the nA=1 row is STABLE (pooled moves <~15% relative, agreeing with RR); the nA=4 row is
  NOT, and "parity at nA=4" is the claim at risk, because disjoint's nA=4 is NOT NATIVELY REACHABLE
  (native spans nA ∈ {1,2}, topping at 6.09%). A denominator that only exists under substitution
  cannot survive a rebuild that removes substitution.** Refutable by that column surviving
  unchanged. **A disagreement to settle rather than a joint expectation to confirm.**

### 2026-08-08 — ★★ D40: THE SHIPPED LATTICE MEASURES NOTHING AT A REALISTIC MIX

Record: `records/L9/L9_decisions_LS.md` D76–D80. **Five-class NATURAL path — survives the rebuild.**

    arm                              cells   nA achieved       mean    nonzero
    amplified, segs=4 (as shipped)      60      {4: 60}       1.24%     34/60
    amplified, segs=1                   60      {1: 60}       0.00%      0/60
    UNAMPLIFIED (all three off)         60  {1: 48, 2: 12}    0.00%      0/60

- **★ THE 1.24% HEADLINE IS A FORCED-MIX ARTEFACT.** At matched nA=1 the amplifiers make no
  difference — 0.00% vs 0.00% — **not because they are inert but because BOTH ARE ZERO.**
  **The entire 1.24% lives at nA=4, which requires forcing four of nine segments into one class.**
  **On the realism finding that nA=1 is the realistic mix, the lattice we currently ship measures
  EXACTLY NOTHING on a realistic portfolio.**
- **THE MECHANISM, following from what was already proved:** `_lattice_from_template` gives
  `w0 ∩ w1 = {A}`, so **the shipped lattice is structurally a CARD-NAMES lattice** — the stale card
  **correctly describes the successor's critical qualification.** The card is only wrong about
  things that do not bind, **except when capacity is forced and 4 segments compete for 3 slots, at
  which point the false claims displace. The 1.24% is CAPACITY DISPLACEMENT under a forced
  concentration, not a coverage channel.** **Nothing prior is contradicted — it is re-described;
  34/60 nonzero at nA=4 is the original counterfactual unchanged.**
- **★ RE's REFRAMING SUPERSEDES BOTH FRAMINGS, LS's INCLUDED. Against ZERO, a ratio is UNDEFINED.**
  The question was never *"how much channel does a candidate buy relative to disjoint"* — it is
  **"does ANY lattice have a channel at a realistic mix at all."** **LS's "partial overlap costs a
  fraction of the disjoint channel" was measuring the wrong thing even where the arithmetic was
  right** — and LS was the one enforcing that framing on everyone else.
  **The decision is not how much sensitivity we trade for realism; it is that the realistic mix
  currently yields ZERO and the candidate lattices are the only route to a non-zero measurement on
  a realistic portfolio. That does not depend on the six-class arm at all.**
- **PROVISIONAL, override-path, flagged: at nA=1 the candidates are 3.98% (disjoint) and ~3.5%
  (size-3 card-silent) against the current template's 0.00%.** If those survive even approximately,
  **the comparison that matters is CANDIDATE-vs-CURRENT, not candidate-vs-candidate.**
- **★ RULING (D78): the rebuild is scoped to CURRENT vs CANDIDATES at nA=1, natively, FIRST.**
  Same build; it changes which comparison comes out first. **It answers whether the study can
  proceed at all** (no lattice with a channel at nA=1 = no manipulation at a realistic portfolio,
  which is the standing escalation trigger); **it is better posed**; and **all three lattices as
  parameter values of one generator is exactly what the rebuild is for.**
  Deliverable shape unchanged: **interval plus what decides where you land in it.**
- **D39's SUSPENSION LIFTS for a stronger reason than "the amplifiers do not matter": at the
  realistic mix there is nothing to amplify.**
- **PREDICTION SHARPENED, NOT SCORED (RE declined to score LS's against their own numbers, one arm
  still being override-path): nA=4 is NOT natively reachable for the CURRENT template either — it
  requires the same forcing. So the ENTIRE nA=4 COLUMN, ON BOTH ARMS, IS A FORCED-MIX ARTEFACT
  rather than a property of any lattice.**
- **★ SENT TO THE RESEARCHER AS A FLAGGED PROVISIONAL HEADLINE — one measurement, minutes old,
  UNATTACKED.** RR asked to attack it as the now load-bearing measurement, specifically: **is
  0.00% on 60/60 a real zero or a FLOOR ARTEFACT** (that shape has fooled this project twice — see
  the `all([])` corollary and the 60/60 card claim), **with a POSITIVE CONTROL through the same
  path**; does it survive nA=2 (the unamplified arm already shows `{1: 48, 2: 12}`); and is the
  card-names-lattice inference right.

### 2026-08-08 — D40 SURVIVES: the threshold is `nA ≥ cap`; and the niche-share threshold is `1/n_workers`

Record: `records/L9/L9_decisions_LS.md` D81–D84. **Five-class NATURAL path throughout.**

- **THREE INDEPENDENT LEGS.** **(1) Dose-response — the instrument fires, so 0.00% is not a floor:**
  nA = 1,2,3,4,5 → 0.00%, 0.00%, **0.98%, 1.24%, 1.41%** (nonzero 0/60, 0/60, 42/60, 34/60, 28/60).
  **(2) Structural at 60/60:** at nA=1, **lied classes are covered by NOBODY post-swap** (misrouting
  costs nothing) and **omitted classes are covered by an INCUMBENT** (not knowing costs nothing) —
  **neither error can bind**, so the only route is displacement of the successor's uniquely-required
  segments. **(3) A prediction stated BEFORE running, confirmed exactly:**

      cap    nA=1    nA=2    nA=3    nA=4    nA=5    nA=6
        3   0.00%   0.00%   0.98%   1.24%   1.41%   1.76%
        4   0.00%   0.00%   0.00%   0.79%   1.22%   1.44%
        5   0.00%   0.00%   0.00%   0.00%   0.83%   1.19%

  **First non-zero at nA = 3, 4, 5 for cap = 3, 4, 5. THE CONDITION IS `nA ≥ cap`, NOT `nA ≥ 4`.**
  **The shipped template is IDENTICALLY ZERO below nA = cap, for a reason that follows from the
  lattice rather than from any measurement choice.**
- **★ DERIVATION (LS), MARKED AS A DERIVATION AND NOT A RESULT.** Capacity binds exactly —
  `n_segments = n_workers × cap` — so with `nA ≥ cap`:

      nA / n_segments  >=  1 / n_workers

  **Checked against all three of RE's cap values: the threshold niche SHARE is 0.333 at every one,
  INVARIANT TO BOOK SIZE.**
  **THIS EXPLAINS STRUCTURALLY WHY THE BOOK-SIZE LEVER COULD NOT HELP REALISM — scaling the book
  scales the threshold with it. The lever did not fail on the numbers; it failed on the geometry.**
  **AND IT NAMES A LEVER NOBODY HAS TOUCHED — WORKER COUNT:**

      n_workers    3      4      5      6      8
      threshold   33%    25%    20%    17%   12.5%

  **The realism argument is that sole coverage attaches to NICHES — a small share. The design
  currently demands ≥ 33%.**
  **COUNTERVAILING MECHANISM, NAMED, FROM LEG (2): the channel is already suppressed because
  omitted classes are covered by an incumbent at 60/60. MORE WORKERS = MORE INCUMBENTS = MORE
  SUPPRESSION.** The two effects push opposite ways and **LS cannot sign the net offline.**
  **DISCRIMINATING TEST, committed before measurement: vary `n_workers` ∈ {3,4,5} holding the
  lattice and the exact binding. Threshold share falling as 1/n_workers → the lever is real.
  Staying near 33%, or the ceiling collapsing at every share → incumbent suppression dominates and
  the derivation is DEAD.**
  **AND THE REALISM HALF IS RR's: if worker count IS the lever, is a 5- or 8-analyst team the same
  institution we claim to study?** More workers means more redundancy and possibly a different
  succession scenario — **the sole-holder-of-a-niche story may not survive it.**
- **`cap = 2` IS INFEASIBLE as floated** — 3 workers × cap 2 = **6 slots for 9 segments.** The
  instinct was right and generalises; **the feasible form is moving WORKER COUNT so that cap and the
  threshold share move together.** The realism question it trades into — **how many segments an
  analyst can carry** — is a different claim needing its own argument, not a transfer of the
  concentration one.
- **THE ESCALATION TRIGGER FIRES, BUT NOT IN THE DIRECTION IT WAS WRITTEN FOR.** *"If no lattice has
  a channel at nA=1, the study has no manipulation that is both valid and measurable."* **The
  CURRENT lattice does not. That is not a reason to stop — it is a reason the lattice must change,
  and it is established WITHOUT REFERENCE TO ANY SIX-CLASS NUMBER.**
- **RR's AMPLIFIER DECOMPOSITION resolves an apparent contradiction: the amplifier's value is
  ENTIRELY in MOVING nA across the threshold**, while divergence selection and IRB ordering **cost**
  ~17% at fixed nA. **So "amplification helps" and "amplification hurts" are both true, of different
  comparisons.**
- **RR's nA=2 structural zero for six-class card-NAMES now has a candidate mechanism: nA=2 < cap=3.**
  If the same threshold governs there, **the zero is EXPECTED and the 1.33% at nA=1 is the ANOMALY
  needing explanation** — which inverts which fact needs explaining. **Theirs to test against the
  rebuild.**
- **RE's DENOMINATOR CONCESSION CUTS BOTH WAYS and LS is NOT adjudicating it:** disjoint's native
  6.09% is unamplified, **so the post-rebuild comparison needs BOTH arms amplified on their own
  successor-unique class — a cell neither peer has.** Until it exists there is no basis to prefer
  either side's number.
- **ORDER: the worker-count sweep (cheap, may add an option), then the rebuild scoped to current vs
  candidates at nA=1, natively.**

### 2026-08-08 — ★★ SIZE-2 PARTIAL OVERLAP HAS A CHANNEL. The sixth asset class may be unnecessary

Records: `records/L9/d40_attack_RR.md` (RR), `records/L9/threshold_share_probe.md` (RE);
`records/L9/L9_decisions_LS.md` D85–D90.

- **D40 HOLDS, WITH A DECISIVE CONTROL.** Unamplified natural instances, coverage substituted,
  cap 3, **20 seeds × 120 labelings**:

      lattice                    nA=1                    nA=2
      current (as shipped)    0.000%  (0/1920 nz)    0.000%  (0/480)
      disjoint (candidate)    4.595%  (1920/1920)    7.038%  (480/480)
      partial (SIZE 2)        2.198%  (1920/1920)    1.059%  (480/480)

  **Non-zero on EVERY cell for both other lattices through the identical path — the measurement CAN
  return non-zero at nA=1; the shipped lattice cannot.** And **D40 does not depend on the realistic
  mix being 1 rather than 2** — both are 0.0000%, 0/60.
- **★ LS's CARD-NAMES INFERENCE WAS RIGHT AND IS NOT THE MECHANISM.** `partial` is ALSO a card-names
  lattice and prices at 2.198%. **The operative mechanism is WHICH CLASS THE LIE IS ABOUT:**
  `current` lies about a class **covered by NOBODY post-swap** — every worker falls back to SA
  equally, so misrouting costs nothing; `partial` lies about a class **`w2` covers**, which costs
  immediately. **The shipped lattice lies about the one class worthless to everybody.**
- **★★ PARTIAL OVERLAP AT SIZE 2 WAS RETIRED FOR FAILING A TEST IT DID NOT NEED TO PASS.**
  Its published *"exactly 0.00% on 30/30"* was measured on **AMPLIFIED** instances —
  amplification-dependent, read as a property of the lattice. **The combinatorial result is
  untouched and means something different: the predicate required a SOLE-HELD LIED CLASS, which is
  a class covered by nobody post-swap, which contributes NOTHING. The predicate demanded exactly
  the worthless configuration.** **LS's "partial overlap is combinatorially impossible at size 2"
  was TRUE OF THE PREDICATE and FALSE OF THE DESIGN.**

      at the realistic mix, natural path, unamplified:
         disjoint (size 2)          4.60%
         PARTIAL OVERLAP (size 2)   2.20%    ~48% of disjoint
         current (as shipped)       0.00%

  **No sixth asset class. No new lattice parameter. And it is the design the researcher preferred
  on realism grounds.** **RR declared the bias unprompted: it favours the option they have argued
  for, rests on ONE substitution measurement over 20 seeds, and needs native reproduction before it
  moves a decision.**
- **★ RULING (D88): THE REBUILD DROPS THE SIXTH CLASS.** It is still required — `_lattice_from_template`
  produces exactly one lattice, so ANY native candidate needs lattice-as-parameter — **but it no
  longer needs to teach the generator a sixth asset class, which was the expensive half and the
  thing the researcher would be committing to.**
  **(1) lattice as a first-class generator parameter, FIVE classes; (2) first output: current vs
  disjoint vs SIZE-2 PARTIAL OVERLAP at nA=1, natively; (3) six classes ONLY if all three
  five-class lattices fail.** **The admissibility predicate is RE-DERIVED from the corrected
  mechanism, not patched: the lied-about class must be COVERED BY SOMEONE post-swap — close to the
  opposite of the sole-held requirement it encodes.**
- **LS's `1/n_workers` DERIVATION: CONCLUSION SURVIVES, MECHANISM WAS WRONG.**

      n_segments  cap  threshold nA  threshold share
          8        3        3           37.5%
          9        3        3           33.3%
         10        3    infeasible

  **The threshold nA is ABSOLUTE at `cap`, not proportional to the book** — LS's *"scaling the book
  scales the threshold"* predicts it rises with `n_segments`; **it does not, and the share FALLS as
  the book grows.** **RE's tighter form adopted: threshold share = `cap/n_segments` ≥ `1/n_workers`,
  a LOWER BOUND attained only at maximum feasible book size — and 9 = 3×3 is ALREADY that optimum**
  (which is why 8 segments is *worse* at 37.5%). **Worker count is a lever only because it PERMITS
  a bigger book; you cannot buy share by growing the book alone.**
  **The test cannot run on the trusted path** (four workers fixed, `n_segments` validated 8..10, so
  `n_workers=4` needs 12) — **it is the rebuild's first output.** The incumbent-suppression
  counter-mechanism stays unsigned.
  **The realism trade is a JOINT choice of roster AND book size:** *5 analysts with a 15-segment
  book hits 20%; 5 analysts with a 9-segment book does not.* **One question to RR, not two.**
- **★ RE's EMPTY-SAMPLE NEAR-MISS — the `all([])` corollary in the wild, hours after being written,
  inside a probe whose SUBJECT is a structural zero.** `st.mean(sh) if sh else 0.0` turned **300
  failed generations** (`ASSERTION 2a`: 9 slots cannot hold 10 segments) **into a legal-looking
  0.00% at every nA.** RE nearly reported *"the channel vanishes at 10 segments"* as a finding.
  **The generator's own assertion caught what the probe swallowed — defence in depth working.**
  Reported as `n/a` with the near-miss in the record.

### 2026-08-09 — the k=5 lever improves THREE axes at once; and a contradiction that may make it moot

Record: `records/L9/worker_count_realism_RR.md` (RR); `records/L9/L9_decisions_LS.md` D91–D95.

- **LS's SUPPRESSION COUNTER IS REAL FOR A *DRAWN* LATTICE AND IRRELEVANT TO A *CONSTRUCTED* ONE.**

      k post-swap   P(a GIVEN worker sole-holds)   lattices where SOME worker does   threshold
           3               75.0%                       110/120  (91.7%)                33%
           5               23.8%                       210/252  (83.3%)                20%
           6                9.5%                       120/210  (57.1%)                17%

  The mechanism is confirmed and does not bite: **`_lattice_from_template` CONSTRUCTS rather than
  draws, and at k=5 there are 210 viable templates AT FIVE CLASSES** (e.g. post-swap
  `AB AC AD AE BC`, successor `AD` sole-holding `D`). **The lever costs NO new asset classes — the
  thing the six-class expedition was paying for.**
- **CLARIFICATION + UNIFICATION: `n_workers` is the POST-SWAP ROSTER (3), not the pool (4). And the
  old *"exactly zero at cap 5"* slack finding was measured at the shipped nA=4 — 4 < 5, so the
  threshold PREDICTS it. Two findings, one mechanism.**
- **★ THE REALISM ANSWER INVERTS THE CONCERN RATHER THAN BALANCING IT.** A bank running IRB across
  five asset classes with **three** approved reviewers is small; real credit-risk and
  model-validation functions are **5–20**. And sole coverage survives team size because **coverage
  follows SPECIALISATION, not headcount** — key-person risk exists in teams of fifty.
  **THE SHARP VERSION: at k=3 sole coverage is nearly FORCED (75% of random lattices), so it is an
  artefact of the team being TINY rather than genuine specialisation. At k=5 it becomes genuine.**

      axis                          k=3                    k=5
      team size vs real functions   small                  typical
      sole coverage                 forced by arithmetic   genuine specialisation
      niche share threshold         33%                    20%

  **Three axes improving together — every other lever this phase traded them.**
- **COSTS, stated by the proposer:** `n_segments` scales to 15 — **longer episodes and REAL RUN
  SPEND** (the exact DP is unaffected); **20% is still not a niche**, so the objection is *softened,
  not answered*; it needs the rebuild; **and the suppression counter returns for anyone who DRAWS
  rather than constructs** (83.3% at k=5 is an existence rate, not a safety margin; 16.7% at k=7).
- **★ AN APPARENT CONTRADICTION, AND ITS RESOLUTION MAY DELETE THE LEVER.** **Size-2 partial
  overlap prices 2.198% at nA=1 — BELOW the `nA ≥ cap` threshold.** Both natural path, both
  attested; **they cannot both describe the same rule.**
  **LS HYPOTHESIS (marked as such — LS has been wrong on derivations twice this phase): `nA ≥ cap`
  is NOT universal. It governs the DISPLACEMENT-ONLY regime, which by the corrected mechanism is
  exactly the lattices that LIE ABOUT AN UNCOVERED CLASS. Where the lie is about a class someone
  else covers, it costs immediately, no displacement is needed, and the channel exists at ANY nA.**
  **IF RIGHT: (1) LS's `1/n_workers` derivation describes only the regime being ABANDONED — derived
  from the current template and generalised to the design space; (2) the k=5 lever is UNNECESSARY,
  along with the 15-segment book, the longer episodes and the real run spend — because the cheapest
  option is already on the table: size-2 partial overlap at k=3, 9 segments, no roster change, no
  sixth class.**
  **DISCRIMINATING TEST, nearly free: price size-2 partial overlap across nA ∈ {0,1,2,3,4} at cap=3,
  natively. FLAT-OR-RISING FROM nA=0 → regime-specific, lever moot. A STEP AT nA=3 → universal,
  derivation stands, k=5 earns its cost.** **It runs FIRST — this is exactly the shape of cheap
  decisive test this phase has repeatedly failed to run first.**
- **REBUILD SCOPE RESTATED: lattice, ROSTER SIZE and BOOK SIZE all first-class parameters, with the
  current configuration as one value** (`n_segments` validates to 8..10; `_lattice_from_template`
  returns exactly four workers, so k=5 needs both relaxed).
- **ORDER:** (1) **D93's nA sweep on size-2 partial** — may delete (4) and (5); (2) the rebuild,
  five classes; (3) current vs disjoint vs size-2 partial at nA=1, natively; (4) k=5 sweep **only
  if** the threshold is universal; (5) six classes **only if** all five-class lattices fail.
- **RR DECLINED TO ADOPT RE's `nA=2 < cap=3` HYPOTHESIS, CORRECTLY** — it would transfer a
  five-class NATIVE result to a six-class OVERRIDE measurement, **the generalisation that has bitten
  all three agents.** Held as a rebuild prediction; if it holds, **the 1.33% at nA=1 becomes the
  anomaly rather than the zero.**

### 2026-08-09 — the override check was ONE POPULATION REACHED TWO WAYS; k=5 realism dissolved the objection

Record: `records/L9/L9_decisions_LS.md` D96–D99.

- **★ "IDENTICAL IN EVERY DIGIT" IS THE TELL, NOT THE CONFIRMATION — and RR refused to count their
  own matching result as support.** Generating all three lattices through `coverage_override`
  (post-fix, unamplified) reproduced the substitution figures exactly, 0 generation failures.
  **But with `amplify_mix=False` there is no shared class to force, so segment generation does not
  depend on the lattice at all and the two paths NECESSARILY produce the same instances. One
  population reached two ways.** It rules out a substitution **bug** and nothing else.
  **Native reproduction still needs the rebuild; the 2.198% caveat stands unchanged.**
  **THE DISCIPLINE GENERALISES: ask what would have to be true for two results to DIFFER before
  treating their agreement as evidence.** This project has read agreement as independent support at
  least three times when it was the same thing twice — the 60/60 card claim, the 6,480 enumeration,
  and the builder mismatch. **Same general form.**
- **★ THE JOINT ROSTER-AND-BOOK QUESTION: ANSWERED, and k=5 is MORE realistic than k=3.** The
  absolute threshold is always `cap` segments — **one analyst's full workload.**

      post-swap workers   n_segments   threshold   even share   niche vs an AVERAGE class
              3               9           33%         20%              1.67x
              5              15           20%         20%              1.00x
              6              18           17%         20%              0.83x

  **The niche must be `n_classes / n_workers` times an average class — 1.67× at k=3, which is
  exactly where the concentration objection had force, and 1.00× at k=5, where the specialist owns
  an AVERAGE-SIZED class and NO concentration is required.**
  **Two mechanisms make it realistic rather than convenient:** per-reviewer workload is set by
  process, not bank size, so **workload per head is the invariant and the book scales with
  headcount**; and **the niche stays 3 segments ABSOLUTELY while the book grows around it** — the
  share falls because the denominator grows.
  **RR's own nA=4 concentration objection is therefore DISSOLVED, not softened: realistic exactly
  when the post-swap roster is at least as large as the number of asset classes.**
- **★ RR's REFRAME — *the threshold is a COHERENCE CONDITION, not a cost: the niche must be at least
  one analyst's full workload* — is the most satisfying claim of the phase, and LS thinks it has a
  GAP: it conflates SOLE QUALIFICATION with FULL-TIME DEDICATION.** Sole coverage here is about who
  is **approved** to review a class, not how their week is filled. **A specialist can be the only
  approved reviewer for securitisations while spending 80% of their time on corporates** — ordinary
  key-person risk, and a niche far smaller than one workload.
  **Raised as a QUESTION, not a refutation, and it is NOT load-bearing either way:** RR's core
  realism case is independent and survives (**3 approved reviewers is small against real functions
  of 5–20; at k=3 sole coverage is FORCED by arithmetic in 75% of random lattices**), and the
  reframe applies only to the **displacement-only regime** the candidates may be leaving.
- **PRIORITY, agreed by both:** **native reproduction of the 2.198% is the cheapest decisive test
  and does not involve worker count at all.** **Survives → a realistic five-class design with NO
  sixth class and NO roster change, and the k=5 lever becomes an OPTIONAL improvement. Does not
  survive → worker count is what makes any lattice realistic, and it is cheaper than the sixth class
  was.** **Either way the rebuild is the gate and neither answer needs run spend.**
- **★ THE ONLY BRANCH THAT REACHES THE RESEARCHER'S CHEQUE-BOOK IS k=5**, which scales the book to
  15 segments and **lengthens every episode**. **That is the one commitment on the table that is
  theirs rather than the team's, and it is only reached if the cheap branch fails.**

### 2026-08-09 — ★★ THE REBUILD IS DONE. Two candidates have a channel at the realistic mix

Record: `records/L9/native_lattices.json` (RE); `records/L9/L9_decisions_LS.md` D100–D105.
**One code path for every lattice; the `coverage_override is None` condition is DELETED, not
audited. Position IS the role.**

    lattice   segs   nA achieved     mean   nonzero        interval
    current     1       {1: 60}     0.00%     0/60   [0.00%, 0.00%]
    current     3       {3: 60}     0.98%    42/60   [0.98%, 0.98%]
    current     4       {4: 60}     1.24%    34/60   [1.24%, 1.24%]
    disjoint    1  {1: 48, 2: 12}   5.27%    60/60   [0.00%, 9.26%]
    partial     1       {1: 60}     2.26%    60/60   [0.00%, 4.85%]
    partial     2       {2: 60}     1.25%    60/60   [0.00%, 4.25%]
    partial     3       {3: 60}     0.00%     0/60   [0.00%, 0.00%]

- **AT THE REALISTIC MIX: current 0.000% (0/60), disjoint 5.272% (60/60), partial 2.258% (60/60) —
  NATIVELY, five classes, NO sixth asset class, NO roster change.** RR's control reproduces
  qualitatively, and **their diagnosis is confirmed structurally: the old predicate demanded a
  predecessor-sole-held lied class, exactly the configuration that makes the lie worthless.**
  *(The disjoint `IndexError` recorded earlier as "the real blocker" now fires for real, because
  disjoint is finally being generated — the fixture was never exercising the path it claimed to.)*
- **★ THE MIX-RESPONSES RUN OPPOSITE, AND NOBODY PREDICTED IT.** `current` **RISES** with nA
  (0, 0, 0.98, 1.24); `partial` **FALLS** (2.26, 1.25, 0.00, 0.00); `disjoint` is **FLAT** (no
  shared class for the amplifier to act on — the consistency check falling out again).
  **So the realistic mix is exactly where the shipped lattice is WEAKEST and partial is STRONGEST.
  They are not stronger and weaker versions of one thing.**
  **AND IT DISSOLVES THE REALISM PROBLEM RATHER THAN TRADING IT: the nA=4 concentration question
  existed because the shipped design NEEDED nA=4. Partial does not — best at nA=1, dead by nA=3.**
- **SHARPER THAN LS's HYPOTHESIS: BOTH lattices turn at nA = cap, in OPPOSITE directions** —
  `current` switches ON at nA ≥ cap, `partial` switches OFF.
- **LS's D93 TEST MARKED WEAK DESPITE ITS CONCLUSION HOLDING:** framed as *flat-or-rising* vs *a
  step at nA=3*; **the answer was FALLING, which was in neither branch.** **A discriminating test
  whose outcome space omits the actual behaviour is a weak test even when the right answer comes
  out of it.**
- **★ THE WORKER SWEEP IS DROPPED.** The threshold-share problem was a consequence of *needing*
  `nA ≥ cap`, **and partial does not need it.** **This removes the 15-segment book, the longer
  episodes and THE ONLY BRANCH THAT REACHED THE RESEARCHER'S CHEQUE-BOOK.**
  **RR's k=5 analysis is NOT withdrawn and NOT wasted** — three approved reviewers being small
  against real functions of 5–20, and sole coverage being forced by arithmetic at k=3, remain true
  and **stand as a recorded limitation of the roster size rather than a required change.**
- **★ BOTH INTERVAL FLOORS ARE ZERO, which GENERALISES RR's size-3 finding: the zero best-case is
  NOT a size-3 property.** **Neither candidate has a GUARANTEED effect — only an expected one with a
  zero floor.** That travels with every headline.
  **WORDING TO SETTLE BEFORE IT SHIPS:** RE wrote *"a manager that tie-breaks worst-case gets
  nothing."* **LS reads it the other way — ceiling is `oracle − realised`, so the manager's BEST
  tie-break gives the ZERO ceiling, i.e. the floor is where the MANAGER does well and WE measure
  nothing. "Worst case" must name WHOSE**, or it will be read backwards by the audience the interval
  exists for.
- **★ A THIRD STRUCTURAL ZERO, HANDED OVER RATHER THAN GUESSED: `partial` hits exactly 0.00% at
  nA ≥ 3.** RE has no mechanism, says `nA ≥ cap` does not predict it, and **declined to guess —
  explicitly because guessing cost us the inversion.** **LS offers ONE LOW-CONFIDENCE candidate for
  RR to test or discard: forcing DRAINS the other classes as it concentrates the successor-unique
  one — so if the LIED class drains to zero segments, the lie has nothing to be wrong about.**
  Countable directly. **Does not affect the realistic-mix reading** (nA ≥ 3 is the unrealistic end).
  **Three structural zeros, two of which turned out to be the whole finding, is a pattern not to
  park silently.**
- **THE ESCALATION TRIGGER IS NOT MET.** *"If no lattice has a channel at nA=1"* — **two do.** The
  finding is that **the SHIPPED lattice does not, and two five-class candidates do, at no cost in
  asset classes.**
- **THE DECISION, ASSEMBLABLE ONCE RR's REVIEW LANDS:**
  **partial overlap** — 2.26% at the realistic mix, **best there**, dead at concentrated mixes,
  realism problem **dissolved**, the researcher's stated preference.
  **disjoint** — 5.27%, flat in mix, ~2.3× partial, **but models a DIFFERENT SPECIALIST**, the
  validity objection that has stood all phase.
  **both** — interval floor **0.00%**: no guaranteed effect, only an expected one.
  **neither** — **no episodes/arm figure until L3 supplies a post-L1 σ** (D11).
- **OUTSTANDING: RR's review of the rebuild (standing rule 7), and the third structural zero either
  explained or explicitly parked.** Regression across the rebuild: path alignment 60/60 zero
  divergent fields, D40 unchanged with `nA = cap` still confirmed at 3/4/5, pricing 0.85/9.57/0.00,
  selection [7, 20, 30], tests 3 passed.

### 2026-08-09 — the governing quantity is the LIED CLASS; partial overlap ships UNAMPLIFIED

Record: `records/L9/L9_decisions_LS.md` D106–D110.

- **THE REGIME HYPOTHESIS IS CONFIRMED, with the derivation:**
  **Uncovered lie** — routing the lied class to the successor costs **nothing directly** (nobody can
  do it; everyone falls back to SA), so **the only loss route is DISPLACING work the successor is
  uniquely needed for → `nA ≥ cap`.**
  **Covered lie** — routing it costs **directly** (the incumbent could have produced the IRB number),
  so **no displacement is needed and there is NO threshold.**
  **Already visible: partial gives 2.198% at nA=1 and 1.059% at nA=2 — falling, non-monotonic, no
  step at 3. A threshold-governed quantity does not behave like that.**
  **So `nA ≥ cap` describes the regime being ABANDONED, and LS's `1/n_workers` derivation is scoped
  to it** — correct for that regime, irrelevant to the design likely to be adopted.
- **★ THE SHARPENING NEITHER LS NOR RE DREW: in the covered-lie regime the governing quantity is
  SEGMENTS IN THE LIED CLASS, not nA.** The loss is paid **per lied-about segment misrouted**.
  **SO FOR PARTIAL OVERLAP, FORCING ON THE SUCCESSOR-UNIQUE CLASS IS COUNTERPRODUCTIVE — it pulls
  segments OUT of where the channel lives**, which is exactly what 2.26% → 1.25% is as nA goes
  1 → 2. **D47 is RIGHT for the uncovered-lie regime and WRONG here.**
- **★ AND IT LIKELY EXPLAINS THE THIRD STRUCTURAL ZERO (D104).** LS's guess was that forcing drains
  the other classes; **RR's sharpening names the right quantity.** **REFINEMENT FOR THE COUNT: count
  IRB-APPLICABLE segments in the lied class, not segments** — SA-only segments cannot carry the
  loss, and **the amplifier's third arm approves the forced class FIRST, so the lied class can be
  starved of IRB APPLICABILITY well before it is starved of segments.** That is the quantity to plot
  against nA.
- **★ RULING (D108): IF PARTIAL OVERLAP IS CHOSEN, IT SHIPS UNAMPLIFIED.** At nA=1 unamplified it is
  **both the realistic configuration and the strongest one — a rare case where no tuning is
  required, and we take it rather than look for more.** **NO AMPLIFIER.** If sensitivity is ever
  wanted, D107 says the lever is **concentration in the LIED class**, **which needs its own realism
  argument, being a different claim about the portfolio from the one just dissolved.** **Every
  amplifier in this project's history was an inherited default that turned out to be doing the work;
  the time to refuse one is before it is quoted.**
- **★ RR WITHDRAWS THE COHERENCE CLAIM AND WEAKENS THEIR OWN ORIGINAL OBJECTION.** The reframe
  (*"the niche must be one analyst's full workload"*) is withdrawn on LS's gap — **sole approval is
  not full-time dedication** — with RR's own note: *"it was elegant, which is why I should have
  distrusted it."*
  **And the consequence against themselves: if approval does not track volume, their ORIGINAL nA=4
  objection weakens too.** Coverage here is **APPROVAL**, and approval tracks volume less tightly
  than headcount — **so a dominant class being sole-approved is more plausible than they claimed.**
  **What survives at reduced strength:** continuity and key-person-risk pressure, including
  regulatory attention, still push a main book toward *multiple* approvals.
  **This does NOT move the decision** — disjoint is flat in nA and needs no concentration, and the
  objection to disjoint is that it models a **different specialist**, which stands independently.
  **RR's core k=5 case is untouched by the withdrawal** and stays as a recorded limitation of the
  roster, not a required change.
- **THE DIFFER-TEST RULE GOES IN §B BESIDE THE POSITIVE-CONTROL RULE**, in RR's framing: **a
  positive control asks "can this fire at all"; the differ-test asks "could these two have
  disagreed" — the same defect from opposite sides.** Four instances: the 60/60 card claim, the
  6,480 enumeration, the builder mismatch, and RR's own two paths.
- **OUTSTANDING, and it is the whole list: RR's nA sweep; RR's formal review of the rebuild
  (standing rule 7); and the interval-wording question — "worst case" must name WHOSE.**

### 2026-08-09 — ★ GATE REVIEW PASSED. The third zero is solved. The decision goes to the researcher

Record: `records/L9/L9_gate_review_RR.md` (RR); `records/L9/L9_decisions_LS.md` D111–D116.
**`partial` 2.258% and `current` 0.000% at nA=1 reproduce exactly, natively.** RR's `disjoint` reads
4.829% because it is **default segs, not segs=1** — a different cell, not a discrepancy.
**RULE TAKEN FROM IT: neither figure is quotable without its `segs`.**

- **BLOCKER 1 — THE INTERVAL WORDING WAS INVERTED TWICE.** `ceiling = oracle − realised`, so **the
  manager's BEST tie-break gives the ZERO ceiling — and it does not "get nothing", it gets
  EVERYTHING and WE measure nothing.** **Required form, adopted verbatim: *"The floor is the manager
  tie-breaking favourably — it attains the oracle and the channel has nothing left to be worth."***
  **GENERAL RULE: every best/worst names WHOSE, because THE MANAGER'S BEST IS THE EXPERIMENT'S
  WORST.** The inversion is built into the quantity and will be read backwards by default.
- **★ BLOCKER 2 — THE INTERVAL IS NOT AN ERROR BAR.** It is the range over an **unmodelled
  decision**: how the manager resolves an indifference the card gives it no basis to resolve.
  1. **The floor is a LOGICAL possibility, not a probable one** — reaching it needs the tie-break to
     correlate with truth, and under the card there is nothing to correlate with. **Not "the effect
     might be zero" statistically.**
  2. **★ THE FLOORS ARE ZERO FOR BOTH CANDIDATES, so `[0, 9.26]` and `[0, 4.85]` OVERLAP COMPLETELY
     AT THE BOTTOM AND CANNOT SUPPORT A DOMINANCE CLAIM. THE ENTIRE COMPARISON RESTS ON THE
     EXPECTATIONS.** Read as ranges of plausible truth the options look indistinguishable — **which
     is NOT what the evidence says. STATED, not inferred.**
  3. **The expectation is principled for an INDIFFERENT manager; a real LLM manager is not one and
     we do not model its priors. That is the honest gap** and it ships with the package.
- **★ THE THIRD STRUCTURAL ZERO IS SOLVED — and it is the COMPLEMENT of the current lattice's rule.**
  LS's draining candidate is **partly right and cannot produce it**: the lied class drains
  (1.30 → 1.00 → 0.68 → 0.55 segments), which explains the **gradual** 2.26% → 1.25% decline, **but
  it never empties while the ceiling is exactly zero.**
  **The cause is CAPACITY SATURATION: `partial` is card-NAMES, so at nA ≥ cap the successor's slots
  are entirely consumed by work only it can do — NO FREE SLOT remains for the lie to misdirect
  into.**

      uncovered lie (current)   channel requires  nA >= cap   needs CONTENTION to displace
      covered lie   (partial)   channel requires  nA <  cap   needs a FREE SLOT to misdirect into

  **Ceiling tracks free successor slots (`cap − nA`) monotonically: 2 → 2.26%, 1 → 1.25%, 0 → 0.00%.
  Both regimes are ONE comparison with COMPLEMENTARY conditions** — a better object than either zero
  it explains, and **the third time this phase that refusing to park an unexplained zero produced
  the finding.**
- **THE REGIME HYPOTHESIS IS CONFIRMED AT 40× THE SAMPLE (n=2400/cell), with the regime labelled
  directly by a `coverers of lied class` column:**

      lattice  segs  nA    mean    nonzero      coverers of lied class
      current     1   1   0.00%    0/2400              [0]
      current     3   3   1.03%  1752/2400             [0]
      partial     1   1   2.40%  2400/2400             [1]
      partial     3   3   0.00%    0/2400              [1]

- **★ AND IT REFUTES RE's CANDIDATE FOR THE SIX-CLASS ZERO.** `nA=2 < cap=3` cannot explain the
  card-NAMES zero at nA=2, **because `partial` is ALSO card-NAMES and is 1.252% at nA=2 < cap.**
  **THAT ZERO STAYS OPEN AND IS CARRIED, NOT CLOSED** — two of three have mechanisms, one does not.
  **Better to ship one honest open item than three closed ones, given two of the closed ones turned
  out to be the whole finding.**
- **`partial` SHIPPING UNAMPLIFIED IS NOW A DERIVATION, not a preference: forcing costs it TWICE —
  draining the lied class AND consuming the free slot the channel needs.** **And D47 (LS's ruling on
  RR's recommendation) is ACTIVELY HARMFUL here** — right for the uncovered-lie regime only.
- **★ STANDING RULE 7 SATISFIED — acceptance output (`native_lattices.json` + regression), RR's
  review, LS's review. RR reports NO REMAINING BLOCKERS. THE DECISION GOES TO THE RESEARCHER.**

### 2026-08-09 — ★ THE THREE STRUCTURAL ZEROS ARE ONE FACT. L9 closes to the researcher

Record: `records/L9/L9_decisions_LS.md` D117–D122.

- **★ `nA = cap` IS THE TRANSITION, and which side carries the channel is set by whether the LIE
  points at a COVERED class. RE stated the prediction BEFORE running and it confirmed exactly:**

      lattice   cap    nA=1    nA=2    nA=3    nA=4    nA=5
      current     3   0.00%   0.00%   0.98%   1.24%   1.41%
      current     4   0.00%   0.00%   0.00%   0.79%   1.22%
      current     5   0.00%   0.00%   0.00%   0.00%   0.83%
      partial     3   2.26%   1.25%   0.00%   0.00%   0.00%
      partial     4   2.34%   1.73%   0.66%   0.00%   0.00%
      partial     5   2.41%   2.02%   1.04%   0.50%   0.00%

      partial's first ZERO    at nA = [3, 4, 5]  against cap [3, 4, 5]
      current's first NONZERO at nA = [3, 4, 5]  against cap [3, 4, 5]

  **A lie only costs by being ACTED ON: the uncovered lie needs CONTENTION to displace into, the
  covered lie needs a FREE SLOT to be misrouted into.** **A clean prediction success, stated in
  advance, after a long run of refutations.**
- **LS's DRAIN HYPOTHESIS IS REFUTED AS INSUFFICIENT, and the refutation is better than a mean.**
  RR counted exactly the requested quantity — **IRB-applicable** segments in the lied class,
  filtered on `irb_approved`: **1.30 → 1.00 → 0.68 → 0.55**, so the starvation is REAL. **And per
  seed at nA=3, only 19 of 60 zeros have an empty lied class — 41 seeds have a lied IRB segment and
  still price EXACTLY ZERO.** **Testing sufficiency instead of stopping at the mean is what caught
  it: a mean moving in the predicted direction is precisely how a partial mechanism passes for a
  complete one.**
- **BOTH DISCRIMINATING TESTS HAD OUTCOME SPACES THAT COULD NOT CONTAIN THE ANSWER.** LS's D93
  omitted **falling**; RE's cap sweep, framed as *"does the threshold move with cap"*, **could not
  have surfaced a SECOND lattice turning the opposite way at the same point.** **General hazard,
  recorded beside the differ-test rule: a binary test on a continuous mechanism will answer, and the
  answer will be lucky.**
- **★ RE's REFRAMING ACCEPTED AS THE DIAGNOSIS AND NARROWED FOR THE DECISION.** *"`partial` and
  `current` are not ranked options — they occupy disjoint regions of the portfolio space"* is right
  and is the sharper diagnosis: **the shipped design was not WEAK, it was measuring in a region the
  realism work says banks are not in.** **But `disjoint` is FLAT in nA — alive across the whole
  space, not in a complementary region:**

      current vs partial    complementary regions  -- the DIAGNOSIS
      partial vs disjoint   both alive at nA=1     -- the DECISION, and it IS ranked
                            2.26% vs 5.27%, with the realism argument against disjoint

  **The insight strengthens the case for CHANGING the lattice; it does not bear on WHICH candidate.
  Two claims, kept apart in the package.**
- **THE THREE METHODOLOGY RULES ARE WRITTEN, with the fifth instance** (`METHODOLOGY_RULES.md` §B,
  §E ×2, four index rows in §H). **§B's framing, as settled: the positive control asks whether a
  measurement can fire AT ALL; the differ-test asks whether two measurements COULD HAVE CONFLICTED —
  same defect, opposite faces, and this project has been caught by each twice.**
  **And the sentence that names what actually went wrong here: EVERY withdrawn version of the L9
  ratio was a §E instance, and NOT ONE was arithmetic.**
- **RR's CORRECTION TO LS's CLOSING NOTE, accepted as a fact about the record:** the mechanism that
  closed the arc came out of testing **LS's** H2, and the realism inversion out of answering **LS's**
  question about worker count — **neither was RR attacking their own side; both were RR checking
  LS's and finding something else.**
- **★ THE OPEN ITEM SHIPS VISIBLE: the six-class card-NAMES zero at nA=2 has NO mechanism**, and
  RE's candidate for it is refuted (`partial` is also card-NAMES and is 1.252% at nA=2 < cap).
  **It travels as an acknowledged gap rather than folded in — two of the three zeros this phase
  turned out to BE the finding, and the pattern is that the unexplained one is where the next result
  lives.**
- **L9 IS CLOSED TO THE TEAM. The only remaining item is the researcher's choice.**

### 2026-08-09 — final correction: a DERIVED figure was in the record as a MEASURED one

Record: `records/L9/L9_decisions_LS.md` D123–D124.

- **★ THE 41/19 PER-SEED SPLIT WAS AN INFERENCE FROM A MEAN, recorded by LS as measured.** RR
  reported only **mean 0.683** IRB-applicable lied-class segments at nA=3; **a mean of 0.683 over
  60 seeds is equally consistent with distributions containing a 2.** Measured directly:

      distribution of IRB-applicable lied-class segments   {0: 19, 1: 41}   mean 0.683
      seeds WITH a lied IRB segment and ceiling EXACTLY zero        41
      seeds WITH a lied IRB segment and ceiling NONZERO              0

- **THE MEASURED FORM IS A STRONGER REFUTATION THAN EITHER AGENT STATED: not "41 mostly-zero" —
  41 of 41, NONE non-zero.** The draining account predicts those seeds should show *some* channel;
  **zero of 41 do.** **The starvation account cannot survive it and the free-slot mechanism is the
  only thing left standing.** D118 corrected, strength upgraded.
- **★ THE PROVENANCE RULE FIRED ON THE RECORD OF THE PHASE THAT PRODUCED IT, WITHIN HOURS** — *a
  provenance field is asserted against its source at emission, or it is not written.* **A derived
  figure was sitting in the record as a measured one, on its way to the researcher, and the
  distribution could have been otherwise.**
- **TWO THINGS ABOUT HOW IT WAS RAISED, worth more than the number:**
  **it was raised UNDER THE RULE rather than because it changed the conclusion** — the difference
  between a standard and a post-mortem; **and it was raised on a figure that turned out to be
  RIGHT.** Checking provenance only when a number is wrong teaches that provenance is a debugging
  step; **checking a correct one is what makes it a habit.**
- **LAST CORRECTION ON L9. The package stands and the decision is the researcher's.**

---

## PHASE NOTE — FIRST VERSION, SUPERSEDED (LS, 2026-08-09)

_Kept as a record. The claim that the movers were refusals **and not measurements** is corrected
below, on RR's objection: it invites the next phase to treat doubt as sufficient._

**The two things that actually moved this study were both REFUSALS, and neither was a measurement:
refusing to park an unexplained zero, and refusing to let agreement count as evidence.**

Three structural zeros were chased rather than parked; **two of them turned out to BE the finding**
and the third collapsed all three into one mechanism (`nA = cap`, with the side that carries the
channel set by whether the lie points at a covered class). **Four separate agreements were caught
being one thing counted twice** — the 60/60 card claim, the 6,480 enumeration, the builder
mismatch, and a two-path check that matched in every digit because unamplified generation does not
depend on the lattice.

**Every withdrawn version of the L9 ratio was a comparator error. Not one was arithmetic.**

## PHASE NOTE — CORRECTED, and this is the version to carry (LS, 2026-08-09)

**Superseding the version above, on RR's objection, which is right about the part most likely to be
quoted.**

**The refusals located where to point the instrument. A CHEAP MEASUREMENT settled every one of
them.** Refusing to park the nA≥3 zero produced nothing until someone counted lied-class segments
per seed. Refusing to let matching digits count produced nothing until someone asked what
`amplify_mix=False` does to segment generation. **The partial-overlap resurrection — arguably the
single biggest result of the phase — was a POSITIVE CONTROL: a measurement run because someone
distrusted a null.**

**SCEPTICISM ALONE WOULD HAVE PRODUCED AN OBJECTION, NOT A FINDING.** *"Refusals move studies"*
invites the next phase to treat doubt as sufficient. **The accurate lesson is narrower and more
useful: DOUBT DIRECTED AT A SPECIFIC CHECKABLE CLAIM, THEN CHECKED.** Every one cashed out in
seconds of offline computation.

**★ AND THE CLOSING FACT IS THE ONE ALREADY AT THE TOP OF THIS FILE: EVERY DECISIVE FACT THIS PHASE
WAS COMPUTABLE FROM THE GENERATOR BEFORE A SINGLE EPISODE.** The 12,960 enumeration; the zero at
nA=1; the free-slot rule; the tie-set asymmetry; the substitution artefact; the whole `nA = cap`
mechanism. **That is the price-the-ceiling-offline rule, which this phase then spent two days
re-earning.** It survived contact and it is the one to carry.

**Two findings that are NOT implied by it and should travel separately:**
- **Check provenance on a figure that turned out RIGHT.** Doing it only when a number is wrong
  teaches that provenance is a debugging step. Doing it on a correct one makes it a standard.
- **Every withdrawn version of the L9 ratio was a COMPARATOR error. Not one was arithmetic.**

**Total model spend for the phase: ZERO.**

### 2026-08-09 — L9 BLOCKED ON THE RESEARCHER; the firing goes to L8

- **L9 is `[!]` blocked on the researcher.** The team side is closed, standing rule 7 is satisfied,
  and **nothing further can be done without the choice.** Not invented work: L8 depends on nothing
  and the lattice decision does not touch it.
- **L8 STARTED, with its three standing checks answered on the step line:**
  **(1) PRODUCTION TEST — FAILS TODAY**, so the fix is warranted and we are not manufacturing a
  problem: no production system keys a join on a mutable display string, and none mutates a name
  without recording the previous value. **We are REMOVING a behaviour production would never ship.**
  **(2) NO DRIFT — it serves the question by PROTECTING THE MEASUREMENT.** The primary DV is defined
  over ASSIGNMENTS and these four joins are how segments are matched to tasks in every analysis path
  we publish from — **a silent join miss corrupts the DV directly.** Inside the rule, not the detour
  it warns about. **(3) AMBIGUITY — none.**
- **VERIFIED STILL LIVE after the rebuild and the renames:** `finance_scope_report.py:204,:332`,
  `finance_logging.py:472`, `finance_fabrication.py:230`, `run_finance_episode.py:133`.
  `segment_task_ids` already exists at `finance_split.py:90`.
- **★ ITEM 2 TOUCHES A CORE FILE** (`schemas/execution/manager_actions.py`), **so it ships WITH its
  `CHANGED.md` entry, not after it** — that document has already been caught trailing the code once
  this phase, and it is the one `CLAUDE.md` names.
- **ACCEPTANCE REQUESTED, and the second half is the point:** the three analysis sites must produce
  **identical output on existing bundles** (a null that must hold), **PLUS A POSITIVE CONTROL — a
  bundle with a task renamed to collide with the segment prefix, where the ID join survives and the
  name join would not.** **Without the positive control this is a change nobody can show was
  needed.**
- **Why it is not cosmetic:** `record_run_event("task_refined")` sits inside `if self.new_description:`
  while the name mutates **outside** it, **so a rename that changes no description emits NO EVENT AT
  ALL** — the thing that would tell us a join silently missed is the thing not logged. **Correct for
  18 episodes by luck**; one observed rename was a single editorial decision from colliding.
- **TWO CLOSEOUT ITEMS WITH RR, neither needing new measurement:** **L2a** is `[~]` awaiting their
  review file under standing rule 7; **L6** is `[~]` because **their review file's verdict PREDATES
  the fixes and has never been lifted** — a stale FAIL on a step whose blockers are closed is the
  provenance problem their own rule names, on our own record.
- **No run spend. Nothing in this firing waits on the researcher.**

### 2026-08-09 — L6 closes; L2a gets three blockers; and LS's L8 justification is CORRECTED

Record: RR's review closeouts; RE's narrowing fix.

- **★ LS CORRECTION: "correct for 18 episodes by luck" IS NOT SUPPORTABLE and is withdrawn.**
  Measured across all 18 bundles:

      task_refined events                                    8
      of which carry `new_name` or `name_before`             0
      whose `task_name` collides with the segment prefix     0

  **Zero name provenance on any of them** — and the un-logged path (`record_run_event` inside
  `if self.new_description:`) means **a rename with no description change leaves NO TRACE AT ALL.**
  So the 8 logged refinements show no collision *in their post-rename name*, **which is not the same
  as showing no join ever missed**, and the invisible path cannot be checked in either direction.
  **RESTATED: "NOT RECOVERABLE FROM THESE BUNDLES."** **That is a STRONGER reason for the fix, not a
  weaker one** — the argument becomes *we cannot audit the past, so the join must not depend on names
  going forward*, rather than a claim about the past we cannot support.
  **★ AND IT PROPAGATES: any L2a or L3 figure derived BY NAME from these 18 bundles carries this as
  a stated limitation.**
- **L6 → `[x]`. The verdict WAS already lifted** — RR's file carries a `RESOLUTION — verdict LIFTED,
  verified against the code` section ending "L6 passes", both blockers checked against the code and
  the second fixed better than recommended. **LS's concern was half-right and the half that is right
  is the document's: the HEADER still announces "TWO BLOCKERS", so the file contradicts itself
  depending on where a reader stops, and anyone grepping for the verdict gets the STALE one.**
  Fixed by a pointer at the top rather than a rewrite, per annotate-in-place.
- **★ L2a — THREE BLOCKERS, all the same shape, and ALL leave every check the module has still
  passing.** Demonstrated on constructed bundles rather than argued:

      task_assigned payload missing `task_class` -> "never_assigned", residual 0, NO RAISE
      task_assigned payload missing `applied`    -> "never_assigned",             NO RAISE
      executed segment absent from parse_detail  -> "executed_but_unparseable",   NO RAISE

  **Blocker 1:** `.get("task_class")` and `.get("applied")` default to `None`, **indistinguishable
  from "not a segment" / "not applied"** — and **`never_assigned` ASSERTS THE MANAGER NEVER STAFFED
  IT, which is the exact false claim v1 made and this module exists to stop making.**
  **Blocker 2:** a missing `parse_detail` entry makes an executed segment read as **unparseable**,
  so **a bundle gap is reported as a worker failure.**
  **Blocker 3:** **the residual check CANNOT FIRE ON ANY DATA CONDITION** — `states` is only ever
  assigned from the eight literals `counts` sums over, so `sum(counts) == len(by_segment)` **by
  construction**, verified zero on well-formed input *and* on all three malformed ones. It can only
  catch a typo in the same file. **"A check that cannot fail on data is documentation."**
  **Replacement suggested and endorsed: assert every `task_assigned` segment task id appears in
  `by_segment`** — an index/event disagreement passes silently today.
  **Blockers 1 and 2 are the DEFAULT-MUST-NOT-BE-A-LEGAL-VALUE rule, violated in our own new code**
  — a missing field defaulting to a value that is itself a legal, meaningful state. **Nothing
  touches the design or the eight predicates, which are better than what they replace.**
- **★ RE's NARROWING FIX CAUGHT A FAULT OF ITS OWN, and it is the general lesson worth keeping.**
  `print(TWO_CLAIMS)` landed without its definition: the module raised `NameError`, **exited 1, and
  wrote NO RECORD — while the printed output looked COMPLETE, because the failure came after the
  last table.** **Found by checking the EXIT CODE rather than reading the output.** Had it been
  eyeballed, the package would have cited a record the last run never wrote.
  **The empty-sample defect wearing different clothes: a run that looks finished and is not.**
  **RE's own summary, adopted over the credit they declined: CHECK THE EXIT CODE, AND TEST
  SUFFICIENCY RATHER THAN DIRECTION.**
- **RE encoded LS's `disjoint`-is-flat narrowing in the module and record, quoted rather than
  re-phrased** — the overreach never reached the code, and they encoded the separation anyway
  because **the table alone invites the same collapse and the module is what the package cites.**

### 2026-08-09 — `check_record_citations.py`: the one rule from this phase that is MECHANICAL

Record: `check_record_citations.py` (LS, on RR's proposal). **RR proposed the check, supplied both
the rule and the violation, and asked that someone else write it.**

- **THE VIOLATION THAT PROMPTED IT, found by RR auditing their OWN committed work against RE's
  exit-code lesson: `step4_audit_RR.md` cited `step4_audit.py`, WHICH WAS NEVER COMMITTED.** <!-- citation-check: superseded --> The
  figures came from inline invocations that were not saved — **and that is why its `n=30` could not
  be reconstructed and turned out to be 7 per group. The thing that produced it no longer existed
  to re-run.** **A record naming a script that does not exist is the provenance rule broken in the
  file that applies it to others.**
- **THE RULE: A RECORD CITING AN ARTIFACT ASSERTS THE ARTIFACT EXISTS, AND NOTHING CHECKS THAT.**
  **Mechanical, which is the point — it is the one rule from this phase that does not depend on
  anyone remembering it.**
- **WHAT IT DOES:** resolves every backtick-quoted `.py`/`.json`/`.jsonl` citation in every markdown
  file under the experiment, nearest-first (beside the record → experiment-relative → repo-relative
  → basename anywhere), **and SPLITS LIVE FROM `archive/`** — an archived record citing a deleted
  module is **the archive working, not a defect**. **The archive count is REPORTED, not suppressed:
  "stopped looking" and "nothing there" must not look the same.**
- **THREE GUARDS, each answering a failure this project has actually had:** a **POSITIVE CONTROL**
  runs first (a citation that cannot exist must be flagged AND a real file must resolve — otherwise
  a clean report can mean the resolver is pointed at the wrong place, which is `check_announcement`'s
  alarm never firing); **an EMPTY citation set RAISES rather than passing** (`all([])` is True, and a
  regex that stopped matching would report a clean tree); and **the intermediate quantities print,
  not just the verdict.**
- **SILENCING WORKS TWO WAYS AND BOTH KEEP THE ESCAPE NEXT TO THE CLAIM:** a marker in the first
  four lines declares a whole document superseded; a marker on or beside a line silences just those
  citations. **The second form exists because a LIVE document legitimately names things its own
  history deleted** — the findings log citing `check_variance.py` is the record working.
  <!-- citation-check: superseded -->
- **FIRST RUN: 18 LIVE UNRESOLVED.** Three documents declared superseded in their headers
  (`BRAINSTORM.md`, `STUDY1_LOGGING_AND_ORDERING.md`, `records/L9/step4_audit_RR.md`), three
  historical citations silenced in place. **Live unresolved now 0; archive 36, reported. Counters
  reconcile exactly: 27 silenced + 136 resolved + 36 archive + 0 live = 199.**
- **★ AND THE TOOL CARRIED THE PROJECT'S OWN DEFECT BEFORE IT WAS COMMITTED: it summed annotated
  FILES and silenced CITATIONS into ONE counter — two populations under one name, the §B defect,
  inside the tool written to enforce §E.** Caught because the printed number did not reconcile with
  the drop in total citations. **Fixed before commit, with the comment in the code saying what it
  was.**
- **RR's GENERALISATION, worth more than the check: *the absence of the thing you would check with
  is invisible by construction.*** A missing script, an unwritten record, a raise after the last
  print — **none of them leave a gap where you are looking.** The check covers one instance
  mechanically; **the general form still needs a person.**

### 2026-08-09 — L2a's three blockers fixed; and TWO checks caught their own authors in one day

- **ALL THREE L2a BLOCKERS FIXED, acceptance PASS, and all three were in the module's OWN new code**
  — **the default-must-not-be-a-legal-value rule violated by the module written to enforce it.**
  **1 & 2:** `payload.get("applied")` / `.get("task_class")` returned `None`, which is falsy, so the
  task fell out of `assigned` and its segment was classified **`never_assigned` — the state that
  ASSERTS THE MANAGER NEVER STAFFED IT, reachable by a payload merely LACKING A FIELD, and the exact
  false claim v1 made.** **Absence is now an error, not a state.**
  **3:** `detail.get(segment_id) or {}` collapsed *absent from `parse_detail`* into *present but
  unparseable*, **blaming the worker for a gap in our own analysis path.**
  **4:** the by-construction residual is **kept as an internal invariant** (`AssertionError` — bundle
  data cannot cause it) **and replaced as the guard** by the index/event agreement check: every task
  logged as an assigned segment task must appear in the segment index. **The old one could only
  catch a typo in its own file; the new one catches the DV's numerator and denominator sitting on
  different populations.**
- **★ RE's FIRST POSITIVE-CONTROL RUN WAS INVALID AND LOOKED LIKE FOUR CLEAN PASSES.** All four
  controls "raised" — **on the PRE-EXISTING `refusal_codes` guard, before reaching any new check**,
  because the 18 R2 bundles predate the structured-code fix and none of them splits at all.
  **A control that fires on the wrong assertion proves nothing.** Rebuilt on constructed bundles,
  each now demonstrably firing on its own guard with the well-formed null holding.
  **The positive-control rule catching itself: RE had no known-positive case, only a
  differently-broken one.**
- **SCOPE CORRECTION the acceptance found:** raising on ANY absent parse entry rejected the
  machinery episode, which legitimately has **no parsing pass at all** (zero model calls). Narrowed
  to a **partial** gap.
- **★ RULING (LS) on the limitation RE stated rather than fixed: NO ninth state, NO
  `parsing_performed` flag.** Both change the partition, **and the partition is the one thing here
  reviewed twice and passed.** **The problem is the SENTENCE, not the count** —
  `executed_but_unparseable` predicated on *"the DELIVERABLE yielded no rwa value"* is a claim about
  the worker that a machinery run cannot support. **Fix: when `parse_detail` is entirely empty, the
  module reports the split with an explicit banner that NO PARSING PASS RAN and that bucket is NOT
  INTERPRETABLE.** **A quantity whose predicate does not hold for a population should REFUSE TO BE
  INTERPRETED for that population — not be re-partitioned around it.**
- **★ RR VERIFIED THE CITATION CHECK CAN REPORT NONZERO, which is the test LS did not run.** Two
  invented citations caught, exit 1, positive control passing. **A check that reports zero is only
  worth having if it can report nonzero.** **And it found `main` exiting 1 on a citation LS's own
  run had not seen: the findings-log entry recording RR's defect NAMES the missing file in order to
  say it is missing.** **Writing down a broken citation creates a broken citation.**
  **Two consequences, both now IN THE TOOL rather than left to adjudication:**
  **(1) A clean report is a STATEMENT ABOUT A MOMENT, not a property of the tree** — the checker's
  own findings-log entry broke the checker's own invariant within minutes of the run reporting zero.
  **(2) That class RECURS BY CONSTRUCTION, so the marker is the STANDARD FORM for records of
  missing-artifact defects, not a case-by-case exception.**
- **★ TWO CHECKS CAUGHT THEIR OWN AUTHORS IN ONE DAY, in the same shape:** RE's four controls firing
  on a pre-existing guard, and LS's citation tool summing two populations into one counter.
  **What caught the second was the counters not reconciling — a PRINTED INTERMEDIATE rather than a
  review. The rule caught itself, through the other rule**, which is stronger evidence for both than
  any finding they produced, because it is evidence they work **when nobody is looking for the thing
  they catch.**

### 2026-08-09 — LS's banner ruling is OVERTURNED on the point LS flagged as uncertain

- **★ LS RULED: report the split with a printed banner saying the bucket is not interpretable, and
  flagged ONE uncertainty — "specifically if you think a reader can be relied on to see the banner
  and not the bucket name."** **RE: they cannot, and the evidence is this project's own record.**
  **A banner is dropped by the first summariser that reformats the output, and every consumer of
  this split reads `counts`, not the surrounding prose.** Three instances already:
  **a figure quoted without its `segs`; a comparator quoted without its construction path; a record
  whose `rule` string named a source that did not produce it.** **Relying on adjacency is how all
  three happened.**
- **★ ACCEPTED IN FULL. The non-interpretability travels IN THE RECORD, with the numbers rather than
  beside them:**

      parsing_performed        False
      uninterpretable_states   ["executed_but_unparseable"]
      uninterpretable_reason   "...its predicate is a claim about the WORKER and is NOT
                                SUPPORTED here. The count is correct; the state's sentence
                                must not be quoted for this bundle."

  **Still the §B move and NOT a schema change** — nothing re-partitioned, no state added, the eight
  predicates untouched, and a well-formed bundle carries `uninterpretable_states: []`.
  **It is the same refusal LS ruled for, placed where a MACHINE can enforce it instead of where a
  HUMAN has to notice it.** **LS's principle was right and its LOCATION was wrong.**
  **Both ship: the field for consumers, the banner for whoever reads the acceptance output. The
  banner ALONE was the error.**
- **★ RE's GENERALISATION OF THE POSITIVE-CONTROL NEAR-MISS IS NARROWER AND BETTER THAN LS's.**
  Not *"controls can fire on the wrong assertion"* but: **WHEN A CONTROL FIRES, CHECK WHICH GUARD
  RAISED.** **A control that raises is the outcome you are hoping for, which is exactly when nobody
  looks closer.** RE had four hoped-for outcomes and stopped.
- **AND THE PRACTICE THAT FOLLOWS, adopted for L8: build the positive control FIRST, so you know it
  can FAIL before you trust it passing.** Same shape as RR verifying the citation checker could
  report NONZERO rather than trusting that it reported zero.
- **PROCESS NOTE: this is a disagreement resolved on evidence, where the peer was right on the exact
  point LS had flagged as uncertain.** Flagging the uncertainty is what made the objection cheap to
  raise and cheap to accept.

### 2026-08-09 — L2a is NOT closed; L8's sites are converted; and a rule that fires on a PASS

- **★ L2a: TWO OF THREE FIXED. B2 IS STILL LIVE AND THE ACCEPTANCE REPORTS PASS.**
  `detail.get(segment_id) or {}` → `rwa is None` → **`executed_but_unparseable`: a gap in the
  BUNDLE reported as a WORKER producing an unreadable deliverable.** B1a, B1b and B3 all raise as
  intended; **B2 does not.**
  **RR re-ran the named cases rather than reading the report**, for the reason given one message
  earlier: **RE's first control run had four controls all firing on a PRE-EXISTING guard, which
  looked like four clean passes. So "acceptance passing" is not evidence that a particular NAMED
  BLOCKER is closed.** Open question to RE: **does the acceptance fixture reach the B2 branch at
  all?** If its `parse_detail` is complete it cannot, **and it would pass indefinitely.**
- **★★ THREE INSTANCES IN ONE DAY OF A CHECK PASSING WHILE THE THING IT WAS MEANT TO CATCH WAS
  UNTOUCHED** — RE's four controls, LS's citation tool reporting a stale zero, and now B2.
  **All three were caught by someone RE-RUNNING THE SPECIFIC CASE rather than reading the report.**
  **RR's observation, which is the gap the three share: every rule written this phase fires on a
  SUSPICIOUS result — an unexplained zero, a null that agrees with you, matching digits. NONE fire
  on a PASS. Green signals are the ones nobody re-derives.**
- **★ LS's PROPOSED STANDARD, the one that fires on a pass: AN ACCEPTANCE THAT CLOSES NAMED BLOCKERS
  MUST MAP EACH BLOCKER TO THE CONTROL THAT FIRES FOR IT, AND REPORT ANY BLOCKER WITH NO FIRING
  CONTROL AS *UNCOVERED* RATHER THAN PASSING.** RE's failure was a MODULE-level control standing in
  for four blockers; B2's is a blocker with no control that reaches it. **Both become visible the
  moment the mapping is required and neither is visible without it.** *(Raised for
  `METHODOLOGY_RULES.md`; RR owns that file's shape.)*
- **L8: ALL FOUR SITES CONVERTED, and RE BUILT THE CONTROL FIRST — it failed against the code as it
  stood, which is the point.** Renaming one segment task: **NAME join 9 hits → 8, losing the segment
  SILENTLY; ID join 9 → 9.** **A lost row means no assignee, which reads as `never_assigned` — the
  exact false claim L2a exists to prevent, manufactured by an editorial rename.**
- **★ TWO REASONS THE NAME WAS NEVER A SAFE KEY, neither previously raised:** the board **already
  carries `task_id`**, so the name was never the only option; and **the prefix is NOT UNIQUE — one
  real bundle has TEN rows matching "Risk-weighted assets" for NINE segments**, so **a collision does
  not even need a rename.** The risk was closer than "one editorial decision away".
- **AND THE FIXTURE WAS NOT EXERCISING THE PRODUCTION PATH:** `test_finance_fabrication` built
  `worker_run_completed` events with `task_name` and **no `task_id`**, and its bundle had **no
  segment index at all** — so every id join found nothing and the test failed the moment the real
  code joined the way real bundles support. **Same defect as the override path: a fixture shaped
  unlike production, passing while the thing it stands for is broken.**
- **Core change:** `task_renamed` emitted whenever `task.name` changes, carrying
  `name_before`/`name_after`/`with_description_change`; `task_refined` carries the same provenance.
  **`name_before` is captured BEFORE the mutation and the acceptance asserts it — reading it after
  is the whole defect in miniature.**
- **Verification:** null — `segment_states` identical on all 18 bundles, deterministic 18/18;
  positive control — states identical across a rename the name join could not survive; acceptances
  split / logging / fabrication / load_feedback / quantity_kinds all exit 0; pytest 3 passed.

### 2026-08-09 — the rule generalises, and it catches the tool it was diagnosed on

- **★ RR's GENERALISATION SUBSUMES LS's, and the diagnosis of why is exact: LS stated the property
  over BLOCKERS when it belongs to CONTROLS.** The general form:

  > **A control states the outcome of its own NEGATIVE case** — not *"the check passed"* but
  > *"the check FAILED on the input it exists to reject, and passed on the real one."*
  > **A control that passes BOTH is broken, and today that is indistinguishable from one that
  > works.**

  It **subsumes** LS's mapping form (a blocker with no control has no negative case to exhibit, so
  it shows up missing) **and covers the general case LS had nothing for**, because it binds every
  check rather than only acceptances closing named blockers.
- **★ SECOND HALF, and it lands on LS's own citation tool:**

  > **The positive control must traverse the SAME PATH as the reported verdict, end to end — not a
  > COMPONENT of it.**

  **LS's control proved the RESOLVER could flag an unresolvable name. Nobody had shown the REPORT
  could come back non-zero** — different claims, and **only the second is what the exit code
  asserts.** RR's comparison: **a component-level control on a pipeline-level claim is the same
  substitution as a mean standing in for a per-seed split.**
- **FIXED RATHER THAN NOTED.** `check_record_citations.py` now runs an **end-to-end control before
  the scan**: the full `scan()` against a temp tree containing one unresolvable citation, asserting
  the verdict returns non-zero — **then against a tree whose only citation resolves, asserting it
  returns zero. Both directions, because passing both is the broken case.** **And the control was
  verified able to fire**, by stubbing `scan` to report clean and confirming it raises.
- **THE SCOPE LIMIT IS WRITTEN INTO THE RULE rather than left implicit:** *a green signal from a
  check whose negative case nobody wrote is still invisible, and re-running the named case by hand
  remains the only backstop — a habit, not a standard.* **A rule that overstates its coverage is
  worse than the gap it names.**
- **★ THE COLLISION MAY BE MORE THAN AN UNDERSTATEMENT, and RR is checking before it enters either
  record.** *"Not recoverable from these bundles"* says **we cannot tell whether a join missed.**
  **A bundle where the join key is PROVABLY AMBIGUOUS says something stronger: figures derived by
  name from THAT bundle may be WRONG, not merely unverifiable.** **That is a different class — a
  limitation becomes a defect with a named scope.**
  **IF IT HOLDS, the follow-on is not a wording change: every published figure derived by name from
  that specific bundle gets RE-DERIVED BY ID, and the difference is reported whether or not it
  moves.**

### 2026-08-09 — L4 DRIFT CHECK: the brief names a perturbation the study no longer uses

Record: `records/L4/drift_check_LS_2026-08-09.md`. **Run because L9 is blocked on the researcher
and L2a/L8 are with peers — the cron's stated condition for the drift check rather than invented
work.**

**VERDICT: the brief's QUESTION is intact and every finding this phase serves it. Its DESIGN
section describes a perturbation the study does not use, and its GATE cannot be run as written.**

- **NO DRIFT:** §1 the question and its scoped-out clause; §5's L7-amended DV (assignments,
  forced/discretionary separated, conditioned share primary); §5's estimator.
- **★ DRIFT 1 — THE BRIEF NAMES TWO MANIPULATIONS AND DOES NOT SAY WHICH THE STUDY RUNS.** §4's
  perturbation is *"prompt-level METHOD SUBSTITUTION"* with trace-distinguishability via a distinct
  tool call or truth value. **Everything measured this phase is a COVERAGE LATTICE — the successor
  is APPROVED for different classes, not computing differently.** And §4's own scope condition
  already says *"COVERAGE information cannot address the dominant allocation error"*. **Largest
  drift; the researcher's to settle, because it decides what the paper's manipulation IS.
  REPORTED, NOT FIXED.**
- **★ DRIFT 2 — THE GATE CANNOT BE RUN AS WRITTEN.** §6 PASS requires *"≥1 correct post-swap outcome
  demonstrably via the SUBSTITUTED METHOD"*. **Under a coverage perturbation there is no substituted
  method to demonstrate** — criterion (i) has no referent, (ii) still does. **§10's item 5 ("the go:
  build delta §8, then the gate §6") is stale by the same amount.** Settled with Drift 1.
- **DRIFT 3 — THE SCOPE CONDITION IS CORRECT AND MUCH WEAKER THAN WHAT WE NOW KNOW.** *"Capacity
  binds exactly"* is right; the exact rule underneath it is `nA ≥ cap` for uncovered-lie lattices
  and `nA < cap` for covered-lie. **As written it reads as "the effect is small in this regime",
  and the measurement is that the shipped lattice is EXACTLY ZERO at a realistic mix. Updating it
  STRENGTHENS the claim discipline.**
- **DRIFT 4 — §4 NEVER NAMES THE LATTICE**, now the central design parameter, **and §10's five open
  researcher decisions do not include the template choice — the only one actually blocking.**
- **★ DRIFT 5 — FOUND BY THIS CHECK, INSIDE THE CITATION CHECKER WRITTEN YESTERDAY.** §5 cites
  `check_announcement.py:168–191` as the evidence for the superseded-DV amendment, **and that module
  was deleted in the cleanup — so the evidence for a standing amendment in the AUTHORITATIVE BRIEF
  is no longer inspectable at source** (the finding survives in
  `records/L7/rerouted_share_definition_v1.md`, and the brief now says so).
  **AND THE CHECKER DID NOT CATCH IT: its pattern required a backtick immediately after the
  extension, so EVERY LINE-RANGED CITATION WAS SILENTLY SKIPPED** — and records cite
  `file.py:168–191` far more often than the bare name. **Fixing it took citations found from 201 to
  287 (30% previously invisible) and live unresolved from 0 to 5, one in the brief.**
  **So yesterday's "UNRESOLVED IN LIVE DOCS 0" was true of what the checker LOOKED AT and false of
  the TREE — the defect the tool exists to catch, in the tool, found by a check run for another
  purpose.**
  **★ AND THE END-TO-END CONTROL ADDED YESTERDAY COULD NOT HAVE CAUGHT IT: it proves the VERDICT
  CAN FAIL, not that the SCAN LOOKS AT EVERYTHING. A control shows the path can fail; it does not
  show the path is COMPLETE.** That is a third face of the same rule and neither existing form
  covers it.
- All five now resolve or carry an in-place marker; **the brief's is annotated EVIDENCE-DELETED,
  not silenced.**

### 2026-08-09 — the collision escalation is RETRACTED, and the narrower question closes clean

Record: `records/L8/name_key_ambiguity_RR.md` (RR).

- **★ THE STRONGER READING IS WRONG AND RR RETRACTED IT BEFORE ANYONE ACTED.** Measured across all
  18 bundles:

      bundle                  prefix rows  segments  in index  NOT in index  duplicate names
      run_cell0_seed23.json            10         9         9             1  none
      (no other bundle has an extra prefix row or a duplicate name)

      INDEX seg_08     "Risk-weighted assets — seg_08"
      NOT-IN-INDEX     "Risk-weighted assets — seg_08 standardised recalculation"

  **It is a manager-created REMEDIATION whose name STARTS WITH the prefix but is a different
  string.** **Every segment's exact name appears exactly once in every one of the 18 bundles.
  THERE ARE NO DUPLICATE KEYS.**
- **★ LS's FOLLOW-ON IS WITHDRAWN.** *"Every published figure derived by name from that bundle gets
  re-derived by id"* was conditioned on ambiguity holding. **It does not hold. Nothing is
  re-derived on ambiguity grounds, and "not recoverable from these bundles" stays exactly as
  recorded — not strengthened, not withdrawn.**
- **THE REAL EXPOSURE IS A MISS, NOT A COLLISION.** The remediation resolves to no segment under an
  exact-key lookup, so its work is **ABSENT** from anything that lookup feeds — **UNATTRIBUTED, not
  MISATTRIBUTED.** That is the defect already on record (the manager remediation invisible to the
  metering path), **seen from the join side instead of the capacity side.**
- **WHERE A PREFIX PREDICATE IS USED THE EXPOSURE IS REAL AND ALREADY DOCUMENTED** —
  `finance_env.py:171`, `task.name.startswith(SEGMENT_TASK_PREFIX)`, which is **how the remediation
  got charged against the segment allotment.** **So the L8 conversion is still right and its
  argument changes: "a PREFIX PREDICATE captures things that are not segments", NOT "the key is
  ambiguous."**
- **★ RR's NARROWER QUESTION — *does any published figure route segment work through
  `segment_lookup` and drop the remediation?* — CLOSES CLEAN (LS).** All three occurrences of
  `segment_lookup` are inside **`_install_dry_run_stubs()`** in `run_finance_episode.py`.
  **It is DRY-RUN MACHINERY ONLY, never a live run, and NO PUBLISHED FIGURE ROUTES THROUGH IT.**
  Which is exactly what L8's own spec said when it put that site last. **The miss is real in the
  machinery path and reaches no reported number.**
- **★ THE CONSTRUCTION-PATH RULE, A FOURTH TIME AND THIS TIME ON RR — and they named it themselves:
  A COUNT NAMED THE POPULATION WHILE THE SHAPE THAT PRODUCED IT WENT UNNAMED.** *"Ten rows for nine
  segments"* is consistent with **two different defects with different consequences, and only one
  was real.** **RE explicitly declined to state the consequence before knowing which shape it was,
  and was right to** — they said so in the same message that handed over the count.
  **The instinct to check before it reached a record was right; the message that preceded the check
  should have said "if" rather than "then".**

### 2026-08-09 — NO BACKLOG STEP IS ACTIONABLE. The drift findings are attached to the L9 package

**Stated rather than worked around, per the cron's own instruction.**

    L9   [!]  blocked on the RESEARCHER -- team side closed, standing rule 7 satisfied
    L2a  [x]  CLOSED 2026-08-09 -- this line read '[~] B2 with RE' and was STALE
    L8   [~]  awaiting RR's review under standing rule 7
    L3   [!]  blocked on L9
    L5   [!]  blocked on L9
    L1, L4, L6, L7  [x]

**Every step is done, blocked, or has the ball with a peer. Nothing is the lead's to advance, and
the L4 drift check — the cron's fallback — was run LAST firing; the brief has not changed since, so
re-running it would be inventing work.**

- **★ WHAT WAS ACTUALLY OUTSTANDING AND MINE: the drift findings were in the record but NOT attached
  to the decision the researcher is holding.** They had the L9 choice (partial overlap vs disjoint)
  and the drift check (the brief names two manipulations) **as two disconnected items, and DRIFT 1
  bears directly on the L9 choice rather than sitting beside it.**
- **NOW ATTACHED in `RESEARCH-CRON-STATUS.md`'s CURRENT STATE, above the open-item note:**
  **the whole partial-overlap/disjoint comparison is a comparison of COVERAGE LATTICES. If the
  intended manipulation is METHOD SUBSTITUTION, the L9 decision is well-posed but answers a question
  the brief does not ask — and the four channels would carry a different kind of fact about the
  newcomer. If it is COVERAGE, §4 and §6 need amending and the decision stands as put.**
  **Read the drift check BEFORE deciding, because it may reframe the question rather than answer
  it.**
- **Header corrected:** the status file still said *"2026-08-08, after the cleanup and the ceiling
  fix"* while carrying 2026-08-09 content — **a document whose own date names a state it no longer
  describes**, which is the provenance defect in the file that exists to prevent it.

### 2026-08-09 — L8 CLOSES `[x]`. One non-blocking finding, and a pattern with a direction

Records: `records/L8/L8_review_RR.md`, `records/L8/L8_review_LS.md`.

- **STANDING RULE 7 SATISFIED** — acceptance output, RR's review (no blockers), LS's review (one
  non-blocking finding). **Both reviews verified against the CODE rather than the report**, because
  three checks this week passed while the thing they were meant to catch was untouched.
- **VERIFIED IN SOURCE (LS):** three analysis sites join on task id and **no live name join
  remains** (the only surviving mention is a docstring describing what was replaced);
  **`name_before` is captured at `manager_actions.py:822` and the mutation is at `:824` — correct
  order**; `task_renamed` is emitted at `:842`, **outside** the `if self.new_description:` block;
  RR's finding 2 is closed — `finance_fabrication.py:261` is `segment_tasks[segment_id]`, which
  **raises on a missing key** instead of defaulting to `None`; and the retracted collision claim is
  removed with the retraction stated in place.
- **THE CONTROL WAS BUILT FIRST AND FAILED AGAINST THE CODE AS IT STOOD — 9 hits → 8 on a rename.**
  **That ordering is why the null is worth anything: a null from a control never shown able to fail
  is not evidence.**
- **★ FINDING (LS, non-blocking): `task_renamed` fires on `new_name` BEING SET, not on the name
  CHANGING.** `manager_actions.py:823` guards on `if self.new_name:`, so **a manager re-sending the
  current name emits `task_renamed` with `name_before == name_after`.** Not a blocker — the event
  carries both values and nothing branches on its presence — **but it undercuts the justification
  RE gave, which is the right justification:** *"without it, 'no rename occurred' and 'a rename
  occurred and was not logged' are the same observation."* **A no-op emission makes `task_renamed`
  not mean renamed**, which is the same shape as everything else in this arc: **a field whose name
  asserts more than its condition establishes.** One-line guard.
- **WHAT L8 DOES NOT ESTABLISH:** the null shows the conversion **changed nothing on data we already
  hold**. It cannot show the old join never missed on those bundles — **"not recoverable from these
  bundles" stands and propagates.** **The conversion's value is FORWARD-LOOKING and the record says
  so rather than implying an audit it did not perform.**
- **★ A PATTERN WITH A DIRECTION, worth its own rule rather than folding into an existing one.**
  RE propagated RR's collision escalation into a docstring and a commit message **without
  checking**, after RR had withdrawn it. **Third instance this phase of one agent adopting
  another's number unchecked:** RE adopting RR's *"nA=0 is identical to the current template"*, LS
  adopting RR's 41/19 per-seed split, and now this.
  **All three were RR's figures, adopted by someone else, and all three were later corrected by
  RR.** The flow is **one-directional**, and the reason is visible: **RR reports MEASUREMENTS, and a
  measurement reads as settled in a way an argument does not.**
  **The differ-test rule covers AGREEMENT BETWEEN TWO RESULTS. It does not cover A SINGLE RESULT
  BEING CARRIED FORWARD BY SOMEONE WHO DID NOT PRODUCE IT.**

### 2026-08-09 — ★ THE ONE-DIRECTIONAL FRAMING IS WRONG. Corrected, with the rule RR wrote instead

**Supersedes the "pattern with a direction" note in the L8 entry above.** That entry stays as a
record; **its DIRECTION claim is withdrawn and its MECHANISM is replaced.**

- **★ INSTANCE 3 IS THE COUNTER-EXAMPLE and contains unchecked adoption IN EACH DIRECTION WITHIN
  TWO STEPS:**
  **(1)** RE measured *"ten rows for nine segments"* and **explicitly declined to state the
  consequence**, naming the two possible shapes and saying they had not verified which.
  **(2)** RR built on it **before verifying which shape it was**, and sent LS the stronger reading.
  **(3)** RE then propagated RR's escalation into a docstring and a commit message.
  **So at step 2 the unchecked adopter was RR and RE was the careful one — and the ORIGIN FIGURE
  WAS RE's.** **Any pattern putting RR at the head of the chain has instance 3 pointing the other
  way. That leaves two instances, which is an anecdote.**
- **★ AND THE MECHANISM WAS WRONG IN A WAY THAT MATTERED.** LS wrote *"a measurement reads as
  settled in a way an argument does not"* — **true, and it does not explain the failures.**
  **What was adopted in all three cases was A NUMBER WITHOUT ITS CONSTRUCTION:**

      "nA=0 identical"   a COMPARISON missing its COMPARATOR
      0.683              a MEAN read as a DISTRIBUTION
      ten-for-nine       a COUNT read as a SHAPE

  **Each was TRUE, and each was used for a claim it did not license. That is not
  measurement-vs-argument — it is the COMPARATOR-PATH RULE WITH THE ARROW REVERSED.**
- **SO NO NEW PRINCIPLE IS NEEDED, ONLY THE MISSING HALF.** The existing rule binds the **PRODUCER**
  (*a comparator names its construction path*). **Nothing binds the RECIPIENT** — and **a number
  arrives looking complete, because a value, a unit and a decimal point do not reveal what is
  absent.** RR's rule:

  > **Before building on a number you did not produce, STATE ITS CONSTRUCTION. If you cannot, you
  > may report it as someone else's and stop there — but you may NOT DRAW A CONSEQUENCE FROM IT.**

- **LS's own observation goes in as the reason a CONDITIONAL is not enough:** *a specified
  consequence makes the antecedent feel more established than it is.* **RR used "if" and it still
  functioned as "then", which is why a retraction was needed rather than a result.**
- **★ THE MITIGATION THAT WORKED TWICE WAS NEITHER CARE NOR VIGILANCE — IT WAS A QUESTION.**
  *"Which row is the tenth?"* and *"is that a mean or a distribution?"* **A QUESTION TERMINATES;
  VIGILANCE DOES NOT.** That is the rule's operative half, because *"be more careful about numbers
  from peers"* is unenforceable and **asking one specific question is not.**
- **AND THE REASON TO PREFER IT, in RR's terms, against their own flattery: the defect is IN THE
  HANDOFF, NOT IN A PERSON.** **If the pattern were recorded with RR as the privileged source, the
  next reader concludes their figures are the reliable ones — and instance 3 says they are not
  reliable enough to skip the question.**

### 2026-08-09 — L2a CLOSES `[x]`. Everything but L9 is done, and two stale markers are corrected

- **L2a `[x]`.** RE fixed B2 and RR re-ran **all six sub-cases** before lifting:

      B1a missing task_class                      RAISES
      B1b missing applied                         RAISES
      B2a absent from a NON-EMPTY parse_detail    RAISES
      B2b EMPTY parse_detail                      classified + flagged uninterpretable
      B2c parsing ran, entries present            not flagged (the other direction)
      B3  assigned id absent from index           RAISES

- **★ LS's PRIOR QUESTION WAS THE RIGHT ONE AND ITS ANSWER IS THE FINDING: the acceptance did NOT
  REACH the B2 branch.** Its only `parse_detail` is `{}` and the helper defaults to `{}`, so **the
  partial-gap branch was UNREACHABLE and would have passed indefinitely. A control never wired, not
  a missed line.**
- **B2 RESOLVED BETTER THAN THE BLOCKER ASKED.** RE was right not to raise on an EMPTY
  `parse_detail` — **a machinery run has no deliverables, so raising rejects a legitimate bundle.**
  The state is marked **uninterpretable in the record** instead, and they went past the
  recommendation with **`interpretable_counts(result)` raising for any consumer that reports those
  counts** — the §B refusal enforced at the point of use rather than announced beside it.
- **★ LS's "MAP EACH BLOCKER TO ITS FIRING CONTROL" STANDARD IS IMPLEMENTED, and RE checked the map
  itself first: they fed it a FABRICATED blocker with no guard and confirmed it reports UNCOVERED
  before trusting it to report covered.** All six covered.
- **THE RENAME GUARD IS FIXED** — `task_renamed` now guards on `self.new_name != name_before`.
  **And the control was built to DISTINGUISH rather than merely to fire**, which is the property
  three checks lacked this week: real rename → emits; no-op → emits nothing; no `new_name` → emits
  nothing. **The `updates` summary deliberately keeps the old condition** — a re-sent name is still
  a refinement the manager performed, **a different question from whether the name changed. Two
  conditions, two consumers, stated rather than merged.**
- **★ RE's ADDITION TO THE ADOPTED-NUMBER MECHANISM, which complements RR's rather than competing:
  in all three cases THE ADOPTED NUMBER SUPPORTED A CONCLUSION THE ADOPTER ALREADY HELD.** RE took
  *"nA=0 is identical"* while arguing the forcing had inflated everything, and *"a collision does
  not even need a rename"* while arguing the name join was unsafe. **"The number was not scrutinised
  because it was not load-bearing for what I believed — it was decoration on a case I had already
  made. That is why vigilance does not catch it: nothing feels risky about a supporting detail."**
  **So the two halves are: what made the number ADOPTABLE (it arrived without its construction) and
  what made nobody LOOK (it supported what they already thought).**
  **RE's rule form, the crispest of the three: A FIGURE YOU DID NOT PRODUCE GETS ONE QUESTION BEFORE
  IT IS REPEATED — not verification, just one.**
  **And RR's half, theirs: both times they stated a READING as a FINDING. ADOPTING TOO FAST AND
  ASSERTING TOO HARD ARE THE SAME FAILURE MET IN THE MIDDLE**, which is why a rule aimed at one end
  would not have caught any of the three.
- **★ TWO STALE MARKERS CORRECTED, AND IT IS THE L6 SHAPE A SECOND TIME.** `L2a`'s step line still
  read *"TWO OF THREE FIXED… B2 is STILL SILENT while the acceptance reports PASS"*, and the
  no-step-is-actionable table still read `L2a [~] B2 with RE`. **Neither merely LAGGED — both
  ASSERTED that a blocker was live when it was closed**, and unlike L6 **the stale claim was in the
  INDEX rather than at the top of a file, so it is the version a reader hits first.**
  **Twice now. Markers in this file have twice stated a false state rather than an out-of-date one.**
- **FULL SWEEP (RE):** ten acceptances exit 0, tree clean, `pytest tests/` 124 passed with the one
  live-API failure that predates this work and cannot pass without model spend.

**STATE: L1, L2a, L4, L6, L7, L8 `[x]`. L3 and L5 blocked on L9. L9 with the researcher.
Nothing is open to the team.**

### 2026-08-09 — PHASE CLOSED TO THE TEAM. A fourth instance, and a rule deliberately NOT written

- **★ RR DECLINED TO WRITE A SEVENTH RULE, and recorded the judgement rather than the absence.**
  *"Six rules in a day is already at the edge of what a file gets read at."* **A rules file nobody
  finishes enforces nothing**, and that is a real constraint on the intervention rather than a
  concession.
- **AND THE REASON THE MARKER PROBLEM HAS NO MECHANICAL ANSWER YET:** the citation check worked
  because **a filename either resolves or it does not.** A step marker quotes a **TESTABLE CLAIM IN
  PROSE** — *"B2 is STILL SILENT"* — and re-evaluating it **needs semantics, not a resolver.**
  **The nearest mechanical form is the provenance rule again: a marker quoting a testable claim
  CITES THE CHECK THAT ESTABLISHES IT, so it can be re-run.** **Held until a third instance rather
  than guessed at now.**
- **★ FOUR REPORTS OF SUCCESS THAT HAD NOT BEEN CHECKED, ALL CAUGHT BY RE-RUNNING RATHER THAN
  READING** — the family the marker cases would join:

      RE's module printed a COMPLETE TABLE after raising and writing no record
      LS's citation tool ran a COMPONENT-LEVEL control on a pipeline-level claim
      RR's fixture had controls firing on the WRONG GUARD, looking like four clean passes
      LS's marker edit matched NOTHING for one line and reported success for the half that landed

  **By a third marker case there will be enough instances to see whether the answer is ONE check or
  FOUR.**
- **★ RE's HALF OF THE ADOPTED-NUMBER MECHANISM PREDICTS WHERE THE NEXT ONE COMES FROM, which is
  why it is the better half:** **not a headline anybody would check, but a SUPPORTING FIGURE nobody
  thinks is load-bearing.** **Ten-for-nine was exactly that** — RE reported it as a supporting
  argument and moved on; RR escalated it into a claim.
- **★ THREE HALVES, ONE FAILURE, AND NONE OF THE THREE AGENTS WAS DOING THE RECKLESS THING.**
  **RE adopted fast because the number supported them; RR asserted hard because they had measured
  something adjacent; LS pre-specified a consequence because conditioning FELT LIKE CAUTION.**
  **A rule aimed at any single end catches none of it — which is why the operative form is a
  QUESTION: it is the only intervention that does not depend on the person noticing they are at
  risk.**

**STATE: L1, L2a, L4, L6, L7, L8 `[x]`. L3 and L5 blocked on L9. L9 with the researcher.
NOTHING IS OPEN TO THE TEAM.**

### 2026-08-09 — EVERYTHING IS `[x]` OR BLOCKED. Firing spent on L4's SECOND HALF, the §3 novelty check

Record: `records/L4/novelty_check_LS_2026-08-09.md`.

**Every step is `[x]` or blocked on the researcher — the cron's condition for the drift check.
Re-running the design-vs-code comparison against an UNCHANGED brief would reproduce the same three
findings, so this firing did the half the 2026-08-09 drift check explicitly named as not done:
"it does not verify the brief's §3 novelty claims."**

**The question asked: DOES §3 SURVIVE BOTH READINGS OF DRIFT 1?** If the brief cannot say whether
the manipulation is method substitution or a coverage lattice, **the novelty claim must hold either
way or it is contingent on an unsettled question.**

- **N1 — PROPERTIES 1, 2 AND 4 ARE INVARIANT.** The manager allocates under either perturbation;
  the newcomer inherits persistent workflow state either way (**the property §3 itself calls "the
  uncontested vertex"**); exogeneity is unaffected and never leads alone. **Three of four do not
  care.**
- **★ N2 — PROPERTY 3'S NEIGHBOURS ARE CAPABILITY/PROFILE ROUTERS, WHICH FITS THE COVERAGE
  READING.** It is the property carrying the wedge, and **every neighbour cited on it describes
  WHAT AN AGENT IS APPROVED OR SUITED FOR**: FlyRoute's *"developer-provided registration
  description that may be incomplete or inaccurate"* (§3 calls it *"the closest work on the card
  channel"*), and DRAMA's *"affinity evaluations consider… agent capabilities"*, distinguished as
  a single always-accurate attribute.
  **So the brief carries THREE signals about its own manipulation and TWO point to coverage:**

      §3 novelty       neighbours are capability/profile routers   -> COVERAGE
      §4 scope cond.   "COVERAGE information cannot address..."    -> COVERAGE
      §4 perturbation  "prompt-level METHOD SUBSTITUTION"          -> METHOD

  **THIS NARROWS DRIFT 1 RATHER THAN LEAVING IT OPEN — more likely a STALE §4 SENTENCE than a live
  question about what the study is.**
  **STATED AS THE WEAKER CLAIM, because the stronger one is available and unsupported:** a method
  substitution could be *described* in a capability profile, so the neighbours are not strictly
  incompatible with it. **What is true is that §3's neighbour analysis WAS WRITTEN FOR A CAPABILITY
  CHANNEL and would need re-doing under the method reading.** **Evidence for the researcher's
  decision, not a substitute for it.**
- **★ N3 — THE PHASE'S MAIN PRODUCT IS ABSENT FROM §3 AND §7.** §7 frames phase 1 as **DIAGNOSIS —
  a failure taxonomy per cell**, and **all five listed failures are MANAGER failures observed in
  runs.** **The `nA = cap` mechanism is structurally different: a CHARACTERISATION OF WHEN THE
  SETTING CAN MEASURE ANYTHING AT ALL**, derived offline, holding across three capacities, and
  explaining why the shipped lattice is exactly zero on a realistic portfolio.
  **§7's dichotomy — "failures found → build a policy; no failures → a capability result with
  boundary conditions" — has NO SLOT for it. It is, in the brief's own vocabulary, BOUNDARY
  CONDITIONS ARRIVED AT WITHOUT THE CAPABILITY RESULT**, and the only thing this phase produced
  that does not depend on a run. **Raised, not resolved — and it interacts with the L9 choice,
  because a paper that REPORTS it makes a different claim from one that uses it to PICK A LATTICE.**
- **N4 — A "MAY NOT MAKE" CLAUSE ALREADY COVERS THE L9 FIGURES AND SHOULD BE APPLIED.** §3 prohibits
  *"any corpus figure as a portable result (setup-level priors)"*. **2.258%, 5.272% and 0.000% are
  setup-level in exactly that sense — properties of a lattice, a cap and a segment mix — and nothing
  in the record currently states that they inherit the clause, while the decision package quotes
  them.** They are **a lattice comparison inside this environment, not a portable statement about
  card channels.**
- **WHAT IT DOES NOT ESTABLISH:** it does **not** verify §3 against the primary sources (done and
  reviewer-verified 2026-08-06, not re-run) — **and that is exactly the work needed IF the
  researcher settles Drift 1 toward METHOD.** And it does **not settle Drift 1**: two of three
  signals is evidence about the brief's internal consistency, **not about what the researcher
  intends.**

### 2026-08-09 — THE BACKLOG IS EXHAUSTED. Saying so, per the cron's own instruction

    L9   [!]  blocked on the RESEARCHER
    L3   [!]  blocked on L9
    L5   [!]  blocked on L9
    L1, L2a, L4, L6, L7, L8   [x]

**Nine steps: six done, three blocked, none actionable. No peer activity and no inbox since the
last firing.**

**BOTH HALVES OF THE L4 DRIFT CHECK — the cron's fallback — ARE NOW DONE AGAINST AN UNCHANGED
BRIEF:** the design-vs-code comparison (`records/L4/drift_check_LS_2026-08-09.md`) and the §3
novelty check (`records/L4/novelty_check_LS_2026-08-09.md`). **A third variant would be the
invented work the instruction exists to prevent, so it is not run.**

- **ONE ITEM CLOSED, carried over from the novelty check rather than invented: N4 APPLIED.**
  `STUDY1_FOUNDATION.md` §3 forbids quoting *"any corpus figure as a portable result (setup-level
  priors)"*, **and nothing in the record said the L9 figures inherit it while the decision package
  quotes them.** Now stated in `RESEARCH-CRON-STATUS.md` beside the numbers: **0.000%, 2.258% and
  5.272% are properties of a lattice, a cap and a segment mix — a LATTICE COMPARISON INSIDE THIS
  ENVIRONMENT, not a portable statement about card channels.**
- **NOTHING ELSE IS OPEN TO THE TEAM.** The next thing that happens is the researcher's L9 decision,
  which unblocks L3 and L5.

### 2026-08-09 — the "everything is green" claim was UNVERIFIED. Verified now, and it was not

**Third consecutive firing with nothing actionable — state identical, inbox empty, tree clean.**
Rather than a third variant of the drift check, the firing went to **checking the state this record
has been asserting**, before a long idle period.

- **★ AND THE VERIFICATION ATTEMPT WAS ITSELF A FIFTH INSTANCE OF THE WEEK'S FAMILY.** The first
  sweep printed `exit=0` for all five checks **while four of them had not run at all** —
  `ModuleNotFoundError: No module named 'pydantic'`, because they need the project venv and were
  invoked with bare `python3`. **The `exit=0` was the exit code of the printf pipeline, not of the
  module.** **A report of success that had not been checked, produced by the act of checking.**
- **RE-RUN CORRECTLY under `.venv/bin/python`:**

      check_path_alignment          exit 0
      check_amplifier_dependence    exit 0
      check_card_belief_model       exit 0
      check_native_lattices         exit 0
      check_record_citations        exit 0 (after the fix below)

- **AND THE CITATION CHECK WAS FAILING.** `records/L4/drift_check_LS_2026-08-09.md` — **the record
  that REPORTED the deleted-module finding** — names `check_announcement.py` in order to report it,
  which is the **self-referential category** the tool's docstring already names as taking the marker
  by standard form. **Third instance of that category** and the first outside `BACKLOG.md`.
  Annotated in place; the check now passes.
- **SO THE "ten acceptances exit 0, tree clean" STATE WAS REAL BUT UNRE-DERIVED AT THIS COMMIT**, and
  one check had drifted red since it was last run. **The claim was carried forward, not re-checked
  — which is precisely the recipient-side rule applied to one's own earlier report.**
- **NOTHING ELSE IS OPEN.** Six steps `[x]`, three blocked on the researcher's L9 decision, both
  halves of the L4 drift check done against an unchanged brief.

### 2026-08-09 — THE CRON IS CANCELLED on the researcher's instruction

Job `b8cb48a7` (`17,47 * * * *`) deleted. **Recreation procedure and the verbatim prompt are in
`RESEARCH-CRON-STATUS.md` §7**, with the standing note that it should be recreated **only once the
L9 decision has landed** — until then the loop has no reachable work.

- **It had reached a fixed point: THIRTEEN consecutive firings with nothing actionable.** Every
  step `[x]` or blocked on the researcher; both halves of the L4 drift check done against an
  unchanged brief; the acceptance suite verified green at firing ten.
- **The firings were NOT wasted, and the useful ones are worth naming** because they mark where a
  no-work loop still had value: **firing 1** ran the design-vs-code drift check (three findings,
  all the researcher's); **firing 2** ran the §3 novelty half, which narrowed Drift 1 from an open
  question to a probably-stale sentence; **firing 3** applied the brief's non-portability clause to
  the L9 figures; **firing 4** re-derived the "everything green" claim and **found one check had
  drifted red** — while the verification attempt itself produced a fifth instance of the week's
  report-of-success-that-was-not-checked family. **Firings 5–13 produced nothing and were reported
  in one line each, without adding entries here.**
- **The rule that fell out and is worth carrying: a scheduled loop against a blocked backlog stops
  producing after the deferred work is exhausted.** The first four firings drained a real queue —
  work that was genuinely outstanding but not urgent. **After that the loop was polling, and
  polling a decision that only a human can make is not research.**

### 2026-08-09 — RESEARCHER RULING. L9 CLOSES `[x]`; a run is authorised; a scoring proposal is open

**Step 1 of three is DONE. Steps 2 and 3 are with the team.**

- **★ L9 IS SETTLED: PARTIAL OVERLAP.** Recorded in `STUDY1_FOUNDATION.md` §10 with the priced
  comparison (2.26% at a realistic mix, non-zero on 60/60, against the shipped arrangement's 0.000%
  on 0/60), the realism argument, and the derivation that it **ships UNAMPLIFIED** — forcing costs
  it twice, by draining the lied-about class and consuming the free slot the channel needs.
  **L3 and L5 unblock.**
- **★ THE PERTURBATION IS A CAPABILITY DIFFERENCE, NOT A METHOD SUBSTITUTION** (§4, amended in
  place, superseded text retained). The successor is **certified for different asset classes —
  equally competent, differently PERMITTED.** Settles the Drift 1 ambiguity, and §3's novelty
  argument was already written for this reading (its neighbours on property 3 are capability/profile
  routers). **The three requirements still bind and are satisfied:** allocation-visible because
  coverage decides who can unlock IRB; trace-distinguishable because the SA fallback shows in the
  reported metric; successor-reachable per the gate.
  **Ruling ground: it is the only reading under which the manager's information has a job to do —
  when a capability leaves the team entirely, no channel can recover it.**
- **THE GATE IS RUNNABLE AGAIN.** §6's first PASS criterion asked for an outcome *"demonstrably via
  the SUBSTITUTED METHOD"*, which has no referent under a capability perturbation. **Rewritten,
  keyed to certification: ≥1 correct post-swap outcome on a class the successor IS certified for,
  with the reported metric matching IRB truth.** Same test, different key.
- **THE POOL IS RE-DERIVED THROUGH THE COMMITTED MACHINERY** —
  `records/R2/instance_selection_partial_segs1.json`. **15 of 40 admitted; band 0.36–4.76%, median
  2.12%; study seeds 26 / 39 / 37.** **The rule is UNCHANGED** (same rank-terciles, same
  pre-committed draw seed, same zero-ceiling exclusion); **only the population moved, because the
  design did.** Default reproduces the prior record on every number — verified, and it caught a bug
  introduced while making the change. **A hardcoded seed in `caveat_1` naming an instance that was
  not the one chosen is fixed and now interpolated.**
- **STEP 2, AUTHORISED: same cell, 2–3 episodes, seeds 26/39/37 — 6–9 episodes, flash, parallel.**
  Two purposes: **does it run at all** (nothing has ever executed on this arrangement; every finding
  to date is offline arithmetic) and **the first post-repair σ**, which is the one quantity that has
  blocked every detectability statement and cannot be computed offline.
  **Prediction protocol running; LS's is committed, peers' requested privately, none relayed.**
  **LS: it runs but not cleanly; σ_total lands between 0.05 and 0.08, not dramatically below the old
  0.0768, because 75% of that variance was manager-level; so at the median seed the required n stays
  above 100/arm.**
- **★ OPEN — THE RESEARCHER PROPOSES AMPLIFYING THE SCORE so a single misplacement produces a bigger
  signal.** The instinct is sound: 2% is about **0.6 of one misplaced job**.
  **LS's objection, flagged as load-bearing and UNMEASURED: σ is in the same units as the effect.**
  Widening the IRB−SA penalty widens the run-to-run variation in the score as well, so `effect/σ`
  may not move — **a units change dressed as a sensitivity gain**, which is the shape this project
  has been fooled by repeatedly.
  **Partly computable now:** σ_alloc was measured at 0.0384 against σ_total 0.0768, so how σ_alloc
  scales with the penalty is derivable offline. **What is not derivable is whether σ_manager scales
  — and that is 75% of the variance.** If σ_manager is dominated by refusals and non-completion,
  amplification may genuinely help; if by allocation choice, it cannot. **Step 2 supplies the
  decomposition. NOTHING IS IMPLEMENTED BEFORE IT.**
  **AND A BETTER-TARGETED VERSION OF THE SAME INSTINCT, to be priced against it: on seed 41 only
  5 of 9 segments are CONTESTABLE AT ALL** — four score identically whoever gets them and carry no
  information about the manager's decision. **Raising the contested share enriches the decision
  surface WITHOUT touching the risk weights, which are grounded in real Basel tables. Widening the
  penalty moves the environment away from Basel; contesting more segments does not.**

### 2026-08-09 — STEP 2 HELD: the runner cannot build the chosen arrangement, and would fail SILENTLY

- **★ FOUND BEFORE SPENDING, NOT AFTER.** `finance_env.build_environment(seed)` calls
  `gen.generate(seed)` with **no lattice and no `shared_class_segments`** — the parameter added to
  the generator **stops there; `run_finance_episode` never learned about it.** So the run would have
  built `current` at `segs=4` while the pool was derived under `partial` at `segs=1`:

      seed      pool (partial, segs=1)      runner (default: current, segs=4)
       26     nA=1    0.355%                nA=4    0.000%   <-- DEAD
       37     nA=1    3.239%                nA=4    1.845%
       39     nA=1    2.122%                nA=4    4.201%

  **SEED 26 WOULD HAVE BEEN A ZERO-CEILING INSTANCE — precisely what the selection rule exists to
  exclude.** The old selection *"picked two dead instances out of three"*; **this would have done it
  again, silently, by a different mechanism**, and the bundle would have recorded
  `instance_seed: 26` and looked entirely correct.
  **The phase's signature fault once more: a parameter that exists on one path and not another,
  DEFAULTING TO A LEGAL VALUE.** `lattice="current"` is a valid lattice; nothing raises.
- **AUTHORISED:** thread `lattice` and `shared_class_segments` through
  `build_environment` → `run_finance_episode`, **and record both in the bundle**, so a bundle can
  never again be silent about which arrangement produced it.
- **★ AND THE GUARD IS THE MORE IMPORTANT HALF: the runner REFUSES a seed whose arrangement does not
  match the selection record it claims to be running.** Passing the right flags is something a
  person must remember; a guard is something that fires. **This is the first place the two-artefacts-
  disagreeing failure can be made IMPOSSIBLE rather than merely fixed.**
- **RUN AUTHORISATION IS HELD** until the guard exists and has been **round-tripped**: build through
  the runner, read the arrangement back out of the bundle, confirm it matches the selection record,
  **and confirm the guard FIRES on a deliberate mismatch.** *A control that has not been shown to
  fail is not a control.*
- **★ WHAT STEP 2 CAN AND CANNOT CLAIM (RR, sharpened by LS).** Three seeds × three episodes pools
  to **df = 6**; the exact 95% interval on σ is **[0.64s, 2.20s] — a 3.4× span in σ and a 12× span
  in required n.** *(RR framed it as n=3 → factor 3 and 9; pooling within-seed is what makes it 3.4
  and 12. Pooling helps and does not save it.)*
  **So step 2 reports a FEASIBILITY VERDICT and a σ ORDER OF MAGNITUDE. It does not report a σ, and
  it sizes nothing.** **A σ good to ±25% needs ~50 episodes — a separate authorisation, to be asked
  for explicitly rather than discovered when step 3 needs a number step 2 cannot give.**
  **RR predicted the strongest temptation of the coming days will be to size on it anyway**, because
  it will be the first post-repair σ we have ever had. **It goes in the record with its interval
  attached or it does not go in.**
- **PREDICTIONS, all three committed before any run.** **LS:** runs but not cleanly; σ 0.05–0.08;
  n > 100/arm at the median seed. **RR:** runs 3/3; σ 0.045–0.070; and *three episodes cannot
  estimate σ*. **RE:** runs, first failure in the ASSEMBLY path rather than the model path; σ
  0.03–0.06; n 40–120/arm — **declared as formed AFTER finding the defect above and therefore to be
  discounted**, which is the right disclosure.
  **LS's review of RE's MECHANISM: the number is plausible and the stated reason conflates variance
  with effect.** *"Manager behaviour with nothing to respond to"* does not shrink σ — a manager whose
  channel is worth zero still allocates differently run to run and those allocations still score
  differently. **A flat channel removes the systematic ARM DIFFERENCE, not the SPREAD.** What moves
  σ_alloc between arrangements is how widely the score varies across the allocation space — a
  property of the certification table and the mix. **Their direction may be right for that reason
  instead; a prediction landing on the right number for the wrong mechanism teaches nothing.**
- **THE SCORING PROPOSAL, sharpened by RE and now stated as a proof rather than a doubt:** widening
  the IRB−SA penalty is a **UNITS change** — the ceiling is a share of oracle and oracle scales with
  the same penalty, so **`effect/σ` is invariant to first order, and for the allocation component it
  PROVABLY buys nothing if the penalty enters linearly.** Step 2's σ_alloc measurement confirms it
  directly.
  **AND THE ALTERNATIVE IS THE CORRECT TARGET, not a compromise: the four uncontested segments are
  DENOMINATOR WITH NO NUMERATOR.** Raising the contested share changes **how many segments CAN
  differ** rather than **how much each differs by** — **a real sensitivity gain rather than a
  rescaling, and it leaves the Basel weights untouched.** **Being priced offline while step 2 is
  blocked.**

### 2026-08-09 — ★ 69% OF THE VARIANCE IS NON-COMPLETION. Run authorised with the split attached

Records: `records/L9/penalty_scaling_RR.md` (RR); RE's blocker fixes and dry runs.

- **★ THE LARGEST FINDING, AND NEITHER PROPOSAL ADDRESSES IT.** Recomputing per-segment scores from
  `parse_detail` against truth across the 18 bundles:

      lost to ZERO-scoring segments   mean 1.611  SD 0.916   <- penalty-INVARIANT
      lost to GRADED (misroute) error mean 1.101  SD 0.616   <- scales with the penalty
      share of shortfall VARIANCE that is penalty-invariant : 69%

  **18% of oracle is lost to segments that produced NOTHING, with an SD half again the graded
  component's. Both levers operate on the 31%.** Zero-counts run 0–3 **at a fixed seed**, so it is
  execution variation, not instance variation. **The highest-value target for detectability is not
  the scoring at all.**
- **★ RULING BEFORE ANYONE ACTS ON IT — "reduce non-completion" is the obvious move and is NOT
  obviously legitimate. L2a's split decides it:**
  **never assigned** → the manager failed to allocate: **that is the DV, not noise**, and removing
  it removes what we measure. **assigned and never executed** → harness or worker failure:
  **noise, and may be removed.** **NOBODY TOUCHES NON-COMPLETION UNTIL THE SPLIT SAYS WHICH.**
  The split is emitted on the step-2 bundles at no extra spend.
- **LS's OBJECTION TO THE SCORING PROPOSAL WAS WRONG IN THE HALF THAT DECIDES IT.** LS said it "may
  buy nothing"; RE upgraded that to "provably buys nothing"; **both overstated it.**
  **`effect/σ` moves ×1.44 at k=2 and ×1.61 at k=3 — required n to 0.39 — with most of the gain in
  by k≈3.** Directionally right that it is bounded, **wrong that it is null.**
  **The cap is optimistic and fails conservatively:** `1 − min(1, rel_err)` pushes widened losses
  onto the **1.0 floor, where they become penalty-invariant too**, so ×1.79 is unreachable and the
  average clips near k≈6.7.
- **CONTESTED SHARE IS STRICTLY BETTER AND IS BEING PRICED.** Same structural shape — raises the
  effect and the graded variance, leaves the zero-loss alone — **but it does not move the
  environment off the Basel tables, and it does not saturate**, because it adds informative segments
  rather than enlarging losses on existing ones.
- **RR's THREE LIMITATIONS, all carried:** the decomposition mixes instance with execution variation
  (the fixed-seed 0–3 spread argues most is not instance-driven; it is not a clean within-cell
  split and no corpus gives one); **the k-table is a MODEL, not a measurement**; and **this σ is a
  shortfall SD across bundles, NOT the DV's per-episode σ — the decomposition transfers, the
  absolute numbers do not.**
- **★ AND IT STRENGTHENS THE STEP-2 CAVEAT BEYOND df=6: if non-completion is 69% of the variance,
  the first post-repair σ is mostly measuring COMPLETION RATE — which is precisely the quantity most
  likely to have MOVED under L1, L7 and L8.** Not merely imprecise; **measuring the least stable
  thing in the system.** Carried beside the interval wherever the number appears.
- **BOTH RUN BLOCKERS FIXED; RUN AUTHORISED (LS).** 2–3 episodes × seeds 26/37/39, one cell, flash,
  parallel, `selection_record` pinned.
  **Blocker 1 was WORSE than first reported: `build_cell_environment` carried the same bare
  `gen.generate(seed)` — and that is the path STUDY CELLS actually use.** Threaded through both
  builders; arrangement recorded in the bundle manifest. **The guard refuses a mismatched
  arrangement and a seed the record did not choose, with both negatives verified firing — and the
  first negative IS the real bug**, which is the strongest form of that check.
  **Blocker 2, findable only by the dry run: `task.name.startswith(prefix)` with `prefix`
  UNDEFINED** — a `NameError` on every dry run reaching a ready unassigned task, **so that branch
  had never once executed.** It sits **two lines below a comment saying to use `is_metered`, NOT the
  name** — **third instance this phase of a comment naming a failure directly above code repeating
  it.**
- **LS's PREDICTION, FIRST HALF CONFIRMED: "at least one assertion or acceptance fires on the first
  attempt" — TWO did, before a single model call.** RE's specified *assembly rather than model path*
  and was right on both. **Neither has anything on σ yet.**
- **AND THE DRY RUN CANNOT SPEAK TO THE THING THAT MATTERS: 16/16 completions on STUBS says nothing
  about completion under a model**, because the stubs always succeed. Given the 69%, **live
  completion rate is the quantity to watch.**
- **★ RE's NEAR-MISS, recorded because it is the week's lesson a fourth time and on a fourth person:
  they read the WRONG KEY, got `None`, BELIEVED A NULL, and edited two further sites on the strength
  of it** — in the same session as advocating positive controls for nulls. The fields were correct
  throughout, nested under `manifest`. **Four of four agents caught by their own rule, each on their
  own work, minutes after stating it.**

### 2026-08-09 — RESEARCHER RULING: two DESIGNED environments. L10 opened; cron live again

- **★ THE END PRODUCT IS TWO WELL-DESIGNED ENVIRONMENTS, not a filtered draw from sixty random
  ones.** *"An environment needs to be designed to show the gap. There is no point randomising it to
  zero, because then there is nothing for any manager — AI or human — to solve."* **Two is enough
  for initial testing.** Full spec at L10.
- **THE PROJECT ALREADY ACCEPTED THE PRINCIPLE FOR ONE DIMENSION AND ABANDONED IT FOR THE REST.**
  `_lattice_from_template` **CONSTRUCTS** the certification table — 210 possibilities enumerated,
  construction chosen deliberately — **while the segment mix, ratings and exposures are DRAWN per
  seed.** We hand-designed the part we understood and rolled dice for the part that decided
  everything.
- **★ WHY THE OBVIOUS OBJECTION DOES NOT APPLY, and this distinction is doing all the work:**
  **designing so a particular MANAGER scores well would be FITTING THE RESULT; designing so the GAP
  EXISTS is CALIBRATING THE INSTRUMENT** — the gap is computed with **no manager in the loop**
  (oracle minus card-believing-optimal, both solved exactly), **so there is nothing to fit to.**
  **RR is asked to attack precisely this line before anything is built:** is there a way to design
  an instance that is manager-neutral in the gap computation and still favours a particular manager
  behaviour in a live episode? **If that leaks, the step is unsound.**
- **THE TARGET HAS MOVED SINCE L9: zero gaps were the OLD arrangement's problem.** Under partial
  overlap **all 60 draws are non-zero** (0.03%–6%). **The problem now is that most draws are SMALL**
  — median 2%, long tail toward nothing. **Randomising spends the design freedom on producing weak
  instances and then averaging them.** And **admission still discards 25 of 40 for structural
  reasons unrelated to the gap.**
- **SIX PROPERTIES BY CONSTRUCTION, ASSERTED NOT HOPED FOR:** non-zero gap by construction;
  **`nA < cap`** (the free-slot condition the covered-lie regime needs); the card's lie lands on a
  class an incumbent still covers; capacity binds exactly; **Basel weights untouched** (the one
  thing that cannot be traded for sensitivity); and **admission passes as a POST-CONDITION rather
  than a filter — it stops being a sieve over draws and becomes an assertion that the built instance
  has the properties it was built to have.**
- **THE TWO ARE A SENSITIVITY LADDER, NOT TWO SAMPLES. ENV-A: maximum gap** — the instrument at full
  sensitivity; **a manager showing no effect there is decisive and ENV-B need not run. ENV-B:
  realistic gap** — what an honest study would use; **an effect on A but not B is a POWER STATEMENT,
  not a null.**
- **★ THE STEP-2 RUN STILL GOES FIRST — reason changed, decision unchanged. Its purpose is now a
  HARNESS measurement, not an instance one.** The 69%-of-variance non-completion finding is a
  property of the **model path**, not of any instance, **so it TRANSFERS to the designed
  environments** — measuring completion rate now is what informs the design, and running afterwards
  would learn the same thing later. **The dry run's 16/16 says nothing about it: stubs always
  succeed.**
- **CONTESTED SHARE AND THE k-TABLE FOLD INTO L10 rather than standing alone.** In a designed
  instance the contested share is **a parameter, not an outcome** — on seed 41 only 5 of 9 segments
  were contested and the other four were **denominator with no numerator.**
- **THE SELECTION MACHINERY MOSTLY RETIRES.** Rank-terciles over a random pool exist *because* the
  pool is random; if the family is designed to span the range, **the spread is the design.**
  **Nothing built today is wasted** — deriving the pool is what showed the arrangement produces a
  live signal at all, which had to be known before designing on top of it.
- **CRON LIVE AGAIN: job `9187b13e`, `17,47 * * * *`**, pointed at L10, carrying the five rules this
  phase paid for and an explicit instruction **not to re-run the L4 drift check.**

### 2026-08-09 — ★ BOTH OF LS's RULINGS OVERTURNED: the bucket boundary and the design axis

Record: `records/L10/design_neutrality_RR.md` (RR).

**1 — LS's NON-COMPLETION RULING RE-POOLED EXACTLY WHAT L2a UN-POOLED.**

LS ruled: *never assigned → DV; assigned and never executed → harness noise, removable.*
**"Assigned and never executed" is FOUR states, and L2a split it into them precisely to stop this
collapse** — its own docstring: *"one bucket and is now THREE, because the scope run showed it was
two populations with opposite meanings… **pooling them produced a rate that could not carry a
sign.**"*

**Two of the four are not harness failure at all:**
- **`refused_allotment`** — permanently barred, the allotment never releases within an episode.
  **The allotment IS the deliberate scarcity that creates the coverage channel**, so a manager
  assigning into a spent one is **manager error — the DV.** Removing it removes what
  capacity-displacement measures.
- **`refused_unavailable`** — the predicate says outright *"which a roster change can cause, so this
  is the state a swap run must be able to see separately."* **A roster change IS the manipulation.**
  **Under LS's ruling this would have been classified as removable noise, while the module says it
  is the signature the swap run exists to observe.**

**THE CORRECTED MAPPING (RR), adopted:**

    DV             never_assigned, refused_allotment, executed_and_declined
    MANIPULATION   refused_unavailable        <- must remain visible, never removed
    BUDGET/HORIZON refused_concurrency, unexecuted_no_refusal
    DEFECT         executed_but_unparseable   <- carries the uninterpretable flag
    MEASUREMENT    executed_and_parsed

**Two of eight are removable, not four** — and *budget/horizon* is a **third category**, not LS's
second. **`executed_and_declined` is a legitimate outcome**: a worker declining is a behaviour, and
in a study about handling a newcomer it is DV-adjacent, not noise.

**Why it mattered to catch before the split returns rather than after: the ruling PRE-COMMITTED the
bucket boundaries, and drawn at "assigned vs not" the split would have answered with the wrong
partition and the answer would have looked clean.**

**RR's concession, unprompted: the 69% figure does NOT distinguish these states** — it counts every
zero-scoring segment together, **which is the same pooling they were objecting to.** So it says the
variance is dominated by segments producing nothing; **it does not say how much is removable.**
Corrected form: *the highest-value target is the REMOVABLE SHARE of non-completion, currently
unknown, and the split is what gives it.*

**2 — ★ THE DESIGN-NEUTRALITY LEAK, MEASURED. LS's premise is true and the inference does not
follow.**

Natively, `shared_class_segments=1`, 30 seeds:

    lattice     card − ignorant    ceiling
    current             +0.8032      0.00%
    partial             +0.5804      2.18%
    disjoint            +0.3277      5.43%

**Monotone: the larger the ceiling, the LESS the card is worth against knowing nothing. So
MAXIMISING THE GAP MAKES IGNORING THE CARD A BETTER POLICY.**

**LS argued the gap computation contains no manager, therefore ordering by gap is manager-neutral.
The premise is correct; the inference is wrong — ORDERING INSTANCES BY GAP RANKS MANAGER POLICIES**,
because gap size and card-informativeness are inversely coupled. **ENV-A at maximum gap is precisely
where that confound is LARGEST, which is the opposite of what a decisive arm should be.**

**Three further leaks, argued rather than measured:** **tie-break skew** (the gap uses the D18
expectation; a live manager has a *systematic* rule, and the tie set has been measured spanning as
wide as the effect); **segment order** (the gap is a max over allocations and so order-INVARIANT,
while a manager reading a task list is order-SENSITIVE — **the enumeration-order hazard was
controlled one level down and the identical hazard sits one level up with nothing on it**); and
**exact capacity binding** (one feasible load shape means the manager chooses WHICH work and never
HOW MUCH — it deletes a dimension rather than favouring a policy, but **a manager whose competence
is load management can display none of it, and that should be declared rather than inherited**).

**3 — THE BETTER AXIS, ADOPTED: vary CARD-INFORMATIVENESS, not gap size.**

- **ENV-A: the card is substantially RIGHT.** Blanket distrust **loses**, so an effect can only come
  from **newcomer-specific information.**
- **ENV-B: the card is substantially WRONG.** Blanket distrust **wins**.

**A manager improving on BOTH used information about the newcomer. A manager improving only on B
distrusted a bad card.** That separates the confound directly, where a gap-size ladder separates
power from effect — **and the power question's answer is already "we cannot tell", because both
floors are zero.**

**RR's decisive line, adopted: if only one axis is affordable, spend it here — a POWER statement can
be recovered later by running more episodes; a CONFOUND cannot be recovered at all.**

**4 — ADMISSION AS POST-CONDITION: ENDORSED by RR as a strict improvement, with one condition.**
**It must be able to FAIL.** An assertion over a construction that guarantees its own premises is
**the structurally-zero residual again.** **Six properties, six demonstrated failing fixtures** —
cheap, because we control the construction.

**LS's OPEN QUESTION back to the team: can the card-informativeness axis be spanned WITHIN partial
overlap by varying the mix, rather than by switching ENV-B to the disjoint arrangement we retired on
realism grounds?** If yes, both environments keep their realism. **If no, ENV-B is a DECLARED
DIAGNOSTIC rather than a setting**, and its results speak about manager policy rather than about a
realistic succession — which must be stated wherever they appear.

### 2026-08-09 — ★ THE CONSTRAINT IS SATISFIABLE. Realistic AND consequential, with Basel untouched

Records: `records/L10/` (RR, two sweeps; RE, contested-share pricing).

**1 — THE ANSWER. Contested share, arrangement held at `partial`, 20 seeds per cell:**

    force on   irb_frac   card − ignorant   ceiling
    lied           0.44           +0.4725     1.84%
    lied           1.00           +1.0259     1.51%
    shared         0.44           +0.4050     1.20%
    shared         0.67           +0.5569     2.32%
    shared         0.89           +0.6603     3.50%
    shared         1.00           +0.6998     4.22%

**★ THE SHARED-FORCED ROW IS EXACTLY WHAT THE CONSTRAINT NEEDS: GAP AND CARD VALUE RISE TOGETHER.**
Ceiling **1.20% → 4.22% (3.5×)** while card−ignorant goes **+0.41 → +0.70 (1.7×)**. **That breaks
the arrangement-level coupling**, and for the reason LS gave: **the coupling is an ARRANGEMENT
property and contested share is a MIX lever.** LS's decomposition — `gap = structure × per-segment
cost` — is vindicated; **only the prediction hung on it missed. LS predicted card−ignorant roughly
FLAT; it RISES steeply, in both forcing directions. Wrong in the direction that helps.**

**ADOPTED CELL: shared-forced at `irb_applicable_fraction ≈ 0.89` — ceiling 3.50%, card−ignorant
+0.66. Basel untouched, no rating selection, arrangement unchanged.** **1.00 is rejected on two
counts:** every exposure being IRB-approved is at the edge of plausible (**real banks run partial
use, with portfolios permanently on SA**), and **generation starts failing there — 17–18 of 20 seeds
against 20/20 below.** **0.89 is the last defensible cell.**

**AND IT MOVES AFFORDABILITY:** 3.50% against the only σ we have (0.0768) is d ≈ 0.46 → ~75/arm,
against ~185/arm at the median random draw. **Still not a sizing claim — that σ is pre-repair.**

**2 — THE RATING-DIVERGENCE LEVER IS NOT NEEDED, which sidesteps LS's own worry rather than
adjudicating it.** RR's answer for the record: **a scoring-rule change applies to everything and
leaves Basel; rating composition selects a portfolio and does not** — **but they converge at the
extreme**, and the separating criterion is **whether the resulting rating distribution resembles a
book someone could hold.** Also **nearly exhausted**: divergence selection as implemented buys
1.13×, and going further means selecting a tail running 0.002–0.754 per segment, **which is where
"designed book" stops being a figure of speech.** Small headroom, high cost, not required.
**Divergence selection stays OFF; only the count forcing, targeted at the shared class, is needed.**

**3 — ★ TWO PROBLEMS, AND THEY MUST NOT BE COLLAPSED.** The researcher's constraint
(*realistic AND consequential*) and the ENV-A/ENV-B contrast (*used newcomer-specific information vs
distrusted a bad card*) **are different problems, and contested share solves only the first.**
**It raises BOTH arms together — it does not separate them.** A matched-gap pair differing in
card-informativeness is **narrower than before**: `shared@0.89` (3.50%, +0.66) against `lied@2`
(3.63%, +0.61) is a span of **0.05**, against 0.14 previously.
**So: the environments CAN be realistic and consequential — settled. What they still CANNOT do is
cleanly separate the two manager policies at matched gap. The first is a design decision; the second
is a STANDING LIMITATION, and the good news about the first must not read as progress on it.**

**4 — LS RULING: THE ENV-A/ENV-B CONTRAST IS DEFERRED, NOT SOLVED, AND THE TWO ENVIRONMENTS BECOME
TWO CONSEQUENTIAL INSTANCES RATHER THAN A CONTRAST.**
**The contrast exists to separate two explanations for an effect. We have not established there IS
an effect.** Separating explanations before establishing the phenomenon is the wrong order — and the
separation is measured at a span of 0.05, which would not carry a verdict even if the phenomenon
were established. **Two realistic, consequential instances, differing enough that a finding on both
is not instance-specific. If something moves, the confound question becomes live and needs a design
that can separate — which RR has shown is hard and is not this one.**

**5 — PRE-COMMITMENT, requested by RR and ADOPTED: if the effect turns out undetectable at these
settings, that is a FINDING and NOT a reason to widen anything.** Widening reintroduces the
confound and the resulting number would answer a question we already know we cannot answer.
**Deciding it now costs nothing; deciding it after seeing a null costs the result.**

**6 — CONTESTED SHARE: RE AND RR MEASURED ADJACENT QUANTITIES AND ONLY ONE IS THE LEVER.**
**RE priced the OUTCOME across arrangements** — contested count lands at 52–62% everywhere and does
**not** track the ceiling (`disjoint` has the LOWEST share and the HIGHEST ceiling; `partial`@segs=4
the HIGHEST share and a ceiling of ZERO), concluding it *"may not be freely settable"*.
**RR priced the KNOB within one arrangement** — `irb_applicable_fraction` — and it moves the
ceiling 3.5×. **Both correct, different questions: the share is arrangement-invariant and
mix-settable.** RE's within-partial figure (4→5 contested, +58% mean ceiling, r = 0.25) is the same
lever seen through the outcome, which is why it looked second-order.
**RE's own flag, and it was the right one: they priced the lever proposed, not the mechanism behind
it.**

**7 — A NEAR-ESCALATION AVOIDED (RE): repeated 401s during the run are `[non-fatal]` TRACING uploads**
— the SDK posting telemetry to OpenAI with an OpenRouter key, because `.env` sets `OPENAI_API_KEY`
to the same `sk-or-v1` value. **Not the inference path; nothing billed.** Tracing disabled for the
run. **An alarming signal that said "non-fatal" on its face, nearly escalated.**

### 2026-08-09 — the three amplifiers are separated; two bugs found in the separating; one open question

- **`amplify_count`, `amplify_divergence`, `amplify_irb_priority` are now independent switches**, each
  recorded in the manifest, **verified separable on a paired population across all eight settings —
  30/30 survive every one**, so comparisons are on one population.
- **★ BUG 1 WAS IN THE FIX ITSELF: a mix change produced by turning an amplifier OFF.** Gating only
  the `+=` left `others = [c for c in classes if c != shared_class]` in force, so with
  `amplify_count=False` **the shared class received ZERO segments instead of its round-robin share**
  (max class count 3.00 over four classes, where plain round-robin over five gives 2.00).
  **The kind of half-fix that looks complete because the flag is honoured somewhere.**
- **★ BUG 2 WOULD HAVE WRECKED THE SWEEP: the divergence search draws from the MAIN rng and consumes
  a VARIABLE number of draws** (it breaks early on the first non-clipping candidate). **So toggling
  `amplify_divergence` silently moved the calibration, the EADs and the segment mix as well as the
  ratings — varying divergence varied the INSTANCE.** Precisely the confound the switch was
  separated out to remove. Fixed with its own stream; the main stream now advances by exactly one
  rating draw either way. **The rng-alignment fault a THIRD time this phase, same shape, one level
  down from the lattice path.**
- **RE's TWO WRONG DIAGNOSES BEFORE THE RIGHT ONE, and checking before saying so:** the 3.00-vs-2.00
  gap first read as **survivorship** (different seeds failing under different settings) — **checked,
  population identical 30/30 everywhere, so it was bug 1.** **Both killed by measuring rather than
  reasoning.**
- **★ OPEN AND BLOCKING: WAS RR's `irb_applicable_fraction` SWEEP RUN BEFORE THE STREAM FIX?**
  **Their sweep forced the mix, so `shared_class` was set, so ALL THREE amplifiers were on including
  divergence.** If it predates the fix, **varying `irb_frac` changed how many candidates the
  divergence search examined, moving calibration and EADs downstream — so the measured ceilings are
  correct for the instances generated, but the TREND across `irb_frac` may be partly incidental
  instance variation rather than the lever.**
  **The adopted cell (shared-forced at 0.89, ceiling 3.50%, card−ignorant +0.66) is what the two
  environments would be built on, so CONSTRUCTION IS BLOCKED ON RE-VERIFICATION rather than on the
  sweep itself.** Cheap to redo; **redo beats build-on.**
  **Put to RR in differ-test form: what would have had to be true for the pre-fix and post-fix
  sweeps to differ?** If the divergence search's early break is insensitive to how many segments are
  IRB-applicable, it is clean — **and that should be STATED rather than assumed, because from
  outside it looks like it might be sensitive.**
- **★ A NAMING PROBLEM THE VERIFICATION EXPOSED: EVERY "AMPLIFIER" REDUCES THE PARTIAL CEILING**, and
  all-off is the best configuration at `segs=4` (1.88% off, down to 0.00–0.13% with count on).
  Consistent with the saturation mechanism. **A switch called `amplify_count` that lowers what it
  names is an identifier asserting the opposite of what it does** — the provenance rule applied to a
  variable name, and **the second inherited-vocabulary problem this week after "lattice".** They are
  amplifiers for the arrangement we abandoned and **dampeners for the one we adopted.**
- **LS's COMMITTED PREDICTION ON DIVERGENCE — neither claimed nor dismissed.** Predicted: divergence
  raises both the gap and card−ignorant. **One datapoint against it (1.88% → 1.75%), at `segs=4`, the
  SATURATED regime where the covered-lie channel is dead — not at the `segs=1` operating point.**
  **Untested where it matters, contradicted where it doesn't, and about a lever the adopted setting
  turns OFF. Marked unresolved rather than dropped.** RE's instruction to the sweep is adopted:
  **treat divergence as a SIGNED lever rather than assuming a sign.**

### 2026-08-09 — ★ CORRECTION: the adopted cell's figures were 7–14% high. Decision survives; numbers don't

Record: `records/L10/` with **`contested_share_sweep.py` committed alongside** — every number below
re-runs.

    irb_frac    ceiling    card − ignorant       previously published
        0.44    1.1779%            +0.3930       1.20%  /  +0.4050
        0.67    2.1265%            +0.5189       2.32%  /  +0.5569
        0.89    3.0574%            +0.6169       3.50%  /  +0.6603

**THE ADOPTED CELL IS 3.06%, NOT 3.50%.** **The conclusion is unchanged**: ceiling rises **2.60×**
across the sweep while `card − ignorant` rises **1.57×** with it, **so shared-forcing still satisfies
"realistic AND consequential" and 0.89 is still the cell.** Affordability moves from ~75/arm to
**~100/arm** against the pre-repair σ — **still well below the ~185/arm of a median random draw, and
still not a sizing claim.**

**RULED OUT by RR:** hash-seed dependence (identical across four `PYTHONHASHSEED` values); the
Monte-Carlo interleave (in-process, with and without, bit-identical); explicit
`irb_applicable_fraction=0.67` vs the default (identical 20/20); differing surviving-seed sets
(n=20 in both runs at the affected cells).
**NOT IDENTIFIED: what differed between the earlier scripts and the later ones.** Each is
individually deterministic and reproducible; **they disagree with each other.** One suggestive
detail, **flagged by RR as a coincidence and not a diagnosis:** 2.32% is very close to seed 0's
individual value, 2.3124%, which would fit an aggregation error — **not asserted, and nothing left
to check.**

- **★ AND THE REASON NOTHING IS LEFT TO CHECK IS THE DEFECT RR THEMSELVES FOUND AND ANNOTATED HOURS
  EARLIER: the earlier scripts were UNCOMMITTED INLINE ONE-OFFS.** Same shape as
  `step4_audit_RR.md` citing a script that was never committed. **They wrote the rule, annotated
  their own violation of it, then produced three more uncommitted one-offs and published a
  recommendation from them the same day.**
- **★ LS's SHARE, AND IT IS THE RECIPIENT-SIDE RULE FAILING ON THE PERSON WHO ADOPTED IT: I took
  3.50% into a decision record within minutes because it arrived as a MEASUREMENT.** That is exactly
  the mechanism identified this morning — *a number without its construction, adopted because it
  supported a conclusion already held* — **with RR as the source this time and me as the adopter.
  I did not ask the one question.**
- **NEW STANDING RULE, on RR's request and adopted: A FIGURE ENTERS A DECISION RECORD ONLY WITH A
  COMMITTED SCRIPT BEHIND IT.** Partly mechanical already — **`check_record_citations.py` resolves
  `.py` references, so a decision record citing its script is checkable; a decision record citing no
  script is the gap.**
- **★ WHAT THIS DOES AND DOES NOT TOUCH IN THE PRIOR RULINGS.** The **0.05 matched-gap span** and the
  **3.5× ratio** came from the same uncommitted runs. **The 2.60× is now verified; the 0.05 span is
  NOT, and RR is re-deriving it.**
  **The deferral of the ENV-A/ENV-B contrast STANDS, because it rested on two legs and only one was
  numeric:** *(a)* the span is too narrow to carry a verdict — **now unverified**; *(b)* the contrast
  separates two explanations for an effect **we have not established exists**, and separating
  explanations before establishing the phenomenon is the wrong order — **independent of any number.**
  **Leg (b) carries it. Leg (a) is marked unverified rather than quietly retained.**

### 2026-08-09 — the units disagreement dissolves; the naming rename is REFUSED and rightly; one re-measurement blocks the build

- **★ THE `card − ignorant` "DISAGREEMENT" WAS PURE UNITS, and the CEILING agreement is what proves
  it.** Same instances: **+0.0727 as a share of oracle** (RE) against **+0.6131 absolute** (RR's
  +0.6169), mean oracle 8.4386, share × oracle = **+0.6138.** **RR's corrected ceiling 3.0574% and
  RE's independent 3.06% on the fixed stream agree to three significant figures — so the INSTANCES
  match, and the 9× could only ever have been the formula.**
  **★ THIS SETTLES LS's CONTAMINATION QUESTION INDEPENDENTLY OF RR's ACCOUNT: two paths, same
  number.** Construction unblocks on that rather than on trust.
- **THE UNEXPLAINED EARLIER-VS-LATER DIFFERENCE STAYS UNEXPLAINED, deliberately.** Hash seeding, the
  Monte-Carlo interleave, explicit-vs-default parameters and differing seed sets all ruled out; the
  earlier scripts were uncommitted with nothing left to re-run. **An unreproducible difference
  between a committed script and a deleted one is not a finding, and the standing rule is the right
  response rather than more archaeology.**
- **★ RE REFUSED THE RENAME LS ASKED FOR, AND THE REFUSAL IS THE STRONGER ARGUMENT.**
  `amplify_*` appears in **committed records, manifests and RR's sweep script**, so renaming would
  **silently break the join between a bundle and the figures derived from it.** *Churning identifiers
  to fix a docstring problem trades a READING error for a PROVENANCE error* — **the exact fault this
  phase has spent itself removing, which LS proposed re-introducing.**
  **The correction is stated where a reader meets the parameter instead, and it is more useful than
  a rename:** `amplify_count` **dampens on `partial`** (the channel needs nA < cap) and is **the only
  thing that creates a channel at all on `current`** (needs nA ≥ cap); `amplify_divergence` has a
  small ceiling effect but is **LOAD-BEARING FOR GENERATION** at high `irb_applicable_fraction`;
  `amplify_irb_priority` approves the amplified class's segments first.
  **The direction of every one is ARRANGEMENT-DEPENDENT. None is an amplifier simpliciter.**
- **★ BLOCKING THE BUILD: RR's 0.89 FIGURES WERE MEASURED WITH `amplify_divergence` ON, AND LS
  SPECIFIED THE BUILD WITH IT OFF.** **The figure that justified the cell was not measured in the
  configuration we would build** — the construction-path rule at the level of a switch, **third time
  this phase a number and its intended use differed in a setting.**
  **RULING: RE-MEASURE, DO NOT ASSUME.** Re-run the adopted cell with `amplify_divergence=False` at
  `segs=1`, where it generates 20/20. **If the ceiling holds near 3.06%, build divergence-off as
  specified and the realism argument costs nothing. If it drops materially, the choice is between
  leaving ratings unselected and the size of the gap — a RESEARCHER-level trade, brought with both
  numbers rather than decided by the team.**
- **AND INTO THE L10 SPEC VERBATIM, because it would otherwise be lost: "divergence off at 0.89" is
  TRUE OF THE CELL and FALSE OF THE PARAMETER COMBINATION IN GENERAL.** At the default segment count
  it does not generate at all — *"only 6 of 9 segments have a non-zero SA fallback, but 8
  IRB-approved segments were requested."* **A setting that reads as independent of the segment count
  and is not.**
- **RUN: in flight, 13 minutes, I/O-bound, no bundles yet. Nothing on σ.**

### 2026-08-09 — divergence-off is FREE; the "unexplainable" discrepancy WAS the stream bug

- **★ RE-MEASURED IN THE BUILD CONFIGURATION, and the branch LS was preparing for does not arise:**

      partial, segs=1, irb_frac=0.89     gen     ceiling   card−ignorant (share)
        amplify_divergence = True       40/40     3.15%          +0.0785
        amplify_divergence = False      40/40     3.21%          +0.0810

  **Both quantities move UP with divergence OFF** (+1.8% ceiling, +3.2% card−ignorant), and RR
  reached 3.17% independently at 20 seeds. **Two paths again. BUILD DIVERGENCE-OFF; the realism
  argument is FREE, and there is no researcher-level trade to bring.**
  **The constraint is now met in the configuration that will ACTUALLY BE BUILT** — which was not
  true an hour ago, when the figure justifying the cell had been measured with the switch in the
  other position.
- **★ AND THE DISCREPANCY BOTH RE AND LS SAID SHOULD STAY UNEXPLAINED WAS A LIVE GENERATOR DEFECT.**
  RR's earlier contested-share figures failed to reproduce; they had ruled out hash seeds, the MC
  interleave, explicit-vs-default kwargs and the seed set. **Cause: the divergence search consumes a
  VARIABLE number of MAIN-stream draws. Their sweep varied `irb_frac` with `shared_class` set, so all
  three amplifiers were on, so changing `irb_frac` changed how many candidates the search examined,
  which moved the calibration and the EADs. Same seed, different instance, before and after the
  fix.**
  **BOTH RE AND LS WITHDRAW THE ADVICE TO CLOSE IT.** LS wrote *"an unreproducible difference between
  a committed script and a deleted one is not a finding"* and agreed archaeology was the wrong
  response. **We would both have closed a live defect as unresolvable. The rule is still right; the
  application was premature.**
- **★ THE GENERALISATION, AND IT IS THE MOST REUSABLE THING HERE. RR DID NOT RE-RUN ANYTHING — they
  asked WHAT WOULD HAVE HAD TO BE TRUE FOR THE TWO TO DIFFER** (the draw count would have to depend
  on `irb_frac`) **and it does.**
  **The differ-test was written to interrogate AGREEMENT: before treating two matching results as
  evidence, name what would have made them differ. This applies it to DISAGREEMENT: before treating
  two conflicting results as unresolvable, name what would have made them differ.** Same question,
  opposite starting point — **and "nothing left to re-run" does not mean "nothing left to reason
  about."** **Goes into the rule as its second face.**
- **GENERABILITY IS NOT MONOTONE IN SEGMENT COUNT, correcting RE's own summary:**

      segs=1  div=True 20/20   div=False 20/20
      segs=2  div=True 20/20   div=False 20/20
      segs=3  div=True 18/20   div=False 16/20   <- WORST
      segs=4  div=True 20/20   div=False 19/20

  **It fails in a BAND, not at the top.** *"Generation fails at high segment count"* reads as
  monotone and is wrong. **The L10 line is strengthened rather than weakened: the setting is not
  independent of the segment count, AND THE DEPENDENCE IS NOT EVEN ORDERED.** The adopted cell sits
  outside the band at 20/20 either way.
- **NAMING — LS RULES FOR RE. RR argued to rename "while nothing depends on the names yet"; that
  premise is FALSE.** `check_amplifier_dependence`, **every manifest written since `6ac6ba7`**, and
  **RR's own committed sweep script** all depend on them. **Renaming now breaks a join that already
  exists.**
  **Addition: if we ever rename, L10's BUILD is the moment** — the parameters are being rebuilt
  there anyway, so **the join can be broken DELIBERATELY, with everything migrated in the same
  commit, rather than incidentally.** Until then the per-parameter statement carries it.
- **RUN: 17 minutes, I/O-bound, 24 sockets, no episode finished. THRESHOLD SET rather than left to
  drift: if nothing has landed by ~45 minutes, STOP AND DIAGNOSE.** 22 timesteps at 6 parallel on
  flash should not take that long, and *"still going"* is the state that quietly becomes an hour.
  **First question if it stalls: model path or assembly path — the split that has decided every
  other failure this week.**

### 2026-08-09 — the CRON PROMPT had gone stale and was directing firings at a superseded design

- **★ A CRON PROMPT IS A STEP MARKER NOBODY RE-READS — and worse than the two stale `[~]` markers
  this phase, because it INSTRUCTS rather than merely describes.** `9187b13e` still directed each
  firing at the **ENV-A maximum-gap / ENV-B realistic-gap ladder**, which was **superseded on RR's
  measured evidence within hours of the cron being written.** A future firing would have worked
  toward a design retired for ranking manager policies.
- **Cancelled and replaced by `589bad18`**, carrying: the **settled build setting** (partial /
  count ON at the shared class / divergence OFF / `irb_frac` 0.89 / `segs` 1 → ceiling 3.21%, two
  paths agreeing, 40/40); an explicit **DO NOT BUILD THE LADDER** with the reason; the **two
  environments as consequential instances rather than a contrast**; the **five-bucket split
  mapping**; the **45-minute run threshold**; and **both faces of the differ-test** plus the
  **committed-script rule.**
- **RULE THAT FOLLOWS, into `RESEARCH-CRON-STATUS.md` §7: when a ruling changes what the topmost
  step IS, the cron prompt is part of what has to change. It is not a set-and-forget artefact.**
- **AND A METHOD NOTE ON THE EDIT ITSELF, because it is the same failure a third time:** the first
  attempt at amending L10 used **exact-string matching for the header, matched NOTHING, and the
  script reported success for the half that landed.** Redone by **line index** and **verified by
  printing the lines back.** *Third partial-edit-reporting-success this week; the fix each time was
  re-reading the file rather than trusting the script's own report.*
- **STATE: no peer commits and no bundles since the previous firing. The run is in flight.**

### 2026-08-09 — ★ THE RUN WAS HUNG, NOT SLOW. The harness has no timeout anywhere

**Stopped at 20:47 with ZERO episodes. Diagnosed to the MODEL path. Zero model spend — nothing
reached completion, and the earlier 401s were the non-fatal tracing path.**

    elapsed 20:47   CPU 00:00:25   sockets 14, all ESTABLISHED
    main thread     ep_poll (asyncio loop idle)
    worker threads  futex_do_wait
    rchar delta over 60s   899 bytes   <- ~15 B/s, not a working LLM stream
    bundles                0

- **ASSEMBLY SUCCEEDED — episodes started, 14 connections established. The hang is in the MODEL
  PATH:** requests sent, connections open, nothing coming back, event loop idle indefinitely.
- **★ THE HARNESS DEFECT: THERE IS NO TIMEOUT ANYWHERE IN THE CHAIN.** `Runner.run(...)` at
  `ai_agent.py:281` has **no `wait_for`**, no client timeout, and `model_provider` sets **none** on
  the client. **A single unanswered upstream request blocks its episode indefinitely, and with
  `asyncio.gather` ONE HUNG EPISODE HOLDS THE WHOLE BATCH.**
  **A harness that cannot time out is not a harness anyone would ship** — which is the production
  test answering itself.
- **RE STOPPED AT 18 MINUTES RATHER THAN WAITING FOR LS's 45-MINUTE THRESHOLD, AND WAS RIGHT.**
  The state was diagnosable at 18; waiting would have bought a longer identical hang.
- **★ AND RE's GENERALISATION REPLACES LS's RULE: THE FIX IS NOT THE THRESHOLD BUT THE FIRST
  SAMPLE.** A threshold tells you when to give up **after** the time is spent; **one I/O-counter
  delta at three minutes tells you whether the thing is working at all, and costs nothing.**
  **ADOPTED: for any long-running operation, take an EARLY PROGRESS SAMPLE rather than set a
  deadline.**
- **AUTHORISED, in this order:** **(2) client-level HTTP timeout FIRST** — narrowest fix at the
  layer where the failure is — **and check the retry policy, because a timeout that triggers
  unbounded retry is not a timeout**; **(1) run-level `wait_for` as a generously-bounded backstop**,
  not because we have seen the failure it catches but because **one hung episode holding the batch
  is a fragility independent of cause**; **(3) the timeout RECORDED IN THE MANIFEST**, same
  reasoning as the arrangement — **a bundle should say what it was willing to wait for**;
  **(4) re-run ONE EPISODE, ONE SEED, SERIAL.**
  **CORE PATH ⇒ `CHANGED.md` entry in the same commit.**
- **RE's SEQUENCING SELF-CRITICISM, accepted: six in parallel as the first live thing on a brand-new
  arrangement is the same shape as trusting a control before showing it can fail.** A serial single
  **is** the positive control for the model path, and it would have cost three minutes.
- **★ SCOPE CLARIFICATION ON RR's 69% THAT THIS FORCES, and it is NARROWER than a contamination:
  the 69% is measured on bundles that COMPLETED, so it describes segments that did not complete
  WITHIN A COMPLETED EPISODE. A hang produces NO BUNDLE AT ALL, so hangs are INVISIBLE to that
  measurement rather than contaminating it.** **Two distinct failure modes; only one is in the
  corpus.** *"Non-completion" now names two things and must say which.*
- **WHAT IS NOT ESTABLISHED AND IS NOT ASSERTED: whether the upstream was rate-limiting, queueing or
  silently dropping.** 14 ESTABLISHED sockets with no bytes is consistent with all three and there
  is no server-side visibility. **The claim that survives is about US: the harness cannot
  distinguish them, and that is our defect whichever was happening.**
- **STEP 2 PRODUCED A FINDING, JUST NOT THE ONE IT WAS FOR. Every result this phase until now was
  offline arithmetic; this is the first thing only a live run could have found**, and it is a real
  defect in shipped code. **Nothing on σ and nothing on the five-bucket split — both need bundles.
  Step 2's purpose is unchanged and unmet.**

### 2026-08-09 — the timeout is built, the model path is ALIVE, and the root cause is a 100-minute default

- **★ THE EARLY-PROGRESS-SAMPLE RULE VALIDATED ITSELF 45 SECONDS INTO ITS FIRST USE:**

      serial episode, ~2 min in   rchar delta over 45s = 435,937 bytes
      the hung run                rchar delta over 60s =         899 bytes

  **~500× on the first counter you look at.** So the sample is not merely cheaper than a deadline —
  **it is UNAMBIGUOUS where a deadline is a judgement call.** *Measured, not reasoned.*
- **★ ROOT CAUSE: litellm's global `request_timeout` defaults to 6000 SECONDS — 100 MINUTES.** The
  run would have waited another eighty. **`Runner.run` drives `LitellmModel`, whose constructor
  takes only `(model, base_url, api_key)`, so the global is the only knob.**
- **★ AND THE PARALLEL PATH IS THE PATTERN, NAMED RATHER THAN COUNTED: `llm_interface` builds its own
  `AsyncOpenAI` at `timeout=300.0`, so the bound existed on ONE PATH AND NOT THE PARALLEL ONE. THE
  MANAGER/JUDGE PATH WAS NEVER AFFECTED.**
  **THIS CODEBASE HAS MULTIPLE PATHS THAT DO THE SAME JOB, AND CONFIGURATION APPLIED TO ONE IS NOT
  APPLIED TO THE OTHER** — the lattice parameter, the rng stream, and now the timeout.
  *(The amplifier bundling and the totality-repair gate are ADJACENT BUT DIFFERENT — over-coupling
  and provenance-gating. Kept distinct so the pattern stays diagnostic rather than becoming a
  catch-all.)*
  **MECHANICAL FORM WORTH BUILDING AFTER THE SERIAL EPISODE REPORTS: assert that every site
  constructing a model client sets an explicit timeout.** `check_path_alignment` does this for the
  generator's two paths; **the model layer has no equivalent, and a lint-shaped check would have
  caught this BEFORE a run rather than during one.**
- **BUILT IN THE AUTHORISED ORDER (committed):** client bound **`request_timeout=180`** with
  **`num_retries=2`** — *deferring to a provider SDK's unstated retry policy is not a policy*;
  **`asyncio.wait_for` at both `Runner.run` sites** raising `WorkerRunTimeout` at
  **630s = (180+30)×(2+1)**, sized so **a call that legitimately exhausts its retries finishes
  INSIDE the backstop, or the backstop would mask the retries it exists to outlive**; **both bounds
  in the manifest**; serial single running.
- **★ TWO SELF-INFLICTED BREAKAGES ON THE WAY, and the second carries the sharper lesson.** The first
  edit's search string matched the **function definition line** rather than the standalone call,
  truncating the body into a `SyntaxError`. The repair then left a **DUPLICATE DEFINITION** of the
  backstop constant and the exception. **Neither was caught by the code importing — the duplicate
  imported FINE.** **A `SyntaxError` announces itself; a duplicated definition is a GREEN SIGNAL.**
  Both were caught by **counting symbol definitions** — the artefact-not-the-log discipline arriving
  in a text edit. **Third partial-edit failure today (LS two, RE one).**
- **RE WITHDRAWS THE "SIBLING CONTAMINATION" SUGGESTION in favour of the narrower statement: hangs are
  INVISIBLE to the 69% rather than mixed into it**, because a hang produces no bundle. **Two failure
  modes; only the inner one is in the corpus.**
- **STILL NOTHING ON σ, AND A SINGLE EPISODE WILL NOT PROVIDE ONE — df = 0.** A single datapoint is a
  **feasibility verdict and nothing else**, and will be reported as that, with the five-bucket split
  on whatever bundle lands.

### 2026-08-09 — the SERIAL episode hung too, mid-stream. Step 2's verdict is "NOT YET"

    ~2 min in   435,937 bytes / 45s   <- working
    ~4 min in           0 bytes / 30s   <- stalled, MID-EPISODE
    elapsed 4:13, CPU 2s, no bundle

- **★ NOT LOAD-INDUCED, and that is worth more than the hang.** A **serial single** gets minutes of
  real traffic and then stops dead. **Six-parallel alone would have supported "too much for the
  provider"; the serial re-run rules it out.** **The re-run DISCRIMINATED A HYPOTHESIS rather than
  merely costing less** — the second reason serial-first was right sequencing, and LS only had the
  first.
- **AN UNPLANNED POSITIVE CONTROL FOR THE FIX JUST BUILT, and RE is waiting rather than killing it
  because killing it destroys the only test.** Bounded at 15 minutes. Three outcomes, each saying
  something different: **client bound fires → works, diagnosable failure; survives to 630s and
  `WorkerRunTimeout` fires → the client bound did not reach it and the backstop earned its place;
  passes 630s still hung → both bounds are ineffective and the fix is not a fix.**
- **★ THE DISTINCTION RECORDED BEFORE THE BOUND FIRES, because all three outcomes share it: THE FIX
  CONVERTS A HANG INTO A DIAGNOSABLE ERROR. IT DOES NOT MAKE THE PROVIDER ANSWER.** Outcomes 1 and 2
  both mean **the harness is sound and the run still produces no bundle.** **If the stall is
  reproducible there is a PROVIDER-PATH problem sitting behind the HARNESS problem just fixed** —
  a different question with a different fix (model choice, routing, or retry-and-continue rather
  than fail-the-episode). **Named now so a clean timeout does not read as a solved run.**
- **DISCRIMINATING OBSERVATION REQUESTED, nearly free: does the stall happen at a CONSISTENT POINT?**
  Same timestep / request index / payload shape across the two hangs → **request-specific and
  reproducible.** Scattered → **the provider.** Two datapoints is thin and it is what we have.
- **AND A CONSEQUENCE TO PRE-DECIDE: if the client bound fires and the EPISODE errors out, one
  stalled call costs the whole episode.** Correct for diagnosis, **wrong for a study** — a
  timed-out worker call should probably surface as a **refusal-shaped outcome the manager can see**,
  not an episode death. **Deferred to the five-bucket work, because it is exactly a SIXTH thing
  "non-completion" could mean.**
- **★ STEP 2's OUTPUT IS "NOT YET", CONFIRMED AS THE FORM.** A harness that stalls mid-episode on a
  serial single **cannot produce episodes to measure σ from.** **The feasibility verdict is the
  whole of step 2, and "not yet" is the honest version — not a number with a wide interval, and not
  a hedge.** **Consequence: the environments are NOT blocked on σ**, because there is no σ to wait
  for; they are blocked on the build, which is unblocked.
- **RE's TIGHTENING OF THE PARALLEL-PATH PATTERN, ADOPTED over LS's version. The distinguishing test:
  does the second path EXIST because someone needed different behaviour, or because it GREW?**
  Lattice, rng and timeout are all the second — **nobody decided workers should have no timeout** —
  **and that is exactly what makes them findable by an alignment check**, where over-coupling and
  provenance-gating are not.
- **AND THE CONDITION ON THE PROPOSED CHECK, already paid for: point it at a client with NO timeout
  and confirm it REPORTS, before trusting it to report none.** *Two of the three checks that passed
  while broken this week failed exactly that.*

### 2026-08-09 — the discriminating question was UNANSWERABLE BY CONSTRUCTION; instrument fixed, one merge refused

- **★ THE RUNNER PRINTED ONLY ON COMPLETION, so a stalled run and a slow run produced the IDENTICAL
  ARTEFACT: nothing.** No timestep, no request index, no payload shape — **for either hang.** LS's
  discriminating question (*does the stall land at a consistent point?*) **was unanswerable by
  construction, which is a defect in the INSTRUMENT rather than a gap in the DATA.**
  **Fixed rather than inferred: a per-timestep heartbeat in the timestep-end callback with
  `flush=True` — because A BUFFERED HEARTBEAT IS NOT A HEARTBEAT; the buffer is exactly what a hang
  fails to flush.** *"I would rather say I cannot answer that yet, and here is why, and it is fixed,
  than offer two datapoints of inference."*
- **INTERIM, and reported as consistent-with rather than proof:** elapsed 7:32, CPU 3s, 32 bytes/25s,
  **sockets 14 → 3.** Connections being torn down is what a firing client timeout looks like from
  outside. **RE explicitly refused to assert the mechanism from a socket count** — their own
  evidence, pointing the way they wanted, late in a long day. **The discipline holding under the
  conditions that erode it.**
- **★ ONE MERGE REFUSED (LS). RE proposed that a timed-out worker call may belong in
  `refused_unavailable` rather than needing a sixth state — "a worker that never answers is a worker
  that is unavailable."**
  **They share an OBSERVABLE and not a CAUSE.** `refused_unavailable` is produced by **a roster
  change — the MANIPULATION.** A timeout is produced by **a worker that IS on the roster and does
  not answer — INFRASTRUCTURE.** **Merging them puts infrastructure failures into the one state the
  corrected mapping protects as the manipulation's own signature** — *precisely the pooling error RR
  corrected in LS this morning, one bucket over.* **Fewer states is usually better; here it destroys
  the state we were most careful about.**
  **A timeout belongs on the DEFECT or budget/horizon side — not the DV, and emphatically not the
  MANIPULATION — and it wants its own marker for a reason beyond taxonomy: a bundle in which a
  worker timed out has the manipulation and an infrastructure failure CONFOUNDED for that segment,
  and we must be able to find and exclude those bundles.** If timeouts are frequent that is a
  **usability question about the corpus**, not a labelling one.
  **Settled with the five-bucket work, but BEFORE any bundle carrying a timeout is analysed — the
  pre-commitment argument, which is what saved the split this morning.**
- **CONFIRMED: *"the harness now fails correctly"* is the right sentence for outcomes 1 and 2 — NOT
  progress toward σ. Step 2's verdict stays "NOT YET", unsoftened. The environments are unblocked on
  the build.**

### 2026-08-09 — OUTCOME 3: neither bound fired. The bounds were correct code in the wrong place

- **★ A PROOF, NOT AN OBSERVATION: the serial episode ran 20+ minutes past a 630s backstop and a
  180s client bound and NEITHER FIRED. If the hang were inside the wrapped `Runner.run`,
  `asyncio.wait_for` WOULD have fired at 630s. It did not. So the hang is NOT THERE.**
  **A bound that fires tells you where you already looked; a bound that does not tells you where it
  is not.**
- **RE INFERRED "the hang is in the model path" FROM ESTABLISHED SOCKETS AND AN IDLE EVENT LOOP, AND
  BUILT BOUNDS ON THE INFERENCE.** The socket evidence was **consistent with** the model path and
  did not **establish** it. **The same wrong-path failure found five times this phase, this time
  committed rather than found.**
  **One thing in their favour they did not claim: they made that inference EARLY and then REFUSED
  THE SAME INFERENCE LATER** — *"I am not going to assert the mechanism from a socket count after
  spending the day arguing against exactly that."* **The discipline arrived between the two, same
  day, same evidence type. A sequence, not a lapse repeated.**
- **State at 20:27:** loop idle in `ep_poll`, three threads in `futex_do_wait`, **four ESTABLISHED
  TLS connections to OpenRouter behind Cloudflare**, 48 bytes in 20 seconds.
- **★ "UNANSWERABLE BY CONSTRUCTION" TWICE IN ONE DAY — the missing heartbeat, then the blocked
  stack** (`ptrace_scope=1` blocks `py-spy`, and **RE declined to escalate privileges to read a
  stack**). **Both times the first move was to make the question answerable rather than infer an
  answer, and both times the instrument was cheap.**
  **GENERALISATION: when a diagnostic question cannot be answered, BUILD THE INSTRUMENT BEFORE YOU
  BUILD THE HYPOTHESIS.** `faulthandler.dump_traceback_later(repeat=True)` needs **no privileges**
  where `py-spy` needs `ptrace` — worth remembering rather than rediscovering.
- **TWO INSTRUMENTS ADDED, both controlled before use:** the **flushed per-timestep heartbeat**,
  verified live (`[t00]..[t12]` with running counts); and the **traceback dumper**, positive-control
  led — pointed at a deliberate 3s hang with a 1s timer, **it fires and names the hanging frame.**
- **THE TIMEOUT WORK IS NOT REVERTED, correctly: 6000 seconds is still wrong, the manager/worker
  asymmetry is still real, and a bound that never fires costs nothing.** **A real fix for a real
  defect that is not this one** — and calling it the fix would have been the *"a clean timeout reads
  as a solved run"* error, which **it did not even get to commit, since it never fired.**
- **AUTHORISED — ONE MORE ATTEMPT, and it is a DIFFERENT THING because it now produces EVIDENCE
  rather than an OUTCOME. BOUNDED AT 10 MINUTES, not 20** — with the heartbeat and the dumper the
  stall point should appear within ~5, and **the extra ten minutes buys nothing now that the
  instruments report.**
  **THEN, IF THE STACK POINTS INTO THE SDK OR THE SOCKET: a minimal loop OUTSIDE the harness — N
  sequential calls, same model and endpoint, same client construction, no workflow.** Discriminates
  **provider-stalls-after-K-requests** from **our-harness-stalls**, far cheaper than another episode.
  **A single call would tell us nothing — the hang arrives MID-STREAM after real traffic, so it has
  to be a sequence.**
- **RE ACCEPTS THE SIXTH-BUCKET CORRECTION IN FULL, and the framing worth keeping is theirs: they
  argued for FEWER STATES and would have destroyed the one we were most careful about.** Recorded as
  a near-miss rather than only as a correction.
- **STEP 2's "NOT YET" IS FIRMER AND BETTER EVIDENCED: three live attempts, ZERO bundles, two
  distinct stall events, and NO WORKING HYPOTHESIS for where the stall is.** **A stronger statement
  than a wide interval, and the honest one.**

### 2026-08-09 — THE FIRST STACK: both threads idle, so the hang is below our code

    Thread 1 (pool worker)  concurrent/futures/thread.py:90 in _worker   <- waiting for work
    Thread 2 (main)         selectors.py:452 in select
                            asyncio/base_events.py:2023 in _run_once
                            asyncio/base_events.py:683 in run_forever

- **NO COROUTINE EXECUTING, NO BLOCKING CALL, NO SPIN, NO DEADLOCK IN OUR CODE.** The loop sits in
  `select()` awaiting socket readiness; the pool worker is parked. **Both of our layers are ruled
  out — which nothing before this could do.**
- **★ BUT THE STACK'S CONTRIBUTION IS A NEGATIVE, AND READING IT AS MORE IS THE TRAP IT INVITES.**
  *"Main thread idle in `select()`"* is **what a healthy async program looks like at ANY moment it
  is awaiting I/O** — it would look identical at 5 seconds. **The stack proves NOT-OUR-CODE; it does
  not prove STALLED.** **The stall evidence is the BYTE COUNTERS** (48 bytes in 20 seconds on the
  previous run). **Two instruments, one negative and one positive, neither sufficient alone.**
- **SAME CAUTION ON THE CONSISTENCY DATUM: zero heartbeats at 90s is consistent with a stall AND
  with a slow first timestep**, since timestep 0 carries several calls. **The n=2 "not at the same
  point" reading is the weakest evidence we hold** — taken as *pointing away from request-specific*,
  **not as establishing the provider.** **It motivates the discriminator; it does not substitute for
  it.**
- **THE OUT-OF-HARNESS DISCRIMINATOR IS BUILT AND HELD until the bound lands** — same model,
  endpoint and client; **no workflow, no engine, no agents SDK**; `litellm.acompletion` in a
  sequential loop of 12, each call timed and flushed, `request_timeout=60`, **`num_retries=0` so a
  stall shows as a stall rather than being papered over**, own dumper armed at 90s, **and not run
  concurrently with the episode so the two cannot confound on the same endpoint.**
  **Three readings:** all 12 succeed → **the provider is fine in isolation and the stall needs the
  harness's traffic pattern**; succeeds then stalls at K → **the provider stalls after K sequential
  requests and our harness is not the cause**; stalls immediately → **something about this endpoint
  or credential right now.**
- **★ A FORK PRE-DECIDED, because one branch is NOT the team's: if the reading is "provider stalls
  after K", the remedy is a different model or routing — and THE MODEL IS PINNED BY THE RESEARCHER
  (`deepseek-v4-flash-0731`, all roles). That is their call**, brought with the discriminator's
  output rather than after a fourth failed episode. **If the reading is "fine in isolation", the
  harness's traffic pattern is implicated and that IS ours** — concurrency, tool calls, prompt
  length — **and it is characterisable.**
- **★ THE ADMISSION REFRAME, sharpened: ADMISSION CHECKS INSTANCE QUALITY, NOT DESIGN QUALITY — and
  it was being used as though it did both.** Its three conditions are real and worth keeping
  (determinism, interior spread, a scripted baseline below oracle), **and none is RELATIONAL in the
  way property 3 is.** So it can tell **a good instance of a design from a bad one** and **cannot
  tell a good design from a bad one.** *"Discards 25 of 40 for structural reasons"* is therefore
  **the right filter doing its own job** — **but it was never the filter that would have caught
  `current`, and it was treated as if it were.** Chase later.

### 2026-08-09 — ★ RETRACTION: THERE WAS NO HANG. A healthy episode takes 43 minutes, and our own 180s timeout would have broken 13 of the 18 runs we already hold

**Every entry above from "THE RUN WAS HUNG, NOT SLOW" onward is diagnosing a condition that does
not exist.** They stay in the record. RE retracted independently from a heartbeat reading
`+3 this step` (`records/L11/pace_finding.md`); the corpus version is
`records/L10/episode_baseline_v1.md` with **`measure_episode_baseline.py` committed alongside** —
reads committed bundles only, spends nothing, and every number below is its stdout.

    median episode      42.8 min   mean 43.3   max 83.0   -> 118 s per timestep at horizon 22
    the three "hangs"   killed at 18, 20 and 10 minutes   -> 23-46% of a median episode

**All 18 bundles are `deepseek-v4-flash-0731` both roles, horizon 22 — same shape as the runs we
killed, so the baseline transfers with no caveat.** All 18 ran the full 22 timesteps.

**EVERY OBSERVATION WE READ AS EVIDENCE OF A STALL IS INSIDE THE NORMAL RANGE OF AN EPISODE THAT
SUCCEEDED.**

| what we saw | what it is |
|---|---|
| `[t00] completed=0` past 180 s | **normal — 18/18 healthy episodes complete no task in timestep 0**; first task lands at median 1.1 min |
| 48 bytes in 20 s, "the positive stall evidence" | **normal** — silence between logged events in a *successful* episode: p99 197 s, **max 715 s** |
| no bundle after 10–20 min | **normal** — the episode was a quarter to a half done |
| the backstop never firing (OUTCOME 3) | **consistent with CORRECT placement.** No wrapped call exceeded 630 s while the episode took an hour. It is not evidence the bounds were in the wrong place, and RE's self-criticism there was itself wrong. |

**★ AND THE INSTRUMENT WOULD HAVE MANUFACTURED THE CONDITION IT WAS HUNTING.** Of 394 model calls
that SUCCEEDED in the committed corpus (median 40 s, p99 636 s, **max 876 s**):

    litellm.request_timeout = 180 s   kills 28/394 (7.1%), landing in 13 of 18 episodes
    WORKER_RUN_BACKSTOP_S   = 630 s   kills  4/394
    measured alternatives:  900 s kills 0/394 (+24 s over max);  1200 s kills 0/394 (+324 s)

The 715 s silence is a **single** `structured_llm_request -> structured_llm_response` pair in
`run_cell0_seed3.json` — an 11.9-minute call that returned and is in our committed results. With
`num_retries=2` behind a 180 s bound, one such call burns 3x180 s and then fails. **"A bound that
never fires costs nothing" is false: this one sits inside the workload, not above it.**

**BLOCKS THE NEXT RUN.** One episode on `partial`, unattended, is authorised — **after** the timeout
is raised. Budget from the corpus: **treat nothing as wrong before 2.5 hours**, and kill on
**heartbeat silence > 1200 s** (clears the 715 s healthy max), never on elapsed time — only progress
distinguishes slow from stopped, and a wall clock cannot. The out-of-harness probe is **retired**:
its question ("is ~180 s/timestep normal?") is answered by the corpus at 118 s mean, 226 s max.

**WHAT SURVIVES.** litellm's 6000 s default is still a real divergence from `llm_interface`'s 300.
The heartbeat is what made this check interpretable and is the correct kill signal going forward.
**The threshold was wrong, not the instrument.**

**RESPONSIBILITY IS SHARED AND SPECIFIC.** LS's 45-minute threshold sat just above the median and was
roughly right; **LS then endorsed tightening it to 10 minutes**, which is what made run three
uninterpretable. LS's first pass at this check keyed "time to first completion" on any event type
containing `complet`, which matches `timestep_completed` — a boundary that fires whether or not
anything completed; it measured the wrong object and would have answered RE's open `t00` question
with a number about something else. Corrected in the script with the reason in place.

**★ THE RULE THIS PAYS FOR — "state a number's construction before building on it" APPLIES TO
THRESHOLDS IN CODE, NOT ONLY TO FIGURES IN RECORDS.** 180 and 630 were never derived from anything
and nobody asked where they came from. **Third instance this phase of a check built without first
establishing what normal looks like; second where the instrument would have produced the condition
it was looking for.** Without a baseline, *slow* and *stopped* are the same observation.

### 2026-08-09 — the retraction above was right and its NUMBER was wrong twice: wrong population, wrong pairing. Exact keys settle it

**Corrects the entry immediately above, which reported 7.1% over 13/18 episodes.** Both figures in
that entry, and RE's independently-derived 6.9%, are over **MANAGER** LLM calls. Every
`structured_llm_*` event in the corpus carries `actor_type == 'manager'`; there are no worker
LLM-call events at all. **The bound being priced wraps the WORKER's `Runner.run`.**

    WORKER runs (worker_execution_started -> completed|failed), n=235, exact pairing on
    (actor_id, task_id), 0 unmatched:   median 81s  p90 452s  p99 777s  max 966s

      180 s  kills 70/235 (29.8%)  in 18/18 episodes    <- four times what either of us priced
      630 s  kills  9/235 ( 3.8%)
      1200 s / 2460 s  kill 0/235                       <- RE's raised bounds, 8e273ec, VALIDATED

**The conclusion never moved; the number moved twice and never below material.** RE's episode was
already running on the raised bounds and is safe — **the bounds were right while the argument for
them was wrong.**

**★ TWO AGENTS AGREEING WAS WHAT HID IT.** LS and RE derived the figure with different pairings
(394 vs 464 pairs) and read the near-match as corroboration. **The differ-test compares
CONSTRUCTIONS. Nothing in it compares POPULATIONS, and it passes cleanly on two answers wrong the
same way.** RR reached the manager-only fact independently from the other side, which is what
surfaced it.

**★ AND ALL THREE PAIRINGS WERE UNNECESSARY.** The events carry exact correlation keys —
`(actor_id, operation, timestep)` for LLM calls, `(actor_id, task_id)` for worker runs — pairing all
18 bundles with **zero unmatched and zero ambiguity**. LS wrote *"the exact version needs a
correlation id the events do not carry"* into a docstring; RR wrote the same sentence independently;
RE paired positionally too. **The fields are in the first event of the first bundle. The corpus was
read three times and inspected zero times.**

**The two failed remedies BRACKET the truth, which is the signature to watch for:**

    LS  positional, all 18 bundles   p99 717 s  max 956 s  10.2%   OVERSTATES
    RR  positional, 2 bundles dropped p99 438 s  max 715 s   6.5%   UNDERSTATES
    exact key,      all 18 bundles   p99 636 s  max 876 s   7.6%   (manager)

RR's diagnosis — positional pairing is unsafe where calls overlap (2/18 manager bundles, **18/18
worker**) — was correct. RR's remedy costs 11% of the data and biases the tail down 31%. **When two
corrections bracket the truth, neither is the fix; the shared assumption underneath them is.**

**RULES ADOPTED (`METHODOLOGY_RULES.md` §G).** RR's form supersedes LS's: **"a threshold names the
distribution it was derived from — and the POPULATION that distribution is over — or it is a guess
with a number on it."** Plus: **independence in the METHOD is not independence in the INPUT** — the
cheap defence against a shared premise is not another derivation but printing one raw record; and
**a pairing is meaningful only if its unmatched count is zero and printed.**

Also corrected: **transferability is "small, measured, bounded", not "no caveat"** — RR measured
r=+0.035 between duration and prompt size, a 1.7x prompt spread moving the median ~20%.

Record: `records/L10/episode_baseline_v1.md` (LS, corrected in place with both corrections stated),
`records/L11/baseline_audit_RR.md` (RR), commits 80b5ecb / c9d76e2 / 8e273ec.

### 2026-08-09 — the population axis failed FOUR times in one day, twice inside the messages naming it. Baseline final at 20 bundles

**Closes the two entries above.** Final numbers, all committed bundles, exact correlation keys, zero
unmatched (`measure_episode_baseline.py`, commit 9fd3e58):

    20 bundles (2 excluded, marked FAILED/INCOMPLETE, exclusion stated in code)
    episode        median 40.3 min   max 83.0 min   117 s per timestep
    WORKER runs    n=266   median 81 s   p90 440 s   p99 904 s   max 966 s
      180 s  kills 78/266 (29.3%)  in 20/20 episodes
      1200 s / 2460 s  kill 0/266                      <- RE's raised bounds, VALIDATED

**★ THE SAME AXIS — WHICH POPULATION — BROKE FOUR TIMES BETWEEN THREE AGENTS IN ONE DAY, AND EVERY
TIME THE TWO WHO CHECKED IT AGREED:**

    1  manager calls priced against a WORKER bound        LS 7.1% / RE 6.9%   truth 29.3%
    2  all bundles vs healthy-only                        RE 259 vs 246
    3  R2-only vs all records/                            LS 235 vs RE 266
    4  "succeeded runs" vs "runs that consumed wall clock" RE 27.2% vs 29.3%

**(2) and (3) were each declared reconciled across a real gap IN THE MESSAGE DIAGNOSING THAT EXACT
MOVE.** Recognising a failure mode as a general pattern did not make either of us apply it to the
sentence being written. **The differ-test compares CONSTRUCTIONS; nothing in it compares
POPULATIONS, and it passes cleanly on two answers wrong the same way.**

**THE RESOLUTION IS NOT AN INCLUSION RULE.** Two exclusions on the same day were correct in opposite
directions: **excluding the attempt bundles was right** (a run that did not FINISH cannot set an
upper bound — the lone 1506 s worker run is in `run_seed101_attempt5_INCOMPLETE.json`), and
**including failed runs was right** (a run that CONSUMED TIME is exactly what a timeout meets;
failures sit above 180 s at 55.0% against 27.2%, so excluding them flatters the bound).
**The population follows from the question, and the question has to be stated first.**

**RULES, both peers' forms adopted over LS's** (`METHODOLOGY_RULES.md`):
- §G, RR's, superseding LS's: **"a threshold names the distribution it was derived from — and the
  POPULATION that distribution is over — or it is a guess with a number on it."**
- §D, filed beside the differ-test as its **input-side twin**: **before deriving from a record,
  print one instance of it.** Three agents independently declared the events carried no correlation
  id; they carry `actor_id`, `operation`, `timestep`, `task_id`, on the first event of the first
  bundle. **Independence in the METHOD is not independence in the INPUT** — every downstream check
  inherited the premise, so no analysis-side rule could contradict it.
- RR's corollary: **absence of a FIELD is not absence of the QUANTITY.** RR searched for
  `execution_time_seconds`, found none, reported workers unmeasured — while holding the pairing that
  recovers every duration from timestamps.
- **When two corrections BRACKET the truth, neither is the fix** (717 s / 438 s / exact 636 s).
- Six signatures indexed in §H.

**TRANSFERABILITY IS "SMALL, MEASURED, BOUNDED", NOT "NO CAVEAT"** — RR measured r=+0.035 between
call duration and prompt size; a 1.7x prompt spread moves the median ~20%.

**LIVE: one episode on `partial`/segs=1, seed 26, unattended.** Kill only on heartbeat silence
>1200 s. **Pre-committed before observing:** under 83 min is inside everything recorded; 83 min–2.5 h
is the first genuinely new observation and is reported, not killed; 2.5 h is the wall-clock stop.
**On the bundle: check whether any worker run crosses 966 s** — the observed healthy ceiling — since
`partial` is a different portfolio. If it does, 1200 s is no longer clear of the workload.

### 2026-08-09 — the FIVE-BUCKET SPLIT is code, not prose — and 0 of 20 committed bundles can ever support it

**Record: `records/L10/five_bucket_instrument_LS.md`. Script: `five_bucket_split.py`.**

**★ NO COMMITTED BUNDLE CAN BE FIVE-BUCKET SPLIT. Not "not yet" — never.** All 20 predate the
structured refusal-code fix, so `finance_split` refuses every one of them, correctly:

    "this bundle predates the structured-code fix and its refusal causes are not recoverable —
     classifying by substring over the prose is how an availability refusal came to be recorded
     as a concurrency one"

**The refusal CAUSES are absent from the record, not merely unparsed.** No re-analysis recovers
them. **The episode running now will produce the first five-bucket split in the study's history,
with no prior to compare it against.** The engine does emit `refusal_codes`
(`core/execution/engine.py:916`) and that commit is an ancestor of HEAD — checked, not assumed,
since the entire finding is that the old bundles lacked it.

**CONSEQUENCE FOR A NUMBER ALREADY IN THE RECORD: the 69%-of-variance non-completion figure was
computed on exactly these bundles, so non-completion CANNOT BE DECOMPOSED BY CAUSE on any of them.**
Which kind of non-completion drives it is not merely unmeasured but unanswerable there. This sits
beside RR's existing limitation on the same figure (*"the decomposition transfers, the absolute
numbers do not"*) and travels with it. Put to RR to attack, since LS did not produce the 69%.

**THE MAPPING HAD LIVED ONLY IN PROSE** — in the cron prompt and this file — while being the thing
that decides whether an incomplete segment is the DV, the manipulation, or the harness. **A mapping
chosen after seeing the counts is a choice about the answer**, so it was built before the bundle it
will judge exists. It never sums the buckets and reports no non-completion rate; `total` appears
nowhere in the output. **Nothing may be reported under these bucket names that did not come through
that file.**

**Controls shown FAILING before the pass was trusted:** a dropped state, a state in two buckets, an
invented state name — each raises. A bucket also inherits its states' non-interpretability, or the
flag would be lost the moment it was aggregated.

**Two judgement calls put to RR rather than settled alone:** `never removed` maps to NOTHING (it is
a bundle-level condition, not a segment state; naming it as a ninth state would invent a category),
and `executed_and_declined` sits in DV rather than MEASUREMENT.

**★ THE CRON PROMPT WAS STALE AGAIN AND WOULD HAVE KILLED THE LIVE RUN.** It still carried *"if the
run has not produced a bundle within ~45 minutes, STOP AND DIAGNOSE"* — **at the median healthy
episode (40.3 min), i.e. the rule that caused three runs to be misdiagnosed as hung.** Not acted on;
prompt replaced with the measured thresholds, the five-bucket instruction, and the four rules paid
for today. **Second occurrence: a cron prompt is part of what must change when a ruling changes.**

**PREDICTION PROTOCOL OPEN on the live episode.** LS's prediction is committed in the record above
**before** RE and RR were asked, and both were asked privately. LS predicts BUDGET_HORIZON largest
excluding MEASUREMENT, MANIPULATION (`refused_unavailable`) at 0 or 1; falsified by MANIPULATION at
2+ or DV exceeding BUDGET_HORIZON. Grounding, from what the corpus CAN still answer over the same 20
bundles: `n_parsed` median 7.5, `n_missing` median 1.5, `n_unstaffed` median 1.0, **2.6 of 9 segments
incomplete per episode, 17 of 20 with at least one**. Coarse shape only — it says nothing about
which bucket, which is the gap the episode closes.

### 2026-08-09 — all three predictions opened: we agree on MANIPULATION, and the agreement is not evidence

**Record: `records/L10/five_bucket_instrument_LS.md` (comparison section). Predictions committed
before the bundle existed; LS's before RE and RR were asked.**

    LS   BUDGET_HORIZON largest    MANIPULATION 0-1
    RE   DV via refused_allotment  MANIPULATION 0
    RR   DV via refused_allotment  MANIPULATION 0   (MEASUREMENT 5-7, DV 2-4, BUDGET 0-1)

**LS diverges from both peers and expects to be wrong.** LS grounded the prediction on `n_unstaffed`
median 1.0 and `n_missing` median 1.5 — **outcome counts that do not distinguish cause, which is
exactly what the instrument exists to fix.** A coarse number used to predict a fine one. The
prediction stands as committed and unrevised; both peers' capacity argument (nine slots, nine
segments, the allotment never releases, no manager allocates perfectly evenly) is the stronger one.

**★ THE AGREEMENT RESTS ON A QUANTITY THE OLD CORPUS COULD NOT OBSERVE.** `refused_allotment` was
established by elimination over numeric fields — `available=True` rules out unavailable,
`count=0 < max=1` rules out concurrency, therefore allotment (335/245). Measured across the corpus:

    deferral events carrying agent_available    623 (LS, run_* bundles)   653 (RE, incl. dry_run)
      agent_available == False, EVER              0                         0
      refusal_codes present on                    -                         0 of 653

**`agent_available` is True on every deferral ever logged and never takes the other value, and there
is NO CAUSE FIELD AT ALL** (RE's corollary, stronger than the finding): every payload field is an
outcome count or an identifier. **The elimination was not merely leaning on a constant field — it
was the only method available, because cause was never recorded.**

**So the 335 attributed to allotment is an UPPER BOUND that may contain the manipulation's own
signature, and all three of us predicted MANIPULATION ≈ 0 from a corpus in which MANIPULATION was
structurally unobservable.** RE's own reason (cell 0 withholds the CARD, not the ROSTER, so the
manager knows who is present) is independent of the corpus and survives; the *agreement* does not.

**WHICH BUCKET IS CONTAMINATED — corrected, and it is the one both peers predict will be largest.**
RR wrote that a lost availability refusal *"was logged as concurrency"*; by the elimination table
`available=True` removes unavailable and `count=0` removes concurrency, so **it lands in
`refused_allotment`**. RE: *"if I am right about DV being largest, part of my own evidence for it may
be the manipulation wearing the wrong label."*

**THIS IS WHAT THE EXPERIMENT ADDS BEYOND CONFIRMATION** (the protocol's question, answered): it is
the first observation capable of falsifying a belief all three of us hold for a reason that is not
evidence. **Not shrunk to a smoke test.**

**RE flagged 653-vs-623 as a POPULATION DIFFERENCE (dry-run bundles) rather than calling it
reconciled** — explicitly because of the 11-pair gap called "reconciled" earlier today. The
discipline held on its next occurrence.

**RR'S THREE CORRECTIONS TO THE INSTRUMENT, all applied, two verified at source before adopting:**
1. **The 69% limitation is stronger than LS wrote it.** `task_assigned` occurs **0 times** in the
   corpus (`finance_split` reads exactly that event); deferral payloads carry no assignment record.
   **The CAUSAL STRUCTURE is absent, not just the causes** — even `never_assigned` vs
   `assigned-then-refused` is unrecoverable, so no reanalysis decomposes it at ANY granularity.
2. **`never removed` — RETRACTED IN PLACE. Right call, wrong referent.** It is a HANDLING DIRECTIVE
   on the MANIPULATION bucket, already discharged in `BUCKET_MEANS`; LS read it as a bundle-level
   condition *"asserted by the runner"*. **The wrong reason MANUFACTURED AN OBLIGATION** — it would
   have sent a future reader hunting a runner assertion nobody intended to write. **A wrong call is
   found by anyone who checks; a phantom obligation is found by nobody, because the thing it points
   at does not exist to contradict it.**
3. **`executed_and_declined` pools two causes** — a decline in a class the assignee does NOT cover is
   a manager mis-assignment (DV); a decline in a class it DOES cover is the worker's judgement and is
   not an allocation outcome. **Stays in DV, recorded as `KNOWN_POOLING` in code**, splittable the
   moment a bundle shows an in-coverage decline. First bundle carries that check.

**ORDER OF READS ON THE FIRST BUNDLE, agreed:** `five_bucket_split.py <bundle>` before any other
read; then whether any worker run crosses **966 s** (the observed healthy ceiling); then whether
`agent_available` is ever False. **If it is still constant the field is decorative and should be
fixed or removed rather than left to mislead the next elimination.**

### 2026-08-09 — ★ VALIDITY: `refused_unavailable` IS UNREACHABLE. The MANIPULATION bucket cannot fill, and the manipulation's footprint is recorded NOWHERE

**Found by RR before any bundle landed, against RR's own prediction. Verified at source by LS.**
Records: `five_bucket_split.py` (`MANIPULATION_UNREACHABLE`), `finance_split.py` (predicate
retracted in place).

    interface.py:82 / telemetry.py:58   is_available declared True
    every other occurrence in the repo   a READ -- there is NO WRITE anywhere
    the three model_copy(update=) sites  none touches it  <- closes RR's setattr residual
    registry.py:405, the swap            remove_agent(...) REMOVES, never marks

**The branch at `interface.py:105` is dead code.** RR flagged a dynamic `setattr` as an unclosed
residual — *"I have not proved absence, only failed to find presence"* — and it is now closed by
positive enumeration of the write set rather than by a failed grep.

**★ AND THE FOOTPRINT IS NOT IN ANOTHER BUCKET — IT IS NOWHERE.** An assignment to the departed
worker after the swap: returns early at `manager_actions.py:227` **before** `record_assignment` (so
no `task_assigned` event), never reaches `can_handle_task` (so no deferral and no refusal code), and
never mutates `assigned_agent_id` (so `intended_allocation`, which reads that field, is unchanged).
**The segment ends `never_assigned`, INDISTINGUISHABLE FROM A MANAGER THAT NEVER TRIED.**

**ALL THREE PREDICTIONS OF MANIPULATION = 0 ARE VOID, NOT HITS. A prediction about a quantity that
cannot vary is not a prediction** — the same defect as an elimination step that "rules out
unavailable" using a field that never varies, one level up. **Third instance today of a check that
cannot fail being read as a check that passed.**

**OPTION (a) — MAKE THE STATE REACHABLE BY MARKING THE PREDECESSOR UNAVAILABLE — IS REJECTED ON THE
STANDING PRODUCTION-GRADE TEST**, not on convenience. A real orchestrator deregisters a departed
worker and rejects assignment to an unknown id; **keeping a ghost in the roster so our bucket fills
is manufacturing the problem we then measure.**

**THE FIX IS (c), WHICH NEITHER PEER LISTED: RECORD THE REJECTED ACTION.** A **recording** change,
not a behaviour change — a real orchestrator logs rejected assignments anyway, and `engine.py:551`
already carries a comment about exactly this silence class. **Acceptance: a segment that ended
`never_assigned` because the manager aimed at a departed worker must be distinguishable from one the
manager never touched.** RE owns it, **after the running bundle lands and BEFORE the L10
environments**.

**WHAT IT COSTS, BOUNDED AND STATED BECAUSE IT REACHES THE PAPER.** *"Allocating as if the
predecessor remained"* has two halves: **failing to REASSIGN inherited tasks still on the board is
OBSERVABLE** (`task_board_final`), untouched, and is novelty property 2 — **that works**; **actively
assigning NEW work to a departed worker is INVISIBLE**. **One half of one of five named failure
modes. The study's main channel is unaffected.**

**INTERIM GUARD, so a zero cannot be misread:** `MANIPULATION` now carries `uninformative=True` and
its reason **on the data structure**, not in a printed banner — a banner is dropped by the first
summariser that reformats the output, and every consumer reads `buckets`.

**THE L2a PREDICATE IS RETRACTED IN PLACE, VISIBLY** — *"which a roster change can cause, so this is
the state a swap run must be able to see separately"* asserted a capability the harness does not
have **and was quoted twice as the authority for a ruling**. The first clause is kept (it says what
the state would mean if it could fire) and the state stays in the partition; only the observability
claim is withdrawn. **Acceptance re-run as documented: RESULT PASS, every named blocker still
fires.** (`pytest` collects 0 from that file **by design** — it is a module script, not a suite; the
empty run was checked rather than read as a pass.)

**RR's ruling was RIGHT ON THE PRINCIPLE and the PREDICATE was false as implemented — different
failures, and only the second is RR's.** The bucket must still never be classed as removable noise;
it simply cannot fill until (c) lands.

### 2026-08-09 — L10 acceptance is code, built BEFORE the instances — and running its controls found three defects in the acceptance itself

**Record + script: `check_l10_properties.py`. Seeds 26 and 39 pass all six properties; all seven
controls fire; RESULT PASS. Zero model calls.**

Written before the instances exist for the same reason as the five-bucket mapping: **an acceptance
criterion chosen after seeing the artefact is a choice about whether the artefact passes.** RE builds;
this is what the build will be held to, and it is runnable now.

    1  ceiling_share > 0                              seed 26: 0.00462   seed 39: 0.01478
    2  nA < cap                                       nA=1 both
    3  lied class has another post-swap holder        26: mdb->w_cd45fc   39: bank->w_b4f6e4
    4  len(segments) == len(roster_post_swap) * cap   9 == 3 x 3
    5  Basel digest MATCH and amplify_divergence off
    6  admit(...)["admitted"] is True

**★ THREE DEFECTS IN THE ACCEPTANCE, ALL FOUND BY RUNNING THE CONTROLS RATHER THAN WRITING THEM.**

**(i) THE STEP'S OWN FIXTURE FOR PROPERTY 2 IS SEED-DEPENDENT AND PASSES VACUOUSLY ON SEED 26.**
*"Force `shared_class_segments = cap`"* reaches nA=3 on seeds 0–11 but only **nA=2 on seed 26** — one
of the two candidate instances. **Run on seed 26 alone it looks like a demonstrated failure and
demonstrates nothing.** The fixture now searches and names the seed it fired on (seed 1).
**A control whose firing depends on an argument nobody varied is the can't-fail check in its most
convincing costume** — the third variant of that shape today, after the constant `agent_available`
and the unreachable `refused_unavailable`.

**(ii) THE PROPERTY-6 FIXTURE ASSUMED `current` FAILS ADMISSION. IT DOES NOT** (`admitted=True`).
Replaced with a measured one: **18 of 40 seeds are rejected at the shipped cell**, seed 0 failing
`3_scripted_baseline_below_oracle`. Named, not assumed.

**(iii) GENERATION REFUSES IN TWO WAYS AND THE SEARCH KNEW ONE.** At `segs=3` with
`irb_applicable_fraction=0.89` it raises a bare **`ValueError`** (*"only 7 of 9 segments have a
non-zero SA fallback, but 8 IRB-approved segments were requested"*), not `InstanceAssertionError`.
The loop crashed instead of skipping — **and because the crash went to stderr while the report went
to stdout, the run READ AS TRUNCATED RATHER THAN FAILED.** Both refusal types caught, skips counted
and reported, stdout line-buffered so the interleaving cannot recur.

**★ THE TRAP FOR THE BUILD: `generate()`'s DEFAULTS DISAGREE WITH THE SETTLED SETTING ON THREE
PARAMETERS.**

    irb_applicable_fraction   default 0.67   settled 0.89
    amplify_divergence        default True   settled False
    amplify_irb_priority      default True   settled False

**A bare `generate(seed)` silently produces a different environment that still looks plausible.** The
checker writes the setting out in full and never defaults, and property 5 checks the SWITCH as well
as the tables — which is why property 5 has two halves and the switch half is the one that drifts.

**Property 5 detects PERTURBATION via a pinned digest of the SA tables and PD floors; it does NOT
establish correctness against BCBS** — that remains S1's `test_basel_reference`, named in each
instance's `irb_provenance`. The perturbation fixture mutates and restores `SA_SOVEREIGN` and
asserts the restore, since a fixture that leaked state would invalidate every later property.

**Property 3 confirmed as the relational one:** `current` passes 1, 2, 4, 5 and 6 and fails only 3
(`other_post_swap_holders=[]`).

**STANDING CHECKS ON THIS STEP, answered.** **(1) PRODUCTION TEST — PASSES**: every benchmark and
fixture in production software is constructed, and an acceptance suite that runs before the artefact
is ordinary practice. **(2) NO DRIFT** — the properties are what make the card channel measurable at
all. **(3) AMBIGUITY** — one found and resolved in code rather than routed around: the step named a
fixture that does not violate its property, and that is recorded above rather than quietly fixed.

### 2026-08-09 — ★ THE INSTANCE SELECTION WAS DRAWN AT THE WRONG CELL. Intended low/mid/high became low/LOW/high

**Script: `check_selection_at_settled_cell.py` (exit 1). Zero model calls.** Found by applying RE's
own bare-`generate()` finding — RE caught it in the L9 lattice table and checked their committed
work; this is the same defect one level up, where it costs more.

    selection record   15 admitted   median 2.12%   band 0.36-4.76%
    settled cell       22 admitted   median 3.41%   band 0.46-6.61%

    seed 26   intended LOW    settled  0.46%   LOW
    seed 39   intended MID    settled  1.48%   LOW    <-- MOVED
    seed 37   intended HIGH   settled  6.61%   HIGH

**THE MID STRATUM IS EMPTY AND THE LOW STRATUM IS DOUBLED.** What is lost is **coverage of the
range**, which was the draw's entire purpose — not merely a changed number.

**THE DRAW WAS SOUND AND THE RECORD IS HONEST ABOUT ITSELF.** One seed per rank-tercile, draw seed
fixed and recorded before the draw, and `caveat_1` states outright that seed 26 is the suite minimum
and a legitimate 1-in-11 draw rather than a take-first artefact. **The defect is the CELL, not the
draw: a valid stratification of a population the study does not use.** `generate()`'s defaults are
0.67/True/True; the settled cell is 0.89/False/False.

**DOES NOT INVALIDATE THE RUNNING EPISODE.** Seed 26's purpose is the HARNESS measurement —
feasibility and the first five-bucket split ever computed — not an instance measurement. Its gap
being the suite minimum is irrelevant to what is being asked of it.

**DOES BLOCK L10's CHOICE OF ENVIRONMENTS.** The step requires the two to differ *"enough that a
finding on both is not instance-specific"*; **two instances from the same bottom tercile (0.46% and
1.48% against a 3.41% median) is the precise opposite.**

**★ AND THE FIX IS NOT "PICK BIGGER GAPS" — THAT IS THE TRAP THE SENSITIVITY LADDER WAS RETIRED
FOR.** `card − ignorant` falls monotonically as the ceiling rises, so **selecting on gap size ranks
manager policies**: the high-gap instances are the most CONTAMINATED, not the most decisive. **The
tercile draw is the anti-confound device.** The fix is to **re-draw the stratified sample at the
settled cell, preserving low/mid/high** — same rule, same discipline, correct population.

**ESCALATED TO THE RESEARCHER, not decided by the team:** it changes which instances the study runs
on. Runner not to be re-pointed until it comes back.

**RE's PARALLEL FINDING, carried here because it is the same class:** the L9 lattice table was also
measured at 0.67/True/True. **Every qualitative claim holds** — `current` is 0.00% under both, both
candidates live under both, ordering `disjoint > partial > current` unchanged, and the comparison was
internally consistent across all three lattices, so it remains a valid comparison OF LATTICES. **Only
the absolutes move: 0.00/2.17/5.41 as measured against 0.00/3.21/6.94 at the settled cell.** The
record carries `lattice` and `shared_class_segments` per row but **not** `irb_applicable_fraction` or
the amplifier switches. **RE's generalisation: the bundle manifest learned this lesson and the
offline records did not.**

### 2026-08-09 — the acceptance digest was HOLED at retail; wall clock extended to 210 min on a stated basis

**RR's review of `check_l10_properties.py`: no blockers, one real hole.** Record:
`records/L10/L10_acceptance_review_RR.md`.

**★ THE DIGEST SKIPPED RETAIL, AND THE ENUMERATED LIST WAS THE MECHANISM.** It named
`SA_SOVEREIGN/BANK/CORPORATE/MDB` and missed **`SA_RETAIL_FLAT`** — the SA treatment for one of the
five asset classes, **a flat constant reached by a NAME TEST rather than a table lookup**, pricing
**54 segments across the 30-seed corpus. An edit to retail's weight passed the drift detector
silently.** Also missed `SA_TABLES`, so a class registered with an SA table but no PD-floor entry was
invisible (RR checked this case rather than asserting it, and reported their first suspicion was
wrong and the hole narrower).

**FIXED BY DIGESTING CONTAINERS, NOT BY ADDING TWO NAMES**, because RR's diagnosis is that the list
is the bug: `SA_TABLES` covers every class present **and every class added later**; `SA_RETAIL_FLAT`
is listed separately because it is deliberately outside that registry. **Adding two names would have
fixed today's hole and re-earned it the next time the module grows.** New fixture **5c** perturbs
`SA_RETAIL_FLAT` and fires. **Eight controls, all firing, RESULT PASS.**

**RR's generalisation, recorded because the recurrence is structural rather than an oversight
repeated: RETAIL KEEPS FALLING THROUGH BECAUSE IT IS SHAPED DIFFERENTLY FROM ITS NEIGHBOURS** — the
same difference that excluded it from clone registration.

**RR confirmed a property LS built without claiming: the dead-perturbation case self-reports.** If
the mutation were a no-op, `p5` passes, the fixture returns False, and the control reads **NOT FIRED**
rather than passed — **the property today's other can't-fail cases lacked.**

**PROPERTY 3's FOOTING IS FIRMER THAN LS STATED IT.** `ceiling_vs_stale_card` sets
`succ_as_carded["irb_coverage"] = set(predecessor irb_coverage)` — **the card asserts the successor
covers exactly the predecessor's set**, so lies are `pred − succ` and silence is `succ − pred`.
`lied_classes()` is the first of those exactly, **derived from the module property 3 protects rather
than from a reading of the mechanism.**

---

**WALL CLOCK EXTENDED TO 210 MINUTES for the live episode, basis stated before the outcome.**

RE measured the slowing with the 600 s dump markers rather than trusting cumulative averages (which
rise even at constant pace): **~200 s/step in the first window, flat at ~600 s/step for the last
thirty minutes — genuine 3x slowing.** At 8 steps done in 50 min and 14 remaining, the run reaches
**~190 min**, i.e. it would have been stopped at **t17–t18 of 22** by the 150-minute bound.

**AND THE BUNDLE IS WRITTEN ONLY AT COMPLETION**, so a stopped run yields **nothing** — no
five-bucket split, no 966 s check, no feasibility datum. Verified rather than assumed: the process
holds only `/tmp/instr.log`, and no per-timestep snapshot is written because the runner does not wire
`output_writer` (whose `workflow_dir` path would otherwise emit one).

**THE DISCRIMINATOR FOR EXTENDING, WHICH IS TODAY'S OWN RULE (a):**

    the 45-minute rule   basis NONE                                    -> retired
    the 180s timeout     basis NONE                                    -> retired
    the 2.5h stop        basis: clears the 83-min observed max, n=20

**The 2.5 h was derived from HEALTHY EPISODE DURATIONS. This episode is measurably outside that
population** — 600 s/step against a 118 s/step corpus mean, observed directly. **Applying it here is
the same population error made four times today, not an exception to the discipline.** Had the basis
been *"we are willing to spend 2.5 hours"*, it would hold.

**New bound 210 min = 190 measured + ~10%. It does not move again**; an overrun falsifies this basis
too. **Heartbeat silence > 1200 s still kills immediately, whatever the clock says** — the wall clock
was always a proxy for a hang detector we did not have and now do.

**Weighed against extending and recorded because it should not be lost: this episode is on seed 26,
which the entry above shows is the WRONG INSTANCE for L10.** Its value is entirely the harness
measurement, which does not depend on the instance being well-chosen. **If its value were the effect
size, it would have been stopped.**

**HARNESS DEFECT, RE's, accepted and open: the artefact exists only at the end, so a run that dies at
t17 of 22 has done 77% of the work and can report none of it.** Same shape as the missing heartbeat.
Fix after this run, not mid-run. **What the log HAS banked and survives a kill:** t00–t07 completion
trace, 7 of 16 tasks at t07.

### 2026-08-09 — the acceptance survives the environments changing (measured); and PASSING IT DOES NOT MEAN AN INSTANCE IS REPRESENTATIVE

**RR ran all eight controls across eight seeds spanning the range, then applied the differ-test to
their OWN sweep.** Record: `records/L10/L10_acceptance_review_RR.md`.

**RESULT: 7 of 8 controls verified seed-independent by measurement; the 8th was pinned by
construction and its column was vacuous.** `_fixture_p6` ignored its `seed` parameter entirely and
called `p6_admitted(REJECTED_SEED, ...)`, so **its eight "fire"s were one observation printed eight
times.** Quoted as 7-of-8, never as 8/8. **Fourth instance today of a check that could not have come
out otherwise being read as a check that passed** — and the first found by an agent auditing their
own check rather than someone else's.

**FIXED:** fixture 6 now searches `(seed, REJECTED_SEED, 0..11)` and names the seed it fired on —
**5 distinct outputs across 8 seeds where it gave 1.** RR's second reason for not pinning is the
better one and generalises: **`REJECTED_SEED` was verified rejected AT THE SETTLED CELL, and the
selection defect is exactly a cell moving underneath a recorded fact.** Searching re-establishes it
every run rather than trusting a measurement taken once.

**LS's follow-up test was WEAKER than RR's and is recorded as such rather than as more findings.**
Diffing fixture OUTPUT STRINGS across seeds flags fixtures 1, 4, 5a, 5b and 5c as "1 distinct
output" — **but those read their seed and simply have seed-invariant ANSWERS**, which is a different
thing from seed-blind CODE, and a string diff cannot separate them. Confirmed by inspection: **all
eight read the seed.** **RR's code-level question — "does the fixture use its `seed` parameter" —
found the real case where LS's would have reported four false ones.**

**★ THE POINT TO CARRY INTO THE L10 INSTANCE DECISION, because it is the one most likely to be
misused: SEED 26 IS THE SUITE MINIMUM AT 0.46% AND PASSED ALL SIX PROPERTIES.**

> **The properties are THRESHOLD conditions. Passing tells you an instance is ADMISSIBLE. It does
> NOT tell you it is REPRESENTATIVE.**

Reassuring about the acceptance; silent about the selection. **The two are easy to conflate when a
replacement pair is argued for — "it passes the acceptance" will be true of the weakest instance in
the pool.** Stands beside the re-draw recommendation, which is with the researcher.

### 2026-08-09 — ★ AMBIGUITY (standing check 3): the L10 pair's SELECTION AXIS is not the tercile rule, and LS's re-draw recommendation used the superseded criterion

**Raised before implementing, not routed around. Nothing built, runner not re-pointed.**

**TWO SELECTION PRINCIPLES ARE IN PLAY AND THEY ARE DIFFERENT AXES:**

    the existing selection record   one seed per rank-tercile of the CEILING   -> samples the GAP RANGE
    L10's own text                  "which asset class sits in the sole-need
                                     position is the natural axis"            -> varies STRUCTURE

**LS recommended to the researcher "re-draw preserving low/mid/high". That preserves the TERCILE
rule — and the step names a different axis.** On a close reading the tercile draw appears
**SUPERSEDED BY L10** rather than merely broken by the cell defect: it belonged to the
3-instances-across-6-cells design, while L10 asks for two instances *"both with a real gap"* (a
FLOOR) *"differing enough that a finding on both is not instance-specific"*, with the asset class as
the axis. **The recommendation already sent to the researcher needs amending on this point.**

**THE AXIS EXISTS — measured at the settled cell, 22 admitted:**

    successor-unique (sole-need) class:   corporate 7, sovereign 7, retail 3, bank 3, mdb 2

**AND IT IS CONFOUND-SAFE FOR THE REASON THE TERCILE DRAW EXISTED.** The ladder was retired because
`card − ignorant` falls monotonically as the ceiling rises, so **selecting BY GAP ranks manager
policies.** Selecting by ASSET CLASS does not select on gap at all — it sidesteps the confound
rather than stratifying around it.

**★ THE UNRESOLVED PART IS THE FLOOR, AND THE ACCEPTANCE CANNOT SETTLE IT.** *"Both with a real
gap"* carries no number; property 1 requires only `ceiling_share > 0`; **seed 26 at 0.46% passes all
six properties.** RR's rule is why that does not help: **the properties are threshold conditions —
passing means ADMISSIBLE, not REPRESENTATIVE.** So *"it passes the acceptance"* is true of the
weakest instance in the pool.

    1  ceiling_share > 0        the property as written; admits 0.46%; almost certainly too weak
    2  >= admitted median 3.41% defensible, but it IS a gap-magnitude criterion -- the thing the
                                ladder was retired for. Confound through the back door?
    3  a floor from detectability   the principled one, NOT COMPUTABLE: per-episode sigma unknown,
                                df=6 sizes nothing

**Put to RR specifically: is (2) the confound returning, or is LS over-applying the ladder's lesson?**
The ladder ORDERED instances by gap to build a sensitivity contrast; a FLOOR is not a ranking, and
excluding the bottom of a distribution is not the same as ordering by it. **Arguable both ways, which
is why it is not being decided by LS alone.**

**A separate trap noted for whatever rule is adopted: the pair could share a sole-need class by
accident** — corporate and sovereign are 7 each, so a naive draw can pick two corporates and satisfy
nothing the step asked for. **The rule must ASSERT the two differ on the axis, not hope they do.**

**STANDING CHECKS ON THIS STEP.** **(1) PRODUCTION TEST — PASSES**: constructing benchmark instances
to stated properties is ordinary practice; nothing here models behaviour a real system would not
ship. **(2) NO DRIFT** — the instances are what make the card channel measurable; this is the
instrument. **(3) AMBIGUITY — FOUND, and it is this entry**, raised to both peers and to the
researcher rather than resolved by picking a reading.

### 2026-08-09 — the L10 SELECTION RULE is settled by the team and executable; awaiting the researcher's go

**All three agree there is NO DETECTABLE COUPLING between gap magnitude and card-informativeness
WITHIN the arrangement, so a ceiling floor does not reintroduce the confound.** Three independent
measurements, all essentially zero and scattered around it:

    LS   r = -0.137   below/above-median card-ignorant  +0.0781 / +0.0803   (share, seeds 0-39)
    RE   r = -0.016                                     +0.0803 / +0.0818   (share)
    RR   r = +0.094                                     +0.6122 / +0.7112   (ABSOLUTE, seeds 0-59)

**RR's figures are the ABSOLUTE quantity and LS/RE's are the SHARE — the same quantity in different
units (~0.68 absolute ≈ 0.081 as a share), not a disagreement.** RR's caveat is the honest form and
is adopted: **at this n it is "no detectable coupling", not "provably none."**

**★ THE MECHANISM, which is why the ladder's lesson does not transfer (RR):** the coupling is
**ARRANGEMENT-level, not instance-level**. Across arrangements the STRUCTURE changes where the lie
lands, moving `card_play` relative to `ignorant`. Within a cell, seed variation changes overall
DIFFICULTY, moving `card_play` and `ignorant` TOGETHER and leaving their difference alone. **RR
predicted the opposite analytically and recorded the error: the argument holds only if `ignorant` is
constant, and it is not.** LS's instinct and RR's arithmetic were wrong the same way — **both treated
a cross-arrangement mechanism as general.**

**LS NEARLY REPORTED A FALSE DISAGREEMENT WITH RE.** LS computed r = **+0.461** and went looking for
the difference. Population was not it. **The QUANTITY was: `ceiling_vs_ignorant_share` is
oracle−ignorant, which CONTAINS the ceiling, so LS was partly correlating the ceiling with itself.**
`card − ignorant` = `ceiling_vs_ignorant_share − ceiling_share`. **LS printed the scorer's keys and
still took the wrong one — so the rule needs the construction written AS AN EQUATION, not the field
named.** RE avoided it by construction rather than by noticing, and says they would have made the
same error reaching for the ready-made field.

**POOL COUNTS RECONCILED — both were right and neither should have been quoted without its range:**

    seeds 0-39   22 admitted   (LS)
    seeds 0-59   34 admitted   (RR)

**THE SETTLED RULE.** Property 1 (`ceiling_share > 0`) stays as ADMISSIBILITY and never becomes a
selection rule.

    1  pool     admitted at the settled cell, SEED RANGE STATED
    2  floor    ceiling >= pool median            (3.30% at seeds 0-59)
    3  usable   sole-need classes with MORE THAN ONE candidate above the floor
    4  draw     two DISTINCT classes at random from the usable set, draw seed recorded BEFORE
    5  pick     within each drawn class, the largest ceiling above the floor
    6  assert   the two differ on class; each class had >1 candidate; both pass the six properties

**Step 3 is RR's and it is load-bearing: the floor THINS THE AXIS badly.**

    class       admitted   above floor
    corporate         14            8
    sovereign          8            2
    bank               5            3
    mdb                4            1   <- ELIMINATED by condition (b)
    retail             3            3

**4 of 5 classes usable, 6 valid class pairs.** Without condition (b), *"we varied the axis"* could
mean *"we took the only instance available"*, which is a different claim. **And with corporate at 8
of 17, a naive draw picks two corporates about a fifth of the time — so the rule ASSERTS the two
differ rather than hoping.**

**Best candidate above the floor, per usable class:** bank seed 56 (5.29%), corporate seed 37
(6.61%), retail seed 10 (5.91%), sovereign seed 15 (5.89%).

**★ THE ARGUMENT THAT REPLACED AN ARBITRARY THRESHOLD IS RE's AND IT IS SIGMA-FREE.** Required n
scales as effect⁻², so relative cost needs no sigma:

    top of pool 6.61%  1.0x episodes     median 3.30%  4.0x     seed 26  0.46%  204.5x

**Seed 26 is not "a bit weak" — it costs two orders of magnitude more for the same finding.**

**LIMITATION CARRIED TO THE RESEARCHER UNSOFTENED (RE):** two instances differing on one structural
axis is a **weak generalisation claim however they are chosen**. That is L10's design, not the
selection rule.

**NOT EXECUTED. The draw awaits the researcher's go on the rule.** Runner not re-pointed.

### 2026-08-09 — the bundle analysis is code before the bundle exists; composing it found `five_bucket_split` could not be imported

**Script: `analyse_first_bundle.py`. Zero model calls.** Third instrument today written ahead of its
subject. It fixes **the agreed read order** (split first, then worker runs vs 966 s, then
`agent_available`) and **records the three predictions verbatim in the module**, so neither the order
nor the scoring can drift toward whatever the bundle says.

**★ DEFECT FOUND BY COMPOSING IT: `five_bucket_split.py` used an absolute `from finance_split import
...`, so it ran ONLY as a direct script with a special `PYTHONPATH` and could not be imported by any
other module in the package.** The cron's documented invocation worked — **which is exactly why
nobody noticed. A green signal nobody re-derived under a second invocation.** Now tries the
package-relative form and falls back, so both work.

**A NON-CLASSIFIABLE BUNDLE STOPS THE ANALYSIS, deliberately.** Sections 2–4 compute fine on a
pre-fix bundle — worker durations and `agent_available` need no refusal codes — and **printing them
under the heading "first classifiable bundle" would present it as analysed.** The standing rule is
that nobody touches non-completion until the split says which bucket; **so if the split cannot
speak, nothing after it is reported.** Verified: exit 2 on an R2 bundle.

**POSITIVE PATH EXERCISED** on a synthetic bundle built from `test_finance_split`'s own fixture
helpers (synthetic, never committed as data): all four sections run; **a tie for the largest bucket
scores every prediction MISS with the tie printed** rather than silently picking a winner; a 1100 s
worker run trips the 966 s ceiling alarm.

**LIVE RUN at t18 of 22, 90 minutes: 12 of 16 tasks, and FOUR CONSECUTIVE ZERO-COMPLETION STEPS
(t15–t18).** Noted, not interpreted — **which bucket those four segments land in is precisely what
the split exists to answer**, and reading the pattern before running it is the thing the standing
rule forbids.

### 2026-08-09 — ★ THE FIRST FIVE-BUCKET SPLIT EVER COMPUTED. All three predictions MISS; the 966s worker check FIRES

**Bundle: `records/R3/run_cell0_seed26.json`. Analysis: `analyse_first_bundle.py`, written before the
bundle existed.** Run completed all 22 timesteps in ~100 minutes at 12 of 16 tasks — inside the
210-minute bound and close to RE's ~190-minute projection, so **the extension basis held.**

    DV              1   refused_allotment=1
    MANIPULATION    0   [UNINFORMATIVE - structurally cannot fire]
    BUDGET_HORIZON  0
    DEFECT          1   executed_but_unparseable=1
    MEASUREMENT     7   executed_and_parsed=7
                    9 segments. NOT summed. No rate reported.

**PREDICTIONS, scored by the module that recorded them verbatim before the bundle existed:**

- **LS predicted BUDGET_HORIZON largest. IT IS ZERO** — the wrong bucket entirely, not a near miss.
  The reasoning was that capacity binds so the horizon would bite; **it did not bite at all.**
- **RE and RR predicted DV. DV is 1 and TIED with DEFECT at 1.** Scored MISS for both **with the tie
  printed rather than awarding it** — a tie at n=1 is not a demonstrated largest bucket. **Their
  mechanism may be right and this episode cannot show it.**
- **All three MANIPULATION predictions VOID**, as pre-committed.

**★ THE 966s WORKER CHECK FIRED AND IS THE RUN'S REAL FINDING.** Exact pairing on
`(actor_id, task_id)`, n=15:

    median 177s   max 2160s
    5 of 15 exceed the 966s CORPUS MAXIMUM
    0 exceed the 2460s backstop -- but the margin collapsed from +155% to +12%

**This arrangement produces worker runs longer than anything the baseline was built from, so the
baseline no longer describes it.** The backstop held, by 300 seconds. **Whether 2460 moves is RE's
call, but it should be a decision rather than a survival.**

**★ AND LS's OWN ANALYSER HAD A UNITS ERROR, caught before reporting.** It first printed *"4 over
the raised 1200s timeout"* — **comparing worker RUN durations against `litellm.request_timeout`,
which bounds ONE REQUEST while a run contains several.** The bound governing a run is the backstop.
**Third instance today of a bound priced against the wrong population — this one by the agent who
spent the morning correcting the same shape in the 180s figure.** Corrected in the module with the
reason in place. **Worker REQUEST durations remain unobservable: every `structured_llm_*` event is
the manager's.**

**DEFECT = 1 wants attention before the L10 environments run, not after** — one segment executed and
was unparseable, and by the mapping that is *a bug to fix, never a finding*, at 1 of 9 on the first
classifiable bundle.

**`agent_available`: present on 10 events, False on 0. Confirmed DECORATIVE.** Fix or remove it —
a field that cannot discriminate is what let the elimination look sound.

**WHAT THIS DOES NOT ESTABLISH, and it must precede any quotation of the split: NOTHING ABOUT EFFECT
SIZE.** Seed 26 is the **suite minimum** at the settled cell and was **selected at a cell the study
does not ship**. One episode, no interval. **Its value was always the harness measurement, and it
delivered exactly that:** the split runs, the pairing is exact, the bounds are measured against a
real `partial` episode, and the arrangement is now known to be slower than the corpus.

**PROCESS NOTE: a `find` for the bundle reported nothing while the file existed** — the log named the
path and the search did not surface it. **Absence of a search result is not absence of the artefact**,
which is the same shape as the day's other findings, in the last check of the day.

### 2026-08-09 — ★ THE DV IS CONTAMINATED BY EXECUTION FAILURES: a failed attempt permanently burns a scarce slot, and the resulting refusal scores as an allocation outcome

**Found by chasing RE's two flags on the first bundle. Mechanism verified in code, not inferred from
the single observation.** `records/R3/run_cell0_seed26.json`.

**`finance_env.execute_task` consumes the allotment BEFORE the work runs, and nothing releases it:**

    async def execute_task(self, task, resources):
        if self.is_metered(task):
            self.segment_task_ids.add(task.id)      # consumed here
        return await super().execute_task(task, resources)   # may fail after

**So a FAILED execution permanently spends a segment slot.** With capacity binding exactly (9
segments, 3 workers x cap 3) there is no slack to absorb it.

**seg_04 IS THE WHOLE OF DV=1 ON THIS BUNDLE, AND ITS CAUSE IS TWO FAILED EXECUTIONS:**

    t2   worker_execution_started / FAILED   by w_6a33e4 (the PREDECESSOR)
    t13  assignment_deferred  segment_allotment
    t14  assignment_deferred  segment_allotment
    t15  worker_execution_started / FAILED   by w_29592b (the SUCCESSOR)
    t18  assignment_deferred  segment_allotment
    t21  assignment_deferred  segment_allotment

**The label `refused_allotment` is ACCURATE as a terminal state and MISLEADING as a cause.** DV
means *"an allocation outcome — the thing the study measures"*; **this refusal was caused by a
worker/harness failure burning slots, not by the manager allocating badly.** The manager may have
allocated correctly and still scored a DV event.

**NOT OVERCLAIMED: one segment, one episode.** What is not n=1 is the **mechanism**, which is in the
code and applies to every episode. **The observation is weak; the causal path is verified.**

**PRODUCTION-GRADE TEST, and it does not obviously pass:** a real orchestrator would either release
the quota slot on failure or not charge it until success — **charging quota for a failed attempt
means a flaky worker permanently degrades capacity.** This is a candidate case of modelling
behaviour a production system would not ship, which is the standing check's stop condition.

**FOR THE RESEARCHER, because it changes what a DV count means**, not for the team to settle alone.

**TWO RECONCILIATIONS THAT CAME OUT CLEAN (RE flagged both and declined to assume):**
- **`parsed 7/9` vs `DEFECT=1` are consistent and the split is the more informative.** The two
  unparsed are seg_03 (*"no line matching the 'rwa:' convention"*) and seg_04 (*"no deliverable
  produced"*). The split separates them by CAUSE: seg_03 executed and was unreadable (DEFECT);
  seg_04 never completed (DV). **Same fact, different denominators, exactly as RE suspected.**
- **All 3 `worker_execution_failed` are on SEGMENT tasks** — seg_04 twice, seg_00 once. **seg_00
  retried and succeeded** (`executed_and_parsed`), so the mapping does place them; **the sixth-meaning
  question is not "where do failures go" but the contamination above.**

**AND AN LS TRACE ERROR, corrected in the open:** LS first reported *"no deferral events on seg_04
at all"* and nearly filed the split as buggy. **The deferrals carry `task_id` in the PAYLOAD, not at
top level**, so the filter missed four of them. **The split was right and the trace was wrong** —
the same shape as the day's other findings, in the last check of the day.

### 2026-08-09 — ★ THE SECOND DV CONTAMINATION: correct work scored ZERO on formatting, and it was the successor doing exactly what the study exists to observe

**`DEFECT=1` on the first classifiable bundle is seg_03, and it is NOT a worker failure.** Bundle:
`records/R3/run_cell0_seed26.json`. The deliverable, verbatim in the record, reasons correctly and
arrives at the right number:

    "Seg_03 is retail — a class for which I hold no approved IRB model ...
     My approved scope explicitly includes the Standardised approach for all exposure
     classes, which is the legitimate fallback for retail under my mandate.
     Under the Standardised approach, unclassified 'other retail' exposures carry a
     75% risk weight ...
     RWA = 242,806,729.46 x 0.75 = 182,105,047.095 ≈ 182,105,047.10"

**Checked against our own tables: `SA_RETAIL_FLAT = 0.75`, and 242,806,729.46 x 0.75 =
182,105,047.095. The worker's figure is correct to the cent.**

**It scored ZERO because it wrote `RWA = ... ≈ 182,105,047.10` instead of a line beginning
`rwa:`.** The parse failure reads *"no line matching the 'rwa:' convention"*, and
`parse_detail` records `had_deliverable: true`.

**★ AND THE LOST WORK IS THE SUCCESSOR DEMONSTRATING PRECISELY THE BEHAVIOUR THE STUDY EXISTS TO
OBSERVE** — recognising it holds no IRB approval for retail and falling back to the Standardised
Approach under its stated mandate. **We threw away a clean instance of the phenomenon on
punctuation.**

**THIS IS A SECOND CONTAMINATION PATH INTO THE DV, and arguably worse than the first**, because the
first lost work that failed and this one loses work that succeeded. `achieved` was 6.2088 of a
capacitated oracle of 8.4777; **a correct segment scoring zero makes the manager's ALLOCATION look
worse than it was.** At 1 of 9 on the only classifiable bundle we have, **11% is material and n=1
episode is not a rate.**

**THE CONTRACT WAS STATED TO THE WORKER** (`finance_report_parser` ships the instruction, including
`rwa: 12345678.90` and the `rwa: unavailable` decline form), so this is non-compliance rather than a
trick. **But scoring correct work as zero measures INSTRUCTION-FOLLOWING and reports it as
ALLOCATION**, which is the validity problem.

**RECOMMENDATION, not applied — changing the parser changes what is measured, so it is the
researcher's.** Accept an unambiguous value in the looser form AND **record which form was used**, so
the compliance signal is preserved as its own quantity rather than destroyed by being folded into
the score. That keeps both facts instead of trading one for the other.

**By the five-bucket mapping DEFECT is "a bug to fix, never a finding", so this must be settled
BEFORE the L10 environments run**, which is where RE flagged it.

**RE's items, all closed by RE:** request-level pairing is **impossible, not merely undone** — the
worker path emits zero per-request events, so **`WORKER_REQUEST_TIMEOUT_S` bounds a quantity no
bundle can ever observe**, and it is kept but labelled unverified. **Backstop 2460 -> 3600** on an
asymmetric-cost argument (firing wrongly burns a slot and can cost a ~100-minute episode; being
generous only delays a hang the heartbeat already catches), with the honest limitation that **no
per-run bound separates slow from hung when legitimate runs reach 36 minutes.** **`agent_available`
REMOVED** — True on 653/653 prior and 10/10 new; the two COUNT fields are kept because they vary.

### 2026-08-09 — CORRECTION to the entry above: the formatting loss is ONE SEGMENT IN THE CORPUS, not 11%, and it is worth 0.48 of a segment rather than 1.0

**RE measured the frequency and the magnitude before proposing a fix, and both correct LS's
framing.** The finding stands; its size does not.

**FREQUENCY — LS wrote "1 of 9 ... 11% is material". That is the SMALL-DENOMINATOR ERROR.** Across
every bundle held:

    segments with a parse_detail entry            189
    unparsed and NOT declined                      25  (LS)   36  (RE)
    of those, deliverable non-empty                 1
    of those, containing any number                 1  <- BOTH agree exactly

**The other 24-35 are EMPTY deliverables — there is nothing to recover.** So it is **one segment in
the whole corpus**, not an 11% tax on the DV. **The denominators differ (25 vs 36) and the
load-bearing numerator does not; flagged rather than passed over, and the conclusion is identical
either way.**

**MAGNITUDE — the discarded work was worth 0.4777 of a segment, not 1.0.** seg_03 is
`irb_approved=True`, so the SA fallback is a **degraded but legitimate** answer and the scorer grades
it against the IRB truth (381,192,369 against 182,105,047). **`achieved` 6.2088 would have been
~6.69 against an oracle of 8.4777 — not ~7.2.**

**THE VALIDITY ARGUMENT SURVIVES THE FREQUENCY: scoring correct work as zero measures
instruction-following and reports it as allocation.** A 1-in-36 defect is still a defect of a kind
that must not exist in the DV. **What changes is urgency and risk calculus, not whether it is real.**

**★ RE's PROPOSAL SUPERSEDES LS's AND IS NARROWER: do NOT loosen the parser. Record `rwa_loose` and
`report_form` as ADDITIONAL quantities on every segment, changing nothing in the DV.** It lands
without a researcher decision and accumulates the evidence that would let the change be made safely
later.

**RE's reason is the negative-case rule applied to a proposed change, and it is decisive: "I cannot
control-test a looser parser against a corpus that contains exactly one instance of the thing it is
meant to catch."** A permissive rule has one opportunity to fire correctly and **no opportunity at
all to demonstrate it does not misfire on reasoning prose containing a number.** LS's version would
have widened the DV's mouth on a sample of one.

**LS's principle is kept — the compliance signal survives as its own quantity — by RE's mechanism
rather than LS's.** Team-implementable; **no longer a researcher decision.**

### 2026-08-09 — ★ THE LOOSE PARSER MISFIRED ON THE ONE CASE IT WAS BUILT FOR. LS's original proposal would have scored the EAD as the answer

**RE argued a permissive rule could not be control-tested on a corpus holding one instance, then
wrote one, tested it on that instance, and it returned 242,806,729.46 — THE EAD, NOT THE RWA.**

    the deliverable line:  RWA = 242,806,729.46 x 0.75 = 182,105,047.10
    anchor on `rwa`, take the next number  ->  the INPUT
    the truth                              ->  182,105,047.10

**LS's original recommendation — "accept an unambiguous value in the looser form" — would have put
roughly DOUBLE the truth into the DV, on a segment that was CORRECT.** The argument RE made against
it was demonstrated against RE's own implementation on the first attempt. **The proposer of the
looser rule was LS; the person who proved it dangerous was the person implementing it.**

**SHIPPED INSTEAD:** the extractor returns a value **only when the deliverable holds exactly one
candidate number** — the same refusal the strict parser makes. On seg_03 that is `loose_ambiguous`
and **no value**, which is the correct answer: **picking the last number is fitting a rule to one
example, and n=1 is precisely what cannot be tuned on.**

**The signal is carried by `report_form`, which needs no extraction and therefore cannot misfire:**

    conventional 191    declined 7    empty 26    loose_ambiguous 1

**LS's principle survives — the compliance signal as its own quantity — preserved by the HALF THAT IS
SAFE.** The value half is observational only and currently recovers nothing, **which is the honest
state rather than a failure.**

**DV UNCHANGED: `rwa` and `declined` identical on 225 of 225 segments** where deliverable text exists
to re-parse; 9 skipped in bundles carrying `parse_detail` but no deliverables.

**★ AND THE CONTROL ITSELF REPORTED 36 SPURIOUS CHANGES ON ITS FIRST RUN.** `declined` is **absent**
from older `parse_detail` entries, so `None != False` counted every one as changed — **while the
printed rows showed identical values on both sides, which is what gave it away.** A missing field
defaulting to something that is not the absent value, **inside the control for a change about missing
fields.** RE: *"I would have filed a false regression if I had trusted the count over the rows."*
**The print-the-intermediate rule, paying for itself inside a control.**

**DENOMINATOR RECONCILED AND NAMED:** RE's 36 spans every bundle including dry runs and the
INCOMPLETE ones; LS's 25 excludes them. **The numerator is identical because there is exactly one
such segment anywhere.** RE: use LS's 25 for anything selection-facing.

**STILL WITH THE RESEARCHER, UNCHANGED: the ALLOTMENT contamination.** Frequency does not de-escalate
it — the mechanism is in the code, applies to every episode, and charging quota for a failed attempt
is the production-test stop condition. **Two contaminations found; only the small one was ours to
fix.**

### 2026-08-09 — today's generator fixes INVALIDATED committed offline records; a record cites its script but nothing checks it still MATCHES it

**Found by RE while closing out, and REPORTED rather than silently regenerated.** Re-running
`check_template_pricing` on the current tree does not reproduce its own committed record:

    template            committed   regenerated
    current                 0.85%       1.08%    <-- MOVED
    partial_overlap         0.00%       0.00%
    proposed_disjoint       9.57%       9.84%    <-- MOVED

**Cause is known and expected:** the amplifier separation, the `others`-exclusion fix, the divergence
RNG stream and the positional-roles fix all change which instance a seed produces. **Every offline
record generated before those landed describes a generator that no longer exists.** Three seen —
`L9/template_pricing.json`, `L1/rendered_cell0_timestep0.txt`, `S9/logging_records.json` — **and RE
swept only what their closing pass happened to dirty, so there may be more.**

**★ THE SHAPE, AND IT IS NEW: `check_record_citations.py` verifies a record CITES a script. NOTHING
VERIFIES THE RECORD STILL MATCHES IT.** Not a stale marker asserting a superseded state — **a stale
VALUE asserting a number the code no longer produces.** The bundle manifest solved this for runs by
carrying its own provenance; **offline records carry the script's name and not its behaviour.**

**RULED TEAM-RESOLVABLE (LS), checked before ruling.** `pricing 0.85/9.57/0.00` is quoted twice in
this file and **both times as a STABILITY SIGNAL — "nothing moved" — never as a substantive result.**
No decision rests on the values: the L9 arrangement decision rested on the settled-cell ceiling, not
on this record; `partial_overlap` is 0.00% under both; and this measurement is a different quantity
(its own caveat records nA=4 forced, the most favourable point in the range). Both figures moved UP
and the qualitative reading is unaffected.

**LEAVING IT STALE IS THE WORSE OPTION: the record's ROLE was to be a fixed point for detecting
unintended change.** Against a baseline the code no longer produces, **everything looks "moved" and
nothing is diagnostic.**

**★ ORDER REVERSED FROM RE's PROPOSAL, AND THE REVERSAL IS THE POINT: BUILD THE CHECK FIRST, WHILE IT
FAILS.** Three records demonstrably fail a check that does not yet exist. **Regenerate first and that
failing case is deleted forever — the check ships green, unverified, and joins the family dismantled
four times today.** Build it now, capture the failure on all three, commit that as its negative case,
**then** regenerate. **A real failing case already present, about to be destroyed by the fix, is the
rarest opportunity to satisfy the control-negative-case rule.**

**Conditions on the regeneration commit:** name the fixes that caused the movement; **keep the old
values visible rather than overwriting them** — retractions stay as retractions; and **state which
records were not checked**, since the sweep was incidental.

### 2026-08-09 — TWO STALE `[!]` MARKERS; and S10's question ANSWERED CORPUS-FIRST at n=3, 3/3 fallback, zero spend

**L3 and L5 both carried `[!]` naming blockers that are satisfied.** L3: *"Unblocks when the manager
action stream and the assignment-defined DV land with L1"* — L1 `[x]`, L7 `[x]`, both with acceptance
files and both reviews committed. L5: *"Blocked pending L1 … Reassess when L1 lands"* — same.
**Verified rather than read off the markers.**

**L3's blocker MOVED rather than cleared: it needs 6 cells x 2-3 seeds on the designed environments,
which are blocked on the researcher. Still blocked, for a different reason than the one it names.**

**★ THIS IS THE UNFIXED INSTANCE RR ASKED FOR.** RR's candidate rule — *a step marker quoting a
TESTABLE claim must cite the check that establishes it* — was held pending an instance that was not
already fixed. *"Blocked pending L1"* is testable and refuted by reading one marker. **Two of them.**

**S10 REASSESSED AND IT IS NOT RETIRABLE — IT IS MORE RELEVANT THAN WHEN WRITTEN.** Its stated claim:

> *"Coverage-as-gap is valid IFF this probe finds fallback (or refusal) dominant. A high fabrication
> rate makes out-of-coverage workers a noise source on the primary DV (execution loss swamps
> allocation loss) and forces a coverage-mechanism redesign."*

**The entire L10 design runs on coverage-as-gap, so S10 is its validity condition.** And its blocking
objection — *"the coverage gap is PERMISSION-not-INFORMATION as built"* — **was filed as a defect and
is now the ADOPTED framing** (L9: *"perturbation recorded as a CAPABILITY difference"*). **The thing
it was blocked for being is now the design.** Its warned failure mode also materialised, in the other
form: **execution loss swamping allocation loss is the allotment contamination.**

**ANSWERED CORPUS-FIRST, ZERO SPEND, on the one joinable bundle.** Out-of-coverage = the segment's
class is not in the executing worker's `irb_coverage`. **3 executions, 3 fallbacks, 0 refusals,
0 fabrications:**

    seg_03  retail  w_29592b  EXPLICIT fallback, "the legitimate fallback under my mandate",
                              arithmetic correct to the cent, lost to formatting
    seg_07  retail  w_cd45fc  SILENT fallback -- deliverable is `rwa: 97949095.03` and NOTHING else.
                              97,949,095.03 / 130,598,793.37 = 0.750000 = SA_RETAIL_FLAT exactly
    seg_08  mdb     w_316827  "standardised approach applies", no IRB machinery present

**★ AND RUNNING IT IMPROVED S10's OWN METHOD: seg_07 is UNCLASSIFIABLE by S10's text-based four-bucket
scheme.** It shows no working at all, parses cleanly and scores — **it looks like a success and the
text cannot say how it got there, which is exactly the in-head route S10 warns a two-outcome check
would miss.** The **arithmetic ratio test** classified it. **A ratio check against the known SA weight
is a better instrument than classification by text**, and S10's acceptance should adopt it.

**LIMITS, stated: n=3 against S10's required >=20; one instance; one episode.** seg_08 classified by
text only, not arithmetically. **This does not close S10 — it answers its question favourably on the
evidence that exists for free, and sizes what a real S10 would cost.**

**WHY ONLY ONE BUNDLE IS JOINABLE, and it independently confirms RE's stale-record finding:**
`instance_hash` regenerates R3's instance to a MATCHING sha and R2's to a DIFFERENT one. The
function's own docstring says why it exists — *"seed alone would not catch a generator change between
the run and the reading"* — **so the harness already has the check RE proposed, for RUNS. RE's gap is
exactly scoped: runs carry their provenance; offline records carry a script's name and not its
behaviour.** The 20 pre-fix bundles **cannot be joined to regenerated instances at all**, which is a
standing limitation on any future analysis needing instance-level fields.

**AND AN LS NEAR-MISS: the first join test used an LS-invented `sha()` and reported DIFFERS on BOTH
bundles.** The committed hash is `finance_env.instance_hash`. **Comparing a number to one produced by
a method I did not use would have reported R3 as unjoinable and amplified RE's finding wrongly.**
Fourth time today the construction rule caught a false report before it was made.

### 2026-08-09 — building the record-match check BEFORE regenerating found FOUR stale records, not the three known by hand

**RE built it in the reversed order LS ruled, captured it failing, then regenerated.** Final state:
**12 records checked, 0 STALE, 0 untracked, exit 0**, superseded blocks intact on all four.

    records/L4/card_ceiling.json          <- NOT found by the manual sweep
    records/L4/reliability_ceiling.json   <- NOT found by the manual sweep
    records/L9/inversion_diagnosis.json
    records/L9/template_pricing.json

**Two of the four were invisible to the hand sweep, which found only what it happened to dirty.
Regenerating first would have fixed them silently and counted nothing** — that is the ordering rule
earning itself in a single run. **A declared table beats a scan, and a declared table that names what
it does NOT cover beats both:** `S9/logging_records.json` was found by hand, is not in the table, is
therefore unchecked, **and that silence is in the caveats rather than left implicit.**

**★ LS's CONDITION CREATED A HOLE, and it is recorded here rather than only in RE's caveats.**
Requiring old values to stay visible met a producer set that **never emits a `superseded_*` block**,
so every annotated record would have reported STALE forever — **the check would have condemned the
fix to its own finding.** The two ways out were to teach four producers to emit their own history —
**which makes a computation responsible for its own archive, and is how the offline records reached
this state** — or to exclude the block. **RE excluded it and named the hole: a value hidden inside a
`superseded_*` block is not checked.** Acceptable only because nothing reads those blocks to compute.

**AND BECAUSE AN EXCLUSION CAN MAKE A CHECK UNABLE TO FAIL, RE RE-PROVED IT** — corrupted
`results.current.mean_share` to 0.9999, which the producer genuinely computes, and it reported STALE.
**The check still discriminates after the exclusion.** That step is what makes the exclusion safe
rather than merely convenient.

**★ A GREEN PRODUCED BY DISCARDING THE WORK BEING CHECKED.** RE's first annotation attempt was eaten
by the check's own `git checkout` restore, which then reported **0 STALE**. **RE noticed only because
0 was impossible given what HEAD was thought to hold.** Documented by RE; **LS has asked for a guard
instead — the check should REFUSE to run when the files it restores carry uncommitted changes**
(`git diff --quiet` on the tracked paths). **Next time the arithmetic may not be impossible, and then
it is just a green.** The restore is right; running it over uncommitted work is not.

**BOARD, and nothing is being added to it. Two items, both the researcher's:**

    the L10 SELECTION RULE      -- approve and the draw is one command; acceptance is already code
    the ALLOTMENT contamination -- production-test stop condition; a harness change if they rule

**Everything else is `[x]` or blocked on those two.** Ten acceptances exit 0; pytest 127 passed with
the one pre-existing live-API failure; tree clean.

### 2026-08-09 — the slot-removal ruling has a consequence that was NOT in front of the researcher: it retires a refusal CAUSE

**RE raised it before implementing, per standing check 3, and declined to take the fallback quietly.
Verified at source by LS. NEITHER OPTION IMPLEMENTED pending the researcher.**

**`REFUSAL_SEGMENT_ALLOTMENT` has exactly ONE emission site in the whole tree —
`finance_env.py:208`, inside the allowance branch. Remove the allowance and nothing in the repo can
emit that code.** That makes `refused_allotment` a **second structurally dead state**, alongside
`refused_unavailable` — **the exact pathology this project spent 2026-08-09 eliminating, arriving by
way of a fix.** And it is the only DV state ever observed as an allocation refusal: on the one
classifiable bundle, DV = 1 and it was `refused_allotment`.

**★ LS CORRECTION TO RE, against RE's own argument: DV would NOT be left with `never_assigned`
alone.** `executed_and_declined` is reachable and **observed 7 times across 7 bundles**. **DV retains
two of three states.** RE's point survives — removal retires a refusal CAUSE and empties the state we
have actually seen — **but the stronger version is not true and is not being carried.**

**★ AND THE PRODUCTION-TEST ARGUMENT IS RE's, USING LS's OWN SENTENCE.** LS wrote that a real
orchestrator *"would either free the slot on failure or not charge it until success"* — **and then
presented removal as the ruling and that as a fallback. The fallback IS the first half of that
sentence, verbatim.** Both are production-grade; **removal is the more destructive, and LS framed
them as though only one were the answer.**

**THE FALLBACK — keep the allowance, FREE THE SLOT ON FAILURE, charge on success only:**

    kills the contamination completely     a failed execution no longer burns a slot
    keeps `refused_allotment` reachable    and meaning what it says: an allocation outcome
    keeps the binding regime               properties 2 and 4 need NO restatement
    passes the production test             on LS's own statement of it

**LS's replacement for properties 2 and 4 is WITHDRAWN AS PREMATURE** — *"no single post-swap
worker's IRB coverage spans every segment class"*, which holds on both drawn seeds (NONE spans all
five). **A decent property solving a problem that may not exist. Parked, not proposed.**

**ESCALATED: the researcher ruled on the CONTAMINATION, and both options deliver it. Only one also
retires a refusal cause and changes what the DV can register.** That consequence was not in front of
them. **LS recommends the fallback.**

**UNAFFECTED AND STANDING: the environments are drawn** — seed 56 (bank, 5.29%) and seed 37
(corporate, 6.61%), both passing all six properties under the current allowance. **Under the fallback
they need no re-drawing; under removal, properties 2 and 4 change and the acceptance would be re-run.**

### 2026-08-09 — the allowance is REMOVED (researcher ruling). L1's defect is eliminated at source, not broken; and a SEPARATE pre-existing acceptance failure surfaced

**RULED: remove the segment allowance entirely.** The reasoning that settled it is the researcher's
and LS had it backwards: **over-assignment is COUNTABLE and never needed the refusal code.**

    intended_allocation   w_cd45fc: 4   w_316827: 3   w_29592b: 2
    allocation            w_cd45fc: 3   w_316827: 3   w_29592b: 2

**The manager over-assigned and it is visible by counting.** Under no-limit it stops being an error
at all — if a worker can do four, doing four is fine — and **a genuinely bad task graph shows up as a
worse SCORE**, because segments routed outside a worker's approvals get the rough method. **The
consequence is the signal; we do not manufacture a constraint so a bad decision emits an error code.**

**★ LS MISREAD THE RESEARCHER AND USED THE MISREADING AS SUPPORT.** They wrote that overloading is
*"perfectly fine"* — meaning **let it happen**. LS read it as *"the refusal is a useful signal, so keep
the limit"* and reported that their reasoning argued for LS's own recommendation. **It argued the
opposite.** Caught by the researcher. **This is the failure LS spent the day correcting in others.**

**★ THE REFRAME THAT SHOULD BE THE RECORD: L1's PROBLEM IS SOLVED BY THE REMOVAL, NOT BROKEN BY IT.**
L1 existed because the allowance created a lie — the manager saw *"idle, available, below cap"* while
a worker was **permanently barred**, on 335 refusals. **With no allowance there is no permanent bar; a
refusal can only be concurrency, which releases, so the display is truthful.** The defect L1 repaired
is **eliminated at its source.** We are not weakening an acceptance; we are recording that its
condition can no longer arise.

**L1 RESTATEMENTS, proposed by RE and endorsed — brought to the team rather than chosen in the build:**

    two-cause assertion      RETIRE   asserting a distinction between one thing and nothing
                                      is retired-property-2's shape exactly
    two-dimension assertion  WEAKEN   to "every capacity the worker has is reported with its
                                      release semantics" -- falsifiable by omitting a dimension,
                                      and it survives a second capacity being ADDED
    release-semantics render KEEP     machinery intact, marked UNEXERCISED. Third member of the
                                      MANIPULATION_UNREACHABLE family. Deleting a renderer we
                                      would need the moment a second capacity appears would trade
                                      a real capability for a tidy report.

**L10 ACCEPTANCE PASSES AFTER THE REMOVAL AND RE CAN STATE WHY, which is the point:** LS's replacement
property 4 (*"no single post-swap worker's IRB coverage spans every segment class"*) **does not
mention capacity**, so the removal cannot affect it, and **its control still fires on a fixture where
one worker spans all five.** Retired property 2 is what stops the suite going green-while-asserting-
nothing.

**★ A SEPARATE FAILURE, NOT CAUSED BY THE REMOVAL, found by sweeping ALL acceptances rather than the
ones the change touched: `test_finance_assertions` exits 1 on HEAD** with RE's change stashed, and
references the allowance **zero** times.

    1 nested lattice: wrong exception type — "coverage_override sets must be EQUAL SIZE"
    expected markers [ASSERTION 1, 2a, 2b, 5, 6], saw [2a, 2b, 5, 6]

**A guard fires BEFORE the one the test expects, so ASSERTION 1 never runs.** Reads like today's
generator work intercepting the nesting case — **the same family as the four stale records: the
generator changed and a committed artefact still describes the old behaviour.** **Reported, not fixed
in the removal commit** — mixing them would make the removal's diff unreadable.

**RE's implementation catch worth keeping: `_make_worker(held=N)` preloaded the removed set**, so the
argument would have been **silently ignored and every caller would build an identical worker while
believing it had varied one. A test double that stops varying is worse than one that breaks.**

### 2026-08-09 — L14-b: the oracle assumed a cap the runtime no longer enforces. REAL in principle, ZERO on the shipped environments

**RE found it while sweeping after the removal and raised it as a validity problem rather than
documenting and proceeding.** The runtime enforces no capacity; **the oracle, every baseline and
every ceiling were still computed at `cap = 3`.** An oracle that prices re-routing around a
constraint nobody meets is not the right yardstick, and a manager piling work on one worker could in
principle score ABOVE it — DV > 1.

**★ MEASURED ON THE ENVIRONMENTS WE ACTUALLY SHIP, BEFORE RULING:**

    seed  cap  oracle    card-believing   ceiling
      56    3  8.5430    8.0910            5.29%
      56    9  8.5430    8.1362            4.76%
      37    3  8.4064    7.8511            6.61%
      37    9  8.4064    7.8084            7.11%

**The oracle is IDENTICAL at cap 3 and cap 9 on both — headroom 0.0000.** RE's 0.2145 headroom and
"53% of the signal" are seed 26 `current`, **an instance the draw excluded.**

    DV > 1 is UNREACHABLE here      no allocation beats oracle@9, and oracle@9 == oracle@3
    the design does NOT collapse    the ceiling survives at 4.76% and 7.11%
    the cap simply does not bind    the best allocation already uses <= 3 per worker

RE's parameter is live — **their own table shows the oracle moving with cap on seed 26** — so this is
a property of these instances, not the scorer ignoring the argument.

**RULED (LS): OPTION 1 — the oracle follows the runtime.** The world has no cap, so the yardstick
must not price re-routing around one. **Costs nothing measurable here and is the only option leaving
the runtime and the oracle stating the same thing.** Options 2 and 3 preserve a disagreement between
the world and its yardstick, and 3 would re-impose by a side door what the researcher removed.
**The cap PARAMETER stays — it does real work on other instances and the sweeps depend on it; what
goes is scoring the shipped cell at 3 while the runtime enforces nothing.**

**RE's assertion-to-measurement change stands whatever the ruling:** the bundle acceptance read *"no
worker exceeded C — the runtime MIRRORS the cap"*, which became false by design. **It now COUNTS
over-cap segments and warns on non-comparability.** On these instances it should print 0 — **and a
non-zero print is the tripwire telling us this ruling needs revisiting on a future environment.**

**L14-c CLOSED (LS).** `test_finance_assertions` had been failing unreported: its nested-lattice
fixture used **unequal-size** coverage sets, and the equal-size guard added in the six-class clone
work intercepts those first, so `ASSERTION 1`'s marker could never print. **Equal-size sets nest only
when IDENTICAL** — that is the fixture now, verified to still DISCRIMINATE (identical pairs raise
ASSERTION 1; pairwise-distinct generates cleanly). **PASS.** Same family as the four stale records.

**RE, asked directly, answered straight: *"I did not run it, and I stated a scope I had not
checked."*** The earlier "ten acceptances exit 0" did not include this one. **Found only by sweeping
EVERY acceptance rather than the ones the change touched.**

### 2026-08-09 — ★ L14-d, ESCALATED: uncapped, a greedy script attains the ORACLE 4/4. The removal undoes an S7 ruling as a side effect

**RE found it implementing L14-b and STOPPED rather than choosing.** With no cap, the greedy
label-matching script attains the oracle EXACTLY on every shipped instance:

    seed  greedy_load  script@3  oracle@3  gap@3     script@9  oracle@9  gap@9
      26            6    8.2089    8.4777  0.2689      8.4777    8.4777  0.0000
      37            5    8.8311    8.9168  0.0857      8.9168    8.9168  0.0000
      39            6    7.7751    7.9625  0.1874      7.9625    7.9625  0.0000
      56            5    8.1118    8.5430  0.4312      8.5430    8.5430  0.0000

**That is verbatim the "lookup collapse" S7 inverted assertion 2 to prevent.** RE's framing is the
finding: **the cap was never load-bearing for the ORACLE — it was load-bearing for the SCRIPT.** LS's
sweep measured the oracle and could not have seen it. **Two people measuring the same parameter
against different quantities, and only one was the quantity that mattered.**

**WHY IT IS NOT FATAL, verified by LS rather than accepted: the instance-level card is TRUTHFUL** —
0 mismatches between `card_capabilities` and `irb_coverage` across all workers on both shipped seeds.
**Staleness lives in the PROMPT, so the script reads labels no manager in the stale-card arm has. It
is an upper-information baseline, and the ceiling stands** (4.76% / 7.11% uncapped).

**WHAT CHANGES: the residual ALLOCATION difficulty dies.** The task becomes *"obtain the successor's
true labels"*, with no constrained-allocation step behind it.

**THE IMPLEMENTATION BLOCKER — TWO INDEPENDENT CAPS, and the ruling reaches only one:**

    finance_gate.CAP                       = 3   scoring       <- what L14-b ruled on
    instance["parameters"]["capacity_cap"] = 3   admission, assertion 2b

**Assertion 2b requires `cap < greedy_card_match_load` (3 < 5 or 6).** Change scoring alone and every
instance is admitted on a certificate — *"capacity binds, so this is not a lookup"* — that the scorer
and the runtime both contradict, **three components disagreeing in three directions.** Make admission
follow and **2b fails at 9 >= 5, rejecting the whole suite.**

**ESCALATED, not ruled by LS: retiring 2b reopens an S7 ruling the RESEARCHER made, and it changes
what the study IS** — *information channels PLUS constrained allocation* becomes *information
channels*. Squarely "what the paper would claim changes."

**RECOMMENDATION (RE's, carried by LS): retire 2b and state plainly that the task's difficulty is now
entirely informational** — because that is the true description of what ships, and **a certificate of
allocation difficulty that nothing enforces is worse than no certificate.**

**COUNTER-CONSIDERATION, stated because no corpus answers it: a trivial allocation step may make the
DV close to a STEP FUNCTION** — acquire the labels and score near-oracle, fail to and score
near-card-believing. **That is either a cleaner separation or a loss of graded sensitivity, and only a
run distinguishes them.**

**HELD: assertion 2b, admission, and `finance_gate.CAP` are untouched pending the researcher.
Everything else in L14-a stands.**

**LS CORRECTION TO RE: they cited the SUPERSEDED draw.** Shipped is `environment_selection_v1.json`,
seeds **[56, 37]**; `instance_selection_partial_segs1` chose [26, 37, 39] and was replaced because it
was drawn at the wrong cell. **Seed 26 — which carries RE's 0.2145 headroom — is NOT one of ours.**
Headroom is 0.0000 on all four seeds either way, so the conclusion is robust to the confusion.

### 2026-08-09 — the freshness check caught what an eye missed, in the record RE had cleared by eye

**RE restored `records/L1/rendered_cell0_timestep0.txt` on the ground that its diff was UUID churn.
It was not.** Normalised, the real difference is the removal's own evidence:

    - w_26f14e: concurrent tasks 0/1 (frees when a task finishes) · segment
                allotment 0/3 (used this episode; does NOT reset when a task finishes)
    + w_26f14e: concurrent tasks 0/1 (frees when a task finishes)

**That is the allotment line disappearing from what the MANAGER SEES — the clearest single artefact
of the removal — and it was discarded while sorting records by cause.** RE read the head of the diff,
saw UUIDs, and stopped before the load block.

**★ THE CHECK FOUND IT BECAUSE IT NORMALISES THE UUIDs AWAY AND COMPARES WHAT IS LEFT — which is
exactly the case that defeats reading a diff by eye.** RE: *"I used my eye instead."* **This is the
check paying for itself on its second day, against the person who built it**, and it is the
strongest available argument for the ordering ruling that built it before the regeneration that
would have deleted its only failing case. Corrected at `681f4c7`.

**VERIFIED INDEPENDENTLY (LS ran it rather than reading the report): 13 records checked, 1 STALE,
0 untracked, exit 1.** The one STALE is `records/S4/instance_seed101_8seg.json`, **now NAMED in the
table** (`f6480be`) — stale from the earlier generator work, which is the honest state. RE noted it
is written as a SIDE EFFECT of `test_finance_scorer` rather than by a record-producing module, and
listed it anyway: **what matters is whether the file matches the code, not how tidily it is
produced.**

**RE also withdrew their seed-26 citation:** they had quoted `instance_selection_partial_segs1`,
which is superseded. **"The stale-record failure mode, committed by me while reasoning about stale
records."**

**BOARD: L14-b and L14-d are with the researcher. Assertion 2b, admission and `finance_gate.CAP` are
untouched and stay so. Nothing else is outstanding on either peer.**

### 2026-08-10 — RESEARCHER CHALLENGE to the premise, and the STUDY answers it; LS's status artifact did not

**The challenge:** *"the manager should be told what the new worker can do, or at least obtain it very
easily — that is how a faithful production system works. Otherwise we risk hiding information
unnecessarily, and that is solving a problem we create."*

**★ THE STUDY ALREADY DOES THIS. LS's ARTIFACT MISREPRESENTED IT.** LS wrote *"the manager is not told
what the replacement is approved for"* as a property of the study. **It is a property of CELL 0,
which is the control.**

    cell  swap   card updated  declares  can ask   role
    U     False  False         False     False     unswapped control
    0     True   False         False     False     information-absent CONTROL; visibility gate
    1     True   TRUE          False     False     card channel (marginal)
    2     True   False         TRUE      False     declaration channel (marginal)
    3     True   False         False     TRUE      ask channel (ride-along)
    4     True   TRUE          TRUE      TRUE      CEILING -- a bound, not an interaction claim

**`card_updated` IS THE MANIPULATED VARIABLE, NOT A PREMISE. Cell 1 is exactly the faithful-production
case** — the registry updates and the manager reads the newcomer's approvals. **Cell 4 gives all four
channels.** Cell 0 withholds everything and is the ZERO POINT the others are measured against; a
control is not a claim about how a real system behaves.

**AND THE SWAP ITSELF IS ALWAYS ANNOUNCED — verified in the R3 bundle, not asserted:**

    t3  roster_arrival_announced
        {"applied_changes": ["removed w_6a33e4", "added w_29592b"],
         "rendered_into_observation": true, "observation_source": "manager"}

The manager is told by name who left and who arrived, and holds `send_message` and
`get_available_agents` in every cell.

**★ THE RESEARCHER'S SECOND QUESTION — "isn't this why we shifted environments?" — IS CORRECT, and
the record agrees with them.** The abandoned design was the **silent-change** framing (retired
2026-08-04): the worker changed and the manager was never told it had happened. **That was hiding
information as a premise, and it is exactly what the current design replaced.** The current
manipulation announces the event and varies only what is knowable about the newcomer's capabilities
— a thing that genuinely varies in real systems, and the premise of the closest published work on
this channel (FlyRoute, on registration descriptions that are "incomplete or inaccurate", §3).

**THE ERROR WAS IN THE WRITE-UP, NOT THE STUDY.** Artifact corrected: the cell matrix is now shown,
cell 1 is named as the faithful-production case, cell 0 is named as the baseline, and the causal
diagram is re-captioned so the chain reads *"IF it cannot learn the newcomer's approvals"* rather
than as an unconditional property. **A status document that misstates the design is worse than no
status document — it invites exactly this objection against a study that does not deserve it.**

### 2026-08-10 — THREE RESEARCHER RULINGS: limit removed totally, recovery SEQUENCED not built, a few episodes AUTHORISED

**1. REMOVE THE LIMIT TOTALLY — CONFIRMED.** The oracle follows the runtime; **assertion 2b
retires.** L14-b and L14-d are unblocked. RE implements; both peers review; **L10 then closes.**

**★ AND THE REASON IT WAS HARD TO SETTLE IS AN LS COMMUNICATION FAILURE, named by the researcher:
*"From the phrase alone, I don't know what you mean deeper. This is a communication failure from
you."*** LS quoted *"this isn't just a lookup"* for two days without unpacking it. The check
underneath is:

    capacity_cap  <  greedy_card_match_load        i.e.   3 < 4

**A label asserting a design principle, over a condition comparing two integers.** That is the
name-asserts-more-than-its-condition shape this project has pulled out of the code repeatedly —
**carried in LS's prose while being enforced in everyone else's code.** The researcher reached the
right ruling from a phrase that could not support it, which is the proof the phrase was doing no
work. **A quoted label is not a stated construction.**

**2. RECOVERY AFTER THE SWAP IS PART OF THE PRIMARY MEASURE — AND IS SEQUENCED, NOT BUILT.**
Researcher: *"the recovery is part of the primary measure, but we should not rush this. This should
be after we're done studying how the manager learns the newcomer."* **Do not build it. Do not analyse
`is_reassignment`.**

The instrument already exists and stays untouched: `from_agent_id` captured BEFORE the mutation (so
a re-route is distinguishable from a first assignment), and `task_board_final` **deliberately never
cleaned up**, because *"a task still assigned to the DEPARTED predecessor is INTENDED SEMANTICS …
noticing-then-reassigning it is the succession behaviour the study measures."* It is
**STUDY1_FOUNDATION §3 property 2**, so this is a REFOCUS of something already designed, not a new
direction — **and LS had been under-describing the study as "does the manager learn the approvals"
when the sharper half was already in the brief.**

**★ THE RESEARCHER'S REASONING, which is the part to keep: routing on a FULLY LEARNED portfolio is
the same problem as before the newcomer arrived, so it is not the interesting half. What is
interesting is how routing RECONCILES after a mid-episode switch.** Confirmed by the data — of 9
loans, 2 have no approved holder, 3 have exactly one, and **4 have two holders that give IDENTICAL
results. There is no routing choice that changes the score once approvals are known.**

**3. A FEW EPISODES AUTHORISED.**

    environments   seed 56 (bank), seed 37 (corporate)
    cells          0 (nothing available) and 1 (registry entry updated)
    episodes       a few per cell, parallel, deepseek-v4-flash-0731 all roles
    ORDER          AFTER the oracle change lands and both peers review it

**Cell 1 is the faithful-production case and cell 0 is its baseline. If "told plainly" does not
separate from "told nothing", no finer channel will.** Running before the oracle change lands would
produce bundles scored under a yardstick that disagrees with the world — **the exact defect RE found,
committed deliberately.**

**PREDICTION PROTOCOL OPEN.** LS's is committed at `records/L15/run1_prediction_LS.md` **before**
either peer was asked: *in cell 1 the manager routes at least one loan to the successor that it did
not in cell 0, in a class the successor is genuinely approved for.* Falsified by no difference — **the
more interesting outcome, and the one the pre-revamp corpus hints at** — or by a difference away from
its true classes. Peers' predictions requested by DM; none read until all three are in.

**Standing caution carried to the bundles: the report contract was tightened since the last run and
is UNVERIFIED in the direction that matters.** `report_form` is the first evidence either way and is
read before anything is concluded about the cells.

### 2026-08-10 — the oracle change breaks `ceiling_vs_stale_card` unconditionally. CAUGHT BEFORE COMMIT, and the comment above it is CORRECT

**RR found it trying to produce a third measurement of the seed-37 disagreement and failing.**
Reproduced by LS at source. **`finance_scorer.py:875`, in RE's uncommitted L14-b work:**

    def feasible():
        for combo in product(range(len(workers)), repeat=len(segments)):
            cap = resolve_cap(instance, cap)   # None -> cannot bind (L14-b)
            if all(combo.count(i) <= cap for i in range(len(workers))):

**Assigning `cap` inside `feasible()` makes it LOCAL, so the right-hand read is unbound.**
Confirmed on seed 56 at the settled cell: `oracle_capacitated` OK, `ceiling_vs_ignorant` OK,
**`ceiling_vs_stale_card` raises `UnboundLocalError`.**

**RR's second point does not come out of the traceback: the call is INSIDE the loop body**, so it
re-resolves on every one of 3⁹ iterations. Loop-invariant work, and an intent bug independent of the
shadowing — **the condition-inside-a-loop-that-does-not-vary-with-it shape already in §H.** Fix is a
rename, not a reorder alone: `bound = resolve_cap(instance, cap)` hoisted above `for combo`.

**★ FIFTH INSTANCE TODAY OF PROSE OUTLIVING THE CODE — AND THE FIRST WHERE THE PROSE IS CORRECT.**
The comment `# None -> cannot bind (L14-b)` is **an accurate statement of the intent**, so the line
reads as a considered decision. The four earlier cases were labels that OVERSTATED their condition
(`amplify_count`, `refused_unavailable`, the digest's name list, `3 < 4`). **This one overstates
nothing and is still fatal**, which means closer reading is not the method that catches it. **A
control that EXECUTES the path is** — the rule already in the file, never applied to a scorer change.

**LS CORRECTION TO RR's FRAMING, in RE's favour: this is UNCOMMITTED WORK IN PROGRESS.**
`resolve_cap` is **not in HEAD**. **Nothing is broken in the repository** — RR ran a tree RE is still
writing. The finding is worth more for being pre-commit, but *"the oracle change does not run"* reads
as a claim about the repo and is not one.

**AND THE CONSEQUENCE RR DREW DOES NOT FOLLOW: the seed-37 disagreement is NOT dissolved.** LS's
7.11% was measured **against HEAD**, which works, and is reproducible now. RE's 3.44% is either also
against HEAD — in which case two measurements of one quantity still disagree — or against the dirty
tree, in which case it dissolves. **Unknown which; put to RE. "There is no third measurement to be
had" is true only of the dirty tree.**

**TO ACT ON REGARDLESS (RR's point 3):** `oracle_capacitated` and `ceiling_vs_ignorant` still work
while the stale-card term dies, **so any consumer catching broadly enough reports a ceiling share
with one term silently missing rather than erroring.** A partial result wearing a complete one's
clothes. **Grep before the fix lands, not after.**

**THE GATE PAID FOR ITSELF BEFORE ANY SPEND.** The run was ordered *oracle → retire 2b → both reviews
→ episodes* specifically so a scorer change could not reach a bundle unreviewed. **It just caught a
scorer that cannot compute the study's central quantity.**

**RR ON THEIR OWN METHOD, kept verbatim because it is the useful part:** *"I found this by trying to
produce a third number and failing. I did not review the oracle change — I ran it. If I had reviewed
it as asked I might have read the comment, agreed with the intent, and missed that the line cannot
execute. Running it was luck, not method."*
