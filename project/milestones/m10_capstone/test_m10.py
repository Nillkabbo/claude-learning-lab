"""M10 acceptance tests — 12 checks. python3 verify.py to run them."""
import tempfile
import unittest
from pathlib import Path

from fixtures import (
    CANNED_ABUSIVE, COMPETITORS, DIRTY_DRAFT, SAFETY_VERDICTS, POLICY_TOPICS,
    classify, Recorder, make_worker, DIGEST_PLAN, EVAL_CASES, USAGE, PRICES,
    ARCHITECTURE,
)
from capstone import handle_ticket, nightly_digest, report_card, master_checklist


def make_ctx():
    return {
        "classifier": classify,
        "draft": DIRTY_DRAFT,
        "competitors": COMPETITORS,
        "verdicts": SAFETY_VERDICTS,
        "policy_topics": POLICY_TOPICS,
        "canned_abusive": CANNED_ABUSIVE,
        "vote_threshold": 2,
    }


class M10Tests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.artifacts = Path(self.tmp.name)

    def test_fixture_primitives_work(self):
        self.assertEqual(classify("gate for my flight"), "easy")
        self.assertIn("SSN", DIRTY_DRAFT)

    def test_abusive_ticket_gets_no_model(self):
        r = handle_ticket("you idiot give me a refund", make_ctx())
        self.assertEqual(r["lane"], "abusive")
        self.assertFalse(r["model_called"])
        self.assertEqual(r["response"], CANNED_ABUSIVE)

    def test_easy_lane_drafts_with_enforced_compliance(self):
        r = handle_ticket("gate for my flight please", make_ctx())
        self.assertEqual(r["lane"], "easy")
        self.assertTrue(r["model_called"])
        self.assertNotIn("123-45-6678", r["response"])      # PII stripped
        self.assertNotIn("SkyRival Airlines", r["response"])  # competitor gone
        self.assertIn("[PII removed]", r["response"])

    def test_vote_flags_and_escalates(self):
        r = handle_ticket("gate for my flight please", make_ctx())
        self.assertTrue(r["flagged"])                         # 2-of-3
        self.assertTrue(r["escalated"])
        self.assertTrue(any("vote" in reason for reason in r["reasons"]))

    def test_regulated_lane_enforces_privacy(self):
        r = handle_ticket("I want to file a compensation claim", make_ctx())
        self.assertEqual(r["lane"], "regulated")
        self.assertTrue(r["privacy_enforced"])

    def test_digest_saves_plan_before_workers(self):
        recorder = Recorder()
        nightly_digest(DIGEST_PLAN, make_worker(recorder), self.artifacts, recorder)
        self.assertLess(recorder.events.index("plan-saved"),
                        recorder.events.index("worker:ops"))
        self.assertTrue((self.artifacts / "plan.md").exists())

    def test_digest_references_and_failure_isolation(self):
        recorder = Recorder()
        result = nightly_digest(DIGEST_PLAN, make_worker(recorder, fail_area="crew"),
                                self.artifacts, recorder)
        self.assertEqual({f["area"] for f in result["failures"]}, {"crew"})
        self.assertEqual({r["area"] for r in result["references"]}, {"ops", "maintenance"})
        self.assertIn("crew", result["report"])

    def test_report_card_counts_outcomes(self):
        card = report_card(EVAL_CASES, USAGE, PRICES, batch=True)
        self.assertEqual(card["eval"]["total"], 10)
        self.assertEqual(card["eval"]["passed"], 8)
        self.assertEqual(card["eval"]["failures"], [4, 9])

    def test_report_card_math_stacks_batch_and_cache(self):
        cached_input = (0.50 * 0.1 * 3.00) + (0.25 * 1.25 * 3.00) + (0.25 * 3.00)
        expected = (cached_input + 1.00 * 15.00) * 0.5
        card = report_card(EVAL_CASES, USAGE, PRICES, batch=True)
        self.assertAlmostEqual(card["monthly_cost"], expected)

    def test_report_card_summary_is_pasteable(self):
        card = report_card(EVAL_CASES, USAGE, PRICES, batch=True)
        self.assertIn("8/10", card["summary"])
        self.assertIn("$", card["summary"])

    def test_master_checklist_names_missing_items(self):
        missing = master_checklist(ARCHITECTURE)
        self.assertEqual(missing, ["economics", "lifecycle"])
        self.assertEqual(master_checklist({k: True for k in ARCHITECTURE}), [])

    def test_cli_module_exists(self):
        import cli
        self.assertTrue(callable(getattr(cli, "main", None)))


if __name__ == "__main__":
    unittest.main()
