"""M1 acceptance tests — 8 checks. python3 verify.py to run them."""
import unittest

from fixtures import FixtureModel, text_response, truncated_response, refusal_response
from conversation import ConversationManager, TruncatedResponse, RefusedResponse


def make_manager(*scripted):
    return ConversationManager(FixtureModel(list(scripted)))


class M1Tests(unittest.TestCase):

    def test_fixture_model_works(self):
        m = make_manager(text_response("hello"))
        req = {"model": "x", "max_tokens": 10, "system": "s", "messages": [{"role": "user", "content": "hi"}]}
        resp = m.model.complete(req)
        self.assertEqual(resp.content[0].text, "hello")
        self.assertEqual(m.model.requests_seen[0], req)

    def test_history_contains_all_turns(self):
        m = make_manager(text_response("Answer one."), text_response("Answer two."))
        m.turn("Question one")
        m.turn("Question two")
        request = m.build_request(system="s")
        msgs = request["messages"]
        self.assertEqual([msg["role"] for msg in msgs],
                         ["user", "assistant", "user", "assistant", "user"])

    def test_request_ends_with_user_message(self):
        m = make_manager(text_response("Answer."))
        m.turn("Question")
        request = m.build_request(system="s")
        self.assertEqual(request["messages"][-1]["role"], "user")

    def test_system_prompt_and_max_tokens_in_request(self):
        m = make_manager(text_response("ok"))
        request = m.build_request(system="Apex policy prompt", max_tokens=512)
        self.assertEqual(request["system"], "Apex policy prompt")
        self.assertEqual(request["max_tokens"], 512)
        self.assertIn("model", request)

    def test_stop_reason_end_turn_completes(self):
        m = make_manager(text_response("Your balance is $412.50."))
        text = m.turn("What's my balance?")
        self.assertEqual(text, "Your balance is $412.50.")
        self.assertEqual(m.messages[-1]["role"], "assistant")

    def test_stop_reason_max_tokens_signals_truncation(self):
        m = make_manager(truncated_response())
        with self.assertRaises(TruncatedResponse):
            m.turn("Long report please")

    def test_stop_reason_refusal_flags_escalation(self):
        m = make_manager(refusal_response())
        with self.assertRaises(RefusedResponse):
            m.turn("Something forbidden")
        self.assertTrue(m.escalate)

    def test_fix_legacy_request(self):
        m = make_manager()
        legacy = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 512,
            "temperature": 0,
            "output_format": {"type": "json_schema", "schema": {"type": "object"}},
            "messages": [
                {"role": "user", "content": "Report?"},
                {"role": "assistant", "content": "{"},
            ],
        }
        fixed = m.fix_legacy_request(legacy)
        self.assertNotIn("temperature", fixed)                       # dial retired
        self.assertEqual(fixed["messages"][-1]["role"], "user")      # prefill stripped
        self.assertNotIn("output_format", fixed)                     # parameter moved
        self.assertEqual(fixed["output_config"]["format"]["type"], "json_schema")
        self.assertEqual(legacy["messages"][-1]["role"], "assistant")  # input untouched


if __name__ == "__main__":
    unittest.main()
