# S1 — Reviewer-reproducer review (verbatim, received by DM 2026-08-07)

S1 REVIEW — **PASS, with one finding that is a citation defect rather than a validity defect, and one point where I reach your conclusion by a different and stronger route.**

Read in spec order per my own rule: BACKLOG S1 as amended → HARNESS_SPEC_v2 E2/§4.1/§9 → the check → the output → the primary source. I did not read your review file until after forming my verdict on the tolerance.

════════════════════════════
(1) THE 19 PAIRS AND THE TABLE IDENTITY — VERIFIED AT SOURCE
════════════════════════════
Fetched `https://www.bis.org/publ/bcbs128d.pdf` and extracted. **All 19 transcribed PD→RW pairs match the published table exactly** — 0.03→14.44, 0.05→19.65, 0.10→29.65, 0.25→49.47, 0.40→62.72, 0.50→69.61, 0.75→82.78, 1.00→92.32, 1.30→100.95, 1.50→105.59, 2.00→114.86, 2.50→122.16, 3.00→128.44, 4.00→139.58, 5.00→149.86, 6.00→159.61, 10.00→193.09, 15.00→221.54, 20.00→238.23. No transcription error.

**Table identity confirmed, including the column trap you flagged.** Annex 5, *"Illustrative IRB Risk Weights for UL"*, printed page 278, header `Asset Class: Corporate Exposures | LGD: 45% | Maturity: 2.5 years | Turnover (millions of €): 50`. The adjacent SME column (turnover 5) runs 11.30/15.39/23.30… — visibly lower, consistent with the firm-size adjustment, and **not** what was used. The annex's own text confirms the adjustment applies to *"the second set of risk weights provided in column two given that the turnover of the firm receiving the exposure is assumed to be €5 million."* RE used the right column.

════════════════════════════
(3) THE VERSION READING — **THIS IS THE FINDING: the claim cannot be verified from the cited document**
════════════════════════════
`bcbs128d.pdf` is **the annexes only**. It opens at *"Annex 1 — The 15% of Tier 1 Limit on Innovative Instruments"*, and the string "1.06" **does not appear anywhere in it**. So the assertion that Annex 5 values are pre-1.06-scaling is **not supported by the source the record cites** — the scaling-factor paragraph lives in the main framework, which is a different PDF.

I fetched the full framework (`bcbs128.pdf`) and located it: **¶44** — *"The Committee applies a scaling factor in order to broadly maintain the aggregate level of minimum capital requirements… The scaling factor is applied to the risk-weighted asset amounts for credit risk assessed under the IRB approach"*, with footnote 11: *"The current best estimate of the scaling factor is 1.06."*

And note what that sentence actually says: the factor applies to **risk-weighted asset amounts**, not to the risk-weight function. Annex 5's own text says its weights *"produced using the appropriate risk-weight function… set out in Part 2, Section III"* — a statement about the function, silent on the aggregate scaling. **So the textual reading is at best inferential, in either direction.**

**What settles it is empirical, not textual, and it is already in the record:** our unscaled implementation reproduces all 19 published values to ≤0.0066pp while the 1.06-scaled form misses by up to 14.3pp. That is a demonstration, and it is stronger than any reading of the prose. **Finding: cite `bcbs128.pdf` ¶44 + fn.11 for the scaling factor, cite `bcbs128d.pdf` Annex 5 for the table, and rest the pre-scaling conclusion on the negative control rather than on a textual claim the annex does not make.** As written, the record attributes to one document a statement that is in another — the same class as §6d, caught before it propagated.

════════════════════════════
(2) THE EXPLANATORY-NOTE REJECTION — CORRECT, VERIFIED
════════════════════════════
Fetched `bis.org/bcbs/irbriskweight.pdf`; title-verified *"An Explanatory Note on the Basel II IRB Risk Weight Functions"*, BCBS, **July 2005**. Full TOC is exactly the six sections RE reported: Introduction / Economic foundations / Regulatory requirements / Model specification (4.1–4.7) / Calibration (5.1–5.3) / References. **No illustrative-weights annex, and no occurrence of any published risk-weight value** — I searched for the table's own numbers and found none. **Rejection as tier-1 material is correct.** Worth recording that it remains the right citation for the *formula's derivation*, which is a different use.

════════════════════════════
(4) THE TOLERANCE REVISION — MY OWN VERDICT, FORMED BEFORE READING YOURS
════════════════════════════
**Principled, and I would have accepted it on narrower grounds than you did.**

The suspicious pattern is real and must be named: a tolerance loosened *after* seeing three failures is the shape of a moved goalpost, and it is right that RE self-flagged it. Three things make it survive here:
1. **The published values carry two decimal places, so one unit in the last place is 0.01pp.** A tolerance of 0.005pp asserts agreement to *half* a printed unit — i.e. it demands the published figure be more precise than it is printed. That is not a stricter test, it is an ill-posed one. **0.01pp is the correct tolerance a priori, and choosing it after the fact does not make it post hoc — it makes it late.**
2. **The negative control does the discriminating work.** A tolerance that admits the true form at 0.0066 and rejects the 1.06-scaled form at 14.3 has a separation ratio of ~2000×. There is no tolerance in that gap that changes the verdict, so the revision cannot have manufactured the pass.
3. **The residual is inside a single rounding unit at every point** (max relative 2.5e-4 at the smallest weight, where one printed unit *is* 3.5e-4 relative).

**Where I part company with your reasoning, though not your conclusion:** you rest partly on the −0.508 log-PD/deviation correlation being *"a property of the 2006 table's production"*. I would not lean on that. n=19, and a correlation of that size is not strong evidence about a 20-year-old production process we cannot inspect; it is *consistent* with rounding-plus-drift and equally consistent with a small systematic difference in the published generator's own inverse-normal. **It does not need to carry weight** — points 1 and 2 settle the question without it. Recommend the record state the correlation as an observation, not as support.

**Your double-implementation is the strongest single item in the S1 record** and I have nothing to add to it: two independent inverse-normal paths agreeing to 9.4e-13pp while both deviating from the table identically localises the residual to the published figures, not to us.

════════════════════════════
VERDICT
════════════════════════════
**PASS.** Tier 1 is genuinely reached: ≥3 published numeric worked examples, 19/19 within a correctly-derived tolerance, with a discriminating negative control.

**One finding to apply before S1 is marked `[x]`** (documentation, not re-work): correct the source attribution for the scaling-factor claim per (3), and demote the correlation to an observation per (4).

**Carried forward, not blocking:** the SA lookup table is explicitly NOT validated here — flagged in the output, correctly scoped out, and now ruled into S3's acceptance. That ruling is right and I would add one line to S3: the SA check needs its own published-table citation with the same column-identity discipline that (1) just exercised, because CRE20/21 tables have exposure-class and rating-grade columns that are exactly as easy to mis-select as the €50m/€5m pair.

**What I verified vs took on report:** verified independently — the 19 pairs, the table identity and column, the annexes-only scope of bcbs128d, ¶44+fn.11 in bcbs128, the Explanatory Note's title/date/TOC/absence of numeric weights, and the tolerance argument. Taken on report — your re-runs under three PYTHONHASHSEED values and the 9.4e-13pp agreement between your Acklam+Halley path and RE's `NormalDist.inv_cdf` (I did not re-implement a third path; a third same-source implementation would add little that your different-algorithm path did not already establish).
