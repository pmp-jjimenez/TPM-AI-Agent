import copy
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from persona_router import (
    CHANGE_MANAGER,
    CLOUD_ARCHITECT,
    CUSTOMER_SUCCESS_ADVISOR,
    DELIVERY_MANAGER,
    EXECUTIVE_ADVISOR,
    INCIDENT_COMMANDER,
    OPERATIONS_MANAGER,
    ROUTING_VERSION,
    SECURITY_ADVISOR,
    TECHNICAL_PROGRAM_MANAGER,
    route_personas,
)


class PersonaRouterTests(unittest.TestCase):
    def test_default_routing_uses_technical_program_manager(self):
        result = route_personas({})

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [])
        self.assertEqual(result["routing_version"], ROUTING_VERSION)
        self.assertTrue(result["reasons"])

    def test_new_program_routing_uses_technical_program_manager(self):
        result = route_personas({
            "phase": "Program Initiation",
            "description": "Start a new program for finance modernization.",
        })

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [])
        self.assertIn("New program", result["reasons"][0])

    def test_cloud_program_adds_cloud_architect(self):
        result = route_personas({
            "program_type": "Cloud migration",
            "description": "Move workloads to Azure infrastructure.",
        })

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [CLOUD_ARCHITECT])

    def test_major_incident_routing_uses_incident_commander(self):
        result = route_personas(
            {"issues": [{"description": "P1 outage causing service disruption."}]},
            requested_mode="major incident mode",
        )

        self.assertEqual(result["primary_persona"], INCIDENT_COMMANDER)
        self.assertEqual(
            result["supporting_personas"],
            [TECHNICAL_PROGRAM_MANAGER, OPERATIONS_MANAGER],
        )

    def test_sow_program_incident_escalation_and_sla_keeps_tpm_primary(self):
        result = route_personas(
            {
                "risks": ["Incident escalation procedures must meet the SLA."],
            },
            requested_mode="Start New Program",
            workflow="sow_program_initiation",
            user_request="Support scope includes outage escalation responsibilities.",
        )

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)

    def test_sow_cloud_program_keeps_cloud_architect_supporting(self):
        result = route_personas(
            {
                "description": "Cloud architecture implementation on Azure.",
                "risks": ["Incident escalation must comply with the SLA."],
            },
            requested_mode="Start New Program",
            workflow="sow_program_initiation",
        )

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [CLOUD_ARCHITECT])

    def test_explicit_major_incident_workflow_still_uses_incident_commander(self):
        result = route_personas(
            requested_mode="Major Incident",
            workflow="major_incident",
        )

        self.assertEqual(result["primary_persona"], INCIDENT_COMMANDER)

    def test_executive_review_routing_uses_executive_advisor(self):
        result = route_personas(
            {"health": "Yellow"},
            workflow="Executive Review",
            user_request="Prepare executive reporting for the steering committee.",
        )

        self.assertEqual(result["primary_persona"], EXECUTIVE_ADVISOR)
        self.assertEqual(result["supporting_personas"], [TECHNICAL_PROGRAM_MANAGER])

    def test_operational_readiness_routing_uses_operations_manager(self):
        result = route_personas({
            "phase": "Go-live readiness",
            "next_actions": ["Complete handoff package and ORR checklist."],
        })

        self.assertEqual(result["primary_persona"], OPERATIONS_MANAGER)
        self.assertEqual(result["supporting_personas"], [TECHNICAL_PROGRAM_MANAGER])

    def test_security_risk_adds_security_advisor(self):
        result = route_personas({
            "risks": [
                {
                    "description": "Security compliance risk for customer data privacy.",
                    "status": "Open",
                }
            ],
        })

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [SECURITY_ADVISOR])

    def test_change_and_adoption_adds_change_manager(self):
        result = route_personas({
            "next_actions": [
                {"description": "Create training and communications plan for adoption."}
            ],
        })

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [CHANGE_MANAGER])

    def test_customer_success_routing_adds_customer_success_advisor(self):
        result = route_personas(
            {"description": "Address customer escalation and retention risk."}
        )

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [CUSTOMER_SUCCESS_ADVISOR])

    def test_delivery_pressure_adds_delivery_manager(self):
        result = route_personas({
            "issues": ["Milestone slippage due to dependency coordination blocker."],
        })

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [DELIVERY_MANAGER])

    def test_multiple_simultaneous_routing_signals_are_ordered(self):
        result = route_personas(
            {
                "program_type": "Cloud migration",
                "risks": ["Security compliance risk."],
                "issues": ["Milestone slippage and dependency pressure."],
            },
            workflow="Executive Review",
            user_request="Include customer escalation, adoption outcome, and training.",
        )

        self.assertEqual(result["primary_persona"], EXECUTIVE_ADVISOR)
        self.assertEqual(
            result["supporting_personas"],
            [
                TECHNICAL_PROGRAM_MANAGER,
                CLOUD_ARCHITECT,
                SECURITY_ADVISOR,
                CHANGE_MANAGER,
                CUSTOMER_SUCCESS_ADVISOR,
                DELIVERY_MANAGER,
            ],
        )

    def test_no_duplicate_personas(self):
        result = route_personas({
            "description": "Cloud cloud cloud migration with AWS infrastructure.",
            "risks": ["Security security privacy compliance."],
        })

        self.assertEqual(
            len(result["supporting_personas"]),
            len(set(result["supporting_personas"])),
        )

    def test_primary_persona_is_excluded_from_supporting_personas(self):
        result = route_personas({
            "phase": "Operational readiness",
            "next_actions": ["Go-live readiness and handoff."],
        })

        self.assertEqual(result["primary_persona"], OPERATIONS_MANAGER)
        self.assertNotIn(
            result["primary_persona"],
            result["supporting_personas"],
        )

    def test_stable_ordering_for_incident_with_other_signals(self):
        result = route_personas(
            {
                "description": "Cloud outage with security concern.",
                "issues": ["P1 service disruption and dependency coordination."],
            },
            workflow="executive review",
        )

        self.assertEqual(result["primary_persona"], INCIDENT_COMMANDER)
        self.assertEqual(
            result["supporting_personas"],
            [
                TECHNICAL_PROGRAM_MANAGER,
                OPERATIONS_MANAGER,
                CLOUD_ARCHITECT,
                EXECUTIVE_ADVISOR,
                SECURITY_ADVISOR,
                DELIVERY_MANAGER,
            ],
        )

    def test_missing_and_legacy_fields_are_tolerated(self):
        legacy = {
            "program_name": "Legacy Program",
            "risks": "not a canonical list",
            "legacy_notes": ["Privacy review required."],
        }

        result = route_personas(legacy)

        self.assertEqual(result["primary_persona"], TECHNICAL_PROGRAM_MANAGER)
        self.assertEqual(result["supporting_personas"], [SECURITY_ADVISOR])

    def test_output_is_deterministic(self):
        context = {
            "description": "Azure migration with executive report and compliance risk.",
            "next_actions": ["Training plan", "Dependency coordination"],
        }

        first = route_personas(context)
        second = route_personas(context)

        self.assertEqual(first, second)

    def test_input_data_is_not_mutated(self):
        context = {
            "description": "Cloud migration",
            "risks": [{"description": "Privacy compliance risk"}],
        }
        original = copy.deepcopy(context)

        route_personas(context)

        self.assertEqual(context, original)


if __name__ == "__main__":
    unittest.main()
