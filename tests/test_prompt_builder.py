import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from prompt_builder import build_new_program_prompt


class PromptBuilderTests(unittest.TestCase):
    def test_prompt_includes_project_context_and_expected_sections(self):
        project_description = "Deploy Microsoft Teams across LATAM business units."
        tpm_context = "TPM context: use RAID discipline and confidence scoring."

        prompt = build_new_program_prompt(project_description, tpm_context)

        self.assertIn(project_description, prompt)
        self.assertIn(tpm_context, prompt)
        self.assertIn("TPM OS CONTEXT", prompt)
        self.assertIn("USER PROJECT", prompt)
        self.assertIn("Current Program Phase", prompt)
        self.assertIn("Missing Information", prompt)
        self.assertIn("Initial Risks", prompt)
        self.assertIn("Recommended Playbooks", prompt)
        self.assertIn("Initial Deliverables", prompt)
        self.assertIn("Next Recommended Action", prompt)
        self.assertIn("Confidence Level", prompt)
        self.assertIn("Reason for Confidence", prompt)

    def test_prompt_builder_includes_optional_persona_routing_context(self):
        routing = {
            "primary_persona": "technical_program_manager",
            "supporting_personas": ["cloud_architect", "security_advisor"],
            "reasons": [
                "Cloud or infrastructure context added Cloud Architect.",
                "Security or compliance context added Security Advisor.",
            ],
            "routing_version": "test",
        }

        prompt = build_new_program_prompt(
            "Deploy secure cloud infrastructure.",
            "TPM context.",
            persona_routing=routing,
        )

        self.assertIn("PERSONA ROUTING CONTEXT", prompt)
        self.assertIn("Primary persona:", prompt)
        self.assertIn("Technical Program Manager", prompt)
        self.assertIn("- Cloud Architect", prompt)
        self.assertIn("- Security Advisor", prompt)
        self.assertIn("Cloud or infrastructure context", prompt)
        self.assertIn("Security or compliance context", prompt)
        self.assertIn("Do not claim that independent autonomous agents were executed.", prompt)
        self.assertNotIn("Multiple agents were executed", prompt)


if __name__ == "__main__":
    unittest.main()
