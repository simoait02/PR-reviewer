# Clean Code, Chapter 18: Simple Design, PR review rules

## Keep high-level policy independent of low-level details

`id: sd-policy-independent-of-details | category: architecture | severity: high | source: book (Ch.18) + editorial | languages: any | tags: policy, details, abstraction, dependency-inversion, boundaries`

**Look for in a diff:**
- Business rules directly constructing SQL, HTTP, UI, filesystem, or framework objects
- Report formatting mixed with the policy that calculates report values
- A change to a low-level detail requiring edits to high-level rules

**Why it matters:** Entangling policy with details makes ordinary changes expensive and spreads infrastructure assumptions through the core. Simple design isolates what changes for different reasons.

**Suggested comment:** "The business rule now depends directly on the transport/database detail. Could the policy depend on an abstraction and keep this detail at the boundary?"

**Fix:** Separate policy from implementation details behind narrow interfaces and point dependencies toward the stable policy.

## Use abstractions to preserve essential policy

`id: sd-abstraction-preserves-policy | category: design | severity: high | source: book (Ch.18) + editorial | languages: any | tags: abstraction, polymorphism, interfaces, policy, details`

**Look for in a diff:**
- An interface that exposes framework or storage details to callers
- A high-level policy branching on every low-level implementation type
- An abstraction that hides essential behavior instead of isolating irrelevant detail

**Why it matters:** A useful abstraction amplifies the stable concept and sequesters volatile mechanics. Poor abstractions merely move coupling or make the contract harder to understand.

**Suggested comment:** "This interface exposes the database representation rather than the policy the caller needs. Could it model the stable operation and keep persistence details behind it?"

**Fix:** Define interfaces at the level of the policy, implement them in detail-oriented adapters, and keep the contract minimal.

## Apply YAGNI using change cost and evidence

`id: sd-yagni-evidence | category: design | severity: medium | source: book (Ch.18) + editorial | languages: any | tags: yagni, overengineering, speculative-design, change-cost, hooks`

**Look for in a diff:**
- Extension hooks, configuration options, or generic frameworks with no current requirement
- Abstractions added solely because a future variation is imaginable
- A speculative feature that adds permanent concepts, tests, and maintenance cost

**Do not flag when:** the extension point addresses a known requirement, a stable volatility boundary, or a demonstrated integration constraint.

**Why it matters:** Unused flexibility has a recurring cost in complexity and cognitive load. With good tests and refactoring, many future changes are cheaper to implement when they become real.

**Suggested comment:** "What current requirement justifies this hook? If the future variation is uncertain, could we defer it until its change pressure is demonstrated?"

**Fix:** Compare the ongoing cost of the abstraction with the cost of adding it later, and implement only evidence-backed flexibility.

## Make changed behavior testable

`id: sd-testable-design | category: testing | severity: high | source: book (Ch.18) + editorial | languages: any | tags: tests, coverage, decoupling, design, refactoring`

**Look for in a diff:**
- New branches or policies with no focused tests
- Code that can be exercised only through a large application or external system
- Hidden dependencies that prevent isolated invocation of the changed behavior

**Why it matters:** Testability is a practical signal of decoupling. A trusted suite enables later refactoring toward simpler boundaries without relying on fear or manual inspection.

**Suggested comment:** "This new policy is reachable only through the full application, so its behavior cannot be isolated or safely refactored. Could the dependency boundary be made testable?"

**Fix:** Add focused behavior tests and introduce seams, injected dependencies, or smaller units where the design prevents reliable testing.

## Treat full coverage as a direction, not a substitute for meaningful tests

`id: sd-coverage-asymptotic-goal | category: testing | severity: high | source: book (Ch.18) + editorial | languages: any | tags: coverage, branches, tests, risk, metrics`

**Look for in a diff:**
- New logic merged with no tests because the project already has a high percentage
- Coverage targets accepted while important branches or failure behavior remain unverified
- Coverage reduced without discussion of the risk or replacement checks

**Do not flag when:** generated, unreachable, or inherently untestable boundary code is explicitly isolated and covered by an appropriate compensating check.

**Why it matters:** Coverage is evidence that code was exercised, not proof that its assertions are correct. Pursuing complete meaningful coverage exposes coupling and prevents unverified behavior from accumulating.

**Suggested comment:** "The coverage percentage remains high, but this new failure branch has no assertion. Could the branch behavior be tested or the intentional gap documented?"

**Fix:** Improve line and branch coverage toward the whole behavior surface, prioritizing meaningful assertions and risk over a vanity number.

## Make code reveal its intent

`id: sd-reveal-intent | category: readability | severity: medium | source: book (Ch.18) + editorial | languages: any | tags: intent, naming, structure, expressive-code, readability`

**Look for in a diff:**
- Generic names, unexplained flags, or nested control flow that hides the business rule
- Code requiring comments to explain what a well-named function or type could state directly
- Several abstraction levels mixed in one method

**Why it matters:** Expressive code reduces the amount a reviewer must infer and makes incorrect behavior easier to spot. Structure, names, and boundaries should communicate the underlying policy.

**Suggested comment:** "The condition encodes a business rule but its name and structure do not reveal it. Could the policy be expressed through a named function or value?"

**Fix:** Choose precise names, extract meaningful decisions, separate abstraction levels, and remove incidental detail from policy code.

## Use tests to document how abstractions are used

`id: sd-tests-express-usage | category: documentation | severity: medium | source: book (Ch.18) + editorial | languages: any | tags: tests, documentation, examples, api, abstraction`

**Look for in a diff:**
- A new abstraction with tests that exercise internals but do not show supported usage
- Public behavior whose valid inputs and outputs are unclear from code and tests
- Examples that are stale or not executable

**Why it matters:** Production code communicates implementation; focused tests communicate context and intended use. Together they form a precise, executable design document.

**Suggested comment:** "The new abstraction has implementation tests but no clear example of how callers should use it. Could a focused behavior test document the supported contract?"

**Fix:** Add readable tests at stable boundaries that demonstrate valid scenarios, outcomes, and important failure behavior.

## Eliminate convergent duplication

`id: sd-remove-convergent-duplication | category: design | severity: medium | source: book (Ch.18) + editorial | languages: any | tags: duplication, abstraction, fragility, refactoring, single-source`

**Look for in a diff:**
- The same business rule, traversal, normalization, or invariant implemented in multiple places
- A change that updates one copy while leaving equivalent logic stale elsewhere
- Duplicated code that will need to change together as the data model evolves

**Why it matters:** Real duplication creates multiple sources of truth and makes coordinated changes easy to miss. Centralizing the shared concept reduces fragility and review burden.

**Suggested comment:** "This traversal/rule now has a second implementation, so future changes can diverge. Could the shared behavior be centralized or parameterized?"

**Fix:** Extract the convergent behavior into one cohesive function, object, strategy, or iterator and pass the contextual differences explicitly.

## Preserve divergent duplication when responsibilities differ

`id: sd-preserve-divergent-duplication | category: design | severity: low | source: book (Ch.18) + editorial | languages: any | tags: duplication, srp, cohesion, abstraction, change-reasons`

**Look for in a diff:**
- A shared helper created only because two snippets look similar today
- A generic abstraction joining code owned by different stakeholders or change schedules
- Callers forced to pass flags or callbacks for unrelated future variations

**Do not flag when:** the duplicated behavior has convergent intent and the abstraction keeps both callers clearer and more stable.

**Why it matters:** Not all textual similarity is a shared concept. Prematurely merging divergent behavior couples unrelated changes and can be harder to maintain than explicit duplication.

**Suggested comment:** "These snippets look similar, but they change for different reasons. Could the duplication remain until a stable shared policy emerges?"

**Fix:** Abstract only behavior with shared intent; otherwise keep the code local and let each responsibility evolve independently.

## Refactor duplication only when tests protect behavior

`id: sd-safe-duplication-refactoring | category: process | severity: medium | source: book (Ch.18) + editorial | languages: any | tags: duplication, refactoring, tests, safety, behavior`

**Look for in a diff:**
- A broad deduplication refactor with weak or missing regression coverage
- A shared abstraction introduced without tests for each caller’s meaningful behavior
- Tests changed to match the new helper without proving behavior stayed equivalent

**Why it matters:** Consolidation changes control flow and ownership across callers. Tests make it possible to distinguish a structural improvement from an accidental behavior change.

**Suggested comment:** "This deduplication changes a shared path used by several callers. Could the existing behaviors be captured before the extraction and verified afterward?"

**Fix:** Add regression coverage, extract incrementally, and retain caller-specific tests in addition to shared helper tests.

## Reduce design size after coverage, intent, and duplication are sound

`id: sd-minimize-design-size | category: design | severity: low | source: book (Ch.18) + editorial | languages: any | tags: simplicity, size, classes, modules, functions, indirection`

**Look for in a diff:**
- Extra modules, wrappers, classes, or configuration layers that add no change boundary
- Small abstractions that increase navigation cost without improving intent or testability
- A large design retained after behavior is covered and responsibilities are clear

**Do not flag when:** the additional element isolates real volatility, improves independent testing, or enforces a meaningful architectural boundary.

**Why it matters:** Small elements reduce cognitive and maintenance cost, but reduction is safe only after behavior, expression, and shared concepts are clear.

**Suggested comment:** "This layer adds indirection without isolating a distinct policy or detail. Could the design stay smaller while preserving the tested boundary?"

**Fix:** Remove unnecessary elements after confirming coverage and intent; keep abstractions that pay for themselves through cohesion or change isolation.

## Apply simple-design rules in priority order

`id: sd-priority-order | category: review-guidance | severity: medium | source: book (Ch.18) + editorial | languages: any | tags: tests, intent, duplication, size, refactoring, tradeoffs`

**Look for in a diff:**
- Size reduction that removes tests or obscures intent
- Deduplication that introduces a generic abstraction before the contract is clear
- Readability improvements pursued without preserving behavior coverage

**Why it matters:** The four rules reinforce a sequence: cover behavior, reveal intent, remove real duplication, then reduce unnecessary size. Optimizing a later rule at the expense of an earlier one makes design less safe.

**Suggested comment:** "This simplification reduces lines but also removes the test/intent signal that makes the behavior understandable. Could we preserve coverage and expression before optimizing size?"

**Fix:** Review changes in order: establish tests, clarify intent, singularize convergent concepts, then reduce elements without losing those protections.
