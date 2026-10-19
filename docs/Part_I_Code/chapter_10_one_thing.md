# Clean Code, Chapter 10: One Thing, PR review rules

## A function does one thing if you can't meaningfully extract another from it

`id: ot-extract-till-you-drop | category: functions | severity: medium | source: book (Ch.10) + editorial | languages: any | tags: one-thing, extract-method, extract-till-you-drop, function-size, predicates, nameable-block, single-responsibility, small-functions`

**Look for in a diff:**
- A function from which another function could meaningfully be extracted
- A block inside an `if`, `else`, or loop with a nameable purpose
- A complicated condition that could become a named predicate
- A function longer than a few lines (the book suggests about three to six)

**Do not flag when:** the function is a switch, a formatting routine, or in a language where somewhat larger functions are idiomatic.

**Why it matters:** The test for "one thing" is practical: if you can split a function into two meaningful pieces, it did two things. So extract until you can't meaningfully extract any more, or at least consider every extraction. Most functions end up a few lines long, and typical extractions are the bodies of `if/else` and loops and their predicates, so statements read like prose.

**Suggested comment:** "Could the condition become `should_delete_record(record)` and the loop body its own function? Then this reads as a short summary."

**Fix:** Extract nameable blocks and predicates into functions until nothing meaningful remains.

**Example:**
```python
if should_delete_record(record):
    delete_record(record)
```

## Don't extract when the new function adds no meaning

`id: ot-dont-extract-meaninglessly | category: review-guidance | severity: low | source: book (Ch.10) + editorial | languages: any | tags: over-extraction, pure-delegator, trivial-wrapper, meaningless-extraction, stepdown-rule, indistinguishable-name, inline`

**Look for in a diff:**
- A function whose entire body was moved to a new function, leaving a pure delegator (`add_rental` calling `do_the_add`)
- Extracted functions whose names are indistinguishable from their implementation (`clear_amount()` is just `total_amount = 0`)
- One-line wrappers that don't raise the abstraction level
- Two closely related lines split into separate functions

**Do not flag when:** a delegator is deliberate, for example to move the real function to another module.

**Why it matters:** You can extract too little and you can extract too much. A meaningful extraction follows the stepdown rule: the function's name is more abstract than its implementation. If the name just restates the code, nothing was gained.

**Suggested comment:** "`clear_amount` and `clear_points` are one-liners whose names repeat the code. A single `clear_totals` would say more."

**Fix:** Inline the trivial wrapper, or merge related pieces into one function whose name describes the purpose.

**Example:**
```python
def clear_totals(self):
    self.total_amount = 0
    self.renter_points = 0
```

## Many small, well-named functions reveal intent, they don't hide it

`id: ot-small-functions-dont-obscure-intent | category: review-guidance | severity: low | source: book (Ch.10) + editorial | languages: any | tags: small-functions, objection, bouncing-around, call-order, guideposts, namespaces, navigation, too-many-functions, readability`

**Look for in a diff:**
- A review objection that too many small functions make code harder to follow
- Helper functions scattered randomly through a file
- Extracted functions not placed in the order they are called
- Extracted functions with unclear names, or in the wrong class or module

**Do not flag when:** the helpers are well named, grouped in a sensible class or module, and ordered in call order.

**Why it matters:** A well-organized hierarchy of namespaces, classes, and well-named functions reveals intent. The names are guideposts for finding code and give context for understanding it. A 3,000-line function was navigable only by its author, and a newcomer has no map. If functions are ordered in the sequence they are called (A, then B, C), readers move down from high level to low level without bouncing around.

**Suggested comment:** "Could the helpers follow the order they're called in, so this reads top to bottom?"

**Fix:** Group helpers in a sensible class or module, name them as guideposts, and order them by call order.

## Every large function hides a class

`id: ot-large-function-hides-class | category: design | severity: medium | source: book (Ch.10) + editorial | languages: any | tags: large-function, extract-class, local-variables-to-fields, shared-state, instance-variables, god-function, static-state, multithreading`

**Look for in a diff:**
- A long function whose local variables are used by many indented regions
- Extraction blocked because several locals are modified in a block
- The same values passed between helpers as arguments, or returned as tuples, to carry shared state
- A procedural module where many functions manipulate the same set of variables

**Why it matters:** A group of methods that manipulate a set of variables is a class. Every large function is hiding one (or more): its locals should be fields, and its indented regions should be methods. Temporarily promoting locals to fields breaks encapsulation but lets you extract, and letting helpers share fields is sometimes cleaner than passing arguments.

**Reviewer note:** Shared static or module-level variables can be corrupted in multithreaded code. Use instance state, one instance per use. In functional languages, closures play the same role.

**Suggested comment:** "These helpers all pass `total` and `points` around. Could they become fields of a small class so each helper only takes what's new?"

**Fix:** Extract a class, turn the shared locals into instance fields, and make the regions methods.

## Move methods to the class whose data they use

`id: ot-misplaced-method | category: design | severity: medium | source: book (Ch.10) + editorial | languages: any | tags: misplaced-method, feature-envy, move-method, cohesion, business-rules, wrong-class, uses-other-objects-data`

**Look for in a diff:**
- A method that barely uses its own object's fields but works on another object it receives
- Business calculations sitting in a formatting or container class
- A function that always takes the same argument and only uses that argument's data

**Why it matters:** After extraction it becomes clear which code doesn't belong in its class. In the video store example, the amount and points calculations mainly used the rental, so they moved to `Rental`, and the tests passed unchanged because their design tolerated the change. Moving logic to the class that owns the data takes business rules out of a class that was merely holding them.

**Suggested comment:** "`determine_amount` only reads the rental's fields. Could it live on `Rental`?"

**Fix:** Move the method to the class whose data it uses, and rename the original class if its role has changed.

## Put an attribute on the class where it actually varies

`id: ot-data-belongs-where-it-varies | category: design | severity: medium | source: book (Ch.10) + editorial | languages: any | tags: type-code, wrong-owner, attribute-placement, polymorphism, switch-on-type, ocp, varying-attribute, domain-modeling`

**Look for in a diff:**
- A type or category attribute stored on a class even though it varies by how the object is used
- Tests or examples where the same object takes different values of that attribute
- Switch statements on that type code that are starting to spread

**Why it matters:** In the video store example, the same movie could be a new release one time and a children's movie another, which showed that the type belonged to the rental, not the movie. Once the type is on the right class, switches on it can become polymorphism, which keeps each type's rules in its own class so new types are added without changing old code. Switch statements multiply fast, like gerbils.

**Suggested comment:** "The same product can be sold under different pricing types, so the type probably belongs to the order line. Could it move there, with the switch replaced by classes?"

**Fix:** Move the attribute to the class where it varies, and replace switches on it with polymorphic types.

## Separate business calculation from presentation

`id: ot-separate-calculation-from-presentation | category: design | severity: medium | source: book (Ch.10) + editorial | languages: any | tags: presentation, formatting, business-rules, report, statement, header-details-footer, separation-of-concerns, view-vs-logic`

**Look for in a diff:**
- A class or function that computes business results and formats output together
- A report or statement class that owns pricing or points rules
- A large function whose high-level structure (header, details, footer) isn't visible

**Why it matters:** Extraction separated the business rules from the formatting rules, so the statement class concerned itself only with presentation. Reports are usually a header, a set of details, and a footer, and when that structure shows, a bug in the footer leads straight to `make_footer`.

**Suggested comment:** "This function computes amounts and builds the text at once. Could the calculation live in the domain class so this only formats?"

**Fix:** Move calculations into domain classes, and keep the presenter as a short composition of header, details, and footer.

**Example:**
```python
def make_statement(self):
    self.clear_totals()
    return self.make_header() + self.make_details() + self.make_footer()
```

## Don't build most tests on volatile UI strings

`id: ot-tests-through-ui-strings | category: testing | severity: medium | source: book (Ch.10) + editorial | languages: any | tags: fragile-tests, ui-strings, formatted-output, assertion-on-text, test-design, presentation-coupling, test-once`

**Look for in a diff:**
- Many tests that assert a full formatted output string
- Tests that would all break if wording or layout changed
- Tests with no direct checks of the computed values

**Why it matters:** UI strings are volatile, because someone can change a heading's wording on a whim, and then every test built on them breaks. Test the format once, and have the other tests check the values being computed.

**Suggested comment:** "Twelve tests assert on the full statement text, so a wording change breaks them all. Could most of them check the computed amounts directly, with one test for the format?"

**Fix:** Assert on computed values through a domain-level call, and keep a single test for the formatting.

**Example:**
```python
assert statement.total_owed() == 9.0
assert statement.points() == 2
```

## Give test data names that explain the test's intent

`id: ot-test-data-explains-intent | category: testing | severity: low | source: book (Ch.10) + editorial | languages: any | tags: test-data, fixtures, naming, composed-assertion, test-readability, production-data-in-tests, intent`

**Look for in a diff:**
- Arbitrary or production-like names in tests ("Fred", "The Cell") that say nothing about what is being tested
- The same objects rebuilt in every test
- Long runs of assertions repeated across tests

**Why it matters:** Tests should contain data that explains their intent, not production data. Named variables for repeated objects and a composed assertion keep tests short and let readers see what each one is about.

**Suggested comment:** "`movie1` and `Fred` don't say what this test is about. `new_release_movie` would."

**Fix:** Name fixtures for their role in the test, and add a helper assertion for repeated checks.

**Example:**
```python
statement.add_rental(new_release_movie, days=3)
assert_owed_and_points(9.0, 2)
```

## Extraction shows what code is misplaced, so don't skip it out of habit

`id: ot-extraction-reveals-structure | category: review-guidance | severity: low | source: book (Ch.10) + editorial | languages: any | tags: function-size-preference, inlining, performance, extract-then-inline, style, structure-discovery, nanoseconds, profiling`

**Look for in a diff:**
- Larger functions kept because extraction seems like overkill
- Small named functions inlined back into callers
- An objection to extra function calls based on speed, with no measurements

**Do not flag when:** the team prefers somewhat larger functions (20-25 lines) and the structure is still clear.

**Why it matters:** Preferred function size is partly style. But extraction is what showed which code didn't belong in its class, so if you keep functions larger, don't miss that. You may extract first, then inline selectively once everything is placed, remembering that inlining destroys the name. Function calls cost only a few nanoseconds, compilers often inline single-use functions, and if measurements show a slowdown, inline only the hot ones.

**Suggested comment:** "Unless profiling shows this path is hot, I'd keep the extracted functions. They made it obvious where each rule belongs."

**Fix:** Extract first to see the structure, and inline only where measurements justify it.