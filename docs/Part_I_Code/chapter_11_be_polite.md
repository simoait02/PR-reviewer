# Clean Code, Chapter 11: Be Polite, PR review rules

## Give modules a narrow interface and a deep implementation

`id: bp-narrow-interface | category: design | severity: medium | source: book (Ch.11) + editorial | languages: any | tags: module-interface, deep-implementation, public-api, private-helper, cohesion, encapsulation`

**Look for in a diff:**
- A module exposing many functions or variables that callers do not need
- Callers reaching into implementation details instead of using a small public interface
- Public functions that expose low-level sequencing or storage decisions
- A module whose functions and variables do not share a clear topic

**Do not flag when:** the module is intentionally a small data or configuration boundary with a simple public shape.

**Why it matters:** A narrow interface lets callers understand what the module provides without reading its implementation. A deep implementation keeps details private and gives the module room to change.

**Suggested comment:** "This exposes several implementation helpers to callers. Could the public interface stay limited to the operations callers actually need?"

**Fix:** Keep a few high-level public operations and make lower-level helpers private. Group functions and state around one responsibility.

## Make public functions describe the high-level task

`id: bp-high-level-public-functions | category: functions | severity: medium | source: book (Ch.11) + editorial | languages: any | tags: public-function, abstraction, orchestration, intent, readable-api, implementation-details`

**Look for in a diff:**
- A public function whose body exposes initialization, loops, formatting, and low-level cases together
- A public function named after a data structure instead of an action
- Callers that must inspect the implementation to understand the operation
- High-level workflow mixed with details that belong in private helpers

**Why it matters:** A public function should tell the reader what the module does without requiring them to understand how every detail works. This lets a reviewer verify the high-level behavior quickly.

**Suggested comment:** "The public method exposes the loop and formatting details. Could it orchestrate named helpers so the intended workflow is visible at a glance?"

**Fix:** Use an action-oriented name and make the body a short sequence of calls to lower-level helpers.

## Organize modules like a readable article

`id: bp-module-reading-order | category: readability | severity: medium | source: book (Ch.11) + editorial | languages: any | tags: newspaper-metaphor, module-order, high-level-first, detail, navigation, readability`

**Look for in a diff:**
- Low-level details appearing before the high-level operation they support
- Related functions scattered across unrelated parts of a module
- A module that mixes multiple topics or stories
- Readers having to jump through several files to follow one operation

**Why it matters:** Readers should be able to start with the module name and public operation, then descend through increasingly detailed helpers. High-level concepts should come first; implementation details should appear later.

**Suggested comment:** "The public workflow is difficult to find among low-level helpers. Could the module lead with the high-level operations and group their supporting functions below them?"

**Fix:** Keep one topic per module, place the public interface first, group related helpers, and order details from broad concepts to low-level operations.

## Descend one level of abstraction at a time

`id: bp-stepdown-rule | category: functions | severity: medium | source: book (Ch.11) + editorial | languages: any | tags: stepdown-rule, abstraction-level, top-down, call-order, extraction, mixed-abstraction`

**Look for in a diff:**
- High-level operations mixed with assignments, loops, formatting, or individual cases
- A function that calls a high-level helper and then performs low-level work directly
- A helper whose body operates at several unrelated abstraction levels
- A call sequence that cannot be read from broad intent to implementation detail

**Do not flag when:** a small amount of mixed detail is necessary and the abstraction boundary would add no meaningful clarity.

**Why it matters:** One abstraction level per function keeps the reader's mental model stable. Each call should move approximately one level deeper instead of forcing the reader to jump up and down.

**Suggested comment:** "This function starts with the high-level workflow but then resets fields and handles individual cases directly. Could those details move into helpers one level below?"

**Fix:** Extract meaningful operations, name them for their purpose, and arrange callers before the helpers they call.

## Avoid the abstraction roller coaster

`id: bp-abstraction-roller-coaster | category: readability | severity: medium | source: book (Ch.11) + editorial | languages: any | tags: abstraction-roller-coaster, context-switching, mental-load, low-level-detail, switch, mixed-levels`

**Look for in a diff:**
- A high-level function that alternates between orchestration and low-level mutations
- A loop that contains unrelated initialization, formatting, and type-specific logic
- Switches or nested conditionals embedded in an otherwise high-level workflow
- Code that requires the reviewer to remember a high-level goal while processing unrelated details

**Why it matters:** Switching abstraction levels forces the reader to discard and rebuild the mental model of the operation. This slows review and makes omissions and incorrect ordering easier to miss.

**Suggested comment:** "The function moves between report-level decisions and field-level mutations several times. Could the low-level work be named and kept behind one abstraction boundary?"

**Fix:** Separate orchestration from details, extract cohesive operations, and keep each block at a consistent level.

## Make the code work, then make it readable

`id: bp-work-then-right | category: process | severity: medium | source: book (Ch.11) + editorial | languages: any | tags: first-draft, refactoring, make-it-work, make-it-right, cleanup, readability`

**Look for in a diff:**
- A working implementation that was not reorganized after the behavior was established
- Helpers added in the order they were discovered rather than the order readers need
- Debugging or construction details left in the final public workflow
- A change that treats passing tests as the end of cleanup

**Why it matters:** First drafts often contain the order and abstraction levels used during construction, not the structure readers need. Passing tests prove behavior; they do not prove that the code is understandable.

**Suggested comment:** "The behavior is covered, but the public workflow still follows the order in which it was written. Could we refactor it into a clear top-down sequence before merging?"

**Fix:** After the behavior works, extract and order the function tree, remove construction leftovers, and rerun the tests.

## Treat the rules as defaults, not dogma

`id: bp-context-over-dogma | category: review-guidance | severity: low | source: book (Ch.11) + editorial | languages: any | tags: pragmatism, abstraction, context, tradeoff, review-noise, guidelines`

**Look for in a diff:**
- A demand for strict one-level abstraction when an extraction would add no meaning
- A large refactor justified only by a formatting preference
- A review comment that ignores language conventions, performance evidence, or local design

**Why it matters:** The stepdown rule and polite-module practices are defaults. A needless abstraction can make code harder to follow, just as mixed abstraction can. Review the concrete maintenance benefit.

**Suggested comment:** "This boundary may improve readability, but the helper would add no new meaning. Is there a concrete change or maintenance benefit that justifies it?"

**Fix:** Apply the principle when it reduces mental load or protects a real boundary. Mark style-only preferences as optional.
