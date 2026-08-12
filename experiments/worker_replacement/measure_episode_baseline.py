"""How long does a HEALTHY episode take?

Written because three runs were killed as "hung" at 10-20 minutes without anyone
ever measuring what a normal episode costs. The 18 committed R2 bundles answer it
and were sitting in the record the whole time.

Reads only committed bundles. Spends nothing. Run:

    python experiments/worker_replacement/measure_episode_baseline.py

Every number in records/L10/episode_baseline_v1.md comes from this file.
"""

from __future__ import annotations

import datetime as dt
import glob
import json
import statistics as st
from pathlib import Path

# ALL committed study bundles, not just R2 -- a first version globbed R2 only and silently
# excluded records/S8/, which RE caught. The two S8 bundles marked FAILED/INCOMPLETE are
# excluded deliberately: pricing a timeout on a run that never finished justifies a higher
# bound from a failure. That exclusion is stated here rather than left in a glob.
BUNDLE_GLOBS = ("experiments/worker_replacement/records/*/run_*.json",)
EXCLUDE = ("_FAILED", "_INCOMPLETE")

# The bounds installed 2026-08-08 while chasing the "hang" (ai_agent.py, CHANGED.md L11).
INSTALLED_BOUNDS = [("litellm.request_timeout", 180), ("WORKER_RUN_BACKSTOP_S", 630)]

# Their replacements, raised by RE at 8e273ec once the bounds were shown to sit inside
# the workload rather than above it.
REPLACEMENT_BOUNDS = [("raised request_timeout", 1200), ("raised backstop", 2460)]


def _ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def _events(path: str) -> list[dict]:
    ev = [e for e in (json.load(open(path)).get("events") or []) if e.get("timestamp")]
    return sorted(ev, key=lambda e: e["timestamp"])


def construction(paths: list[str]) -> dict:
    """A baseline only transfers if it was produced under the settings we are about to
    use. Report the settings rather than assuming them."""
    keys = {"manager_model", "worker_model", "horizon", "concurrency"}
    seen: dict[tuple, int] = {}
    for p in paths:
        m = json.load(open(p)).get("manifest", {})
        k = tuple(m.get(x) for x in sorted(keys))
        seen[k] = seen.get(k, 0) + 1
    return {"fields": sorted(keys), "settings": seen}


def episode_spans(paths: list[str]) -> list[float]:
    out = []
    for p in paths:
        ev = _events(p)
        if ev:
            out.append((_ts(ev[-1]["timestamp"]) - _ts(ev[0]["timestamp"])).total_seconds())
    return out


def quiet_gaps(paths: list[str]) -> list[float]:
    """Silence between consecutive logged events in an episode that SUCCEEDED.
    This is the number a hang detector has to clear."""
    out = []
    for p in paths:
        ev = _events(p)
        out += [(_ts(b["timestamp"]) - _ts(a["timestamp"])).total_seconds()
                for a, b in zip(ev, ev[1:])]
    return out


def _paired(paths: list[str], open_ev: str, close_evs: tuple[str, ...],
            key: tuple[str, ...], over: float = 180.0) -> tuple[list[float], int, int]:
    """Pair an opening event to its terminator on an EXACT correlation key.

    Returns (durations, episodes with a duration over `over`, unmatched events).
    `unmatched` must be 0 for the result to mean anything -- it is the check that the
    key really is a key, and it is printed rather than swallowed.

    Two earlier versions of this were wrong in opposite directions and BOTH are worth
    keeping in view, because each looked reasonable:

      * FIFO within an episode. Overlapping calls get paired to the wrong partner, one
        duration too long and its partner too short. RR measured the overlap: 2 of 18
        bundles for manager calls (up to 82% of calls in one), and -- far worse -- 18 of
        18 for worker runs, which is where the bound we were arguing about actually lives.
      * FIFO, then DROP the overlapping bundles (RR's remedy). It removes the bias but
        also removes those bundles' genuinely long calls, so it understates the tail:
        p99 438s against the exact 636s.

    Neither was needed. `structured_llm_*` carries (actor_id, operation, timestep) and
    `worker_execution_*` carries (actor_id, task_id); both pair all 18 bundles with zero
    unmatched and zero ambiguity. We had each concluded the events carried no correlation
    id WITHOUT LOOKING AT THE EVENT FIELDS.

    EVERY terminator must be listed. Omitting `structured_llm_error` let a pairing skip
    across it and report a 956s maximum that no single call ever took.
    """
    durs: list[float] = []
    episodes_over = 0
    unmatched = 0
    for p in paths:
        open_: dict[tuple, list[dt.datetime]] = {}
        longest = 0.0
        for e in _events(p):
            t = e.get("event_type")
            k = tuple(e.get(f) for f in key)
            if t == open_ev:
                open_.setdefault(k, []).append(_ts(e["timestamp"]))
            elif t in close_evs:
                if open_.get(k):
                    d = (_ts(e["timestamp"]) - open_[k].pop(0)).total_seconds()
                    durs.append(d)
                    longest = max(longest, d)
                else:
                    unmatched += 1
        unmatched += sum(len(v) for v in open_.values())
        episodes_over += longest > over
    return sorted(durs), episodes_over, unmatched


def manager_calls(paths: list[str]) -> tuple[list[float], int, int]:
    """MANAGER LLM calls. Every `structured_llm_*` event in this corpus carries
    actor_type == 'manager' -- there are no worker LLM-call events at all, so this
    population CANNOT speak to a bound on the worker path."""
    return _paired(paths, "structured_llm_request",
                   ("structured_llm_response", "structured_llm_error"),
                   key=("actor_id", "operation", "timestep"))


def worker_executions(paths: list[str]) -> tuple[list[float], int, int]:
    """WORKER runs -- the correct population for WORKER_REQUEST_TIMEOUT_S and
    WORKER_RUN_BACKSTOP_S, which wrap the worker's Runner.run and not the manager's."""
    return _paired(paths, "worker_execution_started",
                   ("worker_execution_completed", "worker_execution_failed"),
                   key=("actor_id", "task_id"))


def first_task_completion(paths: list[str]) -> tuple[list[float], int, int]:
    """Time to the first TASK finishing, and how often a task finishes inside timestep 0.

    Deliberately keyed to `worker_execution_completed`. A first pass used any event type
    containing "complet", which matches `timestep_completed` -- a timestep boundary that
    fires whether or not anything completed. That measured the wrong thing and would have
    answered RE's `completed=0 at t00` question with a number about something else.
    """
    firsts, inside_t0, n = [], 0, 0
    for p_ in paths:
        ev = _events(p_)
        if not ev:
            continue
        start = _ts(ev[0]["timestamp"])
        t0_end = next((_ts(e["timestamp"]) for e in ev
                       if e.get("event_type") == "timestep_completed"), None)
        done = [_ts(e["timestamp"]) for e in ev
                if e.get("event_type") == "worker_execution_completed"]
        if done:
            n += 1
            firsts.append((min(done) - start).total_seconds())
            if t0_end and min(done) < t0_end:
                inside_t0 += 1
    return firsts, inside_t0, n


def pct(sorted_vals: list[float], q: float) -> float:
    return sorted_vals[min(int(q * len(sorted_vals)), len(sorted_vals) - 1)]


def main() -> None:
    found = sorted(f for g in BUNDLE_GLOBS for f in glob.glob(g))
    paths = [f for f in found if not any(x in f for x in EXCLUDE)]
    if not paths:
        raise SystemExit(f"no bundles matched {BUNDLE_GLOBS!r} -- refusing an empty baseline")
    print(f"_{len(paths)} bundles; {len(found) - len(paths)} excluded as FAILED/INCOMPLETE_\n")

    print("# Episode baseline from the committed study bundles\n")

    con = construction(paths)
    print("## Construction (a baseline transfers only if these match the run you are about to do)")
    for settings, n in con["settings"].items():
        print(f"  {n:>2} bundles  {dict(zip(con['fields'], settings))}")

    spans = episode_spans(paths)
    print(f"\n## Episode wall-clock (n={len(spans)})")
    print(f"  median {st.median(spans)/60:.1f} min | mean {st.mean(spans)/60:.1f} min "
          f"| max {max(spans)/60:.1f} min | per timestep {st.mean(spans)/22:.0f}s at horizon 22")

    gaps = sorted(quiet_gaps(paths))
    print(f"\n## Silence between logged events, IN EPISODES THAT SUCCEEDED (n={len(gaps)})")
    print(f"  median {st.median(gaps):.0f}s | p90 {pct(gaps,.90):.0f}s "
          f"| p99 {pct(gaps,.99):.0f}s | max {max(gaps):.0f}s")
    print("  -> a multi-minute silence is ORDINARY; it is not evidence of a hang")

    for label, (calls, eps_over, unmatched) in (
        ("MANAGER LLM calls (WRONG population for a worker bound -- see docstring)",
         manager_calls(paths)),
        ("WORKER runs (the population the worker bounds actually govern)",
         worker_executions(paths)),
    ):
        if unmatched:
            raise SystemExit(f"{label}: {unmatched} unmatched events -- the key is not a key")
        print(f"\n## {label}, n={len(calls)}  [exact pairing, 0 unmatched]")
        print(f"  median {st.median(calls):.0f}s | p90 {pct(calls,.90):.0f}s "
              f"| p99 {pct(calls,.99):.0f}s | max {max(calls):.0f}s")
        for name, thr in INSTALLED_BOUNDS:
            over = [c for c in calls if c > thr]
            print(f"    {name:24s} = {thr:>4}s  kills {len(over):>3}/{len(calls)} "
                  f"({100*len(over)/len(calls):.1f}%) that FINISHED")
        for name, thr in REPLACEMENT_BOUNDS:
            over = [c for c in calls if c > thr]
            print(f"    {name:24s} = {thr:>4}s  kills {len(over):>3}/{len(calls)} "
                  f"({100*len(over)/len(calls):.1f}%) that FINISHED")
        print(f"    episodes with at least one over 180s: {eps_over}/{len(paths)}")

    firsts, inside_t0, nf = first_task_completion(paths)
    print(f"\n## First TASK completion (worker_execution_completed), n={nf}")
    print(f"  median {st.median(firsts)/60:.1f} min | mean {st.mean(firsts)/60:.1f} min "
          f"| max {max(firsts)/60:.1f} min")
    print(f"  episodes completing any task INSIDE timestep 0: {inside_t0}/{nf}")
    print(f"  -> 'completed=0 at t00' occurs in {nf - inside_t0}/{nf} healthy episodes: it is NORMAL")

    print("\n## Bounds implied by the measurement")
    print(f"  a request timeout must clear the healthy max ({max(calls):.0f}s) with margin")
    print(f"  a hang detector must clear the healthy max silence ({max(gaps):.0f}s) with margin")
    print(f"  an episode kill threshold must clear the healthy max episode "
          f"({max(spans)/60:.0f} min) with margin")


if __name__ == "__main__":
    main()
