# Preserved run outputs — rescued from the `outputs/` ignore, 2026-07-27

`experiments/worker_replacement/.gitignore` line 1 is **`outputs/`**. Every run artifact written there has
therefore been **beyond `git add` from the moment it was created** — not uncommitted, but
unstageable. `records/` sits outside that ignore, which is why these live here.

These directories back **every figure reported for the Arm-3 belief layer on 2026-07-26/27.** They
were preserved before the `mag_fixes` worktree was retired; without this copy, retiring it would
have destroyed them.

## The collision this fixes

Two different runs occupied the **same path** in two different checkouts:

| checkout | `outputs/toolset_to_screening_silent_arm3i_q_t3_seed101/arm3_state.json` |
|---|---|
| `mag_fixes` | the **v3.0** trace — first `contradicted` at t=10 |
| `manager_agent_gym` | an older **v2.6** trace — never renders `contradicted` |

So deleting the worktree would **not** have produced a missing file and an error. It would have
produced **the older trace silently answering to the newer trace's path** — anyone re-running the
binding analysis afterwards gets a trace with no contradicted cells and concludes the finding does
not reproduce, with nothing indicating that anything moved. That is the stale-artifact failure that
forced the PREREG §7.4 withdrawal, set up to recur at scale.

Both are preserved here under **version-explicit names**. Distinct `md5sum` on `arm3_state.json`
confirms they are different runs:

```
eba631e6   v3.0_silent_arm3i_q_seed101/arm3_state.json      1.2M
5781f821   v2.6_silent_arm3i_q_seed101/arm3_state.json      728K
1a6e86cb   v3.0_noisefloor_r2/…/arm3_state.json             804K
```

## Contents

| directory | what it is |
|---|---|
| `v3.0_silent_arm3i_q_seed101/` | **The v3.0 trace.** Extraction lands Batch A's contradiction at t=10; the t=10 and t=15 binding observations; the t=12 *"best fits portfolio_analyst"* deliberation; the 1004-row aid accounting (22 `contradicted`, 694 bare-prior, 784 at the +0.5 boundary, 214 carrying completions); `arm3t` simulated at t=10. Config tag `a4ba33dab82b`. |
| `v3.0_noisefloor_r2/` | **The same-configuration re-run.** `r_check` 0.8206 against run 1's 0.7317, \|Δ\| = 0.0889, entirely attributable to Batch C going to `risk_analyst` at t=11 for throughput reasons. Confirms the propagation mechanism directly and replicates the t=10 binding observation (n=1 → n=2). |
| `v2.6_silent_arm3i_q_seed101/` | The older comparator's trace at the same scenario/seed. Source of the v2.6 t=12 support-side routing observation. **Not** interchangeable with the v3.0 trace — see the collision above. |
| `corpus_expansion/` | `items_v1.json` (six items) and `items_v2_argued.json` (two argued-equivalence items) — the full labelling deliverable: verdicts, rules, written reasons, determinability flags, exposure status, pre-committed-rule metadata. `cannot-judge` = 0/6 on v1. Existed in exactly one directory before this copy. |
| `shape_c/`, `shape_dump/`, `input_scope/`, `parent_recall/`, `nonmethod_family/`, `ordinary_contradictions/`, `reasoning_field/`, `judgment_stability/`, `smoke101_5b19b5b/` | Probe records backing the payload-shape comparisons, the reasoning-field instrumentation A/B, the affirmation and contradiction tables, and the per-judgment stability figures. |

## Reading rule

**Cite these paths, not `outputs/`.** `outputs/` is ignored, is not shared between checkouts, and — as
above — the same path can hold different runs. A figure traced to `outputs/…` cannot be verified by
anyone else; a figure traced here can.

## Related

The generation path is the underlying defect: probes and runs write into `outputs/` by default, so
their products are unstageable unless someone notices the ignore. Committing more often would not
have helped. `records/` was already the established remedy — this is the same fix previously applied
when the provenance records were found uncommitted.
