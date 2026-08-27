"""test_sync.py — verifies milestone fixtures stay in sync with the starter kit.

The starter kit is the canonical reference; milestones are deliberately self-contained
(each lesson is standalone). This test catches drift: if a milestone's types diverge
from the starter's, it fails with a specific message.

Run: python3 -m unittest starter/test_sync.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path

STARTER = Path(__file__).parent / "claude"
MILESTONES = Path(__file__).parent.parent / "project" / "milestones"


class SyncTests(unittest.TestCase):

    def _load(self, path, stem):
        spec = importlib.util.spec_from_file_location(stem, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[stem] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_m1_fixture_types_match_starter(self):
        starter = self._load(STARTER / "client.py", "starter_client")
        m1 = self._load(MILESTONES / "m1_request_anatomy" / "fixtures.py", "m1_fixtures")
        for name in ["ContentBlock", "Response", "FixtureModel"]:
            self.assertTrue(hasattr(m1, name),
                            f"m1/fixtures.py missing {name}")
        cb = m1.ContentBlock("text", text="x")
        self.assertTrue(hasattr(cb, "text"))
        r = m1.Response([cb], "end_turn")
        self.assertTrue(hasattr(r, "usage"), "m1 Response missing usage (drift from starter)")

    def test_m3_fixture_types_match_starter(self):
        m3 = self._load(MILESTONES / "m3_tool_loop" / "fixtures.py", "m3_fixtures")
        cb = m3.ContentBlock("tool_use", id="t1", name="x", input={})
        self.assertTrue(hasattr(cb, "id"))
        r = m3.Response([cb], "tool_use")
        self.assertTrue(hasattr(r, "usage"), "m3 Response missing usage")

    def test_m6_fixture_types_match_starter(self):
        m6 = self._load(MILESTONES / "m6_claude_code_config" / "fixtures.py", "m6_fixtures")
        cb = m6.ContentBlock("tool_use", id="t1", name="x", input={})
        self.assertTrue(hasattr(cb, "tool_use_id"),
                        "m6 ContentBlock missing tool_use_id (fixed in review — should not regress)")
        r = m6.Response([cb], "tool_use")
        self.assertTrue(hasattr(r, "usage"), "m6 Response missing usage (fixed in review)")

    def test_m4_error_types_match_starter(self):
        starter = self._load(STARTER / "tools.py", "starter_tools")
        m4 = self._load(MILESTONES / "m4_tools_and_errors" / "fixtures.py", "m4_fixtures")
        for name in ["TransientError", "PermanentError", "UncertainStateError"]:
            self.assertTrue(hasattr(m4, name), f"m4/fixtures.py missing {name}")
            exc_cls = getattr(m4, name)
            self.assertTrue(issubclass(exc_cls, Exception), f"m4 {name} is not an Exception")

    def test_starter_requestbuilder_enforces_contract(self):
        client = self._load(STARTER / "client.py", "starter_client2")
        builder = client.RequestBuilder()
        # Valid request builds fine
        msgs = [{"role": "user", "content": "hi"}]
        builder.build(msgs, system="test")  # should not raise
        # Empty messages
        with self.assertRaises(client.ContractViolation):
            builder.build([], system="test")
        # Trailing assistant (prefill)
        with self.assertRaises(client.ContractViolation):
            builder.build([{"role": "user", "content": "x"},
                           {"role": "assistant", "content": "y"}], system="test")
        # Consecutive user without tool_result
        with self.assertRaises(client.ContractViolation):
            builder.build([{"role": "user", "content": "x"},
                           {"role": "user", "content": "y"}], system="test")
        # tool_result in an assistant message
        with self.assertRaises(client.ContractViolation):
            builder.build([
                {"role": "user", "content": "x"},
                {"role": "assistant", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "r"}]},
                {"role": "user", "content": "done"}
            ], system="test")


if __name__ == "__main__":
    unittest.main()
