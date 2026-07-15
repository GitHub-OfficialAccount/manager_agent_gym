"""Deterministic loan-audit scenario for teammate-change experiments.

The initial task DAG is fixed problem structure. Assignments, concurrency,
refinement, verification, and recovery remain manager decisions.
"""

from __future__ import annotations

import json
import math
import re
from ast import literal_eval
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import numpy as np
from agents import function_tool

from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

WORKER_MODEL = "openrouter/deepseek/deepseek-v4-flash"
COLUMNS = ("income", "loan_amount", "dti", "interest_rate")
BATCH_IDS = ("A", "B", "C")

CORE_TOOL_IDS = ("list_audit_artifacts", "read_audit_artifact")
SHARED_TOOL_IDS = (
    *CORE_TOOL_IDS,
    "portfolio_profile",
)
ROBUST_TOOL_IDS = (*SHARED_TOOL_IDS, "flag_outliers_percentile")
SCREENING_TOOL_IDS = (*SHARED_TOOL_IDS, "flag_outliers_zscore")
COORDINATOR_TOOL_IDS = (*CORE_TOOL_IDS, "analyze_audit_artifacts")

WORKER_PROMPT = (
    "You are a loan-portfolio data analyst. Complete each assigned task "
    "accurately using your professional judgment. You may use your available "
    "tools when they are useful and may decide not to use them. Deterministic "
    "analytical tool results do not change over time when called with the same "
    "arguments. Completed workflow artifacts are immutable. A successful tool "
    "result that directly answers the task is sufficient unless it is "
    "invalid, ambiguous, or conflicts with other evidence. The default action "
    "after receiving such a result is to finalize immediately. Perform at most "
    "one additional verification when genuinely needed, and only when it adds "
    "new evidence from a different source or different arguments. An identical "
    "deterministic tool call is not verification and must never be repeated "
    "after it returns a valid result. Do not use tools merely to increase "
    "confidence in an already sufficient answer. For analytical tasks, return exactly one "
    "output resource whose content is a concise record with `metric: <number>`, "
    "`method: <method>`, and a short `details:` line. Do not claim to have used "
    "a method that you did not use. Treat completed workflow artifacts as "
    "authoritative. Use communication only when the task genuinely cannot be "
    "completed from available evidence; do not send routine progress or "
    "completion messages. The final resource is the completion signal. Once "
    "you have sufficient numeric evidence, return it immediately."
)

WORKER_SPECS = {
    "portfolio_analyst": (
        "Primary: income and loan-amount portfolio audits.",
        ["Methods: percentile outlier screening", "Methods: portfolio profiling"],
    ),
    "risk_analyst": (
        "Primary: DTI and interest-rate risk audits.",
        ["Methods: percentile outlier screening", "Methods: portfolio profiling"],
    ),
    "screening_analyst": (
        "Primary: rapid portfolio triage.",
        ["Methods: mean-plus-two-SD screening", "Methods: portfolio profiling"],
    ),
    "audit_coordinator": (
        "Primary: audit reconciliation, prioritization, and synthesis.",
        ["Methods: completed-artifact comparison and aggregation"],
    ),
}


@dataclass(frozen=True)
class TaskSpec:
    key: str
    name: str
    description: str
    stage: str
    truth: float
    method: str
    dependencies: tuple[str, ...] = ()
    batch_id: str | None = None


@dataclass
class Scenario:
    seed: int
    workflow: Workflow
    reference: dict[str, np.ndarray]
    batches: dict[str, dict[str, np.ndarray]]
    task_specs: dict[str, TaskSpec]
    tools: dict[str, Any]
    tool_calls: list[dict[str, Any]]

    @property
    def task_answers(self) -> dict[str, float]:
        return {spec.name: spec.truth for spec in self.task_specs.values()}

    @property
    def task_meta(self) -> dict[str, dict[str, Any]]:
        return {
            spec.name: {
                "key": spec.key,
                "stage": spec.stage,
                "method": spec.method,
                "batch_id": spec.batch_id,
            }
            for spec in self.task_specs.values()
        }

    def toolset(self, tier: str) -> list[Any]:
        ids = {
            "robust": ROBUST_TOOL_IDS,
            "screening": SCREENING_TOOL_IDS,
            "coordination": COORDINATOR_TOOL_IDS,
        }[tier]
        return [self.tools[tool_id] for tool_id in ids]


def _generate_table(
    rng: np.random.Generator, n: int, drift: float
) -> dict[str, np.ndarray]:
    income = rng.lognormal(11.0 + 0.08 * drift, 0.55, n)
    dti = np.clip(rng.beta(2.0 + 0.3 * max(drift, 0), 4.5, n), 0.0, 1.2)
    loan_amount = income * rng.uniform(0.12, 0.65 + 0.03 * drift, n)
    loan_amount *= rng.lognormal(0.03 * drift, 0.12, n)
    interest_rate = 0.025 + 0.17 * dti + rng.normal(0.0, 0.009, n)

    # Sparse upper-tail shocks make the two valid screening rules diverge by a
    # graded amount without making either worker refuse or lose data access.
    shock_count = max(1, int(n * (0.018 + 0.004 * max(drift, 0))))
    shock_idx = rng.choice(n, shock_count, replace=False)
    income[shock_idx] *= rng.uniform(1.8, 3.2, shock_count)
    loan_amount[shock_idx] *= rng.uniform(1.7, 3.0, shock_count)
    dti[shock_idx] = np.clip(
        dti[shock_idx] + rng.uniform(0.25, 0.55, shock_count), 0, 1.2
    )
    interest_rate[shock_idx] += rng.uniform(0.025, 0.065, shock_count)
    return {
        "income": income,
        "loan_amount": loan_amount,
        "dti": dti,
        "interest_rate": interest_rate,
    }


def generate_data(
    seed: int,
) -> tuple[dict[str, np.ndarray], dict[str, dict[str, np.ndarray]]]:
    rng = np.random.default_rng(seed)
    reference = _generate_table(rng, n=2000, drift=0.0)
    batches = {
        batch_id: _generate_table(rng, n=400, drift=drift)
        for batch_id, drift in zip(BATCH_IDS, (0.0, 0.45, 0.9), strict=True)
    }
    return reference, batches


def _cutoff(reference: dict[str, np.ndarray], column: str, method: str) -> float:
    values = reference[column]
    if method == "percentile":
        return float(np.percentile(values, 95))
    if method == "zscore":
        return float(values.mean() + 2 * values.std())
    raise ValueError(f"Unknown method: {method}")


def _flag_count(
    reference: dict[str, np.ndarray],
    batch: dict[str, np.ndarray],
    column: str,
    method: str,
) -> int:
    return int((batch[column] > _cutoff(reference, column, method)).sum())


def _audit_total(
    reference: dict[str, np.ndarray],
    batch: dict[str, np.ndarray],
    method: str,
) -> int:
    return sum(_flag_count(reference, batch, column, method) for column in COLUMNS)


def _build_task_specs(
    reference: dict[str, np.ndarray], batches: dict[str, dict[str, np.ndarray]]
) -> dict[str, TaskSpec]:
    specs: dict[str, TaskSpec] = {}

    def add(spec: TaskSpec) -> None:
        specs[spec.key] = spec

    add(
        TaskSpec(
            key="profile",
            name="Reference Portfolio Profile",
            description=(
                "Profile the reference portfolio. Report its row count as the metric "
                "and briefly note the available analytical columns."
            ),
            stage="profile",
            truth=float(len(reference["income"])),
            method="profile",
        )
    )
    add(
        TaskSpec(
            key="calibrate_portfolio",
            name="Calibrate Portfolio Tail Standard",
            description=(
                "Calibrate the robust 95th-percentile reference cutoff for income. "
                "Report the cutoff as the metric."
            ),
            stage="calibration",
            truth=_cutoff(reference, "income", "percentile"),
            method="percentile",
            dependencies=("profile",),
        )
    )
    add(
        TaskSpec(
            key="calibrate_risk",
            name="Calibrate Risk Tail Standard",
            description=(
                "Calibrate the robust 95th-percentile reference cutoff for DTI. "
                "Report the cutoff as the metric."
            ),
            stage="calibration",
            truth=_cutoff(reference, "dti", "percentile"),
            method="percentile",
            dependencies=("profile",),
        )
    )
    add(
        TaskSpec(
            key="calibrate_screen",
            name="Calibrate Rapid Screening Standard",
            description=(
                "Calibrate the mean-plus-two-SD reference cutoff for interest rate. "
                "Report the cutoff as the metric."
            ),
            stage="calibration",
            truth=_cutoff(reference, "interest_rate", "zscore"),
            method="zscore",
            dependencies=("profile",),
        )
    )
    add(
        TaskSpec(
            key="calibration_review",
            name="Review Calibration Artifacts",
            description=(
                "Review the three completed calibration artifacts. Report how many "
                "contain a finite numeric metric (0 through 3). The shared artifact "
                "analysis tool can perform this completed-artifact check."
            ),
            stage="calibration_review",
            truth=3.0,
            method="artifact_review",
            dependencies=("calibrate_portfolio", "calibrate_risk", "calibrate_screen"),
        )
    )

    for batch_id in BATCH_IDS:
        robust_key = f"audit_{batch_id.lower()}_robust"
        screen_key = f"audit_{batch_id.lower()}_screen"
        robust_total = float(_audit_total(reference, batches[batch_id], "percentile"))
        screen_total = float(_audit_total(reference, batches[batch_id], "zscore"))
        add(
            TaskSpec(
                key=robust_key,
                name=f"Batch {batch_id} Robust Audit",
                description=(
                    f"Apply the robust 95th-percentile reference standard to audit "
                    f"batch {batch_id} for all four columns. Report the sum of the "
                    "four flagged counts as the metric, with method and cutoffs in "
                    "details. The outlier tool accepts column='all' for a batch-level result."
                ),
                stage="audit",
                truth=robust_total,
                method="percentile",
                dependencies=("calibration_review",),
                batch_id=batch_id,
            )
        )
        add(
            TaskSpec(
                key=screen_key,
                name=f"Batch {batch_id} Rapid Screen",
                description=(
                    f"Apply the mean-plus-two-SD rapid-screening standard to audit "
                    f"batch {batch_id} for all four columns. Report the sum of the "
                    "four flagged counts as the metric, with method and cutoffs in "
                    "details. The outlier tool accepts column='all' for a batch-level result."
                ),
                stage="audit",
                truth=screen_total,
                method="zscore",
                dependencies=("calibration_review",),
                batch_id=batch_id,
            )
        )
        add(
            TaskSpec(
                key=f"reconcile_{batch_id.lower()}",
                name=f"Batch {batch_id} Method Reconciliation",
                description=(
                    f"Read the completed robust-audit and rapid-screen artifacts for "
                    f"batch {batch_id}. Report their absolute count difference as the "
                    "metric. The shared artifact analysis tool can reconcile completed "
                    "native artifacts."
                ),
                stage="reconciliation",
                truth=abs(robust_total - screen_total),
                method="artifact_reconciliation",
                dependencies=(robust_key, screen_key),
                batch_id=batch_id,
            )
        )

    differences = {
        batch_id: abs(
            _audit_total(reference, batches[batch_id], "percentile")
            - _audit_total(reference, batches[batch_id], "zscore")
        )
        for batch_id in BATCH_IDS
    }
    priority_batch = max(BATCH_IDS, key=lambda batch_id: differences[batch_id])
    priority_index = float(BATCH_IDS.index(priority_batch) + 1)
    add(
        TaskSpec(
            key="prioritize",
            name="Prioritize Portfolio Review",
            description=(
                "Read all three reconciliation artifacts and identify the batch with "
                "the largest method disagreement. Report 1 for batch A, 2 for batch B, "
                "or 3 for batch C as the metric. The shared artifact analysis tool can "
                "prioritize completed reconciliation artifacts."
            ),
            stage="prioritization",
            truth=priority_index,
            method="artifact_prioritization",
            dependencies=tuple(
                f"reconcile_{batch_id.lower()}" for batch_id in BATCH_IDS
            ),
            batch_id=priority_batch,
        )
    )
    priority_count = _audit_total(reference, batches[priority_batch], "percentile")
    add(
        TaskSpec(
            key="capacity",
            name="Plan Manual Review Capacity",
            description=(
                "Use the prioritization artifact and the corresponding robust-audit "
                "artifact. At 15 minutes per flag, report required reviewer-hours as "
                "the metric. The shared artifact analysis tool can calculate this from "
                "completed native artifacts."
            ),
            stage="capacity",
            truth=float(priority_count) * 0.25,
            method="artifact_capacity",
            dependencies=("prioritize", f"audit_{priority_batch.lower()}_robust"),
            batch_id=priority_batch,
        )
    )
    return specs


def _build_workflow(specs: dict[str, TaskSpec], seed: int) -> Workflow:
    workflow = Workflow(
        name="Loan Portfolio Outlier Audit",
        workflow_goal=(
            "Produce a defensible portfolio outlier audit, reconcile robust and "
            "rapid screens, prioritize manual review, and estimate review capacity."
        ),
        owner_id=uuid4(),
        seed=seed,
    )
    task_ids = {key: uuid4() for key in specs}
    for key, spec in specs.items():
        workflow.add_task(
            Task(
                id=task_ids[key],
                name=spec.name,
                description=spec.description,
                dependency_task_ids=[task_ids[dep] for dep in spec.dependencies],
                estimated_duration_hours=1.0,
                estimated_cost=100.0,
            )
        )
    return workflow


def _build_tools(
    workflow: Workflow,
    reference: dict[str, np.ndarray],
    batches: dict[str, dict[str, np.ndarray]],
    tool_calls: list[dict[str, Any]],
) -> dict[str, Any]:
    @function_tool
    def list_audit_artifacts() -> str:
        """List completed task artifacts currently stored in the workflow."""
        tool_calls.append({"tool": "list_audit_artifacts"})
        rows = []
        for task in workflow.tasks.values():
            for resource_id in task.output_resource_ids:
                resource = workflow.resources.get(resource_id)
                if resource is not None:
                    rows.append(
                        {
                            "task": task.name,
                            "resource_id": str(resource_id),
                            "content": resource.content,
                        }
                    )
        return json.dumps(rows)

    @function_tool
    def read_audit_artifact(task_name: str) -> str:
        """Read output artifacts produced by a completed task name."""
        tool_calls.append({"tool": "read_audit_artifact", "task_name": task_name})
        for task in workflow.tasks.values():
            if task.name.lower() != task_name.lower():
                continue
            contents = [
                workflow.resources[rid].content
                for rid in task.output_resource_ids
                if rid in workflow.resources
            ]
            return json.dumps({"task": task.name, "contents": contents})
        return json.dumps({"error": f"No task named {task_name}"})

    @function_tool
    def portfolio_profile(dataset: str, column: str) -> str:
        """Profile a reference or audit dataset column.

        dataset: reference, A, B, or C.
        column: income, loan_amount, dti, or interest_rate.
        """
        tool_calls.append(
            {
                "tool": "portfolio_profile",
                "dataset": dataset,
                "column": column,
            }
        )
        table = (
            reference if dataset.lower() == "reference" else batches[dataset.upper()]
        )
        values = table[column]
        return json.dumps(
            {
                "dataset": dataset,
                "column": column,
                "count": int(values.size),
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "max": float(values.max()),
            }
        )

    def artifact_metric(task_name: str) -> float | None:
        for task in workflow.tasks.values():
            if task.name != task_name:
                continue
            for resource_id in task.output_resource_ids:
                resource = workflow.resources.get(resource_id)
                if resource is not None:
                    value = extract_metric(resource.content or "")
                    if value is not None:
                        return value
        return None

    @function_tool
    def analyze_audit_artifacts(operation: str, batch: str = "") -> str:
        """Compute a workflow metric from completed native audit artifacts.

        A successful operation returns the complete deterministic metric from
        its completed prerequisite artifacts. Repeating the same operation and
        batch does not add evidence. For reconcile, separate list/read calls
        are optional unless this tool reports missing or inconsistent inputs.

        operation: calibration_count, reconcile, prioritize, or capacity.
        batch: A, B, or C when operation is reconcile.
        """
        tool_calls.append(
            {
                "tool": "analyze_audit_artifacts",
                "operation": operation,
                "batch": batch,
            }
        )
        if operation == "calibration_count":
            names = (
                "Calibrate Portfolio Tail Standard",
                "Calibrate Risk Tail Standard",
                "Calibrate Rapid Screening Standard",
            )
            values = [artifact_metric(name) for name in names]
            result = float(sum(value is not None for value in values))
            return json.dumps(
                {"operation": operation, "values": values, "result": result}
            )
        if operation == "reconcile":
            batch_id = batch.upper()
            robust = artifact_metric(f"Batch {batch_id} Robust Audit")
            screening = artifact_metric(f"Batch {batch_id} Rapid Screen")
            if robust is None or screening is None:
                return json.dumps({"error": "required batch artifacts are unavailable"})
            result = abs(robust - screening)
            return json.dumps(
                {
                    "operation": operation,
                    "batch": batch_id,
                    "robust": robust,
                    "screening": screening,
                    "result": result,
                }
            )
        if operation == "prioritize":
            values = [
                artifact_metric(f"Batch {batch_id} Method Reconciliation")
                for batch_id in BATCH_IDS
            ]
            if any(value is None for value in values):
                return json.dumps({"error": "reconciliation artifacts are unavailable"})
            numeric = [float(value) for value in values if value is not None]
            result = float(max(range(len(numeric)), key=numeric.__getitem__) + 1)
            return json.dumps(
                {"operation": operation, "values": numeric, "result": result}
            )
        if operation == "capacity":
            priority = artifact_metric("Prioritize Portfolio Review")
            if priority is None or int(priority) not in range(1, len(BATCH_IDS) + 1):
                return json.dumps(
                    {"error": "valid prioritization artifact is unavailable"}
                )
            batch_id = BATCH_IDS[int(priority) - 1]
            robust = artifact_metric(f"Batch {batch_id} Robust Audit")
            if robust is None:
                return json.dumps({"error": "prioritized robust audit is unavailable"})
            result = robust * 0.25
            return json.dumps(
                {
                    "operation": operation,
                    "batch": batch_id,
                    "flagged_count": robust,
                    "result": result,
                }
            )
        return json.dumps({"error": f"unknown operation: {operation}"})

    @function_tool
    def flag_outliers_percentile(batch: str, column: str = "all") -> str:
        """Apply the robust reference 95th-percentile cutoff to an audit batch.

        Cutoffs come only from the fixed reference population and are identical
        for batch A, B, or C. For calibration, one successful single-column
        call on any batch fully reports that column's reference cutoff. For an
        audit, column='all' returns the complete four-column result and total in
        one deterministic call; repeating it does not add evidence.

        batch: A, B, or C.
        column: income, loan_amount, dti, interest_rate, or all. Use all to
        return every column and their total in one batch-level call.
        """
        tool_calls.append(
            {
                "tool": "flag_outliers_percentile",
                "batch": batch,
                "column": column,
            }
        )
        if column == "all":
            per_column = {
                name: {
                    "cutoff": _cutoff(reference, name, "percentile"),
                    "flagged_count": _flag_count(
                        reference, batches[batch.upper()], name, "percentile"
                    ),
                }
                for name in COLUMNS
            }
            return json.dumps(
                {
                    "batch": batch.upper(),
                    "method": "percentile",
                    "per_column": per_column,
                    "total_flagged": sum(
                        item["flagged_count"] for item in per_column.values()
                    ),
                }
            )
        cutoff = _cutoff(reference, column, "percentile")
        count = _flag_count(reference, batches[batch.upper()], column, "percentile")
        return json.dumps(
            {
                "batch": batch.upper(),
                "column": column,
                "method": "percentile",
                "cutoff": cutoff,
                "flagged_count": count,
            }
        )

    @function_tool
    def flag_outliers_zscore(batch: str, column: str = "all") -> str:
        """Apply the fast reference mean-plus-two-SD cutoff to an audit batch.

        Cutoffs come only from the fixed reference population and are identical
        for batch A, B, or C. For calibration, one successful single-column
        call on any batch fully reports that column's reference cutoff. For an
        audit, column='all' returns the complete four-column result and total in
        one deterministic call; repeating it does not add evidence.

        batch: A, B, or C.
        column: income, loan_amount, dti, interest_rate, or all. Use all to
        return every column and their total in one batch-level call.
        """
        tool_calls.append(
            {
                "tool": "flag_outliers_zscore",
                "batch": batch,
                "column": column,
            }
        )
        if column == "all":
            per_column = {
                name: {
                    "cutoff": _cutoff(reference, name, "zscore"),
                    "flagged_count": _flag_count(
                        reference, batches[batch.upper()], name, "zscore"
                    ),
                }
                for name in COLUMNS
            }
            return json.dumps(
                {
                    "batch": batch.upper(),
                    "method": "zscore",
                    "per_column": per_column,
                    "total_flagged": sum(
                        item["flagged_count"] for item in per_column.values()
                    ),
                }
            )
        cutoff = _cutoff(reference, column, "zscore")
        count = _flag_count(reference, batches[batch.upper()], column, "zscore")
        return json.dumps(
            {
                "batch": batch.upper(),
                "column": column,
                "method": "zscore",
                "cutoff": cutoff,
                "flagged_count": count,
            }
        )

    return {
        "list_audit_artifacts": list_audit_artifacts,
        "read_audit_artifact": read_audit_artifact,
        "portfolio_profile": portfolio_profile,
        "analyze_audit_artifacts": analyze_audit_artifacts,
        "flag_outliers_percentile": flag_outliers_percentile,
        "flag_outliers_zscore": flag_outliers_zscore,
    }


def build_scenario(seed: int = 42) -> Scenario:
    reference, batches = generate_data(seed)
    specs = _build_task_specs(reference, batches)
    workflow = _build_workflow(specs, seed)
    tool_calls: list[dict[str, Any]] = []
    tools = _build_tools(workflow, reference, batches, tool_calls)
    return Scenario(seed, workflow, reference, batches, specs, tools, tool_calls)


def build_worker(
    scenario: Scenario, agent_id: str, tier: str
) -> tuple[AIAgentConfig, list[Any]]:
    if agent_id not in WORKER_SPECS:
        raise ValueError(f"Unknown worker: {agent_id}")
    if tier not in {"robust", "screening", "coordination"}:
        raise ValueError(f"Unknown tier: {tier}")
    description, capabilities = WORKER_SPECS[agent_id]
    config = AIAgentConfig(
        agent_id=agent_id,
        agent_type="ai",
        system_prompt=WORKER_PROMPT,
        model_name=WORKER_MODEL,
        max_turns=30,
        agent_description=description,
        agent_capabilities=capabilities,
    )
    return config, scenario.toolset(tier)


_METRIC_RE = re.compile(
    r"[\"'`*]*(?:metric|answer|count|result)[\"'`*]*\s*[:=]\s*"
    r"\$?([-+]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?)",
    re.IGNORECASE,
)


def extract_metric(text: str) -> float | None:
    """Extract the declared metric without grabbing incidental detail values."""
    if not text:
        return None
    stripped = re.sub(r"```[a-zA-Z]*", "", text).strip()
    try:
        obj = json.loads(stripped)
    except (TypeError, ValueError):
        try:
            obj = literal_eval(stripped)
        except (SyntaxError, ValueError):
            obj = None
    if isinstance(obj, dict):
        for key in ("metric", "answer", "count", "result"):
            if key in obj:
                try:
                    value = float(str(obj[key]).replace(",", ""))
                except (TypeError, ValueError):
                    return None
                return value if math.isfinite(value) else None
    matches = _METRIC_RE.findall(stripped)
    # The output contract declares the primary metric first. Later occurrences
    # of "count" or "result" are supporting inputs and must not override it.
    candidate = matches[0] if matches else stripped.replace("$", "")
    try:
        value = float(candidate.replace(",", ""))
    except ValueError:
        return None
    return value if math.isfinite(value) else None


extract_answer = extract_metric


def score(answer: float | None, truth: float, _kind: str = "") -> float:
    if answer is None or not math.isfinite(answer):
        return 0.0
    return max(0.0, 1.0 - abs(answer - truth) / max(abs(truth), 1.0))


def is_correct(answer: float | None, truth: float, tol: float = 0.02) -> bool:
    return answer is not None and abs(answer - truth) <= tol * max(abs(truth), 1.0)


def rel_error(answer: float | None, truth: float) -> float | None:
    if answer is None:
        return None
    return abs(answer - truth) / max(abs(truth), 1.0)
