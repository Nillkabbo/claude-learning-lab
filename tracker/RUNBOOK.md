# Runbook — the night shift (Ch 10)

| Failure | Playbook | Owner |
|---|---|---|
| Nightly sync fails (upstream 5xx) | retry once next window; file issue; auto-close on green | automation |
| Two failed windows in a row | PAGE A HUMAN | on-call |
| Any write failure to tasks.json | PAGE A HUMAN (atomic-write invariant) | on-call |
| Corrupt tasks.json found | verify tasks.corrupt.json exists; restore manually | you |
