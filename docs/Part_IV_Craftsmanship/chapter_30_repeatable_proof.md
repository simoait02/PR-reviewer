# Clean Code, Chapter 30: Repeatable Proof, PR review rules

## Provide a quick, reliable, repeatable demonstration

`id: rp-quick-sure-repeatable-proof | category: testing | severity: critical | source: book (Ch.30) + editorial | languages: any | tags: proof, tests, release, repeatability, confidence`

**Look for in a diff:**
- A release with no automated evidence that changed behavior works
- Verification that depends on one person’s manual steps or local environment
- Tests that produce ambiguous results or cannot be repeated by CI and teammates

**Why it matters:** A professional release needs fast evidence that the implemented behavior matches what was paid for and expected. Repeatable proof reduces uncertainty and supports safe change.

**Suggested comment:** "This release path has no quick repeatable demonstration for the changed behavior. Could the acceptance/regression evidence be automated and runnable by anyone?"

**Fix:** Add automated tests and checks that run quickly, fail clearly, and can be repeated in a clean environment.

## Use structured control flow that can be reasoned about

`id: rp-structured-control-flow | category: design | severity: high | source: book (Ch.30) + editorial | languages: any | tags: structured-programming, control-flow, reasoning, goto, loops`

**Look for in a diff:**
- Unconstrained jumps, hidden re-entry, or control flow that bypasses invariants and cleanup
- Loops with unclear entry/exit conditions or multiple hidden termination paths
- A function whose behavior cannot be decomposed into sequence, selection, and iteration

**Why it matters:** Structured control flow makes inputs, outputs, and loop invariants easier to reason about and test. Complex jumps make correctness arguments and failure analysis harder.

**Do not flag when:** a language/runtime construct is necessary and the control flow is isolated, documented, and covered by focused tests.

**Suggested comment:** "This control flow can enter/exit the operation through several paths, making cleanup and invariants hard to reason about. Could it be expressed with structured branches/loops?"

**Fix:** Use explicit sequence, selection, and iteration; isolate unavoidable control transfers behind a small tested abstraction.

## Decompose behavior into small testable units

`id: rp-functional-decomposition | category: design | severity: high | source: book (Ch.30) + editorial | languages: any | tags: decomposition, functions, abstraction, testing, cohesion`

**Look for in a diff:**
- A large function containing multiple independent decisions and side effects
- Tests that require many unrelated fixtures to exercise one branch
- A control-flow change impossible to verify without running the entire system

**Why it matters:** Functional decomposition creates small units whose inputs, outputs, and invariants can be checked independently. It makes both review and debugging more precise.

**Suggested comment:** "This function combines several behaviors, so its correctness cannot be checked locally. Could the policy be decomposed into cohesive testable units?"

**Fix:** Extract cohesive operations with explicit inputs/outputs and preserve a clear top-level orchestration flow.

## Test each required behavior, not just execution paths

`id: rp-tests-cover-required-behavior | category: testing | severity: critical | source: book (Ch.30) + editorial | languages: any | tags: tests, behavior, coverage, requirements, assertions`

**Look for in a diff:**
- Code executed by tests but with no meaningful assertion about the requirement
- Line/branch coverage used as proof while important outcomes remain unspecified
- New behavior inferred from implementation rather than stated in tests

**Why it matters:** Tests are empirical evidence, not a formal proof. They provide confidence only when they assert the behaviors and invariants the system must preserve.

**Suggested comment:** "This path is executed, but the test does not assert the required outcome. Could the behavior contract be made explicit?"

**Fix:** Map requirements to focused tests with meaningful expected outcomes, including failure and boundary cases.

## Keep the proof suite fast enough to run frequently

`id: rp-fast-feedback-suite | category: testing | severity: high | source: book (Ch.30) + editorial | languages: any | tags: tests, speed, feedback, ci, refactoring`

**Look for in a diff:**
- A unit/regression suite slowed by unnecessary integration setup or sleeps
- Developers avoiding the suite during changes because it takes too long
- Critical checks available only in a long nightly job with no fast local subset

**Why it matters:** “Quick” proof supports frequent feedback and refactoring. Delayed feedback increases the cost of locating and correcting defects.

**Suggested comment:** "This adds external setup to a fast feedback suite. Could the core behavior use a fake, with the integration check kept in a separate layer?"

**Fix:** Keep a fast deterministic suite for local/PR feedback and isolate slower system/load checks with clear ownership and reporting.

## Make failures unambiguous and actionable

`id: rp-clear-pass-fail-results | category: testing | severity: high | source: book (Ch.30) + editorial | languages: any | tags: tests, diagnostics, pass-fail, assertions, ci`

**Look for in a diff:**
- Tests requiring log inspection or manual output comparison to decide correctness
- Generic failures that omit expected/actual state and scenario context
- Warnings or skipped tests presented as a successful verification result

**Why it matters:** Proof is useful only when the team can tell whether it passed and what to fix when it fails. Ambiguous signals undermine release decisions.

**Suggested comment:** "The check can be skipped/needs manual interpretation, so the result is not a reliable gate. Could it produce an explicit pass/fail with actionable diagnostics?"

**Fix:** Encode acceptance criteria, fail on unavailable required checks, and report scenario, expected, actual, and environment details.

## Make verification repeatable for any contributor and environment

`id: rp-repeatable-environment | category: testing | severity: high | source: book (Ch.30) + editorial | languages: any | tags: repeatability, environment, ci, reproducibility, test-data`

**Look for in a diff:**
- Tests depending on machine-specific paths, state, locale, time, network, or undocumented setup
- Test data created manually or reused across runs
- A release check that only works on the author’s workstation

**Why it matters:** Repeatability is what turns one successful demonstration into dependable evidence. Everyone should be able to rerun the proof and obtain the same result.

**Suggested comment:** "This verification depends on local state/setup that CI and other developers do not have. Could the environment and test data be made reproducible?"

**Fix:** Automate setup/teardown, control time/randomness/locale, isolate data, and run the same commands in CI and locally.

## Use tests as empirical proof, not absolute certainty

`id: rp-tests-are-evidence | category: review-guidance | severity: medium | source: book (Ch.30) + editorial | languages: any | tags: tests, evidence, confidence, limitations, risk`

**Look for in a diff:**
- A claim that passing tests proves all possible behavior correct
- High-risk paths relying on a narrow test sample
- Test limitations ignored because the suite is green

**Why it matters:** Tests can reveal defects and build strong confidence, but they do not cover every possible execution. Risk, coverage, invariants, and independent review still matter.

**Suggested comment:** "The suite provides useful evidence, but this high-risk path has untested input/schedule combinations. Could the remaining uncertainty and compensating checks be documented?"

**Fix:** Treat passing tests as evidence proportional to their coverage and quality; supplement them with reviews, contracts, static checks, and operational safeguards.

## Keep proof aligned with the release contract

`id: rp-release-proof-matches-contract | category: delivery | severity: critical | source: book (Ch.30) + editorial | languages: any | tags: release, acceptance, requirements, regression, contract`

**Look for in a diff:**
- CI checks that remain green while the user-visible requirement changed
- Tests updated to match implementation without confirming the requirement
- Release evidence covering internals but not the promised behavior

**Why it matters:** The proof suite should demonstrate that the delivered system does what users and stakeholders paid for, not merely that code executes.

**Suggested comment:** "The tests were updated to the new implementation, but the release contract is not asserted. Could the expected user-visible behavior be preserved explicitly?"

**Fix:** Trace release tests to acceptance criteria, review expected outcomes independently, and retain regression coverage for unchanged contracts.

## Run proof continuously, not only at release time

`id: rp-continuous-proof | category: delivery | severity: high | source: book (Ch.30) + editorial | languages: any | tags: ci, continuous, tests, regression, feedback`

**Look for in a diff:**
- Tests that run only before deployment or after a large batch of changes
- A broken build tolerated until release preparation
- No visible status for the current test/release proof

**Why it matters:** Frequent verification localizes defects and prevents uncertainty from accumulating. A release-only test suite gives feedback too late to be cheap.

**Suggested comment:** "This important regression check runs only at release time, so failures will be expensive to diagnose. Could it run in the continuous build?"

**Fix:** Run fast proof on every change, publish visible results, and reserve slower full-system validation for appropriate stages.
