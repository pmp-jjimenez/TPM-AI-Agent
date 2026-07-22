import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.compat import APPLICATION_VERSION, memory
from backend.api.dependencies import get_intelligence_service, get_program_reader
from backend.api.main import app


CONTROLLED_PROGRAM = {
    "schema_version": "1.3.0",
    "program_id": "controlled-program",
    "program_name": "Controlled Program",
    "description": "Program fixture isolated from repository persistence.",
    "customer": "Test Customer",
    "phase": "Program Initiation",
    "health": "Green",
    "confidence": "High",
    "risks": [{
        "object_id": "22222222-2222-4222-8222-222222222222",
        "object_type": "risk", "title": "Controlled stored risk", "description": None,
        "owner": None, "lifecycle_phase": "initiation",
        "audit": {"created_at": None, "updated_at": None, "source": "legacy_import"},
        "status": "open", "probability": None, "impact": None, "priority": None,
        "mitigation_plan": None, "contingency_plan": None, "review_date": None,
        "acceptance_rationale": None, "accepted_by": None,
    }],
    "issues": [{
        "object_id": "44444444-4444-4444-8444-444444444444",
        "object_type": "issue", "title": "Controlled stored issue", "description": None,
        "owner": None, "lifecycle_phase": "initiation",
        "audit": {"created_at": None, "updated_at": None, "source": "legacy_import"},
        "status": "open", "severity": None, "impact": None, "due_date": None,
        "resolution_summary": None, "resolved_at": None, "root_cause": None,
    }],
    "decisions": [],
    "next_actions": [{
        "object_id": "11111111-1111-4111-8111-111111111111",
        "object_type": "action",
        "title": "Controlled stored action",
        "description": None,
        "owner": None,
        "lifecycle_phase": "initiation",
        "audit": {"created_at": None, "updated_at": None, "source": "legacy_import"},
        "status": "open",
        "priority": None,
        "due_date": None,
        "completed_at": None,
        "completion_summary": None,
    }],
    "meeting_history": [],
    "documents": [],
    "artifacts": [],
    "relationships": [],
    "metadata": {
        "created_at": "2026-07-17T00:00:00+00:00",
        "updated_at": "2026-07-17T00:00:00+00:00",
        "source": "test",
    },
}


class FailingProgramReader:
    def list_programs(self):
        raise OSError("private test persistence path")


class ControlledIntelligenceService:
    def generate(self, program):
        return {
            "program_id": program["program_id"],
            "schema_version": "1.0.0",
            "generated_at": "2026-07-17T12:00:00+00:00",
            "source": "ai",
            "routing": {
                "version": "1.0.0",
                "primary_persona": {"id": "technical_program_manager", "display_name": "Technical Program Manager"},
                "supporting_personas": [{"id": "delivery_manager", "display_name": "Delivery Manager"}],
            },
            "summary": "Controlled intelligence",
            "confidence": "High",
            "findings": [{"id": "fnd_1111111111111111", "category": "fact", "statement": "Controlled fact", "confidence": "High", "evidence_refs": ["/phase"]}],
            "recommendations": [{"id": "rec_2222222222222222", "priority": "High", "statement": "Controlled recommendation", "rationale": "Controlled rationale", "evidence_refs": ["/phase"], "related_finding_ids": ["fnd_1111111111111111"]}],
            "decisions_required": [{"id": "dec_3333333333333333", "priority": "Medium", "statement": "Controlled decision", "reason": "Controlled reason", "related_finding_ids": ["fnd_1111111111111111"], "related_recommendation_ids": []}],
            "next_action": {"id": "act_4444444444444444", "priority": "High", "statement": "Controlled next action", "rationale": "Controlled rationale", "related_finding_ids": ["fnd_1111111111111111"], "related_recommendation_ids": ["rec_2222222222222222"]},
            "limitations": [],
        }


class FailingIntelligenceService:
    def generate(self, _program):
        raise RuntimeError("private provider response and filesystem path")

    def load_program(self, _program_id):
        raise OSError("private test persistence path")


class APITests(unittest.TestCase):
    def setUp(self):
        self.original_data_dir = memory.DATA_DIR
        self.temp_dir = tempfile.TemporaryDirectory()
        memory.DATA_DIR = Path(self.temp_dir.name) / "programs"
        memory.create_program_data(CONTROLLED_PROGRAM)
        self.client = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        app.dependency_overrides.clear()
        memory.DATA_DIR = self.original_data_dir
        self.temp_dir.cleanup()

    def test_health_uses_shared_application_version(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "healthy", "version": APPLICATION_VERSION},
        )
        self.assertEqual(APPLICATION_VERSION, "0.2-dev")

    def test_list_programs_returns_controlled_persistence_data(self):
        response = self.client.get("/programs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [CONTROLLED_PROGRAM])

    def test_get_program_returns_controlled_persistence_data(self):
        response = self.client.get("/programs/controlled-program")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), CONTROLLED_PROGRAM)
        self.assertEqual(response.json()["risks"][0]["object_type"], "risk")

    def test_legacy_risk_transport_is_deterministic(self):
        path = memory.program_file("legacy-risk")
        path.write_text(json.dumps({
            "program_id": "legacy-risk", "program_name": "Legacy Risk",
            "description": "Compatibility fixture", "risks": ["Vendor approval may slip"],
        }), encoding="utf-8")
        first = self.client.get("/programs/legacy-risk")
        second = self.client.get("/programs/legacy-risk")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["risks"], second.json()["risks"])
        self.assertEqual(first.json()["risks"][0]["object_type"], "risk")

    def test_legacy_issue_transport_is_canonical_with_nullable_compatibility_fields(self):
        path = memory.program_file("legacy-issue")
        path.write_text(json.dumps({
            "program_id": "legacy-issue", "program_name": "Legacy Issue",
            "description": "Compatibility fixture", "issues": ["Vendor access unavailable"],
        }), encoding="utf-8")
        first = self.client.get("/programs/legacy-issue")
        second = self.client.get("/programs/legacy-issue")
        self.assertEqual(first.status_code, 200)
        issue = first.json()["issues"][0]
        self.assertEqual(issue, second.json()["issues"][0])
        self.assertEqual(issue["object_type"], "issue")
        self.assertIsNone(issue["owner"])
        self.assertIsNone(issue["due_date"])

    def test_malformed_stored_issue_returns_sanitized_error(self):
        path = memory.program_file("malformed-issue")
        path.write_text(json.dumps({
            "program_id": "malformed-issue", "program_name": "Malformed Issue",
            "description": "Invalid persisted fixture",
            "issues": [{"issue": "Issue", "due_date": "secret malformed date"}],
        }), encoding="utf-8")
        response = self.client.get("/programs/malformed-issue")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"]["code"], "program_persistence_error")
        self.assertNotIn("secret malformed date", response.text)

    def test_malformed_stored_risk_returns_sanitized_error(self):
        path = memory.program_file("malformed-risk")
        path.write_text(json.dumps({
            "program_id": "malformed-risk", "program_name": "Malformed Risk",
            "description": "Invalid persisted fixture",
            "risks": [{"description": "Risk", "status": "invented"}],
        }), encoding="utf-8")
        response = self.client.get("/programs/malformed-risk")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"]["code"], "program_persistence_error")
        self.assertNotIn("invented", response.text)

    def test_missing_program_returns_structured_404(self):
        response = self.client.get("/programs/unknown-program")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "program_not_found",
                    "message": "Program 'unknown-program' was not found.",
                }
            },
        )

    def test_intelligence_endpoint_uses_injected_service_and_explicit_contract(self):
        app.dependency_overrides[get_intelligence_service] = lambda: ControlledIntelligenceService()
        response = self.client.get("/programs/controlled-program/intelligence")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "ai")
        self.assertEqual(response.json()["summary"], "Controlled intelligence")
        self.assertEqual(response.json()["schema_version"], "1.0.0")
        self.assertEqual(response.json()["findings"][0]["category"], "fact")
        self.assertNotIn("related_finding_indexes", response.text)
        self.assertNotIn("reasons", response.json()["routing"])

    def test_missing_program_intelligence_returns_structured_404(self):
        app.dependency_overrides[get_intelligence_service] = lambda: ControlledIntelligenceService()
        response = self.client.get("/programs/unknown-program/intelligence")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "program_not_found")

    def test_unexpected_intelligence_failure_is_sanitized(self):
        app.dependency_overrides[get_intelligence_service] = lambda: FailingIntelligenceService()
        response = self.client.get("/programs/controlled-program/intelligence")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            "error": {
                "code": "intelligence_generation_error",
                "message": "Workspace intelligence could not be generated.",
            }
        })
        self.assertNotIn("private provider", response.text)
        self.assertNotIn("filesystem", response.text)

    def test_persistence_failure_returns_structured_500_without_details(self):
        app.dependency_overrides[get_program_reader] = lambda: FailingProgramReader()

        response = self.client.get("/programs")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "program_persistence_error",
                    "message": "Programs could not be loaded.",
                }
            },
        )
        self.assertNotIn("path", response.text)

    def test_cors_preflight_allows_default_frontend_origin_without_credentials(self):
        response = self.client.options(
            "/programs",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )
        self.assertNotIn("access-control-allow-credentials", response.headers)

    def test_openapi_schema_and_required_routes_are_available(self):
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        self.assertIn("/health", paths)
        self.assertIn("/programs", paths)
        self.assertIn("/programs/{programId}", paths)
        self.assertIn("/programs/{programId}/intelligence", paths)
        self.assertEqual(set(paths["/health"]), {"get"})
        self.assertEqual(set(paths["/programs"]), {"get"})
        self.assertEqual(set(paths["/programs/{programId}"]), {"get"})
        schemas = response.json()["components"]["schemas"]
        self.assertIn("IntelligenceFinding", schemas)
        self.assertIn("IntelligenceNextAction", schemas)

    def test_swagger_ui_is_available(self):
        response = self.client.get("/docs")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Swagger UI", response.text)


if __name__ == "__main__":
    unittest.main()
