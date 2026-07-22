import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import memory
from program_domain import create_issue
from schema import apply_compatibility_defaults
from workspace import (
    add_action,
    add_decision,
    add_issue,
    add_risk,
    close_issue,
    display_open_issues,
    get_open_issues,
)


class WorkspaceIssueHelperTests(unittest.TestCase):
    def test_get_open_issues_returns_only_open_issues(self):
        program = {
            "issues": [
                create_issue("Open issue").to_dict(),
                create_issue("Closed issue", status="closed").to_dict(),
                create_issue("Resolved issue", status="resolved").to_dict(),
            ]
        }

        open_issues = get_open_issues(program)

        self.assertEqual(len(open_issues), 1)
        self.assertEqual(open_issues[0]["title"], "Open issue")

    def test_display_open_issues_handles_legacy_issue_without_owner_or_due_date(self):
        open_issues = [create_issue("Legacy issue without optional fields").to_dict()]

        output = io.StringIO()
        with redirect_stdout(output):
            display_open_issues(open_issues)

        rendered = output.getvalue()
        self.assertIn("Legacy issue without optional fields", rendered)
        self.assertIn("Owner   : Not assigned", rendered)
        self.assertIn("Due date: Not defined", rendered)
        self.assertIn("Status  : open", rendered)

    def test_new_workspace_items_receive_stable_ids(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            program = memory.create_program(
                "Workspace IDs",
                "Validate stable IDs for new workspace records.",
            )

            try:
                with patch("builtins.input", return_value="Risk description"):
                    add_risk(program)

                with patch(
                    "builtins.input",
                    side_effect=[
                        "Issue description",
                        "Issue Owner",
                        "2026-08-01",
                        "",
                    ],
                ):
                    add_issue(program)

                with patch("builtins.input", return_value="Decision description"):
                    add_decision(program)

                with patch("builtins.input", return_value="Action description"):
                    add_action(program)

                self.assertEqual(program["risks"][0]["object_type"], "risk")
                self.assertEqual(UUID(program["risks"][0]["object_id"]).version, 4)
                self.assertEqual(program["issues"][0]["object_type"], "issue")
                self.assertEqual(UUID(program["issues"][0]["object_id"]).version, 4)
                self.assertEqual(program["issues"][0]["owner"]["display_name"], "Issue Owner")
                self.assertTrue(
                    program["decisions"][0]["decision_id"].startswith("decision-")
                )
                self.assertEqual(program["next_actions"][0]["object_type"], "action")
                self.assertRegex(
                    program["next_actions"][0]["object_id"],
                    r"^[0-9a-f-]{36}$",
                )
            finally:
                memory.DATA_DIR = original_data_dir

    def test_legacy_issue_without_issue_id_can_still_be_closed(self):
        original_data_dir = memory.DATA_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            memory.DATA_DIR = Path(temp_dir) / "programs"
            program = memory.create_program(
                "Legacy Issue Close",
                "Validate closing legacy issues.",
            )
            program["issues"].append({
                "description": "Legacy issue without id.",
                "status": "Open",
            })
            program = apply_compatibility_defaults(program)
            object_id = program["issues"][0]["object_id"]

            try:
                with patch("builtins.input", side_effect=["1", "Access restored", ""]), \
                     patch("workspace.utc_timestamp", return_value="2026-07-22T12:00:00+00:00"):
                    close_issue(program)

                self.assertEqual(program["issues"][0]["status"], "closed")
                self.assertEqual(program["issues"][0]["object_id"], object_id)
                self.assertEqual(program["issues"][0]["resolution_summary"], "Access restored")
                self.assertEqual(program["issues"][0]["resolved_at"], "2026-07-22T12:00:00+00:00")
            finally:
                memory.DATA_DIR = original_data_dir

    def test_invalid_close_selection_does_not_mutate_canonical_issue(self):
        issue = create_issue("Do not close", owner="Owner", due_date="2026-08-01").to_dict()
        program = {"issues": [issue]}
        original = dict(issue)
        with patch("builtins.input", side_effect=["9", ""]):
            close_issue(program)
        self.assertEqual(program["issues"][0], original)


if __name__ == "__main__":
    unittest.main()
