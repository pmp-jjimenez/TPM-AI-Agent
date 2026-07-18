import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.compat import APPLICATION_VERSION, memory
from backend.api.dependencies import get_program_reader
from backend.api.main import app


CONTROLLED_PROGRAM = {
    "schema_version": "1.0.0",
    "program_id": "controlled-program",
    "program_name": "Controlled Program",
    "description": "Program fixture isolated from repository persistence.",
    "customer": "Test Customer",
    "phase": "Program Initiation",
    "health": "Green",
    "confidence": "High",
    "risks": [],
    "issues": [],
    "decisions": [],
    "next_actions": [],
    "meeting_history": [],
    "documents": [],
    "artifacts": [],
    "metadata": {
        "created_at": "2026-07-17T00:00:00+00:00",
        "updated_at": "2026-07-17T00:00:00+00:00",
        "source": "test",
    },
}


class FailingProgramReader:
    def list_programs(self):
        raise OSError("private test persistence path")

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
        self.assertEqual(set(paths["/health"]), {"get"})
        self.assertEqual(set(paths["/programs"]), {"get"})
        self.assertEqual(set(paths["/programs/{programId}"]), {"get"})

    def test_swagger_ui_is_available(self):
        response = self.client.get("/docs")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Swagger UI", response.text)


if __name__ == "__main__":
    unittest.main()
