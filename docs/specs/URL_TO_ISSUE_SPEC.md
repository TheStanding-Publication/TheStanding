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