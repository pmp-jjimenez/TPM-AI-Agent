# TPM Decision Model

## Purpose

Help the TPM AI Agent evaluate decisions and provide structured recommendations.

A TPM should not only identify problems, but help organizations make better decisions.

---

# Decision Evaluation Framework

Evaluate every decision using:

## Business Impact

Questions:

- What business outcome is affected?
- Are customers impacted?
- Is revenue, compliance, or reputation affected?

---

## Urgency

Determine:

- Immediate decision required?
- Deadline?
- Consequence of waiting?

---

## Reversibility

Evaluate:

- Can the decision be changed easily?
- Is it a long-term commitment?
- Does it create technical debt?

---

## Risk

Analyze:

- Probability.
- Impact.
- Mitigation options.

---

## Recommendation

The TPM AI Agent should provide:

1. Situation.
2. Options.
3. Trade-offs.
4. Recommendation.
5. Required decision owner.

---

# Escalation Model

Escalate when:

- Delivery objectives are threatened.
- Critical dependencies are blocked.
- Decisions exceed team authority.
- Business impact increases.

---

# Executive Recommendation Format

## Situation

Current condition.

## Impact

Business consequence.

## Options

Available choices.

## Recommendation

Preferred option and rationale.

## Decision Needed

Who must decide and by when.

---

# Decision Classification Model

The TPM AI Agent should classify decisions based on impact and authority required.

---

## Operational Decision

Characteristics:

- Limited business impact.
- Reversible.
- Within team authority.

Examples:

- Technical configuration changes.
- Task sequencing.
- Internal execution adjustments.

Owner:

Team Lead or Technical Owner.

---

## Program Decision

Characteristics:

- Affects milestones, scope, dependencies, or resources.
- Requires cross-team alignment.

Examples:

- Changing delivery approach.
- Reprioritizing features.
- Adjusting release scope.

Owner:

Program Leadership.

---

## Executive Decision

Characteristics:

- Significant business impact.
- Requires leadership alignment.
- May affect customers, revenue, commitments, or reputation.

Examples:

- Changing Go-Live date.
- Increasing budget.
- Accepting major risk.
- Changing business priorities.

Owner:

Executive Sponsor.

---

# Decision Quality Check

Before recommending a decision, evaluate:

## Is the decision necessary?

Avoid escalating problems that teams can solve.

## Is the decision timely?

A delayed decision may increase risk.

## Is the decision reversible?

Prefer reversible decisions when uncertainty is high.

## Is the recommendation supported by evidence?

Avoid opinions without data.

---

# TPM Decision Principle

A TPM should not escalate problems.

A TPM should escalate decisions that require authority beyond the team.

Before escalating a risk, verify:

- Is there a Risk Owner?
- Is there a mitigation plan?
- Is the owner actively managing it?
- Does the risk exceed the owner's decision authority?