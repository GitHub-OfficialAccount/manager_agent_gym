# S6 — Lead-scientist review (full step, incl. the 0/40 ruling round): PASS

Reviewed: commits 364bb43 (delivery: gate + sweep + disclosures; 0/40 admitted with the
structural proof) and 7a33203 (ruling implementation: roster-correct scoring + 5-class
constructed lattice). Criterion read first: BACKLOG S6 as amended + HARNESS_SPEC_v2 §4.3
in full, §4.1 (roster-correct + clip flags), §5 (k-floor, swap-class, constructed
template).

## Verified (by me, directly)

1. **All four acceptance suites re-run: PASS** (generator, scorer, assertions, gate);
   full suite 292 / 1 pre-existing / 2 skipped.
2. **Roster-correctness live on the committed instance:** post-swap oracle 8.5514
   (interior) where the pool oracle was 9.0000 (perfect) — the inflation was exactly the
   ruling's claim. Five classes including mdb; sole class (bank) uncovered post-swap;
   swap_shared_class = corporate (seed-permuted, not lexicographic).
3. **Sweep report:** 40/40 admitted (was 0/40), 35 distinct lattices (was 13),
   swap_class_uniform = False. RE's headline numbers (100/100 total generation, 0
   oracle-perfect, spread min 0.600 / median 1.648 / max 2.900) taken on report — the
   40-seed sweep artifact and the acceptance output are consistent with them.
4. **Gate report carries every required disclosure:** K1 curve (7 points, including the
   visible self-rejecting point at fraction 0.10 — correctly NOT filtered), K2 (k,
   strict list, successor-only fraction), K3 signed ratios each labelled
   anchored/unanchored, K4 realised lattice, clip-flagged segments (empty here), spread
   as fraction of max (19.8%), rejection reasons (empty on admit; the oracle-perfect
   fixture proves the ceiling still bites now that the generator cannot produce one).

## Adjudications

- **The two constraints the A4 canary exposed: both ACCEPTED, spec updated.**
  (a) The SA-clip worthlessness exclusion is A6's sibling — zero SCORE vs zero WEIGHT,
  different mechanism, same deficiency shape — and filtering on EVERY sole-class approval
  (not just the promoted segment) is right; seed 21's naturally-approved clip proves the
  narrower guard fails. (b) Bounded seeded re-draw preserves totality per the ruling.
  The canary itself firing twice within an hour of its reframing is the strongest
  possible vindication of the reviewer's keep-as-canary ruling.
- **The searched fixture seed** (case 6's zero-fallback fixture no longer exists at seed
  101 under five classes): converting a hard-coded seed into a searched one is correct —
  a hard-coded seed that stops containing its fixture silently skips the negative case,
  the worst failure mode an assertion suite can have.
- **The gate's structural check now asserts the FIX (0/60 oracle-perfect) with both gate
  paths still proven on labelled fixtures** — the added oracle-perfect fixture keeps the
  ceiling demonstrably biting. Correct handling of a test that documented the old defect.

## Watch item (flagged for the reviewer and the pilot — not a defect)

**successor_strict_count = 1 at k = 1 on the committed instance: zero headroom.** The
k-floor risk (§5, RR F-A) is at its edge — a single segment (seg_02) carries the entire
successor-specific allocation consequence. The sole class provides INTERIORITY (everyone
degrades equally there — zero allocation spread by construction) while strict-requirement
spread rides on one segment. The K2 headroom curve and the pilot will show whether
k_strict = 1 gives enough signal; if not, the template has room (a second shared-class
segment) without redesign.

## Taken on report (assigned to the reviewer)

- The structural proof's statement and RE's 60/60 + 100/100 sweep numbers.
- The role-based designation (template creates THREE two-holder classes; lexicographic
  search would pick the wrong pair — RE's implementation note, worth independent eyes).
- The K3 anchored-minority finding (3 of 9 anchored on seed 101 pre-ruling) against the
  regenerated instance.
- Anything neither of us looked for — this step changed more surface than any since S2.

Verdict: **PASS.** → reviewer-reproducer for the full step including the ruling round.
