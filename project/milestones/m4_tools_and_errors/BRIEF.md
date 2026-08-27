# M4 · Tools & errors (lessons 0006–0007)

Two halves of the same craft: the **interface audit** (Lesson 0006 — descriptions,
enums, consolidation as enforceable rules) and the **error taxonomy** (Lesson 0007 —
transient / permanent / uncertain, instructive results, and the idempotency ledger
that makes retries safe by construction).

**Read first:** [0006 · Designing tool interfaces](../../../lessons/0006-designing-tool-interfaces.html)
· [0007 · Error handling in agent tools](../../../lessons/0007-error-handling-in-agent-tools.html)

## The setup

`fixtures.py` (given, working) provides: the taxonomy as types (`TransientError` with
`retry_after`, `PermanentError` with `alternative`, `UncertainStateError` with
`verify_hint`), raisers for the three Apex failures, a `GOOD_TOOL` that passes a proper
audit, offenders that don't (short description, naked param, open-world cabin), and the
three `github_*_pr` tools begging for consolidation. Your job is the five TODOs in
`tools.py`:

1. **`audit_tool(tool_def)`** — four deterministic axes: description under three
   sentences; params without their own descriptions; a "one of" description without an
   `enum` (a closed world described but not enforced); an un-namespaced name.
2. **`consolidate(tools)`** — merge `github_create_pr` / `github_review_pr` /
   `github_merge_pr` into one `github_pr` tool with a required `action` enum — "fewer,
   more capable tools reduce selection ambiguity."
3. **`classify_error(exc)`** — map exception types to the taxonomy.
4. **`tool_result_for(exc)`** — the instructive `is_error` result: transient carries its
   retry parameters, permanent names its alternative verbatim, uncertain says UNKNOWN
   and contains "do not retry".
5. **`IdempotencyLedger.run(key, fn)`** — same key, one execution: the charge fires
   once no matter how many times the retry lands on it.

## Done means

`python3 verify.py` shows M4 **GREEN** — all 11 checks, including the ledger proving
`fn` ran exactly once across a retry. Paste `project: M4:11/11` to your agent and say
**"next milestone"**.
