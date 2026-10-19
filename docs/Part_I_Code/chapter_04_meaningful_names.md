# Clean Code, Chapter 4: Meaningful Names, PR review rules

## Use intention-revealing names

`id: nm-intention-revealing | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: naming, intention-revealing, unclear-name, single-letter, comment-instead-of-name, units, what-it-measures`

**Look for in a diff:**
- A name that needs a comment to explain what it holds
- Names that don't say what is measured or in what unit (`d`, `t`, `timeout`)
- A function name that doesn't say what it does or how it is used
- Generic names like `data`, `value`, `result` for something specific

**Do not flag when:** the scope is tiny and the context makes the meaning obvious, for example `d = get_elapsed_time_in_days()`.

**Why it matters:** A name should answer why it exists, what it does, and how it is used. If a name requires a comment, it doesn't reveal its intent. Clear names beat short names, even when they are longer.

**Suggested comment:** "`d` needs the trailing comment to make sense. `elapsed_days` or `file_age_in_days` would say what and in what unit."

**Fix:** Rename to say what is being measured and its unit, then delete the comment.

**Example:**
```python
# before
d = 0  # elapsed time in days
# after
elapsed_days = 0
```

## Name the concepts hidden behind magic numbers and positional indexes

`id: nm-system-of-names-magic-numbers | category: naming | severity: high | source: book (Ch.4) + editorial | languages: any | tags: magic-number, positional-index, context, the-list, get-them, primitive-array, named-constant, hidden-concept`

**Look for in a diff:**
- Unexplained literals in conditions (`if x[0] == 4`)
- Positional indexes into lists, tuples, or arrays (`cell[0]`) where each position has a meaning
- Containers or functions with no context in the name (`the_list`, `get_them`, `list1`)
- Code a reader can't understand without asking what the data is, what position 0 means, or what 4 stands for

**Why it matters:** Simple code can still be opaque if it gives no context. Naming the board, the status index, and the flagged value leaves the logic unchanged but makes it clear. A good system of names also tells a reader what the whole application is about.

**Suggested comment:** "I can't tell what `x[0] == 4` checks. A named constant, or a small `Cell` with `is_flagged()`, would explain it."

**Fix:** Name the container, name the constants, and consider a small class or dataclass with an intention-revealing method that hides the magic number.

**Example:**
```python
# before
def get_them():
    return [x for x in the_list if x[0] == 4]


# after
def get_flagged_cells():
    return [cell for cell in game_board if cell.is_flagged()]
```

## Don't leave false clues in names

`id: nm-avoid-disinformation | category: naming | severity: high | source: book (Ch.4) + editorial | languages: any | tags: disinformation, misleading-name, container-type-in-name, account-list, stale-type-name, inconsistent-spelling, false-clue`

**Look for in a diff:**
- A name that claims a type the value isn't (`account_list` holding a dict or set)
- A type embedded in the name that no longer matches after a refactor (`phone_string` now holding a `PhoneNumber`)
- Inconsistent spellings for the same concept (`customer_id`, `custId`, `cust_identifier`)
- A name that suggests one meaning while the code does another

**Why it matters:** Words like "list" mean something specific to programmers, so a wrong one leads to wrong conclusions. Spelling similar concepts similarly is information, and inconsistent spelling is disinformation that also confounds code completion.

**Suggested comment:** "`account_list` is actually a dict keyed by id. `accounts` is shorter and doesn't promise a list."

**Fix:** Use a neutral name (`accounts`, `account_group`), don't encode the container type, and keep one spelling per concept.

## Avoid names that look alike or can be confused with other characters

`id: nm-similar-looking-names | category: naming | severity: medium | source: book (Ch.4) | languages: any | tags: similar-names, confusable-characters, lowercase-l, uppercase-O, near-duplicate-names, optical-illusion, long-names`

**Look for in a diff:**
- Long names that differ only in the middle (`...ForHandlingOfStrings` vs `...ForStorageOfStrings`)
- Names that start the same, which makes code completion less useful
- Variables named `l` or `O`, or names mixing letters and digits like `Oxll`
- Two names that differ by one character

**Why it matters:** Similar names are hard to tell apart unless they sit next to each other, and some fonts make `l` and `1`, or `O` and `0`, indistinguishable.

**Suggested comment:** "These two names differ only in the middle of a long string. Could we make them differ at the start or use clearer words?"

**Fix:** Rename so differences are obvious and early, and avoid `l` and `O` as identifiers.

## If names must differ, they must mean something different

`id: nm-meaningful-distinctions | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: noise-words, number-series, a1-a2, info, data, object, variable-in-name, duplicate-meaning, misspelled-name, klass`

**Look for in a diff:**
- Number-series names (`a1`, `a2`, `x1`, `x2`, `x3`)
- Noise words that add no information: `ProductInfo` or `ProductData` next to `Product`, `CustomerObject` next to `Customer`
- The word "variable" or "table" in a variable or table name, or a type word like `name_string`
- Near-identical function names with unclear differences (`get_active_account`, `get_active_accounts`, `get_active_account_info`)
- Misspelled names used only to dodge a collision

**Do not flag when:** the name is a language convention such as `self` or `cls`.

**Why it matters:** Changing names just to satisfy the compiler, with numbers or noise words, leaves readers unable to tell which to use. Number-series names are uninformative, and `info` and `data` carry no meaning since everything contains data.

**Suggested comment:** "`get_active_account_info` vs `get_active_account`: what's the difference? Either merge them or name the difference."

**Fix:** Name by role (`source`, `destination`), delete noise words, merge duplicates. If you have `x1, x2, x3`, consider an array or structure.

**Example:**
```python
def copy_chars(a1, a2): ...  # before
def copy_chars(source, destination): ...  # after
```

## Use pronounceable names

`id: nm-pronounceable | category: naming | severity: low | source: book (Ch.4) | languages: any | tags: pronounceable, abbreviations, cryptic-names, unreadable, discussable, gen-ymdhms, acronym-soup`

**Look for in a diff:**
- Names made of consonant clusters or compressed abbreviations (`genymdhms`, `DtaRcrd102`, `pszqint`)
- Names a teammate couldn't read aloud in a conversation
- Abbreviations that new developers would need explained

**Why it matters:** If you can't pronounce a name, you can't conveniently discuss it, and programming is a social activity. Teams end up inventing silly spoken forms, and new developers have to be told what each name means.

**Suggested comment:** "`gen_ymdhms` is hard to say or search for. `generated_at` would be easier to read and talk about."

**Fix:** Spell the full words: `generated_at`, `modified_at`, `record_id`.

## Use searchable names, and avoid unexplained literals

`id: nm-searchable | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: searchable, grep, magic-number, single-letter, constant, named-constant, numeric-literal, find-usages`

**Look for in a diff:**
- Single-letter names outside very short scopes
- Numeric literals with a meaning (`7`, `5`, `34`, `4/5`) used inline
- Short names likely to match everywhere (`e`, `s`, `t`)
- Long numeric constants that could be mistyped without being noticed

**Do not flag when:** a short name sits in a tiny, well-known scope, such as `e` in a short `except` block or `i` in a two-line loop.

**Why it matters:** The digit 7 turns up in filenames and unrelated constants, but `MAX_CLASSES_PER_STUDENT` finds only what you want. Searchable names make it possible to find every place a concept is used, and a transposed digit in a literal can hide a bug from search.

**Suggested comment:** "The `5` here is work days per week, but I can't search for that. A `WORK_DAYS_PER_WEEK` constant would make usages findable."

**Fix:** Replace literals with named constants, and give names that cross multiple places a descriptive, searchable form.

**Example:**
```python
# before
for j in range(34):
    s += (t[j] * 4) // 5
# after
for task in tasks:
    total_weeks += (task.estimate * REAL_DAYS_PER_IDEAL_DAY) // WORK_DAYS_PER_WEEK
```

## Variable name length should match scope size

`id: nm-variable-name-length | category: naming | severity: low | source: book (Ch.4) | languages: any | tags: variable-names, scope, name-length, short-names, long-names, instance-variables, globals`

**Look for in a diff:**
- A long, wordy name for a variable used in two lines (`the_number_to_be_squared`)
- Single-letter or cryptic names for instance variables, module-level variables, or globals
- Several one-letter names (`m`, `p`, `i`, `j`) used across a larger scope

**Do not flag when:** a short name sits in a very small scope, for example `n` in a two-line loop.

**Why it matters:** Short names are fine in short scopes, but in longer scopes they become opaque. Arguments and locals can be a word or two, instance variables longer, globals longer still. Properties that look like variables follow the same rule.

**Suggested comment:** "`n` is fine in this loop, but this module-level `n` is used across the file. A descriptive name would help."

**Fix:** Lengthen names as scope grows, and shorten overlong names in tiny scopes.

## Function, class, and namespace names get shorter as scope grows

`id: nm-function-class-name-length | category: naming | severity: low | source: book (Ch.4) + editorial | languages: any | tags: function-names, class-names, namespaces, aliases, scope, name-length, private-methods, test-names`

**Look for in a diff:**
- A global or widely used function with a long encoded name (`open_file_and_throw_if_not_found` instead of `open`)
- A private helper with a vague one-word name that doesn't explain its narrow purpose
- Test names that are short or numbered (`test1`) instead of descriptive
- Namespace aliases that are cryptic in a long module

**Why it matters:** This is the opposite of the variable rule. Widely used functions are used often and are general, so they get short names. Private and inner functions and classes are narrow and need more words. Tests, with the smallest scope, get the longest names. Namespace names are descriptive, and their aliases get longer as the module grows.

**Suggested comment:** "This private helper is called from one place and is named `process`. A longer name that states its narrow job would help."

**Fix:** Keep public, general names short, and give private, narrow, and test names descriptive ones.

## Avoid encodings: type prefixes, member prefixes, and interface prefixes

`id: nm-avoid-encodings | category: naming | severity: low | source: book (Ch.4) + editorial | languages: any | tags: hungarian-notation, type-prefix, member-prefix, m-prefix, interface-prefix, I-prefix, encoding, stale-type-name`

**Look for in a diff:**
- Hungarian-style type or scope codes in names (`str_name`, `iCount`)
- Member prefixes like `m_desc`
- Interfaces prefixed with `I` (`IShapeFactory`)
- A name that embeds a type that was later changed (`phone_string` holding a `PhoneNumber`)

**Do not flag when:** the language or team convention requires it, such as `I`-prefixed interfaces in C# or a leading underscore for private members in Python. Follow local convention.

**Why it matters:** Encoded names are hard to pronounce, easy to mistype, harder to change, and can mislead when the type changes. Modern type systems, IDEs, and small functions make them unnecessary. If something must be encoded, put the marker on the implementation (`ShapeFactoryImp`) rather than the interface.

**Suggested comment:** "`phone_string` no longer holds a string. Could we drop the type from the name so it doesn't mislead?"

**Fix:** Remove the encoding, rely on types and IDE highlighting, and keep classes and functions small enough that the declaration is visible.

## Name classes with singular nouns and avoid noise words

`id: nm-class-names-nouns | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: class-names, nouns, singular-plural, manager, processor, data, info, helper, utils, noise-words`

**Look for in a diff:**
- A class named with a verb or a vague label
- A class for one entity with a plural name (`Customers`), or a collection class with a singular name
- Names ending in `Manager`, `Processor`, `Data`, `Info`, `Helper`, or `Utils`

**Why it matters:** Classes and objects should have noun or noun-phrase names such as `Customer`, `WikiPage`, `Account`, or `AddressParser`. Use a singular noun for one thing and a plural for a holder of many. Words like Manager and Processor add nothing, since classes already manage and process data.

**Suggested comment:** "`CustomerManager` doesn't tell me what it is responsible for. Can the name describe the actual role, for example `CustomerRegistry` or `CustomerBilling`?"

**Fix:** Pick a specific noun for the role. If you can't name it without Manager or Processor, check whether the class has too many responsibilities.

## Name methods with verbs and use named factories when constructors are unclear

`id: nm-method-names-verbs | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: method-names, verbs, predicates, mutators, accessors, static-factory, constructors, named-constructor`

**Look for in a diff:**
- A method that performs an action but has a noun or vague name
- A mutator not named for the change it makes (use `add`, `remove`, `sort`)
- A predicate that doesn't read as a question (`posted()` vs `is_posted()`)
- An overloaded constructor where the meaning of each argument is unclear

**Why it matters:** Methods should have verb or verb-phrase names (`post_payment`, `delete_page`, `save`). Accessors, mutators, and predicates should follow the language convention. When constructors can't be named, static factory methods with descriptive names (`Complex.from_real_number(23.0)`) read better than overloads, and the constructors can be made private to enforce them.

**Suggested comment:** "`Complex(23.0)` doesn't say whether that's the real or imaginary part. A `from_real_number` factory would."

**Fix:** Name methods for the action, follow local get/set/is conventions, and add named factory methods where constructors are ambiguous.

**Example:**
```python
point = Complex.from_real_number(23.0)  # clearer than Complex(23.0)
```

## Prefer keyword-only parameters over long positional lists

`id: nm-keyword-parameters | category: functions | severity: medium | source: book (Ch.4) + editorial | languages: python, ruby, csharp, clojure | tags: keyword-arguments, keyword-only, boolean-flag, positional-parameters, call-site-readability, parameters`

**Look for in a diff:**
- Boolean positional flags at call sites (`sort(pets, True)`)
- Functions with many positional parameters
- Call sites where the meaning of an argument can't be read without looking up the signature

**Why it matters:** If the language supports keyword parameters, limit positional parameters and use explicit keyword-only parameters for variations, so call sites state what they mean.

**Suggested comment:** "`sort(pets, True)` hides what `True` means. Making `reverse` keyword-only would make call sites self-explanatory."

**Fix:** Keep the essential arguments positional and make options keyword-only.

**Example:**
```python
def sort(iterable, *, key=None, reverse=False): ...


sort(pets, reverse=True)
```

## Don't be cute with names

`id: nm-dont-be-cute | category: naming | severity: low | source: book (Ch.4) | languages: any | tags: cute-names, jokes, slang, colloquial, clarity, whack, holy-hand-grenade, humor`

**Look for in a diff:**
- Jokes, pop-culture references, or slang in identifiers (`holy_hand_grenade`, `whack()`, `eat_my_shorts()`)
- Names that only make sense to people who share the author's sense of humor
- Colloquial verbs for ordinary operations (`whack` for `kill`)

**Why it matters:** Cute names are memorable only to those who share the joke, and only while they remember it. Clarity beats entertainment value: say what you mean, mean what you say.

**Suggested comment:** "`holy_hand_grenade` is fun, but a new reader won't know it deletes items. `delete_items` says it."

**Fix:** Replace with a plain name for what the code does.

## Pick one word per concept

`id: nm-one-word-per-concept | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: consistency, lexicon, ubiquitous-language, synonyms, amount-fee-price-cost, fetch-get-retrieve, naming-audit`

**Look for in a diff:**
- Different words for the same concept across modules (`amount`, `fee`, `price`, `cost`)
- Mixed verbs for the same operation (`fetch`, `get`, `retrieve`, `load`)
- A new name for a concept the codebase already has a name for

**Why it matters:** A consistent lexicon, or ubiquitous language, is a great help to anyone using your code. Pick one word per concept, use it throughout, and make sure the team knows it.

**Suggested comment:** "The rest of the codebase uses `price` for this. Could we use the same word here instead of `cost`?"

**Fix:** Use the existing term, and periodically audit names in a class, module, or test suite and harmonize them.

## Use solution-domain names for technical code and problem-domain names for business code

`id: nm-solution-vs-problem-domain | category: naming | severity: low | source: book (Ch.4) | languages: any | tags: domain-names, solution-domain, problem-domain, patterns, algorithm-names, jargon, ubiquitous-language, layering`

**Look for in a diff:**
- Business-domain jargon in low-level implementation code, or invented names for well-known concepts (a custom name for a visitor or a FIFO queue)
- Technical terms (`visitor`, `job_queue`, algorithm names) pushed into code that expresses business rules
- Names the maintainer would have to ask a customer about when a standard term exists

**Why it matters:** Readers are programmers, so in implementation code, use CS terms, algorithm names, and pattern names (`AccountVisitor`, `JobQueue`). Code that is about the business should use problem-domain names, which also give maintainers someone to ask. Don't force one kind of name on the other layer.

**Suggested comment:** "This is a standard FIFO queue. `JobQueue` would be recognized by any developer faster than `PendingThings`."

**Fix:** Use pattern and algorithm names for technical code, and business terms for business logic.

## Group related names into a class to give them context

`id: nm-add-context | category: naming | severity: medium | source: book (Ch.4) + editorial | languages: any | tags: context, primitive-obsession, grouped-variables, address, class-extraction, ambiguous-name, state, long-function`

**Look for in a diff:**
- A set of related variables that always travel together (`first_name`, `last_name`, `street`, `city`, `state`, `postcode`)
- A variable like `state` that could be an address state or a state machine, with no surrounding context
- Primitive obsession: raw floats or ints where a concept like a location would be clearer
- A long function whose local variables only make sense together (`number`, `verb`, `plural_modifier`)

**Why it matters:** Few names are meaningful on their own. Enclosing them in a well-named class, function, or namespace supplies context, and for a long function with related locals, a class gives them a clear home and lets the algorithm split into smaller functions.

**Suggested comment:** "These six variables form an address. Could they be an `Address` dataclass so `state` isn't ambiguous?"

**Fix:** Introduce a class or dataclass for the concept, move the variables into it, and then split the long function into smaller methods.

**Example:**
```python
@dataclass
class Address:
    street: str
    city: str
    state: str
    postcode: str
```

## Don't add gratuitous context to names

`id: nm-no-gratuitous-context | category: naming | severity: low | source: book (Ch.4) | languages: any | tags: prefixes, project-prefix, redundant-context, class-names, ide-completion, naming, over-qualified`

**Look for in a diff:**
- Every class prefixed with a project or app abbreviation (`GSDAccountAddress`)
- Names that repeat information already given by the module, package, or class they live in
- Class names that are over-qualified when the module already supplies the context

**Why it matters:** Prefixing every class with the same letters makes IDE completion return a huge list, working against your tools. Redundant words make names longer without making them more precise. `Address` is a fine class name, and when you must differentiate, use precise names like `PostalAddress`, `MAC`, or `URI`.

**Suggested comment:** "The `GSD` prefix repeats what the package already says and clutters autocomplete. `Address` should be enough."

**Fix:** Drop redundant prefixes and rely on modules and namespaces for context, adding only what makes the name more precise.

## Rename freely when you find a better name

`id: nm-rename-freely | category: naming | severity: low | source: book (Ch.4) + editorial | languages: any | tags: renaming, revision, iteration, temporary-name, naming-churn, audience, better-name`

**Look for in a diff:**
- A name the author admits is temporary or poor (`tmp_name`, "better name later")
- A name that confused reviewers and was left as is
- Hesitation to rename out of fear that others will object

**Why it matters:** Choosing good names takes time but saves more than it costs. Names depend on the audience and are hard to get right the first time, so iterate: all good writing is based on revision. Modern tools make renames cheap, and readers are usually grateful when names improve.

**Suggested comment:** "Not blocking, but `tmp_name` reads as a placeholder. If you have a better name in mind, a quick rename now will save the next reader time."

**Fix:** Rename with IDE tooling and keep the rename in the same PR, or a small follow-up commit if it would add noise to the diff.