#!/usr/bin/env python3
"""The Apex Assistant CLI — works once capstone.py's TODOs are implemented.

    python3 cli.py support "gate for my flight please"
    python3 cli.py digest
    python3 cli.py report
"""
import argparse
import tempfile
from pathlib import Path

from capstone import handle_ticket, nightly_digest, report_card
from fixtures import (
    COMPETITORS, DIRTY_DRAFT, SAFETY_VERDICTS, POLICY_TOPICS, CANNED_ABUSIVE,
    classify, Recorder, make_worker, DIGEST_PLAN, EVAL_CASES, USAGE, PRICES,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apex Assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    p_support = sub.add_parser("support", help="handle one support ticket")
    p_support.add_argument("ticket")

    sub.add_parser("digest", help="run the nightly digest")

    sub.add_parser("report", help="eval + bill report card")

    args = parser.parse_args(argv)

    if args.command == "support":
        ctx = {
            "classifier": classify, "draft": DIRTY_DRAFT, "competitors": COMPETITORS,
            "verdicts": SAFETY_VERDICTS, "policy_topics": POLICY_TOPICS,
            "canned_abusive": CANNED_ABUSIVE, "vote_threshold": 2,
        }
        result = handle_ticket(args.ticket, ctx)
        for k, v in result.items():
            print(f"{k:>18}: {v}")
        return result

    if args.command == "digest":
        with tempfile.TemporaryDirectory() as td:
            recorder = Recorder()
            result = nightly_digest(DIGEST_PLAN, make_worker(recorder), Path(td), recorder)
        print(result["report"])
        print(f"failures: {[f['area'] for f in result['failures']]}")
        return result

    if args.command == "report":
        card = report_card(EVAL_CASES, USAGE, PRICES, batch=True)
        print(card["summary"])
        print(f"failures: {card['eval']['failures']}")
        return card


if __name__ == "__main__":
    main()
