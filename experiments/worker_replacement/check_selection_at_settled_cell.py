"""Do the chosen instances still occupy the strata they were chosen for?

The three study seeds were drawn ONE PER RANK-TERCILE of the ceiling, at a cell that
is not the cell the study will ship. This asks whether that stratification survived
the move, and it exists because the answer is no.

Zero model calls. Generation only. Run:

    python -m experiments.worker_replacement.check_selection_at_settled_cell
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import finance_admission as adm
from . import finance_generator as gen
from . import finance_scorer as sc

RECORD = Path(__file__).resolve().parent / "records/R2/instance_selection_partial_segs1.json"

# The cell the study ships. `generate()`'s defaults are 0.67/True/True, so a selection
# made without passing these was made somewhere else.
SETTLED: dict[str, Any] = {
    "lattice": "partial",
    "shared_class_segments": 1,
    "irb_applicable_fraction": 0.89,
    "amplify_count": True,
    "amplify_divergence": False,
    "amplify_irb_priority": False,
}
CAP = 3
INTENDED = {26: "low", 39: "mid", 37: "high"}


def ceilings_at(setting: dict[str, Any], seeds: range = range(40)) -> dict[int, float]:
    out: dict[int, float] = {}
    for seed in seeds:
        try:
            if not adm.admit(seed, **setting)["admitted"]:
                continue
            inst = gen.generate(seed, **setting)
            out[seed] = sc.ceiling_vs_stale_card(inst, cap=CAP)["ceiling_share"] or 0.0
        except (gen.InstanceAssertionError, ValueError):
            # Generation refuses in two ways; both are legitimate exclusions here and
            # neither is silent -- the admitted count is printed and compared.
            continue
    return out


def tercile(seed: int, ceilings: dict[int, float]) -> str:
    order = sorted(ceilings, key=lambda s: ceilings[s])
    rank, n = order.index(seed), len(order)
    return "low" if rank < n / 3 else ("mid" if rank < 2 * n / 3 else "high")


def main() -> int:
    record = json.loads(RECORD.read_text())
    now = ceilings_at(SETTLED)
    vals = sorted(now.values())

    print("DOES THE STRATIFIED DRAW SURVIVE THE MOVE TO THE SETTLED CELL?\n")
    print(f"  selection record   n_admitted={record['n_admitted']:>3}  "
          f"median {record['ceiling_band']['median']*100:.2f}%  "
          f"band {record['ceiling_band']['min']*100:.2f}-{record['ceiling_band']['max']*100:.2f}%")
    print(f"  settled cell       n_admitted={len(now):>3}  "
          f"median {vals[len(vals)//2]*100:.2f}%  "
          f"band {min(vals)*100:.2f}-{max(vals)*100:.2f}%")
    print("  -> different populations, so the draw was made somewhere the study does not ship\n")

    print("  seed  intended  @selection  @settled  tercile@settled")
    moved = []
    for seed, role in INTENDED.items():
        old = record["ceilings_by_seed"][str(seed)]
        got = tercile(seed, now)
        flag = "" if got == role else "  <-- MOVED"
        if got != role:
            moved.append(seed)
        print(f"  {seed:>4}  {role:>8}  {old*100:>9.2f}%  {now[seed]*100:>7.2f}%  {got.upper():>6}{flag}")

    achieved = [tercile(s, now) for s in INTENDED]
    print(f"\n  intended low/mid/high  ->  achieved {'/'.join(achieved)}")
    empty = sorted({"low", "mid", "high"} - set(achieved))
    if empty:
        print(f"  EMPTY STRATA: {empty}. The draw's whole purpose was one instance per "
              f"tercile,\n  and coverage of the range is what is lost -- not merely a "
              f"changed number.")
    return 1 if moved else 0


if __name__ == "__main__":
    raise SystemExit(main())
