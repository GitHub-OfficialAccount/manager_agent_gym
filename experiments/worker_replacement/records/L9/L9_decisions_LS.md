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
