# Clean Code, Chapter 24: Independence, PR review rules

## Make use cases visible in the architecture

`id: ai-use-cases-visible | category: architecture | severity: high | source: book (Ch.24) + editorial | languages: any | tags: use-cases, intent, architecture, modules, navigation`

**Look for in a diff:**
- A feature’s behavior scattered across framework, controller, persistence, and utility layers
- Top-level modules named after infrastructure rather than user goals
- Reviewers needing to trace many technical components to identify the use case

**Why it matters:** Architecture should expose system intent. When use cases are first-class, developers can find behavior quickly and change it without understanding every delivery detail.

**Suggested comment:** "The new use case is hidden across infrastructure modules and is not visible from the application structure. Could the behavior have a named application-level entry point?"

**Fix:** Organize policy around clearly named use cases and keep adapters/controllers as outer mechanisms that invoke them.

## Keep architecture independent of delivery mechanism

`id: ai-delivery-mechanism-independent | category: architecture | severity: high | source: book (Ch.24) + editorial | languages: any | tags: web, services, ui, monolith, processes, communication`

**Look for in a diff:**
- Core use cases assuming HTTP, a specific UI framework, service boundaries, or a monolithic process
- Communication details determining domain boundaries or business behavior
- A delivery change requiring changes to use-case policy

**Why it matters:** Operational delivery may move between a monolith, processes, threads, or services as needs change. Isolating communication details preserves that option.

**Suggested comment:** "The use case now depends on the current transport/process arrangement. Could communication stay at the boundary so the deployment model can evolve independently?"

**Fix:** Define stable use-case contracts and adapt HTTP, messaging, UI, process, or service mechanisms outside the policy.

## Let operational requirements shape boundaries without dictating policy

`id: ai-operational-boundaries | category: architecture | severity: high | source: book (Ch.24) + editorial | languages: any | tags: throughput, latency, scalability, operations, architecture`

**Look for in a diff:**
- A throughput/latency requirement impossible to satisfy with the current component boundaries
- Performance concerns solved by embedding infrastructure assumptions into business rules
- Components that cannot be scaled or parallelized independently where the workload requires it

**Why it matters:** Architecture must support operational needs, but policy should not be entangled with one deployment strategy. Proper boundaries allow operational changes without rewriting essential behavior.

**Suggested comment:** "This boundary prevents the workload from being scaled/parallelized independently, while the policy now knows about the mechanism. Could the operation be isolated behind a stable contract?"

**Fix:** Measure the operational requirement, partition work at meaningful boundaries, and keep scaling/parallelism concerns in infrastructure and orchestration layers.

## Partition components for independent team development

`id: ai-independent-team-development | category: architecture | severity: high | source: book (Ch.24) + editorial | languages: any | tags: teams, conways-law, components, ownership, development`

**Look for in a diff:**
- Multiple teams editing the same module for unrelated concerns
- Shared components with unclear ownership and frequent merge conflicts
- A boundary that forces teams to understand or release unrelated implementation details together

**Why it matters:** Architecture affects development throughput. Well-isolated components let teams work independently and reduce interference between different concerns and change schedules.

**Suggested comment:** "This boundary makes teams change the same module for unrelated responsibilities. Could ownership and component boundaries be aligned with independent work?"

**Fix:** Partition by cohesive responsibilities and define contracts/ownership that allow teams to develop and validate components independently.

## Keep components independently testable and developable

`id: ai-independent-component-work | category: architecture | severity: medium | source: book (Ch.24) + editorial | languages: any | tags: components, testing, development, dependencies, isolation`

**Look for in a diff:**
- A component requiring the whole system or unavailable infrastructure to build and test
- Tight compile-time or runtime coupling that prevents local iteration
- A new dependency that makes unrelated components part of every developer’s feedback loop

**Why it matters:** Independent development requires more than separate directories. Components need contracts, controlled dependencies, and a way to run meaningful tests without the entire system.

**Suggested comment:** "This component cannot be tested without starting the full system, so teams cannot work independently. Could the dependency be replaced by a contract double or isolated adapter?"

**Fix:** Define narrow contracts, provide fakes/test harnesses, and keep build/test dependencies aligned with the component’s actual responsibility.

## Make every build deployable with minimal manual work

`id: ai-deployable-after-build | category: delivery | severity: high | source: book (Ch.24) + editorial | languages: any | tags: deployment, automation, configuration, reproducibility, ci`

**Look for in a diff:**
- Manual directory creation, property editing, startup ordering, or environment repair required after a build
- Deployment steps that exist only in team knowledge
- A component that builds successfully but cannot be integrated or supervised automatically

**Why it matters:** Immediate deployment reduces integration risk and exposes broken boundaries early. Manual deployment choreography makes every release a bespoke operation.

**Suggested comment:** "This change adds a manual configuration/startup step not represented in the build or deployment process. Could the setup be automated and reproducible?"

**Fix:** Encode configuration, integration, startup, supervision, and health checks in versioned build/deployment automation.

## Isolate master/composition components from policy

`id: ai-composition-root-isolated | category: architecture | severity: medium | source: book (Ch.24) + editorial | languages: any | tags: composition-root, startup, integration, supervision, policy`

**Look for in a diff:**
- Application wiring and process supervision leaking into use-case modules
- Core policy deciding how components are started, connected, or monitored
- A deployment change requiring edits to business behavior

**Why it matters:** Composition components should tie the system together and supervise details without becoming owners of policy. Keeping the roles separate preserves both testability and deployment flexibility.

**Suggested comment:** "The use case now manages startup/integration concerns. Could wiring and supervision stay in the composition layer while the policy remains unaware of deployment?"

**Fix:** Concentrate construction, configuration, integration, and supervision in outer master components.

## Leave architectural options open deliberately

`id: ai-architecture-leaves-options-open | category: architecture | severity: medium | source: book (Ch.24) + editorial | languages: any | tags: options, changeability, architecture, uncertainty, decisions`

**Look for in a diff:**
- An early commitment to a framework, database, process model, or service topology without a current requirement
- Boundaries that make later operational or deployment changes prohibitively expensive
- “Future-proofing” layers added without a real option or experiment they enable

**Why it matters:** Requirements, operations, team structure, and deployment constraints change. A good architecture delays irrelevant decisions while keeping current behavior understandable.

**Suggested comment:** "This commits the system to a deployment/detail decision that the current use case does not require. Could the boundary preserve the option without adding speculative complexity?"

**Fix:** Identify which decisions are policy and which are details, defer the details behind real boundaries, and commit when evidence makes the choice necessary.
