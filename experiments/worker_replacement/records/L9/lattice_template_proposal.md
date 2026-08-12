# Proposed lattice template — for LS and RR before pricing

**Not implemented, not priced.** LS asked for the template written down before it
is priced rather than inferred from code afterwards, and for the sole-held class
question settled. Both below, plus a dependency neither of us had named.

## The problem, stated exactly

Under the current template the class the card LIES about and the class that keeps
the oracle INTERIOR are **the same class**:

```
w0 (PRED) = {A,E}   w1 (SUCC) = {A,B}   w2 = {B,C}   w3 = {C,D}
   lied about        : {E}        sole-held by predecessor : {E}     <-- same
   incumbent coverers of the lied class : 0
```

That is why RR's repair — give the lost class exactly one incumbent coverer —
looks like it destroys interior spread. **It does, under this template, because
one class is doing two jobs.** The predecessor has two slots and one is spent on
the shared class A, so only one is left to carry both roles.

## Proposed template

```
w0 (PREDECESSOR) = {D, E}
w1 (SUCCESSOR)   = {A, B}
w2               = {E, C}
w3               = {C, B}
```

Verified by enumeration over all 5-class 2-subset templates:

```
distinct, equal size (=> non-nested)          : yes
successor strictly required post-swap         : yes — A is held by w1 ALONE
uncovered post-swap (interior spread)         : {D}
lied about by the stale card                  : {D, E}
   D: 0 incumbent coverers  -> sole-held, keeps the oracle interior
   E: 1 incumbent coverer   -> the lie is a COVERAGE error, not just displacement
silent about                                  : {A, B}
   A: 0 incumbent coverers  -> the SILENCE also costs
```

**The predecessor's two slots now carry the two different jobs.** D keeps the
spread interior; E makes the lie cost coverage. Decoupling them is the whole move,
and it requires the predecessor NOT to share a class with the successor.

## Answers to the two questions

**Q2 — does the sole-held class survive? YES.** It is D, and it is now distinct
from the lied-about class. Under the current template they were the same class,
which is the entire reason the repair looked impossible.

**A second gain that was not asked for.** Today the card's SILENCE is always
harmless: the silent class is always covered by an incumbent (measured 60/60), so
not knowing costs nothing. Here **A is held by the successor alone**, so failing to
learn the successor covers A is itself a coverage loss. **Both halves of the card's
error become costly**, where the repair as stated addresses only the lie.

**Q1 — how is it realised? A template edit, plus ONE dependency that BLOCKS.**

**CORRECTION (RR, confirmed against source). An earlier version of this section
claimed the template edit forces `_designate_swap_pair` to be retired, on the
grounds that it derives the swap pair from coverage and would pick a different
pair. That is wrong: `_designate_swap_pair` IS NOT ON THE TEMPLATE PATH.**

`finance_generator.py:536` — the template branch hardcodes the roles positionally:

```python
    if coverage_override is None:
        predecessor_id, successor_id = worker_ids[0], worker_ids[1]
        swap_shared_class = sorted(
            set(workers[0].irb_coverage) & set(workers[1].irb_coverage))[0]
    else:
        predecessor_id, successor_id, swap_shared_class = _designate_swap_pair(workers)
```

The derived rule is the `else`, for `coverage_override` lattices only. **And the
comment three lines above says the derived rule would pick the WRONG pair — the
template creates several two-holder classes — which is why it is bypassed.** So the
two are not "in agreement by construction"; they disagree (RR measured 11 of 40,
28%) and it has never mattered because the rule is not consulted here.

The hazard is real but it is a different one: **dead code whose docstring describes
behaviour that is not live.** A related staleness: the comment at line 571 justifies
publishing `swap_shared_class` on the basis of what `_designate_swap_pair` does,
while on this path the value comes from the `sorted(...)[0]` expression above it —
documentation attributing a value to code that did not produce it.

**HOW I GOT IT WRONG, recorded because it is the error this document argues
against.** I read `_designate_swap_pair`, saw that it computed the swap pair, and
inferred it was live without checking which branch runs — in a proposal whose
central claim is that facts must not be derived from the wrong source.

## THE ACTUAL DEPENDENCY, and it BLOCKS

**The proposed disjoint template does not generate at all.** With `w0={d,e}` and
`w1={a,b}` the intersection is empty, so `sorted(set() & set())[0]` raises
`IndexError` at line 537. This was not caught by the pricing because the pricing
substitutes coverage into instances the generator had ALREADY produced — **the
pricing path and the generation path do not share that line.**

`swap_shared_class` has three consumers: `finance_gate.py:329` (K2's disclosure
publishes it), `finance_gate.py:509/514` (S6 checks its uniformity across the
sweep), and `shared_class_segments = 4` (selects segments OF THAT CLASS).

**Under a disjoint template the mix parameter has no referent at all**, which is a
stronger statement than "a value has not been chosen". Dropping the shared class is
a design change with three things written against it, and it belongs in front of
the team as one rather than being discovered at line 537. **A partial-overlap
template does not have this problem** — it keeps a shared class, so all three
consumers keep their referent.

O3 is unaffected either way: A is held by the successor ALONE post-swap, so every A
segment routes through it; today A has two holders pre-swap and one post.

**Third dependency, which I am NOT proposing a value for:** the segment mix.
`shared_class_segments=4` currently over-weights the shared class because a
round-robin would cap the arrival effect below detectability. With no shared class,
the effect-carrying classes become A (successor-unique) and E (lied,
incumbent-covered). **How many segments each gets is a mix decision that should be
made against the priced ceiling, not before it** — pick it first and we are tuning
the instrument to the answer.

## What I have not done

Not implemented, not priced, no generator change. Pricing needs only the lattice,
so it can be done as soon as the template and the designation rule are agreed.
