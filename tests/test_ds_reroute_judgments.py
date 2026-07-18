from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from experiments.ds_reroute.audit_arm2 import _matches
from experiments.ds_reroute.judgment_protocol import (
    ChangeProbeResponse,
    EvidenceProbeResponse,
    JudgmentProtocol,
    WorkerChangeAssessment,
    WorkerEvidenceItem,
    code_probe_outcome,
    load_protocol,
)
from experiments.ds_reroute.shadow_probe import find_probe_points


PROTOCOL_PATH = Path("experiments/ds_reroute/evidence_labels/toolset_seed101.json")


def test_seed101_judgment_protocol_is_valid_and_fingerprinted() -> None:
    protocol = load_protocol(PROTOCOL_PATH)

    assert protocol.protocol_version == "relation-judgments-v1.1"
    assert len(protocol.labels) == 9
    assert {relation.polarity for relation in protocol.relations} == {
        "diagnostic",
        "exonerating",
        "neutral",
    }
    assert len(protocol.fingerprint()) == 64


def test_protocol_rejects_relation_with_unknown_source_label() -> None:
    payload = load_protocol(PROTOCOL_PATH).model_dump(mode="json")
    payload["relations"][0]["source_label_ids"] = ["missing"]

    with pytest.raises(ValidationError, match="unknown labels"):
        JudgmentProtocol.model_validate(payload)


@pytest.mark.parametrize(
    ("assessment", "evidence", "assigned_agent", "expected"),
    [
        (
            "possible_change",
            "z-score was reported",
            "portfolio_analyst",
            "stated_update_only",
        ),
        (
            "no_change_indicated",
            "z-score was reported",
            "portfolio_analyst",
            "noticed_but_dismissed",
        ),
        (
            "likely_change",
            "z-score was reported",
            "risk_analyst",
            "belief_and_action_update",
        ),
        ("no_change_indicated", "task completed", "portfolio_analyst", "not_engaged"),
    ],
)
def test_probe_outcome_coding_is_deterministic(
    assessment: str, evidence: str, assigned_agent: str, expected: str
) -> None:
    result = code_probe_outcome(
        target_worker="portfolio_analyst",
        assigned_agent=assigned_agent,
        expected_correct_agents=["risk_analyst"],
        engagement_patterns=[r"z.?score"],
        change_response=ChangeProbeResponse(
            assessments=[
                WorkerChangeAssessment(
                    worker_id="portfolio_analyst",
                    assessment=assessment,
                    explanation="assessment",
                )
            ]
        ),
        evidence_response=EvidenceProbeResponse(
            evidence=[
                WorkerEvidenceItem(
                    worker_id="portfolio_analyst",
                    observed_evidence=evidence,
                    implication="ambiguous",
                    explanation="evidence assessment",
                )
            ]
        ),
    )

    assert result == expected


def test_evidence_probe_caps_each_worker_at_three_items() -> None:
    with pytest.raises(ValidationError, match="three-item per-worker cap"):
        EvidenceProbeResponse(
            evidence=[
                WorkerEvidenceItem(
                    worker_id="portfolio_analyst",
                    observed_evidence=f"evidence-{index}",
                    implication="ambiguous",
                    explanation="assessment",
                )
                for index in range(4)
            ]
        )


def test_evidence_probe_cap_is_per_worker() -> None:
    response = EvidenceProbeResponse(
        evidence=[
            WorkerEvidenceItem(
                worker_id=worker_id,
                observed_evidence=f"{worker_id}-{index}",
                implication="ambiguous",
                explanation="assessment",
            )
            for worker_id in ("portfolio_analyst", "risk_analyst")
            for index in range(3)
        ]
    )

    assert len(response.evidence) == 6


@pytest.mark.parametrize(
    ("pattern", "fact"),
    [
        (
            r"method:.*(mean.*2.*SD|zscore)",
            '"method": "reference mean-plus-two-standard-deviation '
            '(z-score) cutoff"',
        ),
        (r"metric:\s*59(?:\D|$)", '"metric": 59'),
        (r"method:.*zscore", "method: z score"),
    ],
)
def test_offline_matcher_accepts_equivalent_serializations(
    pattern: str, fact: str
) -> None:
    assert _matches(
        {"fact_pattern": pattern}, fact=fact, worker=None, task=None
    )


def test_offline_matcher_does_not_change_semantics() -> None:
    assert not _matches(
        {"fact_pattern": r"method:.*zscore"},
        fact='"method": "95th-percentile"',
        worker=None,
        task=None,
    )


def test_probe_points_resolve_exact_saved_pre_action_requests() -> None:
    task_b = "11111111-1111-1111-1111-111111111111"
    task_c = "22222222-2222-2222-2222-222222222222"
    trace = {
        "events": [
            {
                "event_type": "structured_llm_request",
                "actor_type": "manager",
                "timestep": timestep,
                "payload": {
                    "model": "test-model",
                    "messages": [
                        {"role": "system", "content": "system"},
                        {
                            "role": "user",
                            "content": (
                                f"Task: Batch B Robust Audit (ID: {task_b})\n"
                                f"Task: Batch C Robust Audit (ID: {task_c})\n"
                                f"context-{timestep}"
                            ),
                        },
                    ],
                },
            }
            for timestep in (11, 17)
        ],
        "manager_actions": [
            {
                "timestep": 11,
                "action": {
                    "action_type": "assign_task",
                    "task_id": task_b,
                    "agent_id": "portfolio_analyst",
                },
            },
            {
                "timestep": 17,
                "action": {
                    "action_type": "assign_task",
                    "task_id": task_c,
                    "agent_id": "portfolio_analyst",
                },
            },
        ],
    }

    points = find_probe_points(trace, ("Batch B Robust Audit", "Batch C Robust Audit"))

    assert [(point["task_name"], point["timestep"]) for point in points] == [
        ("Batch B Robust Audit", 11),
        ("Batch C Robust Audit", 17),
    ]
    assert points[0]["user"].endswith("context-11")
