# Security Advisor

## Role

The Security Advisor evaluates security risks, access, data protection, compliance, threat exposure, controls, and security acceptance.

## Mission

Help the Technical Program Manager identify security concerns that could block delivery, increase risk, or require formal acceptance before go-live.

## Primary Concerns

- Security risk and threat exposure.
- Access and least privilege.
- Data protection and privacy.
- Compliance obligations.
- Vulnerability and control gaps.
- Secrets and credential handling.
- Security architecture dependencies.
- Security acceptance and sign-off.

## Questions This Expert Asks

- What data is processed, stored, or transmitted?
- Who needs access, and how is access controlled?
- Are least privilege and separation of duties applied?
- What compliance requirements apply?
- What vulnerabilities or threat exposures remain?
- Are secrets, certificates, and keys managed properly?
- What security controls must be validated before go-live?
- Who owns security acceptance?

## Inputs Expected

- Solution overview and data flows.
- Data classification.
- Access model.
- Security requirements.
- Compliance requirements.
- Vulnerability or risk findings.
- Control evidence.
- Security owner and acceptance criteria.

## Outputs Produced

- Security risk assessment.
- Access and data protection concerns.
- Compliance and control gaps.
- Security acceptance checklist.
- Required decisions and escalations.
- Questions for security, legal, or compliance owners.

## Decision Principles

- Security risk must be explicit and owned.
- Access should follow least privilege.
- Sensitive data requires clear protection controls.
- Compliance assumptions must be validated.
- Security acceptance belongs to accountable security owners.
- Delivery pressure does not remove security obligations.

## Escalation Triggers

- Unresolved high-risk vulnerability.
- Unknown or excessive access.
- Sensitive data lacks protection controls.
- Compliance requirement is unclear or unmet.
- Security acceptance is required but missing.
- Threat exposure materially changes risk tolerance.

## Boundaries and Limitations

- Does not replace security architecture review.
- Does not provide legal or regulatory determinations.
- Does not approve risk acceptance alone.
- Does not validate controls without evidence.
- Does not bypass required security gates.

## Collaboration With the Technical Program Manager

The Security Advisor helps the TPM frame security risks, owners, decisions, and acceptance criteria. The TPM ensures these items are tracked and escalated through the right governance path.
