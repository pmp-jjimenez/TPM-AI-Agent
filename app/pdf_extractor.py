from pathlib import Path


DEFAULT_MAX_TEXT_CHARACTERS = 120000


class PDFExtractionError(ValueError):
    """Raised when a local PDF cannot provide usable text."""


def validate_pdf_path(path_value):
    if not isinstance(path_value, str) or not path_value.strip():
        raise PDFExtractionError("A PDF path is required.")

    path = Path(path_value.strip()).expanduser()
    if not path.exists():
        raise PDFExtractionError("The PDF path does not exist.")
    if not path.is_file():
        raise PDFExtractionError("The PDF path must point to a file.")
    if path.suffix.lower() != ".pdf":
        raise PDFExtractionError("The selected file must have a .pdf extension.")
    return path


def extract_pdf_text(path_value, max_characters=DEFAULT_MAX_TEXT_CHARACTERS):
    path = validate_pdf_path(path_value)
    if not isinstance(max_characters, int) or max_characters < 1:
        raise ValueError("max_characters must be a positive integer")

    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as error:
        raise PDFExtractionError(
            "PDF support is unavailable. Install dependencies from requirements.txt."
        ) from error

    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise PDFExtractionError(
                "The PDF is encrypted and cannot be read without a password."
            )

        page_text = []
        extractable_pages = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                extractable_pages += 1
                page_text.append(text.strip())
    except PDFExtractionError:
        raise
    except (PdfReadError, OSError, ValueError) as error:
        raise PDFExtractionError(
            "The PDF could not be read. It may be malformed or damaged."
        ) from error
    except Exception as error:
        raise PDFExtractionError("PDF text extraction failed.") from error

    extracted = "\n\n".join(page_text).strip()
    if not extracted:
        raise PDFExtractionError(
            "No extractable text was found. The PDF may be empty or image-only; OCR is not supported."
        )

    original_characters = len(extracted)
    truncated = original_characters > max_characters
    if truncated:
        extracted = extracted[:max_characters]

    return {
        "text": extracted,
        "metadata": {
            "source_filename": path.name,
            "page_count": len(reader.pages),
            "extractable_page_count": extractable_pages,
            "original_character_count": original_characters,
            "extracted_character_count": len(extracted),
            "truncated": truncated,
            "max_characters": max_characters,
        },
    }
