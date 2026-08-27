"""M7 starter — implement the TODO sections. Read BRIEF.md first.

Lessons 0013-0015 as runnable machinery: routing with a privacy lane,
gated chains, voting thresholds, effort scaling, and the
orchestrator-workers digest with filesystem artifacts.
"""
from pathlib import Path


# ------------------------------------------------------------------
# TODO 1: route(ticket, classifier)  (0014: routing's three wins)
# Classify, then dispatch per lane:
#   easy       -> {"lane": "easy", "model": "haiku", "privacy_enforced": False}
#   hard       -> sonnet lane
#   regulated  -> certified-model lane with privacy_enforced: True
#                 (routing as policy enforcement)
#   abusive    -> {"lane": "abusive", "response": CANNED_ABUSIVE_RESPONSE,
#                  "model": None}  — no LLM call at all
# ------------------------------------------------------------------
def route(ticket, classifier):
    raise NotImplementedError("TODO 1: route")


# ------------------------------------------------------------------
# TODO 2: chain_with_gates(steps, gates)  (0014: prompt chaining)
# steps: list of callables, each taking the previous output.
# gates: list of callables(output -> bool), gates[i] runs AFTER steps[i].
# Run step, check gate, continue. First failing gate: STOP — return
# (output_so_far, failed_at=i). All pass: (final_output, None).
# Gates are programmatic checks, not model calls.
# ------------------------------------------------------------------
def chain_with_gates(steps, gates):
    raise NotImplementedError("TODO 2: chain_with_gates")


# ------------------------------------------------------------------
# TODO 3: vote(verdicts, threshold)  (0014: parallelization / voting)
# verdicts: list of booleans from N independent screeners.
# Return {"flagged": <count >= threshold>, "votes": count}.
# The threshold IS the precision/recall business decision.
# ------------------------------------------------------------------
def vote(verdicts, threshold):
    raise NotImplementedError("TODO 3: vote")


# ------------------------------------------------------------------
# TODO 4: scale_effort(complexity)  (0015: embedded scaling rules)
# "simple"     -> 1 worker,  max 10 tool calls
# "comparison" -> 2 workers, max 15 calls each
# "complex"    -> 10 workers, no call cap (None)
# Return (worker_count, max_calls_per_worker).
# ------------------------------------------------------------------
def scale_effort(complexity):
    raise NotImplementedError("TODO 4: scale_effort")


# ------------------------------------------------------------------
# TODO 5: orchestrate(query, plan, worker, artifact_dir, recorder)  (0015)
# The orchestrator-workers digest:
#  1. SAVE THE PLAN FIRST — write plan.md into artifact_dir and
#     recorder.log("plan-saved") BEFORE any worker runs (contexts
#     truncate; the plan must survive).
#  2. Dispatch every task in `plan` to worker(area, objective,
#     artifact_dir); collect {"area", "artifact"} REFERENCES (not
#     contents — minimize the game of telephone).
#  3. Failure isolation: a raising worker is caught, logged as
#     {"area", "error"}, and does NOT stop the others.
#  4. Synthesize a report string naming every area (from references).
# Return {"plan_saved": bool, "references": [...], "failures": [...],
#         "report": str}.
# ------------------------------------------------------------------
def orchestrate(query, plan, worker, artifact_dir, recorder):
    raise NotImplementedError("TODO 5: orchestrate")
