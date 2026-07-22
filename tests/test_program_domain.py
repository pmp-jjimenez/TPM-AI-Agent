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
    create_action,
    normalize_action,
    normalize_program_entities,
)


class ProgramDomainTests(unittest.TestCase):
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

        actions, relationships = normalize_program_entities({
            "program_id": "alpha",
            "next_actions": [first.to_dict(), second.to_dict()],
            "relationships": [relationship.to_dict()],
        })

        self.assertEqual(actions[0], first.to_dict())
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
