# S8 — environment assembly: the decisions, and what falsified the first versions

Companion to the acceptance transcripts in this directory. It records the choices
that are not obvious from the code and, in three cases, the measurement that
proved an earlier choice wrong. The code comments carry the same reasons; this is
the reader's-eye version.

## 1. The capacity mirror was wrong the first time, and a dry run caught it

S7 ruled C = 3 and S4's oracle is computed under that cap. The runtime has to
mirror it, or agents are scored against the optimum for a problem they were not
solving and every regret number inherits the mismatch.

**First version: pure episode time.** 3 post-swap timesteps x 1 task per worker
per timestep = 3 segments per worker; x 3 post-swap workers = the 9 segments
exactly. This is what the backlog obligation asks for ("engine-native, episode
time, not a bolted rule") and it reads convincingly.

**It was false.** A zero-API dry run through the real engine measured
`w_6f6097` completing **four** segment tasks. Segment tasks stay READY after the
window closes, and a worker simply picks one up later. Episode time bounds how
much work an episode can *contain*; it does not bound any individual worker's
*share* of it, which is the whole content of C = 3.

**Second version: the worker's own capacity method.** `CapacityBoundedAIAgent`
declines a fourth SEGMENT task through `can_handle_task` — the same mechanism
that enforces `max_concurrent_tasks`, consulted by the engine, not a rule bolted
onto the manager. Realised counts are now 3/3/3.

The worker is never switched off (the core-tool rule): it still takes upstream
and downstream tasks, and it still answers every segment it holds. Only a fourth
segment is refused, which is what a capacity constraint *is*.

A consequence worth naming: because the cap is now enforced by the agent, horizon
SLACK became safe. While the horizon was the only bound, every extra timestep
silently loosened C.

## 2. Two core plumbing bugs had to be fixed to get there

Both are in `CHANGED.md` with verification.

1. **`can_handle_task` was never called.** It exists, is documented, and checks
   `max_concurrent_tasks` — and no execution path invoked it. Separately,
   `current_task_ids` was pruned on completion but never appended on start, so
   the capacity branch could not have fired even if it had been called.
   `max_concurrent_tasks` was inert across the whole fork.
2. **`register_ai_agent` hard-coded `AIAgent`**, bypassing the registry's own
   `_agent_classes`, which `create_agent()` does use. So
   `register_agent_class("ai", X)` had no effect on any agent arriving on the
   timeline — which is every worker in a roster-swap study.

Fixing (1) broke one integration test, correctly: freeing the agent's slot in
`_update_workflow_state` (which runs *after* ready-task selection) made an
A->B->C chain advance one task per two timesteps. The slot is now freed at
completion, inside `_execute_ready_tasks`.

## 3. The first real episode failed, and the fix was structural

**What happened.** 2 of 16 tasks completed. Five worker executions died with
`MaxTurnsExceeded` (10 turns) on the two discretionary upstream tasks, which
asked for reconciliation "against the team's stated approval scopes" and a
portfolio-wide attestation. Both invite the worker to go ask its teammates, and
both did. Because all nine segment tasks depended on the full upstream layer,
every segment died with them.

**The wrong fix** would have been to shorten the prompts. **The fix taken** is
two-part:

- The two discretionary tasks are rewritten to be answerable from the task text
  alone. A task whose completion requires unbounded coordination is not a
  reliable DAG node.
- The nine segment tasks now depend on the **fixed** upstream tasks only. The
  study's entire payload should not sit behind a task that can fail. The
  discretionary tasks remain in the DAG — they give the incumbents pre-swap work
  and keep the shape realistic — but nothing depends on them.

`WORKER_MAX_TURNS = 16` is now set explicitly rather than inheriting the SDK
default of 10, and is disclosed as the real constraint it is.

## 4. The parser refuses to guess, and its own acceptance found a fabrication path

The convention is two lines (`method:` and `rwa:`). A parse failure is a MISSING
report — score 0, named in `missing_segments`, and a run event — never a guessed
extraction. A lenient parser that digs a plausible number out of malformed prose
converts a WORKER failure into a SCORER success invisibly, and the
allocation/execution decomposition would then credit the recovered number to the
worker's competence.

The acceptance caught a real hole in the first implementation. With anchored
matching alone, a deliverable reading

    rwa: 4200000 ... On reflection, rwa: 4300000

matched **once** and parsed to 4,200,000 — the number the worker had *abandoned*.
The isolated ambiguity test passed, because there both values sat on clean lines.
Fixed by splitting the two roles: only a conventional line may SUPPLY a value,
but an unanchored contradiction check scans the whole text, and any disagreeing
occurrence makes the deliverable ambiguous. Ambiguous is refused.

## 5. Leakage is asserted, and the assertion is proven non-vacuous

If a private calibration reaches a card or a task description, the competence gap
is public and the study measures nothing. All 45 calibration values are searched
across all 24 public strings (cards, capabilities, every task description): 0
found. The search is then proven non-vacuous by confirming all 4 holders carry
their values in their PRIVATE system prompt — without that second check, a bug
that dropped provisioning entirely would show as a clean leak report.

## 6. The acceptance criterion was amended, and why that is not a waiver

The step's original acceptance said "an episode runs end-to-end to completion".
The landed episode did not: the manager parked seg_01 on a worker already at
capacity three and never moved it, while another worker had a free slot.

LS ruled the CRITERION mis-specified rather than the run inadequate. The reason
is worth keeping: "runs to completion" makes HARNESS acceptance hostage to
MANAGER competence, and manager competence is the measured variable. Under the
original wording a stalling manager fails the harness, and — worse — a harness
change could be made to rescue it. That is the wrong incentive pointed at the
wrong object.

Amended, in three parts:
  (i)   machinery green on a LIVE episode (attempt 6);
  (ii)  full-DAG traversal including the downstream chain proven in the ZERO-API
        dry run — 16/16 completed, 9/9 parsed, scored end to end, so the chain
        the live episode never reached is exercised deterministically;
  (iii) completion is a STUDY OUTCOME reported per bundle, never a harness
        criterion.

`test_finance_bundle.py` now reflects this: the RESULT line adjudicates machinery
only, and completion is printed under "OUTCOME (reported, NOT adjudicated)". The
machinery floor is "at least one segment executed by a POST-SWAP worker" —
deliberately a floor and not a count, because "all nine" would smuggle the
completion criterion back in under another name.

A record correction that belongs here rather than only in a thread: while this
was being adjudicated I reported "all eight acceptance modules PASS". The bundle
module was at that moment FAILING, on precisely the criterion under adjudication.
The substance was the centrepiece of the report; the summary sentence was looser
than the substance.

## 7. What the assembly does NOT establish

- It builds the **accurate-card default only**. The study cells that make a card
  stale are not built here.
- The episode proves the machinery runs. It says nothing about whether the
  manager allocates *well* — that is the study.
- One episode on one seed is an assembly proof, not evidence about behaviour. No
  quantity in the run bundle should be read as a result.

---

## 8. R1: what the repair changed, and the two things it taught

R1 replaced the competence mechanism after S10's probe exposed that it had none.
The full ruling and cost are in the commits; two lessons belong here because they
are about method rather than about finance.

### Absence-assertions can only catch what the author thought to name

E3a required the worker to be unscripted. I removed the procedural clauses and
wrote string assertions over six of them, then reported item 4 met.

It was not met. The REPORT-FORMAT CONVENTION still said "your deliverable MUST
contain these two lines ... do not omit either line" — imperative, in both the
system prompt and the task text, and behaviourally identical to the clause I had
just removed. It survived because it existed for a LEGITIMATE reason
(deterministic parsing).

The mechanism of the miss, stated generally: **I named the clauses by their
INTENT and the survivor was identical in EFFECT.** Every assertion I wrote was
looking for instructions-about-method; none was looking for anything-that-compels-
output. A check built from a list of remembered phrases cannot find the phrase
its author did not think of, which makes absence-assertions a DRIFT GUARD and
never an initial-state check. The initial state has to be established by someone
READING the artefact.

That is now the division: reads establish, assertions guard.

### An unprohibited option is not an available one

The fix was to give refusal a parseable form (`method: none` / `rwa:
unavailable`) rather than to forbid it. The line that does the real work is not
the form itself but:

> "That is a legitimate outcome and is recorded as one; it is not a failure to
> follow the format."

A worker reading a format block reads any deviation from it as non-compliance.
Offering a form without saying it is legitimate leaves declining technically
possible and practically unavailable — and a decline rate measured under that
condition is still partly a measurement of our own instruction. **Availability
stated, not merely unprohibited.**

The same distinction runs through the decline's handling downstream: a decline
and an unreadable deliverable both score 0 and are never summed, because they are
different behaviours. Filing a judgement the worker communicated under "unparsed"
would erase the signal the unscripting exists to expose.
