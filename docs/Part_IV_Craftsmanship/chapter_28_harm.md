# Clean Code, Chapter 28: Harm, PR review rules

## Do not knowingly ship harmful behavior

`id: ha-do-no-harm | category: professional-responsibility | severity: critical | source: book (Ch.28) + editorial | languages: any | tags: safety, ethics, harm, responsibility, users`

**Look for in a diff:**
- Behavior that intentionally deceives users, regulators, customers, or internal controls
- A known harmful outcome accepted because the requirement came from someone else
- Code that disables safeguards or hides material behavior from affected parties

**Why it matters:** Developers are responsible for understanding and communicating what their code does. “I was following instructions” does not remove responsibility for foreseeable harm.

**Suggested comment:** "This behavior bypasses a safeguard or conceals a material outcome. Has the risk been reviewed by the responsible owner, and is this behavior ethically and legally acceptable?"

**Fix:** Stop and escalate material concerns, document the behavior and risks, and remove deceptive or unsafe behavior unless explicitly justified through an accountable review.

## Match verification depth to the potential harm

`id: ha-risk-proportional-verification | category: safety | severity: critical | source: book (Ch.28) + editorial | languages: any | tags: risk, verification, safety-critical, privacy, finance`

**Look for in a diff:**
- High-impact code changed with only a happy-path or local test
- Safety, financial, privacy, or public-service behavior lacking failure analysis
- Release confidence based on a low-risk workflow despite high consequences

**Why it matters:** Perfect certainty is impossible, but acceptable uncertainty depends on the stakes. The higher the potential harm, the stronger the testing, review, rollout, monitoring, and rollback evidence must be.

**Suggested comment:** "This change affects a high-impact path, but its verification is comparable to a low-risk feature. Could the test, review, rollout, and rollback evidence be strengthened proportionally?"

**Fix:** Identify harms and failure modes, use independent review and representative tests, and require staged rollout/monitoring where appropriate.

## Speak up about unsafe release conditions

`id: ha-escalate-known-release-risk | category: professional-responsibility | severity: critical | source: book (Ch.28) + editorial | languages: any | tags: release, escalation, risk, accountability, readiness`

**Look for in a diff:**
- Known defects, missing tests, inconsistent deployments, or failed checks being suppressed for schedule reasons
- A reviewer asked to approve a change while being told not to raise a known risk
- Release readiness claims that omit unresolved safety or correctness concerns

**Why it matters:** Programmers are often the people able to detect technical danger before users experience it. Silence turns known risk into preventable harm.

**Suggested comment:** "There is a known release risk here that is not represented in the rollout decision. Could it be documented and escalated before approval?"

**Fix:** Record the risk, notify the accountable owner, define mitigation/rollback, and do not represent an unsafe state as ready.

## Make harmful states difficult to reach

`id: ha-defensive-safety-invariants | category: safety | severity: critical | source: book (Ch.28) + editorial | languages: any | tags: invariants, fail-safe, validation, safeguards, defense-in-depth`

**Look for in a diff:**
- A single flag, default, or unchecked input able to trigger a high-impact operation
- Safety checks implemented only in the caller rather than at the protected operation
- Invalid, missing, or stale state treated as permission to proceed

**Why it matters:** High-impact safeguards should not depend on every caller remembering the same check. Defensive invariants reduce the chance that a stale or inconsistent state causes harm.

**Suggested comment:** "This operation can reach the harmful state when the caller omits the check. Could the invariant be enforced at the operation boundary with a safe default?"

**Fix:** Validate at trusted boundaries, fail closed where appropriate, require explicit authorization for dangerous actions, and test invalid/stale states.

## Remove dead code and obsolete control paths

`id: ha-remove-dead-harmful-code | category: maintainability | severity: high | source: book (Ch.28) + editorial | languages: any | tags: dead-code, flags, legacy, safety, maintainability`

**Look for in a diff:**
- Disabled features, obsolete branches, stale flags, or unreachable safety-critical code retained indefinitely
- A flag repurposed while old behavior remains available through another path
- Multiple versions of a critical algorithm coexisting without clear ownership

**Why it matters:** Dead code increases uncertainty about what the system can do and can be accidentally reactivated or interact with new behavior.

**Suggested comment:** "This obsolete path remains in the codebase and shares state/flags with the active behavior. Could it be removed or isolated before the flag is reused?"

**Fix:** Delete obsolete code, remove stale flags, or isolate legacy behavior behind an explicit temporary boundary with an owner and removal plan.

## Prevent configuration and deployment drift

`id: ha-consistent-deployment-state | category: operations | severity: critical | source: book (Ch.28) + editorial | languages: any | tags: deployment, drift, versioning, consistency, rollback`

**Look for in a diff:**
- Mixed software versions across servers or workers with behavior-sensitive flags
- Manual deployment steps that can leave part of a fleet on an incompatible version
- Runtime assumptions that are not checked during startup or health verification

**Why it matters:** Inconsistent deployed states can activate incompatible code paths and produce failures that local tests never observe.

**Suggested comment:** "A partial rollout can leave incompatible versions/flags running together. Could deployment verify fleet consistency or use a compatibility-safe migration sequence?"

**Fix:** Automate rollout validation, make versions/configuration observable, support backward-compatible transitions, and provide a fast rollback.

## Preserve structural clarity in high-impact code

`id: ha-structure-supports-understanding | category: maintainability | severity: high | source: book (Ch.28) + editorial | languages: any | tags: structure, clarity, coupling, globals, safety`

**Look for in a diff:**
- Global mutable state, hidden side effects, tangled control flow, or unclear ownership in critical paths
- A reviewer unable to explain what state and dependencies a safety/financial operation uses
- Structural shortcuts that increase uncertainty about behavior

**Why it matters:** Messy structure is not merely aesthetic: it reduces the team’s ability to know what the system will do and to prevent harmful outcomes.

**Suggested comment:** "The critical path now relies on hidden global state, making its behavior difficult to reason about. Could ownership and dependencies be made explicit before merging?"

**Fix:** Encapsulate state, narrow dependencies, name policies, remove hidden side effects, and add tests that make the behavior inspectable.

## Use emergency patches with a recovery plan

`id: ha-timebox-emergency-patches | category: process | severity: high | source: book (Ch.28) + editorial | languages: any | tags: hotfix, emergency, technical-debt, rollback, cleanup`

**Look for in a diff:**
- A deliberately narrow production workaround left without tests, owner, expiry, or follow-up issue
- A hotfix that bypasses normal structure and becomes the permanent path
- Temporary safeguards that cannot be removed safely

**Do not flag when:** the patch is the documented least-risk response to an active incident and its limitations/rollback are explicit.

**Why it matters:** Emergency speed can be justified, but an untracked workaround continues to increase uncertainty and can cause a later incident.

**Suggested comment:** "This is a reasonable emergency containment, but it has no cleanup/verification path. Could we record the risk, owner, test, and removal condition?"

**Fix:** Contain the patch, add monitoring and regression coverage, document the tradeoff, and schedule the structural correction.

## Keep software changeable under changing requirements

`id: ha-preserve-softness | category: maintainability | severity: high | source: book (Ch.28) + editorial | languages: any | tags: changeability, architecture, startup, technical-debt, flexibility`

**Look for in a diff:**
- A short-term feature implemented through hard-coded branches, duplication, or premature coupling
- Structure that makes the next likely product change require broad rewrites
- “Urgency” invoked for ordinary schedule pressure rather than a real production emergency

**Why it matters:** Software exists partly to make behavior easy to change. Inflexible structure turns future requirements into expensive rework and increases the pressure to take more unsafe shortcuts.

**Suggested comment:** "This solves today’s case by hard-coding the current variant and will make the next requirement expensive. Could the change preserve a small, real extension boundary?"

**Fix:** Prioritize structural health except during genuine emergencies; use tests and incremental refactoring to keep normal change affordable.

## Require tests that support safe behavior and structural change

`id: ha-tests-enable-safe-change | category: testing | severity: high | source: book (Ch.28) + editorial | languages: any | tags: tests, regression, refactoring, confidence, professionalism`

**Look for in a diff:**
- Critical behavior changed without regression tests or an explicit compensating check
- Tests removed or weakened to make a structural change pass
- A codebase where missing tests prevent cleanup and leave behavior uncertain

**Why it matters:** Tests provide evidence that behavior works and make structural improvements safer. Without them, teams either accept unknown risk or stop improving the design.

**Suggested comment:** "This change affects a consequential behavior but removes the only regression check. Could the test be preserved or replaced before merging?"

**Fix:** Add focused and integration tests proportional to risk, keep them clean, and use the suite to refactor without fear.
