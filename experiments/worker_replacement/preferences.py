"""What this environment rewards — three numbers, no judge.

Upstream environments score with LLM rubrics because their deliverables are prose
and there is no key to mark against. Here every segment has exactly one right
answer, so all three rubrics are Python functions and the same inputs always
produce the same score. That is the point of this environment, not an economy.

The three are deliberately NOT one number:

    accuracy   what the team actually delivered, against the best available
    routing    what the manager's ALLOCATION made available, against the same
    coverage   whether every segment got priced at all

`routing` isolates the manager's own decision from its workers' arithmetic. A
manager can allocate perfectly and still score badly on `accuracy` because the
workers miscalculated — and reporting only the total hides which happened.

Preferences do not move during an episode. Shifting stakeholder priorities is a
real challenge, but it is not the one under test here, and a moving target would
confound the roster change with a preference change.
"""

from __future__ import annotations

from typing import Any

from manager_agent_gym.schemas.preferences import PreferenceWeights
from manager_agent_gym.schemas.preferences.preference import Preference
from manager_agent_gym.schemas.preferences.evaluator import Evaluator
from manager_agent_gym.schemas.preferences.rubric import RunCondition, WorkflowRubric

from .scoring import SEGMENTS, score_workflow


def _accuracy(workflow: Any) -> tuple[float, str]:
    """Share of the best available score that the team actually delivered."""
    r = score_workflow(workflow)
    if r["best_possible"] <= 0:
        return 0.0, "no scoreable segments"
    share = r["achieved"] / r["best_possible"]
    return share, (
        f"achieved {r['achieved']:.4f} of a best possible "
        f"{r['best_possible']:.4f} ({share * 100:.1f}%); "
        f"execution loss {r['execution_loss']:.4f}"
    )


def _routing(workflow: Any) -> tuple[float, str]:
    """Share of the best available score the manager's ALLOCATION made reachable.

    1.0 means no reallocation could have done better, whatever the workers then
    did with it. Known as the oracle gap in the task-routing literature.
    """
    r = score_workflow(workflow)
    if r["best_possible"] <= 0:
        return 0.0, "no scoreable segments"
    share = r["allocation_faithful"] / r["best_possible"]
    return share, (
        f"the allocation was worth {r['allocation_faithful']:.4f} of a best "
        f"possible {r['best_possible']:.4f}; routing loss {r['routing_loss']:.4f}. "
        f"The routing choice changes the score on {r['n_discriminating']} of "
        f"{len(SEGMENTS)} segments — on the rest no allocation can be wrong"
    )


def _coverage(workflow: Any) -> tuple[float, str]:
    """Share of segments that were allocated and produced a readable figure.

    Separate from accuracy on purpose: a segment nobody priced and a segment
    priced badly are different failures, and averaging them together hides the
    first behind the second.
    """
    r = score_workflow(workflow)
    priced = sum(1 for s in SEGMENTS if r["reports"].get(s["segment_id"]) is not None)
    detail = f"{priced} of {len(SEGMENTS)} segments produced a readable figure"
    if r["unallocated"]:
        detail += f"; never allocated: {', '.join(r['unallocated'])}"
    if r["declined"]:
        detail += f"; declined: {', '.join(r['declined'])}"
    return priced / len(SEGMENTS), detail


def create_preferences() -> PreferenceWeights:
    """Accuracy carries the weight; routing is the diagnostic beside it.

    Routing is weighted but NOT dominant, deliberately. Making it the objective
    would tell the manager that checking its team's work does not count, which is
    the opposite of what a manager is for. It is here to be read, not chased.
    """
    return PreferenceWeights(
        preferences=[
            Preference(
                name="accuracy",
                weight=0.6,
                evaluator=Evaluator(
                    name="accuracy",
                    description="Delivered score against the best available.",
                    rubrics=[WorkflowRubric(
                        name="portfolio_accuracy",
                        description="Achieved / best possible over all segments.",
                        evaluator_function=_accuracy,
                        run_condition=RunCondition.ON_COMPLETION,
                    )],
                ),
            ),
            Preference(
                name="routing",
                weight=0.25,
                evaluator=Evaluator(
                    name="routing",
                    description="Was the work given to workers who could do it?",
                    rubrics=[WorkflowRubric(
                        name="routing_correctness",
                        description=(
                            "The allocation's faithful-execution score against the "
                            "best allocation available to the active roster."
                        ),
                        evaluator_function=_routing,
                        run_condition=RunCondition.ON_COMPLETION,
                    )],
                ),
            ),
            Preference(
                name="coverage",
                weight=0.15,
                evaluator=Evaluator(
                    name="coverage",
                    description="Did every segment get priced at all?",
                    rubrics=[WorkflowRubric(
                        name="segment_coverage",
                        description="Share of segments with a readable figure.",
                        evaluator_function=_coverage,
                        run_condition=RunCondition.ON_COMPLETION,
                    )],
                ),
            ),
        ]
    )


def create_preference_update_requests() -> list:
    """None. Preferences are held fixed so the roster change is the only thing
    moving; a shifting objective would confound the two."""
    return []


def create_evaluator_to_measure_goal_achievement() -> Evaluator:
    """Goal achievement is the accuracy number — the portfolio priced correctly."""
    return Evaluator(
        name="basel_capital_calculation_goal",
        description=(
            "Every exposure segment priced under the approach that applies to it, "
            "scored against the known-correct figure."
        ),
        rubrics=[WorkflowRubric(
            name="goal_achievement",
            description="Achieved score as a share of the best available.",
            evaluator_function=_accuracy,
            run_condition=RunCondition.ON_COMPLETION,
        )],
    )
