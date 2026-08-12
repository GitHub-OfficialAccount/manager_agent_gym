# Attacking D40 — the shipped lattice's zero at a realistic mix (RR)

LS flagged this as the load-bearing unattacked measurement and asked three questions.
**D40 is confirmed, the zero is real, and the mechanism is not the one proposed — and
the control turned up something that may remove the need for the six-class rebuild.**
All on the natural path, so none of it depends on the rebuild.

## Q2 first (fastest): is it zero at nA=2 as well? YES

```
shipped five-class template, natural path, 60 seeds
  amplified segs=4 (as shipped)   nA {4: 60}         1.24%   nonzero 34/60
  amplified segs=1                nA {1: 60}         0.0000% nonzero  0/60
  UNAMPLIFIED (all three off)     nA {1: 48, 2: 12}  0.0000% nonzero  0/60
     of which nA=1: 0.0000% max 0.0000%, 0/48
              nA=2: 0.0000% max 0.0000%, 0/12
```

**Zero at nA=2 too, on every cell.** D40 does not depend on the realistic mix being 1
rather than 2.

## Q1: the zero is REAL, not a floor artefact

The control LS asked for — something that *should* be nonzero at nA=1, through the same
path. Unamplified natural instances, coverage substituted, cap 3, 20 seeds × 120
labelings:

```
lattice                        nA=1                        nA=2
current  (as shipped)     0.000%  (0/1920 nonzero)    0.000%  (0/480)
disjoint (candidate)      4.595%  (1920/1920)         7.038%  (480/480)
partial  (size-2)         2.198%  (1920/1920)         1.059%  (480/480)
```

**Two other lattices are nonzero on every single cell through the identical path.** Not
"sometimes nonzero" — 1920/1920. So the measurement is fully capable of returning a
nonzero ceiling at nA=1, and the zero is a property of the shipped lattice.

## Q3: the card-names inference is correct but is NOT the operative mechanism

LS's restatement is right: `w0 ∩ w1 = {A}`, A is the successor-unique class post-swap
(verified 20/20 earlier), and the card claims A — so the shipped lattice is structurally
a **card-NAMES** lattice.

**But that is not what makes it zero.** The size-2 `partial` template is *also* a
card-names lattice — its successor-unique class is `a`, and the card claims `a` — and it
prices at 2.198%, nonzero on 1920/1920. So card-names does not imply zero.

**The operative mechanism is which class the LIE is about.**

```
current : card claims {A,E}; successor truly holds {A,B}
          the lie is E, and E is covered by NOBODY post-swap
partial : card claims {A,E}; successor truly holds {A,B}
          the lie is E, and E is covered by w2 = {C,E}
```

**A lie about a class nobody covers costs nothing, because every worker falls back to SA
on it equally — routing that segment to the successor is no worse than routing it
anywhere else.** A lie about a class *someone else* covers costs immediately, because the
manager sends it to the worker that cannot do it instead of the one that can.

**The shipped lattice makes its lie about the one class that is worthless to everybody.**
That is why its only channel is capacity displacement, and why it needs forced
concentration to have any channel at all.

## Correction to my own hypothesis

I predicted the threshold would be **nA > cap** (displacement needs overflow). It is
**nA ≥ cap**:

```
segs=1  nA=1: 0.0000%   0/60
segs=2  nA=2: 0.0000%   0/60
segs=3  nA=3: 0.9802%  42/60   <== turns on AT cap, not above it
segs=4  nA=4: 1.2362%  34/60
segs=5  nA=5: 1.4132%  28/60
```

At nA = cap exactly the successor's slots are all needed for A, so a believed-equal E
segment taking one displaces an A — and it is **tie-dependent** (42/60, not 60/60), which
is the same believed-indifference already on the record. Note the nonzero *count* falls
as nA rises while the mean rises: more effect where it occurs, fewer instances where it
occurs.

## ★ The finding the control turned up, and it is decision-relevant

**The size-2 partial-overlap template — the researcher's preferred design, retired as
"not available" — has a real channel at the realistic mix: 2.198% at nA=1, nonzero on
1920 of 1920 cells, with NO sixth asset class.**

Its earlier "prices at exactly 0.00% on 30/30" was measured on **amplified** instances
(substitution onto naturally-amplified books, where the forced class lands on a
different role). **Unamplified it is nonzero everywhere.** That figure was
amplification-dependent and was read as a property of the lattice.

**What still stands:** the combinatorial result is untouched — at coverage size 2 there
are 0 templates with partial overlap *and* a sole-held class *and* a singly-covered lie.
**What that means is different from what it was taken to mean.** That structure was a
*means* to detectability, and the pricing now shows it is not necessary: **the
singly-covered lie alone produces a channel at a realistic mix, and the sole-held class
is precisely the component that contributes nothing.** The admissibility predicate was
over-specified — it required the one feature (a sole-held lied class) that this
measurement shows is worthless.

**So the six-class expedition may be unnecessary.** At the realistic mix, on the natural
path, unamplified: disjoint 4.60%, **partial-overlap-at-size-2 2.20%**, current 0.00%.
Partial overlap is ~48% of disjoint, needs no new asset class, no new lattice parameter
and no rebuild — and it is the design the researcher preferred on realism grounds.

**Declared: this favours the realistic option I have argued for throughout, and it rests
on one substitution measurement over 20 seeds. It should be reproduced natively before
it moves a decision.** But it is cheap to check and it bears on whether the rebuild is
worth its cost, so it should reach the researcher with D40 rather than after it.

## Labels

| finding | label |
|---|---|
| D40 confirmed; zero at nA=2 as well, 0/480 | **confirmed** |
| the zero is real — two lattices nonzero on 1920/1920 through the same path | **confirmed** |
| card-names is correct but not the mechanism; the lie being about an UNCOVERED class is | **mechanism** |
| my nA>cap prediction was wrong; the threshold is nA ≥ cap and is tie-dependent there | **correction, mine** |
| size-2 partial overlap has a real channel unamplified; its 0.00% was amplification-dependent | **blocker on the rebuild's necessity** |
