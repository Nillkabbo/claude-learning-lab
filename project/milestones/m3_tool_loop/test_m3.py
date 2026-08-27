"""M3 acceptance tests — 10 checks. python3 verify.py to run them."""
import unittest

from fixtures import (
    ScriptedToolModel, tool_use_response, parallel_tool_response, text_response,
)
from loop import ToolLoopRunner, LoopLimitReached


def simple_runner():
    """A two-step script: ask for flight status, then answer."""
    return ToolLoopRunner(ScriptedToolModel([
        tool_use_response("get_flight_status", {"flight_number": "AX204"}, tool_id="toolu_A"),
        text_response("Flight AX204 is delayed 45 minutes due to weather."),
    ]))


class M3Tests(unittest.TestCase):

    def test_fixture_model_and_tools_work(self):
        m = ScriptedToolModel([text_response("hi")])
        r = ToolLoopRunner(m)
        self.assertIn("delayed 45", r.tools["get_flight_status"]({"flight_number": "AX204"}))

    def test_loop_returns_final_text_after_tool_use(self):
        r = simple_runner()
        text = r.run_turn("How's AX204 doing?")
        self.assertEqual(text, "Flight AX204 is delayed 45 minutes due to weather.")

    def test_history_has_the_canonical_shape(self):
        r = simple_runner()
        r.run_turn("How's AX204 doing?")
        roles = [m["role"] for m in r.messages]
        self.assertEqual(roles, ["user", "assistant", "user", "assistant"])

    def test_tool_result_matches_tool_use_id(self):
        r = simple_runner()
        r.run_turn("How's AX204 doing?")
        result_msg = r.messages[2]
        block = result_msg["content"][0]
        self.assertEqual(block["tool_use_id"], "toolu_A")
        self.assertIn("delayed 45", block["content"])

    def test_result_message_contains_only_tool_results(self):
        r = simple_runner()
        r.run_turn("How's AX204 doing?")
        result_msg = r.messages[2]
        self.assertTrue(all(b["type"] == "tool_result" for b in result_msg["content"]))

    def test_assistant_turn_is_echoed_in_full(self):
        r = simple_runner()
        r.run_turn("How's AX204 doing?")
        first_assistant = r.messages[1]["content"]
        self.assertEqual(first_assistant[0]["type"], "tool_use")   # not stripped
        self.assertEqual(first_assistant[0]["name"], "get_flight_status")

    def test_parallel_tool_calls_one_message_two_results(self):
        r = ToolLoopRunner(ScriptedToolModel([
            parallel_tool_response([
                ("get_flight_status", {"flight_number": "AX204"}, "toolu_1"),
                ("search_airports", {"query": "austin"}, "toolu_2"),
            ]),
            text_response("AX204 from Austin: delayed 45 minutes."),
        ]))
        r.run_turn("AX204 status and confirm the airport")
        result_msg = r.messages[2]
        ids = [b["tool_use_id"] for b in result_msg["content"]]
        self.assertEqual(ids, ["toolu_1", "toolu_2"])

    def test_unknown_tool_returns_instructive_error_result(self):
        r = ToolLoopRunner(ScriptedToolModel([
            tool_use_response("book_first_class", {}, tool_id="toolu_X"),
            text_response("I can't book first class."),
        ]))
        r.run_turn("Upgrade me")
        block = r.messages[2]["content"][0]
        self.assertTrue(block.get("is_error"))
        self.assertIn("book_first_class", block["content"])

    def test_max_turns_stops_the_loop(self):
        infinite = [tool_use_response("search_airports", {"query": "x"}, tool_id=f"t{i}")
                    for i in range(50)]
        r = ToolLoopRunner(ScriptedToolModel(infinite))
        with self.assertRaises(LoopLimitReached):
            r.run_turn("Keep searching", max_turns=3)

    def test_every_request_carries_full_history(self):
        r = simple_runner()
        r.run_turn("How's AX204 doing?")
        last_request = r.model.requests_seen[-1]
        roles = [m["role"] for m in last_request["messages"]]
        self.assertEqual(roles, ["user", "assistant", "user"])   # ends with user; all prior turns present


if __name__ == "__main__":
    unittest.main()
