# L7 — review (RR): the `rerouted_share` definition, and the implementation

Two parts. **Part A (definition, `rerouted_share_definition_v1.md`): PASS with rulings** — Q1, Q2
and Q4 accepted as proposed, Q3 accepted with a logging dependency, one limitation on
discretionary legal-set sizes. **Part B (implementation, `finance_reroute.py` @ `5e1c076`): DO NOT
COMPUTE — three blockers, all silent, none of which can fire on the episode it was tested against.**

---

# Part A — the definition

## A.1 The corpus numbers reproduce exactly

Independent reconstruction from `structured_llm_response.parsed_response.action`, my own code, no
shared source with RE's:

```
total moves 33 · forced 24 · discretionary 9 · distinct tasks moved 29
forced timesteps        t3:15  t4:8  t6:1
discretionary timesteps t3:1 t4:2 t6:2 | t19:1 t20:1 t21:2
```

33/24/9 and the 29-vs-33 gap all match.

**One nuance RE's summary flattened:** the discretionary population is **bimodal, not late** —
5 of 9 land at t≤6 in the same window as the forced moves. "Discretionary moves happen later"
holds for under half of them. RE corrected the script to state what generalises instead: no
discretionary move had a full choice set, whenever it occurred.

## A.2 Q4 — accepted, on stronger evidence than the doc used

Tested with logged fields only, no reconstruction: an idle-signature segment deferral
(`agent_current_task_count = 0`) **proves** that agent held ≥3 segments at that timestep.

```
FORCED         0 of 24 moves to a provably-exhausted destination
DISCRETIONARY  2 of 9   — t19 → w_b391c0, t20 → w_3330c6, both run_cell1_seed23
```

Positive control: 17 agents proven exhausted across the corpus, so the test is not inert.
**Q4's empirical basis does not depend on the fragile reconstruction at all.**

**A caveat does not suffice, and the 22% framing understates it.** Pre-L1 the manager could not
observe load, so *moving to a full worker* and *moving to a free worker* were the same decision
problem from where it sat; post-L1 the first requires ignoring a visible signal. **That is a
different generating process, not the same process measured more noisily, and a caveat cannot
repair a changed generating process. The contamination is 100% of the population by mechanism;
22% is only the part visible in the outcome.**

**On LS's stronger form, which I verified rather than accepted.** LS claimed all 33 moves followed
a refusal the manager could not see. I first tested permissively (`t <= move`, 33/33), then
strictly (`t < move`), since the manager acts before the engine within a timestep — **24/24 forced
and 9/9 discretionary survive the strict test.**

RE then observed that the permissive form could not have failed. Applying LS's new rule (a
confirming test must be able to disconfirm) to my own result: of 162 segment tasks, **109 (67%)
were ever deferred; of the 29 that moved, 29/29.** Under random selection roughly a third of moved
tasks should have had no prior deferral. **The strict form discriminates; the permissive one did
not.**

## A.3 LIMITATION — do not quote pre-L1 discretionary legal-set sizes

RE characterised this as a timing-attribution weakness. **It is worse, and my evidence is three
failed attempts of my own.** `worker_execution_started` carries
`model / system_prompt / task_prompt / input_resources / tools / max_turns` — **no `agent_id` and
no `task_name`.** Reconstructing allotment state pre-L1 requires scraping the agent id out of a
system-prompt string and the segment out of a task-prompt string. **The join keys themselves are a
text scrape** — a fragile identification, not a fragile estimate.

The forced side survives because it has independent field-level support (0 of 24 to a
provably-exhausted destination). **Quote the forced result; do not quote discretionary legal-set
sizes until a post-L1 run logs capacity state as a field.** Now marked DO NOT QUOTE in the script
output itself rather than in a record someone would have to find.

## A.4 Q1 — TASKS, agreed

An opportunity denominator varies with horizon and dwell time, **and L1 changes both** — visible
execution state changes how long work sits. A primary DV whose denominator moves with the
instrument cannot be compared across the repair that L1 is. Same conclusion as LS's ruling
(confounded with execution speed); this names the specific confound.

## A.5 Q2 — agreed, and the population is measured, not hypothetical: **3 tasks**

3 of the 9 discretionary moves are on tasks that also had a forced move, so **the Q2 rule
determines a third of the numerator.** Also for the doc: 33 moves across 29 distinct tasks, 4
moved twice — **moves sum (24+9=33); tasks do not (29≠33).**

## A.6 Q3 — report both, with a dependency nobody had named

The conditioned share needs legal-set size, which needs capacity state per timestep. **L1 makes
load VISIBLE TO THE MANAGER; that is not the same as RECORDED IN THE BUNDLE** — the
rendering-versus-existence distinction that cost this project a week, and my own §89 error.

RE checked rather than assumed: `manager_load_feedback` records `load` as structured rows carrying
`held` and `capacity` per dimension per worker per timestep — fields, not rendered text — and
`finance_reroute.load_timeline` reads those. **Dependency satisfied; the conditioned share is
computable on any post-L1 bundle.**

---

# Part B — the implementation (`finance_reroute.py` @ `5e1c076`)

## B.1 BLOCKER — the denominator excludes every task that ever completed

`eligible_tasks`, lines 179–192:

```python
terminal = {str(c["task_id"]) for c in bundle.get("completions", [])}   # episode-wide
...
for step in later:
    if assignee in timeline[step] and task_id not in terminal:
```

`task_id not in terminal` does not depend on `step`, so it is invariant across the loop and
reduces to **"any task that ever completed is never eligible."** The ruled predicate is *not yet
terminal at the moment of the manager action* — a task movable at t5 that completed at t20 was
eligible at t5.

Measured: **140 of 162 segment tasks (86%) eventually complete.** On a real episode this keeps
~14% of the denominator, and a small denominator inflates a share — **`rerouted_share` comes out
biased upward by roughly 7×.**

**Why the acceptance missed it:** the machinery episode reports `n_eligible: 9`, all nine
segments, so it had **zero segment completions** — precisely the input on which this cannot fire.

## B.2 BLOCKER — the timestep is reconstructed from list position, and it drifts

Lines 132–146 and 188 map the *i-th applied assignment* to the *i-th timestep*:

```python
step = ordered_steps[min(index, len(ordered_steps) - 1)]
```

Sound only at one applied assignment per timestep. Measured: **156 of 256 manager assignment
actions assign more than one task**, distribution `{1:100, 2:87, 3:26, 4:20, 5:1, 6:4, 9:17, 10:1}`.
In `cell0_seed23`: **45 assignments across 17 timesteps, 9 of them at t3 alone.** Indices run far
ahead of timesteps and `min(...)` clamps the tail onto the final step.

Three quantities read the wrong timestep's view:

1. **`source_present`** → the FORCED/DISCRETIONARY split. An assignment made at t3 attributed to
   t9 finds the predecessor gone and is classified FORCED when it was DISCRETIONARY.
2. **`n_legal_destinations`** → the conditioned share, **the primary DV**.
3. **`eligible_tasks`** → the denominator, again.

The split boundary is `t_swap = 3`, and t3–t4 is where assignment density peaks — **the drift is
largest exactly where the classification matters.** Lines 76–81 criticise the pre-L1
reconstruction for moving a count by one, and substitute a proxy that drifts by twenty.

**Fix is one field: put `timestep` on the `task_assigned` event.** That is the field that makes L7
"logged, not reconstructed", and it is the one that is missing.

## B.3 BLOCKER — the DV returns zero on the only real input, with no positive control there

Committed `records/L7/reroute_acceptance.json`, `machinery_episode_cell0`:

```
n_discretionary_moves 0 · n_forced_moves 0 · n_moved 0 · n_requested_not_applied 0
rerouted_share_conditioned 0.0 · rerouted_share_unconditional 0.0
forced_destinations {to_successor: 0, to_incumbent: 0}
n_eligible 9        <- the only non-zero quantity
```

The five controls all fired and they are good controls, **but all five run on fixtures.** They
establish that the *checks* work, not that the *DV* works. **A DV returning 0 on real data with no
positive control on real data is uninterpretable** — my own null rule pointed at the acceptance.
Both blockers above would produce exactly this all-zeros pattern.

## B.4 LIMITATION — a hollow load timeline yields `0.0`, not an error

`legal_destinations` correctly refuses to count a row with empty `dimensions` (line 107). But if
*every* row is hollow, `n_legal_destinations` is 0 everywhere, `chose` is empty and the
conditioned share is silently `0.0` — a number, not a failure. The L1 live-path check guards the
upstream condition, so this is a limitation. **The DV should refuse to return a share when no
timestep carries a substantive load row.**

## B.5 What is right, recorded separately from the blockers

- **Roster taken from the load timeline rather than the manifest**, citing the cell U retraction.
  Correct source, and it forecloses a repeat of a mistake already made once.
- **`legal_destinations` requiring room in EVERY dimension**, not the binding one — criterion (b)'s
  concurrency-versus-allotment distinction carried into the analysis layer.
- **`establishes` / `does_not_establish` and the predicate strings as fields on the returned
  object** — standing rule 5 made mechanical: the population travels with the number instead of
  living in a document.
- **Q2 implemented correctly** — a task with both moves lands in `moved` via the discretionary set
  and in `n_forced_moves` as a move; one task in two analyses, never summed.
- I suspected line 234 read `successor_id` from the wrong container. **I was wrong** — it is in
  `manifest` in 18/18 bundles.

**Verdict as issued: do not compute the DV on any corpus until B.1 and B.2 are fixed, because both
silently produce plausible numbers rather than errors. B.3 first, since it determines whether the
current implementation has ever produced a non-zero numerator on real events.**

---

# Part C — resolution, verified against the code and the record

**All three blockers and the limitation are fixed. Verdict lifted.** Verified by reading the
committed artifacts rather than the commit messages.

**B.2 was already fixed when I filed it, and LS found it independently.** Timeline: `5e1c076`
(11:42) is the commit I reviewed; `e42c65d` is LS's review naming the same positional-attribution
blocker; `3f58315` (11:53) is RE's fix. So my B.2 was filed against a superseded commit — the
diagnosis was right and matched LS's, but the credit for finding it is joint at best and the fix
preceded my report. Recorded because the record should say who found what and when.

- **B.1 fixed** (`22a1604`) — terminality computed from completion timesteps per step; a completion
  carrying no timestep raises rather than being treated as never-terminal. The acceptance now
  demonstrates the two predicates *disagreeing on real data* before claiming the right one is
  used: 3 segments actually complete, and per-step terminality keeps 9 eligible where episode-wide
  would keep 6.
  **Why the original acceptance could not see it** (RE's finding, and the better half): the
  machinery bundle carried `completions: []`, the one input on which episode-wide and per-step
  terminality agree — and it was empty because the zero-cost worker bypasses
  `AIAgent.execute_task`, so no `worker_execution_completed` events exist in a machinery bundle at
  all. The `[]` was not an oversight in the check; there was nothing to pass.
- **B.2 fixed** (`3f58315`) — the engine wraps each timestep in `trace_scope(timestep=...)`,
  `task_assigned` carries the field, and a missing timestep raises rather than falling back to
  position. Regression: two moves in one timestep, which the old mapping would have placed at
  [1,2] and filed the second as FORCED. **A second hazard fell out of the fix**, same family:
  `timeline.get(step, {})` made an absent load view look like an empty roster, so the source read
  as departed and the move was filed FORCED — absence and evidence rendered identical, inside the
  classification the DV rests on. It now refuses to classify.
- **B.3 fixed** (`22a1604`) — the JSON was not stale; the 1/9 existed in a section RE never wrote
  to the record. Both rows are now committed:
  `machinery_episode_cell0_after_one_real_move` gives `n_eligible 9 · n_moved 1 ·
  n_moved_with_real_choice 1 · rerouted_share_conditioned 0.111`, and the zero row is labelled a
  property of the stub manager rather than a result.
- **B.4 fixed rather than carried** — a bundle where no timestep has a load row with dimensions now
  raises. A share of zero and an unmeasurable share are different statements, and this was the
  third place in this project where they were rendered identically.
