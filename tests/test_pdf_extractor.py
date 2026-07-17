import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from pdf_extractor import PDFExtractionError, extract_pdf_text, validate_pdf_path


class _Page:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class _Reader:
    pages = [_Page("Scope and deliverables")]
    is_encrypted = False

    def __init__(self, unused_path):
        pass


class PDFExtractorTests(unittest.TestCase):
    def test_valid_pdf_path_and_path_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample sow.PDF"
            path.write_bytes(b"fake fixture")
            self.assertEqual(validate_pdf_path(str(path)), path)

    def test_missing_path_is_rejected(self):
        with self.assertRaisesRegex(PDFExtractionError, "does not exist"):
            validate_pdf_path("/tmp/nonexistent-sow-fixture.pdf")

    def test_non_pdf_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.txt"
            path.write_text("not confidential", encoding="utf-8")
            with self.assertRaisesRegex(PDFExtractionError, "\.pdf extension"):
                validate_pdf_path(str(path))

    def test_extract_returns_text_metadata_and_truncation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.pdf"
            path.write_bytes(b"fake fixture")
            with _fake_pypdf(_Reader):
                result = extract_pdf_text(str(path), max_characters=5)
            self.assertEqual(result["text"], "Scope")
            self.assertTrue(result["metadata"]["truncated"])
            self.assertEqual(result["metadata"]["source_filename"], "fixture.pdf")

    def test_empty_or_image_only_pdf_is_rejected(self):
        class EmptyReader(_Reader):
            pages = [_Page("")]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.pdf"
            path.write_bytes(b"fake fixture")
            with _fake_pypdf(EmptyReader):
                with self.assertRaisesRegex(PDFExtractionError, "No extractable text"):
                    extract_pdf_text(str(path))


def _fake_pypdf(reader):
    module = types.ModuleType("pypdf")
    module.PdfReader = reader
    errors = types.ModuleType("pypdf.errors")
    errors.PdfReadError = RuntimeError
    return patch.dict(sys.modules, {"pypdf": module, "pypdf.errors": errors})


if __name__ == "__main__":
    unittest.main()
