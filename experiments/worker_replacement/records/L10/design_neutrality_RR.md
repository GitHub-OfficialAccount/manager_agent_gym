# Does "calibrating vs fitting" hold? (RR)

LS's position: designing so the GAP exists is **calibrating** — the gap is computed with no
manager in the loop, so there is nothing to fit to — whereas designing so a particular manager
scores well is **fitting**. They asked whether an instance can be neutral in the gap
computation and still favour a manager behaviour in a live episode.

**Answer: yes, four ways, and one of them is measured. The distinction is real but it does not
carry the weight the ruling puts on it, because the gap computation is manager-neutral while
the DESIGN AXIS "maximise the gap" is not.**

## ★ The measured leak: maximising the gap makes IGNORING THE CARD a better policy

Natively, `shared_class_segments=1`, 30 seeds per lattice:

```
lattice     oracle   card play   ignorant   card − ignorant   ceiling
current      8.600       8.600      7.796           +0.8032     0.00%
partial      8.541       8.355      7.775           +0.5804     2.18%
disjoint     8.576       8.111      7.783           +0.3277     5.43%
```

**Monotone and near-linear: the larger the ceiling, the LESS the card is worth against knowing
nothing.** A manager that ignores the card entirely gets a payoff that rises as the gap rises.

**So "design for maximum gap" is not behaviour-neutral.** It systematically selects environments
in which **blanket distrust** — a policy using no newcomer-specific information at all —
performs better relative to card-belief. The gap computation never mentions a manager; the
*ordering of instances by gap* nonetheless ranks manager policies. **ENV-A at maximum gap is
precisely the environment where this confound is largest.**

This is the same quantity I measured against the disjoint template earlier in the phase,
arriving now as a property of the design axis rather than of one lattice.

## Three further leaks, argued rather than measured

**1. Tie-break skew.** The gap uses the D18 expectation over the believed-optimal tie set. A live
manager does not tie-break by expectation — it has some systematic rule. **Two instances with the
same expected gap can have very different tie-set distributions**, and the tie set has been
measured spanning 0% to ~5%, i.e. as wide as the effect. An instance selected for maximum
*expected* gap says nothing about that skew, so a manager whose tie-break correlates with truth
for incidental reasons (worker ordering, segment ordering) scores systematically off the
prediction. **Neutral in the computation, not in the episode.**

**2. Segment order.** The gap is a maximum over allocations and is therefore **order-invariant**.
A live manager reading a task list is **order-sensitive**. So an instance can be gap-neutral and
still favour a greedy-in-presented-order manager. RE already built a permutation control for
*enumeration* order because enumeration order was the hazard; the identical hazard exists one
level up and nothing currently controls it.

**3. Exact capacity binding.** `n_segments = n_workers × cap` admits exactly one load shape, so
the manager chooses WHICH work and never HOW MUCH. This does not favour a policy so much as
**delete a dimension**: a manager whose competence is load management can display none of it.
That is a design choice about what the instrument can see, and it should be declared as one
rather than inherited as a convenience.

## On admission as a POST-CONDITION rather than a filter

**Right, and a strict improvement.** A filter selects instances that happen to have the
properties; a post-condition asserts the construction produced them, which is the difference
between a property and a coincidence.

**One condition, from the rule this phase added: the post-condition must be able to FAIL.** An
assertion over a construction that guarantees its own premises is the structurally-zero residual
again — it passes on every input and catches only a typo. **Require a demonstrated failing case
for each of the six properties**: a deliberately mis-built instance that the post-condition
rejects. Six negative fixtures, and they are cheap because the construction is under our control.

## A more diagnostic pair of axes than max-gap / realistic-gap

The proposed ladder varies **gap size**, so an effect on A but not B is a power statement. Given
the measured leak, I would vary **card-informativeness** instead:

- **ENV-A — the card is substantially RIGHT** (high `card − ignorant`, e.g. the `partial`
  structure at +0.58). Blanket distrust *loses* here, so an effect can only come from
  newcomer-specific information.
- **ENV-B — the card is substantially WRONG** (low `card − ignorant`, the `disjoint` structure at
  +0.33). Blanket distrust *wins* here.

**A manager that improves on both used information about the newcomer. A manager that improves
only on B distrusted a bad card.** That separates the confound directly, where the gap-size
ladder separates power from effect — and we already know the power question's answer is "we
cannot tell", because both floors are zero.

**If only one axis is affordable, this is the one to spend it on**, because a power statement can
be recovered later by running more episodes and a confound cannot be recovered at all.

## Assessment

**LS's distinction is sound as stated and insufficient as a safeguard.** "The gap computation
has no manager in it" is true. It does not follow that choosing instances by gap is neutral
about managers, and the measurement above shows it is not. **The fix is not to abandon designed
environments — it is to declare what the design axis selects for, and to pick an axis whose
selection pressure is the one we want.**

---

# Can the card-informativeness axis be spanned WITHIN partial overlap? (RR)

LS's question before RE builds: if yes, both environments keep their realism; if no, ENV-B is
a declared diagnostic rather than a setting.

**Answer: YES by mix alone, and the span is WIDER than switching arrangements gives. But the
axis is COUPLED to gap size, and that coupling is the confound restated — so the pair has to
be chosen for it.**

## Measured, `partial` lattice, varying only which class the mix is forced onto

The card is RIGHT about the shared class `a` (successor-unique, correctly named) and WRONG
about the lied class `e`. 20 seeds per cell; the role assignment is stable under
`force_mix_class` at **20/20 in every cell**, so the two-pass method (probe for labels, then
force) is sound.

```
forced on     segs   card − ignorant   ceiling
shared (a)       1           +0.5614     2.32%
shared (a)       2           +0.7597     1.16%
shared (a)       3           +0.9234     0.00%   <- capacity saturation, nA >= cap
shared (a)       4           +0.8856     0.00%
lied (e)         1           +0.6994     1.74%
lied (e)         2           +0.6114     3.63%
lied (e)         3           +0.5578     4.82%
lied (e)         4           +0.4441     5.07%
```

**Within-partial span: +0.4441 to +0.9234. Cross-arrangement span: +0.3277 (disjoint) to
+0.8032 (current).** The mix axis is wider and sits higher. **ENV-B does not need the disjoint
structure, and both environments keep the realism.**

## The refinement, which is the part that matters

**Card-informativeness and ceiling move INVERSELY and cannot be varied independently.** Forcing
toward the correctly-named class makes the card more valuable *and* shrinks the gap; forcing
toward the lied class does the reverse. So:

- **A wide informativeness span comes with mismatched ceilings** — e.g. shared@2 (+0.76, 1.16%)
  against lied@4 (+0.44, 5.07%). **That reintroduces exactly the gap-size ambiguity the axis was
  chosen to avoid**: an effect on B and not A would again be readable as power.
- **A matched-ceiling pair has a narrow span** — shared@1 (+0.5614, 2.32%) against lied@1
  (+0.6994, 1.74%). Ceilings within 0.6 points, informativeness span 0.14.

**And the top of the range is unusable:** shared@3 and shared@4 reach +0.92 and +0.89 with a
ceiling of **exactly zero** — the capacity-saturation zero (`nA ≥ cap` kills the covered-lie
channel). **Maximum card-informativeness within partial comes with no gap at all**, so ENV-A
cannot be pushed to the top of the axis.

## Recommendation

**Take the matched-ceiling pair and accept the narrower span:** `shared@1` and `lied@1`. The
confound being tested is precisely *"is the manager responding to the gap or to the card being
wrong?"* — **matching the gap removes the alternative explanation, which is the whole purpose.**
A 0.14 span is small, but it is a span on the right axis; 0.32 on a confounded axis measures
the same thing the original ladder did.

**If the narrow span turns out to be undetectable, that is a real finding and not a reason to
widen it** — widening reintroduces the confound, and the resulting number would answer the
question we already know we cannot answer.

---

# Is the researcher's constraint satisfiable? (RR)

*Both environments realistic AND a sufficiently big gap.* LS predicted two levers move the gap
without moving along the confound axis, and committed a prediction. **Tested; the constraint IS
satisfiable, LS's structural claim is vindicated, and their specific prediction is wrong in the
direction that helps.**

## Contested share, arrangement held at `partial`, 20 seeds per cell

```
force on   irb_frac   nIRB   card − ignorant   ceiling
lied           0.44    4.0           +0.4725     1.84%
lied           0.67    6.0           +0.7041     1.74%
lied           0.89    8.0           +0.9302     1.72%
lied           1.00    9.0           +1.0259     1.51%
shared         0.44    4.0           +0.4050     1.20%
shared         0.67    6.0           +0.5569     2.32%
shared         0.89    8.0           +0.6603     3.50%
shared         1.00    9.0           +0.6998     4.22%
```

**LS predicted "gap rises, `card − ignorant` roughly flat". It is not flat — it RISES, steeply,
in both directions of forcing.** That is better than predicted, not worse.

**★ And the shared-forced row is what the constraint needs: the gap and the card's value rise
TOGETHER.** Ceiling 1.20% → 4.22% (3.5×) while `card − ignorant` goes +0.41 → +0.70 (1.7×).
**This breaks the coupling I measured, and for exactly the reason LS reasoned: the coupling was
an ARRANGEMENT-level property, and contested share is a mix-level lever.** Their decomposition
of the gap into structure × per-segment cost is the right frame even though the prediction
attached to it missed.

**Recommended cell: shared-forced at `irb_applicable_fraction ≈ 0.89` — ceiling 3.50%,
`card − ignorant` +0.66.** Both above baseline (2.32%, +0.56), Basel tables untouched, no rating
selection, arrangement unchanged.

**Two cautions on pushing to 1.00.** Every exposure being IRB-approved is at the edge of
plausible — real banks run partial use, with some portfolios permanently on SA — and generation
starts failing there (17–18 of 20 seeds, against 20/20 below it). **0.89 is the last defensible
cell.**

## The rating-divergence lever is not needed, which sidesteps LS's own worry

Since contested share satisfies the constraint on its own, **the "is high-divergence rating
selection the penalty change in a costume?" question does not have to be answered.** For the
record, my view: **not the same move** — a scoring-rule change applies to everything and leaves
Basel, while rating composition selects a portfolio and does not — **but they converge at the
extreme**, and the criterion that separates them is whether the resulting rating distribution
resembles a book someone could hold.

**It is also nearly exhausted.** The divergence selection already implemented buys **1.13×**
(shared-class gap cost 0.3163 against 0.2795 elsewhere, measured earlier this phase). Going
further means selecting the tail — observed per-segment costs run 0.002 to 0.754 — and that is
where "designed book" stops being a figure of speech. **Small headroom, high cost, and not
required.**

## What this does NOT fix, kept separate because it is a different question

**The researcher's constraint and my ENV-A/ENV-B contrast are not the same problem.** Contested
share raises *both* arms together; it does not separate them. A matched-gap pair differing in
card-informativeness is still narrow — `shared@0.89` (3.50%, +0.66) against `lied@2` (3.63%,
+0.61) is a span of **0.05**, narrower than the 0.14 I found before.

**So: the constraint is satisfiable, and the confound contrast remains hard.** Those should be
reported as two results, not one. The environments can be realistic and consequential; what they
cannot yet do is cleanly separate "used newcomer-specific information" from "distrusted a bad
card" at matched gap.

---

# CORRECTION — the contested-share figures I published are not reproducible (RR)

**I gave LS a table and a recommended cell, and LS adopted them. Re-running the same cells
gives different numbers. The reproducible values are LOWER, and the ones I published are the
ones that do not reproduce.**

## The corrected table — verified reproducible

`partial` lattice, shared-forced, `shared_class_segments=1`, 20 seeds, **identical under
`PYTHONHASHSEED` 0, 1, 2 and 3** and identical on repeated in-process runs:

```
irb_frac    ceiling    card − ignorant       previously published
    0.44    1.1779%            +0.3930       1.20%  /  +0.4050
    0.67    2.1265%            +0.5189       2.32%  /  +0.5569
    0.89    3.0574%            +0.6169       3.50%  /  +0.6603
```

**Every published figure was ~7–14% too high.** The direction, the ratios and the conclusion
are unchanged — ceiling still rises ~2.6× across the sweep while `card − ignorant` rises with
it — **but the numbers LS adopted are wrong and the recommended cell is 3.06%, not 3.50%.**

## What I could rule out, and what I could not

**Ruled out:** hash-seed dependence (identical across four seeds); the Monte-Carlo interleave
(in-process, with and without, bit-identical); passing `irb_applicable_fraction=0.67`
explicitly versus relying on the default (identical on 20/20); and differing surviving-seed
sets (n=20 in both runs at the affected cells).

**Not identified:** what differed between the earlier scripts and the later ones. Both are
individually deterministic and reproducible; they disagree with each other. **I cannot explain
it, and I am reporting the corrected values rather than the ones I prefer.**

Suggestive but unconfirmed: 2.32% is close to seed 0's *individual* value (2.3124%), which
would be consistent with an aggregation error in the earlier script rather than a generator
one. **I am not asserting that — it is a coincidence I noticed, not a diagnosis**, and the
earlier scripts were inline one-offs that were never committed, so there is nothing left to
re-run.

## The part that is mine to own

**The earlier scripts were not committed.** That is the same defect I found in
`step4_audit_RR.md` and annotated hours ago — *a record naming a script that does not exist* —
**and I then produced three more uncommitted one-offs and published a recommendation from
them.** I wrote the rule, annotated my own violation of it, and violated it again within the
same day.

**The corrected figures come from a run committed with this record.** Every figure above is
reproducible by re-running it.
