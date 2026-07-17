# Project Structure

This document describes the repository as it exists today.

## Repository Tree

```text
.
├── .gitignore
├── CONTRIBUTING.md
├── QUICKSTART.md
├── README.md
├── START HERE.md
├── backend/
│   └── README.md
├── frontend/
│   └── README.md
├── shared/
│   ├── README.md
│   ├── models/
│   │   └── README.md
│   └── schemas/
│       └── README.md
├── app/
│   ├── context_loader.py
│   ├── engine.py
│   ├── executive.py
│   ├── llm.py
│   ├── main.py
│   ├── memory.py
│   ├── prompt_builder.py
│   ├── router.py
│   ├── test_gemini.py
│   └── workspace.py
├── data/
│   └── programs/
│       └── microsoft-teams-latam.json
├── docs/
│   ├── AI_EXPERT_COUNCIL.md
│   ├── ARCHITECTURE.md
│   ├── BACKLOG.md
│   ├── DEVELOPER_SETUP.md
│   ├── PRODUCT_VISION.md
│   ├── PROJECT_STRUCTURE.md
│   ├── RELEASES.md
│   └── ROADMAP.md
├── examples/
│   └── microsoft-teams.md
├── instructions/
│   ├── master-prompt.md
│   ├── reasoning-engine.md
│   ├── system-prompt.md
│   └── workflow-engine.md
├── knowledge/
│   ├── capability-router.md
│   ├── confidence-engine.md
│   ├── decision-model.md
│   ├── knowledge-transfer-framework.md
│   ├── program-state-model.md
│   ├── recommendation-engine.md
│   ├── service-transition-framework.md
│   ├── sow-analysis-framework.md
│   ├── stakeholder-communication-framework.md
│   ├── status-health-model.md
│   ├── tpm-frameworks.md
│   └── tpm-workflow-decision-engine.md
├── personas/
│   ├── change-manager.md
│   ├── cloud-architect.md
│   ├── customer-success-advisor.md
│   ├── delivery-manager.md
│   ├── executive-advisor.md
│   ├── incident-commander.md
│   ├── operations-manager.md
│   ├── security-advisor.md
│   └── technical-program-manager.md
├── playbooks/
│   ├── daily-tpm-assistant.md
│   ├── executive-program-review.md
│   ├── incident-commander-mode.md
│   ├── internal-delivery-readiness-review.md
│   ├── operational-readiness-review.md
│   ├── postmortem-continuous-improvement.md
│   ├── project-charter-generation.md
│   ├── project-discovery.md
│   ├── sow-to-program-initiation.md
│   └── tpm-program-lifecycle.md
├── prompts/
├── reports/
│   └── executive/
│       └── microsoft-teams-latam_executive_status.md
├── requirements.txt
├── sessions/
│   ├── last_prompt.md
│   └── last_response.md
├── templates/
│   ├── executive-dashboard.md
│   ├── executive-status-update.md
│   ├── handoff-package.md
│   ├── operational-readiness-assessment.md
│   ├── program-initiation-package.md
│   ├── project-charter.md
│   ├── raid-log.md
│   ├── sow-analysis-report.md
│   └── stakeholder-map.md
└── tests/
    ├── confidence-test.md
    └── microsoft-teams/
        ├── expected-output.md
        └── scenario.md
```

macOS `.DS_Store` files may also exist locally. They are not part of the application design.

## Top-Level Directories

### `backend/`

Backend architecture boundary. The current Python implementation remains under `app/` to preserve imports, tests, and CLI behavior; `backend/` contains foundation documentation only in this sprint.

### `frontend/`

Reserved for a future React + TypeScript application. It contains documentation only and has no generated application or dependencies.

### `shared/`

Reserved for future versioned schemas and cross-boundary model contracts. Its current subdirectories are documentation placeholders only.

### `app/`

Python CLI application modules. This is the executable layer that reads user input, loads Markdown context, calls Gemini, persists program JSON, and generates Markdown reports.

### `data/`

Local program persistence. The current application stores program records as JSON files under `data/programs/`.

### `docs/`

Project documentation, including architecture, roadmap, backlog, release notes, product vision, developer setup, and repository structure.

### `examples/`

Example program material used as reference content for expected TPM outputs and scenarios.

### `instructions/`

Core prompt and reasoning instructions for the TPM Operating System. `app/context_loader.py` currently loads `instructions/master-prompt.md` into the New Program prompt context.

### `knowledge/`

Reusable TPM frameworks and decision models. These Markdown assets define concepts such as capability routing, confidence, program state, recommendations, service transition, SOW analysis, stakeholder communication, status health, and TPM workflows.

### `personas/`

Role-specific expert perspectives. These files describe advisory personas such as Technical Program Manager, Executive Advisor, Incident Commander, Security Advisor, and related delivery roles. They are documented assets; the current CLI does not dynamically route persona execution.

### `playbooks/`

Procedure-oriented TPM workflows. These files describe repeatable practices such as project discovery, SOW-to-program initiation, operational readiness, executive review, incident command, and lifecycle management.

### `prompts/`

Prompt asset directory. It currently exists as an empty top-level directory and is not loaded by the current Python application.

### `reports/`

Generated report output. The current executive report generator writes Markdown files under `reports/executive/`.

### `sessions/`

Generated AI session artifacts. The New Program flow writes the last generated prompt to `sessions/last_prompt.md` and the last Gemini response to `sessions/last_response.md`.

### `templates/`

Markdown document templates for program artifacts such as charters, RAID logs, executive dashboards, handoff packages, readiness assessments, and stakeholder maps.

### `tests/`

Markdown-based scenarios and expected outputs. These are reference test assets; there is no currently wired automated test runner in the repository.

## Python Modules Under `app/`

### `app/main.py`

CLI entry point. It prints the product header, version, and menu options, collects the selected option, and delegates routing to `router.route`.

### `app/router.py`

Menu dispatcher. It handles New Program setup, Active Program selection, placeholder menu entries, and exit behavior.

### `app/engine.py`

New Program analysis flow. It validates the project description, loads Markdown context, builds the AI prompt, writes `sessions/last_prompt.md`, calls Gemini through `llm.generate_response`, prints the response, and writes `sessions/last_response.md`.

### `app/llm.py`

Gemini API client. It reads `GEMINI_API_KEY` from the environment, builds the API request with Python standard library modules, sends the prompt to the configured Gemini model, and returns either generated text or an error string.

### `app/memory.py`

Local JSON persistence layer. It creates, loads, saves, and lists program records under `data/programs/`.

### `app/workspace.py`

Active Program workspace. It displays a program summary and supports adding risks, decisions, next actions, and issues; updating health; listing and closing open issues; and generating executive reports.

### `app/executive.py`

Executive report generator. It creates `reports/executive/` when needed and writes a Markdown executive status report for a program.

### `app/context_loader.py`

Markdown context loader. It reads selected instruction, knowledge, playbook, and template files and combines them into the context used by the New Program prompt.

### `app/prompt_builder.py`

Prompt construction module. It builds the structured New Program assessment prompt from the user project description and loaded TPM context.

### `app/test_gemini.py`

Manual Gemini smoke-test script. It sends a short prompt through `llm.generate_response` and prints the response.

## Directory Interactions

### `knowledge/`

Knowledge files provide reusable TPM models and frameworks. `app/context_loader.py` currently loads selected files from this directory into the New Program prompt context.

### `playbooks/`

Playbooks describe procedural workflows. `app/context_loader.py` currently loads `playbooks/sow-to-program-initiation.md` for the New Program flow. Other playbooks are available as documented assets but are not automatically loaded by the current code.

### `templates/`

Templates define expected artifact structures. `app/context_loader.py` currently loads `templates/project-charter.md` and `templates/raid-log.md` into New Program prompt context.

### `personas/`

Personas define role-based advisory perspectives. They interact with the rest of the repository as reference knowledge for future or manual prompt composition. The current CLI does not directly load persona files.

### `tests/`

Tests currently exist as Markdown scenarios and expected outputs. They provide reference material for manual validation and future automated tests.

### `data/`

`data/programs/` stores JSON program state used by `app/memory.py`, `app/router.py`, and `app/workspace.py`. Workspace actions mutate these JSON records.

### `reports/`

`reports/executive/` receives Markdown reports generated by `app/executive.py` through the Active Program workspace.

### `sessions/`

`sessions/` receives the latest generated prompt and response from `app/engine.py`. These files capture the most recent New Program AI interaction.

### `prompts/`

`prompts/` is present but empty. The current application builds prompts in Python through `app/prompt_builder.py` rather than loading prompt files from this directory.

### `docs/`

`docs/` explains the product, architecture, roadmap, backlog, releases, developer setup, and repository structure. It should be updated when behavior, workflows, or repository organization change.

## Current Runtime Flow

1. `app/main.py` starts the CLI.
2. `app/router.py` dispatches the selected menu option.
3. New Program creates a JSON record through `app/memory.py`.
4. `app/engine.py` loads selected Markdown assets from `instructions/`, `knowledge/`, `playbooks/`, and `templates/`.
5. `app/prompt_builder.py` builds a Gemini-ready prompt.
6. `app/llm.py` calls Gemini when `GEMINI_API_KEY` is available.
7. `sessions/` stores the latest prompt and response.
8. Active Program workspace reads and writes `data/programs/*.json`.
9. Executive report generation writes Markdown output to `reports/executive/`.
