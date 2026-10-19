# Clean Code, Chapter 9: The Clean Method, PR review rules

## Refactor in small steps, with tests run after each one

`id: mt-refactor-loop | category: process | severity: high | source: book (Ch.9) + editorial | languages: any | tags: refactoring, small-steps, behavior-preserving, revert, tight-loop, mixed-refactor-and-feature, safe-refactor`

**Look for in a diff:**
- A refactoring PR that also changes behavior
- A large cleanup done in one step, with no sign that tests were run between steps
- A "refactor" that changes observable behavior or updates tests to match
- Tests left failing "to fix later" after restructuring

**Why it matters:** Refactoring is a tight loop: clean one little thing, run the tests, revert if they fail, repeat. A step usually takes between five seconds and two minutes. Martin Fowler's definition is a change to the internal structure of software that makes it easier to understand and cheaper to modify without changing its observable behavior. When a step breaks the tests, revert instead of debugging forward.

**Suggested comment:** "This PR changes structure and behavior together. Could we separate the pure refactoring, where tests stay unchanged, from the behavior change?"

**Fix:** Make one small cleanup at a time, run the tests after each, revert on failure, and keep refactoring and behavior changes in separate commits.

## Clean in small increments as you go, don't let the mess grow

`id: mt-clean-as-you-go | category: process | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: make-it-work-then-right, outer-loop, incremental-cleanup, technical-debt, check-in-and-move-on, mess-too-big, continuous-cleaning`

**Look for in a diff:**
- Working code committed the moment it passes, with obvious mess left behind
- A series of increments, each one messier than the last
- Notes promising to clean up later
- A cleanup backlog that has grown too large to do in one PR

**Why it matters:** Most people cannot hold "make it work" and "make it right" in mind at once, so by the time the code works it is also a mess. The answer is an outer loop: get something small working with tests, clean it in small steps, then repeat. Never allow the mess to get too big to clean, like a sushi chef who keeps cleaning the tools while making sushi.

**Suggested comment:** "This works, but the structure got harder with each addition. Could we spend a few minutes tidying before adding the next piece?"

**Fix:** After each small working increment, clean it up before moving on, rather than saving cleanup for later.

## Refactoring needs fast, trusted tests

`id: mt-fast-trusted-tests | category: testing | severity: high | source: book (Ch.9) + editorial | languages: any | tags: tests, test-coverage, refactoring-safety, slow-tests, flaky-tests, confidence, comprehensive-tests, regression`

**Look for in a diff:**
- Restructuring of code that has no tests
- Tests that don't cover the behavior being reorganized
- Reduced test coverage in the area being cleaned
- A slow or flaky test suite that people avoid running

**Why it matters:** Clean code depends on fast, convenient, and comprehensive tests. Without a suite that runs quickly and that you implicitly trust to show the code works, you won't do much cleaning. The point of cleaning is never to produce clean code that doesn't work.

**Reviewer note:** For any refactoring PR, ask what shows that behavior is preserved.

**Suggested comment:** "I don't see tests covering this logic. Could we add tests that pin down current behavior before restructuring it?"

**Fix:** Add tests first, keep the suite fast, and run it after each cleanup step.

## See a new test fail before making it pass

`id: mt-see-test-fail-first | category: testing | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: tdd, test-first, red-green, failing-test, bug-reproduction, test-validity, assertion, regression-test`

**Look for in a diff:**
- A new test that has never been seen failing, and so might pass for the wrong reason
- A test with no meaningful assertion
- A bug fix without a test that reproduces the bug
- Tests written afterward that simply mirror the implementation

**Why it matters:** In TDD you first watch the test fail and then make it pass. This simple practice saves a lot of debugging time. TDD is not a magic bullet, and bugs still happen (a cap that produced a negative tax was one), but other tests are likely to uncover them.

**Suggested comment:** "Does this test fail without the fix? A quick revert would confirm it actually tests the bug."

**Fix:** Run the test before the production change and confirm it fails for the right reason, then make it pass.

## Keep tests from depending on production data details

`id: mt-tests-resilient-to-change | category: testing | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: test-design, test-data-builder, fixture, helper, brittle-tests, setup-duplication, factory, defaults`

**Look for in a diff:**
- Every test building the complete input structure by hand
- One new field in the production data forcing edits across many tests
- Tests that know the internal shape of the data
- Copy-pasted test setup

**Why it matters:** Having to go back and change a bunch of tests for one new field means there is a flaw in the design of the tests. A helper that fills omitted fields with reasonable defaults decouples tests from the expectations of production code, so new fields rarely require test changes.

**Suggested comment:** "Adding a field would mean editing all of these tests. Could a `make_return()` helper with defaults build the input so each test sets only what matters?"

**Fix:** Use a builder or factory helper with defaults, and have each test override only the fields relevant to its case.

**Example:**
```python
def make_return(**overrides):
    base = {"income": {"salary": 50000}, "badbobs": {"class1": ()}}
    return {**base, **overrides}
```

## Make production code more general as tests get more specific

`id: mt-generalize-production-code | category: testing | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: tdd, hardcoded-test-values, special-casing, fake-implementation, generalization, branch-per-test, overfitting`

**Look for in a diff:**
- Production code special-cased to values used in tests (`if income == 50000`)
- An if/elif branch added for each new test case
- A placeholder implementation (returning a constant) left in place after tests were added
- Production code getting more specific with each test

**Why it matters:** A TDD flow starts with a degenerate implementation and then generalizes it. As the tests grow more specific, the production code should become more generic. Keeping the code general and the tests simple keeps tests from knowing too much about the code, so production changes need fewer test changes.

**Suggested comment:** "This branch only handles the value used in the test. Can we generalize it so the next input doesn't need another branch?"

**Fix:** Replace per-case branches with a general rule or data table.

## Calculate expected values independently of the production code

`id: mt-independent-test-expectations | category: testing | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: test-expectations, expected-values, test-constants, parametrized-tests, composed-assertions, duplicated-literals, second-statement-of-intent`

**Look for in a diff:**
- Expected values computed with the production code, its tables, or its constants
- A test importing the same rate or bracket table that the code uses
- The same magic number repeated across many tests
- Repetitive assertion boilerplate or many near-identical test cases

**Do not flag when:** a shared fixture value is a named constant entered by hand (such as the tax on 50,000), used to keep a rule change in one place.

**Why it matters:** Tests are a second statement of intent, and it makes little sense to use the production code to test the production code. Calculate expected values manually and write them into the tests. Named constants for repeated expectations reduce churn, composed assertions reduce noise, and a pile of similar cases can become a table-driven test.

**Suggested comment:** "The expected value here comes from the same function under test, so the test can't catch a mistake in it. Could we hard-code the hand-calculated result?"

**Fix:** Enter hand-calculated expectations, and use named constants, helper assertions, or parametrized tests to reduce repetition.

## Put changeable rules in tables, not if-ladders

`id: mt-table-driven-rules | category: design | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: table-driven, data-driven, tax-brackets, thresholds, if-elif-ladder, magic-numbers, rate-table, configuration`

**Look for in a diff:**
- A ladder of `if/elif` branches holding thresholds and rates
- Hard-coded rates or limits embedded in logic
- Business tables likely to change (brackets, tiers, fee schedules)
- A new tier added by editing the control flow

**Why it matters:** The numbers will change, and so will the number of rows. Maintaining hard-coded ladders is labor intensive and error prone. A table with a loop turns adding a row into a data change.

**Suggested comment:** "These thresholds will change. Could they live in a table so adding a bracket is a data edit?"

**Fix:** Move thresholds and rates into a data structure and loop over it.

**Example:**
```python
BRACKETS = [(30000, 0.0), (60000, 0.15), (float("inf"), 0.25)]


def rate_for(income):
    return next(rate for limit, rate in BRACKETS if income <= limit)
```

## Express bounds with min and max, and test the boundaries

`id: mt-clamp-and-test-boundaries | category: functions | severity: low | source: book (Ch.9) + editorial | languages: any | tags: clamp, min-max, guard-clauses, negative-value, boundary-tests, caps, floors, off-by-one`

**Look for in a diff:**
- Stacked `if` guards that clamp a value into a range
- Subtraction or adjustment results that can go negative
- Caps and floors with no tests at the boundaries

**Why it matters:** A cap added to limit an adjustment produced a negative tax. It was fixed with guards, which were then simplified with `max`. Boundary conditions are where this kind of bug hides, and other tests may be the only thing that catches it.

**Suggested comment:** "Two guards clamp the value here. `max(0, min(tax, limit))` says it in one line. Do we have tests at the boundaries too?"

**Fix:** Use `min` and `max` for clamping, and add tests for values at, just below, and just above each limit.

**Example:**
```python
# before
if tax > income - FLOOR:
    tax = income - FLOOR
if tax < 0:
    tax = 0

# after
tax = max(0, min(tax, income - FLOOR))
```

## Hide raw nested data structures behind a class

`id: mt-hide-raw-data-structures | category: design | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: encapsulation, nested-dict, raw-data, wrapper-class, data-shape, json, primitive-obsession, ripple-effect`

**Look for in a diff:**
- Several modules indexing the same nested dict, JSON, or tuple structure (`data["income"]["salary"]`)
- Knowledge of the raw layout duplicated across callers
- A change to the data's shape that would require edits in many files

**Why it matters:** A class like `TaxReturn` hides the internal data structure from the rest of the application. When that structure changes, other modules don't need to.

**Suggested comment:** "`data['income']['salary']` appears in four modules. A small `TaxReturn` class with a `salary` property would keep the layout in one place."

**Fix:** Wrap the raw structure in a class with intention-revealing accessors, and let only that class know the layout.

**Example:**
```python
class TaxReturn:
    def __init__(self, data):
        self._data = data

    @property
    def salary(self):
        return self._data["income"]["salary"]
```

## Break reciprocal dependencies and extract sibling concerns consistently

`id: mt-reciprocal-dependencies | category: design | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: circular-dependency, reciprocal, bidirectional, reaching-into-fields, asymmetry, extract-class, shared-data-class, coupling`

**Look for in a diff:**
- Two classes that depend on each other (A holds B and B reads A's fields)
- A collaborator that reads a field of its owner
- One concern extracted into its own class while an equivalent sibling concern stays buried in the parent

**Why it matters:** A reciprocal relationship usually exists because one class uses another's data. Asymmetry is also a hint: if one concern deserves its own class, the similar one probably does too. Extracting a shared class that both depend on (such as a tax return class) removes the loop.

**Suggested comment:** "The adjuster reads `calculator.tax_return`, and the calculator holds the adjuster. Could the data be passed in or extracted into a shared class?"

**Fix:** Pass the needed data as an argument or extract a shared class, and extract similar concerns in the same way.

## Judge extra classes by whether they add complexity, not by count

`id: mt-extraction-not-classitis | category: review-guidance | severity: low | source: book (Ch.9) + editorial | languages: any | tags: classitis, too-many-classes, extract-class, organization, complexity, place-for-everything, over-engineering`

**Look for in a diff:**
- A review objection that new classes are "too many" when they only give names to logic that already existed
- A class extracted from a long class, with its responsibilities named clearly
- Conversely, a new class that holds no real logic

**Do not flag when:** the new classes simply move existing complexity into well-named places.

**Why it matters:** Classitis is the tendency to create so many classes that the design gets complicated. But classes that move existing complexity into nicely named places don't add complexity. The aim is a place for everything and everything in its place.

**Suggested comment:** "The extra classes just name logic that was already here, so I'm fine with them. One note: `Helper` doesn't say what it owns."

**Fix:** Keep extractions that give clearer names and homes, and challenge classes that add indirection without a real responsibility.

## Isolate axes of change behind injected strategies, wired in one place

`id: mt-axes-of-change-injection | category: design | severity: medium | source: book (Ch.9) + editorial | languages: any | tags: axes-of-change, strategy-pattern, dependency-injection, composition-root, main, duck-typing, srp, dip, dependency-rule`

**Look for in a diff:**
- A high-level class that constructs its concrete collaborators internally
- One class mixing two independent reasons to change (base calculation and adjustments)
- No single place where concrete implementations are wired together
- Tests that need heavy patching because collaborators are created inside the class

**Do not flag when:** the system is small and unlikely to grow.

**Why it matters:** Identify the axes of change, such as the base calculation versus the adjustments, and isolate them behind boundaries with SRP and DIP. The high-level class delegates to strategies it receives, and dependencies cross the boundary inward. A main component (in tests, the test setup) creates the implementations and hands them in. In dynamic languages the interface is just the method signatures the high-level code calls.

**Suggested comment:** "`TaxCalculator` creates its own bracket logic, so tests can't swap it. Could it receive the strategy in its constructor and have `main` wire them?"

**Fix:** Pass collaborators in through the constructor, keep the concrete choices in one composition point, and let the high-level class depend only on the methods it calls.

**Example:**
```python
calculator = TaxCalculator(TaxBracketter(), BadBobAdjuster())
```