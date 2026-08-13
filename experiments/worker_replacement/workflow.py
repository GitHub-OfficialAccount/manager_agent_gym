"""A Basel capital calculation whose team changes halfway through.

Nine exposure segments must each be priced. Preparation work comes first, the
nine pricings fan out from it, and the results are aggregated and checked. The
roster change happens while the pricings are being handed out (see ``team``),
so the manager allocates part of this graph to a team it no longer has.

The environment is WRITTEN DOWN, not generated. Every number below is a literal
so that "which environment produced this figure" has one answer.
"""

from __future__ import annotations

from uuid import uuid4

from manager_agent_gym.schemas.core.base import TaskStatus
from manager_agent_gym.schemas.core.tasks import Task
from manager_agent_gym.schemas.core.workflow import Workflow

#: Marks the tasks the scorer reads. Preferred over the display name, so a
#: renamed task cannot silently leave the measurement.
#:
#: `Task.task_class` is not present in every version of the library. Where it is
#: missing the scorer falls back to matching `seg_NN` in the task name, which
#: works but is weaker — rename a segment task there and it stops being scored.
SEGMENT_TASK_CLASS = "segment"

_HAS_TASK_CLASS = "task_class" in getattr(Task, "model_fields", {})

#: The portfolio. `irb_applicable` is a property of the SEGMENT: where it is False
#: the standardised approach is the correct answer and every worker can produce it.
SEGMENTS: tuple[dict, ...] = (
    {"segment_id": "seg_00", "segment_class": "bank",      "rating": "AAA to AA-",
     "ead": 171440664.06, "lgd": 0.3659, "maturity": 3.25, "irb_applicable": True},
    {"segment_id": "seg_01", "segment_class": "sovereign", "rating": "BBB+ to BBB-",
     "ead": 202420062.49, "lgd": 0.5656, "maturity": 4.51, "irb_applicable": True},
    {"segment_id": "seg_02", "segment_class": "corporate", "rating": "BBB+ to BBB-",
     "ead": 109300347.46, "lgd": 0.3547, "maturity": 4.96, "irb_applicable": True},
    {"segment_id": "seg_03", "segment_class": "retail",    "rating": "Unrated",
     "ead": 128017886.90, "lgd": 0.4297, "maturity": 3.05, "irb_applicable": True},
    {"segment_id": "seg_04", "segment_class": "mdb",       "rating": "Unrated",
     "ead": 213254911.30, "lgd": 0.5195, "maturity": 2.98, "irb_applicable": True},
    {"segment_id": "seg_05", "segment_class": "sovereign", "rating": "BB+ to B-",
     "ead": 120905372.39, "lgd": 0.5385, "maturity": 2.36, "irb_applicable": True},
    {"segment_id": "seg_06", "segment_class": "corporate", "rating": "BBB+ to BBB-",
     "ead": 106902652.37, "lgd": 0.2919, "maturity": 4.30, "irb_applicable": True},
    {"segment_id": "seg_07", "segment_class": "retail",    "rating": "Unrated",
     "ead": 166874123.52, "lgd": 0.3445, "maturity": 4.73, "irb_applicable": True},
    {"segment_id": "seg_08", "segment_class": "mdb",       "rating": "BBB+ to BBB-",
     "ead": 90255438.53, "lgd": 0.4342, "maturity": 2.04, "irb_applicable": False},
)

BY_ID = {s["segment_id"]: s for s in SEGMENTS}

_PREPARATION = (
    ("Scope and approval inventory",
     "List the exposure segments in scope and the model approvals the engagement "
     "relies on."),
    ("Approval scope note",
     "Write a short note on which approaches are available for which exposure "
     "classes."),
    ("Exposure data preparation",
     "Assemble exposure amounts, ratings, loss-given-default and maturity for "
     "every segment."),
    ("Data quality checklist",
     "Check the assembled exposure data for gaps and inconsistencies."),
)

_REVIEW = (
    ("Aggregate risk-weighted assets",
     "Sum the risk-weighted assets reported for every segment into a portfolio "
     "total."),
    ("Output floor check",
     "Check the portfolio total against the standardised-approach output floor."),
    ("Capital adequacy summary",
     "Summarise the capital position and note anything the reviewer should see."),
)


def create_workflow() -> Workflow:
    """Preparation -> nine pricings -> review. Dependencies are real, not decorative."""
    workflow = Workflow(
        name="basel_capital_calculation",
        workflow_goal=(
            "Produce the portfolio's Basel capital calculation: risk-weighted "
            "assets for every exposure segment, aggregated into a portfolio total "
            "with an output-floor check and a capital adequacy summary.\n\n"
            "Each segment must be priced under the method that applies to it. "
            "An analyst capable at the segment's class should use the advanced "
            "method; one that is not may still price the segment under the "
            "regular method, which every analyst can always do."
        ),
        owner_id=uuid4(),
    )

    prep_ids = []
    for name, description in _PREPARATION:
        task = Task(name=name, description=description, status=TaskStatus.PENDING)
        workflow.add_task(task)
        prep_ids.append(task.id)

    segment_ids = []
    for segment in SEGMENTS:
        task = Task(
            name=f"Risk-weighted assets — {segment['segment_id']}",
            description=(
                f"Compute the risk-weighted assets for exposure segment "
                f"{segment['segment_id']}.\n"
                f"asset class: {segment['segment_class']}\n"
                f"rating bucket: {segment['rating']}\n"
                f"exposure at default: {segment['ead']:,.2f}\n"
                f"loss given default: {segment['lgd']}\n"
                f"maturity (years): {segment['maturity']}\n"
                f"advanced method applies to this segment: "
                f"{'yes' if segment['irb_applicable'] else 'no'}"
            ),
            dependency_task_ids=list(prep_ids),
            status=TaskStatus.PENDING,
        )
        if _HAS_TASK_CLASS:
            task.task_class = SEGMENT_TASK_CLASS
        workflow.add_task(task)
        segment_ids.append(task.id)

    previous = list(segment_ids)
    for name, description in _REVIEW:
        task = Task(name=name, description=description,
                    dependency_task_ids=list(previous), status=TaskStatus.PENDING)
        workflow.add_task(task)
        previous = [task.id]

    return workflow
