ROUTING_VERSION = "1.0.0"

TECHNICAL_PROGRAM_MANAGER = "technical_program_manager"
CLOUD_ARCHITECT = "cloud_architect"
INCIDENT_COMMANDER = "incident_commander"
EXECUTIVE_ADVISOR = "executive_advisor"
DELIVERY_MANAGER = "delivery_manager"
OPERATIONS_MANAGER = "operations_manager"
CHANGE_MANAGER = "change_manager"
SECURITY_ADVISOR = "security_advisor"
CUSTOMER_SUCCESS_ADVISOR = "customer_success_advisor"

PERSONA_REGISTRY = {
    TECHNICAL_PROGRAM_MANAGER: "Technical Program Manager",
    CLOUD_ARCHITECT: "Cloud Architect",
    INCIDENT_COMMANDER: "Incident Commander",
    EXECUTIVE_ADVISOR: "Executive Advisor",
    DELIVERY_MANAGER: "Delivery Manager",
    OPERATIONS_MANAGER: "Operations Manager",
    CHANGE_MANAGER: "Change Manager",
    SECURITY_ADVISOR: "Security Advisor",
    CUSTOMER_SUCCESS_ADVISOR: "Customer Success Advisor",
}

SUPPORTING_PERSONA_ORDER = (
    TECHNICAL_PROGRAM_MANAGER,
    OPERATIONS_MANAGER,
    CLOUD_ARCHITECT,
    EXECUTIVE_ADVISOR,
    SECURITY_ADVISOR,
    CHANGE_MANAGER,
    CUSTOMER_SUCCESS_ADVISOR,
    DELIVERY_MANAGER,
)

NEW_PROGRAM_TERMS = (
    "new program",
    "start a new program",
    "program initiation",
    "initiation",
    "project charter",
)

CLOUD_TERMS = (
    "cloud",
    "migration",
    "migrate",
    "infrastructure",
    "architecture",
    "architect",
    "aws",
    "azure",
    "gcp",
    "kubernetes",
    "data center",
    "datacenter",
)

INCIDENT_TERMS = (
    "major incident",
    "incident mode",
    "incident",
    "outage",
    "severity",
    "sev",
    "service disruption",
    "p0",
    "p1",
)

ACTIVE_INCIDENT_TERMS = (
    "active incident",
    "active outage",
    "current outage",
    "current production disruption",
    "production is down",
    "severity event",
    "war room",
)

EXECUTIVE_TERMS = (
    "executive review",
    "executive reporting",
    "executive report",
    "executive",
    "steering committee",
    "steerco",
    "board",
    "sponsor update",
)

READINESS_TERMS = (
    "operational readiness",
    "production readiness",
    "go-live readiness",
    "go live readiness",
    "go-live",
    "go live",
    "handoff",
    "orr",
    "readiness review",
    "service transition",
    "hypercare",
)

SECURITY_TERMS = (
    "security",
    "compliance",
    "privacy",
    "audit",
    "sox",
    "gdpr",
    "vulnerability",
    "data protection",
)

CHANGE_TERMS = (
    "adoption",
    "training",
    "communications",
    "communication",
    "organizational change",
    "organisation change",
    "org change",
    "change management",
    "enablement",
)

CUSTOMER_SUCCESS_TERMS = (
    "customer satisfaction",
    "customer escalation",
    "customer adoption",
    "adoption outcome",
    "retention",
    "renewal",
    "churn",
    "csat",
    "nps",
)

DELIVERY_TERMS = (
    "delivery execution",
    "schedule pressure",
    "milestone slippage",
    "slippage",
    "dependency coordination",
    "dependency",
    "dependencies",
    "critical path",
    "delay",
    "delayed",
    "blocker",
)


def route_personas(program_context=None, requested_mode=None, workflow=None, user_request=None):
    """Return deterministic persona routing for structured program context.

    The router is intentionally rule-based and side-effect free. It accepts
    partial current or legacy program dictionaries, optional workflow hints,
    and free-text request context without requiring an AI provider.
    """
    text = _context_text(program_context, requested_mode, workflow, user_request)

    new_program = _contains_any(text, NEW_PROGRAM_TERMS)
    cloud = _contains_any(text, CLOUD_TERMS)
    incident = _contains_any(text, INCIDENT_TERMS)
    sow_program_initiation = (
        str(requested_mode or "").lower() == "start new program"
        and str(workflow or "").lower() == "sow_program_initiation"
    )
    if sow_program_initiation:
        incident = _contains_any(str(user_request or "").lower(), ACTIVE_INCIDENT_TERMS)
    executive = _contains_any(text, EXECUTIVE_TERMS)
    readiness = _contains_any(text, READINESS_TERMS)
    security = _contains_any(text, SECURITY_TERMS)
    change = _contains_any(text, CHANGE_TERMS)
    customer_success = _contains_any(text, CUSTOMER_SUCCESS_TERMS)
    delivery = _contains_any(text, DELIVERY_TERMS)

    primary_persona = TECHNICAL_PROGRAM_MANAGER
    supporting_personas = []
    reasons = []

    if incident:
        primary_persona = INCIDENT_COMMANDER
        _add_reason(
            reasons,
            "Major incident, outage, severity, or service disruption context routed the primary persona to Incident Commander.",
        )
        _add_supporting(supporting_personas, TECHNICAL_PROGRAM_MANAGER)
        _add_supporting(supporting_personas, OPERATIONS_MANAGER)
    elif executive:
        primary_persona = EXECUTIVE_ADVISOR
        _add_reason(
            reasons,
            "Executive review or executive reporting context routed the primary persona to Executive Advisor.",
        )
        _add_supporting(supporting_personas, TECHNICAL_PROGRAM_MANAGER)
    elif readiness:
        primary_persona = OPERATIONS_MANAGER
        _add_reason(
            reasons,
            "Operational readiness, production readiness, go-live readiness, or handoff context routed the primary persona to Operations Manager.",
        )
        _add_supporting(supporting_personas, TECHNICAL_PROGRAM_MANAGER)
    elif new_program:
        _add_reason(
            reasons,
            "New program or program initiation context keeps Technical Program Manager as the primary persona.",
        )
    else:
        _add_reason(
            reasons,
            "No specialized primary routing signal was detected, so Technical Program Manager is the default primary persona.",
        )

    if cloud:
        _add_supporting(supporting_personas, CLOUD_ARCHITECT)
        _add_reason(
            reasons,
            "Cloud, migration, infrastructure, or architecture context added Cloud Architect as a supporting persona.",
        )

    if executive and primary_persona != EXECUTIVE_ADVISOR:
        _add_supporting(supporting_personas, EXECUTIVE_ADVISOR)
        _add_reason(
            reasons,
            "Executive review or reporting context added Executive Advisor as a supporting persona.",
        )

    if readiness and primary_persona != OPERATIONS_MANAGER:
        _add_supporting(supporting_personas, OPERATIONS_MANAGER)
        _add_reason(
            reasons,
            "Operational readiness, production readiness, go-live readiness, or handoff context added Operations Manager as a supporting persona.",
        )

    if security:
        _add_supporting(supporting_personas, SECURITY_ADVISOR)
        _add_reason(
            reasons,
            "Security, compliance, privacy, or security-related risk context added Security Advisor as a supporting persona.",
        )

    if change:
        _add_supporting(supporting_personas, CHANGE_MANAGER)
        _add_reason(
            reasons,
            "Adoption, training, communications, or organizational change context added Change Manager as a supporting persona.",
        )

    if customer_success:
        _add_supporting(supporting_personas, CUSTOMER_SUCCESS_ADVISOR)
        _add_reason(
            reasons,
            "Customer satisfaction, customer escalation, retention, or adoption outcome context added Customer Success Advisor as a supporting persona.",
        )

    if delivery:
        _add_supporting(supporting_personas, DELIVERY_MANAGER)
        _add_reason(
            reasons,
            "Delivery execution, schedule pressure, milestone slippage, or dependency coordination context added Delivery Manager as a supporting persona.",
        )

    supporting_personas = _ordered_supporting_personas(
        supporting_personas,
        primary_persona,
    )

    return {
        "primary_persona": primary_persona,
        "supporting_personas": supporting_personas,
        "reasons": reasons,
        "routing_version": ROUTING_VERSION,
    }


def _context_text(program_context, requested_mode, workflow, user_request):
    values = []
    for value in (requested_mode, workflow, user_request, program_context):
        _collect_text_values(value, values)
    return " ".join(values).lower()


def _collect_text_values(value, values):
    if value is None:
        return

    if isinstance(value, str):
        if value.strip():
            values.append(value.strip())
        return

    if isinstance(value, dict):
        for key in sorted(value.keys()):
            _collect_text_values(value.get(key), values)
        return

    if isinstance(value, (list, tuple)):
        for item in value:
            _collect_text_values(item, values)
        return

    if isinstance(value, (bool, int, float)):
        values.append(str(value))


def _contains_any(text, terms):
    return any(term in text for term in terms)


def _add_supporting(supporting_personas, persona_id):
    if persona_id not in supporting_personas:
        supporting_personas.append(persona_id)


def _add_reason(reasons, reason):
    if reason not in reasons:
        reasons.append(reason)


def _ordered_supporting_personas(supporting_personas, primary_persona):
    order = {persona_id: index for index, persona_id in enumerate(SUPPORTING_PERSONA_ORDER)}
    unique = []

    for persona_id in supporting_personas:
        if persona_id == primary_persona:
            continue
        if persona_id not in unique:
            unique.append(persona_id)

    return sorted(unique, key=lambda persona_id: order.get(persona_id, len(order)))
