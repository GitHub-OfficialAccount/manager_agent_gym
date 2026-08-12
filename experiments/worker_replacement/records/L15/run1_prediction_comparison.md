# Run 1 — all three predictions, opened together

All committed before any episode exists; LS's before either peer was asked.

| | direction | detectable on a few episodes? | the sharp half |
|---|---|---|---|
| **LS** | cell 1 routes ≥1 loan to the successor that cell 0 does not, in a class it truly covers | not stated | the routing observation itself |
| **RE** | cell 1 ≥ cell 0 in mean score; routing difference visible before score difference | **no** — effect lives on 2–3 loans | **cell 0's between-episode VARIANCE exceeds cell 1's** |
| **RR** | cell 1 better in direction | **no** — sampling noise exceeds the whole effect | **the difference is FRONT-LOADED and shrinks over the episode** |

**All three agree on direction. All three of the sharp halves are different quantities** — a routing
event (LS), a spread (RE), a time profile (RR) — **so the run can separate them.** That is the
condition the protocol exists to produce.

**LS's is the weakest.** It predicts an event that a single well-chosen allocation satisfies, and it
says nothing about detectability. RE's and RR's both stake a claim that can be wrong.

---

## ★ RR's finding, verified at source, and it changes what a NULL means

**Cell 0 is not information-free after the first completed segment.** `InspectTaskAction` is
documented as *"Review a specific task's status and outputs … will return a summary of the task's
status and the outputs"*, and a completed report carries `method: IRB` or `method: SA` for a known
asset class. **A manager that inspects a finished segment learns whether the successor is approved
for that class.**

That is channel C2 (by-product self-description) operating **inside the cell that is supposed to have
nothing**. It is available in every cell because `inspect_task` is a core tool, and **removing it
would violate the standing rule that a worker's — or manager's — core tools are never disabled.**

**CONSEQUENCE: a null in cell 1 − cell 0 is AMBIGUOUS.** It is consistent with
*"the registry entry is worthless"* **and** with *"the report route substituted for it"*, and those
are different findings.

**THE DISCRIMINATOR IS TIMING, and it costs nothing to record.** The registry entry is available at
**t=0**; the report route only **after the first completion** (median 1.1 min, never inside timestep
0 across 18 healthy episodes). **So a card effect is front-loaded and a report-substitution effect
cannot be.** RR's sharp half and this discriminator are the same measurement.

**NOT A BLOCKER, and not a reason to restrict a tool.** It is a reason to read the cell difference
**by timestep** rather than in aggregate, and to report a null as ambiguous if the timestep profile
is unavailable.

**Whether the manager actually inspects is unknown** — the one classifiable bundle logs no manager
actions at all (the recording gap RE closed after it ran), so the capability is confirmed and the
usage is not.

---

## Open discrepancy with RE, raised not resolved

    quantity                LS measured    RE reported
    seed 56 ceiling@9       4.76%          4.76%     agree
    seed 37 ceiling@9       7.11%          3.44%     DISAGREE
    n_believed_optima 56    144            648       DISAGREE
    n_believed_optima 37    216            324       DISAGREE

**Seed 56's ceiling agrees exactly and seed 37's does not**, which rules out a wholesale
configuration difference and points at something seed-specific or a different `cap`/`shared_class_
segments`. **RE's feasibility argument rests on these numbers, so the construction is asked for
before either figure is used.**
