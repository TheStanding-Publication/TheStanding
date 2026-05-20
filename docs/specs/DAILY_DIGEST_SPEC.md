# The Standing: Daily Digest & Newsletter Skill

## Purpose
Assemble approved entries from the previous 24 hours into a daily newsletter and publish via Buttondown. This skill handles the final distribution to subscribers.

---

## Overview

**What:** Daily newsletter containing all entries published to the archive that day
**When:** Once per day (default: 6:00 AM ET)
**Where:** Buttondown (buttondown.email)
**Audience:** Email subscribers
**Update cadence:** Daily, every day including weekends (The Standing publishes entries daily, publishes digest daily)

---

## Input Data

### Source of Entries
**Query:** All entries with `status: published` AND `archived: [TODAY]` (where TODAY = today's date)

These come from:
1. **Approved monitoring-intake PRs** merged to main (overnight or early morning)
2. **Approved tip PRs** merged to main
3. **Any manually-published entries** added directly

### Entry Fields Used
For each entry, extract:
- `headline` — One-line factual headline
- `summary` — 2-3 sentence summary
- `date` — Event date (YYYY-MM-DD)
- `archived` — Archive date (today)
- `location` — City/County/State or location string
- `jurisdiction` — federal/state/local/international/private-actor
- `actors` — List of named actors/organizations
- `abuses` — List of abuse slugs
- `slug` — URL-stable entry identifier
- `sources` — URLs with titles (primary source highlighted)
- `confidence` — monitoring/preliminary/well-reported/primary-source

---

## Workflow

### 1. Fetch Today's Entries (6:00 AM ET)

**Process:**
- Query GitHub repo for all entries with:
  - Status: `published`
  - Archived date: Today (2026-05-18 if running on May 18)
- Sort by event date (earliest first)
- Count total entries

**Output:**
- List of entry objects with all fields above

### 2. Format Entries for Newsletter

**For each entry, create a newsletter item:**

```
## [HEADLINE]

**Event:** [DATE]
**Location:** [LOCATION]
**Jurisdiction:** [JURISDICTION]

[SUMMARY — 2-3 sentences]

**People & Organizations:**
[List of actors with roles if available]

**Classified under:**
[List of abuses with friendly names: voter-suppression → Voter Suppression]

**Read the full entry:** [Link to entry on archive]
**Primary source:** [Title of primary source](URL)
```

**Formatting rules:**
- **Headline:** Use entry's headline as-is (already vetted as factual/neutral)
- **Event date:** Format as "May 18, 2026" (human readable)
- **Location:** Use location field as-is (e.g., "Denver, Colorado" or "Federal")
- **Jurisdiction:** Show friendly name (federal → Federal, CO → Colorado, etc.)
- **Summary:** Use entry's summary as-is (already vetted)
- **Actors:** List in order provided in entry, with roles if available
- **Abuses:** Map slug to friendly title (voter-suppression → "Voter Suppression"); list all abuses tagged
- **Archive link:** Construct as `https://thestanding.us/entries/[slug]/`
- **Primary source:** Find first source with `tier: primary`, display title and URL

### 3. Assemble Newsletter

**Newsletter structure:**

```
# The Standing — Daily Brief
[DATE: May 18, 2026]

[EDITORIAL NOTE — optional, if provided]

---

[ENTRY 1]

---

[ENTRY 2]

---

[ENTRY 3]

---

## Archive Stats

**Today's entries:** [COUNT]
**This month:** [RUNNING TOTAL]
**Total archived:** [ALL-TIME TOTAL]

[Optional: "View the full archive" link to site]

---

[Footer: unsubscribe link, contact info, etc. — handled by Buttondown]
```

**Editorial note (optional):**
- If notable pattern across today's entries, include 1-2 sentence editor's note at top
- Example: "Today's entries show escalation in pressure on election officials across multiple states. See [link]."
- Only include if genuinely relevant; don't force it

### 4. Publish to Buttondown

**Process:**
1. Draft email in Buttondown via REST API
2. Include all entries and summary
3. Schedule send for 6:00 AM ET (or publish immediately if running in evening)
4. Include metadata:
   - Subject: "The Standing — [Day], [Date]" (e.g., "The Standing — Tuesday, May 18")
   - Preview text: "[COUNT] entries archived today"
   - Tags: "daily-digest", "[DATE]"
5. Publish/send

**API:** Buttondown REST API
- Endpoint: `POST /api/v1/emails`
- Required fields: subject, body, publish_date, scheduled_for
- Optional: preview_text, tags

### 5. Post-Publish Actions

**After newsletter is sent:**
1. Log publish date/time and entry count
2. Update running monthly/annual totals (for next day's stats)
3. Archive sent email link in git repo (optional but recommended for audit trail)
4. Report to user (optional): "[N] entries in today's brief, sent to [subscriber count] subscribers"

---

## Data Mapping Reference

### Abuse Slug → Friendly Name
(Use for displaying abuses in newsletter)

```
voter-suppression → Voter Suppression
gerrymandering → Gerrymandering
election-denial → Election Denial
election-worker-intimidation → Election Worker Intimidation
disinformation-campaigns → Disinformation Campaigns
post-election-overturning-attempts → Post-Election Overturning Attempts
refusal-to-concede → Refusal to Concede
defying-court-orders → Defying Court Orders
selective-prosecution → Selective Prosecution
pardons-for-allies-or-self → Pardons for Allies or Self
politicized-investigations → Politicized Investigations
ignoring-statutory-requirements → Ignoring Statutory Requirements
selective-non-enforcement → Selective Non-Enforcement
executive-overreach → Executive Overreach
bypassing-congress → Bypassing Congress
defying-subpoenas → Defying Subpoenas
weaponizing-DOJ → Weaponizing DOJ
IG-firings → Inspector General Firings
watchdog-defunding → Watchdog Defunding
obstruction-of-OIG-investigations → Obstruction of OIG Investigations
retaliation-against-whistleblowers → Retaliation Against Whistleblowers
attacks-on-judicial-independence → Attacks on Judicial Independence
lying-to-congress → Lying to Congress
press-retaliation → Press Retaliation
prosecution-of-journalists → Prosecution of Journalists
expulsion-from-public-proceedings → Expulsion from Public Proceedings
access-restrictions-for-critical-outlets → Access Restrictions for Critical Outlets
legal-threats-against-publishers → Legal Threats Against Publishers
FCC-or-licensing-as-leverage → FCC or Licensing as Leverage
protester-surveillance → Protester Surveillance
prosecution-of-protected-speech → Prosecution of Protected Speech
viewpoint-based-permit-denials → Viewpoint-Based Permit Denials
targeting-critics-with-government-power → Targeting Critics with Government Power
blacklisting → Blacklisting
self-dealing → Self-Dealing
bribery → Bribery
undisclosed-financial-conflicts → Undisclosed Financial Conflicts
nepotism → Nepotism
emoluments-violations → Emoluments Violations
pay-to-play → Pay to Play
monetizing-office → Monetizing Office
procurement-irregularities → Procurement Irregularities
politicization-of-uniformed-services → Politicization of Uniformed Services
domestic-deployment-overreach → Domestic Deployment Overreach
pardons-for-uniformed-misconduct → Pardons for Uniformed Misconduct
retaliation-against-officers-following-law → Retaliation Against Officers Following Law
```

### Jurisdiction → Friendly Name
```
federal → Federal
state:CA → California
state:CO → Colorado
[etc. — use full state name]
local:Denver:CO → Denver, Colorado
local:[City]:[State] → [City], [State]
international:[Country] → [Country]
private-actor → Private Actor (Multi-State Policy)
```

### Confidence Level → Friendly Name
```
monitoring → Automated Monitoring
preliminary → Preliminary Report
well-reported → Well Reported
primary-source → Primary Source
```

---

## Location Field in Newsletter

**Display rule:** Include location for all jurisdictions except federal (unless location is specific and noteworthy)

**Examples:**

**State-level entry:**
- Location: "Colorado"
- Display: "Location: Colorado"

**Local-level entry:**
- Location: "Denver, Colorado"
- Display: "Location: Denver, Colorado"

**Federal entry:**
- Location: "N/A" or "Nationwide"
- Display: [Don't show location, or show "Nationwide" if relevant]

**Private actor entry:**
- Location: "Nationwide" (if policy spans multiple states)
- Display: "Location: Nationwide Impact"

---

## Scheduling & Automation

### Scheduled Task
- **Task ID:** standing-daily-digest
- **Schedule:** Daily at 6:00 AM ET
- **Cron:** `0 6 * * *` (6am every day)
- **Timezone:** America/New_York (Eastern Time)

### Fallback Behavior
**If no entries published today:**
- Still send digest with message: "No entries archived today. Check back tomorrow or [view recent entries](link)."
- This maintains subscriber engagement and reminds them the archive exists

**If Buttondown API fails:**
- Log error and retry within 1 hour
- Notify via email or dashboard that digest send failed
- Do NOT discard entries — manual send may be needed

---

## Newsletter Template Example

```
# The Standing — Daily Brief

**Friday, May 18, 2026**

---

## Election Official Faces Threats After Certifying Results

**Event:** May 17, 2026
**Location:** Colorado
**Jurisdiction:** State

A Colorado county election director reported receiving threats and intimidation after certifying election results in the face of public pressure from losing candidates. Law enforcement is investigating the threats.

**People & Organizations:**
- [County Clerk Name] (County Clerk)
- [County Name] Board of Elections

**Classified under:**
- Election Worker Intimidation
- Voter Suppression (related)

**Read the full entry:** https://thestanding.us/entries/issue-15-co-election-worker-intimidation/
**Primary source:** [Court Filing Title](https://...county-court-filing...)

---

## Federal Judge Rules Executive Order Exceeds Authority

**Event:** May 18, 2026
**Location:** Federal
**Jurisdiction:** Federal

A federal district court ruled that an executive order signed by the President exceeded constitutional authority and violated separation of powers doctrine. The court ordered the government to cease enforcement.

**People & Organizations:**
- The President
- U.S. District Court (Southern District of New York)
- [Agency affected]

**Classified under:**
- Executive Overreach
- Separation of Powers Violation

**Read the full entry:** https://thestanding.us/entries/issue-42-federal-executive-overreach/
**Primary source:** [Court Order Title](https://...federal-court-filing...)

---

## Archive Stats

**Today's entries:** 2
**This week:** 12
**May so far:** 31
**Total archived:** 287

[View the full archive →](https://thestanding.us/)

---

Unsubscribe | Manage preferences | Contact
```

---

## Content Guidelines for Newsletter

**Tone:** Factual, straightforward, informative
- Neutral point of view (entries are already vetted for this)
- No commentary or interpretation beyond what sources state
- No ranking by severity

**Length:** Brief but complete
- Summary is key; readers can click for full entry and sources
- Headline + summary + actors/abuses + source = ~150-200 words per entry

**No editorializing:** Let the archive entries speak for themselves
- Exception: Optional opening note if there's a clear pattern (see Editorial Note section above)
- Exception: Facts about archive stats (count, volume)

---

## Metrics & Reporting (Future)

**Track and report:**
- Subscriber count (from Buttondown)
- Open rate (from Buttondown)
- Click-through rate (from Buttondown)
- Average entries per day
- Trending abuses/ideals (entries per category per month)

(These are tracked in Buttondown; this skill exports/reports them if needed)

---

## Workflow Integration

**Input:** Approved entries published to main branch
**Output:** Daily email to subscribers
**Frequency:** Once per day at 6:00 AM ET
**Automation:** GitHub Action or Cowork scheduled task

**Triggers:**
- Manually: `npm run digest [DATE]` to build for specific date
- Automatically: Daily at 6:00 AM ET

**Related skills:**
- ENTRY_RECORDING_SPEC.md — Creates entries that feed into digest
- EDITORIAL_WORKFLOW_SPEC.md — Approves entries before they're available for digest
- PROJECT_PLAN.md → Buttondown section — Newsletter platform details

---

## Buttondown API Reference

**REST API Base:** https://api.buttondown.email/v1/

**Create Draft:**
```json
POST /emails
{
  "subject": "The Standing — Tuesday, May 18",
  "body": "[Full newsletter markdown]",
  "preview_text": "2 entries archived today",
  "publish_date": "2026-05-18",
  "scheduled_for": "2026-05-18T10:00:00Z"
}
```

**Publish Draft:**
```json
POST /emails/{draft_id}/publish
{}
```

**Buttondown Documentation:** https://docs.buttondown.email/

---

## TODO / Future Enhancements

1. **Archive link integration:** Ensure entry URLs are stable and use `/entries/[slug]/` format
2. **Subscriber segmentation:** Allow subscribers to filter by jurisdiction/ideal (future feature)
3. **RSS feed:** Buttondown auto-generates RSS from published emails; ensure we expose it
4. **Social sharing:** Add social preview text per entry (auto-generated from summary)
5. **Archive stats:** Build running stats (monthly/annual) from git history
