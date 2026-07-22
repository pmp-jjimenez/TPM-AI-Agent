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
                {"description": "Open issue", "status": "Open"},
                {"description": "Closed issue", "status": "Closed"},
                {"description": "Lowercase status issue", "status": "open"},
            ]
        }

        open_issues = get_open_issues(program)

        self.assertEqual(len(open_issues), 1)
        self.assertEqual(open_issues[0][0], 0)
        self.assertEqual(open_issues[0][1]["description"], "Open issue")

    def test_display_open_issues_handles_legacy_issue_without_owner_or_due_date(self):
        open_issues = [
            (0, {"description": "Legacy issue without optional fields", "status": "Open"})
        ]

        output = io.StringIO()
        with redirect_stdout(output):
            display_open_issues(open_issues)

        rendered = output.getvalue()
        self.assertIn("Legacy issue without optional fields", rendered)
        self.assertIn("Owner   : Not assigned", rendered)
        self.assertIn("Due date: Not defined", rendered)
        self.assertIn("Status  : Open", rendered)

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
                self.assertTrue(program["issues"][0]["issue_id"].startswith("issue-"))
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

            try:
                with patch("builtins.input", side_effect=["1", ""]):
                    close_issue(program)

                self.assertEqual(program["issues"][0]["status"], "Closed")
                self.assertNotIn("issue_id", program["issues"][0])
            finally:
                memory.DATA_DIR = original_data_dir


if __name__ == "__main__":
    unittest.main()
