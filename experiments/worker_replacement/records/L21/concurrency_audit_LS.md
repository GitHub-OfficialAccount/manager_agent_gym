# L21 — The four episodes that ran at a different setting are exactly the four whose bundles cannot say so

**`concurrency` is recorded per bundle, and the corpus mixes settings — but the mixing does
not move the L20 headline, and my prediction that parallelism costs reliability is not
supported.** Held at **N=2** for the shakedown, recorded, no probe spend.

Raised by RE, who reported the corpus as *"`concurrency=2` on some bundles and `None` on
others"*. That is close but not the shape of it.

---

## 0. My own near-miss, first

I read `metadata` and got **"field absent from all 23 bundles"**, which would have been
reported as a recording gap. **It is written to `manifest`.** Wrong key, not a missing
quantity — *absence of a FIELD is not absence of the QUANTITY*, and I nearly demonstrated the
rule by breaking it. Caught by reading the write site rather than trusting the read.

## 1. The audit

    concurrency   bundles  runs   median      p90      max   fail%   cap%
    <<ABSENT>>          8    100      78s     403s    1506s   11.0%  11.0%
    1                   1     15     177s    1787s    2160s   20.0%   6.7%
    2                  14    184      85s     467s     966s    7.6%   7.1%

**PREDICTION, committed publicly before measuring: parallel bundles would show a longer tail
and more provider-side failures, since everything expensive we found is provider-side.**

**IT FAILED.** `N=2` has the **lowest** failure rate and the **lowest** maximum of the three
groups. RE's caution — that raising concurrency could worsen the provider-side modes — is
**not supported by the corpus**, and neither is my version of it.

**It is also not refuted, and the design is why.** The `N=1` group is a single bundle, and it
is the known-pathological one (`R3/run_cell0_seed26`, the 2160 s hang). Setting is confounded
with study step, arrangement, code revision, and calendar hour — **and we have already
measured a 2.15x hour-to-hour swing on one task**, which is larger than any difference here.
**This is observational, not an experiment.**

## 2. Where the mixing actually is

    cell 0    {N=2: 2, absent: 1, N=1: 1}   VARIES
    cell 1    {N=2: 2, absent: 1}           VARIES
    cell 2    {N=2: 2, absent: 1}           VARIES
    cell 3    {N=2: 3}
    cell 4    {N=2: 3}
    cell U    {N=2: 2, absent: 1}           VARIES

Every `absent` bundle in R2 is a **seed-3** bundle, and the field was added after they ran.

**So the comment at `run_finance_episode.py:515` asserts what the artefacts cannot: *"the
first four scope episodes ran at N=4 and the remaining fourteen at N=2"*.** No bundle records
N=4. **The comment sets the condition itself — "auditable per bundle rather than remembered"
— and that condition is unmet for exactly the four bundles the comment is about.** The
setting for those four is remembered, which is the state the comment was written to prevent.

**Consequence for R2:** cells 3 and 4 are internally uniform; cells 0, 1, 2 and U each carry
one episode at an unrecorded setting. R2 is the exploratory scope run and was already flagged
as such, so this is a recorded limitation, not a retraction of anything R2 produced.

## 3. Consequence for L20

L20's durations pool all of this. **The headline survives**: the two groups with usable n are
median **78 s** (absent, n=100) and **85 s** (N=2, n=184). The 81 s corpus median is not an
artefact of the mixing.

**The tail statistics are weaker than L20 presented them.** The corpus `max` (2160 s) and part
of the `p90` come from the sole `N=1` bundle, so they are partly a statement about one
episode. Noted in the L20 record.

## 4. Decision — held at N=2, and RE's probe is not worth its cost

**Instrument settings must be constant across cells for a powered study.** For the shakedown:
**`concurrency=2`, recorded in every bundle.** It is the setting with by far the most data
(184 runs), the lowest observed failure rate, and it needs no new evidence to justify.

**RE offered a sequential-vs-parallel probe on four tasks, comparing failure counts.** Not
taken:

- The corpus already gives **weak evidence against** the concern the probe would test, so a
  confirming result adds little and a contradicting result on n=4 tasks would not overturn
  184 runs.
- The provider swing (2.15x) is larger than the effect the probe is looking for, so a
  four-task probe run at one hour cannot separate setting from hour.
- **The shakedown itself produces the clean data.** Same setting throughout, recorded per
  bundle — if `started_and_failed` rises we have the field to check it against.

**This is a preference-level call, not a validity one.** If RE thinks the probe answers
something the shakedown will not, it goes on the record and the work proceeds.

## What this does NOT establish

- **Nothing about whether higher concurrency is safe.** The three groups differ on more than
  the setting, and the group that would inform it (`N=4`) is not recorded anywhere.
- Nothing about run *duration* under concurrency: the wall clock of an episode is not the sum
  of its worker runs, and this record only measured worker runs.
- The `N=1` row is one bundle. It should not be read as "sequential is worse".
