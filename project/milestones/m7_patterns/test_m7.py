"""M7 acceptance tests — 13 checks. python3 verify.py to run them."""
import tempfile
import unittest
from pathlib import Path

from fixtures import (
    CANNED_ABUSIVE_RESPONSE, classify_ticket,
    draft_step, gate_has_citations, gate_no_pii, FAILING_GATE,
    SCREEN_A, SCREEN_B, SCREEN_C,
    Recorder, make_worker, DEEP_DIVE_PLAN,
)
from patterns import route, chain_with_gates, vote, scale_effort, orchestrate


class M7Tests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.artifacts = Path(self.tmp.name)

    def test_fixture_primitives_work(self):
        self.assertEqual(classify_ticket("what time is my flight"), "easy")
        self.assertIn("DRAFT", draft_step("x"))

    def test_route_easy_goes_cheap(self):
        r = route("what time is my flight", classify_ticket)
        self.assertEqual(r["model"], "haiku")

    def test_route_regulated_enforces_privacy(self):
        r = route("I want to file a compensation claim", classify_ticket)
        self.assertEqual(r["model"], "certified-model")
        self.assertTrue(r["privacy_enforced"])

    def test_route_abusive_gets_no_model(self):
        r = route("you idiot, refund now or else", classify_ticket)
        self.assertIsNone(r["model"])
        self.assertEqual(r["response"], CANNED_ABUSIVE_RESPONSE)

    def test_chain_passes_all_gates(self):
        steps = [draft_step, lambda out: out + " [cited]"]
        gates = [gate_has_citations, gate_no_pii]
        output, failed_at = chain_with_gates(steps, gates)
        self.assertIsNone(failed_at)
        self.assertIn("[cited]", output)

    def test_chain_stops_at_failing_gate(self):
        steps = [draft_step, lambda out: out + " more"]
        gates = [gate_has_citations, FAILING_GATE]
        output, failed_at = chain_with_gates(steps, gates)
        self.assertEqual(failed_at, 1)
        self.assertNotIn("more", output)          # step after the gate never ran

    def test_vote_two_of_three_flags(self):
        result = vote([SCREEN_A, SCREEN_B, SCREEN_C], threshold=2)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["votes"], 3)

    def test_vote_below_threshold_does_not_flag(self):
        result = vote([True, False, False], threshold=2)
        self.assertFalse(result["flagged"])

    def test_scale_effort_matches_the_rules(self):
        self.assertEqual(scale_effort("simple"), (1, 10))
        self.assertEqual(scale_effort("comparison"), (2, 15))
        workers, cap = scale_effort("complex")
        self.assertGreaterEqual(workers, 10)
        self.assertIsNone(cap)

    def test_orchestrate_saves_plan_before_workers(self):
        recorder = Recorder()
        orchestrate("acquire TargetX", DEEP_DIVE_PLAN, make_worker(recorder), self.artifacts, recorder)
        self.assertTrue(recorder.assert_order("plan-saved", "worker:market"))
        self.assertTrue((self.artifacts / "plan.md").exists())

    def test_orchestrate_collects_references_not_contents(self):
        recorder = Recorder()
        result = orchestrate("acquire TargetX", DEEP_DIVE_PLAN, make_worker(recorder), self.artifacts, recorder)
        self.assertEqual({r["area"] for r in result["references"]}, {"market", "financials", "legal"})
        for ref in result["references"]:
            self.assertIn("artifact", ref)                     # a path reference…
            self.assertNotIn("findings", str(ref).lower())     # …not the contents
            self.assertTrue(Path(ref["artifact"]).exists())

    def test_orchestrate_report_names_every_area(self):
        recorder = Recorder()
        result = orchestrate("acquire TargetX", DEEP_DIVE_PLAN, make_worker(recorder), self.artifacts, recorder)
        for area in ("market", "financials", "legal"):
            self.assertIn(area, result["report"])

    def test_orchestrate_isolates_worker_failures(self):
        recorder = Recorder()
        result = orchestrate("acquire TargetX", DEEP_DIVE_PLAN,
                             make_worker(recorder, fail_area="legal"), self.artifacts, recorder)
        self.assertEqual({f["area"] for f in result["failures"]}, {"legal"})
        self.assertEqual({r["area"] for r in result["references"]}, {"market", "financials"})
        self.assertIn("legal", result["report"])               # the gap is visible, not hidden


if __name__ == "__main__":
    unittest.main()
