"""S3 acceptance — finance instance generator.

Checks, in the order the acceptance text states them:

  1. `generate(seed)` twice IN TWO PROCESSES produces byte-identical instance JSON.
  2. A committed instance shows >=2 asset classes, >=4 workers, and every worker
     holding SA over all segments.
  3. S1 follow-through: the SA table matches published CRE20/21-equivalent values,
     transcribed from the FETCHED d424.pdf, asserted per value class with the
     column-identity traps as NEGATIVE controls — a check that only ever confirms
     the values it was written from proves nothing about selecting the right table.
  4. The IRB path is IMPORTED from the S1-validated module, asserted by identity
     rather than by inspection.

Also asserted, because the spec requires them by construction rather than by
later check: non-nestedness of the coverage lattice, and identifier opacity.

Run:  python3 -m experiments.worker_replacement.test_finance_generator
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import finance_generator as gen
from . import test_basel_reference as basel

HERE = Path(__file__).resolve().parent
INSTANCE_PATH = HERE / "records" / "S3" / "instance_seed101.json"

# Values a WRONG but plausible table selection would produce. Asserted absent, so
# the SA check cannot pass by having been written from whatever table was open.
WRONG_TABLE_TRAPS = {
    "Table 5 (MDB) mistaken for Table 10 (corporate)":
        ("corporate", "A+ to A-", 0.30),
    "Table 6 short-term ROW mistaken for the base row":
        ("bank", "BBB+ to BBB-", 0.20),
    "Table 7 (SCRA grades) mistaken for Table 6 (ECRA ratings)":
        ("bank", "AAA to AA-", 0.40),
    "corporate weights mistaken for sovereign":
        ("sovereign", "AAA to AA-", 0.20),
}


def main() -> int:
    failures: list[str] = []
    print("S3 — finance generator acceptance\n")

    # --- 1. cross-process byte identity ------------------------------------
    print("1. determinism — generate(101) in two separate processes:")
    code = (
        "from experiments.worker_replacement.finance_generator import generate, to_json;"
        "print(to_json(generate(101)), end='')"
    )
    # DIFFERENT PYTHONHASHSEED per process, deliberately: with the same seed both
    # processes share dict/set iteration order, so identity would prove only that
    # the code is not calling time or uuid. Varying it also covers ordering.
    import os
    runs = [
        subprocess.run(
            [sys.executable, "-c", code], cwd=HERE.parents[1],
            capture_output=True, text=True, check=True,
            env={**os.environ, "PYTHONHASHSEED": hashseed},
        ).stdout
        for hashseed in ("1", "99")
    ]
    identical = runs[0] == runs[1]
    print(f"   [{'ok' if identical else 'FAIL'}] byte-identical across processes "
          f"({len(runs[0])} bytes)")
    if not identical:
        failures.append("instance JSON is not byte-identical across processes")

    instance = json.loads(runs[0])
    INSTANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    INSTANCE_PATH.write_text(runs[0])
    print(f"   committed instance -> {INSTANCE_PATH.relative_to(HERE.parents[1])}")

    # --- 2. shape ----------------------------------------------------------
    print("\n2. instance shape:")
    classes = {s["asset_class"] for s in instance["segments"]}
    workers = instance["workers"]
    checks = [
        (f">=2 asset classes (got {len(classes)}: {sorted(classes)})", len(classes) >= 2),
        (f">=4 workers (got {len(workers)})", len(workers) >= 4),
        (f"8-10 segments (got {len(instance['segments'])})",
         8 <= len(instance["segments"]) <= 10),
    ]
    # SA universality. Stated precisely rather than by looping over workers without
    # using them (which an earlier version of this file did, and which proved
    # nothing): SA is universal BECAUSE its signature takes no worker at all, so it
    # cannot depend on coverage. Assert both halves — the signature, and that every
    # segment in the instance actually resolves.
    import inspect
    sa_params = list(inspect.signature(gen.sa_risk_weight).parameters)
    sa_worker_free = sa_params == ["asset_class", "rating"]
    sa_resolves = all(
        isinstance(gen.sa_risk_weight(s["asset_class"], s["rating"]), float)
        for s in instance["segments"]
    )
    checks.append(
        (f"SA takes no worker argument (signature {sa_params}) — universal by "
         "construction", sa_worker_free))
    checks.append(("every segment resolves under SA", sa_resolves))
    for label, ok in checks:
        print(f"   [{'ok' if ok else 'FAIL'}] {label}")
        if not ok:
            failures.append(label)

    # --- 2b. non-nestedness, by construction --------------------------------
    print("\n   coverage lattice (non-nested BY CONSTRUCTION — distinct equal-size sets):")
    covs = {w["worker_id"]: set(w["irb_coverage"]) for w in workers}
    for worker_id, cov in sorted(covs.items()):
        print(f"     {worker_id}  IRB{sorted(cov)}  + SA[all]")
    nested = [
        (a, b) for a in covs for b in covs
        if a != b and covs[a] < covs[b]
    ]
    print(f"   [{'ok' if not nested else 'FAIL'}] no worker's coverage contains another's"
          + (f" — nested: {nested}" if nested else ""))
    if nested:
        failures.append("coverage lattice is nested")

    # --- 2c. identifier opacity ---------------------------------------------
    print("\n   identifier opacity (ids must carry no method/coverage/class token):")
    tokens = list(gen.ASSET_CLASSES) + ["irb", "sa", "corp", "retail", "quant", "senior"]
    leaky = [
        w["worker_id"] for w in workers
        if any(t in w["worker_id"].lower() for t in tokens)
    ]
    print(f"   [{'ok' if not leaky else 'FAIL'}] {len(workers)} ids opaque"
          + (f" — leaky: {leaky}" if leaky else ""))
    if leaky:
        failures.append("worker ids leak domain tokens")
    # The production path is callable AND is demonstrably the one the generator
    # used — S5's negative case must drive THIS builder, so the claim has to be
    # checked, not printed. (An earlier version of this line asserted `... or True`,
    # which is not a check.)
    rebuilt = {gen.make_worker_id(101, i) for i in range(len(workers))}
    actual = {w["worker_id"] for w in workers}
    path_ok = rebuilt == actual
    print(f"   [{'ok' if path_ok else 'FAIL'}] make_worker_id() reproduces exactly the "
          f"instance's ids — it IS the production path")
    if not path_ok:
        failures.append(f"make_worker_id() does not reproduce instance ids: "
                        f"{sorted(rebuilt)} vs {sorted(actual)}")

    # --- 3. SA values, with wrong-table traps as negative controls -----------
    print("\n3. SA table vs the FETCHED d424.pdf (values transcribed per class):")
    published = {
        ("sovereign", "AAA to AA-"): 0.00, ("sovereign", "A+ to A-"): 0.20,
        ("sovereign", "BBB+ to BBB-"): 0.50, ("sovereign", "BB+ to B-"): 1.00,
        ("sovereign", "Below B-"): 1.50, ("sovereign", "Unrated"): 1.00,
        ("bank", "AAA to AA-"): 0.20, ("bank", "A+ to A-"): 0.30,
        ("bank", "BBB+ to BBB-"): 0.50, ("bank", "BB+ to B-"): 1.00,
        ("bank", "Below B-"): 1.50,
        ("corporate", "AAA to AA-"): 0.20, ("corporate", "A+ to A-"): 0.50,
        ("corporate", "BBB+ to BBB-"): 0.75, ("corporate", "BB+ to BB-"): 1.00,
        ("corporate", "Below BB-"): 1.50, ("corporate", "Unrated"): 1.00,
        ("retail", "Unrated"): 0.75,
    }
    bad = [
        f"{ac}/{rating}: ours {gen.sa_risk_weight(ac, rating)} != published {want}"
        for (ac, rating), want in sorted(published.items())
        if abs(gen.sa_risk_weight(ac, rating) - want) > 1e-12
    ]
    print(f"   [{'ok' if not bad else 'FAIL'}] {len(published)} published values match")
    failures.extend(bad)
    for b in bad:
        print(f"       {b}")

    print("\n   negative controls — wrong-table selections must NOT match:")
    for label, (ac, rating, wrong_value) in sorted(WRONG_TABLE_TRAPS.items()):
        ours = gen.sa_risk_weight(ac, rating)
        avoided = abs(ours - wrong_value) > 1e-12
        print(f"   [{'ok' if avoided else 'FAIL'}] {label}: ours {ours} vs trap "
              f"{wrong_value}")
        if not avoided:
            failures.append(f"SA table matches a wrong-table trap: {label}")

    # --- 4. IRB is imported, not re-implemented -----------------------------
    print("\n4. IRB provenance:")
    same = gen.capital_requirement is basel.capital_requirement
    print(f"   [{'ok' if same else 'FAIL'}] generator uses the S1-validated "
          f"capital_requirement by IDENTITY (not a copy)")
    if not same:
        failures.append("IRB function is not the S1-validated object")
    seg = next(s for s in instance["segments"] if s["asset_class"] != "retail")
    covered = next((w for w in workers if seg["asset_class"] in w["irb_coverage"]), None)
    uncovered = next((w for w in workers if seg["asset_class"] not in w["irb_coverage"]), None)
    if covered and uncovered:
        rw_cov = gen.irb_risk_weight_for(seg, covered)
        rw_unc = gen.irb_risk_weight_for(seg, uncovered)
        print(f"   covered worker   -> IRB RW {rw_cov:.4f}")
        print(f"   uncovered worker -> {rw_unc} (falls back to SA "
              f"{gen.sa_risk_weight(seg['asset_class'], seg['rating'])})")
        if rw_unc is not None:
            failures.append("uncovered worker was given an IRB number")

    print()
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  {f}")
        return 1
    print("RESULT: PASS — deterministic across processes; shape and lattice correct; "
          "SA matches published values and avoids every wrong-table trap; IRB imported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
