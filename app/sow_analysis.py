import json
from copy import deepcopy

from schema import create_program_record, generate_item_id


ANALYSIS_VERSION = "1.0.0"

STRING_FIELDS = (
    "document_title",
    "customer_name",
    "program_name",
    "business_objective",
    "executive_summary",
    "program_type",
    "recommended_primary_persona",
    "recommended_next_action",
    "source_filename",
    "analysis_version",
)

LIST_FIELDS = (
    "products_or_services",
    "in_scope",
    "out_of_scope",
    "deliverables",
    "assumptions",
    "dependencies",
    "integrations",
    "environments_or_platforms",
    "locations_or_countries",
    "licensing_or_capacity",
    "key_stakeholders",
    "customer_responsibilities",
    "supplier_responsibilities",
    "acceptance_criteria",
    "milestones",
    "risks",
    "open_questions",
    "missing_critical_information",
    "recommended_supporting_personas",
)


class SOWAnalysisError(ValueError):
    """Raised when Gemini does not return a usable SOW analysis."""


def parse_sow_analysis(response_text, source_filename=""):
    if not isinstance(response_text, str) or not response_text.strip():
        raise SOWAnalysisError("Gemini returned an empty SOW analysis.")

    candidate = _remove_json_fence(response_text.strip())
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise SOWAnalysisError("Gemini returned invalid JSON for the SOW analysis.") from error

    if not isinstance(parsed, dict):
        raise SOWAnalysisError("The SOW analysis must be a JSON object.")

    normalized = {}
    for field in STRING_FIELDS:
        value = parsed.get(field)
        if value is None:
            normalized[field] = ""
        elif isinstance(value, str):
            normalized[field] = value.strip()
        else:
            raise SOWAnalysisError(f"SOW analysis field '{field}' must be a string or null.")

    normalized["confidence"] = _normalize_confidence(parsed.get("confidence"))

    for field in LIST_FIELDS:
        value = parsed.get(field)
        if value is None:
            normalized[field] = []
        elif isinstance(value, list):
            normalized[field] = deepcopy(value)
        else:
            raise SOWAnalysisError(f"SOW analysis field '{field}' must be a list or null.")

    normalized["source_filename"] = source_filename or normalized["source_filename"]
    normalized["analysis_version"] = normalized["analysis_version"] or ANALYSIS_VERSION

    if not any(
        normalized[field]
        for field in ("program_name", "customer_name", "business_objective", "executive_summary")
    ):
        raise SOWAnalysisError(
            "The SOW analysis does not contain enough information to create a program."
        )
    return normalized


def map_analysis_to_program(analysis):
    snapshot = deepcopy(analysis)
    program_name = (
        _string(snapshot.get("program_name"))
        or _string(snapshot.get("document_title"))
        or "SOW-Initiated Program"
    )
    objective = (
        _string(snapshot.get("business_objective"))
        or _string(snapshot.get("executive_summary"))
        or "Program initiated from a Statement of Work."
    )
    customer = _string(snapshot.get("customer_name"))
    program_id = _slugify(program_name)
    program = create_program_record(
        program_id,
        program_name,
        objective,
        source="sow_pdf",
    )
    program["customer"] = customer
    program["confidence"] = _normalize_confidence(snapshot.get("confidence"))

    for risk in snapshot.get("risks") or []:
        description = _item_description(risk)
        if description:
            program["risks"].append({
                "risk_id": generate_item_id("risk"),
                "description": description,
                "status": "Open",
                "source": "SOW analysis",
            })

    actions = []
    recommended = _string(snapshot.get("recommended_next_action"))
    if recommended:
        actions.append(recommended)
    for item in (snapshot.get("missing_critical_information") or []):
        description = _item_description(item)
        if description:
            actions.append(f"Clarify missing critical information: {description}")
    for item in (snapshot.get("open_questions") or []):
        description = _item_description(item)
        if description:
            actions.append(f"Resolve open question: {description}")

    for description in _unique(actions):
        program["next_actions"].append({
            "action_id": generate_item_id("action"),
            "description": description,
            "status": "Open",
            "source": "SOW analysis",
        })

    filename = _string(snapshot.get("source_filename"))
    if filename:
        program["documents"].append({
            "document_type": "SOW",
            "filename": filename,
            "original_file_persisted": False,
        })
    return program


def _remove_json_fence(text):
    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].strip().lower() in ("```json", "```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def _string(value):
    return value.strip() if isinstance(value, str) else ""


def _item_description(item):
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        for field in ("description", "risk", "question", "name", "title"):
            value = _string(item.get(field))
            if value:
                return value
    return ""


def _normalize_confidence(value):
    if isinstance(value, str):
        normalized = value.strip().lower()
        return {"high": "High", "medium": "Medium", "low": "Low"}.get(
            normalized, "Medium"
        )
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 0 <= value <= 1:
            return "High" if value >= 0.75 else "Medium" if value >= 0.40 else "Low"
        if 1 < value <= 100:
            return "High" if value >= 75 else "Medium" if value >= 40 else "Low"
        return "Medium"
    if isinstance(value, dict):
        for field in ("level", "value", "score", "confidence"):
            if field in value:
                return _normalize_confidence(value[field])
    return "Medium"


def _slugify(value):
    characters = []
    previous_dash = False
    for character in value.lower():
        if character.isalnum():
            characters.append(character)
            previous_dash = False
        elif not previous_dash:
            characters.append("-")
            previous_dash = True
    return "".join(characters).strip("-") or "sow-initiated-program"


def _unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
