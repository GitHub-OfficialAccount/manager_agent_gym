# STUDY 1 FOUNDATION — the authoritative brief

_**AMENDED 2026-08-08** (L1/L4/L7, three dated amendments in §4 and §5, marked ★): load feedback
is part of the SETTING and constant across cells; the central claim carries the exactly-binding
capacity qualifier; and the primary DV is redefined over ASSIGNMENTS because the pre-revamp
`rerouted_share` was completion-derived. Amendments are additive and marked — the superseded text
is retained. Drift audit: `records/L4/drift_check_LS.md` + `L4_review_RR.md`._

_Status: AUTHORITATIVE as of 2026-08-06 — reviewer-verified claim-by-claim at 22ca6a5 (five
corrections applied and read; "no residual objections"). Open researcher decisions in §10. Supersedes the direction content of OVERVIEW.md, PREREG.md, ARM3_SPEC.md, and
REVAMP.md (all now in `archive/`, retained as records with banners). Every claim carries its BRAINSTORM.md section
pointer; BRAINSTORM is the audit log and is never edited, only annotated. Written by lead-scientist;
verified claim-by-claim by reviewer-reproducer (pending); spec details owned by research-engineer in
STUDY1_LOGGING_AND_ORDERING.md._

## 1. The question

When a manager agent's worker is replaced mid-workflow by an event the manager did not choose,
which sources of information about the newcomer actually change the manager's decisions? [§115–116]
(Non-consumption of a channel is a null-shaped claim under §5's own pricing — where observed it is
reported as underpowered-by-design, never asserted; the headline question is the positive half.)

Plainly: a manager runs a workflow — interdependent tasks, standing descriptions, partial results.
One worker is swapped (model upgrade, vendor restaffing). The newcomer is fully capable but works
differently. The manager can learn what it got from four sources: the registry **card** (still
describing the predecessor — stale by succession, nobody fabricates anything), the newcomer's own
**by-product self-descriptions** (`method:` lines in its outputs), **asking** it (it may answer
well, badly, or not at all), and its execution **trace**. We measure what the manager does with
these sources on the one margin it owns and that demonstrably moves: **who gets which task** — plus
whether it re-specifies the now-wrong task descriptions, and whether it ever asks. [§116, §99–100]

Scoped OUT: in-place behavioural change of stateless configured workers. Agreement with the
researcher on record: such workers do not change, they get changed; what looks like in-place change
in real scenes decomposes into replacement, negotiated (announced) change, or human drift. In-place
change survives only as the learning-teammate horizon (memory-bearing agents, drift-by-design) and
the human umbrella. [§115] The switching ≈ announced-in-place-change equivalence is OUR modelling
decision, argued on its merits — GPL's formalism permits both and its instantiation studied only
leave+enter; the field distinguishes the cases. [§117–118]

## 2. The event and its realism

The frame is **open-team management**: members arrive, leave, and get replaced — handling
composition change is a manager's job description, and every real scene we examined has it
natively. Study 1's event is the minimal composition change: **one-for-one replacement, team size
constant**. Arrival is visible by nature in the SCENE (the roster changes) — and build item 1
exists precisely because it is not yet visible in the SUBSTRATE. That the manager's behaviour
actually reflects the roster event is an ASSUMPTION CHECKED AT THE GATE, not a property of the
scene: CHECK-5 showed the roster channel is queried (282/2100 actions) but not consumed into the
choice on fixed teams. If a manager sees the arrival and still allocates as if the predecessor
remained, that is not a design failure — it is the first entry in §7's failure taxonomy. [§115,
§116, CHECK-5]

Use cases (motivating, not asserted as measured facts): a team member's agent swapped for a more
advanced model mid-project; incident response (forensic firm rotates responders mid-breach);
eDiscovery (vendor restaffs reviewers mid-matter); product recall (supplier swaps engineers);
post-merger integration (acquired staff replaced mid-integration); agent platforms (a worker behind
an A2A/AgentCard-style card is upgraded while the published card lags — cards are shipping
infrastructure, so card staleness is a protocol-level fact, not a contrivance). [§116]

The current data-science scenario is defensible under this framing: a worker being upgraded or
replaced mid-workflow is natural in ANY internal workflow. The richer stranger-scenes (eDiscovery,
integration, recall, breach — §114a Tier 1) are the paper's motivating scenes and generalization
targets, not study 1's substrate.

## 3. Novelty — the four-property intersection (every neighbour read at full length)

We study a setting with four properties whose combination no prior work holds. Contribution
sentence in POSITIVE form ("we study X", neighbours cited per property); the literature search is
documented in the paper so the positioning is auditable. [§116–118, P7 discipline]

External scoop check, reviewer-verified at primary source (2026-08-06;
`SCOOP_CHECK_2026-08-06.md`, BRAINSTORM §131–133): no work matches ≥3 of the four properties;
the nearest neighbour is DRAMA (arXiv:2508.04332v1 — cite v1 ONLY, never the retitled version)
at 2.5/4. Our platform's own upstream paper (Masters et al., DAI '25, arXiv 2510.02557) names
the setting an open challenge — "This defines the classic ad hoc teamwork (AHT) problem—a
long-standing challenge in multi-agent systems." (§4.3) — while its evaluation holds team
composition fixed within a workflow: the problem is stated there, not studied. And the EVENT is
staged by no one: DRAMA stages Agent Dropout (size falls) and Agent Addition (size rises) as
separate scenarios — one-for-one, size-constant, mid-workflow replacement appears in no
neighbour. [§131–133]

1. **The response is an allocation decision one agent holds.** Nearest prior: M3RL (Shu & Tian,
   ICLR 2019) — a trained manager assigning to unknown workers, with team membership resampled and
   workers replaced BETWEEN episodes ("75% of the workers will be replaced with new ones after
   every 2,000 episodes"; no within-episode replacement anywhere), self-described as "ad-hoc worker
   teaming" — and behaviour as its ONLY channel (its sole alternative is a ground-truth oracle
   baseline). Classical open-AHT egos (GPL/CIAO/NAHT) are peers acting in the
   teammates' own action space; AgentVerse's assignment emerges from group consensus, no single
   decider. On the LLM side, DRAMA's control plane holds a centralized single-planner allocation
   (Dual-Capacity Hungarian over affinity scores) under exogenous roster events with
   deterministic scoring — the nearest LLM prior on this property. [§116, §117, §118, §133]
2. **The newcomer inherits persistent workflow state** — outstanding tasks, artifacts, and
   descriptions written for its predecessor. Held by NO neighbour on any side (grid/SMAC worlds are
   stateless in this sense; M3RL has contracts but no standing task graph; DRAMA's takeover
   module reassigns "unfinished tasks" for RE-EXECUTION — no authored artifacts or standing
   descriptions pass to anyone). The uncontested vertex, and the precondition for
   staleness-by-succession. [§117–118, §133]
3. **The newcomer has an information interface beyond behaviour.** The CAT line (SOMALI CAT; EDP)
   prices truthful, noiseless, mechanism-forced goal queries; the Provenance Paradox studies
   ADVERSARIALLY inflated cards with a rule-based router. DRAMA's allocator DOES read a
   capability input — affinity evaluations "consider factors such as agent capabilities,
   location, and current workload" — but as a single always-accurate system attribute of a
   resource object: no unreliable, absent, or competing channel, and no manipulation of channel
   availability. FlyRoute (arXiv 2605.22057) is the closest work on the card channel — a
   developer-provided registration description that "may be incomplete or inaccurate, but it
   serves as the initial signal for cold-start routing" — and it SOLVES that unreliability by
   learning a better profile from observation: the engineering response to the condition we
   MEASURE. Ours: incidental staleness (the world
   moved — not zero-mean, no noise parameter recovers it), by-product self-description (unasked,
   non-pedagogical — nearest prior structure: Torrey & Taylor's stipulated student announcements,
   three differences named), answering-as-behaviour (open language, no forced reply — cf. workers
   addressing nonexistent recipients), and content over an unknown change space. [§110–112, §133]
4. **The change is exogenous** — cited ONLY against the LLM-orchestration line (AgentVerse
   recruits, DyLAN selects, and their 2025–26 successors — Puppeteer, LATTE, AdaptOrch, ATM — all
   cause their own composition changes). NOT a standalone
   claim: GPL's openness is exogenous, unannounced, and mid-episode — and DRAMA's dropout and
   addition events are exogenous too (random removal "simulating a crash or disconnection").
   Exogeneity never leads alone; the wedge inside the conjunction is (2)+(3). [§117, §131, §133]

Claims we may NOT make: "the field models change as leave+enter" (GPL's formalism permits both);
G1/G3 as originally drafted (communication and its pricing are named AHT solution methods);
"nobody studies manager adaptation to replaced workers" (M3RL); (b)-as-unoccupied (occupied
adversarially); anything cross-model (flash-only scope); 0/864 or any corpus figure as a portable
result (setup-level priors); **`mean_r_check` as corroboration** (it is downstream of rerouting —
the allocation effect's mechanism check, never a second independent result [§92]); **the within-run
attribution sentence "in runs where the manager read X, allocation was Y"** (prohibited in advance —
consumption claims are between-cell contrasts only [§91]); **"DRAMA has no capability model"**
(false — v1 twice states the allocator considers "agent capabilities"; only the
single-always-accurate-attribute formulation is defensible [§133]); **"DRAMA stages a
Replacement scenario"** (no such scenario exists in v1 — Dropout and Addition are separate,
never one-for-one [§133]); **"exogeneity distinguishes us" as a standalone claim**
(non-separating on both the classical side (GPL) and the LLM side (DRAMA) [§131, §133]).
[§109–111, §116, §103, §131–133]

## 4. Design

**★ AMENDED 2026-08-08 (L1, researcher ruling). LOAD FEEDBACK IS PART OF THE SETTING, CONSTANT
ACROSS EVERY CELL, AND NOT A MANIPULATED CHANNEL.** The manager sees truthful execution state
(`not started / running / done`), per-worker load against each capacity dimension with its
release semantics, and any refusal at the time it fires. **This is information about the
MANAGER'S OWN ACTIONS, not about the newcomer — a different referent, so it is not a fifth
channel** (checked: nothing refuses on scope and the allotment has no per-worker override, so a
refusal cannot distinguish predecessor from successor).

**Why it is in the setting rather than absent, in the brief's own terms:** §3 property 3 records
that DRAMA's allocator considers *"agent capabilities, location, and current workload"*. Before
this amendment our manager had NO workload signal at all — **we were behind the nearest
neighbour on an input this document itself cites. L1 is PARITY, not innovation**, and should be
described that way.

**★ SCOPE CONDITION ON THE CENTRAL CLAIM — carried here from the thread because a condition that
lives only in a DM will not survive into the paper.** The finding that coverage information
cannot address the dominant allocation error holds **IN A REGIME WHERE CAPACITY BINDS EXACTLY**:
C=3 × 3 workers = 9 segments leaves no slack, so every coverage-driven preference must be
overridden somewhere and coverage-optimal play itself violates the cap. **With slack, coverage
and feasibility would not compete.** Without this qualifier the claim reads as "coverage channels
are useless", which is far larger than anything measured.

**Substrate:** the existing worker_replacement scenario (workers, tools, computable ground truth)
unchanged. **The event:** predecessor removed + successor added at the swap timestep via the
existing registry scheduling (verified end-to-end; applied before the manager acts). The successor
carries a NEW agent id — identity is itself a second trace signature via
`worker_run_completed.actor_id`. [§116, RE receipts]

**★ AMENDED 2026-08-09 (researcher ruling). THE PERTURBATION IS A CAPABILITY DIFFERENCE, NOT A
METHOD SUBSTITUTION.** The successor is **certified for different asset classes** — equally
competent, differently *permitted*. Everything measured in the L9 phase is this, and §3's novelty
argument was already written for it (its neighbours on property 3 are capability/profile routers:
FlyRoute's registration description, DRAMA's "agent capabilities" input). **The paragraph below
described a method substitution and is SUPERSEDED as the perturbation** — it is retained because
its three requirements (allocation-visible, trace-distinguishable, successor-reachable) still bind
and are satisfied by a capability difference: allocation-visible because coverage decides who can
unlock IRB; trace-distinguishable because the SA fallback is visible in the reported metric;
successor-reachable per the gate. **Ruling made on realism grounds: a certification difference is
what a restaffing produces, and it is the only reading under which the manager's information has a
job to do — when a capability leaves the team entirely, no channel can recover it.**
_(Superseded text follows.)_

**The perturbation (successor's difference):** prompt-level method substitution under three
requirements — **allocation-visible** (the difference must give the manager an allocation reason;
allocation is the only affordable DV), **trace-distinguishable** (distinct tool call and/or distinct
truth value — "demonstrably via method B" = reported metric matches method B's computed truth, both
already in `_audit_total`), and **successor-reachable** (see gate). [§92, §98, §116]

**Channels / cells (main effects only — the factorial is unaffordable [§91]):**
- **Roster event** = the arrival announcement (rendered into the manager's observation — build item
  1). Held constant across cells; arrival visibility is not a studied variable. [§93, §116]
- **Card**: present-and-stale (predecessor's card stays on file — manufacture-free) vs updated.
  [§116]
- **Declaration**: the successor's `method:` lines — present / absent (`WORKER_PROMPT_NO_METHOD`,
  n=0 executed; first run is diagnostic). Declaration accuracy must be RE-ESTABLISHED under the new
  perturbation before any cell leans on it (0/221 is tool-swap-regime evidence). [§98]
- **Ask**: ride-along interrogation; the manager-addressed reply is part of the MANIPULATION (workers
  don't produce the manager's id spontaneously — 2/56); answers truthful / stale / mute. [§101, §100]
- **Trace**: post-hoc substrate (build deferred until its cell runs; never through observation_aid;
  no operand normalisation — S6 non-foreclosure). [§83, §104]
- **Control**: no-channel cell — scientific control, no ecological claim. [§106, §115]
- **Descriptions are stale by succession in every study cell** (written for the predecessor;
  byte-identical to pre-swap text, asserted in logs — never authored) — the standing reason for
  `refine_task`, read positive-only. Gate pair only: descriptions consistent with the successor's
  method. [§94, §97]

## 5. Measurement

- **Primary DV: the allocation margin** (rerouted_share family) — task denominators, never worker
  denominators; constant n makes shares comparable; any future size-changing variant invalidates
  cross-variant comparison until re-derived. [§116]
  **★ AMENDED 2026-08-08 (L7). The pre-revamp `rerouted_share` is SUPERSEDED, not restored.** It
  <!-- citation-check: superseded -->
  was COMPLETION-DERIVED (`check_announcement.py:168–191` — **that module was DELETED in the
  2026-08-08 cleanup, so this amendment's evidence is no longer inspectable at source; the
  finding survives in `records/L7/rerouted_share_definition_v1.md`**) <!-- citation-check: superseded -->, so work assigned to the swap target
  and never executed left BOTH numerator and denominator — biasing the share UPWARD exactly in
  the capacity-refusal regime, the same defect as the `allocation`-from-completions bug that cost
  four retracted claims. **The DV is now defined over ASSIGNMENTS**, with: an explicit denominator
  predicate (*segment tasks assigned to an agent still on the roster at a later manager decision
  while not terminal AT THAT STEP*); **FORCED and DISCRETIONARY moves separated and never summed**
  (73% of pre-L1 moves were forced — the source had departed, so moving was the only legal
  action); forced moves analysed on DESTINATION; and the conditioned share (≥2 capacity-legal
  destinations) PRIMARY for any channel claim, since a move with one legal destination is not a
  choice. It measures BEHAVIOUR, not correctness — **a move is consistent with using any channel
  or none**, so attribution still needs the channel-pull record, and the regret decomposition
  stays as the separate outcome measure. Spec: `records/L7/rerouted_share_definition_v1.md`.
  _Also amended: CHECK-1's +0.611 allocation effect uses the superseded DV and MUST NOT be cited
  as evidence that a channel moves allocation — its derivation is biased toward finding reroutes._
- **Estimator: arm-paired on (seed, batch)** — successor-arm batch vs control-arm batch at the same
  seed. This EXTENDS CHECK-1's validated seed-pairing (full vs silent, 6/6 seeds, p=0.031) to the
  batch level and has not yet been validated on data. Within-run pre/post is logged as descriptive
  only (task-position and P9 confounds). [§116]
- **Secondary, positive-only:** ask propensity (vs the control arm's base rate), refine
  reachability. Attention-budget layer attached (the one corpus-verified non-degenerate graded DV).
  [§91, §84]
- **Claim discipline:** detection of large effects is cheap (~4 runs/arm on allocation); every
  null-shaped claim carries the 42–168+/arm price and is pre-labelled underpowered-by-design or
  dropped. Stratifiers must be UPSTREAM of response DVs (admissibility test: is the stratifier
  predictable from the DV?). A flash null on asking is model-specific, never general. [§89, §92–93]
- **Four logging records** (specced in STUDY1_LOGGING_AND_ORDERING.md): target's message pulls;
  refine events with before/after text; message→manager rendered-window visibility; ask-reply
  addressing. Plus the constant-n checklist as logged assertions. [§93, §99–101, §116]

## 6. The gate (before any study cell)

**2 SSRs, deepseek-v4-flash all roles, clean pair (control + successor), no instruments.** PASS =
(i) **★ AMENDED 2026-08-09 — the original read "demonstrably via the SUBSTITUTED METHOD
(metric-truth match)", which has no referent under a capability perturbation and made the gate
unrunnable as written.** Now: **≥1 correct post-swap outcome on an asset class the successor IS
certified for, with the reported metric matching the IRB truth** — the same
demonstrably-did-the-right-thing test, keyed to certification rather than to method;
(ii) ≥1 post-swap task successfully assigned to AND executed by the successor id (add/remove has
never been exercised in a live run — zero roster dynamics in all 86 corpus bundles). FAIL = zero
correct post-swap outcomes via method B. A 3/3 is recorded as "capability established,
outcome-channel signal absent" — never as non-degeneracy. Power limit carried from §97: at 1
run/arm with ~3 post-swap audits the observable support is {0..3}/3 — reliable against HARD
degeneracy only; the gate establishes non-degeneracy weakly. **"Gate passed" licenses capability
only; allocation-visibility is gated by study cell 1 = the information-ABSENT cell** (a moving
margin there licenses visibility; a flat one stops the sweep with everything downstream unspent).
Reference value (not a threshold — the criterion is support-based): control mean_r_check 0.995/14. Pinning proposal (provider pinning,
`allow_fallbacks: false`) rides the gate spec; pin-then-compare predictions are on record. [§94–97,
§101, §107, §116]

## 7. Paper shape: analysis, then the solution it licenses

Phase 1 (this design) is DIAGNOSIS — a failure taxonomy per cell: allocating as if the predecessor
remained; trusting the stale card; reading declarations without acting (the consumption failure);
never verifying; never asking. Phase 2, under a PRE-COMMITTED rule (build only if phase 1 finds
failures): a **newcomer-handling policy** — on roster change, invalidate predecessor-derived
beliefs; treat the card as a hypothesis until one trace confirms it; ask exactly when channels are
silent or conflict; re-specify stale descriptions before the next assignment. A scaffold
(prompt-structure + at most one composite action), flash-only, evaluated on the SAME cells at
detection-level cost. If phase 1 finds no failures, the paper is a capability result with boundary
conditions and no solution is bolted on. [in-thread with researcher, 2026-08-06]

## 8. Build delta (everything else exists)

1. Successor identity + roster event into `ManagerObservation` (~0.5d, CORE, CHANGED.md) — the one
   real core change. 2. Perturbation build (~2–3d; riskiest item; three requirements). 3. Stale-card
   cell (~0.25d, config). 4. Logging records + assertions (cheap, specced). 5. Framing/labels (zero
   code). Deferred: trace substrate (~1d), NO_METHOD extractor exposure (~0.5d), provider pinning
   (~0.5d, core). [§116 and in-thread]

## 9. Rules in force

See METHODOLOGY_RULES.md (consolidated P1–P14 + conventions: quote to end of sentence including
trailing citations; name the glob and file total; total sort keys with byte-stability acceptance;
title-verify fetched papers; annotate-in-place, never rewrite records; a correction is not in the
record until the corrected text is READ; verdict and mechanism scored separately (P13); kills state
their level (P14); prediction protocol before experiments and reads).

## 10. Open researcher decisions

1. Framing: state the deliberate violation of AHT Assumption 2 as the setting's defining feature
   (team recommendation; CIAO cited as the field's own statement of the line), or occupy
   "ad hoc teaming" as the named problem. [§109, §117]
2. Bless the threshold fix to the avoidability test ("available to the party bearing the
   coordination cost, at the time coordination is needed"). [§108]
3. Sign off the §3 novelty statement.
4. Decision-1 (shared tools / absorb channel): accept deferral or override. [§90]
5. The go: build delta §8, then the gate §6.

**★ SETTLED 2026-08-09 (researcher):** the capability arrangement is **PARTIAL OVERLAP** — the
successor shares one asset class with the predecessor, and the class the stale card lies about is
one an incumbent still covers. Priced natively at **2.26% of oracle at a realistic mix, non-zero on
60 of 60 instances**, against the shipped arrangement's **0.000% on 0 of 60**. Chosen on realism:
it is strongest exactly where realistic books sit, needs no sixth asset class and no larger roster,
and **ships unamplified** (forcing the mix costs it twice — draining the lied-about class and
consuming the free slot the channel needs). Pool re-derived at
`records/R2/instance_selection_partial_segs1.json`; study seeds **26, 39, 37**.
**This decision resolves the §4 ambiguity above and unblocks L3 and L5.**
