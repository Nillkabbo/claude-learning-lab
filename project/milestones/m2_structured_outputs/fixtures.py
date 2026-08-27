"""M2 fixtures — a model that returns raw text (sometimes fenced, sometimes flawed).

Lesson 0004 in miniature: the model returns text; YOU enforce shape, semantics,
and review gates. Self-contained on purpose (each milestone directory is standalone).
"""
import json


class JsonModel:
    """Stateless stand-in returning scripted raw text, like a text content block."""

    def __init__(self, texts):
        self._texts = list(texts)
        self.requests_seen = []

    def complete(self, request):
        self.requests_seen.append(request)
        return self._texts.pop(0)


def _json_text(d):
    return json.dumps(d)


GOOD = {
    "flight_number": "AX204",
    "airport_code": "AUS",
    "delay_minutes": 45,
    "reason": "weather",
    "confidence": 0.93,
}
GOOD_TEXT = _json_text(GOOD)

# Same data, but wrapped in markdown fences with a chatty preamble — parse it anyway.
FENCED_TEXT = "Sure! Here is the extraction:\n```json\n" + _json_text(GOOD) + "\n```\n"

# Grammar-valid shape, semantics broken (delay out of the 0–300 policy range).
OUT_OF_RANGE_TEXT = _json_text({**GOOD, "delay_minutes": 450})

# Grammar-valid shape, semantics broken (airport code not exactly three letters).
BAD_CODE_TEXT = _json_text({**GOOD, "airport_code": "AUST"})

# Shape and semantics fine, but confidence below the review threshold.
LOW_CONF_TEXT = _json_text({**GOOD, "confidence": 0.41})
