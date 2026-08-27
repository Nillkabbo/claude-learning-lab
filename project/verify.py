#!/usr/bin/env python3
"""Apex Project verifier. Run from the project root: python3 verify.py

Runs every milestone's test suite and prints a report whose summary line is
meant to be pasted to the teaching agent as demonstrated-mastery evidence.
"""
import io
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

MILESTONES = [
    ("m1_request_anatomy", "M1 · Request anatomy (lessons 0001-0003)"),
    ("m2_structured_outputs", "M2 · Structured outputs (lesson 0004)"),
    ("m3_tool_loop", "M3 · The tool loop (lesson 0005)"),
    ("m4_tools_and_errors", "M4 · Tools & errors (lessons 0006-0007)"),
    ("m5_context_management", "M5 · Context management (lesson 0008)"),
    ("m6_claude_code_config", "M6 · Claude Code config & Agent SDK (lessons 0009-0012)"),
    ("m7_patterns", "M7 · Composition patterns (lessons 0013-0015)"),
    ("m8_evals_and_cost", "M8 · Evaluation & cost (lessons 0016-0017)"),
    ("m9_workflow_lifecycle", "M9 · Workflow & lifecycle (lessons 0018-0021)"),
    ("m10_capstone", "M10 · Capstone (lesson 0022)"),
]


def run_milestone(slug):
    """Return (results, total) for a milestone directory, or (None, 0) if unbuilt."""
    mdir = PROJECT_ROOT / "milestones" / slug
    if not (mdir / "verify_marker").exists() and not list(mdir.glob("test_*.py")):
        return None, 0
    sys.path.insert(0, str(mdir))
    try:
        suite = unittest.defaultTestLoader.discover(str(mdir), pattern="test_*.py", top_level_dir=str(mdir))
        runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
        return runner.run(suite), suite.countTestCases()
    finally:
        sys.path.pop(0)
        # Milestones share module names (fixtures, extractor, ...) — evict this
        # milestone's modules so the next one imports its own.
        for name, mod in list(sys.modules.items()):
            mod_file = getattr(mod, "__file__", None)
            if mod_file and str(mdir) in str(mod_file):
                del sys.modules[name]


def main():
    print("=" * 56)
    print("  APEX PROJECT REPORT")
    print("=" * 56)
    summary = []
    for slug, label in MILESTONES:
        results, total = run_milestone(slug)
        if results is None or total == 0:
            print(f"\n{label}\n  (not built yet — say \"next milestone\" to scaffold it)")
            continue
        passed = results.testsRun - len(results.failures) - len(results.errors)
        status = "GREEN" if passed == total else "IN PROGRESS"
        print(f"\n{label}  [{status}]")
        for case, _ in results.failures + results.errors:
            name = case.id().split(".")[-1]
            print(f"  ✗ {name}")
        print(f"  {passed}/{total} checks passed")
        summary.append((slug.split("_")[0].upper(), f"{passed}/{total}"))
    print("\n" + "=" * 56)
    if summary:
        paste = " ".join(f"{m}:{s}" for m, s in summary)
        print("PASTE THIS TO YOUR AGENT:")
        print(f"  project: {paste}")
    else:
        print("No milestones built yet. Start with milestones/m1_request_anatomy/BRIEF.md")
    print("=" * 56)


if __name__ == "__main__":
    main()
