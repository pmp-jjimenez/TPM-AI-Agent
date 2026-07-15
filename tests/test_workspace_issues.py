import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from workspace import display_open_issues, get_open_issues


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


if __name__ == "__main__":
    unittest.main()
