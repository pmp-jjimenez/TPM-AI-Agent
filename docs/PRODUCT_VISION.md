# TPM Operating System Product Vision

## Product Name

TPM Operating System

## Problem Statement

Technical Program Managers lead complex technology programs that require structured judgment across scope, risks, issues, decisions, stakeholders, executive communication, operational readiness, and incidents. Much of this work is still managed through scattered notes, manual status artifacts, and inconsistent program memory.

The TPM Operating System addresses this by giving TPMs a structured assistant that can load reusable TPM knowledge, maintain program state, support workspace actions, and generate decision-oriented outputs.

## Target User

The primary user is a Technical Program Manager responsible for planning, executing, monitoring, and communicating complex technology programs across engineering, cloud, infrastructure, SaaS, cybersecurity, operations, customer delivery, and enterprise transformation contexts.

Secondary users may include delivery leaders, program sponsors, operations leaders, and customer-facing teams who consume TPM-generated artifacts.

## Product Objective

The objective is to help TPMs make better decisions and produce clearer operating artifacts by combining:

- A structured TPM knowledge base.
- Program state persistence.
- Workspace actions for program execution.
- AI-assisted analysis and communication.
- Professional templates and playbooks.

## Current Value Proposition

The current implementation provides a CLI-based TPM assistant that can:

- Start a new program from a user-provided description.
- Load core TPM context from Markdown instructions, knowledge assets, playbooks, and templates.
- Build an AI-ready prompt for an initial TPM assessment.
- Call the Gemini API when `GEMINI_API_KEY` is configured.
- Save the last generated prompt and AI response under `sessions/`.
- Persist program records as JSON under `data/programs/`.
- Open an active program workspace.
- Track risks, issues, decisions, next actions, health, confidence, and phase.
- Add issue owner and due date data.
- List open issues.
- Close open issues.
- Generate a Markdown Executive Status Report under `reports/executive/`.

## Differentiators

- TPM-specific operating model rather than a generic chatbot.
- Reusable Markdown knowledge base covering capability routing, confidence, program state, SOW analysis, incident command, operational readiness, stakeholder communication, and TPM frameworks.
- Program memory that allows workspace actions to accumulate program state across sessions.
- Explicit confidence discipline based on evidence and missing information.
- Executive communication patterns that emphasize business impact, decisions, risks, and next actions.
- CLI-first implementation that keeps the current system simple and inspectable.

## Current Implemented Capabilities

Implemented capabilities are limited to what is currently supported by repository code and assets:

- CLI menu in `app/main.py`.
- Routing for new programs, active program selection, placeholder menu entries, and exit behavior in `app/router.py`.
- New program prompt generation in `app/engine.py` and `app/prompt_builder.py`.
- Core context loading from selected Markdown assets in `app/context_loader.py`.
- Gemini API request handling in `app/llm.py`.
- JSON program creation, loading, saving, and listing in `app/memory.py`.
- Active Program Workspace actions in `app/workspace.py`.
- Markdown Executive Status Report generation in `app/executive.py`.
- Markdown personas, playbooks, knowledge assets, templates, examples, and tests as repository assets.

## Planned Capabilities

The following are planned or documented concepts, not fully implemented capabilities:

- Program Workspace expansion for richer RAID, dependencies, milestones, meeting history, and document tracking.
- Program Data Foundation with stronger schemas, validation, migrations, and safer persistence.
- Executive Intelligence with stronger business impact summaries, decision framing, and trend awareness.
- Automated Testing for core routing, memory, workspace, report generation, and prompt construction.
- Web Interface for a browser-based program workspace.
- SOW Upload and Analysis using existing SOW analysis knowledge and templates.
- Major Incident Mode beyond the current CLI placeholder.
- Operational Readiness workflows beyond the current CLI placeholder.
- Professional PowerPoint generation.
- Docker-based local runtime and deployment packaging.
- Dependency management with `uv`.
- AI Expert Council routing across specialized personas.

## Long-Term SaaS Possibility

The long-term product direction could become a multi-user SaaS operating layer for TPM work. That possibility would require capabilities not present today, including authentication, authorization, organization-level tenancy, durable storage beyond local JSON files, audit logs, collaboration workflows, background jobs, integration APIs, secure document upload, admin controls, and production operations.

This is a product vision option, not a current implementation claim.

## Product Principles

- Support TPM judgment rather than replace it.
- Keep accountability with the human TPM and program leadership.
- Prefer evidence-based recommendations over unsupported certainty.
- Make missing information visible.
- Separate implemented features from planned capabilities.
- Produce concise, decision-ready communication.
- Preserve program context across work sessions.
- Use practical operating artifacts that a TPM can act on.
- Avoid inventing commitments, dates, owners, or technical capabilities.

## Accountability Statement

The TPM Operating System supports TPM judgment. It does not replace TPM accountability, executive decision ownership, engineering ownership, security ownership, operational ownership, customer commitments, or designated business authority. The TPM remains accountable for synthesis, recommendation quality, escalation, communication, and decision documentation. Final decision authority belongs to the designated business, executive, technical, security, customer, or operational owner for the decision.
