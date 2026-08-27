#!/usr/bin/env python3
"""Tracker's completion check: suite green + artifacts present + demo run."""
import os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
ARTIFACTS = [
    "tracker.py", "CLAUDE.md", "CHANGELOG.md", "README.md",
    ".claude/settings.json", ".claude/hooks/audit.py",
    ".claude/skills/release/SKILL.md", ".claude/skills/sync/SKILL.md",
    ".claude/agents/detective.md", ".github/workflows/ci.yml",
    "scripts/nightly.py", "RUNBOOK.md", "COSTS.md",
    "meridian-toolkit/.claude-plugin/plugin.json", "meridian-toolkit/marketplace.json",
]

r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                   capture_output=True, text=True, cwd=HERE)
ran = re.search(r"Ran (\d+) tests", r.stderr)
ok = "OK" in r.stderr and ran and int(ran.group(1)) >= 10   # suite grows, gate adapts
missing = [a for a in ARTIFACTS if not (HERE / a).exists()]

with tempfile.TemporaryDirectory() as td:
    env = {**os.environ, "TRACKER_DATA": str(Path(td) / "t.json")}
    def run(*args):
        return subprocess.run([sys.executable, str(HERE / "tracker.py"), *args],
                              capture_output=True, text=True, env=env).stdout
    run("add", "ship v1.0", "#story")
    run("add", "second task")
    run("close", "2")
    demo = run("search", "story")

verdict = ok and not missing and "ship v1.0" in demo
print(f"suite: GREEN ({ran.group(1)} tests)" if ok else "suite: RED")
print("artifacts:", "ALL PRESENT" if not missing else f"MISSING {missing}")
print("demo search:", repr(demo.strip()))
print("TRACKER:", "COMPLETE — v1.0.1" if verdict else "INCOMPLETE")
sys.exit(0 if verdict else 1)
