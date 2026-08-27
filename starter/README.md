# The Claude Starter Kit

The fundamentals of Claude as **correct-by-construction, runnable code** — the
foundation you copy into any project. Zero dependencies, offline (fixtures by
default; wire a real SDK into `RealClient` when ready).

    python3 selfcheck.py    # proves every fundamental holds
    python3 example.py      # watches them work end-to-end

## The modules (one per law cluster)

| Module | Fundamentals it enforces |
|---|---|
| `client.py` | The request contract: full history, ends-with-user, stop-reason switchboard, the echo rule, tool_result placement |
| `tools.py` | Interface discipline (four-question audit), tool execution, the error taxonomy, instructive errors, idempotency |
| `context.py` | The budget: what counts, the 400 rule, compaction, cache-aware clearing, memory-before-clear |
| `patterns.py` | Composition: routing (with privacy lanes), gated chains, voting, effort scaling, orchestrator-workers |
| `evals.py` | Evidence & economics: outcome suites, cross-model judging, the real cost multipliers, invalidation hierarchy |

## How to use it on a new project

1. Copy `claude/` into your project.
2. Walk the **build-anything playbook** (`reference/build-anything-playbook.html`) phase by phase.
3. Check yourself against the **ten laws** (`reference/foundations-of-claude.html`) at every gate.
4. When you're ready for the real API, implement `RealClient.complete` with the SDK — the contract is already enforced around it.

Everything here mirrors the course: each module cites its laws, and the
[Apex Project](../project/) is the gym where you build the same muscles by hand.
