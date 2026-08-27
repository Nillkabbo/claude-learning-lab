"""M8 acceptance tests — 12 checks. python3 verify.py to run them."""
import unittest

from fixtures import (
    CASES_20, RUBRIC, STRONG_OUTPUT, JUDGE_OPUS, JUDGE_HAIKU, JUDGE_SONNET,
    PRICES, USAGE_MIXED,
)
from evalcost import (
    exact_match, llm_judge, run_suite, monthly_cost, invalidated_levels,
    SameModelJudgingError,
)


class M8EvalTests(unittest.TestCase):

    def test_fixture_primitives_work(self):
        self.assertEqual(len(CASES_20), 20)
        self.assertEqual(JUDGE_OPUS["fn"](STRONG_OUTPUT, RUBRIC), 0.95)

    def test_exact_match_normalizes(self):
        self.assertTrue(exact_match("Delayed ", "DELAYED"))
        self.assertFalse(exact_match("delayed", "on time"))

    def test_cross_model_rule_is_enforced(self):
        with self.assertRaises(SameModelJudgingError):
            llm_judge(STRONG_OUTPUT, JUDGE_SONNET, RUBRIC)      # judge == generator
        result = llm_judge(STRONG_OUTPUT, JUDGE_OPUS, RUBRIC)   # different model
        self.assertTrue(result["passed"])

    def test_judge_threshold_decides(self):
        self.assertFalse(llm_judge(STRONG_OUTPUT, JUDGE_HAIKU, RUBRIC)["passed"])   # 0.60
        self.assertTrue(llm_judge(STRONG_OUTPUT, JUDGE_OPUS, RUBRIC)["passed"])     # 0.95

    def test_suite_is_outcome_based(self):
        report = run_suite(CASES_20)
        self.assertEqual(report["total"], 20)
        self.assertEqual(report["passed"], 17)
        self.assertEqual(report["failures"], [3, 11, 17])

    def test_suite_reports_a_pasteable_summary(self):
        report = run_suite(CASES_20)
        self.assertIn("passed", report) and self.assertIn("failures", report)


class M8CostTests(unittest.TestCase):

    def test_base_cost_no_batch_no_cache(self):
        usage = {"uncached_input_mtok": 1.0, "cached_read_mtok": 0.0,
                 "cached_write_mtok": 0.0, "output_mtok": 1.0}
        self.assertAlmostEqual(monthly_cost(usage, PRICES, batch=False, cache=False),
                               1.0 * 3.00 + 1.0 * 15.00)

    def test_batch_halves_everything(self):
        usage = {"uncached_input_mtok": 1.0, "cached_read_mtok": 0.0,
                 "cached_write_mtok": 0.0, "output_mtok": 1.0}
        self.assertAlmostEqual(monthly_cost(usage, PRICES, batch=True, cache=False),
                               (1.0 * 3.00 + 1.0 * 15.00) * 0.5)

    def test_cache_multipliers_apply(self):
        # reads 0.5×0.1×3 + writes 0.25×1.25×3 + uncached 0.25×3 + output 1×15
        expected = (0.5 * 0.1 * 3.00) + (0.25 * 1.25 * 3.00) + (0.25 * 3.00) + (1.0 * 15.00)
        self.assertAlmostEqual(monthly_cost(USAGE_MIXED, PRICES, batch=False, cache=True), expected)

    def test_batch_and_cache_stack(self):
        cached = monthly_cost(USAGE_MIXED, PRICES, batch=False, cache=True)
        stacked = monthly_cost(USAGE_MIXED, PRICES, batch=True, cache=True)
        self.assertAlmostEqual(stacked, cached * 0.5)

    def test_invalidation_hierarchy(self):
        self.assertEqual(invalidated_levels({"layer": "tools"}), 3)
        self.assertEqual(invalidated_levels({"layer": "system"}), 2)
        self.assertEqual(invalidated_levels({"layer": "messages"}), 1)


if __name__ == "__main__":
    unittest.main()
