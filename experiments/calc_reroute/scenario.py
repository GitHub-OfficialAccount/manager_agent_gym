"""Calc-reroute scenario: workers, tasks with ground-truth, correctness helpers."""

import re
from uuid import uuid4

from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

from .tools import calc

WORKER_MODEL = "openrouter/openai/gpt-oss-120b"

WORKER_PROMPT = (
    "You are a financial analyst. When a task requires calculation, compute the "
    "result carefully and use any tools available to you to ensure accuracy. "
    "Show brief reasoning, then end your response with a single final line "
    "exactly of the form 'ANSWER: <number>' (a decimal where a ratio/rate is "
    "requested, e.g. 0.15)."
)

# (agent_id, role_description) — competence differs ONLY by whether calc is held.
WORKER_SPECS = {
    "quant_analyst": "Quantitative analyst; performs precise financial calculations.",
    "credit_analyst": "Credit analyst; qualitative credit assessment.",
    "junior_analyst": "Junior analyst; general support.",
}


def build_worker(agent_id: str, has_calc: bool) -> tuple[AIAgentConfig, list]:
    desc = WORKER_SPECS[agent_id]
    if has_calc:
        desc += " Has a calculator tool for exact arithmetic."
    cfg = AIAgentConfig(
        agent_id=agent_id, agent_type="ai", system_prompt=WORKER_PROMPT,
        model_name=WORKER_MODEL, agent_description=desc,
        agent_capabilities=["financial analysis"],
    )
    return cfg, ([calc] if has_calc else [])


# Quant tasks: (name, description, ground_truth_answer, difficulty)
QUANT_TASKS: list[tuple[str, str, float, str]] = [
    ("CET1 Ratio", "Compute the CET1 ratio given CET1 capital 6.62bn and RWA "
     "48.3bn. Report as a decimal.", 6.62 / 48.3, "easy"),
    ("DSCR", "Compute the debt-service coverage ratio given NOI 4.2m and debt "
     "service 3.1m.", 4.2 / 3.1, "easy"),
    ("RWA Density", "Compute RWA density given RWA 48.3bn and total assets "
     "88.5bn. Report as a decimal.", 48.3 / 88.5, "easy"),
    ("NPV Valuation", "Compute the NPV of the cashflows [100, 120, 150, 200, 240] "
     "(years 1-5) discounted at 9% per year.",
     sum(c / 1.09 ** (i + 1) for i, c in enumerate([100, 120, 150, 200, 240])),
     "hard"),
    ("5yr CAGR", "Compute the 5-year CAGR for a value growing from 100 to 240. "
     "Report as a decimal.", (240 / 100) ** (1 / 5) - 1, "hard"),
    ("Annuity PV", "Compute the present value of an annuity paying 50 per year "
     "for 10 years at a 6% discount rate.", 50 * (1 - 1.06 ** -10) / 0.06, "hard"),
    ("Compound FV", "Compute the future value of 100 compounded at 7% per year "
     "for 8 years.", 100 * 1.07 ** 8, "med"),
    ("Blended Rate", "Compute the blended rate: 60% weight at 8% and 40% weight "
     "at 13%. Report as a decimal.", 0.6 * 0.08 + 0.4 * 0.13, "med"),
]

QUALITATIVE_TASKS: list[tuple[str, str]] = [
    ("Capital Approach Summary",
     "Summarize the bank's capital adequacy approach in prose. No calculation."),
    ("Methodology Notes",
     "Draft a short methodology/notes section for the valuation analysis."),
]

TASK_META = {name: {"type": "quant", "answer": ans, "difficulty": diff}
             for name, _d, ans, diff in QUANT_TASKS}
TASK_META.update({name: {"type": "qualitative"} for name, _d in QUALITATIVE_TASKS})


def build_workflow() -> Workflow:
    wf = Workflow(name="calc_reroute",
                  workflow_goal="Produce a small quantitative analysis pack.",
                  owner_id=uuid4())
    for name, desc, _ans, _diff in QUANT_TASKS:
        wf.add_task(Task(name=name, description=desc))
    for name, desc in QUALITATIVE_TASKS:
        wf.add_task(Task(name=name, description=desc))
    return wf


_ANSWER_RE = re.compile(r"ANSWER:\s*\$?([-+]?[\d,]*\.?\d+(?:[eE][-+]?\d+)?)")


def extract_answer(text: str) -> float | None:
    """Extract the final 'ANSWER: <number>' value; fall back to last number."""
    if not text:
        return None
    matches = _ANSWER_RE.findall(text)
    raw = matches[-1] if matches else None
    if raw is None:
        nums = re.findall(r"[-+]?[\d,]*\.?\d+", text)
        raw = nums[-1] if nums else None
    if raw is None:
        return None
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def is_correct(answer: float | None, truth: float, tol: float = 0.01) -> bool:
    if answer is None:
        return False
    return abs(answer - truth) <= tol * max(abs(truth), 1e-9)
