from pathlib import Path


def load_markdown_file(file_path):
    path = Path(file_path)

    if not path.exists():
        return f"[Missing file: {file_path}]"

    return path.read_text(encoding="utf-8")


def load_core_context():
    files = [
        "instructions/master-prompt.md",
        "knowledge/capability-router.md",
        "knowledge/confidence-engine.md",
        "knowledge/program-state-model.md",
        "playbooks/sow-to-program-initiation.md",
        "templates/project-charter.md",
        "templates/raid-log.md",
    ]

    context = ""

    for file in files:
        context += f"\n\n--- FILE: {file} ---\n"
        context += load_markdown_file(file)

    return context