"""Read and project offline ds_reroute run bundles for local visualization."""

from __future__ import annotations

import json
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATUS_COLORS = {
    "pending": "#d1d5db",
    "ready": "#fbbf24",
    "running": "#38bdf8",
    "completed": "#34d399",
    "failed": "#fb7185",
}

COMMUNICATION_TOOLS = {
    "send_message",
    "broadcast_message",
    "get_recent_messages",
}


@dataclass(frozen=True)
class RunOption:
    path: Path
    label: str


def discover_runs(root: Path) -> list[RunOption]:
    options: list[RunOption] = []
    for path in sorted(root.rglob("run.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            bundle = json.loads(path.read_text())
            metadata = bundle.get("metadata", {})
            condition = metadata.get("condition", "unknown")
            seed = metadata.get("seed", "?")
            label = f"{condition} · seed {seed} · {path.parent.name}"
        except (OSError, ValueError):
            label = f"Unreadable · {path.parent.name}"
        options.append(RunOption(path=path, label=label))
    return options


class RunBundle:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, Any] = json.loads(path.read_text())
        self.events: list[dict[str, Any]] = self.data.get("events", [])
        self.timesteps = {
            int(event["timestep"]): event
            for event in self.events
            if event.get("event_type") == "timestep_completed"
            and event.get("timestep") is not None
        }
        self._task_start = self._task_start_timesteps()

    @property
    def metadata(self) -> dict[str, Any]:
        return self.data.get("metadata", {})

    @property
    def manifest(self) -> dict[str, Any]:
        return self.data.get("manifest", {})

    @property
    def timestep_numbers(self) -> list[int]:
        return sorted(self.timesteps)

    @property
    def final_timestep(self) -> int:
        return max(self.timesteps, default=0)

    def timestep_metadata(self, timestep: int) -> dict[str, Any]:
        event = self.timesteps.get(timestep, {})
        return event.get("payload", {}).get("metadata", {})

    def workflow_snapshot(self, timestep: int) -> dict[str, Any]:
        return self.timestep_metadata(timestep).get("workflow_snapshot", {})

    def tasks(self, timestep: int) -> dict[str, dict[str, Any]]:
        return self.workflow_snapshot(timestep).get("tasks", {})

    def resources(self, timestep: int) -> dict[str, dict[str, Any]]:
        return self.workflow_snapshot(timestep).get("resources", {})

    def manager_request(self, timestep: int) -> dict[str, Any] | None:
        for event in self.events:
            if (
                event.get("event_type") == "structured_llm_request"
                and event.get("actor_type") == "manager"
                and event.get("timestep") == timestep
            ):
                return event
        return None

    def manager_response(self, timestep: int) -> dict[str, Any] | None:
        for event in self.events:
            if (
                event.get("event_type") == "structured_llm_response"
                and event.get("actor_type") == "manager"
                and event.get("timestep") == timestep
            ):
                return event
        return None

    def manager_exchange(self, timestep: int) -> dict[str, Any]:
        """Project the complete ordered manager request/response exchange for a step."""
        exchange_events: list[dict[str, Any]] = []
        for event in self.events:
            if event.get("actor_type") != "manager" or event.get("timestep") != timestep:
                continue
            payload = event.get("payload") or {}
            event_type = event.get("event_type")
            if event_type == "structured_llm_request":
                exchange_events.append({
                    "sequence": event.get("sequence"),
                    "type": "request",
                    "operation": event.get("operation"),
                    "model": payload.get("model"),
                    "wire_model": payload.get("wire_model"),
                    "messages": payload.get("messages", []),
                    "response_type": payload.get("response_type"),
                    "response_schema": payload.get("response_schema"),
                    "settings": {
                        key: payload.get(key)
                        for key in (
                            "temperature",
                            "seed",
                            "max_completion_tokens",
                            "max_retries",
                        )
                        if payload.get(key) is not None
                    },
                })
            elif event_type == "structured_llm_response":
                exchange_events.append({
                    "sequence": event.get("sequence"),
                    "type": "response",
                    "operation": event.get("operation"),
                    "model": payload.get("model"),
                    "response_type": payload.get("response_type"),
                    "parsed_response": payload.get("parsed_response"),
                })
            elif event_type == "structured_llm_error":
                exchange_events.append({
                    "sequence": event.get("sequence"),
                    "type": "error",
                    "operation": event.get("operation"),
                    "error_type": payload.get("error_type"),
                    "error": payload.get("error") or payload.get("error_message"),
                })

        exchange_events.sort(key=lambda item: item.get("sequence", -1))
        action_entry = next(
            (
                entry
                for entry in self.data.get("manager_actions", [])
                if entry.get("timestep") == timestep
            ),
            None,
        )
        workflow_observation = self.timestep_metadata(timestep).get(
            "manager_observation", {}
        )
        return {
            "timestep": timestep,
            "observed_coordination_changes": self.timestep_metadata(timestep).get(
                "agent_coordination_changes", []
            ),
            "workflow_observation": workflow_observation,
            "recent_communications": workflow_observation.get("recent_messages", []),
            "events": exchange_events,
            "executed_action": (action_entry or {}).get("action"),
        }

    def event_timestep(self, event: dict[str, Any]) -> int | None:
        explicit = event.get("timestep")
        if explicit is not None:
            return int(explicit)
        task_id = event.get("task_id")
        return self._task_start.get(str(task_id)) if task_id is not None else None

    def events_for_timestep(self, timestep: int) -> list[dict[str, Any]]:
        return [event for event in self.events if self.event_timestep(event) == timestep]

    def worker_events(
        self, timestep: int, task_id: str | None = None
    ) -> list[dict[str, Any]]:
        return [
            event
            for event in self.events_for_timestep(timestep)
            if event.get("actor_type") == "worker"
            and (task_id is None or event.get("task_id") == task_id)
        ]

    def task_actor(self, task_id: str) -> str | None:
        """Return the worker identity or identity transition that executed a task."""
        actors: list[str] = []
        for event in self.events:
            if (
                event.get("event_type") == "worker_execution_started"
                and str(event.get("task_id")) == str(task_id)
                and event.get("actor_id")
                and event["actor_id"] not in actors
            ):
                actors.append(event["actor_id"])
        return " -> ".join(actors) if actors else None

    def task_execution(self, task_id: str) -> dict[str, Any] | None:
        """Project all worker execution details for a task across the full run."""
        matching = [
            event
            for event in self.events
            if event.get("actor_type") == "worker"
            and str(event.get("task_id")) == str(task_id)
            and event.get("event_type") in {
                "worker_execution_started",
                "worker_run_completed",
                "worker_execution_completed",
                "worker_execution_failed",
            }
        ]
        if not matching:
            return None

        attempts: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for event in matching:
            payload = event.get("payload") or {}
            event_type = event.get("event_type")
            if event_type == "worker_execution_started" or current is None:
                current = {
                    "actor_id": event.get("actor_id"),
                    "task_name": event.get("task_name"),
                    "started_timestep": self.event_timestep(event),
                    "start_sequence": event.get("sequence"),
                    "input": {},
                    "tool_calls": [],
                    "runs": [],
                }
                attempts.append(current)

            if event_type == "worker_execution_started":
                current["input"] = {
                    "model": payload.get("model"),
                    "system_prompt": payload.get("system_prompt"),
                    "task_prompt": payload.get("task_prompt"),
                    "input_resources": payload.get("input_resources", []),
                    "available_tools": payload.get("tools", []),
                    "max_turns": payload.get("max_turns"),
                }
            elif event_type == "worker_run_completed":
                run_index = event.get("run_index")
                calls = _tool_call_sequence(payload.get("history", []), run_index)
                current["tool_calls"].extend(calls)
                current["runs"].append({
                    "run_index": run_index,
                    "final_output": payload.get("final_output"),
                    "model_responses": payload.get("raw_responses", []),
                })
                if payload.get("final_output") not in (None, ""):
                    current["final_output"] = payload.get("final_output")
            elif event_type == "worker_execution_completed":
                current["completion_sequence"] = event.get("sequence")
                current["parsed_completion"] = {
                    "reasoning": payload.get("reasoning"),
                    "confidence": payload.get("confidence"),
                    "execution_notes": payload.get("execution_notes", []),
                    "output_resources": payload.get("output_resources", []),
                }
            elif event_type == "worker_execution_failed":
                current["failure"] = {
                    "error_type": payload.get("error_type"),
                    "error": payload.get("error") or payload.get("error_message"),
                }

        return {
            "task_id": str(task_id),
            "task_name": next(
                (event.get("task_name") for event in matching if event.get("task_name")),
                None,
            ),
            "actor_id": self.task_actor(task_id),
            "manager_decisions": self.task_manager_decisions(task_id),
            "attempts": attempts,
        }

    def task_manager_decisions(self, task_id: str) -> list[dict[str, Any]]:
        """Return assignment and retry decisions that targeted a task node."""
        task_id = str(task_id)
        decisions: list[dict[str, Any]] = []
        for entry in self.data.get("manager_actions", []):
            action = entry.get("action") or {}
            action_type = action.get("action_type")
            targeted = str(action.get("task_id")) == task_id
            selected_agent = action.get("agent_id")

            if action_type == "assign_tasks_to_agents":
                assignment = next(
                    (
                        item
                        for item in action.get("assignments", [])
                        if str(item.get("task_id")) == task_id
                    ),
                    None,
                )
                targeted = assignment is not None
                selected_agent = assignment.get("agent_id") if assignment else None

            if not targeted or action_type not in {
                "assign_task",
                "assign_tasks_to_agents",
                "retry_task",
            }:
                continue
            decisions.append({
                "timestep": entry.get("timestep"),
                "action_type": action_type,
                "selected_agent_id": selected_agent,
                "reasoning": action.get("reasoning"),
                "success": action.get("success"),
                "result_summary": action.get("result_summary"),
            })
        return decisions

    def perturbations(self) -> list[dict[str, Any]]:
        """Return manifest perturbations enriched with observed before/after tools."""
        raw = self.manifest.get("perturbation", {}).get("perturbations", [])
        starts = [
            event
            for event in self.events
            if event.get("event_type") == "worker_execution_started"
        ]
        result: list[dict[str, Any]] = []
        for perturbation in raw:
            item = dict(perturbation)
            timestep = int(item.get("timestep", 0))
            agent_id = item.get("agent_id")
            prior = [
                event
                for event in starts
                if event.get("actor_id") == agent_id
                and (self.event_timestep(event) or 0) < timestep
            ]
            prior.sort(key=lambda event: event.get("sequence", -1))
            before_tools = (
                (prior[-1].get("payload") or {}).get("tools", []) if prior else []
            )
            item["before_tools"] = [
                tool for tool in before_tools if tool not in COMMUNICATION_TOOLS
            ]
            item["after_tools"] = item.get("new_tool_ids", [])
            item["applied_changes"] = self.timestep_metadata(timestep).get(
                "agent_coordination_changes", []
            )
            result.append(item)
        return result

    def task_truth(self, task: dict[str, Any]) -> dict[str, Any] | None:
        name = task.get("name")
        for truth in self.data.get("task_ground_truth", {}).values():
            if truth.get("name") == name:
                return truth
        return None

    def task_completion(self, task: dict[str, Any]) -> dict[str, Any] | None:
        name = task.get("name")
        return next(
            (
                completion
                for completion in self.data.get("completions", [])
                if completion.get("task_name") == name
            ),
            None,
        )

    def task_outputs(self, timestep: int, task: dict[str, Any]) -> list[dict[str, Any]]:
        resources = self.resources(timestep)
        return [
            resources[resource_id]
            for resource_id in task.get("output_resource_ids", [])
            if resource_id in resources
        ]

    def graph_options(self, timestep: int, selected_task_id: str | None = None) -> dict[str, Any]:
        tasks = self.tasks(timestep)
        depths = _task_depths(tasks)
        by_depth: dict[int, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
        for task_id, task in tasks.items():
            by_depth[depths[task_id]].append((task_id, task))

        nodes: list[dict[str, Any]] = []
        for depth, layer in sorted(by_depth.items()):
            ordered = sorted(layer, key=lambda item: item[1].get("name", ""))
            layer_height = max(1, len(ordered) - 1) * 125
            for index, (task_id, task) in enumerate(ordered):
                status = task.get("effective_status") or task.get("status", "pending")
                selected = task_id == selected_task_id
                actor = self.task_actor(task_id) or task.get("assigned_agent_id") or "unassigned"
                task_label = _wrap_label(task.get("name", task_id), width=16)
                actor_label = _wrap_label(f"@{actor}", width=18)
                nodes.append({
                    "id": task_id,
                    "name": task_id,
                    "label": f"{task_label}\n{actor_label}",
                    "actor_id": actor,
                    "x": depth * 270,
                    "y": index * 125 - layer_height / 2,
                    "symbol": "roundRect",
                    "symbolSize": [136, 88],
                    "itemStyle": {
                        "color": STATUS_COLORS.get(status, "#d1d5db"),
                        "borderColor": "#111827" if selected else "#6b7280",
                        "borderWidth": 3 if selected else 1,
                    },
                    "labelStyle": {"fontWeight": 700 if selected else 500},
                    "value": status,
                })

        edges = [
            {"source": dependency, "target": task_id}
            for task_id, task in tasks.items()
            for dependency in task.get("dependency_task_ids", [])
            if dependency in tasks
        ]
        return {
            "animation": False,
            "tooltip": {"trigger": "item"},
            "series": [{
                "type": "graph",
                "layout": "none",
                "roam": True,
                "data": nodes,
                "links": edges,
                "edgeSymbol": ["none", "arrow"],
                "edgeSymbolSize": 8,
                "lineStyle": {"color": "#9ca3af", "width": 1.5, "curveness": 0.06},
                "label": {
                    "show": True,
                    "position": "inside",
                    ":formatter": "(params) => params.data.label",
                    "fontSize": 9,
                    "lineHeight": 11,
                    "color": "#111827",
                },
                "emphasis": {"focus": "adjacency"},
            }],
        }

    def event_rows(self, timestep: int | None = None) -> list[dict[str, Any]]:
        events = self.events if timestep is None else self.events_for_timestep(timestep)
        return [
            {
                "sequence": event["sequence"],
                "timestep": self.event_timestep(event),
                "event_type": event.get("event_type"),
                "actor": event.get("actor_id") or event.get("actor_type") or "system",
                "task": event.get("task_name") or "",
                "summary": event_summary(event),
            }
            for event in events
        ]

    def event_by_sequence(self, sequence: int) -> dict[str, Any] | None:
        return next((event for event in self.events if event["sequence"] == sequence), None)

    def _task_start_timesteps(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for timestep, event in sorted(self.timesteps.items()):
            metadata = event.get("payload", {}).get("metadata", {})
            for task_id in metadata.get("tasks_started", []):
                result.setdefault(str(task_id), timestep)
        return result


def _task_depths(tasks: dict[str, dict[str, Any]]) -> dict[str, int]:
    memo: dict[str, int] = {}
    visiting: set[str] = set()

    def depth(task_id: str) -> int:
        if task_id in memo:
            return memo[task_id]
        if task_id in visiting:
            return 0
        visiting.add(task_id)
        dependencies = [
            dependency
            for dependency in tasks[task_id].get("dependency_task_ids", [])
            if dependency in tasks
        ]
        value = 0 if not dependencies else max(depth(item) for item in dependencies) + 1
        visiting.remove(task_id)
        memo[task_id] = value
        return value

    for task_id in tasks:
        depth(task_id)
    return memo


def _wrap_label(label: str, width: int = 14) -> str:
    return "\n".join(textwrap.wrap(label, width=width))


def _tool_call_sequence(
    history: list[dict[str, Any]], run_index: int | None
) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(history):
        item_type = item.get("type")
        if item_type == "function_call":
            arguments: Any = item.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except ValueError:
                    pass
            call = {
                "run_index": run_index,
                "position": position,
                "tool": item.get("name"),
                "arguments": arguments,
                "call_id": item.get("call_id"),
                "output": None,
            }
            calls.append(call)
            if item.get("call_id"):
                by_id[item["call_id"]] = call
        elif item_type == "function_call_output":
            call_id = item.get("call_id")
            if call_id in by_id:
                by_id[call_id]["output"] = item.get("output")
            else:
                calls.append({
                    "run_index": run_index,
                    "position": position,
                    "tool": None,
                    "arguments": None,
                    "call_id": call_id,
                    "output": item.get("output"),
                })
    return calls


def event_summary(event: dict[str, Any]) -> str:
    payload = event.get("payload") or {}
    event_type = event.get("event_type", "event")
    if event_type == "structured_llm_request":
        return f"{payload.get('response_type', 'structured')} via {payload.get('model', '?')}"
    if event_type == "structured_llm_response":
        return f"Parsed {payload.get('response_type', 'structured')} response"
    if event_type == "worker_execution_started":
        return f"Started with {len(payload.get('tools', []))} tools"
    if event_type == "worker_run_completed":
        return f"SDK history: {len(payload.get('history', []))} items"
    if event_type == "worker_execution_completed":
        return f"Completed with {len(payload.get('output_resources', []))} resources"
    if event_type in {"worker_execution_failed", "structured_llm_error", "episode_failed"}:
        return f"{payload.get('error_type', 'Error')}: {payload.get('error', '')}"[:180]
    if event_type == "timestep_completed":
        metadata = payload.get("metadata", {})
        return (
            f"started {len(metadata.get('tasks_started', []))}, "
            f"completed {len(metadata.get('tasks_completed', []))}, "
            f"failed {len(metadata.get('tasks_failed', []))}"
        )
    return event_type.replace("_", " ").title()


def event_brief(event: dict[str, Any]) -> dict[str, Any]:
    """Project a trace event into the fields useful for routine inspection."""
    payload = event.get("payload") or {}
    event_type = event.get("event_type", "event")
    brief: dict[str, Any] = {
        "sequence": event.get("sequence"),
        "timestep": event.get("timestep"),
        "event": event_type,
        "actor": event.get("actor_id") or event.get("actor_type") or "system",
        "task": event.get("task_name"),
        "summary": event_summary(event),
    }

    if event_type == "structured_llm_request":
        brief["details"] = {
            "operation": event.get("operation"),
            "model": payload.get("model"),
            "response_type": payload.get("response_type"),
            "message_roles": [item.get("role") for item in payload.get("messages", [])],
            "temperature": payload.get("temperature"),
            "max_retries": payload.get("max_retries"),
        }
    elif event_type == "structured_llm_response":
        brief["details"] = {
            "model": payload.get("model"),
            "response_type": payload.get("response_type"),
            "parsed_response": payload.get("parsed_response"),
        }
    elif event_type == "timestep_completed":
        metadata = payload.get("metadata", {})
        action = metadata.get("manager_action") or {}
        brief["details"] = {
            "manager_action": {
                key: action.get(key)
                for key in ("action_type", "reasoning", "result_summary", "success")
                if action.get(key) is not None
            },
            "tasks_started": metadata.get("tasks_started", []),
            "tasks_completed": metadata.get("tasks_completed", []),
            "tasks_failed": metadata.get("tasks_failed", []),
            "coordination_changes": metadata.get("agent_coordination_changes", []),
        }
    elif event_type == "worker_execution_started":
        brief["details"] = {
            "model": payload.get("model"),
            "max_turns": payload.get("max_turns"),
            "tools": payload.get("tools", []),
            "input_resource_count": len(payload.get("input_resources", [])),
        }
    elif event_type == "worker_run_completed":
        brief["details"] = {
            "run_index": event.get("run_index"),
            "history_items": len(payload.get("history", [])),
            "model_responses": len(payload.get("raw_responses", [])),
            "final_output": _truncate(payload.get("final_output")),
        }
    elif event_type == "worker_execution_completed":
        brief["details"] = {
            "reasoning": payload.get("reasoning"),
            "confidence": payload.get("confidence"),
            "execution_notes": payload.get("execution_notes", []),
            "outputs": [
                {
                    "name": output.get("name"),
                    "content": _truncate(output.get("content")),
                }
                for output in payload.get("output_resources", [])
            ],
        }
    elif event_type in {"worker_execution_failed", "structured_llm_error", "episode_failed"}:
        brief["details"] = {
            "error_type": payload.get("error_type"),
            "error": payload.get("error") or payload.get("error_message"),
        }
    return {key: value for key, value in brief.items() if value is not None}


def _truncate(value: Any, limit: int = 800) -> Any:
    if not isinstance(value, str) or len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."
