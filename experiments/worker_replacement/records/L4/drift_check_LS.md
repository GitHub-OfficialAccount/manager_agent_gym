# L4 — DRIFT CHECK against STUDY1_FOUNDATION.md (LS)

**Standing checks for this step.** *Production test:* n/a — L4 is analysis, nothing is built.
*No drift:* L4 IS the drift check. *Ambiguity:* none; the four sub-questions are specified.

**CONTAMINATION DISCLOSURE, stated first because it affects how this should be weighed.** I told
RR I would not read their independent L4 reading until mine was written. **That was already
false when I said it** — their reading arrived inside a DM I had read in full. So on questions
(ii) and (iii) I am NOT independent: RR reached the inside-but-moves-the-boundary conclusion
first and I am building on it, and I say so at each point. **D1 and D2 below are mine** — RR
raised neither, and they are the two findings that matter most.

---

## ★★ CORRECTION (RR review, verified by LS) — D1's HEADLINE EVIDENCE WAS FALSE, AND I PRODUCED IT WITH THE EXACT FAILURE MODE I COMMITTED TO THE RULES FILE

**I wrote "`rerouted_share` appears NOWHERE in the codebase. Grepped; zero hits." That is
false.** Recursive grep returns **19 hits** (15 when RR checked, before
`check_reroute_recoverability.py` existed).

**How I got it wrong is the part worth recording.** My query was
`grep -rn "rerouted_share\|reroute" experiments/worker_replacement/*.py` — a non-recursive glob whose
every visible hit matched **`worker_replacement` in import paths and docstrings**, not the metric. I
read a screen of path noise as an absence and asserted a null. **No positive control** — which
is the rule RR wrote on 2026-08-08 and *I* committed to `METHODOLOGY_RULES.md` §B: *a query
asserting a NULL must first demonstrate a HIT on a case known to be positive.* Two days later I
broke it in a committed record and in a report to the researcher. Positive control run now:
`channel_effect_ceiling` → 36 hits, so the query shape works.

**THE ACCURATE FINDING IS RR'S, AND IT IS WORSE THAN MINE.** We built `rerouted_share`
(`check_announcement.py:222`), built a variance estimate for it (`check_variance.py:128–139`),
and built a **loud alarm for its absence** (`check_variance.py:224`: `!! PRIMARY DV ABSENT`) —
and the revamp to the finance environment dropped all three. **The alarm never fired because it
lives in the pipeline nobody runs.** A silent regression past our own tripwire beats an
omission.

**AND RESTORING IT WOULD REINSTATE THE ROOT CAUSE.** The old DV is COMPLETION-DERIVED
(`check_announcement.py:168–191`): the population is `completions`, so a task assigned to the
swap target and never executed leaves BOTH numerator and denominator — it does not count as
"not rerouted", it vanishes. **`rerouted_share` is therefore biased UPWARD exactly in the
capacity-refusal regime we have been living in — the same defect, in the same direction, as the
`allocation`-from-completions bug we retracted four claims over.** So: rewritten over
ASSIGNMENTS with an explicit predicate and denominator, never restored. RR's third point stands
as a limitation: CHECK-1's +0.611 allocation effect is this DV and must not be cited as
evidence a channel moves allocation, because its derivation is biased toward finding reroutes.

**MY CAUSAL STORY IS OVER-FITTED AND I AM CUTTING IT.** I claimed the aggregate-vs-behavioural
choice explains the week. RR tested it against the six retractions one at a time: **one is
DV-shaped, and that one (`allocation` from completions) would have happened IDENTICALLY under
the brief's DV, because the brief's DV is completion-derived too.** The other five are
population, comparator and mechanism errors. **The common cause of the week is not
aggregate-vs-behavioural; it is that we specify populations by NAME and check them LATE.** What
survives is the narrower design diagnosis: *we derive a decision quantity from an execution
record* — true of `allocation` and of `rerouted_share` alike, and worth the file. The
explanation sentence is retracted.

**D2 COLLAPSES INTO D1, and RR's merged version is stronger than either.** D2 was PREMATURE
rather than drift — my own text conceded the sequencing, then asserted the stronger diagnosis.
But underneath: four of the brief's five failure modes are MANAGER BEHAVIOURS, and **no manager
action is logged at all.** Thirteen event types across the 18 bundles, the only
assignment-shaped one a refusal; `create_task` is unlogged too — RR found the four created
tasks by diffing the board against the index, not from an event. **The merged finding: the
manager's behaviour is not recorded anywhere. Everything we hold is the environment's RESPONSE
to it.** That is also a revamp regression — `check_announcement.py:149` walks a
`manager_actions.json` the finance pipeline no longer produces.

**ADOPTED RECOMMENDATION (RR's, replacing mine):** (1) log the manager ACTION STREAM, not just
assignments; (2) define the behavioural DV over assignments from scratch; (3) land it **WITH
L1**, by criterion (e)'s argument — L1 makes the manager more able to act, action is what we
would be newly logging, and shipping separately buys a round of episodes where the manager
reacts more and we still cannot see it; (4) reinstate the `PRIMARY DV ABSENT` banner in the
finance pipeline — **cheapest item here and the one that would have caught this without either
of us.** RR's blocker on L3-as-scoped is accepted.

---

## D1 (SUPERSEDED ABOVE — retained per the no-overwrite convention; its first bullet is FALSE)

## D1 (as originally written) — THE BRIEF'S PRIMARY DV IS NEITHER IMPLEMENTED NOR LOGGABLE

§5 of the brief: *"Primary DV: the allocation margin (rerouted_share family) — **task
denominators, never worker denominators**."*

- **`rerouted_share` appears NOWHERE in the codebase.** Grepped; zero hits.
- **It is not recoverable from the bundles either.** The manager holds `assign_task` and
  `assign_tasks_to_agents` (both in `manifest.manager_action_types`), but **no event type
  records an assignment.** The only assignment-shaped event is `assignment_deferred` — a
  REFUSAL. We log the assignments that were rejected and not the ones that were made. All we
  retain is `task_board_final`, a terminal snapshot, so a task assigned once and a task
  reassigned three times are indistinguishable.
- **What we measure instead is a REGRET DECOMPOSITION** against a capacitated oracle, on score
  denominators.

**These are different quantities, and the difference is not cosmetic.** `rerouted_share` is
BEHAVIOURAL — did the manager move work off the newcomer. Regret is an OUTCOME that mixes
allocation with execution quality, coverage structure and capacity. A manager can reroute
heavily and lose little, or reroute nothing and lose a lot.

**This plausibly explains the whole week.** The three-way regret split was an attempt to
recover allocation BEHAVIOUR from an outcome AGGREGATE — and every failure in the review chain
was an un-mixing failure: non-routing that was capacity refusal; mis-routing conditioned on
execution; a coverage rate that needed the oracle's own rate to carry its sign. **The brief
specified measuring the behaviour directly, and we built the aggregate instead.** Measuring
`rerouted_share` requires logging assignment events, which is cheap and does not exist.

**Production test on the omission:** FAILS. No orchestration system in production logs only
rejected assignments and not accepted ones — assignment is the primary audit record.

## D2 (NEW) — THE MEASUREMENT VOCABULARY HAS DRIFTED FROM THE BRIEF'S FAILURE TAXONOMY

§7 makes phase 1 a **failure taxonomy per cell**, and names five manager failures: allocating
as if the predecessor remained; trusting the stale card; reading declarations without acting;
never verifying; never asking.

Our current taxonomy is `never-assigned / assigned-but-unexecuted / executed-but-unparseable /
parsed-and-wrong`. **Not one of the brief's five appears anywhere in it.** Ours is an
EXECUTION-STATUS taxonomy; the brief's is a MANAGER-BEHAVIOUR taxonomy.

The execution-status work was necessary — the instrument was broken and we could not have
known that without it — **but it is not the deliverable, and after a week it is the only
taxonomy we have.** No cell currently reports whether the manager trusted the stale card,
acted on a declaration, verified anything, or asked.

## D3 (ii) — INSIDE OR OUTSIDE? Outside as a channel. NOT INDEPENDENT (RR first)

RR's conclusion — outside the studied object, but it MOVES the boundary, so the claim is scoped
to *a regime where load is observable and constant across cells* — I accept and did not reach
first. Two additions that are mine:

- **The brief's own §3 property 3 quotes DRAMA's allocator as considering "agent capabilities,
  location, and **current workload**".** Pre-L1 our manager had NO workload signal. **So we
  were behind the nearest neighbour on an input the brief itself cites** — L1 brings the
  setting to parity with the work we position against, rather than adding something exotic to
  it. That is a stronger defence of L1 than study-integrity alone, and it belongs in the paper's
  setting description.
- **The pre-L1 suppression was NOT a constant offset across cells.** If a channel changes how
  much the manager concentrates, it changes the refusal rate, so the hidden term varies BY CELL
  and correlates with the manipulation. That is worse than "a second information failure" — it
  is a cell-varying confound, and it is why constancy (acceptance ii) is load-bearing rather
  than tidy.

## D4 (iii) — DV drifting toward instrument health? YES, further than RR's version

RR: not yet, but L3's reading limit is itself an instrument-health measurement; pre-register
that L3's numbers may not later be cited as channel evidence. Accepted. **I would put it more
strongly, because D2 shows the drift has already happened at the taxonomy level**, and because
two of the three next steps have tautological expected outcomes on the record — L1's "the
dominant loss should shrink" and L2's "`assigned-but-unexecuted` ≈ 0". Both are mechanical
consequences of the repair. **If either is reported as a phase result, instrument health has
become the finding.** RE flagged the L2 one themselves; the L1 one is mine and I wrote it into
the backlog, so I am the author of the risk.

## D5 (i) — THE FOUR-PROPERTY NOVELTY INTERSECTION HOLDS

Checked property by property against §3. (1) allocation decision held by one agent — untouched.
(2) newcomer inherits persistent state — untouched; descriptions still stale by succession.
(3) information interface beyond behaviour — the four channels are intact, and load is not a
fifth channel about the NEWCOMER (RR's checked-and-dropped finding: refusal cannot leak
coverage, since nothing refuses on scope and the allotment has no per-worker override).
(4) exogeneity — untouched. **The brief's own wedge is (2)+(3), and L1 touches neither.**

## D6 (iv) — DOES THE SURVIVING CLAIM ANSWER THE BRIEF'S QUESTION? NO, and it should not be sold as if it did

Surviving claim: *in a regime where capacity binds exactly, coverage information alone cannot
address the dominant allocation error; the channels are orthogonal to the dominant loss term.*

The brief asks *which sources of information about the newcomer actually change the manager's
decisions.* **The surviving claim is a BOUNDARY CONDITION on the study — it says what the
channels cannot reach. It is not an answer, and it is currently the only firm result we hold.**
The risk is obvious and worth naming in advance: a boundary condition that is the only solid
thing in the record tends to become the headline. It belongs in the setting/limitations, not in
the contribution.

---

## What I recommend, in priority order

1. **Log assignment events and implement `rerouted_share` before L3.** Without it, L3 re-measures
   the same aggregate that has already produced four retractions. This is cheap and it is the
   brief's own primary DV. **I am NOT ordering it unilaterally** — it changes L3's scope, so it
   goes to RE and RR first, and to the researcher if they disagree.
2. **Add the brief's five failure modes to what each cell reports**, or state explicitly that
   phase 1 has been re-scoped and why.
3. **Carry the regime qualifier into the brief itself**, not just into the thread.
4. Neither (1) nor (2) blocks L1's fixes, which stand on their own.
