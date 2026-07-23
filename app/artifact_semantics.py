"""Immutable, renderer-neutral semantic artifact contracts."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from executive_report import (
    CompletenessNotice as ReportCompletenessNotice,
    DeterministicValue,
    RecommendationCategory,
    RecordKind,
    ReportValue,
    SourceReference,
    ValueClassification,
)


SEMANTIC_ARTIFACT_VERSION = "1.0"


class ArtifactType(str, Enum):
    EXECUTIVE_STATUS_REPORT = "executive_status_report"


class AudienceProfile(str, Enum):
    EXECUTIVE = "executive"


class DensityProfile(str, Enum):
    EXECUTIVE_STANDARD = "executive_standard"
    EXECUTIVE_COMPACT = "executive_compact"


class SemanticEmphasis(str, Enum):
    PRIMARY = "primary"
    STANDARD = "standard"
    SUPPORTING = "supporting"


@dataclass(frozen=True)
class SourceIdentity:
    program_id: ReportValue
    report_date: DeterministicValue
    report_contract_version: str
    report_id: ReportValue


@dataclass(frozen=True)
class ArtifactHeader:
    title: str
    program_name: ReportValue
    customer: ReportValue
    report_date: DeterministicValue
    report_contract_version: str
    artifact_version: str
    classification_label: Optional[str]
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.PRIMARY


@dataclass(frozen=True)
class StatusSummary:
    phase: ReportValue
    health: ReportValue
    confidence: ReportValue
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.PRIMARY


@dataclass(frozen=True)
class Metric:
    label: str
    record_kind: RecordKind
    total: DeterministicValue
    active: DeterministicValue
    blocked: DeterministicValue
    overdue: DeterministicValue
    classification: ValueClassification
    definition: str
    sources: tuple[SourceReference, ...]
    accessibility_label: str


@dataclass(frozen=True)
class MetricGroup:
    label: str
    metrics: tuple[Metric, ...]
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.STANDARD


@dataclass(frozen=True)
class NarrativeBlock:
    label: str
    narrative: ReportValue
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.STANDARD


@dataclass(frozen=True)
class Callout:
    label: str
    classification: ValueClassification
    statement: str
    rationale: str
    category: RecommendationCategory
    evidence_source_ids: tuple[str, ...]
    evidence_references: tuple[SourceReference, ...]
    policy_rule_id: str
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.PRIMARY


@dataclass(frozen=True)
class RecordItem:
    source_id: ReportValue
    record_kind: RecordKind
    title: ReportValue
    description: ReportValue
    status: ReportValue
    priority: ReportValue
    severity: ReportValue
    owner: ReportValue
    relevant_date: ReportValue
    overdue: DeterministicValue
    active: DeterministicValue
    impact: ReportValue
    response: ReportValue
    created_at: ReportValue
    updated_at: ReportValue
    sources: tuple[SourceReference, ...]
    accessibility_label: str


@dataclass(frozen=True)
class RecordCollection:
    label: str
    record_kind: RecordKind
    selection_policy_id: str
    total_available: int
    selected_count: int
    omitted_count: int
    records: tuple[RecordItem, ...]
    empty_state: str
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.STANDARD


@dataclass(frozen=True)
class CompletenessNotice:
    heading: str
    notices: tuple[ReportCompletenessNotice, ...]
    empty_state: str
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.SUPPORTING


@dataclass(frozen=True)
class ArtifactFooter:
    product_name: str
    artifact_type: ArtifactType
    artifact_version: str
    report_date: DeterministicValue
    classification_label: Optional[str]
    accessibility_label: str
    emphasis: SemanticEmphasis = SemanticEmphasis.SUPPORTING


SemanticComponent = Union[
    ArtifactHeader,
    StatusSummary,
    MetricGroup,
    NarrativeBlock,
    Callout,
    RecordCollection,
    CompletenessNotice,
    ArtifactFooter,
]


@dataclass(frozen=True)
class SemanticArtifact:
    artifact_type: ArtifactType
    artifact_version: str
    title: str
    audience_profile: AudienceProfile
    density_profile: DensityProfile
    accessibility_label: str
    components: tuple[SemanticComponent, ...]
    source_identity: SourceIdentity
