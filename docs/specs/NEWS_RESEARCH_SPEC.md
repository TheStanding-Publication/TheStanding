# The Standing: News Research

## Purpose
Automatically monitor major news outlets for events matching The Standing's taxonomy of ideals and abuses, create GitHub issues with comprehensive event information, and avoid duplicates. Runs four times daily on a schedule.

## Key Principle: Agent-Based Evaluation
**This system uses Claude agent analysis instead of pattern matching.** Each story is evaluated for relevance by understanding context and nuance, not just matching keywords.

## How This Skill Is Used

**This document is the operational source of truth.** It is fetched and executed directly by four scheduled tasks (`standing-monitor-morning`, `standing-monitor-midday`, `standing-monitor-afternoon`, `standing-monitor-evening`). Each scheduled task is a thin wrapper that passes scan-specific parameters and otherwise defers entirely to the workflow defined here.

Changes to this file propagate to all four scheduled scans on their next run. **Do not duplicate this workflow into the scheduled-task prompts** — that creates drift and historically has.

## Modes and Inputs

This skill supports two modes, distinguished by the `mode` input. The workflow steps are largely shared; the differences are isolated to source acquisition (Step 2), refusal handling (Step 3), and duplicate handling (Step 5).

### Scheduled-scan mode (default)

Invoked by the four cron tasks (morning/midday/afternoon/evening). Scans the curated source list looking for new events.

- `mode` — `scheduled-scan` (default if unspecified)
- `time_window` — how far back from now to scan (e.g. "last 24 hours", "last 5 hours")
- `scan_label` — which scheduled scan this is (morning / midday / afternoon / evening)

### URL-to-issue mode

Invoked on-demand by an operator (editor) providing a single URL. The agent uses that URL as the starting point and conducts a full event-research run from there.

- `mode` — `url-to-issue`
- `source_url` — a single URL (news article, court filing, agency press release, social-media post, primary document — anything on the open web). Editors do preliminary vetting before submitting; the agent still applies all editorial standards downstream.
- `scan_label` — `url-to-issue` (or operator-supplied identifier for the report)

**Inclusion judgment for this mode is delegated to [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md).** The `url-to-issue` skill runs archive-fit in URL mode before this spec executes; a story only reaches the URL-to-issue research mechanics below when archive-fit's verdict is `archive-fit`. The mode-specific in-scope check (Step 3) and duplicate handling (Step 5) that previously lived here have been removed accordingly — archive-fit owns those.

## Workflow

### Step 1: Load the current taxonomy

The Standing's taxonomy is versioned in the public repo. Fetch the current versions at the start of every run — do **not** work from memory or a hardcoded subset:

- **Sources to scan:** https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/sources.yaml — curated outlets across five categories (`national_news`, `government_sources`, `watchdog_sources`, `press_freedom_sources`, `specialized_sources`). Scan the **full** list, not just the well-known national outlets. Watchdog and specialized sources (Brennan Center, Democracy Docket, ProPublica, ACLU, SCOTUSblog, Documented NY, etc.) often break democracy stories before the wire services do — their inclusion in the list is deliberate.
- **Abuses to evaluate against:** https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/abuses.yaml — every abuse slug currently in the taxonomy, each with a `title` and `description`. Use this list when classifying stories. The full taxonomy is broader than any short summary; do not work from memory.

### Step 2: Acquire source material

**Scheduled-scan mode:** Use the curated sources you just loaded. Fetch RSS feeds where `sources.yaml` provides them; web-scrape otherwise. Focus on the `time_window` provided by the scheduled task, scoped to US governance, democracy, voting, elections, law enforcement, press freedom, separation of powers, civil rights, due process, public service, and institutional accountability.

**URL-to-issue mode:**

1. Fetch the `source_url`. Read the article (or document) content. Send a browser-style User-Agent header — many publisher WAFs return 403 to default HTTP clients.
2. **If the fetch tooling refuses the domain outright** — it reports the URL blocked or blocklisted, which is a tooling-level restriction distinct from the publisher's own paywall or a WAF 403 — do not try to work around it (no alternate fetchers, caches, archives, or mirrors; the restriction exists for legal reasons). The URL itself may be perfectly valid; the agent simply cannot read it through its tools. **Reject the URL:** tell the operator the domain cannot be fetched, name it, and ask them to supply an alternative URL covering the same event — a different outlet, a primary document, or an official statement. Stop and wait for that alternative; do not proceed on the blocked URL and do not reconstruct the story from search snippets alone.
3. If the URL instead doesn't resolve, or returns a substantive paywall/login wall that prevents reading the underlying content, retry once. If still inaccessible, report the failure to the operator and stop — do not create an issue with an unverifiable primary source.
4. **Search for supporting coverage.** The provided URL is the *starting point*, not the final source list. Find additional primary and investigative sources covering the same event — prefer sources from `taxonomy/sources.yaml`, but search beyond it as well. The goal is the same kind of comprehensive intake a scheduled scan produces: multiple sources, primary and investigative, with the original URL among them.
   - **For older events:** plain searches rank recency and bury the original reporting under newer follow-ups. Use site and date-range filters — e.g. `site:npr.org` scoped to a date window around the event. DuckDuckGo's HTML interface (`html.duckduckgo.com/html/`) handles these filters reliably in headless contexts where Google may block automated requests. Iterate one `site:` per outlet rather than one broad query, and verify each result's actual publish date in the fetched page.
   - **Stop once the story is sufficiently vetted.** The operator has already vetted the submitted URL, so the bar here is corroboration, not exhaustiveness. Once the event, its date, the actors, and the central claims are confirmed by enough independent reporting to stand on their own — in practice the submitted URL plus one or two corroborating sources — stop searching. Further fetches past that point add cost without changing the issue. Comprehensive intake means complete, not maximal.
5. **Verify the original URL's claims** against your supporting coverage. If sources contradict the original URL's central claims, surface that to the operator and stop — the URL may be inaccurate or non-canonical.

### Step 3: Evaluate each story semantically

For each story you found in Step 2, ask:

- Is this describing an anti-democratic action or abuse of power?
- Which abuse slugs from the loaded `abuses.yaml` does it map to? (1-5 slugs; only emit slugs that exist in the current taxonomy.)
- Is the source credible?
- What's your confidence level?

Use semantic understanding, not pattern matching. You understand that "weakening Voting Rights Act enforcement" maps to `voter-suppression` (or one of the more specific election slugs) without needing keyword overlap.

**URL-to-issue mode — in-scope check:** archive-fit has already
rendered the inclusion verdict before this spec runs. Stories reach this
step only when archive-fit returned `archive-fit`. No additional
in-scope refusal logic lives here. See
[`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) for the mission test, ideal
match, abuse match, and refusal semantics.

### Step 4: For relevant stories, conduct comprehensive research

**One issue per distinct event.** If the research surfaces more than one
distinct event — for example, a single article that reports two separate
voter-intimidation incidents on different days, or a URL that bundles a
firing and a separate retaliatory action — treat each event as its own
research target and gather the full Step 4 field set per event. The
archive tracks events, not topics or coverage clusters. This mirrors the
event-level deduplication rule in
[`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) Step 5: two incidents that
differ in date, location, actors, or specific act are two events, even
when reported in the same source.

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

Before creating an issue, search the repo `TheStanding-Publication/TheStanding` for **open AND closed** issues whose title or body references the same event, date, and actors.

**Scheduled-scan mode:** If a duplicate exists, skip silently — the event is already in the archive's intake queue. If unclear whether it's a duplicate, note in research and proceed with caution.

**URL-to-issue mode:** duplicate handling has moved to
[`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) (Step 5, event-level
duplicate check). Stories reaching this step have already been judged
against the existing archive — if archive-fit's verdict was
`archive-fit-merge` rather than `archive-fit`, the operator was told to
merge into the existing entry and never invoked `url-to-issue`. The
agent in this mode therefore proceeds without an additional duplicate
search; the recording flow is mechanical.

### Step 6: Create the GitHub issue

**One issue per distinct event** (restating the Step 4 rule at the
creation boundary because it is easy to lose at this step). If
Step 4 produced research records for multiple distinct events, emit one
issue per event using the template below — do **not** bundle them into
a single "[Monitoring]" issue, even if they share a source URL, a
storyline, or an actor. Each issue stands alone, carries its own event
date, actors, mapped abuses, and evidence, and flows through
`ISSUE_TO_ENTRY_SPEC` independently. Cross-link related issues in the
**Analysis** section if the connection matters editorially.

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

**Apply the status tag:**
- `ready-for-entry` (always) — the pipeline-status tag that marks a fully-researched monitoring issue as ready for the entry-recording step (`ISSUE_TO_ENTRY_SPEC`); it is the single tag that step filters on.

Do **not** apply abuse slugs as labels. The mapped abuses already live in the "Mapped abuses" section of the issue body — the canonical place the entry-recording step reads them — and labelling them as well causes unbounded label sprawl and goes stale when slugs are corrected downstream.

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
8. **One issue per distinct event** — if research surfaces multiple distinct events (different date, location, actors, or specific act), each becomes its own issue. Never bundle multiple events into a single issue, even when they share a source URL or storyline.

## Validation Responsibility

Final validity of an issue is the **downstream** ISSUE_TO_ENTRY_SPEC's responsibility, not this one. That skill re-reads source content at process time, corrects taxonomy mismatches using current `taxonomy/abuses.yaml`, normalizes fields, and discards issues it judges unsalvageable.

What that means for this skill:

- **Do** be reasonably thorough on first emission — comprehensive research, valid slugs, primary sources verified loadable.
- **Don't** treat issue creation as the final word. Articles get retracted; the taxonomy evolves; headlines change between emission and recording. Some friction at the downstream step is expected and healthy.
- **Don't** invent abuse slugs to fit a story. If nothing in the taxonomy maps cleanly, that's a signal the taxonomy may need a new abuse — flag in **Analysis** rather than papering over with a wrong slug.

## Scheduled Tasks (Thin Wrappers)

This skill is invoked by four daily scheduled tasks:

- `standing-monitor-morning` (5am) — deep-scan safety net (24-hour window); scheduled early so the heaviest scan completes well before peak working hours (9am-12pm local)
- `standing-monitor-midday` (1pm) — delta scan (8-hour window, covering 5am-1pm); 1pm avoids peak working hours
- `standing-monitor-afternoon` (4pm) — delta scan (5-hour window)
- `standing-monitor-evening` (8pm) — delta scan (5-hour window)

Scheduled-job quiet windows (local time): no monitor scan runs between 9am and 12:59pm; the separate `standing-entry-recorder` task is quiet over a wider window, 6am-12:59pm. Both resume at 1pm.

Each scheduled task is a thin wrapper of the form:

```
You are The Standing's automated news monitoring system.

Fetch and execute the workflow defined in:
https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/NEWS_RESEARCH_SPEC.md

This is the canonical operational spec. Follow it exactly.

Scan parameters for this run:
- time_window: [varies per task]
- scan_label: [morning / midday / afternoon / evening]
```

The scheduled task prompt should be no more than ~15 lines. If a behavior change needs to land in th