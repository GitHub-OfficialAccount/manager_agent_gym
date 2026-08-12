# Environment-Agnostic Harness Layer — Spec v1 (2026-08-06)

_v0 → v1: incorporates the reviewer's seven fixes (three env-dependencies un-smuggled, two interface
gaps, R7 split, R8 added) and RE's five weakenings ((a)–(e) below). v0 is in git history at 0532df1.
Owner: lead-scientist._

## 1. The environment interface (what any env must provide)

- **E1 — Workflow**: a task DAG with dependencies, standing task DESCRIPTIONS reaching worker
  prompts, persistent artifacts, and at least one producer→consumer JOIN where method mismatch has
  downstream consequences. *Compliance is checked against the JOIN's implementation, not its
  existence*: a join computed by a deterministic extractor makes downstream error a TOOL property
  (§77e / CHECK-3) and satisfies E1 only formally. **DS's join requires this explicit check before
  DS is assumed compliant as a replication env.**
  Staleness FORMS are env-specific and must be declared: *by-inaction* (static text, byte-identical
  assertion — DS-like) or *by-authorship* (a predecessor-authored artifact such as a handover
  document — IR-like). Both are staleness-by-succession; the logged assertion differs.
- **E2 — Computable ground truth, SCOPED**: two-method truth (predecessor's and successor's) is
  required **only on the task family the perturbation touches**; single truth elsewhere; judge- or
  rubric-scored secondary outcomes are permitted. No-LLM-judge applies to the GATE criterion and the
  perturbation family only. (As-written v0 was stricter than the DS env itself — RE (a),(b).)
- **E3 — Workers**: LLM agents with identities, cards, by-product declaration conventions.
  *Statelessness is a SCOPING DECISION (commitment-level): stable while "study 1 uses stateless
  workers" holds; it excludes within-shift memory and evaporates under the learning-teammate
  horizon.* Toolsets are a BUILD OBLIGATION, not a selection criterion (RE (d)).
- **E4 — Open process**: join/leave/replace schedulable per timestep (exists:
  `schedule_agent_add/remove`, wired in run_examples.py:117-128; stock scenarios ship native
  timelines, two with removes). Arrival rendered into the manager's observation (the §116 build
  item). Roster event = arrival announcement; card state = separate channel.
- **E5 — Manager**: assign / refine / message / observation incl. roster + artifact previews (free).
- **E6 — Comparability unit** (promoted from O1): a repeated, interchangeable pairing unit whose
  SIZE IS STABLE enough for allocation shares to be comparable — **an env with no such unit fails
  the primary DV, not just the estimator**. DS: task batch (3/episode — pairing power note: fewer
  units per episode must be made up in seeds). Candidates: custodian (eDiscovery), affected system
  (IR), production lot (recall).

## 2. The event (fixed across envs; shape is an imposed simplification)

One-for-one replacement at t_swap (predecessor removed + successor added, NEW `agent_id`).
*One-for-one with constant n is OUR simplification for measurement — not every scene's natural
event shape (IR's native form is whole-shift rotation); the spec says so rather than presenting it
as the scene's minimum.* Successor differs by method substitution: **allocation-visible**,
**trace-distinguishable** (tool signature and/or truth value; `actor_id` free second signature),
**successor-reachable**. Descriptions/cards stale by succession only, per the env's declared
staleness form, asserted in logs.

## 3. Channels (IVs)

C1 card (predecessor's-on-file vs updated); C2 declaration (present/absent); C3 ask (ride-along;
manager-addressed reply = manipulation; truthful/stale/mute later); C4 trace (post-hoc substrate;
no operand normalisation). Control: no-channel. Roster arrival held constant across cells.
**At SELECTION time, in-scene referents are required for C1–C3 only; C4 is assessed when the
substrate exists** (RE (c)).

## 4. DVs, estimator, discipline

Primary: allocation margin over E6-unit/task denominators at constant n (a size-changing variant
invalidates cross-variant share comparisons). Estimator: arm-paired on (seed, E6 unit); within-run
pre/post descriptive only. Secondary positive-only: ask propensity, refine reachability. Attention
layer. Four logging records + comparability checklist as logged assertions. Claim discipline per
FOUNDATION §5.

## 5. The gate (per environment)

2 SSRs, flash, clean pair, successor-arm descriptions method-consistent. PASS = (i) ≥1 correct
post-swap output demonstrably via the successor's method (truth-match on the perturbation family);
(ii) ≥1 post-swap task assigned to AND executed by the successor id. Power limit stated. Study cell
1 = info-absent cell = allocation-visibility gate. **O3 is a live budget decision: Tier-1 workflows
are 25–40+ tasks → est. 30–45 min/SSR (extrapolated, unmeasured) — either trim the candidate DAG to
the measured spine or re-anchor the run budget; the 20-min self-serve line will not cover new-env
gates as-is** (RE (e)).

## 6. Selection criteria

R1 native churn (the event belongs to the scene's story — noting shape-match to one-for-one matters,
not just churn's existence); R2 truth manufacturability (scoped per E2); R3 consequential join with
an in-scene name; R4 in-scene referents for C1–C3; R5 build cost; R6 run cost/episode length;
**R7a CONTROLLABLE confounds** (hold-and-log — a logging requirement) vs **R7b STRUCTURAL confounds**
(inherent to the scene — a validity threat that can disqualify); **R8 sourceability: the scene's
realism claims must be sourceable at full length (P6 applies to scene claims); an unsourced
candidate is UNRANKABLE, visibly**.

## 7. Open questions

O2 RESOLVED against naturalness-of-seeding in eDiscovery: EDRM documents second-level review and
random sampling, not planted known-answer documents ("seed set" in TAR = training data — a different
object). Labeled document sets exist in the scene's toolchain (TAR seed/control sets), so seeding is
a DEFENSIBLE INSTRUMENT, but it may not be claimed as scene practice. O3 see §5. O4 cells per env
for study 1 (primary full grid; replication subset TBD). O5 RESOLVED: DS complies with the §8
FOUNDATION delta + ~0.25d timeline wiring + the E1 join check flagged above.
