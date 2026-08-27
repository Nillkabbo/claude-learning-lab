"""M4 fixtures — tool definitions to audit, and the failure primitives.

Given code: exception classes carrying structured guidance (Lesson 0007's
taxonomy as types), a model-flight tool that passes a proper audit, and
several offenders that don't.
"""


# --- the error taxonomy as types (0007) ----------------------------------------

class TransientError(Exception):
    """Retryable — and the message must SAY so, with parameters."""
    def __init__(self, msg, retry_after):
        super().__init__(msg)
        self.retry_after = retry_after


class PermanentError(Exception):
    """Adapt, don't retry — the message names the alternative path."""
    def __init__(self, msg, alternative):
        super().__init__(msg)
        self.alternative = alternative


class UncertainStateError(Exception):
    """A side effect may have fired. Verify before ANY retry."""
    def __init__(self, msg, verify_hint):
        super().__init__(msg)
        self.verify_hint = verify_hint


def rate_limited_flight_search():
    raise TransientError("Flight search rate limited.", retry_after=30)

def unknown_airport(code):
    raise PermanentError(
        f"Invalid IATA airport code '{code}'.",
        alternative="Call search_airports to resolve city names first.")

def charge_card_timeout():
    raise UncertainStateError(
        "Timed out after submission; charge status unknown.",
        verify_hint="Query get_charge_status with the idempotency key before any retry.")


# --- tool definitions to audit (0006) -------------------------------------------

GOOD_TOOL = {
    "name": "get_flight_status",
    "description": (
        "Gets the current status of a single Apex Airlines flight. "
        "Use when the passenger asks about departure time, delay, or gate for a specific flight number. "
        "Do not use for airport information or bookings — those are separate tools. "
        "Returns one line of status text; it does not provide weather or rebooking."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "flight_number": {
                "type": "string",
                "description": "Apex flight code, e.g. AX204.",
            },
        },
        "required": ["flight_number"],
    },
}

SHORT_DESCRIPTION_TOOL = {
    "name": "flight_status",
    "description": "Gets flight status.",
    "input_schema": GOOD_TOOL["input_schema"],
}

PARAM_WITHOUT_DESCRIPTION_TOOL = {
    "name": "search_airports",
    "description": GOOD_TOOL["description"],
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}

OPEN_WORLD_TOOL = {
    "name": "rebook_passenger",
    "description": GOOD_TOOL["description"],
    "input_schema": {
        "type": "object",
        "properties": {
            "cabin": {"type": "string", "description": "The cabin; one of economy, business."},
        },
        "required": ["cabin"],
    },
}

PR_TOOLS = [
    {"name": "github_create_pr", "description": "Creates a pull request.",
     "input_schema": {"type": "object", "properties": {"title": {"type": "string", "description": "PR title."}}, "required": ["title"]}},
    {"name": "github_review_pr", "description": "Requests a review of a pull request.",
     "input_schema": {"type": "object", "properties": {"number": {"type": "integer", "description": "PR number."}}, "required": ["number"]}},
    {"name": "github_merge_pr", "description": "Merges a pull request.",
     "input_schema": {"type": "object", "properties": {"number": {"type": "integer", "description": "PR number."}}, "required": ["number"]}},
]
