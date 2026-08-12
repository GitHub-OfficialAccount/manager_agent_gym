# Study 1 — cell ordering and logging spec (research-engineer draft)

<!-- citation-check: superseded -->

_**Superseded record.** A pre-revamp draft whose rulings lived in BRAINSTORM; the modules cited below were deleted in the 2026-08-08 cleanup. Governs nothing._

**Status:** draft for the lead's design doc, per §97/§98/§100. Nothing here is a
ruling; the rulings are in BRAINSTORM. This is the buildable form of them, with the
engineering consequences stated where they bite.

**Scope:** "channel consumption under teammate change", main-effects only (§91).
Primary DV: allocation margin under the §89-clean estimator. Secondary reads: ask
propensity, refine reachability (reachability-only).

---

## 1. Cell ordering

§97 rules that "P2 passes" licenses **capability only**, and that
allocation-visibility is tested by the study's first cell, which doubles as its own
gate and is read before further cells run. That makes the ordering load-bearing
rather than cosmetic, because two different things can stop the study and they stop
it at different points.

```
GATE PAIR (2 SSRs, clean, no instruments)
  |  reads: P2 non-degeneracy -- capability established?
  |  PASS  = >=1 post-swap outcome correct DEMONSTRABLY via method B
  |  FAIL  = zero correct post-swap outcomes via method B
  |  3/3   = "capability established, outcome-channel signal absent"
  |          -- recorded as such, NEVER as non-degeneracy of the DV
  v
CELL 1  = control / no-channel  (announcement absent)
  |  doubles as the allocation-visibility gate
  |  reads: does the perturbation move the allocation margin at all?
  |  if the margin does not move here, no later cell can show a channel
  |  moving it, because there is nothing for a channel to move
  v
CELLS 2..n  (announcement present / stale; declaration absent; ask; refine)
```

**Why cell 1 is the no-channel cell and not the announcement-present cell.** The allocation-visibility
requirement asks whether the manager *can* respond to this perturbation. The
announcement-present cell confounds that with the announcement: a manager that
reallocates there may be responding to the announcement, not to the teammate. The
absent cell isolates the perturbation as the only available signal, so a moving
margin there licenses the requirement and a flat margin falsifies it cleanly.

**Consequence for run budget:** if cell 1 is flat, cells 2..n are unspent, not
wasted. That is the whole point of reading it first.

### Naming: "control / no-channel", and the string that must NOT change

Per §106/§107, cell 1 is named **control / no-channel** in prose and spec. It is a
scientific control — the absent-announcement condition carries **no ecological
claim**, because under the managed-migration anchor a real vendor version bump is
announced. Do not write "silent" in prose, and do not read the cell as modelling a
realistic deployment.

**The metadata value stays `silent` (§107 ruling, prose-and-spec only).** This is not
an inconsistency, it is the fix for one. Thirty corpus runs carry
`condition: "silent"` in `run.json`, and the §89-clean +0.611 estimate quotes exactly
those runs. Renaming the config value would make old runs stop matching the new tag,
and any re-derivation would silently lose them — the two-layout denominator failure
arriving by a second route. Any future alias must resolve **both** strings and be
documented where the tag is read.

---

## 2. Study-wide logging records

Four records, all cells including the gate pair. Each exists because a specific
claim is unrecoverable without it.

| # | record | fields | why |
|---|---|---|---|
| 1 | target's channel pulls | timestep, agent, task, call index within run | P2 split before/after the target's first pull (§93). Without it the P2 outcome read cannot be separated from the target having read something. |
| 2 | refine events | timestep, task, before/after description text | P2 split around the refine (§93), and the refine-reachability read. Before/after text because `refine_task` rewrites `task.description`, which is a **worker input** (`ai_agent.py:413-424`) — the change must be attributable, not just counted. |
| 3 | message → manager visibility | message id, sender, addressee as written, timestep, and **whether it entered the manager's rendered window** | The only record that establishes the manager *could* have consumed a message. `recent_messages` is `get_all_messages()[:message_window]` (`interface.py:161-164`), so entry into the window is a property of traffic volume, not of the message. |
| 4 | ask-reply addressing | reply message id, `to_agent` as written, whether it names the manager | §100: the adopted consumption interpretation is addressed-to-me + actionable-by-me, so a reply that is not manager-addressed is not in the consumable class. CHECK-4 measured 48/56 worker sends addressed to non-existent ids, so this cannot be assumed. |

**Record 4 has a build dependency, not just a logging one.** Making the reply
manager-addressed requires a worker-prompt instruction naming the manager's agent id.
The corpus shows workers do not spontaneously produce the id (2/56). The instruction
is part of the ask cell's manipulation and must be stated in the design as such —
otherwise the ask cell measures whether workers can guess an id.

---

## 3. Perturbation requirements (§92 + §98)

Two hard requirements, both testable before any study cell:

1. **Allocation-visible.** The manager must have an allocation reason to act.
   Rationale is the corpus, not taste: detection on `rerouted_share` costs ~4
   runs/arm, on the behavioural DVs 200–12000 (CHECK-2). A perturbation that is
   observable but carries no allocation consequence is unmeasurable at any n this
   project can pay for.
2. **Trace-distinguishable.** The substituted method must leave a distinct
   signature — distinct tool call and/or distinct computed truth, ideally both.
   A prompt-only style change with no signature fails the gate and the study even
   though it satisfies difference-not-deficiency.

**Gate criterion, operationalised (§98).** "Demonstrably via method B" =
the reported metric matches method B's computed truth and not method A's. Both
truths already exist: `_audit_total(reference, batch, "percentile")` and
`_audit_total(..., "zscore")` are computed side by side at `scenario.py:308-309`.
The criterion is therefore a comparison of existing numbers, not new instrumentation.

**NOT the `method:` declaration.** The 0/221 declaration-accuracy result was
validated against tool calls under the tool-swap regime and does not transfer to a
prompt-level method substitution. Declaration accuracy must be re-established under
the new perturbation before any cell leans on that channel.

---

## 4. Declaration-vs-trace accuracy count (free byproduct of the gate pair)

The gate pair already produces, per post-swap audit: the declared method (artifact
`method:` line), the tool actually called (`worker_run_completed` history via
`tool_call_reader`), and the computed truth under both methods. So a 2x2 of
declared vs actual falls out with no extra runs.

Report as: n checkable, n agree, n disagree, and the disagreement direction. At the
gate pair's n this establishes *whether disagreement occurs at all*, not a rate —
label it accordingly. A single false declaration is informative (it refutes 0/221's
transfer); zero false declarations across a handful of artifacts is not evidence of
accuracy and must not be written as if it were.

---

## 5. Two engineering facts the design should not re-derive

**Addressing does not control delivery to the manager.** `send_direct_message`
performs no recipient validation (`service.py:89-108`), and the manager's
observation is built from `get_all_messages()` (`interface.py:161-164`). A message
to a non-existent agent still reaches the manager's prompt, rendered as
`sender → receiver | type: content` (`structured_manager.py:274-281`). Addressing
matters for the *consumable class* (§100), not for delivery.

**Broadcasts render as `→ ALL`.** They are therefore not visibly someone else's
mail, which is why the one spontaneous interrogative broadcast in the corpus sits
in the consumable addressee class.

---

## 6. Printed-ordering convention (adopted; applied)

Every ordering that reaches stdout uses a **total** sort key `(-count, str(key))`.
`Counter.most_common()` and `key=lambda kv: -kv[1]` are not total and must not be
printed directly. Applied across all five check scripts and verified byte-stable
under `PYTHONHASHSEED` in {1, 7, 42, 99}.

---

## 7. P14 constraints on the upcoming perturbation build

Two standing constraints from §102, recorded here because they bind *my* build and
would otherwise be rediscovered late.

**Do not foreclose S6's revival path.** S6 is shelved, not buried, and its revival
needs exactly one thing: a **representation-sensitive consumer task**. The current
consumer is not one — `analyze_audit_artifacts`' reconcile branch extracts numbers
and returns `abs(robust − screening)` (`scenario.py:547-561`), which is why CHECK-3
returned a clean null. The build constraint that follows:

- the perturbation must not assume the consumer is numeric-extraction-only;
- the trace substrate must not render operands in a normalised form that destroys
  the surface variation a future representation-sensitive consumer would key on.

Neither costs anything now. Both are expensive to retrofit, because a normalising
renderer would have to be re-run against every episode to recover the variation.

**Keep the re-price path live.** CHECK-2's variance figures are old-corpus and get
re-derived once new-setup runs exist (S7 is shelved pending re-price, not retired).
Two things make that work:

- setup-specific constants are named and grouped at the top of
  `check_announcement.py` (`TARGET_TASK_KEY_SUFFIX`, `DEGRADED_METHOD_TOOL`), so
  hosting a new setup is an edit in one place;
- `collect()` counts and prints every skip by reason, and `check_variance` prints a
  loud `PRIMARY DV ABSENT` banner when no run yields `rerouted_share`.

The failure this prevents is specific and was verified by simulation: with a new
setup whose task keys no longer match, the old code would have priced the nine
secondary DVs and silently omitted the primary one, printing a table that looks
entirely normal. It now reports `75 skipped: no post-swap task with key ending
'_robust'` instead.
