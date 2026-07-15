import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from schema import (
    CURRENT_SCHEMA_VERSION,
    apply_compatibility_defaults,
    create_program_record,
    validate_program,
)


class ProgramSchemaTests(unittest.TestCase):
    def test_create_program_record_includes_canonical_defaults(self):
        program = create_program_record(
            "payments-modernization",
            "Payments Modernization",
            "Modernize payment processing.",
        )

        self.assertEqual(program["schema_version"], CURRENT_SCHEMA_VERSION)
        self.assertEqual(program["phase"], "Program Initiation")
        self.assertEqual(program["health"], "Unknown")
        self.assertEqual(program["confidence"], "Medium")
        self.assertIn("metadata", program)
        self.assertIn("created_at", program["metadata"])
        self.assertIn("updated_at", program["metadata"])
        self.assertEqual(program["metadata"]["source"], "cli")

        for field in (
            "risks",
            "issues",
            "decisions",
            "next_actions",
            "meeting_history",
            "documents",
            "artifacts",
        ):
            self.assertEqual(program[field], [])

    def test_legacy_record_normalization_adds_defaults_without_mutating_input(self):
        legacy = {
            "program_id": "legacy-program",
            "program_name": "Legacy Program",
            "description": "Older record.",
            "issues": [{"description": "Legacy issue", "status": "Open"}],
        }

        normalized = apply_compatibility_defaults(legacy)

        self.assertNotIn("schema_version", legacy)
        self.assertIsNot(normalized, legacy)
        self.assertEqual(normalized["schema_version"], CURRENT_SCHEMA_VERSION)
        self.assertEqual(normalized["phase"], "Program Initiation")
        self.assertEqual(normalized["health"], "Unknown")
        self.assertEqual(normalized["confidence"], "Medium")
        self.assertEqual(normalized["meeting_history"], [])
        self.assertEqual(normalized["documents"], [])
        self.assertEqual(normalized["artifacts"], [])
        self.assertIn("metadata", normalized)

    def test_invalid_program_record_returns_clear_validation_errors(self):
        valid, errors = validate_program({
            "schema_version": CURRENT_SCHEMA_VERSION,
            "program_id": "",
            "program_name": "",
            "description": "",
            "phase": "Program Initiation",
            "health": "Unknown",
            "confidence": "Medium",
            "risks": "not-a-list",
            "issues": [],
            "decisions": [],
            "next_actions": [],
            "meeting_history": [],
            "documents": [],
            "artifacts": [],
            "metadata": {"source": "cli"},
        })

        self.assertFalse(valid)
        self.assertIn("program_id must be a non-empty string", errors)
        self.assertIn("risks must be a list", errors)
        self.assertIn("metadata.created_at is required", errors)


if __name__ == "__main__":
    unittest.main()
