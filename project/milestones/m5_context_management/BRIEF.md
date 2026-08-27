# M5 · Context management (lesson 0008)

The budget box as code: what counts (and what re-bills), the input-overflow rule that
would 400, compaction as "the primary strategy," cache-aware tool-result clearing with
all four configuration rules, and the memory-before-clear dance.

**Read first:** [0008 · Context management](../../../lessons/0008-context-management.html)

## The setup

`fixtures.py` (given, working) provides a deliberate `estimate_tokens` approximation
(~4 chars/token — swap in the Token Counting API when real), a `summarize()` fixture,
a `MemoryStore` standing in for the memory tool, and builders for fat Apex histories
full of oversized tool results. Your job is the five TODOs in `context.py`:

1. **`count_tokens(messages)`** — sum over *everything*: text and tool_result blocks
   alike. The budget box.
2. **`would_overflow(messages, window)`** — input alone over the window: the check
   that must run before sending, because "prompt is too long" is a 400.
3. **`compact(messages, keep_recent)`** — the primary strategy: older turns become ONE
   summary message; the recent tail survives verbatim.
4. **`clear_tool_results(...)`** — the full `clear_tool_uses` rulebook: fires only past
   `trigger`; clears oldest-first with `PLACEHOLDER` text; never touches the `keep`
   most recent results nor `exclude_tools`; and if achievable savings are below
   `clear_at_least`, changes nothing (`applied=False`) — don't torch the cache for a
   trickle.
5. **`save_essentials_before_clearing(...)`** — inside the warning zone (≥ 90% of
   threshold), persist essentials to memory; below it, save nothing.

## Done means

`python3 verify.py` shows M5 **GREEN** — all 11 checks, including the trickle-clear
prevention and the verbatim-tail guarantee. Paste `project: M5:11/11` to your agent
and say **"next milestone"**.
