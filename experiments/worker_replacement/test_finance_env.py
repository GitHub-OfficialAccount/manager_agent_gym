"""S8 acceptance (offline) — environment assembly, zero model calls.

Everything about the assembled environment that can be checked WITHOUT spending
the authorised episode is checked here first, so the run is spent proving the
things only a run can prove (the engine applies the swap, workers execute, the
DAG completes) rather than rediscovering a typo in a card.

  1. The DAG has the specified shape and task count 15-20.
  2. The capacity mapping is arithmetic, not narration: horizon, window and
     roster size must actually multiply out to C = 3 and cover the segments.
  3. LEAKAGE, asserted per artifact: no card, task description, or agent
     capability may contain a private calibration value or the raw `irb_coverage`
     field. This is the one that would silently invalidate the study.
  4. The swap is wired off the event block, and the registry applies it at t_swap.
  5. The environment is built from a GENERATED, ADMITTED instance (E6), and its
     provenance hash is reproducible.

Run:  python3 -m experiments.worker_replacement.test_finance_env
"""

from __future__ import annotations

import json
from pathlib import Path

from . import finance_admission as adm
from . import finance_env as env
from . import finance_generator as gen
from . import finance_report_parser as rp

HERE = Path(__file__).resolve().parent
SEED = 101



def _drive_capacity_probe(cap: int = 1) -> int:
    """Five ready tasks, one worker, cap 1 -> one start per timestep.

    A stub worker, so this costs nothing and isolates the ENGINE's behaviour from
    any model's. Before the core fix this started all five at once.
    """
    import asyncio
    from uuid import uuid4

    from manager_agent_gym.core.execution.engine import WorkflowExecutionEngine
    from manager_agent_gym.core.workflow_agents.interface import AgentInterface
    from manager_agent_gym.core.workflow_agents.registry import AgentRegistry
    from manager_agent_gym.core.workflow_agents.stakeholder_agent import StakeholderAgent
    from manager_agent_gym.schemas.core.tasks import Task
    from manager_agent_gym.schemas.core.workflow import Workflow
    from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
    from manager_agent_gym.schemas.unified_results import create_task_result
    from manager_agent_gym.schemas.workflow_agents import AgentConfig
    from manager_agent_gym.schemas.workflow_agents.stakeholder import StakeholderConfig
    from tests.helpers.stubs import ManagerNoOp

    class _Stub(AgentInterface):
        def __init__(self, agent_id: str):
            super().__init__(AgentConfig(
                agent_id=agent_id, agent_type="ai",
                system_prompt="stub worker for the capacity probe",
                model_name="none",
                agent_description="stub worker for the capacity probe",
                agent_capabilities=["stub worker"]))

        async def execute_task(self, task, resources):
            return create_task_result(task_id=task.id, agent_id=self.agent_id,
                                      success=True, execution_time=0.01, resources=[])

    workflow = Workflow(name="cap", workflow_goal="d", owner_id=uuid4())
    for i in range(5):
        task = Task(name=f"T{i}", description="d")
        task.assigned_agent_id = "worker-1"
        workflow.add_task(task)
    worker = _Stub("worker-1")
    worker.max_concurrent_tasks = cap
    workflow.add_agent(worker)

    stakeholder = StakeholderAgent(config=StakeholderConfig(
        agent_id="stakeholder", agent_type="stakeholder",
        system_prompt="stakeholder for the capacity probe",
        model_name="none",
        agent_description="stakeholder for the capacity probe",
        agent_capabilities=["stakeholder"],
        name="S", role="Owner",
        initial_preferences=PreferenceWeights(preferences=[])))
    workflow.add_agent(stakeholder)

    engine = WorkflowExecutionEngine(
        workflow=workflow, agent_registry=AgentRegistry(),
        manager_agent=ManagerNoOp(), stakeholder_agent=stakeholder,
        max_timesteps=10, enable_timestep_logging=False,
        enable_final_metrics_logging=False, seed=1)

    from manager_agent_gym.schemas.core.base import TaskStatus

    async def _one_step():
        await engine.execute_timestep()

    asyncio.run(_one_step())
    # A task that started this timestep is RUNNING: the engine awaits the previous
    # timestep's running set BEFORE starting new work, so a start is visible as
    # RUNNING until the next timestep collects it.
    started = sum(1 for t in workflow.tasks.values()
                  if t.status == TaskStatus.RUNNING)
    print(f"   5 ready tasks, one worker at max_concurrent_tasks={cap}: "
          f"{started} started in timestep 0")
    return started


def main() -> int:
    failures: list[str] = []
    print("S8 — environment assembly (offline, zero model calls)\n")

    # --- 5. built from a generated, ADMITTED instance -------------------------
    verdict = adm.admit(SEED)
    print(f"1. provenance (E6 — no hand-authored environment data):")
    print(f"   instance seed {SEED}, admitted {verdict['admitted']}, "
          f"conditions {sorted(k for k, v in verdict['conditions'].items() if v)}")
    if not verdict["admitted"]:
        print(f"     rejection reasons: {verdict['rejection_reasons']}")
    admitted_ok = verdict["admitted"]
    print(f"   [{'ok' if admitted_ok else 'FAIL'}] the environment is built from an "
          f"ADMITTED instance, not a hand-authored one")
    if not admitted_ok:
        failures.append("environment instance is not admitted")

    built = env.build_environment(SEED)
    instance = built["instance"]
    workflow = built["workflow"]
    index = built["index"]

    rebuilt = env.instance_hash(gen.generate(SEED))
    hash_ok = rebuilt == built["instance_sha256"]
    print(f"   instance sha256 {built['instance_sha256'][:16]}... -> "
          f"[{'ok' if hash_ok else 'FAIL'}] reproducible from the seed alone")
    if not hash_ok:
        failures.append("instance hash is not reproducible")

    # --- 1. the DAG ----------------------------------------------------------
    n_tasks = len(workflow.tasks)
    print(f"\n2. the task DAG: {n_tasks} tasks")
    print(f"   {len(index['fixed_task_ids'])} upstream FIXED (pre-assigned to the "
          f"predecessor), {len(index['upstream_task_ids'])} upstream total,")
    print(f"   {len(index['segment_task_ids'])} per-segment, "
          f"{len(index['downstream_task_ids'])} downstream")
    count_ok = 15 <= n_tasks <= 20
    print(f"   [{'ok' if count_ok else 'FAIL'}] task count in the specified 15-20")
    if not count_ok:
        failures.append(f"task count {n_tasks} outside 15-20")

    segs_ok = set(index["segment_task_ids"]) == {
        s["segment_id"] for s in instance["segments"]}
    print(f"   [{'ok' if segs_ok else 'FAIL'}] every segment has exactly one task")
    if not segs_ok:
        failures.append("segment tasks do not match the instance's segments")

    # The DAG must actually be a DAG with the intended layering: no segment task
    # may be ready before the upstream is done, and nothing downstream before all
    # segments. Asserted on the dependency ids rather than assumed from the
    # construction order.
    by_id = {str(t.id): t for t in workflow.tasks.values()}
    fixed = set(index["fixed_task_ids"])
    open_upstream = set(index["upstream_task_ids"]) - fixed
    seg_ids = set(index["segment_task_ids"].values())
    layered = all(
        fixed <= {str(d) for d in by_id[t].dependency_task_ids} for t in seg_ids)
    # And the discretionary upstream tasks must NOT be on the critical path — the
    # first real episode lost every segment to an upstream task that failed.
    off_path = all(
        not (open_upstream & {str(d) for d in by_id[t].dependency_task_ids})
        for t in seg_ids)
    first_downstream = index["downstream_task_ids"][0]
    gated = seg_ids <= {str(d) for d in by_id[first_downstream].dependency_task_ids}
    print(f"   [{'ok' if layered else 'FAIL'}] every segment task depends on the "
          f"FIXED upstream tasks")
    print(f"   [{'ok' if off_path else 'FAIL'}] and on NONE of the discretionary "
          f"upstream tasks — the study's\n        payload is not behind a task that "
          f"can fail (it did, in the first episode)")
    if not off_path:
        failures.append("discretionary upstream tasks are on the critical path")
    print(f"   [{'ok' if gated else 'FAIL'}] aggregation depends on ALL segment tasks")
    if not layered:
        failures.append("segment tasks are not gated on the fixed upstream layer")
    if not gated:
        failures.append("aggregation is not gated on all segment tasks")

    # --- 2. the capacity mapping, as arithmetic ------------------------------
    mapping = built["capacity_mapping"]
    print(f"\n3. capacity mapping (S7 ruled C = 3; the runtime must MIRROR it):")
    print(f"   {mapping['segment_window_timesteps']} timesteps x "
          f"{mapping['max_concurrent_tasks_per_worker']} task/timestep/worker = "
          f"{mapping['segment_window_timesteps']} tasks per worker")
    print(f"   x {mapping['post_swap_roster_size']} post-swap workers = "
          f"{mapping['segment_window_timesteps'] * mapping['post_swap_roster_size']} "
          f"vs {mapping['n_segments']} segments")
    capacity = (mapping["segment_window_timesteps"]
                * mapping["max_concurrent_tasks_per_worker"])
    cap_ok = capacity == 3
    exact_ok = capacity * mapping["post_swap_roster_size"] == mapping["n_segments"]
    print(f"   [{'ok' if cap_ok else 'FAIL'}] per-worker capacity is exactly 3")
    print(f"   [{'ok' if exact_ok else 'FAIL'}] capacity is consumed EXACTLY "
          f"(no slack, so the allocation problem is which-goes-where)")
    if not cap_ok:
        failures.append(f"runtime per-worker capacity is {capacity}, not 3")
    if not exact_ok:
        failures.append("runtime capacity does not equal the segment count")

    expected_horizon = (
        instance["event"]["t_swap"]
        + (index["n_tasks"] - len(index["fixed_task_ids"]))
        + env.DOWNSTREAM_STAGES + env.HORIZON_SLACK)
    horizon_ok = built["horizon"] == expected_horizon
    print(f"   horizon {built['horizon']} = t_swap {instance['event']['t_swap']} + "
          f"{index['n_tasks'] - len(index['fixed_task_ids'])} tasks needing "
          f"assignment\n        + {env.DOWNSTREAM_STAGES} downstream chain + "
          f"{env.HORIZON_SLACK} slack -> "
          f"[{'ok' if horizon_ok else 'FAIL'}] follows from the DAG and t_swap")
    print(f"   SIZED FOR THE MANAGER, NOT THE WORK: ChainOfThoughtManagerAgent "
          f"returns ONE\n        action per timestep, so tasks needing assignment "
          f"set the floor. The landed\n        episode ran out at a "
          f"pipeline-sized horizon of 14 with 2 segments unassigned.")
    print(f"   A generous horizon is FREE (the engine stops at the terminal state) "
          f"and SAFE\n        (C=3 is enforced by the worker, not by the horizon).")
    if not horizon_ok:
        failures.append("horizon does not follow from the DAG and t_swap")

    # --- 3. LEAKAGE ----------------------------------------------------------
    # The check that matters most: if a private calibration reaches the manager or
    # a task description, the competence gap is public and the study measures
    # nothing. Every calibration VALUE in the instance is searched for, in every
    # string the manager or a worker other than its holder could see.
    print(f"\n4. leakage — private calibrations and raw coverage must not appear "
          f"in\n   anything public (cards, capabilities, task text):")
    private_values: set[str] = set()
    for worker in instance["workers"]:
        for buckets in worker["private_pd_calibration"].values():
            for value in buckets.values():
                private_values.add(f"{value:.6f}")
                private_values.add(str(value))

    public_strings: list[tuple[str, str]] = []
    for agent_id, config in built["team"].items():
        public_strings.append((f"card[{agent_id}]", config.agent_description))
        public_strings.append(
            (f"capabilities[{agent_id}]", " ".join(config.agent_capabilities)))
    for task in workflow.tasks.values():
        public_strings.append((f"task[{task.name}]", task.description))

    leaks = [
        (where, value) for where, text in public_strings
        for value in private_values if value in text
    ]
    print(f"   searched {len(private_values)} calibration values across "
          f"{len(public_strings)} public strings")
    print(f"   [{'ok' if not leaks else 'FAIL'}] no calibration value appears in "
          f"public text ({len(leaks)} leaks)")
    for where, value in leaks[:5]:
        print(f"     LEAK {where}: {value}")
    if leaks:
        failures.append(f"{len(leaks)} private calibration values leaked")

    # The check must not be vacuous: the values MUST be present in the private
    # system prompts, or the search above proves nothing.
    provisioned = sum(
        1 for worker in instance["workers"]
        if any(f"{value:.6f}" in built["team"][worker["worker_id"]].system_prompt
               for buckets in worker["private_pd_calibration"].values()
               for value in buckets.values())
    )
    holders = sum(1 for w in instance["workers"] if w["private_pd_calibration"])
    provisioned_ok = provisioned == holders and holders > 0
    print(f"   [{'ok' if provisioned_ok else 'FAIL'}] and the search is NOT vacuous: "
          f"{provisioned}/{holders} calibration holders\n        carry their values "
          f"in their PRIVATE system prompt")
    if not provisioned_ok:
        failures.append("calibrations are not privately provisioned; leak check is vacuous")

    # Raw `irb_coverage` must not be quoted as a field anywhere public.
    coverage_leaks = [
        where for where, text in public_strings if "irb_coverage" in text
    ]
    print(f"   [{'ok' if not coverage_leaks else 'FAIL'}] the raw `irb_coverage` "
          f"field name appears nowhere public")
    if coverage_leaks:
        failures.append(f"irb_coverage leaked into {coverage_leaks}")

    # --- 4. the swap ---------------------------------------------------------
    print(f"\n5. swap wiring (driven off schema v2's event block):")
    event = instance["event"]
    registry = built["registry"]
    import asyncio

    applied_at_zero = asyncio.run(
        registry.apply_scheduled_changes_for_timestep(0))
    print(f"   t=0 applied: {len(applied_at_zero)} change(s) -> pre-swap roster "
          f"{sorted(a.agent_id for a in registry.list_agents())}")
    pre_ok = (sorted(a.agent_id for a in registry.list_agents())
              == sorted(event["roster_pre_swap"]))
    print(f"   [{'ok' if pre_ok else 'FAIL'}] the t=0 roster IS the event block's "
          f"roster_pre_swap")
    if not pre_ok:
        failures.append("t=0 roster does not match roster_pre_swap")

    applied_at_swap = asyncio.run(
        registry.apply_scheduled_changes_for_timestep(int(event["t_swap"])))
    lines = registry.roster_change_lines()
    post = sorted(a.agent_id for a in registry.list_agents())
    print(f"   t={event['t_swap']} applied: {len(applied_at_swap)} change(s) -> "
          f"post-swap roster {post}")
    for line in lines:
        print(f"     {line}")
    swap_ok = len(applied_at_swap) == 2 and len(lines) == 2
    post_ok = post == sorted(event["roster_post_swap"])
    named = " ".join(lines)
    ids_ok = event["predecessor_id"] in named and event["successor_id"] in named
    print(f"   [{'ok' if swap_ok else 'FAIL'}] exactly two changes at t_swap "
          f"(one remove, one add)")
    print(f"   [{'ok' if post_ok else 'FAIL'}] the post-swap roster IS the event "
          f"block's roster_post_swap")
    print(f"   [{'ok' if ids_ok else 'FAIL'}] both changes name the event block's "
          f"predecessor and successor")
    if not swap_ok:
        failures.append(f"{len(applied_at_swap)} changes applied at t_swap, expected 2")
    if not post_ok:
        failures.append("post-swap roster does not match roster_post_swap")
    if not ids_ok:
        failures.append("roster change lines do not name the event's pred/succ")

    # --- identifier opacity, end to end --------------------------------------
    semantic = ["irb", "corporate", "sovereign", "retail", "bank", "mdb",
                "quant", "senior", "junior", "expert", "weak", "strong"]
    id_leaks = [
        wid for wid in
        [w["worker_id"] for w in instance["workers"]]
        if any(token in wid.lower() for token in semantic)
    ]
    print(f"\n6. identifier opacity: worker ids "
          f"{[w['worker_id'] for w in instance['workers']]}")
    print(f"   [{'ok' if not id_leaks else 'FAIL'}] no worker id carries a "
          f"competence-bearing token")
    if id_leaks:
        failures.append(f"semantic worker ids: {id_leaks}")

    # --- the convention reaches the worker -----------------------------------
    convention_in_prompt = all(
        rp.REPORT_CONVENTION_TEXT in config.system_prompt
        for config in built["team"].values()
    )
    seg_task = workflow.tasks[
        __import__("uuid").UUID(next(iter(index["segment_task_ids"].values())))]
    convention_in_task = rp.REPORT_CONVENTION_TEXT in seg_task.description
    print(f"\n7. the report convention reaches the worker:")
    print(f"   [{'ok' if convention_in_prompt else 'FAIL'}] in every system prompt")
    print(f"   [{'ok' if convention_in_task else 'FAIL'}] and in every segment task "
          f"description (which the engine's task template renders)")
    if not convention_in_prompt:
        failures.append("report convention missing from a system prompt")
    if not convention_in_task:
        failures.append("report convention missing from a segment task description")

    # --- 8. the capacity mirror ACTUALLY BINDS, driven through the real engine
    # This is the assertion the mapping arithmetic above cannot make. The engine
    # defines `can_handle_task` (which checks `max_concurrent_tasks`) but never
    # called it from the execution path, and never appended to `current_task_ids`
    # on start -- so an agent assigned N ready tasks started ALL N in one timestep
    # and the time-based capacity mapping bounded nothing. Both are fixed in
    # core (see CHANGED.md); this drives the FIXED engine with a stub worker so
    # the property is measured, not asserted about.
    print(f"\n8. capacity enforcement, driven through the production engine:")
    at_one = _drive_capacity_probe(cap=1)
    # DISCRIMINATING CONTROL: at cap 3 the same probe must start THREE. Without
    # it, "1 started" is equally consistent with an engine that always starts one
    # task per agent per timestep for some unrelated reason, and the probe would
    # pass while measuring nothing about the cap.
    at_three = _drive_capacity_probe(cap=3)
    capacity_ok = at_one == 1 and at_three == 3
    print(f"   [{'ok' if capacity_ok else 'FAIL'}] starts track the CAP "
          f"(cap 1 -> {at_one} started, cap 3 -> {at_three} started), so the "
          f"limit is\n        the cap and not a fixed one-per-timestep")
    if not capacity_ok:
        failures.append("engine does not enforce per-worker concurrency; the "
                        "time-based capacity mapping is unbounded")

    # --- 9. TASK-BOARD FIDELITY, and that it stays channel-safe ---------------
    # LS ruling (spec E5): the board renders assignment state so the manager can
    # see whether its own assignment took. Three constraints make that safe, and
    # all three are asserted rather than trusted, because the whole study rests on
    # what the manager can and cannot see.
    print(f"\n9. task-board fidelity (assignment visible, channel-safe):")
    probe_task = workflow.tasks[
        __import__("uuid").UUID(next(iter(index["segment_task_ids"].values())))]
    probe_task.assigned_agent_id = instance["event"]["successor_id"]
    rendered = probe_task.pretty_print(indent=1)
    shows_assignee = instance["event"]["successor_id"] in rendered
    print(f"   [{'ok' if shows_assignee else 'FAIL'}] the board names the assignee "
          f"(an unassigned task and one parked on a\n        busy worker were "
          f"previously indistinguishable)")
    if not shows_assignee:
        failures.append("task board does not render the assignee")

    # CONSTRAINT 1 — no capacity vocabulary. The manager may infer capacity from
    # BEHAVIOUR (a fourth segment sits unstarted while three run), which is
    # available in every cell; it may not be TOLD.
    capacity_words = ["capacity", "declin", "refus", "full", "max_concurrent",
                      "at limit", "over-assign", "busy"]
    said = [w for w in capacity_words if w in rendered.lower()]
    print(f"   [{'ok' if not said else 'FAIL'}] no capacity vocabulary in the "
          f"board ({said or 'none'})")
    if said:
        failures.append(f"capacity vocabulary leaked into the board: {said}")

    # CONSTRAINT 2 — no coverage content. The assignee appears as an OPAQUE ID and
    # nothing about what it can do. This is the constraint that would invalidate
    # the study if it broke.
    assignee = next(w for w in instance["workers"]
                    if w["worker_id"] == instance["event"]["successor_id"])
    # The task's own text legitimately names its asset class; the question is
    # whether the ASSIGNMENT LINE adds any worker->capability linkage.
    assignment_line = next(
        line for line in rendered.splitlines() if "Assigned to:" in line)
    coverage_in_line = [c for c in assignee["irb_coverage"]
                        if c in assignment_line.lower()]
    caps_in_line = [c for c in assignee["card_capabilities"]
                    if c.lower() in assignment_line.lower()]
    print(f"   assignment line: {assignment_line.strip()!r}")
    print(f"   [{'ok' if not coverage_in_line and not caps_in_line else 'FAIL'}] "
          f"the assignment line carries an OPAQUE ID only — no coverage, no "
          f"capability")
    if coverage_in_line or caps_in_line:
        failures.append("assignment line carries capability/coverage content")

    # CONSTRAINT 3 — cell-independent. Assignment state is workflow state the
    # manager itself produces, so it cannot differ by channel cell by
    # construction. Asserted as: the line's SHAPE does not depend on anything in
    # the instance except the id.
    shape_ok = assignment_line.strip().startswith("Assigned to:")
    print(f"   [{'ok' if shape_ok else 'FAIL'}] the line is a fixed shape "
          f"('Assigned to: <id>'), so it is constant across cells by construction")
    if not shape_ok:
        failures.append("assignment line shape is not fixed")
    probe_task.assigned_agent_id = None

    # --- 10. THE WORKER IS UNSCRIPTED (E3a), asserted as ABSENCES -------------
    # These are the clauses whose presence made the S10 probe's 0% refusal rate a
    # tautology: we forbade declining, then reported that nobody declined. Their
    # removal is asserted rather than trusted, because a prompt edit is exactly
    # the kind of change that reappears quietly.
    print(f"\n10. worker is UNSCRIPTED (E3a) — asserted as absences:")
    banned = [
        ("always produce a number", "compels output"),
        ("no segment you may decline", "forbids declining"),
        ("there is no segment", "forbids declining"),
        ("otherwise use the standardised", "dictates the fallback"),
        ("use the IRB approach with", "dictates the method"),
        ("HOW TO CHOOSE AN APPROACH", "procedural heading"),
    ]
    prompts = {aid: cfg.system_prompt for aid, cfg in built["team"].items()}
    present = [(phrase, why, aid) for aid, text in prompts.items()
               for phrase, why in banned if phrase.lower() in text.lower()]
    for phrase, why, _aid in present:
        print(f"     STILL PRESENT: {phrase!r} ({why})")
    unscripted = not present
    print(f"   [{'ok' if unscripted else 'FAIL'}] none of the {len(banned)} "
          f"procedure clauses appears in any worker prompt")
    if present:
        failures.append(f"{len(present)} procedure clauses survive in worker prompts")

    # And the SITUATION must still be there — otherwise "unscripted" is satisfied
    # by an empty prompt, which is not the same thing at all.
    situation_ok = all(
        "APPROVED SCOPE" in text and "CALIBRATION" in text.upper()
        for text in prompts.values())
    print(f"   [{'ok' if situation_ok else 'FAIL'}] and the SITUATION survives "
          f"(approved scope + holdings) — unscripted is not\n        the same as "
          f"uninformed, and an empty prompt would satisfy the absence check alone")
    if not situation_ok:
        failures.append("worker prompts lost their situation")

    # The public default rate must be gone from task text (R1 item 3).
    seg_text = env.segment_task_description(instance["segments"][0])
    rate_gone = "default rate" not in seg_text.lower()
    print(f"   [{'ok' if rate_gone else 'FAIL'}] the public default-rate line is "
          f"GONE from task text — SA stays\n        computable from class+rating; "
          f"IRB needs the mapping only holders have")
    if not rate_gone:
        failures.append("public default rate still in task text")

    out = HERE / "records" / "S8"
    out.mkdir(parents=True, exist_ok=True)
    (out / "assembly_report.json").write_text(json.dumps({
        "instance_seed": SEED,
        "instance_sha256": built["instance_sha256"],
        "n_tasks": n_tasks,
        "index": index,
        "capacity_mapping": mapping,
        "horizon": built["horizon"],
        "cards": {aid: c.agent_description for aid, c in built["team"].items()},
        "roster_change_lines": lines,
        "n_private_values_searched": len(private_values),
        "n_public_strings_searched": len(public_strings),
        "leaks": leaks,
    }, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — DAG shape and count, capacity mapping arithmetic, "
          "no calibration leakage into public text, swap wired off the event block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
