# Tracker

A tiny issue-tracker CLI. Python 3, stdlib only. (The Story's worked example.)

## Commands
- Run: `python3 tracker.py add|list|close|tag|search ...` (allow-list matches python3)
- Test: `python3 -m unittest discover -s tests`
- Data lives in tasks.json — atomic writes; corrupt input backs up, never destroys

## Conventions
- One behavior per commit; messages like "add: ...", "fix: ..."
- Write JSON atomically (temp file, then replace)
- Test before asking for review; `/release` aborts on red

## MCP trust review (Chapter 6's rule — kept here per the sync skill)
- Tokens: the GitHub MCP server holds its OWN token; never passthrough of ours
- Scopes: read-only on issues; write is a separate, explicit elevation
- Surface: issue reads only; noted 2026-08-27

## Do not
- Add dependencies without asking
- Commit tasks.json or tasks.corrupt*.json
- Push directly to main. Enforcement note (honest): permission patterns are
  string-matching — the deny set covers bare/force/HEAD:main forms, but patterns
  are best-effort; the release skill pushes the release branch, never main.
