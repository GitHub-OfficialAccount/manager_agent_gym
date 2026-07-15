"""Local NiceGUI viewer for ds_reroute offline run bundles.

Run:
    uv run --group viewer python -m experiments.ds_reroute.viewer
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/manager-agent-gym-matplotlib")

from nicegui import events, ui  # noqa: E402

from experiments.ds_reroute.viewer_data import (  # noqa: E402
    RunBundle,
    RunOption,
    discover_runs,
    event_brief,
)


DEFAULT_ROOT = Path("experiments/ds_reroute/outputs")


@dataclass
class ViewerState:
    options: list[RunOption]
    bundle: RunBundle
    timestep: int
    selected_task_id: str | None = None
    selected_event_sequence: int | None = None
    current_events_only: bool = True
    event_detail_mode: str = "brief"


def _pretty(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=True)


def _code_block(content: str, language: str = "text") -> None:
    ui.code(content or "(empty)", language=language).classes(
        "w-full max-h-[56vh] overflow-auto text-xs border border-gray-200"
    )


def build_viewer(root: Path) -> None:
    options = discover_runs(root)
    if not options:
        raise SystemExit(f"No run.json files found below {root}")
    initial = RunBundle(options[0].path)
    state = ViewerState(
        options=options,
        bundle=initial,
        timestep=initial.final_timestep,
    )

    ui.page_title("DS Reroute Run Inspector")
    ui.colors(primary="#0f766e", secondary="#4f46e5", accent="#d97706")
    ui.add_css("""
        body { background: #f8fafc; color: #111827; }
        .q-tab { letter-spacing: 0; }
        .q-btn { letter-spacing: 0; }
        .metric-label { color: #64748b; font-size: 11px; text-transform: uppercase; }
        .metric-value { color: #111827; font-size: 18px; font-weight: 650; }
    """)

    def select_default_task() -> None:
        tasks = state.bundle.tasks(state.timestep)
        if state.selected_task_id not in tasks:
            state.selected_task_id = next(iter(tasks), None)

    select_default_task()

    def refresh_all() -> None:
        select_default_task()
        summary.refresh()
        perturbation_summary.refresh()
        timeline.refresh()
        graph.refresh()
        inspector.refresh()
        event_log.refresh()

    def load_run(path_value: str) -> None:
        state.bundle = RunBundle(Path(path_value))
        state.timestep = state.bundle.final_timestep
        state.selected_task_id = None
        state.selected_event_sequence = None
        refresh_all()

    def set_timestep(value: int | float | None) -> None:
        if value is None:
            return
        state.timestep = int(value)
        state.selected_event_sequence = None
        refresh_all()

    def shift_timestep(delta: int) -> None:
        numbers = state.bundle.timestep_numbers
        if not numbers:
            return
        index = numbers.index(state.timestep)
        state.timestep = numbers[max(0, min(len(numbers) - 1, index + delta))]
        state.selected_event_sequence = None
        refresh_all()

    def select_task(task_id: str) -> None:
        if task_id in state.bundle.tasks(state.timestep):
            state.selected_task_id = task_id
            graph.refresh()
            inspector.refresh()

    def on_graph_click(event: events.EChartPointClickEventArguments) -> None:
        select_task(event.name)

    def select_event(sequence: int) -> None:
        state.selected_event_sequence = int(sequence)
        inspector.refresh()

    @ui.refreshable
    def summary() -> None:
        manifest = state.bundle.manifest
        snapshot = state.bundle.workflow_snapshot(state.timestep)
        tasks = state.bundle.tasks(state.timestep)
        counts: dict[str, int] = {}
        for task in tasks.values():
            status = task.get("effective_status") or task.get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
        metrics = [
            ("Condition", state.bundle.metadata.get("condition", "?")),
            ("Seed", state.bundle.metadata.get("seed", "?")),
            ("R check", f"{manifest.get('r_check', 0):.3f}"),
            ("Completed", f"{manifest.get('completed_predefined', 0)}/{manifest.get('total_predefined', 0)}"),
            ("At timestep", state.timestep),
            ("Task state", f"{counts.get('completed', 0)} done · {counts.get('failed', 0)} failed"),
        ]
        with ui.row().classes("w-full gap-0 border-y border-gray-200 bg-white"):
            for label, value in metrics:
                with ui.column().classes("min-w-32 px-5 py-3 gap-0 border-r border-gray-200"):
                    ui.label(str(label)).classes("metric-label")
                    ui.label(str(value)).classes("metric-value")
        if snapshot.get("name"):
            ui.label(f"{snapshot['name']} · {state.bundle.path}").classes(
                "text-xs text-gray-500 px-1 pt-2"
            )

    @ui.refreshable
    def timeline() -> None:
        numbers = state.bundle.timestep_numbers
        with ui.row().classes("w-full items-center gap-3 bg-white border-b border-gray-200 px-4 py-3"):
            ui.button(icon="chevron_left", on_click=lambda: shift_timestep(-1)).props(
                "flat round dense"
            ).tooltip("Previous timestep")
            ui.slider(
                min=min(numbers, default=0),
                max=max(numbers, default=0),
                step=1,
                value=state.timestep,
                on_change=lambda event: set_timestep(event.value),
            ).props("label label-always").classes("flex-1")
            ui.button(icon="chevron_right", on_click=lambda: shift_timestep(1)).props(
                "flat round dense"
            ).tooltip("Next timestep")
            changes = state.bundle.timestep_metadata(state.timestep).get(
                "agent_coordination_changes", []
            )
            if changes:
                ui.icon("change_circle", color="amber-8").tooltip("Perturbation or coordination change")
                ui.label(f"{len(changes)} change").classes("text-sm text-amber-800")

    @ui.refreshable
    def perturbation_summary() -> None:
        perturbations = state.bundle.perturbations()
        if not perturbations:
            return
        with ui.column().classes(
            "w-full gap-2 border-b border-amber-300 bg-amber-50 px-4 py-3"
        ):
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon("change_circle", color="amber-8", size="22px")
                ui.label("Perturbation").classes("font-semibold text-amber-950")
                ui.label(f"{len(perturbations)} recorded change").classes(
                    "text-xs text-amber-800"
                )
            for change in perturbations:
                timestep = int(change.get("timestep", 0))
                with ui.row().classes("w-full items-start gap-5"):
                    with ui.column().classes("min-w-64 gap-0"):
                        ui.label(
                            f"{change.get('kind', 'change').replace('_', ' ').title()} · "
                            f"{change.get('agent_id', 'unknown agent')}"
                        ).classes("text-sm font-semibold text-gray-900")
                        ui.label(change.get("label") or "No experimenter label").classes(
                            "text-sm text-gray-700"
                        )
                        ui.label(
                            "Announced to manager" if change.get("announce") else "Unannounced"
                        ).classes("text-xs text-gray-600")
                        if change.get("capability_projection"):
                            ui.label(
                                "Manager view: " + change["capability_projection"]
                            ).classes("text-xs text-gray-600")
                        if change.get("announcement"):
                            ui.label(change["announcement"]).classes(
                                "text-xs text-gray-700"
                            )
                    with ui.column().classes("min-w-72 flex-1 gap-0"):
                        ui.label("Before").classes("text-xs font-semibold text-gray-500")
                        ui.label(", ".join(change.get("before_tools", [])) or "Unavailable").classes(
                            "text-xs text-gray-800 break-all"
                        )
                    with ui.column().classes("min-w-72 flex-1 gap-0"):
                        ui.label("After").classes("text-xs font-semibold text-gray-500")
                        ui.label(", ".join(change.get("after_tools", [])) or "Unavailable").classes(
                            "text-xs text-gray-800 break-all"
                        )
                    ui.button(
                        f"Step {timestep}",
                        icon="my_location",
                        on_click=lambda _event=None, value=timestep: set_timestep(value),
                    ).props("flat dense no-caps color=amber-9").tooltip(
                        "Go to perturbation timestep"
                    )

    @ui.refreshable
    def graph() -> None:
        ui.echart(
            state.bundle.graph_options(state.timestep, state.selected_task_id),
            on_point_click=on_graph_click,
            renderer="svg",
        ).classes("w-full h-[610px] bg-white")

    @ui.refreshable
    def inspector() -> None:
        tasks = state.bundle.tasks(state.timestep)
        task = tasks.get(state.selected_task_id or "")
        manager_exchange = state.bundle.manager_exchange(state.timestep)
        selected_event = (
            state.bundle.event_by_sequence(state.selected_event_sequence)
            if state.selected_event_sequence is not None
            else None
        )

        with ui.tabs().props("dense align=left").classes("w-full text-sm") as tabs:
            task_tab = ui.tab("Task", icon="account_tree")
            prompt_tab = ui.tab("Manager Prompt", icon="prompt_suggestion")
            worker_tab = ui.tab("Worker Run", icon="engineering")
            event_tab = ui.tab("Event", icon="data_object")
        with ui.tab_panels(tabs, value=event_tab if selected_event else task_tab).classes(
            "w-full bg-white p-0"
        ):
            with ui.tab_panel(task_tab).classes("p-4"):
                if task is None:
                    ui.label("Select a task in the graph.").classes("text-gray-500")
                else:
                    ui.label(task.get("name", "Unnamed task")).classes("text-lg font-semibold")
                    ui.label(task.get("description", "")).classes("text-sm text-gray-600 mb-3")
                    fields = {
                        "Status": task.get("effective_status") or task.get("status"),
                        "Assigned agent": task.get("assigned_agent_id") or "Unassigned",
                        "Dependencies": task.get("dependency_task_ids", []),
                        "Execution notes": task.get("execution_notes", []),
                        "Ground truth": state.bundle.task_truth(task),
                        "Scored completion": state.bundle.task_completion(task),
                        "Output resources": state.bundle.task_outputs(state.timestep, task),
                    }
                    _code_block(_pretty(fields), "json")
            with ui.tab_panel(prompt_tab).classes("p-4"):
                ui.label(f"Manager exchange at timestep {state.timestep}").classes(
                    "text-lg font-semibold"
                )
                changes = manager_exchange.get("observed_coordination_changes", [])
                if changes:
                    with ui.row().classes(
                        "w-full items-start gap-2 border-y border-amber-300 bg-amber-50 px-3 py-2 mt-3"
                    ):
                        ui.icon("change_circle", color="amber-8")
                        with ui.column().classes("gap-0"):
                            ui.label("Observed change before this decision").classes(
                                "text-xs font-semibold text-amber-900"
                            )
                            for change in changes:
                                ui.label(str(change)).classes("text-sm text-amber-950")

                recent_communications = manager_exchange.get(
                    "recent_communications", []
                )
                ui.label("Workflow observation").classes(
                    "text-xs font-semibold text-gray-500 mt-4"
                )
                ui.label(
                    "Recorded native observation; the request messages below are the exact model input."
                ).classes("text-xs text-gray-500")
                with ui.expansion(
                    f"Recent communications · {len(recent_communications)} message(s)",
                    icon="forum",
                    value=True,
                ).classes("w-full border-b border-gray-200 mt-2"):
                    _code_block(_pretty(recent_communications), "json")
                with ui.expansion(
                    "Complete workflow observation",
                    icon="visibility",
                    value=False,
                ).classes("w-full border-b border-gray-200"):
                    _code_block(
                        _pretty(manager_exchange.get("workflow_observation", {})),
                        "json",
                    )

                exchange_events = manager_exchange.get("events", [])
                if not exchange_events:
                    ui.label("No manager model exchange was recorded.").classes(
                        "text-gray-500 mt-3"
                    )
                for item in exchange_events:
                    item_type = item.get("type")
                    sequence = item.get("sequence")
                    if item_type == "request":
                        with ui.expansion(
                            f"#{sequence} · Request · {item.get('operation') or 'manager decision'}",
                            icon="input",
                            value=True,
                        ).classes("w-full border-b border-gray-200 mt-3"):
                            _code_block(_pretty({
                                "model": item.get("model"),
                                "wire_model": item.get("wire_model"),
                                "response_type": item.get("response_type"),
                                "settings": item.get("settings", {}),
                            }), "json")
                            for message_index, message in enumerate(item.get("messages", []), start=1):
                                ui.label(
                                    f"Message {message_index} · {message.get('role', 'unknown')}"
                                ).classes("text-xs font-semibold text-gray-500 mt-4")
                                content = message.get("content")
                                _code_block(
                                    content if isinstance(content, str) else _pretty(content)
                                )
                            with ui.expansion(
                                "Expected response schema",
                                icon="schema",
                                value=False,
                            ).classes("w-full mt-3"):
                                _code_block(_pretty(item.get("response_schema")), "json")
                    elif item_type == "response":
                        with ui.expansion(
                            f"#{sequence} · Response · {item.get('response_type') or 'structured'}",
                            icon="output",
                            value=True,
                        ).classes("w-full border-b border-gray-200 mt-3"):
                            _code_block(_pretty({
                                "model": item.get("model"),
                                "operation": item.get("operation"),
                                "parsed_response": item.get("parsed_response"),
                            }), "json")
                    else:
                        with ui.expansion(
                            f"#{sequence} · Manager error",
                            icon="error",
                            value=True,
                        ).classes("w-full border-b border-red-200 mt-3"):
                            _code_block(_pretty(item), "json")

                ui.label("Executed decision").classes(
                    "text-xs font-semibold text-gray-500 mt-5"
                )
                executed_action = manager_exchange.get("executed_action")
                if executed_action is None:
                    ui.label("No manager action was executed at this timestep.").classes(
                        "text-sm text-gray-500"
                    )
                else:
                    _code_block(_pretty(executed_action), "json")
            with ui.tab_panel(worker_tab).classes("p-4"):
                execution = (
                    state.bundle.task_execution(state.selected_task_id)
                    if state.selected_task_id is not None
                    else None
                )
                if execution is None:
                    ui.label("No worker execution is recorded for this task.").classes(
                        "text-gray-500"
                    )
                else:
                    ui.label(execution.get("task_name") or "Worker execution").classes(
                        "text-lg font-semibold"
                    )
                    ui.label(
                        f"Executor: {execution.get('actor_id') or 'unknown'} · "
                        "complete-run view"
                    ).classes("text-xs text-gray-500 mb-3")
                    ui.label("Manager assignment decision").classes(
                        "text-xs font-semibold text-gray-500"
                    )
                    decisions = execution.get("manager_decisions", [])
                    if decisions:
                        _code_block(_pretty(decisions), "json")
                    else:
                        ui.label("No manager assignment decision was recorded.").classes(
                            "text-sm text-gray-500 mb-3"
                        )
                    for index, attempt in enumerate(execution.get("attempts", []), start=1):
                        with ui.expansion(
                            f"Attempt {index} · {attempt.get('actor_id') or 'unknown'} · "
                            f"started at step {attempt.get('started_timestep')}",
                            icon="play_circle",
                            value=True,
                        ).classes("w-full border-y border-gray-200"):
                            input_data = attempt.get("input", {})
                            ui.label("Input").classes("text-xs font-semibold text-gray-500 mt-2")
                            _code_block(_pretty({
                                "model": input_data.get("model"),
                                "system_prompt": input_data.get("system_prompt"),
                                "task_prompt": input_data.get("task_prompt"),
                                "input_resources": input_data.get("input_resources", []),
                                "available_tools": input_data.get("available_tools", []),
                                "max_turns": input_data.get("max_turns"),
                            }), "json")
                            ui.label("Tool call sequence").classes(
                                "text-xs font-semibold text-gray-500 mt-4"
                            )
                            _code_block(_pretty(attempt.get("tool_calls", [])), "json")
                            ui.label("Final output").classes(
                                "text-xs font-semibold text-gray-500 mt-4"
                            )
                            _code_block(str(attempt.get("final_output") or "(empty)"))
                            if attempt.get("parsed_completion") is not None:
                                ui.label("Parsed completion").classes(
                                    "text-xs font-semibold text-gray-500 mt-4"
                                )
                                _code_block(_pretty(attempt["parsed_completion"]), "json")
                            if attempt.get("failure") is not None:
                                ui.label("Failure").classes(
                                    "text-xs font-semibold text-red-700 mt-4"
                                )
                                _code_block(_pretty(attempt["failure"]), "json")
            with ui.tab_panel(event_tab).classes("p-4"):
                if selected_event is None:
                    ui.label("Select an event below to inspect its complete payload.").classes(
                        "text-gray-500"
                    )
                else:
                    with ui.row().classes("w-full items-center mb-3"):
                        ui.label(
                            f"#{selected_event['sequence']} · {selected_event['event_type']}"
                        ).classes("text-lg font-semibold")
                        ui.space()

                        def set_event_detail_mode(event: events.ValueChangeEventArguments) -> None:
                            state.event_detail_mode = str(event.value)
                            inspector.refresh()

                        ui.toggle(
                            {"brief": "Brief", "detailed": "Detailed"},
                            value=state.event_detail_mode,
                            on_change=set_event_detail_mode,
                        ).props("dense no-caps")
                    shown_event = (
                        event_brief(selected_event)
                        if state.event_detail_mode == "brief"
                        else selected_event
                    )
                    _code_block(_pretty(shown_event), "json")

    @ui.refreshable
    def event_log() -> None:
        rows = state.bundle.event_rows(
            state.timestep if state.current_events_only else None
        )
        columns = [
            {"name": "sequence", "label": "#", "field": "sequence", "sortable": True},
            {"name": "timestep", "label": "Step", "field": "timestep", "sortable": True},
            {"name": "event_type", "label": "Event", "field": "event_type", "sortable": True},
            {"name": "actor", "label": "Actor", "field": "actor", "sortable": True},
            {"name": "task", "label": "Task", "field": "task", "sortable": True},
            {"name": "summary", "label": "Summary", "field": "summary"},
        ]

        def on_select(event: events.TableSelectionEventArguments) -> None:
            if event.selection:
                select_event(int(event.selection[0]["sequence"]))

        ui.table(
            columns=columns,
            rows=rows,
            row_key="sequence",
            selection="single",
            pagination={"sortBy": "sequence", "rowsPerPage": 10},
            on_select=on_select,
        ).props("flat bordered dense wrap-cells").classes("w-full bg-white")

    with ui.header().classes("bg-gray-950 text-white px-5 py-2 items-center"):
        ui.icon("account_tree", size="24px")
        ui.label("DS Reroute Run Inspector").classes("text-base font-semibold")
        ui.space()
        ui.select(
            {str(option.path): option.label for option in state.options},
            value=str(state.bundle.path),
            on_change=lambda event: load_run(event.value),
        ).props("dense outlined dark options-dense").classes("w-[460px]")

    with ui.column().classes("w-full max-w-[1800px] mx-auto gap-0 px-4 pb-8"):
        summary()
        perturbation_summary()
        timeline()
        with ui.splitter(value=63).classes("w-full h-[660px] border-b border-gray-200") as splitter:
            with splitter.before:
                with ui.column().classes("w-full h-full gap-0"):
                    with ui.row().classes("w-full items-center px-4 py-2 bg-white border-b border-gray-200"):
                        ui.label("Task flow").classes("font-semibold")
                    graph()
            with splitter.after:
                with ui.column().classes("w-full h-full gap-0 bg-white border-l border-gray-200 overflow-auto"):
                    inspector()
        with ui.row().classes("w-full items-center mt-5 mb-2"):
            ui.label("Execution events").classes("text-base font-semibold")
            ui.space()

            def toggle_scope(event: events.ValueChangeEventArguments) -> None:
                state.current_events_only = bool(event.value)
                event_log.refresh()

            ui.switch(
                "Current timestep only",
                value=state.current_events_only,
                on_change=toggle_scope,
            ).props("dense")
        event_log()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()
    build_viewer(args.root)
    ui.run(
        host=args.host,
        port=args.port,
        title="DS Reroute Run Inspector",
        show=False,
        reload=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
