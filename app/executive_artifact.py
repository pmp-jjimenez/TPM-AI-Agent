"""Compose Executive Report truth into renderer-neutral presentation intent."""

from dataclasses import dataclass
from typing import Optional

from artifact_semantics import (
    SEMANTIC_ARTIFACT_VERSION,
    ArtifactFooter,
    ArtifactHeader,
    ArtifactType,
    AudienceProfile,
    Callout,
    CompletenessNotice,
    DensityProfile,
    Metric,
    MetricGroup,
    NarrativeBlock,
    RecordCollection,
    RecordItem,
    SemanticArtifact,
    SourceIdentity,
    StatusSummary,
)
from executive_report import (
    DeterministicValue,
    ExecutiveReportViewModel,
    MissingValue,
    RecordCount,
    RecordKind,
    ReportRecord,
    ReportValue,
)


EXECUTIVE_RECORD_SELECTION_POLICY_VERSION = "1.0"
DEFAULT_MAX_RECORDS_PER_COLLECTION = 10
MAX_RECORDS_PER_COLLECTION = 1000
EXECUTIVE_STATUS_REPORT_TITLE = "Executive Status Report"
PRODUCT_NAME = "TPM Operating System"


class ExecutiveArtifactCompositionError(ValueError):
    """Raised when semantic composition policy is invalid."""


@dataclass(frozen=True)
class ExecutiveArtifactCompositionPolicy:
    maximum_records_per_collection: int = DEFAULT_MAX_RECORDS_PER_COLLECTION
    density_profile: DensityProfile = DensityProfile.EXECUTIVE_STANDARD
    classification_label: Optional[str] = None

    def __post_init__(self):
        maximum = self.maximum_records_per_collection
        if isinstance(maximum, bool) or not isinstance(maximum, int):
            raise ExecutiveArtifactCompositionError(
                "maximum_records_per_collection must be an integer"
            )
        if maximum < 1 or maximum > MAX_RECORDS_PER_COLLECTION:
            raise ExecutiveArtifactCompositionError(
                "maximum_records_per_collection must be between 1 and 1000"
            )
        if not isinstance(self.density_profile, DensityProfile):
            raise ExecutiveArtifactCompositionError(
                "density_profile must be an approved executive density"
            )
        label = self.classification_label
        if label is not None and (
            not isinstance(label, str) or not label.strip() or len(label) > 80
        ):
            raise ExecutiveArtifactCompositionError(
                "classification_label must be a bounded non-empty value"
            )
        if isinstance(label, str):
            object.__setattr__(self, "classification_label", label.strip())


def compose_executive_status_artifact(
    view_model: ExecutiveReportViewModel,
    *,
    policy: ExecutiveArtifactCompositionPolicy = ExecutiveArtifactCompositionPolicy(),
) -> SemanticArtifact:
    """Map approved report meaning into a closed semantic component sequence."""
    if not isinstance(view_model, ExecutiveReportViewModel):
        raise ExecutiveArtifactCompositionError(
            "view_model must be an ExecutiveReportViewModel"
        )
    if not isinstance(policy, ExecutiveArtifactCompositionPolicy):
        raise ExecutiveArtifactCompositionError(
            "policy must be an ExecutiveArtifactCompositionPolicy"
        )

    metadata = view_model.report_metadata
    identity = view_model.program_identity
    status = view_model.reported_status
    recommendation = view_model.primary_recommendation

    header = ArtifactHeader(
        title=EXECUTIVE_STATUS_REPORT_TITLE,
        program_name=identity.program_name,
        customer=identity.customer,
        report_date=metadata.report_date,
        report_contract_version=view_model.contract_version,
        artifact_version=SEMANTIC_ARTIFACT_VERSION,
        classification_label=policy.classification_label,
        accessibility_label=(
            f"{EXECUTIVE_STATUS_REPORT_TITLE}. Program: "
            f"{_accessible_value(identity.program_name)}. Customer: "
            f"{_accessible_value(identity.customer)}. Report date: "
            f"{_accessible_value(metadata.report_date)}."
        ),
    )
    status_summary = StatusSummary(
        phase=status.phase,
        health=status.health,
        confidence=status.confidence,
        accessibility_label=(
            f"Program status. Phase: {_accessible_value(status.phase)}. "
            f"Health: {_accessible_value(status.health)}. "
            f"Confidence: {_accessible_value(status.confidence)}."
        ),
    )
    narrative = NarrativeBlock(
        label="Executive summary",
        narrative=view_model.executive_summary,
        accessibility_label=(
            "Executive summary. "
            f"{_accessible_value(view_model.executive_summary)}"
        ),
    )
    metrics = MetricGroup(
        label="Record metrics",
        metrics=tuple(_compose_metric(count) for count in view_model.record_counts),
        accessibility_label="Record metrics for risks, issues, dependencies, decisions, and actions.",
    )
    callout = Callout(
        label="Primary recommendation",
        classification=recommendation.classification,
        statement=recommendation.statement,
        rationale=recommendation.rationale,
        category=recommendation.category,
        evidence_source_ids=recommendation.evidence_source_ids,
        evidence_references=recommendation.evidence_references,
        policy_rule_id=recommendation.policy_rule_id,
        accessibility_label=(
            f"Primary recommendation. {recommendation.statement} "
            f"Rationale: {recommendation.rationale}"
        ),
    )

    collections = tuple(
        _compose_collection(kind, records, policy.maximum_records_per_collection)
        for kind, records in (
            (RecordKind.RISK, view_model.risks),
            (RecordKind.ISSUE, view_model.issues),
            (RecordKind.DEPENDENCY, view_model.dependencies),
            (RecordKind.DECISION, view_model.decisions),
            (RecordKind.ACTION, view_model.actions),
        )
    )
    completeness_count = len(view_model.completeness.notices)
    completeness = CompletenessNotice(
        heading="Report completeness",
        notices=view_model.completeness.notices,
        empty_state="No reportable completeness notices are recorded.",
        accessibility_label=(
            f"Report completeness. {completeness_count} "
            f"{'notice' if completeness_count == 1 else 'notices'} recorded."
        ),
    )
    footer = ArtifactFooter(
        product_name=PRODUCT_NAME,
        artifact_type=ArtifactType.EXECUTIVE_STATUS_REPORT,
        artifact_version=SEMANTIC_ARTIFACT_VERSION,
        report_date=metadata.report_date,
        classification_label=policy.classification_label,
        accessibility_label=(
            f"{PRODUCT_NAME} {EXECUTIVE_STATUS_REPORT_TITLE}, artifact version "
            f"{SEMANTIC_ARTIFACT_VERSION}, report date "
            f"{_accessible_value(metadata.report_date)}."
        ),
    )
    components = (
        header,
        status_summary,
        narrative,
        metrics,
        callout,
        *collections,
        completeness,
        footer,
    )
    return SemanticArtifact(
        artifact_type=ArtifactType.EXECUTIVE_STATUS_REPORT,
        artifact_version=SEMANTIC_ARTIFACT_VERSION,
        title=EXECUTIVE_STATUS_REPORT_TITLE,
        audience_profile=AudienceProfile.EXECUTIVE,
        density_profile=policy.density_profile,
        accessibility_label=(
            f"{EXECUTIVE_STATUS_REPORT_TITLE} for "
            f"{_accessible_value(identity.program_name)}."
        ),
        components=components,
        source_identity=SourceIdentity(
            program_id=metadata.source_program_id,
            report_date=metadata.report_date,
            report_contract_version=view_model.contract_version,
            report_id=metadata.report_id,
        ),
    )


def _compose_metric(count: RecordCount) -> Metric:
    label = _plural_label(count.kind)
    return Metric(
        label=label,
        record_kind=count.kind,
        total=count.total,
        active=count.active,
        blocked=count.blocked,
        overdue=count.overdue,
        classification=count.total.classification,
        definition=count.total.definition,
        sources=count.total.sources,
        accessibility_label=(
            f"{label}: {count.total.value} total, {count.active.value} active, "
            f"{count.blocked.value} blocked, {count.overdue.value} overdue."
        ),
    )


def _compose_collection(
    kind: RecordKind,
    records: tuple[ReportRecord, ...],
    maximum: int,
) -> RecordCollection:
    selected = records[:maximum]
    total = len(records)
    selected_count = len(selected)
    omitted = total - selected_count
    label = _plural_label(kind)
    empty_state = f"No {kind.value} records are present in the report data."
    return RecordCollection(
        label=label,
        record_kind=kind,
        selection_policy_id=(
            f"executive_record_selection.{EXECUTIVE_RECORD_SELECTION_POLICY_VERSION}"
        ),
        total_available=total,
        selected_count=selected_count,
        omitted_count=omitted,
        records=tuple(_compose_record(record) for record in selected),
        empty_state=empty_state,
        accessibility_label=(
            f"{label} collection. {total} total available; {selected_count} selected; "
            f"{omitted} omitted. "
            + (empty_state if total == 0 else "")
        ).strip(),
    )


def _compose_record(record: ReportRecord) -> RecordItem:
    return RecordItem(
        source_id=record.source_id,
        record_kind=record.kind,
        title=record.title,
        description=record.description,
        status=record.status,
        priority=record.priority,
        severity=record.severity,
        owner=record.owner,
        relevant_date=record.due_date,
        overdue=record.overdue,
        active=record.active,
        impact=record.impact,
        response=record.response,
        created_at=record.created_at,
        updated_at=record.updated_at,
        sources=record.sources,
        accessibility_label=(
            f"{record.kind.value.capitalize()} {_accessible_value(record.source_id)}. "
            f"Title: {_accessible_value(record.title)}. "
            f"Status: {_accessible_value(record.status)}. "
            f"Owner: {_accessible_value(record.owner)}. "
            f"Overdue: {'yes' if record.overdue.value else 'no'}."
        ),
    )


def _accessible_value(value: ReportValue) -> str:
    if isinstance(value, MissingValue):
        return f"Missing value: {value.reason}"
    return str(value.value)


def _plural_label(kind: RecordKind) -> str:
    return {
        RecordKind.RISK: "Risks",
        RecordKind.ISSUE: "Issues",
        RecordKind.DEPENDENCY: "Dependencies",
        RecordKind.DECISION: "Decisions",
        RecordKind.ACTION: "Actions",
    }[kind]
