# Program Data Model Architecture Review

## 1. Executive Assessment

The proposed Program Data Model is directionally strong and matches the TPM Operating System vision: it separates operating state from generated AI analysis, emphasizes evidence and ownership, and creates a vocabulary that can support a future web workspace, reporting layer, readiness workflow, and database-backed product.

Current implementation is much simpler. Program records are local JSON files under `data/programs/` with top-level identity, phase, health, confidence, risks, issues, decisions, next actions, and a small amount of workspace history. There is no schema version, validator, migration layer, nested entity ID strategy, or canonical artifact linkage.

Recommended v1 foundation should not implement the full proposed model at once. The next implementation should introduce a minimum canonical schema around the current CLI behaviors, add compatibility loading for legacy JSON, and validate records without silently rewriting user data.

Recommendation: **Go with Conditions**. Proceed only if implementation starts with a small versioned schema, compatibility tests, and explicit migration behavior.

## 2. Strengths of the Proposed Domain Model

### Current Implementation

- Simple local JSON is easy to inspect and appropriate for the current CLI MVP.
- The implemented workspace already has the core operating categories: risks, issues, decisions, next actions, health, confidence, and phase.
- Issue owner and due date support are useful early signals for the future ownership model.

### Recommended v1 Foundation

- Adding `schema_version` creates the minimum structure needed for validation and migration.
- Stable IDs for nested items make update, close, report, and future audit operations safer.
- Separating AI assessments from accepted program state protects TPM accountability.
- Metadata for created and updated timestamps supports later reporting and debugging.

### Future Model Evolution

- Customers, stakeholders, milestones, deliverables, meetings, artifacts, readiness assessments, and executive reports provide a coherent future SaaS vocabulary.
- The aggregate-first JSON model can later map to relational tables or document collections without changing business language.
- Evidence artifact references create a foundation for higher-confidence executive reporting.

## 3. Missing or Ambiguous Concepts

### Current Implementation

- There is no formal distinction between user-entered state and generated artifacts beyond separate files.
- Program ownership is implicit. The current record does not identify the accountable TPM, sponsor, customer owner, or decision authority.
- Risks, decisions, and actions are free-form lists with limited metadata.

### Recommended v1 Foundation

- Define whether `program_id` is a stable business identifier, a filename slug, or both.
- Define whether top-level `issues` remains supported for compatibility or whether v1 writes only `raid.issues`.
- Define minimum required fields for each mutable item before the CLI can save it.
- Define how unknown values are represented: `null`, `"unknown"`, empty string, or omitted field.
- Define date format requirements for all due, forecast, target, created, and updated dates.

### Future Model Evolution

- Budget, benefits realization, scope baseline, change control, communications plan, and escalation history are not explicitly modeled.
- Cross-program dependencies and portfolio-level entities are future needs but should remain out of v1.
- Approval workflows, signoffs, and role-based authority need clearer boundaries before multi-user use.

## 4. Areas That May Be Over-Engineered for the Current MVP

The full proposed model is too large for immediate implementation in the current CLI. The highest-risk overreach areas are:

- Full customer and stakeholder graphs before the CLI has workflows that use them.
- Meeting history with linked decisions, actions, RAID items, and artifacts before meeting capture exists.
- Operational readiness as a fully nested entity before the operational readiness menu is implemented.
- AI assessment records before generated prompts and responses are linked as artifacts.
- Rich artifact checksum and provenance before there is document ingestion or artifact management.
- Database-ready audit concepts such as tenant IDs and correlation IDs before hosted collaboration exists.

The model should remain the canonical target, but the first executable version should validate and persist only what the current product can responsibly maintain.

## 5. Data Consistency Risks

### Current Implementation

- Records can drift because there is no schema validation.
- Missing fields can break code that indexes directly into dictionaries.
- Nested records do not have IDs, making updates dependent on list position.
- Issue status uses `"Open"` and `"Closed"` while the proposed model uses lowercase controlled values.
- Existing records may contain older issue shapes without `owner` or `due_date`.

### Recommended v1 Foundation

- Add compatibility defaults for missing `risks`, `issues`, `decisions`, `next_actions`, `phase`, `health`, and `confidence`.
- Treat legacy records without `schema_version` as readable and mutable only through compatibility logic.
- Normalize controlled values at the application boundary, not by silently rewriting source files.
- Add tests for malformed, partial, and legacy records before introducing migration.

### Future Model Evolution

- When artifacts and reports become linked entities, stale file paths and missing files will become consistency risks.
- Database migration will require optimistic concurrency or other write-conflict handling.
- Multi-user use will require audit logs and authorization checks before writes.

## 6. Entity Ownership and Decision-Authority Concerns

The model correctly identifies ownership as a first-class concern, but ownership semantics need tightening.

### Current Implementation

- Issues have an owner in the current CLI.
- Risks, decisions, and next actions do not consistently require owners.
- Decision authority is not represented.

### Recommended v1 Foundation

- Require owner fields only where current workflows can capture them reliably.
- Distinguish accountable owner from informed stakeholder.
- For decisions, separate the TPM recommendation from the authorized decision maker.
- Preserve unassigned values explicitly instead of inventing owners.

### Future Model Evolution

- Stakeholder records should become the authority source for sponsor, business owner, technical owner, security approver, operational owner, and customer approver.
- Decision records should support `needed_by_date`, `decision_owner_stakeholder_id`, rationale, reversibility, and related issue or risk IDs.
- Approval history should not be added until there is a clear workflow for capturing it.

## 7. Lifecycle Consistency Review

The proposed lifecycle values are useful, but the current implementation uses display-oriented values such as `"Program Initiation"` and `"Unknown"`.

### Current Implementation

- Phase is a free-form display string.
- Health is mutable through the CLI as Green, Yellow, or Red.
- Confidence defaults to Medium and is not tied to evidence.

### Recommended v1 Foundation

- Support a small normalized internal vocabulary while preserving display labels.
- Define legacy mappings such as `Program Initiation` to `initiation`, `Unknown` to `unknown`, and `Medium` to `medium`.
- Track `last_update` or `metadata.updated_at` consistently on mutating workspace actions.
- Do not introduce closed-program lifecycle semantics until there is an implemented close workflow.

### Future Model Evolution

- Add lifecycle-specific validation only when workflows exist for phase transitions.
- Operational readiness, hypercare, transition, and closure gates should have explicit criteria before they become enforced states.

## 8. Recommended Minimum Viable Canonical Schema

Recommended v1 should be intentionally small:

```json
{
  "schema_version": "1.0.0",
  "program_id": "filename-safe-id",
  "program_name": "Program Name",
  "description": "Program description",
  "phase": "initiation",
  "health": "unknown",
  "confidence": "medium",
  "risks": [],
  "issues": [],
  "decisions": [],
  "next_actions": [],
  "artifacts": [],
  "metadata": {
    "created_at": null,
    "updated_at": null,
    "source": "cli"
  }
}
```

Minimum nested issue shape:

```json
{
  "issue_id": "issue-001",
  "description": "Issue description",
  "owner": null,
  "due_date": null,
  "status": "open",
  "metadata": {
    "created_at": null,
    "updated_at": null,
    "source": "cli"
  }
}
```

This preserves current behavior while creating room for IDs, metadata, validation, and artifact linkage.

## 9. Recommended Implementation Sequence

1. Add tests for current memory, workspace issue helpers, prompt builder, and executive report behavior.
2. Add a schema constants module or lightweight standard-library validator.
3. Add a compatibility loader that fills missing defaults for legacy records in memory.
4. Add stable nested IDs for newly created issues, risks, decisions, and actions.
5. Add validation that reports errors without rewriting existing JSON.
6. Add an explicit migration command or script that writes migrated copies only when invoked.
7. Switch write paths to v1 canonical schema after compatibility tests pass.
8. Add artifact references for generated prompts and executive reports.
9. Expand the model only when corresponding workspace workflows exist.

## 10. Migration Risks From Current JSON Records

- Existing records lack `schema_version` and should be treated as legacy.
- Existing issue records may not include `owner` or `due_date`.
- Existing statuses use capitalized values, which may not match future enums.
- Free-form phase and confidence values may not map cleanly.
- List-position updates could be lost if nested IDs are generated inconsistently.
- Report and session files are not currently linked from program JSON.
- Silent migration could damage user-maintained local records.

Mitigation should include read-only validation first, backups or migrated copies second, and write-path changes only after tests cover legacy examples.

## 11. Decisions That Should Be Captured as Architecture Decision Records

- ADR: Local JSON aggregate remains the persistence model for v1.
- ADR: Schema versioning strategy and legacy record handling.
- ADR: Controlled vocabulary casing and display-label mapping.
- ADR: Stable ID generation for nested entities.
- ADR: Separation of AI-generated assessments from accepted program state.
- ADR: Artifact storage and linking strategy for prompts, responses, and reports.
- ADR: Migration policy for existing records under `data/programs/`.
- ADR: Validation failure behavior for malformed records.
- ADR: Boundary between MVP canonical schema and future full domain model.

## 12. Open Questions Requiring Product Owner or TPM Input

- What is the minimum required information to create a program record?
- Should issue owners be free-text in v1 or references to stakeholder records?
- Should open risks, open issues, pending decisions, and open actions have required owners?
- What phase vocabulary should appear to users in the CLI?
- Should health be human-entered only, AI-suggested only, or both with approval?
- What evidence is required before confidence can be high?
- Should executive reports be generated from live state only or from immutable snapshots?
- Is migration expected to modify existing program JSON in place?
- Which fields are required for executive reporting in the next release?
- Who has decision authority for program go, no-go, readiness, and closure recommendations?

## 13. Go / Go With Conditions / No-Go Recommendation

**Recommendation: Go with Conditions.**

Conditions:

- Do not implement the full proposed model in one step.
- Start with a minimum versioned schema that preserves current CLI behavior.
- Keep legacy records readable.
- Add validation before migration.
- Make migration explicit and reversible.
- Keep AI assessments separate from accepted state.
- Capture unresolved schema decisions in ADRs before enforcing them in code.

The proposed model is a strong target architecture, but the implementation should advance as an engineering foundation, not as a broad domain rewrite.
