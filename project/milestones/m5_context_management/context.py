"""M5 starter — implement the TODO sections. Read BRIEF.md first.

Lesson 0008 as code: what counts, when input alone would 400, compaction
as the primary strategy, cache-aware tool-result clearing, and the
memory-before-clear dance.
"""
from fixtures import estimate_tokens, summarize


PLACEHOLDER = "[cleared: tool result removed to save context]"


class ContextManager:

    # ------------------------------------------------------------------
    # TODO 1: account for what counts (Lesson 0008's budget box)
    # Sum the token estimate over ALL messages — text and tool_result
    # blocks alike (tool results count; so would images/docs if we had them).
    # ------------------------------------------------------------------
    def count_tokens(self, messages):
        raise NotImplementedError("TODO 1: count_tokens")

    # ------------------------------------------------------------------
    # TODO 2: the overflow rule (the API's 400)
    # True iff the INPUT ALONE exceeds `window` tokens — the check you
    # must run before sending, because "prompt is too long" is a 400.
    # ------------------------------------------------------------------
    def would_overflow(self, messages, window):
        raise NotImplementedError("TODO 2: would_overflow")

    # ------------------------------------------------------------------
    # TODO 3: compaction — "the primary strategy"
    # Replace all but the last `keep_recent` messages with ONE summary
    # message: {"role": "user", "content": "[conversation summary] " +
    # summarize(older)}. Return the new list. The recent tail must be
    # untouched, verbatim.
    # ------------------------------------------------------------------
    def compact(self, messages, keep_recent=4):
        raise NotImplementedError("TODO 3: compact")

    # ------------------------------------------------------------------
    # TODO 4: cache-aware tool-result clearing (clear_tool_uses rules)
    # Fires only when total tokens exceed `trigger`. Clears OLDEST-first:
    # replace a tool_result block's content with PLACEHOLDER — but never
    # the `keep` most recent tool_result blocks, never blocks whose
    # message's "tool" is in `exclude_tools`. Stop once at least
    # `clear_at_least` tokens would be saved; if the achievable savings
    # are below clear_at_least, change NOTHING and report applied=False
    # (don't torch the cache for a trickle).
    # Return (new_messages, tokens_cleared, applied).
    # ------------------------------------------------------------------
    def clear_tool_results(self, messages, trigger, keep=3, clear_at_least=0, exclude_tools=()):
        raise NotImplementedError("TODO 4: clear_tool_results")

    # ------------------------------------------------------------------
    # TODO 5: the memory-before-clear dance
    # When tokens exceed `threshold * warn_fraction`, that's the warning
    # zone: save the essentials (each recent message's text) into `memory`
    # under keys "essential-<i>", and return the list of keys saved.
    # Below the zone: save nothing, return [].
    # ------------------------------------------------------------------
    def save_essentials_before_clearing(self, messages, memory, threshold, warn_fraction=0.9):
        raise NotImplementedError("TODO 5: save_essentials_before_clearing")
