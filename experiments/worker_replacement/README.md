# worker_replacement

**A manager agent's worker is replaced mid-workflow by an event it did not choose. Which sources
of information about the newcomer change its allocation decisions?**

The newcomer is fully capable but qualified for different things. The manager can learn what it
got from four channels: the registry **card** (still describing the predecessor — stale by
succession), the newcomer's **self-descriptions**, **asking** it, and its execution **trace**.
We measure what the manager does on the margin it owns: **who gets which task.**

**Environment:** a Basel capital calculation. Nine exposure segments, three workers, each
qualified for some asset classes and not others. Ground truth is computable without an LLM judge.

---

## Read in this order

| | |
|---|---|
| **`../../RESEARCH-CRON-STATUS.md`** | Where it stands, the one open decision, what is live. **Start here** — it is at the repo root. |
| `STUDY1_FOUNDATION.md` | The authoritative brief, with dated amendments (★). |
| `BACKLOG.md` | Current steps; the **findings log** at the bottom is the whole phase in one place. |
| `METHODOLOGY_RULES.md` | Rules, each naming the failure that paid for it. |
| `INDEX.md` | Full document and code map. |

## State in one paragraph

The instrument is repaired and the manipulation is priced. **Knowing the newcomer's true
qualifications is worth 1.24% of achievable score — 0.16σ, ~616 episodes per arm — so it is real
and undetectable at any affordable sample.** One ceiling bounds all four channels. A lattice
repair is proposed but its value depends on an unset parameter it also disables. **One decision
is open and everything waits on it (`RESEARCH-CRON-STATUS.md` §1, at the repo root).** Nothing has run since the scope run.

## Layout

```
finance_*.py     the environment, its scoring, and the measurements
check_*.py       offline pricing — each answers a design question before anything is built
test_*.py        acceptance scripts, run as modules, not pytest:
                   python -m experiments.worker_replacement.test_finance_split
records/         per step: acceptance output + two independent reviews
archive/         superseded documents. Governs nothing.
outputs/         run bundles (untracked)
```

**Core plumbing outside this directory** — nine deliberate deviations from upstream in
`manager_agent_gym/`, documented in `CHANGED.md` at the repo root. A fresh clone behaves
differently; read that before assuming parity.

## Two conventions worth knowing

**Every reported quantity states its population, its comparator and its plausible range** — the
emitter refuses to print one that does not. Six of this project's failures were a number that was
arithmetically right and semantically wrong.

**Price the ceiling offline before spending on a contrast.** Compute the best effect a
manipulation could have, convert to σ and episodes-per-arm. If the ceiling is below detectability,
no run answers the question. That check costs nothing and this project learned it the expensive
way.
