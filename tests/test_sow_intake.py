import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import memory
import router
import sow_intake


ANALYSIS_RESPONSE = json.dumps({
    "program_name": "Demo Program",
    "customer_name": "Example Customer",
    "business_objective": "Deliver the contracted demo scope.",
    "program_type": "Implementation",
    "products_or_services": ["Example Service"],
    "risks": ["Inferred: acceptance criteria need validation."],
    "missing_critical_information": ["Named acceptance authority"],
    "recommended_next_action": "Internal Technical Kickoff",
    "confidence": "Medium",
})


class SOWIntakeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.original_data_dir = memory.DATA_DIR
        self.temp_dir = tempfile.TemporaryDirectory()
        memory.DATA_DIR = Path(self.temp_dir.name) / "programs"

    def tearDown(self):
        memory.DATA_DIR = self.original_data_dir
        self.temp_dir.cleanup()

    def test_success_uses_one_gemini_call_one_routing_result_and_temp_storage(self):
        extraction = {
            "text": "Small synthetic SOW fixture.",
            "metadata": {"source_filename": "fixture.pdf", "truncated": False},
        }
        routing = {
            "primary_persona": "technical_program_manager",
            "supporting_personas": ["cloud_architect"],
            "reasons": ["Technical context."],
            "routing_version": "test",
        }
        with patch("sow_intake.extract_pdf_text", return_value=extraction), \
            patch("sow_intake.generate_response", return_value=ANALYSIS_RESPONSE) as generate, \
            patch("sow_intake.calculate_persona_routing", return_value=(routing, False)) as calculate, \
            patch("sow_intake.display_persona_routing") as display:
            program, analysis, returned_routing = sow_intake.create_program_from_sow("fixture.pdf")

        generate.assert_called_once()
        calculate.assert_called_once()
        display.assert_called_once_with(routing, fallback_used=False)
        self.assertIs(returned_routing, routing)
        self.assertEqual(analysis["source_filename"], "fixture.pdf")
        self.assertTrue(memory.program_file(program["program_id"]).exists())

    def test_failure_before_save_creates_no_program(self):
        extraction = {
            "text": "Synthetic fixture.",
            "metadata": {"source_filename": "fixture.pdf", "truncated": False},
        }
        with patch("sow_intake.extract_pdf_text", return_value=extraction), \
            patch("sow_intake.generate_response", return_value="not json"):
            with self.assertRaisesRegex(sow_intake.SOWIntakeError, "Invalid Gemini"):
                sow_intake.create_program_from_sow("fixture.pdf")
        self.assertFalse(memory.DATA_DIR.exists())

    def test_manual_new_program_path_is_preserved(self):
        program = {
            "program_id": "manual", "program_name": "Manual", "description": "Manual input",
            "phase": "Program Initiation", "health": "Unknown", "confidence": "Medium",
            "risks": [], "issues": [], "decisions": [], "next_actions": [],
        }
        routing = {"primary_persona": "technical_program_manager", "supporting_personas": [], "reasons": []}
        with patch("builtins.input", side_effect=["1", "Manual input", "Manual"]), \
            patch("router.create_program", return_value=program), \
            patch("router.calculate_persona_routing", return_value=(routing, False)), \
            patch("router.display_persona_routing"), \
            patch("router.analyze_new_program") as analyze:
            router.route("1")
        analyze.assert_called_once_with("Manual input", persona_routing=routing)

    def test_sow_menu_delegates_without_exposing_path(self):
        with patch("builtins.input", side_effect=["2", "/temporary path/demo.pdf"]), \
            patch("router.create_program_from_sow") as create:
            router.route("1")
        create.assert_called_once_with("/temporary path/demo.pdf")


if __name__ == "__main__":
    unittest.main()
