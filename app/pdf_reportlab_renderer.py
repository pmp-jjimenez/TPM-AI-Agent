"""Concrete, in-memory ReportLab renderer and backend readiness boundary."""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from html import escape
import importlib
from io import BytesIO
from threading import RLock
from typing import Optional, Tuple

from artifact_design import (
    ArtifactDesignError,
    ColorRole,
    DensityAdjustment,
    SpacingRole,
    StatusVisualRole,
    TextEmphasis,
    TypographyRole,
    status_visual_role_for_health,
    validate_artifact_design_system,
)
from artifact_renderer import (
    ArtifactConfigurationError,
    ArtifactDependencyError,
    ArtifactFormat,
    ArtifactRendererError,
    RenderContext,
    RenderedArtifact,
)
from artifact_semantics import (
    ArtifactFooter,
    ArtifactHeader,
    ArtifactType,
    Callout,
    CompletenessNotice,
    MetricGroup,
    NarrativeBlock,
    RecordCollection,
    SemanticArtifact,
    StatusSummary,
)
from executive_report import MissingValue
from font_assets import (
    FontAssetError,
    FontWeight,
    validate_inter_font_assets,
)


EXPECTED_REPORTLAB_VERSION = "5.0.0"
_REPORTLAB_CONFIG_LOCK = RLock()

_FONT_REGULAR = "TPMInterRegular"
_FONT_SEMIBOLD = "TPMInterSemiBold"
_PAGE_SIZE = (612.0, 792.0)
_MARGINS = {"left": 46.0, "right": 46.0, "top": 54.0, "bottom": 48.0}
_SPACING_POINTS = {
    SpacingRole.NONE: 0.0,
    SpacingRole.XXS: 2.0,
    SpacingRole.XS: 4.0,
    SpacingRole.SM: 7.0,
    SpacingRole.MD: 10.0,
    SpacingRole.LG: 15.0,
    SpacingRole.XL: 22.0,
    SpacingRole.XXL: 30.0,
}
_TYPE_POINTS = {
    TypographyRole.DISPLAY: 22.0,
    TypographyRole.TITLE: 17.0,
    TypographyRole.HEADING: 13.0,
    TypographyRole.SUBHEADING: 11.0,
    TypographyRole.BODY: 9.0,
    TypographyRole.BODY_EMPHASIS: 9.0,
    TypographyRole.LABEL: 7.5,
    TypographyRole.CAPTION: 7.5,
    TypographyRole.METRIC: 16.0,
    TypographyRole.MONOSPACE_IDENTIFIER: 7.5,
}


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


class ReportLabPdfRenderer:
    """Render the approved executive semantic artifact to immutable PDF bytes."""

    @property
    def format(self):
        return ArtifactFormat.PDF

    def render(
        self,
        artifact,
        context=None,
        *,
        design_system=None,
        render_context=None,
    ):
        supplied_context = render_context if render_context is not None else context
        if context is not None and render_context is not None:
            raise ArtifactConfigurationError(
                "pdf-render-context-ambiguous",
                "PDF rendering accepts one render context.",
            )
        if not isinstance(supplied_context, RenderContext):
            raise ArtifactConfigurationError(
                "pdf-render-context-invalid",
                "PDF render context is invalid.",
            )
        if design_system is None:
            raise ArtifactConfigurationError(
                "pdf-design-system-required",
                "PDF rendering requires an approved artifact design system.",
            )
        if not isinstance(artifact, SemanticArtifact):
            raise ArtifactConfigurationError(
                "pdf-artifact-invalid",
                "PDF artifact contract is invalid.",
            )
        if artifact.artifact_type is not ArtifactType.EXECUTIVE_STATUS_REPORT:
            raise ArtifactConfigurationError(
                "pdf-artifact-type-unsupported",
                "PDF renderer supports only executive_status_report.",
            )
        _validate_artifact_contract(artifact)
        try:
            validate_artifact_design_system(design_system)
            design_system.density(artifact.density_profile)
        except ArtifactDesignError as error:
            raise ArtifactConfigurationError(
                "pdf-design-system-invalid",
                "PDF artifact design system is invalid.",
            ) from error

        require_pdf_backend()
        try:
            with temporary_reportlab_config(
                supplied_context.language_tag,
                supplied_context.deterministic_test_mode,
            ):
                fonts = _register_inter_fonts()
                payload = _build_pdf(
                    artifact, design_system, supplied_context, fonts
                )
        except ArtifactRendererError:
            raise
        except (FontAssetError, OSError) as error:
            raise ArtifactConfigurationError(
                "pdf-font-registration-failed",
                "PDF bundled font registration failed.",
            ) from error
        except Exception as error:
            raise ArtifactRendererError(
                "pdf-render-failed",
                "Executive Status Report PDF rendering failed.",
            ) from error
        return RenderedArtifact(
            format=ArtifactFormat.PDF,
            media_type="application/pdf",
            extension="pdf",
            payload=payload,
        )


def _validate_artifact_contract(artifact):
    supported = (
        ArtifactHeader,
        StatusSummary,
        MetricGroup,
        NarrativeBlock,
        Callout,
        RecordCollection,
        CompletenessNotice,
        ArtifactFooter,
    )
    if (
        not isinstance(artifact.components, tuple)
        or not artifact.components
        or any(not isinstance(component, supported) for component in artifact.components)
    ):
        raise ArtifactConfigurationError(
            "pdf-artifact-invalid",
            "PDF artifact contract contains an unsupported component.",
        )


def _register_inter_fonts():
    assets = validate_inter_font_assets()
    paths = {asset.definition.weight: str(asset.path) for asset in assets}
    try:
        pdfmetrics = importlib.import_module("reportlab.pdfbase.pdfmetrics")
        ttfonts = importlib.import_module("reportlab.pdfbase.ttfonts")
        registered = set(pdfmetrics.getRegisteredFontNames())
        if _FONT_REGULAR not in registered:
            pdfmetrics.registerFont(
                ttfonts.TTFont(_FONT_REGULAR, paths[FontWeight.REGULAR])
            )
        if _FONT_SEMIBOLD not in registered:
            pdfmetrics.registerFont(
                ttfonts.TTFont(_FONT_SEMIBOLD, paths[FontWeight.SEMIBOLD])
            )
        # ReportLab's bold mapping deliberately resolves to bundled Inter SemiBold.
        pdfmetrics.registerFontFamily(
            "TPMInter",
            normal=_FONT_REGULAR,
            bold=_FONT_SEMIBOLD,
            italic=_FONT_REGULAR,
            boldItalic=_FONT_SEMIBOLD,
        )
    except Exception as error:
        raise ArtifactConfigurationError(
            "pdf-font-registration-failed",
            "PDF bundled font registration failed.",
        ) from error
    return (_FONT_REGULAR, _FONT_SEMIBOLD)


def _build_pdf(artifact, design_system, context, fonts):
    pagesizes = importlib.import_module("reportlab.lib.pagesizes")
    platypus = importlib.import_module("reportlab.platypus")
    styles_module = importlib.import_module("reportlab.lib.styles")
    canvas_module = importlib.import_module("reportlab.pdfgen.canvas")

    if tuple(float(value) for value in pagesizes.letter) != _PAGE_SIZE:
        raise ArtifactConfigurationError(
            "pdf-page-size-invalid",
            "PDF US Letter page configuration is unavailable.",
        )
    buffer = BytesIO()
    styles = _build_styles(design_system, artifact.density_profile, styles_module, fonts)
    doc = platypus.SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.letter,
        leftMargin=_MARGINS["left"],
        rightMargin=_MARGINS["right"],
        topMargin=_MARGINS["top"],
        bottomMargin=_MARGINS["bottom"],
        title=context.title or artifact.title,
        author=context.author or _footer_product(artifact),
        subject=context.subject or artifact.accessibility_label,
        creator=context.creator or _footer_product(artifact),
        producer=context.producer or "ReportLab 5.0.0",
        pageCompression=1,
        initialFontName=fonts[0],
    )
    story = []
    for component in artifact.components:
        story.extend(_render_component(component, design_system, styles, platypus))
    identity = _page_identity(artifact)
    classification = context.classification_label or _classification(artifact)

    def first_page(canvas, unused_doc):
        _draw_page_chrome(
            canvas, identity, artifact.title, classification, first=True, fonts=fonts
        )

    def later_pages(canvas, unused_doc):
        _draw_page_chrome(
            canvas, identity, artifact.title, classification, first=False, fonts=fonts
        )

    doc.build(
        story,
        onFirstPage=first_page,
        onLaterPages=later_pages,
        canvasmaker=_canvas_factory(
            canvas_module.Canvas,
            context.deterministic_test_mode,
            artifact.source_identity.report_date.value,
        ),
    )
    return buffer.getvalue()


def _build_styles(system, density_profile, styles_module, fonts):
    regular, semibold = fonts
    density = system.density(density_profile)
    scale = 0.92 if density.typography_adjustment is DensityAdjustment.REDUCED else 1.0
    result = {}
    for role in TypographyRole:
        token = system.typography(role)
        size = _TYPE_POINTS[role] * scale
        result[role] = styles_module.ParagraphStyle(
            f"TPM-{role.value}",
            fontName=semibold if token.emphasis is TextEmphasis.STRONG else regular,
            fontSize=size,
            leading=size * token.line_height_ratio,
            textColor=_pdf_color(system, ColorRole.TEXT_PRIMARY),
            splitLongWords=True,
            allowWidows=0,
            allowOrphans=0,
            spaceAfter=0,
        )
    result["secondary"] = styles_module.ParagraphStyle(
        "TPM-secondary",
        parent=result[TypographyRole.BODY],
        textColor=_pdf_color(system, ColorRole.TEXT_SECONDARY),
    )
    result["caption-secondary"] = styles_module.ParagraphStyle(
        "TPM-caption-secondary",
        parent=result[TypographyRole.CAPTION],
        textColor=_pdf_color(system, ColorRole.TEXT_SECONDARY),
    )
    return result


def _render_component(component, system, styles, platypus):
    token = system.component(component)
    gap = _spacing(system, token.external_spacing)
    if isinstance(component, ArtifactHeader):
        flows = _render_header(component, styles, platypus)
    elif isinstance(component, StatusSummary):
        flows = _render_status(component, system, styles, platypus)
    elif isinstance(component, NarrativeBlock):
        flows = _section(component.label, styles, platypus) + [
            _paragraph(_report_value(component.narrative), styles[TypographyRole.BODY], platypus)
        ]
    elif isinstance(component, MetricGroup):
        flows = _render_metrics(component, system, styles, platypus)
    elif isinstance(component, Callout):
        flows = _render_callout(component, system, styles, platypus)
    elif isinstance(component, RecordCollection):
        flows = _render_collection(component, system, styles, platypus)
    elif isinstance(component, CompletenessNotice):
        flows = _render_completeness(component, styles, platypus)
    elif isinstance(component, ArtifactFooter):
        flows = _render_semantic_footer(component, styles, platypus)
    else:
        raise ArtifactConfigurationError(
            "pdf-component-unsupported",
            "PDF artifact contains an unsupported component.",
        )
    flows.append(platypus.Spacer(1, gap))
    return flows


def _render_header(component, styles, platypus):
    flows = [
        _paragraph(component.title, styles[TypographyRole.DISPLAY], platypus),
        platypus.Spacer(1, 8),
        _paragraph(
            f"Program: {_report_value(component.program_name)}",
            styles[TypographyRole.TITLE],
            platypus,
        ),
        _paragraph(
            f"Customer: {_report_value(component.customer)}",
            styles["secondary"],
            platypus,
        ),
        _paragraph(
            f"Report date: {_report_value(component.report_date)}  |  "
            f"Report contract: {component.report_contract_version}  |  "
            f"Artifact: {component.artifact_version}",
            styles["caption-secondary"],
            platypus,
        ),
    ]
    if component.classification_label:
        flows.append(
            _paragraph(
                f"Classification: {component.classification_label}",
                styles[TypographyRole.LABEL],
                platypus,
            )
        )
    return flows


def _render_status(component, system, styles, platypus):
    role = status_visual_role_for_health(component.health)
    status = system.status(role)
    color = _pdf_color(system, status.color_role)
    status_style = styles[TypographyRole.BODY_EMPHASIS].clone(
        f"TPM-status-{role.value}"
    )
    status_style.textColor = color
    rows = [
        [
            _paragraph("PHASE", styles[TypographyRole.LABEL], platypus),
            _paragraph("HEALTH", styles[TypographyRole.LABEL], platypus),
            _paragraph("CONFIDENCE", styles[TypographyRole.LABEL], platypus),
        ],
        [
            _paragraph(_report_value(component.phase), styles[TypographyRole.BODY_EMPHASIS], platypus),
            _paragraph(f"● {_report_value(component.health)}", status_style, platypus),
            _paragraph(_report_value(component.confidence), styles[TypographyRole.BODY_EMPHASIS], platypus),
        ],
    ]
    table = platypus.Table(rows, colWidths=[173, 173, 174], repeatRows=1)
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), _FONT_REGULAR),
        ("BACKGROUND", (0, 0), (-1, -1), _pdf_color(system, ColorRole.SURFACE_EMPHASIS)),
        ("BOX", (0, 0), (-1, -1), 1.0, _pdf_color(system, ColorRole.BORDER_EMPHASIS)),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, _pdf_color(system, ColorRole.BORDER)),
        ("TEXTCOLOR", (1, 1), (1, 1), color),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    table.setStyle(platypus.TableStyle(commands))
    return [table]


def _render_metrics(component, system, styles, platypus):
    flows = _section(component.label, styles, platypus)
    rows = [[
        _paragraph("METRIC", styles[TypographyRole.LABEL], platypus),
        _paragraph("TOTAL", styles[TypographyRole.LABEL], platypus),
        _paragraph("ACTIVE", styles[TypographyRole.LABEL], platypus),
        _paragraph("BLOCKED", styles[TypographyRole.LABEL], platypus),
        _paragraph("OVERDUE", styles[TypographyRole.LABEL], platypus),
    ]]
    for metric in component.metrics:
        rows.append([
            _paragraph(metric.label, styles[TypographyRole.BODY_EMPHASIS], platypus),
            _paragraph(str(metric.total.value), styles[TypographyRole.BODY], platypus),
            _paragraph(str(metric.active.value), styles[TypographyRole.BODY], platypus),
            _paragraph(str(metric.blocked.value), styles[TypographyRole.BODY], platypus),
            _paragraph(str(metric.overdue.value), styles[TypographyRole.BODY], platypus),
        ])
    table = platypus.Table(rows, colWidths=[200, 80, 80, 80, 80], repeatRows=1)
    table.setStyle(platypus.TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _FONT_REGULAR),
        ("BACKGROUND", (0, 0), (-1, 0), _pdf_color(system, ColorRole.SURFACE_EMPHASIS)),
        ("GRID", (0, 0), (-1, -1), 0.5, _pdf_color(system, ColorRole.BORDER)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    flows.append(table)
    return flows


def _render_callout(component, system, styles, platypus):
    data = [[
        [
            _paragraph(component.label, styles[TypographyRole.HEADING], platypus),
            _paragraph(component.statement, styles[TypographyRole.BODY_EMPHASIS], platypus),
            _paragraph(f"Rationale: {component.rationale}", styles[TypographyRole.BODY], platypus),
            _paragraph(f"Category: {component.category.value}", styles[TypographyRole.CAPTION], platypus),
            _paragraph(
                "Evidence IDs: " + (", ".join(component.evidence_source_ids) or "None recorded"),
                styles[TypographyRole.CAPTION],
                platypus,
            ),
            _paragraph(f"Policy rule: {component.policy_rule_id}", styles[TypographyRole.CAPTION], platypus),
        ]
    ]]
    table = platypus.Table(data, colWidths=[520])
    table.setStyle(platypus.TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _FONT_REGULAR),
        ("BACKGROUND", (0, 0), (-1, -1), _pdf_color(system, ColorRole.SURFACE_EMPHASIS)),
        ("BOX", (0, 0), (-1, -1), 1.2, _pdf_color(system, ColorRole.BORDER_EMPHASIS)),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return [table]


def _render_collection(component, system, styles, platypus):
    flows = _section(component.label, styles, platypus)
    flows.append(_paragraph(
        f"Total available: {component.total_available}  |  Selected: "
        f"{component.selected_count}  |  Omitted: {component.omitted_count}",
        styles["caption-secondary"],
        platypus,
    ))
    flows.append(platypus.Spacer(1, 5))
    if not component.records:
        flows.append(_paragraph(component.empty_state, styles[TypographyRole.BODY], platypus))
        return flows
    for index, record in enumerate(component.records):
        if index:
            flows.append(platypus.Spacer(1, 5))
        flows.append(_paragraph(
            f"{index + 1}. {_report_value(record.title)}",
            styles[TypographyRole.SUBHEADING],
            platypus,
        ))
        flows.append(_paragraph(
            f"ID: {_report_value(record.source_id)}",
            styles[TypographyRole.MONOSPACE_IDENTIFIER],
            platypus,
        ))
        facts = (
            ("Status", _report_value(record.status)),
            ("Priority", _report_value(record.priority)),
            ("Severity", _report_value(record.severity)),
            ("Owner", _report_value(record.owner)),
            ("Relevant date", _report_value(record.relevant_date)),
            ("Overdue", "Yes" if record.overdue.value else "No"),
            ("Active", "Yes" if record.active.value else "No"),
        )
        flows.append(_paragraph(
            "  |  ".join(f"{label}: {value}" for label, value in facts),
            styles["caption-secondary"],
            platypus,
        ))
        for label, value in (
            ("Description", record.description),
            ("Impact", record.impact),
            ("Response", record.response),
        ):
            flows.append(_paragraph(
                f"{label}: {_report_value(value)}",
                styles[TypographyRole.BODY],
                platypus,
            ))
        flows.append(platypus.HRFlowable(
            width="100%",
            thickness=0.5,
            color=_pdf_color(system, ColorRole.BORDER),
            spaceBefore=5,
        ))
    return flows


def _render_completeness(component, styles, platypus):
    flows = _section(component.heading, styles, platypus)
    if not component.notices:
        return flows + [_paragraph(component.empty_state, styles[TypographyRole.BODY], platypus)]
    for index, notice in enumerate(component.notices, 1):
        detail = f"{index}. [{notice.importance.value.upper()}] {notice.code}: {notice.message}"
        flows.append(_paragraph(detail, styles[TypographyRole.BODY], platypus))
        if notice.affected_fields:
            flows.append(_paragraph(
                "Affected fields: " + ", ".join(notice.affected_fields),
                styles["caption-secondary"],
                platypus,
            ))
        if notice.affected_record_ids:
            flows.append(_paragraph(
                "Affected record IDs: " + ", ".join(notice.affected_record_ids),
                styles["caption-secondary"],
                platypus,
            ))
    return flows


def _render_semantic_footer(component, styles, platypus):
    text = (
        f"{component.product_name}  |  {component.artifact_type.value}  |  "
        f"Artifact version {component.artifact_version}  |  "
        f"Report date {_report_value(component.report_date)}"
    )
    if component.classification_label:
        text += f"  |  Classification: {component.classification_label}"
    return [_paragraph(text, styles["caption-secondary"], platypus)]


def _section(label, styles, platypus):
    return [
        _paragraph(label, styles[TypographyRole.HEADING], platypus),
        platypus.Spacer(1, 5),
    ]


def _paragraph(value, style, platypus):
    text = escape(str(value), quote=True).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br/>")
    if not text:
        text = " "
    return platypus.Paragraph(text, style)


def _report_value(value):
    if isinstance(value, MissingValue):
        return f"Missing value: {value.reason}"
    return str(value.value)


def _pdf_color(system, role):
    colors = importlib.import_module("reportlab.lib.colors")
    return colors.HexColor(system.color(role).canonical_hex)


def _spacing(system, role):
    system.spacing(role)
    return _SPACING_POINTS[role]


def _draw_page_chrome(canvas, identity, title, classification, *, first, fonts):
    regular, semibold = fonts
    canvas.saveState()
    canvas.setStrokeColorRGB(0.33, 0.39, 0.45)
    canvas.setFillColorRGB(0.09, 0.13, 0.17)
    if not first:
        canvas.setFont(semibold, 7.5)
        canvas.drawString(_MARGINS["left"], 770, identity)
        canvas.setFont(regular, 7.5)
        canvas.drawRightString(612 - _MARGINS["right"], 770, title)
        canvas.line(_MARGINS["left"], 762, 612 - _MARGINS["right"], 762)
    canvas.line(_MARGINS["left"], 34, 612 - _MARGINS["right"], 34)
    canvas.setFont(regular, 7)
    footer = "TPM Operating System | executive_status_report"
    if classification:
        footer += f" | {classification}"
    canvas.drawString(_MARGINS["left"], 22, footer)
    canvas.drawRightString(
        612 - _MARGINS["right"], 22, f"Page {canvas.getPageNumber()}"
    )
    canvas.restoreState()


def _page_identity(artifact):
    for component in artifact.components:
        if isinstance(component, ArtifactHeader):
            return (
                f"{_report_value(component.program_name)} | "
                f"{_report_value(component.report_date)}"
            )
    return artifact.title


def _classification(artifact):
    for component in artifact.components:
        if isinstance(component, ArtifactHeader):
            return component.classification_label
    return None


def _footer_product(artifact):
    for component in artifact.components:
        if isinstance(component, ArtifactFooter):
            return component.product_name
    return "TPM Operating System"


def _canvas_factory(canvas_type, deterministic_test_mode, report_date):
    """Create canvases without allowing ReportLab to acquire the wall clock."""

    class ExplicitTimestampCanvas(canvas_type):
        def __init__(self, *args, **kwargs):
            # Invariant construction prevents ReportLab's PDFDocument from reading
            # the wall clock. Production metadata is replaced from supplied truth.
            kwargs["invariant"] = True
            super().__init__(*args, **kwargs)
            if not deterministic_test_mode:
                self._doc.invariant = 0
                self._doc._timeStamp = _timestamp_from_report_date(report_date)

    return ExplicitTimestampCanvas


def _timestamp_from_report_date(value):
    try:
        parsed = datetime.strptime(str(value), "%Y-%m-%d")
    except (TypeError, ValueError) as error:
        raise ArtifactConfigurationError(
            "pdf-report-date-invalid",
            "PDF metadata requires an ISO report date.",
        ) from error

    class SuppliedTimestamp:
        t = int(parsed.replace(tzinfo=None).timestamp())
        lt = parsed.timetuple()
        YMDhms = (
            parsed.year,
            parsed.month,
            parsed.day,
            parsed.hour,
            parsed.minute,
            parsed.second,
        )
        dhh = 0
        dmm = 0
        tzname = "UTC"

    return SuppliedTimestamp()


def _font_assets_are_valid(asset_dir):
    try:
        validate_inter_font_assets(asset_dir=asset_dir)
    except FontAssetError:
        return False
    return True
