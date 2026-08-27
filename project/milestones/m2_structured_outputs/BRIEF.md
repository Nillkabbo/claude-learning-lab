# M2 · Structured outputs (lesson 0004)

Build the Apex delay extractor with Lesson 0004's three validation layers as real code:
the **grammar** (what constrained decoding would enforce — and what it would reject with
a 400), the **semantic** layer (your code, post-parse), and the **human-review** gate
(low confidence, with provenance kept).

**Read first:** [0004 · Structured outputs](../../../lessons/0004-structured-outputs.html)

## The setup

`fixtures.py` (given, working) provides a `JsonModel` that returns raw text — sometimes
clean JSON, sometimes fenced with a chatty preamble, sometimes subtly wrong. The
`DELAY_SCHEMA` in `extractor.py` is the grammar-supported subset straight from the
lesson's table: types, enums, required. Your job is the four TODOs:

1. **`validate_schema(data, schema)`** — enforce object shape, property types, enum
   membership, required fields (`SchemaViolation`). If the schema itself asks for
   anything the grammar can't say — numerical constraints, length limits — raise
   `UnsupportedSchemaError`, exactly like the API's 400.
2. **`parse_model_json(text)`** — pull the JSON object out of raw model text, fences
   and preamble included.
3. **`semantic_validate(data)`** — the rules the grammar can't express:
   `delay_minutes` in [0, 300]; `airport_code` exactly three uppercase letters.
4. **`extract(report_text, model, threshold)`** — the pipeline: parse → grammar →
   semantics, then the review gate (confidence below threshold → `needs_human_review`
   with a flag) and provenance (keep the source text on the result).

## Done means

`python3 verify.py` shows M2 **GREEN** — all 9 checks, including the two that prove you
know *which layer owns which rule*. Paste `project: M2:9/9` to your agent and say
**"next milestone"**.
