# Which number is the disjoint reference? (RR)

LS asked: is 4.76% the right reference, and what is 5.03%? **Their guess is exactly
right — 4.76% is the nA=1 cell and 5.03% is all cells, on the same path.** But the two
numbers are the smaller half of the answer.

## Both figures, and the two paths that produce them

```
(a) SUBSTITUTION onto naturally-generated instances -- price_disjoint_size2(), as shipped
      nA=0   n=384   2.02%
      nA=1   n=576   3.84%
      nA=4   n=240   9.03%
      pooled n=1200  4.30%

(b) GENERATED through coverage_override, same template, same seeds, same labelings
      nA=1   n=960   4.76%
      nA=2   n=240   6.09%
      pooled n=1200  5.03%
```

**So: 4.76% = nA=1 on path (b). 5.03% = pooled on path (b). 3.84% = nA=1 on path (a) —
the figure RE described as superseded.** LS's reading of the discrepancy is confirmed.

## The three findings underneath it

**1. "nA=1" is not the same population in the two paths.** 576 cells at 3.84% under
substitution, 960 cells at 4.76% under generation. Matching on the nA *label* does not
match the population, so naming the nA cell is not sufficient — **the construction path
has to be named too.**

**2. The disjoint template reaches nA=4 ONLY under substitution.** Generated natively
and unamplified it spans nA ∈ {1,2} and tops out at 6.09%. The 9.03% at nA=4 requires
the *natural* template's amplified shared class to coincide, by labeling, with the
*disjoint* template's successor-unique class. **Disjoint's affordability case — the
~1.11σ, ~13 episodes/arm figure that made this option look affordable at all — lives in
that cell.** It is reachable by design once amplification targets the successor-unique
class (the D47 decision), but it is not what the shipped reference measures, and it is
not a property the template has on its own.

**3. The reference is on the override path too, so the rebuild must cover both arms.**
RE regenerated the reference through `coverage_override` to avoid the substitution
asymmetry. That puts the ratio's **denominator** on the path LS has just ruled nothing
further may be priced on. **The disjoint arm is not safe merely for being five-class** —
no candidate template can be built by `_lattice_from_template`, which only ever produces
`{A,E},{A,B},{B,C},{C,D}`, so *every* candidate needs either substitution or override.
The rebuild has to give the generator the candidate templates natively, or the reference
inherits exactly what the numerator was invalidated for.

## Checked and cleared

`n_a` is computed from `sg["irb_approved"]` in RE's code and from
`applicable_approach(sg)` in mine. **These are the same predicate** —
`applicable_approach` is literally `"IRB" if segment["irb_approved"] else "SA"`, and they
agree on 270/270 segment-instances. So the nA=4-vs-nA=0 disagreement on the size-3 arm
is **not** a predicate difference, and that discrepancy remains open.

## Labels

| finding | label |
|---|---|
| the ratio's denominator is on the override path; the rebuild must cover the disjoint arm | **blocker** |
| disjoint reaches nA=4 only via substitution; its affordability case lives in that cell | **limitation** |
| "nA=1" names different populations on the two paths; the construction path must be named | **limitation** |
| 4.76% = nA=1 path (b); 5.03% = pooled path (b); 3.84% = nA=1 path (a) | resolved |
| `irb_approved` and `applicable_approach` are the same predicate | control passed |
