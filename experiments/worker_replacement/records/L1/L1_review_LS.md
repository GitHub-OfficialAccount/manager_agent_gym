# L1 — LS REVIEW of `220bbfb`

Read the criteria first, then the source, then the acceptance output — never the DM's
description of what the step was meant to do. What follows states what was VERIFIED versus
taken on report.

## Verdict: criteria (a)–(e) MET in the live path. TWO FINDINGS, one of them a live hazard.

Not `[x]` yet: finding 1 must be fixed and RR's review is outstanding.

---

## What I verified in source, not on report

- **(a) MET, and better than the criterion I wrote.** `AgentInterface.refusal_reasons()`
  accumulates and `can_handle_task` is DERIVED (`not self.refusal_reasons(task)`), so the
  boolean may short-circuit and the reason cannot. `CapacityBoundedAIAgent.refusal_reasons`
  appends to `super()`'s list rather than replacing it. The engine computes reasons at the
  refusal site (`engine.py`) and carries `refusal_reasons` + `agent_load` on the event; the old
  concurrency fields are kept for bundle continuity and explicitly demoted in a comment. **The
  masking RR found is structurally impossible now, not merely absent.**
- **(b) MET in the live rendering, which is where I checked it** (`records/L1/
  rendered_cell0_timestep0.txt:229`):
  `- w_26f14e: concurrent tasks 0/1 (frees when a task finishes) · segment allotment 0/3
  (SPENT FOR THE EPISODE — finishing one does NOT free another)`. Two dimensions, distinct
  units, release semantics carried on each.
- **(c) MET.** `task.refusal_count`, `last_refusal_timestep`, `last_refusal_reasons` are set on
  the TASK at the refusal site — a fact about the assignment that happened, not a view derived
  from present capacity, which is what I asked for and is the version that cannot silently
  revert.
- **(e) MET.** `SEGMENT_TASK_CLASS` declared on the nine scored segments; `is_metered` tests
  the class; `engine_set == scorer_set` asserted as strings (the UUID/str normalisation RE
  hit is real and their proposed rule is right). Both remediation names from the natural
  experiment are regression-tested, neither metered.
- **(d) PARTIAL — see finding 1.** Strip list published with a reason per pattern; seven
  positive controls recorded; the comparability assertion in section D is driven against the
  six real bundles and rejects both an all-blind set and a one-cell-blind set. **That part is
  solid and is the load-bearing half of acceptance (ii).**

---

## FINDING 1 (blocking) — the cross-cell RENDERING constancy check is HOLLOW

`_fixed_observation` (`check_load_feedback.py:740`) builds:

```python
AgentLoad(agent_id="w_aaaaaa", held=3, capacity=3, unit="segment tasks", available=True)
```

The current schema's fields are `agent_id`, `available`, `dimensions` — **there is no `held`,
`capacity` or `unit`.** Pydantic's default is `extra='ignore'`, so all three are silently
dropped, `dimensions` stays empty, and `render()` returns the empty-case branch. Confirmed by
construction:

```
AgentLoad(agent_id='w_x', held=3, capacity=3, unit='segment tasks').render()
  -> '- w_x: (load unavailable)'
```

and it is in the committed record: `fixed_state_load_block: "- w_aaaaaa: (load unavailable)\n-
w_bbbbbb: (load unavailable)"`.

**So the fixed-observation constancy check compares `(load unavailable)` against itself six
times. It is constant because it is EMPTY, and would pass identically if the load feature had
never been built.** The refusal half is worse in one respect: it is a hardcoded literal
carrying the **pre-L1 wording** (`"w_aaaaaa is at capacity (3/3 segment tasks)"`), so it also
no longer resembles what the live code emits.

**This is RE's own positive-control rule, violated in the commit that introduced it** — a null
compared against a null, passing. It is the checks-hollow family again, and the published
record shows `(load unavailable)` where a reader would take it for a load-block sample.

**Not fatal to the step,** because section D covers the same claim against real bundles in both
directions. **Fix:** build the fixture from a real `load_report()`, and assert the fixture's
rendered load block is non-empty before comparing it across cells — the positive control the
rule requires.

## FINDING 2 (live hazard, and the more valuable one) — `AgentLoad` silently discards unknown keys

The live path is `AgentLoad(**agent.load_report())` (`manager_agent/interface.py:213`). With
`extra='ignore'`, **any future drift between `load_report()`'s keys and the schema's fields
degrades SILENTLY to `(load unavailable)` instead of raising.** That is exactly how the fixture
broke, on a path that only a test touches; the same mechanism sits under the path the manager
actually reads. A worker whose load block silently became `(load unavailable)` would be
invisible in every check that looks for the block's PRESENCE.

**Fix: `model_config = ConfigDict(extra='forbid')` on `AgentLoad` and `LoadDimension`.**
**Production test:** a data model that silently discards supplied fields is a defect — strict
schemas fail loudly at the boundary. This also makes finding 1 impossible to reintroduce.

## Minor, non-blocking

`segment allotment 0/3 (SPENT FOR THE EPISODE — ...)` reads oddly at **0/3**, where nothing is
spent. The parenthetical is a property of the COUNTER, not of the current value. Suggest
`0/3 used this episode (does not reset when a task finishes)`.

---

## On RE's flagged consequence: manager-created work is charged NOTHING

**RE's choice is right and I am accepting it.** Metering created work is the alternative that
silently shrinks a worker's feasible set below the oracle's model and charges regret against an
optimum for a problem the manager was not solving — the latent harm (e) exists to prevent.

**But "visible in the record" is not a detector.** In 18 pre-L1 episodes four created a task,
one each; L1 raises the rate of exactly that behaviour, and RE is right that at volume the
regret denominator stops meaning what it means now. **So L3 gains an explicit requirement
rather than an intention:** count manager-created tasks per episode, report the distribution,
and state the denominator's validity condition as a predicate. If any episode creates more
segment-equivalent work than the allotment model assumes, that is a finding to report, not a
number to average. I would rather watch it in L3 than pre-emptively cap it — capping would be
scripting the manager, which the standing directive forbids.
