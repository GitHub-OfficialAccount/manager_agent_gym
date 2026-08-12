"""S2 acceptance — the roster-arrival render into the manager's observation.

Asserts three things, the third of which is the property the assignment called out
explicitly:

  1. A remove+add scheduled at timestep t reaches the RENDERED manager prompt at t,
     carrying both agent ids and the change verb.
  2. The rendered block carries NO reason text. This matters: the registry's
     human-readable strings embed `change.reason`, which in real timelines is a
     capability description ("Forensic collection & processing"). Rendering it would
     leak through the arrival channel what the CARD channel is supposed to control
     (HARNESS_SPEC_v2 §5), so the observation path is fed the structured record.
  3. NO-EVENT INVISIBILITY: with no roster change, the block is omitted ENTIRELY --
     not rendered empty -- so an unswapped prompt is byte-identical to the same prompt
     built with no roster field at all.

Run:  python3 -m experiments.worker_replacement.test_roster_render
Exit code 0 = pass.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

from manager_agent_gym import AgentRegistry
from manager_agent_gym.core.manager_agent.structured_manager import (
    ChainOfThoughtManagerAgent,
)
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.execution.manager import ManagerObservation
from manager_agent_gym.schemas.execution.state import ExecutionState
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig
from manager_agent_gym.schemas.workflow_agents.stakeholder import (
    StakeholderPublicProfile,
)

PREDECESSOR = "capital_quant_alpha"
SUCCESSOR = "capital_quant_beta"
SWAP_TIMESTEP = 3
# The reason strings deliberately look like real timeline entries -- i.e. they are
# capability descriptions. The test asserts they do NOT reach the prompt.
REMOVE_REASON = "Rotated off the engagement; IRB corporate approval lapses"
ADD_REASON = "Retail IRB model ownership; concept-review specialist"


def _config(agent_id: str) -> AIAgentConfig:
    return AIAgentConfig(
        agent_id=agent_id,
        agent_type="ai",
        system_prompt="Capital quant.",
        agent_description="Computes regulatory capital.",
        agent_capabilities=["Computes RWA"],
    )


def _profile() -> StakeholderPublicProfile:
    return StakeholderPublicProfile(
        display_name="Stakeholder",
        role="balanced",
        preference_summary="quality",
    )


# ONE workflow shared by every build in this test. A fresh Workflow gets a fresh
# UUID, which lands in the rendered prompt -- so building a new one per call would
# make two identical-input prompts differ on the id alone and the byte-identity
# assertion below would be measuring my fixture instead of the roster field.
_WORKFLOW = Workflow(name="S2 fixture", workflow_goal="render check", owner_id=uuid4())


async def _prompt_for(roster_changes: list[str], timestep: int) -> str:
    """Build the manager's rendered context for a given roster-change list."""
    manager = ChainOfThoughtManagerAgent(preferences=PreferenceWeights(preferences=[]))
    workflow = _WORKFLOW
    observation: ManagerObservation = await manager.create_observation(
        workflow=workflow,
        execution_state=ExecutionState.RUNNING,
        current_timestep=timestep,
        running_tasks={},
        completed_task_ids=set(),
        failed_task_ids=set(),
        communication_service=None,
        stakeholder_profile=_profile(),
        roster_changes=roster_changes,
    )
    assert observation.roster_changes == roster_changes, (
        f"observation did not carry the roster changes: {observation.roster_changes!r}"
    )
    return manager._prepare_context(observation)


async def _prompt_via_engine_setter(roster_changes: list[str], timestep: int) -> str:
    """The path the ENGINE actually uses: setter before step, no step() kwarg.

    Exercised explicitly because the plumbing is a setter rather than a step()
    parameter -- adding a keyword to the public abstract step() broke 27 existing
    tests whose manager subclasses declare explicit signatures.
    """
    manager = ChainOfThoughtManagerAgent(preferences=PreferenceWeights(preferences=[]))
    manager.set_pending_roster_changes(roster_changes)
    observation = await manager.create_observation(
        workflow=_WORKFLOW,
        execution_state=ExecutionState.RUNNING,
        current_timestep=timestep,
        running_tasks={},
        completed_task_ids=set(),
        failed_task_ids=set(),
        communication_service=None,
        stakeholder_profile=_profile(),
    )
    assert observation.roster_changes == roster_changes, (
        f"setter path did not reach the observation: {observation.roster_changes!r}"
    )
    return manager._prepare_context(observation)


async def _prompt_for_no_roster_arg(timestep: int) -> str:
    """Same build, but `roster_changes` never passed — the pre-change call shape."""
    manager = ChainOfThoughtManagerAgent(preferences=PreferenceWeights(preferences=[]))
    observation = await manager.create_observation(
        workflow=_WORKFLOW,
        execution_state=ExecutionState.RUNNING,
        current_timestep=timestep,
        running_tasks={},
        completed_task_ids=set(),
        failed_task_ids=set(),
        communication_service=None,
        stakeholder_profile=_profile(),
    )
    assert observation.roster_changes == [], "default must be empty, not None"
    return manager._prepare_context(observation)


def _engine_expression(registry: AgentRegistry) -> list[str]:
    """Exactly what the engine calls each timestep — the same public accessor.

    Calls the real method rather than recomputing its logic: a test that
    reimplements the code path verifies its own copy, not the subject.
    """
    return registry.roster_change_lines()


async def _swapped_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register_ai_agent(_config(PREDECESSOR), [])
    registry.schedule_agent_remove(SWAP_TIMESTEP, PREDECESSOR, REMOVE_REASON)
    registry.schedule_agent_add(SWAP_TIMESTEP, _config(SUCCESSOR), ADD_REASON)
    return registry


async def _apply_swap() -> list[str]:
    """Schedule remove+add at SWAP_TIMESTEP and return what the engine would pass."""
    registry = await _swapped_registry()

    strings = await registry.apply_scheduled_changes_for_timestep(SWAP_TIMESTEP)
    # The pre-existing ExecutionResult/callback path must still receive its strings.
    assert strings, "the string path lost its content — that path must stay intact"
    assert any(REMOVE_REASON in s for s in strings), (
        "the string path should still carry reasons; only the OBSERVATION path is minimal"
    )
    return _engine_expression(registry)


async def main() -> int:
    failures: list[str] = []
    print("S2 — roster-arrival render acceptance\n")

    # --- 1. the swap reaches the rendered prompt -----------------------------
    roster_changes = await _apply_swap()
    print(f"registry structured record -> {roster_changes}")
    swapped = await _prompt_for(roster_changes, SWAP_TIMESTEP)

    checks = [
        ("block header present", "Roster Changes" in swapped),
        (f"timestep {SWAP_TIMESTEP} named", f"timestep {SWAP_TIMESTEP}" in swapped),
        ("predecessor id present", PREDECESSOR in swapped),
        ("successor id present", SUCCESSOR in swapped),
        ("verb 'removed' present", "removed" in swapped),
        ("verb 'added' present", "added" in swapped),
    ]
    for label, ok in checks:
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
        if not ok:
            failures.append(label)

    # --- 2. no reason text leaks --------------------------------------------
    print("\nleak check — reason text must NOT reach the prompt:")
    for label, reason in (("remove reason", REMOVE_REASON), ("add reason", ADD_REASON)):
        leaked = reason in swapped
        print(f"  [{'FAIL' if leaked else 'ok'}] {label} absent")
        if leaked:
            failures.append(f"{label} leaked into the prompt")
    # Any distinctive capability word from the reasons must be absent too.
    for word in ("approval lapses", "specialist", "model ownership"):
        leaked = word in swapped
        print(f"  [{'FAIL' if leaked else 'ok'}] capability phrase {word!r} absent")
        if leaked:
            failures.append(f"capability phrase {word!r} leaked")

    print("\nrendered block, verbatim:")
    start = swapped.find("### Roster Changes")
    print("    " + swapped[start:swapped.find("###", start + 3)].strip().replace(
        "\n", "\n    "))

    # --- 2b. the ENGINE's actual path (setter, not a step() kwarg) -----------
    print("\nengine path — set_pending_roster_changes before the observation:")
    via_setter = await _prompt_via_engine_setter(roster_changes, SWAP_TIMESTEP)
    setter_ok = PREDECESSOR in via_setter and SUCCESSOR in via_setter
    print(f"  [{'ok' if setter_ok else 'FAIL'}] setter path renders both ids")
    if not setter_ok:
        failures.append("engine setter path did not render")

    # --- 2c. GHOST-REPEAT: a quiet timestep AFTER an eventful one ------------
    # The case the first version of this test could not catch, because it applied
    # only the swap timestep and every prompt build took an explicit list -- so the
    # registry->engine path was never exercised on a quiet timestep following an
    # eventful one. Found by LS review: the reset sat AFTER the method's early
    # return, so quiet timesteps kept the previous record and the one-off arrival
    # became a permanent banner with a falsely advancing timestep label.
    print("\nghost-repeat — quiet timesteps after the swap, through the registry:")
    registry = await _swapped_registry()
    await registry.apply_scheduled_changes_for_timestep(SWAP_TIMESTEP)
    at_swap = _engine_expression(registry)
    print(f"  t={SWAP_TIMESTEP}   engine expression -> {at_swap}")
    if not at_swap:
        failures.append("swap timestep produced no roster changes")

    for quiet in (SWAP_TIMESTEP + 1, SWAP_TIMESTEP + 2):
        await registry.apply_scheduled_changes_for_timestep(quiet)
        after = _engine_expression(registry)
        empty = after == []
        print(f"  t={quiet}   engine expression -> {after}  "
              f"[{'ok' if empty else 'FAIL'}]")
        if not empty:
            failures.append(f"roster record ghost-repeated at quiet timestep {quiet}")
        quiet_prompt = await _prompt_via_engine_setter(after, quiet)
        no_block = "Roster Changes" not in quiet_prompt
        print(f"           rendered prompt carries no roster block "
              f"[{'ok' if no_block else 'FAIL'}]")
        if not no_block:
            failures.append(f"roster block rendered at quiet timestep {quiet}")

    # --- 2d. canonical ordering, independent of scenario append order --------
    # RR review: rendered lines followed scenario append order and nothing asserted
    # it, so block text was generator-dependent and not byte-comparable across
    # cells. Scheduling ADD FIRST here — the reverse of _swapped_registry — must
    # still render removals first.
    print("\ncanonical ordering — add scheduled BEFORE remove:")
    reversed_registry = AgentRegistry()
    reversed_registry.register_ai_agent(_config(PREDECESSOR), [])
    reversed_registry.schedule_agent_add(SWAP_TIMESTEP, _config(SUCCESSOR), ADD_REASON)
    reversed_registry.schedule_agent_remove(SWAP_TIMESTEP, PREDECESSOR, REMOVE_REASON)
    await reversed_registry.apply_scheduled_changes_for_timestep(SWAP_TIMESTEP)
    # The accessor itself must canonicalize — the test does not sort anything.
    canonical = _engine_expression(reversed_registry)
    print(f"  scheduled order  -> add first, then remove")
    print(f"  accessor returns -> {canonical}")
    matches = canonical == ["removed " + PREDECESSOR, "added " + SUCCESSOR]
    print(f"  [{'ok' if matches else 'FAIL'}] removals first, then additions, then id")
    if not matches:
        failures.append("canonical ordering not achieved")

    # --- 2e. ordering with the `replaced` verb present -----------------------
    # RR round 2: with three verbs the order is NOT "removals, then additions, then
    # replacements" -- adds and replaces share the second sort bucket and interleave
    # by id. Asserted so the documented behaviour and the real behaviour cannot
    # drift apart.
    print("\nordering with `replaced` present — adds and replaces interleave by id:")
    mixed = AgentRegistry()
    mixed._last_applied_changes = [
        ("added", "z_agent"),
        ("replaced", "a_agent"),
        ("removed", "m_agent"),
        ("added", "b_agent"),
    ]
    got = mixed.roster_change_lines()
    expected = ["removed m_agent", "replaced a_agent", "added b_agent", "added z_agent"]
    print(f"  -> {got}")
    if got == expected:
        print("  [ok] removals first; adds and replaces interleaved by id, as documented")
    else:
        print(f"  [FAIL] expected {expected}")
        failures.append("ordering does not match the documented total key")

    # --- 3. no-event invisibility -------------------------------------------
    print("\nno-event invisibility:")
    unswapped = await _prompt_for([], SWAP_TIMESTEP)
    absent = "Roster Changes" not in unswapped
    print(f"  [{'ok' if absent else 'FAIL'}] block omitted entirely when nothing changed")
    if not absent:
        failures.append("empty roster block was rendered")

    # The strongest form of the property: byte-identity between an unswapped prompt
    # and one built with the roster argument omitted entirely (default None), on the
    # same workflow. If the empty block left any residue -- a blank line, a header --
    # these would differ.
    baseline = await _prompt_for_no_roster_arg(SWAP_TIMESTEP)
    identical = unswapped == baseline
    print(f"  [{'ok' if identical else 'FAIL'}] unswapped prompt byte-identical to baseline "
          f"({len(unswapped)} chars)")
    if not identical:
        failures.append("unswapped prompt not byte-identical to baseline")

    print()
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  {f}")
        return 1
    print("RESULT: PASS — swap rendered with ids+verb+timestep; no reason text leaked; "
          "block absent with no event")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
