# The override path is not the generator — audit of the six-class arm (RR)

RE found `_designate_swap_pair` re-deriving roles on the `coverage_override` path and
offered that my numbers were the more likely correct ones. **I checked my own code
before accepting that, and the conclusion is that neither of our samples should be
trusted — for a reason bigger than the role bug.**

---

## 1. My implementation does not carry the role defect — but not by design

My pricing read `predecessor_id` / `successor_id` **from the instance**, i.e. from
whatever `_designate_swap_pair` derived, while my carrier label was computed on
template **positions** (`w0` = predecessor, `w1` = successor). That is exactly RE's
defect, structurally. Checked on every surviving cell of my sample:

```
roles MATCH the declared positions : 14
roles DISAGREE                     :  0
```

**So my numbers are not invalidated by the role bug — but that is luck, not
correctness.** The derived rule happened to land on `w0`/`w1` for the templates that
survived. **RE should not defer to my figures on this basis**, and I would not have
noticed if it had gone the other way.

## 2. My reported `n=30` does not reproduce. It is 7 per group (**correction**)

```
group 1: attempted 30, succeeded 7
group 2: attempted 30, succeeded 7
```

**The H2 table and the four-rule tie-break table in `step4_audit_RR.md` rest on 7 cells
per group, not the 30 I printed.** I cannot reconstruct why the earlier run reported
30; what reproduces is 7. Every conclusion in that record that depends on sample size
is weaker than stated, and the ratio figures should be read as indicative only.

**What does not depend on it:** the tie-break sensitivity comparison is within-sample
(same templates, same seeds, four rules), and the zero best-case was observed on every
surviving cell. Those stand as directional findings on a small sample.

## 3. The generation failure is TOTALLY SELECTIVE by sole-held class (**blocker**)

RE flagged that the override path fails generation far more often and said they did not
yet know whether it biases. **It biases, completely.** 60 attempts:

```
sole-held class    survived   failed   survival
corporate                10       10       50%
retail                    4       16       20%
corporate_clone           0       10        0%
mdb                       0       10        0%

TOTAL 14 of 60 -- and the arm is priced ONLY on templates whose sole-held
class is `corporate` or `retail`.
```

All failures are `ASSERTION 7 (sole-class spread source): the sole-held class carries
no IRB-applicable segment`.

**This selects on exactly the property that carries the effect.** The sole-held class is
the interior-spread source — the whole reason the lattice is constructed. Two of the
four possible sole-held classes are excluded at **0%**, so the priced templates are a
23% survivor subset chosen by the mechanism under study. **Any group mean over that
subset is a mean over a filtered population, and the filter correlates with the
outcome.**

One consequence worth naming separately: **the clone class never survives as the
sole-held class.** So the clone's economics never enter through the interior-spread
channel at all, which means the `corporate`-vs-`mdb` clone-source bracket is not
bracketing what it was built to bracket.

## 4. The root cause: `coverage_override` was never a study path

Assertion 7's docstring says the generator **promotes** a segment to satisfy it and
that "the assertion guards the promotion". On the override path the promotion does not
happen, so the assertion simply fails. That is the same shape as the other three.

**Four generator mechanisms are inactive on `coverage_override`:**

1. `shared_class_segments` — the segment count forcing (`:433`);
2. the divergence selection that picks the shared class's ratings adversarially (`:449`);
3. IRB-approval priority for shared-class segments (RE's find);
4. the sole-class IRB promotion that assertion 7 guards.

And the path's own docstring says why:

> _"The three keyword-only arguments exist SOLELY to construct S5's negative cases — a
> generator whose assertions can never be made to fire has not been shown to assert
> anything. **They are never used by study instances.**"_

**Every six-class figure produced this phase was built on a code path documented as
never used by study instances.** `coverage_override` is a test fixture for making
assertions fire, and it is now carrying the template decision. The four missing
mechanisms are not oversights in it — they were never meant to be there, because it was
never meant to generate a study instance.

**That is the finding, and it subsumes the role bug, the amplifier asymmetry and the
survivorship filter: they are four symptoms of using a negative-case fixture as a
generator.**

## Recommendation

**Do not repair the override path incrementally.** Each fix so far has revealed
another mechanism that was silently absent, and the docstring says there is no reason
to expect the list to be complete. **A six-class lattice should be generated by the
generator** — `ASSET_CLASSES` extended and the template constructed the way
`_lattice_from_template` constructs the five-class one, so that every mechanism
applies by default and nothing has to be remembered.

Until then, no size-3 number decides anything, mine included.

## Labels

| finding | label |
|---|---|
| six-class figures built on a path documented as never used by study instances; four mechanisms inactive | **blocker** |
| generation failure totally selective by sole-held class (0% for two of four) | **blocker** |
| my reported `n=30` is actually 7 per group | **correction, mine** |
| my numbers escape the role defect by luck, not construction | **limitation, mine** |
| the clone never survives as sole-held class, so the source bracket does not bracket | **limitation** |
