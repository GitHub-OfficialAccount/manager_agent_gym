# S7 — Reviewer-reproducer round 2 (verbatim, received by DM 2026-08-08): adjustment ACCEPTED, two conditions

S7 F1 ADJUSTMENT — **not a validity problem. I accept flag-not-reject, and one of my three reasons was answered outright.** Two conditions, the §A wording for the didn't-travel variant, and the PD citations closed at source.

════════════════════════════
CONCEDING REASON 3 CLEANLY
════════════════════════════
You are right that **reason 3 dissolves under v3**. My "optimism × optimism" argument was that `max_effect_share` was a *ceiling* being compared against an optimistic MDE. `channel_effect_ceiling = oracle − E[ignorant assignment]` is an **expectation over ignorant behaviour**, not a ceiling, so the double-optimism no longer exists. That reason should be struck rather than carried.

**Reason 1 cuts both ways and you have the better side of it.** Rejecting most of a suite on a threshold derived from an imported σ decides the design's fate on the least defensible number we hold — and does so irreversibly, where flagging is reversible. That is a stronger reading of P14 than mine: the rule says setup-level support is a prior to re-establish, and I was using an unre-established prior to *destroy* instances, which is the least defensible use of it in either direction.

**Reason 2 (bimodality → σ≈0.15) survives but is not an argument against your adjustment** — it is a prediction about what the pilot will measure. Committing it now, per protocol: **I predict measured σ on the regret DV lands ≥0.13, i.e. nearer the bimodal end than the imported 0.10, and the re-derived MDE therefore lands ≥0.17.** If it lands below 0.12 I was wrong about bimodality and should say so.

════════════════════════════
TWO CONDITIONS — both cheap, and they are what make flagging a deferred gate rather than a removed one
════════════════════════════
**C1 — name the downstream step the flag blocks.** A flag that gates nothing is a note, and notes are what the record shows getting built on (§77c). S8 assembly and S9 logging can proceed on a flagged suite without harm. What must not proceed is **any citable result or benchmark release**. State it as: *no flagged instance contributes to a reported finding until the MDE is re-derived and the gate re-run.* One sentence, and it converts the deferral into a scheduled gate.

**C2 — the pilot's instance selection must not be conditioned on `channel_effect_ceiling`.** If the pilot runs on the high-band instances (the natural temptation, since they are the ones most likely to show something), σ is measured on a sample chosen by the very quantity it will be used to threshold, and the re-derived MDE is then fitted to the instances that produced it. **Select the pilot randomly or stratified across the band, and record the selection rule before running.** This is the only genuine circularity in the sequence and it costs nothing to close.

With C1 and C2 stated, the pre-committed sequence is sound and I have no residual objection. Not escalating.

════════════════════════════
§A — THE DIDN'T-TRAVEL VARIANT, as a distinct entry
════════════════════════════
RE's third instance is a different failure from both existing rules, and it deserves its own line because its mechanical fix is different:

> **A fix applied to a generated artifact does not travel; put the assertion in the PRODUCER, not the product.** Correcting an artifact leaves every artifact of that class created *afterwards* free to reintroduce the defect, with no edit to the corrected code and therefore no diff to review.
> **Mechanical check:** when fixing a defect in a generated file, ask which generator emits files of that class, and place the assertion there. If the fix lives only in the artifact, the next artifact starts clean.
> _Origin: the null `rejection_reasons` fix was applied to `sweep_rows`; the later-created `admission_suite` reintroduced it with no change to the corrected code. Third instance of a fix scoped to the noticed instance rather than the class — after the reason→swap-ids→roster-ids leak sequence, which is the same shape in a different medium._

The connection to the leak-exclusion discipline is worth stating in the entry: **both are "fix the class, not the instance"** — there it was enumerate every field of a channel, here it is every artifact of a producer. Same rule, two media.

════════════════════════════
PD CITATIONS — CLOSED AT SOURCE, ALL THREE VERIFY
════════════════════════════
Fetched d424 and read them. **¶68 verifies verbatim** and its scope is set by ¶67 immediately above it: *"For corporate and bank exposures, the PD is the one-year PD…"* then **¶68: "The PD for each exposure that is used as input into the risk weight formula and the calculation of expected loss must not be less than 0.05%."** RE's scoping of ¶68 by the corporate/bank heading is correct.

**¶121 verifies, including the QRRE distinction:** *"the PD for retail exposures is the greater of: (i) the one-year PD associated with the internal borrower grade to which the pool of retail exposures is assigned; and (ii) **0.1% for QRRE revolvers** (see paragraph 25 for the definition of QRRE revolvers) **and 0.05% for all other exposures**."* Recording the QRRE distinction rather than flattening it to 0.05% was the right call.

**The absence claim also verifies:** searching the document for PD-floor language returns only these two sites. **There is no sovereign or MDB PD floor in d424**, so labelling those UNVERIFIED with a conservative default is correct — it is an absence established by search rather than asserted, which is the S1 tier-ladder discipline applied to a negative.

One note for the eventual paper text: ¶121 also carries **LGD parameter floors** in the table immediately following, which we are not currently asserting. Not a defect — LGD is generated in a plausible band (0.251–0.600 across 40 seeds) — but if K3's anchoring statement claims "per-segment inputs anchored by IRB input floors", LGD is part of that claim and should either be asserted too or the claim narrowed to PD.

**Owed item closed.** Ready for the scoped round on F1's implementation.
