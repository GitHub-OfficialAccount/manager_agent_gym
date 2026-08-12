# S6 — Reviewer-reproducer review (verbatim, received by DM 2026-08-08): PASS on deliverable; F2 blocks suite generation

S6 REVIEW — **PASS on the deliverable. Two findings, one of which I found by making the exact mistake the API invites, and one that says the suite should not be generated yet.** Your ruling is correct and the template's guarantees verify.

[Full verdict retained verbatim below.]

════════════════════════════
(1) THE RULING AND THE TEMPLATE — VERIFIED
════════════════════════════
**Roster-correctness is right**, and the pool/roster distinction is real: the pool holds predecessor and successor simultaneously, a team that never exists.

**Template properties, checked against the committed instance** (which I confirmed is *fresh* — `to_json(generate(101))` is byte-identical to the committed file, so I was reviewing the current generator, not a stale artifact). Role mapping A=corporate, E=bank, B=retail, C=sovereign, D=mdb:
- four distinct equal-size sets ✓ non-nested;
- A (corporate) has exactly two holders, and they are the swap pair ✓;
- **E (bank) is held only by the predecessor → post-swap coverage is {corporate, retail, sovereign, mdb}, bank uncovered ✓** — I verified this is what produces the interior spread: `seg_01` (bank, IRB-applicable) is the *only* segment whose per-segment max differs pre vs post (1.0000 → 0.5514), and that single segment is the entire 8.5514-vs-9.0000 gap;
- post-swap every segment remains serviceable via SA ✓.

**Designation-by-role was necessary, not cosmetic** — this is the check you asked for and it confirms the change. The template creates **three** two-holder classes (A, B, C). Lexicographic search over permuted labels would have picked whichever of those sorted first, which is a *different class each seed*, and if it picked B or C the predecessor would not be w0 — so **E would keep a holder post-swap, and the oracle would be perfect again**. Role designation is what makes the sole-class guarantee survive the permutation. The permutation layer itself is sound: 5! labelings, and the sweep's `swap_shared_class` spanning all five classes confirms F-B is resolved at the root rather than reported.

════════════════════════════
(2) THE STRUCTURAL PROOF AND THE TEST INVERSION — SOUND, WITH ONE HONEST LIMIT
════════════════════════════
The proof is correct as stated: among 2-subsets of a 4-set, only C(3,2)=3 avoid any given element, so four distinct 2-subsets must cover all four classes — every IRB segment always had a covered worker, oracle always perfect. That is why 60/60 were oracle-perfect and why the fix had to change the class count, not the draw.

**The 0/60 result is the real evidence; the labelled fixtures are arithmetic checks.** Both reject and accept paths run on hand-built fixtures, which is honest *because it is labelled* — but worth stating plainly: since the generator can no longer produce an oracle-perfect instance, the reject path is exercised only synthetically, and a regression that reintroduced oracle-perfection **through the generator** would be caught by the 0/60 sweep and not by the fixture test. Both exist, so coverage is complete; the record should just not credit the fixture with more than it does.

════════════════════════════
(3) THE CANARY-CAUGHT CONSTRAINTS — THE CLIP FILTER IS COMPLETE, WITH ITS SCOPE STATED
════════════════════════════
`score_report = 1 − min(1, |report − truth|/truth)` hits zero exactly when `|SA − truth| ≥ truth`, i.e. when **SA ≥ 2×truth** or **SA ≤ 0**. Those are the only two roots. A6 forecloses `SA = 0`; the new filter forecloses `SA ≥ 2×truth`. **So for a segment whose report is the SA fallback, the enumeration is exhaustive — there is no third route to roster-wide worthlessness.** Complete.

**Scope worth recording:** the filter is applied to *sole-class* segments, which is right — it protects the **oracle**. It does not eliminate the clip region on non-sole-class segments, where an uncovered worker's fallback can still clip and the **execution term cannot penalise a fabricator** (my S4 finding, §4.1's paragraph). The committed instance reports `clip-flagged segments: []`, so the flagging exists and currently fires on nothing. Fine — just don't let "clip filter complete" be read as "no clip region anywhere".

**Your A4 canary firing twice is the strongest vindication in this step.** I proposed it as a cheap regression detector on A6's premise; it caught two constraints your ruling implied but did not name. That is more than it was designed for, and it argues for the restatement over deletion in a way I could not have shown at the time.

════════════════════════════
(4) DISCLOSURES — ALL FOUR PRESENT; K3's HEADLINE COUNT IS MISLEADING (F1)
════════════════════════════
K1 (7 points, two self-rejecting at the low-fraction end — the domain boundary made visible, which is better than a truncated curve), K2 (present, see F2), K4 (lattice per instance; 35 distinct across 40 — my S3 second-channel finding closed) all check out.

**F1 — K3's "4 anchored / 5 unanchored" overstates the anchor's reach, and the direction of the error flatters us.** Every one of the four `anchored=True` segments has `ratio 1.0` — they are SA-applicable segments where SA *is* the truth, so there is no IRB/SA divergence for the output floor to bound. Meanwhile the genuinely divergent segments (0.4667, 0.5372) are all `anchored=False`. **Among the segments the anchor was introduced to bound — IRB-applicable, SA ≠ truth — the anchored count is zero.** Reporting "4 anchored" invites a reader to conclude the floor covers 44% of the distribution when it covers none of the part that matters. Fix: report anchored-share **among IRB-applicable divergent segments**, or state that ratio-1.0 segments are trivially anchored and excluded from the count. This is my own S4 F3 correction landing one level deeper than I stated it.

════════════════════════════
(5) YOUR WATCH ITEM — F2, AND MY CALL IS THAT IT BLOCKS SUITE GENERATION
════════════════════════════
The K2 curve settles this without a pilot, which is the good news:
```
k=1  strict 1  headroom +0
k=2..5  REJECTED by assertion 3
```
**Strict count 1 is structural, not a seed accident.** The template gives the successor sole post-swap holding of exactly one class (A), so the strictly-required set is *A's IRB-applicable segments*, which at 9 segments over 5 classes is ~1. k cannot be raised without rejecting nearly every instance — the curve shows that directly.

**The consequence is quantitative and it is the blocking part.** The measurable arrival-information effect is bounded by the strictly-required segments: for every other segment, some other post-swap worker scores identically, so knowing about the newcomer buys nothing. One segment out of an 8.5514 oracle is **≤ 0.117 of the oracle, normalised**. My continuous-DV power re-derivation put the minimum detectable effect at **Δ ≈ 0.13–0.20 at n=9/cell** (σ≈0.10, rising if regret is bimodal). **The design's maximum possible effect is smaller than its minimum detectable effect** — and the realised effect will be strictly less than the maximum, since a manager would have to route that one segment perfectly in every informed cell and never in cell 0.

**Call: this blocks suite generation, not because generation is expensive but because the suite would be unusable and would look fine.** Forty admitted instances all carrying a sub-detectable maximum effect is exactly the artifact that gets mistaken for a validated benchmark. The fixes are all generator-side and cheap, and at least one must land first:
- **raise the strict count structurally** — a template where the successor is the sole post-swap holder of **two** classes rather than one (needs a sixth class or a different role assignment; RE's design call, not mine);
- **bias segment allocation toward the sole-post-swap-holder class**, so that class carries 2–3 IRB-applicable segments rather than ~1 — cheapest, and it moves the effect without touching the lattice;
- **raise n per cell**, which fights the wrong end: at a maximum effect of 0.117 you need the *effect* raised, not the noise lowered.

I'd take the second, and re-read the K2 curve after: the acceptance already prints headroom-vs-k, so the check is free and immediate.

════════════════════════════
(6) F3 — `oracle()` SILENTLY OVERRIDES THE WORKERS YOU PASS
════════════════════════════
Found by doing the natural thing. `oracle(instance, workers=None)` resolves the roster via `roster_workers(instance)`, which **filters `instance["workers"]` by `event.roster_post_swap`**. So a caller who builds a pre-swap subset and passes it through `instance["workers"]` gets that subset **intersected with the post-swap roster** — for the committed instance, two workers instead of three — and a plausible-looking number (I got 8.2031) that means nothing. No error, no warning.

Post-swap-default is the right default and I am not disputing the ruling. The defect is that the override is **silent**, and it lands on exactly the caller your own question anticipated: cell-U reporting needs `phase="pre_swap"`, and getting it wrong produces a number rather than a failure. **Fix: raise when explicit `workers` are inconsistent with the resolved roster**, or require the phase argument at the `oracle` boundary rather than defaulting inside `roster_workers`. One check; it converts a silent wrong answer into a loud one, which is the same discipline as F2-in-S2's fail-closed accessor.

════════════════════════════
VERDICT
════════════════════════════
**PASS on S6's deliverable** — gate, sweep, and all four disclosures are correct, and the ruling round genuinely fixed a structural defect rather than tuning around it.

**Findings: F2 blocks suite generation** (sub-detectable maximum effect; fix generator-side, then re-read the free K2 curve). **F1** (K3 anchored-count) and **F3** (silent roster override) are limitations with one-line fixes. The clip-filter completeness question is answered: complete for its scope, with the scope stated.

**What I verified vs took on report:** verified independently — the committed instance is byte-identical to `generate(101)`; the template's four properties by role mapping; that `seg_01` (bank/IRB) is the sole source of the interior spread; the three-two-holder-classes argument for role designation; the clip-root enumeration; the K3 anchored/ratio correspondence per segment; and F3 by direct call. Taken on report — the 100-seed generation totality, the 0/60 and 60/60 sweep counts, and the 35-distinct-lattice figure.
