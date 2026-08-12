"""L6 — §B made mechanical: every reported quantity carries its population and its
comparator, or it does not get written.

§B exists because six of this project's retractions share one shape: a number that
was arithmetically correct and described a different population from the one its
name implied. `__unstaffed__` labelled segments the manager HAD staffed. A
coverage rate conditioned on execution was read as a rate over all segments. A
pooled 9.5% described two populations. **In every case the arithmetic was right
and the predicate was unstated**, so nothing in the pipeline could disagree.

WHAT THIS MODULE DOES. Each quantity a report emits is a registered KIND carrying:
its class, the PREDICATE defining its population, and its comparator — mandatory
for rates, explicitly nullable with a reason otherwise. The emitter refuses to
write a report containing an unregistered quantity.

FIVE CLASSES, NOT TWO. Scoping this step began with a rates-first/counts-second
staging, which dissolved under measurement: whether a quantity is "rate-shaped"
has no type-level answer, and three defensible classifiers split the same file
three ways (12/33, 7/28, 40/79 kinds). Deciding the bucket requires exactly the
judgement the registry entry is supposed to RECORD. Worse, rate-versus-count was
never a partition of this file — it also contains IDENTIFIERs (`seed`), SETTINGs
(`concurrency`, `wall_clock_min`: instrument state, not measurement) and
PARAMETERs (`sigma_*_df`: degrees of freedom). So classification is a property of
the ENTRY, and identifiers are REGISTERED AS IDENTIFIERS rather than filtered out
of the walk — an exemption that is declared is auditable; a walker that silently
skips them is not. That distinction is the whole 413-versus-431 discrepancy
between two people counting the same file.

KEYS ARE DECLARED, NEVER DERIVED FROM THE OUTPUT PATH. Each entry states the path
patterns it covers. A derived normaliser is itself a place a kind can hide: two
different quantities collapsing to one normalised key would silently inherit ONE
population predicate — a kind hiding inside a kind. This project found that exact
failure while SCOPING this step (per-cell rates are one kind under six dict keys,
and the normaliser did not collapse them).

BOTH DIRECTIONS, ALWAYS. No emitted value without a registered kind, AND no
registered kind that nothing emits. A one-directional check rots quietly: rename a
quantity and the stale entry keeps the registry looking complete while coverage
drops without the count changing.

COVERAGE PRINTS IN THE CHECK'S OWN OUTPUT. `§B: PASS` can be mistaken for a
guarantee and would be just as dangerous at 100% coverage; `§B: PASS — 55/55
kinds registered, 0 unregistered values` cannot.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Literal

# SIX CLASSES. `measure` was added after RR showed the five-class set had nowhere
# to put a CONTINUOUS NON-RATE quantity, so `count` had drifted into meaning "has
# a comparator-or-reason and is not a rate" — and seven entries declared `count`
# while emitting continuous values (`achieved` 6.76, `regret` 1.78,
# `split_residual` -8.9e-16). **The one strict class was the one an author had an
# incentive to avoid.** That is a design asymmetry, not seven sloppy entries, and
# the repair is to remove the incentive: the comparator requirement is now
# CLASS-INDEPENDENT, so mis-declaring buys nothing, and value types are asserted
# per class, so mis-declaring is caught.
QuantityClass = Literal[
    "rate", "count", "measure", "identifier", "setting", "parameter"]

# Classes that carry a number, and therefore must declare a plausible range.
# `identifier` and `setting` are exempt because their values are labels and
# instrument state, not measurements.
NUMERIC_CLASSES: frozenset[str] = frozenset(
    {"rate", "count", "measure", "parameter"})

# Roles that may stand in for a comparator. A CLOSED SET, and the entry must name
# which one applies — "no comparator" as free text is how the requirement decays.
COMPARATOR_ABSENT_ROLES: frozenset[str] = frozenset({
    "denominator",      # it IS a denominator for something else
    "identifier",       # not a measurement
    "setting",          # instrument state
    "degrees_of_freedom",
    "residual",         # comparator is zero; non-zero is a defect
    "is_comparator",    # this quantity is what others are read against
    "prior",            # carried for comparison, not measured here
})


@dataclass(frozen=True)
class Quantity:
    """One registered quantity kind.

    `population` is a PREDICATE — the rule deciding what is in the set — never a
    name. "unstaffed segments" is a name and was wrong; "segments with no
    assignee in the final task board" is a predicate and would have been checkable.
    """

    key: str
    cls: QuantityClass
    population: str
    comparator: str | None = None
    comparator_absent_because: str | None = None
    absent_role: str | None = None
    paths: tuple[str, ...] = ()
    note: str = ""
    artifact: str = "scope_report"
    # A kind may DECLARE its unmeasurable form. `rerouted_share` returns None when
    # the denominator is empty, and before this that None was invisible to the
    # walk — the quantity escaped §B in **exactly the case where it is
    # unmeasurable**, which is the inverse of the rule that a zero and an
    # unmeasurable value must never render identically.
    may_be_none: bool = False
    none_means: str = ""
    # THE PLAUSIBLE RANGE (RR, superseding their own class-independence fix). The
    # population rule says what a quantity is OVER; this says what it may BE.
    #
    # ORIGIN: a units error — an RWA figure used as a score — produced losses of
    # ~1e9 and was caught ONLY because it was 1e8 times wrong. **The same
    # substitution at 2x would have survived, been quoted, and been
    # indistinguishable from a finding, and every check in the suite would have
    # passed, because the arithmetic was correct.** That is the §B shape exactly.
    #
    # It is also what makes `cls` HONEST rather than load-bearing: a class-based
    # type rule could not express "a score over nine segments" or "a residual that
    # must be zero", and it failed outright on the seven continuous-declared-count
    # entries. A per-entry range covers currency figures, degrees of freedom and
    # scores on the same footing, and needs no class-set change.
    plausible_range: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        if self.cls in NUMERIC_CLASSES and self.plausible_range is None:
            raise ValueError(
                f"{self.key}: a {self.cls} must declare its plausible range — "
                f"what the quantity may BE, not only what it is over")
        if self.plausible_range and self.plausible_range[0] > self.plausible_range[1]:
            raise ValueError(f"{self.key}: inverted range {self.plausible_range}")
        # CLASS-INDEPENDENT (RR-2). Every quantity states a comparator, or names a
        # role from the closed set that stands in for one. Previously only `rate`
        # was strict, so declaring `count` instead of `rate` bought an escape —
        # and seven entries took it. With the requirement identical across
        # classes, mis-declaring gains nothing, and the per-class VALUE TYPE check
        # in `check()` then catches it.
        if not self.comparator:
            if not self.comparator_absent_because:
                raise ValueError(
                    f"{self.key}: state a comparator or say why there is none")
            if self.absent_role not in COMPARATOR_ABSENT_ROLES:
                raise ValueError(
                    f"{self.key}: absent_role must be one of "
                    f"{sorted(COMPARATOR_ABSENT_ROLES)}, got {self.absent_role!r}"
                    f" — free-text 'no comparator' is how the requirement decays")
        if self.may_be_none and not self.none_means:
            raise ValueError(
                f"{self.key}: a kind that may be None must say what None MEANS, "
                f"or an unmeasurable value is indistinguishable from a zero")


def _q(key: str, cls: QuantityClass, population: str, *paths: str,
       comparator: str | None = None, absent: str | None = None,
       role: str | None = None, note: str = "", artifact: str = "scope_report",
       may_be_none: bool = False, none_means: str = "",
       rng: tuple[float, float] | None = None) -> Quantity:
    return Quantity(key=key, cls=cls, population=population, comparator=comparator,
                    comparator_absent_because=absent, absent_role=role,
                    paths=tuple(paths) or (key,), note=note, artifact=artifact,
                    may_be_none=may_be_none, none_means=none_means,
                    plausible_range=rng)


# What each class may VALUE. Enforced against the emitted report, which is what
# makes mis-declaring a class fail rather than merely being untidy.
def _value_ok(quantity: "Quantity", value: Any) -> bool:
    """Does this value fall inside what the entry says the quantity may BE?

    THE RANGE IS THE CHECK, not the class. A class-based type rule cannot express
    "a score over nine segments" or "a residual that must be zero", and it failed
    outright on the seven continuous-declared-`count` entries. The range covers
    currency figures, degrees of freedom and scores on the same footing — and it
    is what catches a UNITS substitution, which is arithmetically correct and
    therefore invisible to every other check in this suite.
    """
    if value is None:
        return True                       # gated separately by `may_be_none`
    if quantity.plausible_range is None:
        return True                       # identifier / setting: labels, not values
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    low, high = quantity.plausible_range
    return low <= float(value) <= high


# Path patterns are GLOBS over the emitted JSON path, declared per entry. `*`
# matches one path element; `[]` matches any list index. Nothing collapses that is
# not written here.
def _matches(pattern: str, path: str) -> bool:
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\[\]", r"\[\d+\]").replace(r"\*", r"[^.]+")
    return re.fullmatch(escaped, path) is not None


PER_EPISODE = "the 18 scope episodes, one row each (cell x seed)"
PER_CELL_SEED = "one row per (cell, seed) episode actually run"

REGISTRY: tuple[Quantity, ...] = (
    # --- run-level -------------------------------------------------------
    _q("n_episodes", "count", "episodes present in this report's bundle set",
       absent="a total, not a rate; the comparator is the intended suite size "
              "and is recorded in the run plan rather than here", role="denominator", rng=(0, 200)),

    # --- concurrency: INSTRUMENT SETTINGS, not measurements ---------------
    _q("concurrency.per_cell.concurrency", "setting",
       PER_CELL_SEED, "concurrency.per_cell.*.concurrency",
       absent="an instrument setting, reported per episode because it VARIED "
              "across this exploratory run; pinned for any powered study", role="setting", rng=(1, 16)),
    _q("concurrency.per_cell.wall_clock_min", "setting",
       PER_CELL_SEED, "concurrency.per_cell.*.wall_clock_min",
       absent="wall-clock is reported beside concurrency so a content effect "
              "would be visible; it is not itself a study quantity", role="setting", rng=(0.0, 600.0)),
    _q("concurrency.per_cell.completions", "count",
       "tasks reaching COMPLETED in that episode", "concurrency.per_cell.*.completions",
       comparator="n_tasks in the same episode", rng=(0, 40)),
    _q("concurrency.per_cell.n_tasks", "count",
       "tasks on the board at the end of that episode, including any the manager "
       "created mid-run", "concurrency.per_cell.*.n_tasks",
       absent="a denominator, not a measured quantity", role="denominator", rng=(0, 40)),

    # --- coverage misrouting ---------------------------------------------
    # THE FAMILY THAT PRODUCED TWO RETRACTIONS. Every rate here names which
    # segments it is over, because the first version of this measure conditioned
    # on execution and was read as a rate over all segments.
    _q("coverage_misrouting.executed.n", "count",
       "segments that EXECUTED and produced a parseable report",
       "coverage_misrouting.executed.n",
       absent="a denominator for the rate below", role="denominator", rng=(0, 200)),
    _q("coverage_misrouting.executed.misrouted", "count",
       "executed segments whose assignee did not cover the segment's class",
       "coverage_misrouting.executed.misrouted",
       comparator="coverage_misrouting.executed.n", rng=(0, 200)),
    _q("coverage_misrouting.executed.rate", "rate",
       "executed segments only — CONDITIONS ON SUCCESS and therefore cannot "
       "measure allocation failure",
       "coverage_misrouting.executed.rate",
       comparator="the capacitated optimum's own mismatch rate on the same "
                  "instances; without it this rate carries no sign",
       note="RETRACTION: 'mis-routing exactly zero' was drawn from this rate and "
            "withdrawn — it conditions on the allocation having worked.", rng=(0.0, 1.0)),
    _q("coverage_misrouting.assigned_total.n", "count",
       "segments with an assignee in the assignment record, executed or not",
       "coverage_misrouting.assigned_total.n",
       absent="a denominator", role="denominator", rng=(0, 200)),
    _q("coverage_misrouting.assigned_total.misrouted", "count",
       "assigned segments whose assignee did not cover the class",
       "coverage_misrouting.assigned_total.misrouted",
       comparator="coverage_misrouting.assigned_total.n", rng=(0, 200)),
    _q("coverage_misrouting.assigned_total.rate", "rate",
       "ALL assigned segments — the population that does not condition on success",
       "coverage_misrouting.assigned_total.rate",
       comparator="the capacitated optimum's mismatch rate on the same instances", rng=(0.0, 1.0)),
    _q("coverage_misrouting.unexecuted_capacity_refused.n", "count",
       "assigned segments never started because the assignee was at capacity",
       "coverage_misrouting.unexecuted_capacity_refused.n",
       absent="a denominator", role="denominator",
       note="RETRACTION: a pooled rate over this and the timing population "
            "described two populations and was withdrawn.", rng=(0, 200)),
    _q("coverage_misrouting.unexecuted_capacity_refused.misrouted", "count",
       "capacity-refused segments whose assignee did not cover the class",
       "coverage_misrouting.unexecuted_capacity_refused.misrouted",
       comparator="the n of the same population", rng=(0, 200)),
    _q("coverage_misrouting.unexecuted_capacity_refused.rate", "rate",
       "capacity-refused segments ONLY — never pooled with the timing population",
       "coverage_misrouting.unexecuted_capacity_refused.rate",
       comparator="the timing-cutoff rate below, reported separately", rng=(0.0, 1.0)),
    _q("coverage_misrouting.unexecuted_timing_cutoff.n", "count",
       "assigned segments never started because the horizon ended first",
       "coverage_misrouting.unexecuted_timing_cutoff.n", absent="a denominator", role="denominator", rng=(0, 200)),
    _q("coverage_misrouting.unexecuted_timing_cutoff.misrouted", "count",
       "timing-cutoff segments whose assignee did not cover the class",
       "coverage_misrouting.unexecuted_timing_cutoff.misrouted",
       comparator="the n of the same population", rng=(0, 200)),
    _q("coverage_misrouting.unexecuted_timing_cutoff.rate", "rate",
       "timing-cutoff segments ONLY",
       "coverage_misrouting.unexecuted_timing_cutoff.rate",
       comparator="the capacity-refused rate above, reported separately", rng=(0.0, 1.0)),
    _q("coverage_misrouting.capacitated_optimum_comparator."
       # DECLARED `rate` UNTIL THE RANGE RULE ASKED. It is mismatches PER
       # INSTANCE — a count divided by instances, which can exceed 1 and is not
       # bounded by [0,1] at all. Naming a range is what forced the question;
       # `cls` alone never would have, because nothing bound the class to the data.
       "avoidable_mismatches_per_instance", "measure",
       "instances on which the capacitated optimum was computed",
       "coverage_misrouting.capacitated_optimum_comparator."
       "avoidable_mismatches_per_instance",
       rng=(0.0, 9.0),
       comparator="the manager's own mismatches per instance — this quantity IS "
                  "the comparator the manager rates are read against"),
    _q("coverage_misrouting.capacitated_optimum_comparator.n_checked", "count",
       "instances on which the optimum was recomputed for this comparison",
       "coverage_misrouting.capacitated_optimum_comparator.n_checked",
       absent="a denominator", role="denominator", rng=(0, 200)),
    _q("coverage_misrouting.excluded_sole_held_class", "count",
       "segments excluded because the assignee held the only covering class, so "
       "'mis-routed' is undefined for them",
       "coverage_misrouting.excluded_sole_held_class",
       absent="an exclusion count; it exists so the excluded set is visible "
              "rather than silently absent from the denominators above", role="denominator", rng=(0, 200)),

    # --- declines ---------------------------------------------------------
    _q("declines.n_declined", "count",
       "segments whose worker returned the permitted decline form",
       "declines.n_declined", "episodes[].n_declined",
       comparator="segments assigned in the same population",
       note="a DECLINE is not an unreadable deliverable; both score 0 and they "
            "are different behaviours.", rng=(0, 200)),
    _q("declines.n_unreadable", "count",
       "segments whose deliverable could not be parsed AND was not a decline",
       "declines.n_unreadable", "episodes[].n_unreadable",
       comparator="segments assigned in the same population",
       note="RETRACTION: a mechanism and a 13.6% figure drawn from this count "
            "were withdrawn. Its population was the defect.", rng=(0, 200)),

    # --- per-episode rows -------------------------------------------------
    _q("episodes[].seed", "identifier", "n/a — an instance identifier",
       "episodes[].seed",
       absent="an identifier, not a measurement. Registered rather than filtered "
              "so the exemption is auditable: a walker that silently skips "
              "identifiers is the difference between two people counting the "
              "same file and getting 413 and 431.", role="identifier"),
    _q("episodes[].concurrency", "setting", PER_EPISODE, "episodes[].concurrency",
       absent="instrument setting; see concurrency.per_cell", role="setting", rng=(1, 16)),
    _q("episodes[].n_tasks", "count",
       "tasks on that episode's board at the end", "episodes[].n_tasks",
       absent="a denominator", role="denominator", rng=(0, 40)),
    _q("episodes[].completions", "count",
       "tasks reaching COMPLETED in that episode", "episodes[].completions",
       comparator="episodes[].n_tasks", rng=(0, 40)),
    _q("episodes[].n_parsed", "count",
       "segments whose deliverable yielded an rwa value", "episodes[].n_parsed",
       comparator="the 9 scored segments", rng=(0, 9)),
    _q("episodes[].n_unstaffed", "count",
       "segments with NO assignee in the assignment record — NOT segments that "
       "failed to execute", "episodes[].n_unstaffed",
       comparator="the 9 scored segments",
       note="RETRACTION: this was derived from COMPLETIONS, so assigned-but-"
            "unexecuted work collapsed into it and the label asserted the manager "
            "had never staffed work it had staffed. The defect that opened this "
            "phase; the predicate above is the repair.", rng=(0, 9)),
    _q("episodes[].achieved", "measure",
       "the episode's realised score over its 9 scored segments",
       "episodes[].achieved", comparator="episodes[].oracle", rng=(0.0, 9.0)),
    _q("episodes[].oracle", "measure",
       "the capacitated optimum for that episode's OWN roster",
       "episodes[].oracle",
       absent="it IS the comparator; cell U is scored against the pre-swap roster "
              "because scoring it against a team it never had would compare its "
              "regret to an unattainable optimum", role="is_comparator", rng=(0.0, 9.0)),
    _q("episodes[].regret", "measure", "oracle minus achieved for that episode",
       "episodes[].regret", comparator="episodes[].oracle", rng=(0.0, 9.0)),
    _q("episodes[].regret_share", "rate",
       "one episode; regret as a fraction of that episode's own oracle",
       "episodes[].regret_share", "per_cell_descriptive.*.values[]",
       comparator="episodes[].oracle, per episode — never a cross-episode oracle", rng=(0.0, 1.0)),
    _q("episodes[].staffed_regret_share", "rate",
       "segments that were STAFFED — excludes never-assigned work, so it is not "
       "comparable with regret_share",
       "episodes[].staffed_regret_share",
       comparator="episodes[].regret_share, from which it differs by the "
                  "unstaffed population", rng=(0.0, 1.0)),
    _q("episodes[].allocation_loss_staffed", "measure",
       "loss attributable to WHO the work went to, over staffed segments",
       "episodes[].allocation_loss_staffed",
       comparator="episodes[].execution_loss_signed", rng=(-9.0, 9.0)),
    _q("episodes[].execution_loss_signed", "measure",
       "loss attributable to what the assignee PRODUCED, signed",
       "episodes[].execution_loss_signed",
       comparator="episodes[].allocation_loss_staffed", rng=(-9.0, 9.0)),
    _q("episodes[].unstaffed_loss", "measure",
       "loss from segments with no assignee at all",
       "episodes[].unstaffed_loss", comparator="episodes[].regret", rng=(-9.0, 9.0)),
    _q("episodes[].split_residual", "measure",
       "regret minus the three loss terms — zero iff the decomposition is exact",
       "episodes[].split_residual",
       absent="a residual; its comparator is zero and any non-zero value is a "
              "defect rather than a measurement", role="residual", rng=(-1e-6, 1e-6)),

    # --- per-cell descriptives -------------------------------------------
    _q("per_cell_descriptive.mean_regret_share", "rate",
       "episodes in that cell — 2 to 3, which supports NO contrast verdict",
       "per_cell_descriptive.*.mean_regret_share",
       comparator="the same quantity in cell 0, with the NO-ORDERING rule "
                  "attached: cell ordering was confounded with completion rate "
                  "at r=0.93 and with a concurrency block", rng=(0.0, 1.0)),
    _q("per_cell_descriptive.n_episodes", "count",
       "episodes contributing to that cell's mean",
       "per_cell_descriptive.*.n_episodes",
       absent="a denominator, and the reason the mean above carries no verdict", role="denominator", rng=(0, 200)),

    # --- segment states ---------------------------------------------------
    _q("segment_state_counts.assigned_but_unexecuted", "count",
       "segments with an assignee that the engine never started",
       "segment_state_counts.assigned_but_unexecuted",
       comparator="the 9 scored segments per episode",
       note="expected near zero after L1; a non-zero value is a finding.", rng=(0, 200)),
    _q("segment_state_counts.executed_but_unparseable", "count",
       "segments that ran but whose deliverable yielded no value",
       "segment_state_counts.executed_but_unparseable",
       comparator="the 9 scored segments per episode", rng=(0, 200)),
    _q("segment_state_counts.executed_and_parsed", "count",
       "segments that ran and yielded a value, correct or not",
       "segment_state_counts.executed_and_parsed",
       comparator="the 9 scored segments per episode", rng=(0, 200)),

    # --- variance ---------------------------------------------------------
    # PARAMETERS, not rates. Classifying these as rate-shaped without saying so is
    # the entire 56-versus-46 disagreement between two people scoping this step.
    _q("variance_quantities.sigma_pooled_within_cell", "parameter",
       "within-cell deviations pooled across cells",
       "variance_quantities.sigma_pooled_within_cell",
       comparator="sigma_pooled_staffed_only",
       note="MEASURED PRE-L1. Must not size any suite: L1 is designed to destroy "
            "the distribution it was measured on.", rng=(0.0, 1.0)),
    _q("variance_quantities.sigma_pooled_df", "parameter",
       "degrees of freedom behind sigma_pooled_within_cell",
       "variance_quantities.sigma_pooled_df",
       absent="a df, carried so the interval on sigma can be computed; df=12 is "
              "roughly a 5.3x span on n", role="degrees_of_freedom", rng=(0, 500)),
    _q("variance_quantities.sigma_pooled_staffed_only", "parameter",
       "within-cell deviations of the STAFFED-only share",
       "variance_quantities.sigma_pooled_staffed_only",
       comparator="sigma_pooled_within_cell", rng=(0.0, 1.0)),
    _q("variance_quantities.sigma_pooled_staffed_df", "parameter",
       "degrees of freedom behind sigma_pooled_staffed_only",
       "variance_quantities.sigma_pooled_staffed_df", absent="a df", role="degrees_of_freedom", rng=(0, 500)),
    _q("variance_quantities.sigma_d_paired_vs_cell0", "parameter",
       "per-seed differences against cell 0, paired within instance",
       "variance_quantities.sigma_d_paired_vs_cell0",
       comparator="sigma_pooled_within_cell", rng=(0.0, 1.0)),
    _q("variance_quantities.sigma_d_df", "parameter",
       "degrees of freedom behind the paired sigma",
       "variance_quantities.sigma_d_df", absent="a df", role="degrees_of_freedom", rng=(0, 500)),
    _q("variance_quantities.sigma_between_instance", "parameter",
       "instance means, across instances",
       "variance_quantities.sigma_between_instance",
       comparator="sigma_pooled_within_cell", rng=(0.0, 1.0)),
    _q("variance_quantities.sigma_between_df", "parameter",
       "degrees of freedom behind the between-instance sigma",
       "variance_quantities.sigma_between_df", absent="a df", role="degrees_of_freedom", rng=(0, 500)),
    _q("variance_quantities.sigma_gap_full_minus_staffed", "parameter",
       "the difference between the full and staffed-only sigmas",
       "variance_quantities.sigma_gap_full_minus_staffed",
       comparator="zero",
       note="RETRACTION: '24% of the spread' was withdrawn — the gap reverses "
            "at df=6 and the components are anti-correlated at r=-0.42.", rng=(-1.0, 1.0)),
    # --- newly VISIBLE once the walk stopped dropping non-float leaves -----
    # These were emitted all along and exempt from §B because the walk could not
    # see them. Two of the three are not really quantities — which is the point:
    # **the walk surfaces, the REGISTRY adjudicates.** A walk that decided for
    # itself is how `seed` came to be silently skipped by one of us and not the
    # other.
    _q("episodes[].cell", "identifier",
       "n/a — the cell label, which happens to parse as a number",
       "episodes[].cell",
       absent="an identifier, not a measurement", role="identifier",
       note="15 of the 16 numeric-looking strings in this report are these."),
    _q("concurrency.concurrency_varies", "setting",
       "the episodes in this report, taken together",
       "concurrency.concurrency_varies",
       absent="a boolean fact about the instrument", role="setting",
       note="booleans were exempt from the walk entirely before RR-1."),
    _q("concurrency.concurrency_values_seen[]", "setting",
       "distinct concurrency values across the episodes in this report",
       "concurrency.concurrency_values_seen[]",
       absent="instrument state", role="setting",
       note="a genuine STRING-FORMATTED NUMBER, and the evasion RR-1 names — "
            "already present in the committed report."),

    _q("variance_quantities.design_side_prior_ceiling_sd", "parameter",
       "the design-side prior, not a measurement from this run",
       "variance_quantities.design_side_prior_ceiling_sd",
       absent="a prior carried for comparison against the measured sigmas", role="prior", rng=(0.0, 1.0)),
)


# --- the reroute artifact (L7's primary DV) -------------------------------
# REGISTERED BECAUSE RR-1 FOUND IT ESCAPING. `rerouted_share` returns None when
# the denominator is empty, and `None` was invisible to the walk — so the primary
# DV was exempt from §B in exactly the case where it is UNMEASURABLE. Both shares
# now DECLARE that form and say what it means.
REGISTRY += (
    _q("reroute.rerouted_share_conditioned", "rate",
       "eligible segment tasks with >=2 capacity-legal destinations at the move",
       "rerouted_share_conditioned", artifact="reroute",
       comparator="rerouted_share_unconditional, and at n=9 discretionary moves "
                  "neither supports a channel claim",
       may_be_none=True,
       none_means="the denominator was empty — no segment was ever assigned to a "
                  "present agent at a later decision, so the share is "
                  "UNMEASURABLE rather than zero", rng=(0.0, 1.0)),
    _q("reroute.rerouted_share_unconditional", "rate",
       "all eligible segment tasks, including moves with one legal destination",
       "rerouted_share_unconditional", artifact="reroute",
       comparator="rerouted_share_conditioned; the gap is moves that were not "
                  "choices",
       may_be_none=True,
       none_means="empty denominator — unmeasurable, not zero", rng=(0.0, 1.0)),
    _q("reroute.n_eligible", "count",
       "segment tasks assigned to an agent still on the roster at a later "
       "manager decision while not terminal", "n_eligible", artifact="reroute",
       absent="a denominator", role="denominator", rng=(0, 9)),
    _q("reroute.n_moved", "count",
       "eligible tasks with at least one discretionary move", "n_moved",
       artifact="reroute", comparator="n_eligible", rng=(0, 9)),
    _q("reroute.n_moved_with_real_choice", "count",
       "eligible tasks moved when >=2 destinations were capacity-legal",
       "n_moved_with_real_choice", artifact="reroute", comparator="n_moved", rng=(0, 9)),
    _q("reroute.n_discretionary_moves", "count",
       "MOVES, not tasks, where both agents were present",
       "n_discretionary_moves", artifact="reroute",
       comparator="n_moved — moves sum and tasks do not (33 vs 29 on the scope "
                  "corpus)", rng=(0, 100)),
    _q("reroute.n_forced_moves", "count",
       "moves whose source agent had left the roster — not choices",
       "n_forced_moves", artifact="reroute",
       comparator="n_discretionary_moves, never summed with it", rng=(0, 100)),
    _q("reroute.forced_destinations", "count",
       "forced moves, by destination", "forced_destinations.*",
       artifact="reroute",
       comparator="each other; and note BOTH failure mode #1 and capacity-optimal "
                  "play predict the successor, so the raw split discriminates "
                  "nothing", rng=(0, 100)),
    _q("reroute.n_requested_not_applied", "count",
       "assignments the manager requested that the engine skipped",
       "n_requested_not_applied", artifact="reroute",
       comparator="applied assignments in the same episode", rng=(0, 200)),
    _q("reroute.forced_to_successor_uncovered", "count",
       "forced moves to the successor, restricted to IRB segments outside its "
       "approval scope", "forced_to_successor_uncovered.n_uncovered",
       artifact="reroute",
       comparator="forced_to_successor_uncovered.n_forced_to_successor",
       may_be_none=True,
       none_means="UNCOMPUTABLE — the bundle carries no instance, so coverage "
                  "could not be resolved. A zero would read as 'the manager "
                  "never did this'.", rng=(0, 100)),
    _q("reroute.forced_to_successor_total", "count",
       "forced moves whose destination was the successor",
       "forced_to_successor_uncovered.n_forced_to_successor", artifact="reroute",
       absent="a denominator for the restricted count", role="denominator",
       may_be_none=True, none_means="UNCOMPUTABLE; see n_uncovered", rng=(0, 100)),
    _q("reroute.forced_to_successor_computable", "setting",
       "whether coverage could be resolved for this bundle",
       "forced_to_successor_uncovered.computable", artifact="reroute",
       absent="a computability flag, not a measurement", role="setting"),
)

BY_KEY: dict[str, Quantity] = {q.key: q for q in REGISTRY}


def walk(node: Any, path: str = "") -> Iterator[tuple[str, Any]]:
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")
    else:
        yield path, node


# A trailing `%` is a DISPLAY SUFFIX, not prose. Without it `{'r': '12.5%'}` — a
# rate emitted as a display percentage — stayed invisible to §B, which is the
# residual left after the first walk fix: strings that parse as a number were
# surfaced, and the commonest way to format a rate as a string was not.
_NUMERIC_STRING = re.compile(r"-?\d+(\.\d+)?([eE][-+]?\d+)?%?")


def is_quantity_value(value: Any) -> bool:
    """Is this leaf a QUANTITY the rule applies to? (RR-1)

    The first version took `int`/`float` and dropped `bool` — so a quantity
    formatted as a string, returned as `None`, or expressed as a boolean was
    EXEMPT rather than flagged. **§B cannot apply to what the walk cannot see**,
    and the exemption was widest exactly where it hurt most: `rerouted_share`
    returns `None` when its denominator is empty, so the primary DV escaped the
    mechanism precisely in the case where it is UNMEASURABLE — the inverse of the
    rule that unmeasurable and zero must never render identically.

    PROSE IS NOT A QUANTITY, so free-text strings stay out; a string that PARSES
    AS A NUMBER does not. That is a real evasion and one is already in the
    committed report (`concurrency_values_seen[0] = '2'`). Whether such a value is
    genuinely a quantity is then the REGISTRY's judgement, not the walk's — 15 of
    the 16 numeric-looking strings in that file are cell labels, and they are
    registered as identifiers rather than silently skipped.
    """
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return True
    return isinstance(value, str) and bool(_NUMERIC_STRING.fullmatch(value.strip()))


def numeric_leaves(report: dict[str, Any]) -> list[tuple[str, Any]]:
    """Every leaf §B applies to. Named for continuity; see `is_quantity_value`."""
    return [(p, v) for p, v in walk(report) if is_quantity_value(v)]


def resolve(path: str, artifact: str = "scope_report") -> Quantity | None:
    for quantity in REGISTRY:
        if quantity.artifact != artifact:
            continue
        if any(_matches(pattern, path) for pattern in quantity.paths):
            return quantity
    return None


def check(report: dict[str, Any],
          artifact: str = "scope_report") -> dict[str, Any]:
    """Both directions, with coverage in the result rather than in a document."""
    leaves = numeric_leaves(report)
    unregistered: list[str] = []
    wrong_type: list[dict[str, Any]] = []
    undeclared_none: list[str] = []
    in_artifact = [q for q in REGISTRY if q.artifact == artifact]
    matched: dict[str, int] = {q.key: 0 for q in in_artifact}
    for path, value in leaves:
        quantity = resolve(path, artifact)
        if quantity is None:
            unregistered.append(path)
            continue
        matched[quantity.key] += 1
        # VALUE TYPE PER CLASS. This is what makes mis-declaring a class fail
        # rather than merely read oddly: seven entries declared `count` while
        # emitting continuous values, and nothing could tell.
        if not _value_ok(quantity, value):
            wrong_type.append({"path": path, "value": value,
                               "declared": quantity.cls, "key": quantity.key,
                               "plausible_range": quantity.plausible_range})
        # AN UNDECLARED None IS THE UNMEASURABLE CASE ESCAPING. A kind that can
        # be None must say what None means.
        if value is None and not quantity.may_be_none:
            undeclared_none.append(path)

    # THE SECOND DIRECTION. A registry that only checks emitted-implies-registered
    # rots quietly: rename a quantity and the stale entry keeps the count looking
    # complete while coverage drops.
    never_emitted = sorted(k for k, n in matched.items() if n == 0)

    return {
        "ok": not (unregistered or never_emitted or wrong_type
                   or undeclared_none),
        "n_values": len(leaves),
        "wrong_class_for_value": wrong_type,
        "undeclared_none_values": sorted(set(undeclared_none)),
        "n_kinds_registered": len(in_artifact),
        "n_kinds_matched": sum(1 for n in matched.values() if n),
        "unregistered_values": sorted(set(unregistered)),
        "registered_kinds_never_emitted": never_emitted,
        "summary": (
            f"{sum(1 for n in matched.values() if n)}/{len(in_artifact)} registered "
            f"kinds emitted · {len(leaves) - len(unregistered)}/{len(leaves)} "
            f"values covered · {len(unregistered)} unregistered · "
            f"{len(never_emitted)} stale entries · "
            f"{len(wrong_type)} out-of-range values · "
            f"{len(undeclared_none)} undeclared None"
        ),
    }


def registered_artifacts() -> set[str]:
    """Every artifact the registry claims to cover."""
    return {q.artifact for q in REGISTRY}


def assert_artifact_coverage(checked: set[str]) -> dict[str, Any]:
    """The set of artifacts CHECKED must equal the set REGISTERED.

    THE HIDING PLACE THIS CLOSES, which I opened while closing two others.
    Artifact scoping was necessary — otherwise one report's entries read as stale
    against another's — but it made **registering under a new artifact a way to
    opt OUT of validation while appearing registered.** Measured at the time:
    `scope_report` had 55 entries and was checked by the acceptance; `reroute` had
    12, including `rerouted_share_conditioned` — THE PRIMARY DV — and was checked
    by nothing. Direction 2 cannot fire for an artifact nobody checks, so those
    entries could have been stale, misnamed or duplicated and no check would have
    said so.

    That is the both-directions rot one level up: **coverage drops while the count
    stays flat.**
    """
    registered = registered_artifacts()
    unchecked = sorted(registered - checked)
    unregistered = sorted(checked - registered)
    return {
        "ok": not unchecked and not unregistered,
        "registered": sorted(registered),
        "checked": sorted(checked),
        "registered_but_never_checked": unchecked,
        "checked_but_not_registered": unregistered,
        "summary": (f"{len(checked)}/{len(registered)} registered artifacts "
                    f"validated" + (f" · UNCHECKED: {unchecked}" if unchecked
                                    else "")),
    }


def write_report(report: dict[str, Any], path: Path,
                 allow_unregistered: bool = False) -> dict[str, Any]:
    """Serialize — refusing, or STAMPING, when a quantity is unregistered.

    WRITE-TIME REFUSAL because a research record that gets quoted is expensive and
    hard to reverse, while blocking a write is cheap. The escape exists so an
    exploratory run is not blocked mid-flight, and it **stamps the artifact
    itself** rather than recording the gap somewhere a reader must go find: the
    same principle as printing coverage in the check's own output.
    """
    verdict = check(report)
    if not verdict["ok"]:
        if not allow_unregistered:
            raise ValueError(
                f"refusing to write {path.name}: {verdict['summary']}. "
                f"unregistered: {verdict['unregistered_values'][:5]} ... "
                f"stale: {verdict['registered_kinds_never_emitted'][:5]}"
            )
        report = dict(report)
        report["CONTAINS_UNREGISTERED_QUANTITIES"] = {
            "unregistered_values": verdict["unregistered_values"],
            "registered_kinds_never_emitted":
                verdict["registered_kinds_never_emitted"],
            "meaning": ("§B is NOT satisfied for this artifact. Quantities listed "
                        "here have no stated population or comparator and must "
                        "not be quoted."),
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    return verdict
