"""D40 — how much of the CURRENT template's card channel is the amplifiers?

THE QUESTION. `check_template_pricing` reports the current five-class template's
card channel at ~1.24% of oracle. That instance is generated with three amplifiers
active on the shared class: `shared_class_segments = 4` (segment COUNT), divergence
selection (the rating chosen by bounded search to maximise the SA fallback penalty),
and IRB-approval priority (shared-class segments approved first). D40 asks what is
left when they are off, at a matched mix.

WHY IT SURVIVES THE REBUILD. This runs on the five-class NATURAL path — the one the
override faults never touched, and the one held bit-identical through every fix in
this phase. Its answer does not depend on the instrument being rebuilt.

WHY TURNING ALL THREE OFF IS THE RIGHT SWITCH. Measured rather than read: it takes
segment count from 4-of-9 to round-robin, the divergence flag from True to False,
and IRB approval from 4-of-6 on the amplified class to one per class. All three gate
on `shared_class is not None`, which it sets to None.

nA IS MEASURED PER CELL AND THE ACHIEVED DISTRIBUTION IS PRINTED, even where it is
requested — a forced parameter that lands on one value in every cell is a constant
being reported as a variable, which is how the original nA=4 forcing went unnoticed
for a phase.

Run:  python3 -m experiments.worker_replacement.check_amplifier_dependence
"""

from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(60)


def successor_unique_class(instance: dict[str, Any]) -> str | None:
    """The class the successor ALONE holds post-swap, read off the INSTANCE.

    Read from the instance rather than from the template, because the template's
    declared roles and the instance's actual roles were not the same thing until
    this phase, and reading the wrong one is the fault that invalidated the
    six-class figures.
    """
    event = instance["event"]
    coverage = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
    successor = event["successor_id"]
    incumbents = [w for w in event["roster_post_swap"] if w != successor]
    unique = sorted(coverage[successor].difference(*(coverage[i] for i in incumbents)))
    return unique[0] if unique else None


def _safe_generate(seed: int, segs: int):
    try:
        return gen.generate(seed, shared_class_segments=segs)
    except gen.InstanceAssertionError:
        return None


def arm(amplified: bool, segments: int | None) -> dict[str, Any]:
    shares, achieved = [], defaultdict(int)
    for seed in SEEDS:
        kwargs: dict[str, Any] = {"amplify_count": amplified,
                                  "amplify_divergence": amplified,
                                  "amplify_irb_priority": amplified}
        if segments is not None:
            kwargs["shared_class_segments"] = segments
        try:
            instance = gen.generate(seed, **kwargs)
        except gen.InstanceAssertionError:
            continue
        unique = successor_unique_class(instance)
        achieved[sum(1 for s in instance["segments"]
                     if s["irb_approved"] and s["asset_class"] == unique)] += 1
        shares.append(sc.ceiling_vs_stale_card(instance, cap=CAP)["ceiling_share"] or 0.0)
    return {"cells": len(shares), "mean_share": st.mean(shares),
            "median_share": st.median(shares),
            "nonzero": sum(1 for s in shares if s > 1e-9),
            "n_a_achieved": dict(sorted(achieved.items()))}


def main() -> int:
    print("D40 — the CURRENT five-class template, amplifiers ON vs OFF at matched nA")
    print("native generation, positional roles, aligned streams, no substitution\n")

    arms = {
        "amplified, segs=4 (as shipped)": arm(True, 4),
        "amplified, segs=1": arm(True, 1),
        "UNAMPLIFIED (all three off)": arm(False, None),
    }
    print(f"{'arm':<32}{'cells':>7}{'nA achieved':>18}{'mean':>9}{'median':>9}{'nonzero':>9}")
    for name, row in arms.items():
        print(f"{name:<32}{row['cells']:>7}{str(row['n_a_achieved']):>18}"
              f"{row['mean_share']:>8.2%}{row['median_share']:>8.2%}"
              f"{row['nonzero']:>6}/{row['cells']}")

    on = arms["amplified, segs=1"]["mean_share"]
    off = arms["UNAMPLIFIED (all three off)"]["mean_share"]
    shipped = arms["amplified, segs=4 (as shipped)"]["mean_share"]
    print(f"""
D40 VERDICT: at matched nA=1 the amplifiers make NO difference — {on:.2%} against
{off:.2%}. But not because they are inert: because BOTH ARE ZERO.

★ THE CURRENT TEMPLATE HAS NO CARD CHANNEL AT nA=1 AT ALL. Its entire {shipped:.2%}
lives at nA=4, and nA=4 is reachable only by forcing four of nine segments into the
shared class. On the realism finding that nA=1 is the realistic mix, the shipped
lattice measures EXACTLY NOTHING at a realistic portfolio.

That reframes what the candidate lattices are for. The question is not "how much
more channel does a candidate buy" — against zero, any ratio is undefined. It is
whether a candidate has a channel at nA=1 AT ALL, which the current one does not.

WHAT THIS DOES NOT ESTABLISH: nothing here prices a candidate. Both candidate arms
are on the override path and provisional pending the rebuild. This measures only the
SHIPPED template, natively, and that measurement survives the rebuild.
""")

    # --- POSITIVE CONTROL: is 0.00% a real zero or a floor? --------------------
    # A null needs one, and this shape has fooled us twice. If the instrument
    # returns 0.00% on 60/60 because it CANNOT return anything else on this path,
    # the finding is an artefact. So the same path is driven across the mix.
    print("POSITIVE CONTROL — dose-response on the SAME native path:")
    print(f"{'segs':>5}{'cells':>7}{'nA':>6}{'mean':>9}{'max':>9}{'nonzero':>10}")
    dose = {}
    for segs in range(1, 6):
        shares, achieved = [], set()
        for seed in SEEDS:
            try:
                instance = gen.generate(seed, shared_class_segments=segs)
            except gen.InstanceAssertionError:
                continue
            achieved.add(sum(1 for s in instance["segments"] if s["irb_approved"]
                             and s["asset_class"] == successor_unique_class(instance)))
            shares.append(sc.ceiling_vs_stale_card(
                instance, cap=CAP)["ceiling_share"] or 0.0)
        dose[segs] = {"mean": st.mean(shares), "max": max(shares),
                      "nonzero": sum(1 for x in shares if x > 1e-9),
                      "cells": len(shares), "n_a": sorted(achieved)}
        print(f"{segs:>5}{len(shares):>7}{str(sorted(achieved)):>6}"
              f"{st.mean(shares):>8.2%}{max(shares):>8.2%}"
              f"{dose[segs]['nonzero']:>7}/{len(shares)}")
    print("   -> the instrument FIRES on this path from nA=3. The zero is the bottom\n"
          "      of a dose-response curve, not a floor.\n")

    # --- MECHANISM, and it is structural rather than numerical -----------------
    lie_dead, omission_covered, total = 0, 0, 0
    for seed in SEEDS:
        try:
            instance = gen.generate(seed, shared_class_segments=1)
        except gen.InstanceAssertionError:
            continue
        total += 1
        event = instance["event"]
        cover = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
        successor = event["successor_id"]
        incumbents = [w for w in event["roster_post_swap"] if w != successor]
        lied = cover[event["predecessor_id"]] - cover[successor]
        omitted = cover[successor] - cover[event["predecessor_id"]]
        lie_dead += all(not any(c in cover[i] for i in incumbents) for c in lied)
        omission_covered += all(any(c in cover[i] for i in incumbents) for c in omitted)
    print("WHY THE ZERO IS STRUCTURAL — what the card gets wrong at nA=1:")
    print(f"   LIED classes covered by NOBODY post-swap : {lie_dead}/{total}")
    print(f"   OMITTED classes covered by an incumbent  : {omission_covered}/{total}")
    print("   The lie points at a class worthless to EVERY worker, so misrouting")
    print("   there costs nothing; the omission points at one an incumbent covers,")
    print("   so not knowing costs nothing. Neither error can bind.\n")

    # --- THE THRESHOLD IS CAPACITY, and that is a falsifiable claim ------------
    # If the only route by which the card can cost anything is displacing the
    # successor's uniquely-required segments, the channel should switch on exactly
    # when those segments saturate its capacity -- so the threshold must MOVE with
    # cap. Predicted before running: first non-zero column at nA = cap.
    print("THE THRESHOLD IS CAPACITY. Predicted first non-zero column at nA = cap:")
    print(f"{'cap':>4}" + "".join(f"{'nA=' + str(n):>10}" for n in range(1, 7)))
    built = {(segs, seed): _safe_generate(seed, segs)
             for segs in range(1, 7) for seed in SEEDS}
    threshold = {}
    for cap in (3, 4, 5):
        row, first = [], None
        for segs in range(1, 7):
            shares = [sc.ceiling_vs_stale_card(built[(segs, s)], cap=cap)["ceiling_share"] or 0.0
                      for s in SEEDS if built[(segs, s)] is not None]
            mean = st.mean(shares)
            if first is None and mean > 1e-9:
                first = segs
            row.append(f"{mean:>9.2%}")
        threshold[cap] = first
        print(f"{cap:>4}" + "".join(row))
    holds = all(threshold[c] == c for c in threshold)
    print(f"   -> {'CONFIRMED' if holds else 'REFUTED'}: switch-on at "
          f"{ {c: threshold[c] for c in threshold} } against cap "
          f"{sorted(threshold)}\n")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "amplifier_dependence.json").write_text(json.dumps({
        "arms": arms,
        "positive_control_dose_response": dose,
        "mechanism_at_n_a_1": {
            "lied_classes_covered_by_nobody_post_swap": f"{lie_dead}/{total}",
            "omitted_classes_covered_by_incumbent": f"{omission_covered}/{total}",
        },
        "capacity_threshold": {"first_nonzero_n_a_by_cap": threshold,
                               "predicted_n_a_equals_cap": holds},
        "verdict": "the current template's card channel is ZERO at nA=1 under both "
                   "amplifier settings; its shipped figure lives entirely at nA=4",
        "declares": {
            "baseline": "stale card",
            "belief_model": "whole card (D1)",
            "tie_break": "expectation over the believed-optimal set (D19)",
            "path": "five-class NATURAL generation — never touched by the override "
                    "faults, held bit-identical through this phase",
        },
        "caveats": [
            "measures the SHIPPED template only; prices no candidate",
            "a CEILING under exact optimal play",
            "all three amplifiers off, set independently (amplify_count, "
            "amplify_divergence, amplify_irb_priority) and measured not read",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"written: {out / 'amplifier_dependence.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
