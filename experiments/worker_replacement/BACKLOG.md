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

## L9 — THE TEMPLATE DECISION: price partial overlap, then choose `[ ]`
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

## L2a — the split CODE against the repaired schema `[~] (built fd42a82; LS blocker fixed 0720cf3 and verified; LS PASSES; awaiting RR review file)`
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

## L8 — Retire the display-name join, and log renames `[ ]`
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

---

## L3 — Re-measure at scope: does an effect appear once the instrument is honest? `[!]`
> **BLOCKED (RR, accepted by LS).** As scoped this re-measures the same regret aggregate that
> produced four retractions, without the behavioural DV. Unblocks when the manager action
> stream and the assignment-defined DV land with L1.
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

## L5 — S10 and S11: reassess, do not resume blind `[!]`
**Blocked pending L1.** S10 (fabrication linchpin probe) was blocked on the coverage-repair
ruling, which R1 resolved; S11 (gate pair) never started. **Both were specified against an
environment that lied to the manager.** Do not resume either from the archived backlog without
re-reading its acceptance criterion against the repaired environment. Reassess when L1 lands.

---

## L6 — §B enforcement: population predicates in reported quantities `[~] (all three blockers fixed — LS's at de32dff, RR's two at e3f4e78 with the range rule; LS PASSES; RR's review file is on record but its verdict PREDATES the fixes and has not been lifted)`
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
