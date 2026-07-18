# Evidence-recall labels

Create one frozen JSON file per seed before interpreting Arm 2. Labels describe
change-relevant facts visible to the manager, never hidden mutation state. Each
label requires `label_id`, `channel`, and a case-insensitive `fact_pattern`; it
may also constrain `worker` and `task_pattern`.

Run `python -m experiments.ds_reroute.audit_arm2 --labels <labels.json> <run-dir>`.
Report overall recall, recall by channel, and ledger delay. A null reward result
is uninterpretable when relevant-fact recall is inadequate.
