#!/usr/bin/env python3
"""analyzer.py — Insight's core engine. Composes every starter module.

  client   -> contract-valid requests + stop-reason dispatch   (Laws 1, 2, 3)
  tools    -> read/grep/glob + the full error taxonomy          (Laws 5, 6)
  context  -> the 400 pre-check, cache-aware clearing, compact  (Law 7)
  patterns -> routing, gated validation chain, voting           (Law 9)
  evals    -> cost arithmetic with real cache/batch multipliers (Law 10)

Offline by default: no model given means FixtureModel replaying scripted
responses from fixtures/responses.py. Pass a RealClient for production —
the engine never knows which one it is talking to.

Zero dependencies: Python 3 stdlib only.
"""
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
for _p in (str(_HERE), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from starter.claude.client import (
    Action, FixtureModel, RealClient, RequestBuilder, assistant_turn_message,
    handle_response,
)
from starter.claude.tools import (
    IdempotencyLedger, PermanentError, Tool, ToolRunner, TransientError,
    UncertainStateError, audit,
)
from starter.claude.context import (
    clear_tool_results, compact, count_tokens, would_overflow,
)
from starter.claude.patterns import chain_with_gates, route, vote
from starter.claude.evals import monthly_cost


# --- Law 3: the system prompt is policy, not vibe ----------------------------
SYSTEM_PROMPT = (
    "You are Insight, a static-analysis assistant embedded in a code-quality CLI.\n"
    "Role: read source files with your tools and report correctness, security, and "
    "maintainability issues.\n"
    "Scope: the single target file you are given; report only what the code shows you.\n"
    "Output: exactly one fenced ```json block of the shape "
    '{"file": "...", "findings": [...]}; every finding needs id, severity '
    "(critical|warning|info), line, title, evidence, recommendation.\n"
    "Do not: report an issue you cannot locate, invent line numbers, propose code "
    "edits, or read anything outside the target path.\n"
    "If the file is clean, return an empty findings list."
)

SEVERITIES = ("critical", "warning", "info")
CONTEXT_WINDOW = 100_000        # tokens, Sonnet-class
COMPACT_TRIGGER = 60_000        # start reclaiming before the cliff
CLEAR_KEEP = 3                  # newest tool results stay intact
MAX_STEPS = 8                   # tool-loop guard
COST_BUDGET_USD = 0.05          # per-analysis budget (REQUIREMENTS.md)
SIMPLE_LANE_MAX_LINES = 30      # routing threshold (Law 9)
PRICES = {"input": 3.0, "output": 15.0}   # $ per million tokens, Sonnet-class

# Law 9: routing buys each rung only when it pays.
LANES = {
    "simple": {"mode": "single-call", "max_tokens": 1024, "tools": False},
    "deep":   {"mode": "tool-loop",   "max_tokens": 2048, "tools": True},
}


class GrammarError(Exception):
    """A validation layer rejected the model's output (Law 4)."""


class LoopLimitError(Exception):
    """The tool loop exceeded MAX_STEPS — complexity was misrouted."""


class TruncationError(Exception):
    """max_tokens stayed exhausted even after lifting the cap twice."""


class RefusalError(Exception):
    """The model refused — a policy path, never retried blindly."""


# --- Law 5: tools with interface discipline + the error taxonomy (Law 6) -----
DENIED_PATH_TOKENS = (".env", "secret", "id_rsa", ".pem", ".key", ".p12")


def _read_fn(ledger):
    def read_file(inp):
        raw = inp.get("path", "")
        path = Path(raw)
        low = str(path).lower()
        if any(token in low for token in DENIED_PATH_TOKENS):
            raise PermanentError(
                f"'{raw}' looks like secret material.",
                "It is deny-listed. Analyze code files only.")
        if not path.exists():
            raise PermanentError(
                f"'{raw}' does not exist.",
                "List candidate files with insight_glob first.")
        if path.is_dir():
            raise PermanentError(
                f"'{raw}' is a directory.",
                "Use insight_glob to list its files instead.")
        if path.suffix == ".writing":
            raise TransientError(
                f"'{raw}' is mid-write (lock convention).", 2)
        # Same path = one filesystem read, even if the model asks twice.
        return ledger.run(str(path), lambda: path.read_text())
    return read_file


def _grep_fn(inp):
    path = Path(inp.get("path", ""))
    pattern = inp.get("pattern", "")
    if inp.get("fixed_string", False):
        rx = re.compile(re.escape(pattern))
    else:
        try:
            rx = re.compile(pattern)
        except re.error as exc:
            raise PermanentError(
                f"invalid regex '{pattern}': {exc}.",
                "Pass fixed_string=true to search for it literally.")
    if not path.is_file():
        raise PermanentError(
            f"'{path}' is not a readable file.",
            "Resolve the right path with insight_read_file or insight_glob.")
    hits = [f"{i}: {line.rstrip()}"
            for i, line in enumerate(path.read_text().splitlines(), 1)
            if rx.search(line)]
    return "\n".join(hits) if hits else f"no matches for /{pattern}/"


def _glob_fn(inp):
    directory = Path(inp.get("directory", "."))
    pattern = inp.get("pattern", "*")
    if not directory.is_dir():
        raise PermanentError(
            f"'{directory}' is not a directory.",
            "Use insight_read_file for single files.")
    matches = sorted(str(p) for p in directory.rglob(pattern) if p.is_file())
    return "\n".join(matches[:50]) if matches else f"no files match '{pattern}'"


def make_tools(ledger=None):
    """The analyzer's toolset. Each tool passes the four-question audit."""
    read = Tool(
        name="insight_read_file",
        description=("Reads one file and returns its full text. Use when you need the "
                     "source of the analysis target. Do not use for directories or for "
                     "searching — that is insight_glob and insight_grep. Secret-looking "
                     "paths (.env, keys) are deny-listed and always fail."),
        input_schema={"type": "object",
                      "properties": {"path": {"type": "string",
                                              "description": "Absolute or cwd-relative path of one file."}},
                      "required": ["path"]},
        fn=_read_fn(ledger or IdempotencyLedger()))
    grep = Tool(
        name="insight_grep",
        description=("Searches one file for a regex, returning numbered matching lines. "
                     "Use to confirm an issue appears elsewhere in the file. Do not use "
                     "on unknown paths — read the file first. An invalid pattern is a "
                     "permanent error unless fixed_string is true."),
        input_schema={"type": "object",
                      "properties": {"path": {"type": "string",
                                              "description": "File to search."},
                                     "pattern": {"type": "string",
                                                 "description": "Python regex, or literal text when fixed_string is true."},
                                     "fixed_string": {"type": "boolean",
                                                      "description": "Treat pattern as literal text instead of regex."}},
                      "required": ["path", "pattern"]},
        fn=_grep_fn)
    glob = Tool(
        name="insight_glob",
        description=("Lists files under a directory matching a glob pattern, newest "
                     "paths sorted, capped at 50. Use to discover files before reading. "
                     "Do not use to read contents — that is insight_read_file. "
                     "Directories only; a file path is a permanent error."),
        input_schema={"type": "object",
                      "properties": {"directory": {"type": "string",
                                                   "description": "Directory to search from."},
                                     "pattern": {"type": "string",
                                                 "description": "Glob such as *.py or **/*.json."}},
                      "required": ["directory", "pattern"]},
        fn=_glob_fn)
    tools = [read, grep, glob]
    for tool in tools:                      # interface discipline, enforced
        problems = audit(tool)
        if problems:
            raise RuntimeError(f"{tool.name} failed tool audit: {problems}")
    return tools


TOOL_SPECS = [{"name": t.name, "description": t.description,
               "input_schema": t.input_schema} for t in make_tools()]


# --- Law 4: validation layers, chained behind gates (Law 9) ------------------
def _extract_json_block(text):
    fence = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    first, last = text.find("{"), text.rfind("}")
    return text[first:last + 1] if 0 <= first < last else None


def _parse_json(block):
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        return None


def _semantic_pass(parsed, line_count):
    """Code checks the model's claims: severity enum, line bounds, dedupe."""
    if not all(isinstance(f, dict) for f in parsed["findings"]):
        return None
    kept, dropped, seen = [], [], set()
    for finding in parsed["findings"]:
        fid = finding.get("id", "")
        problems = []
        if not isinstance(fid, str) or not fid.strip():
            problems.append("missing-id")
        elif fid in seen:
            problems.append("duplicate-id")
        if finding.get("severity") not in SEVERITIES:
            problems.append(f"bad-severity:{finding.get('severity')!r}")
        line = finding.get("line")
        if not isinstance(line, int) or not 1 <= line <= max(line_count, 1):
            problems.append(f"line-out-of-range:{line!r}")
        if not str(finding.get("title", "")).strip():
            problems.append("missing-title")
        if not str(finding.get("recommendation", "")).strip():
            problems.append("missing-recommendation")
        if problems:
            dropped.append({"id": str(fid) or "<unnamed>", "problems": problems})
        else:
            seen.add(fid)
            kept.append(finding)
    return {"findings": kept, "dropped": dropped}


def parse_findings(text, line_count):
    """Three layers behind gates: locate -> grammar -> semantics.

    A failing layer stops the chain and raises — the analyzer refuses to
    invent findings it cannot validate.
    """
    steps = [
        lambda: _extract_json_block(text),
        _parse_json,
        lambda parsed: _semantic_pass(parsed, line_count),
    ]
    gates = [
        lambda block: isinstance(block, str) and bool(block.strip()),
        lambda parsed: isinstance(parsed, dict) and isinstance(parsed.get("findings"), list),
        lambda result: result is not None,
    ]
    result, failed_at = chain_with_gates(steps, gates)
    if failed_at is not None:
        layer = ("locating the JSON block", "JSON grammar", "semantic checks")[failed_at]
        raise GrammarError(f"validation failed at layer {failed_at} ({layer}); "
                           "refusing to report unvalidated findings")
    return result


# --- Law 7: the context budget, managed before every send --------------------
def _summarize(old_messages):
    parts = []
    for message in old_messages:
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(str(b.get("content", b.get("text", ""))) for b in content)
        parts.append(str(content)[:200])
    return f"{len(old_messages)} earlier turns: " + " | ".join(parts)[:2000]


def _starts_with_tool_result(message):
    content = message.get("content", "")
    return (isinstance(content, list) and bool(content)
            and content[0].get("type") == "tool_result")


def _repair_alternation(messages):
    """compact() inserts a user summary; fold it in if the next message is
    also user-without-tool_result, or the builder will (correctly) refuse."""
    if len(messages) >= 2 and messages[0].get("role") == "user" \
            and messages[1].get("role") == "user" \
            and not _starts_with_tool_result(messages[1]):
        second = messages[1].get("content")
        folded = str(messages[0].get("content"))
        if isinstance(second, str):
            folded += "\n\n" + second
        else:
            folded += "\n\n" + json.dumps(second)
        return [{"role": "user", "content": folded}] + messages[2:]
    return messages


def check_context(messages, window=CONTEXT_WINDOW, trigger=COMPACT_TRIGGER):
    """Cheap first (clear old tool results), drastic second (compact)."""
    messages, _cleared, applied = clear_tool_results(
        messages, trigger, keep=CLEAR_KEEP, clear_at_least=2000)
    if applied:
        return _repair_alternation(messages)
    if would_overflow(messages, window):        # the 400 check, before the 400
        compacted = compact(messages, _summarize, keep_recent=4)
        return _repair_alternation(compacted)
    return messages


# --- Laws 1 + 2 + 5: the stateless loop ---------------------------------------
def run_conversation(model, messages, system, max_tokens, tools=None, runner=None):
    """Resend the full history every request (Law 1); dispatch on stop_reason
    (Law 2); echo the assistant turn and place tool_results as the next user
    message (Law 5). Returns (final_text, usage, messages)."""
    builder = RequestBuilder()
    usage = {"requests": 0, "uncached_input_tokens": 0, "cached_read_tokens": 0,
             "output_tokens": 0, "tool_calls": 0}
    lifts = 0
    for _step in range(MAX_STEPS):
        messages = check_context(messages)
        request = builder.build(messages, system, max_tokens, tools=tools)
        response = model.complete(request)
        usage["requests"] += 1
        tokens_in = response.usage.get("input_tokens", 0)
        # First request pays full input; later requests hit the cached prefix.
        if usage["requests"] == 1:
            usage["uncached_input_tokens"] += tokens_in
        else:
            usage["cached_read_tokens"] += tokens_in
        usage["output_tokens"] += response.usage.get("output_tokens", 0)

        action, payload = handle_response(response)
        if action is Action.COMPLETE:
            return payload, usage, messages
        if action is Action.RUN_TOOLS:
            usage["tool_calls"] += len(payload)
            messages.append(assistant_turn_message(response))
            results = [runner.execute(block) for block in payload]
            messages.append({"role": "user", "content": results})
            continue
        if action is Action.TRUNCATED:          # your cap fired — lift it, twice max
            if lifts >= 2:
                raise TruncationError("output still truncated after lifting max_tokens twice")
            lifts += 1
            max_tokens *= 2
            continue
        raise RefusalError(f"the model refused: {payload!r}")   # policy path
    raise LoopLimitError(f"tool loop exceeded {MAX_STEPS} steps")


# --- Law 10: the economics ----------------------------------------------------
def calculate_cost(usage):
    """Cost of one analysis run via the real multipliers (reads 0.1x, no batch)."""
    mtok = {"uncached_input_mtok": usage.get("uncached_input_tokens", 0) / 1e6,
            "cached_read_mtok": usage.get("cached_read_tokens", 0) / 1e6,
            "cached_write_mtok": 0.0,
            "output_mtok": usage.get("output_tokens", 0) / 1e6}
    total = monthly_cost(mtok, PRICES, batch=False, cache=True)
    return {"total_usd": round(total, 6),
            "under_budget": total < COST_BUDGET_USD,
            "budget_usd": COST_BUDGET_USD,
            "usage_mtok": {k: round(v, 6) for k, v in mtok.items()},
            "prices_per_mtok": dict(PRICES)}


# --- Law 6 (verify): evidence must survive the analysis -----------------------
def analyze_file(path, model=None, system=SYSTEM_PROMPT):
    """Analyze one file. Routes complexity (Law 9), runs the loop, validates
    the output (Law 4), verifies the file did not change mid-flight (Law 6),
    and prices the run (Law 10)."""
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise PermanentError(f"'{path}' is not a readable file.",
                             "Pass a .py file or a directory to the CLI.")
    text = resolved.read_text()
    line_count = len(text.splitlines())
    mtime_before = resolved.stat().st_mtime_ns

    lane = route(resolved, LANES, classify)
    if model is None:
        from fixtures.responses import script_for
        model = FixtureModel(script_for(resolved, lane["lane"]))
    runner = ToolRunner(make_tools(IdempotencyLedger()))

    if lane["tools"]:
        messages = [{"role": "user", "content":
                     f"Analyze {resolved.name} for correctness, security, and "
                     f"maintainability issues. The file is at {resolved}. Use your "
                     "tools to read it, then report findings in the specified JSON."}]
        tool_specs = TOOL_SPECS
    else:
        messages = [{"role": "user", "content":
                     f"Analyze {resolved.name} for correctness, security, and "
                     "maintainability issues. The full source:\n\n```\n"
                     + text + "\n```\nReport findings in the specified JSON."}]
        tool_specs = None

    final_text, usage, _messages = run_conversation(
        model, messages, system, lane["max_tokens"], tools=tool_specs, runner=runner)

    if resolved.stat().st_mtime_ns != mtime_before:
        raise UncertainStateError(
            f"{resolved.name} changed while it was being analyzed.",
            "Do not trust these findings — re-run the analysis.")

    parsed = parse_findings(final_text, line_count)
    order = {s: i for i, s in enumerate(SEVERITIES)}
    parsed["findings"].sort(key=lambda f: (order[f["severity"]], f["line"]))
    return {"file": str(resolved), "name": resolved.name,
            "lane": lane["lane"], "mode": lane["mode"],
            "findings": parsed["findings"], "dropped": parsed["dropped"],
            "usage": usage, "cost": calculate_cost(usage)}


def analyze_path(path, model=None):
    """CLI entry: one file, or every .py file under a directory."""
    resolved = Path(path)
    if resolved.is_dir():
        files = sorted(p for p in resolved.rglob("*.py") if p.is_file())
        return [analyze_file(f, model=model) for f in files]
    return [analyze_file(resolved, model=model)]


def classify(path):
    """The routing classifier: small files get one call, big ones the loop."""
    lines = len(Path(path).read_text().splitlines())
    return "simple" if lines <= SIMPLE_LANE_MAX_LINES else "deep"


def stability_vote(runs):
    """vote() over per-file verdicts: found everything, with correct severities."""
    return vote([r.get("exact", False) for r in runs], threshold=len(runs))
