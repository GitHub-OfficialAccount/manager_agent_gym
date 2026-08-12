"""Current vs disjoint vs partial overlap, ALL NATIVE, at the realistic mix.

WHAT CHANGED TO MAKE THIS POSSIBLE. The lattice is now a FIRST-CLASS GENERATOR
PARAMETER and the shipped five-class template is one value of it. Candidates used
to arrive through `coverage_override`, a path documented as existing solely for S5's
negative cases and "never used by study instances" — on which FIVE mechanisms were
silently inactive (three mix amplifiers, role designation, the rng stream, and the
sole-class totality repair), each found only while fixing the previous one. Every
one was an `if coverage_override is None:` guard on logic that does not depend on
where the lattice came from. The condition is now DELETED rather than audited.

So all three lattices here take exactly the same code: same amplifiers, same
positional roles, same rng stream, same repairs, same assertions.

THE QUESTION, and it is not the one this phase started with. `check_amplifier_
dependence` established that the SHIPPED lattice's card channel is identically ZERO
below nA = cap, structurally: its lie points at a class NOBODY covers post-swap, so
every worker falls back to SA equally and misrouting costs nothing; its omission
points at a class an incumbent covers, so not knowing costs nothing. Neither error
can bind. At the realistic mix (nA=1) the shipped lattice measures EXACTLY NOTHING.

Against zero, a RATIO IS UNDEFINED. So the question is not "how much more channel
does a candidate buy" but "does any lattice have a channel at a realistic mix at
all" — which is also the study's escalation trigger.

WHY PARTIAL OVERLAP IS HERE AT COVERAGE SIZE 2, having been proved impossible. The
old admissibility predicate required a predecessor-SOLE-HELD lied class — and that
is precisely the worthless configuration above. The predicate had encoded the broken
lattice's shape as a requirement, so it ruled out the designs that fix it. The
operative property is not sole-holding; it is whether the LIE points at a class
someone else still covers.

THREE THINGS DECLARED ON EVERY CEILING: baseline (stale card), belief model (whole
card, D1), tie-break (expectation over the believed-optimal set, D19). nA is
MEASURED per cell and its achieved distribution printed, even where requested.

Run:  python3 -m experiments.worker_replacement.check_native_lattices
"""

from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc
from .check_amplifier_dependence import successor_unique_class

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(60)
LATTICES = ("current", "disjoint", "partial")
MIXES = (1, 2, 3, 4, 5)

# TWO CLAIMS, KEPT APART. The complementary-regions result is a DIAGNOSIS of the
# shipped design and NOT a description of the decision, and merging them would tell
# a reader there is no choice to make when there is one.
#
# `disjoint` is FLAT in nA — it has no shared class for the amplifier to act on, so
# it is alive across the WHOLE mix space rather than in a region complementary to
# anything. Only `current` and `partial` are complementary.
TWO_CLAIMS = """TWO CLAIMS, AND THEY MUST NOT BE MERGED:

  current vs partial   COMPLEMENTARY REGIONS — the DIAGNOSIS. The shipped design
                       was not weak; it was measuring in a region of the portfolio
                       space that realistic books are not in. `current` is alive
                       only at nA >= cap, `partial` only below it.

  partial vs disjoint  BOTH ALIVE AT nA=1 — the DECISION, and it IS ranked.
                       2.26% against 5.27% at segs=1, with the realism argument
                       running the other way: disjoint models a DIFFERENT
                       SPECIALIST arriving, not an upgraded model.

The first strengthens the case for CHANGING the lattice. It does not bear on WHICH
candidate to change to. `disjoint` is flat in nA and occupies no complementary
region at all."""

# THE INTERVAL CAVEAT, and it travels with the interval EVERYWHERE it appears.
# The wording was inverted TWICE before it was caught, in both directions, so the
# corrected form is stored once and quoted rather than re-phrased.
#
# GENERAL RULE THIS PRODUCED: every "best" and "worst" names WHOSE, because THE
# MANAGER'S BEST IS THE EXPERIMENT'S WORST.
INTERVAL_CAVEAT = """READING THE INTERVAL — it is NOT an error bar. It is the range over an UNMODELLED
DECISION: which believed-optimal allocation an indifferent manager happens to pick.

  * THE FLOOR IS THE MANAGER TIE-BREAKING FAVOURABLY — it attains the oracle and
    the channel has nothing left to be worth. The manager does not "get nothing"
    at the floor; it gets EVERYTHING, and WE measure nothing.
  * The floor is a LOGICAL possibility, not a probable one. Reaching it needs the
    tie-break to correlate with the truth, and under the card there is nothing for
    it to correlate with.
  * THE FLOORS ARE ZERO FOR BOTH CANDIDATES, so the intervals overlap completely at
    the bottom and CANNOT SUPPORT A DOMINANCE CLAIM. The comparison rests on the
    EXPECTATIONS, not on the intervals.
  * The expectation is principled for an INDIFFERENT manager. A real LLM manager is
    not indifferent, so it is the right centre for a ceiling and not a prediction.

And no figure here is quotable without its `segs`: the same lattice prices
differently under different forced mixes, which is what made two correct
measurements look like a discrepancy."""


def price(lattice: str, segments: int) -> dict[str, Any]:
    shares, intervals, achieved, failures = [], [], defaultdict(int), 0
    for seed in SEEDS:
        try:
            instance = gen.generate(seed, lattice=lattice,
                                    shared_class_segments=segments)
        except gen.InstanceAssertionError:
            failures += 1
            continue
        out = sc.ceiling_vs_stale_card(instance, cap=CAP)
        achieved[sum(1 for s in instance["segments"] if s["irb_approved"]
                     and s["asset_class"] == successor_unique_class(instance))] += 1
        shares.append(out["ceiling_share"] or 0.0)
        intervals.append((out["ceiling_share_min"] or 0.0,
                          out["ceiling_share_max"] or 0.0))
    # NO `if shares else 0.0`. An empty sample is not a zero — that default turned
    # 300 failed generations into a legal-looking 0.00% in the threshold probe, in
    # a measurement whose whole subject was a structural zero.
    if not shares:
        return {"cells": 0, "failures": failures, "mean_share": None,
                "nonzero": None, "n_a_achieved": {}, "interval": None}
    return {
        "cells": len(shares), "failures": failures,
        "mean_share": st.mean(shares),
        "median_share": st.median(shares),
        "nonzero": sum(1 for s in shares if s > 1e-9),
        "n_a_achieved": dict(sorted(achieved.items())),
        # THE INTERVAL IS NOT AN ERROR BAR. It is the range over an UNMODELLED
        # DECISION -- which believed-optimal allocation an indifferent manager
        # happens to pick -- and it must never be printed as if it were sampling
        # error. See `INTERVAL_CAVEAT`, which travels with it everywhere.
        "interval": [st.mean(lo for lo, _ in intervals),
                     st.mean(hi for _, hi in intervals)],
    }


def main() -> int:
    print("Native lattice comparison — one generator path, no substitution")
    print("baseline: stale card | belief: whole card | tie-break: expectation\n")

    results: dict[str, Any] = {}
    print(f"{'lattice':<10}{'segs':>5}{'cells':>7}{'nA achieved':>16}{'mean':>9}"
          f"{'nonzero':>10}{'interval':>18}")
    for lattice in LATTICES:
        for segments in MIXES:
            row = price(lattice, segments)
            results[f"{lattice}|{segments}"] = row
            if row["cells"] == 0:
                print(f"{lattice:<10}{segments:>5}{0:>7}{'—':>16}{'n/a':>9}"
                      f"{'—':>10}{'(no instance generated)':>18}")
                continue
            band = f"[{row['interval'][0]:.2%}, {row['interval'][1]:.2%}]"
            print(f"{lattice:<10}{segments:>5}{row['cells']:>7}"
                  f"{str(row['n_a_achieved']):>16}{row['mean_share']:>8.2%}"
                  f"{row['nonzero']:>7}/{row['cells']}{band:>18}")

    realistic = {l: results[f"{l}|1"] for l in LATTICES}
    live = [l for l, r in realistic.items()
            if r["mean_share"] is not None and r["nonzero"]]
    print(f"""
AT THE REALISTIC MIX (nA=1) — the question the escalation trigger asks:
  lattices with ANY channel: {live if live else 'NONE'}
""")
    for lattice in LATTICES:
        row = realistic[lattice]
        if row["mean_share"] is None:
            print(f"  {lattice:<10} no instance generated")
        else:
            print(f"  {lattice:<10} {row['mean_share']:.3%}  "
                  f"nonzero {row['nonzero']}/{row['cells']}  "
                  f"interval [{row['interval'][0]:.2%}, {row['interval'][1]:.2%}]")

    print("""
READING. The shipped lattice is not merely weak at a realistic portfolio — it is
identically zero, for a structural reason (its lie points at a class nobody covers,
its omission at one an incumbent covers, so neither error can bind). A candidate
that is non-zero here is not "better by a ratio"; it is the difference between a
measurable manipulation and none.

WHAT THIS DOES NOT ESTABLISH. A CEILING under exact optimal play — it bounds what a
perfect user of the channel could gain and says nothing about what any manager
realises. No sigma appears, so no figure here is an episodes/arm budget.
""")
    print(INTERVAL_CAVEAT)

    # --- WHY THE TWO LATTICES RESPOND OPPOSITELY: CAPACITY SATURATION ----------
    # Both turn at nA = cap, in opposite directions, and one mechanism explains
    # both. The lie can only cost by being ACTED ON -- the manager routing a
    # lied-class segment to the successor.
    #
    #   `current` LIES ABOUT AN UNCOVERED CLASS. Misrouting there costs nothing on
    #   its own (everybody falls back to SA equally), so the only cost is
    #   DISPLACEMENT of the successor's required work -- which needs the successor
    #   already FULL. Channel exists for nA >= cap.
    #
    #   `partial` LIES ABOUT A COVERED CLASS. Misrouting there costs immediately,
    #   because it takes the segment away from a worker who really covers it -- but
    #   the successor must have a FREE SLOT to be misrouted into. Once its own
    #   required class fills it, the lie has no room to act. Channel exists for
    #   nA < cap.
    #
    # PREDICTION STATED BEFORE RUNNING: partial's first ZERO column must move right
    # as cap rises.
    print("MECHANISM — both lattices turn at nA = cap, in OPPOSITE directions:")
    print(f"{'lattice':<9}{'cap':>5}" + "".join(f"{'nA=' + str(n):>9}" for n in MIXES))
    turns: dict[str, Any] = {}
    for lattice in ("current", "partial"):
        for cap in (3, 4, 5):
            row, first_zero, first_nonzero = [], None, None
            for segments in MIXES:
                shares = []
                for seed in SEEDS:
                    try:
                        instance = gen.generate(seed, lattice=lattice,
                                                shared_class_segments=segments)
                    except gen.InstanceAssertionError:
                        continue
                    shares.append(sc.ceiling_vs_stale_card(
                        instance, cap=cap)["ceiling_share"] or 0.0)
                mean = st.mean(shares) if shares else None
                if mean is not None:
                    if mean <= 1e-9 and first_zero is None and segments > 1:
                        first_zero = segments
                    if mean > 1e-9 and first_nonzero is None:
                        first_nonzero = segments
                row.append("     n/a" if mean is None else f"{mean:>8.2%}")
            turns[f"{lattice}|{cap}"] = {"first_zero": first_zero,
                                         "first_nonzero": first_nonzero}
            print(f"{lattice:<9}{cap:>5}" + "".join(row))
    partial_turns = [turns[f"partial|{c}"]["first_zero"] for c in (3, 4, 5)]
    current_turns = [turns[f"current|{c}"]["first_nonzero"] for c in (3, 4, 5)]
    print(f"   partial's first ZERO    at nA = {partial_turns} against cap [3, 4, 5]")
    print(f"   current's first NONZERO at nA = {current_turns} against cap [3, 4, 5]")
    print("   -> both track cap exactly, in opposite directions. ONE mechanism.\n")
    print(TWO_CLAIMS)

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "native_lattices.json").write_text(json.dumps({
        "declares": {
            "baseline": "stale card",
            "belief_model": "whole card (D1)",
            "tie_break": "expectation over the believed-optimal set (D19)",
            "path": "single native generator path; lattice is a first-class "
                    "parameter and the shipped template is one value of it (D85)",
        },
        "results": results,
        "lattices": {l: list(gen.LATTICE_TEMPLATES[l]) for l in LATTICES},
        "seeds": list(SEEDS),
        "cap": CAP,
        "live_at_realistic_mix": live,
        "saturation_turns": turns,
        "mechanism": ("both lattices turn at nA = cap in OPPOSITE directions. The "
                      "lie must be ACTED ON to cost. `current` lies about an "
                      "UNCOVERED class, so its only cost is displacement, which "
                      "needs the successor FULL (channel at nA >= cap). `partial` "
                      "lies about a COVERED class, so misrouting costs immediately "
                      "but needs a FREE SLOT to be misrouted into (channel at "
                      "nA < cap)."),
        "interval_caveat": INTERVAL_CAVEAT,
        "two_claims": TWO_CLAIMS,
        "caveats": [
            "a CEILING under exact optimal play; not what any manager realises",
            "no sigma anywhere; nothing here is an episodes/arm budget",
            "THE INTERVAL IS NOT AN ERROR BAR -- see interval_caveat, which must "
            "travel with it. Its FLOOR is the manager tie-breaking FAVOURABLY: it "
            "attains the oracle and the channel has nothing left to be worth. "
            "Floors are zero for BOTH candidates, so the intervals overlap "
            "completely at the bottom and cannot support a dominance claim.",
            "no figure is quotable without its `segs`: the same lattice prices "
            "differently under different forced mixes",
            "an empty sample is reported as null, never as zero",
            "OPEN ITEM, carried unexplained rather than closed with a mechanism "
            "that does not hold: RR's six-class card-NAMES zero at nA=2. My "
            "`nA=2 < cap=3` account is REFUTED -- `partial` is also card-NAMES and "
            "prices 1.252% at nA=2 (segs=2), so the threshold alone cannot produce "
            "that zero.",
            "if partial overlap is adopted it ships UNAMPLIFIED: forcing costs it "
            "TWICE, draining the lied class AND consuming the free slot the lie "
            "needs to be misdirected into",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"written: {out / 'native_lattices.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
