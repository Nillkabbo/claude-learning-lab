"""M10 starter — the capstone. Read BRIEF.md first.

Lesson 0022's master checklist as ONE pipeline: lanes, drafts, enforced
compliance, voting, escalation, the nightly digest, and the report card
(evals + the bill). Each function is a checklist line.
"""
from pathlib import Path


# ------------------------------------------------------------------
# TODO 1: handle_ticket(ticket, ctx)  (lines 3-8 of the checklist)
# ctx: {"classifier", "draft" (the scripted draft text), "competitors",
#       "verdicts", "policy_topics", "canned_abusive", "vote_threshold": 2}
# Flow:
#   lane = ctx["classifier"](ticket)
#   abusive  -> {"lane": "abusive", "response": canned, "model_called": False}
#   easy/hard -> draft = ctx["draft"]; filtered = compliance filter
#                (SSN \d{3}-\d{2}-\d{4} -> "[PII removed]", competitor
#                names -> "[competitor]"); flagged = 2-of-3 vote;
#                escalated = flagged OR last-user policy topic
#   regulated -> certified lane: privacy_enforced True, same draft flow
# Return the result dict (keep keys: lane, response, privacy_enforced,
# model_called, flagged, escalated, reasons).
# ------------------------------------------------------------------
def handle_ticket(ticket, ctx):
    raise NotImplementedError("TODO 1: handle_ticket")


# ------------------------------------------------------------------
# TODO 2: nightly_digest(plan, worker, artifact_dir, recorder)  (0015/0022)
# Save plan.md and recorder.log("plan-saved") BEFORE workers; dispatch all
# tasks; collect references (area + artifact path); isolate failures into
# a failures list; report names every area (failed ones included).
# Return {"plan_saved": bool, "references": [...], "failures": [...],
#         "report": str}.
# ------------------------------------------------------------------
def nightly_digest(plan, worker, artifact_dir, recorder):
    raise NotImplementedError("TODO 2: nightly_digest")


# ------------------------------------------------------------------
# TODO 3: report_card(cases, usage, prices)  (0016/0017/0022)
# Eval side: outcome-based over cases ({"id","expected","actual"}) with
# normalized exact match -> {"passed": k, "total": n, "failures": [ids]}.
# Cost side: reads x0.1, writes x1.25, uncached x1.0 of input price;
# output full price; batch=True multiplies the total by 0.5.
# Return {"eval": {...}, "monthly_cost": c,
#         "summary": "eval 8/10 | bill $X.XX"}.
# ------------------------------------------------------------------
def report_card(cases, usage, prices, batch=True):
    raise NotImplementedError("TODO 3: report_card")


# ------------------------------------------------------------------
# TODO 4: master_checklist(architecture)  (0022's design review)
# architecture: {item_name: bool} for the 11 checklist lines. Return the
# list of FALSE item names (what's missing); [] when the design review
# passes. Order preserved from the input dict.
# ------------------------------------------------------------------
def master_checklist(architecture):
    raise NotImplementedError("TODO 4: master_checklist")
