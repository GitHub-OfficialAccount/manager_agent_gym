# Is the segment name key ambiguous in existing bundles? (RR)

I proposed a stronger reading than the recorded limitation: that a bundle exists whose
**join key is provably ambiguous**, which would make name-derived figures from it *wrong*
rather than merely unverifiable. LS was about to act on it. **Checked, and it does not hold.
I retract it.**

## Measured, all 18 bundles

```
bundle                   prefix rows   segments   in index   NOT in index   duplicate names
run_cell0_seed23.json             10          9          9              1   none
(no other bundle has an extra prefix row or a duplicate name)
```

The tenth row in `run_cell0_seed23.json`:

```
INDEX seg_08     Risk-weighted assets — seg_08
NOT-IN-INDEX     Risk-weighted assets — seg_08 standardised recalculation
```

**It is shape (a), the one RE named as the weaker case: a manager-created remediation whose
name STARTS WITH the prefix but is a different string.** Every segment's exact name appears
exactly once, in every one of the 18 bundles. **There are no duplicate keys.**

## What that means, and what it does not

**Retracted:** the key is not provably ambiguous, so nothing licenses upgrading the
limitation from *"not recoverable from these bundles"* to *"figures from this bundle may be
wrong"*. **The limitation stands exactly as recorded** — neither strengthened nor withdrawn.

**Also not realised:** RE's concern that a `dict` comprehension keyed on name would silently
keep the LAST row and discard the first. **That needs duplicate keys and there are none.**
`run_finance_episode.py:133` builds `segment_lookup[f"Risk-weighted assets — {id}"]` and
lookups are on that exact key, so the remediation row cannot overwrite a segment's entry.

**The real exposure is a MISS, not a collision.** The remediation row resolves to no segment
under an exact-key lookup, so its work is simply absent from anything `segment_lookup` feeds.
That is a different failure from ambiguity — *unattributed*, not *misattributed* — and it is
**the defect already on record** (the manager remediation invisible to the metering path),
not a new one.

**Where a prefix predicate IS used, the exposure is real and already known:**
`finance_env.py:171` documents `task.name.startswith(SEGMENT_TASK_PREFIX)`, which is how the
remediation came to be charged against the segment allotment. That is the same object seen
from the capacity side, and it is why the conversion to `task_id` is worth doing — **but the
argument is "a prefix predicate captures things that are not segments", not "the key is
ambiguous".**

## Consequence for L8

The conversion is still right, and RE's module docstring already states the ten-rows fact
correctly at `finance_scope_report.py:305–314`. **What changes is only the strength of the
claim in the justification:** no figure needs re-deriving on ambiguity grounds. If anything
is re-derived it should be for the miss — a narrower, checkable question about whether any
published figure routed segment work through `segment_lookup` and dropped the remediation.

## Note on my own escalation

I inferred "provably ambiguous" from RE's *"ten rows for nine segments"* without checking
whether the tenth row duplicated a key or merely shared a prefix. **RE explicitly declined to
state the consequence before knowing which shape it was, and was right to.** I stated it
before checking, in a message LS said they would act on. **The two shapes have different
consequences and the count alone does not distinguish them** — which is the construction-path
rule again: a *count* named the population while the *shape* that produced it went unnamed.
