"""Does each committed record still MATCH the code that produced it?

`check_record_citations` verifies a record CITES a script. Nothing verified that
the record still matches what that script now emits — so a figure can be quoted,
the code beneath it can change, and the record keeps asserting the old number with
nothing indicating it is stale.

THIS IS A DIFFERENT SHAPE FROM THE STALE MARKERS WE HAVE BEEN FINDING. Those were
a marker asserting a superseded STATE; this is a stale VALUE asserting a number the
code no longer produces. The bundle manifest solved it for runs by carrying its own
provenance. Offline records carry the script's NAME and not its BEHAVIOUR.

CAUGHT IT: today's generator fixes — the amplifier separation, the `others`
-exclusion bug, the divergence rng stream and the positional-roles change — all
alter which instance a seed produces, so every offline record generated before them
describes a generator that no longer exists.

    template              committed   regenerated
    current                   0.85%       1.08%
    proposed_disjoint         9.57%       9.84%
    partial_overlap           0.00%       0.00%

NORMALISATION, DECLARED. Some records legitimately differ every run: UUIDs are
regenerated per workflow and timestamps are wall clock. Those are normalised out
before comparison, so a report of "stale" is a real value change and not churn. Any
normalisation is a hole in the check, and these two are the ones taken.

HOW IT RESTORES, AND WHY THAT IS HOSTILE TO UNCOMMITTED EDITS. A record-producing
module writes to its fixed path, so the check runs it, compares against
`git show HEAD:<path>`, and restores the committed version with `git checkout`.

That makes it safe to run casually on a clean tree and DESTRUCTIVE to uncommitted
edits of the records it inspects. It ate mine: I annotated four records with their
superseded values, ran this to confirm it passed, and it reverted every annotation
and then reported 0 STALE -- a green result produced by discarding the work it was
checking. Commit record edits BEFORE running this. Not fixed, because the restore
is what makes the check safe to run at all; documented instead.

Run:  python3 -m experiments.worker_replacement.check_record_freshness
      python3 -m experiments.worker_replacement.check_record_freshness --regenerate
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

# Module -> the record paths it writes, relative to the repo root. Declared rather
# than discovered: a scan that guessed wrong would report a clean record stale, and
# an explicit table is checkable by reading it.
PRODUCERS: dict[str, tuple[str, ...]] = {
    "check_template_pricing": ("experiments/worker_replacement/records/L9/template_pricing.json",),
    "check_lattice_enumeration": ("experiments/worker_replacement/records/L9/lattice_enumeration.json",),
    "check_card_belief_model": ("experiments/worker_replacement/records/L9/card_belief_model.json",),
    "check_tie_rate": ("experiments/worker_replacement/records/L9/tie_rate.json",),
    "check_native_lattices": ("experiments/worker_replacement/records/L9/native_lattices.json",),
    "check_amplifier_dependence": ("experiments/worker_replacement/records/L9/amplifier_dependence.json",),
    "check_inversion": ("experiments/worker_replacement/records/L9/inversion_diagnosis.json",),
    "check_path_alignment": ("experiments/worker_replacement/records/L9/path_alignment.json",),
    "check_card_ceiling": ("experiments/worker_replacement/records/L4/card_ceiling.json",),
    "check_reliability_ceiling": ("experiments/worker_replacement/records/L4/reliability_ceiling.json",),
    "check_quantity_kinds": ("experiments/worker_replacement/records/L6/quantity_kinds.json",),
    "check_load_feedback": (
        "experiments/worker_replacement/records/L1/rendered_cell0_timestep0.txt",
    ),
    # ADDED 2026-08-09, and it was found by ABSENCE rather than by failure. Three
    # records regenerated as a side effect of running the L14 acceptances; two were
    # already listed here and reported STALE, and this one changed silently because
    # nothing was watching it. An unchecked record is a decision; an unchecked
    # record nobody has named is an accident waiting to be quoted (LS).
    #
    # NOTE ON THE PRODUCER: `test_finance_scorer` writes this as a SIDE EFFECT of
    # an acceptance run -- it is not a record-producing module in the sense the
    # rest of this table means. Listed anyway, because what matters here is whether
    # the file still matches the code, not how tidily it is produced.
    "test_finance_scorer": (
        "experiments/worker_replacement/records/S4/instance_seed101_8seg.json",
    ),
}

_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?")


# Keys that are PROVENANCE ABOUT the record rather than output OF it. A
# `superseded_*` block records what the file asserted before a regeneration; the
# producer does not emit it and never will, so without this every annotated record
# would report STALE forever -- and the annotation exists precisely because the
# record was regenerated. I created that conflict by annotating, and this is the
# narrower of the two fixes: the alternative is teaching four producers to emit
# their own history, which makes the computation responsible for its own archive.
#
# IT IS A HOLE AND IT IS NAMED: a value hidden inside a `superseded_*` block is
# not checked. That is acceptable only because nothing reads those blocks to
# compute anything -- they exist to be read by a person meeting an old figure.
_ANNOTATION_KEYS = ("superseded_",)


def strip_annotations(text: str) -> str:
    """Drop provenance-about-the-record keys before comparing."""
    try:
        data = json.loads(text)
    except Exception:
        return text
    if isinstance(data, dict):
        data = {k: v for k, v in data.items()
                if not any(k.startswith(p) for p in _ANNOTATION_KEYS)}
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def normalise(text: str) -> str:
    """Strip what legitimately varies per run. Every substitution here is a HOLE."""
    text = strip_annotations(text)
    text = _UUID.sub("<UUID>", text)
    return _ISO.sub("<TIMESTAMP>", text)


def carry_annotations(before: str, after: str) -> tuple[str, list[str]]:
    """Copy `superseded_*` blocks from the COMMITTED text into a regenerated one.

    ★ THE HOLE I NAMED WAS WORSE THAN I NAMED IT (LS, 2026-08-10). I wrote that a
    value inside a `superseded_*` block "is not checked". It is not merely
    unchecked -- it is DELETED by the routine regeneration this check exists to
    prompt, and every check we have goes green afterwards. `L4/card_ceiling.json`
    regenerated as +0/-478: zero value change, and all 478 deleted lines were the
    preserved prior values and the notes explaining what superseded them.

    A value-neutral, history-destroying edit is the worst shape a regeneration can
    have, because nothing downstream can distinguish it from a no-op.

    THE FIX IS ON THE WRITE PATH, NOT THE COMPARISON. Excluding `superseded_*` from
    the comparison is still right -- the producer does not emit it, so an annotated
    record would otherwise report STALE forever. What was missing is that
    `--regenerate` must CARRY the annotation across rather than let the producer's
    output silently drop it. The producer stays ignorant of its own archive.

    Returns the merged text and the keys carried, so the run can report them
    instead of doing it invisibly.
    """
    try:
        old, new = json.loads(before), json.loads(after)
    except Exception:
        return after, []
    if not isinstance(old, dict) or not isinstance(new, dict):
        return after, []
    carried = sorted(k for k in old
                     if any(k.startswith(p) for p in _ANNOTATION_KEYS)
                     and k not in new)
    if not carried:
        return after, []
    merged = {**new, **{k: old[k] for k in carried}}
    return json.dumps(merged, indent=2, sort_keys=True) + "\n", carried


def committed(path: str) -> str | None:
    out = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=REPO,
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def restore(path: str) -> None:
    subprocess.run(["git", "checkout", "--", path], cwd=REPO, capture_output=True)


def dirty_records() -> list[str]:
    """Tracked record paths with uncommitted changes.

    THE GUARD THAT TURNS A DOCUMENTED TRAP INTO AN UNREACHABLE ONE (LS). The
    restore below is `git checkout`, so running this over uncommitted edits
    DESTROYS them and then reports on what is left. It ate my first annotation
    attempt and reported 0 STALE -- a green result produced by discarding the work
    it was checking.
    
    I caught that one only because 0 was impossible given what I thought HEAD held.
    NEXT TIME THE ARITHMETIC MAY NOT BE IMPOSSIBLE, AND THEN IT IS JUST A GREEN.
    Documenting the trap leaves it reachable; refusing to run does not.

    AGAINST `HEAD`, NOT THE INDEX (L14-i, 2026-08-10). This ran
    `git diff --name-only`, which reports UNSTAGED changes only, so a record edit
    that was `git add`-ed but not committed passed the guard.

    It was never destructive -- `git checkout -- path` restores from the INDEX, so
    staged content survives. The failure was a FALSE STALE: the comparison below
    reads `git show HEAD:<path>`, so a staged-but-uncommitted record was compared
    against the previous commit and reported as asserting a number the code no
    longer produces, when in fact the record had already been updated.

    Adding `HEAD` is strictly more inclusive and cannot lose data. I flagged this
    rather than fixing it, on the general principle of not widening a guard the day
    before a run; LS's counter is the correct one -- that principle does not apply
    to a change that only ever catches MORE and destroys nothing, and a
    false-positive path is exactly the confusing signal to not carry into a run.
    """
    paths = [p for ps in PRODUCERS.values() for p in ps]
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--"] + paths,
                         cwd=REPO, capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def main() -> int:
    regenerate = "--regenerate" in sys.argv
    dirty = dirty_records()
    if dirty and not regenerate:
        print("REFUSING TO RUN: these records have uncommitted changes, and this "
              "check RESTORES them with `git checkout`:\n")
        for path in dirty:
            print(f"    {path}")
        print("\nCommit or stash them first. The restore is what makes this safe "
              "to run casually;\nrunning it over uncommitted work is what is not.")
        return 2
    print("Record freshness — does each record still match the code that wrote it?")
    print("normalised: UUIDs, timestamps. Anything else differing is a VALUE change.\n")

    stale: list[dict] = []
    annotations_carried: list[dict] = []
    checked = missing = 0
    print(f"{'module':<30}{'record':<44}{'verdict':>10}")
    for module, paths in sorted(PRODUCERS.items()):
        run = subprocess.run([sys.executable, "-m",
                              f"experiments.worker_replacement.{module}"],
                             cwd=REPO, capture_output=True, text=True)
        for path in paths:
            before = committed(path)
            if before is None:
                print(f"{module:<30}{path.split('/')[-1]:<44}{'UNTRACKED':>10}")
                missing += 1
                continue
            actual = (REPO / path)
            after = actual.read_text() if actual.exists() else ""
            # CARRY THE ANNOTATION BEFORE ANYTHING ELSE LOOKS AT THE FILE. Only in
            # --regenerate, because that is the only mode that leaves the new file
            # in the tree; without it the restore below puts the committed version
            # back anyway.
            if regenerate and after:
                after, carried = carry_annotations(before, after)
                if carried:
                    actual.write_text(after)
                    annotations_carried.append({"record": path, "keys": carried})
            checked += 1
            if normalise(before) == normalise(after):
                print(f"{module:<30}{path.split('/')[-1]:<44}{'fresh':>10}")
            else:
                print(f"{module:<30}{path.split('/')[-1]:<44}{'STALE':>10}")
                stale.append({"module": module, "record": path,
                              "producer_exit": run.returncode})
            if not regenerate:
                restore(path)

    print(f"\n  {checked} records checked, {len(stale)} STALE, {missing} untracked")
    if stale:
        print("  A STALE record asserts a number the code no longer produces.")
        for s in stale:
            print(f"    {s['record']}")
    if regenerate:
        print("\n  --regenerate: the regenerated files are LEFT IN THE TREE for commit.")
        if annotations_carried:
            print("  RETRACTION HISTORY CARRIED ACROSS (the producer does not emit it):")
            for row in annotations_carried:
                print(f"    {row['record']}: {', '.join(row['keys'])}")
        else:
            print("  no `superseded_*` blocks needed carrying — if you expected "
                  "some, that is a finding,\n  not a pass: check the record still "
                  "has them.")
    else:
        print("\n  tree restored; run with --regenerate to keep the new outputs")

    out = HERE / "records" / "L13"
    out.mkdir(parents=True, exist_ok=True)
    (out / "record_freshness.json").write_text(json.dumps({
        "checked": checked, "stale": stale, "untracked": missing,
        "normalised": ["UUID", "ISO timestamp", "superseded_* annotation blocks"],
        "annotations_carried": annotations_carried,
        "caveats": [
            "PRODUCERS is a DECLARED table, not a scan. A record produced by a "
            "module not listed here is NOT checked, and its absence is silent.",
            "each normalisation is a hole: a value that differs only inside a "
            "UUID or timestamp cannot be detected",
            "this checks that a record MATCHES its producer, not that either is "
            "correct",
            "`superseded_*` blocks are excluded from the comparison: they are "
            "provenance ABOUT the record that the producer does not emit. A value "
            "inside one is therefore NOT checked -- but as of 2026-08-10 it is at "
            "least PRESERVED: --regenerate carries existing blocks across, because "
            "before that a regeneration deleted them value-neutrally and every "
            "check went green afterwards (L4/card_ceiling.json, +0/-478).",
        ],
    }, indent=2, sort_keys=True) + "\n")
    print(f"  written: {out / 'record_freshness.json'}")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
