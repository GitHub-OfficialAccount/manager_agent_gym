# Does σ scale with the IRB−SA penalty? (RR)

LS's objection to the researcher's scoring proposal: **widening the penalty widens σ along
with the effect, so `effect/σ` may not move — a units change dressed as a sensitivity gain.**
They asked me to test it rather than agree with it, and named the decomposition as the
question.

**Verdict: the mechanism is right, the magnitude is not. σ scales with the penalty — but only
the 31% of variance that is graded. 69% is non-completion, which is penalty-invariant. So
amplification does buy detectability, and it is BOUNDED.**

## The decomposition, measured on the 18 real bundles

A segment scoring **0 because it never completed** is invariant to the penalty. A segment
scoring **<1 because it was misrouted** scales with it. Per-segment scores recomputed from
`parse_detail` against each instance's truth:

```
                                     mean     SD
lost to ZERO-scoring segments       1.611   0.916    <- penalty-INVARIANT
lost to GRADED (misroute) error     1.101   0.616    <- scales with the penalty
total shortfall                     2.712   0.724

share of shortfall VARIANCE that is penalty-invariant : 69%
```

**The dominant source of run-to-run variation is segments that never completed, and no
scoring change touches it.** Zero-counts run 0–3 per bundle *at a fixed seed*, so this is
execution variation rather than instance variation.

## What amplification would actually buy

Treating the effect and the graded loss as both scaling with a factor k while the zero-loss
does not:

```
   k   effect x   sigma x   effect/sigma x   required n x
   1       1.00      1.00             1.00           1.00
   2       2.00      1.39             1.44           0.48
   3       3.00      1.87             1.61           0.39
   5       5.00      2.91             1.72           0.34
  inf       —          —              1.79           0.31
```

**So LS's objection is half right in exactly the way that matters: `effect/σ` does move, but
it is capped at ×1.79 and most of the gain is in by k≈3.** It is not the unbounded lever the
proposal's instinct assumes, and it is not the no-op the objection assumes.

**And the cap is optimistic.** `score_report` is `1 − min(1, rel_err)`, so a widened penalty
pushes graded losses onto the 1.0 floor — **where they become penalty-invariant too**. Mean
graded loss is 0.149 per graded segment, so the average segment clips around k≈6.7 and the
tail clips much earlier. **The asymptote is not reachable; the practical ceiling is below
×1.79.**

## LS's alternative, priced against it

Raising the contested share (on seed 41 only 5 of 9 segments are contestable) has **the same
structural shape** — it raises the effect and the graded variance while leaving the zero-loss
untouched — **but it is strictly better on two counts.** It does not move the environment away
from the Basel tables, which is the whole realism argument for using them; and it does not run
into the clipping ceiling, because it adds informative segments rather than enlarging the loss
on existing ones. **Same gain, no realism cost, no saturation.** I would take it over widening
the penalty.

## The finding neither option addresses, and it is the largest one

**69% of the variance is non-completion.** Mean 1.611 of an ~8.75 oracle — **18% of the oracle
lost to segments that never produced anything**, with an SD nearly 50% larger than the graded
component's.

**Neither lever touches it.** Widening the penalty and contesting more segments both operate on
the 31%. **The highest-value target for detectability is not the scoring at all — it is
reducing non-completion**, which would lower the noise floor and the shortfall together. That
is where I would look before spending realism on either proposal.

## Limitations

- **The 69% is cross-bundle**, so it mixes instance variation with execution variation. The
  zero-count varying 0–3 *at a fixed seed* says most of it is not instance-driven, but this is
  not a clean within-cell decomposition and there is no corpus that would give one.
- **The k-scaling table is a model, not a measurement** — it assumes effect and graded loss
  scale linearly and independently of the zero-loss. The clipping caveat is the known place
  that assumption fails, and it fails in the conservative direction.
- **σ here is the shortfall SD across bundles, not the DV's per-episode σ.** The decomposition
  is the transferable part; the absolute numbers are not the σ that sizes a suite.
