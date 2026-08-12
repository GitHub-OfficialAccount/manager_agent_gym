# L23 — what the four bundles can and cannot answer, committed before the cell-1 bundle exists

**The five-bucket split is a HARNESS gate, not the dependent variable for the channel question.
If it comes back all-MEASUREMENT in both cells — as it did in cell 0 — it will have said the
episode was clean and nothing about whether information changed the manager's allocation.**

Written while episodes 2 and 3 are at 13 of 16 tasks and no cell-1 bundle exists. Episode 1's
allocation has deliberately **not** been read, so this cannot be fitted to half the comparison.

---

## 1. What the split can say, and where it stops

Cell 0 returned `MEASUREMENT 9`, every other bucket 0. **If cell 1 returns the same, the two are
identical on the instrument and the instrument is not the measurement.** The split answers *"did
this episode execute cleanly enough to be read?"* — a precondition. It does not rank allocations.

**So a sentence of the form "the split is the same in both cells, therefore the card made no
difference" would be wrong**, and it is the sentence most available once four green gates are
sitting in a row.

## 2. The quantities that could discriminate, named now

    allocation      which worker got which segment_id  (`allocation`, keyed on the segment index)
    score           `achieved` against the per-segment truth in `finance_scorer`
    mismatch        segments given to a worker whose IRB coverage does not include that class

**The manipulation is `card_updated`.** Cell 0's manager holds the predecessor's card after the
swap; cell 1's holds the successor's. **The discriminating prediction is about `mismatch`: a
manager reading a stale card should route by the predecessor's coverage, and a manager reading
the updated card should route by the successor's.** Where those two coverages differ is the only
place the manipulation can act.

**If the successor's coverage happens to overlap the predecessor's on every segment the manager
routed, cell 0 and cell 1 are indistinguishable BY CONSTRUCTION for that instance** — not because
information did not matter, but because the instance gave it nothing to bite on. **That is a
property of the drawn environment and must be checked before any difference or non-difference is
interpreted.**

## 3. What n=1 per cell forbids

    cells   0 and 1
    seeds   42 and 30
    n       ONE episode per (cell, seed)

**No interval. No variance estimate. No test.** A difference between two single episodes is
consistent with a large effect, no effect, and an effect in the opposite direction — the study's
own declared MDE is 0.20 and this arrangement's ceilings are **0.25x and 0.36x** of it.

**Therefore, binding, and stated before the data:**

- **A difference between cell 0 and cell 1 on one seed is an OBSERVATION, not a finding**, and
  will be reported with the pair of raw numbers and no ratio, no percentage change, and no
  language implying direction was established.
- **Agreement between the two seeds is not replication.** Two instances differing on one
  structural axis is a weak generalisation claim however they are chosen — already recorded at
  L10 and carried here.
- **A null is not evidence of no effect.** The shakedown is not powered for the channel question;
  a null from it may not be read either way, which was pre-declared when the subset was
  authorised.

## 4. What this run IS for

**Harness behaviour, and that is not a consolation prize.** It establishes, on real bundles:
provenance end to end; that the nine states partition live data; `report_form` compliance; the
timestep profile; the failure classes and their rates; and **this environment's spread, which is
what makes the full L3 sizable at all.**

**The sigma from four episodes sizes nothing** — 3 seeds x 3 episodes pools to df=6, the 95%
interval on sigma spans 3.4x and required n spans 12x. **Four episodes is less than that.** Any
feasibility statement carries an order of magnitude with its interval attached, or is not made.

## 5. The one comparison that IS available at n=1

**Whether the manager's allocation is CONSISTENT with the card it holds.** That is a within-
episode property — read the card the manager was given, read where it sent each segment, and ask
whether the routing follows that card's coverage.

**It needs no second episode and no interval**, because it is not a comparison of outcomes; it is
a check of whether the manipulated input reached the decision at all. **If cell 1's manager
routes as though it had the stale card, the channel did not land, and that is a harness finding
worth having before spending on a powered run.**

**This is the quantity to compute first when the bundles are in.**

## What this does NOT establish

- Nothing about effect size, direction, or existence. It is a plan, written before the data.
- The consistency check in §5 can show the channel failed to land; **it cannot show the channel
  worked** — a manager might route correctly by coincidence, by the segments' difficulty, or by
  ignoring the card and asking. Distinguishing those needs the other cells, which are not in this
  run.
