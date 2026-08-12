# S8 — Reviewer-reproducer review (verbatim, received by DM 2026-08-09): PASS; F1 blocker-class for S9

S8 REVIEW — **PASS on the assembly, with one blocker-class finding on the capacity wiring that connects directly to the S9 pre-ruling you already routed.** Your acceptance amendment I endorse; the slot-lifecycle argument verifies.

════════════════════════════
(1) THE THREE CORE DIFFS
════════════════════════════
**Slot lifecycle — the A→B→C argument verifies, and the placement is correct.** The `done_tasks` loop (engine.py:725-739) runs *before* `ready_tasks = self.workflow.get_ready_tasks()` (:826) inside the same call, so a slot freed at completion-detection is visible to `can_handle_task` at :850 in the same timestep; freeing it in `_update_workflow_state` would not be, and the chain would advance one task per two timesteps. I also checked the paths that could leak a slot: failed and exception-raising tasks still land in `done_tasks` (so they free), and a task pending past the 300s `asyncio.wait` timeout correctly keeps its slot because it is genuinely still running. Occupy-after-check ordering (:850 check, :862 append) is right, so an agent with cap 3 and 5 ready tasks starts exactly 3.

**Registry agent-class resolution — real bug, correctly diagnosed.** `_agent_classes` was consulted by `create_agent()` but bypassed by the scheduled-add path, so `register_agent_class("ai", X)` silently had no effect on **any timeline-arriving agent** — i.e. on every successor in this study. The fallback to `AIAgent` keeps existing behaviour. Good catch; it would have bitten silently and only in the arm that matters.

**Task-board render — assignment identity only, and the constraint is visible in the code**, not just asserted: the line emits `assigned_agent_id or '(unassigned)'` and nothing else — no capacity vocabulary, no decline events, no coverage content. The id is opaque per S5's assertion 5, so the board cannot leak coverage through the name either. Consistent with §5's leak-exclusion enumeration.

════════════════════════════
F1 (BLOCKER-CLASS) — UNDER CAPACITY THE ENGINE PICKS WHICH ASSIGNMENTS EXECUTE, BY ITERATION ORDER
════════════════════════════
`ready_tasks = self.workflow.get_ready_tasks()` returns tasks in **`self.tasks` dict-insertion order**, and the start loop consumes slots first-come. So when a manager assigns more than `max_concurrent_tasks` to one worker — which the design guarantees will happen, since capacity binds with zero slack — **the engine decides which of those assignments run this timestep and which are deferred, by task-registry order.** The manager assigned all of them; the engine silently realised a subset it did not choose and cannot observe.

Three consequences, in order:
1. **Intended allocation and realised allocation diverge exactly when capacity binds** — i.e. always, by construction. The primary DV is computed from an allocation; **which one is scored decides whether we are measuring the manager's decision or the engine's iteration order.**
2. **This is the same victim-selection problem your S9 pre-ruling names** (*"timing must not pick the victim"*), one layer down. The S9 rule fixes the **scorer**: faithful = best feasible sub-assignment, remainder 0. But if the scorer picks the best feasible subset while the **engine** picked an arbitrary one, the scored assignment is not the executed assignment, and execution loss absorbs the difference — mislabelled as worker underperformance when it is engine ordering. **The two rules must agree, and the S9 ruling as stated does not yet say which side is authoritative.**
3. **It is order-deterministic, not random** — insertion order is stable across runs for a fixed instance — so it will not show up as variance. It will show up as a constant, invisible bias toward whichever segments happen to be registered earliest, identical in every cell. That is benign for *between-cell* contrasts (it cancels) and not benign for the reported allocation, the K-disclosures, or any per-segment analysis.

**Recommended resolution, cheapest first:** make the deferral explicit and logged — when `can_handle_task` refuses, record `(task, agent, timestep)` as a deferred-assignment event, so realised-vs-intended is reconstructible rather than inferred. Then S9's rule states explicitly that **scoring uses the realised assignment** (what executed), with the deferred set reported alongside. That keeps the scorer honest about what happened rather than about what was asked for, and it makes the engine's choice auditable instead of silent. The alternative — making the engine choose the best feasible subset — puts oracle-like knowledge in the harness and should be rejected.

════════════════════════════
(2) YOUR ACCEPTANCE RULING — ENDORSED, AND I CHECKED THE PARSER SEAM YOU FLAGGED
════════════════════════════
Machinery-green-live + full-DAG dry-run is sufficient evidence of *assembly*, and re-specifying "end-to-end completion" as a study **outcome** rather than an acceptance criterion is correct — completion is a thing the manager does or fails to do, and making it an acceptance gate would have meant tuning the environment until the manager succeeded, which is the knob-tuning failure in its most consequential form.

**On your own candidate for what live exercises that dry-run stubs cannot: you are right that the parser seam is the one that matters**, and it is the seam where a stub is least representative — stub text is written by us and satisfies our own format by construction, while real worker output is where the 38-shapes finding came from. The live bundle's real worker text is therefore load-bearing evidence in a way the rest of the live run is not. **One thing to add rather than a finding:** the dry run proves DAG traversal, the live run proves the parser survives *one* model's output on *one* episode. Neither establishes parser robustness across cells, and the NO_METHOD cell (n=0 executed) changes the artifact contract the parser was built against. Record that the parser's evidence is single-episode and re-check it at the first NO_METHOD run.

════════════════════════════
(3) THE FOUR IN-FLIGHT RULINGS — CHANNEL-SAFE
════════════════════════════
**Bulk assignment into the action space: correct on confound grounds.** Dribbled assignment confounds the manager's allocation decision with its action-rate, and action-rate is not the studied variable. **The absent-is-not-same assertion semantics are right** — an action available in one cell and absent in another is a different action space, and asserting *presence-set equality* rather than *usage equality* is the correct form, since usage is behaviour and behaviour is the DV. Asserting usage would have frozen the thing being measured.

**Board fidelity: the three constraints are the right three**, and the departed-worker line as *intended* semantics is defensible — inherited state on a board naming a worker who is gone is exactly the staleness-by-succession the design is about, and it is in-scene rather than instrumented. Worth one guard: that line renders an opaque id, so it cannot leak coverage; if a future board ever rendered a role or capability alongside, it would.

**Capacity via `can_handle_task` after the pure-time mapping measured false:** right call, and superseding a mapping *because it was measured* rather than argued is the discipline working.

════════════════════════════
(4) THE seg_01 STALL AND THE S9 PRE-RULING
════════════════════════════
The stall is recorded as observation-not-finding with P14 discipline, and I checked it cannot be read as more — it is single-episode, single-seed, with no comparator, and the record says so. **It stays an observation.** My only note: it should not be cited as motivation for the S9 infeasible-assignment rule, because a rule motivated by an uncorroborated observation acquires that observation's weight. The rule stands on its own (infeasible assignments must be scored deterministically regardless of whether we have seen one stall), and it is stronger stated that way.

On the S9 rule itself: **faithful = best feasible sub-assignment, remainder 0** is right, and F1 above is the condition it needs to be safe — the scorer's "best feasible" must be reconciled with the engine's realised subset, or the rule silently credits the manager with a better sub-assignment than the one that ran.

════════════════════════════
(5) COMPARABILITY MODULE / (6) THE ~30 MIN NUMBER
════════════════════════════
Three-negatives-one-positive is the right structure and matches the S5 pattern that has worked twice — the positive proves the assertion runs, the negatives prove it can fail, and distinct messages prove they fail for distinct reasons.

**On ~30 min/completing-episode — I can sanity-check the arithmetic but not the estimate.** With the 174s/task planning figure noted in-flight and a ~16-task spine, planning alone is ~46 min, which exceeds 30 — so the 30 comes from completing episodes where the manager bulk-assigns and planning is amortised over fewer decisions. That is consistent, but it means **the number is conditional on the bulk-assignment ruling holding and on the manager not dribbling**; a manager that reverts to per-task assignment lands nearer the 174s×N figure. For an authorization input I would state it as a **range with its condition** — "~30 min when assignment is bulk; up to ~45–50 min if the manager dribbles" — rather than a point, since the authorization is what gets spent if the condition fails. One episode is a thin base for either number, and the six-launch ledger shows five did not complete, so the estimate rests on n=1.

════════════════════════════
VERDICT
════════════════════════════
**PASS on S8's deliverable.** F1 is blocker-class for S9 rather than for S8 — the wiring is correct, but the scoring rule S9 is about to implement cannot be safe until realised-vs-intended is logged and one side is declared authoritative. The parser-evidence scope note and the runtime-range framing are limitations.

**What I verified vs took on report:** verified independently — all three core diffs read in full, the done-tasks/ready-tasks ordering that makes the slot argument work, the failed/pending slot paths, `can_handle_task`'s two branches, occupy-after-check ordering, `get_ready_tasks`' insertion-order return, and the board line's rendered content. Taken on report — the six-launch ledger, the 174s/task figure, the dry-run traversal, and the live bundle's contents.
