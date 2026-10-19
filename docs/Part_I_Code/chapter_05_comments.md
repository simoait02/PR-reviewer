# Clean Code, Chapter 5: Comments, PR review rules

## Express intent in code before writing a comment

`id: cm-express-in-code-first | category: comments | severity: medium | source: book (Ch.5) + editorial | languages: any | tags: comments, explanatory-variable, extract-function, self-documenting, intent, replace-comment-with-name, boolean-expression`

**Look for in a diff:**
- A comment explaining what a condition or block does, where a function or variable name could say the same thing
- A cryptic expression (bit flags, magic values, chained conditions) with a comment above it
- A comment that needs its own explanation, with unclear terms or notation
- A new comment above a line that would read fine with one extracted name

**Do not flag when:** the comment explains why, or states something the code truly cannot express.

**Why it matters:** Comments compensate for a failure to express ourselves in code. Sometimes they are necessary, but before writing one, try to turn the tables. Usually it takes a few seconds to create a function or explanatory variable that says what the comment would. This is not a license to skip needed explanations.

**Suggested comment:** "Could we extract this condition into `is_eligible_for_full_benefits()` and drop the comment?"

**Fix:** Extract a named function or explanatory variable, then delete the comment.

**Example:**
```python
# before
# check if the employee is eligible for full benefits
if (employee.flags & HOURLY_FLAG) and employee.age > 65:

# after
if employee.is_eligible_for_full_benefits():
```

## Clean confusing code instead of commenting it

`id: cm-clean-dont-comment | category: comments | severity: medium | source: book (Ch.5) | languages: any | tags: comments, bad-code, refactor, explain-the-mess, cluttered-code, apologetic-comment, rewrite`

**Look for in a diff:**
- A comment that apologizes for or warns about confusing code ("hacky", "complicated, bear with me")
- Long comment blocks narrating convoluted logic step by step
- A comment on nearly every line of a dense function

**Why it matters:** Writing a comment because you know the code is a mess is the wrong response. Clear, expressive code with few comments beats cluttered, complex code with lots of them. Time spent explaining the mess should go into cleaning it.

**Suggested comment:** "This comment explains a lot of tangled logic. Could we simplify the code itself (extract, rename, flatten) so the explanation isn't needed?"

**Fix:** Refactor first, then delete the comments the new structure makes unnecessary.

## Comments must be true: no stale, drifted, or misleading comments

`id: cm-comments-must-be-true | category: comments | severity: high | source: book (Ch.5) + editorial | languages: any | tags: stale-comment, lying-comment, misleading-comment, outdated, comment-code-mismatch, orphaned-comment, inaccurate`

**Look for in a diff:**
- A comment that no longer matches the code that was just changed
- A comment now separated from the line it describes by newly inserted lines
- Subtly wrong wording, such as "returns when X becomes true" for code that waits a timeout and then fails
- Mismatches in behavior, units, defaults, or thresholds between comment and code

**Why it matters:** Inaccurate comments are worse than none. They mislead, set expectations that will never be met, and describe rules that no longer apply. The older a comment and the farther it sits from its code, the more likely it is wrong. Only the code tells the truth.

**Suggested comment:** "This comment says it returns as soon as `closed` is true, but the code waits for the full timeout otherwise. Can we correct the comment or remove it?"

**Fix:** Update the comment to match the behavior, move it next to the code, or delete it. Prefer making the code self-explanatory.

**Example:**
```python
response = None
saved_locale = None  # Example: "Tue, 02 Apr 2003 22:18:49 GMT"   <- describes a regex defined earlier
```

## Write comments for readers who don't know the code

`id: cm-too-intimate | category: comments | severity: low | source: book (Ch.5) | languages: any | tags: comments, reader-perspective, author-intimacy, jargon, context, unclear-comment, internal-shorthand`

**Look for in a diff:**
- Comments that use internal shorthand or assume knowledge of the author's design
- Comments that only make sense after you have read the whole implementation
- References like "the usual handling" or "the other thing" without saying what they are

**Why it matters:** Comments are usually written by someone who understands the code intimately, but the reader doesn't share that context. The words may be meaningless until the reader has already understood the code.

**Suggested comment:** "I couldn't follow this comment until I'd read the whole function. Could it name the concept explicitly, or could a clearer function name replace it?"

**Fix:** Rewrite for a reader who hasn't seen the code, or express the idea in names and structure.

## Make the link between a comment and its code obvious

`id: cm-unobvious-connection | category: comments | severity: low | source: book (Ch.5) | languages: any | tags: unclear-comment, unexplained-constant, comment-needs-explanation, magic-number, ambiguous-comment, typo-in-comment`

**Look for in a diff:**
- A comment beside code where it's unclear which part it refers to
- A comment that raises questions about constants or arithmetic instead of answering them (`# filter bytes` next to `size = w * h * 3 + 200`)
- A comment that needs its own explanation
- Possible typos that make the comment ambiguous (filter vs filler)

**Why it matters:** A comment exists to explain code that doesn't explain itself. If the reader can't tell what it describes, it adds confusion.

**Suggested comment:** "I can't tell which part of the expression this comment explains. Named constants for the `3` and the `200` would make it clear."

**Fix:** Name the constants, place the comment directly beside the code it describes, and make the wording specific.

## Keep comments local: no system-wide facts in a local comment

`id: cm-nonlocal-information | category: comments | severity: medium | source: book (Ch.5) + editorial | languages: any | tags: nonlocal-comment, default-value-in-comment, duplicated-fact, config, stale-comment, single-source-of-truth`

**Look for in a diff:**
- A docstring on a setter or function that states a default controlled somewhere else ("Defaults to 8082")
- A comment describing how another module behaves
- Configuration values restated in comments

**Why it matters:** The function has no control over that default, and nothing guarantees the comment is updated when the code that owns the default changes.

**Suggested comment:** "The function doesn't set the default port, so this comment can go stale when the config changes. Could we drop it or point to the constant?"

**Fix:** Describe only the code nearby. Refer to the single source of truth (a named constant or config) or delete the comment.

## Short legal headers are fine, long ones are not

`id: cm-legal-comments | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: license, copyright, legal-header, boilerplate, license-reference, file-header`

**Look for in a diff:**
- A copyright or license header at the top of a new file
- Large legal text or contract-style terms pasted into the source file

**Do not flag when:** a short copyright or license statement is required by company standards.

**Why it matters:** Copyright and authorship statements are reasonable and sometimes mandatory. They shouldn't be contracts or legal tomes. Where possible, refer to a standard license or external document, and editors can collapse the header.

**Suggested comment:** "Keep the header, but consider replacing the full license text with a short reference to the LICENSE file."

**Fix:** Keep a short standard header and point to the license file for the terms.

## Informative and clarifying comments are fine, but verify them

`id: cm-informative-clarifying | category: comments | severity: medium | source: book (Ch.5) | languages: any | tags: regex-comment, clarifying-comment, informative-comment, obscure-argument, library-code, accuracy, canonical-pattern`

**Look for in a diff:**
- A comment describing the format a regular expression is meant to match
- A comment explaining a return value when the name is constrained by a pattern or convention
- A comment that translates an obscure argument or return value from a library or code you can't change

**Do not flag when:** the comment adds information the code can't express.

**Why it matters:** Regexes are hard to read, so a hint is polite. But clarifying comments carry real risk of being wrong, and they are hard to verify. If the comment is wrong, fix the code to match it. Where you control the code, make the argument or return value clear in its own right.

**Suggested comment:** "The comment says this matches `hh:mm:ss EEE, MMM dd, yyyy`, but the pattern also matches `:: , , `. Let's tighten the regex and keep the comment."

**Fix:** Verify each clarifying comment against the code, and correct whichever one is wrong.

**Example:**
```python
# matches "hh:mm:ss EEE, MMM dd, yyyy"
TIME_RE = re.compile(r"\d*:\d*:\d* \w*, \w* \d*, \d*")  # also matches ":: , , "
```

## Comments that explain why are worth keeping

`id: cm-explain-intent | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: intent, rationale, why-comment, design-decision, workaround, trade-off, algorithm-choice, test-intent`

**Look for in a diff:**
- A comment explaining the reason behind a non-obvious decision (ordering rule, workaround, trade-off)
- A comment giving the rationale for an algorithm detail, such as why a loop stops at the square root
- A comment stating what a test setup is trying to achieve ("our best attempt to create a race condition")

**Do not flag when:** it explains why and no name or structure can carry that reason.

**Why it matters:** Code shows what happens, but often not why it was chosen. Even if you disagree with the solution, you know what the author was trying to do. Still, if the intent can be named, extract a function (`attempt_race_condition()`) and let the name carry it.

**Reviewer note:** Starting many threads and hoping they race usually fails, because they tend to line up and run one after another. Forcing a race takes explicit synchronization or injected random delays.

**Suggested comment:** "Good to have the rationale here. Could the loop be a named `attempt_race_condition()` so the comment isn't needed?"

**Fix:** Keep why-comments, and extract named functions where a name can state the intent.

## Comments that warn of consequences or stress a non-obvious step are worth keeping

`id: cm-warn-amplify | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: warning-comment, amplification, thread-safety, skipped-test, important-call, gotcha, do-not-change, skip-reason`

**Look for in a diff:**
- A comment warning about a consequence (not thread-safe, slow, order-sensitive)
- A comment emphasizing a call that looks trivial but matters (a `strip()` that keeps a line from being parsed as another list item)
- A skipped test with a reason

**Do not flag when:** the comment prevents a plausible mistake, such as someone "optimizing" a per-call object into a shared one.

**Why it matters:** These comments stop future programmers from breaking something that looks harmless. For skipped tests, use the framework's skip marker with a reason string so the reason is visible in reports.

**Suggested comment:** "Keep this warning. For the skipped test, a `skip(reason=...)` marker would put the reason in the test report too."

**Fix:** Keep the warning, and use the skip mechanism with an explanatory reason instead of renaming tests.

**Example:**
```python
@pytest.mark.skip(reason="Takes too long to run")
def test_really_big_file(): ...
```

## Document public APIs well, and keep those docs accurate

`id: cm-public-api-docs | category: comments | severity: medium | source: book (Ch.5) | languages: any | tags: docstring, public-api, javadoc, api-documentation, contract, library, documentation-comment`

**Look for in a diff:**
- A new public function, class, or endpoint in a library or public API with no docstring
- A public docstring that doesn't tell callers what they need: purpose, parameters, return value, errors

**Do not flag when:** the code is internal and maintained by a team that already knows it.

**Why it matters:** A well-described public API is extremely helpful, and consumers can't read the implementation. But documentation comments can be as misleading, nonlocal, and dishonest as any other comment, so the other rules in this chapter still apply.

**Suggested comment:** "This is part of the public API. Please add a docstring covering what it returns and what it raises."

**Fix:** Write precise docs covering the contract, and keep them in sync with behavior.

## Don't require doc comments on everything

`id: cm-mandated-doc-comments | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: mandatory-docstring, javadoc, param-restatement, lint-rule, internal-code, clutter, boilerplate-docs`

**Look for in a diff:**
- Docstrings or Javadoc on every function or field that restate the signature (`:param title: The title of the CD`)
- Doc comments on internal code that a small team maintains and will never publish
- A linter or process rule forcing comments with no real content

**Why it matters:** A rule requiring a comment on every function or variable creates clutter and propagates misinformation. If you generate the documentation with and without these comments, the output is nearly identical, so they add nothing.

**Suggested comment:** "This docstring only repeats the parameter names. Let's remove it and keep docstrings for public APIs and non-obvious behavior."

**Fix:** Delete restating comments, and reconsider any lint rule that requires them.

**Example:**
```python
def add_cd(title, author, tracks, duration_in_minutes):
    """
    :param title: The title of the CD
    :param author: The author of the CD
    """
```

## Don't mumble: make every comment specific or delete it

`id: cm-mumbling | category: comments | severity: low | source: book (Ch.5) | languages: any | tags: vague-comment, cryptic-comment, box-ticking, unclear-comment, mumbling, low-effort-comment`

**Look for in a diff:**
- A comment added because the process demands one, with no real information
- Vague or cryptic wording ("handle the usual case", "per config", "see above")
- A comment that leaves the reader with more questions than answers

**Why it matters:** Writing a comment just because you feel you should is a hack. If you decide to write one, spend the time to make it the best comment you can, otherwise it leaves an enigma behind.

**Suggested comment:** "I can't tell what 'per config' means here. Could the comment say which setting and what happens?"

**Fix:** Say precisely what and why, or remove the comment.

## Delete redundant and noise comments

`id: cm-redundant-noise | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: redundant-comment, noise-comment, restates-code, obvious-comment, copy-paste-comment, venting, generated-docs`

**Look for in a diff:**
- A comment that restates the code (`# increment i`, `# the day of the month` above `day_of_month`)
- A header comment that takes longer to read than the function and is less precise
- Auto-generated or pasted comments with copy-paste errors
- A frustrated or venting comment in a try/except block
- Inconsistent terms in comments (component vs container) with no clear difference

**Do not flag when:** the comment explains why an exception is deliberately ignored.

**Why it matters:** Noise trains readers to skip comments, so they miss the ones that start lying. A redundant comment is less precise than the code and invites readers to trust it instead of understanding the code. A venting comment often signals a structure problem, such as repeated try/except blocks that could be one extracted function.

**Suggested comment:** "This comment repeats the field name. Let's delete it."

**Fix:** Delete it. If repetition is the frustration, extract the repeated structure into a function.

**Example:**
```python
# the day of the month
day_of_month: int
```

## A clear name and signature beat a function header comment

`id: cm-function-headers | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: function-header, docstring, signature, naming, type-hints, short-functions, replace-comment-with-name`

**Look for in a diff:**
- A header docstring on a short, single-purpose function that restates its name and signature
- A long description of parameters that are already clear from their names and types
- A vague function name paired with a long docstring compensating for it

**Why it matters:** Short functions don't need much description. A well-chosen name and signature for a function that does one thing is usually better than a comment header.

**Suggested comment:** "If we rename this to `generate_n_primes(n)` and add type hints, the docstring is redundant."

**Fix:** Improve the name and signature, then delete the header.

**Example:**
```python
# before
def generate(n):
    """Computes the first prime numbers; returns them in increasing order."""

# after
def generate_n_primes(n: int) -> list[int]:
```

## Don't keep a change journal in comments

`id: cm-journal-comments | category: comments | severity: low | source: book (Ch.5) | languages: any | tags: changelog-in-code, journal-comment, modification-history, version-control, git-history, file-header`

**Look for in a diff:**
- A log at the top of a file that records each edit with a date or author
- "Modified by X on date" lines added with each change
- A comment block that grows with every PR

**Why it matters:** Keeping a log in each module made sense before version control. Now these journals clutter the module, and the source control system records the same history.

**Suggested comment:** "Version control already has this history. Let's remove the change log and put the details in the commit message."

**Fix:** Delete the journal and let commit history carry it.

## Don't check in TODO comments

`id: cm-todo-comments | category: comments | severity: medium | source: book (Ch.5) + editorial | languages: any | tags: todo, fixme, backlog, deferred-work, unfinished, placeholder, tech-debt-marker`

**Look for in a diff:**
- A new `TODO` or `FIXME` comment
- A stub or placeholder return marked with a TODO
- A "temporary" note with no plan for resolving it

**Why it matters:** The author changed his mind about TODOs and came to read them as "Don't Do". They are fine locally while you work, but should not be checked in: do the work, remove the reason for it, or put it in the backlog. If your team does allow TODOs, require a ticket reference.

**Suggested comment:** "Can we resolve this now or move it to the backlog instead of checking in a TODO?"

**Fix:** Complete it, eliminate the need for it, or track it in the issue tracker.

## Don't decorate comments with HTML or banners

`id: cm-comment-decoration | category: comments | severity: low | source: book (Ch.5) + editorial | languages: any | tags: html-in-comments, banner-comment, position-marker, section-divider, decorative-comment, ascii-art, clutter`

**Look for in a diff:**
- Hand-written HTML tags in comments (`<p>`, `<pre>`, `<ul>`)
- Banner or divider lines (`# ===== Actions =====`, a long run of slashes)
- Decorative formatting to mark sections of a file

**Do not flag when:** the documentation tool requires specific markup (such as Markdown or reStructuredText in docstrings), or a banner is used rarely and gives clear benefit.

**Why it matters:** HTML makes comments hard to read in the one place they should be easiest to read, and formatting is the doc tool's job. Banners stand out when rare but fade into background noise when overused.

**Suggested comment:** "These divider banners add noise. If the file needs sections to navigate, consider splitting it instead."

**Fix:** Remove the markup and banners, and let tooling handle formatting.

## Keep attributions and ticket numbers out of source comments

`id: cm-attributions-bylines | category: comments | severity: low | source: book (Ch.5) | languages: any | tags: byline, attribution, added-by, ticket-number, jira, pr-number, graffiti, commit-message`

**Look for in a diff:**
- Comments like `# Added by Rick` or `# Fixed by Jane, 2024`
- Ticket, PR, or issue numbers written into code comments

**Why it matters:** Bylines are graffiti. Source control already records who added what and when, and these comments stay for years, getting less accurate and relevant. The same goes for PR numbers and JIRA tags.

**Suggested comment:** "Git blame already records this. Let's drop the byline and put the ticket in the commit message."

**Fix:** Delete the comment and put references in the commit message or PR description.

## Don't check in commented-out code

`id: cm-commented-out-code | category: comments | severity: medium | source: book (Ch.5) | languages: any | tags: commented-out-code, dead-code, old-version, debug-code, version-control, cruft, delete-dont-comment`

**Look for in a diff:**
- Blocks of code turned into comments
- The old implementation left commented out beside the new one
- Comments like "removed for now" or "old version"

**Why it matters:** Others who see commented-out code won't dare delete it, assuming it is there for a reason, so it piles up. Version control remembers old code. Commenting code out while debugging is fine, but don't check it in.

**Suggested comment:** "Please remove the commented-out block. It's in git history if we ever need it."

**Fix:** Delete it.

## Keep comments free of long history and background

`id: cm-too-much-information | category: comments | severity: low | source: book (Ch.5) | languages: any | tags: long-comment, rfc-excerpt, background-info, pasted-docs, historical-discussion, irrelevant-detail, link-instead`

**Look for in a diff:**
- A comment with historical discussion or long background
- A pasted spec or RFC excerpt
- Essay-length explanations of details a reader of this code doesn't need

**Why it matters:** A reader only needs what is necessary to understand this code. Long background, like pasted text about how an encoding works, adds noise.

**Suggested comment:** "A reference like 'See RFC 2045 §6.8' is enough here. We can drop the pasted text."

**Fix:** Keep a short pointer to the source, and delete the rest.