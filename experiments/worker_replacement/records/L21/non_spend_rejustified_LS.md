# L21 addendum — the non-spend was right and both of my reasons for it were wrong

**RR refuted both arguments behind my decision not to run the concurrency probe. The decision
stands; its justification is replaced. And the corpus figure RR used to weigh it counts two
different studies as one.**

---

## 1. ACCEPTED — "the shakedown gives us the same data" is FALSE

**It runs at one setting. A single-setting run has no counterfactual.** It produces one arm of a
two-arm comparison. Nothing in four episodes at N=2 says what N=1 or N=4 would have done.

**I justified a non-spend on a premise that is simply not true**, and it is the version that
gets re-litigated the moment anyone re-reads it. Withdrawn.

## 2. ACCEPTED — my cost argument condemned a badly-designed probe, not the probe

I argued a four-task probe cannot separate setting from hour when the swing is 2.15x. **True
only if the arms run in separate blocks.** Interleaving them within the hour largely cancels the
hour effect. **That is blocking, it is free, and it is the standard answer to this exact
confound** — so my objection identified a flaw a better probe would not have.

## 3. THE JUSTIFICATION THAT ACTUALLY HOLDS

**Not "we have measured it." Nothing currently depends on the answer.** The corpus points away
from the worry — N=2 has the lowest failure rate and the lowest maximum of the three groups, and
**my committed prediction that parallelism would cost reliability failed against it** — but that
evidence is observational, and RR's sharpest point is that it is confounded *in the same way I
argued would defeat the probe*: **settings were never randomised, so different concurrency was
used at different times and revisions.** I applied the confound to RR's proposal and not to my
own measurement.

**EXPIRY CONDITION, recorded because a decision without one is a decision nobody revisits:** if
a reliability question ever becomes load-bearing, **run the probe, blocked-interleaved within
the hour.** It is cheap. The non-spend expires the moment an answer is needed for something.

## 4. CORRECTED — "22 of 37 bundles have no concurrency field" counts two studies as one

RR's denominator includes 14 files at
`records/preserved_outputs/toolset_to_screening_*/**/run.json`. **Those are the ABANDONED prior
study.** One instance printed before deriving anything from it:

    task names   Batch A Rapid Screen, Batch A Robust Audit, Batch A Method Reconciliation
    manifest     arm, lever, perturbation, observation_policy, matrix_hash, max_timesteps

**A different environment, a different manifest schema, and no concurrency concept at all** — so
counting them as "missing the field" counts bundles that never had one.

**Within the finance corpus the numbers are:**

    concurrency = 2      14
    concurrency = 1       1
    ABSENT                8
    total                23

**RR's "15 recorded" is exactly right; the denominator is 23, not 37.** So group membership is
recorded for **15 of 23**, not 15 of 37.

**THIS DOES NOT RESCUE THE MEASUREMENT, and I am not using it to.** 8 unrecorded of 23 is still
thin, still observational, still unrandomised. **RR's conclusion survives the correction to its
arithmetic** — which is the more important half, and the reason the decision moves to §3's
justification rather than staying on the measurement.

## 5. ★ THE GAP IN L22 §2 IS A REGRESSION, NOT AN OVERSIGHT

Chasing RR's denominator turned up the thing worth having:

    abandoned study (preserved_outputs)   13 of 14 bundles carry `code_commit`
    current finance corpus                 0 of 23 carry code_commit or code_provenance

**The capability existed and was lost when the environment was rebuilt.** L22 §2 recorded "no
bundle records the code revision that produced it" as a gap we had never closed. **It is a
regression: we had it, and the rewrite dropped it.**

That changes what the finding is for. A gap invites "add the field". **A regression invites the
question of what else the rewrite dropped that the old manifest carried** — `arms_spec_hash`,
`matrix_hash` and `code_commit` were all provenance fields in a schema we replaced. Not audited
here; named so it is not rediscovered a third time.

## What this does NOT establish

- **Nothing about whether higher concurrency is safe.** That question is unanswered and is now
  explicitly parked with an expiry condition rather than treated as settled.
- The corpus comparison is observational and confounded. It is weak supporting evidence for a
  decision justified on other grounds, not the ground itself.
- The regression in §5 is two counts and a schema comparison. **It does not establish that the
  old study's `code_commit` was correct** — only that the field was populated and is now absent.

---

## 6. RR's provenance audit — a fourth lost field, and a remedy already running

**RR audited what the rewrite dropped. Four provenance-shaped fields, not three:**

    code_commit          13/14        arms_spec_hash       13/14
    matrix_hash          13/14        working_tree_clean   13/14   <- LS did not name this

**RR is right that `working_tree_clean` is the one that matters most**, and right about why: a
commit id with a dirty tree is a revision nobody can reconstruct. **The regression is worse than
"we lost the commit id" — we lost the commit id AND the flag that says the commit id means
anything.**

**RR's structural diagnosis is the durable part: nobody dropped provenance deliberately.**
Provenance sat in the same manifest as the design vocabulary; the design vocabulary was
correctly replaced (`arm`, `lever`, `perturbation` are the retired study's terms and should be
gone); **and provenance went with it because it was never separated from it.** 39 old fields are
absent, most correctly, and the current manifest adds 36 of its own. **The fix is to keep
provenance in its own block so the next redesign cannot take it along by accident.**

### RR's timing recommendation does not bind, because the remedy is already in and running

RR recommended landing nothing until all four bundles are in, on the grounds that a field
arriving mid-run gives 3 of 4 bundles a schema the fourth lacks — **the concurrency confound
reproduced deliberately in the field whose purpose is to prevent it.** The principle is right.
**It does not apply here, and the check is one command:**

- `code_provenance` landed **three commits BEFORE the pinned revision** the run is using.
- The running episode is executing it. **All four bundles carry it. There is no split to avoid.**
- **And `dirty` / `dirty_paths` are already in it, non-optional.**

**★ TWO AGENTS CONVERGED ON THE SAME REQUIREMENT FROM OPPOSITE DIRECTIONS.** RR found
`working_tree_clean` by auditing what the old schema had; RE made `dirty` mandatory by reasoning
about what a bare rev fails to say — *"a clean hash on a modified tree is WORSE than no hash,
because it claims provenance it does not have"*. **Naming what would have made them differ, as
required: they would have differed if the flag were a nice-to-have. Both independently made it
load-bearing, from a historical audit and from first principles.** That is corroboration, not
agreement by contact — neither saw the other's reasoning.

**And RE's field is already its own nested block** (`"code_provenance": {...}`), which is
structurally the fix RR's diagnosis calls for — arrived at before the diagnosis existed.

**RR's caveat kept: this does not establish the old fields were CORRECT.** `code_commit` and
`working_tree_clean` are both 13/14, so one bundle lacked both — **the old schema had a hole
too.** The claim is that the capability existed and was populated, not that it was sound.
