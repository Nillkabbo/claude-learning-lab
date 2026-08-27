"""M3 starter — implement the TODO sections. Read BRIEF.md first.

Lesson 0005's loop, built by hand: parse tool_use, execute, return tool_result
in a user message matched by tool_use_id, echo the assistant turn in full,
loop until end_turn — with a stopping condition.
"""
from fixtures import TOOL_IMPLEMENTATIONS


class LoopLimitReached(Exception):
    """The max_turns stopping condition fired — never loop forever."""


class ToolLoopRunner:
    def __init__(self, model, tools=None):
        self.model = model
        self.tools = tools if tools is not None else TOOL_IMPLEMENTATIONS
        self.messages = []

    # ------------------------------------------------------------------
    # TODO 1: execute one tool call
    # Look up block.name in self.tools and call it with block.input.
    # Return a tool_result block dict:
    #   {"type": "tool_result", "tool_use_id": block.id, "content": <output>}
    # Unknown tool name -> a result with "is_error": True and instructive
    # content ("Unknown tool <name>; available: ...") — never an exception.
    # ------------------------------------------------------------------
    def execute_tool(self, block):
        raise NotImplementedError("TODO 1: execute_tool")

    # ------------------------------------------------------------------
    # TODO 2: append the assistant turn IN FULL
    # Append {"role": "assistant", "content": [...]} carrying the response's
    # blocks (all of them — the echo rule; the model re-reads its own request).
    # ------------------------------------------------------------------
    def append_assistant_turn(self, response):
        raise NotImplementedError("TODO 2: append_assistant_turn")

    # ------------------------------------------------------------------
    # TODO 3: append the tool results
    # ONE user message containing ONLY tool_result blocks — first in content,
    # immediately after the assistant turn, one per tool_use, matched by id.
    # ------------------------------------------------------------------
    def append_tool_results(self, result_blocks):
        raise NotImplementedError("TODO 3: append_tool_results")

    # ------------------------------------------------------------------
    # TODO 4: the loop itself
    # Build each request with the FULL history (statelessness — Lesson 0001),
    # call self.model.complete, and branch on stop_reason:
    #   "tool_use" -> execute every tool_use block, append results, continue
    #   "end_turn" -> append the assistant turn, return the text
    # Raise LoopLimitReached if more than max_turns model calls are needed.
    # ------------------------------------------------------------------
    def run_turn(self, user_text, system="You are Apex Airlines' assistant.", max_turns=6):
        raise NotImplementedError("TODO 4: run_turn")
