#!/usr/bin/env python3
"""insight.py — the CLI face of the Insight analyzer.

  python3 insight.py analyze <file|dir> [--real] [--json]
  python3 insight.py report
  python3 insight.py eval
  python3 insight.py cost

Offline by default (FixtureModel). --real switches to the live Messages API
via the stdlib — needs ANTHROPIC_API_KEY, costs about $0.02 per file.
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from types import SimpleNamespace

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import analyzer
from fixtures.responses import SEED_ISSUES

LAST_RUN = _HERE / ".insight" / "last-run.json"
FIXTURES = _HERE / "fixtures" / "code_samples"
SEVERITY_MARK = {"critical": "CRITICAL", "warning": "WARNING ", "info": "INFO    "}


# --- optional live mode (Law 1: same shape, different transport) --------------
def make_real_model(model="claude-sonnet-4-5"):
    from starter.claude.client import RealClient
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("No ANTHROPIC_API_KEY set. Create one at console.anthropic.com, "
                 "export it, and re-run. Offline mode needs no key (just drop --real).")

    def sdk(**request):
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(request).encode(),
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        return SimpleNamespace(content=data["content"],
                               stop_reason=data["stop_reason"],
                               usage=data["usage"])

    return RealClient(sdk, model=model)


# --- output -------------------------------------------------------------------
def print_result(result):
    usage, cost = result["usage"], result["cost"]
    print(f"\n{result['name']} · lane: {result['lane']} ({result['mode']}) · "
          f"{usage['tool_calls']} tool calls · {usage['requests']} requests · "
          f"${cost['total_usd']:.4f}")
    if not result["findings"]:
        print("  no findings")
    for finding in result["findings"]:
        print(f"  {SEVERITY_MARK[finding['severity']]}  L{finding['line']:<4} "
              f"{finding['id']} — {finding['title']}")
        print(f"            → {finding['recommendation']}")
    for drop in result["dropped"]:
        print(f"  [dropped by validation] {drop['id']}: {', '.join(drop['problems'])}")
    if not cost["under_budget"]:
        print(f"  ! cost ${cost['total_usd']:.4f} exceeds the ${cost['budget_usd']} budget")


def cmd_analyze(args):
    model = make_real_model() if args.real else None
    results = []
    for target in args.paths:
        try:
            results.extend(analyzer.analyze_path(target, model=model))
        except analyzer.GrammarError as exc:
            sys.exit(f"error: {exc}")
        except Exception as exc:                      # taxonomy errors reach here
            sys.exit(f"error analyzing {target}: {exc}")
    for result in results:
        print_result(result)
    totals = _totals(results)
    print(f"\ntotal: {totals['files']} files, {totals['findings']} findings "
          f"({totals['critical']} critical / {totals['warning']} warning / "
          f"{totals['info']} info) · ${totals['cost']:.4f}")
    LAST_RUN.parent.mkdir(exist_ok=True)
    LAST_RUN.write_text(json.dumps(results, indent=2))
    print(f"saved: {LAST_RUN.relative_to(_HERE.parent)}  (see: report, cost)")
    if args.json:
        print(json.dumps(results, indent=2))


def _totals(results):
    counts = {s: 0 for s in analyzer.SEVERITIES}
    for r in results:
        for f in r["findings"]:
            counts[f["severity"]] += 1
    return {"files": len(results), "findings": sum(counts.values()), **counts,
            "cost": sum(r["cost"]["total_usd"] for r in results)}


def _load_last_run():
    if not LAST_RUN.exists():
        sys.exit("No run on record yet — start with: python3 insight.py analyze "
                 f"{FIXTURES.relative_to(_HERE.parent)}")
    return json.loads(LAST_RUN.read_text())


def cmd_report(_args):
    results = _load_last_run()
    totals = _totals(results)
    lanes = {"deep": sum(1 for r in results if r["lane"] == "deep"),
             "simple": sum(1 for r in results if r["lane"] == "simple")}
    usage = {k: sum(r["usage"][k] for r in results) for k in
             ("requests", "uncached_input_tokens", "cached_read_tokens",
              "output_tokens", "tool_calls")}
    dropped = sum(len(r["dropped"]) for r in results)
    print("Insight — last run")
    print(f"  files: {totals['files']} · findings: {totals['findings']} "
          f"({totals['critical']}C / {totals['warning']}W / {totals['info']}I)")
    print(f"  lanes: {lanes['deep']} deep (tool-loop), {lanes['simple']} simple (single-call)")
    print(f"  tool calls: {usage['tool_calls']} · requests: {usage['requests']} · "
          f"tokens in: {usage['uncached_input_tokens'] + usage['cached_read_tokens']:,} "
          f"({usage['uncached_input_tokens']:,} uncached) · out: {usage['output_tokens']:,}")
    print(f"  cost: ${totals['cost']:.4f} (budget ${analyzer.COST_BUDGET_USD}/analysis)")
    print(f"  dropped by validation: {dropped}")
    for r in results:
        c = {s: sum(1 for f in r["findings"] if f["severity"] == s)
             for s in analyzer.SEVERITIES}
        print(f"    {r['name']:<18} {len(r['findings'])} findings "
              f"({c['critical']}C/{c['warning']}W/{c['info']}I) · {r['lane']:<6} "
              f"${r['cost']['total_usd']:.4f}")


def cmd_cost(_args):
    results = _load_last_run()
    usage = {k: sum(r["usage"][k] for r in results) for k in
             ("uncached_input_tokens", "cached_read_tokens", "output_tokens")}
    total = sum(r["cost"]["total_usd"] for r in results)
    for r in results:
        u = r["usage"]
        print(f"  {r['name']:<18} ${r['cost']['total_usd']:.4f}   "
              f"in {u['uncached_input_tokens']:,} uncached + {u['cached_read_tokens']:,} "
              f"cached · out {u['output_tokens']:,}")
    print(f"\n  total: ${total:.4f} across {len(results)} files "
          f"(avg ${total / len(results):.4f}/file, budget ${analyzer.COST_BUDGET_USD})")
    print("  arithmetic: input $3/MTok, cached reads 0.1x, output $15/MTok, "
          "no batch discount (interactive CLI). Multipliers from evals.monthly_cost.")


# --- Law 10: the eval suite, scored against the seed --------------------------
def _run_exact(result, seed):
    found = {(f["id"], f["severity"]) for f in result["findings"]}
    expected = {(f["id"], f["severity"]) for f in seed}
    return found == expected


def cmd_eval(_args):
    from starter.claude.evals import run_suite
    from fixtures.responses import SEED_ISSUES as seed_all
    cases, lines = [], []
    results, reruns = {}, {}
    for name in sorted(seed_all):
        results[name] = analyzer.analyze_file(FIXTURES / name)
        reruns[name] = analyzer.analyze_file(FIXTURES / name)

    seed_flat = {f["id"]: f for seed in SEED_ISSUES.values() for f in seed}
    found_sev = {f["id"]: f["severity"]
                 for r in results.values() for f in r["findings"]}

    for fid, seed_f in seed_flat.items():
        actual = (f"{fid}:found:{found_sev[fid]}" if fid in found_sev
                  else f"{fid}:missing")
        cases.append({"id": fid, "actual": actual,
                      "expected": f"{fid}:found:{seed_f['severity']}"})
        lines.append(("ok " if actual == cases[-1]["expected"] else "FAIL") +
                     " " + actual)

    recall = sum(1 for fid in seed_flat if fid in found_sev) / len(seed_flat)
    cases.append({"id": "recall>=90%", "actual": "pass" if recall >= 0.9 else "fail",
                  "expected": "pass"})
    lines.append(("ok " if recall >= 0.9 else "FAIL") +
                 f" recall {recall:.0%} of seeded issues found (target >=90%)")

    false_criticals = sorted(
        f["id"] for r in results.values() for f in r["findings"]
        if f["severity"] == "critical" and seed_flat.get(f["id"], {}).get("severity") != "critical")
    precision_ok = not false_criticals
    cases.append({"id": "critical-precision>=95%",
                  "actual": "pass" if precision_ok else "fail:" + ",".join(false_criticals),
                  "expected": "pass"})
    lines.append(("ok " if precision_ok else "FAIL") +
                 " no false criticals (critical precision 100%)")

    over = [r["name"] for r in results.values() if not r["cost"]["under_budget"]]
    cases.append({"id": "cost<$0.05/analysis", "actual": "pass" if not over else "fail",
                  "expected": "pass"})
    lines.append(("ok " if not over else "FAIL") + " cost under budget for every file")

    for name in sorted(seed_all):                      # determinism via vote()
        verdicts = [
            _run_exact(results[name], seed_all[name]),
            _run_exact(reruns[name], seed_all[name]),
            all(f["line"] == seed_flat[f["id"]]["line"]
                for f in results[name]["findings"] if f["id"] in seed_flat),
        ]
        ballot = analyzer.vote(verdicts, threshold=3)
        stable = "stable" if ballot["flagged"] else "unstable"
        cases.append({"id": f"stability:{name}", "actual": stable, "expected": "stable"})
        lines.append(("ok " if stable == "stable" else "FAIL") +
                     f" {name}: identical across reruns (vote {sum(verdicts)}/{ballot['votes']})")

    print("\n".join(lines))
    summary = run_suite(cases)
    print(f"\nsuite: {summary}")
    if summary["failures"]:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="insight", description="Insight — the starter-kit code analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser("analyze", help="analyze a file or directory")
    p_analyze.add_argument("paths", nargs="+", help="file or directory to analyze")
    p_analyze.add_argument("--real", action="store_true",
                           help="use the live API (needs ANTHROPIC_API_KEY)")
    p_analyze.add_argument("--json", action="store_true", help="also print raw JSON")
    p_analyze.set_defaults(fn=cmd_analyze)

    p_report = sub.add_parser("report", help="summary of the last run")
    p_report.set_defaults(fn=cmd_report)

    p_eval = sub.add_parser("eval", help="run the eval suite against the fixtures")
    p_eval.set_defaults(fn=cmd_eval)

    p_cost = sub.add_parser("cost", help="cost breakdown of the last run")
    p_cost.set_defaults(fn=cmd_cost)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
