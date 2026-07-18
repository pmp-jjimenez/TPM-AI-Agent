import json
import os
import socket
import sys
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch


APP_DIR = Path(__file__).resolve().parents[1] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import llm
from intelligence import WorkspaceIntelligenceService, bounded_program_snapshot
from intelligence_analysis import (
    MAX_ITEM_LENGTH,
    MAX_LIST_ITEMS,
    IntelligenceAnalysisError,
    parse_intelligence_analysis,
)


PROGRAM = {
    "program_id": "controlled-program",
    "program_name": "Controlled Program",
    "description": "A controlled delivery program.",
    "customer": "Customer",
    "phase": "Program Initiation",
    "health": "Green",
    "confidence": "High",
    "risks": [{"description": "Stored delivery risk", "status": "Open"}],
    "issues": [{"description": "Stored issue", "status": "Open"}],
    "next_actions": [{"description": "Stored action", "status": "Open"}],
}

AI_RESPONSE = json.dumps({
    "summary": "Grounded AI summary",
    "attention_items": ["Review the stored issue"],
    "risks": ["Stored delivery risk"],
    "missing_information": ["Sponsor"],
    "recommended_actions": ["Internal Technical Kickoff"],
    "confidence": "High",
    "limitations": [],
})


def fixed_clock():
    return datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def fixed_router(*_args, **_kwargs):
    return ({
        "routing_version": "1.0.0",
        "primary_persona": "technical_program_manager",
        "supporting_personas": ["delivery_manager"],
        "reasons": ["not transported"],
    }, False)


class IntelligenceServiceTests(unittest.TestCase):
    def test_ai_success_uses_one_provider_call_and_stable_contract(self):
        provider = Mock(return_value=AI_RESPONSE)
        router = Mock(side_effect=fixed_router)
        original = deepcopy(PROGRAM)
        result = WorkspaceIntelligenceService(provider, fixed_clock, router).generate(PROGRAM)

        self.assertEqual(provider.call_count, 1)
        self.assertEqual(router.call_count, 1)
        self.assertEqual(PROGRAM, original)
        self.assertEqual(result["source"], "ai")
        self.assertEqual(result["generated_at"], "2026-07-17T12:00:00+00:00")
        self.assertEqual(result["routing"]["primary_persona"], {
            "id": "technical_program_manager", "display_name": "Technical Program Manager"
        })
        self.assertEqual(result["routing"]["supporting_personas"][0]["id"], "delivery_manager")
        self.assertNotIn("reasons", result["routing"])
        self.assertEqual(set(result), {
            "program_id", "generated_at", "source", "routing", "summary",
            "attention_items", "risks", "missing_information",
            "recommended_actions", "confidence", "limitations",
        })

    def test_missing_configuration_returns_grounded_fallback(self):
        provider = Mock(side_effect=llm.ProviderExecutionError("missing_configuration"))
        result = WorkspaceIntelligenceService(provider, fixed_clock, fixed_router).generate(PROGRAM)

        self.assertEqual(result["source"], "deterministic_fallback")
        self.assertEqual(result["risks"], ["Stored delivery risk"])
        self.assertEqual(result["attention_items"], ["Stored issue"])
        self.assertIn("Sponsor", result["missing_information"])
        self.assertIn("Internal Technical Kickoff", result["recommended_actions"])
        self.assertIn("grounded deterministic intelligence", result["limitations"][0])

    def test_timeout_and_provider_failures_return_fallback(self):
        for kind in ("timeout", "transport_failure", "provider_failure", "empty_response", "malformed_provider_response"):
            with self.subTest(kind=kind):
                provider = Mock(side_effect=llm.ProviderExecutionError(kind))
                result = WorkspaceIntelligenceService(provider, fixed_clock, fixed_router).generate(PROGRAM)
                self.assertEqual(result["source"], "deterministic_fallback")
                self.assertEqual(provider.call_count, 1)

    def test_malformed_analysis_returns_complete_fallback(self):
        for response in ("not json", "{}", json.dumps({**json.loads(AI_RESPONSE), "confidence": "Certain"})):
            with self.subTest(response=response):
                result = WorkspaceIntelligenceService(Mock(return_value=response), fixed_clock, fixed_router).generate(PROGRAM)
                self.assertEqual(result["source"], "deterministic_fallback")
                self.assertNotEqual(result["summary"], "Grounded AI summary")

    def test_parser_rejects_unsupported_fields_and_bounds(self):
        parsed = json.loads(AI_RESPONSE)
        with self.assertRaises(IntelligenceAnalysisError):
            parse_intelligence_analysis(json.dumps({**parsed, "extra": "unsupported"}))
        with self.assertRaises(IntelligenceAnalysisError):
            parse_intelligence_analysis(json.dumps({**parsed, "risks": ["x"] * (MAX_LIST_ITEMS + 1)}))
        with self.assertRaises(IntelligenceAnalysisError):
            parse_intelligence_analysis(json.dumps({**parsed, "risks": ["x" * (MAX_ITEM_LENGTH + 1)]}))
        with self.assertRaises(IntelligenceAnalysisError):
            parse_intelligence_analysis(json.dumps({**parsed, "risks": [""]}))

    def test_bounded_snapshot_omits_arbitrary_and_limits_content(self):
        snapshot = bounded_program_snapshot({
            **PROGRAM,
            "secret": "must not enter prompt",
            "description": "x" * 5000,
            "risks": [{"description": str(index) * 600} for index in range(30)],
        })
        self.assertNotIn("secret", snapshot)
        self.assertEqual(len(snapshot["description"]), 1000)
        self.assertEqual(len(snapshot["risks"]), 20)
        self.assertTrue(all(len(item) <= 500 for item in snapshot["risks"]))

    def test_service_does_not_call_persistence_or_write_sessions(self):
        with patch("intelligence.load_core_context", return_value="context"), \
             patch("builtins.open") as open_file:
            WorkspaceIntelligenceService(Mock(return_value=AI_RESPONSE), fixed_clock, fixed_router).generate(PROGRAM)
        open_file.assert_not_called()


class ProviderBoundaryTests(unittest.TestCase):
    def test_missing_configuration_is_classified_and_compatibility_string_is_preserved(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(llm.ProviderExecutionError) as captured:
                llm.execute_provider("prompt")
            self.assertEqual(captured.exception.kind, "missing_configuration")
            self.assertEqual(llm.generate_response("prompt"), "ERROR: GEMINI_API_KEY is not configured.")

    def test_timeout_is_classified_without_retry(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "controlled-secret"}, clear=True), \
             patch("urllib.request.urlopen", side_effect=socket.timeout()) as urlopen:
            with self.assertRaises(llm.ProviderExecutionError) as captured:
                llm.execute_provider("private prompt", timeout=3)
        self.assertEqual(captured.exception.kind, "timeout")
        self.assertEqual(urlopen.call_count, 1)
        self.assertNotIn("controlled-secret", str(captured.exception))
        self.assertNotIn("private prompt", str(captured.exception))


if __name__ == "__main__":
    unittest.main()
