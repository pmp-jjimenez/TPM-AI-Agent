import tempfile
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import memory


class ProgramMemoryTests(unittest.TestCase):
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
                self.assertEqual(len(reloaded["issues"]), 1)
                self.assertEqual(reloaded["issues"][0]["owner"], "Integration Lead")
            finally:
                memory.DATA_DIR = original_data_dir


if __name__ == "__main__":
    unittest.main()
