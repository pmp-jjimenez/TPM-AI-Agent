from copy import deepcopy
from datetime import datetime, timezone

from context_loader import load_core_context
from intelligence_analysis import (
    IntelligenceAnalysisError,
    finalize_intelligence_analysis,
    parse_intelligence_analysis,
)
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
        bounded, evidence_catalog = extract_intelligence_evidence(snapshot)
        try:
            prompt = build_workspace_intelligence_prompt(
                bounded, evidence_catalog, load_core_context(), routing
            )
            analysis = parse_intelligence_analysis(self.provider(prompt), evidence_catalog)
            return {
                "program_id": _text(snapshot.get("program_id")),
                "generated_at": generated_at,
                "source": "ai",
                "routing": transport_routing,
                **analysis,
            }
        except (ProviderExecutionError, IntelligenceAnalysisError):
            return deterministic_intelligence(
                snapshot, transport_routing, generated_at, bounded, evidence_catalog
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
        "dependenciesById": _bounded_dependencies(program.get("dependencies")),
        "governance": _bounded_value(program.get("governance")),
        "risksById": _bounded_risks(program.get("risks")),
        "issuesById": _bounded_issues(program.get("issues")),
        "next_actions": _descriptions(program.get("next_actions")),
    }


def extract_intelligence_evidence(program):
    """Return the exact prompt snapshot and its nonempty, referenceable JSON pointers."""
    snapshot = bounded_program_snapshot(program)
    catalog = []
    _collect_evidence_paths(snapshot, "", catalog)
    return snapshot, tuple(sorted(catalog))


def _collect_evidence_paths(value, path, catalog):
    if isinstance(value, dict):
        for key, item in value.items():
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            _collect_evidence_paths(item, f"{path}/{escaped}", catalog)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_evidence_paths(item, f"{path}/{index}", catalog)
    elif _has_value(value) and path:
        catalog.append(path)


def deterministic_intelligence(program, routing, generated_at, bounded=None, evidence_catalog=None):
    if bounded is None or evidence_catalog is None:
        bounded, evidence_catalog = extract_intelligence_evidence(program)
    risks = bounded["risksById"]
    issues = bounded["issuesById"]
    dependencies = bounded["dependenciesById"]
    missing = [label for label, field in COMPLETENESS_FIELDS if not _has_value(program.get(field))]
    findings = []
    recommendations = []
    decisions = []
    for object_id, risk in risks.items():
        findings.append({
            "category": "risk", "statement": risk["title"], "confidence": "High",
            "evidence_refs": [f"/risksById/{_pointer_segment(object_id)}/title"],
        })
    for object_id, issue in issues.items():
        findings.append({
            "category": "fact", "statement": f"A program issue is recorded: {issue['title']}",
            "confidence": "High", "evidence_refs": [f"/issuesById/{_pointer_segment(object_id)}/title"],
        })
    for object_id, dependency in dependencies.items():
        findings.append({
            "category": "dependency", "statement": dependency["title"],
            "confidence": "High",
            "evidence_refs": [f"/dependenciesById/{_pointer_segment(object_id)}/title"],
        })
    missing_indexes = {}
    for label, field in COMPLETENESS_FIELDS:
        if label in missing:
            missing_indexes[field] = len(findings)
            findings.append({
                "category": "missing_information",
                "statement": f"{label} is not recorded.",
                "confidence": "High", "evidence_refs": [],
            })
    if _text(program.get("phase")).lower() == "program initiation":
        phase_finding = len(findings)
        findings.append({
            "category": "fact", "statement": "The program is in Program Initiation.",
            "confidence": "High", "evidence_refs": ["/phase"],
        })
        recommendations.append({
            "priority": "High", "statement": "Conduct the Internal Technical Kickoff.",
            "rationale": "The initiation phase requires technical alignment before delivery planning.",
            "evidence_refs": ["/phase"], "related_finding_indexes": [phase_finding],
        })
    if missing:
        recommendations.append({
            "priority": "Medium",
            "statement": "Collect executive program information: " + ", ".join(missing) + ".",
            "rationale": "Completing the program record will improve decision support and confidence.",
            "evidence_refs": [],
            "related_finding_indexes": [missing_indexes[field] for _label, field in COMPLETENESS_FIELDS if field in missing_indexes],
        })
    if "sponsor" in missing_indexes:
        decisions.append({
            "priority": "High", "statement": "Confirm the accountable executive sponsor.",
            "reason": "Executive accountability cannot be established from the current program record.",
            "related_finding_indexes": [missing_indexes["sponsor"]],
            "related_recommendation_indexes": [len(recommendations) - 1] if missing else [],
        })
    if recommendations:
        selected = min(range(len(recommendations)), key=lambda index: _priority_rank(recommendations[index]["priority"]))
        recommendation = recommendations[selected]
        next_action = {
            "priority": recommendation["priority"],
            "statement": recommendation["statement"],
            "rationale": recommendation["rationale"],
            "related_finding_indexes": recommendation["related_finding_indexes"],
            "related_recommendation_indexes": [selected],
        }
    else:
        next_action = {
            "priority": "Low", "statement": "Review the current program state with accountable stakeholders.",
            "rationale": "No stronger deterministic action is supported by the bounded program evidence.",
            "related_finding_indexes": [], "related_recommendation_indexes": [],
        }
    summary = _deterministic_summary(program)
    analysis = finalize_intelligence_analysis({
        "summary": summary,
        "confidence": _confidence(program.get("confidence")),
        "findings": findings,
        "recommendations": recommendations,
        "decisions_required": decisions,
        "next_action": next_action,
        "limitations": [FALLBACK_LIMITATION],
    }, evidence_catalog)
    return {
        "program_id": _text(program.get("program_id")),
        "generated_at": generated_at,
        "source": "deterministic_fallback",
        "routing": routing,
        **analysis,
    }


def _priority_rank(priority):
    return {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}[priority]


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


def _bounded_risks(items):
    result = {}
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        object_id = _text(item.get("object_id"))
        title = _text(item.get("title"))
        if object_id and title:
            result[object_id] = {"title": title[:500]}
        if len(result) == PROGRAM_LIST_LIMIT:
            break
    return result


def _bounded_issues(items):
    result = {}
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        object_id = _text(item.get("object_id"))
        title = _text(item.get("title"))
        if object_id and title:
            result[object_id] = {"title": title[:500]}
        if len(result) == PROGRAM_LIST_LIMIT:
            break
    return result


def _bounded_dependencies(items):
    result = {}
    for item in items if isinstance(items, list) else []:
        if len(result) >= PROGRAM_LIST_LIMIT:
            break
        if not isinstance(item, dict):
            continue
        object_id = _text(item.get("object_id"))
        title = _text(item.get("title"))[:500]
        if object_id and title:
            result[object_id] = {"title": title}
    return result


def _pointer_segment(value):
    return str(value).replace("~", "~0").replace("/", "~1")


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
