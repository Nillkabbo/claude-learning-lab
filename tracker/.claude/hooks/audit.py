#!/usr/bin/env python3
"""Chapter 7's tripwire: log every Bash call; block destructive variants the rules miss.
Exit 0 = allow (logged); exit 2 = block. NOTE (the honesty box): hooks fail open —
the permission rules in settings.json are the guarantee layer; this is the recorder.
This script must NEVER crash: any error means silently allow (exit 0)."""
import json, re, sys
from pathlib import Path

try:
    event = json.loads(sys.stdin.read() or "{}")
    cmd = str(event.get("tool_input", {}).get("command", ""))

    # Log (best-effort: unwritable path means no log, not a crash)
    try:
        with open(Path(__file__).parents[2] / ".audit.log", "a") as f:
            f.write(cmd + "\n")
    except (OSError, PermissionError):
        pass

    # Block destructive patterns (best-effort: regex failure means allow)
    if re.search(r"rm\s+(-\w*\s+)*-rf?\s+(/|/\*|~|\$HOME|\.)", cmd):
        print(json.dumps({"systemMessage": "blocked by audit hook: destructive rm"}))
        sys.exit(2)
except Exception:
    pass  # fail-open: any error means allow

sys.exit(0)
