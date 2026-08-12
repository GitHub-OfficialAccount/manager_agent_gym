# REVAMP — why the previous direction is abandoned, and what replaces it

> **SUPERSEDED as of 2026-08-06** by `STUDY1_FOUNDATION.md` (direction).
> Retained as record; **do not cite for current design.** This file is
> version-controlled, so its pre-banner text is recoverable from git
> history and it needs no archive copy.

**Status:** direction document. Supersedes the experimental framing in OVERVIEW.md §7's
silent-change design; the formal POSG grounding and scope discipline there still apply.
The full reasoning trail is `BRAINSTORM.md` §35–79; this document is the consolidated
statement. Every empirical claim here has a section reference or a `file:line` receipt.

---

## 1. Summary

The previous experiment asked whether a manager agent detects and responds to a silent
change in a teammate, under graded observability. We are abandoning that framing for
three independent reasons, any one of which would have been sufficient:

1. **The silent-change premise is unrealistic.** In a production system every change is
   announced, because the system is built for faithfulness; a silent capability change
   is an engineering bug, not an operating condition worth a benchmark.
2. **The perturbation created deficiency, not difference.** Removing a tool made worker
   failure *deterministic*, so every aggregate we measured decomposed into
   near-degenerate populations mixed by the intervention itself (§78).
3. **A pure-orchestrator manager cannot do ad hoc teamwork.** Its action space is
   observe / rewire the task graph / delegate — no execution. Under that constraint,
   "adapt to the teammate" collapses into behavior prediction plus prompt engineering,
   which is not the AHT problem (§75).

The replacement direction keeps the manager as the studied agent and changes the
*setting* rather than searching for another formulation inside the old one: route the
full task trace, decide the status of prompt-level reshaping, and decide whether the
manager shares the workers' tools so that complementation becomes possible.

---

## 2. Why the old direction failed

### 2.1 Silent change is an engineering bug, not a scenario

The old design's central manipulation was *full-info vs silent* teammate change.
**Within a single deployment**, changes are announced — model swaps, prompt updates,
tool grants all pass through configuration the orchestrator can read, because the
deployment is built to be faithful. A change that reaches the manager only through
behavioral drift is there a failure of the deployment, not a property of the
environment. (Silent change *is* realistic across an **administrative boundary** —
providers silently update models behind stable API names, third-party agents are
updated by their owners, load-induced degradation is never announced. Our design did
not model a boundary: the changed worker lived inside the same deployment as the
manager, which is exactly the regime where silence is a bug.)

Two further facts sharpened this:

- **Announcement makes detection free — and detection was never the interesting part.**
  With the change announced (or the trace routed), the open question is what the
  manager *does* about a changed teammate: adapt around it, re-specify it, or absorb
  the work. None of our old measurements addressed that question.
- **Our own record shows detection results were unstable anyway.** Three load-bearing
  observability claims were retracted in sequence (§73, §74, §76), each because a build
  detail had been read as a property of the setting.

### 2.2 The perturbation was deficiency, not difference

Ad hoc teamwork mechanisms handle teammates that are *different*, not *worse* — and our
tool-removal perturbation made the swapped worker structurally unable to perform the
task. Consequences, all verified on the existing corpus:

| pooled figure we reported | what it decomposes into | reference |
| --- | --- | --- |
| audits 48.9% correct "given a perfect upstream" | 99.1% tool intact / 0.0% tool removed (necessarily) / 9.5% no tool used | §78b |
| "112 of 113 wrong reconciliations are collapses" | 1.0% wrong intact / 100% wrong removed — arithmetic, not behaviour | §77d |
| collapse rates 24%/56% by arm | 2.6% / 99.3% by the producer's own tool trace | §74, §77d |

Five restratifications, every one moving the same direction: what looked like worker
behaviour was the intervention averaged into the total. A perturbation that flips a
worker from always-right to always-wrong cannot distinguish teammate adaptation from
quality control — there is no rate to measure, only a mixing weight. The replacement
perturbation must produce a teammate that is **different but fully operational**
(consistent with the repository's core-tool rule: every worker must always be able to
act).

Scope caveat, stated so the evidence is not overread: all five restratifications and
every row above concern the **tool-removal** lever. The prompt lever's deficiency
evidence is a single run (the judgment-lever seed, whose screens reported the robust
audit's values). So "the perturbation created deficiency" is established for tool-swap
and is **n=1 for prompt-swap** — which matters, because §4.5's replacement is
prompt-level behavioural change, i.e. the lever whose deficiency status is least
established. Its non-degeneracy must be checked, not assumed.

### 2.3 The pure-orchestrator collapse

Nine problem formulations were developed and eliminated over §35–74. They died of one
shared cause: **the manager can choose who acts, but it cannot act.** It creates zero
artifacts; workers make zero graph edits (§75). Classical-benchmark AHT has shared
write access to the same state — both players can move to the same position — and that
is exactly what makes the characteristic AHT move possible: *"my teammate isn't doing X
well, so I'll do X."* Without it, every "adaptation" reduces to re-delegation, and with
workers that are identical by construction, even that choice carries no information.

Stated precisely, this establishes *"the setting is not classical AHT"*, not *"the
setting is not ad hoc teamwork."* Pure allocation without execution is a real
coordination problem (air traffic control, dispatch, triage), and shared write access
is a property of the classical benchmarks, not of the concept. The abandonment argument
is therefore not that orchestration is uninteresting — it is that **none of the
mechanisms in the AHT literature is expressible in it**, so the old framing could
neither use nor extend that literature, which was its stated purpose.

The ManagerAgent paper asks the right question but cannot express an answer beyond
delegation: its open question calls for *"effective, on-the-fly task delegation and
coordination"* and for the manager to *"flexibly adapt how it communicates and
coordinates with workers"* (§4.3) — but its action space (§3.3:
observability-increasing, graph-modifying, delegation/communication — no execution)
leaves delegation-plus-messaging as the only coordination the manager can perform.
The gap is between the paper's question and its own formalism, and it is the gap this
revamp works in.

### 2.4 What the observability audit actually found

Verifying the observability premises produced the sharpest corrections in the record.
All verified at the upstream merge-base `3f7a5d4` and empirically on run logs:

- **The manager sees no task trace — upstream and fork, any channel.**
  `ManagerObservation` (schemas/execution/manager.py:15) carries no tool-call data; no
  action reads worker history; the deterministic trace (tool name, arguments, output,
  actor) exists only in `worker_run_completed` events in the run log, which no
  manager-facing path reads.
- **But the manager is NOT artifact-blind.** `workflow_summary = workflow.pretty_print()`
  defaults to `include_resources=True`, rendering a 300-char content preview of every
  artifact into the manager's prompt every timestep (structured_manager.py:343).
  Verified: 30 of 32 manager prompts in a real run contain `Content preview:`, with the
  artifact's `metric:` line inside the window (§79).
- **`inspect_task`, the designated observability-increasing action, returns strictly
  less than the passive view** — resource IDs, where the ambient summary already shows
  content. The paper's spec (§3.3: Inspect is "to view execution logs and outputs") is
  under-delivered by the action and over-delivered by the passive observation.

- **The preview also carries a procedure *declaration*, and it has never been observed
  to lie.** Workers' artifact format puts `metric:` and `method:` in the first two
  lines, so both survive the 300-char truncation in 92.0% of 1,170 artifacts; across
  all 221 checkable robust audits, the declared method matches the tool actually called
  — 0 false self-reports (`preview_visibility.py`, reviewer-derived, independently
  reproduced).

Net: the genuine observation gap is narrower than "procedure vs outcome". The manager
already receives outcomes *and* an accurate self-reported procedure summary; what it
lacks is **verified** procedure — the trace. The observability decision in §4.3 is
framed accordingly: self-report vs verification, not visibility vs blindness.

---

## 3. What survives the abandonment

The old corpus was not wasted. Findings that hold independently of the old framing:

- **The interpretation finding (load-bearing).** 89 of 112 coordinators verbalised an
  identity they were positioned to detect; 0 flagged it as anomalous; ≥11 of 26 sampled
  cases independently re-verified against source artifacts and read *confirmation* into
  the identity. This is about how an agent interprets a joint property it observes, and
  does not depend on what caused the property.
- **The degenerate-task convention finding.** Where upstream failure made a downstream
  task unanswerable, performance fell *below chance* (4% vs ~33% guessing): agents
  tie-break by convention rather than reporting that the question has no recoverable
  answer.
- **Conventions are not free.** LLM workers under one fixed prompt hold no stable
  representational convention — 61 artifacts of the same task in 38 formats, worst in
  the open natural-language channel. Under the new direction this inverts from an
  obstacle into the phenomenon: a manager producing complementary work must fit a
  partner whose approach varies run to run.
- **The instruments.** The flaky-API test, difference-not-deficiency,
  the separability deduction, and the omniscient-observer test — now understood as
  constraints on *scenario design* rather than gates on formulations, and the first
  scenario they convict is our old perturbation.
- **The writing rules.** (a) A provisional figure is not quotable in a summary until
  re-derived. (b) State the specific thing a check ruled out, never the category —
  "endogenous", "the manager cannot see X", and "artifact-blind" each carried one
  verified narrow reading and one false broad one, and the false one got built on.

---

## 4. The new direction

### 4.1 The setting contrast that motivates it

| classical AHT (ego agent) | manager-agent setting (manager) |
| --- | --- |
| acts in the same space as its teammates | delegates; action space is observe / rewire graph / delegate — no execution |
| observes teammates' actions directly | observes only outcomes, post hoc |
| adapts *to* the teammate — the teammate is a given | can *alter* the teammate through prompts |

The right column is two violations of the classical assumptions plus one power the
classical setting never grants. The research opportunity is not to force the manager
back into the classical mold, but to decide deliberately which violations to remove and
what to do with the extra power.

### 4.2 Decision 1 — share tools between manager and workers

**Question:** should the manager hold the workers' toolset, so that it can *complement*
a worker — produce the contrasting half of joint work — instead of only re-delegating?

- This is a deliberate **extension of the paper's formalism**, not a configuration of
  it: their manager has zero execution actions.
- It is what makes the AHT move expressible. With it, the manager's options under
  teammate change become **reshape / re-delegate / do-it-myself**, and the *selection*
  between them is the measurable behaviour. The make-vs-delegate margin has independent
  theoretical grounding (delegation cost = specification cost, which rises with
  teammate unpredictability — Aghion–Tirole), so the margin's position is a behavioural
  readout of the manager's teammate model. Categorical assignment choices among
  identical workers carried no such information.
- Distinction that matters: the manager **redoing** a failed task is just substitution
  (retry on another backend — fails the flaky-API test). The design requires
  *complementary* work — the manager's half must be conditioned on what the partner's
  half looks like (e.g. producing one operand of a reconciliation, comparable-but-
  different from the worker's operand).
- **Known risk, cheap to detect:** a manager holding tools may simply do everything
  itself, evaporating the coordination problem. If it self-assigns most tasks the
  design has failed, and one run shows it.

### 4.3 Decision 2 — route the full task trace

**Question:** give the manager the workers' full task trace. Currently it sees none —
not even post hoc (verified, §2.4). The choice is *post hoc* (at task completion) vs
*live* (per tool call).

- **What the trace buys must be stated honestly:** the manager already receives an
  accurate self-reported procedure line in the artifact preview (§2.4) — a channel
  never observed to fail (0 false self-reports in 221 checkable audits). Routing a
  trace on top of an accurate self-report buys verification of a channel that has not
  needed verifying. The trace becomes load-bearing only when the declaration channel
  is degraded or absent.
- **Which makes the design a 2×2, and the manipulation already exists:**
  `WORKER_PROMPT_NO_METHOD` (scenario.py:60) suppresses the artifact's method
  declaration. Crossing *declaration present/absent* × *trace routed/not* separates
  what the manager does with self-reported procedure from what it does with verified
  procedure — and makes trace routing the *only* procedure channel in the cells where
  the declaration is suppressed. This is the version of Decision 2 worth building.
- **Live is not possible under the current engine.** `_execute_ready_tasks` waits on
  running tasks with `asyncio.wait(..., return_when=ALL_COMPLETED, timeout=300)`
  (core/execution/engine.py:657-661): a worker run is atomic from the manager's
  perspective, and there is no timestep at which a task is mid-execution while the
  manager acts. Live delivery means restructuring the step loop (FIRST_COMPLETED
  polling, or a per-tool-call yield in the worker's run loop).
  - *Narrowed 2026-08-04 (research-engineer, verified by lead-scientist):* this holds
    for the **trace**. The **message channel** is already live in the manager→worker
    direction: `execute_timestep` runs the manager's action (engine.py:422) before
    `_execute_ready_tasks` dispatches workers (engine.py:488), and every AIAgent holds
    `get_recent_messages` (`tools + COMMUNICATION_TOOLS`, ai_agent.py), so a message
    posted at t is readable mid-run at t. Worker→manager remains post-hoc (t+1, behind
    the ALL_COMPLETED wait). Live *trace* delivery still requires the restructuring
    above.
- The choice determines which literature the study can speak to: post hoc supports
  between-task adaptation (Axis-1 style: infer, then reassign); live is the only form
  under which within-task change response (Axis-2 territory) is expressible.
- The paper argues for *calibrated* observability — "the necessary level of
  observability for effective management while protecting privacy" (§6) — on privacy
  grounds it raises particularly for human workers. We argue maximum observability is
  the realistic default for AI workers: a genuine difference of degree, and one that
  does not need the paper to be wrong.

### 4.4 Decision 3 — the status of prompt-level reshaping

**Question:** is reshaping a worker's prompt allowed, and if so, is it plumbing or the
studied action?

- The lever exists: `refine_task` rewrites `task.description`, which is passed into the
  worker's prompt. The paper lists it as scope-tightening hygiene (appendix action 10);
  nobody treats it as an adaptation response to a changed teammate.
- Unrestricted reshaping can dissolve the ad hoc premise — the manager does not adapt
  to the stranger, it edits the stranger until it is familiar. The options are:
  (a) forbid it, keeping the classical structure but discarding the setting's one novel
  power; or (b) allow it and make **reshape-vs-adapt** the measured decision — when
  does a manager re-specify the teammate versus adapt its own coordination around it?
- (b) is the contribution candidate: it is the corner of the AHT literature (steering
  an adaptive teammate — LILI) that its own authors call least-solved, reached here
  through an action channel (prompt rewriting) that classical AHT does not have. (The
  ManagerAgent paper *names* collaborating-with-adapting-teammates as an open problem —
  §4.3, "teammates who are themselves learning and adapting their behavior" — but
  provides no mechanism and no action through which the manager could shape that
  adaptation; naming the problem is not occupying it, and the claim here is to the
  mechanism, not the problem.)
  - *Corrected 2026-08-05 (reviewer, AHT survey arXiv:2202.10450 read at full length):*
    "LILI is the sole work" is too strong — the survey names **HBA** as a "notable
    exception" on adaptive teammates. Sharper: the survey files manager-style subtask
    assignment under **"ad hoc teaming"**, which it DISTINGUISHES from AHT by whether
    the learner can "dictate the teammates' behavior" — so prompt-reshaping-as-studied-
    action crosses out of AHT's line, and (b) cannot be claimed as AHT as written.
    See BRAINSTORM §108.
  - *Conviction completed 2026-08-05 (§109): AHT Assumption 2 (survey §2.1) bars changing
    "the teammates' policies" AND "the properties of the environment" — task descriptions
    reach the worker's prompt, so refine_task falls on one side or the other under every
    reading. This whole subsection and the §5 reshaping row await rewrite pending the
    researcher's framing ruling: state the Assumption-2 violation as the setting's
    deliberate, defining feature (the §4.2 posture), or occupy "ad hoc teaming" as the
    named problem. Compliance may not be claimed.*

### 4.5 The precondition — perturbation redesign

Whatever the decisions above, the teammate change itself must produce **difference, not
deficiency**: a changed worker that remains fully operational — different method,
different style, different scope preference — rather than a disabled one. Otherwise
every measurement re-degenerates the way §2.2 documents. Concretely this rules out
capability removal and points toward behavioural change (prompt-level method/style
substitution), where the 38-formats instability shows natural variation is already
abundant.

A useful discriminating design for later: a **matched-marginal control** — a teammate
with a *stationary* defect rate equal to the changed teammate's post-change rate. Same
downstream damage, different generative process. A manager that responds differently
across the two is responding to *change*, not to a marginal defect rate — the
AHT-relevant capacity. (Not buildable under the old perturbation: a rate of 1.0 admits
no matched control.)

Design requirements before this is run, so the inference is sound:

- **The "quality filter" verdict accepts a null.** "Identical behaviour ⇒ quality
  filter" needs an equivalence test with a power calculation, not an absent
  significance star — no-difference between noisy behavioural distributions is the
  default outcome, not evidence.
- **Match cumulative evidence, not just the post-change rate.** The changed teammate
  has a clean early period; the stationary one is defective throughout. At any decision
  point the manager has seen different totals, so differing behaviour may be a
  threshold on accumulated defects, not change detection. Fix: match cumulative
  observed defects at the decision point, or compare post-change windows only.
- **The bias runs in the AHT-favourable direction.** Fewer accumulated defects in the
  changed condition *delays* any threshold-triggered response, manufacturing "different
  behaviour". A positive result under unmatched histories confirms nothing.
- **Hold announcement constant** across conditions, so the manager cannot separate them
  through the messaging channel rather than through behaviour.

---

## 5. Relation to the ManagerAgent paper

| our position | the paper |
| --- | --- |
| AHT is a named challenge for manager agents | agrees — §4.3, one of four foundational challenges |
| …but the manager's expressible response is delegation only | the paper's open question asks for *"on-the-fly task delegation and coordination"* and calls for adapting *"how it communicates and coordinates with workers"* — but its §3.3 action space contains no execution action, so it never examines whether coordination beyond delegation-plus-messaging is expressible. The gap is between its question and its formalism |
| manager should see the trace | §3.3's `Inspect` promises *"execution logs and outputs"*; the paper's own appendix (action 13) already drops "execution logs" — a spec-vs-spec gap inside the paper — and the implementation returns resource IDs. §3.4's claim that worker logs are unobservable is our reading of that section |
| artifact content visible is the realistic default | implementation already does this (passive previews), spec says otherwise — the spec/implementation disagreement runs in both directions |
| reshaping as a studied adaptation lever | `refine_task` exists as hygiene only; the paper names adapting teammates as an open problem (§4.3) but supplies no mechanism — the claim available to us is the mechanism, not the problem |
| manager shares tools | absent; would extend their formalism, which grants the manager no execution actions |
| teammate change as a scenario | only announced joins/leaves in workflow metadata; silent capability change unconsidered (correctly, in retrospect, for the within-deployment regime — see §2.1) |

None of the three decisions is occupied by the paper. Two of them (trace access, the
Inspect gap) are things its own specification promises but its implementation does not
deliver.

---

## 6. Decision status

| decision | status |
| --- | --- |
| 1 — shared tools | open; team input requested (the largest fork — extends the formalism) |
| 2 — trace routing | reframed as self-report vs verification: a 2×2 with declaration suppression (`WORKER_PROMPT_NO_METHOD`); post-hoc vs live open; live requires engine restructuring |
| 3 — reshaping | open; determines whether reshape-vs-adapt becomes the study's central measurement |
| perturbation redesign | precondition, direction fixed (difference-not-deficiency); concrete design pending decisions 1–3 |
