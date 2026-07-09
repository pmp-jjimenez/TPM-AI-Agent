import json
from pathlib import Path

DATA_DIR = Path("data/programs")


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def program_file(program_id):
    return DATA_DIR / f"{program_id}.json"


def create_program(program_name, description):
    ensure_data_dir()

    program_id = program_name.lower().replace(" ", "-")

    data = {
        "program_id": program_id,
        "program_name": program_name,
        "description": description,
        "phase": "Program Initiation",
        "health": "Unknown",
        "confidence": "Medium",
        "risks": [],
        "issues": [],
        "decisions": [],
        "next_actions": [],
        "meeting_history": [],
        "documents": [],
        "last_update": None
    }

    with open(program_file(program_id), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return data


def load_program(program_id):
    file = program_file(program_id)

    if not file.exists():
        return None

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_program(program):
    with open(program_file(program["program_id"]), "w", encoding="utf-8") as f:
        json.dump(program, f, indent=2)


def list_programs():
    ensure_data_dir()

    programs = []

    for file in DATA_DIR.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            programs.append(json.load(f))

    return programs