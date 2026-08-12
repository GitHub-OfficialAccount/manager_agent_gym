# eDiscovery environment — concrete task-and-truth sketch

**Status:** specification and estimation only. No code, no runs. Research-engineer draft
for the reviewer's pass, then the researcher presentation. Implements HARNESS_SPEC v1
(E1–E5, the fixed replacement event, channels C1–C4, per-env gate) in the
`legal_litigation_ediscovery` scene.

**Skeleton reused:** `examples/end_to_end_examples/legal_litigation_ediscovery/`
(`workflow.py` 214 lines, `team.py` 164, `preferences.py` 663). We keep its scene, DAG
shape and role names; we replace its scoring with computable truth and add the toolset it
does not have (no stock scenario contains a `function_tool` — that gap is the build).

---

## 1. The measured spine, and the explicit cut list

The stock workflow is four phases with subtasks. Most of it is defensibility
documentation, which is real eDiscovery work and carries none of our measurement. Trimmed
toward the spine per O3.

**KEPT (the spine):**

| task | role in the study |
|---|---|
| `Search Strategy` (from Legal Hold & Scoping) | produces the agreed term list. **This is the artifact whose description goes stale** — it is written for the keyword method |
| `Forensic Collection` (per custodian, collapsed to one task) | produces the per-custodian document sets. One task, not per-custodian, to keep the pre-swap window short |
| `Responsiveness Review — <custodian>` × N | **the perturbation family.** One task per custodian; this is where the method substitution lives and where allocation is measured |
| `QC Sampling & Second-Level Review` | the **join**: consumes first-pass codings; produces overturn findings. Mechanism evidence comes from the gate pair / fixed-assignment condition; descriptive-only in study cells (§4) |
| `Production Set Assembly` | terminal consumer; makes the review consequential |

**CUT, and why** (stated so nobody reads the trimmed scene as the eDiscovery workflow):

| cut | reason |
|---|---|
| `Custodian Interviews`, `Hold Notices` | pre-collection administrivia; no artifact the measured chain consumes |
| `Processing` (deNIST/dedupe) | culling mechanics; would need its own truth model and feeds nothing we measure |
| `ECA` | sizing estimate; its output is advisory, consumed by no downstream task here |
| `TAR Setup & Training` | **deliberate**: keeping it would make TAR availability a task the manager schedules, turning the method into an allocation *choice* rather than a property of the worker. That fuses IV and DV |
| `Redactions & QC`, `Load Files & Metadata` | production mechanics downstream of the join; the join is where method mismatch bites |
| the 663-line preference rubric set | replaced by computable truth for the gate and the perturbation family (HARNESS_SPEC v1 (b)); rubrics may return later as secondary outcomes |

Spine size: 3 fixed tasks + N custodian reviews + 2 downstream ≈ **16–20 tasks** at N=8–10,
against DS's 16.

## 2. The corpus and its ground truth

**Unit:** a synthetic document set, partitioned by custodian. Each document carries a
hidden label `responsive ∈ {true, false}` fixed at construction.

**Naming, fixed before it spreads.** The successor's method is called
**classifier-based / concept review** throughout, never "TAR". TAR is a term of art for
supervised machine learning with a human in the loop; our successor uses a deterministic
rule fixed at construction. Reusing the field's word for a different object is a
same-name-different-meaning collision against the field's own vocabulary — the class that
has already cost this project `v2.6`, `full`, `belief_model`, and "silent". It stands in
for TAR's *role* in the scene (the non-term-based review method), and the paper says that
once and explicitly. The rename also dissolves the pre-training fiction: a deterministic
rule needs no training phase, which is consistent with cutting `TAR Setup & Training`.

**Two closed-form truths per custodian**, the direct analogue of
`_audit_total(..., "percentile")` / `_audit_total(..., "zscore")` (scenario.py:308-309):

```
truth_keyword(c)  = |{d in custodian c : term_list matches d}|
truth_concept(c)      = |{d in custodian c : classifier(d) = responsive}|
truth_actual(c)   = |{d in custodian c : label(d) = responsive}|     # the real answer
```

`term_list` is fixed by the `Search Strategy` artifact. `classifier` is a **deterministic
function defined at construction**, not a trained model — an LLM-free rule over document
features, so the truth is closed-form and reproducible. Both methods are scoreable
against `truth_actual`, and against each other.

**Divergence is built, not hoped for.** The corpus contains three document classes:

| class | keyword finds it | concept review finds it | purpose |
|---|---|---|---|
| **plain responsive** — uses the agreed terms | yes | yes | shared baseline; nobody is switched off (core-tool rule) |
| **coded responsive** — responsive, phrased around the terms (synonyms, euphemism, internal shorthand) | **no** | yes | concept review's advantage |
| **term-bearing non-responsive** — contains the terms in an innocuous context | **yes (false positive)** | no | keyword's failure mode |

**Custodian-dependent mix is the allocation lever.** The proportions of the three classes
vary by custodian. Some custodians are keyword-friendly (mostly plain), others are
coded-heavy. That makes method suitability *a property of the custodian*, so the manager
has a reason to route particular custodians to particular reviewers — which is exactly
what "allocation-visible" requires. This mirrors the DS env's column-dependent gap
(junior ~0.9 on income, ~0.14 on dti) that made the linchpin work.

**Qualifier, carried with the same discipline as §3's:** per-custodian method-suitability
variation is **our construction** — a plausible design choice, NOT a sourced property of
eDiscovery practice. What is sourced-safe is that review is *organised* by custodian.
That custodians differ systematically in how well term-based search serves them is
something we build because the study needs an allocation lever, and it must be presented
that way. (§119's lesson, applied before someone asks: assert only what is sourced, and
label the rest as design.)

**Two corpus controls, both LOGGED ASSERTIONS, not conventions.** The allocation lever is
the load-bearing element of the design, so its uncontrolled alternatives are checked
mechanically:

1. **Equal custodian size.** Document count is held CONSTANT across custodians; only class
   *proportions* vary. Without this, volume masquerades as method-fit — a manager rerouting
   a custodian because it is large would be indistinguishable from one rerouting it because
   term search suits it badly, and the DV cannot tell them apart. Asserted per episode:
   all custodians have identical document counts.
2. **Randomised mix-profile-to-position within seed.** Which custodian carries which class
   mix is randomised per seed, and logged. Otherwise mix is confounded with DAG position
   and with pre/post-swap membership — the coded-heavy custodian would always be the third
   one reviewed, and "method fit" would be indistinguishable from "reviewed later".

**Trace-distinguishable on all three legs:** distinct tool (`search_by_terms` vs
`classify_by_concept`), distinct truth value (the counts differ by construction), and
`actor_id` free.

### 2b. The planting-artefact pre-check — run before any episode

My named riskiest item, sharpened by the withdrawal of the seed-set claim (§119: seeding
is an **instrument**, never scene practice — TAR *training* seed sets are not planted
scoring documents, and the paper must not say they are).

**The risk, in P3 form:** if planted documents are recognisable as planted, the reviewer
responds to the planting artefact rather than to the review task. A suspiciously clean
positive is easy to find *by any method*, which compresses the keyword-vs-concept divergence
the design depends on — biasing toward agreement between methods, i.e. toward a null on
trace-distinguishability. The failure manufactures the wrong answer, quietly.

**The check (reviewer calls, no episodes):** run the reviewer prompt over the corpus twice
— once with seeded items present, once with them removed — and compare **detection rates
on the unseeded documents**. If seeded items behave as ordinary documents, the unseeded
rate should not move. A material move means the seeded items are altering how the
reviewer treats everything else, and the corpus needs rebuilding before any episode runs.

Cost: k × n reviewer calls, ~1 hour to write. This is the eDiscovery analogue of the
synthetic-format ablation specced for S6, and it is a **gate on the corpus**, not a
finding.

## 3. Custodian pairing structure, with the arithmetic

**Pairing unit (O1): the custodian.** Repeated, interchangeable-but-distinct, and native —
eDiscovery batches by custodian as a matter of practice (this claim *is* sourced-safe;
it is about workflow organisation, not about planted documents).

**How many, and why — two separate quantities that get conflated:**

**(a) Seeds set whether significance is reachable at all — and this is a FORK for the
researcher, not a recommendation I should make silently.**

The estimator is arm-paired on (seed, custodian) with a sign test, because n is
single-digit and no distributional assumption is defensible. Two-sided p for S paired
seeds, computed not assumed:

| paired seeds | unanimous (S/0) | one dissenter (S−1/1) |
|---|---|---|
| 5 | 0.0625 — cannot reach 0.05 even if perfect | 0.375 |
| **6** | **0.031** | 0.219 |
| 7 | 0.016 | **0.125** |
| 8 | 0.008 | 0.070 |
| **9** | 0.004 | **0.039** |

**The fork:**
- **S = 6** — unanimity-or-nothing. Cheapest design that can reach 0.05 at all, but it has
  **zero margin**: one seed going the other way puts the result at p=0.219 and there is no
  recovery short of running more.
- **S = 9** — the first design that survives a single dissenting seed (8/1 → p=0.039). Costs
  50% more episodes than 6 and buys the only robustness available.

**Correcting my own earlier recommendation: I proposed 7 for "headroom" and that was
arithmetically wrong.** At S=7 a 6/1 split gives p=0.125 — 7 seeds is 17% more runs than 6
for *zero* additional robustness. There is no intermediate: the next design that tolerates
a dissenter is 9. I asserted headroom instead of computing it, which is the same failure
mode as the seed-set claim, one week apart.

**Recorded explicitly, because it changes how CHECK-1 should be read:** CHECK-1's
announcement result was 6/6 at p=0.031 — that sat exactly **on the floor with zero margin**.
It was not a comfortable result that happened to use 6 seeds; 6 was the minimum that could
have produced any significant result, and a single non-conforming seed would have taken it
to p=0.219. The finding stands as reported; its fragility should be stated whenever it is
quoted.

**(b) Custodians set the DV's resolution.** `rerouted_share` is a fraction over post-swap
tasks in the perturbation family. DS had 3 post-swap robust audits, so the DV took values
in {0, ⅓, ⅔, 1} — four levels, and that coarseness is visible in CHECK-1's per-seed table
(values are almost all 0.333 / 0.667 / 1.000). **With 6+ post-swap custodian reviews the
DV has ≥7 levels**, which reduces lumpiness without adding a single episode.

**Recommendation: N = 8–10 custodians, ~2–3 pre-swap and 6–7 post-swap. Seed count is
the researcher's fork above (6 or 9), not mine to pick.**

### 3c. The denominator is COMPUTED, never assumed

The pairing structure above assumes the post-swap task set is the custodian reviews that
started after `t_swap`. **That assumption is not enforced by the engine**, and two ordinary
manager actions break it: `retry_task` can re-run a pre-swap custodian after the swap, and
`create_task` can add one. Either moves a pre-swap custodian into the post-swap window, and
the DV's denominator silently changes composition — the two-layout denominator failure
arriving through the manager's own action space rather than through a glob.

Enforcement, all mechanical:

- **Compute the DV denominator from the ACTUAL post-swap task set** observed in the run,
  never from the intended custodian list.
- **Log every `retry_task` and `create_task`** in the perturbation family with its
  **pre/post-swap origin** — was the underlying custodian first reviewed before or after
  `t_swap`.
- **Assert denominator composition** per episode: the post-swap set contains exactly the
  intended post-swap custodians, or the deviation is recorded.
- **Report exclusions explicitly.** If a run's denominator deviates, it is reported with
  the reason, not silently dropped and not silently kept.

## 4. Overturn as mechanism check — and it moves out of the study cells

QC second-level review overturns first-pass coding; overturn rate is the natural
"the method difference mattered" signal. **It cannot carry the DV**, and the reviewer's
R7 flag is right: overturn is a **join property** (§77e), determined by both the coder and
the QC reviewer, exactly as CHECK-3's downstream error turned out to be a tool property.

**It is also collider-exposed**, which is the sharper problem and is the CHECK-1 trap
transplanted: a manager that reroutes away from the successor early prevents the successor
from producing codings that could be overturned. Overturn rate is therefore *downstream of
the allocation DV*, and conditioning on it — or stratifying by it — reproduces the
manifested-collider error at full strength.

**Therefore the mechanism evidence moves OUT of the study cells.** In a study cell the set
of codings available to overturn is *manager-selected* — it is the allocation DV's output —
so overturn there is confounded by the very thing the study measures, and no stratification
fixes it (stratifying on it is the collider; conditioning on it is worse).

**Design, after relocation:**
- **Mechanism evidence comes from the GATE PAIR or a fixed-assignment condition**, where
  the coding set is determined by the design rather than by the manager. `fixed_gate.py`
  already provides exactly this: `FixedNoOpManager` / `FixedRetryManager` with fixed
  assignments, so the successor's codings exist regardless of what a manager would have
  done. That is where "the method difference propagated into consequential joint work" can
  actually be established.
- **In study cells overturn is DESCRIPTIVE ONLY**, reported per cell with the caveat that
  its denominator is manager-selected. It is never a stratifier, never conditioned on
  within-run, and never quoted as evidence the mechanism operated.
- If overturn turns out to be driven by the coding tool rather than the reviewer, that is a
  finding about the instrument and is reported as one.

## 5. The replacement event, in the scene

| element | concrete form |
|---|---|
| **who** | the first-pass responsiveness reviewer. Predecessor `review_analyst_kw` (keyword/Boolean specialist); successor **new `agent_id`** `review_analyst_concept` |
| **story** | the contract review vendor rotates staff mid-matter — the manager did not choose it and did not schedule it. Exogenous, announced-as-fact, uncharacterised in content |
| **when** | `t_swap` after 2–3 custodians are reviewed, so a pre-swap baseline exists and 6–7 custodians remain |
| **mechanism** | `schedule_agent_remove(t_swap, "review_analyst_kw")` + `schedule_agent_add(t_swap, tar_config)` — already wired via `run_examples.py:117-128`; the only new build is rendering the arrival (§116, ~0.5d core) |
| **stale card (C1)** | the predecessor's capability list stays on file: *"applies agreed search-term lists; Boolean and proximity search; term-hit reporting."* True when written, never revised. No fabrication |
| **stale descriptions** | the per-custodian review task descriptions say *"Apply the agreed search-term list to this custodian's collection…"* — written for keyword, byte-identical after the swap, now wrong for a concept reviewer. This is the §87 instrument arising **by succession**, in-scene |

## 6. Channels C1–C3, in-scene referents

- **C1 card** — the reviewer's capability entry in the roster. In-scene: a vendor staffing
  record. Manipulation: predecessor's-still-on-file vs updated.
- **C2 declaration** — the by-product `method:` line in the coding artifact ("coded via
  term-list hits" / "coded via classifier score ≥ τ"). In-scene: the coding rationale a
  reviewer records for defensibility. Manipulation: present / absent.
- **C3 ask** — the manager messages the reviewer about its method; ride-along, reply
  manager-addressed by prompt instruction (that instruction is part of the manipulation —
  workers name the manager's id in 2 of 56 corpus sends, so it cannot be assumed).
  In-scene: supervising attorney querying a reviewer's protocol.
- **C4 trace** — deferred at selection per HARNESS_SPEC v1 (c); the substrate is unbuilt.

## 7. Comparability assertions — rendered text and effective values only

Per §120-addendum (6), every assertion is on what was **rendered**, never on the parameter
that generated it. This is the same distinction that made `belief_model` a hazard
(parameter vs effective value) and that the observation-vs-shown conflation cost twice.

| assertion | asserted on |
|---|---|
| stale descriptions unchanged | the description string **as formatted into the worker prompt** (`ai_agent.py:413-424`), byte-identical pre/post swap |
| stale card unchanged | the card **as rendered into `available_agent_metadata`** after redaction, not the config object |
| roster arrival held constant across cells | the rendered roster-change block, byte-identical across cells |
| model constant | the **effective** model recovered from `structured_llm_response` events, not the requested route |
| term list constant | the `Search Strategy` artifact's rendered content |
| equal custodian size | the document count actually delivered per custodian in the episode |
| mix-profile randomisation | the realised profile→custodian assignment for that seed |
| DV denominator composition | the observed post-swap task set, with every retry/create tagged pre/post-swap origin |

## 8. Build cost and episode length

| item | estimate |
|---|---|
| corpus construction + three document classes + labels | 1.5–2d |
| truth functions (`truth_keyword`, `truth_concept`, `truth_actual`) | 0.5d |
| tool pair + shared core tools + worker toolsets | 1d |
| DAG adaptation from the stock skeleton, spine + cut list | 0.5–1d |
| worker cards, prompts, declaration convention | 0.5d |
| DV scorer/extractor, four logging records, assertions | 0.5d |
| **planting-artefact pre-check** | 0.25d |
| corpus controls + denominator assertions + exclusion reporting | 0.25d |
| **linchpin validation** — does keyword-vs-concept actually diverge under flash | 0.5–1d |
| **total** | **5.5–7.0d** |

The linchpin line is the one that historically slips: it is where the calculator no-go and
the strict-superset no-go were found, and each invalidated a finished build.

**Episode length (O3).** My untrimmed estimate for Tier-1 candidates was 30–45 min/SSR
against DS's 18. The spine trim removes 7 stock tasks and the rubric evaluation, and adds
N custodian reviews. Net at N=8–10: **~16–20 tasks, estimated 25–35 min/SSR.** The trim
buys back roughly the top third of the range. Still above the 20-minute self-serve line,
so the per-env gate (2 SSRs) needs authorisation as a unit.

## 9. What this sketch does not establish

- **No linchpin evidence.** Nothing here shows that keyword and concept review actually diverge *for
  an LLM reviewer under flash*. The corpus makes the truths diverge by construction; whether
  the agent's behaviour follows is the linchpin check, and it is the item most likely to
  fail. Treat every downstream number as conditional on it.
- **The planting-artefact check is a gate, not a result.** Passing it means the corpus is
  usable, not that the study works.
- Build days are single-point judgement, no spread.
- Episode length is extrapolated from task counts; no stock scenario has been run under
  our harness.
- Custodian counts assume post-swap tasks are the perturbation family only. If the manager
  can reassign pre-swap custodians too, the denominator changes and §3's arithmetic needs
  re-deriving.
