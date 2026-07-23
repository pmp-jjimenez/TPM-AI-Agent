# TPM Operating System Release History

This release history is based on the actual Git history available in the repository. Some commits do not carry explicit sprint numbers. Where exact sprint mapping is uncertain, that uncertainty is stated rather than inferred.

## DX-1.0 — Developer Console

Implemented the first engineering increment after v0.7.0 as a local, modular Bash
Developer Console. The root `tpm-dev` entry point provides interactive and
non-interactive start, stop, status, test, build, release-check, existing-CLI, and
help workflows. Repository-local PID and log handling verifies recorded process
identity and port ownership, removes stale metadata, avoids broad process-kill
commands, and never stops unrelated services automatically.

The console adds no third-party dependency, does not modify local environment files,
and does not commit, tag, push, deploy, or open a browser.

## v0.7.0 — Foundation & Experience

Status: Complete.

This is the first demonstrable TPM Operating System product release. It establishes
the canonical program domain, read-only API, enterprise Application Shell, Home
Command Center, Programs experience, Program Mission Control, Product Design System,
responsive and accessibility foundations, and Enterprise Program Intelligence
identity.

See the canonical [v0.7.0 release document](releases/v0.7.0-foundation-and-experience.md)
for delivered scope, validation baseline, known limitations, demonstration flow, and
release metadata. The next product version is **v0.8 Intelligence**; the next
engineering sprint is **DX-1.0 Developer Console**.

## Product Design System v1 — UX-1.2.5

Established a centralized Material UI design system for the frontend with a restrained
enterprise palette, semantic surface/border/text/status/confidence tokens, compact
operational typography variants, consistent shape and elevation rules, visible focus
states, and shared component overrides. Raw visual decisions are now concentrated in
the theme rather than repeated across product screens.

Added typed Health, Confidence, Phase, and Severity badges with normalized display
labels, text and marker redundancy, and safe Unknown fallbacks. Shared Surface,
SectionHeader, MetricDisplay, MetadataList, and divider primitives support future
screens. The application shell, Command Center, Program Workspace, feedback states,
and not-found experience use the system without changing routes, business behavior,
backend contracts, or stored domain values. Dark mode, selectable themes, branding,
charts, and full workspace redesign remain out of scope.

## Home Command Center — UX-1.2

Transformed the existing Programs landing experience into a decision-oriented TPM
Command Center within the application shell. The page now presents a time-aware welcome,
portfolio summary metrics derived from existing Program data, structured focus and AI
advisor previews, and a bounded active-program card preview with direct workspace links.

The responsive Material UI composition uses reusable summary, section, focus, advisor,
and program-preview components. Major Incidents and advisor guidance remain explicitly
non-live placeholders. Routes, API behavior, backend logic, persistence, intelligence,
and domain entities are unchanged.

## Decision Record Foundation v1 — US-58.1

Adopted stored Program decisions as canonical `DecisionRecord` entities using the
existing `ProgramEntity`, UUID, ownership, lifecycle, audit, compatibility, and
aggregate-validation foundation. Program Schema `1.5.0` adds the closed proposed,
approved, superseded, and rejected status vocabulary; decision and rationale text;
alternatives considered; decision and review dates; and impact.

New DecisionRecords use UUIDv4 identity. Legacy strings, partial dictionaries,
`decision_id` values, display-case statuses, and string owners normalize without
mutating the source; missing identity uses deterministic UUIDv5. DecisionRecords
participate in aggregate identity and may `relates_to` Risk, Issue, Dependency, or
Action through explicitly stored relationships. No relationship or decision reasoning
is inferred.

Workspace Intelligence remains Contract `1.0.0` and projects stable evidence at
`/decisionsById/<UUID>/title`. The API transports canonical decisions and the workspace
strictly validates and renders a read-only Decision Records section with no editing UI.

## RAID Adoption v1 — Risk Adoption — US-57.1

Adopted stored Program risks as framework-neutral `Risk` entities using the existing
`ProgramEntity`, ownership, lifecycle, audit, and UUID foundation. Program Schema
`1.2.0` adds controlled risk status, probability, impact, and human-assigned priority,
plus optional mitigation, contingency, review, and acceptance data. Accepted risks
require both an acceptance rationale and accepting owner.

New CLI and SOW risks use UUIDv4 identities. Legacy strings, partial dictionaries,
`risk_id` values, display-case statuses, string owners, `due_date`, and `severity`
normalize non-mutatingly into the canonical representation. Missing legacy identity
uses deterministic UUIDv5; explicit save writes canonical Risk JSON. Aggregate identity
and relationship validation now use the combined Action and Risk object registry.

Workspace Intelligence still emits Contract v1 unchanged. Its bounded Risk projection
uses object-keyed RFC 6901 evidence at `/risksById/<UUID>/title`, making a Risk pointer
stable across array reordering. The API transports canonical Risks and the workspace
strictly validates and renders stored Risk cards. Issue and Dependency are not adopted.

## Program Knowledge Model Foundation — US-56.2

Introduced the framework-neutral `ProgramEntity`, owner, lifecycle, audit, UUID, and
typed relationship primitives. Action is the first canonical Program entity, with
closed status and priority vocabularies plus optional ownership, lifecycle, due-date,
completion, and audit fields. New CLI and SOW Actions use UUIDv4 identity.

Legacy action strings, dictionaries, and `action_id` values normalize into the same
runtime representation. Missing legacy IDs receive deterministic UUIDv5 identities;
loads remain non-mutating and explicit saves write Program Schema `1.1.0`. Aggregate
validation enforces unique object identity and valid relationship endpoints. The
frontend renders canonical Actions using `object_id` while the Intelligence Contract
v1, its evidence paths, semantic IDs, prompt, provider, and fallback remain unchanged.

This release does not migrate any entity other than Action and does not add PostgreSQL,
authentication, migrations, relationship inference/UI, persistent intelligence, or
new AI behavior.

## Structured Intelligence Result Contract v1 — US-56.1

Replaced Workspace Intelligence's parallel string arrays with versioned categorized
findings, structured recommendations, decisions required, and exactly one prioritized
next action. Results carry bounded RFC 6901 evidence references and backend-owned,
deterministic stable IDs. The existing single prompt and Gemini provider call use a
strict provider DTO with index relationships; complete backend validation resolves those
indexes to public IDs. Deterministic fallback uses the same final contract builder and
evidence shape as AI output. The Executive Workspace validates and presents the nested
contract without performing AI reasoning or fallback behavior.

Intelligence remains explicitly generated, read-only, and non-persisted. This change
does not introduce IntelligenceRun, evidence snapshot persistence, DecisionRecord or
recommendation feedback persistence, PostgreSQL, authentication, knowledge-model
entities, vector storage, autonomous agents, model training, retries, background jobs,
or deployment changes.

## Workspace Intelligence Integration — US-55.5

Implemented a read-only, explicitly generated intelligence area in the Executive
Program Workspace. FastAPI delegates to a permanent application service that reuses
existing context, prompt construction, persona routing, Gemini configuration, and
grounded deterministic rules. Strict bounded JSON parsing uses all-or-fallback
behavior. Provider failures return visibly labeled fallback intelligence; generated
results are not persisted. CLI and SOW behavior and stored workspace sections remain
compatible.

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

## Sprint 52: CLI Persona Routing Integration v1

Current working change set.

Implemented:

- Integrated the Sprint 51 deterministic persona router with the CLI and New Program prompt path.
- Added CLI integration boundary that builds non-mutating routing context, calls routing once per top-level operation, and provides safe Technical Program Manager fallback if routing fails.
- Added concise CLI persona routing presentation using human-readable names from `PERSONA_REGISTRY`.
- Integrated routing display into:
  - Start New Program.
  - Manage Active Program.
  - Major Incident placeholder.
  - Executive Review placeholder.
  - Operational Readiness placeholder.
- Extended New Program prompt construction with optional `PERSONA ROUTING CONTEXT`.
- Passed the already-calculated routing result from CLI routing into the New Program prompt path.
- Preserved existing prompt-builder callers by keeping routing optional.
- Added focused `unittest` coverage for routing presentation, prompt routing context, route-once integration behavior, fallback, and non-mutation.

Explicit non-goals:

- No multi-agent orchestration.
- No additional Gemini calls.
- No one-call-per-persona behavior.
- No simulated expert debate.
- No program schema change.
- No routing persistence in program JSON.
- No completion of placeholder Major Incident, Executive Review, or Operational Readiness workflows.
- No Stakeholder Council or executive governance persona layer.

Known limitations:

- Persona routing is deterministic and intentionally lightweight.
- Prompt routing context is currently wired into the New Program AI flow only because that is the only current Gemini-backed workflow.
- Placeholder menu items display expected routing but still do not provide full operational workflows.

Recommended next step:

- Sprint 53 should add the next highest-value workflow while reusing the route-once routing pattern.

## Sprint 53: SOW Intake Foundation v1

Implemented:

- Added a New Program submenu that preserves manual creation and adds local SOW PDF intake.
- Added case-insensitive PDF path validation, home expansion, selectable-text extraction metadata, a 120,000-character safety bound, and clear encrypted, malformed, empty, and image-only errors.
- Added one maintained dependency, `pypdf`, solely for PDF text extraction; OCR is not included.
- Added a dedicated factual SOW extraction prompt that requests strict JSON and prohibits fabrication, chain-of-thought exposure, autonomous-agent claims, and additional model calls.
- Added controlled JSON fence removal, parsing, type validation, optional-field normalization, and unusable-response rejection.
- Added non-mutating mapping to canonical program records, including customer, objective, initiation defaults, confidence, stable-ID risks, stable-ID next actions, and source filename only.
- Added create-without-overwrite behavior and atomic validated program updates.
- Reused the deterministic persona router once and displayed the same routing result with a concise initiation summary.
- Added isolated `unittest` coverage with synthetic text, mocked PDF readers, mocked Gemini responses, and temporary program directories.

Privacy and scope boundaries:

- No SOW PDF, full source path, extracted text, prompt, or raw Gemini response is persisted by the SOW flow.
- No real Gemini call occurs in tests.
- No OCR, database, web UI, dashboard, PowerPoint generation, or multi-agent orchestration is included.

Recommended next step:

- Sprint 54: Project Initiation Artifacts generated from reviewed structured analysis, beginning with an Internal Technical Kickoff and Project Charter.
## RAID Adoption v1 — Issue Adoption — US-57.2

Adopted stored Program issues as framework-neutral `Issue` entities on the existing
`ProgramEntity` foundation. Program Schema `1.3.0` defines canonical Issue status,
optional severity and impact, due date, root cause, resolution summary, and resolved
timestamp. Legacy strings and dictionaries normalize without rewriting storage;
missing identity uses deterministic UUIDv5 and explicit save emits canonical JSON.

CLI issue creation continues to require owner and due date and uses UUIDv4. Closure now
targets the selected canonical `object_id`, requires a resolution summary, and updates
the closed status, UTC resolved timestamp, and audit timestamp. Aggregate identity and
relationship endpoints cover Actions, Risks, and Issues, including resolves,
realized-as, results-from, and adopted-entity relates-to rules.

Workspace Intelligence remains Contract `1.0.0`; Issue title evidence is catalogued at
stable RFC 6901 paths `/issuesById/<UUID>/title`. The read API transports canonical
Issues and the React workspace strictly parses and renders them read-only. Dependency
adoption, CRUD endpoints, relationship inference/UI, and graph traversal remain deferred.

## RAID Adoption v1 — Dependency Adoption — US-57.3

Adopted Dependency as the fourth canonical RAID entity on `ProgramEntity`. Program Schema
`1.4.0` provides UUID identity, controlled status and dependency type, owner/lifecycle/audit
metadata, dependency target, external party, required-by date, impact, and mitigation plan.
Legacy strings and dictionaries normalize non-mutatively with deterministic UUIDv5 identity;
explicit saves are canonical and new CLI Dependencies use UUIDv4.

Aggregate UUID uniqueness now spans Actions, Risks, Issues, and Dependencies. Relationships
validate known endpoints for Dependency `relates_to` adopted entities and Action/Dependency
`blocks` in either direction, without inference, inverse generation, traversal, or UI.
Intelligence Contract `1.0.0` is unchanged; dependency title evidence is stable and RFC 6901
compatible at `/dependenciesById/<UUID>/title`. The read API, executive reporting, and strict
read-only React workspace now present canonical Dependencies.
