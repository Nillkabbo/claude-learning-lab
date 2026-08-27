# Insight — agent policy

Law 3: this file is policy, not a suggestion. If you (an agent) work in this
directory, these rules bind.

## Role

You are helping build **Insight**, a CLI code analyzer that demonstrates the
ten laws of Claude in production by composing the five starter modules
(`starter/claude/{client,tools,context,patterns,evals}.py`).

## Scope

- Only this directory (`portfolio/`) and, when asked, its references from
  `reference/*.html` and `publish.py`.
- Python 3 stdlib only. Zero dependencies is a hard requirement — the whole
  point is that the contract, not the SDK, is the product.

## Commands

- Run the suite: `python3 portfolio/tests/test_insight.py`
- Run the eval: `python3 portfolio/insight.py eval`
- Try it: `python3 portfolio/insight.py analyze portfolio/fixtures/code_samples/auth.py`

Both the suite and the eval must be green before you call any change done.

## Do not

- **Never edit `fixtures/responses.py` or `fixtures/code_samples/` to make a
  failing run pass.** They are the spec — SEED_ISSUES is ground truth, not an
  obstacle. Change the analyzer, not the truth.
- Never add try/except that swallows validation failures — a GrammarError is
  the system working.
- Never loosen a validation layer, a deny rule, or the eval threshold to
  unblock yourself; escalate instead.
- Never introduce caching of analysis results keyed by path alone — files
  change (that is what UncertainStateError is for).

## Style

- Match the starter kit: dataclasses over dicts where the starter uses them,
  instructive error messages an agent can act on, comments that cite the law
  they demonstrate.
- Every tool must pass `audit()` — namespaced name, four-question description,
  described schema properties.
