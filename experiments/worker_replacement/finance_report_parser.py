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
# ★ TIGHTENED 2026-08-09 (researcher-approved) AFTER A MEASURED FAILURE. One worker
# wrote its answer inside a numbered sentence — `4. RWA = 242,806,729.46 x 0.75 =
# 182,105,047.10` — and scored zero although the figure was correct to the cent.
#
# THE FIX IS IN THE CONTRACT, NOT IN THE READER, and that is measured rather than
# preferred: `check_value_extraction_rules.py` scores both proposed lenient readers
# against the 157 deliverables the strict parser already reads correctly.
#   take the LAST number       -> 7.0% wrong
#   anchor on `rwa`, next number -> 1.9% wrong
# Both return PARAMETERS the worker mentioned after answering — the 12.5 Basel
# multiplier, the 75% retail weight, a maturity in years — which are plausible and
# would enter the DV unflagged. The strict reader costs ONE correct answer in the
# whole corpus; every lenient reader tested costs more, silently.
#
# So reasoning goes BEFORE the two lines, and the old permission that invited the
# failure — "explanatory prose around them is fine" — is withdrawn.
#
# ★ TWO PROHIBITIONS WERE DROPPED ON RE's REVIEW, and the reason is worth keeping so
# nobody re-adds them as an obvious tightening. The first draft also forbade thousands
# separators and forbade anything following the rwa line. THE PARSER ACCEPTS BOTH — so
# the contract asserted two rules that nothing checked, which is the same shape as a
# field asserting more than its condition establishes, in prose. Neither protected
# anything the parser cannot already handle, and every extra rule is more surface for a
# worker to violate while trying to comply. The operative remedy is the worked-line
# warning below, which RE verified parses when followed.
REPORT_CONVENTION_TEXT = (
    "REPORT FORMAT — so your answer can be read automatically, END your reply with "
    "exactly these two lines, in this order, each alone on its own line with nothing "
    "else on it:\n"
    "  method: IRB        (or SA, if you used the standardised approach)\n"
    "  rwa: <the risk-weighted assets figure, in currency units>\n"
    "Put ALL your reasoning and arithmetic BEFORE these lines.\n"
    "Write the number plainly and alone, e.g. 'rwa: 12345678.90' — no '=' or '≈' "
    "on that line, not a range, and not more than one rwa line.\n"
    "A worked line such as 'RWA = 242,806,729.46 x 0.75 = 182,105,047.10' is NOT "
    "the rwa line and will not be read — it is reasoning. Show it above, then give "
    "the bare figure on its own rwa line.\n"
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


# A LOOSE READING, RECORDED AND NEVER SCORED (L13).
#
# WHY IT EXISTS. seg_03 of the first `partial` bundle computed the retail SA
# fallback correctly to the cent -- 242,806,729.46 x 0.75 = 182,105,047.095 --
# and scored ZERO because it wrote `RWA = ... = 182,105,047.10` instead of a line
# beginning `rwa:`. That is the successor recognising it holds no IRB approval and
# falling back under its mandate: the phenomenon the study exists to observe,
# discarded on punctuation. Scoring correct work as zero measures
# INSTRUCTION-FOLLOWING and reports it as ALLOCATION.
#
# WHY IT DOES NOT FEED THE SCORE. Across every bundle we hold, exactly ONE unparsed
# non-declined segment has a non-empty deliverable containing a number; the other
# 24-35 are empty. So a permissive rule gets ONE chance to fire correctly and NO
# chance to demonstrate it does not misfire on reasoning prose that happens to
# contain a figure. It cannot be control-tested on this corpus, and a rule that
# cannot be shown not to misfire must not be in the DV.
#
# So both facts are kept instead of trading one for the other: the strict parse is
# unchanged and remains the ONLY thing scored, while `rwa_loose` and `report_form`
# accumulate the evidence that would let the change be made safely later. If the
# two ever diverge on prose, we see it before it is scoring anything.
_NUMERIC_RE = re.compile(
    r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d{1,2}|\d{4,})")


def loose_rwa(text: str | None) -> tuple[float | None, str]:
    """A value the strict convention missed. NEVER scored -- recorded only.

    IT REFUSES TO GUESS, AND ON THE ONE CASE WE HAVE IT REFUSES. seg_03 wrote
    `RWA = 242,806,729.46 x 0.75 = 182,105,047.10`: the EAD, the weight and the
    answer, all on one line. My first version anchored on the token `rwa` and took
    the next number -- and returned **242,806,729.46, the EAD**, on the single
    segment the rule was written to recover. A permissive rule tested against its
    one instance MISFIRED on it.

    So this returns a value only when the deliverable contains EXACTLY ONE
    candidate number, which is the same refusal-to-guess the strict parser makes.
    On seg_03 that is `loose_ambiguous` and no value -- correct, because picking
    the last number is fitting a rule to one example, and n=1 is what I argued we
    could not tune on.

    THE FIELD THAT ACTUALLY CARRIES THE SIGNAL IS `report_form`, not this one: it
    needs no value extraction, so it cannot misfire. This is retained because it
    costs nothing and accumulates evidence for a decision on more data.
    """
    if not text or not text.strip():
        return None, "empty"
    values = {round(v, 6) for v in
              (_to_float(m.group(1)) for m in _NUMERIC_RE.finditer(text))
              if v is not None}
    if len(values) == 1:
        return values.pop(), "loose_single_number"
    if len(values) > 1:
        return None, "loose_ambiguous"
    return None, "loose_no_number"


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
        loose_value, loose_form = loose_rwa(text)
        detail[segment_id] = {
            "rwa": parsed.rwa,
            "method": parsed.method,
            "reason": parsed.reason,
            "declined": parsed.declined,
            "had_deliverable": segment_id in deliverables and bool(text),
            # OBSERVATIONAL ONLY. Nothing reads these to score; they exist so the
            # compliance signal survives as its own quantity instead of being
            # destroyed by folding it into the score. `report_form` is
            # "conventional" whenever the strict parse succeeded, so a reader can
            # count non-compliance directly rather than inferring it.
            "rwa_loose": loose_value,
            "report_form": ("conventional" if parsed.rwa is not None
                            else "declined" if parsed.declined else loose_form),
            "loose_recovers": parsed.rwa is None and not parsed.declined
                              and loose_value is not None,
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
