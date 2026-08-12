# L23 — the first non-zero DV is STRUCTURAL, and the same condition lands in two different buckets

**Both drawn instances contain an IRB-applicable asset class that NO worker covers — before or
after the swap. Episode 2's two declines are those segments. No allocation could have prevented
them.**

Computed from the instances alone, zero model calls. Raised by RE, who named the condition
(*"whether any post-swap worker covers `bank` is exactly the thing to check"*) and had not checked
it.

---

## 1. Neither instance can be completed correctly by anyone

    seed 30   predecessor w_4b5a60 (mdb, sovereign) -> successor w_00c22b (mdb, corporate)
              IRB classes no post-swap worker covers:  ['bank']
              structurally undeliverable:              seg_02, seg_06
    seed 42   predecessor w_9f1635 (bank, retail)   -> successor w_721a8b (bank, corporate)
              IRB classes no post-swap worker covers:  ['mdb']
              structurally undeliverable:              seg_04

**The uncovered set is IDENTICAL pre-swap and post-swap in both instances.** So it is not caused
by the replacement; it is a property of the generated environment.

**Episode 2's DV of 2 is exactly `seg_02` and `seg_06`.** The manager staffed every segment
(`n_unstaffed 0`) and no routing decision available to it would have produced a correct IRB
number for those two. **The first non-zero DV in the study is not a manager outcome.**

## 2. ★ THE SAME CONDITION LANDS IN TWO DIFFERENT BUCKETS, because the workers behaved differently

    seed 42  seg_04 (mdb, IRB-applicable, uncovered)   -> w_613442 (sovereign, corporate)
             "no MDB PD calibration exists, so the IRB flag cannot be actioned ...
              Application: Basel Standardised Approach"       rwa 213,254,911.30
             declined = False   ->  MEASUREMENT (executed_and_parsed)

    seed 30  seg_02, seg_06 (bank, IRB-applicable, uncovered) -> declined
             "rwa: unavailable ... bank asset class falls outside my approved IRB
              model scope"                                      rwa None
             declined = True    ->  DV (executed_and_declined)

**Both are correct behaviour for a worker outside its approval. One fell back to the
standardised approach and reported a number; the other declined.** The number is scored against
the IRB truth, so **the fallback is a WRONG ANSWER counted as a measurement, and the decline is
NO ANSWER counted as a DV outcome.**

**CONSEQUENCE: `DV = 0` in episode 1 and `DV = 2` in episode 2 do not mean the seed-42 manager
allocated better.** Both instances contain undeliverable segments; the difference is what the
workers did when they met one. **Reading those two numbers as a manager comparison would be
wrong, and it is the comparison the bucket names invite.**

## 3. The card's action space is ONE segment per instance

    seed 30   successor_strictly_required_segments: ['seg_00']
    seed 42   successor_strictly_required_segments: ['seg_00']

**Exactly one segment in each instance can only be done by the successor.** That single segment
is the entire surface on which `card_updated` can act: everywhere else, either another worker
covers the class or nobody does.

**This is stated as a fact about the drawn environments, not a complaint about them** — it
follows from the approved selection rule, which chose on sole-need class. **But it bounds what
any comparison of cell 0 against cell 1 can show, and it was not visible until the instances were
read this way.**

## 4. The pre-commitment fired

Written three hours ago, before any of this was known:

> *"If the successor's coverage happens to overlap the predecessor's on every segment the manager
> routed, cell 0 and cell 1 are indistinguishable BY CONSTRUCTION for that instance — not because
> information did not matter, but because the instance gave it nothing to bite on. That is a
> property of the drawn environment and must be checked before any difference or non-difference is
> interpreted."*

**The condition it named is real and now measured.** Episode 4 (seed 30, cell 1) will meet the
same two uncovered `bank` segments, and **whatever it reports for them is not evidence about the
card.**

## What this does NOT establish

- **Not that the instances are badly drawn.** Uncovered classes are a realistic property of a
  bank's approval perimeter, and the study's own core-tool rule requires every worker to remain
  able to act — the SA fallback is exactly that.
- **Not that fallback-vs-decline is systematic.** It is 3 segments across 2 episodes: one fallback
  and two declines. Whether it varies by worker, by class, by cell, or at random is unmeasured,
  and the split cannot answer it because it puts the two in different buckets by construction.
- **Nothing about effect size or direction.** No cell-1 bundle has been read.
- The `achieved` figures are not compared here; the oracle is priced at cap 3 against an uncapped
  runtime and comparing them would reintroduce the mismatch L14-b removed.
