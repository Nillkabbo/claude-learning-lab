# M7 · Composition patterns (lessons 0013–0015)

The workflow kit, runnable: routing with its three wins (focus, cost, privacy), gated
chains, voting thresholds as a precision/recall dial, effort scaling rules, and the
orchestrator-workers digest — plan saved to memory first, filesystem artifacts,
references not contents, failure isolation.

**Read first:** [0013 · Workflows vs agents](../../../lessons/0013-workflows-vs-agents.html)
· [0014 · Composition patterns](../../../lessons/0014-composition-patterns.html)
· [0015 · Orchestrator-workers](../../../lessons/0015-orchestrator-workers.html)

## The setup

`fixtures.py` (given, working): a ticket classifier, model tiers, a canned abusive
response, chain steps and gates (including one that always fails), three screener
verdicts, a `Recorder` that timestamps the order of operations, a worker factory that
writes markdown artifacts (and can be told to fail one area), and a three-area
due-diligence plan. Your job is the five TODOs in `patterns.py`:

1. **`route(ticket, classifier)`** — easy→Haiku, hard→Sonnet, regulated→the
   certified model with `privacy_enforced: True`, abusive→the canned response with
   `model: None` (no LLM call at all).
2. **`chain_with_gates(steps, gates)`** — run a step, check its gate, continue; a
   failing gate stops the chain dead (`failed_at=i`) — programmatic checks, never
   model calls.
3. **`vote(verdicts, threshold)`** — count over threshold flags; the threshold is the
   business decision.
4. **`scale_effort(complexity)`** — the embedded rules: 1 worker/10 calls, 2/15,
   10+/uncapped.
5. **`orchestrate(query, plan, worker, artifact_dir, recorder)`** — save `plan.md`
   and log `plan-saved` BEFORE any worker; collect area+path references (not
   contents); isolate failures into a `failures` list without stopping survivors;
   synthesize a report naming every area — including failed ones, visibly.

## Done means

`python3 verify.py` shows M7 **GREEN** — all 13 checks, including the order-proof that
the plan was saved before the first worker ran, and the anti-telephone test that what
came back were references, not artifacts' contents. Paste `project: M7:13/13` to your
agent and say **"next milestone"**.
