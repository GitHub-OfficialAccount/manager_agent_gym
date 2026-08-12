# S5 — Reviewer-reproducer review (verbatim, received by DM 2026-08-08): PASS with findings

S5 REVIEW — **PASS with findings. Four items, of which two matter: assertion 4 is vacuous rather than merely negative-free, and the strict counter's comparison is exact-`>` while your probe used 1e-12 — so the probe did not exercise the production comparison.**

════════════════════════════
(1) FIDELITY TO ORIGIN RULINGS — ALL FOUR FAITHFUL
════════════════════════════
- **A1 non-nestedness** ← my S3 limitation: implemented **inside `generate()`, unconditional**, which is what I asked for — it converts the derived property into an asserted one and does not depend on `COVERAGE_SIZE` staying constant. ✓
- **A5 id opacity** ← my S2 F1+F4: instance-wide, tokens drawn from the instance's own lattice **and** method names, and the negative fires on `irb_corporate_quant_0` with the offending tokens named in the message. ✓
- **A6 zero-fallback** ← my S4 F1: both halves present — the generator-side sampling constraint *and* the guarding assertion, which is the distinction I asked for (excluded by construction, not merely rejected). The 100-seed sweep showing 44 zero-SA-fallback segments arising and 0 IRB-approved is exactly the non-vacuity evidence that claim needed. ✓
- **A3 strict O3** ← §132/§134 lineage: the strict form is implemented and the tie-inclusive count is *retained and printed* rather than discarded, which keeps the gap auditable. ✓

Your round-1 catch is the strongest item in the record. Counting tie-inclusive routing where the honest number is strict would have overstated K2 threefold in every published instance, and K2 is the knob whose disclosure is the defence against manufacturing the headline. The k=3 discriminating negative — sitting *between* the two counts, so the old counter passes and the new one rejects — is what makes the fix falsifiable rather than merely different.

════════════════════════════
(2) THE STRICT COMPARISON — CORRECT TODAY, FRAGILE BY CONSTRUCTION, AND YOUR PROBE TESTED A DIFFERENT COMPARISON
════════════════════════════
Production is a bare float `>`: `all(score_for(seg, successor) > score_for(seg, other) for other in others)`. **No tolerance.**

It is correct *today* for a reason worth writing down: two workers score identically only when they take the same branch of `attainable_report`, and both branches call the same function with the same arguments, so equal scores are **bit-identical**, and `>` is exactly false. There is no different-path-same-value case in the current implementation.

**But the failure mode is asymmetric and lands on the wrong side.** If `s` ever acquires a path where two mathematically equal scores differ by an ulp — any accumulation, any ordering difference — `>` counts that segment as **strictly required**, and K2's published count overstates. The strict form exists precisely to prevent overstatement, so its comparison should fail *safe*, toward under-counting. One line: `> other + TIE_EPS`, with TIE_EPS documented as "a difference below this is a tie, and ties are never strict requirements."

**And the probe point, which is the §A rule shape in your own check:** you probed with 1e-12; production compares exactly. **A probe using a different comparison than the code cannot detect a tie-vs-strict boundary error** — it verifies a reimplementation. Not a defect in the outcome (both agree on this instance, since ties are bit-identical), but the probe should call `successor_routing_counts` rather than re-derive the comparison, or it is the third instance of the pattern in a checker rather than a test.

════════════════════════════
(3) ASSERTION 4 — MY VERDICT: RE IS RIGHT THAT NO NEGATIVE EXISTS, AND THE REASON IS THAT THE ASSERTION IS VACUOUS
════════════════════════════
I accept the conclusion and reach a stronger statement of it. Assertion 4 checks both rosters are serviceable. **Under a universal fallback every worker can act on every segment via SA — the spec says so itself** (*"under a universal fallback the set-cover half of O3 is trivially true, so the oracle-routing condition is O3's entire content"*). So assertion 4 cannot fail for reasons that have nothing to do with assertion 6: it is true by SA's universality alone. Assertion 6 forecloses one *additional* route to worthlessness, but even without it, "serviceable" is satisfied.

**A vacuous assertion is not free.** It reports six assertions where five can fire, and a reader counting coverage gets a wrong number. Two honest options: delete it with the reason recorded, or — better — **restate it as the canary for assertion 6's premise**: *every segment is serviceable at score > 0 by at least one worker in each roster*. Under A6 that is implied, so it still cannot fail today — but it would fail the moment A6 were relaxed or its sampling constraint regressed, which makes it a genuine guard rather than a restatement of SA. That converts a vacuous line into a cheap regression detector on the constraint I care most about.

════════════════════════════
(4) SWEEP AND HOOKS — SOUND
════════════════════════════
44 chances / 0 violations across 100 seeds is real non-vacuity, and it is the right shape: it demonstrates the *sampling* excludes the condition rather than that the assertion rejects it. Injection hooks drive production paths — the id negative in particular goes through the real generator rather than a hand-built roster, honouring the S2 carry-forward. The distinctness check (5 markers across 6 cases, no catch-all) is the right guard against one assertion masquerading as several; the 6-cases/5-markers gap is correctly explained by 3 and 3b sharing marker 3, which is the point of 3b.

════════════════════════════
(5) SCHEMA v2 EVENT BLOCK — CORRECT
════════════════════════════
`roster_pre_swap` excludes the successor, `roster_post_swap` excludes the predecessor, from a 4-worker pool → **3 active before and 3 after**, constant n as §5 requires, and the two rosters are derived from one list rather than authored separately (so they cannot drift). ✓

════════════════════════════
(6) TWO THINGS NEITHER OF US LOOKED FOR
════════════════════════════
**F-A — `k` defaults to 1, and the default instance's strict count is 2 of 9.** `min_successor_routed: int = 1`. So the shipped guarantee is that **one** segment strictly requires the successor; the observed instance has two. That is a floor low enough to be worth a second look: with 2 of 9 segments strictly requiring the successor, the entire allocation-regret consequence of ignoring the arrival is bounded by those two segments' contribution. §5 warns about k too *high* (regret degenerates to "did the manager notice"); the opposite risk is not stated and is the one the default sits near. **The acceptance output should print k alongside the strict count** — right now it prints the count and not the threshold, so a reader cannot see how much headroom the assertion had. S6's sweep should report regret headroom as a function of k, which is the K2 curve the disclosure rule already requires.

**F-B — `_designate_swap_pair` systematically selects the lexicographically-first asset class with exactly two holders.** Deterministic and correct for its purpose, but it means the swapped pair's shared class is chosen by **alphabetical order over class names**, not by the seed. Across instances that biases which asset class the event concerns — `bank` sorts before `corporate`, `retail`, `sovereign`, so any seed whose lattice gives `bank` two holders will always swap on `bank`. If segment mixes differ by class (they do — applicability and SA divergence are class-dependent), the event is correlated with a specific class across the suite in a way nothing reports. **Not a defect** — determinism is required — but it is a generator property that moves the spread and is therefore covered by §4.3's disclosure rule: **publish the swapped pair's shared class per instance**, and check in S6 whether it is uniform across the suite. If it is, the benchmark's event is always about one asset class, which is a scope limit worth knowing before 45 episodes.

════════════════════════════
VERDICT
════════════════════════════
**PASS.** Findings: (3) assertion 4 restated as A6's canary or deleted with reason; (2) tolerance on the strict comparison and the probe calling the production function; F-A print k and sweep it in S6; F-B publish the swap class per instance. None blocks S5; all four are cheap and belong before S6 generates a suite.

**What I verified vs took on report:** verified independently — all six assertions against their origin text in BACKLOG and §2/§4.3/§5/§4.1, `successor_routing_counts` and its exact-`>` comparison read in source, `_designate_swap_pair`'s selection rule, `min_successor_routed`'s default, the roster derivation, and the acceptance output's marker distinctness. Taken on report — the 100-seed sweep counts and suite parity.
