"""S8 — run ONE end-to-end episode on the assembled finance environment.

This is the only part of S8 that spends model calls. Everything checkable offline
is checked by `test_finance_env.py` and `test_finance_report_parser.py` first, so
the episode is spent proving what only a run can prove: that the engine applies
the swap, that both the predecessor and the successor actually execute, and that
the DAG completes.

  uv run python -m experiments.worker_replacement.run_finance_episode --seed 101

Writes a RUN BUNDLE to records/S8/. The bundle carries the instance seed and its
content hash, so an episode's provenance is checkable rather than asserted; a
seed alone would not catch a generator change between the run and the reading.

No LLM judge is involved anywhere. Scoring is post-hoc: worker text -> the
deterministic parser -> S4's scorer.
"""

from __future__ import annotations

import argparse
import asyncio
import faulthandler
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from manager_agent_gym import ChainOfThoughtManagerAgent, WorkflowExecutionEngine
from manager_agent_gym.core.common.model_provider import (
    disable_agents_tracing_if_proxied,
)
from manager_agent_gym.core.common.run_trace import RunTraceRecorder
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.schemas.execution.callbacks import TimestepEndContext
from manager_agent_gym.schemas.execution.observation_policy import ObservationPolicy
from manager_agent_gym.schemas.preferences.evaluator import (
    AggregationStrategy,
    Evaluator,
)
from manager_agent_gym.schemas.preferences.preference import (
    Preference,
    PreferenceWeights,
)

from examples.common_stakeholders import create_stakeholder_agent

from manager_agent_gym.core.workflow_agents.ai_agent import (
    WORKER_RUN_BACKSTOP_S as _WORKER_BACKSTOP,
    _apply_worker_request_limits as _worker_request_limits,
)

from . import finance_generator as gen
from . import finance_env as env
from . import finance_report_parser as rp
from . import finance_scorer as sc

# SELF-DUMPING STACKS ON A HANG. Two runs stalled and NEITHER could be inspected:
# `ptrace_scope=1` blocks py-spy without elevated privileges, and escalating
# privileges to read a stack is not a trade worth making. So the process dumps its
# own.
#
# `faulthandler.dump_traceback_later(repeat=True)` prints EVERY thread's stack to
# stderr on a timer and rearms, so a hang produces a stack every interval instead
# of silence. Same defect as the heartbeat one level down: "where is it stuck" was
# unanswerable BY CONSTRUCTION, and the fix is instrumentation rather than
# inference.
#
# Cancelled on a clean finish, so a normal run prints nothing.
HANG_DUMP_INTERVAL_S = float(os.getenv("MAG_HANG_DUMP_INTERVAL_S", "120"))

HERE = Path(__file__).resolve().parent
MANAGER_MODEL = env.WORKER_MODEL  # flash for every role (run-spend authorisation)


def _preferences() -> PreferenceWeights:
    """A single placeholder preference.

    Deliberately inert: the study's outcome is the S4 score computed post-hoc from
    parsed reports, NOT a preference-weighted rubric, and no LLM judge runs in the
    loop. This exists only because the engine requires a preference object.
    """
    return PreferenceWeights(preferences=[
        Preference(
            name="completion", weight=1.0,
            description="Complete the capital calculation",
            evaluator=Evaluator(
                name="placeholder",
                description="Not scored — the outcome is computed post-hoc by "
                            "the S4 scorer over parsed reports.",
                aggregation=AggregationStrategy.WEIGHTED_AVERAGE, rubrics=[]),
        )
    ])


class _Recorder:
    """Per-task completion facts needed to reconstruct the allocation."""

    def __init__(self) -> None:
        self.completions: list[dict] = []

    async def callback(self, ctx: TimestepEndContext) -> None:
        # PER-TIMESTEP HEARTBEAT. Two runs have now stalled mid-episode and
        # neither could say WHERE, because this runner printed only on completion
        # -- so a stalled run and a slow run produced the identical artefact:
        # nothing. The discriminating question is whether the stall lands at a
        # CONSISTENT point (request-specific and reproducible) or a scattered one
        # (the provider), and it cannot be asked without this line.
        #
        # Flushed, because a buffered heartbeat is not a heartbeat: the buffer is
        # exactly what a hang fails to flush.
        print(f"[t{ctx.timestep:02d}] completed={len(self.completions)} "
              f"+{len(ctx.tasks_completed)} this step", flush=True)
        for task_id in ctx.tasks_completed:
            task = ctx.workflow.tasks.get(task_id)
            if task is None:
                continue
            self.completions.append({
                "timestep": ctx.timestep,
                "task_id": str(task_id),
                "task_name": task.name,
                "agent_id": task.assigned_agent_id,
                "output_resource_ids": [str(r) for r in task.output_resource_ids],
            })


def _install_dry_run_stubs() -> None:
    """Replace the LLM calls with deterministic stand-ins. ZERO API calls.

    Exercises the ENTIRE runner path — engine loop, roster swap, completion
    recording, allocation reconstruction, parser, scorer, bundle write — without
    spending the authorised episode. A crash in the post-processing after the
    model calls have been made would waste the one run we are allowed, so the
    path is proven cold first.

    The stub worker emits a FAITHFUL, conventional report, so a dry run should
    parse 9/9. That is the point: any parse failure in a dry run is the harness's
    fault, which is exactly what we want to find before the real episode.
    """
    from manager_agent_gym.core.manager_agent import structured_manager
    from manager_agent_gym.core.workflow_agents import ai_agent as ai_agent_module
    from manager_agent_gym.schemas.core.resources import Resource
    from manager_agent_gym.schemas.unified_results import create_task_result

    segment_lookup: dict[str, dict] = {}

    async def _stub_execute(self, task, resources):
        segment = segment_lookup.get(task.name)
        if segment is not None:
            worker = next(
                w for w in _DRY_RUN_INSTANCE["workers"]
                if w["worker_id"] == self.config.agent_id)
            value = sc.attainable_report(segment, worker)
            text = (f"Computed for {segment['segment_id']}.\n"
                    f"method: {sc.applicable_approach(segment)}\n"
                    f"rwa: {value:,.2f}")
        else:
            text = "Done."
        return create_task_result(
            task_id=task.id, agent_id=self.config.agent_id, success=True,
            execution_time=0.01,
            resources=[Resource(name=f"{task.name} output", description="stub",
                                content=text)])

    for segment in _DRY_RUN_INSTANCE["segments"]:
        segment_lookup[f"Risk-weighted assets — {segment['segment_id']}"] = segment

    ai_agent_module.AIAgent.execute_task = _stub_execute

    # A round-robin manager: assigns every ready, unassigned task to the
    # least-loaded present worker. Deterministic, no model call.
    from manager_agent_gym.schemas.core.base import TaskStatus

    async def _stub_take_action(self, observation):
        from manager_agent_gym.schemas.execution.manager_actions import NoOpAction
        workflow = _DRY_RUN_ENGINE["engine"].workflow
        present = [a for a in workflow.agents.values()
                   if a.agent_id.startswith("w_")]
        if present:
            # Count SEGMENT assignments separately: the capacity bound applies to
            # segment tasks only, and a stub that ignores it strands a task on a
            # full worker (measured: 12/16 completed, one segment unstaffed). The
            # real manager's allocation quality is the study's subject; this stub
            # only has to exercise the plumbing without deadlocking it.
            seg_counts = {a.agent_id: 0 for a in present}
            all_counts = {a.agent_id: 0 for a in present}
            for task in workflow.tasks.values():
                if task.assigned_agent_id in all_counts:
                    all_counts[task.assigned_agent_id] += 1
                    # is_metered, not the name (L1 criterion (e)): the
                    # stub must count what the ENGINE meters, or it strands work
                    # for a reason invisible to both.
                    if env.CapacityBoundedAIAgent.is_metered(task):
                        seg_counts[task.assigned_agent_id] += 1
            for task in workflow.get_ready_tasks():
                if task.assigned_agent_id is not None or task.status == TaskStatus.RUNNING:
                    continue
                # `is_metered`, NOT the name — the same predicate the counting
                # loop above already uses, and for the same reason (L1 criterion
                # (e)). This line still read `task.name.startswith(prefix)` with
                # `prefix` UNDEFINED, two lines below a comment saying not to use
                # the name: a NameError on every dry run that reached a ready
                # unassigned task, so this branch had never once executed.
                #
                # It is the third instance this phase of a comment naming a failure
                # directly above code repeating it. The comment was written while
                # the OTHER line was being fixed, and this one was not revisited.
                if env.CapacityBoundedAIAgent.is_metered(task):
                    eligible = [a for a in seg_counts
                                if seg_counts[a] < env.CapacityBoundedAIAgent.segment_capacity]
                    if not eligible:
                        continue
                    chosen = min(eligible, key=lambda a: (seg_counts[a], a))
                    seg_counts[chosen] += 1
                else:
                    chosen = min(all_counts, key=lambda a: (all_counts[a], a))
                task.assigned_agent_id = chosen
                all_counts[chosen] += 1
        return NoOpAction(reasoning="dry run")

    structured_manager.ChainOfThoughtManagerAgent.take_action = _stub_take_action


_DRY_RUN_INSTANCE: dict = {}
_DRY_RUN_ENGINE: dict = {}


async def run_episode(seed: int, out_dir: Path, dry_run: bool = False,
                      cell: str | None = None, concurrency: int = 1,
                      lattice: str = gen.DEFAULT_LATTICE,
                      shared_class_segments: int = 4,
                      selection_record: Path | None = None) -> dict:
    # THE ARRANGEMENT TRAVELS WITH THE RUN, and it did not. Both builders called
    # `gen.generate(seed)` bare, so an episode built the DEFAULT lattice whatever
    # arrangement the study had selected, and `lattice="current"` is legal so
    # nothing raised.
    # Arm the hang dump for the duration of the episode.
    faulthandler.dump_traceback_later(HANG_DUMP_INTERVAL_S, repeat=True, exit=False)
    try:
        return await _run_episode_inner(
            seed=seed, out_dir=out_dir, dry_run=dry_run, cell=cell,
            concurrency=concurrency, lattice=lattice,
            shared_class_segments=shared_class_segments,
            selection_record=selection_record)
    finally:
        faulthandler.cancel_dump_traceback_later()


async def _run_episode_inner(
    seed: int, out_dir: Path, dry_run: bool = False,
    cell: str | None = None, concurrency: int = 1,
    lattice: str = gen.DEFAULT_LATTICE,
    shared_class_segments: int = 4,
    selection_record: Path | None = None,
) -> dict:
    if selection_record is not None:
        # AND IT IS CHECKED AGAINST THE RECORD IT CLAIMS TO BE RUNNING, rather than
        # trusting that the right flags were passed. Two artefacts asserting
        # different arrangements is what this whole phase has been spent removing;
        # passing flags correctly is a habit, and this is a guard.
        chosen = json.loads(Path(selection_record).read_text())
        mismatch = {k: (chosen.get(k), v) for k, v in
                    (("lattice", lattice),
                     ("shared_class_segments", shared_class_segments))
                    if chosen.get(k) != v}
        if mismatch:
            raise ValueError(
                f"arrangement mismatch against {selection_record}: {mismatch}. The "
                f"selection record and the run disagree about which arrangement "
                f"this is, and the bundle would record the seed and look correct"
            )
        if seed not in (chosen.get("chosen_seeds") or []):
            raise ValueError(
                f"seed {seed} is not in {selection_record}'s chosen_seeds "
                f"{chosen.get('chosen_seeds')}; running an unselected seed under a "
                f"selection record misattributes it to a rule that did not pick it"
            )

    # CELL is the study configuration (R2). Absent means the S8 accurate-card
    # default, which is what the machinery episodes ran on.
    if cell is None:
        built = env.build_environment(
            seed, lattice=lattice, shared_class_segments=shared_class_segments)
    else:
        from . import finance_cells as fc

        built = fc.build_cell_environment(
            seed, cell, lattice=lattice,
            shared_class_segments=shared_class_segments)
    instance = built["instance"]
    workflow = built["workflow"]
    index = built["index"]
    event = instance["event"]

    # The two upstream FIXED tasks are pre-assigned to the predecessor. Left to
    # the manager they might never reach it, and the episode would carry no
    # pre-swap evidence of the worker about to be replaced.
    for task_id in index["fixed_task_ids"]:
        workflow.tasks[__import__("uuid").UUID(task_id)].assigned_agent_id = (
            event["predecessor_id"])

    if dry_run:
        _DRY_RUN_INSTANCE.update(instance)
        _install_dry_run_stubs()

    # BULK ASSIGNMENT, added to the default action set (experiment-local, not a
    # global default change). `AssignTasksToAgentsAction` exists upstream and is
    # NOT in `get_default_action_classes()`, so the manager could only assign one
    # task per timestep. That was the binding constraint on the landed episode:
    # 14 tasks needing assignment cannot be assigned in 14 timesteps while also
    # leaving room for the work to run, and two segments plus the whole downstream
    # chain went unrun.
    #
    # It is arguably the more faithful action set for THIS study as well as the
    # cheaper one: the construct is ALLOCATION, and an allocation decision made
    # over a view of the whole board is closer to what a manager does than a
    # dribble of single assignments. MUST BE HELD CONSTANT ACROSS CELLS — it is
    # part of the manager's action space, not a channel.
    from manager_agent_gym.core.manager_agent.llm_action_utils import (
        get_default_action_classes,
    )
    from manager_agent_gym.schemas.execution.manager_actions import (
        AssignTasksToAgentsAction,
    )

    action_classes = [*get_default_action_classes(), AssignTasksToAgentsAction]
    manager = ChainOfThoughtManagerAgent(
        preferences=_preferences(), model_name=MANAGER_MODEL,
        action_classes=action_classes)
    stakeholder = create_stakeholder_agent(
        persona="balanced", preferences=_preferences())
    # FLASH FOR EVERY ROLE. The persona helper leaves `model_name` at the
    # settings default, which is gpt-4o-mini — outside the run authorisation
    # (flash, all roles) and against the standing model preference. Overridden
    # explicitly here and asserted below rather than assumed from .env.
    stakeholder.config.model_name = MANAGER_MODEL
    role_models = {
        "manager": manager.model_name,
        "stakeholder": stakeholder.config.model_name,
        **{aid: cfg.model_name for aid, cfg in built["team"].items()},
    }
    off_policy = sorted(r for r, m in role_models.items() if m != MANAGER_MODEL)
    if off_policy:
        raise RuntimeError(
            f"run authorisation is flash for ALL roles; these are not: "
            f"{ {r: role_models[r] for r in off_policy} }"
        )
    print(f"all {len(role_models)} roles on {MANAGER_MODEL}")
    recorder = _Recorder()
    tracer = RunTraceRecorder(metadata={
        "study_step": "S8",
        "instance_seed": seed,
        # The ARRANGEMENT, in the bundle, so a bundle can never again be silent
        # about which one produced it.
        "lattice": instance["parameters"]["lattice"],
        "shared_class_segments": instance["parameters"]["shared_class_segments"],
        "instance_sha256": built["instance_sha256"],
        "manager_model": MANAGER_MODEL,
        "worker_model": env.WORKER_MODEL,
        "horizon": built["horizon"],
        "capacity_mapping": built["capacity_mapping"],
        "t_swap": event["t_swap"],
        "predecessor_id": event["predecessor_id"],
        "successor_id": event["successor_id"],
    })

    engine = WorkflowExecutionEngine(
        workflow=workflow,
        agent_registry=built["registry"],
        manager_agent=manager,
        stakeholder_agent=stakeholder,
        communication_service=CommunicationService(),
        max_timesteps=built["horizon"],
        enable_timestep_logging=True,
        enable_final_metrics_logging=False,
        timestep_end_callbacks=[recorder.callback, tracer.timestep_callback],
        observation_policy=ObservationPolicy(),
        seed=seed,
    )

    _DRY_RUN_ENGINE["engine"] = engine
    started_at = datetime.now(timezone.utc).isoformat()
    with tracer.activate():
        await engine.run_full_execution(save_outputs=False)
    finished_at = datetime.now(timezone.utc).isoformat()

    # --- reconstruct the allocation and the deliverables ---------------------
    task_to_segment = {tid: sid for sid, tid in index["segment_task_ids"].items()}
    resources = {str(rid): res for rid, res in workflow.resources.items()}

    allocation: dict[str, str] = {}
    deliverables: dict[str, str | None] = {}
    for completion in recorder.completions:
        segment_id = task_to_segment.get(completion["task_id"])
        if segment_id is None:
            continue
        allocation[segment_id] = completion["agent_id"]
        texts = [resources[rid].content for rid in completion["output_resource_ids"]
                 if rid in resources]
        deliverables[segment_id] = "\n\n".join(t for t in texts if t) or None

    segment_ids = [s["segment_id"] for s in instance["segments"]]

    # THE INTENDED ALLOCATION, FROM THE ASSIGNMENT RECORD — not from completions.
    #
    # THIS IS THE DEFECT THAT HID A WEEK OF WRONG STATEMENTS. `allocation` above is
    # built by walking COMPLETIONS, so a segment the manager assigned and the
    # engine never executed cannot be represented in it at all: it silently became
    # `__unstaffed__`, which reads as "the manager never staffed it". Measured
    # across the 18 scope episodes: ALL 22 so-called unstaffed segments carry a
    # real `assigned_agent_id` on the board, and ZERO were never assigned. The
    # manager routed every one of them.
    #
    # So "non-routing" was never non-routing. It was ASSIGNED-AND-NEVER-EXECUTED —
    # 580 `assignment_deferred` events across the study, workers at
    # max_concurrent_tasks=1, and a manager whose context contains no word for any
    # of it.
    parsed_lookup = rp.parse_segment_reports(deliverables, segment_ids)["reports"]
    intended: dict[str, str | None] = {}
    for segment_id, task_id in index["segment_task_ids"].items():
        task = workflow.tasks.get(__import__("uuid").UUID(task_id))
        intended[segment_id] = task.assigned_agent_id if task else None

    # FOUR STATES, because the old two collapsed three distinct outcomes into one.
    segment_states: dict[str, str] = {}
    for segment_id in segment_ids:
        if not intended.get(segment_id):
            segment_states[segment_id] = "never_assigned"
        elif segment_id not in allocation:
            segment_states[segment_id] = "assigned_but_unexecuted"
        elif parsed_lookup.get(segment_id) is None:
            segment_states[segment_id] = "executed_but_unparseable"
        else:
            segment_states[segment_id] = "executed_and_parsed"

    unstaffed = [sid for sid in segment_ids if sid not in allocation]
    for segment_id in unstaffed:
        allocation[segment_id] = "__unstaffed__"

    parsed = rp.parse_segment_reports(deliverables, segment_ids)
    parsed_lookup = parsed["reports"]
    achieved = sc.achieved(instance, allocation, parsed["reports"])

    # SCORE AGAINST THE CELL'S OWN ROSTER. Cell U keeps the PRE-swap roster, so
    # its oracle is over a different team; scoring it post-swap compares its
    # regret to an optimum for a team it never had. Measured on seed 3: 8.7337
    # pre-swap against 8.5462 post-swap, so U's regret was understated by 0.1875.
    #
    # `finance_cells.active_roster()` had this right and the runner did not read
    # it — the fix existed one module away and was never wired through.
    phase = "pre_swap" if (cell is not None and not built["cell_config"]["swap"]) \
        else "post_swap"
    oracle_value = sc.oracle_capacitated(instance, phase=phase, cap=3)

    tag = f"cell{cell}_" if cell else ""
    bundle_path = out_dir / (
        f"dry_run_{tag}seed{seed}.json" if dry_run
        else f"run_{tag}seed{seed}.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    tracer.write_json(
        bundle_path,
        manifest={
            "study_step": "S8" if cell is None else "R2-scope",
            "cell": cell,
            "cell_config": built.get("cell_config"),
            # CONCURRENCY IS AN INSTRUMENT SETTING (LS ruling). The first four
            # scope episodes ran at N=4 and the remaining fourteen at N=2, so it
            # VARIES ACROSS CELLS — normally forbidden by the comparability rule.
            # Accepted as a recorded limitation for an exploratory run, on the
            # condition that it is auditable per bundle rather than remembered.
            # For any powered study it is constant across cells, no exceptions.
            "concurrency": concurrency,
            "dry_run": dry_run,
            "instance_seed": seed,
            # THE ARRANGEMENT, IN THE BUNDLE THAT IS ACTUALLY WRITTEN. The first
            # version of this fix added the fields to the other payload in this
            # file and I read the log line rather than the artefact -- the run
            # reported OK while every written bundle carried `lattice: None`. The
            # fields are on both now, and the acceptance reads the FILE.
            "lattice": instance["parameters"]["lattice"],
            "shared_class_segments": instance["parameters"]["shared_class_segments"],
            # WHAT THIS RUN WAS WILLING TO WAIT FOR. Same reason as the
            # arrangement: a bundle that cannot say its own timeout cannot be told
            # apart from one that had none -- and until now none of them had one.
            **_worker_request_limits(),
            "worker_run_backstop_s": _WORKER_BACKSTOP,
            "instance_sha256": built["instance_sha256"],
            "manager_model": MANAGER_MODEL,
            "worker_model": env.WORKER_MODEL,
            "role_models": role_models,
            "horizon": built["horizon"],
            "capacity_mapping": built["capacity_mapping"],
            "t_swap": event["t_swap"],
            "predecessor_id": event["predecessor_id"],
            "successor_id": event["successor_id"],
            "roster_pre_swap": event["roster_pre_swap"],
            "roster_post_swap": event["roster_post_swap"],
            "n_tasks": index["n_tasks"],
            "manager_action_types": sorted(
                c.model_fields["action_type"].default for c in action_classes),
            "started_at": started_at,
            "finished_at": finished_at,
        },
        index=index,
        # THE ASSIGNMENT RECORD, distinct from the realised one. `allocation` is
        # what EXECUTED; `intended_allocation` is what the manager ASSIGNED. They
        # differ exactly where the engine deferred an assignment forever, and
        # conflating them is what made "the manager failed to staff" out of "the
        # manager assigned and the engine never ran it".
        intended_allocation=intended,
        segment_states=segment_states,
        # THE BOARD AS THE MANAGER LAST SAW IT. Recorded because a task still
        # assigned to the DEPARTED predecessor is INTENDED SEMANTICS (spec E5,
        # novelty property 2): inherited workflow state surfacing on the board,
        # and noticing-then-reassigning it is the succession behaviour the study
        # measures. It is never to be cleaned up, and it has to be visible in the
        # bundle or a reviewer cannot tell the intended line from a swap bug.
        task_board_final=[
            {"task_name": t.name, "task_id": str(t.id),
             "status": t.status.value, "assigned_agent_id": t.assigned_agent_id}
            for t in workflow.tasks.values()
        ],
        completions=recorder.completions,
        allocation=allocation,
        unstaffed_segments=unstaffed,
        parse_detail=parsed["detail"],
        parse_failures=parsed["failures"],
        reports=parsed["reports"],
        outcome={
            "achieved": achieved,
            "oracle_capacitated": oracle_value,
            "oracle_roster_phase": phase,
            "n_parsed": parsed["n_parsed"],
            "n_missing": parsed["n_missing"],
            # DECLINES ARE THE POINT OF THE UNSCRIPTING, and the runner was not
            # recording them. The parser has produced n_declined / n_unreadable /
            # declined_segments since R1 item 4; the outcome block wrote neither.
            # Same failure as the U-oracle defect: the correct thing existed one
            # module away and was not wired through. Recoverable post hoc from
            # `parse_detail`, which is why no episode is re-run — but a summary
            # nobody reads is how a channel we built stops being observed.
            "n_declined": parsed["n_declined"],
            "n_unreadable": parsed["n_unreadable"],
            "declined_segments": parsed["declined_segments"],
            "n_unstaffed": len(unstaffed),
        },
        deliverables=deliverables,
    )
    print(f"\nrun bundle -> {bundle_path}")
    print(f"  completions {len(recorder.completions)}/{index['n_tasks']}, "
          f"parsed {parsed['n_parsed']}/{len(segment_ids)}, "
          f"unstaffed {len(unstaffed)}")
    print(f"  achieved {achieved:.4f} of capacitated oracle {oracle_value:.4f} "
          f"({phase} roster)")
    return {"bundle_path": bundle_path}


async def main() -> None:
    disable_agents_tracing_if_proxied()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--concurrency", type=int, default=1,
                        help="episodes running in parallel; an INSTRUMENT SETTING, "
                             "recorded per bundle")
    parser.add_argument("--cell", type=str, default=None,
                        help="study cell: U 0 1 2 3 4 (omit for the S8 default)")
    parser.add_argument("--dry-run", action="store_true",
                        help="stub every model call; proves the runner path cold")
    parser.add_argument("--out", type=Path, default=HERE / "records" / "S8")
    args = parser.parse_args()
    await run_episode(args.seed, args.out, dry_run=args.dry_run, cell=args.cell,
                      concurrency=args.concurrency)


if __name__ == "__main__":
    asyncio.run(main())
