# Author your M6 artifacts here

Three files, checked by `test_m6.py` with the validators you build in `validate.py`:

1. **`CLAUDE.md`** — standing facts for working in THIS project (how to run
   `python3 verify.py`, the fixture-model contract, the Apex scenario). Specific over
   vague; under 200 lines; it is context, not enforced configuration.
2. **`settings.json`** — a permissions block that denies `Read(./.env)`, allows
   `Bash(python3 verify.py)`, and asks before `Bash(git push *)`. Strict JSON.
3. **`agents/release-notes.md`** — a read-only subagent: lowercase-hyphen `name`,
   a real delegation `description` (20+ chars — include "use proactively"),
   `tools: [Read, Grep, Glob]`, and a body that is its system prompt.

Optional once green: a PreToolUse `hooks/` script and a `/verify` skill folder —
bring them to your agent for review.
