# L1 — load feedback to the manager. RE implementation record.

**Owner:** RE · **Status:** built, acceptance passing, awaiting LS and RR review
(standing rule 7) · **Cost:** zero model calls. The acceptance runs six machinery
episodes through the real engine with the model call removed from the workers;
wall-clock is a few seconds.

**Production-grade test (standing rule 1): PASSES on all three counts.** No
scheduler ships a status field that reports permanently-refused work as ready;
rejection is signalled to the caller because the caller is the only party that can
re-route; load is observable state. The environment failed all three before this.

**No-drift check (standing rule 2): this serves the question.** The question is
which information about a NEWCOMER changes allocation. Every channel contrast was
previously measured against a manager that could not see whether its own
instructions had taken effect, and that second failure sits directly on the
dominant loss term (over-concentration correlated with regret at r = 0.93). This
does not add a channel; it removes a confound from all six cells equally.

---

## What was built

Detailed in `CHANGED.md` §L1. In short: five additive core changes — truthful
execution vocabulary on the board, `AgentInterface.load_report()` with a
`CapacityBoundedAIAgent` override, refusals buffered by the engine and handed to
the manager unconditionally before each decision, both blocks always rendered into
the prompt, and a per-timestep `manager_load_feedback` record so a bundle carries
its own evidence.

## One deliberate deviation from the ruling's wording, flagged rather than taken silently

The ruling says `not started / running / done`. I render `not started` with a
qualifier: `(waiting on dependencies)` versus `(dependencies met, not yet
running)`. A real scheduler distinguishes blocked from queued, and collapsing them
would let the manager re-route work that was merely waiting its turn — the same
class of error in the opposite direction from the one being fixed. The state
vocabulary is unchanged and `ready` is gone from the board. **If LS or the
researcher prefers the literal three, it is a one-line change in
`EXECUTION_STATE_LABELS`.**

## Acceptance — `check_load_feedback.py` (current output)

```
L1 acceptance — load feedback reaches the manager, constant across cells

A. machinery episode (cell 0, real engine, zero model calls)
   10 manager decisions recorded
   [ok] worker-load block present at every timestep (missing at none)
   [ok] refusal block present at every timestep (missing at none)
   [ok] board speaks execution state or REFUSED only (13 distinct states; unexplained: none)
   [ok] the word `ready` no longer appears as a task state (at none)
   [ok] REFUSED is its own board state, not absorbed into `not started`
   [ok] and it coexists with plain `not started`, so the two are distinguishable on one board
   [ok] and it PERSISTS: refused tasks on the board per timestep = [0, 2, 9, 8, 7, 6, 6, 6, 6, 6]
   [ok] refusals name their OWN cause: ['allotment', 'concurrency'] — the transient and the permanent case are distinguished, not merged
   [ok] a real refusal reached the manager (56 refusal lines across the episode)
   [ok] both capacities reported, distinguishable: [('concurrent tasks', True), ('segment allotment', False)]
   [ok] and their OPPOSITE release semantics are in the RENDERED text, not just the model
   [ok] a worker is observed exhausting a capacity
   [ok] no worker descriptor appears in either block (13 candidate strings from the instance's own workers; leaked: none)
   [ok] the refusal buffer is DRAINED per decision: 6 left after the last timestep vs 56 raised across the episode (max 9 in any one gap)
   [ok] and it GOES QUIET when nothing was refused, rather than repeating the last line

B. constancy — one FIXED state rendered under all six cell configs
   (the claim is that no cell switch touches these blocks; live cells
    hold different rosters, so identical CONTENT is not the claim)
   [ok] the compared blocks are SUBSTANTIVE, not six copies of an empty rendering
        load:    - w_aaaaaa: concurrent tasks 0/1 (frees when a task finishes) · segment allotment 3/3 (used this
        refusal: - task 'fixture_task' was not started: w_aaaaaa refused it — concurrency limit reached (1/1 conc
   [ok] load block byte-identical across all six cells (1 distinct)
   [ok] refusal block byte-identical across all six cells (1 distinct)
   [ok] present in every cell (absent in none)

C. live machinery episode per cell — identical FORM, content free to differ
   U: 10 decisions, 56 refusal lines, max load 3
   0: 10 decisions, 56 refusal lines, max load 3
   1: 10 decisions, 56 refusal lines, max load 3
   2: 10 decisions, 56 refusal lines, max load 3
   3: 10 decisions, 56 refusal lines, max load 3
   4: 10 decisions, 56 refusal lines, max load 3
   [ok] identical row grammar across all six live cells (1 distinct)
   [ok] every cell exercised a real refusal (silent in none)

D. comparability assertion over the six machinery bundles
   [ok] comparable=True, problems=none
   [ok] and it REJECTS a bundle whose load-feedback record is absent (the pre-L1 condition)
   [ok] and it rejects a set where only ONE cell ran blind — the case that would look like a channel effect

E. the allotment predicate (criterion (e))
   [ok] the metered set and the scored set are the SAME SET (9 vs 9; symmetric difference 0)
   [ok] manager-created, prefix-matching (was refused 13× in cell0_seed23): metered=False
   [ok] manager-created, non-matching (completed in cell0_seed36): metered=False
   NOTE, not a check: manager-created work is now charged NOTHING, so a manager
        can obtain labour outside the allotment the oracle assumes. Deliberate —
        the alternative shrinks a worker's feasible set below the oracle's model.
        It is the analysis's business, and it is visible in the record.

F. positive controls — every null-shaped check, shown FIRING
   [ok] board-state check fires on `Status: ready`
   [ok] descriptor-leak check has a NON-EMPTY candidate list (13 strings) — the first version had 0 and passed against nothing
   [ok] descriptor-leak check fires on a planted capability
   [ok] constancy check fires when one cell's block differs
   [ok] grammar check still distinguishes a real difference after stripping
   [ok] release-semantics check fires on a bare `3/3`
   [ok] reconciliation check fires on a mismatched set

RESULT: PASS — execution state, per-worker load and refusal reach the manager's rendered context at every timestep, in identical form in every cell, and a real refusal is observed in all six
```

Suite at parity: 292 passed, 2 skipped, 1 pre-existing live-API failure
(`test_live_anthropic_returns_pydantic`, 401 on an absent key). All twelve
`worker_replacement` acceptance scripts pass.

## Why the constancy claim is put the way it is

Acceptance (ii) asks for the signals "in identical form across all six cells". The
six cells hold genuinely different rosters — cell U keeps the predecessor — so
identical CONTENT across live episodes is not available, and a check demanding it
could not pass for a reason that is not a defect. So the claim splits:

- **Part B** holds the STATE fixed and varies only the cell, requiring
  byte-identical output. This is the actual claim: no cell switch touches these
  signals.
- **Part C** runs the six live and requires identical row GRAMMAR, content free to
  differ by roster.

## Two things caught while building, worth recording

**The first version of the acceptance would have passed on an episode where
nothing ran.** It assigned only segments; the upstream tasks were never assigned,
so no segment ever became runnable, no refusal ever fired, and the refusal check
had nothing to fire on. It reported zero refusals — which I read as a bug in the
signal before realising it was a bug in the fixture. A check whose subject never
occurs is not a passing check.

**One printed line tested nothing.** `[ok] refusals are drained per decision` was
unconditional — a decorative check of exactly the kind this project keeps
rediscovering. Replaced with two real ones: the buffer holds one gap's worth (6)
rather than the episode's (56), and an emptied buffer renders as quiet.

## What this does NOT establish

- That any model USES the signals. Nothing here involves a model. **That is L3,
  and the expected consequence stated in advance is that the dominant loss term
  SHRINKS, possibly a lot.**
- That the signals are *sufficient* for the manager to reach the capacitated
  optimum. Load is the input the scope run identified as missing; whether it is
  enough is an empirical question this does not answer.
- The `manager_load_feedback` record establishes the signals were in the
  OBSERVATION, not that they were rendered into the prompt. Rendering is
  established by the acceptance script against the real renderer, on machinery
  episodes — not on any live bundle yet.

## Population and comparator for every number above (standing rule 5)

Each count is over **manager decisions in a zero-model machinery episode at seed
101, ten timesteps, with all nine segments assigned to the single
lowest-sorted-id worker and non-segment work spread round-robin** — a deliberately
failing allocation, not a representative one. "56 refusal lines" is the total
raised across those ten decisions, comparator: 0 lines raised in the same
configuration before L1. "max load 3" is against a capacity of 3.

---

# Addendum — RR's five blocking criteria (folded in after `49e5d45`)

The criteria reached me after the first L1 commit. All five are met; `49e5d45`
should not be reviewed on its own. Details in `CHANGED.md` §"L1 addendum".

**(a) MET, and the root cause was worse than the reporting problem.** I had not
read the concurrency fields through — the line was built from `load_report()` —
but your masking point killed what I had: a line saying "3/3 segment allotment"
when the branch that fired was concurrency is a true number attached to the wrong
cause. Fixed at the root rather than around it: `refusal_reasons()` evaluates all
branches and `can_handle_task` is derived from it, so the boolean may
short-circuit and the reason cannot.

**This episode contains the masking case, so the fix is exercised, not asserted.**
The same tasks are refused for CONCURRENCY at t0–t8 and for ALLOTMENT from t10.
Under the old code both would have logged identically.

**(b) MET.** Both capacities, each carrying its release semantics, checked on the
rendered text.

**(c) MET.** REFUSED is its own board state, coexists with plain `not started`,
and persists: refused-tasks-on-board per timestep = `[0, 2, 9, 8, 7, 6, 6, 6, 6,
6]`. The decay from 9 to 6 is the three that got slots as the pile drained.

**(d) MET, and the check it names was worthless as first written.** The
descriptor-leak check gathered its candidates by walking the instance dict for
`str` and `list` values. The fields are TUPLES. It collected ZERO candidate
strings and printed `[ok] no worker descriptor appears in either block (0
candidate strings ...)`. **A null-shaped check that fails to empty reports a clean
pass against nothing** — which is the rule you sent, arriving in my own output
about forty minutes after I read it. It now builds candidates from the cards the
run actually uses (13 strings) and asserts the list is non-empty before trusting
the null. Strip list published in `load_feedback_acceptance.json`.

**(e) MET.** `task_class` is declared on the nine scored segments; the engine's
metered set and the scorer's `index.segment_task_ids` are asserted identical; the
natural experiment is a regression test — both remediation names, neither metered.

## Two things I am flagging rather than deciding

**1. Manager-created work is now free.** Not metering it is the only option that
keeps the oracle's model true, and it is what (e) implies. But it means a manager
can create tasks and obtain labour outside the C=3 the oracle assumes. Nothing
currently bounds that. It did not arise in 18 episodes (4 had task creation, of 1
task each), and L1 raises the rate of the triggering behaviour by your own
argument. **If a manager starts creating segment-equivalent work at volume, the
regret denominator stops meaning what it means now.** I would rather this be
watched in L3 than pre-emptively capped, but it is your call and RR's.

**2. My reconciliation check reported a false defect on its first run** —
symmetric difference 18 over two 9-element sets, because the index stores task ids
as `str` and the workflow as `UUID`. One name, two representations; §B again, this
time inside a check written to enforce §B. Fixed by comparing as strings. Worth a
line in the methodology file if you agree: **a set comparison across two modules
must normalise representation before it can claim identity, or it reports a
difference that is entirely its own.**

## Not done, deliberately

**σ is not re-estimated and I have cited it nowhere.** Per your instruction it was
measured on the distribution L1 destroys. L3 re-estimates with the χ² interval.


---

# Addendum 2 — LS review findings (both fixed)

## FINDING 1 (blocking) — the fixed-observation constancy check was hollow. CONFIRMED, reproduced, fixed.

LS is exactly right and I reproduced it before touching anything:

```
AgentLoad(agent_id='w_x', held=3, capacity=3, unit='segment tasks').render()
  -> '- w_x: (load unavailable)'
```

`held` / `capacity` / `unit` were the schema's fields BEFORE criterion (b) split
load into dimensions. I updated the schema and never updated the fixture.
Pydantic's default `extra='ignore'` dropped all three silently, `dimensions`
stayed empty, and **Part B compared `(load unavailable)` to itself six times. It
was constant because it was EMPTY — it would have passed identically had the load
feature never been built.** The committed record carries the evidence:
`fixed_state_load_block: "- w_aaaaaa: (load unavailable)"`. The refusal half was a
hardcoded literal still carrying the pre-L1 wording.

**This is my own positive-control rule failing in the commit that introduced it.**
Part F demonstrated six other checks firing; the seventh, added in the same
commit, was never given a control and was the one that was hollow.

Three fixes, in increasing order of how much they matter:

1. The fixture is now BUILT FROM THE PRODUCTION `load_report()` on a real
   `CapacityBoundedAIAgent`, so it cannot describe a shape the code no longer has.
   The refusal line is taken from Part A's live episode with ids neutralised,
   rather than transcribed.
2. **Part B now asserts the compared blocks are SUBSTANTIVE before comparing
   them** — the control that was missing. `constant-because-empty` is not the
   claim.
3. The schema is strict, so the old fixture raises rather than degrading.

**What was NOT wrong, and I want this on the record because it bounds the damage:**
section D carries the same constancy claim against the six REAL bundles in both
directions, and that part was always sound. The hollow check was redundant, not
load-bearing. That is luck, not design.

## FINDING 2 (not blocking, more valuable) — the same mechanism under a live path. Fixed, and further than suggested.

`AgentLoad(**agent.load_report())` in `create_observation` had the same
`extra='ignore'` exposure with a `except Exception` around it — so schema drift
would have degraded to `(load unavailable)` on the path the manager actually
reads, invisible to every check that tests the block's PRESENCE.

`extra='forbid'` alone would NOT have fixed it: the surrounding `except Exception`
would have caught the `ValidationError` and produced the same silent empty row.
So the catch is now split — **`ValidationError` propagates** (a deterministic
programming error every episode hits identically, and which the acceptance hits
before a run costs anything), and any other exception yields a row whose agent id
carries `[LOAD REPORTING FAILED: <type>]` rather than looking like an ordinary
empty. A research instrument failing loudly beats a bundle that looks fine.

## MINOR — accepted

`0/3 (SPENT FOR THE EPISODE ...)` read as though something had been spent when
nothing had. Now `segment allotment 0/3 (used this episode; does NOT reset when a
task finishes)`. The parenthetical describes the counter, not the value.

## On L3 gaining a manager-created-task requirement

Accepted, and "visible in the record is not a detector" is the right correction to
what I wrote. L3 will count manager-created tasks per episode, report the
distribution, and state the denominator's validity condition as a predicate.
