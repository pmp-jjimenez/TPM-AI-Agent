# TPM Operating System Release History

This release history is based on the actual Git history available in the repository. Some commits do not carry explicit sprint numbers. Where exact sprint mapping is uncertain, that uncertainty is stated rather than inferred.

## Initial MVP

Git commit: `ee26c59` - `MVP v0.1 - AI-powered TPM Operating System`

Known from repository state:

- Established the AI-powered TPM assistant concept.
- Introduced foundational Markdown assets for TPM personas, playbooks, templates, knowledge, examples, or tests.
- Created the early project structure for a TPM-oriented assistant.

Exact feature boundaries for this initial commit should be verified from the commit contents before assigning more detailed sprint scope.

## Program Memory and Workspace Actions

Git commit: `b711ee5` - `Add program memory and workspace actions`

Implemented:

- Program memory support in `app/memory.py`.
- Active Program Workspace behavior in `app/workspace.py`.
- Routing updates in `app/router.py`.
- Example program data under `data/programs/`.

Sprint mapping is uncertain from the commit message alone.

## Executive Status Report

Git commit: `6d52120` - `Sprint 38: Add Executive Status Report generation`

Implemented:

- Markdown Executive Status Report generation in `app/executive.py`.
- Workspace option for generating executive reports.
- Report output under `reports/executive/` at runtime.

## Codex Integration Workflow

Git commit: `cb0acae` - `Sprint 39: Update CLI product header with Codex`

Implemented:

- Updated CLI product header and menu presentation in `app/main.py`.
- Aligned the visible CLI product language with the TPM Operating System direction.

The exact scope of "Codex integration workflow" beyond the CLI header is not fully evident from the commit summary, so this release entry does not claim additional implemented runtime capability.

## Issue Management

Git commit: `8a58339` - `Sprint 40: Add issue management to program workspace`

Implemented:

- Added issue management capability to the Active Program Workspace.
- Added an issue entry flow to program state.

## Issue Owner and Due Date

Git commit: `6194064` - `Sprint 40: Add issue ownership listing and closure`

Implemented:

- Issue owner capture.
- Due date capture.
- Open issue listing.
- Issue closure flow.

## Open Issue Listing

Git commit: `6194064` - `Sprint 40: Add issue ownership listing and closure`

Implemented:

- Display of open issues.
- Display of issue owner, due date, and status.

This was delivered in the same commit as owner capture and closure support.

## Issue Closure

Git commit: `6194064` - `Sprint 40: Add issue ownership listing and closure`

Implemented:

- Selection of an open issue by displayed number.
- Validation of selected issue number.
- Update of selected issue status to `Closed`.
- Persistence of the updated program record.

## Date Validation and CLI Feedback

Git commit: `89e247d` - `Sprint 40: Improve issue validation and CLI feedback`

Implemented:

- Due date validation using `YYYY-MM-DD` format.
- Improved CLI feedback for invalid issue input.
- Return-to-workspace prompts after certain issue actions.

## Issue Workflow Continuity

Git commit: `33fe987` - `Sprint 40: Improve issue workflow continuity`

Implemented:

- Additional workflow continuity improvements in `app/workspace.py`.
- Refinements to how issue actions return control to the workspace.

## Documentation Foundation and AI Expert Council Personas

Current working change set: Epic 41 and Epic 42.

Implemented by this documentation-only change set:

- Product vision documentation.
- Roadmap documentation.
- Structured backlog documentation.
- Current architecture documentation.
- Release history documentation.
- AI Expert Council documentation.
- Eight new expert persona documents.

No Python code, JSON program data, dependency installation, or Git commit is part of this change set.

## Persona Routing Foundation v1

Sprint 51.

Implemented:

- Added deterministic persona routing in `app/persona_router.py`.
- Added a canonical persona registry with stable machine-readable identifiers.
- Added routing result structure with `primary_persona`, `supporting_personas`, `reasons`, and `routing_version`.
- Implemented rule-based routing for:
  - New program and program initiation context.
  - Cloud, migration, infrastructure, and architecture context.
  - Major incident, outage, severity, service disruption, and incident mode.
  - Executive review and executive reporting.
  - Operational readiness, production readiness, go-live readiness, and handoff.
  - Security, compliance, privacy, and security-related risk.
  - Adoption, training, communications, and organizational change.
  - Customer satisfaction, customer escalation, retention, and adoption outcome.
  - Delivery execution, schedule pressure, milestone slippage, and dependency coordination.
- Added unittest coverage for default routing, required routing scenarios, simultaneous signals, duplicate prevention, primary exclusion from supporting personas, stable ordering, missing or legacy fields, deterministic output, and input immutability.

Not implemented:

- No multiple AI calls.
- No autonomous agents.
- No Gemini dependency for routing.
- No CLI behavior change.
- No canonical program schema change.

Known limitations:

- Routing uses explicit keyword and structured-field rules only.
- The router does not interpret ambiguous intent beyond deterministic term matching.
- Persona routing is not yet connected to prompt construction, workspace actions, or report generation.

Logical next steps:

- Integrate routing results into CLI workflows and generated prompts.
- Add user-visible routing summaries where useful.
- Build AI Expert Council orchestration only after deterministic routing is exercised in real workflows.
