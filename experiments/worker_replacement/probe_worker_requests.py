"""L16 — where does a worker task's time actually go? Requests, turns, and gaps.

THE QUESTION, from the researcher: a segment task takes 13 minutes when it should
take under two. One episode split cleanly — 8 tasks at a 1.6 min median, 7 tasks at
a 24.5 min median, same work, and the 36-minute one produced a correct answer.

WHY THIS CANNOT BE ANSWERED FROM A BUNDLE, which is unusual for us and is the
reason this script exists at all: THE WORKER PATH EMITS NO PER-REQUEST EVENTS.
Every `structured_llm_*` in every bundle is the MANAGER's. So no committed artefact
prices a worker request, and the corpus-first rule has nothing to work with.

WHAT IT MEASURES, and it is deliberately three things rather than one:

  1. REQUESTS PER RUN — the turn count. Never observed before. Messages are the
     only turns visible in a bundle and they do NOT track the slow runs (a 29.8 min
     task sent zero messages; a 2.9 min task sent four), so if there is a loop it is
     thinking rather than messaging and only this number settles it.
  2. PER-REQUEST DURATION — one long call, or many short ones.
  3. THE GAPS BETWEEN REQUESTS — time inside the run that is NOT in a request:
     tool execution, retry backoff, SDK overhead. Without this, "the requests only
     account for 90 s of a 600 s run" is invisible and the other 510 s gets silently
     attributed to the provider.

INSTRUMENT SCOPE, STATED BECAUSE IT IS THE FAILURE MODE HERE. This registers a
`litellm.CustomLogger` and touches NOTHING in `ai_agent.py`. An instrument that
changes the timing it reports would be worthless when the fast population's whole
cost is 1.6 minutes. Runs measured with it should be cited as "<commit> + probe",
never as the bare commit.

WHAT IT DOES NOT ESTABLISH. It runs tasks in isolation, so it cannot reproduce
whatever contention an episode creates; and it measures the CLIENT's view of a
request, so provider-side queuing appears as request duration and is not separable
from generation. Both are named rather than corrected — separating them needs
provider telemetry we do not have.

Run:  python3 -m experiments.worker_replacement.probe_worker_requests [--trials N]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics as st
import time
from pathlib import Path
from typing import Any

from . import finance_report_parser as rp

HERE = Path(__file__).resolve().parent

_REQUESTS: list[dict[str, Any]] = []


def _install_probe() -> None:
    """Register a per-request logger. Provider layer only."""
    import litellm
    from litellm.integrations.custom_logger import CustomLogger

    class _RequestProbe(CustomLogger):
        def _record(self, kwargs, response_obj, start_time, end_time, ok: bool):
            usage = {}
            try:
                usage = dict(getattr(response_obj, "usage", None) or {})
            except Exception:
                pass
            _REQUESTS.append({
                "ok": ok,
                "start": start_time.timestamp() if start_time else None,
                "end": end_time.timestamp() if end_time else None,
                "seconds": ((end_time - start_time).total_seconds()
                            if start_time and end_time else None),
                "model": kwargs.get("model"),
                "usage": usage,
            })

        def log_success_event(self, kwargs, response_obj, start_time, end_time):
            self._record(kwargs, response_obj, start_time, end_time, True)

        def log_failure_event(self, kwargs, response_obj, start_time, end_time):
            self._record(kwargs, response_obj, start_time, end_time, False)

        async def async_log_success_event(self, kwargs, response_obj, start_time,
                                          end_time):
            self._record(kwargs, response_obj, start_time, end_time, True)

        async def async_log_failure_event(self, kwargs, response_obj, start_time,
                                          end_time):
            self._record(kwargs, response_obj, start_time, end_time, False)

    litellm.callbacks = [*(litellm.callbacks or []), _RequestProbe()]


async def _seed_inbox(service, worker_id: str) -> None:
    """Put a real message in the worker's inbox before it runs.

    ★ THE PROBE'S OWN BLIND SPOT, CLOSED (LS). Runs measured in isolation use an
    EMPTY `CommunicationService`, so `get_recent_messages` returns nothing and a
    worker cannot spend turns reading or answering. "Four turns" measured that way
    is therefore the turn count of a worker that CANNOT be interrupted -- which is
    not the configuration a study episode runs, and cell 3 makes the ask channel
    the manipulation itself.

    So this is not decoration: without it the probe answers a slightly different
    question from the one asked, and would have under-reported turns by however
    much messaging costs.
    """
    from manager_agent_gym.schemas.core.communication import MessageType

    await service.send_direct_message(
        from_agent="structured_manager",
        to_agent=worker_id,
        content=("Quick check before you file this one: are you approved to use the "
                 "IRB model for this segment's asset class, or will you be falling "
                 "back to the standardised approach?"),
        message_type=MessageType.REQUEST,
    )


def _build_worker_and_tasks(seed: int, cell: str = "1", with_message: bool = False):
    from manager_agent_gym.core.communication.service import CommunicationService
    from manager_agent_gym.core.workflow_agents.tool_factory import ToolFactory

    from . import finance_cells as fc
    from . import finance_env as env

    built = fc.build_cell_environment(seed, cell, **fc.shipped_setting())
    instance, workflow = built["instance"], built["workflow"]
    fc.assert_matches_selection(seed, instance)

    segments = [t for t in workflow.tasks.values()
                if env.CapacityBoundedAIAgent.is_metered(t)]
    successor = instance["event"]["successor_id"]
    config = built["team"][successor]
    # EXACTLY THE TOOLS THE REGISTRY GIVES A WORKER, not ToolFactory.create_ai_tools().
    # Checking the wrong path is how the duplicate-tool question got answered wrong
    # once already: `create_ai_tools()` returns five ANALYSIS tools that no worker on
    # the study path ever receives.
    service = CommunicationService()
    tools = ToolFactory.add_communication_tools([], service, config.agent_id)
    worker = env.CapacityBoundedAIAgent(config=config, tools=tools)
    # The agent reads its inbox through the SERVICE the tools were bound to, so the
    # worker must hold the same instance or a seeded message is invisible to it.
    worker.communication_service = service
    return worker, segments, instance, service


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cell", type=str, default="1")
    parser.add_argument("--with-message", action="store_true",
                        help="seed the worker's inbox before each task, so turns "
                             "spent reading/answering are counted. Isolation "
                             "under-reports turns for cell 3 by construction.")
    parser.add_argument("--trials", type=int, default=3,
                        help="worker tasks to run. Minutes, not hours.")
    parser.add_argument("--out", type=Path, default=HERE / "records" / "L16")
    args = parser.parse_args()

    # THE RUNNER DOES THIS AND THE FIRST VERSION OF THIS PROBE DID NOT. Without it
    # the Agents SDK POSTs traces to platform.openai.com using an OpenRouter key and
    # every run emits a 401. It recorded 0 failed MODEL requests, so the measurement
    # survived -- but an unexplained 401 in the output of a timing probe is exactly
    # the thing that makes a reader distrust the number, and it costs latency we are
    # trying to measure.
    from manager_agent_gym.core.common.model_provider import (
        disable_agents_tracing_if_proxied)

    disable_agents_tracing_if_proxied()
    _install_probe()
    worker, segments, _, service = _build_worker_and_tasks(
        args.seed, args.cell, args.with_message)
    tool_names = [getattr(t, "name", "?") for t in worker.tools]

    print(f"L16 worker request probe — seed {args.seed}, cell {args.cell}")
    print(f"  worker {worker.config.agent_id}  max_turns={worker.config.max_turns}")
    print(f"  tools ({len(tool_names)}): {tool_names}")
    print(f"  duplicates dropped: "
          f"{getattr(worker, '_duplicate_tools_dropped', 'n/a')}")
    print(f"  trials: {args.trials}\n")

    runs = []
    for i in range(min(args.trials, len(segments))):
        task = segments[i]
        before = len(_REQUESTS)
        wall_start = time.time()
        error = None
        result = None
        if args.with_message:
            await _seed_inbox(service, worker.config.agent_id)
        try:
            result = await worker.execute_task(task, [])
        except Exception as exc:  # a failure is data, not a crash
            error = f"{type(exc).__name__}: {exc}"
        wall = time.time() - wall_start
        mine = _REQUESTS[before:]
        durations = [r["seconds"] for r in mine if r["seconds"] is not None]
        in_requests = sum(durations)
        # ★ DID IT ANSWER, OR WAS IT CUT OFF? (L16b). One task used EXACTLY
        # max_turns=16 and reported no error, and the probe threw the result away --
        # so "used 16 turns and answered" was indistinguishable from "was truncated
        # at 16". That is the difference between a COST finding and a VALIDITY one,
        # and it cannot be settled from the turn count alone.
        #
        # The test is the study's own parser, not a length heuristic: a report that
        # yields an rwa value is a report the run can score. Anything else is
        # degraded output however long it is.
        text = ""
        for attr in ("output", "content", "result", "execution_notes"):
            value = getattr(result, attr, None)
            if isinstance(value, str) and value:
                text = value
                break
        if not text and result is not None:
            for res in (getattr(result, "output_resources", None) or []):
                value = getattr(res, "content", None)
                if isinstance(value, str) and value:
                    text = value
                    break
        parsed = None
        declined = False
        parse_reason = None
        if text:
            try:
                report = rp.parse_report(text)
                parsed, declined, parse_reason = (
                    report.rwa, report.declined, report.reason)
            except Exception as exc:
                parse_reason = f"{type(exc).__name__}: {exc}"

        row = {
            # A DECLINE COUNTS AS ANSWERED. "rwa: unavailable" in the agreed
            # form is a judgement the study records as an outcome, not a failure
            # to produce one -- conflating it with an unreadable deliverable is
            # exactly the distinction `declined` exists to keep.
            "answered": parsed is not None or declined,
            "rwa": parsed,
            "declined": declined,
            "parse_reason": parse_reason,
            "output_chars": len(text),
            "hit_turn_cap": len(mine) >= (worker.config.max_turns or 10**9),
            "task": task.name,
            "wall_s": round(wall, 2),
            "requests": len(mine),
            "in_requests_s": round(in_requests, 2),
            "outside_requests_s": round(wall - in_requests, 2),
            "longest_request_s": round(max(durations), 2) if durations else None,
            "median_request_s": round(st.median(durations), 2) if durations else None,
            "failed_requests": sum(1 for r in mine if not r["ok"]),
            "error": error,
        }
        runs.append(row)
        print(f"  [{i + 1}] {task.name[:30]:<30} wall {row['wall_s']:>7.2f}s  "
              f"req {row['requests']:>3}"
              f"{' [AT CAP]' if row['hit_turn_cap'] else '        '}  "
              f"answered={'YES' if row['answered'] else 'NO '}  "
              f"chars {row['output_chars']:>5}"
              + (f"  ERROR {error[:34]}" if error else ""))

    ok = [r for r in runs if not r["error"]]
    print("\nSUMMARY — the BASELINE first, because without it slow and stopped are "
          "the same observation:")
    if ok:
        print(f"  completed {len(ok)}/{len(runs)}  wall median "
              f"{st.median([r['wall_s'] for r in ok]):.2f}s  "
              f"turns median {st.median([r['requests'] for r in ok]):.1f}  "
              f"turns max {max(r['requests'] for r in ok)}")
        print(f"  time INSIDE requests: "
              f"{sum(r['in_requests_s'] for r in ok) / sum(r['wall_s'] for r in ok):.1%}"
              f" of wall clock")
    else:
        print("  no run completed — report that, do not summarise it away")

    args.out.mkdir(parents=True, exist_ok=True)
    suffix = "_withmsg" if args.with_message else ""
    path = args.out / f"request_probe_seed{args.seed}_cell{args.cell}{suffix}.json"
    path.write_text(json.dumps({
        "seed": args.seed, "cell": args.cell,
        "inbox_seeded": bool(args.with_message),
        "max_turns": worker.config.max_turns,
        "tools": tool_names,
        "runs": runs,
        "does_not_establish": [
            "tasks run in ISOLATION, so episode contention is not reproduced",
            "request duration is the CLIENT's view: provider-side queuing is "
            "included in it and is not separable from generation",
            "measured with the probe registered — cite as '<commit> + probe'",
        ],
    }, indent=2) + "\n")
    print(f"\n  written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
