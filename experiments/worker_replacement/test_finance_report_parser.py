"""S8 acceptance — the report parser.

The seam between worker text and the S4 scorer. Three things are demonstrated:

  1. POSITIVES: the convention parses, including the messy-but-unambiguous forms
     models actually emit (thousands separators, currency prefixes, markdown
     bullets, surrounding prose).
  2. NEGATIVES: every failure mode returns rwa=None WITH A NAMED CAUSE. Most
     important is AMBIGUITY — two different rwa values must be REJECTED, because
     first-one-wins would fabricate an observation.
  3. THE SEAM ITSELF: parsed reports flow into the production scorer and a parse
     failure lands in `missing_segments`, driven through the real scorer rather
     than asserted about it.

Run:  python3 -m experiments.worker_replacement.test_finance_report_parser
"""

from __future__ import annotations

import json
from pathlib import Path

from . import finance_generator as gen
from . import finance_report_parser as rp
from . import finance_scorer as sc

HERE = Path(__file__).resolve().parent

POSITIVES: list[tuple[str, str, float, str]] = [
    ("plain", "method: IRB\nrwa: 12345678.90", 12345678.90, "IRB"),
    ("thousands separators", "method: SA\nrwa: 12,345,678.90", 12345678.90, "SA"),
    ("currency prefix", "method: IRB\nrwa: EUR 4200000", 4200000.0, "IRB"),
    ("markdown bullet", "- method: SA\n- rwa: 999.5", 999.5, "SA"),
    ("lowercase keys and value", "method: irb\nrwa: 1000", 1000.0, "IRB"),
    ("surrounded by prose",
     "I applied the internal model to this segment.\n\nmethod: IRB\n"
     "rwa: 8,675,309.00\n\nThe figure reflects the maturity adjustment.",
     8675309.0, "IRB"),
    ("trailing period", "method: SA.\nrwa: 250000.00.", 250000.0, "SA"),
    ("repeated but IDENTICAL value is not ambiguous",
     "rwa: 1000.00\nmethod: SA\nSummary line — rwa: 1000.00", 1000.0, "SA"),
]

NEGATIVES: list[tuple[str, str | None, str]] = [
    ("empty", "", "empty"),
    ("none", None, "empty"),
    ("no rwa line", "method: IRB\nThe capital charge is roughly 4.2 million.",
     "convention"),
    ("prose number only", "The risk-weighted assets come to EUR 4,200,000.",
     "convention"),
    ("AMBIGUOUS — two different values",
     "rwa: 4200000\nmethod: IRB\nOn reflection, rwa: 4300000", "ambiguous"),
    ("unparseable number", "method: SA\nrwa: about four million", "convention"),
    ("range instead of a number", "method: IRB\nrwa: 4000000-4500000", "ambiguous"),
]


def main() -> int:
    failures: list[str] = []
    print("S8 — report-format convention and parser\n")

    print("1. positives — the convention parses through the messy forms models emit:")
    for label, text, expected, method in POSITIVES:
        parsed = rp.parse_report(text)
        ok = (parsed.rwa is not None and abs(parsed.rwa - expected) < 1e-9
              and parsed.method == method)
        print(f"   [{'ok' if ok else 'FAIL'}] {label:<44} -> "
              f"{parsed.rwa} / {parsed.method}")
        if not ok:
            failures.append(f"positive '{label}' parsed as {parsed}")

    print("\n2. negatives — every failure is rwa=None WITH A NAMED CAUSE:")
    for label, text, _kind in NEGATIVES:
        parsed = rp.parse_report(text)
        ok = parsed.rwa is None and bool(parsed.reason)
        print(f"   [{'ok' if ok else 'FAIL'}] {label:<44} -> "
              f"{(parsed.reason or 'NO REASON GIVEN')[:52]}")
        if not ok:
            failures.append(f"negative '{label}' returned {parsed}")

    # The one that would do real damage if it regressed: two different values must
    # never resolve to one of them. A first-one-wins parser passes every other test
    # in this file, so it is asserted on its own.
    ambiguous = rp.parse_report("rwa: 4200000\nrwa: 4300000")
    amb_ok = ambiguous.rwa is None and "ambiguous" in (ambiguous.reason or "")
    print(f"\n   [{'ok' if amb_ok else 'FAIL'}] AMBIGUITY IS REJECTED, not "
          f"resolved — first-one-wins would fabricate an\n        observation and "
          f"nothing downstream could detect it")
    if not amb_ok:
        failures.append("ambiguous input did not reject")

    # Distinct reasons: a single catch-all message would make the named-cause
    # requirement decorative (the S5 'no catch-all masquerading' check).
    reasons = {rp.parse_report(text).reason for _l, text, _k in NEGATIVES}
    print(f"   [{'ok' if len(reasons) >= 3 else 'FAIL'}] {len(reasons)} DISTINCT "
          f"failure messages across {len(NEGATIVES)} negatives — no catch-all")
    if len(reasons) < 3:
        failures.append("parser failure messages are not discriminating")

    # --- 3. the seam, driven through the PRODUCTION scorer --------------------
    print("\n3. the seam — parsed reports drive the real scorer:")
    instance = gen.generate(101)
    segment_ids = [s["segment_id"] for s in instance["segments"]]
    workers = sc.roster_workers(instance)
    allocation = {sid: workers[i % len(workers)]["worker_id"]
                  for i, sid in enumerate(segment_ids)}

    # Faithful deliverables for every segment except one, which is malformed.
    broken = segment_ids[2]
    deliverables: dict[str, str | None] = {}
    for sid in segment_ids:
        segment = next(s for s in instance["segments"] if s["segment_id"] == sid)
        worker = next(w for w in instance["workers"]
                      if w["worker_id"] == allocation[sid])
        value = sc.attainable_report(segment, worker)
        deliverables[sid] = (
            "The figure could not be finalised." if sid == broken
            else f"method: {sc.applicable_approach(segment)}\nrwa: {value:,.2f}"
        )

    parsed = rp.parse_segment_reports(deliverables, segment_ids)
    print(f"   parsed {parsed['n_parsed']}/{len(segment_ids)}, "
          f"missing {parsed['n_missing']}")
    for failure in parsed["failures"]:
        print(f"     {failure['segment_id']}: {failure['reason'][:60]}")

    missing = sc.validate_reports(instance, allocation, parsed["reports"])
    seam_ok = missing == [broken]
    print(f"   [{'ok' if seam_ok else 'FAIL'}] the malformed deliverable reaches "
          f"the scorer as a MISSING segment: {missing}")
    if not seam_ok:
        failures.append(f"missing_segments was {missing}, expected [{broken}]")

    achieved = sc.achieved(instance, allocation, parsed["reports"])
    faithful = sc.score(instance, allocation)
    loss_ok = achieved < faithful - 1e-9
    print(f"   achieved {achieved:.4f} vs faithful-execution {faithful:.4f} -> "
          f"[{'ok' if loss_ok else 'FAIL'}] the missing report COSTS score "
          f"({faithful - achieved:.4f})")
    if not loss_ok:
        failures.append("a missing report did not reduce the achieved score")

    # A guessed extraction would have scored here instead. Demonstrated rather
    # than asserted in prose: the same text under a lenient reading carries a
    # number, and the parser still refuses it.
    lenient_bait = "The risk-weighted assets come to EUR 4,200,000."
    print(f"   [{'ok' if rp.parse_report(lenient_bait).rwa is None else 'FAIL'}] "
          f"a deliverable containing a perfectly good number in PROSE is still "
          f"missing —\n        recall is deliberately sacrificed to keep worker "
          f"failures attributable")
    if rp.parse_report(lenient_bait).rwa is not None:
        failures.append("prose number was extracted; the parser is guessing")

    # --- 4. THE PERMITTED DECLINE, a first-class outcome ---------------------
    # LS's R1 read: the old convention re-imposed produce-a-number ("your
    # deliverable MUST contain these two lines ... do not omit either line").
    # That clause had a legitimate purpose (deterministic parsing) and an
    # identical EFFECT to the one E3a removed, so it relocated the tautology
    # rather than removing it. Refusal now has a FORM instead of a prohibition.
    print("\n4. refusal has a PARSEABLE FORM, not a prohibition:")
    declines = [
        ("permitted form", "method: none\nrwa: unavailable"),
        ("with prose", "I cannot price this segment.\nmethod: none\n"
                       "rwa: unavailable"),
        ("n/a variant", "rwa: N/A"),
        ("not available", "method: none\nrwa: not available"),
    ]
    for label, text in declines:
        parsed = rp.parse_report(text)
        ok = parsed.rwa is None and parsed.declined
        print(f"   [{'ok' if ok else 'FAIL'}] {label:<18} -> declined="
              f"{parsed.declined}")
        if not ok:
            failures.append(f"decline form '{label}' not recognised")

    # A DECLINE IS NOT AN UNREADABLE DELIVERABLE. Both score 0; they are different
    # behaviours and summing them would erase the signal the unscripting exists to
    # expose.
    garbage = rp.parse_report("the figure could not be finalised")
    split_ok = garbage.rwa is None and not garbage.declined
    print(f"   [{'ok' if split_ok else 'FAIL'}] an UNREADABLE deliverable is NOT "
          f"counted as a decline (declined={garbage.declined})")
    if not split_ok:
        failures.append("unreadable deliverable was counted as a decline")

    mixed = rp.parse_segment_reports(
        {"a": "method: none\nrwa: unavailable", "b": "unreadable prose",
         "c": "method: SA\nrwa: 1000.00"}, ["a", "b", "c"])
    counts_ok = (mixed["n_declined"] == 1 and mixed["n_unreadable"] == 1
                 and mixed["n_parsed"] == 1)
    print(f"   [{'ok' if counts_ok else 'FAIL'}] a mixed batch splits cleanly: "
          f"{mixed['n_parsed']} parsed, {mixed['n_declined']} declined, "
          f"{mixed['n_unreadable']} unreadable")
    if not counts_ok:
        failures.append("decline/unreadable/parsed counts do not split")

    # --- 5. THE IMPERATIVE IS GONE FROM THE CONVENTION ITSELF ----------------
    banned = ["must contain", "do not omit", "always produce", "you must provide"]
    present = [b for b in banned if b in rp.REPORT_CONVENTION_TEXT.lower()]
    print(f"\n5. the convention no longer COMPELS a figure:")
    print(f"   [{'ok' if not present else 'FAIL'}] none of {banned} appears "
          f"({present or 'none'})")
    if present:
        failures.append(f"the convention still compels output: {present}")
    invites = "cannot price" in rp.REPORT_CONVENTION_TEXT.lower()
    print(f"   [{'ok' if invites else 'FAIL'}] and it explicitly INVITES the "
          f"decline form — availability stated, not merely\n        unprohibited")
    if not invites:
        failures.append("the convention does not offer the decline form")

    out = HERE / "records" / "S8"
    out.mkdir(parents=True, exist_ok=True)
    (out / "parser_cases.json").write_text(json.dumps({
        "positives": [{"label": lab, "text": txt, "expected_rwa": exp,
                       "expected_method": m} for lab, txt, exp, m in POSITIVES],
        "negatives": [{"label": lab, "text": txt,
                       "reason": rp.parse_report(txt).reason}
                      for lab, txt, _k in NEGATIVES],
        "seam": {"missing_segments": missing, "achieved": achieved,
                 "faithful": faithful},
    }, indent=2, sort_keys=True) + "\n")

    print()
    if failures:
        print("RESULT: FAIL")
        for line in failures:
            print(f"  {line}")
        return 1
    print("RESULT: PASS — the convention parses, every failure names a cause, "
          "ambiguity is rejected, and a parse failure reaches the scorer as a "
          "missing segment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
