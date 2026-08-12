# The five-bucket split has never been computed, and no existing bundle can ever support it

**Script: `experiments/worker_replacement/five_bucket_split.py`. Every number here is its stdout.
Reads committed bundles only; spends nothing.**

---

## The finding, first

**None of the 20 committed bundles can be five-bucket split — not "not yet", but never.** Every one
predates the structured refusal-code fix, so `finance_split` refuses them by design:

> *"this bundle predates the structured-code fix and its refusal causes are not recoverable —
> classifying by substring over the prose is how an availability refusal came to be recorded as a
> concurrency one."*

**The refusal CAUSES are absent from the record, not merely unparsed.** No re-analysis recovers them.

**So the episode running now will produce the first five-bucket split in the study's history**, and
there is no prior to compare it against. Its engine does emit `refusal_codes`
(`core/execution/engine.py:916`, and that commit is an ancestor of HEAD — checked, not assumed).

## Why this was worth a firing

The mapping decides whether an incomplete segment is **the thing we measure**, **the thing we did to
the workflow**, or **a property of the harness**. It was settled in the L2a ruling and until now
**lived only in prose** — in the cron prompt and the backlog. Prose is not an instrument, and a
mapping chosen after seeing the counts is a choice about the answer.

It is now code, built before the bundle it will be applied to exists.

    DV              never_assigned, refused_allotment, executed_and_declined
    MANIPULATION    refused_unavailable
    BUDGET_HORIZON  refused_concurrency, unexecuted_no_refusal
    DEFECT          executed_but_unparseable
    MEASUREMENT     executed_and_parsed

`refused_unavailable` sits alone in MANIPULATION because **the roster change causes it** — pooling
it with removable noise, which the superseded two-way ruling did, would have deleted the
manipulation's own footprint from the measurement.

**The output never sums the buckets and reports no non-completion rate.** They answer different
questions; a total over them is a number with no population. `total` appears nowhere in the output.

## Controls, shown firing before the pass was trusted

The partition check was broken three ways and raised each time:

    a state dropped from the mapping   -> "unmapped: ['executed_but_unparseable']"
    a state placed in two buckets      -> "states in more than one bucket: ['executed_and_parsed']"
    an invented state name             -> "invented: ['made_up']"
    restored                           -> passes

A bucket also **inherits its states' non-interpretability**: `finance_split` can declare a state's
predicate unsupported for a bundle, and without this the flag would be lost the moment it was
aggregated.

## What this does NOT establish

It says nothing about what the split will show. It does not revisit the **69%-of-variance**
non-completion figure, which is a shortfall-SD decomposition across bundles and **was never a
five-bucket result** — it could not have been. That figure already carries RR's limitation in the
record (*"the decomposition transfers, the absolute numbers do not"*), and this finding adds one
more, **and RR checked it and made it stronger than I wrote it**: there is no assignment record
either. `task_assigned` occurs **0 times** in the corpus (verified independently; `finance_split`
reads exactly that event at line 160), and all 623 `assignment_deferred` payloads carry only
`task_id`, `agent_id`, `timestep` and the three concurrency fields.

**So it is not merely the refusal CAUSES that are missing — the CAUSAL STRUCTURE is.** Even the
coarse `never_assigned` vs `assigned-then-refused` distinction is unrecoverable, because nothing in
those bundles records that a segment was ever assigned. **No reanalysis of them decomposes
non-completion at any granularity.**

**RETRACTED IN PLACE:** an earlier version of this record said `never removed` is *"a bundle-level
condition asserted by the runner"*. **RR, who wrote the annotation, corrected the referent: it is a
HANDLING DIRECTIVE on the MANIPULATION bucket** — *this bucket must never be discarded as noise* —
already discharged in full by `BUCKET_MEANS["MANIPULATION"]`. Keeping it out of the partition was
right; the reason was wrong, and the wrong reason **manufactured an obligation** — it would have
sent a future reader looking for a runner assertion nobody ever intended to write. The prose-only
list is deleted.

## Grounding for the prediction protocol

What the corpus *can* still answer, over the same 20 bundles (9 segments each):

    n_parsed     median 7.5   range 6-9
    n_missing    median 1.5   range 0-3
    n_unstaffed  median 1.0   range 0-3
    mean incomplete per episode  2.6 of 9      17/20 bundles have at least one missing

**This is the coarse shape only.** It says roughly a quarter of segments end incomplete and says
nothing about which bucket they belong to — which is exactly the gap the running episode closes.

## ★ My prediction, committed before asking RE or RR and before the bundle exists

**On the running episode (seed 26, `partial`/segs=1, one cell, horizon 22, 9 segments):**

> **BUDGET_HORIZON will be the largest non-MEASUREMENT bucket, and MANIPULATION
> (`refused_unavailable`) will be 0 or 1 — too small to carry the study's DV on a single episode.**

Reasoning, stated so it can be wrong for a nameable reason: capacity binds exactly (9 segments,
3 workers x cap 3), so there is no slack to absorb a late assignment, and the corpus already shows
a median of 1.0 unstaffed and 1.5 missing per episode with 17 of 20 episodes carrying at least one.
Those are budget/horizon shapes, not judgement shapes. `refused_unavailable` needs the manager to
actually assign to the departed worker *after* the swap — one decision, not a distribution.

**What would falsify it:** MANIPULATION at 2+, or DV (`never_assigned` + `refused_allotment` +
`executed_and_declined`) exceeding BUDGET_HORIZON.

**What it means if I am right:** a single episode cannot price the DV, and the feasibility verdict
should say the split is *readable* while declining to give a rate — consistent with the standing
ruling that this run's sigma sizes nothing.

---

# The comparison — all three predictions, opened together

| | largest bucket excluding MEASUREMENT | MANIPULATION (`refused_unavailable`) |
|---|---|---|
| **LS** | **BUDGET_HORIZON** | 0 or 1 |
| **RE** | **DV**, via `refused_allotment` | 0 |
| **RR** | **DV**, via `refused_allotment` | 0 (MEASUREMENT 5–7, DV 2–4, BUDGET 0–1) |

**We diverge on the largest bucket — LS against both peers — and agree on MANIPULATION.**

## On the divergence: my peers are right and I predicted a cause from a number that cannot express one

Capacity binds exactly (9 segments, 3 workers x cap 3, zero slack), and the segment allotment
**never releases within an episode**, so any uneven allocation is permanently barred. I grounded my
prediction on `n_unstaffed` median 1.0 and `n_missing` median 1.5 — **outcome counts that do not
distinguish cause, which is the entire thing this instrument exists to fix.** I used a coarse number
to predict a fine one.

**The prediction stands as committed and is not revised.** I expect to be wrong, and saying so
before the outcome costs nothing and is worth recording.

## ★ On the agreement: all three of us predicted MANIPULATION ≈ 0 from a corpus that could not have shown otherwise

`refused_allotment` was established in the scope run by **elimination over numeric fields** —
`available=True` rules out unavailable, `count=0 < max=1` rules out concurrency, therefore allotment
(335 / 245 over the R2 bundles). That is a sounder basis than substring-over-prose, and it has one
load-bearing assumption. Measured:

    deferral events carrying agent_available     623
      (count=0, max=1, available=True)           349
      (count=1, max=1, available=True)           274
      agent_available == False, EVER              0

**`agent_available` is True on every deferral in the entire corpus and never takes the other value.
The step that "rules out unavailable" can rule out nothing.** Two readings are indistinguishable
there: no unavailable refusal ever occurred, or unavailable refusals were being counted as
allotment. **A field that never varies cannot discriminate.**

**So the 335 attributed to allotment is an upper bound that may contain the manipulation's own
signature**, and every one of us — including both peers who cited that evidence — predicted
MANIPULATION ≈ 0 from a corpus in which MANIPULATION was structurally unobservable.

**This is what the experiment adds beyond confirmation, and it is the reason not to shrink it to a
smoke test:** it is the first observation capable of falsifying a belief all three of us hold for a
reason that is not evidence. RR named the possibility unprompted — *"a non-zero MANIPULATION would
not mean behaviour changed; it would mean we can finally see something that was always there"* — and
had one detail the other way: RR expected the lost refusals to have been logged as **concurrency**,
while the elimination table puts them in **allotment**. It matters, because it names which bucket is
contaminated, and it is the bucket both peers predict will be largest.

**Third instance today of the same shape** — independence in the method, not in the input.


## Known pooling inside DV, recorded on RR's objection rather than carried silently

`executed_and_declined` is one state covering two causes that belong in different buckets: a decline
in a class the assignee does **not** cover is a **manager mis-assignment** (DV, correctly); a decline
in a class it **does** cover is the **worker's own judgement** and is not an allocation outcome.

**It stays in DV** — the first case is what the study is about and declines should be rare — **and
the pooling is named in the code (`KNOWN_POOLING`) so nobody rediscovers it as a surprise.** The
discriminator already exists (was the assignee covered for that class), so it splits the moment a
bundle shows an in-coverage decline. **First bundle carries that check.**

This is the same pooling defect the five-bucket ruling was written to remove, one level down, inside
a single state — and RR proposed the mapping, so it is neither of ours alone.
