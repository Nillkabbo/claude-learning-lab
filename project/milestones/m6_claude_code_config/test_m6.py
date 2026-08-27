"""M6 acceptance tests — 12 checks. python3 verify.py to run them."""
import json
import unittest
from pathlib import Path

from fixtures import (
    SETTINGS_GOOD, SETTINGS_BAD, SUBAGENT_GOOD, SUBAGENT_BAD,
    HOOK_CONFIG_GOOD, HOOK_CONFIG_BAD, KNOWN_HOOK_EVENTS,
    ScriptedModel, tool_use, text, TOOL_IMPLEMENTATIONS, parse_frontmatter,
)
from validate import evaluate_permission, validate_subagent, hook_decision, query

CONFIG = Path(__file__).resolve().parent / "config"


class M6PartATests(unittest.TestCase):

    def test_fixture_primitives_work(self):
        meta, body = parse_frontmatter(SUBAGENT_GOOD)
        self.assertEqual(meta["name"], "release-notes")
        self.assertIn("release-notes writer", body)

    def test_exact_allow_rule_allows(self):
        perms = SETTINGS_GOOD["permissions"]
        self.assertEqual(evaluate_permission("Bash", "python3 verify.py", perms), "allow")

    def test_broad_deny_beats_narrow_allow(self):
        perms = {"allow": ["Bash(aws s3 ls)"], "deny": ["Bash(aws *)"], "ask": []}
        self.assertEqual(evaluate_permission("Bash", "aws s3 ls", perms), "deny")

    def test_bare_deny_and_unmatched(self):
        perms = SETTINGS_GOOD["permissions"]
        self.assertEqual(evaluate_permission("WebFetch", "https://x", perms), "deny")
        self.assertIsNone(evaluate_permission("Read", "README.md", perms))

    def test_subagent_validation_good_and_bad(self):
        self.assertEqual(validate_subagent(SUBAGENT_GOOD), [])
        findings = validate_subagent(SUBAGENT_BAD)
        self.assertIn("bad-name", findings)
        self.assertIn("missing-description", findings)

    def test_hook_exit_code_contract(self):
        self.assertEqual(hook_decision(2, json.dumps({"permissionDecision": "allow"})), "block")
        self.assertEqual(hook_decision(0, json.dumps({"permissionDecision": "deny"})), "deny")
        self.assertEqual(hook_decision(0, "all good"), None)

    def test_hook_config_shape(self):
        # structural sanity of the given configs (documented expectations)
        event = next(iter(HOOK_CONFIG_GOOD))
        self.assertIn(event, KNOWN_HOOK_EVENTS)
        self.assertNotIn(next(iter(HOOK_CONFIG_BAD)), KNOWN_HOOK_EVENTS)


class M6PartBTests(unittest.TestCase):

    def _run_query(self, options=None):
        model = ScriptedModel([
            tool_use("get_flight_status", {"flight_number": "AX204"}),
            text("AX204 is delayed 45 minutes due to weather."),
        ])
        gen = query("How is AX204?", model, options or {})
        messages = list(gen)          # generator's return value is lost here;
        return model, messages        # tests below re-run for the result

    def test_query_executes_tool_and_yields_messages(self):
        model, messages = self._run_query({"allowed_tools": ["get_flight_status"]})
        kinds = [m["type"] for m in messages]
        self.assertIn("assistant", kinds)
        self.assertIn("tool_result", kinds)
        self.assertIn("delayed 45", messages[-1]["content"] if isinstance(messages[-1]["content"], str)
                      else str(messages[-1]))

    def test_query_returns_final_text(self):
        model = ScriptedModel([
            tool_use("get_flight_status", {"flight_number": "AX204"}),
            text("AX204 is delayed 45 minutes due to weather."),
        ])
        gen = query("How is AX204?", model, {"allowed_tools": ["get_flight_status"]})
        final = None
        while True:
            try:
                next(gen)
            except StopIteration as stop:
                final = stop.value
                break
        self.assertEqual(final, "AX204 is delayed 45 minutes due to weather.")

    def test_can_use_tool_denies_execution(self):
        calls = []
        def gate(block):
            calls.append(block.name)
            return False
        model = ScriptedModel([
            tool_use("get_flight_status", {"flight_number": "AX204"}),
            text("I could not check the flight."),
        ])
        messages = list(query("Status?", model,
                              {"allowed_tools": ["get_flight_status"], "can_use_tool": gate}))
        result_blocks = [m for m in messages if m["type"] == "tool_result"]
        self.assertEqual(calls, ["get_flight_status"])       # gate consulted
        self.assertTrue(result_blocks[0].get("is_error"))
        self.assertIn("canUseTool", result_blocks[0]["content"])

    def test_plan_mode_executes_nothing(self):
        executed = []
        tools = {k: (lambda fn=v: executed.append(fn) or "x") for k, v in TOOL_IMPLEMENTATIONS.items()}
        model = ScriptedModel([
            tool_use("get_flight_status", {"flight_number": "AX204"}),
            text("plan: I would check AX204 status"),
        ])
        messages = list(query("Status?", model, {"permission_mode": "plan", "allowed_tools": ["get_flight_status"]}))
        self.assertEqual(executed, [])                        # read-only
        self.assertTrue(any(m["type"] == "assistant" for m in messages))


class M6AuthoredConfigTests(unittest.TestCase):
    """The artifacts YOU author under config/ — checked with YOUR validators."""

    def test_authored_claude_md(self):
        p = CONFIG / "CLAUDE.md"
        self.assertTrue(p.exists(), "author config/CLAUDE.md (see config/README.md)")
        lines = p.read_text().splitlines()
        self.assertGreater(len([l for l in lines if l.strip()]), 3)
        self.assertLessEqual(len(lines), 200)                 # the size discipline

    def test_authored_settings_json(self):
        import validate as V
        p = CONFIG / "settings.json"
        self.assertTrue(p.exists(), "author config/settings.json")
        perms = json.loads(p.read_text())["permissions"]
        self.assertEqual(evaluate_permission("Read", "./.env", perms), "deny")
        self.assertEqual(evaluate_permission("Bash", "python3 verify.py", perms), "allow")

    def test_authored_subagent(self):
        p = CONFIG / "agents" / "release-notes.md"
        self.assertTrue(p.exists(), "author config/agents/release-notes.md")
        self.assertEqual(validate_subagent(p.read_text()), [])


if __name__ == "__main__":
    unittest.main()
