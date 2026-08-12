# L22 — A bundle can say which instance it ran, and cannot say which code ran it

**Two provenance gaps found before the shakedown, one closed and one open. Both are
impossible to fix retroactively, which is the only reason they were worth doing now.**

---

## 1. CLOSED — the selection guard was blind to the drift that forced the L10 re-draw (RR)

`assert_matches_selection` **rebuilds both sides** of its comparison:

    expected = env.instance_hash(gen.generate(seed, **setting))   # re-derived NOW
    actual   = env.instance_hash(instance)

So it catches parameters lost between the record and the builder — the threading bug it was
written for — and **cannot catch the generator moving under a recorded selection.** Both sides
move together, the hashes match, the run proceeds on an instance that is no longer the one
selected.

**Not hypothetical: it is L10's own history.** The v1 record's ceilings were priced at cap 3
while the runtime moved to uncapped. **A rebuild-and-compare guard would have passed that
silently** — it is blind to precisely the failure that forced the v1 → v2 re-draw.

**FIX: `environment_selection_v3.json` carries `instance_sha256` per chosen instance, fixed at
approval time.** v2 is untouched.

    seed 42  bank  4.97%   ef25aa9dc76f0fd5a8d53a7b0f9f1c1f6d8b6c9f370f57b79c5eb720c145ba9a
    seed 30  mdb   7.12%   fc1eac6ced1bec73246d635b45200ec69db568b2ca6a775ecf6ddb5fc23cb875

**v3 IS NOT A RE-DRAW, and the script now proves it rather than asserting it.** Same rule,
same `DRAW_SEED`, same pool. `main()` compares its draw against v2 and **refuses to write** if
they differ:

    drift test: reproduces v2 exactly [(42, 'bank'), (30, 'mdb')]

**Re-running an approved rule under a fixed draw seed IS the drift test** — if the pool has
moved, the draw moves with it, and that is now a hard failure rather than a silent v3.

**THE STAMP IS ONLY HONEST BECAUSE THE GENERATOR HAS NOT MOVED, and that was verified before
stamping, not assumed:** `finance_generator.py` — 0 commits since v2 was recorded;
`instance_hash` — untouched by the one `finance_env.py` commit since. **Stamping after a
generator change would fabricate provenance rather than record it**, and there would be no way
to tell the two apart from the file.

**THAT CONDITION IS NOW A CHECK, NOT A SENTENCE — `check_stamp_honesty.py` (RE's objection).**
It had been written into the record as prose (`stamp_is_honest_because`), which is the
label-over-condition shape this phase has been spent removing: a claim about a design property
sitting over an integer nobody computes. **It is a fixed historical fact — both commits are in
the past, so the answer cannot change — which is exactly what makes it worth computing once
and keeping.**

    v2 recorded at c97c2fc94
    v3 stamped  at f4e61fe12
      finance_generator.py: 0 commit(s) in the stamp window
      finance_env.py:       1 commit(s) -- changed, but not instance_hash
      seed 42 / seed 30: stamp matches the generator as it stands today
      HONEST, and the guard is live.

**★ AND THE CHECK IS STRICTER THAN THE HAND VERSION IT REPLACES.** My manual check used the
**last** commit touching v2 as the window's start; the correct boundary is the commit that
**introduced** v2, which is earlier — so the honest window is **longer** than the one I
actually inspected. **The conclusion held; the window I checked was too narrow to establish
it.** The check uses `--diff-filter=A` and passes over the wider window.

It also distinguishes two failures that would otherwise print the same: a **dishonest stamp**
(generator moved *before* stamping — exit 1) and an **honest stamp the runtime has outgrown**
(generator moved *after* — exit 2). The second is the researcher's call, **not a re-stamp: a
re-stamp would erase the evidence that anything moved.**

**A verification that nearly went unchecked.** `v2['pool'] == v3['pool']` returned **False** —
the alarm condition this record exists to create. It is benign: exactly 2 of 60 rows differ,
by the added `instance_sha256` alone, because the chosen rows are references into the pool and
the stamp mutated them in place. **All 60 seeds are identical on `(seed, ceiling_share,
sole_need_class)`.** Checked field by field rather than explained away.

**STILL OPEN, and it belongs to whoever next touches the guard:** the guard itself does not yet
READ the stamp. Until it does, v3's hashes are a record, not an enforcement, and the guard's
name and error message still claim provenance (*"selecting on one population and running on
another"*) while verifying threading.

## 2. OPEN — no bundle records the code revision that produced it

The manifest records the instance (`instance_sha256`), the models per role, the horizon, the
timeout, the concurrency, the arrangement, the rosters. **It does not record the code.** There
is no git rev anywhere in the manifest and the runner never captures one.

**So "which version produced this figure" is unanswerable for every bundle in the corpus** —
the exact ambiguity the repository's one-branch rule exists to prevent, arriving through a
different door than the one that rule guards.

**It matters now specifically.** In the last three days the code has changed in ways that
change what a bundle CONTAINS: the ninth state `started_and_failed`, the 900 s bound, the tool
dedup, the L17 selection threading. **A bundle from before and after those changes are
different objects and nothing in either says so.**

**The standing rule this violates is already written down:** *running a computation is only a
review if you know which revision you ran, and the revision must not change during the
measurement.* **We currently cannot satisfy the first clause for any bundle we produce.**

Not fixed here — the runner is RE's. Specified to RE with the two conditions that matter: the
rev must be captured **at run start**, and it must record whether the tree was **dirty**, since
a clean hash on a modified tree is worse than no hash.

## 3. Noted, not acted on — every tool a worker holds is a messaging tool (RR)

Verified independently from the bundles rather than from the code:

    598  send_message          598  broadcast_message      598  get_recent_messages
    299  get_conversation_with 299  get_task_messages

Five distinct tools, all communication. `create_ai_tools()` — search, analyse, calculate,
generate — never reaches a worker, because the registry passes `tools=[]`. (The 598s are
2 x 299 executions: the duplicate-tool defect RE fixed; the corpus predates the fix.)

**Consequence for how the study is DESCRIBED, not for whether it is valid.** First draft of this
sentence said the difference is *"entirely the IRB calibration they hold"* — **RR refuted it by
measurement, and the word matters because it is the one a paper is read on.** On seed 42:

    w_9f1635  covers [bank, retail]          calibration == the shared table: True
    w_721a8b  covers [bank, corporate]        True
    w_c0dd2b  covers [retail, sovereign]      True
    w_613442  covers [corporate, sovereign]   True

**Every worker holds the SHARED class-level value for every class it covers.** So workers do not
differ in calibration *quality* — **calibration is downstream of coverage, not a second axis.**
*"The calibration they hold"* invites a graded reading (workers holding calibrations of
differing accuracy) that **was true before R1 and is not true now.** The difference is binary
coverage.

**THE PRECISE FORM:** *the competence difference between workers is **which asset classes they
are IRB-approved for** — calibration values are shared and class-level since R1 — **and not
their tooling**, which is identical on every worker execution in the committed bundles.*

The tooling half keeps its scope deliberately: it is a measurement on worker-execution events
**in this harness at this revision**, not a claim about the design space. *"Workers have no
tools"* would be far larger than the bundles support.

**Why this is not cosmetic:** the brief's vocabulary includes **toolset** as a competence axis,
and the bundles say that axis does not exist on this path — **so a paper describing a toolset
difference would be describing a design we did not run.** Same class as the retired-framing
docstring, corrected for the same reason. Carried to the researcher: description, not design.

## What this does NOT establish

- **The stamp does not prove v2 was correct when approved.** It proves the generator has not
  moved since, and freezes that state going forward. Anything wrong at approval time is
  faithfully preserved by it.
- Closing gap 1 does not close gap 2. Knowing the instance is unchanged says nothing about
  whether the code that consumed it is.
- The tool finding is about description. It does not bear on any result already recorded.
