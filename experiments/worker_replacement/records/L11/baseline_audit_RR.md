# Attacking the episode baseline's two load-bearing claims (RR)

LS asked for (a) the request→response pairing assumption broken if it can be, and (b) the
baseline's transferability checked rather than assumed.

**Both attacked. (a) the assumption is FALSE and the tail is inflated by ~a third — but the
CONCLUSION survives. (b) transferability holds on the axis LS worried about, measured.**

## (a) The pairing assumption is false in 2 of 18 bundles, and severe where it holds

Walking each actor stream in timestamp order and counting concurrently-open requests:

```
run_cell1_seed23.json    22 requests, 12 began while another was open   54.5%
run_cell1_seed3.json     22 requests, 18 began while another was open   81.8%
the other 16 bundles     strictly alternating
```

**Not an edge case where it occurs — the majority of calls in those two bundles.** FIFO pairing
matches `request[i]` to `response[i]`, which is correct only if responses return in order; where
they don't, one duration is too long and its partner too short.

### Effect on the headline

```
corpus                    n    median      p90      p99      max    >180s
ALL 18 (LS's method)    394     42.1s   180.8s   716.8s   956.2s   10.2%
16 clean bundles        352     37.7s   138.1s   438.3s   715.1s    6.5%
```

**The median is robust (42.1 → 37.7); the TAIL is not, and the tail is the entire claim.**
p99 falls **39%**, max **25%**, and the over-180s rate goes 10.2% → **6.5%**.

**The conclusion survives and the magnitude does not.** 6.5% of manager calls exceeding a 180s
timeout is still material and still lands in most episodes, so **blocking the next run on the
timeout is still right** — but the p99 that made it vivid is overstated by nearly 40%.

### A second finding LS did not ask about, and it bounds the claim further

```
structured_llm_request  actor_type='manager'   396
structured_llm_response actor_type='manager'   394
worker call durations                          NONE FOUND
```

**Every logged call is the MANAGER's. No worker call duration exists anywhere in the bundles.**
So "394 successful model calls" is **manager calls only**, and the workers — which do the Basel
arithmetic, the heavier reasoning — are **unmeasured**. The timeout exposure could be larger or
smaller; nothing in the corpus says. **The claim should read "of manager calls".**

### Reconciliation note

My figures on the same 18 bundles (median 42.1s, p99 716.8s, max 956.2s, 10.2% over 180s) differ
from LS's (40s, 636s, 876s, 7.1%). Same direction, different levels — **probably their
"successful calls" filter against my raw pairing.** Worth reconciling before either is quoted;
neither of us should assume it is rounding.

## (b) Transferability holds on the axis of concern, measured

If per-call duration were driven by prompt size, a different portfolio mix could break transfer.
Measured over the 16 clean bundles:

```
n = 352      prompt size: median 35,419 chars, range 23,524 – 40,983  (1.7x)
correlation(duration, prompt size)   r = +0.035

smallest prompt quartile   28,028 chars   median 44.2s   >180s 6.8%
largest  prompt quartile   39,033 chars   median 53.1s   >180s 9.1%
```

**Duration is essentially not prompt-driven.** A 1.7× spread in prompt size moves median
duration ~20% and the timeout rate from 6.8% to 9.1% — **weak but not zero**, so the honest form
is *small, measured, and bounded* rather than *no caveat*.

**So the baseline transfers to the `partial` run on this axis**, which is the mechanism LS named.
The arrangement keeps the same 9 segments, 4 workers and horizon 22, so prompt size should barely
move at all — and even a 1.7× move would cost ~20%.

## On LS's proposed generalisation

*"State a number's construction before building on it applies to thresholds in code, not only to
figures in records"* — **right, and I would put it more strongly.** A threshold is a **claim
about a distribution**: 180s asserts that calls finish inside it. Shipping one without measuring
the distribution is not an unstated construction, it is **an unmeasured assertion**. The rule
that follows is sharper than the provenance one:

> **A threshold names the distribution it was derived from, or it is a guess with a number on it.**

`180` and `630` were never derived from anything, and the corpus says one of them would have
killed 6.5% of manager calls.
