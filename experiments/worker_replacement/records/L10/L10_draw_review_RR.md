# L10 draw review — is the underpowered-pilot reading sound? (RR)

LS asked for the two things they could be wrong about, not the arithmetic (RE recomputed
the pool from the generator: 0 mismatches in 60, floor identical to 17 decimals).

**Verdict: (a) is a SOUND reading and needs one companion condition to stay sound.
(b) LS is right to be unsure — the floor selects RANK, not MAGNITUDE, and (a) is the
evidence that the difference matters.**

## (a) Does an underpowered pilot returning nothing trigger the pre-commitment?

**No — LS's reading is correct.** The pre-commitment was mine, and it was written against
a specific move: *responding to a MEASURED null by widening the manipulation*, because
widening reintroduces the confound the axis was chosen to avoid.

**A run whose ceiling is 0.25–0.36× the MDE is not a measured null. It is a run that
cannot produce evidence either way**, and a null from it is uninformative rather than
informative. **The pre-commitment rules on what a null MEANS; it does not convert a
guaranteed null into a finding.**

**THE COMPANION CONDITION, and without it the reading is unsafe.** *"It was
underpowered"* is available after any null, so if it can be invoked retrospectively the
pre-commitment is neutralised — every null becomes a power failure and nothing is ever a
finding. **The declaration has to be in the record BEFORE the bundles land, and it is:
LS wrote the band, the MDE and the 0.25×/0.36× ratios into the review in advance.**

**So both halves hold together:**
- **This run:** power declared insufficient in advance → a null is uninformative → the
  pre-commitment does not fire.
- **Any powered run:** a null is a finding and widening is still forbidden.

**One thing that follows and should be stated rather than left implicit: if the run cannot
answer the channel question, its purpose has to be named as something else** — harness
behaviour, report-form compliance, the timestep profile. **A run whose only possible
outcome is "uninformative" is defensible as a shakedown and not as a test**, and the
record should say which it is before the bundles are read.

## (b) Is the floor doing anything a random split would not?

**It does something, and not the thing its name suggests.**

**The floor is the pool median, so it is a RANK criterion, not a magnitude one.** It
guarantees the selected instance is in the top half of whatever pool exists — and it
would guarantee exactly that for a pool of all-zeros, where the median is zero and half
the pool clears it. **It cannot fail, and it cannot report that a pool is weak.**

Against a random draw from the whole pool it is not vacuous: it roughly doubles the
expected ceiling of the selection. **Against the researcher's constraint — "both with a
real gap" — it is unsound, because "a real gap" is a MAGNITUDE claim and a median floor
cannot make one.**

**And (a) is the proof that this is not academic.** The floor was satisfied, and the
selected ceilings are **0.25× and 0.36× the MDE**. **A criterion that admits instances at
a quarter of the detectability bar did not deliver "a real gap" — it delivered "the
better half of a pool that has none."** That is the admissible-vs-representative
distinction one level up: **passing the floor tells you an instance out-ranks its peers,
not that it clears anything.**

**What would fix it:** an ABSOLUTE floor derived from the MDE. LS previously listed that
as *"the principled one, and not computable — σ unknown, df=6 sizes nothing"*, which was
true then and is **still true**. So the honest position is not that the floor should be
replaced today but that **it should stop being described as ensuring a real gap**, since
it demonstrably does not.

## The thin-class observation

Bank 4 candidates above the floor, mdb 3, against corporate 12 and retail 8. **With 3–4
candidates the class choice nearly determines the instance**, so the "which instance"
step contributed little and the draw is closer to *pick the class, take what is there*
than the two-stage procedure it reads as. **Not a fault** — class-first with a
pre-recorded seed is what was specified — **but the randomisation is doing less work than
the description implies**, and that belongs beside the draw rather than in a thread.

## Labels

| finding | label |
|---|---|
| (a) the underpowered-pilot reading is sound, given the advance declaration | **confirmed** |
| the advance declaration is the load-bearing part; retrospective invocation would neutralise the pre-commitment | **condition** |
| the run's purpose must be named as something the ceiling permits | **recommendation** |
| (b) the floor selects rank, not magnitude, and cannot satisfy "a real gap" | **limitation** |
| the draw's second stage had 3–4 candidates; randomisation does little | **limitation** |
