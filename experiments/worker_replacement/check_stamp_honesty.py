"""Was the v3 instance stamp honest when it was written? Computed, not asserted.

`environment_selection_v3.json` carries `instance_sha256` per chosen instance, and its
value depends entirely on one condition: THE GENERATOR MUST NOT HAVE MOVED between the
commit that recorded the approved draw (v2) and the commit that stamped it (v3).

If it had moved, the stamp would record the CURRENT generator's output under the name of
an EARLIER approval -- fabricating provenance rather than recording it -- and nothing in
the file could tell the two cases apart afterwards. The stamp looks identical either way.

That condition was checked by hand before stamping and then written into the record as a
sentence (`stamp_is_honest_because`). RE pointed out it had no artefact of its own. A
label asserting a design principle over a condition nobody computes is the exact shape
this phase has been spent removing -- six-plus instances -- so here it is as the
condition.

IT IS A FIXED HISTORICAL FACT. Both commits are in the past; this answer cannot change,
which is what makes it worth having as a check rather than a comment.

Zero model calls. Run:

    .venv/bin/python -m experiments.worker_replacement.check_stamp_honesty
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
V2 = "experiments/worker_replacement/records/L10/environment_selection_v2.json"
V3 = "experiments/worker_replacement/records/L10/environment_selection_v3.json"

#: Everything the stamp's value depends on. `finance_generator` produces the instance;
#: `instance_hash` (in `finance_env`) serialises it. A change to either moves the stamp.
GENERATOR_PATHS = ["experiments/worker_replacement/finance_generator.py"]
HASH_PATH = "experiments/worker_replacement/finance_env.py"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, check=False).stdout


def _first_commit_touching(path: str) -> str | None:
    """The commit that INTRODUCED the file -- the oldest, not the newest."""
    out = _git("log", "--diff-filter=A", "--format=%H", "--", path).split()
    return out[-1] if out else None


def main() -> int:
    v2_commit = _first_commit_touching(V2)
    v3_commit = _first_commit_touching(V3)
    if not v2_commit or not v3_commit:
        raise SystemExit(
            f"cannot locate both selection records in history "
            f"(v2={v2_commit!r}, v3={v3_commit!r}) -- refusing to report a verdict on "
            f"a window this check cannot see"
        )

    print(f"v2 recorded at {v2_commit[:9]}")
    print(f"v3 stamped  at {v3_commit[:9]}\n")

    failures = []
    for path in GENERATOR_PATHS + [HASH_PATH]:
        commits = _git("log", "--format=%H %s", f"{v2_commit}..{v3_commit}~1",
                       "--", path).strip().splitlines()
        # `finance_env.py` legitimately changes for reasons unrelated to hashing (the
        # tool dedup did). Only a change to `instance_hash` itself moves the stamp, so
        # that file is judged on the FUNCTION, not the file.
        if path == HASH_PATH and commits:
            diff = _git("diff", f"{v2_commit}..{v3_commit}~1", "--", path)
            touched = "instance_hash" in diff
            status = "TOUCHES instance_hash" if touched else "changed, but not instance_hash"
            print(f"  {path}: {len(commits)} commit(s) -- {status}")
            for c in commits:
                print(f"      {c[:80]}")
            if touched:
                failures.append(f"{path}: instance_hash changed inside the stamp window")
            continue
        print(f"  {path}: {len(commits)} commit(s) in the stamp window")
        for c in commits:
            print(f"      {c[:80]}")
        if commits:
            failures.append(f"{path}: changed between the approved draw and the stamp")

    # The stamp must also still describe the CURRENT generator, or it is a record of a
    # past state rather than a guard on the present one. This part CAN change, and when
    # it does the answer is the researcher, not a re-stamp.
    print()
    stamped = json.loads((REPO / V3).read_text())["chosen"]
    from . import finance_env as env
    from . import finance_generator as gen
    from .check_l10_properties import SHIPPED
    drifted = []
    for row in stamped:
        now = env.instance_hash(gen.generate(row["seed"], **SHIPPED))
        ok = now == row["instance_sha256"]
        print(f"  seed {row['seed']:>3}  stamp {'matches' if ok else 'DIFFERS FROM'} "
              f"the generator as it stands today")
        if not ok:
            drifted.append(row["seed"])

    print()
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        print("\n  THE STAMP IS NOT HONEST. It was written after the generator moved, so")
        print("  it records the current generator's output under an earlier approval.")
        return 1
    print("  HONEST: the generator did not move between the approved draw and the stamp,")
    print("  so the stamped hashes are the ones the approval was made against.")
    if drifted:
        print(f"\n  BUT THE GENERATOR HAS MOVED SINCE: seeds {drifted} no longer hash to")
        print("  their stamp. The stamp is still an honest record of the approval; the")
        print("  RUNTIME no longer matches it. That is the researcher's call, not a")
        print("  re-stamp -- re-stamping would erase the evidence that anything moved.")
        return 2
    print("  And it still matches the generator as it stands, so the guard is live.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
