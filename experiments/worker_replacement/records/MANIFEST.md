# Raw measurement records — Arm-3 belief layer

Every headline figure in `BELIEF_LAYER_DIAGNOSIS.md` should be reconstructible
from a file here. Until 2026-07-26 these records lived only in an ephemeral
session scratchpad and were not in the repository; a reviewer correctly found
that the figures had no reviewable provenance. This directory is the fix.

Each measurement has, where it exists: the **script** that produced it, the
**raw JSON** it wrote, and the **stdout log** of the run. Timestamps on the
files are the original run times, preserved.

## Two eras — do not mix them

`extraction_probe_prerebuild/` records the **OLD batched comparator**
(`raw_json_schema` / `or_structured` arms, packet-level batches, 25 Jul
10:44–13:23). These are genuine records of the extraction-mode investigation and
are **not** provenance for the v3.0 per-judgment comparator. Nothing in that
directory supports a v3.0 claim.

`v3_comparator/` records the rebuilt per-judgment comparator. These are the
records behind the figures quoted for v3.0.

## What each figure rests on

Reconstructed from `v3_comparator/stage_b.json`, which is self-contained —
each entry carries `samples`, `providers`, `set` and `truth`:

| figure | reconstruction | value |
|---|---|---|
| contradiction recall | `set=gate`, `truth=contradicts_fit`: 8 judgments × 40 | **319/319 returned verdicts**; 320 attempted, 1 `LLMInferenceTruncationError` |
| false contradictions, gate supports | `set=gate`, `truth=supports_fit`: 28 judgments × 40 | **12/1120 = 1.07%** |
| Stage A false contradictions | `stage_a.json`, 28 genuine-support judgments × 20 | **5/560 = 0.89%** |
| fallback-population rate | `fallback_rate_v2.out` | **49/239 = 20.5%** (74.4% before the wording fix) |
| detector on-population | `detect_control.json`, 7 cases × 20 | **140/140** |

Two corrections that follow from the records and supersede earlier reporting:

- Recall is **319 of 319 verdicts returned**, from **320 attempts**. The
  non-match is an inference error, not a wrong verdict. Quote both numbers; a
  bare 319/319 hides that an attempt did not return.
- The denominator is **1120**, not 1117.
- **380/380 is withdrawn.** It combined populations. The defensible detector
  figure is 140/140 on four unrecognised-format cases and three failure notices.

## The unscored clean sample — read this before quoting 1.07%

`stage_b.json` also contains `set=clean`: 35 judgments × 10 draws, carrying
`truth: null`. Because they had no truth they were never scored, and the run
reported only the gate figures.

Scoring them for contradictions alone: **94/350 = 26.9%**, with 23 of the 35
judgments producing at least one. On a population drawn to be ordinary rather
than adversarial, more than a quarter of draws returned `contradicts_fit`.

So 1.07% is the false-contradiction rate **on the labelled gate supports**, not
on what the comparator judges generally. The specificity problem was present in
our own records from 25 Jul and went unnoticed because a `truth: null` column
silently excluded the population that showed it.

## Which records survived a payload change, and which did not

A judgment fingerprint is a content hash over the whole payload, so adding any
payload field moves every key at once. `method_extraction` was added on 25 July
and did exactly that. What decided whether a record survived was whether it
persisted the CONTENT beside the key:

| record | keeps `payload`? | outcome |
|---|---|---|
| `stability_n20.json` | yes, all 237 entries | **recoverable** — re-keyed on content, 237/249 rejoin; the 12 misses are fallback judgments that did not exist when it was written |
| `stage_b.json` | no — `samples`, `providers`, `set`, `truth` only | **perished** — of 35 clean-set judgments only 16 still resolve, and all 16 are `profile_scope`; every `requirement_artifact` member is unrecoverable |

Same morning, same author, one record durable and one not. The seven
most-contradicting judgments in the clean set (10/10, 9/10, 9/10, 8/10, 7/10 and
two at 6/10, carrying 55 of its 94 contradictions) cannot be identified, so they
cannot be labelled, so the question they would have settled stays open.

The rule that follows: persist the content **alongside** the key, not instead of
it. Content-keying alone makes staleness less likely; content alongside the key
makes it recoverable. `probe_judgment_stability.exposure()` now joins on content
with the fingerprint as a fast path, and raises if any judgment KIND matches
zero rather than reporting a clean empty result.

## A phrase to distrust in these records

**"gate-diagnostic" means three different populations** across this directory
and the diagnosis, and each time it was misread the error ran upward:

- every clause judgment, ~44/cell — the version that inflated the first
  exposure table roughly fivefold
- clause text matching a frozen excerpt pattern, 9/cell — what
  `_matches_excerpt_pattern` (formerly `_is_gate_diagnostic`) counts, and the
  version behind the `E[dev] excerpt-match` column
- scored diagnostic relation rows, 3 per silent cell and **0 in the control** —
  the gate criterion itself

The clearest illustration: the exposure table credits `control_arm3i_q` with 9
"gate-diagnostic" judgments and E[dev] 1.10, while that cell contributes nothing
whatever to the recall gate. Scripts archived here predate the rename and still
import `_is_gate_diagnostic`; they are kept as-run and will fail loudly on
import rather than silently computing something else.

## Files

`v3_comparator/`

- `stage_a.{py,json,out}` — 28 genuine-support judgments × n=20, interleaved
- `stage_b.{py,json,out}`, `stage_b_report.py`, `stage_b_clean_sample.json` —
  gate set 36 × n=40 plus clean sample 35 × n=10
- `gate_truth.json` — 36 gate judgments with expected stance. **Keyed on a
  different fingerprint set from `stage_a/b`; the join is empty.** Use
  `stage_b.json`'s own `truth` field instead.
- `factorial.{py,json}` — interleaved 2×2, payload × cache, with provider and
  `cached_tokens` per row
- `narrowed_Morph.{py,json,out}` — pinned-endpoint control on Morph, 40 rows,
  with the cache manipulation check in the log
- `ladder2_l0prime.json`, `ladder.py`, `ladder2.py`, `l0_index.py`,
  `ladder_L0.out`, `l0prime.out` — L0 vs L0-prime
- `fallback_rate{,_v2}.{py,json,out}` — fallback-population false-contradiction
  rate before and after the wording fix
- `detect{,_v2,_control}.{py,json,out}` — method-presence detector and its
  on-population control
- `abc_isolate`, `abc_true_isolate`, `abc_probe`, `regress`,
  `regress_interleaved`, `reversed.out`, `cachecheck`, `morph_recheck`,
  `verify_fix`, `wiring_check` — batch A/B/C asymmetry and regression checks
- `label_coverage.{py,json}`, `reconcile_counts.{py,json}` — clause-question
  population and label coverage (2026-07-26)
- `stability_n20_STALE_JOIN.json` — the stored stability file whose
  `requirement_artifact` fingerprints no longer match `corpus()`. Kept because
  the stale join is itself a documented finding; **not** a usable measurement.
- `wording.{py,json,out}` — prompt-wording candidates. **Halted work.** Ranked
  on a payload the 2×2 showed interacts with the prompt; kept as a record, not
  as a result.

Not committed: `rendered_v3/` and `replay_reps/` (56 MB of bulk replay output)
and `gate_s1.out`. The gate session log is withheld deliberately — the k=3 gate
sequence is blind until all three sessions complete.
