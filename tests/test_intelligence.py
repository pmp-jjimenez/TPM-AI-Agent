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
from intelligence import WorkspaceIntelligenceService, bounded_program_snapshot, extract_intelligence_evidence
from intelligence_analysis import (
    MAX_ITEM_LENGTH,
    MAX_LIST_ITEMS,
    IntelligenceAnalysisError,
    finalize_intelligence_analysis,
    parse_intelligence_analysis,
)


RISK_ID = "22222222-2222-4222-8222-222222222222"
RISK_POINTER = f"/risksById/{RISK_ID}/title"
ISSUE_ID = "44444444-4444-4444-8444-444444444444"
ISSUE_POINTER = f"/issuesById/{ISSUE_ID}/title"
CANONICAL_RISK = {
    "object_id": RISK_ID, "object_type": "risk", "title": "Stored delivery risk",
    "description": None, "owner": None, "lifecycle_phase": "initiation",
    "audit": {"created_at": None, "updated_at": None, "source": "legacy_import"},
    "status": "open", "probability": None, "impact": None, "priority": None,
    "mitigation_plan": None, "contingency_plan": None, "review_date": None,
    "acceptance_rationale": None, "accepted_by": None,
}
CANONICAL_ISSUE = {
    "object_id": ISSUE_ID, "object_type": "issue", "title": "Stored issue",
    "description": None, "owner": None, "lifecycle_phase": "initiation",
    "audit": {"created_at": None, "updated_at": None, "source": "legacy_import"},
    "status": "open", "severity": None, "impact": None, "due_date": None,
    "resolution_summary": None, "resolved_at": None, "root_cause": None,
}
PROGRAM = {
    "program_id": "controlled-program",
    "program_name": "Controlled Program",
    "description": "A controlled delivery program.",
    "customer": "Customer",
    "phase": "Program Initiation",
    "health": "Green",
    "confidence": "High",
    "risks": [CANONICAL_RISK],
    "issues": [CANONICAL_ISSUE],
    "next_actions": [{"description": "Stored action", "status": "Open"}],
}

PROVIDER_RESULT = {
    "summary": "Grounded AI summary",
    "confidence": "High",
    "findings": [
        {"category": "risk", "statement": "Stored delivery risk", "confidence": "High", "evidence_refs": [RISK_POINTER], "impact": "Delivery may be affected."},
        {"category": "fact", "statement": "The program is in initiation.", "confidence": "High", "evidence_refs": ["/phase"]},
    ],
    "recommendations": [{"priority": "High", "statement": "Conduct the Internal Technical Kickoff.", "rationale": "The initiation phase requires alignment.", "evidence_refs": ["/phase"], "related_finding_indexes": [1]}],
    "decisions_required": [{"priority": "Medium", "statement": "Confirm risk treatment.", "reason": "The recorded risk needs direction.", "related_finding_indexes": [0], "related_recommendation_indexes": []}],
    "next_action": {"priority": "High", "statement": "Schedule the Internal Technical Kickoff.", "rationale": "It is the highest-priority supported action.", "related_finding_indexes": [1], "related_recommendation_indexes": [0]},
    "limitations": [],
}
AI_RESPONSE = json.dumps(PROVIDER_RESULT)
EVIDENCE_CATALOG = extract_intelligence_evidence(PROGRAM)[1]


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
        self.assertEqual(result["schema_version"], "1.0.0")
        self.assertEqual(result["generated_at"], "2026-07-17T12:00:00+00:00")
        self.assertEqual(result["routing"]["primary_persona"], {
            "id": "technical_program_manager", "display_name": "Technical Program Manager"
        })
        self.assertEqual(result["routing"]["supporting_personas"][0]["id"], "delivery_manager")
        self.assertNotIn("reasons", result["routing"])
        self.assertEqual(set(result), {
            "program_id", "generated_at", "source", "routing", "schema_version", "summary",
            "findings", "recommendations", "decisions_required", "next_action", "confidence", "limitations",
        })
        self.assertRegex(result["findings"][0]["id"], r"^fnd_[0-9a-f]{16}$")
        self.assertEqual(result["recommendations"][0]["related_finding_ids"], [result["findings"][1]["id"]])
        self.assertNotIn("related_finding_indexes", result["recommendations"][0])

    def test_missing_configuration_returns_grounded_fallback(self):
        provider = Mock(side_effect=llm.ProviderExecutionError("missing_configuration"))
        result = WorkspaceIntelligenceService(provider, fixed_clock, fixed_router).generate(PROGRAM)

        self.assertEqual(result["source"], "deterministic_fallback")
        self.assertIn("risk", [item["category"] for item in result["findings"]])
        self.assertIn("missing_information", [item["category"] for item in result["findings"]])
        self.assertEqual(result["findings"][0]["evidence_refs"], [RISK_POINTER])
        issue_finding = next(item for item in result["findings"] if item["statement"].startswith("A program issue is recorded"))
        self.assertEqual(issue_finding["evidence_refs"], [ISSUE_POINTER])
        self.assertEqual(result["next_action"]["statement"], "Conduct the Internal Technical Kickoff.")
        self.assertEqual(result["next_action"]["related_recommendation_ids"], [result["recommendations"][0]["id"]])
        self.assertEqual(len([result["next_action"]]), 1)
        self.assertIn("grounded deterministic intelligence", result["limitations"][0])

    def test_ai_and_fallback_share_the_same_required_contract(self):
        ai = WorkspaceIntelligenceService(Mock(return_value=AI_RESPONSE), fixed_clock, fixed_router).generate(PROGRAM)
        fallback = WorkspaceIntelligenceService(Mock(side_effect=llm.ProviderExecutionError("missing_configuration")), fixed_clock, fixed_router).generate(PROGRAM)
        self.assertEqual(set(ai), set(fallback))
        self.assertEqual(set(ai["next_action"]), set(fallback["next_action"]))
        self.assertEqual(set(ai["recommendations"][0]), set(fallback["recommendations"][0]))
        required_finding_fields = {"id", "category", "statement", "confidence", "evidence_refs"}
        self.assertTrue(required_finding_fields.issubset(ai["findings"][0]))
        self.assertTrue(required_finding_fields.issubset(fallback["findings"][0]))

    def test_timeout_and_provider_failures_return_fallback(self):
        for kind in ("timeout", "transport_failure", "provider_failure", "empty_response", "malformed_provider_response"):
            with self.subTest(kind=kind):
                provider = Mock(side_effect=llm.ProviderExecutionError(kind))
                result = WorkspaceIntelligenceService(provider, fixed_clock, fixed_router).generate(PROGRAM)
                self.assertEqual(result["source"], "deterministic_fallback")
                self.assertEqual(provider.call_count, 1)

    def test_malformed_analysis_returns_complete_fallback(self):
        malformed = deepcopy(PROVIDER_RESULT)
        malformed["recommendations"][0].pop("rationale")
        for response in ("not json", "{}", json.dumps({**PROVIDER_RESULT, "confidence": "Certain"}), json.dumps(malformed)):
            with self.subTest(response=response):
                result = WorkspaceIntelligenceService(Mock(return_value=response), fixed_clock, fixed_router).generate(PROGRAM)
                self.assertEqual(result["source"], "deterministic_fallback")
                self.assertNotEqual(result["summary"], "Grounded AI summary")

    def test_parser_rejects_unsupported_fields_and_bounds(self):
        parsed = deepcopy(PROVIDER_RESULT)
        with self.assertRaises(IntelligenceAnalysisError):
            parse_intelligence_analysis(json.dumps({**parsed, "extra": "unsupported"}), EVIDENCE_CATALOG)
        with self.assertRaises(IntelligenceAnalysisError):
            parse_intelligence_analysis(json.dumps({**parsed, "findings": parsed["findings"] * (MAX_LIST_ITEMS + 1)}), EVIDENCE_CATALOG)
        with self.assertRaises(IntelligenceAnalysisError):
            bad = deepcopy(parsed); bad["findings"][0]["statement"] = "x" * (MAX_ITEM_LENGTH + 1)
            parse_intelligence_analysis(json.dumps(bad), EVIDENCE_CATALOG)
        with self.assertRaises(IntelligenceAnalysisError):
            bad = deepcopy(parsed); bad["findings"][0]["extra"] = "unsupported"
            parse_intelligence_analysis(json.dumps(bad), EVIDENCE_CATALOG)

    def test_parser_supports_all_categories_and_enums(self):
        parsed = deepcopy(PROVIDER_RESULT)
        parsed["findings"] = [
            {"category": category, "statement": f"Finding {category}", "confidence": confidence, "evidence_refs": []}
            for category, confidence in zip(
                ("fact", "missing_information", "assumption", "risk", "dependency", "conflict"),
                ("High", "Medium", "Low", "High", "Medium", "Low"),
            )
        ]
        parsed["recommendations"] = [
            {"priority": priority, "statement": f"Recommendation {priority}", "rationale": f"Rationale {priority}", "evidence_refs": [], "related_finding_indexes": []}
            for priority in ("Critical", "High", "Medium", "Low")
        ]
        parsed["decisions_required"] = []
        parsed["next_action"]["related_finding_indexes"] = []
        parsed["next_action"]["related_recommendation_indexes"] = []
        result = finalize_intelligence_analysis(parsed, EVIDENCE_CATALOG)
        self.assertEqual({item["category"] for item in result["findings"]}, {"fact", "missing_information", "assumption", "risk", "dependency", "conflict"})
        self.assertEqual({item["priority"] for item in result["recommendations"]}, {"Critical", "High", "Medium", "Low"})

    def test_parser_rejects_invalid_evidence_relationships_duplicates_and_provider_ids(self):
        mutations = []
        for mutate in (
            lambda value: value["findings"][0].update(evidence_refs=["/secret"]),
            lambda value: value["findings"][0].update(evidence_refs=[RISK_POINTER, RISK_POINTER]),
            lambda value: value["recommendations"][0].update(related_finding_indexes=[99]),
            lambda value: value["recommendations"][0].update(related_finding_indexes=[1, 1]),
            lambda value: value["findings"][0].update(id="fnd_provider"),
            lambda value: value["findings"].append({"category": "RISK".lower(), "statement": "  stored   delivery RISK ", "confidence": "High", "evidence_refs": []}),
        ):
            value = deepcopy(PROVIDER_RESULT); mutate(value); mutations.append(value)
        for value in mutations:
            with self.subTest(value=value), self.assertRaises(IntelligenceAnalysisError):
                finalize_intelligence_analysis(value, EVIDENCE_CATALOG)

    def test_empty_or_omitted_evidence_is_not_referenceable(self):
        _snapshot, catalog = extract_intelligence_evidence(PROGRAM)
        self.assertNotIn("/sponsor", catalog)
        bad = deepcopy(PROVIDER_RESULT); bad["findings"][0]["evidence_refs"] = ["/sponsor"]
        with self.assertRaises(IntelligenceAnalysisError):
            finalize_intelligence_analysis(bad, catalog)

    def test_ids_are_normalized_deterministic_and_semantically_sensitive(self):
        first = finalize_intelligence_analysis(deepcopy(PROVIDER_RESULT), EVIDENCE_CATALOG)
        normalized = deepcopy(PROVIDER_RESULT)
        normalized["findings"][0]["statement"] = "  STORED   delivery risk  "
        second = finalize_intelligence_analysis(normalized, EVIDENCE_CATALOG)
        different = deepcopy(PROVIDER_RESULT); different["findings"][0]["statement"] = "Different risk"
        third = finalize_intelligence_analysis(different, EVIDENCE_CATALOG)
        self.assertEqual(first["findings"][0]["id"], second["findings"][0]["id"])
        self.assertNotEqual(first["findings"][0]["id"], third["findings"][0]["id"])

    def test_colliding_short_digests_extend_deterministically(self):
        parsed = deepcopy(PROVIDER_RESULT)
        parsed["findings"].append({"category": "fact", "statement": "Another fact", "confidence": "High", "evidence_refs": []})
        with patch("intelligence_analysis._digest", side_effect=["a" * 16 + "b" * 48, "a" * 16 + "c" * 48, "d" * 64, "e" * 64, "f" * 64, "1" * 64]):
            result = finalize_intelligence_analysis(parsed, EVIDENCE_CATALOG)
        self.assertEqual(len(result["findings"][0]["id"].split("_")[1]), 24)
        self.assertEqual(len(result["findings"][1]["id"].split("_")[1]), 24)

    def test_bounded_snapshot_omits_arbitrary_and_limits_content(self):
        snapshot = bounded_program_snapshot({
            **PROGRAM,
            "secret": "must not enter prompt",
            "description": "x" * 5000,
            "risks": [{**CANONICAL_RISK, "object_id": f"00000000-0000-4000-8000-{index:012d}", "title": str(index) * 600} for index in range(30)],
        })
        self.assertNotIn("secret", snapshot)
        self.assertEqual(len(snapshot["description"]), 1000)
        self.assertEqual(len(snapshot["risksById"]), 20)
        self.assertTrue(all(len(item["title"]) <= 500 for item in snapshot["risksById"].values()))

    def test_risk_evidence_is_object_keyed_and_stable_when_array_reorders(self):
        second = {**CANONICAL_RISK, "object_id": "33333333-3333-4333-8333-333333333333", "title": "Second risk"}
        first_snapshot, first_catalog = extract_intelligence_evidence({**PROGRAM, "risks": [CANONICAL_RISK, second]})
        reordered_snapshot, reordered_catalog = extract_intelligence_evidence({**PROGRAM, "risks": [second, CANONICAL_RISK]})
        self.assertEqual(first_snapshot["risksById"][RISK_ID], reordered_snapshot["risksById"][RISK_ID])
        self.assertIn(RISK_POINTER, first_catalog)
        self.assertIn(RISK_POINTER, reordered_catalog)

    def test_issue_evidence_is_object_keyed_catalogued_and_stable_when_array_reorders(self):
        second = {**CANONICAL_ISSUE, "object_id": "55555555-5555-4555-8555-555555555555", "title": "Second issue"}
        first_snapshot, first_catalog = extract_intelligence_evidence({**PROGRAM, "issues": [CANONICAL_ISSUE, second]})
        reordered_snapshot, reordered_catalog = extract_intelligence_evidence({**PROGRAM, "issues": [second, CANONICAL_ISSUE]})
        self.assertEqual(first_snapshot["issuesById"][ISSUE_ID], reordered_snapshot["issuesById"][ISSUE_ID])
        self.assertIn(ISSUE_POINTER, first_catalog)
        self.assertIn(ISSUE_POINTER, reordered_catalog)
        provider = deepcopy(PROVIDER_RESULT)
        provider["findings"][1]["evidence_refs"] = [ISSUE_POINTER]
        self.assertEqual(finalize_intelligence_analysis(provider, first_catalog)["findings"][1]["evidence_refs"], [ISSUE_POINTER])
        provider["findings"][1]["evidence_refs"] = [f"/issuesById/{ISSUE_ID}/status"]
        with self.assertRaises(IntelligenceAnalysisError):
            finalize_intelligence_analysis(provider, first_catalog)

    def test_evidence_catalog_uses_only_nonempty_bounded_snapshot_values(self):
        dependency = {"object_id": "66666666-6666-4666-8666-666666666666", "title": "Vendor"}
        snapshot, catalog = extract_intelligence_evidence({**PROGRAM, "customer": "", "dependencies": [dependency]})
        self.assertEqual(snapshot["dependenciesById"][dependency["object_id"]]["title"], "Vendor")
        self.assertIn(f"/dependenciesById/{dependency['object_id']}/title", catalog)
        self.assertNotIn("/customer", catalog)

    def test_dependency_evidence_is_stable_when_array_reorders_and_catalogued(self):
        first = {"object_id": "66666666-6666-4666-8666-666666666666", "title": "Vendor circuit"}
        second = {"object_id": "77777777-7777-4777-8777-777777777777", "title": "Customer approval"}
        snapshot, catalog = extract_intelligence_evidence({**PROGRAM, "dependencies": [first, second]})
        reordered, reordered_catalog = extract_intelligence_evidence({**PROGRAM, "dependencies": [second, first]})
        pointer = f"/dependenciesById/{first['object_id']}/title"
        self.assertEqual(snapshot["dependenciesById"][first["object_id"]], reordered["dependenciesById"][first["object_id"]])
        self.assertIn(pointer, catalog)
        self.assertIn(pointer, reordered_catalog)
        provider = deepcopy(PROVIDER_RESULT); provider["findings"][1]["evidence_refs"] = [pointer]
        self.assertEqual(finalize_intelligence_analysis(provider, catalog)["findings"][1]["evidence_refs"], [pointer])

    def test_canonical_action_preserves_contract_v1_bounded_description(self):
        canonical = {
            "object_id": "11111111-1111-4111-8111-111111111111",
            "object_type": "action",
            "title": "Stored action",
            "description": None,
            "owner": None,
            "lifecycle_phase": "initiation",
            "audit": {"created_at": None, "updated_at": None, "source": "legacy_import"},
            "status": "open",
            "priority": None,
            "due_date": None,
            "completed_at": None,
            "completion_summary": None,
        }
        legacy_snapshot = bounded_program_snapshot(PROGRAM)
        canonical_snapshot = bounded_program_snapshot({**PROGRAM, "next_actions": [canonical]})

        self.assertEqual(canonical_snapshot["next_actions"], legacy_snapshot["next_actions"])
        self.assertEqual(extract_intelligence_evidence({**PROGRAM, "next_actions": [canonical]})[1], EVIDENCE_CATALOG)

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
