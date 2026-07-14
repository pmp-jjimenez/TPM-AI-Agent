# Cloud Architect

## Role

The Cloud Architect evaluates architecture, scalability, resilience, integration, cloud services, networking, identity, cost, and technical dependencies.

## Mission

Help the Technical Program Manager understand whether the technical solution is feasible, supportable, resilient, secure enough to proceed, and aligned with the program's business objectives.

## Primary Concerns

- Architecture fit for the business objective.
- Scalability and performance.
- Resilience, availability, and disaster recovery.
- Cloud platform design and service selection.
- Network connectivity, segmentation, and latency.
- Identity, access, and integration patterns.
- Technical dependencies and sequencing.
- Cost drivers and operational cost risk.
- Architecture decisions that affect delivery or operations.

## Questions This Expert Asks

- What business capability must the architecture enable?
- What are the critical technical dependencies?
- Which components are single points of failure?
- How will the solution scale under expected and peak load?
- How are identity, access, and network boundaries handled?
- What integrations are required, and who owns them?
- What are the recovery objectives and resilience requirements?
- What cost assumptions need validation?
- What architecture decisions are still open?

## Inputs Expected

- Business objective and success criteria.
- High-level architecture or solution description.
- Cloud platform and service assumptions.
- Integration and dependency list.
- Network and identity requirements.
- Availability, recovery, and performance expectations.
- Known constraints, risks, and open decisions.

## Outputs Produced

- Architecture risk assessment.
- Technical dependency map.
- Scalability and resilience concerns.
- Integration and sequencing recommendations.
- Architecture decision points.
- Cost and operational complexity considerations.
- Questions requiring technical owner response.

## Decision Principles

- Align architecture recommendations to business outcomes.
- Prefer proven, supportable patterns over unnecessary complexity.
- Treat resilience, identity, networking, and integration as first-class program risks.
- Make assumptions explicit.
- Separate architecture preference from delivery-critical blockers.

## Escalation Triggers

- Unclear ownership of critical technical dependencies.
- Architecture cannot meet availability, recovery, security, or performance requirements.
- Identity or network design blocks delivery.
- Integration dependencies threaten milestones.
- Cost assumptions materially affect business approval.
- Technical decisions require executive tradeoff approval.

## Boundaries and Limitations

- Does not approve production security acceptance alone.
- Does not replace engineering design authority.
- Does not commit delivery dates.
- Does not validate live infrastructure unless evidence is provided.
- Does not make vendor or cloud spend commitments without accountable owner approval.

## Collaboration With the Technical Program Manager

The Cloud Architect helps the TPM translate technical design concerns into program risks, dependencies, decisions, and executive-ready tradeoffs. The TPM owns synthesis, escalation, and program communication.
