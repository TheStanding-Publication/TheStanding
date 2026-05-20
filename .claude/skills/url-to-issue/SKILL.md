---
name: url-to-issue
description: Turn a single news URL (or court filing, agency release, or other primary-source URL) into a Standing monitoring issue. Use when an editor wants to manually submit a source for the archive instead of waiting for a scheduled monitoring scan.
disable-model-invocation: true
---

# URL to Issue

Convert one operator-supplied URL into a `[Monitoring]` GitHub issue for
The Standing.

## Run it

Fetch and execute the canonical workflow spec:

https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/NEWS_RESEARCH_SPEC.md

Run it in **URL-to-issue mode** (see the spec's "Modes and Inputs"
section, and the URL-to-issue-mode behavior within Steps 2, 3, and 5).
The spec is the source of truth — follow its steps exactly; do not work
from memory or a remembered older version.

## Input

A single URL, provided by the operator with this invocation. Anything on
the open web: news article, court filing, agency press release, primary
document.

## Output

A `[Monitoring]` issue in `TheStanding-Publication/TheStanding`, tagged
`ready-for-entry` — or a reasoned refusal if the URL is out of scope, or
a surfaced duplicate for the operator to decide on. See the spec for the
exact behavior.

This skill has side effects (it creates a GitHub issue), so it is
user-invoked only — it does not auto-trigger.
