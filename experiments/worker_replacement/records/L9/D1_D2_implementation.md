# D1 and D2 — implementation record

**Why this file exists rather than a commit message.** The D1/D2 code changes were
committed inside `f78ae94`, whose subject is "L9 addendum 2 (LS): sigma-invariance
holds with a scope condition; bracket the clone; tie check required" — an unrelated
message. The working tree was swept into a commit written by another agent while
these edits were mid-flight, so the code landed and its rationale did not. That is
the "which version produced this figure" failure the one-repo-one-branch rule exists
to prevent, arriving by a different door: not a hidden branch, but a commit message
that does not describe its own diff. **Recorded here because the diff is now
undiscoverable from the log.**

Process note for the team, not a complaint: with three agents committing to one
branch, `git add -A` picks up whatever anyone else has uncommitted. Neither agent
did anything wrong.

---

## D1 — the card is a REPLACEMENT description, not an addition to a true one

`finance_scorer.ceiling_vs_stale_card` now scores the successor THROUGHOUT as the
predecessor's card describes it, so the card's **OMISSION** costs as well as its
**LIE**.

The previous `believed_score` granted `1.0` on a class the card claimed and
otherwise **fell through to the TRUE score** — so wherever the card was silent
about a class the successor really covered, the manager was credited with knowing
it anyway.

**Why it survived:** under the current template the successor's silent class is
always incumbent-covered, so the omission is structurally harmless (0/30 seeds) and
the two models agree (30/30). It was invisible on the only population it was ever
validated against. It stops being invisible exactly where the L9 candidates put
value — a successor that SOLE-HOLDS a silent class.

**This function has now been wrong twice about which question it asks** — first the
BASELINE (it ranked selection against a random-blind manager when the study's
counterfactual is the stale card), now the BELIEF. Its docstring therefore states
both answers rather than one, and the acceptance tests a case where the candidates
must diverge.

### Acceptance — `check_card_belief_model.py`, both halves, fails on either

    control    (current template)   0/30 costly omissions,  30/30 models agree
    divergence (disjoint candidate) 30/30 costly,  0.37% -> 8.51%,  missed 8.13%

The superseded model is kept in the acceptance as a frozen copy (`lie_only_ceiling`)
because an acceptance that only ran the current implementation could not show the
divergence, and the divergence is the half the fix exists to produce.

### Two assertions requested by RR, both guarding this model's isolation

* **Calibration must be CLASS-LEVEL.** RR verified segment-by-segment that the two
  models differ ONLY where the card is silent (162 of 810 cells) and NEVER where it
  claims (0 of 810). That holds only because a carded successor holds the TRUE class
  table, so `s()` really is `1.0` on a claimed class and coincides with the old
  hardcoded `1.0`. Restore per-worker calibration and the lie starts granting
  attainment too — silently, and in the direction that **inflates** the
  belief-model effect. Now raises.
* **A ceiling is non-negative by construction.** Float noise (`-2e-17` on 4 of 30
  seeds) snaps to zero; anything below `-1e-9` raises, because at that size the
  believed allocation beat the true optimum and the enumeration is wrong. A
  negative share also violated the plausible-range rule.

---

## D2 — re-derive the admitted set, AND THE MOVE IS NOT D1'S

    admitted   34 -> 21
    chosen     [3, 23, 36] -> [7, 20, 30]

**D1 changes the ceiling on 0 of 34 admitted seeds.** That is what the control
predicted, and checking it is why the prediction was worth making: the re-derivation
looked at first like a large D1 effect and is not one.

The entire move is the earlier **IGNORANT → STALE CARD baseline fix**.
`records/R2/instance_selection.json` had never been regenerated after that fix
landed, so the selection record on disk described a rule nobody was running. Both
belief models agree on which 13 seeds are dead, so the exclusion is a baseline
property, not a belief property.

**This independently confirms the earlier diagnosis: seeds 23 and 36 — two of the
three instances the pilot actually ran — have a stale-card ceiling of exactly
zero.**

### Two record-hygiene fixes made in passing

* Written as `instance_selection_v2_wholecard.json`, **not over the old file**.
  Three episodes were already run against the old seeds; overwriting would leave
  those runs pointing at a record that no longer describes how their seeds were
  chosen.
* The payload's `"rule"` string still said `ceiling_vs_ignorant` while the code
  ranked on `ceiling_vs_stale_card` — documentation naming a source that did not
  produce the value, **inside the record of the fix for exactly that fault.**

### Caveat carried forward, unchanged in kind from the previous draw

The low pick is again the suite minimum (0.0051; chosen mean 0.0301 vs admitted mean
0.0214), so effect magnitudes sit below the suite's by construction, and it compounds
with the stratification's deliberate widening of `sigma_between`. Harmless for sigma,
not harmless for anything reading effect magnitudes.

### What D2 does NOT establish

It does not say the new three instances are good, only that they are alive under the
study's own counterfactual. No episode has been run against seeds 7, 20 or 30.
