# Scope run — which interim claims survived, and which did not

Every quantitative claim made while the run was in flight, with what happened to
it. Both authors' claims are here; three of the corrections were to things the
lead had already passed upward, and those are marked, because a ledger that only
records the research engineer's errors would misdescribe how the round went.

FINALISED AT 18 of 18 episodes. Figures below are the n=18 values.

---

## Claims that SURVIVED

| # | Claim | Author | Status at 18 |
|---|-------|--------|--------------|
| 2 | **The stale card cannot bite**, structurally, in every instance — both of its errors are costless | LS | held; verified independently on all three study seeds |
| 3 | **Half the units cannot discriminate** — ~0.50 across 24 instances, 57% traced to the SA-applicable fraction | RE | held |
| 4 | **"Non-routing is a large share of regret"** | LS flagged, RE measured and named it | **WITHDRAWN — THE LABEL WAS FALSE.** The term is real (48.3% at n=18) but it is not non-routing. All 22 segments carry a real `assigned_agent_id`; ZERO were never assigned. The manager routed every one and the engine never executed them — 580 `assignment_deferred` events, workers at `max_concurrent_tasks=1`. It is CAPACITY STARVATION. Root cause is a defect in my runner: `allocation` is derived from COMPLETIONS, so an assignment that never executed structurally could not be represented and collapsed to `__unstaffed__`. |
| 5 | **A band exists** separating faithful-approximate from fabricated | LS asked, RE measured | held — on a *better* argument than first given (below), and now with 2 segments inside the band rather than 0, which weakens the "empty region" argument slightly without overturning it |
| 6 | **The empty middle**: covered ASRF errors are bimodal | RE | **HELD BUT SOFTENED at n=18.** 51 of 82 within 5%, 29 above 15% — and the middle is no longer strictly empty: 2 segments landed in 5-15%. The bimodality holds and 95.1% of covered loss is still above a 15% band; "nothing between" was an n=52 statement and is now "almost nothing between". |

## Claims that were RETRACTED or CORRECTED

| # | Claim | Author | What happened |
|---|-------|--------|---------------|
| 4c | **"The allocation error is a live channel-sensitive effect"** | LS | **WITHDRAWN BY LS.** Over-concentration is LOAD-BALANCING; every channel built here carries COVERAGE. Knowing what a newcomer can do says nothing about how much has already been given to someone. The capacitated-oracle and selection-effect corrections stand; the inference from them does not. |
| 4b | **"The channel-sensitive term is essentially empty"** / "the manager routed all but one unit as well as the oracle" | RE | **WITHDRAWN.** Both rest on a per-segment metric that cannot see the dominant allocation error. THE ORACLE IS CAPACITATED: with 9 units, 3 workers and C=3 its shape is necessarily 3/3/3. The manager's allocation VIOLATES that in **13 of 18 episodes** (shapes to 6/2/1), and the median episode then sat **15 idle timesteps** in which reassignment would have fixed it. Assigning a unit is not routing it well; over-concentrating on one worker IS the allocation error, and it is the one that costs 48.3%. |
| 6a | **"Mis-routing is exactly zero"** on staffed-and-discriminating segments (0 of 33 at 10 episodes) | RE (carried upward twice by LS) | **FALSIFIED. Final: 1 of 66.** **CORRECTED FIGURE: 3 of 105 assigned (2.9%)**, with executed-only 1 of 83 (1.2%) reported BESIDE it, never replacing it — the unexecuted set is 2 of 22 (9.1%), several times enriched. 15 sole-held-class segments are excluded because no correct choice existed there by design; counting them would have produced a ~10x-wrong figure and measured the generator rather than the manager. **AND THE EXECUTED-ONLY NUMBER CONDITIONS ON THE ALLOCATION HAVING WORKED** — a selection effect I presented as a virtue ("the defect never touched it, it was computed over segments that EXECUTED"). The 22 excluded segments are precisely the ones where the allocation failed. 1/66 is a valid statement about executed segments and about nothing else. The single case is a failure to ACT on CORRECT card information — cell 0, seed 36, a BANK segment, and bank is the shared class, so the stale card correctly stated the successor covered it. Evidence about card CONSUMPTION, not content. The conclusion it supported is unchanged: one segment at 0.48 against ~30 total regret leaves the channel-sensitive term essentially empty, and this case is not one a channel manipulation could have moved. |
| 7 | "At 24% of the spread the two σ's answer different questions" | RE (adopted by LS over their own framing, and carried to the researcher) | **RETRACTED.** An artefact of df=2. At df=6 the gap reversed to −0.006. The two components are anti-correlated (r = −0.42) because they partition the same nine units, so no gap was predicted in either direction. A percentage should never have been put on a two-degree-of-freedom estimate, labelled df or not. |
| 8 | "Essentially all regret is failure to staff" | LS | **CORRECTED.** It is ~52% non-routing *and* ~51% execution. Execution became the largest single component. Both are channel-insensitive, so the conclusion held by a different split — but the correction made the picture worse, not better. |
| 9 | "Channels cannot plausibly affect staffing" | LS | **DOWNGRADED** to an assumption. Partly testable and not established; carried at that weight. |
| 10 | "The compute tool repairs the primary instrument (the only route to a working detector)" | RE (passed upward by LS) | **RETRACTED.** A band recovers 60% of covered segments today at zero cost. The 100% false-positive rate was a *tolerance artefact*, not an environmental limit — I had implied it could not be fixed by tuning. It can. |
| 11 | "The compute tool attacks 63% of execution loss" | RE (from LS's inference) | **RETRACTED.** 96.6% of covered loss sits above a 15% band, in a population that is not precision-limited. A calculator addresses the ~3% in the 1–5% band. |
| 12 | The C1 repair is a **lattice** change | LS | **CORRECTED.** The lattice does not choose the swap pair; `_designate_swap_pair` searches for a two-holder class and reimposes a shared pair on any lattice. The defect is in the *designation rule*, and the repair needs three coupled changes plus a schema consequence. |
| 13 | "In-head ASRF cannot hit six significant figures" ⇒ the computation is poor | RE | **HALF RETRACTED.** The first clause held (0 of 52 at 1e-6). The implication did not: 27% land within 0.1%, median 3.8%. *"27% within 0.1%" and "52 of 52 failed" describe the same data* — which is the whole lesson about identity tolerances. |
| 14 | The band is safe because the 5–15% plateau is flat | RE | **REPLACED BY A BETTER ARGUMENT.** The plateau argument rested on n=6 fabricated points. The surviving argument is structural: the band sits in a genuinely *empty* region of the covered distribution, so it separates two populations without cutting through either. Same number, defensible reason. |

---

## What the C1 repair is actually for

Recorded because the justification changed and the second one is stronger.

The repair was proposed on "the manipulation has no content". The better argument
is that it **converts an unanswerable question into an answerable one**. As built,
an accurate stale card plus a correctly-routing manager is uninformative: *"reads
the card and follows it"* and *"ignores the card entirely"* predict IDENTICAL
behaviour. That is the confound this run is stuck in, and it is why the three
competing explanations for stale-cells-matching-updated-cells could not be
separated.

After the repair the card MISLEADS on the load-bearing class, so the hypotheses
come apart:

* route correctly ⟹ the manager is **not** consuming the card — a finding, and
  the study's own subject;
* mis-route ⟹ the manager **is** consuming it — also a finding, and the one the
  design assumed.

Either outcome is informative. Nothing the current environment can produce has
that property.

## The defect that produced the most wrong statements

`allocation` was built by walking COMPLETIONS. A segment the manager assigned and
the engine never ran could not be represented in that dict at all, so it became
`__unstaffed__` — a label that reads as *"the manager never staffed it"*.

Everything downstream inherited the error: the three-way regret split's largest
term, the "non-routing dominates" reading, the inference that channels cannot
affect staffing, and the framing that the manager "fails to staff ~17% of units".
The manager assigned all of them.

**Why no check caught it.** Every assertion in this build tests the *scorer's*
requirements — that the allocation covers every segment, that reports match the
allocation, that regret decomposes exactly. `__unstaffed__` satisfies all of them.
The field was internally consistent and externally false, and a check written
against the scorer's contract cannot see a value that meets the contract while
misdescribing the world.

**Fixed** by building the intended allocation from the ASSIGNMENT record and
splitting the outcome four ways:

| state | n (18 episodes) |
|---|---|
| never_assigned | **0** |
| assigned_but_unexecuted | **22** |
| executed_but_unparseable | 7 |
| executed_and_parsed | 133 |

Old bundles are reconstructed from `task_board_final` + `parse_detail`, so nothing
is re-run.

## The finding that reframes the study — SURVIVING FORM

The anti-correlation claim was asserted, verified arithmetically, and then
**WITHDRAWN**. What survives is narrower and still consequential.

**SURVIVES (a):** coverage-optimal allocation CONFLICTS with capacity. The
uncapped per-segment argmax exceeds the cap on all three instances.

**SURVIVES (b'), and it is BETTER evidence than (b) because it is about the
FAILING segments specifically:** splitting the 22 unexecuted by final board
status —

| | n | coverage-relevant | mis-routed |
|---|---|---|---|
| capacity-refused (never started) | 20 | 20 | **0 (0.0%)** |
| timing cutoff (started, unfinished) | 2 | 2 | 2 (n=2) |

**Every overflow placement is COVERAGE-CORRECT.** The manager fills a covering
worker past capacity and the invisible constraint absorbs the cost. And the
pooled ~9% figure I reported describes NEITHER population — it must not be
quoted, including where it appears to support the account.

**SURVIVES (b):** the over-concentration is coverage-CONSISTENT — 54 of 58 IRB
segments piled on over-loaded workers are covered by that worker (93%).

**WITHDRAWN — the direction.** "Coverage channels are ANTI-CORRELATED with the
dominant error" does not follow. The argmax establishes a CONFLICT, not a
DIRECTION: a manager given coverage information does not thereby *lose* capacity
information, and would compute the CAPACITATED optimum rather than the argmax.
The argmax is the strongest form of one input, not the natural consequence of
supplying it. And the empirical direction points the other way or nowhere — cell 4
(all channels) ties cell 0 (none) at the bottom of the max-load table.

**WITHDRAWN — "6x more coverage-faithful than optimal play."** The arithmetic is
exact and the comparison is invalid: it compares a FEASIBLE allocation against an
INFEASIBLE one. The optimum's 1.00 mismatch per instance IS THE PRICE OF
FEASIBILITY; the manager did not pay it because its allocation violates the cap.
Coverage fidelity bought by breaking the constraint is not fidelity.

**KEPT:** the comparator itself. 3-of-105 alone carries the wrong sign. Its
caption is now *"the optimum accepts one mismatch per instance as the price of
feasibility"* — never *"the manager beat the optimum."*

**SCOPE, which now attaches to the surviving claim:** C=3 with 9 units and 3
workers binds EXACTLY, so the conflict is a property of THIS regime. With slack,
coverage and feasibility would not compete. Without this the result reads as
"coverage channels are useless", which is far larger than the measurement.

**EVIDENCE BASE, which must not share a paragraph with the episode results:**
(a) and (b) are OFFLINE properties of THREE STRATIFIED INSTANCES — one of them
the suite minimum, not a random draw. The 18 episodes buy nothing for them.

### Cell U — the exact correspondence

Verified independently after LS retracted a looser version of it. In all three
cell-U episodes, the spare capacity among the workers ACTUALLY PRESENT matches
the unstaffed count exactly:

| episode | loads (present workers) | spare slots | unstaffed | match |
|---|---|---|---|---|
| U/seed 23 | 6 / 2 / 1 | 3 | 3 | yes |
| U/seed 3  | 5 / 2 / 2 | 2 | 2 | yes |
| U/seed 36 | 5 / 2 / 2 | 2 | 2 | yes |

The manager piled 5–6 units onto one worker while two present workers had
precisely enough room for the overflow.

**A RETRACTED VERSION OF THIS REACHED THE RESEARCHER** — that "a worker on the
roster was given nothing at all". The zero-load worker in each case
(`w_3330c6` / `w_e350ed` / `w_002c52`) **never ran anything in the episode**:
`roster_post_swap` is a COUNTERFACTUAL field for cell U, which carries no swap.
The worker being pointed at was not on the team. Cells 0–4 are unaffected —
`roster_post_swap` is their real roster.

Same root cause as both denominator discrepancies: a FIELD NAME standing in for a
predicate that was never stated.

### What goes to the researcher

> Coverage information alone cannot address the dominant error, and on these
> instances — where capacity binds exactly — coverage-optimal play would itself
> violate capacity. The channels are ORTHOGONAL to the dominant loss term, and
> the input that would address over-concentration is LOAD, which none of the
> built channels carries.

## What the pattern says

Seven failure modes recurred, and none of them is carelessness:

1. **A missing wire does not announce itself when absence and zero look alike.**
   Twice the correct logic existed one module away and was never read — the
   U-oracle phase, and the decline counts. Both times the missing value had a
   plausible default: an oracle matching the other cells, a `None` reading as
   "none occurred". Both were found by *reading output*, not by a check.

2. **A defect whose signature is EQUALITY wears the shape of a passing check.**
   Every comparability assertion in this build exists to confirm equality across
   cells, so the U-oracle bug — wrong precisely by matching the other cells —
   would have been applauded by the check-shaped defence.

3. **A metric that conditions on success cannot measure failure.** Per-segment
   mis-routing was computed only over segments that EXECUTED — excluding exactly
   the segments where the allocation failed — and I offered the exclusion as
   evidence the number was robust. Same family as the denominator errors.

4. **A field can satisfy every check and still misdescribe the world.**
   `__unstaffed__` met the scorer's contract exactly — covered the segment set,
   scored 0, decomposed exactly — while asserting something false about who did
   what. Checks written against an internal contract cannot detect a value that
   honours the contract and lies about reality.

5. **A discrepancy you can explain is still a discrepancy.** My argmax
   tie-breaks gave 7/1/1 where LS's gave 8/1 on the same instance. I reported the
   difference, said "conclusion identical", and moved on — when the instability
   was itself evidence the construct could not carry a directional claim. LS
   treated a 10x discrepancy as a signal to investigate; I treated a shape
   discrepancy as a footnote.

6. **A rate without its comparator can carry the wrong sign.** "3 of 105
   mis-routed" sounds like failure until the capacitated optimum's own rate (6x
   higher) is put beside it. Four numbers this week needed a comparator to mean
   what they appeared to mean.

7. **Small-n estimates acquire authority by being quoted.** Claim 7 was labelled
   df=2 and travelled anyway. Labelling the degrees of freedom did not stop the
   number being carried upward; only retracting it did.
