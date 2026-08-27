"""M6 starter — implement the TODO sections. Read BRIEF.md first.

Part A: the rules layer as code (0009-0011) — permission evaluation,
subagent frontmatter validation, the hook exit-code contract.
Part B: the Agent SDK shape (0012) — query() with allowed_tools,
permission modes, and can_use_tool as the confirmation gate.
"""
from fixtures import TOOL_IMPLEMENTATIONS, parse_frontmatter


# =====================================================================
# Part A — the rules layer
# =====================================================================

# ------------------------------------------------------------------
# TODO 1: evaluate_permission(tool, arg, permissions)
# The evaluation law (0009): deny, then ask, then allow — FIRST MATCH
# WINS. A rule matches when its tool name equals `tool` AND its
# specifier (if any) matches `arg`:
#   - bare rule ("WebFetch") matches every use of that tool
#   - "Read(./.env)" matches arg exactly
#   - "Bash(rm *)" matches args equal to "rm" or starting with "rm "
# Return "deny" | "ask" | "allow", or None when nothing matches.
# ------------------------------------------------------------------
def evaluate_permission(tool, arg, permissions):
    raise NotImplementedError("TODO 1: evaluate_permission")


# ------------------------------------------------------------------
# TODO 2: validate_subagent(md_text) -> list[str] of findings
# Parse frontmatter (parse_frontmatter is given). Findings:
#   - "missing-name" / "bad-name" (name must match ^[a-z][a-z0-9-]*$)
#   - "missing-description" / "short-description" (under 20 chars —
#     delegation is description-driven; vague = never called)
#   - "empty-body" (the body IS the system prompt)
# Return [] for a clean subagent.
# ------------------------------------------------------------------
def validate_subagent(md_text):
    raise NotImplementedError("TODO 2: validate_subagent")


# ------------------------------------------------------------------
# TODO 3: hook_decision(exit_code, stdout) -> str | None
# The exit-code contract (0010):
#   - exit code 2: "block" — regardless of any JSON printed
#   - exit code 0 with JSON containing "permissionDecision":
#     "deny" or "allow" from the JSON
#   - anything else: None (no decision)
# stdout may be plain text or JSON — only JSON that parses counts.
# ------------------------------------------------------------------
def hook_decision(exit_code, stdout):
    raise NotImplementedError("TODO 3: hook_decision")


# =====================================================================
# Part B — query(), the SDK shape (0012)
# =====================================================================

# ------------------------------------------------------------------
# TODO 4: query(prompt, model, options) — a generator, SDK-style
# options: {"allowed_tools": [...], "permission_mode": "default"|"plan",
#           "can_use_tool": callable(block)->bool or None}
# Yield message dicts as they happen:
#   {"type": "assistant", "content": [...]}         each model turn
#   {"type": "tool_result", ...}                    each executed call
# End by RETURNING (generator return value) the final text.
# Rules:
#   - "plan": read-only — yield the assistant turn but execute nothing
#   - tools not in allowed_tools: not executed; result says not allowed
#   - can_use_tool returning False: not executed; is_error result
#     saying "denied by canUseTool"
# Build each request with the full history (you know this law by now).
# ------------------------------------------------------------------
def query(prompt, model, options=None):
    raise NotImplementedError("TODO 4: query")
