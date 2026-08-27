"""client.py — the request contract, enforced. Law 1, 2, 3, 4.

A Messages-API-shaped client: fixtures by default, real API optional.
The RequestBuilder refuses to build an invalid request; handle_response
turns stop_reason into an action. Copy this into any project.
"""
from dataclasses import dataclass, field
from enum import Enum


def estimate_tokens(text):
    """~4 chars/token. Swap for the Token Counting API in production."""
    return max(1, len(str(text)) // 4)


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
    stop_reason: str          # end_turn | tool_use | max_tokens | refusal
    usage: dict = field(default_factory=dict)


class Action(Enum):
    COMPLETE = "complete"
    RUN_TOOLS = "run_tools"
    TRUNCATED = "truncated"
    REFUSED = "refused"


class FixtureModel:
    """A stateless, scripted model — the real API's contract in miniature."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests_seen = []

    def complete(self, request):
        self.requests_seen.append(request)
        if not self._responses:
            return Response([ContentBlock("text", text="…")], "end_turn")
        return self._responses.pop(0)


class RealClient:
    """Optional: wire a real SDK here. Same complete(request) shape."""

    def __init__(self, sdk_messages, model="claude-sonnet-4-6"):
        self._create = sdk_messages
        self.model = model

    def complete(self, request):
        raw = self._create(**request)
        blocks = [ContentBlock(b.get("type", "text"),
                               text=b.get("text", ""),
                               id=b.get("id", ""),
                               name=b.get("name", ""),
                               input=b.get("input", {}))
                  for b in raw.content]
        return Response(blocks, raw.stop_reason, dict(raw.usage))


class RequestBuilder:
    """Builds only contract-valid requests (Law 1: statelessness)."""

    def build(self, messages, system, max_tokens=1024, tools=None, model="claude-sonnet-4-6"):
        if not messages:
            raise ValueError("messages must not be empty")
        if messages[-1]["role"] != "user":
            raise ValueError("requests must end with a user message (no prefills)")
        request = {"model": model, "max_tokens": max_tokens, "system": system,
                   "messages": messages}
        if tools:
            request["tools"] = tools
        return request


def handle_response(response):
    """The stop_reason switchboard -> (Action, payload)."""
    if response.stop_reason == "end_turn":
        text = " ".join(b.text for b in response.content if b.type == "text")
        return Action.COMPLETE, text
    if response.stop_reason == "tool_use":
        return Action.RUN_TOOLS, [b for b in response.content if b.type == "tool_use"]
    if response.stop_reason == "max_tokens":
        return Action.TRUNCATED, None          # your cap fired — not the model
    if response.stop_reason == "refusal":
        return Action.REFUSED, None            # policy path — never retry blindly
    raise ValueError(f"unknown stop_reason: {response.stop_reason}")


def assistant_turn_message(response):
    """The echo rule: the full assistant turn, blocks intact (Law 5)."""
    return {"role": "assistant",
            "content": [{"type": b.type, "text": b.text, "id": b.id,
                         "name": b.name, "input": b.input} for b in response.content]}


def tool_results_message(blocks):
    """One user message, tool_result blocks only, first in content (Law 5)."""
    return {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": b.id, "content": str(b.input)} for b in blocks]}
