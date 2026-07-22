from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from program_domain import DomainValidationError, normalize_program_entities


CURRENT_SCHEMA_VERSION = "1.2.0"
SUPPORTED_SCHEMA_VERSIONS = (None, "1.0.0", "1.1.0", CURRENT_SCHEMA_VERSION)

DEFAULT_PHASE = "Program Initiation"
DEFAULT_HEALTH = "Unknown"
DEFAULT_CONFIDENCE = "Medium"
DEFAULT_SOURCE = "cli"

LIST_FIELDS = (
    "risks",
    "issues",
    "decisions",
    "next_actions",
    "meeting_history",
    "documents",
    "artifacts",
    "relationships",
)


def utc_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def generate_item_id(prefix):
    return f"{prefix}-{uuid4()}"


def create_program_record(program_id, program_name, description, source=DEFAULT_SOURCE):
    now = utc_timestamp()
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "program_id": program_id,
        "program_name": program_name,
        "description": description,
        "customer": "",
        "phase": DEFAULT_PHASE,
        "health": DEFAULT_HEALTH,
        "confidence": DEFAULT_CONFIDENCE,
        "risks": [],
        "issues": [],
        "decisions": [],
        "next_actions": [],
        "meeting_history": [],
        "documents": [],
        "artifacts": [],
        "relationships": [],
        "metadata": {
            "created_at": now,
            "updated_at": now,
            "source": source,
        },
    }


def apply_compatibility_defaults(program):
    normalized = deepcopy(program) if isinstance(program, dict) else {}

    if normalized.get("schema_version") in SUPPORTED_SCHEMA_VERSIONS:
        normalized["schema_version"] = CURRENT_SCHEMA_VERSION
    normalized.setdefault("program_id", "")
    normalized.setdefault("program_name", "")
    normalized.setdefault("description", "")
    normalized.setdefault("customer", "")
    normalized.setdefault("phase", DEFAULT_PHASE)
    normalized.setdefault("health", DEFAULT_HEALTH)
    normalized.setdefault("confidence", DEFAULT_CONFIDENCE)

    for field in LIST_FIELDS:
        if not isinstance(normalized.get(field), list):
            normalized[field] = []

    metadata = normalized.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    metadata.setdefault("created_at", None)
    metadata.setdefault("updated_at", None)
    metadata.setdefault("source", DEFAULT_SOURCE)
    normalized["metadata"] = metadata

    try:
        actions, risks, relationships = normalize_program_entities(normalized)
    except DomainValidationError as error:
        raise ValueError(f"Invalid Program domain data: {error}") from error
    normalized["next_actions"] = actions
    normalized["risks"] = risks
    normalized["relationships"] = relationships

    return normalized


def validate_program(program):
    errors = []

    if not isinstance(program, dict):
        return False, ["program must be a JSON object"]

    for field in ("program_id", "program_name", "description"):
        value = program.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    if not isinstance(program.get("customer", ""), str):
        errors.append("customer must be a string")

    for field in ("schema_version", "phase", "health", "confidence"):
        value = program.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    if program.get("schema_version") != CURRENT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CURRENT_SCHEMA_VERSION}")

    for field in LIST_FIELDS:
        if not isinstance(program.get(field), list):
            errors.append(f"{field} must be a list")

    if not errors:
        try:
            normalize_program_entities(program)
        except DomainValidationError as error:
            errors.append(str(error))

    metadata = program.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
    else:
        for field in ("created_at", "updated_at", "source"):
            if field not in metadata:
                errors.append(f"metadata.{field} is required")
        source = metadata.get("source")
        if not isinstance(source, str) or not source.strip():
            errors.append("metadata.source must be a non-empty string")

    return len(errors) == 0, errors
