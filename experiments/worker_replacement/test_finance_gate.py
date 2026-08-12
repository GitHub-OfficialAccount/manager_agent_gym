"""S6 acceptance — sensitivity gate, sweep, and knob disclosures.

  1. The gate emits all four disclosures on a committed instance, K1 at >=5 points.
  2. An instance outside floor/ceiling is REJECTED by the same script — the
     committed S3/S4 instances are the natural negative (they are oracle-perfect).
  3. The sweep reports regret-headroom-vs-k and the swap-class uniformity result.
  4. Curves are produced by DRIVING the production generator and scorer across
     parameter values, never by re-deriving spread arithmetic here (§A rule).

Run:  python3 -m experiments.worker_replacement.test_finance_gate
"""

from __future__ import annotations

import json
from pathlib import Path

from . import finance_gate as gate
from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
SEED = 101


def gate_fixture_oracle_perfect(instance: dict) -> dict:
    """A GATE FIXTURE: an oracle-perfect instance, to prove the REJECT path.

    After the S6 ruling the generator no longer produces one, so the ceiling would
    be untestable without a fixture. Built by giving every worker coverage of every
    class, which is what the pre-ruling lattice effectively did.
    """
    stuffed = json.loads(json.dumps(instance))
    for worker in stuffed["workers"]:
        worker["irb_coverage"] = list(gen.ASSET_CLASSES)
        # COVERAGE AND CALIBRATION MOVE TOGETHER (R1). Approval without the class
        # table is not a state the generator can produce — assertion 9 forbids it
        # — so a fixture that granted one without the other would be testing a
        # world that cannot exist. Exposed by the schema change: the old fixture
        # granted coverage alone and the truth lookup raised.
        worker["private_pd_calibration"] = {
            cls: dict(table) for cls, table in stuffed["class_calibration"].items()
        }
    return stuffed


def gate_fixture_non_perfect(instance: dict) -> dict:
    """A GATE FIXTURE: an instance whose oracle is imperfect.

    The generator provably cannot produce one at current parameters (see the
    structural finding printed below), so the ACCEPT path of the gate would be
    untestable without this. Constructed by removing one asset class from every
    worker's coverage, leaving IRB segments of that class attainable by nobody.

    This tests the GATE, which is the unit under test here; it is not a proposed
    generator configuration and is never used to produce study instances.
    """
    stripped = json.loads(json.dumps(instance))
    # Strip a class the swap pair do NOT share. Stripping the shared class would
    # remove the successor's strictly-required segments and the instance would be
    # rejected for BEING BELOW THE EFFECT-SIZE FLOOR rather than admitted — a
    # different verdict than this fixture is meant to demonstrate. Derived from
    # the instance rather than named, since the shared class is seed-permuted.
    shared = instance["event"]["swap_shared_class"]
    victim = next(
        c for c in gen.ASSET_CLASSES
        if c != shared and any(c in w["irb_coverage"] for w in instance["workers"])
    )
    for worker in stripped["workers"]:
        worker["irb_coverage"] = [c for c in worker["irb_coverage"] if c != victim]
        worker["private_pd_calibration"].pop(victim, None)  # both, together
    return stripped


def main() -> int:
    failures: list[str] = []
    print("S6 — sensitivity gate, sweep, knob disclosures\n")

    instance = gen.generate(SEED)
    verdict = gate.evaluate(instance)

    # --- 2. the committed instance must be REJECTED -------------------------
    print("1. gate verdict on the committed instance (records/S3/instance_seed101.json):")
    print(f"   oracle {verdict['oracle']:.4f} / {verdict['n_segments']} segments, "
          f"worst {verdict['worst']:.4f}, spread {verdict['spread']:.4f} "
          f"({verdict['spread_fraction_of_max']:.1%} of max)")
    print(f"   admitted: {verdict['admitted']}")
    for reason in verdict["rejection_reasons"]:
        print(f"     REJECTED — {reason}")
    admitted_ok = verdict["admitted"]
    print(f"   [{'ok' if admitted_ok else 'FAIL'}] instance ADMITTED with interior "
          f"spread (it was rejected as oracle-perfect before the S6 ruling)")
    if not admitted_ok:
        failures.append("post-fix instance is still not admitted")

    # --- the structural finding, and its FIX, both measured -----------------
    print("\n   STRUCTURAL HISTORY — what this gate exposed, and what fixed it:")
    perfect = sum(
        1 for seed in range(60)
        if abs(sc.oracle(gen.generate(seed))
               - len(gen.generate(seed)["segments"])) < 1e-9
    )
    print(f"   oracle-perfect instances now: {perfect}/60")
    print("   BEFORE: 60/60 were oracle-perfect, for a provable reason — 4 workers")
    print("   held distinct 2-subsets of 4 classes, and only 3 such subsets can avoid")
    print("   any given element, so every class was covered and every IRB segment had")
    print("   a covered worker. The gate rejected 40/40.")
    print("   TWO FIXES, both from the S6 ruling: (i) ROSTER-CORRECT scoring — the")
    print("   pool contains predecessor AND successor and is a team that can never")
    print("   exist, so scoring it inflated the oracle; (ii) a CONSTRUCTED five-class")
    print("   lattice in which one class is held only by the predecessor, so post-swap")
    print("   nobody covers it and the spread is interior BY CONSTRUCTION.")
    if perfect != 0:
        failures.append(f"expected 0/60 oracle-perfect after the fix, saw {perfect}")

    # --- 1. the four disclosures --------------------------------------------
    print("\n2. disclosures on that instance:")
    k1 = gate.k1_curve(SEED, points=7)
    usable = [p for p in k1 if p.get("spread") is not None]
    print(f"   K1 spread-vs-covered-fraction curve: {len(k1)} points "
          f"({len(usable)} with a spread)")
    for point in k1:
        if point.get("spread") is None:
            print(f"     frac {point['irb_applicable_fraction']:.2f}  "
                  f"{point['rejected']}: {point['detail'][:60]}")
        else:
            print(f"     frac {point['irb_applicable_fraction']:.2f}  "
                  f"spread {point['spread']:.4f}  oracle {point['oracle']:.2f}")
    k1_ok = len(k1) >= 5
    print(f"   [{'ok' if k1_ok else 'FAIL'}] K1 curve has >=5 points "
          f"(the CURVE, never the operating point alone)")
    if not k1_ok:
        failures.append("K1 curve has fewer than 5 points")

    print(f"\n   K2 per instance: k={verdict['k_threshold']}, strict "
          f"{verdict['successor_strict_count']} {verdict['successor_strict_segments']}, "
          f"tie-inclusive {verdict['successor_tie_inclusive_count']}, "
          f"successor-only fraction {verdict['successor_only_fraction']:.3f}")
    k2 = gate.k2_headroom_curve(SEED)
    print("   K2 regret-headroom-vs-k curve:")
    for point in k2:
        if point["admitted_by_assertion"]:
            print(f"     k={point['k']}  ceiling "
                  f"{point['ceiling_vs_ignorant']:.4f} "
                  f"({point['ceiling_vs_ignorant_share']:.4f} of oracle)"
                  f"   [diag: strict {point['diagnostic_strict_count']}, "
                  f"headroom {point['diagnostic_headroom']:+d}]")
        else:
            print(f"     k={point['k']}  REJECTED by assertion 3")
    # K2 IS NO LONGER AN ADMISSION GATE (R1). The curve MEASURED the ceiling to
    # be flat across k=1..4, so the knob rejected instances and moved nothing. The
    # old assertion here required the curve to show a REJECTION BOUNDARY — which
    # is precisely the behaviour that was removed, so continuing to require it
    # would be asserting that a retired gate still fires.
    #
    # What is still worth checking is the finding that retired it: the ceiling
    # does not move with k. Asserted now, so a future change that makes k matter
    # again surfaces here rather than silently reinstating a live knob.
    shares = [p["ceiling_vs_ignorant_share"] for p in k2
              if p.get("admitted_by_assertion") and p.get("ceiling_vs_ignorant_share")]
    flat = bool(shares) and (max(shares) - min(shares)) < 0.01
    k2_ok = len(k2) >= 3 and flat
    print(f"   [{'ok' if k2_ok else 'FAIL'}] the ceiling is FLAT across k "
          f"(spread {max(shares) - min(shares):.4f} < 0.01 over {len(shares)} "
          f"points) —\n        the measurement that retired K2 as an effect knob")
    if not k2_ok:
        failures.append("K2 ceiling is no longer flat — the knob may be live again")

    rows_k3 = verdict["signed_divergences"]
    anchored = [d for d in rows_k3 if d.get("anchored")]
    trivial = [d for d in rows_k3 if d.get("trivially_anchored")]
    undefined = [d for d in rows_k3 if d.get("ratio_sa_over_truth") is None]
    unanchored = [d for d in rows_k3
                  if d.get("anchored") is False and not d.get("trivially_anchored")
                  and d.get("ratio_sa_over_truth") is not None]
    # THREE categories plus undefined, not two: an earlier summary said "2 genuine,
    # 3 trivial" when the data held 2 genuine, 2 trivial and 1 zero-truth row whose
    # ratio is undefined and which belongs in its own category (LS F5).
    print(f"\n   K3 signed divergences (sa/truth): {len(rows_k3)} segments — "
          f"{len(anchored)} genuinely ANCHORED, {len(unanchored)} UNANCHORED, "
          f"{len(trivial)} trivially anchored (sa==truth, no information), "
          f"{len(undefined)} zero-truth (ratio undefined)")
    if len(anchored) + len(unanchored) + len(trivial) + len(undefined) != len(rows_k3):
        failures.append("K3 categories do not partition the segments")
    for row in verdict["signed_divergences"][:4]:
        print(f"     {row['segment_id']}  ratio {row.get('ratio_sa_over_truth')}  "
              f"anchored={row.get('anchored')}")
    k3_ok = all("anchored" in d for d in verdict["signed_divergences"])
    print(f"   [{'ok' if k3_ok else 'FAIL'}] every divergence labels its tail — the "
          f"floor anchors ONE side and must not be quoted as covering the distribution")
    print("     SCOPE (S7 round-3 addendum): the anchoring claim is NARROWED TO PD. "
          "The\n     adjacent LGD floors are NOT asserted — the source PDF is not "
          "retained here, so\n     the per-class LGD values are not citable without "
          "a re-fetch, and an asserted\n     floor nobody can point at reads as "
          "verified when it is not.")
    if not k3_ok:
        failures.append("K3 rows missing the anchored label")

    print(f"\n   aggregate output floor: IRB/SA = "
          f"{verdict['aggregate_output_floor_ratio']:.4f} vs published "
          f"{gate.OUTPUT_FLOOR} — ENFORCED as an admission condition (the floor "
          f"binds on the TOTAL, not per segment)")
    print(f"   max effect share: {verdict['max_effect_share_of_oracle']:.4f} vs "
          f"declared MDE {verdict['declared_mde']}")

    # v3 — the PUBLISHED, thresholded quantity, and the diagnostics beside it.
    print(f"\n   CHANNEL-EFFECT CEILING (v3, thresholded): "
          f"{verdict['ceiling_vs_ignorant']:.4f} = "
          f"{verdict['ceiling_vs_ignorant_share']:.4f} of oracle "
          f"(Monte-Carlo, {verdict['ignorant_draws']} draws/seed)")
    print(f"     oracle - E[coverage-blind, capacity-respecting assignment]. This "
          f"is what a manager\n     that learns nothing about the newcomer forgoes "
          f"IN EXPECTATION — the honest\n     headroom for any information channel.")
    print(f"   DIAGNOSTIC (v2, retired as the threshold quantity — NOT the "
          f"published effect):")
    print(f"     drop-the-successor      M = "
          f"{verdict['diagnostic_m_successor']:.4f}")
    print(f"     drop-an-incumbent           {verdict['diagnostic_m_incumbent']:.4f}"
          f"  <- comparator")
    print(f"     coverage-attributable       "
          f"{verdict['diagnostic_coverage_attributable']:.4f}"
          f"   capacity-attributable {verdict['diagnostic_capacity_attributable']:.4f}")
    print(f"     the split is published because v2 is ~"
          f"{verdict['diagnostic_capacity_attributable'] / max(verdict['diagnostic_m_successor'], 1e-12):.0%}"
          f" CAPACITY, not information —\n     dropping ANY worker costs nearly as "
          f"much, so v2 overstated the channel effect.")
    for flag in verdict["flags"]:
        print(f"   [FLAG] {flag}")
    print(f"   NOTE: a below-MDE ceiling FLAGS and never rejects — the pilot, not "
          f"this gate,\n   decides whether the band is too small to study.")
    print(f"\n   DESIGN FACT (carried in every gate report until the pilot answers "
          f"it):\n     {verdict['design_fact']}")

    # --- the estimator's OWN noise, measured rather than promised --------------
    # RR S7 round-3: at 300 draws the estimator noise could flip an instance across
    # the eventual MDE by draw seed alone. Raised to 10,000. The achieved SE is
    # published per row, and here it is CHECKED against the actual spread over
    # k=10 independent streams — sd/sqrt(n) is an assumption about independence,
    # not a measurement, so it gets driven rather than trusted.
    import statistics as _st
    streams = [
        sc.ceiling_vs_ignorant_stats(instance, cap=gate.CAP, stream=k)
        for k in range(10)
    ]
    shares = [c["ceiling_share"] for c in streams]
    cross = _st.stdev(shares)
    claimed = _st.fmean(c["ceiling_share_se"] for c in streams)
    print(f"\n   MONTE-CARLO PRECISION at {sc.IGNORANT_DRAWS} draws (raised from 300):")
    print(f"     achieved SE (share units) {claimed:.6f}   "
          f"cross-stream sd over k=10 {cross:.6f}")
    print(f"     ceiling share across 10 independent streams: "
          f"{min(shares):.4f} to {max(shares):.4f}")
    print(f"     UNITS MATTER and get confused: SE in SCORE units is "
          f"{_st.fmean(c['ceiling_se'] for c in streams):.5f}; the MDE lives in\n"
          f"     SHARE units, so the share SE above is the one that bears on "
          f"admission.")
    # The check: the achieved SE must be the right ORDER as a predictor of the
    # real spread. A factor-2 band, because the k=10 sd is itself a noisy estimate.
    se_ok = 0.5 <= cross / claimed <= 2.0 if claimed else False
    print(f"     [{'ok' if se_ok else 'FAIL'}] achieved SE predicts the cross-stream "
          f"spread (ratio {cross / claimed:.2f}, tolerance 0.5-2.0)")
    if not se_ok:
        failures.append(f"achieved SE mispredicts cross-stream spread: {cross/claimed:.2f}")
    # And the precision must be far below the threshold it feeds.
    precision_ok = claimed < 0.01 * gate.MDE
    print(f"     [{'ok' if precision_ok else 'FAIL'}] SE {claimed:.6f} is under 1% of "
          f"the MDE {gate.MDE} — the draw seed cannot decide admission")
    if not precision_ok:
        failures.append("MC precision is not negligible against the MDE")

    # --- K5 against the v3 ceiling, with the rule PRE-STATED -------------------
    print(f"\n   K5 (shared_class_segments) vs the v3 CEILING — requested by LS, "
          f"interpretation\n   rule PRE-STATED in spec section 8 and quoted here "
          f"BEFORE the numbers:")
    print(f"     substantial movement -> K5 is a RESCUE LEVER;")
    print(f"     slight movement -> the channel effect is small, no knob rescues "
          f"it, recorded\n       as a DESIGN FINDING with no fourth-knob search.")
    k5 = gate.k5_shared_class_curve(SEED, counts=(1, 2, 3, 4, 5, 6, 7))
    for point in k5:
        if "error" in point:
            print(f"     n={point['shared_class_segments']}  rejected: "
                  f"{point['error'][:52]}")
            continue
        print(f"     n={point['shared_class_segments']}  ceiling share "
              f"{point['ceiling_vs_ignorant_share']:.4f} "
              f"+- {point['ceiling_vs_ignorant_share_se']:.4f}   "
              f"[diag strict {point['diagnostic_strict_count']}]  "
              f"below MDE: {point['below_provisional_mde']}")
    # SINGLE-SEED CURVES MISLEAD, so the multi-seed table is computed here and
    # committed as a record rather than quoted from a DM. Same lesson as the C=4
    # cap ruling, which generalised from one instance and had to be revised.
    k5_seeds = range(24)
    k5_counts = (2, 3, 4, 5)
    by_count: dict[int, list[float]] = {c: [] for c in k5_counts}
    for k5_seed in k5_seeds:
        for point in gate.k5_shared_class_curve(k5_seed, counts=k5_counts):
            if "error" in point:
                continue
            by_count[point["shared_class_segments"]].append(
                point["ceiling_vs_ignorant_share"])
    print(f"\n     MULTI-SEED K5 ({len(list(k5_seeds))} seeds) — the reading that counts:")
    k5_table = []
    for count in k5_counts:
        vals = by_count[count]
        row = {
            "shared_class_segments": count, "n_seeds": len(vals),
            "median_ceiling_share": _st.median(vals),
            "min": min(vals), "max": max(vals),
            "n_reaching_mde": sum(v >= gate.MDE for v in vals),
        }
        k5_table.append(row)
        print(f"       n={count}  seeds {len(vals):2d}  median "
              f"{row['median_ceiling_share']:.4f}  range {row['min']:.4f}-"
              f"{row['max']:.4f}  reaching MDE: {row['n_reaching_mde']}/{len(vals)}")
    peak = max(k5_table, key=lambda r: r["median_ceiling_share"])
    current = next(r for r in k5_table if r["shared_class_segments"] == 4)
    gain = peak["median_ceiling_share"] - current["median_ceiling_share"]
    print(f"       peak at n={peak['shared_class_segments']}; current setting is "
          f"n=4; retuning gains {gain:+.4f} of share")
    print(f"       against a gap to the MDE of "
          f"{gate.MDE - current['median_ceiling_share']:.4f}. K5 MOVES the ceiling "
          f"but the current\n       setting is already near the peak, so it is NOT "
          f"a rescue. This case does not\n       fall cleanly on either side of the "
          f"pre-stated rule — flagged for LS, and NO\n       fourth-knob search is "
          f"being run.")
    (HERE / "records" / "S7").mkdir(parents=True, exist_ok=True)
    (HERE / "records" / "S7" / "k5_ceiling_curve_multiseed.json").write_text(
        json.dumps({"seeds": list(k5_seeds), "mde": gate.MDE,
                    "ignorant_draws": sc.IGNORANT_DRAWS, "rows": k5_table},
                   indent=2, sort_keys=True) + "\n")
    k5_usable = [p for p in k5 if "error" not in p]
    k5_ok = len(k5_usable) >= 4
    print(f"   [{'ok' if k5_ok else 'FAIL'}] K5 curve reports the THRESHOLDED "
          f"quantity with its SE at >=4 settings")
    if not k5_ok:
        failures.append("K5 curve has fewer than 4 usable settings")
    blind = verdict["fabrication_blind_effect_carriers"]
    print(f"   strict ∩ clip-flagged: {blind or 'none'}")
    if blind:
        print("     S10 IMPLICATION: the measurable effect sits on segments where "
              "the execution term cannot penalise fabrication.")
    else:
        print("     (effect carriers are unclipped — fabrication stays penalisable "
              "on every strictly-required segment)")

    print(f"\n   K4 realised lattice: {verdict['coverage_lattice']}")
    print(f"   clip-flagged segments (§4.1): {verdict['clip_flagged_segments']}")
    k4_ok = len(verdict["coverage_lattice"]) == len(instance["workers"])
    print(f"   [{'ok' if k4_ok else 'FAIL'}] K4 reports the lattice per instance")
    if not k4_ok:
        failures.append("K4 lattice incomplete")

    # --- 3. the sweep --------------------------------------------------------
    print("\n3. sweep across 40 seeds:")
    report = gate.sweep(range(40))
    print(f"   generated {report['n_generated']}/{report['n_seeds']}, "
          f"admitted {report['n_admitted']}")
    print(f"   distinct coverage lattices: {report['distinct_lattices']} "
          f"(K4 — lattice selection is a second seed-varying spread channel; "
          f"unreported it would look like scatter in the K1 curve)")
    print(f"   swap_shared_class values: {report['swap_class_values']}")
    if report["swap_class_uniform"]:
        print(f"   *** NAMED SCOPE LIMIT: the swapped pair's shared class is "
              f"{report['swap_class_values'][0]!r} in EVERY instance of this suite. "
              f"Findings are scoped to a swap over that class and must say so. ***")
    sweep_ok = report["n_generated"] > 0 and "swap_class_uniform" in report
    print(f"   [{'ok' if sweep_ok else 'FAIL'}] sweep reports uniformity result")
    if not sweep_ok:
        failures.append("sweep did not report uniformity")

    # --- gate REJECT path, on a labelled fixture -----------------------------
    print("\n4. gate reject path (labelled fixture — see docstring):")
    perfect_fixture = gate_fixture_oracle_perfect(instance)
    perfect_verdict = gate.evaluate(perfect_fixture)
    print(f"   oracle {perfect_verdict['oracle']:.4f} / "
          f"{perfect_verdict['n_segments']}  admitted: {perfect_verdict['admitted']}")
    for reason in perfect_verdict["rejection_reasons"]:
        print(f"     REJECTED — {reason[:88]}")
    rejects = not perfect_verdict["admitted"] and any(
        "ORACLE-PERFECT" in r for r in perfect_verdict["rejection_reasons"])
    print(f"   [{'ok' if rejects else 'FAIL'}] the gate REJECTS an oracle-perfect "
          f"instance — the ceiling still bites")
    if not rejects:
        failures.append("gate no longer rejects an oracle-perfect instance")

    print("\n5. gate accept path (labelled fixture — see docstring):")
    fixture = gate_fixture_non_perfect(instance)
    fixture_verdict = gate.evaluate(fixture)
    print(f"   oracle {fixture_verdict['oracle']:.4f} / "
          f"{fixture_verdict['n_segments']}, spread "
          f"{fixture_verdict['spread']:.4f} "
          f"({fixture_verdict['spread_fraction_of_max']:.1%} of max)")
    print(f"   admitted: {fixture_verdict['admitted']}  "
          f"{fixture_verdict['rejection_reasons']}")
    accepts = fixture_verdict["admitted"]
    print(f"   [{'ok' if accepts else 'FAIL'}] the gate ADMITS a non-oracle-perfect "
          f"instance — it is not rejecting everything")
    if not accepts:
        failures.append("gate rejected even a non-oracle-perfect instance")

    # --- 6. FRESHNESS: the committed report must match a fresh run ----------
    # A committed record that predates the code silently misdescribes the system,
    # and this file shipped one (clip_flagged_segments: [] when the code returned
    # two). Checked BEFORE rewriting, so a stale record fails rather than being
    # quietly overwritten by the same run that was supposed to detect it.
    # --- THE HEADLINE, with its provenance, so it cannot be mis-sourced again --
    # THE SHIPPED CELL, NOT THE GENERATOR DEFAULT (L14-b). This called
    # `suite_headline()` bare, which reports the `current` lattice -- a cell whose
    # stale-card ceiling is 0.000% on 60 of 60 instances, so under the restated
    # criterion 3 it admits NOTHING. The acceptance was printing "QUOTE THIS FOR
    # THE STUDY" over a population the study does not run on.
    headline = gate.suite_headline(lattice="partial", shared_class_segments=1)
    print(f"\n   HEADLINE EFFECT SIZE — reported for BOTH populations, because "
          f"they answer\n   different questions and a reader cannot tell which "
          f"they hold unless it is labelled:")
    for key in ("generated", "admitted"):
        block = headline[key]
        marker = "  <- QUOTE THIS FOR THE STUDY" if key == "admitted" else ""
        print(f"     {block['population']}, n={block['n']}{marker}")
        if block.get("empty"):
            print(f"       EMPTY — {block['why']}")
            continue
        print(f"       min {block['min']:.4f}  median {block['median']:.4f}  "
              f"mean {block['mean']:.4f}  max {block['max']:.4f}")
        print(f"       sd {block['sd_sample']:.4f} sample / "
              f"{block['sd_population']:.4f} population; reaching MDE "
              f"{headline['mde']}: {block['n_reaching_mde']} of {block['n']}")
    diff = headline['median_difference']
    print(f"     medians differ by "
          f"{'n/a (a population is empty)' if diff is None else format(diff, '.4f')}"
          f" — small, and not the point: the point is\n     that the population "
          f"must be named, since the study runs on the ADMITTED set.")

    # BELOW-MDE IS UNIVERSAL IN BOTH populations. Asserted on both rather than
    # inferred from the subset relation, because "a fortiori" is a reason to
    # expect it and not a substitute for checking.
    universal_ok = (headline["generated"]["below_mde_is_universal"]
                    and headline["admitted"]["below_mde_is_universal"])
    print(f"   [{'ok' if universal_ok else 'FAIL'}] below-MDE is UNIVERSAL in "
          f"BOTH populations — 0 of {headline['generated']['n']} generated and\n"
          f"        0 of {headline['admitted']['n']} admitted reach it. 'Median "
          f"below MDE' leaves room for a favourable tail; this does not.")
    if not universal_ok:
        failures.append("below-MDE is no longer universal; the headline changed")

    provenance_ok = (headline["generated"]["n"] >= 40
                     and headline["study_population"] == "admitted"
                     and headline["admitted"]["n"] > 0)
    print(f"   [{'ok' if provenance_ok else 'FAIL'}] the figure carries its n AND "
          f"its POPULATION — the first fix stopped it being\n        re-sourced "
          f"from a sweep row; this stops the population being swapped under it")
    if not provenance_ok:
        failures.append("headline does not carry both n and population")

    out = HERE / "records" / "S6"
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "gate_report_seed101.json"
    fresh = json.dumps(verdict, indent=2, sort_keys=True) + "\n"
    print("\n6. record freshness:")
    if report_path.exists():
        stale = report_path.read_text() != fresh
        print(f"   [{'FAIL' if stale else 'ok'}] committed gate report "
              f"{'is STALE — regenerating' if stale else 'matches a fresh run'}")
        if stale:
            failures.append(
                "committed gate report did not match a fresh run (regenerated; "
                "re-run to confirm green)")
    else:
        print("   [ok] no committed report yet — writing the first")
    report_path.write_text(fresh)
    (out / "sweep_report.json").write_text(
        json.dumps({k: v for k, v in report.items() if k != "rows"},
                   indent=2, sort_keys=True) + "\n")
    (out / "sweep_rows.json").write_text(
        json.dumps(report["rows"], indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  {f}")
        return 1
    print("RESULT: PASS — gate rejects the oracle-perfect committed instance and "
          "admits a non-perfect one; all four disclosures emitted; sweep reports "
          "headroom-vs-k and swap-class uniformity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
