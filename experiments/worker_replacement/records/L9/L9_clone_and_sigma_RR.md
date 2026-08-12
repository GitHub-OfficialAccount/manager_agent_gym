# L9 — the clone's bias and the σ-invariance break (RR)

Two things LS asked to have attacked **before the number exists**: whether the
economic clone's bias against a real sixth class is signable, and whether template
ratios really are invariant to which σ we eventually use. Both are measurable
offline; neither needed a run. Script: `clone_and_sigma.py`.

**Both come back in LS's favour, and I'd rather say that plainly than manufacture
an objection.** One residual on each, sized.

---

## Q2 — the σ-invariance break is legitimate (limitation, ~5%)

LS's claim: ratios between templates survive a change of σ; absolute levels don't;
so L9 decides on ratio and the absolute verdict moves after L3.

**The arithmetic is trivially true and is not the interesting part.** If one σ
divides every template, it cancels from a ratio. The claim that can fail is the
hidden premise: **that there is one σ.** Detectability is effect ÷ σ *of that
design*, and a template that changes the coverage lattice changes the outcome
distribution too. If the disjoint template widens the spread, dividing it by
`current`'s σ overstates it, and the ratio of *detectabilities* is not the ratio of
*ceilings*.

So I measured the spread each design admits — the SD of realised score over the
allocation space, as a share of oracle, both over all 1,680 feasible allocations
and over the blind sequential procedure `ignorant_stats` uses:

```
template              oracle   SD/oracle (blind)   SD/oracle (all feasible)   vs current
current                8.570              0.0409                     0.0410       1.00x
proposed_disjoint      8.737              0.0431                     0.0431       1.05x
partial_overlap        8.737              0.0431                     0.0431       1.05x
```

**The template moves the design's own spread by 1.05×.** Against between-template
ratios of 6–16×, a 5% distortion cannot change any ordering. **The break holds.**

Three things worth having on the record with it:

- **The residual is signed.** Disjoint has the *wider* spread, so dividing it by
  `current`'s σ **overstates disjoint's detectability by ~5%**. Small, and it
  points against the option that is now the fallback rather than for it.
- **What this proxy does and does not contain.** It captures spread from
  *allocation* variation across a fixed instance set — the component that could
  plausibly depend on the lattice. It does **not** contain across-episode manager
  variability (model stochasticity, message ordering), which is most of the
  difference between this proxy (~0.041) and the published σ (0.0768). That
  component is a property of the manager rather than of the coverage lattice, so
  there is no mechanism by which it would differ by template — which makes the
  invariance claim *safer* than the proxy alone shows, not weaker.
- **The premise to state rather than assume.** The break is valid because
  lattice-driven variance is nearly template-invariant *here*, measured. It is not
  valid as a general principle, and if a future candidate template changes the
  number of *uncovered* classes (all admissible ones so far have exactly one), that
  is where this would break.

---

## Q1 — the clone's bias is signable, bounded, and second-order (limitation)

The ceiling is paid in one currency: the score lost when a coverage gap forces the
SA fallback on a segment whose applicable treatment is IRB. That per-segment cost is
a property of the **class** — its SA/IRB divergence — and **a clone inherits its
source class's cost exactly.** So the bias against a real sixth class is the
difference between the source's divergence and the real class's, and its size is
bounded by how much divergence varies across classes. Measured over 30 seeds:

```
class         segments  IRB-applic   mean gap cost      sd     min     max
mdb                 36          17          0.3564  0.1813   0.002   0.734
retail              54          34          0.3509  0.1692   0.064   0.660
sovereign           80          60          0.3333  0.1926   0.044   0.754
bank                49          39          0.2575  0.1821   0.013   0.631
corporate           51          42          0.2393  0.1726   0.004   0.609

spread across classes : 0.2393 .. 0.3564  = a factor of 1.5
unweighted class mean : 0.3075
```

**Answer: yes, signable — but only once the clone's source is named, and the
choice of source is therefore a decision rather than an implementation detail.**

- Cloning **corporate or bank** understates the class-average gap cost by ~20%.
- Cloning **mdb, retail or sovereign** overstates it by ~14–16%.
- **End to end the clone-source choice can move the sixth class's contribution by
  a factor of 1.5, and no further.** Against template ratios of 6–16× that cannot
  flip an ordering.

**The direction against a *real* sixth class is also partly signable, and it is
conservative.** The five transcribed classes already include the low-divergence end
of the framework (sovereign and MDB carry 0% SA weights in places). The plausible
real candidates for a sixth — equity, real estate, specialised lending — sit at the
*high* SA-weight end, so their gap cost would land at or above the top of the range
observed here. **A clone of an existing class therefore most likely UNDERSTATES
what a real sixth class would deliver**, which is the safe direction: if the clone
clears detectability, a real class clears it by more. I hold this weakly — it rests
on the SA schedules of classes we have not transcribed, so it is an expectation with
a named mechanism, not a measurement.

### The finding that actually matters here, and it is not the clone

**Within-class variation dwarfs between-class variation.** The SD of gap cost
*inside* each class is ~0.18 with a range of 0.002–0.754, against a between-class
spread of 0.12. **Which class you clone matters far less than which segments happen
to land in it.** That puts the clone-source question firmly behind the segment-mix
question — the same parameter that produced the nA artefact and the 27× swing in
required n — and it means a clone-priced σ is:

- **adequate for deciding BETWEEN templates**, which is a ratio question, and
- **inadequate for setting the absolute n**, which is a level question.

That is exactly the split LS's own D11 already makes, arrived at independently.
**So the clone should not be the thing that worries anyone about this decision.**

### One risk the clone introduces that is not about bias (limitation)

An economic clone creates two classes with **identical** SA/IRB economics and
different coverage. For any segment pair (one in the source, one in the clone) and
any two workers covering one class each, the two cross-assignments score
**exactly** equal. That manufactures **exact ties in the allocation optimum** — and
tie-break luck is an already-established failure mode here (the S5 finding, which
is why label permutation was introduced).

**Concrete and checkable once the six-class generator exists:** the rate of exact
ties among optimal allocations should be compared with the five-class case, and if
it rises, the tie-break must be made explicit rather than left to enumeration
order. I would rather this be measured than assumed, and it is cheap.

---

## Labels

| finding | label |
|---|---|
| σ-invariance break is legitimate; residual 1.05×, signed against disjoint | **limitation** |
| clone bias is signable, bounded at a factor of 1.5, cannot flip a template ranking | **limitation** |
| clone-priced σ adequate for ratios, not for absolute n | **limitation** (already D11) |
| within-class variation exceeds between-class by ~1.5×, so the mix dominates the clone | **limitation** |
| economic clone raises the exact-tie rate in the oracle; check when the generator exists | **optional** |

**No blockers.** Neither question is a reason to delay the sixth class.
