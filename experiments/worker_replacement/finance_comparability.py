"""Comparability assertions across run bundles — INSTRUMENT SETTINGS, not outcomes.

A cell comparison is only meaningful if the two cells differ in the ONE thing the
design varies and in nothing else. This module asserts the "nothing else" half by
reading it off the bundles rather than trusting that the runner was configured the
same way twice.

The first such setting is the MANAGER'S ACTION SPACE (LS ruling, spec E5). S8 added
`AssignTasksToAgentsAction` to the manager's action set, because the stock set
forces one assignment per timestep — and that dribble does not merely slow an
episode down, it CONFOUNDS: allocation order becomes harness-imposed
serialization, so a timing difference between cells would partly measure the
dribble rather than information use, and it breaks symmetry with the scripted
baseline, which produces a whole mapping at once.

An action set that differed by cell would therefore be an instrument setting
varying with the condition — the failure class this project already has a name
for. So it is asserted, and the assertion names WHICH cells disagree rather than
returning a bare boolean: "not comparable" that cannot say where is not
actionable.

S9 composes these; nothing here is re-implemented there.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Instrument settings that MUST be identical across every cell of a comparison,
# including the untreated cell and the gate pair. Each maps to its path in a run
# bundle's manifest.
# CONCURRENCY IS REPORTED, NOT PINNED (LS ruling). It VARIES across this
# exploratory run — the first four scope episodes at N=4, the remaining fourteen
# at N=2 — which the pinned rule would otherwise forbid. Pinning it would make
# every cross-batch comparison "not comparable" and hide the real, accepted
# limitation behind a blanket refusal. So it is surfaced in the output with its
# wall-clock and completion, and checked post hoc for a content effect.
# For any POWERED study it moves into PINNED_SETTINGS and is constant, no
# exceptions.
REPORTED_SETTINGS: dict[str, str] = {
    "concurrency": "episodes running in parallel when this one ran",
}

PINNED_SETTINGS: dict[str, str] = {
    "manager_action_types": "the manager's action space",
    "manager_model": "the manager's model",
    "worker_model": "the workers' model",
    "capacity_mapping": "the per-worker capacity mapping",
    "horizon": "the episode horizon",
    "n_tasks": "the task count",
}


# Settings whose VALUE IS A SET, so list order carries no meaning. Named
# explicitly rather than treating every list as unordered: for these the order is
# an artifact of how the runner happened to enumerate them, and a check that fired
# on reordering would fire on noise — which is how a check earns the reputation
# that gets it switched off. Any setting NOT listed here is compared with its
# order intact.
UNORDERED_SETTINGS: frozenset[str] = frozenset({"manager_action_types"})


def canonical(value: Any, unordered: bool = False) -> str:
    """Stable string form for comparison. Sorts elements when the value is a set."""
    if unordered and isinstance(value, list):
        return json.dumps(sorted(json.dumps(v, sort_keys=True, default=str)
                                 for v in value))
    return json.dumps(value, sort_keys=True, default=str)


def load_bundle(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def setting_of(bundle: dict[str, Any], key: str) -> Any:
    """Read one pinned setting. Missing is DISTINCT from any value it could hold.

    A bundle that does not record a setting cannot be shown comparable to one that
    does, so the sentinel is returned rather than a default — defaulting would let
    an unrecorded setting silently match a recorded one.
    """
    manifest = bundle.get("manifest", {})
    return manifest.get(key, "__ABSENT__")


def compare_settings(
    bundles: dict[str, dict[str, Any]],
    settings: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Check every pinned setting across labelled bundles.

    `bundles` maps a cell label to a loaded bundle. Returns a verdict plus, for
    each disagreeing setting, the value each cell held — so a failure says which
    cells differ and how, not merely that they do.
    """
    settings = settings or PINNED_SETTINGS
    disagreements: list[dict[str, Any]] = []

    for key, description in settings.items():
        by_cell = {label: setting_of(bundle, key)
                   for label, bundle in bundles.items()}
        # Compare canonically: lists and dicts must match by content, not by the
        # accident of ordering or key order in JSON.
        unordered = key in UNORDERED_SETTINGS
        canonical_by_cell = {label: canonical(value, unordered)
                             for label, value in by_cell.items()}
        if len(set(canonical_by_cell.values())) > 1:
            disagreements.append({
                "setting": key,
                "description": description,
                "by_cell": by_cell,
            })

    absent = [
        {"setting": key, "cells": [l for l, b in bundles.items()
                                   if setting_of(b, key) == "__ABSENT__"]}
        for key in settings
        if any(setting_of(b, key) == "__ABSENT__" for b in bundles.values())
    ]

    return {
        "comparable": not disagreements and not absent,
        "n_cells": len(bundles),
        "cells": sorted(bundles),
        "disagreements": disagreements,
        "unrecorded_settings": absent,
        "settings_checked": sorted(settings),
    }


# The four study-wide logging records (STUDY1_LOGGING_AND_ORDERING.md §2). A
# bundle missing any of them CANNOT ENTER ANALYSIS: each exists because a specific
# claim is unrecoverable without it, so its absence does not degrade the analysis,
# it silently changes which claims the analysis is entitled to make. Same
# absent-is-not-same rule as the pinned settings.
from . import finance_logging as flog  # noqa: E402  (kept beside its use)


def assert_records_present(
    bundles: dict[str, dict[str, Any]],
    manager_id: str = "structured_manager",
) -> dict[str, Any]:
    """Every bundle must carry all four logging records, plus the deferral log.

    "Present" means the extractor RUNS and returns its record — not that the
    record is non-empty. A run with no refines legitimately has an empty refine
    record; a run whose bundle cannot produce one at all is a different thing, and
    conflating them would reject good runs and admit unanalysable ones.
    """
    required = list(flog.REQUIRED_RECORDS) + ["deferrals", "denominator",
                                              "unstaffed_segments"]
    missing: list[dict[str, Any]] = []
    per_cell: dict[str, dict[str, Any]] = {}

    for label, bundle in bundles.items():
        try:
            records = flog.all_records(bundle, manager_id=manager_id)
        except Exception as exc:  # a bundle that cannot yield records at all
            missing.append({"cell": label, "record": "(all)",
                            "reason": f"{type(exc).__name__}: {exc}"})
            per_cell[label] = {"error": str(exc)}
            continue
        present = {}
        for name in required:
            record = records.get(name)
            present[name] = record is not None
            if record is None:
                missing.append({"cell": label, "record": name,
                                "reason": "extractor produced no record"})
        # PRESENT IS NOT ENOUGH. The extractors are defensive by design, so a
        # bundle stripped of its index still yields records — empty ones. A cell
        # whose segment denominator is zero has nothing to analyse, and calling it
        # analysable because seven dicts came back would be the emptiest possible
        # form of a passing check. Caught by this module's own acceptance, which
        # printed analysable=True beside segment_denominator=0.
        denominator = records["denominator"]["segment_denominator"]
        if denominator <= 0:
            missing.append({
                "cell": label, "record": "denominator",
                "reason": ("segment denominator is 0 — the bundle carries no "
                           "analysable task set (index or task board missing)"),
            })
        per_cell[label] = {
            "present": present,
            "n_channel_pulls": records["channel_pulls"]["n_pulls"],
            "n_refines": records["refine_events"]["n_refines"],
            "refines_attributable": records["refine_events"]["attributable"],
            "n_messages": records["message_visibility"]["n_messages"],
            "n_rendered": records["message_visibility"]["n_rendered"],
            "n_replies": records["reply_addressing"]["n_replies"],
            "n_deferrals": records["deferrals"]["n_deferrals"],
            "n_unstaffed": records["unstaffed_segments"]["n_unstaffed"],
            "segment_denominator": records["denominator"]["segment_denominator"],
            "n_tasks_created_during_run": records["denominator"][
                "n_created_during_run"],
        }

    return {
        "analysable": not missing,
        "required_records": required,
        "missing": missing,
        "per_cell": per_cell,
    }


def report_concurrency(bundles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Surface concurrency per cell WITH wall-clock and completion.

    Reported rather than pinned because it genuinely varies in this run. The
    point of reporting it beside completion is that a CONTENT effect would show
    up here — if the high-concurrency cells completed systematically less, the
    accepted limitation would stop being acceptable.
    """
    from datetime import datetime

    rows = {}
    for label, bundle in bundles.items():
        manifest = bundle.get("manifest", {})
        started, finished = manifest.get("started_at"), manifest.get("finished_at")
        minutes = None
        if started and finished:
            minutes = (datetime.fromisoformat(finished)
                       - datetime.fromisoformat(started)).total_seconds() / 60
        rows[label] = {
            "concurrency": manifest.get("concurrency", "__ABSENT__"),
            "wall_clock_min": minutes,
            "completions": len(bundle.get("completions", [])),
            "n_tasks": manifest.get("n_tasks"),
        }
    values = {r["concurrency"] for r in rows.values()}
    return {
        "per_cell": rows,
        "concurrency_values_seen": sorted(str(v) for v in values),
        "concurrency_varies": len(values) > 1,
        "limitation": ("concurrency varies across cells in this exploratory run; "
                       "recorded rather than erased. Constant across cells for any "
                       "powered study, no exceptions."),
    }


def assert_action_space_identical(bundles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The action-space check on its own, since it is the one LS pinned by name."""
    return compare_settings(bundles, {"manager_action_types": PINNED_SETTINGS[
        "manager_action_types"]})


# The three load signals (L1), asserted per bundle rather than trusted. These are
# INSTRUMENT REPAIR, not a channel: the researcher's ruling is that the manager
# sees execution state, per-worker load and refusals in EVERY cell, so a bundle in
# which they are absent — or a set of bundles in which they differ by cell — is
# not comparable with one in which they are present.
#
# WHY THIS IS ASSERTED FROM THE BUNDLE AND NOT FROM THE CODE. A unit test proves
# the path can carry the signals; it says nothing about whether a particular
# episode did. Load correlates with over-concentration, which correlated with
# regret at r = 0.93 in the scope run, so a cell that quietly ran without the
# signal would have an uncontrolled advantage sitting directly on the dominant
# loss term — and the difference would look like a channel effect.
#
# WHAT IT CANNOT SEE: the record is the OBSERVATION's contents. That the
# observation is then rendered into the manager's prompt is a separate claim,
# established by `check_load_feedback.py` against the real renderer.
LOAD_FEEDBACK_EVENT = "manager_load_feedback"

# The board's execution vocabulary. `ready` is absent BY DESIGN — it is the word
# that asserted work would run when it could not, and its reappearance in a
# bundle's rendered states means the repair was reverted or bypassed.
BOARD_STATES_FORBIDDEN: frozenset[str] = frozenset({"ready"})


def assert_load_feedback_present(
    bundles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Every bundle carries the three load signals, at every manager decision.

    Returns per-cell detail plus a verdict, and names WHICH cell and WHICH
    timestep failed — a bare boolean here would be unactionable in the same way
    the action-space check would have been.
    """
    problems: list[dict[str, Any]] = []
    per_cell: dict[str, dict[str, Any]] = {}

    for label, bundle in bundles.items():
        events = [e for e in bundle.get("events", [])
                  if e.get("event_type") == LOAD_FEEDBACK_EVENT]
        payloads = [(e.get("payload") or {}) for e in events]

        if not events:
            problems.append({
                "cell": label, "problem": "no load-feedback record at all",
                "consequence": ("the manager may have run blind to load; this "
                                "bundle is not comparable with one that did not"),
            })
            per_cell[label] = {"n_decisions": 0}
            continue

        # A DECISION WITH NO LOAD ROWS IS THE FAILURE, NOT A QUIET TIMESTEP.
        # Refusals legitimately number zero — nothing was refused. Load rows do
        # not: there is always a roster, so an empty load list means the signal
        # did not reach that decision. Distinguishing the two is the whole point;
        # summing them would let a blind episode hide behind a quiet one.
        blind = [p.get("timestep") for p in payloads if not p.get("n_load_rows")]
        if blind:
            problems.append({
                "cell": label, "problem": "decisions with no load rows",
                "timesteps": blind,
            })

        stale_board = sorted({
            state for p in payloads for state in (p.get("board_states") or [])
            if state in BOARD_STATES_FORBIDDEN
        })
        # The raw TaskStatus vocabulary is what this event records, so `ready`
        # here is expected and is NOT the failure the board had — the board's
        # rendering is what was repaired. Recorded for visibility rather than
        # failed on, because failing on it would be a check that fires on the
        # correct behaviour.
        per_cell[label] = {
            "n_decisions": len(payloads),
            "n_decisions_with_refusals": sum(1 for p in payloads
                                             if p.get("n_refusals")),
            "n_refusal_lines": sum(int(p.get("n_refusals") or 0)
                                   for p in payloads),
            "load_units": sorted({row.get("unit") for p in payloads
                                  for row in (p.get("load") or [])}),
            "max_load_seen": max(
                (int(row.get("held") or 0) for p in payloads
                 for row in (p.get("load") or [])), default=0),
            "raw_task_states_seen": stale_board,
        }

    # The units must agree across cells: a cell reporting load against a limit
    # that never binds (concurrency, when the binding limit is segment capacity)
    # is showing the manager a true number that means the opposite of what is
    # happening, and it would do so in only some cells.
    units_by_cell = {label: detail.get("load_units")
                     for label, detail in per_cell.items() if detail.get("n_decisions")}
    distinct_units = {json.dumps(u) for u in units_by_cell.values()}
    if len(distinct_units) > 1:
        problems.append({
            "problem": "load is reported against different limits by cell",
            "by_cell": units_by_cell,
        })

    return {
        "comparable": not problems,
        "cells": sorted(bundles),
        "problems": problems,
        "per_cell": per_cell,
        "establishes": ("the three load signals were IN THE OBSERVATION at every "
                        "manager decision, in the same units in every cell"),
        "does_not_establish": ("that they were rendered into the prompt (see "
                               "check_load_feedback.py) or that the manager used "
                               "them"),
    }
