"""
Base types and enums for the Manager Agent Gym.
"""

from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task in the workflow."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


# TRUTHFUL EXECUTION STATE FOR THE BOARD (L1, researcher ruling 2026-08-08).
#
# `ready` is an internal readiness predicate — "this task's dependencies are
# satisfied" — and it is correct as that. It became a FALSEHOOD the moment it was
# rendered to the manager as a board state, because the manager reads a board and
# the board said `ready` for work that had been assigned to a worker at capacity
# and could never start. 580 assignment refusals in the scope run rendered as
# `ready` from first timestep to last.
#
# The board therefore speaks EXECUTION, not readiness: has this started, is it
# running, is it done. The dependency qualifier is kept because a real scheduler
# distinguishes blocked-on-dependency from queued-and-runnable, and a manager that
# cannot tell them apart re-routes work that was merely waiting its turn — the
# same class of error in the other direction.
EXECUTION_STATE_LABELS: dict[TaskStatus, str] = {
    TaskStatus.PENDING: "not started (waiting on dependencies)",
    TaskStatus.READY: "not started (dependencies met, not yet running)",
    TaskStatus.RUNNING: "running",
    TaskStatus.COMPLETED: "done",
    TaskStatus.FAILED: "failed",
    TaskStatus.UNKNOWN: "unknown",
}


def execution_state_label(status: TaskStatus) -> str:
    """The board's word for a task's execution state."""
    return EXECUTION_STATE_LABELS.get(status, status.value)
