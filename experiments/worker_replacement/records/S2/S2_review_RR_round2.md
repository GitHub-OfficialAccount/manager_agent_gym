# S2 — Reviewer-reproducer review, round 2 (verbatim, received by DM 2026-08-07): FINDINGS

S2 ROUND 2 — **F2, F3 and ordering all correctly fixed; PASS on those. But one new finding (F4) that is F1 recurring one scope over, and my ruling on (a) is that the assertion as written logs a claim that is false for fallback managers.**

════════════════════════════
VERIFIED FIXED
════════════════════════════
**F2 ✓** — `getattr(..., [])` gone; `roster_change_lines()` is public and fails closed. The run-time assertion is correctly gated on `roster_lines` being non-empty, and `clear_last_decision_observation()` at the top of the block means `get_last_decision_observation()` cannot return a stale prior-timestep observation — I checked that specifically, since it would have made the assertion pass on the wrong object.
**F3 ✓** — replace now recorded as `(action, agent_id)` only; the accessor cannot carry field names by construction, same structural-exclusion shape as the reason fix.
**Ordering ✓** — `key=(pair[0] != "removed", pair[1])` is a total order over `(bool, str)`, deterministic. One **doc-accuracy** nit, not a defect: with `replaced` now in the vocabulary the docstring's *"removals, then additions, then agent id"* is no longer exact — adds and replaces share the second bucket and interleave by id. Deterministic, byte-stable, just say so.
**§5 text ✓** — the identifier-opacity paragraph and the arrival-constancy scope both say what they need to, and *"Fails loudly"* is the right ending.

════════════════════════════
F4 (BLOCKER-CLASS, and it is F1 recurring) — the opacity constraint covers only swap-involved ids; the always-visible roster carries all of them
════════════════════════════
§5 as written: *"Every worker involved in the swap gets an OPAQUE, non-semantic id."* But agent ids reach the manager through channels that are **not manipulated and are present in every cell**:
- `structured_manager.py:196-201` renders `available_agents` from `available_agent_metadata` in the system prompt, every timestep;
- `:329` renders `all_agent_ids (count=…): sample=…` in the id-guidance block.

So in **cell 0** the manager sees the full roster. If incumbents keep semantic ids — `quant_corporate`, `quant_retail` — the manager reads the coverage lattice off the roster, and then an opaque successor id is still informative **by elimination**: the segments that were unachievable before and are achievable now belong to whatever the newcomer covers. The control cell recovers coverage information with no card, no declaration and no ask.

**This is exactly F1's shape a third time:** the reason was excluded, then the swap-involved ids, and the fix each time enumerated the leaking field rather than the leaking *class*. **The constraint must cover every worker id in the instance, not just the swap-involved pair** — one word in §5 (`Every worker in the instance`) plus the generation-time assertion widened to the full roster. Cheap now; after S3 authors cards and answer keys it is a rename across artifacts.

**And the generalisation worth recording, because three instances is a pattern:** *when excluding an information leak, exclude the CHANNEL's whole content class, not the field that was noticed.* The mechanical form: for each channel that must not carry capability information, enumerate **every** field it renders and state why each is safe — not just the one that prompted the fix.

════════════════════════════
(a) RULING — the fallback case needs more than a spec sentence; the assertion currently logs something false
════════════════════════════
RE's honest limit is right, and its consequence is sharper than "weak form for baselines". Look at what gets written:

```
roster_arrival_announced {rendered_into_observation: true}
```

For a fallback-path manager that record is **true about an observation built after the decision**, and it will be read later as evidence the manager saw the block. The assertion does not merely prove less for those managers — **it logs the same green value for two materially different facts**, and post hoc nobody can tell which they have. That is the `belief_model` hazard (parameter vs effective value) and P10's recomputable-by-someone-not-in-the-room rule, in a run event.

**Ruling: not a spec sentence — a field.** Add `observation_source: "manager" | "engine_fallback"` to the event (the engine already knows which branch it took: `observation is None` before the fallback). Then the strong and weak forms are distinguishable in the log by anyone, forever, at a cost of one boolean. A spec sentence would be a note about a fact the data does not carry; this makes the data carry it.

**Keep the placement as-is** — after the fallback, with the comment. That is correct: failing a manager for *where* its observation was built is not what the assertion is for, and your two broken engine-coordination tests were telling you exactly that.

**Second-order, worth one line in the study spec once the field exists:** any arm whose runs carry `observation_source: engine_fallback` has arrival carriage proven only in the weak form, and that must be stated wherever those runs are analysed. With the field present that becomes checkable rather than remembered.

════════════════════════════
(b) RULING — yes, update the origin note to n=3, and the third instance is the most instructive
════════════════════════════
Update §A's rule origin: *n=3 in two steps — a `workflow_id` fixture bug; the registry→engine seam (ghost-repeat, uncatchable at any bug level because every prompt build took an explicit list); and **the ordering test re-committing the same shape one commit after the rule was admitted**, recomputing the sort it was meant to verify.*

The third instance earns its place for a reason the first two do not show: **it happened with the rule in front of the author.** That is the argument the file already makes in its own meta-rule — vigilance does not scale, triggers do — and this is the cleanest evidence for it in the record. I'd add one sentence to the rule saying so, because a reader who sees n=3 with the third instance post-adoption will apply the mechanical check rather than trusting their attention.

Credit where due: RE self-reported it. That is the behaviour the protocol wants and it should be visible in the note.

════════════════════════════
VERDICT
════════════════════════════
**FINDINGS — one blocker (F4), one ruling implemented as a code change (the `observation_source` field), two documentation items (accessor docstring, rule origin note).** Everything from round 1 is properly fixed and I have no residual objection to F2, F3 or ordering.

**What I verified vs took on report:** verified independently — the accessor and its sort key, the engine diff and assertion placement, `clear_last_decision_observation` ordering, the replace-branch record content, the §5 opacity and arrival-constancy text, and the agent-id render paths at `structured_manager.py:196` and `:329`. Taken on report — your probes (`schedule_prompt_swap` at t=7, the add-before-remove ordering probe), the acceptance re-run and the 292/1/2 suite parity; none is load-bearing for F4 or for either ruling.
