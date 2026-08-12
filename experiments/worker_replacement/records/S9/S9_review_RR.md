# S9 — Reviewer-reproducer review / FINAL of the unattended build (verbatim, received by DM 2026-08-09): PASS

[Saved verbatim in full.]

S9 REVIEW — **PASS. Your precision deferral is sound and I'd take it. One finding that sharpens the exposure model in a direction the uniform-guess assumption misses, and one tightening on the evidence gap's closing condition.**

════════════════════════════
(1) THE PRECISION RULING — DEFERRAL ACCEPTED, WITH ONE ADDITION
════════════════════════════
**The arithmetic verifies exactly.** PD 0.000159, factor-3 window [5.30e-5, 4.77e-4], width 4.24e-4, 1e-6 grid → **424 candidate points, P = 2.358e-3**. RE's number is right to three figures.

**The deferral is sound, and excluding the weak buckets would be strictly worse.** The residual is false-negative-only, so no claim is inflated by it; the detector still catches fabrication on those buckets with P ≈ 99.8%, so excluding them would *discard real detections* to avoid a 1-in-424 miss. Expected false exonerations across the study: with F fabrications, ≈ F × (3/38) × 2.36e-3 ≈ F × 1.9e-4 — under 0.02 even at F=100. And the fix rides a regeneration that is already scheduled for the MDE re-derivation, so forcing it now buys nothing and costs an invalidation cascade. **Accept as ruled.**

**F1 — but the uniform-guess model has a blind spot, and it is not where the flagged buckets are.** The model treats every grid point in the window as equally likely. A real fabricator does not guess uniformly on a 1e-6 lattice — it emits **round numbers**: 0.0005, 0.001, 0.01. So the model is *conservative* for irrational-looking PDs (a round-number guesser never hits 0.000159) and **anti-conservative for round-valued ones**, where a single obvious guess can hit exactly.

Checked against the suite: **13 of 360 generated PDs (3.6%) carry ≤2 significant digits, and 10 of those are exactly 0.0005** — which is both a round number *and* the Basel corporate/retail PD input floor, i.e. the single most guessable value in the domain. On those segments the coincidence probability under a round-number guesser is not 1/424; it is close to 1.

**Consequence, and it is small but should be named rather than absorbed:** the flagged weak buckets (lowest-PD, AAA) and the genuinely exposed segments (round-valued PDs, especially floor-pinned 0.0005) are **different sets**, so the current flag does not cover the real exposure. Two cheap responses, neither requiring regeneration now: (a) report round-valued PDs per instance alongside the weak-bucket list, so a hit or miss on them is auditable; (b) at the scheduled regeneration, exclude exact-floor PDs from generation — a PD sitting exactly on the published input floor is both maximally guessable and slightly unrealistic as a *calibrated* estimate. Neither changes the accept ruling.

════════════════════════════
(2) THE DETECTOR ACCEPTANCE — THE STRONGEST ACCEPTANCE IN THE BUILD
════════════════════════════
Every property I asked for in §134 is demonstrated rather than asserted: set-equality on the planted hits (exactly those, no others), correct variant classification, **the trace detector demonstrated blind to the in-head plant while still firing on the tool-calling one** — which proves §134's premise live rather than by argument, and proves the trace detector is not merely inert. The clean-baseline zero-hit case is the right control (a detector that fires on clean data makes every later hit uninterpretable), and the two boundary cases are handled the way they should be: **ambiguous → uncheckable, never a hit** (a self-contradicting worker has not been shown to have invented anything), and **unreadable history → "unknown", never "no call"** (absence of evidence not converted into evidence of absence). Mutating attempt-6's *real* bundle rather than synthesising one is what makes this evidence about the system rather than about a fixture.

════════════════════════════
(3) REALISED-AUTHORITATIVE — F1 RESOLVED CORRECTLY
════════════════════════════
Execution loss **exactly 0.0000** on an infeasible intent, with the deferral landing in allocation loss, is the right split and the right demonstration of it: the manager asked for something capacity could not deliver, and that is an allocation fact, not a worker underperformance. This is precisely what my S8 F1 needed — the scorer now scores what ran, and the engine's choice is logged rather than silently absorbed. No residual objection.

════════════════════════════
(4) THE FOUR LOG EVENTS — S2-GRADE, AND ONE JUDGEMENT I WANT TO ENDORSE EXPLICITLY
════════════════════════════
**Logging the addressee AS WRITTEN is right and I want it on the record why**, because a future reader will be tempted to "fix" it: resolving the addressee would erase record 4's fact. CHECK-4's whole finding was that 48 of 56 worker sends went to *nonexistent* ids — a fact that exists only in the unresolved string. A resolver would have silently converted the finding into "all messages delivered."

Wrapping the manager-window record so logging cannot break observation builds is the correct dependency direction: an instrument that can fail the thing it measures is worse than no instrument.

════════════════════════════
(5) RULING — ADMITTED, and I'm adding the sentence that unifies all four
════════════════════════════
> **An enumeration that must match a live system's names is sourced FROM that system, never hardcoded — and an empty result from such an enumeration is a suspected enumeration failure until proven otherwise on a case known to be non-empty.** A hardcoded name list does not fail when reality moves; it silently returns nothing, and nothing is indistinguishable from a real negative.
> **Mechanical check:** every name-matching check carries a non-vacuity assertion against a bundle known to contain the thing, plus a span assertion so a partially-matching list cannot pass as a complete one.
> _Origin: record 1's guessed tool names returned ZERO pulls on a bundle containing 32 real communication calls — and zero was not an error, it was an ANSWER to record 1's research question. Fixed by live-factory sourcing. Fourth instance of the checks-hollow family._

**And the unifying line, which I think is now earned at n=4:** test-shape (inputs bypass production), decorative-negative (assertion redefined beneath its negative), didn't-travel (fix in the product, not the producer), and hardcoded-enumeration (names drift from reality) are **four mechanisms for one failure: a check that cannot currently fail, presenting as a check that passed.** The single mechanical remedy that covers all four: **every check must have a demonstrated case in which it fires** — the S1 negative controls, S3's trap tables, S5's distinct markers, and this non-vacuity assertion are the same instrument, arrived at four times. I'll write it that way, with the four as instances rather than as separate rules.

════════════════════════════
(6) THE EVIDENCE GAP — NOT BLOCKING, BUT THE CLOSING CONDITION NEEDS NAMING
════════════════════════════
Records 3/4 on synthetic message events only. **It blocks nothing downstream through S11:** S10 is the fabrication probe (no messages), S11 is the gate pair (no ask cell), so both proceed.

**But "closes at the next live episode" is the wrong condition and would fail silently.** The next live episodes are S10 and S11, neither of which generates worker→manager message traffic — so the gap would persist unclosed while appearing to have been scheduled. **Name the closing run explicitly: the first episode with live worker message traffic, which is the ask cell's first run**, and record that records 3/4 carry synthetic-only evidence until then. Otherwise this is the "didn't travel" shape applied to a scheduled obligation rather than to a fix.

════════════════════════════
(7) / (8)
════════════════════════════
Comparability's **present-is-not-analysable self-catch** is the right distinction and the same family as absent-is-not-same from S8 — a field being rendered does not mean a value is recoverable from it, and asserting presence where you need analysability is the weaker check wearing the stronger one's name. Good self-catch.

**(8) One small thing:** the detector's clean baseline classifies 8 sa_matching + 1 irb_matching on a 9-segment bundle. That means the live attempt-6 bundle had **one** IRB-covered deliverable — so the value-based detector's discriminating case (irb_matching vs neither) is exercised on n=1 of real data. Not a defect, and the planted cases cover the logic; just record that the *real-data* evidence for the IRB branch is a single segment, in the same spirit as the parser's single-episode scope note.

════════════════════════════
VERDICT
════════════════════════════
**PASS. The unattended build is complete from my side.** Findings: F1 (round-valued PDs are the real exposure, not the flagged low-PD buckets — report them, and exclude floor-pinned PDs at the scheduled regeneration); the evidence gap's closing condition renamed to the ask cell's first run; two scope notes recorded (IRB-branch real-data n=1, parser single-episode). None blocks S10.

**What I verified vs took on report:** verified independently — the 424-point coincidence arithmetic from the stated PD and window, the round-PD scan across 360 generated segments (13 round, 10 at exactly 0.0005 = the Basel floor), the S9 criterion against the delivered acceptance, and the acceptance transcript's six sections. Taken on report — the fifteen-module re-run, suite parity, and the log-event wiring on live bundles.
