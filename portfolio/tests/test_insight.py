#!/usr/bin/env python3
"""test_insight.py — proves the analyzer earns its claims. Run:

    python3 portfolio/tests/test_insight.py

Zero dependencies (stdlib unittest). The eval command in insight.py scores
the same ground truth at the CLI level; these tests go one layer deeper:
routing, guardrails, the error taxonomy, validation layers, compaction.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

PORTFOLIO = Path(__file__).resolve().parent.parent
ROOT = PORTFOLIO.parent
for _p in (str(PORTFOLIO), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import analyzer
from fixtures.responses import SEED_ISSUES, script_for
from starter.claude.client import ContentBlock, FixtureModel, RequestBuilder
from starter.claude.tools import (IdempotencyLedger, PermanentError,
                                  TransientError, UncertainStateError)

SAMPLES = PORTFOLIO / "fixtures" / "code_samples"
SEED_FLAT = {f["id"]: f for seed in SEED_ISSUES.values() for f in seed}


def analyze(name):
    return analyzer.analyze_file(SAMPLES / name)


class MutatingModel:
    """FixtureModel wrapper that edits the target mid-conversation —
    forces the verify step (UncertainStateError) in analyze_file."""

    def __init__(self, inner, victim):
        self.inner, self.victim, self.touched = inner, Path(victim), False

    def complete(self, request):
        if not self.touched:
            self.touched = True
            self.victim.write_text(self.victim.read_text() + "\n# mid-flight edit\n")
        return self.inner.complete(request)


class TestEvidence(unittest.TestCase):
    """Law 10: the analyzer's claims, scored against the seed."""

    def test_finds_all_seeded_issues(self):
        found = {f["id"] for r in (analyze(n) for n in SEED_ISSUES)
                 for f in r["findings"]}
        recall = sum(1 for fid in SEED_FLAT if fid in found) / len(SEED_FLAT)
        self.assertGreaterEqual(recall, 0.90,
                                f"recall {recall:.0%} below the 90% requirement")

    def test_severities_match_seed(self):
        for name, seed in SEED_ISSUES.items():
            result = analyze(name)
            by_id = {f["id"]: f["severity"] for f in result["findings"]}
            for issue in seed:
                self.assertEqual(by_id.get(issue["id"]), issue["severity"],
                                 f"{issue['id']}: severity drift")

    def test_lines_match_seed(self):
        for name, seed in SEED_ISSUES.items():
            result = analyze(name)
            by_id = {f["id"]: f["line"] for f in result["findings"]}
            for issue in seed:
                self.assertEqual(by_id.get(issue["id"]), issue["line"],
                                 f"{issue['id']}: location drift")

    def test_no_false_criticals(self):
        results = [analyze(n) for n in SEED_ISSUES]
        criticals = [f["id"] for r in results for f in r["findings"]
                     if f["severity"] == "critical"]
        self.assertTrue(all(SEED_FLAT.get(c, {}).get("severity") == "critical"
                            for c in criticals),
                        f"false criticals: {criticals}")

    def test_cost_under_budget_per_file(self):
        for name in SEED_ISSUES:
            cost = analyze(name)["cost"]
            self.assertTrue(cost["under_budget"],
                            f"{name}: ${cost['total_usd']} over budget")

    def test_idempotent_reruns(self):
        for name in SEED_ISSUES:
            first, second = analyze(name), analyze(name)
            self.assertEqual(json.dumps(first["findings"]),
                             json.dumps(second["findings"]),
                             f"{name}: rerun produced different findings")


class TestRouting(unittest.TestCase):
    """Law 9: simple files get one call, big files the tool loop."""

    def test_utils_routes_simple(self):
        self.assertEqual(analyze("utils.py")["lane"], "simple")

    def test_auth_and_api_route_deep(self):
        self.assertEqual(analyze("auth.py")["lane"], "deep")
        self.assertEqual(analyze("api_handler.py")["lane"], "deep")

    def test_deep_lane_actually_uses_tools(self):
        result = analyze("api_handler.py")
        self.assertGreater(result["usage"]["tool_calls"], 0)
        self.assertEqual(result["mode"], "tool-loop")

    def test_simple_lane_is_one_request(self):
        result = analyze("utils.py")
        self.assertEqual(result["usage"]["requests"], 1)
        self.assertEqual(result["usage"]["tool_calls"], 0)


class TestToolDiscipline(unittest.TestCase):
    """Laws 5 + 6: audited interfaces, the taxonomy, the ledger."""

    def setUp(self):
        self.ledger = IdempotencyLedger()
        self.tools = {t.name: t for t in analyzer.make_tools(self.ledger)}
        self.runner = analyzer.ToolRunner(list(self.tools.values()))

    def test_every_tool_passes_the_audit(self):
        for tool in self.tools.values():
            self.assertEqual(analyzer.audit(tool), [],
                             f"{tool.name}: audit findings")

    def test_read_denies_secret_paths(self):
        block = ContentBlock("tool_use", id="t1", name="insight_read_file",
                             input={"path": "/tmp/env/.env-production"})
        result = self.runner.execute(block)
        self.assertTrue(result["is_error"])
        self.assertIn("Do not retry", result["content"])

    def test_missing_file_is_permanent_with_alternative(self):
        block = ContentBlock("tool_use", id="t2", name="insight_read_file",
                             input={"path": "/tmp/insight-nope-404.py"})
        result = self.runner.execute(block)
        self.assertTrue(result["is_error"])
        self.assertIn("insight_glob", result["content"])

    def test_midwrite_file_is_transient_with_retry_hint(self):
        with tempfile.NamedTemporaryFile(suffix=".writing", delete=False) as fh:
            fh.write(b"x = 1\n")
            path = fh.name
        with self.assertRaises(TransientError) as ctx:
            self.tools["insight_read_file"].fn({"path": path})
        self.assertEqual(ctx.exception.retry_after, 2)

    def test_invalid_regex_is_permanent_with_fixed_string_out(self):
        with self.assertRaises(PermanentError) as ctx:
            self.tools["insight_grep"].fn({"path": str(SAMPLES / "auth.py"),
                                           "pattern": "(unclosed"})
        self.assertIn("fixed_string", ctx.exception.alternative)
        hits = self.tools["insight_grep"].fn({"path": str(SAMPLES / "auth.py"),
                                              "pattern": "(unclosed",
                                              "fixed_string": True})
        self.assertEqual(hits, "no matches for /(unclosed/")

    def test_ledger_reads_each_path_once(self):
        path = str(SAMPLES / "utils.py")
        read = self.tools["insight_read_file"].fn
        first, second = read({"path": path}), read({"path": path})
        self.assertEqual(first, second)
        self.assertEqual(self.ledger.call_counts[path], 1)

    def test_unknown_tool_gets_instructive_error(self):
        block = ContentBlock("tool_use", id="t3", name="insight_nuke",
                             input={})
        result = self.runner.execute(block)
        self.assertTrue(result["is_error"])
        self.assertIn("insight_read_file", result["content"])


class TestValidationLayers(unittest.TestCase):
    """Law 4: grammar finds shape, code checks the claims."""

    def test_missing_json_raises_grammar_error(self):
        with self.assertRaises(analyzer.GrammarError):
            analyzer.parse_findings("I could not read the file, sorry.", 40)

    def test_malformed_json_raises_grammar_error(self):
        with self.assertRaises(analyzer.GrammarError):
            analyzer.parse_findings("```json\n{\"findings\": [}\n```", 40)

    def test_findings_without_list_raises_grammar_error(self):
        with self.assertRaises(analyzer.GrammarError):
            analyzer.parse_findings("```json\n{\"findings\": \"none\"}\n```", 40)

    def test_bad_severity_and_line_are_dropped_not_reported(self):
        payload = {"findings": [
            {"id": "x-bad-sev", "severity": "catastrophic", "line": 1,
             "title": "t", "evidence": "e", "recommendation": "r"},
            {"id": "x-bad-line", "severity": "info", "line": 9999,
             "title": "t", "evidence": "e", "recommendation": "r"},
            {"id": "x-dup", "severity": "info", "line": 2,
             "title": "t", "evidence": "e", "recommendation": "r"},
            {"id": "x-dup", "severity": "info", "line": 3,
             "title": "t", "evidence": "e", "recommendation": "r"},
            {"id": "x-good", "severity": "warning", "line": 4,
             "title": "t", "evidence": "e", "recommendation": "r"}]}
        parsed = analyzer.parse_findings("```json\n%s\n```"
                                         % json.dumps(payload), 10)
        self.assertEqual([f["id"] for f in parsed["findings"]],
                         ["x-dup", "x-good"])     # first x-dup is valid; dup dropped
        self.assertEqual(len(parsed["dropped"]), 3)


class TestUncertainState(unittest.TestCase):
    """Law 6 (verify): evidence that changed mid-analysis is discarded."""

    def test_file_edited_during_analysis_raises(self):
        path = SAMPLES / "auth.py"
        model = MutatingModel(FixtureModel(script_for(path, "deep")), path)
        with self.assertRaises(UncertainStateError) as ctx:
            analyzer.analyze_file(path, model=model)
        self.assertIn("re-run", ctx.exception.verify_hint)
        path.write_text(path.read_text().replace("\n# mid-flight edit\n", ""))


class TestContextBudget(unittest.TestCase):
    """Law 7: compact before the 400, keep the contract after."""

    def _big_history(self):
        filler = "filler " * 400
        return [{"role": "user", "content": filler},
                {"role": "assistant", "content": filler},
                {"role": "user", "content": filler},
                {"role": "assistant", "content": filler},
                {"role": "user", "content": filler},
                {"role": "assistant", "content": "recent turn"},
                {"role": "user", "content": "the actual question"}]

    def test_compaction_shrinks_and_stays_contract_valid(self):
        messages = self._big_history()
        before = analyzer.count_tokens(messages)
        out = analyzer.check_context(messages, window=300, trigger=10_000)
        self.assertLess(analyzer.count_tokens(out), before)
        RequestBuilder().build(out, analyzer.SYSTEM_PROMPT, 64)  # must not raise

    def test_repair_folds_double_user_boundary(self):
        messages = self._big_history()
        out = analyzer.check_context(messages, window=300, trigger=10_000)
        self.assertEqual(out[0]["role"], "user")
        if len(out) > 1 and out[1]["role"] == "user":
            self.assertIn("[conversation summary]", out[0]["content"])


class TestOfflineRobustness(unittest.TestCase):
    """The CLI never crashes on files the fixtures don't cover."""

    def test_unknown_simple_file_gets_empty_findings(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write("x = 1\n" * 5)
            path = fh.name
        result = analyzer.analyze_file(path)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["lane"], "simple")

    def test_unknown_deep_file_gets_empty_findings(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write("x = 1\n" * 40)
            path = fh.name
        result = analyzer.analyze_file(path)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["lane"], "deep")
        self.assertEqual(result["usage"]["tool_calls"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
