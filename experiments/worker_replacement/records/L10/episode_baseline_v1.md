# A healthy episode takes 40 minutes — and our own timeout would have broken every run we already hold

**Script: `experiments/worker_replacement/measure_episode_baseline.py`. Every number below is its
stdout. Reads committed bundles only; spends nothing.**

---

## The finding, first

**There was never a hang.** A healthy episode in this study takes a **median of 40.3 minutes**. The
three runs we diagnosed as hung were killed at **18, 20 and 10 minutes** — between a quarter and a
half of a normal episode. **None of them was ever going to produce a bundle in the time it was
allowed.**

**And the instrument we built to catch the hang would have caused one.** The 180-second request
timeout installed on 2026-08-08 **kills 29.3% of the worker runs that actually finished in the
committed corpus, and lands in 20 of the 20 episodes.** With `num_retries=2` behind it, each such
call burns 3 x 180s and then fails — so the fix plausibly made runs *slower*, and is a live
candidate for the failures it was installed to diagnose.

> **CORRECTED THREE TIMES, same day, and every correction is a POPULATION.
>
> **(iii) Too narrow a bundle set.** The first three versions globbed `records/R2/` only, silently
> excluding `records/S8/`. RE caught it. Widened to all committed bundles (20), with the two marked
> FAILED/INCOMPLETE excluded deliberately and in code — **pricing a timeout on a run that never
> finished justifies a higher bound from a failure**, and the one 1506 s worker run on disk is in
> `run_seed101_attempt5_INCOMPLETE.json`.
>
> **Two corrections below, in opposite directions.** Both corrections are the same mistake:
> nobody looked at the event fields.**
>
> **(i) Wrong population.** The first version said **7.1% in 13/18**, computed over **MANAGER** LLM
> calls — every `structured_llm_*` event carries `actor_type == 'manager'` and there are no worker
> LLM-call events at all — and used it to condemn a bound wrapping the **WORKER**'s `Runner.run`.
> RE re-derived independently, got 6.9%, and **agreed with me on the same wrong population**: the
> differ-test compares constructions, not populations. RR found the same manager-only fact
> independently.
>
> **(ii) Wrong pairing, then over-corrected.** FIFO pairing is unsafe where calls overlap — RR
> measured the overlap and was right (2 of 18 bundles for manager calls, **every episode for worker runs**).
> But RR's remedy, dropping the overlapping bundles, also drops their genuinely long calls and
> **understates the tail (p99 438 s against the exact 636 s)**. Neither remedy was needed:
> `structured_llm_*` carries `(actor_id, operation, timestep)` and `worker_execution_*` carries
> `(actor_id, task_id)`. **Both pair every bundle with zero unmatched and zero ambiguity.** All
> three of us had concluded no correlation id existed without inspecting an event.
>
> **The conclusion is unchanged throughout. Only the number moved, and it never moved below
> material.**

---

## Construction — this baseline transfers exactly

All 20 bundles: **`deepseek-v4-flash-0731` on both manager and worker, horizon 22**, concurrency 2
(14) or unset (6). Same model, same horizon, same shape as the runs we were killing.

**Transfer is "small, measured, bounded" — not "no caveat", which is how the first version put it.**
RR measured it rather than asserting it: correlation between call duration and prompt size is
**r = +0.035**, and a 1.7x spread in prompt size moves the median about 20%. The `partial`
arrangement keeps the same nine segments, roster and horizon, so prompt size should barely move.

## The measurements

| | median | p90 | p99 | max |
|---|---|---|---|---|
| **episode wall-clock** (n=20) | **40.3 min** | — | — | **83.0 min** |
| **silence between logged events, in episodes that SUCCEEDED** (n=3667) | 0 s | 40 s | 193 s | **715 s** |
| **WORKER runs that finished** (n=266) — *the population the worker bounds govern* | 81 s | 440 s | 904 s | **966 s** |
| MANAGER LLM calls that finished (n=436) — *not a worker population* | 40 s | 157 s | 554 s | 876 s |

Both paired on an exact correlation key with **zero unmatched events**, which is the check that the
key is a key. The script exits non-zero if any event goes unmatched rather than reporting a
silently thinned population.

**What each bound does to the population it actually governs (worker runs, n=266):**

    litellm.request_timeout = 180 s  kills  78/266  (29.3%)   in 20/20 episodes
    WORKER_RUN_BACKSTOP_S   = 630 s  kills  10/266  ( 3.8%)
    raised to        1200 s / 2460 s kills   0/266  ( 0.0%)    <- RE's replacement, 8e273ec

**A worker run that FAILED still belongs in this population**: the bound would have fired on it too.
Excluding them is not conservative — failed runs sit above 180 s at **55.6%** against 27.6% for
completed ones, so "successful runs only" understates the exposure, in the flattering direction.

Mean per timestep: **117 s**. First *task* completion (`worker_execution_completed`): median 1.1 min,
max 3.2 min.

**`completed=0` at timestep 0 is normal — it happens in every healthy episode.** RE flagged it as
the one fact surviving the retraction unexplained; **no episode in the corpus has ever completed a
task inside timestep 0.** Every bundle ran the full 22 timesteps.

*A first pass measured this with any event type containing "complet", which matches
`timestep_completed` — a boundary that fires whether or not anything completed. That number
(median 0.9 min) was about something else and is not used here.*

## What each piece of "evidence for a hang" actually was

| what we saw | what the corpus says it is |
|---|---|
| `[t00] completed=0` first appearing past 180 s | **normal** — happens in every healthy episode; first task completes at median 1.1 min |
| 48 bytes of output in 20 s; 96 bytes in 20 s | **normal** — the p99 silence in a *successful* episode is 193 s, the max 715 s |
| three runs producing no bundle in 10–20 min | **normal** — they were killed at 23–46% of a median episode |
| `WORKER_RUN_BACKSTOP_S` never firing (outcome 3) | **consistent with correct placement.** If no single wrapped call exceeds 630 s while the episode takes an hour, a backstop that never fires is what you expect. It is not evidence the bounds were in the wrong place. |

**Every observation we treated as positive evidence of a stall is inside the normal range of an
episode that succeeded.** Without a baseline, *slow* and *stopped* are the same observation — and
the baseline was in the record before the first run was launched.

## What the numbers say the bounds should be

- a request timeout must clear the healthy max **966 s** (worker runs) with margin
- a hang detector must clear the healthy max silence **715 s** with margin — and the **heartbeat, not
  the wall clock, is the correct kill signal**, because only progress distinguishes slow from stopped
- an episode kill threshold must clear the healthy max episode **83 min** with margin

**`WORKER_RUN_BACKSTOP_S = 630 s` sits below the longest silence in a successful episode (715 s,
`run_cell0_seed3.json`, between `structured_llm_request` and `structured_llm_response` — a single
model call of 11.9 minutes that returned and is in our committed results).**

## What this does NOT establish

It does not show the runs would have succeeded — only that they were killed too early to find out,
and that the bounds in place would have damaged them if they had continued. **It does not identify
any real defect in the model path.** The out-of-harness discriminator is now unmotivated: it was
built to test a stall hypothesis for which there is no longer any evidence.

The timeout work is not wasted — litellm's 6000-second default is a genuine divergence from
`llm_interface`'s 300, and the flushed heartbeat is what made this check interpretable. **The
threshold was wrong, not the instrument.**

## ★ The correction is the same failure class as the rule this record was written to establish

The rule committed alongside this record (622d121) says *"a figure is carried one step further than
the thing that justifies it."* **The first version of this record did exactly that, and so did RE's
independent re-derivation, within an hour of the rule being written.** A worker bound was condemned
with a manager number.

**Two agents computed it independently and agreed, and the agreement was worthless** — we differed
in pairing and were identical in population. **The differ-test compares constructions. It does not
compare populations, and it will pass on two wrong answers that are wrong the same way.**

**It then failed three more times on the same axis, each time between two agents who agreed:**
manager-vs-worker; all-bundles-vs-healthy-only (RE's 259 against 246); and R2-only-vs-all-records
(my 235 against 266) — the last declared "reconciled" across an 11-pair gap **in the message
diagnosing precisely that move.** RE's sentence is the one to carry: *"two independent derivations
of the wrong population is not corroboration."*

**The check that catches it is the one already in standing rule 5: name the population as a
PREDICATE, not a name.** "Model calls" is a name. `worker_execution_started -> completed|failed,
paired on (actor_id, task_id)` is a predicate, and writing it down is what surfaced both that
`structured_llm_*` is manager-only and that an exact key existed.

**★ And the deeper one: three agents independently concluded the events carried no correlation id,
and none of us printed an event.** RR wrote that exact pairing "needs a correlation id the events do
not carry"; I wrote the same in a docstring; RE paired positionally too. The fields were
`actor_id`, `operation`, `timestep`, `task_id` — visible in the first event of the first bundle.
**Three independent derivations reproduced one another's blind spot, because independence was in the
method and not in the input.** The corpus was read three times and inspected zero times.

## The pattern, stated once

This is the **third** time this phase that a check has been built without establishing what normal
looks like, and the second where the instrument would have manufactured the condition it was
looking for. The standing rule *"state a number's construction before building on it"* covers
figures in records; **180 s and 630 s were numbers in code, and nobody asked where they came from.**
They came from nowhere. **The rule applies to thresholds, not only to results.**

Responsibility is not RE's alone: the 45-minute kill threshold was mine and roughly right (it sits
just above the median); **I then endorsed tightening it to 10 minutes**, which is what made the
third run uninterpretable.
