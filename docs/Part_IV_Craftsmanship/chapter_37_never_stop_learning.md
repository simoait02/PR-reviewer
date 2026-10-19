# Clean Code, Chapter 37: Never Stop Learning, PR review rules

## Keep learning part of professional practice

`id: nl-continuous-learning | category: professional-development | severity: medium | source: book (Ch.37) + editorial | languages: any | tags: learning, craft, improvement, engineering, skills`

**Look for in a diff:**
- Repeated defects or review findings with no attempt to improve the underlying practice
- A team treating current language/framework knowledge as sufficient despite changing requirements
- New technology adopted without learning the relevant failure modes or operating model

**Why it matters:** Software practices, languages, frameworks, and risks evolve. Continuous learning improves judgment and helps engineers recognize better designs before defects become expensive.

**Suggested comment:** "This change uses a new tool/pattern, but its failure modes and operating assumptions are unclear. Could we document the learning/evidence needed before relying on it?"

**Fix:** Maintain a sustainable learning habit, study relevant practices, and turn important lessons into team guidance or tests.

## Learn beyond one language or paradigm

`id: nl-breadth-of-programming-models | category: professional-development | severity: low | source: book (Ch.37) + editorial | languages: any | tags: languages, paradigms, functional, procedural, static, dynamic`

**Look for in a diff:**
- A design constrained by one language’s habits when another paradigm offers a simpler solution
- Team assumptions treated as universal despite different runtime/type/concurrency models
- New abstractions copied from a familiar ecosystem without checking local fit

**Why it matters:** Exposure to different paradigms expands the design vocabulary used in reviews. Breadth is useful for perspective; it does not require expert-level mastery of every language.

**Suggested comment:** "This solution inherits a language-specific pattern that adds complexity here. Could we compare it with a simpler approach from another paradigm or the project’s existing idioms?"

**Fix:** Study contrasting language/runtime models and apply the simplest approach that fits the current system and team.

## Learn tools and frameworks before making them architectural dependencies

`id: nl-understand-new-dependencies | category: architecture | severity: high | source: book (Ch.37) + editorial | languages: any | tags: frameworks, dependencies, learning, architecture, operations`

**Look for in a diff:**
- A framework/library introduced from a tutorial without evaluating lifecycle, testability, security, upgrade, or operational behavior
- Vendor defaults accepted without understanding their failure modes
- A dependency shaping core architecture before a representative experiment

**Why it matters:** Learning a tool’s surface API is not enough when it becomes part of the system’s boundary. Understanding its constraints prevents accidental coupling and expensive rework.

**Suggested comment:** "Before this dependency shapes the core, could we validate its testability, failure behavior, upgrade path, and operational assumptions with a small experiment?"

**Fix:** Run a focused spike/learning test, document relevant constraints, and keep the dependency behind a boundary until it earns deeper integration.

## Study established ideas as well as new trends

`id: nl-learn-past-and-present | category: professional-development | severity: low | source: book (Ch.37) + editorial | languages: any | tags: history, principles, architecture, learning, judgment`

**Look for in a diff:**
- A “new” practice adopted while ignoring established principles that address the same problem
- Historical design lessons dismissed solely because they are old
- Trend-driven architecture with no connection to the actual system need

**Why it matters:** Foundational ideas often remain useful across languages and tools. Historical context helps engineers distinguish durable principles from temporary fashion.

**Suggested comment:** "This trend introduces a new mechanism for a problem with an established boundary pattern. Could we compare the tradeoffs with the existing principle before committing?"

**Fix:** Learn from both current practice and proven prior work, then choose based on requirements and evidence.

## Turn defects and reviews into learning loops

`id: nl-learn-from-defects | category: improvement | severity: high | source: book (Ch.37) + editorial | languages: any | tags: defects, postmortem, code-review, feedback, prevention`

**Look for in a diff:**
- The same defect pattern recurring after previous incidents or review comments
- A fix that addresses one symptom without improving tests, tooling, or guidance
- Post-incident actions that are not reflected in code or process

**Why it matters:** Experience only improves the system when lessons change future behavior. Repeated defects indicate a learning or feedback gap, not merely individual error.

**Suggested comment:** "This resembles a previous defect pattern. Could we add a regression check or team-level guard so the lesson is encoded rather than relying on memory?"

**Fix:** Capture the lesson in tests, linters, design guidance, runbooks, training, or process changes appropriate to the cause.

## Share learning so it survives individual availability

`id: nl-share-technical-knowledge | category: collaboration | severity: medium | source: book (Ch.37) + editorial | languages: any | tags: knowledge-sharing, documentation, mentoring, bus-factor, team`

**Look for in a diff:**
- A useful discovery kept only in private notes or one person’s memory
- Repeated onboarding or debugging work because lessons are not documented
- A new pattern adopted without examples for maintainers

**Why it matters:** Shared knowledge improves team resilience and makes good practices repeatable. Learning that stays private becomes a single point of failure.

**Suggested comment:** "This introduces an important operational/design lesson that future maintainers will need. Could we add a concise example, decision record, or test documenting it?"

**Fix:** Share relevant knowledge through code examples, tests, documentation, pairing, reviews, and concise decision records.

## Learn through small, reversible experiments

`id: nl-reversible-learning-experiments | category: engineering-practice | severity: medium | source: book (Ch.37) + editorial | languages: any | tags: experiments, spikes, reversibility, evidence, learning`

**Look for in a diff:**
- A large irreversible adoption made before the team has validated the key assumption
- Production architecture changed to answer a question that a small prototype could answer
- Experiment results not recorded or compared with the original hypothesis

**Why it matters:** Small experiments turn uncertainty into evidence while limiting cost and rollback risk. They support better architectural and implementation decisions.

**Suggested comment:** "This commits the system before the key assumption is validated. Could a small reversible experiment measure the behavior first?"

**Fix:** State the hypothesis, build the smallest representative experiment, measure outcomes, record the result, and commit only when evidence supports it.

## Make learning sustainable and connected to the work

`id: nl-sustainable-learning-practice | category: professional-development | severity: low | source: book (Ch.37) + editorial | languages: any | tags: learning, sustainability, career, practice, balance`

**Look for in a diff:**
- Learning expectations that depend on chronic overwork or are disconnected from project needs
- Training treated as optional while new technology is required immediately
- Teams adopting tools without allocating time to understand and operate them

**Why it matters:** Continuous learning works when it is sustainable and connected to real engineering problems. Exhaustion and unplanned adoption reduce both learning quality and software quality.

**Suggested comment:** "This new technology requires learning and operational preparation that is not represented in the plan. Could we allocate sustainable time for evaluation and knowledge sharing?"

**Fix:** Make learning part of planning, provide realistic time and support, and choose tools the team can understand, operate, and maintain.
