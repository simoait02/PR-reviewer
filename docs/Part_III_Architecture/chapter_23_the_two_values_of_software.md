# Clean Code, Chapter 23: The Two Values of Software, PR review rules

## Preserve both behavioral and structural value

`id: av-behavior-and-structure | category: architecture | severity: high | source: book (Ch.23) + editorial | languages: any | tags: architecture, behavior, structure, maintainability, changeability`

**Look for in a diff:**
- A behavior change that makes future changes harder to locate, understand, test, or isolate
- Structural cleanup that changes user-visible behavior without explicit intent
- “It works” used as the only definition of a successful implementation

**Why it matters:** Software delivers behavior, but its structure determines how cheaply and safely future behavior can be changed. A system that works today but resists change has lost a core part of its value.

**Suggested comment:** "The behavior is correct, but this change couples the policy to another detail and raises the cost of future changes. Could the structure preserve a replaceable boundary?"

**Fix:** Verify the requested behavior and review the impact on cohesion, dependencies, testability, and future change cost.

## Keep policy separate from detail

`id: av-policy-independent-of-details | category: architecture | severity: critical | source: book (Ch.23) + editorial | languages: any | tags: policy, details, business-rules, database, framework, boundaries`

**Look for in a diff:**
- Business rules importing database, web, UI, server, framework, or protocol details
- High-level decisions expressed in HTML/SQL/transport-specific types
- Replacing a detail requiring changes to the policy implementation

**Why it matters:** Policy contains the system’s essential value. Details enable communication and deployment but should not determine how the policy behaves.

**Suggested comment:** "The business rule now knows about the database/web/framework detail. Could the policy expose a stable contract and leave this decision at the boundary?"

**Fix:** Isolate details behind adapters and ports so policy can execute without knowing the delivery or storage mechanism.

## Defer irreversible detail decisions

`id: av-defer-detail-decisions | category: architecture | severity: high | source: book (Ch.23) + editorial | languages: any | tags: architecture, options, database, framework, protocols, reversibility`

**Look for in a diff:**
- A database, web framework, transport, deployment model, or DI framework embedded in core policy without evidence it is essential
- An early technology choice forcing interfaces and data models before requirements are known
- Architecture that makes replacing a detail require rewriting business rules

**Do not flag when:** the detail is itself a core requirement or the decision is reversible behind a tested boundary.

**Why it matters:** Deferring irrelevant choices allows more information and experiments before commitment. Early coupling turns an uncertain decision into an expensive constraint.

**Suggested comment:** "This commits the core policy to a concrete technology before the boundary is required. Could the decision be delayed behind a small interface?"

**Fix:** Keep policy technology-agnostic, place selection in composition/configuration code, and commit only when evidence requires it.

## Keep interfaces agnostic about delivery mechanisms

`id: av-delivery-agnostic-policy | category: architecture | severity: high | source: book (Ch.23) + editorial | languages: any | tags: web, rest, ui, protocols, api, policy`

**Look for in a diff:**
- Core use cases returning HTTP responses, UI widgets, HTML, or protocol envelopes
- Business behavior branching on whether the caller is web, CLI, batch, or messaging
- REST/microservice assumptions leaking into domain contracts without a policy need

**Why it matters:** Delivery mechanisms change independently of business rules. Keeping policy agnostic allows the same behavior to be exposed through different interfaces and makes experiments cheaper.

**Suggested comment:** "The use case now returns a transport-specific response, coupling policy to this delivery mechanism. Could the boundary translate a policy result into HTTP/UI details?"

**Fix:** Define application-facing requests/results and perform protocol/UI translation at the outer boundary.

## Keep persistence choices behind policy-level contracts

`id: av-persistence-agnostic-policy | category: architecture | severity: high | source: book (Ch.23) + editorial | languages: any | tags: database, persistence, repositories, policy, schema`

**Look for in a diff:**
- Domain rules depending on SQL queries, ORM entities, document schemas, or database transactions
- A persistence migration requiring business logic changes unrelated to behavior
- Database structure becoming the public shape of the core model by accident

**Why it matters:** Database technology is a detail until requirements prove otherwise. Policy should express the data and operations it needs, not the storage mechanism that supplies them.

**Suggested comment:** "The policy consumes ORM/database types directly, so a storage change will ripple inward. Could an application-facing port keep schema details at the persistence boundary?"

**Fix:** Map persistence records to policy models at the boundary and define repositories/ports around use-case needs.

## Keep dependency resolution out of policy

`id: av-policy-independent-of-di-framework | category: architecture | severity: medium | source: book (Ch.23) + editorial | languages: any | tags: dependency-injection, framework, composition-root, policy, architecture`

**Look for in a diff:**
- Core code importing a DI container or resolving services from a global locator
- Business logic depending on framework lifecycle, annotations, or startup magic
- Switching DI frameworks requiring changes throughout policy modules

**Why it matters:** Dependency resolution is a detail of composition. Policy should receive collaborators through stable contracts rather than knowing how they are found or constructed.

**Suggested comment:** "The use case resolves its dependencies from the container, coupling policy to framework lifecycle. Could construction stay in the composition root and collaborators be passed in?"

**Fix:** Inject policy dependencies explicitly and keep container/configuration code at the application boundary.

## Preserve replaceable options for experiments

`id: av-boundaries-enable-experiments | category: architecture | severity: medium | source: book (Ch.23) + editorial | languages: any | tags: experiments, options, replaceability, performance, architecture`

**Look for in a diff:**
- A design that makes it impossible to compare storage, transport, or framework alternatives
- Performance or suitability assumptions encoded without a replaceable seam
- A detail selected permanently before representative measurements exist

**Why it matters:** A good boundary lets the team connect policy to alternative details and gather evidence. Experiments reduce architectural guesswork before an irreversible commitment.

**Suggested comment:** "This boundary prevents comparing the alternatives that may affect performance/operability. Could the policy remain detail-agnostic long enough to run a representative experiment?"

**Fix:** Keep alternatives behind the same meaningful contract, measure them with realistic workloads, and commit when evidence—not habit—supports the choice.

## Maximize deferred decisions without creating speculative abstraction

`id: av-defer-without-overabstracting | category: architecture | severity: medium | source: book (Ch.23) + editorial | languages: any | tags: options, abstraction, yagni, architecture, changeability`

**Look for in a diff:**
- A framework-free design replaced with a generic abstraction for every imaginable detail
- Interfaces that do not represent a real policy need or current alternative
- “Keeping options open” used to justify layers that make present behavior harder to understand

**Why it matters:** Deferring details is valuable only when the boundary is simpler than the commitment or protects a real option. Speculative abstraction can reduce flexibility by obscuring the current design.

**Suggested comment:** "This abstraction keeps a theoretical option open but adds no current boundary or test benefit. Could we defer the detail with a simpler design until an actual alternative appears?"

**Fix:** Preserve only meaningful options, keep interfaces narrow, and avoid abstraction whose maintenance cost exceeds the decision it defers.
