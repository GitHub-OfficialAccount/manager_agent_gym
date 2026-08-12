"""L1 acceptance — the three load signals reach the manager, in every cell.

WHAT THIS STEP REPAIRS. In the scope run the manager assigned nine segments, the
engine refused 580 of the resulting starts because the assignees were at their
C=3 segment capacity, and the manager was told NOTHING. The board rendered that
work as `ready` from the first timestep to the last, so a manager reading its own
board could not distinguish work in progress from work that would never run. The
researcher's ruling (2026-08-08) is to give the manager all three signals —
truthful execution state, per-worker load, and refusal at the time it happens —
CONSTANT ACROSS EVERY CELL, as instrument repair rather than as a channel.

WHY CONSTANT MATTERS ENOUGH TO TEST. Load correlates with over-concentration,
which correlated with regret at r = 0.93 in the scope run. A load signal that
varied by cell would therefore be an uncontrolled channel sitting directly on the
dominant loss term, and every channel contrast would partly measure it.

WHAT EACH PART ESTABLISHES, and what it does not:

  PART A — a machinery episode (zero model calls, real engine, real cell
  environment). Establishes that the three signals appear in the manager's
  RENDERED CONTEXT at every timestep, and that a refusal that actually fires is
  actually rendered. Does NOT establish anything about a model's use of them.

  PART B — the same fixed synthetic state rendered under all six cell
  configurations, required BYTE-IDENTICAL. This is the constancy claim, and it is
  put this way on purpose: the six cells hold genuinely different rosters (U keeps
  the predecessor), so identical CONTENT across live episodes is not available and
  demanding it would be a check that cannot pass. Holding the state fixed and
  varying only the cell isolates the thing actually claimed — that no cell switch
  touches these three signals.

  PART C — the same three signals over each cell's live machinery episode,
  checked for identical FORM (block headers and row grammar). Content differs by
  roster, which is legitimate; a grammar difference would not be.

Run:  python3 -m experiments.worker_replacement.check_load_feedback
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from manager_agent_gym.core.common.run_trace import RunTraceRecorder
from manager_agent_gym.core.execution.engine import WorkflowExecutionEngine
from manager_agent_gym.core.manager_agent.interface import ManagerAgent
from manager_agent_gym.core.manager_agent.structured_manager import (
    ChainOfThoughtManagerAgent,
)
from manager_agent_gym.core.workflow_agents.stakeholder_agent import StakeholderAgent
from manager_agent_gym.schemas.core.base import EXECUTION_STATE_LABELS, TaskStatus
from manager_agent_gym.schemas.execution.manager_actions import (
    AssignmentPair,
    AssignTasksToAgentsAction,
    NoOpAction,
)
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from manager_agent_gym.schemas.unified_results import create_task_result
from manager_agent_gym.schemas.workflow_agents.stakeholder import StakeholderConfig

from . import finance_cells as cells
from . import finance_comparability as comp
from . import finance_env as env

HERE = Path(__file__).resolve().parent
SEED = 101

LOAD_HEADER = "### Worker Load (all workers currently on the roster)"
REFUSAL_HEADER = "### Assignments Refused Since Your Last Action"


# ---------------------------------------------------------------------------
# Zero-cost worker: the REAL capacity behaviour, no model call.
# ---------------------------------------------------------------------------
class _FreeWorker(env.CapacityBoundedAIAgent):
    """The production worker with only the model call removed.

    `can_handle_task` and `load_report` are INHERITED, deliberately — those are
    the two methods under test, and a stub that reimplemented them would test the
    stub. Only `execute_task` is replaced, so the capacity bookkeeping it performs
    is reproduced here rather than skipped.
    """

    async def execute_task(self, task: Any, resources: Any):
        # NO ALLOTMENT TO CONSUME (L14). The double used to mirror the production
        # agent by adding to `segment_task_ids`; that set is gone, and a double
        # that meters differently from production tests the double.
        return create_task_result(task_id=task.id, agent_id=self.agent_id,
                                  success=True, execution_time=0.01, resources=[])


class _RecordingManager(ManagerAgent):
    """Assigns every segment to ONE worker, then records what it was told.

    THE ALLOCATION IS DELIBERATELY THE FAILING ONE. Nine segments onto a single
    worker with C=3 is precisely the over-concentration the scope run produced, so
    the refusal signal is exercised by a real refusal rather than a simulated one.
    It is also fixed and cell-independent, which is what lets Part C compare the
    six cells at all.

    The rendered context is the REAL renderer (`_prepare_context`), not a
    reconstruction: the claim is about what a manager is shown, and a
    reimplementation here could pass while the shipped prompt omitted everything.
    """

    def __init__(self) -> None:
        super().__init__(agent_id=cells.MANAGER_AGENT_ID,
                         preferences=PreferenceWeights(preferences=[]))
        self.rendered: list[str] = []
        self.observations: list[Any] = []
        # task id -> the FIRST timestep at which it was seen completed. The zero-
        # cost worker bypasses `AIAgent.execute_task`, so no
        # `worker_execution_completed` events exist in a machinery bundle — and
        # without a completion record the L7 denominator's per-step terminality
        # cannot be distinguished from an episode-wide one, which is exactly the
        # input on which that defect could not fire.
        self.completed_at: dict[str, int] = {}
        self._renderer = ChainOfThoughtManagerAgent(
            preferences=PreferenceWeights(preferences=[]),
            model_name="none")
        self._assigned = False

    async def step(self, workflow, execution_state, stakeholder_profile,
                   current_timestep, running_tasks, completed_task_ids,
                   failed_task_ids, communication_service=None,
                   previous_reward: float = 0.0, done: bool = False):
        observation = await self.create_observation(
            workflow=workflow, execution_state=execution_state,
            stakeholder_profile=stakeholder_profile,
            current_timestep=current_timestep, running_tasks=running_tasks,
            completed_task_ids=completed_task_ids,
            failed_task_ids=failed_task_ids,
            communication_service=communication_service)
        self.observations.append(observation)
        self.rendered.append(self._renderer._prepare_context(observation))
        for task_id in completed_task_ids:
            self.completed_at.setdefault(str(task_id), current_timestep)

        if self._assigned:
            return NoOpAction(reasoning="already assigned", success=True,
                              result_summary="noop")
        self._assigned = True
        # Sorted ids, so the choice is identical in every cell.
        workers = sorted(
            a for a in workflow.agents
            if a not in {"stakeholder", cells.MANAGER_AGENT_ID}
        )
        target = workers[0]
        ordered = sorted(workflow.tasks.values(), key=lambda t: t.name)
        segments = [t for t in ordered
                    if env.CapacityBoundedAIAgent.is_metered(t)]
        # NON-SEGMENT WORK IS SPREAD, SEGMENTS ARE PILED. The upstream tasks must
        # actually complete or no segment ever becomes runnable and the refusal
        # path is never reached — the first version of this check assigned only
        # segments, saw zero refusals, and would have reported a PASS on an
        # episode where nothing ever ran. Non-segment work does not count against
        # the segment capacity, so spreading it does not soften the pile-up.
        others = [t for t in ordered
                  if not env.CapacityBoundedAIAgent.is_metered(t)]
        pairs = [AssignmentPair(task_id=t.id, agent_id=target) for t in segments]
        pairs += [AssignmentPair(task_id=t.id, agent_id=workers[i % len(workers)])
                  for i, t in enumerate(others)]
        return AssignTasksToAgentsAction(
            reasoning="pile every segment on one worker; spread the rest",
            assignments=pairs)

    def reset(self) -> None:
        self.rendered.clear()
        self.observations.clear()
        self._assigned = False


def run_machinery_episode(cell_name: str, timesteps: int = 10):
    """Drive the real engine over a real cell environment. Zero model calls."""
    built = cells.build_cell_environment(SEED, cell_name)
    workflow = built["workflow"]

    registry = built["registry"]
    registry.register_agent_class("ai", _FreeWorker)

    stakeholder = StakeholderAgent(config=StakeholderConfig(
        agent_id="stakeholder", agent_type="stakeholder",
        system_prompt="stakeholder for the L1 machinery episode",
        model_name="none",
        agent_description="stakeholder for the L1 machinery episode",
        agent_capabilities=["stakeholder"], name="S", role="Owner",
        initial_preferences=PreferenceWeights(preferences=[])))

    manager = _RecordingManager()
    engine = WorkflowExecutionEngine(
        workflow=workflow, agent_registry=registry, manager_agent=manager,
        stakeholder_agent=stakeholder, max_timesteps=timesteps,
        enable_timestep_logging=False, enable_final_metrics_logging=False,
        seed=1)

    # The trace is recorded so this episode yields a BUNDLE, which is what the
    # comparability assertion reads. Checking that assertion against a
    # hand-written events list would test the fixture, not the record the runner
    # actually writes.
    tracer = RunTraceRecorder(metadata={"study_step": "L1-machinery",
                                        "cell": cell_name, "instance_seed": SEED})

    async def _drive():
        with tracer.activate():
            for _ in range(timesteps):
                await engine.execute_timestep()
                engine.current_timestep += 1

    asyncio.run(_drive())
    # THE BUNDLE CARRIES ITS OWN INDEX, as a real run bundle does. A caller that
    # rebuilds the environment to get one gets a DIFFERENT build with different
    # task uuids, and every segment then reads as never-assigned — which is what
    # the L2a acceptance did on its first run, reporting 9/9 never_assigned for an
    # episode in which the manager assigned all nine.
    bundle = {"metadata": tracer.metadata, "events": tracer.events,
              "index": built["index"],
              "instance": built["instance"],
              "manifest": {"cell": cell_name, "instance_seed": SEED,
                           "successor_id": built["instance"]["event"]["successor_id"],
                           "predecessor_id":
                               built["instance"]["event"]["predecessor_id"],
                           "t_swap": built["instance"]["event"]["t_swap"]}}
    return manager, engine, bundle


# ---------------------------------------------------------------------------
# Form extraction: what a block looks like, with the content removed.
# ---------------------------------------------------------------------------
def block_of(rendered: str, header: str) -> str | None:
    """The block under `header`, up to the next `###` header."""
    if header not in rendered:
        return None
    tail = rendered.split(header, 1)[1]
    body = tail.split("\n###", 1)[0]
    return body.strip("\n")


# THE STRIP LIST, PUBLISHED (criterion (d.2)). Cell U legitimately holds a
# different roster, so a cross-cell comparison must substitute SOMETHING — and a
# checker stripped enough to stop flagging U is stripped enough to hide a real
# difference. Naming exactly what is removed is what lets a reader judge whether
# the remaining comparison is worth anything. This list is written into the
# record beside the verdict, not left in the source.
STRIP_LIST: list[tuple[str, str, str]] = [
    (r"\bw_[0-9a-f]+\b", "<worker>",
     "worker ids — cell U holds the predecessor, 0-4 the successor"),
    (r"'[^']*'", "'<task>'",
     "quoted task names — the refused task differs with the allocation"),
    (r"\d+", "<n>",
     "all integers — loads, counts and timesteps differ by episode"),
]


def grammar_of(block: str) -> list[str]:
    """A block's row GRAMMAR, per the published STRIP_LIST.

    Content legitimately differs across cells, so comparing content would fail for
    a reason that is not a defect. Grammar is the claim being made — that the
    manager is told the same KIND of thing in the same shape everywhere. What that
    claim is worth depends entirely on what was stripped, which is why the list is
    published rather than buried here.
    """
    rows = []
    for line in block.splitlines():
        row = line
        for pattern, replacement, _why in STRIP_LIST:
            row = re.sub(pattern, replacement, row)
        rows.append(row.strip())
    return sorted(rows)


def main() -> int:
    failures: list[str] = []
    print("L1 acceptance — load feedback reaches the manager, constant across "
          "cells\n")

    # ------------------------------------------------------------------ A ---
    print("A. machinery episode (cell 0, real engine, zero model calls)")
    manager, engine, _bundle = run_machinery_episode("0")
    engine_buffer = list(engine._pending_assignment_refusals)
    n_steps = len(manager.rendered)
    print(f"   {n_steps} manager decisions recorded")
    if n_steps < 3:
        failures.append(f"machinery episode produced only {n_steps} decisions")

    # (i) every timestep carries all three signals.
    missing_load = [i for i, r in enumerate(manager.rendered)
                    if block_of(r, LOAD_HEADER) is None]
    missing_refusal = [i for i, r in enumerate(manager.rendered)
                       if block_of(r, REFUSAL_HEADER) is None]
    print(f"   [{'ok' if not missing_load else 'FAIL'}] worker-load block present "
          f"at every timestep (missing at {missing_load or 'none'})")
    print(f"   [{'ok' if not missing_refusal else 'FAIL'}] refusal block present "
          f"at every timestep (missing at {missing_refusal or 'none'})")
    if missing_load:
        failures.append(f"load block missing at timesteps {missing_load}")
    if missing_refusal:
        failures.append(f"refusal block missing at timesteps {missing_refusal}")

    # PRESENCE IS NOT CONTENT (RR blocker). The two checks above test that the
    # HEADER is there. `AgentLoad.render()` returns "- <id>: (load unavailable)"
    # whenever `dimensions` is empty — a plausible-looking line, not an error — so
    # a live episode rendering that for every worker at every timestep would pass
    # both. That is the exact defect the fixture path was caught on, surviving in
    # the check next door on the path that matters more.
    #
    # RR's criterion said the rendered context must "CONTAIN" the signals;
    # "contain" is a presence predicate and a content property was meant. Same
    # name-versus-predicate family, in the criterion written to catch it.
    hollow_load = [i for i, r in enumerate(manager.rendered)
                   if "load unavailable" in (block_of(r, LOAD_HEADER) or "")]
    rostered = [len(o.agent_load) for o in manager.observations]
    dimensionless = [i for i, o in enumerate(manager.observations)
                     if any(not row.dimensions for row in o.agent_load)]
    print(f"   [{'ok' if not hollow_load else 'FAIL'}] and NO rendered load line "
          f"reads `load unavailable` (hollow at {hollow_load or 'none'})")
    print(f"   [{'ok' if not dimensionless else 'FAIL'}] every rostered worker "
          f"carries at least one capacity dimension at every timestep "
          f"(rows/timestep: {rostered})")
    if hollow_load:
        failures.append(f"load block rendered `load unavailable` at {hollow_load} "
                        f"— present but empty, which is the defect not the check")
    if dimensionless:
        failures.append(f"a worker had no capacity dimensions at {dimensionless}")

    # Execution state. Two claims, and they are separate: the board speaks the
    # execution vocabulary, and REFUSED is its own state rather than being
    # absorbed into `not started` (criterion (c)).
    board_states = set()
    stale_ready = []
    for i, r in enumerate(manager.rendered):
        for match in re.findall(r"Status: (.+)", r):
            board_states.add(match.strip())
        if re.search(r"Status: ready\b", r):
            stale_ready.append(i)
    known = set(EXECUTION_STATE_LABELS.values())
    unexplained = {s for s in board_states
                   if s not in known and not s.startswith("REFUSED")}
    truthful = bool(board_states) and not unexplained
    print(f"   [{'ok' if truthful else 'FAIL'}] board speaks execution state or "
          f"REFUSED only ({len(board_states)} distinct states; unexplained: "
          f"{sorted(unexplained) or 'none'})")
    print(f"   [{'ok' if not stale_ready else 'FAIL'}] the word `ready` no longer "
          f"appears as a task state (at {stale_ready or 'none'})")
    if not truthful:
        failures.append(f"board rendered unexplained states: {unexplained}")
    if stale_ready:
        failures.append(f"`Status: ready` still rendered at {stale_ready}")

    # (c) REFUSED IS PERSISTENT AND DISTINGUISHABLE. Both halves matter: a refused
    # task must be separable from never-assigned work, and it must STAY separable
    # — a point-in-time notification leaves a manager reading the board at t+5
    # exactly where it began.
    refused_states = {s for s in board_states if s.startswith("REFUSED")}
    refused_per_step = [
        len(re.findall(r"Status: REFUSED", r)) for r in manager.rendered]
    persisted = sum(1 for n in refused_per_step if n) >= 3
    distinguishable = bool(refused_states) and bool(
        board_states & {EXECUTION_STATE_LABELS[TaskStatus.READY]})
    print(f"   [{'ok' if refused_states else 'FAIL'}] REFUSED is its own board "
          f"state, not absorbed into `not started`")
    print(f"   [{'ok' if distinguishable else 'FAIL'}] and it coexists with plain "
          f"`not started`, so the two are distinguishable on one board")
    print(f"   [{'ok' if persisted else 'FAIL'}] and it PERSISTS: refused tasks on "
          f"the board per timestep = {refused_per_step}")
    if not refused_states:
        failures.append("no REFUSED board state ever rendered")
    if not distinguishable:
        failures.append("REFUSED and `not started` never appeared together, so "
                        "the distinction is untested")
    if not persisted:
        failures.append(f"refused state did not persist: {refused_per_step}")

    # (a) THE REASON IS COMPUTED AT THE SITE, so a refusal says why it happened
    # rather than leaving the manager to infer it from the load numbers.
    #
    # THIS ASSERTION WAS RETIRED AND REPLACED (L14). It read
    # `reasons_seen == {"concurrency", "allotment"}` and existed because the same
    # tasks were refused for CONCURRENCY early and for ALLOTMENT later, and a
    # signal derived from the load numbers alone would have called both the same
    # thing. With the allotment removed there is ONE cause, and asserting a
    # distinction between one thing and nothing is a check that cannot fail --
    # exactly the shape that retired property 2. So the DISTINCTION claim is gone
    # and the SITE-COMPUTED claim, which is the part that survives, is kept in a
    # form that can still break: every rendered refusal must name a cause the code
    # actually emits. A refusal rendered with no cause, or with a cause invented by
    # the renderer, fails this.
    KNOWN_CAUSES = {"concurrency": "concurrency limit"}
    refusal_lines = [line for o in manager.observations
                     for line in o.assignment_refusals]
    reasons_seen = {name for name, marker in KNOWN_CAUSES.items()
                    for line in refusal_lines if marker in line}
    uncaused = [line for line in refusal_lines
                if not any(m in line for m in KNOWN_CAUSES.values())]
    causes_named = bool(refusal_lines) and not uncaused
    print(f"   [{'ok' if causes_named else 'FAIL'}] every refusal names a cause the "
          f"code emits: {sorted(reasons_seen)} over {len(refusal_lines)} lines "
          f"({len(uncaused)} uncaused)")
    print(f"   NOTE, not a check: there is now ONE refusal cause. The "
          f"concurrency/allotment\n        distinction this assertion used to make "
          f"is RETIRED, not failing — see L14.")
    if not causes_named:
        failures.append(
            f"{len(uncaused)} refusal lines named no cause the code emits"
            if uncaused else "no refusal lines were produced to check causes on")

    # (i, second half) A REFUSAL THAT FIRED IS A REFUSAL THAT WAS RENDERED. This is
    # the part that would have caught the original defect: the run event existed,
    # the manager-visible signal did not.
    n_refusal_lines = sum(
        len(o.assignment_refusals) for o in manager.observations)
    fired = any("refused it" in (block_of(r, REFUSAL_HEADER) or "")
                for r in manager.rendered)
    print(f"   [{'ok' if fired else 'FAIL'}] a real refusal reached the manager "
          f"({n_refusal_lines} refusal lines across the episode)")
    if not fired:
        failures.append("no refusal was rendered despite 9 segments on one worker "
                        "at C=3")

    # (b) EVERY CAPACITY THE WORKER HAS IS REPORTED, WITH ITS RELEASE SEMANTICS.
    # The check is on the RENDERED text, not on the model fields: "true in the
    # code" is precisely what the criterion rules out.
    #
    # RESTATED (L14). It used to hardcode `{("concurrent tasks", True),
    # ("segment allotment", False)} <= dims_seen`, which named a dimension that no
    # longer exists. The replacement asks the PRODUCTION `load_report()` what
    # dimensions there are and requires every one of them to reach the manager.
    # That is falsifiable in the way that matters -- a dimension dropped from the
    # rendering breaks it -- and it survives a second capacity being ADDED without
    # another rewrite, which the hardcoded pair could not.
    expected_dims = {(d["name"], d["releases_on_completion"])
                     for d in _fixture_worker("w_probe", held=1)
                     .load_report()["dimensions"]}
    dims_seen = {(d.name, d.releases_on_completion)
                 for o in manager.observations for row in o.agent_load
                 for d in row.dimensions}
    all_dims = bool(expected_dims) and expected_dims <= dims_seen
    load_text = "\n".join(block_of(r, LOAD_HEADER) or "" for r in manager.rendered)
    exhausted_rendered = "[EXHAUSTED]" in load_text
    print(f"   [{'ok' if all_dims else 'FAIL'}] every capacity `load_report()` "
          f"produces reaches the manager: {sorted(dims_seen)}")
    print(f"   [{'ok' if exhausted_rendered else 'FAIL'}] a worker is observed "
          f"exhausting a capacity")
    if not all_dims:
        failures.append(f"capacity dimensions rendered were {sorted(dims_seen)}, "
                        f"missing {sorted(expected_dims - dims_seen)}")
    if not exhausted_rendered:
        failures.append("no worker ever rendered as exhausted")

    # THE OPPOSITE-RELEASE-SEMANTICS CHECK IS UNEXERCISED, NOT DELETED (L14).
    # The renderer still distinguishes the two, and the assertion below still
    # compares them -- but nothing in the environment now produces a dimension
    # that does NOT release on completion, so there is no instance to check it on.
    # Reported as UNINFORMATIVE rather than run, on the `MANIPULATION_UNREACHABLE`
    # pattern: a zero here means the STATE cannot arise, not that the machinery
    # failed. Kept because the moment a second capacity appears this is the check
    # that catches its semantics being rendered wrong, and rebuilding a deleted
    # renderer then is strictly worse than carrying an idle one now.
    non_releasing = sorted(n for n, rel in expected_dims if not rel)
    release_rendered = ("frees when a task finishes" in load_text
                        and "does NOT reset when a task finishes" in load_text)
    if non_releasing:
        print(f"   [{'ok' if release_rendered else 'FAIL'}] OPPOSITE release "
              f"semantics are in the RENDERED text, not just the model")
        if not release_rendered:
            failures.append("release semantics are not visible in the rendering")
    else:
        print(f"   [UNEXERCISED] opposite release semantics — every dimension "
              f"releases on completion,\n        so the contrast has no instance. "
              f"Machinery intact; would fire if one appeared.")

    # (d) NO CAPABILITY TEXT ANYWHERE IN THESE BLOCKS. A descriptor rendered beside
    # the id would reintroduce successor capability into the cells whose card is
    # deliberately stale — the second occurrence of the semantic-agent-id leak.
    # Checked against the ACTUAL card and capability strings of this instance,
    # rather than against a guessed vocabulary.
    #
    # THE CANDIDATE LIST IS BUILT FROM THE CARDS THE RUN ACTUALLY USES — the
    # rendered `agent_description` and `agent_capabilities`, plus the instance's
    # own coverage and card strings. The first version walked the instance dict
    # and collected `str` and `list` values; the fields are TUPLES, so it gathered
    # ZERO candidates and reported a clean pass against nothing. That is precisely
    # the failure the positive-control rule exists for, and it is why control 2
    # below asserts the candidate list is non-empty before trusting the null.
    built_for_leak = cells.build_cell_environment(SEED, "0")
    instance = built_for_leak["instance"]
    descriptors: set[str] = set()

    def _collect(value: Any) -> None:
        if isinstance(value, str):
            if len(value) > 3 and not value.startswith("w_"):
                descriptors.add(value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                _collect(item)

    for config in built_for_leak["team"].values():
        _collect(config.agent_description)
        _collect(config.agent_capabilities)
    for worker in instance["workers"]:
        for key, value in worker.items():
            if key != "private_pd_calibration":
                _collect(value)
    signal_text = "\n".join(
        (block_of(r, LOAD_HEADER) or "") + (block_of(r, REFUSAL_HEADER) or "")
        for r in manager.rendered)
    leaked = sorted(d for d in descriptors if d in signal_text)
    print(f"   [{'ok' if not leaked else 'FAIL'}] no worker descriptor appears in "
          f"either block ({len(descriptors)} candidate strings from the instance's "
          f"own workers; leaked: {leaked or 'none'})")
    if leaked:
        failures.append(f"capability/descriptor text leaked into a load or "
                        f"refusal line: {leaked}")

    # STALENESS, TESTED RATHER THAN ASSERTED. The first version of this line
    # printed `ok` unconditionally and tested nothing — a decorative check, which
    # is the failure mode this project keeps rediscovering. Two real ones:
    #
    #  (a) the engine's buffer is DRAINED at each decision. The same six segments
    #      are refused every timestep, so an undrained buffer grows monotonically:
    #      it would hold ~56 lines at the end instead of one timestep's worth.
    #  (b) the observation reflects an EMPTY buffer as empty. A signal that cannot
    #      go quiet cannot be trusted when it speaks.
    residual = len(engine_buffer)
    per_step = max(len(o.assignment_refusals) for o in manager.observations)
    drained = residual <= per_step
    print(f"   [{'ok' if drained else 'FAIL'}] the refusal buffer is DRAINED per "
          f"decision: {residual} left after the last timestep vs "
          f"{n_refusal_lines} raised across the episode (max {per_step} in any "
          f"one gap)")
    if not drained:
        failures.append(f"refusal buffer accumulated across timesteps "
                        f"({residual} residual)")

    manager.set_pending_assignment_refusals(None)
    quiet = asyncio.run(manager.create_observation(
        workflow=engine.workflow, execution_state=engine.execution_state,
        stakeholder_profile=engine.stakeholder_agent.public_profile,
        current_timestep=99, running_tasks={}, completed_task_ids=set(),
        failed_task_ids=set()))
    quiet_block = block_of(
        ChainOfThoughtManagerAgent(
            preferences=PreferenceWeights(preferences=[]),
            model_name="none")._prepare_context(quiet),
        REFUSAL_HEADER) or ""
    goes_quiet = "(none since your last action)" in quiet_block
    print(f"   [{'ok' if goes_quiet else 'FAIL'}] and it GOES QUIET when nothing "
          f"was refused, rather than repeating the last line")
    if not goes_quiet:
        failures.append(f"an empty refusal buffer rendered as: {quiet_block!r}")

    # ------------------------------------------------------------------ B ---
    print("\nB. constancy — one FIXED state rendered under all six cell configs")
    print("   (the claim is that no cell switch touches these blocks; live cells")
    print("    hold different rosters, so identical CONTENT is not the claim)")
    # THE OBSERVED REFUSAL, taken from Part A's real episode, so the fixture
    # cannot go on asserting wording the emitter has stopped producing.
    observed_refusal = next(
        (line for o in manager.observations for line in o.assignment_refusals),
        None)
    fixed_blocks: dict[str, tuple[str, str]] = {}
    for name in cells.CELLS:
        built = cells.build_cell_environment(SEED, name)
        obs = _fixed_observation(built, observed_refusal)
        rendered = ChainOfThoughtManagerAgent(
            preferences=PreferenceWeights(preferences=[]),
            model_name="none"
        )._prepare_context(obs)
        fixed_blocks[name] = (block_of(rendered, LOAD_HEADER) or "<ABSENT>",
                              block_of(rendered, REFUSAL_HEADER) or "<ABSENT>")

    distinct_load = {b[0] for b in fixed_blocks.values()}
    distinct_refusal = {b[1] for b in fixed_blocks.values()}
    absent = [n for n, b in fixed_blocks.items() if "<ABSENT>" in b]

    # POSITIVE CONTROL ON THE CONSTANCY CHECK ITSELF — the check that says
    # "identical across six cells" is satisfied trivially by six copies of
    # nothing, and this is exactly how it failed: the fixture supplied the
    # pre-criterion-(b) field names, pydantic dropped them, and the comparison ran
    # on "(load unavailable)" six times. It passed, and would have passed
    # identically had the load feature never been built. CONSTANT-BECAUSE-EMPTY
    # is not the claim, so the content is asserted BEFORE the comparison means
    # anything.
    sample_load = sorted(distinct_load)[0]
    sample_refusal = sorted(distinct_refusal)[0]
    substantive = ("load unavailable" not in sample_load
                   and "/" in sample_load
                   and "no refusal was observed" not in sample_refusal
                   and "refused it" in sample_refusal)
    print(f"   [{'ok' if substantive else 'FAIL'}] the compared blocks are "
          f"SUBSTANTIVE, not six copies of an empty rendering")
    print(f"        load:    {sample_load.splitlines()[0][:96]}")
    print(f"        refusal: {sample_refusal.splitlines()[0][:96]}")
    if not substantive:
        failures.append(f"constancy compared an empty/degenerate rendering: "
                        f"{sample_load!r} / {sample_refusal!r}")
    print(f"   [{'ok' if len(distinct_load) == 1 else 'FAIL'}] load block "
          f"byte-identical across all six cells ({len(distinct_load)} distinct)")
    print(f"   [{'ok' if len(distinct_refusal) == 1 else 'FAIL'}] refusal block "
          f"byte-identical across all six cells ({len(distinct_refusal)} distinct)")
    print(f"   [{'ok' if not absent else 'FAIL'}] present in every cell "
          f"(absent in {absent or 'none'})")
    if len(distinct_load) != 1:
        failures.append(f"load block differs by cell: {sorted(distinct_load)}")
    if len(distinct_refusal) != 1:
        failures.append(f"refusal block differs by cell: {sorted(distinct_refusal)}")
    if absent:
        failures.append(f"a signal was absent in cells {absent}")

    # ------------------------------------------------------------------ C ---
    print("\nC. live machinery episode per cell — identical FORM, content free "
          "to differ")
    per_cell: dict[str, dict[str, Any]] = {}
    grammars: dict[str, tuple[str, str]] = {}
    bundles: dict[str, dict[str, Any]] = {}
    for name in cells.CELLS:
        run, _engine, bundle = run_machinery_episode(name)
        bundles[name] = bundle
        load_rows: set[str] = set()
        refusal_rows: set[str] = set()
        for rendered in run.rendered:
            load_block = block_of(rendered, LOAD_HEADER)
            refusal_block = block_of(rendered, REFUSAL_HEADER)
            if load_block is None or refusal_block is None:
                failures.append(f"cell {name}: a signal block was absent")
                continue
            load_rows.update(grammar_of(load_block))
            refusal_rows.update(grammar_of(refusal_block))
        grammars[name] = (json.dumps(sorted(load_rows)),
                          json.dumps(sorted(refusal_rows)))
        per_cell[name] = {
            "n_decisions": len(run.rendered),
            "n_refusal_lines": sum(len(o.assignment_refusals)
                                   for o in run.observations),
            "max_load_seen": max((d.held for o in run.observations
                                  for row in o.agent_load
                                  for d in row.dimensions), default=0),
            "load_grammar": sorted(load_rows),
            "refusal_grammar": sorted(refusal_rows),
        }
        print(f"   {name}: {per_cell[name]['n_decisions']} decisions, "
              f"{per_cell[name]['n_refusal_lines']} refusal lines, "
              f"max load {per_cell[name]['max_load_seen']}")

    distinct_grammar = {g for g in grammars.values()}
    same_grammar = len(distinct_grammar) == 1
    print(f"   [{'ok' if same_grammar else 'FAIL'}] identical row grammar across "
          f"all six live cells ({len(distinct_grammar)} distinct)")
    if not same_grammar:
        by_grammar: dict[tuple[str, str], list[str]] = {}
        for name, g in grammars.items():
            by_grammar.setdefault(g, []).append(name)
        for g, names in by_grammar.items():
            print(f"     {names}: {g[0][:120]}")
        failures.append("live cells rendered different signal grammars")

    # Every cell must actually EXERCISE the refusal path, or "identical" is a
    # statement about six empty blocks.
    silent = [n for n, d in per_cell.items() if d["n_refusal_lines"] == 0]
    print(f"   [{'ok' if not silent else 'FAIL'}] every cell exercised a real "
          f"refusal (silent in {silent or 'none'})")
    if silent:
        failures.append(f"cells {silent} produced no refusal at all")

    # ------------------------------------------------------------------ D ---
    # (iii) The comparability module's assertion, driven against the bundles the
    # six episodes actually produced — not a hand-written fixture, which would
    # test the fixture. Both directions are checked: a check that only ever
    # passes is not a check, and the negative is the one that would have caught
    # the original defect (a run with no manager-visible signal at all).
    print("\nD. comparability assertion over the six machinery bundles")
    verdict = comp.assert_load_feedback_present(bundles)
    print(f"   [{'ok' if verdict['comparable'] else 'FAIL'}] comparable="
          f"{verdict['comparable']}, problems={verdict['problems'] or 'none'}")
    if not verdict["comparable"]:
        failures.append(f"comparability rejected real bundles: "
                        f"{verdict['problems']}")

    blinded = {name: {"events": [e for e in b["events"]
                                 if e.get("event_type") != comp.LOAD_FEEDBACK_EVENT]}
               for name, b in bundles.items()}
    blind_verdict = comp.assert_load_feedback_present(blinded)
    caught = not blind_verdict["comparable"]
    print(f"   [{'ok' if caught else 'FAIL'}] and it REJECTS a bundle whose "
          f"load-feedback record is absent (the pre-L1 condition)")
    if not caught:
        failures.append("comparability accepted a bundle with no load signal")

    one_blind = dict(bundles)
    one_blind["0"] = blinded["0"]
    mixed_verdict = comp.assert_load_feedback_present(one_blind)
    caught_one = not mixed_verdict["comparable"]
    print(f"   [{'ok' if caught_one else 'FAIL'}] and it rejects a set where only "
          f"ONE cell ran blind — the case that would look like a channel effect")
    if not caught_one:
        failures.append("comparability accepted a set with one blinded cell")

    # ------------------------------------------------------------------ E ---
    # (e) SEGMENT IDENTITY IS DECLARED, NOT INFERRED FROM THE DISPLAY NAME, and
    # the engine's notion of "segment" is the SCORER's. One name, two predicates
    # is what let a manager remediation be refused thirteen times for being called
    # the wrong thing.
    print("\nE. the allotment predicate (criterion (e))")
    built0 = cells.build_cell_environment(SEED, "0")
    workflow0, index0 = built0["workflow"], built0["index"]
    # Compared as STRINGS: the index stores task ids as `str`, the workflow as
    # `UUID`. The first version compared them raw, got a symmetric difference of
    # 18 over two 9-element sets, and reported a defect that was entirely its own.
    engine_set = {str(t.id) for t in workflow0.tasks.values()
                  if env.CapacityBoundedAIAgent.is_metered(t)}
    scorer_set = {str(v) for v in index0["segment_task_ids"].values()}
    reconciled = engine_set == scorer_set
    print(f"   [{'ok' if reconciled else 'FAIL'}] the metered set and the scored "
          f"set are the SAME SET ({len(engine_set)} vs {len(scorer_set)}; "
          f"symmetric difference {len(engine_set ^ scorer_set)})")
    if not reconciled:
        failures.append(f"engine meters {len(engine_set)} tasks, scorer scores "
                        f"{len(scorer_set)}; difference {engine_set ^ scorer_set}")

    # THE NATURAL EXPERIMENT, as a regression test. Both names, neither metered,
    # because neither is a scored segment. Before this change the first was
    # charged to allotment and refused forever and the second was free.
    from manager_agent_gym.schemas.core.tasks import Task as _Task
    remediations = [
        ("prefix-matching (was refused 13× in cell0_seed23)",
         "Risk-weighted assets — seg_08 standardised recalculation"),
        ("non-matching (completed in cell0_seed36)",
         "Recompute RWA: seg_02 (bank IRB) and seg_07 (mdb IRB)"),
    ]
    name_free = True
    for label, name in remediations:
        created = _Task(name=name, description="a manager-created remediation")
        metered = env.CapacityBoundedAIAgent.is_metered(created)
        print(f"   [{'ok' if not metered else 'FAIL'}] manager-created, {label}: "
              f"metered={metered}")
        if metered:
            name_free = False
    if not name_free:
        failures.append("a manager-created task is still metered by its name")
    print("   NOTE, not a check: manager-created work is now charged NOTHING, so "
          "a manager\n        can obtain labour outside the allotment the oracle "
          "assumes. Deliberate —\n        the alternative shrinks a worker's "
          "feasible set below the oracle's model.\n        It is the analysis's "
          "business, and it is visible in the record.")

    # ------------------------------------------------------------------ F ---
    # POSITIVE CONTROLS. New methodology rule: a query asserting a NULL must first
    # demonstrate a HIT on a case known to be positive. Most of the checks above
    # are null-shaped — "no unexplained state", "no descriptor leaked", "no cell
    # differs" — and a null-shaped check with a mistyped field name fails to EMPTY
    # and reports a clean pass. Each one is shown FIRING on a deliberately broken
    # input before its green above is worth anything.
    print("\nF. positive controls — every null-shaped check, shown FIRING")
    controls: list[tuple[str, bool]] = []

    # 1. board-state check vs a task rendered with the old vocabulary.
    broken_board = "  Status: ready\n  Status: done"
    seen = {m.strip() for m in re.findall(r"Status: (.+)", broken_board)}
    fires = bool({s for s in seen
                  if s not in known and not s.startswith("REFUSED")}) or bool(
        re.search(r"Status: ready\b", broken_board))
    controls.append(("board-state check fires on `Status: ready`", fires))

    # 2. descriptor-leak check vs a load line with a capability glued on.
    controls.append((f"descriptor-leak check has a NON-EMPTY candidate list "
                     f"({len(descriptors)} strings) — the first version had 0 "
                     f"and passed against nothing", bool(descriptors)))
    if descriptors:
        planted = sorted(descriptors)[0]
        fires = bool([d for d in descriptors if d in f"- w_x: 1/3 ({planted})"])
        controls.append(("descriptor-leak check fires on a planted capability",
                         fires))

    # 3. constancy check vs a genuinely differing block.
    fires = len({fixed_blocks["0"][0], fixed_blocks["0"][0] + " EXTRA"}) != 1
    controls.append(("constancy check fires when one cell's block differs", fires))

    # 4. grammar check vs a row the strip list does NOT normalise away. If the
    #    strip list were over-broad this control would fail, which is exactly the
    #    stripper trap criterion (d.2) names.
    a = grammar_of("- w_aaaaaa: segment allotment 3/3 (x) [EXHAUSTED]")
    b = grammar_of("- w_bbbbbb: segment allotment 3/3 (x) — plus a capability")
    controls.append(("grammar check still distinguishes a real difference "
                     "after stripping", a != b))

    # 5. release-semantics check vs a rendering that omits them.
    # THE PREDICATE IS LIVE; THE CHECK IT GUARDS IS CURRENTLY UNEXERCISED (L14) --
    # no dimension fails to release on completion, so nothing in the live path
    # evaluates it. Kept and LABELLED as such: a green here says the predicate
    # still discriminates, NOT that anything was checked with it this run.
    fires = not ("frees when a task finishes" in "- w_x: 3/3"
                 and "does NOT reset when a task finishes" in "- w_x: 3/3")
    controls.append(("release-semantics PREDICATE fires on a bare `3/3` "
                     "(predicate only — its live check is UNEXERCISED)", fires))

    # 6. metered-set reconciliation vs a mismatched pair.
    controls.append(("reconciliation check fires on a mismatched set",
                     {1, 2} != {1, 2, 3}))

    # 7. THE BLOCKER'S OWN CONTROL. The live-path content check must fire on the
    # very rendering that used to pass — a load row with no dimensions. Without
    # this the fix is another green that has never been shown capable of red.
    from manager_agent_gym.schemas.execution.manager import AgentLoad as _AL
    hollow = _AL(agent_id="w_x", available=True, dimensions=[]).render()
    controls.append((f"live-path content check fires on {hollow!r}",
                     "load unavailable" in hollow))
    controls.append(("and the real rendering does NOT trip it (other direction)",
                     "load unavailable" not in (
                         block_of(manager.rendered[-1], LOAD_HEADER) or "x")))

    for label, fired_ok in controls:
        print(f"   [{'ok' if fired_ok else 'FAIL'}] {label}")
        if not fired_ok:
            failures.append(f"POSITIVE CONTROL FAILED — {label}; the "
                            f"corresponding green above is worthless")

    out = HERE / "records" / "L1"
    out.mkdir(parents=True, exist_ok=True)
    (out / "load_feedback_acceptance.json").write_text(json.dumps({
        "seed": SEED,
        "board_states_rendered": sorted(board_states),
        "execution_state_labels": {k.value: v
                                   for k, v in EXECUTION_STATE_LABELS.items()},
        "strip_list": [{"pattern": pat, "replacement": rep, "why": why}
                       for pat, rep, why in STRIP_LIST],
        "positive_controls": [{"control": lab, "fired": ok} for lab, ok in controls],
        "metered_set_equals_scored_set": reconciled,
        "fixed_state_load_block": sorted(distinct_load)[0],
        "fixed_state_refusal_block": sorted(distinct_refusal)[0],
        "per_cell": per_cell,
        "comparability_verdict": verdict,
        "failures": failures,
    }, indent=2, sort_keys=True) + "\n")
    (out / "rendered_cell0_timestep0.txt").write_text(manager.rendered[0])

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — execution state, per-worker load and refusal reach the "
          "manager's rendered context at every timestep, in identical form in "
          "every cell, and a real refusal is observed in all six")
    return 0


def _fixture_worker(agent_id: str, held: int):
    """A real production worker holding `held` segments. No model call.

    The point is that `load_report()` is the PRODUCTION method — the fixture
    cannot describe a shape the code no longer has, which is how the previous
    fixture came to assert something about a schema that had been replaced.
    """
    template = cells.build_cell_environment(SEED, "0")["team"]
    config = next(iter(template.values())).model_copy(
        update={"agent_id": agent_id})
    from manager_agent_gym.core.workflow_agents.tool_factory import ToolFactory
    worker = _FreeWorker(config, tools=ToolFactory.create_ai_tools())
    # `held` used to preload the segment allotment. With the allotment removed the
    # only capacity is concurrency, so it preloads THAT -- otherwise the helper
    # would silently ignore its own argument and every caller would build the same
    # worker while believing it had varied one.
    worker.current_task_ids = {uuid4() for _ in range(held)}
    return worker


def _fixture_refusal(observed: str | None = None) -> str:
    """A refusal line the ENGINE actually emitted, with the ids neutralised.

    Taken from the live machinery episode rather than transcribed: a literal in
    this file records what the emitter said on the day it was written, and the
    previous one went on asserting the pre-L1 wording after the emitter changed.
    """
    if not observed:
        return "(no refusal was observed to build a fixture from)"
    line = re.sub(r"\bw_[0-9a-f]+\b", "w_aaaaaa", observed)
    return re.sub(r"'[^']*'", "'fixture_task'", line)


def _fixed_observation(built: dict[str, Any], refusal: str | None = None):
    """One synthetic state, identical in every cell, for the constancy check.

    Synthetic ON PURPOSE. The live cells hold different rosters, so a live
    comparison cannot separate "the cell changed the signal" from "the cell has
    different workers". Holding the state fixed leaves the cell configuration as
    the only thing varying, which is the claim.
    """
    from manager_agent_gym.schemas.execution.manager import (
        AgentLoad, ManagerObservation)
    from manager_agent_gym.schemas.workflow_agents.stakeholder import (
        StakeholderPublicProfile)

    workflow = built["workflow"]
    return ManagerObservation(
        workflow_summary="(held constant)",
        timestep=3, workflow_id=workflow.id, execution_state="running",
        task_status_counts={s.value: 0 for s in TaskStatus},
        workflow_progress=0.5,
        # BUILT FROM A REAL `load_report()`, NOT HAND-WRITTEN (LS review, finding
        # 1). The first version supplied `held`/`capacity`/`unit` — the fields the
        # schema had BEFORE criterion (b) split load into dimensions. Pydantic
        # dropped all three, `dimensions` stayed empty, and the constancy check
        # compared "(load unavailable)" to itself six times. **It was constant
        # because it was EMPTY, and would have passed identically if the load
        # feature had never been built.** The schema is now `extra='forbid'`, so
        # that exact fixture raises rather than degrading — but the real defence is
        # sourcing the fixture from the production method, so it cannot describe a
        # shape the code no longer has.
        agent_load=[AgentLoad(**_fixture_worker(agent_id, held).load_report())
                    for agent_id, held in (("w_aaaaaa", 3), ("w_bbbbbb", 1))],
        # Likewise generated by the production code path rather than transcribed:
        # the hand-written literal still carried the PRE-L1 wording ("is at
        # capacity (3/3 segment tasks)") long after the emitter stopped producing
        # it, so the check compared the six cells against a string none of them
        # could ever have rendered.
        assignment_refusals=[_fixture_refusal(refusal)],
        stakeholder_profile=StakeholderPublicProfile(
            display_name="S", role="Owner",
            preference_summary="(held constant)"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
