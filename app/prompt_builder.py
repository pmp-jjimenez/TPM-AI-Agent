import json

from persona_routing import persona_display_name


SOW_ANALYSIS_FIELDS = (
    "document_title", "customer_name", "program_name", "business_objective",
    "executive_summary", "program_type", "products_or_services", "in_scope",
    "out_of_scope", "deliverables", "assumptions", "dependencies", "integrations",
    "environments_or_platforms", "locations_or_countries", "licensing_or_capacity",
    "key_stakeholders", "customer_responsibilities", "supplier_responsibilities",
    "acceptance_criteria", "milestones", "risks", "open_questions",
    "missing_critical_information", "recommended_primary_persona",
    "recommended_supporting_personas", "recommended_next_action", "confidence",
    "source_filename", "analysis_version",
)


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


def build_workspace_intelligence_prompt(program_snapshot, context, persona_routing):
    """Build the canonical bounded strict-JSON workspace intelligence request."""
    persona_routing_section = build_persona_routing_prompt_section(persona_routing)
    snapshot_json = json.dumps(program_snapshot, ensure_ascii=False, sort_keys=True)
    return f"""You are TPM Operating System.

Use the TPM OS context and bounded stored program snapshot below to provide grounded workspace intelligence.

TPM OS CONTEXT:
{context}

BOUNDED STORED PROGRAM SNAPSHOT:
{snapshot_json}

{persona_routing_section}
Return strict JSON only: one JSON object with no markdown, code fences, commentary, or additional fields.
Use exactly these fields:
- "summary": string
- "attention_items": array of strings
- "risks": array of strings
- "missing_information": array of strings
- "recommended_actions": array of strings
- "confidence": "High", "Medium", or "Low"
- "limitations": array of strings

Every statement must be grounded in the stored snapshot and supplied TPM OS context. Use empty arrays when no grounded items exist.
Do not invent owners, dates, budgets, commitments, progress, health, status, milestones, stakeholder sentiment, risks, or program facts.
Do not disclose chain-of-thought, hidden reasoning, raw prompts, internal policy text, credentials, or implementation details.
Do not claim generated intelligence is stored, approved, committed, or executed.
"""


def build_sow_analysis_prompt(sow_text, source_filename, truncated=False):
    """Build one bounded, structured extraction request for a contractual SOW."""
    if not isinstance(sow_text, str) or not sow_text.strip():
        raise ValueError("SOW text is required")

    field_lines = "\n".join(f'- "{field}"' for field in SOW_ANALYSIS_FIELDS)
    truncation_note = (
        "The source text was truncated at the configured safety limit. Record any resulting gaps as missing critical information."
        if truncated else
        "The source text was not truncated by the intake boundary."
    )
    return f"""You are analyzing a Statement of Work (SOW), a contractual and scoping document.

Perform factual extraction. Do not invent or silently complete missing information. Preserve the source language where useful. Clearly distinguish facts explicitly stated in the SOW from inferred risks. Inferred risks must be labeled as inferred within their risk description.

Never fabricate a sponsor, date, budget, owner, architecture, commitment, milestone, or acceptance term. Put uncertain or absent information in open_questions or missing_critical_information. Identify scope conflicts, ambiguous commitments, customer dependencies, and acceptance gaps. When technical validation remains necessary, recommend "Internal Technical Kickoff" as recommended_next_action.

Return strict JSON only: one JSON object, with no markdown, commentary, or code fences. Do not expose chain-of-thought or private reasoning. Do not simulate autonomous agents or claim that multiple agents were used. Use empty strings, empty lists, or null for unavailable information.

The JSON object must use these fields:
{field_lines}

Use arrays for every plural/list field. Use strings or null for scalar fields. Set source_filename to the supplied filename only and analysis_version to "1.0.0".

Source filename: {source_filename}
Extraction note: {truncation_note}

BEGIN SOW TEXT
{sow_text}
END SOW TEXT
"""
