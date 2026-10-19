# Clean Code, Chapter 26: Clean Boundaries, PR review rules

## Encapsulate third-party dependencies behind adapters

`id: cb-wrap-third-party-dependencies | category: architecture | severity: critical | source: book (Ch.26) + editorial | languages: any | tags: third-party, adapters, vendor, boundary, coupling`

**Look for in a diff:**
- Vendor/framework types imported throughout application and policy code
- Many direct references to a third-party API with no controlled integration layer
- Business logic shaped around the vendor’s broad interface

**Why it matters:** Third-party APIs change outside the team’s control. A small adapter limits the blast radius, gives the application a consistent contract, and keeps replacement practical.

**Suggested comment:** "The vendor API is now referenced from multiple application modules. Could a focused adapter expose only the operations the application needs?"

**Fix:** Wrap the dependency, translate at the boundary, and keep internal code dependent on an application-owned interface.

## Depend on the smallest vendor surface required

`id: cb-minimal-third-party-surface | category: architecture | severity: medium | source: book (Ch.26) + editorial | languages: any | tags: third-party, interface, api, coupling, change-surface`

**Look for in a diff:**
- A wrapper exposing the vendor’s entire API instead of a few required operations
- Application code depending on vendor features it does not need
- Vendor-specific configuration and lifecycle concepts leaking through the wrapper

**Why it matters:** Broad dependencies increase upgrade, failure, and migration cost. A minimal application-centered surface is easier to test and replace.

**Suggested comment:** "This boundary mirrors the entire vendor API, so internal code remains coupled to details. Could the adapter expose only the application’s required operations?"

**Fix:** Define a narrow port around application needs and keep unused vendor capabilities out of the core contract.

## Keep vendor adapters low-complexity

`id: cb-low-complexity-adapter | category: architecture | severity: high | source: book (Ch.26) + editorial | languages: any | tags: adapter, vendor, translation, complexity, policy`

**Look for in a diff:**
- Business rules, validation, or reporting logic inside a vendor adapter
- An adapter becoming a second application service with unrelated responsibilities
- A vendor callback handling domain decisions instead of forwarding normalized data

**Why it matters:** Boundary code should translate and coordinate, not become the owner of policy. Keeping it simple makes vendor replacement and integration testing safer.

**Suggested comment:** "This adapter now applies domain policy in addition to translating vendor messages. Could the policy move inward and leave the adapter responsible for integration mechanics?"

**Fix:** Keep adapters thin, normalize external data at the edge, and delegate business decisions to testable core components.

## Inject external boundary dependencies

`id: cb-injected-boundary-dependencies | category: design | severity: high | source: book (Ch.26) + editorial | languages: any | tags: dependency-injection, boundaries, testability, fakes, composition`

**Look for in a diff:**
- Core code constructing vendor clients, queues, processes, or network connections internally
- Tests requiring real infrastructure because the boundary cannot be replaced
- Global singletons hiding external dependencies

**Why it matters:** Injection makes ownership explicit and creates a seam for deterministic tests, alternate vendors, and controlled failure scenarios.

**Suggested comment:** "The application constructs the external client internally, preventing a fake from being used in tests. Could it receive the boundary dependency from the composition root?"

**Fix:** Define an application-owned contract, inject its implementation, and construct concrete dependencies only at the outer composition boundary.

## Isolate asynchronous and process communication

`id: cb-isolate-process-communication | category: concurrency | severity: high | source: book (Ch.26) + editorial | languages: any | tags: queues, processes, async, communication, boundaries`

**Look for in a diff:**
- UI/business code directly managing process/thread synchronization
- Queue semantics scattered across producers and consumers
- Commands, replies, timeouts, and shutdown signals with no single ownership boundary

**Why it matters:** Queues can cleanly separate execution contexts, but only when message contracts and lifecycle semantics are explicit. Isolating them keeps concurrency from infecting policy code.

**Suggested comment:** "Queue and process coordination is spread across the UI and policy layers. Could a focused boundary own message contracts, timeouts, and shutdown behavior?"

**Fix:** Define typed command/reply contracts, isolate queue mechanics, and keep business logic unaware of process/thread implementation.

## Bind concrete objects in one composition root

`id: cb-composition-root | category: architecture | severity: high | source: book (Ch.26) + editorial | languages: any | tags: composition-root, object-creation, startup, wiring, dependency-injection`

**Look for in a diff:**
- Concrete object creation scattered through core modules
- Startup code that wires components in multiple places with inconsistent configuration
- Policy code responsible for process startup, server creation, or vendor selection

**Why it matters:** A composition root makes object creation and dependency direction visible. It keeps use and construction separate and makes deployment configuration auditable.

**Suggested comment:** "Concrete adapters are created in several application modules, making wiring and replacement difficult to audit. Could startup bind all dependencies in one composition root?"

**Fix:** Centralize construction and binding, pass interfaces inward, and keep runtime configuration at the edge.

## Use learning tests for unfamiliar APIs

`id: cb-learning-tests | category: testing | severity: medium | source: book (Ch.26) + editorial | languages: any | tags: learning-tests, third-party, api, experiments, documentation`

**Look for in a diff:**
- A new framework/queue/vendor integrated from examples with no verified assumptions
- Team code relying on undocumented timeout, ordering, capacity, or error behavior
- An upgrade made without tests that describe the dependency behavior the application requires

**Why it matters:** Learning tests turn uncertainty about an external API into executable knowledge. They expose incompatible upgrades early and document the assumptions behind the adapter.

**Suggested comment:** "This integration relies on the dependency’s timeout/ordering behavior, but that assumption is unverified. Could a focused learning test pin down the API behavior we require?"

**Fix:** Write small experiments for relevant success, failure, capacity, timing, and lifecycle behavior; keep them runnable during dependency upgrades.

## Keep learning tests separate from application contracts

`id: cb-separate-learning-and-contract-tests | category: testing | severity: medium | source: book (Ch.26) + editorial | languages: any | tags: learning-tests, contract-tests, third-party, adapter, tests`

**Look for in a diff:**
- A test proving only that the vendor behaves as documented, not that the adapter fulfills application needs
- Application tests coupled directly to vendor implementation details
- Learning experiments treated as the sole regression suite for business behavior

**Why it matters:** Learning tests protect knowledge of the dependency; adapter contract tests protect the application’s boundary. They answer different questions and should not be conflated.

**Suggested comment:** "This test confirms the vendor call but not the application-facing contract. Could the adapter’s normalized behavior be tested separately from the dependency learning test?"

**Fix:** Maintain vendor learning tests, adapter contract tests, and core behavior tests as distinct layers.

## Design an application-owned interface for code not yet available

`id: cb-interface-for-unknown-system | category: architecture | severity: high | source: book (Ch.26) + editorial | languages: any | tags: unknown-dependency, interface, adapter, future-system, testability`

**Look for in a diff:**
- Work blocked on an undefined hardware, service, or subsystem API
- Client code shaped around guesses about the future dependency
- A placeholder with no application-level contract or replacement seam

**Why it matters:** The application can continue against an interface defined by its own needs. Once the real API exists, one adapter can absorb the mismatch and future changes.

**Suggested comment:** "The unknown subsystem is forcing client code to wait for or guess its API. Could we define the application-owned capability we need and add an adapter later?"

**Fix:** Define a minimal port from the client’s perspective, use a fake/stub during development, and implement one adapter when the external API is known.

## Keep fake boundary implementations behaviorally useful

`id: cb-useful-boundary-fakes | category: testing | severity: medium | source: book (Ch.26) + editorial | languages: any | tags: fakes, test-doubles, boundaries, simulation, contract`

**Look for in a diff:**
- A fake that always succeeds and cannot simulate timeout, invalid data, capacity, or ordering behavior
- Tests passing only because the fake is unrealistically simpler than production
- Fake behavior diverging from the application-owned contract

**Why it matters:** Fakes enable fast core tests only when they model the boundary behaviors that matter. Unrealistic doubles hide integration and error-handling defects.

**Suggested comment:** "This fake cannot represent the timeout/invalid reply that production must handle. Could it model the contract’s relevant failure modes without reproducing the entire vendor?"

**Fix:** Keep fakes small but contract-faithful, and cover their assumptions with adapter/contract tests.

## Limit references to outside-controlled code

`id: cb-limit-external-references | category: maintainability | severity: high | source: book (Ch.26) + editorial | languages: any | tags: third-party, references, coupling, migration, maintenance`

**Look for in a diff:**
- Vendor classes, constants, exceptions, and data structures appearing throughout the codebase
- Multiple modules implementing slightly different translations of one vendor concept
- A migration requiring a repository-wide search and rewrite of external API usage

**Why it matters:** Each direct reference is a maintenance point and a path for external changes to leak inward. Centralizing usage makes upgrades and replacement manageable.

**Suggested comment:** "The vendor type is spreading beyond the adapter, so migration will touch many modules. Could the external reference be translated once at the boundary?"

**Fix:** Restrict external references to adapters/composition code and expose stable internal types to the rest of the application.

## Test boundary expectations and failure behavior

`id: cb-boundary-contract-and-failure-tests | category: testing | severity: high | source: book (Ch.26) + editorial | languages: any | tags: boundaries, contract-tests, failures, integration, compatibility`

**Look for in a diff:**
- A new adapter with only a happy-path integration test
- Missing behavior for malformed replies, timeouts, disconnects, retries, or version mismatches
- Boundary changes merged without compatibility evidence

**Why it matters:** Most integration risk lives at the boundary, where external assumptions and failure modes meet. Explicit contract tests protect both application behavior and migration safety.

**Suggested comment:** "The adapter handles success but not timeout/version-invalid responses. Could boundary tests define the expected failure and recovery behavior?"

**Fix:** Test normalized success, malformed input, unavailable dependencies, timeouts, retries, cancellation, and compatibility requirements.
