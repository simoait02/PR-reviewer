# Clean Code, Chapter 34: Work as a Team, PR review rules

## Keep critical knowledge from becoming a single-person silo

`id: wt-no-knowledge-silos | category: collaboration | severity: high | source: book (Ch.34) + editorial | languages: any | tags: teamwork, bus-factor, ownership, knowledge-sharing, resilience`

**Look for in a diff:**
- A critical subsystem understandable or deployable by only one person
- Changes merged without sharing context, rationale, or operational knowledge
- Ownership files that name one expert but provide no backup path

**Why it matters:** A team must be able to continue when someone is unavailable. Knowledge silos create delivery and incident risk and make reviews less effective.

**Suggested comment:** "This critical path depends on one person’s undocumented knowledge. Could we share the design/operational context through pairing, review, or concise documentation?"

**Fix:** Pair on risky work, document decisions and runbooks, rotate ownership, and ensure at least one backup can build, test, and operate the subsystem.

## Use collaborative programming to spread context

`id: wt-collaborative-programming | category: collaboration | severity: medium | source: book (Ch.34) + editorial | languages: any | tags: pairing, mob-programming, review, context, learning`

**Look for in a diff:**
- Complex or high-risk changes developed and reviewed in isolation
- Repeated misunderstandings between people working on connected modules
- Review comments revealing that teammates lack the design context to evaluate the change

**Why it matters:** Pairing, mobbing, and active design collaboration spread the reasoning behind code, not just the final patch. Shared context improves both resilience and decision quality.

**Suggested comment:** "This change crosses a complex boundary and has no shared design context. Could we pair or hold a short collaborative review before committing to the implementation?"

**Fix:** Match collaboration to risk, rotate participants, and capture the resulting decisions in the code/repository.

## Make changes reviewable by teammates

`id: wt-reviewable-team-changes | category: collaboration | severity: high | source: book (Ch.34) + editorial | languages: any | tags: code-review, readability, context, ownership, teamwork`

**Look for in a diff:**
- A patch relying on private context, unexplained shortcuts, or unrecorded conversations
- Large changes that prevent teammates from understanding the behavior and tradeoffs
- Review feedback dismissed because only the author knows the subsystem

**Why it matters:** Review is a team safety mechanism. Code that cannot be understood by another contributor increases bus factor and allows defects to pass through unchecked.

**Suggested comment:** "The rationale for this boundary is known only from context outside the diff. Could the intent, constraint, or decision be made visible so another teammate can review it?"

**Fix:** Keep changes focused, name intent clearly, link relevant decisions, and invite review from people who will maintain adjacent behavior.

## Ensure teammates can cover operational duties

`id: wt-operational-cover | category: operations | severity: high | source: book (Ch.34) + editorial | languages: any | tags: on-call, runbooks, deployment, incidents, bus-factor`

**Look for in a diff:**
- New services/jobs/deployments with no runbook or backup operator
- Critical alerts routed only to one person
- Operational procedures requiring undocumented local knowledge

**Why it matters:** A team cannot respond reliably if the only operator is unavailable. Code review should include how the change is built, deployed, monitored, and recovered by others.

**Suggested comment:** "This introduces an operational path with no backup procedure/owner. Could the runbook, alert, rollback, and handoff information be added?"

**Fix:** Document operational contracts, automate common actions, rotate support, and verify that another teammate can perform the procedure.

## Share ownership across connected components

`id: wt-shared-boundary-context | category: architecture | severity: medium | source: book (Ch.34) + editorial | languages: any | tags: components, ownership, dependencies, collaboration, integration`

**Look for in a diff:**
- Teams owning adjacent components without a shared contract or integration practice
- A change in one component surprising dependent teams
- Interfaces changed without notifying or involving the consumers who maintain them

**Why it matters:** Component boundaries do not remove collaboration needs. Shared context around contracts prevents teams from optimizing locally while breaking the system globally.

**Suggested comment:** "This contract affects another team’s component, but the change is not accompanied by compatibility/context information. Could the consumers review the boundary and migration plan?"

**Fix:** Publish contracts and compatibility expectations, involve dependent owners early, and use integration tests or staged changes.

## Design remote collaboration intentionally

`id: wt-remote-collaboration-contract | category: collaboration | severity: low | source: book (Ch.34) + editorial | languages: any | tags: remote, async, synchronous, time-zones, communication`

**Look for in a diff:**
- Distributed teams unable to obtain timely design decisions or reviews
- Critical collaboration dependent on overlapping hours nobody has defined
- Important context trapped in private chats or unrecorded calls

**Why it matters:** Remote work can support strong collaboration when communication channels, overlap, and artifacts are deliberate. Unstructured distribution increases delay and misunderstanding.

**Suggested comment:** "This boundary decision depends on synchronous context that is not available to all contributors. Could the design, decision, and review expectations be recorded for the distributed team?"

**Fix:** Define collaboration hours/channels, use pairing or shared sessions for complex work, and record decisions in durable project artifacts.

## Preserve human connection in distributed teams

`id: wt-human-team-connection | category: team-health | severity: low | source: book (Ch.34) + editorial | languages: any | tags: remote, empathy, communication, teamwork, conflict`

**Look for in a diff:**
- Hostile or dismissive review language enabled by distance or text-only communication
- Repeated conflict caused by missing context and no direct conversation path
- Team practices that treat contributors as isolated ticket producers

**Why it matters:** Collaboration quality affects knowledge sharing and willingness to ask for help. Human connection reduces misinterpretation and makes difficult technical disagreement productive.

**Suggested comment:** "The discussion is becoming adversarial and context is being lost in text. Could we move the complex disagreement to a short direct conversation and record the decision afterward?"

**Fix:** Use respectful communication, direct conversation for high-context conflict, and durable written outcomes for the team.
