# L10 acceptance review — `check_l10_properties.py` (RR)

Standing rule 7. Six properties, seven controls, built before the instances exist.

**Verdict: the acceptance is sound and the three defects LS found in it are the value.
NO BLOCKERS. One real gap in property 5's digest, one correction in LS's favour on
property 3, and the p5a teardown is right.**

## Property 3 — the definition is correct, and it has a SPEC SENTENCE

LS: *"I derived that reading from the mechanism rather than from a spec sentence."*
**They undersold their own footing. The scorer is the spec.**

`finance_scorer.ceiling_vs_stale_card` builds the belief as:

```python
card_claims        = set(by_id[event["predecessor_id"]]["irb_coverage"])
succ_as_carded     = dict(by_id[successor]); succ_as_carded["irb_coverage"] = card_claims
```

**The card asserts the successor covers exactly the predecessor's set.** So what it claims
and the successor lacks is `predecessor − successor` — **lies** — and what the successor has
and the card omits is `successor − predecessor` — **silence**. LS's `lied_classes()` is the
first of those, exactly. **Not mechanism-derived: derived from the module property 3 exists to
protect.**

Checked against both arrangements: `partial` gives one lied class held by an incumbent
(passes); `current` gives one lied class held by nobody (fails, as intended). **And refusing
rather than picking when `len(lied) != 1` is right** — under a template with two lied classes
the property is ambiguous, and a silent `[0]` would have chosen one.

## Property 5 — the division is honest, and the digest has a hole (limitation)

**The division is right.** A hash detects change from a pinned value and cannot establish that
the pinned value is correct; pairing it with S1's transcription test is the correct split, and
saying so in the comment is what stops it being read as a correctness check.

**But the digest's population is an enumerated list of NAMES, and one is missing:**

```
_TABLE_SOURCES : SA_SOVEREIGN, SA_BANK, SA_CORPORATE, SA_MDB, PD_INPUT_FLOOR, QRRE_REVOLVER_FLOOR
SA_* attributes on the module, NOT digested :  SA_RETAIL_FLAT,  SA_TABLES
```

**`SA_RETAIL_FLAT` is the SA treatment for one of the five asset classes** — `sa_risk_weight`
returns it by a name test rather than a table lookup — and it carries **54 segments across the
30-seed corpus**. **An edit to retail's flat weight passes the drift detector silently.**

This is the same shape-difference that excluded retail from clone registration (*"its SA weight
is a flat constant reached by a NAME TEST … not a table lookup"*). **Retail keeps falling
through because it is shaped differently from its neighbours**, which is a reason to digest by
*container* rather than by an enumerated list of names.

**I checked the added-table case rather than asserting it, and my first suspicion was wrong:**
registering a new class **does** move the digest — but only via `PD_INPUT_FLOOR`. `SA_TABLES`
itself is not digested, so **a class added with an SA table and no PD-floor entry would be
invisible.** Narrower than I expected, still real, and closed by digesting `SA_TABLES` and
`SA_RETAIL_FLAT` instead of naming four tables individually.

## p5a's teardown — correct, including the part LS didn't claim

```python
original = dict(gen.SA_SOVEREIGN)
try:    gen.SA_SOVEREIGN[next(iter(gen.SA_SOVEREIGN))] = 9.99  ...
finally: gen.SA_SOVEREIGN.clear(); gen.SA_SOVEREIGN.update(original)
if basel_digest() != pinned: raise AssertionError("fixture leaked")
```

**Sound.** Shallow copy is safe (float values), `clear()`+`update()` preserves object identity
for anything holding a reference, the `finally` runs on the raising path, and the post-hoc
digest assertion is a real teardown check rather than a comment claiming one.

**And the vacuity case is already self-reporting**, which LS did not claim and should:
if the mutation were a no-op — say the value already equalled 9.99 — `p5` would pass, the
fixture returns `not ok` = **False**, and the control reports as **not fired** rather than as
passed. **The structure catches its own dead perturbation.** That is the property the other
three can't-fail cases today all lacked.

## On the three defects LS found

(i) is the day's fourth can't-fail instance and the first found by *searching for the seed a
fixture fires on* rather than by someone re-running it. (ii) is an assumption replaced by a
measurement. **(iii) is a new shape worth the ledger: a crash on stderr while the report went
to stdout made a FAILED run read as TRUNCATED.** Not "a check that cannot fail" — **a failure
wearing the costume of an incomplete success**, and the fix (line-buffered stdout, counted
skips) is the right one.

## Labels

| finding | label |
|---|---|
| property 3's definition is correct and code-derived, not mechanism-derived | confirmed |
| `SA_RETAIL_FLAT` is outside the digest; retail's SA weight can drift silently | **limitation** |
| `SA_TABLES` not digested: a class added without a PD floor would be invisible | **limitation** |
| p5a teardown correct, and its dead-perturbation case self-reports | confirmed |
