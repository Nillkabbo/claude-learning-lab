# M10 · Capstone (lesson 0022)

The master checklist, executable: four functions that wire the whole course into the
Apex Assistant, and a CLI (`cli.py`, given) that runs them.

**Read first:** [0022 · Capstone](../../../lessons/0022-capstone.html) — the 11-line
checklist this milestone turns into code.

## The setup

`fixtures.py` (given, working): the lanes and a classifier, a dirty scripted draft
(SSN + competitor), 2-of-3 safety verdicts, policy topics, a digest plan with an
injectable worker failure, a 10-case eval suite with exactly two failures, usage and
prices, and an architecture dict with 9 of 11 checklist items satisfied. Your job is
the four TODOs in `capstone.py`:

1. **`handle_ticket(ticket, ctx)`** — the support flow: route the lane; abusive gets
   the canned response with no model call; easy/hard draft and run the *enforced*
   compliance filters (PII, competitors) plus the 2-of-3 vote; regulated adds the
   privacy flag; flagged or policy-relevant tickets escalate with reasons.
2. **`nightly_digest(plan, worker, artifact_dir, recorder)`** — plan saved and logged
   BEFORE workers; references back (not contents); failures isolated; the report
   names every area, failed ones visibly included.
3. **`report_card(cases, usage, prices, batch)`** — the eval outcome (normalized
   exact match, failing ids) AND the bill (0.1×/1.25×/1× input sides, full-price
   output, ×0.5 batch stacking), joined in one paste-able summary line.
4. **`master_checklist(architecture)`** — the design review: name the missing lines;
   empty list passes.

Then run the CLI (given, working once your TODOs are):

```bash
python3 cli.py support "gate for my flight please"
python3 cli.py digest
python3 cli.py report
```

## Done means

`python3 verify.py` shows M10 **GREEN** — all 12 checks — and `python3 verify.py`
shows **every milestone green**: the full roadmap, built by hand. Paste
`project: M1:8/8 … M10:12/12` (the whole line) to your agent. That line is the
course's finish tape — and the strongest possible walk into the CCAR-F exam.
