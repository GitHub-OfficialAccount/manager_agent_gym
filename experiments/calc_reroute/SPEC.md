# Calc-reroute experiment — spec

The simplest environment with a **genuine, exactly-checkable tool-competence
gap**. Competence = possession of a calculator tool. A worker with `calc` gets
multi-step arithmetic right; one without does mental math and errs — graded
(easy calcs right, compounding ones wrong). Correctness is an exact numeric
match, so **no LLM judge and no fuzzy scoring** on the primary metric.

This is the tool-based analogue of `micro_reroute`: same shape, but info-in-
prompt → real tool, and groundedness → exact correctness. Establishes the
tool-competence pipeline cleanly before we add handoffs / fuzzier tools.

## Environment

**3 workers** (all gpt-oss-120b), differentiated only by whether they hold the
`calc` tool. Descriptions state who is the quantitative specialist so t=0
routing is possible:
- `quant_analyst` — **holds `calc`**. "Quantitative analyst; performs precise financial calculations."
- `credit_analyst` — no calc. "Credit analyst; qualitative assessment."
- `junior_analyst` — no calc (gains calc on reroute). "Junior analyst; general support."

**10 tasks: 8 quant (calc-dependent) + 2 qualitative.** Quant tasks are graded
in difficulty; the gap appears on the multi-step ones. Each quant task carries a
canonical expression whose evaluation is the ground truth (same arithmetic the
tool does).

| id | task | expression | answer | difficulty |
|----|------|-----------|--------|-----------|
| Q1 | CET1 ratio | `6.62/48.3` | 0.1371 | easy |
| Q2 | DSCR | `4.2/3.1` | 1.3548 | easy |
| Q3 | RWA density | `48.3/88.5` | 0.5458 | easy |
| Q4 | NPV of [100,120,150,200,240] @ 9% | `sum(cf/1.09**t)` | 606.24 | hard |
| Q5 | 5-yr CAGR 100→240 | `(240/100)**(1/5)-1` | 0.1914 | hard |
| Q6 | PV of annuity C=50, r=6%, n=10 | `50*(1-1.06**-10)/0.06` | 368.00 | hard |
| Q7 | FV compound 100 @7% for 8y | `100*1.07**8` | 171.82 | med |
| Q8 | blended rate 60/40 of 8%/13% | `0.6*0.08+0.4*0.13` | 0.1000 | med |

Qualitative (not scored for correctness; anyone can do them):
- QL1 "Summarize the bank's capital adequacy approach (no calculation)."
- QL2 "Draft the methodology/notes section for the analysis."

Tasks are independent (flat, routing-only) for v1; handoff dependencies come in
the next version.

## The `calc` tool

```python
@function_tool
def calc(expression: str) -> str:
    """Evaluate an arithmetic expression and return the exact result."""
    # safe eval via ast (numbers, + - * / ** ( ), sum-free; no names/calls)
    return str(_safe_eval(expression))
```

Real arithmetic (not simulated) — deterministic and correct. A holder calls it
during task execution (native Agents-SDK tool-calling); a non-holder cannot and
must compute in-head.

## Perturbation (reroute) — needs `ToolSwap`

At `--swap-timestep`, `calc` moves `quant_analyst → junior_analyst`. Quant tasks
should now route to `junior_analyst`.

- **control** — no swap.
- **silent** — swap, no signal, stale descriptions. Manager must detect from
  behavior (quant_analyst's numbers go wrong).
- **oracle** — swap announced with new holdings.

New harness piece: a `ToolSwap` perturbation. Tools are Python objects (not
serializable in the schedule), so `ToolSwap` carries tool **ids** (strings), and
the runner provides a `{tool_id: function_tool}` registry the registry `replace`
action resolves. (v1 fallback if that's over-engineered: a timestep-end callback
in the runner that re-registers the two agents with/without `calc` at the swap
step — no schema change. Prefer the generic `ToolSwap` if cheap.)

## Scoring — exact-match, no LLM

For each quant-task artifact: extract the worker's stated numeric answer (regex
for the final number / a small "extract the answer" pass) and compare to
`eval(expression)` within **1% relative tolerance**. Correct = 1/0. Primary
metric = fraction of post-swap quant tasks correct, by condition. Regret =
oracle − silent. (Optional: absolute relative error for a graded view.)

No groundedness judge, no quality judge on the primary metric — the whole point
of calc-first is that correctness is unambiguous.

## Metrics

- Post-swap quant-task **correctness** by condition (control / silent / oracle).
- **Routing**: who did post-swap quant tasks (did the manager reroute to the new
  calc-holder?).
- **Regret** = oracle − silent correctness.
- Detection probe (reused) for the out-of-band "did an auditor notice" signal.

Expected shape (hypothesis): control high, silent low (manager keeps routing to
now-calc-less quant_analyst → wrong numbers), oracle recovers.

## Reuse vs new

**Reuse:** engine, `AIAgent` (native tool-calling), `ChainOfThoughtManagerAgent`,
`AgentRegistry`, `ObservationPolicy`, `PerturbationSchedule`, `DetectionProbe`,
the `micro_reroute` runner/recorder structure.

**New:** (1) `calc` tool + `_safe_eval`; (2) the 10 tasks + expressions/answers;
(3) `ToolSwap` (registry replace extension + schema) or the callback fallback;
(4) exact-match scorer.

## Build order

1. `calc` tool + `_safe_eval` + unit test.
2. Scenario (workers, 10 tasks, ground-truth table).
3. **Linchpin:** a worker with `calc` vs without on the hard quant tasks —
   confirm the correctness gap (near-certain to pass, but verify + measure size).
4. `ToolSwap` (or callback fallback).
5. Runner (control/silent/oracle) + exact-match scorer.
6. Run 3 conditions × 3 seeds; read correctness + regret.
