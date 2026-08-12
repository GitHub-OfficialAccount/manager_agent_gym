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
  * ★ THE NON-TRIVIALITY CLAIM HERE IS RETIRED (L14-b). It read: "once the cap
    binds, the script must choose WHICH segments to overflow... No script over
    public information can attain the oracle." THE CAP NO LONGER BINDS -- the
    runtime enforces none -- so nothing overflows and this script ties the oracle
    on every instance (56: 8.5430 = 8.5430; 37: 8.9168 = 8.9168).
    The script is still computed and still REPORTED as `scripted_baseline_score`,
    because it remains a meaningful upper-information reference: it is what a
    manager who already knew the successor's true labels would achieve by pure
    label-matching. It is no longer a CRITERION. Criterion 3 now asks whether
    optimal play believing the PREDECESSOR'S card attains the oracle, which is the
    question the old form was standing in for.
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
    crash. (Assertion 2b used to be the common cause here; it is RETIRED -- see
    ALLOCATION_DIFFICULTY_RETIRED in finance_generator.)
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
                "3_stale_card_ceiling_above_zero": False,
            },
        }
    verdict = gate.evaluate(instance)

    identical, detail = regenerates_bit_identically(seed, **kwargs)

    # ★ CRITERION 3 IS RESTATED AGAINST A DIFFERENT BASELINE (L14-b). It asked
    # whether the greedy card-match script stays BELOW the oracle. Uncapped that
    # script ties the oracle on every instance, so the criterion rejected the entire
    # suite -- 0 admitted, and the study could not run at all.
    #
    # WHY THE OLD FORM STOPPED MEASURING ITS OWN INTENT. The intent was "a manager
    # cannot solve this without the information the study supplies". The script
    # reads the SUCCESSOR'S TRUE LABELS, which under the stale-card manipulation the
    # manager does not have -- so it was never a test of what a manager could do. It
    # only LOOKED like one while the cap forced an overflow the labels could not
    # resolve. Remove the cap and the disguise falls off.
    #
    # THE RESTATEMENT TESTS THE INTENT DIRECTLY: can optimal play believing the
    # PREDECESSOR'S CARD attain the oracle? If it can, the successor's identity is
    # worth nothing on this instance and no channel can show an effect. That is
    # `ceiling_vs_stale_card > 0`, which is also exactly what
    # `select_study_instances` already excludes on -- so admission and selection now
    # agree instead of applying two different non-triviality tests.
    #
    # WHAT IS GIVEN UP, PLAINLY: admission no longer certifies "not solvable by a
    # script holding true labels". Under the current design nothing does, because
    # uncapped that is false everywhere. Saying so beats keeping a criterion that
    # certifies it by rejecting everything.
    baseline_allocation = scripted_label_baseline_capped(instance, cap=gate.CAP)
    baseline_score = sc.score(instance, baseline_allocation)
    oracle_score = verdict["oracle"]
    card_ceiling = sc.ceiling_vs_stale_card(instance, cap=gate.CAP)
    # STRICTLY above zero: an instance the stale card already solves cannot exhibit
    # a card effect however many episodes it is given.
    baseline_ok = card_ceiling["ceiling"] > 1e-9

    conditions = {
        "1_bit_identical_regeneration": identical,
        "2_interior_spread_and_disclosures": verdict["admitted"],
        # RENAMED WITH THE CONDITION (L14-b). It was `3_scripted_baseline_below_
        # oracle`, which described the PREVIOUS test. Keeping the old key for
        # historical comparability was the wrong trade: a condition whose name
        # describes a test it no longer runs is how a future reader concludes the
        # gate checks something it does not -- and that is the sixth instance of
        # name-over-condition this week, the first caused by a CORRECT edit.
        # Old rows are readable via this comment; new rows say what they mean.
        "3_stale_card_ceiling_above_zero": baseline_ok,
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
            "optimal play believing the PREDECESSOR'S CARD already attains the "
            "oracle — the successor's identity is worth nothing here, so no "
            "information channel can show an effect on this instance"
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
