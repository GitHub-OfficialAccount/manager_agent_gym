# L9 review — the template decision (RR)

Attacking the 6,480 enumeration and the realism axis, both asked for by LS before
anything is built. Everything below is offline and deterministic; no run spend.

Reproduction scripts are in scratch and their results are transcribed here in
full; nothing in this file depends on a number I did not recompute myself.

---

## Summary

| # | finding | label |
|---|---------|-------|
| 1 | **12,960 reproduces exactly** under an independently-written enumerator. The reframing stands: partial overlap is available at size 3, and option 2 = option 3. | confirmed |
| 2 | **The sixth class is genuinely required** — size 3 over the existing five classes yields **0** admissible templates. The option's stated price is real. | confirmed |
| 3 | **The substitution pricing method cannot price a six-class template.** No instance has a segment of a sixth class, so its coverage is vacuous and the template silently collapses to its five-class projection. | **blocker** |
| 4 | **6,480 is two different counts that coincide.** "12,960 up to incumbent symmetry" and "the ordered count that also satisfies O3" are both exactly 6,480, over different template sets. The generator-legal count up to symmetry is **3,240**. | limitation |
| 5 | **The disjoint template collapses the stale card's value against ignorance by 4×**, and makes it actively worse than ignorance on 7 of 30 seeds. This is the realism concern, measured. | limitation |
| 6 | **The published 57.1% free-draw figure does not reproduce** — the properties named beside it give 90.5%. | limitation |

---

## What I did, and the control that failed first

I wrote the enumerator from the predicate **as documented in prose**, not from LS's
or RE's code, then ran it against four populations whose answers are already
published before pointing it at anything unknown. Three reproduced; one did not,
and I chased that one down before reporting anything else.

```
POSITIVE CONTROL — the three named templates, classified by my predicate
current              partial=True   sole_held=True   singly_covered_lie=False   -> inadmissible
proposed_disjoint    partial=False  sole_held=True   singly_covered_lie=True    -> inadmissible
partial_overlap      partial=True   sole_held=False  singly_covered_lie=False   -> inadmissible
```

All three land exactly where the team's documents say they land, including the
reason each fails. That is the control that matters most, because it tests the
predicate and not just the arithmetic.

```
THE SIZE-2 IMPOSSIBILITY CLAIM          published: 0 at 5, 6, 7 classes
  size 2, 5 classes :       0 ordered templates
  size 2, 6 classes :       0
  size 2, 7 classes :       0
```

Reproduced, and the hand proof is right: with partial overlap `|P\S| = 1` at size
2, and one class cannot have both 0 and 1 post-swap coverers.

---

## Finding 1 — 12,960 reproduces exactly (confirmed)

```
THE CLAIM UNDER ATTACK — size 3, six classes
  core three conditions only                          12960 ordered    6480 up to symmetry
  universe: C(6,3)=20 subsets, 116280 ordered 4-tuples
```

**The number is right and the reframing it supports is right.** Options 2 and 3
are one option at two coverage sizes, and retiring partial overlap on a constraint
that was a parameter was the framing error LS says it was.

## Finding 2 — the sixth class is genuinely required (confirmed)

The cheapest possible refutation of the option's price would be that size-3 partial
overlap already exists over the five classes we have transcribed. It does not:

```
COVERAGE_SIZE=3 over the EXISTING FIVE asset classes
  universe: C(5,3) = 10 subsets
  core three conditions             : 0 ordered
  of which successor-required (O3)  : 0 ordered
```

**A sixth asset class with transcribed SA weights is a real cost, not an avoidable
one.** I went looking for the cheap way out and there isn't one.

## Finding 3 — the substitution method has a hard boundary at the class count (**blocker**)

`check_template_pricing.py` prices a template for free by substituting worker
coverage into existing instances and leaving the segments untouched. That is valid
exactly because coverage and segments are independent — **and it stops being valid
the moment the template mentions a class no segment has.**

```
asset classes appearing in segments across 30 seeds: sovereign 80, retail 54,
corporate 51, bank 49, mdb 36   ->  5 distinct, ASSET_CLASSES = 5
segments per instance: 9, on all 30 seeds
```

A six-class template substituted onto these instances puts coverage on a class with
**zero segments**. It does not error; it prices the template's five-class
projection and reports it under the six-class template's name. That is the
already-familiar shape: a defaulted absence that is indistinguishable from a real
value at the point of use.

**So step 1 as scoped cannot be done the cheap way.** Pricing size-3 templates
requires generating new instances carrying a sixth class, which needs the SA
weights *first* and a segment-mix decision *first* — and with 9 segments spread
over 6 classes rather than 5, the mix is thinner and more decisive than it was when
`shared_class_segments = 4` produced the nA artefact. **I would rather this be
caught now than after a number exists.**

## Finding 4 — 6,480 is two counts that coincide (limitation)

```
  core three conditions only                       12960 ordered   6480 /2
  + successor strictly required post-swap (O3)      6480 ordered   3240 /2
```

Exactly half of the admissible templates satisfy O3 — the property the generator
**asserts** (assertion 3; `_designate_swap_pair` raises without it). So 6,480 is
simultaneously the symmetry-reduced count of the core predicate and the ordered
count of the generator-legal predicate, over two different sets of templates.

The figure as written does not identify which one it is, and **the count of
templates that are both admissible and generator-legal, up to incumbent symmetry,
is 3,240.** Nothing in the decision turns on 3,240 vs 6,480 — both are enormous —
but the coincidence will mislead the next person who divides by two.

## Finding 5 — the realism concern, measured (limitation)

LS asked whether a disjoint template still models *the same job done by someone
else*. I don't think that question has to stay a judgement call, so I priced the
thing underneath it.

The study measures what information **about the newcomer** is worth. Its baseline
is a manager holding the predecessor's stale card. If that card is *maximally*
wrong, then a manager that merely **distrusted it wholesale** — learning nothing
newcomer-specific at all — recovers part of the measured effect, and the design
stops separating "learned about the successor" from "stopped believing a bad
prior". So: three-way, exact, same instances, same machinery.

```
template              ceil vs card   ceil vs ignorant   card-ignorant   card WORSE
current                     0.85%              9.95%         +0.7786        0/30
proposed_disjoint           8.51%             11.02%         +0.2203        7/30
partial_overlap             0.00%             11.02%         +0.9614        0/30
```

`card-ignorant` is the stale card's **net worth against knowing nothing**.

**The disjoint template does not make the card useless, and I want to be exact
about that** — on average it stays positive (+0.22), so blanket distrust is not a
winning policy and my first hypothesis was wrong as stated. What it does is
**collapse the card's value to 23% of what it is worth under partial overlap**
(+0.22 vs +0.96), and drive it **negative on 7 of 30 seeds** — instances where the
card-believing manager scores below a coverage-blind random assignment, beyond 2 MC
standard errors.

**That is the realism concern in a number.** A successor whose card retains a
quarter of its value, and misleads outright a quarter of the time, is quantitatively
close to unrelated to the worker it replaced. "Fully capable but works differently"
is not what a disjoint lattice encodes; **a different specialist walking in** is.
The information channels would then be measured against a near-vacuous prior, which
is a weaker and less interesting claim than the one the brief makes — not a wrong
result, but a different question.

`partial_overlap` at size 2 pricing at **exactly 0.00%** is independently
confirmed here, on the same run.

## Finding 6 — the 57.1% free-draw figure does not reproduce (limitation)

`_lattice_from_template`'s docstring: *"free draws at five classes satisfy them
only 57.1% of the time (all 210 lattices enumerated)"*. The 210 is right
(`C(10,4)`). The 57.1% is not reproducible from the properties named beside it:

```
a 2-holder class AND a 1-holder class (the stated properties)     190/210 = 90.5%
... AND all five classes covered                                  130/210 = 61.9%
... AND the 1-holder class is held by the DERIVED predecessor      55/210 = 26.2%
```

No conjunction of plausible atoms gives 120/210. The only predicate over the 210
that yields exactly 120 is *"some class has exactly three holders"*, which is not
among the stated requirements and has no design motivation I can see.

**Not load-bearing** — construction beats draw-and-reject because generation stays
**total**, not because rejection is expensive, and that argument holds at 90.5% as
well as at 57.1%. But it is a published figure that does not reproduce, sitting in
a docstring where it will be cited again. Correct it or drop it.

---

## Ranking

Pairwise, with the deciding criterion named.

**disjoint (size 2) vs current** — *detectability.* Disjoint, decisively: 8.51% and
nonzero on 30/30, against 0.85% and 15/30. Not close.

**partial overlap (size 3) vs current** — *detectability, unmeasured.* Partial
overlap, on the presumption that it beats an undetectable baseline; no number
exists yet.

**partial overlap (size 3) vs disjoint (size 2)** — *whether the setup answers the
question we claim.* **Partial overlap, and this is the close one.** Disjoint wins
on every measured axis and loses on the only one that decides what the result
means: it reduces the manager's starting belief to something barely better than
noise, and the brief's question presupposes a prior that is substantially right and
locally wrong. **But my ordering here is conditional on a number nobody has** — if
size-3 partial overlap prices below detectability, the ranking inverts to disjoint,
because a realistic setup that cannot measure anything answers no question at all.

**Ordering: partial-overlap-at-3 > disjoint-at-2 > current**, with the top
comparison contingent and the bottom one not close.

**What would change my ranking:** a size-3 partial-overlap price below ~0.5σ. I'd
then take disjoint and state the "different specialist" limitation in the paper
explicitly, rather than take a realistic instrument that measures nothing.

---

## Recommendations

1. **Do not price size-3 templates by coverage substitution** (finding 3). It
   cannot work, and it fails silently rather than loudly. The sixth class's SA
   weights and a segment mix have to come first — which makes step 1 substantially
   more expensive than "offline, zero spend" implies.
2. **When the sixth class is added, assert that every class in a template has at
   least one segment**, at generation, raising. This is the defaults rule applied
   to the class axis: absence must not be silently priced as a real zero.
3. **Report the size-3 price against BOTH baselines** (`ceiling_vs_stale_card` and
   `ceiling_vs_ignorant`) and publish `card − ignorant`. The last column is what
   tells us whether the template preserves the study's premise, and it is one line
   of extra work given both functions already exist.
4. **Fix or drop the 57.1%** (finding 6); state which predicate 6,480 counts
   (finding 4).

---

# RESOLUTION — RE's belief model verified, and one line of mine withdrawn

_Added after RE's `3822e2d`. They asked me to check the isolation of
`check_card_belief_model.ceiling_replacement`, and disputed one line of my nA
decomposition. Both checked below; script in scratch, results transcribed._

**Control on my own reimplementation first**, because I was about to use it to
judge someone else's: independently rebuilt pricing (exact enumeration over the
1,680 feasible 3/3/3 allocations rather than filtering 3⁹) reproduces
`check_template_pricing` to the printed digit — current **0.85%**,
proposed_disjoint **8.51%**, partial_overlap **0.00%**.

## The isolation is clean, and now proved rather than inferred (confirmed)

RE's control — 30/30 agreement under the current template — is *consistent* with
isolation but cannot establish it: two belief models can differ on individual
segments and still select the same allocation, which would hide a second
difference behind an aggregate. So I compared the two `believed_score` functions
**segment by segment**, all three templates × 30 seeds:

```
segment-worker cells compared                                          810
models AGREE                                                           648
differ on a class the card is SILENT about   (the INTENDED difference)  162
differ on a class the card CLAIMS            (a SECOND difference)        0
```

The specific thing I went looking for: the shipped model returns a **hardcoded
1.0** on a card-claimed IRB class, while the replacement model returns
`s(seg, succ_as_carded)`. Those coincide **only if `s()` is exactly 1.0 there**,
and if it were not, the models would differ in two places and the 8.13% gap would
not be attributable to the belief model. **It is exactly 1.0, on 0 of 810
exceptions.** The mechanism: calibration has been class-level since R1, so
`succ_as_carded` holds the *true* table entry for a claimed class, `irb_rwa`
equals `correct_rwa`, relative error is 0 and `score_report` returns 1.0.

**So RE's 8.13% is the belief model's and nothing else's.** One condition on
that, worth an assertion rather than a memory: **the isolation DEPENDS on
calibration being class-level.** Reintroduce any per-worker calibration noise and
the two models begin differing on claimed classes too — silently, and in the
direction of looking like a bigger belief-model effect than it is.

## My "nA=0 is IDENTICAL to the current template" — withdrawn (RE is right)

Their table reproduces exactly on my independent implementation, 10 seeds × all
120 labelings, replacement model, nA measured per cell:

```
                   nA=0   nA=1   nA=4    pooled       cells: 32% / 48% / 20%
   current         0.03   0.06   0.07     0.05    sigma
   proposed_disjoint 0.18  0.45   1.11     0.50    sigma
   ratio            6.9x   7.6x  16.4x
```

**I compared disjoint-at-matched-mix against current-at-its-own-mix**, which are
two different quantities, and RE named the error correctly. At matched mix the
disjoint template beats the current one **6.9× at the least favourable end** and
at every other end. "The repair delivers nothing at nA=0" was wrong.

**What survives is the half that decides affordability**, and it is worth keeping
separate from the part I got wrong:

```
   nA=0     0.18 sigma  ->  ~494 episodes/arm
   pooled   0.50 sigma  ->   ~64 episodes/arm
   nA=4     1.11 sigma  ->   ~13 episodes/arm
```

So **both statements are true**: the template difference is real at every mix, and
the mix still decides whether the study is affordable at all. The correct version
of my point is *"still undetectable at the unfavourable end"*, not *"identical to
the current template"* — a 27× swing in required n across the mix distribution,
from one design parameter.

## New limitation this surfaces (limitation)

**The 13-episodes/arm figure is the nA=4 cell, which is 20% of labelings.**
Realising it means *setting* the mix so 4 of 9 segments are IRB-applicable in the
class exactly one post-swap worker covers — a book with ~44% of its segments in a
single asset class held by a single worker. That is a **second realism cost,
stacked on the disjointness cost of finding 5**, and it lands on the same axis the
researcher pointed at.

I do not think choosing the mix is illegitimate: the ceiling is the instrument's
*sensitivity*, not the answer, and choosing a design that can detect its effect is
ordinary. But it must be **declared as a design parameter with the n it buys**,
because "13 episodes/arm" and "the portfolio is 44% one class" are the same
decision stated twice.

## Optional

`partial_overlap` returns ceiling shares of **−2e-17** on 4 of 30 seeds — float
noise around a genuine zero, not a defect in the finding. But a ceiling is a
non-negative quantity, and by the plausible-range rule it should assert that
rather than print a negative share.

## Accepted without further checking

RE's `labels_of()` mechanism for the six-class failure — `.pop()` on `pred & succ`
and `pred - {a}` treats them as singletons, so at coverage size 3 label recovery is
**undefined rather than merely wrong**, and it fires before my zero-segment
problem but only sometimes. That is the sharper of the two mechanisms and I prefer
it to mine.

**Ranking unchanged** (partial-overlap-at-3 > disjoint-at-2 > current), but the
disjoint option is stronger than my earlier decomposition implied, and the
contingency on the top comparison is unchanged: it still rests on a size-3 price
nobody has.

---

## CORRECTION — the swing is 38×, not 27×, and it is σ-free by construction

_LS's D11 correction is accepted: the episode counts (~494 / ~64 / ~13) divide by
the pre-L1 σ and must not be quoted. Restating the surviving half — and the figure
I gave for it was wrong._

I reported the mix's effect on required n as a **27× swing**. Recomputed from the
raw ceiling shares, with no σ anywhere:

```
disjoint template, mean ceiling share by nA (10 seeds x 120 labelings)
   nA=0      0.013756   (n=384)
   nA=1      0.034689   (n=576)
   nA=4      0.085066   (n=240)
   pooled    0.038066

required-n swing = (effect ratio)^2, so sigma CANCELS
   nA=0 -> nA=4    38.2x
   nA=0 -> pooled    7.7x
   pooled -> nA=4    5.0x

effect ratios, also sigma-free
   nA=4 / nA=0     6.18x
   nA=4 / pooled   2.23x
```

**The swing is 38.2×.** 27× was my arithmetic error, and it has been quoted back to
me twice as the half that survives, so it needs correcting before it settles.

Two things worth stating about the corrected form. It is **stronger** than the
version I gave: expressed as `(effect ratio)²` it never touches σ at all, so it does
not merely survive D11 — it is outside D11's scope by construction, and the same is
true of the 6.18× effect ratio. And it makes the substantive point harder rather
than softer: **one design parameter moves the required sample size by a factor of
38**, which is why the mix has to be a declared choice with the ratio it buys, not
a value inherited from a generator tuned for a retired template.
