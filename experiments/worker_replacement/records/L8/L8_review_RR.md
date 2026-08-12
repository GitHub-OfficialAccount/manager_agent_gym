# L8 review — the display-name joins converted to task id (RR)

Standing rule 7. Three analysis sites converted, plus a core change so a rename leaves a
trace.

**Verdict: the conversion is right and complete, and the core change is the better half of
it. NO BLOCKERS. Two findings: one is a claim in a docstring that I supplied and have since
retracted, and the other is that the conversion fixed mutability without fixing the silent
default underneath it.**

## Verified

All three analysis sites now join on id, and nothing live joins on a name:

```
finance_scope_report.py   -> _board_by_task_id(), keyed on r["task_id"]
finance_logging.py:183    -> "KEYED BY ID, NOT NAME"
finance_fabrication.py    -> task_key = segment_tasks.get(segment_id) from index
finance_split.py (L2a)    -> already took identity from index.segment_task_ids

remaining name constructions, checked and correct:
  finance_env.py:467         task CREATION -- constructs the name, not a join
  run_finance_episode.py:133 DRY-RUN ONLY, correctly demoted after LS caught the ranking
```

**The core change is the part I'd keep.** `RefineTaskAction` captures `name_before` *before*
mutating, emits a new `task_renamed` event, and adds `name_before`/`name_after` to
`task_refined`. And the reason given is the right one: analysis no longer joins on the name,
**so the event is emitted not because the DV needs it but because without it "no rename
occurred" and "a rename occurred and was not logged" are the same observation.** That is a
record-integrity argument rather than a metric one, and it is the stronger of the two.

**The control was built first and fired against the code as it stood** — name join 9 hits → 8
on a rename while the id join stays at 9. Under the rule this phase just added, that is a
control demonstrating its own negative case, and it is why the conversion is not a change
nobody can show was needed.

## Finding 1 — a docstring carries the claim I retracted (limitation)

`finance_scope_report._board_by_task_id`:

> *"And the prefix is not unique — one real bundle has TEN rows matching "Risk-weighted
> assets" for NINE segments, **so a collision does not even need a rename**."*

**I supplied the escalation behind that sentence and have since retracted it**
(`name_key_ambiguity_RR.md`). Measured across all 18 bundles: the tenth row is
`"Risk-weighted assets — seg_08 standardised recalculation"`, a manager-created remediation
whose name *starts with* the prefix but is a different string. **Every segment's exact name
appears exactly once, in every bundle. There is no collision under an exact-key join.**

**The sentence conflates two different things**: an exact-key lookup does not collide, and a
*prefix predicate* captures a non-segment task. The second is real and already realised at
`finance_env.py:171`, which is how the remediation got charged against the segment allotment.

**Recommend the accurate form:** *"a prefix predicate over the name captures tasks that are
not segments — one real bundle has ten prefix-matching rows for nine segments, and the tenth
is a manager remediation. Under an exact-name key it does not collide; it MISSES."* Same
conclusion, and it stops the record asserting a collision that is not there.

## Finding 2 — the id join fixed mutability, not the silent default (limitation)

`finance_fabrication.py`:

```python
task_key = segment_tasks.get(segment_id)
tool_calls = calls_by_task.get(task_key, [])
readable = readable_by_task.get(task_key, False)
```

A missing or partial index yields `task_key = None`, and `None` then indexes two further
`.get(default)` calls. **The docstring names this mechanism for a rename — "silently yields NO
tool calls and readable=False, which here reads as a worker that produced nothing" — and the
same thing happens for a missing key, which it does not name.**

**The same key is guarded inconsistently in two modules.** Demonstrated:

```
bundle with index.segment_task_ids removed:
  finance_split.split()            -> RAISES "bundle carries no segment index"
  finance_fabrication.scan_bundle() -> NO RAISE, 9 rows, task_key None throughout,
                                       tool_calls 0, readable None
```

**Scoped honestly:** I measured **0** fabrication hits in that state, so this does **not**
manufacture hits — the value test is the hit-creating leg and it does not use `task_key`. What
a missing key silently zeroes is the trace and absence detectors, which **classify** hits
(tool-calling vs in-head). So the exposure is **unreliable hit classification, not phantom
hits**, and no current bundle lacks the index.

**Fix is one line and consistency is the argument:** `finance_fabrication` should raise on a
missing index exactly as `finance_split` does. Two modules reading the same key with opposite
guards is the condition under which the weaker one gets used and believed.

## Assessment

**The conversion does what it claims and the reasoning is on the record where the next reader
will find it.** Both findings are about the justification and the guard rather than the join:
one asks the record to stop asserting a collision I put there, the other asks the new key to
be guarded as strictly as the old one was in the neighbouring module. **Neither blocks L8.**
