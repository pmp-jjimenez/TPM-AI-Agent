"""Immutable, renderer-independent Executive Status Report truth model.

The builder consumes the same compatibility-normalized Program representation used
by persistence and API boundaries.  It classifies source facts, deterministic
derivations, recommendations, and missing information without producing presentation
or format-specific objects.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Union

from schema import apply_compatibility_defaults


EXECUTIVE_REPORT_CONTRACT_VERSION = "1.0"
ACTIVE_STATUS_POLICY_VERSION = "1.0"
ORDERING_POLICY_VERSION = "1.0"
RECOMMENDATION_POLICY_VERSION = "1.0"

NO_RECOMMENDATION_TEXT = (
    "No evidence-backed executive action is available from the recorded program data."
)


class ExecutiveReportInputError(ValueError):
    """Raised when report inputs cannot be represented safely."""


class ValueClassification(str, Enum):
    STORED_FACT = "stored_fact"
    DETERMINISTIC_VALUE = "deterministic_value"
    RECOMMENDATION = "recommendation"
    MISSING_VALUE = "missing_value"


class RecordKind(str, Enum):
    RISK = "risk"
    ISSUE = "issue"
    DEPENDENCY = "dependency"
    DECISION = "decision"
    ACTION = "action"


class NoticeImportance(str, Enum):
    INFORMATION = "information"
    ATTENTION = "attention"


class RecommendationCategory(str, Enum):
    BLOCKED_ISSUE = "blocked_issue"
    HIGH_RISK = "high_risk"
    BLOCKING_DECISION = "blocking_decision"
    PRIORITY_ACTION = "priority_action"
    IMPACTING_DEPENDENCY = "impacting_dependency"
    NO_EVIDENCE_BACKED_ACTION = "no_evidence_backed_action"


@dataclass(frozen=True)
class SourceReference:
    path: str
    source_id: Optional[str] = None


@dataclass(frozen=True)
class StoredFact:
    value: Any
    sources: tuple[SourceReference, ...]
    classification: ValueClassification = ValueClassification.STORED_FACT


@dataclass(frozen=True)
class DeterministicValue:
    value: Any
    definition: str
    rule_id: str
    sources: tuple[SourceReference, ...]
    classification: ValueClassification = ValueClassification.DETERMINISTIC_VALUE


@dataclass(frozen=True)
class MissingValue:
    reason: str
    sources: tuple[SourceReference, ...] = ()
    classification: ValueClassification = ValueClassification.MISSING_VALUE


ReportValue = Union[StoredFact, DeterministicValue, MissingValue]


@dataclass(frozen=True)
class ReportMetadataInput:
    report_date: date
    generated_at: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    report_id: Optional[str] = None


@dataclass(frozen=True)
class ReportMetadata:
    report_date: DeterministicValue
    generated_at: ReportValue
    locale: ReportValue
    timezone: ReportValue
    report_id: ReportValue
    source_program_id: ReportValue
    source_program_updated_at: ReportValue


@dataclass(frozen=True)
class ProgramIdentity:
    program_id: ReportValue
    program_name: ReportValue
    customer: ReportValue
    description: ReportValue


@dataclass(frozen=True)
class ReportedStatus:
    phase: ReportValue
    health: ReportValue
    confidence: ReportValue


@dataclass(frozen=True)
class ReportRecord:
    source_id: ReportValue
    kind: RecordKind
    title: ReportValue
    description: ReportValue
    status: ReportValue
    priority: ReportValue
    severity: ReportValue
    owner: ReportValue
    due_date: ReportValue
    impact: ReportValue
    response: ReportValue
    created_at: ReportValue
    updated_at: ReportValue
    active: DeterministicValue
    overdue: DeterministicValue
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class RecordCount:
    kind: RecordKind
    total: DeterministicValue
    active: DeterministicValue
    blocked: DeterministicValue
    overdue: DeterministicValue


@dataclass(frozen=True)
class CompletenessNotice:
    code: str
    message: str
    importance: NoticeImportance
    affected_fields: tuple[str, ...] = ()
    affected_record_ids: tuple[str, ...] = ()
    sources: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class Recommendation:
    statement: str
    rationale: str
    category: RecommendationCategory
    evidence_source_ids: tuple[str, ...]
    evidence_references: tuple[SourceReference, ...]
    policy_rule_id: str
    classification: ValueClassification = ValueClassification.RECOMMENDATION


@dataclass(frozen=True)
class CompletenessAssessment:
    notices: tuple[CompletenessNotice, ...]


@dataclass(frozen=True)
class ExecutiveReportViewModel:
    contract_version: str
    report_metadata: ReportMetadata
    program_identity: ProgramIdentity
    reported_status: ReportedStatus
    executive_summary: ReportValue
    record_counts: tuple[RecordCount, ...]
    risks: tuple[ReportRecord, ...]
    issues: tuple[ReportRecord, ...]
    dependencies: tuple[ReportRecord, ...]
    decisions: tuple[ReportRecord, ...]
    actions: tuple[ReportRecord, ...]
    primary_recommendation: Recommendation
    completeness: CompletenessAssessment


_ACTIVE_STATUSES = {
    RecordKind.RISK: frozenset({"open", "monitoring", "mitigating", "accepted"}),
    RecordKind.ISSUE: frozenset({"open", "in_progress", "blocked"}),
    RecordKind.DEPENDENCY: frozenset({"open", "in_progress"}),
    RecordKind.DECISION: frozenset({"proposed"}),
    RecordKind.ACTION: frozenset({"open", "in_progress", "blocked"}),
}
_CLOSED_STATUSES = {
    RecordKind.RISK: frozenset({"closed"}),
    RecordKind.ISSUE: frozenset({"resolved", "closed"}),
    RecordKind.DEPENDENCY: frozenset({"resolved", "closed"}),
    RecordKind.DECISION: frozenset({"approved", "superseded", "rejected"}),
    RecordKind.ACTION: frozenset({"completed", "cancelled"}),
}
_IMPORTANCE_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def build_executive_report_view_model(
    program: dict[str, Any],
    *,
    report_metadata: ReportMetadataInput,
) -> ExecutiveReportViewModel:
    """Build an immutable report contract without mutating or persisting Program data."""
    if not isinstance(program, dict):
        raise ExecutiveReportInputError("program must be a mapping")
    if not isinstance(report_metadata, ReportMetadataInput):
        raise ExecutiveReportInputError("report_metadata must be ReportMetadataInput")
    if (
        not isinstance(report_metadata.report_date, date)
        or isinstance(report_metadata.report_date, datetime)
    ):
        raise ExecutiveReportInputError("report_metadata.report_date must be a date")

    try:
        normalized = apply_compatibility_defaults(program)
    except (TypeError, ValueError) as error:
        raise ExecutiveReportInputError("Program data failed canonical normalization") from error

    identity = ProgramIdentity(
        program_id=_fact_or_missing(program, "program_id"),
        program_name=_fact_or_missing(program, "program_name"),
        customer=_fact_or_missing(program, "customer"),
        description=_fact_or_missing(program, "description"),
    )
    status = ReportedStatus(
        phase=_fact_or_missing(program, "phase"),
        health=_fact_or_missing(program, "health"),
        confidence=_fact_or_missing(program, "confidence"),
    )
    metadata = _build_metadata(program, report_metadata)

    risks = _build_records(
        normalized["risks"], _original_records(program, "risks"),
        RecordKind.RISK, report_metadata.report_date,
    )
    issues = _build_records(
        normalized["issues"], _original_records(program, "issues"),
        RecordKind.ISSUE, report_metadata.report_date,
    )
    dependencies = _build_records(
        normalized["dependencies"], _original_records(program, "dependencies"),
        RecordKind.DEPENDENCY, report_metadata.report_date,
    )
    decisions = _build_records(
        normalized["decisions"], _original_records(program, "decisions"),
        RecordKind.DECISION, report_metadata.report_date,
    )
    actions = _build_records(
        normalized["next_actions"], _original_records(program, "next_actions"),
        RecordKind.ACTION, report_metadata.report_date,
    )
    collections = (risks, issues, dependencies, decisions, actions)

    summary = MissingValue(
        "The canonical Program schema has no approved executive summary field.",
        (SourceReference("/executive_summary"),),
    )
    recommendation = _recommend(issues, risks, decisions, actions, dependencies)
    completeness = _assess_completeness(identity, status, summary, collections, recommendation)

    return ExecutiveReportViewModel(
        contract_version=EXECUTIVE_REPORT_CONTRACT_VERSION,
        report_metadata=metadata,
        program_identity=identity,
        reported_status=status,
        executive_summary=summary,
        record_counts=tuple(
            _count_records(kind, records)
            for kind, records in zip(RecordKind, collections)
        ),
        risks=risks,
        issues=issues,
        dependencies=dependencies,
        decisions=decisions,
        actions=actions,
        primary_recommendation=recommendation,
        completeness=completeness,
    )


def _build_metadata(program: dict[str, Any], supplied: ReportMetadataInput) -> ReportMetadata:
    metadata = program.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    program_id = _fact_or_missing(program, "program_id")
    return ReportMetadata(
        report_date=DeterministicValue(
            supplied.report_date.isoformat(),
            "Effective date supplied by the report caller.",
            "metadata.report_date.input.v1",
            (),
        ),
        generated_at=_input_or_missing(supplied.generated_at, "generated_at"),
        locale=_input_or_missing(supplied.locale, "locale"),
        timezone=_input_or_missing(supplied.timezone, "timezone"),
        report_id=_input_or_missing(supplied.report_id, "report_id"),
        source_program_id=program_id,
        source_program_updated_at=_fact_or_missing(
            metadata, "updated_at", prefix="/metadata"
        ),
    )


def _input_or_missing(value: Optional[str], field: str) -> ReportValue:
    if isinstance(value, str) and value.strip():
        reference = SourceReference(f"$input/{field}")
        return DeterministicValue(
            value.strip(),
            f"{field.replace('_', ' ').capitalize()} supplied by the report caller.",
            f"metadata.{field}.input.v1",
            (reference,),
        )
    return MissingValue(f"No {field.replace('_', ' ')} was supplied.")


def _fact_or_missing(
    source: dict[str, Any], field: str, *, prefix: str = ""
) -> ReportValue:
    reference = SourceReference(f"{prefix}/{field}")
    value = source.get(field)
    if isinstance(value, str) and value.strip():
        return StoredFact(value.strip(), (reference,))
    return MissingValue(f"No recorded {field.replace('_', ' ')} is available.", (reference,))


def _build_records(
    records: list[dict[str, Any]],
    originals: list[Any],
    kind: RecordKind,
    report_date: date,
) -> tuple[ReportRecord, ...]:
    built = tuple(
        _build_record(record, originals[index], kind, index, report_date)
        for index, record in enumerate(records)
    )
    return tuple(sorted(built, key=_record_sort_key))


def _build_record(
    record: dict[str, Any],
    original: Any,
    kind: RecordKind,
    index: int,
    report_date: date,
) -> ReportRecord:
    collection = "next_actions" if kind is RecordKind.ACTION else f"{kind.value}s"
    path = f"/{collection}/{index}"
    source_id = str(record["object_id"])
    root = SourceReference(path, source_id)
    status = str(record["status"])
    due_field = {
        RecordKind.RISK: "review_date",
        RecordKind.ISSUE: "due_date",
        RecordKind.DEPENDENCY: "required_by_date",
        RecordKind.DECISION: "review_date",
        RecordKind.ACTION: "due_date",
    }[kind]
    priority_field = "priority" if kind in {RecordKind.RISK, RecordKind.ACTION} else None
    severity_field = "severity" if kind is RecordKind.ISSUE else None
    impact_field = "impact" if kind in {
        RecordKind.RISK, RecordKind.ISSUE, RecordKind.DEPENDENCY, RecordKind.DECISION
    } else None
    response_field = {
        RecordKind.RISK: "mitigation_plan",
        RecordKind.ISSUE: "resolution_summary",
        RecordKind.DEPENDENCY: "mitigation_plan",
        RecordKind.DECISION: "rationale",
        RecordKind.ACTION: "completion_summary",
    }[kind]
    due = record.get(due_field)
    overdue = bool(
        due
        and date.fromisoformat(due) < report_date
        and status not in _CLOSED_STATUSES[kind]
    )
    audit = record.get("audit") or {}
    owner = record.get("owner")
    owner_name = owner.get("display_name") if isinstance(owner, dict) else None
    sources = (root,)
    source_id_value = _normalized_fact(
        record["object_id"], original, "object_id", path,
        "Compatibility normalization produced the canonical source ID.",
        f"normalize.{kind.value}.source_id.v1",
    )
    title_value = _normalized_fact(
        str(record["title"]).strip(), original, "title", path,
        "Compatibility normalization produced the canonical record title.",
        f"normalize.{kind.value}.title.v1",
        string_is_value=True,
    )
    status_value = _normalized_fact(
        status, original, "status", path,
        "Compatibility normalization produced the canonical record status.",
        f"normalize.{kind.value}.status.v1",
    )
    priority_aliases = ("severity",) if kind is RecordKind.RISK else ()
    due_aliases = ("due_date",) if kind is RecordKind.RISK else ()
    response_aliases = ("resolution",) if kind is RecordKind.ISSUE else ()
    return ReportRecord(
        source_id=source_id_value,
        kind=kind,
        title=title_value,
        description=_normalized_optional(
            record.get("description"), original, "description", path
        ),
        status=status_value,
        priority=_normalized_optional(
            record.get(priority_field) if priority_field else None,
            original,
            priority_field or "priority",
            path,
            aliases=priority_aliases,
        ),
        severity=_normalized_optional(
            record.get(severity_field) if severity_field else None,
            original,
            severity_field or "severity",
            path,
        ),
        owner=_normalized_owner(owner_name, original, path),
        due_date=_normalized_optional(
            due, original, due_field, path, aliases=due_aliases
        ),
        impact=_normalized_optional(
            record.get(impact_field) if impact_field else None,
            original,
            impact_field or "impact",
            path,
        ),
        response=_normalized_optional(
            record.get(response_field), original, response_field, path,
            aliases=response_aliases,
        ),
        created_at=_normalized_audit_value(
            audit.get("created_at"), original, "created_at", path
        ),
        updated_at=_normalized_audit_value(
            audit.get("updated_at"), original, "updated_at", path
        ),
        active=DeterministicValue(
            status in _ACTIVE_STATUSES[kind],
            f"{kind.value} is active only when status is one of "
            f"{', '.join(sorted(_ACTIVE_STATUSES[kind]))}.",
            f"active_status.{kind.value}.{ACTIVE_STATUS_POLICY_VERSION}",
            (SourceReference(f"{path}/status", source_id),),
        ),
        overdue=DeterministicValue(
            overdue,
            "Due date precedes the supplied report date and status is not complete or closed.",
            f"overdue.{kind.value}.v1",
            (SourceReference(f"{path}/{due_field}", source_id),),
        ),
        sources=sources,
    )


def _record_value(value: Any, path: str, field: str) -> ReportValue:
    reference = SourceReference(f"{path}/{field}")
    if isinstance(value, str) and value.strip():
        return StoredFact(value.strip(), (reference,))
    return MissingValue(f"No recorded {field.replace('/', ' ')} is available.", (reference,))


def _normalized_optional(
    value: Any,
    original: Any,
    field: str,
    path: str,
    *,
    aliases: tuple[str, ...] = (),
) -> ReportValue:
    if not isinstance(value, str) or not value.strip():
        return _record_value(None, path, field)
    normalized_value = value.strip()
    if isinstance(original, dict):
        original_value = original.get(field)
        if isinstance(original_value, str) and original_value.strip() == normalized_value:
            return StoredFact(
                normalized_value, (SourceReference(f"{path}/{field}"),)
            )
        for alias in aliases:
            alias_value = original.get(alias)
            if isinstance(alias_value, str) and alias_value.strip() == normalized_value:
                return DeterministicValue(
                    normalized_value,
                    f"Compatibility normalization mapped {alias} to {field}.",
                    f"normalize.record.{alias}_to_{field}.v1",
                    (SourceReference(f"{path}/{alias}"),),
                )
    return DeterministicValue(
        normalized_value,
        f"Compatibility normalization produced canonical {field}.",
        f"normalize.record.{field}.v1",
        (SourceReference(path),),
    )


def _normalized_owner(value: Optional[str], original: Any, path: str) -> ReportValue:
    if not value:
        return _record_value(None, path, "owner")
    if isinstance(original, dict):
        owner = original.get("owner")
        if isinstance(owner, str) and owner.strip() == value:
            return StoredFact(value, (SourceReference(f"{path}/owner"),))
        if (
            isinstance(owner, dict)
            and isinstance(owner.get("display_name"), str)
            and owner["display_name"].strip() == value
        ):
            return StoredFact(
                value, (SourceReference(f"{path}/owner/display_name"),)
            )
    return DeterministicValue(
        value,
        "Compatibility normalization produced the canonical owner display name.",
        "normalize.record.owner.v1",
        (SourceReference(path),),
    )


def _normalized_audit_value(
    value: Any, original: Any, field: str, path: str
) -> ReportValue:
    if not isinstance(value, str) or not value.strip():
        return _record_value(None, path, f"audit/{field}")
    audit = original.get("audit") if isinstance(original, dict) else None
    if (
        isinstance(audit, dict)
        and isinstance(audit.get(field), str)
        and audit[field].strip() == value.strip()
    ):
        return StoredFact(
            value.strip(), (SourceReference(f"{path}/audit/{field}"),)
        )
    return DeterministicValue(
        value.strip(),
        f"Compatibility normalization produced canonical audit {field}.",
        f"normalize.record.audit_{field}.v1",
        (SourceReference(path),),
    )


def _original_records(program: dict[str, Any], field: str) -> list[Any]:
    value = program.get(field)
    return value if isinstance(value, list) else []


def _normalized_fact(
    value: str,
    original: Any,
    field: str,
    path: str,
    definition: str,
    rule_id: str,
    *,
    string_is_value: bool = False,
) -> ReportValue:
    if isinstance(original, dict):
        original_value = original.get(field)
        if isinstance(original_value, str) and original_value.strip() == value:
            return StoredFact(value, (SourceReference(f"{path}/{field}", value if field == "object_id" else None),))
    elif string_is_value and isinstance(original, str) and original.strip() == value:
        return StoredFact(value, (SourceReference(path),))
    return DeterministicValue(
        value,
        definition,
        rule_id,
        (SourceReference(path),),
    )


def _record_sort_key(record: ReportRecord) -> tuple[Any, ...]:
    importance = _text_value(record.severity) or _text_value(record.priority)
    due = _text_value(record.due_date)
    return (
        _IMPORTANCE_RANK.get(importance, len(_IMPORTANCE_RANK)),
        0 if record.status.value == "blocked" else 1,
        0 if record.overdue.value else 1,
        0 if due else 1,
        due or "",
        record.source_id.value,
    )


def _count_records(kind: RecordKind, records: tuple[ReportRecord, ...]) -> RecordCount:
    references = tuple(reference for record in records for reference in record.sources)
    return RecordCount(
        kind=kind,
        total=DeterministicValue(
            len(records), "Number of normalized records in the source collection.",
            f"count.{kind.value}.total.v1", references,
        ),
        active=DeterministicValue(
            sum(record.active.value for record in records),
            "Number of records matching the active-status policy.",
            f"count.{kind.value}.active.{ACTIVE_STATUS_POLICY_VERSION}", references,
        ),
        blocked=DeterministicValue(
            sum(record.status.value == "blocked" for record in records),
            "Number of records with canonical blocked status.",
            f"count.{kind.value}.blocked.v1", references,
        ),
        overdue=DeterministicValue(
            sum(record.overdue.value for record in records),
            "Number of records matching the overdue rule.",
            f"count.{kind.value}.overdue.v1", references,
        ),
    )


def _recommend(
    issues: tuple[ReportRecord, ...],
    risks: tuple[ReportRecord, ...],
    decisions: tuple[ReportRecord, ...],
    actions: tuple[ReportRecord, ...],
    dependencies: tuple[ReportRecord, ...],
) -> Recommendation:
    blocked_issues = tuple(item for item in issues if item.status.value == "blocked")
    if blocked_issues:
        selected = blocked_issues[0]
        return _recommendation(
            selected, RecommendationCategory.BLOCKED_ISSUE,
            f"Escalate blocked issue {selected.source_id.value} to the accountable owner "
            "and confirm a recovery decision.",
            "The issue has an explicitly recorded blocked status.",
            "recommendation.1.blocked_issue",
            (selected.status,),
        )
    severe_risks = tuple(
        item for item in risks
        if item.active.value
        and (_text_value(item.severity) or _text_value(item.priority)) in {"critical", "high"}
    )
    if severe_risks:
        selected = severe_risks[0]
        level = _text_value(selected.priority)
        return _recommendation(
            selected, RecommendationCategory.HIGH_RISK,
            f"Review active {level}-priority risk {selected.source_id.value} and confirm "
            "the recorded mitigation owner and review date.",
            f"The risk is active with explicitly recorded {level} priority.",
            "recommendation.2.active_high_risk",
            (selected.status, selected.priority),
        )
    # The canonical DecisionRecord has no blocking field and BLOCKS relationships do
    # not permit decisions, so rule 3 cannot qualify in contract 1.0.
    priority_actions = tuple(
        item for item in actions
        if (_text_value(item.priority) in {"critical", "high"})
        and (item.status.value == "blocked" or item.overdue.value)
    )
    if priority_actions:
        selected = priority_actions[0]
        qualifier = "blocked" if selected.status.value == "blocked" else "overdue"
        return _recommendation(
            selected, RecommendationCategory.PRIORITY_ACTION,
            f"Address {qualifier} priority action {selected.source_id.value} and confirm "
            "a revised accountable date.",
            f"The action has explicit high or critical priority and is {qualifier}.",
            "recommendation.4.priority_action",
            (selected.status, selected.priority, selected.due_date),
        )
    impacting_dependencies = tuple(
        item for item in dependencies if item.active.value and not isinstance(item.impact, MissingValue)
    )
    if impacting_dependencies:
        selected = impacting_dependencies[0]
        return _recommendation(
            selected, RecommendationCategory.IMPACTING_DEPENDENCY,
            f"Review dependency {selected.source_id.value} because the record contains "
            "an explicit delivery impact.",
            "The dependency is active and contains an explicitly recorded impact.",
            "recommendation.5.impacting_dependency",
            (selected.status, selected.impact),
        )
    references = tuple(
        reference
        for collection in (issues, risks, decisions, actions, dependencies)
        for record in collection
        for reference in record.sources
    )
    return Recommendation(
        NO_RECOMMENDATION_TEXT,
        "No normalized record qualifies under the deterministic recommendation policy.",
        RecommendationCategory.NO_EVIDENCE_BACKED_ACTION,
        (),
        references,
        "recommendation.6.no_evidence",
    )


def _recommendation(
    record: ReportRecord,
    category: RecommendationCategory,
    statement: str,
    rationale: str,
    rule_id: str,
    evidence_values: tuple[ReportValue, ...],
) -> Recommendation:
    references = tuple(
        reference for value in evidence_values for reference in value.sources
    )
    return Recommendation(
        statement, rationale, category, (record.source_id.value,), references, rule_id
    )


def _assess_completeness(
    identity: ProgramIdentity,
    status: ReportedStatus,
    summary: ReportValue,
    collections: tuple[tuple[ReportRecord, ...], ...],
    recommendation: Recommendation,
) -> CompletenessAssessment:
    notices: list[CompletenessNotice] = []
    checked = (
        ("MISSING_PROGRAM_NAME", "No program name is recorded.", "program_name", identity.program_name),
        ("MISSING_CUSTOMER", "No customer is recorded.", "customer", identity.customer),
        ("MISSING_DESCRIPTION", "No program description is recorded.", "description", identity.description),
        ("MISSING_PHASE", "No reported program phase is recorded.", "phase", status.phase),
        ("MISSING_HEALTH", "No reported program health is recorded.", "health", status.health),
        ("MISSING_CONFIDENCE", "No reported confidence is recorded.", "confidence", status.confidence),
        (
            "MISSING_EXECUTIVE_SUMMARY",
            "The canonical Program schema has no approved executive summary field.",
            "executive_summary",
            summary,
        ),
    )
    for code, message, field, value in checked:
        if isinstance(value, MissingValue):
            notices.append(
                CompletenessNotice(code, message, NoticeImportance.ATTENTION, (field,), sources=value.sources)
            )

    all_records = tuple(record for collection in collections for record in collection)
    missing_owner_ids = tuple(
        record.source_id.value for record in all_records if isinstance(record.owner, MissingValue)
    )
    if missing_owner_ids:
        notices.append(CompletenessNotice(
            "MISSING_RECORD_OWNERS",
            "One or more report records have no recorded owner.",
            NoticeImportance.ATTENTION,
            affected_record_ids=missing_owner_ids,
        ))
    missing_response_ids = tuple(
        record.source_id.value
        for record in (*collections[0], *collections[2])
        if record.active.value and isinstance(record.response, MissingValue)
    )
    if missing_response_ids:
        notices.append(CompletenessNotice(
            "MISSING_ACTIVE_RESPONSE",
            "One or more active risks or dependencies have no recorded response.",
            NoticeImportance.ATTENTION,
            affected_record_ids=missing_response_ids,
        ))
    notices.append(CompletenessNotice(
        "DEPENDENCY_CRITICALITY_UNAVAILABLE",
        "Dependency criticality is not represented by the current Program schema.",
        NoticeImportance.INFORMATION,
        affected_fields=("dependencies.criticality",),
    ))
    notices.append(CompletenessNotice(
        "DECISION_BLOCKER_EVIDENCE_UNAVAILABLE",
        "The current Program schema cannot explicitly classify a proposed decision as blocking work.",
        NoticeImportance.INFORMATION,
        affected_fields=("decisions.blocking",),
    ))
    if recommendation.category is RecommendationCategory.NO_EVIDENCE_BACKED_ACTION:
        notices.append(CompletenessNotice(
            "NO_RECOMMENDATION_EVIDENCE",
            "No record qualifies for an evidence-backed executive action.",
            NoticeImportance.INFORMATION,
        ))
    return CompletenessAssessment(tuple(notices))


def _text_value(value: ReportValue) -> Optional[str]:
    return value.value if isinstance(value, (StoredFact, DeterministicValue)) else None
