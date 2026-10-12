# Chapter 22: Concurrency

> “Objects are abstractions of processing. Threads are abstractions of schedule.”
> —James O. Coplien

Writing clean concurrent programs is hard—very hard. It is much easier to write code that executes in a single thread. It is also easy to write multithreaded code that looks fine on the surface but is broken at a deeper level. Such code works fine until the system is placed under stress. In this chapter, we discuss the need for concurrent programming and the difficulties it presents. We then present recommendations for dealing with those difficulties and writing clean concurrent code. Finally, we discuss testing concurrent code. Clean concurrency is a complex topic, worthy of a book by itself. This chapter presents an overview.

## Why Concurrency?

Concurrency is a decoupling strategy. It helps us decouple what gets done from when it gets done. In single-threaded applications, what and when are so strongly coupled that the state of the entire application can often be determined by looking at the stack backtrace. A programmer who debugs such a system can set a breakpoint, or a sequence of breakpoints, and know the state of the system by which breakpoints are hit.

Decoupling what from when can dramatically improve both the throughput and structure of an application. From a structural point of view, the application looks like many little collaborating computers rather than one big main loop. This can make the system easier to understand and offers powerful ways to separate concerns.

Consider the standard servlet model of Web applications. These systems run under a Web server that partially manages concurrency. Servlets are executed asynchronously whenever Web requests come in. The servlet programmer does not have to manage all incoming requests. In principle, each servlet execution lives in its own little world and is decoupled from all other servlet executions.

Of course, the decoupling provided by Web servers is far from perfect. Servlet programmers must be careful to make sure their concurrent programs are correct. Still, the structural benefits of the servlet model are significant.

Structure is not the only motive for adopting concurrency. Some systems have response-time and throughput constraints that require hand-coded concurrent solutions. For example, consider a single-threaded information aggregator that acquires information from many websites and merges it into a daily summary. Because this system is single-threaded, it visits each website in turn. If the daily run must finish in less than 24 hours, adding more websites can eventually make the run too long. The single thread spends much of its time waiting for I/O to complete. A multithreaded algorithm could contact more than one website at a time.

Similarly, a system that handles one user at a time and requires one second per user becomes unresponsive as the number of users grows. Handling many users concurrently can improve response time. Large data sets can also be partitioned so that multiple computers process different data sets in parallel.

## Myths and Misconceptions

Concurrency has compelling benefits, but it is hard. Common myths and misconceptions include:

- Concurrency always improves performance. It can improve performance when there is a lot of wait time that can be shared between multiple threads or processors, but neither situation is trivial.
- Design does not change when writing concurrent programs. In fact, the design of a concurrent algorithm can be remarkably different from the design of a single-threaded system. Decoupling what from when usually has a large effect on system structure.
- Understanding concurrency issues is not important when working with a Web server. You need to know what the server is doing and how to guard against concurrent updates and deadlocks.

Here are some more balanced statements:

- Concurrency incurs overhead, both in performance and in additional code.
- Correct concurrency is complex, even for simple problems.
- Concurrency bugs are often not repeatable, so they are frequently ignored as one-off events instead of being treated as defects.
- Concurrency often requires a fundamental change in design strategy.

## Challenges

Consider this trivial class:

```java
public class X {
    private int lastIdUsed;

    public int getNextId() {
        return ++lastIdUsed;
    }
}
```

Suppose we create an instance of `X`, set `lastIdUsed` to `42`, and share the instance between two threads. If both threads call `getNextId()`, there are three possible outcomes:

1. Thread one gets `43`, thread two gets `44`, and `lastIdUsed` is `44`.
2. Thread one gets `44`, thread two gets `43`, and `lastIdUsed` is `44`.
3. Thread one gets `43`, thread two gets `43`, and `lastIdUsed` is `43`.

The surprising third result occurs when the two threads interfere with each other. There are many possible paths through that one line of code, and some paths generate incorrect results. For the generated bytecode in this example, there are 12,870 possible execution paths for two `int` values. Changing `lastIdUsed` from `int` to `long` increases that number to 2,704,156. Most paths generate valid results; the problem is that some do not.

## Concurrency Defense Principles

The following principles and techniques help defend systems from problems in concurrent code.

## Single Responsibility Principle

The Single Responsibility Principle states that a method, class, or component should have a single reason to change. Concurrency design is complex enough to be a reason to change in its own right and therefore deserves to be separated from the rest of the code.

Concurrency-related code has its own development, change, and tuning life cycle. It has challenges that differ from, and are often more difficult than, nonconcurrency-related code. The number of ways in which miswritten concurrency code can fail is large enough without the added burden of surrounding application code.

Recommendation: Keep concurrency-related code separate from other code.

## Corollary: Limit the Scope of Data

Two threads modifying the same field of a shared object can interfere with each other. One solution is to use Java’s `synchronized` keyword to protect a critical section that uses the shared object. It is important to restrict the number of such critical sections. The more places shared data can be updated, the more likely it is that:

- You will forget to protect one or more of those places, effectively breaking code that modifies the shared data.
- There will be duplicated effort to ensure that every access is guarded.
- It will be difficult to determine the source of failures, which are already hard enough to find.

Recommendation: Take data encapsulation to heart; severely limit access to any data that may be shared.

Consider using a functional language, or at least a functional style, when writing concurrent modules.

## Corollary: Use Copies of Data

A good way to avoid shared data is to avoid sharing the data in the first place. In some situations, it is possible to copy objects and treat them as read-only. In other cases, threads can work on copies, and their results can be merged in a single thread.

If there is an easy way to avoid sharing objects, the resulting code is far less likely to cause problems. It is worth experimenting to determine whether the cost of extra object creation and garbage collection is actually a problem. If copies allow the code to avoid synchronization, the savings from avoiding locks may make up for that cost.

## Corollary: Threads Should Be as Independent as Possible

Design threaded code so that each thread exists in its own world, sharing no data with other threads. Each thread can process one client request, with required data coming from an unshared source and stored in local variables. This makes each thread behave as if it were the only thread in the world and had no synchronization requirements.

For example, classes that subclass `HttpServlet` receive information as parameters passed to `doGet` and `doPost`. Each servlet can act as if it has its own machine, provided it uses only local variables. Of course, applications eventually encounter shared resources such as database connections.

Recommendation: Partition data into independent subsets that can be operated on by independent threads, possibly on different processors.

## Know Your Language and Library

- Use provided thread-safe collections.
- Use threading frameworks, such as Java’s `Executor`, for executing unrelated tasks.
- Use nonblocking solutions when possible.
- Know which library modules are and are not thread-safe.

### Thread-Safe Collections

The `java.util.concurrent` package provides thread-safe collections for multithreaded situations. `ConcurrentHashMap`, for example, supports simultaneous concurrent reads and writes and provides methods for common composite operations that are otherwise not thread-safe. If Java is the deployment environment, start by becoming familiar with `ConcurrentHashMap` and the classes in `java.util.concurrent`, `java.util.concurrent.atomic`, and `java.util.concurrent.locks`.

Recommendation: Review the concurrency classes available in your language and become familiar with the ones relevant to your system.

## Know Your Execution Models

There are several ways to partition behavior in a concurrent application. The following models are common examples.

## Producer–Consumer

One or more producer threads create work and place it in a buffer or queue. One or more consumer threads acquire that work from the queue and complete it. The queue between producers and consumers is a bounded resource. Producers must wait for free space before writing, and consumers must wait until there is work to consume.

Coordination through the queue involves signaling. Producers write to the queue and signal that it is no longer empty. Consumers read from the queue and signal that it is no longer full. Both may wait to be notified before continuing.

## Readers–Writers

When a shared resource primarily serves as a source of information for readers but is occasionally updated by writers, throughput is an issue. Emphasizing throughput can cause starvation or stale information, while allowing updates can reduce throughput.

The challenge is to coordinate readers so that they do not read data while a writer is updating it, and vice versa, while still providing reasonable throughput and avoiding starvation. If writers wait until there are no readers, continuous readers can starve the writers. If writers receive priority, frequent writes can reduce reader throughput.

## Dining Philosophers

Imagine philosophers sitting around a circular table. A fork is placed to the left of each philosopher, and a bowl of spaghetti is in the center. A hungry philosopher picks up the forks on both sides and eats. If a neighboring philosopher is already using one of the required forks, the philosopher waits.

Replace “philosophers” with “threads” and “forks” with “resources,” and this problem resembles many enterprise applications in which processes compete for resources. Unless carefully designed, such systems can experience deadlock, livelock, reduced throughput, and efficiency degradation.

Recommendation: Many concurrent problems are variations of these three problems. Study the algorithms and implement solutions yourself so that you are prepared to recognize them.

## Beware Dependencies between Synchronized Methods

Dependencies between synchronized methods cause subtle bugs. Java’s `synchronized` keyword protects an individual method, but a class with several synchronized methods can still be used incorrectly when a client needs to call more than one method as a single operation.

Recommendation: Avoid using more than one method on a shared object as part of one client operation.

When multiple methods must be used together, there are three ways to make the code correct:

- Client-based locking: The client locks the server before calling the first method and keeps the lock until after the last method.
- Server-based locking: The server provides a method that acquires the lock, calls the required methods, and releases the lock. The client calls this new method.
- Adapted server: An intermediary performs the locking when the original server cannot be changed.

## Keep Synchronized Sections Small

The `synchronized` keyword introduces a lock. All sections guarded by the same lock are guaranteed to have only one thread executing through them at a time. Locks are expensive because they introduce delays and overhead.

Critical sections must be guarded, but extending synchronization beyond the minimal critical section increases contention and degrades performance.

Recommendation: Keep synchronized sections as small as possible.

## Writing Correct Startup and Shutdown Code Is Hard

Writing a system that stays alive indefinitely is different from writing one that runs for a while and then shuts down gracefully. Graceful shutdown can be difficult to get right. Common problems involve deadlock, with threads waiting for a signal that never comes.

For example, imagine a parent thread that spawns several child threads and then waits for them all to finish before releasing resources. If one child deadlocks, the parent waits forever. Or suppose the parent tells all children to abandon their tasks and finish, while two children are operating as a producer–consumer pair. If the producer shuts down before the consumer receives a message, the consumer may remain blocked and never observe the shutdown signal.

These situations also apply to startup scenarios. If concurrent code must start up and shut down gracefully, expect to spend significant time making those scenarios correct.

Recommendation: Think about startup and shutdown early, and get them working early. Review existing algorithms because the problem is probably harder than it first appears.

## Testing Threaded Code

Proving that code is correct is impractical, and testing does not guarantee correctness. However, good testing can minimize risk. As soon as two or more threads use the same code and shared data, the problem becomes substantially more complex.

Recommendation: Write tests that can expose problems, then run them frequently with different programmatic configurations, system configurations, and loads. If a test fails, investigate it. Do not ignore a failure merely because the next run passes.

More specific recommendations:

- Treat spurious failures as possible threading issues.
- Get nonthreaded code working first.
- Make threaded code pluggable.
- Make threaded code tunable.
- Run with more threads than processors.
- Run on different platforms.
- Instrument code to try to force failures.

## Treat Spurious Failures as Candidate Threading Issues

Threaded code can cause things to fail that seem impossible. Bugs may appear once in a thousand or a million executions, making them frustrating to reproduce. This often leads developers to blame a cosmic ray, hardware glitch, or other “one-off.” It is better to assume that one-offs do not exist.

Recommendation: Do not ignore system failures as one-offs.

## Get Your Nonthreaded Code Working First

Make sure code works outside its use in threads. Generally, this means creating simple modules that are called by the threads. Because these modules are not thread-aware, they can be tested outside the threaded environment.

Recommendation: Do not chase nonthreading bugs and threading bugs at the same time. Make sure nonthreaded code works before introducing threads.

## Make Your Threaded Code Pluggable

Write concurrency-supporting code so that it can run in several configurations:

- Run as one thread, several threads, or with a variable number of threads.
- Allow threaded code to interact with either a real dependency or a test double.
- Execute with test doubles that run quickly, slowly, or at variable speeds.
- Execute tests for many iterations.

Recommendation: Make thread-based code especially pluggable so that it can run in various configurations.

## Make Your Threaded Code Tunable

Getting the right balance of threads typically requires trial and error. Find ways to measure performance under different configurations. Allow the number of threads to be tuned easily, and consider allowing it to change while the system is running. In some systems, self-tuning based on throughput and utilization may be appropriate.

## Run with More Threads Than Processors

Task switching changes execution order. To encourage task swapping, run with more threads than processors or cores. The more frequently tasks swap, the more likely you are to encounter missing critical sections or deadlocks.

## Run on Different Platforms

Different operating systems have different threading policies, and each policy affects execution. Multithreaded code can behave differently in different environments, even when the code is known to be incorrect in all of them.

Recommendation: Run threaded code on all target platforms early and often.

## Instrument Your Code to Try to Force Failures

Flaws in concurrent code can remain hidden. Simple tests may not expose them; failures might appear only once every few hours, days, or weeks. Only a few of the many possible execution paths through a vulnerable section may fail, so the probability of taking a failing path can be very low.

You can instrument code and force different execution orderings by adding calls that wait, sleep, yield, or adjust priority. Each can affect execution order and increase the odds of detecting a flaw. It is better when broken code fails as early and as often as possible.

There are two options for code instrumentation:

- Hand-coded
- Automated

## Hand-Coded

You can insert calls to `wait()`, `sleep()`, `yield()`, and similar methods by hand when testing a particularly difficult piece of code:

```java
public synchronized String nextUrlOrNull() {
    if (hasNext()) {
        String url = urlGenerator.next();
        Thread.yield(); // inserted for testing
        updateHasNext();
        return url;
    }
    return null;
}
```

The inserted call to `yield()` changes the execution paths and may cause code to fail where it did not fail before. If the code breaks, the call has usually exposed an existing defect rather than created one. There are caveats: the JVM does not guarantee preemptive threading, so behavior can differ across operating systems.

Problems with this approach include:

- You must manually find appropriate places to insert calls.
- You must decide where to put the call and which kind to use.
- Leaving test code in production unnecessarily slows the system.
- It is a shotgun approach; you may or may not find flaws.

Instrumentation should be enabled during testing but not in production. It should also be easy to vary configurations between runs. Dividing the system into simple modules that know nothing about threading and modules that control threading makes it easier to instrument the appropriate places. You can then create test jigs that invoke the modules with different patterns of sleep, yield, and related calls.

## Automated

Tools such as CGLIB or ASM can programmatically instrument code with calls to a jiggler. For example:

```java
public class ThreadJigglePoint {
    public static void jiggle() {
    }
}
```

Calls can be added at several points:

```java
public synchronized String nextUrlOrNull() {
    if (hasNext()) {
        ThreadJigglePoint.jiggle();
        String url = urlGenerator.next();
        ThreadJigglePoint.jiggle();
        updateHasNext();
        ThreadJigglePoint.jiggle();
        return url;
    }
    return null;
}
```

Imagine two implementations of `ThreadJigglePoint`: one does nothing in production, and the other randomly sleeps, yields, or falls through during tests. Running tests many times with random jiggling may reveal flaws. The point is to make threads run in different orders at different times. The combination of well-written tests and jiggling can increase the chance of finding errors.

Recommendation: Use jiggling strategies to ferret out errors.

## 2025 Update and Report from the Field

Modern stacks handle multiple users well when those users do not share data. The following examples show why knowledge of parallel and threading issues is still useful. Modern development stacks handle many issues that developers once had to implement by hand, but the underlying problems still exist in systems that manage much of the multiuser behavior for us.

## Data Integrity

Multiuser systems can have data-integrity issues when several users simultaneously update shared data. The examples below come from systems using React Native, AWS Lambda, and a datastore. There is nothing inherently problematic about those technologies; the issues arise when users depend on shared data.

The examples are:

- Joining a game.
- Working on a shared design.
- Players working in parallel to create a deck of cards.
- Double-deleting resources during rerender in a 2D library.
- Loading icon resources in the correct order.

## Joining a Game

Imagine a mobile gaming platform used for training workshops. A game is limited to six players, and each player receives a role numbered from 1 to 6. The backend uses an eventually consistent database.

The original implementation combined logging in, joining a game, and assigning roles. Assigning roles to multiple users joining from different mobile clients could result in duplicate roles or games with too many players. Rather than making that entire operation safe under concurrent execution, the system was redesigned.

Players now join a waiting room at login. Later, an administrator creates games and requests that all waiting players be assigned to games. This moves joining a specific game and assigning roles from potentially parallel execution to a later operation issued by one user. It also simplifies the user experience: players select a waiting room and provide their name instead of entering a game name, username, and password.

## Working on a Shared Design

Another system allowed multiple people to create a design for installing or updating a commercial security system. A design contains many images and connected elements. Usually fewer than five users work on a design, and they tend to edit different parts, so conflicts are unlikely but possible.

Selecting an element to edit provided a natural place to lock it. The system uses a flag on the element. An attempt to lock an already locked element fails and informs the user. When the user deselects the element, its lock is released. A flag was chosen instead of a long-lived database lock. With proper transaction isolation, this is a clean solution for the particular problem.

## Players Working in Parallel to Create a Deck of Cards

This is an example of choosing not to solve a potential concurrency problem. In a game, up to four players create a deck of cards. Two players may create the same card. If the deck contains duplicates, an instructor rejects it, the team cleans it up, and the team resubmits it.

The duplicated work is easy to recover from and can lead to useful discussions about collaboration. The system therefore leaves the possibility in the game. An instructor can run the game with different rules, and human interaction resolves the issue.

## Double-Deleting Resources During Rerender

A React Native application used React Native Web and a 2D graphics library called Skia. React Native and Skia each had a rendering engine, and the engines were not synchronized. When designs began loading asynchronously, Skia frequently crashed.

The cause was rendering the Skia view before loading had finished. React Native rerendered the view, while Skia’s rendering thread attempted to delete and then re-delete the same resources. The solution was to avoid rendering the Skia view until loading was complete:

- Render the Skia view only after loading; otherwise render an empty view.
- Clear the setting that causes the Skia view to render before issuing a change that causes a rerender.
- Set the new value only after the old rendering state has been cleared.

The final design allowed parallel rendering only when a design was loaded. When changing designs, the system stopped rendering Skia, loaded the design, and then began rendering again.

## Loading Icon Resources

The system could load a design before the code that loaded icons had started. This resulted in missing icons or a need to reload the design. Since other parts of the system needed those resources, they were moved into a provider in React Native. Code that could load a design ran under that provider, creating a parent–child relationship. The parent initialized first, guaranteeing the required order.

## Sharing Data

Each example involved shared data:

- Assigning roles while players join a game in parallel with an eventually consistent database.
- Editing a shared design by multiple users in parallel.
- Creating cards in parallel.
- Running dependent rendering loops while other asynchronous activity affects them.
- Loading resources without explicitly controlling execution order.

Different problems called for different approaches:

- Isolate non-thread-safe code and execute it later in a single thread.
- Lock objects with a flag in a relational database.
- Accept the possibility of duplicate work when a human can reject or accept the result.
- Avoid using a second rendering thread until it is needed, and clear it before clearing everything else.
- Make loading a parent–child relationship so the child does not render until the parent is ready.

Once a shared-data issue is discovered, there are many possible responses. The appropriate solution depends on the specific problem.

## Conclusion

Concurrent code is difficult to get right. Code that is simple to follow can become nightmarish when multiple threads and shared data are involved. If you write concurrent code, apply clean-code practices rigorously or face subtle and infrequent failures.

Follow the Single Responsibility Principle. Break the system into simple modules that separate thread-aware code from thread-ignorant code. Test thread-aware code in isolation, keeping it small and focused. Know the possible sources of concurrency issues: multiple threads operating on shared data and multiple threads using a common resource pool. Boundary cases, such as startup, shutdown, and finishing a loop, can be especially difficult.

Learn your libraries and the fundamental concurrency algorithms. Find the regions of code that must be locked, and lock only those regions. Avoid calling one locked section from another. Keep the number of shared objects and the scope of sharing as narrow as possible. Change designs to accommodate clients rather than forcing clients to manage shared state.

Concurrency issues often appear only under load or at seemingly random times. Run thread-related code in many configurations, on many platforms, repeatedly and continuously. Testability implies some level of pluggability, which makes it possible to run code in a wider range of configurations. Instrument code by hand or with automated technology, and invest in this early. The cleaner the approach, the greater the chance of getting concurrent code right.
