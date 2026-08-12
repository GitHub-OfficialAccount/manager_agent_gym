# Is the clone's manufactured indifference signable? (RR)

**LS's question, blocking step 4.** The economic bias is already signed (a clone
inherits its source's SA/IRB divergence, so it understates a real high-divergence
class). This is the other one: the clone is *exact*, which was believed to manufacture
believed-side ties whose re-scoring under truth spreads the ceiling by 7% mean / 14%
max. D14 was narrowed to "signable on economics, unsigned overall".

## Answer: the premise is wrong. The clone does not manufacture the indifference.

**Coverage size 3 does.** The hazard is not ours, and transcribing a real sixth class
will not remove it. Two independent measurements, 10 seeds each.

### 1. A five-class size-3 template with NO clone is already ambiguous

```
arm                           true opt   belief opt   spread mean     max    ambiguous
size 2, 5 classes (shipped)      10.80        10.80         0.00%   0.00%       0/10
size 3, 5 classes, NO CLONE     102.40       102.40         3.94%   7.07%      10/10
size 3, 6 classes with CLONE     30.00        30.00         7.36%  14.10%      10/10
```

**No clone is present in the middle arm at all, and it is ambiguous on 10 of 10
instances with a mean spread of 3.94% and a max of 7.07%** — the same order as the
clone arm and as the effect being measured. The shipped size-2 lattice is exactly
0.00% on 10/10, so the check discriminates.

### 2. Making the sixth class economically DISTINCT does not reduce the ambiguity

A real sixth class differs economically from all five. So I perturbed the sixth
class's SA table by δ, sweeping both signs across nine orders of magnitude — if
exactness were the cause, any δ ≠ 0 would break the degeneracy:

```
     delta    tie set    spread   ambiguous
    -2e-01      30.00     6.55%       10/10
    -1e-02      30.00     7.32%       10/10
    -1e-09      30.00     7.36%       10/10
     0e+00      30.00     7.36%       10/10    <== exact clone
     1e-09      30.00     7.36%       10/10
     1e-02      30.00     7.41%       10/10
     2e-01      30.00     8.22%       10/10
```

**A 20% perturbation of the sixth class's economics leaves the tie set at 30.00 and
the spread within 1 point of the exact clone's.** The degeneracy is not knife-edge and
is not caused by exactness.

**Positive control on my own manipulation, because that invariance is exactly what a
dead knob looks like:** the six-class instances do carry clone segments (1 per seed,
10 of 90 across the sweep), and a 50% perturbation changes 1 of 9 SA numbers in seed
0. **The knob is live; the invariance is a result, not a broken lever.**

## Consequences

**1. The ε-perturbation diagnostic is not confounded — it is INERT (blocker on that
plan).** It cannot sign the bias because it does not break the degeneracy: at δ=0.20
the tie set is still 30.00 and 10/10 instances are still ambiguous. There is no
"unique perturbed ceiling" to compare against the tie set, at any δ. **Tell RE not to
spend on it.**

**2. D14 should be re-pointed rather than narrowed further.** "Virtue and hazard are
the same property" is not what is happening — the hazard is not a property of the
clone. The clone's *economic* bias remains signed and bounded (factor 1.5, cannot flip
a 6–16× ranking). Nothing about the tie ambiguity argues against clone pricing
specifically.

**3. The tie-break is not scaffolding, it is part of the instrument — permanently.**
Expectation over the believed-optimal set with `[min, max]` alongside was adopted as a
fix for a clone artefact. It is not: **any size-3 design has this, including a real
transcribed sixth class.** It must ship with the study rather than be retired when the
clone is.

**4. A NEW cost on the size-3 option that was in nobody's accounting (limitation).**
The size-2 lattice yields an exact ceiling (0.00% spread, 0/10 ambiguous). The size-3
lattice yields a ceiling with a **±4–7% ambiguity band, on every instance.** Since the
effects at stake are 3–8% of oracle, **the size-3 detectability estimate is itself
uncertain by about the size of the thing it estimates.**

Stated precisely, because it is easy to overclaim: this is ambiguity about **what the
ceiling is**, an offline design quantity — not extra noise in what a run would
measure. It degrades the precision of *the decision*, not of the study. But the
decision is being made on detectability, so it lands squarely on the decision.

## Limitation of my own control

The two size-3 arms differ in more than clone presence: my five-class size-3 template
places `sovereign` in all four workers, which is unusually redundant and shows up as
102 tied optima against the clone arm's 30. **So I cannot cleanly attribute the 2×
amplification from 3.94% to 7.36% to the clone rather than to lattice structure.**

What survives that limitation is the part the conclusion rests on: **coverage size 3
alone is sufficient to produce same-order ceiling ambiguity with no clone present**,
and the δ-sweep independently shows exactness is not the cause. Both point the same
way and neither depends on the amplification factor.

## Effect on my ranking

**Unchanged in order** (partial-overlap-at-3 > disjoint-at-2 > current), but the top
comparison is now closer than when I wrote it. Disjoint's ceiling is exact; size-3's
is ±4–7%. That is a real cost against the realism gain, and if the size-3 price comes
in near the detectability threshold, **the ambiguity band means we would not be able
to tell which side of it we are on** — which is a stronger version of my original
contingency, not a new one.
