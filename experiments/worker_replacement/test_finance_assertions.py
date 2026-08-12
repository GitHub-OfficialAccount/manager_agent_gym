"""S5 acceptance — the six generation-time assertions.

Every negative case must be REJECTED, and with a DISTINCT message: a single
catch-all would let one working assertion masquerade as six. Each case is
constructed through the generator's own paths — the semantic-id case drives an
injected id BUILDER rather than a hand-written id list, per the §A rule and the S2
carry-forward, because a hand-written list would bypass the code under test.

Case 5 additionally demonstrates the GENERATOR-SIDE constraint, not just the
assertion: across a seed sweep the default sampling never produces a
zero-SA-fallback IRB segment, while such segments demonstrably occur in the pool.
An assertion guarding a condition that could never arise proves nothing.

Run:  python3 -m experiments.worker_replacement.test_finance_assertions
"""

from __future__ import annotations

from . import finance_generator as gen

SEED = 101


def expect_rejection(
    label: str, marker: str, seed: int = SEED, **kwargs
) -> tuple[bool, str]:
    """Generate with `kwargs`; expect InstanceAssertionError whose message has `marker`."""
    try:
        gen.generate(seed, **kwargs)
    except gen.InstanceAssertionError as exc:
        message = str(exc)
        return (marker in message), message
    except Exception as exc:  # a different failure mode is NOT a pass
        return False, f"wrong exception type {type(exc).__name__}: {exc}"
    return False, "generate() returned an instance — no assertion fired"


def main() -> int:
    failures: list[str] = []
    print("S5 — generation-time assertions\n")

    # --- the positive case: a default instance must GENERATE ----------------
    print("positive control — default instance generates cleanly:")
    instance = gen.generate(SEED)
    print(f"   [ok] schema {instance['schema']}, "
          f"{len(instance['segments'])} segments, {len(instance['workers'])} workers")
    event = instance["event"]
    print(f"   event: {event['predecessor_id']} -> {event['successor_id']} "
          f"at t={event['t_swap']}")
    # BOTH counts printed so the gap stays visible (LS review of S5). Assertion 3
    # and K2 use STRICT; tie-inclusive counts segments any worker could have served
    # and would let an inert arrival pass on tie-break luck.
    strict, tie_inclusive = gen.successor_routing_counts(instance)
    k = instance["parameters"]["min_successor_routed"]
    print(f"   successor required — STRICT {len(strict)} {strict}  "
          f"(threshold k={k}, headroom {len(strict) - k})")
    print(f"                        tie-inclusive {len(tie_inclusive)} {tie_inclusive}")
    print(f"   swapped pair's shared class: {instance['event']['swap_shared_class']!r} "
          f"— uniform across a suite is a suite-level regularity S6 checks")
    print(f"   recorded for K2: "
          f"{event['successor_strictly_required_segments']} (strict)")
    if event["successor_strictly_required_segments"] != strict:
        failures.append("recorded K2 count is not the strict count")
    if len(strict) >= len(tie_inclusive):
        print("   note: no tie-inclusive inflation on this instance")

    # Locate a zero-SA-weight segment (sovereign rated AAA to AA-) to force for
    # case 6. Seed 101 no longer draws one under the five-class lattice, so the
    # seed is SEARCHED rather than hard-coded — a hard-coded seed that stops
    # containing the fixture turns a real negative case into a silent skip.
    zero_fallback, zf_seed = [], SEED
    for candidate_seed in range(200):
        candidate = gen.generate(candidate_seed)
        hits = [
            x for x in candidate["segments"]
            if gen.sa_risk_weight(x["asset_class"], x["rating"]) == 0.0
        ]
        if hits:
            zero_fallback, zf_seed = hits, candidate_seed
            break
    print(f"   (case 6 fixture seed: {zf_seed})")
    print(f"   zero-SA-fallback segments present in the pool: "
          f"{[s['segment_id'] for s in zero_fallback]} "
          f"(none of them IRB-approved: "
          f"{all(not s['irb_approved'] for s in zero_fallback)})")

    # --- the five negative cases -------------------------------------------
    print("\nnegative cases — each must be rejected, with a DISTINCT message:")
    cases = [
        (
            "1 nested lattice",
            "ASSERTION 1",
            # ★ FIXTURE CORRECTED 2026-08-09. It used UNEQUAL-size sets —
            # ("bank",) against pairs — and a guard added since then rejects those
            # FIRST: "coverage_override sets must be EQUAL SIZE; unequal ones can
            # nest, and non-nestedness is what makes the lattice measure anything."
            # So the case never reached ASSERTION 1 and this acceptance had been
            # failing, unreported, on a marker that could no longer be produced.
            #
            # Same family as the four stale records: the generator gained a guard
            # and a committed artefact still describes the old ordering.
            #
            # Equal-size sets nest only when IDENTICAL, so that is the case now
            # used. Verified reachable: it raises ASSERTION 1 (non-nestedness),
            # while equal-size pairwise-distinct coverage generates cleanly — so
            # the fixture still discriminates rather than merely raising.
            dict(n_workers=4, coverage_override=[
                ("bank", "corporate"), ("bank", "corporate"),
                ("corporate", "retail"), ("sovereign", "retail"),
            ]),
        ),
        (
            "2a capacity INFEASIBLE (roster x cap < segments)",
            "ASSERTION 2a",
            # Assertion 2 INVERTED with the S7 ruling: capacity must now BIND, not
            # be absent. The old negative (max_timesteps=1) targeted the retired
            # form and silently stopped firing — it passed generation and was
            # caught only because the distinctness check counts markers.
            dict(capacity_cap=2),
        ),
        # ★ THE 2b CONTROL IS REMOVED, NOT DISABLED (L14-b). It drove
        # `capacity_cap=9` and required ASSERTION 2b to fire. Assertion 2b is
        # RETIRED -- the runtime enforces no cap, so a check that the cap binds
        # asserts a property of a constraint nothing has. Keeping the control with
        # its expectation flipped would be worse than deleting it: it would read as
        # evidence that non-triviality is still certified somewhere, and it is not.
        # See ALLOCATION_DIFFICULTY_RETIRED in finance_generator.
        (
            "5 semantic worker ids",
            "ASSERTION 5",
            dict(id_builder=lambda seed, index: f"irb_corporate_quant_{index}"),
        ),
    ]
    if zero_fallback:
        cases.append((
            "6 zero-SA-fallback IRB segment",
            "ASSERTION 6",
            dict(seed=zf_seed,
                 force_irb_segment_ids=(zero_fallback[0]["segment_id"],)),
        ))
    else:
        print("   [FAIL] seed has no zero-fallback segment to force — case 6 unbuildable")
        failures.append("no zero-fallback segment available to construct case 6")

    seen_markers: dict[str, str] = {}
    for label, marker, kwargs in cases:
        ok, message = expect_rejection(label, marker, **kwargs)
        first_line = message.split(" — ")[0][:100]
        print(f"   [{'ok' if ok else 'FAIL'}] {label}")
        print(f"        {first_line}")
        if not ok:
            failures.append(f"{label}: {message[:160]}")
        else:
            seen_markers[marker] = label

    # Distinctness is about ASSERTIONS, not cases: 3 and 3b deliberately exercise
    # the same assertion from two directions (zero-k, and k between the strict and
    # tie-inclusive counts). What must hold is that every DISTINCT assertion under
    # test fired its own marker — a catch-all would collapse them to one.
    expected_markers = {marker for _, marker, _ in cases}
    distinct = seen_markers.keys() == expected_markers
    print(f"\n   [{'ok' if distinct else 'FAIL'}] {len(seen_markers)} distinct assertion "
          f"markers fired across {len(cases)} cases, covering "
          f"{sorted(m.split()[1] for m in expected_markers)} — no catch-all masquerading")
    if not distinct:
        failures.append(
            f"expected markers {sorted(expected_markers)}, saw {sorted(seen_markers)}")

    # --- assertion 4 is a CANARY, not an independent check -------------------
    # RR's restatement, adopted: under universal SA every roster is serviceable by
    # construction, so A4 cannot fire while A6 holds. Calling it an achievability
    # check would be restating SA's universality and calling it a guard. It is kept
    # as a canary for A6 regression — if the sampling constraint ever breaks, or a
    # future asset class adds another zero-weight bucket, A4 fires on the
    # consequence instead of leaving a worthless segment inside a spread.
    print("\n   assertion 4 is a CANARY, not an independent check: under universal SA")
    print("   every roster is serviceable by construction, so it cannot fire while")
    print("   assertion 6 holds. Kept so that a REGRESSION in A6's sampling")
    print("   constraint — or a new zero-weight rating bucket — fires here rather")
    print("   than surfacing as a worthless segment inside a spread.")

    # --- TIE_EPS is exercised, not merely present ---------------------------
    # A one-line guard nobody drives is indistinguishable from no guard. Patch the
    # scorer so a rival worker lands within TIE_EPS BELOW the successor on one
    # segment: bare `>` would count it strict, the epsilon-guarded comparison must
    # not. Fail-safe direction is undercounting (RR review of S5).
    print("\nTIE_EPS guard — a sub-epsilon lead must not count as a strict requirement:")
    from . import finance_scorer as sc

    baseline_strict, _ = gen.successor_routing_counts(instance)
    target_seg = baseline_strict[0]
    real_s = sc.s

    def nudged(segment, worker, calibration=None):
        value = real_s(segment, worker, calibration)
        if (segment["segment_id"] == target_seg
                and worker["worker_id"] != event["successor_id"]):
            # Rival scores a hair BELOW the successor — a tie in every sense that
            # matters, and below TIE_EPS.
            return real_s(segment, next(
                w for w in instance["workers"]
                if w["worker_id"] == event["successor_id"]), calibration) - 1e-15
        return value

    sc.s = nudged
    try:
        nudged_strict, _ = gen.successor_routing_counts(instance)
    finally:
        sc.s = real_s
    dropped = target_seg not in nudged_strict
    print(f"   baseline strict: {baseline_strict}")
    print(f"   with a 1e-15 lead on {target_seg}: {nudged_strict}")
    print(f"   [{'ok' if dropped else 'FAIL'}] sub-epsilon lead NOT counted strict "
          f"(bare `>` would have counted it)")
    if not dropped:
        failures.append("TIE_EPS guard did not exclude a sub-epsilon lead")

    # --- case 5's generator-side constraint, across a seed sweep ------------
    print("\ngenerator-side constraint (case 6) — 100 seeds:")
    produced, pool_hits = 0, 0
    for seed in range(100):
        inst = gen.generate(seed)
        for segment in inst["segments"]:
            if gen.sa_risk_weight(segment["asset_class"], segment["rating"]) == 0.0:
                pool_hits += 1
                if segment["irb_approved"]:
                    produced += 1
    print(f"   zero-SA-fallback segments appearing across 100 instances: {pool_hits}")
    print(f"   of those, IRB-approved by the default sampling: {produced}")
    constraint_ok = produced == 0 and pool_hits > 0
    print(f"   [{'ok' if constraint_ok else 'FAIL'}] sampling never PRODUCES one, and "
          f"the condition is not vacuous ({pool_hits} chances to)")
    if not constraint_ok:
        failures.append(
            f"generator-side constraint unproven: produced={produced}, pool={pool_hits}")

    print()
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  {f}")
        return 1
    print("RESULT: PASS — default generates; every constructible negative rejected "
          "with a distinct assertion; sampling constraint demonstrated non-vacuously")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
