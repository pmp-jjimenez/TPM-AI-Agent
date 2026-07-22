import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import memory
from schema import CURRENT_SCHEMA_VERSION


class ProgramMemoryTests(unittest.TestCase):
    def test_legacy_risk_load_is_non_mutating_and_explicit_save_is_canonical(self):
        original_data_dir = memory.DATA_DIR
        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            memory.ensure_data_dir()
            path = memory.program_file("legacy-risk")
            legacy = {"program_id": "legacy-risk", "program_name": "Legacy Risk", "description": "Compatibility", "risks": [{"description": "Vendor approval may slip", "status": "Open"}]}
            path.write_text(json.dumps(legacy, indent=2), encoding="utf-8")
            before = path.read_text(encoding="utf-8")
            try:
                first = memory.load_program("legacy-risk")
                second = memory.load_program("legacy-risk")
                self.assertEqual(path.read_text(encoding="utf-8"), before)
                self.assertEqual(first["risks"], second["risks"])
                self.assertEqual(first["risks"][0]["object_type"], "risk")
                memory.save_program(first)
                saved = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(saved["risks"], first["risks"])
                self.assertNotIn("risk_id", saved["risks"][0])
            finally:
                memory.DATA_DIR = original_data_dir
    def test_legacy_actions_load_deterministically_without_rewrite_and_save_canonically(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            memory.ensure_data_dir()
            program_path = memory.program_file("legacy-actions")
            legacy = {
                "program_id": "legacy-actions",
                "program_name": "Legacy Actions",
                "description": "Normalize stored actions.",
                "next_actions": [
                    "Confirm rollout cohort",
                    {
                        "action": "Review support model",
                        "status": "Open",
                        "owner": "Operations",
                        "due_date": "2026-08-01",
                    },
                ],
            }
            program_path.write_text(json.dumps(legacy, indent=2), encoding="utf-8")
            before = program_path.read_text(encoding="utf-8")

            try:
                first = memory.load_program("legacy-actions")
                second = memory.load_program("legacy-actions")

                self.assertEqual(program_path.read_text(encoding="utf-8"), before)
                self.assertEqual(first, second)
                self.assertEqual(first["schema_version"], CURRENT_SCHEMA_VERSION)
                self.assertEqual(first["next_actions"][0]["object_type"], "action")
                self.assertEqual(first["next_actions"][0]["title"], "Confirm rollout cohort")
                self.assertEqual(first["next_actions"][1]["owner"]["display_name"], "Operations")

                memory.save_program(first)
                saved = json.loads(program_path.read_text(encoding="utf-8"))
                self.assertEqual(saved["next_actions"], first["next_actions"])
                self.assertEqual(saved["relationships"], [])
                self.assertNotIn("action_id", saved["next_actions"][0])
            finally:
                memory.DATA_DIR = original_data_dir

    def test_create_save_and_reload_program_in_temporary_directory(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            try:
                program = memory.create_program(
                    "Payments Modernization",
                    "Modernize payment processing for enterprise customers.",
                )
                program["health"] = "Yellow"
                program["issues"].append({
                    "description": "Vendor API contract is not finalized.",
                    "owner": "Integration Lead",
                    "due_date": "2026-08-01",
                    "status": "Open",
                })

                memory.save_program(program)
                reloaded = memory.load_program(program["program_id"])

                self.assertIsNotNone(reloaded)
                self.assertEqual(reloaded["program_id"], "payments-modernization")
                self.assertEqual(reloaded["program_name"], "Payments Modernization")
                self.assertEqual(
                    reloaded["description"],
                    "Modernize payment processing for enterprise customers.",
                )
                self.assertEqual(reloaded["phase"], "Program Initiation")
                self.assertEqual(reloaded["health"], "Yellow")
                self.assertEqual(reloaded["confidence"], "Medium")
                self.assertEqual(reloaded["schema_version"], CURRENT_SCHEMA_VERSION)
                self.assertIn("metadata", reloaded)
                self.assertEqual(len(reloaded["issues"]), 1)
                self.assertEqual(reloaded["issues"][0]["owner"], "Integration Lead")
            finally:
                memory.DATA_DIR = original_data_dir

    def test_load_legacy_program_normalizes_without_rewriting_source_file(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            memory.ensure_data_dir()
            program_path = memory.program_file("legacy-program")
            legacy_json = """{
  "program_id": "legacy-program",
  "program_name": "Legacy Program",
  "description": "Older record.",
  "issues": [
    {
      "description": "Legacy issue without owner or due date.",
      "status": "Open"
    }
  ]
}"""
            program_path.write_text(legacy_json, encoding="utf-8")
            before = program_path.read_text(encoding="utf-8")

            try:
                loaded = memory.load_program("legacy-program")
                after = program_path.read_text(encoding="utf-8")

                self.assertEqual(before, after)
                self.assertEqual(loaded["schema_version"], CURRENT_SCHEMA_VERSION)
                self.assertEqual(loaded["meeting_history"], [])
                self.assertEqual(loaded["documents"], [])
                self.assertEqual(loaded["artifacts"], [])
                self.assertEqual(loaded["relationships"], [])
                self.assertEqual(loaded["metadata"]["source"], "cli")
                self.assertNotIn("owner", loaded["issues"][0])
                self.assertNotIn("due_date", loaded["issues"][0])
            finally:
                memory.DATA_DIR = original_data_dir

    def test_save_program_writes_schema_updates_timestamp_and_preserves_created_at(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            created_at = "2026-01-01T00:00:00+00:00"
            first_updated = "2026-01-02T00:00:00+00:00"
            second_updated = "2026-01-03T00:00:00+00:00"
            program = {
                "program_id": "save-behavior",
                "program_name": "Save Behavior",
                "description": "Validate save metadata.",
                "phase": "Program Initiation",
                "health": "Unknown",
                "confidence": "Medium",
                "risks": [],
                "issues": [],
                "decisions": [],
                "next_actions": [],
                "meeting_history": [],
                "documents": [],
                "artifacts": [],
                "relationships": [],
                "metadata": {
                    "created_at": created_at,
                    "updated_at": first_updated,
                    "source": "cli",
                },
            }

            try:
                with patch("memory.utc_timestamp", return_value=second_updated):
                    memory.save_program(program)

                reloaded = memory.load_program("save-behavior")

                self.assertEqual(reloaded["schema_version"], CURRENT_SCHEMA_VERSION)
                self.assertEqual(reloaded["metadata"]["created_at"], created_at)
                self.assertEqual(reloaded["metadata"]["updated_at"], second_updated)
            finally:
                memory.DATA_DIR = original_data_dir

    def test_save_legacy_program_syncs_in_memory_created_at_after_write(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            created_at = "2026-02-01T00:00:00+00:00"
            first_updated_at = "2026-02-01T00:01:00+00:00"
            second_updated_at = "2026-02-01T00:02:00+00:00"
            program = {
                "program_id": "legacy-sync",
                "program_name": "Legacy Sync",
                "description": "Legacy in-memory record.",
                "metadata": {
                    "updated_at": None,
                    "source": "cli",
                },
            }

            self.assertNotIn("created_at", program["metadata"])

            try:
                with patch(
                    "memory.utc_timestamp",
                    side_effect=[created_at, first_updated_at, second_updated_at],
                ):
                    memory.save_program(program)

                    self.assertEqual(program["metadata"]["created_at"], created_at)
                    first_created_at = program["metadata"]["created_at"]

                    memory.save_program(program)

                self.assertEqual(program["metadata"]["created_at"], first_created_at)
                self.assertEqual(program["metadata"]["updated_at"], second_updated_at)
                datetime.fromisoformat(program["metadata"]["updated_at"])
                self.assertEqual(program["schema_version"], CURRENT_SCHEMA_VERSION)
                self.assertEqual(program["phase"], "Program Initiation")
                self.assertEqual(program["health"], "Unknown")
                self.assertEqual(program["confidence"], "Medium")
                self.assertEqual(program["risks"], [])
                self.assertEqual(program["issues"], [])
                self.assertEqual(program["decisions"], [])
                self.assertEqual(program["next_actions"], [])
                self.assertEqual(program["meeting_history"], [])
                self.assertEqual(program["documents"], [])
                self.assertEqual(program["artifacts"], [])
                self.assertEqual(program["relationships"], [])

                with open(memory.program_file("legacy-sync"), "r", encoding="utf-8") as f:
                    saved = json.load(f)

                self.assertEqual(saved, program)
            finally:
                memory.DATA_DIR = original_data_dir

    def test_save_invalid_program_fails_clearly(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"

            try:
                with self.assertRaisesRegex(ValueError, "program_id must be a non-empty string"):
                    memory.save_program({
                        "program_id": "",
                        "program_name": "Invalid",
                        "description": "Missing usable id.",
                    })
            finally:
                memory.DATA_DIR = original_data_dir


if __name__ == "__main__":
    unittest.main()
