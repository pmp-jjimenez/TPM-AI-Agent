from copy import deepcopy

from persona_router import PERSONA_REGISTRY, ROUTING_VERSION, route_personas


FALLBACK_REASON = (
    "Persona routing was unavailable, so the default Technical Program Manager "
    "persona was used."
)


def persona_display_name(persona_id):
    persona = PERSONA_REGISTRY.get(persona_id)

    if isinstance(persona, str) and persona:
        return persona

    if isinstance(persona, dict):
        display_name = persona.get("display_name")
        if display_name:
            return display_name

    return str(persona_id).replace("_", " ").title()


def build_routing_context(
    menu_mode,
    workflow_name,
    user_request=None,
    program=None,
    extra_signals=None,
):
    """Build a non-mutating routing context from available CLI operation data."""
    program_snapshot = deepcopy(program) if isinstance(program, dict) else {}
    context = {
        "menu_mode": menu_mode,
        "workflow_name": workflow_name,
        "user_request": user_request or "",
        "program": {
            "program_id": program_snapshot.get("program_id"),
            "program_name": program_snapshot.get("program_name"),
            "description": program_snapshot.get("description"),
            "program_type": program_snapshot.get("program_type"),
            "phase": program_snapshot.get("phase"),
            "health": program_snapshot.get("health"),
            "confidence": program_snapshot.get("confidence"),
            "risks": program_snapshot.get("risks", []),
            "issues": program_snapshot.get("issues", []),
            "decisions": program_snapshot.get("decisions", []),
            "next_actions": program_snapshot.get("next_actions", []),
        },
        "signals": list(extra_signals or []),
    }
    return context


def fallback_persona_routing():
    return {
        "primary_persona": "technical_program_manager",
        "supporting_personas": [],
        "reasons": [FALLBACK_REASON],
        "routing_version": ROUTING_VERSION,
    }


def calculate_persona_routing(
    menu_mode,
    workflow_name,
    user_request=None,
    program=None,
    extra_signals=None,
):
    """Calculate routing once at the application boundary with controlled fallback."""
    context = build_routing_context(
        menu_mode=menu_mode,
        workflow_name=workflow_name,
        user_request=user_request,
        program=program,
        extra_signals=extra_signals,
    )

    try:
        combined_request = " ".join(
            value
            for value in [
                context["user_request"],
                " ".join(context["signals"]),
            ]
            if value
        )
        return route_personas(
            program_context=context["program"],
            requested_mode=context["menu_mode"],
            workflow=context["workflow_name"],
            user_request=combined_request,
        ), False
    except Exception:
        return fallback_persona_routing(), True


def render_persona_routing(routing, fallback_used=False):
    lines = [
        "",
        "Persona Routing",
        "---------------",
        "",
    ]

    if fallback_used:
        lines.append(
            "Warning: Persona routing was unavailable. The default TPM persona will be used."
        )
        lines.append("")

    primary_persona = routing.get("primary_persona", "technical_program_manager")
    lines.append("Primary Persona:")
    lines.append(persona_display_name(primary_persona))
    lines.append("")

    lines.append("Supporting Personas:")
    supporting = routing.get("supporting_personas") or []
    if supporting:
        for persona_id in supporting:
            lines.append(f"- {persona_display_name(persona_id)}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("Routing Reasons:")
    reasons = routing.get("reasons") or []
    if reasons:
        for reason in reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None")

    return "\n".join(lines)


def display_persona_routing(routing, fallback_used=False):
    print(render_persona_routing(routing, fallback_used=fallback_used))
