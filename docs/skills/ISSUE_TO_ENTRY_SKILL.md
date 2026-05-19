# The Standing: Issue to Entry Skill (Claude Agent)

## Purpose
Claude agent that converts GitHub monitoring-intake issues into fully recorded entry files, feature branches, and pull requests. Runs on schedule or on-demand.

## Invocation

```bash
# Process all eligible issues (default for scheduled runs)
/issue-to-entry --all

# Process specific issue
/issue-to-entry --issue 42

# Limit issues per run (e.g., max 5)
/issue-to-entry --all --limit 5
```

## Implementation Overview

This skill is a Claude agent that orchestrates the full workflow:
1. Fetch monitoring-intake issues from GitHub
2. For each issue: parse, validate, create entry, verify build, add comment
3. Create branch, commit, push to GitHub
4. Create PR with appropriate labels
5. Report summary of what was processed

**Key principle:** Each validation failure adds a comment and skips to the next issue. No stopping on errors.

---

## Detailed Agent Workflow

### Step 1: Fetch Eligible Issues

**What the agent does:**
- Call GitHub API to search for issues
- Query: `is:issue state:open label:monitoring-intake sort:number-asc`
- Skip issues with `url-validation-hold` label if last comment is < 24 hours old
- Build list of issues to process

**GitHub API call:**
```
GET /search/issues?q=repo:TheStanding-Publication/TheStanding+is:issue+state:open+label:monitoring-intake&sort=number&order=asc&per_page=100
```

> **Note:** the `is:issue` qualifier is required. GitHub's search API rejects the query with HTTP 422 (`"Query must include 'is:issue' or 'is:pull-request'"`) if it's omitted.

**Handle:**
- If `--issue N` flag: fetch only issue #N
- If `--all` flag: fetch all eligible (respecting `--limit` if provided)
- Authentication: Use `GITHUB_TOKEN` environment variable

### Step 2: For Each Issue - Parse Issue Body

**Expected format** (from STANDING_MONITOR_SKILL output):
```
## Automated News Monitoring

**Source:** [Primary news outlet]
**Date:** [YYYY-MM-DD]              # scan/report date — also accepted as `**Scan date:**`
**Event date:** [YYYY-MM-DD]

### What happened
[2-3 sentence summary]

### Jurisdiction
[Federal / State / Local / International / Private actor]

### Location
[City, County, State]

### Actors involved
- [Name] ([Title/Role])
- [Organization]

### Mapped abuses
- [abuse-slug-1] (Abuse Title)
- [abuse-slug-2] (Abuse Title)

### Evidence
**Primary:**
- [Source title](URL)

**Secondary:**
- [Additional reporting](URL)
```

**What the agent does:**
- Extract each section from issue body
- Build dictionary: headline, summary, date, jurisdiction, location, actors, abuses, sources
- Actors: parse from "Name (Role)" format, extract both
- Abuses: extract slugs from bulleted list
- Sources: extract URL, publisher, tier (primary/investigative/secondary), title

> **Parser tolerance:** accept both `**Date:**` and `**Scan date:**` for the scan/report-date field. The upstream STANDING_MONITOR_SKILL currently emits `**Date:**`; older fixtures used `**Scan date:**`. Either should work without manual cleanup.

### Step 3: Validate Data

**Check all required fields:**
- `headline` — non-empty, <100 chars
- `summary` — non-empty, 2-3 sentences
- `date` — YYYY-MM-DD format
- `jurisdiction` — one of: federal, state, local, international, private-actor
- `location` — meets jurisdiction requirements (state for state, city/county/state for local, etc.)
- `actors` — at least 1, all non-empty
- `abuses` — at least 1, all must exist in `/taxonomy/abuses.yaml`
- `sources` — at least 1, all have url/publisher/tier

**If validation fails at this stage:**
→ Go to **Step 8: Failure Handling**

### Step 4: URL Validation & Normalization

**For each source URL:**

1. **Make GET request** to verify status
   - **Send a browser-like User-Agent header** (e.g. `Mozilla/5.0 (compatible; TheStandingBot/1.0; +https://thestanding.us)`). Many publisher WAFs return 403/406 to default HTTP-client User-Agents on otherwise-live articles. Without this, healthy news sites get falsely flagged dead.
   - Follow redirects automatically
   - Capture final URL if redirected (301/302)
   - **Accept (live):** 200 OK
   - **Dead** (drop from sources): 404, 410, DNS failure, connection refused, TLS failure, hard timeout
   - **Needs review** (keep the source in the entry; add `url-needs-review` label to the issue): 403, 406, 451, 5xx. These are usually bot-blocking or transient publisher issues, not actually-gone content. Do **not** treat these as dead — dropping live primary sources because of a WAF is a worse failure mode than keeping an occasional zombie URL.
   - Treat anything else not listed above as dead.

2. **Update URL** if redirected (301/302)

3. **Remove dead URLs** from sources list (do not remove "needs review" URLs — keep them and surface for human check)

4. **After cleaning:**
   - Count remaining primary sources
   - Count remaining investigative sources
   
   **If all primary sources are dead:**
   → Add `url-validation-hold` label and comment, skip this issue
   
   **Else if sourcing floor not met** (need 1 primary OR 2 investigative after cleaning):
   → Go to **Step 8: Failure Handling**
   
   **Else:** Continue with remaining sources

### Step 5: Create Entry File

**File location:** `/src/entries/YYYY/MM/DD/[slug].md`

Where slug is: `issue-{number}-{jurisdiction}-{primary-abuse}`

**Slug generation rules:**
- `{number}` = GitHub issue number
- `{jurisdiction}` =
  - `federal` — federal action
  - `<2-letter-state-code>` — state action (e.g. `tn`, `co`, `tx`). **Use the 2-letter postal code, NOT the literal word "state"** — this keeps Tennessee distinguishable from Texas in the slug.
  - `local` — city/county/local action (state code is captured in the `location` field, not the slug)
  - `intl` — international
  - `private` — private actor
- `{primary-abuse}` = first abuse in list (kebab-case)

Examples:
- `issue-42-federal-defying-subpoenas`
- `issue-15-co-excessive-force` (Colorado state action)
- `issue-6-tn-gerrymandering` (Tennessee state action)
- `issue-28-private-press-retaliation`

This rule is load-bearing: it satisfies Key Principle #3 ("deterministic slugs"). Two runs against the same issue must produce the same slug.

**File format:**
```yaml
---
date: YYYY-MM-DD
archived: [TODAY in YYYY-MM-DD]
slug: [generated slug]
status: published

headline: "[From parsed issue]"
summary: >
  [From parsed issue, 2-3 sentences]

abuses:
  - abuse-slug-1
  - abuse-slug-2

episodes: []

actors:
  - "[Actor 1]"
  - "[Actor 2]"

jurisdiction: [federal|state|local|international|private-actor]
location: "[City, State or State or Country]"

sources:
  - url: "[Final URL after redirects]"
    publisher: "[Source name]"
    tier: [primary|investigative|secondary]
    title: "[Article/document title]"
    accessed: [TODAY in YYYY-MM-DD]
---
```

**Body:** 2-3 paragraphs of markdown, factual and neutral tone. Use summary as base and expand with context from sources.

### Step 6: Verify Build

**What the agent does:**
1. Create the entry file (write to filesystem)
2. Run: `npm install` (once, if not already done in this run)
3. Run: `npm run build`
4. Check if build succeeds

**If build fails:**
→ Go to **Step 8: Failure Handling** (note: build error in comment)

**If build succeeds:**
→ Continue to Step 7

### Step 7: Add Status Comment to Issue

**If successful so far, add comment:**
```markdown
✅ **Entry recorded successfully**

Entry created: `[slug]`
Event date: YYYY-MM-DD
Jurisdiction: [jurisdiction]
Location: [location]
Abuses: [abuse-1, abuse-2]

Branch: `entry/[slug]`
PR: (will be created next)

**Validation results:**
- ✓ All required fields present
- ✓ URLs verified and normalized
- ✓ Location meets jurisdiction requirements
- ✓ Abuses valid and in taxonomy
- ✓ Sourcing meets floor (1 primary OR 2 investigative)
- ✓ Build validation passed

Ready for editorial review.
```

### Step 8: Create Branch & Commit

**What the agent does:**
1. Pull latest main: `git pull origin main`
2. Create branch: `git checkout -b entry/[slug]`
3. Stage file: `git add src/entries/YYYY/MM/DD/[slug].md`
4. Commit: `git commit -m "Record entry: [slug]\n\nCloses #[issue-number]"`
5. Push: `git push origin entry/[slug]`

### Step 9: Create Pull Request

**GitHub API call:**
```
POST /repos/TheStanding-Publication/TheStanding/pulls
```

**PR details:**
- Title: `[Entry] [Headline]`
- Body: See PR template below
- Head: `entry/[slug]`
- Base: `main`

**PR body template:**
```markdown
Closes #[issue-number]

## Entry Details

**Slug:** [slug]
**Event date:** YYYY-MM-DD
**Jurisdiction:** [jurisdiction]
**Location:** [location]
**Abuses:** [abuse-1, abuse-2]

## Validation Summary

✓ All required fields present
✓ URLs verified and normalized  
✓ Actors verified against registry
✓ Location meets jurisdiction requirements
✓ Abuses valid and in taxonomy
✓ Sourcing meets floor (1 primary OR 2 investigative)
✓ Build validation passed

## For Review

- Is headline factual and neutral?
- Is summary accurate and 2-3 sentences?
- Are abuses correctly mapped?
- Are actors correctly named?
- Any missing sources or context?
- Any related episodes to link?

---

*Automated entry recording from issue #[issue-number]*
```

**Add labels:**
- `entry-intake` (always)
- `[primary-abuse]` (abuse slug, e.g., `defying-subpoenas`)

### Step 10: Clean Up Git

**What the agent does:**
1. Switch back to main: `git checkout main`
2. Delete local branch: `git branch -d entry/[slug]`

### Step 11: Failure Handling

**If any validation fails:**

1. **Determine error type and message**
2. **Check what failed:**
   - URL validation: All primary sources dead?
   - Other validation: Which field(s) failed?
   - Build error: What does build output say?
3. **Format appropriate comment for issue**

**If all primary sources are dead:**
```markdown
⏸️ **URL validation hold**

All primary sources for this event are currently unreachable:
- [URL] → 404
- [URL] → timeout

This issue will be re-evaluated in 24 hours. If primary sources come back online, entry will be recorded automatically.

**Sources to check:**
[List dead primary URLs]
```
Add label: `url-validation-hold`

**For other validation failures:**
```markdown
❌ **Entry recording failed**

Entry could not be recorded due to:

**[Error type]:** [Specific error]

**Details:**
[What went wrong, which field(s), why]

**To fix:**
[Specific, actionable steps]

Comment here when fixed, and it will be re-evaluated.
```

**Special case — invalid abuse slug(s):** When one or more mapped abuses are not in `/taxonomy/abuses.yaml`, the failure comment **must** include the closest valid slugs as suggestions, not just "not in taxonomy". Compute closeness with (a) substring containment against slug AND title, (b) Levenshtein distance ≤ 4 as a fallback. Surface up to 3 candidates per invalid slug. Without this, the upstream monitor can't self-correct on the next pass.

Example:
```markdown
❌ **Entry recording failed**

**Invalid abuse slugs:** 2 of 2 mapped abuses are not in the taxonomy.

- `voter-dilution` — not in taxonomy. Closest valid slugs: **`gerrymandering`**, `voter-suppression`, `voter-roll-purges`
- `electoral-manipulation` — not in taxonomy. Closest valid slugs: **`gerrymandering`**, `post-election-overturning-attempts`, `disinformation-campaigns`

**To fix:** Edit the "Mapped abuses" section of this issue to use slugs that exist in `taxonomy/abuses.yaml`, then comment so the skill re-evaluates.
```

3. **Add comment to issue with error details**
4. **Skip to next issue** (don't stop execution)

### Step 12: Final Report

After processing all issues, agent outputs summary:

```
=== ISSUE TO ENTRY PROCESSING REPORT ===

Run date: YYYY-MM-DD HH:MM:SS
Mode: [--all | --issue N]
Limit: [N or unlimited]

RESULTS:
- Total issues processed: N
- Successful PRs created: N (links to PRs)
- Failed validations: N (with reasons)
- URL holds placed: N

SUCCESSFUL ENTRIES:
- #42: [slug] → PR #XXX
- #43: [slug] → PR #XXX

FAILURES:
- #44: All primary sources dead (24h hold)
- #45: Invalid abuse slug (needs fix)

Next steps:
- Review open PRs
- Check url-validation-hold issues in 24 hours
```

---

## Key Principles

1. **One issue per PR** — No batching across issues
2. **Fail gracefully** — Validation failure = comment + skip, not stop
3. **Deterministic slugs** — Same issue data always produces same slug
4. **Paper trail** — All failures documented in issue comments
5. **Build validation** — Every entry must pass `npm run build`
6. **Source preservation** — Dead URLs get marked for hold, not removed
7. **Automatic recovery** — 24-hour hold issues re-check automatically

## Error Scenarios

| Scenario | Action |
|----------|--------|
| Issue parse fails | Comment: "Could not parse issue body" |
| Required field missing | Comment: "Missing [field]" |
| Invalid abuse slug | Comment: "Abuse '[slug]' not in taxonomy" |
| All primary URLs dead | Add `url-validation-hold` label + comment |
| Sourcing insufficient (after cleaning) | Comment: "Insufficient sources after URL cleanup" |
| Build fails | Comment: Show build error + guidance |
| Git command fails | Comment: "Could not create branch (git error)" |
| PR creation fails | Comment: "Could not create PR (GitHub error)" |

---

## Testing

**Dry-run equivalent:** Use `--issue N` with a known good issue to test end-to-end without affecting multiple issues.

**Common test scenarios:**
1. Test with issue that has all dead primary URLs (should go on hold)
2. Test with issue that has redirect (should update URL)
3. Test with issue that's missing a required field (should comment with error)

---

## Notes for Implementation

- GITHUB_TOKEN must be set in environment
- npm must be installed with dependencies (npm install runs once)
- Git must be configured (user.name, user.email for commits)
- **Always clone into a fresh, agent-owned working directory** (e.g. `mktemp -d`). Do **not** operate on a user's existing local checkout — local checkouts may have stale state, uncommitted changes, divergent branches, or filesystem mounts that corrupt git's binary index files. A fresh clone makes the run reproducible and removes the "agent should handle stale state" caveat entirely.
- All timestamps should be in YYYY-MM-DD format or ISO 8601 with timezone

## Upstream Contract (STANDING_MONITOR_SKILL)

This skill assumes the upstream monitor produces issues that meet the following preconditions:

1. The issue carries the `monitoring-intake` label. (Without this, the Step 1 search filter returns zero results and the agent has no work to do.)
2. The body uses `**Date:**` (or `**Scan date:**`) and `**Event date:**` headers in the format shown in Step 2.
3. Every slug in "Mapped abuses" exists in `taxonomy/abuses.yaml` at the time the issue is opened.

If any of these preconditions are violated, this skill reports the issue in its failure-handling flow and skips it — it does **not** silently process broken issues. Fix STANDING_MONITOR_SKILL upstream rather than papering over broken intake here.
