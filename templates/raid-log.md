# RAID Log Template

## Purpose

Provide structured visibility into program risks, assumptions, issues, and dependencies.

---

# Risks

| ID | Description | Impact | Probability | Risk Score | Risk Owner | Mitigation Plan | Action Owner | Due Date | Status |

---

# Assumptions

| ID | Assumption | Validation Needed | Owner | Status |
|---|---|---|---|---|

---

# Issues

| ID | Issue | Business Impact | Action Plan | Owner | Due Date | Status |
|---|---|---|---|---|---|---|

---

# Dependencies

| ID | Dependency | Required Date | Dependency Owner | Impact | Status |
|---|---|---|---|---|---|

---

# TPM Review Questions

The TPM AI Agent should ask:

- Which risks are increasing?
- Which dependencies threaten milestones?
- Which issues require escalation?
- Which assumptions need validation?
- Who owns the next action?

---

# Risk Scoring Model

The TPM AI Agent should evaluate risks using:

## Probability

Likelihood that the risk will occur.

Scale:

1 - Low probability  
2 - Medium probability  
3 - High probability

---

# RAID Ownership Model

Every RAID item must have a clearly identified owner.

---

## Risk Owner

Responsible for:

- Monitoring the risk.
- Ensuring mitigation strategy exists.
- Reporting risk status.
- Escalating when necessary.

The Risk Owner does not necessarily execute all mitigation activities.

---

## Action Owner

Responsible for:

- Completing specific mitigation actions.
- Providing progress updates.
- Meeting committed dates.

---

# Ownership Rule

A RAID item without an owner is considered unmanaged.

The TPM AI Agent should identify:

- Missing owners.
- Overdue actions.
- Risks without mitigation plans.
- Dependencies without accountable teams.

---

## Impact

Potential consequence if the risk occurs.

Evaluate:

- Business impact.
- Customer impact.
- Schedule impact.
- Financial impact.
- Operational impact.

Scale:

1 - Low impact  
2 - Medium impact  
3 - High impact

---

## Risk Score

Formula:

Probability × Impact = Risk Score

Example:

Probability: 3  
Impact: 3  

Risk Score: 9 (Critical)

---

# Risk Priority

## Critical

Characteristics:

- High business impact.
- Requires immediate attention.
- Executive visibility may be required.

Action:

Escalate and define mitigation plan.

---

## High

Characteristics:

- Could affect program objectives.
- Requires active monitoring.

Action:

Assign owner and mitigation timeline.

---

## Medium

Characteristics:

- Manageable within team.

Action:

Track during regular reviews.

---

## Low

Characteristics:

- Limited impact.

Action:

Monitor.

---

# RAID Review Questions

During program reviews, the TPM AI Agent should ask:

- Which risks increased since the last review?
- Which risks threaten critical milestones?
- Which dependencies have no owner?
- Which issues require executive decisions?
- Are mitigation actions progressing?

---

# Executive RAID Summary

For leadership communication, summarize:

## Top Risks

The three highest priority risks.

## Critical Issues

Current problems affecting delivery.

## Key Dependencies

External factors requiring attention.

## Decisions Required

Leadership actions needed.