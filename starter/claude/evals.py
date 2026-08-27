"""evals.py — evidence and economics. Law 10."""


class SameModelJudgingError(Exception):
    """The judge is the generator — it inherits its own blind spots."""


def exact_match(actual, expected):
    """The spectrum's floor: normalized equality."""
    norm = lambda s: " ".join(str(s).split()).lower()
    return norm(actual) == norm(expected)


def llm_judge(output, judge, rubric, threshold=0.8):
    """Cross-model rule FIRST; then score via judge['fn'](output, rubric)."""
    if judge["name"] == output.get("generator"):
        raise SameModelJudgingError(
            f"{judge['name']} judged its own output — use a different model")
    score = judge["fn"](output, rubric)
    return {"score": score, "passed": score >= threshold}


def run_suite(cases):
    """Outcome-based: totals plus failing ids — ready to paste."""
    failures = [c["id"] for c in cases if not exact_match(c["actual"], c["expected"])]
    return {"total": len(cases), "passed": len(cases) - len(failures), "failures": failures}


BATCH_DISCOUNT = 0.5
CACHE_READ_MULTIPLIER = 0.1
CACHE_WRITE_MULTIPLIER = 1.25


def monthly_cost(usage, prices, batch=True, cache=True):
    """The arithmetic: reads 0.1x, writes 1.25x, batch stacks on everything."""
    input_price = prices["input"]
    if cache:
        input_cost = (usage.get("cached_read_mtok", 0) * CACHE_READ_MULTIPLIER
                      + usage.get("cached_write_mtok", 0) * CACHE_WRITE_MULTIPLIER
                      + usage.get("uncached_input_mtok", 0)) * input_price
    else:
        total_input = sum(usage.get(k, 0) for k in
                          ("cached_read_mtok", "cached_write_mtok", "uncached_input_mtok"))
        input_cost = total_input * input_price
    output_cost = usage.get("output_mtok", 0) * prices["output"]
    total = input_cost + output_cost
    return total * BATCH_DISCOUNT if batch else total


INVALIDATION = {"tools": 3, "system": 2, "messages": 1}


def invalidated_levels(change):
    """The hierarchy: tools -> 3 levels die, system -> 2, messages -> 1."""
    return INVALIDATION[change["layer"]]
