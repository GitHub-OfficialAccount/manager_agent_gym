# Is worker count a realistic lever? (RR)

LS derived that the detectability threshold is a niche **share** equal to `1/n_workers`,
and asked me to attack the derivation and answer the realism half: **is a 5- or
8-analyst team the same institution we claim to study?**

**Answer: the derivation holds, LS's own counter-argument does NOT apply to a
constructed lattice, and worker count improves realism on three axes at once. It is the
first lever this phase that buys sensitivity and realism together.**

## The derivation holds, with one clarification and one unification

`n_segments = n_workers × cap` (capacity binds exactly) plus `nA ≥ cap` gives
`nA / n_segments ≥ 1 / n_workers`. Arithmetically right.

**Clarification:** `n_workers` is the **post-swap roster** (3), not the pool (4). The
lever is post-swap roster size.

**Unification worth recording:** the threshold rule subsumes the earlier slack finding.
"Card ceiling exactly zero at cap 5" was measured at the shipped `nA=4`, and `4 < 5`, so
the threshold predicts zero. **Two findings, one mechanism.**

**And LS is right that this explains my book-size lever structurally rather than
numerically.** Book size scales `n_segments` and `cap` together, leaving
`nA/n_segments ≥ 1/n_workers` untouched. **My lever failed on the geometry, not on the
variance** — the variance accounting was correct but was answering a question the
geometry had already closed.

## LS's suppression counter applies to DRAWN lattices, and this generator CONSTRUCTS

LS could not sign the net because more workers means more incumbents, so omitted classes
are more likely incumbent-covered and sole coverage rarer. **Counted over all sets of k
distinct 2-subsets of five classes:**

```
k post-swap   lattices   P(a GIVEN worker sole-holds)   lattices where SOME worker does   threshold
     3           120                75.0%                     110  (91.7%)                  33%
     4           210                46.4%                     195  (92.9%)                  25%
     5           252                23.8%                     210  (83.3%)                  20%
     6           210                 9.5%                     120  (57.1%)                  17%
```

**The suppression is real for a random draw — 75% → 24% → 9.5% — and irrelevant to a
constructed one.** `_lattice_from_template` constructs; it does not draw. What matters is
whether a viable template **exists**, and at k=5 there are **210** of them at five
classes. Example, sole coverage intact:

```
post-swap roster  AB  AC  AD  AE  BC        sole-held: D, E
successor         AD  (sole-holds D)        threshold niche share 1/5 = 20%
```

**So the lever costs no new asset classes** — the thing the six-class expedition was
paying for. The `1/n_workers` gain is available at five classes today.

## The realism answer, which is what was asked

**A 5-analyst team is MORE realistic than a 3-analyst one, not less.** A bank running IRB
across five asset classes with three approved reviewers is on the small side; real
credit-risk and model-validation functions are 5–20. So the lever moves *toward* the
institution we claim to study.

**Sole coverage survives team size in reality.** Key-person risk exists in teams of fifty
because coverage follows **specialisation**, not headcount — one person owns the
securitisation book whether the team is 5 or 50. Team size does not dissolve sole
expertise; it is what makes it specialisation rather than arithmetic.

**And that is the sharpest point, because it inverts the concern.** At k=3, sole coverage
is nearly forced — 75% of random lattices have it — so it is a consequence of the team
being *tiny*, not of anyone being a specialist. **At k=5+ sole coverage stops being an
artefact of smallness and becomes genuine specialisation, which is the scenario the brief
actually describes.** The succession we claim to study — an organisation loses the sole
holder of a niche capability — is better modelled by a specialist in a team of five than
by one of three generalists.

**Three axes, all improving together:**

| axis | k=3 | k=5 |
|---|---|---|
| team size vs real institutions | small | typical |
| sole coverage | forced by arithmetic | genuine specialisation |
| niche share threshold | 33% | 20% |

**This is the first lever this phase that buys sensitivity and realism together.** Every
other one traded them — concentration, cap, book size.

## Costs and caveats, stated because the lever is mine to be sceptical of

1. **`n_segments` must scale**: k=5 at cap 3 means **15 segments**, not 9. That is a
   longer episode and more run spend, and the exact DP is unaffected (transportation
   problem) but live runs are not. **A real cost, in money rather than realism.**
2. **20% is still not a niche.** The threshold improves in the right direction and does
   not reach "one specialist in a large book". At k=6 it is 17%. The realism argument I
   made about nA=4 is softened, not answered.
3. **It needs the lattice-as-parameter rebuild** to express a k=5 template at all — but
   that is already ruled, and this needs no *additional* machinery beyond it.
4. **The suppression counter returns if anyone ever draws instead of constructing.** The
   83.3% at k=5 is the existence rate, not a safety margin; at k=7 it falls to 16.7% and
   the lever would die on a drawn lattice.

## Labels

| finding | label |
|---|---|
| the `1/n_workers` derivation holds; `n_workers` is the post-swap roster | **confirmed** |
| it unifies the earlier "zero at cap 5" slack finding | **confirmed** |
| LS's suppression counter applies to drawn lattices only; 210 viable constructed templates at k=5 | **resolves the open sign** |
| worker count improves realism on team size, the nature of sole coverage, and niche share | **judgement, mine** |
| costs 15 segments per episode; 20% is still not a niche | **limitation** |

---

# Addendum — the joint configuration, and a caveat on my own reproduction

## The reproduction is a CONSISTENCY check, not an independent one (caveat, mine)

Generating the three lattices through `coverage_override` (post-fix, unamplified) instead
of substituting onto unamplified natural instances:

```
current   nA=1  0.000%  (0/1920)      nA=2  0.000%  (0/480)
disjoint  nA=1  4.595%  (1920/1920)   nA=2  7.038%  (480/480)
partial   nA=1  2.198%  (1920/1920)   nA=2  1.059%  (480/480)
generation failures: 0
```

**Identical to the substitution figures in every digit — and that is the tell.** With
`amplify_mix=False` there is no shared class to force, so **segment generation does not
depend on the lattice at all**, and the two paths necessarily produce the same instances.

**So this is not a second path agreeing; it is one population reached two ways.** It rules
out a substitution *bug* and nothing else. **Native reproduction still requires the
lattice-as-parameter rebuild**, and my caveat that the 2.198% needs native confirmation
before it moves a decision stands unchanged.

## The joint question: is 5 analysts + a 15-segment book the same institution?

**Yes — and it is more realistic than the k=3 configuration, for a specific reason rather
than a general preference.**

The threshold in absolute terms is always **`cap` segments** — one analyst's full
workload. Expressed against an even class share:

```
post-swap workers   n_segments   threshold   even share   niche vs an AVERAGE class
        3                9          33%         20%               1.67x
        4               12          25%         20%               1.25x
        5               15          20%         20%               1.00x
        6               18          17%         20%               0.83x
```

**The niche must be `n_classes / n_workers` times an average asset class.** At k=3 that is
**1.67×** — which is where my concentration objection had its force. **At k=5 it is
exactly 1.00×: the specialist owns an AVERAGE-SIZED asset class.** No concentration is
required at all.

**Two things make the joint scaling the realistic move rather than a convenient one:**

1. **Segments per analyst stays at 3.** Per-reviewer workload in a real risk function is
   set by process — how long an RWA calculation takes — not by the size of the bank. So
   *workload per head* is the invariant and *total book* is what scales with headcount.
   Holding the book at 9 while adding analysts is the odd configuration, not this one.
2. **The niche stays 3 segments in absolute terms while the book grows around it.** That
   is how niches behave: a specialist's portfolio does not grow with the institution; the
   mainstream lines do. The share falls because the denominator grows, which is the real
   mechanism.

## This dissolves my own nA=4 objection rather than softening it

I argued that concentration in the sole-covered class is anti-realistic because staffing
follows volume — an institution's dominant exposure is its best-covered. **At k=5 the
design needs no concentration: the niche is an average-sized class held by one
specialist**, which is ordinary. The tension I identified was real at k=3 and is an
artefact of a 3-person roster, not of the design.

**And the threshold restates as a realism CONDITION rather than a cost:** the niche must
be **at least one analyst's full workload**. That is precisely the condition under which a
dedicated sole specialist exists at all — a niche smaller than one person's job would be
covered alongside other work, and its holder would not be its sole holder. **The design
requires exactly what makes the scenario coherent.**

## Revised bottom line

| configuration | niche vs average class | realism verdict |
|---|---|---|
| k=3, 9 segments (current) | 1.67× | concentration objection stands |
| k=5, 15 segments | 1.00× | ordinary institution; objection dissolves |
| k=6, 18 segments | 0.83× | niche can be below average |

**Realistic exactly when the post-swap roster is at least as large as the number of asset
classes.** Cost remains run spend: 15 segments per episode rather than 9.
