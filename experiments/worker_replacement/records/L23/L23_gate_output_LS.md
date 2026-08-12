# L23 — first bundle: three gates GREEN, all nine segments measured, all three predictions MISSED

**Every segment produced a readable report, every provenance gate passed, and nobody predicted
the outcome.** `records/L23/run_cell0_seed42.json`, cell 0, seed 42, 90.2 min.

---

## Gate 3 first, because nothing may be read before the split speaks

    DV              0   -
    MANIPULATION    0   -  [UNINFORMATIVE]
    BUDGET_HORIZON  0   -
    DEFECT          0   -
    MEASUREMENT     9   executed_and_parsed=9
    9 segments. residual 0. NOT summed and no rate reported.

**All nine segments executed and parsed.** `n_parsed 9, n_missing 0, n_declined 0,
n_unreadable 0, n_unstaffed 0` from the runner independently.

## Gate 1 — code provenance: PASS

    rev          16362c503b8e9ebb25f3e0cf1ad688a9bb293e0f   == the pinned revision
    dirty        false
    dirty_paths  (none)
    captured_at  run_start

**Printed per path rather than summarised, as agreed — there are none, and no FOREIGN path.**

**★ AND IT SETTLES THE ARGUMENT RE AND LS HAD ABOUT IT — AGAINST BOTH OF US.** LS predicted
`dirty: false` from the code ordering; **the supporting evidence (a directory's mtime read as its
creation time) was invalid.** RE predicted `dirty: true` because their shell `mkdir -p` preceded
python; **the bundle says the tree was clean at capture, so the directory did not exist yet.**

**LS's conclusion was right and LS's reasoning was not. That is not vindication and is recorded
as not being vindication** — the standing lesson holds exactly as RR stated it: **a
better-argued guess about what the bundle says is still a guess, and the bundle settled it in one
read.**

## Gate 2 — selection provenance: PASS

    check                   stamped_hash          <- NOT the rebuild fallback
    checks_generator_drift  true
    matches_selection       true
    instance_sha256         ef25aa9dc76f0fd5a8d53a7b0f9f1c1f6d8b6c9f370f57b79c5eb720c145ba9a
    selection_record        environment_selection_v3.json
    caveat                  null

**The chain closes end to end: the hash stamped at approval time is the hash the episode ran**,
and the guard compared against the stored value rather than re-deriving it. **This is the first
episode in the study whose environment provenance is checkable rather than asserted.**

## The prediction protocol: three misses

    LS  largest non-MEASUREMENT bucket = BUDGET_HORIZON   MISS
    RE  largest non-MEASUREMENT bucket = DV               MISS
    RR  largest non-MEASUREMENT bucket = DV               MISS

**Every non-MEASUREMENT bucket is zero, so there is no largest — the instrument reports a
four-way tie and scores all three as misses, which is correct.** Nobody predicted a clean sweep.

**The MANIPULATION predictions (0 / 0 / 0) are VOID, not correct** — `refused_unavailable`
cannot fire in this harness, so the quantity could not have come out otherwise. **A prediction
about a quantity that cannot vary is not a prediction.**

## The ending was the pre-declared one, and slightly better

    worker_execution_failed:  MaxTurnsExceeded x2       both AGGREGATION
    final board:              15 of 16 complete, 1 task left `ready` (never ran)

**Pre-classified as normal BEFORE it happened**, on RE's injection test with a control that could
actually fire. **Establishing that afterwards would have been indistinguishable from explaining
away.**

**RE's refinement is adopted for episodes 2-4:** a missing segment because it FAILED
(`started_and_failed`, DEFECT) is a stop-and-diagnose; a missing segment because the HORIZON
ended (`unexecuted_no_refusal`, BUDGET_HORIZON) is a **recorded limitation of a 22-timestep
horizon, not a defect.** Moot here — all nine ran — and on the record before an episode needs it.

## Harness numbers, with their populations

    episode wall clock   90.2 min     NEW MAXIMUM (previous 83.0 among FINISHERS)
    worker runs          n=17   median 487s   max 1293s
    over 966s            2      <- exceeds every worker run in the prior corpus
    over the 2460s backstop  0  (margin +47%, was +155%)

**The 966 s and 83 min figures are both conditioned on success** — they describe episodes that
finished, so they are floors on what health looks like, not ceilings. **This episode becomes the
new maximum rather than an anomaly against it.**

**`agent_available` is now present on 0 events.** The decorative field is gone rather than
constant.

## What this does NOT establish

- **Nothing about the channel question.** This is **cell 0 alone** — the information-absent
  control. It has no cell 1 beside it and one episode carries no interval.
- **The `achieved` / `oracle_capacitated` ratio is NOT reported here and should not be quoted.**
  The oracle is priced at cap 3 while the runtime enforces no capacity — the exact mismatch L14-b
  removed. Comparing them would reintroduce it.
- A clean sweep on one bundle does not establish the harness is sound in general; it establishes
  that **this** episode's segments all ran and parsed.
- The prior for comparison is a single shipped splittable bundle whose DV of 0 is partly
  structural, so **"matches the prior" is not replication** and is not claimed.
