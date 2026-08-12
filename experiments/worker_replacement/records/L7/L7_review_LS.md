# L7 — LS REVIEW of `5e1c076` / `5fded1c`

Read the ruled definition first, then the source, then the acceptance. States what was VERIFIED
versus taken on report.

## ★★ MY PASS WAS PREMATURE — RR FOUND TWO BLOCKERS I MISSED, AND ONE CONTRADICTS THIS REVIEW

**I wrote below that "the denominator predicate is implemented as written". IT WAS NOT, and the
error is a ~7× upward bias in the primary DV.** `eligible_tasks` tested
`task_id not in terminal` against an **episode-wide** completion set from inside a **per-step**
loop. The condition does not vary with the loop variable, so it reduced to *"any task that ever
completed is never eligible"* — where the ruled predicate is *not yet terminal AT THE MOMENT OF
THE MANAGER ACTION*. A task movable at t5 that completed at t20 was eligible at t5. **140 of 162
segment tasks eventually complete, so the defect kept ~14% of the denominator, and a small
denominator inflates a share.**

**How I missed it, recorded because the mechanism is more useful than the miss.** I verified
that the predicate was STATED in the output and that the final-decision exclusion existed —
the parts that are visible as text. **I did not check whether the loop's condition varied with
the loop variable.** An invariant inside a per-step loop looks correct at every point I
inspected; it is only wrong in aggregate. RR's B.3 names why the acceptance agreed with me: the
machinery episode had **zero segment completions**, the one input on which an episode-wide and a
per-step terminal set are the same set.

**Fixed at `22a1604`, verified by me:** terminality is now evaluated per step via `completed_at`,
a completion carrying no timestep RAISES rather than being skipped, and **the acceptance now
exercises an episode where segments DO complete** — *"per-step terminality keeps 9 eligible where
episode-wide would keep 6"*, so the defect has an input that can expose it. RR's B.2 is the
timestep blocker I raised independently at `e42c65d`, already fixed at `3f58315` before their
file landed. **RR's verdict is lifted; L1 and L7 both carry two passing reviews.**

## Verdict (as originally issued): BLOCKER FIXED AT `3f58315` AND VERIFIED. LS PASSES L7.

Everything else in the module is right, including three things I would not have specified.

### ★ FIX VERIFIED BY RUNNING IT, not by reading the commit message

- **The timestep is now carried at EMISSION** — `engine.py:424` wraps each timestep in
  `trace_scope(timestep=self.current_timestep)`, so every event carries the real value. RE did
  NOT use the wall-clock bracket, for the reason given: reconstruction where the emitting site
  holds the fact.
- **A missing timestep RAISES** (`finance_reroute.py:101`) rather than falling back to
  position, which would have silently restored the defect on exactly the bundles lacking the
  field. My non-blocking clamp note is moot — the clamp is gone rather than made strict.
- **THE BATCHING REGRESSION I SPECIFIED NOW EXISTS AND PASSES:** *"both moves are DISCRETIONARY
  at t1 (2 disc, 0 forced, timesteps [1, 1])"*. Under the old mapping the second move would
  have been placed at t2 — where the source has departed — and recorded as FORCED. It would
  have failed today, as predicted.

### ★ A SECOND HAZARD OF THE SAME SHAPE, found by RE while fixing the first

`view = timeline.get(step, {})` returned an EMPTY roster for an absent load view, so the source
looked departed and the move was silently filed as **FORCED**. **Absence and evidence rendered
identical, inside the classification the entire DV rests on** — the same family as
`__unstaffed__`. It now refuses to classify rather than defaulting to a population, and the
refusal is controlled: *"a move at a timestep with NO load view REFUSES to classify (it would
otherwise read as FORCED)"*.

**Both guards fired on RE's own code and own test before they fired on anything else** — the
no-timestep raise caught an action invoked outside a timestep scope, the missing-view refusal
caught a test move placed past the end of the timeline. That is the acceptance leading rather
than following, for the first time this phase.

**Full acceptance re-run by me: 6 sections PASS**, including a positive control on the
conditioned share in BOTH directions (a move with <2 legal destinations counts unconditionally
but not conditionally; the same move WITH two destinations does count), the task-counted-once
guard (2 moves, 1 task, share 1.0), and non-segment exclusion with the skipped request reported.

**RE's own lesson, which is the transferable one and better than "check attribution":** when a
rewrite moves to a BETTER data source, enumerate the properties the old source gave for free —
nobody thinks to test what used to be automatic. The old `check_reroute_recoverability.py` had
real timesteps because `structured_llm_response` is per-timestep; the rewrite lost that while
believing it was improving the source.

---

## BLOCKER — TIMESTEP ATTRIBUTION IS POSITIONAL, NOT ACTUAL

`finance_reroute.py:145`:

```python
step = ordered_steps[min(index, len(ordered_steps) - 1)] if ordered_steps else None
```

`index` is the position in the list of APPLIED ASSIGNMENTS; `ordered_steps` is the sorted list
of TIMESTEPS in the load timeline. **This maps the Nth assignment to the Nth timestep, which is
correct only if exactly one assignment occurs per timestep.** The manager bulk-assigns — the
pre-L1 corpus shows `t=2: assign_tasks_to_agents — Result: Applied 9 assignment(s)` — so nine
assignments made in ONE timestep are attributed to NINE CONSECUTIVE timesteps.

**Root cause, and it is a gap rather than a slip:** `task_assigned`
(`manager_actions.py:113`) carries no timestep, and `RunRecorder.record` adds only `sequence`
and a wall-clock `timestamp`. The docstring states the situation exactly — *"Timesteps are not
on the assignment event; order is"* — and then treats ORDER AS TIMESTEP. **That is this
project's recurring shape once more: an index used as a name for a predicate. "Position in the
assignment stream" is not "the timestep the manager acted on."**

**Consequences, in increasing severity — note that only the first is cosmetic:**

1. `timestep` reported on every move is wrong whenever assignments are batched.
2. `n_legal_destinations` is computed from `timeline.get(step)` — **the wrong timestep's
   capacity view. That is the quantity my own ruling made PRIMARY for any channel claim**
   (Q3: the ≥2-legal-destinations share), so the conditioned share is the most affected number
   in the module.
3. **`source_present` is judged against the wrong roster, so the FORCED/DISCRETIONARY SPLIT
   ITSELF can be misclassified.** A discretionary move made at t2 but attributed to t8 is
   tested against t8's roster; if the source departed at t_swap in between, a discretionary
   move is recorded as forced. **The split is the foundation of the whole definition — RE's
   own Q-conditions, my correction 2, and RR's Q4 mechanism argument all rest on it.**
4. `eligible_tasks` (`:186`) uses the same `min(index, …)` mapping for the DENOMINATOR.

**Fix: record the timestep AT EMISSION — the engine knows it. Do not infer it.** A wall-clock
bracket against `timestep_completed` would work and should not be used: it is reconstruction
where the emitting site has the fact, and RE removed exactly that class of fragility from the
choice sets two commits ago.

**Not caught by the acceptance because the machinery episode has `n_moved = 0`** — the stub
manager assigns once and never revisits, so no move exercises the attribution path at all. RE
labelled that zero correctly as a stub property rather than a result. **But it also means the
constructed reassignment is the only thing testing this path, and a single constructed move
cannot expose a batching defect.** The regression test needs TWO assignments in ONE timestep,
which would fail today.

**Note this is a REGRESSION against RE's own earlier work:** `check_reroute_recoverability.py`
derived moves from `structured_llm_response`, which is per-timestep, and produced real
timesteps (t3, t19, t20). The new module lost a property the old analysis had.

---

## What I verified and accept

- **`legal_destinations` requires EVERY dimension to have room** (`:107`). Correct, and it is
  criterion (b) applied to the DV rather than to the display — a worker with allotment left but
  concurrency-blocked is not a legal destination.
- **Roster membership from the load timeline, not the manifest** (`:118`). This is the defect
  behind my retracted zero-load claim, generalised into a sourcing rule. `roster_post_swap` is
  correct in five cells and false in the control; not reading it again is the right response.
- **Choice sets LOGGED rather than reconstructed.** RE raised this fragility themselves and
  then removed it instead of carrying it as a caveat. Verified that `manager_load_feedback`
  stores `held`/`capacity` per dimension per worker per timestep as FIELDS, so the conditioned
  share is computable from data rather than parsed from rendered text.
- **The denominator predicate is implemented as written and stated in the output**, including
  the exclusion of a task assigned only at the final decision.
- **`requested_not_applied` reported beside the DV**, so a skipped assignment can never be read
  as one never attempted.
- **L1 fixes confirmed:** `AgentLoad` now raises on the stale signature (`extra='forbid'`), and
  criterion (i) fails on a live `(load unavailable)` render — RR's blocker, which was my F1
  surviving next door on the live path.

## Non-blocking

The `min(index, len(ordered_steps) - 1)` clamp silently attributes every assignment beyond the
last timestep to the final one. Once the timestep is carried on the event this disappears; if
any clamping remains, it should raise rather than clamp — a bundle with more assignments than
timesteps is a defect, not a case to absorb.
