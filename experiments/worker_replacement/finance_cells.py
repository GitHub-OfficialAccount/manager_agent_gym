"""R2 — the six study cells, as CONFIGURATION over the S8 environment.

Not six environments. One environment with three switches, so "everything else is
identical" is true BY CONSTRUCTION rather than by diligence — and asserted anyway
by `finance_comparability`, because construction is exactly what was wrong the
last time something was assumed identical.

    | Cell | Swap | Card (C1)             | Declaration (C2) | Ask (C3) |
    |------|------|-----------------------|------------------|----------|
    | U    | none | n/a                   | n/a              | n/a      |
    | 0    | yes  | predecessor's on file | absent           | disabled |
    | 1    | yes  | UPDATED at t_swap     | absent           | disabled |
    | 2    | yes  | predecessor's on file | PRESENT          | disabled |
    | 3    | yes  | predecessor's on file | absent           | ENABLED  |
    | 4    | yes  | UPDATED               | PRESENT          | ENABLED  |

WHAT EACH SWITCH ACTUALLY IS, since each could have been built the wrong way:

  C1 CARD. The successor's `agent_description` either carries the PREDECESSOR's
  text (stale by succession — nobody authored a lie, the file simply was not
  updated) or its own. Staleness is byte-identical to the predecessor's pre-swap
  card, never written afresh, so the cell cannot accidentally differ in wording.

  C2 DECLARATION. The `method:` line — a BY-PRODUCT self-description: a worker
  that writes "SA" on an IRB-approved segment has revealed something about its
  own coverage without being asked. Absent means the report convention does not
  request it; the `rwa:` line and the decline form are untouched, so scoring and
  the refusal channel are identical across cells.

  C3 ASK. NOT a tool difference — the core-tool rule forbids that, and every
  worker holds the same tools in every cell. What changes is whether the worker's
  prompt names the MANAGER'S AGENT ID as the address for replies. The corpus
  measured workers naming the manager in 2 of 56 sends, so a manager-addressed
  reply cannot be assumed; making it addressable IS the manipulation, and that is
  stated in the design rather than left as an implementation detail.

CELL U IS NOT "CELL 0 WITHOUT INFORMATION". It has no swap at all: the
predecessor never leaves. It scores against ITS OWN roster's oracle (the pre-swap
roster persists), so U-vs-0 compares each cell's regret against its own attainable
optimum rather than against a shared one.

AND U-vs-0 IS A JOINT CONTRAST, NOT THE SWAP EFFECT. U holds the predecessor;
0-4 hold the successor. So the two differ by whether a swap occurred AND by which
three workers are present, and those are not separable by any analysis of these
cells. Any claim from U-vs-0 is about the joint quantity — "the swap and the
roster change it entails" — never about the swap alone.

EVERY CONTRAST IS MARGINAL. Behaviour — artifacts, outcomes, what a worker
actually produces — is an always-present fifth channel in every cell. A null
therefore licenses "channel X added nothing beyond what behaviour already showed",
never "channel X had no effect".
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from manager_agent_gym.core.workflow_agents.registry import AgentRegistry
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig

from . import finance_env as env
from . import finance_generator as gen
from . import finance_report_parser as rp

MANAGER_AGENT_ID = "structured_manager"


@dataclass(frozen=True)
class Cell:
    """One cell as three switches plus the swap. Nothing else may vary."""

    name: str
    swap: bool
    card_updated: bool
    declaration_present: bool
    ask_enabled: bool
    role: str


CELLS: dict[str, Cell] = {
    "U": Cell("U", swap=False, card_updated=False, declaration_present=False,
              ask_enabled=False,
              # CLAIM NARROWED (RR, R2 review). Not "the replacement effect":
              # U keeps the predecessor while 0-4 have the successor, so U-vs-0
              # differs by whether a swap occurred AND by which three workers are
              # present. Those are not separable, and U's oracle is over a
              # different team. Scoring U against its own roster stays right; the
              # CLAIM is the joint quantity, not the swap alone.
              role="unswapped control — the JOINT effect of the swap and the "
                   "roster change it entails (NOT the swap effect alone: U and 0 "
                   "differ by which workers are present as well as by the swap)"),
    "0": Cell("0", swap=True, card_updated=False, declaration_present=False,
              ask_enabled=False,
              role="information-absent control; allocation-visibility gate"),
    "1": Cell("1", swap=True, card_updated=True, declaration_present=False,
              ask_enabled=False, role="card channel (marginal)"),
    "2": Cell("2", swap=True, card_updated=False, declaration_present=True,
              ask_enabled=False, role="declaration channel (marginal)"),
    "3": Cell("3", swap=True, card_updated=False, declaration_present=False,
              ask_enabled=True, role="ask channel (ride-along)"),
    "4": Cell("4", swap=True, card_updated=True, declaration_present=True,
              ask_enabled=True,
              role="CEILING — a bound, NOT an interaction claim"),
}

# The report convention, split so C2 can remove the declaration WITHOUT touching
# the value line or the decline form. Scoring and refusal must be identical across
# cells; only the by-product self-description varies.
_VALUE_CONVENTION = (
    "REPORT FORMAT — so your answer can be read automatically, put your "
    "conclusion in this line:\n"
    "  rwa: <the risk-weighted assets figure, in currency units>\n"
    "Write the number plainly, e.g. 'rwa: 12345678.90' — not a range, and not "
    "more than one rwa line. Explanatory prose around it is fine.\n"
    "If you judge that you cannot price this segment, say so in the same form:\n"
    "  rwa: unavailable\n"
    "That is a legitimate outcome and is recorded as one; it is not a failure to "
    "follow the format."
)


def convention_text(cell: Cell) -> str:
    """The report convention for this cell. C2 adds the declaration line."""
    if cell.declaration_present:
        return rp.REPORT_CONVENTION_TEXT
    return _VALUE_CONVENTION


def ask_text(cell: Cell) -> str:
    """C3. Naming the manager's id is what makes a reply addressable to it."""
    if not cell.ask_enabled:
        return ""
    return (
        f"\n\nIf the manager ({MANAGER_AGENT_ID}) messages you, you may reply. "
        f"Address any reply to {MANAGER_AGENT_ID}.\n"
    )


def build_team(instance: dict[str, Any], cell: Cell) -> dict[str, AIAgentConfig]:
    """The team for this cell. Identical across cells except the three switches."""
    team = env.build_team(instance)
    event = instance["event"]
    predecessor = next(w for w in instance["workers"]
                       if w["worker_id"] == event["predecessor_id"])

    out: dict[str, AIAgentConfig] = {}
    for worker_id, config in team.items():
        system_prompt = config.system_prompt.replace(
            rp.REPORT_CONVENTION_TEXT, convention_text(cell)) + ask_text(cell)
        description = config.agent_description
        if (cell.swap and not cell.card_updated
                and worker_id == event["successor_id"]):
            # STALE BY SUCCESSION. The successor inherits the PREDECESSOR's card
            # text verbatim — nobody authored a false description, the file simply
            # was not updated when the person changed. Taking the predecessor's
            # own string rather than rewriting one is what keeps the staleness
            # byte-identical and unauthored.
            description = team[predecessor["worker_id"]].agent_description
        out[worker_id] = config.model_copy(update={
            "system_prompt": system_prompt,
            "agent_description": description,
        })
    return out


def wire_roster(instance: dict[str, Any], registry: AgentRegistry,
                team: dict[str, AIAgentConfig], cell: Cell) -> None:
    """Pre-swap roster always; the swap only in swap-carrying cells."""
    event = instance["event"]
    for worker_id in event["roster_pre_swap"]:
        registry.schedule_agent_add(0, team[worker_id], "initial engagement team")
    if not cell.swap:
        return                     # cell U: the predecessor never leaves
    registry.schedule_agent_remove(int(event["t_swap"]), event["predecessor_id"],
                                   "rolled off the engagement")
    registry.schedule_agent_add(int(event["t_swap"]),
                                team[event["successor_id"]],
                                "joined the engagement")


def active_roster(instance: dict[str, Any], cell: Cell) -> list[str]:
    """Whose oracle this cell is scored against.

    Cell U keeps the PRE-swap roster, so it is scored against its own attainable
    optimum. Scoring U against the post-swap roster would compare its regret to an
    optimum for a team it never had.
    """
    event = instance["event"]
    return list(event["roster_pre_swap"] if not cell.swap
                else event["roster_post_swap"])


# ---------------------------------------------------------------------------
# THE SELECTION RECORD IS THE AUTHORITY ON WHAT WE RUN (L17, LS ruling)
#
# The approved draw fixes BOTH which seeds run and the generator setting they were
# drawn under. Threading that setting through the build path makes a mismatch
# unlikely; this makes it UNSHIPPABLE. The distinction earned its place: threading
# is the fix that was applied to this same function once before, for the lattice,
# and it did not hold when four more parameters arrived.
#
# THE EVIDENCE ALREADY EXISTED AND NOTHING COMPARED IT (LS). Every bundle manifest
# records `instance_sha256`, so today's mismatch would have been recoverable from
# the artefact afterwards -- and flagged by nothing. A recorded fact nobody
# compares is the shape we keep finding.
# v3 = v2 plus `instance_sha256` stamped per chosen instance at approval
# time. Same rule, same draw seed, same pool -- not a re-draw. Pointing here
# is what upgrades the guard from a threading check to a provenance one.
SELECTION_RECORD = (Path(__file__).resolve().parent / "records" / "L10"
                    / "environment_selection_v3.json")


def shipped_setting(record_path: Path = SELECTION_RECORD) -> dict[str, Any]:
    """The generator setting the approved draw was made under. One object."""
    return json.loads(record_path.read_text())["setting"]


def shipped_seeds(record_path: Path = SELECTION_RECORD) -> list[int]:
    return [row["seed"] for row in
            json.loads(record_path.read_text())["chosen"]]


def assert_matches_selection(seed: int, instance: dict[str, Any],
                             record_path: Path = SELECTION_RECORD) -> dict[str, Any]:
    """REFUSE unless this instance is the one the selection record specifies.

    Compares against an instance REBUILT FROM THE RECORD'S OWN SETTING rather than
    against a stored hash, because the approved record does not carry one -- and
    re-deriving an approved artefact to add a field is a worse trade than deriving
    the expectation from what it already states.

    Raises rather than warning. A run that has already spent money and then reports
    a mismatch is the failure this exists to prevent, so it fires BEFORE the first
    timestep and stops the episode.
    """
    setting = shipped_setting(record_path)
    actual = env.instance_hash(instance)

    # ★ PREFER THE STORED HASH; REBUILDING IS A WEAKER CHECK (RR, L22). My first
    # version ALWAYS rebuilt the expected side with the current generator, so both
    # sides moved together: if the generator changed, expected and actual changed
    # in step and the guard passed. That verifies THREADING -- did the six
    # parameters reach `generate()` -- and not PROVENANCE, while the error message
    # claimed provenance.
    #
    # It is not hypothetical. L10's own history is the counterexample: the v1
    # ceilings were priced at cap 3 against a runtime enforcing none, and a
    # rebuild-both-sides guard would have passed that silently every time.
    #
    # A hash STAMPED AT APPROVAL TIME cannot move with the generator, so comparing
    # against it catches generator drift as well as threading. Records that predate
    # the stamp fall back to rebuilding, and the return says WHICH check ran --
    # a guard that cannot report its own strength is the shape this whole phase has
    # been spent removing.
    record = json.loads(record_path.read_text())
    stamped = {row["seed"]: row.get("instance_sha256")
               for row in record.get("chosen", [])}
    expected = stamped.get(seed)
    mode = "stamped_hash"
    if not expected:
        expected = env.instance_hash(gen.generate(seed, **setting))
        mode = "rebuilt_from_setting"

    if expected != actual:
        raise ValueError(
            f"INSTANCE MISMATCH for seed {seed}: this run built {actual[:16]} but "
            f"{record_path.name} selected {expected[:16]} (check: {mode}). The "
            f"record's setting is {setting}. Refusing to run -- selecting on one "
            f"population and running on another is not a degraded run, it is a run "
            f"of something nobody chose."
        )
    return {"instance_sha256": actual, "selection_record": record_path.name,
            "setting": setting, "matches_selection": True,
            "check": mode,
            "checks_generator_drift": mode == "stamped_hash",
            "caveat": (None if mode == "stamped_hash" else
                       "no stored hash in this record: expected was REBUILT with "
                       "the current generator, so this verifies threading and NOT "
                       "generator drift -- both sides move together if the "
                       "generator changes")}


def build_cell_environment(seed: int, cell_name: str,
                           lattice: str | None = None,
                           shared_class_segments: int | None = None,
                           **instance_kwargs: Any) -> dict[str, Any]:
    """A runnable environment for (instance seed, cell). The single entry point.

    ★ THE WHOLE SETTING IS ONE OBJECT NOW, AND THAT IS THE POINT (L17). This took
    `lattice` and `shared_class_segments` as named parameters and passed ONLY those
    two to `generate()`. The shipped setting has SIX. The other four fell back to
    generator defaults, so the runner built a different instance from the one the
    draw selected:

        seed 42   drawn on  ef25aa9d  ceiling 0.04970
                  built     ce61d5b5  ceiling 0.02632   <- BELOW the 0.03238 floor
                                                           that selected it

    Not a degraded run -- a run of something we never chose.

    THIS IS THE SECOND TIME THE SAME FIX WAS APPLIED HERE. The paragraph this
    replaces read: "THE ARRANGEMENT IS A PARAMETER, and it was not. This called
    `gen.generate(seed)` bare, so a study run built the DEFAULT lattice no matter
    which arrangement had been selected." The lattice was threaded; the four
    amplifiers arrived later and were not. **Threading parameters ONE AT A TIME is
    the bug, not the missing parameter** -- every new generator knob re-opens it at
    every hop.

    So the signature now takes `**instance_kwargs` and forwards the lot. The two
    named parameters are kept for existing callers and default to None, meaning
    "not specified", rather than to a value that silently disagrees with the
    selection record.

    THREADING ALONE IS NOT THE FIX AND WAS NOT LAST TIME EITHER. The run-start hash
    assertion in `run_finance_episode` is what makes this unshippable rather than
    merely unlikely -- see `assert_matches_selection`.
    """
    cell = CELLS[cell_name]
    if lattice is not None:
        instance_kwargs["lattice"] = lattice
    if shared_class_segments is not None:
        instance_kwargs["shared_class_segments"] = shared_class_segments
    instance = gen.generate(seed, **instance_kwargs)
    workflow, index = env.build_workflow(instance)

    if not cell.declaration_present:
        # The task text carries the convention too; both must move together or the
        # worker sees two different conventions.
        for task in workflow.tasks.values():
            if rp.REPORT_CONVENTION_TEXT in task.description:
                task.description = task.description.replace(
                    rp.REPORT_CONVENTION_TEXT, convention_text(cell))

    team = build_team(instance, cell)
    registry = AgentRegistry()
    registry.register_agent_class("ai", env.CapacityBoundedAIAgent)
    wire_roster(instance, registry, team, cell)

    return {
        "cell": cell.name,
        "cell_config": {
            "swap": cell.swap, "card_updated": cell.card_updated,
            "declaration_present": cell.declaration_present,
            "ask_enabled": cell.ask_enabled, "role": cell.role,
        },
        "instance": instance,
        "workflow": workflow,
        "team": team,
        "registry": registry,
        "index": index,
        "horizon": env.horizon(instance, n_tasks=index["n_tasks"],
                              n_fixed=len(index["fixed_task_ids"])),
        "active_roster": active_roster(instance, cell),
        "instance_seed": seed,
        "instance_sha256": env.instance_hash(instance),
        "capacity_mapping": {
            "cap": env.SEGMENT_WINDOW_TIMESTEPS,
            "segment_window_timesteps": env.SEGMENT_WINDOW_TIMESTEPS,
            "max_concurrent_tasks_per_worker": 1,
            "post_swap_roster_size": len(active_roster(instance, cell)),
            "n_segments": len(instance["segments"]),
        },
    }
