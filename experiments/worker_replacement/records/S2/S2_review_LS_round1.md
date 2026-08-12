# S2 — Lead-scientist review, round 1: FAIL (one finding, reproduced; fix is one line + one test case)

Reviewed: commit 0c6fb29 (5 core files + test + CHANGED.md archive). Criterion read first:
BACKLOG S2 acceptance + HARNESS_SPEC_v2 E4 ("arrival visible via a roster event rendered
into the manager's observation") and §5 ("roster arrival held constant across all cells").

## FINDING (reproduced, records/S2/S2_ghost_repro_LS.py + _output.txt): the announcement ghost-repeats on every timestep after the swap

`apply_scheduled_changes_for_timestep` (registry.py) early-returns on any timestep with no
scheduled changes — BEFORE the `self._last_applied_changes = []` reset, which sits after the
early return. The engine's per-timestep expression (engine.py:427) reads the stale record
unconditionally. Reproduction:

    t=2: engine would pass []
    t=3: engine would pass ['removed alpha', 'added beta']
    t=4: engine would pass ['removed alpha', 'added beta']   <- BUG
    t=5: engine would pass ['removed alpha', 'added beta']   <- BUG

Consequences: (a) the block's own contract is violated — the schema field and the rendered
header both say changes "applied at THIS timestep", and at t=4 that is false text in the
manager's prompt; (b) the event semantics the spec requires (a roster EVENT, one-timestep,
held constant across cells) become a persistent banner, a standing prompt differential
between swap and unswapped cells beyond the event itself; (c) the falsely-updating
"timestep N" label misdates the swap for any post-hoc reader of the prompt.

Why the delivered acceptance test could not catch it: `_apply_swap` applies only the swap
timestep, and every prompt build takes an explicit roster list — the registry→engine path
is never exercised on a quiet timestep after an eventful one.

## Required fix

1. Reset `self._last_applied_changes = []` unconditionally at method ENTRY (before the
   early return), so a quiet timestep yields an empty record.
2. Add the missing test case: through the registry path, after applying t_swap, apply
   t_swap+1 and assert the engine expression is empty and the rendered prompt at t_swap+1
   carries NO roster block.

## Everything else examined in round 1 — sound, and carried forward to round 2

- The delivered acceptance test passes as-is (exit 0, re-run by me).
- The spec-over-backlog setter call: CORRECT. The step()-keyword route measurably broke 27
  tests; E4 requires the render, not the plumbing; precedence stated in the file.
- The reason-leak exclusion: CORRECT and structural — the observation path is fed
  (action, agent_id) and cannot carry `change.reason`; the string path is untouched.
- No-event byte-identity: holds on the delivered test (1241-char prompts identical).
- Verdict on these is provisional until round 2 re-review of the fixed commit; the full
  293-test suite parity claim will be re-verified then as well.

Verdict: **FAIL — back to RE for the one-line reset + the missing test case.**
