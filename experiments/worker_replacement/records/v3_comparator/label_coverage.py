"""How much of what the comparator judges carries ground truth?

Zero LLM calls: packet construction and `judgments_for` are deterministic, and
this is the same code path `plan_replay` uses to count calls without issuing
them. Nothing is written outside the scratchpad.

Definitions, stated because both numbers have been wrong once already:
  clause question = a distinct (requirement excerpt, artifact stated method)
                    text pair judged in the requirement_artifact channel.
                    This is the "141" population from the text-pair diff.
  labelled        = the judgment's evidence intersects evidence matched by a
                    protocol label that a `task_artifact_relation` judgment
                    cites, AND the requirement excerpt matches one of that
                    scope's expected patterns -- the same two conditions the
                    scorer applies at arm3_replay.py:770.

The fact-matching block is replicated verbatim from `_score` (arm3_replay.py:511)
rather than imported, because it is inline there. If it drifts, this measurement
drifts with it; flagged rather than hidden.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")

from experiments.worker_replacement.arm3_relations import (  # noqa: E402
    Arm3SemanticExtractor,
    DeterministicRelationPacketBuilder,
    judgments_for,
)
from experiments.worker_replacement.arm3_replay import (  # noqa: E402
    _ledger,
    _load_run,
    _observations,
    load_replay_labels,
)
from experiments.worker_replacement.judgment_protocol import load_protocol  # noqa: E402
from experiments.worker_replacement.arm3_requirements import (  # noqa: E402
    VisibleRequirementStore,
)

ROOT = Path(
    "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym/experiments/worker_replacement"
)
SMOKE = ROOT / "outputs" / "smoke101_5b19b5b"
LABELS = ROOT / "evidence_labels"

CELLS = {
    "control_arm3i_q": ("toolset_control_seed101", "arm3_toolset_control_seed101"),
    "silent_arm3i_noq": ("toolset_seed101", "arm3_toolset_seed101"),
    "silent_arm3i_q": ("toolset_seed101", "arm3_toolset_seed101"),
    "silent_arm3t": ("toolset_seed101", "arm3_toolset_seed101"),
}


async def one_cell(cell: str, protocol_name: str, labels_name: str) -> dict:
    run_dir = SMOKE / f"toolset_to_screening_{cell}_t3_seed101"
    payload = _load_run(run_dir)
    observations = _observations(payload)
    complete_ledger = await _ledger(payload, observations)
    protocol = load_protocol(LABELS / f"{protocol_name}.json")
    replay_labels = load_replay_labels(LABELS / f"{labels_name}.json")

    # verbatim from _score
    fact_matches: dict[str, list] = {}
    for label in protocol.labels:
        fact_matches[str(label["label_id"])] = [
            entry
            for entry in complete_ledger
            if (not label.get("worker") or entry.worker == label["worker"])
            and re.search(str(label["task_pattern"]), entry.task or "", re.I)
            and re.search(str(label["fact_pattern"]), entry.fact, re.I)
        ]

    # Which labels carry a task_artifact_relation judgment, and of what polarity.
    polarity_by_label: dict[str, str] = {}
    for judgment in protocol.relations:
        if judgment.channel != "task_artifact_relation":
            continue
        for source_id in judgment.source_label_ids:
            polarity_by_label[source_id] = judgment.polarity
    evidence_polarity: dict[str, str] = {}
    for label_id, polarity in polarity_by_label.items():
        for entry in fact_matches[label_id]:
            evidence_polarity[entry.evidence_id] = polarity

    requirements = VisibleRequirementStore()
    scope_store = Arm3SemanticExtractor(model="deterministic-plan", seed=replay_labels.seed)
    builder = DeterministicRelationPacketBuilder()

    pairs: dict[tuple, str | None] = {}
    total_judgments = 0
    for observation in observations:
        requirements.update(observation)
        await scope_store.assign_missing_scopes(requirements, timestep=observation.timestep)
        visible = [
            entry
            for entry in complete_ledger
            if entry.first_observed_timestep <= observation.timestep
        ]
        packets = builder.build(
            requirements=requirements,
            ledger=visible,
            timestep=observation.timestep,
            active_task_ids={
                str(t)
                for t in [*observation.ready_task_ids, *observation.running_task_ids]
            },
            task_constraints=scope_store.task_constraints,
        )
        for packet in packets:
            for judgment in judgments_for(packet):
                if judgment.judgment_kind != "requirement_artifact":
                    continue
                total_judgments += 1
                payload_ = judgment.payload
                excerpt = str(payload_.get("requirement_clause", ""))
                method = "\n".join(
                    str(claim["stated_method"])
                    for claim in payload_.get("artifact_stated_method", [])
                )
                evidence_ids = {
                    claim.get("evidence_id")
                    for claim in payload_.get("artifact_stated_method", [])
                }
                touched = {
                    evidence_polarity[e]
                    for e in evidence_ids
                    if e in evidence_polarity
                }
                expected_patterns = {
                    expectation.exact_excerpt_pattern
                    for scope_label in replay_labels.scope_expectations
                    for expectation in scope_label.constraint_expectations
                }
                excerpt_expected = any(
                    re.search(p, excerpt, re.I) for p in expected_patterns
                )
                key = (excerpt, method)
                label = None
                if touched and excerpt_expected:
                    label = "diagnostic" if "diagnostic" in touched else "exonerating"
                if key not in pairs or (label and not pairs[key]):
                    pairs[key] = label
    return {
        "cell": cell,
        "judgments_drawn": total_judgments,
        "distinct_pairs": len(pairs),
        "labelled": sum(1 for v in pairs.values() if v),
        "labelled_diagnostic": sum(1 for v in pairs.values() if v == "diagnostic"),
        "labelled_exonerating": sum(1 for v in pairs.values() if v == "exonerating"),
        # NOT truncated: a 60-char key collapsed 16 distinct pairs on the first
        # run and produced a corpus count of 125 against the true 141.
        "pairs": {f"{k[0]} || {k[1]}": v for k, v in pairs.items()},
    }


async def main() -> None:
    rows = []
    corpus: dict[tuple, str | None] = {}
    for cell, (protocol, labels) in CELLS.items():
        row = await one_cell(cell, protocol, labels)
        for key, value in row.pop("pairs").items():
            if key not in corpus or (value and not corpus[key]):
                corpus[key] = value
        rows.append(row)
        print(
            f"{row['cell']:18s} drawn={row['judgments_drawn']:4d}  "
            f"distinct={row['distinct_pairs']:4d}  labelled={row['labelled']:3d} "
            f"(diag {row['labelled_diagnostic']}, exon {row['labelled_exonerating']})",
            flush=True,
        )
    n = len(corpus)
    lab = sum(1 for v in corpus.values() if v)
    diag = sum(1 for v in corpus.values() if v == "diagnostic")
    exon = sum(1 for v in corpus.values() if v == "exonerating")
    print(
        f"\nCORPUS-WIDE distinct clause questions : {n}"
        f"\n  carrying ground truth               : {lab}  ({lab / n:.1%})"
        f"\n    contradiction side (diagnostic)   : {diag}"
        f"\n    support side (exonerating)        : {exon}"
        f"\n  unlabelled                          : {n - lab}  ({(n - lab) / n:.1%})"
    )
    Path(
        "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/"
        "38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/label_coverage.json"
    ).write_text(json.dumps({"cells": rows, "corpus": corpus}, indent=1))


asyncio.run(main())
