"""M5 acceptance tests — 11 checks. python3 verify.py to run them."""
import unittest

from fixtures import (
    estimate_tokens, MemoryStore, user_msg, assistant_msg, tool_result_msg, big_history,
)
from context import ContextManager, PLACEHOLDER


class M5Tests(unittest.TestCase):

    def setUp(self):
        self.cm = ContextManager()

    def test_fixture_primitives_work(self):
        self.assertGreater(estimate_tokens("a" * 400), 90)
        mem = MemoryStore()
        mem.save("k", "v")
        self.assertEqual(mem.load("k"), "v")

    def test_count_tokens_counts_tool_results_too(self):
        msgs = [user_msg("hi"), tool_result_msg("t1", "x" * 400)]
        total = self.cm.count_tokens(msgs)
        self.assertGreater(total, 100)

    def test_would_overflow_is_the_400_rule(self):
        msgs = big_history(n_turns=4)
        self.assertTrue(self.cm.would_overflow(msgs, window=200))
        self.assertFalse(self.cm.would_overflow(msgs, window=10_000))

    def test_compact_replaces_old_with_summary_and_shrinks(self):
        msgs = big_history(n_turns=4)          # 12 messages
        compacted = self.cm.compact(msgs, keep_recent=4)
        self.assertEqual(len(compacted), 5)    # 1 summary + 4 kept
        self.assertIn("[conversation summary]", compacted[0]["content"])
        self.assertLess(self.cm.count_tokens(compacted), self.cm.count_tokens(msgs))

    def test_compact_keeps_recent_tail_verbatim(self):
        msgs = big_history(n_turns=4)
        compacted = self.cm.compact(msgs, keep_recent=4)
        self.assertEqual(compacted[1:], msgs[-4:])

    def test_clearing_fires_past_trigger_oldest_first(self):
        msgs = big_history(n_turns=5)
        new_msgs, cleared, applied = self.cm.clear_tool_results(msgs, trigger=100, keep=2, clear_at_least=0)
        self.assertTrue(applied)
        self.assertGreater(cleared, 0)
        self.assertEqual(new_msgs[1]["content"][0]["content"], PLACEHOLDER)   # oldest cleared
        self.assertNotEqual(new_msgs[-1]["content"][0]["content"], PLACEHOLDER)  # newest kept

    def test_clearing_respects_keep_count(self):
        msgs = big_history(n_turns=5)
        new_msgs, _, applied = self.cm.clear_tool_results(msgs, trigger=100, keep=3, clear_at_least=0)
        untouched = [m for m in new_msgs
                     if m.get("content") and isinstance(m["content"], list)
                     and m["content"][0].get("content") != PLACEHOLDER
                     and m["content"][0].get("type") == "tool_result"]
        self.assertEqual(len(untouched), 3)

    def test_excluded_tools_are_never_cleared(self):
        msgs = big_history(n_turns=5)
        for m in msgs:
            m["tool"] = "web_search"
        new_msgs, cleared, applied = self.cm.clear_tool_results(
            msgs, trigger=100, keep=0, clear_at_least=0, exclude_tools=("web_search",))
        self.assertFalse(applied)
        self.assertEqual(cleared, 0)
        self.assertEqual(new_msgs, msgs)

    def test_clear_at_least_prevents_trickle_clears(self):
        msgs = [user_msg("tiny"), tool_result_msg("t1", "y" * 40), assistant_msg("ok")]
        new_msgs, cleared, applied = self.cm.clear_tool_results(
            msgs, trigger=5, keep=0, clear_at_least=10_000)
        self.assertFalse(applied)                 # savings below the bar
        self.assertEqual(new_msgs, msgs)          # nothing changed

    def test_memory_before_clear_saves_essentials_in_warning_zone(self):
        msgs = big_history(n_turns=4)
        mem = MemoryStore()
        keys = self.cm.save_essentials_before_clearing(msgs, mem, threshold=self.cm.count_tokens(msgs) + 1)
        self.assertTrue(keys)
        self.assertTrue(all(mem.load(k) for k in keys))

    def test_no_saving_below_warning_zone(self):
        msgs = [user_msg("hello")]
        mem = MemoryStore()
        keys = self.cm.save_essentials_before_clearing(msgs, mem, threshold=1_000_000)
        self.assertEqual(keys, [])
        self.assertEqual(mem.keys(), [])


if __name__ == "__main__":
    unittest.main()
