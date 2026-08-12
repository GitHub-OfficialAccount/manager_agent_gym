"""Pricing candidate lattice templates — offline, no generator change.

The card channel prices at 1.24% of oracle / 0.16sigma on the CURRENT template,
below detectability at any affordable n. Two candidate repairs are priced here
against the same instances.

HOW THIS PRICES A TEMPLATE WITHOUT CHANGING THE GENERATOR. A lattice change alters
only WHO COVERS WHAT. The segments — their classes, ratings, exposures and
IRB-applicability — are untouched. So each existing instance is re-used with its
worker coverage sets SUBSTITUTED, and the seed's own label permutation is
RECOVERED from the instance rather than re-derived, so the new coverage lands on
the same classes the segment mix was built around.

THE CAVEAT THAT GOES WITH EVERY NUMBER BELOW, AND AN EARLIER VERSION OF IT WAS
BACKWARDS. It said the old mix "most likely UNDERSTATES" the candidates. It
OVERSTATES them, and by a known amount.

`labels_of()` recovers `a` as the CURRENT template's shared class — the one
`shared_class_segments = 4` forces four segments into — and the disjoint candidate
assigns `w1 (SUCCESSOR) = {a, b}`. So the successor-unique class lands on the
forced class in EVERY instance: measured nA = 4 in 30 of 30 seeds. nA is the
number of IRB segments in the successor-unique class and it is what the effect
scales with. RR's independent probe (10 seeds x all 120 labelings, 1200 cells)
decomposes it:

    nA = 0    0.16 sigma    32% of labelings    <- IDENTICAL to the current template
    nA = 1    0.44 sigma    natural round-robin mix
    nA = 4    1.02 sigma    where this file's headline figure lives

So the headline is the most favourable case in the range, not a property of the
template. `nA` only ever takes 0, 1 or 4 and never 2 or 3: the fingerprint of the
forcing. AND THE 30/30-NONZERO RESULT GOES WITH IT — every seed showed an effect
because nA = 4 in every seed. A repair that fires on every single seed is not a
repair with a distribution; it is a constant being reported as a finding.

The honest statement is a range with a dependency: the disjoint template is worth
between NOTHING and ~6x the current ceiling depending on one unset parameter — and
that same parameter sets how well a dump-on-newcomer shortcut does, so the two
constraints pull on the same knob. Deferring the mix does not leave it neutral; it
silently adopts the most favourable value. See `check_mix_sweep.py`, which prices
across the mix instead of inheriting it.

WHAT THIS STILL DOES NOT PRICE: substitution re-uses instances the CURRENT
generator produced, so it inherits that generator's forcing. A revised generator
has no shared class to force anything into.

WHAT IS PRICED: optimal play under the truth minus optimal play under the stale
card, scored in the true world. A CEILING. It bounds what a perfect user of the
channel could gain; it does not say any manager gains it.

Run:  python3 -m experiments.worker_replacement.check_template_pricing
"""

from __future__ import annotations

import json
import statistics as st
from itertools import product
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
CAP = 3
SEEDS = range(30)

# Roles are DECLARED, in template order: predecessor, successor, incumbent,
# incumbent. The current path derives the swap pair from coverage instead, which
# cannot survive these templates — see records/L9.
TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    # w0={a,e} w1={a,b} w2={b,c} w3={c,d} — the lied-about class and the
    # sole-held class are THE SAME CLASS, which is why the repair looks impossible.
    "current": ("ae", "ab", "bc", "cd"),
    # Predecessor and successor share NOTHING. Two free predecessor slots, so d is
    # sole-held (interior spread) and e is singly covered (the lie costs coverage).
    # a is successor-ONLY, so the card's SILENCE costs too.
    "proposed_disjoint": ("de", "ab", "ce", "cb"),
    # LS's realism variant: partial overlap on a. PROVABLY cannot also sole-hold a
    # class at coverage size 2 — the predecessor's other slot is the only lied
    # class and cannot be both sole-held and singly-covered.
    "partial_overlap": ("ae", "ab", "ce", "cb"),
}


def labels_of(instance: dict[str, Any]) -> dict[str, str]:
    """Recover this seed's label permutation from the instance it produced.

    The generator permutes class labels per seed. Re-deriving the permutation
    would require reproducing its rng state; recovering it from the coverage sets
    the instance already carries is exact and needs nothing from the generator.
    """
    event = instance["event"]
    by_id = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
    pred, succ = event["predecessor_id"], event["successor_id"]
    incumbents = [w for w in event["roster_post_swap"] if w != succ]
    a = (by_id[pred] & by_id[succ]).pop()
    e = (by_id[pred] - {a}).pop()
    b = (by_id[succ] - {a}).pop()
    w2 = next(i for i in incumbents if b in by_id[i])
    c = (by_id[w2] - {b}).pop()
    w3 = next(i for i in incumbents if i != w2)
    d = (by_id[w3] - {c}).pop()
    return {"a": a, "b": b, "c": c, "d": d, "e": e,
            "_pred": pred, "_succ": succ, "_w2": w2, "_w3": w3}


def card_ceiling_for_template(seed: int, template: tuple[str, str, str, str]) -> dict[str, Any]:
    instance = gen.generate(seed)
    lab = labels_of(instance)
    calibration = instance["class_calibration"]
    segments = instance["segments"]

    roles = ["_pred", "_succ", "_w2", "_w3"]
    coverage = {lab[r]: tuple(lab[ch] for ch in spec)
                for r, spec in zip(roles, template)}
    # Substitute ONLY the coverage. Everything else — ids, and the class-level
    # calibration a worker holds for the classes it is approved for — comes from
    # the real instance, so the price is of the LATTICE and of nothing else. The
    # calibration is class-level since R1, so a worker approved for a class holds
    # exactly the shared table's entry for it.
    real = {w["worker_id"]: w for w in instance["workers"]}
    workers = []
    for r in roles:
        wid = lab[r]
        row = dict(real[wid])
        row["irb_coverage"] = coverage[wid]
        row["private_pd_calibration"] = {
            c: instance["class_calibration"][c] for c in coverage[wid]}
        workers.append(row)
    by_id = {w["worker_id"]: w for w in workers}

    predecessor, successor = lab["_pred"], lab["_succ"]
    roster = [by_id[lab[r]] for r in ("_succ", "_w2", "_w3")]
    card_claims = set(coverage[predecessor])

    def true_score(segment, worker):
        return sc.s(segment, worker, calibration)

    # THE CARD HAS TWO ERRORS, NOT ONE, AND THE FIRST VERSION MODELLED ONLY ONE.
    # It gave the successor a believed 1.0 where the card FALSELY CLAIMS coverage,
    # and otherwise fell through to the TRUE score — so where the card is SILENT
    # about a class the successor really covers, the manager was credited with
    # knowing it anyway. That is the card's OMISSION, and under the current
    # template it costs nothing (the silent class is always incumbent-covered, 60
    # of 60), which is why the omission never mattered and the model survived.
    # Under a template where the successor SOLE-holds a silent class it is the
    # larger half of the effect, and a model blind to it prices exactly the
    # property the template was designed to add at zero.
    believed_coverage = card_claims          # the manager believes the card, entire
    succ_as_believed = dict(by_id[successor])
    succ_as_believed["irb_coverage"] = tuple(believed_coverage)
    succ_as_believed["private_pd_calibration"] = {
        c: instance["class_calibration"][c] for c in believed_coverage}

    def believed(segment, worker):
        if worker["worker_id"] != successor:
            return sc.s(segment, worker, calibration)
        # Scored as the CARD describes the successor: false claims grant coverage
        # it lacks, and omissions withhold coverage it has.
        return sc.s(segment, succ_as_believed, calibration)

    def best(scoref):
        best_v, best_a = -1.0, ()
        for combo in product(range(len(roster)), repeat=len(segments)):
            if any(combo.count(i) > CAP for i in range(len(roster))):
                continue
            value = sum(scoref(sg, roster[w]) for sg, w in zip(segments, combo))
            if value > best_v:
                best_v, best_a = value, combo
        return best_v, best_a

    true_value, _ = best(true_score)
    _, card_alloc = best(believed)
    realised = sum(true_score(sg, roster[w])
                   for sg, w in zip(segments, card_alloc))
    return {"seed": seed, "true_optimum": true_value, "realised": realised,
            "ceiling": true_value - realised,
            "share": (true_value - realised) / true_value}


def main() -> int:
    print("Pricing candidate lattice templates — offline, no generator change\n")
    print("CAVEAT ON EVERY FIGURE: the segment mix over-weights the class the OLD")
    print("template shared, and the disjoint candidate's successor-unique class")
    print("lands on it in 30/30 seeds. These figures are the MOST FAVOURABLE case")
    print("in the range, not a property of the template — they OVERSTATE it.")
    print("See check_mix_sweep.py, which prices across the mix.\n")

    sigma = 0.0768   # measured pre-L1; stale, used only to scale, never to size
    results: dict[str, Any] = {}
    print(f"{'template':<20} {'nonzero':>9} {'mean share':>11} {'nonzero mean':>13} "
          f"{'max':>8} {'~sigma':>8}")
    for name, template in TEMPLATES.items():
        rows = [card_ceiling_for_template(seed, template) for seed in SEEDS]
        shares = [r["share"] for r in rows]
        nonzero = [s for s in shares if s > 1e-9]
        mean = st.mean(shares)
        # The ceiling is a share of oracle; sigma is a share of oracle too, so the
        # ratio is the effect in sigma units. Sigma is PRE-L1 and stale — it scales
        # the comparison and must not size a suite.
        results[name] = {"rows": rows, "mean_share": mean,
                         "n_nonzero": len(nonzero),
                         "nonzero_mean": st.mean(nonzero) if nonzero else 0.0,
                         "max": max(shares), "sigma_units": mean / sigma}
        print(f"{name:<20} {len(nonzero):>6}/{len(rows):<2} {mean:>10.2%} "
              f"{results[name]['nonzero_mean']:>12.2%} {max(shares):>7.2%} "
              f"{mean / sigma:>7.2f}")

    base = results["current"]["mean_share"]
    print(f"\nrelative to the current template:")
    for name in TEMPLATES:
        if name == "current":
            continue
        factor = results[name]["mean_share"] / base if base else float("inf")
        print(f"   {name:<20} {factor:>6.1f}x the current ceiling")

    print("\nSTRUCTURAL RESULT, proved by enumeration and independent of pricing:")
    print("   at COVERAGE_SIZE=2 — for ANY number of classes — a template CANNOT")
    print("   have partial predecessor/successor overlap AND a predecessor-sole-held")
    print("   class AND a singly-covered lie. The predecessor's non-shared slot is")
    print("   the only lied class, and it cannot be both sole-held (0 coverers) and")
    print("   singly covered (1). At COVERAGE_SIZE=3 with 6 classes, 6480 templates")
    print("   satisfy all three — but a sixth asset class needs its own SA weights.")
    print("   So partial overlap and 'the swap creates the coverage gap' are")
    print("   MUTUALLY EXCLUSIVE at the current coverage size. That is a")
    print("   combinatorial fact, not a preference.")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "template_pricing.json").write_text(json.dumps({
        "templates": {k: list(v) for k, v in TEMPLATES.items()},
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                    for k, v in results.items()},
        "per_seed": {k: v["rows"] for k, v in results.items()},
        "sigma_used": sigma,
        "caveats": [
            "the segment mix OVERSTATES these candidates, it does not understate "
            "them: labels_of recovers `a` as the OLD template's shared class, "
            "shared_class_segments=4 forces four segments into it, and the "
            "disjoint candidate's successor-unique class IS `a` — so nA=4 in "
            "30/30 seeds, the most favourable point in the range. RR's "
            "decomposition: nA=0 -> 0.16 sigma (identical to current), nA=1 -> "
            "0.44, nA=4 -> 1.02. The 30/30-nonzero result is the same artifact: "
            "a constant, not a distribution. See check_mix_sweep.py.",
            "sigma is the PRE-L1 measurement and must not size a suite",
            "a CEILING: optimal play under truth minus optimal play under the "
            "card; it does not say any manager realises it",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'template_pricing.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
