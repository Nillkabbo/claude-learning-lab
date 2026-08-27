# M6 · Claude Code config & Agent SDK (lessons 0009–0012)

Two worlds in one milestone: the **rules layer** (permissions, subagents, hooks — as
code you implement and then use on your own artifacts) and the **SDK shape** (a
`query()` wrapper with `allowed_tools`, modes, and `can_use_tool` as the confirmation
gate).

**Read first:** [0009 · Claude Code essentials](../../../lessons/0009-claude-code-essentials.html)
· [0010 · Claude Code in the team](../../../lessons/0010-claude-code-in-the-team.html)
· [0011 · Subagents & skills](../../../lessons/0011-subagents-and-skills.html)
· [0012 · Agent SDK](../../../lessons/0012-agent-sdk.html)

## The setup

`fixtures.py` (given, working): good/bad settings, subagent markdown, and hook configs;
a frontmatter parser; a scripted model + Apex tool registry. Your job:

**In `validate.py` — four TODOs:**
1. **`evaluate_permission(tool, arg, permissions)`** — the evaluation law: deny →
   ask → allow, first match wins; bare rules match all uses; `Bash(rm *)` matches
   `rm` and `rm …`; a broad deny beats a narrow allow.
2. **`validate_subagent(md_text)`** — frontmatter rules: lowercase-hyphen name, a real
   delegation description (≥ 20 chars — vague means never delegated to), non-empty body.
3. **`hook_decision(exit_code, stdout)`** — the exit-code contract: 2 blocks
   regardless of JSON; 0 + JSON `permissionDecision` decides; otherwise no decision.
4. **`query(prompt, model, options)`** — SDK-shaped generator: yields assistant and
   tool_result messages, returns the final text; `allowed_tools` filters; `"plan"`
   mode executes nothing; `can_use_tool` returning False skips execution with an
   `is_error` result.

**In `config/` — three artifacts YOU author** (see `config/README.md`): a `CLAUDE.md`
under 200 lines, a strict-JSON `settings.json` whose rules pass YOUR evaluator, and a
read-only `agents/release-notes.md` that passes YOUR validator.

## Done means

`python3 verify.py` shows M6 **GREEN** — all 14 checks, including the three that grade
your own config artifacts with the validators you built. Paste `project: M6:14/14` to
your agent and say **"next milestone"**.
