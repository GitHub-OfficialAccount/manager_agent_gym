# L2a review — the segment-state split (RR)

Standing rule 7. `finance_split.py`, the four-way split re-derived as eight predicates
against the repaired schema.

**Verdict: the design is right and the history in the docstring is the best part of it.
THREE BLOCKERS, all the same shape, and all of them leave every check this module has
still passing.** No new measurement needed; all three are demonstrated on constructed
bundles.

## What is right, and worth keeping

- **States are predicates, not names**, with the sentence declared as authoritative where
  the two disagree. That is the §B fix applied at the point of definition rather than in a
  review.
- **Segment identity from the index, never from the display name** — and the docstring
  says which failure that avoids.
- **Refusal cause from the logged enum, not from the concurrency fields.** The comment
  that those fields call a permanently-barred worker idle and available on 58% of refusals
  is the reason this is right, and it is recorded where someone would otherwise "simplify"
  it.
- **An unknown refusal code RAISES** instead of falling into a catch-all. That is the
  defect that made an availability refusal read as a concurrency one, fixed at the source.
- **Splitting `assigned_but_unexecuted` into three** because the pooled bucket held two
  populations with opposite meanings and could not carry a sign.

## BLOCKER 1 — a missing `task_class` silently reproduces the v1 defect

```python
if payload.get("applied") and payload.get("task_class") == SEGMENT_TASK_CLASS:
```

Both `.get()` calls default to `None`, and `None` is indistinguishable from "this is not a
segment" / "this assignment was not applied". Demonstrated:

```
task_assigned payload missing `task_class` -> seg_00 classified "never_assigned", residual 0, NO RAISE
task_assigned payload missing `applied`    -> seg_00 classified "never_assigned",             NO RAISE
```

**`never_assigned` asserts "the manager never staffed it" — which is precisely the false
claim v1 made and this module exists to stop making.** A renamed or absent field
reintroduces it, and the module's own guards cannot see it: the partition holds and the
residual is zero.

**Fix:** a `task_assigned` payload that lacks `task_class` or `applied` must **raise**.
Absence and evidence have to be distinguishable at the point of use (§B defaults). An
unknown `task_class` value should raise for the same reason `KNOWN_REFUSAL_CODES` does —
the module already applies this discipline one field over.

## BLOCKER 2 — an executed segment missing from `parse_detail` is recorded as unparseable

```python
parsed = detail.get(segment_id) or {}
...
elif parsed.get("rwa") is None: states[segment_id] = "executed_but_unparseable"
```

```
executed segment absent from parse_detail -> "executed_but_unparseable", NO RAISE
```

**"Unparseable" is a substantive finding about the worker's deliverable.** Here it is also
what a missing bundle section produces, so a parse-detail gap is reported as a worker
failure. **Same defaults shape as blocker 1, and it lands on a state that carries meaning
rather than on a residual.**

**Fix:** if `task_id in executed`, a missing `parse_detail` entry is a bundle defect —
raise. `None` for `rwa` is a real value and must come from a present entry.

## BLOCKER 3 — the residual check cannot fire on any data condition

```python
residual = len(by_segment) - sum(counts.values())
```

`states` is only ever assigned from the eight literals in `STATE_PREDICATES`, and `counts`
sums over exactly those keys — so `sum(counts.values()) == len(states) == len(by_segment)`
**by construction, for every input.** Verified: residual is 0 on well-formed input and on
all three malformed ones above.

**It can only fire on a typo in a state string in this same file.** The docstring presents
it as "the same discipline as the regret decomposition's" — but that residual guards
against a *data* condition, and this one cannot. **A check that cannot fail on data is
documentation, and calling it a partition guarantee is the confirming-test shape from §H.**

**Fix:** either say what it actually guards (a coding error in this module), or make it
guard something real — assert that every `segment_task_ids` key received a state *and*
that every `task_assigned` segment task id appears in `by_segment`, which would catch an
index/event disagreement that currently passes silently.

## Limitations

- **The unknown-code raise is not scoped to segment tasks.** The `assignment_deferred`
  loop does not filter on `task_class`, so a new refusal code on a *non-segment* task
  blocks the segment split. Defensible as fail-loud, but it means this module's
  availability depends on unrelated code paths. Worth one line saying it is deliberate.
- **`refusals` and `executed` are unfiltered by `task_class` while `assigned` is
  filtered.** The asymmetry is invisible today because segment task ids are looked up from
  the index, but it is the kind of thing that stops being harmless when a task type is
  added.

## Assessment

**Nothing here touches the design or the state definitions**, which are the substance of
the step and are better than the version they replace. All three blockers are the gap
between what the module asserts and what it can detect — and all three fail toward
"a confident, well-formed, wrong answer", which is the failure mode this phase has spent
two days on. **Once they raise, I have no remaining objection.**

---

# RESOLUTION — verdict LIFTED, verified against the code

_Re-ran the exact negative cases I demonstrated, rather than reading the acceptance report.
All three blockers are closed. **B2 was two sub-cases and RE's narrowing is correct.**_

```
B1a  task_assigned missing `task_class`                RAISES ValueError            fixed
B1b  task_assigned missing `applied`                   RAISES ValueError            fixed
B3   assigned segment task id absent from the index    RAISES ValueError            fixed
     (the guard that replaced the structurally-zero residual, and it FIRES)

B2a  executed segment absent from a NON-EMPTY parse_detail   RAISES ValueError      fixed
B2b  EMPTY parse_detail (no parsing pass ran)          classified, and flagged:
        parsing_performed=False
        uninterpretable_states=['executed_but_unparseable']
        + a reason string, in the RETURNED RECORD
B2c  parsing ran, all entries present                  parsing_performed=True,
                                                       uninterpretable_states=[]   (other direction)
```

**RE's narrowing is right and I would not have got there from my own test case.** A
machinery run has zero model calls, so no deliverables exist to parse — raising on an empty
`parse_detail` rejects a legitimate bundle rather than a defective one. **The case I hit was
the empty one.** The objection underneath it is honoured differently and better: rather than
raising, the record now says the state is **uninterpretable**, because
`executed_but_unparseable`'s predicate is a claim about the WORKER that a run with no model
calls cannot support.

**And the question turned out to matter more than the blocker.** The acceptance's only
`parse_detail` was `{}`, so the partial-gap branch was **unreachable and would have passed
indefinitely** — a control that was never wired, not a missed line. That is now fixed
structurally, with each blocker mapped to the control that fires for it, and RE verified the
map can report **UNCOVERED** before trusting it reporting covered.

## Limitation — the flag is in the record but nothing requires a consumer to read it

`uninterpretable_states` is the right place for it, and RE's reason is right: a printed
banner is dropped by the first summariser while every consumer reads `counts`. **But `counts`
still carries an ordinary-looking integer for `executed_but_unparseable` on a bundle where
that state is uninterpretable.** A consumer that reads `counts` and ignores the flag
reproduces exactly the claim the flag exists to prevent.

**The stronger form, recommended not required:** on a bundle where a state is
uninterpretable, `counts` should not carry a plain number for it — a sentinel, or omission,
so that **a consumer reading only `counts` cannot obtain a value that asserts something
unsupported.** That is the defaults rule one level up: the flag is a *separate field*, and a
separate field is exactly what gets dropped.

Recorded as a limitation rather than a blocker because the information is present and
recoverable from the record, which is the property that was missing before.

## Credit where it is RE's

**"A blocker names the bundle shape it fires on"** is theirs, and it is the construction-path
rule extended to blockers rather than to comparators. It is why B2a and B2b are two rows
instead of one row called B2 — and had they been one row, my re-run and their narrowing
would each have been correct about a different bundle and we would have traded aggregates.

**L2a passes.** One limitation recorded above.
