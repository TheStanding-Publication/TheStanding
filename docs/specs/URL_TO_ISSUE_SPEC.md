# The Standing: URL-to-Issue Intake

**This is a pointer document — it has no workflow of its own.**

Turning an operator-submitted URL into a monitoring issue is handled by
**URL-to-issue mode** of the news monitoring spec. The full workflow lives
in one place:

→ **[`STANDING_MONITOR_SPEC.md`](./STANDING_MONITOR_SPEC.md)** — see the
**"Modes and Inputs"** section and the **"URL-to-issue mode"** entries
within Steps 2, 3, and 5.

The invocable skill for this workflow is **`url-to-issue`** (in
`.claude/skills/`), a thin wrapper that fetches and executes the spec
above.

## Why this isn't its own workflow spec

URL-to-issue intake shares ~90% of its workflow with the scheduled news
scan — taxonomy loading, comprehensive research, duplicate checking,
issue creation, labels, and the issue template are all identical. Only
three steps differ by mode:

- **Step 2** — fetch the operator's URL and search for supporting
  coverage, instead of scanning the curated source list.
- **Step 3** — an explicit in-scope check that refuses with reasoning
  when the URL doesn't describe an abuse of power within scope.
- **Step 5** — duplicate handling surfaces the match to the operator
  rather than skipping silently.

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
  like any other monitoring issue.
- **Refusal:** if the URL is out of scope, the agent explains why and
  creates no issue. Override by re-submitting with an explicit
  "file anyway" instruction.
