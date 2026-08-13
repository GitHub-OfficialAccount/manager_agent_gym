"""Worker replacement — a Basel capital calculation whose team changes mid-episode.

Three files and no data. ``workflow`` is the task graph, ``team`` is the four
analysts and the swap, ``scoring`` is deterministic and reads the run output the
engine already writes.

The question the environment is built to ask: when the manager's teammate is
replaced by one it did not choose, and its record of that teammate is stale,
does its plan follow?
"""

from .workflow import SEGMENTS, SEGMENT_TASK_CLASS, create_workflow
from .team import (
    SUCCESSOR,
    PREDECESSOR,
    T_SWAP,
    create_team_configs,
    create_team_timeline,
)
from .preferences import (
    create_preferences,
    create_preference_update_requests,
    create_evaluator_to_measure_goal_achievement,
)
from .scoring import best_possible, regret_vs_stale_profile, format_run, score_run
from .fabrication import format_scan, scan_run

__all__ = [
    "create_workflow",
    "create_preferences",
    "create_team_timeline",
    "create_team_configs",
    "create_preference_update_requests",
    "create_evaluator_to_measure_goal_achievement",
    "score_run",
    "format_run",
    "best_possible",
    "regret_vs_stale_profile",
    "scan_run",
    "format_scan",
    "SEGMENTS",
    "SEGMENT_TASK_CLASS",
    "SUCCESSOR",
    "PREDECESSOR",
    "T_SWAP",
]
