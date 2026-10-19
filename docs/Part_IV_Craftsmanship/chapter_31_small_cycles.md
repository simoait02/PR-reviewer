# Clean Code, Chapter 31: Small Cycles, PR review rules

## Integrate small, working changes frequently

`id: sc-frequent-small-integration | category: delivery | severity: high | source: book (Ch.31) + editorial | languages: any | tags: small-cycles, integration, commits, collaboration, merges`

**Look for in a diff:**
- Large changes held privately for days or weeks before integration
- A merge combining many unrelated behaviors and making failures hard to localize
- Work that blocks other contributors because its integration point is delayed

**Why it matters:** Small integrations reduce merge cost, expose incompatibilities early, and prevent one developer’s work from impeding the team.

**Suggested comment:** "This change has accumulated several behaviors before integration, increasing merge and regression risk. Could it be split into smaller working increments?"

**Fix:** Commit/push tested increments frequently and keep each integration point buildable.

## Keep each commit or push coherent and verifiable

`id: sc-coherent-verifiable-increments | category: version-control | severity: medium | source: book (Ch.31) + editorial | languages: any | tags: commits, history, tests, bisect, reviewability`

**Look for in a diff:**
- A commit mixing feature behavior, unrelated formatting, dependency upgrades, and cleanup
- A commit that cannot build or pass tests on its own without later commits
- History that makes rollback, review, or defect localization difficult

**Why it matters:** Coherent increments make the change history useful for review, debugging, rollback, and collaboration. Small does not mean arbitrary; it means a meaningful verifiable step.

**Suggested comment:** "This increment mixes unrelated work and is not independently verifiable. Could the feature, cleanup, and dependency changes be separated into coherent steps?"

**Fix:** Keep commits focused, buildable, and tested; use history rewriting before sharing when needed to present coherent integration units.

## Keep the main line healthy

`id: sc-mainline-always-green | category: continuous-integration | severity: critical | source: book (Ch.31) + editorial | languages: any | tags: ci, mainline, build, tests, integration`

**Look for in a diff:**
- A push that knowingly leaves the build or test suite failing
- Broken checks tolerated because “someone will fix it later”
- Tests disabled, skipped, or weakened to restore a green status

**Why it matters:** A failing main line blocks everyone and destroys the signal that tells the team whether new changes are safe. Ignored failures become normal and eventually become lies.

**Suggested comment:** "This leaves the main line red/weakens the check. Could we fix or revert the change before integrating so the build remains trustworthy?"

**Fix:** Run the relevant build/tests before pushing, repair or revert failures immediately, and never normalize a broken main line.

## Use reliable tests to make frequent integration safe

`id: sc-tests-enable-integration | category: testing | severity: critical | source: book (Ch.31) + editorial | languages: any | tags: ci, tests, integration, regressions, confidence`

**Look for in a diff:**
- Frequent integration without regression coverage for changed behavior
- A fast green build that omits important acceptance or contract checks
- Merges performed manually because the team does not trust automated tests

**Why it matters:** Small cycles work only when the team can detect integration errors quickly. Reliable tests turn frequent integration from a coordination risk into a feedback mechanism.

**Suggested comment:** "The change will integrate frequently, but the suite does not cover the affected contract. Could the missing regression/acceptance check be added before relying on the green build?"

**Fix:** Maintain fast unit checks plus appropriate acceptance, contract, and integration tests for the changed boundary.

## Avoid long-lived branches unless the change is genuinely isolated

`id: sc-avoid-long-lived-branches | category: collaboration | severity: high | source: book (Ch.31) + editorial | languages: any | tags: branches, integration, merge-conflicts, isolation, git`

**Look for in a diff:**
- Feature branches diverging for days or weeks while surrounding code changes
- A branch with a large final merge and no intermediate integration strategy
- Branch isolation used to hide incomplete or untested work from feedback

**Do not flag when:** the work is genuinely isolated, cannot be sliced safely, and has strong tests plus an explicit integration plan.

**Why it matters:** Long-lived branches accumulate conflicts and make it difficult to know whether the combined system works. Isolation is justified only when the merge cost is bounded and understood.

**Suggested comment:** "This branch has diverged substantially, so integration will be risky. Could the work be integrated incrementally or protected behind a safe toggle?"

**Fix:** Prefer short-lived branches and frequent integration; use a long-lived branch only for isolated work with a deliberate merge plan.

## Use safe toggles for incomplete mainline work

`id: sc-safe-feature-toggles | category: delivery | severity: high | source: book (Ch.31) + editorial | languages: any | tags: feature-flags, toggles, incomplete-features, release, safety`

**Look for in a diff:**
- Partially implemented behavior reachable by production users
- A feature flag with unsafe defaults, unclear ownership, or no removal plan
- Toggle checks scattered across policy code instead of one controlled boundary

**Do not flag when:** the feature is fully implemented and the toggle is an intentional operational control with documented lifecycle and access rules.

**Why it matters:** Safe toggles allow incomplete work to integrate without exposing it. Poor toggles create hidden branches, stale complexity, and accidental production activation.

**Suggested comment:** "This incomplete path can be enabled in production, but the default/permissions/removal plan are unclear. Could the toggle be isolated and its lifecycle documented?"

**Fix:** Default safely, isolate the toggle at a boundary, test both states, restrict activation, monitor it, and remove it when rollout completes.

## Keep partial features behaviorally inert until ready

`id: sc-incomplete-code-not-user-visible | category: release | severity: high | source: book (Ch.31) + editorial | languages: any | tags: feature-flags, rollout, incomplete, ui, production`

**Look for in a diff:**
- New buttons/routes/events exposing unfinished behavior
- Partially wired commands that can be triggered through an undocumented path
- Incomplete data migrations or handlers active before all consumers are compatible

**Why it matters:** Integrating code is safe only if unfinished behavior cannot affect users or existing paths. Hiding a UI button is not enough if alternate entry points remain reachable.

**Suggested comment:** "The unfinished behavior is reachable through this route/event even though the primary UI is hidden. Could all entry points be guarded until the feature is complete?"

**Fix:** Guard every activation path, use compatible migrations, and test the disabled state as part of the release contract.

## Automate build and deployment cycles

`id: sc-automated-build-deployment | category: delivery | severity: high | source: book (Ch.31) + editorial | languages: any | tags: build, deployment, automation, ci, cd, reproducibility`

**Look for in a diff:**
- Manual build, packaging, configuration, or deployment steps
- A build that cannot run automatically on every push
- Deployment scripts treated as external to the tested system

**Why it matters:** Automation shortens the cycle and removes human variation. Build/deployment code is part of the system and can fail just like application code.

**Suggested comment:** "This release still depends on manual setup, which prevents short repeatable cycles. Could the build/deployment step be scripted and tested?"

**Fix:** Automate build, packaging, configuration, migration, rollout, and rollback; validate the automation in CI or a disposable environment.

## Make the build fast enough for frequent feedback

`id: sc-fast-continuous-build | category: build | severity: high | source: book (Ch.31) + editorial | languages: any | tags: build-speed, ci, feedback, incremental-build, developer-productivity`

**Look for in a diff:**
- Unnecessary full rebuilds or slow checks added to every small change
- Developers waiting so long that they batch changes instead of integrating
- Build bottlenecks left unmeasured despite frequent-cycle goals

**Why it matters:** Slow builds expand cycle time, increase change batch size, and delay detection of integration errors. Build speed is an architectural and team productivity concern.

**Suggested comment:** "This change adds a costly step to every push and may encourage larger batches. Could it be optimized, cached, or moved to an appropriate slower validation stage?"

**Fix:** Measure bottlenecks, parallelize/cache safely, split fast checks from slow checks, and keep the required push feedback short.

## Treat a broken build as an immediate team problem

`id: sc-broken-build-is-urgent | category: collaboration | severity: critical | source: book (Ch.31) + editorial | languages: any | tags: ci, build, incident, ownership, alerts`

**Look for in a diff:**
- A red build left unresolved while unrelated work continues
- Alerts suppressed because failures are frequent or annoying
- A failing test deleted or quarantined without a replacement plan

**Why it matters:** The main build is shared infrastructure for the team. The longer it stays broken, the less trustworthy it becomes and the more failures accumulate behind it.

**Suggested comment:** "The build has been failing long enough to block reliable integration. Could we stop unrelated work and fix/revert the cause before adding more changes?"

**Fix:** Assign ownership immediately, fix or revert, restore the signal, and only quarantine a flaky check with an owner and deadline.
