# Insight — Requirements

The success criteria for the portfolio analyzer. Phase 1 of the
build-anything playbook: know what "done" means before building.

## Requirements

| # | Requirement | Target | Verified by |
|---|-------------|--------|-------------|
| 1 | Recall of seeded issues | ≥ 90% | `python3 portfolio/insight.py eval` (recall case) + `tests/test_insight.py` |
| 2 | Critical-finding precision | ≥ 95% (zero false criticals) | eval (critical-precision case) + `test_no_false_criticals` |
| 3 | Cost per analysis | < $0.05 with the real API | eval (cost case) + `test_cost_under_budget_per_file` — priced from fixture usage, same multipliers |
| 4 | Runs offline | zero dependencies, no API key | every command below runs with no network and no env vars |

## Definition of done

- `python3 portfolio/insight.py analyze portfolio/fixtures/code_samples/auth.py` prints findings
- `python3 portfolio/insight.py eval` exits 0 (all cases pass)
- `python3 portfolio/tests/test_insight.py` exits 0 (26 tests)
- All ten laws of Claude demonstrably used (see README table)
- Analyzer imports all five starter modules — `grep "from starter.claude" portfolio/analyzer.py`

## Out of scope (deliberately)

- No cross-file analysis (one file, or one directory of files, per run)
- No auto-fixing — Insight reports, humans decide
- No persistence beyond `.insight/last-run.json` (a convenience, not a database)
- No batching or async — an interactive CLI pays no batch discount
