# Clean Code, Chapter 29: No Defect in Behavior or Structure, PR review rules

## Review both behavior and structure before calling a change done

`id: ns-review-behavior-and-structure | category: review-guidance | severity: high | source: book (Ch.29) + editorial | languages: any | tags: behavior, structure, done, quality, review`

**Look for in a diff:**
- Functional behavior that passes while responsibilities, dependencies, or readability degrade
- “It works” used as the end of review with no structural assessment
- Structural cleanup that accidentally changes the requested behavior

**Why it matters:** Behavior provides immediate value; structure determines whether the system can continue to deliver value as requirements change. Both are part of completion.

**Suggested comment:** "The behavior is covered, but the change leaves a structural defect that will make the next change harder. Could we address this boundary/duplication before marking the work complete?"

**Fix:** Verify outcomes, then review cohesion, dependency direction, testability, and maintainability before moving on.

## Refactor after making the smallest behavior pass

`id: ns-red-green-refactor | category: process | severity: high | source: book (Ch.29) + editorial | languages: any | tags: tdd, red-green-refactor, tests, refactoring, feedback`

**Look for in a diff:**
- A test made to pass followed immediately by unrelated feature work with known messy structure
- Refactoring postponed until several behaviors are piled onto the same unclear design
- Structural changes made without a passing behavioral safety net

**Why it matters:** Small red-green-refactor cycles keep behavior and structure aligned. They make cleanup cheap and prevent temporary implementation choices from becoming permanent coupling.

**Suggested comment:** "The new test passes, but the implementation is still a difficult first draft. Could we refactor under this test before adding the next behavior?"

**Fix:** Make one test pass, refactor for clarity/cohesion/duplication, then proceed to the next behavior.

## Prevent rigidity from small changes causing broad releases

`id: ns-prevent-rigidity | category: architecture | severity: high | source: book (Ch.29) + editorial | languages: any | tags: rigidity, dependencies, components, deployment, coupling`

**Look for in a diff:**
- A small feature requiring rebuild/redeployment of many unrelated modules
- New dependencies from stable components to volatile implementation details
- Shared configuration or package structure forcing broad release coordination

**Why it matters:** Rigidity means the effort to integrate or deploy a change is much larger than the change itself. It slows delivery and increases release risk.

**Suggested comment:** "This small change now requires several unrelated components to rebuild/release. Could the dependency or deployment boundary be narrowed?"

**Fix:** Isolate volatile details, split release units by change reason, and invert dependencies where stable components are exposed.

## Prevent fragility from behavior changes rippling across modules

`id: ns-prevent-fragility | category: architecture | severity: high | source: book (Ch.29) + editorial | languages: any | tags: fragility, coupling, regression, contracts, dependencies`

**Look for in a diff:**
- A local behavior change requiring edits to many callers or tests for incidental reasons
- Shared data/flags whose meaning is interpreted differently across modules
- A change that can silently alter unrelated behavior through hidden coupling

**Why it matters:** Fragility makes small behavior changes dangerous and creates a high chance of silently breaking other paths.

**Suggested comment:** "Changing this rule requires updating many modules because they depend on its implementation details. Could the contract be narrowed or the shared policy centralized?"

**Fix:** Define stable contracts, reduce shared mutable knowledge, and add regression tests for each affected behavior.

## Prevent immobility by keeping reusable behavior extractable

`id: ns-prevent-immobility | category: design | severity: medium | source: book (Ch.29) + editorial | languages: any | tags: immobility, reuse, cohesion, extraction, coupling`

**Look for in a diff:**
- Useful behavior tied to unrelated application state, framework lifecycle, or global configuration
- A module that cannot be reused without importing an entire application subsystem
- Extraction blocked by tangled dependencies and hidden side effects

**Why it matters:** Immobility means valuable behavior cannot be reused elsewhere because it is too entangled with its original context.

**Suggested comment:** "This useful calculation is tied to application/global state, so it cannot be reused or tested independently. Could its inputs and dependencies be made explicit?"

**Fix:** Separate cohesive behavior, inject dependencies, remove hidden side effects, and expose a stable reusable contract.

## Keep source and data dependencies intentional

`id: ns-manage-dependencies | category: architecture | severity: high | source: book (Ch.29) + editorial | languages: any | tags: dependencies, solid, architecture, data, structure`

**Look for in a diff:**
- New imports or data references crossing ownership boundaries without review
- A shared model changed to satisfy one consumer while affecting unrelated consumers
- High-level code depending on volatile concrete details

**Why it matters:** Rigidity, fragility, and immobility are usually dependency problems. Managing source and data dependencies is the practical way to preserve a valuable structure.

**Suggested comment:** "This dependency ties the policy to a volatile detail/shared representation. Could the contract or data boundary prevent unrelated changes from propagating?"

**Fix:** Apply cohesion, dependency inversion, encapsulation, and component principles to keep change localized.

## Do not accumulate known structural defects

`id: ns-no-known-structural-defects | category: maintainability | severity: high | source: book (Ch.29) + editorial | languages: any | tags: technical-debt, cleanup, defects, maintainability, ownership`

**Look for in a diff:**
- New behavior knowingly layered onto duplicated, tangled, or untestable code
- A structural issue identified in review but repeatedly deferred without a plan
- Temporary shortcuts lacking an owner, risk note, or removal condition

**Why it matters:** Known structural defects compound. Each new behavior built on them raises the cost and risk of every later change.

**Suggested comment:** "This adds behavior on top of a known structural defect, increasing the cost of the next change. Could we fix the local issue first or record an explicit bounded follow-up?"

**Fix:** Refactor before extending when practical; otherwise isolate the shortcut, document the risk, and schedule a concrete cleanup.

## Prioritize important structural work over ordinary urgency

`id: ns-urgency-does-not-erase-structure | category: process | severity: medium | source: book (Ch.29) + editorial | languages: any | tags: urgency, prioritization, structure, tradeoffs, risk`

**Look for in a diff:**
- Normal schedule pressure used to justify permanent structural damage
- Important cleanup repeatedly deferred for the next feature
- A genuine emergency treated as permission to leave the emergency workaround indefinitely

**Do not flag when:** a real incident requires a temporary containment and the team has documented its risk, rollback, and cleanup plan.

**Why it matters:** Urgent work is short-term; structure affects every future change. Treating all deadlines as emergencies creates a compounding productivity and reliability problem.

**Suggested comment:** "This shortcut may be justified for the immediate deadline, but it needs a cleanup/rollback commitment so the urgent fix does not become permanent structural debt."

**Fix:** Distinguish true emergencies from normal urgency, preserve the smallest safe structure, and address deferred cleanup before adding more behavior.

## Treat developers as responsible stakeholders in structure

`id: ns-engineer-owns-structure | category: professional-responsibility | severity: high | source: book (Ch.29) + editorial | languages: any | tags: ownership, engineering, design, escalation, quality`

**Look for in a diff:**
- Technical risks hidden because requirements owners cannot see structural consequences
- A developer accepting a design known to make future changes unsafe without raising it
- No engineering rationale for a compromise that affects maintainability or release risk

**Why it matters:** Engineers are accountable for how the system is built, not only for translating instructions into code. Stakeholders need clear tradeoffs to make informed delivery decisions.

**Suggested comment:** "This design tradeoff affects future change cost and release risk. Could the engineering impact be documented so the decision is explicit?"

**Fix:** Communicate structural risks, propose safer alternatives, and make informed compromises visible to the decision-makers.
