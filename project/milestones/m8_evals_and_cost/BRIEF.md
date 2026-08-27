# M8 · Evaluation & cost (lessons 0016–0017)

The harness and the bill. On the eval side: normalized exact match, an LLM-judge with
the cross-model rule enforced by YOUR code, and an outcome-based 20-case suite. On the
cost side: the arithmetic that makes the lever map real — batch's flat 50%, the cache
multipliers (reads 0.1×, writes 1.25×), their stacking, and the invalidation hierarchy.

**Read first:** [0016 · Evaluation & feedback loops](../../../lessons/0016-evaluation-and-feedback-loops.html)
· [0017 · Batches, cost & latency](../../../lessons/0017-batches-cost-latency.html)

## The setup

`fixtures.py` (given, working): a 20-case suite with exactly three deterministic
failures, a five-criterion rubric, three judges (one of which IS the generator — the
trap), prices per million tokens, and a realistic usage mix (uncached/read/write/output).
Your job is the five TODOs in `evalcost.py`:

1. **`exact_match(actual, expected)`** — normalized on whitespace and case: the
   spectrum's floor.
2. **`llm_judge(output, judge, rubric, threshold)`** — enforce the cross-model rule
   FIRST (`SameModelJudgingError` when the judge's name equals the generator's), then
   score and threshold.
3. **`run_suite(cases)`** — outcome-based: totals plus the failing ids, ready to paste.
4. **`monthly_cost(usage, prices, batch, cache)`** — the arithmetic: reads at 0.1×,
   writes at 1.25×, uncached at 1× (all input at 1× when caching is off), output
   always full price, and batch multiplying the whole total by 0.5 — because it stacks.
5. **`invalidated_levels(change)`** — the hierarchy as a number: a tools change kills
   3 levels, system 2, messages 1.

## Done means

`python3 verify.py` shows M8 **GREEN** — all 11 checks, including the same-model trap
raising and the stacking test proving batch+cache multiply. Paste `project: M8:11/11`
to your agent and say **"next milestone"**.
