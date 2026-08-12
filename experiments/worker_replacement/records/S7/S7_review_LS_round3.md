# S7 — Lead-scientist review, round 3 (F1 implementation; commits ca9ad37 + 588bbf5): PASS

Criterion read first: spec §5 as amended (v3 quantity + history, flag-not-reject + C1/C2,
MDE provisional) and §4.3 (K3 narrowed to PD).

## Verified (by me, directly)

1. All five acceptance suites PASS; full suite 292 / 1 pre-existing / 2 skipped.
2. **v3 ceiling stats reproduce exactly from the committed artifact**: n=40, min 0.0753 /
   median 0.1477 / max 0.1875 — RE's headline numbers are recomputable, per the standard
   their own S7 round set.
3. **Flags verified at field level**: `below_provisional_mde: True` per row;
   `declared_mde_status: "provisional — no in-environment variance estimate yet"`;
   **C1 is folded into the flag STRING itself** ("GATE ON THE FLAG (C1): no flagged
   instance contributes to a reported finding…") — the gate cannot be quoted away from
   the flag it qualifies. 40/40 flagged, 0 rejected, exactly per the ruling.
4. **The v2 retirement is visible, not silent**: `diagnostic_m_successor`,
   `diagnostic_m_incumbent`, `diagnostic_coverage_attributable` ship per row; suite-wide
   the coverage-attributable share of M has median 0.185 — v2 overstated the channel
   effect ~5×, corroborating RR's F1 on all 40 seeds.
5. `ignorant_draws` disclosed per row (300); K2 rewired to the ceiling with the strict
   count demoted (and the new reading recorded: the ceiling is FLAT across k=1..4 — k
   gates admission and does not move the effect; k is NOT a rescue lever).

## Adjudications

- **RE's declined LGD widening: ACCEPTED.** An asserted floor nobody can point at reads
  as verified when it is not — the same distinction PD_FLOOR_VERIFIED already draws. The
  narrow PD claim stands; widening requires a re-fetch and proper verification, on offer
  if wanted.
- **RE's σ prediction, committed early so it cannot drift, recorded verbatim in the
  predictions file**: within-cell σ 0.10–0.20 of oracle — comparable to or larger than
  the median ceiling — under which "the design is not detectable at any n we would pay
  for and needs a different effect channel, not more seeds." All three predictions now
  diverge informatively: RE (band unstudiable), RR (σ ≥ 0.13, MDE ≥ 0.17), LS
  (σ 0.08–0.12, band marginal-but-studiable). The pilot discriminates all three.

## One follow-up question, assigned with this review (cheap, offline)

K2's k is flat — but **is K5 (`shared_class_segments`) a lever on the v3 ceiling?** Under
v2 the K5 curve moved max-effect 0.096→0.300 across counts 2–6; under v3 nobody has
looked. Produce the K5-vs-v3-ceiling curve (same machinery as the existing sweeps).
Whether a rescue lever EXISTS should be known BEFORE the pilot answers the σ question —
if the band is too small and no knob moves it within realism anchors, the redesign
conversation starts from that fact, not from a search.

Verdict: **PASS.** → reviewer-reproducer for the scoped F1-implementation round
(finance_scorer.py: channel_effect_ceiling / expected_ignorant_score).
