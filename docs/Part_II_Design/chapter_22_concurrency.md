# Clean Code, Chapter 22: Concurrency, PR review rules

## Justify concurrency with a concrete throughput or structure need

`id: cc-justify-concurrency | category: concurrency | severity: high | source: book (Ch.22) + editorial | languages: any | tags: concurrency, throughput, latency, complexity, design`

**Look for in a diff:**
- Threads, tasks, or async code added without a measurable latency/throughput need
- Concurrency used where sequential processing would be simpler and sufficient
- A claim that concurrency automatically improves performance

**Why it matters:** Concurrency adds scheduling, synchronization, testing, and operational complexity. It helps when work can overlap or when decoupling “what” from “when” improves the design, but it is not free performance.

**Suggested comment:** "What latency/throughput or structural requirement needs concurrency here? Could the simpler sequential design meet the requirement with lower failure risk?"

**Fix:** Establish the performance or decoupling need, measure the baseline, and introduce the smallest concurrency model that addresses it.

## Separate concurrency mechanics from application policy

`id: cc-separate-concurrency-responsibility | category: architecture | severity: high | source: book (Ch.22) + editorial | languages: any | tags: concurrency, srp, threads, scheduling, policy`

**Look for in a diff:**
- Business rules mixed with thread creation, locks, queues, retries, or cancellation
- A class that both computes results and coordinates worker lifecycle
- Concurrency changes requiring edits throughout otherwise sequential domain code

**Why it matters:** Concurrency has its own design, tuning, and failure lifecycle. Isolating it keeps the application behavior testable and limits the surface where scheduling defects can occur.

**Suggested comment:** "This method mixes the business calculation with executor/lock management. Could the policy run in a thread-agnostic module and leave scheduling to a focused coordinator?"

**Fix:** Separate thread-aware orchestration from thread-ignorant behavior and define a clear handoff between them.

## Minimize shared mutable state

`id: cc-limit-shared-state | category: concurrency | severity: critical | source: book (Ch.22) + editorial | languages: any | tags: shared-state, race-condition, encapsulation, mutation, thread-safety`

**Look for in a diff:**
- Multiple threads reading and writing the same mutable field
- Shared collections or caches updated from several paths
- Mutable state exposed publicly or passed through many layers

**Why it matters:** Every shared write creates possible interleavings, races, and hidden invariants. Limiting access reduces the number of places that must be synchronized and makes failures diagnosable.

**Suggested comment:** "This mutable state is shared across worker paths and can be updated from several places. Could ownership be narrowed or the state made immutable/isolated?"

**Fix:** Encapsulate shared data, reduce writers, prefer immutable values, and centralize any required synchronization.

## Prefer copies, immutable values, or single-owner state

`id: cc-avoid-sharing-by-copy | category: concurrency | severity: high | source: book (Ch.22) + editorial | languages: any | tags: immutability, copies, ownership, synchronization, functional`

**Look for in a diff:**
- Workers sharing mutable objects when each could operate on a snapshot
- Results merged concurrently when a single owner could merge them safely
- Locks added around state that could be copied or treated as read-only

**Do not flag when:** copying is demonstrably too expensive and the shared ownership protocol is explicit, bounded, and tested.

**Why it matters:** Avoiding shared mutation often removes the need for locks and makes execution easier to reason about. The cost of copying should be measured against synchronization and failure complexity.

**Suggested comment:** "These workers mutate the same object even though each appears to need only a snapshot. Could they process copies and merge results in one controlled owner?"

**Fix:** Use immutable snapshots, thread-local data, message passing, or a single merge point where feasible.

## Design workers to be independent where possible

`id: cc-independent-workers | category: concurrency | severity: high | source: book (Ch.22) + editorial | languages: any | tags: workers, partitioning, isolation, parallelism, data`

**Look for in a diff:**
- Workers coordinating through incidental shared fields
- Data partitions that overlap without an explicit ownership rule
- One worker’s progress or failure unexpectedly corrupting another worker’s result

**Why it matters:** Independent workers require less synchronization and can often be tested and scaled separately. Partitioning data and responsibility reduces race opportunities.

**Suggested comment:** "These workers overlap on mutable state rather than owning independent partitions. Could the work/data be partitioned so each worker behaves independently?"

**Fix:** Partition inputs and state, pass required data explicitly, and define a controlled result-merge or coordination step.

## Use thread-safe libraries and know their guarantees

`id: cc-use-proven-threading-primitives | category: concurrency | severity: high | source: book (Ch.22) + editorial | languages: any | tags: thread-safe, collections, executors, libraries, guarantees`

**Look for in a diff:**
- A custom queue, pool, atomic operation, or lock protocol replacing a proven library primitive
- A collection assumed to be thread-safe without documentation
- A library call whose compound operations are not atomic as used

**Why it matters:** Concurrency primitives encode difficult memory and scheduling guarantees. Reimplementing them or assuming stronger guarantees than documented creates subtle defects.

**Suggested comment:** "The code assumes this collection/operation is safe across threads, but its compound update is not atomic. Could a documented concurrent primitive or explicit synchronization be used?"

**Fix:** Use the language’s concurrency utilities, verify their guarantees, and keep compound operations inside the correct synchronization boundary.

## Choose and document the execution model

`id: cc-explicit-execution-model | category: concurrency | severity: high | source: book (Ch.22) + editorial | languages: any | tags: producer-consumer, readers-writers, queues, scheduling, model`

**Look for in a diff:**
- A queue, pool, or lock protocol with no stated ownership, backpressure, or completion semantics
- Producer/consumer code with unbounded buffers or unclear shutdown behavior
- Readers/writers coordination with no starvation or freshness policy

**Why it matters:** Common models have known failure modes. Naming the model exposes the required constraints around capacity, fairness, ordering, and completion.

**Suggested comment:** "This queue behaves like producer/consumer but has no capacity or shutdown policy. Could the execution model and backpressure semantics be made explicit?"

**Fix:** Document the model, bounds, ownership, ordering, cancellation, fairness, and error propagation rules; test each invariant.

## Prevent deadlock, livelock, and starvation

`id: cc-prevent-lock-pathologies | category: concurrency | severity: critical | source: book (Ch.22) + editorial | languages: any | tags: deadlock, livelock, starvation, locks, ordering, resources`

**Look for in a diff:**
- Multiple locks acquired in inconsistent order
- Threads waiting while holding resources needed by other threads
- Retry/yield loops that can make no progress or starve one class of work
- Resource acquisition patterns analogous to dining philosophers

**Why it matters:** Concurrent failures can appear only under rare schedules and may halt or degrade the system without a normal exception. Resource ordering and bounded waits are essential defenses.

**Suggested comment:** "This path acquires resources in a different order and can deadlock with the other path. Could lock ordering or a single ownership protocol prevent the cycle?"

**Fix:** Establish a global acquisition order, minimize simultaneous resources, use timeouts/cancellation where appropriate, and test progress and fairness.

## Avoid multi-call protocols on synchronized objects

`id: cc-atomic-client-operation | category: concurrency | severity: critical | source: book (Ch.22) + editorial | languages: any | tags: synchronization, atomicity, locks, race-condition, api`

**Look for in a diff:**
- A client calling two or more individually synchronized methods as one logical operation
- Check-then-act sequences split across public methods
- A lock held by one method released before the next required method runs

**Why it matters:** Method-level synchronization does not make a multi-method protocol atomic. Another thread can change state between calls and violate the client’s assumptions.

**Suggested comment:** "These two synchronized calls form one check-and-update operation, but another thread can interleave between them. Could the atomic operation move behind the server boundary?"

**Fix:** Provide one server-side atomic method, use a documented client lock, or add an adapter that owns the complete synchronization protocol.

## Keep critical sections minimal and complete

`id: cc-small-complete-critical-sections | category: concurrency | severity: high | source: book (Ch.22) + editorial | languages: any | tags: critical-section, locks, contention, atomicity, performance`

**Look for in a diff:**
- Locks held across I/O, callbacks, slow computation, or unrelated work
- Shared invariants updated outside the lock that protects related fields
- Large synchronized blocks added as a blanket fix

**Why it matters:** Critical sections must contain the entire invariant-preserving operation, but unnecessary work inside them increases contention and deadlock risk.

**Suggested comment:** "The lock covers network/work that does not require shared state, increasing contention. Could the critical section be reduced while keeping the state transition atomic?"

**Fix:** Identify the invariant, lock only the required state transition, and perform slow/external work outside the lock.

## Design startup and shutdown as explicit protocols

`id: cc-lifecycle-protocol | category: concurrency | severity: critical | source: book (Ch.22) + editorial | languages: any | tags: startup, shutdown, cancellation, lifecycle, deadlock, resources`

**Look for in a diff:**
- Workers started without readiness/error reporting or stopped without cancellation
- Parent threads waiting forever for children that are blocked on queues or signals
- Shutdown paths that can drop work, leak resources, or deadlock

**Why it matters:** Lifecycle boundaries contain distinct concurrency hazards. A system that works while running can still hang or corrupt state during startup, cancellation, and shutdown.

**Suggested comment:** "The shutdown signal cannot reach a consumer blocked on this queue, so the parent may wait forever. Could cancellation, queue closure, and worker completion be designed as one protocol?"

**Fix:** Define startup readiness, failure propagation, cancellation, queue closure, draining, joining, and resource-release behavior; test each path.

## Make concurrent code pluggable and tunable

`id: cc-pluggable-tunable-concurrency | category: testing | severity: high | source: book (Ch.22) + editorial | languages: any | tags: concurrency, executors, test-doubles, configuration, tuning, load`

**Look for in a diff:**
- Thread counts, timing, and dependencies hard-coded into production logic
- No way to run the same behavior sequentially, with a fake, or with varied worker counts
- Performance tuning requiring source changes rather than configuration

**Why it matters:** Pluggable execution makes concurrency testable and allows throughput/latency tradeoffs to be measured. Tunability is necessary because the correct configuration depends on workload and environment.

**Suggested comment:** "The worker count and timing are fixed inside the policy, preventing sequential/fake stress tests and tuning. Could execution configuration be injected?"

**Fix:** Inject executors, clocks, schedulers, and test doubles; make worker counts and relevant limits configurable and observable.

## Test non-threaded behavior before threaded behavior

`id: cc-test-sequential-core-first | category: testing | severity: medium | source: book (Ch.22) + editorial | languages: any | tags: concurrency, unit-tests, sequential, isolation, debugging`

**Look for in a diff:**
- Threading introduced before the underlying calculation or state transition has focused tests
- Failures that could be ordinary logic bugs but are debugged only under concurrency
- Thread-aware modules containing all application logic

**Why it matters:** Separating and testing sequential behavior first reduces the space of possible causes. Concurrency tests can then focus on scheduling and shared-state guarantees.

**Suggested comment:** "This failure could be in the calculation itself or in scheduling. Could the thread-agnostic module be tested sequentially before adding concurrency coverage?"

**Fix:** Extract pure/sequential behavior, test it directly, then test the coordinator’s concurrency contract separately.

## Treat every intermittent failure as a real defect candidate

`id: cc-investigate-intermittent-failures | category: testing | severity: critical | source: book (Ch.22) + editorial | languages: any | tags: concurrency, flaky-tests, race-condition, diagnostics, reliability`

**Look for in a diff:**
- A flaky or one-off failure ignored because the next run passed
- Retries added without capturing schedule, load, platform, or state information
- Tests marked flaky instead of investigating possible races or lifecycle defects

**Why it matters:** Concurrency defects are often rare and non-repeatable. Ignoring a single failure allows a real race to reach production and makes later diagnosis harder.

**Suggested comment:** "This intermittent failure may indicate a race rather than noise. Could we preserve the failure context and investigate before adding a retry or suppression?"

**Fix:** Treat one-offs as evidence, capture diagnostics, reproduce under controlled stress, and fix or explicitly document the concurrency invariant.

## Stress concurrent code across schedules and environments

`id: cc-stress-schedules-platforms | category: testing | severity: high | source: book (Ch.22) + editorial | languages: any | tags: concurrency, stress, platforms, scheduling, load, race-condition`

**Look for in a diff:**
- Concurrency tests run once with one worker count and one platform
- No load above processor count or variation in timing/scheduling
- Tests that cannot repeat the operation many times under different configurations

**Why it matters:** Correctness depends on execution order, load, runtime, and platform behavior. Varied schedules increase the chance of exposing missing synchronization and lifecycle defects.

**Suggested comment:** "This concurrency test uses one schedule and one worker count, so rare interleavings remain untested. Could it run repeatedly with varied load, timing, and target platforms?"

**Fix:** Run repeated stress tests with varied worker counts, delays, processor pressure, platforms, and dependency speeds.

## Instrument scheduling to expose hidden races

`id: cc-schedule-instrumentation | category: testing | severity: high | source: book (Ch.22) + editorial | languages: any | tags: concurrency, instrumentation, yield, scheduling, jiggling, test-hooks`

**Look for in a diff:**
- A race-prone section with no way to force alternate interleavings
- Sleep/yield calls permanently left in production paths
- Instrumentation that cannot be enabled, varied, or disabled safely for tests

**Why it matters:** Many schedules are unlikely in normal runs. Controlled delays, yields, or scheduler hooks can make broken interleavings occur frequently enough to diagnose.

**Suggested comment:** "The race window is difficult to exercise naturally. Could test-only scheduling hooks vary the interleaving without adding production sleeps or timing assumptions?"

**Fix:** Add pluggable test instrumentation or deterministic scheduling controls, keep them disabled in production, and run the affected tests repeatedly.

## Choose a data-integrity strategy for concurrent updates

`id: cc-explicit-shared-data-strategy | category: data-integrity | severity: critical | source: book (Ch.22) + editorial | languages: any | tags: shared-data, transactions, locking, consistency, idempotency`

**Look for in a diff:**
- Concurrent check-then-write operations against eventually consistent or shared storage
- Duplicate assignments, lost updates, double deletes, or invalid resource counts
- A system requiring strict uniqueness but relying on timing or client cooperation

**Why it matters:** Shared-data problems need an explicit strategy: transaction/lock, serialized processing, idempotency, conflict detection, or deliberate acceptance of recoverable duplicates.

**Suggested comment:** "Two clients can observe the same available state before writing, so this update can duplicate/overfill the resource. What consistency or conflict strategy should enforce the invariant?"

**Fix:** Move the operation into an atomic transaction/serialized coordinator, add idempotency/conflict handling, or document why duplicates are acceptable and recoverable.

## Prefer simpler serialized workflows when they preserve correctness

`id: cc-serialize-hard-shared-operation | category: architecture | severity: medium | source: book (Ch.22) + editorial | languages: any | tags: concurrency, serialization, workflow, consistency, simplicity`

**Look for in a diff:**
- Complex locking added to make a naturally sequential business operation concurrent
- A redesign opportunity where users can queue work and one coordinator can process it safely
- Concurrency retained despite low throughput need and high consistency risk

**Why it matters:** Moving a hard shared update into a later serialized operation can eliminate races and simplify user-visible behavior. Not every possible parallelism is worth implementing.

**Suggested comment:** "This operation is difficult to make safe under concurrent updates. Could the workflow serialize assignment/commit at a controlled boundary instead of coordinating every client?"

**Fix:** Compare serialized, queued, transactional, and concurrent designs; choose the simplest one that meets measured requirements and preserves invariants.
