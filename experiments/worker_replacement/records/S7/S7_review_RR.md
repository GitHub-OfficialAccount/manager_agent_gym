# S7 — Reviewer-reproducer review (verbatim, received by DM 2026-08-08): FINDINGS

[Received and saved verbatim; F1 blocker-class — the max-effect quantity must be the one
the cells can move.]

S7 REVIEW — **FINDINGS. The capacity rulings are right and RE's C=3 correction of your C=4 is right. But the M redefinition has restored a large-looking number by counting CAPACITY, not information, and I can quantify the split.**

════════════════════════════
F1 (BLOCKER) — M/oracle ≈ 0.35 is ~80% "a warm body arrived", ~20% "and it covers X"
════════════════════════════
`M = oracle − oracle_without_successor`. Under C=3 with exact consumption (3 workers × 3 = 9 segments, zero slack), removing the successor leaves **6 capacity for 9 segments**, so three segments go **unstaffed and score 0**. The acceptance says so in its own words: *"without the successor: 6 capacity for 9 segments -> segments MUST go unstaffed."* M is therefore dominated by the raw capacity a *body* supplies, not by the coverage *this* body has.

**The decisive test, run over 12 seeds: drop the successor versus drop an arbitrary incumbent.**
```
mean M(drop successor)   2.9362      M/oracle ≈ 0.35
mean M(drop an incumbent) 2.3631
difference                0.5731     ≈ 0.068 of oracle
```
Same capacity loss either way. **The successor-specific, coverage-attributable part is ≈0.57 score points ≈ 0.068 of the oracle — not 0.35.**

**Why this blocks:** every experimental cell has the successor present, so no contrast in §8's grid realises M's counterfactual. What the channels can move is *which three segments* the successor gets, not *whether it exists* — capacity forces the manager to give it exactly three regardless of what it knows. So **M is not an upper bound on the channel effect; it is an upper bound on a comparison the design never makes.** This is my S6 F2 finding re-emerging through the capacity ruling: the number recovered its size, and the part that recovered it is not information.

**The measurable band, computed rather than argued** (oracle vs a capacity-respecting assignment that ignores coverage, 300 draws/seed):
```
seed  oracle   worst    (oracle − random)/oracle
   0  8.5797   6.5661            0.1484
   3  8.0377   5.7308            0.1634
   6  7.9578   5.1602            0.1835
   7  8.2210   6.9387            0.0892
```
An ignorant-but-staffing manager sits ~0.09–0.18 below oracle. **That is the real ceiling on what any channel can buy, and it straddles the declared MDE of 0.20 from below** — with the scripted baseline (which already reads the full-channel labels) at a median shortfall of only 0.2461 absolute ≈ 0.029 of oracle.

**Recommendation:** report M as the diagnostic it now is, and adopt **oracle − ignorant-assignment** as the published max-effect quantity, since that is the quantity the cells can move. It is offline, cheap, and already computable from existing code. If that quantity is what admission is thresholded on, expect the admitted count to fall sharply at MDE 0.20 — which is the honest outcome, and better learned now than after 45 episodes.

════════════════════════════
(1) THE CAPACITY RULINGS — BOTH CORRECT, ONE UNNAMED CONSEQUENCE
════════════════════════════
**The trade is right.** Under non-binding capacity greedy card-matching *is* the oracle, so condition 3 could never fire — RE escalating rather than patching was correct, and the one-line oracle was worth superseding for a real reason rather than defended for elegance.

**DP semantics verified as stated:** the maximiser may skip freely because scores are ≥ 0, so an unstaffed segment never helps it; the minimiser may **not**, or `worst` trivially unstaffs everything and collapses to zero. That asymmetry is genuine and easy to get backwards — RE's drop-order bug (6.2269 vs 6.3880) is exactly the shape that survives when a probe reimplements rather than calls, and it was caught by reconciliation, which is the right instrument.

**Your C=4 error and its correction:** RE is right, and the failure mode is worth naming for the record — **a single-instance generalisation** (the committed instance's load-6 read as typical, where 23/40 seeds have load exactly 4 and 2b refuses generation). That is the same class as the M3RL "mid-run" slip and my own S4 F3 output-floor misreading: a property observed once, promoted to a rule. Crediting it in §4.3 is right.

**The unnamed consequence you asked about — exact consumption removes all slack, and that is a runtime fragility, not just a design property.** 3×3=9 with zero slack means **any** worker refusal, failure, or timeout at runtime leaves a segment unstaffed scoring 0 — a 1.0-point hit, roughly 12% of oracle, from a single execution failure. Two consequences: (i) execution loss becomes *large and lumpy* rather than graded, which interacts badly with the signed-execution-term reporting (a refusal is indistinguishable in the aggregate from a badly-wrong report); (ii) an arm where one worker fails more often is penalised structurally, not behaviourally. **Recommend logging unstaffed-segment count per run as a first-class field** and reporting it beside regret, so a capacity-starvation artifact cannot be read as an allocation finding.

════════════════════════════
(2) THE NON-TRIVIALITY CLAIM — SURVIVES, WITH THE ARGUMENT STATED PRECISELY
════════════════════════════
The claim needs: no script over public information attains the oracle. Public = ratings, EAD, asset class, and therefore SA (SA is a pure function of class + rating). Private = the per-class PD calibration, hence the IRB truth.

**The claim holds, and the reason is that the *penalty* is |SA − truth|, which requires truth.** A script can compute SA exactly and can read coverage labels; what it cannot compute is how much a fallback *costs* on a given segment, because that is a function of the IRB number. Two segments with identical public fields can carry very different fallback penalties, since PD/LGD/M drive IRB and only PD's calibration is private. So the ordering over "which segments most need a covered worker" is not recoverable from public data. ✓

**One qualification worth stating rather than leaving implicit:** the script *can* recover the sign and rough magnitude in aggregate — SA is systematically above or below IRB by class, and a script that learned class-level tendencies from the public fields would approach, though not attain, the oracle. Condition 3 tests attainment (set-equality on the rejection list), which is the right test, but the claim in the paper should be *"no public-information script attains the oracle"*, not *"public information is uninformative"*. The five label-trivial rejections (seeds 8, 11, 14, 16, 29, shortfall exactly 0.0000 / −0.0000) show the test discriminating, and the set-equality assertion is the correct form — no more, no fewer.

════════════════════════════
(3) PD FLOOR CITATIONS — VERIFY BEFORE PUBLICATION; THE HONEST-LABELLING CALL IS RIGHT
════════════════════════════
I have not re-fetched d424 this round, so I am **not** signing off ¶68/¶66 (corporate/bank) or ¶121 (retail, with the 0.1% QRRE distinction) at source — that is a citation check I owe and will do before any paper text quotes them. What I do endorse now is the *method*: labelling sovereign/MDB **UNVERIFIED with a conservative default** rather than inventing a floor is the correct handling of an absence claim, and it is the same discipline as the S1 tier ladder. Flagging honestly: this is the one item in my pass taken entirely on report.

════════════════════════════
(5) RULING — ADMITTED, and the wording generalises past the instance
════════════════════════════
RE's find is a distinct failure from the §A test-shape rule and deserves its own entry:

> **When an assertion is redefined, its negative must be RE-DERIVED, not merely re-run.** A negative case is written against a *specific* failure mode; changing the assertion's semantics can leave the negative targeting the retired form, where it still passes and still asserts nothing. A passing negative is not evidence that the current assertion can fail.
> **Mechanical check:** after changing an assertion, confirm its negative fails *for the new reason* — mutate the assertion to always-pass and verify the negative then breaks. If it does not, the negative is decorative.
> _Origin: S5's assertion-2 negative went decorative when the assertion's semantics changed under the capacity ruling — still targeting the retired form, passing while asserting nothing. Caught by the marker-vs-assertion distinctness check, which was itself added for a different reason (S5), i.e. by an instrument built for another purpose._

The mutation check is the load-bearing half, and it is the same move as the negative controls in S1 and the trap tables in S3: **a check that cannot fail is not a check**, and the cheapest proof that it can fail is to break the thing it guards. I'll fold it into §A beside the test-shape rule.

════════════════════════════
(4) AND (6)
════════════════════════════
Condition 3's set-equality assertion is the right form and fires correctly on all five injected seeds. The null `rejection_reasons` regression is already in flight — worth one line in the record that it *is* a regression of an item closed in S6, because a re-opened finding is evidence about the fix, not just about the field.

**(6) One more, small:** `strict_count` is now uniform at 4 across all admitted instances and the strict list is demoted to diagnostic — but K2's published disclosure was *defined* on the strict count. If the disclosure still ships `k` and the strict list while the effect quantity is M, a reader gets two numbers that no longer refer to the same construct. **Recommend K2 publish the max-effect quantity it is actually thresholded on**, with the strict list clearly marked diagnostic-only.

════════════════════════════
VERDICT
════════════════════════════
**FINDINGS — not a pass.** F1 is blocker-class: the max-effect quantity should be the one the cells can move, and on current numbers that band (0.09–0.18) sits below the declared MDE, which is a design fact worth confronting before S8 assembles anything. The capacity rulings themselves I endorse, including RE's correction of yours.

**What I verified vs took on report:** verified independently — the drop-successor vs drop-incumbent comparison over 12 seeds, the ignorant-assignment band over 8 seeds × 300 draws, oracle/worst/spread under capacity, the exact-consumption arithmetic, and condition 3's rejection set against the injected seeds. Taken on report — the DP drop-order bug figures, the K6 curve's 23/40 load-4 finding, and the PD floor paragraph numbers (item 3, which I owe at source).
