"""Does `ceiling_vs_stale_card` model the whole card, or only half of it?

THE CARD HAS TWO ERRORS. It CLAIMS coverage the successor lacks (the lie), and it
is SILENT about coverage the successor has (the omission). A stale card describes
the worker that LEFT, so it is a REPLACEMENT description, not an addition to a
true one.

`finance_scorer.ceiling_vs_stale_card` USED TO model the lie and not the omission:
its `believed_score` granted 1.0 where the card claimed coverage and otherwise fell
THROUGH TO THE TRUE SCORE, so wherever the card was silent about a class the
successor really covered, the manager was credited with knowing it anyway. D1 fixed
it. This module is the acceptance for that fix and asserts BOTH halves.

`lie_only_ceiling` below is the SUPERSEDED model, kept deliberately: an acceptance
that only ran the current implementation could not show the divergence, and the
divergence is the half that the current implementation exists to produce. It is a
frozen copy of the old behaviour, never imported by anything else.

WHY THAT HAS NOT MATTERED, AND WHY IT IS ABOUT TO. Under the CURRENT template the
successor's silent class is always covered by an incumbent, so not knowing about it
costs nothing and the two models agree exactly. Under any template where the
successor SOLE-HOLDS a silent class, the omission is a real coverage loss — and a
model blind to it prices that property at ZERO. That property is precisely what the
L9 candidates are designed to add, so the instrument would systematically
under-price the designs it is being used to choose between.

THIS IS A POSITIVE-CONTROL CHECK, NOT AN ASSERTION OF A NULL. The replacement model
must AGREE with the current one where the omission is known to be harmless (that is
the control: a "better" model that moved numbers there would be wrong, not better),
and diverge ONLY where the successor sole-holds a silent class. Both are measured.

Run:  python3 -m experiments.worker_replacement.check_card_belief_model
"""

from __future__ import annotations

import json
import statistics as st
from itertools import product
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc
from .check_template_pricing import TEMPLATES, labels_of

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(30)


def lie_only_ceiling(instance: dict[str, Any], cap: int = CAP) -> dict[str, Any]:
    """THE SUPERSEDED MODEL — a frozen copy of `ceiling_vs_stale_card` before D1.

    Grants 1.0 where the card CLAIMS coverage and otherwise falls through to the
    TRUE score, so the card's OMISSION costs nothing. Kept only so this acceptance
    can demonstrate the divergence the fix produces; nothing else imports it, and
    it must never be used to price anything.
    """
    event = instance["event"]
    successor = event["successor_id"]
    calibration = instance["class_calibration"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    workers = [by_id[w] for w in event["roster_post_swap"]]
    segments = instance["segments"]
    card_claims = set(by_id[event["predecessor_id"]]["irb_coverage"])

    def true_score(segment, worker):
        return sc.s(segment, worker, calibration)

    def believed_score(segment, worker):
        if worker["worker_id"] != successor:
            return sc.s(segment, worker, calibration)
        if (sc.applicable_approach(segment) == "IRB"
                and segment["asset_class"] in card_claims):
            return 1.0
        return sc.s(segment, worker, calibration)   # <- the fall-through, the fault

    def best(scoref):
        best_value, best_alloc = -1.0, ()
        for combo in product(range(len(workers)), repeat=len(segments)):
            if any(combo.count(i) > cap for i in range(len(workers))):
                continue
            value = sum(scoref(sg, workers[w]) for sg, w in zip(segments, combo))
            if value > best_value:
                best_value, best_alloc = value, combo
        return best_value, best_alloc

    true_value, _ = best(true_score)
    _, believed_alloc = best(believed_score)
    realised = sum(true_score(sg, workers[w])
                   for sg, w in zip(segments, believed_alloc))
    return {
        "ceiling": true_value - realised,
        "ceiling_share": (true_value - realised) / true_value if true_value else None,
        "oracle": true_value,
        "baseline": "SUPERSEDED: optimal play believing the card's CLAIMS only",
    }


def omission_is_costly(instance: dict[str, Any]) -> bool:
    """Does the successor SOLE-HOLD a class the card is silent about?

    That is the exact condition under which the two belief models can differ, and
    it is checked structurally rather than inferred from the numbers agreeing.
    """
    event = instance["event"]
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    successor = event["successor_id"]
    card_claims = set(by_id[event["predecessor_id"]]["irb_coverage"])
    incumbents = [by_id[w] for w in event["roster_post_swap"] if w != successor]
    silent = set(by_id[successor]["irb_coverage"]) - card_claims
    return any(not any(c in w["irb_coverage"] for w in incumbents) for c in silent)


def main() -> int:
    print("D1 ACCEPTANCE — ceiling_vs_stale_card (SHIPPED, whole card) against")
    print("the SUPERSEDED lie-only model. Both halves are asserted.\n")

    # --- POSITIVE CONTROL: the current template, where the omission is harmless ---
    rows, structural = [], []
    for seed in SEEDS:
        instance = gen.generate(seed)
        shipped = sc.ceiling_vs_stale_card(instance, cap=CAP)["ceiling_share"] or 0.0
        superseded = lie_only_ceiling(instance)["ceiling_share"] or 0.0
        rows.append((seed, superseded, shipped))
        structural.append(omission_is_costly(instance))

    disagree = [r for r in rows if abs(r[1] - r[2]) > 1e-12]
    print("CONTROL — current template, where the successor's silent class is always")
    print("incumbent-covered, so the omission is known to cost nothing:")
    print(f"   seeds with a costly omission (structural) : {sum(structural)}/{len(rows)}")
    print(f"   seeds where the two models DISAGREE       : {len(disagree)}/{len(rows)}")
    control_ok = sum(structural) == 0 and not disagree
    print(f"   -> {'PASS' if control_ok else 'FAIL'}: the replacement model must not "
          f"move numbers where the omission is harmless\n")

    # --- THE CASE THAT DIVERGES: a template where the successor sole-holds ---------
    # Priced by coverage substitution, the same technique as check_template_pricing:
    # the segments, ratings and calibration are the real instance's, and ONLY the
    # coverage sets change, so the difference is the lattice's and nothing else's.
    print("DIVERGENCE — the disjoint candidate, where the successor SOLE-HOLDS the")
    print("class the card is silent about. The fix MUST move numbers here, or it")
    print("has not taken:")
    superseded_shares, shipped_shares, costly = [], [], []
    for seed in SEEDS:
        instance = substitute(gen.generate(seed), TEMPLATES["proposed_disjoint"])
        superseded_shares.append(lie_only_ceiling(instance)["ceiling_share"] or 0.0)
        shipped_shares.append(sc.ceiling_vs_stale_card(instance, cap=CAP)["ceiling_share"] or 0.0)
        costly.append(omission_is_costly(instance))
    understated = st.mean(shipped_shares) - st.mean(superseded_shares)
    print(f"   seeds with a costly omission (structural) : {sum(costly)}/{len(SEEDS)}")
    print(f"   SUPERSEDED lie-only mean ceiling share    : {st.mean(superseded_shares):.2%}")
    print(f"   SHIPPED whole-card mean ceiling share     : {st.mean(shipped_shares):.2%}")
    print(f"   what the superseded model MISSED          : {understated:.2%} of oracle")
    # A divergence check that cannot fail proves nothing. This one fails if the
    # fix is reverted, if the substitution stops producing a sole-held silent
    # class, or if the two models are accidentally the same object.
    divergence_ok = sum(costly) == len(list(SEEDS)) and understated > 0.01
    print(f"   -> {'PASS' if divergence_ok else 'FAIL'}: the whole-card model must "
          f"price the omission ABOVE the lie-only model here\n")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "card_belief_model.json").write_text(json.dumps({
        "control_current_template": {
            "seeds_with_costly_omission": sum(structural),
            "seeds_where_models_disagree": len(disagree),
            "passes": control_ok,
        },
        "divergence_disjoint_template": {
            "seeds_with_costly_omission": sum(costly),
            "superseded_lie_only_mean_share": st.mean(superseded_shares),
            "shipped_whole_card_mean_share": st.mean(shipped_shares),
            "missed_by_superseded_model": understated,
            "passes": divergence_ok,
        },
        "caveats": [
            "the divergence figures use coverage SUBSTITUTION into instances the "
            "current generator produced, so they inherit its segment mix — see "
            "check_template_pricing's caveat, which is that the mix OVERSTATES "
            "these candidates. The MISMATCH BETWEEN THE TWO MODELS is the finding "
            "here; the absolute levels are not.",
            "this compares two belief models on one lattice. It does not say which "
            "lattice to choose.",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'card_belief_model.json'}")
    return 0 if (control_ok and divergence_ok) else 1


def substitute(instance: dict[str, Any],
               template: tuple[str, str, str, str]) -> dict[str, Any]:
    """Return the instance with worker coverage replaced by `template`.

    Roles are DECLARED positionally by the template; the label permutation is
    recovered from the instance rather than re-derived.
    """
    lab = labels_of(instance)
    roles = ["_pred", "_succ", "_w2", "_w3"]
    coverage = {lab[r]: tuple(lab[ch] for ch in spec)
                for r, spec in zip(roles, template)}
    workers = []
    for worker in instance["workers"]:
        row = dict(worker)
        if worker["worker_id"] in coverage:
            row["irb_coverage"] = coverage[worker["worker_id"]]
            row["private_pd_calibration"] = {
                c: instance["class_calibration"][c] for c in coverage[worker["worker_id"]]}
        workers.append(row)
    return {**instance, "workers": workers}


if __name__ == "__main__":
    raise SystemExit(main())
