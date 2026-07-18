# Evidence-recall labels

Create one frozen JSON protocol per seed before interpreting Arm 2. Atomic labels
describe change-relevant facts visible to the manager, never hidden mutation
state. Each requires `label_id`, `channel`, and a case-insensitive
`fact_pattern`; it may also constrain `worker` and `task_pattern`.

The same file freezes offline relation judgments. A relation cites atomic label
IDs and is coded `diagnostic`, `exonerating`, `neutral`, or `ambiguous`. These
ground-truth-side labels are analysis metadata only and never enter Arms 0–2.
The protocol also fixes correct recovery agents and regexes used only to code
whether a shadow response engaged with change-relevant evidence.

Run `python -m experiments.ds_reroute.audit_arm2 --labels <labels.json> <run-dir>`.
Report overall recall, recall by channel, and ledger delay. A null reward result
is uninterpretable when relevant-fact recall is inadequate.

Run the non-intervening probes with:

```bash
uv run python -m experiments.ds_reroute.shadow_probe <run-dir> \
  --protocol <labels.json>
```

Use `--dry-run` to verify the frozen B/C assignment points without making LLM
calls. Probe outputs are stored as `shadow_probes.json` and joined by the audit.
