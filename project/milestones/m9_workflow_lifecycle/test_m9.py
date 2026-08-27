"""M9 acceptance tests — 12 checks. python3 verify.py to run them."""
import unittest

from fixtures import (
    CONVERSATION, POLICY_TOPICS, DIRTY_RESPONSE, CLEAN_RESPONSE, COMPETITORS,
    FAILURE_CATALOG, INTEGRATION_BAD, INTEGRATION_CLEAN,
)
from workflow import escalate, compliance_stack, degrade, paired_metrics, mcp_review


class M9Tests(unittest.TestCase):

    def test_fixture_primitives_work(self):
        self.assertIn("SSN", DIRTY_RESPONSE)
        self.assertEqual(len(FAILURE_CATALOG), 3)

    def test_low_confidence_escalates_with_real_handoff(self):
        result = escalate(CONVERSATION, confidence=0.3, policy_topics=POLICY_TOPICS)
        self.assertTrue(result["escalate"])
        hand = result["handoff"]
        self.assertIn("compensation claim", hand["summary"])
        self.assertEqual(hand["state"]["turns"], 3)
        self.assertTrue(hand["provenance"])

    def test_policy_topic_escalates(self):
        result = escalate(CONVERSATION, confidence=0.95, policy_topics=POLICY_TOPICS)
        self.assertTrue(result["escalate"])
        self.assertTrue(any("policy" in r for r in result["reasons"]))

    def test_high_confidence_no_policy_no_escalation(self):
        clean = [{"role": "user", "content": "Gate for AX204?"},
                 {"role": "assistant", "content": "Gate 12."}]
        result = escalate(clean, confidence=0.97, policy_topics=POLICY_TOPICS)
        self.assertFalse(result["escalate"])

    def test_compliance_strips_pii(self):
        filtered, flags = compliance_stack(DIRTY_RESPONSE, COMPETITORS)
        self.assertNotIn("123-45-6678", filtered)
        self.assertIn("[PII removed]", filtered)
        self.assertIn("pii", flags)

    def test_compliance_replaces_competitor_and_leaves_clean(self):
        filtered, flags = compliance_stack(DIRTY_RESPONSE, COMPETITORS)
        self.assertNotIn("SkyRival Airlines", filtered)
        self.assertIn("competitor", flags)
        clean, no_flags = compliance_stack(CLEAN_RESPONSE, COMPETITORS)
        self.assertEqual(clean, CLEAN_RESPONSE)
        self.assertEqual(no_flags, [])

    def test_every_failure_has_a_designed_exit(self):
        for failure in FAILURE_CATALOG:
            exit_ = degrade(failure)
            self.assertTrue(exit_["message"].strip(), f"silent failure for {failure}")
            self.assertTrue(exit_["offer"].strip())
            self.assertTrue(exit_["action"].strip())

    def test_mid_charge_timeout_verifies_never_retries_blindly(self):
        exit_ = degrade("mid_charge_timeout")
        self.assertIn("UNKNOWN", exit_["message"])
        self.assertIn("verify", exit_["message"].lower())
        self.assertNotIn("retry now", exit_["message"].lower())

    def test_status_api_down_degrades_honestly(self):
        exit_ = degrade("status_api_down")
        self.assertIn("unavailable", exit_["message"])
        self.assertIn("static", exit_["offer"].lower())

    def test_paired_metrics_healthy(self):
        result = paired_metrics(0.75, 4.3)
        self.assertTrue(result["healthy"])
        self.assertEqual(result["flags"], [])

    def test_paired_metrics_detects_gaming(self):
        result = paired_metrics(0.93, 3.2)
        self.assertFalse(result["healthy"])
        self.assertIn("gaming", result["flags"])

    def test_mcp_review_flags_and_approves(self):
        findings = mcp_review(INTEGRATION_BAD)
        self.assertEqual(set(findings), {"token-passthrough-forbidden", "scope-inflation",
                                         "sessions-must-not-authenticate", "consent-missing"})
        self.assertEqual(mcp_review(INTEGRATION_CLEAN), [])


if __name__ == "__main__":
    unittest.main()
