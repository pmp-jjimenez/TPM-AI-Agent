from persona_routing import persona_display_name


def build_persona_routing_prompt_section(persona_routing=None):
    if not persona_routing:
        return ""

    primary = persona_display_name(
        persona_routing.get("primary_persona", "technical_program_manager")
    )
    supporting = persona_routing.get("supporting_personas") or []
    reasons = persona_routing.get("reasons") or []

    lines = [
        "PERSONA ROUTING CONTEXT",
        "",
        "Primary persona:",
        primary,
        "",
        "Supporting personas:",
    ]

    if supporting:
        for persona_id in supporting:
            lines.append(f"- {persona_display_name(persona_id)}")
    else:
        lines.append("- None")

    lines.extend([
        "",
        "Routing reasons:",
    ])

    if reasons:
        for reason in reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None")

    lines.extend([
        "",
        "Instructions for the AI:",
        "- Use the primary persona as the principal analysis perspective.",
        "- Use supporting personas as additional specialist perspectives.",
        "- Do not claim that independent autonomous agents were executed.",
        "- Produce one coherent response rather than simulated multi-agent dialogue.",
        "",
    ])

    return "\n".join(lines)


def build_new_program_prompt(project_description, context, persona_routing=None):
    persona_routing_section = build_persona_routing_prompt_section(persona_routing)
    prompt = f"""
You are TPM Operating System.

Use the TPM OS context below to analyze the user's project.

TPM OS CONTEXT:
{context}

USER PROJECT:
{project_description}

{persona_routing_section}
TASK:
Provide an initial TPM assessment.

Do not generate full project documents yet.

Return:

1. Current Program Phase
2. Program Type
3. Missing Information
4. Initial Risks
5. Recommended Playbooks
6. Initial Deliverables
7. Next Recommended Action
8. Confidence Level
9. Reason for Confidence
"""
    return prompt
