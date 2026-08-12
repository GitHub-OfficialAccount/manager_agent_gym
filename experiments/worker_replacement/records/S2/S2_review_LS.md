# S2 — Lead-scientist review, round 2: PASS

Reviewed: commits 0c6fb29 (delivery) + a5a52b5 (fix). Round-1 FAIL and its reproduction:
`S2_review_LS_round1.md`, `S2_ghost_repro_LS.py`. Criterion read first: BACKLOG S2
acceptance + HARNESS_SPEC_v2 E4/§5.

## Verified (by me, directly, on the fixed commit)

1. **The ghost-repeat is fixed at the root.** The reset now sits unconditionally at method
   entry, before the early return, with the defect's consequence and the reproduction
   pointer in the comment. My reproduction re-run: t=2 `[]`, t=3 `['removed alpha',
   'added beta']`, t=4 `[]`, t=5 `[]` — the event is one-timestep again.
2. **Acceptance test re-run: exit 0**, now including the case it structurally lacked —
   the registry path driven across t_swap, t_swap+1, t_swap+2 with the engine expression
   asserted empty and the prompt asserted block-free on both quiet steps.
3. **Full suite parity re-verified by me:** 292 passed, 1 failed
   (`test_live_anthropic_returns_pydantic`, pre-existing live-API failure), 2 skipped —
   matching RE's claim exactly.
4. **No-event byte-identity holds** (1241-char unswapped prompt identical to a build with
   the roster argument never passed).
5. **The two design calls RE flagged, adjudicated:**
   - *Setter over step()-keyword (spec-over-backlog):* CORRECT. The keyword route
     measurably broke 27 tests; E4 requires the render, not the plumbing; precedence was
     stated, evidence given, and the deviation is purely additive.
   - *Reason-leak exclusion:* CORRECT and structural. The observation path is fed the
     registry's (action, agent_id) record and cannot carry `change.reason` — which in
     real timelines is a capability description. The pre-existing string path is
     untouched (asserted in the test).

## Taken on report / assigned to the reviewer

- Independent adversarial read of the five core diffs for anything neither RE nor I
  thought to look for (the round-1 defect was exactly that class).
- The two design calls above deserve independent verdicts, not inheritance of mine.
- RE named a generalisable test-shape pattern ("a test that takes explicit inputs where
  the real path computes them is verifying its fixture, not its subject" — second
  instance in two steps). Candidate methodology rule; the reviewer owns
  METHODOLOGY_RULES.md and should rule on admitting it.

Verdict: **PASS.** → reviewer-reproducer for independent review.

---

# Round 3 (after RR round-1 findings F2/F3/ordering; commit d9a5f04): PASS

## Verified (by me, directly)

1. **F2 fix, stronger than asked:** the engine now calls a public `roster_change_lines()`
   accessor — fail-closed (absence raises), and the announcement has ONE definition
   (content + canonical order) instead of one in the engine and one in tests. The
   run-time assertion logs `roster_arrival_announced` every run and raises if an applied
   change did not reach the observation. Placement after the compatibility fallback is
   correct for the reason stated in the comment (verified against the two
   engine-coordination tests that failed the earlier placement).
2. **Accessor semantics re-probed end-to-end** (records this file's evidence): reset —
   t=2 `[]`, t=3 `['removed alpha','added beta']`, t=4/5 `[]`; canonical ordering —
   changes scheduled add-before-remove still render removals first; **replace branch
   (F3)** — `schedule_prompt_swap` at t=7 yields `['replaced gamma']` with no field
   names and no reason text, and t=8 resets to `[]`.
3. **Acceptance test re-run: PASS. Full suite re-run by me: 292 passed / 1 pre-existing
   live failure / 2 skipped.**
4. **RE's F3 call adjudicated:** recording `replace` structurally (rather than
   documenting the omission) is the right default — an in-place change reaching the logs
   but not the manager is the exact failure class this project studies. Field names
   excluded on the same principle as `reason`.

## Recorded limits (for the reviewer's round 2)

- RE's honest limit on the run-time assertion: for a manager whose observation is built
  by the engine's compatibility FALLBACK (stubs, custom baselines), the observation is
  constructed after the action was chosen — the assertion proves the observation carried
  the announcement, not that the manager saw it pre-decision. The STRONG form holds for
  the structured manager, which is what the study runs. RR to rule whether this needs a
  spec sentence for baseline arms.
- RE re-committed the test-shape defect (ordering test recomputed the sort) one commit
  after the §A rule was admitted, self-caught, and fixed via the single-definition
  accessor. The datum stands: the rule's mechanical check does work the prose does not.

Verdict: **PASS.** → reviewer-reproducer for round 2.

---

# Round 4 (after RR round-2 items; commit d059442): PASS

Verified by me, directly: (1) `observation_source` present on `roster_arrival_announced`
and DISTINGUISHES the branches — RE's committed probe re-run:
`manager` for a manager capturing its own decision observation, `engine_fallback` for a
stub relying on the engine fallback, both with `rendered=True` — the two previously
identical green values are now separable post hoc, per RR's ruling; (2) the ordering
docstring corrected AND pinned by a fixed-example assertion in the acceptance test
(`['removed m_agent', 'replaced a_agent', 'added b_agent', 'added z_agent']` — removals
first, adds/replaces interleaved by id), so documented and real behaviour cannot drift;
(3) acceptance test re-run PASS; (4) full suite re-run by me: 292 / 1 pre-existing / 2
skipped. F4's spec fix (instance-wide id opacity + leak-exclusion discipline) was applied
by LS at 9795411 and is not RE-side work.

Verdict: **PASS.** → reviewer-reproducer for round 3 (scope: the two round-2 items only).
