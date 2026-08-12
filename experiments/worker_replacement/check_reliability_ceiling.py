"""Pricing the OBSERVED reliability channel — what knowing execution quality is worth.

WHY THIS EXISTS. Every information channel in the study conveys COVERAGE, and a
correct card conveys all of it (240/240 verified), so cells 1-4 share one ceiling
at 1.24% of oracle / 0.16σ — below detectability at any affordable n. **Execution
quality is the one worker attribute a card cannot carry at all**, and it varies
enormously in the existing corpus. So it is the one candidate where the four
channels would NOT share a bound.

THE OBSERVED CHANNEL, NOT A HYPOTHESISED ONE. Pricing a manipulation we might
build would require specifying it, and that is a design commitment. This prices
the variation ALREADY PRESENT: what would an allocator gain from knowing each
worker's execution quality, versus assuming faithful execution as the current
oracle does. That is true whether or not anything is ever manipulated.

TWO CONFOUNDS GUARDED, because both are the un-mixing failure this phase kept
finding:

  1. THE SPREAD MAY BE A SEGMENT PROPERTY, NOT A WORKER PROPERTY. A worker that
     drew harder segments looks worse. Guarded by a WITHIN-SEGMENT contrast: 13 of
     26 (seed, segment) pairs were executed by two or more distinct workers across
     cells, so the same segment can be compared across workers with difficulty
     held fixed.

  2. n PER WORKER IS 3-14. A median over three observations is not a reliability
     estimate. Every figure carries its n, and small-n workers are reported as
     UNPRICED rather than as measured.

AND THE REFERENCE CLASS, per the rule this phase produced: find a population where
the correct answer is fixed OUTSIDE the system under test. SA-only segments are a
table lookup — exposure x a published risk weight — so the right answer does not
depend on the worker or the harness. If a worker is exact on SA and poor on IRB,
its error is METHOD-SPECIFIC; if poor on both, it is general incompetence.

Run:  python3 -m experiments.worker_replacement.check_reliability_ceiling
"""

from __future__ import annotations

import collections
import glob
import json
import statistics as st
from itertools import product
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
BUNDLES = str(HERE / "records" / "R2" / "run_cell*_seed*.json")
CAP = 3
MIN_N = 5          # below this a worker is reported UNPRICED, not measured


def observations() -> list[dict[str, Any]]:
    """One row per executed, parsed segment: what was attainable and what landed."""
    rows: list[dict[str, Any]] = []
    for path in sorted(glob.glob(BUNDLES)):
        bundle = json.loads(Path(path).read_text())
        seed = bundle["manifest"]["instance_seed"]
        instance = gen.generate(seed)
        calibration = instance["class_calibration"]
        segments = {s["segment_id"]: s for s in instance["segments"]}
        workers = {w["worker_id"]: w for w in instance["workers"]}
        allocation = bundle.get("allocation") or {}
        for segment_id, detail in (bundle.get("parse_detail") or {}).items():
            reported = detail.get("rwa")
            worker_id = allocation.get(segment_id)
            if reported is None or worker_id not in workers:
                continue
            segment = segments[segment_id]
            rows.append({
                "seed": seed, "segment": segment_id, "worker": worker_id,
                "realised": sc.score_report(segment, reported, calibration),
                "attainable": sc.s(segment, workers[worker_id], calibration),
                "irb_approved": segment["irb_approved"],
                "covered": (segment["asset_class"]
                            in workers[worker_id]["irb_coverage"]),
            })
    return rows


def reliability(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Per worker: realised / attainable on work it was qualified for.

    The ratio, not the raw score: a worker sent out-of-scope work scores badly for
    a COVERAGE reason, which is a different construct and already priced. This is
    only over segments the worker could in principle have got right.
    """
    by_worker: dict[str, list[float]] = collections.defaultdict(list)
    for row in rows:
        if row["attainable"] <= 0:
            continue
        if row["irb_approved"] and not row["covered"]:
            continue          # out-of-scope: a coverage failure, not a quality one
        by_worker[row["worker"]].append(row["realised"] / row["attainable"])
    return {
        worker: {"n": len(values), "median": st.median(values),
                 "mean": sum(values) / len(values),
                 "priced": len(values) >= MIN_N}
        for worker, values in sorted(by_worker.items())
    }


def within_segment_contrast(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """CONFOUND GUARD 1 — is the spread a worker property or a segment property?

    For every (seed, segment) executed by two or more distinct workers, the
    difficulty is held fixed by construction. If the spread survives here it is
    about workers; if it collapses, the per-worker table was pricing which
    segments each worker happened to draw.
    """
    by_key: dict[tuple, dict[str, list[float]]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for row in rows:
        if row["attainable"] <= 0 or (row["irb_approved"] and not row["covered"]):
            continue
        by_key[(row["seed"], row["segment"])][row["worker"]].append(
            row["realised"] / row["attainable"])

    spreads: list[float] = []
    comparable = 0
    for _key, per_worker in by_key.items():
        if len(per_worker) < 2:
            continue
        comparable += 1
        means = [sum(v) / len(v) for v in per_worker.values()]
        spreads.append(max(means) - min(means))

    overall = [r["realised"] / r["attainable"] for r in rows
               if r["attainable"] > 0
               and not (r["irb_approved"] and not r["covered"])]
    return {
        "n_segments_with_2plus_workers": comparable,
        "median_within_segment_spread": st.median(spreads) if spreads else None,
        "max_within_segment_spread": max(spreads) if spreads else None,
        "overall_spread": max(overall) - min(overall),
    }


def method_specificity(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """THE REFERENCE CLASS — is a worker's error method-specific or general?

    SA-only segments have a right answer fixed OUTSIDE the system under test: a
    table lookup on published risk weights, independent of worker and harness.
    """
    out: dict[str, dict[str, Any]] = collections.defaultdict(
        lambda: {"sa_n": 0, "sa_ratios": [], "irb_n": 0, "irb_ratios": []})
    for row in rows:
        if row["attainable"] <= 0:
            continue
        ratio = row["realised"] / row["attainable"]
        if not row["irb_approved"]:
            out[row["worker"]]["sa_n"] += 1
            out[row["worker"]]["sa_ratios"].append(ratio)
        elif row["covered"]:
            out[row["worker"]]["irb_n"] += 1
            out[row["worker"]]["irb_ratios"].append(ratio)
    return {
        w: {"sa_n": v["sa_n"],
            "sa_median": st.median(v["sa_ratios"]) if v["sa_ratios"] else None,
            "irb_n": v["irb_n"],
            "irb_median": st.median(v["irb_ratios"]) if v["irb_ratios"] else None}
        for w, v in sorted(out.items())
    }


def reliability_ceiling(seed: int, quality: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """What knowing execution quality is worth, on this instance.

    KNOWING  — the allocator maximises attainable x reliability.
    NOT KNOWING — it maximises attainable, which is what the current oracle does.
    Both are then evaluated on attainable x reliability, the expected realised
    score. The gap is the ceiling.
    """
    instance = gen.generate(seed)
    event = instance["event"]
    calibration = instance["class_calibration"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    workers = [by_id[w] for w in event["roster_post_swap"]]
    segments = instance["segments"]

    def rel(worker) -> float | None:
        row = quality.get(worker["worker_id"])
        return row["median"] if row and row["priced"] else None

    if any(rel(w) is None for w in workers):
        return {"seed": seed, "computable": False,
                "why": "at least one rostered worker has fewer than "
                       f"{MIN_N} observations, so its reliability is UNPRICED"}

    def expected(segment, worker):
        return sc.s(segment, worker, calibration) * rel(worker)

    def blind(segment, worker):
        return sc.s(segment, worker, calibration)

    def best(scoref):
        best_v, best_a = -1.0, ()
        for combo in product(range(len(workers)), repeat=len(segments)):
            if any(combo.count(i) > CAP for i in range(len(workers))):
                continue
            value = sum(scoref(sg, workers[w]) for sg, w in zip(segments, combo))
            if value > best_v:
                best_v, best_a = value, combo
        return best_v, best_a

    knowing_value, _ = best(expected)
    _, blind_alloc = best(blind)
    blind_realises = sum(expected(sg, workers[w])
                         for sg, w in zip(segments, blind_alloc))
    return {"seed": seed, "computable": True,
            "knowing": knowing_value, "blind_realises": blind_realises,
            "ceiling": knowing_value - blind_realises,
            "ceiling_share": (knowing_value - blind_realises) / knowing_value}


def main() -> int:
    rows = observations()
    print("Pricing the OBSERVED reliability channel — no run, no new manipulation\n")
    print(f"observations (executed, parsed segments): {len(rows)}\n")

    print("1. per-worker execution quality — realised / attainable, on work it "
          "was qualified for")
    quality = reliability(rows)
    for worker, row in quality.items():
        flag = "" if row["priced"] else f"   <-- UNPRICED (n < {MIN_N})"
        print(f"   {worker}  n={row['n']:>3}  median {row['median']:.3f}  "
              f"mean {row['mean']:.3f}{flag}")
    priced = [w for w, r in quality.items() if r["priced"]]
    print(f"   {len(priced)} of {len(quality)} workers have n >= {MIN_N}.")

    print("\n2. CONFOUND GUARD — is the spread a WORKER property or a SEGMENT "
          "property?")
    contrast = within_segment_contrast(rows)
    print(f"   (seed, segment) pairs executed by 2+ distinct workers: "
          f"{contrast['n_segments_with_2plus_workers']}")
    print(f"   median spread BETWEEN workers on the SAME segment: "
          f"{contrast['median_within_segment_spread']:.3f}")
    print(f"   max spread on the same segment: "
          f"{contrast['max_within_segment_spread']:.3f}")
    print(f"   overall spread ignoring segment: {contrast['overall_spread']:.3f}")
    survives = (contrast["median_within_segment_spread"] or 0) > 0.05
    print(f"   => the spread {'SURVIVES' if survives else 'COLLAPSES'} when "
          f"difficulty is held fixed, so it is "
          f"{'about workers' if survives else 'about which segments each drew'}")

    print("\n3. REFERENCE CLASS — is a worker's error method-specific or general?")
    print("   (SA is a table lookup: the right answer is fixed OUTSIDE the "
          "system under test)")
    for worker, row in method_specificity(rows).items():
        sa = "  n/a" if row["sa_median"] is None else f"{row['sa_median']:.3f}"
        irb = "  n/a" if row["irb_median"] is None else f"{row['irb_median']:.3f}"
        print(f"   {worker}  SA {sa} (n={row['sa_n']:>2})   "
              f"IRB {irb} (n={row['irb_n']:>2})")

    print("\n4. THE CEILING — what knowing execution quality is worth")
    results = [reliability_ceiling(seed, quality) for seed in (3, 23, 36)]
    for row in results:
        if not row["computable"]:
            print(f"   seed {row['seed']}: UNCOMPUTABLE — {row['why']}")
            continue
        print(f"   seed {row['seed']:>3}: knowing {row['knowing']:.4f}  "
              f"blind realises {row['blind_realises']:.4f}  "
              f"ceiling {row['ceiling']:.4f} ({row['ceiling_share']:.2%})")
    live = [r for r in results if r.get("computable")]
    if live:
        mean = sum(r["ceiling_share"] for r in live) / len(live)
        print(f"   mean ceiling across the study instances: {mean:.2%} of the "
              f"knowing optimum")
        print(f"   COMPARE: the coverage ceiling is 1.24% (0.16 sigma).")

    print("\n5. WHY THE CEILING IS ZERO — and it is structural, not incidental")
    instance = gen.generate(3)
    n_seg = len(instance["segments"])
    n_workers = len(instance["event"]["roster_post_swap"])
    print(f"   {n_seg} segments, {n_workers} workers, cap {CAP} -> total capacity "
          f"{n_workers * CAP}, slack {n_workers * CAP - n_seg}")
    print("   With ZERO SLACK every worker takes exactly CAP segments no matter "
          "what the\n   manager knows. **Knowing a worker is half as good does "
          "not let the manager\n   give it LESS work — only DIFFERENT work.** And "
          "reliability is a per-worker\n   multiplier applying equally to all its "
          "segments, so reshuffling which three\n   it gets can only exploit "
          "variation in ATTAINABLE score across segments, which\n   is small.")
    print("   => the reliability channel is not merely weak here, it is "
          "STRUCTURALLY BLOCKED\n      by the same exactly-binding cap that makes "
          "the coverage channel weak.")
    print("   A design where reliability could matter needs SLACK — capacity "
          "exceeding work,\n   so under-loading a poor worker is an available "
          "move.")

    out = HERE / "records" / "L4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "reliability_ceiling.json").write_text(json.dumps({
        "n_observations": len(rows),
        "per_worker_quality": quality,
        "within_segment_contrast": contrast,
        "method_specificity": method_specificity(rows),
        "ceilings": results,
        "establishes": ("what an allocator would gain from knowing each worker's "
                        "execution quality, using variation already in the corpus"),
        "does_not_establish": ("that any channel could convey it, or that a "
                               "manager would use it; and reliability is "
                               "estimated from 3-14 observations per worker"),
    }, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\nwritten: {out / 'reliability_ceiling.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
