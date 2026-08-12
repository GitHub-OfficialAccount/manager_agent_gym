# Is the nA=4 concentration realistic? (RR)

LS's question, and they flagged it as load-bearing: forcing the mix means deliberately
choosing the favourable value of the parameter we criticised for being silently
inherited. **Is a portfolio with 4 of 9 segments in one asset class realistic — and
does the concentration that makes the effect measurable make the succession scenario
less like the one we claim to study?**

**Short answer: the concentration is realistic; its ALIGNMENT with the staffing change
is not, and the direction of that error is knowable. The consequence hits the disjoint
template exactly as hard as size 3, so it is not an argument between the options — it
is an argument about what the affordability claim rests on.**

---

## First, what the forcing actually does — two amplifiers, not one

Measured over 30 natural five-class instances:

```
IRB-applicable segments in the shared class : 4.00 per seed, min 4, max 4  (44% of the book)
gap cost, shared-class IRB segments         : 0.3163 mean
gap cost, all other IRB segments            : 0.2795 mean      -> ratio 1.13x
combined amplification vs an even round-robin (1.8 segments at average cost): 2.51x
```

**Two mechanisms target the same class.** `shared_class_segments = 4` sets the count
(2.22×), and the divergence selection at `finance_generator.py:449` chooses that
class's *ratings* from a seeded search to maximise the SA-fallback penalty (1.13×).
Both are keyed on `asset_class == shared_class`. **So the design does not merely
concentrate the book — it also picks the worst-case ratings inside the concentrated
class.** That second amplifier is easy to miss when defending the first.

## The concentration itself: realistic (LS's prior is right)

44% of a book in one asset class is ordinary rather than exotic. Bank loan books are
typically dominated by one or two exposure classes — a retail lender's book is mostly
retail and residential mortgage; a corporate lender's is mostly corporate. Basel's
Pillar 2 concentration framework exists *because* concentration is the norm. On this
axis 4-of-9 is unremarkable and I would defend it.

## The alignment: not realistic, and the error has a known sign

**But "real books are concentrated" is not the claim the design needs.** The design
concentrates the book **in the class where the staffing change bites** — the shared
class under the current template, the successor-unique class under the candidates.
Those are two different propositions and only the first is supported by how books look.

**Staffing follows volume.** An institution's dominant exposure is its *best*-covered,
because that is where the work is. Sole coverage in reality attaches to **specialist
niches** — low-volume, high-expertise classes where one approved person is normal
precisely because the volume does not justify two. **So in real institutions
concentration and thin coverage are NEGATIVELY correlated. The design requires them
positively correlated, and maximally so.**

That is the sharp version of LS's question, and it is sharper than the one asked: the
problem is not the 44%, it is that the 44% sits on the one class exactly one post-swap
worker covers.

## Therefore the realistic configuration is nA SMALL

The scenario we claim to study — an organisation loses the sole holder of a capability
— realistically involves a *niche* capability, and a niche is a small share of the
book. **The realistic value of nA is 1, which is what the unforced generator produces.**
nA=4 is the configuration in which the bank's dominant business line is covered by one
person.

## The consequence, and it is not an argument between the options

**Every option's affordability case rests on the forced mix, disjoint included.**

```
disjoint, nA=4 (forced)     0.0851 of oracle   1.11 sigma   ~13 episodes/arm
disjoint, nA=1 (realistic)  0.0347 of oracle   0.45 sigma   ~64 episodes/arm
size-3,   nA=1 (forced off) 0.0135-0.0189
```

Realism costs disjoint a factor of **2.4× in effect and ~6× in n** — the same
mechanism, the same magnitude, as it costs size 3. **So this does not reorder my
ranking.** What it does is put a condition on the headline both options share: *"13
episodes per arm"* is a statement about a book whose dominant asset class has one
qualified reviewer.

**This is why it goes to the researcher WITH the number rather than after it**, exactly
as LS said. Recommending a design on the strength of a mix chosen because it flattered
the measurement is the failure the ceiling arc already caught once.

## Recommendation

1. **Report nA=1 as the primary configuration and nA=4 as a declared upper bound**, not
   the other way round. The unforced mix is the realistic one; the forced mix is the
   best case.
2. **Declare both amplifiers when the forced number is quoted**, not just the count.
   "4 of 9 segments in one class" understates it; the ratings inside that class are
   also chosen adversarially, for a combined 2.51×.
3. **Buy detectability with BOOK SIZE rather than concentration** — the realism-
   preserving lever, and I think it is the one nobody has considered. The effect as a
   *share* of oracle is scale-invariant (loss and oracle both scale with the number of
   segments), while the allocation-variance component of σ falls as ~1/√n. So a larger
   book at a **realistic** 10% niche concentration gains detectability as ~√n without
   touching the mix at all.

   **Caveat, stated because it bounds the gain:** only the allocation component of σ
   shrinks that way. I measured it at ~0.041 of oracle against a published total σ of
   0.0768, so roughly half the variance is manager-level and will not shrink with book
   size. The gain is real but sub-√n, and larger books cost episode length and make
   the exact DP enumeration more expensive.

## Confidence

The measurements (4.00 segments in 30/30, the 1.13× and 2.51× amplification, the
nA=1-vs-nA=4 effect figures) are direct. **The realism judgement — that staffing
follows volume, so sole coverage attaches to niches — is a judgement about how
institutions staff, not something I measured**, and it is the load-bearing step in the
argument. I hold it firmly but it is the part to challenge if anyone disagrees.
