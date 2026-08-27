# M1 · Request anatomy (lessons 0001–0003)

You are building the foundation of the Apex Assistant: a `ConversationManager` that owns
the conversation for a stateless model — correctly, in every situation the course taught.

**Read first:** [0001 · The anatomy of a Claude request](../../../lessons/0001-anatomy-of-a-claude-request.html)
· [0002 · System prompts & prefilling](../../../lessons/0002-system-prompts-and-prefilling.html)
· [0003 · Output control](../../../lessons/0003-output-control.html)

## The setup

`fixtures.py` (given, working) provides a `FixtureModel` — a stand-in for the real API
that returns scripted `Response` objects. `conversation.py` gives you the types and the
`FixtureModel`; your job is the four TODO sections:

1. **`build_request(system, max_tokens)`** — produce the request dict the API contract
   demands: the *full* message history in order, the system prompt, a sane `max_tokens`.
   Remember what Lesson 0001 says the second request must contain, and what a request
   must always end with.
2. **`handle_response(response)`** — branch on `stop_reason` exactly as Lesson 0003's
   switchboard says: `end_turn` completes the turn; `max_tokens` means truncation (raise
   `TruncatedResponse`); `refusal` must set `escalate=True` and never be retried
   blindly; a text reply's content gets appended to history as the assistant turn.
3. **`fix_legacy_request(request)`** — Apex inherited 2025-era code. Migrate one request
   dict to current-model rules (Lesson 0002 + 0003): drop any `temperature` that isn't
   1.0 (the dial is retired), remove a trailing assistant message (retired prefill —
   requests must end with a user message), and rename the old `output_format` parameter
   to `output_config.format`.
4. **`turn(user_text)`** — the glue: build, call the model, handle the response, repeat
   until the turn completes. Return the assistant's text.

## Done means

`python3 verify.py` shows M1 **GREEN** — all 8 checks. Then paste the report line to
your agent (`project: M1 8/8`) and say **"next milestone"**.

## Hints (only if stuck)

- The messages array is the conversation. If it's not all there, in order, the API model
  of 0001 is being violated.
- `stop_reason` is control flow, not trivia — each value has an owner action.
- The migration fixer is pure dict surgery: three independent fixes, three asserts.
