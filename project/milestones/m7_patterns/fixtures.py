"""M7 fixtures — lanes, classifiers, workers, and plan/memory recorders.

Given code. The classifier stands in for a structured-output routing call;
the workers stand in for subagents with their own contexts writing
filesystem artifacts (the anti-telephone pattern).
"""
import json
from pathlib import Path


CANNED_ABUSIVE_RESPONSE = "I can't help with that. Let's keep it to flights and bookings."

MODEL_TIERS = {"easy": "haiku", "hard": "sonnet", "regulated": "certified-model"}


def classify_ticket(ticket):
    """Fixture classifier: a structured-output call, decided."""
    t = ticket.lower()
    if "refund now or" in t or "idiot" in t:
        return "abusive"
    if "compensation" in t or "claim" in t:
        return "regulated"
    if "why" in t or "compare" in t or "explain" in t:
        return "hard"
    return "easy"


# --- gated-chain material ---------------------------------------------------------

def draft_step(text):
    return f"DRAFT: {text}"

def gate_has_citations(output):
    return "DRAFT" in output          # fixture gate: shape check

def gate_no_pii(output):
    return "SSN" not in output        # fixture gate: policy check

FAILING_GATE = lambda output: False    # a gate that always fails


# --- voting material --------------------------------------------------------------

SCREEN_A = True     # three screeners over the same draft
SCREEN_B = True
SCREEN_C = False


# --- orchestrator material ---------------------------------------------------------

class Recorder:
    """Records the order of operations — tests prove plan-before-workers."""

    def __init__(self):
        self.events = []

    def log(self, event):
        self.events.append(event)

    def assert_order(self, first, second):
        return self.events.index(first) < self.events.index(second)


def make_worker(recorder, fail_area=None):
    """A worker fn(area, objective) that writes an artifact and returns a reference."""
    def worker(area, objective, artifact_dir):
        if area == fail_area:
            raise RuntimeError(f"worker failure in {area}")
        recorder.log(f"worker:{area}")
        path = Path(artifact_dir) / f"{area}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {area} findings\n\nObjective: {objective}\n\nFound 3 items. [source: apex-ops/{area}]\n")
        return {"area": area, "artifact": str(path)}
    return worker


DEEP_DIVE_PLAN = [
    {"area": "market", "objective": "Assess market position for the acquisition target."},
    {"area": "financials", "objective": "Summarize 3 years of financials with sources."},
    {"area": "legal", "objective": "Assess litigation and sanctions exposure."},
]
