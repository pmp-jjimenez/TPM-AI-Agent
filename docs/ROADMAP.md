# TPM Operating System Roadmap

This roadmap describes product direction without assigning fabricated dates. Version labels reflect current repository language and likely maturity stages, not committed delivery schedules.

## Current State

**v0.7.0 — Foundation & Experience is complete.** It is the first demonstrable
product release and establishes the canonical program domain, read-only API,
enterprise Application Shell, Home Command Center, Programs experience, Program
Mission Control, Product Design System, responsive and accessibility foundations,
and visual product identity.

The runtime remains a single-user local development baseline. Mission Control AI
Assessment is a preview, the web interface is read-only, and there is no production
deployment. See the canonical [v0.7.0 release document](releases/v0.7.0-foundation-and-experience.md)
for the delivered scope and complete limitations.

## Next

- **Next product version:** v0.8 Intelligence.
- **Next engineering sprint:** DX-1.0 Developer Console.

v0.8 will build grounded, explainable intelligence capabilities on the v0.7 domain
and experience foundation. DX-1.0 will first strengthen the local developer
operating experience and provide a dependable console for inspecting the system.

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
