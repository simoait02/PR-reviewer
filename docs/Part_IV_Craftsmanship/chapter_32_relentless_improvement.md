# Clean Code, Chapter 32: Relentless Improvement, PR review rules

## Leave touched code better without expanding scope recklessly

`id: ri-boy-scout-improvement | category: maintainability | severity: medium | source: book (Ch.32) + editorial | languages: any | tags: boy-scout-rule, cleanup, refactoring, scope, maintainability`

**Look for in a diff:**
- Code left slightly worse after a feature change when a small safe cleanup was available
- Cleanup mixed into a large unrelated rewrite that is difficult to review
- “Improve everything” changes that expand risk beyond the touched behavior

**Why it matters:** Small improvements prevent structural decay and make future changes easier. The cleanup must remain reviewable and protected by tests.

**Suggested comment:** "This touched area still has a small naming/duplication issue that makes the new behavior harder to read. Could we improve it locally without broadening the change?"

**Fix:** Make focused improvements around the changed code, keep them behavior-preserving, and separate larger refactors into their own tested changes.

## Use coverage as a diagnostic, not a punishment

`id: ri-coverage-as-developer-tool | category: testing | severity: medium | source: book (Ch.32) + editorial | languages: any | tags: coverage, metrics, assertions, incentives, testing`

**Look for in a diff:**
- Coverage thresholds met with trivial/no assertions
- Coverage used as the sole quality gate or team performance target
- A percentage increase presented as proof that behavior is tested

**Why it matters:** Coverage measures execution, not whether tests verify semantics. Punitive targets encourage gaming and can reduce trust in the metric.

**Suggested comment:** "Coverage increased, but the new test does not assert the behavior meaningfully. Could we use the metric to find an unverified path rather than optimize the percentage alone?"

**Fix:** Use line/branch coverage to identify gaps, add meaningful assertions, and interpret the result with risk and behavior evidence.

## Improve coverage toward the meaningful behavior surface

`id: ri-meaningful-coverage | category: testing | severity: high | source: book (Ch.32) + editorial | languages: any | tags: coverage, branches, behavior, tests, risk`

**Look for in a diff:**
- New branches, error paths, or policy variants with no focused tests
- High-risk code excluded from coverage without compensating checks
- Coverage declining in the exact area changed by the PR

**Do not flag when:** generated/unreachable/boundary code is intentionally excluded and its behavior is covered by an appropriate integration or contract test.

**Why it matters:** The useful goal is increasing confidence in required behavior, approaching complete meaningful coverage over time rather than chasing an arbitrary number.

**Suggested comment:** "The changed branch is unverified despite the overall percentage. Could we add a behavior test or explain the boundary and its compensating check?"

**Fix:** Cover meaningful lines and decisions, prioritize consequential paths, and document deliberate exclusions.

## Use mutation testing to find weak assertions

`id: ri-mutation-testing | category: testing | severity: medium | source: book (Ch.32) + editorial | languages: any | tags: mutation-testing, assertions, semantic-coverage, surviving-mutants, quality`

**Look for in a diff:**
- High line/branch coverage but tests that would pass if comparisons, constants, or assignments changed
- Critical policies with no assessment of assertion strength
- Mutation results ignored or surviving mutations repeatedly accepted without rationale

**Why it matters:** Mutation testing asks whether tests detect semantic changes, not merely whether code executed. Surviving mutations reveal gaps in the test oracle.

**Suggested comment:** "Coverage shows execution but not semantic protection for this decision. Could mutation testing or stronger assertions check whether incorrect comparisons would fail?"

**Fix:** Run mutation analysis on critical modules when practical, investigate surviving mutations, and strengthen tests rather than only increasing execution coverage.

## Preserve semantic stability during refactoring

`id: ri-semantic-stability | category: refactoring | severity: critical | source: book (Ch.32) + editorial | languages: any | tags: semantic-stability, refactoring, regression, acceptance-tests, behavior`

**Look for in a diff:**
- Structural changes that alter required behavior without updated acceptance criteria
- Tests that pass despite removed/changed user-visible semantics
- Refactors relying only on implementation snapshots

**Why it matters:** Semantic stability means required behavior remains protected while structure changes. It is what makes cleanup and refactoring safe.

**Suggested comment:** "This refactor changes a behavior boundary, but the suite does not prove the required semantics remain unchanged. Could acceptance/regression tests cover the contract?"

**Fix:** Combine unit, acceptance, contract, and integration tests appropriate to the behavior before and after structural changes.

## Use small cleanups to test flexibility

`id: ri-cleanups-test-flexibility | category: design | severity: medium | source: book (Ch.32) + editorial | languages: any | tags: refactoring, flexibility, design-smell, cohesion, coupling`

**Look for in a diff:**
- A trivial rename or extraction unexpectedly requiring broad changes
- Cleanup blocked by hidden dependencies, globals, or tangled responsibilities
- Developers avoiding harmless edits because the code is too risky to touch

**Why it matters:** The cost of a small behavior-preserving change is evidence about structural flexibility. Difficult cleanup exposes an area where dependencies or boundaries need improvement.

**Suggested comment:** "This small cleanup requires changes across unrelated modules, which suggests hidden coupling. Could we isolate the dependency before proceeding?"

**Fix:** Use safe small refactors to discover inflexibility, then reduce coupling and add tests before larger changes.

## Improve names and organization when they reduce reader effort

`id: ri-editorial-cleanup | category: readability | severity: low | source: book (Ch.32) + editorial | languages: any | tags: naming, organization, clarity, refactoring, code-review`

**Look for in a diff:**
- Names that no longer match behavior or domain terminology
- Misplaced functions/modules that force readers to search for related code
- Comments compensating for unclear structure or stale terminology

**Why it matters:** Small editorial improvements strengthen the code as a communication artifact and make later behavior changes easier to locate and understand.

**Suggested comment:** "This name no longer describes the behavior after the change. Could we update the name/placement so the code remains self-explanatory?"

**Fix:** Rename precisely, move behavior toward its cohesive owner, and remove comments that become unnecessary after the structure is clear.

## Never degrade existing structure without an explicit tradeoff

`id: ri-no-structural-regression | category: maintainability | severity: high | source: book (Ch.32) + editorial | languages: any | tags: structural-regression, technical-debt, refactoring, quality`

**Look for in a diff:**
- Duplication, hidden state, complexity, or coupling added to deliver a small feature
- Existing tests weakened or boundaries bypassed for convenience
- A short-term compromise with no owner, risk, or recovery plan

**Why it matters:** Every structural regression raises the cost of future behavior and makes the system less soft. Accumulated degradation eventually blocks safe change.

**Suggested comment:** "This shortcut adds structural coupling beyond the feature’s behavior. Could we preserve the existing boundary or document a bounded temporary tradeoff?"

**Fix:** Keep the structure at least as healthy as before, or explicitly contain, test, own, and schedule the compromise.
