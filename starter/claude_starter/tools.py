"""tools.py — the interface discipline and the error taxonomy. Law 5, 6."""
from dataclasses import dataclass, field


class TransientError(Exception):
    def __init__(self, msg, retry_after):
        super().__init__(msg)
        self.retry_after = retry_after

class PermanentError(Exception):
    def __init__(self, msg, alternative):
        super().__init__(msg)
        self.alternative = alternative

class UncertainStateError(Exception):
    def __init__(self, msg, verify_hint):
        super().__init__(msg)
        self.verify_hint = verify_hint


@dataclass
class Tool:
    name: str
    description: str          # the four questions: what / when / when-not / limits
    input_schema: dict
    fn: object = None         # callable(input_dict) -> str
    strict: bool = True


def audit(tool):
    """The four-question audit — returns findings; [] means clean."""
    findings = []
    desc = tool.description or ""
    if sum(desc.count(c) for c in ".!?") < 3:
        findings.append("description-too-short (aim 3-4+ sentences)")
    for key, prop in tool.input_schema.get("properties", {}).items():
        if "description" not in prop:
            findings.append(f"param-missing-description:{key}")
        if "one of" in prop.get("description", "").lower() and "enum" not in prop:
            findings.append(f"open-world:{key} (described but not enforced)")
    if "_" not in tool.name:
        findings.append("name-not-namespaced")
    return findings


class ToolRunner:
    """Executes tool_use blocks and builds contract-correct results."""

    def __init__(self, tools):
        self.tools = {t.name: t for t in tools}

    def execute(self, block):
        """-> a tool_result block dict. Unknown tools get instructive errors."""
        tool = self.tools.get(block.name)
        if tool is None:
            available = ", ".join(sorted(self.tools))
            return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                    "content": f"Unknown tool '{block.name}'. Available: {available}"}
        try:
            return {"type": "tool_result", "tool_use_id": block.id,
                    "content": str(tool.fn(block.input))}
        except (TransientError, PermanentError, UncertainStateError) as exc:
            return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                    "content": error_content(exc)}


def error_content(exc):
    """Instructive error text — the model reads this and decides (Law 6)."""
    if isinstance(exc, TransientError):
        return f"{exc}. Retry after {exc.retry_after} seconds."
    if isinstance(exc, PermanentError):
        return f"{exc}. Do not retry. {exc.alternative}"
    return (f"{exc}. Outcome UNKNOWN — do not retry. {exc.verify_hint}")


class IdempotencyLedger:
    """Same key, one execution — makes retries safe by construction."""

    def __init__(self):
        self._results = {}
        self.call_counts = {}

    def run(self, key, fn):
        if key in self._results:
            return self._results[key]
        self.call_counts[key] = self.call_counts.get(key, 0) + 1
        self._results[key] = fn()
        return self._results[key]
