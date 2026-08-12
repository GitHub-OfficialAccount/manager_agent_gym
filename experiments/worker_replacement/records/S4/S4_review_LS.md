# S4 — Lead-scientist review: PASS (with one correction against my own assignment)

Reviewed: commit c46d585 (`finance_scorer.py`, `test_finance_scorer.py`, `records/S4/`).
Criterion read first: BACKLOG S4 + HARNESS_SPEC_v2 §4.1/§4.3/§2 + my assignment's
definitional pin (faithful-execution reference point; losses sum identically).

## Verified (by me, directly)

1. **Acceptance re-run: PASS** — exhaustive enumeration of all 65,536 allocations of the
   committed 8-segment/4-worker instance THROUGH the production `score()` (§A honoured);
   `oracle ≥ score ≥ worst` with zero escapes; **both bounds attained** (RE's addition
   beyond the acceptance text — right call: unattained bounds are vacuous and a constant
   scorer would pass the raw inequality). Suite parity: 292 / 1 pre-existing / 2 skipped.
2. **Decomposition: exact and separable** — sum residual 0.00e+00; faithful-reports case
   shows execution loss exactly 0 with allocation loss surviving (0.348252) — the terms
   are genuinely distinguishable, not just summing.
3. **The signed-execution finding REPRODUCED INDEPENDENTLY through the real API**
   (probe alongside this file): segment seg_02 (corporate), IRB truth ≈ 57.0M, uncovered
   worker's faithful SA ≈ 76.8M (+34.8% overstatement); reporting 0.8× its own faithful
   value lands nearer the truth → **execution loss −0.26965**, sum identity holds
   (allocation 0.348252 + execution −0.269650 = total 0.078602). The mechanism is exactly
   as RE described.
4. **Single-source by identity:** IRB `capital_requirement` is the S1 object; SA lookup is
   S3's `sa_risk_weight`; no third copy.
5. **Oracle precondition** (non-binding capacity) stated in the docstring with its
   consequence; S5 asserts it per instance.

## Adjudications

- **The finding stands, and it corrects MY assignment framing.** I wrote that the
  decomposition "is the instrument that would DETECT the fabrication regime." Wrong, per
  RE's counterexample: a fabricated number landing nearer the truth than the worker's own
  fallback registers as NEGATIVE execution loss — a fabricator can be REWARDED by this
  term. The decomposition ATTRIBUTES; §6's value/trace/absence assertions DETECT.
  Spec updated (§4.1, "the execution term is signed") so the correction is in the
  governing document, not just this review.
- **Exhaustive-at-8 over sampled-at-9: accepted as flagged.** The enumeration establishes
  the scorer's bound property; instance-size generality follows from the per-segment
  algebra, not from enumerating a larger case. No 9-segment run required.
- **Keeping the negative case documented while the acceptance case amplifies AWAY from
  truth** (so both losses are positive for the hand-check): correct handling — the
  surprising example is recorded inline rather than quietly swapped out.

## Taken on report (assigned to the reviewer)

- The decomposition algebra independently (the cancellation argument in the docstring).
- Cross-document consistency of `score_report`'s shape with METRIC_AND_SENSITIVITY_SPEC.
- Whether §4.1's new signed-term text says everything the finding requires.
- Anything neither RE nor I looked for.

Verdict: **PASS.** → reviewer-reproducer for independent review.
