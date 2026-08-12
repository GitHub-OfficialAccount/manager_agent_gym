# L9 gate review — the native table before the researcher (RR)

Standing rule 7. Three items asked for, in LS's priority order, plus what I verified.

**Verdict: the table is sound and the two candidate figures reproduce. One wording fix
is required before this goes out, the interval needs relabelling rather than rethinking,
and the third structural zero now has a complete mechanism — which is NOT the one
proposed, and which refutes RE's candidate for a different zero.**

## Verification

Independently, native path, `lattice=` parameter:

```
partial, shared_class_segments=1   nA=1   2.258%   <- reproduces LS's figure exactly
current, shared_class_segments=1   nA=1   0.000%   <- reproduces
disjoint, default segs=4, nA=1     n=48   4.829%   <- different population from LS's
                                                       5.272%; theirs is segs=1, mine
                                                       is the default. Not a discrepancy,
                                                       but the two are not the same cell
                                                       and neither should be quoted
                                                       without its `segs`.
```

## Item 2 first, because it is the one that would be read backwards

**LS is right, and the sentence is inverted twice.** `ceiling = oracle − realised`, so:

- the manager's **best** tie-break maximises `realised` and therefore gives the **zero**
  ceiling;
- the manager's **worst** tie-break gives the interval's **maximum**.

So *"a manager that tie-breaks worst-case gets nothing"* is wrong on both halves: it is
the manager tie-breaking **well** that produces the zero, and such a manager does not get
nothing — **it gets everything, and we measure nothing.**

**Required wording:** *"The floor is the manager tie-breaking favourably — it attains the
oracle, and the channel has nothing left to be worth. The maximum is the manager
tie-breaking unfavourably."* Every use of "best"/"worst" in this interval must name
**whose**, because the manager's best is the experiment's worst.

## Item 1 — the zero floors: right reading, wrong object label

**The reading is right:** neither candidate has a guaranteed effect, only an expected one,
and the zero best-case is not a size-3 property — it generalises. Confirmed.

**But the interval is being handed over as if it were an error bar, and it is not.** It is
**the range over an unmodelled decision** — how the manager resolves an indifference the
card gives it no basis to resolve. Three consequences:

1. **The floor is a logical possibility, not a probable outcome.** Attaining it requires
   the manager's tie-break to correlate with truth, and under the card it has no
   information to correlate with. **A zero floor does not mean "the effect might be
   zero" in the statistical sense.**
2. **★ The floors are zero for BOTH candidates, so the intervals overlap completely at
   the bottom and cannot support any dominance claim.** `[0, 9.26]` vs `[0, 4.85]` —
   **the entire comparison rests on the expectations.** If the researcher reads the
   intervals as ranges of plausible truth, the two options are indistinguishable, which
   is not what the evidence says. This must be stated, not left to inference.
3. **The honest gap:** the expectation is the principled estimate for an *indifferent*
   manager. A real LLM manager is not indifferent — it has priors that may correlate with
   truth in either direction, and **we do not model that.** So the expectation is a
   reasonable centre, not a prediction.

**Recommended object:** expectation as the point estimate, interval labelled as *the
range over manager tie-breaking*, and one sentence saying where a run lands is decided by
something outside the manipulation. **Not "±", not a CI, and not a range of plausible
effect sizes.**

## Item 3 — the third structural zero, with a complete mechanism

**LS's draining candidate is partly right and cannot be the whole story.** Counted
directly, `partial`, forcing on the successor-unique class:

```
segs  nA   IRB segs in LIED class   of which COVERED   free successor slots   ceiling
  1    1            1.30                  1.30                 2              2.258%
  2    2            1.00                  1.00                 1              1.252%
  3    3            0.68                  0.68                 0              0.000%
  4    4            0.55                  0.55                 0              0.000%
```

The lied class **does** drain (1.30 → 0.55), which explains the gradual 2.26% → 1.25%
decline. **But it never empties** — 0.68 and 0.55 segments remain while the ceiling is
*exactly* zero. **Draining alone cannot produce a hard zero.**

**The mechanism is capacity saturation, and it is the exact COMPLEMENT of the current
lattice's rule.** `partial` is a card-NAMES lattice: the card correctly claims the
successor-unique class `a`. At nA ≥ cap the successor's slots are entirely consumed by
work only it can do, so **there is no free slot for the lie to misdirect anything into**,
and the lie costs nothing.

```
uncovered lie (current)  channel requires  nA >= cap   -- needs contention to displace
covered lie   (partial)  channel requires  nA <  cap   -- needs a FREE SLOT to misdirect into
```

**Complementary and mutually exclusive, which is why the two mix-responses run opposite.**
And the ceiling tracks **free successor slots** (`cap − nA`) monotonically: 2 → 2.26%,
1 → 1.25%, 0 → 0.00%.

**This refutes RE's candidate mechanism for a different zero.** RE proposed that my
six-class card-NAMES zero at nA=2 was explained by `nA=2 < cap=3`. **It cannot be:
`partial` is also card-NAMES and at nA=2 < cap it is 1.252%, not zero.** So the six-class
nA=2 zero remains **unexplained**, and it is the one open item I would carry rather than
close. Three structural zeros: two now have mechanisms, one does not.

## Consequences for the package

- **`partial` should ship UNAMPLIFIED, and this is now a mechanism rather than a
  preference:** forcing costs it twice — draining the lied class *and* consuming the free
  slot the channel needs. Its best configuration is the realistic one, which is the
  rare case where those coincide.
- **D47 (amplify the successor-unique class) was my recommendation and is wrong for
  `partial`.** It is right for the uncovered-lie regime and actively harmful here. If
  `partial` ships, D47 does not apply to it.
- **`nA ≥ cap` and my `1/n_workers` derivation are scoped to the uncovered-lie regime**
  and describe the lattice being retired. The worker-count lever is correctly dropped.

## Labels

| finding | label |
|---|---|
| "worst case" must name whose; the manager's best is the experiment's worst | **blocker on wording** |
| the intervals overlap completely at zero and cannot support a dominance claim | **blocker on presentation** |
| the interval is a range over an unmodelled decision, not an error bar | **limitation, must be labelled** |
| the covered-lie channel requires nA < cap — complement of the uncovered-lie rule | **mechanism, confirmed** |
| RE's `nA < cap` explanation for the six-class nA=2 zero is refuted | **correction** |
| the six-class card-NAMES zero at nA=2 remains unexplained | **open** |
| `partial` 2.258% and `current` 0.000% reproduce natively | **verified** |
