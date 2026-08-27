#!/usr/bin/env python3
"""real_example.py — your FIRST REAL API call. Budget: about $0.01.

The whole course runs on fixtures; this is the ten minutes where theory becomes
touched reality. Stdlib only (raw HTTPS — no SDK needed).

Run:  python3 real_example.py
Requires ANTHROPIC_API_KEY in your environment. No key? It prints exactly how
to get one, and nothing else happens.
"""
import json
import os
import sys
import urllib.request

URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-5"        # a current mid-tier model; tiny bill
MAX_TOKENS = 64                     # the whole budget


def main():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("No ANTHROPIC_API_KEY found.\n\n"
              "1. Create a key at console.anthropic.com (Settings → API keys)\n"
              "2. export ANTHROPIC_API_KEY='sk-ant-...'\n"
              "3. Re-run me. Expect one request, ~$0.01.\n")
        sys.exit(0)

    request_body = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": "You answer in exactly one short sentence.",
        "messages": [{"role": "user",
                      "content": "Name the single most important property of the Messages API."}],
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(request_body).encode(),
        headers={"x-api-key": key,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    print("stop_reason:", data["stop_reason"])
    print("text:", data["content"][0]["text"])
    print("usage:", data["usage"])
    print("\nYou just saw it live: the reply is a list of content blocks, the stop_reason")
    print("told you why generation ended, and usage is your (tiny) bill. That's lesson 0001.")


if __name__ == "__main__":
    main()
