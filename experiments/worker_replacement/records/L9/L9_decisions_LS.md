# L9 — decisions after both peers' step-1 pushback (LS, 2026-08-08)

Both peers objected to step 1 as I specified it, independently and from different directions, and
**both objections are upheld.** This file records what changes, in what order, and what I got
wrong. Inputs: `card_belief_model.json` + `lattice_enumeration.json` (RE), `L9_review_RR.md` +
`realism_probe.py` (RR).

---

## D1 — The belief model is wrong and is fixed FIRST, before anything is priced

**Upheld, and verified independently in source.** `finance_scorer.py:740` — `believed_score`
returns 1.0 where the card claims coverage and otherwise **falls through to `true_score`**. So
wherever the card is SILENT about a class the successor really covers, the manager is credited
with knowing it anyway.

A registry card is a **complete description of what a worker is qualified for**, not a partial
one. Believing a stale card means believing the successor covers *exactly* the predecessor's
classes — the omissions are part of the lie, not a gap the manager fills in from the truth.

**This is the SECOND time this one function has been wrong by not asking the study's question.**
First the baseline (oracle − random, when the manager always holds a card); now the belief. Both
were arithmetically correct and semantically wrong, and both survived review because the number
they produced looked reasonable. **A ceiling function must state its baseline AND its belief
model, and be tested on a case where the two candidate beliefs must diverge.**

- **Nothing published on the current template changes.** RE's positive control: the two models
  agree on 30/30 seeds, because the successor's silent class is always incumbent-covered there.
  The 1.24% / 0.16σ headline stands.
- **On the disjoint candidate the shipped model misses 96% of the effect** (0.37% vs 8.51%).
- **Acceptance for the fix:** the control (agreement on the current template) and the divergence
  (disjoint) are both asserted, so a future revert cannot pass silently.

## D2 — Order of operations, corrected

RE is right that my ordering was unsafe. Selection excludes zero-ceiling instances **using the
defective model**, so a template whose value lies in the card's omission would be scored zero and
**silently excluded before it was ever priced.**

    1. fix the belief model  ->  2. re-derive the admissible set  ->  3. price

Re-deriving the admitted set now has two independent reasons: the ignorant-baseline fault (already
recorded) and this one.

## D3 — Step 1's METHOD is dead. Coverage substitution cannot price six classes

**Upheld, both peers, independently.** Every instance has 9 segments over exactly 5 classes.
Substituting a template that mentions a sixth class puts coverage on a class with **zero
segments**: it does not raise, it prices the template's **five-class projection** and reports it
under the six-class name. RE adds a second, mechanical reason — `labels_of()` recovers the
permutation by `.pop()`-ing sets it assumes are singletons, which at size 3 is undefined rather
than merely inaccurate.

**Consequence: the `partial_overlap` row reading 0.00% in RR's realism table is not a price.** It
is the artefact of pricing a six-class template against instances that have no sixth class. It
must not be quoted as evidence about partial overlap in either direction.

**So step 1 is NOT "offline, zero spend" as I wrote it.** It needs generated instances.

## D4 — The sixth class goes in the GENERATOR, not in the pricing module

RE offered to build it as a stand-in inside the pricing module to avoid touching the generator.
**Declined, and my own instruction is what created the false choice.**

"Do not change the generator before the ceiling is priced" was aimed at building a lattice
*variant* for the study. **Adding the class that makes pricing possible at all is not that**, and
RE was right that the two constraints as stated cannot both be satisfied.

The reason to prefer the generator is the failure mode we have now hit three times: **the pricing
path runs while the generation path never does.** RE's own proposed template raises `IndexError`
in `swap_shared_class` and had never been generated; `_designate_swap_pair` was believed live on a
path it does not run on. A stand-in inside the pricing module reproduces exactly that shape — a
second source of truth for the segment mix, priced but never built.

**Conditions on the sixth class:**
- **Economics are a documented CLONE of an existing class** — same SA weights, same PD floor, same
  rating pool — so the price isolates the LATTICE instead of confounding it with new Basel weights.
  **No BCBS citation, because nothing is being transcribed.**
- **It is explicitly marked synthetic and is not the version that ships** if partial overlap wins.
  A clone gives a neutral-economics estimate; a real sixth class could price above or below it,
  and **we will not know the direction.** That is a stated limitation, not a resolved one.
- **RR's assertion lands with it:** generation raises if any class named by a template has no
  segment. That is the check that would have caught D3 at the source.

## D5 — Realism: disjoint is disqualified on validity, pending the size-3 price

RR measured what I had called a judgement call, which is the right response to "we cannot compute
this" (`realism_probe.py`, 30 seeds, exact, CAP=3):

    template            ceil vs card   ceil vs ignorant   card-ignorant   card WORSE than blind
    current                   0.85%              9.95%         +0.7786        0/30
    proposed_disjoint         8.51%             11.02%         +0.2203        7/30
    partial_overlap           0.00%             11.02%         +0.9614        0/30   <- see D3, not a price

**Under disjoint the stale card retains 23% of its partial-overlap value and is actively
misleading — worse than coverage-blind random, beyond 2 MC SEs — on 7 of 30 seeds.** A successor
whose predecessor's card is that uninformative is not *the same job done by someone else*; it is a
different specialist walking in. **That is the setup answering a different question from the one
we claim to answer**, and it is what the researcher's guidance was pointed at.

**I asked RR to tell me if disjoint stops being our problem even where it prices better. It does,
and I am taking that over the σ.** Disjoint is now the fallback, not the leading option, and if it
is chosen the limitation goes in the paper explicitly rather than being priced away.

**This changes the shape of the decision.** It was "which template wins on two axes". It is now:
does a realistic template clear detectability? **If size-3 partial overlap does not, the study has
no manipulation that is both valid and measurable** — and that goes to the researcher, because it
changes what the paper can claim.

## D6 — My 6,480 was right for a predicate I never stated

RR: the ordered count under the core conditions is **12,960**; up to incumbent symmetry, **6,480**;
adding O3 (successor strictly required post-swap, which the generator *asserts*), **6,480 ordered
and 3,240 up to symmetry**. **So 6,480 is two different counts that coincide over different
template sets, and I quoted it without saying which.**

Nothing in the decision turns on 3,240 vs 6,480 — both are enormous. **But "my number
reproduced" is not what happened**, and this is the third enumeration this phase whose agreement
was less informative than it looked. Going forward the count is quoted as
**"12,960 ordered / 3,240 admissible-and-generator-legal up to symmetry"**, or not quoted.

**What both peers independently confirmed, having gone looking to refute it: five classes at size
3 admits ZERO templates, structurally.** Three 3-subsets of the four remaining classes cover each
of them at least twice, so the successor can never sole-hold anything. **The sixth asset class is
a real cost, not an avoidable one.** RE's attempt to refute my costing and RR's independent
enumerator both landed on it.

## D7 — Reconciliation and cleanup items

- **`0.85%` (RR, 30 seeds) vs the published `1.24%` headline** — different populations, almost
  certainly, but **neither is quoted with its population as a predicate**, which is standing rule
  5. One of them is restated with its predicate or both stop being quoted.
- **The 57.1% free-draw figure does not reproduce** (RR gets 90.5%; no conjunction gives 120/210).
  Not load-bearing — construction wins because generation is *total* — but it sits in a docstring
  and will be cited again. Fix or drop.
- **`records/L9/lattice_template_proposal.md` carries the `_designate_swap_pair` dependency claim**,
  which is wrong; RE has the correction drafted.

---

## The prediction protocol, for the size-3 price

RR logged theirs before RE reports, unprompted, which is the protocol working. **Mine is below and
was written before I had RE's.** RE has been asked for theirs privately and RR's has NOT been
relayed to them.

**LS:** the pool splits hard on carrier count and the pooled number is meaningless. The
**two-carrier subfamily prices in the same band as disjoint** (within a factor of 2 of 8.51% under
the corrected belief model); the **single-carrier subfamily prices near zero**, like the current
template. So the decision rests on the two-carrier subfamily at a defensible mix, not on "size 3".

**Where this diverges from RR:** RR predicts the whole pool at 2–5%, i.e. *below* disjoint,
because redundancy (mean post-swap coverers per class 1.20 → 1.50) lets the manager substitute out
of a misallocation. I expect that effect to be real but confined to the single-carrier half.
**The discriminating observation is the two-carrier subfamily's price**, and we disagree about it
by roughly a factor of two.

**This is why the experiment is worth running rather than confirmatory:** we agree on the ordering
and disagree on the level, and **the decision turns on the level** — RR's own conditional is that
below ~0.5σ the ranking inverts back to disjoint.

**Reporting requirement, from RR and adopted: any size-3 number is reported SPLIT ON CARRIER
COUNT.** A single headline for "size 3" is the nA artefact returning by a different door, and
every σ carries its mix parameter.

---

# Addendum, same day — after RE's mix sweep, carrier test and prediction

Inputs: RE's `check_mix_sweep.py` (L9-e) and carrier stratification (L9-f), committed 3822e2d.

## D8 — The matched-mix correction, and a comparator error I propagated

RE measured nA per cell over 120 label permutations × 10 seeds under the **corrected** belief
model:

    sigma           nA=0    nA=1    nA=4   pooled     cells:  32% / 48% / 20%
    current         0.03    0.06    0.07    0.05
    disjoint        0.18    0.45    1.11    0.50

**Two things follow, and the second is not what my own correction implied.**

1. The forcing did inflate the headline: 1.11σ is the nA=4 row, 20% of the label space, and the
   no-forcing pooled figure is 0.50σ. That part stands.
2. **At MATCHED mix the disjoint template beats the current one 6–7× at every nA, including
   nA=0.** So the forced mix inflated the ABSOLUTE LEVEL; **it did not manufacture the template
   DIFFERENCE**, which is what the retraction was widely read as saying.

**"nA=0 is IDENTICAL to the current template" is a comparator error and I accepted it without
checking.** It compares disjoint-at-nA=0 against **current-as-shipped**, which carries its own
`shared_class_segments = 4` forcing — not against current-at-nA=0, which is 0.03σ. **Same shape as
the six §B failures: a number that is arithmetically right and semantically about something else.**
It is in `check_template_pricing.py`'s docstring, in `records/L4/DIRECTIONS_LS.md`, and in this
file's parent commit. RE corrected the docstring; the rest are corrected here.

**This cuts against my own D5 ranking, so I am stating it plainly rather than burying it: on
DETECTABILITY the disjoint template is far stronger than I had it — 10× the current template
pooled, not "0.16σ to 1.02σ, possibly no better than today."** Its demotion to fallback rests on
RR's validity finding alone, and that is now the whole of the case against it.

## D9 — RE's carrier test makes D1 load-bearing rather than merely correct

RE tested four candidate definitions of "carrier" against RR's 2,160/4,320 split instead of
assuming which was meant. Three are constant at 1 across all 6,480. **Exactly one reproduces the
split: classes the card is SILENT about that the successor SOLE-HOLDS.**

**So the second carrier IS the omission — precisely the half the shipped belief model prices at
zero.** Pricing the 6,480 with the shipped model would score all 4,320 two-carrier templates as
single-carrier: it would not measure RR's stratification, **it would collapse it by construction**,
and the output would read as "carrier count doesn't matter" — the opposite of the truth, produced
by an instrument blind to the variable. Two independent objections turn out to be one.

## D10 — The sixth class is a CLONE now, transcribed only if it ships

RE asked for this call. **Clone for the decision; transcribe if and only if the class survives into
the built design.**

A clone isolates the lattice, which is exactly what a ceiling comparison wants. It is
**indefensible the moment the sixth class appears in a reported result**, so the clone carries a
marker that **raises if used on a live study path**. Two-stage: cheap now, honest later, and the
expensive half is only paid if partial overlap wins.

## D11 — ★ A SECOND CIRCULAR DEPENDENCY, of the same shape as L2/L3, found before it bit

**Every σ in this decision divides by σ = 0.0768, which is the PRE-L1 measurement and which we have
already ruled must not size a suite.** So:

    L9 step 5 "does it clear detectability?"  needs an absolute sigma
    an absolute post-L1 sigma                 needs L3's bundles
    L3                                        is blocked on L9

**L9 as scoped cannot be finished before the thing that depends on it** — the same circle as
`L2 -> L3 -> L2`, and it would have surfaced at the decision rather than now.

**Broken the same way:**
- **L9 decides on RATIO plus REALISM.** Ratios survive a change of σ; absolute levels do not.
  Template A beats template B by 6–7× regardless of what σ turns out to be.
- **The absolute detectability verdict moves OUT of L9** into a step after L3 supplies a post-L1 σ.
  **No one says "clears detectability" until then**, in either direction.

**Consequence for RE's framing warning, which was well made:** *"if the answer is ~0.25σ, the
honest conclusion is that neither candidate reaches detectability and the sixth class was spent
finding that out."* **That conclusion is not available yet either** — 0.25 pre-L1 σ is not 0.25
post-L1 σ, and L1 repaired an instrument whose noise was part of the old denominator. The
defensible statement is the ratio.

## D12 — All three predictions are in; the comparison, and my own is the weak one

| | prediction for size-3 partial overlap |
|---|---|
| **LS** | pool splits hard; two-carrier **within a factor of 2 of disjoint**; single-carrier near zero |
| **RE** | two-carrier **~0.35σ**, single-carrier **~0.12σ**, pooled **~0.25σ**, split **~3×**; below disjoint's nA=1 row (0.45σ) |
| **RR** | **2–5% of oracle pooled**, below disjoint; bimodal; single-carrier ≈ current (undetectable), two-carrier ≈ disjoint's structure |

**We agree on more than I expected: all three predict a split, two-carrier above single-carrier,
and the pool below size-2 disjoint.** Under my own rule that is the point to ask what the exercise
adds beyond confirmation.

**It adds the one thing all three of us are uncertain about: WHERE the two-carrier group lands
relative to disjoint** — RE says 0.78× (0.35 vs 0.45), RR says below, I said within 2×.
**And my prediction is the badly formed one: "within a factor of 2" spans 0.25× to 1.0× and
contains RE's point estimate, so it cannot be refuted by the result.** RE's is the model to copy —
a point estimate, a mechanism, and explicit refutation conditions (two-carrier ≥ 0.45σ, or a split
below 1.5×).

**RE's positive control is the best part of the protocol so far and is adopted: a split near 1.0
is not a finding, it is the belief-model fix failing to take**, because the second carrier is
defined as the thing the old model priced at zero.

**Since the ratio is what decides (D11), the discriminating quantity is
`two-carrier size-3 / disjoint at matched mix`.** LS ≥ 0.5, RE ≈ 0.78, RR < 0.5 — we are not
predicting the same thing, so the exercise is not confirmatory.

---

# Addendum 2, same day — after RR's σ-invariance and clone-bias measurements

Input: `records/L9/L9_clone_and_sigma_RR.md` (RR), script at `266049e`. **Both questions I asked
came back in my favour, and RR said so plainly rather than manufacturing an objection.**

## D13 — The σ-invariance break holds, WITH a scope condition that goes in the record

RR did not test the arithmetic (σ cancels from a ratio — trivially true and not the risk). They
tested **the hidden premise: that there IS one σ.** A template that changes the lattice changes the
outcome distribution, so if disjoint widens the spread, dividing by the current template's σ
overstates it and the ratio of *detectabilities* stops being the ratio of *ceilings*.

    template            SD/oracle (all 1680 feasible)   vs current
    current                                    0.0410       1.00x
    proposed_disjoint                          0.0431       1.05x
    partial_overlap                            0.0431       1.05x

**1.05× against ratios of 6–16×: it cannot reorder anything.** Three riders, all adopted:

- **The residual is SIGNED and points AGAINST the fallback.** Disjoint has the wider spread, so a
  shared σ **overstates disjoint by ~5%.** The correction, such as it is, argues against the
  template I demoted — not for it.
- **The proxy omits across-episode manager variability**, which is most of the gap between ~0.041
  and the published 0.0768. That component is a property of **the manager, not the lattice**, so
  there is no mechanism for it to differ by template — which makes the break *safer* than the
  proxy alone shows.
- **★ SCOPE CONDITION: the break is valid HERE, measured — not as a general principle.** It would
  fail for a candidate template that **changes the number of uncovered classes**, which every
  admissible template so far fixes at exactly one. **Any future template that changes that number
  re-opens this question and must be re-measured.**

## D14 — The clone bias is signable, bounded, and second-order. So BRACKET it instead of choosing

The ceiling is paid in one currency — score lost when a coverage gap forces the SA fallback — and
that is a property of the **class**, which a clone inherits exactly. So the bias is the
source-vs-real gap:

    mdb 0.3564   retail 0.3509   sovereign 0.3333   bank 0.2575   corporate 0.2393
    class mean 0.3075;  end-to-end spread 1.5x

**Cloning corporate/bank understates by ~20%; mdb/retail/sovereign overstates by ~14–16%.
1.5× end to end cannot flip a 6–16× ranking — but the SOURCE CHOICE is now a decision, not an
implementation detail.**

**DECISION: do not choose a source. Price under TWO — `corporate` (low, 0.2393) and `mdb` (high,
0.3564) — and report the BRACKET.** The enumeration takes seconds, and it converts a judgement
call into a stated interval. **A single-source number would be a point estimate whose error bar
exists and is unreported**, which is the shape of six earlier failures. Every reported figure names
its clone source.

**Direction against a REAL sixth class, held weakly and marked as such:** the five transcribed
classes occupy the low-divergence end, and the plausible real candidates (equity, real estate,
specialised lending) sit at the high-SA-weight end — so **a clone most likely UNDERSTATES a real
sixth class**, and if the clone clears, a real class clears by more. This rests on schedules we
have not transcribed. **Expectation with a named mechanism; not a measurement.**

**And the finding that actually matters is not the clone.** Within-class variation **dwarfs**
between-class: SD ~0.18 inside each class (range 0.002–0.754) against a 0.12 spread between them.
**Which segments land in the class matters far more than which class is cloned** — putting the
clone behind the segment mix, the same parameter that produced the 38.2× swing (**corrected from
27× — see D17**). **A clone-priced
figure is adequate for ratios and inadequate for absolute n, which is exactly the split D11 makes.**

## D15 — The manufactured-tie check is REQUIRED, not optional

RR flagged it as optional. **Upgraded, and it is the only thing in their message I am overriding.**

Two classes with identical economics and different coverage make cross-assignments score
**exactly** equal, **manufacturing exact ties in the allocation optimum** — resolved by enumeration
order. **Tie-break luck is an established failure mode in this project** (it is why label
permutation exists at all), and this is a tie we would be **creating with our own construction**,
inside an optimum whose value is the study's headline.

**Required with the six-class generator:** compare the exact-tie rate among optimal allocations
against the five-class case. **If it rises, the tie-break becomes explicit** rather than being left
to iteration order. Cheap, and the alternative is discovering it in a published number.

## D16 — Absolute episode counts, again

RR's message still quotes *"~494/arm at nA=0, ~64 pooled, ~13 at nA=4"* as the surviving half.
**The SWING survives; the three counts do not** (and the swing is **38.2×**, not 27× — D17) — they divide by the pre-L1 σ that must not
size a suite (D11). The substantive point is right and important: **the mix is a declared design
choice, not an inherited one.** It is stated as the swing.

## D17 — The swing is 38.2×, not 27×, and the corrected form is OUTSIDE D11 by construction

RR recomputed after my D16 objection and found their own figure wrong. **Verified independently
here from the raw shares before adopting it:**

    disjoint template, mean ceiling share by nA (10 seeds x 120 labelings)
      nA=0  0.013756 (n=384)   nA=1  0.034689 (n=576)   nA=4  0.085066 (n=240)   pooled 0.038066

      effect ratio  nA=4 / nA=0   = 6.184      required-n swing = ratio^2 = 38.2x
      effect ratio  nA=4 / pooled = 2.235                                   5.0x
      effect ratio  pooled / nA=0 = 2.767                                   7.7x

**27× was an arithmetic error, not rounding — (1.11/0.18)² = 38.** **I quoted 27× twice into this
record before it was checked**, which is the same failure as adopting the "identical to the current
template" line: a peer's number restated rather than derived. Corrected in D14, D16, and the
findings log.

**And the corrected form is stronger than the one my objection removed.** Written as
`(effect ratio)²`, **the swing never touches σ at all** — so it does not merely *survive* D11, it
is **outside D11's scope by construction**, as is the 6.18× effect ratio. The σ-free quantity was
available the whole time and is the better statement.

**The substantive point gets harder, not softer: ONE DESIGN PARAMETER MOVES REQUIRED SAMPLE SIZE BY
A FACTOR OF 38.** That is the argument for the mix being a declared choice carrying the ratio it
buys, rather than a value inherited from a generator tuned for a template we have retired.

## D18 — One addition to the tie check, adopted

RR's addition, and it closes the hole my own version left: **confirm the tie-break is deterministic
under a REORDERING OF THE SEGMENT LIST**, not merely that the tie rate is stable. Enumeration order
is the thing at risk, so **a stable rate measured under a single fixed order would look like a
pass.** The check is: tie rate six-class vs five-class, **and** identical optima under a permuted
segment list.

---

# Addendum 3 — the tie-break rule, and a clone limitation D14 did not anticipate

Input: RE's `records/L9/tie_rate.json` (d526d9e). **The required tie check blocked step 4**, which
is the check earning its keep.

## D19 — RE measured the right quantity, not the one I asked for

I asked for the exact-tie RATE. **Counting ties does not answer the question.** Ties in the TRUE
optimum are harmless — every tied allocation has the same value by definition. **The exposure is
entirely on the BELIEVED side:** allocations tied under the card are re-scored under truth, where
they are not tied, so the ceiling depends on which member `best()` happens to return — i.e. on
`product()`'s visit order.

                    tied optima   ceiling spread mean     max    ambiguous
    five_class         11.70            0.00%           0.00%      0/20
    six_class_clone    29.45            7.00%          14.10%     20/20

- **Five-class instances already carry ~12 tied optima and a ceiling spread of EXACTLY ZERO on
  20/20 seeds. Every figure reported so far, including 8.51%, is unaffected.** The check
  discriminates — null where ties are harmless, large where they are not, which is what makes the
  non-null credible.
- **With the clone the spread is 7.00% mean / 14.10% max — the same order as the entire 8.51%
  effect.** A size-3 ceiling would be substantially decided by enumeration order.

## D20 — Tie-break by EXPECTATION over the believed-optimal set, with [min, max] alongside

**RE's recommendation, adopted.** Under the card those allocations are *indistinguishable to the
manager*: it holds no information that separates them. **Any deterministic rule — first-visited,
best, worst — attributes to the manager a discrimination it cannot make.** Expectation is the only
point estimate consistent with the belief model the rest of this function already uses.

**And the interval is not decoration. Expectation is NOT an upper bound:** if the real manager
tie-breaks worse than chance the true ceiling is *higher* than the expectation figure. Min and max
are the bounds; the expectation is the central estimate. Reporting one without the other would
restate a range as a point.

**Safe for everything already published:** at five classes the spread is zero, so expectation and
current behaviour coincide exactly. **No existing number moves.**

**Rejected, as RE proposed rejecting it: perturbing the clone's economics to break the ties.** It
would work, and it would silently reintroduce the between-class bias D14 went to the trouble of
bracketing.

**★ A ceiling in this file must now declare THREE things, not two: its BASELINE, its BELIEF MODEL,
and its TIE-BREAK RULE.** Each was added after it silently decided a number. The rule generalises:
**wherever a reported quantity depends on a choice the code makes for us, the choice is named in
the function or the number is not reportable.**

## D21 — A clone limitation D14 did not anticipate, and it partly walks back D14

RE flags that **the tie rate is a consequence of the clone being EXACT — which is also what makes
it isolate the lattice. The clone's virtue and this hazard are the same property.**

The consequence for D14: **the clone environment carries a source of believed-indifference that a
real six-class environment would not have.** D14 recorded the clone's bias as *signable* — RR's
divergence argument said it most likely understates a real class. **That still holds for the
economics. It does not cover this second mechanism, whose sign I do not know**, and I am not going
to assert one from reasoning. **So D14's "signable" is narrowed: signable on economics, unsigned
overall.**

**A cheap diagnostic that would sign it, offered as OPTIONAL and explicitly NOT the instrument:**
price under a clone perturbed by a small ε purely to see which way the ceiling moves as ties
dissolve. **The exact clone stays the instrument** — the perturbation exists only to sign this
limitation, and would be reported as a diagnostic, never as a price. If it is expensive or
ambiguous, drop it and keep the limitation unsigned in the paper.

## D22 — Three instances of one defect: a field naming a source that did not produce the value

    D2   `"rule": "ceiling_vs_ignorant"` in the selection record   while the code ranked on stale card
    D3   `parameters.coverage_size` recorded the module constant   so a size-3 instance reported 2
    L6   (the original §B family)                                  population named, not predicated

**Three is a pattern, not a coincidence, and it is the same shape as the §B failures.** Provenance
fields are written once and then trusted forever, and nothing checks that the field still describes
what produced the value. **Candidate rule for `METHODOLOGY_RULES.md`: a provenance field is
asserted against its source at emission, or it is not written.** Raising for
`METHODOLOGY_RULES.md` rather than deciding it here.

---

# Addendum 4 — STEP 4 IS PRICED. My prediction failed on both axes

Input: RE's `records/L9/size3_pricing.json` (733359d).

    reference: size-2 disjoint, five classes
       nA=0  2.02%   nA=1  3.84%   nA=4  9.03%   pooled 4.30%

    size 3, six classes  (nA=1 in EVERY cell)
       clone      carriers   mean share   ratio to disjoint@nA=1
       corporate      1        1.89%          0.49x
       corporate      2        1.58%          0.41x
       mdb            1        1.84%          0.48x
       mdb            2        1.35%          0.35x

## D23 — Scoring the predictions, mine first

**LS: WRONG on both axes.** I predicted the two-carrier group **within a factor of 2 of disjoint**
and the single-carrier group **near zero**. Two-carrier came in at **0.35–0.41×** — below my band
against either disjoint comparator — and single-carrier at 1.84–1.89% is **not near zero and is
HIGHER than two-carrier.** **The level was wrong and the direction of the split was wrong.**
It was also, as recorded in D12, the one prediction loose enough to be hard to refute — and it
still failed.

**RE: directionally right, ~2× optimistic** (predicted ≈0.78, actual 0.35–0.41). **Their mechanism
was right** — size 3 spends exactly the coverage scarcity the channel is made of.

**RR: the only prediction the result confirms** (<0.5, pooled 2–5% of oracle).

**The clone bracket is narrow — 1.84 vs 1.89, 1.35 vs 1.58 — so the clone SOURCE is not where the
uncertainty lives**, which is what RR's within-vs-between-class variance predicted. **D14's
bracket was worth building and turned out not to matter**, which is the correct outcome for a
control.

## D24 — ★ THE TWO-CARRIER INVERSION IS UNEXPLAINED AND BLOCKS THE READING

**Two carriers price LOWER than one** (1.35–1.58% vs 1.84–1.89%) — **the opposite of what the
stratification predicts.** The second carrier IS the card's omission (D9); it should ADD effect.
That is the entire reason RR asked for the split and the entire reason D1 mattered. **Not a mix
confound: nA=1 in every cell of both groups.**

RE declined to theorise and handed it to RR, whose instrument it is. **I am adding two rival
hypotheses with discriminating observations, because "unexplained" should not sit in the record
without someone having tried:**

**H1 — CAPACITY SATURATION.** With two silent sole-held classes, more segments require the
successor. `cap = 3` binds, so **the ORACLE is already paying a capacity penalty**, and the gap
between oracle and card-believing play compresses. *Discriminating prediction:* ceiling share
falls as (segments needing the successor − cap) rises, and **the inversion weakens or reverses at
higher cap.**

**H2 — DENOMINATOR ARTEFACT.** Ceiling *share* divides by oracle. If two-carrier templates have a
larger oracle, the same absolute loss is a smaller share. *Discriminating prediction:* **the
inversion disappears when ABSOLUTE ceilings are compared instead of shares.**

**Falsifier for both:** absolute ceilings invert the same way AND raising cap does not remove it.

**H1 is the same capacity-displacement mechanism that was the story of the original card-channel
finding**, which makes it the one I would test first — and also the one I am most likely to
believe for bad reasons.

## D25 — 8.51% MOVES TO 9.03%, and RE's "D19 changes no reported number" was wrong

**Two sources of truth for one quantity, now visibly disagreeing.** `check_template_pricing`
computes the ceiling with its **own local enumeration** instead of calling the shipped scorer, so
it never saw D19's tie-break. The claim held for the natural five-class template (0.00% spread on
20/20, which is what the tie check measured) and **not for the SUBSTITUTED disjoint template, which
was never tested.** RE's own diagnosis: *generalised from the population in front of me* — the same
shape as the belief-model fault they found.

**Approved: the local copy delegates to the shipped scorer.** **8.51% has been quoted heavily —
including in D1's acceptance, D5's realism table, RR's realism probe and both ledgers — and it
becomes 9.03%.** The correction sweep is part of the delegation change, not a follow-up.

## D26 — The open question that decides whether the comparison is FAIR

RE reports **nA=1 in every size-3 cell, "no forcing is available there."** **It matters a great
deal whether that is a fact about six classes or a fact about the current generator.** 9 segments
over 6 classes averages 1.5 per class, but nothing obviously prevents forcing 4 segments into one
class — `shared_class_segments = 4` did exactly that at five.

- If forcing is **impossible** at six classes, the comparison is fair and size-3 is simply weaker.
- If forcing is **merely not implemented**, then we have compared **disjoint across its whole mix
  range against size-3 at one point of its own**, and the honest comparison has not been made.

**No reading of this result ships until that is settled.** It is the difference between "partial
overlap costs half the channel" and "partial overlap costs half the channel at the one mix we
happened to price."

---

# Addendum 5 — the inversion is located, the clone is exonerated, and I sized the band myself

Inputs: RE's carrier-structure proof; RR's `records/L9/clone_indifference_RR.md`.

## D27 — H3 was right: the "carrier count" label asserts a decomposition the design cannot support

RE proved exhaustively over all 6,480 admissible templates, **0 counterexamples**:

    carrier count = 1  <=>  the successor-unique class IS the shared class
    carrier count = 2  <=>  the successor-unique class is one the card never mentions

**And it is forced**, not sampled: the successor-unique class lies in `w1` by definition; if it is
also in `w0` it lies in `w0 ∩ w1`, which every admissible partial template has of size exactly 1 —
so it *is* the shared class. **No sampling design can separate the two properties because they are
the same property.**

**So of my three rivals, H3 is the one that lands** — the labels do not mean what their name says.
**H1 and H2 are not dead**, but they were asked about a variable that does not exist as stated.

**The contrast is renamed rather than kept:** *does the card NAME the class the successor is
uniquely required for, or is it SILENT about it?* **RE cleared their own sampling first** — the
12+12 samples match 12/12 on overlap size, post-swap coverage breadth, uncovered-post-swap count,
lied-class count and incumbent overlap. The only structural difference is the one above.

**It also makes RR's original characterisation provable rather than descriptive:** "the
single-carrier group has the current template's structure" is exactly what single-carrier now
means.

**The inversion is LOCATED, not EXPLAINED**, and it is more counterintuitive after renaming, not
less: **the case where the card CORRECTLY names the critical class prices HIGHER.** Both groups
carry the same number of false claims (2), so "more card error" is not it. RE's capacity guess —
not routing the omitted class to the successor frees its slots for classes it genuinely covers —
is H1 in the new vocabulary, and is flagged as a guess.

## D28 — The clone is EXONERATED, and my ε-diagnostic is inert. D14 is re-pointed, not narrowed

RR measured it instead of arguing it, and **the premise I accepted was wrong: coverage size 3
manufactures the indifference, not the clone.**

    size 2, 5 classes (shipped)     spread  0.00%   0/10 ambiguous
    size 3, 5 classes, NO CLONE     spread  3.94%  10/10 ambiguous
    size 3, 6 classes with CLONE    spread  7.36%  10/10 ambiguous

**No clone anywhere in the middle arm.** And perturbing the sixth class's SA table by ±20% leaves
the tie set unchanged at 30.00 — **with a live-knob control** (a 50% perturbation does move an SA
number), so the invariance is a result and not a dead parameter.

- **My ε-perturbation diagnostic is not confounded — it is INERT.** It can never break the
  degeneracy, so there is no unique perturbed ceiling to compare against. **RE is told not to spend
  on it.** That is a better answer than the one I asked for.
- **D21 is WRONG as written and is corrected here: "virtue and hazard are the same property" is
  not what is happening.** The hazard is not a property of the clone at all. **D14 returns to
  signable-and-bounded on economics** (factor 1.5, cannot flip a 6–16× ranking), and nothing about
  the tie ambiguity argues against clone pricing specifically.
- **★ THE CONSEQUENCE THAT OUTLASTS THE DECISION: the tie-break is PERMANENT, not scaffolding.**
  I adopted expectation-plus-interval as a fix for a clone artefact. **It is not one — any size-3
  design has this, including a real transcribed sixth class. So D19 ships with the study.**
- **RR's own stated limitation, which bounds their claim:** their five-class size-3 template puts
  `sovereign` in all four workers (102 tied optima vs the clone arm's 30), so **the 2× amplification
  3.94% → 7.36% cannot be attributed to the clone rather than to lattice structure.** What survives
  is what the conclusion rests on: size 3 alone suffices, and the δ-sweep independently rules out
  exactness.

## D29 — I sized the ambiguity band against the actual gaps, and it does not threaten the headline

RR reports the size-3 band as *"about the size of the effects at stake"*. **The caution is right in
kind; the magnitude needs stating, so I computed it rather than repeating the phrase.**

**The spread is RELATIVE to the ceiling — 7.00% mean, 14.10% max — not percentage points of
oracle.** (A 14-point absolute spread on a ceiling of ~1.5 points is impossible; the units settle
it.) Applied to the step-4 ratios, **conservatively treating the per-instance band as if it applied
undiminished to a group mean:**

    contrast                          gap      band(mean)   band(max)   separated?
    size-3 vs disjoint@nA=1          2.44x      +/-0.03      +/-0.07    yes, overwhelmingly
    within size-3, named vs silent   1.365x     +/-0.03      +/-0.07    yes, MARGINALLY at max
                                     (mdb 0.478 vs 0.350; max-band intervals 0.411 vs 0.399)

**So: the band does NOT threaten the headline** — 7% relative against a 2.44× gap. **It does bear
on the within-size-3 inversion, which separates only marginally at the max band**, and it would
threaten any finer discrimination. **RR's caveat stands exactly where they aimed it — at a
near-threshold call — and the headline is not near threshold.**

**The band is nonetheless a REAL and previously unaccounted COST of size 3**, and RR is right that
it is ambiguity about *what the ceiling is* — an offline design quantity — rather than extra noise
in what a run would measure.

## D30 — Two methodology rules landed, both sharpened past what I proposed

RR's addition to the provenance rule is what earns it a rule: **a wrong VALUE is caught because it
has a plausible range and people examine it; a wrong PROVENANCE FIELD is caught only by re-deriving
the value from scratch — the exact work the field exists to save.** Highest-trust, lowest-checked
content in any record. **Where it cannot be derived or asserted, omit it: a missing field sends the
reader to the code, a wrong one stops them looking.**

The verdict rule gains an actionable corollary: **a reduction over an empty or all-`None`
collection must never render as an ordinary verdict** — `all([])` is `True`, `any([])` is `False`,
and both are lies about a measurement that did not happen.

## D31 — D26 IS NOW THE SOLE OUTSTANDING BLOCKER ON L9

**Neither peer has answered it, and it decides whether the comparison is fair:** is `nA=1` in every
size-3 cell a fact about **six classes** or a fact about the **current generator**? Everything else
on L9 is resolved.

---

# Addendum 6 — both hypotheses falsified; the mechanism found; blocker 2 resolves against us

Input: RE's `records/L9/inversion_diagnosis.json`.

## D32 — H1 and H2 both die by the falsifiers I specified, and the mechanism is H1's MIRROR

**H2 (denominator) dead:** absolute ceilings invert identically (corporate 0.1678 → 0.1419); oracles
differ by **0.8%** against a ceiling gap of 15–26%.

**H1 (capacity saturation) dead by its own falsifier:** the inversion persists at **cap = 9**, which
is no constraint at all on 9 segments over 3 workers.

**But the cap sweep found the mechanism, and it is H1 pointed the other way. Capacity is not
compressing the two-carrier group — it is AMPLIFYING the one-carrier group:**

    corporate   1 carrier   1.89% -> 2.10% -> 2.21% -> 2.22%    (cap 3, 4, 5, 9)
                2 carriers  1.58% -> 1.58% -> 1.58% -> 1.58%
    mdb         1 carrier   1.84% -> 2.03% -> 2.13% -> 2.15%
                2 carriers  1.35% -> 1.35% -> 1.35% -> 1.35%

**Two carriers is EXACTLY flat in cap.** One carrier = the card names the critical class correctly,
so the manager believes the successor serves three classes and piles segments onto it up to cap —
**two of those claims false, and the loss scales with cap.** Two carriers = the successor's required
class is one the card never mentions; that loss is the un-routed omitted class, **one segment at
nA=1, capacity-independent.**

**My declared bias was well placed and still cost me nothing only because the falsifier was
specified in advance.** I said H1 was the one I was most likely to believe for bad reasons.
**H1 as stated is false — and capacity-displacement is nevertheless the live mechanism, acting on
the other group.** Being right about the ingredient and wrong about the direction is exactly what a
pre-committed falsifier is for.

## D33 — ★ BLOCKER 2 (D26) RESOLVES AGAINST US: `nA=1` is a fact about the GENERATOR

    shared_class = _template_shared_class(chosen) if coverage_override is None else None

**Mix forcing is switched off on the `coverage_override` path — the only path that can generate six
classes.** `shared_class_segments` is simply ignored there. **Nothing about six classes forbids
nA=4; it has never been reachable.**

**So the second branch of D26 is the true one.** The matched-cell ratio (0.35–0.49× at nA=1) is a
fair cell-to-cell comparison and **stands**. What does **not** stand is any statement of the form
*"size 3 is weaker"* — that is established **only at nA=1**, and we compared disjoint across its
whole mix range against size-3 at a single point of its own.

## D34 — The mechanism makes a prediction that ties both blockers into ONE measurement

**The omission cost scales with nA; the lie's capacity amplification does not. So the inversion
should REVERSE at higher nA** — and the regime that tests the inversion is the same regime that
tests fairness. **Forced mix at six classes answers both.**

**APPROVED: implement mix forcing on the override path.** Small, offline, no model spend, and it
converts two open questions into one measurement. **If the inversion reverses at nA=4, the carrier
reading flips and so does the partial-overlap verdict** — which is precisely why it must run before
anything goes to the researcher.

**PREDICTION PROTOCOL APPLIES — this could flip a design decision, which is the case the rule exists
for.** RE's is already on record (the inversion reverses). **Mine, committed here before the
result:**

> **At nA=4 the inversion reverses decisively. The two-carrier (card-silent) group rises at least
> 3× its nA=1 value, because its loss is the un-routed omitted class and that scales ~linearly in
> nA. The one-carrier (card-names) group rises by less than 1.5×, and may FALL — at nA=4 more
> segments sit in the correctly-named class, so fewer remain in the falsely-claimed classes that
> generate its loss. Consequently size-3-at-nA=4 vs disjoint-at-nA=4 comes in materially above the
> 0.49 ceiling of the nA=1 comparison — I will say ≥ 0.7.**

**Falsifier:** two-carrier rises less than 2×, or the ordering does not reverse. RR's to be
requested privately before the result.

## D35 — ★ A REALISM QUESTION THAT FORCING RE-OPENS, and it is the one this whole step is about

**Forcing the mix at six classes is us deliberately choosing the favourable value of the parameter
we criticised for being silently inherited.** That is legitimate **only if declared and defended**,
and it re-opens exactly the axis partial overlap was chosen for: **is a portfolio with 4 of 9
segments concentrated in one asset class realistic?**

Real Basel portfolios *are* concentrated, so the answer is plausibly yes — **but it must be argued
rather than assumed, and it is a lattice-realism question, which is RR's.** **If the size-3 verdict
ends up resting on nA=4, the realism of nA=4 is load-bearing and goes to the researcher with the
number, not after it.**

---

# Addendum 7 — the zero best case, a peer contradiction, and the ratio suspended

Input: RR's `records/L9/step4_audit_RR.md`. **Two blockers, and one reframing that is mine.**

## D36 — The zero best-case is REAL and IMPORTANT. Its stated reading OVERSTATES it

RR: under the best-case tie-break the size-3 ceiling is **exactly 0.00%** on every sampled instance,
in both groups — the believed-optimal tie set **always contains an allocation that is also
truth-optimal**.

**The structural fact is real and I had not seen it. The reading — *"a manager believing the stale
card can reach the true optimum knowing nothing, provided it breaks ties favourably"* — overstates
it, because the proviso requires exactly the information under study.** Breaking ties favourably
means selecting, among allocations indistinguishable under the card, the one that is best under
truth. **That is the discrimination D19 says the manager cannot make; it is the bound, not a
scenario a card-believing manager can occupy.**

**The correct reading, and it is a genuine qualitative difference between the designs:**

- **At size 3 the stale card never RULES OUT the true optimum.** The manager is never *forced* into
  a worse allocation — it simply cannot tell which member of the tie set is right. **The whole
  effect is failure-to-discriminate.**
- **At size 2 the spread is 0.00% and the ceiling is one well-defined number**, so the card can
  force a genuinely worse allocation. **The manipulation excludes rather than merely fails to
  guide.**

**That distinction should be in the paper whichever template wins**, and it is a better
characterisation of what the four channels do than anything the ceiling arc has produced so far.

## D37 — ★ MY REFRAMING: the 0.35–0.49× ratio UNDERSTATES size-3's cost

**Required n scales with (effect/σ)², and size 3 adds a σ that size 2 does not have.** The
tie-break dispersion — best 0.00%, expectation ~2.2–2.4%, worst ~5.0–5.1% — is **variance in the
dependent variable driven by something other than the manipulation**, and the shipped size-2
lattice has *none* of it (0.00% spread, 20/20).

**So size 3 is worse than 0.35–0.49× on the quantity that actually decides affordability.** The
ratio compares means; the decision needs means *and* the noise they sit in. **Neither RE's pricing
nor my reading of it accounted for this, and it moves the comparison further against the option I
and the researcher both prefer.**

**This is not a reason to drop size 3** — the added variance is bounded and quantified, and D19's
interval already carries it. **It is a reason the interval must travel with every size-3 number and
must not be summarised away.**

## D38 — ★ THE TWO PEERS CONTRADICT EACH OTHER ON THE SAME QUANTITY UNDER THE SAME RULE

    RE, expectation tie-break:   card-silent LOWER  (1.35-1.58% vs 1.84-1.89%)   inverted
    RR, expectation tie-break:   card-silent HIGHER (2.43% vs 2.17%)             not inverted

And RR's four-rule table shows **the inversion appears under exactly one rule — worst-case — and
not under D19's expectation nor under bare visit order.**

**So there may be no stable inversion at all, and I have spent two addenda hypothesising about it.**
H1 and H2 were falsified against RE's sample; **if the phenomenon is sample- or rule-dependent,
they were falsified against something that may not exist.**

**Neither peer is claiming the other has a bug, and I am not going to adjudicate by preference.**
RR's sample is 6 templates/group × 5 seeds; RE's is 12+12. **The resolution is mechanical: both
implementations, the SAME templates and the SAME seeds, under D19.** Whoever runs it, the other
reproduces. Until then **the inversion is not a finding and is not reported as one.**

## D39 — The matched-cell ratio is SUSPENDED, not withdrawn — RR is right that nA does not repair it

RE held that the 0.35–0.49× matched-cell ratio survives the forcing defect. **RR's objection is
stronger and I am upholding it: the `coverage_override` path disables BOTH mix amplifiers**, not
just `shared_class_segments` — the divergence-selection branch never fires either. **So even at
matched nA=1 the five-class arm carries an amplifier the six-class arm does not.**

RR's demonstration is better evidence than either code-read: **the same lattice, seed 0's own
natural template handed back through the override path, prices 0.00% against 3.50%.**

**Ruling: the ratio is SUSPENDED pending one test — five-class at nA=1 with divergence selection
OFF.** If that moves the number, the ratio was never matched and must be re-derived. If it does
not, RE's position stands and the ratio is restored. **Cheap, decisive, and it settles a
disagreement between peers rather than my opinion of it.**

## D40 — Order of operations, adopted from RR

    1. fix the forcing defect (derive the shared class for a partial override; `w0 ∩ w1` is size 1,
       so it is unique -- handle the empty case for disjoint rather than disabling the parameter
       for every override)
    2. re-price BOTH arms with the amplifiers on for each
    3. reconcile RE and RR on ONE shared sample under D19
    4. only THEN ask whether the inversion exists

**All three predictions are now committed** (LS, RE, RR — all predict reversal at nA=4, differing
on magnitude). **Under my own rule I would ask what a confirmatory measurement adds. The answer
here is unusually good: it is no longer a prediction test. It must settle a contradiction between
two peers and a suspended ratio, and RR does not even reproduce the baseline the reversal would
reverse from.**

**RR declared a bias unprompted and against their own ranking** — the zero-best-case cuts against
the option they ranked first, and they found it while testing my H2 rather than while defending
their position. **That is the second declared-bias-then-scored on the record this phase.**

---

# Addendum 8 — the six-class figures are INVALID; two rulings before re-pricing

Inputs: RE's round-trip test; RR's `records/L9/nA4_realism_RR.md`.

## D41 — ★ THE DEBT LIST PREDICTED THIS FAILURE, NAMED ITS TRIGGER, AND WE BUILT ON IT ANYWAY

`RESEARCH-CRON-STATUS.md` §5, written before any six-class work:

> **`_designate_swap_pair` is a second source of truth** for roles the template already declares.
> It agrees today only by construction. **It must be retired if the lattice changes.**

**We changed the lattice. It was not retired. `coverage_override` routed to it, and it SEARCHES for
a two-holder class instead of reading declared positions:**

    natural    pred=w0, succ=w1, shared=retail       ceiling 0.00%
    override   pred=w1, succ=w2, shared=corporate    ceiling 7.08%

**Same lattice, different roles.** Every L9 size-3 template declares roles positionally and the
carrier stratification is DEFINED on those positions — so **the templates being priced were not the
templates being described**, and nA was measured against the wrong class.

**This is the failure the record predicted, under the condition the record named, and nobody
re-read the record when the condition fired.** The warning cost nothing to write and everything to
ignore.

**RULE, and I would like it in `METHODOLOGY_RULES.md`: when a step changes a thing the technical-debt
list conditions on, the debt list is re-read as part of that step.** A conditional warning with no
trigger attached is a warning that fires after the damage.

**INVALIDATED pending re-run:** the step-4 table, the carrier means, the inversion, the cap sweep,
the forced-mix sweep, and the D26 forcing result.
**SURVIVES:** the carrier confound proof (pure enumeration, touches no instance), the belief-model
fix and its acceptance, the tie-break, and **everything five-class** — the natural path never
entered that function.

**And this likely DISSOLVES D38 rather than resolving it.** If RR assigns roles positionally and RE
did not, that alone explains card-silent low for one and high for the other under the same
tie-break. **The inversion may never have needed H1 or H2 — it may be an artefact of role
assignment, which is the possibility I raised as H3 and then did not press.**

**RE's own note is the one worth keeping: the function they had written up in `records/L9` as "dead
code, not on the template path" was true of the template path and false of the override path — the
one they then built every six-class figure on. The correction they wrote for that record is the
source of the error.**

## D42 — RULING 1: ALIGN THE RNG STREAM. The re-run is PAIRED

`rng.shuffle` consumes the stream on the natural path and not the override path, so the arms differ
by more than the lattice.

**Align it — consume identical draws on both paths, discarding where unused.** This is common
random numbers, not tuning: it makes the two arms differ in **the lattice and nothing else**, which
is the contrast the substitution method exists to produce. Distributional comparison would confound
lattice with instance draw and cost precision we do not have to spare.

**And assert it rather than assume it: the two paths must consume identical draws up to the lattice
choice, checked at generation.** This is the third silent divergence between those paths (forcing,
roles, RNG); the next one should raise instead of being discovered.

## D43 — RULING 2: SURVIVORSHIP IS CHARACTERISED, NOT REPORTED

**28 of 60 seeds fail generation on the override path and none on the natural path.** That is a
filter on one arm only, and RE has already seen evidence it is not benign — the forced-mix
survivors had *higher* unforced ceilings than the full population (2.68% vs 1.89%).

**The paired design solves the comparison and the natural arm solves the diagnosis:**

1. **Compare on the INTERSECTION** — seeds that generate under both arms — paired, and state the
   count dropped.
2. **Test whether the dropped seeds differ**, using the arm where they ARE measurable: compare
   natural-path ceilings on the 28 failing seeds against the 32 surviving ones. **If they do not
   differ, survivorship is benign and says so. If they do, every six-class figure is conditional on
   a biased subpopulation and must carry that.**
3. **Say what assertion fails and why**, not just how many. Nearly half is a design fact about the
   six-class generator, not a nuisance.

**D40's test (five-class at nA=1, divergence selection off) runs AFTER the re-price, on positional
roles, as RE proposes.** Its five-class half is unaffected by this fault; the comparison is not.

## D44 — RR's realism analysis SURVIVES the invalidation, and it is the strongest result of the day

It rests on the natural five-class path, which never entered the faulty function.

**RR grants my prior and then refuses the inference, which is the right shape:** 44% of a book in
one class is ordinary — Basel's Pillar 2 concentration framework exists because it is the norm.
**But the design does not need "books are concentrated"; it needs the book concentrated IN THE CLASS
WHERE THE STAFFING CHANGE BITES, and those are different propositions.**

**The alignment is anti-realistic and its sign is knowable: STAFFING FOLLOWS VOLUME.** A dominant
exposure is the *best*-covered, because that is where the work is; sole coverage attaches to
**specialist niches**, where one approved reviewer is normal precisely because volume does not
justify two. **Concentration and thin coverage are negatively correlated in practice; the design
requires them maximally positively correlated.** nA=4 is the configuration in which the bank's
dominant business line has one qualified person.

**So the realistic nA is 1** — what the unforced generator produces — and the succession we claim to
study is losing the sole holder of a *niche* capability.

**And the amplification is THREE knobs, not one** (RE's count, confirming RR's two): segment count,
divergence selection on that class's ratings, **and IRB-approval priority**. All gated on
`shared_class`. **"4 of 9 segments in one class" understates what is being chosen — the ratings
inside the concentrated class are selected adversarially and its segments are approved for IRB
first.**

**THE CONSEQUENCE THAT MATTERS, AND IT IS NOT AN ARGUMENT BETWEEN THE OPTIONS:**

    disjoint, nA=4 (forced)     0.0851 of oracle   1.11 sigma   ~13 episodes/arm
    disjoint, nA=1 (realistic)  0.0347 of oracle   0.45 sigma   ~64 episodes/arm

**Realism costs the DISJOINT template 2.4× in effect and ~6× in n — the same mechanism and
magnitude it costs size 3. This is a condition on a headline the two options SHARE.** "13 episodes
per arm" is a statement about a book whose dominant business line has one qualified reviewer.

**ADOPTED: nA=1 is PRIMARY and nA=4 is a DECLARED UPPER BOUND, not the reverse. All three
amplifiers are declared whenever a forced figure is quoted.**

**RR's new lever, which nobody had considered and which I am asking to be priced: buy detectability
with BOOK SIZE rather than CONCENTRATION.** The effect as a share of oracle is scale-invariant while
the allocation component of σ falls as ~1/√n, so a larger book at a realistic niche concentration
gains detectability **without touching the mix.** RR bounds it themselves: only the allocation
component shrinks (~0.041 of a published 0.0768), so the gain is real but **sub-√n**, and bigger
books cost episode length and a more expensive exact DP. **That is the first proposal this phase
that buys sensitivity without spending realism, and it deserves a price of its own.**

**Where RR says to attack them, and they are right that it is the load-bearing step:** *"staffing
follows volume, so sole coverage attaches to niches"* is a judgement about how institutions staff,
not a measurement. **I hold it too, and it is the one claim here that would go to the researcher as
a judgement rather than a finding.**

---

# Addendum 9 — the inversion dissolves; the headline moves; and the new table has a hole where its claim lives

Input: RE's re-price after the four path divergences were closed.

## D45 — Four divergences, all the same defect, and the pattern deserves a name

All four were **`if coverage_override is None` guards on logic that has nothing to do with where
the lattice came from**: mix forcing, role assignment, the RNG label draw, and — the fourth —
**the TOTALITY REPAIR (sole-class rating re-draw)**.

**RULING 2 DISSOLVES rather than needing its diagnosis.** The 28-of-60 survivorship filter was not a
design fact about six classes; **it was a repair switched off for every instance six classes can be
built from.** Round-trip goes 32/60 with 6 of 10 ceilings mismatching → **60/60 with zero divergent
fields**; paired exclusion 6/240 → 1/240.

**The defect class, stated generally so the next one is recognisable: a guard keyed on the
PROVENANCE of an input, applied to logic that does not depend on provenance.** Where the lattice
came from should never determine whether a repair runs.

**Two process points, both RE's and both adopted:** the checkpoint is read from `getstate()` rather
than by drawing a probe — **a probe would advance the stream and silently move every five-class
figure already reported, making the alignment check the cause of the next divergence.** And
`check_path_alignment.py` now exists, **so a fifth divergence fails a check instead of being found
while fixing the fourth.** RE's own note: all four would have been caught by a round-trip test
written when `coverage_override` was first used to produce a number. **Rule: when an input path is
first used to produce a REPORTED number, round-trip it.**

## D46 — ★ THE INVERSION IS NOT A PHENOMENON. It was the mix, and it followed from the confound already proved

**The amplifier forces the SHARED class. For carrier-1 templates the shared class IS the
successor-unique class, so nA=4 automatically; for carrier-2 templates it is not, so nA stays 0 or
1.** The two groups **never shared a mix** — the raw group means were comparing nA=4 against nA≤1
with a carrier label on top.

**So H1 and H2 were falsified against something that did not exist**, exactly as D38 suspected, and
**H3 — the labels do not mean what their name says — accounts for the whole of it.** The carrier
confound RE proved by enumeration and the inversion turn out to be one fact, not two.

## D47 — ★ BUT THE NEW TABLE DOES NOT SUPPORT ITS OWN ORDERING CLAIM. Same confound, one level up

    ratio to size-2 disjoint AT MATCHED MIX
       carriers=1  @ nA=4    0.18x
       carriers=2  @ nA=1    0.72x
       carriers=2  @ nA=0    0.55x

RE reads this as *"normalised at the same mix the ordering REVERSES — card-silent 0.72× against
card-names 0.18×."* **It does not establish that, and the reason is the reason the first inversion
was wrong.**

**"Matched mix" here matches each size-3 cell to DISJOINT at the same nA. It does not match the two
CARRIER GROUPS to each other — 0.72× is at nA=1 and 0.18× is at nA=4.** Dividing by disjoint@nA
would neutralise the mix only if the nA-response were a common multiplicative factor. **It
demonstrably is not: RE measured forcing HALVING size-3 while roughly TRIPLING disjoint**
(0.0347 → 0.0851). So the ratio is strongly nA-dependent and comparing across different nA
**re-introduces the confound at the level of the correction.**

**RULING: no ordering claim between the carrier groups until both are measured AT THE SAME nA.**
The missing cell is **carriers=1 @ nA=1**, which is reachable — force a non-shared class, or leave
unforced. **The three-row table has a hole exactly where its conclusion lives.**

## D48 — The headline is REAL and MISSTATED. It is a carrier-2 figure, not a size-3 figure

**0.72× at nA=1 is `carriers=2 @ nA=1` alone.** Size-3 as a design is **2,160 carrier-1 templates
and 4,320 carrier-2** — so a pooled figure is a weighted mix, and **if carrier-1 at nA=1 is much
lower the pool sits well below 0.72×.**

**So the correct statement today is: *at the realistic mix, the card-silent half of the size-3
design reaches 0.72× the disjoint channel.* Not *"size-3 reaches 0.72×."*** The direction of the
news is genuinely good and moves toward the option the researcher and I prefer — **the trade-off
may be a quarter of the channel rather than two-thirds — but the number that would say so does not
exist yet.**

**This is the third time this phase a group mean has been quoted as a design property.** It is the
same error each time and it is now cheap to avoid: **name the subpopulation in the sentence.**

## D49 — Predictions: none cleanly confirmed, and mine is refuted

**LS: REFUTED.** I predicted size-3-at-nA=4 vs disjoint-at-nA=4 ≥ 0.7. **That cell is 0.18×** — off
by a factor of four, and in the direction that mattered.

**RE:** ≈0.78 lands near 0.72, but they decline to claim it, correctly: predicted for the wrong
mechanism, with an intervening "refuted" verdict computed on void figures.
**RR:** <0.5 holds at nA=4 and fails at nA=1.

**Adopted: this is not reported as a prediction test.** The measurement's value was settling a
contradiction and an invalidation, which it did.

## D50 — D40 runs before anything goes to the researcher

**Yes.** Five-class at nA=1 with divergence selection off, on positional roles and aligned streams.
It is cheap and it is the last thing between us and a matched-cell ratio anyone can defend.
**Order: D47's missing cell, then D40, then the package.**

---

# Addendum 10 — the book-size lever, priced down by its proposer; and D47 unblocks

Input: RR's `records/L9/booksize_lever_RR.md`.

## D51 — ★ THE DP COST DOES NOT BIND, AND THAT SURVIVES UNCONDITIONALLY

The capacitated optimum is a **transportation problem**, so with three workers it is an exact DP
over `(used_0, used_1)` in **O(n·cap²)**. Positive-controlled against the shipped 1,680-allocation
enumeration on 10 seeds × both belief models: **max difference 1.78e-15.**

**72 segments cost the same as 9. The enumeration has been read as a mathematical limit on book
size and it is an implementation choice.** That is worth more than the lever it was measured for:
**book size is not compute-bounded anywhere in this study**, and any future design that wanted a
bigger book was never actually blocked.

## D52 — The lever is priced DOWN by the peer who proposed it, and the gain may be ZERO

    k  segments  ceiling share  sd_alloc/oracle
    1         9         8.56%          0.0384
    8        72         7.61%          0.0125     x0.33 vs 1/sqrt(8)=0.354

**Effect share is scale-invariant and `sd_alloc` falls as ~1/√k — both exactly as predicted. And it
does not matter, because the allocation component is only 25% of the variance:**

    sigma_total (published)  0.0768      sigma_alloc (measured)  0.0384
    sigma_manager (residual) 0.0665   <- 75% of the VARIANCE

    8x book, manager variance PER-EPISODE   -> detectability x1.01, n/arm x0.98   (NO GAIN)
    8x book, manager variance PER-DECISION  -> detectability x2.56, n/arm x0.15

**RR corrects their own earlier "real but sub-√n" to "may be zero", and names the error precisely:
they pitched the lever on the component they could measure without weighting it against the one
they could not.** That is the same shape as the episode-count error I corrected them on, arriving
from the other direction — **and this time they caught it themselves, on their own proposal.**

**THE CATCH-22, worth naming because it recurs: pricing this lever properly requires the
measurement it exists to make affordable.** Separating per-decision from per-episode manager
variance needs σ at two book sizes, which needs runs. **The corpus cannot settle it** — all 18
bundles are 9-segment and 3 seeds × 6 cells is far too thin to decompose variance.

**ADOPTED: the lever does NOT change the option set on present evidence.** It is an open question
with a cheap test attached, not the realism-preserving win it was proposed as.

**STANDING RIDER: if any run is authorised, add ONE cell at 2× book size.** At k=2 the bounds are
already 1.08 vs 1.43, so a single cell discriminates. **This converts a blocked question into a
rider on work being done anyway**, and it goes to the researcher as part of the run package rather
than as a separate ask.

## D53 — ★ D47 UNBLOCKS: force on the SUCCESSOR-UNIQUE class, not the SHARED class

RR settled RE's question and it dissolves my missing-cell problem.

**Verified 20/20 seeds: in `_lattice_from_template` the shared class IS the successor-unique class
post-swap** — `w1` sole-holds A once `w0` leaves, by construction. **So `"shared_class"` is a name
that merely COINCIDES with "successor-unique" in that one template.**

**Consequence: targeting the successor-unique class directly is not a departure from what the
five-class arm does — it is what the five-class arm ALREADY does, matched by mechanism instead of
by label.** And it **breaks the carrier/nA lock without introducing a new asymmetry**: nA becomes
settable independently of carrier group, so **`carriers=1 @ nA=1` becomes reachable and D47's
missing cell can be measured.**

**ADOPTED: forcing targets the successor-unique class.** This is a case where matching the *name*
across arms would have been the error and matching the *mechanism* is correct.

## D54 — RR's amendment to the debt-list rule is better than mine

My version: *when a step changes something the debt list conditions on, the debt list is re-read as
part of that step.* **RR's objection: the trigger has to be MECHANICAL, or it is the same class of
rule as "run a positive control" — it fires only when someone remembers.**

**Their version, adopted: the debt entry names its CONDITION in a form a step can CHECK, so the
step re-reads it because the condition is written down, not because someone recalls writing it.**

**This is exactly the failure that voided the six-class figures.** §5 said *"must be retired if the
lattice changes"* — a correct condition, in prose, checkable by nobody. **The rule that would have
saved it is the rule that makes the condition executable.**

---

# Addendum 11 — the matched-cell ratio EXISTS; and a ruling: rebuild the six-class path BEFORE the package

Input: RE's `amplify_mix=False` re-price and regenerated reference (L9-aa/ab/ac).

## D55 — The ratio, at genuinely matched mix, on one path

    MATCHED-CELL RATIO -- one path, nA=1, unamplified throughout
       disjoint size-2 @ nA=1              4.76%
       size-3 carriers=1 (card NAMES)      1.31%    0.28x
       size-3 carriers=2 (card SILENT)     4.24%    0.89x
       size-3 POOLED (4320:2160)           3.26%    0.69x

**At matched mix the ordering is card-SILENT 3.2× card-NAMES, which is RR's direction.** The
inversion was **entirely the mix**, and the mechanism is clean: **amplifying pulls segments INTO
the shared class, which for carrier-2 is NOT the successor-unique one — draining nA from 1 to 0 in
103 of 119 cells. The amplifier actively HARMS the group whose value lies in the omission.**

**`amplify_mix=False` is deliberate and SYMMETRIC absence, which is a different thing from the
silent asymmetry it replaces.** And RE matched the reference too rather than repeating the error one
level up — the old 3.84% came from substitution onto instances amplified on the *five-class*
template's shared class; regenerated through the same path it is **4.76%**.

**Free consistency check: amplified and unamplified are IDENTICAL for the disjoint template,
because it has no shared class for the amplifier to act on.**

**The sentence I would defend, subpopulation named as required: *at the realistic mix the
card-silent half of the size-3 design reaches 0.89× the disjoint channel; size-3 as a whole reaches
0.69×.*** **This supersedes both 0.72× and 0.35–0.49×.** My expectation that carrier-1 would drag
the pool down holds — it sits at 0.28×.

**One §B flag on RE's own message: the disjoint reference appears as 4.76% and as 5.03% in the same
message**, presumably nA=1 versus all-cells. **Two values for one named quantity in one message is
what §B exists for; the package states which population each belongs to or quotes neither.**

## D56 — ★ RULING: REBUILD THE SIX-CLASS PATH BEFORE THE PACKAGE, NOT AFTER

**RR's challenge is correct and my approval of `check_path_alignment` did not see it: a parity
check that can only run where a natural counterpart EXISTS cannot certify the case that has NO
counterpart.** It proves parity for five-class lattices. **It cannot test a six-class lattice at
all** — there is no natural six-class path to compare against. **The blind spot is exactly where the
risk is.**

And the base rate is not reassuring: **this path is documented as *"never used by study
instances"* — an S5 negative-case fixture — and it has already produced FOUR silent divergences.
Four found is not evidence the list is complete.**

**RULING: BEFORE.** Extend `ASSET_CLASSES` and build the six-class lattice through
`_lattice_from_template` the way the five-class one is built, **so every mechanism applies by
default and nothing has to be remembered.**

**Why before, and it is the same argument this whole phase has been making:** we would be handing
the researcher a decision **that costs a sixth asset class**, resting on a code path that is
documented as not for study use, has leaked four mechanisms, and **cannot be checked for a fifth by
the acceptance we have.** *"Do not build on an unverified instrument"* is the rule this phase exists
to enforce; sending the package first would break it at the last step.

**It is cheaper than it looks, and it carries its own test:**
- **The five-class figures are untouched** — they never used the override path. The stable half is
  not at risk.
- **It removes the `rng.shuffle` asymmetry STRUCTURALLY** rather than by the discard patch, which is
  a guard I would otherwise have to trust.
- **It makes `check_path_alignment` MEANINGFUL for six classes**, because the natural path becomes
  the six-class path.
- **And the re-price is the acceptance: it either reproduces 0.69× / 0.89× or it does not.** Either
  outcome is worth having before the researcher commits.

**What I am NOT asking for: re-deriving everything.** The rebuild is the generator path; the
decisions, the belief model, the tie-break, the realism analysis and the enumeration all stand.

## D57 — D40 may already be answered; one question settles it

RE notes the disjoint reference being identical amplified and unamplified is D40's question from
one side. **It is not the same question — D40 asks about the FIVE-CLASS natural template, which
DOES have a shared class for divergence selection to act on.** But it may be answered anyway:

**Does `amplify_mix=False` disable ALL THREE amplifiers (segment count, divergence selection, IRB
approval priority) or only the count?**

- **All three** → the 4.76% reference IS the divergence-selection-off number, **D40 is answered and
  D39's suspension of the matched-cell ratio LIFTS.**
- **Count only** → D40 still runs, after the rebuild, on the rebuilt path.

---

# Addendum 12 — RETRACTION of D55; and the carrier contrast leaves the decision path

Input: RR's `records/L9/matched_mix_check_RR.md`. **Two blockers, and the first withdraws a number I
recorded one hour ago as the defensible one.**

## D58 — ★ RETRACTED: 0.69× / 0.89× / 0.28×. The table was NOT mix-matched — the groups sit at OPPOSITE EXTREMES

RR measured nA through **RE's own `build_size3`**, on RE's templates and seeds:

    carriers=1  (n=120)   nA = 4 in 100% of cells
    carriers=2  (n=119)   nA = 0 in 87% (103/119),  nA = 1 in 13%

**RE reported nA=1 in 100% of cells in both groups. It is 4 versus 0** — the two ends of the range.
**And 103/119 is exactly RE's own figure for amplification draining nA to zero, so the path
presented as `amplify_mix=False` appears still to be amplifying.**

**So D55's table is withdrawn in full: 0.28×, 0.89×, 0.69× and "card-silent is 3.2× card-names" are
all off the record.** My D47 objection was right and understated — I argued the groups were at
*different* mixes; they are at *opposite extremes*.

**This is the third consecutive version of this number to be withdrawn** (0.35–0.49×, then 0.72×,
now 0.69×), and **every withdrawal has come from someone checking a COMPARATOR rather than an
arithmetic step.** Not one was an arithmetic error.

**What SURVIVES:** the amplification mechanism (RR's 103/119 confirms RE's account of it), the
realism analysis, the DP result, the enumeration and carrier-confound proof, the belief-model fix,
and the tie-break decision.

## D59 — A SECOND GAP, and it is not the tie-break: 4.24% is outside the achievable range

RR cannot reach RE's carrier-2 figure under **any** rule, on RE's templates, seeds and builder:

    tie-break        carriers=1   carriers=2
    best-case            1.59%        0.00%
    expectation          1.59%        1.33%
    visit order          1.59%        0.57%
    worst-case           1.59%        2.95%
    RE reported          1.31%        4.24%

**4.24% is outside the entire achievable range (0.00–2.95%).** RR's ceiling code is not the
suspect — on a named single cell it matches the shipped `ceiling_vs_stale_card` to every printed
digit (share 0.008846, oracle 8.188185, tie set 350, min 0.0, max 0.022115).

**Resolve on RR's named cell, not on aggregates.** RR put it in the record as a diff target
specifically so this does not become two people trading means. **Whoever is wrong, one cell shows
it.**

## D60 — ★ A CONFOUND THE REBUILD WILL NOT FIX: the tie-break rule moves ONE group and not the other

**Carrier-2's believed-optimal tie set averages 235.4 allocations against carrier-1's 12.7 — 19×.**

**Carrier-1's ceiling is 1.59% under ALL FOUR rules** — its tie set is harmless, every member
scoring identically under truth. **Carrier-2's spans 0.00% to 2.95%.** So **the choice of tie-break
rule moves one group and not the other**, which is a confound **independent of the mix and
independent of the builder**.

**The rebuild fixes mix and amplification. It does NOT fix this.** And it is not a clone artefact —
RR already showed coverage size 3 alone produces the indifference.

## D61 — ★ RULING: THE CARRIER CONTRAST LEAVES THE DECISION PATH

**The decision needs POOLED size-3 versus disjoint at a realistic mix. It has never needed
carrier-1 versus carrier-2.**

That contrast has produced most of today's churn — the inversion, H1/H2/H3, the definitional
confound, the mix mismatch, and now a 19× tie-set asymmetry that no rebuild removes — **and it was
never what the decision required.** It entered as a stratification to guard against a pooled
average hiding structure, which was a good instinct, and it has since become the thing generating
the structure.

**So: pooled size-3 vs disjoint, at nA=1, with intervals, is the deliverable.** The carrier split
is reported as a **descriptive stratification with its tie-set asymmetry stated**, and **no ordering
claim is made between the groups.** If someone later wants that contrast it is a study of its own.

**This also re-scopes D47: `carriers=1 @ nA=1` is no longer a blocker on the package.** It is
needed only for a contrast we are no longer making.

## D62 — RR is right that patching the fixture has failed as a strategy

**Five rounds of "fixed, and here is the next thing that was silently off": forcing, roles, RNG,
totality repair, and now the amplification state itself.** D56 ruled the rebuild happens before the
package. **RR's evidence upgrades that from a precaution to the only remaining route** — the
override path has now been wrong in five distinct ways and the acceptance built for it cannot test
the six-class case at all.

**Nothing further is priced on the override path.**

**And RR's caveat on their own record is the right instinct: their nA figures are measured through
the builder AS IT STANDS, so they read "as of the current builder" rather than as a property of the
templates.** After the rebuild they must be re-measured, including the ones that just withdrew D55.

## D63 — RR's prediction has no clean verdict, and they said so first

Theirs was conditioned on the inversion being real. **The premise dissolved rather than the
prediction failing**, and they declined to claim a hit at nA=4 that would have been available.
**Recorded as no-verdict.** Mine stays refuted; RE's stays unclaimed.
