# The worker stall — LS prediction, committed before RE measures anything

**Researcher-directed diagnosis. Written before any probe exists, so it cannot be claimed afterwards.**

## The observation

Same task type — price one loan slice — splits in two on the one `partial` episode:

    8 tasks   median 1.6 min   fastest 0.3 min    <- the real cost of the work
    7 tasks   median 24.5 min  slowest 36.0 min   <- the same work, stuck

**The 36-minute task COMPLETED and produced a correct, parseable answer.** It was not struggling.
Concurrency does not separate the groups: the 36-minute run had 4 alongside it, a 2.8-minute run
also had 4, and a 9.4-minute stall happened with nothing else running.

## The prediction

> **The stalls are ONE model request hanging until the 1200 s timeout, then a retry that completes in
> normal time.** 1200 s + ~1.6 min ≈ 22 min, and the observed slow group is 24.5 min median with a
> 36 min max — consistent, and bounded by the 2460 s backstop that never fired.

**Falsified by:** stalls that are NOT ~1200 s plus a short tail; stalls with no retry; or time
accumulating across many short tool round-trips rather than one long wait.

**The alternative I rate second:** the agent loop burns turns — `max_turns=16` on every task — with
each turn a real call. That predicts stalls in multiples of a call, not one long block.

## What the diagnosis must establish

1. **Where the time goes inside a stalled task** — one long request, or many short ones.
2. **Whether a retry occurred.** If the first attempt is ~1200 s the timeout is the proximate cause
   and the question becomes why the provider stalls.
3. **Provider-side or ours** — a stall that reproduces outside the harness is theirs; one that only
   happens inside is ours.

## What it must NOT do, and why this is stated first

**Three runs were once spent diagnosing a "hang" that was ordinary slowness, because no baseline
existed and every claim reasoned from ABSENCE — no bundle, no bytes, no bound firing.** So:

- **establish what a NORMAL call costs before calling anything abnormal**;
- **reason from presence** — a timestamp, a completed request — never from something not appearing;
- **no full episode.** The unit is a single worker task, repeated. Minutes, not hours;
- **name the revision measured against**, and do not measure against a moving tree.

## What it is worth

**If the stall is fixable, an episode is ~30 min rather than 103, and the authorised run drops from
~3.4 hours to under one.** Every run after it inherits the same factor. **That is why this runs
before the shakedown rather than after.**

---

# Opened against RE's prediction, and the data goes further than either

**RE's line: there is NO single stall population — the ≥20-minute cases are our own 1200 s bound
firing and retrying, the ~9-minute cases never reached it and are just slow, and what looks bimodal
is a slow tail with a SHELF our bound stamped into it.**

**Their arithmetic is what beat mine:** a 1200 s timeout **cannot** explain a 564 s task, so if the
whole stalled group were timeout+retry there would be a hard floor at 1200 s and nothing between 2
and 20 minutes.

## ★ And the split turns out to be exactly completed-vs-failed

    2160 s  36.0 min  COMPLETED   above 1200
    1787 s  29.8 min  COMPLETED   above 1200
    1609 s  26.8 min  COMPLETED   above 1200
    1467 s  24.5 min  COMPLETED   above 1200
    ---------------------------- 1200 s bound ----------------------------
    1040 s  17.3 min  FAILED      below -- no timeout fired
     607 s  10.1 min  FAILED      below
     564 s   9.4 min  FAILED      below
     177 s and under  COMPLETED   x8, the normal population

**All four above the bound completed. All three below it failed. Zero exceptions**, and the split
was not imposed — it falls out of sorting by duration.

**RE's version is right and the completed/failed alignment is stronger evidence for it than the 9.4
figure they built it on.** LS's prediction — *"one timeout plus a retry"* — is correct for four of
seven and **silent on the three that matter most.** Not revised; recorded as the weaker call.

## ★ Which changes the priority, and this is the addition

**The four long COMPLETED runs are EXPENSIVE BUT HARMLESS** — they finish, they parse, they score.

**The three FAILED runs are expensive AND DESTRUCTIVE**: they consume the run and produce nothing,
and **on this bundle a failed task created the only DV event recorded** (seg_04, which is the entire
DV=1). **If the diagnosis has to choose, the failures are the more valuable target.**

## Two constraints RE added, both adopted

**Scope of the bound, stated from the code BEFORE any timing is quoted.** Whether
`WORKER_REQUEST_TIMEOUT_S` wraps `Runner.run` or a single HTTP request **changes what 2160 s means**
— two attempts or many. RE: *"I have twice this week reasoned about a bound whose scope I assumed."*

**★ An instrument that changes the timing it reports is the failure mode here, and it is not
hypothetical: the fast population's whole cost is 1.6 minutes.** Wall-clock outside the call plus the
provider's own response metadata. **If the probe cannot stay outside the worker path, the measured
revision is `4b13339` + probe and must be named as such — never quoted as `4b13339`.**

---

# ★ ANSWERED: it is not over-engineering. It is one slow request.

**RE probed three segment tasks at `2ae0694` + probe, seed 42 cell 1, in isolation:**

    task     wall      requests   in-request   outside   longest single request
    seg_05   51.5 s       4        51.49 s     0.04 s        19.55 s
    seg_00  320.5 s       5       320.51 s     0.02 s       181.74 s
    seg_03   38.2 s       4        38.20 s     0.01 s        13.76 s

    turns: median 4, MAX 5 -- against a budget of 16
    time inside requests: 100.0% of wall clock

**TURN-BURNING IS EXCLUDED.** No run came near 16; the median is 4, exactly the *"handful of tool
calls"* the code's own comment predicted. **There is no turn overhead, no tool-execution time, no
retry backoff — nothing outside the calls at all.**

**THE COST IS ONE CALL. `seg_00` spent 181.74 s in a single request against a 10–13 s median.** The
slow task is not doing more work; **it is waiting longer on one call.** Provider-side latency
variance — and **the four long COMPLETED runs above 1200 s are our own per-request bound firing on
exactly this and retrying.**

**THE RESEARCHER'S HYPOTHESIS — that over-engineering causes the 13x blowup — IS NOT SUPPORTED BY THE
MEASUREMENT.** It was worth testing and the test is cheap and clean.

## ★ And the cut LS pressed for would have caused harm

`WORKER_MAX_TURNS` 16 → 4 **would kill `seg_00`, which legitimately used 5** — converting a
completing task into `MaxTurnsExceeded`, i.e. **moving work from the expensive-but-harmless
population into the expensive-AND-DESTRUCTIVE one LS had just told RE to prioritise.** → 6 is a
no-op. **A coin-flip between no effect and breaking the run.** RE declined and measured first.

**★ LS REASONED FROM A COMMENT, NOT A MEASUREMENT.** *"A worker that spends 16 turns is looping
rather than working"* is a hypothesis someone wrote beside a constant. **LS quoted it back as
evidence and pressed twice.** The comment describes what 16 turns WOULD mean, not what the workers
DO. **RE had the turn count; LS had a sentence.** The label-over-condition shape, committed by the
agent who has been cataloguing it all week.

## The dedup stands, and RE's self-correction is the useful part

RE first checked `create_ai_tools()` and found no duplicates — **not the path a worker takes.**
`worker_execution_started` records the real list on every run of both bundles: **8 entries, 3
repeated.** Fixed experiment-side, all five kept, **verified through to the SDK agent's own tool list
rather than `self.tools`** — fixing the record and not the model's choice set would have been a fix
that reports success and does nothing.

## An observation carried to the researcher, NOT a decision and NOT gating

**All eight worker tools are MESSAGING.** The registry passes `tools=[]`, so `create_ai_tools()` —
search, analyse, calculate, generate — **never reaches a worker.** A worker computing Basel RWA holds
nothing but ways to talk about it. **`calculate`'s absence is consistent with the calculator no-go and
is almost certainly deliberate; the other three are probably unnoticed.** RE's measurement says the
tool surface is not what costs the time, **so this is tidiness and it gates nothing.**

## Limits, RE's, carried

**Three tasks, run in ISOLATION** — no episode contention, no inbound messages, and **a worker that
receives messages might use more turns than one that cannot.** **And 320 s is not 24 minutes: the
full stall is NOT reproduced outside an episode.** So turn-burning is excluded **for these runs**,
and the 24-minute tasks are not yet shown to be the same animal. A 6-task widening is in flight; the
thing most wanted from it is **whether any run exceeds 5 turns when messages can arrive.**

---

# ★ The 6-task run: RE corrects their own maximum, and the decisive evidence is the same task costing different amounts

    task     wall       req   longest req   median req
    seg_05    35.53 s     3      15.22 s      14.82 s
    seg_00   149.02 s     3      92.69 s      31.03 s
    seg_03    20.38 s     3       9.51 s       7.72 s
    seg_07   438.92 s     8     305.14 s      16.36 s   <- slowest AND most turns
    seg_01   128.37 s     3      93.09 s      18.70 s
    seg_04    63.69 s     3      28.46 s      27.14 s

    turns: median 3, MAX 8.   100.0% inside requests, again.

**RE CORRECTED THEMSELVES: they reported MAX 5 from three runs; it is 8.** True of that sample, not
of the process. **A cap of 4–6 would now have killed TWO tasks** — seg_00 at 5 and seg_07 at 8.
**The hold LS confirmed is more strongly supported than when RE argued for it.**

## ★ Even the 8-turn task is a latency story, not a looping story

    seg_07   305.14 s of 438.92 s in ONE request  (70%)  -- its other 7 calls total ~134 s
    seg_01    93.09 s of 128.37 s                 (73%)
    seg_00    92.69 s of 149.02 s                 (62%)

**seg_07's median request is 16.36 s. It is not eight slow calls; it is seven normal ones and one
that took five minutes.**

## ★ THE DECISIVE EVIDENCE: the same task, same instance, same prompt, an hour apart

    seg_00   320.53 s / 5 req   ->   149.02 s / 3 req
    seg_03    38.21 s / 4 req   ->    20.38 s / 3 req
    seg_05    51.54 s / 4 req   ->    35.53 s / 3 req

**Every task got faster AND used fewer turns on the second run, with no code change between them.**
Nothing about the workflow explains that. **It is the provider.**

**AND THE CONSEQUENCE FOR EVERY DURATION FIGURE THIS PROJECT HAS QUOTED:** the 13-minute mean, RE's
96 s median, the 103-minute episode, and **the 3.4-hour run estimate LS gave the researcher are all
single draws from a wide, time-varying distribution.** RE: *"the spread is the finding, not the
centre."* **LS's sizing was one sample presented as a price.**

## What it now says, narrower than "not over-engineering"

**A worker does 3 calls for a segment, spends 100% of its time waiting on them, and occasionally one
call takes 5 minutes.** The 13-minute tasks are that plus our own 1200 s per-request bound firing and
retrying on the worst of them. **Nothing in the harness is looping, and there is no work to remove.**

## Turn variation is NOT driven by messaging

**8 turns occurred with NO messages seeded.** So a worker with an empty inbox still sometimes takes
8, and **the `--with-message` variant can only add turns on top of a spread that already exists** —
a smaller question than when LS asked it.

## Still not established, and repeated because it will be quoted

**Six tasks, one instance, in ISOLATION. 439 s is not 24 minutes** — the episode stall is still not
reproduced outside an episode. **Client-side timing cannot separate provider queuing from
generation.** The 96 s median is not "what a task costs".

---

# ★ ANSWERED PROPERLY: requests do not get slow — they HANG. A 1290-second gap proves it.

**Twelve completed worker runs in the committed episode, sorted:**

    18.6  38.0  60.5  93.1  94.2  125.1  167.8  176.9 | 1467.4  1608.7  1787.1  2160.4
                                                       ^
                                    NOTHING between 176.9 s and 1467.4 s

**Zero runs between 200 s and 1200 s.** A continuum would put several there. **It is bimodal: a
request either completes normally or it hangs until our bound kills it, and the retry then runs at
ordinary speed.**

**RE RETRACTED THEIR OWN PREDICTION on this evidence** — they had said *"a slow tail with a shelf our
bound stamped into it"*; a shelf on a continuum leaves runs between 200 s and 1200 s and **there are
none.** They reached the right HOLD decision from a wrong model of the process, and said so.

**THE PROBE AND THE EPISODE AGREE ON NORMAL WORK, which is what makes the comparison usable:**
episode 8 normal runs median **~93 s**; probe 6 isolated runs median **96 s**. **Within 3 seconds.**
Isolation reproduces normal work faithfully, and **the probe never triggered the bound** (longest
single request 305 s) — the hang is rare enough that six tasks missed it, which is also why the
24-minute stall could not be reproduced outside an episode.

## Two corrections, one each way

**LS produced a phantom 3343.1 s run while verifying RE's numbers** — paired `started`→`completed`
and **dropped `failed` from the closers**, so a failed run's start was consumed by a later
completion. **Same class as RE's `create_ai_tools()` check: verifying through a path the data does
not take.** LS's earlier careful pass reproduces RE's figures exactly.

**RE overstated: "all four remainders land inside the normal range (20–439 s)". Two do, two do not**
— 587.1 and 960.4 exceed 439. **It does not break the model** (a run makes ~3 requests and seg_07
took 439 s over 8, so a slower multi-request remainder reaching 960 s is ordinary) **but the two that
exceed are the two that most need explaining.**

## ★ RULED: `WORKER_REQUEST_TIMEOUT_S` 1200 s → 600 s

    longest observed LIVE worker request   305.14 s
    population                             ~20 requests over 6 tasks, ISOLATED, at 2ae0694 + probe
    600 s = 1.97x observed max; kills 0 observed live requests
    saves ~600 s per hang; 4 hangs in the one episode = ~40 min

**600 rather than RE's 480 because 305 s is six tasks and the live-request tail is unmeasured** —
600 doubles the observed maximum where 480 gives 57% margin on n≈20. **The extra 120 s costs 8
minutes across four hangs and buys real headroom.** Revisit if the widened probe raises the observed
maximum above 400 s.

**The downside is bounded and self-healing: a wrongly-killed live request is RETRIED, so being too
low costs one extra attempt rather than a lost task.** That asymmetry is why lowering is safe without
more probe runs first.

**AND THE 876 s JUSTIFICATION IS REPLACED IN THE SAME COMMIT, not left beside a corrected value.** It
came from `structured_llm_*` pairs — every one the MANAGER's. **A manager request/response pair
justifying a worker request timeout: the 180 s error, still live in the code until now.**

## Still open, and still the more valuable target

**Three runs started and never completed.** They are absent from the paired data entirely, **so the
gap analysis says nothing about them, and a shorter bound does not help a task that fails without
hanging.**

**And the method caveat that produced LS's phantom: durations are DERIVED from timestamps, not read
from a field.** The bundle records no duration. **A derived quantity is only as good as its pairing
rule, and the rule has to be stated.**

---

# ★ RETRACTION OF A COMMIT SUBJECT — `4b2e07e` announced a code change it did not contain

    git show --stat 4b2e07e
      records/L16/stall_prediction_LS.md | 66 ++++++++++++++++++++++
      1 file changed, 66 insertions(+)

**The subject reads "the bound drops 1200s -> 600s". The constant was still 1200 at that commit.**
One records file, no code. **The actual change is `c15cc39`.**

**This is the label-over-condition shape IN A COMMIT MESSAGE, which is the worst place for it: the
message is what a future reader greps, and `git log --oneline` would report the bound moving on a
commit where it did not.** Every earlier instance of this shape was a name in code that outlived its
condition; **this one was written by the agent cataloguing them, in the medium that is hardest to
re-derive from.**

**Found by RE only because their own `git add` aborted and they checked what had moved instead** —
*"otherwise I would have committed on top and we would have had two commits both claiming to have
made the change, with the diff in neither."*

**Not rewritten.** History rewriting is destructive and the repo rule is one branch committed
directly; **the retraction stays as a retraction, which is the standing rule.**

## Two claims RE corrected in the backstop comment, both consequences of the gap

- ***"with legitimate runs reaching 36 minutes"* — that run was NOT work.** It is 1200 s of hang plus
  a ~960 s retry. **The longest real work observed anywhere is 176.9 s in an episode and 438.9 s in
  isolation.** So the comment's conclusion — that no per-run bound separates slow from hung — **is far
  weaker than written: the populations sit either side of a 1290 s gap.** They looked inseparable
  **because the hang and the retry were being measured as one number.**
- ***"bounds a quantity we cannot observe … unverified"* — we can, and now have.** No BUNDLE prices
  it, because no event is emitted; **the provider layer does.**

## The pairing rule, kept as a rule rather than as an error

**A derived duration is only as good as its CLOSER SET, and the closer set must be stated with the
number.** LS's phantom 3343 s came from pairing `started`→`completed` while omitting `failed`, so a
failed start stayed open and was consumed by a later completion. **The bundle records no duration
field; every duration in this project is derived.**

---

# ★ TWO REVERSALS: the 600 s bound is wrong, and turn-burning is NOT excluded

## RR refuted the bound with a figure LS supplied in the same message

    hour-to-hour swing on ONE task   320/149 = 2.15x
    the margin LS set                600/305 = 1.97x
    a 305 s request in a bad hour    305 x 2.15 = 655 s   ->  a 600 s bound KILLS IT

**The variation LS measured EXCEEDS the margin LS set.** And the self-healing argument fails on
independence: **the retry runs seconds later in the same bad hour**, and with `WORKER_MAX_RETRIES = 1`
that is 1200 s consumed and **the task FAILS**, where the old single attempt would have completed at
~655 s. **The change can convert a slow success into a failure at identical cost** — moving work into
the destructive population, **the second time this week LS proposed exactly that.**

**RR also named the population bias: ~20 requests, 6 tasks, ISOLATED — no contention, no inbound
messages.** The real run has three workers and a manager against one provider. **Provider latency
under load is precisely where a tail lengthens, so 305 s is a LOWER BOUND on the production maximum,
not an estimate of it.** Thin and biased, in the direction that matters.

**REVISED TO 900 s.** Basis stated as the rule requires — **not the single-hour maximum, but that
maximum times the observed hour-to-hour swing**: 305 x 2.15 = 655 s plausible bad-hour edge; 900 s
clears it, kills nothing observed under either hour, still saves ~300 s per hang.

**RR's concession, kept because it separates two claims LS had fused: the GAP is real and is the
strong part of the case; the gap's LOCATION is not.** Twelve observations is thin for an emptiness
claim, and **the 2.15x swing is direct evidence that the fast mode's upper edge MOVES.**

## ★ RE retracted "turn-burning is excluded" — with a message in the inbox a worker hit 16, the cap

    no message    turns  3, 3, 3, 8, 3, 3      median 3
    with message  turns  4, 16, 6, 6           median 6, MAX 16 = max_turns

**seg_00 with a message: 529 s over SIXTEEN requests, longest single call 90 s.** Not a hang —
**many ordinary calls. Looping, exactly the mechanism LS proposed and RE reported as excluded.**

**RE's exclusion was an artefact of their own instrument:** an empty `CommunicationService` meant
`get_recent_messages` returned nothing, **so they measured a worker that COULD NOT be interrupted**
and reported the exclusion without the qualifier they had themselves written down.

**TWO EXPENSIVE MODES, MECHANICALLY DIFFERENT:**

    HANG       one request burns the whole bound producing nothing. The 1290 s gap. Bound fixes it.
    TURN-BURN  many ordinary requests, triggered by an INBOUND MESSAGE. Nothing fixes it.

## ★ AND THE STUDY CONSEQUENCE IS LARGER THAN EITHER BOUND

**Cells 3 and 4 are the ASK cells.** If one inbound message can drive a worker to the turn cap, those
cells are **mechanically more expensive and can hit a ceiling the others never touch** — a difference
between cells **arising from the harness rather than the manipulation, in exactly the cells where the
manipulation IS conversation.** **No bundle has ever shown it, because no ask cell has ever run.**

**AND THE DECIDING UNKNOWN: seg_00 used EXACTLY 16. Nobody knows whether it FINISHED on turn 16 or
was TRUNCATED at it** — the probe discards the output. **If workers in cells 3/4 are truncated
mid-computation, the ask channel is DEGRADED by the turn budget rather than measured. That is a
validity problem, not a cost one.**

**AUTHORISED: re-run the message-seeded probe capturing the worker's OUTPUT and the SDK stop reason,
~4 tasks.** Small spend, decisive.

**`WORKER_MAX_TURNS` HELD, and the answer is no longer the cut LS originally pressed for: lowering to
4–6 would truncate the ask cells hardest — the opposite of what is wanted.** If truncation is
confirmed, RAISE for the ask cells or accept and record a binding cap; **either is a design decision
for the researcher.**

## ★ AND THE CORRECTION RR RATES LARGEST, which is not a threshold at all

LS wrote: *"every duration this project has quoted — including my 3.4-hour run estimate to the
researcher — is one draw from a wide distribution presented as a price."* **RR: that is the
plausible-range rule applied to time, and it landed on a number given to the researcher as a
commitment.** **A schedule quoted without its range is the same defect as a ceiling quoted without
its interval** — and this project spent two days insisting on the second. **Corrected to the
researcher explicitly rather than left standing.**

---

# ★ THE THREE FAILURES ARE EXPLAINED — from the bundle, at zero cost. And the 1290 s gap is CORRECTED.

**`worker_execution_failed` carries `error_type` and a traceback and has done all along. Nobody
looked.** Verified independently by LS:

      seconds  outcome     error_type            detail
       18.6 – 176.9  completed  x8               normal work
        564.1  FAILED    MaxTurnsExceeded        "Max turns (16) exceeded"
        607.4  FAILED    APIConnectionError      litellm / OpenrouterException
       1040.3  FAILED    APIConnectionError      litellm / OpenrouterException
     1467.4 – 2160.4  completed  x4              hang + our bound + retry

## ★ RE CORRECTED THEIR OWN HEADLINE, and it is the same fault as LS's phantom

**RE reported "ZERO runs between 200 s and 1200 s — a 1290 s gap". The gap is real ONLY IN THE
COMPLETED POPULATION. The three failures sit at 564, 607 and 1040 — squarely inside it.**

**They built it by pairing with `worker_execution_completed` alone — precisely the dropped-closer
error that produced LS's phantom 3343 s run.** RE: *"Yours created a run that never happened; mine
created a gap that is not there."* **Twice in one day, in opposite directions, from the same missing
closer.**

**The completed-run durations survive unchanged** — all twelve verified against the correct pairing.
**But *"requests do not get slow, they hang"* was stated over the whole distribution and is true only
of runs that finished.**

## Two error types, two different problems

**`APIConnectionError` — a JSON decode failure on the provider's response body** (*"Expecting value:
line 485 column 1"*). The stream ended mid-document. **Two of three failures, and litellm's one retry
saved neither.** Plausibly the hang's other face: **one variant stops sending and we wait; the other
sends a truncated body and we fail to parse it.**

**★ `MaxTurnsExceeded` AT 564 s — IN CELL 0, WITH NO ASK CHANNEL.** So **turn-burning happens in
production without any messaging manipulation.** RE's no-message probe (3 turns over six tasks) did
not reproduce it and **would have led them to deny it.** It is also the phenomenon behind the comment
that started this whole thread — *"lost five executions to MaxTurnsExceeded"* — **still happening,
now once per episode.**

## ★ WHICH SETTLES THE `max_turns` DIRECTION, AND IT IS THE OPPOSITE OF LS'S ORIGINAL PROPOSAL

**The cap is REACHED AND FATAL in the plainest cell we have. Lowering it makes that more frequent,
and the cost of the cap is a LOST TASK, not a slow one.** The ask cells have not run, and a seeded
message already drove 16 requests there.

**LS proposed cutting 16 → 4–6 three times.** First it was argued from a comment rather than a
measurement; then it would have killed two tasks that legitimately used 5 and 8; **now it is clear it
would multiply the one failure mode that destroys work.** **On this evidence the direction is RAISE
or make it cell-aware — a design decision, and it goes to the researcher.**

## Unreconciled, and RE will not claim otherwise

**16 REQUESTS is not established to equal 16 TURNS.** The probe counts requests; the SDK counts
turns; the episode shows the SDK raising at 16 while the probe's 16-request run returned cleanly.
**Two facts not yet reconciled.**

## The rule this has now cost three errors in one day

**A derived quantity is only as good as its CLOSER SET, and the closer set must be stated with the
number.** LS's phantom run, RE's phantom gap, and the original completed-only pairing. **The bundle
records no duration field: every duration in this project is derived.**

---

# ★ DIAGNOSIS CLOSED. Four modes, one fixed, and the turn cap is a COST decision — not a validity one

## No silent truncation. The cap RAISES.

    seg_05    6 req   DECLINED in the permitted form
    seg_00   12 req   rwa 19,297,000.00
    seg_03    7 req   rwa 96,013,415.18
    seg_07    3 req   rwa 125,155,592.64        4/4 scoreable, max 12 turns

**And the episode settles it more firmly than the probe could: `MaxTurnsExceeded` is an EXCEPTION
with a traceback, not a quiet cut-off.** A worker at the budget **loses the task outright; it never
returns a half-finished report that scores as a good one.** **Loud failures are recoverable — that is
the validity question closed.**

*(The 16- and 17-character outputs looked alarming and are not: a bare `rwa: 96013415.18` line is 16
characters. Terse, valid, scoreable.)*

## The four modes, complete

    normal work          <= 177 s episode, <= 439 s isolated
    turn-burn            MaxTurnsExceeded, 564 s, CELL 0 -- NO messaging needed
    provider malformed   APIConnectionError, JSON decode on a truncated body, 607 s and 1040 s
    hang                 one request burns the bound, then a normal retry, 1467-2160 s   FIXED

**Only the hang is fixed. Two of the remaining three are provider behaviour we cannot fix from here,
only bound.**

## ★ THE TURN CAP IS INSIDE THE NORMAL DISTRIBUTION, NOT ABOVE IT

**Same task, same seeded message, two runs: 16 requests / 529 s, then 12 requests / 376 s.** **Turn
count is not a stable property of a task.** Observed range across all probes: **3 to 16.**

**A cap of 16 therefore sits at the top of ordinary variation rather than clear of it.** That is not
a safety limit — **it is a random task-killer that fires roughly once per episode**, and each firing
destroys a segment.

**LS RECOMMENDS RAISING IT UNIFORMLY (16 -> ~24), NOT MAKING IT CELL-AWARE.** A per-cell budget would
introduce a harness-induced difference between cells **in exactly the cells where the manipulation is
conversation** — the confound RE identified. **A uniform cap clear of normal variation treats every
cell the same and costs only the wall clock of a genuinely runaway worker.** Researcher's call.

## RE's two self-flagged limits, both kept

**The declined segment is a PROBE ARTEFACT, not a finding.** RE's seeded message asked *"are you
approved to use the IRB model for this segment's asset class, or will you be falling back?"* — **and
the worker then declined to price it.** Plausibly the wording leading it. **Not to be read as
"messaging induces declines" on n=1 with a question RE wrote.**

**REQUESTS ARE NOT ESTABLISHED TO BE TURNS.** The probe counts litellm requests; the SDK counts turns
on its own counter and raises there. **An earlier run hit 16 REQUESTS and returned cleanly; the
episode raised at 16 TURNS.** Both true, unreconciled. **"16 requests" is not evidence the cap was
reached.**

## Open for RE to check, not asserted here

**A `MaxTurnsExceeded` loss executed but never completed, so `finance_split` classifies it by the
refusal path — plausibly `unexecuted_no_refusal`, whose predicate reads *"the horizon ended first, or
it never became ready"*.** If so, **a turn-cap death is filed as a BUDGET/HORIZON problem, which is
false**, and the five-bucket split would mis-attribute the one loss per episode. **Worth checking
before any bundle is read.**
