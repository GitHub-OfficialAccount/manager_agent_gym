# S4 — Reviewer-reproducer review (verbatim, received by DM 2026-08-07): PASS with findings routed forward

S4 REVIEW — **the scorer is correct and I'd pass it; the committed INSTANCE exposes three things the acceptance test cannot see, one of which turns your signed-term finding from "possible" into "guaranteed on a segment that exists".**

════════════════════════════
(1) THE ALGEBRA — SOUND; ONE MISUSE SURFACE
════════════════════════════
`(oracle − faithful) + (faithful − achieved) = oracle − achieved`. `faithful` cancels exactly; all three terms are computed inside `decompose_regret` from one `(instance, allocation, reports)` triple, so the API cannot produce a non-summing report by any call sequence. The docstring's cancellation argument is right, and asserting it numerically anyway is the correct instinct.

**F4 (minor, P10 class): `reports` is never validated against `allocation`.** `achieved()` reads `reports.get(segment_id)`, so a **missing** key yields `None` → 0.0, indistinguishable in the decomposition from a report that legitimately scored 0. A stale or partial reports dict produces a well-formed, meaningless decomposition with no signal. One assertion (`set(reports) ⊆ set(allocation)`, and log missing segments explicitly rather than scoring them silently) closes it. This matters because "execution loss was large" will be read post hoc, and a missing worker output and a badly wrong one are different facts.

════════════════════════════
(2) CROSS-DOCUMENT CONSISTENCY — CONSISTENT
════════════════════════════
METRIC_AND_SENSITIVITY_SPEC indexes `s(u, m)` by **method**; `finance_scorer` indexes `s(segment, worker)` by **worker**. Compatible, because worker→method is total via coverage plus the universal fallback — and the scorer's `attainable_report` makes that mapping explicit in three named cases. The spec's per-unit-independence premise (what licenses `oracle = Σ_u max`) is stated in both places, and the scorer's `oracle` docstring adds the capacity precondition the spec's §4.3 requires. No drift found.

════════════════════════════
(3) §4.1'S SIGNED PARAGRAPH — CORRECT BUT INCOMPLETE, AND THE GAP IS THE K3 INTERACTION YOU ASKED ABOUT
════════════════════════════
`score_report = 1 − min(1, |reported − truth|/|truth|)` is **clipped at 0**. So on any segment where the faithful report's relative error is ≥ 1, the faithful score is already the floor, and **every deviation — fabrication included — is weakly rewarded. Not "can be rewarded": cannot be penalised.**

**And such a segment is in the committed instance.** `seg_04` — sovereign, AAA to AA–, applicable = IRB: `truth = 50,829,113`, `SA fallback = 0` (sovereign AAA carries a 0% risk weight). Relative error 1.0, faithful score exactly 0. A worker routed there without sovereign coverage scores zero by reporting faithfully, and **any** fabricated number in (0, 2×truth) scores better.

**The K3 interaction, stated:** the clipping region is exactly the high-divergence tail, and K3 is the knob that sets divergence. **Widening divergence to widen the spread mechanically enlarges the region where the execution term cannot penalise a fabricator.** §4.1 should say this — currently it says a fabricator *can* be rewarded, which understates a construction where on some segments it *must* be.

**Recommended addition:** the signed term is reported per segment alongside the faithful score, and segments at the clip (faithful score 0) are flagged, because the term is uninformative there by construction. Cheap, and it keeps the attribution honest rather than merely disclaimed.

════════════════════════════
F1 — THE UNIVERSAL-FALLBACK PREMISE FAILS ON ZERO-RISK-WEIGHT SEGMENTS
════════════════════════════
Bigger than the sign issue, and it is a premise of the whole coverage design. §2 and the costing doc justify coverage-as-information by: *"SA is the universal fallback — the lookup table needs no private input, so every worker can always produce a defensible number for every segment."* On `seg_04` the defensible number is **zero**, and it scores **zero**. The worker is *operational* and *worthless* — which is the deficiency shape, not the difference shape, and it is the same profile as the DS tool-removal arm we abandoned (uncovered → 0.0%).

One segment class, not the whole instance, so this is not fatal — but it must be **excluded by construction, not discovered per instance**: no IRB-applicable segment may have an SA fallback of zero (equivalently, sovereign AAA–AA– must not be IRB-applicable). That belongs in **S5's generation-time assertions**, and it is checkable in milliseconds.

════════════════════════════
F2 — THE COMMITTED INSTANCE SITS AT HALF THE TRIVIALITY CEILING
════════════════════════════
Acceptance reports `oracle 8.000000` over 8 segments — i.e. **the oracle attains a perfect score**. §4.3: *"Triviality ceiling. Spread at or near maximum (oracle scores perfectly, worst scores zero) → the instance is a detection toy… A design where the oracle cannot reach a perfect score is healthier than one where it can."* Worst is 5.37, not 0, so the instance is not at the full ceiling — but it is on the unhealthy side of the half the spec singles out. Not an S4 defect (the scorer reports what the instance is); an **S5/S6 gate item**, and worth knowing before instances are generated in bulk.

════════════════════════════
F3 — K3'S EXTERNAL ANCHOR IS ONE-SIDED, AND THIS INSTANCE DIVERGES THE OTHER WAY (my recommendation, shown insufficient)
════════════════════════════
I proposed the Basel output floor (IRB RWA ≥ 72.5% of SA) as K3's realism ceiling. On the committed instance, IRB truth **exceeds** SA on 4 of 5 IRB-applicable segments (`sa/truth` = 0.000, 0.467, 0.551, 0.697; only `seg_02` at 1.348 has SA above truth). The floor bounds IRB from **below**, so it is satisfied trivially wherever IRB is higher — **it constrains nothing in the direction this instance actually diverges.** My anchor recommendation is therefore weaker than I claimed: it caps one tail only.

Two consequences: the K3 disclosure needs a **two-sided** realism statement (something bounding how far IRB may fall *below* SA is what the floor gives; the other direction needs a different anchor or an explicit "unanchored" label), and the divergence distribution shipped per instance should report **signed** ratios, not magnitudes, or the asymmetry is invisible to a reader. Owning this: it is my own recommendation failing on contact with real numbers, which is the right way to find out.

════════════════════════════
(4) EXHAUSTIVE AT 8 — ADEQUATE, BUT SAY WHAT IT ESTABLISHES
════════════════════════════
The choice is fine and 4⁹ = 262k would also have been enumerable. The point worth stating is different: **the bound is termwise-provable** (`Σ max_w ≥ Σ s(assignee) ≥ Σ min_w` holds segment by segment), so enumeration verifies the *implementation*, not the mathematics, and the property holds at 9 and 10 by construction. Recording it that way stops "verified over 65,536 allocations" being read as coverage of the study's instance sizes. Also worth a line in the record: **S4's fixed instance (8 segments) is not S3's committed instance (9 segments)** — both are legitimate, but "the fixed instance" now names two different objects across two steps, which is the `v2.6` shape in miniature. Name the file, not the phrase.

════════════════════════════
VERDICT
════════════════════════════
**PASS on S4's deliverable** — scorer, oracle/worst, decomposition and provenance are all correct, and your independent reproduction of the signed term through the real API is the strongest item in the record.

**Findings routed forward rather than back:** F1 and F2 are **S5 gate items** (no IRB-applicable segment with a zero SA fallback; oracle must not attain a perfect score), F3 is a **§4.3 disclosure correction**, F4 is a small assertion in the scorer, and (3)'s clipping paragraph is a §4.1 addition. None of them is a defect in what S4 was asked to build.

**What I verified vs took on report:** verified independently — the decomposition algebra and the API's misuse surface, `score_report`'s clipping and zero-truth branches read in source, the cross-document `s(u,m)` correspondence, and the committed instance's per-segment truth/SA/divergence table recomputed through the production functions (which is where F1–F3 came from). Taken on report — the 65,536-allocation enumeration, the bounds-attained additions, and suite parity.
