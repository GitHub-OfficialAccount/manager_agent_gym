# M1 de-risking run: silent competence swap

**Question:** when a worker's system prompt is silently degraded mid-episode,
does the artifact quality stream actually separate the swap condition from a
no-switch control? This gates all detection experiments — if an independent
judge can't see the degradation in the artifacts, no manager-side detection
result is interpretable.

## Design

- Workflow: `icaap` (worker `documentation_lead` present from t=0, historically
  the most-assigned agent).
- Perturbation: silent `PromptSwap` at `--swap-timestep` (default 8) replacing
  the documentation lead's prompt with a degraded-but-superficially-normal one
  (`prompts.py`).
- Conditions: `control` vs `swap`, same seeds.
- Preference weight-update dynamics are deliberately disabled (single
  non-stationarity; confounds return in the M3 attribution study).
- Observation contract: default `ObservationPolicy` (worker system prompts
  redacted) — recorded in `manifest.json`.
- Out-of-band `DetectionProbe` runs each timestep on the manager's observation;
  its judgments never enter the manager's context.

## Run

```bash
uv run python -m experiments.m1_derisk.run --conditions control swap --seeds 42 \
    --max-timesteps 20 --swap-timestep 8
uv run python -m experiments.m1_derisk.score_artifacts
```

## Outputs (per run dir)

`manifest.json` (ground truth), `probe_reports.json`, `task_completions.json`,
`artifacts.json`, and after scoring `artifact_scores.json`.

Run directories are named `{condition}_t{swap_timestep}_seed{seed}`, so
timestep variants never overwrite each other. Control runs ignore the swap
timestep during the episode but record it as `reference_boundary`, giving
control artifacts the same matched pre/post split in the scorer.

**Go signal:** target-worker post-swap scores drop clearly below both its own
pre-swap scores and the control condition's post-boundary scores, with other
workers flat. **No-go:** streams overlap → fix the degraded prompt or the judge
before building detection conditions.

Known caveats:
- Worker `actual_cost` is $0 for models missing from litellm's price map —
  cost-based metrics are not meaningful here (quality-only study).
- The agent instance (pre/post-swap policy) is bound when a task **starts**;
  work in flight at the swap completes under the old policy. Analysis
  therefore attributes artifacts by `started_timestep`, not completion.
