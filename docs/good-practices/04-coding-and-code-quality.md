---
title: Coding and Code Quality
description: Practices for writing readable, maintainable, secure, testable, and consistent code while handling errors, validation, state, abstractions, and technical debt.
category: code-quality
audience: developers, reviewers, technical-leads
tags: readability, errors, validation, state, abstractions, technical-debt
content_type: engineering-best-practice
---

# Coding and Code Quality

## Prefer readable code

- Use names that reveal intent.
- Keep functions and modules cohesive and reasonably small.
- Make control flow and state changes easy to follow.
- Prefer explicit behavior over clever tricks.
- Remove dead code and commented-out code.

## Follow project conventions

Use a formatter, linter, type checker, and compiler or static analyzer where available. Configure them consistently and run them automatically in local development and CI.

## Handle errors deliberately

Validate inputs at trust boundaries. Preserve useful context when propagating errors. Do not catch errors merely to ignore them, expose sensitive details, or return success after failure. Define which failures are recoverable.

## Keep changes focused

Avoid mixing unrelated refactors with behavior changes. Small changes are easier to review, test, deploy, and revert.

## Manage technical debt

Make debt visible with its impact and a suggested follow-up. Pay down debt that increases security, reliability, delivery, or maintenance risk.

## Review before sharing

Run formatting, static checks, tests, and a manual inspection before opening a pull request. Check boundaries, failure paths, logging, and backwards compatibility.

## Establish a maintainable structure

Organize code around cohesive behavior rather than arbitrary technical layers. Keep public interfaces small and stable. Hide implementation details behind clear boundaries. Avoid modules that know too much about unrelated parts of the system. When a module changes for many unrelated reasons, it is a signal that responsibilities should be separated.

## Validate at boundaries

Validate external input at the point where it enters the system, then use trusted internal representations. Validate type, format, range, size, encoding, and allowed values. Do not rely on client-side validation for security or correctness. Reject invalid data clearly and avoid partial state changes.

## Make state transitions explicit

For workflows with meaningful states, define valid transitions and reject impossible ones. Make operations idempotent where retries or duplicate messages are possible. Use transactions or compensating actions deliberately; do not assume a multi-system operation is atomic.

## Choose abstraction carefully

Abstract stable concepts, not guesses about future requirements. An abstraction should reduce duplication or isolate a real variation. Too little abstraction creates repetition; too much creates indirection, hidden behavior, and difficult debugging. Prefer duplication temporarily over a wrong shared abstraction.

## Optimize with evidence

First make behavior correct and measurable. Profile before optimizing. Improve algorithms, I/O, allocation, caching, and concurrency based on evidence. Document important performance assumptions and add regression tests or benchmarks when an optimization is safety-critical.

## Code quality checklist

- [ ] Names and structure communicate intent.
- [ ] Input validation and authorization occur at trust boundaries.
- [ ] Errors retain useful context and do not leak sensitive data.
- [ ] State transitions and retry behavior are safe.
- [ ] Configuration has safe defaults and clear validation.
- [ ] Logging is useful without exposing secrets or personal data.
- [ ] The change has focused scope and appropriate tests.
- [ ] Static analysis and formatting are automated.
