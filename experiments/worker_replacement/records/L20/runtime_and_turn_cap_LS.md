# L20 — The 13-minute task does not exist, and the turn cap does not reach the DV

**A worker task takes a median of 81 seconds. The "13 minutes" I gave the researcher was
the average of the slowest fifth of runs, quoted next to a maximum taken from all of them.**

Instrument: `probe_runtime_by_task_class.py`. Zero model calls, 299 worker runs across the
23 committed bundles, exact `(actor_id, task_id)` pairing, 0 unmatched.

---

## 1. The correction I owe the researcher

    population        n     mean   median     p90      max
    ALL runs        299     190s      81s    489s    2160s
    SEGMENT only    176     259s     136s    583s    2160s
    over 300s        59     617s     489s   1040s    2160s
    over 600s        20     998s     765s   1787s    2160s

The researcher was told **"on average a worker task is roughly 13 minutes, and the longest
is 36."** The 36 minutes is row 1 — corpus-wide, correct. The 13 minutes sits between rows
3 and 4: **it is the mean of the slow tail.** Two populations, presented as one description
of a task.

**This is the same defect the project already paid for** — *a derived quantity is only as
good as its closer set, and the closer set must be stated with the number.* The rule was
written about refusal codes and applied to durations one day later without noticing.

**And the researcher's expectation was much closer to right than my figure implied.** They
expected "generally less than a minute, at most two." The median is **81 s**, and the median
segment task is **136 s**. The gap is not 13×; it is about 2×, plus a tail: **7% of runs
exceed 10 minutes and they carry a third of the wall clock.**

## 2. Where the time actually goes

    class               runs  died   hours    mean   share
    SEGMENT (the DV)     176     4  12.66h    259s   80.2%
    UPSTREAM (prep)       93     5   1.42h     55s    9.0%
    AGGREGATION           26    18   1.29h    178s    8.2%
    MANAGER_CREATED        4     1   0.41h    368s    2.6%

**80% of the clock is the measured unit doing its job.** There is no scaffolding overhead
to cut. The over-engineering hypothesis is now tested twice — once on what a worker does
inside a task (≈3 calls, 100% of wall clock inside them) and once on which tasks consume the
episode — and is **not supported either time.**

## 3. RETRACTED: "the turn cap is a random task-killer inside the normal distribution"

The variance claim was right; **the causal claim was wrong.** Deaths do not fall uniformly:

    AGGREGATION        18 of  26   69.2%
    UPSTREAM (prep)     5 of  93    5.4%
    SEGMENT (the DV)    2 of 176    1.1%

**They concentrate on tasks that must read nine upstream deliverables to answer at all** —
`Output floor check`, `Aggregate risk-weighted assets`, the reconciliation variants: 100%,
100%, 100%, 67%, 60%, 40%.

**The split cannot read any of them.** `split()` keys on `index.segment_task_ids`, a
`segment_id -> task_id` map, and the scorer scores a reported RWA against *that segment's*
truth. **An aggregation task carries no segment id, so it cannot enter the DV.** Verified in
the code, not inferred from the deaths.

**RR CONFIRMED THIS AND FOUND A STRONGER BASIS THAN MINE — the one I cited is the weakest of
three.** Mine is a property of how a completion is *classified*; RR's is a property of how it
is *collected*, one stage earlier:

- **The completion is dropped before it is ever a deliverable** (`run_finance_episode.py:445`).
  `task_to_segment.get(completion["task_id"])` returns None for an aggregation task and the
  loop `continue`s, so it never enters `allocation` or `deliverables` — it cannot reach
  `parse_segment_reports`, the scorer, or anything downstream of them.
- **The index is fixed at generation** (`finance_env.py:551-564`), one entry per instance
  segment, built before the episode runs. A manager-created task cannot join it — which is
  why the remediation `"Risk-weighted assets — seg_08 standardised recalculation"` sits in
  the board and not in the index.
- **The name path is retired.** All three analysis sites join on `task_id`, and there is no
  `task_name`/`startswith` use in `finance_gate.py` or `finance_quantities.py`. That was the
  route by which a remediation could have entered, and it is closed.

**And the one dying task that is upstream of every segment shows no measurable block — but
the comparison is a BOUND, not a null.** `Exposure data preparation` dies 5 of 26:

    prep DIED  n=3 bundles: mean 7.7 segment completions
    prep OK    n=20 bundles: mean 7.5 segment completions

**RR priced what that comparison could actually have seen**, using per-bundle segment
completions as the noise level (mean 7.78, SD 0.81, range 6-9):

    SE of the difference          0.50 segments
    smallest detectable (~80%)    1.40 segments
    observed difference           0.20 segments  = 0.40 SE

**So the correct sentence is: "no evidence of blocking; n=3, and the comparison could not
have detected a block of fewer than ~1.4 segments."** A block of one or two segments is
invisible to it. Written as a null it would read as *"prep death is harmless"*, which is not
what it says.

## 4. Consequence: the escalation is withdrawn, and `WORKER_MAX_TURNS` stays at 16

**I asked the researcher to decide whether to raise 16 → ~24. That question should not have
reached them.** Raising it would buy at most the 1.1% of segment runs that hit the cap, and
would spend the extra budget on the aggregation tasks — the slowest class, dying at 69%,
whose output nothing reads. **It is a cost with almost no measurement return.**

The codebase already contains this decision, made correctly once (`finance_env.py:456-465`):
five workers died on the cap while messaging each other, and the fix was to **rewrite the
tasks to be answerable from their own text, not to raise the budget.** The note ends: *"a
task whose completion requires unbounded coordination is not a reliable DAG node."* The
aggregation chain is that shape and cannot be made self-contained — aggregation needs the
parts.

**NOT ACTED ON, and deliberately.** Whether the aggregation chain should exist at all is a
real question — it would return ~10% of wall clock and remove 18 of 25 deaths — but it
changes the workflow the manager allocates over, and every committed bundle was collected
with it present. That is a comparability cost, not a cleanup. Raised, not taken.

## What this does NOT establish

- Nothing about effect size, and nothing about whether 259 s is a *reasonable* cost for a
  segment task. It says where the time goes and which deaths reach the measurement.
- The corpus mixes arrangements and two generator revisions. **The class-level split does
  not depend on that mixing; the per-task rates do**, so the 100% figures are small-n
  (2, 3, 4 runs) and should be read as "this class dies", not as per-task rates.
- The 2 segment deaths are both `seg_04`, one of which is the L19 contamination chain. A
  1.1% rate on n=176 carries no interval.
- **The prep-block result is a bound of ~1.4 segments, not a null.** See above.

## Which of the two corrections is the finding (RR)

**The 13-minute slip is housekeeping. The retraction in §3 is the result.** *"The turn cap is
a random task-killer inside the normal distribution"* was a **mechanism** claim, and
69% / 5.4% / 1.1% refutes it structurally: **deaths concentrate where the work is
unbounded-length, and the measured unit is the one they do not touch.**

**The withdrawal did not need the unreachability argument at all.** Two segment deaths in 176
runs is 1.1% — **even if aggregation deaths had been reachable, the segment population is
barely affected, so the recommendation to raise the cap fails on the rate alone.** The
unreachability finding makes it certain; the rate already made it right.

## Instrument-setting caveat added after this record was first written

The durations above **pool bundles run at different `concurrency` settings** (see
`records/L21/`). The two populations with usable n are close — median 78s (setting not
recorded, n=100) against 85s (N=2, n=184) — so **the 81s headline is not an artefact of the
mixing.** The tail statistics are less safe: the worst single bundle is the sole `N=1`
episode, so `max` and `p90` are partly a statement about that one episode.
