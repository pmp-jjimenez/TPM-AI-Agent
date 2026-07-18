import json


INTELLIGENCE_FIELDS = {
    "summary",
    "attention_items",
    "risks",
    "missing_information",
    "recommended_actions",
    "confidence",
    "limitations",
}
LIST_FIELDS = (
    "attention_items",
    "risks",
    "missing_information",
    "recommended_actions",
    "limitations",
)
CONFIDENCE_LEVELS = {"High", "Medium", "Low"}
MAX_SUMMARY_LENGTH = 2000
MAX_ITEM_LENGTH = 500
MAX_LIST_ITEMS = 20


class IntelligenceAnalysisError(ValueError):
    """Raised when provider output is not a complete intelligence contract."""


def parse_intelligence_analysis(response_text):
    if not isinstance(response_text, str) or not response_text.strip():
        raise IntelligenceAnalysisError("Intelligence response is empty.")
    try:
        parsed = json.loads(response_text.strip())
    except json.JSONDecodeError as error:
        raise IntelligenceAnalysisError("Intelligence response is not strict JSON.") from error
    if not isinstance(parsed, dict) or set(parsed) != INTELLIGENCE_FIELDS:
        raise IntelligenceAnalysisError("Intelligence response fields are unsupported.")

    summary = _bounded_text(parsed["summary"], MAX_SUMMARY_LENGTH, "summary", allow_empty=True)
    confidence = parsed["confidence"]
    if confidence not in CONFIDENCE_LEVELS:
        raise IntelligenceAnalysisError("Intelligence confidence is unsupported.")

    result = {"summary": summary}
    for field in LIST_FIELDS:
        result[field] = _string_list(parsed[field], field)
    result["confidence"] = confidence
    return result


def _string_list(value, field):
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    return [_bounded_text(item, MAX_ITEM_LENGTH, field) for item in value]


def _bounded_text(value, limit, field, allow_empty=False):
    if not isinstance(value, str):
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    normalized = " ".join(value.split())
    if (not normalized and not allow_empty) or len(normalized) > limit:
        raise IntelligenceAnalysisError(f"Intelligence field '{field}' is unsupported.")
    return normalized
