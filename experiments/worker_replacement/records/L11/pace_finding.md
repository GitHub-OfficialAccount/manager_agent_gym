# The runs were never hung. They were SLOW, and my bounds were too short.

**Construction path:** `run_episode(seed=26, cell="0", lattice="partial",
shared_class_segments=1, concurrency=1, dry_run=False)`, all six roles on
`openrouter/deepseek/deepseek-v4-flash-0731`, tracing disabled, heartbeat and
`faulthandler.dump_traceback_later(90s)` armed.

## The evidence that settled it

    --- 90s ---
    --- 90s ---
    [t00] completed=0 +0 this step
    --- 90s ---
    [t01] completed=0 +3 this step
    --- 90s ---
    --- 90s ---
    [t02] completed=3 +1 this step
    --- 90s ---

**Tasks are completing** — `+3` at t01, `+1` at t02, four of sixteen done. Forward
progress is not in doubt.

    ~180 s per timestep
    22 timesteps  ->  ~66 minutes per episode
    my bounds were  10 and 20 minutes

## What this retracts

**I called three runs "hung" and killed all three.** They were killed at roughly
timestep 3 to 6 of 22. **None of them was ever going to produce a bundle in the
time I allowed**, and "no bundle after 20 minutes" is the *expected* appearance of
a working episode at this pace, not evidence of a stall.

Retracted specifically:

* *"the run was hung, not slow"* — wrong;
* *"the hang is in the model path"* — there was no hang to locate;
* *"outcome 3: neither bound fired, so the fix was placed where the hang is not"* —
  the bounds did not fire because **there was nothing for them to catch**. The
  reasoning was valid and the premise was false.

## What survives

* **litellm's `request_timeout` default of 6000 s is still wrong**, and the
  manager/worker path asymmetry is still real. A bound that never fires costs
  nothing, and it will contain a genuine stall if one ever happens.
* **The instruments are the finding.** The heartbeat is what produced this; without
  it, "slow" and "hung" are the same artefact — nothing. Both were cheap and both
  were built after a question turned out to be unanswerable by construction.
* **`completed=0` in timestep 0** is real and unexplained by pace: the first
  timestep completed no tasks at all.

## The methodological point, which is mine to have missed

**Every diagnostic claim I made about these runs reasoned from ABSENCE** — no
bundle, no bytes, no bound firing. **The heartbeat is the first thing that reasoned
from PRESENCE, and it reversed the conclusion immediately.** An absence is
consistent with many worlds; a `+3` is consistent with one.

## What it does NOT establish

Whether ~180 s/timestep is normal for this model and prompt size, or itself
pathological. That needs the out-of-harness sequential probe, which is built and
unrun. **A 66-minute episode is feasible; six of them in parallel under contention
is a different question and is not answered here.**
