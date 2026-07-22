import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from prompt_builder import build_sow_analysis_prompt
from sow_analysis import SOWAnalysisError, map_analysis_to_program, parse_sow_analysis


def valid_response():
    return {
        "program_name": "Platform Enablement",
        "customer_name": "Example Customer",
        "business_objective": "Enable a supported platform rollout.",
        "risks": ["Inferred: acceptance ownership is unclear."],
        "recommended_next_action": "Internal Technical Kickoff",
        "confidence": "High",
    }


class SOWPromptTests(unittest.TestCase):
    def test_prompt_requests_bounded_factual_strict_json_analysis(self):
        prompt = build_sow_analysis_prompt("Bounded fixture text", "fixture.pdf", True)
        self.assertIn("contractual and scoping document", prompt)
        self.assertIn("factual extraction", prompt)
        self.assertIn("Return strict JSON only", prompt)
        self.assertIn("Bounded fixture text", prompt)
        self.assertIn("truncated", prompt)
        self.assertIn("Internal Technical Kickoff", prompt)
        self.assertIn("Do not expose chain-of-thought", prompt)
        self.assertIn("Do not simulate autonomous agents", prompt)
        self.assertNotIn("Multiple autonomous agents analyzed", prompt)


class SOWAnalysisParsingTests(unittest.TestCase):
    def test_valid_json_and_missing_optional_fields_are_normalized(self):
        parsed = parse_sow_analysis(json.dumps(valid_response()), "fixture.pdf")
        self.assertEqual(parsed["program_name"], "Platform Enablement")
        self.assertEqual(parsed["deliverables"], [])
        self.assertEqual(parsed["document_title"], "")
        self.assertEqual(parsed["source_filename"], "fixture.pdf")

    def test_code_fenced_json_is_accepted(self):
        response = "```json\n" + json.dumps(valid_response()) + "\n```"
        self.assertEqual(parse_sow_analysis(response)["customer_name"], "Example Customer")

    def test_invalid_json_is_rejected(self):
        with self.assertRaisesRegex(SOWAnalysisError, "invalid JSON"):
            parse_sow_analysis("not json")

    def test_incorrect_field_type_is_rejected(self):
        response = valid_response()
        response["risks"] = "not a list"
        with self.assertRaisesRegex(SOWAnalysisError, "risks.*list"):
            parse_sow_analysis(json.dumps(response))

    def test_confidence_representations_are_normalized(self):
        cases = (
            ("HIGH", "High"),
            (0.85, "High"),
            (85, "High"),
            ({"score": 0.55}, "Medium"),
            ({"level": "low"}, "Low"),
            (["unsupported"], "Medium"),
        )
        for confidence, expected in cases:
            with self.subTest(confidence=confidence):
                response = valid_response()
                response["confidence"] = confidence
                parsed = parse_sow_analysis(json.dumps(response))
                self.assertEqual(parsed["confidence"], expected)

    def test_non_confidence_string_field_with_incorrect_type_is_rejected(self):
        response = valid_response()
        response["program_name"] = 123
        with self.assertRaisesRegex(SOWAnalysisError, "program_name.*string"):
            parse_sow_analysis(json.dumps(response))


class SOWProgramMappingTests(unittest.TestCase):
    def test_maps_canonical_fields_ids_risks_and_actions_without_mutation(self):
        analysis = parse_sow_analysis(json.dumps({
            **valid_response(),
            "open_questions": ["Who approves acceptance?"],
            "missing_critical_information": ["Production capacity"],
            "source_filename": "fixture.pdf",
        }))
        before = deepcopy(analysis)
        program = map_analysis_to_program(analysis)

        self.assertEqual(analysis, before)
        self.assertEqual(program["phase"], "Program Initiation")
        self.assertEqual(program["health"], "Unknown")
        self.assertEqual(program["customer"], "Example Customer")
        self.assertEqual(program["description"], "Enable a supported platform rollout.")
        self.assertEqual(program["confidence"], "High")
        self.assertTrue(program["risks"][0]["risk_id"].startswith("risk-"))
        self.assertTrue(all(item["object_type"] == "action" for item in program["next_actions"]))
        self.assertTrue(all(len(item["object_id"]) == 36 for item in program["next_actions"]))
        self.assertTrue(all(item["audit"]["source"] == "sow_analysis" for item in program["next_actions"]))
        self.assertEqual(program["documents"][0]["filename"], "fixture.pdf")
        self.assertNotIn("path", program["documents"][0])


if __name__ == "__main__":
    unittest.main()
