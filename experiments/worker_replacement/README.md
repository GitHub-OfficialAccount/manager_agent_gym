# Worker replacement

**A manager plans a Basel capital calculation. Partway through, one of its analysts is
replaced by someone it did not choose — and the staff record still describes the person
who left.**

The question the environment asks: does the manager's plan follow the team, and what does
it need to know for that to happen?

## Running it

```bash
python -m examples.run_examples --workflow_name worker_replacement --max-timesteps 22
python -m examples.run_examples --workflow_name worker_replacement_updated_card --max-timesteps 22
```

`--max-timesteps 22` matters. The default is 50, which costs more than it buys; 22 is
enough for the graph to finish and short enough that an unfinished segment is a real
outcome rather than an artefact of an unlimited clock.

You need one API key for whatever provider `team.WORKER_MODEL` names, and nothing else.

The two differ in **one boolean** — whether the newcomer's staff record was updated at the
swap. Everything else is byte-identical, so a difference between them is attributable to
the record and to nothing else.

## Scoring it

The run writes to `simulation_outputs/<scenario>/run_seed_<n>/` — note the scenario
subdirectory; it is not `simulation_outputs/run_<timestamp>/`.

```python
from examples.end_to_end_examples.worker_replacement import format_run, score_run

print(format_run("simulation_outputs/worker_replacement/run_seed_42"))
```

Scoring reads the per-timestep dump the engine already writes, so it needs nothing saved
alongside the run and it can score an episode that was killed part-way — a segment nobody
reached scores zero and is listed as unallocated rather than silently dropped.

The same three numbers are also computed live during the run, as preference rubrics. Both
paths go through one reader, so they cannot disagree.

## What it measures

Every segment has exactly one right answer, so nothing here needs a judge. Three scores,
deliberately not one:

| | what it asks |
|---|---|
| **accuracy** | what the team actually delivered, against the best available |
| **routing** | what the manager's **allocation** made reachable, against the same |
| **coverage** | whether every segment got priced at all |

**`routing` is the one to watch.** It isolates the manager's own decision from its workers'
arithmetic. On the reference episode the routing loss is exactly `0.0000` while the
execution loss is `1.6882` — the manager allocated perfectly and the workers spent it. A
single combined score hides which of the two happened.

Routing is weighted but not dominant, on purpose. Making it the objective would tell the
manager that checking its team's work does not count.

## The environment

Nine exposure segments, four analysts, each holding IRB model approval for two asset
classes and the standardised approach for everything. **Nobody is ever switched off** — an
analyst without the relevant approval still returns a real figure, just a worse one. The
competence gap grades the answer; it never denies an output.

At timestep 3 the predecessor rolls off and a successor joins. In the stale condition the
successor inherits the predecessor's `agent_description` verbatim: nobody authors a false
description, the record simply was not updated when the person changed.

Everything is a literal. There is no generator and no data file, so *which environment
produced this figure* has one answer.

## Known limitation, stated up front

**On six of the nine segments more than one analyst attains the maximum, so no allocation
can be wrong there.** The routing choice only matters on three, and the newcomer is the
sole holder of just one of them — worth 0.27% of the total.

A manager that ignores the swap entirely scores optimally on this environment, and does so
correctly. **That is a property of the environment, not a finding about managers.** Anyone
using this to compare manager policies should expect routing scores near 1.0 and should
read `discriminating_segments()` before concluding anything from that.

## Portability

Imports nothing outside `manager_agent_gym.schemas`. Two optional fields are detected at
import and skipped when absent, so it runs on a library without them:

- `Task.task_class` — without it, segments are matched by the `seg_NN` in their name.
  Weaker: rename a segment task and it stops being scored.
- `AIAgentConfig.max_turns` — without it, workers use the library default of 10 turns and
  some executions will be lost to the limit. A lost execution is recorded as an unpriced
  segment rather than hidden.

Roster removal (`("remove", cfg, reason)` in the team timeline) is standard and needs
nothing extra.

## Files

| | |
|---|---|
| `workflow.py` | the nine segments and the task graph |
| `team.py` | the four analysts, the swap, the stale record |
| `scoring.py` | the Basel formula, best possible, the two losses, the reader |
| `preferences.py` | the three rubrics — all Python functions, no LLM |
| `test_worker_replacement.py` | acceptance; every number above is asserted here |

Run the tests with `pytest examples/end_to_end_examples/worker_replacement/`. They need no
API key and no run directory.
