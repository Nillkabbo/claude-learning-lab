"""M10 fixtures — everything the wired-together Apex Assistant needs.

Given code. The capstone composes the shapes you built in M1-M9 into one
pipeline: lanes, drafts, filters, votes, escalation, workers, evals, bill.
"""
from pathlib import Path

CANNED_ABUSIVE = "I can't help with that. Let's keep it to flights and bookings."

COMPETITORS = {"SkyRival Airlines", "TransOceanic", "JetFast"}

DIRTY_DRAFT = ("Here's the update. My SSN is 123-45-6678 on file. SkyRival Airlines "
               "would charge less for this route. AX204 departs 14:20 gate 12.")

SAFETY_VERDICTS = [True, True, False]        # 2-of-3 flags the draft

POLICY_TOPICS = {"compensation", "claim"}


def classify(ticket):
    t = ticket.lower()
    if "idiot" in t:
        return "abusive"
    if "compensation" in t or "claim" in t:
        return "regulated"
    if "why" in t or "compare" in t:
        return "hard"
    return "easy"


class Recorder:
    def __init__(self):
        self.events = []
    def log(self, e):
        self.events.append(e)


def make_worker(recorder, fail_area=None):
    def worker(area, objective, artifact_dir):
        if area == fail_area:
            raise RuntimeError(f"worker failed: {area}")
        recorder.log(f"worker:{area}")
        p = Path(artifact_dir) / f"{area}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {area}\nObjective: {objective}\n3 findings. [source: apex/{area}]\n")
        return {"area": area, "artifact": str(p)}
    return worker


DIGEST_PLAN = [
    {"area": "ops", "objective": "Summarize the day's delays."},
    {"area": "maintenance", "objective": "Flag overnight maintenance risks."},
    {"area": "crew", "objective": "Crew coverage gaps for tomorrow."},
]

EVAL_CASES = [
    {"id": i, "expected": "delayed" if i % 2 == 0 else "on time",
     "actual": ("on time" if i in (4, 9) else ("delayed" if i % 2 == 0 else "on time"))}
    for i in range(10)
]   # exactly two failures: ids 4 and 9

USAGE = {"uncached_input_mtok": 0.25, "cached_read_mtok": 0.50,
         "cached_write_mtok": 0.25, "output_mtok": 1.00}
PRICES = {"input": 3.00, "output": 15.00}

ARCHITECTURE = {   # the 11-line master checklist, 9 items satisfied
    "criteria": True, "posture": True, "patterns": True, "interfaces": True,
    "errors": True, "context": True, "trust": True, "workflow_concerns": True,
    "evaluation": True, "economics": False, "lifecycle": False,
}
