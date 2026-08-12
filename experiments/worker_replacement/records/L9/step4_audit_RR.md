# Step-4 audit — the inversion, the nA question, and what the size-3 ceiling actually is (RR)

Four things asked of me: verify RE's theorem about my carrier split, settle whether
`nA=1` is a fact about the generator or about six classes, and attack LS's H1/H2 for
the inversion. All offline. Script: `step4_audit.py`.

**Headline: the inversion is not a property of the lattice — it is a property of the
tie-break. And under the most favourable tie-break the size-3 ceiling is EXACTLY ZERO
on every instance I sampled, in both carrier groups.**

---

## 1. RE's theorem is correct, and my stratification is the thing at fault (confirmed)

```
admissible size-3 partial-overlap templates with O3 : 6480
cross-tab (carrier_count, predicted-from-shared)    : {(1,1): 2160, (2,2): 4320}
counterexamples                                     : 0
```

`carrier_count == 1` ⟺ the successor-unique class **is** the shared class. Exactly as
RE derived, with no counterexamples over the whole space. **So "one carrier vs two
carriers" and "the card correctly names the class the successor is required for" are
the same partition, and no sampling design can separate them.**

**RE is right that the label must change, and the fault is mine** — I proposed the
split as a carrier-count contrast and it was never one-dimensional. Reporting group
means under the carrier label would assert a causal decomposition the design cannot
support.

## 2. `nA=1` is a fact about the GENERATOR, not about six classes (**blocker**)

RE's claim reproduces — and more strongly than they put it. Sweeping **all 720
assignments** of the six classes to the template's slots, 3 seeds each:

```
achievable nA values over 2160 cells : {1: 2160}
```

`nA` is pinned at 1. No label choice reaches 2. **But the cause is a generator defect,
not a property of six classes.** `finance_generator.py:433`:

```python
shared_class = _template_shared_class(chosen) if coverage_override is None else None
```

**When `coverage_override` is supplied — the only way to obtain a six-class lattice —
`shared_class` is `None`, so `shared_class_segments` is never applied**, and the
divergence-selection branch (`if asset_class == shared_class`) never fires either.
Both mix amplifiers are silently off. `shared_class_segments=4` remains the default
and is ignored.

Demonstrated on the same lattice through both code paths — seed 0's own natural
template, supplied back as an override:

```
segment class counts, SAME LATTICE:
   natural path  : retail 4, sovereign 2, bank 1, mdb 1, corporate 1
   override path : corporate 2, bank 2, sovereign 2, retail 2, mdb 1
   the shared class `retail` gets 4 segments naturally and 2 under the override
ceiling share, SAME LATTICE:  natural 0.00%   override 3.50%
```

**So step 4 compared the disjoint template WITH the mix amplifier against size-3
WITHOUT it.** Disjoint's affordability case lives at `nA=4`, which exists only because
the forcing puts 4 segments on one class; size-3 is structurally barred from that mix
point by the `else None`. Matching on `nA=1` does not repair this — it matches the
count while the five-class arm also had divergence selection applied.

**Fix, and it is small and specific:** for a partial-overlap override the shared class
is well defined and unique (`w0 ∩ w1`, size exactly 1 in every admissible template —
see §1), so derive it from the supplied template instead of returning `None`, and
apply the forcing. The disjoint template has no shared class, which is presumably why
the branch exists; that is a reason to handle the empty case, not to disable the
parameter for every override.

## 3. H2 is not supported (denominator artefact)

```
group         oracle   ABS ceiling    share      n
1 carrier      8.757        0.1921    2.17%     30
2 carriers     8.896        0.2187    2.43%     30

oracle ratio 2/1  1.016    ABS ceiling 1.138    share 1.119
```

Oracle barely moves (1.6%), and the absolute ceiling and the share move **together**
and in the same direction. H2 predicts the share inverting while the absolute does
not. It does not happen.

## 4. I do not reproduce the inversion at all — and the tie-break decides its direction

My sample gives two carriers **higher** (2.43% vs 2.17%), the direction the split
predicts. Pricing the same sample under four tie-break rules:

```
tie-break        1-carrier   2-carrier    ratio   direction
best-case            0.00%       0.00%      n/a   --
expectation (D18)    2.17%       2.43%     1.12   expected (2>1)
visit order          2.02%       2.86%     1.41   expected (2>1)
worst-case           5.13%       4.97%     0.97   INVERTED (2<1)

band width per instance:  1-carrier 5.13%,  2-carrier 4.97%
                          against expectations of 2.17% and 2.43%
```

**The inversion appears under exactly one rule: worst-case.** Under expectation — which
is D18, the decided rule — and under bare visit order, the split runs the expected way.
**The band is more than twice the expectation it brackets**, so the reported point is
dominated by which member of the tie set it names.

**So H1 should not be tested yet.** There is no stable inversion to explain; the
first question is which tie-break produced RE's numbers. I am not claiming RE has a
bug — I am claiming the quantity is tie-break-determined, and two people can price the
same lattice honestly and get opposite directions.

## 5. The finding that outranks all of the above (**blocker**)

**Under the best-case tie-break the ceiling is EXACTLY 0.00% — on every sampled
instance, in both carrier groups.**

That is not a rounding statement. It means: for every one of these six-class
instances, **the believed-optimal tie set contains an allocation that is also
truth-optimal.** A manager believing the stale card can attain the true optimum
without knowing anything, provided it resolves ties favourably.

The consequence for the decision is direct. **The size-3 partial-overlap design does
not have a guaranteed positive ceiling.** Its ceiling is a range whose lower end is
zero, and where a given run lands inside that range is decided by tie-breaking — which
is not the information channel under study. Contrast the shipped size-2 lattice, where
the spread is exactly 0.00% on 10/10 and the ceiling is a single well-defined number.

**This is what makes D18's interval load-bearing rather than decorative, and it is
worse than D18 assumed: the interval's lower end is not small, it is zero.**

---

## Labels

| finding | label |
|---|---|
| my carrier split is definitionally confounded; the label must change | **confirmed** (RE's) |
| `coverage_override` silently disables `shared_class_segments`, so step 4's two arms differ in mix mechanism | **blocker** |
| the size-3 ceiling's best case is exactly zero on every sampled instance | **blocker** |
| the inversion is tie-break-determined; it appears only under worst-case | **limitation** on step 4's numbers |
| H2 (denominator artefact) not supported | resolved |
| `nA=1` reproduces over all 720 label assignments | **confirmed** (RE's) |

## What I would do before step 4 decides anything

1. **Fix the forcing defect** and re-price both arms with the mix amplifier on for
   each, so the comparison is like-for-like.
2. **Re-price under D18 expectation with `[min, max]` reported**, not a single point.
3. **Then ask whether the inversion still exists.** It may not.

## Limitation of my own work here

My template sample is 6 per group by even spacing over my own enumeration order, 5
seeds each — a different sample from RE's, and small. **I cannot rule out that the
disagreement is sampling rather than tie-break.** What does not depend on the sample
is the tie-break sensitivity table above (same templates, same seeds, four rules) and
the zero best-case, both of which are within-sample comparisons.
