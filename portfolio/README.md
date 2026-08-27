# Insight — a Claude-powered code analyzer

A real, working CLI that analyzes code for security, correctness, and
maintainability issues — and, in the same codebase, demonstrates all **ten
laws of Claude in production** ([foundations](../reference/foundations-of-claude.html))
by composing every module of the
[starter kit](../starter/README.md). Offline-first: it runs on scripted
fixtures with zero dependencies, and swaps in the live Messages API with one
flag. Built phase-by-phase per the
[build-anything playbook](../reference/build-anything-playbook.html).

```bash
python3 portfolio/insight.py analyze portfolio/fixtures/code_samples/auth.py
python3 portfolio/insight.py analyze portfolio/fixtures/code_samples/   # a directory
python3 portfolio/insight.py report                                     # last run, summarized
python3 portfolio/insight.py cost                                       # the bill, explained
python3 portfolio/insight.py eval                                       # 14-case eval suite
python3 portfolio/tests/test_insight.py                                 # 26 unit tests
python3 portfolio/insight.py analyze <your-file.py> --real              # live API (~$0.02)
```

No API key, no network, no dependencies for anything above except `--real`.

## Architecture

```
                     ┌──────────────────────────────────────────────────┐
                     │                    insight.py                    │
                     │        analyze · report · eval · cost (CLI)      │
                     └───────────────────────┬──────────────────────────┘
                                             │
                     ┌───────────────────────▼──────────────────────────┐
                     │                   analyzer.py                    │
                     │  SYSTEM_PROMPT (policy) · routing · parse · cost │
                     └───┬──────────┬──────────┬──────────┬─────────┬───┘
                         │          │          │          │         │
              ┌──────────▼───┐ ┌────▼─────┐ ┌──▼───────┐ ┌▼────────┐ ┌▼────────┐
              │   client.py  │ │ tools.py │ │context.py│ │patterns │ │ evals.py│
              │ Law 1: full  │ │ Law 5:   │ │ Law 7:   │ │ Law 9:  │ │ Law 10: │
              │  history per │ │  read/   │ │  400     │ │  route/ │ │  cost w/│
              │  request     │ │  grep/   │ │  check + │ │  gates/ │ │  real   │
              │ Law 2: stop_ │ │  glob +  │ │  clear + │ │  vote   │ │  cache  │
              │  reason →    │ │  ledger  │ │  compact │ │         │ │  batch  │
              │  action      │ │ Law 6:   │ │          │ │         │ │  rules  │
              │ Law 3: build │ │  error   │ │          │ │         │ │         │
              │  + system    │ │  taxonomy│ │          │ │         │ │         │
              └──────┬───────┘ └────┬─────┘ └──────────┘ └─────────┘ └─────────┘
                     │              │
              ┌──────▼──────────────▼──────┐        ┌────────────────────────┐
              │ FixtureModel (default)      │        │ RealClient (--real)    │
              │ replays fixtures/responses  │        │ stdlib urllib → the    │
              │ .py — deterministic, free   │        │ live Messages API      │
              └─────────────────────────────┘        └────────────────────────┘
```

The engine never knows which model it is talking to — that is Law 1 paying
rent: because every request is self-contained, the transport is a swap.

## The ten laws, live in this code

| Law | Module | Where in Insight | Demo it |
|-----|--------|------------------|---------|
| 1 Statelessness | `client.RequestBuilder` | `run_conversation` resends full history every request | `grep "check_context(messages)" analyzer.py` — rebuilt, not resumed |
| 2 Content blocks | `client.handle_response` | text + tool_use blocks dispatched on stop_reason | watch a deep run: tool_use → tools → end_turn |
| 3 System prompt = policy | `analyzer.SYSTEM_PROMPT` | role, scope, output shape, do-nots in one place | `grep -A8 "SYSTEM_PROMPT" analyzer.py` |
| 4 Validation layers | `patterns.chain_with_gates` + `_semantic_pass` | locate JSON → grammar → severity/line/dedupe checks | `tests/test_insight.py::TestValidationLayers` |
| 5 Tool loop | `tools.ToolRunner` | read/grep/glob execute; assistant turn echoed; tool_results placed as next user message | the api_handler.py run: 3 tool calls |
| 6 Error taxonomy | `tools.TransientError` etc | retry (.writing files), adapt (bad regex → fixed_string), verify (mtime check → UncertainStateError) | `tests/test_insight.py::TestToolDiscipline` |
| 7 Context budget | `context.*` | 400 pre-check, cache-aware clearing, then compaction — before every send | `check_context()` + `TestContextBudget` |
| 8 Enforcement | `.claude/settings.json` | deny-list: no secrets reads, no rm -rf, no force push — policy that cannot be talked around | read the file; try a denied read in Claude Code |
| 9 Complexity purchase | `patterns.route` | ≤30-line files: one call. Bigger: the tool loop. Gates + vote where they pay | `utils.py` (1 request) vs `auth.py` (2+) |
| 10 Evidence + economics | `evals.run_suite` + `monthly_cost` | 14-case eval vs ground truth; cost with 0.1x cache reads, no fake batch discount | `insight.py eval`, `insight.py cost` |

## The interview script

*"Walk me through this project."* (~90 seconds)

> Insight is a CLI code analyzer I built to prove I understand how Claude
> works at the API level, not just through a chat window. You point it at a
> file and it reports security and quality findings as validated JSON.
>
> The core is a stateless conversation loop. Every request rebuilds the full
> history — the system prompt is the policy, the model's turn is echoed back
> intact, and tool results go in as the next user message. The model's
> stop_reason drives everything: end_turn means done, tool_use means I
> execute the read, grep, and glob tools and loop.
>
> Two things make it more than a demo. First, it routes complexity: small
> files get a single call, big files get the full tool loop — I only buy the
> expensive pattern when it pays. Second, nothing the model says is trusted:
> findings pass a gated validation chain — JSON grammar, then semantic checks
> like severity enums and line bounds — and if the file changed mid-analysis,
> an UncertainStateError discards the run rather than report stale evidence.
>
> It's offline-first: a FixtureModel replays scripted responses that obey the
> same contract as the real API, so the whole thing — including the eval
> suite — runs with no key and no network. One flag swaps in the real client.
> The eval suite scores it against seeded ground truth: 100% recall, zero
> false criticals, and cost per analysis computed with real cache multipliers
> — about one and a quarter cents a file.

### Likely follow-ups

- **"Why fixtures instead of just calling the API?"** Determinism and cost.
  The eval suite must be reproducible in CI with no key; FixtureModel obeys
  the same contract (stop_reasons, content blocks, usage), so the engine code
  is identical — only the transport differs.
- **"Where does it break?"** Long files beyond the lane threshold still fit
  the window; when they wouldn't, `check_context` clears old tool results
  first (cache-friendly), then compacts to a summary plus verbatim tail —
  and repairs the role-alternation boundary compaction can create, because
  the RequestBuilder refuses invalid requests anyway. Better a refused build
  than a mystery 400.
- **"How do you know the findings are right?"** Three layers. Grammar (JSON
  shape), semantics (enum severity, line bounds, dedupe), and the eval suite
  (outcome-based: did it find the seeded issues, with no false criticals,
  twice in a row — a `vote()` over reruns).
- **"Cost?"** `evals.monthly_cost` with real multipliers: input $3/MTok,
  cached reads at 0.1x, output $15/MTok, no batch discount because it's
  interactive. The `cost` command shows the arithmetic per file.
- **"Why is there a `.claude/` directory in the repo?"** Law 8: policy that
  can't be argued with. `CLAUDE.md` binds agents working here (never edit the
  fixtures to make evals pass), and `settings.json` denies reading secrets or
  running destructive commands outright.

## Design decisions

- **Fixture scripts include a deliberate failure.** The api_handler.py
  conversation calls grep with an invalid regex; the tool answers with a
  PermanentError instructive message ("pass fixed_string=true"), and the
  scripted model adapts. The error taxonomy isn't documented — it's
  exercised.
- **IdempotencyLedger guards reads.** Same path = one filesystem read per
  analysis, so a retrying model can't double-spend.
- **The four-question audit runs at construction.** `make_tools` asserts
  `audit(tool) == []` for every tool — an unaudited interface can't exist.
- **Cost is computed, not vibes.** Usage comes from response usage blocks,
  the first request pays uncached input, later requests count as cache reads,
  and `monthly_cost` applies the real multipliers.
- **`.writing` files raise TransientError.** A lock-file convention: the
  model is told to retry after 2s — retry is the model's decision, informed
  by the error (Law 6), not a blind loop in my code.

## Honest limitations

- Fixture mode analyzes only the three sample files; anything else gets an
  honest "no scripted response" empty result (or `--real`).
- One file at a time (a directory run is N independent analyses) — no
  cross-file reasoning yet; the natural next rung is the orchestrator-worker
  pattern from `patterns.py`.
- The severity/line numbers in fixture mode are only as good as the script;
  the real test of the analyzer is `--real` against unseen code, which costs
  about $0.02 a file to try.

## Files

| File | What it is |
|------|-----------|
| `insight.py` | CLI: analyze / report / eval / cost (+ `--real`) |
| `analyzer.py` | The engine — composes all five starter modules |
| `fixtures/code_samples/` | Three files with 8 seeded issues (the spec) |
| `fixtures/responses.py` | Scripted model responses + `SEED_ISSUES` ground truth |
| `tests/test_insight.py` | 26 tests: evidence, routing, tools, validation, budget |
| `.claude/CLAUDE.md` · `.claude/settings.json` | Policy + enforceable guardrails |
| `REQUIREMENTS.md` | Success criteria and how each is verified |
