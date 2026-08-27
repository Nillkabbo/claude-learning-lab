"""M3 fixtures — a scripted model that requests tools, and the tools themselves.

Self-contained (each milestone directory is standalone). The ScriptedToolModel
hands out Responses in order: some carrying tool_use blocks (the model asking
YOUR code to act), the last one carrying text with stop_reason end_turn.
"""
from dataclasses import dataclass, field


@dataclass
class ContentBlock:
    type: str                 # "text" | "tool_use" | "tool_result"
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)
    tool_use_id: str = ""


@dataclass
class Response:
    content: list
    stop_reason: str          # "end_turn" | "tool_use" | "max_tokens" | "refusal"
    usage: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})


def tool_use_response(tool_name, tool_input, tool_id="toolu_01"):
    return Response(
        content=[ContentBlock(type="tool_use", id=tool_id, name=tool_name, input=tool_input)],
        stop_reason="tool_use",
    )


def parallel_tool_response(calls):
    """calls: list of (tool_name, tool_input, tool_id)."""
    return Response(
        content=[ContentBlock(type="tool_use", id=tid, name=n, input=i) for (n, i, tid) in calls],
        stop_reason="tool_use",
    )


def text_response(text):
    return Response(content=[ContentBlock(type="text", text=text)], stop_reason="end_turn")


# --- the Apex tool registry: WORKING implementations (given code) -------------

def _get_flight_status(input):
    if input.get("flight_number") == "AX204":
        return "AX204: delayed 45 minutes, departing AUS 14:20, reason weather."
    return f"No flight found for {input.get('flight_number')}."

def _search_airports(input):
    q = input.get("query", "").lower()
    data = {"austin": "AUS — Austin-Bergstrom Intl", "jfk": "JFK — New York"}
    return next((v for k, v in data.items() if k in q), "No matching airport; try search_airports with a city name.")

TOOL_IMPLEMENTATIONS = {
    "get_flight_status": _get_flight_status,
    "search_airports": _search_airports,
}


class ScriptedToolModel:
    """Stateless, scripted — and it records every request it receives."""

    def __init__(self, scripted_responses):
        self._scripted = list(scripted_responses)
        self.requests_seen = []

    def complete(self, request):
        self.requests_seen.append(request)
        if not self._scripted:
            return text_response("…")
        return self._scripted.pop(0)
