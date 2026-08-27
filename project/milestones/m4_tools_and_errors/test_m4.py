"""M4 acceptance tests — 10 checks. python3 verify.py to run them."""
import unittest

from fixtures import (
    GOOD_TOOL, SHORT_DESCRIPTION_TOOL, PARAM_WITHOUT_DESCRIPTION_TOOL,
    OPEN_WORLD_TOOL, PR_TOOLS,
    TransientError, PermanentError, UncertainStateError,
    rate_limited_flight_search, unknown_airport, charge_card_timeout,
)
from tools import audit_tool, consolidate, classify_error, tool_result_for, IdempotencyLedger


class M4Part1InterfaceTests(unittest.TestCase):

    def test_fixture_primitives_work(self):
        with self.assertRaises(TransientError):
            rate_limited_flight_search()

    def test_good_tool_passes_audit_cleanly(self):
        self.assertEqual(audit_tool(GOOD_TOOL), [])

    def test_audit_flags_short_description(self):
        self.assertIn("description-too-short", audit_tool(SHORT_DESCRIPTION_TOOL))

    def test_audit_flags_missing_param_description_and_open_world(self):
        findings = audit_tool(PARAM_WITHOUT_DESCRIPTION_TOOL)
        self.assertIn("param-missing-description:query", findings)
        findings = audit_tool(OPEN_WORLD_TOOL)
        self.assertIn("open-world:cabin", findings)

    def test_audit_flags_unnamespaced_name(self):
        bad_name = dict(GOOD_TOOL, name="flightstatus")
        self.assertIn("name-not-namespaced", audit_tool(bad_name))

    def test_consolidate_merges_pr_tools_with_action_enum(self):
        merged = consolidate(PR_TOOLS)
        self.assertEqual(merged["name"], "github_pr")
        action = merged["input_schema"]["properties"]["action"]
        self.assertEqual(set(action["enum"]), {"create", "review", "merge"})
        self.assertIn("action", merged["input_schema"]["required"])


class M4Part2ErrorTests(unittest.TestCase):

    def test_classify_error_covers_the_taxonomy(self):
        self.assertEqual(classify_error(TransientError("x", 30)), "transient")
        self.assertEqual(classify_error(PermanentError("x", "alt")), "permanent")
        self.assertEqual(classify_error(UncertainStateError("x", "hint")), "uncertain")

    def test_transient_result_is_instructive_with_retry_parameters(self):
        block = tool_result_for(TransientError("Flight search rate limited.", 30))
        self.assertTrue(block.get("is_error"))
        self.assertIn("Retry after 30 seconds", block["content"])

    def test_permanent_result_names_the_alternative(self):
        block = tool_result_for(unknown_airport("AUST"))
        self.assertIn("search_airports", block["content"])

    def test_uncertain_result_demands_verification(self):
        block = tool_result_for(charge_card_timeout())
        self.assertIn("UNKNOWN", block["content"])
        self.assertIn("do not retry", block["content"].lower())

    def test_ledger_charges_once_per_key(self):
        ledger = IdempotencyLedger()
        calls = []
        def expensive_charge():
            calls.append(1)
            return "CHARGE-OK-7"
        first = ledger.run("book-AX204-jane", expensive_charge)
        second = ledger.run("book-AX204-jane", expensive_charge)   # the retry
        self.assertEqual(first, second)
        self.assertEqual(len(calls), 1)                            # fn ran once


if __name__ == "__main__":
    unittest.main()
