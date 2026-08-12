# L6 — LS REVIEW of `557d495`

Read the spec, then the source, then ran the acceptance. States what was VERIFIED versus taken
on report.

## Verdict: the REGISTRY is sound and I pass it. ONE NARROW BLOCKER on section 5's assertion.

The blocker does not touch what the registry does at runtime. It touches the *claim* that the
committed kind list is asserted — and the assertion is weakest exactly where the list is densest.

---

## BLOCKER — section 5's check cannot fail for any kind containing `[]`

`test_finance_quantities.py:147–152`:

```python
unresolved = sorted(
    k for k in committed["kinds"]
    if not any(fq.resolve(p) for p in covered_paths
               if p.startswith(k.split("<")[0].split("[")[0])))
```

Truncating at `[` reduces `episodes[].regret_share` to the prefix **`episodes`**, so the test
asks only *"does ANY path under `episodes` resolve?"* — which is true for every entry in that
container. **A stale or invented entry under an indexed container is undetectable.** Measured, by
planting entries the acceptance never plants:

```
add 'episodes[].totally_made_up_quantity'   -> flagged? False
add 'episodes[].seed_XYZ'                   -> flagged? False
add 'coverage_misrouting.invented'          -> flagged? True    (no '[', so the prefix survives)
```

**`episodes[]` is the single largest group — 17 of the 55 path-derived kinds — so the assertion
is blind over roughly a third of the list, and blind specifically in its densest region.**

**This is the missing positive control, and it is the control I specified.** My ruling said:
*"a positive control shows it firing on a deliberately stale file."* Section 5 has none —
sections 3 and 4 are properly controlled and section 5 is the one that is not. **Had the control
existed it would have caught this**, which is the whole argument for the rule.

**It is also the third instance of this shape in this file's own history**, and section 5's
comment invokes the second one by name (*"the same shape as the fixture that compared
`(load unavailable)` to itself six times"*). The comment is right; the code below it repeats the
defect it names.

**Fix:** compare on the resolved KEY, not on a truncated path prefix — every committed kind must
resolve to a specific registry entry, not merely to some sibling under its container. Plus the
positive control: plant a bogus kind under `episodes[]` and require the check to fire.

---

## What I verified and accept

- **The trap I flagged is genuinely avoided.** `KIND_LIST` is read (`:144`) and never written;
  the only write is `quantity_registry_acceptance.json`, a different file. The list is asserted,
  not regenerated. RE had the weaker instinct, said so, and took the ruling.
- **Direction 1 and direction 2 are both properly positive-controlled and I re-ran them**:
  direction 1 fires on a planted unregistered value; direction 2 fires when a registered kind is
  never emitted, simulated by removing a section — which is what a rename looks like. **These are
  the two that guard the emitted report, and they are sound.**
- **Write-time refusal with a stamping escape, as ruled** — a report with an unregistered
  quantity REFUSES; the escape writes `CONTAINS_UNREGISTERED_QUANTITIES` into the artifact; a
  clean report writes with no stamp, asserted in the other direction.
- **The class contract raises rather than warns:** a rate cannot construct without a comparator;
  a count must state a comparator or say why there is none; well-formed entries of each class do
  construct (the other direction, checked).
- **`52 declared covering 55 path-derived` is the argument for declared keys, not a discrepancy** —
  three kinds (`n_declined`, `n_unreadable`, `regret_share`) are emitted at two sites each, which
  a derived normaliser must double-count and a declared key collapses correctly. **That is my
  item 3 vindicated by a number I did not predict**, and it is stronger than the argument I gave
  for it.
- **Identifiers registered rather than filtered closes 413-vs-431 properly.** `seed` × 18 is
  exactly the gap; my walker skipped it, RE's did not, **and neither of us said so.** Registering
  it as class `identifier` with a stated exemption makes the closure a registry entry rather than
  an agreement between two people.
- **σ entries carry `MEASURED PRE-L1 — must not size any suite`**, so the stale-σ limitation now
  travels with the quantity instead of living in a backlog line. That is better than where I put
  it.

## Non-blocking

RE's cost note — that writing 52 population predicates *was* the work, and that it surfaced
things the prose never did (`episodes[].oracle` has no comparator because it IS the comparator;
`split_residual`'s comparator is zero and any non-zero value is a defect rather than a
measurement) — is the strongest evidence the exercise was worth doing, and belongs in whatever
we write about method.

---

## ★★ RR FOUND TWO BLOCKERS I DID NOT — BOTH VERIFIED BY ME, ONE LIVE ON THE PRIMARY DV

I asked RR to attack exactly these two surfaces and both broke. My own probing tested only the
MATCHING path — bogus kinds, including a one-character typo variant — and neither blocker can be
reached that way, because in both the value never gets as far as being matched.

### RR-1 (LIVE) — §B does not apply to any quantity the walk cannot see

`numeric_leaves` takes `int`/`float` and drops `bool`, so string-formatted, `None` and boolean
quantities are **EXEMPT rather than flagged**. Verified:

```
{'sneaky_rate_as_string':'0.33', 'sneaky_percent':'12.5%',
 'sneaky_null_rate':None, 'sneaky_bool_claim':True, 'legit':1}
walk sees 1 of 5 — the four evasions are invisible, and a partial evasion returns ok:True
```

**And it is live on the primary DV.** `finance_reroute.py:342`:
`return len(numerator) / len(eligible) if eligible else None` — **so `rerouted_share`, in exactly
the case where it is UNMEASURABLE, escapes the §B mechanism**, and there is no registry entry for
it yet either (`REGISTRY` holds `regret_share`/`staffed_regret_share`/`mean_regret_share` only).
**This is the inverse of RR's own default rule: the unmeasurable form evades the check built to
stop unmeasurable and zero rendering identically.** L2a will emit this.

**Fix (RR's, adopted):** walk `None` and `str` as quantities and require registration, so a kind
can DECLARE `None` as its unmeasurable form — which is the statement we actually want recorded.

### RR-2 — the class contract is bypassable by choosing the class, and the registry already does it

`__post_init__` enforces the internal consistency of the ENTRY, never its agreement with the
DATA. Verified: `Quantity(key='fake', cls='count', population='p',
comparator_absent_because='a denominator')` is **ACCEPTED** — so a genuine rate declared `count`
avoids the comparator requirement, which is the module's central mechanism.

**Not hypothetical. Seven existing entries declare `count` while emitting continuous values**,
confirmed by reading their emitted values: `achieved` (6.76), `oracle` (8.55), `regret` (1.78),
`allocation_loss_staffed` (−0.083), `execution_loss_signed` (0.866), `unstaffed_loss`,
`split_residual` (−8.9e-16). **None is a count.**

**RR's diagnosis is the part that matters: the five-class set has nowhere to put a continuous
non-rate MEASURE, so `count` has already drifted into meaning "has a comparator-or-reason and is
not a rate". The one strict class is the one an author has an incentive to avoid.**

**Fix (RR's, adopted): make the comparator requirement CLASS-INDEPENDENT** — every quantity
states a comparator or why there is none, after which mis-declaring buys nothing. A sixth
`measure` class is worth adding for honesty, but **the asymmetry is what creates the bypass.**
A value-type assertion (`rate` within [0,1], `count` integral) becomes enforceable only after
that, since it would currently fail on all seven.

### Two limitations RR recorded, both accepted

**A declared glob is still a derivation, and one crosses subtrees:**
`per_cell_descriptive.cell3.values[0]` resolves to `episodes[].regret_share` and inherits its
population — so a future quantity placed in that list inherits it silently. **Declared keys
NARROW the hiding place; they do not close it**, and the docstring must say so.

**No disjointness assertion.** `resolve` returns the first match; RR probed every pattern pair
and found **0 overlaps today**. Clean now, unguarded later — the same shape as the ordering
non-determinism already fixed once with a total sort key.

**Verdict revised: L6 does NOT pass. Two blockers, both cheap, RR-1 live on the primary DV.**

---

## ★ RE's TWO FIXES VERIFIED — and the hiding place THEY flagged is REAL AND ALREADY ACTIVE

**RR-1 fixed and verified:** the walk now surfaces `None`, `bool` and numeric strings; RR's exact
probe goes from 1-of-5 seen to 4-of-5. **RR-2 fixed and verified:** `Quantity(cls='count',
comparator_absent_because='a denominator')` now RAISES, and the escape requires a role from a
closed set — free text raises too. **RE's division of labour is the right generalisation and I am
keeping their words: THE WALK SURFACES, THE REGISTRY ADJUDICATES.** A walk that decides for
itself is how `seed` came to be skipped by one of us and not the other.

### CONFIRMED, and it is the thing RE asked me to check rather than take

RE registered the DV's quantities under an `artifact` scope and flagged that **a quantity can now
hide by being registered under the wrong artifact** — a new hiding place opened while closing two.
**It is not hypothetical. Measured:**

```
registry artifacts : scope_report (55 entries) · reroute (12 entries)
check(report, artifact='scope_report')  <- the DEFAULT, and what the acceptance runs
grep for any acceptance running check() over the REROUTE artifact against a reroute report: NONE
```

The reroute artifact is touched exactly once, at `test_finance_quantities.py:260`, inside a
**planted value-type control** — not a check of a reroute report. **So the 12 reroute entries —
which include `rerouted_share_conditioned`, the PRIMARY DV — are registered and never validated
against anything.** Direction 2 ("registered kinds never emitted") cannot fire for an artifact
nobody checks, so those entries could be stale, misnamed or duplicated and nothing would catch it.

**This is precisely the both-directions rot RR warned about, one level up: coverage drops while
the count stays flat.** Registering under a new artifact is currently a way to opt OUT of
validation while appearing registered.

**Required before L3 — and I am answering RE's question, they asked whether I wanted this before
or after: BEFORE.** The artifact L3 emits is `reroute`, so shipping L3 with its primary DV's
entries unvalidated is the one ordering that makes the gap matter. **Assertion: the set of
artifacts CHECKED must equal the set of artifacts REGISTERED**, with a positive control on a
registered-but-never-checked artifact.

**The disjointness assertion can wait** (RR measured 0 overlaps today; clean-now-unguarded-later
is a real risk but not one L3 realises). Artifact coverage first.

### RESIDUAL, minor — a PERCENT-formatted rate still evades

`{'r': '12.5%'}` → **not seen**. Numeric strings that parse as a number are now surfaced; a `%`
suffix is not parsed, so a rate emitted as a display percentage remains invisible to §B. Narrow,
and worth closing when the artifact assertion lands rather than on its own.

---

## ★ ARTIFACT COVERAGE VERIFIED (2/2, positive-controlled) — and THREE corrections on the rename finding

RE's fix verified: the reroute artifact is now checked against a real reroute report built from a
machinery episode, a registered-but-unchecked artifact fails the control, and `'12.5%'` is seen.
**L6 passes on my side.** RE's own framing of what they had flagged is the right one: *"I was
describing a leak and it was a door"* — the thing that could hide was not a quantity but an
entire artifact, and the one hiding held the primary DV.

**RE's display-name finding is REAL and valuable: four analysis sites still join on
`f"Risk-weighted assets — {sid}"`** (`finance_scope_report.py:204,:332`, `finance_logging.py:472`,
`finance_fabrication.py:230`, `run_finance_episode.py:133`), and the manager demonstrably renames
tasks. **Three corrections to how it was reported.**

**1. `run_finance_episode.py:133` IS DRY-RUN ONLY, so it does NOT run during a live episode.**
It sits inside `_install_dry_run_stubs()`, called only under `if dry_run:` (`:207`). RE ranked it
first *"because it is the only one that runs DURING an episode, so a rename there corrupts the
run"* — it runs during a MACHINERY episode. **Consequence: no display-name site executes during a
live run, so this is NOT a pre-L3 blocker.** Real cleanup, correctly ranked as a separate step,
but it does not gate the run and I am not blocking L3 on it.

**2. The "8 renames" figure is not supported by the log.** `task_refined`'s payload is
`{task_id, task_name, description_before, description_after}` — **there is no `name_before`, so
the record cannot distinguish a RENAME from a description-only refinement.** The eight are
`task_refined` EVENTS. Renames plainly did occur — *"Output floor check (72.5%) with corrected IRB
figures"* is not an original name — but the count is over a population the log cannot resolve.
**That is our own §B shape, a third time inside this exchange, on a number produced while
investigating it.**

**3. And it exposes a LOGGING GAP of the same family as the assignment-stream one:
`RefineTaskAction` can change `task.name` and the record does not carry the previous name, so a
rename is not reconstructible.** Worth fixing alongside the four sites — a name-based join is
unsafe precisely because names change, and we currently cannot measure how often they do.

**MY OWN ERROR, recorded because it nearly killed a real finding.** I checked for renames by
grepping the payload for `new_name`, got zero, and was one step from reporting that the manager
never renames anything. **The field is `task_name`. I guessed a field name and read the empty
result as evidence** — the exact defect RR caught in themselves on the board schema, and the
reason the null-positive-control rule exists.

**Standing risk, RE's, and it is the sharpest framing of why this matters:** criterion (e) was a
manager-created name that accidentally MATCHED; this is a manager rename that accidentally STOPS
matching. One of the observed renames was *"Aggregate risk-weighted assets"* — **one editorial
decision away from matching the segment prefix.**
