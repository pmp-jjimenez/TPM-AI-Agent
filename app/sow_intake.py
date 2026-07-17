from llm import generate_response
from memory import create_program_data
from pdf_extractor import PDFExtractionError, extract_pdf_text
from persona_routing import calculate_persona_routing, display_persona_routing, persona_display_name
from prompt_builder import build_sow_analysis_prompt
from schema import validate_program
from sow_analysis import SOWAnalysisError, map_analysis_to_program, parse_sow_analysis


class SOWIntakeError(ValueError):
    """A user-actionable failure at a specific SOW intake boundary."""


def create_program_from_sow(pdf_path):
    try:
        extraction = extract_pdf_text(pdf_path)
    except PDFExtractionError as error:
        raise SOWIntakeError(f"PDF extraction failed: {error}") from error

    metadata = extraction["metadata"]
    prompt = build_sow_analysis_prompt(
        extraction["text"],
        metadata["source_filename"],
        truncated=metadata["truncated"],
    )

    response = generate_response(prompt)
    if not isinstance(response, str) or response.startswith("ERROR"):
        detail = response if isinstance(response, str) else "No response was returned."
        raise SOWIntakeError(f"Gemini analysis failed: {detail}")

    try:
        analysis = parse_sow_analysis(response, metadata["source_filename"])
    except SOWAnalysisError as error:
        raise SOWIntakeError(f"Invalid Gemini SOW analysis: {error}") from error

    program = map_analysis_to_program(analysis)
    valid, errors = validate_program(program)
    if not valid:
        raise SOWIntakeError("Program validation failed: " + "; ".join(errors))

    routing, fallback_used = calculate_persona_routing(
        menu_mode="Start New Program",
        workflow_name="sow_program_initiation",
        user_request=_routing_text(analysis),
        program=program,
        extra_signals=["new program", "SOW", "initiation"],
    )

    try:
        saved_program = create_program_data(program)
    except FileExistsError as error:
        raise SOWIntakeError(str(error)) from error
    except (OSError, ValueError) as error:
        raise SOWIntakeError(f"Program save failed: {error}") from error

    display_persona_routing(routing, fallback_used=fallback_used)
    print(render_initiation_summary(saved_program, analysis, routing, metadata))
    return saved_program, analysis, routing


def render_initiation_summary(program, analysis, routing, extraction_metadata=None):
    extraction_metadata = extraction_metadata or {}
    lines = [
        "",
        "Program Created from SOW",
        "------------------------",
        "",
        f"Program: {_display(program.get('program_name'))}",
        f"Customer: {_display(program.get('customer'))}",
        f"Phase: {_display(program.get('phase'))}",
        f"Program type: {_display(analysis.get('program_type'))}",
        f"Products/services: {_display_list(analysis.get('products_or_services'))}",
        f"Primary persona: {persona_display_name(routing.get('primary_persona', 'technical_program_manager'))}",
        f"Supporting personas: {_persona_list(routing.get('supporting_personas'))}",
        f"Initial risks: {_display_list(analysis.get('risks'))}",
        f"Missing critical information: {_display_list(analysis.get('missing_critical_information'))}",
        f"Recommended next action: {_display(analysis.get('recommended_next_action'))}",
        f"Confidence: {_display(program.get('confidence'))}",
        f"Saved program: {program.get('program_id')}.json",
    ]
    if extraction_metadata.get("truncated"):
        lines.append("Extraction: Text was truncated at the configured safety limit.")
    return "\n".join(lines)


def _routing_text(analysis):
    values = [
        analysis.get("program_type", ""),
        " ".join(_descriptions(analysis.get("products_or_services"))),
        " ".join(_descriptions(analysis.get("integrations"))),
        " ".join(_descriptions(analysis.get("risks"))),
    ]
    return " ".join(value for value in values if value)


def _descriptions(items):
    descriptions = []
    for item in items or []:
        if isinstance(item, str) and item.strip():
            descriptions.append(item.strip())
        elif isinstance(item, dict):
            for key in ("description", "name", "title", "risk"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    descriptions.append(value.strip())
                    break
    return descriptions


def _display(value):
    return value.strip() if isinstance(value, str) and value.strip() else "Not identified"


def _display_list(items, limit=3):
    descriptions = _descriptions(items)
    if not descriptions:
        return "None identified"
    shown = "; ".join(descriptions[:limit])
    remaining = len(descriptions) - limit
    return f"{shown} (+{remaining} more)" if remaining > 0 else shown


def _persona_list(personas):
    if not personas:
        return "None"
    return ", ".join(persona_display_name(persona) for persona in personas)
