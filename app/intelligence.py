from copy import deepcopy
from datetime import datetime, timezone

from context_loader import load_core_context
from intelligence_analysis import IntelligenceAnalysisError, parse_intelligence_analysis
from llm import ProviderExecutionError, execute_provider
from persona_routing import calculate_persona_routing, persona_display_name
from prompt_builder import build_workspace_intelligence_prompt


COMPLETENESS_FIELDS = (
    ("Sponsor", "sponsor"),
    ("Budget", "budget"),
    ("Target Go-Live", "target_go_live"),
    ("Architecture", "architecture"),
    ("Dependencies", "dependencies"),
    ("Governance", "governance"),
)
PROGRAM_LIST_LIMIT = 20
PROGRAM_TEXT_LIMIT = 1000
FALLBACK_LIMITATION = (
    "AI generation was unavailable; grounded deterministic intelligence is shown."
)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0)


class WorkspaceIntelligenceService:
    def __init__(self, provider=execute_provider, clock=utc_now, router=calculate_persona_routing):
        self.provider = provider
        self.clock = clock
        self.router = router

    def generate(self, program):
        snapshot = deepcopy(program) if isinstance(program, dict) else {}
        routing, _routing_fallback = self.router(
            menu_mode="Executive Program Workspace",
            workflow_name="workspace_intelligence",
            user_request="Generate workspace intelligence",
            program=snapshot,
            extra_signals=["executive review", "workspace intelligence"],
        )
        generated_at = self.clock().isoformat()
        transport_routing = _transport_routing(routing)
        bounded = bounded_program_snapshot(snapshot)
        try:
            prompt = build_workspace_intelligence_prompt(
                bounded, load_core_context(), routing
            )
            analysis = parse_intelligence_analysis(self.provider(prompt))
            return {
                "program_id": _text(snapshot.get("program_id")),
                "generated_at": generated_at,
                "source": "ai",
                "routing": transport_routing,
                **analysis,
            }
        except (ProviderExecutionError, IntelligenceAnalysisError):
            return deterministic_intelligence(
                snapshot, transport_routing, generated_at
            )


def bounded_program_snapshot(program):
    return {
        "program_id": _bounded_text(program.get("program_id")),
        "program_name": _bounded_text(program.get("program_name")),
        "description": _bounded_text(program.get("description")),
        "customer": _bounded_text(program.get("customer")),
        "phase": _bounded_text(program.get("phase")),
        "health": _bounded_text(program.get("health")),
        "confidence": _bounded_text(program.get("confidence")),
        "sponsor": _bounded_value(program.get("sponsor")),
        "budget": _bounded_value(program.get("budget")),
        "target_go_live": _bounded_value(program.get("target_go_live")),
        "architecture": _bounded_value(program.get("architecture")),
        "dependencies": _bounded_value(program.get("dependencies")),
        "governance": _bounded_value(program.get("governance")),
        "risks": _descriptions(program.get("risks")),
        "issues": _descriptions(program.get("issues")),
        "next_actions": _descriptions(program.get("next_actions")),
    }


def deterministic_intelligence(program, routing, generated_at):
    risks = _descriptions(program.get("risks"))
    issues = _descriptions(program.get("issues"))
    missing = [label for label, field in COMPLETENESS_FIELDS if not _has_value(program.get(field))]
    recommendations = []
    if _text(program.get("phase")).lower() == "program initiation":
        recommendations.append("Internal Technical Kickoff")
    if missing:
        recommendations.append("Collect executive program information: " + ", ".join(missing))
    summary = _deterministic_summary(program)
    return {
        "program_id": _text(program.get("program_id")),
        "generated_at": generated_at,
        "source": "deterministic_fallback",
        "routing": routing,
        "summary": summary,
        "attention_items": issues,
        "risks": risks,
        "missing_information": missing,
        "recommended_actions": recommendations,
        "confidence": _confidence(program.get("confidence")),
        "limitations": [FALLBACK_LIMITATION],
    }


def _transport_routing(routing):
    primary = routing.get("primary_persona", "technical_program_manager")
    return {
        "version": routing.get("routing_version", "1.0.0"),
        "primary_persona": {"id": primary, "display_name": persona_display_name(primary)},
        "supporting_personas": [
            {"id": persona, "display_name": persona_display_name(persona)}
            for persona in routing.get("supporting_personas") or []
        ],
    }


def _deterministic_summary(program):
    description = _text(program.get("description"))
    if not description:
        return "Available program information is insufficient to provide an executive summary."
    facts = []
    for label, field in (("Customer", "customer"), ("Current phase", "phase"), ("Health", "health"), ("Confidence", "confidence")):
        value = _text(program.get(field))
        if value:
            facts.append(f"{label}: {value}.")
    return f"{description} {' '.join(facts)}".strip()


def _descriptions(items):
    result = []
    for item in items if isinstance(items, list) else []:
        value = _text(item)
        if not value and isinstance(item, dict):
            for field in ("description", "action", "title", "name", "issue", "risk"):
                value = _text(item.get(field))
                if value:
                    break
        if value and value not in result:
            result.append(value[:500])
        if len(result) == PROGRAM_LIST_LIMIT:
            break
    return result


def _has_value(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, list):
        return any(_has_value(item) for item in value)
    if isinstance(value, dict):
        return any(_has_value(item) for item in value.values())
    return False


def _bounded_value(value):
    if isinstance(value, (str, int, float, bool)):
        return _bounded_text(value)
    if isinstance(value, list):
        return [_bounded_value(item) for item in value[:PROGRAM_LIST_LIMIT]]
    if isinstance(value, dict):
        return {str(key)[:100]: _bounded_value(item) for key, item in list(value.items())[:PROGRAM_LIST_LIMIT]}
    return None


def _bounded_text(value):
    return _text(value)[:PROGRAM_TEXT_LIMIT]


def _text(value):
    return value.strip() if isinstance(value, str) else str(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else ""


def _confidence(value):
    return value if value in ("High", "Medium", "Low") else "Medium"
