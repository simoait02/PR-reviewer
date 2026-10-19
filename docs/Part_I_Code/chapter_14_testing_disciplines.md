# Clean Code, Chapter 14: Testing Disciplines, PR review rules

## Test behavior before or alongside production code

`id: td-test-before-or-alongside-code | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: tests, tdd, regression, behavior, requirements`

**Look for in a diff:**
- New production behavior with no automated test or explicit test plan
- Tests added only after implementation and missing the behavior that drove the change
- A test suite that verifies the happy path but not the new failure or boundary behavior

**Do not flag when:** the change is configuration-only, generated code is covered by its generator, or the repository has a documented higher-level test that is the correct contract.

**Why it matters:** A failing test makes the required behavior concrete before implementation choices hide it. Tests written with the change provide executable evidence that the code satisfies its contract.

**Suggested comment:** "This adds new behavior without a test that demonstrates the expected contract. Could you add the smallest focused test for the new success and failure behavior?"

**Fix:** Write a failing behavior test first or alongside the implementation, then keep it as a regression test.

## Keep the test-production feedback loop small

`id: td-small-feedback-loop | category: testing | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: tdd, feedback, incremental, debugging, scope`

**Look for in a diff:**
- A large implementation and a large batch of tests reviewed as one inseparable change
- Several unrelated behaviors added before any test feedback is obtained
- A failure that cannot be localized because the change spans many responsibilities

**Why it matters:** Small cycles reveal incorrect assumptions early and make failures easy to diagnose. A short path from change to feedback reduces the cost of correction.

**Suggested comment:** "This change combines several behaviors before the tests provide feedback. Could it be split into smaller behavior-preserving steps?"

**Fix:** Implement one observable behavior at a time and run the narrowest relevant tests after each meaningful step.

## Make the test discipline explicit without enforcing one ritual

`id: td-discipline-is-explicit | category: process | severity: low | source: book (Ch.14) + editorial | languages: any | tags: tdd, tcr, small-bundles, workflow, pragmatism`

**Look for in a diff:**
- A team convention that requires TDD, TCR, or small bundles but is applied inconsistently
- Tests and implementation merged in a large opaque batch with no evidence of incremental verification
- A review rejecting a sound test because it was not written in a prescribed order

**Do not flag when:** the project uses a documented discipline appropriate to its environment and the resulting tests are focused, meaningful, and passing.

**Why it matters:** TDD, test-and-commit-or-revert, and small tested bundles are different ways to obtain rapid feedback. The review target is reliable feedback and coverage of behavior, not a ceremonial sequence.

**Suggested comment:** "The workflow is not the issue by itself; what evidence shows that this bundle was tested and that its edge cases are covered?"

**Fix:** Follow the team’s chosen discipline, keep increments reviewable, and document exceptions when the normal cycle is impractical.

## Keep tests focused on observable behavior

`id: td-test-behavior-not-implementation | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: unit-tests, behavior, coupling, refactoring, public-contract`

**Look for in a diff:**
- Assertions on private fields, call order, or incidental helper methods
- Tests that must change whenever an internal implementation is refactored without changing behavior
- Mocks verifying implementation details instead of the result visible to a caller

**Why it matters:** Behavior-focused tests protect the contract while allowing implementation improvements. Tests coupled to structure become a barrier to clean design and can pass while the real behavior is wrong.

**Suggested comment:** "This assertion locks the test to an internal call sequence. Can it verify the observable result or externally meaningful interaction instead?"

**Fix:** Test through stable interfaces and assert outcomes, externally meaningful side effects, and documented boundary interactions.

## Cover branches and failure paths in each small bundle

`id: td-cover-branches-and-failures | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: coverage, branches, errors, edge-cases, tests`

**Look for in a diff:**
- New conditionals with tests for only one branch
- Error handling, retries, timeouts, empty inputs, or permission failures left untested
- A claimed high coverage percentage hiding untested decision paths

**Why it matters:** A passing happy-path test does not establish that the new behavior is safe. Branch and failure tests expose the cases most likely to produce regressions in production.

**Suggested comment:** "The new branch handles an important failure case, but the test suite covers only success. Could you add a test for the failure and boundary inputs?"

**Fix:** Add focused tests for each meaningful decision path, including invalid input and dependency failure behavior.

## Keep tests fast and repeatable

`id: td-fast-repeatable-tests | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: test-speed, determinism, feedback, isolation, flakiness`

**Look for in a diff:**
- Tests that depend on real time, sleeps, thread scheduling, random values, or network availability
- Shared mutable state or order-dependent tests
- A test suite too slow or flaky to run after each small change

**Why it matters:** A testing discipline only works when developers trust and run it frequently. Slow or nondeterministic tests delay feedback and eventually get ignored.

**Suggested comment:** "This test depends on wall-clock timing or network state and may be nondeterministic. Could the dependency be controlled or isolated so the test gives fast repeatable feedback?"

**Fix:** Inject clocks and randomness, control scheduling, isolate state, and reserve real external integration for a small explicit test layer.

## Isolate operating-system and external boundaries

`id: td-isolate-external-boundaries | category: architecture | severity: high | source: book (Ch.14) + editorial | languages: any | tags: os, io, network, framework, testability, dependency-injection`

**Look for in a diff:**
- Domain logic directly coupled to files, sockets, threads, GUI APIs, databases, or framework callbacks
- Production code that cannot be exercised without starting external infrastructure
- Test doubles added after the fact but no boundary abstraction exists

**Why it matters:** External boundaries are expensive and often impractical to test exhaustively. Isolating them keeps most intelligence in deterministic code that can be verified quickly.

**Suggested comment:** "This class combines the business rule with the socket/framework boundary, which makes the rule hard to test. Could the boundary be isolated behind a small adapter?"

**Fix:** Move decision-making into a testable component and keep adapters thin; inject the boundary dependency where appropriate.

## Keep untestable boundary code thin

`id: td-humble-boundary | category: architecture | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: humble-object, gui, io, adapters, integration-tests`

**Look for in a diff:**
- Large amounts of business logic inside GUI, framework, transport, or hardware callbacks
- A boundary component that transforms data, applies policy, and performs I/O in one method
- Broad code marked "not testable" without a design effort to reduce it

**Do not flag when:** a genuinely visual or hardware-specific assertion requires a boundary test and the surrounding logic remains small and protected by contract tests.

**Why it matters:** Some final effects are difficult or subjective to automate. Keeping the boundary simple limits the unverified surface and makes the rest of the system safe to refactor.

**Suggested comment:** "The callback contains policy as well as rendering or I/O. Could the policy move behind a testable interface and leave this boundary as a thin adapter?"

**Fix:** Extract computation and decisions from the boundary; test the adapter with a small number of integration or approval tests.

## Protect testable code from untestable frameworks

`id: td-framework-isolation | category: architecture | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: framework, adapter, coupling, integration, testability`

**Look for in a diff:**
- Framework types spreading through domain and application layers
- Business rules requiring framework bootstrapping or complex callback graphs in unit tests
- A new dependency chosen without a strategy for testing code that uses it

**Why it matters:** A framework can make large parts of an application difficult to verify. An isolation layer preserves testability and limits the cost of replacing or upgrading the framework.

**Suggested comment:** "The framework API now reaches the core policy, making unit tests depend on framework setup. Could an adapter keep the framework at the boundary?"

**Fix:** Define a narrow application-facing interface, implement it at the framework boundary, and test the core against a deterministic fake.

## Do not confuse TDD with architectural design

`id: td-tdd-does-not-prove-architecture | category: design | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: tdd, architecture, design, dependencies, boundaries`

**Look for in a diff:**
- A claim that passing unit tests proves module boundaries or system architecture are sound
- Tests that validate local behavior while dependencies point in the wrong direction
- A design decision justified only by the existence of tests

**Why it matters:** Testing disciplines improve tactical feedback and can encourage decoupling, but they do not automatically detect poor architecture, misplaced responsibilities, or harmful dependency direction.

**Suggested comment:** "The unit tests pass, but they do not verify the dependency boundary introduced here. Could the architectural constraint be reviewed or tested separately?"

**Fix:** Combine fast unit tests with explicit boundary, integration, contract, and architecture checks where those risks matter.

## Use tests as executable low-level documentation

`id: td-tests-document-contracts | category: documentation | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: tests, documentation, examples, api, contract`

**Look for in a diff:**
- Public behavior with no clear example of construction, invocation, or expected result
- Tests that are too broad or repetitive to explain one behavior
- Documentation examples that can drift from the implementation

**Why it matters:** Small isolated tests show how an API is used and keep examples executable. They document low-level behavior more precisely than prose that is not run.

**Suggested comment:** "This public behavior has no focused usage example. Could a small test demonstrate the supported inputs and result?"

**Fix:** Give each important contract a readable, isolated test that fails clearly when the contract changes.

## Treat missing coverage as an explicit risk

`id: td-explicit-test-gaps | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: coverage, risk, manual-testing, confidence, release`

**Look for in a diff:**
- Tests omitted because the code is difficult to exercise
- A passing suite used as release evidence despite known untested paths
- Manual verification described as a substitute for repeatable regression coverage

**Do not flag when:** the uncovered behavior is documented as a deliberate boundary limitation and a compensating integration, manual, or monitoring check exists.

**Why it matters:** A green suite is only as trustworthy as the behavior it covers. Unacknowledged holes create false confidence and make safe release or refactoring decisions difficult.

**Suggested comment:** "This path is currently untested, so the green suite does not cover the new risk. Could you add a test or document the gap with a compensating check?"

**Fix:** Make the code testable where practical; otherwise isolate the gap, document it, and add the strongest feasible verification.

## Keep test code as clean as production code

`id: td-keep-tests-clean | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: test-maintainability, readability, duplication, design, refactoring`

**Look for in a diff:**
- Poor names, duplicated setup, giant fixtures, hidden shared state, or tangled assertions in tests
- Tests that are difficult to modify when production behavior changes
- A test suite treated as disposable because it currently passes

**Why it matters:** Tests evolve with production code. Dirty tests become a maintenance liability, are eventually bypassed or deleted, and remove the safety net needed to improve the system.

**Suggested comment:** "This test setup is duplicated and difficult to change. Could the fixture and assertions be simplified while keeping each test’s behavior obvious?"

**Fix:** Apply the same naming, cohesion, duplication, and design standards to tests; keep setup local and intentions visible.

## Prefer independent tests with one clear reason to fail

`id: td-independent-single-purpose-tests | category: testing | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: isolation, test-design, diagnostics, fixtures, assertions`

**Look for in a diff:**
- Tests whose outcome depends on another test’s execution or shared ordering
- One test covering many unrelated behaviors with many reasons to fail
- Failures that require reading a large fixture or reproducing an entire scenario

**Why it matters:** Independent focused tests provide precise documentation and make failures actionable. They also allow the suite to run selectively while preserving confidence.

**Suggested comment:** "This test covers several unrelated outcomes, so a failure will not identify the broken contract. Could the behaviors be split into focused independent tests?"

**Fix:** Give each test a clear scenario and outcome, isolate state, and use small reusable helpers without hiding the behavior under test.

## Use a passing test suite to enable safe change

`id: td-tests-enable-change | category: maintainability | severity: medium | source: book (Ch.14) + editorial | languages: any | tags: refactoring, regression, confidence, maintainability, clean-code`

**Look for in a diff:**
- Refactoring or cleanup that removes tests without preserving equivalent behavior coverage
- Tests disabled or weakened to make a change pass
- A production change that leaves the suite unable to detect regressions in the touched area

**Why it matters:** Reliable tests reduce the fear and cost of refactoring. They are not overhead separate from clean code; they are the feedback mechanism that lets the design improve safely.

**Suggested comment:** "This change removes the regression check that protects the refactor. Could the test be updated to the new interface while preserving the behavior it verifies?"

**Fix:** Preserve meaningful coverage during refactors, strengthen weak tests, and remove tests only when their contract is intentionally removed.

## Evaluate AI and subjective outputs with suitable checks

`id: td-evaluate-subjective-and-ai-output | category: testing | severity: high | source: book (Ch.14) + editorial | languages: any | tags: ai, evaluation, subjective-output, golden-tests, human-review, quality`

**Look for in a diff:**
- AI-generated output accepted without measurable requirements or representative cases
- Visual, ranking, wording, or formatting behavior tested only with brittle exact strings
- A claim that an output is correct without an evaluation or review method

**Do not flag when:** the project has an appropriate combination of invariants, representative evaluations, tolerances, golden samples, and human review for the output.

**Why it matters:** Some outputs are subjective or probabilistic and cannot be validated by a single exact assertion. They still need explicit quality criteria and a repeatable way to detect regressions.

**Suggested comment:** "This output is judged as correct without a defined evaluation. Could you add representative cases and the invariants or review criteria that determine acceptable results?"

**Fix:** Define measurable constraints, use tolerant or rubric-based evaluations where exact equality is inappropriate, and keep human review for genuinely subjective decisions.
