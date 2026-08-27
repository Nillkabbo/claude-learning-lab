"""M5 fixtures — token estimation, a summarizer, memory store, history builders.

Given code. estimate_tokens is a deliberate approximation (len//4): the
architecture lesson is about WHAT counts and WHEN to act, not tokenizer
fidelity — swap in the Token Counting API's numbers when you go real.
"""


def estimate_tokens(text):
    """Approximate tokens for a string (~4 characters per token)."""
    return max(1, len(str(text)) // 4)


def summarize(messages):
    """A fixture summarizer: compresses messages into one summary string."""
    heads = []
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(b.get("content", b.get("text", ""))) for b in content)
        heads.append(content.strip()[:40])
    return "SUMMARY OF PRIOR CONVERSATION: " + " | ".join(heads)


class MemoryStore:
    """File-less stand-in for the memory tool: save/load essentials."""

    def __init__(self):
        self._store = {}

    def save(self, key, value):
        self._store[key] = value

    def load(self, key):
        return self._store.get(key)

    def keys(self):
        return sorted(self._store)


# --- history builders -----------------------------------------------------------

def user_msg(text):
    return {"role": "user", "content": text}

def assistant_msg(text):
    return {"role": "assistant", "content": text}

def tool_result_msg(tool_use_id, output, tool_name="get_flight_status"):
    return {"role": "user", "tool": tool_name, "content": [
        {"type": "tool_result", "tool_use_id": tool_use_id, "content": output},
    ]}


def big_history(tool_outputs=None, n_turns=4):
    """A realistic history: n_turns exchanges, each with a fat tool result."""
    tool_outputs = tool_outputs or ["AX204 " + "delayed 45 minutes at gate 12. " * 40] * n_turns
    messages = []
    for i, output in enumerate(tool_outputs):
        messages.append(user_msg(f"Question {i} about flight AX204"))
        messages.append(tool_result_msg(f"toolu_{i}", output))
        messages.append(assistant_msg(f"Answer {i}: it is delayed."))
    return messages
