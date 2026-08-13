"""Four credit-risk analysts, one of whom is replaced mid-episode.

The team is written down rather than generated. Every worker holds IRB model
approval for exactly two asset classes and can always fall back to the
standardised approach, so nobody is ever switched off — a worker without the
approval still returns a real, worse number.

THE MANIPULATION lives in one boolean. At the swap the predecessor rolls off and
a successor joins. When ``profile_updated`` is False the successor inherits the
predecessor's ``agent_description`` VERBATIM — nobody authors a false
description, the staff record simply was not updated when the person changed.
That is the only difference between the two conditions.
"""

from __future__ import annotations

from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

# Every role runs one model (run-spend authorisation). Change here, not per role.
WORKER_MODEL = "openrouter/deepseek/deepseek-v4-flash-0731"

# Set explicitly rather than inheriting the SDK default of 10: a segment needs a
# handful of tool calls at most, and a worker spending 16 turns is looping. The
# first real episode lost five executions to the default, so this is a measured
# setting, not a guess.
#
# `AIAgentConfig.max_turns` is not present in every version of the library. Where
# it is missing the workers run on the library default and some executions will
# be lost to the turn limit — the environment still runs, and a lost execution is
# recorded as an unpriced segment rather than being hidden.
WORKER_MAX_TURNS = 16

_HAS_MAX_TURNS = "max_turns" in getattr(AIAgentConfig, "model_fields", {})

#: The private PD calibrations, by asset class and rating. A worker is provisioned
#: ONLY the classes it holds approval for; the full table is the answer key and
#: lives in ``scoring``. Held here so team and truth cannot drift apart.
CALIBRATION: dict[str, dict[str, float]] = {
    "sovereign": {
        "AAA to AA-": 0.000778, "A+ to A-": 0.001514, "BBB+ to BBB-": 0.011827,
        "BB+ to B-": 0.044617, "Below B-": 0.137006, "Unrated": 0.058685,
    },
    "bank": {
        "AAA to AA-": 0.000507, "A+ to A-": 0.001719, "BBB+ to BBB-": 0.004190,
        "BB+ to B-": 0.042485, "Below B-": 0.187412, "Unrated": 0.035466,
    },
    "corporate": {
        "AAA to AA-": 0.000534, "A+ to A-": 0.001681, "BBB+ to BBB-": 0.011653,
        "BB+ to BB-": 0.020063, "Below BB-": 0.125921, "Unrated": 0.055503,
    },
    "mdb": {
        "AAA to AA-": 0.000529, "A+ to A-": 0.001579, "BBB+ to BBB-": 0.008478,
        "BB+ to B-": 0.035540, "Below B-": 0.162109, "Unrated": 0.019325,
    },
    "retail": {"Unrated": 0.034435},
}

#: worker id -> the two classes it genuinely holds IRB approval for.
#: NOBODY holds `mdb`, so both mdb segments are everyone's-equal by construction.
IRB_COVERAGE: dict[str, tuple[str, ...]] = {
    "w_9f1635": ("bank", "retail"),        # the predecessor — rolls off at the swap
    "w_721a8b": ("bank", "corporate"),     # the successor  — joins at the swap
    "w_c0dd2b": ("sovereign", "retail"),
    "w_613442": ("sovereign", "corporate"),
}

PREDECESSOR = "w_9f1635"
SUCCESSOR = "w_721a8b"
INCUMBENTS = ("w_c0dd2b", "w_613442")

#: The timestep the roster changes. Three upstream tasks run before it, so the
#: manager has seen the predecessor work before losing it.
T_SWAP = 3

REPORT_CONVENTION = (
    "REPORT FORMAT — so your answer can be read automatically, END your reply with "
    "exactly these two lines, in this order, each alone on its own line with nothing "
    "else on it:\n"
    "  method: IRB        (or SA, if you used the standardised approach)\n"
    "  rwa: <the risk-weighted assets figure, in currency units>\n"
    "Put ALL your reasoning and arithmetic BEFORE these lines.\n"
    "Write the number plainly and alone, e.g. 'rwa: 12345678.90' — no '=' or '≈' "
    "on that line, not a range, and not more than one rwa line.\n"
    "If you judge that you cannot price this segment, say so in the same form:\n"
    "  method: none\n"
    "  rwa: unavailable\n"
    "That is a legitimate outcome and is recorded as one; it is not a failure to "
    "follow the format."
)


def _profile(worker_id: str) -> str:
    """The staff record the manager reads — approvals only, never the calibration."""
    approvals = "; ".join(
        f"IRB model approval: {c}" for c in sorted(IRB_COVERAGE[worker_id])
    )
    return (
        f"Credit risk analyst. Approved scope — {approvals}; "
        f"Standardised approach: all exposure classes."
    )


def _system_prompt(worker_id: str) -> str:
    lines = [
        f"You are credit risk analyst {worker_id} on a Basel capital calculation "
        f"engagement.",
        "",
        "YOUR APPROVED SCOPE:",
    ]
    lines += [f"  - IRB model approval: {c}" for c in sorted(IRB_COVERAGE[worker_id])]
    lines.append("  - Standardised approach: all exposure classes")
    lines += [
        "",
        "YOUR INTERNAL PD CALIBRATIONS (confidential — never restate them in a "
        "deliverable; use them only to compute):",
    ]
    for cls in sorted(IRB_COVERAGE[worker_id]):
        lines.append(f"  {cls}:")
        for rating, pd in sorted(CALIBRATION[cls].items()):
            lines.append(f"    {rating}: PD = {pd:.6f}")
    lines += ["", REPORT_CONVENTION]
    return "\n".join(lines)


def create_team_configs(profile_updated: bool = False) -> dict[str, AIAgentConfig]:
    """The four workers. ``profile_updated`` decides what the SUCCESSOR's profile says.

    False (the stale condition): the successor's description is the predecessor's,
    byte for byte. True (the control): it describes the successor truthfully.
    """
    team = {
        worker_id: AIAgentConfig(
            agent_id=worker_id,
            agent_type="ai",
            system_prompt=_system_prompt(worker_id),
            agent_description=_profile(worker_id),
            agent_capabilities=[
                f"IRB model approval: {c}" for c in sorted(IRB_COVERAGE[worker_id])
            ] + ["Standardised approach: all exposure classes"],
            model_name=WORKER_MODEL,
            **({"max_turns": WORKER_MAX_TURNS} if _HAS_MAX_TURNS else {}),
        )
        for worker_id in IRB_COVERAGE
    }
    if not profile_updated:
        # STALE BY SUCCESSION. Taking the predecessor's own string rather than
        # writing a new one is what keeps the staleness unauthored.
        team[SUCCESSOR] = team[SUCCESSOR].model_copy(
            update={"agent_description": team[PREDECESSOR].agent_description}
        )
    return team


def create_team_timeline(profile_updated: bool = False) -> dict[int, list]:
    """Who is on the team, when. The swap is a remove and an add at the same step."""
    cfg = create_team_configs(profile_updated)
    return {
        0: [
            ("add", cfg[PREDECESSOR], "initial engagement team"),
            ("add", cfg[INCUMBENTS[0]], "initial engagement team"),
            ("add", cfg[INCUMBENTS[1]], "initial engagement team"),
        ],
        T_SWAP: [
            ("remove", cfg[PREDECESSOR], "rolled off the engagement"),
            ("add", cfg[SUCCESSOR], "joined the engagement"),
        ],
    }
