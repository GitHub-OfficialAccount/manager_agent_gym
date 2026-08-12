"""S3 — finance environment instance generator.

Emits a complete instance from a seed alone: portfolio segments, a worker coverage
lattice, and the private parameters that constitute coverage. No hand-authored
instance data (HARNESS_SPEC_v2 E6); everything derives from `seed`.

DESIGN COMMITMENTS, each of which is a spec requirement rather than a taste:

* **Coverage is INFORMATION, never a withheld tool** (§2). Every worker can compute
  SA for every segment, because SA needs only the public external rating. IRB
  additionally needs the bank's own validated PD calibration for that asset class —
  which is exactly what IRB approval *is* — and that calibration is delivered as
  private prompt data to covered workers only. A worker without it cannot produce
  the IRB number and correctly falls back to SA. Nobody is ever switched off.
* **Non-nestedness BY CONSTRUCTION** (§2). Every worker's IRB coverage is a distinct
  subset of the SAME SIZE. Distinct equal-size sets are pairwise incomparable, so no
  worker's coverage can contain another's — it is not checked and hoped for, it is
  arithmetically impossible. S5 asserts it independently.
* **Interior spread BY CONSTRUCTION** (§5). The lattice template leaves exactly one
  class held only by the predecessor, so post-swap nobody covers it and its
  IRB-applicable segments cap below a perfect score. Without this the oracle is
  perfect and the instance measures nothing — see `_lattice_from_template`.
* **ROSTER-CORRECT scoring** (§4.1). Scores range over the ACTIVE roster, never the
  pool: the pool holds both predecessor and successor and is a team that can never
  exist, and scoring it inflates the oracle to perfection.
* **Identifier opacity, instance-wide** (§5). EVERY worker id is opaque and carries
  no method, coverage or asset-class token — not just the swap pair. Semantic
  incumbent ids would let a reader recover the lattice and attribute the remainder to
  the newcomer by elimination. Ids come from `make_worker_id()`, a callable path, so
  S5's negative case can drive the real builder rather than inline literals.
* **The dilution knob is a parameter** (§4.3). `irb_applicable_fraction` sets the
  share of segments requiring IRB. Segments servable by the universal fallback score
  identically under every allocation and contribute zero spread, so this is the knob
  that governs whether the instance can show an allocation effect at all.

IRB FUNCTIONS ARE IMPORTED, NEVER RE-IMPLEMENTED. They come from
`test_basel_reference`, the module validated in S1 against BCBS Basel II Annex 5
(19/19 published cases). A second hand-typed copy would silently void that
validation — which is how a validated module stops being the one in use.

SA RISK WEIGHTS are transcribed from a FETCHED PDF and cited per value class below.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from typing import Any

from .test_basel_reference import capital_requirement

# ---------------------------------------------------------------------------
# SA risk weights — BCBS "Basel III: Finalising post-crisis reforms", December
# 2017 (https://www.bis.org/bcbs/publ/d424.pdf), transcribed from the fetched PDF
# because the Basel Framework webpage does not render its tables.
#
# COLUMN-IDENTITY DISCIPLINE (the S1 Annex-5 lesson: the €50m and €5m columns were
# equally easy to select). These tables are MORE hazardous than Annex 5, not less,
# and the specific traps are recorded so a future editor cannot fall into them:
#
#   * Table 5 (MDB) has the same header shape as Table 10 (corporate) with
#     DIFFERENT values (20/30/50/100/150/50). Selecting it for corporates is silent.
#   * Table 6 (banks) carries TWO rows — "base" and "short-term exposures"
#     (20/20/20/50/150). Selecting the wrong ROW is silent.
#   * Table 7 is the same exposure class as Table 6 under a DIFFERENT APPROACH
#     (SCRA, grades A/B/C — 40/75/150). Selecting it is a methodology swap, not a
#     value error.
#   * BUCKET BOUNDARIES DIFFER BY ASSET CLASS: corporates use "BB+ to BB–" and
#     "Below BB–"; sovereigns and banks use "BB+ to B–" and "Below B–". The grade
#     strings are not interchangeable across tables.
# ---------------------------------------------------------------------------

# Table 1, paragraph 7 — sovereigns and central banks.
SA_SOVEREIGN = {
    "AAA to AA-": 0.00, "A+ to A-": 0.20, "BBB+ to BBB-": 0.50,
    "BB+ to B-": 1.00, "Below B-": 1.50, "Unrated": 1.00,
}
# Table 6 — banks, External Credit Risk Assessment Approach, "BASE" ROW ONLY.
SA_BANK = {
    "AAA to AA-": 0.20, "A+ to A-": 0.30, "BBB+ to BBB-": 0.50,
    "BB+ to B-": 1.00, "Below B-": 1.50, "Unrated": 1.00,
}
# Table 10, paragraph 39 — general corporate exposures.
SA_CORPORATE = {
    "AAA to AA-": 0.20, "A+ to A-": 0.50, "BBB+ to BBB-": 0.75,
    "BB+ to BB-": 1.00, "Below BB-": 1.50, "Unrated": 1.00,
}
# Paragraph 55 — "regulatory retail", rating-independent (flat), hence no grades.
SA_RETAIL_FLAT = 0.75

# Table 5 — multilateral development banks. Added for the five-class lattice
# template (§5). Same fetched document, and note it is the very table named as a
# column-identity TRAP for corporates: same header shape, different values. It is
# safe to use HERE because it is being used as itself.
SA_MDB = {
    "AAA to AA-": 0.20, "A+ to A-": 0.30, "BBB+ to BBB-": 0.50,
    "BB+ to B-": 1.00, "Below B-": 1.50, "Unrated": 0.50,
}

SA_TABLES: dict[str, dict[str, float]] = {
    "sovereign": SA_SOVEREIGN,
    "bank": SA_BANK,
    "corporate": SA_CORPORATE,
    "mdb": SA_MDB,
}
ASSET_CLASSES = ("sovereign", "bank", "corporate", "retail", "mdb")

# FIVE asset classes, not four, and the lattice is CONSTRUCTED rather than drawn
# (see `_lattice_from_template`). The history matters because the arithmetic is
# easy to get wrong twice:
#
#   * four classes seat four workers on distinct 2-subsets without nesting, which
#     is why the first version used them — but ANY four distinct 2-subsets of a
#     4-set must cover all four elements (only three such subsets can avoid a
#     given element), so every class was always covered, every IRB segment always
#     had a covered worker, and the oracle was ALWAYS PERFECT. The S6 gate rejected
#     40/40 instances on exactly this;
#   * at five classes a free draw satisfies the joint requirements only 57.1% of
#     the time (all 210 lattices enumerated), so construction beats
#     draw-and-reject and keeps generation total.
COVERAGE_SIZE = 2

# ---------------------------------------------------------------------------
# PD INPUT FLOORS — BCBS d424 (the same fetched PDF as the SA tables), cited per
# class, with the UNVERIFIED classes labelled rather than assumed:
#
#   corporate  0.05%  — paragraph 68: "The PD for each exposure that is used as
#                       input into the risk weight formula ... must not be less
#                       than 0.05%." Scoped by paragraph 66 to corporate and bank.
#   bank       0.05%  — paragraph 68, same scope.
#   retail     0.05%  — paragraph 121: "the greater of ... 0.1% for QRRE revolvers
#                       ... and 0.05% for all other exposures". Ours is regulatory
#                       retail, NOT a QRRE revolver, so 0.05% applies; the 0.1%
#                       figure is recorded so the distinction is not lost.
#   sovereign  0.05%  — NOT VERIFIED for this class. Paragraph 66 scopes 67-115 to
#   mdb        0.05%    corporate and bank exposures, and I did not find a
#                       sovereign/MDB-specific input floor in the fetched document.
#                       0.05% is applied as a CONSERVATIVE DEFAULT and labelled as
#                       such rather than cited.
PD_INPUT_FLOOR = {
    "corporate": 0.0005, "bank": 0.0005, "retail": 0.0005,
    "sovereign": 0.0005, "mdb": 0.0005,
}
PD_FLOOR_VERIFIED = {"corporate", "bank", "retail"}
QRRE_REVOLVER_FLOOR = 0.001  # d424 para 121, not used: our retail is not QRRE

# ---------------------------------------------------------------------------
# SYNTHETIC CLONE CLASSES (D3/D4) — FOR PRICING ONLY, AND THEY RAISE IF THEY
# REACH A STUDY PATH.
#
# WHY A CLONE. Pricing a COVERAGE_SIZE=3 partial-overlap lattice needs a sixth
# asset class: at five classes the cell is EMPTY, and structurally so — three
# 3-subsets of the four remaining classes cover every one of them at least twice,
# so the successor can never be the sole post-swap holder (check_lattice_
# enumeration.py). A clone gives the sixth class the economics of an existing one,
# so the price isolates the LATTICE instead of confounding it with new Basel
# weights.
#
# WHY IT MUST NOT SHIP. Nothing here is transcribed from d424, so no clone class
# may carry a BCBS citation, and a reported result containing one would be
# claiming a regulatory basis it does not have. `assert_no_synthetic_classes`
# enforces that at the study boundary rather than by convention.
#
# WHY TWO SOURCES ARE PRICED, NOT ONE. The clone inherits its source's SA/IRB
# divergence exactly, and that divergence varies by class (RR: corporate 0.2393 at
# the low end, mdb 0.3564 at the high, class mean 0.3075). Cloning corporate
# understates by ~20% and mdb overstates by ~14-16%. That cannot flip a 6-16x
# ranking, but picking one source silently would put an unreported error bar on
# every figure — so both are priced and the BRACKET is reported.
SYNTHETIC_CLASSES: dict[str, str] = {}


def register_synthetic_clone(name: str, source: str) -> str:
    """Register `name` as an exact economic clone of `source`. Returns `name`.

    Clones the SA table, the PD input floor and (through both) the rating pool.
    Idempotent, so a pricing module can register at import without ordering care.
    """
    if source not in SA_TABLES:
        raise ValueError(
            f"clone source {source!r} must be one of {sorted(SA_TABLES)}. "
            f"'retail' is excluded deliberately: its SA weight is a flat constant "
            f"reached by a NAME TEST in sa_risk_weight, not a table lookup, so a "
            f"clone of it would silently get a different SA treatment from its "
            f"source and stop being a clone"
        )
    if name in ASSET_CLASSES:
        raise ValueError(f"{name!r} is a real asset class, not a clone target")
    if name in SYNTHETIC_CLASSES and SYNTHETIC_CLASSES[name] != source:
        raise ValueError(
            f"{name!r} is already a clone of {SYNTHETIC_CLASSES[name]!r}; "
            f"re-registering it against {source!r} would change the economics of "
            f"figures already priced under that name"
        )
    SA_TABLES[name] = dict(SA_TABLES[source])
    PD_INPUT_FLOOR[name] = PD_INPUT_FLOOR[source]
    SYNTHETIC_CLASSES[name] = source
    return name


def assert_no_synthetic_classes(instance: dict[str, Any]) -> None:
    """Raise if a study instance contains a clone class. Call on every live path.

    A clone is defensible for a CEILING COMPARISON, where only the lattice varies
    and the economics are held constant on purpose. It is indefensible the moment
    the class appears in a reported result, because its risk weights are a copy of
    another class's and carry no BCBS basis.
    """
    present = {sg["asset_class"] for sg in instance["segments"]}
    present |= {c for w in instance["workers"] for c in w["irb_coverage"]}
    synthetic = sorted(present & set(SYNTHETIC_CLASSES))
    if synthetic:
        raise ValueError(
            f"synthetic clone class(es) {synthetic} reached a study path. These "
            f"carry COPIED risk weights with no BCBS transcription behind them and "
            f"are valid for offline ceiling PRICING only. To ship a sixth class, "
            f"transcribe its tables from d424 and register it as a real class"
        )

# A score difference at or below this is a TIE, and ties are never strict
# requirements. Bare `>` is correct only while equal scores are bit-identical
# (today they are: the same branch of the same function produces them). If s()
# ever acquires an ulp-divergent path, `>` would OVERCOUNT strict requirements —
# precisely the direction the strict form exists to prevent — so the comparison
# fails safe toward UNDERCOUNTING (RR review of S5).
TIE_EPS = 1e-12


def sa_risk_weight(asset_class: str, rating: str) -> float:
    """Public SA risk weight. Needs only the rating — hence the universal fallback."""
    if asset_class == "retail":
        return SA_RETAIL_FLAT
    table = SA_TABLES[asset_class]
    if rating not in table:
        raise KeyError(
            f"rating {rating!r} is not a bucket of the {asset_class} table; "
            f"bucket strings are NOT interchangeable across asset classes "
            f"(valid here: {sorted(table)})"
        )
    return table[rating]


def make_worker_id(seed: int, index: int) -> str:
    """Opaque worker id — the single production path, callable by S5's negative case.

    Carries no method, coverage or asset-class token. Derived from (seed, index) so
    it is stable across processes, and from a fixed alphabet so it can never
    accidentally spell a domain word.
    """
    rng = random.Random(f"worker-id::{seed}::{index}")
    return "w_" + "".join(rng.choice("0123456789abcdef") for _ in range(6))


@dataclass(frozen=True)
class Segment:
    segment_id: str
    asset_class: str
    rating: str
    ead: float
    # NO `pd`. Removed from the SCHEMA (R1), not merely left unread: the truth is
    # derivable only through the class calibration, so nothing downstream can
    # silently reintroduce a public default rate. (class, rating) is public; the
    # rating -> PD mapping is the private input the gap is built on.
    lgd: float
    maturity: float
    irb_approved: bool


@dataclass(frozen=True)
class Worker:
    worker_id: str
    irb_coverage: tuple[str, ...]
    # The registry CARD as the manager sees it in the all-channels cell. Held
    # separately from `irb_coverage` because the two DIVERGE by succession: the
    # predecessor's card stays on file after the swap, so a stale card describes
    # coverage its holder no longer has. The scripted baseline matches on THESE
    # strings, never on `irb_coverage` and never on the opaque worker id.
    card_capabilities: tuple[str, ...] = ()
    # The private parameter: rating -> PD calibration, per covered asset class. This
    # IS coverage. A worker without it cannot obtain the PD input the IRB formula
    # needs and must fall back to SA, which needs only the public rating.
    private_pd_calibration: dict[str, dict[str, float]] = field(default_factory=dict)


def _rating_pool(asset_class: str) -> tuple[str, ...]:
    if asset_class == "retail":
        return ("Unrated",)
    return tuple(SA_TABLES[asset_class])


def generate(
    seed: int,
    n_segments: int = 9,
    n_workers: int = 4,
    irb_applicable_fraction: float = 0.67,
    t_swap: int = 3,
    max_timesteps: int = 20,
    min_successor_routed: int = 1,
    shared_class_segments: int = 4,
    capacity_cap: int = 3,
    *,
    id_builder: Any = None,
    coverage_override: list[tuple[str, ...]] | None = None,
    force_irb_segment_ids: tuple[str, ...] = (),
    asset_classes: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Emit one complete instance. Deterministic in `seed` alone.

    `irb_applicable_fraction` is the dilution knob (§4.3): the share of segments
    requiring IRB. Segments servable by SA score identically under every allocation
    and contribute zero spread, so this parameter governs whether an allocation
    effect is expressible at all. S6 reports the spread as a function of it.

    `min_successor_routed` is O3's k: how many segments the ORACLE allocation must
    route through the successor for the arrival to carry allocation consequence.

    The three keyword-only arguments exist SOLELY to construct S5's negative cases
    — a generator whose assertions can never be made to fire has not been shown to
    assert anything. They are never used by study instances:
      * `id_builder` overrides the opaque id path (the semantic-id negative must
        drive a builder, not a hand-written id list that bypasses it);
      * `coverage_override` supplies a lattice directly (to build a NESTED one);
      * `force_irb_segment_ids` marks named segments IRB-approved regardless of
        eligibility (to build a zero-SA-fallback IRB segment).

    `asset_classes` widens the class set beyond the five real ones, for OFFLINE
    LATTICE PRICING at COVERAGE_SIZE=3 (D3). Any class in it that is not a real
    one must first be registered with `register_synthetic_clone`, and
    `assert_no_synthetic_classes` keeps the result off study paths.
    """
    if not 8 <= n_segments <= 10:
        raise ValueError("n_segments must be 8-10 (HARNESS_SPEC_v2 episode sizing)")

    classes = tuple(asset_classes) if asset_classes is not None else ASSET_CLASSES
    unknown = [c for c in classes
               if c not in ASSET_CLASSES and c not in SYNTHETIC_CLASSES]
    if unknown:
        raise ValueError(
            f"asset_classes names {unknown}, which are neither real classes nor "
            f"registered clones. Register a clone with register_synthetic_clone() "
            f"so its SA table and PD floor exist before anything is priced on it"
        )

    # The coverage_size the LATTICE actually uses, not the module constant. With a
    # coverage_override the constant describes a different lattice than the one
    # being built, and validating against it would be the wrong-source fault.
    coverage_size = (len(coverage_override[0]) if coverage_override
                     else COVERAGE_SIZE)
    max_workers = _n_choose_k(len(classes), coverage_size)
    if not 4 <= n_workers <= max_workers:
        raise ValueError(
            f"n_workers must be 4..{max_workers}: distinct {coverage_size}-subsets of "
            f"{len(classes)} asset classes are what make coverage non-nested by "
            "construction, and there are only that many"
        )
    if coverage_override is not None:
        named = {c for cover in coverage_override for c in cover}
        if not named <= set(classes):
            raise ValueError(
                f"coverage_override names classes {sorted(named - set(classes))} "
                f"that are not in asset_classes {list(classes)}. Substituting such "
                f"a lattice onto instances that have NO SEGMENTS in those classes "
                f"prices that coverage against nothing and reports it under the "
                f"template's name -- silently, since nothing else would raise (RR)"
            )
        if len({len(cover) for cover in coverage_override}) != 1:
            raise ValueError(
                "coverage_override sets must be EQUAL SIZE; unequal ones can nest, "
                "and non-nestedness is what makes the lattice measure anything"
            )

    rng = random.Random(f"finance-instance::{seed}")

    # --- coverage lattice: distinct equal-size subsets => pairwise incomparable ---
    if coverage_override is not None:
        chosen = [tuple(c) for c in coverage_override]
    else:
        chosen = _lattice_from_template(rng)

    # --- THE CLASS CALIBRATION (R1). One validated table per asset class ------
    #
    # The bank has ONE validated model per portfolio, not one per analyst. Drawing
    # it per worker made "truth = the holder's calibration" incoherent: two holders
    # of the same class held tables a factor of ~2 apart, so truth moved with the
    # assignee, E2 broke and the oracle became a max over workers of a quantity
    # whose target moved with the worker.
    #
    # Class-level makes truth SEGMENT-LEVEL and WORKER-INDEPENDENT, and it is what
    # creates the informational gap: (class, rating) is public, the MAPPING from
    # rating to PD is not. A covered worker holds the mapping; an uncovered one
    # cannot derive it from anything printed in the task.
    class_calibration: dict[str, dict[str, float]] = {
        asset_class: {
            rating: _draw_admissible_pd(rng, asset_class, rating)
            for rating in _rating_pool(asset_class)
        }
        for asset_class in classes
    }

    workers: list[Worker] = []
    for index, coverage in enumerate(chosen):
        # Holders of a class hold the CLASS table, identical across holders.
        calibration = {
            asset_class: dict(class_calibration[asset_class])
            for asset_class in coverage
        }
        workers.append(
            Worker(
                worker_id=(id_builder or make_worker_id)(seed, index),
                card_capabilities=tuple(
                    [f"IRB model approval: {c}" for c in sorted(coverage)]
                    + ["Standardised approach: all exposure classes"]
                ),
                irb_coverage=tuple(coverage),
                private_pd_calibration=calibration,
            )
        )

    # --- segments ------------------------------------------------------------
    n_irb = round(n_segments * irb_applicable_fraction)

    # SEGMENT-MIX BIAS (RR F2). The strictly-required set is exactly the SHARED
    # class's IRB-applicable segments, because post-swap the successor is that
    # class's only holder. Under an even round-robin over five classes that set is
    # ~1 segment, which caps the maximum measurable arrival effect at ~0.117 of the
    # oracle — BELOW the minimum detectable effect. A suite generated that way
    # would be sub-detectable BY DESIGN and would look entirely healthy.
    #
    # So the shared class is given `shared_class_segments` slots rather than its
    # round-robin share. This is a MIX change, not a lattice change: the template,
    # the non-nestedness and the sole-class guarantee are untouched.
    shared_class = _template_shared_class(chosen) if coverage_override is None else None
    class_sequence: list[str] = []
    if shared_class is not None:
        class_sequence += [shared_class] * min(shared_class_segments, n_segments)
    others = [c for c in classes if c != shared_class]
    index = 0
    while len(class_sequence) < n_segments:
        class_sequence.append(others[index % len(others)])
        index += 1

    drafts: list[dict[str, Any]] = []
    for index in range(n_segments):
        asset_class = class_sequence[index]
        base = {
            "segment_id": f"seg_{index:02d}",
            "asset_class": asset_class,
            "ead": round(rng.uniform(5_000_000, 250_000_000), 2),
            "lgd": round(rng.uniform(0.25, 0.60), 4),
            "maturity": round(rng.uniform(1.0, 5.0), 2),
        }
        # NOTE: NO "pd" FIELD. Deleted from the schema rather than merely unread
        # (assertion in the producer, not the product): the truth is now derivable
        # only through the class calibration, so nothing can silently read a public
        # default rate again.
        if asset_class == shared_class:
            # DIVERGENCE SELECTION on the shared class only (RR F2). The maximum
            # measurable arrival effect is the sum over strictly-required segments
            # of (1 - the fallback's score), so a shared-class segment where SA
            # happens to sit close to the IRB truth contributes almost nothing even
            # though it is counted. Raising the COUNT alone left the median effect
            # at 0.109 against an MDE of 0.13, so the rating is chosen from a
            # bounded seeded search to maximise the fallback penalty.
            #
            # Safe here and ONLY here: post-swap the successor covers this class, so
            # even a fully clipped fallback leaves the segment attainable and the A4
            # canary intact. On the SOLE class the same move would make the segment
            # worthless to the whole roster.
            #
            # This is a published knob: it shapes K3's divergence distribution and is
            # reported in `parameters` so it cannot manufacture the headline unseen.
            # PREFER THE ratio<1 TAIL (LS review round 2, F3). Maximising raw
            # penalty pushed the selection into ratio>2, where the fallback CLIPS
            # to zero — and the clip region is exactly where the execution term
            # cannot penalise fabrication (S4's clipping finding). The measurable
            # effect would then be concentrated on segments that are blind to the
            # failure mode S10 exists to detect.
            #
            # In the ratio<1 tail (SA UNDERSTATES the IRB truth) the penalty is
            # 1 - ratio, which approaches but never reaches 1, so the fallback
            # never clips and fabrication stays penalisable. It is also the
            # labelled-UNANCHORED direction, so there is no tension with the output
            # floor. Only if that tail yields nothing do we top up from ratio>1,
            # capped at the floor's implied bound.
            # CLIP-AVOIDANCE ONLY (R1). The penalty maximisation that used to
            # sit here is REMOVED: choosing each segment's rating to make the SA
            # fallback as wrong as possible is manufacturing, and it was measured
            # to buy 1.29x spread with 0 of 20 instances falling below the gate
            # floor without it. Smaller effect and sharper instrument.
            #
            # What REMAINS is a different mechanism and is kept deliberately: a
            # rating whose SA fallback CLIPS to zero makes the segment blind to
            # the failure mode the fabrication probe exists to detect, because a
            # faithful score already at the floor cannot be further penalised.
            # That protects a measurement rather than inflating one, and the two
            # must not be collapsed back together by a later reader.
            best = None
            for _ in range(48):
                rating = rng.choice(_rating_pool(asset_class))
                if sa_risk_weight(asset_class, rating) <= 0.0:
                    continue
                candidate = {**base, "rating": rating}
                if _fallback_ratio(candidate, class_calibration) < 1.0:
                    best = candidate      # never clips; take the first such
                    break
                if best is None:
                    best = candidate      # fall back to whatever we have
            drafts.append(best if best is not None else {
                **base, "rating": rng.choice(_rating_pool(asset_class))})
        else:
            rating = rng.choice(_rating_pool(asset_class))
            drafts.append({**base, "rating": rating})

    # IRB-approval is drawn ONLY from segments whose SA fallback is non-zero.
    # A zero-fallback IRB segment (sovereign rated AAA to AA-, SA risk weight 0%)
    # makes an uncovered worker operational-but-WORTHLESS on it: its fallback
    # scores 0, which is the deficiency shape wearing coverage's clothes, and it
    # sits in the score_report clip region where a fabricator cannot be penalised
    # at all. Excluded at SAMPLING time so such instances are never produced,
    # rather than produced and rejected downstream (S4 review, RR F1).
    eligible = [
        d for d in drafts
        if sa_risk_weight(d["asset_class"], d["rating"]) > 0.0
    ]
    if len(eligible) < n_irb:
        raise ValueError(
            f"only {len(eligible)} of {n_segments} segments have a non-zero SA "
            f"fallback, but {n_irb} IRB-approved segments were requested; raise "
            "n_segments or lower irb_applicable_fraction"
        )
    # Determine the sole-held class BEFORE choosing approvals, because sole-class
    # segments carry an extra constraint: post-swap nobody covers that class, so a
    # clipping fallback there is worthless to the WHOLE roster. Applied to every
    # sole-class approval, not only to the promoted one — an earlier version
    # guarded only the promotion and seed 21 still failed the A4 canary, because a
    # naturally-approved sole-class segment clipped.
    sole_class = None
    if coverage_override is None:
        post_coverage = {c for w in workers[1:] for c in w.irb_coverage}
        sole_held_classes = sorted(set(workers[0].irb_coverage) - post_coverage)
        sole_class = sole_held_classes[0] if sole_held_classes else None

    # TOTALITY REPAIR. The sole-held class must be able to supply at least one
    # IRB-applicable segment that is degraded-but-not-worthless. Whether it can
    # depends on the ratings drawn for that class, and at seed 41 the draw produced
    # none — generation is meant to be TOTAL under the constructed lattice, so the
    # fix is to re-draw that class's rating rather than to reject the seed.
    # Bounded and seeded, so determinism is preserved.
    if sole_class is not None and not any(
        d["asset_class"] == sole_class and _fallback_is_degraded_not_worthless(d, class_calibration)
        for d in eligible
    ):
        pool = [d for d in drafts if d["asset_class"] == sole_class]
        repaired = False
        for draft in pool:
            for _ in range(64):
                rating = rng.choice(_rating_pool(sole_class))
                if sa_risk_weight(sole_class, rating) <= 0.0:
                    continue
                candidate = {**draft, "rating": rating}
                if _fallback_is_degraded_not_worthless(candidate, class_calibration):
                    draft.update(candidate)
                    repaired = True
                    break
            if repaired:
                break
        if not repaired:
            raise InstanceAssertionError(
                f"could not draw any {sole_class!r} segment that is "
                "degraded-but-not-worthless under the SA fallback; the sole-held "
                "class cannot supply a spread source for this seed"
            )
        eligible = [
            d for d in drafts
            if sa_risk_weight(d["asset_class"], d["rating"]) > 0.0
        ]

    approvable = [
        d for d in eligible
        if d["asset_class"] != sole_class or _fallback_is_degraded_not_worthless(d, class_calibration)
    ]
    if len(approvable) < n_irb:
        raise ValueError(
            f"only {len(approvable)} segments can be IRB-approved without leaving "
            f"the post-swap roster worthless on them, but {n_irb} were requested"
        )
    # Shared-class segments are approved FIRST: they are the strictly-required set,
    # so leaving them SA-applicable would put the mix bias in place and still leave
    # the strict count at zero.
    approvable.sort(key=lambda d: (d["asset_class"] != shared_class, d["segment_id"]))
    approved = {d["segment_id"] for d in approvable[:n_irb]} | set(force_irb_segment_ids)

    # SAMPLING REQUIREMENT (§5): at least one IRB-applicable segment must lie in the
    # SOLE-HELD class — the class only the predecessor covers, which nobody covers
    # post-swap. That class is the entire source of interior spread: if none of its
    # segments needs IRB, every post-swap segment is attainable at full score, the
    # oracle is perfect again, and the constructed lattice buys nothing. Enforced by
    # promoting one eligible segment of that class rather than by rejecting the
    # instance, so generation stays total.
    if sole_class is not None:
        if True:
            already = any(
                d["segment_id"] in approved and d["asset_class"] == sole_class
                for d in drafts
            )
            if not already:
                # The promoted segment must be DEGRADED BUT NOT WORTHLESS under the
                # SA fallback. Post-swap nobody covers the sole-held class, so every
                # worker falls back to SA; if SA lands at or beyond twice the IRB
                # truth the relative error reaches 1 and the score CLIPS TO ZERO —
                # the segment is then worthless to the entire roster, which is
                # deficiency, not difference, and the A4 canary rejects it (it did,
                # on the first version of this promotion).
                #
                # A6 does not cover this: it excludes a zero SA RISK WEIGHT, whereas
                # this is a zero SCORE arising from SA being far from the IRB truth.
                # Different mechanism, same deficiency shape.
                candidates = [
                    d for d in approvable
                    if d["asset_class"] == sole_class
                    and d["segment_id"] not in approved
                    and _fallback_is_degraded_not_worthless(d, class_calibration)
                ]
                if not candidates:
                    raise InstanceAssertionError(
                        f"no eligible segment in the sole-held class {sole_class!r} "
                        "can be made IRB-applicable — the instance would have no "
                        "source of interior spread"
                    )
                approved.add(candidates[0]["segment_id"])
    segments = [
        Segment(**d, irb_approved=d["segment_id"] in approved) for d in drafts
    ]
    rng.shuffle(segments)

    # The replacement event. Two incumbents stay throughout, so the team is larger
    # than the swap and the manager always has a real choice (HARNESS_SPEC_v2 §5).
    worker_ids = [w.worker_id for w in workers]
    if coverage_override is None:
        # The TEMPLATE fixes the roles: worker 0 is the predecessor, worker 1 the
        # successor, and they share exactly class A. Designation is by construction
        # rather than by searching for a two-holder class -- the template creates
        # SEVERAL two-holder classes (A, B and C), so a lexicographic search would
        # pick the wrong pair and the sole-held class would not be the vacated one.
        predecessor_id, successor_id = worker_ids[0], worker_ids[1]
        swap_shared_class = sorted(
            set(workers[0].irb_coverage) & set(workers[1].irb_coverage)
        )[0]
    else:
        predecessor_id, successor_id, swap_shared_class = _designate_swap_pair(workers)
    instance = {
        "schema": "worker_replacement.finance_instance.v2",
        "seed": seed,
        "parameters": {
            "n_segments": n_segments,
            "n_workers": n_workers,
            "irb_applicable_fraction": irb_applicable_fraction,
            # The size of the lattice THIS instance has, not the module default.
            # Recording the constant would report COVERAGE_SIZE=2 on a size-3
            # instance -- a field naming a source that did not produce the value.
            "coverage_size": coverage_size,
            "asset_classes": list(classes),
            "synthetic_clone_classes": {
                c: SYNTHETIC_CLASSES[c] for c in classes if c in SYNTHETIC_CLASSES},
            "t_swap": t_swap,
            "max_timesteps": max_timesteps,
            "min_successor_routed": min_successor_routed,
            "shared_class_segments": shared_class_segments,
            "shared_class_divergence_selection": True,
            "capacity_cap": capacity_cap,
        },
        "event": {
            "t_swap": t_swap,
            "predecessor_id": predecessor_id,
            "successor_id": successor_id,
            "roster_pre_swap": [w for w in worker_ids if w != successor_id],
            "roster_post_swap": [w for w in worker_ids if w != predecessor_id],
            # Populated after the assertions run (needs the assembled instance).
            # K2's disclosure publishes the STRICT count: the tie-inclusive one
            # would overstate the successor's necessity by counting segments any
            # worker could have served.
            "successor_strictly_required_segments": [],
            # The asset class the swapped pair jointly and exclusively held, which
            # the successor uniquely holds post-swap. Published because
            # _designate_swap_pair takes the LEXICOGRAPHICALLY FIRST two-holder
            # class, so it is a function of the lattice and may be uniform across a
            # whole suite — a suite-level regularity a reader must be able to see.
            # S6 checks uniformity across the sweep.
            "swap_shared_class": swap_shared_class,
        },
        # THE CLASS CALIBRATION. Present in the instance because the SCORER needs
        # it to compute truth, and absent from every public surface because that
        # is the gap. The leak assertion checks the public strings, not this.
        "class_calibration": class_calibration,
        "segments": [asdict(s) for s in segments],
        "workers": [asdict(w) for w in workers],
        "sa_provenance": {
            "document": "BCBS, Basel III: Finalising post-crisis reforms, Dec 2017",
            "url": "https://www.bis.org/bcbs/publ/d424.pdf",
            "sovereign": "Table 1, para 7",
            "bank": "Table 6 (ECRA), BASE row — not the short-term row, not Table 7 (SCRA)",
            "corporate": "Table 10, para 39 — not Table 5 (MDB)",
            "retail": "para 55, regulatory retail, flat 75%",
        },
        "irb_provenance": {
            "module": "experiments.worker_replacement.test_basel_reference",
            "validated_by": "S1 — BCBS Basel II Annex 5, 19/19 published cases",
            "note": "imported, never re-implemented",
        },
    }
    _assert_instance_valid(instance)
    strict, _ = successor_routing_counts(instance)
    instance["event"]["successor_strictly_required_segments"] = strict
    return instance


# R1 item 5a. A SCORE-BEARING calibration must not sit on a value a fabricator
# can simply state.
MIN_CALIBRATION_SIGNIFICANT_DIGITS = 3


def _significant_digits(value: float) -> int:
    text = f"{value:.10f}".rstrip("0")
    return len(text.split(".")[1].lstrip("0")) if "." in text else 0


def _pd_is_admissible(value: float, asset_class: str) -> bool:
    """False for a value a fabricator can NAME rather than guess.

    Two exclusions, and the second is not a refinement of the first:

    * EXACTLY AT A PUBLISHED INPUT FLOOR. Under R1 the calibration is the answer
      key, so a fabricator naming the most guessable number in the domain lands
      ON the truth and the detector CLEARS it — an exact coincidence becomes an
      exact exoneration. Independently, a calibration pinned to a floor is what a
      bank reports when it has NO model, which is the opposite of what holding an
      approved calibration means, so excluding it improves realism too.
    * TWO OR FEWER SIGNIFICANT DIGITS. A round number is guessable for the same
      reason a floor is, without being any particular published value.
    """
    if abs(value - PD_INPUT_FLOOR[asset_class]) < 1e-12:
        return False
    return _significant_digits(value) >= MIN_CALIBRATION_SIGNIFICANT_DIGITS


def _draw_admissible_pd(rng: random.Random, asset_class: str, rating: str) -> float:
    """Draw a calibration entry that is neither floor-pinned nor round.

    Bounded resample, then a deterministic nudge onto the finest grid so the
    function cannot fail to terminate. The nudge moves UP, away from the floor.
    """
    for _ in range(64):
        value = round(pd_with_floor(asset_class, _pd_for(rng, rating)), 6)
        if _pd_is_admissible(value, asset_class):
            return value
    value = round(PD_INPUT_FLOOR[asset_class] + 137e-6, 6)
    while not _pd_is_admissible(value, asset_class):
        value = round(value + 1e-6, 6)
    return value


def pd_for(segment: dict[str, Any], calibration: dict[str, dict[str, float]]) -> float:
    """The PD for this segment: the class table's entry for its rating.

    (class, rating) is public; this MAPPING is not. That is the whole information
    gap — an uncovered worker knows the rating and cannot get the PD.
    """
    return calibration[segment["asset_class"]][segment["rating"]]


def irb_risk_weight_for(segment: dict[str, Any], worker: dict[str, Any]) -> float | None:
    """IRB risk weight if this worker holds the calibration, else None (=> SA).

    Uses the S1-validated `capital_requirement`. Returns None rather than a number
    when uncovered: the caller falls back to SA, which is the modelled behaviour.
    """
    if segment["asset_class"] not in worker["irb_coverage"]:
        return None
    # The worker's own table. Identical to the class table by construction, and
    # asserted so at generation — so this is worker-INDEPENDENT in value while
    # remaining worker-GATED in access.
    calibration = worker["private_pd_calibration"]
    return 12.5 * capital_requirement(
        calibration[segment["asset_class"]][segment["rating"]],
        segment["lgd"], segment["maturity"],
    )


def to_json(instance: dict[str, Any]) -> str:
    """Canonical serialisation — sorted keys, fixed separators, no timestamps."""
    return json.dumps(instance, sort_keys=True, indent=2) + "\n"


# --- small deterministic helpers (no itertools import-order surprises) ---------
def _combinations(items: tuple[str, ...], k: int) -> list[tuple[str, ...]]:
    if k == 0:
        return [()]
    out: list[tuple[str, ...]] = []
    for i, item in enumerate(items):
        for rest in _combinations(items[i + 1 :], k - 1):
            out.append((item,) + rest)
    return out


def _n_choose_k(n: int, k: int) -> int:
    return len(_combinations(tuple(str(i) for i in range(n)), k))


def _pd_for(rng: random.Random, rating: str) -> float:
    """PD drawn from a band consistent with the rating. Bands are OUR construction."""
    bands = {
        "AAA to AA-": (0.0001, 0.0008), "A+ to A-": (0.0008, 0.0030),
        "BBB+ to BBB-": (0.0030, 0.0120), "BB+ to BB-": (0.0120, 0.0500),
        "BB+ to B-": (0.0120, 0.0700), "Below BB-": (0.0700, 0.2000),
        "Below B-": (0.0900, 0.2000), "Unrated": (0.0100, 0.0600),
    }
    low, high = bands[rating]
    return rng.uniform(low, high)


def pd_with_floor(asset_class: str, pd: float) -> float:
    """Apply the class's PD input floor. Never returns a PD below the floor."""
    return max(pd, PD_INPUT_FLOOR[asset_class])


# ---------------------------------------------------------------------------
# S5 — generation-time assertions. Run UNCONDITIONALLY inside generate(), not as
# an optional validator someone can forget to call. Each raises with a DISTINCT
# message: a single catch-all would let one working assertion masquerade as six.
# ---------------------------------------------------------------------------


class InstanceAssertionError(ValueError):
    """An instance violated a generation-time invariant. Never caught internally."""


def _assert_instance_valid(instance: dict[str, Any]) -> None:
    _assert_non_nested(instance)
    _assert_capacity_binds(instance)
    _assert_no_zero_fallback_irb(instance)
    _assert_id_opacity(instance)
    _assert_both_rosters_serviceable(instance)
    # K2 REMOVED (R1). `_assert_oracle_routes_through_successor` enforced a
    # minimum successor-routed count, and the K2 curve MEASURED the channel-effect
    # ceiling to be FLAT across k=1,2,3,4 — the knob gated admission and moved
    # nothing. It cost instance rejections and a disclosure obligation for no
    # measured benefit. The function is retained below for the sweep's historical
    # curve; it is no longer an admission gate.
    _assert_sole_class_has_irb_segment(instance)
    _assert_pd_input_floors(instance)
    _assert_calibration_is_class_level(instance)
    _assert_calibration_not_guessable(instance)


def _assert_non_nested(instance: dict[str, Any]) -> None:
    """1 — no worker's IRB coverage contains another's.

    True by construction today (distinct equal-size subsets), but the construction
    lives in a module constant that a later edit could change. This converts a
    derived property into an asserted one.
    """
    coverage = {w["worker_id"]: set(w["irb_coverage"]) for w in instance["workers"]}
    for a, cov_a in sorted(coverage.items()):
        for b, cov_b in sorted(coverage.items()):
            if a != b and cov_a <= cov_b:
                raise InstanceAssertionError(
                    f"ASSERTION 1 (non-nestedness): coverage of {a} {sorted(cov_a)} is "
                    f"contained in {b} {sorted(cov_b)} — a nested lattice makes one "
                    "worker dominate (deficiency) AND collapses the oracle, so both "
                    "gates fail together"
                )


def _assert_capacity_binds(instance: dict[str, Any]) -> None:
    """2 — INVERTED by the S7 ruling. Capacity must BIND, and must be FEASIBLE.

    The old form required capacity to be non-binding so the oracle stayed a
    per-unit maximum. That premise bought a task with no allocation difficulty:
    with no contention, greedy per-segment card matching is optimal by definition
    and attained the oracle exactly on 20/20 instances. Capacity is now what makes
    this an allocation problem at all.

    (a) FEASIBLE: total active capacity >= segments, or segments go unstaffed for
        reasons unrelated to management.
    (b) BINDING: the per-worker cap is strictly BELOW the instance's own measured
        greedy card-match load — measured, not assumed, because a cap above that
        load leaves the greedy match feasible and the lookup collapse returns.
    """
    from .finance_scorer import greedy_card_match_load

    cap = instance["parameters"]["capacity_cap"]
    roster = len(instance["event"]["roster_post_swap"])
    demand = len(instance["segments"])
    if roster * cap < demand:
        raise InstanceAssertionError(
            f"ASSERTION 2a (capacity feasible): {roster} workers x cap {cap} = "
            f"{roster * cap} < {demand} segments — segments would go unstaffed for "
            "reasons unrelated to allocation quality"
        )
    load = greedy_card_match_load(instance)
    if cap >= load:
        raise InstanceAssertionError(
            f"ASSERTION 2b (capacity binds): cap {cap} is not below the greedy "
            f"card-match load {load} — the greedy match stays feasible, so a "
            "public-information script attains the oracle and the task is a lookup"
        )


def _assert_no_zero_fallback_irb(instance: dict[str, Any]) -> None:
    """6 — no IRB-applicable segment whose SA fallback risk weight is zero.

    Such a segment makes an uncovered worker operational-but-WORTHLESS on it (its
    fallback scores 0), which is the deficiency shape, and it sits in the clip
    region where a fabricator cannot be penalised at all (§4.1).
    """
    for segment in instance["segments"]:
        if not segment["irb_approved"]:
            continue
        fallback = sa_risk_weight(segment["asset_class"], segment["rating"])
        if fallback == 0.0:
            raise InstanceAssertionError(
                f"ASSERTION 6 (no zero-fallback IRB): segment "
                f"{segment['segment_id']} ({segment['asset_class']}, "
                f"{segment['rating']}) is IRB-approved but its SA fallback risk "
                "weight is 0% — an uncovered worker would be operational but "
                "worthless on it, which is deficiency, not difference"
            )


def _assert_id_opacity(instance: dict[str, Any]) -> None:
    """5 — no worker id carries a token from the instance's OWN lattice or methods.

    Instance-wide, not swap-pair-only: semantic INCUMBENT ids would let a reader
    recover the coverage lattice and attribute the uncovered remainder to the
    opaque newcomer by elimination (S2 review F4).
    """
    tokens = set(instance["parameters"]["asset_classes"]) | {
        "irb", "sa", "basel", "rwa", "quant", "senior", "junior", "new", "old",
    }
    for worker in instance["workers"]:
        lowered = worker["worker_id"].lower()
        hit = sorted(t for t in tokens if t in lowered)
        if hit:
            raise InstanceAssertionError(
                f"ASSERTION 5 (identifier opacity): worker id "
                f"{worker['worker_id']!r} contains {hit} — semantic ids let a reader "
                "recover the lattice and identify the newcomer by elimination"
            )


def _assert_both_rosters_serviceable(instance: dict[str, Any]) -> None:
    """4 — in BOTH rosters, every segment is serviceable at score > 0 by someone.

    HONESTLY: this cannot fire while assertion 6 holds. Under the universal SA
    fallback every roster can serve every segment, and A6 forecloses the only route
    to a zero-scoring one (an IRB-approved segment whose SA fallback risk weight is
    0%). So this is NOT an independent achievability check — treating it as one
    would be restating SA's universality and calling it a guard.

    It is kept deliberately as a CANARY: if A6's sampling constraint ever regresses,
    or a future asset class introduces another zero-weight bucket, this fires on the
    consequence rather than leaving it to be found downstream in a spread that
    quietly contains a worthless segment. Checked on BOTH rosters because a
    replacement can remove the only worker that made a segment worth anything.
    """
    from .finance_scorer import s as score_for

    by_id = {w["worker_id"]: w for w in instance["workers"]}
    for label in ("roster_pre_swap", "roster_post_swap"):
        roster = [by_id[wid] for wid in instance["event"][label]]
        for segment in instance["segments"]:
            if max(score_for(segment, w, instance["class_calibration"])
                   for w in roster) <= 0.0:
                raise InstanceAssertionError(
                    f"ASSERTION 4 (both rosters serviceable): in {label}, every "
                    f"worker scores 0 on segment {segment['segment_id']} — the "
                    "segment is worthless to that entire roster"
                )


def _assert_oracle_routes_through_successor(instance: dict[str, Any]) -> None:
    """3 — O3, in its binding form.

    NOT "achievable only via the successor", which is vacuous under a universal
    fallback (every worker can act on every segment, so the condition can never
    fire). The binding form is that the ORACLE allocation must route at least k
    segments through the successor — i.e. successor coverage is strictly required
    to attain the oracle score. Uses S4's oracle_allocation over the post-swap
    roster; no re-derivation here.
    """
    strict, tie_inclusive = successor_routing_counts(instance)
    event = instance["event"]
    k = instance["parameters"]["min_successor_routed"]
    if len(strict) < k:
        raise InstanceAssertionError(
            f"ASSERTION 3 (O3 oracle-routing): only {len(strict)} segment(s) STRICTLY "
            f"require successor {event['successor_id']} (tie-inclusive would say "
            f"{len(tie_inclusive)}), need >= {k} — without a strict requirement the "
            "arrival carries no allocation consequence and the instance is inert"
        )


def successor_routing_counts(instance: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Segments the successor is required for: (STRICT, TIE-INCLUSIVE).

    STRICT means `s(seg, successor)` beats EVERY other post-swap worker outright.
    That is the honest measure of "the successor is required to attain the oracle".

    TIE-INCLUSIVE means the oracle ALLOCATION happens to name the successor, which
    includes segments where several workers score identically and a tie-break picked
    it. On SA-applicable segments every worker scores 1.0, so tie-inclusive counting
    credits the successor with segments any worker could have served — and an
    instance with ZERO strictly-required segments could pass on tie-break luck
    alone, which is the inert-arrival trap arriving through a side door.

    Both are returned so the gap between them stays visible: the assertion and the
    K2 disclosure use STRICT, and the acceptance prints both (LS review of S5).
    """
    from .finance_scorer import oracle_allocation, s as score_for

    cal = instance["class_calibration"]
    event = instance["event"]
    post_ids = set(event["roster_post_swap"])
    successor_id = event["successor_id"]
    post_workers = [w for w in instance["workers"] if w["worker_id"] in post_ids]
    successor = next(w for w in post_workers if w["worker_id"] == successor_id)
    others = [w for w in post_workers if w["worker_id"] != successor_id]

    strict = sorted(
        seg["segment_id"]
        for seg in instance["segments"]
        if all(
            score_for(seg, successor, cal) > score_for(seg, other, cal) + TIE_EPS
            for other in others
        )
    )
    allocation = oracle_allocation({**instance, "workers": post_workers})
    tie_inclusive = sorted(
        seg_id for seg_id, wid in allocation.items() if wid == successor_id
    )
    return strict, tie_inclusive


def _designate_swap_pair(workers: list[Worker]) -> tuple[str, str, str]:
    """Choose (predecessor, successor) so the arrival is LOAD-BEARING by construction.

    O3 requires the post-swap oracle to route segments through the successor. That
    does not happen by picking any two workers: with several workers covering the
    same asset class, ties on s(seg, w) go to whichever worker the tie-break prefers,
    and the successor may win nothing — the instance is then inert, which is exactly
    what assertion 3 caught on the first version of this function.

    So: find an asset class covered by exactly TWO workers and designate that pair.
    Post-swap the predecessor is gone, leaving the successor as the ONLY worker
    covering that class, so every segment of it routes through the successor in the
    oracle allocation. The arrival carries allocation consequence by construction
    rather than by luck, and assertion 3 then guards the construction.
    """
    by_class: dict[str, list[str]] = {}
    for worker in workers:
        for asset_class in worker.irb_coverage:
            by_class.setdefault(asset_class, []).append(worker.worker_id)
    for asset_class in sorted(by_class):
        holders = sorted(by_class[asset_class])
        if len(holders) == 2:
            # Deterministic: predecessor is the lexicographically first holder.
            return holders[0], holders[1], asset_class
    raise InstanceAssertionError(
        "no asset class is covered by exactly two workers, so no swap pair can make "
        "the successor uniquely required post-swap; the arrival would be inert"
    )


def _lattice_from_template(rng: random.Random) -> list[tuple[str, ...]]:
    """The CONSTRUCTED five-class lattice (HARNESS_SPEC_v2 §5), not a free draw.

    Roles over permuted class labels A..E:

        w0 (PREDECESSOR) = {A, E}
        w1 (SUCCESSOR)   = {A, B}
        w2               = {B, C}
        w3               = {C, D}

    Four properties hold SIMULTANEOUSLY, which is why this is constructed rather
    than drawn and rejected (free draws at five classes satisfy them only 57.1% of
    the time — 210 lattices enumerated by LS):

      * all four sets are distinct and equal-size -> NON-NESTED by construction;
      * class A has exactly two holders, the swap pair -> the successor is
        STRICTLY required post-swap, so O3 holds by construction;
      * class E is held ONLY by the predecessor -> post-swap NOBODY covers it, so
        its IRB-applicable segments cap below a perfect score and the spread is
        INTERIOR by construction. This is what the free-draw lattice could never
        deliver: with four classes it is combinatorially impossible, which is the
        second half of the oracle-perfection proof;
      * post-swap coverage is {A,B,C,D} and every segment remains serviceable via
        the universal SA fallback -> the A4 canary stays intact.

    Class labels are PERMUTED BY SEED across all 5! labelings, so the shared class
    varies between instances instead of being whichever label sorts first. That
    removes the suite-level swap-class uniformity risk at its root rather than
    reporting it as a scope limit.
    """
    labels = list(ASSET_CLASSES)
    rng.shuffle(labels)
    a, b, c, d, e = labels
    return [(a, e), (a, b), (b, c), (c, d)]


def _assert_sole_class_has_irb_segment(instance: dict[str, Any]) -> None:
    """7 — the sole-held class must carry at least one IRB-applicable segment.

    The sole-held class is the one only the predecessor covers, so post-swap nobody
    covers it. Its IRB-applicable segments are the ENTIRE source of interior spread:
    without one, every post-swap segment is attainable at full score, the oracle is
    perfect again, and the constructed lattice has bought nothing. The generator
    promotes a segment to satisfy this; the assertion guards the promotion.
    """
    from .finance_scorer import roster_workers

    pool_ids = {w["worker_id"] for w in instance["workers"]}
    post_ids = set(instance["event"]["roster_post_swap"])
    predecessor_only = pool_ids - post_ids
    if not predecessor_only:
        return
    by_id = {w["worker_id"]: w for w in instance["workers"]}
    predecessor = by_id[instance["event"]["predecessor_id"]]
    post_coverage = {c for w in roster_workers(instance) for c in w["irb_coverage"]}
    sole_held = set(predecessor["irb_coverage"]) - post_coverage
    if not sole_held:
        return
    has_irb = any(
        segment["irb_approved"] and segment["asset_class"] in sole_held
        for segment in instance["segments"]
    )
    if not has_irb:
        raise InstanceAssertionError(
            f"ASSERTION 7 (sole-class spread source): the sole-held class "
            f"{sorted(sole_held)} carries no IRB-applicable segment — post-swap "
            "every segment would be attainable at full score and the oracle would "
            "be perfect again"
        )


def _fallback_is_degraded_not_worthless(
    draft: dict[str, Any], calibration: dict[str, dict[str, float]]) -> bool:
    """True when the SA fallback scores strictly above zero against the IRB truth.

    The score is 1 - min(1, |sa - truth| / truth), so it clips to zero once SA
    reaches twice the truth (or falls to zero). Segments in the sole-held class
    must sit inside that band: degraded enough to create spread, not so degraded
    that the post-swap roster is worthless on them.
    """
    irb_rw = 12.5 * capital_requirement(
        calibration[draft["asset_class"]][draft["rating"]],
        draft["lgd"], draft["maturity"],
    )
    if irb_rw <= 0:
        return False
    sa_rw = sa_risk_weight(draft["asset_class"], draft["rating"])
    return abs(sa_rw - irb_rw) / irb_rw < 1.0


def _template_shared_class(lattice: list[tuple[str, ...]]) -> str | None:
    """The class the swap pair share — worker 0 and worker 1 of the template."""
    if len(lattice) < 2:
        return None
    shared = sorted(set(lattice[0]) & set(lattice[1]))
    return shared[0] if shared else None


def _fallback_penalty(draft: dict[str, Any], calibration: dict[str, dict[str, float]]) -> float:
    """1 - the SA fallback's score against the IRB truth. The per-segment ceiling
    on what the arrival can be worth on this segment."""
    irb_rw = 12.5 * capital_requirement(
        calibration[draft["asset_class"]][draft["rating"]],
        draft["lgd"], draft["maturity"],
    )
    if irb_rw <= 0:
        return 0.0
    sa_rw = sa_risk_weight(draft["asset_class"], draft["rating"])
    return min(1.0, abs(sa_rw - irb_rw) / irb_rw)


def _fallback_ratio(draft: dict[str, Any], calibration: dict[str, dict[str, float]]) -> float:
    """sa / truth for this draft. Below 1 means SA understates the IRB truth."""
    irb_rw = 12.5 * capital_requirement(
        calibration[draft["asset_class"]][draft["rating"]],
        draft["lgd"], draft["maturity"],
    )
    if irb_rw <= 0:
        return float("inf")
    return sa_risk_weight(draft["asset_class"], draft["rating"]) / irb_rw


def _assert_calibration_not_guessable(instance: dict[str, Any]) -> None:
    """10 — no calibration entry is floor-pinned or round (R1 item 5a).

    Asserted at generation rather than filtered downstream: the calibration is
    the answer key now, so an entry a fabricator can NAME is an entry on which
    fabrication is exonerated by construction.
    """
    for asset_class, table in instance["class_calibration"].items():
        for rating, value in table.items():
            if not _pd_is_admissible(value, asset_class):
                raise InstanceAssertionError(
                    f"ASSERTION 10 (calibration not guessable): "
                    f"{asset_class}/{rating} = {value} is either pinned at the "
                    f"published input floor {PD_INPUT_FLOOR[asset_class]} or "
                    f"carries fewer than {MIN_CALIBRATION_SIGNIFICANT_DIGITS} "
                    f"significant digits"
                )


def _assert_calibration_is_class_level(instance: dict[str, Any]) -> None:
    """9 — every holder of a class holds the IDENTICAL table (R1).

    This is the assertion that makes truth well-defined. When calibrations were
    drawn PER WORKER, two holders of `corporate` held tables a factor of ~2 apart
    (0.044476 vs 0.022533 on one rating), so "truth = the holder's calibration"
    made the answer key move with the assignee: E2 broke and the oracle became a
    max over workers of a quantity whose target moved with the worker.

    Asserted rather than trusted to the construction, because the construction is
    exactly what was wrong before and a future edit could reintroduce a per-worker
    draw without anything else noticing.
    """
    calibration = instance["class_calibration"]
    for worker in instance["workers"]:
        for asset_class, table in (worker["private_pd_calibration"] or {}).items():
            expected = calibration.get(asset_class)
            if table != expected:
                raise InstanceAssertionError(
                    f"ASSERTION 9 (class-level calibration): worker "
                    f"{worker['worker_id']} holds a {asset_class} table that "
                    f"differs from the class table — truth would move with the "
                    f"assignee"
                )
        for asset_class in worker["irb_coverage"]:
            if asset_class not in (worker["private_pd_calibration"] or {}):
                raise InstanceAssertionError(
                    f"ASSERTION 9 (class-level calibration): worker "
                    f"{worker['worker_id']} is approved for {asset_class} but "
                    f"holds no calibration for it"
                )


def _assert_pd_input_floors(instance: dict[str, Any]) -> None:
    """8 — every segment's PD respects its class's input floor (d424 paras 68/121).

    Upgrades K3's anchoring statement: divergence is bounded not only by the
    aggregate output floor but by the INPUT floor on PD, which caps how extreme
    the IRB truth can be at the low-PD end. Without it the generator could draw a
    PD of 0.01% and produce a divergence no real portfolio could exhibit.
    """
    for asset_class, table in instance["class_calibration"].items():
        floor = PD_INPUT_FLOOR[asset_class]
        for rating, value in table.items():
            if value < floor - 1e-12:
                raise InstanceAssertionError(
                    f"ASSERTION 8 (PD input floor): class calibration "
                    f"{asset_class}/{rating} has pd {value} below the class "
                    f"floor {floor}"
                )
