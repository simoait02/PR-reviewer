# Clean Code, Chapter 27: The Clean Architecture, PR review rules

## Point source dependencies toward higher-level policy

`id: ca-dependencies-point-inward | category: architecture | severity: critical | source: book (Ch.27) + editorial | languages: any | tags: clean-architecture, dependency-rule, policy, details, boundaries`

**Look for in a diff:**
- Entities or use cases importing UI, database, web, framework, or vendor code
- Inner layers naming classes, functions, or formats declared in outer layers
- A dependency arrow crossing inward toward a lower-level mechanism

**Why it matters:** Inner policy is more valuable and stable than outer mechanisms. Inward dependencies protect business rules from changes in delivery, persistence, and frameworks.

**Suggested comment:** "This use case imports an outer-layer type, so a detail change will force policy changes. Could the inner layer define the contract and let the outer adapter implement it?"

**Fix:** Invert the dependency at the boundary and keep source references directed toward higher-level policy.

## Keep entities independent of application and delivery concerns

`id: ca-entities-protect-enterprise-rules | category: architecture | severity: critical | source: book (Ch.27) + editorial | languages: any | tags: entities, business-rules, use-cases, ui, database`

**Look for in a diff:**
- Core business entities depending on navigation, authorization framework, ORM, HTTP, or UI concerns
- Enterprise rules changed because an application-specific workflow changed
- Entities containing transport/persistence annotations that alter their core contract

**Why it matters:** Entities contain the most general business rules and should survive changes to applications and external mechanisms.

**Suggested comment:** "This entity now knows about the application/ORM concern, so an outer change can affect enterprise rules. Could the mapping stay outside the entity?"

**Fix:** Keep entities focused on general business invariants and translate external/application concerns at the appropriate boundary.

## Keep use cases isolated from frameworks and infrastructure

`id: ca-use-cases-independent | category: architecture | severity: critical | source: book (Ch.27) + editorial | languages: any | tags: use-cases, frameworks, database, ui, application-rules`

**Look for in a diff:**
- Use cases directly querying databases, returning HTTP responses, or invoking UI/framework APIs
- Application rules implemented inside controllers, repositories, or framework callbacks
- A framework migration requiring changes to use-case logic

**Why it matters:** Use cases orchestrate application behavior and should be testable without external systems. Keeping them independent preserves the core of the application.

**Suggested comment:** "The use case now performs database/HTTP work directly. Could it depend on an inner port and let an adapter handle the external mechanism?"

**Fix:** Keep orchestration and application policy inward; inject ports and move infrastructure calls to adapters.

## Keep interface adapters responsible for data conversion

`id: ca-adapters-translate-data | category: architecture | severity: high | source: book (Ch.27) + editorial | languages: any | tags: adapters, controllers, presenters, mappers, data-conversion`

**Look for in a diff:**
- Controllers passing framework request objects into use cases
- Presenters or repositories leaking external records, rows, or response types inward
- Conversion rules duplicated across controllers, use cases, and views

**Why it matters:** Adapters convert external representations into forms convenient for policy and back again. Centralizing translation keeps each layer independent and reduces format leakage.

**Suggested comment:** "The use case receives a framework request/database row, coupling the inner layer to the outer format. Could the adapter map it to a simple input structure?"

**Fix:** Map inputs and outputs at the adapter boundary and keep the inner contract composed of simple application-owned data.

## Keep frameworks and drivers at the outer edge

`id: ca-frameworks-at-the-edge | category: architecture | severity: high | source: book (Ch.27) + editorial | languages: any | tags: frameworks, drivers, database, web, glue-code`

**Look for in a diff:**
- Framework conventions determining domain module structure
- Significant business logic placed in controllers, ORM models, route handlers, or framework callbacks
- Outer technology types exported as core APIs

**Why it matters:** Frameworks and drivers are details and often change. Keeping their code thin limits the impact of replacement, upgrades, and testing constraints.

**Suggested comment:** "This controller/ORM callback contains core business logic and will be difficult to exercise independently. Could it become a thin adapter to a use case?"

**Fix:** Keep outer code as glue, delegate policy inward, and prevent framework types from crossing into inner layers.

## Use only the layers the change actually needs

`id: ca-layers-are-not-a-fixed-count | category: architecture | severity: low | source: book (Ch.27) + editorial | languages: any | tags: layers, architecture, boundaries, pragmatism, overengineering`

**Look for in a diff:**
- Empty layers or wrappers added solely to match a diagram
- A rigid four-layer structure that obscures a small feature
- Missing boundaries where the dependency rule is violated because the project has fewer named layers

**Why it matters:** Clean Architecture is about dependency direction and policy/detail separation, not a mandatory number of circles or packages.

**Suggested comment:** "This layer adds no policy or boundary and only forwards calls. Could we keep the design smaller while preserving the dependency rule?"

**Fix:** Use as many layers as provide meaningful change protection, and judge them by dependency direction and responsibility.

## Invert output dependencies at the boundary

`id: ca-invert-output-boundary | category: architecture | severity: high | source: book (Ch.27) + editorial | languages: any | tags: dependency-inversion, output-port, presenters, use-cases, polymorphism`

**Look for in a diff:**
- A use case directly constructing or calling a presenter/view/controller
- Inner code importing outer output types
- Output formatting decisions made inside the use case solely to satisfy one UI

**Why it matters:** Control flow may move outward to a presenter, but source dependencies must remain inward. An inner output port preserves both the flow and the dependency rule.

**Suggested comment:** "The interactor calls the concrete presenter, so the inner layer depends outward. Could it call an inner output port implemented by the presenter?"

**Fix:** Define an output boundary in the inner layer and implement it in the outer adapter.

## Pass simple boundary data structures

`id: ca-simple-boundary-data | category: architecture | severity: high | source: book (Ch.27) + editorial | languages: any | tags: dto, data-transfer, entities, database-rows, boundaries`

**Look for in a diff:**
- Entities, ORM records, framework request objects, or database rows crossing architectural boundaries
- Boundary data carrying lazy loading, persistence methods, or framework behavior
- Inner layers depending on an outer data format because it is convenient

**Why it matters:** Data crossing a boundary should be shaped for the receiving inner layer. Passing outer objects leaks implementation details and creates transitive coupling.

**Suggested comment:** "This database row/entity crosses into the use case and carries persistence behavior. Could the adapter map it to a simple request/response structure?"

**Fix:** Use plain arguments, value objects, DTOs, or simple records owned by the receiving contract.

## Keep presentation formatting out of policy

`id: ca-presenter-formats-output | category: architecture | severity: medium | source: book (Ch.27) + editorial | languages: any | tags: presenter, formatting, dates, currency, view-model, ui`

**Look for in a diff:**
- Use cases formatting dates, currency, labels, button names, or display flags for one view
- Views applying business decisions that should be consistent across interfaces
- Presentation-specific strings returned from entities or domain policies

**Why it matters:** Presenters translate application output into a view model while policy remains independent of display technology. This allows multiple UIs and consistent business behavior.

**Suggested comment:** "The use case formats a date/currency for this view, coupling application behavior to presentation. Could the presenter create the view model from a policy-level result?"

**Fix:** Return semantic output from the use case and perform display formatting and view-state selection in the presenter/adapter.

## Test inner circles without outer systems

`id: ca-test-inner-circles-isolated | category: testing | severity: high | source: book (Ch.27) + editorial | languages: any | tags: testability, use-cases, entities, unit-tests, infrastructure`

**Look for in a diff:**
- Entity/use-case tests requiring a web server, database, framework, or real external service
- No way to replace outer ports with controlled test implementations
- Core behavior verified only by slow end-to-end tests

**Why it matters:** The architecture is valuable partly because inner policy can be tested quickly and independently. Isolated tests expose regressions before outer integration noise obscures them.

**Suggested comment:** "The inner policy can only be tested through the full stack, so the boundary is not providing isolation. Could the outer dependency be replaced by a test port?"

**Fix:** Test entities and use cases against simple inputs and fakes; test adapters and full integration separately.

## Verify the dependency rule when adding a framework feature

`id: ca-framework-feature-does-not-invert-core | category: architecture | severity: high | source: book (Ch.27) + editorial | languages: any | tags: framework, dependency-rule, annotations, imports, architecture`

**Look for in a diff:**
- A convenience framework feature adding outer imports to inner modules
- An annotation, base class, or generated type that makes policy framework-dependent
- A short-term integration shortcut that permanently moves the boundary inward

**Why it matters:** Framework convenience can silently reverse the dependency rule and make future replacement or isolated testing expensive.

**Suggested comment:** "This framework feature requires the inner module to depend on an outer package. Could an adapter or mapping preserve the dependency rule?"

**Fix:** Keep framework usage at the edge, introduce an application-owned port or mapper, and review the full dependency graph after integration.
