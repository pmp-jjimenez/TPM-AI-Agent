# TPM Operating System Backlog

This backlog distinguishes completed work, in-progress documentation work, planned implementation work, and future product vision. Priorities are relative and do not imply committed dates.

| Epic ID | Epic Name | Objective | Tickets or Capabilities | Current Status | Priority |
|---|---|---|---|---|---|
| Epic 40 | Program Workspace Issue Management | Improve active program execution by tracking issues with ownership and closure. | Add issues to workspace; capture owner; capture due date; validate due date format; list open issues; close issues; improve return-to-workspace feedback. | Completed | High |
| Epic 41 | Engineering Documentation Foundation | Establish core engineering and product documentation for maintainability and planning. | Product vision; roadmap; backlog; architecture; release history. | Completed | High |
| Epic 42 | AI Expert Council Foundation | Document specialized expert personas and define how a future council should support TPM judgment. | Create cloud architect, incident commander, executive advisor, delivery manager, operations manager, change manager, security advisor, and customer success advisor personas; document council purpose, invocation, conflict handling, and current implementation boundary. | Completed | High |
| Sprint 51 | Persona Routing Foundation v1 | Make persona selection deterministic and testable before adding AI orchestration. | Canonical persona identifiers; pure routing module; primary and supporting persona result structure; rule-based routing for initiation, cloud, incident, executive, readiness, security, change, customer success, and delivery-pressure signals; unittest coverage. | Completed | High |
| Sprint 52 | CLI Persona Routing Integration v1 | Integrate deterministic persona routing into the CLI and New Program prompt path without multi-agent orchestration. | Calculate routing once per top-level CLI operation; display concise routing summary; pass routing into prompt construction; add safe TPM fallback; preserve placeholders and backward compatibility. | Completed | High |
| TBD | Program Data Foundation | Make local program persistence safer, clearer, and easier to evolve. | Program schema; validation; migrations; malformed JSON handling; field defaults; generated artifact references; data integrity checks. | Planned | High |
| TBD | Executive Intelligence | Improve executive-facing analysis and decision support. | Business impact summaries; decisions required; confidence rationale; trend awareness; executive-ready recommendations; status report improvements. | Planned | High |
| TBD | Automated Testing | Create confidence that CLI flows, data persistence, and generated artifacts do not regress. | Unit tests for memory, workspace, router behavior, prompt building, executive report generation, and edge cases; scenario-based regression tests. | Planned | High |
| TBD | Web Interface | Provide a browser-based program workspace. | Program dashboard; RAID views; issue management; decisions; actions; reports; artifact access; responsive UI. | Planned | Medium |
| TBD | SOW Analysis | Turn SOW inputs into a structured program foundation. | SOW upload or paste workflow; scope extraction; deliverables map; milestone summary; dependencies; risks; clarification questions; initiation package output. | Planned | High |
| TBD | Major Incident Mode | Support structured incident coordination and communications. | Incident intake; severity assessment; impact summary; action tracker; owner tracking; executive updates; ETA discipline; RCA support. | Planned | High |
| TBD | Operational Readiness | Help TPMs validate supportability before go-live or transition. | ORR checklist; support readiness; monitoring readiness; KT tracking; runbook verification; service acceptance; hypercare and handoff. | Planned | High |
| TBD | Professional Artifacts | Generate polished stakeholder-facing artifacts. | Professional PowerPoint decks; refined Markdown/PDF outputs; executive status packages; steering committee materials; readiness packages. | Future | Medium |
| TBD | Docker and Deployment | Make the app easier to run consistently and prepare for deployable environments. | Dockerfile; local container run instructions; environment configuration; runtime packaging; deployment documentation. | Planned | Medium |
| TBD | Dependency Management with `uv` | Introduce reproducible dependency management when project dependencies require it. | `pyproject.toml`; lockfile strategy; documented setup; development command standardization. | Planned | Medium |
| TBD | Persona Routing Expansion | Extend persona routing beyond top-level CLI integration while preserving deterministic, transparent behavior. | Improve routing rules; broaden prompt integration where real workflows exist; add richer operation context; keep routing transient unless a formal execution-record model is introduced. | Planned | Medium |
| TBD | AI Expert Council Orchestration | Explore whether specialized expert perspectives should become a formal orchestration layer. | Council review prompt builder; conflict summary; TPM synthesis output; guardrails against fake agent execution; tests for routing behavior and AI response shape. | Future | Medium |

## Notes

- Epic 40 is marked completed based on Git history and current workspace behavior.
- Epic 41 and Epic 42 are documentation foundation epics completed by this controlled change set.
- Sprint 51 implements routing only. It does not invoke personas, run multiple AI calls, or change CLI behavior.
- Sprint 52 adds executable persona routing integration but does not complete the Major Incident, Executive Review, or Operational Readiness placeholder workflows.
- Sprint 52 does not implement a Stakeholder Council or governance persona layer for sponsors, CIOs, CTOs, VPs, steering committees, finance, legal, or PMO leadership.
- Several capabilities already exist as Markdown playbooks or templates but are not yet implemented as executable product flows.
