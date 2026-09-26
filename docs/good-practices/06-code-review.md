---
title: Code Review
description: Practices for performing efficient, risk-based, respectful code reviews that identify correctness, security, testing, operability, and maintainability issues.
category: code-review
audience: developers, reviewers, technical-leads
tags: review, correctness, security, testing, maintainability, feedback
content_type: engineering-best-practice
---

# Code Review

## Review the right things

Prioritize correctness, security, data integrity, compatibility, failure handling, tests, operability, and maintainability. Automate formatting and trivial style concerns.

## Review efficiently

Understand the problem before implementation details. Review the diff and relevant surrounding code. Test important behavior locally when risk warrants it. Ask for evidence when claims depend on performance, security, or compatibility.

## Give actionable feedback

State the issue, why it matters, and a concrete direction when possible. Distinguish blocking defects from suggestions. Avoid comments that merely reflect personal preference unless they follow an agreed standard.

## Review for missing work

Check validation, authorization, error paths, observability, documentation, migrations, feature flags, rollback, and tests—not only the changed happy path.

## Keep review healthy

Set reasonable review-size expectations and response times. Authors should respond to each comment and explain intentional decisions. Approve when blocking concerns are resolved rather than demanding perfection.

## Classify findings by severity

Use a shared vocabulary such as:

- **Blocker:** creates a serious correctness, security, data-loss, or release risk.
- **Major:** likely causes user impact, operational trouble, or substantial maintenance cost.
- **Minor:** worthwhile improvement that does not need to block the change.
- **Suggestion:** optional alternative or learning opportunity.

The exact labels matter less than making the impact and blocking status explicit.

## Review in a useful order

First confirm that the change solves the stated problem. Then inspect architecture and data flow, authorization and trust boundaries, failure handling, tests, observability, and maintainability. Review details such as naming and style afterward. This prevents spending time polishing code that implements the wrong behavior.

## Ask high-value questions

Examples include: What happens on duplicate requests? What if the dependency times out? Can an unauthorized user reach this path? What data is persisted and for how long? How is this rolled back? How will an operator know it is failing? What test would fail if this behavior regressed? Questions are often more constructive than rewriting the author’s code.

## Review tests critically

Check that tests prove externally meaningful behavior, include negative cases, and would fail if the implementation were broken. Beware tests that only assert a mock was called, snapshot large unstable outputs, or rely on shared state. Test names should explain the behavior and condition.

## Review checklist

- [ ] Problem and intended behavior are clear.
- [ ] The diff is focused and understandable.
- [ ] Authorization, validation, and sensitive data handling are correct.
- [ ] Error, timeout, retry, duplicate, and partial-failure behavior is safe.
- [ ] Tests cover important positive and negative paths.
- [ ] Logs, metrics, alerts, and documentation are sufficient.
- [ ] Migration, compatibility, rollout, and rollback are addressed.
- [ ] Feedback is actionable, respectful, and correctly prioritized.
