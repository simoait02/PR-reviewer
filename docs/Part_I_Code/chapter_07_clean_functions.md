# Clean Code, Chapter 7: Clean Functions, PR review rules

## Keep functions very small

`id: fn-small-functions | category: functions | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: function-size, small-functions, long-function, extract-method, dozen-lines, decomposition, readability`

**Look for in a diff:**
- A function longer than about a dozen lines
- Steps in one function separated by comments or blank lines, each of which could be its own function
- A function that grew in this PR by gaining another block
- A function you must scroll to read

**Do not flag when:** the function is a flat sequence, mapping, or dispatch table, or when splitting would make it harder to read. The author notes small functions can be overdone, and a few functions read better undivided.

**Why it matters:** Experience moved from 3,000-line functions to 100-300 lines, then 20-30, and finally a dozen lines or less. In a codebase of very small functions, each is two to four lines with a descriptive name, is obviously correct, tells a story, and leads to the next. This is a guideline, not a hard rule.

**Suggested comment:** "This function is about 40 lines and has three distinct steps. Could each step be a named function so this reads as a short summary?"

**Fix:** Extract each coherent step into a function with a descriptive name.

## Keep nesting shallow and make blocks one or two lines

`id: fn-shallow-nesting | category: functions | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: nesting, indentation-depth, nested-if, nested-loops, block-size, calls-in-blocks, reads-like-prose, guard-clause`

**Look for in a diff:**
- Indentation more than one or two levels deep inside a function
- The body of an `if`, `else`, or loop that is longer than a couple of lines
- Inline logic inside a block where a call to a named function would read better

**Do not flag when:** a deeper structure reads best undivided in an exceptional case.

**Why it matters:** In very small functions, blocks are one or two lines and often a single call. The called function's name adds documentary value, and the statement reads like prose (`if employee.should_be_paid_today(): employee.pay()`). Small functions cannot hold deeply nested structures, so indent depth rarely exceeds one or two.

**Suggested comment:** "This is four levels deep. Could the inner loop body become a named function, with guard clauses for the early exits?"

**Fix:** Extract block bodies into functions named for what they do, and flatten with early returns.

**Example:**
```python
if employee.should_be_paid_today():
    employee.pay()
```

## Keep each function at one level of abstraction

`id: fn-one-level-of-abstraction | category: functions | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: abstraction-level, homogenous, mixed-levels, orchestration-vs-detail, extract-function, broken-windows, magic-return-values`

**Look for in a diff:**
- High-level steps (looping over customers, choosing a type) mixed with low-level details (counters, price arithmetic, formatting)
- Raw arithmetic, parsing, or string handling beside orchestration calls
- A body whose lines are not all one level below what the name says
- Bare return values like `0`, `+1`, `-1` with no names

**Why it matters:** Mixing levels is confusing, because readers can't tell whether an expression is an essential concept or a detail. Like broken windows, once details mix with concepts, more details accrete. Extracting the lower level makes the function homogenous. The result may be slightly longer and a few CPU cycles slower, but readers' time is worth more than saving 50 nanoseconds.

**Suggested comment:** "The loop and the points arithmetic are at different levels here. Could the price calculation move to its own function so this stays at the orchestration level?"

**Fix:** Extract lower-level lines into a named function, and give meaningful names to coded return values.

**Example:**
```python
def orientation(a, b, c):
    cross = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    return sign(cross)


def sign(n):
    return 0 if n == 0 else (1 if n > 0 else -1)
```

## Order functions so the code reads top-down (stepdown rule)

`id: fn-stepdown-rule | category: functions | severity: low | source: book (Ch.7) + editorial | languages: any | tags: stepdown-rule, top-down, functional-decomposition, abstraction-levels, refactor-first-draft, make-it-work-then-right, narrative`

**Look for in a diff:**
- A function followed by helpers at unrelated or higher abstraction levels
- A long first-draft function that works but was never decomposed
- A function whose steps don't read as one level below its name
- A module you can't read from the top descending one level at a time

**Why it matters:** The code should read like a top-down narrative: each function is followed by those at the next level down, so a reader descends one level of abstraction at a time. This is classic functional decomposition. When first writing a function, you tend to search depth-first through all the levels, so the first draft mixes them. Once it works, refactor by extracting each level into a named function: first make it work, then make it right.

**Suggested comment:** "This works, but it mixes setup, per-item details, and formatting. Could we refactor it into `make_statement` calling `make_header`, `make_details`, and `make_footer`?"

**Fix:** Extract each level into named functions and order them caller first, callees next, in call order.

**Example:**
```python
def make_statement(customer):
    clear_totals()
    return make_header(customer) + make_details(customer) + make_footer()
```

## Don't split a function into entangled pieces

`id: fn-entanglement | category: functions | severity: low | source: book (Ch.7) + editorial | languages: any | tags: entanglement, over-decomposition, coupled-helpers, hidden-shared-state, merge-functions, tradeoff, john-ousterhout`

**Look for in a diff:**
- Small helpers that can't be understood without reading each other
- Helpers that share hidden state or pass many values back and forth
- Extraction that made the code harder to follow rather than easier

**Do not flag when:** the helpers each step down one level of abstraction and appear after their caller.

**Why it matters:** Two functions are entangled when you must understand one to understand the other, and decomposing large functions can create them. The author tolerates some entanglement as long as functions step down one level and lower-level functions come after higher-level ones. John Ousterhout would rather merge entangled functions, so this is a trade-off worth judging case by case.

**Suggested comment:** "`prepare` and `finish` only make sense together and share state through `self.tmp`. Would merging them or redefining the boundary be clearer?"

**Fix:** Merge pieces that cannot stand alone, or redraw the split so each function has a self-contained meaning.

## Hide switch statements behind polymorphism

`id: fn-switch-statements | category: design | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: switch, if-elif-chain, polymorphism, type-code, factory, repeated-switch, srp, ocp, match-statement`

**Look for in a diff:**
- A `switch`, `match`, or `if/elif` chain over a type code
- The same type switch repeated across functions (price, points, coupon, age rating)
- A function that must change every time a new type is added
- Per-type behavior written inline

**Do not flag when:** there is a single switch in a concrete low-level module (like a factory or `main`), used to create polymorphic objects and hidden behind an interface.

**Why it matters:** Switch statements always do N things, so they tend to be large, do more than one thing, violate SRP, and violate OCP because they change with every new type. The worst problem is that other functions will need the same switch structure, so the knowledge is repeated everywhere.

**Suggested comment:** "`determine_points` will need the same type switch as `determine_amount`. Could each rental type implement both so we only switch once, in a factory?"

**Fix:** Use polymorphism, and keep the one switch in a factory that creates the right object.

**Example:**
```python
class RentalTypeFactory:
    def make(self, type_name):
        match type_name:
            case "regular":
                return RegularRental()
            case "childrens":
                return ChildrensRental()
            case "new release":
                return NewReleaseRental()


amount = rental_type.amount(days_rented)  # callers never switch
```

## Place functions in the right context and keep internals private

`id: fn-contextual-placement | category: design | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: context, public-interface, private-helper, encapsulation, access-modifiers, utils-dumping-ground, module-boundary, cohesion`

**Look for in a diff:**
- A public function that is only used inside its own module or class
- A function placed in a class or module that has no relation to its data
- A new function dropped into a `utils` or catch-all file
- A context (class or module) with no clear external interface, or no convention marking private functions

**Why it matters:** Every function lives in a context: a cooperative grouping of functions and data with an external interface and an internal implementation. Identifying, creating, and managing those contexts is the programmer's job. The boundary expresses what is higher level and stable versus what is lower level and likely to change.

**Suggested comment:** "`_parse_row` is only used by this class, so it should be private. And `format_money` works on invoice data and might belong with `Invoice`."

**Fix:** Mark internals private (or use a naming convention), move functions next to the data they work on, and keep the public surface small.

## Name functions for what they do, not how they do it

`id: fn-descriptive-names | category: naming | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: function-names, descriptive, verb-names, hides-implementation, long-names, naming, convenient, rename-to-restructure`

**Look for in a diff:**
- A name that exposes the implementation (`add_a_to_b_and_divide_by_2`)
- A function name that is not a verb or verb phrase
- A short, enigmatic name where a clear longer one is possible
- An overly generic name (`add`) in a detailed context where more words are needed
- A comment compensating for a vague name

**Why it matters:** A function name describes behavior at slightly higher abstraction than its code, so the implementation can change without renaming (`average` stays right when it takes many arguments). More detailed contexts need longer names. A long descriptive name beats a short enigmatic one and often beats a long comment. Frequently called, general functions can have short names for convenience. Trying several names often leads to a better structure.

**Suggested comment:** "`add_a_to_b_and_divide_by_2` describes how. `average` says what and survives implementation changes."

**Fix:** Rename to a verb or implicit verb at the right abstraction, with more words for narrower contexts, and treat a hard-to-name function as a signal to restructure.

## Limit function arguments to about three

`id: fn-limit-arguments | category: functions | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: parameters, argument-count, too-many-arguments, parameter-object, coupling, insulated, dataclass, long-parameter-list`

**Look for in a diff:**
- A function with more than three parameters
- A group of parameters that are always passed together
- A new parameter added to an already long list
- Callers that must supply many values just to use the function

**Do not flag when:** the function takes one, two, or three genuinely independent inputs, which is normal.

**Why it matters:** Each input and output is a coupling, another strand woven through the function. More arguments couple the function more tightly to its callers. A limit of three is preferred where feasible. Beyond that, ask why you aren't passing an object, or whether the data and behavior belong in separate contexts.

**Suggested comment:** "This takes seven parameters, and the address fields always travel together. Could we pass an `Address` instead?"

**Fix:** Introduce a parameter object or dataclass, split the function, or move behavior into the context that owns the data.

**Example:**
```python
# before
def create_user(first, last, street, city, state, postcode, phone): ...


# after
def create_user(name: Name, address: Address, phone: str): ...
```

## Callers should depend on a narrow interface and nothing else

`id: fn-narrow-interface-insulation | category: design | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: insulation, narrow-interface, low-coupling, encapsulation, state-machine, events, hidden-state, decoupling, dependency-injection`

**Look for in a diff:**
- Callers that know a component's internal states, transitions, or logic
- An API that requires several calls in a specific order to work
- A wide interface that exposes internal actions to outside code
- Component logic tangled with the implementation of the actions it triggers

**Why it matters:** In the turnstile example, outside code only needs to send `coin` and `pass` events. The state logic lives behind a strong insulation barrier, and the action implementations can be swapped in a derived class. Few arguments at boundary-crossing functions keep coupling low.

**Suggested comment:** "Callers here set `machine.state` directly. Could they send events through a small interface so the state logic stays hidden?"

**Fix:** Expose a small interface, hide state and logic inside it, and inject the implementations of side actions.

## Prefer pure functions

`id: fn-pure-functions | category: functions | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: pure-function, side-effects, immutability, global-state, mutating-arguments, testability, concurrency, referential-transparency`

**Look for in a diff:**
- A function that reads or writes global or shared state, or mutates its arguments
- Hidden dependence on time, randomness, or environment that the name doesn't suggest
- A function that can only be tested after elaborate system setup
- Shared mutable state in concurrent code
- In Python, a mutable default argument that carries state between calls

**Do not flag when:** the mutation is of local variables hidden from callers. Purity is an external property, so internal impurity that no outside observer can see is fine.

**Why it matters:** A pure function's behavior depends only on its arguments, and executing it changes nothing else. Such functions are easier to test, combine, cache, run concurrently, and distribute across processors, and they are less prone to race conditions.

**Suggested comment:** "`apply_discount` mutates the order and reads a global rate. Could it take the rate as an argument and return the new total?"

**Fix:** Pass dependencies in as arguments, return new values instead of mutating inputs, and push side effects to the edges.

**Example:**
```python
# impure
def apply_discount(order):
    order.total *= CURRENT_RATE


# purer
def discounted_total(total, rate):
    return total * rate
```

## Wrap side effects so callers can't leave the system altered

`id: fn-hide-impurity-wrappers | category: functions | severity: medium | source: book (Ch.7) + editorial | languages: any | tags: partial-purity, side-effects, resource-management, context-manager, open-close, cleanup, try-finally, with-statement`

**Look for in a diff:**
- A resource opened in one function and closed in another
- Callers required to call setup and cleanup in the right order
- A function that leaves the system in a changed state (open file, global flag, changed directory) and relies on callers to restore it
- Cleanup that is skipped when an exception occurs

**Why it matters:** Purity depends on what is being observed. A side-effecting operation like opening a file can be wrapped in a function that performs the work and then restores the original state, so for callers the combination is effectively pure and nothing can leak.

**Suggested comment:** "Callers have to remember to close this. Could we wrap it in a context manager so cleanup is guaranteed?"

**Fix:** Use a wrapper function, callback, or context manager that sets up, runs the work, and restores state in one place.

**Example:**
```python
with open(path, "r+") as f:
    append_line_end(f)
```