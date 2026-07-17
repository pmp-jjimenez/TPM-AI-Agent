# TPM Operating System

TPM Operating System is the product evolution of TPM AI Agent: an AI-assisted operating system for Technical Program Managers to plan, execute, monitor, and communicate complex technology programs.

The repository is being prepared for a production-grade SaaS architecture. The current product remains a local Python CLI, and this foundation work does not introduce a web application, API server, or behavioral changes.

## Current CLI

The existing CLI continues to be the supported application interface. It helps Technical Program Managers create and manage programs, maintain risks, issues, decisions, and next actions, generate executive status reports, and use Gemini-backed analysis where configured.

Run it from the repository root:

```bash
python3 app/main.py
```

Install the current Python dependencies first when needed:

```bash
python3 -m pip install -r requirements.txt
```

Gemini-backed workflows require a `GEMINI_API_KEY`. Local program-management workflows remain filesystem based. See [QUICKSTART.md](QUICKSTART.md) and [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) for current setup and usage details.

## Product Direction

The long-term repository boundary is:

```text
backend/   Python application and future service/API boundary
frontend/  Future React + TypeScript application
shared/    Future cross-boundary schemas and shared models
docs/      Product and engineering documentation
scripts/   Development and operational utilities
```

For backward compatibility, the current Python backend implementation remains in `app/`. Moving or renaming those modules is intentionally deferred until a separately tested migration can preserve every import and CLI entry point. The `frontend/` directory contains no generated React code, and no API framework has been introduced.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for current and target architecture details.

## Current Capabilities

- Standardize Technical Program Management practices.
- Create and maintain local program records.
- Track risks, issues, decisions, actions, and program health.
- Generate Markdown executive status reports.
- Build AI-assisted program assessments and SOW intake outputs.
- Route documented expert personas deterministically.

## Repository Status

Under active development. The SaaS boundaries are architectural placeholders; the current runtime is still the existing CLI.
