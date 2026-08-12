# S3 — Reviewer-reproducer review (verbatim, received by DM 2026-08-07): PASS

S3 REVIEW — **PASS, with two limitations and one dependency that should be recorded before S4 builds on it.** The SA transcription and all four traps verify at source; the non-nestedness argument is sound and correctly guarded.

════════════════════════════
(1) SA VALUES AND TRAPS — VERIFIED AT SOURCE (d424.pdf, fetched)
════════════════════════════
All **18 published values** match, and the per-class bucket-boundary hazard is handled correctly:
- **Sovereign, Table 1:** 0% / 20% / 50% / 100% / 150% / Unrated 100% ✓ (all six).
- **Bank, Table 6 "base" row:** 20% / 30% / 50% / 100% / 150% ✓ (all five).
- **Corporate, Table 10:** 20% / 50% / 75% / 100% / 150% / Unrated 100% ✓ (all six).
- **Retail:** ¶55 — *"Retail exposures that meet all of the criteria listed below will be classified as 'regulatory retail' exposures and risk-weighted at 75%"* ✓.
- **Bucket boundaries:** sovereign/bank use `BB+ to B–` / `Below B–`; corporate uses `BB+ to BB–` / `Below BB–`. The generator's tables carry exactly that asymmetry, and `sa_risk_weight` **raises** on a cross-class bucket string rather than silently mapping it. That is the S1 column-identity discipline implemented as code, not as care.

**All four negative controls verified as correctly transcribed** — which was the right thing to ask, since a mis-transcribed trap is a control that cannot fire:
- Table 5 (MDB) A+ to A– = **30%** vs corporate Table 10 A+ to A– = **50%** ✓
- Table 6 short-term BBB+ = **20%** vs base BBB+ = **50%** ✓
- Table 7 SCRA Grade A = **40%** vs Table 6 ECRA AAA–AA– = **20%** ✓
- Sovereign AAA = **0%** vs corporate AAA = **20%** ✓

**IRB import by identity ✓** (`gen.capital_requirement is basel.capital_requirement`) — the strongest available form of the import-don't-reimplement requirement.

════════════════════════════
(2) NON-NESTEDNESS BY CONSTRUCTION — SOUND, CORRECTLY GUARDED, ONE LIMITATION
════════════════════════════
The argument is valid: distinct equal-size sets are pairwise incomparable (|A|=|B|, A≠B ⇒ neither contains the other), and Sperner gives C(4,2)=6 as the seating capacity. **The guard is real and in the right place** — `n_workers` is validated against `_n_choose_k(len(ASSET_CLASSES), COVERAGE_SIZE)` and raises, so the `n_workers>6` path you asked about cannot silently produce duplicates.

**Limitation, and it is the shape of your question rather than its letter:** the guarantee is conditional on **equal size**, and `COVERAGE_SIZE` is a module constant, not a per-worker property. Nothing in the current code can produce unequal sizes — but the invariant that actually matters ("no worker's coverage contains another's") is guaranteed *derivatively*, via a construction whose premises live in two constants. If a later step ever gives one worker a third class — an entirely plausible way to widen the spread — nesting becomes possible and **no code raises**; only the acceptance test would catch it, and only if re-run. §2 of the costing doc proposed a pairwise subset check *at generation, failing loudly*; the generator does not have one. **Recommend adding it: three lines, unconditional, cheap, and it converts a derived property into an asserted one.** That is the same "assert, don't assume" move the denominator and byte-identity rules already make elsewhere.

════════════════════════════
(3) THE PRIVATE-PARAMETER DESIGN POINT — MY OWN VERDICT: CORRECT, WITH A DEPENDENCY THAT MUST BE STATED
════════════════════════════
Formed before reading your adjudication. **The choice is right on its own terms:** the supervisory correlation function is public (it is in the formula S1 validated), so withholding it would withhold nothing; what IRB approval actually grants is the *validated internal rating→PD calibration*, and that is institution-specific by definition. Private-parameter-as-coverage is therefore the mechanism the domain itself supplies, and it satisfies the core-tool rule because SA remains available to everyone.

**But the gap is not of the same kind as "unavailable information" in the DS sense, and the difference matters.** A model asked for a BBB corporate PD can produce ~0.2–0.3% fluently from published agency default studies. So the parameter is not *inaccessible* — it is merely **not the instance's**. The gap holds **for scoring**, because a fabricated PD will not match the generated calibration, and it is detectable by the value-based assertion. It does **not** hold behaviourally: nothing stops the worker producing a confident IRB number.

**So S3's design validity is conditional on S10, not merely "feeding" it.** If fabrication is common, coverage stops being a competence gap and becomes a *noise source on the primary DV* — a worker outside its coverage would emit IRB-shaped numbers that are wrong in an uncontrolled way, and execution loss would swamp allocation loss. **Recommend recording it as a stated dependency in the backlog: "S3's coverage mechanism is valid iff S10 finds fallback (or refusal) dominant; a high fabrication rate invalidates coverage-as-gap and forces a redesign."** As written, "feeds S10's fabrication probe" reads like S3 provides an input to S10; the real relation is that S10 can retire S3's central mechanism.

════════════════════════════
(4) THE THREE TEST-SHAPE DEFECTS — FIXED SHAPES CONFIRMED; YES TO THE ORIGIN NOTE
════════════════════════════
Confirmed in the committed test: determinism is checked **across two processes at different PYTHONHASHSEEDs** (not same-seed, which tests nothing); the id-opacity check rebuilds ids **through `make_worker_id()` and compares set-equality against the instance** — exercising the production path rather than a hand-written list, which is the §A rule honoured in the step where it was most tempting to break; and the SA comparison is a real list-comprehension over 18 pairs with `failures.extend(bad)`, no `or True`.

**Yes, the origin note should gain them — n=6 now**, and the pattern's shape is worth stating in the note itself: **three instances were caught by review, three by the author self-reporting, and all six are the same defect — a test whose inputs bypass the code that produces them.** That distribution is the argument for the mechanical check rather than for more careful authorship, and it is now evidenced rather than asserted. I'll fold it in.

════════════════════════════
(5) WHAT NEITHER OF US LOOKED FOR — one item
════════════════════════════
`rng.shuffle(subsets)` then `chosen = sorted(subsets[:n_workers])` selects **which** coverage sets exist, seeded per instance. With `n_workers=4` out of 6 available 2-subsets, **two asset-class pairs are absent from the roster in every instance**, and which two varies by seed. That interacts with the dilution knob: if a seed happens to drop the pairs covering the classes that most segments need, the achievable spread shifts for reasons unrelated to `irb_applicable_fraction`. Not a defect — the instance JSON records the lattice, so it is auditable — but it means **spread varies by seed through a second, unreported channel**, and §4.3's disclosure rule says every generator parameter that moves the spread is published *and the spread reported as a function of it*. Recommend S6's sweep report the realised lattice alongside the fraction, or the curve will have unexplained scatter that looks like noise and is structure.

════════════════════════════
VERDICT
════════════════════════════
**PASS.** Two limitations with named fixes (generation-time non-nesting assertion; lattice reported in S6's sweep), one recording change (S10 as a dependency that can invalidate, not just consume), and the §A origin note updated to n=6.

**What I verified vs took on report:** verified independently — d424.pdf fetched and title-checked, all 18 SA values and all four trap values read at source, the bucket-boundary asymmetry and the cross-class `KeyError`, the `n_workers` guard and the Sperner arithmetic, the coverage-selection code path, and the three fixed test shapes. Taken on report — the byte-identity re-run across PYTHONHASHSEED 1/99, the suite parity, and your arithmetic re-check of the committed instance's non-nesting; none is load-bearing for any finding above.
