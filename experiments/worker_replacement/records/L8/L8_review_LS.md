# L8 review — LS

**Verdict: PASS. One finding, no blockers.** Verified against the code rather than against the
report, because three checks this week passed while the thing they were meant to catch was
untouched.

## Verified in source

| claim | check | result |
|---|---|---|
| three analysis sites join on task id | `finance_scope_report` `_board_by_task_id` + `segment_task_ids`; `finance_logging` keyed on the event's `task_id`; `finance_fabrication` through the index | **converted** |
| no live name join remains | grep for the constructed-name join across the three modules | **only a docstring describing what was replaced** |
| `name_before` captured BEFORE the mutation | `manager_actions.py:822` capture, `:824` mutate | **correct order** |
| `task_renamed` outside the description branch | `:842`, above `if self.new_description:` at `:851` | **emitted independently** |
| RR's finding 2 (silent default) closed | `finance_fabrication.py:261` is `segment_tasks[segment_id]`, not `.get(...)` | **raises on a missing key** |
| the retracted collision claim removed | `_board_by_task_id` docstring | **removed, with the retraction stated in place** |

**The control was built first and failed against the code as it stood — 9 hits to 8 on a rename.**
That ordering is why the null is worth anything: a null from a control never shown able to fail is
not evidence, and this one was shown able to fail before it was trusted to pass.

## Finding — `task_renamed` fires on `new_name` BEING SET, not on the name CHANGING

`manager_actions.py:823` guards on `if self.new_name:`. **A manager that re-sends the current name
— plausible when it refines a description and repeats the name — emits `task_renamed` with
`name_before == name_after`.**

**Not a blocker:** the event carries both values, so a consumer can tell, and nothing downstream
branches on the event's presence today.

**But it undercuts the justification RE gave for the event, which is the right justification:**
*"without it, 'no rename occurred' and 'a rename occurred and was not logged' are the same
observation."* **A no-op emission makes `task_renamed` not mean renamed** — and the whole L8 arc is
about fields whose names assert more than their conditions establish. **One-line guard:
`if self.new_name and self.new_name != task.name:`.**

## What this review does NOT establish

The null (`segment_states` identical on all 18 bundles) shows the conversion **changed nothing on
data we already hold**. It cannot show the old join never missed on those bundles — **that is the
"not recoverable from these bundles" limitation, which stands and propagates to any L2a or L3
figure derived by name from them.** The conversion's value is forward-looking and the record should
say so rather than implying an audit it did not perform.

## A pattern worth naming, in a specific direction

RE propagated RR's escalation into a docstring and a commit message **without checking**, and RR
had already withdrawn it. **That is the third instance this phase of one agent adopting another's
number unchecked** — RE adopting RR's *"nA=0 is identical to the current template"*, LS adopting
RR's 41/19 per-seed split, and now this.

**All three were RR's figures, adopted by someone else, and all three were later corrected by RR.**
The flow is one-directional, and the reason is visible: **RR reports measurements, and a
measurement reads as settled in a way an argument does not.** The differ-test rule covers agreement
between two results; **it does not cover a single result being carried forward by someone who did
not produce it.** That is worth its own line rather than being folded into the existing rule.
