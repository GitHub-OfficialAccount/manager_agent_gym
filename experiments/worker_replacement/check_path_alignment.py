"""Do the two generation paths produce the SAME instance from the same lattice?

THE TEST. Take a seed's own naturally-generated lattice and hand it straight back
through `coverage_override`. Nothing about the instance has been asked to change,
so every field must be identical. Anything that differs is a path divergence.

WHY THIS EXISTS. FOUR of them were found in one afternoon, each silent, each
found only because the next one was being fixed:

  1. MIX FORCING     — `shared_class_segments` ignored on the override path, and
                       with it divergence selection and IRB-approval priority:
                       THREE amplifiers, not one;
  2. ROLES           — `_designate_swap_pair` re-derived predecessor and successor
                       instead of reading declared positions, so seed 0 came back
                       as (w1, w2, corporate) instead of (w0, w1, retail) and its
                       ceiling as 7.08% instead of 0.00%;
  3. RNG STREAM      — the template path drew a label permutation and the override
                       path did not, so every downstream draw diverged and the two
                       could not be paired seed-for-seed at all;
  4. TOTALITY REPAIR — the sole-class rating re-draw was gated off, so ASSERTION 7
                       failed on 27 of 60 seeds handed their OWN lattice back.
                       That was the whole "survivorship filter" on the six-class
                       arm: not a fact about six classes, but a repair switched off
                       for every instance six classes can be built from.

Each was a `if coverage_override is None:` guard on something that had nothing to
do with where the lattice came from. The debt list predicted #2 by name and
recorded its trigger — *"it must be retired if the lattice changes"* — and the
lattice changed without the record being re-read.

So this is an ACCEPTANCE, not a diagnostic. A fifth divergence should fail a check
rather than be discovered by whoever happens to run a round-trip next.

Run:  python3 -m experiments.worker_replacement.check_path_alignment
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path
from typing import Any

from . import finance_generator as gen
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent
SEEDS = range(60)
CAP = 3

# Fields compared field-by-field rather than by whole-dict equality, so a failure
# NAMES what diverged instead of only reporting that something did.
def instance_fingerprint(instance: dict[str, Any]) -> dict[str, Any]:
    event = instance["event"]
    ids = [w["worker_id"] for w in instance["workers"]]
    params = instance["parameters"]
    return {
        "rng_checkpoint": params["rng_checkpoint_post_lattice"],
        "predecessor_index": ids.index(event["predecessor_id"]),
        "successor_index": ids.index(event["successor_id"]),
        "swap_shared_class": event["swap_shared_class"],
        "mix_amplified_class": params["mix_amplified_class"],
        "divergence_selection": params["shared_class_divergence_selection"],
        "segment_classes": [s["asset_class"] for s in instance["segments"]],
        "segment_ratings": [s["rating"] for s in instance["segments"]],
        "irb_approved": [s["irb_approved"] for s in instance["segments"]],
        "calibration": instance["class_calibration"],
        "coverage": [tuple(w["irb_coverage"]) for w in instance["workers"]],
    }


def main() -> int:
    print("Path alignment: a seed's OWN lattice handed back through the override\n"
          "path must reproduce the natural instance EXACTLY.\n")

    generated, failed, divergences = 0, [], {}
    ceilings_natural, ceilings_override = [], []
    for seed in SEEDS:
        natural = gen.generate(seed)
        coverage = [tuple(w["irb_coverage"]) for w in natural["workers"]]
        try:
            round_trip = gen.generate(seed, coverage_override=coverage)
        except gen.InstanceAssertionError as exc:
            failed.append({"seed": seed, "assertion": str(exc).split("—")[0].strip()})
            continue
        generated += 1

        left, right = instance_fingerprint(natural), instance_fingerprint(round_trip)
        for field in left:
            if left[field] != right[field]:
                divergences.setdefault(field, []).append(seed)

        a = sc.ceiling_vs_stale_card(natural, cap=CAP)["ceiling_share"] or 0.0
        b = sc.ceiling_vs_stale_card(round_trip, cap=CAP)["ceiling_share"] or 0.0
        ceilings_natural.append(a)
        ceilings_override.append(b)
        if abs(a - b) > 1e-12:
            divergences.setdefault("ceiling_share", []).append(seed)

    print(f"round-tripped: {generated}/{len(list(SEEDS))} seeds")
    if failed:
        print(f"FAILED TO GENERATE: {len(failed)}")
        for row in failed[:5]:
            print(f"   seed {row['seed']}: {row['assertion']}")
    if divergences:
        print("\nDIVERGENT FIELDS — each is a path difference on an identical lattice:")
        for field, seeds in sorted(divergences.items()):
            print(f"   {field:<22} {len(seeds)} seed(s), e.g. {seeds[:5]}")
    else:
        print("\nno divergent field on any round-tripped seed")

    ok = not divergences and not failed
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — the two paths "
          f"{'agree on every field and every seed' if ok else 'still differ'}")
    if ok:
        print("A FIFTH DIVERGENCE WILL FAIL THIS CHECK. That is the point: the four")
        print("found so far were each discovered while fixing the previous one.")

    out = HERE / "records" / "L9"
    out.mkdir(parents=True, exist_ok=True)
    (out / "path_alignment.json").write_text(json.dumps({
        "seeds": list(SEEDS),
        "round_tripped": generated,
        "failed_to_generate": failed,
        "divergent_fields": {k: v for k, v in divergences.items()},
        "passes": ok,
        "mean_ceiling_natural": st.mean(ceilings_natural) if ceilings_natural else None,
        "mean_ceiling_override": st.mean(ceilings_override) if ceilings_override else None,
        "divergences_fixed": [
            "mix forcing (3 amplifiers: segment count, divergence selection, "
            "IRB-approval priority)",
            "roles (_designate_swap_pair re-derived instead of reading positions)",
            "rng stream (label permutation drawn on one path only)",
            "totality repair (sole-class rating re-draw gated off)",
        ],
        "caveats": [
            "this asserts the paths AGREE; it does not assert either is correct",
            "the derived-roles opt-out (positional_roles=False) is NOT covered — it "
            "deliberately produces a different instance and is used only for S5's "
            "negative cases",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'path_alignment.json'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
