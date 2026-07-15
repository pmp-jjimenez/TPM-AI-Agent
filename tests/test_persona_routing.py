import io
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import persona_routing
import persona_router
import router


class PersonaRoutingPresentationTests(unittest.TestCase):
    def test_render_displays_human_readable_primary_supporting_and_reasons(self):
        routing = {
            "primary_persona": "technical_program_manager",
            "supporting_personas": ["cloud_architect", "security_advisor"],
            "reasons": [
                "Cloud or infrastructure context added Cloud Architect.",
                "Security or compliance context added Security Advisor.",
            ],
            "routing_version": "test",
        }

        rendered = persona_routing.render_persona_routing(routing)

        self.assertIn("Persona Routing", rendered)
        self.assertIn("Technical Program Manager", rendered)
        self.assertIn("- Cloud Architect", rendered)
        self.assertIn("- Security Advisor", rendered)
        self.assertIn("Cloud or infrastructure context", rendered)
        self.assertIn("Security or compliance context", rendered)

    def test_render_handles_empty_supporting_personas(self):
        routing = {
            "primary_persona": "technical_program_manager",
            "supporting_personas": [],
            "reasons": [],
            "routing_version": "test",
        }

        rendered = persona_routing.render_persona_routing(routing)

        self.assertIn("Supporting Personas:", rendered)
        self.assertIn("- None", rendered)
        self.assertIn("Routing Reasons:", rendered)

    def test_render_unknown_persona_id_does_not_crash(self):
        routing = {
            "primary_persona": "unknown_specialist",
            "supporting_personas": ["another_unknown_persona"],
            "reasons": ["Unknown persona was returned by a future router."],
            "routing_version": "test",
        }

        rendered = persona_routing.render_persona_routing(routing)

        self.assertIn("Unknown Specialist", rendered)
        self.assertIn("Another Unknown Persona", rendered)

    def test_display_writes_rendered_output(self):
        routing = {
            "primary_persona": "technical_program_manager",
            "supporting_personas": [],
            "reasons": [],
            "routing_version": "test",
        }

        output = io.StringIO()
        with redirect_stdout(output):
            persona_routing.display_persona_routing(routing)

        self.assertIn("Technical Program Manager", output.getvalue())


class PersonaRoutingIntegrationTests(unittest.TestCase):
    def test_empty_program_collection_keys_do_not_create_supporting_personas(self):
        routing = persona_router.route_personas({
            "workflow_name": "active_program_workspace",
            "program": {
                "risks": [],
                "issues": [],
                "decisions": [],
                "next_actions": [],
            },
        })

        self.assertEqual(routing["primary_persona"], "technical_program_manager")
        self.assertEqual(routing["supporting_personas"], [])

    def test_new_program_routes_once_and_passes_same_result_to_display_and_prompt(self):
        routing = {
            "primary_persona": "technical_program_manager",
            "supporting_personas": ["cloud_architect"],
            "reasons": ["Cloud context."],
            "routing_version": "test",
        }
        program = {
            "program_id": "cloud-program",
            "program_name": "Cloud Program",
            "description": "Azure migration.",
            "phase": "Program Initiation",
            "health": "Unknown",
            "risks": [],
            "issues": [],
            "decisions": [],
            "next_actions": [],
        }

        with patch("builtins.input", side_effect=["Azure migration", "Cloud Program"]), \
            patch("router.create_program", return_value=program), \
            patch("router.calculate_persona_routing", return_value=(routing, False)) as calculate, \
            patch("router.display_persona_routing") as display, \
            patch("router.analyze_new_program") as analyze:

            router.route("1")

        calculate.assert_called_once()
        display.assert_called_once_with(routing, fallback_used=False)
        analyze.assert_called_once_with("Azure migration", persona_routing=routing)
        self.assertEqual(calculate.call_args.kwargs["workflow_name"], "program_initiation")
        self.assertIn("initiation", calculate.call_args.kwargs["extra_signals"])

    def test_major_incident_supplies_incident_signal(self):
        routing = persona_routing.fallback_persona_routing()

        with patch("router.calculate_persona_routing", return_value=(routing, False)) as calculate, \
            patch("router.display_persona_routing"):

            router.route("3")

        calculate.assert_called_once()
        self.assertEqual(calculate.call_args.kwargs["workflow_name"], "major_incident")
        self.assertIn("incident", calculate.call_args.kwargs["extra_signals"])

    def test_executive_review_supplies_executive_signal(self):
        routing = persona_routing.fallback_persona_routing()

        with patch("router.calculate_persona_routing", return_value=(routing, False)) as calculate, \
            patch("router.display_persona_routing"):

            router.route("4")

        calculate.assert_called_once()
        self.assertEqual(calculate.call_args.kwargs["workflow_name"], "executive_review")
        self.assertIn("executive", calculate.call_args.kwargs["extra_signals"])

    def test_operational_readiness_supplies_readiness_signal(self):
        routing = persona_routing.fallback_persona_routing()

        with patch("router.calculate_persona_routing", return_value=(routing, False)) as calculate, \
            patch("router.display_persona_routing"):

            router.route("5")

        calculate.assert_called_once()
        self.assertEqual(calculate.call_args.kwargs["workflow_name"], "operational_readiness")
        self.assertIn("operational readiness", calculate.call_args.kwargs["extra_signals"])

    def test_active_program_routing_uses_selected_program_context(self):
        routing = persona_routing.fallback_persona_routing()
        program = {
            "program_id": "active-program",
            "program_name": "Active Program",
            "description": "Security compliance rollout.",
            "phase": "Execution",
            "health": "Yellow",
            "risks": [{"description": "Audit risk"}],
            "issues": [],
            "decisions": [],
            "next_actions": [],
        }

        with patch("builtins.input", return_value="1"), \
            patch("router.list_programs", return_value=[program]), \
            patch("router.calculate_persona_routing", return_value=(routing, False)) as calculate, \
            patch("router.display_persona_routing"), \
            patch("router.open_workspace") as open_workspace:

            router.route("2")

        calculate.assert_called_once()
        self.assertIs(calculate.call_args.kwargs["program"], program)
        open_workspace.assert_called_once_with("active-program")

    def test_router_failure_returns_safe_fallback(self):
        with patch("persona_routing.route_personas", side_effect=RuntimeError("boom")):
            routing, fallback_used = persona_routing.calculate_persona_routing(
                menu_mode="Major Incident",
                workflow_name="major_incident",
                user_request="Incident",
            )

        self.assertTrue(fallback_used)
        self.assertEqual(routing["primary_persona"], "technical_program_manager")
        self.assertEqual(routing["supporting_personas"], [])
        self.assertIn("default Technical Program Manager", routing["reasons"][0])
        self.assertIn("routing_version", routing)

    def test_build_routing_context_does_not_mutate_input_program_data(self):
        program = {
            "program_id": "immutability",
            "program_name": "Immutability",
            "risks": [{"description": "Original risk"}],
            "issues": [],
            "decisions": [],
            "next_actions": [],
        }
        original = deepcopy(program)

        context = persona_routing.build_routing_context(
            menu_mode="Manage Active Program",
            workflow_name="active_program_workspace",
            program=program,
        )
        context["program"]["risks"][0]["description"] = "Changed in context"

        self.assertEqual(program, original)


if __name__ == "__main__":
    unittest.main()
