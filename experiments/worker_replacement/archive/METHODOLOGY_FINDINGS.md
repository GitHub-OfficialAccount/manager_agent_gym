# Methodology findings

_Consolidated 2026-07-27 from material scattered across `BELIEF_LAYER_DIAGNOSIS.md` §9,
`RISKS_AND_DIRECTIONS.md` §3, and `BELIEF_CONSUMPTION_FINDINGS.md` §6. These are findings about
**measuring with LLM-based instruments**, not about the Arm-3 result. They may be the more
transferable contribution._

---

## 1. The signature: a credible number, never a crash

**Every defect found in this investigation produced a plausible result rather than an error.** Not one
was caught by re-running. That is the property that makes them dangerous and it is why the detection
mechanisms below matter more than care does.

## 2. The recurring family: a query whose unit, vocabulary or scope did not match the claim

Eighteen instances. Each returned **a clean negative that looked like an answer**:

| # | instance |
|---|---|
| 1 | truncated key — `parent[:60]` collapsed three questions into one record |
| 2 | single-format regex — four surface formats, one pattern, silence read as absence |
| 3 | pooled denominator — a rate over a population that did not exist |
| 4 | wrong-timestep value — t=17's `con` applied to a t=15 row |
| 5 | per-worker where the claim was per-scope |
| 6 | a field name absent from the schema — `.get()` returning `None` 1004 times |
| 7 | free-text substring standing in for a structured `assignee` field |
| 8 | eligibility checked per-case but not on the pooled aggregate |
| 9 | a search scoped to one polarity of a two-polarity claim |
| 10 | two denominators reported without checking their intersection |
| 11 | a check that could not distinguish "run not started" from "run finished" |
| 12 | a search matching key *names* at depth 3, missing `events/payload/messages` |
| 13 | a guard whose own `mkdir` side effect created the condition it guarded against |
| 14 | **a verification that compared the wrong two things and could only return "match"** |
| 15 | batch membership inferred from a name that had legitimately changed |
| 16 | **a process check that read the wrapper instead of the child holding the variable** |
| 17 | **a pattern matching `instead of the required`, missing `instead of the intended`** |
| 18 | **a filter keyed on an artifact only the treated arm produces — deleting the comparison arm** |

**Rules adopted, in the order they were forced:**

- Assert a key exists before reading its values — a uniform `None` is not evidence of a null field.
- Match on the field that carries the claim, never on a serialisation containing the word.
- Re-run an eligibility check at **every level the claim is aggregated to**.
- **Name both sides in the output.** A count that prints one number can only be self-consistent.
- The denominator for a detection claim is the number of opportunities at which **the signal was
  present** — not how often the topic came up.
- **State the tolerance.** Five runs at `1e-9` are six at `1e-4`; a reader using `==` gets a different
  answer than the claim.

### Instance 17, and why it belongs at the top of this list

**The measurement written to end this family reproduced it.** Three inconsistent articulation figures were
in circulation (`2 of 8`, `2 of 9`, `3 of 10`), so a corpus-wide re-measurement was written to settle it.
Its wrongness pattern included `instead of the required` — and the `arm3i_noq` run says *"instead of the
**intended**"*. **The run was dropped and the script returned a confident `2 of 12`.**

It was caught only because a doc cited a run the measurement said had no articulation, and that
disagreement was checked rather than assumed stale. **The correct figure is 3 of 12.**

> **A measurement built to fix a class of error is not outside that class.** Instance 2 of this family was
> *"single-format regex — four surface formats, one pattern, silence read as absence."* Instance 17 is the
> same error, committed while writing the fix for it, by someone who had written instance 2 down.

**Rule adopted:** when a measurement disagrees with an existing record, **the measurement is the first
suspect, not the record.** The record was produced by someone reading the text; the measurement was
produced by someone guessing how the text would be phrased.

### Instance 18 — when the filter key is an effect of the manipulation

**The sharpest instance in the family, and it is not a coverage gap.** Found by Reviewer-Reproducer in their
own analysis, 2026-07-28.

The question was *whether the observation aid changes the manager's routing.* The analysis joined task names
via `arm3_state.json`. **Only aided runs produce `arm3_state.json`** — an aid-free run has no aid state to
write. So the loop skipped every aid-free run and returned silently.

> **The analysis covered 7 of 14 runs and excluded every aid-free run by construction, while reasoning about
> whether the aid changes behaviour. The exclusion was perfectly anti-correlated with the hypothesis.**

And it hid more than it distorted: the excluded set contained the **full-observability** run, where all three
robust audits go to the correct worker at r=1.00 — the existence proof that the target behaviour is reachable
at all. That was invisible for the same reason.

**The rule, and it is a class rather than an incident:**

> **The hazard is not that a filter restricts the population. It is that the restriction can be
> anti-correlated with the hypothesis. Keying on an artifact that the treatment produces selects the treated
> population and silently deletes the comparison arm.**

Generalises to **any filter whose key is itself an effect of the manipulation** — a log the new code path
writes, a field the new schema adds, a directory the new arm creates. Each looks like a neutral join key and
each is a treatment indicator.

**Detection:** name the population size beside every result and check it against the number of runs you
believe exist. `7 of 14` is visible; a silent skip is not. This is §2's *"name both sides in the output"* in
population form.

**It also sits beside §5.** A test written from outside cannot see that its join key is downstream of the
treatment — the key resolves, the join succeeds, the rows returned are real. Only knowing what writes the
artifact reveals the restriction, which is again reading the code rather than checking the output.

## 2b. A distinct class: a check evaluated over a union, asked about a member

**Two instances tonight, and it is NOT the §2 family.** §2 defects restrict the population and lose rows;
this one **keeps every row and asks the question at the wrong granularity.**

| whose | the check | why it could not fire |
|---|---|---|
| lead scientist | `if expects_cutoff and not any(seen.values())` — "did extraction yield anything?" | evaluated **across workers**, so `screening_analyst` yielding a legitimate cutoff suppressed the alarm for `portfolio_analyst` yielding nothing — on precisely the run the guard existed to catch |
| Research Engineer | completions summed **per worker across scopes** | would have reported *"never occurs"* for the t=8 zero-completion dissociation, because the worker had completions in other scopes. Caught by RE, who named the **scope** as the right unit |

> **A check evaluated over a union is satisfied by any member, so a per-member failure is invisible.**

**The tells differ, which is why they should not be filed together:**

- a **filter** defect shows up as a **suspiciously clean population** — `7 of 14`, or an unexplained absence
- an **aggregation** defect shows up as **a check that never fires** — no alarm, ever, including when it should

**Operational form, and it is short:**

> **State the unit the check is about before writing it, and assert at that unit.**

Both instances were **per-subject questions asked of a collection**. Mine was per-worker, written corpus-wide.
RE's was per-scope, written per-worker. Neither was a coding slip — both read correctly and answered a
different question than the one intended.

_Aggravating detail on the first: it was written as the fix for the reviewer's half-guard, twenty minutes
after diagnosing that a guard which only validates what it DID extract cannot see what it failed to extract.
The fix inherited a sibling defect from the same family._

### And a distinction worth keeping about guards that work for the wrong reason

The value guard — *every extracted number must be one of the seed's two legitimate cutoffs* — was proposed
against the trap form `income flagged=N`. **It earned its keep against a different form:** `income=18` where
"flagged" sits earlier in the sentence, which the negative lookahead misses entirely.

> **That is a guard doing better than its rationale, which is not the same as a guard doing what was
> claimed.** Record it as found, not as designed — otherwise the rationale gets credited with coverage it
> did not provide, and the next person trusts the lookahead.

## 3. One rule, two domains

> **ACTIONS** — a delay is only a failure if action was available **and the agent was eligible for it**.
> **OBSERVATIONS** — a non-detection is only a failure if the signal was **already present**.

Discovered separately, then recognised as identical. Both fail the same way when the denominator is
"how often the topic came up" rather than "how often the answer was there to be had." Applied four
times, it **removed three apparent findings and confirmed one** — which is what a load-bearing check
looks like.

## 4. Corrections are where defects come from

**Three defects in one four-hour window were introduced by corrections**, not by original work:

| the correction | the defect it introduced |
|---|---|
| preserving records out of a doomed worktree | orphaned every probe that read them |
| renaming a version token to its true config tag | dropped the most-cited cell from its batch |
| wiring ten modules to a resolver | would have relabelled every cell in every downstream table |

**Each was caught by a test written *for* the correction, not by the correction itself.** Nothing in
ordinary process treats a correction as a change requiring the same scrutiny as a feature — and **a fix
ships with the confidence of having just understood something, which is exactly when scrutiny drops.**

## 4b. The case where nothing broke and the process was still unsafe

**A distinct category from §2, and the hardest to catch, because there is no wrong answer to point at.**

A recording defect was found late: every action's `execute()` set `success` and `result_summary` on its
**success path only**, so every early return of every action type recorded silence. `manager_actions.json`
— the record most analyses read — showed `success: null` on failures.

Every assignment timeline in the project had been built by **matching on `result_summary`**. So a failed
attempt would have been invisible to all of them. The natural reading is that a conclusion was reached on
corrupt data.

**It was not.** The defect hid **outcomes**, never **attempts**: `action_type`, `task_id`, `agent_id` and
`reasoning` were recorded regardless of result. And `success: null` occurred **once** in the entire
corpus — at t=11 of the amendment run, created hours *after* every absence claim was made. So no claim
was ever read across a null record.

> **The instrument was wrong even though the data never exercised it. The fix removes the hazard; the
> check shows it never fired. Those are two different things and both belong in the record.**

Distinguish carefully — this is **not** "a correction exposed a defect in a conclusion." The conclusions
were sound. It is:

> **A correction exposed that a conclusion had been reached with an instrument that could have been
> wrong. The finding survived; the method did not.**

The right instrument was `action_type`, which was never corrupted, and the claim it supports
(*"at t=14 and t=20 the manager did not try"*) is closed by an architectural fact rather than by the
field that had been used: **exactly one action per timestep, 32 actions over timesteps 0–31 with no gaps
in either run**, so there is no room for an unrecorded attempt.

_One precision if this argument is extended: the one-action-per-timestep property was **observed** in two
runs, not shown to be enforced. It is sufficient for these two claims and would need checking before it
carries a third._

## 5. A test validates outputs; only reading the code validates meaning

The sharpest version, and it came from Research Engineer after a labelling error survived a
pre-committed population test:

> The population test and the label derivation **read the same paths** and would have disagreed only in
> a field the test did not examine. **Any** test written from outside had that limitation. It was caught
> because wiring forces you to look at what each expression *means*, not at what it returns.
>
> **A test validates outputs; only reading the code validates meaning — and a refactor changes meaning
> while preserving outputs. That is why refactors are where these land.**

## 6. What actually caught things, cheapest first

1. **Testing a claim about a check** — free.
2. **Checking a count against expectation** — free.
3. **Reading source you did not write** — cheap.
4. **Producing a wrong result and retracting it** — expensive.
5. **Sweeping the prior record with a check adopted mid-investigation** — a conclusion that predates a
   check will never be flagged by it. This caught the widest errors here.

**Nothing was caught by re-running.**

## 6b. Instance 16 in detail — the check that answered about the wrong process

Worth writing out because it nearly produced a confident false negative on a load-bearing fact, and
because the fix is one command.

**Claim to verify:** the running experiment has `MANAGER_MODEL_NAME` set to the pro model.
**The check:** `pgrep -f "worker_replacement.run"` then read `/proc/<pid>/environ`.
**Result:** `MANAGER_MODEL_NAME` **not set** — which was wrong.

The variable was set **inline on the python child**, so it exists on the child and not on the bash
wrapper that spawned it. **`pgrep -f` returns the wrapper first, because the wrapper's own `cmdline`
contains the pattern.** So the check reads a real PID, finds a real environment, and reports a real
absence — about the wrong process.

**Fix: read `cmdline` before `environ`, and iterate every match rather than taking the first.**

```
pid 2470680  /bin/bash -c source …        MANAGER_MODEL_NAME (not set)      <- wrapper
pid 2470704  .venv/bin/python -m …run     MANAGER_MODEL_NAME=…-v4-pro       <- the process making calls
```

**Same family as §2:** the query's scope (any process matching a string) did not match the claim's scope
(the process issuing the LLM calls). And it has the §1 signature — a plausible answer, no error.

**The generalisable rule:** `/proc/<pid>/environ` is the right instrument for *"did this configuration
reach the running process"* — stronger than re-resolving the config in a fresh interpreter, which only
shows what the code *would* do. But it is only right once you have identified the process. **Verifying a
value is a different step from identifying the subject, and a check can pass the first while failing the
second.**

## 6c. A stated principle applied to exactly one branch

`Task.pretty_print` carries our own comment: *"Surface why it failed — inspectors can't diagnose from
status alone."* The principle is correct and general. **It was applied only to the `FAILED` branch.**

The `completed`-with-wrong-output branch — the one competence change actually lives in — still returns
resource identifiers. And at `q` t=20 the manager chose `inspect_task` and received exactly that.

> **Writing the general principle into a comment created the impression it had been applied generally.**
> The comment is evidence the limitation was understood; the code is evidence only one case was fixed.
> **A comment stating a general rule beside a specific fix is a place to check, not a place to trust.**

Distinct from §4 (corrections introducing defects): nothing here was broken by a change. The narrow fix
was correct and remains correct. **What the record lacked was any note that the other branch was still
open** — which is why it went unnoticed for two weeks and was found by reading upstream for an unrelated
reason.

## 6d. A run that recorded a commit not containing its own code

**Found 2026-07-27 while staging unrelated documentation.** Different in kind from §2 — the record was
internally consistent, well-formed, and wrong about the only thing it exists to establish.

`outputs/amendment_fav` — the run behind the entire Arm-3 conclusion (t=11 diagnosis, t=14/t=20
re-assignment) — records:

```
code_commit         ed27273b95c2754c651a847e15667fd831bec7ec
working_tree_clean  None
aid_presentation    favourable
```

**`ed27273` does not contain the `--aid-presentation` flag.** The amendment arm was implemented in the
working tree and never staged, so a checkout of the recorded commit could not execute the recorded
configuration — it would reject the argument. **The run was not reproducible from its own provenance,
and every figure derived from it inherited that.** Same for the v3.0 cells, whose recorded commits
likewise predate code they ran.

**A guard for exactly this existed and did not fire.** `working_tree_clean` is a manifest field whose
purpose is to flag this condition. `_resolve_cells` populates it only on the `--matrix` path; the
`--observability/--arm` path passes `None`. **Every run in the corpus took the un-populated path**, so
the field is `None` throughout and no run has ever asserted a clean tree.

**Rules adopted:**

- **A recorded commit is a claim that the code is retrievable. Verify it against a real behaviour** —
  cheapest check: does the recorded commit contain the flags in the recorded config?
- **`code_commit` and a dirty tree are contradictory provenance.** Record the dirt or refuse to record
  the commit; `None` is the worst option because it reads as "not applicable."
- **A guard on one code path is not a guard.** §2 rule *"re-run an eligibility check at every level the
  claim is aggregated to"*, in its provenance form.

**Committing does not alter the working tree**, so a batch that straddles a commit still ran one body of
code — but only if that is stated explicitly, which is why `71b6969` records it for `outputs/mgr_pro`.

_Not fixed: the `working_tree_clean` gap on the non-matrix path. Recorded so a decision to fix it is
deliberate._

## 6e. We each read the text we went looking in

**The fourth text-based reversal of the day, and the one with the cleanest mechanism.**

A claim was made about the pro-manager run from reasoning text (*"it detected the anomaly and engineered
around it"*, from t=19's tie-break). The reviewer overturned it **from the same turns**, by an absence
check. **The resolution came from a third turn neither of us had read** — t=18, a quiet `noop`, which
contained the actual finding.

> **The searcher looked for anomaly language and found the word "mismatch." The checker searched the same
> turns to test that claim. Both searches were scoped to where the claim lived, so neither could reach
> the turn where the evidence was.**

**The turn nobody read was the one where nothing happened.** `noop` turns look like non-events and get
skipped — but a justified `noop` is a decision, and its justification is exactly where a validity
judgment surfaces.

**Rules adopted:**

- **When testing a claim about reasoning, do not restrict to the turns that motivated it.** A refutation
  scoped to the claim's own evidence can only confirm or deny *that* evidence.
- **Read the turns where nothing happened.** `noop` is an action with a stated ground, and inaction is
  the outcome most claims about belief-to-action are actually about.
- **Prefer a claim corroborated by the action over one resting on text alone.** The t=19 claim had text
  only and fell; the t=18 claim has text *and* a `noop` it licensed, and held. **That difference, not
  confidence, is why one was withdrawn and the other kept.**

## 6f. Four claims about what the code supports, made from what the design space looked like

**One document pass, 2026-07-28, produced four errors of a single shape — two from the lead scientist, two
from the reviewer.** The symmetry is the point: **this is not a difference in care between roles.**

| claim | asserted from | what the code says |
|---|---|---|
| *"work quality is in R_M and not in S; unobservable by construction"* | **lead scientist** | `Task.quality_score` exists at `tasks.py:80`, and `Task` is in **G** |
| *"populate it and render it — no schema change"* | **lead scientist** | `ManagerObservation` carries tasks as `list[UUID]`; **nothing conveys task attributes**, so it needs a new field plus a `_prepare_context` change |
| *"entity indexing is the operative variable"* | **reviewer** | `prose_capability` was worker-indexed **and** pre-aggregated, and produced the floor — a condition the reviewer had cited themselves |
| *"shape 1 (make reconciliation FAIL) is implementable without plumbing"* | **reviewer** | `FAILED` is set only at `engine.py:722`/`:746`, from an execution result or a caught exception; **no conformance validator exists in `core/`** |

**Why it happens:** each was a statement about what the implementation supports, reached by reasoning about
what the design space looked like. **Design-space reasoning feels like knowledge and is not**, and neither
seat is protected from it — the reviewer's two came from the same move as the lead scientist's, one of them
while correcting the other's instance of it.

> **The check, in operational form: BEFORE CLASSIFYING AN INTERVENTION, GREP FOR THE THING THAT WOULD HAVE TO
> EXIST.** It is cheap. **Neither of us ran it four times.**

**THE FIX, AND WHY THE OBVIOUS VERSION OF IT DOES NOT WORK.** Six errors this pass were counts quoted
without the population they were over — one mine, four the reviewer's, one a cell selection rather than a
directory. The natural remedy is to have the reader return `(count, population, scope)` instead of a bare
number. **That is necessary and it is not sufficient, for a reason this project has already paid for once:**

> **In every one of the six, the population was AVAILABLE to whoever computed it** — the glob was on screen —
> **and did not travel.** `records/MANIFEST.md` is the precedent: it made provenance available and figures
> still moved without it. **Availability is not enforcement, and a check that can be ignored will be.**

**So the operation to protect is the COMPARISON, not the read.** The expensive error was not a bare count; it
was **two counts over different populations compared as if they were one** (`0` rapid screens over 14
preserved runs against `5` from outside it). A tuple makes that mismatch *visible*; it does not prevent it.

```
compare(a, b)  raises unless  a.population == b.population and a.scope == b.scope
```

**That converts "visible" into "impossible", which is the difference between the manifest and the
join-assertion that actually caught things.** If only one thing is built, build that. Two smaller ones: **name
the fields** so `.count` is explicit and `count, _, _ = read(...)` looks wrong — destructuring is how the
population gets dropped in practice; and **state the boundary** — the moment a number enters prose the
machinery ends.

> **The reader closes the COMPUTATION-time class and not the PROSE-time one.** §7.9 was wrong three times
> about which population its figures described, and **every one of those was prose-time — the reader would
> have caught none of them.** Pair it with the documentation rule; do not treat it as a replacement.

**A fifth, adjacent case, kept separate because the pattern differs.** *"`tool_calls.json` records arguments
only — drift measurement is blocked"* was also wrong, but not from design-space reasoning: the file genuinely
is name-only, and the error was **inferring that the data was absent from the fact that one file lacked it**.
The research engineer found all 89 calls attributable in `events`. **The general form there is: a lossy
derived file is not evidence about the source.** Related but distinct — and the 87-vs-89 count gap is a third
thing again, a **scope boundary with no field marking it** (`send_message` is a framework tool the scenario
never wraps), which was initially misread as silent loss.

---

## 6g. When a manufactured fixture is evidence, and when it is only evidence about itself

**The distinction, which we had been applying case-by-case without naming:**

| a constructed input used to estimate a **RATE** | **illegitimate** — it tells you about the construction |
|---|---|
| a constructed input used to verify a **FUNCTION'S BEHAVIOUR ON A SPECIFIED INPUT** | **legitimate** — that is what a unit test is |

**The case that forced it.** `tool_call_reader`'s `outcome_source == "missing"` branch — an outcome aged out of
the rolling prompt window — **cannot occur in the only hand-verified fixture** (`amendment_fav`, 32 of 32
outcomes recovered), so the test asserting no outcome is silently lost **can only pass there.** The proposal was
to manufacture the condition by trimming the prompt history rather than spending a longer run.

**It is legitimate, and for a stronger reason than the general principle gives.** The reader's input **is** the
set of prompt contents. In a real long run an outcome ages out and is therefore **absent from every prompt**;
trimming produces **absence from every prompt**. **The reader cannot distinguish the two, because they are the
same input** — the cause differs, the interface does not. **So the fixture reproduces the condition exactly
rather than approximating it**, which is a better position than most constructed tests occupy. Worth stating in
the test's own docstring, because *"constructed"* otherwise reads as *"weaker"* to a later reader.

**This is also our own §9 rule applied to an unobserved condition** — define the category by a property, make
the fallback conservative, then **assert the fallback with a test using a type that does not exist yet** (the
`SomeFutureSDKError` case). Same move, different subject.

**The constraint that makes or breaks it: trim MINIMALLY and assert BOTH halves.**

```
t=11's outcome is `missing`
every OTHER action in the fixture still resolves as `recorded` or `prompt_history`
```

**Without the second assertion the test cannot distinguish "correctly detected one aged-out outcome" from "the
trim broke prompt parsing and everything is missing"** — a wholesale-trim bug passes a test that checks only
t=11. **That is a check satisfied by the wrong subject, which is already on this list twice.**

**What it does NOT establish, and must be labelled as not establishing.** It says nothing about **whether**
aging occurs or **how often**. The corpus cannot currently answer that: **0 `missing` across 89 runs, but only
3 outcomes ever exercised the window at all**, so the frequency is **UNMEASURED, not zero.** **Correctness of
the branch and incidence of the condition are different claims** and only the first is being tested. A long run
would answer the second and is not needed for the first.

---

## 6h. Derived artifacts that assert more than their input determines

**Four instances, three of which cost a wrong inference, and they are one pattern.** Each artifact was
**internally consistent and wrong at the boundary of what it could know** — which is why none of them looked
broken.

| artifact | asserted | what its input actually determined |
|---|---|---|
| `tool_calls.json` | *"the tool calls"* — the name claims the population | **scenario-defined tools only.** `send_message` was never in scope, and **no field marked the boundary.** Read as a 2-call loss; it was an edge |
| `manager_actions.json` `success: null` | nothing — but **read as** *"no action"* | **refused** and **not attempted** are the same `null`. The engine's *"only failed tasks can be retried"* existed only in `events`. **The first reading of that run drew the wrong inference** |
| `tool_call_reader`'s `unjoined` | *"the join key did not match"* — **a cause** | prompts exist and the key is absent. **Aging out and a join-key mismatch are the SAME INPUT.** The label asserted a cause it could not know |
| `effective_status` | a composite status | `node.status.value` — **inherits the enum gap** and adds nothing |

> **The general form: a derived artifact must report the OBSERVATION and refuse the DIAGNOSIS whenever its
> input cannot distinguish the causes.** `unresolved` — *"prompt history exists, this outcome is not in it,
> cause not determinable"* — is the corrected shape of all four.

**The third instance is the interesting one, because it was caught by construction rather than by cost.** It was
found in the branch of the module whose entire purpose is to stop refusal-versus-absence conflation — **the same
error, committed inside the tool built to prevent it, by the person who built it.** Self-caught when the
manufactured fixture (§6g) returned a label the author had not predicted. **The fixture earned its place by
falsifying the design it was written to confirm.**

**Practical rule:** a derived file or field needs (a) a scope marker naming its population, and (b) label names
that survive the question *"could my input have told me that?"*

---

## 6i. Addendum to mutation testing: verify that the mutant mutates

**A mutation that fails to mutate looks exactly like a test that passes correctly.** Two mutants written to
break a half-of-the-assertion check both passed, and the natural conclusion — *the suite is fine* — was wrong
in both cases:

```
mutant 1   kept the `t=11` guard, so it touched 10 messages, not the whole history
mutant 2   searched a JSON dump for `—` where the em-dash was escaped, and matched nothing
```

**Neither mutant did what it claimed.** The third one did, and it failed the suite immediately —
`AssertionError: assert 'missing' == 'unresolved'` — which is how the inadequate check was found.

> **So: confirm the mutant changes behaviour BEFORE concluding the suite caught it.** A green suite under
> mutation is evidence only if the mutation was real.

**AND THE "HYPOTHETICAL" MUTANT WAS NOT HYPOTHETICAL.** Mutant 2 — *a refusal read as a success* — was written to
cover a polarity error **nobody had ever produced**, and was described that way at the time. **The reviewer then
found it live on the corpus:** two of the three `prompt_history` recoveries were being **granted successes**,
including one whose text reads `FAILED TO RUN`.

> **So the mutation aimed at an unobserved failure mode found a real one.** The value of covering *"what has
> never happened"* is not hypothetical robustness — **it is that the author's belief about what has never
> happened is itself untested.** Fixed, mutation-tested and committed at `09cd9f6`; the guard's two-scope
> limitation followed at `95013a6`.

**And what it found is worth recording separately, because it is the §6f pattern again:** the original half-two
assertion — *"every other action still reads `recorded`"* — **passes under a wholesale trim**, because 31 of 32
outcomes in that run are read from the file and are **untouched by any amount of prompt trimming.** The check
was **aimed at the wrong artifact**: the trim modifies prompts, so the assertion has to be made against prompts.
**A check satisfied by the wrong subject — the third instance this pass.**

---

## 6j. Agreement across statistics is evidence only if the statistics COULD have disagreed

**The error.** Identifiability was measured with three statistics — tool-name marginal, parameterisation, sequence
bigrams — and all three put the same pair last (1.60 / 1.76 / 1.30). **I reported the ordering as robust across
statistics and treated the convergence as strength.**

**The population could not have produced disagreement.** `portfolio_analyst` and `risk_analyst` are identical in
**toolset tier** (`ROBUST_TOOL_IDS`) *and* in **system prompt** (`scenario.py:38-47`, one shared template). **There
was nothing for any statistic to distinguish.**

> **So the convergence carried NO information and read as robustness.** Three checks agreeing on a population
> identical by construction is not triangulation — it is **one uninformative measurement performed three times.**

**The generalised rule:**

> **Convergent measurements are evidence only when the measurements COULD have diverged. Before citing agreement
> across statistics, ask what population state would have made them disagree — and confirm that state was
> possible.**

**Why it was hard to see.** This is **the same shape as a check satisfied by the wrong subject (§6f), one level
up** — a *set* of checks satisfied by the wrong **population**. And it inverts an instinct this project spent the
whole session building: **every other lesson here says convergent measurement is trustworthy.** This is the case
where that instinct is exactly backwards, which is why escalating to a third statistic felt like rigour and added
nothing.

**The tell, in hindsight:** three different statistics agreeing *that* closely on a *ratio* is itself anomalous.
**Suspicious agreement should prompt a check of the population, not confidence in the result.**

---

## 6k. The over-claiming family SPLITS: one shape is decidable from the AST, four are not

**§6h collected five instances of *"a derived artifact asserting more than its input determines."* They do not all
have the same status, and the split is more useful than the family.**

| **MECHANISABLE** | a log line asserting a **delta it destroyed** — `f"updated from {task.x} to {new}"` after `task.x = new` | **AST rule, shipped** (`ee2653a`) |
|---|---|---|
| **JUDGEMENT** | `tool_calls.json`'s name over-claiming its scope · `success: null` conflating **refused** with **not attempted** · `unjoined` asserting an undeterminable cause · `effective_status` inheriting an enum gap | **requires knowing what the input CANNOT determine** |

> **The four remaining share a property the fifth lacks: they require a SEMANTIC fact about the domain, not a
> SYNTACTIC one about the code.** No AST pass can know that a refusal and its absence are the same `null`, or that
> aging-out and key-mismatch present identically at the interface.

**The rule, and the scoping decision that made it usable.** An AST pass for *attribute assigned, then read inside an
f-string later in the same block* flagged **exactly three** across the whole package, **zero false positives.** The
decision that produced that: **attributes assigned inside an `if` body are checked against THAT body, not the
enclosing one.** Without it, a trailing `logger.info(f"Task {task.name} refined…")` flags — and it **should not**,
because it states a **current value** and claims no *"before"*.

> **The rule catches FALSE CLAIMS OF CHANGE, not READS OF MUTATED STATE.** Conflating those is what would have made
> it noisy enough to be disabled.

**And the correct idiom already existed twenty lines below the defect, in the same function** —
`additional_instructions` captures `old_instruction` before overwriting. **So this was not a missing pattern but one
applied unevenly, which is exactly the case where a mechanical check beats individual fixes.** (`new_name` is
**correct by omission**: it logs `name -> '{new}'` and claims no "from".)

**The rule was verified able to FAIL** — reverting the `cost` fix produces `1 failed` — plus two unit tests using the
original defect's source as expected input. **§6i's addendum applied without being asked for.**

### What might mechanise the other four, and it is not a naming lint

**The proposal was a lint on names that assert a cause or completeness** (`unjoined`, `effective_`, `_all`,
`_complete`) requiring a docstring stating what they cannot distinguish — **not built, on false-positive doubt.**

> **Better target: make it a TYPE obligation rather than a name pattern.** All four judgement cases are about
> **what the input cannot determine** — which is precisely what `Count(count, population, scope)` was built to carry
> for numbers. **A derived value that carries its own non-distinguishability is enforced by construction: the type
> either has the field or it does not, with no pattern matching on identifiers.** That is the same move that turned
> the denominator problem from a convention into a guard (§6f), applied one level out.

---

## 7. Positional independence beats disinterest

The arrangement worked because **positions differ**, not because any seat sees better. Recorded because
the natural assumption is the opposite:

- The lead scientist held a stake in a mechanism and had the **correct fact**; the reviewer had no stake
  and the **wrong scope**.
- The reviewer raised the `.gitignore` exposure **unprompted** — a question nobody had asked them —
  which is the only reason a rescue happened before a deletion.
- Research Engineer refused to adjudicate a number their own arm produced, and later declined to
  classify their own screen as verified.

**Structural conclusion:** an unverified endorsement and an unaudited check fail the same way — **they
remove the reason for the next person to look.**
