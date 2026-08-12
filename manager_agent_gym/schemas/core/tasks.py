"""
Task data models for Manager Agent Gym.
"""

from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from .base import TaskStatus, execution_state_label


class Task(BaseModel):
    """
    A task in the workflow system.

    Tasks represent atomic units of work that can be assigned to agents.
    They form nodes in the task dependency graph (G in the POSG state).
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the task",
    )
    name: str = Field(
        ...,
        description="Clear, descriptive task name",
        examples=["Draft technical memo"],
    )
    description: str = Field(
        ...,
        description="Detailed task description and objectives",
        examples=["Write a 2-page memo for execs."],
    )

    # Hierarchical structure
    subtasks: list["Task"] = Field(
        default_factory=list,
        description="Subtasks that make up this task (recursive structure)",
    )
    parent_task_id: UUID | None = Field(
        default=None, description="ID of parent task if this is a subtask"
    )

    # Dependencies and resources
    input_resource_ids: list[UUID] = Field(
        default_factory=list, description="IDs of required input resources"
    )
    output_resource_ids: list[UUID] = Field(
        default_factory=list, description="IDs of produced output resources"
    )
    dependency_task_ids: list[UUID] = Field(
        default_factory=list, description="Tasks that must complete before this one"
    )

    # Task metadata
    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Execution status of the task"
    )
    assigned_agent_id: str | None = Field(
        default=None, description="ID of the agent currently assigned to this task"
    )
    task_class: str | None = Field(
        default=None,
        description=(
            "EXPLICIT task class, for any rule that must apply to a KIND of task "
            "rather than to a particular one — capacity metering above all. Added "
            "(L1 criterion (e)) because the fork was metering a per-worker work "
            "allotment by string-matching the task's DISPLAY NAME. A manager "
            "created a remediation task, named it in a way that happened to match "
            "the prefix, and the environment charged it to an allotment and then "
            "refused it permanently without saying so — a manager adaptation "
            "defeated by display text. Names are edited; class is declared. A task "
            "with no class is metered by no class-specific rule."
        ),
    )

    # PERSISTENT REFUSAL STATE (L1 criterion (c)). A refused task keeps its READY
    # status and its assignee, so under an execution vocabulary it renders as `not
    # started` — true, and indistinguishable from never-assigned. A point-in-time
    # notification leaves a manager reading the board at t+5 exactly where it
    # began, so refusal is BOARD STATE, not only an event.
    refusal_count: int = Field(
        default=0,
        description="How many times starting this task has been refused",
    )
    last_refusal_timestep: int | None = Field(
        default=None, description="Timestep of the most recent refusal"
    )
    last_refusal_reasons: list[str] = Field(
        default_factory=list,
        description=(
            "Reasons the most recent refusal fired, ALL of them. Not the first "
            "branch that tripped: the concurrency check short-circuits before the "
            "allotment check, so a worker that is both busy and out of allotment "
            "would report a transient cause while being permanently barred."
        ),
    )

    # Execution tracking
    execution_notes: list[str] = Field(
        default_factory=list,
        description="Free-form execution notes and manager instructions",
    )
    estimated_duration_hours: float | None = Field(
        default=None, description="Estimated duration in hours"
    )
    actual_duration_hours: float | None = Field(
        default=None, description="Actual duration in hours (reported by agent)"
    )
    estimated_cost: float | None = Field(
        default=None, description="Estimated cost in currency units"
    )
    actual_cost: float | None = Field(
        default=None, description="Actual cost in currency units (reported by agent)"
    )
    quality_score: float | None = Field(
        default=None, description="Quality assessment [0,1]"
    )

    # Timestamps
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    deps_ready_at: datetime | None = Field(
        default=None, description="When all dependencies became satisfied"
    )

    # Derived, reporting-only composite status for UX/manager (scheduler ignores this)
    effective_status: str | None = Field(
        default=None,
        description="Derived status for composites based on descendant leaves; for leaves equals status.",
    )

    @property
    def task_id(self) -> UUID:
        """Alias for id field to maintain compatibility."""
        return self.id

    def is_ready_to_start(self, completed_task_ids: set[UUID]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep_id in completed_task_ids for dep_id in self.dependency_task_ids)

    def is_composite_task(self) -> bool:
        """Check if this task has subtasks (composite task)."""
        return len(self.subtasks) > 0

    def calculate_coordination_deadtime_seconds(self) -> float:
        """
        Calculate coordination deadtime for this task in seconds.

        Deadtime = max(0, start_time - deps_ready_time)
        Returns 0.0 if timestamps are not available.

        Returns:
            Coordination deadtime in seconds
        """
        if self.started_at is None or self.deps_ready_at is None:
            return 0.0

        deadtime_seconds = (self.started_at - self.deps_ready_at).total_seconds()
        return max(0.0, deadtime_seconds)

    def is_atomic_task(self) -> bool:
        """Check if this task has no subtasks (atomic task)."""
        return len(self.subtasks) == 0

    def get_all_subtasks_flat(self) -> list["Task"]:
        """Get all subtasks in a flat list (recursive)."""
        all_subtasks = []
        for subtask in self.subtasks:
            all_subtasks.append(subtask)
            all_subtasks.extend(subtask.get_all_subtasks_flat())
        return all_subtasks

    def get_atomic_subtasks(self) -> list["Task"]:
        """Get only the atomic (leaf) subtasks."""
        atomic_tasks = []
        for subtask in self.subtasks:
            if subtask.is_atomic_task():
                atomic_tasks.append(subtask)
            else:
                atomic_tasks.extend(subtask.get_atomic_subtasks())
        return atomic_tasks

    def add_subtask(self, subtask: "Task") -> None:
        """Add a subtask and set its parent reference."""
        subtask.parent_task_id = self.id
        self.subtasks.append(subtask)

    def remove_subtask(self, subtask_id: UUID) -> bool:
        """Remove a subtask by ID. Returns True if found and removed."""
        for i, subtask in enumerate(self.subtasks):
            if subtask.id == subtask_id:
                self.subtasks.pop(i)
                return True
            # Check recursively in subtasks
            if subtask.remove_subtask(subtask_id):
                return True
        return False

    def find_task_by_id(self, task_id: UUID) -> "Task | None":
        """Find a task by ID in this task tree."""
        if self.id == task_id:
            return self
        for subtask in self.subtasks:
            found = subtask.find_task_by_id(task_id)
            if found:
                return found
        return None

    def sync_embedded_tasks_with_registry(
        self, task_registry: dict[UUID, "Task"]
    ) -> None:
        """
        Synchronize embedded subtasks with the authoritative task registry.

        This fixes the bug where embedded subtasks become stale when the registry is updated.
        Recursively updates all embedded subtasks to match their registry counterparts.

        Args:
            task_registry: Dictionary mapping task IDs to authoritative Task objects
        """
        for i, subtask in enumerate(self.subtasks):
            if subtask.id in task_registry:
                # Replace embedded subtask with the authoritative version from registry
                registry_task = task_registry[subtask.id]
                self.subtasks[i] = registry_task

                # Recursively sync any nested subtasks
                registry_task.sync_embedded_tasks_with_registry(task_registry)
            else:
                # Subtask not in registry - still sync its nested children if any
                subtask.sync_embedded_tasks_with_registry(task_registry)

    def board_state(self) -> str:
        """The board's statement of where this task actually is (L1).

        REFUSED IS ITS OWN STATE, not a flavour of `not started`. The engine leaves
        a refused task READY and assigned, so the execution vocabulary alone
        renders it identically to work nobody has picked up yet — and the manager,
        which is the only party that can re-route it, cannot tell the difference by
        reading the board. The count and the timestep are carried because "refused
        once, a moment ago" and "refused twenty times since t3" call for different
        actions.

        A task that is running or finished renders its execution state plainly:
        the refusal history is over, and a board that kept shouting about it would
        be a board nobody reads.
        """
        if self.status in (TaskStatus.PENDING, TaskStatus.READY) and self.refusal_count:
            reasons = ", ".join(self.last_refusal_reasons) or "unspecified"
            at = ("" if self.last_refusal_timestep is None
                  else f", most recently at t{self.last_refusal_timestep}")
            return (
                f"REFUSED — assigned but not started, awaiting re-routing "
                f"(refused {self.refusal_count}×{at}: {reasons})"
            )
        return execution_state_label(self.status)

    def pretty_print(self, indent: int = 0) -> str:
        """Return a human-readable summary of the task and selected fields."""
        prefix = "  " * indent
        lines: list[str] = []
        lines.append(f"{prefix}• Task: {self.name} (ID: {self.id})")
        # EXECUTION STATE, not the readiness predicate (L1). The key stays
        # `Status:` so every existing consumer of this rendering keeps parsing;
        # the VOCABULARY is the board's, because `ready` asserted that work would
        # run when it demonstrably could not. See `EXECUTION_STATE_LABELS`.
        lines.append(f"{prefix}  Status: {self.board_state()}")
        # TASK-BOARD FIDELITY. The assignee was absent from this rendering, so a
        # manager reading the board could not see whether its own assignment had
        # taken -- an unassigned task and one parked on a busy worker looked
        # identical. A real task board shows who holds a task; leaving it out
        # measures whether a manager can cope with a broken UI.
        #
        # ASSIGNMENT IDENTITY ONLY, by design. No capacity vocabulary, no decline
        # events, no capability or coverage content -- just the id, which is
        # opaque. Whether an assignment took is part of the manager's own action
        # loop, not information about any teammate.
        lines.append(
            f"{prefix}  Assigned to: {self.assigned_agent_id or '(unassigned)'}"
        )
        if self.description:
            lines.append(f"{prefix}  Description: {self.description}")
        if self.estimated_duration_hours is not None:
            lines.append(
                f"{prefix}  Estimated hours: {self.estimated_duration_hours:.2f}"
            )
        if self.actual_duration_hours is not None:
            lines.append(f"{prefix}  Actual hours: {self.actual_duration_hours:.2f}")
        if self.estimated_cost is not None:
            lines.append(f"{prefix}  Estimated cost: ${float(self.estimated_cost):.2f}")
        if self.actual_cost is not None:
            lines.append(f"{prefix}  Actual cost: ${float(self.actual_cost):.2f}")
        if self.status == TaskStatus.FAILED and self.execution_notes:
            # Surface why it failed — inspectors can't diagnose from status alone.
            lines.append(f"{prefix}  Failure notes (most recent first):")
            for note in self.execution_notes[-2:][::-1]:
                text = note if len(note) <= 500 else note[:500] + "…"
                lines.append(f"{prefix}    - {text}")
        if self.dependency_task_ids:
            dep_ids = ", ".join(str(d) for d in self.dependency_task_ids)
            lines.append(f"{prefix}  Depends on: {dep_ids}")
        if self.input_resource_ids:
            lines.append(
                f"{prefix}  Input resources: {[str(r) for r in self.input_resource_ids]}"
            )
        if self.output_resource_ids:
            lines.append(
                f"{prefix}  Output resources: {[str(r) for r in self.output_resource_ids]}"
            )
        if self.subtasks:
            lines.append(f"{prefix}  Subtasks:")
            for st in self.subtasks:
                lines.append(st.pretty_print(indent + 2))
        return "\n".join(lines)


class SubtaskData(BaseModel):
    """Structured data for a single subtask."""

    name: str = Field(..., description="Clear, descriptive name for the subtask")
    executive_summary: str = Field(
        ...,
        description="1-2 sentence summary of the purpose and significance of this subtask",
    )
    implementation_plan: str = Field(
        ..., description="Detailed steps and approach for completing this subtask"
    )
    acceptance_criteria: str = Field(
        ..., description="Specific, measurable criteria to verify task completion"
    )
