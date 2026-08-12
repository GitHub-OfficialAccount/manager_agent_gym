# S6 setup-change costing — what it costs to host the shelved idea

**Status:** estimation only, per P14's standing setup-change option. No build, no runs.
Requested §104. S6 is shelved with one revival condition: a **representation-sensitive
consumer task**. This prices that condition.

---

## 1. Why the current consumer is insensitive, precisely

Every operation in `analyze_audit_artifacts` (`scenario.py:517-594`) routes through
`artifact_metric(name)` — a regex that pulls **one scalar** out of the producer's
artifact. `reconcile` then returns `abs(robust − screening)` (`:547-562`).

So the producer's entire artifact is compressed to a single number before the
consumer sees anything. Form cannot matter, because form is discarded upstream of
the consumer by construction. That is the mechanism behind CHECK-3's clean null, and
no parameter change reaches it.

## 2. The design that restores sensitivity

**The consumer must be an AGENT reading artifact text, not a TOOL parsing it.** This
is the load-bearing choice and it is where the obvious version of this design fails:
if we implement the new consumer as another deterministic tool, then *our regex* is
the representation-sensitive consumer, and the whole study measures the
experimenter's parser. That is CHECK-3's P3 objection, inverted — there the parser
was a nuisance variable, here it would be the entire effect.

`read_audit_artifact` (`scenario.py:461-473`) already returns raw artifact **content**
to a worker. So an agent-consumer is available today with no new plumbing.

**Proposed task: per-column discrepancy attribution.** The consumer reads the Batch X
Robust Audit and Batch X Rapid Screen artifacts and reports *which column* carries
the largest robust-vs-screen discrepancy.

Why this shape:
- It requires **multiple fields** from each producer (per-column counts), not one
  scalar, so the producer's layout determines recoverability.
- It requires a **join on column identity** across two producers — the literal form
  of S6's claim that joint work fails by non-comparable operands. If one producer
  writes `dti` and the other writes `debt-to-income`, the join is the task.
- The truth is deterministic and already computable:
  `_flag_count(reference, batch, column, method)` (`scenario.py:209-215`) exists per
  column for both methods. No new ground-truth machinery.
- The consumer's **answer is a single token** (a column name), so the DV extraction
  is trivial and does not reintroduce a parser confound. The representation
  sensitivity lives upstream, in what the consumer had to read; the DV itself is
  categorical and clean.

**Producer contract change required:** artifacts must carry per-column detail. They
must NOT carry it in a fixed template — the natural format variation (38 shapes on
audit, §48) is the phenomenon, and normalising it would destroy the IV. The contract
asks for per-column values and says nothing about how to lay them out.

Note on the repository's core-tool rule: this does **not** remove a tool from anyone.
Every worker keeps its full toolset; the new task simply has no single-call shortcut,
so composition happens in the agent. Nobody is switched off, which is what the rule
protects.

## 3. Cost

| item | estimate |
|---|---|
| consumer task spec + deterministic truth (reuses `_flag_count`) | 0.5d |
| producer artifact contract change (per-column detail, no template) | 0.25d |
| consumer-answer scoring + the format-feature extractor for the IV | 0.5d |
| validation that the task is answerable at all from well-formed inputs | 0.5d |
| **total** | **~1.75d, call it 1.5–2d** |

Cheaper than the ~2–3d replacement perturbation because the ground truth, the
artifact reader, and the scoring harness all already exist. The genuinely new work is
one task definition and one contract change.

## 4. DAG impact and coexistence

The new task attaches where `reconcile` attaches — dependencies
`(audit_<batch>_robust, audit_<batch>_screen)` — so it is a sibling of the existing
reconciliation, not a replacement, and the graph stays a DAG with no restructuring.

**But it should NOT coexist inside study 1's cells.** Adding tasks changes the
manager's workload, timestep budget, and action counts. Study 1's primary DV is
`rerouted_share`, whose §89-clean estimate is anchored to the corpus baseline; adding
a task to every cell holds the change constant *across cells* but breaks comparability
*with the corpus*, which is where the +0.611 estimate and CHECK-2's variance figures
come from. Both would need re-deriving on the new graph.

**Recommendation: its own scenario variant / own arm.** Study 1 runs on the current
graph and keeps its corpus anchor; study 2 runs on the extended graph. The cost of
separation is that study 2 cannot borrow study 1's variance estimates, which it
cannot anyway — P14 already says those get re-priced once new-setup runs exist.

## 5. Cheapest smoke, and the mechanical property that could fake it

**The smoke needs no episodes at all.** The corpus already holds >1,000 audit
artifacts in many natural formats. Feed *existing* artifact pairs to the proposed
consumer prompt offline and measure whether accuracy varies with producer format.
Cost is one consumer call per pair, not a 32-timestep run — roughly two orders of
magnitude cheaper than an SSR, and it uses data we already paid for.

**P3 — three mechanical properties that could fake representation sensitivity, and
what separates each:**

1. **Our own parser.** Avoided by construction: the consumer is an agent, the DV is a
   single token. Stated first because it is the one that would invalidate everything.
2. **Format correlates with producer trace.** This is not hypothetical — CHECK-3
   measured 18 of 20 JSON-shaped operands coming from `zscore`-trace producers. So a
   format effect could be the perturbation showing through form, exactly as in
   CHECK-3. Separator: stratify by producer trace, upstream-only, before reading
   anything.
3. **Length / truncation.** A longer artifact may be truncated or simply harder,
   making "format" a proxy for length. Separator: control artifact length across
   format strata, or report the effect within length bands.

**The clean separating test, which I would run before the corpus smoke:** a
**synthetic-format ablation**. Take one set of per-column numbers, render it in k
formats (JSON dict, `metric:` lines, prose sentence, markdown table, mismatched
column labels), hold information content *identical by construction*, and measure
consumer accuracy across renderings. Any difference is attributable to form alone,
because content, length, and provenance are all fixed. This is the check that decides
whether the idea is real; the corpus smoke then tells us whether the effect survives
in naturally-occurring formats, which is a different and weaker question.

Cost of the ablation: ~1 hour to write, k×n consumer calls, no episodes.

## 6. What this costing does not establish

- It prices the *condition* S6 needs, not S6's value. A representation-sensitive
  consumer makes the question askable; it does not make the answer interesting.
- The ablation could show sensitivity that never occurs naturally — the corpus smoke
  exists precisely because a synthetic effect and a natural one are different claims.
- The estimate assumes the consumer task is answerable by the current worker model
  from well-formed inputs. That is what the 0.5d validation line buys, and if it
  fails, the design needs an easier task rather than more days.
- No part of this has been built or run.
