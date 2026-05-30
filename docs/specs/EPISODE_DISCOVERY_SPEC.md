# The Standing: Episode Discovery

## Purpose

Find the **episodes** hiding in the archive: groups of already-recorded entries that
are facets of one compound real-world happening — a protest with arrests and press
retaliation and surveillance, an election day with intimidation across precincts, a
hearing where several officials lied, a wave of copycat state actions after one ruling.

This spec defines a **distinct, on-demand discovery process** that reads the registered
entries in `src/entries/` and produces a **list of recommendations**: new episodes worth
creating, and existing episodes that newly-arrived entries should be linked to.

It is deliberately **not** a step inside entry recording, issue-to-entry, or PR review.
Episode discovery is its own pass that an editor runs when they want it, looking across
the whole archive at once rather than judging episodes one entry at a time. Grouping
decisions made with a wide view are better than grouping decisions bolted onto the
recording of a single entry.

---

## Where this sits in the pipeline

```
monitoring → tip → issue → entry (recorded in src/entries/)
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │  EPISODE DISCOVERY      │  ← this spec (on demand)
                          │  read-only scan         │
                          │  → recommendation list  │
                          └────────────────────────┘
                                      │
                                      ▼
                    editor reviews, then (separately, by hand)
                    creates episode file + adds episodes: links
```

Discovery sits **downstream of entry recording** and is decoupled from it. It runs against
the entries that already exist. Acting on its recommendations — writing the episode file,
editing entries — is a separate editorial step described under "What the editor does next."

---

## Invocation

On-demand only. The editor runs a discovery pass when they want one (for example after a
burst of related entries lands, or periodically as a housekeeping sweep). There is no
scheduled task and no automatic trigger; nothing creates or links episodes as a side
effect of another process.

Typical prompts: "run episode discovery", "are there episodes hiding in the archive",
"should any recent entries be grouped into an episode".

Optional scope argument — discovery may be narrowed to a window or a subset, e.g.
"episode discovery over the last 60 days" or "...over entries tagged `partisan-gerrymandering`".
Default scope is the entire archive.

---

## What counts as an episode

An episode is a **named compound happening that contains two or more entries**. The test
is whether a reader would understand the entries as parts of one larger real-world event,
not merely as topically similar.

Qualifies:
- Multiple distinct abuses occurring as part of a single event (one protest → an arrest
  entry, a press-credential-revocation entry, a surveillance entry).
- The same kind of event repeated across places as one identifiable wave with a common
  origin (post-*Callais* state gerrymanders; a coordinated multi-state purge).
- A single proceeding generating several entries (a hearing where multiple officials
  separately cross a line).

Does **not** qualify:
- Two entries that merely share an actor or an abuse tag but are unrelated happenings.
  (Two unrelated Trump entries are not an episode.)
- A single entry, however significant. Episodes are compound by definition; one entry is
  just an entry.
- Hypothetical or threatened groupings ("if these bills pass they'll form a pattern").
  Apply the **actually-happening threshold** — the compound event must have occurred or be
  imminent, not be a forecast.

---

## Grouping signal: semantic judgment, evidenced

The grouping decision is a **semantic judgment**, not a mechanical rule. The agent reads the
candidate entries and decides whether they are facets of one happening. Structured fields
are used as **evidence that focuses attention**, not as the decision itself:

- **Shared actors** — overlapping names in `actors:` across entries.
- **Temporal proximity** — `date:` values clustered in a window (same day, same week, or a
  longer arc for a slow-rolling wave).
- **Shared abuse / jurisdiction / location** — overlapping `abuses:`, `jurisdiction:`, or
  `location:`.

Use these to surface candidate clusters cheaply, then read the entries' `headline:` and
`summary:` and make the call. A strong structured overlap with no real-world connection is
not an episode; a real connection with weak structured overlap (different actors, spread
over months) still is, if the entries are genuinely one happening. The narrative judgment
wins.

Every recommendation must carry a one-to-three-sentence rationale stating the real-world
happening that ties the entries together. If you cannot state it crisply, it is not an
episode.

---

## Workflow

### Step 1: Sync main, then load the archive

First, make sure the working copy reflects the published archive — discovery is only as
good as the entries it can see, and recently-merged entries are often the whole reason to
run it:

```bash
git checkout main
git pull origin main
```

This is a read-only sync; discovery makes no commits of its own. If the working tree has
uncommitted local changes that block the pull, stop and surface that to the editor rather
than stashing or discarding — discovery should never run against an ambiguous tree.

Then read all entries under `src/entries/**/*.md` whose `status:` is not `draft` — matching
how the build's `entriesByEpisode` collection filters (`status !== "draft"`). For each,
retain: `id`, `slug`, file path, `date`, `headline`, `summary`, `actors`,
`abuses`, `jurisdiction`, `location`, and the current `episodes:` list.

Load existing episodes from `src/content/episodes/*.md`: their `slug`, `title`,
`start_date`, `end_date`, and overview. These are the episodes a new entry might join.

### Step 2: Cluster on structured signals (cheap pass)

Group entries that share actors and/or fall in a common date window and/or share abuse,
jurisdiction, or location. This is a coarse filter to produce candidate clusters — over-
inclusion here is fine; Step 3 prunes.

Also, for every existing episode, gather published entries that fit its window/subject but
do **not** currently list it in `episodes:` — these are retroactive-link candidates.

### Step 3: Judge each cluster (semantic pass)

For each candidate cluster, read the entries and decide:
- Is this one compound real-world happening? (Apply "What counts as an episode" and the
  actually-happening threshold.)
- If yes, is it a **new episode**, or do these entries belong to an **existing episode**?
- Which specific entries are members? (Drop entries that merely co-occur but aren't part of
  the happening.)

Discard clusters that are only topical similarity. Require ≥2 member entries for a new
episode.

### Step 4: Assemble recommendations

Produce a ranked list (highest-confidence / most-complete episodes first). Two kinds:

**A. New episode** — propose:
- a stable `slug` (kebab-case, URL-safe, descriptive; e.g. `post-callais-state-gerrymanders`)
- a display `title`
- `start_date` (earliest member `date`) and `end_date` (latest, or omit if ongoing)
- a draft editorial overview (2–4 sentences: what the compound event was, its scale and
  context) the editor can refine
- the member entries, each shown as `slug` + `id` + `date` + `headline`
- the rationale (the real-world tie) and a confidence note

**B. Link to existing episode** — propose:
- the existing episode `slug` + `title`
- the entries to add (each `slug` + `id` + `date` + `headline`)
- the rationale

### Step 5: Present the list

Output the recommendations directly to the editor (in chat / the run report). Discovery
**stops here**. It does not create episode files and does not edit entries.

---

## Output format

```markdown
# Episode Discovery — <date>, scope: <whole archive | window>

Scanned <N> published entries, <M> existing episodes.
<K> recommendations.

## New episodes

### 1. Post-Callais state gerrymanders  (confidence: high)
- slug: `post-callais-state-gerrymanders`
- dates: 2026-03-12 → ongoing
- Why: After *Louisiana v. Callais* loosened the constraint, multiple states redrew
  congressional maps along the same partisan playbook within weeks. These entries are
  facets of one coordinated wave, not isolated state stories.
- Members:
  - `issue-6-tennessee-...` (b4f8…) 2026-03-12 — "Tennessee legislature redraws…"
  - `issue-19-louisiana-...` (9a2c…) 2026-03-28 — "Louisiana adopts…"
  - `issue-24-missouri-...` (1d77…) 2026-04-04 — "Missouri map…"
- Draft overview: <2–4 sentences>

## Links to existing episodes

### A. Add to "June 2026 ICE Raids" (`june-2026-ice-raids`)
- `issue-31-portland-...` (4c10…) 2026-06-09 — "Portland facility…"
- Why: same operation, same week, named in DHS's own release alongside the others.

## Considered and rejected
- Entries X and Y share actor "Donald Trump" but are unrelated events (pardons vs.
  tariff order) — not an episode.
```

The "Considered and rejected" section is encouraged for near-misses, so the editor sees
the judgment calls and the pass is auditable.

---

## What the editor does next (separate from discovery)

Discovery hands the editor a list. Acting on it is a deliberate, separate step — by hand
today, or a future dedicated promote-skill — never folded back into discovery:

1. **Create the episode file** at `src/content/episodes/<slug>.md` with required
   frontmatter (`id`, `title`, `start_date`, optional `end_date`, optional `slug`) and a
   required editorial overview body. See the schema below.
2. **Link the entries** by adding the episode `slug` to each member entry's `episodes:`
   list.
3. **Build** (`npm run build`) — the build validates that every `episodes:` reference
   resolves to an existing episode file, that episode `id`s are well-formed and unique, and
   that the overview body is non-empty.
4. **PR** as normal editorial review.

---

## Episode file schema (target of recommendations)

An episode is a Markdown file at `src/content/episodes/<slug>.md`:

```yaml
---
id: <UUID v4>          # stable, globally unique; generate with `uuidgen` or
                       # python3 -c "import uuid; print(uuid.uuid4())"
slug: post-callais-state-gerrymanders   # URL-stable, immutable after first reference
                                         # (defaults to filename if omitted)
title: "Post-Callais State Gerrymanders"
start_date: 2026-03-12
end_date: 2026-04-04    # optional; omit while ongoing
---

Required editorial overview body — what the compound event was, its scale, context, and
timeline. An episode without an overview is just a tag and the build rejects it.
```

**Episode `id` (UUID v4).** Episodes carry a stable `id` exactly as entries do, separate
from the slug: the slug is for URLs and display, the `id` is the canonical identifier.
This was deferred when there were zero episodes; it lands with the first episode. The build
must enforce `id` presence, UUID-v4 format, and global uniqueness for episodes, mirroring
the entry-id validation already in `.eleventy.js`. (Cross-references between entries and
episodes stay **slug-based** — that decision stands; the `id` is the canonical key, not the
foreign key in `episodes:` lists.)

**URL stability.** Episode slugs are immutable after first publish, like entry and ideal
URLs. If a slug must ever change, the old URL becomes a permanent redirect.

---

## Key principles

- **Distinct and on-demand.** Episode discovery is its own process. Nothing else creates or
  proposes episodes as a side effect. Entry recording and issue-to-entry leave
  `episodes: []` and move on; the "any related episodes?" reviewer prompt in those specs is
  a courtesy pointer to run discovery, not a place where grouping is decided.
- **Read-only.** A discovery pass never writes an episode file, never edits an entry, and
  makes no commits. Its only git interaction is the read-only sync of `main` in Step 1; its
  only output is a recommendation list. This is what keeps it from becoming a side effect.
- **Recommend, don't decide.** The editor confirms every episode. Discovery proposes slugs,
  titles, dates, and a draft overview to make confirmation fast, but creating the file and
  adding links is the editor's deliberate act.
- **Semantic judgment over mechanical rules.** Structured fields focus attention; the
  narrative tie decides. Every recommendation states that tie in plain language.
- **Actually-happening threshold.** Group events that have occurred or are imminent. No
  hypothetical or forecast episodes.
- **Two or more, genuinely connected.** One entry is not an episode; coincidental overlap is
  not an episode.

---

## Worked example: post-Callais state gerrymanders

The archive's first obvious episode. After *Louisiana v. Callais*, several states redrew
congressional maps along the same partisan lines within weeks. Each is recorded as its own
entry (the Tennessee redraw, issue #6, is one node). Individually they read as separate
state stories; together they are one coordinated wave.

A discovery pass clusters them on shared abuse (`partisan-gerrymandering`), federal/state
jurisdiction, and a tight date window, reads the entries, and recognizes the common origin.
It recommends a **new episode** `post-callais-state-gerrymanders` listing every state entry
as a member, with a draft overview explaining the *Callais* trigger and the wave. As later
state entries arrive, a