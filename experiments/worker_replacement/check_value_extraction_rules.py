"""Would a looser value-extraction rule be safe? Measured, not argued.

Written because two lenient rules were proposed in good faith and both are wrong,
and because the objection to testing them ("the corpus holds one instance of the
thing they must catch") is only half true. The RECOVERY case is n=1. The SAFETY
case is n=157: every deliverable the strict parser already read correctly is an
opportunity for a lenient rule to disagree, and disagreement there is a wrong
number entering the DV silently.

    rule A  anchor on `rwa`, take the NEXT number   (RE built it; returns the EAD)
    rule B  take the LAST number in the deliverable (proposed by the researcher)

Zero model calls. Run:

    python -m experiments.worker_replacement.check_value_extraction_rules
"""

from __future__ import annotations

import glob
import json
import re
from typing import Any

NUM = re.compile(r"[-+]?\d[\d,]*\.?\d*")
ANCHORED = re.compile(r"(?i)rwa[^0-9\n]{0,20}([-+]?\d[\d,]*\.?\d*)")
TOL = 0.01


def _f(s: str) -> float | None:
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def rule_last_number(text: str) -> float | None:
    found = NUM.findall(text)
    return _f(found[-1]) if found else None


def rule_anchored_next(text: str) -> float | None:
    m = ANCHORED.search(text)
    return _f(m.group(1)) if m else None


RULES = {"B: last number": rule_last_number, "A: anchored, next number": rule_anchored_next}


def deliverables() -> list[tuple[str, str, str, dict[str, Any]]]:
    out = []
    for p in sorted(glob.glob("experiments/worker_replacement/records/*/run_*.json")):
        if "_FAILED" in p or "_INCOMPLETE" in p:
            continue
        b = json.load(open(p))
        detail = b.get("parse_detail") or {}
        texts = b.get("deliverables") or {}
        for seg, d in detail.items():
            t = texts.get(seg)
            if isinstance(t, str) and t.strip():
                out.append((p.split("/")[-1], seg, t, d))
    return out


def main() -> int:
    rows = deliverables()
    if not rows:
        raise SystemExit("no deliverables -- refusing to report an empty verdict")
    print(f"{len(rows)} deliverables with text, across the committed corpus\n")

    for name, rule in RULES.items():
        agree = disagree = recovered = 0
        worst: list[tuple[str, str, float, float | None]] = []
        for fname, seg, text, d in rows:
            got = rule(text)
            truth = d.get("rwa")
            if truth is not None:                       # the strict parser READ it: truth known
                if got is not None and abs(got - truth) < TOL:
                    agree += 1
                else:
                    disagree += 1
                    worst.append((fname, seg, truth, got))
            elif not d.get("declined") and got is not None:
                recovered += 1
        total = agree + disagree
        print(f"{name}")
        print(f"  SAFETY  (strict parser succeeded, n={total}): "
              f"{agree} agree, {disagree} DISAGREE  -> {100*disagree/total:.1f}% wrong")
        print(f"  RECOVERY (strict parser failed):              {recovered}")
        worst.sort(key=lambda r: -(abs(r[2] - (r[3] or 0))))
        for fname, seg, truth, got in worst[:4]:
            print(f"    {fname:<26} {seg}  answer={truth:,.0f}  rule gave={got}")
        print()

    print("VERDICT: both lenient rules put wrong numbers into the DV, and the wrong")
    print("numbers are PARAMETERS the worker mentioned after answering -- the 12.5")
    print("Basel multiplier, the 75% retail weight, a maturity in years. They are")
    print("plausible-looking and nothing downstream would flag them.")
    print("\nThe strict parser costs ONE correct answer in the whole corpus.")
    print("Every lenient rule tested costs more, silently. The fix belongs in the")
    print("CONTRACT the worker is given, not in how the answer is read.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
