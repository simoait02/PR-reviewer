# Clean Code, Chapter 21: Continuous Design, PR review rules

## Treat every behavior change as a design change

`id: cd-design-changes-with-behavior | category: process | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: continuous-design, change, architecture, maintenance, behavior`

**Look for in a diff:**
- New behavior added without considering ownership, boundaries, or future change cost
- A feature treated as complete once it works, with no cleanup of the design it altered
- Repeated local patches increasing navigation or modification cost

**Why it matters:** Software design is the current structure of code and configuration, not a one-time planning artifact. Every change either preserves or degrades the system’s ability to support the next behavior.

**Suggested comment:** "This works for the current case, but it adds another responsibility/branch to an already strained boundary. Could we adjust the design now while the change is still localized?"

**Fix:** Review the design impact of each behavior change and make the smallest refactoring needed to keep future changes affordable.

## Decompose user goals into small behavioral slices

`id: cd-slice-behavioral-work | category: process | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: slicing, behavior, requirements, incremental, delivery`

**Look for in a diff:**
- A feature branch combining retrieval, persistence, UI, and policy with no independently testable behavior
- Work items too large to verify or release incrementally
- Technical tasks that cannot be connected to a user-visible behavior

**Why it matters:** Small behavioral slices create faster feedback and reveal design pressure before a large change becomes expensive. They also make it easier to preserve existing behavior.

**Suggested comment:** "This change spans several behaviors and boundaries at once. Could it be split into smaller user-visible slices that can be tested and reviewed independently?"

**Fix:** Break goals into thin vertical behaviors, then implement the smallest technical steps needed to deliver each one.

## Optimize for the four Cs: clarity, conciseness, confirmability, cohesion

`id: cd-four-cs-review | category: design | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: clarity, conciseness, confirmability, cohesion, review`

**Look for in a diff:**
- Code that is short but opaque, clear but unnecessarily repetitive, testable but incohesive, or cohesive but unverified
- A review focusing on one quality dimension while ignoring the tradeoffs among the others
- New behavior that makes future changes harder to find, understand, verify, or isolate

**Why it matters:** Continuous design requires balancing four practical questions: Can readers understand it? Is it needlessly large? Can behavior be verified? Do the elements belong together?

**Suggested comment:** "This improves conciseness but makes the policy harder to understand/test. Could we review the change against clarity, confirmability, and cohesion as well?"

**Fix:** Assess each change across all four Cs and choose the smallest structure that keeps them mutually supportive.

## Make policy-level code easy to find and understand

`id: cd-policy-level-clarity | category: readability | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: clarity, policy, helpers, naming, abstraction-levels`

**Look for in a diff:**
- Multipurpose functions mixing policy with string formatting, parsing, transport, or collection mechanics
- A reviewer needing to trace many low-level statements to understand the main behavior
- Generic helper names that conceal the decision being made

**Why it matters:** The top-level flow should reveal the behavior and delegate incidental detail. Clear policy code reduces navigation time and makes incorrect decisions easier to detect.

**Suggested comment:** "The function mixes the workflow with formatting/parsing details. Could the policy remain at the top level while intention-revealing helpers hide the mechanics?"

**Fix:** Extract cohesive details into named functions/modules and keep the primary function as a readable declaration of policy.

## Edit working code when its design is unclear

`id: cd-edit-for-clarity | category: maintainability | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: refactoring, clarity, cleanup, fear, tests`

**Look for in a diff:**
- A first draft left in place because it already passes tests
- Comments or team folklore required to explain code that could be made self-evident
- Developers avoiding safe cleanup because the code is difficult to touch

**Why it matters:** Code that is hard for teammates to understand is already imposing a maintenance defect. Small verified edits keep the design from becoming progressively more expensive.

**Suggested comment:** "This implementation works but requires substantial decoding. Could we make the intent explicit now, with the existing tests protecting the behavior?"

**Fix:** Refactor names, structure, and boundaries under test protection before moving on to unrelated work.

## Prefer intention-revealing helpers over clever expressions

`id: cd-intention-revealing-helpers | category: readability | severity: low | source: book (Ch.21) + editorial | languages: any | tags: clarity, functions, helpers, idioms, defects`

**Look for in a diff:**
- Dense expressions, nested lambdas, or boundary-prone loops hiding a business concept
- Idiomatic code that still requires careful token-by-token interpretation
- Repeated implementation details that would be clearer behind a named predicate or transformation

**Do not flag when:** the idiom is standard for the project, unambiguous in context, and does not hide a meaningful policy or boundary condition.

**Why it matters:** Names expose intent and reduce the chance that reviewers miss off-by-one, null, ordering, or filtering defects hidden in compact syntax.

**Suggested comment:** "This expression is compact but makes the policy and boundary condition hard to scan. Could a named helper state the intent and make the edge case explicit?"

**Fix:** Extract meaningful predicates/transformations, use precise names, and retain concise idioms only when they remain immediately clear.

## Keep pipelines streamlined and intention-oriented

`id: cd-streamlined-pipelines | category: readability | severity: low | source: book (Ch.21) + editorial | languages: any | tags: pipelines, functional, lambdas, clarity, cohesion`

**Look for in a diff:**
- Long chains with multiple inline lambdas and mixed transformation levels
- A pipeline whose business flow is obscured by sorting, mapping, filtering, and formatting details
- Extracted helpers that belong in another cohesive module

**Why it matters:** Pipelines can express a clear flow, but too much inline detail forces readers to simulate every step. Named operations expose the flow and reveal misplaced responsibilities.

**Suggested comment:** "The pipeline’s main flow is buried under inline details. Could the key operations be named and moved to the module that owns their policy?"

**Fix:** Name meaningful steps, keep the pipeline at one abstraction level, and move domain operations to cohesive owners.

## Balance clarity against conciseness

`id: cd-balance-clarity-conciseness | category: readability | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: clarity, conciseness, cleverness, duplication, tradeoffs`

**Look for in a diff:**
- Code compressed into terse expressions that require rereading
- Verbose helper layers that obscure a simple operation
- Optimization for minimum tokens instead of minimum reader effort

**Why it matters:** The shortest code is not necessarily the simplest. Good design says exactly what it needs with enough context for a reviewer to understand it quickly.

**Suggested comment:** "This is shorter but harder to read than the explicit version. Could we choose the form that minimizes reader effort rather than line count?"

**Fix:** Prefer clear concise code; ask whether a teammate can understand it quickly, and extract or expand only where that improves comprehension.

## Make every intentional behavior confirmable

`id: cd-confirmable-behaviors | category: testing | severity: high | source: book (Ch.21) + editorial | languages: any | tags: confirmability, unit-tests, regression, documentation, behavior`

**Look for in a diff:**
- New decisions, branches, or transformations without direct behavior tests
- Tests that cover only end-to-end success while many unit choices remain unverified
- A change whose correctness depends on manual inspection or tribal knowledge

**Why it matters:** A system contains thousands of small behavioral decisions. Fast focused tests provide living documentation and detect regressions before they become expensive.

**Suggested comment:** "This adds a new decision path without a focused behavior test. Could the intended result be captured so the change is confirmable and documented?"

**Fix:** Add fast isolated tests for meaningful behavior and supplement them with integration, contract, performance, or end-to-end tests where appropriate.

## Design for testability while coding

`id: cd-design-for-confirmability | category: architecture | severity: high | source: book (Ch.21) + editorial | languages: any | tags: testability, dependencies, cohesion, unit-tests, design`

**Look for in a diff:**
- Deep private dependency chains that make test setup large and fragile
- Code requiring full application startup to exercise a small calculation
- Tests added after implementation that need invasive access to internals

**Why it matters:** Testability is easier to preserve during design than to retrofit. Small isolated units expose cohesive behavior and reduce the fear of later refactoring.

**Suggested comment:** "Testing this behavior requires constructing the entire dependency chain. Could the policy be isolated behind injected dependencies so it can be verified directly?"

**Fix:** Keep units cohesive, inject volatile dependencies, expose stable behavior boundaries, and write tests with each new behavior.

## Do not use coverage targets as the design goal

`id: cd-coverage-is-not-the-goal | category: testing | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: coverage, metrics, testing, confirmability, risk`

**Look for in a diff:**
- Trivial assertions added only to satisfy a percentage threshold
- Complex behavior left untested because the target number was reached elsewhere
- Coverage used as proof of correctness without reviewing assertion quality

**Why it matters:** Coverage metrics can encourage superficial tests. The goal is confidence in intended behavior and the ability to change safely, not a particular percentage.

**Suggested comment:** "The metric is satisfied, but this complex behavior still lacks meaningful assertions. Could we prioritize the unverified risk over increasing the percentage?"

**Fix:** Measure coverage as a diagnostic, test all meaningful behavior, and review whether assertions demonstrate the actual contract.

## Keep modules cohesive around one purpose

`id: cd-cohesive-modules | category: design | severity: high | source: book (Ch.21) + editorial | languages: any | tags: cohesion, srp, modules, persistence, policy`

**Look for in a diff:**
- Domain management logic mixed with storage, transport, formatting, or framework code
- A module that must be opened in many places when one implementation detail changes
- Functions that share data but not a coherent purpose

**Why it matters:** Cohesive modules are easier to find, understand, test, and replace. Mixed responsibilities force unrelated changes into the same boundary.

**Suggested comment:** "This module combines definition management with persistence mechanics. Could the storage detail move behind a focused interface so the module retains one purpose?"

**Fix:** Separate policy from infrastructure and group functions that share a change reason, data ownership, and abstraction level.

## Use abstractions to isolate volatile implementation details

`id: cd-isolate-volatile-details | category: architecture | severity: high | source: book (Ch.21) + editorial | languages: any | tags: cohesion, abstraction, persistence, lmm, boundaries`

**Look for in a diff:**
- In-memory, vendor, database, or transport choices leaking into domain APIs
- A future persistence/provider change requiring edits throughout the feature module
- An abstraction that hides the implementation but does not express a stable policy contract

**Why it matters:** Isolating volatility lets the core behavior remain stable while details change. The boundary also improves testability and reduces migration cost.

**Suggested comment:** "The module’s public API exposes the current storage representation, so replacing it will ripple through callers. Could it expose behavior-level operations instead?"

**Fix:** Define a narrow behavior-oriented port, keep volatile implementation behind it, and test the policy independently.

## Revisit design at every development stage

`id: cd-design-at-every-stage | category: process | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: planning, design, slicing, product, estimates`

**Look for in a diff:**
- Planning assumptions carried forward after new requirements expose hidden complexity
- Technical slicing that ignores actual dependency and design constraints
- A feature estimate or implementation plan that does not account for design resistance

**Why it matters:** Design decisions occur during product discovery, slicing, implementation, testing, and cleanup. Revisiting the model prevents early assumptions from becoming expensive surprises.

**Suggested comment:** "The newly clarified requirement changes the design pressure, but the implementation plan still assumes the original boundary. Could the slice and estimate be revisited?"

**Fix:** Re-evaluate design when requirements become concrete, split work into thin slices, and update estimates when the codebase resists the change.

## Refactor after each behavior is verified

`id: cd-refactor-between-behaviors | category: process | severity: medium | source: book (Ch.21) + editorial | languages: any | tags: refactoring, feedback, tdd, clarity, cohesion, conciseness`

**Look for in a diff:**
- Many new behaviors accumulated on top of an unclear first draft
- Tests passing but names, duplication, or boundaries left visibly degraded
- Cleanup postponed until the change is too broad to review safely

**Why it matters:** Short verified cycles make clarity, conciseness, and cohesion affordable. Delayed cleanup increases the cost and risk of improving the design.

**Suggested comment:** "The behavior is covered, but the implementation now contains duplication/mixed concerns that will make the next slice harder. Could we refactor under the passing tests before adding more?"

**Fix:** After each meaningful behavior, run the tests and edit the code for clarity, conciseness, confirmability, and cohesion.
