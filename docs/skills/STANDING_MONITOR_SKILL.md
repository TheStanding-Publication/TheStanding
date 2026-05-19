# The Standing: News Monitoring Skill

## Purpose
Automatically monitor major news outlets for events matching The Standing's taxonomy using Claude agent evaluation, create GitHub issues with comprehensive event information, and avoid duplicates.

## Key Principle: Agent-Based Evaluation
**This system uses Claude agent analysis instead of pattern matching.** Each story is evaluated for relevance by understanding context and nuance, not just matching keywords.

## Ideals & Abuses Reference
Available via taxonomy: 12 ideals with 77 specific abuses. The agent evaluates stories semantically against these ideals.

## Sources Reference
The curated list of monitoring sources is defined in `taxonomy/sources.yaml`. This includes national news outlets, government sources, civil rights watchdogs, and press freedom organizations. Each source includes RSS feed URLs where available.

## Workflow

### 1. Search for Relevant News
- Monitor from the curated sources list in `taxonomy/sources.yaml`
- Sources include national news outlets, government documents, civil rights organizations, and specialized investigative publications
- Use broad news searches across all topics related to US governance and democracy
- Focus on recent news (last 24 hours for daily scans)
- Fetch via RSS feeds where available, or web scraping for sources without feeds

### 2. Evaluate Relevance (Claude Agent)
**For each story, Claude evaluates:**
- Does this describe an anti-democratic action or abuse?
- Which ideals/abuses from The Standing's taxonomy does this relate to?
- Is this a credible source?

**Claude determines:** Relevant or not relevant, and if relevant, which abuses apply.

Key advantage: Claude understands that "Voting Rights Act enforcement weakened" = voter-suppression without needing exact keyword match.

### 3. Comprehensive Event Research (Claude Agent)
**If relevant, Claude gathers ALL of the following before creating an issue:**

- **Event description**: What happened? Concise 2-3 sentence summary
- **Event date**: When did this occur? (YYYY-MM-DD if known, or approximate)
- **Jurisdiction**: Federal / State / Local / International / Private actor (using the decision rules)
- **Location**: City, county, state (where applicable). Required for local/state events, optional for federal
- **Actors**: Named officials, agencies, candidates, organizations with roles/titles
- **Primary evidence**: Links to news article, official statement, court filing, video
- **Secondary sources**: Additional reporting or official documentation
- **Mapped abuses**: 1-3 abuse slugs that MUST exist in `taxonomy/abuses.yaml` *at the time the issue is created*. Read the taxonomy file before emitting an issue and verify each proposed slug is in the file. If unsure which slug fits, pick the closest valid slug and explain the uncertainty in the **Analysis** section — never invent a slug. (Invented slugs are the single most common cause of downstream entry failures.)
- **Context**: Any background needed to understand significance

**Claude conducts thorough research upfront:**
- Search for original reporting (not just one outlet's coverage)
- Identify official statements from involved parties
- Note related court filings or public records
- Check for follow-up reporting or additional context

This prevents wasting editorial time re-investigating if the issue is accepted.

### 4. Check for Duplicates
**Before creating an issue:**
1. Search open AND closed issues in the repo for related keywords
2. Check issue titles and bodies for similar events
3. If a duplicate exists (same event, same date, same actors), don't create a new issue
4. If unclear if it's a duplicate, note in research but proceed with caution

### 5. Create GitHub Issue
Create an issue with:

```
Title: [Brief headline or event description]

Body:
## Automated News Monitoring

**Source:** [Primary news outlet]
**Scan date:** [When the monitoring scan ran]
**Event date:** [When the event occurred]

### What happened
[2-3 sentence description of the event]

### Jurisdiction
[Federal / State / Local / International / Private actor]

### Location
[City, County, State — e.g., "Douglas County, Colorado" or "Federal (nationwide)" or "N/A"]

### Actors involved
- [Name] ([Title/Role])
- [Organization/Agency]
- [Other relevant actors]

### Mapped abuses
- [abuse-slug-1] (Abuse Title)
- [abuse-slug-2] (Abuse Title)

### Evidence
**Primary:**
- [Source title](URL)

**Secondary:**
- [Additional reporting](URL)
- [Official statement](URL)

### Analysis
[Any relevant context about why this maps to these abuses, significance, related events]

---
*Created by The Standing's automated news monitoring system.*
```

**Labels:**
- `monitoring-intake` (always)
- `needs-research` (always)
- [abuse-slug] for primary mapped abuse (e.g., `voter-suppression`)

### 6. Report Results
For each scan, report:
- How many stories were evaluated
- How many were marked as relevant
- How many duplicates were found and skipped
- How many new issues were created
- Any stories that were borderline/uncertain

## Key Principles

1. **Single point of truth**: All monitoring scans use this skill
2. **Upfront research**: Complete research before issue creation, not after
3. **Comprehensive data**: Gather everything needed to record the event if accepted
4. **Duplicate avoidance**: Check open and closed issues before creating
5. **Taxonomy-driven**: Search and categorize strictly against The Standing's ideals/abuses; abuse slugs MUST exist in `taxonomy/abuses.yaml` at emission time
6. **Evidence-based**: Primary sources only; citizen documentation acceptable if verifiable

## Validation Responsibility

Final validity of an issue is the **downstream** ISSUE_TO_ENTRY_SKILL's responsibility, not this one. That skill re-reads source content at process time, corrects taxonomy mismatches using current `taxonomy/abuses.yaml`, normalizes fields, and discards issues it judges unsalvageable.

What that means for this skill:

- **Do** be reasonably thorough on first emission — comprehensive research, valid slugs, primary sources verified loadable.
- **Don't** treat issue creation as the final word. Articles get retracted; the taxonomy evolves; headlines change between emission and recording. Some friction at the downstream step is expected and healthy.
- **Don't** invent abuse slugs to fit a story. If nothing in the taxonomy maps cleanly, that's a signal the taxonomy may need a new abuse — flag in **Analysis** rather than papering over with a wrong slug.

## Scheduled Tasks
This skill is referenced by 4 daily scheduled tasks:
- `standing-monitor-morning` (8am)
- `standing-monitor-midday` (12pm)
- `standing-monitor-afternoon` (4pm)
- `standing-monitor-evening` (8pm)
