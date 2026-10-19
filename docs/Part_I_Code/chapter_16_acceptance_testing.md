# Clean Code, Chapter 16: Acceptance Testing, PR review rules

## Express requirements as executable acceptance tests

`id: at-requirements-as-tests | category: requirements | severity: high | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, requirements, behavior, specification, qa`

**Look for in a diff:**
- A feature implemented from prose with no executable acceptance criteria
- Requirements that cannot be mapped to inputs, actions, and expected outcomes
- QA sign-off based on an undocumented or manually remembered scenario

**Why it matters:** The behavior that is actually tested becomes the behavior the team can verify before release. Executable acceptance tests make requirements precise, reviewable, and repeatable.

**Suggested comment:** "This feature has no executable acceptance criterion for its expected behavior. Could the requirement be captured as an input, action, and observable outcome?"

**Fix:** Add acceptance tests that specify the user-visible behavior and make them part of the feature’s definition of done.

## Keep business, QA, and developers aligned on scenarios

`id: at-shared-acceptance-language | category: collaboration | severity: high | source: book (Ch.16) + editorial | languages: any | tags: ba, qa, developers, collaboration, shared-language`

**Look for in a diff:**
- Acceptance tests written only in implementation terms that business or QA cannot validate
- Different interpretations of the same requirement across product, QA, and code
- A developer automating a scenario without evidence that the author considers it faithful

**Why it matters:** Acceptance tests are a shared specification, not merely another developer test. A common language exposes ambiguity before implementation and makes automation auditable by the people who own the requirement.

**Suggested comment:** "This scenario is expressed in internal API details, so its fidelity to the business requirement is difficult to review. Could it use user-visible language and be confirmed by BA/QA?"

**Fix:** Agree on readable scenario language, review the cases with business and QA stakeholders, and keep implementation details behind the test steps.

## Use Given-When-Then or Arrange-Act-Assert consistently

`id: at-given-when-then-structure | category: testing | severity: medium | source: book (Ch.16) + editorial | languages: any | tags: bdd, given-when-then, aaa, acceptance-tests, structure`

**Look for in a diff:**
- Acceptance cases that mix setup, action, and expected results
- A scenario with multiple unrelated actions or unclear preconditions
- Test tables whose columns do not identify inputs, operation, and output

**Why it matters:** A consistent scenario structure makes requirements easy to read and automate. It also reveals missing inputs, ambiguous actions, and incomplete expected results.

**Suggested comment:** "The scenario does not distinguish its precondition, action, and expected result. Could it be rewritten as Given, When, Then so the contract is unambiguous?"

**Fix:** Define the initial state, one meaningful user action, and the observable result for each scenario.

## Cover happy paths and meaningful failure paths

`id: at-cover-success-and-failure | category: testing | severity: high | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, qa, happy-path, failure, edge-cases`

**Look for in a diff:**
- Acceptance coverage limited to the expected successful workflow
- Missing cases for invalid input, authorization, unavailable dependencies, limits, or recovery
- QA scenarios that explore failures but are not automated or retained

**Why it matters:** Business scenarios define intended success, while failure scenarios define safe behavior under real conditions. Both are part of a complete feature specification.

**Suggested comment:** "The acceptance suite covers the successful workflow but not the rejected input/permission failure. Could QA add the expected user-visible behavior for that case?"

**Fix:** Add representative happy-path, boundary, and failure scenarios with explicit expected outcomes.

## Make acceptance tests user-observable

`id: at-user-observable-contract | category: testing | severity: high | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, black-box, user-behavior, contract, api`

**Look for in a diff:**
- Acceptance tests asserting private fields, database implementation details, or internal call order
- A test passing while the user-visible response, state, or side effect is wrong
- Scenarios coupled to one implementation rather than the supported contract

**Why it matters:** Acceptance tests verify that the feature works for its consumers. Internal assertions make the suite brittle and can provide false confidence when the external behavior regresses.

**Suggested comment:** "This acceptance test verifies an internal persistence detail rather than what the user or API client observes. Could it assert the resulting response or externally visible state?"

**Fix:** Drive the system through supported interfaces and assert user-visible outputs, state transitions, and business outcomes.

## Keep acceptance cases independent and deterministic

`id: at-independent-deterministic-scenarios | category: testing | severity: high | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, isolation, repeatability, fixtures, ci`

**Look for in a diff:**
- Scenarios depending on execution order, shared accounts, or data from another case
- Current-time, random, network, or environment-sensitive expectations
- Acceptance tests that pass only when a specific environment or prior test has prepared state

**Why it matters:** Acceptance tests run in continuous builds and must provide trustworthy release evidence. Nondeterministic or coupled cases create noise and hide real regressions.

**Suggested comment:** "This scenario relies on state from another test/current time. Could it create its own fixture and control the environment so it is repeatable in CI?"

**Fix:** Isolate fixtures, control time and randomness, and make external dependencies explicit through stable test environments or contract doubles.

## Keep one meaningful behavior per acceptance scenario

`id: at-single-behavior-scenario | category: testing | severity: medium | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, scope, diagnostics, scenarios, readability`

**Look for in a diff:**
- A scenario that walks through multiple independent features before asserting results
- A failure that cannot identify which user behavior is broken
- End-to-end cases used as a substitute for focused acceptance contracts

**Why it matters:** Focused scenarios produce clearer requirements and actionable failures. Large workflows are expensive to debug and can pass despite a broken intermediate behavior.

**Suggested comment:** "This scenario verifies several independent behaviors, so a failure will not identify the broken requirement. Could the cases be split while keeping a separate critical-path journey if needed?"

**Fix:** Keep each acceptance test centered on one user-visible behavior and use a small number of full journeys for cross-feature confidence.

## Automate acceptance tests without hiding their meaning

`id: at-automation-preserves-meaning | category: testing | severity: medium | source: book (Ch.16) + editorial | languages: any | tags: automation, acceptance-tests, readability, test-dsl, traceability`

**Look for in a diff:**
- Step definitions that hide important business conditions behind generic helpers
- A test framework syntax that is readable but automation does not actually execute the authored steps
- Acceptance cases requiring developers to decode low-level setup before validating the requirement

**Why it matters:** Automation saves repeated manual effort only if it faithfully executes the intended requirement. Readable steps let BA and QA inspect that mapping and detect drift.

**Suggested comment:** "This step is generic enough to hide the business rule it executes. Could the acceptance language state the condition and outcome directly while the helper handles mechanics?"

**Fix:** Keep scenario text business-readable, map each step transparently to automation, and review the mapping with the requirement authors.

## Define acceptance tests before declaring a feature done

`id: at-tests-define-done | category: delivery | severity: high | source: book (Ch.16) + editorial | languages: any | tags: definition-of-done, acceptance-tests, release, feature-complete`

**Look for in a diff:**
- A feature marked complete while acceptance scenarios are missing or failing
- Tests added after release approval as documentation rather than as a delivery gate
- Manual sign-off that does not identify the cases that passed

**Why it matters:** A feature is not complete merely because its code compiles or unit tests pass. Acceptance tests connect implementation to the user requirement and provide a concrete completion criterion.

**Suggested comment:** "The feature is marked done without passing acceptance coverage for the new behavior. Could the acceptance cases become a completion gate?"

**Fix:** Define acceptance cases with the feature, automate them where practical, and require them to pass before completion or release.

## Run acceptance tests in the continuous build

`id: at-continuous-build-coverage | category: delivery | severity: high | source: book (Ch.16) + editorial | languages: any | tags: ci, continuous-build, acceptance-tests, regression, release`

**Look for in a diff:**
- Acceptance tests that run only manually or on a developer workstation
- New scenarios not included in the CI/build pipeline
- A build reported green while acceptance tests were skipped or unavailable

**Why it matters:** Continuous execution catches regressions soon after they are introduced and keeps the whole team aware of system behavior. A test outside the build cannot reliably protect future changes.

**Suggested comment:** "This acceptance test is not part of the continuous build, so later changes can break the feature silently. Could it be integrated into the appropriate CI suite?"

**Fix:** Add the test to the continuous build, publish a visible result, and make skipped or unavailable acceptance checks fail or be explicitly reported.

## Stop and repair acceptance regressions

`id: at-repair-failing-acceptance-tests | category: delivery | severity: high | source: book (Ch.16) + editorial | languages: any | tags: ci, regression, build, triage, release`

**Look for in a diff:**
- A known failing acceptance test left in the build while unrelated work continues
- Flaky failures retried or ignored without root-cause work
- A release approved despite a regression in an existing user behavior

**Why it matters:** Accumulated failures destroy trust in the continuous build and make it impossible to distinguish a new regression from existing noise.

**Suggested comment:** "This acceptance regression is being left in the build, which makes future failures ambiguous. Could it be fixed, reverted, or explicitly isolated before continuing?"

**Fix:** Treat failures as urgent feedback: repair the behavior or test, revert the introducing change, and keep the build signal trustworthy.

## Keep acceptance tests maintainable and traceable

`id: at-maintainable-traceable-scenarios | category: maintainability | severity: medium | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, traceability, requirements, maintenance, refactoring`

**Look for in a diff:**
- Scenarios with no link to a requirement, story, or business outcome
- Duplicated steps and fixtures that make requirement changes expensive
- Obsolete acceptance cases retained after the product behavior changes

**Why it matters:** Acceptance suites are the executable requirements document. Without traceability and maintenance, they drift from the product and become too costly to trust.

**Suggested comment:** "This scenario has no clear requirement owner and duplicates setup from several cases. Could it be linked to the business rule and refactored without hiding its intent?"

**Fix:** Keep scenarios concise, link them to requirements, remove obsolete cases, and refactor shared mechanics while preserving readable behavior.

## Use human review where automation cannot fully judge output

`id: at-human-review-for-subjective-output | category: testing | severity: medium | source: book (Ch.16) + editorial | languages: any | tags: acceptance-tests, subjective-output, ai, visual, human-review`

**Look for in a diff:**
- Visual, wording, ranking, or AI output accepted with no defined quality criteria
- Exact snapshots used where valid variation is expected
- Manual review performed inconsistently with no record of the evaluated scenario

**Do not flag when:** objective invariants are automated and the remaining subjective judgment has a documented rubric and review record.

**Why it matters:** Not every user-visible result has one exact expected string or pixel arrangement. Explicit human evaluation can complement automation when the criteria and scope are clear.

**Suggested comment:** "This output cannot be fully judged by exact equality, but the acceptance check has no rubric or recorded review. Could the acceptable qualities and evaluation process be made explicit?"

**Fix:** Automate objective invariants, define tolerances or representative examples, and retain structured human review for genuinely subjective behavior.
