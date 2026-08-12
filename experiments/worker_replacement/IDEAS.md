# Candidate directions — recorded, not adopted

_Ideas raised while other work is in flight. Each entry records the idea, the strongest objection to
it, and what would have to be true for it to be worth doing. Ideas are cheap; the objections are the
useful part._

**§1 and §2 are unauthorised and unscheduled. §3 is a brainstorm record and parts of it are decided —
those parts are marked inline.**

---

## 1. Worker↔manager communication (researcher, 2026-07-27)

**The idea.** Let the manager and workers exchange messages. If the manager can ask a worker what
method it is using — or the worker can report a change — detection becomes direct rather than
inferential.

**The researcher's own caveat, and it is the right one:** the mechanism may be too trivial to
publish, even combined with a simple belief layer.

### The decisive objection: detection was never the bottleneck

Communication improves the **sensor**. Everything measured in this experiment says the failure is
in the **consumer**:

| finding | figure |
|---|---|
| the manager detects the wrong method unaided, from raw artifact text | 3 of 12 silent runs |
| the belief layer renders `contradicted` **correctly** when it fires | 3 accepted contradictions, all true |
| routing is invariant to the belief score | 3 of 3 conflict cases; +2.5 to −1.5 got the same decision |
| the numeric channel (already computed, already in an artifact) is read | 0 of 332 manager turns — **flash only; superseded below, pro reads it** |

**A better sensor feeding a consumer that ignores the sensor changes nothing.** On current evidence
communication would raise the quality of a signal already being discarded.

### The second objection: the worker cannot report the change

The perturbation swaps the worker's toolset and prompt at t=3. **The worker has no introspective
access to its prior configuration** — it cannot say "I used to compute percentiles and now I don't,"
because nothing in its context records that it changed.

What it *can* report is its **current** method. And it already does, in every artifact:

```
method: robust 95th-percentile reference standard (mean+2*SD cutoff from reference population)
```

That report is **self-contradictory** — it names the required standard and describes a different
procedure. So a communication channel would add a second self-report from the same worker, with the
same defect, and no access to the fact that matters.

**This is why Axis 2 infers from behaviour rather than asking.** PLASTIC compares observed
transitions; ODITS tracks a latent; ConvCPD reads a changepoint out of action likelihoods. None of
them query the teammate, and the reason is structural: **a teammate that is unaware of its own
change cannot report it.** Our scenario reproduces that faithfully, which is a point in the
scenario's favour.

**So: communication substitutes for extraction, not for detection.** It gives the method claim more
reliably; it does not reveal that the method changed, and it does not make the manager act.

### The version that is NOT trivial, and it comes out of our own traces

Reframe communication as the **action** rather than the **sensor**.

At `q` t=20 the manager detected the mismatch unaided, wrote it out correctly, and chose
`inspect_task` — an **information-seeking** action — rather than rerouting. `inspect_task` returned
task metadata and a resource **ID**, no content. So:

> **The manager's revealed preference was to seek information before acting, and the environment had
> no channel for it.**

That reframes the proposal entirely. Not *"let them talk so the manager can detect"* but:

> **Given a belief that a worker may have changed, is QUERYING the right action — cheaper and more
> reversible than rerouting — and does a manager that can query act on beliefs it otherwise ignores?**

That addresses the **belief-to-action gap** we have measured rather than the detection gap we have
not. It is responsive to observed behaviour rather than imposed on it. And it is a two-stage decision
under uncertainty — detect, query, then act — which is a real problem rather than a prompt tweak.

It also connects to the least-solved corner of the literature summary: querying is an action whose
value depends on what the teammate will say, which is the adaptive-teammate problem in miniature.

### What would have to be true for it to be worth doing

1. **The belief-to-action gap survives the aid amendment.** If the manager reroutes once the aid's
   default stops reading as an endorsement, there is no gap for querying to bridge.
2. **Querying must be able to return something extraction cannot.** If the answer is just the method
   line again, the channel adds nothing — it has to reach a fact the artifact does not carry.
3. **The query must have a cost.** Free queries make the optimal policy "always ask," which is not a
   research question.

### Verdict

**The sensor framing is trivial and also wrong for this failure.** The action framing is neither, and
it is the one the traces point at. **Do not pursue until the aid amendment reports** — condition (1)
is the gate, and it is currently being tested.

### Superseded 2026-07-27 — condition (1) resolved, and the objection is now stronger

_Section references to `RETHINK.md` below are historical: that file was deleted 2026-07-28 and its content
is superseded by `REFLECTION.md`. They are left as written rather than repointed, because they record what
was argued at the time._

**The gate has reported.** Condition (1) was *"the belief-to-action gap survives the aid amendment."*
It survived: `amendment_fav` t=14 and t=20 both assigned the degraded worker with the aid reading
`contradicted` and an idle eligible alternative. **So this entry is not blocked any more — but two
later results make the sensor framing worse than merely trivial.**

**The pro-manager run kills it outright.** A stronger manager **cites the numeric channel** at t=18,
t=19 and t=20, where **0 of 332 flash turns** ever did — and then used those values as grounds for
`noop`. **A channel that is read, and whose content is offered as evidence for inaction, cannot be
improved by adding a second channel.** Communication would supply, more reliably, information the
manager already has and already misreads.

**And the environment already contains a better sensor than communication would be** (see `IDEAS.md` §2
and `CONSUMPTION_BOTTLENECK.md`): the reconciliation identity — `0` where the workflow's own ground truth
expects 5/18/17 — is an arithmetic impossibility, stronger than any self-report a worker could make. It
fires perfectly, three times per run, and changes nothing.

**The action framing survives but its precondition has moved.** It rested on the t=20 `inspect_task`
choice reading as *"the manager wanted information and the environment had no channel."* That is now
confirmed and sharpened: `Inspect(Ti)` **is** the formalism's designated channel (`ManagerAgent.pdf`
§3.3), and the content renderer exists one dereference away (`Resource.pretty_print`,
`schemas/core/resources.py:44`) and is never called. **So the question is no longer "should we add a
query action" but "what happens when the query action that already exists is made to work"** —
`RETHINK.md` §7 item 4, and much cheaper than a communication mechanism.

**Condition (3) — the query must have a cost — is unchanged and still binding.** In the current
environment `Inspect`, `AssignTask` and `noop` are all free, so there is no tradeoff for any belief to
inform (`RETHINK.md` §6).

---

## 2. Reframe: signal-strength threshold instead of aid design (lead scientist, 2026-07-27)

**Prompted by a finding, not by a hunch.** The `Method Reconciliation` task is a purpose-built,
in-band change detector that nobody designed as one:

| | Batch A | Batch B | Batch C |
|---|---|---|---|
| healthy (`control`, `full`) | 5 | 18 | 17 |
| degraded (`silent`) | **0** | **0** | **0** |

It computes `|robust_count − rapid_count|`. When the target degrades to a rapid-screen method the
robust audit returns *the same number* as the rapid screen, so the difference is **arithmetically
zero where the workflow's own ground truth expects 5/18/17**. The coordinator states it in plain
text three times:

```
Batch A Robust Audit flagged 59 outliers; Batch A Rapid Screen flagged 59 outliers.
Absolute difference = 0. Confirmed via shared artifact analysis tool with result=0.0.
```

**This is a stronger signal than the belief layer produces** — an identity between two numbers that
cannot legitimately be equal — and it is ignored. **Detection channels are now three, and 0 of 3
trigger an action:** (1) the artifact `method:` string, (2) the reconciliation identity, (3) the aid's
`contradicted` label.

### The compounding fact: there is no failure feedback anywhere

`completed_predefined` is **16/16 in every run** — the 1.000 ceiling and the 0.732 floor are
**indistinguishable to the manager**. `r_check` is an offline grader the manager never sees. Nothing
is ever marked `FAILED` except the stakeholder sign-off. **The reconciliation task reports `0` and
succeeds.** The failure is silent, consequence-free in-band, and we then measured whether the manager
notices.

### The reframe

Seven arms are null, and the nulls are uninformative because no channel is being consumed — a better
belief format is the eighth thing that will not be read. So stop asking *"does aid X help"* and ask:

> **How unmissable must the signal be before the manager acts on it?**

| rung | signal | status |
|---|---|---|
| 1 | artifact `method:` string | **no action** (articulated in only 3 of 12 silent runs) |
| 2 | reconciliation identity, `0` vs 5/18/17 | **no action** |
| 3 | belief aid `contradicted` | **no action** |
| 4 | reconciliation **task fails** rather than succeeding with `0` | untested |
| 5 | stakeholder raises it in-band | untested |
| 6 | direct standing instruction to verify methods | untested |

The crossing point is a **measured quantity** rather than a null, it is a claim about LLM managers
rather than about our aid, and rungs 1–3 are already spent. Monotone by construction, so a
non-monotone result is itself informative.

### Two confounds on the current null that need clearing either way

1. **Missing affordance.** No action implements *"this completed work is wrong, redo it elsewhere"* —
   `RetryTaskAction` refused the single correct attempt (t=11). Does adding it change t=14/t=20?
2. **No failure feedback.** If reconciliation *fails* instead of succeeding with `0`, does a failure
   signal produce rerouting where a belief did not?

Both are environment properties rather than mechanisms, both are cheap, and until they are cleared
the seven-arm null is **partly a statement about our environment, not only about the manager.**

### Open scope question for the researcher

Is the contribution **(i)** an AHT mechanism — looking closed in this environment — or **(ii)** a
diagnostic result: *detection is not the bottleneck; belief-to-action is, and task-completion status
dominates artifact content*? The evidence sits with (ii). See `CONSUMPTION_BOTTLENECK.md` for the
t=11→t=20 self-overwrite that states it most sharply.

---

## 3. Brainstorm record — 2026-07-27 (researcher + lead scientist)

_Unlike §1 and §2, **parts of this are decided**, and they are marked. Held after arm 3 closed and after
the pro-manager run, prompted by the researcher's objection that the tool-change framing is too narrow
and his hypothesis that the failure is an engineering problem rather than an LLM limit._

### The researcher's hypothesis was right, and it is measured

Extracted the verbatim manager prompt at the failing turns. The information is present; the geometry is
hostile and the aid is broken:

| | |
|---|---|
| requirement, char **11,706** | *"Apply the robust 95th-percentile reference standard to audit batch A"* |
| delivered method, char **20,138** | *"method: reference mean-plus-two-standard-deviations (z-score cutoffs)"* |
| **gap** | **8,432 chars**, opposite ends of one 11,860-char section |
| aid's verdict | `contradicted`, citing `[r34]` — **which appears once in 30,543 chars, in the row citing it** |

**All 9 relation IDs the aid cites are dead links.** And it is not a rendering bug — it is the schema's
contract. `ManagerFacingWorkerState` sets `extra="forbid"` and every evidence field is
`*_relation_ids: list[str]`. **There is no text field, and one cannot be added without changing the
schema.**

> **The design principle was "the aid must not add information, only point at what is visible." Quoting
> visible text is not adding information — it is the safest form of pointing, because the reader can
> check it. By forbidding text, the schema made verification impossible instead of unnecessary.**

### Two claims of mine withdrawn here

- **"The null survives with every known presentation defect removed."** False. The amendment fixed four
  presentation *choices* and never touched the two largest defects, which were unknown then.
- **"The aid at 93.6% depth is a defect."** Probably backwards. The aid is the last substantive block, and
  the end of a prompt is a *strong* position; lost-in-the-middle penalises the middle. The real positional
  problem is one level down: **~72% of the 6,489-char aid block is ledger JSON placed before the readable
  table.** That disappears with the rewrite.

### Should we use RL, since the problem is a POSG? — DECIDED: no

The POSG in `ManagerAgent.pdf` §3 is a **specification** device, not a mandate; the paper's own baselines
are prompted LLMs. Against RL here: one episode is ~50 manager calls and 13–18 min, so RL sample counts
are infeasible; and `ICRL4AHT` (Jing et al. 2026) ran the nearest thing — AD and DPT on AHT — and found
they **underperform random baselines with flat learning curves**, *"not merely an implementation detail."*

**What the formalism does earn:** it names `O_M`, the observation function. Our finding is that `O_M` is
the problem. **The contribution the POSG framing supports is observation design, not policy learning.**

### `O_M` versus the belief layer — a distinction worth keeping

`O_M` determines what information **exists** in the prompt. The belief layer is a **derived summary**
appended on top; it never changed `O_M`. And the 8,432-char gap is neither — it is **layout**, which the
formalism does not name and which may be doing most of the work.

### Modelling behavioural change — DECIDED: keep the current levers

The researcher's judgment: the two levers are the right way to model it and there is no cleaner one; do
not spend effort perfecting the degradation, whatever the worker reports is realistic.

| lever | changes | runs |
|---|---|---|
| `toolset_to_screening` | capability — tools removed, and the worker **announces the consequence** in its `method:` line | **15** |
| `model_prompt_judgment` | model + prompt; **capability intact**, integration degraded | **0** |

**The judgment lever is implemented and has never been run.** Its prompt keeps every tool and instructs
the worker to report a partial single-column result without aggregation, never mentioning the change. So
**the method claim stays correct and the number is wrong** — which kills string-comparison detection by
construction and makes detection a question of numeric plausibility. It requires a replacement model
(`requires_replacement_model=True`), so it needs authorisation.

Change dimensions, by how much inference they force: capability (done) → **reliability** (stochastic, needs
accumulation) → intent/priorities → protocol adherence.

### `arm3t` already aggregates — correct, and it sharpens the point

`arm3t` is recency-weighted accumulation (`score = prior + 0.5·(score − prior) + evidence_sum`). The
problem is that **under the toolset lever every observation after t=3 points the same way** — the signal is
noise-free and monotone, so one observation is as good as ten. **Aggregation is a mechanism whose problem
does not exist in this environment.** It earns its keep only when observations conflict, which the judgment
lever supplies for free (integration failure bites on multi-column tasks only, so the same worker looks
fine on single-column work).

### The Assign-All objection — the researcher's, and the strongest point raised

Information-gathering actions consume execution time, widening a gap that is already bad: the paper reports
**Assign-All 0.502 goal completion against CoT 0.313**, CoT **17× slower** with 25.8% delegation overhead,
and the authors concede *"managerial interventions can sometimes be actively detrimental."*

**Rather than avoid it, make it the question:** *when is it worth a manager's turn to verify a subordinate
rather than dispatch more work?* In our environment the value of information is computable — one wrong batch
costs its own score **plus its reconciliation entirely** (1.0 → 0.0), ~0.09–0.13 of total `r_check`.

### Forms of the estimate, and the candidate mechanism

| form | estimates | why inadequate here |
|---|---|---|
| explicit competence label (ours) | `method:` claim vs task clause | **dead under the judgment lever** — the claim stays correct |
| latent embedding (ODITS) | continuous teammate state | needs gradient training; our manager is prompted |
| type posterior (PLASTIC/HBA) | belief over a type library | needs a pre-enumerated type space |
| outcome bandit | empirical quality per worker | needs quality feedback; environment reports 16/16 always |
| peer cross-check | one worker verifies another | **that is our reconciliation — inert, no expectation** |

**Candidate mechanism: prediction, then surprise.** Before delegating, the manager commits in its own words
to what the artifact should say — method, and rough magnitude. On arrival it compares against **its own
stated expectation**.

Why this one:
- It is **Axis 2's actual machinery** (likelihood of observed behaviour under a model) ported to an
  orchestrator, where the "action" is an artifact.
- It **manufactures the expectation whose absence is our sharpest finding** — verification without an
  expectation is inert; the reconciliation computed `0` faithfully and nobody knew `0` was impossible.
- It makes the comparison **local** — its own prediction against the arriving artifact. No cross-reference,
  no glossary, no position problem.
- It is **the only route that survives the judgment lever.**
- It has real design problems: prediction granularity, anchoring on what you then see, the cost of a turn,
  and inverted surprise when the manager predicts wrongly.

### Paper shape

**Motivation:** corrupt success is an orchestration blind spot — structural completion read as competence
(the self-overwrite, 3 runs, 2 models). **Mechanism:** prediction-then-surprise. **Evaluation axis:** when
verification is worth a turn.

### The rendering fix — DECIDED: build it, and it is NOT a contribution

Replace the table with sentences that state the fact instead of citing an unresolvable ID, scoped to
on-scope eligible workers:

```
Worker fit, from artifact methods already shown above:
- portfolio_analyst's last Robust Audit reported "reference mean-plus-two-standard-deviations
  (z-score cutoffs)". Robust Audit requires "the robust 95th-percentile reference standard".
  These do not match.
- risk_analyst has not done a Robust Audit yet.
```

~330 chars against 6,489. No glossary, no score, no identifiers, no boilerplate rows. **The evidence is the
sentence, so there is nothing left to cite.**

> **Stated plainly: if this works we do not have a paper, we have an erratum.** Its value is entirely
> gating. If routing moves, the seven-arm null is an artifact and **must not be published as a fact about
> managers** — one reviewer noticing nine dead links dismisses the whole result. If routing does not move,
> the null is **earned** and reportable. Neither outcome is reportable without it.

**Sequence, one variable at a time** — because the amendment changed four factors at once and nothing could
be attributed afterwards:

| step | change | status |
|---|---|---|
| 1 | natural-language rendering, position held **last** | **building** |
| 2 | move the block earlier, after the task listing | only if 1 fails |
| ~~3~~ | ~~inline the note on the ready task~~ | **dropped — redundant with 1 once scoped to eligible workers** |

**Position stays last** for step 1: a verdict placed before the task list has nothing to attach to, and the
last block is adjacent to the decision the manager is about to make.

## 4. THE SHELF — potentially good ideas held for researcher discussion (2026-08-05)

_Standing list under the researcher's protocol (BRAINSTORM §103): potentially good/novel ideas are
SHOWN TO THE RESEARCHER for discussion; only ideas rejected as not-good/not-novel in team discussion
may be discarded. Objection levels per P14 (+ commitment-level, §103). Each entry: what it would
establish / why potentially novel / strongest standing objection / what discussion decides._

1. **Priced information acquisition ("the information economy").** Where does a manager stop paying
   for information about a teammate? Novel: no cost term on information actions exists anywhere in
   AHT (G3, unverified), and it is the Aghion–Tirole bridge. Objection: no price exists in the
   current build (setup-level — needs binding horizons or explicit prices). Decides: study-2
   ambition worth designing toward, or drop.
2. **S6 — commensurability with a representation-sensitive consumer.** Manager acting on the team's
   shared representation; convention mismatch as a teammate type (G5, unverified). Objection: needs
   a scenario redesign (setup-level, now a legitimate cost). Decides: sanction the redesign now or
   after study 1. Current default: study-2 lead.
   *Costed 2026-08-05 (`S6_SETUP_CHANGE_COSTING.md`): ~1.5–2d; validity crux = agent consumer, not
   tool; per-column discrepancy-attribution task; own arm, not inside study 1. A decisive
   episode-free test exists (synthetic-format ablation, ~1h + small flash spend) — awaiting
   researcher's word.*
3. **Serving-backend drift as the NATURAL silent change.** Same model name, different backend or
   quantisation — §2.1's administrative-boundary regime, where silent change is realistic, occurring
   in the wild. Reconnects the project's original silent-change interest in its defensible form;
   `llm_interface.py:246` already captures `serving_backend`. Objection: none filed yet — never
   evaluated. Decides: worth a scoping pass.
4. **S1 — repertoire selection (reshape / re-delegate / absorb).** Decision 1's full form. RE-TAGGED
   SHELVED by the reviewer (2026-08-05): every kill leg was setup-level (correct graph, no execution
   action); reviving change named (shared tools + wrong-for-teammate graph). Constraint, not defect:
   a forced choice is not a selection. Decides: the Decision-1 override, already on the researcher's
   desk.
   *Boundary annotation (2026-08-05, per BRAINSTORM §108–109): the reshape leg violates AHT
   Assumption 2 (survey §2.1). If the reviving setup change ever arrives, S1 revives as an
   **ad hoc teaming** study, not an AHT one — recorded now so the shelf cannot quietly resurrect
   an AHT claim.*
5. **S4-arbitration — which channel wins under conflict / peer-testimony credence.** What an LLM
   manager's teammate model is made of; the reviewer called the underlying comparison "bigger than
   AHT". Objections: model-dependence (commitment-level: "teammate is an LLM"), and conflict must be
   manufactured — but the §6g conviction of the fabricated cell was REGIME-BOUND (0/221 was
   tool-swap evidence), so the cell is shelved, not buried. Decides: park until cross-model is
   authorized, or design the honest (stale) conflict version inside study 1's frame.
6. **Prospective commitment vs behaviour.** Elicit "how would you approach X", inject the commitment,
   check behaviour against it — a consumption DV cleaner than any self-report, and a novel probe of
   generative-teammate consistency. Objection (idea-level, constrains claims): testimony from a
   generator is a generated answer, not a retrieved one — weaker evidence than designs tend to
   credit. Currently a design detail inside study 1's ask cell; could be its own study.
7. **Announcement design as prescriptive interface work.** "What should a deployment tell its
   manager" — tiered content as an interface-design result. Objection: different genre from the
   descriptive program (the §91 genre question, dissolved by rescope rather than decided). Decides:
   whether the paper wants a prescriptive thread.
8. **S7 — change-vs-rate discrimination.** Shelved: null prior and unsizeability are old-setup
   evidence; the definability objection is COMMITMENT-LEVEL (depends on difference-not-deficiency —
   no rate, no matched history) and evaporates if that commitment is ever revisited. Decides:
   re-price after new-setup variance exists.

_REJECTED in researcher discussion 2026-08-05 (removable per protocol):_
- ~~**Serving-backend drift as the natural silent change.**~~ Researcher: "not a problem in a
  serious production system" — serious deployments pin serving; the 12-provider heterogeneity in
  our corpus is our rig's spot-routing artifact, and studying it would solve a self-created
  problem. Residue kept as METHODOLOGICAL HYGIENE only: provider pinning proposed for future runs;
  provider-stratification check on replicate variance (internal validity). See BRAINSTORM §106.
