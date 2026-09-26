---
title: Requirements and Planning
description: Practices for writing actionable requirements, defining acceptance criteria, prioritizing work, managing dependencies, estimating effort, and tracking project risk.
category: requirements-and-planning
audience: product-managers, project-managers, developers, technical-leads
tags: requirements, acceptance-criteria, prioritization, estimation, risk
content_type: engineering-best-practice
---

# Requirements and Planning

## Write actionable requirements

Describe observable behavior and constraints. Include actor, trigger, expected result, failure behavior, and acceptance criteria. Avoid vague terms such as “fast,” “easy,” or “secure” without a measurable interpretation.

## Consider the whole workflow

For every significant change, ask about normal and exceptional flows, permissions and abuse cases, validation and retention, accessibility and internationalization, performance and scale, migration, support, and rollback.

## Prioritize deliberately

Prioritize by user value, risk reduction, urgency, dependencies, and cost. Make trade-offs visible when capacity is limited.

## Plan incrementally

Break work into vertical slices that produce a demonstrable outcome. Identify dependencies and the critical path. Include discovery, integration, testing, review, and operational work.

## Track risk

For each material risk, document probability, impact, warning signs, mitigation, contingency, owner, and next review date. Reduce uncertainty early with prototypes or experiments.

## Estimate responsibly

Use estimates as forecasts, not promises. Include testing, documentation, reviews, deployment, and coordination. Express uncertainty and update forecasts when evidence changes.

## Use a consistent requirement format

A useful requirement usually contains:

1. **Context:** why the change is needed and who benefits.
2. **Behavior:** what the system must do.
3. **Rules:** validations, permissions, limits, and business constraints.
4. **Failure behavior:** what happens when input or dependencies are invalid.
5. **Acceptance criteria:** observable conditions that prove completion.
6. **Operational notes:** telemetry, migration, rollout, and support needs.

Example acceptance criteria should be testable: “When an authenticated customer submits a valid order, the order is persisted once and a confirmation is shown.” Also specify relevant negative cases: “If payment authorization fails, no fulfilled order is created and the customer receives a retry-safe error.”

## Separate discovery from commitment

When important information is missing, create a time-boxed discovery task rather than pretending the work is fully understood. Discovery may include user interviews, data analysis, technical spikes, prototypes, threat modeling, or performance experiments. Record what was learned, what remains uncertain, and how the result changes the plan.

## Manage dependencies

For each dependency, identify the providing team or service, required interface, expected date, failure impact, and fallback. Prefer contracts and test doubles that allow parallel work. Do not schedule dependent work as if the dependency were guaranteed unless the risk is accepted explicitly.

## Use a decision-oriented backlog

Each backlog item should have an owner, priority reason, status, acceptance criteria, dependencies, and an indication of uncertainty. Split items when they contain multiple independent outcomes. Close or archive stale items; an enormous backlog is not a plan.

## Planning checklist

- [ ] The user problem is clear and validated.
- [ ] Acceptance criteria cover success and failure.
- [ ] Security, privacy, accessibility, and operational needs are included.
- [ ] Unknowns have discovery tasks and time limits.
- [ ] Dependencies and critical path are visible.
- [ ] Work is sliced into independently demonstrable increments.
- [ ] The plan includes release, support, and rollback work.
- [ ] Risks are reviewed when evidence or scope changes.

## Anti-patterns

Avoid turning estimates into commitments before discovery, writing requirements as implementation instructions, planning only developer tasks, and measuring progress by percentage complete. “Ninety percent done” is meaningless if integration, testing, migration, or release remains. Measure completed outcomes and working increments instead.
