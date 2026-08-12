# Truncation audit — did any bundle end before its swap? (RR)

**Question (LS):** `end_workflow` was handed to every worker and the stakeholder in
`COMMUNICATION_TOOLS`, against its own docstring, and the inline comment records an
episode killed one timestep before a scheduled event. Every finding this phase is
corpus-first, derived from existing bundles. **Are those bundles exposed, and did any
of them truncate?** Decided from the bundles, not from when the fix landed — the
history was condensed and dates are unreliable. Read-only.

## Verdict: NO bundle truncated. The exposure was latent, never realised.

**No finding needs re-deriving or withdrawing.** This does not go to the researcher.

### All 18 study bundles ran the full horizon

`records/R2/run_cell{0,1,2,3,4,U}_seed{3,23,36}.json` — 6 cells × 3 seeds.

```
horizon = 22 for all 18; timesteps seen = 0..21 on all 18; n(timestep_completed) = 22 on all 18
t_swap  = 3  for all 18; every bundle reached it
swap event at exactly t=3 in 15/15 swap cells (cells 0-4)
cellU: no swap event, BY DESIGN -- cell_config = {"swap": false,
       "role": "unswapped control — the replacement effect itself"}
```

The check rests on a count that would be **lower** under truncation
(`n(timestep_completed)`), not on the absence of a termination event — so it is a
positive signal, not an unfalsifiable null.

**Swap detector validated on a known-positive case before use**: `cell0_seed3`,
whose arrival event I had read by eye (`t=3`, `["removed w_8fcf6e", "added
w_e350ed"]`). The detector fires there; only then was it applied to the other 17.

### `end_workflow` was never invoked, and the absence is meaningful

```
across all 36 run bundles on disk:   end_workflow   0 occurrences
control, same COMMUNICATION_TOOLS list:
   send_message          2,605 occurrences across the 18 study bundles
   get_workflow_status      67 in a single bundle
```

Sibling tools from the same list appear in the thousands, so **tool activity is
recorded in this bundle format** and 0 is a measurement rather than a blind spot.

### The one short run anywhere is a legitimate finish, not a truncation

`records/S8/run_seed7.json` — 18 timesteps of a 22 horizon. Not truncation:

```
task_board_final : 16/16 completed        outcome: n_missing 0, n_unstaffed 0
last timestep    : success=True, error_message=None
end_workflow     : 0
```

The workflow finished its work at t=17 and the engine stopped. (The two S8 files
named `..._FAILED` and `..._INCOMPLETE` are self-labelled and no finding rests on
them.)

## What this audit CANNOT establish (limitation)

**Whether `end_workflow` was absent from the worker toolset in these runs, or
present and simply never called.** Both produce 0 invocations, and the bundles
record tool *calls* rather than tool *inventories*, so the two are
indistinguishable from this evidence.

That does not weaken the verdict — no run truncated either way. It does mean I
cannot certify the tool was unavailable, only that it was never used. The practical
consequence is forward-looking: **anyone re-running on a pre-fix checkout is still
exposed**, and the current checkout is not (the append is commented out in
`communication_di.py`).

**A bundle should record each agent's tool inventory, not only its tool calls.** One
line at setup, and it converts this limitation into a check. Recorded as optional.

## Method note

My first pass reported `all passed t_swap: False` — from a collector that returned
`None` for all 18 rows, because I read `timestep` from the event's `payload.id`
(`"timestep_0"`) when it is a top-level field. **The same empty-collector failure
this project has now logged four times.** What caught it was that the null was
*visible* — a `None` column on every row — rather than plausible-looking. That is
the argument for printing the intermediate quantity rather than only the verdict it
feeds: a collector that fails to empty produces a clean, wrong answer, and the only
defence is that the emptiness is on screen.
