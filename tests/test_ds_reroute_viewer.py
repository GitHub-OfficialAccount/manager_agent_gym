import json
from pathlib import Path

from experiments.ds_reroute.viewer_data import RunBundle, discover_runs, event_brief


def _write_bundle(path: Path) -> None:
    task_a = {
        "id": "a",
        "name": "Profile",
        "status": "completed",
        "effective_status": "completed",
        "dependency_task_ids": [],
        "output_resource_ids": ["resource-a"],
        "assigned_agent_id": "analyst",
    }
    task_b = {
        "id": "b",
        "name": "Audit",
        "status": "running",
        "effective_status": "running",
        "dependency_task_ids": ["a"],
        "output_resource_ids": [],
        "assigned_agent_id": "analyst",
    }
    timestep_payload = {
        "metadata": {
            "tasks_started": ["b"],
            "tasks_completed": ["a"],
            "tasks_failed": [],
            "manager_observation": {
                "timestep": 2,
                "recent_messages": [{
                    "sender_id": "analyst",
                    "content": "Capability changed.",
                }],
            },
            "workflow_snapshot": {
                "tasks": {"a": task_a, "b": task_b},
                "resources": {"resource-a": {"content": "metric: 10"}},
            },
        }
    }
    bundle = {
        "schema_version": "1.0",
        "metadata": {"condition": "silent", "seed": 7},
        "manifest": {
            "r_check": 0.8,
            "perturbation": {
                "num_perturbations": 1,
                "perturbations": [{
                    "kind": "tool_swap",
                    "timestep": 3,
                    "agent_id": "analyst",
                    "new_tool_ids": ["screen"],
                    "announce": False,
                    "label": "screening update",
                }],
            },
        },
        "events": [
            {
                "sequence": 0,
                "event_type": "structured_llm_request",
                "timestep": 2,
                "actor_type": "manager",
                "payload": {"messages": [{"role": "system", "content": "system"}]},
            },
            {
                "sequence": 1,
                "event_type": "worker_execution_started",
                "actor_type": "worker",
                "actor_id": "analyst",
                "task_id": "b",
                "task_name": "Audit",
                "payload": {
                    "model": "test-model",
                    "system_prompt": "You are an analyst.",
                    "task_prompt": "Audit the batch.",
                    "input_resources": [{"name": "batch"}],
                    "tools": ["audit", "send_message"],
                    "max_turns": 5,
                },
            },
            {
                "sequence": 5,
                "event_type": "structured_llm_response",
                "timestep": 2,
                "actor_type": "manager",
                "actor_id": "workflow-orchestrator",
                "operation": "manager_action",
                "payload": {
                    "model": "test-manager",
                    "response_type": "ManagerAction",
                    "parsed_response": {
                        "reasoning": "Assign the audit.",
                        "action": {"action_type": "assign_task", "task_id": "b"},
                    },
                },
            },
            {
                "sequence": 2,
                "event_type": "worker_run_completed",
                "run_index": 0,
                "actor_type": "worker",
                "actor_id": "analyst",
                "task_id": "b",
                "task_name": "Audit",
                "payload": {
                    "history": [
                        {
                            "type": "function_call",
                            "name": "audit",
                            "arguments": "{\"batch\": \"A\"}",
                            "call_id": "call-1",
                        },
                        {
                            "type": "function_call_output",
                            "call_id": "call-1",
                            "output": "{\"count\": 4}",
                        },
                    ],
                    "raw_responses": [{"id": "response-1"}],
                    "final_output": "metric: 4",
                },
            },
            {
                "sequence": 3,
                "event_type": "worker_execution_completed",
                "actor_type": "worker",
                "actor_id": "analyst",
                "task_id": "b",
                "task_name": "Audit",
                "payload": {
                    "reasoning": "Audited batch A.",
                    "confidence": 0.9,
                    "execution_notes": [],
                    "output_resources": [{"content": "metric: 4"}],
                },
            },
            {
                "sequence": 4,
                "event_type": "timestep_completed",
                "timestep": 2,
                "payload": timestep_payload,
            },
        ],
        "manager_actions": [{
            "timestep": 2,
            "action": {
                "action_type": "assign_task",
                "task_id": "b",
                "agent_id": "analyst",
                "reasoning": "The analyst has the audit tool.",
                "success": True,
                "result_summary": "Assigned task b to analyst",
            },
        }],
        "task_ground_truth": {
            "profile": {"name": "Profile", "truth": 10},
        },
        "completions": [{"task_name": "Profile", "r_check": 1.0}],
    }
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(bundle))


def test_run_bundle_correlates_events_tasks_and_outputs(tmp_path) -> None:
    path = tmp_path / "silent_seed7" / "run.json"
    _write_bundle(path)
    bundle = RunBundle(path)

    assert bundle.timestep_numbers == [2]
    assert bundle.final_timestep == 2
    assert bundle.event_timestep(bundle.events[1]) == 2
    assert [event["sequence"] for event in bundle.worker_events(2, "b")] == [1, 2, 3]
    assert bundle.manager_request(2) == bundle.events[0]
    assert bundle.task_truth(bundle.tasks(2)["a"])["truth"] == 10
    assert bundle.task_completion(bundle.tasks(2)["a"])["r_check"] == 1.0
    assert bundle.task_outputs(2, bundle.tasks(2)["a"]) == [
        {"content": "metric: 10"}
    ]

    exchange = bundle.manager_exchange(2)
    assert [item["type"] for item in exchange["events"]] == ["request", "response"]
    assert exchange["events"][0]["messages"] == [
        {"role": "system", "content": "system"}
    ]
    assert exchange["events"][1]["parsed_response"]["reasoning"] == "Assign the audit."
    assert exchange["executed_action"]["reasoning"] == "The analyst has the audit tool."
    assert exchange["recent_communications"] == [{
        "sender_id": "analyst",
        "content": "Capability changed.",
    }]
    assert exchange["workflow_observation"]["timestep"] == 2

    execution = bundle.task_execution("b")
    assert execution is not None
    assert execution["actor_id"] == "analyst"
    assert execution["attempts"][0]["input"]["task_prompt"] == "Audit the batch."
    assert execution["attempts"][0]["final_output"] == "metric: 4"
    assert execution["manager_decisions"] == [{
        "timestep": 2,
        "action_type": "assign_task",
        "selected_agent_id": "analyst",
        "reasoning": "The analyst has the audit tool.",
        "success": True,
        "result_summary": "Assigned task b to analyst",
    }]
    assert execution["attempts"][0]["tool_calls"] == [{
        "run_index": 0,
        "position": 0,
        "tool": "audit",
        "arguments": {"batch": "A"},
        "call_id": "call-1",
        "output": "{\"count\": 4}",
    }]


def test_run_bundle_builds_layered_graph_and_event_rows(tmp_path) -> None:
    path = tmp_path / "silent_seed7" / "run.json"
    _write_bundle(path)
    bundle = RunBundle(path)
    options = bundle.graph_options(2, selected_task_id="b")
    nodes = {node["id"]: node for node in options["series"][0]["data"]}

    assert nodes["a"]["x"] == 0
    assert nodes["b"]["x"] > nodes["a"]["x"]
    assert nodes["b"]["itemStyle"]["borderWidth"] == 3
    assert nodes["b"]["actor_id"] == "analyst"
    assert "@analyst" in nodes["b"]["label"]
    assert options["series"][0]["links"] == [{"source": "a", "target": "b"}]
    assert bundle.event_rows(2)[1]["summary"] == "Started with 2 tools"


def test_run_bundle_enriches_perturbation_with_prechange_tools(tmp_path) -> None:
    path = tmp_path / "silent_seed7" / "run.json"
    _write_bundle(path)

    perturbation = RunBundle(path).perturbations()[0]

    assert perturbation["timestep"] == 3
    assert perturbation["before_tools"] == ["audit"]
    assert perturbation["after_tools"] == ["screen"]


def test_discover_runs_uses_bundle_metadata(tmp_path) -> None:
    path = tmp_path / "silent_seed7" / "run.json"
    _write_bundle(path)

    options = discover_runs(tmp_path)

    assert len(options) == 1
    assert options[0].path == path
    assert options[0].label == "silent · seed 7 · silent_seed7"


def test_event_brief_keeps_action_transitions_without_workflow_snapshot() -> None:
    event = {
        "sequence": 8,
        "timestep": 3,
        "event_type": "timestep_completed",
        "actor_id": "workflow_engine",
        "payload": {
            "metadata": {
                "manager_action": {
                    "action_type": "assign_task",
                    "reasoning": "The task is ready.",
                    "result_summary": "Assigned task a",
                    "success": True,
                    "task_id": "a",
                },
                "tasks_started": ["a"],
                "tasks_completed": [],
                "tasks_failed": [],
                "agent_coordination_changes": [],
                "workflow_snapshot": {"tasks": {"a": {"description": "large"}}},
            }
        },
    }

    brief = event_brief(event)

    assert brief["details"]["manager_action"]["action_type"] == "assign_task"
    assert brief["details"]["tasks_started"] == ["a"]
    assert "workflow_snapshot" not in brief["details"]


def test_event_brief_removes_traceback_and_truncates_worker_output() -> None:
    failure = {
        "sequence": 4,
        "event_type": "worker_execution_failed",
        "actor_id": "analyst",
        "task_name": "Audit",
        "payload": {
            "error_type": "MaxTurnsExceeded",
            "error": "Max turns exceeded",
            "traceback": "large traceback",
        },
    }
    completed = {
        "sequence": 5,
        "event_type": "worker_run_completed",
        "payload": {"history": [1], "raw_responses": [1, 2], "final_output": "x" * 900},
    }

    assert event_brief(failure)["details"] == {
        "error_type": "MaxTurnsExceeded",
        "error": "Max turns exceeded",
    }
    assert len(event_brief(completed)["details"]["final_output"]) < 900
