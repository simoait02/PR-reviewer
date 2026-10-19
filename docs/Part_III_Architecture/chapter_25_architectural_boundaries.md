# Clean Code, Chapter 25: Architectural Boundaries, PR review rules

## Draw boundaries around policy and details

`id: ab-boundary-policy-from-details | category: architecture | severity: critical | source: book (Ch.25) + editorial | languages: any | tags: boundaries, policy, details, coupling, architecture`

**Look for in a diff:**
- Business rules and framework, UI, database, or transport code in the same module
- A detail decision becoming visible in core types or control flow
- A change to an ancillary tool requiring edits to essential policy

**Why it matters:** Architectural boundaries control knowledge and coupling. Separating what matters from what is replaceable reduces the manpower required to build and maintain the system.

**Suggested comment:** "The core policy now knows about this framework/database detail. Could a boundary keep the detail from crossing into the business rules?"

**Fix:** Partition policy and details into components with a stable policy-facing contract.

## Make dependency arrows point toward the core

`id: ab-dependency-rule-toward-core | category: architecture | severity: critical | source: book (Ch.25) + editorial | languages: any | tags: dependency-rule, dip, core, interfaces, components`

**Look for in a diff:**
- Core code importing concrete database, UI, server, or framework implementations
- An adapter interface defined in the detail component and pulled inward by policy
- Dependency direction crossing a boundary toward a lower-level detail

**Why it matters:** The protected policy should own the abstraction it needs. Details can depend on that abstraction, allowing them to change or be replaced without rewriting the core.

**Suggested comment:** "The dependency crosses the boundary toward the database/UI detail. Could the core define the interface and have the adapter implement it?"

**Fix:** Place policy-level interfaces on the core side and make outer components implement/adapt them.

## Keep databases behind policy-facing ports

`id: ab-database-behind-port | category: architecture | severity: high | source: book (Ch.25) + editorial | languages: any | tags: database, persistence, port, adapter, schema`

**Look for in a diff:**
- Use cases issuing SQL or receiving ORM/schema types directly
- Database technology determining business method names and data shapes
- Persistence replacement requiring changes to business logic

**Why it matters:** The core needs operations and data relevant to policy, not schema/query details. A port lets the system defer or change the storage technology.

**Suggested comment:** "The business rule now depends on query/schema details. Could a persistence port expose only the operations this use case needs?"

**Fix:** Define a core-owned repository/port, translate between policy models and storage records in the adapter, and test both sides at their contracts.

## Keep user interfaces as plug-ins to the core

`id: ab-ui-as-plugin | category: architecture | severity: high | source: book (Ch.25) + editorial | languages: any | tags: ui, gui, web, plugin, use-cases, boundaries`

**Look for in a diff:**
- Core policy returning UI widgets, HTML, framework events, or view-model details
- UI technology determining business behavior or validation rules
- Supporting a second interface requiring changes to the core use cases

**Why it matters:** Web, console, client/server, and service interfaces are delivery details. Treating them as plug-ins keeps the business rules reusable and replaceable.

**Suggested comment:** "The use case now returns UI-specific data, so another delivery mechanism will require policy changes. Could the UI adapter translate a core response instead?"

**Fix:** Keep use cases interface-agnostic and place presentation/input mapping in outer controllers, presenters, or adapters.

## Use plug-in boundaries to defer technology choices

`id: ab-plugin-defer-technology | category: architecture | severity: medium | source: book (Ch.25) + editorial | languages: any | tags: plugins, options, framework, database, experiments`

**Look for in a diff:**
- A framework or database chosen before the business behavior requires it
- Core development blocked by an infrastructure dependency that could be stubbed
- No way to test policy without starting the selected technology

**Why it matters:** Plug-in boundaries let teams develop and test policy while details remain undecided. They also make experiments and later replacement practical.

**Suggested comment:** "The feature does not yet require this technology, but the core is already coupled to it. Could a plug-in/port let development continue with a simple test implementation?"

**Fix:** Introduce a minimal boundary, use an in-memory/fake implementation during policy development, and select the technology at composition time.

## Keep adapters responsible for translation

`id: ab-adapter-translates-contracts | category: architecture | severity: high | source: book (Ch.25) + editorial | languages: any | tags: adapters, translation, mapping, boundaries, encapsulation`

**Look for in a diff:**
- Database/UI/framework types leaking across a boundary
- Mapping logic duplicated in policy and adapter layers
- A core use case interpreting transport status codes, schema fields, or framework events

**Why it matters:** Translation belongs at the boundary. Keeping it there prevents external representations from becoming part of the policy model and localizes integration changes.

**Suggested comment:** "The use case interprets transport/database representation directly. Could the adapter translate it into the core contract once at the boundary?"

**Fix:** Map external inputs to policy requests and policy results to external outputs in dedicated adapters.

## Test the core without infrastructure

`id: ab-core-testable-without-details | category: testing | severity: high | source: book (Ch.25) + editorial | languages: any | tags: testing, boundaries, unit-tests, infrastructure, feedback`

**Look for in a diff:**
- Core tests requiring a real database, web server, framework container, or filesystem
- Slow or flaky infrastructure setup for behavior that should be deterministic
- No fake or in-memory implementation for a boundary contract

**Why it matters:** The point of the boundary is to protect policy from details. Fast core tests provide feedback while infrastructure tests verify adapters separately.

**Suggested comment:** "This policy test requires the real database/server, so boundary isolation is not providing fast feedback. Could a contract fake test the core and leave integration to adapter tests?"

**Fix:** Test core behavior with controlled ports, test adapters against their external contract, and reserve end-to-end tests for critical integration paths.

## Keep boundaries narrow and purpose-specific

`id: ab-narrow-boundary-contracts | category: architecture | severity: medium | source: book (Ch.25) + editorial | languages: any | tags: boundaries, interfaces, cohesion, api, coupling`

**Look for in a diff:**
- A boundary interface exposing an entire framework, database client, or domain object graph
- Ports containing operations needed by only one unrelated adapter/client
- A “generic” boundary that increases knowledge instead of reducing it

**Why it matters:** Broad boundaries leak details and make both sides change together. A narrow contract expresses what the policy needs and keeps the boundary stable.

**Suggested comment:** "This port exposes the full vendor/database API, so policy still depends on details. Could it contain only the operations and data this use case requires?"

**Fix:** Define role-specific ports, keep data contracts minimal, and split boundaries when clients have different change reasons.

## Review boundaries as change-protection decisions

`id: ab-boundary-protects-change | category: architecture | severity: medium | source: book (Ch.25) + editorial | languages: any | tags: boundaries, changeability, volatility, architecture, review`

**Look for in a diff:**
- A new boundary with no clear volatile detail or protected policy
- A supposedly protected component still requiring edits when the detail changes
- Boundary placement justified by folder structure rather than dependency direction and change impact

**Why it matters:** A boundary is valuable only if it protects one side from changes on the other. Review it by asking what decision it defers and which changes it prevents from propagating.

**Suggested comment:** "This interface adds a layer but the concrete detail still leaks through the types. What change is the boundary meant to protect, and can that protection be demonstrated?"

**Fix:** Name the protected policy and deferred detail, verify dependency direction, and remove boundaries that provide no real change isolation.
