# Clean Code, Chapter 20: Component Principles, PR review rules

## Treat components as independently deployable boundaries

`id: cp-independent-deployment-boundary | category: architecture | severity: high | source: book (Ch.20) + editorial | languages: any | tags: components, deployment, releases, modules, ownership`

**Look for in a diff:**
- A component that cannot be built, tested, versioned, or deployed without unrelated components
- Internal details of one deployable unit leaking into another
- A new component boundary with no clear ownership, release contract, or reason for independent deployment

**Why it matters:** Components are units of deployment and development. A boundary is useful when teams can change and release it without coordinating every internal detail with the whole system.

**Suggested comment:** "This component boundary does not appear independently buildable or releasable because it relies on internal details of another unit. Could the contract and ownership be made explicit?"

**Fix:** Define a stable public contract, isolate implementation details, and ensure the component can be developed, tested, versioned, and released predictably.

## Group reusable code by a coherent release theme

`id: cp-reuse-release-equivalence | category: component-design | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: rep, reuse, release, versioning, cohesion`

**Look for in a diff:**
- Unrelated modules bundled into one reusable package
- A package reused by consumers that cannot adopt its changes independently
- A release lacking versioning, compatibility notes, or a clear shared purpose

**Why it matters:** The unit that users reuse should be the unit they can track and release. A coherent release group lets consumers make informed upgrade decisions.

**Suggested comment:** "This package combines unrelated capabilities that consumers will need to version independently. Could the release boundary follow a coherent reusable concept?"

**Fix:** Group modules that share a reusable abstraction and release lifecycle; split unrelated capabilities into separately versioned components.

## Collocate code that changes for the same reason

`id: cp-common-closure | category: component-design | severity: high | source: book (Ch.20) + editorial | languages: any | tags: ccp, common-closure, change-reasons, cohesion, deployment`

**Look for in a diff:**
- A requirement change spread across many components that should evolve together
- Classes owned by one stakeholder or policy scattered across release units
- A component containing features with unrelated reasons or schedules for change

**Why it matters:** The Common Closure Principle localizes change so one requirement can be implemented, validated, and deployed with minimal collateral work.

**Suggested comment:** "This policy change requires coordinated edits across several components that always change together. Could the cohesive implementation move into one release boundary?"

**Fix:** Group code with shared change pressure and separate code that changes for different actors, schedules, or volatility.

## Keep volatility aligned within a component

`id: cp-align-component-volatility | category: component-design | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: ccp, volatility, releases, cohesion, maintainability`

**Look for in a diff:**
- Highly volatile features bundled with stable policies
- A minor cosmetic change forcing validation or release of unrelated critical code
- Low- and high-frequency changes sharing one deployment unit without a reason

**Why it matters:** Mixed volatility increases release cost and makes stable code appear risky to change. Component boundaries should reflect how often and why code evolves.

**Suggested comment:** "This fast-changing integration now ships with a stable core policy, so small updates will trigger broad validation. Could the volatility boundary be separated?"

**Fix:** Separate components with materially different change frequency or release urgency, unless their shared closure clearly outweighs the cost.

## Group modules that are reused together

`id: cp-common-reuse | category: component-design | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: crp, reuse, modules, cohesion, coupling`

**Look for in a diff:**
- A reusable type split from the helpers, iterators, codecs, or policies it always requires
- Consumers forced to assemble an incomplete abstraction from several packages
- A package containing modules that are rarely used together

**Why it matters:** The Common Reuse Principle keeps inseparable reusable abstractions together while avoiding packages that impose unrelated dependency baggage.

**Suggested comment:** "Consumers of this abstraction must also import these tightly coupled helpers. Could the reusable unit be packaged together, or should the helpers be made independent?"

**Fix:** Package modules that are normally reused together and separate modules that consumers can use independently.

## Do not make consumers depend on unused modules

`id: cp-avoid-unused-component-dependencies | category: component-design | severity: high | source: book (Ch.20) + editorial | languages: any | tags: crp, dependencies, packaging, rebuilds, deployment`

**Look for in a diff:**
- A client importing a package for one small capability while inheriting many unrelated modules
- Unused package changes forcing recompilation, redeployment, or compatibility review
- A broad component dependency where a focused component or port would suffice

**Why it matters:** Depending on a component means accepting its release and failure surface, even when the client uses only one module. Unused baggage increases coupling and deployment work.

**Suggested comment:** "This client uses one capability but depends on the whole broad component. Could a smaller package or interface avoid unrelated release and failure coupling?"

**Fix:** Split unrelated modules or expose a focused component boundary; keep tightly coupled reusable modules together only when consumers need them together.

## Balance reuse, closure, and release cost

`id: cp-balance-cohesion-for-context | category: component-design | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: rep, ccp, crp, tradeoffs, evolution, architecture`

**Look for in a diff:**
- A component split that improves reuse but causes routine changes across many releases
- A monolithic component retained solely for reuse despite unrelated change schedules
- A component structure treated as permanent before the system’s use and maturity are known

**Why it matters:** REP, CCP, and CRP pull component boundaries in different directions. The right balance depends on whether the current priority is development speed, release isolation, or reuse.

**Suggested comment:** "This boundary optimizes reuse but makes ordinary changes cross several releases. Which current cost are we optimizing, and can the structure evolve as usage changes?"

**Fix:** Choose boundaries based on actual change, reuse, and release pressure; revisit them incrementally as the system and consumers mature.

## Evolve component boundaries incrementally

`id: cp-evolve-component-structure | category: architecture | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: architecture, refactoring, components, incremental, change-pressure`

**Look for in a diff:**
- A speculative component architecture designed before responsibilities and reuse are known
- A large one-time split with no migration or release plan
- Component boundaries left unchanged despite repeated evidence of coupling or deployment pain

**Why it matters:** Component cohesion becomes clearer through real changes and reuse. Small frequent adjustments are safer than trying to predict the final structure upfront.

**Suggested comment:** "The boundary is based on a future usage assumption rather than current change pressure. Could we make the smallest change now and defer further splitting until reuse or release evidence appears?"

**Fix:** Use observed dependencies and release pain to guide small boundary refactors, keeping migration and compatibility explicit.

## Keep the component dependency graph acyclic

`id: cp-acyclic-dependencies | category: architecture | severity: high | source: book (Ch.20) + editorial | languages: any | tags: adp, dependency-graph, cycles, build-order, components`

**Look for in a diff:**
- A new dependency path that leads back to the originating component
- Components that cannot be built, tested, or released in a valid order
- A package cycle forcing unrelated teams to coordinate every change

**Why it matters:** Cycles collapse multiple components into one change unit, complicate build order, and create the morning-after problem where another team’s change unexpectedly breaks local work.

**Suggested comment:** "This dependency creates a cycle between the components, so they can no longer be built and released independently. Could the dependency be inverted or moved to a shared component?"

**Fix:** Keep the graph a DAG; break cycles with dependency inversion or an extracted component containing the shared stable contract.

## Break cycles with dependency inversion or a shared component

`id: cp-break-cycles-deliberately | category: architecture | severity: high | source: book (Ch.20) + editorial | languages: any | tags: adp, dip, cycles, interfaces, shared-component`

**Look for in a diff:**
- A cycle resolved by duplicating unstable implementation details
- A shared module extracted without a focused contract or ownership
- An interface placed in the wrong component, leaving the original cycle intact

**Why it matters:** Breaking a cycle should restore independent build and release paths. A policy-level interface or genuinely shared stable component prevents the cycle without merging unrelated implementation.

**Suggested comment:** "The extracted module breaks the build cycle syntactically but still contains volatile implementation details. Could the shared boundary contain only the contract both sides need?"

**Fix:** Invert the dependency at the stable policy boundary or extract the minimal shared abstraction, then verify the graph has no cycle.

## Depend toward stable components

`id: cp-stable-dependencies | category: architecture | severity: high | source: book (Ch.20) + editorial | languages: any | tags: sdp, stability, fan-in, fan-out, volatility, dependencies`

**Look for in a diff:**
- A difficult-to-change component depending on a highly volatile component
- A stable component gaining a dependency on a feature that changes frequently
- Stable policy exposed to the release schedule of an unstable integration

**Why it matters:** The Stable Dependencies Principle prevents volatile components from becoming hard to change through incoming dependencies. Dependency direction should reduce instability toward the protected core.

**Suggested comment:** "The stable component now depends on this frequently changing integration, so its changes will require broader coordination. Could the dependency point through a stable boundary?"

**Fix:** Invert the dependency, move the contract to a stable component, or redesign the ownership so volatility remains isolated.

## Use fan-in and fan-out as diagnostic signals

`id: cp-use-stability-signals | category: architecture | severity: low | source: book (Ch.20) + editorial | languages: any | tags: sdp, fan-in, fan-out, instability, metrics, architecture`

**Look for in a diff:**
- A component with many incoming dependencies and many outgoing volatile dependencies
- A proposed boundary whose stability is assumed but not reflected in its dependency graph
- Metrics presented as a pass/fail rule without considering volatility and ownership

**Why it matters:** Fan-in, fan-out, and instability help reveal whether a component is exposed to too many reasons to change. They are design signals, not a replacement for understanding actual change pressure.

**Suggested comment:** "This component has many dependents but also depends on several volatile details. Could we review whether it is a stable policy boundary or an accidental coupling hub?"

**Fix:** Inspect incoming and outgoing coupling, isolate volatile dependencies, and use metrics to focus design review rather than enforce arbitrary thresholds.

## Make stable components appropriately abstract

`id: cp-stable-abstractions | category: architecture | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: sap, abstractness, stability, policy, extension`

**Look for in a diff:**
- A stable component containing rigid concrete policy that cannot be extended safely
- An abstract interface added with no implementation or client
- High-level policy forced to depend on concrete lower-level details

**Do not flag when:** the concrete component is a stable platform facility or the abstraction would be unused speculative structure.

**Why it matters:** Stable high-level components need extension points so their stability does not make the architecture rigid. Conversely, unused abstractions add complexity without flexibility.

**Suggested comment:** "This stable policy is difficult to extend because its concrete details are fixed in the component. Is there a real variation that warrants a focused abstraction?"

**Fix:** Place meaningful policy interfaces in stable components, keep implementations in volatile components, and remove abstract types with no real consumer.

## Treat zone-of-pain and zone-of-uselessness as review signals

`id: cp-review-exclusion-zones | category: architecture | severity: medium | source: book (Ch.20) + editorial | languages: any | tags: architecture, stability, abstractness, rigidity, uselessness, metrics`

**Look for in a diff:**
- A volatile concrete component with many dependents and no extension boundary
- An interface-heavy component with no meaningful clients or implementations
- Metrics used to justify a refactor without identifying real release or change pain

**Do not flag when:** the concrete component is intentionally stable infrastructure or the abstract boundary is a valid published contract awaiting an implementation in a staged migration.

**Why it matters:** Highly stable concrete components can become rigid, while highly abstract unused components become architectural debris. Both are warnings to investigate, not automatic violations.

**Suggested comment:** "This boundary looks both hard to change and concrete, or abstract but unused. What actual change/reuse pressure justifies its current position?"

**Fix:** Protect volatile concrete details behind stable contracts, remove unused abstractions, and evaluate component structure with real dependency and release evidence.
