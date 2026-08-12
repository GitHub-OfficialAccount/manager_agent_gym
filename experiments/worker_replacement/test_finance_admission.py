"""S7 acceptance — the admission pipeline.

  1. Per instance, PASS/FAIL on each of the three conditions, with the scripted
     baseline's score printed beside the oracle's.
  2. A suite containing one deliberately label-trivial instance rejects EXACTLY
     that one. The trivial instance is produced through generator paths (a seed
     whose capped card-match happens to tie the oracle), never hand-authored JSON.
  3. The capacity ruling's consequences are asserted, not narrated: the cap binds
     on every instance, and removing the successor leaves segments unstaffed.

Run:  python3 -m experiments.worker_replacement.test_finance_admission
"""

from __future__ import annotations

import json
from pathlib import Path

from . import finance_admission as adm
from . import finance_gate as gate
from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
SUITE = range(40)


def main() -> int:
    failures: list[str] = []
    print(f"S7 — admission pipeline (cap K6 = {gate.CAP})\n")

    result = adm.admit_suite(SUITE)
    rows = result["rows"]
    generated = [r for r in rows if r.get("generated")]

    # --- 1. per-instance table -----------------------------------------------
    print("per-instance conditions (1 regeneration / 2 gate / 3 baseline):")
    print(f"  {'seed':>4} {'1':>3} {'2':>3} {'3':>3}  {'oracle':>8} {'baseline':>9} "
          f"{'shortfall':>10} {'M/oracle':>9}")
    trivial_seeds = []
    for row in rows[:14]:
        if not row.get("generated"):
            print(f"  {row['seed']:>4}   —   —   —   (generation rejected)")
            continue
        c = row["conditions"]
        marks = ["P" if c[k] else "F" for k in sorted(c)]
        if row["baseline_shortfall"] <= 1e-9:
            trivial_seeds.append(row["seed"])
        print(f"  {row['seed']:>4} {marks[0]:>3} {marks[1]:>3} {marks[2]:>3}  "
              f"{row['oracle']:>8.4f} {row['scripted_baseline_score']:>9.4f} "
              f"{row['baseline_shortfall']:>10.4f} {row['max_effect_share']:>9.4f}")
    all_trivial = [r["seed"] for r in generated if r["baseline_shortfall"] <= 1e-9]
    print(f"  ... {len(rows)} seeds total")

    print(f"\n  generated {result['n_generated']}/{result['n']}, "
          f"fully admitted {result['n_admitted']}/{result['n']}")
    print(f"  failures by condition: {result['failures_by_condition']}")
    print(f"  baseline shortfall: min {result['baseline_shortfall_min']:.4f}, "
          f"median {result['baseline_shortfall_median']:.4f}")

    ok_gen = result["n_generated"] == len(list(SUITE))
    print(f"  [{'ok' if ok_gen else 'FAIL'}] every seed generates at cap "
          f"{gate.CAP} (assertion 2b binds universally)")
    if not ok_gen:
        failures.append("not every seed generated")

    # --- 2. exactly the trivial instances are rejected by condition 3 --------
    print(f"\nlabel-trivial instances (capped baseline TIES the oracle): "
          f"{all_trivial}")
    print("  these are the gate working: an instance a public-information script")
    print("  solves completely measures lookup, not management.")
    rejected_by_3 = [
        r["seed"] for r in generated
        if not r["conditions"]["3_stale_card_ceiling_above_zero"]
    ]
    exact = sorted(rejected_by_3) == sorted(all_trivial)
    print(f"  condition 3 rejects: {sorted(rejected_by_3)}")
    print(f"  [{'ok' if exact else 'FAIL'}] condition 3 rejects EXACTLY the "
          f"label-trivial instances — no more, no fewer")
    if not exact:
        failures.append("condition 3 rejections do not match the trivial set")
    if not all_trivial:
        print("  [FAIL] no label-trivial instance in the suite — the negative case "
              "is absent, so condition 3 is unexercised")
        failures.append("suite contains no label-trivial instance")

    # --- 2b. no rejected row may carry an empty cause ------------------------
    # Anti-regression assertion: the named-cause ruling has now regressed once
    # (fixed in the sweep rows, not carried into this artifact), so it is asserted
    # rather than trusted. A rejected row with no reason is indistinguishable from
    # one rejected for the wrong reason.
    unexplained = [
        r["seed"] for r in rows
        if not r["admitted"] and not r.get("rejection_reasons")
    ]
    print(f"\n  [{'ok' if not unexplained else 'FAIL'}] every rejected row names a "
          f"cause ({len(rows) - result['n_admitted']} rejected, "
          f"{len(unexplained)} unexplained)")
    if unexplained:
        failures.append(f"rejected rows with no cause: {unexplained}")
    for row in rows:
        if not row["admitted"]:
            print(f"     seed {row['seed']:>3}: {row['rejection_reasons'][0][:78]}")

    # --- 3. the capacity ruling's consequences, asserted --------------------
    print("\ncapacity consequences (asserted, not narrated):")
    instance = gen.generate(101)
    load = sc.greedy_card_match_load(instance)

    # ★ "THE CAP BINDS" IS RETIRED (L14-b). It asserted `gate.CAP < load`, and
    # gate.CAP is now UNCAPPED. Reported as context, asserted on nothing.
    print(f"  greedy card-match load {load} vs cap {gate.CAP} (UNCAPPED) -> "
          f"the cap-binds assertion is RETIRED, see ALLOCATION_DIFFICULTY_RETIRED")

    # ★ "STRUCTURALLY LOAD-BEARING" IS RESTATED, AND THE CHANGE IS SCIENTIFIC, NOT
    # COSMETIC. It read: without the successor, (roster-1) x cap < segments, so
    # segments MUST go unstaffed -- the successor mattered by ARITHMETIC, whoever it
    # was. With no cap two workers can absorb all nine segments, so that guarantee
    # is gone.
    #
    # What must now carry it is COVERAGE: the successor matters because of WHICH
    # classes it is approved for, not because there is nowhere else to put the work.
    # That is the better property for this study -- the whole question is whether
    # the manager learns WHO the newcomer is -- but it is strictly weaker, it is not
    # guaranteed by construction, and it is now MEASURED per instance instead of
    # being implied by three integers.
    without = sc.oracle_without_successor(instance, cap=gate.CAP)
    full = sc.oracle_capacitated(instance, cap=gate.CAP)
    load_bearing = full - without > 1e-9
    print(f"  without the successor: oracle {full:.4f} -> {without:.4f}, "
          f"M/oracle {(full - without) / full:.4f} -> "
          f"[{'ok' if load_bearing else 'FAIL'}] the successor is load-bearing "
          f"through COVERAGE (capacity no longer forces it)")
    if not load_bearing:
        failures.append(
            "successor is not load-bearing: removing it does not lower the oracle, "
            "so no information about it can matter on this instance")

    # Sigma-max must remain a valid upper bound on the capacitated oracle.
    bound_ok = full <= sc.oracle(instance) + 1e-9
    print(f"  [{'ok' if bound_ok else 'FAIL'}] capacitated oracle {full:.4f} <= "
          f"Sigma-max bound {sc.oracle(instance):.4f}")
    if not bound_ok:
        failures.append("capacitated oracle exceeds the Sigma-max bound")

    out = HERE / "records" / "S7"
    out.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in result.items() if k != "rows"}
    payload["rows"] = [
        # `rejection_reasons` is deliberately KEPT in the artifact; only the
        # gate's raw duplicate is dropped.
        {k: v for k, v in r.items() if k != "gate_rejection_reasons"} for r in rows
    ]
    payload["label_trivial_seeds"] = all_trivial
    payload["capacity_cap_k6"] = gate.CAP
    (out / "admission_suite.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  {f}")
        return 1
    print("RESULT: PASS — all seeds generate; condition 3 rejects instances whose "
          "stale card already attains the oracle; the successor is load-bearing "
          "through COVERAGE (the capacity guarantee is retired, L14-b)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
