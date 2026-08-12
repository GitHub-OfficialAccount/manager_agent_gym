"""Resolve every artifact a record cites, against the tree.

WHY THIS EXISTS. A record citing a script that was never committed is invisible by
construction: the reader sees a filename in backticks and stops, because the thing
you would check with is the thing that is absent. It surfaced when RR audited their
own work and found `step4_audit_RR.md` citing `step4_audit.py`, which had never
been committed -- and that is why the n=30 in its tables could not be reconstructed
and turned out to be 7 per group. The script that produced it no longer existed to
re-run. The rule this enforces:

    A RECORD CITING AN ARTIFACT ASSERTS THE ARTIFACT EXISTS, AND NOTHING CHECKS THAT.

It is mechanical, which is the point -- it is the one rule from this phase that does
not depend on anyone remembering it.

WHAT IT DOES NOT DO. It cannot tell "never existed" from "existed and was moved or
deleted". Both are worth surfacing and only a human can say which. Superseded
citations are silenced by annotating the citing record with the marker below,
beside the pointer to what replaced it -- so silencing one is a documented act, not
a config edit somewhere else.

    <!-- citation-check: superseded -->

A marker in the first four lines silences a whole document; a marker on or beside a
line silences only the citations there.

ONE CATEGORY TAKES THE MARKER BY DEFAULT, and it recurs by construction: A RECORD OF
A MISSING-ARTIFACT DEFECT MUST NAME THE MISSING ARTIFACT IN ORDER TO REPORT IT.
Writing down a broken citation creates a broken citation. This checker's own findings
-log entry broke this checker's own invariant within minutes of the run that reported
zero -- which is the shortest available demonstration that A CLEAN REPORT IS A
STATEMENT ABOUT A MOMENT, NOT A PROPERTY OF THE TREE. Such entries take the in-place
marker as standard form, not as a case-by-case exception to be adjudicated.

GUARDS, each answering a failure this project has actually had:
  - a POSITIVE CONTROL runs first: a citation known to be unresolvable must be
    flagged, or the checker reports nothing because it is looking in the wrong place
    (`check_announcement`'s alarm never fired for exactly that reason);
  - an EMPTY citation set RAISES rather than passing: `all([])` is True and would
    render "0 unresolved" as a pass for a scan that found nothing;
  - the INTERMEDIATE QUANTITIES print, not just the verdict -- how many records were
    read, how many citations found, how many resolved and by which route.

Run as a module, not pytest:
    python -m experiments.worker_replacement.check_record_citations
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SUPERSEDED = "<!-- citation-check: superseded -->"

# Backtick-quoted tokens ending in a source or data extension. Deliberately narrow:
# prose mentions a filename without backticks often enough that widening this would
# drown the signal, and a citation a reader would follow is one that is marked up.
# The optional `:lines` suffix is why this is not simply `...`: records cite
# `check_announcement.py:168-191` far more often than the bare name, and an earlier
# version of this regex required a backtick immediately after the extension -- so it
# silently skipped every line-ranged citation and reported a clean tree. Found by the
# L4 drift check, not by this checker.
CITATION = re.compile(r"`([A-Za-z0-9_./-]+\.(?:py|json|jsonl))(?::[0-9][^`]*)?`")

# Cited names that are not repository artifacts. Kept short and explicit; anything
# longer than this is a sign the pattern is too wide.
NOT_ARTIFACTS = {"__init__.py"}

# `archive/` is superseded BY DEFINITION -- every document in it carries a banner
# saying it governs nothing, and it records a state in which the artifacts it cites
# did exist. Silencing it is therefore already a documented act, done once here
# rather than 16 times in the files. Its count is REPORTED rather than suppressed,
# because "we stopped looking" and "there is nothing there" must not look the same.
ARCHIVE = "archive"


def records_and_docs(root: Path = HERE) -> list[Path]:
    """Every markdown file that can carry a citation, under `root`."""
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def index_tree() -> dict[str, list[Path]]:
    """basename -> every path with that basename, repo-wide."""
    by_name: dict[str, list[Path]] = {}
    for p in REPO.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            by_name.setdefault(p.name, []).append(p)
    return by_name


def resolve(cited: str, doc: Path, by_name: dict[str, list[Path]]) -> str | None:
    """Return the route that resolved this citation, or None.

    Routes are tried nearest-first, because a citation is read relative to where it
    sits before it is read as a repo path.
    """
    name = Path(cited).name
    for route, candidate in (
        ("beside the record", doc.parent / cited),
        ("experiment-relative", HERE / cited),
        ("repo-relative", REPO / cited),
    ):
        if candidate.is_file():
            return route
    if name in by_name:
        return f"basename elsewhere ({len(by_name[name])} match(es))"
    return None


def scan(by_name: dict[str, list[Path]], root: Path = HERE) -> dict[str, object]:
    """Resolve every citation, split LIVE from ARCHIVE.

    The split is the whole value of the report. Archive documents cite artifacts
    that existed when they were written and were deleted in the cleanup -- that is
    a fact about the archive, not a defect. A LIVE document citing a deleted file
    is a reader following a pointer to nothing.
    """
    live: list[tuple[Path, str]] = []
    archived: list[tuple[Path, str]] = []
    routes: dict[str, int] = {}
    # Counted separately on purpose. An earlier version of this function summed
    # ANNOTATED FILES and SILENCED CITATIONS into one number, which is the §B defect
    # -- two populations under one name -- in the tool written to enforce §E.
    files_total = 0
    files_annotated = 0
    citations_total = 0
    citations_silenced = 0

    for doc in records_and_docs(root):
        files_total += 1
        text = doc.read_text(encoding="utf-8", errors="replace")
        in_archive = ARCHIVE in doc.relative_to(root).parts
        lines = text.split("\n")

        # A LIVE document legitimately refers to deleted things in its own history --
        # the findings log names modules the cleanup removed, and that is the record
        # working. So the marker silences PER CITATION, on the line it appears or the
        # line either side, keeping the escape next to the claim it excuses rather
        # than in a config file nobody reads. A marker in the first three lines
        # silences the whole document, which is how a superseded record declares itself.
        whole_file = any(SUPERSEDED in ln for ln in lines[:4])
        if whole_file:
            files_annotated += 1
        silenced: set[str] = set()
        for i, line in enumerate(lines):
            if SUPERSEDED in line:
                silenced.update(CITATION.findall("\n".join(lines[max(0, i - 1): i + 2])))

        for cited in dict.fromkeys(CITATION.findall(text)):
            if Path(cited).name in NOT_ARTIFACTS or cited.startswith("/"):
                continue  # leading slash is a URL path, not a repo artifact
            citations_total += 1
            if whole_file or cited in silenced:
                citations_silenced += 1
                continue
            route = resolve(cited, doc, by_name)
            if route is None:
                (archived if in_archive else live).append((doc, cited))
            else:
                key = route.split(" (")[0]
                routes[key] = routes.get(key, 0) + 1

    return {"live": live, "archived": archived, "routes": routes,
            "files_total": files_total, "files_annotated": files_annotated,
            "citations_total": citations_total, "citations_silenced": citations_silenced}


def positive_control(by_name: dict[str, list[Path]]) -> None:
    """A citation that CANNOT resolve must be reported unresolvable.

    Without this the checker can report a clean tree because it is looking in the
    wrong place, which is how `check_announcement`'s alarm never fired.
    """
    fake = "step4_audit_this_was_never_committed.py"
    route = resolve(fake, HERE / "records" / "L9" / "probe.md", by_name)
    if route is not None:
        raise AssertionError(
            f"POSITIVE CONTROL FAILED: a citation that cannot exist resolved via {route!r}. "
            "The resolver is matching too loosely and a clean report would mean nothing."
        )
    real = "finance_scorer.py"
    if resolve(real, HERE / "records" / "L9" / "probe.md", by_name) is None:
        raise AssertionError(
            f"POSITIVE CONTROL FAILED: {real!r} exists and did not resolve. "
            "The resolver is matching too tightly and would report false unresolvables."
        )
    print("resolver control        PASS  (unresolvable flagged, real file resolved)")


def end_to_end_control(by_name: dict[str, list[Path]]) -> None:
    """The REPORT must come back non-zero on a tree that contains a bad citation.

    The resolver control above proves a COMPONENT works. It does not prove the
    verdict's own path does -- and the verdict is what the exit code asserts. RR
    caught exactly this gap in this file: a correctly-built positive control on the
    resolver, shipping a verdict whose own path was never shown able to fail.

        A CONTROL STATES THE OUTCOME OF ITS OWN NEGATIVE CASE, AND TRAVERSES THE
        SAME PATH AS THE REPORTED VERDICT -- NOT A COMPONENT OF IT.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "negative_case.md").write_text(
            "# negative case\n\nCites `there_is_no_such_module_xyzzy.py` deliberately.\n",
            encoding="utf-8",
        )
        bad = scan(by_name, root)
        if not bad["live"]:
            raise AssertionError(
                "END-TO-END CONTROL FAILED: a tree containing an unresolvable citation "
                "reported NO live unresolved. The verdict cannot fail, so its passing "
                "means nothing."
            )
        (root / "positive_case.md").write_text(
            "# positive case\n\nCites `finance_scorer.py`, which exists.\n",
            encoding="utf-8",
        )
        (root / "negative_case.md").unlink()
        good = scan(by_name, root)
        if good["live"]:
            raise AssertionError(
                f"END-TO-END CONTROL FAILED: a tree whose only citation resolves reported "
                f"{good['live']} as unresolved. The verdict cannot pass, so its failing "
                "means nothing either."
            )
    print("end-to-end control      PASS  (verdict returns non-zero on a bad tree, zero on a good one)")


def main() -> int:
    by_name = index_tree()
    positive_control(by_name)
    end_to_end_control(by_name)

    r = scan(by_name)
    live, archived = r["live"], r["archived"]
    total = r["citations_total"]

    print(f"markdown files scanned  {r['files_total']}  "
          f"({r['files_annotated']} declared superseded in their header)")
    print(f"citations found         {total}  "
          f"({r['citations_silenced']} silenced by an in-place marker)")
    for route, n in sorted(r["routes"].items()):
        print(f"  resolved: {route:<22} {n}")
    print(f"unresolved in archive/  {len(archived)}  (expected -- superseded by definition, "
          f"counted so 'stopped looking' cannot look like 'nothing there')")
    print(f"UNRESOLVED IN LIVE DOCS {len(live)}")

    # An empty citation set is not a pass. `all([])` is True and this is where that
    # would bite: a regex that stopped matching would report a clean tree.
    if total == 0:
        raise AssertionError(
            "NO CITATIONS FOUND AT ALL across "
            f"{r['files_total']} markdown files. That is not a pass -- the pattern has "
            "stopped matching, or the records moved. Refusing to report clean."
        )

    if live:
        print()
        print("Each line is a LIVE record asserting an artifact that is not in the tree.")
        print(f"If the citation is superseded, annotate the record with {SUPERSEDED}")
        print("beside a pointer to what replaced it -- silencing one is a documented act.")
        print()
        for doc, cited in live:
            print(f"  {doc.relative_to(REPO)}  ->  `{cited}`")
        return 1

    print("\nPASS -- every artifact cited by a live record resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
