import json
import os
import tempfile
from pathlib import Path

from schema import (
    CURRENT_SCHEMA_VERSION,
    apply_compatibility_defaults,
    create_program_record,
    utc_timestamp,
    validate_program,
)

DATA_DIR = Path("data/programs")


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def program_file(program_id):
    return DATA_DIR / f"{program_id}.json"


def create_program(program_name, description):
    program_id = program_name.lower().replace(" ", "-")
    data = create_program_record(program_id, program_name, description)
    create_program_data(data)
    return data


def create_program_data(program):
    """Validate and create a program without silently replacing an existing one."""
    ensure_data_dir()
    normalized = apply_compatibility_defaults(program)
    valid, errors = validate_program(normalized)
    if not valid:
        raise ValueError("Invalid program record: " + "; ".join(errors))

    destination = program_file(normalized["program_id"])
    try:
        with open(destination, "x", encoding="utf-8") as file:
            json.dump(normalized, file, indent=2)
    except FileExistsError as error:
        raise FileExistsError(
            f"Program '{normalized['program_id']}' already exists; choose a different program name."
        ) from error
    return normalized


def load_program(program_id):
    file = program_file(program_id)

    if not file.exists():
        return None

    with open(file, "r", encoding="utf-8") as f:
        return apply_compatibility_defaults(json.load(f))


def save_program(program):
    ensure_data_dir()

    normalized = apply_compatibility_defaults(program)
    metadata = normalized["metadata"]
    metadata["created_at"] = metadata.get("created_at") or utc_timestamp()
    metadata["updated_at"] = utc_timestamp()
    normalized["schema_version"] = CURRENT_SCHEMA_VERSION

    valid, errors = validate_program(normalized)
    if not valid:
        raise ValueError("Invalid program record: " + "; ".join(errors))

    destination = program_file(normalized["program_id"])
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{normalized['program_id']}.", suffix=".tmp", dir=str(DATA_DIR)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            json.dump(normalized, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_name, destination)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise

    program.clear()
    program.update(normalized)


def list_programs():
    ensure_data_dir()

    programs = []

    for file in DATA_DIR.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            programs.append(apply_compatibility_defaults(json.load(f)))

    return programs
