import ast
from dataclasses import fields, replace
import importlib
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import artifact_renderer
import font_assets
import pdf_reportlab_renderer


class DependencyDeclarationTests(unittest.TestCase):
    def test_requirements_contains_exact_reportlab_pin_and_preserves_pypdf_constraint(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(requirements.count("reportlab==5.0.0"), 1)
        self.assertIn("pypdf>=5.0.0,<7.0.0", requirements)


class RendererIsolationTests(unittest.TestCase):
    def test_renderer_neutral_and_markdown_modules_import_without_reportlab(self):
        target_modules = ("artifact_renderer", "font_assets", "executive")
        saved_modules = {name: sys.modules.get(name) for name in target_modules}
        for name in target_modules:
            sys.modules.pop(name, None)

        original_import = __import__

        def blocked_import(name, *args, **kwargs):
            if name == "reportlab" or name.startswith("reportlab."):
                raise ModuleNotFoundError("simulated unavailable dependency")
            return original_import(name, *args, **kwargs)

        try:
            with patch("builtins.__import__", side_effect=blocked_import):
                for name in target_modules:
                    importlib.import_module(name)
        finally:
            for name in target_modules:
                sys.modules.pop(name, None)
                if saved_modules[name] is not None:
                    sys.modules[name] = saved_modules[name]

    def test_reportlab_references_are_confined_to_approved_backend_modules(self):
        approved = {"pdf_reportlab_renderer.py"}
        referenced_by = set()
        for path in APP_DIR.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            if "reportlab" in source.lower():
                referenced_by.add(path.name)
        self.assertEqual(referenced_by, approved)

    def test_artifact_format_declares_only_pdf(self):
        self.assertEqual(list(artifact_renderer.ArtifactFormat), [artifact_renderer.ArtifactFormat.PDF])

    def test_rendered_artifact_is_in_memory_and_has_no_path_field(self):
        result = artifact_renderer.RenderedArtifact(
            format=artifact_renderer.ArtifactFormat.PDF,
            media_type="application/pdf",
            extension="pdf",
            payload=b"%PDF-proof",
        )
        self.assertIsInstance(result.payload, bytes)
        self.assertNotIn("path", {field.name for field in fields(result)})

    def test_renderer_errors_and_diagnostics_are_bounded_and_sanitized(self):
        private_value = "/Users/example/private\\secret\n" + ("x" * 300)
        error = artifact_renderer.ArtifactRendererError("internal/path", private_value)
        result = artifact_renderer.RenderedArtifact(
            format=artifact_renderer.ArtifactFormat.PDF,
            media_type="application/pdf",
            extension="pdf",
            payload=b"%PDF-proof",
            diagnostics=(private_value,),
        )
        self.assertNotIn("/", str(error))
        self.assertNotIn("\\", str(error))
        self.assertNotIn("\n", str(error))
        self.assertLessEqual(len(str(error)), artifact_renderer.MAX_DIAGNOSTIC_LENGTH)
        self.assertNotIn("/", result.diagnostics[0])
        self.assertLessEqual(
            len(result.diagnostics[0]), artifact_renderer.MAX_DIAGNOSTIC_LENGTH
        )


class FontAssetTests(unittest.TestCase):
    def test_bundled_fonts_exist_and_match_approved_checksums(self):
        validated = font_assets.validate_inter_font_assets()
        self.assertEqual(
            [asset.definition.weight for asset in validated],
            [font_assets.FontWeight.REGULAR, font_assets.FontWeight.SEMIBOLD],
        )
        self.assertTrue(all(asset.path.is_file() for asset in validated))

    def test_font_license_identifies_sil_open_font_license_1_1(self):
        license_text = (font_assets.INTER_ASSET_DIR / "OFL.txt").read_text(encoding="utf-8")
        self.assertIn("SIL OPEN FONT LICENSE Version 1.1", license_text)

    def test_missing_font_is_rejected_without_exposing_absolute_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(font_assets.FontAssetError) as raised:
                font_assets.validate_font_asset(
                    font_assets.INTER_FONT_ASSETS[0],
                    asset_dir=temp_dir,
                )
        self.assertIn("Inter-Regular.ttf", str(raised.exception))
        self.assertNotIn(temp_dir, str(raised.exception))

    def test_altered_font_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "Inter-Regular.ttf"
            path.write_bytes(b"altered")
            with self.assertRaisesRegex(
                font_assets.FontAssetError, "failed checksum validation"
            ):
                font_assets.validate_font_asset(
                    font_assets.INTER_FONT_ASSETS[0],
                    asset_dir=temp_dir,
                )

    def test_wrong_expected_checksum_is_rejected(self):
        definition = replace(font_assets.INTER_FONT_ASSETS[0], sha256="0" * 64)
        with self.assertRaisesRegex(
            font_assets.FontAssetError, "failed checksum validation"
        ):
            font_assets.validate_font_asset(definition)

    def test_unsupported_weight_is_rejected(self):
        with self.assertRaisesRegex(font_assets.FontAssetError, "Unsupported"):
            font_assets.font_asset_for_weight("bold")

    def test_font_asset_module_has_no_reportlab_reference(self):
        source = (APP_DIR / "font_assets.py").read_text(encoding="utf-8")
        self.assertNotIn("reportlab", source.lower())


class PdfBackendReadinessTests(unittest.TestCase):
    def test_missing_reportlab_is_detected(self):
        def missing_importer(unused_name):
            raise ModuleNotFoundError("simulated")

        readiness = pdf_reportlab_renderer.inspect_pdf_backend(
            module_importer=missing_importer
        )
        self.assertFalse(readiness.ready)
        self.assertFalse(readiness.reportlab_available)
        self.assertEqual(readiness.diagnostics, ("reportlab-missing",))

    def test_incorrect_reportlab_version_is_detected(self):
        readiness = pdf_reportlab_renderer.inspect_pdf_backend(
            module_importer=lambda unused_name: types.SimpleNamespace(Version="4.5.1")
        )
        self.assertFalse(readiness.ready)
        self.assertEqual(readiness.installed_version, "4.5.1")
        self.assertIn("reportlab-version-mismatch", readiness.diagnostics)

    def test_approved_reportlab_and_fonts_are_ready(self):
        readiness = pdf_reportlab_renderer.inspect_pdf_backend(
            module_importer=lambda unused_name: types.SimpleNamespace(Version="5.0.0")
        )
        self.assertTrue(readiness.ready)
        self.assertTrue(readiness.font_assets_valid)
        self.assertEqual(readiness.diagnostics, ())

    def test_invalid_font_assets_are_detected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            readiness = pdf_reportlab_renderer.inspect_pdf_backend(
                asset_dir=temp_dir,
                module_importer=lambda unused_name: types.SimpleNamespace(Version="5.0.0"),
            )
        self.assertFalse(readiness.ready)
        self.assertFalse(readiness.font_assets_valid)
        self.assertIn("font-assets-invalid", readiness.diagnostics)

    def test_explicit_backend_request_raises_actionable_bounded_errors(self):
        def missing_importer(unused_name):
            raise ModuleNotFoundError("private dependency detail")

        with self.assertRaises(artifact_renderer.ArtifactDependencyError) as raised:
            pdf_reportlab_renderer.require_pdf_backend(module_importer=missing_importer)
        self.assertEqual(str(raised.exception), "PDF generation requires ReportLab 5.0.0.")
        self.assertNotIn("private", str(raised.exception))

    def test_import_does_not_mutate_reportlab_global_configuration(self):
        from reportlab import rl_config

        previous_language = rl_config.documentLang
        previous_invariant = rl_config.invariant
        importlib.reload(pdf_reportlab_renderer)
        self.assertEqual(rl_config.documentLang, previous_language)
        self.assertEqual(rl_config.invariant, previous_invariant)

    def test_temporary_configuration_restores_after_normal_completion(self):
        from reportlab import rl_config

        previous_language = rl_config.documentLang
        previous_invariant = rl_config.invariant
        with pdf_reportlab_renderer.temporary_reportlab_config(
            "en-US", deterministic_test_mode=True
        ):
            self.assertEqual(rl_config.documentLang, "en-US")
            self.assertEqual(rl_config.invariant, 1)
        self.assertEqual(rl_config.documentLang, previous_language)
        self.assertEqual(rl_config.invariant, previous_invariant)

    def test_temporary_configuration_restores_after_exception(self):
        from reportlab import rl_config

        previous_language = rl_config.documentLang
        previous_invariant = rl_config.invariant
        with self.assertRaisesRegex(RuntimeError, "proof failure"):
            with pdf_reportlab_renderer.temporary_reportlab_config(
                "es-MX", deterministic_test_mode=False
            ):
                self.assertEqual(rl_config.documentLang, "es-MX")
                self.assertEqual(rl_config.invariant, 0)
                raise RuntimeError("proof failure")
        self.assertEqual(rl_config.documentLang, previous_language)
        self.assertEqual(rl_config.invariant, previous_invariant)

    def test_temporary_configuration_serializes_concurrent_access(self):
        from reportlab import rl_config

        previous_language = rl_config.documentLang
        previous_invariant = rl_config.invariant
        first_entered = threading.Event()
        second_attempted = threading.Event()
        second_entered = threading.Event()
        release_first = threading.Event()
        failures = []

        def first_context():
            try:
                with pdf_reportlab_renderer.temporary_reportlab_config(
                    "en-US", deterministic_test_mode=True
                ):
                    first_entered.set()
                    if not release_first.wait(timeout=2):
                        failures.append("first context timed out")
            except Exception as error:
                failures.append(str(error))

        def second_context():
            try:
                if not first_entered.wait(timeout=2):
                    failures.append("second context did not observe first")
                    return
                second_attempted.set()
                with pdf_reportlab_renderer.temporary_reportlab_config(
                    "es-MX", deterministic_test_mode=False
                ):
                    second_entered.set()
                    if rl_config.documentLang != "es-MX" or rl_config.invariant != 0:
                        failures.append("second context received incorrect configuration")
            except Exception as error:
                failures.append(str(error))

        first = threading.Thread(target=first_context)
        second = threading.Thread(target=second_context)
        first.start()
        second.start()
        self.assertTrue(first_entered.wait(timeout=2))
        self.assertTrue(second_attempted.wait(timeout=2))
        self.assertFalse(second_entered.is_set())
        release_first.set()
        first.join(timeout=2)
        second.join(timeout=2)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertTrue(second_entered.is_set())
        self.assertEqual(failures, [])
        self.assertEqual(rl_config.documentLang, previous_language)
        self.assertEqual(rl_config.invariant, previous_invariant)


class DoctorArtifactDiagnosticsTests(unittest.TestCase):
    def test_doctor_pdf_diagnostic_is_read_only_and_bounded(self):
        from scripts import doctor

        assets = [
            font_assets.INTER_ASSET_DIR / "Inter-Regular.ttf",
            font_assets.INTER_ASSET_DIR / "Inter-SemiBold.ttf",
        ]
        before = [(path.stat().st_mtime_ns, path.read_bytes()) for path in assets]
        diagnostic = doctor.Doctor()

        doctor.check_pdf_backend(diagnostic)

        after = [(path.stat().st_mtime_ns, path.read_bytes()) for path in assets]
        self.assertEqual(before, after)
        self.assertFalse(diagnostic.has_failures())
        self.assertTrue(
            any("ReportLab version is 5.0.0" in message for _, message in diagnostic.results)
        )
        self.assertTrue(
            any("checksum validation" in message for _, message in diagnostic.results)
        )


if __name__ == "__main__":
    unittest.main()
