import tempfile
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import executive


class ExecutiveReportTests(unittest.TestCase):
    def test_generate_executive_report_in_temporary_directory(self):
        original_report_dir = executive.REPORT_DIR

        with tempfile.TemporaryDirectory() as temp_dir:
            executive.REPORT_DIR = Path(temp_dir) / "executive"
            try:
                program = {
                    "program_id": "payments-modernization",
                    "program_name": "Payments Modernization",
                    "phase": "Execution",
                    "health": "Red",
                    "confidence": "Medium",
                    "risks": [
                        {"description": "Cutover window may be missed."},
                    ],
                    "issues": [
                        {"description": "API defect blocks testing.", "status": "Open"},
                        {"description": "Vendor decision is delayed.", "status": "Open"},
                    ],
                    "decisions": [],
                    "next_actions": [],
                }

                report_path = executive.generate_executive_report(program)
                report = report_path.read_text(encoding="utf-8")

                self.assertTrue(report_path.exists())
                self.assertIn("Payments Modernization", report)
                self.assertIn("Red", report)
                self.assertIn("Cutover window may be missed.", report)
                self.assertIn("Open Issues: 2", report)
            finally:
                executive.REPORT_DIR = original_report_dir


if __name__ == "__main__":
    unittest.main()
