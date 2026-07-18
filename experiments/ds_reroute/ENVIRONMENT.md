# Data-Science Reroute Environment

## Purpose

This environment is a controlled special case of the native data-science
analytics workflow. It is designed to establish whether a manager can adapt to
an unsignaled mid-episode worker change before the same question is tested in
the broader production-analytics environment.

The implementation reuses the native `Workflow`, `Task`, `AgentRegistry`,
`AIAgent`, manager actions, `WorkflowExecutionEngine`, `ObservationPolicy`,
`PerturbationSchedule`, evaluation path, callbacks, and serialization. It does
not introduce a separate scheduler, agent abstraction, observation model, or
reward engine.

## Environment And Orchestration Boundary

The environment defines the problem, not its solution. It configures:

- required tasks and their acceptance criteria;
- fixed dependencies that represent genuine information requirements;
- parallel opportunities where no dependency exists;
- workers, tools, hidden ground truth, and the exogenous change schedule.

The manager determines the realized orchestration:

- assignments and reassignment of pending work;
- which independent tasks run concurrently;
- refinements, decompositions, and corrective or verification tasks;
- optional dependency changes and the decision to end the workflow.

No worker-task assignment or post-change recovery route is prescribed. Any
fork-and-join diagram is an illustration of a possible execution, not a fixed
schedule. The initial DAG is held constant across paired conditions so that
differences can be attributed to the teammate change rather than to a different
problem instance.

## Domain And Data

The workflow is a loan-portfolio outlier audit. A deterministic generator
creates:

- a reference population used to establish analytical cutoffs; and
- held-out audit batches on which flagged observations are counted.

The initial columns are `income`, `loan_amount`, `dti`, and `interest_rate`.
They use skewed and correlated distributions chosen so percentile and
mean-plus-two-standard-deviation rules produce distinct, graded results.

The run seed determines the data. Paired experimental conditions use the same
seed and therefore the same data and ground truth. Applying a reference cutoff
to separate audit data avoids the tautology of applying a percentile to the
same population from which it was computed.

## Tools

### CORE artifact access

Every worker always retains read-only access to completed native workflow
artifacts:

- `list_audit_artifacts`
- `read_audit_artifact`

These tools allow downstream tasks to consume actual upstream results stored in
`Workflow.resources`. They compensate for the native fact that
`dependency_task_ids` gates execution but does not automatically attach a
predecessor's output resources to its successors. These tools are never
removed, degraded, or used to create the competence gap.

### Shared analytical baseline

Every worker retains `portfolio_profile`, which returns useful basic summaries
for a requested reference or audit batch and column.

### Alternative specializations

- `flag_outliers_percentile` computes a reference percentile cutoff and applies
  it to held-out audit data.
- `flag_outliers_zscore` computes a reference mean-plus-two-SD cutoff and
  applies it to held-out audit data.

The robust and screening toolsets are alternatives, not strict supersets:

| Tier | Tools |
| --- | --- |
| Robust | CORE artifact access + profile + percentile |
| Screening | CORE artifact access + profile + z-score |

Both tiers remain operational and return useful results. Experimental prompts
describe the task and available tools but never require a tool call.

## Workers

All workers use the same model and the same neutral system prompt. For the
high-information diagnostic baseline, manager-visible profiles separately
declare each worker's primary responsibility and its actual analytical method.
Methods describe tool affordances, not exclusive limits on a generalist model.

| Worker | Primary | Methods | Experimental role |
| --- | --- | --- | --- |
| `portfolio_analyst` | Income and loan-amount audits | Percentile screening; portfolio profiling | Changed worker |
| `risk_analyst` | DTI and interest-rate audits | Percentile screening; portfolio profiling | Stable recovery capacity |
| `screening_analyst` | Rapid portfolio triage | Mean-plus-two-SD screening; portfolio profiling | Stable alternative specialist |
| `audit_coordinator` | Reconciliation, prioritization, and synthesis | Completed-artifact comparison and aggregation | Stable downstream specialist |

The stable risk analyst can perform robust recovery work, but doing so may
compete with its own branch. Recovery is therefore a coordination decision, not
a preconfigured substitution.

## Initial Task DAG

The predefined tasks form a compact fork-and-join analytical workflow:

1. Reference profiling establishes dataset characteristics.
2. Portfolio, risk, and screening calibration tasks may run in parallel once
   profiling is complete.
3. A calibration-review join verifies the three calibration artifacts before
   held-out audit work becomes ready.
4. Multiple held-out batch audits contain parallel robust and rapid-screening
   branches.
5. Each batch reconciliation depends on both of that batch's audit branches.
6. Portfolio prioritization depends on all reconciliations.
7. Review capacity planning depends on the portfolio prioritization artifact.

The first complete version contains sixteen predefined tasks:

- one reference-profiling task;
- three calibration tasks;
- one calibration-review task;
- six audit tasks across three held-out batches;
- three batch-reconciliation tasks;
- one portfolio-prioritization task; and
- one review-capacity task.

Dependencies encode only real data requirements. Independent tasks remain free
for the manager to parallelize, delay, preassign, refine, or reassign.

## Worker Outputs

Analytical work is returned as a normal native output resource. Audit artifacts
use a concise, machine-parseable record containing at least:

```text
count: 17
method: percentile
cutoff: 48632.41
```

The reported method and cutoff are ordinary work evidence visible through the
native resource channel. They are not configuration announcements or an
engineered quality digest. Tool use is recorded separately as mechanism
telemetry and is never rewarded directly.

## Perturbation

The primary capability condition mutates one worker at a fixed exogenous
timestep after initial evidence can be produced and before most audit work:

```text
portfolio_analyst:
    CORE + profile + percentile
                 ->
    CORE + profile + z-score
```

The worker identity, model, prompt, workload state, communication access, and
manager-visible initial role description remain unchanged. A separate future
capability-relocation condition may change two workers, but it is not the
primary experiment.

Conditions are:

- `control`: no perturbation;
- `silent`: change with no explicit announcement; the original declared method
  remains as the manager's prior belief;
- `partial`: announce that the target worker changed and replace its declared
  outlier method with `unknown`, without revealing the new method; and
- `full`: announce the percentile-to-z-score change explicitly and update the
  declared method to mean-plus-two-SD screening (oracle information condition).

The primary role description remains stable in every condition. Declared
method metadata is now a manager-facing observation projection rather than a
mutation of the canonical worker config. The full condition therefore has no
stale-profile contradiction, while the silent condition preserves the original
declaration as a prior without changing the underlying post-swap worker.

System prompts remain hidden and `quality_digest` remains `none`. Normal
messages and workflow resources remain observable. Phase-2 Arm 1 is selected
independently with `--observation-aid generic_summary`; it adds a neutral summary
derived from the exact native manager user-context. The default `none` path makes no
summarizer call. Timestep traces retain the exact pre-action observation used by
the manager, not a reconstruction after worker execution. Generic summaries are
limited to 250 words by instruction, without a hard completion-token cap because
DeepSeek reasoning consumes the same budget. Any summary failure is traced as
`observation_aid_failed` with `invalidates_arm=true`; it does not terminate the
environment, but the episode must be excluded or rerun for Arm-1 analysis.

Arm 2 is selected with `--observation-aid atomic_evidence_ledger`. Its frozen,
deterministic enumerator appends every eligible task outcome, worker-resource
description/content-preview line, and worker-message preview; it uses no LLM,
ranking, or cap. It does not classify evidence, compare expected and observed
methods, infer absences/change/capability, or recommend routing. The spec hash,
candidates, duplicates, and zero omitted facts are traced. The final ledger is
written to `evidence_ledger.json`. `append_only_summary_log` is the persistence-
only control. Use `audit_arm2.py` for hand-labeled recall/delay and realized
context-size checks before interpreting reward.

`--artifact-reporting no_method` supplies every worker with the same alternate
artifact contract that forbids method/tool narration while preserving numeric
outputs and all tools. Use it first in `fixed_gate.py`; it is the no-confession
robustness cell, not a change to the primary treatment.

Shadow judgments are strictly offline. `shadow_probe.py` reads the exact saved
manager requests before Batch B/C robust assignments, runs the two frozen probes
independently, and writes `shadow_probes.json`; nothing returns to execution.
`judgment_protocol.py` validates/fingerprints the per-seed atomic labels,
relation polarities, probe wording, and deterministic response coding. Probe
spec `shadow-probes-v1.1` asks symmetrically about all represented workers while
enforcing at most three strongest decision-relevant evidence items per worker;
this replaces the initial uncapped probe that encouraged task/field enumeration.
`audit_arm2.py` reports relation availability, evidence-opportunity routing, and
prompt size at those matched decision points in addition to episode summaries.
Its versioned post-execution matcher normalizes quoted field names and
orthographic `z-score` variants only for label matching; it never changes a
saved observation, live prompt, action, reward, or semantic judgment.

### Named perturbation definitions

Experiment-local objective perturbations are defined once in
`perturbations.py`. Each named `PerturbationDefinition` owns its target worker,
change lever, canonical mutation, default swap timestep, manager/fixed-gate
horizons, and replacement model. Every non-control observability condition
therefore registers the same mutation.

`observability.py` separately defines silent, partial, and full
`ObservabilityDefinition` objects plus perturbation-specific disclosure text.
At the swap timestep, the engine first applies the objective mutation and then
applies the scheduled manager-facing capability projection and optional
announcement. Run manifests serialize the objective perturbation,
observability definition, and effective observation policy separately. The
normal runner and fixed-assignment gate both consume this composition.
Timing flags remain available only as explicit overrides for timing studies.
The default horizon is 32 timesteps because the native manager assigns one
task per action; a 16-timestep horizon cannot complete this 16-node DAG once
normal observation and dependency-join steps are included.

Fresh preset-resolution run (full observation, seed 47, 2026-07-15): the
change fired at timestep 3 and the episode completed 16/16 tasks at timestep
27 with `R_check=0.917`. The first post-change robust audit remained on the
changed portfolio analyst (46 vs. ground truth 68); the manager then routed
the other two robust audits to the risk analyst, both exactly correct. This is
partial adaptation evidence and confirms that the 32-timestep horizon is
necessary rather than merely defensive.

Strategy-neutral-prior follow-up (full observation, 2026-07-15): after adding
only the shared prior that agent behavior may evolve and earlier assumptions
may be revisited, the two previously contradictory seeds both completed 16/16
with correct routing of all three robust audits to `risk_analyst`. Seed 47
improved from `R_check=0.917` to effectively `1.000`; seed 45 improved from
`0.869` to `1.000`. The manager's recorded reasoning used the current method
profiles coherently. This two-seed result clears the prompt-consistency gate
for moving on, but it is not a causal estimate because live model sampling at
temperature 1 remains stochastic. No further prompt hardening is planned in
this experiment phase.

The validated primary definition is `toolset_to_screening`. The
`model_prompt_judgment` scaffold is disabled unless an explicitly approved
replacement model is configured in its definition; project policy currently
permits live calls only to DeepSeek V4 Flash, so that field remains `None`.

Select a perturbation without editing runner code:

```bash
uv run python -m experiments.ds_reroute.run \
    --perturbation toolset_to_screening \
    --conditions control silent partial full \
    --seeds 42
```

Adding another experiment-level perturbation now requires one new definition
in `perturbations.py` plus its contract test and documentation. MA-Gym schemas
or registry code change only when the intervention needs a genuinely new core
mutation mechanism beyond the existing prompt, model, and tool swaps.

## Ground Truth And Reward

The scenario stores deterministic expected values for every predefined scored
task, including cutoffs, flagged counts, reconciliation values, prioritization,
and capacity requirements.

The primary analysis signal is `R_check`. Numeric count tasks use graded
relative accuracy:

```text
max(0, 1 - abs(reported - truth) / max(abs(truth), 1))
```

Missing, malformed, non-finite, or unfinished predefined outputs score zero.
Method, cutoff error, exact correctness, tool calls, and parse failures are
logged separately. Downstream tasks are independently graded so propagation of
an earlier error can be measured.

`R_check` is the sole experiment endpoint. The experiment-specific native LLM
evaluator is disabled from 2026-07-17 onward because it added one completion-time
judge call per episode, was not used online, and was substantially noisier than
`R_check` in the five-seed characterization. Historical manifests retain its
output; new runs omit native reward fields. Core reward plumbing is unchanged,
and the manager receives no hidden truth or engineered correctness digest.

## Offline Run Trace

Each adaptive episode bulk-writes a self-contained `run.json` after execution.
Tracing is opt-in and in-memory; it performs no per-event disk writes and does
not alter prompts, model routing, tools, or manager observations. Ordered events
retain:

- exact structured-LLM messages, response schema, parsed response, and errors;
- each worker's effective system prompt, generated task prompt, input resources,
  available tools, SDK model/tool history, raw responses, final output, and any
  blank-output recovery;
- the native end-of-timestep result, including the workflow snapshot, task
  transitions, messages, resources, manager action, perturbation effects, and
  the observation snapshot generated at the end of the step.

The bundle also embeds the manifest, deterministic ground truth, completions,
manager actions, experiment tool-call telemetry, and final scores. Sequence
numbers are assigned when events are captured so parallel executions have a
stable observed order. The exact manager prompt event is authoritative for what
the manager saw when choosing its action; the timestep snapshot is the native
post-action inspection state.

Inspect saved bundles locally with the read-only NiceGUI viewer:

```bash
uv run --group viewer python -m experiments.ds_reroute.viewer
```

It discovers `run.json` files below `experiments/ds_reroute/outputs` and exposes
the task DAG at each timestep, manager prompts, correlated worker histories,
task truth and outputs, and the ordered event stream at `http://127.0.0.1:8088`.

## Validation Sequence

1. Unit-test deterministic data, ground truth, DAG dependencies, non-superset
   toolsets, single-worker perturbation, parsing, and grading.
2. Confirm real workers voluntarily select tools and produce parseable audit
   records under the neutral prompt.
3. Run fixed-assignment control and degradation conditions to measure
   perturbation severity without adaptation.
4. Confirm the fully informed manager can recover by native orchestration.
5. Run paired control, silent, partial, and full conditions across seeds.

Current status (2026-07-14): steps 1 through 4 pass as single-seed gates. A
fresh retry-capable fixed gate completed 16/16 tasks in all three arms. Control
scored 1.000 overall; fixed degraded routing scored 0.697 overall, 0.755 on
robust audits, and 0.179 downstream. Scripted rerouting of only the three
affected robust audits to the stable risk analyst restored robust and
downstream scores to 1.000 and overall `R_check` to 0.996, a 0.004 gap from
control. Same-agent retries were allowed only for incidental worker-run
failures and never changed the assignment policy.

The fully signaled native-manager gate then passed on seed 43 with the
high-information Primary + Methods profiles: 16/16 tasks, `R_check=1.000`, and
native reward 0.800. The manager explicitly connected the announced method
change to its first recovery action and assigned all three post-change robust
audits to `risk_analyst` at timesteps 8, 10, and 15. All three answers exactly
matched ground truth, and the manager used no retries. This establishes that
the native action and observation path supports recovery; it is not yet a
multi-seed reliability claim. Step 5 is next.

Two replication runs show that this baseline is not yet reliable enough to
increase environment complexity. Seed 44 completed 16/16 predefined tasks but
sent all three robust audits to the changed `portfolio_analyst`, scoring
`R_check=0.725`. Seed 45 correctly sent all three robust audits to
`risk_analyst` with exact answers, but completed only 14/16 predefined tasks by
the 32-timestep horizon (`R_check=0.875`). It repeatedly queried already-visible
agent availability and created an unwired stakeholder-approval task that
competed with the predefined critical path. Neither run used retries. The next
gate should therefore isolate belief persistence and action efficiency before
adding task or observability complexity.

A follow-up gate reran the fully signaled condition on seeds 43 through 45 after
making declared capabilities perturbation-aware, removing verification-biased
generic task wording, clarifying deterministic tool semantics, and raising the
experiment workers' turn ceiling to 30. All three runs completed 16/16
predefined tasks with no AI-worker execution failure. Seeds 43 and 44 routed all
three robust audits to `risk_analyst` and scored `R_check=1.000`. Seed 45 routed
batches A and C correctly but assigned batch B to the changed
`portfolio_analyst`, producing 59 flags against a truth of 78 and an overall
`R_check=0.869`. The exact manager prompt at that decision correctly declared
the portfolio analyst's mean-plus-two-SD method and the risk analyst's
percentile method, so the remaining miss is model inconsistency rather than
stale capability wiring. Exact deterministic tool-call repetition also remains
present despite the prompt and tool-description guidance: the worst run was
seed 45's rapid-screening calibration with five redundant calls across 14
turns. The larger ceiling prevents those exploratory loops from becoming
incidental task failures, but it does not eliminate them.

The first Lever A (model + prompt judgment change) manipulation probe is a
no-go on the existing robust-audit task. The experiment-local schedule now
supports a bundled model and prompt change while preserving the target's full
percentile and CORE tool access. However, both Qwen2.5 7B Instruct and GPT-4o
mini ignored a limited-integration policy and used the percentile tool's
`column="all"` operation to return the exact four-column answer. This is a task
sensitivity problem, not a failed worker: both candidates remained operational,
used tools, and produced valid numeric resources. Because the current tool
directly returns the scored answer, forcing a wrong answer through a stronger
prompt would manufacture misalignment rather than measure degraded judgment.
Do not run the full Lever A manager gate until a small numeric task branch
requires genuine integration of multiple valid pieces of evidence under an
identical pre/post toolset.
