"""ReportLab-specific dependency and configuration readiness boundary.

This increment intentionally does not implement a renderer or generate a PDF.
"""

from contextlib import contextmanager
from dataclasses import dataclass
import importlib
from threading import RLock
from typing import Optional, Tuple

from artifact_renderer import ArtifactConfigurationError, ArtifactDependencyError
from font_assets import FontAssetError, validate_inter_font_assets


EXPECTED_REPORTLAB_VERSION = "5.0.0"
_REPORTLAB_CONFIG_LOCK = RLock()


@dataclass(frozen=True)
class PdfBackendReadiness:
    ready: bool
    reportlab_available: bool
    installed_version: Optional[str]
    font_assets_valid: bool
    diagnostics: Tuple[str, ...]


def inspect_pdf_backend(asset_dir=None, module_importer=None):
    """Inspect the concrete backend without generating output or changing config."""
    importer = module_importer or importlib.import_module
    try:
        reportlab = importer("reportlab")
    except (ImportError, ModuleNotFoundError):
        return PdfBackendReadiness(
            ready=False,
            reportlab_available=False,
            installed_version=None,
            font_assets_valid=_font_assets_are_valid(asset_dir),
            diagnostics=("reportlab-missing",),
        )

    installed_version = getattr(reportlab, "Version", None) or getattr(
        reportlab, "__version__", None
    )
    diagnostics = []
    if installed_version != EXPECTED_REPORTLAB_VERSION:
        diagnostics.append("reportlab-version-mismatch")

    fonts_valid = _font_assets_are_valid(asset_dir)
    if not fonts_valid:
        diagnostics.append("font-assets-invalid")

    return PdfBackendReadiness(
        ready=not diagnostics,
        reportlab_available=True,
        installed_version=str(installed_version) if installed_version is not None else None,
        font_assets_valid=fonts_valid,
        diagnostics=tuple(diagnostics),
    )


def require_pdf_backend(asset_dir=None, module_importer=None):
    """Require explicit PDF readiness with bounded application-facing failures."""
    readiness = inspect_pdf_backend(asset_dir=asset_dir, module_importer=module_importer)
    if not readiness.reportlab_available:
        raise ArtifactDependencyError(
            "pdf-dependency-unavailable",
            "PDF generation requires ReportLab 5.0.0.",
        )
    if readiness.installed_version != EXPECTED_REPORTLAB_VERSION:
        raise ArtifactConfigurationError(
            "pdf-version-mismatch",
            "PDF generation requires the approved ReportLab version.",
        )
    if not readiness.font_assets_valid:
        raise ArtifactConfigurationError(
            "pdf-font-assets-invalid",
            "PDF generation requires valid bundled Inter font assets.",
        )
    return readiness


@contextmanager
def temporary_reportlab_config(document_language, deterministic_test_mode=False):
    """Apply process-global ReportLab settings temporarily and restore them."""
    if not document_language or len(document_language) > 35:
        raise ArtifactConfigurationError(
            "pdf-language-invalid",
            "PDF document language must be a bounded non-empty value.",
        )

    try:
        rl_config = importlib.import_module("reportlab.rl_config")
    except (ImportError, ModuleNotFoundError) as error:
        raise ArtifactDependencyError(
            "pdf-dependency-unavailable",
            "PDF generation requires ReportLab 5.0.0.",
        ) from error

    with _REPORTLAB_CONFIG_LOCK:
        previous_language = rl_config.documentLang
        previous_invariant = rl_config.invariant
        rl_config.documentLang = document_language
        rl_config.invariant = 1 if deterministic_test_mode else 0
        try:
            yield rl_config
        finally:
            rl_config.documentLang = previous_language
            rl_config.invariant = previous_invariant


def _font_assets_are_valid(asset_dir):
    try:
        validate_inter_font_assets(asset_dir=asset_dir)
    except FontAssetError:
        return False
    return True
