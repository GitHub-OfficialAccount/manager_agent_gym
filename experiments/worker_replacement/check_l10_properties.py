"""L10 acceptance — the six properties, each shown FAILING before it is trusted to pass.

Written BEFORE the two instances exist, so the acceptance cannot be shaped by what
got built. Same discipline as `five_bucket_split.py`: a criterion chosen after seeing
the artefact is a choice about whether the artefact passes.

RR's condition, from the step: six passing assertions over a construction that
guarantees its own premises is the structurally-zero residual in a new costume. Six
assertions each DEMONSTRATED FAILING on a named fixture is a post-condition. So every
property here ships with the fixture that violates it, and `--controls` runs them.

Zero model calls. Generation only. Run:

    python -m experiments.worker_replacement.check_l10_properties            # the shipped cell
    python -m experiments.worker_replacement.check_l10_properties --controls # + the six fixtures
"""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

from . import finance_admission as adm
from . import finance_generator as gen
from . import finance_scorer as sc

# THE SETTLED BUILD SETTING. Written out in full and never defaulted, because
# `generate()`'s own defaults DISAGREE with it on three parameters -- irb_applicable_fraction
# 0.67 vs 0.89, amplify_divergence True vs False, amplify_irb_priority True vs False.
# A bare generate(seed) silently produces a DIFFERENT environment that still looks
# plausible, which is property 5's second half and the reason it is a parameter check
# rather than a table check alone.
SHIPPED: dict[str, Any] = {
    "lattice": "partial",
    "shared_class_segments": 1,
    "irb_applicable_fraction": 0.89,
    "amplify_count": True,
    "amplify_divergence": False,
    "amplify_irb_priority": False,
}
CAP = 3

# Digest of the Basel tables as committed. Property 5 detects PERTURBATION; it does not
# establish correctness against BCBS -- that is S1's job via `test_basel_reference`, and
# the instance carries `irb_provenance` naming it. Recorded here so a later edit to the
# tables cannot pass silently.
# DIGEST BY CONTAINER, NOT BY AN ENUMERATED LIST (RR). The first version listed
# SA_SOVEREIGN/BANK/CORPORATE/MDB by name and MISSED TWO SOURCES:
#
#   SA_RETAIL_FLAT   the SA treatment for one of the five asset classes -- a flat
#                    constant reached by a NAME TEST rather than a table lookup.
#                    54 segments across the 30-seed corpus. An edit to retail's
#                    weight passed the drift detector silently.
#   SA_TABLES        the registry. A class added with an SA table but no PD-floor
#                    entry moved nothing, so registration was invisible.
#
# Retail keeps falling through BECAUSE IT IS SHAPED DIFFERENTLY FROM ITS NEIGHBOURS
# -- the same difference that excluded it from clone registration. An enumerated
# list re-earns that bug every time the module grows; digesting SA_TABLES covers
# every present and future class in it, and SA_RETAIL_FLAT covers the one that is
# deliberately not in it.
_TABLE_SOURCES = ("SA_TABLES", "SA_RETAIL_FLAT", "PD_INPUT_FLOOR",
                  "PD_FLOOR_VERIFIED", "QRRE_REVOLVER_FLOOR")


def basel_digest() -> str:
    blob = json.dumps({n: _jsonable(getattr(gen, n)) for n in _TABLE_SOURCES},
                      sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def _jsonable(v: Any) -> Any:
    return sorted(v) if isinstance(v, (set, frozenset)) else v


def successor_unique_class(instance: dict[str, Any]) -> str | None:
    """The class the successor ALONE holds post-swap. Reproduced from
    `check_amplifier_dependence.successor_unique_class` deliberately rather than
    imported: that module runs sweeps on import-time constants, and an acceptance
    check that drags a sweep's configuration in with it is not checking this cell."""
    event = instance["event"]
    coverage = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
    successor = event["successor_id"]
    incumbents = [w for w in event["roster_post_swap"] if w != successor]
    unique = sorted(coverage[successor].difference(*(coverage[i] for i in incumbents)))
    return unique[0] if unique else None


def lied_classes(instance: dict[str, Any]) -> list[str]:
    """Classes the STALE CARD claims and the successor does not hold.

    The card describes the PREDECESSOR; after the swap it is read as though it
    described the successor. The lie is exactly predecessor_coverage - successor_coverage.
    """
    coverage = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
    ev = instance["event"]
    return sorted(coverage[ev["predecessor_id"]] - coverage[ev["successor_id"]])


def n_a(instance: dict[str, Any]) -> int:
    """IRB-approved segments in the successor-unique class."""
    unique = successor_unique_class(instance)
    return sum(1 for s in instance["segments"]
               if s["irb_approved"] and s["asset_class"] == unique)


# --------------------------------------------------------------------------- #
# The six properties. Each returns (passed, detail). None of them prints.
# --------------------------------------------------------------------------- #

def p1_ceiling_positive(inst: dict[str, Any]) -> tuple[bool, str]:
    share = sc.ceiling_vs_stale_card(inst, cap=CAP)["ceiling_share"]
    return (share or 0.0) > 1e-9, f"ceiling_share={0.0 if share is None else share:.5f}"


def p2_na_below_cap(inst: dict[str, Any]) -> tuple[bool, str]:
    v = n_a(inst)
    return v < CAP, f"nA={v} cap={CAP} unique_class={successor_unique_class(inst)!r}"


def p3_lied_class_has_other_holder(inst: dict[str, Any]) -> tuple[bool, str]:
    """THE RELATIONAL ONE, and the only property `current` fails while satisfying
    every neighbour. It needs the lied class AND who still holds it -- it cannot be
    read off a single field, which is why a checklist of atomic properties could not
    tell the two designs apart."""
    lied = lied_classes(inst)
    if len(lied) != 1:
        return False, f"expected exactly one lied class, got {lied!r}"
    cls = lied[0]
    ev = inst["event"]
    coverage = {w["worker_id"]: set(w["irb_coverage"]) for w in inst["workers"]}
    holders = [w for w in ev["roster_post_swap"]
               if w != ev["successor_id"] and cls in coverage[w]]
    return bool(holders), f"lied_class={cls!r} other_post_swap_holders={holders}"


def p4_capacity_binds(inst: dict[str, Any]) -> tuple[bool, str]:
    n_seg = len(inst["segments"])
    n_post = len(inst["event"]["roster_post_swap"])
    return n_seg == n_post * CAP, f"{n_seg} segments vs {n_post} workers x cap {CAP}"


def p5_basel_intact_and_switch_off(inst: dict[str, Any], pinned: str) -> tuple[bool, str]:
    digest = basel_digest()
    div = inst["parameters"]["amplify_divergence"]
    ok = digest == pinned and div is False
    return ok, f"digest={'MATCH' if digest == pinned else 'DIFFERS'} amplify_divergence={div}"


def p6_admitted(seed: int, **kwargs: Any) -> tuple[bool, str]:
    r = adm.admit(seed, **kwargs)
    return bool(r["admitted"]), f"admitted={r['admitted']}"


PROPERTIES = (
    ("1 ceiling > 0", p1_ceiling_positive),
    ("2 nA < cap", p2_na_below_cap),
    ("3 lied class has another post-swap holder", p3_lied_class_has_other_holder),
    ("4 capacity binds exactly", p4_capacity_binds),
    ("5 Basel tables intact AND divergence off", p5_basel_intact_and_switch_off),
    ("6 admitted", p6_admitted),
)


def check_instance(seed: int, pinned: str, **overrides: Any) -> tuple[bool, list[str]]:
    kwargs = {**SHIPPED, **overrides}
    inst = gen.generate(seed, **kwargs)
    lines, all_ok = [], True
    for name, fn in PROPERTIES:
        if name.startswith("5"):
            ok, detail = fn(inst, pinned)
        elif name.startswith("6"):
            ok, detail = fn(seed, **kwargs)
        else:
            ok, detail = fn(inst)
        all_ok &= ok
        lines.append(f"    [{'ok' if ok else 'FAIL'}] {name:44s} {detail}")
    return all_ok, lines


# --------------------------------------------------------------------------- #
# THE FIXTURES. Each must make its property FAIL. A property never shown failing
# is not a post-condition -- it is a restatement of the construction.
# --------------------------------------------------------------------------- #

def _fixture_p1(seed: int, pinned: str) -> tuple[bool, str]:
    """`current`, at a cell where its ceiling is structurally zero -- SEARCHED and NAMED.

    ★ THE PREMISE IS CELL-SPECIFIC AND AN EARLIER VERSION INHERITED IT FROM `SHIPPED`
    (RR). `current` lies about a class nobody else covers, so its channel is
    identically zero only BELOW cap: at shared_class_segments=1 the control fires,
    and at 2/3/4 `current` acquires a positive ceiling and the control stops firing
    (on some seeds it raises instead of reporting).

    That is the same defect closed in `_fixture_p6`: a fact verified AT THE SETTLED
    CELL, with the cell able to move underneath it -- and the cell IS moving, since
    the instance selection was drawn at the wrong one. It failed safe (a non-firing
    control reports NOT FIRED) but misleadingly: editing `shared_class_segments`
    would read as "the acceptance is broken" rather than "this control's premise was
    cell-specific".

    So the premise is re-established every run rather than assumed.
    """
    tried = []
    for segs in (SHIPPED["shared_class_segments"], 1, 2, 3):
        for candidate in (seed, *range(6)):
            try:
                inst = gen.generate(candidate, **{**SHIPPED, "lattice": "current",
                                                  "shared_class_segments": segs})
            except (gen.InstanceAssertionError, ValueError):
                continue
            ok, detail = p1_ceiling_positive(inst)
            tried.append(f"segs={segs} seed={candidate}")
            if not ok:
                return True, (f"`current` at segs={segs}, seed {candidate}: {detail} "
                              f"(premise re-established, not inherited)")
    return False, f"no `current` cell with a zero ceiling in {len(tried)} tried"


def _fixture_p2(seed: int, pinned: str) -> tuple[bool, str]:
    """Force shared_class_segments = cap.

    ★ THE SPEC'S FIXTURE IS SEED-DEPENDENT AND THIS IS WHERE THAT WAS FOUND. The step
    names "force shared_class_segments = cap" as the violation for property 2. It
    reaches nA=3 on seeds 0-11 -- but only nA=2 on SEED 26, which is one of the two
    candidate instances. Run on seed 26 alone the control PASSES VACUOUSLY: it looks
    like a demonstrated failure and demonstrates nothing.

    So the fixture searches rather than asserting on one seed, and NAMES the seed it
    fired on. A control whose firing depends on an argument nobody varied is the
    can't-fail check in its most convincing costume.
    """
    tried, skipped = [], []
    for candidate in (seed, *range(12)):
        try:
            inst = gen.generate(candidate, **{**SHIPPED, "shared_class_segments": CAP})
        except (gen.InstanceAssertionError, ValueError) as exc:
            # Generation refuses in TWO ways and an earlier version knew only one:
            # at segs=3 and irb_applicable_fraction=0.89 it raises a bare ValueError
            # ("only 7 of 9 segments have a non-zero SA fallback, but 8 IRB-approved
            # segments were requested"), which is not InstanceAssertionError. The
            # search crashed instead of skipping, and the crash printed to stderr
            # while the report printed to stdout -- so the run LOOKED truncated
            # rather than failed. Skips are counted and reported, never silent.
            skipped.append(f"{candidate}:{type(exc).__name__}")
            continue
        ok, detail = p2_na_below_cap(inst)
        tried.append(f"seed {candidate}: {detail}")
        if not ok:
            return True, f"fired on seed {candidate} -- {detail}"
    return False, (f"did not reach nA >= cap on any of {len(tried)} seeds "
                   f"(skipped {len(skipped)}: {','.join(skipped[:4])}); "
                   + " | ".join(tried[:3]))


def _fixture_p3(seed: int, pinned: str) -> tuple[bool, str]:
    """`current`: the lied class is the departed worker's SOLE class, so no other
    post-swap worker holds it. This is the fixture that matters -- `current` passes
    1, 2, 4, 5 and 6 and fails only this one."""
    inst = gen.generate(seed, **{**SHIPPED, "lattice": "current"})
    ok, detail = p3_lied_class_has_other_holder(inst)
    return (not ok), detail


def _fixture_p4(seed: int, pinned: str) -> tuple[bool, str]:
    """8 segments against 3 workers x cap 3 -- capacity no longer binds exactly.
    Applied to the OBJECT rather than through the generator, which asserts capacity
    binds and would refuse to build it: the fixture has to reach the predicate."""
    inst = gen.generate(seed, **SHIPPED)
    inst = {**inst, "segments": inst["segments"][:-1]}
    ok, detail = p4_capacity_binds(inst)
    return (not ok), detail


def _fixture_p5c(seed: int, pinned: str) -> tuple[bool, str]:
    """THE HOLE RR FOUND: perturb SA_RETAIL_FLAT, which the first digest missed.
    Retail is a flat constant reached by a name test rather than a table lookup, so
    an enumerated list of SA_* tables skips it while it still prices 54 segments."""
    inst = gen.generate(seed, **SHIPPED)
    original = gen.SA_RETAIL_FLAT
    try:
        gen.SA_RETAIL_FLAT = 9.99
        ok, detail = p5_basel_intact_and_switch_off(inst, pinned)
    finally:
        gen.SA_RETAIL_FLAT = original
    if basel_digest() != pinned:
        raise AssertionError("fixture leaked: SA_RETAIL_FLAT not restored")
    return (not ok), detail + " (constant restored)"


def _fixture_p5a(seed: int, pinned: str) -> tuple[bool, str]:
    """A perturbed SA table. Mutated and restored around the read so the module is
    left exactly as found -- a fixture that leaks state would make every later
    property in this run meaningless."""
    inst = gen.generate(seed, **SHIPPED)
    original = dict(gen.SA_SOVEREIGN)
    try:
        gen.SA_SOVEREIGN[next(iter(gen.SA_SOVEREIGN))] = 9.99
        ok, detail = p5_basel_intact_and_switch_off(inst, pinned)
    finally:
        gen.SA_SOVEREIGN.clear()
        gen.SA_SOVEREIGN.update(original)
    if basel_digest() != pinned:
        raise AssertionError("fixture leaked: SA_SOVEREIGN not restored")
    return (not ok), detail + " (table restored)"


def _fixture_p5b(seed: int, pinned: str) -> tuple[bool, str]:
    """The switch left ON -- the half that drifts, because it is a parameter and not
    a table, and because it is the generator's own DEFAULT."""
    inst = gen.generate(seed, **{**SHIPPED, "amplify_divergence": True})
    ok, detail = p5_basel_intact_and_switch_off(inst, pinned)
    return (not ok), detail


#: A seed measured as rejected at the shipped cell (18 of 40 are; seed 0 is the
#: lowest, failing `3_scripted_baseline_below_oracle`). Used only as a SEARCH HINT
#: now -- see `_fixture_p6`, which no longer trusts it.
REJECTED_SEED = 0


def _fixture_p6(seed: int, pinned: str) -> tuple[bool, str]:
    """A seed admission actually rejects -- SEARCHED, not pinned.

    ★ AN EARLIER VERSION PINNED `REJECTED_SEED` AND IGNORED ITS `seed` ARGUMENT
    ENTIRELY. RR caught it by applying the differ-test to their own sweep: running
    all eight controls across eight seeds, this row printed "fire" eight times from
    ONE observation, so the sweep said nothing about it. A control that cannot vary
    with the argument being varied is the day's fourth instance of that shape.

    Pinning was also fragile for a second reason: `REJECTED_SEED` was verified
    rejected AT THE SETTLED CELL, and the selection defect shows a cell can move
    underneath a recorded fact. Searching re-establishes it every run.
    """
    tried = []
    for candidate in (seed, REJECTED_SEED, *range(12)):
        try:
            result = adm.admit(candidate, **SHIPPED)
        except (gen.InstanceAssertionError, ValueError):
            continue
        tried.append(candidate)
        if not result["admitted"]:
            failed = [k for k, v in result["conditions"].items() if v is not True]
            return True, f"seed {candidate}: admitted=False failing={failed}"
    return False, f"no seed in {tried[:8]} was rejected -- admission never refuses here"


FIXTURES = (
    ("1 ceiling > 0", "`current` at nA=1", _fixture_p1),
    ("2 nA < cap", f"shared_class_segments = cap = {CAP} (searches seeds)", _fixture_p2),
    ("3 lied class has another holder", "`current` -- the relational one", _fixture_p3),
    ("4 capacity binds exactly", "8 segments vs 3 x 3", _fixture_p4),
    ("5a Basel tables intact", "perturbed SA_SOVEREIGN", _fixture_p5a),
    ("5b divergence off", "switch left ON (the generator default)", _fixture_p5b),
    ("5c retail not skipped", "perturbed SA_RETAIL_FLAT (RR's hole)", _fixture_p5c),
    ("6 admitted", "a seed admission rejects (searched)", _fixture_p6),
)


def main(argv: list[str]) -> int:
    # stdout unbuffered, so a traceback on stderr cannot appear ABOVE a report that
    # was written first. That interleaving made a CRASH read as a truncated run.
    sys.stdout.reconfigure(line_buffering=True)
    seeds = [int(a) for a in argv if a.isdigit()] or [26, 39]
    pinned = basel_digest()

    print("L10 ACCEPTANCE — six properties, asserted not hoped for")
    print(f"setting: {json.dumps(SHIPPED, sort_keys=True)}  cap={CAP}")
    print(f"Basel table digest pinned at run start: {pinned[:16]}...\n")

    ok_all = True
    for seed in seeds:
        try:
            ok, lines = check_instance(seed, pinned)
        except gen.InstanceAssertionError as exc:
            print(f"  seed {seed}: GENERATION REFUSED — {exc}")
            ok_all = False
            continue
        ok_all &= ok
        print(f"  seed {seed}: {'PASS' if ok else 'FAIL'}")
        print("\n".join(lines))

    if "--controls" in argv:
        print("\nCONTROLS — every property shown FAILING on its named fixture")
        print("(a property never shown failing is a restatement of the construction)")
        for name, fixture, fn in FIXTURES:
            try:
                fired, detail = fn(seeds[0], pinned)
            except (gen.InstanceAssertionError, ValueError) as exc:
                fired, detail = True, f"generation refused ({type(exc).__name__}): {str(exc)[:60]}"
            ok_all &= fired
            verdict = "fires" if fired else "** DID NOT FIRE -- the check is vacuous **"
            print(f"    [{'ok' if fired else 'FAIL'}] {name:34s} {fixture:38s} {verdict}")
            print(f"           {detail}")

    if basel_digest() != pinned:
        print("\n** the Basel tables were left MUTATED by this run **")
        ok_all = False

    print(f"\nRESULT: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
