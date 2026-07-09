# Status Health Model

## Purpose

Define how the TPM AI Agent evaluates program health using configurable business rules.

The agent should not assume universal thresholds. Each organization should define its own health criteria based on baseline, tolerance, and business priorities.

---

# Health Dimensions

Program health should consider:

## Schedule

Evaluate:

- Baseline milestone dates.
- Current forecast.
- Variance.
- Recovery plan.

---

## Scope

Evaluate:

- Approved scope.
- Scope changes.
- Delivery impact.

---

## Budget

Evaluate:

- Planned budget.
- Actual spend.
- Forecast variance.

---

## Risk

Evaluate:

- Critical risks.
- Risk exposure.
- Mitigation progress.

---

## Dependencies

Evaluate:

- External blockers.
- Dependency confidence.
- Ownership.

---

# Status Classification

Organizations should configure thresholds.

Example:

## Green

Characteristics:

- Within approved baseline.
- Risks controlled.
- No critical blockers.

---

## Yellow

Characteristics:

- Variance exists.
- Recovery plan required.
- Management attention needed.

---

## Red

Characteristics:

- Objectives threatened.
- Executive intervention required.
- Recovery plan uncertain.

---

# Trend Analysis

Status should include trend.

## Improving ↘

Situation is recovering.

Example:

- Risk decreasing.
- Schedule recovery progressing.

---

## Stable →

No significant change.

---

## Deteriorating ↗

Situation is worsening.

Example:

- Increasing delays.
- New critical risks.

---

# Confidence Level

The TPM AI Agent should indicate confidence:

## High

Based on validated data.

## Medium

Some assumptions remain.

## Low

Information incomplete or changing.

---

# Executive Health Format

Example:

Status: Yellow

Trend: Deteriorating

Confidence: Medium

Reason:
Schedule variance increased due to external dependency delay.

Recommended Action:
Review recovery options with program leadership.

---

# Configuration Principle

Health thresholds must be configurable per organization.

The TPM AI Agent should ask:

- What is the approved baseline?
- What variance is acceptable?
- Who defines escalation thresholds?
- What business impact changes severity?