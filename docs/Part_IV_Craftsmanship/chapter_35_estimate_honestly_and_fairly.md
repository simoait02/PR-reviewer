# Clean Code, Chapter 35: Estimate Honestly and Fairly, PR review rules

## Distinguish an estimate from a commitment

`id: ef-estimate-is-not-commitment | category: planning | severity: high | source: book (Ch.35) + editorial | languages: any | tags: estimates, commitments, uncertainty, planning, honesty`

**Look for in a diff:**
- A single date presented as certain despite unresolved technical or product uncertainty
- A plan treated as an estimate because a deadline was chosen first
- “We will try” used to imply a promise without a credible delivery path

**Why it matters:** An estimate communicates uncertainty; a commitment accepts responsibility for achieving a result. Confusing them transfers risk silently and undermines planning trust.

**Suggested comment:** "This date is presented as a commitment, but the implementation still has unresolved uncertainty. Could we separate the estimate/range from the decision to commit?"

**Fix:** State whether the date is a forecast or commitment, include uncertainty, and commit only when the team has reasonable confidence.

## Express estimates as ranges with confidence

`id: ef-range-with-confidence | category: planning | severity: high | source: book (Ch.35) + editorial | languages: any | tags: estimates, ranges, probability, accuracy, precision`

**Look for in a diff:**
- Exact dates without best/nominal/worst cases or confidence level
- Uncertainty hidden in a broad scope estimate
- Precision finer than the evidence supports

**Why it matters:** A range can be accurate without pretending to be precise. It gives decision-makers the risk information needed to choose scope, sequencing, and mitigation.

**Suggested comment:** "The estimate is precise but the design/unknowns do not support that precision. Could we provide a range and explain the confidence/uncertainty?"

**Fix:** Provide best, expected, and worst cases or an equivalent probability range, and update it as evidence improves.

## Expose unknowns instead of hiding them in optimism

`id: ef-name-estimate-unknowns | category: planning | severity: high | source: book (Ch.35) + editorial | languages: any | tags: estimates, unknowns, risk, discovery, assumptions`

**Look for in a diff:**
- Estimates based on unfamiliar architecture, vendor behavior, migration complexity, or unclear requirements with no discovery work
- Risk buffers omitted to make a plan fit a desired date
- Assumptions not recorded or tested

**Why it matters:** Unknowns are part of the estimate. Making them visible allows the team to buy down uncertainty through spikes, prototypes, tests, or scope reduction.

**Suggested comment:** "This estimate depends on the unverified vendor/migration assumption. Could we identify the unknown and schedule a spike or provide a wider range?"

**Fix:** List assumptions, identify risks, run discovery work, and update the estimate based on what is learned.

## Estimate the real work, including integration and verification

`id: ef-estimate-full-delivery-work | category: planning | severity: high | source: book (Ch.35) + editorial | languages: any | tags: estimates, testing, integration, deployment, maintenance`

**Look for in a diff:**
- Implementation effort estimated without tests, refactoring, review, migration, deployment, or operational work
- A feature considered complete when only the coding task is finished
- Integration dependencies omitted from the plan

**Why it matters:** Coding is only one part of delivery. Excluding verification and integration makes estimates systematically optimistic and creates late schedule surprises.

**Suggested comment:** "The estimate covers implementation but not acceptance tests, migration, rollout, or integration with the dependent service. Could the full delivery path be included?"

**Fix:** Estimate design, implementation, tests, review, integration, deployment, documentation, and follow-up risk explicitly.

## Use experiments to increase certainty

`id: ef-buy-down-uncertainty | category: planning | severity: medium | source: book (Ch.35) + editorial | languages: any | tags: estimates, spikes, prototypes, discovery, uncertainty`

**Look for in a diff:**
- A team pressured for precision without being given time to investigate unknowns
- A high-risk estimate left unchanged despite available prototype or integration evidence
- A large commitment made before validating the hardest technical assumption

**Why it matters:** Certainty comes from doing the work or representative parts of it. Small experiments can narrow the range more honestly than debate or pressure.

**Suggested comment:** "The hardest assumption has not been exercised, so precision is not credible. Could a short spike/prototype reduce the uncertainty before committing?"

**Fix:** Run the smallest experiment that tests the dominant risk, then update scope, range, and confidence.

## Decompose large work before estimating it

`id: ef-decompose-before-estimating | category: planning | severity: medium | source: book (Ch.35) + editorial | languages: any | tags: estimates, decomposition, components, tasks, uncertainty`

**Look for in a diff:**
- A single estimate for a multi-component effort with hidden dependencies
- No separate estimates for independent work streams or integration points
- A large task whose range is too wide to support a decision

**Why it matters:** Decomposition exposes different risks and lets the team aggregate uncertainty more honestly. It also creates incremental delivery options.

**Suggested comment:** "This estimate combines several independent/high-risk pieces, so the uncertainty is hidden. Could the work be decomposed and estimated by behavior/component?"

**Fix:** Split work into coherent slices, estimate each with assumptions and confidence, and identify dependency-driven sequencing.

## Update estimates when evidence changes

`id: ef-estimates-are-revisable | category: planning | severity: medium | source: book (Ch.35) + editorial | languages: any | tags: estimates, forecasting, status, replanning, evidence`

**Look for in a diff:**
- A stale estimate preserved after new complexity, scope, or dependency information appears
- Status reports that hide variance to maintain the original date
- Team decisions based on an obsolete forecast

**Why it matters:** An estimate is a model of current knowledge, not a promise that reality will obey the original number. Updating it improves decisions and makes risk visible early.

**Suggested comment:** "The discovered integration complexity changes the forecast, but the original date remains unchanged. Could we update the range and explain the new evidence/options?"

**Fix:** Re-estimate when assumptions change, report variance without blame, and give stakeholders options such as scope, sequence, or resources.

## Say no to commitments without reasonable confidence

`id: ef-no-unreliable-commitments | category: professional-responsibility | severity: high | source: book (Ch.35) + editorial | languages: any | tags: commitments, honesty, pressure, risk, communication`

**Look for in a diff:**
- A developer promising a date they know is unlikely to meet
- Pressure framed as a test of commitment rather than a request to manage scope/risk
- A “yes” with no changed plan, resources, or risk mitigation

**Why it matters:** Unreliable commitments create a chain of failed dependencies and destroy trust. Honest uncertainty lets leaders manage risk rather than discovering it at the deadline.

**Suggested comment:** "The proposed date is not supported by the current evidence. Could we state the uncertainty and offer scope/sequence alternatives instead of making an unreliable commitment?"

**Fix:** Communicate a credible range, state what would make the date achievable, and negotiate scope/resources rather than pretending certainty.

## Separate schedule pressure from technical truth

`id: ef-deadline-does-not-change-estimate | category: planning | severity: high | source: book (Ch.35) + editorial | languages: any | tags: deadlines, estimates, risk, scope, honesty`

**Look for in a diff:**
- A desired deadline used as evidence that the work can be completed by then
- Risk removed from the estimate because the business date is fixed
- Quality/testing omitted to make the plan fit without explicit approval

**Why it matters:** A date requirement is a constraint, not a solution. Changing the estimate to match it hides the tradeoff and increases the chance of late failure or unsafe release.

**Suggested comment:** "The deadline is fixed, but the implementation effort has not changed. Could we make the scope/quality/resource tradeoff explicit rather than treating the date as the estimate?"

**Fix:** Present honest options: reduce scope, add capacity, sequence delivery, increase certainty, or accept a documented risk.

## Use estimates to manage risk, not to assign blame

`id: ef-estimates-enable-risk-management | category: collaboration | severity: medium | source: book (Ch.35) + editorial | languages: any | tags: estimates, risk-management, collaboration, forecasting, trust`

**Look for in a diff:**
- Estimate variance used to punish rather than improve assumptions and process
- Developers hiding uncertainty because honest ranges are treated as failure
- No review of why an estimate was wrong or what evidence would improve future estimates

**Why it matters:** Estimates are uncertain forecasts. A blameless feedback loop improves planning quality; fear produces optimistic numbers and less useful information.

**Suggested comment:** "The estimate variance is being treated as individual failure, but the underlying assumptions were not reviewed. Could we use the evidence to improve the forecast/process?"

**Fix:** Compare forecasts with outcomes, update assumptions, improve discovery/decomposition, and keep reporting honest and non-punitive.
