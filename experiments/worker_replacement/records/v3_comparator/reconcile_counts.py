"""Resolve two population counts: 125-vs-141, and the recall bar's 9-vs-4.

Zero LLM calls. Both counts are structural.

(1) Does adding profile_scope questions to the 125 requirement_artifact ones
    reach 141? Counts distinct profile_scope questions by their payload text
    the same way -- (worker_profile text, task_scope).
(2) The recall bar scores 3 diagnostic rows in each of 3 silent cells = 9
    (cell, label) targets. How many DISTINCT (excerpt, method) text questions
    do those 9 reduce to? 9 counts scoring opportunities; the smaller number
    counts questions the comparator is actually asked.
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
from experiments.worker_replacement.arm3_requirements import VisibleRequirementStore  # noqa: E402
from experiments.worker_replacement.judgment_protocol import load_protocol  # noqa: E402

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
SILENT = [c for c in CELLS if c.startswith("silent")]


async def enumerate_cell(cell: str, protocol_name: str, labels_name: str) -> dict:
    run_dir = SMOKE / f"toolset_to_screening_{cell}_t3_seed101"
    payload = _load_run(run_dir)
    observations = _observations(payload)
    complete_ledger = await _ledger(payload, observations)
    protocol = load_protocol(LABELS / f"{protocol_name}.json")
    replay_labels = load_replay_labels(LABELS / f"{labels_name}.json")

    fact_matches: dict[str, list] = {}
    for label in protocol.labels:
        fact_matches[str(label["label_id"])] = [
            entry
            for entry in complete_ledger
            if (not label.get("worker") or entry.worker == label["worker"])
            and re.search(str(label["task_pattern"]), entry.task or "", re.I)
            and re.search(str(label["fact_pattern"]), entry.fact, re.I)
        ]
    # evidence -> the diagnostic label(s) that cite it
    diagnostic_evidence: dict[str, set[str]] = {}
    for judgment in protocol.relations:
        if judgment.channel != "task_artifact_relation" or judgment.polarity != "diagnostic":
            continue
        for source_id in judgment.source_label_ids:
            for entry in fact_matches[source_id]:
                diagnostic_evidence.setdefault(entry.evidence_id, set()).add(
                    judgment.relation_id
                )

    requirements = VisibleRequirementStore()
    scope_store = Arm3SemanticExtractor(
        model="deterministic-plan", seed=replay_labels.seed
    )
    builder = DeterministicRelationPacketBuilder()

    artifact_pairs: set[tuple] = set()
    scope_pairs: set[tuple] = set()
    diagnostic_targets: dict[str, set[tuple]] = {}

    expected_patterns = {
        expectation.exact_excerpt_pattern
        for scope_label in replay_labels.scope_expectations
        for expectation in scope_label.constraint_expectations
    }

    for observation in observations:
        requirements.update(observation)
        await scope_store.assign_missing_scopes(
            requirements, timestep=observation.timestep
        )
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
                p = judgment.payload
                if judgment.judgment_kind == "profile_scope":
                    scope_pairs.add(
                        (
                            "\n".join(
                                str(r["text"]) for r in p.get("worker_profile", [])
                            ),
                            str(p.get("task_scope", "")),
                        )
                    )
                    continue
                excerpt = str(p.get("requirement_clause", ""))
                claims = p.get("artifact_stated_method", [])
                method = "\n".join(str(c["stated_method"]) for c in claims)
                artifact_pairs.add((excerpt, method))
                if not any(re.search(pat, excerpt, re.I) for pat in expected_patterns):
                    continue
                for claim in claims:
                    for relation_id in diagnostic_evidence.get(
                        claim.get("evidence_id"), ()
                    ):
                        diagnostic_targets.setdefault(relation_id, set()).add(
                            (excerpt, method)
                        )
    return {
        "cell": cell,
        "artifact_pairs": artifact_pairs,
        "scope_pairs": scope_pairs,
        "diagnostic_targets": diagnostic_targets,
    }


async def main() -> None:
    rows = [await enumerate_cell(c, *CELLS[c]) for c in CELLS]

    artifact = set().union(*(r["artifact_pairs"] for r in rows))
    scope = set().union(*(r["scope_pairs"] for r in rows))
    print("(1) 125 vs 141")
    print(f"  distinct requirement_artifact questions : {len(artifact)}")
    print(f"  distinct profile_scope questions        : {len(scope)}")
    print(f"  both channels combined                  : {len(artifact) + len(scope)}")

    print("\n(2) recall bar: 9 (cell, label) targets -> how many distinct questions?")
    targets: list[tuple[str, str]] = []
    distinct: set[tuple] = set()
    for row in rows:
        if row["cell"] not in SILENT:
            continue
        for relation_id, pairs in sorted(row["diagnostic_targets"].items()):
            targets.append((row["cell"], relation_id))
            distinct |= pairs
            for pair in sorted(pairs):
                print(f"  {row['cell']:18s} {relation_id:20s} {pair[1][:58]!r}")
    print(f"\n  (cell, label) scoring targets : {len(targets)}")
    print(f"  distinct text questions       : {len(distinct)}")
    for pair in sorted(distinct):
        print(f"    {pair[1][:70]!r}")

    Path(
        "/tmp/claude-1000/-home-therealgod-Projects-AdHocTeamwork/"
        "38875bdd-4424-4a39-a4aa-f50a3c3bcd10/scratchpad/reconcile_counts.json"
    ).write_text(
        json.dumps(
            {
                "requirement_artifact_distinct": len(artifact),
                "profile_scope_distinct": len(scope),
                "combined": len(artifact) + len(scope),
                "diagnostic_scoring_targets": len(targets),
                "diagnostic_distinct_questions": len(distinct),
            },
            indent=1,
        )
    )


asyncio.run(main())
