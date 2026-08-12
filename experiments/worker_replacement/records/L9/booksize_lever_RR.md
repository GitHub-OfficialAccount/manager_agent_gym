# Pricing the book-size lever (RR)

LS asked what a realistic-niche book at 2× and 4× the segment count buys, and where the
DP cost becomes binding. **I proposed this lever, so the headline is that it is much
weaker than I pitched it: the gain is bounded between ZERO and 6.7× in required n, and
which end applies is not determinable offline.** Method: `booksize.py`.

---

## 1. The DP is not the binding constraint, and never was

The capacitated optimum is a **transportation problem**, not something that needs
enumerating over allocations. With three workers it is an exact DP over
`(used_0, used_1)` — O(n · cap²). Positive control against the shipped
1,680-allocation enumeration, 10 seeds × both belief models:

```
max |DP - enumeration| : 1.78e-15   -> IDENTICAL
```

**So book size is free for offline pricing.** 72 segments costs the same as 9. The
1,680-allocation enumeration has been read as a mathematical limit on book size; it is
an implementation choice. **LS's "where does the DP cost bind" has the answer: it
doesn't.** The binding constraint on book size is episode length in live runs, not
ceiling computation.

## 2. The scaling behaves as predicted — on the component I could measure

Each segment replicated k times, cap scaled to 3k, so class mix, concentration and
niche share are held **exactly** constant and only book size moves.

```
  k  segments   cap  ceiling share  sd_alloc/oracle   effect/sd_alloc
  1         9     3         8.56%           0.0384              2.23
  2        18     6         7.70%           0.0265              2.90
  4        36    12         7.68%           0.0182              4.21
  8        72    24         7.61%           0.0125              6.08

relative to k=1:  effect share x0.89 (flat after k=2);  sd_alloc x0.33 at k=8
                  against 1/sqrt(8) = 0.354 -- so sd_alloc falls very close to 1/sqrt(k)
```

**Effect share is scale-invariant** (a one-off 11% drop from k=1 to k=2, then flat), and
**the allocation component of σ falls as ~1/√k**, both as predicted.

## 3. But the allocation component is only 25% of the variance (**and this kills it**)

```
sigma_total (published, k=1)   0.0768
sigma_alloc (measured here)    0.0384
sigma_manager (residual)       0.0665   <- 75% of the VARIANCE
```

Whether manager variance shrinks with book size depends on whether the manager's errors
are **per-decision** (they shrink as 1/√k) or **per-episode** (they don't). That is a
property of the manager, and **it cannot be determined offline.** Both bounds:

```
  k   |  PESSIMISTIC (manager variance fixed)  |  OPTIMISTIC (manager ~1/sqrt k)
      |     sigma    effect/sigma              |     sigma    effect/sigma
  1   |    0.0768            1.11              |    0.0768            1.11
  2   |    0.0716            1.08              |    0.0540            1.43
  4   |    0.0690            1.11              |    0.0379            2.03
  8   |    0.0677            1.12              |    0.0266            2.86

8x the book:  PESSIMISTIC  x1.01 detectability, n/arm x0.98   -- essentially NOTHING
              OPTIMISTIC   x2.56 detectability, n/arm x0.15   -- a 6.7x saving
```

**Correction to what I told LS.** I said the gain was "real but sub-√n". That was wrong:
**the gain may be zero.** Because 75% of the variance is manager-level, the pessimistic
case is not a modest discount on √k — it is no gain at all. I pitched the lever on the
component I could measure and did not weight it against the component I could not.

## 4. The catch-22 worth naming

**Pricing this lever properly requires the measurement it is meant to make affordable.**
Deciding between the two bounds needs σ measured at two book sizes, which needs runs —
and the reason to want the lever is that runs are expensive. The current corpus cannot
settle it: all 18 bundles are 9-segment, and 3 seeds × 6 cells is far too thin to
decompose per-decision from per-episode variance.

**The cheapest resolution, if a run is happening anyway:** run ONE cell at 2× book size
and measure σ directly. That distinguishes the bounds for the cost of a single cell, and
it is the only honest way to price the lever. At k=2 the two bounds are already far
apart (1.08 vs 1.43), so one cell discriminates.

## Verdict

| finding | label |
|---|---|
| the exact optimum is a transportation problem; book size is free for offline pricing | **confirmed, useful** |
| effect share is scale-invariant; sd_alloc falls as ~1/√k | **confirmed** |
| the lever's value is bounded [0, 6.7× in n] and undecidable offline; 75% of variance is manager-level | **limitation — mine, and it retracts my own pitch** |
| my earlier "real but sub-√n" was wrong; the gain may be zero | **correction, mine** |

**Recommendation: do not let the book-size lever change the option set on present
evidence.** It is not the realism-preserving win I proposed it as — it is an open
question with a cheap test attached. If any run happens, add the 2× cell and settle it;
otherwise treat the lever as unpriced.

**What does survive unconditionally is §1**: nothing about book size is limited by the
ceiling computation, so if a larger book is ever wanted for another reason, the DP is not
the obstacle and the enumeration should be replaced regardless.
