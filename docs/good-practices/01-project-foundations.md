---
title: Project Foundations
description: Practices for defining a software project’s purpose, scope, stakeholders, outcomes, constraints, quality expectations, and decision-making process.
category: project-management
audience: product-managers, project-managers, technical-leads
tags: scope, stakeholders, outcomes, constraints, decisions
content_type: engineering-best-practice
---

# Project Foundations

## Establish the purpose

- State the user problem and the outcome the project should produce.
- Identify primary users, affected stakeholders, and the person accountable for decisions.
- Define measurable success criteria; implementation alone is not success.
- Record assumptions, constraints, deadlines, compliance obligations, and out-of-scope work.

## Make scope explicit

- Maintain a short project brief as the source of truth.
- Separate must-have, should-have, and optional work.
- Write down non-goals to prevent scope drift.
- Prefer a small, usable first release over a large release with uncertain value.

## Define quality

Agree early on security, availability, performance, accessibility, privacy, portability, and maintainability expectations. Give important attributes measurable targets where possible.

## Define done

A work item is done only when implementation, tests, documentation, review, security impact, telemetry, and deployment considerations are complete for its risk level. Do not silently move unfinished work into “done.”

## Manage decisions

Record decisions that affect future work: context, decision, alternatives, consequences, owner, and date. Revisit a decision when its assumptions change; do not rewrite history.

## Identify stakeholders and users

Create a stakeholder map. Distinguish users, customers, operators, administrators, security owners, legal or compliance owners, support teams, and teams that depend on the system. Different groups may have different definitions of success. Identify who can approve scope, who can accept risk, who must be consulted, and who must be informed.

## Define measurable outcomes

Use outcome measures instead of activity measures. “Ship the dashboard” is an output; “reduce the time to identify a failed payment from two hours to ten minutes” is an outcome. Define a baseline, target, measurement method, owner, and review date. Avoid metrics that encourage harmful behavior, such as optimizing ticket count instead of user value.

## Establish constraints explicitly

Capture budget, staffing, deadlines, supported platforms, data residency, regulatory requirements, uptime expectations, integration limitations, and organizational policies. Constraints should influence design and planning. A constraint that is not written down will eventually be rediscovered as a surprise.

## Set project operating rules

Agree on where requirements, decisions, code, incidents, and status updates live. Define how urgent decisions are made, how risks are escalated, expected review time, and who can approve exceptions. These rules reduce coordination overhead and prevent knowledge from becoming private or tribal.

## Foundation checklist

- [ ] The problem and intended users are clearly described.
- [ ] Success measures have baselines, targets, and owners.
- [ ] Scope, non-goals, constraints, and assumptions are written down.
- [ ] Stakeholders and decision rights are known.
- [ ] Quality attributes have explicit expectations.
- [ ] Major risks and dependencies have owners.
- [ ] The definition of done covers operational readiness.
- [ ] The project has a single discoverable source of truth.

## Common failure modes

Projects often fail because they optimize for delivery of features rather than outcomes, begin implementation before resolving key assumptions, treat non-functional requirements as “later,” or allow every request to enter scope. Another common failure is having no accountable decision-maker, which causes unresolved disagreements and rework. Correct these problems by making decisions and trade-offs visible early.
