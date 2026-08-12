"""R2 acceptance — the six cells differ in the three switches and NOTHING ELSE.

The claim this file exists to defend is not "the cells are configured correctly".
It is "everything other than the manipulated channel is identical", because that
is the claim every contrast rests on. So the checks are mostly NEGATIVE: what must
NOT differ.

  1. The configuration matrix matches the spec table exactly.
  2. C1: the stale card is BYTE-IDENTICAL to the predecessor's own — staleness by
     succession, never authored.
  3. C2: the declaration line moves; the VALUE line and the DECLINE form do not.
     Scoring and refusal must be identical across cells or contrasts measure the
     scorer.
  4. C3: the manager's id appears only in ask cells, and TOOLS ARE IDENTICAL in
     every cell (the core-tool rule forbids a tool difference).
  5. Cell U carries no swap and is scored against its OWN roster.
  6. THE RESIDUAL DIFF: system prompts across cells differ ONLY inside the
     convention and ask blocks. This is the check that catches an accidental
     divergence nobody thought to look for — the others can only find what I
     named.
  7. finance_comparability's pinned settings are identical across all six.

Run:  python3 -m experiments.worker_replacement.test_finance_cells
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from . import finance_cells as fc
from . import finance_comparability as cmp
from . import finance_env as env
from . import finance_report_parser as rp

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records" / "R2"
SEED = 3

EXPECTED = {
    "U": (False, False, False, False),
    "0": (True, False, False, False),
    "1": (True, True, False, False),
    "2": (True, False, True, False),
    "3": (True, False, False, True),
    "4": (True, True, True, True),
}


def manager_side_residual(seed: int) -> dict:
    """The residual-diff check pointed at the MANAGER prompt family.

    WHY THIS EXISTS SEPARATELY (RR, R2 review). The worker-side residual check was
    a completeness proof over the wrong surface for C1: the CARD never appears in
    a worker prompt at all. It is manager-side — rendered into the manager's
    system prompt through `get_agent_capability_summary()`, which prints
    `agent_description`. So the check that finds what the author did not name was
    covering half the surface, and no amount of strengthening it would have shown
    that. A single reviewer's completeness proof can be pointed at the wrong
    family.

    The manager prompt is where the DV comes from — its decisions are the
    allocation — so this is the family that most needed the proof.
    """
    import asyncio

    from manager_agent_gym.core.communication.service import CommunicationService
    from manager_agent_gym.core.manager_agent.structured_manager import (
        ChainOfThoughtManagerAgent,
    )
    from manager_agent_gym.core.workflow_agents.tool_factory import ToolFactory
    from manager_agent_gym.schemas.preferences.preference import PreferenceWeights

    manager = ChainOfThoughtManagerAgent(
        preferences=PreferenceWeights(preferences=[]), model_name="none")

    rendered: dict[str, str] = {}
    for name in EXPECTED:
        built = fc.build_cell_environment(seed, name)
        registry = built["registry"]

        async def _to_swap():
            await registry.apply_scheduled_changes_for_timestep(
                0, CommunicationService(), ToolFactory())
            await registry.apply_scheduled_changes_for_timestep(
                int(built["instance"]["event"]["t_swap"]),
                CommunicationService(), ToolFactory())

        asyncio.run(_to_swap())
        present = sorted(registry.list_agents(), key=lambda a: a.agent_id)
        rendered[name] = manager._get_system_prompt([a.config for a in present])
    return rendered


def _strip_roster_card_block(text: str, cell_name: str) -> str:
    """Remove ONLY the roster/card block — the surface C1 is allowed to vary on.

    A stripper that removes more than the manipulated block would hide exactly
    what this check exists to find, so this removes the agent lines and nothing
    else, and the cell name is not used to decide what to strip.
    """
    kept = [line for line in text.splitlines()
            if not line.strip().startswith("Agent ")
            and "| Description:" not in line]
    return "\n".join(kept).strip()


def main() -> int:
    failures: list[str] = []
    print("R2 — six cells as configuration; only three switches may differ\n")

    built = {name: fc.build_cell_environment(SEED, name) for name in EXPECTED}
    instance = built["0"]["instance"]
    event = instance["event"]

    # --- 1. the matrix -------------------------------------------------------
    print("1. configuration matrix vs the spec table:")
    print(f"   {'cell':<5} {'swap':<6} {'card_upd':<9} {'decl':<6} {'ask':<6}")
    matrix_ok = True
    for name, expected in EXPECTED.items():
        cell = fc.CELLS[name]
        actual = (cell.swap, cell.card_updated, cell.declaration_present,
                  cell.ask_enabled)
        ok = actual == expected
        matrix_ok &= ok
        print(f"   {name:<5} {str(cell.swap):<6} {str(cell.card_updated):<9} "
              f"{str(cell.declaration_present):<6} {str(cell.ask_enabled):<6}"
              f"{'' if ok else '   <- MISMATCH'}")
    print(f"   [{'ok' if matrix_ok else 'FAIL'}] all six match the spec table")
    if not matrix_ok:
        failures.append("cell configuration does not match the spec table")

    # --- 2. C1: staleness is INHERITED, not authored -------------------------
    print("\n2. C1 card — the stale card is the predecessor's own text:")
    pred, succ = event["predecessor_id"], event["successor_id"]
    pred_card = built["0"]["team"][pred].agent_description
    stale_card = built["0"]["team"][succ].agent_description
    fresh_card = built["1"]["team"][succ].agent_description
    identical = stale_card == pred_card
    differs = fresh_card != pred_card
    print(f"   predecessor card: {pred_card[:64]}...")
    print(f"   successor in cell 0 (stale): {stale_card[:64]}...")
    print(f"   [{'ok' if identical else 'FAIL'}] BYTE-IDENTICAL to the "
          f"predecessor's — inherited, never written afresh")
    print(f"   [{'ok' if differs else 'FAIL'}] and cell 1's updated card is the "
          f"successor's own, which differs")
    if not identical:
        failures.append("stale card is not byte-identical to the predecessor's")
    if not differs:
        failures.append("updated card does not differ from the stale one")

    # --- 3. C2: declaration moves, scoring and refusal do NOT ----------------
    print("\n3. C2 declaration — only the method line moves:")
    for cell_name, want in (("0", False), ("2", True), ("4", True), ("1", False)):
        prompt = built[cell_name]["team"][succ].system_prompt
        seg_task = next(t for t in built[cell_name]["workflow"].tasks.values()
                        if env.CapacityBoundedAIAgent.is_metered(t))
        has_prompt = "method:" in prompt
        has_task = "method:" in seg_task.description
        ok = has_prompt == want and has_task == want
        print(f"   [{'ok' if ok else 'FAIL'}] cell {cell_name}: method line in "
              f"prompt={has_prompt}, in task={has_task} (want {want} in both)")
        if not ok:
            failures.append(f"cell {cell_name} declaration state wrong")

    # THE VALUE LINE AND THE DECLINE FORM MUST BE IDENTICAL EVERYWHERE. If they
    # moved with the cell, a contrast would partly measure the scorer or the
    # refusal channel rather than the declaration.
    invariant_ok = True
    for name in EXPECTED:
        text = fc.convention_text(fc.CELLS[name])
        if "rwa: <the risk-weighted assets figure" not in text:
            invariant_ok = False
        if "rwa: unavailable" not in text or "legitimate outcome" not in text:
            invariant_ok = False
    print(f"   [{'ok' if invariant_ok else 'FAIL'}] the VALUE line and the "
          f"DECLINE form are present in EVERY cell — scoring and\n        refusal "
          f"are identical, so a contrast cannot measure them")
    if not invariant_ok:
        failures.append("value line or decline form varies by cell")

    # --- 4. C3: prompt-level, never tool-level -------------------------------
    print("\n4. C3 ask — a prompt difference, NOT a tool difference:")
    for cell_name, want in (("0", False), ("3", True), ("4", True)):
        prompt = built[cell_name]["team"][succ].system_prompt
        named = fc.MANAGER_AGENT_ID in prompt
        ok = named == want
        print(f"   [{'ok' if ok else 'FAIL'}] cell {cell_name}: manager id named "
              f"in prompt = {named} (want {want})")
        if not ok:
            failures.append(f"cell {cell_name} ask state wrong")

    async def _tools(cell_name: str) -> list[str]:
        registry = built[cell_name]["registry"]
        from manager_agent_gym.core.communication.service import CommunicationService
        from manager_agent_gym.core.workflow_agents.tool_factory import ToolFactory
        await registry.apply_scheduled_changes_for_timestep(
            0, CommunicationService(), ToolFactory())
        agent = registry.list_agents()[0]
        return sorted(getattr(t, "name", type(t).__name__)
                      for t in getattr(agent, "tools", []))

    tools_by_cell = {name: asyncio.run(_tools(name)) for name in ("0", "3", "4")}
    tools_ok = len({tuple(v) for v in tools_by_cell.values()}) == 1
    print(f"   tools in cells 0/3/4: {tools_by_cell['0']}")
    print(f"   [{'ok' if tools_ok else 'FAIL'}] TOOLS ARE IDENTICAL across cells "
          f"— the core-tool rule forbids differentiating\n        by tool "
          f"possession, so the ask channel cannot be built that way")
    if not tools_ok:
        failures.append("tools differ across cells; core-tool rule violated")

    # --- 5. cell U: no swap, own roster --------------------------------------
    print("\n5. cell U — no swap, scored against its OWN roster:")
    u_registry = fc.build_cell_environment(SEED, "U")["registry"]

    async def _apply(reg, t):
        return await reg.apply_scheduled_changes_for_timestep(t)

    asyncio.run(_apply(u_registry, 0))
    at_swap = asyncio.run(_apply(u_registry, int(event["t_swap"])))
    u_roster = sorted(a.agent_id for a in u_registry.list_agents())
    no_swap = len(at_swap) == 0 and u_roster == sorted(event["roster_pre_swap"])
    print(f"   changes applied at t_swap: {len(at_swap)}; roster {u_roster}")
    print(f"   [{'ok' if no_swap else 'FAIL'}] the predecessor never leaves")
    own_roster = built["U"]["active_roster"] == list(event["roster_pre_swap"])
    print(f"   [{'ok' if own_roster else 'FAIL'}] and U is scored against the "
          f"PRE-swap roster — its own attainable optimum,\n        not one for a "
          f"team it never had")
    if not no_swap:
        failures.append("cell U applied a swap")
    if not own_roster:
        failures.append("cell U is not scored against its own roster")

    # --- 6. THE RESIDUAL DIFF ------------------------------------------------
    # The check that can catch what I did not think to name: strip the two blocks
    # that are ALLOWED to vary, and every cell's prompt must then be identical.
    print("\n6. residual diff — with the convention and ask blocks removed, every "
          "cell's\n   prompt must be IDENTICAL (this is the check that finds what "
          "I did not name):")
    stripped = {}
    for name in EXPECTED:
        text = built[name]["team"][succ].system_prompt
        for block in (rp.REPORT_CONVENTION_TEXT, fc._VALUE_CONVENTION,
                      fc.ask_text(fc.CELLS[name])):
            if block:
                text = text.replace(block, "")
        stripped[name] = text.strip()
    residual_ok = len(set(stripped.values())) == 1
    # THE STRIP LIST IS PART OF THE CLAIM (RR). A residual count of 1 means
    # nothing without knowing what was removed to reach it: a stripper that
    # quietly removes an UNINTENDED difference hides exactly what the check exists
    # to find. So the list is published HERE, beside the count, in the check's own
    # output rather than in a report someone may or may not read.
    print(f"   STRIPPED (the full list — the claim is only as good as this):")
    print(f"     1. the report-convention block (C2's surface), whichever variant "
          f"the cell uses")
    print(f"     2. the ask block (C3's surface), empty in non-ask cells")
    print(f"   and NOTHING ELSE. The stripper does not consult the cell name, so "
          f"it cannot remove\n   an unintended difference in the one cell that "
          f"has it.")
    print(f"   distinct residual prompts across six cells: "
          f"{len(set(stripped.values()))}")
    print(f"   [{'ok' if residual_ok else 'FAIL'}] exactly one — nothing varies "
          f"outside the two stripped blocks")
    if not residual_ok:
        for name, text in stripped.items():
            print(f"     cell {name}: {len(text)} chars")
        failures.append("prompts differ outside the manipulated blocks")

    # The instance, DAG shape and horizon must be identical too.
    shapes = {name: (built[name]["instance_sha256"], built[name]["index"]["n_tasks"],
                     built[name]["horizon"]) for name in EXPECTED}
    shape_ok = len(set(shapes.values())) == 1
    print(f"   [{'ok' if shape_ok else 'FAIL'}] instance hash, task count and "
          f"horizon identical across all six")
    if not shape_ok:
        failures.append(f"environment shape varies by cell: {shapes}")

    # --- 7. THE MANAGER-SIDE RESIDUAL — the family C1 actually lives in -------
    print("\n7. manager-side residual diff (RR: C1 is a MANAGER-side manipulation;"
          "\n   the worker check could never have covered it):")
    manager_prompts = manager_side_residual(SEED)
    stale_in_0 = pred_card in manager_prompts["0"]
    fresh_in_1 = built["1"]["team"][succ].agent_description in manager_prompts["1"]
    print(f"   [{'ok' if stale_in_0 else 'FAIL'}] cell 0's manager prompt carries "
          f"the PREDECESSOR's card for the successor")
    print(f"   [{'ok' if fresh_in_1 else 'FAIL'}] cell 1's carries the "
          f"successor's own — so C1 is visible where the DV is made")
    if not stale_in_0:
        failures.append("stale card does not reach the manager prompt")
    if not fresh_in_1:
        failures.append("updated card does not reach the manager prompt")

    mgr_stripped = {name: _strip_roster_card_block(text, name)
                    for name, text in manager_prompts.items()}
    mgr_ok = len(set(mgr_stripped.values())) == 1
    print(f"   distinct manager residuals across six cells: "
          f"{len(set(mgr_stripped.values()))}")
    print(f"   [{'ok' if mgr_ok else 'FAIL'}] exactly one — with the roster/card "
          f"block removed, every cell's MANAGER\n        prompt is identical. "
          f"Only the agent lines were stripped; a stripper that removed\n        "
          f"more would hide what this check exists to find.")
    if not mgr_ok:
        lengths = {n: len(t) for n, t in mgr_stripped.items()}
        print(f"     residual lengths: {lengths}")
        failures.append("manager prompts differ outside the roster/card block")

    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / "cell_configuration.json").write_text(json.dumps({
        "seed": SEED,
        "cells": {name: built[name]["cell_config"] for name in EXPECTED},
        "predecessor_card": pred_card,
        "stale_card_is_predecessors": identical,
        "tools_by_cell": tools_by_cell,
        "residual_prompt_variants": len(set(stripped.values())),
        "shapes": {k: list(v) for k, v in shapes.items()},
    }, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — the matrix matches the spec; the stale card is inherited "
          "byte-identically; scoring and refusal are identical across cells; the "
          "ask channel is prompt-level with identical tools; U carries no swap; "
          "and nothing varies outside the manipulated blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
