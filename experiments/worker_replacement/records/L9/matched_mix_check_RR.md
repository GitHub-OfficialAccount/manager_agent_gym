# Is the corrected size-3 table matched on mix? (RR)

LS asked directly, and asked to be told if wrong. **LS is right, and more strongly than
they argued.** The corrected table is not matched on mix; the two carrier groups sit at
**opposite extremes** of it.

## Measured on RE's own templates, seeds and builder

`nA` = IRB-applicable segments in the successor-unique class, via
`check_size3_pricing.build_size3(template, 'corporate', seed)`:

```
carriers=1  (n=120)   nA = 4 in 100% of cells
carriers=2  (n=119)   nA = 0 in 87% (103/119), nA = 1 in 13% (16/119)
```

**RE reported `nA=1` in 100% of cells in both groups.** Through the builder I can run,
it is 4 versus 0 — the two ends of the range, not a match. Notably 103/119 is exactly
the figure RE gives for amplification draining nA to 0, so the builder appears to be
amplifying on the path presented as unamplified.

**So LS's objection stands and strengthens:** normalising each cell against
disjoint@nA does not match the carrier groups to each other, and here they are not
merely at different nA — they are at 4 and 0. **No ordering claim between the carrier
groups survives, and `carriers=1 @ nA=1` is still genuinely missing.**

## A second, separate disagreement I cannot close

My independent pricing on RE's templates/seeds/builder does not reproduce their
carrier-2 figure under **any** tie-break:

```
tie-break      carriers=1  carriers=2   ratio
best-case          1.59%       0.00%      0.00
expectation        1.59%       1.33%      0.84
visit order        1.59%       0.57%      0.36
worst-case         1.59%       2.95%      1.85
RE report          1.31%       4.24%      3.2
```

RE's 4.24% is **outside the entire achievable range** I measure (0.00–2.95%), so the gap
is not the tie-break alone. My ceiling code is not the suspect: on a single cell it
agrees with the shipped `sc.ceiling_vs_stale_card` to every printed digit
(`ceiling_share` 0.008846, oracle 8.188185, tie set 350, min 0.0, max 0.022115).

**Carrier-1 is well-determined** — 1.59% under all four rules, because its tie set is
small (mean 12.7) and every member scores the same under truth. **Carrier-2 is entirely
tie-break-determined** — tie set mean 235.4, a 19× difference, spanning 0.00% to 2.95%.
**Two groups whose tie sets differ 19-fold cannot be compared without fixing the
tie-break first**, independently of the mix problem.

## Single-cell diff target for RE

`templates[2][0]`, clone `corporate`, seed 0 — carriers=2:

```
workers    w_a65374 [bank, corporate, sovereign]   <- predecessor
           w_c4e399 [mdb, retail, sovereign]       <- successor
           w_e15d96 [bank, retail, sovereign]
           w_8e44e0 [corporate_clone, retail, sovereign]
card claims  [bank, corporate, sovereign]      successor-unique class: mdb
segments     one mdb segment (seg_07), and it is SA -> nA = 0
oracle 8.188185   believed optimum 9.000000   tie set 350/1680
realised over tie set  min 8.007105  mean 8.115753  max 8.188185
ceiling share  best 0.0000%   expectation 0.8846%   worst 2.2115%
```

## Labels

| finding | label |
|---|---|
| the corrected table is not mix-matched: nA=4 vs nA=0 through the builder I can run | **blocker** |
| RE's carrier-2 figure is outside my achievable range under every tie-break | **blocker** |
| carrier-2's tie set is 19× carrier-1's, so the groups are not comparable at a fixed rule | **limitation** |
| my ceiling code matches the shipped function to every digit on a named cell | control passed |
