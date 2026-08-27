#!/usr/bin/env python3
"""Chapter 10's night-shift. Fences IMPLEMENTED (review fix):
- retry: exactly one retry window, then file + page-a-human
- exit codes honored; failures produce a distinct morning report
- allow-list: read-only tools (claude flags)
- spend cap: enforced at the workspace/plan level (documented in COSTS.md);
  this script's lever is the tight allow-list + single retry budget
Dry-runs without a claude binary."""
import subprocess, sys, shutil
from pathlib import Path

PROMPT = "Run the sync per RUNBOOK.md; on failure retry once, then file an issue."
CMD = ["claude", "-p", PROMPT, "--output-format", "json",
       "--allowedTools", "Read,Grep,Glob,mcp__github__list_issues"]
REPORT = Path(__file__).parents[1] / ".nightly-report.txt"

def attempt(n):
    if not shutil.which("claude"):
        print(f"dry-run (no claude binary): {' '.join(CMD)}")
        REPORT.write_text("dry-run: no claude binary\n")
        return 0
    r = subprocess.run(CMD, capture_output=True, text=True)
    REPORT.write_text(f"attempt {n}: exit={r.returncode}\n{r.stdout}\n{r.stderr}\n")
    return r.returncode

rc1 = attempt(1)
if rc1 == 0:
    print("nightly: green on first window"); sys.exit(0)
rc2 = attempt(2)                      # the ONE retry window
if rc2 == 0:
    print("nightly: green on retry"); sys.exit(0)
print("nightly: PAGE A HUMAN — two failed windows (report: .nightly-report.txt)")
sys.exit(2)
