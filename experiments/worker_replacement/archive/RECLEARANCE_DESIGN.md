# §7.2 re-clearance design — for review before any call is spent

> **STATUS 2026-07-27 — NOT AUTHORISED, NOT PURSUED, NO CALLS SPENT.** §7.2 re-clearance was explicitly
> excluded from the 2026-07-27 authorisation (`RISKS_AND_DIRECTIONS.md` §0), and the belief-layer path it
> serves is now retired — see the §10b gate referral in `CONSUMPTION_BOTTLENECK.md`. **Retained as a
> design record, not a plan.** Its §3 (what would falsify a pass) and §6 (multi-session requirement on
> every rate) are reusable if any LLM-judged instrument is ever re-cleared; nothing here should be read as
> scheduled work.

Status: **DRAFT FOR REVIEW.** Sent simultaneously to lead-scientist and
reviewer-reproducer. No calls until both reviews are in.

This measurement is intended to justify a pin. Today produced five design
defects in probes written by me, of which my own checks caught two; the rest
were caught by someone reading the design rather than the result. A pin is the
artefact nobody re-examines afterwards, so the design is reviewed first.

---

## 0. What must be stated before anything else

**We were failing `diagnostic_comparison_recall` worst.** The k=3 gate at
`a4ba33dab82b` / `bfaac382`:

| criterion (target 1.0) | s1 | s2 | s3 | |
|---|---|---|---|---|
| `diagnostic_contradiction_recall` | FAIL | PASS | PASS | 2/3 |
| `diagnostic_comparison_recall` | FAIL | FAIL | PASS | **1/3** |

§7 of this design proposes changing the definition of the criterion we failed
1-of-3. That ordering is deliberate: the failure is stated before the proposal,
because a reader who learns it from us can weigh the proposal, and a reader who
learns it elsewhere cannot.

**The six misses were artefacts, not accuracy** (diagnosed from session caches,
two cells faithful, one cache incomplete and reported separately):

- **type A** — correct `contradicts_fit` on the standard clause, destroyed by
  `arm3_relations.py:1728` (`contradicting and supporting -> neutral`)
- **type B** — correct contradiction landed on the *reporting* clause, so the
  excerpt-pattern match failed
- **type C** — two judgments never returned (`parse_validation`); no verdict

None is a wrong verdict on a diagnostic clause. Verdict accuracy across the gate
is consistent with 319/319.

**But "artefact" is wrong for type C, by our own preregistration.** PREREG §7.1
classes parse/validation as **semantic — invalidating, never re-rolled**. So 2 of
the 6 misses are cell-invalidating events, not artefacts. Measured across k=3:

| | |
|---|---|
| `parse_validation` failures | 7 |
| draws | 2,060 |
| per-draw rate | **0.34%** |
| draws per cell-repeat | 86 |
| **P(≥1 per cell-repeat)** | **25.3%** |
| observed cell-repeats with ≥1 | **5 of 24** (21%) |

At 50 cells that is a cell-survival question, not a footnote: roughly a quarter
of cells would carry at least one invalidating event. **Worse for PAIRED
analysis** — a pair needs both cells, so at independence
1 − (1 − 0.253)² = **44.2% of pairs are lost**. On n=5 seeds that is a power
problem, not a bookkeeping one.

**Independent of (a):** transport and model, not input path. This finding
neither helps nor hurts the change and survives whatever is decided about the
comparator.

**The proposed reclassification does not apply uniformly, and cannot yet be
evidenced.** The argument is that §7.1's own principle — does the failure carry
information about the object of measurement — makes a parse failure a *no
answer* rather than a *wrong answer*, and therefore retryable. Checked against
the allow-list at `arm3_relations.py:98`:

| type | no-answer or wrong-answer? |
|---|---|
| `JSONDecodeError` | **no answer** — nothing parsed |
| `IncompleteOutputException` | **no answer** — truncated |
| `ModeError` | **no answer** — configuration, not model output |
| `ValidationError`, `AsyncValidationError` | **WRONG ANSWER** — the response WAS parsed and then failed the schema, which is informative about compliance. This is the shape-invalid class that stays invalidating. |
| `InstructorRetryException` | **ambiguous** — a wrapper; its class depends on the cause it exhausted retries on |
| `PydanticSerializationError`, `PydanticUserError` | neither — these indicate a defect in our own schema or call, not model behaviour |

So the amendment must be **narrower** than "parse/validation is retryable".

**And we cannot say which fired in the k=3 sessions.** `gate_session.py` persists
`failures_by_class` and `generation_failures` but not the failure TYPE;
`extraction["failure_audit"]` carries it and is not written to the session file.
The distinction the amendment turns on is therefore **not recoverable from the
sessions we have**. Fix the recording first, then the amendment can be evidenced
rather than argued.

---

## 1. Population and unit

Every count names its unit (instances / distinct questions / draws / calls).

| set | unit | n |
|---|---|---|
| diagnostic targets | distinct questions | **8** |
| exonerating targets, current labels | distinct questions | **3** |
| exonerating-affirmation set (§5) | distinct questions | **15** |
| counterfactual arm (§4) | distinct questions | 8 |

Under (a) the corpus is **62** distinct (parent, method) questions, down from
141 (clause, method). Judgment *instances* are 185 today; that number is not
used here.

## 2. Arms, and the ground truth each is scored against

Never crossed. Scoring one arm by the other's truth marks correct answers as
failures — the error that nearly shipped in the family probe.

| arm | input | truth |
|---|---|---|
| `current` | split clause + extracted method | baseline only, carried in-run |
| `parent` | full `task_requirement` + same method | verdict must match the parent's named standard |
| `counterfactual` | parent + a **real matching** method | verdict must move off `contradicts_fit` |

`parent` truth is mechanical: percentile method under a percentile parent →
`supports_fit`; z-score method under a percentile parent → `contradicts_fit`;
the mixed claim → `contradicts_fit` (see DIAGNOSIS §3 on why cause-ambiguity
does not license fact-neutrality). The classifier raises rather than guessing on
an unclassifiable case.

**Baseline in the same run, at comparable depth.** Not convenience: if `parent`
comes in low, suppression must be distinguishable from an unlucky routing
period, and only a same-run baseline at comparable depth does that.

## 3. What would falsify a pass

Stated as falsification, not as what a pass looks like. The previous
pre-commitment in this investigation mapped a *shape* to a *cause* on no
evidence and was wrong.

**§3 is a MECHANISM check at modal level. It is NOT the criterion.** The gate
criterion operates per row at **n=1 across k=3** and lives in §9 step 4. A target
contradicting 8 of 10 has a correct modal verdict and would still fail a gate row
about one time in five. **So clearing §3 does not clear the bar**, and a reader
must not be able to take it as doing so. This is precisely the gap that produced
the gate failure: verdict accuracy was fine and rows missed anyway.

- any diagnostic target whose modal verdict under `parent` is not
  `contradicts_fit` → mechanism not cleared (weaker than the criterion)
- any counterfactual row that **contradicted under `parent`** and whose verdict
  does not move off `contradicts_fit` when the method is swapped for a matching
  one → the contradiction is not attributable to the method
- any mirror row (§4b) whose verdict does **not** become `contradicts_fit` when
  a mismatching method is swapped in → the verdict does not track match-status
- any of the **3 scored** exonerating questions contradicting under `parent` →
  false-contradiction bar breached. (The **15** constructed questions of §5 are
  reported alongside and do NOT substitute for the 3 — see §9 step 5.)
- any rate measured in one session and reported as a rate → see §6

**Precondition on the counterfactual.** It is interpretable only for rows that
contradicted under `parent`. A row that never contradicted has nothing to move
off, so its counterfactual is **moot, not failed** — the row's failure is already
recorded by the recall condition above, and scoring it twice would double-count
one defect as two.

## 4. The counterfactual arm

Replaces the clause-pattern match, which was a **proxy** for attribution — it
asked *where* the contradiction landed as a stand-in for *what it was about*.
The counterfactual tests attribution directly: swap the method for one matching
the parent's standard, hold everything else fixed, and see whether the verdict
tracks it.

**Substitutes are real strings from the corpus, same cell as their target**,
never authored. Recorded per row with character length, so a length effect is
visible rather than inferred:

| cell | substitute | chars |
|---|---|---|
| `silent_arm3i_noq` | "percentile (95th-percentile reference cutoff)" | 45 |
| `silent_arm3i_q` | "95th-percentile robust reference cutoff" | 39 |
| `silent_arm3t` | "95th-percentile reference cutoff" | 32 |

The bare `"percentile"` is excluded — measured per-judgment accuracy 0.49 and
0.38, both among the three modal failures, r=+0.365 on method-text length. It
occurs only in the control cell, which carries no diagnostic targets, so the
exclusion costs nothing. **The exclusion applies to substitute strings only**,
not to any other population.

Varying the substitute buys independence: eight rows flipping on different
strings cannot be an artefact of one unusually readable string. **But `noq` has
exactly one matching string, so its three targets share a substitute — six
distinct strings across eight rows, not eight.** A reader taking the
independence argument at face value would over-count.

Read the **flip**, not the destination. `neutral` establishes attribution as
well as `supports_fit` does; the destination is reported but not required.

**Draw count and decision rule, pre-committed** (a falsification criterion cannot
leave these to be chosen afterwards). Per row, per condition: **n=10**, both
conditions in the same interleaved run. "Moved off `contradicts_fit`" means the
**modal verdict** is not `contradicts_fit`; a tie is reported as a tie and
resolved as *not moved*, the conservative direction. Given a measured modal share
of 0.907 and one question observed at 12/20 against 16/60 hours apart, n=5 would
let a genuinely attributable row fail to flip by chance and an unattributable one
appear to flip.

**Run at k=3 sessions, spaced** (see §6). 3 × (8 + 11) × 2 conditions × n=10 ≈
1,140 calls against a ~2,100-call gate spend. Attribution is the sole carrier of
what the clause-match was proxying, so it gates; a non-gating single-session
check would silently demote it.

### 4b. The mirror (required)

An earlier draft declined the mirror on the grounds that a support not
attributable to the method is still not a false contradiction, so the bar is met
either way. **That reasoning is correct about the BAR and irrelevant to
ATTRIBUTION**, which is what the counterfactual exists to establish.

One direction cannot separate two hypotheses:

- the contradiction tracked the **mismatch** (what we want to show), or
- **any substitution** reduces contradictions (what would also produce a flip)

Real same-cell strings narrow the second without closing it: a real substitute
still differs in length, specificity and parenthetical structure, and the
mixed-claim result proves this comparator is sensitive to parenthetical structure
specifically.

So the reverse direction is required. On the **11 supports-expected questions**,
swap in a real **mismatching** method from the same cell and require a
contradiction to appear. **Attribution holds only if the verdict tracks
match-status in both directions, across several string pairs.** The counterfactual
is currently the sole carrier of the attribution the clause-match was proxying,
so it cannot rest on a one-directional test.

~110 calls (11 questions × n=10).

## 5. Exonerating-affirmation measurement (new)

The family probe found a failure mode outside every pre-registered branch:
expected `supports_fit`, got `neutral` — **under-affirmation**, in 4 of 15
questions, spanning all four cells. One of the four is a scored exonerating
question, because under (a) the tool-capability question and the scored
exonerating row become the same question.

This breaches neither zero-tolerance bar (neutral is not a contradiction; these
are not diagnostic) but it degrades `change_relevant_relation_recall` — which is
**NOT preregistered**. `grep` returns it zero times in `PREREG.md`; §3's
secondary list contains no affirmation metric. It exists in code only
(`arm3_replay.py:865`). **It is a cost of (a) and is reported as one.**

That absence sharpens §10b rather than weakening it: affirmation loss is not
visible through any preregistered metric, so the fifth-instance referral is not a
backstop behind an existing measurement — **it is the only thing that would
surface the problem at all.**

One instance of three is not a rate, and all three scored exonerating questions
live in one cell. So this measures **15** questions — the family set, whose
truth is mechanical — **in addition to** the 3 scored ones. Both are reported;
the 15 do not substitute for the 3 (§9 step 5).

## 6. Multi-session requirement on every rate

Three drift observations, largest a factor of 2.2 on one question between
sessions (12/20 vs a reviewer's 16/60). Three overlapping false-contradiction
measurements sit at 15.6%, 24.0%, 26.7%. **We have never measured a rate on this
instrument twice the same.**

So: any number reported as an *instrument property* requires k≥3 spaced
sessions. Numbers reported as *this session's observation* do not, and are
labelled as such.

Applying that honestly: **the counterfactual and mirror (§4, §4b) run at k=3 and
GATE.** An earlier draft made them single-session non-gating checks, which
composed with §7 to move attribution from a k=3 gate criterion to a
single-session non-gating one — a real weakening that the draft did not state as
one. At ~1% of the gate spend that was a false economy.

The affirmation set (§5) remains a **single-session mechanism check** and is
reported as "4 of 15 hedged, this session" rather than as an affirmation rate.
That is what I would drop rather than measure once and call a rate.

## 7. `diagnostic_comparison_recall` under (a): a granularity change

**The argument is structural and does not depend on the observed value.** It
would hold identically had we passed 3 of 3.

Under (a) one judgment covers several constraints, so its single verdict is
written to every covered constraint_id (`arm3_relations.py:1502`). Per-constraint
attribution is therefore *fiction*: the verdict is about the requirement, and
assigning it to a constraint is an artefact of our own copying. A bookkeeping
assertion cannot fix this — it would assert a property of the copy.

The criterion's **intent** is that the comparator's contradiction corresponds to
the labelled diagnostic opportunity. That intent survives; the granularity at
which it is checkable moves from clause to requirement. Because requirement-level
correspondence is weaker alone, the counterfactual carries the attribution the
clause-match was proxying.

**Two readings, for the reviewer to adjudicate:**

- *(lead-scientist)* a criterion surviving at a different granularity with a
  supplement — not a deletion
- *(reviewer-reproducer, as relayed)* the clause-match and the counterfactual
  answer **different questions**, which if right means the granularity framing
  understates the change and this is closer to replacement

I do not think I should adjudicate between these, having authored the
counterfactual.

**Preregistration change, for the researcher:** one of the two gate criteria
changes definition as a consequence of a change approved on other grounds. That
consequence should be attached to the approval, not discovered separately.

## 8. Withdrawn: the pattern-promiscuity finding

I reported that `95th.percentile` would match 52 constraints under (a) against
20 today. **Withdrawn.** I computed it by applying the patterns to parent text in
a scratch script; I did not trace the scorer. Tracing it: `:492` sets
`requirement_exact_excerpt` from `constraint.exact_excerpt`, and
`arm3_replay.py:607-616` matches patterns against that field, which is
clause-level and which §7.7 keeps clause-level.

The error class is worth naming because it is not simply being wrong: **the
number was correct for the question I actually asked and wrong for the one I
claimed to answer.** Second instance today.

What survives becomes an **assertion, not guidance** — guidance in a design
document decays, per §9:

> (a) widens the JUDGMENT's `requirement_clause`. It must NOT widen
> `constraint.exact_excerpt`. Asserted in code, failing loudly.

## 9. §7.2 step coverage

| step | satisfied by | status |
|---|---|---|
| 1 — frozen configuration | version bump moves the tag; probe headers carry the tag they were measured under | satisfied |
| 2 — per-judgment stability through the production path | re-run required on the post-(a) comparator; the repaired probe now calls `user_prompt()` | **satisfied only after re-run** |
| 3 — run-level exposure | content-keyed join recovered (237/249) | satisfied |
| 4 — criteria on the shipped comparator | k=3 sessions, post-(a) | satisfied by this design |
| 5 — false contradictions on competent no-change scopes | §5's 15 questions + the 3 scored | **NOT SATISFIED** — see below |

**Step 5 is not satisfied and I am not substituting something adjacent.** The
scored exonerating population is 3 questions in one cell. §5 measures 15 by
construction-derived truth, which is better, but it is not the preregistered
population and does not become it by being larger. A pin resting on step 5
should say the step is met on 3 labelled questions and supplemented by 15
constructed ones — or the researcher should expand the labelled exonerating set,
which is the only thing that would actually satisfy it.

## 10. Is (a) still the right change?

**My view: yes** — over-contradiction breaches a zero-tolerance bar;
under-affirmation degrades a secondary. But this is surfaced for the researcher
rather than assumed, and three things cut against it:

1. (a) is adopted on evidence from **twelve questions** (4 false-contradiction +
   8 diagnostic), plus 15 in the family probe. 130 questions remain unmeasured
   under either arm.
2. (a) introduces under-affirmation — the **fourth trade** today, and the same
   trade as the terse prompt: intact detection, degraded endorsement. Every
   mechanism we have found that reduces willingness to contradict also reduces
   willingness to affirm. We have not found one that moves only the errors.
3. **(a) creates the measurement artefact; it does not reveal one.** Under the
   current architecture per-constraint attribution was NOT fiction — each clause
   carried its own judgment and verdict, and the criterion was measurable.
   Adopting (a) gives up that measurability. Concretely: **type B — a correct
   contradiction landing on the reporting clause — becomes undetectable by
   construction**, because there is no longer a wrong clause for a verdict to
   land on. The comparator's behaviour is unchanged; our ability to observe it
   is removed. A criterion we failed 1-of-3, redefined so the observed failure
   mode can no longer be observed, is the most attackable thing in the pin.
   (Reviewer-reproducer's adjudication of §7; recorded here rather than in §7
   so the researcher weighs it against the benefit.)
4. **Near-circularity, said out loud:** (a) is being adopted partly on evidence
   from a criterion set that (a) itself alters. Not circular — contradiction
   recall and the false-contradiction bar are unaffected — but close enough that
   it should be stated rather than left to be noticed.

## 10b. Stopping rule for the trade (pre-committed)

§10.2 records the fourth instance of one pattern: every mechanism that reduces
the comparator's willingness to contradict also reduces its willingness to
affirm. With §7.6 permanently banning aggregation, **the input side is the only
remaining lever**. If the trade is structural rather than incidental, the
zero-tolerance false-contradiction bar may not be reachable by any input-side
change, and each further attempt buys one margin with the other indefinitely.

So, committed before the next attempt:

- **If (a) clears the false-contradiction bar and affirmation loss grows**, both
  are reported together. Affirmation loss is never traded away silently to clear
  a bar.
- **After a fifth instance of the trade** — a fifth mechanism moving both margins
  — the bar is referred back to the researcher as **possibly unachievable rather
  than unmet**, with the four-or-five instances as the evidence. We do not
  attempt a sixth first.
- **This is a preregistration question, not an engineering one.** It reaches the
  researcher with this design, not after the next trade.

## 10c. PREREG §7.9 — the paired symmetric bar

| half | target | observed, per-question modal | observed, per-draw |
|---|---|---|---|
| `contradicts_fit` on determinate mismatches | ≥ 0.80 | **4/4 = 1.000** | **80/80 = 1.000** |
| `supports_fit` on determinate matches | ≥ 0.80 | **7/11 = 0.636** | **32/55 = 0.582** |
| false contradictions, competent no-change | 0 | — | — |

**The affirmation half is unmet, and by more than the amendment states.** §7.9 was
written against "11/15 = 0.73". That figure is the count of questions answered
correctly across BOTH truths — 7 matches plus 4 mismatches — not the match rate.
The affirmation rate is **0.636 modal / 0.582 per draw**, against a 0.80 floor.

**The floor must name its unit** (units rule, §DIAGNOSIS). Per-question modal and
per-draw differ by 5 points here and production runs at **n=1**, so the per-draw
figure is the operative one. A floor stated without its unit would be assessed
at whichever reading the assessor reached for.

**Measured as a GATED criterion at k=3**, not a session observation. Stated
explicitly because this is the same composition error caught on attribution: a
criterion introduced in an amendment must not land in §6's non-gated bucket by
default.

### The floor's LEVEL is unevidenced and needs recalibration

0.80 was chosen against a cited 0.73 — a modest stretch. **The real figure is
0.582 per draw, so the actual gap is 0.218, not 0.07.** The cited number was
corrected; the threshold derived from it was not. The floor's *existence* is
right (a floor that currently passes is not a floor); its *level* is now a number
that looked reasonable beside a figure that was wrong.

This must reach the researcher explicitly: **he approved an absolute floor on a
0.07 gap, and the gap is 0.218.** Approving a floor you are 7 points under is a
tuning decision; approving one you are 22 points under is a decision about
whether the instrument can meet it at all. Different questions, and he was shown
the first.

**Derive the level from what the floor protects — and we do not currently know
what that is.** An earlier draft derived it from the exonerating cells:
under-affirmation means failing to record that a competent worker is fine, which
appeared to land on `control`, `fp_ctrl_q` and §3's false-positive analysis.
**That derivation is withdrawn.** Rerouting is triggered by contradictions, not
by absence of support, so fewer supports produce no additional false reroutes —
**under-affirmation FLATTERS `fp_ctrl_q` rather than harming it.** An endpoint
that improves as the instrument degrades cannot justify a floor protecting it.

**The endpoint inventory is: PRIMARY at risk but unquantifiable, everything else
checked and unharmed.** Not "nothing identified" — that was too strong, and it
invites dropping the floor rather than keeping a conservative one.

- **PRIMARY, at risk.** §3's primary behavioural endpoint is the post-evidence
  corrective-routing rate — the fraction of B/C robust audits routed to a
  **non-degraded** worker. Under-affirmation leaves the manager able to identify
  whom to route *from* and with no positive evidence about whom to route *to*.
  Routing to a non-degraded replacement is exactly the quantity at risk.
  **It cannot be quantified from here**, because realisation depends on whether
  the frozen policy uses positive evidence in replacement selection — which is
  behaviour under study. "Cannot be quantified without the behaviour we are
  measuring" is not "no harm identified".
- **False-positive endpoint, unharmed** — indeed flattered (above).
- **`first accepted relation` latency, unharmed.** Checked and the route is
  closed: `arm3_relations.py:1742-1744` accepts a relation on a `neutral` stance
  whenever the packet carries method evidence, so a support decaying to neutral
  still produces an accepted relation with a different stance. Verified
  independently rather than taken. Reported because a failed check is worth as
  much as a finding here.
- **Detection path, unharmed** — 8/8 and 4/4.

So the floor's justification is weaker than "it protects a measured outcome" and
stronger than "nothing is harmed". The accurate statement for the researcher is
that the only identified path runs to the PRIMARY endpoint and cannot be resolved
without the behaviour under study — which argues for a conservative floor rather
than for dropping one.

### Report the contrast alongside, every time

Absolute floor and in-run contrast answer different questions and both are
needed:

| | question | decides |
|---|---|---|
| absolute floor | is the instrument good enough to pin? | the pin |
| contrast vs in-run `current` | did **(a)** cause this? | what to do when the floor fails |

At 0.582 the absolute number alone cannot distinguish "(a) broke affirmation"
from "affirmation was always ~0.58 and (a) is neutral on it" — and those imply
opposite actions. If pre-(a) is 0.85, reverting is on the table; if it is 0.60,
reverting costs the false-contradiction gain and buys nothing. **A failing floor
with no contrast tells you that you failed, not what to do about it.**

Third use: this instrument's levels have moved 2.2× between sessions. If the
contrast is stable across k=3 while the absolute level swings, the floor reading
is noise-dominated and the contrast is the quantity to trust. The contrast is a
**diagnostic on the floor's own reliability**, not a softer substitute for it.

It costs nothing — §2 already carries `current` in-run at comparable depth.

## 10d. PREREG §7.8 — effect on cell survival cannot be computed

| | under §7.1 as written | under §7.8 |
|---|---|---|
| invalidating failures observed | 7 of 7 | **between 0 and 7** |
| P(≥1 per cell-repeat) | 25.3% | **0% to 25.3%** |
| pairs lost at independence | 44.2% | **0% to 44.2%** |

The range is not conservatism. `gate_session.py` records `failures_by_class` and
`generation_failures`, never the failure TYPE, and `extraction["failure_audit"]`
carries the type and is not persisted. So the split between no-answer types and
`ValidationError` — the split §7.8 turns on — is unrecoverable from k=3.

**Fix the recording, re-run, then state the effect.** Reporting a point estimate
here would be a fourth instance of a number correct for the question I could
answer and wrong for the one being asked.

**Recording fixed** — `gate_session.py` now persists `failure_audit` (the type)
alongside `failures_by_class`. The breakdown falls out of the next run as a
by-product; nothing waits on it.

**The clustering test is asymmetric and cannot license the permissive branch.**
Retrying a parse failure is a re-draw on a nondeterministic instrument, so
whether it biases the verdict depends on whether parse failure is independent of
judgment difficulty. Testing that by whether failures cluster on the same
judgments works in ONE direction only. Power, at ~12 expected failures over 62
questions (balls-in-bins, 50k trials):

| model | P(observe 0–1 questions with ≥2 failures) |
|---|---|
| independent of difficulty | **76.1%** |
| strongly concentrated (20% carry 80%) | **13.9%** |

Observing 2+ collisions is informative — 5× likelier under concentration.
Observing 0–1 is the **modal outcome under both**, so scatter bounds nothing. It
is DIAGNOSIS §4's "0 errors in 96 calls does not establish a safe rate", and the
same shape as the empty join and the null truth column: a result that reads as
reassurance because the check could not have produced anything else.

  clustering detected      → evidence the retry is selective → do not retry
  clustering NOT detected  → **not** evidence the retry is safe → conservative
                             default stands

**So §7.8 is not decided on this run's data.** Adopt the narrowing to the three
no-answer types, keep them invalidating, persist the type breakdown, revisit only
if the rate turns out materially above 0.34%. The deferral is free because **the
measurement becomes feasible exactly when it becomes necessary**: if failures
stay rare, cell loss is tolerable and the retry is not needed; if they become
common, cell loss hurts *and* there are enough events for the test to have power.

If a signal from this run is wanted anyway: test the **covariate**, not the
collisions — ask whether failures land preferentially on low-modal-share
judgments, using per-judgment modal share from the step-2 re-run. A rank
correlation uses all ~12 events rather than only repeat-hits. Still weak, but it
fails less silently. A diagnostic, never a clearance.

**And the amendment may be unnecessary.** DIAGNOSIS §5 traced null content under
non-strict `json_schema` to nested `$defs` in `RelationBatchResponse`. Checked
the current schema: `JudgmentVerdict` is **flat — no `$defs`, zero `$ref`,
one enum field**, deliberately so after that finding. So the shipped schema does
not carry the known fragility, and the 7 failures are more likely truncation or
transport-adjacent than schema-shape. Driving the rate down at the schema is not
available here; the type breakdown is what will say what is.

## 11. Cost

| part | calls |
|---|---|
| k=3 gate sessions, post-(a) | ~3 × 700 |
| counterfactual arm, 8 rows | ~80 |
| exonerating-affirmation, 15 questions | ~150 |
| mirror arm, 11 questions | ~110 |
| §7.2 step 2 re-run | ~250 |
| §7.9 affirmation half, gated at k=3 | ~450 |

Sessions spaced ≥2h and spread across periods, not clustered.

---

## Revision history

**r2** — three findings from lead-scientist's review, all accepted:

1. **The mirror was missing.** §4b added. This was a **coordination failure, not
   a design defect**: lead-scientist reversed their own no-mirror position after
   reviewer-reproducer's attribution-validity argument, sent the reversal to the
   reviewer, and never to me. The draft documented their superseded position
   faithfully. Same class as the defects in this investigation's tally — an
   instruction existing in one place and not where it was needed — committed in
   the coordination layer rather than in code.
2. **§3's mechanism check split from the criterion.** Modal-level clearance is
   weaker than per-row-at-n=1 across k=3, and the document did not say so.
3. **The counterfactual's precondition stated.** Vacuous on rows that never
   contradicted; those are moot rather than failed.

**r3** — reviewer-reproducer's review at `31754d4`, all six items accepted:

- *blocking 1* (mirror missing) was already fixed in r2 from lead-scientist's
  parallel review; both reviewers found it independently. Root cause was a
  coordination failure, not a design defect.
- *blocking 2* — the counterfactual now runs at k=3 and **gates**. Composing the
  old §6 and §7 silently demoted attribution from a k=3 gate criterion to a
  single-session non-gating check, at a saving of ~1% of the gate spend.
- *blocking 3* — n=10 per row per condition and "modal verdict" as the decision
  rule, pre-committed; ties resolve as *not moved*.
- *material 4* — §3's exonerating criterion now names the 3 scored questions.
- *material 5* — type C reclassified: `parse_validation` is semantic and
  invalidating under §7.1, 0.34% per draw, **P(≥1 per cell-repeat) = 25.3%**,
  observed 5 of 24. A cell-survival question for the 50-cell spend.
- *material 6* — stopping rule for the trade, §10b.
- *§7 adjudication* — "closer to replacement", and the cost moved to §10 as the
  fourth argument against (a), which the reviewer judges the largest.
- *§5* — "rather than" → "in addition to".

**r4** — two items, neither blocking:

- *reviewer-reproducer*: `change_relevant_relation_recall` is **not**
  preregistered; §5 called it a preregistered secondary. Third instance today of
  **correct about the code, wrong about the preregistration** — named rather than
  quietly corrected, per the error-class discipline. Consequence for §10b
  recorded: the referral is the only route by which affirmation loss surfaces.
- *lead-scientist*: paired-loss figure added (44.2%), and the proposed
  no-answer/wrong-answer reclassification checked against the allow-list — it
  does **not** apply uniformly (`ValidationError` is a parsed-then-rejected
  response and stays invalidating), and which types fired in k=3 is **not
  recoverable**, because the session file records the class and not the type.

**r5** — PREREG §7.8 and §7.9 landed; two corrections to their stated basis:

- **§7.9's affirmation figure is wrong in the amendment.** "11/15 = 0.73" counts
  questions correct across BOTH truths (7 matches + 4 mismatches). The
  affirmation rate is **7/11 = 0.636 modal, 32/55 = 0.582 per draw**. The half is
  unmet by more than stated, and the floor needs its **unit** named — production
  is n=1, so per-draw is operative.
- **§7.8's effect on cell survival cannot be computed** from k=3: the failure
  TYPE was never persisted, so the no-answer / `ValidationError` split is
  unrecoverable. Bounds given (0–25.3% per cell, 0–44.2% of pairs) rather than a
  point estimate.
- §7.9's affirmation half is **gated at k=3**, stated explicitly so a new
  criterion does not inherit §6's non-gated default.

**r6** — reviewer-reproducer, all accepted:

- **The floor's level inherits the defect of the figure it was calibrated
  against.** 0.80 was set beside a cited 0.73 that pooled two populations; the
  real gap is 0.218, not 0.07. The researcher approved on the smaller number and
  must see the larger one. Level to be derived from what the exonerating cells
  need, not from proximity to an observed rate.
- **Contrast reported alongside the absolute floor, every time**, with three
  reasons: it decides what to do when the floor fails, it separates "(a) caused
  this" from "this was always so", and it diagnoses whether the floor reading is
  noise-dominated. Free — the baseline is already carried.
- **Recording fixed**: `gate_session.py` now persists `failure_audit`, so §7.8's
  type split becomes evidenced by-product rather than argument.
- **Schema checked**: `JudgmentVerdict` is flat, no `$defs`, zero `$ref`. The
  known nested-schema fragility is not present, so lowering the failure rate at
  the schema is not available and the type breakdown is what will say what is.
- `ValidationError` / `AsyncValidationError` should **raise** rather than be
  counted: they indicate a defect in our own schema or call, and a silent count
  lets our defect masquerade as instrument noise.

**r7** — reviewer-reproducer:

- **My clustering test's null branch was unsafe.** Scatter is the modal outcome
  under both hypotheses (76.1% vs 13.9%), so "if they scatter, the concern is
  bounded" bounds nothing. Disposition is asymmetric: clustering can forbid the
  retry, its absence cannot permit it — which is §7.1's own rule that absence of
  a mapping never grants permissiveness.
- **§7.8 deferred, not decided.** The narrowing to three no-answer types stands
  and they stay invalidating. Free deferral: the measurement becomes feasible
  exactly when it becomes necessary.
- **The exonerating derivation for the affirmation floor is WITHDRAWN**
  (lead-scientist's correction, relayed by the reviewer): under-affirmation
  flatters `fp_ctrl_q` rather than harming it, since rerouting is triggered by
  contradictions and not by absence of support. No preregistered endpoint has yet
  been identified that under-affirmation harms. Recorded as a weaker
  justification rather than replaced with a substitute endpoint.
