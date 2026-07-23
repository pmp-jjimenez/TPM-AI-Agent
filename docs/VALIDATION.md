# Validation

This document describes how to validate the TPM Operating System development environment and regression foundation.

## Automated Tests

Run:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The test suite uses Python's built-in `unittest` library. It does not require `GEMINI_API_KEY`, does not call Gemini, and does not make network calls.

Current automated coverage validates:

- Exact ReportLab dependency declaration and isolation from renderer-neutral modules.
- Versioned Inter 4.1 asset presence, license, supported weights, and checksums.
- ReportLab backend readiness, bounded missing/version/font failures, and temporary
  global-configuration restoration.
- Immutable ExecutiveReportViewModel construction, source classification, complete
  normalized collections, deterministic status/count/ordering/overdue/recommendation
  policies, compatibility safety, and completeness notices without ReportLab.
- Immutable SemanticArtifact contracts, the closed eight-component vocabulary, exact
  executive component order, accessibility labels, truthful empty states, and
  selection policy 1.0. Composer tests prove that default/custom limits disclose
  omissions, preserve supplied ordering and classifications, and leave the complete
  view model unchanged.
- Immutable Artifact Design System identity and closed typography, spacing, color,
  surface, border, status, emphasis, component, and density vocabularies. Tests
  validate strict immutable lookup, complete references, health-to-visual-role
  mapping, non-adaptive density, contrast requirements, textual reinforcement,
  grayscale policy, and rejection of incomplete or contradictory systems without
  importing renderer libraries.
- In-memory ReportLab rendering of all eight components on US Letter portrait pages,
  bundled Inter embedding, selectable escaped text, pagination and repeated page
  chrome, PDF security structure, metadata, invariant byte equality, input
  immutability, and serialized/restored ReportLab global configuration.
- Program memory create, save, and reload behavior in a temporary directory.
- Prompt builder inclusion of project description, TPM context, and expected assessment sections.
- Executive report generation in a temporary reports directory.
- Workspace issue helper behavior for open issues and older issue records without owner or due date.

The automated tests do not validate:

- Gemini API behavior.
- Interactive CLI input flows end to end.
- Real program records under `data/programs/`.
- Real report generation under `reports/`.
- Generated session files under `sessions/`.
- Human visual approval of the Executive Status Report PDF.
- Certified PDF/UA, tagged-PDF, WCAG, or screen-reader conformance.
- Production PDF filesystem output, filenames, and CLI integration.
- Future Docker, incident, readiness, PowerPoint, or HTML artifact workflows.

## Environment Doctor

Run:

```bash
python scripts/doctor.py
```

The doctor performs safe local diagnostics only. It does not install packages, generate reports, modify program JSON records, call external services, or print secrets.

Result meanings:

- `[PASS]`: The check succeeded.
- `[WARN]`: The check found a non-blocking setup gap or optional tool is unavailable.
- `[FAIL]`: The check found a required condition that should be fixed before development or validation.

The command exits with code `0` when there are no `[FAIL]` results. It exits with code `1` when at least one `[FAIL]` result exists.

The doctor validates:

- Python version is 3.9 or newer.
- The current directory appears to be the repository root.
- Required project directories exist.
- Core application modules can be imported.
- ReportLab 5.0.0 is installed.
- Bundled Inter 4.1 Regular and SemiBold assets pass checksum validation.
- `data/programs/` exists and is writable.
- `reports/` exists and is writable, or could be created from the repository root.
- `sessions/` exists and is writable, or could be created from the repository root.
- `GEMINI_API_KEY` is configured or missing.
- Git, Codex, and GitHub CLI availability.

The doctor does not validate:

- Gemini credentials by calling Gemini.
- GitHub authentication.
- Codex authentication.
- Network access.
- Dependency installation.
- Full CLI behavior.
- JSON schema migration safety.
- Final PDF rendering or visual quality.

## Manual Validation Before Committing

Before committing a change, run:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/doctor.py
git diff --check
git status --short
```

Also inspect the diff for accidental changes to generated artifacts or local program records:

```bash
git diff --stat
git diff -- data/programs reports sessions
```

Do not commit generated reports, generated session artifacts, secrets, or unintended changes to program JSON records.

## PDF visual fixtures and manual review

Run:

```bash
.venv/bin/python scripts/generate_pdf_visual_fixtures.py
ls -lh reports/pdf-visual-fixtures
```

The ignored directory contains sparse, healthy compact, warning, critical, long
multipage, missing-data, special-character, and omitted-record scenarios. Automated
tests do not claim visual approval.

For every fixture, manually review hierarchy, typography, spacing, recommendation
prominence, wrapping, long IDs, special characters, multipage flow, repeated page
chrome, numbering, grayscale readability, textual status distinction, empty and
missing states, omission disclosure, completeness notices, evidence visibility,
clipping, and reasonably avoidable orphaned headings. The renderer provides
selectable text and component-order reading flow but does not claim PDF/UA, tagged
PDF, WCAG, or screen-reader certification.

Paragraph alignment remains left-aligned for IDs, metadata, metrics, technical
record fields, completeness codes, affected-record lists, empty-state messages,
and page headers and footers. Selective justification of narrative paragraphs may
be evaluated in a later increment; universal justification is not approved and is
not part of the caution-color correction.
