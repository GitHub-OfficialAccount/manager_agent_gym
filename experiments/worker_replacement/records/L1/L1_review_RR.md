# L1 — review (RR)

**Verdict: PASS, after one blocker was raised and fixed.** The five acceptance criteria below
were pre-registered by me *before any L1 code existed* (`e46f2ce`, `aafad7f`) and LS-verified
independently. That ordering is the reason they are worth anything — neither of us could write
the criterion around the implementation.

---

## 1. The five criteria, and why each exists

### (a) The deferral event's own fields assert the worker is FREE — BLOCKER, fixed

`assignment_deferred` (engine.py:862) recorded `agent_current_task_count`,
`agent_max_concurrent`, `agent_available` — the CONCURRENCY numbers. The dominant refusal cause
is the SEGMENT ALLOTMENT, which none of the three describes. Tabulated across all 580 events in
the 18 R2 bundles:

```
current_task_count=0, max_concurrent=1, available=True   335   all segment tasks
current_task_count=1, max_concurrent=1, available=True   245   229 segment + 16 other
```

`can_handle_task` has exactly three refusal branches — unavailable, concurrency, allotment. The
335 have `available=True` and `0 < 1`, so **by elimination all 335 are allotment refusals: the
permanent ones. 57.8% of all deferrals.** At the moment of a permanent refusal the event stated
the agent was idle, available and below its cap. 23 (bundle, agent, task) triples were refused
≥5 times with the agent idle; the longest run is `run_cellU_seed23 / w_4f4d0d / seg_04`, 20
deferrals spanning t2–t21, split 3 concurrency-signature + 17 allotment-signature.

**Second reason this criterion is load-bearing, found while checking it:** the concurrency branch
short-circuits *before* the allotment branch, so a worker that is both busy and exhausted logs as
a *transient* deferral. I expected this to mean 335 undercounts and tested it — allotment is
monotone (`segment_task_ids` is only added to), so every segment deferral at or after an agent's
first idle refusal is permanent regardless of signature. That set is **exactly 335, of which 0
are count=1.** The masking is real in the code and empty in this data, because an exhausted
worker never picks up other work and so is never busy again. **That is a property of this run,
not of the code** — therefore no combination of the logged fields can be made to yield the
reason, and it must be computed at the refusal site and recorded as an enum.

RE's fix does exactly that: `refusal_reasons()` evaluates every branch and `can_handle_task` is
derived from it, so the boolean may short-circuit and the reason cannot. It fired on the first
episode run after the change (same tasks refused for concurrency at t0–t8, allotment from t10).

### (b) Two capacities with opposite release semantics must not share one display

`max_concurrent_tasks_per_worker = 1` releases on completion. `segment_capacity = 3` **never
releases** — `segment_task_ids` is a set added to in `execute_task` and never pruned, so it is a
per-episode lifetime allotment. A line reading `w_X: 3/3` carries the universal scheduler
convention that finishing frees a slot; here it does not.

**On the production-grade test, the two halves separate:** it PASSES for the mechanic — a fixed
per-person allotment inside an engagement is ordinary (WIP budgets, per-reviewer caps) and
finishing one does not earn a fourth — and FAILS for the naive display. Worth keeping separate so
rule 1 is not read as blessing whatever renders the allotment.

### (c) `not started` must not absorb `refused`

Post-deferral the engine sets `agent = None` and the task stays READY. Under a
`not started / running / done` vocabulary a permanently-refused task renders as `not started` —
literally true and indistinguishable from never-assigned. Refused-and-awaiting-reroute must be
**persistent board state**, not only a transient notification.

### (d) Identity across cells is necessary, not sufficient

Two ways acceptance (ii) can pass while being wrong:

1. **Capability re-leak.** A worker descriptor rendered beside the id would reintroduce successor
   capability into cells whose card is deliberately stale — the semantic-agent-id leak, second
   occurrence. Verified fixed in the schema itself: `AgentLoad`'s docstring states the
   restriction as load-bearing, and `render()` emits id and dimensions only.
2. **The stripper trap.** Cell U has no swap, so its roster differs legitimately. A checker that
   strips enough to stop flagging U will strip enough to hide a real difference. Same trap as R2
   items 6/7 — the strip list must be published with the result.

### (e) The allotment predicate is NAME-BASED — LS's finding, verified

`can_handle_task` tests `task.name.startswith(SEGMENT_TASK_PREFIX)`, so a manager-created task
whose name matches is charged to segment allotment. Reproduced: 4 of 18 episodes create a task,
exactly one collides.

```
cell0_seed23  Risk-weighted assets — seg_08 standardised recalculation   ready      w_b391c0  prefix=True
cell0_seed36  Recompute RWA: seg_02 (bank IRB) and seg_07 (mdb IRB)      COMPLETED  w_002c52  prefix=False
cell1_seed3   Stakeholder review: capital adequacy report                ready      unassigned
cellU_seed3   Stakeholder review and approval of capital adequacy...     ready      unassigned
```

**The first two are a natural experiment.** Same act — the manager judging a segment wrong and
ordering a recomputation. One was named with the prefix and refused 13 times to the horizon; the
other ran to completion. The environment's response was decided by the display string, which
rules out "the remediation was ill-formed" in a way the single refused case could not.

**Scoring is clean and no retraction is owed.** The completed created task appears in
`completions` and in none of `reports` (8), `deliverables` (9), `parse_detail` (9), `allocation`
(9). The scorer keys on `index.segment_task_ids`, an id map over the 9 instance segments, so a
manager-created task cannot be read as a segment answer whatever it is called.

**The latent harm, which did not fire here.** `oracle_capacitated` is computed under C=3 over the
9 instance segments. A prefix-matching created task landing on a worker with a spare slot
executes and consumes one of those three, so the feasible set shrinks below what the oracle
assumed and regret is charged against an optimum for a problem the manager was not solving —
verbatim the failure the C=3 docstring exists to prevent, through the opposite door. It did not
fire only because the one collision hit a worker already at 3/3.

**Build-order consequence, which is why (e) is a prerequisite and not tidy-up: L1 raises the rate
of the behaviour that triggers it.** A manager that can finally see load, execution state and
refusals is better equipped to *react*, and task creation is what reacting looks like. Shipping
(e) after L1 means increasing the frequency of the triggering input at the same moment we make
the manager competent enough to produce it. Adopted as a build-order constraint.

---

## 2. The blocker I raised against my own criterion — criterion (i) passed on a hollow load block

RE's first constancy fix was correct for what it covered: `AgentLoad.model_config =
ConfigDict(extra="forbid")`, the substantive assertion at `check_load_feedback.py:501`, and the
observation that `extra='forbid'` alone would not have fixed the live path because the
surrounding `except Exception` swallowed the ValidationError.

**But the substantive assertion was on the FIXTURE path only.** `sample_load` derives from
`fixed_blocks`, the six-cell comparison. The live-path check for criterion (i) was:

```python
missing_load = [i for i, r in enumerate(manager.rendered) if block_of(r, LOAD_HEADER) is None]
```

Header presence only — and `AgentLoad.render()` returns `- <id>: (load unavailable)` for empty
`dimensions`, a plausible line rather than an error. **A live episode rendering that for every
worker at every timestep would have passed (i), and (ii) never looks at the live render.** The
same defect, on the path that matters more.

**The wording was mine.** I wrote *"a script asserts the manager's rendered context contains
execution state, per-worker load, and any refusal that fired."* "Contains" is a presence
predicate; I meant a content property. Same name-vs-predicate family as the rest of this week,
in the criterion I authored to catch this class.

Fixed in `5fded1c`, both directions controlled: no rendered load line may read
`load unavailable`; every rostered worker carries at least one capacity dimension at every
timestep; the check fires on `- w_x: (load unavailable)` and does not fire on the real rendering.

---

## 3. An objection I checked and dropped

I expected refusal-signalling to leak COVERAGE — the manager probes, is refused, and infers what
the newcomer cannot do, giving a fifth channel present in all cells that attenuates every
contrast. **It does not.** `can_handle_task` refuses only on availability, concurrency and
allotment; an out-of-scope segment is accepted and answered badly (SA fallback), never refused.
`segment_capacity` has no per-worker override, so predecessor and successor are identical and
refusal cannot distinguish them.

Recorded as a **design constraint rather than a footnote**: it is the load-bearing assumption
under the researcher's ruling that load is information about the manager's own actions. Had it
failed, there would be a fifth channel in every cell and the ruling would need revisiting.

---

## 4. Carried limitation — the power number is stale

`σ = 0.0768 (df=12) → n ≈ 8–12/cell` was measured on the pre-repair distribution. L1's stated
purpose is to shrink the dominant loss term, which changes both the mean and the variance
structure of the DV. **It is not conservative in a known direction** — removing a large common
loss term can cut σ or leave a smaller mean with comparable spread, which is worse. σ must be
re-estimated post-repair before it sizes anything, with the χ² interval carried alongside (df=12
gives roughly a 5.3× span on n). Recorded as a standing prohibition: **n ≈ 8–12 cannot authorise
a suite.**
