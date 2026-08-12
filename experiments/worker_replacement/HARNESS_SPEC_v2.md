# Environment-Agnostic Harness Layer — Spec v2 (2026-08-06)

_Supersedes `archive/HARNESS_SPEC.md` (v1) in content; v1 is retained unedited per the no-overwrite
convention. RE draft at 5f37f42; **lead's final pass applied** — §134 fold-in (three-assertion
fabrication detector, knob-disclosure rule, admission criterion) and the study-1 cell grid
(§8). Owner: lead-scientist._

**What changed from v1:** the measurement hierarchy inverted (§122–125), worker
differentiation became coverage-based (§132), CBS and the three-tier test became standing
requirements (§128–129), the fabrication detector and knob disclosures landed (§134), the
admission criterion was adopted with two adaptations (§134), and the study-1 cell grid was
added (§8).

Everything study 1 measures is defined independently of any environment, so environments are
pluggable and multi-env replication is a configuration change rather than a redesign. The
current pair is **finance (env-1)** and **record linkage (env-2)**.

---

## 1. The environment interface

- **E1 — Workflow.** A task DAG with dependencies, standing task DESCRIPTIONS (text that
  reaches workers' prompts), and persistent artifacts. At least one producer→consumer JOIN
  where method mismatch has downstream consequences. **The join is excluded from the primary
  score** and kept as mechanism evidence (§4.4).
- **E2 — Computable ground truth.** Every output in the perturbation family objectively
  scoreable **without an LLM judge**, with the truth under each method computable per unit.
  Scoped per v1's adopted weakening: two-method truth on the perturbation family, single
  truth elsewhere; no-judge required for the gate and the perturbation family, rubric-scored
  secondary outcomes permitted.
- **E3a — WORKERS ARE NOT SCRIPTED (researcher directive, 2026-08-09 — standing, overrides
  any prompt convention below).** A worker is told its SITUATION, never its PROCEDURE:
  what it is approved for, what data it holds, what the task is. It is NOT told which
  method to use, and NOT told it must always produce a number. Falling back, handing the
  task back, saying it cannot price the unit, asking — all are FREE CHOICES the study
  OBSERVES; none is prescribed and none is forbidden. Consequence for S10's numbers: the
  0% decline rate is an ARTEFACT of the current prompt ("always produce a number"), not a
  property of the workers, and the 42% is compliance-relative rather than behavioural —
  both are re-measured once the prompt states the situation only. Consequence for
  scoring: a non-answer must remain scoreable (S9 already logs missing → 0 explicitly),
  and refusal/handback are OUTCOMES to report, never failures of the harness.
  **KEEP THE SETUP SIMPLE (same directive).** Complexity added to defend a measurement
  is itself a threat: prefer removing an affordance over adding a rule. Every knob,
  cap, and constraint must justify itself against this at the regeneration — the
  candidates to re-examine are the tuned rating selection (divergence maximisation),
  the layered generator knobs, and anything that exists only to make a number come out.
  **SIMPLIFICATION RULINGS (2026-08-09, from measured counterfactuals — net removal):**
  · **Rating PENALTY maximisation: REMOVED.** RE's offline counterfactual over 20 seeds —
    tuned spread median 0.2388 vs untuned 0.1854, cost 1.29×, and 0 of 20 fall below the
    gate floor. It buys 29% more effect, is not load-bearing for admissibility, and (RR's
    K3 point) widening divergence enlarges the clip region where the execution term
    cannot penalise fabrication. Removing it makes the effect smaller AND the instrument
    sharper.
  · **Rating CLIP-AVOIDANCE: KEPT** — distinct mechanism, and the distinction is
    principled: it excludes ratings whose fallback scores zero, which protects a
    measurement (a clipped unit is blind to the failure mode the probe exists to detect)
    rather than inflating one.
  · **K2 (min_successor_routed): REMOVED as an effect knob** — measured FLAT across
    k=1..4, so it gated admission and moved nothing: disclosure burden and instance
    rejection for no measured benefit.
  · **K5 (shared-class mix): KEPT as a disclosed SCENARIO choice** — a portfolio's class
    mix is a real business fact that differs between banks, so choosing one is choosing a
    scenario; choosing each unit's RATING to maximise the method gap is not a scenario any
    bank exhibits. Condition, because the ruling otherwise flatters us: the **neutral-mix
    ceiling is reported alongside the chosen-mix one**, so a reader sees the effect
    without the scenario choice.
  · **Capacity cap: KEPT**, and the E3a tension is recorded as CONSIDERED, not assumed —
    an agent that cannot start a fourth unit is the WORLD constraining it, not us
    instructing it. What must go is any prompt clause forbidding refusal, not the
    constraint itself.
  **PROBE RE-RUN reports THREE things (RR's design, adopted):** the bucket distribution
  under situation-only prompting (decoupled from our instruction); the REALISED
  guess-vs-fallback score comparison on actually-fabricated values (measurement replacing
  LS's stand-in arithmetic, free — the probe generates exactly that data); and the
  round-PD subset SEPARATELY, where the coincidence exposure and the guess-model charity
  converge.
  **LADDER RE-DERIVED (RR, retirement branch WITHDRAWN by its author):** ≤15% clean ·
  15–35% report rate AND variance per cell · >35% a COSTING consequence (n roughly
  doubles), never a retirement. Fabrication does not bias the estimand — it inflates σ,
  the one currency this design is short of. Surviving rung, and it HARDENED: a
  fabrication rate differing BY CELL is now a VARIANCE confound (unequal-variance arms
  break the pooled-σ assumption), which is harder to detect and correct than the mean
  confound it replaced.
  **LS's 0.72-vs-0.73 arithmetic is downgraded by its own caveat (RR's attack, accepted):**
  it assumes RATING-CONDITIONED guessing, which is the charitable case and is concentrated
  exactly on the floor-pinned round PDs already flagged; a rating-unaware fabricator does
  far worse, widening spread and pushing σ UP — against LS's own conclusion. At n=6,
  "better on three, worse on three" supports **"no evidence of a free pass"** and NOT
  equality.
  **POST-RULING CEILING, MEASURED (RE, 12 seeds, zero API — a WAYPOINT, computed with the
  CURRENT scorer where truth = ASRF(public pd); every figure moves under (B′) in a
  direction nobody has measured):** removing the penalty tuning costs ~20% of the ceiling,
  0.1434 → **0.1146 median (band 0.057–0.149)**, and no seed of 12 reaches the provisional
  MDE of 0.20. **K5 PASSED ITS CONDITION CLEANLY**: once the tuning is gone, choosing the
  mix buys +0.012 (0.1029 → 0.1146) — a scenario choice worth about a percentage point,
  not a device holding the result up. That is exactly what the condition was written to
  surface, and it could not have been said before the condition forced the measurement.
  **THE HONEST FRAME IS COST, NOT DEATH** (0.20 is a threshold derived from an IMPORTED σ,
  which the pilot exists to replace): seeds per cell scale as (σ/effect)² —
  at effect 0.115, **n ≈ 8 per cell at σ=0.08, ≈ 13 at σ=0.10, ≈ 22 at σ=0.13, ≈ 29 at
  σ=0.15** (48–175 episodes over six cells; ~25–90 h sequential, ~6–22 h at four-way
  parallelism). The pilot's measured σ picks the row. Under (A) the ceiling additionally
  scales by the measured ~58% obedience factor → ≈0.067, dead twice over.
  **THE COST CURVE IS OPTIMISTIC IN FIVE NAMED WAYS — all corrections accepted; four push
  n UP, one down, they do not cancel.** (RE) *Pairing may halve it*: the curve is unpaired
  two-sample, but §4.4's estimator is arm-paired, so if instance variance pairs away n
  drops to ~4/6/10/13 — NOT bankable, since CHECK-2 found within-seed nondeterminism
  dominant on 10 of 12 DVs, i.e. much of σ survives pairing; the pilot measures σ AND σ_d
  at no extra cost. (RE) *Multiplicity*: five comparisons against control at 5% gives
  ~23% family-wise error; Bonferroni raises n ~40% (27→38/cell at σ=0.15). **RULED: ONE
  PRE-REGISTERED PRIMARY CONTRAST — all-channels vs control — everything else SECONDARY
  and reported as such.** Costs nothing, decided before the pilot rather than after.
  (RR) *Every n on the curve is a FLOOR*: the ceiling is ignorant-vs-oracle while the
  realised contrast is informed-vs-cell-0, both strictly interior. (RR) *Median ≠ pooled*:
  the suite spans 0.057–0.149 and low-ceiling instances contribute noise without signal,
  so n must be computed against the effect actually pooled — report both, and any
  exclusion of low-ceiling instances is itself an admission decision requiring disclosure.
  (RR) **The big one — effect HETEROGENEITY is a second variance component the curve set to
  zero**: a per-instance effect ranging 0.057–0.149 IS variance in the paired contrast, on
  top of within-instance σ, plausibly comparable in size — which roughly doubles the
  relevant variance and lifts every row again. **The pilot therefore measures FOUR things,
  not one: σ, σ_d, between-instance effect sd, and the effect under (B′).** Only one of
  them is currently guessed at.
  **PRIMARY-CONTRAST CONDITIONS AND ALLOCATION (RR, adopted).** (i) Cell 4 vs cell 0 is an
  EXISTENCE claim — *whether any combination of channels moves allocation* — NOT the
  §1 question *which* sources do. Those are different sentences and only the first is
  powered; the abstract may not let the primary's significance carry the question's
  phrasing. (ii) The single-channel secondaries are UNDERPOWERED-BY-DESIGN and pre-labelled
  so: a null on the card cell means "we could not have detected it", never "the card does
  not matter". (iii) **A NULL ON THE PRIMARY IS A REPORTABLE FINDING, pre-committed now**:
  cell 4 is the most-informed cell available, so if no combination of card, declaration and
  ask moves allocation against control, that is a substantive result about manager agents
  and information channels — not the study failing. (iv) **UNEQUAL ALLOCATION follows from
  the ruling rather than sitting beside it**: equal fifths give the primary n = N/5 per arm
  while funding secondaries we have just demoted; 30% each to cells 0 and 4 and 13.3% each
  to 1–3 gives the primary n = 0.3N — 1.5× the episodes, ~18% smaller detectable effect
  (MDE ∝ 1/√n), which is a meaningful fraction of the 0.115-vs-MDE gap we are fighting over.
  The cost falls on claims we are not making. LS note on scope, for the researcher: this
  buys the existence claim at the price of the which-channel decomposition, which survives
  only as exploratory point estimates — an acceptable trade while the effect is marginal,
  and one to revisit if the pilot's σ comes in low.
  **THE PAIRING AND HETEROGENEITY CORRECTIONS ARE ONE COUPLED QUESTION, NOT TWO
  INFLATORS (RE, measured — and neither correction captured this alone).** Post-ruling,
  24 seeds: ceiling share mean 0.1094, **sd 0.0254 (CV 0.232)**, median 0.1108, range
  0.0566–0.1565. So RR is right that the component is non-zero and my curve was wrong to
  set it to zero — but the "roughly doubles the variance" magnitude holds ONLY under
  effective pairing: at σ_within ≈ 0.15 the total is √(0.15² + 0.0254²) = 0.152, i.e.
  heterogeneity adds ~1.4%, not a doubling; if pairing drives σ_d down toward 0.03,
  heterogeneity becomes comparable or dominant. **Effective pairing shrinks σ_d AND
  promotes heterogeneity to the leading term — the two corrections push in opposite
  directions and partially self-cancel.** Pilot design consequence: σ_d and heterogeneity
  are ONE question with a measured prior on one side, which makes the pilot cheaper to
  specify, not dearer. RE's limiting caveat, load-bearing: this is the spread of the
  CEILING (headroom), not of the realised EFFECT; it transfers only if realised effects
  scale roughly with headroom — plausible, untested, so it enters as a PRIOR, never a
  result. Also quantified: **3 of 24 seeds sit below 0.08 ceiling**, the low-ceiling
  instances RR flagged as pulling a pooled estimate below the median.
  **FREE PRE-PILOT MEASUREMENT (RR):** between-instance effect sd is estimable NOW from the
  existing 12–40 seed sweeps, since per-instance ceilings are already computed offline. It
  bounds rather than equals the realised value, and it costs nothing — have it before the
  pilot, not only after.
  **THE DENOMINATOR FAMILY IS STRUCTURAL, NOT CARELESS — THREE INSTANCES, EACH INSIDE THE
  FIX FOR THE LAST (recorded 2026-08-09).** (i) 0.1018 was correct arithmetic on a K5
  sweep row rather than the suite — fixed by making the figure carry its own `n` and
  `source` at the PRODUCER, so it could not be re-sourced by a later reader. (ii) That fix
  did not stop the POPULATION being swapped underneath the same value: generated-40 vs
  admitted-34, same function, same number, second way to be wrong about what it describes,
  and invisible to the fix for the first. (iii) RE's first implementation of THAT fix used
  the GATE's "admitted" (condition 2 alone) instead of full three-condition admission,
  which would have returned 40 of 40 — reporting one population twice while appearing to
  report both, and passing review as "both populations reported". RE's diagnosis, adopted:
  **"'admitted' reads as a single obvious thing right up until you notice it has three
  conditions and you used one."** The general form: a denominator error is not a slip in a
  number, it is an unexamined assumption about WHICH SET the number describes — so each
  fix closes one route and leaves the others open. Consequence for practice: below-MDE is
  asserted on BOTH populations rather than inferred from the subset relation, because **a
  fortiori is a reason to EXPECT a result, never a substitute for CHECKING it.**
  **⛔ THE STALE CARD IS STRUCTURALLY TOOTHLESS UNDER THE S6 TEMPLATE — LS DEFECT, LS
  TEMPLATE, VERIFIED ON ALL THREE STUDY INSTANCES.** The C1 manipulation cannot bite,
  and the reason is the template's own guarantee. Measured (seeds 23/3/36, identical
  pattern in each): the successor is uniquely needed post-swap on the SHARED class, and
  the shared class is on the predecessor's card BY DEFINITION OF SHARED — so **the stale
  card is CORRECT about exactly the units where the successor is required**. Its two
  errors are both free: the FALSE POSITIVE names the predecessor's sole class, which
  post-swap has **0 holders** (everyone falls back, so routing there costs nothing); the
  FALSE NEGATIVE omits the successor's non-shared class, which post-swap has **2 holders**
  (someone else can do it, so missing it costs nothing). **A card-following manager and a
  card-ignoring manager route identically.** This fully explains RE's observation that
  stale-card cells route as well as updated-card cells (6/7, 6/6, 3/3 vs 7/7, 4/4) —
  neither "the manager ignores the card" nor "sampling accident", but structure. Provenance
  is mine: S6's template was designed so the successor is strictly required VIA the shared
  class, and that very property makes the stale card accurate where it matters.
  **REPAIR — LS's first version was WRONG and RE corrected it: the defect is in the
  DESIGNATION RULE, not the lattice, so a template change alone leaves it in place.**
  `_designate_swap_pair` SEARCHES for a class covered by exactly two workers and
  designates those two as pred/succ regardless of template order — RE ran LS's proposed
  lattice through the generator and it produced a shared pair and the same toothless
  structure. And that rule is not incidental: it exists to make the arrival load-bearing
  (S5's assertion-3 fix, after an inert first version). **So the real coupling is
  "successor load-bearing VIA A SHARED CLASS" ⟹ "stale card correct on the load-bearing
  class" ⟹ C1 toothless.**
  **THE REPAIR IS THREE COUPLED CHANGES (RE, verified):** (1) LATTICE; (2) DESIGNATION
  RULE — make the successor load-bearing on a class the predecessor NEVER HELD; RE found
  a satisfying designation in the proposed lattice (`pred={mdb,retail}`,
  `succ={bank,sovereign}`: succ uniquely required post-swap on sovereign, sovereign ABSENT
  from the stale card so a card-following manager withholds it and MIS-ROUTES — the bite
  C1 needs; mdb uncovered post-swap so interior spread survives; NO shared class);
  (3) SEGMENT MIX — the mix currently gives extra segments to the SHARED class because
  that is where the strictly-required set lived (RR's F2), so it must now target the
  SUCC-ONLY class or the strictly-required set collapses to ~1 and F2's sub-MDE problem
  returns while C1's is fixed. Plus a SCHEMA change: `swap_shared_class` RETIRES, since
  the pair no longer shares anything — it is published in the event block and checked for
  suite uniformity in S6, so both go. In the estimate, not discovered during it.
  **THE RULE THIS DEFECT EARNS (RE's sharpening, and it is the general form):** every
  check we built asked whether the manipulation was PRESENT and CORRECTLY CONSTRUCTED —
  non-nestedness, interiority, strict requirement, byte-identical inheritance, one
  residual — and **none asked whether it could still MISLEAD. A channel can be perfectly
  implemented and carry no information, and "correctly built" was the property we kept
  verifying.** Required henceforth: for every manipulated channel, an assertion that a
  consumer FOLLOWING it would behave differently from one IGNORING it — the manipulation's
  content, not its construction.
  **THE DISCRIMINATING FRACTION IS NOW A PUBLISHED PER-INSTANCE PROPERTY (LS ruling on
  RE's measurement — the quantity this build never asked for and most needed).** Across
  the three study instances, post-swap roster: **WHO YOU ROUTE TO MATTERS ON ONLY 14 OF 27
  SEGMENTS (52%)** — on the other 13 every post-swap worker scores IDENTICALLY, so there
  is nothing for any channel to inform. Where it does matter the gap is real (median
  0.218, max 0.544), so the design is not degenerate. The ceiling captures this only in
  AGGREGATE (if nothing discriminated, ignorant = oracle and the ceiling would be 0) and
  never shows the FRACTION — which is the quantity that says whether the manager had
  anything to get wrong. Required: fraction published per instance beside the ceiling, and
  reported for the staffed-AND-DISCRIMINATING subset, which is the number that decides
  whether this is a MANAGER finding or a GENERATOR one. **And it is the actionable half:
  the discriminating fraction is a fixable generator property; "managers do not mis-route"
  is not.**
  **TWO LS ERRORS CORRECTED BY RE, both against me, one making the problem worse.**
  (i) I wrote "allocation-loss-on-staffed is ≈0". It is **EXACTLY ZERO** — RE decomposed
  it into positive and negative parts, because a near-zero net could have hidden
  offsetting components and would have made my inference unsafe: positive part **+0.0000
  over 0 segments**, negative −0.6248 over 8. **Across 8 episodes and ~57 staffed
  segments the manager NEVER ONCE routed a staffed unit worse than the oracle's choice.**
  The channel-sensitive component is not small, it is EMPTY. (ii) I wrote "essentially all
  regret is failure to staff" — wrong: it is 61.6% non-routing AND 41.7% EXECUTION, and
  execution loss is ALSO channel-insensitive (worker fidelity, what an assignee did with a
  unit it held, which no card, declaration or ask can touch). **So: two large
  channel-insensitive components and one empty channel-sensitive one** — worse than my
  version, not better. (iii) Also flagged by RE and NOT to be put to the researcher as
  established: *"channels cannot plausibly affect staffing"* is an ASSUMPTION of mine, not
  a result. Partly testable here — unstaffed by cell is U [3,2] against swapped
  [1,1,1,1,2,1], suggestive that the SWAP drives staffing rather than the channels, at
  n=1–2 per cell and claiming nothing.
  **CEILING CRITIQUE SHARPENED (RE):** oracle − E[ignorant] measures the value of knowing
  WHO to route to. If managers never mis-route when they route, the ignorant baseline is
  not the operative counterfactual — observable headroom is bounded by MIS-ROUTING, and
  mis-routing measures zero. **The ceiling is not merely optimistic; it measures a
  quantity the observed behaviour does not produce.**
  **CORRECTION AT df=6 TO THE df=2 INTERIM — the SPREAD claim does not survive, and it is
  the half LS adopted over his own framing (RE, self-corrected before the final report).**
  df=2: full σ 0.1310 vs staffed-only 0.0995, gap +0.0315, read as "24% of the spread is
  the unstaffed component". df=6: **full 0.0990 vs staffed-only 0.1051, gap −0.0061 —
  REVERSED and essentially zero.** RE's own verdict: a percentage should not have been put
  on a two-degree-of-freedom estimate even with the df labelled. **MECHANISM, checked
  rather than guessed: the two components are ANTI-CORRELATED at r = −0.42** because they
  partition the same nine units — more unstaffed means fewer staffed units on which to
  accumulate execution loss — so full-regret σ is NOT staffed-only σ plus independent
  unstaffed noise, and **no gap should have been expected in either direction**. What
  SURVIVES: reporting σ twice, and staffed-only as the sizing figure — because it is the
  variance of the quantity a channel could move, regardless of which is larger. What is
  RETIRED: that the GAP measures how much the DV is about stalling. The anti-correlation
  confounds it.
  **AND THE LEVEL SPLIT MOVED — EXECUTION LOSS IS NOW THE LARGEST SINGLE COMPONENT.**
  df=2: non-routing 61.6% / execution 41.7% / allocation −3.3%. df=6: **non-routing 51.6%
  / execution 51.3% / allocation −2.9%.** So the biggest driver of regret is WORKERS
  PRODUCING WRONG NUMBERS ON UNITS THEY HOLD — neither the manager's routing nor its
  failure to route. Same conclusion by a different split (both large components are
  channel-insensitive), with the emphasis moved from "the manager stalls" to "the manager
  stalls and the workers are inaccurate, in roughly equal measure". Mis-routing remains
  EXACTLY ZERO on staffed-and-discriminating units and has not moved.
  **SEPARABILITY ANSWERED — A BAND EXISTS, SO THE 100% FALSE-POSITIVE RATE IS A TOLERANCE
  ARTEFACT, NOT AN ENVIRONMENTAL LIMIT (RE, retracting their own "cannot be fixed by
  tuning" and LS's "the tool repairs the instrument").** Covered relative error vs IRB
  truth, n=52: min 0.000, **p25 0.001, median 0.038**, p75 0.482, max 0.947. Uncovered
  n=6: min 0.179, median 0.590, max 1.000. Band search: 5%–15% classifies **60% of covered
  as faithful with 0/6 false-faithful on uncovered**, and the PLATEAU IS FLAT across that
  range, so the threshold is not perched on a knife edge. **The finding underneath: covered
  workers are NOT bad at ASRF — a quarter land within 0.1%, median 3.8%.** RE's S10 claim
  ("in-head ASRF cannot hit six significant figures") is TRUE at 0/52 and was letting an
  implication ride that the computation was poor. It is good to two or three significant
  figures, and the identity tolerance was discarding all of it. **"27% within 0.1%" and
  "52 of 52 failed" describe the same data.**
  **WHAT TUNING CANNOT FIX:** the upper half of the covered distribution (p75 0.482, max
  0.947) overlaps the uncovered range entirely — **~40% of covered workers are genuinely
  indistinguishable from fabricators by value alone, at any threshold.** So the compute
  tool is **ONE OF TWO ROUTES, not the only one**: a band recovers 60% today at zero cost
  from committed data; the tool's residual detector value is the other 40%, moving the
  tail down rather than relabelling it. Weaker than the argument LS carried to the
  researcher, and retracted before it could support a regeneration.
  **THE CAVEAT THAT BOUNDS ALL OF IT: THE UNCOVERED SAMPLE IS SIX.** The zero-false-
  positive column rests on six observations and collapses to 3/6 at a 20% band. RE will
  not set a band on n=6 and neither will I — it is the same shape as their df=2 spread
  claim, which LS had already carried onward. And the S10 probe's 10 fabrications CANNOT
  supply a better sample: those trials ran pre-R1, where truth was ASRF(public pd) and the
  instances differ under the same seeds, so they are not scoreable against current truth
  (RE checked rather than assumed). A re-run of the out-of-coverage arm (~24 calls) would
  supply it. **LS SEQUENCING RULING: that re-run does NOT happen now** — if the C1 repair
  regenerates, both distributions must be re-measured on the new instances and a band set
  today is throwaway. The band is measured AFTER the regeneration, on regenerated
  instances, with an adequately-sized fabricated sample, and it remains a PRE-SCORING GATE.
  **★★ RETRACTION (supersedes the entry immediately below, which was written before the
  decisive check and is WRONG in its conclusion). THE DESIGN-FAILS-ON-EFFECT CONCLUSION IS
  WITHDRAWN. RR's escalation was correct; my defence of the conclusion was not.** RR pressed
  past their own refuted mechanism to ask the right question — is "assigned and never ran"
  a manager behaviour (capacity over-assignment) or an instrument setting (horizon
  exhaustion)? — and required the answer before shipping. Measured on all 18 bundles:

  - **Every one of the 22 has a REAL `assigned_agent_id` on the board** (w_3330c6, w_e350ed,
    w_4f4d0d, …). The manager DID assign them. **The `allocation` field records
    `__unstaffed__` for all 22 — it disagrees with the board.** `allocation` is derived from
    COMPLETIONS, not assignments, so it reports "nobody was assigned" for work that was
    assigned to a named worker. **This is a scorer defect and it is the reason the whole
    question stayed invisible: the field the split is computed from cannot see assignment.**
  - **The horizon was NEVER binding.** Last segment completion lands at t5–t15 against
    H=22 — 7 to 17 timesteps of slack in every episode. Horizon exhaustion is refuted.
  - **The assignee was OVER the C=3 cap for 20 of the 22**, and per-episode
    `excess_over_cap` equals `n_unstaffed` EXACTLY in 16 of 18 episodes. The manager put
    4, 5, or 6 segments on ONE worker while roster workers sat with spare capacity — in
    three cell-U episodes a rostered worker got **zero** segments while 2–3 went unrun.
  - **`max_concurrent_tasks_per_worker = 1`.** Workers are SERIAL. The engine fired
    `assignment_deferred` **580 times** across the study, and **the manager's observation
    contains no signal of it whatsoever** — zero occurrences of defer/capacity/concurrent/
    queue/busy in its context. At its FINAL timestep the manager sees those segments as
    `Status: ready, Assigned to: <worker>`, which reads as "handled", for 22 timesteps.

  **Honest label: ASSIGNED-BUT-SILENTLY-DEFERRED-PAST-THE-HORIZON** — not non-routing, not
  parse failure, not horizon exhaustion. **Consequences: (1) the 48.3% term is NOT outside
  channel reach** — over-concentration is an allocation behaviour and a coverage channel
  could plausibly move it, so the "movable quantity ≈ 0" argument loses its largest premise.
  **(2) My sentence "only the first is plausibly channel-sensitive" is not merely unargued,
  it is probably FALSE** — and it comes out. **(3) The DV's dominant component is compounded
  with a harness observability defect**, so effect-size conclusions cannot be drawn from this
  run at all. **(4) The capacitated oracle SURVIVES** — C=3 is achievable (every maxload=3
  episode finished with 0–1 unstaffed), so the oracle's feasible set is real and the
  denominators stand. RE owes: the `allocation`-vs-board fix, and a decision on whether
  deferral becomes observable to the manager (it is a design question, not a bug fix —
  an invisible deferral may be a legitimate thing to study, but it cannot be silently
  folded into a routing metric).
  **★ MY "A ROSTERED WORKER GOT ZERO SEGMENTS" CLAIM IS FALSE — CORRECTED. It reached the
  researcher and it is retracted here.** RE's denominator reconciliation exposed it: I applied
  the POST-SWAP roster uniformly, which is right for cells 0–4 and WRONG FOR CELL U, whose own
  roster carries no swap. Verified directly — in all three cell-U episodes the zero-load
  "rostered" worker (w_3330c6 / w_e350ed / w_002c52) **was never present in the run at all**
  (`ran anything? False`). `roster_post_swap` is a COUNTERFACTUAL field for cell U, not its
  roster; the operative roster includes the predecessor, who is still there. So no worker was
  ever handed nothing — the worker I was pointing at was not on the team.

  **WHAT IS TRUE, AND IT IS TIGHTER THAN WHAT I CLAIMED.** Among the workers actually holding
  segments in cell U, spare capacity equals unstaffed work EXACTLY:

  ```
  cellU_seed23   spare slots 3   unstaffed 3
  cellU_seed3    spare slots 2   unstaffed 2
  cellU_seed36   spare slots 2   unstaffed 2
  ```

  The manager piled 5–6 onto the predecessor while two PRESENT workers had exactly enough room
  for the overflow. That is the same finding without the false detail, and the exact match is
  better evidence than the anecdote was. **Cells 0–4 are unaffected** — `roster_post_swap` is
  their real roster and every "spare capacity" figure quoted for them stands.

  **RE'S TREATMENT IS THE CORRECT ONE and mine was wrong, by the same ruling that fixed the
  U-oracle: each cell is scored against the roster it ACTUALLY HAD.** Both denominator gaps
  (20 vs 19; 105/83/22 vs 102/81/21) trace to this one cause — three segments in
  predecessor-only classes, sole-held under a post-swap roster, covered under cell U's own.
  No figure moves; 0-of-20 and 3-of-105 both stand.

  **AND THIS IS THE CASE FOR §B, made by the rule's own authors against themselves:** the
  clause *"a covering worker exists"* lived in two different versions in two heads, with
  nothing in either implementation saying which. **A NAME — "coverage-relevant" — covered two
  PREDICATES, twice, between two people who agreed on the conclusion and had verified each
  other's arithmetic.** The predicate is now stated in the code: *"IRB-approved, assigned to a
  worker on THE CELL'S OWN roster, and at least one worker on THAT roster covers the class."*

  **★ THE 8× ENRICHMENT DISSOLVES — AND NOT THE WAY RR PROPOSED. It was POOLING TWO DISTINCT
  FAILURE MODES.** RR offered the loose end as support: the deferred set being disproportion-
  ately mis-routed (executed 1/81 = 1.2%, unexecuted 2/21 = 9.5%) is what over-concentration
  *should* produce, since overflow past the cap has fewer good options left and lands worse.
  Testable, so tested — splitting the 22 unexecuted by WHY they did not run:

  ```
  CAPACITY-REFUSED  n=20   coverage-relevant 19   MIS-ROUTED 0    0.0%
  TIMING            n= 2   coverage-relevant  2   MIS-ROUTED 2  (100%, n=2)
  ```

  **The 20 capacity-refused segments are COVERAGE-PERFECT — zero mis-routes in 19 relevant
  placements. The entire enrichment comes from the 2 TIMING segments, a different failure
  mode.** RR's mechanism predicts the overflow lands worse; measured, the overflow lands
  PERFECTLY and the mis-routes are elsewhere. **This is the opposite of the prediction, and it
  supports the surviving account more strongly than RR's version would have:** every one of
  the 19 overflow placements is coverage-correct, which is precisely *"the manager fills a
  covering worker past capacity and the constraint absorbs the cost."* **The 100% is n=2 and
  means nothing on its own** — the load-bearing number is the 0 of 19. **Fourth mechanism
  offered, fourth to die; the anomaly it was offered to explain turned out to be an artefact
  of pooling.** Do not quote the pooled 9.5% anywhere: it describes no single population.

  **★★ ANTI-CORRELATION WITHDRAWN BEFORE IT LEFT THE TEAM. RR's adversarial pass killed it and
  I am not sending it.** The entry below stands as the measurement; its INFERENCE is retracted
  here.

  **(i) ACCEPTED IN FULL, and it is the objection that ends it.** The argmax establishes a
  CONFLICT between coverage-optimality and capacity-feasibility; it does NOT establish a
  DIRECTION. The missing link is channels → manager moves toward argmax → concentration rises.
  A manager given coverage information does not thereby lose capacity information; it would
  compute the CAPACITATED optimum, not the argmax. **And RR's closing point is the one that
  settles it: two messages earlier I refused to carry a mechanism on the per-cell max-load
  table (cell 4, all channels, ties cell 0, none, at the bottom) — and then asserted the
  OPPOSITE direction from an offline construct. Declining the empirical direction and
  asserting its converse is the exact shape of both errors already retracted today.**

  **(ii) VERDICT ACCEPTED — (c) IS WITHDRAWN — BUT RR'S MECHANISM IS NOT WHAT HAPPENED, and
  the distinction matters for what we conclude.** RR proposed a selection effect: the manager
  "resolves about seven placements and abandons two", so its coverage score sits on a sample
  the deferral selected, and asked for a recomputation over all-assigned. **Measured: the
  manager made EVERY placement — 162 of 162 segments across 18 episodes carry an
  `assigned_agent_id`, none unassigned. And the recomputation RR asked for was already the
  one reported: the 3 mismatches are over all 102 coverage-relevant ASSIGNED segments,
  deferred ones included.** So there is no selection effect here and the manager did not
  abandon placements. **(c) fails for a different and simpler reason: it compares a FEASIBLE
  allocation against an INFEASIBLE one.** The optimum's ~1 mismatch per instance is THE PRICE
  OF FEASIBILITY; the manager didn't pay it because its allocation violates the constraint.
  Coverage fidelity purchased by breaking the cap is not fidelity, and **"6× more
  coverage-faithful than optimal" is not a meaningful comparison.** Withdrawn.

  **(iii) ACCEPTED, and RR's extension is the sharper half:** the three instances were
  STRATIFIED and one is the suite MINIMUM, so they are not a random draw from the suite —
  whatever magnitude the coverage-vs-capacity conflict has here is not the suite's magnitude.
  (a) and (b) are offline properties of three instances and must not share a paragraph with
  the 18 episodes, which buy nothing for them.

  **WHAT SURVIVES AND GOES TO THE RESEARCHER (RR's wording, RE's claim strengthened by (a)
  and (b), without the anti-correlation leap and without (c)):** *Coverage information alone
  cannot address the dominant error, and on these instances coverage-optimal play would
  itself violate capacity. The channels are ORTHOGONAL to the dominant loss term, and there
  is a structural reason to think they cannot become aligned with it: the input that would
  address over-concentration is LOAD, and none of the built channels carries load.*

  **ITEM 2 GOES AS A FORK, NOT A RECOMMENDATION** (RR, and I agree): **branch 1** — honest
  board, load visible, CONSTANT across cells — removes a confound and gains no effect; the
  study still has no channel addressing its largest loss term. **Branch 2** — load/deferral
  as a MANIPULATED channel — supplies a candidate channel aligned with the dominant error,
  and is arguably a DIFFERENT STUDY, since the object shifts from *what the manager learns
  about the newcomer* to *what the manager learns about its own allocation*. Branch 1 is owed
  on honesty regardless. Branch 2 is a real direction and should be PROPOSED as one rather
  than absorbed into a study built around a different question.
  **★★★ THE MEASUREMENT (inference above retracted; the numbers stand). RE proposed "this study's channels cannot IN PRINCIPLE move this
  study's dominant allocation error." I tested it rather than forwarding it, and the truth is
  SHARPER AND WORSE: the channels' information, used CORRECTLY, is what CAUSES the error.**

  **(a) COVERAGE-OPTIMAL ALLOCATION WANTS TO CONCENTRATE.** The uncapped per-segment argmax —
  i.e. pure coverage-following, "give each segment to whoever is best for it" — produces
  loads of **5/4, 5/4 and 8/1** against a cap of 3, on all three instances. Coverage pushes
  past the cap by construction.

  **(b) THE MANAGER WAS FOLLOWING COVERAGE, NOT IGNORING IT.** Across the 13 over-loaded
  workers, **54 of the 58 IRB-applicable segments piled onto them are segments that worker
  ACTUALLY COVERS**. The over-concentration is coverage-CONSISTENT behaviour, not
  coverage-blind behaviour.

  **(c) THE OPTIMUM MAKES THE OPPOSITE TRADE FROM THE MANAGER.** Avoidable coverage
  mismatches (sole-held excluded, apples-to-apples):

  ```
  CAPACITATED OPTIMUM : 1 per instance, every instance  -> ~1.0 per episode
  MANAGER             : 3 across ALL 18 episodes        -> ~0.17 per episode
  ```

  **The capacitated optimum DELIBERATELY SACRIFICES COVERAGE to respect capacity. The manager
  sacrifices CAPACITY to respect coverage — and is roughly SIX TIMES MORE COVERAGE-FAITHFUL
  than optimal play.** It is not routing badly. It is routing by the only dimension it has
  information about, and the dominant loss is the price of that.

  **CONSEQUENCE, and it is a DESIGN finding rather than a finding about managers: a coverage
  channel operating PERFECTLY pushes the manager FURTHER in the direction that produces the
  48.3%.** More coverage information is not neutral with respect to the dominant loss term —
  it is COUNTERPRODUCTIVE. RE's "cannot move it" understates this; the correct statement is
  that the channels are anti-correlated with the dominant error.

  **THIS REFRAMES THE PENDING ITEM-2 DECISION FROM A SIDE QUESTION INTO THE CENTRAL ONE.**
  Making deferral/refusal visible would give the manager LOAD information — **the one input
  that could address the dominant error, and the only candidate channel in the design that
  is not anti-correlated with it.** RR's "fix the board, leave the events out" was argued on
  honesty grounds and remains right on those grounds; but the choice now also determines
  whether the study has ANY channel addressing its largest loss term. That goes to the
  researcher as part of the same decision, not after it.

  **WHAT THIS DOES NOT ESTABLISH:** that a load channel WOULD move the error (untested); that
  the manager would trade correctly if given both (untested); and it says nothing about
  effect sizes, which remain unmeasured. n=3/cell and the concurrency block still apply to
  every per-cell number quoted anywhere above.
  **★ RR'S STRUCTURAL ARGUMENT — VERIFIED NUMERICALLY (they checked the reasoning and said
  so; I checked the arithmetic, which is the complementary half).** RR argued the conclusion
  rests on something stronger than "the number is small": post-swap the SOLE-HELD CLASS is
  covered by NOBODY, so every worker scores IDENTICALLY on those segments — they cap the
  oracle below perfect (the S6 template's purpose) but contribute **ZERO to oracle−worst**.
  Measured across all three instance seeds, scoring every segment under every post-swap
  worker:

  ```
  SOLE-HELD-CLASS      n= 4   max worker-to-worker spread = 0.000e+00   nonzero: 0
  DIFFERENTIALLY-COV   n=23   max worker-to-worker spread = 5.438e-01   nonzero: 17
  ```

  **Exactly zero, not approximately.** So the allocation-movable quantity lives ENTIRELY on
  the differentially-covered classes, and mis-routing there is **3 of 102**. That is not an
  estimate of a ceiling — **it is a COUNT OF THE EVENTS A COVERAGE CHANNEL COULD HAVE
  CHANGED, and it is three.** This also independently justifies excluding the 15 sole-class
  mismatches from check 1: where no correct choice exists there is neither a manager error
  nor a channel that could have prevented one. **The conclusion is therefore structural:
  the channels address coverage; coverage-relevant allocation events number 102 of which 3
  went wrong; the dominant error is CAPACITY, which no coverage channel names.**

  **★ METHODS FINDING, RR's precision, and it is the transferable half.** I recorded that the
  value lay in the stopping rule rather than in any diagnosis. RR's addition: **the rule
  worked because INVOKING IT WAS CHEAP.** A coincidence in a table cleared the bar because
  raising it cost one message and nobody had to be wrong for it to be worth raising. Had
  stopping been expensive — procedurally, or because an alarm implied an accusation — a
  numerical coincidence would not have justified it, and three refuted mechanisms would have
  been three reasons not to speak again. **Corollary, to be written down: A STOPPING RULE
  THAT REQUIRES THE STOPPER TO BE RIGHT IS NOT A STOPPING RULE.** RR's alarm was wrong on
  mechanism twice and the defect finally surfaced — a field derived from completions rather
  than assignments — was predicted by none of the three mechanisms. Had the protocol demanded
  a diagnosis rather than a reason to look, that field would still be in the metric.
  **★★ RR CAUGHT MY LEAN, AND THE TWO CHECKS THEY ASKED FOR SETTLE IT AGAINST ME. THE
  POSITION IS: RETRACT THE NEGATIVE, DO NOT ASSERT THE POSITIVE.** I argued to RE that "the
  study has a live effect after all." RR accepted both of my arguments against RE and then
  refused the conclusion drawn from them: what they establish is *there is a large allocation
  error and the metrics hid it*, NOT that the error is CHANNEL-SENSITIVE — and over-
  concentration is a **LOAD-BALANCING** failure while every channel in the design carries
  **COVERAGE** information. Knowing what a newcomer can do does not tell a manager how much
  it has already given someone. Both checks were free and offline.

  **CHECK 2 — max assignment load by cell. DOES NOT SUPPORT MY MECHANISM.** Load is not flat
  (3.33–5.33) but it **does not order by channel count**: cell 0 (NO channels) 3.33 and
  **cell 4 (ALL THREE channels) 3.33 — joint LOWEST**, with the one-channel cells scattered
  between at 3.67/4.33/4.67. Cell U is worst at 5.33 but has NO newcomer at all, and RE
  independently flagged that U confounds "most information about the worker" with "no roster
  change to react to". **The two cells most relevant to the prediction point OPPOSITE ways.**
  The hypothesis *"the manager concentrates on the worker it knows most about"* is NOT
  directionally supported and is not carried forward as anything but a hypothesis.

  **CHECK 1 — mis-routing recomputed over ASSIGNED rather than EXECUTED. RR's selection
  effect is REAL, and it is smaller than the framing implied.** My first pass gave 18
  mismatches / 16.3%, contradicting RE's 1-of-66 — I did NOT report that, because the
  discrepancy was the finding: **15 of the 18 were SOLE-HELD-CLASS segments where NO correct
  choice existed** (post-swap nobody covers that class — by design, it is the source of
  interior spread), which is not a manager error. Restricting to segments where a covering
  worker WAS on the post-swap roster:

  ```
  EXECUTED    n= 81   mis-routed 1   1.2%    <- reproduces RE's numerator exactly
  UNEXECUTED  n= 21   mis-routed 2   9.5%    <- the excluded set, ~8x enriched
  ASSIGNED    n=102   mis-routed 3   2.9%    <- the honest denominator
  ```

  **So the conditioning DID hide mis-routes and the excluded set IS enriched ~8x, exactly as
  RR predicted — and the corrected count is still 3.** Mis-routing triples and remains small.
  **The dominant error is capacity, not coverage, and the channels address coverage.**

  **ADOPTED POSITION, RR's wording:** *the metrics as computed concealed a large allocation
  error — the capacity shape is violated in 13 of 18 episodes and the mis-routing rate was
  measured on a denominator that excluded exactly the failures. **Whether that error is
  channel-sensitive is now an OPEN QUESTION rather than a settled negative.** The previous
  conclusion said the movable quantity was ≈0; the correct statement is that IT HAS NOT BEEN
  MEASURED.* This retracts the negative without asserting the positive, and it is the version
  that goes to the researcher.
  **★ RR'S ORACLE CHALLENGE — ANSWERED FROM CODE, RESOLVES IN THE FAVOURABLE DIRECTION, AND
  CORRECTS MY OWN "QUEUED".** RR asked whether C=3 is enforced by the engine or exists only
  in the oracle — because if only the latter, "C=3 is achievable" is evidence from 18
  episodes rather than a structural guarantee, and every regret share computed against those
  denominators becomes contingent. **It is enforced.** `CapacityBoundedAIAgent.can_handle_task`
  (`finance_env.py:158`) is consulted by the engine at `engine.py:851`. Two DIFFERENT bounds
  ride the same method: `super().can_handle_task()` enforces `max_concurrent_tasks=1`
  (SIMULTANEITY), and line 165 enforces `segment_capacity=3` as a **PER-EPISODE CUMULATIVE
  TOTAL** — `segment_task_ids` is a set that is added to in `execute_task` and **NEVER
  PRUNED**. So the oracle's feasible set matches the engine's enforced constraint exactly,
  and **the denominators are STRUCTURAL, not contingent on these 18 episodes.**

  **THE CORRECTION THIS FORCES, and it is mine:** I described the 22 as "queued" and told the
  researcher so. **They were not queued — they were PERMANENTLY REFUSED.** The log separates
  the two mechanisms cleanly and unambiguously: in cellU_seed23, `seg_03` was deferred at t2
  and t3 and then RAN (transient, concurrency-1 resolving), while `seg_00`/`seg_01`/`seg_04`
  were deferred at **every timestep from t2 to t21 — 20 consecutive deferrals to the end of
  the episode**, because their assignee had already executed 3 segments and line 165 refuses
  the fourth forever. That is why slack did not save them and never could have.
  **This STRENGTHENS the over-concentration finding rather than softening it:** the manager
  had ~19 timesteps in which the only thing that could have recovered that work was
  REASSIGNMENT, it could see the segments sitting `ready`, and it did not act. A recoverable
  allocation error left unrecovered is more squarely an allocation behaviour than a queue
  that ran out of time.

  **RR'S THREE-WAY SPLIT OF THE DESIGN QUESTION IS ADOPTED OVER MY TWO-WAY.** (1) **The board
  is FALSE, and repairing it is a DEFECT FIX, not a channel** — it renders `Status: ready,
  Assigned to: <worker>` for a task that is permanently refused, which does not omit
  information but ASSERTS A WRONG ONE, since "ready + assigned" reads as *handled*. RR
  retracted their own S8 pass ("an honest board, not a capacity channel") on the fact.
  Execution state (`not started / running / done`) happens whichever way the design question
  goes. (2) **Surfacing deferral EVENTS is the genuine design question**, and RR's position —
  fix the board, leave the events out — is better than my original "make queuing visible",
  because with execution state truthful the manager can observe over-concentration THROUGH
  ITS CONSEQUENCE and the inference remains the thing being measured rather than something we
  hand it. **I have adopted it and withdrawn my own recommendation.** (3) **Whichever is
  chosen must be CONSTANT ACROSS CELLS** and asserted in the comparability module — a
  deferral signal varying by cell would be an uncontrolled channel correlated with
  over-concentration, which is correlated with regret at r=0.93. **And the condition is part
  of the claim either way:** if deferral stays invisible the finding is *"managers
  over-concentrate under a load-feedback blackout"*, which belongs in the sentence, not the
  limitations.
  **★ SUPERSEDED ENTRY (kept per no-overwrite; its conclusion is retracted above):**
  **RR'S UNSTAFFED==UNREADABLE ALARM: THE COUPLING IS REAL, THE DIRECTION IS INVERTED
  (LS verified directly on all 18 bundles before defending the conclusion).** RR found
  `n_unstaffed` == `n_unreadable` exactly in all six cells (22 = 22) and inferred that
  parse failures were being counted as non-routing, putting the design-fails conclusion at
  risk. Measured: **all 22 "unstaffed" segments were ASSIGNED in the allocation, and all 22
  have NO DELIVERABLE AT ALL — zero produced any text.** So no worker ever executed them.
  Consequences: **(i) "non-routing" is CORRECTLY named** — those segments were assigned and
  never ran, which is a staffing failure, not a parse failure; the 48.3% term and the
  design-fails-on-effect conclusion SURVIVE. **(ii) "n_unreadable" is MISNAMED and
  inflated** — it counts segments with no deliverable as unreadable deliverables, so the
  two fields coincide because absence is double-counted, not because parse failures are
  mislabelled. **(iii) RR's derived "13.6% parse failure" figure is therefore NOT
  supported** and must not enter the record as an instrument finding: there is nothing to
  parse where there is no text. RE to confirm the field's definition and rename it
  (never-executed vs produced-but-unparseable are different populations and the honest
  three-way is **never-executed / executed-but-unparseable / parsed-and-wrong**).
  **The alarm was right to raise:** an exact six-for-six coincidence at these counts
  demanded reconciliation, and the reconciliation found a real labelling defect — just not
  the one predicted, and not one that touches the conclusion.
  **★ SCOPE RUN COMPLETE, 18/18 (eb19efd, 403 min, N=2). σ IS MEASURED IN-ENVIRONMENT FOR
  THE FIRST TIME AND IT IS FAVOURABLE — AND IT DOES NOT RESCUE THE DESIGN, BECAUSE THE
  BINDING CONSTRAINT WAS NEVER NOISE.**
  Four quantities: **σ within-cell 0.0768 (df=12) · σ staffed-only 0.0834 · σ_d paired
  0.0666 (df=10) · σ between-instance 0.0655 (df=2, against a design-side prior of
  0.0254 — read as "the prior was too low", not as a number).** Pairing buys ~13%, NOT the
  2× the coupling argument allowed for; the first half of that argument is real and small.
  **σ PREDICTIONS SCORED (all pre-committed before any pilot existed):** RR ≥0.13 —
  WRONG (high). RE 0.10–0.20, "band unstudiable" — WRONG (high). **LS 0.08–0.12 —
  CLOSEST**: full 0.0768 just below the band, staffed-only 0.0834 inside it. The reasoning
  that carried it (exact-consumption regret has many support points, and the deterministic
  DV lacks the judge-noise that inflated the imported prior) is the part worth keeping.
  **WHAT THE FAVOURABLE σ IMPLIES, AND WHY IT CHANGES NOTHING:** at the admitted-suite
  effect of 0.0988 the measured σ gives **n ≈ 10–12 per cell unpaired, ≈8 paired — about
  46–73 episodes over six cells, entirely affordable.** So the design is NOT
  noise-limited. **But the realised effect is not the ceiling: mis-routing is 1 of 66 and
  allocation-on-staffed is −1.0% of regret, so the quantity a channel could move is
  ≈0.** The pilot answered its question, the answer was the good one, and the design fails
  anyway — on EFFECT, not on POWER. That is a cleaner failure than the one we spent two
  days costing, and it is the strongest possible argument that the cost curve was never
  the real question.
  **REGRET SPLIT AT 18:** non-routing 48.3% · execution 52.7% · allocation-on-staffed
  −1.0%. Execution remains the largest component. **DECLINES: 7 explicit, 22 unreadable,
  never summed — seven behaviours that were STRUCTURALLY IMPOSSIBLE under the old prompt.**
  **TWO RE CLAIMS SOFTENED AT n=18, self-recorded:** "NOTHING between 5% and 15%" becomes
  "ALMOST nothing" — 2 of 82 covered segments landed in the band (51 within 5%, 29 above
  15%, 95.1% of covered loss still above a 15% band). The bimodality holds; the
  strictly-empty claim was an n=52 statement stated as structure. Consequently the band's
  "empty region" argument is WEAKENED, not overturned: the threshold now cuts through a
  very thin part of the distribution rather than a vacuum, and remains the better of the
  two arguments for it.
  **AND A THREAD-VS-RECORD CORRECTION RE MADE ON THEMSELVES:** they had retracted the
  "σ-gap measures stalling" claim to LS and LEFT IT IN THE REPORT ARTEFACT. Now corrected
  in the module beside what survives. Same gap this project keeps finding — a retraction
  in a thread is not a retraction in the record.
  **"MIS-ROUTING IS EXACTLY ZERO" IS FALSIFIED AT 14 BUNDLES — 1 of 50, self-corrected by
  its author off the survived list.** The single case (cell 0, stale card, seed 36,
  seg_02, asset class BANK): the oracle chose the SUCCESSOR, the manager chose a worker
  without bank coverage, cost 0.4820. **And bank is the SHARED class on that seed — so by
  the structural analysis the stale card CORRECTLY stated that the successor covers bank,
  and the manager routed elsewhere anyway.** Not a card-accuracy failure: **a failure to
  ACT on correct card information**, which is evidence about card CONSUMPTION rather than
  card content, pointing the same way as stale-cells-route-as-well-as-updated-cells. n=1,
  claiming nothing about a rate. The substantive conclusion is unchanged and slightly
  strengthened: the channel-sensitive term is still essentially empty (0.48 against ~30
  total regret), and the one case populating it is **not one a channel manipulation could
  have moved, because the information was already there and correct.**
  **THIS IS NOW THE STRONGEST ARGUMENT FOR THE C1 REPAIR, and it is different from the
  one the repair was proposed on (LS).** The repair was justified as "the manipulation has
  no content". The better justification is that **it converts an UNANSWERABLE question
  into an ANSWERABLE one.** As built, an accurate stale card plus a correctly-routing
  manager is uninformative — "reads the card and follows it" and "ignores the card" predict
  identical behaviour, which is exactly the confound the current run is stuck in. After the
  repair the card MISLEADS on the load-bearing class, so the two hypotheses separate: if
  the manager still routes correctly it is NOT consuming the card (a finding, and the
  study's own subject); if it mis-routes it IS (also a finding, and the one the design
  assumed). **Either outcome is informative, which is not true of anything the current
  environment can produce.** The repair buys the ability to distinguish, not merely a
  manipulation with content.
  **⛔ THE COMPUTE TOOL IS DROPPED FROM THE REGENERATION BUNDLE — BOTH ARGUMENTS FOR IT
  HAVE COLLAPSED, EACH RETRACTED BY ITS AUTHOR (RE).** Covered execution loss by error
  band, 52 segments, total 9.771: **<1% error → 23 segs, 0% of loss · 1–5% → 8 segs, 3%
  · 5–15% → 0 segs, EMPTY · 15–50% → 16 segs, 66% · >50% → 5 segs, 31%. So 96.6% of
  covered loss sits ABOVE a 15% band.** A calculator would have to move segments from
  >15% down to <5%, and those are not precision failures — **exact arithmetic does nothing
  for a worker that used the wrong input or the wrong procedure.** The 63% target shrinks
  to the ~3% in the 1–5% band, which is the only place exactness buys anything. Detector
  argument already fell to the band existing; regret argument falls here. RE's own
  verdict, adopted: the researcher should NOT approve a regeneration on either as stated.
  **THE REGENERATION BUNDLE IS THEREFORE ONE ITEM, NOT TWO: the C1 three-part repair
  stands alone** (the card's structural toothlessness is unaffected by any of this).
  **THE EMPTY MIDDLE IS ITSELF AN OBSERVATION WORTH THE RECORD (n=52 segments, 12
  episodes, one model — observation, not finding).** The distribution is BIMODAL with
  NOTHING between 5% and 15%: 31 of 52 essentially correct (23 within 1%), 21 wrong by
  more than 15%. **Precision-limited arithmetic produces a CONTINUUM; this is TWO
  POPULATIONS.** Workers computing the Basel formula unaided either get it right to within
  1% or fail badly — there are no near-misses. What cannot be told from value alone is
  whether the failing population used a wrong input, a wrong procedure, or blundered; the
  confidentiality instruction suppresses exactly that evidence (already recorded in the
  detector's evidence scope), so RE's hypothesis that a tool might remove
  wrong-PROCEDURE as a failure mode is UNTESTED and explicitly not priced.
  **AND THE BAND GOT STRONGER, on a better argument than the one it had:** it sits in a
  genuinely EMPTY region rather than merely a flat one, so a threshold anywhere in 5–15%
  separates two populations WITHOUT CUTTING THROUGH EITHER. That is structural — it rests
  on the COVERED distribution's own shape — and it therefore survives the n=6 caveat on
  the fabricated side, which the plateau argument did not.
  **LS INFERENCE, CONFIRMED (kept for provenance):** Covered execution loss is 0.188/seg while the MEDIAN relative error is
  0.038 — so the mean is dragged by the tail, and the loss is concentrated in a MINORITY
  of badly-wrong outputs rather than in systematic in-head imprecision. If that tail is
  fabrication or gross blunder rather than arithmetic precision, **a calculator does not
  address it**, and the tool's 63% target shrinks to whatever share of that bucket is
  precision-limited. Check: the covered loss split by error decile, and what share of
  total covered loss sits above the band.
  **⛔ THE PRIMARY FABRICATION DETECTOR IS UNUSABLE ON COVERED SEGMENTS — 52 OF 52
  FLAGGED (RE, live data at 12 episodes; confirms their S10 structural prediction of 0 of
  6, now 0 of 52).** Every covered worker computing IRB in-head classifies `neither` —
  the FABRICATION class — so the detector's **false-positive rate on that population is
  100%**, and it cannot separate faithful-but-approximate from invented. Not a tuning
  problem at the current tolerance: **the tolerance is an IDENTITY test in an environment
  where identity is UNATTAINABLE.** Consequence: **any fabrication rate reported from
  covered segments is meaningless as it stands**, and the deferred band decision (S10:
  "the band is chosen by the TEAM from the measured distribution") now has its
  distribution and cannot be settled by tuning alone.
  **EXECUTION LOSS SPLIT BY WHAT THE WORKER HAD TO COMPUTE (RE, verifying LS's inference
  rather than accepting it):** IRB+COVERED (in-head ASRF) 63%, 0.188/seg over 52;
  IRB+UNCOVERED (SA fallback, one multiplication) 31%, **0.479/seg over 10 — the HIGHEST
  per-segment loss is on the SIMPLEST computation**; SA-applicable 6%, 0.033/seg over 30.
  So LS's compute-tool inference **holds for the dominant bucket and is qualified on the
  rest**: only 3 of 10 uncovered workers fell back correctly, which is the S10 fabrication
  phenomenon with numbers, and a calculator does not fix it — **it plausibly makes it
  EASIER, since a fabricated IRB becomes cheaper to produce than an in-head one.** The
  tool is well-targeted at 63% of execution loss and orthogonal-to-possibly-harmful on the
  31%. RE's qualification, not to be dropped when the argument is summarised.
  **RE'S STRONGEST ARGUMENT FOR THE TOOL, WHICH LS DID NOT MAKE: it repairs the primary
  instrument.** With a calculator, exact computation becomes ATTAINABLE, so `neither`
  recovers its meaning and the value detector becomes usable on covered segments for the
  first time. The tool does not merely shrink the largest regret component — without it,
  the detector cannot be fixed by choosing a band unless faithful-approximate and
  fabricated values are separable, which is now an EMPIRICALLY TESTABLE question (in-head
  error distribution over 52 covered segments vs the S10 probe's fabricated values) and
  must be answered BEFORE the researcher rules, because it decides whether the tool is the
  only route to a working detector or merely one of two.
  **CONSEQUENCE LS DRAWS, for the deferred compute-tool decision:** execution loss at
  ~51% is in-head ASRF fidelity — the same mechanism as "no live worker has ever matched
  at the 1e-6 tolerance". A shared compute tool, deferred at S10 to the scheduled
  regeneration precisely so it could be decided WITH data, would attack the single largest
  regret component; and because allocation is what remains after non-routing and execution
  are removed, shrinking execution raises the allocation signal's SHARE of a smaller
  total. That is now an argument with a number behind it rather than a preference, and it
  belongs in the same decision as the C1 repair since both are regeneration-gated.
  **INTERIM RESULT OF THAT RULING (8 of 18 episodes, df=2 — DIRECTION ONLY, values will
  move):** regret splits **non-routing 61.6% · allocation-on-staffed −3.3% · execution
  41.7%**, exact by construction (residual 8.9e-16). **The DV as it stood was MAJORITY a
  measure of the manager failing to staff units at all.** σ full 0.1310 vs staffed-only
  0.0995 — a 24% gap, so roughly a quarter of the spread is the unstaffed component. RE's
  sharpening, adopted: at 61.6% of the LEVEL and 24% of the SPREAD the two σ's are
  **answering different questions, not measuring the same thing more or less precisely**.
  **THE CONSEQUENCE THAT MAY BE DESIGN-LEVEL, flagged now and NOT concluded at df=2:**
  allocation-loss-on-staffed is ≈0 (indeed slightly negative). If that holds as episodes
  land, then **when the manager staffs a unit it staffs about as well as the oracle would,
  and essentially all regret is failure to staff** — a behaviour the information channels
  cannot plausibly affect, since a card tells you WHO to route to, not THAT you should
  route. The channel-effect ceiling (oracle − ignorant assignment) assumes a manager that
  STAFFS EVERYTHING; real managers leave ~17% unstaffed, so the observable headroom for
  channels is bounded by something smaller than the published ceiling, possibly by the
  staffed-only allocation loss itself. **If it holds, it is a finding about manager agents
  and a problem for this design simultaneously, and it needs a researcher decision rather
  than a fix.**
  **WHY NEGATIVE ALLOCATION-LOSS IS NOT "THE MANAGER BEAT THE ORACLE" (RE, pre-empting a
  sentence that survives one summarisation and cannot be walked back):** the capacitated
  oracle DELIBERATELY UNDER-SERVES some units to free capacity for others — measured on
  seed 3, 1 of 9, sacrificing 0.083. A manager that staffs such a unit beats the oracle's
  choice ON THAT UNIT while losing overall by failing to staff the ones the oracle was
  protecting. The term is a difference from the oracle's OWN ATTRIBUTION, not from a
  per-unit optimum; the report prints this wherever the term is negative. New scorer
  support: `oracle_allocation_capacitated` reconstructs the DP's own per-unit choices,
  because the per-unit argmax ignores capacity and cannot attribute the oracle's total
  once the cap binds — re-deriving attribution by any other rule would produce a split
  that does not sum.
  **σ MUST BE COMPUTED TWICE — FULL REGRET AND STAFFED-ONLY REGRET (LS ruling on RE's
  interim flag, before the numbers land).** Across the first 8 episodes: **1.5 of 9
  segments unstaffed on average (17%)**, every episode incomplete at 10–12 of 16 tasks. By
  the realised-authoritative rule an unstaffed unit scores 0 in the faithful term, so it
  lands in ALLOCATION loss — correctly, since failing to staff IS an allocation failure.
  But that puts **two behaviours in one term: MIS-routing (staffed the wrong worker) and
  NON-routing (never staffed it at all)**, and only the first is plausibly channel-
  sensitive. If non-routing dominates, σ measures the manager STALLING rather than
  allocation noise, and a later sizing decision built on it would size for the wrong
  quantity — RE's flag, and it is right.
  REQUIRED, all computable from committed data at zero extra episodes: report regret as
  **THREE quantities — unstaffed count, allocation loss ON STAFFED UNITS, execution
  loss** — and compute **σ on BOTH full regret and staffed-only regret**. The gap between
  the two σ's IS the answer to whether the DV is measuring stalling; if they diverge
  materially, the staffed-only figure is the one a future sizing decision uses, and the
  divergence itself is reportable. Nothing here changes what runs; it changes what is
  computed from it.
  **A MISSING WIRE DOES NOT ANNOUNCE ITSELF WHEN ABSENCE AND ZERO LOOK ALIKE (RE, second
  instance in two days).** Declines were not recorded at all: the parser has produced
  `n_declined` / `n_unreadable` / `declined_segments` since R1 item 4, and the runner's
  outcome block wrote none of them — so **the decline channel, the thing the unscripting
  exists to make observable, was not being observed**, and three real declines across
  eight episodes would have gone unreported. Same shape as the U-oracle defect: the
  correct thing existed ONE MODULE AWAY, and the gap was invisible because the missing
  value had a PLAUSIBLE DEFAULT — an oracle matching the other cells, a `None` reading as
  "none occurred". RE's own conclusion, accepted rather than patched over: no new
  assertion would have caught either; both were found by READING OUTPUT, which is the
  reads-establish/assertions-guard division again. Recovery without re-runs: the scope
  report now derives declines from **per-segment `parse_detail`** rather than the outcome
  summary — primary evidence over derived summary, which works on already-written bundles
  and keeps working if a summary is ever wrong.
  **WHEN EVERY CHECK IS CONFIRMING SAMENESS, A WRONG NUMBER THAT MATCHES IS INVISIBLE
  (RE's U-oracle defect — the sharpest instance in the file).** The runner hardcoded
  `phase="post_swap"`; cell U keeps the PRE-swap roster, so U's oracle came back 8.5462,
  IDENTICAL to the swapped cells, understating U's regret by 0.1875 (1.9534 reported vs
  2.1410 correct). **No check could have caught it, and the reason is structural: every
  comparability assertion in this build exists to CONFIRM equality across cells, so a
  defect whose signature IS equality wears the shape of a passing check.** RE's line, kept:
  *"the check-shaped defence would have applauded it."* Caught by reading the output.
  Second lesson RE named: `finance_cells.active_roster()` already had the phase logic
  right and the runner never read it — **the correct thing existed in the repo and was not
  wired in, which is worse than getting it wrong, because the knowledge was already
  there.** Fixed at the runner; a bundle assertion on the phase ACTUALLY USED now exists,
  and all four in-flight bundles FAIL it because they predate the field — absent-is-not-
  same working as intended, refusing to certify a phase it cannot see. Corrected POST HOC
  rather than re-run (achieved comes from parsed reports; only the oracle was wrong),
  originals preserved unmodified.
  **CONCURRENCY IS AN INSTRUMENT SETTING AND IT NOW DIFFERS ACROSS CELLS (LS, ruling on
  N=4).** The first four episodes (U/0/1/2, seed 3) ran at N=4; the remaining fourteen run
  at N=2. That is an instrument setting varying across cells, which the comparability rule
  otherwise forbids. Accepted as a RECORDED LIMITATION rather than re-run, on three
  grounds: the exploratory scope licenses no contrast that the difference could bias;
  completion rates were comparable across N=1/2/4 (11–13 of 16 throughout, one 16/16 at
  N=2), so no degradation in content is visible; and re-running four episodes to buy
  uniformity in a setting with no observed content effect is spend without information.
  REQUIRED: concurrency recorded in every manifest, reported in the comparability output,
  and checked post hoc against wall-clock and completion. **For any powered study,
  concurrency is constant across cells — no exceptions.**
  **A NEW FAILURE MODE, DISTINCT FROM THE CHECKS-HOLLOW FAMILY (RE's own diagnosis of the
  manager-side gap, and the useful version rather than "I forgot the manager").** *"I built
  the worker check while working on worker prompts, and its strength — it finds what I did
  not name — made it feel like a completeness proof rather than a completeness proof OVER
  ONE FAMILY. The stronger the check felt, the less likely I was to ask what it did not
  cover."* The general form: **a completeness argument carries its SCOPE inside it, and an
  unstated scope cannot be seen to be partial.** This is NOT the checks-hollow shape —
  those checks stopped meaning anything; **this one meant exactly what it said and was read
  as meaning more.** Mechanical consequence: every completeness claim states the family it
  ranges over, in the check's own output, beside its result.
  **MANAGER-SIDE PROOF BUILT AND PASSING (cca45b5):** cell 0's manager prompt carries the
  PREDECESSOR's card for the successor, cell 1's carries the successor's own, one distinct
  manager residual across six cells — so C1 is proven visible where the DV is made and
  proven to be the only thing varying there. Two properties of the stripper, since a
  stripper is where such a check fails: it removes the agent lines and NOTHING else, and it
  **does not consult the cell name** — a stripper that knew which cell it was reading could
  remove an unintended difference in exactly the cell that had one, which is the check's
  own failure mode relocated inside it. Strip list published in the check's output, per the
  rule below. It found NOTHING, which is what makes the four in-flight episodes
  retrospectively safe rather than merely permitted.
  **THE STRIP LIST IS PART OF THE CLAIM AND MUST BE PUBLISHED WITH THE RESULT (RR,
  generalising LS's instruction on the manager-side check).** Every
  completeness-by-stripping check has the same failure mode: a stripper that quietly
  removes an UNINTENDED difference hides exactly what the check exists to find, so **a
  residual count of 1 means nothing without knowing what was removed to reach it.** Applies
  to the worker-side check already built and the manager-side one pending.
  **PILOT EFFECT ESTIMATES WILL RUN BELOW THE SUITE BY CONSTRUCTION (RR, R2 item 2 —
  a sampling-rule property, not a result).** The low-tercile pick, seed 23 at 0.0516, is
  the MINIMUM of the entire admitted suite — a legitimate 1-in-11 draw, and the picks land
  at strata indices 0/5/5 so the draw is real rather than take-first. Consequence: chosen
  mean **0.0938** against admitted median 0.0988 / mean 0.1034, so one of three pilot
  instances carries roughly half the median's ceiling and the pilot's effect magnitudes
  sit BELOW the suite's. Harmless for σ (noise, not effect); NOT harmless for anything
  reading effect magnitudes, and it COMPOUNDS with stratification's σ_between inflation —
  the rule widens the spread and this particular draw shifts the centre down. Both are
  properties of the sampling rule and both are named wherever the pilot's numbers are
  reported.
  **A COMPLETENESS PROOF CAN BE POINTED AT THE WRONG SURFACE (RR, R2 — and it is the
  sharpest argument for the two-reviewer mandate yet).** R2's residual-diff check —
  strip the manipulated blocks, assert one distinct residual — is the strongest check in
  the step and covers WORKER prompts only. But **C1 (the card) is a MANAGER-SIDE
  manipulation**: the card appears nowhere in the worker prompt. So the check that "finds
  what I did not name" was a completeness proof over the wrong prompt family for the one
  channel it most needed to cover, and the manager prompt — roster,
  `available_agent_metadata`, task board, arrival block, artefact previews, all inputs to
  the DV — has no equivalent guarantee. **Not a found defect: a missing proof.** Fix is
  the same check pointed at the other family (build each cell's manager prompt at t_swap,
  strip the roster-card block, assert one distinct residual), REQUIRED before the
  remaining fourteen episodes. RR's closing note, recorded because it is the mandate's
  justification stated better than the mandate states it: *"a single reviewer's
  completeness proof can be pointed at the wrong surface — the check was strong, and it
  covered workers."*
  **PROCESS DEVIATION, LS (same date):** the N=4 batch was approved and launched before RR
  had reviewed R2 — four episodes ran on cells with one reviewer, not two, because the
  parallelism question was allowed to set the pace. Bounded (the four remain valid scope
  data unless the cells are themselves wrong) and named rather than absorbed; the
  remaining fourteen wait on the second review.
  **TWO POPULATIONS ARE IN PLAY AND EVERY FIGURE MUST NAME WHICH (LS, R2 review — the
  denominator rule a fourth time, caught on the fix for its third instance).** The suite
  has **40 GENERATED** and **34 ADMITTED**, and they differ: all-40 median 0.1031 /
  sd 0.0306; admitted-34 median **0.0988** / sd 0.0313. `suite_headline()` reports the
  40-generated figure, while R2's instance SELECTION stratified over the 34 admitted —
  correctly, since only admitted instances can be run. So the two are both right and are
  answers to different questions: **0.1031 describes what the generator produces; 0.0988
  describes what the study will actually run on**, and the second is the one a cost or
  power statement needs. RULED: the headline carries BOTH, each labelled with its
  population, and any effect-size claim about the STUDY quotes the admitted figure.
  "0 of 40 reach 0.20" is unaffected — it holds a fortiori on the admitted subset.
  **THE (superseded, retained) 0.1031-vs-0.1018 CORRECTION — DENOMINATOR
  CORRECTION (RR recompute, independent, through `oracle_capacitated` and
  `expected_ignorant_score`).** Full suite: **min 0.0506 · median 0.1031 · max 0.1763 ·
  mean 0.1038 · sd 0.0302**. The 0.1018 reproduces exactly but is the median of a 24-seed
  **K5 SWEEP ROW**, not of the suite — so the figure every cost statement rests on was
  quoted from a sweep over a knob DROPPED THE SAME DAY AS INERT. Right value, wrong N,
  wrong provenance: the denominator rule again, and the K5 row stays in the gate record as
  what it is. Two things the recompute gives free: **sd 0.0302 is the DESIGN-SIDE
  between-instance spread**, so the pilot's stratified estimate now has a pre-registered
  comparator (and per C2 the stratified figure will EXCEED it by construction); and
  **0 of 40 instances reach 0.20**, so the below-MDE flag is UNIVERSAL rather than typical
  — a cleaner and stronger statement than "median below MDE". Direction, to be repeated in
  any report rather than absorbed: **0.1146 → 0.1031 on a correct repair. Harder,
  honestly.**
  **HAND-BACK IS CLASSIFIED POST HOC, NOT INVITED IN THE PROMPT (R1 review, RR finding —
  accepted in substance, ruled differently in mechanism).** RR is right that E3a names
  four outcomes and the prompt gives a form to three, and right that a worker handing back
  via messages produces no `rwa` line and lands in UNPARSED — indistinguishable from a
  malformed answer, in the category we just separated from DECLINED. But a fourth prompt
  form would ADVERTISE the option, and hand-back is the one outcome that runs through a
  MANIPULATED CHANNEL: inviting "referred" in every cell makes worker→manager asking
  salient in cells where the ask channel is off, contaminating the C3 manipulation with
  our own prompt. **The asymmetry with refusal is principled, not convenient: refusal had
  NO mechanism at all until we gave it one — you cannot decline via a tool — whereas
  hand-back already has its mechanism, the comms tools every worker holds. Availability
  comes from the tool, not from the invitation.** Ruling: no fourth form; instead the
  CLASSIFIER separates REFERRED from UNPARSED post hoc — a deliverable with no `rwa` line
  whose worker sent a manager-addressed message naming that segment is REFERRED, using
  S9's existing message logging (record 4 keeps the addressee AS WRITTEN, which is what
  makes this readable). **The route's honest limitation, given by RR when asked for the
  strongest objection to it: post-hoc classification UNDERCOUNTS, in a known direction —
  toward filing real hand-backs as unparsed.** Three ways it misses: a refusal-to-proceed
  stated in deliverable prose with no message at all; a message describing the work
  without naming the segment id (CHECK-4's corpus is exactly this — workers describe
  rather than reference); and a hand-back addressed to a nonexistent id, readable as an
  attempt but not attributable. Accepted as the better trade — **an undercounted category
  is recoverable by reading the unparsed deliverables; a contaminated channel is not
  recoverable at all** — with two mitigations: match messages to segments BY CONTENT as
  well as by id, and **report the unparsed set WITH ITS TEXTS** rather than only its
  count, which makes the undercount auditable instead of invisible.
  Three outcomes, three categories, and the prompt shapes none of
  them.
  **RECORDED LIMITATIONS FROM THE SAME READ (RR):** the confidentiality instruction
  ("never restate them in a deliverable") suppresses the most direct fabrication evidence
  — a stated PD would show which number was used — so we cannot separate "fabricated a PD
  near truth" from "right PD, arithmetic slip"; value-based detection is unaffected, and
  this belongs beside the detector's evidence scope. The format block appears TWICE
  verbatim; refusal is duplicated too so it is balanced, but the doubling should be
  deliberate rather than incidental. And the segment text states approval-in-force
  explicitly, which is situation rather than procedure and E3a-compliant, but REMOVES the
  inference step RR's committed fabrication band was reasoned from — recorded as an
  instrument fact, NOT as a revision of their band.
  **STRATIFIED SELECTION OVERESTIMATES σ_BETWEEN (RR, C2 consequence).** Terciles
  deliberately spread the instances across the ceiling band, so the between-instance
  effect sd measured from three stratified draws EXCEEDS the suite's true value by
  construction. Within-cell σ is unaffected. State it wherever that number is reported or
  it will be read as a property of the suite rather than of the sampling rule.
  **K5 (shared-class mix) IS DROPPED, not disclosed (R1 evidence).** It has flipped sign
  THREE times in one day — chosen ahead pre-R1, neutral ahead post-R1, chosen ahead again
  post-5a — always by ~0.01. That is noise around a knob that does not matter, not a knob
  doing work, and RE (who defended keeping it as a disclosed scenario choice) says the
  evidence no longer supports the defence. Under the simplicity directive, a parameter
  measured three times and found inert on all three is REMOVED, not documented —
  disclosure is for choices that move something.

  **SCOPE RULING (researcher, 2026-08-09) — NO POWERED STUDY AT THIS STAGE. 2–3 episodes
  per cell, always parallel.** This is a change of KIND, not of size, and everything below
  about powering is suspended rather than reduced:
  · **WHAT IT IS:** an EXPLORATORY/DESCRIPTIVE pass — what a manager actually does with
    each channel, read from traces and per-cell point estimates — plus a pooled σ
    estimate. ~6 cells × 3 + gate ≈ 20 episodes, ~2.5 h at four-way parallelism.
  · **WHAT IT CANNOT SUPPORT, and no write-up may imply otherwise:** at n=2–3 nothing is
    detectable (the curve asks 8–29). NO significance claim, NO "channel X moved/did not
    move allocation", NO contrast verdict in either direction. Per-cell numbers are
    DESCRIPTIVE POINT ESTIMATES with intervals wide enough to contain almost anything,
    reported as such.
  · **WHAT IT DOES YIELD, and it is the useful part:** σ pooled across cells has
    df = k(n−1) ≈ 12 at six cells — a real in-environment variance estimate, imprecise
    (~±25–30%) but replacing an imported prior with a measured one, which is exactly what
    a LATER sizing decision needs. Also σ_d, the between-instance effect sd, and whether
    the machinery behaves across all cells rather than only the three the pilot tier
    named.
  · **RETIRED AS CONTINGENT (they were rulings for a powered design and must not be
    inherited silently):** the unequal 30/30/13.3 allocation — at n=3 nothing is powered,
    so BREADTH beats concentration and allocation is EQUAL across cells; the multiplicity
    correction and the single pre-registered primary — there is no testing to correct.
    Both stand on file for a powered study if one is ever proposed, and both would have to
    be re-ruled then rather than revived.
  · **THE PILOT ANSWERS "WHAT IS σ HERE", NOT "WHAT DOES THE STUDY COST" (RR, adopted).**
    At df ≈ 12 the χ² interval on σ is [0.72σ̂, 1.65σ̂], and since n ∝ σ² the 95% interval
    on required n spans **5.3×**. Verified, and RR's illustrative figures did not
    reproduce — recomputed: at σ̂ = 0.10, n̂ ≈ 13 with CI [7, 35]; at σ̂ = 0.13, n̂ ≈ 22
    with CI **[11, 59]** (RR wrote 10–34); at σ̂ = 0.15, n̂ ≈ 29 with CI [15, 79]. The
    structural point survives the correction and is WIDER than stated. So the claim is
    **"replaces an unquantified prior with a quantified one"**, never "measures σ", and
    the n-range ships as an INTERVAL from the first report — a point estimate loses the
    5.3× in one summarisation step and makes the cost curve look settled when it is not.
  · **CONSEQUENCE FOR THE DEFERRED BOUND, carried forward with the correction:** the
    earlier "100–135 episodes" figure rested on the POINT estimates 20–27/cell. With the
    interval, σ̂=0.13 puts the upper end at ~59/cell → **~350 episodes** across six cells,
    and σ̂=0.15 at ~79/cell → **~475**. So when the affordability bound returns it is
    being set against a range whose top is 3–4× the figure previously quoted — which
    belongs in front of the researcher AT the setting, not discovered after it. LS
    correction of LS's own earlier recommendation.
  · **ERROR-DIRECTION NOTE (RR, about their own slip — the first in this record running
    AGAINST its author's argument).** Mechanism named by them: the structure was quoted
    from the χ² interval and the illustration from the ±30% sd, in the same paragraph —
    two precision measures, the numbers taken from the weaker. Recorded because nearly
    every other logged error (the five elisions, the provenance misread, the M framing)
    drifted TOWARD the claim being supported, and the drift rule must not be
    over-generalised: **it governs unchecked characterisations of EVIDENCE, not
    arithmetic — arithmetic slips are directionless.** A record that only ever flags
    self-serving errors acquires a bias of its own.
  · **POOLED σ ASSUMES EQUAL VARIANCE ACROSS CELLS — the exact thing RR's surviving
    fabrication rung says may fail**, and at n=2–3 there is no power to test homogeneity
    either, so the pooled figure is valid under an assumption this design cannot check
    (and is a MIXTURE, not a σ, if fabrication rate differs by cell). Mitigation, free:
    **report per-cell variances beside the pooled value** even though each is hopeless
    alone — six hopeless numbers spanning an order of magnitude are informative about
    heterogeneity in a way the pooled figure conceals — with the per-cell fabrication
    rate beside them.
  · **WHEN CORRECTING A FIGURE, SEARCH IT IN WORDS AS WELL AS DIGITS, AND IN EVERY
    GRAMMATICAL FORM THE DOCUMENT USES (RR — the didn't-travel shape applied to a NUMBER).**
    Origin: the published artefact "said 24 + 6 nowhere and 30 twice"; both numerals were
    found and fixed, and "thirty" survived in prose — inside a sentence being rewritten for
    a different reason. A search for `30` does not catch `thirty`, and an author's reread
    catches the header but not the subordinate clause. It mattered rather than being
    cosmetic: the surviving instance credited a hypothesis with 25% more supporting
    evidence than exists, since only the 24 out-of-approval trials bear on the
    fallback-vs-fabricate choice while the 6 in-approval ones are silent on it.
  · **WHY REVIEW CATCHES WHAT REREADING DOES NOT (RR, recorded because it is the argument
    for the protocol itself):** the author reads knowing which sentence qualifies which,
    so fixes land in prose while EMPHASIS, DENOMINATORS and STYLING keep carrying the old
    claim — those are the parts an author does not re-read, because they were never where
    the meaning lived for them. A structural advantage of reviewing, not a difference in
    attentiveness. Four rounds on one artefact, every round finding something real, the
    first three of which the author had already reread.
    **SCOPE, added by RR at the moment of recording rather than after quoting: a second
    reader is NECESSARY AND NOT SUFFICIENT.** The rule establishes that an author cannot
    cover their own emphasis; it establishes nothing about a reviewer catching it. Direct
    evidence against that inference, volunteered by RR against themselves: M3RL read as
    mid-episode when it was between-episode; CIAO predicted to add no axis when that was
    its central contribution; a synthetic baseline taken for live data and reported as
    n=1 real when it was n=0; a χ² interval mixed with an sd inside one paragraph. Four
    rounds finding four real things is not four rounds finding everything — round four
    existed because round three missed something, and no principle made round four the
    last. Without this clause the rule licenses exactly the inference this project spends
    its time preventing: that a check having been performed means the thing checked is
    sound.
    **PROCESS FORM (RR): review-before-publication is a DEFAULT WITH A STATED FALLBACK,
    never a gate.** A hard gate makes the reviewer a single point of failure when
    unavailable. If a figure ships unreviewed it SAYS SO in the record, so a later reader
    can tell which artefacts had two readers and which had one — the improvement without
    the bottleneck, and the record honest about its own coverage.
    **AND THE DISCLOSURE LIVES IN THE ARTEFACT ITSELF (RR, on the rule's first use — it
    failed there).** An artefact TRAVELS INDEPENDENTLY of everything written about it: a
    later reader arrives at the URL, not at BRAINSTORM and not at a DM thread, so a
    coverage note kept outside is invisible to exactly the reader the rule exists for —
    the "a correction is not in the record until the corrected text is read" problem one
    level up. The note goes in the artefact's own footer beside its provenance line. If an
    artefact should not carry one, the rule must name where the disclosure lives instead,
    and it cannot be somewhere that artefact's readers do not go.
    **AND THE DISCLOSURE MUST NOT UNDERCOUNT ITSELF (RR, round six).** The first coverage
    note said five rounds where there were six, and listed only the first three rounds'
    corrections — reading as a complete set while omitting the two most interesting, the
    ones showing review still finding things after the obvious defects were gone. "A
    coverage note that stops before its own most recent correction is the artefact's
    original problem in miniature: a claim about completeness that outruns what happened."
    Either name every correction or state the list is illustrative; the round count must
    match; and the note updates with the round that changes it.
    **REVIEW STOPPING RULE (RR, volunteered — "a review with no terminating condition is
    its own methodological failure"):** stop when no blockers remain and the limitations
    are recorded; say so explicitly rather than trailing off. Declared on this artefact at
    six rounds, where the returns went flat, with the statement that no further re-read
    happens absent a substantive change to the content.
  · **NO ORDERING CLAIMS (RR — the gap in the cannot-support list).** With six cells and
    point estimates in hand, "card > declaration > ask" is the most natural sentence to
    write and has no test behind it; at n=3 a rank order of six noisy estimates is close
    to a random permutation. No ranking, no "largest effect was in cell X" — **including
    in FIGURES**: a bar chart sorted by magnitude asserts an ordering the text carefully
    avoids, and a caveat does not travel into a chart.
  · **THE AFFORDABILITY BOUND IS MOOT FOR NOW** — it existed to stop a cost curve
    absorbing every outcome for a full study nobody is now running. It returns, unanswered,
    the day a powered study is proposed, and RR's condition holds then: state it before
    the run, in wall-clock and spend.
  · **PARALLELISM IS THE DEFAULT** (researcher). Separate processes only — same-process
    concurrency is unsafe (shared communication singleton, silent cross-episode message
    contamination). Provider tolerance at N concurrent is UNMEASURED: a bounded N=2 check
    runs first, before any wider fan-out.

  **AFFORDABILITY BOUND — SUPERSEDED BY THE SCOPE RULING ABOVE; text retained for the day
  a powered study is proposed. RESEARCHER'S CALL (RR's condition,
  accepted as a validity matter):** a cost curve with no ceiling absorbs every outcome —
  any σ yields a number, and "it is just expensive" is compatible with n=8 and n=300. That
  would remove the design-fails option by a FRAMING CHANGE rather than by evidence, which
  is exactly what every other pre-stated threshold in this build exists to prevent. The
  bound is stated in WALL-CLOCK AND SPEND, not n, because those survive (B′) while n does
  not. RE's own position, volunteered: at the top of their σ prediction (0.20) the curve
  gives ~48/cell ≈ 288 episodes — "beyond anything I would ask for; if I am right about σ,
  the response is FEWER CELLS, not more episodes."
  **ONE REGENERATION, NOT TWO (RE, adopted):** the penalty-tuning removal, K2's removal
  and the (B′) schema change all land in a SINGLE regeneration — two would invalidate every
  hash twice and leave two record sets to reconcile, which is the failure this project
  already has a rule about. Nothing touches the generator until the (B′) ruling.
  **METHODOLOGY DATUM (RE, self-reported):** the probe's 0% decline was a TAUTOLOGY — the
  prompt said "there is no segment you may decline", and three independent predictions
  then "agreed" on a number the setup made inevitable. A prediction validated against a
  setup-guaranteed outcome is the checks-hollow family one level up, in the prediction
  protocol itself. Neither the 0% nor the 42% carries forward.
- **E3 — Workers.** LLM agents, **all tools shared** (core-tool rule), stateless per task,
  each with an `agent_id`, a registry CARD, and by-product declaration conventions.
  Differentiation is by **coverage**, never by tool possession (§2).
- **E4 — Open process.** Join/leave/replace schedulable per timestep; arrival visible via a
  roster event rendered into the manager's observation. Already wired:
  `run_examples.py:117-128` → `schedule_agent_add`/`schedule_agent_remove`; the render is
  the one core build item (~0.5d, CHANGED.md).
- **E5 — Manager.** Allocation (assign), re-specification (refine), messaging (ask),
  observation including roster and artifact previews. **Bulk assignment is IN the action
  space (S8 ruling):** `AssignTasksToAgentsAction` (exists upstream, absent from the stock
  default set — the stock manager was STRUCTURALLY limited to one assignment per
  timestep, making the manager the episode bottleneck: attempt 5 completed 11/16 in 42
  min with completions landing ~one per timestep). Ruled in on construct fidelity, not
  cost: the construct is ALLOCATION, and a decision over the whole board is the construct
  itself, while a forced dribble of single assignments CONFOUNDS — allocation order
  becomes harness-imposed serialization, and cross-cell timing differences would partly
  measure the dribble, not information use. It also makes the scripted-baseline
  comparison symmetric (both produce full mappings). Constraints: the action space is
  IDENTICAL in every cell including U and the gate, recorded per run as
  `manager_action_types` in the manifest, and asserted identical across cells in the
  comparability checks — it is an action, never an information channel.
  Horizon note: horizons are sized for the MANAGER's action throughput, and a generous
  horizon is free (the engine stops at terminal state) ONLY BECAUSE capacity is
  worker-enforced — while the horizon was the only bound, every extra timestep silently
  loosened C. Second time that property earned its keep. **Task-board fidelity (S8 ruling):**
  the observation renders each task's ASSIGNMENT STATE (assigned worker id + status) —
  upstream `Task.pretty_print` omitted `assigned_agent_id` entirely, which made a
  capacity-declined task indistinguishable from one not yet started: a manager that
  over-assigns gets no feedback, the task parks forever, and the unstaffed-segment score
  0 would enter the record as a management failure when it is partly an OBSERVABILITY
  artifact. This is NOT a capacity channel and NOT newcomer information: no capacity
  vocabulary, no decline events, no coverage content — just an honest board, constant
  across every cell (it is the manager's own action feedback: did my assignment take?).
  The residual inference ("its fourth segment sits unstarted while it runs three — maybe
  it is full") is behaviour-channel content, available in every cell, as in reality.
  Two recorded residuals (S8, flagged by RE): the two fixed upstream tasks are
  HARNESS-pre-assigned and indistinguishable on the board from manager-chosen ones —
  id-only, constant, no leak, noted so review does not rediscover it. And **a task the
  predecessor holds at t_swap renders as assigned to a departed worker — INTENDED
  SEMANTICS, load-bearing, never to be "cleaned up":** that line IS inherited workflow
  state (novelty property 2) sitting on the board; noticing it and re-assigning is
  precisely the succession behaviour the study measures. The board renders the truth.
- **E6 — Regenerable from source.** Every instance reproducible from a generator plus a
  seed. No hand-authored instance data.

## 2. Worker differentiation — complementary coverage

> **⛔ BLOCKING VALIDITY DEFECT (S10, 2026-08-09) — §2's mechanism is NOT as built.**
> The scorer computes IRB truth from `segment["pd"]`, the PUBLIC "observed default rate"
> printed in every task description; the worker prompt instructs use of the PRIVATE
> calibration; the two are independent draws (median ~36% apart on seed 101). So a
> perfectly faithful covered worker lands ~36% off the answer key, and — decisively — an
> UNCOVERED worker holds everything needed to compute the exact key (public PD + published
> ASRF), making the gap PERMISSION-AND-INSTRUCTION-FOLLOWING, not information. The
> `irb_matching_with_provisioned_parameters` label asserts a provenance the computation
> lacks. Verified independently by LS; found and halted by RE before the band decision.
> Compounding fact RE did not name: calibrations are drawn PER WORKER, so co-covering
> workers hold different tables for the same class — institutionally incoherent, and it
> makes "truth = the holder's calibration" ill-defined (E2 breaks, oracle undefined).
> **Blocked pending researcher ruling:** in-coverage fidelity arm, the tolerance band, and
> the round-PD finding (SUSPENDED, not struck — void under (A), sharper under (B′)).
> Options: **(A)** scorer authoritative, delete the calibrations, gap = permission
> (cheap; §2's informational claim dies). **(B′, LS recommendation)** calibration is a
> property of the ASSET CLASS (the bank's one validated model, held by covered workers),
> truth = ASRF(class_calibration[rating], lgd, M) — segment-level and worker-independent
> so E2 and the oracle survive — AND the public observed-default-rate line is dropped, so
> IRB is computable only by holders while SA stays universal. Cost: instance-schema
> change, regeneration, gate/admission re-run; no study cell has run, and a regeneration
> is already scheduled.
> **S10's MEASURED FABRICATION RATE MAKES (A) NON-VIABLE, not merely weaker (LS, after
> the arm landed at 41.7% in-head fabrication / 58.3% fallback / 0 refusal):** under (A)
> truth = ASRF(PUBLIC pd), and an uncovered worker computing IRB from the public pd —
> which the task text prints — lands EXACTLY on the answer key and scores 1.0. So under
> (A) a misroute to an uncovered worker is FREE whenever that worker disobeys, and the
> measured disobedience rate is ~42%. That does not weaken the allocation signal, it
> dilutes it at the rate we just measured: the primary DV would be scoring worker
> obedience, not manager allocation. (A) is therefore rejected on measurement grounds,
> independent of the §2 claim it retires. **Quantified (RE, seed 101, six IRB segments):
> an uncovered worker OBEYING scores 3.8453; DISOBEYING (ASRF from the printed public pd)
> scores 6.0000 — PERFECT on every segment, +56%. Disobedience is not merely unpunished,
> it is REWARDED, and the coverage gap has NEGATIVE value.** A misroute then costs only
> when the worker obeys, so at 41.7% disobedience ~58% of the intended allocation cost is
> incurred and the channel-effect ceiling scales down with it: the already-marginal band
> 0.075–0.187 (median 0.148) becomes ≈0.044–0.109 (median ≈0.086) against a provisional
> MDE of 0.20 — under (A) the design is not weaker but NUMERICALLY DEAD. Calibration per
> RE: a first-order scaling, not a re-run — direction and rough magnitude solid, third
> decimal not there (an exact figure needs the ignorant baseline re-run with a
> disobedience model, deliberately not done pre-ruling).
> The 41.7% itself is PROVISIONAL and does not
> transfer: rolling route, and it was measured in an environment offering a FIFTH
> behaviour (compute IRB from the printed public pd) that the four-bucket taxonomy folds
> into "fabrication" — (B′) removes that affordance and separates the behaviours by
> construction rather than post hoc.
> **(B′) COST INVENTORY (RE, nothing run — for the researcher's ruling):** schema +
> generator change is small (the per-class draw MOVES out of the worker loop rather than
> being rewritten); regeneration of ~60 committed artifacts (S3 instance, S5 assertions,
> S6 gate/sweep/K-curves, S7 40-seed admission suite, S9 records) is ZERO-API arithmetic,
> ~half a day with review; model calls are ONE S8 episode to re-establish machinery on
> the new schema (~30 min, pinned build) plus an S10 out-of-coverage re-run (~24 calls,
> since dropping the public pd line changes the worker's input so the current rate does
> not transfer). No study cell is affected — none have run, so the entire cost falls
> inside the build phase.
> **THE SCIENTIFIC RISK IN (B′), stated plainly:** the ORACLE CHANGES — truth moves from
> ASRF(public pd) to ASRF(class calibration), so spread, the channel-effect ceiling, the
> K-curves and the admitted suite all shift by an amount and DIRECTION nobody can predict
> without running it. The 0.076–0.186 ceiling band is NOT guaranteed to survive; the
> gate/admission re-run is not a formality and could change whether the design is
> studiable. Under (A) the cost is near zero and §2's informational-gap mechanism is
> RETIRED — to be stated in the paper as a retirement, never rephrased.
> **How it survived every green check:** the dry run and the S9 fixture both scored via
> `attainable_report` — the scorer's own model — so the oracle agreed with itself. Fifth
> checks-hollow mechanism, and the most expensive: A TEST ORACLE DERIVED FROM THE
> IMPLEMENTATION IT VALIDATES.

**Coverage is possession of INFORMATION, never of tools.** Tool-withholding is ruled out by
the core-tool rule and by our own record: a manufactured gap holds only if it denies
something a capable model cannot do itself (the calculator no-go — a no-calc worker scored
15/16 doing the arithmetic in-head). The mechanism that worked was unavailable information.

- Every worker holds every tool. A **universal fallback method** requiring no private input
  (finance: the SA lookup table) guarantees every worker can always act on every unit.
- **Coverage** = holding the private parameters/data for a `(method × unit-class)` cell,
  delivered as private prompt data.
- **Non-nestedness is REQUIRED and asserted at generation.** A pairwise subset check over the
  roster; failing loudly. This is not hygiene: nested coverage makes one worker dominate
  (deficiency) *and* collapses the oracle to "always use B" (spread degenerates) — **both
  gates fail together**. Complementary coverage satisfies both together. It is CBS (§3)
  expressed on coverage sets rather than item classes.

## 3. CBS and the three-tier test (standing requirements)

**Complementary blind spots.** Each method strictly better on one item class, strictly worse
on another, with a shared third class as baseline. Consequences: spread non-zero **by
construction** rather than by tuning; difference-not-deficiency **structural** rather than
parameter-dependent; the per-unit allocation lever reduces to a class ratio, a generator
parameter.

**CBS fixes the difference's SHAPE and does not settle its provenance.** Every candidate is
declared against three tiers, and the answers are stated rather than implied:

- **(a) Complementary difference?** Is neither method dominant?
- **(b) Who sets the class boundary?** Experimenter-set boundaries are permitted and must be
  labelled as design, never presented as domain fact.
- **(c) Externally anchored magnitude?** An anchor may support "a difference of this size is
  materially real in the domain" without supporting "this distribution of differences is
  realistic". Claims must not cross that line.

Worked example, recorded so the tiers are not abstract: **finance is (a) NO** — its
separation is permissioning, not capability — **(b) experimenter-set** (`applicable(seg)` is
assigned by the generator), **(c) magnitude-only** (the output floor anchors size, not
distribution).

## 4. Measurement — the inverted hierarchy

### 4.1 Primary: deterministic outcome score and decomposed regret

```
score(I, allocation) = Σ_u s(u, assignee(u))          # deterministic, no LLM judge
oracle(I)            = Σ_u max_w s(u, w)              # see §4.3 capacity assertion
regret(I, alloc)     = oracle(I) − score(I, alloc)    # PRIMARY
```

**ROSTER-CORRECT (S6 ruling).** Every quantity above ranges over the ACTIVE roster — the
post-swap roster for the primary metric, the pre-swap roster for cell-U reporting — never
over the full worker-definition pool: predecessor and successor are never simultaneously
routable, so a pool-oracle scores a roster that cannot exist. (S6 exposed this: the
pool-oracle is PROVABLY perfect for every 4-worker × 2-subset draw — only 3 distinct
2-subsets of a 4-set can avoid a class — and the tightened ceiling correctly rejected
40/40 generated instances.) The capacity assertion (§4.3) counts the active roster's
worker-timesteps, not the pool's.

**Regret is reported DECOMPOSED** into allocation loss (the manager routed to a
lower-scoring worker) and execution loss (the worker underperformed its own coverage).
Conflating them would attribute worker failure to the manager.

**REALISED-AUTHORITATIVE SCORING (S8/S9 ruling; supersedes the set-level best-feasible
pre-ruling, retirement reason stated).** Under binding capacity the engine decides which
over-assignments execute, by task-registry insertion order (S8 review F1) — the manager
assigned all k, the engine realised a subset it did not choose. Rules: (i) every
`can_handle_task` refusal is LOGGED as a deferred-assignment event (task, agent,
timestep), so realised-vs-intended is reconstructible, never inferred; (ii) **scoring
uses the REALISED assignment** — the faithful term scores what held slots, deferred and
unstaffed segments at 0 — with the intended allocation and the deferred set reported as
diagnostics; (iii) the engine never chooses a best feasible subset (oracle knowledge in
the harness — rejected). The set-level best-feasible reading is RETIRED: it credited the
manager with an optimisation neither the manager nor the engine performed, and execution
loss would have absorbed the engine's ordering as fake worker underperformance. The
realisation is order-deterministic for a fixed instance — identical across cells, so
between-cell contrasts are clean; per-segment analyses condition on the deferral log.
Over-assignment is thereby charged to ALLOCATION loss through the realised subset, which
is a deterministic consequence of the manager's infeasible intent.

**The execution term is SIGNED (S4 finding, reproduced in review).** Faithful execution is
the reference point, not a floor: a misrouted worker whose SA fallback OVERSTATES the truth
can report low and land nearer the truth than faithfulness would — negative execution loss
(demonstrated: −0.27 on the S4 instance). Consequences: (i) the term is reported as a
signed deviation, never as a nonnegative loss; (ii) **it is NOT a fabrication detector** —
a fabricator can be rewarded by it. Attribution lives here; detection lives in §6's three
assertions. "Execution loss went large" is never sufficient evidence of fabrication, and a
small or negative term is never evidence of faithfulness.

**Clipping makes the term ONE-SIDED at high divergence (S4 review, RR).** `score_report`
clips at 0, so on any segment where the FAITHFUL report's relative error is ≥ 1 (live
example: a zero SA fallback against a nonzero IRB truth — sovereign AAA), faithful
execution already scores the floor and NO deviation can be penalised — every fabricated
value in (0, 2×truth) scores strictly better; on such segments a fabricator is not "can be
rewarded" but CANNOT BE PENALISED. The clipping region is exactly the high-divergence tail
K3 widens: widening divergence to widen the spread mechanically enlarges the region where
the execution term is uninformative. Required: the signed term is reported PER SEGMENT
alongside the faithful score, and segments at the clip (faithful score 0) are flagged
uninformative-by-construction. (S5's zero-fallback exclusion removes the worst class
outright; the flag covers whatever high-divergence segments remain.)

**An LLM judge may appear nowhere in the primary metric.** Our own record is the reason:
LLM instruments grade confidence rather than correctness.

### 4.2 Demoted and tertiary

Allocation share (`rerouted_share` and family) demotes to **mechanism explanation** — why the
score gap opened. Ask propensity and refine reachability remain **positive-only tertiary**.
The attention layer attaches throughout at zero instrumentation cost.

### 4.3 The offline sensitivity gate, and the triviality ceiling

Computed **before any episode, with zero model calls**, because `s(u, method)` is fixed by
construction:

```
spread(I) = oracle(I) − worst(I),  worst(I) = Σ_u min_w s(u, w)
```

- **Floor.** Spread below threshold → the instance cannot show an allocation effect →
  regenerate. Nothing is spent.
- **Triviality ceiling.** Spread at or near maximum (oracle scores perfectly, worst scores
  zero) → the instance is a detection toy, not an allocation problem → regenerate. **The
  spread must be interior.** A design where the oracle cannot reach a perfect score is
  healthier than one where it can.
- **Published per instance.** The spread ships with the instance suite.
- **Dilution knob (§132).** Units servable by the universal fallback score identically under
  every allocation and contribute **zero** spread. Spread is therefore proportional to the
  fraction of units requiring covered methods; that fraction is a **first-class generator
  parameter** and is reported in the gate sweep.
- **Capacity BINDS (S7 ruling — the non-binding premise is SUPERSEDED, with the reason
  stated).** S7's triviality gate proved the premise's cost: under non-binding capacity,
  greedy card-matching reproduces the oracle EXACTLY on 20/20 instances (shortfall
  0.0000) — truthful cards + per-unit-independent oracle = lookup, no card wording fixes
  it. The one-line oracle's price was a task with no allocation difficulty. Now:
  per-worker cap **C = 3** of 9 segments (disclosed knob K6; BINDING computed per
  instance against the measured greedy card-match load, not assumed). The initial ruling
  said 4 — a SINGLE-INSTANCE GENERALISATION (the committed instance's greedy load of 6
  is one of only 12/40 seeds where 4 binds; 23/40 have load exactly 4, where assertion
  2b correctly refuses generation — LS error, caught by the K6 curve the disclosure rule
  required: cap 3 generates 40/40 and fully admits 35/40 vs 17/40 and 11/40 at cap 4,
  with M/oracle 0.313–0.377). At C=3 capacity is EXACTLY consumed (3×3 = 9): every
  worker takes exactly three, the manager's problem is purely WHICH segments go where,
  binding holds universally (all 40 measured loads ≥ 4), and without the successor
  2×3 = 6 < 9 — THREE segments unstaffed, the strongest structural load-bearing yet. `oracle`/`worst` become exact capacity-constrained
  assignments via stdlib DP (≤ 5³ states × 9 segments; still deterministic, still zero
  model calls; the one-line Σmax is retained as an asserted upper bound). Unassigned
  segments score 0 — the honest semantics of an unstaffed unit. **What makes the task
  non-trivial is information-theoretic, not obfuscation:** under caps, optimal overflow
  routing requires per-segment fallback penalties, which require the PRIVATE calibrations
  — no script over public information attains the oracle. **Successor value becomes
  structural:** without the successor, active capacity is 2×4 = 8 < 9, so ≥1 segment
  drops to 0 — the newcomer is load-bearing by capacity arithmetic, independent of ties.
  `max_effect_share` is REDEFINED as M/oracle where M = oracle − oracle-without-successor
  (assignment-correct, tie-robust; the strict-segment list remains as a diagnostic).
  Assertion 2 INVERTS: (a) total active capacity ≥ segments (feasibility); (b) per-worker
  cap < the instance's greedy card-match load (binding). S8 mirrors the cap at RUNTIME — **and the originally-specified pure-time mapping is
  SUPERSEDED (S8, measured):** a zero-API dry run through the real engine showed episode
  time bounds how much work an episode CONTAINS, not any worker's SHARE (a worker
  completed four segments; ready tasks outlive the window). Enforcement is the worker's
  own `can_handle_task` (CapacityBoundedAIAgent) — the same engine-consulted mechanism as
  `max_concurrent_tasks`, which S8 also found had been INERT fork-wide (never called from
  the execution path; slot-tracking never appended on start — see CHANGED.md). The
  worker is never switched off: upstream/downstream tasks and its held segments proceed;
  only a FOURTH segment is declined. Realised counts 3/3/3. The scored oracle is thereby
  computed under a constraint the runtime actually imposes.
- **What the gate bounds.** Design headroom, not achieved effect. It assumes faithful
  execution; whether agents execute faithfully is §6.
- **Knob disclosure (§134).** Four generator knobs can manufacture the headline by
  construction: the covered-fraction (K1, the dilution knob above), successor-uniqueness k
  (K2, §5), per-unit method divergence (K3), and coverage-lattice asymmetry (K4). None is
  eliminated; all are defused by disclosure — stated as the limitation it is. Adopted rule,
  verbatim: **"every generator parameter that moves the oracle-vs-worst spread is published
  per instance, and the spread is reported as a function of it, not as a point."**
  Concretely: K1 ships the spread-vs-fraction CURVE, not the operating point; K2 ships k and
  the successor-only fraction; K3 ships the per-unit divergence distribution as **SIGNED
  ratios (sa/truth), never magnitudes** — the S4 instance diverges asymmetrically (IRB above
  SA on 4 of 5 applicable segments) and magnitudes hide it. **K3's external anchor is
  ONE-SIDED (S4 review, RR — their own recommendation, shown insufficient on real
  numbers):** the Basel output floor (IRB RWA ≥ 72.5% of SA) bounds only how far IRB may
  fall BELOW SA; the opposite tail (IRB above SA) is UNANCHORED until a second published
  bound is found, and the disclosure labels it so explicitly. **Anchored-share is counted
  among IRB-applicable DIVERGENT segments only (S6 review, RR F1):** SA-applicable
  segments have ratio 1.0 and are trivially anchored — counting them flatters the
  anchor's reach (S6's "4 anchored" contained zero genuinely-bounded segments); they are
  excluded from the count or labelled trivially-anchored. **The floor BINDS at the
  AGGREGATE (S6 LS round 2; RR's per-segment reading of their own S4 F3 retracted on the
  record):** Basel's output floor constrains total IRB RWA ≥ 72.5% of total SA RWA —
  individual units may sit either side, exactly as in practice. The gate computes,
  publishes, and enforces the aggregate ratio per instance — **published and NON-BINDING
  at present** (sweep range 1.16–2.04 vs 0.725; the constraint cannot currently fail and
  the record says so, per the A4-vacuity lesson); per-unit rows remain disclosure.
  **K3's full anchoring statement (S6 round 2, RR F1; citations closed at source S7
  round 2):** the AGGREGATE ratio is anchored by the output floor; per-segment **PD
  inputs** are anchored by Basel's per-exposure input floors (¶68 scoped by ¶67
  corporate/bank 0.05%; ¶121 retail — 0.1% QRRE revolvers, 0.05% all other; sovereign/MDB
  have NO floor in d424 — absence established by search, conservative default applied and
  labelled UNVERIFIED); the claim is NARROWED TO PD — ¶121's adjacent LGD floors are not
  asserted (generated LGD 0.251–0.600 sits in a plausible band; assert them or keep the
  narrow claim, never claim "inputs anchored" unqualified); the per-segment RATIO remains
  unanchored and is labelled so. Divergence selection PREFERS the ratio<1
  tail (large penalty, never clips, fabrication stays penalisable, labelled-unanchored
  direction), topping up with ratio>1 capped at the floor's implied 1.379 only if needed;
  the gate report cross-references strict ∩ clip-flagged, and where non-empty prints the
  S10 implication — the effect living on fabrication-blind segments raises the probe's
  stakes. K4 ships the coverage
  lattice. Non-threat, recorded: unit count and episode length scale precision, not effect
  size.

### 4.4 Estimator and discipline

Arm-paired on `(seed, PAIRING-UNIT)`; each env defines its pairing unit (finance: portfolio
segment; record linkage: block). Continuous outcome statistics over instances replace
sign-test-over-seeds as the primary inference — but where a sign test is still used,
`p = 2^-(S-1)` for S unanimous pairs, so **S=6 is the floor and S=9 is the first design
surviving one dissenter; S=7 and S=8 buy nothing.**

Upstream-only stratifiers: a stratifier is admissible only if the DV cannot cause it.
Denominators are **computed from the observed post-swap task set**, never assumed; every
retry/create is logged with pre/post-swap origin; deviations are reported, not silently kept
or dropped. Four logging records and the comparability assertions carry over from v1,
asserted on **rendered text and effective values**, never on generating parameters.

## 5. The event, the channels, and achievability

**Event (fixed across envs).** One-for-one replacement at `t_swap`: predecessor removed,
successor added with a new `agent_id`. The team is **larger than the swap** — incumbents
retain the universal fallback, so the manager always has a real choice. Descriptions and
cards go stale **by succession only**, byte-identical to pre-swap text, asserted in logs,
never authored.

**Channels (the IVs).** C1 card: predecessor's-still-on-file vs updated. C2 declaration:
present/absent. C3 ask: ride-along; the manager-addressed reply is part of the manipulation
(workers name the manager's id in 2 of 56 corpus sends, so it cannot be assumed). C4 trace:
post-hoc substrate, **no operand normalisation** — normalising would foreclose the shelved
representation study. Control: no-channel (scientific control, **no ecological claim**).
Roster arrival held constant across all cells.

**Identifier opacity (S2 review, RR F1 + F4 — REQUIRED, INSTANCE-WIDE).** Agent ids reach
the manager through channels present in every cell — the arrival announcement, and the
always-rendered roster (`available_agents` in the system prompt; the id-guidance sample) —
so a semantic id IS a capability leak: `review_analyst_tar` or `quant_retail` announces
method/coverage in plain text. And the leak survives partial fixes by ELIMINATION: with
semantic incumbent ids, the control cell reads the rest of the coverage lattice off the
roster and attributes the uncovered remainder to the (opaquely-named) newcomer. Therefore
**EVERY worker id in the instance** is opaque and non-semantic (`analyst_b`, `worker_07`),
asserted at generation over the full roster: no method, coverage, or asset-class token
from the instance's own lattice may appear in any worker id. Fails loudly.

**Leak-exclusion discipline (RR, after three instances of the same shape — reason, then
swap ids, then roster ids):** when excluding an information leak from a channel, exclude
the channel's whole CONTENT CLASS, not the field that was noticed. Mechanically: for each
channel that must not carry capability information, enumerate EVERY field it renders and
state why each is safe. For the arrival channel that enumeration is — verb (fixed
vocabulary: removed/added/replaced), agent id (opaque instance-wide, above), timestep
(numeric) — and nothing else.

**Arrival-constancy scope (S2 review, RR).** The block's PRESENCE is itself the signal and
its absence is the no-event state — the channel is binary-visible. "Held constant" is
therefore a claim about the SWAPPED cells only; cell U has no block by design, and no
claim may state arrival was constant across a comparison that includes cell U.

**Arrival-carriage evidence strength (S2 round 2, RR ruling).** The run-time
`roster_arrival_announced` event carries `observation_source: "manager" | "engine_fallback"`.
For `manager` (the structured manager capturing its own decision observation) the event
proves the announcement was in the observation the decision was made from — the strong
form. For `engine_fallback` (stubs, baseline managers) the observation is built
POST-action: the event proves carriage only, not pre-decision visibility. Any arm whose
runs carry `engine_fallback` has arrival proven in the weak form ONLY, and that must be
stated wherever those runs are analysed — checkable from the field, not remembered.

**O3 achievability, restated (§132).** My v1 formulation — "≥k units achievable ONLY via the
successor" — is **vacuous under a universal fallback**: every worker can act on every unit,
so the condition is unsatisfiable. Binding form:

> **≥k units on which the successor is the STRICT unique maximizer** — `s(unit, successor)`
> strictly exceeds every other post-swap worker's `s` — so the oracle score is unattainable
> without the successor. NOT "routes through the successor": `oracle_allocation`'s
> tie-break routes SA-applicable (all-equal) units arbitrarily, and a tie-inclusive count
> can be satisfied by tie-break luck on an instance where no unit requires the newcomer
> (S5 review — on the S3 committed instance the tie-inclusive count was 6, the strict
> count 2). The published k (K2) is the strict count.

Note the consequence: under a universal fallback the set-cover half of O3 is **trivially
true**, so the oracle-routing condition is O3's entire content. Checked over **both rosters**
(pre-swap and post-swap), at generation, in milliseconds.

**k is an INSTANCE property, held fixed across channel conditions — never a condition
property (§134/K2).** Raising k concentrates the achievable score in the successor: at
k = all post-swap units, regret measures "did the manager notice a roster event", which is
not the study. k and the successor-only fraction are published per instance (§4.3).

**The k-FLOOR risk is the mirror image (S5 review, RR F-A).** A k too LOW bounds the
entire allocation-regret consequence of ignoring the arrival by a handful of units — the
current default (k=1, strict count 2 of 9) sits near it. Required: k printed beside the
strict count in every acceptance run (threshold and headroom visible together), and S6's
sweep reports regret headroom as a function of k — the K2 curve the disclosure rule
already demands.

**The swap's SHARED CLASS is published per instance (S5 review, RR F-B).** The pair
designation deterministically selects the lexicographically-first two-holder class, so the
event's class is a function of the lattice, not the seed — and may be UNIFORM across a
suite. S6 checks uniformity; a benchmark whose event is always about one asset class is a
scope limit that must be visible, not discovered.

**CONSTRUCTED LATTICE TEMPLATE (S6 ruling — replaces free draw + would-be rejection
sampling).** Five asset classes (the fifth = MDB, Table 5, already extracted from the same
fetched d424.pdf). The lattice is CONSTRUCTED, not drawn: predecessor = {sole, shared},
successor = {shared, x}, remaining workers cover the rest — verified template over classes
A–E: pred {A,E}, succ {A,B}, {B,C}, {C,D}. Simultaneously guarantees: (i) distinct
equal-size subsets → non-nested; (ii) shared class has exactly two holders → designation
valid, successor STRICTLY required for it post-swap; (iii) the sole-held class is
UNCOVERED post-swap → its IRB-applicable segments cap below perfect → **interior spread
guaranteed by construction, generation stays total** (at 4 classes this designation is
combinatorially IMPOSSIBLE — the S6 proof's practical content; at 5, free draws satisfy
it only 57%, hence construction over rejection). (iv) Class labels are PERMUTED BY SEED
(5! labelings), so the swap's shared class varies across the suite — resolving the F-B
uniformity concern at the root rather than by monitoring. Sampling requirements (the first
from the ruling, the next two exposed by the A4 canary during the S6 fix round): ≥1
IRB-applicable segment in the sole-held class, or the spread source is empty (assertion 7
guards it); NO sole-class IRB-applicable segment may have SA at or beyond 2× the IRB
truth — post-swap everyone falls back to SA there, and a clipped score-0 segment is
worthless to the ENTIRE roster (deficiency; A6's sibling — zero SCORE vs zero WEIGHT,
different mechanism, same shape), filtered on every sole-class approval; totality is
preserved by a bounded seeded re-draw of the class's rating when no qualifying segment
exists, never by rejecting the seed.

**EFFECT-SIZE FLOOR (S6 review, RR F2 — blocks suite generation until met).** The
strictly-required set IS the shared class's IRB-applicable segments (the successor is its
sole post-swap holder), and the maximum measurable arrival-information effect is bounded
by them: for every other segment some other post-swap worker scores identically, so
newcomer information buys nothing there. At ~1 such segment the maximum effect
(≤ 0.117 of the oracle, normalised) is BELOW the minimum detectable effect
(Δ ≈ 0.13–0.20 at n=9/cell) — a suite of admitted instances would be sub-detectable by
design and would look fine. Requirement: segment allocation is biased so the SHARED class
carries **2–3 IRB-applicable segments**; the K2 headroom-vs-k curve is re-read after any
change to this sampling (free, printed by the acceptance).

**THE PUBLISHED MAX-EFFECT QUANTITY IS THE CHANNEL-EFFECT CEILING (S7 review, RR F1 —
supersedes both earlier quantities, each retired with its reason).** History, kept
because each revision taught something: (v1) strict-set score share — overstated by
tie-inclusive counting, then structurally ~1 segment; (v2) M/oracle where
M = oracle − oracle_without_successor — restored a large number (~0.35) by counting
CAPACITY, not information: RR's drop-an-incumbent comparison showed ~80% of M is "a warm
body arrived" (mean 2.936 vs 2.363; coverage-attributable ≈ 0.068 of oracle), and M's
counterfactual (successor absent) is realised by NO cell in §8's grid — every cell has
the successor; channels move WHICH segments it gets, not WHETHER it exists. (v3, CURRENT)
**channel_effect_ceiling = oracle − E[ignorant assignment]** — a capacity-respecting
assignment that ignores coverage, seeded Monte-Carlo (draw count disclosed): the quantity
the cells can actually move. Measured band on current instances: **0.09–0.18 of oracle**,
with the full-channel scripted baseline only ≈ 0.03 below oracle. M and the strict list
are PUBLISHED AS DIAGNOSTICS (M beside its drop-an-incumbent comparator so the
capacity/information split stays visible); K2's disclosure carries the thresholded
quantity, diagnostics marked diagnostic-only.

**The declared MDE is 0.20, PROVISIONAL — and thresholding on the NEW quantity is
DEFERRED to the post-pilot re-derivation (S7 LS ruling; reasoning on record).** RR's
0.20 rested on three reasons: (1) σ imported from the DS substrate (P14); (2) bimodality
risk; (3) max_effect was a CEILING vs an expectation — optimism × optimism. Reason (3)
DISSOLVES under v3, which is already the realisable band, and reason (1) cuts BOTH ways:
rejecting most of a suite because an imported σ makes the honest band (0.09–0.18) sit
below an MDE derived from that same import would decide the design's fate on the least
defensible number we hold. Ruling: instances are FLAGGED (not rejected) where
channel_effect_ceiling < 0.20; the pre-stated sequence runs — pilot measures σ on the
deterministic-regret DV → MDE re-derived → gate re-runs at zero cost and rejection
resumes at the measured threshold. If the measured σ leaves the band undetectable at any
affordable n, the design fails HONESTLY and is redesigned — that fact is confronted, not
deferred: it is stated here and in every gate report until the pilot answers it.
Adjustment accepted by RR with reason 3 struck ("optimism × optimism" — v3 is an
expectation, not a ceiling) and TWO CONDITIONS, both adopted:
**C1 — the flag gates something named:** S8 assembly and S9 logging may proceed on a
flagged suite; **no flagged instance contributes to a reported finding or benchmark
release until the MDE is re-derived and the gate re-run.** A flag that gates nothing is
a note, and notes get built on (§77c).
**C2 — pilot selection is never conditioned on channel_effect_ceiling:** the pilot's
instances are selected randomly or stratified ACROSS the band, with the selection rule
recorded BEFORE any run — else σ is measured on a sample chosen by the quantity it will
threshold, the one genuine circularity in the sequence. σ predictions are pre-committed:
RR ≥0.13 (bimodal end; wrong if <0.12, said in advance), LS 0.08–0.12 (support-point
dampening under exact consumption; discriminating boundary ~0.12–0.13); RE's requested
at pilot authorization. The shared-class
segment count (`shared_class_segments`) is itself a DISCLOSED KNOB (K5) with its own
short curve — RE's restraint at 4-of-9 over 5-of-9 is endorsed, and the rule is about
disclosure, not magnitude. Rejected sweep rows name their rejection cause.

**Attainability is not discoverability.** O3 guarantees the oracle is attainable. It says
nothing about whether the manager can find the route — and that gap *is* the regret being
measured. A passed O3 must never be read as "the manager can succeed here".

## 6. Behavioural gates (what arithmetic cannot settle)

**Per-env gate.** 2 SSRs, flash, clean pair, no instruments. PASS = (i) ≥1 correct post-swap
output demonstrably via the successor's method (truth-match, not the declaration — the
0/221 declaration-accuracy figure is tool-swap-regime evidence and does not transfer), and
(ii) ≥1 post-swap task assigned to AND executed by the successor id. "The gate passed"
licenses **capability only**, never "the perturbation is validated". Study cell 1 = the
information-absent cell = the allocation-visibility gate.

**Fabrication-not-fallback (first linchpin check, §132).** A worker lacking coverage for a
unit still holds the tool that would compute it, so the failure mode is **inventing the
missing parameters** rather than falling back — producing a well-formed number with a method
line and the right format. Precedent: the DS junior relayed the z-rule number every time with
zero self-correction (14/25/91/92 against a truth of 100).

- **Check first**, before anything is built on it: hand a worker an out-of-coverage unit and
  observe **three** outcomes — falls back to the universal method / refuses / **fabricates**
  — with fabrication split into tool-calling and in-head. A two-outcome check would report a
  pass while the in-head route runs.
- **Detector liveness is ENVIRONMENT-SCOPED (S10 pre-probe, RE's own disclosure of an S9
  defect):** env-1's workers hold COMMUNICATION TOOLS ONLY — and RE's follow-up verification
  upgraded the cause from design property to FORK-WIDE PLUMBING BEHAVIOUR:
  `register_ai_agent`'s `if not additional_tools` conditional means the base AI toolset
  (analyze_data, calculate_metrics, …) is SILENTLY DROPPED for every worker holding
  comms tools — every AI worker in every engine-driven run in this fork. RULED: recorded
  as an UPSTREAM-LIMITATION-class CHANGED.md entry, NOT patched mid-study — a fix would
  hand workers a calculator after S8's acceptance and invalidate bundle comparability;
  deliberate tool provisioning is decided AT THE SCHEDULED REGENERATION with the
  in-coverage fidelity data (note: a calculator does NOT collapse the coverage gap —
  the withheld thing is DATA, which no compute tool derives — so the calculator no-go
  does not bar it; the decision is about execution fidelity and detector liveness, not
  gap integrity). Comms tools are also DUPLICATED (two comms modules both reach the
  agent) — recorded; dedupe at regeneration. All arithmetic is in-head by construction
  meanwhile. Consequences: the tool-calling fabrication
  bucket is STRUCTURALLY ZERO (an environment property, never a model result); the TRACE
  and ABSENCE detectors are structurally inert here (nothing passes invented parameters
  through a tool; the absence condition holds for faithful and fabricating workers
  alike) — the VALUE detector is the only live one, which is safe because it was ruled
  primary and needs no trace, and absence never CREATES hits (it only labels variants),
  so S9's set-equality acceptance stands. S9's synthetic compute_rwa fixture
  misrepresents production and is recorded as such. §2's "every worker holds every tool"
  is READ AS CAPABILITY-PARITY as implemented (methods-as-instructions + provisioned
  data); a SHARED compute tool is a candidate change AT THE SCHEDULED REGENERATION —
  it would make execution fidelity tool-mediated and the trace/absence detectors live —
  decided there WITH the in-coverage fidelity data below, never mid-suite.
- **The 1e-6 irb_matching tolerance has a FALSE-POSITIVE mechanism in this environment
  (S10 pre-probe, RE's disclosure — opposite direction to the round-PD residual and
  larger):** a FAITHFUL in-coverage worker computing ASRF in-head cannot plausibly hit
  six significant figures, so it classifies NEITHER = the fabrication class —
  potentially ~100% of in-coverage IRB segments. Out-of-coverage buckets are unaffected
  (SA fallback is a single exact multiplication; any IRB attempt without the calibration
  IS fabrication by definition), so S10's primary number stands. RULED SEQUENCE: the
  probe reports the raw in-coverage error distribution; the tolerance BAND separating
  approximate-faithful from fabricated is chosen by the TEAM from that distribution —
  never retuned by the implementer to admit the errors observed — and the band decision
  is a PRE-PILOT GATE ITEM: no study episode is scored until it lands.
  **The band is chosen from n ≥ 15 trials on the PINNED build, never from n=6 (S10, RE's
  counter-proposal, adopted over LS's cheaper re-run-the-same-6):** the band is an
  instrument setting that scores every study episode, relative-error distributions here
  are skewed and heavy-tailed (one dropped factor of 10 moves a median of 6), and
  choosing it from six numbers is the SAME ERROR CLASS as the C=4 cap generalised from
  one instance and the K5 curve read off one seed — twice-committed, so the rule is now
  general: **any number that becomes an instrument setting is estimated with a reported
  SPREAD, never as a point from a handful.** Trials are STRATIFIED across round-PD and
  non-round rows (the S9 F1 intersection), so the band can be conditioned on the
  anti-conservative case. The rolling-route 6 become a free TRANSFER CHECK: if the
  pinned distribution sits inside the rolling one, the model-pin split is immaterial for
  this quantity, stated with numbers instead of assumed. This also closes RR's withdrawn
  item (8) at n ≥ 15 real IRB-branch cases rather than n=0.
- **In-head IRB execution fidelity is an UNVERIFIED assumption (n=1: attempt 6's single
  irb_matching deliverable).** Covered workers compute the ASRF formula in-head from
  provisioned calibrations; if that approximates rather than computes, execution loss is
  inflated everywhere — a direct σ inflator bearing on all three pre-committed σ
  predictions. The S10 probe DOUBLES as the fidelity measurement: ~6 in-coverage trials
  (covered worker × IRB segment) report the in-head-computed value against the
  provisioned-parameter truth. This is env-1's sibling of env-2's Fellegi–Sunter
  execution-fidelity first check, which the record already required there.

- **What the probe decides (S3 review, RR):** the private parameter is not INACCESSIBLE —
  a model produces a plausible PD fluently from published default studies; it is merely not
  the instance's. The gap therefore holds for SCORING (a fabricated PD matches neither
  truth) but not behaviourally. **Coverage-as-gap is valid iff fallback or refusal is
  dominant; a high fabrication rate turns out-of-coverage workers into a noise source on
  the primary DV (execution loss swamps allocation loss) and forces a coverage-mechanism
  redesign. The probe can retire §2's mechanism, not just characterise it.**
  VALIDITY LADDER, pre-stated by RR before any trial output (adopted; not revisable
  after the result): fabrication ≤15% → survives cleanly; 15–35% → survives
  CONDITIONALLY — fabrication rate reported per cell as a covariate, and if it differs
  by cell the channels are confounded with fabrication propensity; >35% → RETIRED as a
  competence mechanism (response fork: a prompt-level fallback-salience fix + RE-PROBE,
  since that is an environment change requiring re-validation — or accept that the
  environment measures something other than §2 claims). And the substrate-vs-finding
  line, verbatim: a high rate is a publishable finding about LLM workers under
  missing-input conditions, "but it cannot be both the study's substrate and one of its
  findings — if it lands high we choose which."
- **Detector (§134 — the trace-only assertion is UNSOUND alone).** The trace assertion fires
  only if the worker calls the tool; the named failure mode is fully available in-head (the
  calculator no-go one level up — published formulas, fluently invented parameters), and an
  in-head fabrication leaves NO tool signature, breaking the tool-signature leg of
  trace-distinguishability exactly in the case the detector was built for. The surviving
  sound leg is truth-value. Three assertions replace the one:
  1. **Value-based (primary, sound):** every output classified SA-matching /
     method-matching-with-this-worker's-parameters / **neither** — "neither" is the
     fabrication class. Computable from the answer key alone; needs no trace.
  2. **Trace-based (secondary, kept):** tool called with arguments never provisioned to that
     worker. Catches the tool-using variant; free.
  3. **Absence-based:** a method-declared output with no corresponding tool call in
     `worker_run_completed.payload.history` — the specific signature of in-head fabrication.
- **Generator requirement (S9 ruling — measured and bounded, no longer merely asserted):**
  the coincidence probability of a fabricated guess landing on a true value is MEASURED
  per bucket with an explicit guess model (never a significant-digit proxy, which passes
  on values still easy to hit), BOUNDED, and PUBLISHED per instance. Known residual on
  the current 1e-6 PD grid: worst bucket ≈ 1-in-424, 2–3 weak buckets per instance —
  FALSE-NEGATIVE-ONLY (a fabricator exonerated, never a false hit), expected false
  exonerations well below 1 at study size. The finer grid is deliberately deferred to the
  POST-PILOT REGENERATION (already scheduled by the MDE re-derivation), where it rides an
  existing invalidation cascade instead of forcing one. **The REAL exposure is
  round-valued PDs, not the flagged low buckets (S9 review, RR F1):** a fabricator emits
  round numbers, so the uniform-guess model is conservative for irrational-looking PDs
  and ANTI-conservative for round ones — 13 of 360 generated PDs carry ≤2 significant
  digits, 10 of them exactly 0.0005 = the Basel input floor, the single most guessable
  value in the domain (coincidence near 1 under a round-number guesser). Responses:
  round-valued PDs reported per instance beside the weak-bucket list NOW; exact-floor PDs
  excluded from generation AT THE SCHEDULED REGENERATION (floor-pinned values are also
  slightly unrealistic as calibrated estimates). Scope notes on record: the value-based
  detector's IRB branch has real-data evidence of **n=0** — the "1 irb_matching" in S9's
  clean baseline was SYNTHETIC, constructed from the answer key (a three-way provenance
  conflation: RE's report said "clean baseline" without "synthetic", RR's item (8) and
  LS's pre-registered puzzle both read it as live; corrected by RE before the probe
  landed; whether attempt 6's LIVE bundle contains any irb_matching is inspected with
  the probe results). RR withdrew their item (8) and added the precision point: the IRB
  branch is CLOSED by the 6 in-coverage fidelity trials (n=6 real when landed), never by
  the out-of-coverage main body (an uncovered worker cannot produce a correct
  provisioned-IRB number); any in-coverage trial landing on a round-PD row is flagged —
  the intersection of the two S9 exposures, the strongest single real-data case. RR's
  direction-of-error note is recorded as a PATTERN datum: reporting more real-data
  support than existed drifts in the same direction as the five elision instances —
  toward the claim being supported — extending the drift pattern from quotations to
  EVIDENCE. Their §A rule (provenance does not carry across transcript sections; every
  section names its own data source or reads as unknown) is theirs to fold. Records 3/4
  carry SYNTHETIC-ONLY evidence until their named closing run — **the ask cell's first
  episode** (S10 and S11 generate no message traffic, so "next live episode" would close
  nothing while appearing scheduled).

## 7. Admission criterion — adopted (§134)

An instance enters the released suite only if all three hold:

1. **Bit-identical regeneration, agent-free.** `generate(seed) → score(fixed_outputs)` is
   bit-identical across two independent processes (≥2 `PYTHONHASHSEED` values; total sort key
   `(-count, str(key))`; the test is byte-identity of the artifact, never "the reported line
   is fixed"). ClawMark's original criterion re-runs the AGENT and compares checker verdicts;
   ours must not — CHECK-2's within-seed nondeterminism (dominant on 10 of 12 DVs in
   `check_variance.txt`, which now includes the three allocation-family DVs added after §89 —
   themselves within-seed-dominated at 0.587/0.659/0.852) would reject every instance. What
   is admitted is instance + scorer determinism, nothing more.
2. **Interior spread** — inside the declared floor and ceiling (§4.3), with the knob
   disclosures attached.
3. **Scripted-baseline triviality gate.** A deterministic label-matching baseline — route
   each unit by matching its surface labels to worker coverage labels, given the FULL-channel
   observation — must NOT attain the oracle score. An instance a script solves by surface
   matching measures lookup, not management.

Cite ClawMark (arXiv 2604.23781) for the criterion's origin — their second independent
arrival at one of our rulings, after no-LLM-judge; the two adaptations are ours and are
stated as such.

## 8. Study-1 cell grid (lead; revised per the reviewer's five-hole pass, §135)

Channel cells; the instance suite and every generator knob (k included, §4.3/§5) are
IDENTICAL across swap-carrying cells — conditions differ in information only. Trace (C4) is
the post-hoc substrate in every cell, not a manipulated in-episode channel in study 1.
Study-1 scope: the ACCURATE-announcement condition (unreliable/stale-content variants are
env-2 / study-2 territory).

**Every contrast is MARGINAL.** Behaviour — artifacts, outcomes — is an always-present fifth
channel in every cell. A null therefore licenses "channel X added nothing beyond what
behaviour already showed", never "channel X had no effect". [§135]

| Cell | Swap | Card (C1) | Declaration (C2) | Ask (C3) | Role |
|------|------|-----------|------------------|----------|------|
| U    | **none** | n/a | n/a | n/a | unswapped control — licenses the JOINT effect of the swap AND the roster change it entails, never "the replacement effect itself" (RR, R2: U keeps the predecessor while 0–4 have the successor, so U-vs-0 differs by whether a swap occurred AND by which three workers are present; those are not separable, and U's oracle is over a different team. Inherent to having an unswapped arm at all — scoring U against its own roster remains right — but the claim is the narrower one) [H2] |
| 0    | yes  | predecessor's on file | absent | disabled | information-absent control; allocation-visibility gate |
| 1    | yes  | **updated at t_swap** | absent | disabled | card channel (marginal) |
| 2    | yes  | predecessor's on file | **present** | disabled | declaration channel (marginal) |
| 3    | yes  | predecessor's on file | absent | **enabled** | ask channel (ride-along; replying is behaviour) |
| 4    | yes  | updated | present | enabled | **CEILING** — with everything available, how close to oracle? A bound, NOT an interaction claim |

Cell U scores against its own roster's oracle (the pre-swap roster persists), so U-vs-0
compares regret against each cell's own attainable optimum. Single-channel-added contrasts
run against cell 0; card-vs-declaration style comparisons are differences of differences and
are labelled indirect. Estimator per §4.4: arm-paired on (seed, pairing unit).

**Interpretation rules, pre-committed:**
- **Cell 1** is reported conditional on the updated card having been RENDERED into the
  manager's observation after `t_swap` (logged; a reported DENOMINATOR, never a stratifier) —
  otherwise the cell measures re-reading, not card consumption. [H3]
- **Cell 3** reports the ask rate per cell; if it is near zero, cell 3 is a REACHABILITY
  result and is reported as such — not as evidence about the ask channel. [H4]

**Sizing — RESEARCHER RULING (2026-08-07): quick-test-first.** The A/B/C powered-release fork
was declined as too long; the ruling is short runs for quick testing. Adopted structure:

- **Pilot selection rule (C2, S7 round 2 — write down BEFORE the pilot is specced):**
  pilot instances are selected randomly or stratified ACROSS the channel-effect band,
  never conditioned on `channel_effect_ceiling`, and the selection rule is recorded
  before any run — else σ is measured on a sample chosen by the quantity it will
  threshold.
- **K5-curve interpretation, pre-stated (S7 round 3, RR):** if K5 moves the v3 ceiling
  substantially, it is a real rescue lever; if only slightly, the honest conclusion is
  that the environment's channel effect is SMALL AND NO KNOB RESCUES IT — a design
  finding, recorded as one, not a trigger for a fourth-knob search.
- **K5-curve OUTCOME (S7 close): a THIRD case the rule did not anticipate, resolved to
  the design-finding branch.** The curve is HUMPED (24 seeds; medians 0.123 / 0.153 /
  0.145 / 0.133 at n=2..5) and the current n=4 sits near the peak: movement is
  substantial relative to the estimator SE (the rule's "rescue lever" antecedent) yet
  retuning to the apparent peak gains +0.008 against a 0.055 gap to the MDE — within the
  trust width at 24 seeds. RULING: setting UNCHANGED (chasing a within-noise +0.008 is
  knob-tuning); the band 0.076–0.186 / median 0.146 IS the environment's channel effect;
  no fourth-knob search; the pilot's measured σ decides studiability. Recorded beside
  it: the single-seed K5 curve reads MONOTONE where the 24-seed truth is humped — the
  C=4 single-instance error class, avoided because RE computed the multi-seed table IN
  the acceptance as a committed artifact (records/S7/k5_ceiling_curve_multiseed.json),
  never quoting a curve from a DM.
- **Rule re-worded in place (RR, closing the third case):** a lever is a RESCUE only if
  it CLOSES THE GAP TO THE MDE, not if it moves the quantity — movement was substantial
  by any statistical reading (~37 SEs), sufficiency was not (+0.008 vs 0.055). Declining
  the retune also avoids fitting the knob to sampling noise in the gate's own curve
  (the argmax of a shallow 24-seed hump is an estimate, not a setting).
- **The hump is PREDICTED by capacity, not merely observed (RR):** below cap C the
  shared class's extra segments add effect; at and beyond it they must be served by
  someone else regardless of coverage, so the marginal contribution turns over — the
  peak is a CONSEQUENCE OF C, not a free parameter. A future C change moves the peak in
  a knowable direction; no new sweep required to believe it.
- **The design finding PRICES the study rather than killing it (RR, pre-stated so the σ
  result arrives as a costing decision, not a crisis):** at median ceiling 0.146,
  detection needs roughly **n≈8/cell at σ=0.10 and n≈17/cell at σ=0.15** — the pilot's σ
  selects between the current 45-episode budget and roughly double it, and the correct
  response to the unfavourable branch is MORE EPISODES PER CELL, never another knob.
  Caveat pushing the same way: the ceiling is ignorant-vs-oracle while the realised
  contrast is informed-vs-cell-0, both strictly interior — the realised effect sits
  BELOW the ceiling, so those n are floors.
- **Episode wall-clock for authorization math (S8, stated as a range with its condition
  per RR):** ~30 min per completing episode WHEN assignment is bulk; up to ~45–50 min if
  the manager dribbles single assignments. n=1 base (attempt 6; five of six launches did
  not complete) — treat as planning input, not a measurement.
- **Pilot tier (the first authorized runs): cells U, 0, and CEILING × 3 seeds = 9 episodes**,
  plus the gate pair (2 SSRs) and the fabrication probes (~5 model-call trials, not
  episodes) — roughly half a day of flash in total. The pilot answers the three gating
  questions in cost order: (i) the MAXIMUM-information contrast (0 vs ceiling) — if
  allocation does not move with everything available, single channels are moot (the cheapest
  decisive test); (ii) the swap effect (U vs 0) at pilot precision; (iii) REAL
  within/between-seed variance on regret, replacing the P14-provisional CHECK-2 priors.
- **Single-channel cells (1–3) and full-grid sizing are DEFERRED until pilot variance
  exists.** H1's power fact stands recorded for the eventual release: whatever its size, it
  is sized on the continuous statistic, never the sign test, and every null cell is either
  equivalence-powered or pre-labelled underpowered-by-design at release.

Oracle, worst, and the scripted baseline cost zero episodes (offline arithmetic). Prediction
protocol before the pilot runs: all three commit predicted contrasts, LS first, peers by DM.

## 9. Open items carried into v2

- The Basel implementation is **unvalidated against published worked examples** (0.5–1d,
  precondition, not done).
- Fellegi–Sunter **execution fidelity** is env-2's first check: an agent asked to sum
  log-likelihood weights may approximate rather than compute, and if that arm cannot be
  executed the environment collapses to one matcher.
- The **usable-window search** for env-2 is offline arithmetic and is the sensitivity gate
  run as a sweep; the window is a region in ≥2 parameters because the published deficiency
  bound is per-record while degradation is a mixture.
- **No linchpin evidence anywhere.** Every number in this spec assumes faithful execution.
