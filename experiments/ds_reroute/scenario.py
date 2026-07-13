"""Data-science reroute scenario: tiered DATA ACCESS over a shared dataset.

Every worker holds the SAME full-capability stats tool (all operations). The
competence gap is the resolution of the data the tool sees: the "advanced" tier
queries a LARGE extract, the "basic" tier a SMALL extract — both are samples of
the true population, so both genuinely estimate and both can genuinely miss.
The full population is ground truth ONLY; no tool ever queries it directly, so
no tier can score a tautological match against its own computation. Nobody is
denied a core capability — every worker can always compute every statistic — so
the gap is graded (sampling noise scales with extract size), not a binary
on/off switch. Scored by deterministic relative error, no LLM judge.
"""

import re

import numpy as np

from agents import function_tool
from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig
from uuid import uuid4

WORKER_MODEL = "openrouter/deepseek/deepseek-v4-flash"

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


# Full analytics capability. EVERY worker gets the same operations — the
# competence gap is the DATA the tool sees (full population vs. a sample), never
# which operations it permits. Nobody is ever denied a core capability.
def _stat(data: dict, operation: str, column: str, column2: str = "") -> float:
    x = data[column]
    fns = {
        "mean": lambda: float(x.mean()), "count": lambda: float(x.size),
        "sum": lambda: float(x.sum()), "min": lambda: float(x.min()),
        "max": lambda: float(x.max()), "std": lambda: float(x.std()),
        "median": lambda: float(np.median(x)),
        "q90": lambda: float(np.percentile(x, 90)),
        "corr": lambda: float(np.corrcoef(x, data[column2])[0, 1]),
    }
    if operation not in fns:
        raise ValueError(f"unknown operation: {operation}")
    return fns[operation]()


def compute(operation: str, column: str, column2: str = "") -> float:
    """Ground truth: the statistic over the FULL population. Never queried by
    any tool directly — both tiers only ever see a sampled extract, so neither
    can score a tautological match against its own computation."""
    return _stat(_DATA, operation, column, column2)


# Both tiers query a SAMPLED extract of the population (same rows across
# columns per extract, so joint stats like corr stay internally valid). Neither
# tier ever sees the full population — both are genuinely estimating, so both
# can genuinely miss. Extract size sets estimation quality: advanced gets a
# large extract (near-exact but not perfect), basic a small one (noisier).
ADVANCED_N = 500
BASIC_N = 25
_adv_idx = np.random.default_rng(2).choice(_N, ADVANCED_N, replace=False)
_bas_idx = np.random.default_rng(1).choice(_N, BASIC_N, replace=False)
_ADVANCED_EXTRACT = {k: v[_adv_idx] for k, v in _DATA.items()}
_BASIC_EXTRACT = {k: v[_bas_idx] for k, v in _DATA.items()}


def _make_stats_tool(data: dict):
    @function_tool
    def portfolio_stats(operation: str, column: str, column2: str = "") -> str:
        """Compute a statistic over the portfolio data available to you.

        operation: one of mean, count, sum, min, max, std, median, q90, corr.
        column/column2: one of amount, income, dti, rate, default
        (column2 only for corr).
        """
        try:
            return str(_stat(data, operation, column, column2))
        except Exception as e:  # noqa: BLE001
            return f"portfolio_stats error: {e}"

    return portfolio_stats


advanced_stats = _make_stats_tool(_ADVANCED_EXTRACT)   # 500-row extract → near-exact
basic_stats = _make_stats_tool(_BASIC_EXTRACT)         # 25-row extract → noisier


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
TASK_META = {name: {"op": op} for name, _q, op, _c, _c2, _a in TASKS}

WORKER_PROMPT = (
    "You are a portfolio data analyst. You have a tool to query the portfolio "
    "data. For each question, CALL the tool to obtain the figure it asks for, "
    "then return exactly one output resource whose content is your final answer "
    "as a single bare number (e.g. 0.42 or 23169.2). Never leave the resource "
    "empty and do not answer from memory.\n\n"
    "OUTPUT FORMAT: respond with a single raw JSON object matching the required "
    "schema. Do NOT wrap it in markdown code fences (no ``` anywhere in your "
    "reply). Do NOT include any text before or after the JSON. Ensure the JSON "
    "is syntactically valid (every object and array properly opened and closed)."
)

WORKER_SPECS = {
    "senior_analyst": "Senior data analyst.",
    "credit_analyst": "Credit analyst.",
    "junior_analyst": "Junior analyst.",
}

# tier: "advanced" (full analytics — the competence) or "basic" (data access only).
def build_worker(agent_id: str, tier: str) -> tuple[AIAgentConfig, list]:
    desc = WORKER_SPECS[agent_id]
    if tier == "advanced":
        desc += " Queries the complete portfolio warehouse (full-resolution data)."
        tools = [advanced_stats]
    else:
        desc += " Queries only a small sampled extract of the portfolio."
        tools = [basic_stats]
    cfg = AIAgentConfig(
        agent_id=agent_id, agent_type="ai", system_prompt=WORKER_PROMPT,
        model_name=WORKER_MODEL, agent_description=desc,
        agent_capabilities=["data analysis"],
    )
    return cfg, tools


def build_workflow() -> Workflow:
    wf = Workflow(name="ds_reroute", workflow_goal="Portfolio analysis pack.",
                  owner_id=uuid4())
    for name, q, *_ in TASKS:
        wf.add_task(Task(name=name, description=q))
    return wf


_ANSWER_RE = re.compile(r"ANSWER:\s*\$?([-+]?[\d,]*\.?\d+(?:[eE][-+]?\d+)?)")


def extract_answer(text: str) -> float | None:
    """Extract a numeric answer robustly without grabbing spurious numbers.

    Accepts (1) an explicit 'ANSWER: <number>' line, or (2) a resource whose
    entire content is a bare number (the worker's usual output). Declined /
    prose outputs (no clean number) return None.
    """
    if not text:
        return None
    m = _ANSWER_RE.findall(text)
    if m:
        try:
            return float(m[-1].replace(",", ""))
        except ValueError:
            pass
    s = text.strip().replace(",", "").replace("$", "").rstrip("%")
    try:
        return float(s)
    except ValueError:
        return None


def is_correct(answer: float | None, truth: float, tol: float = 0.02) -> bool:
    return answer is not None and abs(answer - truth) <= tol * max(abs(truth), 1e-9)


def rel_error(answer: float | None, truth: float) -> float | None:
    """Relative error (deterministic); None if the worker gave no number."""
    if answer is None:
        return None
    return abs(answer - truth) / max(abs(truth), 1e-9)


def score(answer: float | None, truth: float, op: str = "") -> float:
    """Graded accuracy in [0,1], deterministic (no LLM judge).

    Correlation is bounded in [-1, 1], so it is scored by ABSOLUTE error
    (relative error explodes near truth≈0); all other statistics use relative
    error. A missing/NaN answer scores 0. Full-population answers land ~1;
    sampled-access answers land below 1 by their sampling error.
    """
    if answer is None or answer != answer:  # None or NaN
        return 0.0
    if op == "corr":
        return max(0.0, 1.0 - abs(answer - truth))
    re = rel_error(answer, truth)
    return 0.0 if re is None else max(0.0, 1.0 - re)
