"""M6 fixtures — configs to validate, a scripted model, and tools.

Given code. Part A material: settings/subagent/hook configs, good and bad,
plus a frontmatter parser. Part B material: a scripted model and the Apex
tool registry for your query()-shaped wrapper.
"""
import re
from dataclasses import dataclass, field


# --- Part A: configs (0009-0011) ------------------------------------------------

SETTINGS_GOOD = {
    "permissions": {
        "allow": ["Bash(python3 verify.py)", "Bash(python3 -m unittest *)"],
        "ask": ["Bash(git push *)"],
        "deny": ["Read(./.env)", "Read(./.env.*)", "WebFetch"],
    }
}

SETTINGS_BAD = {
    "permissions": {
        "allow": ["Bash(python3 verify.py)"],
        "deny": ["Bash(aws *)"],
        "allow_again": ["Read(./.env)"],     # unknown list; and a trap
    }
}

SUBAGENT_GOOD = """---
name: release-notes
description: Drafts release notes from commits and merged PRs. Use proactively after merges to main.
tools: [Read, Grep, Glob]
---
You are a senior release-notes writer for Apex Airlines tooling. Group changes by
area, cite PR numbers, and never invent entries.
"""

SUBAGENT_BAD = """---
name: Release Notes!
tools: [Read]
---
Body without a description.
"""

HOOK_CONFIG_GOOD = {
    "PreToolUse": [
        {"matcher": "Bash",
         "hooks": [{"type": "command", "command": "./hooks/block-rm.sh"}]},
    ]
}

HOOK_CONFIG_BAD = {
    "BeforeEverything": [{"matcher": "*", "hooks": [{"type": "cmd", "command": ""}]}],
}

KNOWN_HOOK_EVENTS = {"PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop", "PreCompact",
                     "SessionStart", "SessionEnd", "Notification"}


def parse_frontmatter(md_text):
    """Split '---\\nkey: value\\n---\\nbody' into (dict, body). Given helper."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", md_text, re.S)
    if not m:
        return {}, md_text
    meta, body = {}, m.group(2)
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body


# --- Part B: scripted model + tools (0012) --------------------------------------

@dataclass
class ContentBlock:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)
    tool_use_id: str = ""


@dataclass
class Response:
    content: list
    stop_reason: str
    usage: dict = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})


def tool_use(name, input, id="toolu_1"):
    return Response([ContentBlock("tool_use", id=id, name=name, input=input)], "tool_use")


def text(text_):
    return Response([ContentBlock("text", text=text_)], "end_turn")


def _flight_status(input):
    return "AX204: delayed 45 minutes, reason weather."

def _search_airports(input):
    return "AUS - Austin-Bergstrom Intl"

TOOL_IMPLEMENTATIONS = {
    "get_flight_status": _flight_status,
    "search_airports": _search_airports,
}


class ScriptedModel:
    def __init__(self, responses):
        self._responses = list(responses)
        self.requests_seen = []

    def complete(self, request):
        self.requests_seen.append(request)
        if not self._responses:
            return text("…")
        return self._responses.pop(0)
