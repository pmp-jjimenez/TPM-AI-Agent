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
- Final Executive Status Report PDF content, layout, pagination, and visual quality.
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
