# Clean Code, Chapter 1: PR review rules

## A function should do one thing

`id: cc-one-thing | category: functions | severity: medium | source: book (Stroustrup) + editorial | languages: any | tags: single-responsibility, function-size, mixed-concerns, validate-and-save, long-function`

**Look for in a diff:**
- A function that validates, transforms, persists, and notifies in one body
- A name containing "and" or "also" (`save_and_send`, `parse_and_store`)
- Several unrelated blocks separated by comments
- A function whose purpose cannot be stated in one sentence without "and"

**Do not flag when:** the function is a short orchestrator that only calls other named functions in sequence.

**Why it matters:** "One thing" is subjective, so test it: if the function has more than one reason to change, it does more than one thing. Mixed responsibilities are harder to name, test, and change safely.

**Suggested comment:** "This function handles X and Y. Consider splitting so each has one reason to change."

**Fix:** Extract each responsibility into a named function. Keep the caller as a short sequence of steps.

**Example:**
```python
# before
def process_order(o):
    if not o.items:
        raise ValueError("empty")
    db.save(o)
    mailer.send(o.user.email, "Thanks!")


# after
def process_order(o):
    validated = validate_order(o)
    saved = order_repo.save(validated)
    notifier.order_confirmed(saved)
```

## Names should communicate purpose

`id: cc-names-purpose | category: naming | severity: medium | source: book (Booch) + editorial | languages: any | tags: naming, variable-names, unclear-name, abbreviations, data, tmp, flag`

**Look for in a diff:**
- Generic names: `data`, `data2`, `tmp`, `result`, `obj`, `flag`, `x`
- Single-letter or cryptic abbreviations outside tiny loops
- Function names that describe how, not what (`loop_and_filter`)
- Boolean names that don't read as a question (`status`, `check`)

**Do not flag when:** the name is a conventional short name in a tiny scope (`i`, `k`, `v` in a 3-line comprehension).

**Why it matters:** Readers should follow intent without reconstructing the design from scattered details. A precise name removes the need to read the implementation.

**Suggested comment:** "`data2` doesn't say what it holds. A name like `active_subscriptions` would make this readable without tracing the code."

**Fix:** Rename to the domain concept. Name booleans as questions (`is_expired`, `has_access`).

**Example:**
```python
# before
d = [u for u in users if u.s == 1]
# after
active_users = [u for u in users if u.status == Status.ACTIVE]
```

## Names and signatures must not mislead

`id: cc-misleading-names | category: naming | severity: high | source: book (Feathers, Cunningham) + editorial | languages: any | tags: misleading-name, name-mismatch, get-with-side-effects, surprising-behavior, wrong-name`

**Look for in a diff:**
- A `get_*` / `is_*` / `check_*` function that mutates state, writes, or calls the network
- A name that no longer matches behavior after this change
- A return value that contradicts the name (`validate()` returns the parsed object, `find()` raises instead of returning None)
- A parameter that is accepted but ignored

**Why it matters:** Code that misleads or befuddles transfers its cost to every future maintainer. A routine should turn out to be pretty much what its name says.

**Suggested comment:** "`get_user` also creates the user if missing. Either rename (`get_or_create_user`) or split the creation out so the name stays truthful."

**Fix:** Rename to match behavior, or change the behavior to match the name. Prefer splitting when one name hides two actions.

**Example:**
```python
# misleading
def is_valid(token):
    token.last_used = now()  # hidden write
    return token.exp > now()
```

## Avoid hidden side effects and unrelated work

`id: cc-hidden-side-effects | category: functions | severity: high | source: book (Cunningham) + editorial | languages: any | tags: side-effects, hidden-work, global-state, mutation, surprising, unexpected`

**Look for in a diff:**
- A function that modifies its arguments, globals, or shared state without saying so
- Logging, caching, metrics, or DB writes buried inside a function that sounds pure
- Initialization or I/O triggered on import or inside a getter
- A small helper that now does unrelated work "while it's here"

**Why it matters:** Reading should be predictable: the control flow follows the apparent purpose, and the routine does not hide unrelated work. Hidden effects cause surprises that are hard to debug.

**Suggested comment:** "This helper now also updates the cache, which callers won't expect from the name. Can the cache update move to the caller, or be made explicit in the name?"

**Fix:** Make the effect explicit (name, parameter, or return value), or move it to the caller.

## Routines should do what a reader expects

`id: cc-predictable-routines | category: readability | severity: medium | source: book (Cunningham) | languages: any | tags: predictable, surprising-code, inputs-outputs, consistency, expected-behavior`

**Look for in a diff:**
- Name, inputs, and output that don't agree with the behavior
- Control flow that doesn't follow the apparent purpose (early returns that skip required steps, flags that reverse meaning)
- Logic that needs a comment to explain why it doesn't do the obvious thing
- Inconsistent handling compared to similar functions nearby

**Why it matters:** Clean code is code you read and simply agree with from top to bottom. Predictability means the code communicates its decisions clearly, even when the logic isn't trivial.

**Suggested comment:** "Reading this, I expected X from the name, but it does Y. Can we align the name or the behavior so the next reader isn't surprised?"

**Fix:** Align naming, signature, and flow with the established pattern in the module.

## Keep functions small enough to fit in your head

`id: cc-fits-in-head | category: functions | severity: medium | source: book (Seeman) + editorial | languages: any | tags: function-length, complexity, nesting, too-many-parameters, long-function, moving-parts`

**Look for in a diff:**
- A function that no longer fits on one screen
- Deep nesting (3+ levels of `if`/`for`/`try`)
- Many parameters or many local variables to track at once
- Long boolean conditions with mixed `and`/`or`

**Do not flag when:** the function is a flat table, a mapping, or a straightforward sequence with no branching.

**Why it matters:** Good code involves no more than a handful of moving parts, precise names, and size that a reader can hold in mind. It stays understandable to peers years later.

**Suggested comment:** "This function has four levels of nesting and seven locals. Extracting the inner loop into a named helper would make it easier to follow."

**Fix:** Extract named helpers, use guard clauses to flatten nesting, and name complex conditions.

**Example:**
```python
# before
if u and u.active and (u.role == "admin" or u.role == "owner") and not u.locked:
    ...
# after
if can_manage_billing(u):
    ...
```

## Code should compose without hidden coupling and be easy to delete

`id: cc-deletable-low-coupling | category: design | severity: medium | source: book (Seeman) + editorial | languages: any | tags: coupling, hidden-dependency, cohesion, deletable, shotgun-surgery, tight-coupling`

**Look for in a diff:**
- A change that forces edits in many unrelated modules
- Reaching into another module's internals or private state
- Implicit ordering requirements between calls ("must call `init()` first")
- A new dependency from a low-level module up to a high-level one

**Why it matters:** Good code composes with other code without hidden coupling, and can be removed without unnecessary changes elsewhere.

**Suggested comment:** "This reaches into `Cart._items` directly, so changing the cart's storage will break this too. Could we go through a public method?"

**Fix:** Depend on small explicit interfaces, pass dependencies in, and keep related logic together.

## Remove duplication

`id: cc-duplication | category: duplication | severity: medium | source: book (Boy Scout Rule, Feathers) + editorial | languages: any | tags: duplication, copy-paste, dry, repeated-code, duplicated-logic`

**Look for in a diff:**
- The same block copy-pasted in multiple handlers or tests
- Two functions that differ by one literal or one condition
- A bug fix applied in one copy but not its twins
- Repeated validation or formatting logic

**Do not flag when:** two snippets look alike but change for different reasons. Forced sharing can couple unrelated code.

**Why it matters:** Duplication multiplies every future change and lets copies drift apart. Removing even one small duplication is a valid cleanup.

**Suggested comment:** "This block is the same as the one in `create_user`. Could we extract a helper so a future fix only needs to happen once?"

**Fix:** Extract a function, parameterize the differences, or move shared logic to one place.

## Prefer straightforward code over clever shortcuts

`id: cc-clever-vs-clear | category: readability | severity: medium | source: book (Booch) + editorial | languages: any | tags: clever-code, readability, one-liner, nested-comprehension, control-flow, obscure`

**Look for in a diff:**
- Dense one-liners, chained ternaries, or nested comprehensions
- Operator tricks and implicit conversions that need a second look
- Control flow that jumps around (flags, `continue` chains, exceptions as flow control)
- Related operations scattered instead of kept together

**Why it matters:** Code should read like well-written prose, with each function dealing with one idea that flows into the next.

**Suggested comment:** "This works but takes a few reads to parse. Would splitting into two named steps make the intent clearer?"

**Fix:** Use intermediate named variables, straightforward loops, and keep related operations adjacent.

**Example:**
```python
# before
r = [y for x in a if x for y in (x.items if x.ok else []) if y.v > 0]
# after
valid = (x for x in a if x and x.ok)
r = [item for x in valid for item in x.items if item.v > 0]
```

## Leave the code cleaner than you found it

`id: cc-boy-scout | category: process | severity: low | source: book | languages: any | tags: boy-scout-rule, small-cleanup, refactoring, continuous-improvement, touch-and-improve`

**Look for in a diff:**
- A PR that edits a function or file but leaves an obvious small mess next to the change
- A misleading name, tangled conditional, or small duplication in the touched lines
- Large cleanups mixed in with a small feature (suggest splitting)

**Why it matters:** The improvement can be tiny: rename one variable, split one function, remove one duplication, simplify one conditional. Done consistently, code cannot rot.

**Suggested comment:** "Since you're already in this function, could you also rename `tmp` to something descriptive? Small cleanups like this keep the file from decaying."

**Fix:** Make one small improvement in the code you touch. Keep large refactors in a separate commit or PR.

## Do not defer cleanup with "we will fix it later"

`id: cc-later-equals-never | category: process | severity: medium | source: book + editorial | languages: any | tags: todo, technical-debt, later-equals-never, shortcut, deadline, hack, fixme`

**Look for in a diff:**
- New `TODO`, `FIXME`, or `HACK` comments with no ticket or owner
- A comment admitting a shortcut ("temporary", "quick fix", "clean up later")
- A working-but-messy solution justified by deadline pressure

**Why it matters:** Later often becomes never. A shortcut turns a short-term saving into a permanent maintenance cost, and each new feature makes the mess harder to change.

**Suggested comment:** "This TODO has no ticket. Can we either fix it now or link a tracked issue so it doesn't get lost?"

**Fix:** Clean it in this PR if it's small. Otherwise open a tracked issue and reference it in the comment.

## Make it work, then make it right before merging

`id: cc-make-it-right | category: process | severity: medium | source: book (Kent Beck) + editorial | languages: any | tags: first-draft, refactor, cleanup, leftover-code, debug-code, commented-out-code`

**Look for in a diff:**
- First-draft structure that works but was never tidied
- Leftover debug prints, commented-out code, or dead branches
- Confusing or fragile code in the unit this PR just finished

**Why it matters:** Nobody writes clean code on the first pass. Clean code comes from the extra step of cleaning a working draft. Do not move on while leaving the current unit unnecessarily confusing.

**Suggested comment:** "This looks like it works. Before merging, could you remove the commented-out block and the debug print, and tidy the naming?"

**Fix:** After tests pass, refactor for clarity and remove leftovers. Keep behavior unchanged.

## Keep comments accurate; delete obsolete ones

`id: cc-comments | category: comments | severity: low | source: book (Boy Scout Rule) + editorial | languages: any | tags: comments, stale-comment, obsolete-comment, commented-out-code, misleading-comment, documentation`

**Look for in a diff:**
- A comment that no longer matches the changed code
- Comments that restate what the code obviously does
- A comment used to excuse an unclear name or structure
- Blocks of commented-out code

**Why it matters:** A stale comment misleads the next reader. Clarifying one comment or deleting an obsolete one is a valid small cleanup.

**Suggested comment:** "This comment says the list is sorted, but the sort was removed. Please update or delete it."

**Fix:** Update or delete the comment. If code needs a comment to be understood, consider renaming or extracting first.

## Optimize code for the reader, not the writer

`id: cc-optimize-for-reading | category: readability | severity: medium | source: book + editorial | languages: any | tags: readability, maintainability, reading-vs-writing, future-reader, understandable`

**Look for in a diff:**
- Code that is quick to write but hard to follow
- Missing context a new reader would need (unclear boundaries, surprising conventions)
- A change that breaks the conventions of the surrounding code

**Why it matters:** Developers spend well over ten times more time reading code than writing it. New code must stay consistent with the old, so easy-to-read surroundings make new code easier to write.

**Suggested comment:** "Someone reading this in six months will need to trace three files to understand it. Could a clearer name or a short helper make the intent obvious?"

**Fix:** Match local conventions, choose precise names, and favor clarity over brevity.

## Prefer incremental cleanup over a full rewrite

`id: cc-no-big-bang-rewrite | category: process | severity: medium | source: book + editorial | languages: any | tags: rewrite, rewrite-from-scratch, big-bang, refactoring, incremental, redesign`

**Look for in a diff:**
- A PR that replaces a whole module or system rather than improving it in steps
- A parallel "v2" implementation of existing behavior
- Large changes with no preserved behavior or tests from the old code

**Why it matters:** The old code is the most reliable record of actual behavior, including undocumented requirements and bug fixes. A rewrite chases a moving target while the old system keeps changing, and it can repeat the same structural mistakes.

**Suggested comment:** "This replaces the whole module at once. Could we migrate in smaller steps while keeping behavior covered by tests?"

**Fix:** Refactor in small steps, preserve behavior, and keep the system releasable while it evolves.

## Clean means livable, not perfect: avoid nitpicking

`id: cc-good-enough-not-perfect | category: review-guidance | severity: low | source: book (Livability) + editorial | languages: any | tags: nitpick, perfectionism, over-engineering, review-noise, pragmatism, livable`

**Look for in a diff:**
- Cosmetic issues that do not affect how easily the code can be changed
- Pressure to abstract or isolate beyond what the change needs
- Review comments that ask for polish without a maintenance benefit

**Why it matters:** Clean code is code you can live with, not golden perfection. Ordinary imperfections that do not impede change are acceptable. Flag problems that accumulate into structural damage.

**Suggested comment:** (Usually none. If raising it, label it as optional: "Nit, non-blocking: ...")

**Fix:** Reserve blocking comments for issues that slow understanding or change; mark the rest as optional.