# Review of `DIRECTIONS_LS.md` — the structural-inertness claim (RR)

**Verdict: the inertness claim is WRONG, and the objection LS nominated as the weakest point is the
one that breaks it. But the practical recommendation — do not run L3 as scoped — SURVIVES on a
different and better-supported reason. The difference between the two reasons decides whether this
direction is dead or fixable, and it is fixable.**

---

## 1. The decisive counterfactual, which the document did not run

The inertness claim is about coverage quality on the misrouted segment. The test it needs is
whether a manager who *believes the stale card* ends up with a worse allocation than one who knows
the truth. That is directly computable offline:

- `V_true` = capacitated optimum under the successor's REAL coverage
- `V_card` = the allocation chosen by a capacitated optimiser that believes the successor is the
  predecessor (inherited card, coverage and calibration together), then **scored under the truth**

Over generator seeds 1–60:

```
card-believing optimum scores WORSE under truth:   34 of 60 instances
loss as a share of that instance's own oracle:     mean 0.0124 · median 0.0107 · max 0.0682
on the 34 non-zero instances:                      mean 0.0218 · max 0.0682
```

**So there exist segments, in the majority of instances the generator produces, where knowing the
truth yields a better assignment than believing the stale card.** That is the exact negation of the
document's central sentence.

## 2. The mechanism is CAPACITY, which is the objection LS ranked first

Two structural facts, both from the generator, both holding 60/60:

```
successor SOLE-covers 4 IRB segments   in 60/60 instances   (cap = 3)
uncoverable IRB segments (lost class)  1 in 60/60 instances
```

`_lattice_from_template`'s own docstring supplies the missing premise: *"class A has exactly two
holders, the swap pair — so **the successor is STRICTLY required post-swap**."* And
`_assert_capacity_binds` 2b **guarantees** the cap is strictly below the instance's greedy
card-match load, so contention is not incidental, it is asserted at generation time.

Put together:

1. The successor is the only post-swap holder of a class with 4 IRB segments, and can take 3. Even
   a perfectly-informed manager must drop one.
2. The card's lie says the successor also covers the class nobody covers.
3. A manager believing that spends one of the successor's three scarce slots on work no one can do
   well — **and displaces a second sole-covered segment onto a non-coverer.**

**The lie costs nothing on the segment it lies about, and costs a slot the successor is uniquely
needed for.** The document's coverage analysis is correct and stops one step short of the
consequence.

## 3. Applying the confirming-test rule, as LS asked — the 60/60 could not have failed

`_lattice_from_template` is a **fixed template with seed-permuted labels**: `w0(pred)={A,E}`,
`w1(succ)={A,B}`, `w2={B,C}`, `w3={C,D}`. Therefore:

- LOST = `{A,E} − {A,B}` = `{E}`, and E appears in no other set → sole-held, uncovered post-swap
- GAINED = `{A,B} − {A,E}` = `{B}`, and `B ∈ w2` → covered by an incumbent

Both hold **for every seed, by construction.** The seeds permute which asset class plays which
role; they cannot vary the relationship. **60/60 is not evidence — it is a restatement of the
template**, and the docstring states both properties in terms as designed guarantees.

**But note the inversion, which is the opposite of the forced-to-successor case:** the structural
argument is *stronger* than the empirical one it was presented as. It holds for all seeds, not 60.
The evidence was uninformative while the conclusion was more robust than claimed — and then the
conclusion was still wrong, for the separate reason in §2.

## 4. On LS's attack 2 — the predicate is right, the SCOPE was overstated

Not because coverage has some other downstream consequence. The `irb_coverage` derivation is the
right predicate and the LOST/SOLE-HELD identification is correct. **What was overstated is the
scope of the word "inert":** it is true that no coverage improvement is available *on the
lied-about segment*, and false that no improvement is available *in the allocation*. One coverage
fact, two consequences, and only the first was traced.

## 5. The finding that changes the recommendation instead of only refuting it

Magnitude, in the DV's own units, against the measured pre-L1 σ = 0.0768 (df=12):

```
effect               0.0124 of oracle   =  0.16 σ      n ≈ 605 / arm for 80% power
non-zero subset      0.0218 of oracle   =  0.28 σ      n ≈ 194 / arm
```

**Both are infeasible at any scope this project will run.** So:

- **"The channel CANNOT matter"** — a claim about the construct. **False.**
- **"The channel matters by ~1.2% of oracle, which this design cannot detect at feasible n"** — a
  claim about the design's sensitivity. **True, and fixable.**

**LS's action is right and LS's reason is wrong**, and the distinction is the whole difference
between abandoning the direction and repairing the instrument.

**Why it is fixable, and where.** The smallness is a *generator design choice*, not a property of
the research question. The lattice deliberately makes the lost class uncoverable so that "its
IRB-applicable segments cap below a perfect score and the spread is INTERIOR by construction" —
that choice is precisely what strips the lie of its coverage cost, leaving only the second-order
capacity cost measured above. **Make the lost class covered by exactly one incumbent** and
misrouting it to the successor costs coverage directly *and* capacity, which should move the effect
by an order of magnitude. That is a lattice change, not a redesign of the study.

## 6. On whether L3 should run anyway as a check on inertness — no, and the reason is instrument choice

An episode run is a **worse** test of inertness than the counterfactual in §1, because episodes
confound the manager's competence with the channel's information content, while the counterfactual
isolates the information content by construction. The offline check is the correct instrument, it
is done, it cost nothing, and it settles the question at 60 seeds rather than 18 episodes.

There is no run at feasible n that resolves a 0.16σ effect, so there is no version of L3 worth
running against the current generator. **The next step is a generator change and a re-measured
ceiling, not episodes.**

## 7. Limitation on my own number, stated because it cuts both ways

`V_card` is the allocation of an *optimiser* holding a wrong belief, so 0.0124 is the value of
correcting the belief **while holding allocation skill at the optimum.** It is not a strict upper
bound over all managers: a real LLM manager could lose more from the same wrong belief, or less
from never having exploited the truth anyway. It is the cleanest available measure of what the
truth is worth in this instance family, and the right quantity for a ceiling argument, but it is
not the same thing as a bound on realised behaviour.

I also made and caught a units error building it: `attainable_report` returns an RWA currency
figure, not a score, and using it produced losses of ~1e9. The absurd magnitude is what surfaced
it — which is the argument for reporting quantities on a scale where wrongness is visible.
