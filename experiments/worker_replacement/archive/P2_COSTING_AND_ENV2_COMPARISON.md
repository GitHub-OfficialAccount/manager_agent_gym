# P2 record-linkage costing, and the env-2 comparison against eDiscovery

**Status:** estimation only. No code, no runs. Phase-3 input per §129. Task 2 renders a
comparison, not a verdict — the verdict belongs to the synthesis.

---

## 1. P2 — record linkage / entity resolution, costed

### 1a. What gets built

**Generator.** Person records with seeded duplicate pairs. Fields: given name, surname,
date of birth, address (street/city/postcode), a national-ID-like key, phone. The generator
emits the true identity map as it builds, so the truth table is exact by construction and
never inferred.

Degradation is applied per record against **published field-error rates** — the reviewer's
sourcing requirement — as independent per-field corruptions: character transposition,
phonetic substitution, truncation, missing value, format variation (dates, postcodes).
Records carry an **error count** `e ∈ {0, 1, 2, …}`, and the *distribution* of `e` across a
block is the generator's degradation parameter.

**The two matchers, both deterministic given the record set:**
- **Deterministic rule cascade** — exact agreement on a declared key set (e.g. surname +
  DOB + first initial), with a small ordered fallback cascade. High precision, low recall
  under corruption.
- **Fellegi–Sunter probabilistic** — per-field agreement weights `log(m/u)` summed to a
  match score, compared against a **threshold fixed at construction**. Higher recall on
  corrupted records, generates false links between similar-but-distinct people.

**Parameters fixed at construction, never fitted to the instance** — my own RE-2 warning
applied here: `m`/`u` weights and the threshold are constants of the environment, not
quantities tuned per instance. Fitting them would put the oracle-fitting hazard inside the
method definition, where it is much harder to see than in the oracle.

**Truth and scoring.** `true_links(u)` from the generator; `linked(u, m)` a deterministic
function; `s(u, m) = F1(linked(u, m), true_links(u))`. Zero model calls.

**Units and pairing.** Units = **blocks** (surname-initial or geography), 8–10 per instance,
each with its own degradation profile. Pairing unit = the block.

**Tasks (~16).** Source inventory & match specification (1), extraction & standardisation
(1), per-block linkage (8–10), duplicate-cluster review (1), golden-record publication (1),
plus 2 upstream fixed.

**Channel artifacts.** C1 card = the data steward's tooling profile on file ("matches on
declared key rules"). C2 declaration = the `method:` line in the match report ("linked on
exact key agreement" / "linked at Fellegi–Sunter score ≥ τ"). C3 ask = the data owner asking
what matching basis produced a cluster before golden records publish — an ordinary
stewardship question.

### 1b. Build estimate

| item | days |
|---|---|
| generator: records, realistic field distributions, seeded duplicates, per-field corruption at published rates | 1.5 |
| deterministic rule cascade + blocking | 0.5 |
| Fellegi–Sunter: weights, scoring, fixed threshold | 0.75 |
| truth tables + F1 scorer | 0.5 |
| **usable-window sweep** (§1c) | 0.25–0.5 |
| DAG/tasks, cards, prompts, declaration convention | 1.0 |
| logging records, comparability assertions, sensitivity-gate script | 0.5 |
| linchpin validation (do the agents execute the two matchers faithfully) | 0.5–1.0 |
| **total** | **5.5–6.25d** |

### 1c. The usable-window search — arithmetic, pre-episode, cheap

**The window.** Degradation must sit **above** the too-clean-to-differ floor (pristine
records → deterministic finds everything → spread ≈ 0) and **below** the published
deficiency bound (≥3 erroneous fields → deterministic finds nothing → deficiency, not
difference, and the core-tool rule is violated).

**It is offline arithmetic on the generator, and it needs zero model calls.** Both matchers
are deterministic functions of the record set, so for any degradation setting `d`:

```
for d in grid:
    build blocks at degradation d          # generator only
    for each block u: s(u, det), s(u, prob)  # set operations
    spread(d) = Σ_u |s(u,det) − s(u,prob)|
    floor(d)  = min_u s(u, det)            # deficiency guard: must stay > 0
choose d where spread(d) is large AND floor(d) > 0
```

Pick the interior. This is the sensitivity gate run as a **sweep** rather than as a single
check, which is a pleasant consequence: the window search and the gate are the same
computation at different granularity, so building one gives the other free.

**One subtlety that makes the window a region rather than a point.** The published
deficiency bound is a **per-record** property (≥3 erroneous fields). Degradation is applied
per record from a distribution, so a block is a *mixture* of error counts. Two consequences:

1. The window lives in ≥2 parameters (mean error rate × its dispersion), so the sweep is a
   small grid rather than a line. Still arithmetic, still seconds.
2. **The mixture is what keeps the deterministic matcher operational.** Deficiency bites
   only if essentially every record is ≥3-error; with a realistic spread of error counts the
   deterministic matcher always retains the clean tail, so the core-tool rule is satisfied
   *by the mixture itself* rather than by a tuning constraint. Worth naming because it is
   the same structural-vs-tuned distinction the CBS principle is about.

**What the window search does NOT settle.** It fixes the degradation at which the two
matchers, *executed faithfully*, diverge usefully. Whether an LLM worker told to "link on
exact agreement of surname, DOB and first initial" actually does that — rather than
approximating, or quietly matching on judgement — is the linchpin question, is behavioural,
and is not addressed by any amount of sweeping. **The window is pre-episode; agent fidelity
is not.** Keeping these apart matters, because a passed window would otherwise read as
evidence the environment works.

---

## 2. Env-2 comparison: P2 vs eDiscovery

Rendered per §129's open item. **No verdict** — several rows favour each.

| dimension | P2 record linkage | eDiscovery (§121-passed sketch) |
|---|---|---|
| **build days** | 5.5–6.25d | 5.5–7.0d |
| **planting risk** | **absent** — records, not prose; nothing for an agent to notice as synthetic. No pre-check line item | **present** — prose corpus; 0.25d pre-check, plus rebuild exposure if it fails. My named riskiest item |
| **CBS status (tier a)** | **complementary and SOURCED** — probabilistic recall vs deterministic precision is documented in the peer-reviewed literature | complementary but **constructed by us** (coded-responsive vs term-bearing-non-responsive) |
| **class boundary (tier b)** | **experimenter-set** — we choose the degradation distribution per block | **experimenter-set** — we choose the class mix per custodian. Equal on this tier |
| **external anchor (tier c)** | published field-error rates anchor the degradation; the deficiency bound anchors the window's upper edge | EDRM anchors the *scene*; nothing external anchors the class mix |
| **window unknowns** | a real new line item, but **arithmetic, pre-episode, 0.25–0.5d**, and it yields the sensitivity gate as a by-product | none of this kind — classes are constructed directly, so spread is set rather than searched |
| **staleness-story credibility** | steward/vendor **rotation** — the card describes tooling that rotated with staff. Unsourced on staffing (as all candidates are) | review-vendor rotation mid-matter. Also unsourced on staffing; the *scene* is EDRM-sourced |
| **scene sourcing** | linkage practice is well documented; the specific workflow is ours | **stronger** — EDRM is an external, citable process model for the whole scene |
| **reuse of existing sketch work** | harness-side discipline transfers in full (spine shape, cut-list method, denominator enforcement, comparability assertions, pairing arithmetic). Env-specific work does not | **~0.5–1d of env-specific design already done and passed review** (corpus classes, F1 spec, spine, cut list). That is the only row where the sunk work is decisive |
| **truth mechanism** | generator's identity map — set operations | labelled corpus — set operations. **Same mechanism**, which is the diversity point below |

**Two observations I would put beside the table rather than in it:**

- **Mechanism diversity against finance.** §129 recommends finance + P2 partly on
  "a replication that could fail differently". On the truth mechanism, P2 and eDiscovery are
  the *same* object — F1 over a seeded set via set operations — so either one pairs with
  finance (formula truth) equally well on that axis. Where they differ against each other is
  sourcing of the complementarity (P2 stronger) versus sourcing of the scene (eDiscovery
  stronger), and those are different kinds of credibility.
- **The sunk-work row is the only one where the answer is not close**, and it is worth being
  explicit that sunk cost is not an argument for a choice — it is an argument about
  *transition cost*, and 0.5–1d is small against a 5.5–7d build. It should be weighed as
  what it is and not more.

---

## 3. What this costing does not establish

- **No linchpin evidence for P2**, and the window search does not provide any. Agent
  fidelity to a stated matching rule is the open question in every candidate, and P2's
  Fellegi–Sunter arm may be the hardest of all to execute faithfully in prose — an agent
  asked to sum log-likelihood weights and threshold them may approximate rather than compute.
  **That is a specific, named risk for P2 and I would want it checked early**, because if the
  probabilistic arm cannot be executed faithfully, the environment collapses to one matcher.
- Build days are single-point judgement; the linchpin line is where estimates have slipped
  before.
- Published field-error rates are cited as a requirement here; I have not fetched the sources
  and the reviewer's sourcing is the authority for them.
- The window's location is asserted to exist, not demonstrated. The sweep is cheap precisely
  so that its non-existence would be discovered in hours rather than after a build.
