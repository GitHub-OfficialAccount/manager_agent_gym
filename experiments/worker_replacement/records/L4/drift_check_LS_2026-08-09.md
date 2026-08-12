# L4 drift check — `STUDY1_FOUNDATION.md` against the state after L9 (LS, 2026-08-09)

Run because **L9 is blocked on the researcher and L2a/L8 are with peers**, which is the cron's
stated condition for spending a firing on the drift check rather than inventing work.

**Verdict: the brief's QUESTION is intact and every finding this phase serves it. Its DESIGN
section describes a perturbation the study no longer uses, and its GATE cannot be run as written.**

---

## No drift

- **§1 The question** — unchanged and fully served. *"The newcomer is fully capable but works
  differently… four sources… who gets which task."* Every L9 finding is about which source changes
  allocation. **No drift.**
- **§1 Scoped OUT** (in-place behavioural change) — unchanged, still honoured.
- **§5 Primary DV** — the L7 amendment (defined over ASSIGNMENTS, forced/discretionary separated
  and never summed, conditioned share primary) is current and was not touched by L9. **No drift.**
- **§5 Estimator** — arm-paired on (seed, batch). Untouched.

## ★ DRIFT 1 — the brief names a perturbation the study does not use, and contains both

**§4:** *"The perturbation (successor's difference): prompt-level METHOD SUBSTITUTION under three
requirements — allocation-visible, trace-distinguishable (distinct tool call and/or distinct truth
value), successor-reachable."*

**Everything measured this phase is a COVERAGE LATTICE: the successor is APPROVED for different
asset classes.** It does not compute differently; it is qualified differently. *"Trace-distinguishable
via a distinct tool call or truth value"* does not describe it.

**And the brief already contains the other version, unreconciled:** §4's own scope condition says
*"COVERAGE information cannot address the dominant allocation error"*. **So the authoritative brief
names two different manipulations and does not say which one the study runs.**

**This is the largest drift and it is the researcher's to settle**, because the answer decides what
the paper's manipulation *is*. **Not fixed here** — a drift check reports.

## ★ DRIFT 2 — the gate cannot be run as written

**§6:** PASS requires *"(i) ≥1 correct post-swap outcome demonstrably via the SUBSTITUTED METHOD
(metric-truth match)"*.

**Under a coverage perturbation there is no substituted method to demonstrate.** Criterion (i) has
no referent; criterion (ii) (a post-swap task assigned to and executed by the successor id) still
does. **The gate is half-applicable and §10's item 5 — *"the go: build delta §8, then the gate
§6"* — is stale by the same amount.** Follows from Drift 1 and is settled with it.

## DRIFT 3 — the scope condition is CORRECT and much weaker than what we now know

**§4:** *"holds IN A REGIME WHERE CAPACITY BINDS EXACTLY: C=3 × 3 workers = 9 segments leaves no
slack."* **Still true.** The phase found the exact rule underneath it:

    uncovered lie   channel requires  nA >= cap   needs CONTENTION to displace
    covered lie     channel requires  nA <  cap   needs a FREE SLOT to misdirect into

**The qualifier as written understates the finding in a way that flatters the shipped design:**
it reads as *"the effect is small in this regime"*, and the measurement is that **the shipped
lattice is EXACTLY ZERO at a realistic mix.** **Updating it strengthens the claim discipline
rather than weakening the paper.**

## DRIFT 4 — the brief never names the LATTICE, and §10 omits the only open decision

**§4 does not mention the coverage lattice at all**, which is now the central design parameter and
the subject of the one decision blocking the study. **§10 "Open researcher decisions" lists five,
none of them the template choice.** Its item 5 assumes a build order that Drift 2 has stalled.

## ★ DRIFT 5 — found by this check, in the CHECKER I wrote yesterday

**§5 cites `check_announcement.py:168–191` as the evidence for the superseded-DV amendment. That
module was deleted in the 2026-08-08 cleanup — so the evidence for a standing amendment in the
authoritative brief is no longer inspectable at source.** The finding survives in
`records/L7/rerouted_share_definition_v1.md`, and the brief now says so.

**AND THE CITATION CHECKER DID NOT CATCH IT.** Its pattern required a backtick immediately after
the extension, so **every LINE-RANGED citation was silently skipped** — and records cite
`file.py:168–191` far more often than the bare name. **Fixing the pattern took citations found from
201 to 287 (30% previously invisible) and live unresolved from 0 to 5**, one of them in the
authoritative brief.

**So yesterday's "UNRESOLVED IN LIVE DOCS 0" was true of what the checker looked at and false of
the tree** — which is the same defect the tool exists to catch, in the tool, found by a check run
for another purpose entirely. **The end-to-end control added yesterday could not have caught it:
it proves the verdict can fail, not that the scan looks at everything.** *A control shows the path
can fail; it does not show the path is complete.*

All five now resolve or carry an in-place marker; the brief's is annotated as
**evidence-deleted**, not silenced.

---

## What this check does NOT establish

It compares the brief against the current design and code. **It does not verify the brief's
§3 novelty claims against the literature** — that was L4's original scope in part and is not
re-run here. Drifts 1, 2 and 4 are **reported, not fixed**: they change what the paper's
manipulation is, which is the researcher's call and is already in front of them with the L9
decision.
