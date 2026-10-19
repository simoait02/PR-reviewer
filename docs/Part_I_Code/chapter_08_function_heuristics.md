# Clean Code, Chapter 8: Function Heuristics, PR review rules

## Make argument order unambiguous at the call site

`id: fh-argument-order | category: functions | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: argument-order, parameters, swapped-arguments, keyword-arguments, named-arguments, call-site-readability, commutative, variadic`

**Look for in a diff:**
- Several parameters of the same type that could be swapped without any error (`send(sender, receiver, amount)`)
- Calls where a reader cannot tell which value is which
- More than three positional arguments with no natural order
- A call site full of bare numbers, strings, or booleans

**Do not flag when:** the order has a clear rationale (`distance(x1, y1, x2, y2)`), the arguments are commutative, the call site uses keyword arguments, or the function is variadic (a `format(fmt, *args)` function really takes two arguments).

**Why it matters:** Every argument makes a function harder to understand. Zero or one is easiest, two is manageable because there is only one way to get the order wrong, three has five wrong orders, and four has twenty-three. Arguments are harder to read than to write, because the IDE helps while writing but much less while reading. Three is a usual limit, though an arbitrary one. Keyword arguments relieve most of the order worry.

**Suggested comment:** "`transfer(a, b, 100)` doesn't show which account is the source. Keyword arguments, or a small request object, would make it clear."

**Fix:** Use keyword arguments, group arguments into an object, or reduce the number of parameters.

**Example:**
```python
transfer(source=checking, destination=savings, amount=100)
```

## Reduce argument lists with fields or cohesive objects

`id: fh-reduce-args-with-context | category: functions | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: parameter-object, fields, instance-state, argument-threading, cohesion, long-parameter-list, context-object`

**Look for in a diff:**
- The same values passed through several functions as arguments
- Groups of three or four arguments that are always passed together
- Long parameter lists in methods of a class that could hold the values as fields

**Do not flag when:** the values are independent or short-lived, where turning them into fields would only add state.

**Why it matters:** Arguments are couplings. If four things are cohesive enough to be passed together, they should probably already be an object (or a named map). One of the simplest ways to shorten argument lists is to hold the values in fields of the current class, so functions communicate through their shared context instead of long argument lists.

**Suggested comment:** "`host`, `port`, `timeout`, and `retries` are passed through five functions. Could they live in a `Connection` object or be fields on this class?"

**Fix:** Introduce a parameter object or cohesive fields, and keep only genuinely varying inputs as arguments.

## Don't use boolean flag arguments

`id: fh-flag-arguments | category: functions | severity: medium | source: book (Ch.8) | languages: any | tags: flag-argument, boolean-parameter, boolean-trap, split-function, one-thing, call-site-readability, option-flag`

**Look for in a diff:**
- A boolean parameter that switches the function's behavior (`render(True)`, `get_month_names(long=True)`)
- Call sites with a bare `True` or `False`
- A function body that starts with `if flag:` and does two different things

**Do not flag when:** it is a simple binary setter on an object, such as `set_enabled(bool)`, which just sets a property.

**Why it matters:** A flag complicates the signature and proclaims that the function does more than one thing: one thing if true and another if false. At the call site, a bare `True` is hard to read, so the reader has to open the function to learn what it means.

**Suggested comment:** "`get_month_names(True)` doesn't say what `True` means. Splitting into `get_long_month_names()` and `get_short_month_names()` would make it obvious."

**Fix:** Split into two functions, one for each case.

**Example:**
```python
# before
names = get_month_names(True)

# after
names = get_long_month_names()
```

## Avoid output arguments

`id: fh-output-arguments | category: functions | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: output-parameter, out-argument, mutate-argument, return-value, multiple-return-values, least-surprise, tuple-return`

**Look for in a diff:**
- A parameter that is modified to deliver a result (out parameters, references, pointers, lists or dicts passed in to be filled)
- A function that returns nothing but fills one of its arguments
- A call site that passes in variables only to have results written into them

**Do not flag when:** a method updates its own object (`self`), or a language idiom like Go's `value, err` return is used.

**Why it matters:** Readers expect data to go in through arguments and come out through the return value. Output arguments violate the principle of least surprise and force a double take. Where objects exist, the object itself can hold the results.

**Suggested comment:** "`stats(values, mean, total)` fills `mean` and `total`, which isn't obvious from the call. Could it return `mean, total`, or could we have two functions?"

**Fix:** Return multiple values (tuple, named tuple, or object), or split into one function per result. Splitting is often best.

**Example:**
```python
# surprising
stats(values, mean_out, sum_out)

# clearer
mean, total = stats(values)
```

## Separate commands from queries

`id: fh-command-query-separation | category: functions | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: cqs, command-query-separation, side-effects, getter-with-side-effect, set-returns-bool, ambiguous-condition, pop`

**Look for in a diff:**
- A function that both changes state and returns information about it (`set()` that also returns True/False)
- A call in a condition whose meaning is ambiguous (`if set("username", "bob"):`)
- A getter or query with side effects

**Do not flag when:** a deliberate, convenient violation like `stack.pop()` is made safe, for example atomic under concurrency.

**Why it matters:** A function should either do something (a command that changes state) or answer something (a query), not both. `if set(...)` could mean "was it already set?" or "was it successfully set?", because `set` reads like an adjective instead of a verb. Even convenient violations have costs: without atomicity, `pop` can race and hand one item to two threads, and returning a value while altering state can leave a container in an unknown state if an exception occurs.

**Suggested comment:** "`if set(...)` is ambiguous. Could we separate `attribute_exists()` from `set_attribute()`?"

**Fix:** Split into a command and a query, and violate the rule only after considering the outcomes.

**Example:**
```python
if attribute_exists("username"):
    set_attribute("username", "unclebob")
```

## Prefer exceptions to returned error codes

`id: fh-prefer-exceptions | category: error-handling | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: exceptions, error-codes, return-codes, nested-ifs, happy-path, status-code, error-handling, guard-clauses`

**Look for in a diff:**
- Command functions returning status or error codes that callers compare in `if` statements
- Deeply nested `if (action() == OK)` chains
- Guard-style early returns that repeat error logging after every call
- Functions that both do work and return a success flag

**Do not flag when:** the language has no exceptions, or an error-return convention (like Go's `value, err`) is applied narrowly and consistently.

**Why it matters:** Returning error codes from commands subtly violates command-query separation and encourages commands used as conditions. It forces the caller to handle the error immediately, which creates deep nesting, and guard clauses only hide it. Exceptions separate the error handling from the happy path and simplify both. In some languages (older C++) exceptions are less reliable.

**Suggested comment:** "Each step returns a code that's checked in a nested `if`. Raising exceptions would let the happy path read straight through with one handler."

**Fix:** Raise specific exceptions at the point of failure and handle them in one place.

**Example:**
```python
try:
    delete_page(page)
    registry.delete_reference(page.name)
    config_keys.delete_key(page.name.make_key())
except PageDeletionError as e:
    logger.log(str(e))
```

## Error handling is one thing: extract try/except bodies

`id: fh-error-handling-is-one-thing | category: error-handling | severity: low | source: book (Ch.8) + editorial | languages: any | tags: try-except, try-catch, extract-function, error-handling, one-thing, separation, exception-handling-structure`

**Look for in a diff:**
- A function that mixes `try/except` with other logic
- Code after the `except` or `finally` block
- A `try` body containing many lines of normal-path work
- An `except` block with substantial logic inline

**Why it matters:** Try/catch blocks confuse the structure and mix error processing with normal processing. Error handling is one thing, so a function that handles errors should do nothing else: `try` is the first statement (after maybe declarations), and nothing follows the catch or finally block. Extracting the bodies lets readers understand and ignore the error handling separately from the real work.

**Suggested comment:** "Could we move the body of this `try` into its own function, so `delete` only handles errors and the other does the deletion?"

**Fix:** Extract the try body and the handler into named functions.

**Example:**
```python
def delete(page):
    try:
        delete_page_and_all_references(page)
    except PageDeletionError as e:
        log_error(e)
```

## Don't create a shared error definition that every module depends on

`id: fh-error-code-dependency-magnet | category: error-handling | severity: low | source: book (Ch.8) + editorial | languages: any | tags: dependency-magnet, error-codes, shared-enum, errors-module, rebuild, exception-hierarchy, coupling, reuse-error-code`

**Look for in a diff:**
- A central file of error codes, enum, or exceptions that nearly every module imports
- A new code added to that shared file
- An existing error code reused for a different meaning to avoid touching the shared file

**Why it matters:** If everything depends on one error definition, adding a code can force rebuilding and redeploying everything. That pressure made programmers reuse old codes in creative ways, which caused confusion. An enum limits the impact to files that use the new code, and interfaces or independent error types avoid a magnet entirely. Know how your build system treats these dependencies.

**Suggested comment:** "Adding another code to the shared `errors` module touches everything that imports it. Could this error be its own exception type next to where it's raised?"

**Fix:** Define independent error or exception types that implement a shared base or interface, close to the code that raises them.

## Extract duplication by weighing its size and how often it repeats

`id: fh-dry-extraction-threshold | category: duplication | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: dry, duplication, copy-paste, extract-function, repeated-code, how-many-copies, how-large, premature-extraction`

**Look for in a diff:**
- The same block repeated in many places
- A large block repeated even twice
- A repeated block likely to grow, such as an initialization list
- A tiny repeat being extracted purely to remove duplication

**Do not flag when:** both the block and the number of copies are small (two trivial lines twice). Extracting them may do more harm than good.

**Why it matters:** The cost of duplication depends on the number of lines (L) and the number of places (P). If P is large, every change must be found in every copy. If L is large, the odds that it needs changing are higher. Extract when either is large, and extract small blocks only as a readability convenience.

**Suggested comment:** "This 12-line block now appears in four handlers. Could we extract a function so a future change only happens once?"

**Fix:** Extract a well-named function when the block is large or repeated often, and leave tiny repeats alone.

## Extract similar code by parameterizing the differences

`id: fh-similar-code-extract | category: duplication | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: similar-code, near-duplicate, copy-paste-modify, parameterize, extract-function, repeated-sections, fields`

**Look for in a diff:**
- Near copies that differ in one or two constants or variable names
- A series of blocks where each copy changes one field
- A new block copied from an old one with small edits

**Why it matters:** Similar snippets tend to be larger, so they are good candidates for extraction. Usually it just means adding an argument or two to the extracted function. If that makes the argument list too long, move some variables into fields. Changes then happen in one place instead of several, and after extracting, look for further duplication.

**Suggested comment:** "These four blocks differ only by the section name. A `render_section(name)` helper would put the change in one place."

**Fix:** Extract a function that takes the varying values as arguments, or fields if there are too many.

**Example:**
```python
html += render_section(page, "SetUp")
html += render_section(page, "TearDown")
```

## Write a traversal loop once and pass in the body

`id: fh-loop-duplication | category: duplication | severity: low | source: book (Ch.8) + editorial | languages: any | tags: loop-duplication, traversal, iterator, visitor, strategy, command, template-method, higher-order-function, lambda`

**Look for in a diff:**
- The same loop over a data structure repeated with a different body each time
- Several functions that walk the same nested structure
- Hand-written nested iteration at many call sites

**Why it matters:** When a structure is traversed in many places, the loop is always the same and only the body changes. Write the loop once and pass the body in. A lambda is the popular way now, and the Command, Strategy, and Template Method patterns are older and sometimes better options.

**Suggested comment:** "This floor/room traversal is repeated in three places. Could we write `for_each_room(building, action)` once?"

**Fix:** Write the traversal once as an iterator, visitor, or higher-order function, and pass in the varying behavior.

**Example:**
```python
def for_each_room(building, action):
    for floor in building.floors:
        for room in floor.rooms:
            action(room)
```

## Don't merge accidental duplicates

`id: fh-accidental-duplication | category: duplication | severity: medium | source: book (Ch.8) + editorial | languages: any | tags: accidental-duplication, essential-duplication, srp, actors, over-sharing, shared-helper, premature-dry, wrong-abstraction`

**Look for in a diff:**
- A PR that merges two similar blocks from different modules into one shared function
- A shared helper that keeps gaining flags or options to satisfy different callers
- Similar code that changes for different reasons (different stakeholders, different rules)

**Why it matters:** Essential duplicates change together, while accidental duplicates evolve apart. Use SRP as the test: if two stretches of code serve different actors, they will change independently, and a shared function risks breaking one actor while satisfying the other. If both serve the same actor, they will change together, so forgetting one copy will break that actor.

**Suggested comment:** "These look alike, but one belongs to billing and the other to shipping, which will change independently. Is a shared helper worth coupling them?"

**Fix:** Keep accidental duplicates separate, or share only the part that truly changes together.

## Watch for temporal coupling caused by side effects

`id: fh-temporal-coupling | category: functions | severity: high | source: book (Ch.8) + editorial | languages: any | tags: temporal-coupling, side-effects, order-dependence, open-close, acquire-release, init-before-use, race-condition, shared-state, encapsulation`

**Look for in a diff:**
- Calls that only work in a specific order (open before read, initialize before use)
- Paired operations (open/close, lock/unlock, begin/commit, allocate/free) that callers must match
- Code that works only after two adjacent calls are swapped
- State changed in one call and relied on in the next
- Static or shared mutable state used from multiple threads

**Why it matters:** A side effect is any state change that outlives the function, even when it is the function's main purpose. Side effects create temporal coupling: a change of state means the order of the lines must be preserved, and side effects come in pairs, one that creates and one that undoes. People are bad at this, which is why memory got garbage collection, but nothing equivalent exists for file handles, locks, or sessions. Temporal coupling underlies concurrent-update, reentrancy, and race-condition bugs and most initialization and finalization bugs.

**Reviewer note:** Hiding side effects behind a single public method protects callers in single-threaded code. If the hidden state is shared (static), multithreaded use needs synchronization, or an instance per use.

**Suggested comment:** "Callers must call `open()` before `read()` and remember `close()`. Could one function encapsulate the whole sequence so the order can't be wrong?"

**Fix:** Encapsulate the sequence in a single function or class where private steps change internal state, and release resources in the same place that acquires them (context manager or try/finally).

## Prefer producing new values over overwriting existing ones

`id: fh-prefer-immutable-updates | category: functions | severity: low | source: book (Ch.8) + editorial | languages: any | tags: immutability, overwrite, mutation, functional-style, reassignment, in-place-update, copy-on-update, side-effects`

**Look for in a diff:**
- A data structure passed in and modified in place by the function
- One variable repeatedly overwritten across a function while later lines depend on its earlier state
- Updates whose correctness depends on the order of preceding statements

**Do not flag when:** the mutation is of local data that no outside observer can see, or in a performance-critical path where mutation is justified.

**Why it matters:** Functional languages let you rebind a name but not overwrite a value, because overwriting is a side effect that separates the lines above from the lines below with a change of state. Functional style doesn't eliminate side effects, but it makes them easier to manage and spot.

**Suggested comment:** "This mutates the caller's `clouds` list. Returning a new list would keep the update from depending on call order."

**Fix:** Build and return new values with comprehensions, `map`/`filter`, or copies, instead of mutating inputs.

**Example:**
```python
def aged_clouds(clouds, decay):
    decayed = [replace(c, concentration=c.concentration * decay) for c in clouds]
    return [c for c in decayed if c.concentration > 1]
```

## Keep control flow easy to follow: sequence, selection, iteration

`id: fh-structured-control-flow | category: functions | severity: low | source: book (Ch.8) + editorial | languages: any | tags: structured-programming, control-flow, goto, spaghetti, break-continue, flags, single-entry-single-exit, readability`

**Look for in a diff:**
- Tangled control flow using flags, labeled breaks, or `goto`
- Exceptions or jumps used for ordinary control flow
- Loops with many `break` and `continue` paths
- A function where the path from start to finish is hard to trace

**Do not flag when:** guard clauses and early returns in a small function keep the flow easy to follow.

**Why it matters:** Programs can be built from three structures, sequence, selection, and iteration, applied recursively as units with a single entry and a single exit. These are easy to reason about because you can follow each path and evaluate the outcome. Arbitrary jumps make following paths impractical and produce a rat's nest of control flow.

**Suggested comment:** "The flags and nested `break`s make it hard to follow which path leads where. Could we restructure it as simple sequence, selection, and iteration, or extract the inner loop?"

**Fix:** Restructure around plain sequence, selection, and iteration, and extract complicated parts into named functions.