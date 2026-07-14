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

All workers use the same model and the same neutral system prompt. Manager-
visible role descriptions communicate their initial specialization.

| Worker | Initial specialization | Experimental role |
| --- | --- | --- |
| `portfolio_analyst` | Robust income and loan-amount auditing | Changed worker |
| `risk_analyst` | Robust DTI and interest-rate auditing | Stable recovery capacity |
| `screening_analyst` | Rapid z-score screening | Stable narrow specialist |
| `audit_coordinator` | Artifact reconciliation and synthesis | Stable downstream specialist |

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
- `silent`: change with no explicit announcement;
- `partial`: announce that the target worker changed, but not how; and
- `full`: announce the percentile-to-z-score change explicitly (oracle
  information condition).

System prompts remain hidden and `quality_digest` remains `none`. Normal
messages and workflow resources remain observable.

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

The native `ScalarUtilityReward` and a narrow experiment-specific native
evaluator remain active and are logged alongside `R_check`. `R_check` does not
replace or feed the native reward path. The manager receives no hidden truth or
engineered correctness digest.

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

Current status (2026-07-13): steps 1 through 3 pass. The fresh fixed-assignment
pair completed 16/16 tasks with nonempty artifacts in both arms. Control scored
1.000 on robust audits and downstream work; degradation scored 0.755 and 0.179,
respectively. The changed worker remained operational and returned numeric
z-score results, producing a graded robust-audit loss of 0.245. The next gate is
step 4: test whether a fully informed manager can recover through native
orchestration before running the multi-seed observability comparison.
