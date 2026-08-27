"""M9 starter — implement the TODO sections. Read BRIEF.md first.

Lessons 0018-0021 as one workflow brain: escalation with a real handoff,
compliance as enforced code, the degradation ladder, paired metrics that
can't be gamed, and the MCP review checklist.
"""
import re


# ------------------------------------------------------------------
# TODO 1: escalate(conversation, confidence, policy_topics)  (0018)
# Triggers (any one): confidence < 0.5; the LAST user message mentions
# a policy topic (word-boundary match, case-insensitive); the user
# explicitly asks for a human ("human", "agent", "manager").
# On trigger, return {"escalate": True, "reasons": [...], "handoff": {
#   "summary": the first user message's text,
#   "state": {"turns": len(conversation),
#             "last_line": the final assistant message's text or ""},
#   "provenance": True}}.
# No trigger: {"escalate": False}.
# ------------------------------------------------------------------
def escalate(conversation, confidence, policy_topics):
    raise NotImplementedError("TODO 1: escalate")


# ------------------------------------------------------------------
# TODO 2: compliance_stack(text)  (0017->0018: enforced layers)
# Deterministic filters — code, not prompts:
#   - SSN-like patterns (\d{3}-\d{2}-\d{4}) -> "[PII removed]"
#   - competitor names from fixtures.COMPETITORS -> "[competitor]"
# Return (filtered_text, flags) where flags lists "pii" and/or
# "competitor" for the filters that actually fired.
# ------------------------------------------------------------------
def compliance_stack(text, competitors):
    raise NotImplementedError("TODO 2: compliance_stack")


# ------------------------------------------------------------------
# TODO 3: degrade(failure)  (0018: the ladder)
# For each catalog failure, return a DESIGNED exit dict:
#   {"message": non-empty user-facing line,
#    "offer": what still works,
#    "action": what the system does next}
# Rules the tests enforce:
#   - "status_api_down":  message contains "unavailable"; offer includes
#     the static schedule; action escalates to ops.
#   - "mid_charge_timeout": message says the charge status is UNKNOWN
#     and contains "verify"; it must NOT contain "retry now".
#   - "model_overload": message mentions reduced service; offer is the
#     FAQ floor; action queues the request.
# Every message must be non-empty — never silence, never fabrication.
# ------------------------------------------------------------------
def degrade(failure):
    raise NotImplementedError("TODO 3: degrade")


# ------------------------------------------------------------------
# TODO 4: paired_metrics(deflection, csat)  (0018/0020)
# Healthy: deflection in [0.7, 0.8] AND csat >= 4.
# High deflection (> 0.85) with csat < 4: UNHEALTHY, flag "gaming"
# (the agent got cheap and bad).
# Return {"healthy": bool, "flags": [...]}.
# ------------------------------------------------------------------
def paired_metrics(deflection, csat):
    raise NotImplementedError("TODO 4: paired_metrics")


# ------------------------------------------------------------------
# TODO 5: mcp_review(integration)  (0021: the checklist as code)
# Findings for each violation:
#   token_passthrough      -> "token-passthrough-forbidden"
#   wildcard_scopes        -> "scope-inflation"
#   sessions_auth          -> "sessions-must-not-authenticate"
#   local_command_shown == False -> "consent-missing"
# Return the findings list; empty list means approved.
# ------------------------------------------------------------------
def mcp_review(integration):
    raise NotImplementedError("TODO 5: mcp_review")
