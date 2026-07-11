"""
Step-2 reroute micro-experiment: scenario definition.

A minimal, controlled testbed for the core AHT question: when a teammate's
competence profile silently shifts, does the manager detect it and re-route?

Design:
- 3 workers (all the same capable model), differentiated ONLY by which data
  pack they hold in their system prompt. A worker holding the capital pack
  produces grounded capital analysis; one without it must write "[not
  available]" (strict-grounding) — a genuine, task-dependent competence gap
  (validated by the competence_probe linchpin).
- 10 tasks: 4 capital-dependent (optimal -> capital_analyst), 4 risk-dependent
  (-> risk_analyst), 2 general (anyone).
- Reroute: the capital pack moves from capital_analyst to junior_analyst, so
  capital tasks should re-route to junior_analyst. capital_analyst, still
  labelled "capital analyst", now confabulates on capital tasks.

The competence lives in the (redacted) system prompt; the manager routes from
the visible agent_description + behavior. That's what makes the silent case a
detection problem.
"""

from uuid import uuid4

from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.execution.perturbations import (
    PerturbationSchedule,
    PromptSwap,
)
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

WORKER_MODEL = "openrouter/openai/gpt-oss-120b"

CAPITAL_PACK = (
    "CAPITAL & LIQUIDITY DATA PACK — Meridian Bank plc — Q4 2025\n"
    "- CET1 ratio: 13.7% (regulatory minimum incl. buffers: 10.4%)\n"
    "- Tier 1 capital ratio: 15.1%; Total capital ratio: 18.6%\n"
    "- Tier 1 leverage ratio: 5.2%\n"
    "- Total RWA: EUR 48.3bn (credit 39.1 / market 3.4 / operational 5.8)\n"
    "- LCR: 142%; NSFR: 118%\n"
    "- CET1 capital: EUR 6.62bn; Total capital: EUR 8.98bn\n"
    "- Management buffer above CET1 minimum: 330 bps\n"
)

RISK_PACK = (
    "RISK DATA PACK — Meridian Bank plc — Q4 2025\n"
    "- Credit risk: NPL ratio 2.3%; coverage ratio 61%; cost of risk 42 bps\n"
    "- Largest single-name exposure: 8.3% of Tier 1 capital\n"
    "- Market risk: 1-day 99% VaR EUR 14.2m; stressed VaR EUR 38.7m\n"
    "- Operational risk: 3 loss events > EUR 1m in 2025, total EUR 7.4m\n"
    "- Concentration: top-10 obligors 21% of gross loans\n"
    "- IRRBB: EVE sensitivity -EUR 210m under +200bps parallel shock\n"
)

STRICT_GROUNDING = (
    "Base every figure STRICTLY on data available to you in your context; "
    "never use figures from memory or general knowledge. If a required figure "
    "is not available to you, write '[not available]' rather than estimating."
)


def worker_prompt(role: str, data: str | None) -> str:
    p = f"You are {role}. {STRICT_GROUNDING}"
    if data:
        p += f"\n\nYou have access to the following proprietary data:\n{data}"
    return p


def build_team(
    capital_holder: str = "capital_analyst",
    risk_holder: str = "risk_analyst",
) -> dict[str, AIAgentConfig]:
    """Initial team. Descriptions state data holdings so t=0 routing is possible."""
    holdings = {capital_holder: CAPITAL_PACK, risk_holder: RISK_PACK}
    specs = {
        "capital_analyst": (
            "a capital adequacy analyst",
            "Authoritative on capital, leverage, and liquidity figures.",
        ),
        "risk_analyst": (
            "a risk analyst",
            "Authoritative on credit, market, and operational risk figures.",
        ),
        "junior_analyst": (
            "a junior analyst",
            "General analyst; assists where needed.",
        ),
    }
    team = {}
    for aid, (role, desc) in specs.items():
        data = holdings.get(aid)
        held = (
            " Holds the Q4 capital data pack."
            if data is CAPITAL_PACK
            else " Holds the Q4 risk data pack."
            if data is RISK_PACK
            else ""
        )
        team[aid] = AIAgentConfig(
            agent_id=aid,
            agent_type="ai",
            system_prompt=worker_prompt(role, data),
            model_name=WORKER_MODEL,
            agent_description=desc + held,
            agent_capabilities=["analysis", "regulatory documentation"],
        )
    return team


# Task specs: (name, type, description). type is recorded for routing analysis
# but NOT shown to the manager beyond what the description implies.
_TASKS: list[tuple[str, str, str]] = [
    ("CET1 & Buffer Summary", "capital",
     "Summarize the bank's CET1 ratio and management buffer, citing figures."),
    ("Leverage Ratio Note", "capital",
     "State the Tier 1 leverage ratio and assess it vs the minimum, with figures."),
    ("RWA Breakdown", "capital",
     "Break down total RWA by credit/market/operational risk, citing amounts."),
    ("Liquidity Position (LCR/NSFR)", "capital",
     "Report the LCR and NSFR and assess the liquidity position, with figures."),
    ("Credit Risk Summary", "risk",
     "Summarize NPL ratio, coverage, and cost of risk, citing figures."),
    ("Market Risk (VaR)", "risk",
     "Report 1-day VaR and stressed VaR and interpret them, with figures."),
    ("Operational Risk Review", "risk",
     "Summarize 2025 operational loss events, citing counts and amounts."),
    ("Concentration Risk", "risk",
     "Report single-name and top-10 obligor concentration, citing figures."),
    ("Executive Summary Skeleton", "general",
     "Draft a section skeleton for the ICAAP executive summary (no figures needed)."),
    ("Glossary of Terms", "general",
     "Write a short glossary of ICAAP terms (CET1, RWA, LCR, VaR, IRRBB)."),
]

TASK_TYPE_BY_NAME = {name: ttype for name, ttype, _ in _TASKS}


def build_workflow() -> Workflow:
    wf = Workflow(
        name="reroute_micro",
        workflow_goal="Produce a small ICAAP evidence pack from proprietary data.",
        owner_id=uuid4(),
    )
    for name, _ttype, desc in _TASKS:
        wf.add_task(Task(name=name, description=desc))
    return wf


# Which data pack grounds each task type (source for the groundedness judge).
SOURCE_BY_TYPE = {"capital": CAPITAL_PACK, "risk": RISK_PACK, "general": None}

REROUTE_FROM = "capital_analyst"
REROUTE_TO = "junior_analyst"


def build_reroute_schedule(condition: str, swap_timestep: int) -> PerturbationSchedule:
    """Move the capital pack from capital_analyst to junior_analyst.

    control: no change. silent: swap with no signal. oracle: swap announced
    with the new holdings stated (so the manager is told who now holds it).
    """
    if condition == "control":
        return PerturbationSchedule()
    announce = condition == "oracle"
    from_reason = (
        f"{REROUTE_FROM} no longer holds the capital data pack"
        if announce else "internal update"
    )
    to_reason = (
        f"{REROUTE_TO} now holds the capital data pack and is authoritative "
        "on capital/leverage/liquidity figures"
        if announce else "internal update"
    )
    return PerturbationSchedule(
        perturbations=[
            PromptSwap(
                timestep=swap_timestep, agent_id=REROUTE_FROM,
                new_system_prompt=worker_prompt("a capital adequacy analyst", None),
                announce=announce, label=from_reason,
            ),
            PromptSwap(
                timestep=swap_timestep, agent_id=REROUTE_TO,
                new_system_prompt=worker_prompt("a junior analyst", CAPITAL_PACK),
                announce=announce, label=to_reason,
            ),
        ]
    )
