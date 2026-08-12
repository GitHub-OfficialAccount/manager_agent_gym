# Do workers depart from coverage-optimal play? — whether the coverage ceiling bounds all four cells

**LS's question.** An updated card conveys the complete coverage truth (240/240
verified), so no channel can convey MORE coverage information. But declaration and
trace also carry BEHAVIOUR — which method the worker actually chose — which a card
does not. That can exceed the coverage ceiling **only to the extent workers depart
from coverage-optimal play**, which had never been measured.

**Measured on the 18 committed scope bundles. No run.**

## Method choice: NO departures

Method is inferred from the reported figure rather than from the `method:` line,
because the declaration is only present in cells 2 and 4 — inferring from the value
makes the check independent of the channel being tested.

Population: IRB-approved segments, executed, whose assignee COVERS the class — the
only cases where a worker had a choice to make.

```
IRB-approved segments executed by a worker that covers the class : 82
   reported the IRB figure (coverage-optimal)                    : 42
   reported the SA figure  (DEPARTURE)                           :  0
   matched neither figure                                        : 40
(IRB-approved segments whose assignee did NOT cover: 10 — no choice available)
```

**Zero of 82.** No worker holding IRB coverage fell back to the standardised
figure. So a declaration saying "I used SA" is a near-constant on this corpus, and
**the behavioural signal about METHOD CHOICE carries nothing the card does not.**

## The 40 unmatched are execution error, not method choice

```
closer to the IRB figure : 20
closer to the SA figure  : 20
reported/IRB ratio: median 1.038, range 0.053–4.202
```

Scattered on both sides with a ratio spanning two orders of magnitude. That is the
signature of arithmetic error, not of a method decision. **A worker that attempted
IRB and got it wrong has still made the coverage-optimal choice.**

## CONCLUSION, and the caveat that survives it

**The coverage ceiling is TIGHT for method choice, so 1.24% of oracle / 0.16σ does
bound cells 1–4 on the construct the study manipulates.** "Drop the card cell and
rely on the other channels" is not available.

**BUT there is a second behavioural signal the card cannot carry, and it is not
bounded by this ceiling: EXECUTION QUALITY.** 40 of 82 covered IRB attempts land
off the exact figure. A trace showing a worker botching work it is approved for is
information about that worker's reliability — a different construct from coverage,
which the ceiling does not price because the scorer's `s(seg, w)` assumes faithful
execution.

**That is outside what the study currently manipulates or measures**, so it does
not rescue the current design. It is recorded because "the channels are bounded by
the coverage ceiling" is true of coverage and **not** true of everything a trace
could convey, and the distinction should not be lost if the design is revisited.

---

# Addendum — the tolerance, and the control that decides whether the check has power

**LS's correction, accepted in part.** My "42 used IRB, 0 used SA" came from a 2%
tolerance that I did not state. **That is §B on my own check: "reported the IRB
figure" is a population, and its tolerance is part of the predicate.** At exact
match nothing matches either figure, and the count is a function of the threshold:
22 / 39 / 42 / 51 at 0.1% / 1% / 2% / 5%.

**But the conclusion survives, because the check has a reference class I failed to
run — and it has power.**

SA is a table lookup: exposure × a published risk weight. IRB is the ASRF formula.
**So SA-only segments, where SA is the only option, tell us how exactly a worker
reproduces an SA figure when SA is what it is doing.**

```
tolerance | SA-only: matches SA | covered IRB: matches IRB | covered IRB: matches SA
    0.1%  |        41/41        |         22/82            |        0/82
    1%    |        41/41        |         39/82            |        1/82
    2%    |        41/41        |         42/82            |        1/82
    5%    |        41/41        |         51/82            |        2/82
```

**41 of 41, at one part in a thousand.** When a worker is doing SA, it reproduces
the SA figure exactly. **So if a covered worker had fallen back to SA, it would
have landed within 0.1% of the SA figure — and 0 of 82 do.**

**Deliberate SA fallback is therefore bounded at 0–2 of 82, not unmeasured.** The
test can detect SA use; it is demonstrated detecting it 41 times.

**On "19 of 82 are nearer SA": nearer is not AT.** Only 2 of those 19 come within
even 5% of the SA figure. Nearest-figure classification has no power here because
the IRB errors are large; tolerance-based classification anchored by a validated
reference class does.

**And the asymmetry is itself the evidence: the noise is IRB-SPECIFIC.** Workers
reproduce SA exactly and IRB loosely, which is what you would expect if they are
all attempting IRB and the formula is hard — not if some were quietly doing SA.

**LS's one-ceiling claim therefore stands** on this corpus: cells 1–4 share the
card's coverage ceiling, and "drop the card cell and rely on the other channels"
remains unavailable.

**What I got wrong stands too:** the tolerance was unstated, and I reported a
threshold-dependent count as though it were a fact about behaviour. The control
above is what I should have run before quoting either number — it is LS's own
corollary, *check that the computation could have come out otherwise*, and the
reference class is where that check lives.
