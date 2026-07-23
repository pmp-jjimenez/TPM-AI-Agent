import importlib
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import date
from io import BytesIO
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch


APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from pypdf import PdfReader

import artifact_renderer
import pdf_reportlab_renderer
from artifact_design import (
    DEFAULT_ARTIFACT_DESIGN_SYSTEM,
    ArtifactDesignError,
)
from artifact_renderer import (
    ArtifactConfigurationError,
    ArtifactFormat,
    ArtifactRenderer,
    RenderContext,
)
from executive_artifact import (
    ExecutiveArtifactCompositionPolicy,
    compose_executive_status_artifact,
)
from executive_report import (
    NO_RECOMMENDATION_TEXT,
    ReportMetadataInput,
    build_executive_report_view_model,
)
from font_assets import FontAssetError


REPORT_INPUT = ReportMetadataInput(
    report_date=date(2026, 7, 23),
    generated_at="2026-07-23T12:00:00-06:00",
    locale="en-US",
    timezone="America/Mexico_City",
    report_id="status-alpha-2026-07-23",
)
CONTEXT = RenderContext(
    "en-US",
    deterministic_test_mode=True,
    title="Executive Status Report",
    subject="Approved executive status",
    author="TPM Operating System",
    creator="TPM Operating System",
    producer="ReportLab 5.0.0",
)


def program(**overrides):
    value = {
        "schema_version": "1.5.0",
        "program_id": "alpha-00000000-0000-4000-8000-000000000001",
        "program_name": "Alpha Delivery",
        "description": "Delivery program",
        "customer": "Cliente México",
        "phase": "Execution",
        "health": "Yellow",
        "confidence": "Medium",
        "risks": [{
            "title": "Risk & assurance <review>",
            "status": "monitoring",
            "priority": "high",
            "owner": "Program Owner",
            "review_date": "2026-07-22",
            "impact": "high",
            "mitigation_plan": "Validate <controls> safely.",
        }],
        "issues": [{
            "description": "Blocked integration",
            "status": "blocked",
            "severity": "critical",
        }],
        "dependencies": [{"name": "Vendor approval", "impact": "Schedule"}],
        "decisions": [{"decision": "Approve scope", "status": "proposed"}],
        "next_actions": [{"description": "Confirm sponsor", "priority": "high"}],
        "relationships": [],
        "metadata": {"updated_at": "2026-07-22T12:00:00+00:00"},
    }
    value.update(overrides)
    return value


def artifact_for(source=None, maximum=10):
    view_model = build_executive_report_view_model(
        program() if source is None else source,
        report_metadata=REPORT_INPUT,
    )
    return compose_executive_status_artifact(
        view_model,
        policy=ExecutiveArtifactCompositionPolicy(
            maximum_records_per_collection=maximum
        ),
    )


def render(artifact=None, context=CONTEXT, design_system=DEFAULT_ARTIFACT_DESIGN_SYSTEM):
    return pdf_reportlab_renderer.ReportLabPdfRenderer().render(
        artifact or artifact_for(),
        design_system=design_system,
        render_context=context,
    )


def reader(result):
    return PdfReader(BytesIO(result.payload))


def extracted(result):
    return "\n".join(page.extract_text() or "" for page in reader(result).pages)


class RendererContractTests(unittest.TestCase):
    def test_import_protocol_and_output_contract(self):
        renderer = pdf_reportlab_renderer.ReportLabPdfRenderer()
        self.assertIsInstance(renderer, ArtifactRenderer)
        self.assertEqual(renderer.format, ArtifactFormat.PDF)
        result = render()
        self.assertEqual(result.media_type, "application/pdf")
        self.assertEqual(result.extension, "pdf")
        self.assertIsInstance(result.payload, bytes)
        self.assertTrue(result.payload.startswith(b"%PDF-"))
        with self.assertRaises(FrozenInstanceError):
            result.payload = b"changed"

    def test_supported_type_parses_and_has_pages(self):
        result = render()
        parsed = reader(result)
        self.assertGreaterEqual(len(parsed.pages), 1)

    def test_unsupported_type_and_malformed_inputs_fail_boundedly(self):
        invalid = replace(artifact_for(), artifact_type="html")
        with self.assertRaisesRegex(
            ArtifactConfigurationError, "only executive_status_report"
        ):
            render(invalid)
        with self.assertRaisesRegex(ArtifactConfigurationError, "contract is invalid"):
            render(object())
        with self.assertRaisesRegex(ArtifactConfigurationError, "context is invalid"):
            render(context=object())

    def test_invalid_design_system_fails_before_rendering(self):
        invalid = replace(DEFAULT_ARTIFACT_DESIGN_SYSTEM, name="Unsupported")
        with self.assertRaisesRegex(ArtifactConfigurationError, "design system is invalid"):
            render(design_system=invalid)

    def test_missing_altered_font_wrong_version_and_registration_fail_boundedly(self):
        with patch.object(
            pdf_reportlab_renderer,
            "validate_inter_font_assets",
            side_effect=FontAssetError("private font path"),
        ):
            with self.assertRaisesRegex(
                ArtifactConfigurationError, "valid bundled Inter font assets"
            ):
                render()
        with patch.object(
            pdf_reportlab_renderer,
            "inspect_pdf_backend",
            return_value=pdf_reportlab_renderer.PdfBackendReadiness(
                False, True, "4.5.1", True, ("reportlab-version-mismatch",)
            ),
        ):
            with self.assertRaisesRegex(
                ArtifactConfigurationError, "approved ReportLab version"
            ):
                render()
        with patch.object(
            pdf_reportlab_renderer,
            "_register_inter_fonts",
            side_effect=RuntimeError("private path"),
        ):
            with self.assertRaisesRegex(
                artifact_renderer.ArtifactRendererError, "rendering failed"
            ):
                render()

    def test_fonts_register_repeatedly(self):
        first = render()
        second = render()
        self.assertTrue(first.payload)
        self.assertTrue(second.payload)


class ContentAndPaginationTests(unittest.TestCase):
    def test_all_semantic_content_is_selectable_and_ordered(self):
        text = extracted(render())
        leading = (
            "Executive Status Report",
            "Alpha Delivery",
            "Cliente México",
            "2026-07-23",
            "Execution",
            "Yellow",
            "Medium",
            "Executive summary",
            "Record metrics",
            "Primary recommendation",
        )
        positions = [text.index(value) for value in leading]
        cursor = positions[-1] + len(leading[-1])
        for label in ("Risks", "Issues", "Dependencies", "Decisions", "Actions"):
            cursor = text.index(label, cursor)
            positions.append(cursor)
            cursor += len(label)
        positions.append(text.index("Report completeness", cursor))
        self.assertEqual(positions, sorted(positions))
        for value in ("TOTAL", "ACTIVE", "BLOCKED", "OVERDUE", "Evidence IDs"):
            self.assertIn(value, text)

    def test_record_details_omissions_and_limit_notices_are_visible(self):
        artifact = artifact_for()
        risk = next(
            component for component in artifact.components
            if getattr(component, "label", None) == "Risks"
        ).records[0]
        text = extracted(render(artifact))
        for value in (
            risk.source_id.value,
            "Selected: 1",
            "Omitted: 0",
            "Owner: Program Owner",
            "Overdue: Yes",
            "DEPENDENCY_CRITICALITY_UNAVAILABLE",
            "DECISION_BLOCKER_EVIDENCE_UNAVAILABLE",
        ):
            self.assertIn(value, text)

    def test_special_characters_multiline_and_markup_are_safe(self):
        special = program(program_name="Línea uno\nLínea dos & <tres> áéíóú")
        result = render(artifact_for(special))
        text = extracted(result)
        self.assertIn("Risk & assurance <review>", text)
        self.assertIn("Línea uno", text)
        self.assertIn("Línea dos & <tres> áéíóú", text)
        self.assertIn("Validate <controls> safely.", text)

    def test_health_roles_use_distinct_visuals_with_text(self):
        streams = {}
        for health in ("Green", "Yellow", "Red"):
            result = render(artifact_for(program(health=health)))
            parsed = reader(result)
            streams[health] = b"".join(
                page.get_contents().get_data() for page in parsed.pages
            )
            self.assertIn(health, extracted(result))
        self.assertIn(b".141176 .419608 .270588 rg", streams["Green"])
        self.assertIn(b".545098 .396078 0 rg", streams["Yellow"])
        self.assertIn(b".631373 .14902 .176471 rg", streams["Red"])

    def test_missing_values_empty_states_and_no_recommendation_are_exact(self):
        sparse = {
            "program_id": "sparse",
            "risks": [],
            "issues": [],
            "dependencies": [],
            "decisions": [],
            "next_actions": [],
        }
        text = extracted(render(artifact_for(sparse)))
        self.assertIn("Missing value:", text)
        self.assertIn(NO_RECOMMENDATION_TEXT, text)
        self.assertIn("No risk records are present in the report data.", text)
        self.assertIn("Omitted: 0", text)

    def test_long_artifact_is_multipage_and_terminal_content_survives(self):
        risks = [
            {
                "title": f"Long risk {index}",
                "status": "open",
                "priority": "high",
                "mitigation_plan": ("Long wrapped narrative & evidence. " * 35),
            }
            for index in range(18)
        ]
        result = render(artifact_for(program(risks=risks), maximum=18))
        parsed = reader(result)
        text = extracted(result)
        self.assertGreater(len(parsed.pages), 3)
        self.assertIn("Long risk 17", text)
        self.assertIn("Report completeness", text)
        self.assertIn("Artifact version 1.0", text)
        self.assertGreaterEqual(text.count("TPM Operating System | executive_status_report"), len(parsed.pages))
        self.assertGreaterEqual(text.count("Executive Status Report"), len(parsed.pages))
        for number in range(1, len(parsed.pages) + 1):
            self.assertIn(f"Page {number}", text)

    def test_more_than_ten_records_discloses_omissions_without_reselection(self):
        risks = [{"description": f"Risk {index}"} for index in range(12)]
        text = extracted(render(artifact_for(program(risks=risks))))
        self.assertIn("Total available: 12", text)
        self.assertIn("Selected: 10", text)
        self.assertIn("Omitted: 2", text)


class PdfStructureTests(unittest.TestCase):
    def test_fonts_metadata_language_and_security_structure(self):
        parsed = reader(render())
        metadata = parsed.metadata
        self.assertEqual(metadata.title, CONTEXT.title)
        self.assertEqual(metadata.author, CONTEXT.author)
        self.assertEqual(metadata.creator, CONTEXT.creator)
        self.assertEqual(metadata.producer, CONTEXT.producer)
        root = parsed.trailer["/Root"]
        self.assertEqual(root.get("/Lang"), "en-US")
        self.assertNotIn("/OpenAction", root)
        self.assertNotIn("/Names", root)
        self.assertNotIn("/JavaScript", root)

        base_fonts = set()
        for page in parsed.pages:
            fonts = page["/Resources"].get("/Font", {})
            for font in fonts.values():
                base_fonts.add(str(font.get_object().get("/BaseFont", "")))
        joined = " ".join(base_fonts)
        self.assertIn("Inter-Regular", joined)
        self.assertIn("Inter-SemiBold", joined)
        self.assertNotIn("Helvetica", joined)

    def test_invariant_render_is_byte_identical(self):
        artifact = artifact_for()
        self.assertEqual(render(artifact).payload, render(artifact).payload)

    def test_normal_metadata_follows_supplied_inputs(self):
        context = replace(
            CONTEXT,
            deterministic_test_mode=False,
            title="Truthful supplied title",
            author="Supplied product",
        )
        parsed = reader(render(context=context))
        self.assertEqual(parsed.metadata.title, "Truthful supplied title")
        self.assertEqual(parsed.metadata.author, "Supplied product")
        self.assertEqual(
            parsed.metadata.creation_date.isoformat(),
            "2026-07-23T00:00:00+00:00",
        )


class SafetyAndStateTests(unittest.TestCase):
    def test_renderer_does_not_mutate_inputs(self):
        artifact = artifact_for()
        design = DEFAULT_ARTIFACT_DESIGN_SYSTEM
        context = CONTEXT
        before = (deepcopy(artifact), deepcopy(design), deepcopy(context))
        render(artifact, context, design)
        self.assertEqual((artifact, design, context), before)

    def test_renderer_does_not_call_application_clock(self):
        with patch("time.time", side_effect=AssertionError("clock called")):
            render()
            render(context=replace(CONTEXT, deterministic_test_mode=False))

    def test_global_configuration_restores_after_success_and_failure(self):
        from reportlab import rl_config

        before = (rl_config.documentLang, rl_config.invariant)
        render()
        self.assertEqual((rl_config.documentLang, rl_config.invariant), before)
        with patch.object(
            pdf_reportlab_renderer, "_build_pdf", side_effect=RuntimeError("failure")
        ):
            with self.assertRaises(artifact_renderer.ArtifactRendererError):
                render()
        self.assertEqual((rl_config.documentLang, rl_config.invariant), before)

    def test_concurrent_renders_complete_without_interleaving(self):
        results = []
        failures = []

        def worker(language):
            try:
                results.append(render(context=replace(CONTEXT, language_tag=language)))
            except Exception as error:
                failures.append(error)

        threads = [
            threading.Thread(target=worker, args=("en-US",)),
            threading.Thread(target=worker, args=("es-MX",)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(failures, [])
        self.assertEqual(len(results), 2)
        self.assertTrue(all(reader(result).pages for result in results))

    def test_renderer_has_no_program_persistence_cli_gemini_or_javascript_dependency(self):
        source = Path(pdf_reportlab_renderer.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "normalize_program",
            "build_executive_report_view_model",
            "compose_executive_status_artifact",
            "gemini",
            "save_program",
            "open(",
            "javascript",
        ):
            self.assertNotIn(forbidden, source.lower())

    def test_neutral_modules_import_when_reportlab_is_blocked(self):
        target_modules = ("artifact_renderer", "artifact_semantics", "artifact_design")
        original_import = __import__

        def blocked(name, *args, **kwargs):
            if name == "reportlab" or name.startswith("reportlab."):
                raise ModuleNotFoundError("blocked")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=blocked):
            for name in target_modules:
                self.assertIs(importlib.import_module(name), sys.modules[name])


if __name__ == "__main__":
    unittest.main()
