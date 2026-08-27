# FACTS-TO-REVERIFY — the staleness tripwire

The curriculum's sharpest facts, pinned to August-2026 documentation. Claude moves
fast; before relying on any of this for the real exam, re-verify the load-bearing
ones against their sources. Tripwire: the official Exam Guide's version/date line
(v1.0, effective July 2026, when parsed) — a new version means re-check everything.

## Before booking the exam (must re-verify)

| Fact | Source | Status |
|---|---|---|
| Domain names + weights (27/18/20/20/15) | Official Exam Guide PDF (`resources/ccar-f-exam-guide.txt` §4) | parsed 2026-08-27 |
| 4-of-6 scenario structure; the six scenarios | Exam Guide §5 | parsed 2026-08-27 |
| MC + multiple-response formats; 720 pass; $125; 120 min | Exam Guide §3 | parsed 2026-08-27 |
| Booking gate: Partner Academy work email + Partner Network org | Skilljar page | fetched 2026-08-26 |

## Model-behavior facts (highest reversal risk)

| Fact | Source | Status |
|---|---|---|
| Prefill unsupported on Claude 4.6+ (trailing assistant → 400) | platform.claude.com/api/errors, working-with-messages | fetched 2026-08-27 |
| Temperature only 1.0 on post-Opus-4.6 models (else 400); top_k rejected | Messages API reference | fetched 2026-08-27 |
| output_format → output_config.format migration; Python SDK TypeError | structured outputs page | fetched 2026-08-27 |
| Thinking budget counts against max_tokens; effort = low→max | API reference | fetched 2026-08-27 |
| Newer Opus over-responds to system prompts (soften ALL-CAPS) | prompting best practices | fetched 2026-08-27 |

## Economics (numbers change with pricing pages)

| Fact | Source | Status |
|---|---|---|
| Batch flat 50%, stacks with caching; 24h expiry; 100K req/256MB | batch-processing page | fetched 2026-08-27 |
| Cache writes 1.25×/2×; reads 0.1×; invalidation tools→system→messages | prompt-caching page | fetched 2026-08-27 |

## Tooling facts (docs move weekly — 166 pages, weekly digest)

| Fact | Source | Status |
|---|---|---|
| CLAUDE.md scope ladder, @imports ≤4 hops, "context not enforcement" | code.claude.com/docs/memory | fetched 2026-08-27 |
| Permission eval deny→ask→allow; trust gating; hooks exit-2; fail-open | permissions + hooks refs | fetched 2026-08-27 |
| Subagents: description-driven, 20 concurrent/3 deep | sub-agents page | fetched 2026-08-27 |
| Agent SDK: Python/TS only; query(); canUseTool; CLI -p JSON for others | SDK overview + quickstart | fetched 2026-08-27 |
| MCP security: token passthrough forbidden; sessions must not auth; progressive scopes | MCP spec 2025-11-25 security_best_practices | fetched verbatim 2026-08-27 |

## Standing external gaps (never verified)

- CCAR-P official blueprint (third-party corroborated: 14% stakeholder/lifecycle, 7% dev productivity, $175, 63 items)
- Anthropic "mitigating prompt injection" post (unreachable, 3 attempts — substance covered by lessons 0007/0021)
