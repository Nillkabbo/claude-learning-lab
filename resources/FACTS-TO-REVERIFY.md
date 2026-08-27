# FACTS-TO-REVERIFY — the staleness tripwire

Last full re-verification: **2026-08-27 (second pass)**. All facts below confirmed
against live official documentation on this date.

## Re-verification results (2026-08-27, second pass)

### 🔴 REVERSED — prefilling is now SUPPORTED
- **Was taught as**: retired on Claude 4.6+ (400 error on trailing assistant messages)
- **Current truth**: fully supported; the only limitation is unavailability with
  extended thinking modes. Code examples use claude-sonnet-4-5.
- **Fix applied**: lessons 0002, 0003, glossary, both mocks, phase-1 review corrected

### ✅ CONFIRMED — API facts
| Fact | Source | Status |
|---|---|---|
| Temperature: only 1.0 on post-Opus-4.6; else 400 | Messages API ref | confirmed |
| top_k: also deprecated (400, no backwards compat) | Messages API ref | confirmed (new detail) |
| Structured outputs: output_config.format; same unsupported constraints | structured outputs page | confirmed |
| Batch: flat 50%; 24h max; 100K requests/256MB | batch-processing page | confirmed |
| Cache reads 0.1×; writes 1.25× (5-min) / 2× (1-hour) | prompt-caching page | confirmed |
| Invalidation hierarchy: tools→system→messages | prompt-caching page | confirmed |
| 1M-token windows default on current models | context-windows page | confirmed |
| Compaction = "primary strategy" (server-side, beta on 4.6+) | context-windows page | confirmed |
| stop_reason: end_turn, max_tokens, stop_sequence, model_context_window_exceeded, refusal, tool_use | context-windows page | confirmed (7 values now) |
| Input alone exceeding window → 400 "prompt is too long" | context-windows page | confirmed |

### ✅ CONFIRMED — Claude Code facts
| Fact | Source | Status |
|---|---|---|
| Native install (curl\|bash) recommended | quickstart | confirmed |
| Auth: Pro/Max/Team/Console/Bedrock/Vertex/Foundry + self-hosted gateway (new) | quickstart | confirmed |
| CLAUDE.md loaded recursively upward; "context, not enforced configuration" | memory page | confirmed |
| @imports max 4 hops | memory page | confirmed |
| Permissions: deny→ask→allow, first match; trust-gated allows | permissions page | confirmed |
| Permission modes: default, acceptEdits, plan, **auto** (new), **dontAsk** (new), bypassPermissions | permissions page | confirmed (expanded) |
| Subagents: description-driven; 20 concurrent / 3-deep (now configurable) | sub-agents page | confirmed |
| Agent SDK: Python/TS only; CLI subprocess for others | SDK overview | confirmed |

### ✅ CONFIRMED — Exam facts
| Fact | Source | Status |
|---|---|---|
| $125; 60 items; 120 min; 720/1000 pass | Skilljar + exam guide PDF | confirmed |
| Exam guide Version 1.0, effective July 2026 | PDF | confirmed |
| 4 scenarios from bank of 6 | exam guide §5 | confirmed |
| MC + multiple-response formats | exam guide §3 | confirmed |

### ✅ CONFIRMED — MCP security
| Fact | Source | Status |
|---|---|---|
| Token passthrough forbidden | MCP spec security page | confirmed |
| Sessions must not authenticate | MCP spec security page | confirmed |

## Standing gaps (still open)
- CCAR-P official blueprint: still unpublished (third-party corroborated only)
- Prompt-injection engineering post: still unreachable (substance in lessons 0007/0021)

## Next re-verification trigger
- A new Exam Guide version (currently v1.0 July 2026)
- Or: before booking the exam (whichever comes first)
