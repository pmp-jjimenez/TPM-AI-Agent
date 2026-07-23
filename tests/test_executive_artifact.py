import inspect
import sys
import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path
from unittest.mock import patch


APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import executive_artifact
from artifact_semantics import (
    ArtifactFooter,
    ArtifactHeader,
    ArtifactType,
    AudienceProfile,
    Callout,
    CompletenessNotice,
    DensityProfile,
    MetricGroup,
    NarrativeBlock,
    RecordCollection,
    StatusSummary,
)
from executive_artifact import (
    DEFAULT_MAX_RECORDS_PER_COLLECTION,
    EXECUTIVE_RECORD_SELECTION_POLICY_VERSION,
    ExecutiveArtifactCompositionError,
    ExecutiveArtifactCompositionPolicy,
    compose_executive_status_artifact,
)
from executive_report import (
    MissingValue,
    RecordKind,
    ReportMetadataInput,
    ValueClassification,
    build_executive_report_view_model,
)


REPORT_INPUT = ReportMetadataInput(
    report_date=date(2026, 7, 23),
    generated_at="2026-07-23T12:00:00-06:00",
    locale="en-US",
    timezone="America/Mexico_City",
    report_id="status-alpha-2026-07-23",
)


def program(**overrides):
    value = {
        "schema_version": "1.5.0",
        "program_id": "alpha",
        "program_name": "Alpha",
        "description": "Delivery program",
        "customer": "Customer",
        "phase": "Execution",
        "health": "Yellow",
        "confidence": "Medium",
        "risks": [],
        "issues": [],
        "dependencies": [],
        "decisions": [],
        "next_actions": [],
        "relationships": [],
        "metadata": {
            "created_at": "2026-07-01T12:00:00+00:00",
            "updated_at": "2026-07-22T12:00:00+00:00",
            "source": "api",
        },
    }
    value.update(overrides)
    return value


def compose(value=None, policy=None):
    view_model = build_executive_report_view_model(
        program() if value is None else value,
        report_metadata=REPORT_INPUT,
    )
    artifact = compose_executive_status_artifact(
        view_model,
        **({"policy": policy} if policy is not None else {}),
    )
    return view_model, artifact


def collections(artifact):
    return tuple(
        component
        for component in artifact.components
        if isinstance(component, RecordCollection)
    )


class ExecutiveCompositionBoundaryTests(unittest.TestCase):
    def test_module_is_renderer_independent(self):
        source = inspect.getsource(executive_artifact).lower()
        for forbidden in (
            "reportlab",
            "pillow",
            "pypdf",
            "gemini",
            "persistence",
            "normalize_program",
            "apply_compatibility",
        ):
            self.assertNotIn(forbidden, source)

    def test_artifact_identity_audience_version_and_default_density(self):
        _, artifact = compose()
        self.assertEqual(artifact.artifact_type, ArtifactType.EXECUTIVE_STATUS_REPORT)
        self.assertEqual(artifact.artifact_type.value, "executive_status_report")
        self.assertEqual(artifact.artifact_version, "1.0")
        self.assertEqual(artifact.audience_profile, AudienceProfile.EXECUTIVE)
        self.assertEqual(artifact.density_profile, DensityProfile.EXECUTIVE_STANDARD)

    def test_compact_density_is_explicit_and_never_automatic(self):
        many = [{"description": f"Risk {index}"} for index in range(15)]
        _, default = compose(program(risks=many))
        _, compact = compose(
            program(risks=many),
            ExecutiveArtifactCompositionPolicy(
                density_profile=DensityProfile.EXECUTIVE_COMPACT
            ),
        )
        self.assertEqual(default.density_profile, DensityProfile.EXECUTIVE_STANDARD)
        self.assertEqual(compact.density_profile, DensityProfile.EXECUTIVE_COMPACT)

    def test_component_order_is_exact(self):
        _, artifact = compose()
        self.assertEqual(
            tuple(type(component) for component in artifact.components),
            (
                ArtifactHeader,
                StatusSummary,
                NarrativeBlock,
                MetricGroup,
                Callout,
                RecordCollection,
                RecordCollection,
                RecordCollection,
                RecordCollection,
                RecordCollection,
                CompletenessNotice,
                ArtifactFooter,
            ),
        )
        self.assertEqual(
            tuple(item.record_kind for item in collections(artifact)),
            tuple(RecordKind),
        )

    def test_composer_does_not_acquire_wall_clock_time(self):
        view_model, _ = compose()
        with patch("time.time", side_effect=AssertionError("clock called")):
            compose_executive_status_artifact(view_model)

    def test_sparse_empty_and_legacy_models_compose(self):
        inputs = (
            {},
            program(program_name=None, health=None),
            program(
                risks=["Legacy risk"],
                issues=["Legacy issue"],
                dependencies=["Legacy dependency"],
                decisions=["Legacy decision"],
                next_actions=["Legacy action"],
            ),
        )
        for value in inputs:
            view_model = build_executive_report_view_model(
                value, report_metadata=REPORT_INPUT
            )
            self.assertEqual(
                len(compose_executive_status_artifact(view_model).components), 12
            )


class ExecutiveMappingTests(unittest.TestCase):
    def test_header_and_source_identity_preserve_source_values(self):
        view_model, artifact = compose()
        header = artifact.components[0]
        self.assertIs(header.program_name, view_model.program_identity.program_name)
        self.assertIs(header.customer, view_model.program_identity.customer)
        self.assertIs(header.report_date, view_model.report_metadata.report_date)
        self.assertEqual(header.report_contract_version, view_model.contract_version)
        self.assertIs(
            artifact.source_identity.program_id,
            view_model.report_metadata.source_program_id,
        )
        self.assertIs(
            artifact.source_identity.report_id,
            view_model.report_metadata.report_id,
        )
        self.assertFalse(
            hasattr(artifact.source_identity, "executive_summary")
            or hasattr(artifact.source_identity, "description")
        )

    def test_status_and_missing_meaning_are_preserved_as_text(self):
        view_model, artifact = compose(program(phase=None, health=None, confidence=None))
        status = artifact.components[1]
        self.assertIs(status.phase, view_model.reported_status.phase)
        self.assertIs(status.health, view_model.reported_status.health)
        self.assertIs(status.confidence, view_model.reported_status.confidence)
        self.assertIsInstance(status.health, MissingValue)
        self.assertIn("Missing value", status.accessibility_label)

    def test_narrative_preserves_exact_report_value(self):
        view_model, artifact = compose()
        narrative = artifact.components[2]
        self.assertIs(narrative.narrative, view_model.executive_summary)
        self.assertIn(view_model.executive_summary.reason, narrative.accessibility_label)

    def test_metrics_use_supplied_counts_and_classifications(self):
        view_model, artifact = compose(
            program(issues=[
                {"description": "Open", "status": "open"},
                {"description": "Closed", "status": "closed"},
            ])
        )
        metrics = artifact.components[3].metrics
        for metric, count in zip(metrics, view_model.record_counts):
            self.assertIs(metric.total, count.total)
            self.assertIs(metric.active, count.active)
            self.assertIs(metric.blocked, count.blocked)
            self.assertIs(metric.overdue, count.overdue)
            self.assertEqual(metric.classification, count.total.classification)
            self.assertEqual(metric.definition, count.total.definition)
        self.assertEqual(metrics[1].active.value, 1)

    def test_callout_preserves_recommendation_without_rerunning_policy(self):
        view_model, artifact = compose(program(issues=[
            {"description": "Blocked", "status": "blocked"}
        ]))
        callout = artifact.components[4]
        recommendation = view_model.primary_recommendation
        self.assertEqual(callout.statement, recommendation.statement)
        self.assertEqual(callout.rationale, recommendation.rationale)
        self.assertEqual(callout.category, recommendation.category)
        self.assertEqual(callout.classification, ValueClassification.RECOMMENDATION)
        self.assertIs(callout.evidence_source_ids, recommendation.evidence_source_ids)
        self.assertIs(callout.evidence_references, recommendation.evidence_references)
        self.assertEqual(callout.policy_rule_id, recommendation.policy_rule_id)

    def test_completeness_notices_and_known_limitations_preserve_order(self):
        view_model, artifact = compose({})
        component = artifact.components[10]
        self.assertIs(component.notices, view_model.completeness.notices)
        codes = tuple(notice.code for notice in component.notices)
        self.assertIn("DEPENDENCY_CRITICALITY_UNAVAILABLE", codes)
        self.assertIn("DECISION_BLOCKER_EVIDENCE_UNAVAILABLE", codes)
        self.assertIn("MISSING_EXECUTIVE_SUMMARY", codes)
        self.assertFalse(hasattr(component, "score"))

    def test_footer_has_identity_but_no_page_number(self):
        _, artifact = compose()
        footer = artifact.components[-1]
        self.assertEqual(footer.artifact_type, ArtifactType.EXECUTIVE_STATUS_REPORT)
        self.assertFalse(hasattr(footer, "page_number"))
        self.assertFalse(hasattr(footer, "page_count"))

    def test_every_component_has_meaningful_accessibility_label(self):
        _, artifact = compose()
        for component in artifact.components:
            self.assertIsInstance(component.accessibility_label, str)
            self.assertTrue(component.accessibility_label.strip())
        for collection in collections(artifact):
            self.assertIn(str(collection.selected_count), collection.accessibility_label)
            self.assertIn(str(collection.omitted_count), collection.accessibility_label)


class RecordSelectionTests(unittest.TestCase):
    def test_policy_version_and_default_are_explicit(self):
        self.assertEqual(EXECUTIVE_RECORD_SELECTION_POLICY_VERSION, "1.0")
        self.assertEqual(DEFAULT_MAX_RECORDS_PER_COLLECTION, 10)

    def test_fewer_exactly_and_more_than_default_limit(self):
        for total, expected_selected in ((9, 9), (10, 10), (11, 10)):
            records = [{"description": f"Risk {index}"} for index in range(total)]
            view_model, artifact = compose(program(risks=records))
            collection = collections(artifact)[0]
            self.assertEqual(collection.total_available, total)
            self.assertEqual(collection.selected_count, expected_selected)
            self.assertEqual(collection.omitted_count, total - expected_selected)
            self.assertEqual(len(view_model.risks), total)

    def test_custom_positive_limit_preserves_existing_order(self):
        records = [
            {"description": "Low", "priority": "low"},
            {"description": "Critical", "priority": "critical"},
            {"description": "High", "priority": "high"},
        ]
        view_model, artifact = compose(
            program(risks=records),
            ExecutiveArtifactCompositionPolicy(maximum_records_per_collection=2),
        )
        selected = collections(artifact)[0].records
        self.assertEqual(
            tuple(item.source_id for item in selected),
            tuple(item.source_id for item in view_model.risks[:2]),
        )
        self.assertEqual(
            tuple(item.title for item in selected),
            tuple(item.title for item in view_model.risks[:2]),
        )

    def test_invalid_limits_are_rejected(self):
        for value in (0, -1, True, False, 1001, 1.5, "10"):
            with self.subTest(value=value):
                with self.assertRaises(ExecutiveArtifactCompositionError):
                    ExecutiveArtifactCompositionPolicy(
                        maximum_records_per_collection=value
                    )

    def test_all_five_empty_collections_are_present_and_truthful(self):
        _, artifact = compose()
        self.assertEqual(len(collections(artifact)), 5)
        for collection in collections(artifact):
            self.assertEqual(collection.records, ())
            self.assertEqual(collection.total_available, 0)
            self.assertIn("records are present", collection.empty_state)
            self.assertNotIn(
                f"No {collection.record_kind.value}s exist",
                collection.empty_state,
            )

    def test_record_items_preserve_all_view_model_values(self):
        view_model, artifact = compose(program(risks=[{
            "description": "Risk",
            "status": "monitoring",
            "priority": "high",
            "owner": "Owner",
            "review_date": "2026-07-22",
            "impact": "high",
            "mitigation_plan": "Mitigate",
        }]))
        source = view_model.risks[0]
        item = collections(artifact)[0].records[0]
        for item_field, source_field in (
            ("source_id", "source_id"),
            ("title", "title"),
            ("description", "description"),
            ("status", "status"),
            ("priority", "priority"),
            ("severity", "severity"),
            ("owner", "owner"),
            ("relevant_date", "due_date"),
            ("overdue", "overdue"),
            ("active", "active"),
            ("impact", "impact"),
            ("response", "response"),
        ):
            self.assertIs(getattr(item, item_field), getattr(source, source_field))
        self.assertIs(item.sources, source.sources)


class ImmutabilityTests(unittest.TestCase):
    def test_artifact_components_and_nested_records_are_immutable_tuples(self):
        _, artifact = compose(program(risks=[{"description": "Risk"}]))
        self.assertIsInstance(artifact.components, tuple)
        collection = collections(artifact)[0]
        self.assertIsInstance(collection.records, tuple)
        with self.assertRaises(FrozenInstanceError):
            artifact.title = "Changed"
        with self.assertRaises(FrozenInstanceError):
            collection.records[0].title = "Changed"

    def test_composition_is_deeply_equal_and_view_model_unchanged(self):
        view_model = build_executive_report_view_model(
            program(risks=[{"description": f"Risk {index}"} for index in range(12)]),
            report_metadata=REPORT_INPUT,
        )
        before = deepcopy(view_model)
        first = compose_executive_status_artifact(view_model)
        second = compose_executive_status_artifact(view_model)
        self.assertEqual(first, second)
        self.assertEqual(view_model, before)
        self.assertEqual(len(view_model.risks), 12)


if __name__ == "__main__":
    unittest.main()
