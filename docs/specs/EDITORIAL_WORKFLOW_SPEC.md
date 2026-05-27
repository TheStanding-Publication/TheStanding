# The Standing: Editorial Workflow Skill

## Purpose
Define the human review and approval process for entries before they are recorded in the archive. This skill addresses two intake channels (monitoring and tips) with different workflows, and ensures all entries meet The Standing's editorial standards while respecting the broken-windows principle (no significance threshold — proper sourcing is what matters).

## Inclusion judgment is owned by ARCHIVE_FIT

The machine-level inclusion judgment — does this story belong in the
archive at all? — lives in [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md).
By the time an issue reaches an editor for any of the review gates
below, archive-fit has already rendered a verdict (`archive-fit`,
`archive-fit-merge`, `not-fit`, or `blocked-on-taxonomy`) on it as a
label plus an explanatory comment.

The editor's job at each gate is no longer to re-derive the inclusion
judgment from scratch — it is to **read archive-fit's verdict and decide
whether to accept, override, or escalate it**. Specifically:

- **`archive-fit`** — proceed with the gate as usual. The verdict
  comment names the ideal, abuses, and any precedent entries; use those
  as the starting point for editorial review rather than rebuilding from
  the issue body.
- **`archive-fit-merge`** — the gate's outcome is usually "merge into
  the named existing entry," not "approve as new." Override only when
  you see something archive-fit missed about why the candidate is a
  distinct event (different date, location, or actors — see the
  event-level dedup rule in archive-fit Step 5).
- **`not-fit`** — close the issue with the verdict comment as
  reasoning, unless you have a substantive disagreement; if so, document
  the override in a reply comment so archive-fit's reasoning trail and
  your override sit side by side.
- **`blocked-on-taxonomy`** — review the taxonomy PR archive-fit opened
  before this gate proceeds. The issue is held until the PR resolves.

The rubrics below (decision points, approval criteria, rejection
criteria) remain useful as **editorial standards for the human
judgment** that archive-fit's verdict cannot fully replace — headline
neutrality, framing, summary quality, source diversity, broken-windows
application at the edges. Where the rubrics duplicate archive-fit (does
the story match an abuse, is it a duplicate, is it in mission scope),
defer to archive-fit and don't re-derive.

## Key Principle: Broken Windows
*No anti-democratic action is too small to record.* An entry is worthy of the archive if it credibly describes an abuse in The Standing's taxonomy and meets the sourcing standard. There is no requirement that an event be part of a wider pattern. The threshold is proper sourcing + relevant abuse, not "significance" or "part of a bigger story." Small accumulating breaches are themselves the pattern.

## Two Intake Channels

### Channel 1: Monitoring Intake (`monitoring-intake` label)
**Source:** Automated news monitoring (NEWS_RESEARCH_SPEC.md)
**Review stages:** Issue creation (automated, human-viewable) → PR review (editorial approval gate)

### Channel 2: Tip Submissions (`tip` label)
**Source:** External tips via email (tips@thestanding.us) or GitHub issue form
**Review stages:** Issue review (editorial triage) → PR review (editorial approval gate)

---

## Workflow

### A. Monitoring Intake Issues (Automated Monitoring)

#### 1. Issue Created
- **Actor:** Automated monitoring system
- **Trigger:** Story evaluated as relevant by Claude agent
- **Contents:** Full comprehensive research (event date, jurisdiction, location, actors, evidence, mapped abuses)
- **Labels:** `monitoring-intake`, `needs-research`, `[abuse-slug]`
- **Status:** Issue created, awaiting editorial review

#### 2. Editorial Review of Issue (Optional)
*Editors can optionally review and comment on the raw issue before moving to PR.*

**Decision points:**
- Is this credibly describing an abuse in the taxonomy?
- Are the sources reliable (primary source or 2+ investigative sources)?
- Are the actors correctly identified?
- Is the jurisdiction and location correct?
- Are the mapped abuses appropriate?

**Outcome:** 
- If major issues found, comment on issue and let monitoring system know to hold or revise
- If acceptable, proceed to PR review (step 3)
- Do NOT require editorial approval at this stage for monitoring intake — the PR review is the gate

#### 3. Entry Recording & PR Creation
- **Actor:** Automated entry recording system (ENTRY_RECORDING_SPEC.md)
- **Trigger:** Issue review complete, no blockers
- **Process:** Run automated validation checks (URL validation, actors verification, location verification, taxonomy validation)
- **Output:** 
  - Entry file created in `/src/entries/YYYY/MM/DD/[slug].md`
  - PR created with `[Entry] [Headline]` title
  - PR includes validation checklist showing all checks passed
  - Links to original issue number

#### 4. Editorial Review of PR (Approval Gate)
**This is the primary review stage for monitoring intake.**

**Decision points:**
- ✓ All automated checks passed?
- ✓ Event meets criteria (credible source + relevant abuse)?
- ✓ Headline is factual and neutral?
- ✓ Summary is 2-3 sentences and accurate?
- ✓ Abuses are correctly mapped (verify against abuse definitions)?
- ✓ Actors are correctly identified and normalized?
- ✓ Location is accurate and complete for the jurisdiction level?
- ✓ No missing or suspicious sources?

**Approval criteria:**
- Passes broken-windows threshold: credible source + relevant abuse
- No factual errors in headline/summary
- Abuses are correctly mapped
- Meets the editorial standards in `/standards/`

**Rejection criteria:**
- Sources do not meet floor (not primary + not 2x investigative)
- Abuses are misapplied or not in taxonomy
- Event does not describe an abuse (e.g., just political disagreement, no abuse pattern)
- Significant factual errors that cannot be corrected

**Actions:**
- Approve: Comment "Approved for archive" and merge PR
- Revise: Comment on PR with specific changes needed; request changes
- Reject: Close PR and issue with explanation

---

### B. Tip Submissions (External Tips)

#### 1. Issue Created
- **Actor:** Public via email (tips@thestanding.us) or GitHub issue form
- **Trigger:** Tip received
- **Contents:** Depends on submission format (may be sparse)
- **Labels:** `tip`, `needs-research`, `awaiting-triage`
- **Status:** Issue created, awaiting editorial triage

#### 2. Editorial Triage Review (First Gate)
**This is the gating decision: is this worth investigating?**

**Process:**
- Editor reviews tip for basic relevance
- If clearly not related to The Standing's mission, close with explanation

**Decision points:**
- Does this describe potential abuse within The Standing's taxonomy?
- Is the source credible enough to investigate?
- Is there enough detail to research further?

**Approval criteria:**
- Could plausibly relate to one or more abuses
- Tipster provides some verifiable detail (name, date, location, organization)
- At least one potential source identified

**Rejection criteria:**
- Clearly outside mission (e.g., celebrity gossip, local crime unrelated to institutional abuse)
- No verifiable details provided
- Tipster requests anonymity on claims that require verification
- Duplicate of existing entry

**Actions:**
- Approve: Add `approved-for-research` label; begin research phase
- Reject: Close issue with explanation; thank tipster for submission

#### 3. Research Phase (Post-Approval)
**Actor:** Editorial team or Claude agent (per workflow design)

**Process:**
- Conduct comprehensive research (event date, jurisdiction, location, actors, evidence)
- Find primary sources or 2+ investigative sources
- Map to specific abuses in taxonomy
- Follow same comprehensive research process as NEWS_RESEARCH_SPEC.md

**Outcome:**
- Update issue with research findings
- Add labels for mapped abuses

#### 4. Editorial Review of Issue (Second Gate)
**Can we confidently record this?**

**Decision points:**
- Sources meet floor (primary OR 2x investigative)?
- Event clearly describes a taxonomy abuse?
- Actors correctly identified?
- Jurisdiction and location accurate?

**Approval criteria:**
- Passes sourcing floor
- Clearly describes a relevant abuse
- Research is complete and well-documented

**Rejection criteria:**
- Sources insufficient
- Abuse mapping is unclear or inappropriate
- Insufficient detail to create entry

**Actions:**
- Approve: Move to entry recording (step 5)
- Reject: Close issue with explanation

#### 5. Entry Recording & PR Creation
- **Actor:** Automated entry recording system
- **Trigger:** Issue approved for recording
- **Process:** Same as monitoring intake (step 3)
- **Output:** Entry file + PR

#### 6. Editorial Review of PR (Final Gate)
- **Same as monitoring intake (step 4)**

---

## Editorial Standards (All Channels)

### Headline Standards
- **Factual, not interpretive.** State what happened, not why it matters.
  - ✓ "Senator blocks subpoena compliance"
  - ✗ "Senator abuses power"
- **Neutral point of view.** Avoid loaded language.
  - ✓ "Campaign official sentenced for undisclosed lobbying"
  - ✗ "Corrupt official finally faces justice"
- **Clear and specific.** What happened, not vague implications.
  - ✓ "Texas District Court strikes down voter ID requirement"
  - ✗ "Voting rules questioned"

### Summary Standards
- **2-3 sentences.** Who, what, when, where, why (if relevant).
- **Cite specifics.** Actor names, roles, agencies, dates.
- **Neutral, factual tone.** No commentary or judgment.
- **Accurate to sources.** Never extend beyond what sources say.

### Abuse Mapping Standards
- **Verify abuse definition.** Does the event match the abuse definition in `/taxonomy/abuses.yaml`?
- **One primary abuse.** Which abuse is the core of this event?
- **Secondary abuses OK.** But use sparingly (1-3 abuses per entry typical).
- **Avoid over-mapping.** Not every abuse is relevant just because the actor is powerful.
  - ✓ "Election official intimidated" maps to `election-worker-intimidation`
  - ✗ Map the same event to `excessive-force-by-law-enforcement` unless police violence occurred

### Location Field Standards

**Requirements by jurisdiction:**
- **Federal:** Location optional (can be "N/A" or "Nationwide")
- **State:** State abbreviation required (e.g., "Colorado", "CO")
- **Local:** City/County and state required (e.g., "Denver, Colorado" or "Douglas County, Colorado")
- **International:** Country required
- **Private actor:** Location required if abuse is geographically bounded; optional if policy is nationwide

**Format:**
- City, State or State alone (not "State, City")
- Full state name or two-letter abbreviation (either is acceptable)
- County format: "County Name, State" (e.g., "Maricopa County, Arizona")

---

## Location Field Handling (All Channels)

**This field is required and must be propagated through all workflows.**

1. **Sourcing:** Monitoring and tips must gather location during research phase
2. **Entry recording:** Validation checks location for jurisdiction requirements
3. **Entry file:** Location field in YAML frontmatter
4. **Archive pages:** Location is searchable and filterable (future enhancement)

---

## Anti-Threshold-Creep Guidelines

**Question for editors: "Is this a documented event that matches a defined abuse?"**

- If YES to both: Record it. Don't ask "Is this significant enough?" or "Is this part of a pattern?"
- If MAYBE: Consult the taxonomy definition for that abuse and the broken-windows principle.
- If NO to either: Don't record it.

**Examples of what to INCLUDE despite being small:**
- Single instance of voter suppression (one polling place, one election)
- Single instance of press retaliation (one journalist detained, one letter from administration)
- Single instance of election worker intimidation (one official receives threats)
- Nepotism in one hire (even if others have merits)

**Examples of what to EXCLUDE:**
- Political disagreement without institutional abuse
- Public figures criticizing each other (not retaliation unless using state power)
- General complaints without specific events
- Unverified allegations without sourcing floor

---

## Approval Checklist (Use for All PR Reviews)

**Entry PR Review Checklist:**

- [ ] Headline is factual and neutral
- [ ] Summary is 2-3 sentences and accurate
- [ ] Event date is correct (YYYY-MM-DD or appropriate approximate format)
- [ ] Jurisdiction is correctly identified (federal/state/local/international/private)
- [ ] Location meets jurisdiction requirements (state for state/local, city/county/state for local, etc.)
- [ ] All actors are correctly named and roles/titles are accurate
- [ ] Abuses are correctly mapped to taxonomy (