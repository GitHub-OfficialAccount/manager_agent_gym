# worker_replacement — index

_`README.md` is the one-page version. This is the full map._

Study 1: **when a manager's worker is replaced mid-workflow by an event it did not choose, which
sources of information about the newcomer change its allocation decisions?**

---

## Start here, in this order

| | |
|---|---|
| **`../../RESEARCH-CRON-STATUS.md`** | Where the study stands, the one open decision, and what is live. **Read this first** — it is at the repo root. |
| **`STUDY1_FOUNDATION.md`** | The authoritative brief. Carries dated amendments (★) from the repair phase. |
| **`BACKLOG.md`** | Current steps + the **findings log** at the bottom — the whole phase in one place, retractions kept as retractions. |
| **`METHODOLOGY_RULES.md`** | The rules. Every one names the failure that paid for it. |

## Specs and reference

| | |
|---|---|
| `HARNESS_SPEC_v2.md` | The build-governing spec for the harness layer. |
| `STUDY1_LOGGING_AND_ORDERING.md` | Logging records and ordering detail. |
| `SCOOP_CHECK_2026-08-06.md` | External novelty check, verified at primary source. Cited as evidence by the brief. |
| `IDEAS.md` | The idea shelf. §4 holds surfaced-but-not-taken ideas. |
| `BRAINSTORM.md` | The audit log. **Never edited, only annotated** — it is how the direction was reached. |

## Records

`records/<step>/` holds, per step: the acceptance-check output, `*_review_LS.md`, and
`*_review_RR.md`. A step is complete only when all three exist.

`records/L4/DIRECTIONS_LS.md` is the ceiling arc and the three-way decision in full — the single
most useful record if you are picking up the science rather than the code.

## Archive

`archive/` holds superseded documents, retained rather than deleted. **Nothing there governs
current work.** If a live document cites one, it is citing history.

---

## Code map

**The environment and its scoring** — `finance_env`, `finance_generator`, `finance_scorer`,
`finance_cells`, `finance_report_parser`.

**Measurement** — `finance_split` (segment outcome by cause), `finance_reroute` (the behavioural
DV over assignments), `finance_scope_report`, `finance_quantities` (the quantity registry that
refuses to print a rate without its population and comparator).

**Gates and guards** — `finance_admission`, `finance_comparability`, `finance_fabrication`,
`finance_gate`, `finance_logging`.

**Entry points** — `run_finance_episode`, `select_study_instances`.

**Offline pricing** (no run spend; each answers a design question before it is built) —
`check_card_ceiling`, `check_reliability_ceiling`, `check_slack_sweep`, `check_template_pricing`,
`check_reroute_recoverability`, `check_load_feedback`, `check_quantity_kinds`.

**Tests** — `test_finance_*` are acceptance scripts run as modules
(`python -m experiments.worker_replacement.test_finance_split`), not pytest tests. They print a
`RESULT: PASS` line and assert their own positive controls.

---

_Renamed from `ds_reroute` on 2026-08-08 — the environment is Basel finance, not data science,
and the study is worker replacement. `evidence_labels/` moved to `records/evidence_labels_arm3/`;
it holds artifacts of the deleted pipeline and was not current._

_The pre-revamp pipeline (arm3, probes, tss, collapse, viewer, and the old `check_*`) was removed
in the 2026-08-08 cleanup — 56 modules and their 10 orphaned tests. Nothing live imported them._
