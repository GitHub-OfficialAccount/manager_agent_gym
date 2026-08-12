# BACKLOG — study-1 finance environment implementation

**How to use this file.** Flat ordered list. Work the topmost step that is not `[x]` and
whose `Depends` are all `[x]`. Update the marker in place and commit. **Do not reorder** —
the order is by DECISIVENESS (what can invalidate the most work if it fails), not by
convenience or by dependency comfort.

`[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked (say why on the line)

**Acceptance checks are mechanical.** Every step states a check that passes or fails without
judgement. A step is not `[x]` until its check has been run and its output committed under
`records/`. "Looks right" is not an acceptance check.

**Dual review (researcher mandate, 2026-08-07).** Every step is implemented by the
research-engineer and reviewed by BOTH the lead scientist and the reviewer-reproducer. A step
is `[x]` only when three artifacts exist under `records/`: the acceptance-check output,
`<step>_review_LS.md`, and `<step>_review_RR.md` (the reviewer's verdict verbatim). Phase is
tracked on the step line: `[~] (RE implementing)` → `[~] (LS pass, RR pending)` → `[x]`.
Review findings route back to the implementer; the marker reverts to
`[~] (RE implementing: fixes)`.

**Review discipline (reviewer's two points, adopted 2026-08-07).** (1) Reviews are serial, so
drift survives agreement: each reviewer reads the governing criterion in HARNESS_SPEC_v2 /
FOUNDATION FIRST, then the check, then the output — never the DM's description of what the
step was meant to do (§81: nobody inside the conversation catches paraphrase drift). A step
whose criterion is not written down anywhere is itself a finding. (2) Every verdict states
what was VERIFIED versus taken on report — a bare "pass" is a stamp, and a stamp tells you
nothing about where a later failure slipped through. Agreed in advance: a pass is a statement
about what was checked, not a warranty; a later failure RE-OPENS the step as new evidence,
never as a reversal of the earlier verdict.

**Costs** are pulled from `COVERAGE_DIFFERENTIATION_COSTING.md` (§5) and
`METRIC_AND_SENSITIVITY_SPEC.md` (§4); total 6.5–8.75d including the Basel validation.

**Spec of record:** `HARNESS_SPEC_v2.md`. Where this backlog and the spec disagree, the spec
wins and this file is wrong.

---

### S1 — Basel worked-example validation `[x]` (tier 1, 19/19; reviews in records/S1/; fix 7ac400c verified against RR's specification)
**Cost:** 0.5–1d · **Depends:** — · **Blocks:** everything downstream that scores anything

Validate the SA lookup table and the IRB ASRF implementation against **published BCBS worked
examples**. The formula is already implemented and runs (stdlib `statistics.NormalDist`, no
scipy); what has never happened is checking it against an external reference.

**First act of S1: verify source availability** (RE flag 2026-08-07 — the original check
ASSUMED BCBS publishes numeric worked examples for the IRB function; unverified). Candidate
leads, to be title-verified at full length, not asserted: the Basel II framework's
"illustrative IRB risk weights" annex tables; the BCBS "Explanatory Note on the Basel II IRB
Risk Weight Functions"; EBA materials. The SA half is not at issue — CRE20/21 risk weights
are published as literal tables.

**Acceptance (mechanical), ordered fallback — the highest satisfiable tier applies, and the
tier used is stated in the committed record:**
1. **Published numeric worked examples (≥3):** `abs(ours − published) < published_tolerance`,
   each case citing its source document and paragraph in a comment.
2. **Published curve/table anchors:** reproduce published risk-weight values at stated
   benchmark PD/LGD/M points from a citable table, same tolerance discipline.
3. **Independent reimplementation + structural anchors — WEAKER, labelled so in the record**
   (establishes internal correctness and consistency with published PROPERTIES, not agreement
   with a published NUMBER): a second implementation written from the published formula text
   by a **different agent** than the S1 implementer (a same-author reimplementation shares any
   misreading of the text), asserted equal across a PD grid; plus published structural
   properties — monotonicity in PD, the correlation bounds 0.12–0.24, and the output-floor
   relation (IRB RWA ≥ 72.5% of SA). A tier-3 pass must never later be read as an external
   check.

**Why first:** a wrong Basel implementation is wrong in a way that still looks like numbers —
every downstream artifact, spread, oracle and instance would be plausible and invalid. This
step alone can invalidate the environment design, so nothing else is worth building before
it passes.

---

### S2 — Roster-arrival render into `ManagerObservation` `[x]` (5 defects caught across 3 review rounds; reviews in records/S2/; spec gained instance-wide id opacity, leak-exclusion discipline, arrival-carriage evidence field)
**Cost:** 0.5d (core) · **Depends:** — · **CHANGED.md entry required**

Carry `agent_coordination_changes` (engine.py:413) into `manager_agent.step()`, add the field
to `ManagerObservation`, and render a "Roster changes this timestep" block in the prompt
builder. Today those strings reach only the ExecutionResult path (engine.py:601, :621), so
the arrival is invisible to the manager.

**Acceptance (mechanical):** a test that schedules a remove+add at timestep t and asserts the
rendered manager prompt at t contains both agent ids and the change verb. Plus a CHANGED.md
entry naming the three touched files.

**Why second:** it is the only core change in the plan and the announcement channel does not
exist without it. Cheap, and everything about the event depends on it.

---

### S3 — Generator: segments, coverage lattice, applicability `[x]` (reviews in records/S3/; SA + all four traps verified at source; RR limitations routed: non-nesting assertion → S5, lattice disclosure → S6, S10 dependency recorded)
**Cost:** 1.5d · **Depends:** S1

Portfolio generator emitting an instance from a seed: 8–10 segments with
`EAD/PD/LGD/M/rating/asset_class`, `irb_approved`, and a worker coverage lattice over
`(approach × asset_class)`. Coverage is **private parameters delivered as prompt data** —
never a withheld tool (core-tool rule; the calculator no-go). SA needs no private input and
is the universal fallback.

**Acceptance (mechanical):** `generate(seed)` twice in two processes produces byte-identical
instance JSON; a committed instance shows ≥2 asset classes, ≥4 workers, and every worker
holding SA over all segments. **Plus (S1 follow-through — LS ruling + RR line):** the
generator's SA risk-weight table matches published CRE20/21 values, verified against a
FETCHED PDF (the framework webpage did not render its tables), cited per value class, with
the same column-identity discipline S1's review exercised — CRE20/21 tables carry
exposure-class and rating-grade columns exactly as easy to mis-select as Annex 5's €50m/€5m
pair. The IRB functions are IMPORTED from the S1-validated module, never re-implemented
(a re-implementation voids S1 and is a review finding on this step).

---

### S4 — Truth functions, scorer, oracle and worst `[x]` (reviews in records/S4/; F4 fix 1117d3b verified against RR's specification; signed execution term + clipping now spec §4.1)
_Naming note (RR (4)): S4's fixed instance is `records/S4/instance_seed101_8seg.json` (8 seg);
S3's committed instance is `records/S3/instance_seed101.json` (9 seg) — name the FILE, never
"the fixed instance". Enumeration verifies the implementation; the bound is termwise-provable
and holds at any size by construction._
**Cost:** 0.5d · **Depends:** S1, S3

`correct(seg)` under `applicable(seg)`; `s(seg, w)` per HARNESS_SPEC_v2 §4.1;
`oracle = Σ max_w`, `worst = Σ min_w`; regret **decomposed** into allocation loss and
execution loss.

**Acceptance (mechanical):** on a fixed instance, `oracle ≥ score(any allocation) ≥ worst`
asserted over all enumerated allocations; and a hand-checked segment where allocation loss and
execution loss are non-zero and sum to total regret.

---

### S5 — Generation-time assertions `[x]` (reviews in records/S5/; six assertions incl. A4-as-canary; strict counter with exercised TIE_EPS guard; k+headroom printed; swap_shared_class published)
**Cost:** 0.25–0.5d · **Depends:** S3, S4

Five assertions, all failing loudly at generation:
1. **Non-nestedness** — pairwise subset check over the roster; no worker's coverage contains
   another's. **Inside `generate()` itself, unconditional** (S3 review, RR: the equal-size
   construction makes nesting impossible TODAY, but the premise lives in a module constant;
   a future unequal-coverage change would nest silently. The assertion converts a derived
   property into an asserted one).
2. **Capacity non-binding** — worker-timesteps ≥ segments, so the oracle stays a per-unit max.
3. **O3 oracle-routing** — **≥k segments whose ORACLE allocation routes through the
   successor.** NOT "achievable only via the successor", which is vacuous under a universal
   fallback (every worker can act on every segment; the condition can never fire).
4. **Both rosters** — achievability checked pre-swap and post-swap.
5. **Id opacity, INSTANCE-WIDE (S2 review, RR F1 + F4)** — no worker id ANYWHERE in the
   instance contains any method, coverage, or asset-class token drawn from the instance's
   own lattice or method names. Not just the swap pair: the always-rendered roster shows
   all ids in every cell, and semantic incumbent ids let the control cell read the
   coverage lattice and infer the newcomer's coverage by elimination. Spec:
   HARNESS_SPEC_v2 §5 "Identifier opacity" + "Leak-exclusion discipline".
6. **No zero-fallback IRB segment (S4 review, RR F1)** — no IRB-applicable segment may
   carry a ZERO SA fallback (equivalently: sovereign AAA–AA– is never IRB-applicable). A
   zero fallback makes an uncovered worker operational-but-WORTHLESS — the deficiency
   shape (the DS tool-removal profile), violating difference-not-deficiency — and it puts
   the segment at score_report's clip, where the execution term cannot penalise
   fabrication (§4.1 clipping paragraph). **Includes the GENERATOR-side constraint** (RE
   flag: the S3 generator can currently produce such instances — the sampling must
   exclude them so they are not generated, not merely rejected; the assertion then guards
   the constraint).

**Acceptance (mechanical):** a test that constructs a deliberately nested lattice, a
capacity-bound sizing, a zero-k instance, AND a semantic-id roster (a worker id carrying a
token from the instance's own lattice or method names), and asserts the generator
**rejects all four** with distinct error messages. Per the §A test-shape rule and the S2
carry-forward: the id list must be built by the PRODUCTION path that builds ids — a test
that hands the assertion a hand-written id list verifies its fixture.

---

### S6 — Sensitivity gate, sweep, and knob disclosures `[x]` (reviews in records/S6/ incl. two RR rounds; effect-size floor + aggregate anchor + tiered divergence selection; five S6-round-2 items land as S7 pre-work)
**Cost:** 0.5d · **Depends:** S4, S5

`spread(I) = oracle − worst`, zero model calls. Floor and **triviality ceiling** (spread at or
near maximum → detection toy → regenerate; the spread must be interior). **Ceiling tightened
(S4 review, RR F2): an instance whose ORACLE attains a perfect score is rejected regardless
of worst** — the S4 committed instance sat at oracle 8/8, the unhealthy half §4.3 names ("a
design where the oracle cannot reach a perfect score is healthier than one where it can").
Knob disclosures per
§4.3: **K1** ships the spread-vs-covered-fraction CURVE (not the operating point), **K2** ships
k and the successor-only fraction, **K3** ships the per-unit divergence distribution anchored
on the Basel output floor (IRB RWA ≥ 72.5% of SA), **K4** ships the coverage lattice —
**including in the SWEEP report** (S3 review, RR: the generator seeds WHICH 4 of the 6
possible coverage pairs exist, so spread varies by seed through the realised lattice — a
second channel beyond the fraction; unreported, the K1 curve carries scatter that looks
like noise and is structure).

**Acceptance (mechanical):** running the gate on a committed instance emits a report
containing all four disclosures, and the K1 curve has ≥5 points. An instance outside the
declared floor/ceiling is rejected by the same script. **Plus (S5 review, RR F-A/F-B):**
the sweep reports regret headroom as a function of k (the K2 curve), and reports the
swapped pair's shared class across the suite with a uniformity check — if every instance
swaps on the same class, that is printed as a named scope limit, not left implicit.

---

### S7 — Admission pipeline `[x]` (reviews in records/S7/ incl. three RR rounds; v3 channel_effect_ceiling at 10k draws with per-row SE both units; 40/40 flagged vs provisional MDE — pilot's σ decides; K5 humped near-peak, no knob rescues, no fourth-knob search)
**Cost:** 0.5d (+0.25d pre-work) · **Depends:** S6

**PRE-WORK (S6 round-2 RR findings — both admission-changing, so they land here BEFORE a
suite is admitted):** (i) PD input-floor generation assertion (pd ≥ 0.05% for
corporate/retail, class-specific floors where they differ — Basel per-exposure input
floors; upgrades K3 to the three-part anchoring statement, spec §4.3); (ii) declared MDE
set to 0.20 PROVISIONAL (spec §5 — re-derivation sequence stated), gate re-run at 0.20:
expected ~28/40 admitted; (iii) aggregate floor labelled published-and-non-binding in the
gate report; (iv) shared_class_segments promoted to disclosed knob K5 with its own short
curve; (v) rejected rows name their rejection cause.

Three admission conditions per §7, all three required:
1. **Bit-identical regeneration, agent-free** — `generate(seed) → score(fixed_outputs)`
   byte-identical across ≥2 `PYTHONHASHSEED` values. **Agent-inclusive re-runs are explicitly
   NOT the test** — CHECK-2's within-seed nondeterminism dominates 10 of 12 DVs
   (`check_variance.txt`, incl. the allocation family) and would reject every instance.
2. **Interior spread** with knob disclosures attached.
3. **Scripted-baseline triviality gate** — a deterministic label-matching baseline, routing
   each unit by matching surface labels to worker coverage labels under the FULL-channel
   observation, **must not attain the oracle score**.

**Acceptance (mechanical):** the pipeline run on a candidate suite emits, per instance,
PASS/FAIL on each of the three with the scripted baseline's score printed beside the oracle's.
A suite containing one deliberately label-trivial instance must reject exactly that one.

---

### S8 — Environment assembly `[x]` (reviews in records/S8/; acceptance amended — completion is a study outcome; six-launch ledger; four in-flight rulings; core diffs clean; RR F1 → realised-authoritative scoring, S9)
**Cost:** 2.0d · **Depends:** S3, S4

The DAG (~16 tasks: scope & approval inventory, data prep, 8–10 per-segment computations,
aggregation, report, 2 upstream fixed); workers with private-parameter provisioning; cards
reflecting approval scope; the `method:` declaration convention; timeline wiring for
remove+add at `t_swap` via `schedule_agent_remove`/`schedule_agent_add`.

**Acceptance (mechanical, AMENDED by LS ruling at S8 close — the original "runs
end-to-end to completion" made harness acceptance hostage to manager competence, the
measured variable):** (i) machinery assertions green on a LIVE flash episode (provenance,
strong-form arrival, worker_run_completed for predecessor pre-swap and successor
post-swap, capacity ≤ C, task count 15–20, parser seam complete); (ii) full-DAG traversal
including the downstream chain proven in the ZERO-API dry run; (iii) workflow completion
is a STUDY OUTCOME reported per bundle, never a harness criterion.

---

### S9 — Logging records, comparability assertions, fabrication detectors `[x]` (reviews in records/S9/; precision measured-bounded-published; round-PD exposure named; records 3/4 synthetic-only until the ask cell's first run; §A gains the hardcoded-enumeration rule + the n=4 unifying entry)

AUTHORIZED-BY-LEAD: S10 — fabrication probe, deepseek-v4-flash only, ≥20 out-of-coverage
trials (model calls, not episodes), plus the three small S9-review addenda (round-PD
per-instance report; closing-condition + scope notes recorded in the gate report). No
threshold set in the probe; the rate goes to the team per the step text.
_S9 now also carries (accumulated): the unstaffed-segment count as a first-class run
field (S6/S7 reviews); REALISED-AUTHORITATIVE scoring + deferred-assignment logging (S8
review F1 + spec §4.1 — the set-level best-feasible pre-ruling is retired); the parser's
single-episode evidence scope note (re-check at the first NO_METHOD run); and the
infeasible-assignment rule stands on its own, never motivated by the seg_01 observation._
**Cost:** 0.5d · **Depends:** S8

Four logging records (target channel pulls; refine events with before/after description text;
message→manager visibility including whether it entered the rendered window; ask-reply
addressing). Comparability assertions on **rendered text and effective values**, never on
generating parameters. **Denominator computed from the observed post-swap task set**, with
every retry/create logged by pre/post-swap origin. Fabrication detectors, all three:
value-based (primary), trace-based (secondary), absence-based (method-declared output with no
corresponding tool call in `worker_run_completed.payload.history`).

**Acceptance (mechanical):** on a synthetic run bundle containing one planted instance of each
fabrication variant (tool-calling and in-head), the detector reports exactly two hits and
classifies each correctly. Comparability assertions pass on an unperturbed run.

---

### R2 — Study cells + instance selection `[ ]` (blocks the scope run)
**Cost:** ~0.5d zero-API · **Depends:** R1

S8 built the ACCURATE-CARD DEFAULT ONLY. The six cell configurations do not exist, so the
scope run cannot start. Build them as configuration over the existing environment, not as
new environments:
- **U** unswapped control (no roster event; scores against the pre-swap roster's own oracle)
- **0** swapped, information-absent: predecessor's card still on file, no declaration, ask disabled
- **1** card updated at t_swap · **2** declaration present · **3** ask enabled
- **4** all three channels
Everything else IDENTICAL across cells by construction — same instances, same action space,
same capacity, same horizon, same model — and asserted so by `finance_comparability`
(absent-is-not-same semantics already implemented).

**INSTANCE SELECTION RULE, RECORDED BEFORE ANY RUN (C2 obligation, LS, 2026-08-09).**
Three instances, used across ALL six cells so contrasts are paired on (instance, segment).
Drawn from the 34 admitted by **STRATIFIED SAMPLING ACROSS THE CEILING BAND** — the
admitted set is split into terciles by `channel_effect_ceiling`, one instance drawn at
random within each tercile using a recorded seed. Rationale, and the distinction that
makes this compliant rather than a violation of C2: selection is **BALANCED across the
band, never conditioned toward the favourable end** — a plain random draw of three risks
landing on three similar instances and losing the between-instance heterogeneity that is
one of the four quantities the run exists to measure. RR permitted "randomly OR stratified
across the band"; this is the second, and the tercile boundaries plus the draw seed are
committed BEFORE the run so the selection cannot be revisited after seeing outcomes.

**Acceptance:** six cell configs instantiate; comparability assertions pass across all six
on rendered text and effective values; the three selected instance ids + tercile bounds +
draw seed committed under `records/R2/` before any episode; a zero-API dry run shows each
cell's channel state differing ONLY in the intended field.

### R1 — Coverage repair (B′) + bundled removals + unscripted workers `[~] (RE implementing)`
**Cost:** ~0.5d zero-API + 1 machinery episode · **Depends:** S9 [x] · **Authorised by the
researcher 2026-08-09** ("start the repair"). ONE regeneration carries all of it.

1. **Calibration is a property of the ASSET CLASS**, not the worker — one validated table
   per class (rating → PD), held by every worker approved for that class. Assert: all
   covered holders of a class hold the IDENTICAL table.
2. **Truth = ASRF(class_calibration[rating], lgd, maturity).** The scorer no longer reads
   `segment["pd"]`; **DELETE the field from the schema** so nothing can silently read it
   (assertion in the producer, not the product).
3. **Drop the public default-rate line** from the task text. Public stays: class, rating,
   EAD, LGD, maturity, approval flag. Assert by string check on the rendered description.
4. **Unscript the worker (E3a).** Prompt states SITUATION only — what you are approved
   for, what you hold, what the task is. No method instruction, no "always produce a
   number", no clause forbidding refusal. Assert absence of both by string check; commit
   the prompt diff. **String assertions are NECESSARY, NOT SUFFICIENT (RR):** a reworded
   procedural instruction passes every string check, so READS establish the initial state
   and ASSERTIONS guard it against drift — LS and RR each read the committed diff
   SEPARATELY and record in their own review file that they read it and what they looked
   for (any surviving procedure about what to do when an input is missing, however
   phrased). Otherwise "string-asserted absent" becomes "verified unscripted" in one
   summarisation step, on the very clause that made the 0% decline a tautology.
5. **Bundled removals:** rating PENALTY maximisation out (clip-avoidance KEPT, separate
   mechanism); **K2** out as an effect knob.
5a. **NO FLOOR-PINNED OR ROUND CALIBRATIONS (RR's S9 F1 fix — R1 IS the regeneration it
   was deferred to, so it lands here or needs its own cascade later).** No class
   calibration at exactly a Basel input floor (0.0005 corporate/retail, 0.001 QRRE) nor
   at ≤2 significant digits; asserted at generation. Two independent reasons: under R1
   calibrations are SCORE-BEARING, so an exact coincidence becomes an exact EXONERATION —
   the most guessable number in the domain would land on truth and clear the detector;
   and a calibration sitting on a published floor is what a bank reports when it has NO
   model, the opposite of holding an approved one, so exclusion improves realism too.
   Floor-pinned enumeration stays as disclosure (item 7).
6. **Regenerate everything from HEAD in ONE pass** — S3/S5/S6/S7/S9 records; freshness
   assertion must pass; suite parity.
7. **Re-report:** new ceiling band (chosen AND neutral mix), aggregate floor, admitted
   count; **UN-SUSPEND the round-PD finding** — calibrations are now score-bearing, so a
   fabricator guessing the floor value hits truth exactly; rename the detector's
   `irb_matching_with_provisioned_parameters` label to match what it now computes.

**Acceptance:** every assertion above green; one machinery episode on the pinned build
(bundle assertions pass, roster event strong-form, capacity respected, parser seam clean);
records regenerated and fresh. Governing spec: §2 banner, E3a, §4.1, §4.3.

### S10 — Fabrication linchpin probe `[!] BLOCKED on R1 — spec/implementation conflict awaiting researcher ruling: the coverage gap is PERMISSION-not-INFORMATION as built (scorer computes IRB truth from the PUBLIC pd printed in every task; private calibrations touch no scored quantity; calibrations also drawn per-worker, so co-covering workers differ). See HARNESS_SPEC_v2 §2 blocking banner. Out-of-coverage arm allowed to finish (unaffected either way); in-coverage arm, tolerance band and the round-PD finding all held. Options (A) scorer-authoritative / (B′ = LS recommendation) class-level calibration + drop public pd line. Nothing further runs until the ruling.`
**Cost:** 0.5–1d · **Depends:** S8, S9 · **Model calls, not full episodes**

Hand a worker an out-of-coverage segment and classify the outcome into **four** buckets:
falls back to SA / refuses / fabricates-with-tool-call / fabricates-in-head. A two-outcome
check would report a pass while the in-head route runs. Also assert the generator's precision
requirement: private parameters carry enough precision that a guess cannot coincide with truth.

**S3 validity dependency (S3 review, RR — this step can RETIRE S3's mechanism, not just
consume it):** the private PD calibration is not inaccessible information — a model can
produce a plausible PD fluently from published default studies; the gap holds for SCORING
(fabricated PD ≠ generated calibration) but not behaviourally. **Coverage-as-gap is valid
iff this probe finds fallback (or refusal) dominant. A high fabrication rate makes
out-of-coverage workers a noise source on the primary DV (execution loss swamps allocation
loss) and forces a coverage-mechanism redesign.**

**Acceptance (mechanical):** ≥20 out-of-coverage trials, outcome counts committed under
`records/`, with the fabrication rate (both variants summed) reported as a single number.
**No threshold is set here** — the number goes to the team, because what rate is tolerable is
a design decision, not mine.

---

### S11 — Gate pair `[ ]`
**Cost:** 2 SSRs · **Depends:** S1–S10 all `[x]` · **Needs run authorisation**

2 SSRs, flash, clean pair, no instruments, successor-arm descriptions method-consistent.
PASS = (i) ≥1 correct post-swap output demonstrably via the successor's method by
**truth-match, not declaration** (the 0/221 declaration-accuracy figure is tool-swap-regime
evidence and does not transfer), and (ii) ≥1 post-swap task assigned to AND executed by the
successor id.

**Acceptance (mechanical):** both conditions evaluated by script against the run bundles, with
the verdict and the supporting task ids committed. A 3/3 result is recorded as **"capability
established, outcome-channel signal absent"** and never as non-degeneracy of the DV.

**Reading limit:** "the gate passed" licenses **capability only** — never "the perturbation is
validated". Allocation-visibility is gated separately by study cell 1.

---

## Not in this backlog, deliberately

- **The study cells themselves** (5 cells × 9 seeds = 45 episodes). They follow the gate and
  need their own authorisation; putting them here would invite the cron to run 45 episodes
  off a checklist.
- **Env-2 (record linkage).** Separate backlog when env-1 lands. Its first check is
  Fellegi–Sunter execution fidelity, not the generator.
- **Provider pinning, trace substrate, NO_METHOD extractors.** Deferred; none blocks the gate.
