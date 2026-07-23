# ADR 0001: Use ReportLab as the Isolated ART-1.0 PDF Backend

- Status: Accepted
- Date: 2026-07-23
- Decision owners: Javier Jiménez, Product Owner; TPM Operating System engineering
- Scope: ART-1.0 Executive Artifact Foundation

## Context

ART-1.0 will add an Executive Status Report PDF while preserving the existing
Markdown report. The renderer must support professional multi-page output, selectable
text, tables with repeated headers, bundled typography, deterministic tests, and
structural PDF validation without coupling Program data or future semantic artifact
contracts to a PDF library.

A bounded feasibility proof ran on macOS 15.7.7, Intel x86_64, and CPython 3.9.6.
ReportLab 5.0.0 installed from a universal Python wheel with Pillow and
charset-normalizer as transitive dependencies. It generated and validated a ten-page
US Letter proof using embedded static Inter fonts. No Homebrew package, browser, or
external system renderer was required.

## Decision

- Pin the direct runtime dependency to `reportlab==5.0.0`.
- Keep `pypdf>=5.0.0,<7.0.0` unchanged for selectable-text extraction and future
  structural validation.
- Isolate ReportLab imports and native objects inside explicitly named concrete PDF
  backend modules.
- Keep renderer-neutral contracts, Program domain behavior, persistence, Markdown
  reporting, and CLI orchestration importable without ReportLab.
- Bundle Inter 4.1 Regular 400 and SemiBold 600 static TTF files as application-owned
  assets under the SIL Open Font License 1.1.
- Resolve fonts only from the version-controlled repository location and reject
  missing, altered, unsupported, or checksum-mismatched assets. Do not fall back to
  system or network fonts.
- Use US Letter for the later production PDF renderer.
- Use explicitly injected truthful report metadata for production. The renderer must
  not acquire wall-clock time. ReportLab invariant mode, including its normalized
  year-2000 PDF metadata, is allowed only for deterministic tests.
- Treat `rl_config.documentLang` and `rl_config.invariant` as process-global state:
  apply them only in a bounded, serialized context and restore prior values after
  success or failure.
- Require structural, content, pagination, grayscale, accessibility, and human visual
  regression review before release and before any renderer or font upgrade.

This decision does not implement a PDF renderer, semantic artifact model, report view
model, PDF layout, or CLI PDF action.

## Consequences

- PDF generation will have a reproducible direct dependency and versioned typography.
- Existing Markdown reporting remains independent of ReportLab availability.
- The repository adds approximately 812 KiB of font binaries plus the OFL license and
  source metadata.
- ReportLab and its transitive dependencies must remain compatible with the supported
  Python runtime.
- Renderer tests must account for global configuration, font subsetting, PDF metadata,
  and same-environment versus cross-platform determinism.
- PDF accessibility is not automatic. Selectable text, language metadata, reading
  order, contrast, and any tagging support require explicit implementation and
  validation. This ADR does not claim PDF/UA conformance.

## Alternatives Considered

- **WeasyPrint:** rejected for this environment because the maintained line requires a
  newer Python runtime plus native Pango infrastructure and introduces HTML/CSS
  resource-loading concerns.
- **fpdf2:** retained only as a contingency; it offered no repository-specific
  advantage after the ReportLab proof succeeded.
- **Headless Chromium or wkhtmltopdf:** rejected because they add browser or external
  executable lifecycle, sandboxing, and release-check complexity.
- **Raw pypdf:** retained for validation and extraction, not selected as a flowing
  document-layout engine.

## Upgrade Policy

Any ReportLab, Pillow, charset-normalizer, Inter, or supported-Python upgrade requires:

1. clean-environment installation validation;
2. font checksum and license review;
3. complete backend and frontend regression tests;
4. PDF structural and extracted-content validation;
5. long-content, repeated-header, and pagination tests;
6. grayscale and accessibility checks;
7. visual approval by the Product Owner.
