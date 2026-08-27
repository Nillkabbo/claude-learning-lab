# M9 · Workflow design & lifecycle (lessons 0018–0021)

The support brain and the security checklist, as code: escalation with a real context
handoff, compliance as deterministic filters (prompts are context — these are
enforced), the degradation ladder with no silent failures, paired metrics that catch
gaming, and the MCP review from Lesson 0021's seven-attack catalog.

**Read first:** [0018 · Workflow design](../../../lessons/0018-workflow-design.html)
· [0020 · Lifecycle management](../../../lessons/0020-lifecycle-management.html)
· [0021 · Trust, security & MCP](../../../lessons/0021-trust-security-mcp.html)

## The setup

`fixtures.py` (given, working): a three-turn conversation with a policy landmine, a
PII-and-competitor-laden response plus a clean one, the three-failure catalog (your
runbook skeleton), and two MCP integrations — one guilty of all four sins, one clean.
Your job is the five TODOs in `workflow.py`:

1. **`escalate(conversation, confidence, policy_topics)`** — triggers (low
   confidence, policy topic in the last user message, explicit human request) and a
   handoff the human can actually use: summary, state, provenance.
2. **`compliance_stack(text, competitors)`** — SSN patterns → `[PII removed]`,
   competitor names → `[competitor]`, flags for what fired. Code, not prompts.
3. **`degrade(failure)`** — a designed exit for every catalog failure: non-empty
   message (never silence, never fabrication), what still works, what happens next.
   The mid-charge timeout says UNKNOWN and demands verification — never "retry now".
4. **`paired_metrics(deflection, csat)`** — healthy only when deflection sits in the
   official 70–80% band AND CSAT ≥ 4; high deflection with falling CSAT flags
   `"gaming"`.
5. **`mcp_review(integration)`** — the checklist: token passthrough, wildcard scopes,
   session auth, missing one-click consent — findings for each; empty means approved.

## Done means

`python3 verify.py` shows M9 **GREEN** — all 12 checks, including the no-silent-failure
loop over the whole catalog and the four-finding review. Paste `project: M9:12/12` to
your agent and say **"next milestone"**.
