---
description: Runs the full release ritual for Tracker. Use when asked to release or bump.
argument-hint: "[version, e.g. v0.4]"
allowed-tools: Bash(python3 *), Bash(git *)
---
Run the tests first (python3 -m unittest discover -s tests); ABORT the release
if any fail. Then bump VERSION in tracker.py, prepend a dated CHANGELOG.md
entry, commit "release: <version>", tag, push with tags. Announce nothing.
