# Changelog

## v1.0.1 — the expert review fixes (2026-08-27)
- fix: push-to-main denials closed (bare/force/HEAD:main forms); python3 allowed
- fix: graceful close/tag arg errors; search handles hashed multi-word needles
- fix: corrupt backups never overwrite (corrupt-N.json); audit regex broadened
- fix: nightly fences implemented (one retry window, exit codes, page-a-human, report)
- add: MCP trust review in CLAUDE.md; COSTS with numbers + settings chain
- add: CI review job (secret-gated); toolkit populated + marketplace.json
- test: +3 tests (backup isolation, hashed needles, graceful exits); dead mock removed

## v1.0.0 — the story complete (Ch 12)
- Toolkit packaged: release + sync skills, detective agent, guardrails (plugin skeleton in meridian-toolkit/)

## v0.3.0 — two features, one Friday (Ch 8)
- add: tags via #tokens; search across text and tags

## v0.2.0 — the Friday chore (Ch 4)
- add: close command; /release skill (aborts on red tests)

## v0.1.0 — the Thursday demo (Ch 2)
- add + list; quotes-safe args; atomic writes with corrupt-backup
