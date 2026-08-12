# S1 — Lead-scientist review: PASS (with two required follow-throughs)

Reviewed: commit 9bc096a (`test_basel_reference.py`, `records/S1/S1_acceptance_output.txt`).
Criterion read first, per protocol: BACKLOG S1 as amended (three-tier fallback, tier stated in
record) and HARNESS_SPEC_v2 E2 / §4.1 / §9.

## Verified (by me, directly)

1. **Acceptance check re-run** under `PYTHONHASHSEED` 1/42/99: exit 0 all three; output
   **byte-identical** (md5 `1cd91be7…`) to the committed acceptance record.
2. **Tier-1 claim structure**: 19 published PD→RW pairs, each within 0.01pp; negative control
   present and firing (the 1.06-scaled form deviates up to 14.3pp and is rejected — the check
   can demonstrably fail).
3. **The tolerance revision (0.005 → 0.01pp), adjudicated with new evidence.** I wrote an
   independent implementation from the CRE31 formula text using a DIFFERENT inverse-normal
   algorithm (Acklam rational approximation + one Halley refinement; RE's path is
   `statistics.NormalDist.inv_cdf`). Result, committed alongside this review
   (`S1_independent_check.py`, `S1_independent_check_output.txt`):
   **maximum gap between the two implementations across all 19 points = 9.4e-13 pp.**
   Both implementations deviate from the published table identically (max 0.0066pp,
   8 positive / 11 negative, corr(log PD, deviation) = −0.508 — RE's diagnostics reproduce
   exactly). With the computation double-implemented to machine precision, the residual —
   including the −0.51 correlation RE honestly reported as evidence against their own
   conclusion — is a property of the 2006 table's production (period numerics + 2dp
   rounding), not of our code. **The one-published-ULP tolerance is principled; the
   tuning-to-pass reading is refuted by evidence, not by assurance.**

## Taken on report (assigned to the reviewer's independent pass)

- Transcription fidelity of the 19 pairs and the table identity (Annex 5, printed
  pp. 277-278, Corporate column, LGD 45% / M 2.5y / turnover €50m, UL table, non-SME
  column) against the actual PDF at `bis.org/publ/bcbs128d.pdf`.
- The rejection of the Explanatory Note (July 2005) as tier-1 material (TOC, no
  illustrative-weights annex).
- The version reading (Annex 5 states pre-1.06-scaling values; current framework CRE31
  carries no 1.06).

## Required follow-throughs (recorded here so they cannot silently lapse; not failures)

1. **Single source of truth.** No other IRB implementation exists in the repo (grep
   verified). The functions validated here are therefore THE canonical implementation:
   S3/S4/S8 MUST import from this module (or from a module extracted from it) — any
   downstream re-implementation of the formula voids this validation and is a review
   finding on that step.
2. **SA half.** RE flagged (correctly, rather than accepting my assignment's scoping) that
   the SA table was NOT validated — the CRE20 page did not render to the fetcher. RULING:
   an explicit SA-table check joins **S3's acceptance** — the generator's SA risk-weight
   table must match published CRE20/21 values, verified against a fetched PDF (not the
   framework webpage), cited per value class. S1's flag stands in its docstring; the
   unvalidated-implementation flag in v2 §9 is cleared for the IRB half ONLY.

Verdict: **PASS.** → reviewer-reproducer for independent review.

---

## Addendum (2026-08-07, after the reviewer's verdict — applied per their finding (4))

The reviewer accepted the tolerance revision on narrower grounds and is right that my
attribution of the −0.508 correlation to "the 2006 table's production" over-reads n=19:
the correlation is CONSISTENT with rounding-plus-drift and equally consistent with a small
systematic in the period generator's own inverse-normal, and it does not need to carry
weight — the printed-precision argument (0.005pp demands more precision than 2dp printing
carries; one printed unit is the correct a-priori bound) and the ~2000× negative-control
separation settle the question without it. **The correlation is hereby demoted to an
observation, not support.** My two-path agreement stands as evidence that the residual is
not in our code; where it lives on the published side stays unattributed.
