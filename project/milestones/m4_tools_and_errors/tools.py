"""M4 starter — implement the TODO sections. Read BRIEF.md first.

Two halves: the interface audit (Lesson 0006's craft, as code) and the
error taxonomy with an idempotency ledger (Lesson 0007).
"""
from fixtures import TransientError, PermanentError, UncertainStateError


# =====================================================================
# Part 1 — the interface audit (0006)
# =====================================================================

# ------------------------------------------------------------------
# TODO 1: audit_tool(tool_def) -> list[str] of findings
# Four axes, deterministic rules:
# - "description-too-short"  if the description has fewer than 3
#   sentences (count '.', '!', '?').
# - "param-missing-description:<name>" for any schema property
#   without its own "description".
# - "open-world:<name>" for any property whose description contains
#   "one of" while the property itself has no "enum" (a closed world
#   described but not enforced).
# - "name-not-namespaced" if the tool name contains no '_'.
# Return [] for a clean tool.
# ------------------------------------------------------------------
def audit_tool(tool_def):
    raise NotImplementedError("TODO 1: audit_tool")


# ------------------------------------------------------------------
# TODO 2: consolidate(tools) -> one tool
# Given tools sharing a prefix ("github_create_pr", "github_review_pr",
# "github_merge_pr"), produce ONE tool named "<prefix>_pr" — wait:
# the shared stem. Produce "github_pr" with an "action" property whose
# enum is the differing suffixes ("create", "review", "merge"), required;
# merge the descriptions; carry over the union of other properties.
# Fewer, more capable tools reduce selection ambiguity.
# ------------------------------------------------------------------
def consolidate(tools):
    raise NotImplementedError("TODO 2: consolidate")


# =====================================================================
# Part 2 — the error taxonomy (0007)
# =====================================================================

# ------------------------------------------------------------------
# TODO 3: classify_error(exc) -> "transient" | "permanent" | "uncertain"
# Use the exception types from fixtures.py.
# ------------------------------------------------------------------
def classify_error(exc):
    raise NotImplementedError("TODO 3: classify_error")


# ------------------------------------------------------------------
# TODO 4: tool_result_for(exc) -> dict
# An is_error tool_result block whose content is INSTRUCTIVE:
# - transient: state retryability with parameters,
#   e.g. "Rate limit exceeded. Retry after 30 seconds."
# - permanent: name the alternative path verbatim.
# - uncertain: say the outcome is UNKNOWN and demand verification —
#   the words "do not retry" must appear.
# ------------------------------------------------------------------
def tool_result_for(exc, tool_use_id="toolu_err"):
    raise NotImplementedError("TODO 4: tool_result_for")


# ------------------------------------------------------------------
# TODO 5: IdempotencyLedger — make retries safe by construction
# run(key, fn): the FIRST call with a key executes fn and stores the
# result; any later call with the SAME key returns the stored result
# WITHOUT calling fn again. Track call counts so tests can prove it.
# ------------------------------------------------------------------
class IdempotencyLedger:
    def __init__(self):
        self.results = {}
        self.call_counts = {}

    def run(self, key, fn):
        raise NotImplementedError("TODO 5: IdempotencyLedger.run")
