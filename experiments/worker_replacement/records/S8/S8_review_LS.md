# S8 — Lead-scientist review + acceptance ruling: PASS with one pre-specified amendment

Reviewed: the S8 commit chain through 9030110 (build 5626aad; interims 72918c3, 3627a42,
d2c988d, 5264c20, 4a302de, 7e47528; completion 9030110). Criterion read first: BACKLOG S8
+ HARNESS_SPEC_v2 E1/E3/E4/E5(as amended in-flight)/E6, §4.3 (capacity), §5, §4.1.

## THE ACCEPTANCE RULING (RE's options (a)/(b)/(c) → (a)-AMENDED)

The written criterion "an episode runs end-to-end to completion" was MIS-SPECIFIED when
written: it makes harness acceptance hostage to manager competence, which is the measured
variable. Option (b) is rejected for RE's own reason (tuning the thing we measure);
option (c) is rejected because capacity slack would break C=3's load-bearing properties
(binding universality per the K6 curve; the structural successor value). Amended
acceptance, which the evidence SATISFIES:

1. **Machinery assertions green on a LIVE episode** — attempt 6: provenance hash,
   roster_arrival_announced strong-form at t=3, worker_run_completed for predecessor
   (pre-swap) and successor (post-swap), capacity 3/2/3 ≤ C, task count 16, parser seam
   complete (8 parsed / 1 missing / 1 unstaffed, re-parse reproduces exactly).
2. **Full-DAG traversal proven in the ZERO-API dry run** — verified by me directly:
   16/16 tasks completed including "Aggregate risk-weighted assets" and "Capital adequacy
   report", 9/9 segments parsed, scored end-to-end (achieved 7.8393 vs capacitated oracle
   8.2791). The chain the live episode never reached is exercised deterministically.
3. **Workflow completion is a STUDY OUTCOME, reported per bundle — never a harness
   criterion.**

Pre-specified amendment (RE, S1-style): `test_finance_bundle`'s RESULT drops the
completion criterion — completion becomes a reported outcome field; the machinery
assertions stay pass/fail. (As committed, the module FAILS on exactly the criterion under
adjudication; RE's "all eight modules PASS" was loose phrasing — the substance was
disclosed prominently in the same report, but the record should note the discrepancy.)

## THE FIRST SUBSTANTIVE OBSERVATION (recorded with P14 discipline)

seg_01 sat ready on a full worker from t=9 to horizon while a slot was free elsewhere;
the manager acted throughout (4 assigns, 6 inspects) and never made the reassignment;
AssignTaskAction overwrites unconditionally, so the move was available. **One episode,
one seed, one model — an OBSERVATION, not a finding.** Its σ implication (unstaffed
segments as cross-cell variance) stands flagged for the pilot. The E5 board ruling is
unchanged: the inference was available; this model did not make it; that is data.

## NEW SCORING-SEMANTICS ITEM (routed to S9)

Under the current decomposition, seg_01's zero would land in EXECUTION loss (faithful
score counts s(seg, assignee) as if executed) — but assigning a FOURTH segment to a full
worker is an ALLOCATION failure: the worker could not run it, not would not. Rule for
S9: **assignments beyond a worker's cap score 0 in the FAITHFUL term**, putting the loss
in allocation loss where it belongs — RR's capacity-starvation warning, prevented from
inverting.

## Core diffs (S2-grade scrutiny) — all three CLEAN, CHANGED.md entries verified present

- **engine.py**: `can_handle_task` consulted at task start (the method existed and was
  never called — `max_concurrent_tasks` inert fork-wide); slot APPENDED on start (was
  never appended, so the capacity branch could not fire); slot freed at completion, not
  in `_update_workflow_state` (which runs after ready-selection — the A→B→C
  one-task-per-two-timesteps bug, correctly caught by the suite). Rationale in place.
- **registry.py**: `_agent_classes.get("ai", AIAgent)` — the scheduled-add path honoured
  the registered class for the first time; fallback preserves stock behaviour. This bug
  would have bitten EVERY timeline-arriving worker, i.e. every successor in this study.
- **tasks.py**: assignment identity only ("Assigned to: <id> / (unassigned)"), no
  capacity vocabulary, no coverage content — matches the E5 ruling and the three
  asserted constraints.

## Verified (by me, directly)

All nine experiment acceptance modules re-run: eight PASS; `test_finance_bundle` fails
only on the completion criterion this ruling amends. Full suite 292 / 1 pre-existing / 2
skipped. Dry-run full-DAG traversal verified from the artifact. Bulk-assignment effect
visible (eight segments done by t=9 vs seven by t=13 in attempt 5). Comparability module:
absent-is-not-same fired correctly against the attempt-5 bundle.

## For the record

Run ledger: six launches — two real findings (a1: payload-behind-discretionary-tasks;
a5: the manager is the throughput bottleneck, which invalidated planning numbers I was
carrying too), two killed by rulings arriving mid-flight, one self-charged harness
timeout, one landed. **Authorization number: ~30 min per completing episode** (attempt 6:
2057s to t=9 deadlock + cheap manager-only tail; 12–14 working timesteps typical).

Verdict: **PASS** (with the pre-specified bundle-RESULT amendment). → reviewer-reproducer
for the full step.

---

## Amendment verified (327f3ba)

RESULT adjudicates machinery only; completion prints under "OUTCOME (reported, NOT
adjudicated — this is the study's dependent variable)" with every incomplete task
itemised; the live-machinery floor is deliberately "at least one segment executed by a
post-swap worker" — a floor, not a count, so completion cannot creep back in under
another name. Both bundles PASS (machinery): live 12/16 and dry-run 16/16
(S8_dryrun_bundle_assertions.txt = the standing evidence for amended criterion (ii)).
Suite 292/1/2, re-run by me. RE also wrote the modules-PASS phrasing correction into
S8_DESIGN_NOTES.md §6 rather than leaving it in the thread.

**S9 pre-ruling, adopted from RE's flag:** "beyond-cap" is defined SET-LEVEL — an
allocation assigning k > C segments to a worker is infeasible in (k−C) of them, and the
faithful term scores the BEST FEASIBLE SUB-ASSIGNMENT with the remainder at 0. The
alternative (score the one that did not run) lets ENGINE START ORDER pick the victim,
coupling allocation loss to execution timing — the exact coupling the decomposition
exists to break. RE implements set-level in S9.
