---
title: Delivery and Operations
description: Practices for trustworthy CI/CD, reproducible artifacts, environment management, safe releases, migrations, configuration, rollback, and operational readiness.
category: delivery-and-operations
audience: developers, platform-engineers, release-engineers, operators
tags: ci-cd, releases, migrations, configuration, rollback, deployment
content_type: engineering-best-practice
---

# Delivery and Operations

## Automate the delivery path

CI should install from a clean environment, validate formatting and static checks, run tests, build artifacts, scan relevant risks, and publish clear results. Keep pipelines repeatable and fail for actionable reasons.

## Separate environments safely

Keep development, staging, and production configuration separate. Do not treat staging as proof of production safety when infrastructure, data, traffic, or permissions differ materially.

## Release gradually

Use small releases, feature flags, canaries, blue-green deployment, or staged rollouts when risk justifies them. Define success metrics, an owner, a stop condition, and rollback steps before release.

## Manage schema and data changes

Make migrations backward-compatible when old and new application versions may coexist. Take backups where appropriate, test migration duration and failure recovery, and never assume destructive changes are reversible.

## Roll back deliberately

Know whether rollback means reverting code, disabling a flag, restoring data, or applying a forward fix. Test the chosen recovery path and consider irreversible side effects.

## Keep operations documented

Document deployment prerequisites, configuration, health checks, common failures, escalation, runbooks, and ownership. Update these documents after operational changes.

## Use a promotion model

Build an immutable artifact once, then promote the same artifact through environments. Keep environment-specific configuration separate and auditable. Avoid rebuilding differently for production, because that makes testing evidence unreliable.

## Make CI trustworthy

Run checks from a clean checkout with pinned tools and dependencies. Cache only what is safe and invalidate caches correctly. Publish test reports and artifact identifiers. Make failures reproducible and keep pipeline credentials narrowly scoped.

## Design safe releases

Before release, identify affected users, database changes, dependencies, dashboards, alerts, support notes, success metrics, and stop conditions. During rollout, watch both technical and business indicators. Stop or roll back when predefined conditions are met; do not continue because of schedule pressure.

## Manage configuration

Validate configuration at startup or deployment, document defaults, and fail clearly for missing required values. Separate secrets from ordinary configuration. Version important configuration changes and audit who changed production settings.

## Migrations and compatibility

Use expand-and-contract migrations when old and new versions overlap: add compatible structures, deploy code that can use both, backfill safely, switch reads or writes, then remove old structures only after verification. Make backfills restartable and observable.

## Operations checklist

- [ ] Build artifacts are reproducible and identifiable.
- [ ] CI checks code, tests, security, and packaging from a clean environment.
- [ ] Environments and configuration are separated.
- [ ] Release metrics, owner, stop conditions, and rollback are defined.
- [ ] Migrations support mixed application versions when required.
- [ ] Health checks distinguish readiness from liveness.
- [ ] Runbooks and escalation paths are current.
- [ ] Restoration and rollback procedures have been exercised.
