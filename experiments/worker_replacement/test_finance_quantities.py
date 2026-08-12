"""L6 acceptance — §B is enforced, and every direction of the check FIRES.

Run:  python3 -m experiments.worker_replacement.test_finance_quantities
"""

from __future__ import annotations

import json
from pathlib import Path

from . import finance_quantities as fq

HERE = Path(__file__).resolve().parent
REPORT = HERE / "records" / "R2" / "scope_report.json"
KIND_LIST = HERE / "records" / "L6" / "quantity_kinds.json"


def main() -> int:
    failures: list[str] = []
    print("L6 acceptance — every reported quantity carries its population and "
          "comparator\n")

    report = json.loads(REPORT.read_text())

    # ------------------------------------------------------------------ 1 ---
    print("1. the committed scope report is fully covered, BOTH DIRECTIONS")
    verdict = fq.check(report)
    print(f"   {verdict['summary']}")
    print(f"   [{'ok' if not verdict['unregistered_values'] else 'FAIL'}] no "
          f"emitted value lacks a registered kind")
    print(f"   [{'ok' if not verdict['registered_kinds_never_emitted'] else 'FAIL'}]"
          f" and no registered kind is never emitted (stale entries)")
    if verdict["unregistered_values"]:
        failures.append(f"unregistered: {verdict['unregistered_values'][:5]}")
    if verdict["registered_kinds_never_emitted"]:
        failures.append(f"stale: {verdict['registered_kinds_never_emitted'][:5]}")

    # COVERAGE IS NON-VACUOUS. A registry covering 3 values would also report
    # "0 unregistered", and that is the shape of every hollow check in this
    # project's history.
    substantive = verdict["n_values"] > 100 and verdict["n_kinds_matched"] > 20
    print(f"   [{'ok' if substantive else 'FAIL'}] and the coverage is "
          f"SUBSTANTIVE ({verdict['n_values']} values, "
          f"{verdict['n_kinds_matched']} kinds) — not a registry covering nothing")
    if not substantive:
        failures.append("coverage is too small to mean anything")

    # ------------------------------------------------------------------ 2 ---
    print("\n2. the class contract holds — rates cannot omit a comparator")
    try:
        fq.Quantity(key="x", cls="rate", population="p",
                    plausible_range=(0.0, 1.0))
        raised = False
    except ValueError:
        raised = True
    print(f"   [{'ok' if raised else 'FAIL'}] constructing a RATE with no "
          f"comparator RAISES")
    if not raised:
        failures.append("a rate without a comparator was constructible")

    try:
        fq.Quantity(key="x", cls="count", population="p",
                    plausible_range=(0, 9))
        raised_count = False
    except ValueError:
        raised_count = True
    print(f"   [{'ok' if raised_count else 'FAIL'}] and a COUNT must state a "
          f"comparator OR say why there is none")
    if not raised_count:
        failures.append("a count with neither comparator nor reason was "
                        "constructible")

    # The other direction: a well-formed entry of each class constructs.
    ok_forms = True
    try:
        fq.Quantity(key="r", cls="rate", population="p", comparator="c",
                    plausible_range=(0.0, 1.0))
        # The escape now requires a ROLE from the closed set, not free text —
        # which is what makes choosing a lax class buy nothing (RR-2).
        fq.Quantity(key="c", cls="count", population="p",
                    comparator_absent_because="a denominator",
                    absent_role="denominator", plausible_range=(0, 200))
    except ValueError:
        ok_forms = False
    print(f"   [{'ok' if ok_forms else 'FAIL'}] and well-formed entries of each "
          f"class DO construct (the other direction)")
    if not ok_forms:
        failures.append("a well-formed entry was rejected")

    # ------------------------------------------------------------------ 3 ---
    print("\n3. POSITIVE CONTROLS — each direction shown FIRING")
    planted = json.loads(REPORT.read_text())
    planted["a_quantity_nobody_registered"] = 0.42
    fired_unregistered = bool(fq.check(planted)["unregistered_values"])
    print(f"   [{'ok' if fired_unregistered else 'FAIL'}] direction 1 fires on an "
          f"UNREGISTERED emitted value")
    if not fired_unregistered:
        failures.append("POSITIVE CONTROL FAILED — an unregistered value passed")

    # Direction 2: a registered kind nothing emits. Simulated by checking a
    # report with a whole section removed, which is what a rename looks like.
    renamed = json.loads(REPORT.read_text())
    renamed.pop("variance_quantities", None)
    fired_stale = bool(fq.check(renamed)["registered_kinds_never_emitted"])
    print(f"   [{'ok' if fired_stale else 'FAIL'}] direction 2 fires when a "
          f"registered kind is NEVER EMITTED (what a rename looks like)")
    if not fired_stale:
        failures.append("POSITIVE CONTROL FAILED — stale entries passed")

    # ------------------------------------------------------------------ 4 ---
    print("\n4. WRITE-TIME REFUSAL, and the escape STAMPS rather than bypasses")
    out = HERE / "records" / "L6"
    try:
        fq.write_report(planted, out / "_should_not_exist.json")
        refused = False
    except ValueError:
        refused = True
    print(f"   [{'ok' if refused else 'FAIL'}] writing a report with an "
          f"unregistered quantity REFUSES")
    if not refused:
        failures.append("an unregistered report was written silently")
    (out / "_should_not_exist.json").unlink(missing_ok=True)

    stamped_path = out / "_stamped_example.json"
    fq.write_report(planted, stamped_path, allow_unregistered=True)
    stamped = json.loads(stamped_path.read_text())
    has_stamp = "CONTAINS_UNREGISTERED_QUANTITIES" in stamped
    print(f"   [{'ok' if has_stamp else 'FAIL'}] and the escape writes the gap "
          f"INTO THE ARTIFACT, not into a document someone must find")
    if not has_stamp:
        failures.append("the escape bypassed silently")
    stamped_path.unlink(missing_ok=True)

    # And a clean report writes without a stamp — the other direction.
    clean_path = out / "_clean_example.json"
    fq.write_report(report, clean_path)
    clean = json.loads(clean_path.read_text())
    print(f"   [{'ok' if 'CONTAINS_UNREGISTERED_QUANTITIES' not in clean else 'FAIL'}]"
          f" and a fully registered report writes with NO stamp")
    if "CONTAINS_UNREGISTERED_QUANTITIES" in clean:
        failures.append("a clean report was stamped")
    clean_path.unlink(missing_ok=True)

    # ------------------------------------------------------------------ 5 ---
    # THE KIND LIST IS ASSERTED, NOT REGENERATED. Regeneration achieves non-drift
    # by making drift undetectable — the same shape as the fixture that compared
    # "(load unavailable)" to itself six times.
    print("\n5. the committed kind list is ASSERTED against the registry, not "
          "regenerated")
    committed = json.loads(KIND_LIST.read_text())
    registered_keys = sorted(q.key for q in fq.REGISTRY)

    def concrete(kind: str) -> str:
        """A real path of this kind, by instantiating its index dimensions."""
        return (kind.replace("[]", "[0]")
                    .replace("<cell/seed>", "0/23")
                    .replace("<cell>", "0")
                    .replace("<seed>", "seed3"))

    # RESOLVED KEY, NOT A TRUNCATED PREFIX (LS blocker). The first version took
    # `k.split("[")[0]` and asked whether ANY path under that container resolved.
    # For `episodes[].regret_share` the prefix is `episodes`, so the question was
    # "does anything under `episodes` resolve" — true for every entry in the
    # container, and therefore **blind to 17 of the 55 kinds, the densest region
    # of the list**. Each kind must now resolve to a SPECIFIC registry entry.
    resolution = {k: fq.resolve(concrete(k)) for k in committed["kinds"]}
    unresolved = sorted(k for k, q in resolution.items() if q is None)
    print(f"   {len(registered_keys)} registered entries cover "
          f"{len(committed['kinds'])} path-derived kinds")
    print(f"   [{'ok' if not unresolved else 'FAIL'}] every path-derived kind "
          f"resolves to a SPECIFIC registry entry "
          f"({unresolved[:3] or 'all resolve'})")
    if unresolved:
        failures.append(f"path-derived kinds with no registry entry: {unresolved}")

    # THE CONTROL LS SPECIFIED AND I DID NOT BUILD. Without it the check above
    # passed while being blind over a third of the list — and section 5's own
    # comment named the defect it was repeating. Planted inside `episodes[]`
    # deliberately: that is the container the truncation made invisible.
    planted_kinds = ["episodes[].totally_made_up_quantity",
                     "episodes[].seed_XYZ",
                     "coverage_misrouting.invented"]
    fired = [k for k in planted_kinds if fq.resolve(concrete(k)) is None]
    all_fired = len(fired) == len(planted_kinds)
    print(f"   [{'ok' if all_fired else 'FAIL'}] and a bogus kind is REJECTED, "
          f"including inside `episodes[]` where the truncation was blind "
          f"({len(fired)}/{len(planted_kinds)} rejected)")
    if not all_fired:
        failures.append(
            f"POSITIVE CONTROL FAILED — these bogus kinds resolved: "
            f"{[k for k in planted_kinds if k not in fired]}; the section-5 "
            f"assertion is worthless without it")

    # THE DIFFERENCE BETWEEN 55 AND 52 IS THE POINT, not a discrepancy: three
    # kinds are emitted at TWO sites each (`n_declined`, `n_unreadable`,
    # `regret_share`), and a path-derived normaliser necessarily counts them
    # twice. Declared keys collapse them correctly; a derived key cannot.
    print(f"   NOTE: {len(committed['kinds'])} path-derived vs "
          f"{len(registered_keys)} declared. The gap is kinds emitted at more "
          f"than one\n        site — which is the argument for declaring keys "
          f"rather than deriving them.")


    # ------------------------------------------------------------------ 6 ---
    # RR-1: §B CANNOT APPLY TO WHAT THE WALK CANNOT SEE. The first walk took
    # int/float and dropped bool, so a quantity formatted as a string, returned as
    # None, or expressed as a boolean was EXEMPT rather than flagged — and the
    # widest case was the primary DV's own None, its UNMEASURABLE form.
    print("\n6. the walk sees every evasion RR probed")
    want = {"0.42": True, None: True, True: True, 7: True,
            "this sentence is not a measurement": False}
    for value, expect in want.items():
        got = fq.is_quantity_value(value)
        print(f"   [{'ok' if got == expect else 'FAIL'}] {str(value)[:34]!r}: "
              f"walked={got}")
        if got != expect:
            failures.append(f"walk saw {value!r} as {got}, expected {expect}")

    for name, value in [("string", "0.42"), ("none", None), ("bool", True)]:
        probe = json.loads(REPORT.read_text())
        probe[f"unregistered_{name}"] = value
        fired = bool(fq.check(probe)["unregistered_values"])
        print(f"   [{'ok' if fired else 'FAIL'}] an unregistered {name}-valued "
              f"quantity is FLAGGED (seeing is not flagging)")
        if not fired:
            failures.append(f"an unregistered {name} value passed")

    dv_none = fq.BY_KEY["reroute.rerouted_share_conditioned"]
    ok_none = dv_none.may_be_none and "UNMEASURABLE" in dv_none.none_means
    print(f"   [{'ok' if ok_none else 'FAIL'}] the PRIMARY DV declares its None "
          f"form and says it means unmeasurable, not zero")
    if not ok_none:
        failures.append("the DV's None form is undeclared")

    fired_none = bool(fq.check({"n_episodes": None})["undeclared_none_values"])
    print(f"   [{'ok' if fired_none else 'FAIL'}] a registered kind returning an "
          f"UNDECLARED None is flagged")
    if not fired_none:
        failures.append("an undeclared None passed")

    # ------------------------------------------------------------------ 6b ---
    # EVERY REGISTERED ARTIFACT IS CHECKED AGAINST A REAL REPORT OF THAT ARTIFACT.
    # I introduced this gap while closing two others: artifact scoping made
    # registering under a new artifact a way to opt OUT of validation while
    # appearing registered. `reroute` held 12 entries including the PRIMARY DV and
    # was validated by nothing.
    print("\n6b. every REGISTERED artifact is CHECKED — the gap artifact scoping "
          "opened")
    from .check_load_feedback import run_machinery_episode
    from . import finance_reroute as rr

    manager, _engine, machinery = run_machinery_episode("0")
    machinery["completions"] = [{"task_id": t, "timestep": s}
                                for t, s in manager.completed_at.items()]
    reroute_report = rr.rerouted_share(machinery)

    checked_verdicts = {
        "scope_report": verdict,
        "reroute": fq.check(reroute_report, artifact="reroute"),
    }
    coverage = fq.assert_artifact_coverage(set(checked_verdicts))
    print(f"   {coverage['summary']}")
    for artifact, v in sorted(checked_verdicts.items()):
        print(f"     {artifact:<14} {v['summary']}")
        if not v["ok"]:
            failures.append(f"{artifact}: {v['summary']}")
    print(f"   [{'ok' if coverage['ok'] else 'FAIL'}] artifacts CHECKED == "
          f"artifacts REGISTERED (unchecked: "
          f"{coverage['registered_but_never_checked'] or 'none'})")
    if not coverage["ok"]:
        failures.append(f"artifact coverage: {coverage}")

    # POSITIVE CONTROL — a registered artifact that nobody checks must FAIL.
    fired_cov = not fq.assert_artifact_coverage({"scope_report"})["ok"]
    print(f"   [{'ok' if fired_cov else 'FAIL'}] and the assertion FIRES when an "
          f"artifact is registered but never checked")
    if not fired_cov:
        failures.append("POSITIVE CONTROL FAILED — an unchecked artifact passed")

    # And the residual LS left with it: a rate emitted as a display percentage.
    pct_seen = fq.is_quantity_value("12.5%")
    print(f"   [{'ok' if pct_seen else 'FAIL'}] a rate emitted as a display "
          f"percentage ('12.5%') is now SEEN by the walk")
    if not pct_seen:
        failures.append("a percentage-formatted rate is still invisible")
    pct_flagged = bool(fq.check({"unregistered_pct": "12.5%"})["unregistered_values"])
    print(f"   [{'ok' if pct_flagged else 'FAIL'}] and FLAGGED when unregistered")
    if not pct_flagged:
        failures.append("a percentage-formatted rate passed unregistered")

    # ------------------------------------------------------------------ 7 ---
    # RR-2: the class contract was bypassable BY CHOOSING THE CLASS, and seven
    # entries had done it. The comparator rule is class-independent now, so
    # mis-declaring buys nothing, and the value type is asserted, so it is caught.
    print("\n7. the RANGE binds the entry to the data — what it may BE")
    try:
        fq.Quantity(key="fake", cls="count", population="p",
                    comparator_absent_because="a denominator",
                    plausible_range=(0, 9))
        bypass = True
    except ValueError:
        bypass = False
    print(f"   [{'ok' if not bypass else 'FAIL'}] RR's exact bypass — cls='count' "
          f"with a free-text reason — is REJECTED (absent_role required)")
    if bypass:
        failures.append("RR's bypass still constructs")

    # THE RANGE RULE — what a quantity may BE, not only what it is over.
    # ORIGIN: a units error (an RWA figure used as a score) produced losses of
    # ~1e9 and was caught only because it was 1e8x wrong. The SAME substitution at
    # 2x would have survived every check in this suite, because the arithmetic was
    # correct. So the controls below include the 2x case, not just the absurd one.
    try:
        fq.Quantity(key="x", cls="measure", population="p", comparator="c")
        no_range = True
    except ValueError:
        no_range = False
    print(f"   [{'ok' if not no_range else 'FAIL'}] a numeric entry with NO "
          f"declared range is REJECTED at construction")
    if no_range:
        failures.append("a numeric quantity without a range was constructible")

    units = bool(fq.check({"episodes": [{"achieved": 4.2e9}]})
                 ["wrong_class_for_value"])
    print(f"   [{'ok' if units else 'FAIL'}] a UNITS substitution (an RWA figure "
          f"as a score) is caught — the 1e8x case")
    if not units:
        failures.append("a units substitution passed")

    subtle = bool(fq.check({"episodes": [{"achieved": 17.2}]})
                  ["wrong_class_for_value"])
    print(f"   [{'ok' if subtle else 'FAIL'}] AND THE 2x CASE — a score of 17.2 "
          f"over 9 segments — which every other check in this suite passes")
    if not subtle:
        failures.append("a 2x-scale error passed; the range is too loose to bind")

    residual = bool(fq.check({"episodes": [{"split_residual": 0.03}]})
                    ["wrong_class_for_value"])
    print(f"   [{'ok' if residual else 'FAIL'}] and a decomposition residual of "
          f"0.03 is caught — its range says it must be ~0")
    if not residual:
        failures.append("a non-zero residual passed")

    in_range = not fq.check({"episodes": [{"achieved": 8.4}]})["wrong_class_for_value"]
    print(f"   [{'ok' if in_range else 'FAIL'}] and a PLAUSIBLE score passes "
          f"(the other direction)")
    if not in_range:
        failures.append("a plausible value was rejected")

    caught_rate = bool(fq.check({"rerouted_share_conditioned": 1.7},
                                artifact="reroute")["wrong_class_for_value"])
    print(f"   [{'ok' if caught_rate else 'FAIL'}] and a share outside [0,1] is "
          f"caught")
    if not caught_rate:
        failures.append("an out-of-range rate passed")

    still_wrong = verdict["wrong_class_for_value"]
    print(f"   [{'ok' if not still_wrong else 'FAIL'}] and every value in the "
          f"live report falls inside its declared range")
    if still_wrong:
        failures.append(f"class/value mismatches remain: {still_wrong[:3]}")

    (out / "quantity_registry_acceptance.json").write_text(json.dumps({
        "verdict": verdict,
        "n_registered_entries": len(registered_keys),
        "n_path_derived_kinds": len(committed["kinds"]),
        "classes": sorted({q.cls for q in fq.REGISTRY}),
        "entries_with_retraction_notes": sorted(
            q.key for q in fq.REGISTRY if "RETRACTION" in q.note),
        "failures": failures,
    }, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print(f"§B: PASS — {coverage['summary']} · {verdict['summary']}. "
          f"Rates cannot omit a comparator, both "
          f"directions of the registry fire on planted defects, the emitter "
          f"refuses unregistered quantities and stamps the artifact when "
          f"explicitly overridden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
