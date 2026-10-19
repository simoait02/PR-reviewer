# Clean Code, Chapter 17: AIs, LLMs, and God Knows What, PR review rules

## Treat AI-generated code as unverified implementation

`id: ai-generated-code-needs-review | category: ai-review | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, llm, generated-code, verification, correctness`

**Look for in a diff:**
- AI-generated code accepted because it compiles or looks plausible
- No evidence that the implementation was checked against requirements and failure cases
- Generated code added across a broad boundary without focused human review

**Why it matters:** LLM output is probabilistic and can contain subtle semantic, security, or integration defects while appearing polished. Compilation is not evidence that the behavior is correct.

**Suggested comment:** "This code appears generated, but the diff does not show how its behavior was verified against the requirement and edge cases. Could you add tests or explain the independent checks?"

**Fix:** Review generated code as if it came from an unfamiliar contributor, verify its contract, and keep the change small enough to inspect.

## Define ambiguous terms before prompting or implementing

`id: ai-define-domain-terms | category: requirements | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, prompt, ambiguity, specification, domain-language`

**Look for in a diff:**
- Requirements using undefined terms such as "word," "sentence," "active," "valid," or "next"
- Different code paths making different assumptions about the same domain term
- Prompt instructions that describe intent without defining inputs, boundaries, or special cases

**Why it matters:** Ambiguous requirements lead humans and models to fill gaps with incompatible assumptions. Precise definitions make implementation and review deterministic.

**Suggested comment:** "The requirement uses `valid` without defining the accepted forms or boundary cases. Could the domain term be specified before we rely on this implementation?"

**Fix:** Define terms, units, normalization rules, boundaries, and exceptional cases in the requirement or contract.

## Specify inputs, actions, and outputs explicitly

`id: ai-explicit-input-action-output | category: requirements | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, specification, aaa, contract, behavior`

**Look for in a diff:**
- A prompt or ticket describing a goal without concrete examples
- Missing behavior for empty, malformed, missing, or repeated inputs
- Expected output implied by prose rather than stated as an observable result

**Why it matters:** Input/action/output contracts constrain interpretation and give reviewers something testable to compare with the implementation.

**Suggested comment:** "The desired result is implied but not defined for this input. Could the request specify the input, action, and expected output, including the relevant edge case?"

**Fix:** Express each important behavior as concrete inputs, one action, and an expected observable result.

## Overload specifications with independent examples and tests

`id: ai-overload-specification-with-tests | category: ai-review | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, specifications, examples, scenarios, redundancy, tests`

**Look for in a diff:**
- A single prose prompt used as the only source of truth for complex behavior
- Examples that do not cover the interpretation-sensitive parts of the requirement
- Tests that merely repeat the implementation’s assumptions

**Why it matters:** A formal definition and independent scenarios act as cross-checks. If one statement is misunderstood, the other can expose the inconsistency.

**Suggested comment:** "This behavior depends on several interpretation-sensitive rules but has only prose coverage. Could the specification be paired with representative Given-When-Then cases?"

**Fix:** Combine definitions, constraints, examples, invariants, and independent tests that exercise the same contract from different angles.

## Use tests to constrain generated changes

`id: ai-tests-constrain-generation | category: ai-review | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, llm, tests, regression, incremental-change`

**Look for in a diff:**
- A prompt regenerated the whole module for a small change
- Existing behavior is not covered before asking an AI to modify it
- A revised output fixes one symptom while silently changing unrelated behavior

**Why it matters:** Regeneration can produce a different interpretation of every ambiguous instruction. A passing regression suite makes unintended changes visible and supports incremental edits.

**Suggested comment:** "This change regenerates the implementation for a narrow fix, but existing behavior is not protected by tests. Could the current contract be captured before accepting the new output?"

**Fix:** Establish regression tests, request narrow changes, inspect the complete diff, and rerun the full relevant suite after each generation.

## Prefer incremental AI-assisted changes

`id: ai-incremental-changes | category: process | severity: medium | source: book (Ch.17) + editorial | languages: any | tags: ai, incremental, diff-size, reviewability, rollback`

**Look for in a diff:**
- Large generated rewrites for a localized requirement
- Unrelated formatting, renaming, and dependency changes mixed with generated behavior
- A change too large to review or revert by behavior

**Why it matters:** Small increments limit blast radius and make it possible to identify which instruction or generated change introduced a defect.

**Suggested comment:** "The generated rewrite includes unrelated changes, making behavioral review difficult. Could the request be narrowed and the diff split into reviewable increments?"

**Fix:** Ask for one bounded change, preserve unrelated code, and separate cleanup or refactoring from generated feature behavior.

## Verify generated tests independently

`id: ai-independent-test-verification | category: testing | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, tests, independence, oracle, verification`

**Look for in a diff:**
- Implementation and tests generated from the same ambiguous prompt
- Tests that duplicate the implementation algorithm instead of checking outcomes
- A green generated suite with no manually reviewed examples or independent oracle

**Why it matters:** A model can consistently encode the same misunderstanding in both production and test code. Passing tests do not prove correctness when the tests share the implementation’s assumptions.

**Suggested comment:** "The implementation and tests appear to share the same generated assumptions. Could the expected cases be reviewed or derived independently from the requirement?"

**Fix:** Review test cases against external requirements, use independent expected values, and add boundary cases not suggested by the implementation.

## Review normalization, punctuation, and case rules explicitly

`id: ai-explicit-normalization-rules | category: correctness | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, parsing, normalization, unicode, case-sensitivity, whitespace`

**Look for in a diff:**
- Text processing that leaves case, whitespace, punctuation, Unicode, or end-of-input behavior implicit
- Fixes for one formatting symptom without a defined normalization policy
- Different operations using different tokenization or comparison rules

**Why it matters:** Text edge cases are easy for generated code to mishandle and difficult to notice in a happy-path example. Explicit normalization rules make behavior stable and testable.

**Suggested comment:** "The parser’s treatment of case and repeated whitespace is implicit. Could the normalization policy be defined and covered by examples before relying on this code?"

**Fix:** Define tokenization and normalization once, implement it consistently, and test punctuation, spacing, case, Unicode, and terminal inputs.

## Do not patch symptoms without finding the contract violation

`id: ai-fix-root-cause | category: correctness | severity: medium | source: book (Ch.17) + editorial | languages: any | tags: ai, debugging, root-cause, prompt, regression`

**Look for in a diff:**
- A prompt or code change that adds a special case only for a reported output
- A formatting fix with no explanation of why the original behavior was wrong
- Repeated prompt patches accumulating contradictory instructions

**Why it matters:** Symptom patches can hide an unclear definition and create new regressions. The correct fix should address the violated contract, not only the observed example.

**Suggested comment:** "This handles the reported example but does not explain the general rule. Could the underlying contract be clarified and tested so the fix covers the class of failures?"

**Fix:** Reproduce the defect, identify the violated invariant, update the specification and regression cases, then implement the smallest general correction.

## Treat prompts as versioned engineering artifacts

`id: ai-version-prompt-contracts | category: maintainability | severity: medium | source: book (Ch.17) + editorial | languages: any | tags: ai, prompts, reproducibility, versioning, provenance`

**Look for in a diff:**
- Critical generated code with no record of the prompt, model assumptions, or source requirements
- A prompt changed without rerunning representative evaluations
- Generated output that cannot be reproduced or explained by the team

**Why it matters:** Prompt changes can alter output broadly. Traceability helps reviewers understand provenance and detect regressions when models, context, or instructions change.

**Suggested comment:** "This behavior depends on generated output, but the prompt and evaluation cases are not traceable. Could the generation inputs and verification suite be kept with the change?"

**Fix:** Version important prompts or specifications, record relevant model/context changes, and rerun deterministic evaluations before accepting new output.

## Keep human reasoning responsible for requirements and contracts

`id: ai-human-contract-ownership | category: ai-review | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, human-review, requirements, contracts, accountability`

**Look for in a diff:**
- Business or safety decisions delegated to an AI without an accountable owner
- A generated implementation treated as the requirement rather than as a proposal
- No human review of security, privacy, failure, or dependency implications

**Why it matters:** Models can generate code but do not own the correctness of the requirement. Humans must reason about intent, tradeoffs, constraints, and consequences.

**Suggested comment:** "The generated behavior makes a requirement-level decision without an explicit owner or rationale. Could the contract and its risks be reviewed by the responsible engineer or domain owner?"

**Fix:** Keep humans responsible for requirements, contracts, architecture, security, and final acceptance; use AI to accelerate bounded implementation work.

## Use AI output as a proposal for architecture, not architectural evidence

`id: ai-architecture-needs-independent-review | category: architecture | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, architecture, boundaries, dependencies, design-review`

**Look for in a diff:**
- Generated abstractions accepted without checking dependency direction or ownership
- Frameworks, layers, or interfaces introduced because the model suggested them
- Local tests passing while module boundaries or operational constraints remain unexamined

**Why it matters:** AI can produce locally coherent structure that is globally wrong, overcomplicated, or inconsistent with the system’s change boundaries.

**Suggested comment:** "The generated abstraction may be locally reasonable, but its dependency direction and ownership need architectural evidence. Could the boundary be reviewed independently of the generated code?"

**Fix:** Evaluate architecture against actual change pressure, operational constraints, dependency rules, and independent design criteria.

## Evaluate AI behavior with representative and adversarial cases

`id: ai-evaluate-representative-adversarial-cases | category: testing | severity: high | source: book (Ch.17) + editorial | languages: any | tags: ai, evaluation, edge-cases, adversarial, regression, llm`

**Look for in a diff:**
- Only one or two successful examples used to validate generated behavior
- Missing malformed, ambiguous, adversarial, long, empty, or distribution-sensitive inputs
- Probabilistic output accepted without thresholds, invariants, or repeatability checks

**Why it matters:** Generated and AI-driven behavior often fails outside the examples that inspired it. Representative and adversarial evaluation reveals ambiguity, instability, and unsafe assumptions.

**Suggested comment:** "The evaluation covers the happy example but not malformed or ambiguous inputs. Could representative edge cases and the acceptable output criteria be added?"

**Fix:** Build a versioned evaluation set with boundary, failure, adversarial, and representative cases; define thresholds and investigate regressions.

## Keep generated code understandable and maintainable

`id: ai-generated-code-must-be-maintainable | category: maintainability | severity: medium | source: book (Ch.17) + editorial | languages: any | tags: ai, readability, duplication, complexity, ownership`

**Look for in a diff:**
- Repeated generated logic, unnecessary abstractions, unexplained branches, or opaque names
- Code no team member can confidently modify without regenerating it
- Generated comments that describe intent but do not match behavior

**Why it matters:** AI assistance does not remove future maintenance. Unclear generated code increases the cost of review, debugging, and the next change.

**Suggested comment:** "This generated implementation is difficult to understand and modify locally. Could it be simplified or refactored into the project’s established patterns before merging?"

**Fix:** Apply normal readability, cohesion, duplication, security, and ownership standards; regenerate only when that remains the clearest maintainable option.
