# L6 — review (RR)

> **STATUS (added later): VERDICT LIFTED — L6 PASSES.** Both blockers were fixed and verified
> against the code; see the RESOLUTION section at the end of this file. The verdict below is the
> ORIGINAL one and is retained unrewritten, but a reader stopping at this header would get the
> stale answer — which is why this pointer is here rather than an edit to the text.

**Verdict: the design is right and the two things LS asked me to attack both break. TWO BLOCKERS,
both cheap to fix, one of them live rather than hypothetical. Two limitations.**

The scoping decision that produced this module is the best judgement call of the phase: rates-first
dissolved under measurement because "rate-shaped" has no type-level answer (three defensible
classifiers gave 12/33, 7/28, 40/79 on the same file), so classification became a property of the
*entry*. That is my own selection-rule argument taken further than I took it — I said select by
implication-in-a-retraction rather than by shape, and the right conclusion was that shape is not a
property of the quantity at all. Registering identifiers *as identifiers* rather than filtering
them out of the walk is the same instinct: a declared exemption is auditable, a silent skip is the
413-versus-431 discrepancy.

---

## BLOCKER 1 — §B does not apply to any quantity the walk cannot see, and the primary DV is one of them

`numeric_leaves` collects `int`/`float` and excludes `bool`. **Four value types are therefore
exempt from the registry entirely**, not flagged as unregistered — invisible:

```
report = {..., 'sneaky_rate_as_string': '0.33', 'sneaky_percent': '12.5%',
               'sneaky_null_rate': None, 'sneaky_bool_claim': True}
check(report) -> n_values 3 · unregistered_values []
```

Four unregistered quantities, zero flagged. **And partial evasion passes cleanly**: `unregistered`
only ever contains numeric leaves with no match, and a string leaf never enters `leaves` at all, so
a complete numeric report *plus* one string-formatted quantity returns `ok: True`. The second
direction only catches wholesale evasion, where enough kinds go missing to populate
`never_emitted`.

**The `null` case is live, and it collides with a rule committed this phase.**
`finance_reroute.rerouted_share` returns `None` when the denominator is empty:

```python
return len(numerator) / len(eligible) if eligible else None
```

So **the study's primary DV, in exactly the case where it is unmeasurable, is invisible to the §B
check** — an unmeasurable quantity is exempt from stating its population. That is the inverse of
the §B rule added at `fbfcef1`: *"unmeasurable" and "zero" must never render identically.* Here it
is worse than identical rendering; the unmeasurable form escapes the mechanism designed to catch
it. L2a will emit this quantity.

**Fix:** walk `None` and `str` leaves as quantities too, and require registration for them. A
registered kind may then declare that `None` is its unmeasurable form, which is exactly the
statement we want on the record.

## BLOCKER 2 — the class contract does not bind to the emitted values, so strictness is opt-out

`__post_init__` enforces internal consistency of the *entry*: a `rate` needs a comparator, anything
else needs a comparator or a reason. **It never checks that the declared class matches the data.**

```
Quantity(key='fake', cls='count', population='p',
         comparator_absent_because='a denominator')      -> ACCEPTED
```

A genuine rate declared `count` with `absent="a denominator"` sails through, and the
comparator requirement — the central mechanism of this module — is avoided by choosing the class.
Answering LS's question directly: **yes, it can be bypassed by a kind that declares the wrong
class, and nothing downstream notices.**

**And this is not hypothetical, because the registry already does it — without intent.** Seven
entries declare `count` while emitting continuous values:

```
episodes[].achieved · episodes[].oracle · episodes[].regret
episodes[].allocation_loss_staffed · episodes[].execution_loss_signed
episodes[].unstaffed_loss · episodes[].split_residual
```

None of these is a count. They are continuous scores, and they are declared `count` because **the
five-class set has nowhere else to put them** — there is no class for a continuous non-rate
measure. So `count` is already functioning as "has a comparator-or-reason and is not a rate", which
means the class field carries less information than the docstring claims, and the one strict class
is the one an author has an incentive to avoid.

**Fix, and it is two lines rather than a redesign: make the comparator requirement
class-independent.** Every quantity states a comparator or why there is none, full stop. Then
mis-declaring a class buys nothing, because strictness no longer varies by class. Adding a sixth
class (`measure`) is worth doing for honesty, but it is the comparator asymmetry that creates the
bypass, not the missing class.

A value-type assertion (`rate` emits within [0,1], `count`/`identifier` emit integers) becomes
enforceable *after* the class set is fixed — it would currently fail on all seven entries above,
which is itself the evidence for the fix.

## LIMITATION 1 — a declared glob is still a derivation, and one crosses subtrees

The docstring's case against a derived normaliser is right, and the failure it cites is real. But a
hand-written glob narrows that failure rather than removing it. Measured:

```
per_cell_descriptive.cell3.values[0]  -> episodes[].regret_share
   inherits population: "one episode; regret as a fraction of that episode's own oracle"
```

The `episodes[].regret_share` entry declares `per_cell_descriptive.*.values[]`, so **any future
quantity placed in that list silently inherits the regret-share predicate** — a kind hiding inside
a kind, which is the failure declared keys were meant to prevent. Latent, requiring a future
change, so a limitation rather than a blocker. Worth stating in the docstring: declared keys narrow
the hiding place, they do not close it.

## LIMITATION 2 — no disjointness assertion, and `resolve()` returns the first match

`resolve` iterates `REGISTRY` in order and returns the first pattern that matches. **Nothing
asserts the patterns are pairwise disjoint**, so a future entry overlapping an earlier one loses
silently and inherits the earlier population. I probed every pattern pair by instantiating each
glob and testing it against all others: **0 overlaps at present.** So this is clean today and
unguarded tomorrow — the same shape as the ordering non-determinism this project already fixed once
with a total sort key. One assertion over the probe set closes it.

## What holds, checked rather than assumed

- **Both directions are genuinely implemented.** `never_emitted` catches the stale-entry rot I
  raised, and `ok` requires both to be empty.
- **Coverage prints in the check's own output** — `n_kinds_matched/n_kinds_registered` and
  `covered/total values` in `summary`, not in a document a reader must find. This was the condition
  I attached to approving a staged pass and it is met.
- **Write-time refusal, with the escape hatch STAMPING THE ARTIFACT** rather than logging the gap
  elsewhere. `CONTAINS_UNREGISTERED_QUANTITIES` carries the meaning sentence into the file itself.
  That is the right shape: the artifact that gets quoted is the artifact that carries the warning.
- **Retraction notes attached to the entries that caused them** — `episodes[].n_unstaffed`,
  `coverage_misrouting.executed.rate`, `declines.n_unreadable`,
  `variance_quantities.sigma_gap_full_minus_staffed`. A reader meeting the quantity meets its
  history, which is stronger than a separate retraction list.
- **`sigma_pooled_within_cell` carries the prohibition in its own note** — "must not size any
  suite: L1 is designed to destroy the distribution it was measured on." The carried limitation is
  now attached to the number rather than to a thread.

**Neither blocker touches the design; both are gaps between what the contract says and what it can
enforce. The fixes are a wider walk and an unconditional comparator.**

---

## RESOLUTION — verdict LIFTED, verified against the code

Both blockers are fixed, and the second is fixed **better than the way I recommended**.

- **Blocker 1 closed.** `numeric_leaves` now delegates to `is_quantity_value`, which surfaces
  `None`, booleans and numeric-parsing strings while keeping free-text prose out. The docstring
  names the case I raised: `rerouted_share` returning `None` on an empty denominator escaped the
  mechanism precisely where it is unmeasurable. And a registered kind now declares `may_be_none`
  with a mandatory `none_means` — so the unmeasurable form is *stated* rather than exempt, which is
  the outcome I asked for rather than merely blocking the leak.
- **Blocker 2 closed, and superseded.** The comparator requirement is class-independent, with the
  escape restricted to a **closed set of roles** (`absent_role ∈ COMPARATOR_ABSENT_ROLES`) rather
  than free text — the code comment notes that "free-text 'no comparator' is how the requirement
  decays", which is a failure mode I did not name. **My fix stopped the bypass; the range rule
  closes the gap underneath it.** `plausible_range` is mandatory for every numeric class, so an
  entry is now bound to its data. That is what `cls` never did, and it works where my fallback
  suggestion (rates in [0,1], counts integral) could not, because it needed no class-set change.
- **Limitation 1 partly addressed:** `resolve` now takes an `artifact` argument and filters on it,
  so cross-artifact collisions are impossible. The within-artifact glob inheritance I described
  remains, and remains a limitation.

**No new attack surface from the range rule.** I looked for one, since I proposed it: a range is a
declared interval checked against observed values, so the failure mode would be a range declared so
wide it cannot fail. That is visible on the face of the entry in a way a class is not, which is the
property I wanted. Worth one convention if the registry grows: **a range spanning more than a few
orders of magnitude should carry a reason**, on the same logic as `absent_role`.

**L6 passes.** Two limitations remain recorded: within-artifact glob inheritance, and no pairwise
disjointness assertion over path patterns (0 overlaps measured at the time of review).
