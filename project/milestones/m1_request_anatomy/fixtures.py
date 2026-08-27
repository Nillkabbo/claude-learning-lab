"""Fixture model + response types for M1. Given code — read it, don't change it.

The FixtureModel stands in for the real Messages API: stateless, scripted.
Lesson 0001's law applies to it exactly as to the real thing — it remembers
nothing between calls; whatever your ConversationManager wants it to "know"
must arrive in the messages array you send.
"""
from dataclasses import dataclass, field


@dataclass
class ContentBlock:
    type: str                 # "text" | "tool_use" | "tool_result"
    text: str = ""
    id: str = ""              # tool_use id
    name: str = ""            # tool name
    input: dict = field(default_factory=dict)
    tool_use_id: str = ""     # tool_result linkage


@dataclass
class Response:
    content: list             # list[ContentBlock]
    stop_reason: str          # "end_turn" | "max_tokens" | "refusal" | "tool_use"
    usage: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})


def text_response(text, stop_reason="end_turn"):
    return Response(content=[ContentBlock(type="text", text=text)], stop_reason=stop_reason)


def truncated_response(text="Your checking balance is $4"):
    return Response(content=[ContentBlock(type="text", text=text)], stop_reason="max_tokens")


def refusal_response():
    return Response(content=[ContentBlock(type="text", text="I can't help with that.")],
                    stop_reason="refusal")


class FixtureModel:
    """A scripted, stateless model. complete() pops the next scripted response."""

    def __init__(self, scripted_responses):
        self._scripted = list(scripted_responses)
        self.requests_seen = []   # every request dict you sent — for tests

    def complete(self, request):
        self.requests_seen.append(request)
        if not self._scripted:
            return text_response("…")
        return self._scripted.pop(0)
