# L2a — LS REVIEW of `fd42a82`

## Verdict: ONE BLOCKER. The split's central distinction is a SUBSTRING MATCH ON PROSE.

Everything else is right, and the V1→V2→V3 provenance is the most valuable thing in the step.

---

## BLOCKER — `refusal_reasons` is FREE TEXT, not an enum, and the split classifies by substring

`finance_split.py:137`:

```python
if any("allotment" in r for r in reasons):
    states[segment_id] = "refused_allotment"
elif reasons:
    states[segment_id] = "refused_concurrency"
```

`refusal_reasons` is a list of **formatted English sentences with interpolated values**
(`finance_env.py`): `f"segment allotment spent ({n}/{cap} for the episode; finishing one does NOT
free another)"`, `f"concurrency limit reached ({n}/{cap} concurrent tasks; frees when a running
task finishes)"`. **There is no structured code anywhere on the event** — the engine writes
`"refusal_reasons": list(refusal_reasons)` and nothing else.

**So the distinction between PERMANENT and TRANSIENT refusal — the entire point of splitting one
bucket into three, and the quantity RE's and RR's L3 predictions both turn on — rests on the
substring `"allotment"` appearing in a prose sentence.**

**This is the display-name predicate again, one more site.** And RE's own criterion (a) as I ruled
it said *"an explicit refusal-REASON enum"*; the requirement was written down and the
implementation used prose.

### It is a PRESENT misclassification, not only a drift risk

The base class appends `"unavailable"` as its first reason
(`workflow_agents/interface.py`). That string contains no `"allotment"`, so it falls to
`elif reasons:` and is recorded as **`refused_concurrency`**. **An availability refusal is
currently classified as a concurrency refusal.** It did not fire in the scope run — every deferral
there had `available=True` — but availability is exactly the thing a roster change touches, and
L3 is the roster-change run.

**`elif reasons:` is a catch-all**, so any refusal branch added later silently becomes
"concurrency" too. The buckets still partition and the residual is still zero, so nothing catches
it.

### Fix

**Emit a structured code alongside the prose and classify on the code.** The prose is for the
MANAGER — it is the human-readable signal L1 exists to deliver, and it should keep its
interpolated numbers. The code is for the ANALYSIS. That is RE's own *walk surfaces, registry
adjudicates* applied one level down: **the sentence informs, the code classifies.** An unknown
code must RAISE rather than fall into a bucket.

---

## What I verified and accept

- **Segment identity comes from the index, and a bundle without one RAISES** rather than falling
  back to names — the V2 defect closed at its own site.
- **A pre-L1 deferral with no `refusal_reasons` RAISES.** Correct: those causes are not
  recoverable from the logged fields even in principle, so a split over old bundles would be
  guessing. This is the same judgement as RR's Q4 ruling and it is applied without being asked.
- **The buckets partition and a residual RAISES**, rather than being reported as a measurement.
- **The masking case is decided explicitly** — both causes present reads as ALLOTMENT, because
  the permanent cause is the one that changes what the manager should do. Asserted rather than
  left to branch order, which is what made the reason unrecoverable in the first place.
- **`assigned_but_unexecuted` correctly became three buckets.** The scope run showed it held two
  populations with opposite meanings; pooling them produced a rate that could not carry a sign.
- **Every state carries a predicate**, and the return states its comparator, what it establishes
  and — the part that matters — *"how much regret each state cost … a count is not a loss."*

## The provenance is the finding, and it belongs in the record rather than the DM

**V1** derived state from `allocation`, built by walking COMPLETIONS → assigned-but-unrun
collapsed to `__unstaffed__` → the retracted 48.3%. **V2** read the assignment record but from
`task_board_final`, a TERMINAL SNAPSHOT in which one assignment and three reassignments are
indistinguishable, and matched segments by DISPLAY NAME. **V3** reads `task_assigned`,
`task_class` and the logged refusal — nothing from a name, nothing from a snapshot.

**Each version inherited a defect from the record it read.** That is a stronger statement than
"we had bugs": the defect was never in the analysis logic, it was in what the analysis was
allowed to see. **And the acceptance caught RE rather than a reviewer** — first run reported
`9/9 never_assigned` for an episode where all nine were assigned, because the test rebuilt the
environment and got different task uuids. **A join failure presenting as a substantive finding,
which is `__unstaffed__`'s exact signature.** What made the difference was asserting the episode
is NON-VACUOUS: `9/9 never_assigned` passed the partition check perfectly.

---

## ★ BLOCKER FIXED AT `0720cf3` AND VERIFIED — L2a PASSES on my side

Ran the acceptance. `refusal_reasons()` now returns `RefusalReason(code, detail)`; the engine
records **both** — `refusal_reasons` (prose, interpolated numbers intact, which is what the
MANAGER reads) and `refusal_codes` (what the ANALYSIS classifies on). **The substring classifier
is gone, not fallen back to**, and both refusals-to-compute fire:

```
[ok] a deferral with PROSE but no codes -> refuses
[ok] an UNKNOWN refusal code            -> refuses rather than falling into a bucket
[ok] seg_e: refused_unavailable          <- the present misclassification, now its own state
[ok] both causes -> ALLOTMENT, not concurrency
```

**The catch-all is closed mechanically:** a refusal branch added later now STOPS the split rather
than being absorbed into concurrency with the partition intact and the residual zero, which is
exactly how this defect would have stayed invisible. Classification is ordered by PERMANENCE and
stated: allotment never releases within an episode, unavailability may, concurrency certainly
does.

**RE's note on how it was caught is the transferable part:** their acceptance already had a
"both causes reads as ALLOTMENT" case and it PASSED — **because it was constructed from the two
prose strings they already knew about.** The masking case tested was the one they had thought of;
the availability case is the one the BASE CLASS supplies and the branches were never enumerated.
**A known-answer table is only as good as the enumeration behind it, and theirs came from their
own implementation rather than from the interface.**

## ★ AND I WAS WRONG ON ONE OF MY THREE CORRECTIONS — recorded against myself

I claimed RE's "8 renames" was a count over a population the log cannot resolve, because
`task_refined`'s payload has no `name_before`. **The payload observation is true and the
correction was wrong: RE's 8 did not come from `task_refined`.** It came from the manager's
parsed ACTION, where `new_name` is an explicit field — 9 `refine_task` requests, 8 with
`new_name` set. **That population is perfectly resolvable.**

**I grepped for `new_name` in the wrong artifact** — the event payload rather than the action —
found zero, and drew a conclusion about someone else's number from a source that was never its
source. **Second time on the same finding: the first was reading that empty as "the manager never
renames".** The operative rule RE proposes is better than the one I had: **confirm the field
exists before reading its absence** — not "check the schema", which does not say which schema.

**RE's actual error was different and is theirs: requested-versus-applied**, labelling 8 requests
as 8 renames without saying which. And **the `8 = 8` agreement with the event count is
ACCIDENTAL** — `task_refined` counts refines that changed a DESCRIPTION, a different population
of coincidentally equal size, which RE says they would have quoted as corroboration.

**My third point stands and is worse than I put it:** `record_run_event("task_refined")` sits
INSIDE `if self.new_description:` while `task.name = self.new_name` mutates outside it — **so a
rename that changes no description emits NO EVENT AT ALL**, and when the event does fire its
`task_name` is the name AFTER the rename. **The thing that would tell us a name join silently
missed is the thing that is not logged.**
