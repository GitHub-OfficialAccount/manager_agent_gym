# S6 — Lead-scientist review, round 2 (RE's F1/F2/F3 fix commit 2504b1d): FAIL — findings, all reproduced

Verified before the findings: all four acceptance suites PASS; suite parity 292/1/2;
max_effect_share_of_oracle = 0.295 > MDE on the committed instance; strict count 3
(seg_00/01/02, all corporate = the shared class); K2 re-read confirms strict 3 at k≤3,
rejection at k=4; F3's oracle boundary now takes phase= and raises on inconsistent
workers; F1's trivially_anchored labels present.

## Finding 1 (P10 / byte-identity): the committed gate report is STALE

`records/S6/gate_report_seed101.json` says `clip_flagged_segments: []`. Calling the
committed code on the committed instance NOW returns TWO flagged segments
(seg_01, seg_02 — zero-scoring workers w_68358d, w_e172a9 on each). The committed record
does not match what HEAD regenerates — some S6 records were not regenerated after the
final code state. This is exactly the regeneration discipline S7's admission criterion
formalises, arriving one step early. FIX: regenerate every S6 record from HEAD, and add a
freshness assertion to the gate acceptance — the committed report must be byte-identical
to a fresh run of the committed code.

## Finding 2 (the anchor's honest form): the output floor binds at the AGGREGATE, and nothing enforces it

The two divergence-selected segments carry within_output_floor: False (ratios 2.19,
2.84 > 1.379) — the F2 fix bought its max-effect by pushing PAST the per-segment floor
bound. But Basel's floor genuinely binds at the AGGREGATE (total IRB RWA ≥ 72.5% × total
SA RWA), and I computed the committed instance's aggregate: **1.496 — PASSES comfortably**
(individual segments either side, exactly how the real floor works). So the instance is
realistic by the published standard's honest form — but NOTHING computes, publishes, or
enforces the aggregate. FIX: gate computes + publishes + ENFORCES aggregate
truth/sa ≥ 0.725 per instance (admission condition); per-segment rows stay as disclosure;
sweep publishes the aggregate-ratio distribution. Spec reframed on my side (same commit).

## Finding 3 (design-consequential): the max-effect carriers are fabrication-blind, and selection can avoid this

seg_01/seg_02 = 2 of the 3 strict segments AND both in the clip region (uncovered
workers' fallback scores 0) — the measurable effect is concentrated exactly where the
execution term cannot penalise fabrication (§4.1). The divergence selection chose the
ratio>1 tail into clipping. The ratio<1 tail is strictly better: penalty up to 1−ratio
approaches 1 WITHOUT ever clipping (fabrication stays penalisable) and sits in the
labelled-unanchored direction rather than against the floor. FIX: divergence selection
PREFERS the ratio<1 tail, topping up with ratio>1 capped at the floor's implied 1.379
only if needed; the gate report cross-references strict ∩ clip-flagged so effect-carrier
fabrication-blindness is always visible; where it is non-empty, the S10 probe implication
is printed.

## Finding 4 (P10): RE's sweep statistics are not recomputable from the committed artifact

The DM quotes max-effect min 0.156 / median 0.214 / max 0.352; sweep_report.json carries
no max-effect key at all. FIX: per-instance max_effect_share in the sweep report.

## Nit

DM said "2 genuine, 3 trivial" anchors; the data shows 2 genuine, 2 trivial, plus one
zero-truth row with ratio undefined. Make the summary match the data (the zero-truth row
is its own category).

Verdict: **FAIL — back to RE with the five items above.** RR's scoped round 2 follows the
fixes.

---

# Round 3 (fix commit 4d7308a): PASS

Verified by me, directly: all four suites PASS; suite parity 292/1/2; the regenerated
gate report is fresh (clip flags consistent with live code — the freshness assertion RE
added CAUGHT ITS OWN MOTIVATING CASE on first run because it checks before rewriting);
strict ∩ clip-flagged = ∅ on the committed instance (was 2 of 3 — the tiered ratio<1
selection eliminated fabrication-blind carriers 40/40 → 0/40 across the sweep);
aggregate_output_floor_ratio = 1.3633 published and enforced (sweep min 1.1622, median
1.4503); per-seed rows committed (sweep_rows.json) — I verified from them that the FOUR
REJECTIONS are exactly the sub-MDE instances (0.0707–0.1239) and every admitted instance
clears the MDE (min 0.1433, median 0.241); K3 partitions four ways with a count
assertion.

Adjudication worth the record: RE DECLINED the knob turn to shared_class_segments=5
(39/40 admissions) because it concentrates 5 of 9 segments in one class — "a gate that
admits everything after enough tuning is not a gate." Settled at 4 (36/40) with the
rejections standing. That is the knob-disclosure rule applied by its own operator, and
the 36/40 outcome is more credible than 40/40 would have been.

Minor, for RR's round 2 rather than another loop: rejected rows carry
rejection_reasons: None — the reason ("max_effect below declared MDE") should be named
in the row.

Verdict: **PASS.** → reviewer-reproducer, scoped round 2 (F2 mechanism end-to-end + the
five fixes).
