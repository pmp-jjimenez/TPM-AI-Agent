# TPM Operating System Backlog

This backlog distinguishes completed work, in-progress documentation work, planned implementation work, and future product vision. Priorities are relative and do not imply committed dates.

| Epic ID | Epic Name | Objective | Tickets or Capabilities | Current Status | Priority |
|---|---|---|---|---|---|
| Epic 40 | Program Workspace Issue Management | Improve active program execution by tracking issues with ownership and closure. | Add issues to workspace; capture owner; capture due date; validate due date format; list open issues; close issues; improve return-to-workspace feedback. | Completed | High |
| Epic 41 | Engineering Documentation Foundation | Establish core engineering and product documentation for maintainability and planning. | Product vision; roadmap; backlog; architecture; release history. | Completed | High |
| Epic 42 | AI Expert Council Foundation | Document specialized expert personas and define how a future council should support TPM judgment. | Create cloud architect, incident commander, executive advisor, delivery manager, operations manager, change manager, security advisor, and customer success advisor personas; document council purpose, invocation, conflict handling, and current implementation boundary. | Completed | High |
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
| TBD | AI Expert Council Routing | Implement code-level routing for specialized expert personas. | Persona selection rules; council review prompt builder; conflict summary; TPM synthesis output; tests for routing behavior. | Future | Medium |

## Notes

- Epic 40 is marked completed based on Git history and current workspace behavior.
- Epic 41 and Epic 42 are documentation foundation epics completed by this controlled change set.
- Several capabilities already exist as Markdown playbooks or templates but are not yet implemented as executable product flows.
