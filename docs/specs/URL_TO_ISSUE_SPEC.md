# The Standing: URL-to-Issue Intake

**This is a pointer document — it has no workflow of its own.**

Turning an operator-submitted URL into a monitoring issue is handled by
**URL-to-issue mode** of the news monitoring spec. The full workflow lives
in one place:

→ **[`NEWS_RESEARCH_SPEC.md`](./NEWS_RESEARCH_SPEC.md)** — see the
**"Modes and Inputs"** section and the **"URL-to-issue mode"** entries
within Steps 2, 3, and 5.

The invocable skill for this workflow is **`url-to-issue`** (in
`.claude/skills/`), a thin wrapper that fetches and executes the spec
above.

## Fit judgment delegated to ARCHIVE_FIT_SPEC

As of the introduction of [`ARCHIVE_FIT_SPEC.md`](./ARCHIVE_FIT_SPEC.md),
the inclusion judgment (mission test, ideal/abuse mapping, archive
duplicate check, taxonomy-gap handling) is owned by that spec. The
`url-to-issue` skill runs archive-fit in URL mode first and only creates
a monitoring issue when the verdict is `archive-fit`. The recording
mechanics — issue body template, labels, the entry-recording handoff —
remain governed by `NEWS_RESEARCH_SPEC`.

## Why this isn't its own workflow spec

URL-to-issue intake shares ~90% of its workflow with the scheduled news
scan — taxonomy loading, comprehensive research, duplicate checking,
issue creation, labels, and the issue template are all identical. Only
three steps differ by mode:

- **Step 2** — fetch the operator's URL and search for supporting
  coverage, instead of scanning the curated source list.
- **Step 3** — formerly an explicit in-scope check; the inclusion
  judgment now lives in [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) and
  runs *before* this spec executes (only `archive-fit` URLs reach the
  research mechanics).
- **Step 5** — formerly an operator-surfaced duplicate handler; the
  event-level duplicate check now lives in archive-fit Step 5. Stories
  reaching this step have already cleared that check.

Keeping both modes in a single spec avoids drift — there is one
canonical workflow, and a change to it propagates to both the
scheduled scans and URL-to-issue intake at once.

## Quick reference

- **Invocation:** the `url-to-issue` skill (slash command), or ask an
  operator agent to run URL-to-issue mode.
- **Input:** a single URL — news article, court filing, agency press
  release, primary document, anything on the open web.
- **Output:** a `[Monitoring]` GitHub issue in
  `TheStanding-Publication/TheStanding`, labelled `monitoring-intake`,
  `needs-research`, and the mapped abuse slug(s) — identical in form to
  a scheduled-scan issue. It then flows through `ISSUE_TO_ENTRY_SPEC`
  like any other monitoring issue. **If research surfaces more than one
  distinct event from the submitted URL, the output is one issue per
  event** — see `NEWS_RESEARCH_SPEC` Step 6.
- **Refusal:** if the URL is out of scope, the agent explains why and
  creates no issue. Override by re-submitting with an explicit
  "file anyway" instruction.

## One URL can produce multiple issues

A single submitted URL is not necessarily a single archive event. An
investigative piece may bundle two voter-intimidation incidents; an
agency press release may announce both a firing and a separate
retaliatory action; a court order may rule on two distinct claims.
When research at Step 4 of `NEWS_RESEARCH_SPEC` surfaces more than one
distinct event (different date, location, actors, or specific act), the
skill emits one `[Monitoring]` issue per event, not one issue bundling
them. Archive-fit must have already rendered an `archive-fit` verdict
per event before issue creation; if the operator only ran archive-fit
on the URL as a whole, re-run it per event before filing.
