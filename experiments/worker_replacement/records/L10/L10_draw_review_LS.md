# L10 draw v2 — LS review

**Verdict: the draw is sound and I approve it. The RUN it feeds is not powered, and that must be
said before the spend rather than as a caveat on a null.**

## The draw reproduces

RE recomputed the pool from the generator rather than reading the record: **60/60 pool, 0 ceiling
mismatches, floor identical to 17 decimal places, per-class counts exact.** Both seeds pass all five
surviving properties; all seven controls fire, and control 6 now rejects on
`3_stale_card_ceiling_above_zero` — RE's rename showing up where it should.

**Nothing about the draw is in question.**

## ★ The gate prints a design band that describes no instance we ship

    gate.DESIGN_FACT   "the channel-effect ceiling lands in a band around 0.09-0.18 of the oracle"
    shipped pool       min 0.0017   median 0.0324   MAX 0.0712
    seeds in [0.09, 0.18]                                       0 of 60

**The band's FLOOR is 1.3x the best instance in the suite.** It was measured before the lattice moved
and before the cap went; it is off by roughly 2.5x. **This is the stale-figure shape of the whole
week, sitting in the text the gate prints on every report.**

## ★ And the consequence, which is why it is not cosmetic

    seed 42   ceiling 0.0497  =  0.25x the declared MDE of 0.20
    seed 30   ceiling 0.0712  =  0.36x
    pool max  0.0712          =  0.36x

**A PERFECT manager — one attaining the oracle — beats the stale-card baseline by 5% and 7% on these
instances, against a bar declared detectable at 20%. The entire available signal is a quarter to a
third of the threshold.**

**The gate's own failure criterion is written against the stale band:** *"If the measured sigma leaves
this band undetectable at any affordable n, the design fails honestly and is redesigned."* **The band
has moved down 2.5x since that sentence, so the criterion is calibrated to a design that no longer
exists.** Restating it is not this review's business, but it cannot be applied as written.

## What this run is, stated before it runs

**It measures this environment's variance and exercises the whole path — environment, swap, scoring,
split, report contract — on the designed instances for the first time. IT IS NOT POWERED TO DETECT
THE CHANNEL EFFECT.**

**A null from it cannot be read as "the card channel is worthless."** It can be read as *"at this n,
with this ceiling, nothing was distinguishable"* — which was computable in advance and is therefore
not news.

**This does not conflict with the researcher's standing pre-commitment** (*"if the effect turns out
undetectable at these settings, that is a FINDING and NOT a reason to widen anything"*). **That rules
on what to do when undetectability is MEASURED. It does not convert an underpowered pilot into
evidence of undetectability** — the pilot's job is to supply the sigma that makes the pre-commitment
applicable at all.

## Two properties of this draw, recorded now rather than discovered later

**It landed on the two THINNEST usable classes:** bank has 4 candidates above the floor and mdb has
3, against corporate's 12 and retail's 8. **Not a fault — the rule is class-first and the seed was
fixed before drawing — but the "which instance" step had almost no room in either**, and if a
property ever retires an mdb instance the class has 2 left.

**Admission admits 60 of 60 within `partial`.** With 2b retired no seed in the shipped arrangement is
rejected, **so the FLOOR does all the selecting and the admission pipeline contributes nothing to
this pool.** The gate still discriminates on ARRANGEMENT (`current` rejected 12/12), so it is not
vacuous — **but "60 of 60 admitted" must not be read as 60 instances clearing a quality bar. Within
`partial` there is no bar left to clear.**

## What this review does NOT establish

Nothing about whether the manager uses any channel. Nothing about effect size. **And nothing about
whether the design should be redesigned — that needs the measured sigma this run exists to produce,
and the criterion that would decide it is currently stale.**

---

# Amended after RR's review

**RR confirmed reading (a) and supplied the condition without which it is unsafe. Both are adopted.**

## ★ The companion condition — why "underpowered" is not an escape hatch here

**"It was underpowered" is available after ANY null.** If it can be invoked retrospectively the
pre-commitment is dead: every null becomes a power failure and nothing is ever a finding.

**What makes this reading sound is that the declaration is IN THE RECORD BEFORE THE BUNDLES EXIST.**
The band, the MDE, and the ratios (0.25x and 0.36x) were written in advance, above. **That is the
only thing separating a stated limitation from a retrospective excuse, and it has to be said in
those terms** — the next person reaching for "underpowered" will not have declared it first.

RR's ruling on their own pre-commitment: it was written against **responding to a MEASURED null by
widening the manipulation**, because widening reintroduces the confound the axis avoids. **A run at
0.25-0.36x the MDE cannot produce evidence either way, so its null is uninformative rather than
informative. The pre-commitment rules on what a null MEANS; it does not convert a guaranteed null
into a finding.**

## ★ So the run's purpose is renamed, before the bundles land

**This is a SHAKEDOWN, not a test of the channel question.** A run whose only possible outcome on the
headline question is "uninformative" is defensible as the first, and not as the second.

**What it is actually for, and what may be concluded from it:**

    harness behaviour on the designed instances    the whole path, first time
    `report_form` compliance                       the tightened contract is UNVERIFIED
    the timestep profile of any cell difference    RR's front-loading discriminator
    this environment's variance                    the input the MDE needs to be re-derived

**Nothing about whether the card channel works may be concluded from it in either direction.**

## The floor claim is withdrawn (RR)

**The floor selects RANK, not MAGNITUDE.** It is the pool median, so it would admit half of a pool of
all-zeros; **it cannot fail and cannot report that a pool is weak.** Against a random draw it is not
vacuous — it roughly doubles the expected ceiling — **but against the researcher's "both with a real
gap" it is unsound, because that is a magnitude claim.**

**And the proof is not academic: the floor was satisfied and the selected ceilings are a quarter and
a third of the MDE. It delivered "the better half of a pool that has none."** The admissible-vs-
representative distinction, one level up from where RR first raised it.

**Not replaced today** — the principled fix is an absolute floor from the MDE, which is not
computable until this run supplies the variance. **What changes now is that it stops being described
as ensuring a real gap.** Corrected in `environment_selection_v2.json`.

## And the randomisation does less than it reads as

The draw landed on the two **thinnest** usable classes — bank 4, mdb 3, against corporate 12 and
retail 8. **With 3-4 candidates the class choice nearly determines the instance**, so the second
stage contributed little. Class-first with a pre-recorded seed is what was specified; **this is a
property of the draw, recorded now rather than discovered later.**
