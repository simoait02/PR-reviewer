---
title: Dependencies and Supply Chain
description: Practices for selecting, pinning, updating, verifying, securing, licensing, and removing software dependencies and build artifacts.
category: dependencies-and-supply-chain
audience: developers, security-engineers, platform-engineers, technical-leads
tags: dependencies, vulnerabilities, licensing, provenance, reproducible-builds
content_type: engineering-best-practice
---

# Dependencies and Supply Chain

## Select dependencies deliberately

Evaluate maintenance activity, security history, license, transitive dependencies, release quality, documentation, community health, and operational fit. A dependency creates long-term ownership cost.

## Pin and reproduce

Use a lockfile or equivalent, record runtime and toolchain versions, and make builds reproducible. Review changes to dependency resolution rather than blindly accepting them.

## Update safely

Apply security updates promptly according to severity and exposure. Update other dependencies regularly in small batches, run the full test suite, inspect changelogs, and plan breaking upgrades.

## Verify provenance

Use trusted registries and authenticated sources. Prefer signed or verifiable artifacts when available. Restrict build permissions and separate dependency installation from sensitive deployment steps.

## Remove unnecessary dependencies

Delete unused packages and replace risky or unmaintained packages. Keep a software bill of materials or equivalent inventory when the project’s risk warrants it.

## Respect licensing

Track licenses and obligations for direct and transitive dependencies. Escalate incompatibilities before distribution.

## Establish dependency policy

Define approved sources, supported versions, review requirements, licensing rules, and who owns each major dependency. Prefer a small number of well-understood libraries over many overlapping packages. A package should have a clear purpose and a removal plan if it becomes unmaintained.

## Secure the build environment

Use isolated, reproducible build environments. Limit network and filesystem permissions for build steps, protect signing keys, and separate build identity from deployment identity. Do not execute unreviewed scripts from packages with production credentials.

## Verify updates

Review lockfile changes, transitive additions, install scripts, release notes, advisories, and integrity metadata. Test behavior and performance after upgrades. Treat a dependency update as a code change, not administrative maintenance.

## Respond to vulnerabilities

Inventory affected versions, determine whether vulnerable code is reachable, assess exposure, and choose upgrade, patch, configuration, isolation, or replacement. Record decisions when an immediate upgrade is impossible, including compensating controls, owner, and expiry date.

## Supply-chain checklist

- [ ] Direct and transitive dependencies are inventoried.
- [ ] Versions and build tools are reproducible.
- [ ] Dependency sources and artifacts are verified.
- [ ] Automated vulnerability checks have an owner and triage process.
- [ ] Updates are reviewed and tested.
- [ ] Build and deployment credentials are separated and restricted.
- [ ] Licenses and notices are tracked.
- [ ] Unused or abandoned dependencies are removed.
