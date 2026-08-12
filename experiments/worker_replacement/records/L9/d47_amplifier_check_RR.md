# Does amplifying the successor-unique class work? (RR)

D47 — forcing the mix on the successor-unique class rather than the shared class — was
my recommendation. RE's single-cell diff showed amplified (6.19%) *below* unamplified
(7.43%) on one carriers=2 cell, which is the opposite of what I claimed it would do. So
I checked it across the grid. **Provisional: `build_six` uses `coverage_override`, so
these numbers are on the path being rebuilt.**

## The result: D47 works for the group that matters, and the anomaly is real too

`check_matched_grid.build_six`, clone `corporate`, 12 templates × 10 seeds per cell:

```
                     shared_class_segments=1     =2          =4
carriers=1 (NAMES)         1.33%  (nA=1)      0.00% (nA=2)   1.59% (nA=4)
carriers=2 (SILENT)        3.50%  (nA=1)      6.37% (nA=2)   9.35% (nA=4)
```

**Card-silent rises monotonically with nA — 3.50 → 6.37 → 9.35.** D47 does what I said
it would for the group whose value is in the omission, which is the group the decision
rests on.

## But RE's observation is also right, and it decomposes the amplifier

At **matched nA=1**, amplified card-silent is **3.50%** against RE's unamplified
**4.24%**. So the amplifier is mildly *harmful* at fixed nA while being strongly helpful
across nA.

**The amplifier's entire value is moving nA. Its side-effects — divergence selection and
IRB-approval ordering — cost about 17% at fixed nA.** That is worth stating whenever a
forced figure is quoted, and it means "amplification helps" and "amplification hurts"
are both true of different comparisons. Neither is reportable without saying which nA the
comparison holds fixed — the same construction-naming defect as everywhere else this
phase, now inside the amplifier itself.

## A NEW structural zero (limitation)

**Card-NAMES at nA=2 prices at exactly 0.00% on 120 of 120 cells.** Not small — zero.
And the sequence 1.33 → 0.00 → 1.59 is non-monotonic, so it is not a dilution effect.

This is the third configuration in which the size-3 design's channel is worth exactly
nothing: the best-case tie-break on every sampled instance, the carrier-2 tie set's lower
end, and now card-names at nA=2 outright. **I do not have a mechanism for this one** and
would not guess at one — but a design with three separate exact zeros in its
configuration space is a design whose effect is contingent in a way size 2's is not
(size 2: 0.00% *spread*, single well-defined ceiling).

## What it may do to the ordering (provisional, and it cuts my way — flagged as such)

**Card-silent at nA=4 reaches 9.35%, above the natively-generated disjoint maximum of
6.09%.** So at high nA the ordering may invert in size 3's favour rather than merely
approach parity. At the *realistic* nA=1 it does not: 3.50–4.24% against disjoint's 4.76%,
i.e. 0.74–0.89×.

**Declared: this is the second finding today that favours the option I ranked first, and
I am reporting it as provisional on the override path rather than as a result.** It
should be re-measured after the rebuild before it is quoted, and my realism finding says
the nA=4 row it lives in is the unrealistic one for both options anyway.

## Labels

| finding | label |
|---|---|
| D47 works: card-silent rises monotonically with nA | **confirmed** |
| the amplifier's value is entirely in moving nA; side-effects cost ~17% at fixed nA | **limitation** |
| card-NAMES at nA=2 is exactly 0.00% on 120/120, non-monotonic, mechanism unknown | **limitation** |
| card-silent at nA=4 may exceed disjoint's native maximum | **provisional, favours my ranking** |
