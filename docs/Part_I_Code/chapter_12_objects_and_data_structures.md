# Clean Code, Chapter 12: Objects and Data Structures, PR review rules

## Choose objects or data structures based on what changes

`id: od-object-or-data | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: objects, data-structures, volatility, behavior, schema, design-choice`

**Look for in a diff:**
- A design that exposes mutable data while also pretending to encapsulate it
- A choice between objects and data structures made by convention rather than expected change
- Business behavior coupled to a representation likely to change
- A model that is difficult to extend in the direction the product actually changes

**Why it matters:** Objects hide data and expose behavior, which makes new data types easier to add. Data structures expose data and use procedures, which makes new behavior easier to add. Choose the boundary that protects the more stable side from the more volatile side.

**Suggested comment:** "This model hides behavior but exposes a representation that is likely to change. Which side—data shape or behavior—is expected to vary more?"

**Fix:** Make the volatility decision explicit and use either an object or a data structure consistently within the boundary.

## Hide representation behind behavior, not getters and setters

`id: od-abstract-data | category: encapsulation | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: data-abstraction, getters, setters, representation, interface, invariants, behavior`

**Look for in a diff:**
- Getters and setters that expose every field without expressing a domain operation
- Callers manipulating several fields independently to perform one logical update
- Public fields or accessors that reveal storage units, coordinate systems, or internal states
- Invariants enforced only by callers instead of the owning object

**Do not flag when:** a DTO or boundary object is intentionally a transparent data structure.

**Why it matters:** A layer of getters and setters does not hide implementation if callers still depend on the representation. An abstract interface lets the implementation change while preserving the policy and invariants.

**Suggested comment:** "Callers set these two fields independently even though they form one invariant. Could the object expose one operation that updates them atomically?"

**Fix:** Expose operations in domain terms, preserve invariants inside the owner, and keep representation details private.

## Keep objects responsible for their behavior

`id: od-object-responsibility | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: object-behavior, message-passing, tell-dont-ask, feature-envy, cohesion, responsibility`

**Look for in a diff:**
- A caller reading several fields and performing the object's business logic itself
- A class that contains data while another class owns all meaningful behavior for it
- Repeated calculations spread across callers instead of being owned by the relevant object
- Commands and queries used together to reconstruct an operation externally

**Why it matters:** Behavior should be located with the data and invariants it protects. Asking an object to perform an operation reduces knowledge of its internal representation and keeps responsibilities cohesive.

**Suggested comment:** "This caller reads the object's fields and calculates the result itself. Could the object expose the operation so its invariants stay in one place?"

**Fix:** Move behavior to the object that owns the relevant data, or use an explicit data-structure/procedure design instead of a confused hybrid.

## Do not create object/data-structure hybrids

`id: od-avoid-hybrids | category: design | severity: high | source: book (Ch.12) + editorial | languages: any | tags: hybrid, object, data-structure, getters, setters, feature-envy, muddled-design, encapsulation`

**Look for in a diff:**
- A class with substantial behavior plus public fields or representation-level accessors
- Callers using getters to manipulate the object as if it were a record
- Business rules split between the object and external procedures
- A design that is hard to extend with either new behaviors or new data types

**Why it matters:** Hybrids provide neither a clean object boundary nor a simple data structure. They spread responsibility and make future changes difficult in both directions.

**Suggested comment:** "This type exposes its fields while also owning behavior over them, so callers can bypass its rules. Could we make it a true data structure or hide the representation behind operations?"

**Fix:** Choose one model. Use a transparent DTO for data transfer, or hide data and expose behavior for a domain object.

## Keep data transfer objects simple and explicit

`id: od-dto-boundary | category: data-modeling | severity: low | source: book (Ch.12) + editorial | languages: any | tags: dto, data-transfer, boundary, serialization, database, message, public-fields`

**Look for in a diff:**
- A DTO containing business rules or side effects
- A transport object that exposes accidental persistence or domain details
- A bean with getters and setters that provides no abstraction beyond public fields
- Domain objects being used directly as wire or database representations without a deliberate boundary

**Why it matters:** DTOs are useful at database, message, and API boundaries because their purpose is to carry data. They should not be mistaken for domain objects or used to hide behavior that belongs elsewhere.

**Suggested comment:** "This response DTO now contains pricing behavior. Could the calculation remain in the domain model and leave this type as a transport structure?"

**Fix:** Keep DTO fields explicit, validate at the boundary, and translate between transport data and domain objects where their responsibilities differ.

## Keep callers from navigating object internals

`id: od-law-of-demeter | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: law-of-demeter, object-graph, friends, coupling, accessors, trainwreck`

**Look for in a diff:**
- A method calling through several returned objects
- Call chains that reveal the structure of a collaborator's collaborators
- Callers that know which nested object owns a value before performing an operation
- Accessor chains that become longer as the model evolves

**Do not flag when:** the values are intentionally transparent data structures and the chain is a clear data projection.

**Why it matters:** Knowledge of an object's internal object graph creates coupling. Changes to an intermediate object can force unrelated callers to change.

**Suggested comment:** "This caller knows that options contain a scratch directory and that the directory has a path. Could the owning object expose the operation the caller actually needs?"

**Fix:** Tell the relevant object what to do, pass an explicit collaborator, or use a transparent data structure consistently.

## Avoid trainwreck call chains

`id: od-trainwrecks | category: coupling | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: trainwreck, method-chain, nested-access, coupling, navigation, object-graph`

**Look for in a diff:**
- Chains such as `context.get_options().get_directory().get_path()` in business logic
- Repeated traversal of the same object graph in multiple callers
- A chain that mixes queries with commands or hides which object owns the result

**Why it matters:** Splitting a chain into local variables may improve readability but does not remove the coupling. The real issue is whether the caller should know the intermediate structure at all.

**Suggested comment:** "Naming each link makes this easier to read, but the caller still depends on three internal relationships. Could `context` provide the operation directly?"

**Fix:** Expose a meaningful operation on the owning object, or document the structure as an intentional data-transfer shape.

## Tell objects what to do instead of asking for internals

`id: od-tell-other-guy | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: tell-dont-ask, message-passing, command-query-separation, encapsulation, behavior`

**Look for in a diff:**
- A caller collecting fields only to perform an operation on behalf of another object
- File, cache, transaction, or validation details assembled outside their owner
- A new accessor added solely to enable external manipulation

**Why it matters:** The operation's owner has the best knowledge of its invariants and implementation. Telling it to perform the operation keeps details behind the boundary and reduces caller knowledge.

**Suggested comment:** "The caller only wants a scratch stream, but it constructs the path from internal details. Could the context object create the stream itself?"

**Fix:** Add a domain-level command to the owner, keeping queries for genuine data needs and commands for behavior.

## Put behavior where adding the next change is cheapest

`id: od-procedural-vs-object | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: procedural, polymorphism, objects, functions, extension-axis, volatility, shapes`

**Look for in a diff:**
- A new type requiring edits to every function that handles existing types
- A new operation requiring edits to every existing type
- A polymorphic design introduced even though behavior is the volatile axis
- A procedural design retained even though data types are frequently added

**Why it matters:** Procedural data structures make new operations easier but new data types harder. Objects and polymorphism make new data types easier but new operations harder. The right choice depends on the expected direction of change.

**Suggested comment:** "This abstraction is optimized for adding new shapes, but the requirements mainly add new operations. Could a data-oriented design reduce the number of existing types that change?"

**Fix:** Identify the likely extension axis and choose the representation that isolates that change.

## Keep switch statements at the change boundary

`id: od-switch-boundary | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: switch, if-else, type-code, polymorphism, ocp, rigid, fragile, boundary`

**Look for in a diff:**
- The same switch on a type code repeated across many methods
- Adding one variant requiring edits in many modules
- Type-specific behavior spread across a central manager
- A switch placed in core policy instead of at an input or composition boundary

**Do not flag when:** the switch is at the system edge, handles a small stable set, or behavior is clearly more volatile than the data types.

**Why it matters:** Repeated switches make a design rigid and fragile. A new type can require many edits, and missing one case can create inconsistent behavior.

**Suggested comment:** "Adding a new shape requires updating several switches. Could the boundary create a polymorphic shape and let the rest of the system use its interface?"

**Fix:** Move switches to the periphery, keep one controlled creation point, or use polymorphism when new types are the expected change.

## Use polymorphism when new data types are the expected change

`id: od-polymorphic-extension | category: design | severity: medium | source: book (Ch.12) + editorial | languages: any | tags: polymorphism, ocp, dip, plugin, independent-deployment, extension`

**Look for in a diff:**
- A central manager accumulating type-specific cases
- New implementations that require changing stable high-level behavior
- Concrete variants bundled into a component that should be independently deployable
- Domain operations that belong naturally to each type

**Why it matters:** Polymorphism can isolate new data types and allow implementations to be added without changing existing clients. It is valuable when the system is expected to grow by adding types.

**Suggested comment:** "The manager changes for every new shape. Could `Shape` own the operation so new shapes can be added without modifying the manager?"

**Fix:** Define a focused interface, implement behavior in each type, and instantiate implementations at the boundary.

## Do not force polymorphism when new operations are the volatile axis

`id: od-polymorphism-tradeoff | category: review-guidance | severity: low | source: book (Ch.12) + editorial | languages: any | tags: tradeoff, polymorphism, procedural, visitor, operations, performance, context`

**Look for in a diff:**
- A large hierarchy created for a small stable set of data types
- Every new operation requiring edits to every class in the hierarchy
- A procedural design rejected solely because it is not object-oriented

**Why it matters:** Every design makes some changes easier and others harder. Object-oriented designs favor new data types; procedural designs favor new operations over stable data. Mature design chooses based on actual change pressure.

**Suggested comment:** "Before adding this hierarchy, which is more likely to change: the data types or the operations? The answer should determine the extension strategy."

**Fix:** Choose the design that protects the stable axis and measure performance before trading away clarity.

## Optimize dispatch only with evidence

`id: od-profile-dispatch | category: performance | severity: low | source: book (Ch.12) + editorial | languages: any | tags: performance, polymorphic-dispatch, switch, profiling, premature-optimization, hot-path`

**Look for in a diff:**
- Readable polymorphism removed for an unmeasured performance claim
- Switch statements spread across the system to save a few dispatch costs
- Architecture made harder to change without a profile or benchmark

**Why it matters:** A switch may be faster than polymorphic dispatch in a hot loop, but that difference is irrelevant in most code. Localize measured optimizations instead of weakening the whole design.

**Suggested comment:** "Do we have a profile showing dispatch is the bottleneck? Without measurement, the clearer extension boundary is safer."

**Fix:** Profile first, optimize only the measured hot path, and preserve the broader design boundary.
