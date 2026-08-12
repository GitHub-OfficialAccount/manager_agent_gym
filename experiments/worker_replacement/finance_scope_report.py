"""The scope run's report: four measured quantities, and NO CLAIMS.

The run is 2-3 episodes per cell. At that size there is no significance claim, no
"channel X moved or did not move allocation", and no contrast verdict in either
direction — and this module refuses to produce one rather than leaving it to the
reader's restraint. Per-cell numbers are DESCRIPTIVE POINT ESTIMATES whose
intervals are wide enough to contain almost anything.

WHAT THE RUN IS FOR, and all four were previously assumed rather than measured:

  1. SIGMA, pooled within-cell. df = k(n-1) ≈ 12 at six cells — imprecise, ±25-30%,
     and an IN-ENVIRONMENT measurement replacing an imported prior. That is what a
     later sizing decision needs.
  2. SIGMA_D, the paired standard deviation. Whether pairing on (instance, cell)
     removes variance decides whether n halves — and it is coupled to (3): effective
     pairing shrinks sigma_d AND promotes heterogeneity to the leading term, so the
     two corrections partially self-cancel.
  3. BETWEEN-INSTANCE EFFECT SD, against the design-side prior of 0.0254 (ceiling
     CV 23%). The prior is spread of HEADROOM and transfers only if realised
     effects scale with headroom, which this measures.
  4. THE EFFECT under R1's schema, which no prior run has produced.

TWO SAMPLING FACTS THAT TRAVEL WITH EVERY NUMBER HERE, because they bias in a
direction a reader must know about and a footnote is what gets dropped:

  * THE LOW PICK IS THE SUITE MINIMUM. Seed 23 at 0.0516 is the minimum of the
    admitted suite (a legitimate 1-in-11 draw). Chosen mean 0.0938 against
    admitted mean 0.1034, so EFFECT MAGNITUDES SIT BELOW THE SUITE'S BY
    CONSTRUCTION.
  * IT COMPOUNDS WITH THE STRATIFICATION INFLATION. The rule widens sigma_between
    BY DESIGN and this draw shifts the centre DOWN. Harmless for sigma — noise,
    not effect — and not harmless for effect magnitudes.

  uv run python -m experiments.worker_replacement.finance_scope_report
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path
from typing import Any

from . import finance_cells as fc
from . import finance_comparability as cmp
from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records" / "R2"

NO_CLAIM = (
    "NO SIGNIFICANCE CLAIM. At 2-3 episodes per cell there is no contrast verdict "
    "in either direction — not 'channel X moved allocation', and not 'channel X "
    "did not'. These are descriptive point estimates with intervals wide enough to "
    "contain almost anything. The run exists to see behaviour and measure variance."
)


def load_cell_bundles(directory: Path = RECORDS) -> dict[tuple[str, int], dict]:
    """Every scope bundle, keyed by (cell, seed). Dry runs excluded."""
    out: dict[tuple[str, int], dict] = {}
    for path in sorted(directory.glob("run_cell*_seed*.json")):
        bundle = json.loads(path.read_text())
        manifest = bundle.get("manifest", {})
        if manifest.get("dry_run"):
            continue
        cell = manifest.get("cell")
        seed = manifest.get("instance_seed")
        if cell is None or seed is None:
            continue
        out[(cell, seed)] = bundle
    return out


def per_episode_outcome(bundle: dict[str, Any]) -> dict[str, Any]:
    """One episode, with regret split THREE ways (LS ruling on the 17% unstaffed).

    Realised-authoritative scoring puts an unstaffed unit's loss in ALLOCATION
    loss, which is correct — failing to staff IS an allocation failure. But it
    puts TWO BEHAVIOURS in one term: MIS-routing (staffed the wrong worker) and
    NON-routing (never staffed it), and only the first is plausibly
    channel-sensitive. At 17% unstaffed, a sigma dominated by non-routing measures
    the manager STALLING, and a sizing decision built on it sizes the wrong
    quantity.

    So regret is reported as three parts that sum to it exactly:

        regret = unstaffed_loss + allocation_loss_staffed + execution_loss

    where unstaffed_loss is the oracle's own contribution for units nobody held.
    """
    manifest = bundle["manifest"]
    cell = manifest["cell"]
    seed = manifest["instance_seed"]
    instance = gen.generate(seed)
    cal = instance["class_calibration"]
    phase = "pre_swap" if not fc.CELLS[cell].swap else "post_swap"
    oracle = sc.oracle_capacitated(instance, phase=phase, cap=3)
    achieved = bundle["outcome"]["achieved"]

    # Per-segment oracle contributions, from the DP's own choices.
    oracle_alloc = sc.oracle_allocation_capacitated(instance, phase=phase, cap=3)
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    allocation = bundle.get("allocation", {})
    reports = bundle.get("reports", {})

    unstaffed_loss = allocation_staffed = execution_loss = 0.0
    for segment in instance["segments"]:
        sid = segment["segment_id"]
        oracle_worker = oracle_alloc.get(sid)
        oracle_contrib = (sc.s(segment, by_id[oracle_worker], cal)
                          if oracle_worker else 0.0)
        assignee = allocation.get(sid)
        if not assignee or assignee == sc.UNSTAFFED or assignee not in by_id:
            unstaffed_loss += oracle_contrib
            continue
        faithful = sc.s(segment, by_id[assignee], cal)
        got = sc.score_report(segment, reports.get(sid), cal)
        allocation_staffed += oracle_contrib - faithful
        execution_loss += faithful - got

    regret = oracle - achieved
    staffed_regret = allocation_staffed + execution_loss
    return {
        "cell": cell,
        "seed": seed,
        "oracle_roster_phase": phase,
        "oracle": oracle,
        "achieved": achieved,
        "regret": regret,
        "regret_share": regret / oracle if oracle else None,
        # THE THREE PARTS. They sum to regret by construction; the residual is
        # reported so a drift between this split and the scorer is visible rather
        # than absorbed.
        "unstaffed_loss": unstaffed_loss,
        "allocation_loss_staffed": allocation_staffed,
        "execution_loss_signed": execution_loss,
        "split_residual": regret - (unstaffed_loss + allocation_staffed
                                    + execution_loss),
        # STAFFED-ONLY regret, same denominator as the full share so the two
        # sigmas are directly comparable and their gap is the unstaffed component.
        "staffed_regret_share": staffed_regret / oracle if oracle else None,
        "completions": len(bundle.get("completions", [])),
        "n_tasks": manifest.get("n_tasks"),
        "n_unstaffed": bundle["outcome"].get("n_unstaffed"),
        "n_parsed": bundle["outcome"].get("n_parsed"),
        "n_declined": _declines(bundle),
        "n_unreadable": _unreadable(bundle),
        "segment_states": segment_states(bundle),
        "concurrency": manifest.get("concurrency", "__ABSENT__"),
    }


def coverage_misrouting(bundles: dict[tuple[str, int], dict]) -> dict[str, Any]:
    """Mis-routing over ASSIGNED segments, reported for BOTH populations.

    THE SELECTION EFFECT THIS FIXES: the earlier figure was computed only over
    segments that EXECUTED — excluding exactly the segments where the allocation
    failed — and the exclusion was offered as evidence the number was robust. It
    is not; the excluded set is ~8x enriched in mis-routing.

    THE EXCLUSION THAT IS LEGITIMATE, and which nearly produced a 10x-wrong
    figure before it was noticed: SOLE-HELD-CLASS segments, where no worker on the
    post-swap roster covers the class. There is no correct choice to make on those
    — the absence is BY DESIGN, it is the source of interior spread — so counting
    them as mis-routes measures the generator, not the manager.

    Both populations are reported and NEITHER replaces the other: they are true of
    different sets, and the pair is more informative than either alone.
    """
    # THE POPULATION PREDICATE, stated because a name would hide it (§B):
    #   "IRB-approved, assigned to a worker on THE CELL'S OWN ROSTER, and at
    #    least one worker on THAT roster covers the class."
    #
    # "the cell's own roster" is the whole of both denominator discrepancies with
    # LS this week — 20 vs 19, and 105/83/22 vs 102/81/21. Reconciled: the three
    # segments are cell U's seed-23 seg_04 (sovereign) and seeds 3/36 seg_07
    # (mdb), all classes held ONLY by the predecessor. Under a post-swap roster
    # they are sole-held and drop out; under the PRE-swap roster — which is cell
    # U's own, since U carries no swap — a coverer exists and they count.
    #
    # MINE IS THE CORRECT ONE, by the same ruling that fixed the U-oracle: cell U
    # is scored against the roster it actually had. Both discrepancies trace to
    # one unstated predicate, which is exactly what §B exists to prevent.
    from . import finance_cells as _fc

    ex = [0, 0]
    refused = [0, 0]
    timing = [0, 0]
    sole = 0
    for (cell, seed), bundle in bundles.items():
        instance = gen.generate(seed)
        roster = set(_fc.active_roster(instance, _fc.CELLS[cell]))
        by_id = {w["worker_id"]: w for w in instance["workers"]}
        active = [by_id[r] for r in roster if r in by_id]
        board = _board_by_task_id(bundle)
        segment_tasks = (bundle.get("index") or {}).get("segment_task_ids") or {}
        allocation = bundle.get("allocation", {})
        for segment in instance["segments"]:
            if not segment["irb_approved"]:
                continue
            sid = segment["segment_id"]
            row = board.get(segment_tasks.get(sid)) or {}
            assignee = row.get("assigned_agent_id")
            if not assignee or assignee not in by_id:
                continue
            if not any(segment["asset_class"] in w["irb_coverage"]
                       for w in active):
                sole += 1
                continue
            mis = segment["asset_class"] not in by_id[assignee]["irb_coverage"]
            executed = allocation.get(sid) not in (None, "__unstaffed__")
            if executed:
                target = ex
            else:
                # THE UNEXECUTED SET IS TWO POPULATIONS, NOT ONE. Splitting by
                # final board status: `ready` means the capacity refusal held to
                # the end; `running` means it started and the horizon cut it off.
                # Pooled, they give ~9% and describe NEITHER — 0 of 20 for the
                # first and 2 of 2 for the second. The pooled figure must not be
                # quoted, INCLUDING where it appears to support the account.
                target = (refused if row.get("status") == "ready" else timing)
            target[0] += 1
            target[1] += 1 if mis else 0

    # THE COMPARATOR THAT GIVES THE NUMBER ITS SIGN. Without it, "3 of 105" reads
    # as a manager failing at coverage, which is the wrong sign.
    #
    # WHAT THE COMPARATOR MEANS, AND WHAT IT DOES NOT. The capacitated optimum
    # accepts ONE avoidable mismatch per instance AS THE PRICE OF FEASIBILITY. It
    # is NOT that "the manager beats the optimum on coverage" — that reading was
    # withdrawn, because it compares a FEASIBLE allocation against an INFEASIBLE
    # one. The manager did not pay the price because its allocation violates the
    # cap, and coverage fidelity purchased by breaking the constraint is not
    # fidelity. The two rates are not commensurable as a ranking; the optimum's
    # rate is here to show that a nonzero mismatch count is what feasibility
    # COSTS, not what failure looks like.
    oracle_mis = oracle_n = 0
    for seed in sorted({s for _c, s in bundles}):
        instance = gen.generate(seed)
        post = [w for w in instance["workers"]
                if w["worker_id"] in instance["event"]["roster_post_swap"]]
        by_id = {w["worker_id"]: w for w in instance["workers"]}
        oa = sc.oracle_allocation_capacitated(instance, phase="post_swap", cap=3)
        for segment in instance["segments"]:
            if not segment["irb_approved"]:
                continue
            if not any(segment["asset_class"] in w["irb_coverage"] for w in post):
                continue
            assignee = oa.get(segment["segment_id"])
            if not assignee:
                continue
            oracle_n += 1
            if segment["asset_class"] not in by_id[assignee]["irb_coverage"]:
                oracle_mis += 1

    return {
        "capacitated_optimum_comparator": {
            "avoidable_mismatches_per_instance": oracle_mis / 3 if oracle_mis else 0,
            "n_checked": oracle_n,
            "reading": ("the optimum accepts one mismatch per instance AS THE "
                        "PRICE OF FEASIBILITY. This is NOT a ranking: the "
                        "manager's allocation violates the cap, so its lower rate "
                        "is coverage fidelity bought by breaking the constraint. "
                        "Quote the manager's rate only with this beside it — "
                        "alone it carries the wrong sign — but do NOT read it as "
                        "the manager outperforming the optimum."),
        },
        "executed": {"n": ex[0], "misrouted": ex[1],
                     "rate": ex[1] / ex[0] if ex[0] else None},
        # SPLIT, never pooled. The pooled rate describes no population.
        "unexecuted_capacity_refused": {
            "n": refused[0], "misrouted": refused[1],
            "rate": refused[1] / refused[0] if refused[0] else None,
            "reading": ("every overflow placement is COVERAGE-CORRECT — the "
                        "manager fills a covering worker past capacity and the "
                        "invisible constraint absorbs the cost. This is the "
                        "load-bearing figure for the surviving account, and it is "
                        "better evidence than the aggregate because it is about "
                        "the FAILING segments specifically."),
        },
        "unexecuted_timing_cutoff": {
            "n": timing[0], "misrouted": timing[1],
            "rate": timing[1] / timing[0] if timing[0] else None,
            "reading": "a different failure mode; n=2, no rate claimed",
        },
        "assigned_total": {
            "n": ex[0] + refused[0] + timing[0],
            "misrouted": ex[1] + refused[1] + timing[1],
            "rate": ((ex[1] + refused[1] + timing[1])
                     / (ex[0] + refused[0] + timing[0])
                     if (ex[0] + refused[0] + timing[0]) else None)},
        "excluded_sole_held_class": sole,
        "note": ("REPORT THE ASSIGNED FIGURE, with the executed one BESIDE it and "
                 "not replaced by it. The executed-only number conditions on the "
                 "allocation having worked; the unexecuted set is where it failed "
                 "and is several times enriched."),
    }


def _board_by_task_id(bundle: dict[str, Any]) -> dict[str, Any]:
    """The task board keyed by TASK ID, never by display name.

    THE JOIN THIS REPLACES KEYED ON `f"Risk-weighted assets — {segment_id}"`, a
    MUTABLE DISPLAY STRING. `RefineTaskAction` renames tasks, so a rename breaks
    the join and the segment silently reads as UNASSIGNED — no row found, no
    assignee, no error, and `never_assigned` is the exact false claim L2a exists
    to prevent. Measured: renaming one segment task takes the name join from 9
    hits to 8 while the id join stays at 9.

    The board already carries `task_id`, so the name was never the only key
    available.

    A CLAIM THAT WAS HERE AND IS RETRACTED. An earlier version said the prefix is
    not unique, so "a collision does not even need a rename". RR supplied that
    escalation and then withdrew it, and I had propagated it without checking.
    **Every segment's exact name appears exactly once across all 18 bundles, so
    under an exact-name key there is no collision.**

    The accurate form reaches the same conclusion by a different route: a PREFIX
    predicate over the name captures tasks that are not segments — one bundle has
    ten prefix-matching rows for nine segments, the tenth being
    `"Risk-weighted assets — seg_08 standardised recalculation"`, a MANAGER
    REMEDIATION. Under an exact-name key that row does not collide; it MISSES. So
    the name is safe against collision and unsafe against mutation, which is
    exactly the failure a rename produces.

    NOT RECOVERABLE FROM THE 18 EXISTING BUNDLES: `task_refined` is emitted inside
    `if self.new_description:` while the name mutates outside it, so a rename that
    changes no description leaves no trace at all. Any figure derived by name from
    those bundles carries that as a stated limitation.
    """
    return {r["task_id"]: r for r in (bundle.get("task_board_final") or [])}


def segment_states(bundle: dict[str, Any]) -> dict[str, str]:
    """Four states per segment, reconstructed from the ASSIGNMENT record.

    THE DEFECT THIS REPLACES: `allocation` in a run bundle is built by walking
    COMPLETIONS, so a segment the manager ASSIGNED and the engine never executed
    could not be represented in it — it silently became `__unstaffed__`, which
    reads as "the manager never staffed it".

    Measured across all 18 scope episodes: all 22 supposedly-unstaffed segments
    carry a real `assigned_agent_id` on the board (20 `ready`, 2 `running`), and
    ZERO were never assigned. So the term I labelled NON-ROUTING — 48.3% of
    regret — was not non-routing at all. The manager routed every one of them and
    the engine never ran them: 580 `assignment_deferred` events, workers at
    max_concurrent_tasks=1, and a manager whose observation contains no word for
    any of it.

    Bundles written before the runner recorded `segment_states` are reconstructed
    here from `task_board_final` + `parse_detail`, which is why no episode is
    re-run.
    """
    if bundle.get("segment_states"):
        return dict(bundle["segment_states"])

    index = bundle.get("index", {}).get("segment_task_ids", {})
    board = _board_by_task_id(bundle)
    detail = bundle.get("parse_detail") or {}
    allocation = bundle.get("allocation", {})

    out: dict[str, str] = {}
    for segment_id, task_id in index.items():
        row = board.get(task_id) or {}
        assignee = row.get("assigned_agent_id")
        executed = (allocation.get(segment_id)
                    not in (None, "__unstaffed__"))
        if not assignee:
            out[segment_id] = "never_assigned"
        elif not executed:
            out[segment_id] = "assigned_but_unexecuted"
        elif detail.get(segment_id, {}).get("rwa") is None:
            out[segment_id] = "executed_but_unparseable"
        else:
            out[segment_id] = "executed_and_parsed"
    return out


def _declines(bundle: dict[str, Any]) -> int:
    """Explicit declines, from the per-segment parse detail."""
    detail = bundle.get("parse_detail") or {}
    return sum(1 for v in detail.values() if v.get("declined"))


def _unreadable(bundle: dict[str, Any]) -> int:
    """Deliverables we could not read — NEVER summed with declines."""
    detail = bundle.get("parse_detail") or {}
    return sum(1 for v in detail.values()
               if v.get("rwa") is None and not v.get("declined"))


def _pooled_sigma(rows: list[dict[str, Any]], key: str) -> tuple[float | None, int]:
    """Pooled within-cell sd of `key`. Only cells with >=2 episodes contribute."""
    by_cell: dict[str, list[float]] = {}
    for row in rows:
        if row.get(key) is not None:
            by_cell.setdefault(row["cell"], []).append(row[key])
    num = den = 0.0
    for values in by_cell.values():
        if len(values) < 2:
            continue
        num += sum((v - st.fmean(values)) ** 2 for v in values)
        den += len(values) - 1
    return ((num / den) ** 0.5 if den else None), int(den)


def variance_quantities(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The four quantities. Each reports its own df, because at this size the
    precision of a variance estimate matters more than its point value."""
    by_cell: dict[str, list[float]] = {}
    by_seed: dict[int, list[float]] = {}
    for row in rows:
        if row["regret_share"] is None:
            continue
        by_cell.setdefault(row["cell"], []).append(row["regret_share"])
        by_seed.setdefault(row["seed"], []).append(row["regret_share"])

    # 1. SIGMA POOLED WITHIN CELL. Only cells with >=2 episodes contribute.
    numerator = denominator = 0.0
    for values in by_cell.values():
        if len(values) < 2:
            continue
        numerator += sum((v - st.fmean(values)) ** 2 for v in values)
        denominator += len(values) - 1
    sigma_pooled = (numerator / denominator) ** 0.5 if denominator else None

    # 3. BETWEEN-INSTANCE spread of the per-instance mean.
    instance_means = [st.fmean(v) for v in by_seed.values() if v]
    sigma_between = (st.stdev(instance_means) if len(instance_means) > 1 else None)

    # 2. SIGMA_D on the paired contrast against cell 0, per instance. Requires
    # both cells present for the same instance, which is what pairing means.
    paired: dict[str, list[float]] = {}
    lookup = {(r["cell"], r["seed"]): r["regret_share"] for r in rows}
    for cell in sorted({r["cell"] for r in rows}):
        if cell == "0":
            continue
        diffs = [lookup[(cell, seed)] - lookup[("0", seed)]
                 for seed in sorted({r["seed"] for r in rows})
                 if (cell, seed) in lookup and ("0", seed) in lookup
                 and lookup[(cell, seed)] is not None
                 and lookup[("0", seed)] is not None]
        if len(diffs) > 1:
            paired[cell] = diffs

    sigma_d = None
    if paired:
        pooled_num = sum(sum((d - st.fmean(v)) ** 2 for d in v)
                         for v in paired.values())
        pooled_den = sum(len(v) - 1 for v in paired.values())
        sigma_d = (pooled_num / pooled_den) ** 0.5 if pooled_den else None

    # SIGMA TWICE (LS ruling). The GAP between them is itself the answer to
    # whether the DV is measuring stalling: if they diverge materially, the
    # staffed-only figure is what a future sizing decision uses, and the
    # divergence is reportable in its own right rather than a caveat on the other.
    sigma_staffed, sigma_staffed_df = _pooled_sigma(rows, "staffed_regret_share")
    gap = (None if sigma_pooled is None or sigma_staffed is None
           else sigma_pooled - sigma_staffed)

    return {
        "sigma_pooled_within_cell": sigma_pooled,
        "sigma_pooled_df": int(denominator),
        "sigma_pooled_staffed_only": sigma_staffed,
        "sigma_pooled_staffed_df": sigma_staffed_df,
        "sigma_gap_full_minus_staffed": gap,
        # RETRACTED READING, kept as a correction rather than deleted. I claimed
        # the GAP measured how much the DV is about stalling. It does not: the two
        # components are ANTI-CORRELATED (r = -0.42 at 12 episodes) because they
        # partition the same nine units — more unstaffed means fewer staffed units
        # on which to accumulate execution loss — so no gap was predicted in
        # either direction and its sign carries no information about stalling.
        #
        # WHAT SURVIVES: report sigma twice, and use the STAFFED-ONLY figure for
        # sizing, because it is the variance of the quantity a channel could move
        # — regardless of whether it lands above or below the full one.
        "sigma_gap_reading": (
            "THE GAP CARRIES NO INFORMATION ABOUT STALLING — that reading was "
            "retracted. The two components are anti-correlated because they "
            "partition the same units, so no gap was predicted either way. Use "
            "the STAFFED-ONLY sigma for sizing: it is the variance of the "
            "quantity a channel could move."),
        "sigma_d_paired_vs_cell0": sigma_d,
        "sigma_d_df": sum(len(v) - 1 for v in paired.values()),
        "sigma_between_instance": sigma_between,
        "sigma_between_df": (len(instance_means) - 1) if instance_means else 0,
        "design_side_prior_ceiling_sd": 0.0254,
        "pairing_heterogeneity_coupling": (
            "sigma_d and sigma_between are ONE COUPLED QUESTION, not two "
            "independent inflators: effective pairing shrinks sigma_d AND "
            "promotes between-instance heterogeneity to the leading term, so the "
            "two corrections partially self-cancel."),
    }


def build_report(directory: Path = RECORDS) -> dict[str, Any]:
    bundles = load_cell_bundles(directory)
    rows = [per_episode_outcome(b) for b in bundles.values()]
    rows.sort(key=lambda r: (r["cell"], r["seed"]))

    concurrency = cmp.report_concurrency(
        {f"{c}/{s}": b for (c, s), b in bundles.items()})
    # `__ABSENT__` is NOT unknown: it is the first four scope episodes, which ran
    # at N=4 before the field existed. Explained here rather than BACKFILLED into
    # the bundles — editing a committed record to make a report tidy is how a
    # record stops being evidence. The value is recoverable from the commit that
    # launched them (a9833aa) and from R2_oracle_phase_correction.json.
    concurrency["absent_means"] = (
        "the first four scope episodes (cells U/0/1/2 on seed 3), which ran at "
        "N=4 before `concurrency` was a manifest field. Not backfilled: a "
        "committed record edited to tidy a report stops being evidence.")

    # THE DECLINE CHANNEL, reported at the run level. It exists because R1
    # unscripted the worker and gave refusal a parseable form; if it is never
    # summarised, we built an observable channel and did not observe it.
    # THE FOUR-WAY SPLIT that replaces the mislabelled "non-routing" term.
    states: dict[str, int] = {}
    for row in rows:
        for state in row["segment_states"].values():
            states[state] = states.get(state, 0) + 1

    total_declined = sum(r["n_declined"] for r in rows)
    total_unreadable = sum(r["n_unreadable"] for r in rows)

    per_cell = {}
    for cell in sorted({r["cell"] for r in rows}):
        values = [r["regret_share"] for r in rows
                  if r["cell"] == cell and r["regret_share"] is not None]
        per_cell[cell] = {
            "n_episodes": len(values),
            "mean_regret_share": st.fmean(values) if values else None,
            "values": values,
            "role": fc.CELLS[cell].role,
        }

    return {
        "NO_CLAIM": NO_CLAIM,
        "n_episodes": len(rows),
        "coverage_misrouting": coverage_misrouting(bundles),
        "segment_state_counts": states,
        "state_note": (
            "'assigned_but_unexecuted' is what was previously reported as "
            "UNSTAFFED and read as NON-ROUTING. The manager assigned every one of "
            "them; the engine never ran them. It is capacity starvation, not a "
            "routing failure, and it must not be folded into a routing metric."),
        "declines": {
            "n_declined": total_declined,
            "n_unreadable": total_unreadable,
            "note": ("an explicit decline and an unreadable deliverable both "
                     "score 0 and are NEVER summed — they are different "
                     "behaviours, and the decline is the one the unscripting was "
                     "built to make observable"),
        },
        "episodes": rows,
        "per_cell_descriptive": per_cell,
        "variance_quantities": variance_quantities(rows),
        "concurrency": concurrency,
        "sampling_caveats": (
            "the low pick is the SUITE MINIMUM (seed 23 at 0.0516) and the chosen "
            "mean 0.0938 sits below the admitted mean 0.1034, so EFFECT "
            "MAGNITUDES ARE BELOW THE SUITE'S BY CONSTRUCTION; and this compounds "
            "with the stratification inflation, which widens sigma_between by "
            "design. Harmless for sigma, not harmless for effect magnitudes."),
    }


def main() -> int:
    report = build_report()
    print("SCOPE RUN REPORT — descriptive only\n")
    print(NO_CLAIM)
    print(f"\nepisodes: {report['n_episodes']}\n")
    print(f"  {'cell':<5} {'n':<3} {'mean regret share':<20} role")
    for cell, block in report["per_cell_descriptive"].items():
        mean = block["mean_regret_share"]
        print(f"  {cell:<5} {block['n_episodes']:<3} "
              f"{(f'{mean:.4f}' if mean is not None else '-'):<20} "
              f"{block['role'][:44]}")

    # THE THREE-WAY SPLIT, printed before the sigmas because it is what makes
    # them readable: a sigma on full regret means something different depending
    # on how much of that regret is non-routing.
    rows = report["episodes"]
    if rows:
        tot_uns = sum(r["unstaffed_loss"] for r in rows)
        tot_alloc = sum(r["allocation_loss_staffed"] for r in rows)
        tot_exec = sum(r["execution_loss_signed"] for r in rows)
        tot_reg = sum(r["regret"] for r in rows)
        resid = max(abs(r["split_residual"]) for r in rows)
        print(f"\nREGRET SPLIT THREE WAYS (summed over {len(rows)} episodes; "
              f"they sum to regret by construction):")
        print(f"  ASSIGNED-BUT-UNEXECUTED loss        {tot_uns:8.4f}  "
              f"{100 * tot_uns / tot_reg:5.1f}%")
        print(f"  allocation loss on STAFFED units    {tot_alloc:8.4f}  "
              f"{100 * tot_alloc / tot_reg:5.1f}%")
        print(f"  execution loss (signed)             {tot_exec:8.4f}  "
              f"{100 * tot_exec / tot_reg:5.1f}%")
        print(f"  total regret                        {tot_reg:8.4f}   "
              f"(max per-episode residual {resid:.2e})")
        print(f"  THE FIRST TERM IS NOT 'NON-ROUTING' — that label was WRONG. All "
              f"22 of these\n  segments carry a real assignee on the board and "
              f"ZERO were never assigned. The\n  manager routed every one; the "
              f"engine never ran them (580 deferral events,\n  workers at "
              f"max_concurrent_tasks=1). It is CAPACITY STARVATION, and folding "
              f"it\n  into a routing metric is what produced a week of wrong "
              f"statements.")
        if tot_alloc < 0:
            print(f"  NOTE ON THE NEGATIVE ALLOCATION TERM, which is not evidence "
                  f"the manager\n  out-allocated the oracle: the capacitated "
                  f"oracle DELIBERATELY UNDER-SERVES some\n  segments to free "
                  f"capacity for others (measured on seed 3: 1 of 9). A manager "
                  f"that\n  staffs such a segment beats the oracle's choice ON "
                  f"THAT SEGMENT while losing\n  overall by failing to staff the "
                  f"ones the oracle was protecting. The split is\n  exact; this "
                  f"term is a difference from the oracle's own attribution, not a\n"
                  f"  per-segment optimum.")

    v = report["variance_quantities"]
    print("\nTHE FOUR QUANTITIES (each with its df — at this size the precision "
          "matters\nmore than the point value):")
    print(f"  sigma pooled within cell : "
          f"{_fmt(v['sigma_pooled_within_cell'])}  df={v['sigma_pooled_df']}")
    print(f"  sigma pooled STAFFED-ONLY: "
          f"{_fmt(v['sigma_pooled_staffed_only'])}  "
          f"df={v['sigma_pooled_staffed_df']}")
    gap = v["sigma_gap_full_minus_staffed"]
    print(f"  GAP (full - staffed)     : {_fmt(gap)}")
    print(f"    {v['sigma_gap_reading']}")
    print(f"  sigma_d paired vs cell 0 : "
          f"{_fmt(v['sigma_d_paired_vs_cell0'])}  df={v['sigma_d_df']}")
    print(f"  sigma between instances  : "
          f"{_fmt(v['sigma_between_instance'])}  df={v['sigma_between_df']}"
          f"   (design-side prior {v['design_side_prior_ceiling_sd']})")
    print(f"\n  {v['pairing_heterogeneity_coupling']}")

    cm = report["coverage_misrouting"]
    print(f"\nCOVERAGE MIS-ROUTING — both populations, neither replacing the other:")
    for key in ("executed", "unexecuted_capacity_refused",
                "unexecuted_timing_cutoff", "assigned_total"):
        b = cm[key]
        print(f"  {key:<16} n={b['n']:>3}  mis-routed {b['misrouted']}  "
              f"{100 * b['rate']:.1f}%" if b["rate"] is not None else
              f"  {key:<16} n={b['n']:>3}")
    comp = cm["capacitated_optimum_comparator"]
    print(f"  CAPACITATED OPTIMUM, same measure: "
          f"{comp['avoidable_mismatches_per_instance']:.2f} avoidable mismatches "
          f"per instance —\n     THE PRICE OF FEASIBILITY, not a benchmark the "
          f"manager beat.\n     {comp['reading']}")
    print(f"  excluded as sole-held-class (no correct choice existed): "
          f"{cm['excluded_sole_held_class']}")
    print(f"  {cm['note']}")

    st_counts = report["segment_state_counts"]
    print(f"\nSEGMENT STATES — the four-way split that replaces 'unstaffed':")
    for k in ("never_assigned", "assigned_but_unexecuted",
              "executed_but_unparseable", "executed_and_parsed"):
        print(f"  {k:<28} {st_counts.get(k, 0)}")
    print(f"  {report['state_note']}")

    d = report["declines"]
    print(f"\nDECLINE CHANNEL (what the unscripting was built to expose): "
          f"{d['n_declined']} explicit declines,\n  {d['n_unreadable']} unreadable "
          f"deliverables — never summed, different behaviours.")
    print(f"\nCONCURRENCY (an instrument setting that VARIES here): "
          f"{report['concurrency']['concurrency_values_seen']}")
    print(f"  {report['concurrency']['limitation']}")
    print(f"\nSAMPLING: {report['sampling_caveats']}")

    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / "scope_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\nwritten -> {RECORDS / 'scope_report.json'}")
    return 0


def _fmt(value: float | None) -> str:
    return f"{value:.4f}" if value is not None else "insufficient data"


if __name__ == "__main__":
    raise SystemExit(main())
