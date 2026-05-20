# The Standing: Issue to Entry Skill (Claude Agent)

## Purpose
Claude agent that converts open GitHub issues opened by the `thestanding` bot account into fully recorded entry files, feature branches, and pull requests. Runs on schedule or on-demand.

## Invocation

```bash
# Process all eligible issues (default for scheduled runs)
/issue-to-entry --all

# Process specific issue
/issue-to-entry --issue 42

# Limit issues per run (e.g., max 5)
/issue-to-entry --all --limit 5
```

## Modes

This skill runs in one of two modes. Both execute the identical Step 1-12 workflow below; the mode only affects which issues enter the queue.

### Scheduled-batch mode (default)

Invoked by the `standing-entry-recorder` scheduled task. Processes eligible issues from the repository queue.

- `--all` — process every eligible issue.
- `--limit N` — cap the number processed per run. The scheduled task uses `--limit 1` (one issue per run, lowest-numbered first), so entry PRs arrive at a steady, reviewable pace rather than in a large batch.

### Manual mode

Invoked on-demand by an operator.

- `--issue N` — process exactly issue #N. The agent still runs the full Step 1 eligibility check on #N (open, authored by `thestanding`, no `invalid` label, no open PR referencing it) and refuses with a clear error if #N is not eligible, rather than processing it anyway.

## Implementation Overview

This skill is a Claude agent that orchestrates the full workflow:
1. Fetch open issues authored by `thestanding` from GitHub
2. For each issue: re-read sources, validate-and-correct, create entry, verify build
3. Create branch, commit, push to GitHub
4. Create PR with appropriate labels
5. Report summary of what was processed (entries recorded, issues discarded, corrections made)

**Key principle:** This agent is responsible for **validity**, not just transcription. Each step is a chance to detect and correct drift between what the monitor saw and what's actually true now. An invalid issue is either corrected by the agent or skip-flagged with the `invalid` label and an explanatory comment.

## Validation Philosophy

The upstream monitor produces issues in good faith based on what it saw at scan time. By the time this skill runs, things may have changed: the taxonomy may have evolved, articles may have been retracted or corrected, headlines may have been revised, the bot may have made an honest taxonomy mistake. **This skill exists to bridge that gap.**

What the agent will correct in flight (no human intervention, just a note in the PR body):

- **Invalid or stale taxonomy slugs** — re-derive correct abuse slugs from the issue body and current source content, mapped against the live `taxonomy/abuses.yaml`. Do not fail because the monitor used an out-of-date or invented slug.
- **Field normalization** — jurisdiction free-text like "State (Tennessee)" → `jurisdiction: state` and `tn` in the slug; location parentheticals stripped; actor list filtered to those who took the action (not contextual or target parties); etc. Use judgment; don't write a parser.
- **Headline / summary drift** — if the article's current headline or framing has shifted from the issue's claim, the entry reflects the current truth, not the snapshot.

What the agent will skip-flag (skip + comment + `invalid` label, leave issue open for human review):

- **Body is incomprehensible** as a news event description.
- **All primary sources have been retracted** or the live article content contradicts the issue's claim about what happened.
- **No abuse in `taxonomy/abuses.yaml` cleanly applies** to what the sources actually describe (and the agent is confident, not just unsure — uncertainty defaults to correction, not discard).
- **The "event" is debunked** by subsequent reporting between scan time and process time.

The agent does NOT close issues, even when flagging them invalid. Closure is a human call.

---

## Detailed Agent Workflow

### Step 1: Fetch Eligible Issues

**Eligibility criterion:** the issue is open and was opened by the `thestanding` bot account. That is the **only** eligibility criterion. Labels, title prefixes, and naming conventions are intentionally **not** part of the filter — they're brittle (require upstream coordination, drift over time) and the bot's authorship is the canonical signal that this is a monitor-produced issue intended for entry recording.

**What the agent does:**
- Call GitHub API to search for issues
- Query: `is:issue state:open author:thestanding sort:number-asc`
- Skip issues that already carry the `invalid` label (those are skip-flagged from a prior run; a human needs to remove the label to make them eligible again).
- **Skip issues that already have an open PR referencing them.** This is critical when the skill runs on a schedule — a single in-flight entry PR can sit in review for hours or days, and without this check the next scheduler run would re-process the same issue and open a duplicate PR.
- Build list of issues to process

**GitHub API call:**
```
GET /search/issues?q=repo:TheStanding-Publication/TheStanding+is:issue+state:open+author:thestanding&sort=number&order=asc&per_page=100
```

**Checking for an existing open PR (per issue):**

For each candidate issue `N`, fetch the open PRs in the repo and check whether any references the issue via a closing keyword in the PR body:

```
GET /repos/TheStanding-Publication/TheStanding/pulls?state=open&per_page=100
```

A PR "references" issue `N` if its body contains any of: `Closes #N`, `Closes: #N`, `Fixes #N`, `Fixes: #N`, `Resolves #N`, `Resolves: #N` (case-insensitive, also accept the fully-qualified `TheStanding-Publication/TheStanding#N` form). If a match is found, skip issue `N` — its entry is already in flight.

> Use judgment, not a brittle regex match: the rule is "is there an open PR whose author intent is to close this issue?" In practice the closing keywords cover every PR this skill itself produces (Step 9 mandates `Closes #N` in the PR body), and a human-authored PR that addresses the issue almost always uses one of these keywords too.

> **Notes:**
> - `is:issue` is required by GitHub's search API; without it the API returns HTTP 422.
> - `author:thestanding` is what makes the issue eligible. If the bot account login changes, update this filter (and the corresponding line in `Notes for Implementation`).
> - PRs opened by `thestanding` are excluded automatically from the issue search by the `is:issue` qualifier.

**Handle:**
- If `--issue N` flag: fetch only issue #N (and verify author is `thestanding` before processing — refuse with a clear error if it isn't, to prevent accidental runs against human-opened issues). The open-PR check above still applies — if `--issue N` is passed for an issue that already has an open PR, refuse with a clear error rather than opening a duplicate.
- If `--all` flag: fetch all eligible (respecting `--limit` if provided)
- Authentication: Use `GITHUB_TOKEN` environment variable

### Step 2: For Each Issue - Parse Issue Body

**Expected format** (from STANDING_MONITOR_SPEC output):
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

> **Parser tolerance:** accept both `**Date:**` and `**Scan date:**` for the scan/report-date field. The upstream STANDING_MONITOR_SPEC currently emits `**Date:**`; older fixtures used `**Scan date:**`. Either should work without manual cleanup.

### Step 3: Validate and Correct

For each field, ensure it can produce a valid entry. The agent reads the issue body, applies judgment, and produces a clean working dictionary. **Most "validation failures" are correctable in place — don't skip-flag on things the agent can clearly fix.**

Required fields and what counts as "valid enough":

- `headline` — non-empty, <100 chars. Correct from the issue title or first sentence of "What happened" if missing.
- `summary` — 2-3 sentences. Compress from "What happened" + "Analysis" if needed. If sources have updated the framing since the issue was written, write the summary to current reality, not the snapshot.
- `date` (event date) — YYYY-MM-DD. Parse out of the issue body's `**Event date:**` line. If the body has approximate dates ("early May 2026"), agent picks the most defensible specific date and notes the imprecision in the entry body.
- `jurisdiction` — must end up as exactly `federal`, `state`, `local`, `international`, or `private-actor`. The issue body may say "State (Tennessee)" or "Federal (nationwide)" — strip parentheticals and normalize. Capture any state code into the slug-generation context.
- `location` — free-text string. Strip helpful-but-noisy parentheticals like "(9th Congressional District)" from the location string itself; if that context matters for the entry, it goes in the body, not the metadata.
- `actors` — at least 1. Filter to entities who *took the action*: a court whose ruling created the legal context is not an actor in the gerrymandering; a targeted incumbent is not an actor in the gerrymandering. Use judgment, don't blindly transcribe the issue's list.
- `abuses` — at least 1; **every slug must exist in the current `/taxonomy/abuses.yaml`**. If the issue uses slugs that aren't in the taxonomy (or aren't in it anymore), the agent re-derives the right slugs by reading the issue body and source articles against the taxonomy's `slug + title + description` fields. Note any re-derivation in the PR body. Do **not** fail just because the upstream monitor used a stale or invented slug.
- `sources` — at least 1 primary OR 2 investigative, each with url/publisher/tier/title. Step 4 will do the heavy work of source verification.

**When correction isn't enough:** if the agent cannot in good conscience produce a valid entry from this issue (the event isn't real, the body is incoherent, the taxonomy genuinely has no place for it), → **Step 11: Discarding Issues**.

### Step 4: Source Re-verification (URL + Content)

This is more than a 200-OK check — but it is also not an exhaustive re-read of every link. The agent fully re-verifies the **primary source(s)** and corroborates the entry's key details against **one genuinely independent source**; remaining sources get only a lightweight liveness check. The agent makes these calls with judgment; no fixed status-code table.

**Verification standard — two independent sources agree.** A detail — the event, its date, the actors, the outcome — counts as confirmed when the primary source supports it *and* a second, independent source agrees. This is the newsroom two-source rule, and it is what "the details are correct" means here: confirmation comes from primary-source documents the entry can cite, not from an AI-generated search summary and not from "it sounds plausible." If the primary and the corroborator disagree on a material detail, that disagreement is itself a finding — resolve it against the source record, or surface it via Step 11 if it cannot be resolved. Where the primary source is itself the authoritative record of the event — a court opinion, an agency statement, the Federal Register — it stands on its own; a second source is welcome corroboration but not required.

**Prioritization and stopping point.** Re-verify in priority order — primary source(s) first, then the strongest independent corroborator. Once the primary is verified and one independent source corroborates the key details, the event is confirmed; stop there. Do not full-read every remaining link for completeness — give the rest a lightweight liveness check (does the URL still resolve; is it not a 404 or a retraction notice). Promote one of them to a full content read only if a primary fails re-verification and a secondary has to carry the event instead.

For each source you fully re-verify:

1. **Fetch the page** using a browser-like User-Agent (e.g. `Mozilla/5.0 (compatible; TheStandingBot/1.0; +https://thestanding.us)`) and follow redirects. Capture the final URL if redirected.

2. **Interpret the response with judgment**, not a status-code table:
   - **Page loads and the article is present** → live source, continue to content check.
   - **404 / 410 / page replaced with a "this article is no longer available" notice** → the article is gone. This is a dead source.
   - **403 / 406 / 451 / 5xx with a known reputable publisher** → almost always bot-blocking by the publisher's WAF, not actually missing content. Keep the source in the entry. Note in the PR body that human review of the URL is appropriate. Do not drop the source.
   - **TLS / DNS / connection failure on a known domain** → most likely transient. Retry once with backoff; if still failing, keep the source but flag for review.
   - **Known-hard publishers** → some outlets (notably the Washington Post) run aggressive anti-bot / WAF systems that produce repeated timeouts or 403s even on healthy, current articles. When the source is one of these, use a longer initial timeout and treat a repeat failure as "keep with note" immediately — do not burn multiple retry cycles. A repeated timeout from a known-hard publisher is evidence the publisher blocks automated clients, not evidence the article is gone.

3. **Read the article content** and verify it still supports the entry:
   - **Does the article confirm the event happened as the issue describes?** If the live article says something materially different — different date, different actors, different outcome — update the entry to reflect the article. The article is the source of truth, not the issue's snapshot.
   - **Look for explicit correction or retraction notices** in the article: "Correction:", "Update:", "Retracted:", "This article has been updated to reflect…", "[Editor's note]". If present:
     - **Correction** that doesn't change the core event → reflect in the entry body, note the correction in the PR.
     - **Substantive update** that changes the framing → rewrite the entry summary to match current state.
     - **Retraction** → treat this source as effectively dead for this event.
   - **Compare current headline to the issue's claimed headline.** If the headline has been revised substantively (not just typo fixes), use the current headline in the entry's source list, and note the change in the PR.

4. **After re-verification, evaluate sourcing floor:**
   - **All primary sources retracted or contradict the issue** → the event itself is in doubt. Skip-flag via Step 11 with a comment summarizing what the sources now say.
   - **Sourcing floor not met** (need 1 primary OR 2 investigative remaining) → Step 11.
   - **Otherwise** → continue with the verified, possibly-updated source list.

5. **Record per-source notes** in the entry's `sources:` list when re-verification surfaces something useful: `note: "Article updated 2026-05-15 to add quote from Senate spokesperson"`, `note: "WAF returns 403 to automated checks; article verified live"`, etc.

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
id: [generated UUID v4]
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

> **`id:` is a freshly generated UUID v4** (e.g. `550e8400-e29b-41d4-a716-446655440000`). Generate one at entry creation with `python3 -c "import uuid; print(uuid.uuid4())"` or `uuidgen`. The id is the entry's canonical identifier — globally unique, never changes — and is enforced by the build (`.eleventy.js`) for both presence and uniqueness. The slug is for URLs and display; the id is what cross-references and future graph operations should rely on. Never reuse an id from another entry, and never change an existing entry's id after publication.

> **`status:` is always `published`.** The build accepts four values (`draft`, `published`, `corrected`, `retracted` — see `.eleventy.js`) but this skill is producing live archive entries, so it sets `published` unconditionally. `corrected` and `retracted` are reserved for a future re-evaluation workflow that operates on already-published entries; `draft` is for human-authored work-in-progress and shouldn't appear in agent output. Do not leave the field unset — explicit beats implicit, and an unset status would silently skip the build's draft filter (which is fine today but is the kind of footgun worth pre-empting).

> **`quote:` is optional but recommended.** When present, structure as `quote: { text: "...", source-index: N }` where `source-index` is the 0-indexed position of the source the quote came from in the `sources:` list. **`quote.text` must be fewer than 30 words** — the build (`.eleventy.js`) throws an error if the quote is 30 words or more. Pick a tight, single-sentence quote that lands; if no source has a quote that compresses to <30 words cleanly, omit the field rather than pad. Re-check the source index after adding/removing sources during validate-and-correct (Step 3-4), since the list ordering can shift.

**Body:** 2-3 paragraphs of markdown, factual and neutral tone. Use summary as base and expand with context from sources.

### Step 6: Verify Build

**What the agent does:**
1. Create the entry file (write to filesystem)
2. Run: `npm install` (once, if not already done in this run)
3. Run: `npm run build`
4. Check if build succeeds

**If build fails:**
→ Go to **Step 11: Discarding Issues** with the build output in the comment. (Build failures here usually mean bad input — invalid YAML, malformed source URL, etc. — so the issue is skip-flagged for human review.)

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

### Step 11: Discarding Issues (Skip-Flag)

Most problems are corrected in Step 3 or Step 4 and never reach here. Step 11 only fires when the agent has concluded the issue cannot be turned into a valid entry — and even then, the agent does **not** close the issue. Closure is a human call. The agent:

1. **Adds a comment** explaining what's wrong and what the agent concluded.
2. **Applies the `invalid` label.**
3. **Skips to the next issue.**

The issue stays open. A human can decide whether to fix the underlying problem (update the body, restore a source, update the taxonomy) and remove the `invalid` label to make it eligible again on the next run.

**When to skip-flag (not exhaustive — use judgment):**

- The body cannot be read as a news event description at all.
- All primary sources are gone OR retracted OR substantively contradict the issue's claim about what happened.
- After reading source content, the agent concludes the "event" was a misunderstanding, hoax, or was debunked by subsequent reporting.
- No abuse in `taxonomy/abuses.yaml` cleanly applies, even after re-reading the body and sources against the full taxonomy. (If the agent is uncertain rather than confident-no, that's a correction case, not a discard case.)
- Build verification (Step 6) fails in a way that points to bad input rather than a build-system bug.

**Comment template:**

```markdown
⚠️ **Marked invalid** (skip-flagged by ISSUE_TO_ENTRY)

The agent reviewed this issue and was not able to record it as a valid entry. Reason:

**[One-line summary of why]**

Details:
[2-4 sentences explaining what the agent saw — which sources were checked, what they said now vs. what the issue claimed, why no taxonomy slug applies, etc.]

What to do:
- If you can fix the underlying problem (update the body, restore a source, etc.), remove the `invalid` label and the agent will re-evaluate on the next run.
- If this issue genuinely shouldn't be recorded, close it manually.

The agent did not close this issue. That's intentional — discarding events is a human call.
```

**For corrections made in flight (not skip-flag):** the agent does not add a comment on the issue. Instead, the **PR body** describes any corrections made (re-mapped slugs, normalized fields, updated summary from current sources). This keeps issue threads clean and makes correction history reviewable at PR time, which is the right place for it.

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
- Issues skip-flagged invalid: N (with reasons)
- Corrections applied in flight: N (re-mapped slugs, normalized fields, updated summaries from current sources)

SUCCESSFUL ENTRIES:
- #42: [slug] → PR #XXX (notes: re-mapped 1 abuse slug, normalized jurisdiction)
- #43: [slug] → PR #XXX

SKIP-FLAGGED (invalid label applied, issue left open):
- #44: All primary sources retracted; live articles contradict the event claim
- #45: No taxonomy slug applies; event is real but not a Standing-tracked abuse

Next steps:
- Review open PRs
- Review issues with the `invalid` label and decide whether to fix, close, or update the taxonomy
```

---

## Key Principles

1. **One issue per PR** — No batching across issues
2. **Correct before failing** — Validation drift is corrected in flight when possible; skip-flag only when the agent concludes the issue cannot become a valid entry
3. **Deterministic slugs** — Same issue data always produces same slug
4. **Paper trail** — All failures documented in issue comments
5. **Build validation** — Every entry must pass `npm run build`
6. **Source preservation** — Dead URLs get marked for hold, not removed
7. **Automatic recovery** — 24-hour hold issues re-check automatically

## Error Scenarios

| Scenario | Action |
|----------|--------|
| Body unparseable as a news event | Skip-flag (`invalid` label + comment) |
| Required field genuinely missing | Correct from issue body / sources; if not possible, skip-flag |
| Invalid abuse slug | **Correct in flight** — re-derive from body+sources against current taxonomy |
| Stale article (correction / update / retraction) | Reflect in entry; if all primaries retracted or contradicted, skip-flag |
| All primary sources gone | Skip-flag (event in doubt) |
| Sourcing insufficient after re-verification | Skip-flag |
| Build fails on what looks like bad input | Skip-flag with build output in comment |
| Git command fails / PR creation fails | Stop run, report to operator; do not modify issue |

---

## Testing

**Dry-run equivalent:** Use `--issue N` with a known good issue (authored by `thestanding`) to test end-to-end without affecting multiple issues. The agent verifies authorship before processing, so passing an issue opened by a human will refuse rather than proceed.

**Common test scenarios:**
1. Test with issue that has all dead primary URLs (should go on hold)
2. Test with issue that has redirect (should update URL)
3. Test with issue that's missing a required field (should comment with error)
4. Test with `--issue N` against an issue **not** authored by `thestanding` (should refuse cleanly)

---

## Notes for Implementation

- GITHUB_TOKEN must be set in environment
- npm must be installed with dependencies (npm install runs once)
- Git must be configured (user.name, user.email for commits)
- **Always clone into a fresh, agent-owned working directory** (e.g. `mktemp -d`). Do **not** operate on a user's existing local checkout — local checkouts may have stale state, uncommitted changes, divergent branches, or filesystem mounts that corrupt git's binary index files. A fresh clone makes the run reproducible and removes the "agent should handle stale state" caveat entirely.
- All timestamps should be in YYYY-MM-DD format or ISO 8601 with timezone

## Upstream Contract (STANDING_MONITOR_SPEC)

The **only** hard precondition is that monitoring issues are opened by the `thestanding` bot account. Anything `thestanding` opens is in scope; anything opened by a human or different bot is out of scope. No labels or title prefixes are required.

That said, the upstream monitor *should* still produce bodies in the format shown in Step 2 — that's what makes parsing reliable. If a body deviates, this skill reports the parse/validation failure via Step 11 and skips the issue; it does not silently process broken issues. The right place to fix systematic format problems is in STANDING_MONITOR_SPEC, not by adding parser exceptions here.

**Soft expectations** (not enforced, but worth maintaining):

- Body uses `**Date:**` (or `**Scan date:**`) and `**Event date:**` headers.
- Every slug in "Mapped abuses" exists in `taxonomy/abuses.yaml` at the time the issue is opened.
- Sections appear in the order shown in Step 2.

When these expectations are violated, the failure comment posted by Step 11 tells the upstream monitor (or a human editor) what to fix.
