# L10 acceptance — output on the shipped environments

Produced by `python -m experiments.worker_replacement.check_l10_properties 42 30 --controls`
at the settled revision, against `records/L10/environment_selection_v2.json`.

```
L10 ACCEPTANCE — six properties, asserted not hoped for
setting: {"amplify_count": true, "amplify_divergence": false, "amplify_irb_priority": false, "irb_applicable_fraction": 0.89, "lattice": "partial", "shared_class_segments": 1}  cap=UNCAPPED (runtime enforces none)
Basel table digest pinned at run start: 80cd0a2983c51188...

  seed 42: PASS
    [ok] 1 ceiling > 0                                ceiling_share=0.04970
    [ok] 3 lied class has another post-swap holder    lied_class='retail' other_post_swap_holders=['w_c0dd2b']
    [ok] 4 allocation is non-trivial                  5 segment classes; workers spanning all of them: none
    [ok] 5 Basel tables intact AND divergence off     digest=MATCH amplify_divergence=False
    [ok] 6 admitted                                   admitted=True
  seed 30: PASS
    [ok] 1 ceiling > 0                                ceiling_share=0.07120
    [ok] 3 lied class has another post-swap holder    lied_class='sovereign' other_post_swap_holders=['w_36b62b']
    [ok] 4 allocation is non-trivial                  5 segment classes; workers spanning all of them: none
    [ok] 5 Basel tables intact AND divergence off     digest=MATCH amplify_divergence=False
    [ok] 6 admitted                                   admitted=True

CONTROLS — every property shown FAILING on its named fixture
(a property never shown failing is a restatement of the construction)
    [ok] 1 ceiling > 0                      `current` at nA=1                      fires
           `current` at segs=1, seed 42: ceiling_share=0.00000 (premise re-established, not inherited)
    [ok] 3 lied class has another holder    `current` -- the relational one        fires
           lied_class='retail' other_post_swap_holders=[]
    [ok] 4 allocation is non-trivial        a worker covering every segment class  fires
           5 segment classes; workers spanning all of them: ['w_721a8b']
    [ok] 5a Basel tables intact             perturbed SA_SOVEREIGN                 fires
           digest=DIFFERS amplify_divergence=False (table restored)
    [ok] 5b divergence off                  switch left ON (the generator default) fires
           digest=MATCH amplify_divergence=True
    [ok] 5c retail not skipped              perturbed SA_RETAIL_FLAT (RR's hole)   fires
           digest=DIFFERS amplify_divergence=False (constant restored)
    [ok] 6 admitted                         a seed admission rejects (searched)    fires
           lattice='current' seed 42: admitted=False failing=['3_stale_card_ceiling_above_zero']

RESULT: PASS
```

**Five properties, not six.** Property 2 (`nA < cap`) is RETIRED — with no capacity
allowance its condition is unconditionally true and the check could not fail. Property 4
was REPLACED: "capacity binds exactly" would have kept passing while no longer meaning
what its name said, so it is now "no single post-swap worker's IRB coverage spans every
segment class" — same job, falsifiable without a cap.

**Every surviving property is shown FAILING on a named fixture above.** A property never
shown failing is a restatement of the construction, not a post-condition.
