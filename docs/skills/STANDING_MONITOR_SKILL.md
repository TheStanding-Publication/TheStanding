# The Standing: News Monitoring Skill

## Purpose
Automatically monitor major news outlets for events matching The Standing's taxonomy of ideals and abuses, create GitHub issues with comprehensive event information, and avoid duplicates. Runs four times daily on a schedule.

## Key Principle: Agent-Based Evaluation
**This system uses Claude agent analysis instead of pattern matching.** Each story is evaluated for relevance by understanding context and nuance, not just matching keywords.

## How This Skill Is Used

**This document is the operational source of truth.** It is fetched and executed directly by four scheduled tasks (`standing-monitor-morning`, `standing-monitor-midday`, `standing-monitor-afternoon`, `standing-monitor-evening`). Each scheduled task is a thin wrapper that passes scan-specific parameters and otherwise defers entirely to the workflow defined here.

Changes to this file propagate to all four scheduled scans on their next run. **Do not duplicate this workflow into the scheduled-task prompts** — that creates drift and historically has.

## Inputs Provided by the Scheduled Task

- `time_window` — how far back from now to scan (e.g. "last 24 hours", "last 6 hours"). The scheduled task chooses this.
- `scan_label` — which scheduled scan this is (morning / midday / afternoon / evening). For the run report.

## Workflow

### Step 1: Load the current taxonomy

The Standing's taxonomy is versioned in the public repo. Fetch the current versions at the start of every run — do **not** work from memory or a hardcoded subset:

- **Sources to scan:** https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/sources.yaml — curated outlets across five categories (`national_news`, `government_sources`, `watchdog_sources`, `press_freedom_sources`, `specialized_sources`). Scan the **full** list, not just the well-known national outlets. Watchdog and specialized sources (Brennan Center, Democracy Docket, ProPublica, ACLU, SCOTUSblog, Documented NY, etc.) often break democracy stories before the wire services do — their inclusion in the list is deliberate.
- **Abuses to evaluate against:** https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/abuses.yaml — every abuse slug currently in the taxonomy, each with a `title` and `description`. Use this list when classifying stories. The full taxonomy is broader than any short summary; do not work from memory.

### Step 2: Search recent news

Use the curated sources you just loaded. Fetch RSS feeds where `sources.yaml` provides them; web-scrape otherwise. Focus on the `time_window` provided by the scheduled task, scoped to US governance, democracy, voting, elections, law enforcement, press freedom, separation of powers, civil rights, due process, public service, and institutional accountability.

### Step 3: Evaluate each story semantically

For each story you find, ask:

- Is this describing an anti-democratic action or abuse of power?
- Which abuse slugs from the loaded `abuses.yaml` does it map to? (1-5 slugs; only emit slugs that exist in the current taxonomy.)
- Is the source credible?
- What's your confidence level?

Use semantic understanding, not pattern matching. You understand that "weakening Voting Rights Act enforcement" maps to `voter-suppression` (or one of the more specific election slugs) without needing keyword overlap.

### Step 4: For relevant stories, conduct comprehensive research

Before creating an issue, gather all of:

- **Event description** — 2-3 sentences.
- **Event date** — `YYYY-MM-DD` if known, or the most defensible approximation.
- **Jurisdiction** — `federal` / `state` / `local` / `international` / `private-actor`.
- **Location** — city, county, state where applicable.
- **Actors** — named officials, agencies, candidates, organizations with roles/titles, **filtered to those who took the action**. Contextual parties (a court whose prior ruling enabled the action; an opposition party that protested it; the targets of the action) are not actors of the abuse — describe them in the body if relevant, but do not list them as actors.
- **Primary evidence** — links to news articles, official statements, court filings, video. Verify each loads.
- **Secondary sources** — additional reporting or official documentation.
- **Mapped abuses** — 1-5 abuse slugs that MUST exist in the `abuses.yaml` you loaded in Step 1. **Never invent a slug.** If no slug fits cleanly, pick the closest valid one and explain the uncertainty in **Analysis** — the downstream skill will correct in flight. Use as many slugs as genuinely apply; don't trim, don't pad. Most events map to 1-3 in practice.
- **Context / Analysis** — significance, related events, downstream effects.

### Step 5: Check for duplicates

Before creating an issue, search the repo `TheStanding-Publication/TheStanding` for **open AND closed** issues whose title or body references the same event, date, and actors. If a duplicate exists, skip. If unclear, note in research and proceed with caution.

### Step 6: Create the GitHub issue

For each new relevant story, create an issue with this template:

```
Title: [Monitoring] [Brief headline]

Body:
## Automated News Monitoring

**Source:** [Primary news outlet]
**Date:** [YYYY-MM-DD scan date]
**Event date:** [YYYY-MM-DD]

### What happened
[2-3 sentences]

### Jurisdiction
[federal / state / local / international / private-actor]

### Location
[City, County, State — or "federal" / "nationwide" / "N/A"]

### Actors involved
- [Name] ([Title/Role])
- [Organization/Agency]

### Mapped abuses
- [abuse-slug-1] (Abuse Title)
- [abuse-slug-2] (Abuse Title)

### Evidence
**Primary:**
- [Source title](URL)

**Secondary:**
- [Additional reporting](URL)

### Analysis
[Context, significance, related events]

---
*Created by The Standing's automated news monitoring system (scan: [scan_label]).*
```

**Apply labels:**
- `monitoring-intake` (always)
- `needs-research` (always)
- Each abuse slug emitted in "Mapped abuses" as a label

### Step 7: Report the run

Return a summary to the conversation:

- Stories evaluated
- Stories marked relevant
- Duplicates skipped
- New issues created (with issue numbers)
- Any borderline / uncertain cases worth surfacing

## Key Principles

1. **Single point of truth** — this file. All four scheduled scans execute the workflow described here.
2. **Upfront research** — complete research before issue creation, not after.
3. **Comprehensive data** — gather everything the downstream entry-recording skill needs.
4. **Duplicate avoidance** — check open and closed issues before creating.
5. **Taxonomy-driven** — abuse slugs MUST exist in the live `abuses.yaml`. Inventing slugs is the single most common cause of downstream entry failures.
6. **Evidence-based** — primary sources only; citizen documentation acceptable if verifiable.
7. **Scan the full source list** — many of The Standing's strongest entries originate in watchdog and specialized outlets that wire services pick up only later, or not at all.

## Validation Responsibility

Final validity of an issue is the **downstream** ISSUE_TO_ENTRY_SKILL's responsibility, not this one. That skill re-reads source content at process time, corrects taxonomy mismatches using current `taxonomy/abuses.yaml`, normalizes fields, and discards issues it judges unsalvageable.

What that means for this skill:

- **Do** be reasonably thorough on first emission — comprehensive research, valid slugs, primary sources verified loadable.
- **Don't** treat issue creation as the final word. Articles get retracted; the taxonomy evolves; headlines change between emission and recording. Some friction at the downstream step is expected and healthy.
- **Don't** invent abuse slugs to fit a story. If nothing in the taxonomy maps cleanly, that's a signal the taxonomy may need a new abuse — flag in **Analysis** rather than papering over with a wrong slug.

## Scheduled Tasks (Thin Wrappers)

This skill is invoked by four daily scheduled tasks:

- `standing-monitor-morning` (8am)
- `standing-monitor-midday` (12pm)
- `standing-monitor-afternoon` (4pm)
- `standing-monitor-evening` (8pm)

Each scheduled task is a thin wrapper of the form:

```
You are The Standing's automated news monitoring system.

Fetch and execute the workflow defined in:
https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/skills/STANDING_MONITOR_SKILL.md

This is the canonical operational spec. Follow it exactly.

Scan parameters for this run:
- time_window: [varies per task]
- scan_label: [morning / midday / afternoon / evening]
```

The scheduled task prompt should be no more than ~15 lines. If a behavior change needs to land in the scheduled scans, change it **here**, not in the scheduled-task prompts.
