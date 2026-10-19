# Clean Code, Chapter 33: Maintain High Productivity, PR review rules

## Optimize the whole feedback loop, not typing speed

`id: mp-optimize-feedback-loop | category: productivity | severity: medium | source: book (Ch.33) + editorial | languages: any | tags: productivity, build, test, debug, deploy, feedback`

**Look for in a diff:**
- A local coding optimization that slows build, test, debug, or deployment cycles
- New process/tooling friction ignored because the code change itself is small
- Productivity measured by lines or features rather than completed reliable feedback cycles

**Why it matters:** Writing code is only one part of delivery. Fast feedback through build, test, diagnosis, and deployment lets the team move quickly without sacrificing quality.

**Suggested comment:** "This change increases the build/test/deploy feedback cost. Could we preserve or improve the whole loop rather than optimize only implementation speed?"

**Fix:** Measure cycle time across edit, build, test, debug, and deploy; remove bottlenecks that affect the team’s ability to verify changes.

## Keep builds fast enough for small changes

`id: mp-fast-builds | category: build | severity: high | source: book (Ch.33) + editorial | languages: any | tags: build, speed, incremental, caching, ci`

**Look for in a diff:**
- A small edit requiring a full slow rebuild without a clear reason
- New dependencies or generation steps that expand every build unnecessarily
- Developers batching changes because build feedback is too slow

**Why it matters:** Slow builds lengthen the cycle, increase merge size, and delay integration failures. Build speed is part of the architecture and developer experience.

**Suggested comment:** "This adds a costly step to every build and may encourage larger change batches. Could it be incremental, cached, or moved to a slower validation stage?"

**Fix:** Measure and remove bottlenecks, use safe incremental builds/caching, and keep fast local/PR checks separate from deep validation.

## Keep tests fast without reducing meaningful coverage

`id: mp-fast-tests-with-real-coverage | category: testing | severity: high | source: book (Ch.33) + editorial | languages: any | tags: tests, speed, mocks, integration, coverage, feedback`

**Look for in a diff:**
- Repeated login/navigation/database/network setup in every test
- Slow peripheral operations on the critical unit-test path
- Test shortcuts that remove the behavior actually being verified

**Why it matters:** Fast tests run frequently, but speed must not come from deleting meaningful assertions. Controlled test APIs and doubles can bypass repeated mechanics while preserving contracts.

**Suggested comment:** "Every test repeats the same slow setup, delaying feedback. Could a controlled fixture/test API bypass the repeated path while keeping one dedicated test for that integration?"

**Fix:** Isolate slow boundaries, reuse safe setup, use realistic fakes, and retain focused tests for each external contract.

## Automate deployment and test the deployment procedure

`id: mp-automated-tested-deployment | category: delivery | severity: high | source: book (Ch.33) + editorial | languages: any | tags: deployment, automation, scripts, rollback, ci-cd`

**Look for in a diff:**
- Manual deployment commands, configuration edits, or server preparation
- Deployment scripts changed without validation in a disposable/staging environment
- No automated rollback or health verification for a new deployment step

**Why it matters:** Deployment is a procedure that can fail like application code. Automation makes it repeatable, while tests and health checks make releases safer.

**Suggested comment:** "This deployment change depends on a manual step and has no verification/rollback check. Could the procedure be automated and exercised before production?"

**Fix:** Version deployment code, automate setup/migrations/rollout, verify health, and test rollback paths.

## Reduce debugging by improving proof and diagnostics

`id: mp-debugging-through-proof | category: diagnostics | severity: medium | source: book (Ch.33) + editorial | languages: any | tags: debugging, tests, diagnostics, observability, mutation-testing`

**Look for in a diff:**
- A recurring defect class with no regression test or useful failure output
- Logging added instead of isolating the behavior and testing the invariant
- A production issue that cannot be connected to a reproducible scenario

**Why it matters:** Strong tests, semantic checks, and diagnostics shorten debugging by turning vague failures into localized evidence.

**Suggested comment:** "This failure will require log archaeology because the invariant is not tested or reported clearly. Could we add a focused regression check and actionable diagnostics?"

**Fix:** Add a reproducer/regression test, improve failure context, and isolate the responsible behavior or boundary.

## Protect focused work from unnecessary interruption

`id: mp-protect-focused-work | category: collaboration | severity: low | source: book (Ch.33) + editorial | languages: any | tags: focus, interruptions, meetings, collaboration, productivity`

**Look for in a diff:**
- Review/process changes that require repeated context switching for trivial updates
- Meetings or synchronous coordination added without a decision or collaboration need
- Critical work blocked by unclear ownership or interruption channels

**Why it matters:** Context switching reduces the quality and speed of reasoning, especially for complex design and concurrency work. Teams should make necessary collaboration easy and unnecessary interruption rare.

**Suggested comment:** "This process adds repeated synchronous interruptions without a decision need. Could the information/review be handled asynchronously or with a focused session?"

**Fix:** Use clear ownership, concise async context, time-boxed meetings, and protected focus periods while preserving necessary collaboration.

## Use pairing/review to counter tunnel vision

`id: mp-counter-tunnel-vision | category: collaboration | severity: medium | source: book (Ch.33) + editorial | languages: any | tags: pairing, review, focus, design, quality`

**Look for in a diff:**
- A complex change authored and merged without a second perspective
- Hyper-focused implementation that skips requirements, failure, or structural review
- A critical decision justified only by the author’s local reasoning

**Why it matters:** Collaboration exposes assumptions and keeps intense focus from narrowing the solution. A second perspective is especially valuable for risky boundaries and production changes.

**Suggested comment:** "This change has significant design/operational risk but no independent review evidence. Could we pair or request a focused review before merging?"

**Fix:** Match collaboration intensity to risk, use pairing/design review for complex changes, and record important decisions.

## Treat developer capacity as a finite system resource

`id: mp-sustainable-engineering-capacity | category: team-health | severity: medium | source: book (Ch.33) + editorial | languages: any | tags: sustainability, workload, quality, interruptions, planning`

**Look for in a diff:**
- Schedule pressure that removes testing, cleanup, review, or recovery time
- Repeated emergency work caused by known tooling/process bottlenecks
- A plan that assumes constant concentration and no capacity for maintenance

**Why it matters:** Unsustainable pace increases defects and structural degradation, which later reduces productivity. Sustainable capacity is part of delivering reliably.

**Suggested comment:** "The plan leaves no capacity for verification/cleanup and repeats the same bottleneck. Could the scope or schedule account for the work needed to keep the system healthy?"

**Fix:** Plan capacity for testing, maintenance, incidents, and collaboration; address systemic friction instead of relying on heroics.

## Keep productivity measures aligned with quality

`id: mp-measure-quality-and-flow | category: process | severity: low | source: book (Ch.33) + editorial | languages: any | tags: metrics, productivity, flow, quality, incentives`

**Look for in a diff:**
- Incentives based only on lines changed, tickets closed, or meeting attendance
- Process changes that improve a local metric while increasing defects or cycle time
- Build/test/deployment friction omitted from team productivity discussions

**Why it matters:** Narrow metrics create perverse incentives and can reward unsafe speed. Useful measures include flow time, recovery, build health, defect rates, and confidence in releases.

**Suggested comment:** "This metric may reward output while hiding test/deployment/rework cost. Could we evaluate the effect on end-to-end flow and quality as well?"

**Fix:** Use balanced measures and inspect whether the team can deliver tested, maintainable behavior faster over time.
