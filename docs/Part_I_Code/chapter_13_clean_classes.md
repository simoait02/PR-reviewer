# Clean Code, Chapter 13: Clean Classes, PR review rules

## Keep one primary class or module per source file

`id: cl-one-class-per-file | category: organization | severity: low | source: book (Ch.13) + editorial | languages: any | tags: class, module, file, namespace, organization, cohesion`

**Look for in a diff:**
- Unrelated classes added to an already crowded file
- A file whose name does not identify its primary class or module
- Classes that are only co-located because they happened to be edited together

**Do not flag when:** small records, exceptions, or tightly coupled private helpers clearly belong with the primary type.

**Why it matters:** A predictable file boundary helps developers find code and understand ownership. The important rule is conceptual cohesion, not a rigid file-count rule.

**Suggested comment:** "These classes have separate responsibilities and callers. Could they live in separate files so each module has a clear home?"

**Fix:** Keep one primary cohesive class or module per file and colocate only genuinely related support types.

## Keep classes small and focused

`id: cl-small-focused-classes | category: design | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: class-size, cohesion, monolith, god-class, redundancy, complexity`

**Look for in a diff:**
- A class accumulating unrelated methods or state
- A class that is difficult to name without joining responsibilities with "and"
- New behavior added to a class already responsible for several policies
- A class whose growth increases test setup and defect risk

**Why it matters:** Small cohesive classes are easier to locate, reuse, test, and change. Large classes hide multiple reasons to change and make unrelated modifications interfere with one another.

**Suggested comment:** "This class now owns checkout, fine calculation, and reporting. Could those policies be separated so each class has one reason to change?"

**Fix:** Split by responsibility and keep each resulting class focused on one related set of behaviors.

## Judge class design by its change reasons

`id: cl-change-reasons | category: design | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: srp, reasons-to-change, policy, cohesion, changeability, design-quality`

**Look for in a diff:**
- One class changing for different stakeholders or policies
- A feature change requiring edits to unrelated behavior in the same class
- A class whose public API contains several independent concerns

**Why it matters:** A class is cohesive when its methods are closely related and it has one primary reason to change. Changeability is a better design test than size alone.

**Suggested comment:** "These rules change for different reasons, so one policy change could affect the other. Could each responsibility have its own owner?"

**Fix:** Identify independent policies and move them into focused classes or strategies.

## Use heuristics as review signals, not absolute laws

`id: cl-heuristics-not-laws | category: review-guidance | severity: low | source: book (Ch.13) + editorial | languages: any | tags: heuristics, solid, code-smells, simple-design, balance, pragmatism`

**Look for in a diff:**
- A principle applied without considering the change pressure or local design
- Tiny classes created only to satisfy a rule
- Copy-paste logic introduced instead of a justified abstraction
- A review that treats SOLID or a code smell as an automatic defect

**Why it matters:** Design heuristics point toward useful structure but can conflict. Small, testable, named elements are valuable, yet minimizing elements and avoiding needless indirection matter too.

**Suggested comment:** "This split follows the principle, but what maintenance problem does it solve here? If the responsibilities change together, one cohesive class may be clearer."

**Fix:** State the concrete change or risk the design addresses and choose the smallest structure that solves it.

## Separate orchestration from policy implementation

`id: cl-orchestration-vs-policy | category: design | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: service-class, orchestration, policy, implementation, delegation, srp`

**Look for in a diff:**
- A service that coordinates operations while also implementing every domain rule
- Persistence, external calls, validation, and business policy mixed in one class
- A facade that becomes the owner of unrelated calculations

**Why it matters:** Orchestration and implementation change for different reasons. Mixing them makes the service harder to understand, test, and modify.

**Suggested comment:** "This service both declares the workflow and implements the fine policy. Could it delegate the policy to a focused class and remain an orchestrator?"

**Fix:** Keep orchestration in the service and delegate domain or utility policies to cohesive collaborators.

## Extract complex policy decisions into named predicates

`id: cl-extract-policy-predicates | category: readability | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: predicate, conditional, feature-envy, policy, comments, extraction`

**Look for in a diff:**
- A complex conditional embedded in a long workflow
- A comment explaining what an `if` condition means
- A predicate that asks another object several questions to calculate a result
- A method that is easier to understand after naming one decision

**Why it matters:** A meaningful predicate exposes policy in the calling code and removes implementation detail. It also provides a clear place for future policy changes.

**Suggested comment:** "Could this condition become `holding.is_late()`? The name would state the policy without making readers decode the date comparison."

**Fix:** Extract the decision into a named method and move it to the object that owns the relevant data and rules.

## Move behavior toward the data it uses

`id: cl-move-feature-envy | category: design | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: feature-envy, cohesion, move-method, data-owner, encapsulation, responsibility`

**Look for in a diff:**
- A method that asks another object several questions before calculating a result
- A service that knows details of a domain object’s state
- Business rules located in a class that merely coordinates or formats

**Why it matters:** Feature envy indicates that behavior may belong with the object whose data and invariants it uses. Moving it reduces knowledge in the caller and keeps the rule near its owner.

**Suggested comment:** "This method reads several `Holding` values to calculate the fine. Could `Holding` or its material policy own that calculation?"

**Fix:** Move the method to the data owner, or introduce a focused policy object when the rule has an independent reason to change.

## Close classes against the changes you expect

`id: cl-open-closed-policy | category: design | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: ocp, closed-class, strategy, extension, open-implementation, volatility`

**Look for in a diff:**
- A class that must be edited whenever a new policy variant appears
- A switch or conditional containing rules for many material or product types
- New behavior added by opening stable classes instead of adding a focused implementation

**Why it matters:** Open classes increase the risk and cost of changes. A strategy or policy abstraction can let new behavior be added without repeatedly modifying the class that coordinates it.

**Do not flag when:** the change is isolated, the set of variants is stable, or the abstraction would be speculative.

**Suggested comment:** "Each new fine scheme requires editing this class. Could the policy be represented by a strategy so new schemes extend the design?"

**Fix:** Extract stable interfaces and focused strategies when the variation is real and recurring.

## Refactor toward the next real change, not every possible change

`id: cl-prefactor-for-real-change | category: process | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: prefactoring, refactoring, change-pressure, speculative-design, strategy, ocp`

**Look for in a diff:**
- A large abstraction added only because a future change is imaginable
- A confirmed new policy being added directly to a tangled switch
- Refactoring that does not reduce the cost or risk of the current requirement

**Why it matters:** Speculative cleanup adds risk without a concrete benefit. When a real new variant arrives, small prefactoring can create a safe extension point before adding the behavior.

**Suggested comment:** "The new policy is confirmed, so this is a good point to isolate the existing branches. Could we keep the refactor focused on this change rather than building a general framework?"

**Fix:** Refactor enough to isolate the current axis of change and defer unsupported generality.

## Keep service classes focused on policy or implementation

`id: cl-service-single-purpose | category: architecture | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: service, policy, implementation, orchestration, boundaries, srp`

**Look for in a diff:**
- A service that mixes workflow policy with low-level domain details
- A service that grows a separate method for every unrelated route or policy
- A policy change requiring changes to infrastructure-oriented service code

**Why it matters:** A service should either declare and delegate a policy or contain a cohesive implementation for a related domain. Mixing both makes navigation and maintenance more expensive.

**Suggested comment:** "This service now contains orchestration and material-specific rules. Could the service delegate the rule to a domain policy while retaining the workflow?"

**Fix:** Separate orchestration from implementation and keep each service aligned with one coherent responsibility.

## Test extracted policies as independent behavior

`id: cl-test-extracted-policy | category: testing | severity: medium | source: book (Ch.13) + editorial | languages: any | tags: unit-tests, strategy, behavior, implementation-details, testability, documentation`

**Look for in a diff:**
- A new focused policy class without direct behavior tests
- Tests that cover only a large service path for a reusable rule
- Tests coupled to private fields or implementation structure
- A refactor that changes production structure and removes behavior coverage

**Why it matters:** Small closed policies are easier to test in isolation. Tests that verify outcomes through stable interfaces document intended behavior better than comments tied to implementation details.

**Suggested comment:** "This fine policy is now isolated but has no focused boundary tests. Could we cover its rates, limits, and edge cases directly?"

**Fix:** Test extracted behavior through its public contract and keep higher-level tests for orchestration and integration.

## Do not over-engineer for theoretical closure

`id: cl-avoid-class-explosion | category: review-guidance | severity: low | source: book (Ch.13) + editorial | languages: any | tags: over-engineering, class-explosion, srp, ocp, abstraction, indirection, complexity`

**Look for in a diff:**
- A separate class for every branch or trivial delegation
- An abstraction that increases navigation cost without isolating real volatility
- A controller, service, or route split solely to satisfy a principle

**Why it matters:** Fully pluggable designs can be difficult to discover and maintain. SRP and OCP are directions for improvement, not a requirement to create a class for every line of behavior.

**Suggested comment:** "This adds several layers for one stable branch. What expected change justifies the extra indirection?"

**Fix:** Keep cohesive behavior together until a real change boundary or testability benefit justifies extraction.

## Use AI-generated class designs as proposals, not proof

`id: cl-ai-class-review | category: ai-review | severity: high | source: book (Ch.13) + editorial | languages: any | tags: ai-generated-code, tests, srp, ocp, design-review, verification`

**Look for in a diff:**
- AI-generated classes with plausible local structure but unclear system boundaries
- Generated abstractions that ignore dependency direction or change axes
- Tests generated from the same assumptions as the implementation
- AI output accepted without checking behavior against requirements

**Why it matters:** AI can produce structurally plausible code while missing architectural goals or introducing defects. Clean boundaries make errors easier to isolate, but they do not replace human review and independent tests.

**Suggested comment:** "The generated classes look locally coherent, but the dependency direction and change boundary need evidence. Could we verify the design against the expected future variation and independent tests?"

**Fix:** Review AI output at module and architecture level, validate tests against requirements, and verify behavior independently.
