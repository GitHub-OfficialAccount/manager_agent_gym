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

## L9 — THE TEMPLATE DECISION: price partial overlap, then choose `[!] BLOCKED ON THE RESEARCHER (team side CLOSED, standing rule 7 satisfied). At the realistic mix, natively: current 0.000%, partial overlap 2.258%, disjoint 5.272%. LS recommends partial overlap -- no sixth class, no roster change, ships unamplified. Nothing further the team can do without the choice.)`
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

## L2a — the split CODE against the repaired schema `[~] TWO OF THREE FIXED. B2 (executed segment absent from parse_detail -> classified executed_but_unparseable) is STILL SILENT while the acceptance reports PASS -- RR re-ran the named case rather than reading the report. Does the acceptance fixture even REACH the B2 branch? If its parse_detail is complete it cannot, and it would pass indefinitely.`
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
    L2a  [~]  B2 with RE
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
