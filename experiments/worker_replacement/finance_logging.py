"""S9 — the four study-wide logging records, the denominator, and the deferral log.

Everything here READS a committed run bundle. Nothing re-runs an episode and
nothing calls a model. Each record exists because a specific claim is
unrecoverable without it (STUDY1_LOGGING_AND_ORDERING.md §2), so each extractor
returns the fields that claim needs and says when they are absent rather than
defaulting them away.

THE RULE THAT SHAPES ALL FOUR: assert on RENDERED TEXT AND EFFECTIVE VALUES,
never on generating parameters (spec §4.4). A parameter says what was intended;
the rendered text is what the agent actually saw, and only the second supports a
claim about what could have been consumed.

RECORD 1  target's channel pulls        — timestep, agent, task, call index
RECORD 2  refine events                 — timestep, task, BEFORE/AFTER description
RECORD 3  message -> manager visibility — message id, sender, addressee as written,
                                          timestep, and whether it entered the
                                          manager's RENDERED window
RECORD 4  ask-reply addressing          — reply id, to_agent as written, whether it
                                          names the manager

Record 3's window field is the one that is easy to get wrong. `recent_messages` is
`get_all_messages()[:message_window]`, so entry into the window is a property of
TRAFFIC VOLUME, not of the message: a message can be correctly addressed,
delivered, and still never rendered. "The manager could have consumed it" is a
claim about the window, not about the addressing.
"""

from __future__ import annotations

from typing import Any

# CHANNEL PULLS are the tools through which an agent ACQUIRES information it was
# not given. Sends are separated out: a push is not a pull, and record 1 exists to
# split P2 before/after the target has READ something.
#
# THESE NAMES WERE WRONG THE FIRST TIME, and the way they were wrong is the reason
# `live_tool_names()` exists below. The first version guessed plausible names
# (`send_direct_message`, `read_messages`) that no tool actually has. The extractor
# then reported ZERO pulls on a bundle containing 32 real tool calls — and zero
# pulls is indistinguishable from "the target never pulled", which is a finding.
# A wrong list does not fail; it quietly answers the research question with a
# default.
PULL_TOOLS: frozenset[str] = frozenset({
    "get_recent_messages",
    "get_conversation_with",
    "get_task_messages",
})
PUSH_TOOLS: frozenset[str] = frozenset({
    "send_message",
    "broadcast_message",
})
CHANNEL_PULL_TOOLS = PULL_TOOLS  # kept: record 1 is about pulls


def live_tool_names() -> set[str]:
    """The tool names the harness ACTUALLY builds, from the production factory.

    Used to assert that the classification above still covers the real tool set.
    A renamed or added communication tool must break loudly here rather than
    silently drop out of record 1.
    """
    from manager_agent_gym.core.communication.service import CommunicationService
    from manager_agent_gym.core.workflow_agents.tool_factory import ToolFactory

    tools = ToolFactory.add_communication_tools([], CommunicationService(), "probe")
    return {getattr(t, "name", type(t).__name__) for t in tools}


def classification_covers_live_tools() -> dict[str, Any]:
    """Assert the pull/push classification still spans every live comms tool."""
    live = live_tool_names()
    classified = PULL_TOOLS | PUSH_TOOLS
    return {
        "live_tools": sorted(live),
        "classified": sorted(classified),
        "unclassified_live_tools": sorted(live - classified),
        "classified_but_not_live": sorted(classified - live),
        "holds": not (live - classified),
    }


ABSENT = "__ABSENT__"


def _events(bundle: dict[str, Any], event_type: str) -> list[dict[str, Any]]:
    return [e for e in bundle.get("events", []) if e.get("event_type") == event_type]


# ---------------------------------------------------------------------------
# RECORD 1 — the target's channel pulls
# ---------------------------------------------------------------------------
def record_channel_pulls(bundle: dict[str, Any]) -> dict[str, Any]:
    """Every channel-pull tool call, with its index WITHIN THE RUN.

    The call index is what makes a before/after split possible: P2 must be read
    separately before and after the target's FIRST pull, because a target that has
    read something is no longer the same object as one that has not.
    """
    pulls: list[dict[str, Any]] = []
    for event in bundle.get("events", []):
        payload = event.get("payload") or {}
        history = payload.get("history") if isinstance(payload, dict) else None
        tool_name = None
        if isinstance(payload, dict):
            tool_name = payload.get("tool_name") or payload.get("name")
        if tool_name in PULL_TOOLS:
            pulls.append({
                "sequence": event.get("sequence"),
                "timestep": (payload.get("timestep")
                             if isinstance(payload, dict) else None),
                "agent_id": event.get("actor_id"),
                "task_name": event.get("task_name"),
                "tool_name": tool_name,
            })
        for call in _tool_calls_in_history(history):
            if call["name"] in PULL_TOOLS:
                pulls.append({
                    "sequence": event.get("sequence"),
                    "timestep": None,
                    "agent_id": event.get("actor_id"),
                    "task_name": event.get("task_name"),
                    "tool_name": call["name"],
                })

    for index, pull in enumerate(sorted(pulls, key=lambda p: (p["sequence"] or 0))):
        pull["call_index_within_run"] = index

    by_agent: dict[str, int] = {}
    for pull in pulls:
        agent = pull["agent_id"] or "(unknown)"
        by_agent[agent] = by_agent.get(agent, 0) + 1

    first_by_agent = {}
    for pull in sorted(pulls, key=lambda p: p.get("call_index_within_run", 0)):
        first_by_agent.setdefault(pull["agent_id"], pull["call_index_within_run"])

    return {
        "record": "channel_pulls",
        "pulls": pulls,
        "n_pulls": len(pulls),
        "pulls_by_agent": by_agent,
        "first_pull_index_by_agent": first_by_agent,
        "tools_counted": sorted(PULL_TOOLS),
        "pushes_not_counted": sorted(PUSH_TOOLS),
        "classification_check": classification_covers_live_tools(),
    }


def _tool_calls_in_history(history: Any) -> list[dict[str, Any]]:
    """Tool calls inside a `worker_run_completed` history, defensively parsed.

    The history's shape is the SDK's, not ours, so this reads permissively and
    reports what it found rather than assuming a schema. A shape it cannot read
    yields no calls — which the absence-based detector treats as UNKNOWN, never as
    "no tool was called".
    """
    calls: list[dict[str, Any]] = []
    if not isinstance(history, list):
        return calls
    for item in history:
        if not isinstance(item, dict):
            continue
        if item.get("type") in ("function_call", "tool_call") or "arguments" in item:
            name = item.get("name") or item.get("function", {}).get("name")
            if name:
                calls.append({"name": name, "arguments": item.get("arguments")})
        for content in (item.get("content") or []) if isinstance(
                item.get("content"), list) else []:
            if isinstance(content, dict) and content.get("type") in (
                    "tool_use", "function_call"):
                name = content.get("name")
                if name:
                    calls.append({"name": name,
                                  "arguments": content.get("input")
                                  or content.get("arguments")})
    return calls


def tool_calls_by_task(bundle: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Tool calls per completed worker run, keyed by task name.

    `history_readable` is tracked separately from "no calls": the absence-based
    detector must not read an unparseable history as evidence of in-head work.
    """
    out: dict[str, list[dict[str, Any]]] = {}
    for event in _events(bundle, "worker_run_completed"):
        payload = event.get("payload") or {}
        history = payload.get("history") if isinstance(payload, dict) else None
        task = event.get("task_name") or f"seq_{event.get('sequence')}"
        out[task] = _tool_calls_in_history(history)
        out.setdefault("__readable__", [])  # type: ignore[arg-type]
    return {k: v for k, v in out.items() if k != "__readable__"}


def history_readable_by_task(bundle: dict[str, Any]) -> dict[str, bool]:
    """Whether each worker run's history could be parsed at all."""
    out: dict[str, bool] = {}
    for event in _events(bundle, "worker_run_completed"):
        payload = event.get("payload") or {}
        history = payload.get("history") if isinstance(payload, dict) else None
        task = event.get("task_name") or f"seq_{event.get('sequence')}"
        out[task] = isinstance(history, list)
    return out


# ---------------------------------------------------------------------------
# RECORD 2 — refine events, with before/after description text
# ---------------------------------------------------------------------------
def record_refine_events(bundle: dict[str, Any]) -> dict[str, Any]:
    """Refines, with the BEFORE and AFTER description text.

    Text, not a count. `refine_task` rewrites `task.description`, which is a
    WORKER INPUT rendered into the task prompt — so a refine changes what the
    worker saw. A counted refine cannot be attributed; a refine with its
    before/after text can.
    """
    refines: list[dict[str, Any]] = []
    # Primary source: the `task_refined` event, which carries the before/after
    # TEXT. The manager's own action payload records that a refine happened but
    # not what the description was before, so it cannot support attribution.
    for event in _events(bundle, "task_refined"):
        payload = event.get("payload") or {}
        refines.append({
            "sequence": event.get("sequence"),
            "timestep": payload.get("timestep"),
            "task_id": payload.get("task_id"),
            "task_name": payload.get("task_name"),
            "description_before": payload.get("description_before", ABSENT),
            "description_after": payload.get("description_after", ABSENT),
        })

    # Fallback: refines visible only as a manager ACTION, with no text. Counted
    # separately and flagged unattributable rather than merged, because a refine
    # whose before-text is unknown cannot be tied to a change in worker input.
    action_only = 0
    for event in bundle.get("events", []):
        payload = event.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        parsed = payload.get("parsed_response")
        action = None
        if isinstance(parsed, dict):
            inner = parsed.get("action")
            action = (inner or {}).get("action_type") if isinstance(inner, dict) else None
            action = action or parsed.get("action_type")
        if action == "refine_task":
            action_only += 1

    missing_text = [r for r in refines
                    if r["description_before"] == ABSENT
                    or r["description_after"] == ABSENT]
    return {
        "record": "refine_events",
        "refines": refines,
        "n_refines": len(refines),
        # A refine without its before/after text is NOT usable for attribution.
        # Reported rather than silently counted, because the count is the thing
        # the spec explicitly says is not enough.
        "n_missing_before_after_text": len(missing_text),
        # ATTRIBUTABLE means every refine that HAPPENED carries its text — not
        # merely that the ones we can see do. A run with refine actions and no
        # text records is exactly the unattributable case.
        "attributable": (not missing_text
                         and action_only <= len(refines)),
        # If the manager refined more often than the text record shows, the
        # difference is refines we CANNOT attribute. Surfaced, never silently
        # equal to zero.
        "n_refine_actions_seen": action_only,
        "n_refines_without_text_record": max(0, action_only - len(refines)),
    }


# ---------------------------------------------------------------------------
# RECORD 3 — message -> manager visibility
# ---------------------------------------------------------------------------
def record_message_visibility(
    bundle: dict[str, Any],
    manager_id: str = "structured_manager",
) -> dict[str, Any]:
    """Every message, its addressee AS WRITTEN, and whether it was RENDERED.

    The distinction that matters: `recent_messages` is
    `get_all_messages()[:message_window]`, so whether a message reaches the
    manager's rendered window is a function of TRAFFIC VOLUME, not of the message.
    A correctly addressed, correctly delivered message can still never be
    rendered — and only the rendered ones support "the manager could have consumed
    it".
    """
    messages: list[dict[str, Any]] = []
    rendered_ids: set[str] = set()
    window_sizes: list[int] = []

    # Which ids the manager actually SAW, from the window record.
    for event in _events(bundle, "manager_message_window"):
        payload = event.get("payload") or {}
        for message_id in payload.get("rendered_message_ids") or []:
            if message_id:
                rendered_ids.add(str(message_id))
        if payload.get("message_window") is not None:
            window_sizes.append(int(payload["message_window"]))

    for event in _events(bundle, "message_sent"):
        payload = event.get("payload") or {}
        message_id = str(payload.get("message_id"))
        messages.append({
            "message_id": message_id,
            "sender_id": payload.get("sender_id"),
            "to_agent_as_written": payload.get("to_agent_as_written", ABSENT),
            "message_type": payload.get("message_type"),
            "related_task_id": payload.get("related_task_id"),
            "entered_rendered_window": message_id in rendered_ids,
        })

    return {
        "record": "message_visibility",
        "messages": messages,
        "n_messages": len(messages),
        "n_rendered": sum(1 for m in messages if m["entered_rendered_window"]),
        "manager_id": manager_id,
        "message_window_sizes_seen": sorted(set(window_sizes)),
        "n_window_records": len(_events(bundle, "manager_message_window")),
        "note": ("entry into the rendered window is a property of traffic volume, "
                 "not of the message — addressing does not imply visibility"),
    }


# ---------------------------------------------------------------------------
# RECORD 4 — ask-reply addressing
# ---------------------------------------------------------------------------
def record_reply_addressing(
    bundle: dict[str, Any],
    manager_id: str = "structured_manager",
) -> dict[str, Any]:
    """Replies, their `to_agent` AS WRITTEN, and whether it names the manager.

    The adopted consumption interpretation is addressed-to-me AND actionable-by-me,
    so a reply that does not name the manager is not in the consumable class. This
    cannot be assumed: the corpus measured 48 of 56 worker sends addressed to ids
    that do not exist.
    """
    visibility = record_message_visibility(bundle, manager_id=manager_id)
    replies = [m for m in visibility["messages"]
               if m["sender_id"] and m["sender_id"] != manager_id]
    for reply in replies:
        addressee = reply["to_agent_as_written"]
        reply["names_manager"] = (isinstance(addressee, str)
                                  and manager_id in addressee)
    return {
        "record": "reply_addressing",
        "replies": replies,
        "n_replies": len(replies),
        "n_naming_manager": sum(1 for r in replies if r.get("names_manager")),
        "manager_id": manager_id,
    }


# ---------------------------------------------------------------------------
# The deferral log and the realised/intended split
# ---------------------------------------------------------------------------
def record_deferrals(bundle: dict[str, Any]) -> dict[str, Any]:
    """Every logged `can_handle_task` refusal (spec §4.1 (i)).

    Realised-vs-intended must be RECONSTRUCTIBLE, never inferred: a segment absent
    from the completions could be a deferral, a crash, or a task never assigned at
    all, and those are three different findings.
    """
    events = _events(bundle, "assignment_deferred")
    deferrals = [{
        "task_id": (e.get("payload") or {}).get("task_id"),
        "task_name": (e.get("payload") or {}).get("task_name"),
        "agent_id": (e.get("payload") or {}).get("agent_id"),
        "timestep": (e.get("payload") or {}).get("timestep"),
        "agent_current_task_count": (e.get("payload") or {}).get(
            "agent_current_task_count"),
        "agent_max_concurrent": (e.get("payload") or {}).get("agent_max_concurrent"),
    } for e in events]
    by_task: dict[str, int] = {}
    for deferral in deferrals:
        key = deferral["task_name"] or "(unknown)"
        by_task[key] = by_task.get(key, 0) + 1
    return {
        "record": "deferrals",
        "deferrals": deferrals,
        "n_deferrals": len(deferrals),
        "deferrals_by_task": by_task,
        "tasks_ever_deferred": sorted({d["task_name"] for d in deferrals
                                       if d["task_name"]}),
    }


# ---------------------------------------------------------------------------
# The denominator
# ---------------------------------------------------------------------------
def observed_denominator(bundle: dict[str, Any]) -> dict[str, Any]:
    """The denominator COMPUTED FROM THE OBSERVED POST-SWAP TASK SET (spec §4.4).

    Never assumed from the generator's task count: a run that created or retried
    tasks has a different denominator from the one the generator implies, and
    quoting the generator's number would divide by a set that did not exist.

    Every task is stamped with its PRE/POST-SWAP ORIGIN. A task created after
    t_swap is not comparable to one that existed before it, and a denominator that
    mixes them silently changes meaning between cells.
    """
    manifest = bundle.get("manifest", {})
    t_swap = manifest.get("t_swap")
    board = bundle.get("task_board_final") or []
    index = bundle.get("index", {})
    planned = set(index.get("segment_task_ids", {}).values())
    planned |= set(index.get("upstream_task_ids", []))
    planned |= set(index.get("downstream_task_ids", []))

    completions_by_task = {c["task_id"]: c for c in bundle.get("completions", [])}

    rows = []
    for entry in board:
        task_id = entry.get("task_id")
        completion = completions_by_task.get(task_id)
        # ORIGIN: a task present in the generator's index existed before the run,
        # so it is pre-swap by construction. Anything else was created during the
        # run, and its origin is decided by WHEN — which only the completion (or a
        # create event) can tell us.
        if task_id in planned:
            origin = "pre_swap_planned"
        elif completion and t_swap is not None:
            origin = ("post_swap_created" if completion["timestep"] > t_swap
                      else "pre_swap_created")
        else:
            origin = "created_origin_unknown"
        rows.append({
            "task_id": task_id,
            "task_name": entry.get("task_name"),
            "status": entry.get("status"),
            "origin": origin,
            "completed": entry.get("status") == "completed",
        })

    by_origin: dict[str, int] = {}
    for row in rows:
        by_origin[row["origin"]] = by_origin.get(row["origin"], 0) + 1

    segment_ids = set(index.get("segment_task_ids", {}).values())
    segment_rows = [r for r in rows if r["task_id"] in segment_ids]

    return {
        "record": "denominator",
        "n_observed_tasks": len(rows),
        "n_planned_tasks": len(planned),
        "by_origin": by_origin,
        "n_created_during_run": sum(
            1 for r in rows if r["origin"] != "pre_swap_planned"),
        "segment_denominator": len(segment_rows),
        "segments_completed": sum(1 for r in segment_rows if r["completed"]),
        "rows": rows,
    }


def unstaffed_segment_count(bundle: dict[str, Any]) -> dict[str, Any]:
    """UNSTAFFED SEGMENTS as a first-class field (S6/S7 reviews).

    Reported beside regret, always, because capacity starvation and bad allocation
    produce the SAME regret number by different mechanisms. Without this count a
    starved run reads as an allocation finding.
    """
    unstaffed = list(bundle.get("unstaffed_segments") or [])
    deferrals = record_deferrals(bundle)
    deferred_names = set(deferrals["tasks_ever_deferred"])
    index = bundle.get("index", {})
    name_by_segment = {
        seg: name for seg, name in (
            (seg, f"Risk-weighted assets — {seg}")
            for seg in index.get("segment_task_ids", {})
        )
    }
    unstaffed_after_deferral = [
        seg for seg in unstaffed if name_by_segment.get(seg) in deferred_names
    ]
    return {
        "record": "unstaffed_segments",
        "n_unstaffed": len(unstaffed),
        "unstaffed_segments": unstaffed,
        "n_unstaffed_with_a_logged_deferral": len(unstaffed_after_deferral),
        "unstaffed_with_a_logged_deferral": unstaffed_after_deferral,
        "note": ("capacity starvation and bad allocation produce the same regret "
                 "by different mechanisms; this count is what separates them"),
    }


REQUIRED_RECORDS = (
    "channel_pulls",
    "refine_events",
    "message_visibility",
    "reply_addressing",
)


def all_records(bundle: dict[str, Any],
                manager_id: str = "structured_manager") -> dict[str, Any]:
    """Every record, keyed by name. What a bundle must carry to enter analysis."""
    return {
        "channel_pulls": record_channel_pulls(bundle),
        "refine_events": record_refine_events(bundle),
        "message_visibility": record_message_visibility(bundle, manager_id),
        "reply_addressing": record_reply_addressing(bundle, manager_id),
        "deferrals": record_deferrals(bundle),
        "denominator": observed_denominator(bundle),
        "unstaffed_segments": unstaffed_segment_count(bundle),
    }


# ---------------------------------------------------------------------------
# HAND-BACKS — post-hoc classification, with its undercount made auditable
# ---------------------------------------------------------------------------
def match_messages_to_segments(
    bundle: dict[str, Any],
    segment_ids: list[str],
    segment_terms: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Attribute messages to segments by ID **and by CONTENT**.

    WHY CONTENT MATCHING IS NOT OPTIONAL. CHECK-4's corpus says workers DESCRIBE
    rather than reference — they write "the corporate exposure I was given",
    not "seg_03". Id-matching alone would therefore miss most hand-backs, and the
    miss would be invisible: a zero would read as "workers do not hand back".

    WHY THIS IS STILL AN UNDERCOUNT, stated rather than hidden. Post-hoc
    classification cannot recover a hand-back phrased in terms this function does
    not know. The accepted trade (RR, after withdrawing the fourth-form proposal):
    inviting an explicit `referred` form in EVERY cell would shape C3 in its own
    control cells, which is a larger contamination than the classification gap it
    fixes. An undercount is recoverable by READING; a contaminated channel is not.

    Which is why `unmatched` carries the TEXTS and not merely a count — the known
    undercount is auditable rather than invisible.
    """
    terms = segment_terms or {}
    messages = record_message_visibility(bundle)["messages"]
    events = {e.get("payload", {}).get("message_id"): e
              for e in _events(bundle, "message_sent")}

    matched: dict[str, list[dict[str, Any]]] = {sid: [] for sid in segment_ids}
    unmatched: list[dict[str, Any]] = []

    for message in messages:
        payload = (events.get(message["message_id"]) or {}).get("payload") or {}
        text = str(payload.get("content") or "")
        related = payload.get("related_task_id")
        hits = [sid for sid in segment_ids
                if sid in text
                or (related and sid in str(related))
                or any(term.lower() in text.lower() for term in terms.get(sid, []))]
        if len(hits) == 1:
            matched[hits[0]].append({**message, "matched_by":
                                     "id" if hits[0] in text else "content"})
        else:
            # AMBIGUOUS OR UNMATCHED, kept WITH ITS TEXT. A message naming two
            # segments is not assigned to either: guessing would manufacture an
            # attribution, which is the same refusal the parser makes.
            unmatched.append({**message, "text": text[:400],
                              "n_candidate_segments": len(hits)})

    return {
        "record": "message_segment_matching",
        "matched": {k: v for k, v in matched.items() if v},
        "n_matched": sum(len(v) for v in matched.values()),
        "unmatched": unmatched,
        "n_unmatched": len(unmatched),
        "limitation": ("post-hoc classification UNDERCOUNTS toward filing real "
                       "hand-backs as unmatched; the unmatched TEXTS are reported "
                       "so the undercount is auditable by reading"),
    }
