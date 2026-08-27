# M3 · The tool loop (lesson 0005)

Hand-build the loop the Agent SDK would hand you: parse `tool_use` blocks, execute the
tools, return `tool_result` in a user message matched by `tool_use_id`, echo the
assistant turn in full, and loop until `end_turn` — with a stopping condition.

**Read first:** [0005 · Tool use fundamentals](../../../lessons/0005-tool-use-fundamentals.html)

## The setup

`fixtures.py` (given, working) provides a `ScriptedToolModel` that hands out responses
in order — some requesting tools (including one *parallel* call and one *unknown* tool),
the last answering — plus a working Apex tool registry (`get_flight_status`,
`search_airports`). Your job is the four TODOs in `loop.py`:

1. **`execute_tool(block)`** — resolve the tool by name, call it with the input, and
   build the `tool_result` block. Unknown tool: an instructive `is_error` result
   (naming the tool and what's available) — never an exception through the loop.
2. **`append_assistant_turn(response)`** — the echo rule: the model re-reads its own
   request, so the assistant turn goes into history with all its blocks intact.
3. **`append_tool_results(blocks)`** — one user message, `tool_result` blocks only,
   first in content, immediately after the assistant turn, matched by id.
4. **`run_turn(user_text, max_turns)`** — the loop: full history in every request
   (statelessness), branch on `stop_reason`, and a `max_turns` cap that raises
   `LoopLimitReached` — the stopping condition every agent needs.

## Done means

`python3 verify.py` shows M3 **GREEN** — all 10 checks, including the parallel-call
shape, the unknown-tool discipline, and the full-history invariant. Paste
`project: M3:10/10` to your agent and say **"next milestone"**.
