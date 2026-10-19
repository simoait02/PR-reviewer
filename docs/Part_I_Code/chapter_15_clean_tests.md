# Clean Code, Chapter 15: Clean Tests, PR review rules

## Make each test readable at the behavior level

`id: ct-readable-behavior | category: testing | severity: medium | source: book (Ch.15) + editorial | languages: any | tags: readability, tests, intent, noise, clarity`

**Look for in a diff:**
- Test bodies dominated by framework setup, casts, transport details, or object construction noise
- A reader needing to understand implementation plumbing before finding the behavior under test
- Test names that do not describe the scenario and expected outcome

**Why it matters:** Tests are executable documentation. If their intent is obscured, reviewers miss coverage gaps and future changes are more likely to break or bypass the wrong contract.

**Suggested comment:** "The test’s setup hides the behavior being checked. Could the irrelevant construction details move behind a focused helper so the scenario is obvious?"

**Fix:** Keep test names and bodies centered on the scenario, action, and observable result; hide only irrelevant mechanics.

## Structure tests as Arrange, Act, Assert

`id: ct-arrange-act-assert | category: testing | severity: low | source: book (Ch.15) + editorial | languages: any | tags: aaa, arrange, act, assert, test-structure`

**Look for in a diff:**
- Setup, actions, and assertions interleaved without a clear boundary
- A test with multiple actions or assertions whose relationship is difficult to follow
- Assertions mixed into fixture construction or helper side effects

**Why it matters:** AAA gives readers a predictable path through the test: establish the scenario, perform one operation, then verify its result.

**Suggested comment:** "Could this test separate setup, the operation under test, and verification? The current interleaving makes the actual behavior hard to identify."

**Fix:** Organize the test into Arrange, Act, and Assert sections, using small helpers only when they preserve that structure.

## Build a small domain-specific test language

`id: ct-test-domain-language | category: testing | severity: medium | source: book (Ch.15) + editorial | languages: any | tags: test-api, helpers, abstraction, readability, domain-language`

**Look for in a diff:**
- Repeated low-level setup or protocol calls across many tests
- Test helpers named after implementation mechanics rather than domain behavior
- New tests duplicating transformations that are irrelevant to the assertion

**Why it matters:** A focused test API lets tests express domain intent and reduces the number of details every reader must learn. Repeated test code is evidence that a useful testing vocabulary may be missing.

**Suggested comment:** "These tests repeat the same request/response plumbing. Could a behavior-oriented helper express the scenario and keep protocol details in one place?"

**Fix:** Extract cohesive builders, actions, and assertions with domain names; keep helpers deterministic and transparent about important behavior.

## Use composed assertions for one logical fact

`id: ct-composed-assertions | category: testing | severity: medium | source: book (Ch.15) + editorial | languages: any | tags: assertions, readability, abstraction, diagnostics, logical-fact`

**Look for in a diff:**
- Several low-level assertions repeated to verify one meaningful state or contract
- Assertions that force readers to decode flags, ordering, or protocol representation
- A helper that hides unrelated assertions or produces poor failure diagnostics

**Do not flag when:** separate assertions represent genuinely independent contracts or splitting them would make failures clearer.

**Why it matters:** A composed assertion can state the business-level fact directly and keep the test readable. It must still report enough detail to identify which part failed.

**Suggested comment:** "These assertions jointly describe one controller state. Could a named assertion express that state while retaining a useful failure message?"

**Fix:** Create a focused assertion for one logical fact, with diagnostics that identify the mismatched component.

## Compose complex results into an explicit test representation

`id: ct-composed-test-results | category: testing | severity: low | source: book (Ch.15) + editorial | languages: any | tags: test-results, state, representation, readability, helpers`

**Look for in a diff:**
- Long lists of repetitive state assertions that obscure the expected outcome
- A test comparing raw internal objects when a compact domain state would be clearer
- A custom representation whose encoding is undocumented or ambiguous

**Why it matters:** A deliberate test representation can make repeated state expectations easy to scan and compare. The representation is safe only when its ordering and symbols are obvious to test readers.

**Suggested comment:** "The expected state is spread across many repetitive assertions. Could a named state representation make the contract clearer and document its encoding?"

**Fix:** Introduce a stable composed result or value object with a clear name, ordering, and failure output.

## Keep production efficiency separate from test readability

`id: ct-test-production-tradeoff | category: testing | severity: low | source: book (Ch.15) + editorial | languages: any | tags: test-code, performance, dual-standard, readability, pragmatism`

**Look for in a diff:**
- Production-oriented micro-optimizations making tests cryptic
- Test helpers optimized for memory or CPU at the cost of intent
- A test abstraction criticized solely because it would be unsuitable in production

**Do not flag when:** the test suite’s scale creates a demonstrated performance problem or the helper changes timing/concurrency behavior being tested.

**Why it matters:** Test code has different resource constraints. Readability and diagnostic value should normally take priority, while production performance remains a separate concern.

**Suggested comment:** "This optimization makes the test harder to understand without addressing a measured test bottleneck. Could the simpler expressive form be used here?"

**Fix:** Optimize tests only for a measured suite problem; otherwise choose the clearest representation that preserves the behavior under test.

## Test one action per test

`id: ct-single-act | category: testing | severity: high | source: book (Ch.15) + editorial | languages: any | tags: single-act, isolation, diagnostics, aaa, assertions`

**Look for in a diff:**
- Arrange, act, assert, act, assert sequences in one test
- Multiple production operations whose later assertions depend on earlier side effects
- A test that can pass even when one intermediate action is broken

**Why it matters:** One action per test prevents upstream failures from corrupting downstream assertions and makes each test’s reason for failure clear.

**Do not flag when:** several assertions verify one atomic operation or one logical state transition.

**Suggested comment:** "This test performs two independent actions, so the second assertion may depend on state created by the first. Could the actions be tested separately?"

**Fix:** Arrange one scenario, perform one meaningful action, and assert its result in an independent test.

## Keep tests fast

`id: ct-fast-tests | category: testing | severity: high | source: testing | languages: any | tags: first, fast, feedback, unit-tests, performance`

**Look for in a diff:**
- Unit tests starting processes, making network calls, waiting on real time, or using large unnecessary fixtures
- A helper that turns many focused tests into slow integration tests
- Tests slow enough that developers avoid running them during refactoring

**Why it matters:** Slow tests delay feedback and reduce the frequency with which the suite is run. Fast tests support frequent cleanup and make failures cheaper to investigate.

**Suggested comment:** "This unit test performs real external work and will slow the feedback loop. Could that dependency be replaced with a controlled fake, leaving one integration test for the boundary?"

**Fix:** Keep unit tests local and deterministic, and move required external verification to a small separately identified integration layer.

## Isolate tests from one another

`id: ct-isolated-tests | category: testing | severity: high | source: testing | languages: any | tags: first, isolated, shared-state, order-dependence, diagnostics`

**Look for in a diff:**
- Tests sharing mutable fixtures, database rows, filesystem paths, or global configuration
- A test that relies on another test having run first
- Cleanup performed only by a later test or suite-level teardown

**Why it matters:** Isolated tests can run in any order and fail at the actual defect. Shared state creates cascades of misleading failures and hides independent defects.

**Suggested comment:** "This test depends on state created by another test. Could it create and clean up its own fixture so it remains independently runnable?"

**Fix:** Create test state locally, reset global resources, and make each test safe to run alone and in a randomized order.

## Make tests repeatable in constrained environments

`id: ct-repeatable-tests | category: testing | severity: high | source: testing | languages: any | tags: first, repeatable, environment, network, time, randomness`

**Look for in a diff:**
- Dependence on a developer machine, current time zone, locale, network, filesystem layout, or random seed
- Tests that pass locally but require an unavailable service in CI
- Uncontrolled nondeterminism masked by retries

**Why it matters:** A test that cannot run reliably in different environments becomes an excuse rather than evidence. Repeatability is required for trustworthy regression detection.

**Suggested comment:** "This test depends on local environment state. Could the clock, locale, seed, or external dependency be controlled so it produces the same result in CI and locally?"

**Fix:** Inject environment-sensitive dependencies, control seeds and clocks, and make required external resources explicit and reproducible.

## Make tests self-validating

`id: ct-self-validating-tests | category: testing | severity: high | source: testing | languages: any | tags: first, self-validating, assertions, automation, ci`

**Look for in a diff:**
- Tests that require reading logs or manually comparing output files to decide pass/fail
- Assertions replaced with print statements or snapshots with no failure criteria
- A human reviewer required to interpret every test result

**Why it matters:** Automated tests must produce an unambiguous pass/fail result. Subjective or manual evaluation cannot reliably gate changes or provide repeatable regression evidence.

**Suggested comment:** "This test produces output but does not fail when the behavior is wrong. Could it assert the relevant invariant or use an explicit approval/evaluation check?"

**Fix:** Encode acceptance criteria as assertions, structured comparisons, tolerances, or a documented evaluator that returns a clear result.

## Write tests in a timely fashion

`id: ct-timely-tests | category: testing | severity: medium | source: testing | languages: any | tags: first, timely, testability, design, regression`

**Look for in a diff:**
- Production code merged with no test and a promise to test later
- Tests added long after implementation that omit difficult paths
- A design made hard to exercise because dependencies were fixed internally

**Why it matters:** Writing tests with production code exposes testability problems while the design is still cheap to change. Delayed tests often cement a coupled design and leave behavior unprotected.

**Suggested comment:** "The new code is difficult to exercise because its dependencies are constructed internally. Could the test be added now and the dependency boundary made explicit?"

**Fix:** Add tests with the feature and introduce seams or dependency injection when the test reveals excessive coupling.

## Keep test helpers less coupled than production details

`id: ct-minimize-test-coupling | category: testing | severity: high | source: book (Ch.15) + editorial | languages: any | tags: test-design, coupling, refactoring, maintainability, fixtures`

**Look for in a diff:**
- One production signature change requiring edits to many unrelated tests
- Fixtures that construct the entire object graph for every assertion
- Helpers exposing internal data structures or leaking framework details into every test

**Why it matters:** Test suites should change with requirements, not with every implementation detail. Excessive coupling makes valid refactoring expensive and causes tests to be weakened or deleted.

**Suggested comment:** "This internal signature change requires broad test rewrites. Could a focused fixture or public behavior helper reduce coupling while preserving the contract being tested?"

**Fix:** Centralize stable setup, test through public behavior, and keep helpers narrow so implementation changes affect only relevant tests.

## Preserve diagnostic quality when abstracting tests

`id: ct-preserve-test-diagnostics | category: testing | severity: medium | source: book (Ch.15) + editorial | languages: any | tags: assertions, helpers, diagnostics, failures, readability`

**Look for in a diff:**
- Generic helpers whose failure message omits the expected scenario or mismatched value
- Deep helper stacks that make it hard to locate the failing assertion
- A composed assertion that hides multiple unrelated contracts

**Why it matters:** Readable tests are useful only when failures explain what broke. Abstraction that removes diagnostics increases repair time and encourages rerunning or debugging blindly.

**Suggested comment:** "This helper improves reuse but its failure output loses the scenario and actual value. Could it include actionable diagnostics or remain closer to the test?"

**Fix:** Include scenario, expected, and actual values in failures; keep abstractions aligned with one logical behavior.

## Keep the test suite clean as behavior evolves

`id: ct-maintain-test-cleanliness | category: maintainability | severity: high | source: book (Ch.15) + editorial | languages: any | tags: clean-tests, refactoring, maintainability, readability, design`

**Look for in a diff:**
- New duplication, unclear names, oversized fixtures, or dead tests
- Tests disabled instead of updated after a production refactor
- A suite whose structure makes adding the next case harder than changing production code

**Why it matters:** Tests preserve flexibility only while they remain understandable and changeable. A suite that rots becomes a liability and eventually stops protecting production code.

**Suggested comment:** "This change leaves the test suite harder to read and extend. Could the new cases be refactored now so the tests remain a useful safety net?"

**Fix:** Refactor tests continuously, remove obsolete cases, improve names and helpers, and preserve clear behavior coverage.
