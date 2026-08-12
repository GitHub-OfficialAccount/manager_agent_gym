# S5 — Lead-scientist review, round 1: FAIL (one finding, reproduced; fix pre-specified)

Reviewed: commit b232aa4. Criterion read first: BACKLOG S5 (six assertions as amended) +
HARNESS_SPEC_v2 §2/§4.3/§5/§4.1. Verified before the finding: acceptance re-run PASS (5
negatives, 5 distinct markers, 100-seed sweep — 44 chances, 0 violations); S3/S4
acceptance green under schema v2; suite parity 292/1/2; the inert-arrival fix's headline
number (successor routes 6) reproduced independently.

## FINDING (reproduced; probe output below): assertion 3 counts TIE-INCLUSIVE routing, not strict requirement

Splitting the 6 successor-routed segments by unique-vs-tied maximizer on the committed
instance (records/S3/instance_seed101.json, post-swap roster):

    STRICT unique-maximizer through successor: seg_05 (bank), seg_01 (bank)  -> k_strict = 2
    TIED (oracle attainable WITHOUT the successor): seg_08 (sovereign, 3-way),
        seg_07 (retail, 3-way), seg_04 (sovereign, 3-way), seg_00 (sovereign, 2-way)

The three 3-way ties are SA-applicable segments — everyone scores identically and
`oracle_allocation`'s tie-break hands them to the successor arbitrarily. So the assertion
as implemented measures a quantity 4/6 of which is tie-break artifact:

- **It can pass on ties alone.** A future lattice or tie-break change could satisfy
  "routes ≥k through the successor" while NO segment strictly requires the newcomer —
  the inert-arrival trap S5 exists to prevent, admitted through the side door.
- **K2's disclosure would overstate.** §4.3 publishes "k and the successor-only fraction";
  k=6 is not the successor-ONLY count. The honest figure on this instance is k_strict=2.

**Spec ambiguity acknowledged as contributing cause (fixed in the same commit as this
review):** §5 stated the condition as "≥k units whose ORACLE allocation routes through the
successor — successor coverage strictly required to attain the oracle score". The two
formulations joined by that dash are NOT equivalent (routing includes ties; strict
requirement does not), and RE implemented the first literally. The spec now states only
the strict form.

## Pre-specified fix

1. Assertion 3 counts segments where `s(seg, successor) > max over every OTHER post-swap
   worker` (strict unique maximizer) — no dependence on `oracle_allocation`'s tie-break.
2. The published k (K2 disclosure, instance metadata) is the STRICT count.
3. The zero-k negative case re-verified against the strict counter.
4. Acceptance prints both counts (strict and tie-inclusive) so the gap is visible per
   instance rather than rediscovered.

## Otherwise verified and carried to round 2

- The inert-arrival design gap RE's assertion caught (first/last designation → zero
  routing) and the construction-based fix (pair designated from a two-holder class) —
  correct and the right kind of fix; with the strict counter the construction guarantees
  k_strict ≥ (segments of the vacated class) = 2 here.
- Assertion 6's generator-side constraint, demonstrated non-vacuously (44/0 over 100
  seeds).
- Assertion 4's unconstructible negative: RE's call ACCEPTED — a test that disables one
  assertion to exercise another is fixture-shaped evidence; the honest statement of the
  dependency is stronger. Recorded.
- Injection hooks for negatives driving production paths (§A honoured); schema v2 event
  block (t_swap, pair, both rosters — constant n verified: 3 active pre and post).

Verdict: **FAIL — back to RE for the strict counter.** Everything else stands.

---

# Round 2 (fix commit 7f41d76): PASS

Verified by me, directly: strict counter implemented tie-break-independent
(`successor_routing_counts` compares s-values, not `oracle_allocation` output); instance
metadata records `successor_strictly_required_segments: ['seg_01','seg_05']` — the list,
strictly more informative than a bare k, and the K2 disclosure reads from it; both counts
printed every run (strict 2 / tie-inclusive 6 on the committed instance); the
**discriminating k=3 negative** (RE's addition beyond the specification — between strict 2
and tie-inclusive 6, passed by the old counter, rejected by the new) is the case that
makes the fix falsifiable, and it correctly forced the distinctness check to per-assertion
form (5 markers across 6 cases — cases 3 and 3b exercise one assertion from two
directions); acceptance PASS; suite parity 292/1/2.

RE's note on the shared-blame framing — that they had already written the vacuity analysis
for O3's earlier form and so the noticing was theirs to do regardless of the spec's dash —
is recorded as they stated it.

Verdict: **PASS.** → reviewer-reproducer for the full step.
