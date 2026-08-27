"""fixtures/responses.py — scripted model responses and the ground truth they encode.

Fixture mode: the analyzer talks to FixtureModel, which replays these Responses
in order. No API key, no network, fully deterministic — the same file analyzed
twice yields the same findings (that determinism is itself a test).

SEED_ISSUES is the ground truth: the known issues deliberately planted in the
code samples. The eval suite scores the analyzer against it. Treat this file
as the spec — never edit it (or the samples) to make a failing run pass.

The api_handler.py script deliberately includes an invalid-regex tool call:
the grep tool answers with a PermanentError instructive message and the
"model" adapts — the error taxonomy working end to end (Law 6).
"""
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from starter.claude.client import ContentBlock, Response


# --- ground truth: what a correct analysis of each sample must find ----------
SEED_ISSUES = {
    "auth.py": [
        {"id": "auth-sql-injection", "severity": "critical", "line": 12,
         "title": "SQL injection in get_user",
         "evidence": "cursor.execute(\"SELECT ... WHERE id = \" + user_id) — string concatenation into SQL",
         "recommendation": "Parameterize the query: cursor.execute(\"... WHERE id = ?\", (user_id,)). Line 37 has the same flaw in change_password."},
        {"id": "auth-unhandled-none", "severity": "warning", "line": 28,
         "title": "login crashes when get_user returns None",
         "evidence": "stored_hash = user[2] with no None check — a unknown username raises TypeError",
         "recommendation": "Check `if user is None: return {\"ok\": False}` before indexing."},
        {"id": "auth-unused-import", "severity": "info", "line": 3,
         "title": "json is imported but never used",
         "evidence": "import json — no json.* reference in the file",
         "recommendation": "Remove the import."},
    ],
    "api_handler.py": [
        {"id": "api-hardcoded-secret", "severity": "critical", "line": 4,
         "title": "Live API secret hardcoded in source",
         "evidence": "API_SECRET = \"sk-live-9f3e2ab7c4d8e1f6a0b5c3d7e9f2a4b8\"",
         "recommendation": "Move to an environment variable and rotate the leaked key immediately."},
        {"id": "api-bare-except", "severity": "warning", "line": 21,
         "title": "Bare except swallows every error",
         "evidence": "except: — catches KeyboardInterrupt and SystemExit too, hiding real failures",
         "recommendation": "Catch the specific exception, e.g. `except KeyError:`, and log it."},
        {"id": "api-no-input-validation", "severity": "warning", "line": 10,
         "title": "Handler indexes payload keys without validation",
         "evidence": "payload[\"username\"] and json.loads(event[\"body\"]) are unguarded — malformed input raises KeyError/JSONDecodeError",
         "recommendation": "Validate required keys and wrap json.loads before dispatching."},
    ],
    "utils.py": [
        {"id": "utils-mutable-default", "severity": "warning", "line": 9,
         "title": "Mutable default argument shared across calls",
         "evidence": "def add_tag(tag, tags=[]) — the list persists between calls, accumulating tags",
         "recommendation": "Default to None and build inside: `tags = tags if tags is not None else []`."},
        {"id": "utils-no-docstrings", "severity": "info", "line": 1,
         "title": "No docstrings on module or functions",
         "evidence": "slugify, add_tag, truncate have no docstrings",
         "recommendation": "Add one-line docstrings stating intent and return value."},
    ],
}


def _read_call(call_id, path, in_tok, out_tok):
    return Response([ContentBlock("tool_use", id=call_id, name="insight_read_file",
                                  input={"path": str(path)})],
                    "tool_use", {"input_tokens": in_tok, "output_tokens": out_tok})


def _grep_call(call_id, path, pattern, in_tok, out_tok):
    return Response([ContentBlock("tool_use", id=call_id, name="insight_grep",
                                  input={"path": str(path), "pattern": pattern})],
                    "tool_use", {"input_tokens": in_tok, "output_tokens": out_tok})


def _turn(name, in_tok, out_tok):
    body = {"file": name, "findings": SEED_ISSUES[name]}
    text = ("Analysis of %s complete. Findings below, worst first.\n\n```json\n%s\n```\n"
            % (name, json.dumps(body, indent=2)))
    return Response([ContentBlock("text", text=text)], "end_turn",
                    {"input_tokens": in_tok, "output_tokens": out_tok})


# --- one scripted conversation per sample file --------------------------------
def _auth_script(path):
    return [
        _read_call("tu_auth_1", path, 620, 70),
        _turn("auth.py", 3050, 540),
    ]


def _api_handler_script(path):
    return [
        _read_call("tu_api_1", path, 640, 70),
        _grep_call("tu_api_2", path, "(unclosed", 3080, 48),   # invalid regex -> PermanentError
        _grep_call("tu_api_3", path, "except|SECRET", 3120, 55),
        _turn("api_handler.py", 3160, 620),
    ]


def _utils_script(_path):
    return [
        _turn("utils.py", 780, 420),
    ]


_SCRIPTS = {"auth.py": _auth_script, "api_handler.py": _api_handler_script,
            "utils.py": _utils_script}


def _generic_script(path, lane):
    """Unknown file, offline mode: read it (if the lane allows tools), find nothing."""
    note = ("Offline fixture mode: scripted responses exist only for the three sample "
            "files in fixtures/code_samples. No findings reported for this file. "
            "Re-run with --real (ANTHROPIC_API_KEY set) for a live analysis.")
    empty = json.dumps({"file": Path(path).name, "findings": []}, indent=2)
    text = "%s\n\n```json\n%s\n```" % (note, empty)
    end = Response([ContentBlock("text", text=text)], "end_turn",
                   {"input_tokens": 600, "output_tokens": 90})
    if lane == "deep":
        return [_read_call("tu_generic_1", path, 590, 60), end]
    return [end]


def script_for(path, lane):
    """Build a fresh scripted conversation for this exact path and lane."""
    factory = _SCRIPTS.get(Path(path).name)
    if factory is None:
        return _generic_script(path, lane)
    return factory(path)
