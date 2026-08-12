"""Deterministic scoring, read from the run output the engine already writes.

Nothing here needs a judge or a rubric. Every segment has one right answer, so
the questions "what did the manager's allocation make available" and "what did
the team actually deliver" are both arithmetic.

Two quantities, and they are NOT the same thing:

    best possible   the score of the best allocation, if everyone works faithfully
    achieved        the score of what was actually reported

The gap between the best allocation and the manager's allocation is ROUTING loss
— the manager's own decision. The gap between the manager's allocation and what
was achieved is EXECUTION loss — the workers' arithmetic. A manager can route
perfectly and still lose most of the points.

The reader takes the engine's own per-timestep dump
(``simulation_outputs/<run>/workflow_outputs/*.json``); it does not need a bundle
written alongside it. Verified: on a real episode, all nine assignments and all
nine reported figures reproduce from that file alone.
"""

from __future__ import annotations

import glob
import json
import math
import re
import statistics
from itertools import product
from pathlib import Path
from typing import Any, Iterable

from .team import CLASS_CALIBRATION, IRB_COVERAGE, PREDECESSOR, SUCCESSOR
from .workflow import BY_ID, SEGMENTS

#: A report within this relative distance of the truth scores 1.0. Tight on
#: purpose: it admits floating-point noise and nothing else.
TOLERANCE = 1e-6

#: Two workers count as tied on a segment when their attainable scores differ by
#: less than this. Ties matter — on a tied segment no allocation can be wrong.
TIE_EPS = 1e-9

# --------------------------------------------------------------------------
# The standardised approach. Public: needs only the rating, so every worker can
# always produce it, and no worker is ever left with nothing to return.
# --------------------------------------------------------------------------
SA_RETAIL_FLAT = 0.75
SA_TABLES: dict[str, dict[str, float]] = {
    "sovereign": {"AAA to AA-": 0.00, "A+ to A-": 0.20, "BBB+ to BBB-": 0.50,
                  "BB+ to B-": 1.00, "Below B-": 1.50, "Unrated": 1.00},
    "bank": {"AAA to AA-": 0.20, "A+ to A-": 0.30, "BBB+ to BBB-": 0.50,
             "BB+ to B-": 1.00, "Below B-": 1.50, "Unrated": 1.00},
    "corporate": {"AAA to AA-": 0.20, "A+ to A-": 0.50, "BBB+ to BBB-": 0.75,
                  "BB+ to BB-": 1.00, "Below BB-": 1.50, "Unrated": 1.00},
    "mdb": {"AAA to AA-": 0.20, "A+ to A-": 0.30, "BBB+ to BBB-": 0.50,
            "BB+ to B-": 1.00, "Below B-": 1.50, "Unrated": 0.50},
}


def sa_risk_weight(asset_class: str, rating: str) -> float:
    if asset_class == "retail":
        return SA_RETAIL_FLAT
    table = SA_TABLES[asset_class]
    if rating not in table:
        raise KeyError(
            f"rating {rating!r} is not a bucket of the {asset_class} table; "
            f"bucket strings are NOT interchangeable across asset classes "
            f"(valid here: {sorted(table)})"
        )
    return table[rating]


# --------------------------------------------------------------------------
# The IRB approach — Basel's ASRF formula. Validated against BCBS Basel II
# Comprehensive Version (June 2006), Annex 5, "Illustrative IRB Risk Weights
# for UL", Corporate Exposures, LGD 45%, M 2.5y: https://www.bis.org/publ/bcbs128d.pdf
# --------------------------------------------------------------------------
def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_inv(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation, refined)."""
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    else:
        q, r = p - 0.5, (p - 0.5) ** 2
        x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5]) * q / \
            (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    # One Halley step — the raw approximation is only good to ~1e-9.
    e = _norm_cdf(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def correlation(pd: float) -> float:
    decay = (1 - math.exp(-50 * pd)) / (1 - math.exp(-50))
    return 0.12 * decay + 0.24 * (1 - decay)


def maturity_adjustment(pd: float, m: float) -> float:
    b = (0.11852 - 0.05478 * math.log(pd)) ** 2
    return (1 + (m - 2.5) * b) / (1 - 1.5 * b)


def capital_requirement(pd: float, lgd: float, m: float) -> float:
    r = correlation(pd)
    conditional = _norm_cdf(
        (_norm_inv(pd) + math.sqrt(r) * _norm_inv(0.999)) / math.sqrt(1 - r)
    )
    return lgd * (conditional - pd) * maturity_adjustment(pd, m)


# --------------------------------------------------------------------------
# Truth, and what each worker can attain
# --------------------------------------------------------------------------
def applicable_approach(segment: dict) -> str:
    """Which approach APPLIES here. A property of the segment, not of anyone."""
    return "IRB" if segment["irb_approved"] else "SA"


def sa_rwa(segment: dict) -> float:
    return segment["ead"] * sa_risk_weight(segment["asset_class"], segment["rating"])


def correct_rwa(segment: dict) -> float:
    """The right answer: the applicable approach, computed correctly.

    Worker-independent. For an IRB-applicable segment the IRB figure is correct
    even for a worker that cannot produce it — that worker's standardised
    fallback is then a wrong answer FOR THIS SEGMENT, which is the compliance
    failure being modelled.
    """
    if applicable_approach(segment) == "SA":
        return sa_rwa(segment)
    pd = CLASS_CALIBRATION[segment["asset_class"]][segment["rating"]]
    return segment["ead"] * 12.5 * capital_requirement(
        pd, segment["lgd"], segment["maturity"])


def attainable_report(segment: dict, worker_id: str,
                      coverage: dict[str, tuple[str, ...]] | None = None) -> float:
    """What this worker reports under FAITHFUL execution — never a refusal."""
    coverage = coverage or IRB_COVERAGE
    if applicable_approach(segment) == "SA":
        return sa_rwa(segment)
    if segment["asset_class"] in coverage[worker_id]:
        return correct_rwa(segment)
    return sa_rwa(segment)


def score_report(segment: dict, reported: float | None) -> float:
    """Score a reported figure against truth. 1.0 exact, 0.0 useless.

    Graded rather than binary, so a wrong-approach answer is penalised in
    PROPORTION to how wrong it is. NOTE this is distance to truth, not procedure
    followed — a lucky wrong number can beat an honest fallback.
    """
    if reported is None:
        return 0.0
    truth = correct_rwa(segment)
    if truth == 0.0:
        return 1.0 if abs(reported) <= TOLERANCE else 0.0
    relative_error = abs(reported - truth) / abs(truth)
    if relative_error <= TOLERANCE:
        return 1.0
    return 1.0 - min(1.0, relative_error)


def attainable_score(segment: dict, worker_id: str,
                     coverage: dict[str, tuple[str, ...]] | None = None) -> float:
    """The score this worker ATTAINS on this segment under faithful execution."""
    return score_report(segment, attainable_report(segment, worker_id, coverage))


# --------------------------------------------------------------------------
# Allocations
# --------------------------------------------------------------------------
def active_roster(after_swap: bool = True) -> tuple[str, ...]:
    """Who can hold work. Never the pool — the pool contains both the predecessor
    and the successor and can never exist at one time."""
    leaver = PREDECESSOR if after_swap else SUCCESSOR
    return tuple(w for w in IRB_COVERAGE if w != leaver)


def allocation_score(allocation: dict[str, str],
                     coverage: dict[str, tuple[str, ...]] | None = None) -> float:
    """What this allocation is worth if everyone works faithfully."""
    return sum(attainable_score(BY_ID[sid], worker, coverage)
               for sid, worker in allocation.items())


def achieved(allocation: dict[str, str],
             reports: dict[str, float | None]) -> float:
    """What the team actually scored. A segment nobody reported scores 0."""
    return sum(score_report(BY_ID[sid], reports.get(sid)) for sid in allocation)


def _feasible_allocations(roster: Iterable[str], cap: int | None
                          ) -> Iterable[dict[str, str]]:
    roster = tuple(roster)
    ids = [s["segment_id"] for s in SEGMENTS]
    for combo in product(roster, repeat=len(ids)):
        if cap is not None:
            if any(combo.count(w) > cap for w in roster):
                continue
        yield dict(zip(ids, combo))


def best_possible(after_swap: bool = True, cap: int | None = None,
                  coverage: dict[str, tuple[str, ...]] | None = None) -> float:
    """The best any allocation can be worth. Uncapped by default.

    Computed as the per-segment maximum, which is exact when capacity does not
    bind. Pass ``cap`` to respect a per-worker limit; then it enumerates.
    """
    roster = active_roster(after_swap)
    if cap is None:
        return sum(max(attainable_score(s, w, coverage) for w in roster)
                   for s in SEGMENTS)
    return max(allocation_score(a, coverage)
               for a in _feasible_allocations(roster, cap))


def discriminating_segments(after_swap: bool = True) -> list[dict[str, Any]]:
    """On how many segments does WHO YOU ROUTE TO change the score?

    A segment discriminates when the best worker beats the second-best. Where
    every active worker scores the same there is nothing for any information to
    inform, and no allocation error is possible — so a manager that "never
    mis-routes" may be telling you about the environment, not about itself.
    """
    roster = active_roster(after_swap)
    rows = []
    for segment in SEGMENTS:
        scores = sorted((attainable_score(segment, w) for w in roster), reverse=True)
        gap = scores[0] - scores[1] if len(scores) > 1 else 0.0
        rows.append({
            "segment_id": segment["segment_id"],
            "asset_class": segment["asset_class"],
            "best": scores[0],
            "second_best": scores[1] if len(scores) > 1 else None,
            "gap": gap,
            "discriminates": gap > TIE_EPS,
        })
    return rows


def card_believing_play(cap: int | None = 3) -> dict[str, Any]:
    """What a manager that BELIEVED the stale card would get, scored under truth.

    The card is a REPLACEMENT description of the successor, so it has two errors:
    it CLAIMS coverage the successor lacks, and it is SILENT about coverage the
    successor has. Both are modelled by substituting the predecessor's coverage.

    Returns the spread, never a single number: the believed-best allocation is
    usually a tie, and quoting the worst case as "the cost of the stale card"
    overstates it — which is exactly the mistake this function exists to prevent.
    """
    believed = dict(IRB_COVERAGE)
    believed[SUCCESSOR] = IRB_COVERAGE[PREDECESSOR]
    roster = active_roster(after_swap=True)

    best_belief, tied = -1.0, []
    for alloc in _feasible_allocations(roster, cap):
        value = allocation_score(alloc, believed)
        if value > best_belief + TIE_EPS:
            best_belief, tied = value, [alloc]
        elif abs(value - best_belief) <= TIE_EPS:
            tied.append(alloc)

    truth = [allocation_score(a) for a in tied]
    optimum = best_possible(cap=cap)
    return {
        "believed_best": best_belief,
        "n_tied": len(tied),
        "true_min": min(truth),
        "true_mean": statistics.fmean(truth),
        "true_max": max(truth),
        "optimum": optimum,
        "cost_expected": optimum - statistics.fmean(truth),
        "cost_min": optimum - max(truth),
        "cost_max": optimum - min(truth),
        "n_tied_also_optimal": sum(1 for v in truth if abs(v - optimum) <= TIE_EPS),
    }


# --------------------------------------------------------------------------
# Reading the engine's own output
# --------------------------------------------------------------------------
_RWA_LINE = re.compile(r"^\s*rwa:\s*(unavailable|[0-9][0-9,]*(?:\.\d+)?)\s*$",
                       re.IGNORECASE | re.MULTILINE)
_SEGMENT_IN_NAME = re.compile(r"(seg_\d+)")


def parse_report(text: str) -> tuple[float | None, bool]:
    """Return (figure, declined). Ambiguity yields no figure, never a guess.

    Two DIFFERENT `rwa:` lines mean the worker contradicted itself; that is not a
    number and is not treated as one.
    """
    matches = _RWA_LINE.findall(text or "")
    if not matches:
        return None, False
    if any(m.lower() == "unavailable" for m in matches):
        return None, True
    values = {float(m.replace(",", "")) for m in matches}
    if len(values) != 1:
        return None, False
    return values.pop(), False


def _extract(tasks: Iterable[Any], content_of: Any, agents: Iterable[Any]
             ) -> dict[str, Any]:
    """The one reader. Works on the JSON dump and on a live ``Workflow`` alike,
    because the field names are the same on both — so a live evaluation and a
    post-hoc score cannot disagree about what the episode did."""
    def field(obj: Any, name: str, default: Any = None) -> Any:
        return obj.get(name, default) if isinstance(obj, dict) else getattr(
            obj, name, default)

    allocation: dict[str, str] = {}
    reports: dict[str, float | None] = {}
    declined: list[str] = []
    states: dict[str, str] = {}
    for task in tasks:
        match = _SEGMENT_IN_NAME.search(str(field(task, "name", "")))
        if not match or field(task, "task_class") not in (None, "segment"):
            continue
        segment_id = match.group(1)
        if segment_id not in BY_ID:
            continue
        allocation[segment_id] = field(task, "assigned_agent_id")
        states[segment_id] = str(field(task, "status"))
        text = "\n".join(content_of(rid) or ""
                         for rid in (field(task, "output_resource_ids") or []))
        value, was_declined = parse_report(text)
        reports[segment_id] = value
        if was_declined:
            declined.append(segment_id)

    roster, cards = [], {}
    for agent in agents:
        if field(agent, "agent_type") != "ai":
            continue
        agent_id = field(agent, "agent_id")
        roster.append(agent_id)
        config = field(agent, "config") or {}
        cards[agent_id] = (config.get("agent_description")
                           if isinstance(config, dict)
                           else getattr(config, "agent_description", None))
    return {
        "allocation": allocation,
        "reports": reports,
        "declined": sorted(declined),
        "unallocated": sorted(set(BY_ID) - set(allocation)),
        "states": states,
        "roster": roster,
        "cards": cards,
    }


def read_workflow(workflow: Any) -> dict[str, Any]:
    """Read a LIVE ``Workflow`` object — what a rubric function is handed."""
    resources = getattr(workflow, "resources", {}) or {}
    return {
        "timestep": None,
        **_extract(
            (getattr(workflow, "tasks", {}) or {}).values(),
            lambda rid: getattr(resources.get(rid), "content", None),
            (getattr(workflow, "agents", {}) or {}).values(),
        ),
    }


def read_run(run_dir: str | Path) -> dict[str, Any]:
    """Allocation, reports and roster, from the engine's last workflow dump.

    ``run_dir`` is a ``simulation_outputs/run_*`` directory. The engine writes one
    file per timestep, so a killed run still yields everything up to its last step.
    """
    files = sorted(glob.glob(str(Path(run_dir) / "workflow_outputs" / "*.json")))
    if not files:
        raise FileNotFoundError(f"no workflow_outputs/*.json under {run_dir}")
    workflow = json.loads(Path(files[-1]).read_text())
    resources = workflow.get("resources") or {}
    return {
        "run_dir": str(run_dir),
        "timestep": workflow.get("timestep"),
        **_extract(
            workflow["tasks"].values(),
            lambda rid: (resources.get(rid) or {}).get("content"),
            workflow.get("agents") or [],
        ),
    }


def score_view(run: dict[str, Any], cap: int | None = None) -> dict[str, Any]:
    """The whole picture for one episode, split into the two losses."""
    allocation = {k: v for k, v in run["allocation"].items() if v}
    optimum = best_possible(cap=cap)
    routed = allocation_score(allocation)
    got = achieved(allocation, run["reports"])
    rows = discriminating_segments()
    return {
        **run,
        "best_possible": optimum,
        "allocation_faithful": routed,
        "achieved": got,
        "routing_loss": optimum - routed,
        "execution_loss": routed - got,
        "captured_share": got / optimum if optimum else 0.0,
        "routing_share": routed / optimum if optimum else 0.0,
        "n_discriminating": sum(1 for r in rows if r["discriminates"]),
        "discriminating": rows,
    }


def score_run(run_dir: str | Path, cap: int | None = None) -> dict[str, Any]:
    """Score a finished episode from ``simulation_outputs/run_*``."""
    return score_view(read_run(run_dir), cap)


def score_workflow(workflow: Any, cap: int | None = None) -> dict[str, Any]:
    """Score a LIVE workflow — the entry point the rubric functions use."""
    return score_view(read_workflow(workflow), cap)


def format_run(run_dir: str | Path, cap: int | None = None) -> str:
    """A human-readable episode report. Every number above, none of them invented."""
    r = score_run(run_dir, cap)
    lines = [
        f"run              {r['run_dir']}  (last timestep {r['timestep']})",
        f"roster           {', '.join(r['roster'])}",
        "",
        f"{'segment':9} {'class':10} {'assignee':10} {'could':>7} {'did':>7}  matters",
    ]
    gaps = {row["segment_id"]: row for row in r["discriminating"]}
    for segment in SEGMENTS:
        sid = segment["segment_id"]
        worker = r["allocation"].get(sid)
        could = attainable_score(segment, worker) if worker else 0.0
        did = score_report(segment, r["reports"].get(sid))
        lines.append(
            f"{sid:9} {segment['asset_class']:10} {str(worker):10} "
            f"{could:7.4f} {did:7.4f}  {'yes' if gaps[sid]['discriminates'] else '-'}"
        )
    lines += [
        "",
        f"  best possible        {r['best_possible']:8.4f}",
        f"  the manager's plan   {r['allocation_faithful']:8.4f}   "
        f"routing loss {r['routing_loss']:.4f}",
        f"  actually achieved    {r['achieved']:8.4f}   "
        f"execution loss {r['execution_loss']:.4f}",
        f"  captured             {r['captured_share'] * 100:7.1f}%",
        "",
        f"  segments where the routing choice matters: "
        f"{r['n_discriminating']} of {len(SEGMENTS)}",
    ]
    if r["declined"]:
        lines.append(f"  declined: {', '.join(r['declined'])}")
    if r["unallocated"]:
        lines.append(f"  never allocated: {', '.join(r['unallocated'])}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    import sys
    print(format_run(sys.argv[1]))
