import copy
import unittest
from unittest.mock import patch
from uuid import UUID

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from program_domain import (
    ActionPriority,
    ActionStatus,
    DomainSource,
    DomainValidationError,
    LifecyclePhase,
    ProgramRelationship,
    RelationshipType,
    RiskImpact,
    RiskPriority,
    RiskProbability,
    RiskStatus,
    create_action,
    create_risk,
    normalize_action,
    normalize_program_entities,
    normalize_risk,
)


class ProgramDomainTests(unittest.TestCase):
    def test_new_minimal_and_complete_risks_are_canonical_uuid4(self):
        with patch("program_domain.utc_timestamp", return_value="2026-07-22T12:00:00+00:00"):
            minimal = create_risk("Licensing approval may delay deployment")
            complete = create_risk(
                "Adoption readiness may delay rollout", description="Regional readiness gap",
                owner="Change Lead", lifecycle_phase="execution", status="monitoring",
                probability="high", impact="critical", priority="high",
                mitigation_plan="Run readiness reviews", contingency_plan="Stage rollout",
                review_date="2026-08-01",
            )
        self.assertEqual(UUID(minimal.object_id).version, 4)
        self.assertEqual(minimal.object_type, "risk")
        self.assertEqual(minimal.status, RiskStatus.OPEN)
        self.assertEqual(minimal.audit.source, DomainSource.CLI)
        self.assertEqual(complete.probability, RiskProbability.HIGH)
        self.assertEqual(complete.impact, RiskImpact.CRITICAL)
        self.assertEqual(complete.priority, RiskPriority.HIGH)
        self.assertEqual(complete.owner.display_name, "Change Lead")

    def test_risk_validation_and_accepted_requirements(self):
        invalid = (
            ({"status": "waiting"}, "status"), ({"probability": "certain"}, "probability"),
            ({"impact": "extreme"}, "impact"), ({"priority": "urgent"}, "priority"),
            ({"review_date": "August 1"}, "review_date"), ({"owner": " "}, "owner"),
            ({"lifecycle_phase": "invented"}, "lifecycle_phase"),
            ({"status": "accepted", "accepted_by": "Sponsor"}, "acceptance_rationale"),
            ({"status": "accepted", "acceptance_rationale": "Within tolerance"}, "accepted_by"),
        )
        for values, message in invalid:
            with self.subTest(values=values), self.assertRaisesRegex(DomainValidationError, message):
                create_risk("Valid risk", **values)
        with self.assertRaisesRegex(DomainValidationError, "title"):
            create_risk(" ")
        accepted = create_risk("Accepted exposure", status="accepted", acceptance_rationale="Within tolerance", accepted_by="Sponsor")
        self.assertEqual(accepted.status, RiskStatus.ACCEPTED)

    def test_legacy_risk_normalization_aliases_ids_and_non_mutation(self):
        legacy = {"risk": "Vendor approval may slip", "status": " Monitoring ", "owner": "Vendor Lead", "due_date": "2026-08-01", "severity": "high", "ignored": "compatible"}
        original = copy.deepcopy(legacy)
        first = normalize_risk(legacy, "alpha", 2)
        second = normalize_risk(legacy, "alpha", 2)
        self.assertEqual(legacy, original)
        self.assertEqual(first, second)
        self.assertEqual(UUID(first.object_id).version, 5)
        self.assertEqual(first.review_date, "2026-08-01")
        self.assertEqual(first.priority, RiskPriority.HIGH)
        self.assertEqual(first.owner.display_name, "Vendor Lead")
        bare = "22222222-2222-4222-8222-222222222222"
        self.assertEqual(normalize_risk({"risk_id": f"risk-{bare}", "description": "Prefixed", "status": "Open"}, "alpha", 0).object_id, bare)
        self.assertEqual(normalize_risk({"risk_id": bare, "name": "Bare", "status": "Closed"}, "alpha", 0).object_id, bare)
        self.assertEqual(normalize_risk("String risk", "alpha", 0).title, "String risk")

    def test_risk_errors_are_path_specific_and_canonical_fields_are_closed(self):
        for value, index, message in (({"description": "Risk", "status": "bad"}, 1, r"risks\[1\]\.status"), ({"description": "Risk", "due_date": "bad"}, 2, r"risks\[2\].*review_date"), (" ", 0, r"risks\[0\]")):
            with self.subTest(value=value), self.assertRaisesRegex(DomainValidationError, message):
                normalize_risk(value, "alpha", index)
        canonical = create_risk("Canonical").to_dict()
        canonical["unknown"] = True
        with self.assertRaisesRegex(DomainValidationError, r"risks\[0\].*unsupported"):
            normalize_risk(canonical, "alpha", 0)
    def test_new_action_uses_uuid4_and_canonical_values(self):
        with patch("program_domain.utc_timestamp", return_value="2026-07-22T12:00:00+00:00"):
            action = create_action(
                "Confirm rollout cohort",
                priority="high",
                owner="Delivery Lead",
                lifecycle_phase="Program Initiation",
                due_date="2026-08-01",
            )

        self.assertEqual(UUID(action.object_id).version, 4)
        self.assertEqual(action.object_type, "action")
        self.assertEqual(action.status, ActionStatus.OPEN)
        self.assertEqual(action.priority, ActionPriority.HIGH)
        self.assertEqual(action.owner.display_name, "Delivery Lead")
        self.assertEqual(action.lifecycle_phase, LifecyclePhase.INITIATION)
        self.assertEqual(action.audit.source, DomainSource.CLI)
        self.assertEqual(action.audit.created_at, "2026-07-22T12:00:00+00:00")

    def test_legacy_normalization_is_deterministic_and_non_mutating(self):
        legacy = {
            "action": "Review support model",
            "status": "In Progress",
            "owner": "Operations",
            "due_date": "2026-08-01",
        }
        original = copy.deepcopy(legacy)

        first = normalize_action(legacy, "alpha", 2)
        second = normalize_action(legacy, "alpha", 2)

        self.assertEqual(legacy, original)
        self.assertEqual(first, second)
        self.assertEqual(UUID(first.object_id).version, 5)
        self.assertEqual(first.title, "Review support model")
        self.assertEqual(first.status, ActionStatus.IN_PROGRESS)
        self.assertEqual(first.owner.display_name, "Operations")

    def test_string_and_existing_action_id_are_normalized(self):
        string_action = normalize_action("Confirm scope", "alpha", 0)
        existing = normalize_action({
            "action_id": "action-11111111-1111-4111-8111-111111111111",
            "description": "Existing action",
            "status": "Open",
        }, "alpha", 1)

        self.assertEqual(string_action.title, "Confirm scope")
        self.assertEqual(existing.object_id, "11111111-1111-4111-8111-111111111111")

    def test_action_validates_owner_lifecycle_status_priority_and_dates(self):
        invalid = (
            ({"owner": " "}, "owner"),
            ({"lifecycle_phase": "invented"}, "lifecycle_phase"),
            ({"status": "waiting"}, "status"),
            ({"priority": "urgent"}, "priority"),
            ({"due_date": "August 1"}, "due_date"),
        )
        for values, message in invalid:
            with self.subTest(values=values), self.assertRaisesRegex(DomainValidationError, message):
                create_action("Valid title", **values)

    def test_aggregate_requires_unique_object_ids(self):
        action_id = "11111111-1111-4111-8111-111111111111"
        value = {
            "action_id": f"action-{action_id}",
            "description": "Duplicate identity",
            "status": "Open",
        }
        with self.assertRaisesRegex(DomainValidationError, "object_id values must be unique"):
            normalize_program_entities({
                "program_id": "alpha",
                "next_actions": [value, value],
                "relationships": [],
            })

    def test_risks_participate_in_aggregate_identity_and_relationship_registry(self):
        shared = "11111111-1111-4111-8111-111111111111"
        action = create_action("Action").to_dict()
        action["object_id"] = shared
        risk = create_risk("Risk").to_dict()
        risk["object_id"] = shared
        with self.assertRaisesRegex(DomainValidationError, "object_id values must be unique"):
            normalize_program_entities({"program_id": "alpha", "next_actions": [action], "risks": [risk], "relationships": []})

        action = create_action("Mitigate risk")
        risk = create_risk("Delivery risk")
        relationship = ProgramRelationship(
            relationship_id="33333333-3333-4333-8333-333333333333",
            relationship_type=RelationshipType.MITIGATES,
            source_object_id=action.object_id, target_object_id=risk.object_id,
            created_at=None, source=DomainSource.MANUAL,
        )
        _actions, _risks, relationships = normalize_program_entities({
            "program_id": "alpha", "next_actions": [action.to_dict()],
            "risks": [risk.to_dict()], "relationships": [relationship.to_dict()],
        })
        self.assertEqual(relationships[0]["target_object_id"], risk.object_id)

    def test_realized_as_is_vocabulary_only_until_issue_adoption(self):
        risk = create_risk("May become an issue")
        relationship = {
            "relationship_id": "33333333-3333-4333-8333-333333333333",
            "relationship_type": "realized_as", "source_object_id": risk.object_id,
            "target_object_id": "44444444-4444-4444-8444-444444444444",
            "created_at": None, "source": "manual",
        }
        with self.assertRaisesRegex(DomainValidationError, "unknown object_id"):
            normalize_program_entities({
                "program_id": "alpha", "next_actions": [], "risks": [risk.to_dict()],
                "issues": [{"issue_id": "issue-44444444-4444-4444-8444-444444444444", "description": "Legacy issue"}],
                "relationships": [relationship],
            })

    def test_relationship_round_trip_and_referential_validation(self):
        first = create_action("First")
        second = create_action("Second")
        relationship = ProgramRelationship(
            relationship_id="33333333-3333-4333-8333-333333333333",
            relationship_type=RelationshipType.DEPENDS_ON,
            source_object_id=first.object_id,
            target_object_id=second.object_id,
            created_at="2026-07-22T12:00:00+00:00",
            source=DomainSource.MANUAL,
        )

        actions, risks, relationships = normalize_program_entities({
            "program_id": "alpha",
            "next_actions": [first.to_dict(), second.to_dict()],
            "relationships": [relationship.to_dict()],
        })

        self.assertEqual(actions[0], first.to_dict())
        self.assertEqual(risks, [])
        self.assertEqual(relationships, [relationship.to_dict()])

        invalid = relationship.to_dict()
        invalid["target_object_id"] = "44444444-4444-4444-8444-444444444444"
        with self.assertRaisesRegex(DomainValidationError, "unknown object_id"):
            normalize_program_entities({
                "program_id": "alpha",
                "next_actions": [first.to_dict(), second.to_dict()],
                "relationships": [invalid],
            })

    def test_relationship_rejects_self_reference_and_unsupported_type(self):
        action = create_action("Only action")
        base = {
            "relationship_id": "33333333-3333-4333-8333-333333333333",
            "relationship_type": "depends_on",
            "source_object_id": action.object_id,
            "target_object_id": action.object_id,
            "created_at": None,
            "source": "manual",
        }
        with self.assertRaisesRegex(DomainValidationError, "same source and target"):
            normalize_program_entities({
                "program_id": "alpha", "next_actions": [action.to_dict()],
                "relationships": [base],
            })
        base["target_object_id"] = "44444444-4444-4444-8444-444444444444"
        base["relationship_type"] = "invented"
        with self.assertRaisesRegex(DomainValidationError, "relationship_type"):
            normalize_program_entities({
                "program_id": "alpha", "next_actions": [action.to_dict()],
                "relationships": [base],
            })


if __name__ == "__main__":
    unittest.main()
