"""M2 starter — implement the TODO sections. Read BRIEF.md first.

Lesson 0004's three validation layers, as code:
  grammar   -> validate_schema()        (what constrained decoding would enforce)
  semantic  -> semantic_validate()      (your code, post-parse)
  human     -> review flags in extract()(high stakes / low confidence)
"""
import json
import re
from dataclasses import dataclass, field

# The grammar layer: only what constrained decoding SUPPORTS (Lesson 0004's table).
# Types, enums, required — no numerical constraints, no minLength/maxLength.
DELAY_SCHEMA = {
    "type": "object",
    "properties": {
        "flight_number": {"type": "string"},
        "airport_code": {"type": "string"},
        "delay_minutes": {"type": "integer"},
        "reason": {"enum": ["weather", "crew", "mechanical", "air_traffic"]},
        "confidence": {"type": "number"},
    },
    "required": ["flight_number", "airport_code", "delay_minutes", "reason", "confidence"],
}

# Keys the grammar layer CANNOT enforce — per the official docs these 400 at request
# time. Your validator must refuse them the same way, with a different exception.
UNSUPPORTED_SCHEMA_KEYS = {"minimum", "maximum", "multipleOf", "minLength", "maxLength"}


class UnsupportedSchemaError(Exception):
    """The schema asks the grammar for something it can't say (an API 400)."""


class SchemaViolation(Exception):
    """Shape is wrong: missing required field, wrong type, bad enum value."""


class SemanticViolation(Exception):
    """Grammar-valid but rule-breaking — ranges, formats: your code's job."""


@dataclass
class Extraction:
    data: dict
    needs_human_review: bool = False
    flags: list = field(default_factory=list)
    source_text: str = ""    # provenance: the report the extraction came from


# ------------------------------------------------------------------
# TODO 1: the grammar layer
# Validate `data` against `schema` (object type, per-property types, enum
# membership, required fields present). Raise SchemaViolation with a useful
# message on any shape problem. If the SCHEMA itself contains any key from
# UNSUPPORTED_SCHEMA_KEYS (anywhere in properties), raise
# UnsupportedSchemaError — mimicking the API's 400.
# ------------------------------------------------------------------
def validate_schema(data, schema):
    raise NotImplementedError("TODO 1: validate_schema")


# ------------------------------------------------------------------
# TODO 2: parse the model's raw text
# The model returns a text block that may carry a preamble and markdown
# json fences. Extract the JSON and return it as a dict; raise ValueError
# if no JSON object is found.
# ------------------------------------------------------------------
def parse_model_json(text):
    raise NotImplementedError("TODO 2: parse_model_json")


# ------------------------------------------------------------------
# TODO 3: the semantic layer (the grammar can't say these)
# - delay_minutes must be an integer in [0, 300]
# - airport_code must be EXACTLY three uppercase letters ([A-Z]{3})
# Raise SemanticViolation naming the broken rule.
# ------------------------------------------------------------------
def semantic_validate(data):
    raise NotImplementedError("TODO 3: semantic_validate")


# ------------------------------------------------------------------
# TODO 4: the full pipeline with the human-review gate
# Parse -> schema-validate -> semantic-validate; then flags:
# - confidence below `threshold` -> needs_human_review=True, flag
#   "low-confidence"
# Always keep source_text for provenance. Return an Extraction.
# ------------------------------------------------------------------
def extract(report_text, model, threshold=0.7):
    raise NotImplementedError("TODO 4: extract")
