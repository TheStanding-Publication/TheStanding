# The Standing: Actor Normalization Skill

## Purpose
Ensure that actors (people and organizations) are consistently named across the archive, reducing fragmentation and enabling readers to find all entries related to a person or organization. This skill defines when and how to add aliases to `taxonomy/aliases.yaml`.

---

## The Problem

Without normalization, the same actor might appear as:
- "Donald Trump"
- "Trump, Donald"
- "President Trump"
- "Donald J. Trump"
- "D. Trump"

This causes fragmentation — readers searching for "Trump" might miss entries where he appears as "President Trump" or "Donald J. Trump."

**Solution:** Maintain a controlled alias file that maps variations to a canonical name.

---

## The Aliases File

**Location:** `/taxonomy/aliases.yaml`

**Format:**
```yaml
canonical_name: "Donald Trump"
aliases:
  - "Donald J. Trump"
  - "President Trump"
  - "Trump, Donald"
  - "D. Trump"
```

**Build process:** When the site builds, the system normalizes all actor names using this file. All variations are replaced with the canonical name in display.

---

## When to Add an Alias

**Rule:** Add an alias when:
1. An actor appears in multiple entries with different name variations, AND
2. That actor is appearing in ≥3 total entries (threshold for creating actor page)

**Don't prematurely normalize.** Wait until you see evidence of fragmentation across multiple entries. One-off name variations can be handled in editorial review.

### Triggers for Adding an Alias

**Trigger 1: Multiple entries show name variation**
- Entry 1: "Donald Trump"
- Entry 2: "President Trump"
- Entry 3: "Donald J. Trump"
→ Create alias

**Trigger 2: Build system flags probable duplicates**
- Build system uses Levenshtein distance + abbreviation matching to flag likely duplicates
- Example: "Steve Miller" and "Stephen Miller" in different entries
- Build output: ⚠️ Probable duplicate: "Steve Miller" ≈ "Stephen Miller"
→ Create alias if they're the same person

**Trigger 3: Known person with multiple identities**
- Example: Someone who held multiple titles (e.g., "Captain, NYPD" then "Police Commissioner")
- Don't fragment — use canonical name + roles in separate metadata
→ Create alias to unify

### Triggers to IGNORE (Don't Add Alias)

**Different people with similar names:**
- "John Smith" (senator) and "John Smith" (activist)
→ Keep separate; add clarifying role/context in entries, not aliases

**One-off typo or variation:**
- Entry: "Stephen Miller" (correct)
- Another entry: "Stephen Milller" (typo)
→ Fix the typo in editorial review; don't add alias

**Organizational rebranding:**
- "FBI" and "Federal Bureau of Investigation"
→ Use alias (both refer to same organization)

**Organizational restructuring:**
- "U.S. Department of Justice" (old) → "Department of Justice" (new)
→ Use alias; readers should find both under same organization

---

## How to Create an Alias

### Step 1: Identify the Canonical Name
**Choose the most formal/complete name:**
- For individuals: Full legal name without title
  - ✓ "Donald Trump" not "President Trump"
  - ✓ "Stephen Miller" not "Steve Miller"
- For organizations: Full official name
  - ✓ "U.S. Department of Justice" not "DOJ"
  - ✓ "Federal Bureau of Investigation" not "FBI"

### Step 2: List All Known Variations
**Search entries and sources for all versions:**
- How does the person appear in news articles? (formal, informal, abbreviated)
- How do they appear in official documents? (titles, full name)
- How do they appear in social media? (nicknames, abbreviations)

**Example: Stephen Miller**
- "Stephen Miller" (most common)
- "Stephen G. Miller" (formal)
- "Steve Miller" (informal)
- "Senior Advisor Stephen Miller" (with title)
→ Canonical: "Stephen Miller" (remove title, use formal first name)
→ Aliases: "Stephen G. Miller", "Steve Miller"

### Step 3: Add to aliases.yaml

**Edit `/taxonomy/aliases.yaml`:**

```yaml
# Existing entries above...

- canonical_name: "Stephen Miller"
  aliases:
    - "Stephen G. Miller"
    - "Steve Miller"
    - "Senior Advisor Stephen Miller"

# Continue alphabetically...
```

**Rules for the file:**
- Sort entries alphabetically by canonical name
- Canonical name should NOT be in aliases list (only in canonical_name)
- One canonical per actor (no circular aliases)
- Comments are OK to explain context

### Step 4: Test the Build

**After adding alias, run the build:**
```bash
npm run build
```

**Check:**
- No build errors
- Actor pages are generated correctly
- All variations now appear as canonical name in entries
- See-also relationships work correctly

### Step 5: Create PR

**Submit change to version control:**
- PR title: `[Alias] Normalize [Canonical Name]`
- Description: "Normalizing [number] name variations for [canonical name] across [number] entries"
- No need for approval; this is metadata; can merge after build passes

---

## Guidelines for Specific Actor Types

### Government Officials (Federal)

**Canonical format:** `[First Name] [Last Name]` (no title)
- ✓ "Donald Trump" not "President Trump"
- ✓ "Eric Holder" not "Attorney General Eric Holder"
- ✓ "Merrick Garland" not "AG Merrick Garland"

**Aliases:** Include common abbreviations, nicknames, full formal names
- "Donald Trump" → aliases: "Donald J. Trump", "President Trump", "Donald John Trump"

**Note:** Titles are tracked separately in entry metadata (e.g., "Donald Trump (President)"). Use canonical name only.

### Government Agencies

**Canonical format:** Full official name
- ✓ "U.S. Department of Justice"
- ✓ "Federal Bureau of Investigation"
- ✓ "Department of Homeland Security"

**Aliases:** Abbreviations and alternate names
- "U.S. Department of Justice" → aliases: "DOJ", "Department of Justice", "Justice Department"
- "Federal Bureau of Investigation" → aliases: "FBI", "Federal Bureau"

### State/Local Officials & Agencies

**Canonical format:** Full name with state/city context (if needed to disambiguate)
- ✓ "Governor Ron DeSantis" or "Ron DeSantis"?
  → "Ron DeSantis" (title tracked separately; state context in metadata)
- ✓ "Mayor Eric Adams" or "Eric Adams"?
  → "Eric Adams, New York" (if other Eric Adams in archive); or just "Eric Adams" (if unique)

**Aliases:** All variations including with/without location

### Private Organizations

**Canonical format:** Official legal name
- ✓ "Meta Platforms, Inc." or "Meta"?
  → "Meta Platforms, Inc." (legal name); alias: "Meta", "Facebook Inc." (former name)
- ✓ "Tesla, Inc." or "Tesla"?
  → "Tesla, Inc." (legal name); alias: "Tesla"

**Aliases:** Brand names, former names, colloquial names
- "Meta Platforms, Inc." → aliases: "Meta", "Facebook Inc.", "Facebook"

### Activist Groups / NGOs

**Canonical format:** Official legal name (if registered); otherwise most common name
- ✓ "American Civil Liberties Union" (legal name)
- ✓ "Black Lives Matter" or "Black Lives Matter Global Network Foundation"?
  → Check official registration; use legal name if distinct

**Aliases:** Abbreviations, alternate names
- "American Civil Liberties Union" → aliases: "ACLU"

---

## Special Cases

### Name Changes

**Scenario:** Person changes legal name (e.g., gender transition, marriage)
- Canonical: Use current legal name
- Aliases: Include previous legal names
- Build: Display current name; historical accuracy preserved via aliases

**Example:**
```yaml
- canonical_name: "Chelsea Manning"
  aliases:
    - "Bradley Manning"
```

### Organizational Mergers/Splits

**Scenario:** Organization merges or splits
- If organizations remain distinct: Treat as separate actors
- If organization renamed/consolidated: Use aliases

**Example (consolidation):**
```yaml
- canonical_name: "Department of Homeland Security"
  aliases:
    - "DHS"
    - "Office of Homeland Security" # former name
```

### Temporary Names vs. Canonical Names

**Scenario:** Person holds temporary title (e.g., "Acting Attorney General")
- Canonical: Base name only
- Don't include "Acting" in canonical; include in entry-level metadata if needed

**Example:**
```yaml
- canonical_name: "Jeffrey Rosen"
  aliases:
    - "Acting Attorney General Jeffrey Rosen"
```

### International Figures

**Scenario:** Non-English name with transliteration variations
- Canonical: Most common English transliteration
- Aliases: Alternative transliterations

**Example:**
```yaml
- canonical_name: "Vladimir Putin"
  aliases:
    - "Vladimir Vladimirovich Putin"
    - "V. Putin"
```

---

## Manual Normalization vs. Automatic Detection

**Manual normalization (this skill):**
- Used for actors appearing in ≥3 entries
- Proactively managed by editorial team
- Creates aliases in taxonomy file

**Automatic detection (build system):**
- Build flags probable duplicates using string similarity
- Shows warnings: "⚠️ Probable duplicate: 'Steve Miller' ≈ 'Stephen Miller'"
- Editor reviews warnings and decides whether to create alias

**Workflow:**
1. Build generates list of probable duplicates
2. Editor reviews list
3. Editor creates aliases for confirmed matches
4. Re-run build to apply normalization

---

## When NOT to Normalize

**Don't create aliases for:**

**Case 1: Genuinely different people with similar names**
- "John Smith" (senator) appearing in 2 entries
- "John Smith" (activist) appearing in 1 entry
→ Keep separate; use roles/context to distinguish, don't alias

**Case 2: Typographical errors in sources**
- Entry text has typo from source article
→ Fix typo in editorial review; don't alias
→ Exception: If same typo appears in multiple entries, then alias

**Case 3: Informal vs. formal (used consistently)**
- Some entries use "FBI" (every entry, consistently)
- Some entries use "Federal Bureau of Investigation" (every entry, consistently)
- Readers clearly understand they're the same
→ Still create alias; consistency helps discovery

**Case 4: Abbreviations for one-off appearances**
- "FBI" appears once; "Federal Bureau of Investigation" used elsewhere
→ Create alias (normalization aids discovery)

---

## Maintenance & Auditing

### Periodic Audit (Monthly)

**Task:** Review `aliases.yaml` for completeness and accuracy

**Check:**
1. Are all duplicates from build warnings captured as aliases?
2. Are canonical names still the most common form?
3. Are there obvious missing aliases (e.g., new actor appearing multiple times)?
4. Do any aliases reference actors that no longer appear in archive?

**Actions:**
- Add new aliases as needed
- Remove obsolete aliases (if actor no longer in archive)
- Update canonical names if convention changes

### PR Review for Aliases

**When someone submits PR with new alias:**
- Verify the actor appears in ≥3 entries (trigger met)
- Check that canonical name is truly canonical
- Ensure all common variations are in aliases list
- Run build to confirm no errors
- Merge after check passes

---

## Integration with Build System

**Build process uses aliases.yaml to:**
1. Normalize actor names in entry display
2. Generate actor pages (one page per canonical name)
3. Auto-detect actor pages (threshold: ≥3 entries)
4. Build see-also relationships
5. Flag probable duplicates (for next audit)

**Build warnings:**
```
⚠️ Probable duplicate actors:
  - "Steve Miller" (2 entries) ≈ "Stephen Miller" (3 entries)
  → Create alias? Run: git edit taxonomy/aliases.yaml
```

---

## Related Skills & Workflows
- EDITORIAL_WORKFLOW_SPEC.md — Entry review (where actor names are verified)
- ENTRY_RECORDING_SPEC.md — Entry creation (where actors are normalized)
- PROJECT_PLAN.md → Data Model section — Actor field definition

---

## Examples in Practice

### Example 1: Federal Official Over Time

**Entries:**
1. "Steve Miller" (2020 entry, informal style)
2. "Stephen Miller" (2024 entry, formal style)
3. "Stephen G. Miller" (2026 entry, very formal)
4. "Senior Policy Advisor Stephen Miller" (2026 entry, with title)

**Action:**
- Create alias: canonical "Stephen Miller" (formal, first-name variant)
- Aliases: "Steve Miller", "Stephen G. Miller", "Senior Policy Advisor Stephen Miller"
- Result: All 4 entries appear under "Stephen Miller" actor page

### Example 2: Organizational Rebranding

**Entries:**
1. "Attorney General of the United States" (formal, 1 entry)
2. "Department of Justice" (informal, 3 entries)
3. "U.S. Department of Justice" (formal, 5 entries)
4. "DOJ" (abbreviation, 2 entries)

**Action:**
- Create alias: canonical "U.S. Department of Justice" (official full name)
- Aliases: "Department of Justice", "Attorney General of the United States", "DOJ"
- Result: All 11 entries appear under "U.S. Department of Justice" actor page

### Example 3: Person with Multiple Roles

**Entries:**
1. "Captain John Smith, NYPD" (2020, as police captain)
2. "Police Commissioner John Smith" (2024, after promotion)
3. "John Smith" (2026, quoted in unrelated context)

**Action:**
- Create alias: canonical "John Smith"
- Aliases: "Police Commissioner John Smith", "Captain John Smith, NYPD"
- Metadata: Entry 1 has `role: "Captain, NYPD"`, Entry 2 has `role: "Police Commissioner"`
- Result: All 3 entries under same actor page, but roles are displayed contextually
