# Scoop & Recency Check — external deep-research report (received 2026-08-06)

_Provenance: commissioned by the researcher from a dedicated deep-research agent, using the
lead-scientist-authored brief (four-property verdict lines; three-section output; queries on
record). Saved verbatim below. **Quotes in this report are NOT record-grade until verified at
primary source** — the report itself flags FlyRoute (2605.22057), Self-Healing Agentic
Orchestrators (2606.01416), and Registry-Governed Agent Lifecycle (2607.00345) quotes as
subagent-sourced and unfetched. Verification tasked to reviewer-reproducer; see BRAINSTORM §131.
Nothing below enters STUDY1_FOUNDATION.md until the verification pass returns._

_**VERIFICATION PASS APPLIED (2026-08-06, reviewer-reproducer; full results BRAINSTORM §133).
The headline "no ≥3/4 match" conclusion STANDS. Three corrections to the text below:**_

1. _**DRAMA "Replacement" scenario: FALSE.** The string "Replacement" does not appear in v1.
   DRAMA v1 stages Agent Dropout (removal; team size falls) and Agent Addition (introduction;
   size rises) as separate scenarios — never one-for-one, never size-constant. Do not cite the
   report's "It explicitly stages a 'Replacement' scenario" sentence._
2. _**DRAMA "no capability profile": FALSE.** v1 states twice that affinity evaluations
   "consider factors such as agent capabilities, location, and current workload". Correct
   characterisation: DRAMA's allocator reads a single always-accurate capability attribute; it
   has no unreliable, absent, or competing channel about the newcomer, and no manipulation of
   channel availability. Verdict 2/4 → 2.5/4; the wedge — (2) inheritance (verified absent) +
   (3) imperfect multi-channel interface — is unchanged._
3. _**Quote status:** DRAMA (4/5 quotes; cite v1 only, arXiv:2508.04332v1), MA-Gym (both),
   FlyRoute, and ClawMark quotes are now VERIFIED at primary source. 2607.00345 and 2606.01416
   exist and titles match, but their quotes remain UNVERIFIED._

---

# Scooping & Recency Check: Open Ad Hoc Teamwork with LLM Agents

## TL;DR
- **No published or preprint work fully matches your four-property intersection.** The closest overlap is **DRAMA** (arXiv:2508.04332), which stages a mid-workflow, exogenously-triggered "Replacement" event and re-allocates tasks under deterministic scoring — but it matches only properties (1) and (4), and crucially lacks (2) successor state inheritance and (3) imperfect information channels about the newcomer. Your integrated scenario appears novel and unclaimed.
- **The problem you study has been explicitly named as open** by the "Manager Agent" position paper (arXiv:2510.02557, DAI '25), and the two sub-problems you rely on — routing from stale/unverified capability declarations, and inferring a teammate from its trace — are each attacked in isolation by separate 2025–2026 works (FlyRoute, ReCollab, the A2A/MCP staleness literature), but never combined with an exogenous swap plus state inheritance.
- **Deterministic manager benchmarks are emerging fast:** ClawArena-Team and ClawMark both use rule-based, no-LLM-judge scoring and both stage mid-episode *exogenous* updates, but neither swaps a worker agent — they mutate tasks/environment, not team composition.

## SCOOP-RISK (items matching ≥3 of the 4 properties)
**None found.** No single work matches three or more of: (1) allocation decision held by one manager agent; (2) newcomer inherits persistent workflow state written for its predecessor; (3) manager has information channels about the newcomer beyond observed behavior; (4) replacement is exogenous. The highest-overlap item, DRAMA, matches only (1) and (4). This is the central finding of the scoping check: the specific intersection is open.

---

## SECTION 1 — FOUND AND RELEVANT

### Q1 — Scooping check (highest priority)

**DRAMA: A Dynamic and Robust Allocation-based Multi-Agent System for Changing Environments** — Naibo Wang, Yifan Zhang, Sai Liu, Xinkui Zhao, Guanjie Cheng, Yueshen Xu (Zhejiang University / Xidian University). arXiv:2508.04332. Venue is genuinely dual: the arXiv v1 PDF carries AAAI 2026 formatting and copyright ("Copyright © 2026, Association for the Advancement of Artificial Intelligence"), while a CVPR 2026 poster page lists it under the retitled name "DRAMA: Next-Gen Dynamic Orchestration for Resilient Multi-Agent Ecosystems in Flux." URL: https://arxiv.org/abs/2508.04332
- **Mechanics:** DRAMA separates a centralized "control plane" (global monitoring + planning) from a "worker plane" of autonomous LLM agents. Both agents and tasks are abstracted as resource objects with lifecycles; the planner assigns tasks via an *affinity* score computed from an agent's available workload capacity and its predicted spatial (Euclidean) distance to the task, solved globally with a Dual-Capacity Hungarian Assignment. When an agent drops out, a decentralized takeover module reallocates the affected agent's *unfinished tasks* to peers and triggers re-execution. It is evaluated deterministically in a VirtualHome/C-WAH embodied setting (Average Steps, Conflict Rate, Throughput) with no LLM judge, against baselines including AgentVerse-Static/Dynamic, CoELA, MCTS, and ProAgent. It explicitly stages a "Replacement" scenario (an agent leaves and is replaced by a new agent at a different location).
- **Relevant sentences (quoted in full):** "The control plane enables real-time monitoring and centralized planning, allowing flexible and efficient task reassignment as agents join, depart, or become unavailable, thereby ensuring continuous and robust task execution." And: "The worker plane comprises a cluster of autonomous agents, each with local reasoning, task execution, the ability to collaborate, and the capability to take over unfinished tasks from other agents when needed." And: "To our knowledge, DRAMA is the first MAS framework capable of supporting agent dropout scenarios." The removal event itself is randomized, not scheduled at fixed points: "At a randomly selected step between 5 and 10, one agent is randomly removed from the environment (simulating a crash or disconnection), leaving the remaining agents to complete the task." (Note: a later retitled version describes aligning structural changes "to fixed progress ratios of the overall task execution"; the two arXiv versions differ on this detail — verify against the version you cite.) Reported gains: "DRAMA achieves a 17% improvement in runtime efficiency and a 13% reduction in resource consumption compared to existing frameworks, while maintaining superior robustness and adaptability under frequent agent turnover."
- **Verdict:** Has (1) [centralized single-planner allocation] and (4) [exogenous, externally-triggered replacement]. Lacks (2) [peers *re-execute* the unfinished task; the successor does **not** inherit the predecessor's persistent internal/workflow state] and (3) [the planner uses only workload + distance; **no** capability profile, self-report, stale registry, or interrogation]. **2/4 — closest prior art, and the two missing properties are exactly your novelty.**

**Orchestrating Human-AI Teams: The Manager Agent as a Unifying Research Challenge** — Charlie Masters, Advaith Vellanki, Jiangbo Shangguan, Bart Kultys, Jonathan Gilmore, Alastair Moore, Stefano V. Albrecht (DeepFlow). arXiv:2510.02557 (2025); Conference on Distributed Artificial Intelligence (DAI '25), ACM DOI 10.1145/3772429.3772439. URL: https://arxiv.org/abs/2510.02557
- **Mechanics:** A position/framework paper that formalizes workflow management as a Partially Observable Stochastic Game in which an "Autonomous Manager Agent" decomposes goals into task graphs, allocates tasks to human and AI workers, monitors progress, and adapts. It "identif[ies] four foundational challenges: (1) compositional reasoning for hierarchical decomposition, (2) multi-objective optimization under shifting preferences, (3) coordination and planning in ad hoc teams, and (4) governance and compliance by design," and releases MA-Gym, an open-source simulator, evaluating GPT-5-based manager agents across 20 workflows. Some metrics are deterministic (constraint adherence, completion time) but others use LLM rubrics — so it is **not** a purely deterministic-scored benchmark.
- **Relevant sentences (quoted in full):** "Because the team composition is not fixed, this entire process must occur under the challenging conditions of ad hoc teamwork ..., where the Manager Agent must be able to collaborate with new teammates without pre-coordination between agents (such as prior joint training)." And: "The Manager Agent must be able to quickly infer the skills, knowledge, and preferences of workers based on limited interactions, and flexibly adapt how it communicates and coordinates with workers."
- **Verdict:** Has (1) [single manager agent holding allocation]; partial (3) [manager infers worker skills from limited interaction — an information channel beyond raw behavior, but no stale profile or self-report registry]. No (2); (4) is only generic "team not fixed," not a studied exogenous swap. **~1.5/4 — states your research question as an open problem, directly supporting your novelty.**

**FlyRoute: Self-Evolving Agent Profiling via Data Flywheel for Adaptive Task Routing** — arXiv:2605.22057 (2026 preprint; author list/date to be verified at primary source). URL: https://arxiv.org/abs/2605.22057
- **Mechanics:** Models task routing from an agent capability profile that begins as a possibly-inaccurate developer-provided seed description and is refined ("learned description") from accumulated success examples — a data flywheel. Directly addresses the "declared profile is unreliable; learn the true capability" sub-problem underlying your channel (3).
- **Relevant sentence (quoted in full):** "Seed description $d_i^{seed}$: the natural-language description provided by the developer at registration. This may be incomplete or inaccurate, but it serves as the initial signal for cold-start routing." (Quote via subagent extraction — verify against the primary source.)
- **Verdict:** Partial (1) [routing] and partial (3) [unreliable declared profile refined by observation]. No (2), no (4). **~1.5/4 — closest work on the stale/unverified-profile sub-problem, but no exogenous replacement and no state inheritance.**

**ReCollab / Collab: Retrieval-Augmented LLMs for Cooperative Ad-hoc Teammate Modeling** — Conor Wallace, Umer Siddique, Yongcan Cao. arXiv:2512.22129 (Dec 2025), cs.MA/cs.AI/cs.LG. URL: https://arxiv.org/abs/2512.22129
- **Mechanics:** Uses an LLM as a "world model" over teammate behavior: Collab classifies an unseen partner's type from a behavior rubric derived from short trajectory features; ReCollab adds retrieval-augmented generation over an offline labeled trajectory database to stabilize the classification, then selects a best-response policy from a library. Evaluated in cooperative Overcooked with a contributed labeled dataset of five teammate types.
- **Relevant sentence (quoted in full):** "Large language models (LLMs) offer a flexible alternative: by mapping short behavioral traces into high-level hypotheses, they can serve as world models over teammate behavior."
- **Verdict:** Relevant to your "infer the newcomer from its observable trace" channel, but it is a single ad hoc agent (not a manager allocating), uses only observed behavior (no self-report/profile), no exogenous replacement, no state inheritance. **~0.5/4 — tangential; the strongest recent LLM-AHT teammate-modeling paper.**

### Q2 — LLM orchestration with runtime team changes

**Autonomous Topology Mutation (ATM): Safe Runtime Restructuring for Multi-Agent LLM Systems** — arXiv:2607.20488 (2026). URL: https://arxiv.org/abs/2607.20488
- **Mechanics:** A runtime team-mutation mechanism that monitors a six-signal "Bottleneck Index"; when a threshold is breached it *factorises* an overloaded agent into specialised sub-agents and hot-swaps the parent into a coordinator role, gated by three formal invariants (capability monotonicity, state-routing completeness, shadow-before-live). Evaluated on 720 DeepSeek-V3 task runs with deterministic tool stubs. **(a) Change initiator:** the orchestrator itself (telemetry-driven) — endogenous, not exogenous. **(b) Information about new agents:** capability sets derived from the parent (invariant I1). **(c) Evaluation:** deterministic tool stubs.
- **Relevant sentence (quoted in full):** "ATM differs in exactly this respect: it does not merely repair outputs or arguments; it changes the agent-team structure under telemetry-driven overload detection and the three formal ..."
- **Verdict:** Has (1) [coordinator], deterministic eval. Fails (4) [self-initiated]; no (2)/(3) in your sense. Useful as a 2025–2026 successor to AgentVerse/DyLAN on the "system changes its own composition" side.

**LATTE: Improving the Efficiency of Language Agent Teams with Adaptive Task Graphs** — arXiv:2605.06320 (2026). URL: https://arxiv.org/abs/2605.06320
- **Mechanics:** Defines graph-mutation operators (Discover, Assign, Claim, Complete, Release, Close, Verify) with pre/postconditions; a hybrid model where worker agents propose structural graph modifications and a lead orchestrator accepts/rejects, preserving global consistency.
- **Relevant sentence (quoted in full):** "We introduce a two-tier coordination model in which worker agents propose structural modifications to the graph and a lead orchestrator accepts or rejects them, preserving global consistency while enabling local adaptability."
- **Verdict:** Has (1). Composition changes are system-initiated (endogenous). No (2)/(3)/(4). AgentVerse/DyLAN successor.

**Multi-Agent Collaboration via Evolving Orchestration ("Puppeteer")** — Yufan Dang, Chen Qian et al. (Tsinghua / SJTU / Siemens / Tencent Robotics X). arXiv:2505.19591; published at NeurIPS 2025 (v2 revised 21 Oct 2025). URL: https://arxiv.org/abs/2505.19591
- **Mechanics:** A centralized orchestrator dynamically sequences agents and uses reinforcement learning to update its policy from completed-task feedback, promoting effective agents and pruning less useful ones over time.
- **Relevant sentence (quoted in full):** "As the task progresses, the orchestrator adaptively promotes more effective agents while removing those that are less useful, analogous to a puppeteer learning to skillfully pull ..."
- **Verdict:** Has (1). Composition change is orchestrator-initiated (endogenous). No (2)/(3)/(4). Direct DyLAN successor with a named venue (NeurIPS 2025).

**AdaptOrch: Task-Adaptive Multi-Agent Orchestration** — arXiv:2602.16873 (2026). URL: https://arxiv.org/abs/2602.16873
- **Mechanics:** A router selects among four canonical topologies (parallel, sequential, hierarchical, hybrid) per task from task dependency graphs; reports a 22.9% improvement over the single best baseline on SWE-bench Verified (author-reported).
- **Relevant sentence (quoted in full):** "We present AdaptOrch, a formal framework for task-adaptive multi-agent orchestration that dynamically selects among four canonical topologies ... based on task dependency graphs and empirically derived domain characteristics."
- **Verdict:** Has (1). Endogenous topology choice. No (2)/(3)/(4). Figures are self-reported; verify.

**Multi-Agent Coordination Adaptation via Structure-Guided Orchestration** — arXiv:2605.25746 (2026). URL: https://arxiv.org/abs/2605.25746
- **Verdict:** Orchestration-structure adaptation, endogenous. Has (1). No (2)/(3)/(4). Listed for completeness as an AgentVerse/DyLAN successor.

**Practitioner side — agent registries & stale/unverified capability descriptions:**
- **Google A2A "Agent Card":** The spec defines a JSON metadata document (typically at `/.well-known/agent-card.json`) advertising identity, capabilities, and skills, and it does **not** mandate how cards are verified. Security analyses document *stale capability claims* ("If an agent card is not kept current ... client agents may route tasks incorrectly or attempt authentication that silently fails"), *agent card shadowing/spoofing*, and description-field injection ("injecting persuasive text into the card's description field could hijack task routing"). These map directly onto your "stale registry profile" and "unverified self-description" channels.
- **MCP tool-description poisoning:** A cluster of 2026 benchmarks/systems — MCPTox (45 live servers, 353 tools, 1,348 malicious cases), "When the Manual Lies" / MCP-TDP (arXiv:2605.24069), TRUSTDESC (arXiv:2604.07536), AutoMalTool, MCP-ITP (arXiv:2601.07395) — study how unreliable/malicious *capability metadata* steers an agent's decisions before any tool is invoked. OWASP classifies this as MCP03:2025. These establish that stale/unverified capability descriptions are actively studied, but from a security angle, not a task-allocation-adaptation angle.
- **LLM self-reported capability calibration:** Multiple 2026 papers document systematic overconfidence in self-reported capability/confidence — e.g., "When Planning Fails Despite Correct Execution: On Epistemic Calibration for LLM-Based Multi-Agent Systems" (arXiv:2605.23414) and "The Confidence Dichotomy: ... Miscalibration in Tool-Use Agents" (arXiv:2601.07264). These justify your assumption that a newcomer's self-descriptions are unverified/unreliable.

### Q3 — Classical (non-LLM) open ad hoc teamwork, recency

**Open-ended coordination for multi-agent systems using modular open policies** — Autonomous Agents and Multi-Agent Systems (Springer), 2025 (s10458-025-09723-7). URL: https://link.springer.com/article/10.1007/s10458-025-09723-7
- **Mechanics:** RL approach controlling one agent among a changing number of distinct others (each with an individual task), using policy blending over an online goal-inference module and a collection of learned interaction policies. Treats interaction policies as modular components so agents can be added/removed and tasks can change — an explicit "frequent agent turnover" framing.
- **Relevant sentence (quoted in full):** "This paper presents a new reinforcement learning approach to tackle collaboration in open environments controlling one agent with a changing number of distinct other agents, each with an individual task."
- **Verdict:** Recent (2025) open-AHT extension, but observation-only (no teammate communication/declaration channel), classical RL.

**Challenges in Credit Assignment for MARL in Open Agent Systems** — Alireza Saleh Abadi, Leen-Kiat Soh (Univ. Nebraska-Lincoln). arXiv:2510.27659 (Oct 2025). URL: https://arxiv.org/abs/2510.27659
- **Mechanics:** Conceptual + empirical review of how agent-openness (agents entering/leaving), task-openness, and type-openness break credit-assignment assumptions; shows openness causes credit misattribution empirically.
- **Relevant sentence (quoted in full):** "We first conduct a conceptual analysis, introducing new sub-categories of openness to detail how events like agent turnover or task cancellation break the assumptions of environmental stationarity and fixed team composition that underpin existing CAP methods."
- **Verdict:** 2025 open-systems theory; relevant framing of "agent turnover," but not a learner-with-information-channel method.

**A Game-Theoretic Framework for N-Agent Ad Hoc Teamwork** — arXiv:2506.11285 (June 2025). URL: https://arxiv.org/abs/2506.11285
- **Mechanics:** Provides a theoretical basis for modeling open multi-agent systems and a new algorithm for NAHT, positioning itself against POAM as the only prior practical NAHT solution.
- **Relevant sentence (quoted in full):** "Given the novelty of this problem, only an initial practical solution called POAM [6] has been proposed."
- **Verdict:** 2025 NAHT follow-up (likely one you do not have). Observation-based; no teammate communication/declaration channel.

**Benchmarking the Limits of In-Context Reinforcement Learning for Ad-Hoc Teamwork** — arXiv:2605.24423 (2026). URL: https://arxiv.org/abs/2605.24423
- **Mechanics:** Tests whether general-purpose in-context RL agents adapt to unseen heterogeneous teammates purely from interaction history in Overcooked; finds no consistent improvement with longer context.
- **Relevant sentence (quoted in full):** "Contrary to expectations from single-agent ICRL, where longer context windows typically enable better in-context adaptation, we observe no consistent improvement as context length increases."
- **Verdict:** 2026 AHT recency; observation/history-only channel.

**Also relevant to Q3 (information channel beyond observed behavior):** TAGET (Ad Hoc Teamwork via Offline Goal-Based Decision Transformers, OpenReview, 2025/2026) and the knowledge-based reasoning AHT work in Frontiers in AI, Vol. 9 (2026), where the agent reasons with qualitative prior-knowledge statements and can be queried by a human — but neither gives the *learner* a capability-declaration channel *from teammates*.

### Q4 — Deterministic manager benchmarks

**ClawArena-Team: Benchmarking Subagent Orchestration and Dynamic Workflows in Language-Model Agents** — Kaiwen Xiong and 6 co-authors (aiming-lab). arXiv:2606.31174 (released ~Jul 1, 2026). URL: https://arxiv.org/abs/2606.31174 — **the ID resolves** (contrary to the possibility flagged in the brief).
- **Mechanics:** Isolates the management ability of a single LLM acting as leader over a *fixed, locally-served subagent pool* (served via local vLLM), framed as a principal–agent problem. 41 multi-turn, multimodal, multi-directory scenarios, 258 evaluation rounds, 72 staged updates. Scoring is fully execution-based (Subagent-Management Score = task correctness × least-privilege/modality-routing factor); every round ships a shell command whose exit code decides pass/fail; no LLM judge. Across twelve proprietary, community-hosted, and self-hosted models, "the management bottleneck is privilege granting rather than perception (no model exceeds 50% workspace-permission precision)," "most leaderboard scores cluster within a 9.9-point band while orchestration behaviors diverge by more than an order of magnitude," and the newly released glm-5.2 is the strongest open-weight manager (SMS 50.4, 4th overall).
- **Relevant sentences (quoted in full):** "All scoring is execution-based with no LLM judge: an overall score—the Subagent-Management Score (Sms)—multiplies task correctness by a least-privilege and modality-routing factor." And: "It commands a fixed, locally served subagent pool, so score differences reflect management skill, not raw capability."
- **Verdict:** Has (1) [single LLM manager], deterministic. The "72 staged updates" mutate the workflow/tasks, not the subagent roster (pool is fixed) — so no (2)/(3)/(4). Strong Q4 match; the mid-episode change is task-level, not agent-replacement.

**ClawMark: A Living-World Benchmark for Multi-Turn, Multi-Day, Multimodal Coworker Agents** — Fanqing Meng and 48 co-authors. arXiv:2604.23781 (Apr 2026, v2 May 2026). URL: https://arxiv.org/abs/2604.23781
- **Mechanics:** A coworker-agent benchmark with a stateful sandboxed service environment (filesystem, email, calendar, knowledge base, spreadsheet) whose state mutates *between turns independently of the agent* (exogenous). 100 tasks across 13 professional scenarios, scored by 1,537 deterministic Python checkers with no LLM judge; each task is admitted to the corpus only after two independent re-runs produce bit-identical checker verdicts. The strongest model reaches 75.8 weighted score, but the best strict Task Success is only 20.0%, "indicating that partial progress is common while complete end-to-end workflow completion remains rare."
- **Relevant sentences (quoted in full):** "We present ClawMark, a benchmark for coworker-agent evaluation that combines multi-turn multi-day tasks, a stateful sandboxed service environment, exogenous between-turn environment changes, and deterministic rule-based scoring in a single executable setting." And: "Turn-level analysis shows that performance drops after the first exogenous environment update, highlighting adaptation to changing state as a key open challenge."
- **Verdict:** Deterministic + explicit *exogenous* mid-episode mutation (a (4)-flavored motif), but the mutation is to the *environment/state*, not a *worker agent*, and it is a single coworker agent, not a manager over workers. No (1)/(2)/(3) in your sense. **Strongest existing "exogenous mid-episode + deterministic" precedent — directly relevant framing for your evaluation design.**

**Self-Healing Agentic Orchestrators** — arXiv:2606.01416 (2026 preprint; verify at primary source). URL: https://arxiv.org/abs/2606.01416
- **Mechanics:** Control-plane/data-plane orchestrator that recovers from tool/agent failures under a budget; deterministic 100-task fault-injection benchmark. Preserves execution state and applies a bounded recovery action.
- **Relevant sentence (quoted, via subagent — verify):** "it preserves execution state, identifies the likely failure class, applies a bounded recovery action, and verifies whether execution can safely continue."
- **Verdict:** Has (1), deterministic. Failures are tool/execution-level, not exogenous replacement of a competent worker by a different competent worker; state preservation is task-trajectory, not successor inheritance. No (2)/(3)/(4).

---

## SECTION 2 — FOUND AND RULED OUT (with reason)

- **DyLAN** (arXiv:2310.02170), **Multi-Agent Collaboration via Evolving Orchestration** (2505.19591), **LATTE** (2605.06320), **AdaptOrch** (2602.16873), **Structure-Guided Orchestration** (2605.25746), **ATM** (2607.20488): all change team composition/topology **endogenously** (the system/orchestrator decides), violating property (4). Documented above under Q2 for completeness but ruled out as scoops.
- **Cooperation on the Fly: Language Agents for Ad Hoc Teamwork in Avalon** (arXiv:2312.17515): LLM-AHT but a peer agent in a game — no manager/allocation, no replacement, no state inheritance. Ruled out (pre-2025 and off-scenario).
- **SwapServeLLM / engine-agnostic model hot-swapping** (ACM SC'25 Workshops) and the "LLM Fallbacks / recovery layer" writeups: "swap" here is **infrastructure model hot-swapping / fallback routing for serving**, not a teammate-agent replacement in a task workflow. Ruled out (systems/serving, not AHT).
- **Decentralized adaptive task allocation** (Scientific Reports, s41598-025-21709-9): decentralized (no single manager); task allocation to LLMs but no agent replacement/inheritance/profile channel. Ruled out on (1)/(2)/(3)/(4).
- **Orchestrated multi-agents sustain accuracy under clinical-scale workloads** (npj Health Systems, s44401-026-00077-0): a manager routes tasks to workers, but workers are fixed and homogeneous; no replacement, no imperfect-info channel. Ruled out.
- **MCP tool-poisoning benchmarks** (MCPTox, 2605.24069, 2604.07536, 2601.07395): about malicious/unreliable *tool* metadata and security, not task-allocation adaptation to a swapped teammate. Ruled out of Q1 but cited under Q2 as evidence that capability descriptions are studied as stale/unverified.
- **Registry-Governed Agent Lifecycle / EDDOps** (arXiv:2607.00345, verify): formalizes registry staleness detection and version lineage — relevant to your "stale registry profile" channel — but a systems/governance paper with no manager task-allocation experiments and no replacement study. Ruled out of Q1, noted for the registry channel.
- **Knowledge Reuse of MARL in Cooperative Tasks** (PMC9025018): "adding a teammate" with policy transfer, but co-trained MARL — not ad hoc, not a manager, not LLM. Ruled out.

---

## SECTION 3 — SEARCHED BUT NOTHING FOUND (queries run, so null results are verifiable)

Lead-author queries (web_search):
1. "open ad hoc teamwork LLM agents"
2. "LLM multi-agent worker replacement mid-task orchestrator adaptation"
3. "dynamic team composition LLM agents runtime"
4. "agent turnover replacement multi-agent reinforcement learning open team"
5. "LLM agent hot swap successor agent task allocation adaptation"
6. "open ad hoc teamwork 2025 communication capability declaration teammate"
7. "ClawArena team benchmark LLM orchestrator deterministic"
8. "A2A Agent Card stale capability description reliability"
9. "ReCollab retrieval-augmented LLM cooperative ad-hoc teammate modeling"
10. "NAHT N-agent ad hoc teamwork 2026 follow-up POAM"
11. "ROTATE open ad hoc teamwork 2025 teammate generation"
12. "MCP tool description poisoning unreliable capability LLM agent"
13. "LLM self-reported capability calibration overconfidence agent"
14. "agent replacement mid-workflow orchestrator task reallocation exogenous"
15. "open ad hoc teamwork querying teammate capability declaration 2026"
16. "LLM agent onboarding new worker existing workflow persistent state"
17. "ClawMark living world benchmark exogenous between-turn mutation LLM agent"
18. "personnel turnover multi-agent reinforcement learning agent departure replacement 2025"

Subagent queries (targeted Q1 scoop-risk):
19. "agent replacement mid-task orchestrator LLM multi-agent" — no exact match
20. "worker agent replaced mid-workflow manager task reallocation LLM benchmark" — no match (returned office/workflow benchmarks such as TheAgentCompany/WorkArena, none on replacement)
21. "successor agent inherits predecessor state stale profile registry manager routing" — no match
22. "capability-aware task reallocation agent dropout replacement orchestrator self-report unverified" — no match
23. "open ad hoc teamwork LLM agents new teammate" — nearest is the Manager Agent position paper (2510.02557), which frames the problem as open

**Null-result conclusion:** No search surfaced a work in which a manager agent adapts task routing after an *exogenous* worker replacement where the successor inherits the predecessor's persistent workflow state and the manager reasons under imperfect information channels (stale predecessor profile + unverified self-report + interrogation + observed trace). The intersection is, to the best of this search, unclaimed.

---

## Recommendations
1. **Claim the four-property intersection, but position against DRAMA explicitly and early.** DRAMA is your nearest neighbor and a reviewer will find it. Foreground three differentiators: DRAMA (a) reallocates by workload+distance affinity with *no capability model*; (b) has peers *re-execute* an unfinished task rather than a successor *inheriting persistent state*; and (c) uses decentralized trust-chain recovery rather than a single manager reasoning under imperfect information. Your properties (2) and (3) are the wedge. Also note DRAMA's replacement is a *crash/disconnection* ("At a randomly selected step between 5 and 10, one agent is randomly removed"), whereas yours is a *competent-but-different successor* — a qualitatively different information problem.
2. **Cite the Manager Agent paper (2510.02557) as the explicit open-problem statement**, and FlyRoute (2605.22057) + ReCollab (2512.22129) as the two sub-problems solved in isolation. This frames your contribution as the first to combine stale/unverified declaration channels with exogenous replacement and state inheritance. Threshold that would change this: if a 2026 paper appears that adds a *capability-declaration/interrogation channel about a swapped teammate* to a manager (rather than a peer), your novelty narrows to state inheritance + deterministic allocation scoring — re-run the FlyRoute/DRAMA citation graphs before submission.
3. **Anchor your deterministic-scoring design in ClawArena-Team and ClawMark.** Both are strong, recent precedents for no-LLM-judge, execution-based scoring; ClawMark's "exogenous between-turn mutation" (and its finding that "performance drops after the first exogenous environment update") is the closest existing evaluation motif to your exogenous swap — differentiate by mutating the *worker*, not the *environment*, and by scoring the *allocation decision* against an optimal assignment rather than end-state task success.
4. **Verify the 2026 preprints before citing:** FlyRoute (2605.22057), Self-Healing Agentic Orchestrators (2606.01416), and Registry-Governed Agent Lifecycle (2607.00345) came via the subagent and were not fetched at primary source; confirm titles, authors, dates, and quotes.
5. **If you widen scope,** add the MCP tool-poisoning benchmark cluster (for the "unverified capability description" channel) and the epistemic-calibration papers (2605.23414, 2601.07264) as citations that self-reports are unreliable — these strengthen the motivation for treating the newcomer's self-descriptions as untrusted.

## Caveats
- **Venue ambiguity for DRAMA is real and confirmed:** the arXiv v1 PDF carries AAAI 2026 copyright, while a CVPR 2026 poster page lists a retitled version ("DRAMA: Next-Gen Dynamic Orchestration for Resilient Multi-Agent Ecosystems in Flux"). The v1 and v3 abstracts differ, and they describe the replacement-timing mechanism differently (v1: "randomly selected step between 5 and 10"; a later version: "aligned to fixed progress ratios"). Confirm which version/venue you cite and quote against it.
- **ClawArena-Team arXiv ID 2606.31174 resolves** (contrary to the brief's flagged possibility); its abstract and GitHub confirm execution-based, no-LLM-judge scoring, and the "72 staged updates" are task/workflow updates over a *fixed* subagent pool, not agent replacements.
- **Self-reported figures:** AdaptOrch's 22.9%, DRAMA's 17%/13%, and ClawArena/ClawMark leaderboard numbers are author-reported, not independently verified.
- **Subagent-sourced quotes** (FlyRoute, Self-Healing Agentic Orchestrators, Registry-Governed Agent Lifecycle) were not re-fetched at primary source — flagged for verification.
- This scan is broad but **not exhaustive** of closed-access or not-yet-indexed venue proceedings (AAMAS 2026, IJCAI 2026), which could contain a closer match; a final citation-graph pass on DRAMA, NAHT, and the Manager Agent paper immediately before submission is advisable.
