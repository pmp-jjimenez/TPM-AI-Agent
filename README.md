# TPM Operating System

TPM Operating System is an enterprise program intelligence product for Technical Program Managers to plan, execute, monitor, and communicate complex technology programs.

The current release is [v0.7.0 — Foundation & Experience](docs/releases/v0.7.0-foundation-and-experience.md), the first demonstrable product release. It combines a canonical program domain, local Python workflows, a read-only FastAPI service, and a React enterprise application experience. The runtime remains a single-user local development baseline and has not been deployed to production.

## Current Experience

The browser application provides an enterprise Application Shell, Home Command Center, Programs experience, and Program Mission Control. It presents canonical Programs, Actions, Risks, Issues, Dependencies, and Decision Records through a read-only API. Mission Control's AI Assessment is currently a preview and the web interface has no editing workflows.

The existing CLI remains available for local program workflows, executive report generation, SOW intake, and Gemini-backed operations where configured.

Run it from the repository root:

```bash
python3 app/main.py
```

Install the current Python dependencies first when needed:

```bash
python3 -m pip install -r requirements.txt
```

Gemini-backed workflows require a `GEMINI_API_KEY`. Local program-management workflows remain filesystem based. See [QUICKSTART.md](QUICKSTART.md) and [docs/DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) for current setup and usage details.

## Repository Boundaries

The long-term repository boundary is:

```text
backend/   FastAPI read-only service boundary
frontend/  React + TypeScript browser application
shared/    Future cross-boundary schemas and shared models
docs/      Product and engineering documentation
scripts/   Development and operational utilities
```

For backward compatibility, the core Python implementation remains in `app/`. The API delegates to that application boundary rather than duplicating domain and persistence behavior.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for current and target architecture details.

## Current Capabilities

- Canonical Programs, Actions, Risks, Issues, Dependencies, and Decision Records.
- Deterministic Persona Routing.
- Enterprise Application Shell and responsive navigation.
- Home Command Center and read-only Programs experience.
- Program Mission Control with executive health and operational records.
- Product Design System and accessibility foundation.
- Local CLI workflows, SOW intake, and Markdown executive status reports.

## Repository Status

v0.7.0 is complete. The next product version is **v0.8 Intelligence**, and the next engineering sprint is **DX-1.0 Developer Console**. See the [roadmap](docs/ROADMAP.md) for direction and the [canonical release document](docs/releases/v0.7.0-foundation-and-experience.md) for delivered scope and limitations.
