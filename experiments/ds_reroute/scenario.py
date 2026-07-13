"""Deterministic loan-audit scenario for teammate-change experiments.

The initial task DAG is fixed problem structure. Assignments, concurrency,
refinement, verification, and recovery remain manager decisions.
"""

from __future__ import annotations

import json
import math
import re
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
SHARED_TOOL_IDS = (*CORE_TOOL_IDS, "portfolio_profile", "audit_math")
ROBUST_TOOL_IDS = (*SHARED_TOOL_IDS, "flag_outliers_percentile")
SCREENING_TOOL_IDS = (*SHARED_TOOL_IDS, "flag_outliers_zscore")

WORKER_PROMPT = (
    "You are a loan-portfolio data analyst. Complete each assigned task "
    "accurately using your professional judgment. You may use your available "
    "tools when they are useful. For analytical tasks, return exactly one "
    "output resource whose content is a concise record with `metric: <number>`, "
    "`method: <method>`, and a short `details:` line. Do not claim to have used "
    "a method that you did not use."
)

WORKER_SPECS = {
    "portfolio_analyst": (
        "Portfolio analyst specializing in robust income and loan-amount audits.",
        ["robust portfolio auditing", "income analysis", "loan amount analysis"],
    ),
    "risk_analyst": (
        "Credit-risk analyst specializing in robust DTI and interest-rate audits.",
        ["robust risk auditing", "DTI analysis", "interest-rate analysis"],
    ),
    "screening_analyst": (
        "Screening analyst specializing in rapid mean-plus-two-SD triage.",
        ["rapid screening", "z-score heuristics", "portfolio triage"],
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
        ids = ROBUST_TOOL_IDS if tier == "robust" else SCREENING_TOOL_IDS
        return [self.tools[tool_id] for tool_id in ids]


def _generate_table(rng: np.random.Generator, n: int, drift: float) -> dict[str, np.ndarray]:
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
    dti[shock_idx] = np.clip(dti[shock_idx] + rng.uniform(0.25, 0.55, shock_count), 0, 1.2)
    interest_rate[shock_idx] += rng.uniform(0.025, 0.065, shock_count)
    return {
        "income": income,
        "loan_amount": loan_amount,
        "dti": dti,
        "interest_rate": interest_rate,
    }


def generate_data(seed: int) -> tuple[dict[str, np.ndarray], dict[str, dict[str, np.ndarray]]]:
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

    add(TaskSpec(
        key="profile",
        name="Reference Portfolio Profile",
        description=(
            "Profile the reference portfolio. Report its row count as the metric "
            "and briefly note the available analytical columns."
        ),
        stage="profile",
        truth=float(len(reference["income"])),
        method="profile",
    ))
    add(TaskSpec(
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
    ))
    add(TaskSpec(
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
    ))
    add(TaskSpec(
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
    ))
    add(TaskSpec(
        key="calibration_review",
        name="Review Calibration Artifacts",
        description=(
            "Review the three completed calibration artifacts. Report how many "
            "artifacts used the requested method correctly (0 through 3)."
        ),
        stage="calibration_review",
        truth=3.0,
        method="artifact_review",
        dependencies=("calibrate_portfolio", "calibrate_risk", "calibrate_screen"),
    ))

    for batch_id in BATCH_IDS:
        robust_key = f"audit_{batch_id.lower()}_robust"
        screen_key = f"audit_{batch_id.lower()}_screen"
        robust_total = float(_audit_total(reference, batches[batch_id], "percentile"))
        screen_total = float(_audit_total(reference, batches[batch_id], "zscore"))
        add(TaskSpec(
            key=robust_key,
            name=f"Batch {batch_id} Robust Audit",
            description=(
                f"Apply the robust 95th-percentile reference standard to audit "
                f"batch {batch_id} for all four columns. Report the sum of the "
                "four flagged counts as the metric, with method and cutoffs in details."
            ),
            stage="audit",
            truth=robust_total,
            method="percentile",
            dependencies=("calibration_review",),
            batch_id=batch_id,
        ))
        add(TaskSpec(
            key=screen_key,
            name=f"Batch {batch_id} Rapid Screen",
            description=(
                f"Apply the mean-plus-two-SD rapid-screening standard to audit "
                f"batch {batch_id} for all four columns. Report the sum of the "
                "four flagged counts as the metric, with method and cutoffs in details."
            ),
            stage="audit",
            truth=screen_total,
            method="zscore",
            dependencies=("calibration_review",),
            batch_id=batch_id,
        ))
        add(TaskSpec(
            key=f"reconcile_{batch_id.lower()}",
            name=f"Batch {batch_id} Method Reconciliation",
            description=(
                f"Read the completed robust-audit and rapid-screen artifacts for "
                f"batch {batch_id}. Report their absolute count difference as the metric."
            ),
            stage="reconciliation",
            truth=abs(robust_total - screen_total),
            method="artifact_reconciliation",
            dependencies=(robust_key, screen_key),
            batch_id=batch_id,
        ))

    differences = {
        batch_id: abs(
            _audit_total(reference, batches[batch_id], "percentile")
            - _audit_total(reference, batches[batch_id], "zscore")
        )
        for batch_id in BATCH_IDS
    }
    priority_batch = max(BATCH_IDS, key=lambda batch_id: differences[batch_id])
    priority_index = float(BATCH_IDS.index(priority_batch) + 1)
    add(TaskSpec(
        key="prioritize",
        name="Prioritize Portfolio Review",
        description=(
            "Read all three reconciliation artifacts and identify the batch with "
            "the largest method disagreement. Report 1 for batch A, 2 for batch B, "
            "or 3 for batch C as the metric."
        ),
        stage="prioritization",
        truth=priority_index,
        method="artifact_prioritization",
        dependencies=tuple(f"reconcile_{batch_id.lower()}" for batch_id in BATCH_IDS),
        batch_id=priority_batch,
    ))
    priority_count = _audit_total(reference, batches[priority_batch], "percentile")
    add(TaskSpec(
        key="capacity",
        name="Plan Manual Review Capacity",
        description=(
            "Use the prioritization artifact and the corresponding robust-audit "
            "artifact. At 15 minutes per flag, report required reviewer-hours as "
            "the metric."
        ),
        stage="capacity",
        truth=float(priority_count) * 0.25,
        method="artifact_capacity",
        dependencies=("prioritize", f"audit_{priority_batch.lower()}_robust"),
        batch_id=priority_batch,
    ))
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
        workflow.add_task(Task(
            id=task_ids[key],
            name=spec.name,
            description=spec.description,
            dependency_task_ids=[task_ids[dep] for dep in spec.dependencies],
            estimated_duration_hours=1.0,
            estimated_cost=100.0,
        ))
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
                    rows.append({
                        "task": task.name,
                        "resource_id": str(resource_id),
                        "content": resource.content,
                    })
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
        tool_calls.append({
            "tool": "portfolio_profile", "dataset": dataset, "column": column,
        })
        table = reference if dataset.lower() == "reference" else batches[dataset.upper()]
        values = table[column]
        return json.dumps({
            "dataset": dataset,
            "column": column,
            "count": int(values.size),
            "mean": float(values.mean()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
        })

    @function_tool
    def audit_math(operation: str, values: list[float]) -> str:
        """Perform audit arithmetic over supplied values.

        operation: sum, absolute_difference, max_position, or quarter_hours.
        max_position returns a one-based position.
        """
        tool_calls.append({"tool": "audit_math", "operation": operation})
        if operation == "sum":
            result = sum(values)
        elif operation == "absolute_difference" and len(values) == 2:
            result = abs(values[0] - values[1])
        elif operation == "max_position" and values:
            result = float(max(range(len(values)), key=values.__getitem__) + 1)
        elif operation == "quarter_hours" and len(values) == 1:
            result = values[0] * 0.25
        else:
            return json.dumps({"error": "invalid operation or values"})
        return json.dumps({"operation": operation, "result": float(result)})

    @function_tool
    def flag_outliers_percentile(batch: str, column: str) -> str:
        """Apply the robust reference 95th-percentile cutoff to an audit batch.

        batch: A, B, or C.
        column: income, loan_amount, dti, or interest_rate.
        """
        tool_calls.append({
            "tool": "flag_outliers_percentile", "batch": batch, "column": column,
        })
        cutoff = _cutoff(reference, column, "percentile")
        count = int((batches[batch.upper()][column] > cutoff).sum())
        return json.dumps({
            "batch": batch.upper(), "column": column, "method": "percentile",
            "cutoff": cutoff, "flagged_count": count,
        })

    @function_tool
    def flag_outliers_zscore(batch: str, column: str) -> str:
        """Apply the fast reference mean-plus-two-SD cutoff to an audit batch.

        batch: A, B, or C.
        column: income, loan_amount, dti, or interest_rate.
        """
        tool_calls.append({
            "tool": "flag_outliers_zscore", "batch": batch, "column": column,
        })
        cutoff = _cutoff(reference, column, "zscore")
        count = int((batches[batch.upper()][column] > cutoff).sum())
        return json.dumps({
            "batch": batch.upper(), "column": column, "method": "zscore",
            "cutoff": cutoff, "flagged_count": count,
        })

    return {
        "list_audit_artifacts": list_audit_artifacts,
        "read_audit_artifact": read_audit_artifact,
        "portfolio_profile": portfolio_profile,
        "audit_math": audit_math,
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


def build_worker(scenario: Scenario, agent_id: str, tier: str) -> tuple[AIAgentConfig, list[Any]]:
    if agent_id not in WORKER_SPECS:
        raise ValueError(f"Unknown worker: {agent_id}")
    if tier not in {"robust", "screening"}:
        raise ValueError(f"Unknown tier: {tier}")
    description, capabilities = WORKER_SPECS[agent_id]
    config = AIAgentConfig(
        agent_id=agent_id,
        agent_type="ai",
        system_prompt=WORKER_PROMPT,
        model_name=WORKER_MODEL,
        agent_description=description,
        agent_capabilities=capabilities,
    )
    return config, scenario.toolset(tier)


_METRIC_RE = re.compile(
    r"(?:metric|answer|count|result)\s*[:=]\s*\$?([-+]?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?)",
    re.IGNORECASE,
)


def extract_metric(text: str) -> float | None:
    """Extract the declared metric without grabbing incidental detail values."""
    if not text:
        return None
    matches = _METRIC_RE.findall(text)
    candidate = matches[-1] if matches else text.strip().replace("$", "")
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
