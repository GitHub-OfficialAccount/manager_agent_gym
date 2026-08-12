# Is the niche-share threshold `1/n_workers`? — probe on the trusted path

**Construction path, named per the handover rule:** `gen.generate(seed, n_segments=N,
shared_class_segments=S)` for `seed in range(60)`, five-class NATIVE path (no
`coverage_override`), `amplify_mix` default True, scored by shipped
`sc.ceiling_vs_stale_card(inst, cap=3)`. nA measured per cell off the INSTANCE.

## The claim under test

LS derived, from `nA >= cap` plus `n_segments = n_workers x cap`:

> threshold SHARE = `nA / n_segments >= 1 / n_workers`

with the supporting statement that *"scaling the book scales the threshold with
it"*, which would mean the threshold `nA` rises with `n_segments`.

## Result — the threshold does NOT scale with the book

    n_segments   cap   threshold nA   threshold share   generated
         8        3          3            37.5%          274/300
         9        3          3            33.3%          300/300
        10        3         n/a            n/a             0/300

**The threshold `nA` is ABSOLUTE at `cap`, not proportional to the book.** So the
SHARE falls as the book grows, with no change to worker count: 37.5% at 8 segments,
33.3% at 9.

## So the derivation's CONCLUSION is right and its STATED MECHANISM is not

Threshold share = `cap / n_segments`. Feasibility requires `n_segments <=
n_workers x cap` (there must be enough slots), so

    threshold share = cap / n_segments  >=  cap / (n_workers x cap)  =  1 / n_workers

**`1/n_workers` is a LOWER BOUND on the threshold share, attained exactly when the
book is at maximum feasible size** — and the current configuration already sits at
that optimum, `9 = 3 x 3`. That is why 8 segments is *worse* (37.5%) rather than
better: shrinking the book moves the share away from the bound.

So worker count is still the lever LS identified, but the reason is tighter than
"scaling the book scales the threshold": the threshold is fixed at `cap`, the share
is `cap/n_segments`, and raising `n_workers` is what *permits* a larger book without
violating feasibility.

## What this probe CANNOT settle, and why the discriminating test is not cheap

LS's test — vary `n_workers` in {3,4,5} at `n_segments = n_workers x cap` — **cannot
run on the trusted path today.** `_lattice_from_template` returns exactly FOUR
workers, and `n_segments` is validated to 8..10, so `n_workers=4` would need 12
segments. Reaching it requires either `coverage_override` (the path under rebuild)
or a lattice that is a first-class generator parameter. **It is the rebuild's first
output, not a preliminary to it.**

The counter-mechanism LS named — more incumbents means more of the card's omissions
are covered, so more suppression — is therefore also untested. It remains unsigned.

## A fault in this probe, recorded because it is the one this project keeps finding

The first run of this probe reported `n_segments=10` as **0.00% at every nA**, and
that was not a measurement. All 300 generations failed `ASSERTION 2a (capacity
feasible)` — 3 post-swap workers x cap 3 = 9 slots cannot hold 10 segments — and the
probe's `st.mean(sh) if sh else 0.0` turned an EMPTY SAMPLE into a legal-looking
zero.

**A default whose value is indistinguishable from a real result, in the same probe
whose subject is a structural zero.** The generator's own assertion caught what my
code silently swallowed; the row is reported as `n/a` above, not as zero.
