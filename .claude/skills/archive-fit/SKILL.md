---
name: archive-fit
description: Render a verdict on whether a candidate story belongs in The Standing's archive. Takes either an open GitHub issue number or a URL and evaluates against the project mission, the taxonomy of ideals and abuses, and existing entries. Use when an editor asks "does this belong in the archive", wants an inclusion verdict on a tip or monitoring issue, supplies a URL and wants to know if it's in scope, or mentions archive fit, taxonomy gap, archive duplicate, or merging entries. Always invoke when the user asks to judge or evaluate a story for archive inclusion.
disable-model-invocation: true
---

# Archive Fit

Render an inclusion verdict on one candidate story for The Standing.

## Run it

Fetch and execute the canonical workflow spec:

https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/ARCHIVE_FIT_SPEC.md

The spec is the source of truth — follow its steps exactly; do not work
from memory or a remembered older version.

## Input

One of:

- A GitHub issue number in `TheStanding-Publication/TheStanding`
  (issue mode — produces label + comment on the issue), or
- A URL to a news article, court filing, agency release, or primary
  document (URL mode — produces a chat verdict only).

The operator provides exactly one of these with the invocation. If both
are provided, use the issue number and treat the URL as a supplementary
source for the evaluation.

## Output

One of four verdicts:

- **`archive-fit`** — passes mission, has a clean ideal + abuse match,
  no same-event duplicate. In issue mode: label applied, verdict
  comment posted. In URL mode: operator should run `url-to-issue` next.
- **`archive-fit-merge`** — same-event entry already exists in the
  archive. Verdict comment names the existing entry path and recommends
  merging sources rather than filing as new.
- **`not-fit`** — fails the mission test (out of scope, not
  actually-happening, or allegation-without-action). Verdict comment
  explains which threshold failed.
- **`blocked-on-taxonomy`** — passes mission and ideal match, but no
  existing abuse fits cleanly. The skill opens a PR against
  `taxonomy/abuses.yaml` proposing the new abuse and links it in the
  verdict comment. The source issue is held until the PR resolves.

In issue mode, only one verdict label is on the issue at a time. Any
prior verdict label from an earlier run is cleared before the new one
is applied.

## What this skill does NOT do

- It does not promote a tip to `ready-for-entry` (that is
  `tip-to-issue` after a clean `archive-fit` verdict).
- It does not create a monitoring issue from a URL (that is
  `url-to-issue` after a clean `archive-fit` verdict in URL mode).
- It does not record entries (that is `issue-to-entry`).
- It does not close issues. A `not-fit` verdict is editorial; closure
  is an operator action.

See the spec for the full output contract, the comment template, and the
taxonomy-PR procedure.

This skill has side effects in issue mode (it labels and comments on a
GitHub issue, and may open a taxonomy PR), so it is user-invoked only —
it does not auto-trigger.
