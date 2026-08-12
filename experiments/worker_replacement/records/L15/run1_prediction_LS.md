# First authorised run on the designed environments — LS prediction

**Committed BEFORE asking RE or RR, and before any episode exists.**

## What is being run

Environments **seed 56 (bank)** and **seed 37 (corporate)**, at the settled cell, **after** the
oracle is aligned to the runtime. Cells **0** (nothing available — the zero point) and **1** (the
registry entry is updated). Few episodes; feasibility scale, not a powered comparison.

**Why 0 vs 1 and not more:** cell 1 is the faithful-production case and cell 0 is the baseline it is
measured against. If the difference between *"told nothing"* and *"told plainly"* does not show, no
subtler channel will.

## The prediction

> **In cell 1 the manager will route at least one loan to the successor that it did not route there
> in cell 0, and that loan's asset class will be one the successor is genuinely approved for.**

Stated as an observation rather than a rate, because a few episodes cannot support a rate.

**Reasoning:** the successor is the sole approved holder of one class, and the updated entry names
it. A manager that reads the entry has a direct reason to move work there; a manager in cell 0 has
no signal at all and should allocate as though the predecessor's approvals still applied.

## What would falsify it

- **No routing difference between the cells** — the manager does not read or does not act on the
  registry entry. That is the more interesting outcome and it is the one the prior corpus hints at:
  the pre-revamp finding was that a manager ignoring the swap and following the outdated document
  scored optimally anyway.
- **A difference in the wrong direction** — cell 1 routes AWAY from the successor's true classes,
  which would mean the entry is being misread rather than unused.

## What it does NOT establish

Nothing about effect size, and nothing about the other three channels. **A few episodes is a smoke
test of the whole path — environment, swap, scoring, split — on the designed environments for the
first time.** The report contract was tightened since the last run and is UNVERIFIED; `report_form`
on these bundles is the first evidence either way.
