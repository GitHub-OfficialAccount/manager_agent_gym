# S3 — Lead-scientist review: PASS

Reviewed: commit 2d12f01 (`finance_generator.py`, `test_finance_generator.py`,
`records/S3/` acceptance output + committed instance). Criterion read first: BACKLOG S3 as
amended (SA-table check + import rule) + HARNESS_SPEC_v2 §2, §5 (identifier opacity
instance-wide, leak-exclusion), E6, §4.3 (dilution knob).

## Verified (by me, directly)

1. **Acceptance re-run: PASS** — including the byte-identity across processes at
   PYTHONHASHSEED 1/99, the 18 SA values, all four wrong-table negative controls, and the
   IRB identity-import assertion. Full suite re-run: 292 / 1 pre-existing / 2 skipped.
2. **Committed instance inspected independently:** 4 workers with opaque hash-style ids
   (`w_26f14e` — no lattice token; built by `make_worker_id()`, a callable production path
   per the S2 carry-forward); equal-size (2) coverage subsets over 4 asset classes,
   **pairwise non-nested — verified arithmetically on the instance by me**, not taken from
   the test; `private_pd_calibration` per worker; 6 of 9 segments `irb_approved`,
   matching the declared `irb_applicable_fraction = 0.67`.
3. **The dilution knob is a real generator parameter** (`irb_applicable_fraction`,
   §4.3 pointer in the docstring) — present though unmentioned in RE's completion DM.
4. **Instance self-documents its provenance**: SA citations per class with the trap
   warnings inline ("Table 6 ECRA BASE row — not the short-term row, not Table 7"), IRB
   module provenance naming S1's validation. A reader of the JSON alone can audit the
   sources.
5. **The 4-class-minimum argument checked:** four workers need a 4-antichain; subsets of
   a 3-set have a largest antichain of 3 (Sperner), so three classes cannot seat four
   non-nested workers; C(4,2)=6 seats them with room. Sound.

## Adjudicated (the design point RE flagged for review)

**Private parameter = the bank's own rating→PD calibration per covered asset class:
ADOPTED.** This is the honest analogue of IRB approval — the Basel correlation parameters
are public text, so "holding the formula" would be no real gap (the calculator no-go's
lesson), while a bank's validated PD estimates are exactly what approval grants. It also
makes S10's fabrication probe concrete: a fabricating worker must invent PD values, which
the value-based detector classifies as "neither" truth.

## Taken on report (assigned to the reviewer)

- The 18 transcribed SA values and the four trap tables against the actual d424.pdf at
  source (transcription fidelity + column identity — the reviewer's S1 discipline).
- The three self-caught test-shape defects RE reported (same-hashseed determinism check,
  vacuous universality loop, `... or True` assertion) — fixed shapes worth confirming in
  the committed test, and a datum for the §A rule's origin note if the reviewer wants it.
- Anything neither RE nor I looked for.

Verdict: **PASS.** → reviewer-reproducer for independent review.
