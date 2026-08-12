# The display-name join, measured — exposure, and a logging gap that hides it

**Status:** finding, not a fix. Recorded so the step that fixes it starts from
measurement rather than from the grep.

## The sites

Four analysis sites derive segment identity from the task's DISPLAY NAME:

```
finance_scope_report.py:204, :332   board.get(f"Risk-weighted assets — {sid}")
finance_logging.py:472              (seg, f"Risk-weighted assets — {seg}")
finance_fabrication.py:230          task_name = f"Risk-weighted assets — {segment_id}"
run_finance_episode.py:133          segment_lookup[f"Risk-weighted assets — {sid}"]
```

**The fourth is DRY-RUN ONLY** — it sits inside `_install_dry_run_stubs()`, called
under `if dry_run:`. I originally ranked it first on the grounds that it runs
during an episode; it runs during a *machinery* episode. LS caught that and the
correction stands: **no display-name site executes during a live run.** The three
analysis sites matter more, because they run over bundles we publish from.

`finance_split.py` (L2a) does not: it takes identity from `index.segment_task_ids`.

## Why it is live rather than latent

`RefineTaskAction` carries `new_name` and executes `task.name = self.new_name`.
**The manager renames tasks.**

```
refine_task actions requested across the 18 scope bundles :  9
  of which carried a new_name                             :  8
task_refined events logged                                :  8
```

The eight renamed:

```
'Output floor check (72.5%) with corrected IRB figures'
'Exposure data preparation'                                  (x2)
'Aggregate risk-weighted assets'                             (x2)
'Output floor check (reconcile portfolio totals first)'
'Exposure data preparation (with provided data)'
'Exposure data preparation and completeness check'
```

**Every one targeted an upstream or downstream task. Zero hit a segment: 0 of 18
bundles have a missing segment name on the board.** So four name-based joins have
been correct for eighteen episodes **by luck**.

`'Aggregate risk-weighted assets'` is one editorial decision from matching the
segment prefix. **Criterion (e) was a manager-created name that accidentally
MATCHED; this is the same predicate from the other side — a manager rename that
accidentally STOPS matching.**

## The population, stated precisely (§B, on the number produced while investigating §B)

**8 is a count of rename REQUESTS**, from the manager's own parsed action, where
`new_name` is an explicit field. That population IS resolvable — it is the
requested-versus-applied distinction, not an unresolvable one.

Whether all 8 were APPLIED is not recorded. `RefineTaskAction` sets the name
unconditionally once the task resolves, so requested ≈ applied here, but the
bundle does not say so.

**The 8 = 8 agreement with `task_refined` is accidental**, not corroboration:
those are refines that changed a DESCRIPTION, a different population that happens
to have the same size.

## The logging gap, and it is worse than "no `name_before`"

`task_refined` is recorded **inside `if self.new_description:`**. `task.name` is
mutated outside it.

1. **A rename that changes no description emits NO EVENT AT ALL.** Not a record
   missing a field — a mutation with no record.
2. **When the event does fire, its `task_name` is the name AFTER the rename**, so
   it silently reports the new name as though it had always been the name. A join
   on that field is correct-looking and misdescribes history.

So a rename is not reconstructible from a bundle, which is precisely why the
name-based joins cannot be audited for having silently missed — **the thing that
would tell us the join broke is the thing that is not logged.**

## Recommended scope for the fixing step

1. The three ANALYSIS sites move to `index.segment_task_ids`.
2. `RefineTaskAction` records a rename: `name_before` / `name_after`, emitted on
   the NAME change rather than nested under the description change.
3. The dry-run site, last — real, but it cannot corrupt a live run.

**None of this blocks L3** (LS ruling): no display-name site executes during a
live run, so an L3 bundle cannot be corrupted by it. The exposure is to analyses
run over those bundles afterwards, which can be re-run once the sites are fixed.
