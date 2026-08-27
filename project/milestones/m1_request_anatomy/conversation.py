"""M1 starter — implement the TODO sections. Read BRIEF.md first.

Types and the FixtureModel come from fixtures.py (working code).
Everything you implement is checked by test_m1.py; run `python3 verify.py`.
"""
from fixtures import FixtureModel, text_response  # noqa: F401 (re-exported for convenience)


class TruncatedResponse(Exception):
    """stop_reason == "max_tokens": the reply was cut off by your own cap."""


class RefusedResponse(Exception):
    """stop_reason == "refusal": policy path, never retry blindly."""


class ConversationManager:
    def __init__(self, model):
        self.model = model
        self.messages = []       # list of {"role": ..., "content": ...}
        self.escalate = False    # set True on refusal (Lesson 0003's safety path)

    # ------------------------------------------------------------------
    # TODO 1: build the request (Lesson 0001)
    # Return a dict: {"model": ..., "max_tokens": max_tokens, "system": system,
    #                 "messages": <the FULL history, oldest first>}
    # The API is stateless: send everything. The request must end with a
    # user message (Lesson 0002).
    # ------------------------------------------------------------------
    def build_request(self, system, max_tokens=1024):
        raise NotImplementedError("TODO 1: build_request")

    # ------------------------------------------------------------------
    # TODO 2: the stop_reason switchboard (Lesson 0003)
    # - end_turn: append the assistant's text blocks to self.messages as one
    #   {"role": "assistant", "content": <joined text>} turn; return the text.
    # - max_tokens: raise TruncatedResponse (the cap fired, not the model).
    # - refusal: set self.escalate = True and raise RefusedResponse.
    # ------------------------------------------------------------------
    def handle_response(self, response):
        raise NotImplementedError("TODO 2: handle_response")

    # ------------------------------------------------------------------
    # TODO 3: migrate a legacy request (Lessons 0002 + 0003)
    # Return a NEW dict (don't mutate the input) with:
    # - no "temperature" key unless it is exactly 1.0 (the dial is retired)
    # - no trailing assistant message in "messages" (retired prefill hack)
    # - "output_format" renamed to {"output_config": {"format": <value>}}
    # ------------------------------------------------------------------
    def fix_legacy_request(self, request):
        raise NotImplementedError("TODO 3: fix_legacy_request")

    # ------------------------------------------------------------------
    # TODO 4: the turn glue
    # Add the user message, build a request with the given system prompt,
    # call self.model.complete(...), and handle the response. Loop until a
    # turn completes; return the assistant's text.
    # ------------------------------------------------------------------
    def turn(self, user_text, system="You are Apex Airlines' assistant. Be concise.", max_tokens=1024):
        raise NotImplementedError("TODO 4: turn")
