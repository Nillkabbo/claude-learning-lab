"""M8 fixtures — graders, a 20-case suite, judges, and usage numbers.

Given code. Judges are deterministic fns of (output, rubric) -> score in
[0,1]; the cross-model rule is enforced by YOUR harness, not the judge.
"""


# --- grader spectrum material (0016) ---------------------------------------------

CASES_20 = []
for i in range(20):
    expected = "delayed" if i % 2 == 0 else "on time"
    actual_is_wrong = (i in (3, 11, 17))          # three failures, deterministic
    CASES_20.append({
        "id": i,
        "input": f"flight AX{i:03d} status",
        "expected": expected,
        "actual": "on time" if actual_is_wrong != (i % 2 == 0) else expected,
        "generator": "sonnet-4-6",
        "grader": "exact_match",
    })

RUBRIC = ["factual accuracy", "citation accuracy", "completeness", "source quality", "tool efficiency"]

STRONG_OUTPUT = {"generator": "sonnet-4-6", "text": "AX204 delayed 45m [source: ops]"}

JUDGE_OPUS = {"name": "opus-5", "fn": lambda output, rubric: 0.95}
JUDGE_HAIKU = {"name": "haiku-4-5", "fn": lambda output, rubric: 0.60}
JUDGE_SONNET = {"name": "sonnet-4-6", "fn": lambda output, rubric: 0.99}   # same as generator!


# --- cost model material (0017) ----------------------------------------------------
# Prices per MILLION tokens; token counts in millions (floats are fine).

PRICES = {"input": 3.00, "output": 15.00}

USAGE_MIXED = {
    "uncached_input_mtok": 0.25,
    "cached_read_mtok": 0.50,
    "cached_write_mtok": 0.25,
    "output_mtok": 1.00,
}

BATCH_DISCOUNT = 0.5        # flat, stacks with caching
CACHE_READ_MULTIPLIER = 0.1
CACHE_WRITE_MULTIPLIER = 1.25
