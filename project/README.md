# The Apex Project

**Build the whole roadmap with your hands.** One project — a production-grade support
and research assistant for the fictional Apex Airlines — built in ten milestones, each
one mapped to the lessons of the [Claude Architect course](../reference/claude-architect-roadmap.html).
Every concept you studied, you will now implement, break, and fix.

## How it teaches

- **Offline-first**: a fixture-driven model client stands in for the real API — zero
  dependencies, zero API keys, pure Python 3 standard library. (A real key is optional
  prestige; nothing here requires it.)
- **Brief → TODO → tests**: each milestone has a `BRIEF.md` (the what and why, linked to
  lessons), a starter file with `TODO` markers, and a test suite that defines "done."
- **The report is the evidence**: run `python3 verify.py` and paste the report line to
  your agent. Green milestones are recorded as demonstrated mastery — this replaces the
  quiz-report loop.

## The milestones

| # | Milestone | Lessons | Status |
|---|---|---|---|
| M1 | Request anatomy — conversation manager, stop reasons, legacy migration | 0001–0003 | scaffolded |
| M2 | Structured outputs — schema'd extraction + semantic validation | 0004 | scaffolded |
| M3 | The tool loop — hand-built `tool_use` ↔ `tool_result` | 0005 | scaffolded |
| M4 | Tool interfaces & errors — descriptions, taxonomy, idempotency | 0006–0007 | scaffolded |
| M5 | Context management — accounting, summarization, memory-before-clear | 0008 | scaffolded |
| M6 | Claude Code config & Agent SDK — CLAUDE.md, permissions, hook, subagent, skill, `query()`-shaped wrapper + product posture | 0009–0012 | scaffolded |
| M7 | Composition patterns — router, gates, voting, orchestrator-workers | 0013–0015 | scaffolded |
| M8 | Evaluation & cost — eval harness, cross-model judging, the bill | 0016–0017 | scaffolded |
| M9 | Workflow design & lifecycle — escalation, degradation, runbook, threat model | 0018–0021 | scaffolded |
| M10 | Capstone — wire it all into the Apex Assistant CLI | 0022 | scaffolded |

Say **"next milestone"** to your agent to scaffold the next one after you've gone green.

## Workflow

```bash
cd project
python3 verify.py        # see where you stand
# pick the milestone's BRIEF.md, implement the TODOs in its starter file
python3 verify.py        # watch it go green
```

Then paste the report line to your agent:

```
project: M1 8/8
```

That line writes a learning record. Ten of those lines and the roadmap is yours.

## The scenario

Apex Airlines needs an assistant that answers passenger questions (status, baggage,
rebooking), runs a nightly operations digest, escalates safely to humans, survives
failures, and can justify its bill. Everything you studied — from statelessness to
rainbow deployments — has a job here.
