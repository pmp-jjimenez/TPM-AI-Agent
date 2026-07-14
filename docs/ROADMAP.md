# TPM Operating System Roadmap

This roadmap describes product direction without assigning fabricated dates. Version labels reflect current repository language and likely maturity stages, not committed delivery schedules.

## Current State

The product is a CLI-based TPM assistant with local Markdown knowledge assets and JSON program persistence.

Implemented:

- CLI entry point and routing.
- New Program flow that creates a program record, builds an AI-ready prompt, loads selected TPM context, calls Gemini, and saves generated prompt and response files.
- Active Program Workspace flow for viewing summary data and managing risks, issues, decisions, next actions, program health, and executive reports.
- Issue management with issue description, owner, due date validation, open issue listing, and closure.
- Markdown Executive Status Report generation.
- Markdown knowledge assets, playbooks, templates, examples, and tests.

Present but not fully implemented:

- CLI placeholders for Major Incident, Executive Review, and Operational Readiness.
- Markdown knowledge and templates for SOW analysis, incident command, operational readiness, service transition, executive communication, and related TPM workflows.

## Version 0.1

Objective: establish the initial MVP for an AI-powered TPM assistant.

Scope reflected by repository history:

- Basic TPM assistant concept.
- Markdown persona, playbook, template, and knowledge foundation.
- Initial project artifact orientation.
- Early CLI usage pattern.

## Version 0.2-dev

Objective: turn the MVP into a program operating workspace.

Implemented in the current branch:

- Program memory and workspace actions.
- Executive Status Report generation.
- CLI product header aligned to TPM Operating System.
- Issue Management in the Program Workspace.
- Issue owner and due date capture.
- Open issue listing.
- Issue closure.
- Date validation and CLI feedback.
- Documentation foundation for product vision, roadmap, backlog, architecture, releases, and AI Expert Council personas.

Planned next areas:

- Broader Program Workspace data model.
- Automated tests for memory, workspace actions, prompt creation, routing, and reports.
- Stronger program data validation.

## Version 0.5

Objective: create a reliable local TPM operating environment.

Planned areas:

- Program Workspace:
  - Expanded RAID support for assumptions, dependencies, changes, milestones, meeting history, and documents.
  - More consistent workspace navigation and feedback.
  - Better summaries for active program state.

- Program Data Foundation:
  - Versioned program schema.
  - Validation and migration strategy.
  - Safer handling of malformed or missing program data.
  - Clear separation between user-entered state and generated artifacts.

- Executive Intelligence:
  - Improved executive summaries.
  - Decision-required views.
  - Business impact framing.
  - Trend and confidence reasoning where supported by stored evidence.

- Automated Testing:
  - Unit coverage for core functions.
  - Workspace behavior tests.
  - Report generation tests.
  - Regression scenarios based on examples.

- Dependency Management with `uv`:
  - Project dependency definition.
  - Reproducible local setup.
  - Documented runtime commands.

## Version 1.0

Objective: provide a coherent TPM product experience suitable for repeated real program usage.

Planned areas:

- Web Interface:
  - Browser-based Program Workspace.
  - Views for program state, RAID, issues, decisions, actions, artifacts, and reports.
  - Clear separation between implemented actions and AI-generated recommendations.

- SOW Upload and Analysis:
  - Document intake workflow.
  - Extraction of scope, deliverables, milestones, assumptions, dependencies, risks, and clarification questions.
  - Output aligned with existing SOW analysis framework and templates.

- Major Incident Mode:
  - Structured incident intake.
  - Severity and impact assessment.
  - Action and owner tracking.
  - Executive communication support.
  - Post-incident review support.

- Operational Readiness:
  - ORR checklist workflows.
  - Knowledge transfer tracking.
  - Monitoring, support, security, and acceptance gates.
  - Go / Go with Risks / No-Go recommendation support based on evidence.

- Professional PowerPoint Generation:
  - Executive-ready deck generation.
  - Status, steering committee, readiness, and incident review decks.
  - Consistent formatting and branding support.

- Docker:
  - Containerized local runtime.
  - Documented development and run commands.
  - Foundation for later deployment environments.

## Future Vision

Longer-term opportunities:

- AI Expert Council:
  - Routing to specialized expert personas.
  - Structured multi-perspective reviews for readiness, incidents, security, delivery, operations, and executive decisions.
  - TPM-led synthesis of recommendations.

- SaaS Possibility:
  - Multi-user collaboration.
  - Secure document handling.
  - Organization-level program portfolio views.
  - Integrations with project management, communication, incident, and document systems.
  - Auditability, permissions, and operational controls.

- Advanced Intelligence:
  - Portfolio health analytics.
  - Dependency and risk propagation.
  - Decision history and rationale tracking.
  - Lessons learned reuse across programs.
