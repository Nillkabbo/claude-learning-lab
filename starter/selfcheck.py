#!/usr/bin/env python3
"""selfcheck.py — proves the starter kit's fundamentals hold. Run: python3 selfcheck.py"""
import subprocess
import sys


def main():
    result = subprocess.run([sys.executable, "example.py"], capture_output=True, text=True)
    out = result.stdout
    checks = [
        ("core loop completes", "AX204 is delayed 45 minutes due to weather." in out),
        ("tool executed", "tool executed: get_flight_status" in out),
        ("routing enforces privacy", "certified" in out),
        ("vote flags 2-of-3", "'flagged': True" in out),
        ("context counted", "tokens:" in out and "overflow@1000: True" in out),
        ("compaction shrank history", "after compact: 5 messages" in out),
        ("eval outcomes reported", "'failures': [1]" in out),
        ("cost arithmetic present", "monthly:" in out),
        ("orchestrator report", "COMPLETE" in out),
        ("idempotency held", "fn ran 1 time" in out),
    ]
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("  OK  " if ok else "  FAIL") + " " + name)
    if failed or result.returncode != 0:
        print("\nSTARTER SELF-CHECK: FAILED")
        sys.exit(1)
    print("\nSTARTER SELF-CHECK: OK — all fundamentals hold")


if __name__ == "__main__":
    main()
