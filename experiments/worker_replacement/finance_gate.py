"""S6 — the offline sensitivity gate, the parameter sweep, and the knob disclosures.

Zero model calls: every quantity is arithmetic on a generated instance. The gate
decides ADMISSION before any episode is spent; the sweep publishes the curves that
stop a generator knob from manufacturing the headline.

Single source: spread/oracle/worst come from S4's scorer, instances from S3's
`generate()`. This module is a DRIVER — it re-derives nothing.

WHAT THE GATE BOUNDS: design headroom, never achieved effect. It assumes faithful
execution. Whether agents execute faithfully is the linchpin question (S10).
"""

from __future__ import annotations

from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

# Floor: below this share of the maximum possible spread, an allocation effect
# cannot be shown and the instance is not worth an episode.
SPREAD_FLOOR_FRACTION = 0.05
# Ceiling: at or above this share, the instance is a detection toy rather than an
# allocation problem.
SPREAD_CEILING_FRACTION = 0.95
# Basel output floor: IRB RWA >= 72.5% of SA RWA. Anchors ONE tail of K3 only.
OUTPUT_FLOOR = 0.725
# K6 — the per-worker capacity cap. A DISCLOSED KNOB: it is what makes the task an
# allocation problem rather than a lookup, so its value moves the headline.
#
# C = 3, set from the measured K6 curve rather than from one instance. The first
# ruling was C = 4, generalised from the committed instance whose greedy load is 6
# — but the load is exactly 4 on 23 of 40 seeds, and assertion 2b requires
# cap < load, so C=4 refused to generate those: 17/40 generated and 11/40 fully
# admitted, against 40/40 and 35/40 at C=3. Recorded because it is the same
# single-instance generalisation the disclosure rule exists to catch.
#
# C = 3 also consumes capacity EXACTLY (3 workers x 3 = 9 segments), so the
# manager's problem is purely WHICH segments go where, and it makes the successor
# maximally load-bearing: without it, 2 x 3 = 6 < 9 and three segments go unstaffed.
# FOLLOWS THE RUNTIME (L14-b, researcher ruling 2026-08-10). This was 3 and the
# paragraph above is the record of how 3 was chosen; it is kept because it explains
# the instances we generated, not because it still governs scoring.
#
# The runtime enforces no per-worker segment cap (L14), so the gate must not score
# against one. `finance_scorer.UNCAPPED` resolves per instance to its segment count
# -- present in form, never binding. Passing an explicit integer still constrains,
# which is what the K6 sweep below relies on.
CAP = sc.UNCAPPED
# DECLARED MINIMUM DETECTABLE EFFECT — 0.20, and PROVISIONAL.
#
# It is provisional because no variance estimate exists for the outcome score in
# THIS environment: CHECK-2's figures are old-corpus and, per P14, get re-derived
# once new-setup runs exist. Until then 0.20 is a declared standard, not a measured
# one, and the gate reports it as such rather than implying a power calculation
# nobody has done.
#
# RE-DERIVATION SEQUENCE, so the provisional value cannot quietly become permanent:
#   1. run the gate pair and the first admitted cells;
#   2. estimate the outcome score's within-cell variance from those runs;
#   3. recompute the MDE at the study's n and REPLACE this constant;
#   4. re-run the admission pipeline over the suite — instances admitted under the
#      provisional value are NOT grandfathered.
MDE = 0.20

# Printed in EVERY gate report until the pilot answers it. A design fact stated
# up front is not a hedge: if the measured sigma leaves this band undetectable at
# any affordable n, the design fails honestly and is redesigned.
DESIGN_FACT = (
    "The channel-effect ceiling lands in a band around 0.09-0.18 of the oracle, "
    "against a PROVISIONAL MDE of 0.20 imported from the old corpus. Whether that "
    "band is detectable is unknown until the pilot measures this environment's "
    "variance. Sequence: pilot measures sigma -> MDE re-derived -> the gate re-runs "
    "free -> rejection resumes at the measured threshold. If the measured sigma "
    "leaves this band undetectable at any affordable n, the design fails honestly "
    "and is redesigned."
)
MDE_STATUS = "provisional — no in-environment variance estimate yet"


def spread(instance: dict[str, Any]) -> float:
    return (sc.oracle_capacitated(instance, cap=CAP)
            - sc.worst_capacitated(instance, cap=CAP))


def clip_flagged_segments(instance: dict[str, Any]) -> list[dict[str, Any]]:
    """Segments where some worker's faithful score is CLIPPED to zero (§4.1).

    On these a fabricator cannot be penalised — the score is already at the floor —
    so they are reported per segment rather than aggregated away.
    """
    flagged = []
    for segment in instance["segments"]:
        zeroed = [
            w["worker_id"] for w in instance["workers"]
            if sc.s(segment, w, instance["class_calibration"]) <= 0.0
        ]
        if zeroed:
            flagged.append(
                {"segment_id": segment["segment_id"], "zero_scoring_workers": zeroed}
            )
    return flagged


def k3_signed_divergences(instance: dict[str, Any]) -> list[dict[str, Any]]:
    """Per-unit SIGNED divergence ratios sa/truth, with the anchored tail marked.

    SIGNED because direction matters and an absolute ratio would hide it: SA above
    truth and SA below truth are different regulatory situations.

    The Basel output floor (IRB RWA >= 72.5% of SA) bounds how far IRB may fall
    BELOW SA, i.e. it anchors ratios sa/truth <= 1/0.725 ~ 1.379. It says NOTHING
    about how far IRB may exceed SA, so ratios above 1 in the other direction are
    UNANCHORED and are labelled as such — an external anchor that covers one tail
    must not be quoted as if it covered the distribution (S4 review F3).

    SCOPE OF THE ANCHORING CLAIM — NARROWED TO PD, DELIBERATELY (S7 round-3
    addendum). The input-parameter floors this harness asserts are the PD floors
    (PD_INPUT_FLOOR, with PD_FLOOR_VERIFIED naming the classes whose value we
    actually checked against the text). The ADJACENT LGD floors of the same
    paragraph are NOT asserted anywhere and are NOT claimed here.

    The choice, stated rather than left implicit: widening to LGD was offered and
    DECLINED, because the source PDF is not retained in the repo and the per-class
    LGD values are therefore not citable from the table without a re-fetch. An
    asserted floor we cannot point at is worth less than an absent one — it reads
    as verified. This is the same distinction PD_FLOOR_VERIFIED already draws
    between the classes we checked and sovereign/MDB, which we did not.
    """
    rows = []
    for segment in instance["segments"]:
        truth = sc.correct_rwa(segment, instance["class_calibration"])
        sa_value = sc.sa_rwa(segment)
        if truth == 0.0:
            rows.append({
                "segment_id": segment["segment_id"], "ratio_sa_over_truth": None,
                "anchored": False, "note": "truth is zero — ratio undefined",
            })
            continue
        ratio = sa_value / truth
        # TRIVIALLY anchored: an SA-applicable segment has sa == truth by
        # definition, so ratio 1.0 carries no information about the floor's bite.
        # Counting those inflated S6's "4 anchored" to include ZERO genuinely
        # bounded segments (RR F1), so they are labelled and excluded from the
        # anchored SHARE.
        trivial = not segment["irb_approved"] or abs(ratio - 1.0) < 1e-12
        anchored = (ratio >= 1.0) and not trivial
        rows.append({
            "segment_id": segment["segment_id"],
            "asset_class": segment["asset_class"],
            "ratio_sa_over_truth": round(ratio, 6),
            "anchored": anchored,
            "trivially_anchored": trivial,
            "within_output_floor": (ratio <= 1.0 / OUTPUT_FLOOR) if anchored else None,
        })
    return rows


def aggregate_output_floor(instance: dict[str, Any]) -> float:
    """Aggregate IRB/SA ratio — the output floor's REAL form (LS review round 2, F2).

    Basel's floor binds on the TOTAL, not per exposure: aggregate IRB RWA must be
    at least 72.5% of aggregate SA RWA. Individual segments may sit far outside
    that band, and ours do by design (the divergence selection targets them), so
    enforcing it per segment would be enforcing a bound the standard does not
    impose. Enforcing the aggregate is the honest form, and it was previously
    neither computed nor published.
    """
    total_truth = sum(sc.correct_rwa(seg, instance["class_calibration"])
                      for seg in instance["segments"])
    total_sa = sum(sc.sa_rwa(seg) for seg in instance["segments"])
    return total_truth / total_sa if total_sa else float("inf")


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    """Admission verdict plus every per-instance disclosure."""
    n = len(instance["segments"])
    # CAPACITY-CONSTRAINED (S7 ruling). Sigma-max is retained below as an asserted
    # upper bound, not as the oracle.
    oracle_score = sc.oracle_capacitated(instance, cap=CAP)
    worst_score = sc.worst_capacitated(instance, cap=CAP)
    sigma_max_bound = sc.oracle(instance)
    if oracle_score > sigma_max_bound + 1e-9:
        raise AssertionError(
            f"capacitated oracle {oracle_score} exceeds the Sigma-max upper bound "
            f"{sigma_max_bound} — the DP is wrong"
        )
    observed = oracle_score - worst_score
    # Maximum possible spread on this instance: every segment from 1 down to 0.
    max_spread = float(n)
    fraction = observed / max_spread if max_spread else 0.0

    oracle_perfect = abs(oracle_score - n) < 1e-9
    reasons: list[str] = []
    if oracle_perfect:
        reasons.append(
            f"ORACLE-PERFECT: oracle {oracle_score:.4f} of {n} segments. Rejected "
            "regardless of worst (S4-review tightening) — an instance the oracle "
            "solves completely measures finding the right worker, not managing"
        )
    if fraction < SPREAD_FLOOR_FRACTION:
        reasons.append(
            f"BELOW FLOOR: spread {observed:.4f} is {fraction:.1%} of the maximum "
            f"{max_spread:.0f}, under {SPREAD_FLOOR_FRACTION:.0%} — no allocation "
            "effect is expressible"
        )
    if fraction > SPREAD_CEILING_FRACTION:
        reasons.append(
            f"ABOVE CEILING: spread is {fraction:.1%} of maximum, over "
            f"{SPREAD_CEILING_FRACTION:.0%} — a detection toy, not an allocation "
            "problem"
        )

    strict, tie_inclusive = gen.successor_routing_counts(instance)
    event = instance["event"]

    # MAX MEASURABLE ARRIVAL EFFECT (RR F2 / §5 EFFECT-SIZE FLOOR). The largest
    # score difference the arrival can produce is what the successor uniquely
    # contributes on the strictly-required segments. If that is below the declared
    # MDE, the instance is sub-detectable BY DESIGN and no number of runs helps.
    # M = oracle - oracle_without_successor. Assignment-correct and tie-robust,
    # and under caps the successor is load-bearing STRUCTURALLY: 2 workers x cap 4
    # is 8 < 9 segments, so removing it forces a segment unstaffed regardless of
    # routing. The strict-segment list is retained as a DIAGNOSTIC only — it was
    # the old effect proxy and is tie-sensitive.
    # v3 — the thresholded quantity. Its counterfactual is a manager that HAS the
    # successor and the same capacity but no coverage information, which is what
    # the no-channel cell actually is; so the gap is attributable to INFORMATION.
    ceiling_stats = sc.ceiling_vs_ignorant_stats(
        instance, cap=CAP, draws=sc.IGNORANT_DRAWS)
    ceiling = ceiling_stats["ceiling"]
    ceiling_share = ceiling / oracle_score if oracle_score else 0.0

    # v2 and its comparator, kept as DIAGNOSTICS so the capacity/information split
    # stays visible rather than being replaced silently.
    oracle_without = sc.oracle_without_successor(instance, cap=CAP)
    m_successor = oracle_score - oracle_without
    m_incumbent = oracle_score - sc.oracle_without_incumbent(instance, cap=CAP)
    coverage_attributable = m_successor - m_incumbent

    # FLAG, NOT REJECT (S7 round-3 ruling). The MDE is imported and provisional;
    # rejecting most of a suite on the least defensible number we hold would decide
    # the design's fate on it. The pre-stated sequence runs instead: pilot measures
    # sigma -> MDE re-derived -> this gate re-runs free -> rejection resumes at the
    # measured threshold.
    below_mde = ceiling_share < MDE
    flags = []
    if below_mde:
        flags.append(
            f"CHANNEL-EFFECT CEILING BELOW PROVISIONAL MDE: {ceiling_share:.3f} < "
            f"{MDE}. FLAGGED, not rejected — the MDE is imported and provisional. GATE ON THE FLAG (C1): no flagged instance contributes to a reported finding or benchmark release until the MDE is re-derived and the gate re-run."
        )
    aggregate_ratio = aggregate_output_floor(instance)
    # PUBLISHED, AND NON-BINDING AT PRESENT: every instance the generator produces
    # clears it comfortably (sweep minimum 1.16 against a floor of 0.725), so it
    # currently rejects nothing. Kept and enforced anyway — a bound that binds only
    # if the generator changes is worth having BEFORE the generator changes — but
    # reported honestly so nobody cites it as a filter that is doing work.
    if aggregate_ratio < OUTPUT_FLOOR:
        reasons.append(
            f"BELOW AGGREGATE OUTPUT FLOOR: aggregate IRB/SA is "
            f"{aggregate_ratio:.4f}, under the published {OUTPUT_FLOOR} — the "
            "instance is unrealistic by the standard's own aggregate bound"
        )

    # STRICT n CLIP cross-reference (F3). Where the effect carriers are also
    # clip-flagged, the measurable effect sits exactly where fabrication cannot be
    # penalised, and S10 must be told.
    clip_ids = {row["segment_id"] for row in clip_flagged_segments(instance)}
    fabrication_blind = sorted(set(strict) & clip_ids)

    return {
        "admitted": not reasons,
        "flags": flags,
        # v3 — the thresholded quantity
        "ceiling_vs_ignorant": ceiling,
        "ceiling_vs_ignorant_share": ceiling_share,
        # ACHIEVED Monte-Carlo standard error, measured per row rather than
        # promised by the draw count. Published in BOTH units because the two get
        # confused: the raw SE is in score units, the share SE is in units of the
        # oracle, and the MDE lives in share units.
        "ceiling_vs_ignorant_se": ceiling_stats["ceiling_se"],
        "ceiling_vs_ignorant_share_se": ceiling_stats["ceiling_share_se"],
        "ignorant_per_draw_sd": ceiling_stats["per_draw_sd"],
        "ignorant_draws": sc.IGNORANT_DRAWS,
        "below_provisional_mde": below_mde,
        # v2 + comparator — DIAGNOSTIC ONLY, published so the capacity/information
        # split stays visible rather than the retired quantity vanishing silently.
        "diagnostic_m_successor": m_successor,
        "diagnostic_m_incumbent": m_incumbent,
        "diagnostic_coverage_attributable": coverage_attributable,
        "diagnostic_capacity_attributable": m_successor - coverage_attributable,
        # THE DISCRIMINATING FRACTION, published per instance beside the ceiling
        # (LS ruling). The ceiling captures it only in aggregate and never shows
        # the fraction, and the fraction is what says whether the manager had
        # anything to get wrong.
        "discriminating": sc.discriminating_segments(instance, phase="post_swap"),
        "design_fact": DESIGN_FACT,
        # SPEC'D HERE, IMPLEMENTED IN S9 as a first-class RUN field. At zero slack
        # (3 workers x cap 3 = 9 segments exactly) a single worker refusal leaves a
        # segment unstaffed, worth ~12% of the oracle — so execution loss is lumpy
        # and a capacity-starvation artifact could read as an allocation finding
        # unless the count travels with every run.
        "unstaffed_segment_count_field": "spec'd for S9 run records",
        "aggregate_output_floor_ratio": aggregate_ratio,
        "capacity_cap_k6": CAP,
        "sigma_max_upper_bound": sigma_max_bound,
        "oracle_without_successor": oracle_without,
        "greedy_card_match_load": sc.greedy_card_match_load(instance),
        "aggregate_output_floor_status": (
            "published; non-binding at present — no generated instance has failed it"
        ),
        "declared_mde_status": MDE_STATUS,
        "fabrication_blind_effect_carriers": fabrication_blind,
        # Retained under their old names for compatibility with existing readers,
        # but now carrying the v3 quantity — the v1/v2 values live under their
        # diagnostic names so nothing silently keeps the retired meaning.
        "max_effect_share_of_oracle": ceiling_share,
        "declared_mde": MDE,
        "rejection_reasons": reasons,
        "oracle": oracle_score,
        "worst": worst_score,
        "spread": observed,
        "spread_fraction_of_max": fraction,
        "n_segments": n,
        # K2 — per instance
        "k_threshold": instance["parameters"]["min_successor_routed"],
        "successor_strict_segments": strict,
        "successor_strict_count": len(strict),
        "successor_tie_inclusive_count": len(tie_inclusive),
        "successor_only_fraction": len(strict) / n if n else 0.0,
        # K4 — the realised lattice
        "coverage_lattice": {
            w["worker_id"]: list(w["irb_coverage"]) for w in instance["workers"]
        },
        "swap_shared_class": event["swap_shared_class"],
        # K3
        "signed_divergences": k3_signed_divergences(instance),
        # §4.1
        "clip_flagged_segments": clip_flagged_segments(instance),
    }


def k1_curve(seed: int, points: int = 7, **generate_kwargs) -> list[dict[str, Any]]:
    """K1 — spread as a FUNCTION of the covered fraction, never the operating point.

    Driven through the production generator: each point is a real `generate()` call
    at a different `irb_applicable_fraction`, scored by the production scorer. The
    curve is not computed from a formula for spread.
    """
    curve = []
    for index in range(points):
        fraction = round(0.1 + index * (0.8 / max(1, points - 1)), 4)
        try:
            instance = gen.generate(
                seed, irb_applicable_fraction=fraction, **generate_kwargs
            )
        except (gen.InstanceAssertionError, ValueError) as exc:
            curve.append({
                "irb_applicable_fraction": fraction, "spread": None,
                "rejected": type(exc).__name__, "detail": str(exc)[:90],
            })
            continue
        curve.append({
            "irb_applicable_fraction": fraction,
            "spread": round(spread(instance), 6),
            "oracle": round(sc.oracle(instance), 6),
            "worst": round(sc.worst(instance), 6),
        })
    return curve


def k2_headroom_curve(seed: int, k_values: tuple[int, ...] = (1, 2, 3, 4, 5)) -> list[dict]:
    """K2 — regret headroom as a function of k, the successor-routing threshold.

    Each point is a real `generate()` at that k, so the curve shows where the
    assertion starts rejecting rather than asserting a threshold in prose.

    WHAT THIS CURVE DISCLOSES (S7 round-3, item 2): the THRESHOLDED quantity —
    the channel-effect ceiling — at each k. The strict successor-routing COUNT is
    retained as a DIAGNOSTIC only: it counts segments, and a segment count says
    nothing about how much value rides on them. k is a knob on the DESIGN; the
    ceiling is what the knob is supposed to move, so the ceiling is what a reader
    needs to see against it.
    """
    curve = []
    for k in k_values:
        try:
            instance = gen.generate(seed, min_successor_routed=k)
        except gen.InstanceAssertionError as exc:
            curve.append({"k": k, "admitted_by_assertion": False,
                          "detail": str(exc)[:80]})
            continue
        strict, _ = gen.successor_routing_counts(instance)
        oracle_k = sc.oracle_capacitated(instance, cap=CAP)
        stats_k = sc.ceiling_vs_ignorant_stats(instance, cap=CAP)
        ceiling_k = stats_k["ceiling"]
        curve.append({
            "k": k, "admitted_by_assertion": True,
            # the disclosed quantity
            "ceiling_vs_ignorant": ceiling_k,
            "ceiling_vs_ignorant_share": ceiling_k / oracle_k if oracle_k else None,
            "ceiling_vs_ignorant_se": stats_k["ceiling_se"],
            # diagnostic only — a count of segments, not of value
            "diagnostic_strict_count": len(strict),
            "diagnostic_headroom": len(strict) - k,
        })
    return curve


def k5_shared_class_curve(seed: int, counts: tuple[int, ...] = (2, 3, 4, 5, 6)) -> list[dict]:
    """K5 — max-effect as a function of `shared_class_segments`.

    Promoted to a disclosed knob because it moves the headline directly: it sets
    how many segments the strictly-required set can contain, and I chose its value
    (4) against a measured alternative that admitted more (5 -> 39/40). Publishing
    the curve is what stops that choice from being invisible.

    NOW REPORTED AGAINST THE v3 CEILING (LS request, S7 round-3). The INTERPRETATION
    RULE IS PRE-STATED in spec section 8 and is binding on whatever this returns:
      * SUBSTANTIAL movement in the ceiling across the K5 range -> K5 is a RESCUE
        LEVER, and a design too small at the current setting can be retuned.
      * SLIGHT movement -> the channel effect is SMALL, and no knob rescues it.
        That is a DESIGN FINDING and is recorded as one. NO search for a fourth
        knob follows — searching knobs until one moves the headline is how a
        design gets tuned into significance.
    Pre-stating it is the point: the rule cannot be chosen after seeing the curve.
    """
    curve = []
    for count in counts:
        try:
            instance = gen.generate(seed, shared_class_segments=count)
        except Exception as exc:
            curve.append({"shared_class_segments": count, "error": str(exc)[:70]})
            continue
        verdict = evaluate(instance)
        curve.append({
            "shared_class_segments": count,
            "ceiling_vs_ignorant": round(verdict["ceiling_vs_ignorant"], 6),
            "ceiling_vs_ignorant_share": round(
                verdict["ceiling_vs_ignorant_share"], 6),
            "ceiling_vs_ignorant_share_se": round(
                verdict["ceiling_vs_ignorant_share_se"], 6),
            "max_effect_share": round(verdict["max_effect_share_of_oracle"], 6),
            "diagnostic_strict_count": verdict["successor_strict_count"],
            "admitted": verdict["admitted"],
            "below_provisional_mde": verdict["below_provisional_mde"],
        })
    return curve


def k6_capacity_curve(seeds: range, caps: tuple[int, ...] = (2, 3, 4, 5)) -> list[dict]:
    """K6 — yield and effect as a function of the per-worker cap.

    Disclosed because the cap is what makes this an allocation problem rather than
    a lookup, so its value moves the headline more than any other knob. It also has
    a non-obvious interaction: a cap must be FEASIBLE (roster x cap >= segments)
    AND BINDING (cap < the instance's greedy card-match load), and those pull in
    opposite directions — the curve is how that trade becomes visible instead of
    being settled by one probe on one instance.
    """
    global CAP
    original = CAP
    curve = []
    try:
        for cap in caps:
            CAP = cap
            generated = admitted = 0
            for seed in seeds:
                try:
                    instance = gen.generate(seed, capacity_cap=cap)
                except Exception:
                    continue
                generated += 1
                verdict = evaluate(instance)
                baseline = sc.scripted_label_baseline_capped(instance, cap=cap)
                if verdict["admitted"] and (
                    verdict["oracle"] - sc.score(instance, baseline) > 1e-9
                ):
                    admitted += 1
            curve.append({
                "cap": cap, "feasible": 3 * cap >= 9,
                "generated": generated, "fully_admitted": admitted,
            })
    finally:
        CAP = original
    return curve


def sweep(seeds: range) -> dict[str, Any]:
    """Suite-level report: admission, swap-class uniformity, lattice variety."""
    rows = []
    for seed in seeds:
        try:
            instance = gen.generate(seed)
        except (gen.InstanceAssertionError, ValueError) as exc:
            rows.append({"seed": seed, "generated": False, "detail": str(exc)[:80]})
            continue
        verdict = evaluate(instance)
        rows.append({
            "seed": seed, "generated": True,
            "admitted": verdict["admitted"],
            "spread": round(verdict["spread"], 6),
            # Published per instance so every stat quoted from this sweep is
            # recomputable from the committed report rather than from a DM (P10).
            "max_effect_share": round(verdict["max_effect_share_of_oracle"], 6),
            "aggregate_output_floor_ratio": round(
                verdict["aggregate_output_floor_ratio"], 6),
            "strict_count": verdict["successor_strict_count"],
            "fabrication_blind_carriers": verdict["fabrication_blind_effect_carriers"],
            # Named cause, not a bare False: a sweep that says only "not admitted"
            # cannot tell a below-MDE instance from an oracle-perfect one, and the
            # two call for opposite fixes.
            "rejection_causes": [r.split(":")[0] for r in verdict["rejection_reasons"]],
            "oracle_perfect": abs(verdict["oracle"] - verdict["n_segments"]) < 1e-9,
            "swap_shared_class": verdict["swap_shared_class"],
            "lattice": tuple(sorted(
                tuple(v) for v in verdict["coverage_lattice"].values())),
        })
    generated = [r for r in rows if r["generated"]]
    classes = {r["swap_shared_class"] for r in generated}
    lattices = {r["lattice"] for r in generated}
    effects = sorted(r["max_effect_share"] for r in generated)
    ratios = sorted(r["aggregate_output_floor_ratio"] for r in generated)
    return {
        "max_effect_share_min": effects[0] if effects else None,
        "max_effect_share_median": effects[len(effects) // 2] if effects else None,
        "max_effect_share_max": effects[-1] if effects else None,
        "aggregate_floor_min": ratios[0] if ratios else None,
        "aggregate_floor_median": ratios[len(ratios) // 2] if ratios else None,
        "instances_with_fabrication_blind_carriers": sum(
            1 for r in generated if r["fabrication_blind_carriers"]),
        "n_seeds": len(rows),
        "n_generated": len(generated),
        "n_admitted": sum(1 for r in generated if r["admitted"]),
        "swap_class_values": sorted(classes),
        "swap_class_uniform": len(classes) <= 1,
        "distinct_lattices": len(lattices),
        "rows": rows,
    }


def suite_headline(seeds: range = range(40), **instance_kwargs) -> dict[str, Any]:
    """THE headline effect size, over BOTH populations, each labelled.

    This function exists twice over, for two versions of the same mistake.

    FIRST: the headline was once quoted at 0.1018 — a figure that reproduced
    exactly and was the median of a 24-SEED K5 SWEEP ROW, over a knob dropped the
    same day as inert. Right value, wrong n, wrong provenance.

    SECOND, found on the fix for the first: there are TWO POPULATIONS and they
    answer different questions. The GENERATED suite (40) describes what the
    generator produces. The ADMITTED suite (34) describes WHAT THE STUDY WILL
    ACTUALLY RUN ON — instances are selected from the admitted set — and that is
    the one any cost, power or effect-size statement about the study needs. They
    differ by 0.0042 in median, which is small and is not the point: the point is
    that a reader cannot tell which they have been handed unless it is labelled.

    So the value now travels with BOTH its n and its POPULATION, because the
    previous fix stopped the figure being re-sourced from a sweep row and did not
    stop the population being swapped underneath it.
    """
    import statistics as _st

    # ADMITTED means ALL THREE admission conditions, not just the gate. Using
    # `evaluate()` here returned 40 of 40 and made the two populations identical
    # — the gate is condition 2 alone, and conditions 1 (bit-identical
    # regeneration) and 3 (scripted baseline below oracle) are what take the set
    # to 34. A "population" that is silently the wrong population is the same
    # failure this function exists to prevent, one level in.
    from . import finance_admission as adm  # local: admission imports this module

    # `instance_kwargs` (lattice, shared_class_segments, ...) THREADS TO BOTH the
    # admission sweep and the regeneration below. It defaulted to the generator's
    # own default -- `current` -- which is NOT the shipped cell, so this function
    # described a population the study does not run on while labelling its output
    # "WHAT THE STUDY WILL ACTUALLY RUN ON". That is the third version of the same
    # mistake the docstring above records twice (L14-b).
    suite = adm.admit_suite(seeds, **instance_kwargs)
    admitted_seeds = {row["seed"] for row in suite["rows"] if row["admitted"]}

    generated, admitted = [], []
    for seed in seeds:
        try:
            instance = gen.generate(seed, **instance_kwargs)
        except gen.InstanceAssertionError:
            continue
        share = sc.ceiling_vs_ignorant_stats(
            instance, cap=CAP)["ceiling_share"]
        generated.append(share)
        if seed in admitted_seeds:
            admitted.append(share)

    def _stats(values: list[float], population: str, question: str) -> dict:
        # AN EMPTY POPULATION IS A RESULT, NOT A CRASH (L14-b). Criterion 3 now
        # admits only instances whose stale-card ceiling is above zero, and at this
        # module's DEFAULT lattice (`current`) that is 0 of 60 -- so `admitted` came
        # back empty and `min()` raised, hiding a meaningful verdict behind a
        # traceback. The emptiness is correct and is exactly why `current` is not
        # the shipped lattice; it has to be REPORTED, because a headline that dies
        # cannot say "this lattice admits nothing" and a reader would otherwise meet
        # a stack trace where a finding belongs.
        if not values:
            return {
                "population": population,
                "answers": question,
                "n": 0,
                "empty": True,
                "why": ("no instance was admitted, so no distribution exists. Under "
                        "criterion 3 this means every instance's stale-card ceiling "
                        "is zero -- the successor's identity is worth nothing on any "
                        "of them. Expected at the `current` lattice; a finding "
                        "anywhere else."),
            }
        return {
            "population": population,
            "answers": question,
            "n": len(values),
            "min": min(values), "median": _st.median(values),
            "mean": _st.fmean(values), "max": max(values),
            # The pilot reports a SAMPLE sd, so that is the like-for-like
            # comparator; the population sd is emitted beside it, named.
            "sd_sample": _st.stdev(values),
            "sd_population": _st.pstdev(values),
            "n_reaching_mde": sum(1 for v in values if v >= MDE),
            "below_mde_is_universal": not any(v >= MDE for v in values),
        }

    return {
        "quantity": "ceiling_vs_ignorant_share",
        "source": "full generated suite, evaluated per population",
        "mde": MDE,
        "generated": _stats(
            generated, "GENERATED (all seeds that produce an instance)",
            "what the generator produces"),
        "admitted": _stats(
            admitted, "ADMITTED (the set instances are selected from)",
            "WHAT THE STUDY RUNS ON — quote this for any effect-size, cost or "
            "power statement about the study"),
        "instance_kwargs": dict(instance_kwargs) or {"lattice": "current (DEFAULT — not the shipped cell)"},
        "study_population": "admitted",
        # None rather than a number when either population is empty — this figure
        # exists to show how far admission MOVES the distribution, and with nothing
        # admitted there is no distribution to have moved (L14-b).
        "median_difference": (
            _st.median(generated) - _st.median(admitted)
            if generated and admitted else None),
    }
