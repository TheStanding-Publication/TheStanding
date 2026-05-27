# The Standing: Taxonomy Application Skill

## Purpose
Guide editors and automated systems on how to map documented events to the correct abuses within The Standing's taxonomy. This ensures consistent, accurate categorization across the archive.

## The Taxonomy Structure

The Standing's taxonomy has two levels:

**Level 1: Democratic Ideals (12 total)**
- Free and fair elections
- Rule of law and equal application
- Separation of powers and independent oversight
- Free press
- Freedom of speech, assembly, and association
- Public service over self-dealing
- Civilian control of armed and uniformed services
- Due process and fair trials
- Transparent governance
- Constitutional limits on executive power
- Non-interference in elections (domestic and foreign)
- Protection of vulnerable populations

**Level 2: Abuses (77 total)**
Each ideal has multiple specific abuses. For example, "Free and fair elections" includes:
- voter-suppression
- gerrymandering
- election-denial
- election-worker-intimidation
- disinformation-campaigns
- (and more)

**Key rule:** When you tag an entry with an abuse, **the parent ideal is auto-derived at archive build time.** You only need to list abuse slugs — the ideal pages and entry-to-ideal relationships are handled automatically.

---

## How to Apply the Taxonomy

### Step 1: Understand the Event
Read the entry's headline, summary, and sources carefully. **What specifically happened?**

- WHO did it? (Actor name, title, agency)
- WHAT did they do? (Specific action)
- WHEN? (Date)
- WHERE? (Location, jurisdiction)
- HOW does it violate democratic norms? (Which ideal(s)?)

### Step 2: Identify the Primary Abuse
**Ask: What specific abuse definition does this event match?**

Refer to `/taxonomy/abuses.yaml` and read the definition for candidate abuses. Match the event to the abuse definition, not to a vague keyword.

**Examples:**

**Event:** "State election official certifies results despite losing candidate's public pressure campaign."
- Candidate abuses: election-denial, voter-suppression, election-worker-intimidation
- **Primary abuse:** election-worker-intimidation (the official faced pressure/intimidation)
- Why not election-denial? The official didn't deny the election; they resisted denial.

**Event:** "Federal court rules executive order exceeded constitutional authority."
- Candidate abuses: executive-overreach, separation-of-powers-violation
- **Primary abuse:** executive-overreach (executive acted beyond authority)
- Why not ambiguous? The abuse definition explicitly covers acting beyond constitutional limits.

**Event:** "Police use force against protesters during legal assembly; 5 people injured."
- Candidate abuses: excessive-force-by-law-enforcement, freedom-of-assembly-restriction
- **Primary abuse:** excessive-force-by-law-enforcement (force was the abuse)
- Why not freedom-of-assembly? The restriction came through force, not through permit denial or legal barrier.

### Step 3: Check for Secondary Abuses
**Ask: Does this event also clearly violate other ideals?**

Use secondary abuses sparingly. Typical entry has 1-3 abuses. Avoid tagging just because it's "related" — tag only if the abuse definition clearly applies.

**Examples of appropriate secondary tags:**

**Event:** "President fires inspector general who was investigating the president's agency; DOJ then launches investigation of the fired IG for alleged crimes."
- Primary: retaliation-against-whistleblowers
- Secondary: weaponizing-DOJ (DOJ launching politically-motivated investigation)
- Tertiary: IG-firings (if appropriate under separation-of-powers ideal)
- Why? All three abuses are clearly at play.

**Event:** "State passes law requiring voter ID; research shows impact is 3x higher on minority voters."
- Primary: voter-suppression
- Secondary: NOT discrimination-of-protected-class (unless law explicitly targets by race)
- Why? The data shows impact but the law doesn't explicitly discriminate. Voter-suppression is sufficient.

### Step 4: Avoid Common Over-Tagging Mistakes

**Mistake 1: Tagging the actor, not the abuse.**
- ✗ "A politician lied in a speech" tagged as `selective-prosecution` (because we associate the actor with abuse)
- ✓ "A politician lied in court testimony, obstructing investigation" tagged as `obstruction-of-OIG-investigations`
- Why? Tag the specific abuse, not the actor's general bad behavior.

**Mistake 2: Tagging political disagreement.**
- ✗ "Senator votes against regulation" tagged as `executive-overreach`
- ✓ Only if the event describes an abuse (executive exceeded authority, not legislative disagreement)

**Mistake 3: Confusing correlation with abuse.**
- ✗ "Event occurs in state where abuse happens, so tag it" (location ≠ causal abuse)
- ✓ Tag only if the event itself describes abuse.

**Mistake 4: Over-specificity.**
- ✗ "This is both voter-suppression AND election-denial" (when only one applies)
- ✓ Identify the primary abuse and include secondary only if both clearly apply.

**Mistake 5: Missing the real abuse by focusing on the symptoms.**
- ✗ Event: "State legislature passes law that happens to impact minorities; tagged as discrimination-of-protected-class"
- ✓ Event: "State legislature passes law that explicitly targets voters by race or felony history; tagged as voter-suppression + potential discrimination" (if law is explicit)
- Why? Impact without intent or explicit targeting is noted in sources; the abuse classification is about the law itself.

---

## Decision Trees for Common Scenarios

### Election-Related Events

**Event involves voters not being able to vote:**
- Is access blocked by law, administrative action, or polling place closure? → `voter-suppression`
- Are election workers being pressured/intimidated? → `election-worker-intimidation`
- Is someone denying election results? → `election-denial`
- Are election workers not certifying? → `certification-refusal`

**Event involves election integrity:**
- Is someone spreading false claims about election? → `election-denial` + `disinformation-campaigns`
- Are districts redrawn for political advantage? → `gerrymandering`
- Are voting machines or procedures undermined? → `election-integrity-sabotage` (if exists)

### Law Enforcement / Protest Events

**Event involves police and protesters:**
- Did police use force? → `excessive-force-by-law-enforcement`
- Did police arrest protesters for lawful speech? → `prosecution-of-protected-speech`
- Did police require permits unreasonably? → `viewpoint-based-permit-denials` (if permit was denied for viewpoint)
- Did police or government surveil protesters? → `protester-surveillance`

### Press / Speech Events

**Event involves journalists:**
- Was journalist arrested/prosecuted for journalism? → `prosecution-of-journalists`
- Did government retaliate against press outlet? → `press-retaliation`
- Did government restrict press access? → `expulsion-from-public-proceedings`
- Did government threaten publisher? → `legal-threats-against-publishers`

**Event involves speech restrictions:**
- Was speech prosecuted? → `prosecution-of-protected-speech`
- Was speech targeted by government? → `targeting-critics-with-government-power`
- Was speech restricted by permit denial? → `viewpoint-based-permit-denials`

### Government Accountability Events

**Event involves oversight/investigation:**
- Did official refuse to comply with investigation? → `defying-subpoenas`
- Did official fire watchdog/IG? → `IG-firings`
- Did official block investigation? → `obstruction-of-OIG-investigations`
- Did official retaliate against person reporting wrongdoing? → `retaliation-against-whistleblowers`

**Event involves executive power:**
- Did executive act beyond authority? → `executive-overreach`
- Did executive bypass legislature? → `bypassing-congress`
- Did executive defy court order? → `defying-court-orders`
- Did executive improperly pardon? → `pardons-for-allies-or-self`

### Corruption / Self-Dealing Events

**Event involves financial benefit to official:**
- Did official benefit from conflict of interest? → `undisclosed-financial-conflicts`
- Did official family get job/contract? → `nepotism`
- Did official use office for personal enrichment? → `self-dealing` + `monetizing-office`
- Did official accept bribe? → `bribery`
- Did official use executive power to help business associate? → `pay-to-play` + `self-dealing`

---

## Guidelines for Handling Ambiguity

### When the Event Could Fit Multiple Abuses

**Approach:**
1. Read each candidate abuse definition in `/taxonomy/abuses.yaml`
2. Ask: "Which abuse is the CORE of what happened?"
3. Tag the core abuse as primary
4. Tag 1-2 secondary abuses only if they're equally clear

**Example:** Official threatens journalist to stop investigating corruption.
- Candidate abuses: `press-retaliation`, `targeting-critics-with-government-power`
- Primary: `press-retaliation` (the abuse is retaliation against press)
- Secondary: `targeting-critics-with-government-power` (also fits, but press-specific abuse is more precise)

### When the Event Doesn't Fit an Abuse Exactly

**Decision:** Don't force-fit. If it doesn't match the defined abuse, it may not be an entry.

**Example:** "Mayor proposes budget that would reduce park funding"
- Does this match any abuse? No. It's governance disagreement, not abuse.
- Don't create entry.

**Example:** "Police use non-lethal force against protesters during unlawful assembly"
- Is this `excessive-force`? Only if force was disproportionate to threat.
- If lawful assembly → likely excessive-force
- If unlawful assembly → may not be excessive-force; depends on context.

### When You're Unsure

**Consult:**
1. Read the ideal's explainer page (if exists)
2. Look at similar entries already in the archive and see how they're tagged
3. Ask: "Would future readers expect to find this under [ideal name]?"
4. If still unsure, err toward the narrower, more defensible abuse
5. Add a note in the entry for editorial review

---

## Auto-Derivation Rules

**You do NOT manually assign ideals.** The build process automatically derives them from abuses.

**Example:**
If you tag an entry with `voter-suppression`, the build system:
1. Looks up `voter-suppression` in `/taxonomy/abuses.yaml`
2. Finds its parent ideal: "Free and fair elections"
3. Auto-adds this entry to the ideal's page and entry list

**This means:**
- One abuse → one ideal
- Multiple abuses → entry appears on multiple ideal pages
- No extra work needed from you

---

## Taxonomy Maintenance (Editorial)

### When to Create a New Abuse

**Do NOT create new abuses lightly.** The taxonomy is designed to be stable.

**Only create new abuse if:**
1. An event clearly describes institutional abuse
2. That abuse doesn't fit existing definitions
3. You expect future similar events (not one-off)

### Two ways a new abuse gets proposed

**Automatic (story-driven):** When [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md)
evaluates a candidate story that matches one of the 12 ideals but no
existing abuse fits cleanly, archive-fit opens a PR against
`taxonomy/abuses.yaml` proposing the new abuse and applies
`blocked-on-taxonomy` to the source issue. This is the default path —
most new abuses originate from a real story that exposed the gap. The
operator reviews the PR; merging it unblocks the source issue, which
re-evaluates cleanly on the next archive-fit run.

**Manual (editor-driven):** When an editor notices a gap unrelated to a
specific in-flight story — reviewing the taxonomy, comparing against
external frameworks, or anticipating future events — the steps below
still apply. Manual additions are rarer in practice but remain
supported.

**Manual process:**
1. Propose new abuse to Bill (via GitHub issue in taxonomy)
2. Define it clearly
3. Assign to appropriate ideal
4. Generate slug (kebab-case)
5. Add to `/taxonomy/abuses.yaml`
6. Submit PR for team review

### Avoiding Abuse Sprawl

**Principle:** Reuse existing abuses. New abuses only when necessary.

**Example:**
- "Official improperly fires agency official" → `IG-firings` or `retaliation-against-whistleblowers` (don't create `improper-firing`)
- "Judge rules against defendant without hearing" → `due-process-violation` (don't create `denial-of-hearing`)

---

## Confidence Levels and Abuse Mapping

**Confidence level** (monitoring, preliminary, well-reported, primary-source) refers to **source quality**, not abuse clarity.

**Abuse mapping confidence** is separate:
- If sources are clear and abuse is obvious → "well-reported" or "primary-source"
- If sources are clear but abuse definition is fuzzy → note in editorial review
- If sources are developing and abuse is unclear → "developing" confidence level

---

## Common Abuse Slugs Reference

**Elections:** voter-suppression, election-denial, election-worker-intimidation, gerrymandering, certification-refusal

**Law enforcement:** excessive-force-by-law-enforcement, protester-surveillance, prosecution-of-protected-speech

**Press:** press-retaliation, prosecution-of-journalists, expulsion-from-public-proceedings, legal-threats-against-publishers

**Oversight:** defying-subpoenas, IG-firings, obstruction-of-OIG-investigations, retaliation-against-whistleblowers

**Executive power:** executive-overreach, bypassing-congress, defying-court-orders, weaponizing-DOJ

**Corruption:** nepotism, self-dealing, bribery, undisclosed-financial-conflicts, pay-to-pla