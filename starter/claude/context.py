"""context.py — the budget that rots, managed. Law 7."""
from .client import estimate_tokens

PLACEHOLDER = "[cleared: tool result removed to save context]"


def count_tokens(messages):
    """Everything counts: text, tool_result blocks, all of it."""
    total = 0
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, list):
            for b in content:
                total += estimate_tokens(b.get("content", b.get("text", "")))
        else:
            total += estimate_tokens(content)
    return total


def would_overflow(messages, window):
    """Input alone over the window — the pre-send check (the 400 rule)."""
    return count_tokens(messages) > window


def compact(messages, summarize, keep_recent=4):
    """The primary strategy: old turns -> ONE summary; tail verbatim."""
    if len(messages) <= keep_recent:
        return list(messages)
    summary = {"role": "user", "content": "[conversation summary] " + summarize(messages[:-keep_recent])}
    return [summary] + messages[-keep_recent:]


def clear_tool_results(messages, trigger, keep=3, clear_at_least=0, exclude_tools=()):
    """The clear_tool_uses rulebook. Returns (new_messages, tokens_cleared, applied)."""
    total = count_tokens(messages)
    if total <= trigger:
        return list(messages), 0, False
    tool_msgs = [i for i, m in enumerate(messages)
                 if isinstance(m.get("content"), list)
                 and any(b.get("type") == "tool_result" for b in m["content"])
                 and m.get("tool") not in exclude_tools]
    clearable = tool_msgs[:-keep] if keep else tool_msgs
    if not clearable:
        return list(messages), 0, False
    savings = sum(count_tokens([messages[i]]) for i in clearable)
    if savings < clear_at_least:
        return list(messages), 0, False        # don't torch the cache for a trickle
    new_messages = [dict(m) for m in messages]
    for i in clearable:
        new_messages[i] = {**new_messages[i], "content": [
            {**b, "content": PLACEHOLDER} if b.get("type") == "tool_result" else b
            for b in new_messages[i]["content"]]}
    return new_messages, savings, True


def save_essentials(messages, memory, threshold, warn_fraction=0.9):
    """The memory-before-clear dance: persist essentials inside the warning zone."""
    if count_tokens(messages) < threshold * warn_fraction:
        return []
    keys = []
    for i, m in enumerate(messages[-5:]):
        key = f"essential-{i}"
        memory.save(key, str(m.get("content"))[:200])
        keys.append(key)
    return keys
