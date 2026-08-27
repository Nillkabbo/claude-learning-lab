#!/usr/bin/env python3
"""example.py — the starter kit working end-to-end on fixtures.

Run:  python3 example.py    (no API key, no dependencies)
"""
import tempfile
from pathlib import Path

from claude_starter.client import (
    FixtureModel, RequestBuilder, handle_response, Action,
    assistant_turn_message, tool_results_message, ContentBlock, Response,
)
from claude_starter.tools import Tool, ToolRunner, IdempotencyLedger
from claude_starter import context, patterns, evals


# --- tools with interface discipline -------------------------------------------
get_status = Tool(
    name="get_flight_status",
    description=("Gets the current status of one Apex flight. Use when the user asks "
                 "about departure time, delay, or gate for a specific flight number. "
                 "Do not use for bookings — that is a separate tool. "
                 "Returns one line of status; no weather, no rebooking."),
    input_schema={"type": "object",
                  "properties": {"flight_number": {"type": "string",
                                                   "description": "Apex code, e.g. AX204"}},
                  "required": ["flight_number"]},
    fn=lambda inp: "AX204: delayed 45m, gate 12, reason weather." if inp["flight_number"] == "AX204"
                   else f"No flight {inp['flight_number']}.")
search = Tool(
    name="search_airports",
    description=("Resolves city names to IATA codes. Use before any tool needing an "
                 "airport code when the user gave a city. Do not use for flight status. "
                 "Returns 'CODE — name' or a not-found line."),
    input_schema={"type": "object",
                  "properties": {"query": {"type": "string", "description": "City name."}},
                  "required": ["query"]},
    fn=lambda inp: "AUS — Austin-Bergstrom" if "austin" in inp["query"].lower() else "Not found.")
runner = ToolRunner([get_status, search])


def demo():
    # Phase 3: the core loop (law 1, 2, 5)
    model = FixtureModel([
        Response([ContentBlock("tool_use", id="t1", name="get_flight_status",
                               input={"flight_number": "AX204"})], "tool_use"),
        Response([ContentBlock("text", text="AX204 is delayed 45 minutes due to weather.")], "end_turn"),
    ])
    builder = RequestBuilder()
    messages = [{"role": "user", "content": "How is AX204?"}]
    print("== core loop ==")
    while True:
        request = builder.build(messages, system="You are Apex's assistant. Be concise.")
        response = model.complete(request)
        action, payload = handle_response(response)
        messages.append(assistant_turn_message(response))
        if action is Action.COMPLETE:
            print("final:", payload)
            break
        messages.append(tool_results_message(payload))
        print("tool executed:", payload[0].name)

    # Phase 7: patterns (law 9)
    lanes = {"easy": {"model": "haiku", "privacy_enforced": False},
             "regulated": {"model": "certified", "privacy_enforced": True}}
    print("\n== routing ==")
    print(patterns.route("compensation claim", lanes, lambda t: "regulated" if "claim" in t else "easy"))
    print(patterns.vote([True, True, False], threshold=2))

    # Phase 5 + 8: context budget and evidence (law 7, 10)
    big = [{"role": "user", "content": "x" * 4000}] * 6
    print("\n== context ==")
    print("tokens:", context.count_tokens(big), "| overflow@1000:", context.would_overflow(big, 1000))
    compacted = context.compact(big, summarize=lambda ms: "six near-identical questions")
    print("after compact:", len(compacted), "messages")
    suite = [{"id": 0, "expected": "delayed", "actual": "Delayed "},
             {"id": 1, "expected": "on time", "actual": "delayed"}]
    print("\n== evals & cost ==")
    print(evals.run_suite(suite))
    print("monthly:", round(evals.monthly_cost(
        {"uncached_input_mtok": 0.25, "cached_read_mtok": 0.5,
         "cached_write_mtok": 0.25, "output_mtok": 1.0},
        {"input": 3.0, "output": 15.0}, batch=True, cache=True), 2))

    # Orchestrator-workers (law 9)
    def file_worker(area, objective, directory):
        path = Path(directory) / f"{area}.md"
        path.write_text(f"{area}: {objective}")
        return {"area": area, "artifact": str(path)}
    with tempfile.TemporaryDirectory() as td:
        result = patterns.orchestrate("digest", [
            {"area": "ops", "objective": "delays"},
            {"area": "crew", "objective": "coverage"}], file_worker, td)
        print("\n== orchestrator ==")
        print(result["report"])

    ledger = IdempotencyLedger()
    calls = []
    ledger.run("key-1", lambda: calls.append(1) or "CHARGED")
    ledger.run("key-1", lambda: calls.append(1) or "CHARGED")
    print("\nidempotency: fn ran", len(calls), "time(s) across a retry")


if __name__ == "__main__":
    demo()
