---
description: Pulls my open GitHub issues into Tracker as tasks. Use when asked to sync.
allowed-tools: mcp__github__list_issues, Read, Write
---
Fetch open issues assigned to me via the GitHub MCP server. For each: if no
Tracker task mentions the issue number, add one formatted "[gh-N] title".
Report added and skipped counts. (Requires the MCP server + its trust review
in CLAUDE.md — Chapter 6's rule.)
