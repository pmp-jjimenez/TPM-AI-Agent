# TPM Operating System Architecture

This document describes the current repository architecture first. Future architecture considerations are listed separately and should not be interpreted as implemented behavior.

## Current Architecture

The current product is a local CLI application backed by Markdown knowledge assets, JSON program persistence, and optional Gemini API calls.

### Components

| Component | Current Responsibility |
|---|---|
| CLI | Presents menu options, captures user input, and prints feedback. |
| `app/main.py` | Application entry point. Displays product header, version `0.2-dev`, menu options, and delegates routing. |
| `app/router.py` | Routes menu selections for New Program, Active Program, placeholder modes, and exit behavior. |
| `app/engine.py` | Runs the New Program analysis flow: loads context, builds prompt, saves prompt, calls Gemini, prints and saves response. |
| `app/llm.py` | Sends prompt payloads to the Gemini API when `GEMINI_API_KEY` is configured. |
| `app/memory.py` | Creates, loads, saves, and lists JSON program records under `data/programs/`. |
| `app/workspace.py` | Provides Active Program Workspace actions for risks, issues, decisions, next actions, health updates, and executive report generation. |
| `app/executive.py` | Generates Markdown Executive Status Reports under `reports/executive/`. |
| `app/context_loader.py` | Loads selected Markdown context files for New Program prompt construction. |
| `app/prompt_builder.py` | Builds the structured New Program prompt sent to the AI model. |
| Markdown knowledge assets | Provide reusable TPM instructions, frameworks, playbooks, templates, personas, and examples. |
| JSON program persistence | Stores program state locally in `data/programs/*.json`. |
| Gemini API | Provides AI-generated analysis for the New Program flow. |
| Generated sessions and reports | `sessions/last_prompt.md`, `sessions/last_response.md`, and reports under `reports/executive/` are generated at runtime. |

## Main Execution Flow

1. User runs the CLI application.
2. `app/main.py` prints the TPM Operating System header and menu.
3. User selects a menu option.
4. `app/main.py` calls `route(option)` from `app/router.py`.
5. `app/router.py` dispatches to the selected flow.

Current menu entries exist for New Program, Active Program, Major Incident, Executive Review, Operational Readiness, and Exit. Major Incident, Executive Review, and Operational Readiness currently print placeholder text only.

## New Program Flow

1. User selects `Start a New Program`.
2. `app/router.py` prompts for project description and program name.
3. `app/memory.py` creates a JSON program record under `data/programs/`.
4. `app/engine.py` loads core context through `app/context_loader.py`.
5. `app/prompt_builder.py` builds an AI-ready initial TPM assessment prompt.
6. `app/engine.py` saves the prompt to `sessions/last_prompt.md`.
7. `app/llm.py` calls the Gemini API if `GEMINI_API_KEY` is configured.
8. The AI response is printed and saved to `sessions/last_response.md`.

## Active Program Workspace Flow

1. User selects `Manage an Active Program`.
2. `app/router.py` lists available JSON program records from `data/programs/`.
3. User selects a program.
4. `app/workspace.py` loads the selected program and shows a summary.
5. User can perform workspace actions:
   - Add Risk.
   - Add Decision.
   - Add Next Action.
   - Update Health.
   - Generate Executive Report.
   - Add Issue.
   - List Open Issues.
   - Close Issue.
6. `app/memory.py` saves updated program state after mutating actions.
7. `app/executive.py` writes Markdown reports when requested.

## Data Storage

Current data storage is local filesystem storage:

- Program records: `data/programs/*.json`.
- Last generated AI prompt: `sessions/last_prompt.md`.
- Last generated AI response: `sessions/last_response.md`.
- Executive reports: `reports/executive/*.md`.
- Static operating knowledge: Markdown files under `instructions/`, `knowledge/`, `playbooks/`, `templates/`, `personas/`, `examples/`, and `tests/`.

There is no database, schema migration layer, multi-user storage, authentication, or server-side persistence service in the current implementation.

## AI Boundary

The AI model is used in the New Program flow only:

- The system loads selected local Markdown context.
- The system builds a prompt with that context and the user's project description.
- The system calls Gemini through `app/llm.py`.
- The system stores the prompt and response as generated session files.

The AI does not autonomously modify program JSON, close issues, update health, create reports, route expert personas, upload documents, or operate a web interface. Human CLI input currently drives state-changing workspace actions.

## Current Limitations

- CLI-only user experience.
- Local JSON files are the only program persistence mechanism.
- No formal schema validation or migrations for program records.
- No automated test suite is currently wired to validate application behavior.
- No implemented web interface.
- No implemented Docker runtime.
- No implemented dependency management with `uv`.
- No implemented SOW upload flow.
- Major Incident, Executive Review, and Operational Readiness are menu placeholders only.
- No implemented AI Expert Council routing.
- Executive report generation is Markdown-only and relatively simple.
- Gemini model availability and behavior depend on external API access and a configured `GEMINI_API_KEY`.

## Future Architecture Considerations

Future architecture may include:

- A web application layer for the Program Workspace.
- A more robust program data model with validation, versioning, and migration support.
- A document ingestion service for SOWs and related program artifacts.
- An expert routing layer that selects personas and produces TPM-synthesized council reviews.
- A report generation layer for professional PowerPoint, PDF, and executive packages.
- Docker packaging for consistent local and hosted runtime behavior.
- Dependency management through `uv`.
- A durable database if the product moves beyond local single-user operation.
- Authentication, authorization, audit logging, and tenant isolation for any SaaS direction.

These are future considerations and are not implemented in the current codebase.
