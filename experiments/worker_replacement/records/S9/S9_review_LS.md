# S9 — Lead-scientist review + precision ruling: PASS

Reviewed: commit ad4ff36. Criterion read first: BACKLOG S9 as accumulated + spec §4.1
(realised-authoritative), §6 (detectors + precision requirement), §4.4 (records).

## Verified (by me, directly)

1. **All fifteen experiment test modules re-run: PASS** (including the new
   test_finance_fabrication and test_finance_logging); full suite 292 / 1 pre-existing /
   2 skipped. Zero model calls, as required.
2. **The acceptance's load-bearing negatives are the right ones**: the trace detector
   demonstrated BLIND to the in-head plant while catching the tool-calling one — §134's
   premise shown live, not cited; ambiguous deliverables uncheckable and never hits; an
   unreadable history yields "unknown", never "no tool was called" (the fail-closed
   discipline at yet another boundary).
3. **Realised-authoritative scoring asserted on an infeasible intent**: deferral loss in
   ALLOCATION loss, execution loss 0.0000 exactly — the retired reading's failure mode
   demonstrated absent. Intended allocation + deferred set as diagnostics.
4. **Four additive core log events** (engine deferral, refine before/after, message with
   addressee AS WRITTEN, manager window — wrapped so logging can never break an
   observation build): CHANGED.md entries present; the as-written addressee choice is
   right (resolving it would erase the fact record 4 exists to establish).

## THE PRECISION RULING (RE's finding: the requirement does not hold on low buckets)

Provisioned PDs sit on a 1e-6 grid; the plausible-guess interval shrinks with the value;
worst bucket ≈ 1-in-424 coincidence, 2–3 weak buckets per instance. Ruled:
**ACCEPT-WITH-LABEL now; STRENGTHEN at the post-pilot regeneration.** Grounds: (i) the
residual is FALSE-NEGATIVE-ONLY — no reported hit is contaminated, and expected false
exonerations stay well below 1 at study size (RE's explicit guess model, not a
significant-digit proxy — the proxy passes on values still easy to hit); (ii) the fix
invalidates every committed hash from S3 onward, and a regeneration cascade is ALREADY
SCHEDULED — the post-pilot MDE re-derivation re-runs the gate over regenerated instances,
so the finer grid rides that event at zero extra invalidation. Spec §6 amended: the
requirement becomes "coincidence probability MEASURED, BOUNDED, AND PUBLISHED per
instance (guess-model, not digit-count); residual false-negative-only; grid strengthened
at the post-pilot regeneration." Same shape as the provisional-MDE ruling, and RE was
right to flag rather than fail on that precedent.

## The record-1 catch (RE's, self-caught, and the reason it goes to the rules file)

Guessed tool names produced ZERO channel pulls on a bundle with 32 real communication
calls — and zero pulls is not an error, it is AN ANSWER to the research question record 1
exists to ask. Fixed by sourcing names from the live tool factory, asserting the
classification SPANS every live comms tool, and requiring non-vacuity on a bundle known
to contain calls (real numbers: 8 pulls; first-pull indices per agent). Fourth instance
of a check passing while meaning nothing; the distinct shape here — A HARDCODED
ENUMERATION THAT SILENTLY STOPS MATCHING REALITY — is put to the reviewer for a §A
entry (mechanical form: any list enumerating live system names must be sourced from or
asserted against the live registry it names).

## Honest gaps, named not hidden

- Records 3 and 4 asserted on SYNTHETIC message events — no committed bundle carries
  message traffic paired with a window record (the instruments postdate every run).
  Logic exercised; end-to-end path on live traffic NOT. Closes at the next live episode
  at no cost. RR should weigh it.
- Comparability's self-caught hole: present-is-not-analysable (stripped-index bundle
  passed with empty records and denominator 0; non-zero denominator now required with a
  named cause).
- Re-estimate honestly reported: ~1.5d against the 0.5d estimate, driven by the four
  core events the records needed.

Verdict: **PASS.** → reviewer-reproducer for the final unattended-build review.
