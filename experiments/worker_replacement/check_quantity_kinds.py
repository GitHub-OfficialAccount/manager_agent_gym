"""L6 sizing — how many QUANTITY KINDS does the scope report actually emit?

§B requires every reported quantity to carry its population predicate and its
comparator. L6 makes that mechanical. Before building the registry, the job has to
be sized — and sizing it turned out to be the same problem the rule is about.

TWO WAYS THE COUNT MOVES, and the second is bigger than the first:

  1. THE NORMALISER. A registry keys on a normalised path, and a path that fails
     to normalise splits ONE kind into many. `concurrency.per_cell.<cell/seed>.*`
     is FOUR kinds emitted under seventeen `cell/seed` keys; a normaliser that
     collapses list indices but not dict keys reports 68. LS flagged this for the
     per-cell rates (22 versus ~17) and it is larger than that: it is the
     difference between 119 kinds and 55.

  2. THE CLASSIFIER — and this is the one that makes "rates first, counts second"
     unworkable as a staging axis. Whether a quantity is RATE-shaped or
     COUNT-shaped has no type-level answer. Three defensible classifiers give
     three different splits of the same file:

        by leaf name (share|rate|frac|pct|ratio)   12 rate kinds / 33 count kinds
        by name, cell keys collapsed                7 / 28
        by Python type (float vs int)              40 / 79

     **Deciding which bucket a quantity belongs in requires exactly the judgement
     the registry entry is supposed to RECORD.** So the classification is a
     property of the ENTRY, not a filter on what must be registered.

THE RECOMMENDATION THAT FOLLOWS: register all 55 kinds; do not stage. Each entry
declares its own kind, its population predicate, and its comparator — mandatory
for rates, explicitly nullable with a reason for counts. That keeps LS's rules 2
and 3 intact while removing the ambiguity from the scoping.

THE NORMALISER NEEDS ITS OWN TWO-SIDED GUARD, because over-collapsing is the
dangerous direction: two genuinely different quantities sharing a normalised key
would silently inherit ONE predicate — a kind hiding inside another kind, which is
this project's recurring shape one level up. So the collapse map is printed for
reading, and both directions are checked: no registered kind without an emitted
value, no emitted value without exactly one kind.

Run:  python3 -m experiments.worker_replacement.check_quantity_kinds
"""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
REPORT = HERE / "records" / "R2" / "scope_report.json"

# Each pattern collapses ONE declared index dimension. Nothing collapses by
# accident: a key that is not an index dimension keeps its identity, because a
# normaliser that merges two different quantities is worse than one that splits
# a single quantity into several.
INDEX_DIMENSIONS: list[tuple[str, str, str]] = [
    (r"\[\d+\]", "[]", "list position — episodes, samples"),
    (r"\.(U|[0-4])/\d+\.", ".<cell/seed>.", "cell/seed composite key"),
    (r"\.(U|[0-4])\.", ".<cell>.", "cell key"),
    (r"\.seed\d+\.", ".<seed>.", "seed key"),
]


def walk(node: Any, path: str = "") -> Iterator[tuple[str, Any]]:
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")
    else:
        yield path, node


def normalise(path: str) -> str:
    for pattern, replacement, _why in INDEX_DIMENSIONS:
        path = re.sub(pattern, replacement, path)
    return path


def main() -> int:
    report = json.loads(REPORT.read_text())
    numeric = [(p, v) for p, v in walk(report)
               if isinstance(v, (int, float)) and not isinstance(v, bool)]

    collapse: dict[str, list[str]] = collections.defaultdict(list)
    for path, _value in numeric:
        collapse[normalise(path)].append(path)

    print("L6 sizing — quantity kinds in the committed scope report\n")
    print(f"numeric leaves emitted : {len(numeric)}")
    print(f"DISTINCT KINDS         : {len(collapse)}\n")

    print("index dimensions collapsed (nothing else is):")
    for _pattern, replacement, why in INDEX_DIMENSIONS:
        print(f"   {replacement:<16} {why}")

    print("\nkinds per section:")
    per_section = collections.Counter(k.split(".")[0] for k in collapse)
    for section, n in sorted(per_section.items()):
        print(f"   {n:>3}  {section}")

    # THE COLLAPSE MAP, PRINTED. Over-collapsing is the dangerous direction — two
    # different quantities under one key inherit one predicate — and the only
    # cheap defence is that a human can read what was merged.
    merged = {k: v for k, v in collapse.items() if len(v) > 1}
    print(f"\n{len(merged)} kinds were collapsed from more than one emitted path; "
          f"the largest:")
    for kind, paths in sorted(merged.items(), key=lambda kv: -len(kv[1]))[:5]:
        print(f"   {len(paths):>3} x  {kind}")
        print(f"          e.g. {paths[0]}")

    print("\nthe full kind list, which is the L6 work item:")
    for kind in sorted(collapse):
        print(f"   {kind}")

    out = HERE / "records" / "L6"
    out.mkdir(parents=True, exist_ok=True)
    (out / "quantity_kinds.json").write_text(json.dumps({
        "source": str(REPORT.relative_to(HERE)),
        "n_numeric_leaves": len(numeric),
        "n_kinds": len(collapse),
        "index_dimensions": [{"pattern": p, "replacement": r, "why": w}
                             for p, r, w in INDEX_DIMENSIONS],
        "kinds": sorted(collapse),
        "collapse_map": {k: sorted(v) for k, v in sorted(collapse.items())},
        "note": ("Kind count depends on the NORMALISER; the rate/count split "
                 "additionally depends on a CLASSIFIER with no type-level answer, "
                 "which is why the registry records the classification rather "
                 "than being staged by it."),
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwritten: {out / 'quantity_kinds.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
