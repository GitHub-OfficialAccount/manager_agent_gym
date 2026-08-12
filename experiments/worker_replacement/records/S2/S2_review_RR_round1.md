# S2 — Reviewer-reproducer review, round 1 (verbatim, received by DM 2026-08-07): FINDINGS

S2 REVIEW — **FINDINGS, not a pass.** Three, of which the first is the same defect class as the reason-leak, hiding one field over: the exclusion works and the thing it excludes is still getting through. Plus the requested ruling.

Read in spec order: BACKLOG S2 → HARNESS_SPEC_v2 E4/§5 → the five diffs → the acceptance output. Verdicts on the two design calls are mine, formed before opening your review files.

════════════════════════════
F1 (BLOCKER) — `agent_id` IS a capability description in our own designs, so the reason-exclusion does not close the leak it was built to close
════════════════════════════
The registry strips `change.reason` because it *"in real timelines is a capability description"*, and renders `f"{action} {agent_id}"` instead. But the id is not neutral in the designs this channel exists to serve:
- eDiscovery sketch §5, ours, already passed: predecessor `review_analyst_kw`, successor **`review_analyst_tar`**. The successor's *method* is in its id.
- The finance coverage lattice is worse, because coverage is the studied variable: any id of the shape `quant_corporate` / `quant_retail_sec` announces the successor's coverage set in the arrival block.

So a manager in **cell 0** — the information-absent control, stale card, no declaration, no ask — is told *"added review_analyst_tar"* and can infer the method from the string alone. **The card and declaration channels are then measured against a control that already leaked their content**, which biases every single-channel contrast toward null and does it silently. That is the same failure as the reason-leak, one field over, and it is invisible to any test that asserts "the prompt contains both agent ids" — which is precisely what the acceptance criterion asserts.

**This is not S2's code defect; the code does what it says.** It is a spec gap S2 has now made load-bearing. **Fix belongs here anyway, because S2 is where the constraint is discoverable:** require opaque, non-semantic agent ids for any worker involved in the swap (`worker_07` / `analyst_b`), as a generation-time assertion in the env spec, and record the constraint in §5 next to "roster arrival held constant". Cheap now; after S3 builds the generator it is a rename across artifacts, cards, and answer keys.

════════════════════════════
F2 (BLOCKER, silent-failure class) — the arrival channel fails OPEN to absent, with no signal
════════════════════════════
`engine.py:427-434` reads the record as `getattr(self.agent_registry, "_last_applied_changes", [])`. A defensive getattr on a **private** attribute means: any registry that is subclassed, mocked, or replaced — and any future rename of a private field, which carries no deprecation obligation — yields `[]`, the block is omitted, and **the run proceeds silently with no announcement**. §5 requires arrival held constant across all cells; this path can drop it in some runs and not others with nothing in the logs.

Note the asymmetry that makes it dangerous: the failure produces *exactly* the appearance of a well-formed no-event timestep. There is no crash, no warning, and the prompt is byte-identical to a legitimate quiet step.

**Fix, small:** drop the default — read the attribute directly so a missing record raises — or, if defensiveness is wanted, assert presence once at engine construction. And add the assertion the study actually needs: **at `t_swap`, the rendered prompt contains the roster block** — a logged run-time check, not only a unit test. This is the same discipline as the byte-identical description assertion; the channel that must be constant should be verified in every run, not assumed from a passing test.

════════════════════════════
F3 (LIMITATION) — the `replace` branch records nothing structurally, so one event shape is silently unannounced
════════════════════════════
`add` and `remove` append to `_last_applied_changes`; the **`replace` branch does not** (registry.py:380-450 — it appends to the human-readable `changes` list and broadcasts a comms notice, but never touches the structured record). So an in-place `replace` produces a prompt with **no roster block at all** while the ExecutionResult path reports a change.

Study 1 uses remove+add, so this is not blocking — but §9's learning-teammate horizon and `WORKER_PROMPT_NO_METHOD` both live on the replace path, and a future step that switches to it would inherit a silently unannounced event. **Either record it structurally too, or comment the omission as deliberate with the reason.** Right now the asymmetry is undocumented, which is how it becomes a surprise later.

════════════════════════════
(2) THE TWO DESIGN CALLS — MY OWN VERDICTS
════════════════════════════
**Setter over `step()` keyword: CORRECT, and the precedence reasoning is sound independent of the count.** BACKLOG says *"carry into `manager_agent.step()`"*; HARNESS_SPEC_v2 E4 requires only that arrival be *"rendered into the manager's observation"*. E4 states the requirement, the backlog stated one implementation of it, and the spec wins by the stated precedence — that holds at 0 test breakages, not just 27. The 27 is evidence that the backlog's phrasing was incidental, not evidence of the precedence. Two things I'd add: the setter is a **public method on a public abstract class**, so it is fork surface a subclass could override — worth a CHANGED.md line if not already there; and `_pending_roster_changes` is manager state that is *overwritten* every timestep rather than consumed, which is safe only because the engine sets it unconditionally before every step. That invariant is currently implicit — one comment at the setter would make it explicit.

**Reason-leak structural exclusion: CORRECT in mechanism, INCOMPLETE in coverage.** Feeding the observation path `(action, agent_id)` so it *cannot* carry the reason is the right shape — a structural exclusion beats a filter, and I'd generalise that as its own small rule. But F1 is the coverage gap: the exclusion enumerated one leaking field and the id was the other.

════════════════════════════
(3) MINIMALITY — RESIDUAL CHANNELS BEYOND F1
════════════════════════════
- **Block position: clean.** Inserted at a fixed point before `observation_aid_block` in every render.
- **Ordering within the block: NOT asserted, and it is cheap to fix.** Lines follow `self._scheduled_changes[timestep]` list order. For our remove+add at one timestep the rendered order is whatever the scenario appended — stable in practice, but nothing asserts it, and if a generator ever emits changes from a dict or set the text varies run to run and breaks byte-comparability across cells. **Assert a canonical order (e.g. removes before adds, then id) at render time.**
- **Verb vocabulary: clean** — `added`/`removed` are fixed strings.
- **Timestep label: correct and now load-bearing**, since your round-1 catch was precisely its false advance. Good.
- **One thing the minimality argument should say and does not:** the block's *presence* is itself the signal, and its absence is the no-event state. That is intended, but it means the channel is binary-visible and cannot be "held constant" in the strict sense across swapped and unswapped runs — only across the five swapped cells. Fine for §8's grid (all cells are swapped), and it is exactly why H2's missing unswapped arm matters. Worth one sentence so nobody later claims arrival was constant across a comparison that included an unswapped run.

════════════════════════════
(4) RULING — ADMITTED, with a mechanical check
════════════════════════════
RE's pattern is real and now n=2 in two steps. Admitting it to METHODOLOGY_RULES.md §A, worded to be checkable rather than aspirational:

> **A test that supplies explicit inputs where the real path computes them is verifying its fixture, not its subject.** Every acceptance test must exercise the production path that produces its inputs, and for state that is *reset* or *accumulated*, must cover at least one call where the state should be EMPTY following one where it was not.
> **Mechanical check:** for each input the test constructs by hand, name the production function that computes it in the real path; if that function is not called anywhere in the test, the test does not cover it.
> _Origin: n=2 in two steps — a `workflow_id` fixture bug, then the registry→engine seam, where the roster record ghost-repeated on quiet timesteps and the acceptance test could not have caught it at any bug level because every prompt build took an explicit list. The test passed because of its shape._

The **empty-after-non-empty clause is the load-bearing half** and it generalises past this instance: reset bugs are invisible to any suite that only tests the eventful case, and both of our per-timestep records (`_last_applied_changes`, `_pending_roster_changes`) are of that kind. I'll fold it in with the file's other §A rules.

════════════════════════════
VERDICT
════════════════════════════
**FINDINGS — not a pass.** F1 and F2 are blocker-class and both are cheap: an id-opacity constraint plus a generation-time assertion, and removing a `getattr` default plus a run-time roster assertion at `t_swap`. F3 and the ordering assertion are limitations with named fixes. Your round-1 ghost catch and its fix I verified in the diff and it is correct — the reset is unconditional at method entry, before the early return.

**What I verified vs took on report:** verified independently — all five diffs read in full, the engine call-site ordering, the registry apply loop including the `replace` branch, the `getattr` default, the render insertion point, and the id-semantics collision against our own eDiscovery sketch. Taken on report — the 292/1/2 suite parity and the 27-breakage measurement (I did not re-run the suite; neither number is load-bearing for any finding above).
