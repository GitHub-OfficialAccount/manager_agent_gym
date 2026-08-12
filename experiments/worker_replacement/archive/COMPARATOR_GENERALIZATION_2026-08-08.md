# Belief-Layer Comparator Generalization — Design Contract

> **SUPERSEDED as of 2026-08-06** — this was a pending amendment to ARM3_SPEC.md, which is itself
> superseded by `STUDY1_FOUNDATION.md`; the promised reconciliation will not occur. Retained as
> record; do not cite for current design. Frozen copy:
> `manager_agent_gym/experiments/ds_reroute/archive/COMPARATOR_GENERALIZATION_2026-07-24.md`.

_Author: Lead Scientist · 2026-07-24 · supersedes the deterministic-family portion of ARM3_SPEC §4.2 (to be reconciled into ARM3_SPEC once validated)_

## Motivation

The seed-101 smoke analysis found two Tier-2 detection failures in the frozen
deterministic requirement↔artifact comparator, both invisible to the offline gates
(which replayed a trace whose artifacts happened to be clean plain-text confessions):

1. **Format miss (Bug 1):** an artifact emitted as a single-line JSON object is stored
   as one blob atom; the comparator only reads a standalone `method:` atom, so it returned
   `no_relation` and silently missed a genuine confession (`arm3i_q` Batch A: `e24`
   `{"method":"zscore (reference mean + 2*SD)"}` → missed; Batch C plain-text → caught).
2. **Mixed-claim false support (Bug 2):** an artifact stating a correct-sounding primary
   with the true degraded method in a parenthetical (`arm3t`: `robust 95th-percentile
   reference standard (mean+2*SD cutoff from reference population)`) is read as percentile
   by the primary-method-wins rule → rendered `+2.25 supported`, actively reinforcing the
   degraded worker.

**Decision (human researcher, 2026-07-24):** do not add more method-specific rules. The
belief layer must be **general and method-agnostic** — never a detector for a single
method pair — because (a) that is the actual research claim, and (b) only a general
comparator transfers to Lever A (model+prompt change), which has no method-name channel.

**Honest tension to hold:** the deterministic two-family ontology exists *because* the
earlier general LLM comparator (v2.0) was empirically unstable at temperature 0 (the
v2.0→v2.6 retreat). Generalizing reopens that stability problem. The lever for resolving
it is the **belief-layer model**, which is not constrained by information-preservation
(`z_t=f(o₁…oₜ;ξ)` only requires reading manager-visible text; the model computing `f` is
free). The model choice is **deferred to the human after these fixes**, and is expected to
be made empirically from a bake-off against the gates below.

## Scope

- **Replace:** the deterministic percentile/z-score family-ontology requirement↔artifact
  comparison in ARM3_SPEC §4.2.
- **Keep unchanged:** scope normalization, packet construction/batching/dedup, structural
  validation, the updater math, rendering, the information-preservation boundary, the
  Arm-2 ledger and byte-identical prefix, and the confirmatory matrix. No confirmatory
  seeds.

## Two sub-fixes

### A. Format-robust method extraction (deterministic, model-free, unit-tested)

Given the artifact evidence for a requirement↔artifact packet in **any** format — JSON
object (`{"method": "..."}`), plain lines (`method: ...`), or prose — deterministically
extract the artifact's stated method/approach text. Must cover the JSON-blob case (Bug 1).
Implement in the comparator's packet-input reading, **not** the ledger enumerator, to keep
the Arm-2 ledger and byte-identical prefix unchanged. This is general parsing, not a
method rule; unit-test it directly (JSON blob, plain lines, prose, no-method → extract or
cleanly report absent).

### B. General method-agnostic semantic judgment (model-based, model swappable)

Replace the family ontology with a semantic judgment over **text only** (ARM3_SPEC §2
permits requirement-text ↔ artifact-text): *is the artifact's stated method/approach
consistent with what the task requires?* Output `supports_fit` / `contradicts_fit` /
`neutral`. Requirements:

- **No hard-coded method families, no single-method rules, no primary-vs-parenthetical
  rule.** Works for any method/use case.
- **Internally inconsistent claims → not support.** A claim naming two different
  procedures (e.g. a percentile standard *and* a mean+2·SD cutoff) must not be credited as
  support; general reasoning should recognize the inconsistency (fixes Bug 2 without a
  method rule).
- **Ambiguous / insufficient → `neutral`, never false support.**
- Reads only manager-visible requirement + artifact text; no forbidden inputs.

## Model-agnostic implementation (the deferred decision)

- The belief-layer model is a **config parameter** (e.g. `belief_model`), distinct from
  the manager model, recorded in the extractor config tag / manifest for attribution.
  **Do not hard-wire a model.**
- Build and validate the **model-independent** parts now: sub-fix A (unit tests), the
  judgment prompt/schema, packet/batch/dedup/structural validation, updater, rendering.
- Defer the semantic-stability gate to model selection: set up the offline-gate harness so
  it runs with a **swappable** model, so once the human names candidate model(s) we run
  them against the gates and pick empirically.
- Temperature 0, cached by input fingerprint (preserve replay determinism). If a candidate
  model is unstable at temp-0 single-shot, n-sample self-consistency is a possible fallback
  **to flag and discuss** (it weakens strict determinism), not a default.

## Acceptance gates (unchanged bar, augmented traces)

Whatever the general comparator + chosen model, it must pass the existing offline gates on
the changed and competent-control seed-101 traces:

- preregistered diagnostic-contradiction recall = 100%
- false contradictions on competent no-change scopes = 0
- (plus the existing scope/clause/family coverage gates)

**Augment the gate traces** to include the two failure modes this smoke exposed:
- a **JSON-blob** artifact (from `smoke101_5b19b5b/…arm3i_q…` Batch A, `e24`);
- a **mixed / internally-inconsistent** method claim (from `…arm3t…`, all robust artifacts).
These must now be exercised, so a regression can't slip through as before.

## Validation & re-pin cycle (after model chosen)

1. Model-independent unit/structural tests green; ruff clean.
2. Human picks belief-layer model (bake-off on augmented gates).
3. Offline gates pass on changed + competent-control + augmented-variant traces.
4. Re-pin (new frozen commit supersedes `5b19b5b`).
5. Re-run the seed-101 smoke; re-do the detectability count **against the actual comparator
   verdict** (not raw-content regex — the raw count overstated true detection).
6. Only then reconsider the confirmatory go.

The pin is intentionally **open** during this redesign; `5b19b5b` is not the confirmatory
reference anymore. No confirmatory seeds until step 6.
