"""M8 starter — implement the TODO sections. Read BRIEF.md first.

Lesson 0016 as a harness: normalized exact match, an LLM-judge with the
cross-model rule, outcome-based suites. Lesson 0017 as arithmetic: the
batch discount, the cache multipliers, and the invalidation hierarchy.
"""
from fixtures import (
    BATCH_DISCOUNT, CACHE_READ_MULTIPLIER, CACHE_WRITE_MULTIPLIER, PRICES,
)


class SameModelJudgingError(Exception):
    """The judge is the generator — it inherits its own blind spots."""


# ------------------------------------------------------------------
# TODO 1: exact_match(actual, expected)  (0016: the spectrum's floor)
# Normalize whitespace and case on both sides, then compare.
# ------------------------------------------------------------------
def exact_match(actual, expected):
    raise NotImplementedError("TODO 1: exact_match")


# ------------------------------------------------------------------
# TODO 2: llm_judge(output, judge, rubric, threshold=0.8)  (0016)
# Enforce the cross-model rule FIRST: if judge["name"] equals
# output["generator"], raise SameModelJudgingError — every official
# example judges with a different model.
# Otherwise score via judge["fn"](output, rubric) and return
# {"score": s, "passed": s >= threshold}.
# ------------------------------------------------------------------
def llm_judge(output, judge, rubric, threshold=0.8):
    raise NotImplementedError("TODO 2: llm_judge")


# ------------------------------------------------------------------
# TODO 3: run_suite(cases)  (0016: outcome-based, volume > polish)
# Each case: {"id", "expected", "actual", "grader": "exact_match"}.
# Grade every case by OUTCOME; return
# {"total": n, "passed": k, "failures": [ids that failed]}.
# ------------------------------------------------------------------
def run_suite(cases):
    raise NotImplementedError("TODO 3: run_suite")


# ------------------------------------------------------------------
# TODO 4: monthly_cost(usage, prices, batch=False, cache=True)  (0017)
# Token amounts are in millions; prices per million.
# Input side (prices["input"]):
#   cache=True  -> reads ×0.1, writes ×1.25, uncached ×1.0
#   cache=False -> all input (uncached + reads + writes) ×1.0
# Output side: output_mtok × prices["output"], always ×1.0
# batch=True multiplies the WHOLE total by 0.5 (it stacks).
# ------------------------------------------------------------------
def monthly_cost(usage, prices, batch=False, cache=True):
    raise NotImplementedError("TODO 4: monthly_cost")


# ------------------------------------------------------------------
# TODO 5: invalidated_levels(change)  (0017: the hierarchy)
# change: {"layer": "tools" | "system" | "messages"}
# tools -> 3 (tools, system, messages all die)
# system -> 2 ; messages -> 1
# ------------------------------------------------------------------
def invalidated_levels(change):
    raise NotImplementedError("TODO 5: invalidated_levels")
