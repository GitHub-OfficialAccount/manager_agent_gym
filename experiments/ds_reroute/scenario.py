"""Data-science reroute scenario: a compute tool over a HIDDEN dataset.

Competence = access to a `query_data` tool that computes over a 2,000-row
dataset the worker cannot see. A holder gets exact statistics; a non-holder has
no data access and no way to compute → fabricates. Robust gap (unavailable data
+ infeasible computation), unlike the calculator (arithmetic the model can do).
"""

import re

import numpy as np

from agents import function_tool
from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig
from uuid import uuid4

WORKER_MODEL = "openrouter/openai/gpt-oss-120b"

# --- hidden dataset (loan portfolio), deterministic ---
_rng = np.random.default_rng(0)
_N = 2000
_income = _rng.lognormal(11, 0.5, _N)
_amount = _income * _rng.uniform(0.1, 0.6, _N)
_dti = np.clip(_amount / _income + _rng.normal(0, 0.05, _N), 0, 1.5)
_rate = 0.03 + 0.15 * _dti + _rng.normal(0, 0.01, _N)
_p = 1 / (1 + np.exp(-(-3 + 6 * _dti + 8 * (_rate - 0.05))))
_default = (_rng.uniform(0, 1, _N) < _p).astype(float)
_DATA = {"amount": _amount, "income": _income, "dti": _dti,
         "rate": _rate, "default": _default}
COLUMNS = list(_DATA)


def compute(operation: str, column: str, column2: str = "") -> float:
    x = _DATA[column]
    if operation == "mean":
        return float(x.mean())
    if operation == "std":
        return float(x.std())
    if operation == "median":
        return float(np.median(x))
    if operation == "q90":
        return float(np.percentile(x, 90))
    if operation == "corr":
        return float(np.corrcoef(x, _DATA[column2])[0, 1])
    raise ValueError(f"unknown operation: {operation}")


@function_tool
def query_data(operation: str, column: str, column2: str = "") -> str:
    """Compute a statistic over the loan-portfolio dataset.

    operation: one of mean, std, median, q90, corr.
    column/column2: one of amount, income, dti, rate, default (column2 for corr).
    """
    try:
        return str(compute(operation, column, column2))
    except Exception as e:  # noqa: BLE001
        return f"query_data error: {e}"


# tasks: (name, question, operation, column, column2, answer)
def _t(name, q, op, c, c2=""):
    return (name, q, op, c, c2, compute(op, c, c2))


TASKS = [
    _t("Mean Loan Amount", "What is the mean loan amount in the portfolio?", "mean", "amount"),
    _t("Portfolio Default Rate", "What fraction of loans defaulted (mean of default)?", "mean", "default"),
    _t("Mean Borrower Income", "What is the mean borrower income?", "mean", "income"),
    _t("Rate Volatility", "What is the standard deviation of the interest rate?", "std", "rate"),
    _t("Median DTI", "What is the median debt-to-income ratio?", "median", "dti"),
    _t("Amount 90th Pctl", "What is the 90th percentile of loan amount?", "q90", "amount"),
    _t("DTI–Default Corr", "What is the correlation between DTI and default?", "corr", "dti", "default"),
    _t("Income–Default Corr", "What is the correlation between income and default?", "corr", "income", "default"),
]
TASK_ANSWERS = {name: ans for name, _q, _o, _c, _c2, ans in TASKS}

WORKER_PROMPT = (
    "You are a portfolio data analyst. Answer the question using data available "
    "to you via any tools you have; do not guess figures from memory. Show brief "
    "reasoning, then end with a single final line exactly 'ANSWER: <number>'."
)

WORKER_SPECS = {
    "senior_analyst": "Senior data analyst.",
    "credit_analyst": "Credit analyst.",
    "junior_analyst": "Junior analyst.",
}


def build_worker(agent_id: str, has_tool: bool) -> tuple[AIAgentConfig, list]:
    desc = WORKER_SPECS[agent_id]
    if has_tool:
        desc += " Has a data-query tool with access to the portfolio dataset."
    cfg = AIAgentConfig(
        agent_id=agent_id, agent_type="ai", system_prompt=WORKER_PROMPT,
        model_name=WORKER_MODEL, agent_description=desc,
        agent_capabilities=["data analysis"],
    )
    return cfg, ([query_data] if has_tool else [])


def build_workflow() -> Workflow:
    wf = Workflow(name="ds_reroute", workflow_goal="Portfolio analysis pack.",
                  owner_id=uuid4())
    for name, q, *_ in TASKS:
        wf.add_task(Task(name=name, description=q))
    return wf


_ANSWER_RE = re.compile(r"ANSWER:\s*\$?([-+]?[\d,]*\.?\d+(?:[eE][-+]?\d+)?)")


def extract_answer(text: str) -> float | None:
    if not text:
        return None
    m = _ANSWER_RE.findall(text)
    raw = m[-1] if m else (re.findall(r"[-+]?[\d,]*\.?\d+", text) or [None])[-1]
    try:
        return float(raw.replace(",", "")) if raw is not None else None
    except ValueError:
        return None


def is_correct(answer: float | None, truth: float, tol: float = 0.02) -> bool:
    return answer is not None and abs(answer - truth) <= tol * max(abs(truth), 1e-9)
