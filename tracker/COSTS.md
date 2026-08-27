# Costs — Chapter 11's ledger (with numbers)

- Driver: nightly sync contexts, ~40% of the step-down target; lever applied:
  stable-prefix prompt ordering → cached reads at 0.1x on the ~2,000-token prefix
  (measured shape: reads 0.5Mtok x 3.00 x 0.1 = $0.15 vs $1.50 uncached)
- Right-size: sync + diff review on the small tier (-60% per call); ultrareview
  reserved for >300-line branches
- Fence: workspace spend cap at 2x median month; the LIMIT pages, not a person
- Habit: /clear between unrelated tasks; /context before big ones

## Settings chain (managed -> repo -> local)
- managed (org): hook allowlist, spend caps, deny of destructive patterns
- repo (.claude/settings.json, committed): the push/main denies, task-file Read denies
- local (gitignored): personal overrides — none currently
