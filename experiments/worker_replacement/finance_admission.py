"""S7 — the admission pipeline. Three conditions, all required.

Composes S3's `generate()`, S4's scorer and S6's gate. Re-implements nothing.

THE SCRIPTED BASELINE'S MATCHING SPECIFICATION, committed with the pipeline
because a baseline nobody can reconstruct is not a gate (P10):

  * INPUT, per segment: the string `asset_class`. Nothing else — not
    `irb_approved`, not `pd`, not the truth.
  * INPUT, per worker: the strings in `card_capabilities`, which is the registry
    card as the all-channels cell would show it. NEVER `irb_coverage` (ground
    truth the manager does not see) and NEVER `worker_id` (opaque by S2/S5, so an
    id-matching baseline would be testing our id scheme, not the task).
  * RULE: route the segment to the first worker, in sorted card order, whose card
    contains a capability line ending in that asset class. UNDER THE PER-WORKER
    CAP: when the preferred worker is full, overflow to the first worker with
    remaining capacity; if all are full the segment goes unstaffed and scores 0.
  * WHY THIS IS NOW NON-TRIVIAL, and the property is INFORMATION-THEORETIC rather
    than a matter of obscuring labels: once the cap binds, the script must choose
    WHICH segments to overflow, and the optimal overflow depends on each segment's
    fallback penalty |SA - truth| — which requires the truth, and so lives in the
    PRIVATE CALIBRATIONS. No script over
    public information can attain the oracle, because the information required to
    do so is not public. Obfuscating card wording would only have tested string
    matching; this tests whether the manager acquires and uses value information
    the cards do not carry.
  * TIE-BREAK: sorted by the worker's joined card text, so the baseline is
    deterministic and reproducible without reference to ids.

The baseline is scored through the PRODUCTION scorer, so its score and the
oracle's are commensurable by construction.
"""

from __future__ import annotations

from typing import Any

from . import finance_gate as gate
from . import finance_generator as gen
from . import finance_scorer as sc
from .finance_scorer import scripted_label_baseline_capped  # single definition


def regenerates_bit_identically(seed: int, hash_seeds: tuple[str, ...] = ("1", "99"),
                                **kwargs) -> tuple[bool, str]:
    """Condition 1 — AGENT-FREE bit-identical regeneration.

    generate(seed) -> score(fixed_outputs), byte-identical across processes run at
    different PYTHONHASHSEEDs. Agent-INCLUSIVE re-runs are explicitly not the test:
    CHECK-2 measured within-seed nondeterminism dominating 10 of 12 DVs, so an
    agent-inclusive criterion would reject every instance ever generated. What is
    admitted here is instance + scorer determinism, and nothing more.
    """
    import os
    import subprocess
    import sys
    from pathlib import Path

    code = (
        "from experiments.worker_replacement.finance_generator import generate, to_json;"
        "from experiments.worker_replacement import finance_scorer as sc;"
        f"i=generate({seed}, **{kwargs!r});"
        "print(to_json(i), end='');"
        "print(round(sc.oracle(i), 12), round(sc.worst(i), 12))"
    )
    root = Path(__file__).resolve().parents[2]
    outputs = [
        subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True,
                       text=True, check=True,
                       env={**os.environ, "PYTHONHASHSEED": h}).stdout
        for h in hash_seeds
    ]
    identical = len(set(outputs)) == 1
    return identical, f"{len(outputs[0])} bytes across PYTHONHASHSEED {hash_seeds}"


def admit(seed: int, **kwargs) -> dict[str, Any]:
    """Run all three admission conditions on one generated instance.

    A seed whose instance fails a GENERATION assertion is reported as a rejection,
    not raised: a suite builder that dies on the first invalid seed cannot build a
    suite, and the assertion firing is a correct outcome to record rather than a
    crash. Assertion 2b in particular rejects seeds whose greedy card-match load
    happens to equal the cap.
    """
    try:
        instance = gen.generate(seed, **kwargs)
    except gen.InstanceAssertionError as exc:
        return {
            "seed": seed, "admitted": False, "generated": False,
            "generation_rejection": str(exc)[:140],
            "rejection_reasons": [f"generation assertion: {str(exc)[:120]}"],
            "conditions": {
                "1_bit_identical_regeneration": False,
                "2_interior_spread_and_disclosures": False,
                "3_scripted_baseline_below_oracle": False,
            },
        }
    verdict = gate.evaluate(instance)

    identical, detail = regenerates_bit_identically(seed, **kwargs)

    # Greedy card-matching UNDER the cap (S7 ruling item 5).
    baseline_allocation = scripted_label_baseline_capped(instance, cap=gate.CAP)
    baseline_score = sc.score(instance, baseline_allocation)
    oracle_score = verdict["oracle"]
    # STRICTLY below: a baseline that merely ties the oracle has still solved the
    # instance by surface matching.
    baseline_ok = baseline_score < oracle_score - 1e-9

    conditions = {
        "1_bit_identical_regeneration": identical,
        "2_interior_spread_and_disclosures": verdict["admitted"],
        "3_scripted_baseline_below_oracle": baseline_ok,
    }

    # NAMED CAUSES on every non-admitted row (S6 round-2 item 4, which regressed
    # into this artifact: rejected rows carried `None`). A row that says only
    # "not admitted" cannot distinguish a below-MDE instance from one a script
    # solves, and those call for opposite fixes. Never None and never empty for a
    # rejected row — the acceptance asserts it so this cannot regress a third time.
    rejection_reasons: list[str] = []
    if not identical:
        rejection_reasons.append("instance is not bit-identically regenerable")
    if not verdict["admitted"]:
        rejection_reasons.extend(verdict["rejection_reasons"])
    if not baseline_ok:
        rejection_reasons.append(
            "scripted baseline attains oracle — the instance is solvable from "
            "public information alone, so it measures lookup, not management"
        )
    return {
        "seed": seed,
        "generated": True,
        "admitted": all(conditions.values()),
        "conditions": conditions,
        "regeneration_detail": detail,
        "oracle": oracle_score,
        "scripted_baseline_score": baseline_score,
        "baseline_shortfall": oracle_score - baseline_score,
        "rejection_reasons": rejection_reasons,
        "gate_rejection_reasons": verdict["rejection_reasons"],
        # NAMED explicitly so the artifact cannot be read as the retired v2
        # quantity. `max_effect_share` is now the v3 ceiling; the v2 numbers
        # travel beside it under diagnostic_ names and are NOT thresholded.
        "max_effect_share": verdict["max_effect_share_of_oracle"],
        "ceiling_vs_ignorant": verdict["ceiling_vs_ignorant"],
        "ceiling_vs_ignorant_share": verdict["ceiling_vs_ignorant_share"],
        # ACHIEVED Monte-Carlo SE, PER ROW (RR S7 round-3). Published in both
        # units: the share SE is the one that bears on admission, because the MDE
        # is in share units. A draw count promises precision; only this measures it.
        "ceiling_vs_ignorant_se": verdict["ceiling_vs_ignorant_se"],
        "ceiling_vs_ignorant_share_se": verdict["ceiling_vs_ignorant_share_se"],
        "ignorant_per_draw_sd": verdict["ignorant_per_draw_sd"],
        "ignorant_draws": verdict["ignorant_draws"],
        "below_provisional_mde": verdict["below_provisional_mde"],
        "flags": verdict["flags"],
        "diagnostic_m_successor": verdict["diagnostic_m_successor"],
        "diagnostic_m_incumbent": verdict["diagnostic_m_incumbent"],
        "diagnostic_coverage_attributable": verdict["diagnostic_coverage_attributable"],
        "declared_mde": verdict["declared_mde"],
        "declared_mde_status": verdict["declared_mde_status"],
    }


def admit_suite(seeds: range, **kwargs) -> dict[str, Any]:
    rows = [admit(seed, **kwargs) for seed in seeds]
    generated = [r for r in rows if r.get("generated")]
    return {
        "n": len(rows),
        "n_generated": len(generated),
        "n_admitted": sum(1 for r in rows if r["admitted"]),
        "generation_rejections": [
            {"seed": r["seed"], "cause": r["generation_rejection"].split(":")[0]}
            for r in rows if not r.get("generated")
        ],
        "baseline_shortfall_min": (
            min(r["baseline_shortfall"] for r in generated) if generated else None),
        "baseline_shortfall_median": (
            sorted(r["baseline_shortfall"] for r in generated)[len(generated) // 2]
            if generated else None),
        "failures_by_condition": {
            name: sum(1 for r in rows if not r["conditions"][name])
            for name in rows[0]["conditions"]
        } if rows else {},
        "rows": rows,
    }
