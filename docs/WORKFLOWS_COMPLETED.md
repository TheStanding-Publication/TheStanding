# The Standing: Workflows Completed (May 18, 2026)

## Summary
Completed the full suite of workflow skills for The Standing's sourcing, entry recording, editorial review, and distribution processes. All workflows are now documented and integrated.

---

## Completed Workflows

### 1. ✓ Internal Sourcing (Automated News Monitoring)
**Skill:** `STANDING_MONITOR_SKILL.md`
**Status:** UPDATED to agent-based evaluation (semantic understanding, not keyword matching)

**Key features:**
- **Search:** Major outlets (NYT, WaPo, NPR, AP, Reuters, BBC) daily
- **Evaluate:** Claude agent semantic assessment of relevance (not pattern matching)
- **Research:** Comprehensive data gathering upfront (date, actors, jurisdiction, location, sources)
- **Duplicate check:** Prevent re-filing of same events
- **Create issues:** Auto-generate GitHub issues with full event data
- **Schedule:** 4x daily (8am, 12pm, 4pm, 8pm ET)

**Agent-based evaluation principle:**
Claude understands that "weakening Voting Rights Act enforcement" = voter suppression without requiring exact keyword matches. Evaluates like an editor assessing newsworthiness through the lens of democratic health.

**Scheduled tasks updated:**
- `standing-monitor-morning` → Updated prompt
- `standing-monitor-midday` → Updated prompt
- `standing-monitor-afternoon` → Updated prompt
- `standing-monitor-evening` → Updated prompt

---

### 2. ✓ External Sourcing (Tips/Submissions)
**Status:** Existed; referenced by EDITORIAL_WORKFLOW_SKILL.md

**Channels:**
- Email: tips@thestanding.us
- GitHub: Issue form

**Process:** Tips create GitHub issues labeled `tip`, then go through editorial triage (entry-worthy?) before research and recording.

---

### 3. ✓ Entry Recording (Automated Validation & PR Creation)
**Skill:** `ENTRY_RECORDING_SKILL.md`
**Status:** Comprehensive, referenced by editorial workflow

**Validation checks:**
- URL validation (live check + content hashing for integrity)
- Actors validation (verified against sources, normalized)
- Jurisdiction & location validation (location required per jurisdiction)
- Taxonomy validation (abuses must exist and be appropriate)
- Required fields check (headline, summary, date, actors, abuses, sources)

**Slug generation:** `issue-{#}-{jurisdiction}-{abuse}`
- Examples: `issue-42-federal-voter-suppression`, `issue-15-co-excessive-force`

**Output:** Entry file + PR for human approval

---

### 4. ✓ Editorial Workflow (Review & Approval)
**Skill:** `EDITORIAL_WORKFLOW_SKILL.md` — NEW

**Two channels with different workflows:**

**Monitoring-intake (automated):**
- Automated issue creation (comprehensive research included)
- Optional editorial comment on issue
- Automated entry recording → PR creation
- PR review (APPROVAL GATE) → Approve/Reject/Revise
- Merge to publish

**Tips (manual):**
- Tip submission → Issue created
- Editorial triage (First Gate): Is this worth investigating?
- Research phase
- Editorial issue review (Second Gate): Can we record this?
- Automated entry recording → PR creation
- PR review (Approval Gate): Same as monitoring
- Merge to publish

**Key principle:** Broken-windows doctrine — no significance threshold, only proper sourcing + relevant abuse.

**Approval checklist included** for all PR reviews covering:
- Factual, neutral headlines
- Location meeting jurisdiction requirements
- Correct abuse mapping
- Live URLs with verified content
- Confidence level appropriate to sources
- No over-mapping or misapplied abuses

---

### 5. ✓ Taxonomy Application (Abuse Mapping)
**Skill:** `TAXONOMY_APPLICATION_SKILL.md` — NEW

**Decision trees provided for:**
- Election-related events (voter-suppression, election-denial, etc.)
- Law enforcement / protest events (excessive-force, protester-surveillance, etc.)
- Press / speech events (press-retaliation, prosecution-of-journalists, etc.)
- Government accountability (defying-subpoenas, IG-firings, obstruction, retaliation-against-whistleblowers, etc.)
- Corruption / self-dealing (nepotism, self-dealing, bribery, conflicts, pay-to-play, etc.)

**Guidelines:**
- Identify primary abuse (the core of what happened)
- Include secondary abuses sparingly (1-3 total typical)
- Avoid over-tagging (tag abuse, not actor)
- Avoid tagging political disagreement (unless institutional abuse)

**Common over-tagging mistakes documented** with examples and corrections.

**Auto-derivation rule:** Parent ideals are automatically generated from abuse tags at build time. Only tag the specific abuse.

---

### 6. ✓ Daily Newsletter (Buttondown Distribution)
**Skill:** `DAILY_DIGEST_SKILL.md` — NEW

**Process:**
- Fetch all entries published today (archived: TODAY)
- Format each entry with headline, summary, location, actors, abuses, and archive link
- Assemble newsletter with optional editor's note
- Publish to Buttondown via REST API
- Schedule: 6:00 AM ET daily

**Newsletter template provided** with formatting rules:
- Headline: Use as-is (already vetted)
- Location: Display based on jurisdiction
- Actors: List in order with roles if available
- Abuses: Friendly names (voter-suppression → Voter Suppression)
- Archive link: `https://thestanding.us/entries/[slug]/`

**Fallback behavior:** If no entries, send notice to maintain subscriber engagement.

**Metrics:** Tracks from Buttondown (subscriber count, open rate, click-through rate).

---

### 7. ✓ Actor Normalization (Alias Management)
**Skill:** `ACTOR_NORMALIZATION_SKILL.md` — NEW

**When to add alias:**
- Actor appears in ≥3 entries with different name variations
- Build system flags probable duplicates via string similarity

**Canonical name rules:**
- Individuals: Full formal name without title
- Organizations: Full official name
- Examples: "Stephen Miller" (not "Steve Miller"), "U.S. Department of Justice" (not "DOJ")

**Special cases documented:**
- Name changes (e.g., gender transition)
- Organizational mergers/splits/rebranding
- People with multiple roles over time
- International names with transliteration variations

**Maintenance:**
- Monthly audit of `taxonomy/aliases.yaml`
- Build process flags probable duplicates
- Editor creates aliases and submits PR

**Integration:** Aliases file enables:
- Consistent actor pages (one page per canonical name)
- Accurate actor appearance counts (≥3 threshold for actor pages)
- See-also relationships built on shared actors/abuses

---

## Location Field Integration

**Fully integrated into:**
- ✓ Entry recording (validation required per jurisdiction level)
- ✓ Editorial workflow (approval checklist includes location verification)
- ✓ Daily digest/newsletter (location displayed for each entry)
- ✓ Entry frontmatter (location field in YAML)

**Build-time feature (future):**
- [ ] Archive pages: location searchable/filterable
- [ ] Location-based entry discovery (e.g., "All entries from Colorado")

---

## Remaining Implementation Work

**To make workflows live, need:**

1. **Test scheduled monitoring tasks**
   - Verify 4x daily tasks can fetch news and evaluate relevance
   - Confirm GitHub API access for duplicate checking and issue creation
   - Verify Claude agents have necessary tool permissions

2. **Create GitHub Actions triggers**
   - Automated entry recording on issue labeled `monitoring-intake`
   - Automated newsletter assembly at 6 AM ET

3. **Build system features (11ty)**
   - Location filtering/searching in archive
   - Actor page generation
   - See-also relationships from shared ideals/abuses

4. **Archive integration**
   - Wayback Machine snapshots of source URLs
   - IPFS pinning for permanence (optional)

5. **Newsletter platform**
   - Buttondown account setup
   - REST API key configuration
   - Subscriber management

---

## Files Created/Updated

**New workflow skills:**
- `EDITORIAL_WORKFLOW_SKILL.md` (2026-05-18)
- `TAXONOMY_APPLICATION_SKILL.md` (2026-05-18)
- `DAILY_DIGEST_SKILL.md` (2026-05-18)
- `ACTOR_NORMALIZATION_SKILL.md` (2026-05-18)

**Updated:**
- `STANDING_MONITOR_SKILL.md` (agent-based evaluation, 2026-05-18)
- Scheduled monitoring tasks x4 (agent-based prompts, 2026-05-18)
- `TASKS.md` (workflow completion tracking)

**Existing (comprehensive):**
- `STANDING_MONITOR_SKILL.md` (sourcing)
- `ENTRY_RECORDING_SKILL.md` (validation & recording)
- `PROJECT_PLAN.md` (full design document)

---

## Architecture Summary

**Data flow:**

```
External Tips              Internal Monitoring
       ↓                           ↓
GitHub Issue (tip)         GitHub Issue (monitoring-intake)
       ↓                           ↓
Editorial Triage            [Optional comment]
       ↓                           ↓
[If approved]         Automated Entry Recording
       ↓                           ↓
Research Phase              PR Created
       ↓                           ↓
Editorial Review       ┌─ Editorial PR Review (GATE)
       ↓               │
[If approved]  ← ─ ─ ─┘
       ↓
Automated Entry Recording
       ↓
       └─────────────────── PR + Entry File
                                  ↓
                        ┌─ Editorial PR Review (GATE)
                        │
                    [Merge to main]
                        ↓
                    ✓ Published to Archive
                        ↓
          ┌─────────────────┴────────────────┐
          ↓                                  ↓
    Daily Digest Assembly (6 AM ET)   Archive Pages
          ↓                           (auto-generated)
    Buttondown Newsletter Send
```

---

## Key Principles Embedded

1. **Broken-windows editorial policy:** No significance threshold; proper sourcing + relevant abuse is the criterion.
2. **Agent-based evaluation:** Semantic understanding, not keyword pattern matching.
3. **Comprehensive research upfront:** All event data gathered before issue creation (prevents editorial waste).
4. **Location as required field:** Captured throughout workflows; required per jurisdiction level.
5. **Public-from-day-one:** Git history is audit trail; all edits timestamped and attributable.
6. **Automated validation gates:** URL integrity, actor verification, taxonomy validation before human review.
7. **Two-stage editorial:** Monitoring uses PR review as gate; tips use issue + PR review.
8. **Taxonomy-driven:** All entries tagged with specific abuses; ideals auto-derived at build time.

---

## Single Points of Truth

Each workflow has one authoritative skill document:
- **Monitoring:** `STANDING_MONITOR_SKILL.md` (referenced by 4 scheduled tasks)
- **Entry Recording:** `ENTRY_RECORDING_SKILL.md`
- **Editorial:** `EDITORIAL_WORKFLOW_SKILL.md`
- **Taxonomy:** `TAXONOMY_APPLICATION_SKILL.md`
- **Newsletter:** `DAILY_DIGEST_SKILL.md`
- **Actors:** `ACTOR_NORMALIZATION_SKILL.md`

All scheduled tasks, GitHub Actions, and other automation reference these skills for workflow definition.

---

## What's Ready to Test

- ✓ Monitoring system (scheduled tasks with agent-based prompts)
- ✓ Entry recording workflow (validation checks + PR generation)
- ✓ Editorial approval process (checklists and workflows)
- ✓ Newsletter assembly logic (formatting rules and templates)
- ✓ Actor normalization process (alias creation and maintenance)

**Next:** Run a monitoring task manually to verify it can execute its workflow end-to-end.
