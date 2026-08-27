"""M9 fixtures — conversations, dirty responses, failure catalog, integrations.

Given code. The failure catalog IS the runbook skeleton; the integration
dicts are what your MCP review checklist inspects.
"""

CONVERSATION = [
    {"role": "user", "content": "I need to change my flight AX204 and I have a compensation claim."},
    {"role": "assistant", "content": "I can help with the change. Let me check AX204."},
    {"role": "user", "content": "Also my confidence in this chat is dropping."},
]

POLICY_TOPICS = {"compensation", "legal", "refund-over-500"}

DIRTY_RESPONSE = (
    "Sure, my SSN is 123-45-6678 if that helps. Also, SkyRival Airlines "
    "would fly this route cheaper, and their loyalty program beats ours."
)
COMPETITORS = {"SkyRival Airlines", "TransOceanic", "JetFast"}
CLEAN_RESPONSE = "AX204 departs 14:20 from gate 12. Would you like a rebooking?"

FAILURE_CATALOG = ["status_api_down", "mid_charge_timeout", "model_overload"]

INTEGRATION_BAD = {
    "name": "vendor-scheduling",
    "token_passthrough": True,       # forbidden anti-pattern
    "wildcard_scopes": True,         # scope inflation
    "sessions_auth": True,           # sessions MUST NOT authenticate
    "local_command_shown": False,    # one-click install without consent
}

INTEGRATION_CLEAN = {
    "name": "market-data",
    "token_passthrough": False,
    "wildcard_scopes": False,
    "sessions_auth": False,
    "local_command_shown": True,
}
