# S7 — Reviewer-reproducer scoped round / FINAL (verbatim, received by DM 2026-08-08): PASS

S7 SCOPED ROUND — **PASS, with one measurement you should take before the ceiling is published as a threshold, and one item where I'm declining to demand what you offered.**

════════════════════════════
(1) MC STABILITY — MEASURED. 300 DRAWS IS NOT ENOUGH FOR A THRESHOLDED QUANTITY
════════════════════════════
Your instinct was right and the number is worse than the 0.02 you worried about at the tail. I re-ran the estimator with 12 independent streams per instance:
```
seed 0  ceiling mean 0.1465  sd 0.0034  spread across streams 0.0114
seed 3         0.1603        0.0045                          0.0146
seed 6         0.1851        0.0050                          0.0203
seed 7         0.0874        0.0022                          0.0068
```
And against draw count on the worst case (seed 6):
```
draws    300 : sd 0.0029   range 0.0093
draws   3000 : sd 0.0013   range 0.0035
draws  10000 : sd 0.00045  range 0.0014
```
**At 300 draws the published ceiling moves up to ~0.02 between MC streams.** That is tolerable for a disclosed diagnostic and **not** tolerable for the quantity admission is thresholded on: an instance sitting near the eventual MDE can be admitted or flagged by the draw seed alone, which is exactly the "tie-break luck" failure your own S5 round-1 catch was about, relocated into a Monte-Carlo estimator.

It is also cheap to fix — the estimator is offline, zero model calls, and 10,000 draws costs milliseconds per instance. **Recommend `IGNORANT_DRAWS = 10_000`, with the achieved MC standard error published per row** so a reader can see the ceiling's own precision beside the value. That makes the quantity stable to ~0.0005, two orders below any plausible MDE, and the seeding-from-instance property is preserved either way.

Note this does not change any conclusion drawn so far — the band I computed (0.09–0.18) is unmoved at higher precision, and the suite median coverage share of 0.185 corroborates F1 on all 40 rather than on my 12. It changes whether a *threshold* can be applied to the number later.

════════════════════════════
(2) FLAG MECHANICS — CORRECT, AND C1 FOLDED INTO THE STRING IS BETTER THAN MY VERSION
════════════════════════════
`below_provisional_mde` per row plus `declared_mde_status` is the right shape: the row carries its own status rather than requiring a reader to join against a threshold recorded elsewhere. Putting C1's prohibition **inside the flag string** is a genuine improvement on what I asked for — I proposed a sentence in the spec, which is a note; a string that travels with every flagged row cannot be separated from the rows it governs. That is the "put the assertion in the producer" rule applied to prose.

C2 (pilot selection not conditioned on the ceiling) is not visible in this round's artifacts — it belongs to the pilot's spec rather than here, so I'm noting rather than finding it, but it should be written down before the pilot is specced or it will be decided by whoever picks the seeds.

════════════════════════════
(3) DIAGNOSTICS — v2's RETIREMENT IS PROPERLY VISIBLE
════════════════════════════
`m_successor` / `m_incumbent` / `coverage_attributable` sitting beside each other is the right way to keep a retired quantity legible: a reader who encounters M elsewhere can see immediately why it was demoted, and the comparator is in the same row rather than in a section of the record they'd have to find. Suite median coverage share **0.185** against my 12-seed 0.195 — consistent, and it confirms the split holds across the full sweep rather than in my sample.

════════════════════════════
(4) LGD — I DECLINE TO DEMAND THE RE-FETCH, WITH ONE CONDITION
════════════════════════════
I'm not asking for it, and RE's discipline is right: `PD_FLOOR_VERIFIED` means what it says, and inventing an LGD floor from memory to widen a claim is precisely the drift the labelling convention exists to stop.

**But the K3 anchoring statement must then narrow to match.** If the claim is "per-segment inputs anchored by IRB input floors" while only PD is asserted, the sentence over-claims by exactly one parameter. Narrow it to **"per-segment PD anchored by the ¶68/¶121 input floors; LGD floors exist in ¶121's table and are not asserted"** — which is both true and stronger than a vague claim, because it names what is missing. That costs nothing and needs no re-fetch. (For the record: I did see the LGD table in ¶121 while verifying PD, and generated LGD sits in 0.251–0.600, which is plausible — but "I saw a table" is not a citation and I'm not offering it as one.)

════════════════════════════
(5) THE FLAT K2 READING — CORRECT, AND IT IS THE CLEANEST RESULT IN THE ROUND
════════════════════════════
Ceiling flat across k=1..4 follows directly: under exact capacity consumption the successor takes three segments regardless, so *which* segments are strictly required does not change what an ignorant manager loses. **k is not an effect lever**, and that is now demonstrated rather than argued. It also retroactively explains why my S6 F2 fix attempt via count-bias alone reached only 12/40 — count was never the lever, which RE found empirically then and the flat curve now explains structurally.

**On the K5-vs-v3 curve:** running it before the pilot is the right order. One thing to pre-state so the result is interpretable either way — under v2, K5 moved max-effect 0.096→0.300, but v2 was ~80% capacity. **If K5 moves the v3 ceiling substantially, that is a real rescue lever; if it moves it only slightly, then the honest conclusion is that the environment's channel effect is small and no knob rescues it** — which is a design finding, not a failure, and it should be recorded as one rather than triggering a search for a fourth knob. Saying that now costs nothing and stops the outcome being reinterpreted after it arrives.

════════════════════════════
VERDICT
════════════════════════════
**PASS.** One finding: raise `IGNORANT_DRAWS` to 10,000 and publish the MC standard error per row, before the ceiling is used as a threshold rather than a disclosure. One narrowing: K3's anchoring sentence to PD only. C2 noted for the pilot spec.

**What I verified vs took on report:** verified independently — `expected_ignorant_score`'s implementation, its MC stability across 12 streams × 4 instances and across four draw counts, the capacity-respecting draw logic (including that the unstaffed branch is unreachable at cap 3 × 3 workers = 9 segments, so the `continue` is dead code today and correct to keep for other caps). Taken on report — the suite-wide median coverage share 0.185, the flag-field wiring across all 40 rows, and the flat-K2 curve values.
