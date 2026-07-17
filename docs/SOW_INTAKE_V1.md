# SOW Intake Foundation v1

## User Workflow

1. Run `python3 app/main.py` from the repository root.
2. Select `Start a New Program`.
3. Select `Create from SOW PDF`.
4. Paste the path to a user-provided local PDF.
5. The application extracts bounded selectable text, makes one Gemini call, validates the JSON response, creates the canonical program, displays persona routing, and shows an initiation summary.
6. Return to the main menu and use `Manage an Active Program` to open the created workspace.

This flow is intended to fit comfortably within a three-minute demonstration.

## Architecture Boundaries

- `app/pdf_extractor.py`: local path validation and bounded selectable-text extraction.
- `app/prompt_builder.py`: dedicated strict-JSON SOW analysis prompt.
- `app/sow_analysis.py`: response parsing, normalization, and non-mutating canonical mapping.
- `app/sow_intake.py`: one-pass orchestration and concise summary presentation.
- `app/llm.py`: the existing Gemini call boundary.
- `app/persona_routing.py`: the existing deterministic persona router and presentation layer.
- `app/memory.py` and `app/schema.py`: validated, non-overwriting canonical persistence.

Extraction, analysis, mapping, persistence, routing, and presentation remain separate. There is one Gemini call and no multi-agent orchestration.

## Structured Analysis

The transient analysis uses these machine-readable fields:

- `document_title`, `customer_name`, `program_name`, `business_objective`, `executive_summary`, `program_type`
- `products_or_services`, `in_scope`, `out_of_scope`, `deliverables`, `assumptions`, `dependencies`, `integrations`
- `environments_or_platforms`, `locations_or_countries`, `licensing_or_capacity`, `key_stakeholders`
- `customer_responsibilities`, `supplier_responsibilities`, `acceptance_criteria`, `milestones`, `risks`
- `open_questions`, `missing_critical_information`
- `recommended_primary_persona`, `recommended_supporting_personas`, `recommended_next_action`, `confidence`
- `source_filename`, `analysis_version`

Unavailable fields normalize to empty strings or lists. This full analysis remains in memory and is not indiscriminately persisted.

## Canonical Program Mapping

- Program name maps from `program_name`, falling back to `document_title`.
- Customer maps to the backward-compatible canonical `customer` field.
- Description maps from `business_objective`, falling back to `executive_summary`.
- Phase remains the canonical `Program Initiation`; health remains the safe `Unknown` default.
- Confidence accepts High, Medium, or Low and otherwise uses Medium.
- Supported risks become open risk records with generated stable IDs and `SOW analysis` source labels.
- The recommended action, missing critical information, and open questions become open next actions with generated stable IDs.
- The documents collection records only the source filename and explicitly indicates that the original file was not persisted.

Detailed scope, responsibilities, milestones, integrations, licensing, stakeholders, and acceptance information remain transient for future initiation-artifact work rather than expanding the v1 program schema.

## Privacy and Confidentiality

- The source PDF is read in place and is never copied into the repository or program workspace.
- Only the source filename is saved; the full path is not saved or printed in summaries.
- Extracted text and the raw Gemini response remain in memory and are not written to session files.
- Extracted text is capped at 120,000 characters before prompt construction; the UI reports truncation without printing document content.
- Tests use synthetic fixtures and mocks. They do not use a real SOW, network access, or the real Gemini API.
- Users remain responsible for ensuring that their configured Gemini service and data-handling terms are appropriate for confidential material.

## Known Limitations

- No OCR. Empty and image-only documents are rejected with guidance.
- Password-protected PDFs are not supported.
- Complex tables and reading order depend on the PDF text layer and `pypdf` extraction.
- One bounded text segment is analyzed; very large documents may be truncated.
- The model response must be usable JSON. There is no repair call or retry call.
- Detailed SOW analysis is not persisted as a standalone artifact in v1.

## Manual Demo

Install dependencies, configure `GEMINI_API_KEY`, start the CLI, and select a local user-provided PDF as described above. Do not place the demonstration PDF inside the repository. Confirm the initiation summary, then open the new program through `Manage an Active Program`.

## Recommended Sprint 54

Project Initiation Artifacts: generate a Project Charter, Internal Technical Kickoff brief, Customer Kickoff brief, Stakeholder Register, and initial RAID content from the validated transient analysis, with an explicit review step before persistence or export.
