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
# ★ NOT A CAPACITY ANY MORE (L14-b). The runtime enforces none, so property 1 must
# not price re-routing around one -- measuring the ceiling at 3 here scored the
# instance under a constraint the world does not have, and reported 5.52% where the
# draw reported 4.97% for the same seed. Two numbers for one quantity, from two
# modules that disagree about the world: the mismatch L14-b removed, surviving in
# the acceptance that is supposed to police it.
#
# The name is KEPT only where it still means a segment count -- fixture 2 forces
# `shared_class_segments = SEGMENTS_PER_WORKER`, which is about how many segments
# land in a class and has nothing to do with capacity.
SEGMENTS_PER_WORKER = 3

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
    share = sc.ceiling_vs_stale_card(inst)["ceiling_share"]  # no cap: the runtime has none
    return (share or 0.0) > 1e-9, f"ceiling_share={0.0 if share is None else share:.5f}"


def p2_RETIRED_na_below_cap(inst: dict[str, Any]) -> tuple[bool, str]:
    """RETIRED 2026-08-09 when the researcher ruled the segment allowance out entirely.

    It asserted `nA < cap`, encoding "the covered lie needs a free slot to misdirect
    into". WITH NO ALLOWANCE THERE IS ALWAYS A FREE SLOT, so the condition is
    unconditionally true and the check cannot fail.

    It would NOT have gone red after the change -- `CAP` is a constant in this module,
    not read from the environment -- so it would have kept passing and asserting
    nothing. That is the failure mode this project spent the day removing, and it is
    why the property is retired rather than left green.

    Kept as a named function so the retirement is visible to anyone counting six.
    """
    raise AssertionError("property 2 is retired; see the docstring")


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


def p4_allocation_is_non_trivial(inst: dict[str, Any]) -> tuple[bool, str]:
    """No single post-swap worker's IRB coverage spans every segment class.

    REPLACES "capacity binds exactly" (`len(segments) == len(roster) * cap`), retired
    with the allowance. That predicate would still have PASSED after the removal --
    9 == 3 x 3 is a fact about the instance shape, not about any enforced capacity --
    while no longer meaning what its name said. A true statement that has stopped
    being the statement you wanted is harder to catch than a false one.

    This does the job the old property did: it keeps the allocation non-trivial, so
    the manager cannot route everything to one worker and still reach the oracle. And
    unlike its predecessor it is falsifiable without a cap -- a roster where one
    worker covers every class present breaks it.
    """
    post = inst["event"]["roster_post_swap"]
    coverage = {w["worker_id"]: set(w["irb_coverage"]) for w in inst["workers"]}
    classes = {s["asset_class"] for s in inst["segments"]}
    spanning = [w for w in post if classes <= coverage[w]]
    return not spanning, (f"{len(classes)} segment classes; workers spanning all of "
                          f"them: {spanning or 'none'}")


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

    ("3 lied class has another post-swap holder", p3_lied_class_has_other_holder),
    ("4 allocation is non-trivial", p4_allocation_is_non_trivial),
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
            inst = gen.generate(candidate, **{**SHIPPED, "shared_class_segments": SEGMENTS_PER_WORKER})
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
    """Give one post-swap worker coverage of every class present. Applied to the
    OBJECT, because the generator will not build a roster like this -- the fixture
    has to reach the predicate, not be refused before it."""
    inst = gen.generate(seed, **SHIPPED)
    classes = sorted({s["asset_class"] for s in inst["segments"]})
    target = inst["event"]["roster_post_swap"][0]
    workers = [{**w, "irb_coverage": classes} if w["worker_id"] == target else w
               for w in inst["workers"]]
    ok, detail = p4_allocation_is_non_trivial({**inst, "workers": workers})
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
#: lowest, failing `3_stale_card_ceiling_above_zero`). Used only as a SEARCH HINT
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
    # ★ THE SEARCH SPACE CHANGED WITH L14-b, AND THE CONTROL SAID SO ITSELF.
    # It used to find a rejected seed inside `partial` -- 18 of 40 were rejected
    # when assertion 2b was live. With 2b retired, admission admits every `partial`
    # seed, and this fixture reported "DID NOT FIRE -- the check is vacuous" rather
    # than quietly passing. That is the control working.
    #
    # Admission still discriminates, just on a different axis: it rejects `current`
    # 12 of 12 on condition 3 (the stale-card ceiling is identically zero there).
    # So the negative case for "admitted" is now an ARRANGEMENT admission refuses,
    # not a seed -- and the fixture searches arrangements first, seeds second, and
    # NAMES which axis it fired on so a future reader is not misled about why.
    tried = []
    for lattice in (SHIPPED["lattice"], "current"):
        for candidate in (seed, *range(12)):
            try:
                result = adm.admit(candidate, **{**SHIPPED, "lattice": lattice})
            except (gen.InstanceAssertionError, ValueError):
                continue
            tried.append(f"{lattice}/{candidate}")
            if not result["admitted"]:
                failed = [k for k, v in result["conditions"].items() if v is not True]
                return True, (f"lattice={lattice!r} seed {candidate}: admitted=False "
                              f"failing={failed}")
    return False, (f"nothing rejected across {len(tried)} (arrangement, seed) pairs -- "
                   f"admission refuses nothing anywhere")


FIXTURES = (
    ("1 ceiling > 0", "`current` at nA=1", _fixture_p1),
    ("3 lied class has another holder", "`current` -- the relational one", _fixture_p3),
    ("4 allocation is non-trivial", "a worker covering every segment class", _fixture_p4),
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
    print(f"setting: {json.dumps(SHIPPED, sort_keys=True)}  cap=UNCAPPED (runtime enforces none)")
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
