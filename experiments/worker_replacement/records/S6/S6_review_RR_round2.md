# S6 — Reviewer-reproducer review, round 2 / FINAL (verbatim, received by DM 2026-08-08): PASS

S6 ROUND 2 — **PASS on the F2 mechanism and all five fixes. Three findings, one of which gives K3 the per-segment anchor we have been asserting doesn't exist, and my ruling on (3) is that the declared MDE must be 0.20, not 0.13.**

════════════════════════════
VERIFIED FROM `sweep_rows.json`
════════════════════════════
36 admitted / 4 rejected; admitted `max_effect_share` **min 0.1433, median 0.2394, max 0.3394**; the four rejections are exactly **0.0707, 0.1148, 0.1170, 0.1239** — every sub-MDE instance and no others, so the threshold is doing precisely the work claimed. `fabrication_blind_carriers` is **0 across all 40** (was 40/40) — the tiered ratio<1 selection works, and that is the fix that mattered most, because a strict carrier sitting in the clip region is a segment where the effect exists and the execution term cannot see fabrication on it. `strict_count` is **4 on every admitted instance** — the count-bias half is stable, not seed-lucky.

RE's restraint on `shared_class_segments=5` is right and I endorse it for their stated reason: 39/40 admission achieved by concentrating 5 of 9 segments in one class is the gate no longer speaking. **But 4-of-9 (44%) is itself a concentration that moves the spread, so §4.3's own rule applies to it** — it is a generator parameter that changes the oracle-vs-worst gap, and the rule says such parameters ship per instance *with the spread as a function of them*. Recommend promoting `shared_class_segments` to a named knob with its own short curve, exactly as K1 has. Answer to your (1): **yes, disclosure-worthy — not because 4 is too high, but because the rule is about disclosure, not about magnitude.**

════════════════════════════
(2) THE AGGREGATE REFRAME — YOU DID NOT OVER-CORRECT; MY ORIGINAL READING WAS WRONG
════════════════════════════
The Basel output floor is explicitly portfolio-level — IRB RWA may not fall below 72.5% of what SA would produce **for the same portfolio**. It is not an exposure-level bound and never was. **My S4 F3 treated it as a per-segment anchor; that was a misreading and the aggregate form is the correct one.** Recording that plainly since it was my finding.

**F1 — but there IS a published per-exposure bound we are now ignoring, and the generator violates it.** Basel's IRB **input floors** are per-exposure: the PD floor is **0.05%** for corporate and retail exposures. Across 40 seeds / 360 segments the generator emits **PD as low as 0.000136 (0.0136%), with 9 segments below the 0.05% floor.** Those instances are unrealistic by a published standard, and the realism is exactly what the K3 disclosure exists to establish.

Two consequences, both good for us:
- **A generation-time assertion** (`pd ≥ 0.0005`, with the class-specific floors where they differ) — cheap, and it removes 9-in-360 unrealistic segments;
- **K3 gains a genuine per-segment anchor.** We have been reporting "unanchored" for the divergent tail because the output floor is aggregate. The input floors are per-exposure, published, and bound the *inputs* that drive IRB — so the honest K3 statement becomes "aggregate ratio anchored by the output floor; per-segment inputs anchored by the IRB input floors; the per-segment *ratio* remains unanchored." That is a materially stronger realism claim than "one side only", and it costs one assertion.

**F2 — the aggregate floor enforcement is currently non-binding.** `aggregate_output_floor_ratio` ranges **1.1622–2.0420** across the sweep against a 0.725 threshold — it cannot fail, which is assertion 4's shape recurring. Not a defect (publishing it is right, and a future generator change could move it), but the record should say it is **published and non-binding at present**, or a reader will count it as a constraint that passed rather than one that never engaged.

════════════════════════════
(3) YOUR DIRECT QUESTION — DECLARE MDE AT 0.20
════════════════════════════
**Use the band's top.** Three reasons that compound rather than merely add:

1. **σ is imported, not measured.** The 0.13 end assumes σ=0.10, which came from `mean_r_check` in the DS environment — a different DV in a different substrate. P14 is explicit that setup-level support is a prior to re-establish, not a result, and taking the *optimistic* end of an unre-established prior is the least defensible use of it.
2. **This design makes bimodality more likely, not less.** I flagged σ→0.15 if regret is bimodal. With 4 strict carriers, the manager's behaviour on them is close to discrete — it routes them to the successor or it doesn't — which is the bimodal case. At σ=0.15 the MDE is 0.198, and **8 of the 36 admitted instances sit below 0.20** (0.1433–0.199).
3. **`max_effect_share` is a ceiling, not an expectation.** It assumes the manager goes from zero to perfect on the strict carriers between cell 0 and an informed cell. Comparing an optimistic MDE against an optimistic effect multiplies two optimisms.

**Recommendation: declare 0.20 provisionally and say so.** That leaves 28 of 40 — still a viable suite — and the honest framing is that the threshold is **provisional pending a measured σ**. The gate is offline and re-runnable at zero cost, so the right sequence is: admit at 0.20 now, measure σ from the first cells, re-derive the MDE, and re-run the gate. Recording it as provisional is what stops a later re-derivation looking like moving the goalposts — the S1 tolerance lesson, applied before the fact instead of after.

════════════════════════════
(4) REJECTION REASONS — AGREED
════════════════════════════
`rejection_reasons: None` on rejected rows should name the cause. The four rejections are all one cause today ("max_effect_share below declared MDE"), which is exactly when a null field is cheapest to leave and most misleading later — a second rejection cause would be indistinguishable in the record. One string.

════════════════════════════
VERDICT
════════════════════════════
**PASS.** The F2 mechanism is sound end-to-end and the fabrication-blind-carrier elimination (40/40 → 0/40) is the strongest single result in this round. Findings: **F1** — PD input-floor assertion, which also upgrades K3's anchoring claim; **F2** — label the aggregate floor as non-binding; **(1)** promote `shared_class_segments` to a disclosed knob; **(3)** declare MDE 0.20, provisional, with the re-derivation sequence stated; **(4)** name the rejection reason. None blocks S6 going `[x]` — F1 and (3) should land before S7 admits a suite, since both change which instances are admitted.

**What I verified vs took on report:** verified independently — the full `sweep_rows.json` distribution (admission split, effect-share quantiles, the four rejected values, zero fabrication-blind carriers, uniform strict_count 4, aggregate-floor range), the Basel output floor's portfolio-level scope, and the PD input-floor violation across 360 generated segments. Taken on report — the pre-fix 12/40 and median 0.109 figures, the freshness assertion catching its own motivating case, and the K3 four-way partition assertion.
