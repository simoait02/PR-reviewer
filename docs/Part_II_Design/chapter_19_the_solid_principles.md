# Clean Code, Chapter 19: The SOLID Principles, PR review rules

## Use SOLID as changeability guidance, not a checklist

`id: solid-changeability-heuristics | category: design | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: solid, design, changeability, cohesion, pragmatism`

**Look for in a diff:**
- A principle applied mechanically without a concrete change or coupling risk
- Interfaces, wrappers, or classes added only to satisfy a slogan
- A design that improves one SOLID concern while harming readability or cohesion

**Why it matters:** SOLID is intended to produce understandable structures that tolerate change. The principles are signals for design tradeoffs, not automatic defects or a requirement for abstraction everywhere.

**Suggested comment:** "What expected change or dependency risk does this SOLID split address? Could we choose the smallest structure that improves that risk?"

**Fix:** Tie each design decision to a responsibility, volatility, substitution contract, client dependency, or policy/detail boundary.

## Separate modules that serve different actors

`id: solid-srp-one-actor | category: design | severity: high | source: book (Ch.19) + editorial | languages: any | tags: srp, actors, stakeholders, cohesion, reasons-to-change`

**Look for in a diff:**
- One module containing payroll, reporting, persistence, or policy code owned by different stakeholders
- A change for one actor unexpectedly modifying behavior used by another actor
- A shared class accumulating methods that change for unrelated business reasons

**Why it matters:** The Single Responsibility Principle is about one reason to change, understood as one actor or group of stakeholders. Separating those responsibilities prevents accidental coupling between teams and policies.

**Suggested comment:** "These methods change for different stakeholder groups, so a payroll change can alter reporting behavior. Could the responsibilities have separate owners?"

**Fix:** Split code by change reason, then use a small facade or coordinator when callers need a convenient entry point.

## Do not confuse SRP with one function per class

`id: solid-srp-is-not-one-function | category: review-guidance | severity: low | source: book (Ch.19) + editorial | languages: any | tags: srp, cohesion, class-size, overengineering, pragmatism`

**Look for in a diff:**
- Classes split into one-method wrappers without independent change pressure
- A review demanding a class extraction solely because a class has multiple methods
- Related operations separated even though they serve the same actor and change together

**Do not flag when:** the extracted unit has a distinct reason to change, a useful contract, or a clear testability/boundary benefit.

**Why it matters:** SRP is about cohesive responsibility, not a numeric method count. Splitting cohesive behavior can add indirection without reducing risk.

**Suggested comment:** "These methods appear to serve the same actor and change together. What independent change boundary justifies separating them?"

**Fix:** Group behavior by stakeholder and change reason; extract only when the resulting boundary is materially clearer or safer.

## Avoid shared helpers that couple different actors

`id: solid-avoid-cross-actor-helper | category: design | severity: high | source: book (Ch.19) + editorial | languages: any | tags: srp, duplication, shared-helper, coupling, change-risk`

**Look for in a diff:**
- A helper reused by unrelated policies because its algorithm currently looks similar
- A change to one consumer’s calculation silently changing another consumer’s result
- Flags or modes added to make one helper serve multiple stakeholder needs

**Why it matters:** Shared code between different actors creates accidental coupling. A harmless change for one policy can corrupt another policy’s output.

**Suggested comment:** "These consumers have different change reasons, even though the calculation is similar today. Could the policies keep separate implementations or use a narrower shared primitive?"

**Fix:** Separate actor-owned rules; share only a genuinely stable, independently owned concept with a contract that fits all consumers.

## Add extension points for real recurring variation

`id: solid-ocp-real-extension | category: design | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: ocp, extension, variation, strategy, switch`

**Look for in a diff:**
- A stable module edited for every new variant or policy
- A growing switch over types, formats, providers, or business rules
- A confirmed variation that could be added through a strategy, plugin, or implementation

**Do not flag when:** the variant set is small and stable, or an abstraction would be speculative and more complex than the current change.

**Why it matters:** The Open-Closed Principle reduces the blast radius of recurring extensions by isolating the axis of variation. It should be driven by actual change pressure.

**Suggested comment:** "Every new provider requires editing this policy module. Could the varying behavior move behind a strategy while the stable workflow remains closed?"

**Fix:** Identify the volatile axis, define a minimal stable contract, and add implementations without repeatedly changing the protected policy.

## Protect high-level policy from peripheral changes

`id: solid-ocp-protect-policy | category: architecture | severity: high | source: book (Ch.19) + editorial | languages: any | tags: ocp, architecture, protection, policy, dependencies, boundaries`

**Look for in a diff:**
- Database, UI, controller, or presentation changes forcing edits to core business rules
- Dependencies flowing from the policy toward every peripheral implementation
- One component that must change whenever a lower-level detail changes

**Why it matters:** A useful dependency hierarchy protects high-level policy from volatile details. This makes extensions safer and keeps central rules stable as delivery mechanisms evolve.

**Suggested comment:** "The core interactor now imports the new view/database detail. Could the dependency point through an interface so peripheral changes do not modify the policy?"

**Fix:** Place interfaces at the protected policy boundary and make peripheral components implement or adapt to them.

## Hide transitive implementation details

`id: solid-hide-transitive-details | category: design | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: information-hiding, transitive-dependency, encapsulation, api, isp`

**Look for in a diff:**
- Callers reaching through a service to its entities, repositories, or framework objects
- Public return types exposing dependencies that callers do not directly use
- A controller knowing internal policy data merely to invoke one operation

**Why it matters:** Transitive dependencies spread knowledge and make unrelated internal changes ripple through callers. Information-hiding boundaries keep each client dependent on only what it uses.

**Suggested comment:** "The controller now depends on the interactor’s internal entity structure. Could the interactor expose a focused request/response contract instead?"

**Fix:** Add a narrow boundary interface or data transfer contract and keep internal collaborators behind it.

## Preserve substitutability contracts

`id: solid-lsp-preserve-contract | category: design | severity: high | source: book (Ch.19) + editorial | languages: any | tags: lsp, substitution, contracts, polymorphism, inheritance`

**Look for in a diff:**
- A subtype rejecting inputs accepted by the base contract
- A subtype returning a different meaning, unit, error model, or lifecycle behavior
- Callers adding type checks or special cases before using an implementation

**Why it matters:** The Liskov Substitution Principle requires implementations to be interchangeable wherever the contract is used. A subtype that changes the caller’s assumptions turns polymorphism into hidden branching.

**Suggested comment:** "This implementation does not honor the interface’s accepted input/error contract, so callers need a special case. Could the contract or implementation be corrected to preserve substitution?"

**Fix:** Define preconditions, postconditions, invariants, errors, and side effects explicitly; test every implementation against the shared contract.

## Treat APIs and services as substitution contracts too

`id: solid-lsp-beyond-inheritance | category: architecture | severity: high | source: book (Ch.19) + editorial | languages: any | tags: lsp, api, rest, services, contracts, compatibility`

**Look for in a diff:**
- A REST/provider implementation using different field names, units, status semantics, or response shapes
- Adapter-specific branches leaking into the common caller
- A service claiming compatibility while requiring caller knowledge of its identity

**Why it matters:** LSP applies to interfaces, adapters, and services, not only class inheritance. Incompatible implementations pollute callers with special cases and increase operational risk.

**Suggested comment:** "This provider changes the shared request field/semantics, forcing a caller special case. Could the adapter conform to the common contract or expose a distinct explicit contract?"

**Fix:** Validate compatibility with contract tests, normalize provider differences at the boundary, and avoid identity-based branching in shared policy code.

## Split interfaces by client needs

`id: solid-isp-client-specific-interfaces | category: design | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: isp, interfaces, clients, coupling, api`

**Look for in a diff:**
- A client depending on a large interface while using only one or two operations
- Changes to unused operations forcing rebuilds, redeployments, mocks, or client updates
- A shared service interface accumulating unrelated client methods

**Why it matters:** The Interface Segregation Principle prevents clients from depending on operations they do not use. Smaller client-specific contracts reduce coupling and make changes local.

**Suggested comment:** "This client depends on a broad interface but uses only `read`. Could it depend on a focused read contract so unrelated changes do not affect it?"

**Fix:** Define narrow role interfaces or ports and compose them where a broader capability is genuinely needed.

## Do not depend on unused dependency baggage

`id: solid-isp-avoid-unused-baggage | category: architecture | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: isp, dependencies, framework, database, coupling, baggage`

**Look for in a diff:**
- A module forced to depend on a framework or database feature it does not use
- Large dependency surfaces imported for a small capability
- Failures or upgrades in unrelated dependency features affecting a client

**Why it matters:** Unused dependency baggage increases build, deployment, failure, and upgrade coupling even in languages without explicit interfaces.

**Suggested comment:** "This component pulls in the full framework/database surface for one capability. Could a smaller adapter or port avoid coupling the client to unused features?"

**Fix:** Depend on the smallest required API, isolate broad frameworks behind adapters, and keep clients unaware of unused capabilities.

## Invert dependencies at volatile boundaries

`id: solid-dip-invert-volatile-dependencies | category: architecture | severity: high | source: book (Ch.19) + editorial | languages: any | tags: dip, dependency-inversion, policy, details, volatility`

**Look for in a diff:**
- High-level policy importing a frequently changing database, UI, vendor, or transport implementation
- Source dependencies following control flow into volatile details
- Business rules difficult to test without constructing concrete infrastructure

**Why it matters:** The Dependency Inversion Principle lets stable policy define the contract while volatile details implement it. This improves testability and limits the impact of infrastructure change.

**Suggested comment:** "The high-level policy now depends directly on a volatile vendor implementation. Could the policy own a narrow interface and have the detail implement it?"

**Fix:** Introduce a policy-level port, inject it into the high-level code, and keep concrete adapters at the composition boundary.

## Depend on stable abstractions, not every concrete type

`id: solid-dip-stable-abstractions | category: design | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: dip, abstractions, stable, concrete, volatility`

**Look for in a diff:**
- New imports, inheritance, or overrides of volatile concrete classes
- Stable policy code naming implementation classes that are still changing frequently
- Concrete dependencies introduced where a meaningful stable contract already exists

**Do not flag when:** the dependency is a stable platform facility or the abstraction would add no useful boundary.

**Why it matters:** Concrete implementations change more often than the contracts they honor. Depending on volatile details makes stable code inherit unnecessary churn.

**Suggested comment:** "This policy depends on a concrete implementation that changes frequently. Could it depend on the stable contract instead, if the boundary is real?"

**Fix:** Isolate volatile concretes behind stable interfaces and treat the rule as a warning to evaluate, not an excuse for interface explosion.

## Keep object creation at composition boundaries

`id: solid-dip-composition-boundary | category: architecture | severity: high | source: book (Ch.19) + editorial | languages: any | tags: dip, factories, composition-root, dependency-injection, main`

**Look for in a diff:**
- Core policy constructing vendor clients, databases, queues, or UI implementations directly
- `new` calls for volatile dependencies scattered throughout business code
- Factory logic mixed into a use case that should only execute policy

**Why it matters:** Creation creates a source dependency on the concrete type. Concentrating that dependency in a composition root keeps the application policy independent and easier to test.

**Suggested comment:** "This use case constructs its infrastructure dependency, tying policy to the concrete class. Could creation move to the composition boundary and be injected?"

**Fix:** Use a composition root, factory, or dependency-injection setup to build concretes and pass stable contracts inward.

## Gather unavoidable concrete dependencies in a small boundary

`id: solid-isolate-concrete-components | category: architecture | severity: medium | source: book (Ch.19) + editorial | languages: any | tags: dip, concrete-components, boundaries, main, pragmatism`

**Look for in a diff:**
- Concrete dependency violations spread across many modules
- Infrastructure setup leaking into otherwise stable business components
- A design claiming zero concrete dependencies through layers of unnecessary abstractions

**Do not flag when:** the concrete dependency is stable platform behavior or is intentionally confined to a clearly named composition/infrastructure boundary.

**Why it matters:** DIP violations cannot always be removed, but they can be contained. A small concrete boundary makes volatility visible and prevents it from infecting the whole system.

**Suggested comment:** "These concrete dependencies are distributed through the policy layer. Could they be gathered in one composition boundary instead of being abstracted at every call site?"

**Fix:** Concentrate construction and vendor knowledge in a small adapter/composition component and keep the rest of the dependency graph pointed toward policy contracts.
