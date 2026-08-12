# Run-CLI Arm Refactor — Contract for Research Engineer

> **BASELINE STALE as of 2026-08-06; AUDITED as of `f758aa2`** — the frozen baseline `6282f85`
> predates later run.py edits. Audit result: all clauses PASS, with one defect found and fixed
> (a duplicate `belief_model` field carrying a different meaning than the manifest's — removed;
> manifest's effective value is the single source). Caveat: §0.1's "run_one internals untouched"
> no longer holds byte-for-byte (the metadata dict lives inside run_one). Frozen copy:
> `manager_agent_gym/experiments/ds_reroute/archive/RUN_CLI_CONTRACT_2026-07-24.md`.

_Author: Lead Scientist · 2026-07-24 · frozen baseline: manager_agent_gym @ `6282f85`_

This specifies a **behavior-preserving** refactor of `experiments/ds_reroute/run.py`
so each ladder arm is a first-class, list-takeable CLI entity and the confirmatory
matrix is one reproducible, auditable command. It supersedes nothing in OVERVIEW.md
or ARM3_SPEC.md; it is CLI plumbing only. No arm's *behavior* changes.

## 0. Non-negotiable invariants

1. **Behavior preservation.** Every (arm, observability, controls, seed) cell the new
   CLI produces must call `run_one(...)` with **byte-identical** kwargs to what the
   current explicit flags produce for the same cell. `run_one` internals, `run_dir`
   naming, `ObservationPolicy` composition, and the observability↔perturbation
   separation are untouched.
2. **Do not fuse the two IVs.** Observability (config channel) and representation aid
   (`observation_aid`) stay orthogonal and separately serialized in the manifest
   (OVERVIEW §5). An "arm" is a convenience label over the aid axis; it must not
   collapse the factorial structure in stored data.
3. **Re-freeze.** Commit the refactor as a new frozen reference once parity is proven;
   the preregistration pins that new commit. The specificity gate at `6282f85` carries
   over unchanged (it is an offline replay that never invokes `run.py`).

## 1. `--arm` replaces `--observation-aid`, becomes list-taking

Canonical arm names (match ARM3_SPEC §13.1 ladder), each mapping to the current
`observation_aid` string — mapping is the identity for all but `native`:

| `--arm` value | resolves to `observation_aid` |
|---|---|
| `native` | `none` |
| `summary` | `generic_summary` |
| `summary_log` | `append_only_summary_log` |
| `ledger` | `atomic_evidence_ledger` |
| `arm3i_noq` | `arm3i_noq` |
| `arm3i_q` | `arm3i_q` |
| `arm3t` | `arm3t` |

- `--arm` takes `nargs="+"`. Default `["native"]`.
- Keep the raw `observation_aid` strings (incl. `none`) accepted as aliases, and keep
  `--observation-aid` as a hidden single-value deprecated alias for one cycle, so
  existing docs/scripts don't break. `native → none` must keep `run_dir` suffix empty
  (today `none` yields no aid suffix — preserve exactly).

## 2. Loop and axes

Run the cross of the **explicitly listed** axes only:

```
for seed in --seeds:
  for observability in --conditions:        # already nargs="+"; rename to --observability, keep --conditions as alias
    for arm in --arm:
      run_one(condition=observability, observation_aid=resolve(arm), seed=seed, ...)
```

`--perturbation`, `--artifact-reporting`, `--worker-noise` stay as flags (they are
modifier axes, not arms — this preserves orthogonality and avoids a name explosion).
The existing coupling guards (`--worker-noise` requires `control`; `no_method` only for
the toolset lever) are unchanged.

## 3. `--matrix NAME` — frozen sparse-cell preset

The confirmatory matrix is a **sparse** set of (arm, observability) cells, so it cannot
be expressed as one dense `--arm × --observability` cross without generating meaningless
cells. `--matrix` names the exact sparse set as a **code constant**:

- `--matrix` is **mutually exclusive** with `--arm` / `--observability` / `--seeds`
  (error if combined — no silent merge).
- It resolves to an explicit list of `(arm, observability, seed)` cells at fixed
  `perturbation=toolset_to_screening, artifact_reporting=standard, worker_noise=none`.
- The frozen arm set + its content hash + the matrix name are stamped into **every**
  cell's manifest.

### `confirmatory` preset — PROVISIONAL default (pending prereg lock)

Do not treat these contents as final; the human researcher's three prereg decisions
(scope, primary endpoint, false-positive breadth) may adjust them, after which we
re-freeze. Recommended default:

- Method arms @ `silent`: `native, summary, summary_log, ledger, arm3i_noq, arm3i_q, arm3t`
- References: `(native, control)`, `(native, full)`
- False-positive controls: `(arm3i_q, control)` — add `(arm3t, control)` if breadth chosen
- Seeds: `102, 103, 104, 105, 106`

**Explicitly deferred, NOT in this refactor:** `ledger_pad` (Arm-2-PAD, ARM3_SPEC §7).
It is a *new aid* (atomic ledger + content-free padding matched to a stored Arm-3
padding schedule) with **no current behavior to preserve**, so it is a separate
implementation task, not a rename. Leave a `# TODO(arm2-pad)` marker only.

## 4. Manifest additions (the load-bearing audit part)

Add to each run's `manifest.json` (currently missing):

- `arm` — the canonical arm name (alongside the existing `observation_aid`, not
  replacing it).
- `matrix_name` and `matrix_hash` — or `null` when not run via `--matrix`.
- `code_commit` — `git rev-parse HEAD` of `manager_agent_gym` at run time (this is
  what makes a run verifiably against the frozen reference).
- `arms_spec_hash` — hash of the frozen arm-definitions table.

## 5. Parity verification (required before re-freeze)

- Add `--plan-only`: print the resolved cell list and, per cell, the full `run_one`
  kwargs — **without** invoking any LLM or engine.
- Diff `--plan-only` output for representative cells against the equivalent
  current-flag invocation; require identical kwargs. Include at least: `native/silent`,
  `ledger/silent`, `arm3i_q/silent`, `native/control`, `native/full`, `arm3i_q/control`.
- Full targeted DS-REROUTE test suite green; Ruff clean.
- One cheap sanity live run of a single cheap cell (e.g. `native/control` seed 102) to
  confirm the manifest additions populate and `code_commit` is correct.

## 6. Out of scope

- No change to `run_one`, scenario, observation-aid builders, observability, or
  perturbation logic.
- No Arm-2-PAD implementation (separate task).
- No confirmatory seeds — stop after parity + re-freeze; the confirmatory run waits on
  the preregistration.
