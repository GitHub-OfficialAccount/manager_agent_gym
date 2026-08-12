# L17 — LS review. PASS.

**Verified at source rather than from the report, because the failure this fixes was a two-field
call and the previous guard against it was also two fields.**

## The assertion discriminates, both ways that matter

    seed 42   from-record ef25aa9d | old-runner ce61d5b5 differs | one-param-off 47c7f8bd differs
    seed 30   from-record fc1eac6c | old-runner 2d88dfb5 differs | one-param-off a43ae6d4 differs

**Wholesale mismatch and a SINGLE flipped parameter both produce a different hash**, so the check
does not merely catch the fault we found — it catches the next one, which will be a different
parameter.

**And the record now SUPPLIES the setting rather than being consulted about two fields of it** — all
six, forwarded as one object. **A new generator knob is picked up with no code change, because
nothing enumerates the knobs any more.** That is what makes it a fix to the CLASS rather than the
instance.

## ★ RE's own finding is the strongest argument for the approach, and it was not predicted

**The PREVIOUS guard had already gone stale against the current record.** It read
`chosen.get("lattice")` and `chosen.get("shared_class_segments")` from top-level keys; v2 keeps the
setting under `setting`, **so those reads returned `None` and every run against the approved record
would have raised a confusing arrangement mismatch.**

**The guard against running the wrong instance was itself broken by the record it was meant to
guard.** A two-field guard goes stale exactly as a two-field call does — **which is why threading
alone was not the answer, and why this one compares a hash rather than fields.**

## Two gaps RE closed that were not in the brief

**`selection_record` had no CLI flag** — a Python parameter only, so **the command a person actually
types could not opt into the guard that makes a run trustworthy.** A safety check the CLI cannot
reach does not run.

**The manifest now records WHETHER THE COMPARISON HAPPENED**, not only the hash. The standing line
was *"a recorded fact nobody compares is the shape we keep finding"*; RE supplied its second half —
**a bundle could not say whether anyone had compared it.** `selection_provenance` empty now means
UNGUARDED and says so in the artefact.

## What this review does NOT establish

**Not that the shipped instances are the right ones** — only that what runs is what the record
selected. **The record's own limitations stand** (the median floor selects rank not magnitude; the
ceilings are 0.25x and 0.36x the MDE), and this fix makes them binding rather than avoidable.

**And it does not touch the 876 s justification**, which both agents now agree was measured from
`structured_llm_*` pairs — every one of which is the MANAGER's. **A manager request/response pair
justifying a WORKER request timeout is the 180 s error still live in the code.** The probe's job.
