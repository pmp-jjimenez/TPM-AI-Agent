# AI Expert Council

## Purpose

The AI Expert Council is a planned product capability that would allow the TPM Operating System to evaluate program decisions through multiple specialized expert perspectives. The council is intended to improve the quality of TPM reasoning by surfacing risks, tradeoffs, missing evidence, and decision criteria that one general TPM perspective may miss.

The council supports decisions. It does not replace the Technical Program Manager, accountable executives, engineering owners, operations owners, security owners, or customer decision makers.

## Personas vs Autonomous Agents

Personas are documented expert perspectives. They describe how a specialist should reason, what questions they should ask, what inputs they need, and what outputs they should produce.

Autonomous agents would be executable system behavior that independently routes work, invokes tools, changes state, or performs actions.

Current status: the repository now documents expert personas, but council routing is not implemented in code. The current application does not automatically invoke these experts, synthesize council output, or update program state based on persona recommendations.

## TPM Accountability

The Technical Program Manager remains accountable for synthesizing council output into a clear recommendation, but does not automatically become the final decision owner. Final decision authority belongs to the designated business, executive, technical, security, customer, or operational owner for the decision. The TPM should:

- Decide which expert perspectives are relevant.
- Validate the evidence behind recommendations.
- Reconcile conflicting advice.
- Decide what to escalate.
- Communicate the final recommendation.
- Ensure decisions are captured with clear ownership.

## Expert Invocation Guide

| Expert | Invoke When |
|---|---|
| Cloud Architect | Architecture, scalability, resilience, cloud design, networking, identity, integration, cost, or technical dependency concerns exist. |
| Incident Commander | A service disruption, severity assessment, containment plan, recovery plan, ETA communication, or RCA is needed. |
| Executive Advisor | Business impact, executive escalation, strategic alignment, decision framing, or concise senior stakeholder communication is needed. |
| Delivery Manager | Scope, milestones, resources, RAID, dependencies, commitments, or governance discipline need review. |
| Operations Manager | Operational readiness, monitoring, support model, runbooks, KT, hypercare, service acceptance, or handoff is in question. |
| Change Manager | Adoption, stakeholder impact, communications, training, deployment readiness, CAB controls, rollback, or ADKAR concerns exist. |
| Security Advisor | Access, data protection, compliance, threat exposure, security controls, or security acceptance must be evaluated. |
| Customer Success Advisor | Customer goals, expectations, adoption, satisfaction, value realization, relationships, or renewal risk need attention. |

## Example Council Review: Go-Live Readiness Decision

Scenario: A program is approaching go-live. The TPM must recommend Go, Go with Risks, or No-Go.

Relevant expert perspectives:

- Cloud Architect reviews resilience, integration dependencies, capacity, identity, networking, and rollback feasibility.
- Operations Manager reviews monitoring, alerting, runbooks, support ownership, KT completion, and hypercare readiness.
- Security Advisor reviews access controls, vulnerabilities, data protection, compliance, and security acceptance.
- Change Manager reviews stakeholder communications, training, deployment readiness, CAB approval, and rollback communication.
- Delivery Manager reviews milestone commitments, open RAID items, resource readiness, and governance status.
- Executive Advisor reviews business impact, decision required, confidence, escalation needs, and concise recommendation.
- Customer Success Advisor reviews customer expectations, adoption impact, stakeholder confidence, and value realization risk.

Possible TPM synthesis:

- Recommendation: Go with Risks.
- Rationale: Core technical deployment is ready, but operations acceptance and customer training have partial gaps.
- Conditions: Operations sign-off, final runbook review, customer communication approval, rollback owner confirmation.
- Escalation: Executive sponsor decision required if operations acceptance is not complete by the readiness checkpoint.

## Handling Conflicting Recommendations

Conflicting recommendations should be handled through evidence, decision ownership, and risk tolerance:

- Identify the disagreement precisely.
- Separate facts, assumptions, and opinions.
- Ask which recommendation is supported by stronger evidence.
- Identify irreversible risks and customer impact.
- Clarify who owns the final decision.
- Document tradeoffs and residual risk.
- Escalate when conflict affects business commitments, customer impact, security acceptance, operational readiness, or executive risk tolerance.

The TPM should not average recommendations into a weak compromise. The TPM should synthesize a clear recommendation with rationale, confidence, conditions, decision owner, and escalation path. The council supports judgment, but does not assign authority that the TPM does not have.

## Current Status

Implemented:

- Expert persona documents are available under `personas/`.
- This council operating model is documented.

Not implemented:

- Automated expert routing.
- Council prompt construction.
- Multi-persona AI execution.
- Conflict detection.
- TPM synthesis generation.
- Program state updates from council recommendations.
- Tests for expert routing.

## Future Implementation Concept

A future implementation could add:

- Routing rules that map user intent, program phase, and risk type to relevant expert personas.
- A council review prompt builder that loads only relevant persona files and program context.
- Structured outputs from each expert.
- A TPM synthesis step that summarizes conflicts, evidence, decisions required, and recommended action.
- Explicit confidence scoring tied to available evidence.
- Tests proving that council routing does not invoke irrelevant experts or claim unsupported capabilities.
