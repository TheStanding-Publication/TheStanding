# The Standing: Entry Recording Skill

## Purpose
Take a monitoring-intake GitHub issue (or tip submission), run automated validation checks, record it as an entry file, and create a PR for human review.

## Input
- GitHub issue with `monitoring-intake` label (or `tip` label for manual submissions)
- Issue contains all fields gathered by monitoring system or submitted via tip form

## Workflow

### 1. Parse Issue Content
Extract from issue:
- Headline
- Summary/event description
- Event date
- Jurisdiction
- Location (city/county/state)
- Actors (named individuals/organizations)
- Abuses (mapped taxonomy slugs)
- Sources (with URLs)
- Confidence level (for tips; monitoring uses "preliminary")

### 2. Automated Validation Checks

#### URL Validation (REQUIRED)
For each source URL:
1. **Live check**: GET request to verify URL returns 200 OK (not 404, 410, etc.)
2. **Content integrity**: 
   - Calculate hash/checksum of current page content
   - Compare against hash recorded in issue (if available)
   - If no hash: calculate and store current hash for audit trail
   - Flag if content has changed significantly since issue creation
3. **Archive snapshot**: Capture a snapshot (WayBack Machine or local) before publishing
4. **Pass/Fail**: All URLs must be live. If any URL is dead, issue fails validation and cannot be recorded.

#### Actors Validation
For each actor listed:
1. Check if actor name appears in latest version of source articles
2. If actor exists in `actors.yaml`:
   - Verify the name matches the normalized version from actors.yaml
   - Use normalized version in entry (not the variant from article)
3. If actor doesn't exist in actors.yaml: use the name as found in sources
4. **Pass/Fail**: All actors must be verified against source articles. Typos or mismatches must be corrected.

#### Jurisdiction & Location Validation
1. Jurisdiction must be: Federal / State / Local / International / Private actor
2. **Location requirements:**
   - Federal: location optional (can be "N/A" or nationwide)
   - State: state required (e.g., "Colorado")
   - Local: city/county/state required (e.g., "Denver, Colorado" or "Douglas County, Colorado")
   - International: country required
   - Private actor: location required if relevant
3. **Pass/Fail**: Location must meet requirements for jurisdiction level.

#### Taxonomy Validation
For each abuse slug listed:
1. Verify slug exists in `/taxonomy/abuses.yaml`
2. Verify corresponding ideal from abuses.yaml is consistent
3. Verify abuse definition matches the event (no mismatches)
4. **Pass/Fail**: All abuse slugs must be valid and appropriate.

#### Required Fields Check
Ensure present and non-empty:
- `headline` (non-empty string)
- `summary` (non-empty string, 2-3 sentences)
- `event_date` (valid YYYY-MM-DD or approximate)
- `jurisdiction` (valid value)
- `location` (meets requirements above)
- `actors` (at least one, all verified)
- `abuses` (at least one valid slug)
- `sources` (at least one live URL)

### 3. Slug Generation

**Format: `issue-{#}-{jurisdiction}-{abuse}`**

Where `{jurisdiction}` is determined by these rules:
1. **If acting under federal authority**: use `federal` (regardless of actor type)
2. **Otherwise, track where the abuse takes place**:
   - Abuse at specific location (state/local): use state abbreviation (CO, NY, TX, etc.)
   - Private actor with broad/multi-location policy impact: use `private`
   - International: use `intl`

**Examples:**
- `issue-42-federal-voter-suppression` (federal election office suppressing voters)
- `issue-15-co-excessive-force` (police abuse in Colorado)
- `issue-28-private-press-retaliation` (Meta's content moderation policy affecting multiple states)
- `issue-30-intl-accepting-foreign-electoral-help` (foreign interference in elections)

**Primary abuse selection** (if entry maps to multiple abuses):
- Use the first/primary abuse listed in the entry's `abuses` field
- Editorial can reorder if needed during review

### 4. Create Entry File
If all validation checks pass:

**File path:** `/src/entries/YYYY/MM/DD/[slug].md`

**File format:**
```yaml
date: YYYY-MM-DD
archived: [TODAY]
slug: [generated-slug]
status: published

headline: "[Headline from issue]"
summary: >
  [Summary from issue, reformatted if needed for clarity]

abuses:
  - [abuse-slug-1]
  - [abuse-slug-2]

episodes: []

actors:
  - "[Actor 1 (normalized if in actors.yaml)]"
  - "[Actor 2 (normalized if in actors.yaml)]"

jurisdiction: [federal|state|local|international|private-actor]
location: "[City, State or State or Country as appropriate]"

confidence: [monitoring|preliminary|well-reported|primary-source]

sources:
  - url: "[Source URL 1]"
    hash: "[SHA256 hash of content at time of archiving]"
  - url: "[Source URL 2]"
    hash: "[SHA256 hash of content at time of archiving]"
```

### 5. Create Pull Request
Create a PR with:
- **Title:** `[Entry] [Headline]` (or `[Monitoring] Issue #[number]` if from automated monitoring)
- **Branch:** `entry/[slug]` (based on generated slug)
- **Base:** `main`
- **Description:**
  ```
  Closes #[original-issue-number]
  
  Entry: [slug]
  Date: [event-date]
  Jurisdiction: [jurisdiction]
  Location: [location]
  Abuses: [abuse-1, abuse-2]
  
  **Validation checks passed:**
  - ✓ All URLs live and content verified
  - ✓ Actors verified against sources
  - ✓ Location meets jurisdiction requirements
  - ✓ All taxonomy abuses valid
  - ✓ All required fields present
  
  **For review:**
  - Is this event entry-worthy per standards?
  - Are actors correctly named/identified?
  - Are abuses appropriately mapped?
  - Is summary accurate?
  - Any related episodes to link?
  ```

### 6. Report Results
After recording and PR creation, report:
- Entry slug
- PR URL
- Which checks passed/failed (if any flagged for review)
- Any actors that required normalization
- Any sources that showed content changes

## Key Principles

1. **URL integrity is critical**: Dead links are a blocker. Content changes must be flagged.
2. **Actors must be verified**: Against latest sources, normalized if in actors.yaml.
3. **Location is required** (except federal, where it's optional).
4. **Taxonomy must be valid**: All abuse slugs must exist and be appropriate.
5. **Slug generation deferred**: Needs separate design work (see TODO above).
6. **PR is for human review**: Automated checks pass, but humans decide if entry-worthy.

## Differences: Monitoring vs. Tips

**Monitoring intake (`monitoring-intake` label):**
- Automated checks only
- Skip human editorial review at issue stage
- Confidence: "monitoring"
- PR describes as automated entry

**Tip submissions (`tip` label):**
- Human reviews issue first (editorial decides if worth investigating)
- If approved, runs same automated checks
- Confidence: varies by source quality
- PR is secondary review gate

## TODO

1. **Design slug generation**: Issue number + date + other identifiers
2. **Implement URL content hashing**: SHA256 or similar to detect changes
3. **Archive snapshot strategy**: WayBack Machine integration or local archiving
4. **Handle failures gracefully**: What happens if URL validation fails? Who gets notified?
