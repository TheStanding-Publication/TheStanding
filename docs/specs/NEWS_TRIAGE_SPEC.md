# The Standing: News Triage

## Purpose
A fast, headline-level scan of a single day's news, compared against The Standing's 12 ideals, to surface candidate anti-democratic events and file each as a lightweight "tip" issue. Triage is the **cheap discovery layer** of the monitoring pipeline: it finds stories quickly and at scale — above all for backfilling the historical backlog — without paying the cost of full event research. The research happens later, in the vetting step.

## Where this sits in the pipeline

```
NEWS_TRIAGE     → tip
ARCHIVE_FIT     → archive-fit | archive-fit-merge | not-fit | blocked-on-taxonomy
NEWS_RESEARCH   → ready-for-entry   (on archive-fit verdict, the tip-to-issue skill promotes; scheduled-scan and url-to-issue modes file directly after their own archive-fit pass)
ISSUE_TO_ENTRY  → entry recorded    (issue closed by the entry PR)
```

Triage produces `tip` issues and nothing else. It never produces a `ready-for-entry` issue, and a tip is never sent straight to entry recording — every tip passes through [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) and then research before becoming entry-eligible.

## Key principle: speed over depth
Triage deliberately does little per story. It reads **headlines, not articles**. It maps to the **12 broad ideals, not the 77 specific abuses**. It does a **cursory** duplicate check, not an exhaustive one. It writes a **thin tip**, not a researched issue. Every instinct to "just check one more thing" belongs in the vetting step, not here. The job is breadth and throughput — catch candidates, move on.

## Relationship to ARCHIVE_FIT
Triage is intentionally calibrated to a **lower bar** than the canonical
inclusion judgment in [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md).
Triage's job is to surface candidates cheaply; archive-fit's job is to
gate them rigorously at vetting (mission → ideal → abuse → archive
dedup). The asymmetry is deliberate: a false positive at triage costs
one archive-fit pass, while a false negative is a story lost from the
archive. Do **not** import archive-fit's strict criteria here — the
headline-only, plausibility-based check below is the right tool for
this step. Archive-fit will reject what doesn't fit downstream.

## How this skill is used
Triage is **ledger-driven** and processes **exactly one day per run**. It is invoked by a scheduled task and/or on-demand by an operator. Because each run's state lives in a coverage ledger (below), runs need no memory of one another and a missed run is self-healing — the next run simply picks up the same next-oldest day.

## Modes and inputs
Triage has one job, so there are no modes — only one optional input:

- `target_date` — the day to triage. If the operator supplies it, triage that date. If omitted, triage derives it from the coverage ledger: the day immediately before the earliest date already covered (triage marches **backward** through the backlog).

## The coverage ledger
Triage's job is the historical **backlog** — current news is already covered by the four NEWS_RESEARCH scheduled scans — so triage marches backward in time. To do that without gaps or repeats it maintains a **coverage ledger**: a single pinned GitHub issue, **#77 — "[Triage] Coverage ledger"**, whose body records the span of dates triage has covered.

- **At the start of every run,** read issue #77.
- **Determine the target date:** the operator-supplied `target_date` if given; otherwise the day before the earliest covered date.
- **If the ledger is uninitialized** (no dates recorded yet), triage cannot derive a date — it requires an operator-supplied `target_date`, and that run seeds the ledger.
- **At the end of every run,** update issue #77 to include the date just triaged.
- **Record the date whether or not it produced any tips.** A triaged-but-empty day must be marked covered, or it will be re-triaged forever. This is exactly why the tips themselves cannot serve as the coverage record — an empty day produces no tips.

Keep the ledger body tidy. The agent owns its exact shape; the recommended form is a contiguous span (`Earliest covered` / `Latest covered`) plus any ad-hoc dates done outside that span.

## Workflow

### Step 1: Load the taxonomy
Fetch the current versions at the start of every run — do **not** work from memory:

- **Ideals:** https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/ideals.yaml — the 12 ideals, each with a title and description. Triage classifies headlines against these, not against the abuses.
- **Sources:** https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/sources.yaml — the curated outlet list. Triage scans the same outlets the deep monitor trusts; this keeps a consistent quality bar across both processes.

### Step 2: Determine the target date
Read the coverage ledger (issue #77). The target date is the operator-supplied date, or — if none was given — the day before the earliest covered date. If the ledger is uninitialized and no date was supplied, stop and ask the operator for a starting date; do not guess one.

### Step 3: Scan that day's headlines
For the target date, gather **headlines** (and one-line standfirsts where visible) from the curated `sources.yaml` outlets. Do **not** fetch article bodies.

- For a recent date, an outlet's RSS feed or homepage may still carry that day's items.
- For an older date — the common backlog case — RSS will not reach back. Use **date-scoped search** per outlet: a `site:` filter plus a date window around the target day. DuckDuckGo's HTML interface handles these filters reliably in headless contexts; iterate one `site:` per outlet rather than one broad query, and confirm each result actually falls on the target date.
- This is the one step where triage spends real effort. Keep it bounded: collect headlines, do not chase articles.

### Step 4: Evaluate each headline against the 12 ideals
For each headline, ask: *does this plausibly describe an abuse of power touching one of the 12 ideals?* Use semantic judgment.

- The bar is deliberately **low** — "plausibly relevant" is enough. Triage catches candidates; the vetting step confirms them. A false positive costs one vetting pass; a false negative is a story lost from the archive.
- Do **not** map to specific abuse slugs and do **not** assess significance. Headline text cannot support either, and attempting it is precisely the bog-down triage exists to avoid.
- Record which ideal(s) the headline might touch — one or more of the 12, by slug.
- A headline plainly not about US governance, democracy, or an abuse of power is simply skipped — silently, no tip.

### Step 5: Cursory duplicate check
Before filing a tip, do a quick check that the event is not already in the pipeline. The dedup space spans the whole pipeline: open `tip` issues, `[Monitoring]` issues (open or closed), and published entries under `src/entries/`.

- This is a **cursory** check — a search on the obvious terms (actors, event, date), not an investigation.
- If a clear duplicate exists, skip it — do not file. If it is genuinely unclear, file the tip and note the possible duplicate in it; the vetting step runs the thorough duplicate handling.

### Step 6: File a tip issue
For each surviving candidate, create a GitHub issue using the template below. Apply the **`tip`** label. Do **not** apply `ready-for-entry` — a tip is not ready for entry recording, and the entry-recorder must not pick it up.

**One tip per distinct event.** Headlines are usually 1:1 with events, so this rule rarely fires at triage — but if a single headline or standfirst plainly references two distinct events (different dates, locations, actors, or acts), file a separate tip per event. Do not collapse them into one tip just because they appeared in the same headline. The archive tracks events, not topics; downstream archive-fit and research workflows assume one event per issue.

### Step 7: Update the coverage ledger
Update issue #77 to record the target date as covered — whether or not the day produced any tips.

### Step 8: Report the run
Return a summary: date triaged, headlines scanned, candidates evaluated, tips filed (with issue numbers), duplicates skipped, and the updated coverage span.

## Tip issue template

```
Title: [Tip] [Brief headline]

Body:
## News Triage Tip

**Source:** [Outlet]
**URL:** [Source URL]
**Surfaced from:** headlines of [YYYY-MM-DD] (the triaged day)
**Candidate ideals:** [ideal-slug, ideal-slug]

### Headline
[The headline, and the one-line standfirst if there was one — nothing more.]

---
*Filed by The Standing's news-triage scan (triaged date: [YYYY-MM-DD]). This is an unvetted lead — it needs an archive-fit verdict and tip-to-issue research before it can become an entry.*
```

A tip carries a headline, a URL, a date, and candidate ideals — **nothing verified**. It deliberately has no actors, no abuse slugs, no event-date research, no corroboration. Those are the vetting step's job.

## Scheduled task (thin wrapper)
Triage is invoked by a scheduled task that defers entirely to this spec:

```
You are The Standing's automated news-triage system.

Fetch and execute the workflow defined in:
https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/NEWS_TRIAGE_SPEC.md

This is the canonical operational spec. Follow it exactly.

No target date is supplied — derive it from the coverage ledger and march
the backlog backward, one day per run.
```

The scheduled task supplies **no** date — triage marches the backlog from the ledger. The cadence (how often the task fires) is a deployment choice; it should run during off-peak hours, consistent with the other scheduled jobs. An operator can also invoke triage directly with an explicit `target_date` to fill a specific gap or re-run a day.

## Key principles

1. **Speed over depth** — headlines not articles, ideals not abuses, cursory not exhaustive. Throughput is the point.
2. **Ledger-driven** — the coverage ledger (issue #77) is the single source of truth for what has been triaged; every run reads it and updates it.
3.
3. **One day per run** — bounded, predictable, self-healing.
4. **Tips are leads, not records** — thin by design, never `ready-for-entry`, always vetted before entry recording.
5. **Low bar — caught, not confirmed** — a false positive costs a vetting pass; a false negative loses a story. Lean toward filing.
6. **Mark every triaged day** — covered means covered, tips or no tips.

## Downstream contract (vet-tip mode of NEWS_RESEARCH)
A `tip` issue is a lead. The vetting step — NEWS_RESEARCH in vet-tip mode — takes a tip, performs full event research, rewrites it into a complete monitoring issue, and transitions the tag `tip` → `ready-for-entry`; or, if the tip does not pan out, closes it (which keeps it in the dedup set so the same story is not re-tipped). Triage should be reasonably good but it does not need to be perfect — some tips will be rejected at vetting, and that is the system working as designed.
