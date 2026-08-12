"""S8 — the report-format convention and its DETERMINISTIC parser.

This is the seam between free worker text and S4's scorer. The scorer consumes
`{segment_id: float | None}`; the worker produces prose. Everything the study
concludes passes through this function, so it is deliberately boring, strict, and
asserted.

THE RULE THAT SHAPES THE WHOLE MODULE: a parse failure is a MISSING REPORT, never
a guessed extraction. If the text does not carry the convention exactly, the
segment scores 0, is named in `missing_segments`, and a run event is recorded.

Why refusing to guess matters more than recall here: a lenient parser that digs a
plausible number out of malformed prose converts a WORKER failure into a SCORER
success, and does it invisibly. The allocation/execution decomposition would then
attribute the recovered number to the worker's competence. A missing report is a
real, interpretable outcome; a guessed one is a fabricated observation, and there
is no later stage that can tell the two apart.

Every rejection carries a NAMED reason, for the same reason S7's rejected rows do:
"failed to parse" cannot distinguish a worker that ignored the convention from a
parser that is broken.

THE CONVENTION
--------------
Two lines, anywhere in the deliverable, each on its own line:

    method: IRB          (or)   method: SA
    rwa: 12345678.90

Case-insensitive on the key and on IRB/SA. Thousands separators are accepted in
the number because models emit them constantly and rejecting them would measure
formatting compliance rather than capital calculation. AMBIGUITY IS REJECTED: two
different `rwa:` values in one deliverable is a parse failure, not a
first-one-wins guess.
"""

from __future__ import annotations

import re
from typing import Any, NamedTuple

from manager_agent_gym.core.common.run_trace import record_run_event

# REPORT FORMAT — a FORMAT, not an instruction to produce an answer.
#
# The previous wording ("your deliverable MUST contain these two lines ... do not
# omit either line") re-imposed produce-a-number through the back door. The clause
# whose PURPOSE was to force an answer had been removed under E3a; this one, whose
# EFFECT is identical, survived because it exists for a legitimate reason —
# deterministic parsing. That relocated the tautology rather than removing it: a
# worker that would decline had still been told its deliverable must carry a
# figure, so a measured decline rate would still be partly a measurement of our
# own instruction.
#
# The fix is to give REFUSAL A PARSEABLE FORM rather than to forbid it. Declining
# is now available AND machine-readable, which is better than either forbidding it
# or accepting unparseable prose.
REPORT_CONVENTION_TEXT = (
    "REPORT FORMAT — so your answer can be read automatically, put your "
    "conclusion in these two lines, each on its own line:\n"
    "  method: IRB        (or SA, if you used the standardised approach)\n"
    "  rwa: <the risk-weighted assets figure, in currency units>\n"
    "Write the number plainly, e.g. 'rwa: 12345678.90' — not a range, and not "
    "more than one rwa line. Explanatory prose around them is fine.\n"
    "If you judge that you cannot price this segment, say so in the same form:\n"
    "  method: none\n"
    "  rwa: unavailable\n"
    "That is a legitimate outcome and is recorded as one; it is not a failure to "
    "follow the format."
)

# The permitted decline form. Recognised as a FIRST-CLASS OUTCOME rather than a
# parse failure: a worker that declines in the agreed shape has communicated
# something, and collapsing it into "unparseable" would throw away the signal the
# unscripting exists to expose.
_DECLINE_RWA_RE = re.compile(
    r"^[ \t>*\-]*rwa[ \t]*:[ \t]*"
    r"(unavailable|none|n/?a|not available|cannot[ \t]+be[ \t]+determined)"
    r"[ \t.]*$",
    re.IGNORECASE | re.MULTILINE,
)
_DECLINE_METHOD_RE = re.compile(
    r"^[ \t>*\-]*method[ \t]*:[ \t]*(none|n/?a)[ \t.]*$",
    re.IGNORECASE | re.MULTILINE,
)

_METHOD_RE = re.compile(r"^[ \t>*\-]*method[ \t]*:[ \t]*(IRB|SA)[ \t.]*$",
                        re.IGNORECASE | re.MULTILINE)
# ANCHORED: what the convention actually asks for, and the only thing allowed to
# SUPPLY the value. Precise, so prose mentioning a number never becomes a report.
_RWA_RE = re.compile(
    r"^[ \t>*\-]*rwa[ \t]*:[ \t]*"
    r"(?:eur|usd|gbp|€|\$|£)?[ \t]*"
    r"(-?[0-9][0-9,_ ]*(?:\.[0-9]+)?)"
    r"[ \t]*(?:eur|usd|gbp)?[ \t.]*$",
    re.IGNORECASE | re.MULTILINE,
)
# UNANCHORED, and used ONLY as a contradiction check — never to supply a value.
#
# WHY THIS EXISTS (caught by this module's own acceptance): with anchored matching
# alone, a deliverable reading "rwa: 4200000 ... On reflection, rwa: 4300000"
# matched ONCE and parsed to 4,200,000. The worker's revision sat in the text and
# the parser reported the number the worker had abandoned — precisely the silent
# fabrication this module exists to prevent, arriving through the mid-prose form
# rather than the two-clean-lines form the ambiguity test used.
#
# Splitting the two roles keeps precision (only a conventional line can supply a
# value) while removing the blind spot (any disagreeing occurrence anywhere in the
# text makes the deliverable ambiguous, and ambiguous is refused).
_RWA_ANY_RE = re.compile(
    r"rwa[ \t]*:[ \t]*(?:eur|usd|gbp|€|\$|£)?[ \t]*"
    r"(-?[0-9][0-9,_]*(?:\.[0-9]+)?)",
    re.IGNORECASE,
)
# A RANGE where a number belongs: reported separately from "no rwa line at all",
# because the two say different things about the worker. One ignored the
# convention; the other followed it and declined to commit to a figure.
_RWA_RANGE_RE = re.compile(
    r"^[ \t>*\-]*rwa[ \t]*:[ \t]*[^\n]*?[0-9][ \t]*(?:-|–|to)[ \t]*[0-9]",
    re.IGNORECASE | re.MULTILINE,
)


class ParsedReport(NamedTuple):
    """One worker deliverable, parsed. `rwa is None` means NOT REPORTED.

    `declined` distinguishes the two ways that happens: an EXPLICIT decline in the
    agreed form (the worker judged it could not price the segment and said so),
    versus a deliverable we could not read. Both score 0; they are entirely
    different behaviours and must never be summed.
    """

    rwa: float | None
    method: str | None
    reason: str | None  # named cause when rwa is None; None when parsed
    declined: bool = False


def _to_float(raw: str) -> float | None:
    cleaned = raw.replace(",", "").replace("_", "").replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_report(text: str | None) -> ParsedReport:
    """Parse one deliverable. Never guesses; every failure names its cause."""
    if text is None or not text.strip():
        return ParsedReport(None, None, "deliverable is empty")

    # EXPLICIT DECLINE first — before anything can call it malformed.
    if _DECLINE_RWA_RE.search(text) or _DECLINE_METHOD_RE.search(text):
        return ParsedReport(
            None, "NONE",
            "explicit decline in the permitted form (method: none / rwa: "
            "unavailable) — a judgement, not a formatting failure",
            declined=True)

    methods = sorted({match.group(1).upper() for match in _METHOD_RE.finditer(text)})
    if len(methods) > 1:
        return ParsedReport(
            None, None,
            f"conflicting 'method:' declarations {methods} — ambiguous",
        )
    method = methods[0] if methods else None

    raw_values = [match.group(1) for match in _RWA_RE.finditer(text)]
    if not raw_values:
        if _RWA_RANGE_RE.search(text):
            return ParsedReport(
                None, method,
                "the 'rwa:' line holds a RANGE, not a figure — the convention asks "
                "for a single number and picking an endpoint would invent one",
            )
        return ParsedReport(None, method, "no line matching the 'rwa:' convention")

    values = [_to_float(raw) for raw in raw_values]
    if any(value is None for value in values):
        return ParsedReport(None, method, "an 'rwa:' line held an unparseable number")

    # CONTRADICTION CHECK across the whole text, not just the conventional lines.
    # Any `rwa: <number>` anywhere that disagrees makes the deliverable ambiguous.
    everywhere = [_to_float(match.group(1)) for match in _RWA_ANY_RE.finditer(text)]
    distinct = {round(value, 6) for value in values + everywhere if value is not None}
    if len(distinct) > 1:
        return ParsedReport(
            None, method,
            f"{len(distinct)} DIFFERENT 'rwa:' values in one deliverable "
            f"({sorted(distinct)}) — ambiguous, and guessing one is not allowed",
        )

    return ParsedReport(values[0], method, None)


def parse_segment_reports(
    deliverables: dict[str, str | None],
    segment_ids: list[str],
) -> dict[str, Any]:
    """Parse every allocated segment's deliverable into the scorer's report dict.

    Returns the `reports` dict S4 consumes, plus the per-segment parse detail and
    the named failures. A segment with no deliverable at all and one whose
    deliverable failed to parse are BOTH missing, and both are named — the
    distinction is preserved in `failures` rather than collapsed.
    """
    reports: dict[str, float | None] = {}
    detail: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, str]] = []

    for segment_id in segment_ids:
        text = deliverables.get(segment_id)
        parsed = parse_report(text)
        detail[segment_id] = {
            "rwa": parsed.rwa,
            "method": parsed.method,
            "reason": parsed.reason,
            "declined": parsed.declined,
            "had_deliverable": segment_id in deliverables and bool(text),
        }
        if parsed.rwa is None:
            reason = (
                parsed.reason if segment_id in deliverables and text
                else "no deliverable produced for this segment"
            )
            failures.append({"segment_id": segment_id, "reason": reason,
                             "declined": parsed.declined})
            # A DECLINE IS ITS OWN EVENT. Logging it as "unparsed" would file a
            # judgement the worker communicated under the same heading as a
            # deliverable we could not read.
            record_run_event(
                "segment_declined" if parsed.declined else "segment_report_unparsed",
                {"segment_id": segment_id, "reason": reason},
                actor_type="parser",
            )
            continue
        reports[segment_id] = parsed.rwa

    return {
        "reports": reports,
        "detail": detail,
        "failures": failures,
        "n_parsed": len(reports),
        "n_missing": len(failures),
        # SPLIT, never summed: an explicit decline and an unreadable deliverable
        # are different behaviours that happen to share a score of 0.
        "n_declined": sum(1 for f in failures if f.get("declined")),
        "n_unreadable": sum(1 for f in failures if not f.get("declined")),
        "declined_segments": [f["segment_id"] for f in failures if f.get("declined")],
    }
