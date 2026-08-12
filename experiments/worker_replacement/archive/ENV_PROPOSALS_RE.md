# Purpose-built environment proposals — research-engineer, phase 1 (divergence)

**Status:** divergence contribution. No ranking, including of my own. Spec only, no code,
no runs. Answers §126: finance reframed as purpose-built and script-generated, plus two
designs of my own.

---

## 0. A design principle I want on the table, because it changes how any of these are built

**Prefer COMPLEMENTARY BLIND SPOTS over GRADED COMPETENCE.**

Every environment we have built or sketched so far uses graded competence: method B is
better than method A on some units and the gap varies (DS's column-dependent tool gap,
eDiscovery's custodian-dependent F1). That works, but it has two costs we have paid
repeatedly:

- **The spread must be tuned into existence.** If the grading is too gentle, oracle and
  worst allocations score nearly the same and the sensitivity gate fails — the researcher's
  "I foresee the scores won't differ" is exactly this worry.
- **Difference-not-deficiency holds only by careful parameter choice.** Push the grading
  and method B starts dominating everywhere, which is deficiency again.

**Complementary blind spots** means each method is *strictly better on one class of item
and strictly worse on another*, by construction:

```
class X:  method A finds it,        method B misses it
class Y:  method A misses it,       method B finds it
class Z:  both find it              (shared baseline — nobody is switched off)
```

Then: no allocation dominates for any instance with both classes present; the spread is
non-zero **by construction** rather than by tuning; difference-not-deficiency is structural
rather than a tuning result; and the unit-level allocation lever is just the X:Y ratio per
unit, which is a generator parameter. The sensitivity gate becomes a knob we set rather
than a number we hope for.

eDiscovery already half-has this (coded-responsive vs term-bearing-non-responsive are
complementary), which is a point in its favour that the sketch did not name. Both proposals
below are built on it deliberately. **Finance does not have it** — SA/IRB is
applicability-based, not blind-spot-based — which is a real structural difference between
the incumbent and these, and worth the reviewer's attention rather than my adjudication.

---

## 1. FINANCE, reframed as purpose-built and script-generated (the incumbent)

Not the `icap` scenario extended. A generator script that emits a complete instance.

**Domain and work units.** A bank's annual capital calculation. Units = **portfolio
segments** (8–10 per instance), each a set of exposures with `EAD, PD, LGD, M, rating,
asset_class`, plus an `irb_approved` flag.

**The two methods, with their truth functions** (verified stdlib-computable — §5d9cf75):
- **SA**: `RWA = Σ EAD_i × RW(rating_i, asset_class_i)` — supervisory lookup table.
- **IRB**: `RWA = 12.5 × Σ EAD_i × K_i`, with `K` from the ASRF formula (correlation
  `R(PD)`, maturity adjustment `b(PD)`, `Φ`/`Φ⁻¹` from `statistics.NormalDist`).
- `applicable(seg) = IRB if irb_approved else SA`; `correct(seg)` = the applicable formula
  applied correctly; `s(seg, m) = 1 − min(1, |reported − correct| / correct)`.

**Replacement story.** The quant vendor migrates its capital engine; the successor computes
under the other approach. Model-change governance makes this a documented industry event.

**Channel referents.** C1 card = the quant's model-approval scope on file. C2 declaration =
the `method:` line in the capital memo ("computed under the standardised approach"). C3 ask
= the capital planner querying which approach the quant applied — a real review question.

**Pairing unit.** The portfolio segment.

**Expected spread shape.** Large and asymmetric: applying the wrong approach misstates
capital by **−70% to +122%** depending on segment PD, crossing near PD ≈ 1.2%. Instance
generation controls the spread directly by choosing the PD distribution across segments.

**Tasks (~16).** Scope & approval inventory (1), data preparation (1), per-segment capital
computation (8–10), aggregation (1), capital adequacy report (1), plus 2 fixed upstream.

**Build:** 4.75–6.25d, of which 0.5–1d is validating the Basel implementation against
published worked examples — still a precondition, still not done.

**Its distinctive strength:** the method-fit variation is a documented property of the
framework, not our construction. **Its distinctive weakness:** no complementary blind
spots, so the spread comes from applicability rather than from structure, and
`applicable(seg)` is assigned by us.

### 1a. The §129 demotion, absorbed — stated plainly, no redesign

The stress-test demoted finance one leg on the three-tier test, and the demotion is
correct. Recording it here so the spec carries it rather than the reader having to
reconcile two documents:

- **Tier (a) — complementary difference: finance does NOT have it.** Its two methods are
  separated by **permissioning, not capability**. A quant applying SA to an IRB-approved
  segment is not worse at the work; it is applying the approach it is not permitted to
  apply there. That is a real and consequential difference, and it is not the
  complementary-blind-spots structure §0 argues for — it is closer to an eligibility rule
  than to a capability gap.
- **Tier (b) — who sets the class boundary: we do.** `applicable(seg)` is an
  **experimenter-set** boundary. Which segments carry IRB approval is assigned by the
  generator, exactly as eDiscovery's custodian suitability was (§121). The *divergence
  magnitude* between the approaches is framework behaviour; the *assignment* of which
  segment sits on which side is ours, and the two must not be quoted as though the first
  licences the second.
- **Tier (c) — external anchor: magnitude only.** The Basel output floor anchors how large
  a capital difference can legitimately be. It anchors **nothing about which segments
  differ, or by how much in our instances** — those are generator parameters. So the anchor
  supports "a difference of this size is materially real in the domain" and not "this
  distribution of differences is realistic".

**Net:** finance's realism claim survives at magnitude and structure, and does not extend to
the allocation boundary. Nothing in §1 changes; the claims made *about* §1 narrow.

---

## 2. RE-1 — LEDGER RECONCILIATION (exact vs tolerance matching)

**Domain and work units.** Month-end reconciliation between two ledgers (e.g. bank
statement vs internal sub-ledger). Units = **accounts** (8–10 per instance), each holding a
few hundred entry pairs.

**The two methods.**
- **Exact matching**: match on `(key, amount, date)` identity.
- **Tolerance matching**: match on amount within ±ε, date within a ±d window, and
  normalised counterparty string.

**Complementary blind spots, by construction:**

| entry class | exact | tolerance | why it exists |
|---|---|---|---|
| **clean pairs** | match | match | shared baseline (core-tool rule) |
| **drifted pairs** — true matches with a rounding difference, FX cent-drift, or 1-day settlement lag | **miss** | match | tolerance's advantage |
| **near-collisions** — genuinely DIFFERENT transactions that fall inside the tolerance window (same counterparty, same day, similar amount) | correctly unmatched | **false match** | exact's advantage |

**Truth functions.** The generator emits the true pairing as it builds the ledgers, so
`true_matches(u)` is known exactly. `matched(u, m)` is a deterministic set operation.
`s(u, m) = F1(matched(u, m), true_matches(u))`. Zero model calls; the sensitivity gate is
a set operation per account.

**Allocation lever.** The drifted:near-collision ratio varies by account — an FX-heavy
account is drift-rich (tolerance wins), a high-volume same-counterparty account is
collision-rich (exact wins). Both are realistic account characteristics.

**Replacement story.** The reconciliation platform is upgraded mid-close, or the outsourced
ops team rotates to a vendor whose engine uses tolerance matching. Both are ordinary and
exogenous; the close does not stop for it.

**Channel referents.** C1 card = the ops analyst's tooling profile on file. C2 declaration =
the `method:` line in the reconciliation memo ("matched on exact key" / "matched within
±0.01 and ±1 day"). C3 ask = the controller asking what matching basis was used — a
standard review question at close.

**Pairing unit.** The account.

**Expected spread shape.** Directly settable: spread per account ≈ the F1 difference driven
by the class mix, so the generator sets it. With a 60/20/20 clean/drift/collision mix the
two methods differ by roughly the minority-class share in F1 terms.

**Tasks (~16).** Close calendar & scope (1), ledger extraction (1), per-account
reconciliation (8–10), exception summary (1), close package (1), plus 2 fixed upstream.

**Build: ~4–5d.** Cheaper than eDiscovery for one specific reason worth stating: **the
corpus is records, not prose.** There is nothing for an agent to notice as synthetic, so the
**planting-artefact pre-check disappears entirely** — my named riskiest item on eDiscovery
does not exist here. Episode ~15–18 tasks, target ~20 min.

**Riskiest item.** Tolerance matching must be *specified* precisely enough to be
deterministic (matching order matters when several candidates fall inside the window). A
greedy left-to-right matcher and a global optimal matcher give different answers on the same
data, so the method definition must fix one and the truth must use the same rule.

---

## 3. RE-2 — DATA-FEED VALIDATION (schema rules vs statistical profiling)

**Domain and work units.** A data-quality gate on inbound feeds before a warehouse load.
Units = **feeds** (8–10 per instance), each a few hundred records.

**The two methods.**
- **Schema/rule validation**: declared types, required fields, enumerations, referential
  constraints.
- **Statistical profiling**: per-column distribution fitting on a clean reference window,
  flagging records outside learned bounds.

**Complementary blind spots, by construction:**

| bad-record class | schema rules | profiling | why it exists |
|---|---|---|---|
| **type/constraint violations** — wrong type, null in a required field, value outside an enum | **catch** | miss (it is in-distribution once cast) | schema's advantage |
| **semantic anomalies** — schema-valid but impossible: negative tenure, a rate of 3.4, a birth date in 2031 | miss (all types valid) | **catch** | profiling's advantage |
| **clean records** | pass | pass | shared baseline |
| *(the honest fourth)* **legitimately unusual records** — real outliers | pass | **false positive** | profiling's cost, so precision matters and F1 is the right score |

**Truth functions.** The generator labels every record as it emits it, so `bad(u)` is exact.
`flagged(u, m)` is a deterministic function of the record set and the method's fixed
parameters. `s(u, m) = F1(flagged(u, m), bad(u))`. Zero model calls.

**Allocation lever.** The type-violation:semantic-anomaly ratio varies by feed — a feed from
a legacy CSV exporter is type-violation-rich (schema wins), a feed from a well-typed API
with bad upstream business logic is semantic-anomaly-rich (profiling wins). Both are
recognisable to anyone who has run a data platform.

**Replacement story.** The data-quality vendor migrates from rule-based to
profiling/ML-based validation — one of the most common real platform migrations, and the
migration is announced-as-fact with uncharacterised behavioural content, which is exactly
our event's shape.

**Channel referents.** C1 card = the data engineer's tooling profile. C2 declaration = the
`method:` line in the validation report ("validated against declared schema" / "profiled
against the 30-day reference window"). C3 ask = the platform owner asking what the gate
actually checked before a load is approved.

**Pairing unit.** The feed.

**Expected spread shape.** Set by the class mix per feed, same as RE-1. The fourth class
(legitimately unusual records) gives profiling a real precision cost, so neither method
reaches F1 = 1 and the spread stays interior — which is healthier for a benchmark than a
design where the oracle scores perfectly.

**Tasks (~16).** Feed inventory & contract review (1), reference-window preparation (1),
per-feed validation (8–10), exception triage (1), load-approval memo (1), plus 2 upstream.

**Build: ~4–5d.** Same records-not-prose advantage as RE-1: no planting-artefact risk.
Episode ~15–18 tasks, ~20 min.

**Riskiest item.** Profiling's parameters (reference window, bound width) must be fixed at
construction and not fitted to the instance, or the method's truth becomes a function of our
tuning rather than of the design — the oracle-fitting hazard arriving through the method
definition instead of the oracle.

---

## 4. Cross-cutting: what these three do not settle

- **No linchpin evidence for any of them.** All truth functions are computable by
  construction; whether an LLM worker faithfully executes "match within ±0.01 and ±1 day" or
  "profile against the reference window" is the behavioural question, and it is the item
  most likely to fail in every design here. Complementary blind spots make the *design*
  robust; they do nothing for agent fidelity.
- **Build days are single-point judgement**, and the linchpin line is where they slip.
- **RE-1 and RE-2 are structurally similar to each other** (F1 over a seeded set with
  complementary classes). If a reviewer wants genuine diversity across a multi-env
  replication, choosing both would give less independence than choosing one of them plus
  finance, whose truth is a formula rather than a set operation.
- **Sourceability differs sharply.** Finance's method divergence is documented in the Basel
  framework. RE-1's and RE-2's method pairs are real practice, but the *unit-dependent fit*
  is our construction in both — the same label §121 forced onto eDiscovery, and it should be
  applied here rather than waiting to be asked.
