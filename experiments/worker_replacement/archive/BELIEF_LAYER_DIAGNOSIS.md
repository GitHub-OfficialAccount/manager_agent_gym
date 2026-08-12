# Belief-Layer Diagnosis — seed-101 relation extraction

_Research Engineer · 2026-07-25 · evidence for the COMPARATOR_GENERALIZATION.md validation cycle_

> **Provenance note added 2026-07-27.** The label **`v2.6`** is **ambiguous** and must not be used as a
> run identifier. Two distinct runs of the same cell carried it: `71770f08bfd5` (644 rows, r_check
> 0.7317), which **nothing in this analysis used**, and **`c91475579309`** (960 rows, r_check 0.8592),
> which is the run **every v2.6 figure in this document cites** — the t=12 support-side observation, the
> v2.6 assignment timeline, and the r_check table. Preserved at
> `records/preserved_outputs/<cell>/c91475579309/`. Version tokens are now config tags where the
> artifact has one; a release name cannot identify a run.



Diagnostic investigation of the Arm-3 relation-extraction path, prompted by the
belief-model question. Every number below is from direct API calls against
`openrouter/deepseek/deepseek-v4-flash` at temperature 0, seed 101, on real
packets rebuilt from the seed-101 smoke traces with current code. No live smoke
was re-run.

Probe tooling: `probe_extraction.py`, `probe_report.py`,
`probe_rendered_stability.py`, `probe_judgment_stability.py`. Raw records under
`outputs/extraction_probe/` and `outputs/judgment_stability/`.

**Provenance.** Failure classification changed twice during this investigation
(wrapper-name → unwrapped class, then semantic-by-default → semantic-by-allow-list).
Every figure here was swept for exposure to a superseded classifier. None passed
through one: the verdict counts (§1–§3) record errors as a distinct `ERR:` value
that is never counted as a stance; the shape rates (§4) come from structural
validation rather than exception classification; the Ionstream 429s (§6, §8) were
raw unwrapped `httpx.HTTPStatusError` with the status in the message; the §8 table
describes the superseded code deliberately. 260 calls collected under the first
classifier were discarded rather than mixed in.

---

## 1. Headline: Bug 2 is fixed — by the payload, not the model

**Current status (v3.0 comparator, short prompt + plain-text payload, n=40 per
judgment):** diagnostic-contradiction recall is **319/319 = 1.0000** across the
8 gate-scored contradiction judgments, including all three mixed-claim
instances at 40/40 each. Modal verdict correct on 8/8. Sub-fix B works.

**How it looked before**, and why the route mattered. The same three mixed-claim
judgments under the batched comparator and then under the first rebuild:

| batch | batched v2.6 | shipped v3.0 (JSON payload) | v3.0 short+plain |
|---|---|---|---|
| A (e31) | 15–19/20 | 5/20 | **40/40** |
| B (e42) | 0–2/20 | 5/20 | **40/40** |
| C (e52) | 0–1/20 | 6/20 | **40/40** |

Two retractions on the way here, both mine: an early "12/12, both bugs fixed"
claim measured on Batch A alone, and a "prompt innocent, payload guilty"
attribution from a blocked 2×2 that interleaving overturned (§9).

**Sub-fix A (format-robust extraction) works**: the e24 JSON blob is 20/20
`contradicts_fit`. **Sub-fix B works only under the plain-text payload** — the
same rule and the same model score 0/20 when the identical content is
JSON-wrapped (§2).

## 2. Cause: packaging, not model capability

_Positive control, re-run interleaved with the backend pinned to Morph and the
cache manipulation verified per call: cached 4/20, nonce-busted 4/20, Morph
serving all 40 calls. The modal verdict is `supports_fit` under the production
payload, so B's failure reproduces on a second backend, and the cache effect is
an exact null rather than merely a small one._


| | minimal payload | production payload |
|---|---|---|
| **cache-warm** | 17/19 (89%) | **0/20 (0%)** |
| **cache-cold** | 20/20 (100%) | 2/20 (10%) |

Packaging flips the verdict at both cache states; cache state barely moves it at
either payload. **Packaging is necessary and sufficient. Caching is neither.**

Supporting ladder (batch B, n=20):

| condition | A | B | C |
|---|---|---|---|
| L0 — no rule, no bookkeeping | 1/20 | 1/20 | 3/20 |
| L0-prime — rule only, minimal payload | 15/20 | **18/20** | 15/20 |
| production — rule + full payload | 19/20 | 0–2/20 | 0–1/20 |

Two things follow:

- **The inconsistency rule is load-bearing.** Without it, 1–3/20; with it,
  15–18/20. General semantic comparison here is not "the model just knows" — it
  needs an explicit rule. That rule is method-agnostic, so the generalization
  requirement in COMPARATOR_GENERALIZATION.md survives intact.
- **The discrimination is reachable on all three instances.** This is a method
  limit, not a model limit.

**Interpreting the rule's neutral clause** (an interpretation, not a change —
the prompt is not touched, and moving its sha would void the validations). The
rule permits `neutral` "if it is genuinely ambiguous which procedure was
actually used". On the mixed claim — *robust 95th-percentile reference standard
(mean+2\*SD cutoff from reference population)* — there IS a real ambiguity, but
it is not the one the clause is about:

- **unresolvable:** *why* the statement is inconsistent. Did the worker run
  percentile and mislabel the cutoff, or run SD and mislabel the standard?
  Nothing in the text decides it.
- **not ambiguous:** *what procedure the text describes.* The operative noun in
  the parenthetical is **cutoff** — the quantity a standard determines. A
  percentile standard yields a 95th-percentile cutoff; an SD standard yields a
  mean+2\*SD cutoff. The string names one standard and specifies the other's
  cutoff. For the alternative reading — that the parenthetical describes the
  reference population rather than the computation — "cutoff" would have to be
  doing no work in the sentence, and it is the only concrete quantity in it.

So the described procedure plainly departs from the clause, and
`contradicts_fit` is correct. **An ambiguity about the CAUSE of an inconsistency
does not license neutrality about the FACT of it** — and under either resolution
the artifact fails to demonstrate compliance, so the unresolvable half never
reaches the verdict. A `neutral` here is under-calling, not correct restraint.

Recorded because a future labeller will reach for `neutral` on exactly these
grounds, and the rule's wording alone will not stop them.

Positive control: production payload + warm cache **pinned to Morph** reproduced
B's failure at 0/20, against the 0–2/20 unpinned DeepInfra-dominated baseline.
The failure is not backend-specific — two very different backends give the same
near-zero result.

Manipulation verified per call, not assumed: warm arm 16/20 calls at 1792 cached
tokens; busted arm 0/20; Morph served all 40 calls in both arms.

## 3. Instrument nondeterminism

At temperature 0 with a fixed seed, on byte-identical requests:

- **Modal share** 0.907 across 25 judgment keys (n=12); 14/25 keys perfectly
  stable. Flips are minority events around a stable mode — except
  `q_profile_late`, a genuine 6/6 split.
- **Flip-at-least-once is not a stability metric.** It rises monotonically with
  n (24%@n=5 → 44%@n=12 on the same arm) and tends to 100%. Use modal share.
- **Instability concentrates in the prior channel** (`profile_scope_support`),
  not the requirement↔artifact channel. Architecturally expected: comparing
  concrete method text to a clause is sharp; judging whether a profile
  establishes competence is diffuse.
- **It reaches the dependent variable.** Across 5 independent full
  extraction→updater→rendering replays with a fresh cache each:

  | cell | rendered rows differing | decision points differing byte-for-byte |
  |---|---|---|
  | arm3i_q | 924/2880 (32%) | 96/96 |
  | arm3t | 1065/2952 (36%) | 90/96 |

  `diagnostic_contradiction_recall` was `[1.0, 0.5, 1.0, 1.0, 1.0]` on arm3i_q
  and `[0.0, 0.33, 0.33, 0.0, 0.33]` on arm3t — failing the 100% bar in 1 of 5
  and 5 of 5 respectively.
- **Wall-clock drift.** The same byte-identical request gave 19/20 in one window
  and 5/20 forty minutes later. No single-session measurement here should be
  trusted to two significant figures, and any *blocked* comparison carries a
  time confound (see §9).
- **Serving backend substantially predicts the verdict.** Over gate-diagnostic
  judgments, `contradicts_fit` rate by backend spans 0% (Io Net n=28, CoreWeave
  n=22) to 42.9% (Parasail n=14), with DeepInfra at 21.0% (n=210). Backends are
  not randomly assigned — routing responds to prompt shape and cache state — so
  this is association under non-randomised assignment. It supports stratifying
  by backend as the right tool without establishing that routing *causes* the
  drift.
- **Likely mechanism** (recorded, not further probed): continuous batching on a
  large MoE model — batch composition changes the expert-parallel reduction
  order, so numerics differ per request regardless of temperature or seed. Not
  fixable from the client.

## 4. Extraction mode is a scientific variable

Four arms (raw json_schema, `OPENROUTER_STRUCTURED_OUTPUTS`, `MD_JSON`, live)
agreed 100% on parse success and fingerprint-echo exactness across 160 calls —
but **7 of 25 judgment keys have arm-dependent modal verdicts**, including one
where live says `contradicts_fit` and raw json_schema says `supports_fit`.

Instructor mode therefore belongs on the frozen surface alongside
`RELATION_PROMPT_SHA256` and `RELATION_SCHEMA_SHA256`. It is not a transport
detail.

Shape-invalidating rate (returned constraint_ids ≠ frozen set →
`_validate_result_shape` fails → `invalidates_arm`), measured with real
validation: `or_structured` 1/96 (1.0%, ⇒ 25.4% chance of invalidating a cell at
28 calls); `raw_json_schema` and pinned-DeepInfra 0/96. 0 observed at n=96 does
not establish a safe rate.

## 5. `RelationBatchResponse` is fragile — three independent instances

1. The 64-hex `packet_fingerprint` echo requirement.
2. Arm-dependent modal verdicts (§4).
3. Null content returned under non-strict `json_schema` with nested `$defs`,
   fixed only by inlining the schema.

A schema that breaks differently across extraction modes is not a stable
instrument.

## 6. Settled negatives

Recorded so they are not re-litigated:

- **Neither original suspect is responsible.** `MD_JSON` parsed 100% and the
  64-hex echo was exact in all 160 calls.
- **The 45s ceiling is not mistuned.** 0/160 calls exceeded it; p95 12–19s, max
  35.3s, median ~3.3s.
- **Provider pinning does not help.** Prior-channel instability is 8/8 unpinned,
  7/8 pinned DeepInfra, 7/8 pinned Ionstream. It is also operationally fragile:
  Ionstream returned 83.3% parse (all failures HTTP 429), CoreWeave and Parasail
  timed out entirely under sustained load. Pinning concentrates load and gets
  throttled.
- **Voting/self-consistency is BANNED, permanently, by researcher decision**
  (PREREG §7.6). The rationale given is that aggregation is a workaround rather
  than a fix, and buys reliability with call volume. The machinery is removed
  rather than switched off: a live knob for a banned technique is the same
  hazard as a comment asserting a check that does not exist.

  The evidence supports the decision, and supports it more strongly than when it
  was made. Aggregation cannot repair a wrong *mode*, and we have now observed
  three separate wrong-mode failures: the original Bug 2 mixed claim (batch B at
  20/20 `supports_fit`), the fallback failure notices, and the decisive
  false-contradiction cluster contradicting 8–10 of 10 on methods that *match*
  their parent requirement. In each, majority voting returns the wrong verdict
  with higher confidence.

  **This is not a finding that aggregation is useless.** Judgments with a
  correct mode and minority deviation are exactly what it repairs, and this
  corpus contains those too — three tool-capability judgments hold correct modes
  at 16/20, 13/20 and 15/20. The honest statement is that the failures carrying
  the harm *here* are the kind aggregation cannot fix. A reader who takes
  "voting rejected" as an empirical claim about aggregation in general would be
  misreading this section, and it would be our fault.

  Operative consequence: **the false-contradiction bar now has no sampling
  route.** It must be met by construction — input scope, prompt, or
  requirement/artifact alignment. Every remaining candidate changes *what* the
  comparator is asked, not *how many times*.
- **The cheap cache fix does not exist** (§2).

## 7. Reproducibility hazards found along the way

- **`seed` is silently ignored** by Baidu, StreamLake, SiliconFlow, Venice,
  Fireworks, DigitalOcean and DeepSeek — it is absent from their
  `supported_parameters`. On an unpinned route "seed=101" has never been a
  reproducibility guarantee, for any role including the manager.
- **`structured_outputs` support varies by backend**, which restricts routing
  for json_schema requests and is the likely mechanism behind pool-composition
  differences between extraction modes. Any fallback rule must filter on
  `supported_parameters`, not quantization.
- **OpenRouter routes cache-warm requests to the backend holding the prefix.**
  Repeated identical requests stick to one backend and stay warm; nonced
  requests scatter across the pool. Any cache manipulation that does not pin the
  provider varies cache state *and* backend together.
- **`cached_tokens` reporting is provider-specific.** DeepInfra reports a
  64-token floor even under a unique prefix (block/suffix granularity), so a
  nonce does not guarantee a cold prefill there. DeepInfra is the
  production-modal backend, so cache-based conclusions validated elsewhere do
  not automatically transfer.
- **Serving-backend attribution** is now recorded on every structured call
  (`serving_backend` on `structured_llm_response`); see root `CHANGED.md`.

## 8. The invalidation criterion cannot express PREREG §7's distinction

Measured against the real extractor, nothing changed:

| failure injected | `invalidates_arm` | audit `error_type` | original recoverable |
|---|---|---|---|
| transport timeout, 3 retries exhausted | True | `TimeoutError` | already correct |
| parse/validation | True | `LLMInferenceTruncationError` | yes → `ValidationError` |
| HTTP 429 (transport) | True | `LLMInferenceTruncationError` | yes → `HTTPStatusError` |

Two independent defects:

1. **`invalidates_arm` is `_failures > 0`** — every class increments one
   counter, so §7's transport-vs-semantic line is not expressible in the flag.
2. **`_generate_with_transport_retry` catches only `TimeoutError`.** Every
   other transport failure (429, 5xx, connection reset, read error) arrives
   pre-wrapped as `LLMInferenceTruncationError`, bypasses the retry loop
   entirely, and invalidates the cell on first occurrence under an audit name
   indistinguishable from a semantic failure. §7 *names* upstream 5xx as
   retryable, so this under-implements the preregistration as literally
   written.

`LLMInferenceTruncationError` is a catch-all wrapper, not a diagnosis — the
original class is present on the exception and was simply never read.

**Resolved by PREREG §7.1** (human researcher, 2026-07-25, before any
confirmatory seed): transport class retried byte-identically with backoff,
semantic class invalidating and never re-rolled, unclassified invalidating.
`invalidates_arm` now fires on semantic + unclassified only; transport
exhaustion sets `requires_regeneration` instead. Per-class and per-exception-type
counts in every snapshot. See §7.1 for the amendment and its rationale.

**Counterfactual.** The pinned-Ionstream run returned 16 HTTP 429s in 96 calls.
Under the live extractor each would have invalidated a cell on first occurrence
and been filed as a semantic failure — which §7 classes as a real result, never
to be re-rolled. Ordinary rate-limiting would have been reported as genuine
extractor failure, and our own discipline would have barred correcting it. That
is a validity failure, not an availability one.

**This defect is independent of everything else here.** With a perfectly
deterministic extractor and a perfect comparator, a 429 would still kill a cell
and still be misfiled.

## 9. Four checks that produced false reassurance

Each is why a check that cannot fail loudly is worse than no check.

- **The offline gate had been dead since `c0809c0`.** `arm3_replay._score` read
  `item["compatibility"]`, but the comparator generalization renamed that field
  to `stance` (`supports_fit`/`contradicts_fit`/`neutral`). Every gate
  invocation raised `KeyError` — which reads as no-news. Fixed at
  `arm3_replay.py:722,743`. The gate could not have caught the Sub-fix B
  regression because it could not run.
- **A corpus item was mislabelled** "no method_claims at all" based on the
  smoke's `no_relation` outcome, which was itself the *old* comparator failing
  to parse the very case Sub-fix A fixes. The mislabel is a fossil of Bug 1.
- **Transport failures were filed as semantic failures** (§8). The smoke's one
  failure happened to be an asyncio timeout — the single transport class the
  retry loop catches — so the aggregate picture looked sound while the general
  case was misclassified.

- **A `PoolTimeout` escaped the catch clause entirely** — `_judge` caught a
  fixed tuple of three exception types, so anything outside it aborted the whole
  extraction with no failure record, no per-class count and no snapshot. It
  would have surfaced as a crashed cell mid-matrix, not a bad number.

All four were invisible in the same way: a check that could not run, a label
that was wrong, a class that was never read, and a failure that escaped
unrecorded. None would have been caught by anything then in the harness.

### The pattern behind three of them

The retry loop's `except TimeoutError`, PREREG §7.1's first draft enumerating
library exception names, and the `_judge` catch tuple are **one bug at three
layers**: a closed enumeration standing in for an open category, where
staleness fails *permissively* in the direction of the original defect.

What makes it a pattern rather than three incidents is that each enumeration
looked complete against the failures actually observed. The retry loop was
written when the only failure anyone had seen was an asyncio timeout — which is
exactly what the smoke recorded. **Each list was empirically adequate and
structurally wrong.**

### A second pattern: blocked designs confound the variable with time

Distinct from the closed-enumeration family above, and conflating them weakens
both. That family is *a category defined by an incomplete list*. This one is *a
confound between an independent variable and wall-clock*.

A byte-identical request scored 19/20 in one run and 5/20 forty minutes later.
Every comparison in this investigation was initially run as blocks — one
condition to completion, then the next — so condition was confounded with time
throughout. Re-running the payload/prompt 2×2 interleaved (conditions
round-robined per iteration) overturned its conclusion: the arm I had declared
innocent scored 19/20 blocked and 12/20 interleaved.

**Drift hits conditions near the decision boundary hardest.** In the interleaved
run the robust condition was 10/10 in both halves and the dead condition 0/0 in
both, while the two marginal conditions swung (one went 10/10 → 2/10). That is
what makes a blocked design dangerous rather than merely untidy: drift perturbs
precisely the cells whose value you are trying to read, and leaves the
already-decided ones alone.

The same confound was then found in the experiment itself: `_resolve_cells`
iterates arms in a fixed order within each seed, and that order *is* the ladder
contrast, so arm identity is perfectly confounded with execution position in
every seed. A monotone drift would manufacture a monotone ladder effect in the
predicted direction — it would not look like noise, it would look like H1. Same-
seed pairing does not help: `native` is always first in its block and `arm3t`
always last, so pairing preserves the confound. Addressed by PREREG §7.3
(randomised cell order, ordering seed recorded, drift reported as a diagnostic).

**Shared cause, two patterns.** Both were built against the failure modes already
observed rather than the space of possible ones — an enumeration adequate to
every failure seen, and a design adequate to a stationary instrument. Neither is
a special case of the other.

**Quote contrasts, not levels — and note where that fails.** Re-running the
pinned-Morph control interleaved gave 4/20 vs 4/20 where the blocked version
gave 0/20 vs 2/20: the absolute rate moved between sessions, the contrast did
not. Interleaving removes drift from a comparison but not from a level.

That is a real limit on the discipline, because **both gate criteria are
levels**. "Diagnostic-contradiction recall = 100%" and "false contradictions on
competent no-change scopes = 0" are absolute and cannot be restated as
contrasts. So the gates are exactly where drift is least mitigated, and
319/319 and 1.07% are single-session levels of the same kind that moved
1/20 → 4/20 elsewhere. A validated instrument could fail a re-run for reasons
having nothing to do with the instrument.

Mitigations applied to the gate-trace run: k repeats separated in time rather
than batched, with wall-clock and serving-backend mix recorded per repeat; the
between-session variance component measured rather than assumed; and the
exposure reported as a limitation of the **gate design**, not only of the
measurement. Whether the criteria should become "100% on k of k sessions" is a
preregistration question, deliberately left open here.

### Prose decays too, and prose carries the interpretation

A provenance sweep of this document looked for stale *numbers*, because the
discarding of 260 calls had been about numbers. The actual decay was in a
statement of code state: §8 asserted the invalidation defect was still live and
untouched, which was true when written and false the moment PREREG §7.1 was
implemented. A reader would have drawn the wrong conclusion from correct
figures.

The same audit applied to PREREG found three more: a section still headed
"PINNED" long after the pin was declared open, a v2.6 certification issued by
the gate later found unrunnable, and a Phase-1 figure with no note that it was
never seed-reproducible.

This is the same class of lesson as *empirically adequate and structurally
wrong*, one level up. There, a list was correct against every failure observed
and wrong about the category. Here, a sentence was correct when written and
wrong about the current state. Both decay silently, and neither is caught by
re-checking the numbers.

Corollary worth keeping: **deliberately stale text is fine when labelled as
such.** §8's description of superseded code is correct, because describing it is
its purpose. The defect was the sentence claiming the defect was still live —
not the past tense itself.

### Two operational rules that fall out of it

**Every count names its unit.** This corpus has four, and they differ by large
factors:

| unit | meaning | example |
|---|---|---|
| **instances** | judgments issued, recurring across timesteps and cells | 185 |
| **distinct questions** | unique (clause, method) text pairs | 141 |
| **draws** | model calls including repeats of one question | 350 at n=10 |
| **calls** | draws plus retries; what the bill counts | 89.25/cell |

Every judgment here recurs, so **every count is ambiguous between instances and
distinct questions unless it says which**. We conflated three different pairs
among these four in one day: 24 instances read as 24 questions on the
tool-capability family; 185 instances read as 141 questions corpus-wide; and a
reviewer's three judgments read as three questions when they were three
instances of one — a mixed-claim question whose "independent replication" would
otherwise have been 5 draws against their 60.

The third happened *after* the first two had been caught and corrected, which is
why this is a rule rather than a caution. A number without its unit is not a
measurement, exactly as a number without its config tag is not a result.

**Cross-artifact fragmentation — a lead, not a proposal.** Two fragmentations
are discussed elsewhere here: the requirement split into clauses, and the
artifact split into atoms. There is a third, and no shape considered — A, B or C
— touches it.

The reference statistics needed to validate ANY cutoff live in a **different
artifact**. The profile task reports `income (mean 70,713, std 43,909)`;
a degraded audit reports `cutoffs: income=158531.64`. And 70713 + 2(43909) =
158531 — the number is provably the mean+2·SD cutoff, i.e. direct evidence of the
degraded procedure in the artifact's own output. **But the packet is (parent
requirement, THIS artifact)**, so within it `158531.64` is uninterpretable: there
is no way to distinguish it from the percentile cutoff `151164.49` without stats
the model was never shown.

So the strongest available evidence of the degradation is **unreachable by
construction in every shape**. Corroborating for a reader who knows the reference
stats; inert for the model.

**The lever and the instrument share a dependency, and it is satisfied HERE and
at risk under LEVER A.** The detection chain rests on the worker volunteering a
`method:` line. Measured on this corpus, at the ARTIFACT level (not the atom
level — 24% of atoms carry a method claim, which is a different and misleading
number):

| cell | artifacts with an extractable method claim |
|---|---|
| `control_arm3i_q` | 15/15 = 100% |
| `silent_arm3i_noq` | 16/18 = 89% |
| `silent_arm3i_q` | 16/17 = 94% |
| `silent_arm3t` | 16/18 = 89% |
| **total** | **63/68 = 93%** |

**And the 7% is task failure, not reporting failure.** The five artifacts
carrying no extractable method were inspected directly rather than inferred from
`68 − 63 = 5`: every one is a failure notice — *"- Failed: Stakeholder failed to
complete task"*, *"- Failed: None"*, two with *"- Retry requested by manager"* —
with no work product to describe. So:

> **artifacts representing completed work, carrying an extractable method claim:
> 63/63 = 100%.**

A worker that completed a task always reported its method, under every arm. That
is a materially stronger statement than 93%.

So under the TOOLSET lever the dependency holds **in fact**: the perturbation
removes a tool and does not touch the reporting instruction, and reporting
behaviour is stable across arms. 8/8 recall is conditional on a behaviour that
was observed, not merely assumed.

**Under LEVER A it is structurally at risk.** Lever A swaps the worker's model
AND prompt — and the prompt is what instructs the worker to report method and
cutoffs. So that lever manipulates the mechanism the instrument depends on for
its signal. A null would then be ambiguous between "the instrument transferred
and found nothing" and "the instrument stopped receiving its input", and nothing
in the current design distinguishes them. **Two checks belong in Lever A's
design:**

1. verify both prompts carry an equivalent method-reporting instruction, and
   **record the two instructions side by side** rather than asserting equivalence
2. **measure** reporting behaviour under both — equivalent wording does not
   guarantee equivalent compliance from a different model. The observable is the
   table above, per arm, and it needs no comparator. If it differs between arms,
   the transfer test needs a different design before it runs.

**Measure EXTRACTABILITY, not presence.** Because a completing worker apparently
always reports a method, the Lever A risk is narrower and more specific than
"will it report one": it is whether the report is **extractable**. We have hit
that failure once already — Bug 1 was `extract_method_text` missing a method that
was present, in a JSON-formatted artifact. Presence and extractability diverge
exactly where a different model formats its output differently, which is the most
likely consequence of swapping a model. So the observable is *the fraction of
COMPLETED artifacts whose method claim is extractable, per arm*, and a drop there
is indistinguishable from a judgment effect unless measured separately.

**Not proposed as a fix.** Joining artifacts is a larger scope expansion than C;
the current levers do not need it (the method-string inconsistency is sufficient
signal, and 8/8 recall proves it); and it raises its own questions about what the
manager could plausibly hold in view at once.

**Why it matters anyway:** the instrument detects the change through the worker's
**self-description**, not through its **output**. A degraded worker that reported
nothing about its method would be undetectable; one that lied consistently would
be undetectable. That is a limitation of the approach rather than of this
implementation, and a referee will ask what happens when the artifact does not
confess.

**So the scope claim needs narrowing, and "unsignaled" is doing work it has not
earned.** What is demonstrated is detection where **the artifact reports its
method**. The CHANGE is unsignaled; the METHOD is self-reported. Detection
without self-report is outside what was tested and outside what this instrument
can see. That is a smaller claim than "detects unsignaled behavioural change from
ordinary work artifacts", and it is the one we have evidence for.

**Atomisation-as-comparator-input and the atomic ledger are different things,
and only one of them has been measured.** They must stay separable in this
record, because "atomisation was harmful" reads as "the ledger arm was useless"
and that inference is not available:

| | status |
|---|---|
| **atomisation as the COMPARATOR's input** — sending one `method:` atom to answer a clause demanding a sum, a method and cutoffs | **measured, harmful.** The artifact reports all three; we discarded the compliance before asking. Drives the decisive false-contradiction cluster. |
| **the atomic evidence ledger as ARM-2's treatment** — what the manager sees | **never measured.** The confirmatory run has not run. |

The ledger is a **term in the mechanism test**: PREREG §1's H2 rule is
`arm3i_noq <= ledger < arm3i_q`, and §6 preregisters its expected null as a
deliverable. Removing it would make H2 untestable and any Arm-3 gain
unattributable. A comparator that stops reading atoms does not imply a manager
that stops seeing them — two consumers, one source.

### What actually caught things

The count is not the finding — **the detection rate is**. Seven-plus defects
surfaced because two independent parties were explicitly asking what would break
each check. A project without that arrangement finds fewer, *not because it has
fewer but because it detects fewer*. The observable is defects caught; the
unobservable is defects present. So the claim this record supports is not "these
instruments contain many defects" but: **adversarial review of measurement
machinery surfaces defects at a rate that should worry you, and here is what they
look like.**

Four mechanisms did the catching, ordered by cost:

| | mechanism | cost | catches |
|---|---|---|---|
| 1 | **test a claim ABOUT a check** | free, before any result exists | the depth-7 overtake bug (would the equivalence test catch a depth change? it would not); the missing mirror (a §4 paragraph contradicting a reversal stated elsewhere); the sha comment (grep for the test it asserted existed); §9 step 5's consistency (verified rather than accepted) |
| 2 | **check a COUNT against an independent expectation** | free, before spending | family population 20 → 18 → 12; atom-share 24% vs artifact-share 93%; the "15" that were 12 |
| 3 | **read source you did not write** | cheap | the stability probe's payload; `exposure()`'s empty join; the "52"; §7.9's pooled 0.73 |
| 4 | **produce a wrong result and retract it** | expensive — calls, or a claim withdrawn | the `evidence_id` collision (80 calls); the recall probe's record key; the gate KeyError live since `c0809c0` |

Categories 1 and 2 are free and catch before anything is spent. Category 3 is the
only one that catches a **sound computation answering a different question**.
Category 4 is where the cost lands.

**Nothing was caught by re-running and getting the same answer**, and that is
structural rather than incidental. **Reproducibility checks determinism, not
correctness.** A defect producing a consistent wrong answer reproduces perfectly:
the stability probe would have returned 0.854 forever, the exposure join clean
zeros every time. And on a NONDETERMINISTIC instrument it is worse — "reproduced"
cannot be distinguished from "coincided", so the check catches nothing at all.
The drift finding proves this instrument is nondeterministic, and it was itself
found by two derivations disagreeing, not by any run reproducing.

So "I re-ran it and got the same answer" is worth *less* here than in ordinary
software, which is the opposite of the instinct most readers bring.

**This is not an argument against reproducibility, and the two claims are not in
tension:**

> **Reproducibility is necessary for audit. Re-deriving your own number and
> getting the same answer detects nothing.**

The first is why an hour went into rescuing records from an ephemeral scratchpad,
why records are content-keyed, why the payload is persisted beside the key, and
why the manifest says which script produced which file — a result nobody can
re-derive cannot be checked by anyone. The second is why "I re-ran it" is not a
check.

The clearest demonstration is in this investigation's own records, same morning,
same author: `stability_n20.json` persisted `payload` beside every key and was
**recoverable** — re-keyed on content, 237/249 rejoined. `stage_b.json` persisted
only `samples`/`providers`/`set`/`truth` and **perished** — 19 of 35 judgments
unidentifiable, including the seven carrying 58% of its contradictions. The
difference was whether a SECOND DERIVATION was possible, not whether a re-run
would agree.

**Attribution runs both ways.** The errors came from whoever was closest to the
design and were caught by whoever was not — that is the whole lesson, and it is
lost if the record reads as one party's mistakes found by another. Roughly equal
numbers originated with the implementer and with the specifier, and the
independent reviewer's three blocking findings were all on **specifications**
rather than on implementation, which is the cleanest evidence in the record that
those are different failure surfaces.

**Bound on all of it:** one investigation, one comparator, one model, one corpus,
about two days. The defect *families* may generalise; their *frequency here* says
nothing about frequency elsewhere.

**A retracted basis does not leave its conclusion standing.** When a cited
figure or a derivation is withdrawn, the conclusion built on it does not survive
by default — it has to be re-argued, or it goes with the basis. Three instances
in one day, and in each the conclusion outlived its support silently:

| retracted | conclusion left standing |
|---|---|
| the "52 constraints" promiscuity count | the pattern-promiscuity concern |
| the cited affirmation figure "0.73" | the 0.80 floor derived beside it |
| the exonerating derivation for that floor | the floor's endpoint justification |

This is a distinct class from the others catalogued here: not a closed
enumeration, not a blocked design, not two correct statements composing badly. It
is **a load-bearing input removed without the load being recomputed**, and it is
invisible precisely because the retraction itself feels like a completed
correction.

**Print the numerator and denominator beside every rate.** A rate alone cannot
distinguish "0 errors in 240 calls" from "0 errors in 0 calls".

**Any keyed lookup must assert its join succeeded.** A ground-truth file keyed
on judgment fingerprints matched zero of 36 after a payload field was added, and
returned a clean empty set — indistinguishable from a population with no errors
in it. The header printing set sizes is the only reason it was caught.

Underlying property, worth knowing rather than rediscovering: a judgment
fingerprint is a content hash over the whole payload, so **adding any payload
field silently invalidates every fingerprint-keyed artefact** — replay caches,
ground-truth files, label maps.

### A documented asymmetry, so it is not "fixed" later

`_BOUNDARY` ("judge only from the text supplied…") is in `PROFILE_SCOPE_PROMPT`
and **deliberately not** in `ARTIFACT_CLAUSE_PROMPT`. A clause judgment's
payload carries only the requirement clause and the method claim, so no hidden
state is reachable to infer — the guarantee rests on the input restriction, not
the instruction. Adding the sentence would move the prompt sha and void the
recorded validation (319/319, 1.07%, 20/20) in exchange for nothing the model
could otherwise reach. Recorded here and at the constant because a future
reader will otherwise read the asymmetry as an oversight.

### Primary engineering lesson: derive probe input from the production path

Established three independent times in this investigation, same fix each time:

| drift | fix |
|---|---|
| probe and live audit classified failures differently | probe imports `classify_failure` |
| validated prompt ≠ shipped prompt | validation probes import `ARTIFACT_CLAUSE_PROMPT` |
| detector control fed a hand-assembled input production never sends | control built via `judgments_for` |

**A probe that reconstructs its input measures something production does not
do.** Every instance produced a number that looked like a result: a false
classification rate, a validation that described absent code, and a detector
accuracy of 10.62% that would have killed a working design. This is the single
rule from this investigation that would have prevented the most damage.

**On who catches what.** The catching mechanism was adversarial review, and it
ran in both directions. Defects introduced by the implementer and caught by the
reviewer, and defects introduced by the reviewer and caught by the implementer,
occurred at comparable rates — a closed enumeration in the §7.1 draft, a
targeting criterion that would have leaked answer-key information, an
allow-list proposal that reinstated the pattern it was meant to remove, a
cell-survival table keyed on the wrong input, an invented variance factor, an
over-bought sampling allocation. Neither party caught their own design before
spending.

So the lesson is positional, not dispositional: **whoever did not commit to a
design can see its scope.** "Keep a reviewer" is supported; "the reviewer is
more careful" is not, and would suggest hiring care rather than arranging
positions.

### Diagnostic: a result too tidy for its input variety is a test defect

The counterpart to "a check that cannot fail loudly" — actionable, because it
says what to look at rather than what to avoid.

- A detector answered "not a method" **20/20 on six different method names**.
  That is not a weak model; it is a model answering a different question. The
  probe was feeding it an extracted field value instead of artifact text.
- A ground-truth join matched **zero of 36** judgments and returned a clean
  empty set — indistinguishable from a population containing no errors.

Uniform failure across semantically varied inputs, and perfect emptiness, are
both signatures of a mis-specified test. **Treat a result too tidy for its input
variety as a test defect until proven otherwise.**

### Secondary lesson: name the parameter that would break the check

### Methodological contribution: test the check, not the thing checked

The generalisable fix: **define the category by a property, make the fallback
conservative, then assert the fallback with a test using a type that does not
exist yet.** The `SomeFutureSDKError` test would have caught all three layers,
because it tests the *shape* of the classification rather than any member of it.

The gate canary is the same principle in a different domain — a synthetic
contradiction asserting the scorer can read the comparator end to end, plus a
test that simulated field drift makes it *fail* rather than pass quietly. Both
are tests of the check itself rather than of the thing checked.

Every one of the four false reassurances above was a check that could not fail
loudly. That is the methodological point this investigation most supports.

## 10. The fallback branch can commit the error under study

`judgments_for` originally skipped a requirement_artifact packet whenever
`extract_method_text` found nothing, which would render a silent `neutral` for
any method format we had not anticipated — Bug 1's failure mode through a new
door, and invisible because there is no call to inspect. The skip is now
affirmative: a packet skips only when it carries **no visible artifact text at
all**; otherwise the artifact's own words are sent verbatim and the verdict is
measured. `method_extraction` records `explicit` vs `full_text_fallback`.

**State honestly what this caught.** Nothing yet. Across the whole corpus the
fallback population is 12 judgments carrying three distinct texts — `- Failed:
Stakeholder failed to complete task`, `- Retry requested by manager`, `-
Failed: None`. These are task-failure notices, not artifacts in an
unrecognised method format. The protection is **prospective**: it guards a hole
we have not fallen into.

**Zero gate-diagnostic judgments are in the fallback population** (0 of 9 per
cell, confirmed by enumeration), so the recall and false-contradiction figures
above cover the gate-scored set in fact, not merely in principle.

**Why a contradiction here would be worse than a false positive.** The correct
verdict on a failure notice is `neutral`. If `- Failed: Stakeholder failed to
complete task` drove a `contradicts_fit` against a method clause, the belief
layer would be inferring a *competence* judgment from *completion status* —
completion-as-competence conflation, which is the exact Phase-1 mechanism this
experiment exists to study. A contradiction there is not just a gate-bar
violation; it is the instrument committing the error under investigation.

The mitigation, if the measured rate warrants one, is neither to reinstate the
skip nor to enumerate "status-only" shapes — both are the closed-enumeration
pattern. It is to **state the absence rather than let it be inferred**: tell the
model the artifact reports no method, so the design rule (no method claim →
neutral) is given rather than deduced. No enumeration, no silent skip, no lost
measurement.

## 11. Open

_Validation of the rebuilt comparator follows the PREREG §7.2 re-clearance
path: unit tests, per-judgment stability (hard/clean split), run-level exposure
reported separately for diagnostic and non-diagnostic judgments, k-repeat gate
traces with the canary armed, and the §7.1 per-class failure table. Only then
may a pin be proposed._

- **The A/B/C asymmetry is unexplained.** A survives the heavy payload; B and C
  do not, with no content difference found (identical modulo batch letter,
  identifiers, clause ordering, and packet timestep). Cold production still
  fails, so cache history does not explain it. May dissolve under the rebuild —
  re-check afterwards rather than hunting it now.
- **Per-judgment stability across the full corpus is unmeasured.** The 15–18/20
  L0-prime rates are the *hardest* case (internally-inconsistent mixed claim);
  clean cases look far better (e24 at 20/20). In flight: 237 distinct judgments
  × n=20 against the rebuilt comparator. Step 2 of the PREREG §7.2 re-clearance
  path; the voting decision turns on it and it is deliberately not estimated
  anywhere in this document.

  Two limits to carry with that number when it lands. It is deduplicated by
  content fingerprint, so it measures judgment **difficulty**, not run-level
  exposure — §7.2 step 3 bridges the two arithmetically. And its samples are
  fired concurrently, which leaves little time for the prefix cache to warm; at
  light payload cache-warm scored 89% against cache-cold 100%, so the headline
  is plausibly optimistic relative to production's sequential path. A sequential
  control on the hard cases plus a clean subset bounds it.

## 12. Pre-committed reading rule for the C-vs-(a) contradiction table

_Written and committed **before the table exists**. The run is in flight at the
time of writing (80 of 320 draws on the current record set). This section is here
because every reading criterion in this investigation that lived only in
conversation drifted by the time its numbers arrived — see §9's "prose decays
too" — and because the affirmation half of this same comparison has already been
reported once on records that turned out to be corrupt. The rule is fixed now so
that it cannot be fitted to the result._

**What is being decided.** Whether the rebuilt comparator ships as shape **C**
(whole requirement vs. whole artifact) or falls back to form **(a)** (whole
requirement vs. one atom). Not whether C's affirmation number is large.

**What the data is.** 40 records, 20 questions × 2 arms, all drawn in one session
so both halves share one drift condition. Depth is **not** uniform:

| set | questions | records | draws each |
|---|---|---|---|
| affirmation (matched method) | 12 | 24 | 10 |
| contradiction, plain mismatch | 5 | 10 | 5 |
| contradiction, **mixed claim** | 3 | 6 | 5 → **10, see amendment** |

The 3 mixed claims are internally inconsistent artifacts that name the required
standard while describing a different one. They are the discriminating cases,
because they are exactly where a reader that has learned to affirm produces a
*confident wrong* `supports_fit` rather than a visible failure.

> **Amendment, 2026-07-26, before the data.** The first version of this section
> stated "10 draws each" across all 20 questions. That was wrong: the
> contradiction set is n=5. Caught by Research Engineer against the record set,
> and it landed on the deciding test — the branch table below keys on a *modal*
> verdict, and at n=5 a mode is 3-of-5, so one question at 3/2 and two clean
> would have satisfied row 1 on evidence one draw from row 4. The depth
> allocation put the shallowest sampling on what this section itself calls the
> entire test. It was a defensible allocation when made (depth where the prior
> was weakest, and the prior was then weakest on affirmation) and stale by the
> time the branches were written.
>
> Two changes, both approved before any of this data was read: the three mixed
> claims are extended to **n=10 in both arms** (30 additional calls, run in the
> same session so clause 2 below still applies), and "modal verdict" — which was
> the underspecification that let the error hide — is now given an explicit
> threshold. The five plain mismatches stay at n=5; a wrong mode there is visible
> at that depth and they are the stronger form of rows 2–3, not the test.
>
> Recorded as an amendment rather than a silent correction, for the same reason
> §13 records why §7.4 was withdrawn: "we fixed the criterion while the run was
> in flight" means nothing without the reason, and a pinned rule that can be
> quietly rewritten is not pinned.

**Determinacy threshold.** A question's verdict is determinate iff **≥8 of 10
draws agree**; at 5–7 it is indeterminate and the question counts toward row 4.
C already met 10/10 on every affirmation question, so 8/10 is a lenient bar for
it, not a strict one.

**Why the affirmation half cannot decide this on its own.** C affirming 12/12
matching questions at 10/10 with zero hedging draws is what a real improvement
looks like **and** what an affirmation bias looks like. The two are
indistinguishable on the affirmation set by construction. Only the mismatches
separate them.

**Branches, by C's determinate verdicts on the three mixed claims.** Rows are
evaluated **in order**; the first that applies is the reading.

| condition across the 3 mixed claims | reading | consequence |
|---|---|---|
| **any one** determinate at `supports_fit` | **Affirmation bias.** C credits an artifact for naming a standard it does not follow. One confident wrong answer is the disqualifying observation — it does not need a majority. | C disqualified; the 12/12 becomes the symptom, not the result. Fall back to (a). |
| **all three** determinate at `contradicts_fit` | Real effect. C affirms matches and contradicts mismatches, dominating (a) on both bars. | Adopt C. The affirmation gain stands as a finding. |
| all determinate, one or more at `neutral`, none at `supports_fit` | **Hedging.** Fails recall — cause-ambiguity does not license fact-neutrality, settled 2026-07-26 — but is not evidence of bias. | Neither shape clears. The affirmation result survives alongside a separate, named recall problem. No pin. |
| **any** question indeterminate (5–7/10), none determinate at `supports_fit` | Depth does not support a reading. | Report per-question destinations; do not pool three questions into one rate. No pin, and no claim in either direction. |

Ordering matters and is deliberate: a single determinate `supports_fit`
outranks two clean contradictions, because the failure mode under test is a
*confident wrong* answer, and averaging it against successes is precisely how it
would be missed.

The distinction between rows 2 and 3 is diagnostic, not an escape hatch: **both
fail the recall bar.** They differ only in whether the affirmation number is
impugned. This is deliberately noted because an earlier supports-vs-neutral
branch in this investigation *was* an escape hatch — it attributed a comparator
failure to the preregistration — and the surface similarity should not license
reading "it went neutral" as a pass a second time.

The remaining 5 contradiction questions are plain mismatches. C failing on those
is a stronger form of rows 2–3, not a separate case.

> **Amendment 2, 2026-07-26, AFTER the data. Read this as the weaker kind of
> amendment and weigh it accordingly.** The result landed on a boundary the table
> above does not cover, and the defect is in the rule, not in the reporting.
>
> **What landed.** Mixed claims A and B: `contradicts_fit` 10/10 under both arms.
> Mixed claim C: **(a) 10/10 `contradicts_fit` → C 5 `supports_fit` / 5
> `contradicts_fit`, zero `neutral`.** By the letter, 5/10 is not determinate, no
> row-2 trigger fires, and the reading falls to row 4.
>
> **Why the letter is wrong here.** The 8/10 threshold was set to stop a weak
> majority from establishing a *verdict* — a **capability** claim, where crediting
> C with correct reading requires reliability. Row 2 is not a capability claim. It
> asks whether C ever produces a confident wrong answer on an internally
> inconsistent artifact — an **existence** claim, for which one occurrence is
> evidence and 5/10 is overwhelming. The same threshold was applied to both
> directions when they require opposite evidentiary asymmetries. That is the
> defect.
>
> Row 3/4's disposition ("does not impugn affirmation") was written for **hedging**
> — decay toward `neutral`, a failure of nerve. What occurred is a bimodal split
> between correct and *confidently wrong*, with **not one `neutral` draw**. That is
> not an uncertain instrument; it is an instrument with two modes that selects one
> per draw. Filing it under the hedging disposition would apply a reading built for
> a different failure.
>
> **Amended condition for row 2:** *any* `supports_fit` draw on a mixed claim, at
> any rate, triggers it. Determinacy governs verdict attribution only. This fires
> row 2 on the present data: **C is not adopted.**
>
> **Direction of the amendment, stated because it is the only real check on
> post-data rule changes.** It cuts against the shape the lead scientist predicted
> and advocated, and against the strongest number the run produced. That is
> evidence of principle rather than proof of it — the reader should still discount
> this amendment relative to the pre-data rule, and the pre-data rule's own
> verdict (row 4, no pin) is recorded above unaltered.
>
> **Practically nothing turns on it:** "no pin" is the outcome under every reading.
> What the amendment changes is what may be *claimed*, which is why it was not left
> to the person whose arm produced the number.

> **Amendment 3, 2026-07-26, after the data. Denominators audited; three of the
> lead scientist's claims withdrawn.**
>
> **The three "mixed claims" are one question.** Requirement identical but for the
> batch letter at position 67; method line **byte-identical**; all eight mismatch
> questions share one batch-normalised parent. Pooled, arm C mis-affirms at
> **5/30 = 16.7% per draw** against (a) at 0/30. This makes C's defect a *rate on a
> characterised population*, not a single-item quirk — worse than the
> "one of twenty questions" framing that both the lead scientist and the reviewer
> initially used.
>
> **Distinct-question audit**, normalising the batch letter and counting distinct
> (parent, method) pairs:
>
> | population | nominal | distinct | note |
> |---|---|---|---|
> | affirmation (matches) | 12 | **12** | 12 different method strings; CI over 12 units is *not* inflated |
> | contradiction (mismatches) | 8 | **4** | two replicate families of 3 + two singletons; **two divergence patterns total** |
>
> The lead scientist predicted pseudo-replication in the affirmation set and it is
> **not there**. It is in the mismatch set, which is the population carrying the
> decision. Filed as **a denominator that was never audited** rather than as a
> count that was really N/k: the affirmation 12 was correct, the mismatch 8 was
> not, and nobody had checked either.
>
> **Caveat on the affirmation unit.** The 12 distinct method strings are surface
> variants of **two** underlying standards (4 percentile-family, 8 SD-family). So
> 12 is the correct unit for a claim about *robustness to surface form* — which
> this investigation has shown is what matters — and the wrong unit for a claim
> about 12 independent *semantic* tests. Phrase it the first way.
>
> **Gold label is mechanical, and the artifact refutes itself numerically.**
> `task_ground_truth.json` fixes the required method as `percentile` with truth
> values A=64, B=89, C=97; the artifacts report 59, 71, 80 — the SD-procedure
> answers — with SD cutoffs throughout (158531.64 = 70713 + 2·43909). The label is
> a regex over the artifact's own method line, not anyone's reading. `supports_fit`
> is indefensible on every construal, since genuine ambiguity would license
> `neutral` and arm C returned **zero neutral draws in 175**.
>
> **Withdrawn by the lead scientist:** (i) the *polarity trade-off* — (a)'s match
> failures are 40 neutrals against 4 contradictions, so the axis is assertiveness,
> not polarity; (ii) the *gold-label dissolution hypothesis*. Asking which
> replicate group the variance landed in is a category error — three draws-of-ten
> from a single p≈0.167 process — so "why batch C" is not a question about the
> corpus and no further spend goes to it.
>
> **The naming-credit withdrawal is itself RETRACTED, 2026-07-26 — it was invalid.**
> It was withdrawn on the argument that "all three mixed claims name the required
> standard and C answered two at 10/10, so a name-crediting reader would fail all
> three." **The three are one question.** There was no "all three" to fail, and the
> argument treated replicate draws as independent trials of a deterministic
> mechanism — the same pseudo-replication error this amendment documents, committed
> inside the amendment that documents it.
>
> Corrected: C answered one question correctly on 25 of 30 draws. A *partial*
> name-crediting tendency firing ~17% of the time predicts exactly that. So
> naming-credit returns as a live CANDIDATE — not established, but not refuted.
>
> It is a candidate worth testing because the method line contains **both**
> standards: `robust 95th-percentile reference standard (mean+2*SD cutoff from
> reference population)` — required standard as the head noun, actual procedure in
> the parenthetical. **Prediction:** if C credits the head noun, inverting the
> order (`mean+2*SD cutoff (robust 95th-percentile reference standard)`) should move
> its error rate systematically. That is a corpus variant plus a replay, and it is
> a mechanism test rather than another shape.
>
> **Reported alongside the disqualification, per the reviewer:** as a *rate*
> comparison, 5/30 vs 0/30 gives **p = 0.052** over a four-question base. The §12
> rule was pre-committed as an *existence* claim, which is unaffected by how many
> distinct questions surround it; the rate framing weakens the harder anyone looks,
> so quote the existence framing.
>
> **Corpus prerequisite before any further shape work.** The study currently
> discriminates shapes on **two** divergence patterns. Absent: sample-versus-
> population, wrong percentile, right estimator on the wrong column set, correct
> method with a wrong cutoff value. Any shape selected on this evidence is selected
> on its behaviour toward wrong-estimator substitution. Generate the new patterns
> **and fix each expected verdict from the text at generation time**, before
> observing any shape's performance on them.

> **Amendment 4, 2026-07-27: the comparator has no observable output, and every
> diagnosis in this document was inferred from verdict distributions alone.**
>
> `JudgmentVerdict` carries exactly one field, `stance`. There is no reasoning
> field, no stored raw completion, nothing beyond the enum — for any shape, at any
> point in this investigation. So "what did the comparator say and why" **does not
> exist and cannot be recovered**; it was never generated.
>
> This is why no mechanism for C's mis-affirmation was ever established. Not because
> the failure is mysterious: we built an instrument that cannot be introspected and
> then spent two days asking it to explain itself. Naming-credit, the polarity
> trade, difficulty, item-specificity and positional artefacts were all inferred
> from *rates*, which is why each survived only until someone recomputed a
> denominator.
>
> The flatness was deliberate — three separate fragilities were traced to nested
> schemas (`Resource` inside `AITaskOutput`, `RelationBatchResponse`) — so this is
> the **cost of a correct earlier decision**, not an oversight. But the cost was
> never priced.
>
> **Fix under test, in three steps, not switched on as plumbing.** (1) Add a flat
> `reasoning: str` beside `stance` — flat, since the traced fragilities were to
> nesting rather than to field count — and verify the parse-failure rate against the
> current shape on the same questions in the same session. (2) **A/B it**, because
> asking a model to state reasoning is a chain-of-thought intervention that may move
> verdict rates: if rates shift, the field is an *arm* and must be reported as one;
> if they do not, it is instrumentation and output shapes come free. (3) Only then
> the payload-shape run, with `sent_user_prompt`/`sent_system_prompt` persisted
> literally as `input_scope_v2` already does — `shape_c` and `nonmethod_family`
> store no prompts, so those payloads can be *regenerated* but not *evidenced*, and
> a regeneration presented as a record is what §7.4 died of.
>
> **Constructed-input rule, arising with the head-noun probe.** The inverted method
> line (`mean+2*SD … (robust 95th-percentile …)`) occurs in no artifact. Constructed
> inputs are legitimate for *mechanism* probes — the question is precisely what
> happens to text that does not exist — but their results may **never** be pooled
> with corpus-derived measurements, and they must be labelled constructed at the
> point of generation rather than in the writeup.
>
> **Payload determines the verdict — the cleanest instance in the corpus.** On the
> *compliant* sibling artifact, where the correct answer is unambiguously `supports`
> and literal prompts are stored: **A 10/10 `contradicts` (unanimously wrong), B
> 10/10 `supports` (unanimously right)**, (a) 8 supports / 2 neutral. The only
> difference is whether the artifact side is the method atom or the whole text.

**Three things that will not count as evidence:**

1. **A larger affirmation contrast is not confirmation.** The earlier +0.325 and
   its CI were computed on a partial and corrupted record set. If the recomputed
   figure is larger, the earlier one was mismeasured and the new one is the
   measurement — the increase itself says nothing.
2. **No comparison against a remembered cross-run baseline.** (a)'s own arm moved
   0.582 → 0.675 on identical questions between two runs on 2026-07-26. Scoring
   C against the earlier figure would have claimed ≈+0.418 where the within-run
   paired contrast gives +0.325, making **≈22% of the apparent effect the clock.**
   All contrasts are within-run and paired.
3. **Completeness is not correctness.** The first version of this table looked
   complete while silently containing 32 records that mixed draws across three
   questions under one truncated key. The count matching the plan is now asserted
   in code; a table that merely *looks* finished is not evidence that it is.

## 13. Preregistration amendments arising from this investigation

_PREREG.md is authoritative and unversioned; this is a dated summary kept in the
committed repo so the amendment sequence has a verifiable history. It records
what changed and why, not the amendment text. If the two ever disagree, PREREG
is correct and this is stale._

All amendments were made **before any confirmatory seed ran** and before any
Arm-3 outcome inspection, each prompted by a measured defect rather than an
outcome.

| § | date | what | status |
|---|---|---|---|
| 7.1 | 2026-07-25 | Failure classification: transport (retryable, bounded, byte-identical) vs semantic (invalidating, never re-rolled) vs unclassified (invalidating). Transport class defined by principle, not a closed list. | in force |
| 7.2 | 2026-07-25 | Acceptance gates are repeat-based: criteria stated over k repeats with tolerance and k recorded; a canary must fail loudly when the scorer cannot read the comparator; five-step re-clearance path before a pin may be proposed. | in force |
| 7.3 | 2026-07-25 | Cell order randomised across the matrix with the ordering seed recorded; wall-clock and serving-backend mix recorded per cell; drift reported as a diagnostic. Arm identity was perfectly confounded with execution position. | in force |
| 7.4 | 2026-07-25 | Emit profile packets on artifact-triggered scope activation. | **WITHDRAWN same day** |
| 7.5 | 2026-07-25 | Named uninformative prior for the designed stakeholder absence; both unguarded `_temporal_priors` accesses guarded; invariant asserted that no non-stakeholder pair carrying a relation may lack a prior. | replaces 7.4 |

**Why §7.4 was withdrawn**, recorded because "we amended and then pulled it back
the same day" means little without the reason. It was approved on my enumeration
of missing profile priors, which I computed from `arm3_state.json` inside
`outputs/smoke101_5b19b5b/` — state written by the builder at commit `5b19b5b`,
several versions superseded. Instrumenting the live builder showed the gap does
not exist: the control cell emits four profile packets for the scope in question
at t=2, and the unguarded population is stakeholder-only, one pair per cell,
which is the designed absence §7.5 covers. The confound argument that justified
§7.4 dissolved with it — under current code there are zero artifact-triggered
activations in any cell.

The failure is the one this document names as its primary engineering lesson,
one step further removed: a saved artefact is not production input. See §9.

## 14. Call-volume measurement

Exact, from the four Arm-3 smoke traces under current code:

| cell | today | one-question-per-call | ratio |
|---|---|---|---|
| control_arm3i_q | 24 | 77 | 3.21 |
| silent_arm3i_noq | 28 | 94 | 3.36 |
| silent_arm3i_q | 28 | 90 | 3.21 |
| silent_arm3t | 28 | 92 | 3.29 |
| **mean per cell (projected)** | **27.0** | **88.2** | **3.27** |

Measured on the shipped v3.0 comparator via `arm3_replay --plan-only`, at
`bfaac38`. **Two different quantities, and an earlier version of this table
reported one under the other's heading:**

| cell | calls planned | distinct judgments |
|---|---|---|
| control_arm3i_q | 81 | 81 |
| silent_arm3i_noq | 94 | 88 |
| silent_arm3i_q | 90 | 88 |
| silent_arm3t | 92 | 88 |
| **mean per cell** | **89.25** | **86.25** |

*Calls planned* is what `plan_replay` returns. *Distinct judgments* is what a
replay cache file contains, because repeated identical judgments across
timesteps collapse to one cache key. Both are real and they answer different
questions: **distinct judgments is the right base for per-judgment error
rates, calls is the right base for cost.** The previous table gave 81/88/88/88
under the heading "Exact" — those are the distinct-judgment counts labelled as
planned calls. Reported by a reviewer, reproduced, corrected here.

Under the projection because a requirement_artifact packet with no method claim
now issues no call — its stance is structurally determined, and the batched
extractor already enforced that as a hard shape check. Reported separately as
`structural_neutrals_no_call`, never folded into model-returned neutrals.

At 50 cells: ~1,350 today vs ~4,313. Reliability bought with call volume is the
researcher's explicit decision, not something to absorb quietly.
