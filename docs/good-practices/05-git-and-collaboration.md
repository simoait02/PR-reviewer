---
title: Git and Collaboration
description: Practices for repository hygiene, commit quality, branching, pull requests, conflict resolution, protected branches, and effective team collaboration.
category: collaboration
audience: developers, reviewers, technical-leads
tags: git, commits, branches, pull-requests, collaboration, repository-hygiene
content_type: engineering-best-practice
---

# Git and Collaboration

## Keep history useful

- Make commits small, coherent, and buildable when practical.
- Use imperative, specific commit messages that explain intent.
- Do not commit secrets, generated artifacts, local configuration, or credentials.
- Never rewrite shared history without team agreement.

## Branch and merge safely

Use a branching model that matches the delivery process. Keep branches short-lived, synchronize regularly, resolve conflicts deliberately, and protect important branches with required checks and review.

## Write useful pull requests

Include the problem, solution, scope, testing, risks, migration or rollout notes, examples where useful, and follow-up work. Keep the diff focused and call out areas needing special attention.

## Collaborate respectfully

Discuss code and evidence, not people. Ask clarifying questions before assuming intent. Make disagreements explicit, seek a decision, and document important outcomes.

## Maintain repository hygiene

Provide a clear README, contribution guide, license where applicable, ignore rules, local setup instructions, and automated checks. Keep the default branch releasable when the workflow allows it.

## Choose a workflow intentionally

Small teams often benefit from trunk-based development with short-lived branches and frequent integration. A release-branch model may be appropriate when versions are maintained independently. The important properties are that integration is frequent, branch rules are understandable, and the path from commit to release is visible.

## Protect important branches

Require successful automated checks, at least one appropriate reviewer, and resolved conversations before merging. Restrict force-push and direct production changes. Make exceptions auditable and time-limited rather than bypassing controls permanently.

## Resolve conflicts carefully

Understand both sides of a conflict and rerun relevant tests after resolution. Never resolve a conflict by choosing one side blindly. If the conflict reveals a design disagreement, stop and clarify the intended behavior instead of treating the merge result as the decision.

## Keep commits reviewable

Avoid mixing formatting churn, dependency upgrades, refactors, and behavior changes in one commit. If a mechanical change is necessary, isolate it. A good commit explains one logical change and can be reverted without leaving the system in a confusing state.

## Collaboration checklist

- [ ] Repository setup works from a clean checkout.
- [ ] Branch and merge rules are documented and enforced.
- [ ] Commits contain no secrets or accidental personal data.
- [ ] Pull requests explain behavior, tests, risks, and rollout.
- [ ] Conflicts are resolved using intended behavior, not convenience.
- [ ] Important decisions are recorded outside ephemeral chat.
- [ ] Generated files and local settings are handled consistently.

## Common failure modes

Long-lived branches create painful integration and hide defects. Giant pull requests overwhelm reviewers. Squashing unrelated work makes rollback difficult. Unprotected default branches allow unreviewed or untested changes. Use automation and repository policy to make the safe path the easy path.
