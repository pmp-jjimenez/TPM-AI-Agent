import inspect
import json
import sys
import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch


APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import executive_report
from executive_report import (
    EXECUTIVE_REPORT_CONTRACT_VERSION,
    NO_RECOMMENDATION_TEXT,
    DeterministicValue,
    ExecutiveReportInputError,
    MissingValue,
    RecommendationCategory,
    ReportMetadataInput,
    StoredFact,
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


def build(value):
    return build_executive_report_view_model(value, report_metadata=REPORT_INPUT)


class ExecutiveReportBoundaryTests(unittest.TestCase):
    def test_module_imports_without_reportlab(self):
        self.assertNotIn("reportlab", inspect.getsource(executive_report).lower())

    def test_contract_version_and_metadata_are_explicit(self):
        result = build(program())
        self.assertEqual(result.contract_version, EXECUTIVE_REPORT_CONTRACT_VERSION)
        self.assertEqual(EXECUTIVE_REPORT_CONTRACT_VERSION, "1.0")
        self.assertEqual(result.report_metadata.report_date.value, "2026-07-23")
        self.assertEqual(result.report_metadata.generated_at.value, REPORT_INPUT.generated_at)
        self.assertEqual(result.report_metadata.report_id.value, REPORT_INPUT.report_id)

    def test_builder_never_calls_system_clock(self):
        with patch("time.time", side_effect=AssertionError("clock called")):
            self.assertEqual(build(program()).report_metadata.report_date.value, "2026-07-23")

    def test_invalid_input_error_is_bounded(self):
        secret = {"risks": [{"status": "secret invalid", "private": "do not leak"}]}
        with self.assertRaises(ExecutiveReportInputError) as caught:
            build(secret)
        self.assertNotIn(json.dumps(secret), str(caught.exception))
        self.assertNotIn("do not leak", str(caught.exception))

    def test_report_metadata_type_is_required(self):
        with self.assertRaisesRegex(ExecutiveReportInputError, "ReportMetadataInput"):
            build_executive_report_view_model(program(), report_metadata={})

    def test_datetime_is_not_accepted_as_report_date(self):
        metadata = ReportMetadataInput(report_date=datetime(2026, 7, 23, 12, 0))
        with self.assertRaisesRegex(ExecutiveReportInputError, "must be a date"):
            build_executive_report_view_model(program(), report_metadata=metadata)


class ExecutiveReportTruthTests(unittest.TestCase):
    def test_identity_and_reported_status_are_stored_facts(self):
        result = build(program())
        for value in (
            result.program_identity.program_id,
            result.program_identity.program_name,
            result.program_identity.customer,
            result.program_identity.description,
            result.reported_status.phase,
            result.reported_status.health,
            result.reported_status.confidence,
        ):
            self.assertIsInstance(value, StoredFact)
            self.assertEqual(value.classification, ValueClassification.STORED_FACT)

    def test_missing_identity_and_status_are_missing_not_compatibility_defaults(self):
        result = build({})
        self.assertIsInstance(result.program_identity.program_name, MissingValue)
        self.assertIsInstance(result.reported_status.phase, MissingValue)
        self.assertIsInstance(result.reported_status.health, MissingValue)
        self.assertIsInstance(result.reported_status.confidence, MissingValue)
        self.assertNotEqual(getattr(result.reported_status.health, "value", None), "Green")
        self.assertNotEqual(getattr(result.reported_status.confidence, "value", None), "High")

    def test_executive_summary_is_explicitly_missing(self):
        result = build(program(executive_summary="Unapproved extension field"))
        self.assertIsInstance(result.executive_summary, MissingValue)
        self.assertIn("no approved executive summary", result.executive_summary.reason.lower())

    def test_source_references_are_present(self):
        result = build(program())
        self.assertEqual(result.program_identity.program_name.sources[0].path, "/program_name")
        self.assertEqual(
            result.report_metadata.source_program_updated_at.sources[0].path,
            "/metadata/updated_at",
        )


class ExecutiveReportRecordTests(unittest.TestCase):
    def test_every_collection_retains_all_records_without_display_limit(self):
        many = [{"description": f"Risk {index}"} for index in range(12)]
        result = build(program(
            risks=many,
            issues=[{"description": "Issue"}],
            dependencies=[{"name": "Dependency"}],
            decisions=["Decision"],
            next_actions=["Action"],
        ))
        self.assertEqual(len(result.risks), 12)
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(len(result.dependencies), 1)
        self.assertEqual(len(result.decisions), 1)
        self.assertEqual(len(result.actions), 1)

    def test_active_status_policies(self):
        result = build(program(
            risks=[
                {"description": "Open", "status": "open"},
                {"description": "Monitor", "status": "monitoring"},
                {"description": "Mitigate", "status": "mitigating"},
                {
                    "description": "Accept", "status": "accepted",
                    "acceptance_rationale": "Known exposure", "accepted_by": "Sponsor",
                },
                {"description": "Closed", "status": "closed"},
            ],
            issues=[{"description": value, "status": value} for value in
                    ("open", "in_progress", "blocked", "resolved", "closed")],
            dependencies=[{"name": value, "status": value} for value in
                          ("open", "in_progress", "resolved", "closed")],
            decisions=[{"decision": value, "status": value} for value in
                       ("proposed", "approved", "superseded", "rejected")],
            next_actions=[{"description": value, "status": value} for value in
                          ("open", "in_progress", "blocked", "completed", "cancelled")],
        ))
        self.assertEqual(
            {item.status.value: item.active.value for item in result.risks},
            {"open": True, "monitoring": True, "mitigating": True, "accepted": True, "closed": False},
        )
        self.assertTrue(next(item for item in result.risks if item.status.value == "accepted").active.value)
        self.assertEqual(sum(item.active.value for item in result.issues), 3)
        self.assertEqual(sum(item.active.value for item in result.dependencies), 2)
        self.assertEqual(sum(item.active.value for item in result.decisions), 1)
        self.assertEqual(sum(item.active.value for item in result.actions), 3)

    def test_counts_are_deterministic_values(self):
        result = build(program(issues=[
            {"description": "A", "status": "open"},
            {"description": "B", "status": "closed"},
        ]))
        issue_count = result.record_counts[1]
        self.assertIsInstance(issue_count.total, DeterministicValue)
        self.assertIsInstance(issue_count.active, DeterministicValue)
        self.assertEqual((issue_count.total.value, issue_count.active.value), (2, 1))

    def test_overdue_uses_injected_date_and_excludes_closed(self):
        result = build(program(issues=[
            {"description": "Open old", "status": "open", "due_date": "2026-07-22"},
            {"description": "Open today", "status": "open", "due_date": "2026-07-23"},
            {"description": "Closed old", "status": "closed", "due_date": "2026-07-01"},
        ]))
        overdue = {item.title.value: item.overdue.value for item in result.issues}
        self.assertEqual(overdue, {"Open old": True, "Open today": False, "Closed old": False})

    def test_invalid_dates_follow_canonical_domain_validation(self):
        with self.assertRaises(ExecutiveReportInputError):
            build(program(issues=[{"description": "Bad date", "due_date": "tomorrow"}]))

    def test_ordering_is_importance_blocked_overdue_due_date_then_id(self):
        result = build(program(issues=[
            {"description": "Low", "severity": "low"},
            {"description": "Critical", "severity": "critical"},
            {"description": "Blocked", "severity": "high", "status": "blocked"},
            {"description": "High", "severity": "high", "due_date": "2026-08-01"},
        ]))
        self.assertEqual(
            [item.title.value for item in result.issues],
            ["Critical", "Blocked", "High", "Low"],
        )

    def test_sorting_tolerates_missing_optional_fields(self):
        result = build(program(
            risks=[{"description": "Risk"}],
            issues=[{"description": "Issue"}],
            dependencies=[{"name": "Dependency"}],
            decisions=["Decision"],
            next_actions=["Action"],
        ))
        self.assertEqual(sum(len(value) for value in (
            result.risks, result.issues, result.dependencies, result.decisions, result.actions
        )), 5)

    def test_records_expose_no_mutable_source_dictionary(self):
        result = build(program(risks=[{"description": "Risk", "owner": "Owner"}]))
        record = result.risks[0]
        self.assertFalse(any(isinstance(value, (dict, list)) for value in vars(record).values()))


class ExecutiveReportRecommendationTests(unittest.TestCase):
    def test_blocked_issue_has_first_precedence(self):
        result = build(program(
            issues=[{"description": "Blocked", "status": "blocked", "severity": "low"}],
            risks=[{"description": "Risk", "priority": "critical"}],
        ))
        self.assertEqual(result.primary_recommendation.category, RecommendationCategory.BLOCKED_ISSUE)
        self.assertIn(result.issues[0].source_id.value, result.primary_recommendation.statement)

    def test_high_risk_is_selected_without_blocked_issue(self):
        result = build(program(risks=[
            {"description": "High risk", "status": "monitoring", "priority": "high"}
        ]))
        self.assertEqual(result.primary_recommendation.category, RecommendationCategory.HIGH_RISK)

    def test_priority_action_is_selected(self):
        result = build(program(next_actions=[
            {"description": "Action", "status": "blocked", "priority": "high"}
        ]))
        self.assertEqual(result.primary_recommendation.category, RecommendationCategory.PRIORITY_ACTION)

    def test_overdue_priority_action_is_selected(self):
        result = build(program(next_actions=[{
            "description": "Action", "status": "open", "priority": "critical",
            "due_date": "2026-07-01",
        }]))
        self.assertEqual(result.primary_recommendation.category, RecommendationCategory.PRIORITY_ACTION)
        self.assertIn("overdue", result.primary_recommendation.statement)

    def test_active_dependency_with_explicit_impact_is_selected(self):
        result = build(program(dependencies=[{
            "name": "Dependency", "status": "open", "impact": "Delivery delay"
        }]))
        self.assertEqual(
            result.primary_recommendation.category,
            RecommendationCategory.IMPACTING_DEPENDENCY,
        )

    def test_closed_dependency_with_impact_is_not_selected(self):
        result = build(program(dependencies=[{
            "name": "Dependency", "status": "closed", "impact": "Delivery delay"
        }]))
        self.assertEqual(
            result.primary_recommendation.category,
            RecommendationCategory.NO_EVIDENCE_BACKED_ACTION,
        )

    def test_no_recommendation_text_is_exact(self):
        result = build(program())
        self.assertEqual(result.primary_recommendation.statement, NO_RECOMMENDATION_TEXT)
        self.assertEqual(
            result.primary_recommendation.classification,
            ValueClassification.RECOMMENDATION,
        )

    def test_recommendation_is_bounded_and_evidence_backed(self):
        result = build(program(issues=[{
            "description": "x" * 10000, "status": "blocked", "owner": "Confidential Name"
        }]))
        recommendation = result.primary_recommendation
        self.assertLess(len(recommendation.statement), 250)
        self.assertNotIn("Confidential Name", recommendation.statement)
        self.assertEqual(recommendation.evidence_source_ids, (result.issues[0].source_id.value,))
        self.assertTrue(recommendation.evidence_references)
        self.assertEqual(recommendation.policy_rule_id, "recommendation.1.blocked_issue")

    def test_decision_blocker_rule_is_honestly_unavailable(self):
        result = build(program(decisions=[{"decision": "Approve", "status": "proposed"}]))
        self.assertEqual(
            result.primary_recommendation.category,
            RecommendationCategory.NO_EVIDENCE_BACKED_ACTION,
        )
        self.assertIn(
            "DECISION_BLOCKER_EVIDENCE_UNAVAILABLE",
            {notice.code for notice in result.completeness.notices},
        )


class ExecutiveReportCompletenessTests(unittest.TestCase):
    def test_dependency_criticality_is_never_invented_and_always_disclosed(self):
        for value in (program(), program(dependencies=[{"name": "Dependency"}])):
            result = build(value)
            self.assertIn(
                "DEPENDENCY_CRITICALITY_UNAVAILABLE",
                {notice.code for notice in result.completeness.notices},
            )
            self.assertNotIn("criticality", vars(result.dependencies[0]) if result.dependencies else {})

    def test_missing_fields_create_bounded_notices(self):
        result = build({})
        codes = {notice.code for notice in result.completeness.notices}
        self.assertTrue({
            "MISSING_PROGRAM_NAME", "MISSING_CUSTOMER", "MISSING_DESCRIPTION",
            "MISSING_PHASE", "MISSING_HEALTH", "MISSING_CONFIDENCE",
            "MISSING_EXECUTIVE_SUMMARY",
        }.issubset(codes))

    def test_missing_owner_and_response_are_disclosed(self):
        result = build(program(risks=[{"description": "Risk"}]))
        codes = {notice.code for notice in result.completeness.notices}
        self.assertIn("MISSING_RECORD_OWNERS", codes)
        self.assertIn("MISSING_ACTIVE_RESPONSE", codes)

    def test_no_completeness_score_or_confidence_derivation_exists(self):
        result = build(program())
        self.assertFalse(hasattr(result.completeness, "score"))
        self.assertIsInstance(result.reported_status.confidence, StoredFact)


class ExecutiveReportImmutabilityTests(unittest.TestCase):
    def test_builder_does_not_mutate_canonical_or_legacy_input(self):
        canonical = program(risks=[{"description": "Risk"}])
        legacy = {"program_id": "legacy", "program_name": "Legacy", "risks": ["Risk"]}
        for source in (canonical, legacy):
            before = deepcopy(source)
            build(source)
            self.assertEqual(source, before)

    def test_legacy_generated_id_and_default_status_are_deterministic_not_stored(self):
        result = build({"program_id": "legacy", "risks": ["Recorded risk text"]})
        self.assertIsInstance(result.risks[0].source_id, DeterministicValue)
        self.assertIsInstance(result.risks[0].status, DeterministicValue)
        self.assertIsInstance(result.risks[0].title, StoredFact)

    def test_legacy_aliases_retain_deterministic_provenance(self):
        result = build({
            "program_id": "legacy",
            "risks": [{"risk": "Risk", "severity": "high", "due_date": "2026-08-01"}],
        })
        risk = result.risks[0]
        self.assertIsInstance(risk.priority, DeterministicValue)
        self.assertEqual(risk.priority.sources[0].path, "/risks/0/severity")
        self.assertIsInstance(risk.due_date, DeterministicValue)
        self.assertEqual(risk.due_date.sources[0].path, "/risks/0/due_date")

    def test_non_mapping_legacy_metadata_builds_as_missing(self):
        result = build({"program_id": "legacy", "metadata": None})
        self.assertIsInstance(
            result.report_metadata.source_program_updated_at, MissingValue
        )

    def test_top_level_nested_values_and_collections_are_immutable(self):
        result = build(program(risks=[{"description": "Risk"}]))
        with self.assertRaises(FrozenInstanceError):
            result.contract_version = "2.0"
        with self.assertRaises(FrozenInstanceError):
            result.risks[0].active.value = False
        with self.assertRaises(TypeError):
            result.risks[0] = result.risks[0]
        with self.assertRaises(AttributeError):
            result.risks.append(result.risks[0])

    def test_repeated_builds_are_deeply_equal(self):
        source = program(
            risks=[{"description": "Risk"}],
            issues=[{"description": "Issue"}],
        )
        self.assertEqual(build(source), build(source))

    def test_legacy_and_sparse_programs_build_successfully(self):
        legacy = {
            "program_id": "legacy", "program_name": "Legacy",
            "risks": ["Risk"], "issues": ["Issue"], "next_actions": ["Action"],
        }
        self.assertEqual(len(build(legacy).risks), 1)
        self.assertEqual(build({}).record_counts[0].total.value, 0)


if __name__ == "__main__":
    unittest.main()
