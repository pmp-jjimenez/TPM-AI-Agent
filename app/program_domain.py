"""Framework-neutral Program Domain Model primitives.

Adopted Program entities share this domain layer. Compatibility parsing belongs here
so every application boundary receives the same canonical runtime representation.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
import json
from typing import Optional
from uuid import UUID, uuid4, uuid5


LEGACY_IMPORT_NAMESPACE = UUID("5f147496-bd9d-4cd1-b0dd-80b32f6e7a17")


class DomainValidationError(ValueError):
    """Raised when stored Program domain data cannot be represented safely."""


class LifecyclePhase(str, Enum):
    DISCOVERY = "discovery"
    INITIATION = "initiation"
    PLANNING = "planning"
    EXECUTION = "execution"
    READINESS_GO_LIVE = "readiness_go_live"
    TRANSITION_HANDOFF = "transition_handoff"
    OPERATIONS_CLOSURE = "operations_closure"


class ActionStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    OPEN = "open"
    MONITORING = "monitoring"
    MITIGATING = "mitigating"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class RiskProbability(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DependencyStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DependencyType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    TECHNICAL = "technical"
    BUSINESS = "business"


class RelationshipType(str, Enum):
    RELATES_TO = "relates_to"
    BLOCKS = "blocks"
    DEPENDS_ON = "depends_on"
    MITIGATES = "mitigates"
    RESOLVES = "resolves"
    SUPPORTS = "supports"
    RESULTS_FROM = "results_from"
    SUPERSEDES = "supersedes"
    REALIZED_AS = "realized_as"


class DomainSource(str, Enum):
    MANUAL = "manual"
    CLI = "cli"
    SOW_ANALYSIS = "sow_analysis"
    LEGACY_IMPORT = "legacy_import"
    API = "api"


@dataclass(frozen=True)
class OwnerReference:
    display_name: str
    stakeholder_id: Optional[str] = None

    def __post_init__(self):
        _required_text(self.display_name, "owner.display_name")
        if self.stakeholder_id is not None:
            _uuid(self.stakeholder_id, "owner.stakeholder_id")

    def to_dict(self):
        return {
            "display_name": self.display_name.strip(),
            "stakeholder_id": self.stakeholder_id,
        }


@dataclass(frozen=True)
class AuditMetadata:
    created_at: Optional[str]
    updated_at: Optional[str]
    source: DomainSource

    def __post_init__(self):
        _optional_datetime(self.created_at, "audit.created_at")
        _optional_datetime(self.updated_at, "audit.updated_at")

    def to_dict(self):
        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source": self.source.value,
        }


@dataclass(frozen=True)
class ProgramEntity:
    object_id: str
    object_type: str
    title: str
    description: Optional[str]
    owner: Optional[OwnerReference]
    lifecycle_phase: Optional[LifecyclePhase]
    audit: AuditMetadata

    def __post_init__(self):
        _uuid(self.object_id, "object_id")
        _required_text(self.object_type, "object_type")
        _required_text(self.title, "title")
        _optional_text(self.description, "description")

    def _base_dict(self):
        return {
            "object_id": self.object_id,
            "object_type": self.object_type,
            "title": self.title.strip(),
            "description": self.description.strip() if self.description else None,
            "owner": self.owner.to_dict() if self.owner else None,
            "lifecycle_phase": self.lifecycle_phase.value if self.lifecycle_phase else None,
            "audit": self.audit.to_dict(),
        }


@dataclass(frozen=True)
class Action(ProgramEntity):
    status: ActionStatus
    priority: Optional[ActionPriority]
    due_date: Optional[str]
    completed_at: Optional[str]
    completion_summary: Optional[str]

    def __post_init__(self):
        super().__post_init__()
        if self.object_type != "action":
            raise DomainValidationError("object_type must be 'action'")
        _optional_date(self.due_date, "due_date")
        _optional_datetime(self.completed_at, "completed_at")
        _optional_text(self.completion_summary, "completion_summary")

    def to_dict(self):
        return {
            **self._base_dict(),
            "status": self.status.value,
            "priority": self.priority.value if self.priority else None,
            "due_date": self.due_date,
            "completed_at": self.completed_at,
            "completion_summary": self.completion_summary,
        }


@dataclass(frozen=True)
class Risk(ProgramEntity):
    status: RiskStatus
    probability: Optional[RiskProbability]
    impact: Optional[RiskImpact]
    priority: Optional[RiskPriority]
    mitigation_plan: Optional[str]
    contingency_plan: Optional[str]
    review_date: Optional[str]
    acceptance_rationale: Optional[str]
    accepted_by: Optional[OwnerReference]

    def __post_init__(self):
        super().__post_init__()
        if self.object_type != "risk":
            raise DomainValidationError("object_type must be 'risk'")
        _optional_text(self.mitigation_plan, "mitigation_plan")
        _optional_text(self.contingency_plan, "contingency_plan")
        _optional_date(self.review_date, "review_date")
        _optional_text(self.acceptance_rationale, "acceptance_rationale")
        if self.status == RiskStatus.ACCEPTED:
            if self.acceptance_rationale is None:
                raise DomainValidationError("acceptance_rationale is required when status is accepted")
            if self.accepted_by is None:
                raise DomainValidationError("accepted_by is required when status is accepted")

    def to_dict(self):
        return {
            **self._base_dict(),
            "status": self.status.value,
            "probability": self.probability.value if self.probability else None,
            "impact": self.impact.value if self.impact else None,
            "priority": self.priority.value if self.priority else None,
            "mitigation_plan": self.mitigation_plan,
            "contingency_plan": self.contingency_plan,
            "review_date": self.review_date,
            "acceptance_rationale": self.acceptance_rationale,
            "accepted_by": self.accepted_by.to_dict() if self.accepted_by else None,
        }


@dataclass(frozen=True)
class Issue(ProgramEntity):
    status: IssueStatus
    severity: Optional[IssueSeverity]
    impact: Optional[str]
    due_date: Optional[str]
    resolution_summary: Optional[str]
    resolved_at: Optional[str]
    root_cause: Optional[str]

    def __post_init__(self):
        super().__post_init__()
        if self.object_type != "issue":
            raise DomainValidationError("object_type must be 'issue'")
        _optional_text(self.impact, "impact")
        _optional_date(self.due_date, "due_date")
        _optional_text(self.resolution_summary, "resolution_summary")
        _optional_utc_datetime(self.resolved_at, "resolved_at")
        _optional_text(self.root_cause, "root_cause")

    def to_dict(self):
        return {
            **self._base_dict(),
            "status": self.status.value,
            "severity": self.severity.value if self.severity else None,
            "impact": self.impact,
            "due_date": self.due_date,
            "resolution_summary": self.resolution_summary,
            "resolved_at": self.resolved_at,
            "root_cause": self.root_cause,
        }


@dataclass(frozen=True)
class Dependency(ProgramEntity):
    status: DependencyStatus
    dependency_type: DependencyType
    depends_on: Optional[str]
    external_party: Optional[str]
    required_by_date: Optional[str]
    impact: Optional[str]
    mitigation_plan: Optional[str]

    def __post_init__(self):
        super().__post_init__()
        if self.object_type != "dependency":
            raise DomainValidationError("object_type must be 'dependency'")
        _optional_text(self.depends_on, "depends_on")
        _optional_text(self.external_party, "external_party")
        _optional_date(self.required_by_date, "required_by_date")
        _optional_text(self.impact, "impact")
        _optional_text(self.mitigation_plan, "mitigation_plan")

    def to_dict(self):
        return {
            **self._base_dict(), "status": self.status.value,
            "dependency_type": self.dependency_type.value,
            "depends_on": self.depends_on, "external_party": self.external_party,
            "required_by_date": self.required_by_date, "impact": self.impact,
            "mitigation_plan": self.mitigation_plan,
        }


@dataclass(frozen=True)
class ProgramRelationship:
    relationship_id: str
    relationship_type: RelationshipType
    source_object_id: str
    target_object_id: str
    created_at: Optional[str]
    source: DomainSource

    def __post_init__(self):
        _uuid(self.relationship_id, "relationship_id")
        _uuid(self.source_object_id, "source_object_id")
        _uuid(self.target_object_id, "target_object_id")
        if self.source_object_id == self.target_object_id:
            raise DomainValidationError("relationship cannot reference the same source and target")
        _optional_datetime(self.created_at, "created_at")

    def to_dict(self):
        return {
            "relationship_id": self.relationship_id,
            "relationship_type": self.relationship_type.value,
            "source_object_id": self.source_object_id,
            "target_object_id": self.target_object_id,
            "created_at": self.created_at,
            "source": self.source.value,
        }


def utc_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_action(title, source=DomainSource.CLI, **values):
    now = utc_timestamp()
    return Action(
        object_id=str(uuid4()),
        object_type="action",
        title=title,
        description=values.get("description"),
        status=_enum(ActionStatus, values.get("status", ActionStatus.OPEN), "status"),
        priority=_optional_enum(ActionPriority, values.get("priority"), "priority"),
        owner=_owner(values.get("owner")),
        lifecycle_phase=_optional_phase(values.get("lifecycle_phase")),
        due_date=values.get("due_date"),
        completed_at=values.get("completed_at"),
        completion_summary=values.get("completion_summary"),
        audit=AuditMetadata(now, now, _enum(DomainSource, source, "audit.source")),
    )


def create_risk(title, source=DomainSource.CLI, **values):
    now = utc_timestamp()
    return Risk(
        object_id=str(uuid4()),
        object_type="risk",
        title=title,
        description=values.get("description"),
        owner=_owner(values.get("owner")),
        lifecycle_phase=_optional_phase(values.get("lifecycle_phase")),
        audit=AuditMetadata(now, now, _enum(DomainSource, source, "audit.source")),
        status=_enum(RiskStatus, values.get("status", RiskStatus.OPEN), "status"),
        probability=_optional_enum(RiskProbability, values.get("probability"), "probability"),
        impact=_optional_enum(RiskImpact, values.get("impact"), "impact"),
        priority=_optional_enum(RiskPriority, values.get("priority"), "priority"),
        mitigation_plan=values.get("mitigation_plan"),
        contingency_plan=values.get("contingency_plan"),
        review_date=values.get("review_date"),
        acceptance_rationale=values.get("acceptance_rationale"),
        accepted_by=_owner(values.get("accepted_by"), "accepted_by"),
    )


def create_issue(title, source=DomainSource.CLI, **values):
    now = utc_timestamp()
    return Issue(
        object_id=str(uuid4()), object_type="issue", title=title,
        description=values.get("description"), owner=_owner(values.get("owner")),
        lifecycle_phase=_optional_phase(values.get("lifecycle_phase")),
        audit=AuditMetadata(now, now, _enum(DomainSource, source, "audit.source")),
        status=_enum(IssueStatus, values.get("status", IssueStatus.OPEN), "status"),
        severity=_optional_enum(IssueSeverity, values.get("severity"), "severity"),
        impact=values.get("impact"), due_date=values.get("due_date"),
        resolution_summary=values.get("resolution_summary"),
        resolved_at=values.get("resolved_at"), root_cause=values.get("root_cause"),
    )


def create_dependency(title, source=DomainSource.CLI, **values):
    now = utc_timestamp()
    return Dependency(
        object_id=str(uuid4()), object_type="dependency", title=title,
        description=values.get("description"), owner=_owner(values.get("owner")),
        lifecycle_phase=_optional_phase(values.get("lifecycle_phase")),
        audit=AuditMetadata(now, now, _enum(DomainSource, source, "audit.source")),
        status=_enum(DependencyStatus, values.get("status", DependencyStatus.OPEN), "status"),
        dependency_type=_enum(DependencyType, values.get("dependency_type"), "dependency_type"),
        depends_on=values.get("depends_on"), external_party=values.get("external_party"),
        required_by_date=values.get("required_by_date"), impact=values.get("impact"),
        mitigation_plan=values.get("mitigation_plan"),
    )


def normalize_action(value, program_id, index):
    """Normalize one legacy or canonical value without mutating its source."""
    path = f"next_actions[{index}]"
    if isinstance(value, str):
        record = {"title": value}
    elif isinstance(value, dict):
        record = dict(value)
    else:
        raise DomainValidationError(f"{path} must be a string or object")

    title = _first_text(record, "title", "description", "action", "name")
    if not title:
        raise DomainValidationError(f"{path} must contain non-empty action text")

    object_id = _legacy_object_id(record, program_id, index, value)
    canonical = "object_id" in record or record.get("object_type") == "action"
    if canonical:
        _exact_fields(record, {
            "object_id", "object_type", "title", "description", "status", "priority",
            "owner", "lifecycle_phase", "due_date", "completed_at",
            "completion_summary", "audit",
        }, path)
        if record.get("object_type") != "action":
            raise DomainValidationError(f"{path}.object_type must be 'action'")

    audit_value = record.get("audit") if canonical else None
    if audit_value is None:
        audit = AuditMetadata(None, None, _legacy_source(record.get("source")))
    else:
        audit = _audit(audit_value, f"{path}.audit")

    status = _legacy_status(record.get("status", "open"), path)
    completed_at = record.get("completed_at")

    try:
        return Action(
            object_id=object_id,
            object_type="action",
            title=title,
            description=_clean_optional(record.get("description")) if canonical else None,
            status=status,
            priority=_optional_enum(ActionPriority, record.get("priority"), f"{path}.priority"),
            owner=_owner(record.get("owner"), f"{path}.owner"),
            lifecycle_phase=_optional_phase(record.get("lifecycle_phase"), f"{path}.lifecycle_phase"),
            due_date=_clean_optional(record.get("due_date")),
            completed_at=_clean_optional(completed_at),
            completion_summary=_clean_optional(record.get("completion_summary")),
            audit=audit,
        )
    except DomainValidationError as error:
        raise DomainValidationError(f"{path}: {error}") from error


def normalize_risk(value, program_id, index):
    """Normalize one legacy or canonical Risk without mutating its source."""
    path = f"risks[{index}]"
    if isinstance(value, str):
        record = {"title": value}
    elif isinstance(value, dict):
        record = dict(value)
    else:
        raise DomainValidationError(f"{path} must be a string or object")

    title = _first_text(record, "title", "description", "risk", "name")
    if not title:
        raise DomainValidationError(f"{path} must contain non-empty risk text")

    object_id = _legacy_risk_object_id(record, program_id, index, value)
    canonical = "object_id" in record or record.get("object_type") == "risk"
    if canonical:
        _exact_fields(record, {
            "object_id", "object_type", "title", "description", "owner",
            "lifecycle_phase", "audit", "status", "probability", "impact",
            "priority", "mitigation_plan", "contingency_plan", "review_date",
            "acceptance_rationale", "accepted_by",
        }, path)
        if record.get("object_type") != "risk":
            raise DomainValidationError(f"{path}.object_type must be 'risk'")

    audit_value = record.get("audit") if canonical else None
    audit = _audit(audit_value, f"{path}.audit") if audit_value is not None else AuditMetadata(
        None, None, _legacy_source(record.get("source"))
    )
    review_date = record.get("review_date", record.get("due_date"))
    priority = record.get("priority", record.get("severity"))
    try:
        return Risk(
            object_id=object_id,
            object_type="risk",
            title=title,
            description=_clean_optional(record.get("description")) if canonical else None,
            owner=_owner(record.get("owner"), f"{path}.owner"),
            lifecycle_phase=_optional_phase(record.get("lifecycle_phase"), f"{path}.lifecycle_phase"),
            audit=audit,
            status=_legacy_risk_status(record.get("status", "open"), f"{path}.status"),
            probability=_optional_enum(RiskProbability, record.get("probability"), f"{path}.probability"),
            impact=_optional_enum(RiskImpact, record.get("impact"), f"{path}.impact"),
            priority=_optional_enum(RiskPriority, priority, f"{path}.priority"),
            mitigation_plan=_clean_optional(record.get("mitigation_plan")),
            contingency_plan=_clean_optional(record.get("contingency_plan")),
            review_date=_clean_optional(review_date),
            acceptance_rationale=_clean_optional(record.get("acceptance_rationale")),
            accepted_by=_owner(record.get("accepted_by"), f"{path}.accepted_by"),
        )
    except DomainValidationError as error:
        message = str(error)
        if message.startswith(f"{path}."):
            raise
        raise DomainValidationError(f"{path}: {error}") from error


def normalize_issue(value, program_id, index):
    """Normalize one legacy or canonical Issue without mutating its source.

    Legacy date-only ``resolved_date`` values use the explicit start-of-day UTC
    policy (``YYYY-MM-DDT00:00:00+00:00``).
    """
    path = f"issues[{index}]"
    if isinstance(value, str):
        record = {"title": value}
    elif isinstance(value, dict):
        record = dict(value)
    else:
        raise DomainValidationError(f"{path} must be a string or object")
    title = _first_text(record, "title", "description", "issue", "name")
    if not title:
        raise DomainValidationError(f"{path} must contain non-empty issue text")
    object_id = _legacy_issue_object_id(record, program_id, index, value)
    canonical = "object_id" in record or record.get("object_type") == "issue"
    if canonical:
        _exact_fields(record, {
            "object_id", "object_type", "title", "description", "owner",
            "lifecycle_phase", "audit", "status", "severity", "impact",
            "due_date", "resolution_summary", "resolved_at", "root_cause",
        }, path)
        if record.get("object_type") != "issue":
            raise DomainValidationError(f"{path}.object_type must be 'issue'")
    audit_value = record.get("audit") if canonical else None
    audit = _audit(audit_value, f"{path}.audit") if audit_value is not None else AuditMetadata(
        None, None, _legacy_source(record.get("source"))
    )
    due_date = _clean_optional(record.get("due_date"))
    resolved_at = record.get("resolved_at", record.get("resolved_date", record.get("closed_at")))
    if "resolved_date" in record and "resolved_at" not in record:
        raw = record.get("resolved_date")
        if isinstance(raw, str) and len(raw) == 10:
            _optional_date(raw, f"{path}.resolved_at")
            resolved_at = f"{raw}T00:00:00+00:00"
    resolved_at = _clean_optional(resolved_at)
    _optional_date(due_date, f"{path}.due_date")
    _optional_utc_datetime(resolved_at, f"{path}.resolved_at")
    try:
        return Issue(
            object_id=object_id, object_type="issue", title=title,
            description=_clean_optional(record.get("description")) if canonical else None,
            owner=_owner(record.get("owner"), f"{path}.owner"),
            lifecycle_phase=_optional_phase(record.get("lifecycle_phase"), f"{path}.lifecycle_phase"),
            audit=audit,
            status=_legacy_issue_status(record.get("status", "open"), f"{path}.status"),
            severity=_optional_enum(IssueSeverity, record.get("severity"), f"{path}.severity"),
            impact=_clean_optional(record.get("impact")), due_date=due_date,
            resolution_summary=_clean_optional(record.get("resolution_summary", record.get("resolution"))),
            resolved_at=resolved_at, root_cause=_clean_optional(record.get("root_cause")),
        )
    except DomainValidationError as error:
        message = str(error)
        if message.startswith(f"{path}."):
            raise
        raise DomainValidationError(f"{path}: {error}") from error


def normalize_dependency(value, program_id, index):
    """Normalize one legacy or canonical Dependency without mutating its source."""
    path = f"dependencies[{index}]"
    if isinstance(value, str):
        record = {"title": value}
    elif isinstance(value, dict):
        record = dict(value)
    else:
        raise DomainValidationError(f"{path} must be a string or object")
    title = _first_text(record, "title", "dependency", "description", "name")
    if not title:
        raise DomainValidationError(f"{path} must contain non-empty dependency text")
    object_id = _legacy_dependency_object_id(record, program_id, index, value)
    canonical = "object_id" in record or record.get("object_type") == "dependency"
    if canonical:
        _exact_fields(record, {
            "object_id", "object_type", "title", "description", "owner",
            "lifecycle_phase", "audit", "status", "dependency_type", "depends_on",
            "external_party", "required_by_date", "impact", "mitigation_plan",
        }, path)
        if record.get("object_type") != "dependency":
            raise DomainValidationError(f"{path}.object_type must be 'dependency'")
    audit_value = record.get("audit") if canonical else None
    audit = _audit(audit_value, f"{path}.audit") if audit_value is not None else AuditMetadata(
        None, None, _legacy_source(record.get("source"))
    )
    required_by_date = _clean_optional(record.get("required_by_date"))
    _optional_date(required_by_date, f"{path}.required_by_date")
    try:
        return Dependency(
            object_id=object_id, object_type="dependency", title=title,
            description=_clean_optional(record.get("description")) if canonical else None,
            owner=_owner(record.get("owner"), f"{path}.owner"),
            lifecycle_phase=_optional_phase(record.get("lifecycle_phase"), f"{path}.lifecycle_phase"),
            audit=audit,
            status=_legacy_dependency_status(record.get("status", "open"), f"{path}.status"),
            dependency_type=_enum(DependencyType, record.get("dependency_type", "internal"), f"{path}.dependency_type"),
            depends_on=_clean_optional(record.get("depends_on")),
            external_party=_clean_optional(record.get("external_party")),
            required_by_date=required_by_date,
            impact=_clean_optional(record.get("impact")),
            mitigation_plan=_clean_optional(record.get("mitigation_plan")),
        )
    except DomainValidationError as error:
        message = str(error)
        if message.startswith(f"{path}."):
            raise
        raise DomainValidationError(f"{path}: {error}") from error


def normalize_relationship(value, index):
    path = f"relationships[{index}]"
    if not isinstance(value, dict):
        raise DomainValidationError(f"{path} must be an object")
    _exact_fields(value, {
        "relationship_id", "relationship_type", "source_object_id",
        "target_object_id", "created_at", "source",
    }, path)
    try:
        return ProgramRelationship(
            relationship_id=value.get("relationship_id"),
            relationship_type=_enum(RelationshipType, value.get("relationship_type"), f"{path}.relationship_type"),
            source_object_id=value.get("source_object_id"),
            target_object_id=value.get("target_object_id"),
            created_at=value.get("created_at"),
            source=_enum(DomainSource, value.get("source"), f"{path}.source"),
        )
    except DomainValidationError as error:
        raise DomainValidationError(f"{path}: {error}") from error


def normalize_program_entities(program):
    """Return canonical adopted entities and relationships for one Program."""
    program_id = program.get("program_id") if isinstance(program, dict) else ""
    actions = [
        normalize_action(value, program_id, index)
        for index, value in enumerate(program.get("next_actions", []))
    ]
    risks = [
        normalize_risk(value, program_id, index)
        for index, value in enumerate(program.get("risks", []))
    ]
    issues = [
        normalize_issue(value, program_id, index)
        for index, value in enumerate(program.get("issues", []))
    ]
    dependencies = [
        normalize_dependency(value, program_id, index)
        for index, value in enumerate(program.get("dependencies", []))
    ]
    relationships = [
        normalize_relationship(value, index)
        for index, value in enumerate(program.get("relationships", []))
    ]
    validate_object_identity([*actions, *risks, *issues, *dependencies], relationships)
    return (
        [item.to_dict() for item in actions],
        [item.to_dict() for item in risks],
        [item.to_dict() for item in issues],
        [item.to_dict() for item in dependencies],
        [item.to_dict() for item in relationships],
    )


def validate_object_identity(entities, relationships):
    object_ids = [entity.object_id for entity in entities]
    if len(set(object_ids)) != len(object_ids):
        raise DomainValidationError("Program entity object_id values must be unique")
    known = set(object_ids)
    entity_types = {entity.object_id: entity.object_type for entity in entities}
    relationship_ids = set()
    relationship_keys = set()
    for relationship in relationships:
        if relationship.relationship_id in relationship_ids:
            raise DomainValidationError("relationship_id values must be unique")
        relationship_ids.add(relationship.relationship_id)
        if relationship.source_object_id not in known or relationship.target_object_id not in known:
            raise DomainValidationError(
                f"relationship {relationship.relationship_id} references an unknown object_id"
            )
        source_type = entity_types[relationship.source_object_id]
        target_type = entity_types[relationship.target_object_id]
        required_types = {
            RelationshipType.RESOLVES: ("action", "issue"),
            RelationshipType.REALIZED_AS: ("risk", "issue"),
            RelationshipType.RESULTS_FROM: ("issue", "risk"),
            RelationshipType.BLOCKS: (("action", "dependency"), ("dependency", "action")),
        }
        allowed = required_types.get(relationship.relationship_type)
        if allowed and isinstance(allowed[0], tuple) and (source_type, target_type) not in allowed:
            raise DomainValidationError(
                "relationship blocks must be action -> dependency or dependency -> action"
            )
        if allowed and not isinstance(allowed[0], tuple) and (source_type, target_type) != allowed:
            expected = required_types[relationship.relationship_type]
            raise DomainValidationError(
                f"relationship {relationship.relationship_type.value} must be {expected[0]} -> {expected[1]}"
            )
        key = (
            relationship.relationship_type.value,
            relationship.source_object_id,
            relationship.target_object_id,
        )
        if relationship.relationship_type == RelationshipType.RELATES_TO:
            key = (key[0], *sorted(key[1:]))
        if key in relationship_keys:
            raise DomainValidationError("Program relationships must be unique")
        relationship_keys.add(key)


def _legacy_object_id(record, program_id, index, original):
    candidate = record.get("object_id") or record.get("action_id")
    if candidate:
        try:
            return str(UUID(str(candidate).removeprefix("action-")))
        except (ValueError, AttributeError) as error:
            raise DomainValidationError(
                f"next_actions[{index}].object_id must be a UUID or action-UUID"
            ) from error
    payload = json.dumps(original, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return str(uuid5(LEGACY_IMPORT_NAMESPACE, f"{program_id}|next_actions|{index}|{payload}"))


def _legacy_risk_object_id(record, program_id, index, original):
    candidate = record.get("object_id") or record.get("risk_id")
    if candidate:
        try:
            return str(UUID(str(candidate).removeprefix("risk-")))
        except (ValueError, AttributeError) as error:
            raise DomainValidationError(
                f"risks[{index}].object_id must be a UUID or risk-UUID"
            ) from error
    payload = json.dumps(original, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return str(uuid5(LEGACY_IMPORT_NAMESPACE, f"{program_id}|risks|{index}|{payload}"))


def _legacy_issue_object_id(record, program_id, index, original):
    candidate = record.get("object_id") or record.get("issue_id")
    if candidate:
        try:
            return str(UUID(str(candidate).removeprefix("issue-")))
        except (ValueError, AttributeError) as error:
            raise DomainValidationError(
                f"issues[{index}].object_id must be a UUID or issue-UUID"
            ) from error
    payload = json.dumps(original, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return str(uuid5(LEGACY_IMPORT_NAMESPACE, f"{program_id}|issues|{index}|{payload}"))


def _legacy_dependency_object_id(record, program_id, index, original):
    candidate = record.get("object_id") or record.get("dependency_id")
    if candidate:
        try:
            return str(UUID(str(candidate).removeprefix("dependency-")))
        except (ValueError, AttributeError) as error:
            raise DomainValidationError(
                f"dependencies[{index}].object_id must be a UUID or dependency-UUID"
            ) from error
    payload = json.dumps(original, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return str(uuid5(LEGACY_IMPORT_NAMESPACE, f"{program_id}|dependencies|{index}|{payload}"))


def _legacy_status(value, path):
    if isinstance(value, ActionStatus):
        return value
    if not isinstance(value, str):
        raise DomainValidationError(f"{path}.status is unsupported")
    aliases = {
        "open": ActionStatus.OPEN,
        "in progress": ActionStatus.IN_PROGRESS,
        "in_progress": ActionStatus.IN_PROGRESS,
        "blocked": ActionStatus.BLOCKED,
        "completed": ActionStatus.COMPLETED,
        "done": ActionStatus.COMPLETED,
        "closed": ActionStatus.COMPLETED,
        "cancelled": ActionStatus.CANCELLED,
        "canceled": ActionStatus.CANCELLED,
    }
    try:
        return aliases[value.strip().lower()]
    except KeyError as error:
        raise DomainValidationError(f"{path}.status is unsupported") from error


def _legacy_risk_status(value, path):
    if isinstance(value, RiskStatus):
        return value
    if not isinstance(value, str):
        raise DomainValidationError(f"{path} is unsupported")
    aliases = {item.value.replace("_", " "): item for item in RiskStatus}
    normalized = " ".join(value.strip().lower().replace("_", " ").split())
    try:
        return aliases[normalized]
    except KeyError as error:
        raise DomainValidationError(f"{path} is unsupported") from error


def _legacy_issue_status(value, path):
    if isinstance(value, IssueStatus):
        return value
    if not isinstance(value, str):
        raise DomainValidationError(f"{path} is unsupported")
    aliases = {
        "open": IssueStatus.OPEN, "in progress": IssueStatus.IN_PROGRESS,
        "blocked": IssueStatus.BLOCKED, "resolved": IssueStatus.RESOLVED,
        "done": IssueStatus.RESOLVED, "completed": IssueStatus.RESOLVED,
        "closed": IssueStatus.CLOSED,
    }
    normalized = " ".join(value.strip().lower().replace("_", " ").split())
    try:
        return aliases[normalized]
    except KeyError as error:
        raise DomainValidationError(f"{path} is unsupported") from error


def _legacy_dependency_status(value, path):
    if isinstance(value, DependencyStatus):
        return value
    if not isinstance(value, str):
        raise DomainValidationError(f"{path} is unsupported")
    normalized = "_".join(value.strip().lower().replace("_", " ").split())
    try:
        return DependencyStatus(normalized)
    except ValueError as error:
        raise DomainValidationError(f"{path} is unsupported") from error


def _legacy_source(value):
    if isinstance(value, str) and value.strip().lower() == "sow analysis":
        return DomainSource.SOW_ANALYSIS
    return DomainSource.LEGACY_IMPORT


def _owner(value, path="owner"):
    if value is None:
        return None
    if isinstance(value, OwnerReference):
        return value
    if isinstance(value, str):
        return OwnerReference(value)
    if isinstance(value, dict):
        _exact_fields(value, {"display_name", "stakeholder_id"}, path)
        return OwnerReference(value.get("display_name"), value.get("stakeholder_id"))
    raise DomainValidationError(f"{path} must be a string, object, or null")


def _audit(value, path):
    if not isinstance(value, dict):
        raise DomainValidationError(f"{path} must be an object")
    _exact_fields(value, {"created_at", "updated_at", "source"}, path)
    return AuditMetadata(
        value.get("created_at"),
        value.get("updated_at"),
        _enum(DomainSource, value.get("source"), f"{path}.source"),
    )


def _optional_phase(value, path="lifecycle_phase"):
    if value is None or value == "":
        return None
    aliases = {
        "program initiation": LifecyclePhase.INITIATION,
        "initiation": LifecyclePhase.INITIATION,
        "pre-sales": LifecyclePhase.DISCOVERY,
        "discovery": LifecyclePhase.DISCOVERY,
        "planning": LifecyclePhase.PLANNING,
        "delivery": LifecyclePhase.EXECUTION,
        "execution": LifecyclePhase.EXECUTION,
        "go-live readiness": LifecyclePhase.READINESS_GO_LIVE,
        "operational readiness": LifecyclePhase.READINESS_GO_LIVE,
        "readiness_go_live": LifecyclePhase.READINESS_GO_LIVE,
        "operational transition": LifecyclePhase.TRANSITION_HANDOFF,
        "transition_handoff": LifecyclePhase.TRANSITION_HANDOFF,
        "hypercare": LifecyclePhase.OPERATIONS_CLOSURE,
        "closed": LifecyclePhase.OPERATIONS_CLOSURE,
        "operations_closure": LifecyclePhase.OPERATIONS_CLOSURE,
    }
    if isinstance(value, LifecyclePhase):
        return value
    if isinstance(value, str) and value.strip().lower() in aliases:
        return aliases[value.strip().lower()]
    raise DomainValidationError(f"{path} is unsupported")


def _enum(enum_type, value, path):
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)
    except (ValueError, TypeError) as error:
        raise DomainValidationError(f"{path} is unsupported") from error


def _optional_enum(enum_type, value, path):
    return None if value is None or value == "" else _enum(enum_type, value, path)


def _first_text(record, *fields):
    for field in fields:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _clean_optional(value):
    return value.strip() if isinstance(value, str) and value.strip() else None if value is None or value == "" else value


def _required_text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise DomainValidationError(f"{path} must be a non-empty string")


def _optional_text(value, path):
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise DomainValidationError(f"{path} must be a non-empty string or null")


def _uuid(value, path):
    try:
        UUID(str(value))
    except (ValueError, TypeError, AttributeError) as error:
        raise DomainValidationError(f"{path} must be a UUID") from error


def _optional_date(value, path):
    if value is None:
        return
    if not isinstance(value, str):
        raise DomainValidationError(f"{path} must be an ISO date or null")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise DomainValidationError(f"{path} must be an ISO date or null") from error


def _optional_datetime(value, path):
    if value is None:
        return
    if not isinstance(value, str):
        raise DomainValidationError(f"{path} must be an ISO datetime or null")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise DomainValidationError(f"{path} must be an ISO datetime or null") from error
    if parsed.tzinfo is None:
        raise DomainValidationError(f"{path} must include a timezone")


def _optional_utc_datetime(value, path):
    _optional_datetime(value, path)
    if value is None:
        return
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise DomainValidationError(f"{path} must be a UTC datetime or null")


def _exact_fields(record, fields, path):
    if set(record) != fields:
        raise DomainValidationError(f"{path} has unsupported or missing fields")
