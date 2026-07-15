# Program Data Foundation v1

Program Data Foundation v1 introduces a small executable schema foundation for the current TPM Operating System CLI. It does not implement the full future Program Data Model.

## What Was Implemented

- A canonical program schema version: `1.0.0`.
- Canonical defaults for new program records.
- In-memory compatibility normalization for legacy JSON records.
- Minimum validation before saving program records.
- Stable generated IDs for newly created risks, issues, decisions, and next actions.
- UTC ISO-8601 timestamps for program metadata.

## Deliberately Deferred

- Full future domain entities such as customers, stakeholders, milestones, deliverables, readiness, AI assessments, and executive report entities.
- Lowercase enum migration for phase, health, confidence, and item statuses.
- Automatic migration of existing files under `data/programs/`.
- Backfilling IDs into old nested records during load.
- Database persistence, multi-user audit, and hosted SaaS storage behavior.

## Canonical Schema Fields

New v1 program records contain:

```json
{
  "schema_version": "1.0.0",
  "program_id": "...",
  "program_name": "...",
  "description": "...",
  "phase": "Program Initiation",
  "health": "Unknown",
  "confidence": "Medium",
  "risks": [],
  "issues": [],
  "decisions": [],
  "next_actions": [],
  "meeting_history": [],
  "documents": [],
  "artifacts": [],
  "metadata": {
    "created_at": "...",
    "updated_at": "...",
    "source": "cli"
  }
}
```

The display values `Program Initiation`, `Unknown`, and `Medium` are preserved for current CLI compatibility.

## Compatibility Behavior

Legacy records remain loadable even when they are missing:

- `schema_version`
- `meeting_history`
- `documents`
- `artifacts`
- `metadata`
- list fields such as `risks`, `issues`, `decisions`, or `next_actions`

Compatibility defaults are applied to a normalized in-memory copy. Loading a legacy JSON file does not rewrite the source file merely because fields were missing.

Older issues without `owner`, `due_date`, or `issue_id` remain supported by the workspace issue listing and close flows.

## Validation Behavior

Before saving, records are normalized and validated for the minimum v1 shape:

- required identity fields must be non-empty strings;
- `schema_version` must be `1.0.0`;
- phase, health, and confidence must be present strings;
- collection fields must be lists;
- metadata must exist with `created_at`, `updated_at`, and `source`.

Validation returns clear error messages. `save_program()` raises `ValueError` with those messages instead of writing invalid records.

## ID Strategy

New workspace items receive standard-library UUID-based IDs:

- `risk-<uuid>` for risks;
- `issue-<uuid>` for issues;
- `decision-<uuid>` for decisions;
- `action-<uuid>` for next actions.

IDs are generated only for newly created items. Legacy nested records are not backfilled during load.

## Timestamp Behavior

Timestamps are generated in UTC ISO-8601 format.

- New records receive `metadata.created_at` and `metadata.updated_at`.
- Saves preserve `metadata.created_at` when present.
- Saves refresh `metadata.updated_at`.
- If a record being saved has no `created_at`, save assigns one rather than failing only for that missing value.

## Migration Policy

There is no automatic bulk migration in v1.

The application does not scan or rewrite every file under `data/programs/`. Existing files are normalized in memory when loaded and are written as v1 only when a normal save path explicitly saves that individual program.

## Known Limitations

- Validation is intentionally minimal and does not enforce full business rules.
- Existing records may still contain older item shapes.
- Status values remain current display strings such as `Open` and `Closed`.
- Nested items do not yet have metadata.
- Generated reports and session artifacts are not yet linked from the program record.
