# ★★ RETRACTED: "STRUCTURALLY INERT" IS FALSE. The corrected claim is about SENSITIVITY, not capability — and it changes the direction from dead to repairable.

_Refuted by RR (`records/L4/DIRECTIONS_review_RR.md`, `a15a266`), verified by LS. **My ACTION —
do not run L3 as scoped — survives. My REASON does not, and the difference is the whole
thing.**_

**WHAT I GOT WRONG.** I tested whether knowing the truth improves coverage ON THE LIED-ABOUT
SEGMENT. The question is whether it improves THE ALLOCATION. RR ran the counterfactual I did not:
`V_true` (capacitated optimum under the successor's real coverage) against `V_card` (the
allocation a capacitated optimiser picks BELIEVING the successor is the predecessor, then scored
under the truth). **34 of 60 instances score WORSE under the card belief** — mean loss 0.0124 of
that instance's own oracle, max 0.0682. **That is the exact negation of my central sentence.**

**THE MECHANISM IS CAPACITY — the objection I ranked first, and I verified it:**

```
successor SOLE-covers 4 IRB segments   60/60 instances   (cap = 3)
uncoverable IRB segments                1  60/60 instances
```

The successor is the ONLY holder of a class with four IRB segments and can take three, so **even
a perfectly-informed manager drops one.** The lie adds the uncoverable class to the successor's
apparent scope, so a card-believing manager **spends one of three scarce slots on work nobody can
do, displacing a second sole-covered segment onto a non-coverer.** My coverage analysis was
correct and stopped one step short of the consequence.

**MY 60/60 COULD NOT HAVE FAILED.** `_lattice_from_template` is a FIXED TEMPLATE with
seed-permuted labels — `w0={A,E}`, `w1={A,B}`, `w2={B,C}`, `w3={C,D}` — so LOST=`{E}` and
GAINED=`{B}` hold for every seed BY CONSTRUCTION. Seeds permute which asset class plays which
role; they cannot vary the relationship. **The 60/60 is a restatement of the template**, and both
properties are listed in its docstring as designed guarantees. Third application of our own
confirming-test rule to me, and the one I asked RR to make.

**RR'S INVERSION, which is the opposite of the forced-to-successor case:** my STRUCTURAL argument
was *stronger* than my empirical framing — it holds for all seeds, not 60 — while the EVIDENCE
was uninformative. **The conclusion was more robust than I claimed and still wrong, for an
independent reason.**

## THE CORRECTED CLAIM

Against the measured pre-L1 σ = 0.0768:

```
0.0124 of oracle = 0.16 σ   ->  n ≈ 605 / arm for 80% power
0.0218 (non-zero only)      ->  n ≈ 194 / arm
```

- **"The channel CANNOT matter"** — a claim about the construct. **FALSE.**
- **"The channel matters by ~1.2% of oracle, which THIS DESIGN CANNOT DETECT at feasible n"** —
  a claim about the instrument's sensitivity. **TRUE, and it is what the researcher receives.**

**The first retires the direction; the second identifies a REPAIRABLE instrument.**

## AND IT IS REPAIRABLE AT THE LATTICE

The smallness is a DESIGN CHOICE, not a property of the question. The lattice deliberately makes
the lost class uncoverable so its IRB segments cap the score below perfect and the spread is
interior by construction — **and that choice is exactly what strips the lie of its coverage cost,
leaving only the second-order capacity cost RR measured.** RR's repair: **make the lost class
covered by EXACTLY ONE INCUMBENT.** Then misrouting it to the successor costs coverage AND
capacity, and the effect should move by an order of magnitude. **A lattice change, not a study
redesign** — which is D1 below, now with a specific form and a measured reason.

**ON RUNNING L3 ANYWAY AS A CHECK — RR's reason is better than mine and I withdraw mine.** An
episode run is a WORSE test of this than the offline counterfactual, because episodes confound
the manager's competence with the channel's information content while the counterfactual isolates
the information content by construction. It is done, it cost nothing, and it settles the question
at 60 seeds rather than 18 episodes. **And no run at feasible n resolves 0.16σ.**

**LIMITATION on RR's number, theirs and stated:** `V_card` is an OPTIMISER holding a wrong belief,
so 0.0124 is the value of correcting that belief **with allocation skill held at the optimum** —
the right quantity for a ceiling argument, not a bound on realised behaviour. A real manager could
lose more, or less if it never exploited the truth anyway.

---

# SUPERSEDED BELOW — the original document, retained per the no-overwrite convention

# THE CARD CHANNEL IS STRUCTURALLY INERT — and the directions that follow

_LS, 2026-08-08. Generator-only analysis, 60 seeds, zero run spend. This is a DESIGN finding, not
a measured null: it says the manipulation CANNOT move the primary DV, not that we failed to
detect it moving._

## The finding

A stale card has exactly two kinds of content: it **LIES** about a class the predecessor covered
and the successor does not, and it is **SILENT** about a class the successor gained. **Both are
inert in this design, across all 60 generator seeds tested.**

```
LOST class (the card's lie)     == the SOLE-HELD class, which NOBODY covers post-swap   60/60
GAINED class (the card's silence) is ALSO covered by an incumbent                        60/60
IRB segments where not knowing about the successor costs anything                        0/60
```

**Why each half is inert:**

- **The lie costs nothing** because the class it misleads about is the one no remaining worker
  covers. A manager fooled into sending that work to the successor has not chosen worse — every
  destination is equally wrong, so there is no better allocation the truth would have produced.
- **The silence costs nothing** because the class the successor gained is always covered by an
  incumbent as well. A manager ignorant of the successor's new capability routes that work to the
  incumbent, which is equally correct.

**There is therefore NO segment, in any instance the generator produces, where knowing the
successor's true coverage yields a better assignment than believing the stale card.**

## What this explains

Every anomaly of the phase falls out of it. **Mis-routing is 3 in 102** despite a stale card.
**Zero of 51 coverage-relevant assignments made TO THE SUCCESSOR were wrong.** The channels look
orthogonal to the dominant loss term. **The channels are not weak — they are inert by
construction**, and no number of episodes would have changed that.

**It also generalises beyond the card.** Declaration, ask and trace all carry the same content:
what the successor can do. If knowing the successor's true coverage cannot improve any
assignment, then **no channel carrying coverage information can move the primary DV**, whatever
its fidelity. The four channels differ in RELIABILITY, not in what they are about.

## What it does NOT establish

That the channels are useless in general — this is a property of THIS generator's coverage
lattice. That the manager reads or ignores the card — inertness is about consequence, not
consumption. And nothing about capacity, which remains the dominant loss and is a separate
matter.

---

# DIRECTIONS

Each states what it would establish, the cheapest test, and cost. **Unranked within tiers.**

## Tier 1 — the minimal repairs that make the manipulation manipulate

**D1. Break `LOST == SOLE-HELD`.** Draw the successor so the class it LACKS is one an incumbent
still covers, and keep the sole-held class separate. Then a manager fooled by the stale card
sends work to a worker who cannot do it *while a worker who can is free* — the lie acquires a
cost, and the cost is exactly the channel effect.
_Establishes: whether a coverage channel moves allocation once its content is consequential.
Cheapest test: generator change + regenerate the 3 instances + re-run the 6 cells at 2–3 seeds.
Cost: ~0.5d build, one scope-sized run._

**D2. Make the successor's gained class SUCCESSOR-ONLY.** The mirror repair: the card's SILENCE
acquires a cost, because work only the successor can do is routed to an incumbent that cannot.
_Establishes: whether the channels move allocation via omission rather than misinformation —
a different failure mode from D1 and separable from it. Same cost; combinable with D1 in one
regeneration._

## Tier 2 — move the manipulation to where the loss actually lives

**D3. Manipulate THROUGHPUT rather than coverage.** The successor differs in how MUCH it can do,
not what. Capacity is the dominant loss term and the channels would then carry information about
the binding constraint.
_Establishes: whether channels move allocation when their content concerns the constraint that
binds. Cost: perturbation redesign, ~2–3d — the riskiest item, and it changes what the paper is
about._

**D4. Add slack so coverage and capacity stop competing.** C=3 × 3 workers = 9 segments binds
exactly; coverage-optimal play therefore violates the cap by construction. With slack the two
stop fighting.
_Establishes: whether the orthogonality is a property of the REGIME or of the channels — and the
brief now carries "in a regime where capacity binds exactly" as a scope condition precisely
because we cannot currently tell. Cost: config change + one run. Cheapest decisive test in this
document._

## Tier 3 — study what we actually found

**D5. Silent defeat of manager adaptation.** The manager created a remediation task and the
environment refused it permanently without saying so; it bounced a task between two exhausted
workers because it could not see load. **This is a finding about orchestration harnesses that
holds independently of the newcomer question**, and we have the instrument for it already.
_Establishes: whether managers detect and recover from actions that do not take effect.
Cost: near zero — L1 built the instrument; this is a re-framing of runs we would do anyway._

**D6. Forced-move destination as the primary margin.** 73% of moves are FORCED by the departure,
and they go 22/24 to the successor. That is where the decision volume actually is, and
`forced_to_successor_uncovered` already exists to discriminate it.
_Establishes: whether channel information changes WHERE inherited work goes — the largest
behavioural margin in the design. Cost: analysis only, on runs already planned._

---

## My recommendation

**D1+D2 together, then D4.** D1+D2 are one regeneration and they repair the design's central
manipulation rather than working around it — without them, every cell contrast is measuring a
channel that cannot matter. **D4 is the cheapest decisive test we have** and it settles whether
the surviving claim is about the regime or about coverage as such, which is currently an
explicit scope condition on the brief's central claim.

**D5 is the one I would protect regardless of what happens to the rest.** It is a real finding,
independently publishable, and it does not depend on the manipulation working.

**What I would NOT do: run L3 as currently scoped before D1.** It would measure channel contrasts
across cells whose channels cannot move the DV, and the result would be a null we already know
the reason for.

---

# ★★★ SYNTHESIS — RE's SELECTION FINDING + RR's CEILING, AND NEITHER FIX ALONE IS SUFFICIENT

_LS, computed from `records/L4/card_ceiling.json`. Generator-only, zero run spend._

**RE found what neither RR nor I did: the inertness claim is FALSE of the generator and TRUE of
the SELECTED SET.** Two of the three instances the study actually runs on have a card ceiling of
**exactly zero**:

```
seed  3: 2.15% of oracle      seed 23: 0.00%      seed 36: 0.00%
```

So L3 as scoped would have run two-thirds of its card contrast on instances where the card
**provably cannot move the DV**. That is a SELECTION property, and it explains 3-in-102 and
0-of-51 more precisely than either my inertness claim or RR's generator-wide ceiling.

**BUT SELECTION ALONE DOES NOT REACH DETECTABILITY.** Converting RE's 30-seed sweep against the
measured pre-L1 σ = 0.0768:

```
                            ceiling      effect     n/arm @80%
mean over ALL 30 seeds       0.85%       0.11 σ       ~1320
admit only NON-ZERO          1.69%       0.22 σ        ~330
best single instance         3.58%       0.47 σ         ~74
current study set            0.72%       0.09 σ       ~2000
```

**Admitting only non-zero instances moves the ceiling from 0.11σ to 0.22σ — still ~330
episodes/arm. And these are CEILINGS under optimal play; a real manager realises some fraction
of one.**

## The conclusion, and it is the definitive one

**Both repairs are needed and they do different jobs.**

- **RE's selection rule is NECESSARY** — without it we spend a run measuring a provable zero on
  two of three instances. **It is not sufficient**: it buys 0.11σ → 0.22σ.
- **RR's lattice change is what reaches detectability** — making the lost class covered by
  exactly one incumbent gives the lie a COVERAGE cost on top of the capacity displacement RE
  measured, which is the order-of-magnitude move.

**Sequence: lattice change → recompute the ceiling offline → apply the selection rule to the NEW
generator → only then decide whether a run is affordable.** The ceiling computation costs nothing
and is now the gate. **We did an entire phase without it.**

## ★ DISCREPANCY RECONCILED — it was the SEED SET, not the method, and MY TABLE ABOVE USED THE WRONG NUMBER

RE re-ran their own method across both ranges and reproduced RR's figures **to the digit**:

```
RE method, seeds 0-29   nonzero 15/30   mean 0.85%   <- the subsample I tabulated
RE method, seeds 0-59   nonzero 34/60   mean 1.24%   <- RR's numbers exactly
RE method, seeds 30-59  nonzero 19/30   mean 1.63%
```

**The two computations never disagreed. RE reported a SUBSAMPLE labelled as the quantity** — and
the second half of the range is systematically higher, so it was biased LOW, not merely smaller.
Same shape as the requested-versus-applied rename count, and the shape §B exists for.

**CORRECTED EFFECT SIZES — my table above is superseded by these:**

```
                            ceiling      effect     n/arm @80%
mean over all 60 seeds       1.24%       0.16 σ        ~616
admit only NON-ZERO (34/60)  2.19%       0.29 σ        ~197
```

**The conclusion is unchanged: selection is NECESSARY and NOT SUFFICIENT.** It buys 0.16σ → 0.29σ
and ~197 episodes/arm, which we cannot afford. Only the lattice change is the order-of-magnitude
move.

## Superseded discrepancy note

RE's sweep (30 seeds, exact DP enumeration) gives a mean ceiling of **0.85% of oracle**; RR's
(60 seeds) gives **1.24%**. Same quantity, two independent computations, different answers. Both
point the same way and neither changes the conclusion, **but two people computing one quantity
and getting different numbers is the exact class this project keeps catching**, and it should be
reconciled before either figure is published.

## What none of this establishes

**That any manager realises any of the ceiling.** Every number above is optimal-play-under-truth
minus optimal-play-under-the-card. The design question and the power question are separate; this
answers the first and bounds the second. **A realised effect is necessarily smaller.**

---

# ★★ ONE CEILING BOUNDS ALL FOUR CELLS — the card ceiling is the STUDY's ceiling

_LS, answering the question RE raised and nobody had: we priced the card and assumed the other
channels might be healthier. They are bounded by the same number._

**An UPDATED card conveys the COMPLETE and EXACT coverage truth.** Verified across 60 seeds ×
4 workers: `card_capabilities` names precisely `irb_coverage`, **240/240, zero mismatches.**

So the card update is the MAXIMAL coverage-information channel. **Declaration, ask and trace all
convey the same underlying fact — the successor's true coverage — with less reliability
(`ask` may answer stale or mute), less granularity (a declaration covers one segment's method;
a trace covers only classes already attempted), or later (both are post-hoc).** None can convey
MORE coverage truth than a correct card, because a correct card is all of it.

**Therefore the 1.24% of oracle / 0.16σ ceiling is not the card cell's limit. It is the
STUDY's limit**, and cells 1–4 do not have four separate ceilings to discover — they share one,
already measured, and it is below detectability at any n we can afford.

**THE CAVEAT, stated rather than buried, and it is the one place this could be wrong.**
Declaration and trace also carry BEHAVIOURAL information — which method the worker actually
CHOSE — that a card does not. That can exceed the coverage ceiling **only to the extent workers
depart from coverage-optimal play**, which is an empirical question **we have not measured**.
If workers reliably use the best method available to them, the bound is tight; if they do not,
the trace and declaration cells could carry information the card cannot. **Cheap to check on the
existing corpus and it should be checked before the bound is quoted as covering all four cells.**

## What this does to the directions

It removes an option nobody had ruled out: **"drop the card cell and rely on the other channels"
is not available**, because they share the card's ceiling. **The lattice change is not one option
among several — on current evidence it is the only route to a detectable effect for ANY cell.**

---

## ★ THE CAVEAT IS NOT CLOSED — the method-departure check has NO POWER on this corpus

RE checked whether workers holding IRB coverage ever fall back to SA, reported **0 of 82
departures**, and concluded the coverage ceiling is tight for all four cells. **The conclusion
does not follow from that test.** Verified independently:

```
covered IRB segments executed          82
EXACTLY match the IRB figure            0     (RE reported 42 — a tolerance difference)
EXACTLY match the SA  figure            0     <- the "0 departures"
NEARER the SA figure than the IRB one  19     (23%)
within 0.1% / 1% / 5% of IRB       22 / 39 / 51
```

**At exact match, NOTHING matches either figure — so "0 exact SA matches" is what an exact test
returns when execution is noisy. It is not evidence of zero departures.** And on the
tolerance-free test — which figure is the report NEARER to — **19 of 82 (23%) sit closer to SA.**

**Neither number settles it.** Reported/IRB ratios span 0.053–4.202, so a report nearer SA is
equally consistent with "used SA" and with "attempted IRB and was badly wrong." **The value-based
method inference cannot separate those two on this corpus, in either direction.** RE's own
framing elsewhere is the right one: a worker that attempted IRB and got it wrong still made the
coverage-optimal choice — but the test cannot tell us which happened.

**CONSEQUENCE, and it reopens something I closed too fast.** I wrote that cells 1–4 share the
card's ceiling because every channel conveys the same COVERAGE fact. **That holds only if workers
do not depart from coverage-optimal method choice — which is now UNMEASURED rather than
measured-zero.** If they do depart, declaration and trace carry a behavioural signal a card
cannot, and the card ceiling does not bound them.

**So the honest state: the one-ceiling claim is SUPPORTED for coverage information and NOT
ESTABLISHED for the trace and declaration cells.** It does not change the recommendation — the
lattice change is still the only route to detectability for the card cell, and the other cells
are unpriced rather than known-healthy — but *"drop the card cell and rely on the others"* moves
back from **ruled out** to **unpriced**.

**RE's own caveat stands and is now the larger of the two: EXECUTION QUALITY is a second
behavioural signal the ceiling never priced**, because the scorer's `s(seg, w)` assumes faithful
execution. Roughly half of covered IRB attempts miss the figure by any tolerance. **A trace
showing a worker botching work it is approved for is information about RELIABILITY — a different
construct from coverage, and the one place a trace channel could be worth more than a card.**

**Direction implication, new:** a reliability-based manipulation is the first candidate with a
STRUCTURAL argument for why the trace channel would beat the card — the card cannot carry
execution quality at all. That is worth pricing offline before the lattice change is chosen over
it.

---

## ★★ UN-RETRACTION: the one-ceiling claim STANDS. My "no power" verdict was wrong; the check was under-REPORTED, not under-POWERED.

RE supplied the thing my critique lacked and I did not think to ask for: **a REFERENCE CLASS.**
SA is a table lookup; IRB is the ASRF formula. **SA-only segments are cases where we already know
the worker is doing SA** — so they measure how exactly a worker reproduces an SA figure when SA
is what it is doing. Verified:

```
                     within 0.1%   within 1%   within 5%
SA-only: matches SA      41/41       41/41       41/41
covered: matches IRB     22/82       39/82       51/82
covered: matches SA       0/82        1/82        2/82
```

**41 of 41, at one part in a thousand.** When a worker does SA it reproduces the figure exactly.
**So a covered worker falling back to SA would have landed within 0.1% of the SA figure — and
0 of 82 do.** Deliberate SA fallback is bounded at **0–2 of 82**, which is measured, not
unmeasured. **The test is demonstrated detecting SA use, 41 times over.**

**My 19-of-82-"nearer-SA" carried nothing: NEARER IS NOT AT.** Only 2 of those 19 come within
even 5% of the SA figure. Nearest-figure classification has no power here precisely BECAUSE the
IRB errors are large — but tolerance-based classification anchored by a validated reference class
does, and I conflated the two tests.

**And the asymmetry is itself the evidence:** workers reproduce SA **exactly** and IRB
**loosely**, so **the noise is IRB-SPECIFIC** — what you expect if all of them are attempting IRB
and the formula is hard, and not what you would see if some were quietly doing SA.

**SO: cells 1–4 DO share the card's coverage ceiling, and "drop the card cell and rely on the
other channels" returns to RULED OUT rather than unpriced.** My retraction is withdrawn.

**What survives of my correction, and it is real:** RE's "42 used IRB" came from a **2% tolerance
never stated**, and the count runs 22/39/42/51 across 0.1/1/2/5%. **A threshold-dependent count
quoted as a fact about behaviour is §B on the check itself.** That stands.

**I have now over-corrected in BOTH directions on one claim** — first overclaiming inertness,
then over-retracting the ceiling's scope on a test I had judged powerless without looking for a
population where its answer was already known. **RE's distinction is the one to keep:
under-REPORTED and under-POWERED are different failures, and only the second would have been
fatal.**

## The corollary, sharpened by RE and better than the version I recorded

I wrote: *check that the ceiling computation could have come out otherwise.* **RE's form is
operational where mine was aspirational:** *is there a POPULATION WHERE I ALREADY KNOW THE ANSWER,
and does my test get it right there?* **RE had 41 such cases sitting in the same bundles and did
not look; I judged their test powerless without looking either.** A reference class beats a
synthetic control, because it needs no construction and cannot be built to pass.

**Three of us produced a can't-fail confirmation in a single round** — my template 60/60, RE's
30-seed subsample, RE's untoleranced departure count. **The reference class is where the rule
actually bites.**

---

# ★★★ THE GENERAL DIAGNOSIS — ZERO SLACK REMOVES THE MANAGER'S ROOM TO ACT ON ANY INFORMATION

_RE priced the reliability ceiling; it is ~0.00% on all three study instances, an order of
magnitude below coverage's 1.24%. The REASON is structural and it subsumes both results._

**Verified by enumeration — with 9 segments, 3 workers and cap 3, the feasible load shapes are:**

```
cap = 3 :  [(3,3,3)]                                              ONE shape
cap = 4 :  [(3,3,3), (4,3,2), (4,4,1)]                          three
cap = 5 :  [(3,3,3), (4,3,2), (4,4,1), (5,2,2), (5,3,1), (5,4,0)]  six
```

**The manager chooses WHICH three segments each worker gets. It never chooses HOW MANY.** Every
worker takes exactly three, whatever the manager knows or believes.

**That is why BOTH channel families price near zero, and the cap is implicated in both:**

- **Coverage.** Capacity-optimal play already recommends the successor (it is the emptiest
  destination post-swap), so the card discriminates nothing the constraint does not already force.
- **Reliability.** Zero slack forces an equal split, so **knowing a worker is half as good does
  not let the manager give it LESS work — only DIFFERENT work.** Reliability is a per-worker
  multiplier applying equally across its segments, so reshuffling can only exploit variation in
  attainable score across segments, which is small. Seed 23 rosters a worker with 0.511 median
  error and its reliability ceiling is still **exactly 0.0000**.

**C = 3 with 9 segments and 3 workers was chosen to make capacity BIND EXACTLY. Binding exactly
is what removes the manager's room to act on any information at all.**

## This reorders the directions

**SLACK is promoted from Tier 2 to the PRIMARY lever, above the lattice change.** The lattice
change is a fix for the coverage channel specifically; slack addresses the mechanism that
flattens BOTH families, and it is a one-parameter change. **Neither is priced yet — and pricing
is the same offline calculation, so both should be on the researcher's list rather than one
discovered after the other.**

**RE explicitly did NOT recommend slack over the lattice change** and has not priced it. Nor have
I. **What is established is the DIAGNOSIS, not the remedy's magnitude.**

## RE's guards, adopted as stated

Every figure carries its n; workers below n=5 are **UNPRICED rather than measured**; an instance
with any unpriced rostered worker returns **UNCOMPUTABLE, not zero** (2 of 12 workers unpriced).
The within-segment comparison rests on 10 pairs, 3 involving a low-reliability worker.
**RE's own judgement, which I endorse: the per-worker reliability table should not be quoted as a
measurement of worker quality at all — what is quotable is the ceiling and the structural reason
for it.**

## And my confound fired, which is the reason the table is not quotable

```
median spread BETWEEN workers on the SAME segment : 0.035
overall spread ignoring segment                   : 1.000
```

**`w_3330c6`'s apparent 0.511 is largely WHICH SEGMENTS IT DREW, not how well it works.** RE
checked the guard has power where it matters — 3 of 10 comparable segment-instances include a
low-reliability worker — which is the corollary applied to their own check. **The reference class
also holds: every worker attempting an SA-only segment scored a median of exactly 1.000, seven
workers. Exact where the answer is a table lookup, variable where it is the ASRF formula.**

---

# ★★★ SLACK CLOSES THE COVERAGE CHANNEL. My promotion of it last round is RETRACTED.

_LS, `check_slack_sweep.py`, 30 seeds × 3 capacity settings, offline, no run spend._

I promoted slack above the lattice change on RE's diagnosis that *zero slack removes the
manager's room to act on any information*. **I priced it, and for the COVERAGE channel the
opposite is true:**

```
 cap  shapes  nonzero      mean%   nonzero%   sigma    n/arm
   3       1   15/30       0.85%      1.69%    0.22      330
   4       3   19/30       0.68%      1.07%    0.14      827
   5       6    0/30       0.00%      0.00%    0.00      inf
```

**At cap 5 the card ceiling is EXACTLY ZERO on all 30 seeds.** Mechanism verified on seed 3:

```
cap=3   TRUE load [3,3,3]   CARD load [3,3,3]   segments placed differently: 3   ceiling 2.15%
cap=5   TRUE load [5,3,1]   CARD load [5,3,1]   segments placed differently: 0   ceiling 0.00%
```

**With slack the successor takes everything it genuinely covers AND the lied-about segment. No
displacement, so the lie costs nothing.** The coverage channel's entire effect IS the
displacement RR identified — **and displacement requires scarcity.**

## The two channel families respond to capacity in OPPOSITE directions

- **COVERAGE needs SCARCITY.** The effect is displacement; remove the binding cap and it goes to
  exactly zero.
- **RELIABILITY needs SLACK.** With a forced 3/3/3 the manager cannot give a bad worker LESS
  work, only different work; that is RE's diagnosis and it stands.

**They are in direct tension. No single capacity setting opens both, and "add slack" is a TRADE,
not a general fix.** RE's diagnosis was right about reliability and I generalised it to coverage
without checking — the same error shape as my inertness claim: a correct mechanism, extended one
step past what was verified.

## What this does to the recommendation

**The LATTICE CHANGE returns to primary, and now for a reason it did not have before: it is the
only candidate ROBUST TO THE CAPACITY SETTING.** Giving the lost class a single incumbent coverer
makes the lie cost COVERAGE directly, not via displacement — so the effect survives slack instead
of being destroyed by it. **Every capacity-based remedy trades one channel family for the other;
the lattice change trades nothing.**

**Still unpriced: the lattice change's own ceiling.** That is the next offline calculation and it
is the one that should decide, not the argument above.

---

# ★★★ THE LATTICE REPAIR IS PRICED — 1.11σ, AND THE DECISION IS THREE-WAY

_RE priced it (`3637bef`); I verified the combinatorial claim independently._

```
template            nonzero    mean   nonzero mean     max    ~sigma   n/arm
current              15/30    0.85%      1.69%       3.58%     0.11     ~330
proposed_disjoint    30/30    8.51%      8.51%      17.95%     1.11      ~13
partial_overlap       0/30    0.00%      0.00%       0.00%     0.00      inf
```

**The proposed template is ~10× the current ceiling, clears 1σ, and is NONZERO ON 30 OF 30 —
so it also removes the zero-ceiling instances that were the other half of the selection problem.**
At 1.11σ the study needs roughly **13 episodes per arm**, which is affordable for the first time.

## My realism concern is not a tradeoff — at this coverage size it is IMPOSSIBLE

I asked for a partial-overlap variant, expecting to trade some effect for realism. **It prices at
exactly zero on all 30 seeds**, and the reason is combinatorial rather than particular to RE's
choice. Verified by my own enumeration over ALL templates:

```
COVERAGE_SIZE=2, 5 classes:      0 templates have partial overlap + sole-held + singly-covered lie
COVERAGE_SIZE=2, 6 classes:      0
COVERAGE_SIZE=2, 7 classes:      0        <- not a class-count problem; structural at size 2
COVERAGE_SIZE=3, 6 classes: 12,960 (6,480 up to incumbent symmetry — RE's figure)
```

**At coverage size 2 the predecessor has two slots; partial overlap spends one on the shared
class, so the SINGLE remaining class must be both sole-held (0 post-swap coverers) and singly
covered (1). Contradiction.** So **partial overlap and interior spread are mutually exclusive at
size 2**, and buying both costs a **sixth asset class with SA risk weights transcribed from the
source under S1's column-identity discipline** — real work and a real citation, not a parameter.

**So the tradeoff is sharper than I put it to the researcher: not "detectability at the cost of a
more extreme perturbation" but DETECTABILITY OR PARTIAL OVERLAP, NOT BOTH, at the current
coverage size.**

## RE caught their own model bug, and it hid for the reason the whole phase turned on

Their first run priced the proposed template at **0.37% — BELOW current** — and they did not report
it, on the grounds that a repair designed to add a coverage cost pricing below the thing it
repairs is the shape of a broken measurement. **It was: they modelled the card's LIE and not its
SILENCE**, crediting the manager with knowing about classes the card never mentions.

**Under the CURRENT template that omission costs exactly nothing — the silent class is
incumbent-covered 60/60, which they measured themselves two days ago — which is precisely why the
blindness survived.** The model was validated on the one population where its bug is invisible,
and then priced at zero the very property the new template was built to add. **No prior figure
is retracted: the current template's 1.24%/0.16σ is unchanged, for the same reason the bug hid.**

## The three options, as they should reach the researcher

1. **Disjoint template** — 1.11σ, ~13 episodes/arm, affordable now. Cost: the replacement becomes
   a TOTAL capability change, closer to *a different specialist* than *an upgraded one*.
2. **Partial overlap at coverage size 2** — not available. Zero by construction, not by choice.
3. **Coverage size 3 with a sixth asset class** — realism AND detectability, 6,480 admissible
   templates. Cost: a new asset class with transcribed SA weights and its citation.

**Caveats on every figure, RE's and carried:** σ is the stale pre-L1 measurement and scales the
comparison only — **it must not size a suite**; the segment mix is still tuned for the old shared
class, so **the candidates are UNDERSTATED**; and these are ceilings bounding a perfect user of
the channel, not any manager.

---

# ★★★ THE 1.11σ IS NOT ACHIEVABLE BY THE PROPOSED TEMPLATE AS IT WOULD ACTUALLY GENERATE

_RR attacked the number I asked them to attack and found it is a property of the SEGMENT MIX, not
of the template. I verified the mechanism in the generator and it is stronger than RR put it._

**RR's independent pricing** (built from the scorer, not RE's model, so it prices the lie AND the
silence together — the thing RE's bug missed), 10 seeds × 120 labelings = 1200 cells:

```
effect/oracle  mean 0.0359  median 0.0235  max 0.1657     exactly zero: 322/1200 (27%)
split by nA = IRB segments in the successor-unique class A:
   nA=0   0.0124 = 0.16 sigma   <- IDENTICAL to the current template: the repair delivers nothing
   nA=1   0.0341 = 0.44 sigma
   nA=4   0.0780 = 1.02 sigma   <- where RE's number lives
```

**`nA` takes only 0, 1 and 4 — the signature of `shared_class_segments = 4`.** RE's figure comes
from the 1-in-5 labelings where template-A happens to land on the class the CURRENT generator
force-fills.

## And the generator DISABLES that mechanism under the disjoint template — verified

```
_template_shared_class(CURRENT  w0={A,E} w1={A,B})  ->  'A'
_template_shared_class(DISJOINT w0={D,E} w1={A,B})  ->  None      <- the pair share NOTHING
```

`shared_class = None` skips the force-fill block entirely, so the mix falls back to **pure
round-robin: A:2 B:2 C:2 D:2 E:1.** **The disjoint template cannot produce nA=4. It cannot
produce the number RE quoted.**

**And the generator's own comment already says why that matters:**

> *"Under an even round-robin over five classes that set is ~1 segment, which caps the maximum
> measurable arrival effect at ~0.117 of the oracle — BELOW the minimum detectable effect. A suite
> generated that way would be **sub-detectable BY DESIGN and would look entirely healthy**."*

**So the disjoint template silently disables the exact mechanism added to make the effect
detectable, and the generator documents that doing so is sub-detectable by design.**

## RR's sharpest point, and it is the methodological one

RE declined to set the mix because *"choosing it before the ceiling is priced would be tuning the
instrument to the answer."* **But the ceiling CANNOT be priced without the mix — so declining did
not avoid the tuning; it made it implicit and inherited the most favourable value.** The honest
form: **the disjoint template's ceiling is a FUNCTION of the mix, spanning 0.16σ to 1.02σ, and the
mix must be chosen before any single number can be quoted.** RE's "nonzero 30/30" is mix-dependent
too — 27% of RR's cells are exactly zero.

**The mix would have to be RE-SPECIFIED to target the successor-unique class A rather than the
now-nonexistent shared class. That is a design decision, not a parameter carried over** — and it
is the same decision RE deferred, arriving from the other side.

## What goes to the researcher

**NOT a single ceiling number for the disjoint template.** The range and the dependency: **the
repair is worth between NOTHING (0.16σ, identical to today) and ~6× the current ceiling,
depending on one unset parameter that the proposed template also disables by construction.**

**Caveats, RR's and carried:** their probe holds the segment draw fixed and varies labeling, so
the nA distribution reflects the CURRENT generator's forcing; and **every σ figure here divides by
the stale pre-L1 σ = 0.0768, which RR ruled must not size anything.** These are comparative
ratios — **the ratio between 0.16σ and 1.02σ survives a change of σ; the absolute values do not.**

---

# ★★★ THE DESIGN'S CEILING USES THE WRONG BASELINE — this is the CAUSE of the selection fault

_Found by the researcher asking why `channel_effect_ceiling` and `channel_effect_ceiling_stats`
differ. They do not — the first is a thin wrapper. **The defect is one level up: what the design
means by "ceiling" is not the study's counterfactual.**_

```
finance_scorer.channel_effect_ceiling   =  oracle − E[RANDOM coverage-blind assignment]
this phase's card ceiling               =  oracle − optimal play under the STALE CARD
```

**The manager never knows nothing. It always holds the card.** So the design's ceiling answers
*"how much is coverage information worth against ignorance?"* while the study asks *"how much is
CORRECT coverage information worth against the stale card the manager actually has?"*

**Measured, 12 seeds:**

```
mean random-blind ceiling   0.8505
mean stale-card ceiling     0.0777          overstatement 10.9x
instances where the card ceiling is EXACTLY 0 but random-blind is not:  6 of 12
```

## And the selection rule ranks on it — which is how the dead instances got in

`select_study_instances.py:55` stratifies admitted seeds by
`channel_effect_ceiling_stats(...)["ceiling_share"]` into terciles. The three selected:

```
seed   random-blind (what selection ranked on)   stale-card (what the study needs)
   3            9.65%                                    2.15%
  23            5.16%                                    0.00%
  36           13.34%                                    0.00%
```

**Seed 36 has the HIGHEST random-blind ceiling of the three and a card ceiling of exactly zero.**

**The selection rule worked exactly as written.** It stratified across the band, avoided the
favourable end, committed its bounds in advance — every C2 obligation honoured. **It ranked on a
quantity whose baseline is not the study's counterfactual, and that is sufficient to select
instances where the manipulation provably cannot act.**

**This is the CAUSE of the selection fault RE found.** They measured the symptom — two of three
selected instances at exactly zero. This is why: the gate could not see it, because the gate is
not asking the study's question.

## What follows

1. **The admission gate and the selection rule must rank on the STALE-CARD ceiling**, not the
   random-blind one. It is the same DP with a different baseline; `check_card_ceiling` already
   computes it.
2. **`channel_effect_ceiling` is not wrong as a quantity** — "value of coverage information over
   ignorance" is meaningful. It is wrong as an ADMISSION CRITERION for this study, and nothing at
   its definition site says so. **That is the one-line comment this file argued was optional; it
   is not.**
3. **Every admission and stratification figure in `records/` computed before this note is
   conditioned on the wrong baseline** and should be read as ranking instances by a quantity the
   study does not measure.
