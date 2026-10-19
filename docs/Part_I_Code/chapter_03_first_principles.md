# Clean Code, Chapter 3: First Principles, PR review rules

## Keep everything small, well named, organized, and ordered

`id: fp-small-named-organized-ordered | category: readability | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: small-functions, naming, organization, ordering, structure, module-layout, grab-bag`

**Look for in a diff:**
- Large functions, classes, or files that bundle unrelated things
- Vague names that don't tell a reader what an element is for
- A module with no clear grouping, where related code is scattered
- Concepts presented in an arbitrary order, so the reader has to jump around

**Do not flag when:** the file is generated code or a flat list of simple declarations.

**Why it matters:** Most of what it takes to clean code is in four habits: keep elements small, give them names that communicate, organize the software so others can consume it easily, and order elements so one concept follows another sensibly.

**Suggested comment:** "This module mixes several concerns in no particular order. Could we group related functions and order them so each idea leads into the next?"

**Fix:** Split large elements, rename for purpose, group related code, and order it so a reader moves through concepts naturally.

## Write names and structure for readers who don't know the code

`id: fp-reader-headspace | category: naming | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: naming, author-bias, readability, jargon, abbreviations, unclear-intent, onboarding`

**Look for in a diff:**
- Names that only make sense if you already know the author's context
- Unexplained domain jargon, abbreviations, or internal shorthand
- Comments that exist mainly to decode an unclear name
- A reviewer having to ask "what is this?" about a name or a structure

**Why it matters:** The author's own understanding biases their names and structure toward what feels obvious to them. Good naming requires working to take the headspace of someone who does not understand the code.

**Suggested comment:** "As someone new to this code, I couldn't tell what `proc` refers to. Could a name from the domain (`pending_invoice`) make it self-explanatory?"

**Fix:** Rename using domain language, expand abbreviations, and treat any reviewer confusion as a naming or structure signal.

## Functions should be small, and extract any snippet that can be named

`id: fp-small-functions | category: functions | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: small-functions, extract-method, function-length, separation-of-concerns, long-function, nameable-snippet`

**Look for in a diff:**
- A function that is more than a handful of lines
- A block inside a function that does something you could reasonably name
- Several steps in one body (guard, compute, build result) that read as separate ideas
- A function whose steps are hard to follow without scrolling

**Do not flag when:** the function is a flat sequence, mapping, or configuration with no branching.

**Why it matters:** Small functions can have descriptive names and promote separation of concerns, so each function does one thing. If a snippet can be reasonably named, it belongs in a function named for what it does.

**Suggested comment:** "The validation block and the date calculation here could each be named functions. That would shorten this and let the main flow read top to bottom."

**Fix:** Extract each nameable snippet into its own function and gather related things together.

**Example:**
```python
# before
def previous_weekday(weekday, from_date):
    if not 1 <= weekday <= 7:
        raise ValueError("Invalid day-of-the-week code.")
    diff = from_date.weekday_code - weekday
    return from_date + timedelta(days=-(diff + (0 if diff > 0 else 7)))


# after
def previous_weekday(weekday, from_date):
    check_weekday(weekday)
    return subtract_days(from_date, days_before(weekday, from_date))
```

## Name functions with verbs so the calling code reads like prose

`id: fp-verb-names-read-like-prose | category: naming | severity: low | source: book (Ch.3) + editorial | languages: any | tags: function-names, verbs, readability, calling-sequence, negation, small-things`

**Look for in a diff:**
- A function name that is a noun or vague label instead of a verb saying what it does
- A calling sequence that needs comments to be understood
- Awkward tricks like a leading minus sign or offset where a named operation would be clearer
- Extracted helpers placed far from the code that uses them

**Why it matters:** A good verb name lets the calling sequence read like well-written prose, and a reader can simply agree with the function and move on. Small things, like a leading minus sign that a `subtract_days` function would remove, still matter.

**Suggested comment:** "`add_days(-n, d)` makes the reader work out the sign. A `subtract_days(d, n)` helper would say what it means."

**Fix:** Name functions after what they do, express the operation directly, and keep helpers near their callers.

## Tidy a function before it grows, not after

`id: fp-tidy-before-growth | category: process | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: refactoring, growth, extract-method, rotting-code, feature-creep, accumulating-conditionals, tidy-first`

**Look for in a diff:**
- Yet another branch, rule, or special case added to an already large function
- A function in an area the business is actively expanding (pricing, tax, discounts, promotions)
- Conditionals piling up in one place with no structure for the next rule

**Do not flag when:** the area is stable and the change is a one-off.

**Why it matters:** Code that is already a little unkempt tends to grow into a mess as features are added. Tidying it first, with extract-method refactoring, gives each new rule an obvious home so the function doesn't rot from the inside.

**Suggested comment:** "This function has absorbed several pricing rules already. Before adding another, could we extract price, tax, and discount steps so the new rule has a clear place?"

**Fix:** Extract functions first, in a separate commit if possible, then add the feature.

## Separate responsibilities by who asks for the change (SRP)

`id: fp-srp-stakeholders | category: design | severity: medium | source: book (Ch.3) | languages: any | tags: single-responsibility, srp, fragility, stakeholders, mixed-concerns, tax, discount, unrelated-changes`

**Look for in a diff:**
- One function or class that mixes logic owned by different stakeholders (tax, discounts, formatting, notifications)
- A change to one rule that requires editing code that also holds another rule
- A bug fix for one concern that could plausibly break another in the same body

**Why it matters:** Stakeholders concerned with taxes should only need to change the tax function, and those concerned with discounts only the discount functions. Keeping them apart means a tax change won't break discounts. Ignoring this causes fragility: the system breaks in unexpected ways and stakeholders lose confidence.

**Suggested comment:** "Pricing and tax are computed in the same function here, so a tax rule change could affect pricing. Could we separate them so each can change independently?"

**Fix:** Split by reason to change, one function or class per stakeholder concern.

**Example:**
```python
price = calculate_price(item, days)  # changes with pricing and discount rules
tax = get_tax(item, price)  # changes only with tax rules
```

## Add new features in one place, not many (OCP)

`id: fp-ocp-switch-growth | category: design | severity: medium | source: book (Ch.3) | languages: any | tags: open-closed, ocp, switch-statement, if-elif-chain, type-check, extensibility, enum, polymorphism`

**Look for in a diff:**
- A `switch` or `if/elif` chain on a type or kind that likely needs a new case over time
- The same type check repeated in several places
- Adding one new variant would require edits in multiple existing modules

**Do not flag when:** the switch is over a small, fixed set that is not expected to grow. Switch statements are not intrinsically bad.

**Why it matters:** The Open-Closed Principle says a new feature should be added in one place, and new changes should stay out of old modules. Turning variants into data or polymorphic types removes the scattered type checks.

**Suggested comment:** "Every new item type means editing this chain and the two others like it. Could we move the per-type values into a table or class so a new type is added in one place?"

**Fix:** Replace repeated type checks with a data structure (enum or table) or polymorphic classes, and keep it outside the modules that use it.

**Example:**
```python
# before
if kind == "small_room":
    price = 100
elif kind == "large_room":
    price = 150

# after
CATALOG = {
    "small_room": Item(price=100, tax=0.05),
    "large_room": Item(price=150, tax=0.05),
}
price = CATALOG[kind].price
```

## High-level policy must not depend on low-level details (DIP)

`id: fp-dip-policy-vs-detail | category: design | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: dependency-inversion, dip, high-level-policy, low-level-details, interface, plugin, coupling, abstraction`

**Look for in a diff:**
- Business logic importing concrete low-level classes, enums, or specific variants
- Adding a new low-level variant (item type, provider, tax rule) forces changes or rebuilds in the high-level code
- A high-level function that knows about particular concrete cases
- Low-level values (prices, rates) changing require touching policy code

**Do not flag when:** the project is small and the added abstraction costs more than it saves.

**Why it matters:** Depending on low-level details makes policy code change, recompile, and redeploy whenever those details change. With dependencies inverted, details become plug-ins to the policy through an interface. The trade-off is some lost static type safety and added structure.

**Reviewer note:** AI-assisted refactors tend to improve local structure but often do not invert dependencies or separate policy from detail. Check this explicitly.

**Suggested comment:** "`calculate_total` imports each concrete item class. Could it depend on a small `CatalogItem` interface so new items don't touch this module?"

**Fix:** Define an interface owned by the high-level side, have low-level classes implement it, and create concrete instances at the edges (wiring or tests).

**Example:**
```python
class CatalogItem(Protocol):  # high-level side
    def unit_price(self) -> int: ...
    def tax_rate(self) -> float: ...


class Coffee:  # low-level detail
    def unit_price(self):
        return 10

    def tax_rate(self):
        return 0.0
```

## Dependencies should cross architectural boundaries in one direction

`id: fp-architectural-boundary | category: architecture | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: architecture, boundary, components, circular-dependency, independent-deployability, coupling, shared-data-structure`

**Look for in a diff:**
- A high-level component importing from a low-level one
- Circular dependencies between modules
- A concrete data structure that nearly everything depends on and is likely to change
- A component split that still forces both sides to rebuild together

**Why it matters:** Dependencies should cross a boundary only toward the higher-level side. Done well, the two components deploy independently, so only the one that changed needs to be rebuilt or reloaded, which helps most with slow networks and cached front-end code. A widely shared concrete data structure remains a weak point, because changing it forces everything to rebuild.

**Suggested comment:** "The low-level module now imports from the policy layer and the policy layer imports from it. Could we break the cycle by moving the shared interface to the high-level side?"

**Fix:** Point dependencies toward the higher-level component, put shared interfaces on the high-level side, and keep shared concrete data types small and stable.

## Rename things when their role changes

`id: fp-rename-as-design-evolves | category: naming | severity: medium | source: book (Ch.3) + editorial | languages: any | tags: renaming, stale-name, vague-name, responsibility-change, consistency, concepts, get-items`

**Look for in a diff:**
- A class or function whose responsibility changed in this PR but whose name did not
- Vague names like `get_items` that actually total, filter, or apply bonuses
- Inconsistent names for the same concept across modules
- A container name (`ItemList`) for something that now finalizes an order

**Why it matters:** When a problem is small, vague names are survivable. As it grows, names are how readers keep concepts straight. Reorganizing code often reveals what a thing really is, and its name should follow.

**Suggested comment:** "`ItemList` now applies bonuses and finalizes the order. A name like `RentalReceipt` would describe its role."

**Fix:** After moving responsibilities, rename the affected classes and functions to match their final role.

## Refactor under passing tests and keep tests decoupled from internals

`id: fp-refactor-under-tests | category: testing | severity: high | source: book (Ch.3) + editorial | languages: any | tags: refactoring, tests, test-coupling, regression, behavior-preserving, characterization-tests, safe-refactor`

**Look for in a diff:**
- A refactoring PR with no tests, or with tests deleted
- Tests rewritten heavily to fit the new structure
- Tests that depend on private details or specific concrete classes
- Behavior changes mixed into a structural cleanup

**Why it matters:** The refactoring in this chapter stayed safe because tests existed before it started and passed at every step. Tests changed minimally because they were kept decoupled from production details.

**Suggested comment:** "This restructures pricing but I don't see tests covering the current behavior. Could we add them first so we can confirm the refactor preserves it?"

**Fix:** Add tests for current behavior first, refactor in small steps, keep tests passing, and test through stable interfaces.

## Add structure only when expected growth justifies its cost

`id: fp-yagni-cost-of-structure | category: review-guidance | severity: low | source: book (Ch.3) + editorial | languages: any | tags: yagni, over-engineering, premature-abstraction, indirection, interface, speculative-generality, complexity-cost`

**Look for in a diff:**
- An interface, factory, or plug-in layer with a single implementation and no growth in sight
- Abstraction justified only by "we might need it"
- Indirection that makes simple code harder to follow with no concrete driver

**Do not flag when:** the growth is real and expected, such as new markets, new tax rules, or planned promotions.

**Why it matters:** More modules and indirection add cognitive load, and that cost is not free. YAGNI's original intent is to count the cost before making room for growth. Structure is worth it when growth is likely, and not otherwise.

**Suggested comment:** "What change is this abstraction making room for? If a second implementation is coming soon, it's fine. Otherwise, a plain function may be enough for now."

**Fix:** Ask for the growth rationale. If there isn't one, keep the simple version and introduce the abstraction when the second case appears.

## Don't reject extra structure over tiny performance costs

`id: fp-indirection-performance | category: review-guidance | severity: low | source: book (Ch.3) + editorial | languages: any | tags: performance, polymorphism, switch-vs-polymorphism, premature-optimization, indirection, dispatch, profiling`

**Look for in a diff:**
- A switch statement kept or reintroduced "for speed" in place of polymorphism
- Readable small functions inlined to avoid call overhead
- A review comment objecting to extra references or indirection with no measurement

**Why it matters:** Extra references and polymorphic dispatch are probably slightly slower than a switch, but the difference is usually too small to measure and doesn't matter for most applications.

**Suggested comment:** "Unless profiling shows this is a hot path, I'd favor the clearer structure over saving a function call."

**Fix:** Prefer readable structure, and optimize only where measurements show a real problem.

## Treat the first principles as guidelines, not laws

`id: fp-guidelines-not-laws | category: review-guidance | severity: low | source: book (Ch.3) + editorial | languages: any | tags: pragmatism, guidelines, srp, ocp, dip, context, nitpick, dogmatic-review`

**Look for in a diff:**
- A review comment that cites SRP, OCP, or DIP as an absolute rule
- A demand for a full architectural split on a small, stable change
- Applying a principle without weighing how often the code actually changes

**Why it matters:** These principles are well-established guidelines, not strict laws. Each should be applied in the context of the problem at hand, and a programmer may take whatever license is needed to solve it.

**Suggested comment:** "Principle X would suggest splitting this. Given how rarely this code changes, is it worth it here? Non-blocking either way."

**Fix:** State the concrete benefit of the change, mark principle-based suggestions as optional unless they cause real maintenance pain.