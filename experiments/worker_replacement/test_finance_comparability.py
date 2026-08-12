"""Acceptance — comparability assertions across cells.

The rule this file exists to enforce: a cell comparison is meaningful only if the
cells differ in the ONE thing the design varies. Instrument settings that differ
by cell are the failure class, and the action space is now one of them (LS ruling,
spec E5, after S8 added AssignTasksToAgentsAction).

  1. POSITIVE: two bundles from the same configuration compare as comparable.
  2. NEGATIVES, each with a DISTINCT named cause — a differing action space, a
     differing model, and an UNRECORDED setting. The third matters most: a bundle
     that does not record a setting must not silently match one that does.
  3. The negatives are constructed by MUTATING a real bundle, so they exercise the
     same code path a real cell would.

Run:  python3 -m experiments.worker_replacement.test_finance_comparability
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from . import finance_comparability as cmp

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records" / "S8"


def main() -> int:
    failures: list[str] = []
    print("S8 — cross-cell comparability assertions\n")

    # The source must RECORD the pinned settings, or every case degenerates into
    # the unrecorded-setting branch and the other checks never run. Bundles
    # written before `manager_action_types` existed are skipped for that reason,
    # and the skip is reported rather than silent.
    candidates = [RECORDS / "run_seed101.json",
                  RECORDS / "dry_run_seed101.json",
                  RECORDS / "run_seed101_attempt5_INCOMPLETE.json"]
    source = None
    for path in candidates:
        if not path.exists():
            continue
        if cmp.setting_of(cmp.load_bundle(path), "manager_action_types") == "__ABSENT__":
            print(f"   skipped {path.name}: predates `manager_action_types`")
            continue
        source = path
        break
    if source is None:
        print("RESULT: FAIL — no bundle records the pinned settings")
        return 1
    print(f"cases built by MUTATING a real bundle: {source.name}")
    base = cmp.load_bundle(source)
    print(f"   its action space ({len(cmp.setting_of(base, 'manager_action_types'))} "
          f"actions): {cmp.setting_of(base, 'manager_action_types')}")

    # --- 1. positive ---------------------------------------------------------
    verdict = cmp.compare_settings({"U": base, "T": copy.deepcopy(base)})
    ok = verdict["comparable"]
    print(f"\n1. two cells from the same configuration:")
    print(f"   settings checked: {verdict['settings_checked']}")
    print(f"   [{'ok' if ok else 'FAIL'}] comparable")
    if not ok:
        print(f"     disagreements: {verdict['disagreements']}")
        print(f"     unrecorded: {verdict['unrecorded_settings']}")
        failures.append("identical configurations did not compare as comparable")

    # --- 2. negatives --------------------------------------------------------
    print("\n2. negatives — each must be REJECTED with a distinct named cause:")

    # (a) action space differs — the setting LS pinned by name.
    mutated = copy.deepcopy(base)
    types = list(mutated["manifest"]["manager_action_types"])
    mutated["manifest"]["manager_action_types"] = [
        t for t in types if t != "assign_tasks_to_agents"]
    v_action = cmp.assert_action_space_identical({"U": base, "T": mutated})
    a_ok = not v_action["comparable"] and v_action["disagreements"]
    print(f"   [{'ok' if a_ok else 'FAIL'}] ACTION SPACE differs -> rejected")
    if a_ok:
        d = v_action["disagreements"][0]
        only_in_u = set(d["by_cell"]["U"]) - set(d["by_cell"]["T"])
        print(f"       names the setting ({d['setting']}) and what differs: "
              f"U has {sorted(only_in_u)} and T does not")
    else:
        failures.append("a differing action space was not rejected")

    # (b) model differs.
    mutated_model = copy.deepcopy(base)
    mutated_model["manifest"]["worker_model"] = "openrouter/some/other-model"
    v_model = cmp.compare_settings({"U": base, "T": mutated_model})
    m_ok = not v_model["comparable"] and any(
        d["setting"] == "worker_model" for d in v_model["disagreements"])
    print(f"   [{'ok' if m_ok else 'FAIL'}] WORKER MODEL differs -> rejected")
    if not m_ok:
        failures.append("a differing worker model was not rejected")

    # (c) UNRECORDED setting. The one that would slip through a naive check: a
    # bundle that never recorded the action space must not be declared comparable
    # to one that did, because "absent" is not evidence of "the same".
    stripped = copy.deepcopy(base)
    stripped["manifest"].pop("manager_action_types", None)
    v_absent = cmp.compare_settings({"U": base, "T": stripped})
    ab_ok = not v_absent["comparable"] and v_absent["unrecorded_settings"]
    print(f"   [{'ok' if ab_ok else 'FAIL'}] setting UNRECORDED in one cell -> "
          f"rejected (absent is not evidence of 'same')")
    if ab_ok:
        print(f"       unrecorded: {v_absent['unrecorded_settings']}")
    else:
        failures.append("an unrecorded setting was treated as comparable")

    # (d) ordering must NOT matter — a reordered action list is the SAME space,
    # and rejecting it would make the check fire on noise.
    reordered = copy.deepcopy(base)
    if reordered["manifest"].get("manager_action_types"):
        reordered["manifest"]["manager_action_types"] = list(
            reversed(reordered["manifest"]["manager_action_types"]))
    v_order = cmp.assert_action_space_identical({"U": base, "T": reordered})
    o_ok = v_order["comparable"]
    print(f"   [{'ok' if o_ok else 'FAIL'}] REORDERED action list -> still "
          f"comparable (the check compares content, not JSON order)")
    if not o_ok:
        failures.append("reordering the action list broke comparability")

    # Distinct causes, so the rejections are not one catch-all.
    causes = {
        json.dumps(v_action["disagreements"], sort_keys=True, default=str),
        json.dumps(v_model["disagreements"], sort_keys=True, default=str),
        json.dumps(v_absent["unrecorded_settings"], sort_keys=True, default=str),
    }
    print(f"   [{'ok' if len(causes) == 3 else 'FAIL'}] {len(causes)} DISTINCT "
          f"rejection payloads — no catch-all masquerading as three checks")
    if len(causes) != 3:
        failures.append("rejection causes are not discriminating")

    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / "comparability_cases.json").write_text(json.dumps({
        "source_bundle": source.name,
        "pinned_settings": cmp.PINNED_SETTINGS,
        "positive": verdict,
        "negative_action_space": v_action,
        "negative_worker_model": v_model,
        "negative_unrecorded": v_absent,
        "ordering_insensitive": v_order,
    }, indent=2, sort_keys=True, default=str) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — identical configurations compare; differing action "
          "space, differing model and an unrecorded setting are each rejected "
          "with a distinct named cause; list ordering does not matter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
