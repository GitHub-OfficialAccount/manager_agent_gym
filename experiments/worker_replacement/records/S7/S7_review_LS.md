# S7 — Lead-scientist review (pre-work + pipeline + both capacity rulings): PASS, one pre-specified fix

Reviewed: commits 6a21911 (pre-work + pipeline v1, condition-3 20/20 rejection —
correctly escalated), 2cb7d2f (capacity ruling implementation, C=4), deb6f41 (C=3 final).
Criterion read first: BACKLOG S7 as amended + HARNESS_SPEC_v2 §7/§4.3 (capacity-binds
paragraph incl. the recorded LS cap error)/§5 (MDE provisional)/§4.4.

## Verified (by me, directly)

1. **All five acceptance suites re-run: PASS** (generator, scorer, assertions, gate,
   admission — my earlier module-name guess produced a spurious FAIL, corrected); full
   suite 292 / 1 pre-existing / 2 skipped.
2. **Pipeline end-to-end on the committed suite:** 40/40 generated, 35/40 fully admitted;
   condition-1 (regeneration) and condition-2 (gate) failures zero; **condition 3 rejects
   EXACTLY seeds {8, 11, 14, 16, 29}, asserted as SET EQUALITY** — rejecting the wrong
   instance at the right count would fail, which a count assertion would miss.
3. **Capacity consequences asserted, not narrated, and reproduced:** cap binds on the
   committed instance (load 6 > 3); without the successor 2×3 = 6 < 9 so three segments
   MUST go unstaffed (oracle 8.2791 → 5.2791, **M/oracle 0.3624**); capacitated oracle
   within the Σ-max bound (8.2791 ≤ 8.6434, runtime-asserted).
4. **The C=4 → C=3 correction is recorded at the constant itself**, not only in commit
   history — the next reader of `CAP = 3` sees why it is not 4 without archaeology. My
   single-instance-generalisation error stands in the spec alongside everyone else's.
5. **Two staleness catches by the instrument layer, both real:** S5's assertion-2
   negative had become DECORATIVE (still targeting the retired non-binding form —
   passing while asserting nothing; caught by the marker-vs-assertion distinctness
   check, re-derived as 2a-infeasible + 2b-non-binding with distinct markers); S6's
   freshness assertion flagged its own committed report stale after the cap change and
   regenerated it — firing on the first parameter change, exactly its purpose.

## Pre-specified fix (S1-style; RE in parallel with RR's review)

The five rejected rows in `records/S7/admission_suite.json` carry
`rejection_reasons: None` — a REGRESSION of the S6 round-2 item (4) ruling, which landed
in sweep_rows and was not carried into the new suite artifact. One string per row
("scripted baseline attains oracle"); the acceptance gains a no-null-reasons assertion so
the ruling cannot regress a third time.

## For the reviewer (full-step)

- Both capacity rulings adversarially — including MY error and whether the C=3 record
  states it fully; the DP (drop-order semantics: maximiser skips freely, minimiser may
  not); the M/oracle redefinition vs the retired strict-count share.
- The information-theoretic non-triviality claim (no script over public info attains the
  oracle) — is it STATED correctly in the pipeline report, and is it true (does any
  public field leak per-segment fallback penalties)?
- The PD input-floor citations (¶68/¶66 corporate-bank, ¶121 retail, QRRE 0.1% recorded;
  sovereign/MDB labelled UNVERIFIED with a conservative default) — verify at source.
- RE's proposed §A extension: "when an assertion is redefined, its negative must be
  re-derived, not merely re-run" — a ruling request, n=1 here but the mechanism is
  general.

Verdict: **PASS** (with the one pre-specified fix). → reviewer-reproducer for the full
step.
