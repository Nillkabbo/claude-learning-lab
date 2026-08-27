#!/usr/bin/env python3
"""Chapter 7's tripwire: log every Bash call; block destructive variants the rules miss.
Exit 0 = allow (logged); exit 2 = block. NOTE (the honesty box): hooks fail open —
the permission rules in settings.json are the guarantee layer; this is the recorder."""
import json, re, sys
from pathlib import Path

event = json.loads(sys.stdin.read() or "{}")
cmd = str(event.get("tool_input", {}).get("command", ""))
with open(Path(__file__).parents[2] / ".audit.log", "a") as f:
    f.write(cmd + "\n")
if re.search(r"rm\s+(-\w*\s+)*-rf?\s+(/|/\*|~|\$HOME|\.)", cmd):
    print(json.dumps({"systemMessage": "blocked by audit hook: destructive rm"}))
    sys.exit(2)
sys.exit(0)
