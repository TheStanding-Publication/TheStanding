---
name: episode-discovery
description: Scan The Standing's registered entries for episodes — groups of entries that are facets of one compound real-world happening — and return a recommendation list. Use on demand when an editor wants to find episodes hiding in the archive or check whether recent entries should be grouped or linked to an existing episode.
disable-model-invocation: true
---

# Episode Discovery

Find the episodes hiding in the archive: groups of already-recorded
entries that are facets of one compound real-world happening, plus
recently-arrived entries that should be linked to an existing episode.

## Run it

Fetch and execute the canonical workflow spec:

https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/EPISODE_DISCOVERY_SPEC.md

The spec is the source of truth — follow its Steps 1-5 exactly; do not
work from memory or a remembered older version. Start with the Step 1
read-only sync of `main` before scanning.

## Input

Optional scope, provided by the operator with this invocation — a date
window or a subset (e.g. "over the last 60 days", or entries tagged a
given abuse). Default scope is the entire archive.

## Output

A ranked recommendation list, returned to the operator: new-episode
candidates (with proposed slug, title, dates, draft overview, and member
entries) and links of entries to existing episodes — each with a plain-
language rationale. See the spec's "Output format" section.

This skill is read-only and on-demand only. It never writes an episode
file, never edits an entry, and makes no commits — its only git
interaction is the Step 1 sync. Acting on the recommendations (creating
the episode file and adding `episodes:` links) is a separate editorial
step, by design, so discovery never becomes a side effect of another
process.
