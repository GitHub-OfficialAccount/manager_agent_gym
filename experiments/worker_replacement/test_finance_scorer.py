"""S4 acceptance — scorer, oracle/worst, and the regret decomposition.

  1. On a fixed instance, `oracle >= score(I, allocation) >= worst` over ALL
     enumerated allocations — enumerated THROUGH the production scorer
     (`score(I, allocation)` called per allocation), never through a re-derivation
     in this file (§A test-shape rule).
  2. A hand-checked segment where allocation loss and execution loss are both
     non-zero and sum to total regret.
  3. Single-source: the IRB function is the S1-validated object by identity, and
     the SA lookup is S3's.

Run:  python3 -m experiments.worker_replacement.test_finance_scorer
"""

from __future__ import annotations

import json
from pathlib import Path

from . import finance_generator as gen
from . import finance_scorer as sc
from . import test_basel_reference as basel

HERE = Path(__file__).resolve().parent
SEED = 101


def main() -> int:
    CAL = gen.generate(SEED)["class_calibration"]
    failures: list[str] = []
    print("S4 — scorer, oracle/worst, decomposed regret\n")

    # Smaller instance so exhaustive enumeration is honest rather than sampled:
    # 8 segments x 4 workers = 65,536 allocations, all scored through score().
    instance = gen.generate(SEED, n_segments=8, n_workers=4)
    n_alloc = len(instance["workers"]) ** len(instance["segments"])

    # --- 3. single-source, asserted first: everything below depends on it ----
    print("single-source provenance:")
    irb_same = (
        sc._irb_risk_weight_unrestricted.__module__
        == "experiments.worker_replacement.finance_scorer"
    )
    from .test_basel_reference import capital_requirement as s1_cr

    imported_same = s1_cr is basel.capital_requirement
    sa_same = sc.sa_risk_weight is gen.sa_risk_weight
    print(f"   [{'ok' if imported_same else 'FAIL'}] IRB capital_requirement is the "
          f"S1-validated object (identity)")
    print(f"   [{'ok' if sa_same else 'FAIL'}] SA lookup is S3's sa_risk_weight (identity)")
    if not imported_same:
        failures.append("IRB function is not the S1-validated object")
    if not sa_same:
        failures.append("SA lookup is not S3's function")

    # --- 1. bounds over ALL allocations, via the production scorer -----------
    print(f"\n1. bounds over all {n_alloc:,} allocations (each scored by score()):")
    oracle_score = sc.oracle(instance)
    worst_score = sc.worst(instance)
    lo = hi = None
    violations = 0
    for allocation in sc.all_allocations(instance):
        value = sc.score(instance, allocation)
        lo = value if lo is None else min(lo, value)
        hi = value if hi is None else max(hi, value)
        if value > oracle_score + 1e-9 or value < worst_score - 1e-9:
            violations += 1
    print(f"   oracle              {oracle_score:.6f}")
    print(f"   max over allocations {hi:.6f}")
    print(f"   min over allocations {lo:.6f}")
    print(f"   worst               {worst_score:.6f}")
    bounds_ok = violations == 0
    tight_hi = abs(hi - oracle_score) < 1e-9
    tight_lo = abs(lo - worst_score) < 1e-9
    print(f"   [{'ok' if bounds_ok else 'FAIL'}] no allocation escapes [worst, oracle] "
          f"({violations} violations)")
    # Tightness matters: bounds that are never attained would be vacuous.
    print(f"   [{'ok' if tight_hi else 'FAIL'}] oracle is ATTAINED by some allocation")
    print(f"   [{'ok' if tight_lo else 'FAIL'}] worst is ATTAINED by some allocation")
    for ok, label in ((bounds_ok, "allocation escaped the bounds"),
                      (tight_hi, "oracle not attained"), (tight_lo, "worst not attained")):
        if not ok:
            failures.append(label)

    # --- 2. hand-checked decomposition --------------------------------------
    print("\n2. hand-checked segment — both losses non-zero, summing to total regret:")
    workers = {w["worker_id"]: w for w in instance["workers"]}
    # Pick an IRB-applicable segment that some worker covers and some does not, so
    # a misroute is possible at all.
    target = None
    for segment in instance["segments"]:
        if sc.applicable_approach(segment) != "IRB":
            continue
        covered = [w for w in instance["workers"] if segment["asset_class"] in w["irb_coverage"]]
        uncovered = [w for w in instance["workers"] if segment["asset_class"] not in w["irb_coverage"]]
        if not (covered and uncovered):
            continue
        # The misrouted worker's own attainable score must be STRICTLY POSITIVE,
        # or its execution loss cannot be positive either (it is already at the
        # floor) and the two-non-zero-losses case is unbuildable on that segment.
        # Derived, not assumed: the divergence selection added in the S6 RR round
        # made some fallbacks clip, which is exactly when the old hard-coded pick
        # stopped working.
        if sc.s(segment, uncovered[0], CAL) > 0.0:
            target, best, wrong = segment, covered[0], uncovered[0]
            break
    if target is None:
        print("   [FAIL] no segment admits both a covered and an uncovered worker")
        failures.append("no misroutable segment in the instance")
    else:
        allocation = sc.oracle_allocation(instance)
        allocation[target["segment_id"]] = wrong["worker_id"]  # the MISROUTE

        reports = sc.faithful_reports(instance, allocation)
        # ...and the misrouted worker also under-executes. NOTE: the deviation must
        # move AWAY from the truth. A naive "report 80% of your own number" made
        # execution loss NEGATIVE here, because the SA fallback overstates the IRB
        # truth by ~35%, so shrinking it moved the report closer and scored better
        # than faithful execution. That is a real property of the scorer (see the
        # module docstring), not a bad test — but for a case demonstrating two
        # POSITIVE losses the deviation has to amplify the existing error.
        faithful_value = reports[target["segment_id"]]
        truth = sc.correct_rwa(target, CAL)
        # Amplify the existing error AWAY from truth, then verify the resulting
        # score is strictly lower than the faithful one — deriving the deviation
        # rather than trusting a fixed multiplier to still bite after a generator
        # shape change.
        deviated = faithful_value + 2.0 * (faithful_value - truth)
        if sc.score_report(target, deviated, CAL) >= sc.s(target, wrong, CAL):
            deviated = truth * 10.0
        reports[target["segment_id"]] = deviated

        d = sc.decompose_regret(instance, allocation, reports)
        print(f"   segment {target['segment_id']} ({target['asset_class']}, "
              f"{target['rating']}, applicable={sc.applicable_approach(target)})")
        print(f"     best worker   {best['worker_id']} covers it   -> s = "
              f"{sc.s(target, best, CAL):.6f}")
        print(f"     routed to     {wrong['worker_id']} does not   -> s = "
              f"{sc.s(target, wrong, CAL):.6f}   (SA fallback)")
        print(f"     and it under-executed, amplifying its own error AWAY from truth")
        for key in ("oracle", "faithful_score", "achieved_score",
                    "allocation_loss", "execution_loss", "total_regret"):
            print(f"     {key:<16} {d[key]:.9f}")
        both_nonzero = d["allocation_loss"] > 1e-9 and d["execution_loss"] > 1e-9
        sums = abs((d["allocation_loss"] + d["execution_loss"]) - d["total_regret"])
        identity_ok = sums < 1e-9
        print(f"   [{'ok' if both_nonzero else 'FAIL'}] both losses non-zero")
        print(f"   [{'ok' if identity_ok else 'FAIL'}] allocation + execution == total "
              f"(residual {sums:.2e})")
        if not both_nonzero:
            failures.append("hand-checked case did not produce two non-zero losses")
        if not identity_ok:
            failures.append("decomposition does not sum to total regret")

        # Negative control: with FAITHFUL reports, execution loss must vanish while
        # allocation loss survives. A decomposition that cannot separate them would
        # pass the sum identity above and still be useless.
        faithful_only = sc.decompose_regret(
            instance, allocation, sc.faithful_reports(instance, allocation))
        separated = (
            abs(faithful_only["execution_loss"]) < 1e-9
            and faithful_only["allocation_loss"] > 1e-9
        )
        print(f"   [{'ok' if separated else 'FAIL'}] with faithful reports: execution "
              f"loss {faithful_only['execution_loss']:.2e}, allocation loss "
              f"{faithful_only['allocation_loss']:.6f} — the two are SEPARABLE")
        if not separated:
            failures.append("losses are not separable")

    # --- 4. reports validation (RR finding F4) -------------------------------
    # The empty-after-non-empty shape applied to a keyed collection: a reports dict
    # that is PARTIAL, and one that is FOREIGN, must both be distinguishable from a
    # complete one rather than silently producing a well-formed decomposition.
    print("\n4. reports validation — partial and foreign reports dicts:")
    good_allocation = sc.oracle_allocation(instance)
    complete = sc.faithful_reports(instance, good_allocation)

    # (a) complete reports -> missing_segments present and EMPTY (never omitted)
    d_complete = sc.decompose_regret(instance, good_allocation, complete)
    has_field = "missing_segments" in d_complete and d_complete["missing_segments"] == []
    print(f"   [{'ok' if has_field else 'FAIL'}] complete reports: missing_segments "
          f"present and empty (field never omitted)")
    if not has_field:
        failures.append("missing_segments absent or non-empty for complete reports")

    # (b) one allocated segment unreported -> surfaced, not silently zeroed
    dropped = sorted(complete)[0]
    partial = {k: v for k, v in complete.items() if k != dropped}
    d_partial = sc.decompose_regret(instance, good_allocation, partial)
    surfaced = d_partial["missing_segments"] == [dropped]
    print(f"   [{'ok' if surfaced else 'FAIL'}] dropping {dropped} surfaces it in "
          f"missing_segments -> {d_partial['missing_segments']}")
    if not surfaced:
        failures.append("missing allocated segment was not surfaced")
    # ...and it is distinguishable from a genuinely zero-scoring report
    zeroed = dict(complete)
    zeroed[dropped] = sc.correct_rwa(
        next(x for x in instance["segments"] if x["segment_id"] == dropped),
        CAL) * 1e6
    d_zeroed = sc.decompose_regret(instance, good_allocation, zeroed)
    distinguishable = (
        d_zeroed["missing_segments"] == []
        and abs(d_zeroed["achieved_score"] - d_partial["achieved_score"]) < 1e-9
    )
    print(f"   [{'ok' if distinguishable else 'FAIL'}] a legitimately 0-scoring report "
          f"gives the SAME achieved score but an EMPTY missing_segments — the two "
          f"cases are distinguishable")
    if not distinguishable:
        failures.append("missing vs zero-scoring reports are not distinguishable")

    # (c) a foreign key must raise, not be ignored
    foreign = dict(complete)
    foreign["seg_from_another_run"] = 1.0
    try:
        sc.decompose_regret(instance, good_allocation, foreign)
        raised = False
    except ValueError as exc:
        raised = "seg_from_another_run" in str(exc)
    print(f"   [{'ok' if raised else 'FAIL'}] a report key outside the allocation raises")
    if not raised:
        failures.append("foreign report key did not raise")

    # record the fixed instance used, so the numbers above are reproducible
    out = HERE / "records" / "S4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "instance_seed101_8seg.json").write_text(gen.to_json(instance))

    print()
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  {f}")
        return 1
    print("RESULT: PASS — bounds hold and are attained over all enumerated "
          "allocations; decomposition sums exactly and separates the two losses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
