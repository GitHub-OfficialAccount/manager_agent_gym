"""Where does the wall clock go, and does the turn cap touch the DV? Measured.

Written to settle two questions that had been answered from single instances:

  1. "a worker task averages 13 minutes"  -- quoted to the researcher. It is the mean
     of the SLOW TAIL, not of tasks. The corpus mean is 190s and the median is 81s.
     The 36-minute maximum quoted alongside it IS corpus-wide, so the two numbers
     came from two different populations and were presented as one description.

  2. "the turn cap is a random task-killer inside the normal distribution" -- the
     variance is real but the DEATHS are not random. They concentrate on aggregation
     tasks, and the split cannot read those tasks at all.

THE CLOSER SET, stated with the numbers because a duration is only as good as it:
a run is a `worker_execution_started` paired with the NEXT `worker_execution_completed`
OR `worker_execution_failed` on the same (actor_id, task_id). Dropping `failed` from
the closers is what produced a phantom 3343s run earlier in this project -- a failed
start was consumed by a later completion. `unmatched` must print 0 or the numbers are
void and this module says so rather than reporting them.

WHY TASK CLASS IS THE AXIS. The DV is per-segment: `split()` keys on
`index.segment_task_ids`, a segment_id -> task_id map, and the scorer scores a reported
RWA against that segment's truth. A task with no segment id cannot enter either. So
"does this cost the measurement or only the clock" is answerable by class membership,
and does not need a run.

Zero model calls. Run:

    .venv/bin/python -m experiments.worker_replacement.probe_runtime_by_task_class
"""

from __future__ import annotations

import collections
import datetime as dt
import glob
import json
import statistics as st
from typing import Any

SEGMENT_PREFIX = "Risk-weighted assets —"

#: Names seen in the corpus. The generator's current lists are in `finance_env`
#: (UPSTREAM_FIXED, UPSTREAM_OPEN, DOWNSTREAM); the corpus also holds manager-created
#: remediation tasks with free-form names, which is why the classifier falls through to
#: a MANAGER_CREATED bucket rather than asserting a closed set.
UPSTREAM = {
    "Scope and approval inventory", "Exposure data preparation",
    "Approval scope note", "Data quality checklist",
}
AGGREGATION_HINTS = ("aggregate", "output floor", "capital adequacy",
                     "reconcil", "attestation")


def classify(name: str) -> str:
    if name.startswith(SEGMENT_PREFIX):
        return "SEGMENT (the DV)"
    if name in UPSTREAM:
        return "UPSTREAM (prep)"
    low = name.lower()
    if any(h in low for h in AGGREGATION_HINTS):
        return "AGGREGATION"
    return "MANAGER_CREATED"


def _ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def runs() -> tuple[list[tuple[float, str, str, str]], int]:
    """(duration, class, task_name, outcome) plus the unmatched count."""
    out: list[tuple[float, str, str, str]] = []
    unmatched = 0
    for path in sorted(glob.glob("experiments/worker_replacement/records/*/run_*.json")):
        try:
            bundle: dict[str, Any] = json.load(open(path))
        except (json.JSONDecodeError, OSError):
            continue
        events = sorted((e for e in bundle.get("events") or [] if e.get("timestamp")),
                        key=lambda e: e["timestamp"])
        open_: dict[tuple, list[tuple[dt.datetime, str]]] = {}
        for e in events:
            key = (e.get("actor_id"), e.get("task_id"))
            kind = e.get("event_type")
            name = str(e.get("task_name") or "")
            if kind == "worker_execution_started":
                open_.setdefault(key, []).append((_ts(e["timestamp"]), name))
            elif kind in ("worker_execution_completed", "worker_execution_failed"):
                if open_.get(key):
                    t0, n0 = open_[key].pop(0)
                    err = (e.get("payload") or {}).get("error_type") or ""
                    outcome = "ok" if kind.endswith("completed") else (err or "failed")
                    out.append(((_ts(e["timestamp"]) - t0).total_seconds(),
                                classify(n0), n0, outcome))
                else:
                    unmatched += 1
        unmatched += sum(len(v) for v in open_.values())
    return out, unmatched


def _q(values: list[float], frac: float) -> float:
    s = sorted(values)
    return s[min(int(frac * len(s)), len(s) - 1)]


def main() -> int:
    rows, unmatched = runs()
    if not rows:
        raise SystemExit("no worker runs in the corpus -- refusing to report")
    if unmatched:
        raise SystemExit(f"{unmatched} unmatched start/close events -- pairing is not "
                         f"exact, so every duration below would be a guess. Refusing.")
    print(f"{len(rows)} worker runs, exact pairing, 0 unmatched\n")

    # ---- 1. THE NUMBER THAT WAS MISQUOTED, WITH ITS POPULATION --------------------
    d = [r[0] for r in rows]
    seg = [r[0] for r in rows if r[1] == "SEGMENT (the DV)"]
    print("## 1. A worker task, by population")
    print(f"  {'population':<22} {'n':>5} {'mean':>8} {'median':>8} {'p90':>8} {'max':>8}")
    for label, v in (("ALL runs", d), ("SEGMENT only", seg),
                     ("runs over 300s", [x for x in d if x > 300]),
                     ("runs over 600s", [x for x in d if x > 600])):
        print(f"  {label:<22} {len(v):>5} {st.mean(v):>7.0f}s {st.median(v):>7.0f}s "
              f"{_q(v, .9):>7.0f}s {max(v):>7.0f}s")
    print("\n  The 13-minute figure quoted to the researcher lies between the last two")
    print("  rows -- it describes the SLOW TAIL. The 36-minute maximum quoted with it")
    print("  is row 1. Two populations, presented as one description of a task.")

    # ---- 2. WHERE THE CLOCK GOES -------------------------------------------------
    tot: collections.Counter = collections.Counter()
    n: collections.Counter = collections.Counter()
    dead: collections.Counter = collections.Counter()
    for dur, cls, _name, outcome in rows:
        tot[cls] += dur
        n[cls] += 1
        if outcome != "ok":
            dead[cls] += 1
    grand = sum(tot.values())
    print(f"\n## 2. Wall clock by task class  (total {grand / 3600:.1f} h)")
    print(f"  {'class':<18} {'runs':>5} {'died':>5} {'hours':>7} {'mean':>7} {'share':>7}")
    for cls, _ in tot.most_common():
        print(f"  {cls:<18} {n[cls]:>5} {dead[cls]:>5} {tot[cls] / 3600:>6.2f}h "
              f"{tot[cls] / n[cls]:>6.0f}s {100 * tot[cls] / grand:>6.1f}%")

    # ---- 3. DOES THE TURN CAP TOUCH THE MEASUREMENT? -----------------------------
    print("\n## 3. Turn-cap deaths, by class and by task")
    caps = [r for r in rows if r[3] == "MaxTurnsExceeded"]
    by_cls: collections.Counter = collections.Counter(r[1] for r in caps)
    print(f"  {len(caps)} deaths of {len(rows)} runs ({100 * len(caps) / len(rows):.1f}%)")
    for cls, c in by_cls.most_common():
        started = n[cls]
        print(f"    {cls:<18} {c:>3} of {started:<4} ({100 * c / started:>4.1f}% of that class)")
    print(f"\n  {'task':<44} {'runs':>5} {'died':>5} {'rate':>7}")
    per_task_n: collections.Counter = collections.Counter(r[2] for r in rows)
    per_task_d: collections.Counter = collections.Counter(r[2] for r in caps)
    for name, count in sorted(per_task_n.items(), key=lambda kv: -per_task_d[kv[0]] / max(kv[1], 1)):
        if per_task_d[name]:
            print(f"  {name[:43]:<44} {count:>5} {per_task_d[name]:>5} "
                  f"{100 * per_task_d[name] / count:>6.1f}%")

    seg_caps = by_cls.get("SEGMENT (the DV)", 0)
    print(f"\n  ON THE DV: {seg_caps} of {n['SEGMENT (the DV)']} segment runs "
          f"({100 * seg_caps / n['SEGMENT (the DV)']:.1f}%).")
    print("  Everything else dies on tasks the split cannot read: it keys on")
    print("  `index.segment_task_ids`, and an aggregation task carries no segment id.")

    print("\n## What this does NOT establish")
    print("  Nothing about effect size, and nothing about whether a task SHOULD take")
    print("  259s. It says where the time goes and which deaths reach the measurement.")
    print("  The corpus spans several arrangements and two generator revisions, so the")
    print("  per-task rates mix populations; the class-level split does not depend on")
    print("  that mixing, the per-task table does.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
