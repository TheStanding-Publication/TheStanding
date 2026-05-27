---
name: url-to-issue
description: Turn a single news URL (or court filing, agency release, or other primary-source URL) into a Standing monitoring issue. Use when an editor wants to manually submit a source for the archive instead of waiting for a scheduled monitoring scan.
disable-model-invocation: true
---

# URL to Issue

Convert one operator-supplied URL into a `[Monitoring]` GitHub issue for
The Standing — gated by archive-fit, then recorded mechanically.

## Run it

This skill is now two-phase. **Phase 1 is the inclusion judgment**;
phase 2 is the mechanical recording. Do them in order.

### Phase 1 — archive-fit

Fetch and execute the inclusion-judgment spec, in URL mode, against the
operator's URL:

https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/ARCHIVE_FIT_SPEC.md

The verdict determines what happens next:

- **`archive-fit`** — proceed to Phase 2.
- **`archive-fit-merge`** — stop. Report the existing entry path to the
  operator and recommend merging sources rather than creating a new
  issue. Do not create an issue.
- **`not-fit`** — stop. Report the verdict reasoning to the operator
  (mission failure, out of scope, etc.). Do not create an issue.
- **`blocked-on-taxonomy`** — stop. Report the verdict and the taxonomy
  PR archive-fit opened. Do not create an issue; the URL becomes
  recordable once the taxonomy PR merges.

In URL mode archive-fit emits a chat verdict only — no GitHub mutations.
Phase 2 is what creates the issue.

### Phase 2 — recording (only on `archive-fit`)

Fetch and execute the canonical recording workflow:

https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/NEWS_RESEARCH_SPEC.md

Run it in **URL-to-issue mode**. The spec's mode-specific in-scope check
(Step 3) and duplicate handling (Step 5) have moved to archive-fit and
are no longer part of this phase — the URL has already cleared them.
Follow the remaining steps exactly to fetch supporting coverage,
research the event, and create the `[Monitoring]` issue tagged
`ready-for-entry`.

## Input

A single URL, provided by the operator with this invocation. Anything on
the open web: news article, court filing, agency press release, primary
document.

## Output

- **Archive-fit verdict** (always emitted to chat with reasoning), and
- **A `[Monitoring]` issue** in `TheStanding-Publication/TheStanding`
  tagged `ready-for-entry` — only when the verdict was `archive-fit`.

For the other three verdicts the skill stops at Phase 1 and reports to
the operator; no issue is created.

This skill has side effects in Phase 2 (it creates a GitHub issue) so
it is user-invoked only — it does not auto-trigger.
