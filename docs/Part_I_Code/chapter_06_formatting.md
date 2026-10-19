# Clean Code, Chapter 6: Formatting, PR review rules

## Follow one team-wide formatting style, enforced by a formatter

`id: fm-consistent-team-style | category: formatting | severity: medium | source: book (Ch.6) + editorial | languages: any | tags: formatting, team-style, consistency, formatter, linter, code-style, style-guide, mixed-styles`

**Look for in a diff:**
- Formatting that differs from the rest of the file or project (mixed brace, quote, import, or naming styles)
- A contributor's personal style introduced into shared code
- Style preferences being argued in review instead of encoded in tool configuration

**Why it matters:** Formatting is communication. A reader needs to trust that a formatting gesture in one file means the same thing in another, and inconsistent style makes the code look as if disagreeing individuals wrote it. The team should agree on a single set of rules once, encode them in the formatter, and follow them even when they aren't your preference. The code itself is the best coding standard document.

**Reviewer note:** Pure style that an automated formatter would fix should be handled by the tool, not by review comments.

**Suggested comment:** "This file now mixes two import and quote styles. Could we run the project formatter so it matches the team style?"

**Fix:** Run the configured formatter. If none exists, agree on rules once, encode them in a formatter config, and enforce them in CI.

## Keep formatting-only changes separate from logic changes

`id: fm-separate-formatting-churn | category: formatting | severity: low | source: editorial (consistency principle from Ch.6) | languages: any | tags: whitespace-churn, reformat, noisy-diff, formatting-only, unrelated-changes, review-noise, formatter`

**Look for in a diff:**
- A small logic change buried among many whitespace or reformatting edits
- Reformatting of untouched files or lines
- Hand-formatted code that fights the project's formatter

**Why it matters:** Mixed formatting churn hides the real change and makes review harder. Formatting rules should be applied consistently through an automated tool, not by hand edits in unrelated places.

**Suggested comment:** "The reformatting makes the logic change hard to see. Could it go in a separate commit, or could you revert the unrelated whitespace edits?"

**Fix:** Put mass reformatting in its own commit or PR, and keep feature or bug-fix diffs limited to the lines that matter.

## Prefer small files

`id: fm-small-files | category: formatting | severity: medium | source: book (Ch.6) + editorial | languages: any | tags: file-size, large-file, long-module, split-file, module-size, god-file, cohesion`

**Look for in a diff:**
- Substantial new code added to a file that is already several hundred lines long
- A new file much larger than a few hundred lines
- A file mixing several unrelated classes or concerns

**Do not flag when:** the file is generated code or a large data table.

**Why it matters:** Significant systems can be built from files that are typically around 200 lines, with an upper limit near 500. This is not a hard rule, but it is very desirable, because small files are usually easier to understand and maintain.

**Suggested comment:** "This module is now over 600 lines and covers parsing and persistence. Could we split it by responsibility?"

**Fix:** Move cohesive groups of code into separate modules named for their concept.

## Separate distinct concepts with blank lines

`id: fm-vertical-openness | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: blank-lines, vertical-openness, whitespace, visual-grouping, wall-of-code, readability, separation`

**Look for in a diff:**
- Separate thoughts in a function with no blank line between them
- Imports, constants, and functions run together
- A single dense block that mixes steps (setup, work, cleanup)

**Do not flag when:** the project's formatter already enforces blank-line rules.

**Why it matters:** Code is read top to bottom, and each group of lines is a complete thought. A blank line is a visual cue for a new, separate concept, and removing the blank lines has a remarkably obscuring effect.

**Suggested comment:** "Could we add a blank line between the setup, the calculation, and the return so each step stands out?"

**Fix:** Group lines that form one thought and separate groups with a single blank line.

## Keep closely related lines together

`id: fm-vertical-density | category: formatting | severity: low | source: book (Ch.6) | languages: any | tags: vertical-density, related-lines, blank-lines, interleaved-comments, fields, grouping, readability`

**Look for in a diff:**
- Blank lines or comments splitting closely related lines, such as two fields of the same concept
- Every statement separated by a blank line
- Useless comments sitting between related declarations

**Why it matters:** If openness separates concepts, density implies association. Tightly related lines should look dense so the reader can take them in at a glance. Distracting comments between related fields break their association and force extra eye and head movement.

**Suggested comment:** "These two fields belong together, but the comments between them split them up. Could we remove the comments or group the fields?"

**Fix:** Put related declarations and statements next to each other, and remove noise that separates them.

**Example:**
```python
# before
class ReporterConfig:
    # The class name of the reporter listener
    class_name: str

    # The properties of the reporter listener
    properties: list


# after
class ReporterConfig:
    class_name: str
    properties: list
```

## Keep related code vertically close

`id: fm-vertical-distance | category: formatting | severity: medium | source: book (Ch.6) + editorial | languages: any | tags: vertical-distance, related-code, proximity, scrolling, jumping-between-files, cohesion, locality`

**Look for in a diff:**
- Related functions or concepts placed far apart in a file
- A reader would need to scroll up and down or jump between files to follow one idea
- Closely related concepts split into different files without a good reason
- A helper placed far from its only caller

**Why it matters:** When pieces are scattered, readers spend mental energy locating and remembering where things are instead of understanding what the system does. Related concepts should be close, and the distance should reflect how important each is to understanding the other.

**Suggested comment:** "`parse_header` is only used here but lives 300 lines away. Could we move it next to its caller?"

**Fix:** Move related code together, and keep it in one file unless there is a good reason to separate it.

## Declare variables close to where they are used

`id: fm-declare-near-use | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: variable-declaration, scope, locals, loop-variable, declare-near-use, initialization, long-function`

**Look for in a diff:**
- A variable declared or initialized many lines before its first use
- Locals collected at the top of a long function and used much later
- A loop control variable declared outside the loop statement

**Do not flag when:** the function is short and its locals sit at the top, or the language requires declarations at the top.

**Why it matters:** Variables should be declared as close to their usage as possible. In very short functions the top is fine, loop control variables belong in the loop statement, and only in rare cases in a long function should one be declared at the top of a block or just before a loop.

**Suggested comment:** "`total` is initialized 30 lines before the loop that uses it. Could we declare it right before the loop, or split this function?"

**Fix:** Move the declaration next to its first use, and consider shortening the function.

**Example:**
```python
# before
count = 0
# ... many lines ...
for test in tests:
    count += test.count_cases()

# after
count = 0
for test in tests:
    count += test.count_cases()
```

## Declare instance variables in one well-known place

`id: fm-instance-variables-one-place | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: instance-variables, fields, class-layout, attributes, init, hidden-fields, declaration-order`

**Look for in a diff:**
- Fields declared in the middle of a class, between methods
- Fields scattered across a class rather than grouped
- In Python, attributes first assigned in methods other than `__init__`

**Do not flag when:** the language or team convention puts them elsewhere. Follow the established convention.

**Why it matters:** Instance variables belong at the top or the bottom of a class, so everyone knows where to look. Putting them halfway down the class means a reader finds them only by accident. Follow the pervasive convention of your language.

**Suggested comment:** "These two fields are declared between methods, so they're easy to miss. Could we move them to the top of the class with the others?"

**Fix:** Move all field declarations to the conventional place, and in Python define all attributes in `__init__`.

## Put the calling function above the function it calls

`id: fm-caller-above-callee | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: function-order, caller-callee, top-down, step-down, dependent-functions, constants, readability`

**Look for in a diff:**
- A helper defined above, or far below, the function that uses it
- Called functions listed in a different order than they are called
- A well-known constant buried in a low-level helper instead of passed down from the level that should know it

**Do not flag when:** the language requires definitions before use.

**Why it matters:** If one function calls another, they should be close, with the caller above the callee. That gives the module a natural top-down flow, and readers can trust that definitions follow shortly after their use. Constants should live at the appropriate level, and be passed down from where knowing them makes sense.

**Suggested comment:** "Could `load_page` come right below `render_page`, in the order they're called, so the file reads top-down?"

**Fix:** Order functions so each caller precedes its callees, in call order, and pass key constants down from the higher level.

## Group code with conceptual affinity

`id: fm-conceptual-affinity | category: formatting | severity: low | source: book (Ch.6) | languages: any | tags: conceptual-affinity, grouping, related-functions, overloads, naming-scheme, function-families, organization`

**Look for in a diff:**
- Variations of the same operation spread across a file (`assert_true`, `assert_false`, and their overloads)
- A new function that belongs to an existing family but is added at the end of the file
- Unrelated functions interleaved with a family

**Why it matters:** Some code wants to be near other code. Affinity can come from direct dependency, shared variable use, or a similar operation with a shared naming scheme. The stronger the affinity, the less vertical distance there should be, even if the functions don't call each other.

**Suggested comment:** "`assert_false` is far from `assert_true` even though they're variations of one operation. Could we group them?"

**Fix:** Place related functions together, ordered by concept.

## Keep lines short enough to avoid horizontal scrolling

`id: fm-line-length | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: line-length, line-width, horizontal-scroll, long-lines, wrapping, column-limit, readability`

**Look for in a diff:**
- Lines wider than the team's limit (the book suggests staying under about 100-120 columns)
- Lines that force horizontal scrolling
- Long chained expressions or nested calls on a single line

**Do not flag when:** the project's configured limit differs (follow it), or the line holds an unbreakable string or URL.

**Why it matters:** Programmers strongly prefer short lines. The old 80-column limit is somewhat arbitrary, and 100 or even 120 is acceptable, but beyond that is probably careless. Never force readers to scroll right.

**Suggested comment:** "This line is over 140 characters. Could we break it up or extract an intermediate variable?"

**Fix:** Wrap the expression, or extract variables or functions to shorten it.

## Use horizontal whitespace to show what is related

`id: fm-horizontal-whitespace | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: whitespace, spacing, operators, operator-precedence, commas, assignment, function-call-spacing, readability`

**Look for in a diff:**
- Inconsistent spacing around operators or after commas
- No space around assignment, or a space between a function name and its opening parenthesis
- Uniform spacing that hides operator precedence in math expressions

**Do not flag when:** the project's automatic formatter enforces the spacing. Many formatters ignore operator precedence, so the team rule wins.

**Why it matters:** Whitespace associates strongly related things and separates weakly related ones. Spaces around assignment show its two sides, no space between a function name and its arguments keeps them together, and spaces after commas separate arguments. In math, tight high-precedence factors and spaced lower-precedence terms read nicely.

**Suggested comment:** "Minor: `b * b - 4 * a * c` hides precedence. `b*b - 4*a*c` reads more clearly, if the formatter allows."

**Fix:** Apply consistent spacing, and use spacing to show precedence where the tooling allows.

**Example:**
```python
determinant = b * b - 4 * a * c
root = (-b + math.sqrt(determinant)) / (2 * a)
```

## Don't align declarations or assignments in columns

`id: fm-no-alignment | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: alignment, column-alignment, declarations, assignments, long-lists, class-too-big, formatting-noise`

**Look for in a diff:**
- Names, types, or assigned values lined up in columns with extra spaces
- A long aligned list of declarations
- Alignment that makes the eye skim names and skip types or operators

**Do not flag when:** a formatter or team convention produces the alignment, or the data is genuinely tabular.

**Why it matters:** Alignment emphasizes the wrong things and leads the eye away from the intent. If a long list needs aligning, the real problem is the length of the list. A class with that many declarations probably should be split.

**Suggested comment:** "This aligned block of 20 attributes suggests the class is doing too much. Could we split it instead of aligning?"

**Fix:** Remove the alignment, and if the list is long, split the class.

## Indent consistently and don't collapse scopes onto one line

`id: fm-indentation | category: formatting | severity: low | source: book (Ch.6) + editorial | languages: any | tags: indentation, scope, nesting, one-line-if, collapsed-block, structure, hierarchy, readability`

**Look for in a diff:**
- Inconsistent indentation within a file
- Short `if`, `while`, function, or class bodies collapsed onto a single line
- Layout that hides the hierarchy of scopes

**Do not flag when:** a trivial one-line accessor is more readable that way and fits the team style.

**Why it matters:** Indentation makes the hierarchy of scopes visible, and readers line up the left edge to see what scope each line is in and to skip blocks they don't need. Without it code is almost unreadable. Collapsing short scopes onto one line is tempting, but it usually gets undone later.

**Suggested comment:** "Could we put the body of this `if` on its own indented line so the scope is visible?"

**Fix:** Expand collapsed blocks and indent each level consistently, using the formatter.

**Example:**
```python
# before
if not items:
    return None

# after
if not items:
    return None
```