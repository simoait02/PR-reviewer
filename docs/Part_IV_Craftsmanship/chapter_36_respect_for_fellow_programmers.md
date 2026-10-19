# Clean Code, Chapter 36: Respect for Fellow Programmers, PR review rules

## Evaluate code and decisions by relevant professional criteria

`id: rf-professional-criteria | category: collaboration | severity: high | source: book (Ch.36) + editorial | languages: any | tags: respect, code-review, skills, ethics, inclusion`

**Look for in a diff:**
- Review judgments based on identity, background, personality, or status rather than code and relevant evidence
- Technical disagreement expressed as a judgment of the person
- Dismissal of a valid concern because it came from a junior or unfamiliar contributor

**Why it matters:** Good engineering depends on standards, reasoning, ethics, and evidence. Personal bias reduces review quality and prevents the team from learning from its members.

**Suggested comment:** "Could we evaluate this concern against the behavior, evidence, and project standards rather than the contributor?"

**Fix:** Critique the code and decision, apply the same standards consistently, and invite evidence-based discussion from every contributor.

## Keep review feedback specific and actionable

`id: rf-specific-actionable-feedback | category: code-review | severity: medium | source: book (Ch.36) + editorial | languages: any | tags: code-review, feedback, respect, clarity, collaboration`

**Look for in a diff:**
- Sarcasm, insults, vague disapproval, or comments about intelligence/competence
- Feedback that identifies a problem without explaining the risk or suggested direction
- Review threads that escalate because participants are defending status rather than solving a technical issue

**Why it matters:** Specific technical feedback improves code while preserving a collaborative relationship. Personal or vague criticism creates defensiveness and does not help the author act.

**Suggested comment:** "Could this review comment state the concrete behavior/risk and a possible next step? That will make it easier to resolve without personal interpretation."

**Fix:** Describe the observed issue, why it matters, and the smallest useful change; ask questions where context may be missing.

## Apply standards consistently across contributors

`id: rf-consistent-standards | category: collaboration | severity: high | source: book (Ch.36) + editorial | languages: any | tags: fairness, code-review, standards, inclusion, consistency`

**Look for in a diff:**
- The same code quality issue accepted from one contributor and rejected from another
- Process or review requirements selectively enforced
- “Style” criticism used as a proxy for personal preference or social status

**Why it matters:** Consistent standards make review predictable and fair. Inconsistent enforcement hides defects and signals that belonging depends on identity rather than professional practice.

**Suggested comment:** "We should apply the repository’s standard consistently here. Could we point to the documented rule or decide whether the rule itself needs updating?"

**Fix:** Use documented standards, automate objective checks, and resolve genuine style disagreements at the team level.

## Make disagreement safe and evidence-based

`id: rf-safe-technical-disagreement | category: collaboration | severity: medium | source: book (Ch.36) + editorial | languages: any | tags: disagreement, psychological-safety, evidence, design-review, respect`

**Look for in a diff:**
- Contributors avoiding concerns because disagreement is punished or mocked
- Decisions made by authority without examining requirements, tests, measurements, or constraints
- A review thread looping without a clear decision owner or evidence request

**Why it matters:** Technical disagreement is a way to discover defects and improve design. Teams need a safe process for raising concerns and resolving them with evidence.

**Suggested comment:** "There are competing technical claims here. Could we agree on the requirement/measurement/test that will decide the issue and record the outcome?"

**Fix:** Separate people from ideas, request evidence, time-box debate, decide transparently, and preserve dissenting risk when it remains unresolved.

## Protect an inclusive environment

`id: rf-inclusive-professional-environment | category: collaboration | severity: critical | source: book (Ch.36) + editorial | languages: any | tags: inclusion, harassment, discrimination, respect, team-health`

**Look for in a diff:**
- Discriminatory, harassing, exclusionary, or demeaning language in code, reviews, issues, or documentation
- Jokes or stereotypes that make contributors less safe to participate
- Team practices that exclude people from necessary context or opportunities based on identity

**Why it matters:** A professional team must be safe for people with different identities and backgrounds. Exclusion harms individuals, reduces information flow, and damages engineering quality.

**Suggested comment:** "This language is not relevant to the technical decision and can exclude or demean contributors. Could it be removed and replaced with neutral, precise wording?"

**Fix:** Remove discriminatory content, follow the team’s conduct/reporting process, and ensure participation and access are based on relevant professional criteria.

## Respect skill, ethics, and discipline regardless of seniority

`id: rf-respect-professional-contribution | category: collaboration | severity: medium | source: book (Ch.36) + editorial | languages: any | tags: mentorship, seniority, ethics, skill, teamwork`

**Look for in a diff:**
- Seniority used to silence a technically valid concern
- A junior contributor’s careful work dismissed without review
- Ethical or quality standards waived for a favored contributor or leader

**Why it matters:** Professional respect is earned and demonstrated through skill, standards, discipline, and ethics—not title or social identity. Teams are stronger when everyone can contribute and challenge risk.

**Suggested comment:** "Could we evaluate this contribution against the same technical and ethical standard used for every contributor, independent of seniority?"

**Fix:** Review evidence and outcomes consistently, mentor where needed, and make accountability apply to every role.
