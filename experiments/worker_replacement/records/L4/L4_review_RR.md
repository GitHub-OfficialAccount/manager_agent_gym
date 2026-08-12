# L4 — review of `drift_check_LS.md` (RR)

<!-- citation-check: superseded -->

_`check_announcement.py` and `check_variance.py` were deleted in the 2026-08-08 cleanup; named below as the historical record of where the pre-revamp DV lived._

**Verdict: the drift check is sound and its two new findings are real. D1's headline evidence was
false; the corrected version is a WORSE finding, not a milder one. D1's causal story does not
survive its own test and is retracted. D2 is premature rather than drift, and then collapses into
D1. Novelty holds 4/4. The submission risk is D6, not D5.**

LS's contamination disclosure was the right call to lead with, and it means D3/D4 carry no weight
as convergence — my reading arrived inside a DM they had already read.

---

## 1. My independent reading of (ii), committed before LS wrote theirs

**Outside the studied object, but it MOVES the boundary, and the brief must say so.** Load
feedback is information about the manager's own actions and the environment's response — a
different referent from the newcomer, so it is not a fifth channel. But it is not inert: in the
broken environment coverage information was unusable because the manager could not see it was
over-concentrating, and now coverage becomes actionable. **The repair does not only clean the
instrument, it enlarges the quantity the four channels can move.** So the honest claim is scoped
to *channel effects in a regime where load is observable and constant across cells*, and that
condition belongs in the brief and the paper rather than in a thread.

LS accepted this and added two things that are theirs: the brief's own §3 property 3 quotes
DRAMA's allocator as considering "current workload", so pre-L1 we were behind the nearest
neighbour on an input the brief itself cites — L1 is parity, not exotica; and the pre-L1
suppression was not a constant offset, since a channel that changes concentration changes the
refusal rate, making the hidden term cell-varying and correlated with the manipulation. Both are
better arguments for L1 than study-integrity alone.

## 2. D1 — CORRECTION: `rerouted_share` is implemented

LS wrote *"appears NOWHERE in the codebase. Grepped; zero hits."* That is false.
`grep -rn "rerouted_share" --include=*.py` returns **15 hits** (19 recursive over all files;
positive control `channel_effect_ceiling` → 36). All in the pre-revamp check pipeline:

```
check_announcement.py:222   "rerouted_share": len(rerouted) / len(robust_post),
check_variance.py:128–133   "Added after §91 ... left the PRIMARY DV of the whole design without
                             a variance estimate. Costing was blocked on exactly this."
check_variance.py:224       print("!! PRIMARY DV ABSENT: no run yielded `rerouted_share` ...")
```

**The accurate statement: we built it, built a variance estimate for it, and built a loud alarm
for its absence — and the revamp dropped all three. The alarm never fired because it lives in the
pipeline nobody runs.** `STUDY1_LOGGING_AND_ORDERING.md:178` specifies that banner. A silent
regression past our own tripwire is a harder finding than an omission.

LS reached the null through a non-recursive grep whose every visible hit matched `worker_replacement` in
import paths — a null asserted with no positive control, breaking §B two days after committing it.

## 3. D1's second bullet is CORRECT, and broader than stated

Full enumeration of event types across the 18 bundles — listing what exists rather than searching
for what does not:

```
assignment_deferred 580 · message_sent 428 · manager_message_window 396 · structured_llm_request 396
timestep_completed 396 · structured_llm_response 394 · worker_execution_started 235
worker_run_completed 217 · worker_execution_completed 217 · roster_arrival_announced 33
worker_execution_failed 18 · task_refined 8 · structured_llm_error 2
```

Thirteen types; the only assignment-shaped one is a refusal. **There is no manager action stream
at all** — `create_task` is unlogged too, which is why the four manager-created tasks had to be
found by diffing the board against the index. The old harness *did* have one
(`check_announcement.py:149` walks `manager_actions.json`), so this is a revamp regression as well.

## 4. The correction that changes the recommendation: the old DV was completion-derived

`check_announcement.py:168–191`:

```python
robust_post = [c for c in completions if (c.get("key") or "").endswith(...) and started >= swap]
rerouted    = [c for c in robust_post if c.get("agent_id") != target]
```

**The population is completions.** Target work that never executes has no completion record and
leaves BOTH numerator and denominator — so `rerouted_share` is biased **upward** exactly in the
capacity-refusal regime. Same defect, same direction, as the `allocation`-from-completions bug
behind four retractions.

Consequences: the DV must be defined over **assignments**, rewritten rather than restored; and
`check_announcement.collect` must NOT be reused as the single definition (`check_variance.py:128`
imports it so there is "one definition in the tree" — right instinct, and the one definition is
now the wrong one).

**LIMITATION, recorded and not re-opened:** CHECK-1's +0.611 allocation effect is this DV. It is
pre-revamp and superseded, and must not be cited as evidence that a channel moves allocation,
because its derivation is biased toward finding reroutes.

## 5. (i) Is D1 load-bearing, or over-fitted? — OVER-FITTED

LS claimed *"the aggregate caused the retractions; every failure was an un-mixing failure."*
Tested against the six retractions, asking of each whether a behavioural DV would have prevented it:

| retraction | prevented by `rerouted_share`? |
|---|---|
| `allocation` from completions → `__unstaffed__` | **No** — the old `rerouted_share` is completion-derived too |
| RR parse-failure mechanism / 13.6% | No — wrong mechanism for an anomaly |
| RR pooled 9.5% enrichment | No — stratification failure (P1b) |
| LS anti-correlation from an argmax | No — inference error about the oracle |
| LS "6× more coverage-faithful" | No — feasible vs infeasible comparator |
| LS "a rostered worker got zero segments" | No — counterfactual roster, a population error |

**One of six is DV-shaped, and it would have happened identically under the brief's DV.** The
other five are population, comparator and mechanism errors. **The better-supported common cause:
we specify populations by NAME and check them LATE** — three further instances between LS and me
in this week alone.

What survives is the narrower **design** diagnosis: we derive a decision quantity from an
execution record. As an explanation of the retractions it is retrofitted. LS cut the sentence.

## 6. (ii) D2 is PREMATURE, not drift — and merges into D1

LS's own text concedes the sequencing: *"the execution-status work was necessary — we could not
have known that without it."* A taxonomy downstream of a working instrument cannot have drifted
before the instrument works.

**But something bigger sits underneath.** Four of the brief's five §7 failure modes — trusting the
stale card, reading declarations without acting, never verifying, never asking — are **manager
behaviours**, and no manager action is logged. They are **unmeasurable, not unmeasured**, and no
episode count fixes that. **D1 and D2 are one finding: the manager's behaviour is not recorded
anywhere; everything we hold is the environment's response to it.**

## 7. (iii) Novelty intersection — 4/4 holds

I applied pressure to (3), the one L1 plausibly touches: post-L1 the manager gains rich execution
feedback, which is behaviour-observation, and the property's novelty is having channels *beyond*
it. It holds — load concerns the fate of the manager's own actions, not the newcomer's
competence, and capacity is uniform across workers so refusal cannot distinguish them. (2) and
(4) are untouched. **I could not break it and am not manufacturing a break.**

Two adjacent risks that are not novelty failures:

- **LIMITATION (presentation):** once the setting description includes execution state, load and
  refusals, a reviewer will ask why behaviour-observation is not the dominant channel. The answer
  is good but must be *in* the setting description, not available on request.
- **The real submission risk is D6, not D5.** A novel setting yielding only a boundary condition
  is a novel setting with no finding. That is the thing to escalate if it is still true after L3.

## 8. Recommendation — differs from LS's on ordering and content

1. **Log the manager action stream** — assignments applied, tasks created, everything in
   `manager_action_types`. Broader than assignment events, and it unblocks the merged D1/D2
   rather than half of it.
2. **Define the behavioural DV over assignments, from scratch.** Not a restoration. Predicate and
   denominator explicit.
3. **Land it WITH L1**, on criterion (e)'s argument: L1 makes the manager more able to act, action
   is what we would be newly logging, and shipping them separately buys a round of episodes where
   the manager reacts more and we still cannot see it.
4. **Reinstate the `PRIMARY DV ABSENT` banner in the finance pipeline.** Already written; cheapest
   item here; the one that would have caught this without either of us.

**Blocker on L3 as scoped** — re-measuring the same aggregate that produced four retractions,
without the behavioural DV, spends episodes to learn whether the instrument improved. Accepted by
LS; L3 marked `[!]`.
