"""M2 acceptance tests — 8 checks. python3 verify.py to run them."""
import unittest

from fixtures import JsonModel, GOOD, GOOD_TEXT, FENCED_TEXT, OUT_OF_RANGE_TEXT, BAD_CODE_TEXT, LOW_CONF_TEXT
from extractor import (
    DELAY_SCHEMA, validate_schema, parse_model_json, semantic_validate, extract,
    UnsupportedSchemaError, SchemaViolation, SemanticViolation,
)


class M2Tests(unittest.TestCase):

    def test_fixture_model_works(self):
        m = JsonModel([GOOD_TEXT])
        self.assertEqual(m.complete({"messages": []}), GOOD_TEXT)

    def test_schema_accepts_valid_extraction(self):
        validate_schema(GOOD, DELAY_SCHEMA)  # must not raise

    def test_schema_rejects_missing_required_field(self):
        broken = {k: v for k, v in GOOD.items() if k != "reason"}
        with self.assertRaises(SchemaViolation):
            validate_schema(broken, DELAY_SCHEMA)

    def test_schema_rejects_bad_enum_value(self):
        with self.assertRaises(SchemaViolation):
            validate_schema({**GOOD, "reason": "birds"}, DELAY_SCHEMA)

    def test_unsupported_constraint_raises_400_style_error(self):
        schema_with_maximum = {
            "type": "object",
            "properties": {"delay_minutes": {"type": "integer", "maximum": 300}},
            "required": ["delay_minutes"],
        }
        with self.assertRaises(UnsupportedSchemaError):
            validate_schema({"delay_minutes": 100}, schema_with_maximum)

    def test_semantic_rejects_out_of_range_delay(self):
        data = parse_model_json(OUT_OF_RANGE_TEXT)
        validate_schema(data, DELAY_SCHEMA)              # grammar is happy…
        with self.assertRaises(SemanticViolation):        # …your code must not be
            semantic_validate(data)

    def test_semantic_rejects_bad_airport_code(self):
        data = parse_model_json(BAD_CODE_TEXT)
        with self.assertRaises(SemanticViolation):
            semantic_validate(data)

    def test_low_confidence_flags_human_review(self):
        low = extract("AX204 departed late from Austin.", JsonModel([LOW_CONF_TEXT]))
        self.assertTrue(low.needs_human_review)
        self.assertIn("low-confidence", low.flags)
        self.assertIn("Austin", low.source_text)          # provenance preserved
        good = extract("AX204 departed late from Austin.", JsonModel([GOOD_TEXT]))
        self.assertFalse(good.needs_human_review)

    def test_fenced_output_still_parses(self):
        data = parse_model_json(FENCED_TEXT)
        self.assertEqual(data["flight_number"], "AX204")


if __name__ == "__main__":
    unittest.main()
