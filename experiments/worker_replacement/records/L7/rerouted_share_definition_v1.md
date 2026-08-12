# `rerouted_share` — definition v1, for LS and RR review BEFORE implementation

**Status:** proposed, not implemented. The logging half of L7 is built and
positive-controlled (`task_assigned`, all four apply sites, all three skip paths).
The DV itself waits on this document being ruled on.

**Why it is being circulated first:** the metric has changed shape twice in two
days — from "count reassignments" to "separate forced from discretionary" to
"condition the discretionary side on choice-set size". Each change came from
measurement, not argument. A third change discovered after implementation would
be a third rewrite of the primary DV, and pre-committing the predicate is the
habit that has caught the last four errors.

---

## 1. What is being measured, in one sentence

**Of the segment work the manager could have left where it was, what share did it
move to a different worker?**

## 2. Unit, numerator, denominator

**DENOMINATOR (LS's sharpened predicate).** Segment tasks that, at the moment of
some manager action, were assigned to an agent **still on the roster** and **not
yet terminal** — the set where leaving it alone was a legal option.

Work held by a departed agent is excluded because moving it is not a choice. Work
never assigned is excluded because there is nothing to reroute. Terminal work is
excluded because it cannot move.

**NUMERATOR.** Tasks in that set with **at least one DISCRETIONARY move** — a
change of assignee where the previous assignee was still present.

**UNIT: THE TASK, COUNTED ONCE.** `rerouted_share = |tasks moved| / |eligible
tasks|`. Move counts are reported separately and never divided by a task
denominator: my own first pass produced 29 and 33 for the same corpus because one
counted tasks-with-a-change and the other counted moves. Both correct, different
predicates, and a share mixing them can exceed 1.

## 3. The two populations, never summed

| | definition | n (18 scope bundles) | how it is analysed |
|---|---|---|---|
| **FORCED** | source agent has left the roster | 24 | by **destination** — successor vs incumbent |
| **DISCRETIONARY** | both agents present | 9 | by **share**, conditioned on choice-set size |

**Forced moves are NOT in the share** — they are not choices — **but they are not
discarded**, per LS's correction 2: their DESTINATION is a decision, and handing
the departed worker's queue wholesale to the newcomer is the brief's §7 failure
mode #1, "allocating as if the predecessor remained". Measured 22→successor vs
2→incumbent, against 1→successor vs 8→incumbent for discretionary — near-opposite
distributions.

**The choice-set check clears the forced side and constrains the discretionary
side.** All 24 forced moves had 3 capacity-legal destinations, so destination was
a real decision — but because forced moves land at t3–t6 before capacity binds,
not because capacity is generous. Discretionary moves happen later and have legal
sets of 1 or 2, never 3. **So the conditioning belongs on the discretionary side.**

## 4. Applied, not requested — with requested reported beside it

The DV is computed over **APPLIED** assignments: a request the engine skipped did
not change the allocation. But `applied=False` rows are reported as a named
diagnostic, because a manager that tried and was skipped is behaviourally
different from one that never tried, and collapsing them would credit the second
with the first's restraint.

## 5. Cell U

Cell U has no departure, so its FORCED population is structurally zero (measured:
0 of 0 across three episodes). That is not a finding about any channel and must
carry that sentence wherever the table appears. Its discretionary share is
computed on the identical predicate and is comparable. **U-vs-0 remains a JOINT
contrast** — swap plus roster change — exactly as `finance_cells.py` already
states for every other quantity.

## 6. Open questions I am NOT deciding alone

**Q1 — task or task-timestep denominator?** A task assigned at t3 and still sitting
at t20 offered many opportunities to move. The brief says "task denominators,
never worker denominators", which distinguishes task from *worker*, not task from
*opportunity*. **I propose TASKS**, as the plainer reading, but an
opportunity-denominator is defensible and would change the number.

**Q2 — a task with both a forced and a discretionary move?** **Proposed and
RULED:** it is in the denominator (it was eligible at the discretionary moment)
and contributes to the numerator only for the discretionary move. It also appears
in the forced destination table. One task in two analyses, correct, never summed
across them.

**NOT AN EDGE CASE — RR measured it: 3 of the 9 discretionary moves are on tasks
that also had a forced move. This rule therefore determines a THIRD of the
numerator**, and is recorded here as a measured quantity rather than a
hypothetical.

**Arithmetic a reader recomputing will hit:** 33 moves across 29 distinct tasks, 4
tasks moved twice. **Moves sum (24 + 9 = 33); tasks do not (29 ≠ 33).** This is
the 29-vs-33 discrepancy from the first pass, now stated rather than merely
resolved.

**Q3 — should the headline share be the unconditional one or the ≥2-legal-
destination one?** **I propose reporting both**, with the conditioned one as the
one that answers "did the manager choose", since 3 of 9 discretionary moves had
exactly one legal destination.

**Q3 — RULED both, with the ≥2-legal-destination share PRIMARY for any channel
claim** (LS), since a move with one legal destination is not a choice. RR named a
build dependency nobody had: the conditioned share needs capacity state per
timestep, and **L1 making load VISIBLE TO THE MANAGER is not the same as RECORDING
it in the bundle** — the rendering-versus-existence distinction this project has
already paid for. **CHECKED: `manager_load_feedback` records `load` as structured
rows carrying `held` and `capacity` per dimension per worker per timestep, not
rendered text.** `finance_reroute.load_timeline` reads exactly those fields, so
the conditioned share is computable on any post-L1 bundle. Dependency satisfied,
verified rather than assumed.

**At n = 9 discretionary — 6 after conditioning — NEITHER share supports a claim,
and that sentence travels with the numbers wherever they appear.**

**Q4 — do pre-L1 bundles enter any comparison?** **I propose NOT as a baseline.**
Two of nine pre-L1 discretionary moves went to workers already at 3/3 — the t19/t20
bounce — so the pre-L1 discretionary population is partly noise generated by the
blindness L1 removes. Quoting it as "before" against a post-L1 "after" would
attribute an instrument repair to a channel.

**RULED: accepted, and BOTH reviewers found the argument stronger than I made it.**

- **RR: the 22% framing understates it.** Pre-L1 the manager could not observe
  load, so *moving to a full worker* and *moving to a free worker* were the same
  decision problem from where it sat. Post-L1 the first requires ignoring a
  visible signal. **That is a different generating process, not the same process
  measured more noisily, and a caveat cannot repair a changed generating process.
  The contamination is 100% of the population by mechanism; 22% is only the part
  visible in the outcome.**
- **No clean pre-L1 sub-population exists, including the forced one.** RR verified
  it under the STRICT test (refusal timestep < move timestep, since the manager
  acts before the engine within a timestep): 24/24 forced, 9/9 discretionary.
- **Consequence, recorded against LS's own earlier sentence:** the 22→successor
  forced split is a DESCRIPTIVE record of what the broken environment produced, not
  a "before" measurement.

**One thing I want kept beside that, because it is the difference between a
conclusion and its evidence.** LS's independent version of this test — "all 33
moves occurred after a refusal the manager could not see" — was framed as a search
for an exception that came up empty. It could not have come up otherwise: every
bundle has invisible refusals from t0 or t2 and no move happens before t3, so the
permissive form is satisfied by construction. RR's strict form (`<` rather than
`<=`) is the one that discriminates, and it is the one to quote. The conclusion is
unchanged and stronger — there is no POSSIBLE clean sub-population here, not merely
none observed.

## 7. What this DV does NOT establish

- **That a move was correct.** It is behaviour, not outcome. A manager can reroute
  heavily and lose score, or reroute nothing and lose more. The regret
  decomposition stays as the outcome measure; neither substitutes for the other.
- **Anything at 2–3 episodes per cell.** No contrast verdict in either direction.
- **That the manager used a channel.** A move is consistent with using the card,
  the declaration, the ask, the trace, or none of them. Attribution needs the
  channel-pull record, separately.

## 8. Logging that supports it (built, `4d7137e`+)

`task_assigned` at every one of the four sites that mutate `assigned_agent_id`,
carrying `from_agent_id` read BEFORE the mutation, `to_agent_id`,
`is_reassignment`, `applied`, `reason`, `task_class` and the pre-mutation status.
Positive-controlled: first assignment, reassignment, and all three skip branches
each verified to emit a correct row.
