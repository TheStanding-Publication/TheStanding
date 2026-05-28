# The Standing: Editorial Workflow

## Purpose

This spec defines the **editor's role** in the archive pipeline. It does not describe the pipeline itself — that lives in [`PIPELINE.md`](../PIPELINE.md). What it covers is the editorial standards the archive holds entries to, and the touchpoints where a human decides whether an entry meets those standards.

The pipeline is largely automated up to the entry PR. By design, most inclusion judgment is owned by [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) and most recording mechanics by [`ISSUE_TO_ENTRY_SPEC`](./ISSUE_TO_ENTRY_SPEC.md). The editor's job is to apply judgment where automation can't — neutrality, framing, source diversity, the small calls at the edges.

## Key principle: broken windows

*No anti-democratic action is too small to record.* An entry is worthy of the archive if it credibly describes an abuse in The Standing's taxonomy and meets the sourcing standard. There is no significance threshold. The bar is **credible sourcing + relevant abuse**, not "important enough." Small accumulating breaches are themselves the pattern.

The corollary: an editor never rejects an entry because it feels minor. Reject for sourcing failure, mis-mapped abuse, or factual error. "Not significant enough" is not on the list.

## Where editors plug in

There are three places where a human makes a decision in the pipeline.

### 1. Tip verdict review (when archive-fit returns `archive-fit-merge` or `blocked-on-taxonomy`)

`standing-tip-vetter` runs `ARCHIVE_FIT_SPEC` and acts mechanically on most verdicts:

- `archive-fit` → promoted to `ready-for-entry` automatically.
- `not-fit` → closed automatically.
- `archive-fit-merge` → **held for editor.** The verdict comment names an existing entry that may already cover this event. Editor reviews; either merges the candidate's sources into the existing entry (commit directly, no separate PR needed for a sources-only update) or — if the candidate is actually a distinct event — re-opens the tip with a reasoning comment explaining why.
- `blocked-on-taxonomy` → **held for editor.** Archive-fit has opened a taxonomy PR proposing a new abuse. Editor reviews the PR. Merging it unblocks the tip, which becomes re-eligible on the next archive-fit pass. Closing the PR makes the tip `not-fit`.

### 2. Entry PR review (the main editorial gate)

This is where most editorial judgment happens. By the time an entry PR exists, the archive-fit verdict, the source verification, the taxonomy mapping, and the build validation have all run. The editor's job is to review **what automation can't catch**.

Read in this order:

1. **The archive-fit verdict comment on the linked issue.** That's the inclusion judgment, with the reasoning. Most of the time the editor accepts it; if they don't, the override goes in a reply comment on the issue so both arguments sit side by side.
2. **The PR's validation summary.** What corrections did `issue-to-entry` make in flight? Stale taxonomy slugs re-derived, normalized jurisdictions, actor lists pruned — all of these should be sanity-checked.
3. **The entry file itself.** Apply the standards in the next section.

Accept, request changes, or close. There is no "third reviewer" — the editor closes the loop.

### 3. Spotting fragmentation across recent entries

Not gated on any specific event. While reviewing, an editor may notice that the same actor is appearing under different names across multiple entries, or that several entries describe what should be a single named episode. Both are signals to act:

- Actor name fragmentation → add an alias per [`ACTOR_NORMALIZATION_SPEC`](./ACTOR_NORMALIZATION_SPEC.md).
- Episode candidates → see TASKS.md → "Episodes editorial workflow" for the planned cadence.

Until the planned weekly retrospective job lands, both are caught reactively in PR review.

## Editorial standards

These are the rubrics the editor applies at PR review (gate #2 above).

### Headline

- **Factual, not interpretive.** State what happened, not why it matters.
  - ✓ "Senator blocks subpoena compliance"
  - ✗ "Senator abuses power"
- **Neutral point of view.** Avoid loaded language.
  - ✓ "Campaign official sentenced for undisclosed lobbying"
  - ✗ "Corrupt official finally faces justice"
- **Specific.** What happened, not vague implications.
  - ✓ "Texas District Court strikes down voter ID requirement"
  - ✗ "Voting rules questioned"

### Summary

- **2–3 sentences.** Who, what, when, where, why (if relevant).
- **Cite specifics.** Named actors, roles, agencies, dates.
- **Neutral, factual tone.** No commentary or judgment.
- **Faithful to sources.** Do not extend beyond what the sources actually say.

### Abuse mapping

Apply [`TAXONOMY_APPLICATION_SPEC`](./TAXONOMY_APPLICATION_SPEC.md). Specifically:

- **Verify the definition fit.** Does the event match the abuse's `description` in `abuses.yaml`?
- **One primary abuse.** Whatever a reader would call the event in one phrase.
- **Secondary abuses sparingly.** Typical 1–3 abuses per entry; tag only when the definition independently applies.
- **No over-tagging.** Not every abuse is relevant just because the actor is powerful.
  - ✓ "Election official intimidated" → `election-worker-intimidation`
  - ✗ Adding `excessive-force-by-law-enforcement` to the same event unless police violence occurred.

### Actors

Apply [`ACTOR_NORMALIZATION_SPEC`](./ACTOR_NORMALIZATION_SPEC.md):

- The actor list contains entities that **took the action**, not context or targets.
- Roles/titles appear as parentheticals (`"Donald Trump (President)"`); the bare name resolves through `aliases.yaml`.
- Watch for fragmentation across recent entries; flag for the alias registry if it crosses the threshold.

### Jurisdiction and location

Required on every entry; format gated by the build (see [`BUILD_SPEC`](./BUILD_SPEC.md)). Editorial standard:

- **Federal** — location optional; "N/A" or "Nationwide" both acceptable.
- **State** — state name or two-letter abbreviation required.
- **Local** — city/county plus state required (`"Denver, Colorado"`, `"Maricopa County, Arizona"`).
- **International** — country required.
- **Private actor** — location required if the abuse is geographically bounded; optional if policy is nationwide.

Format: `City, State` or state alone (not the reverse). Full state name or two-letter abbreviation, either is fine.

### Sourcing

The build enforces the sourcing floor (1 primary OR 2 investigative). The editor confirms it's substantively met, not just structurally:

- Primary = official record, court filing, agency statement, primary-source document.
- Investigative = original reporting with sourcing, not aggregation or commentary.
- Two outlets repeating the same wire story do not count as two independent investigative sources.

### Quotation

Quoted material must be **fewer than 30 words** (the build will fail otherwise — see [`BUILD_SPEC`](./BUILD_SPEC.md)). Choose a tight, single-sentence quote that lands. If nothing under 30 words is tight enough, omit the quote rather than pad.

## PR review checklist

For each entry PR:

- [ ] Archive-fit verdict on the linked issue is `archive-fit` (or override is documented).
- [ ] Headline is factual and neutral.
- [ ] Summary is 2–3 sentences, accurate, faithful to sources.
- [ ] Event date is correct (`YYYY-MM-DD`).
- [ ] Jurisdiction is correctly identified; location meets the jurisdiction's requirements.
- [ ] Actors are named accurately, filtered to those who took the action, and roles/titles match the sources.
- [ ] Abuses are correctly mapped (verify against `taxonomy/abuses.yaml`); primary is appropriate.
- [ ] Sourcing floor met substantively — primary present, or two genuinely independent investigative sources.
- [ ] All URLs are live and content-verified (entry-recorder did this; spot-check the ones that mattered).
- [ ] No factual errors in summary or any in-PR commentary.
- [ ] Quote is fewer than 30 words.
- [ ] Broken-windows principle applied (recorded because credible + relevant, not because "significant").

## Anti-threshold-creep

The single test for inclusion: **is this a documented event that matches a defined abuse?**

- **Yes to both → record it.** Don't ask "is this significant?" or "is this part of a pattern?" Those are not on the rubric.
- **Maybe → consult the abuse definition** and re-apply the broken-windows principle. Lean inclusive.
- **No to either → don't record.** A documented event with no abuse fit is a taxonomy-gap signal (see [`TAXONOMY_APPLICATION_SPEC`](./TAXONOMY_APPLICATION_SPEC.md)); an alleged abuse with no documented event is not yet archive material.

Worked examples — things to **include** despite being small:

- Single instance of voter suppression (one polling place, one election).
- Single instance of press retaliation (one journalist detained).
- Single instance of election-worker intimidation (one official receives threats).
- Nepotism in one hire (even if others have merits).

Worked examples — things to **exclude**:

- Political disagreement without institutional abuse.
- Public figures criticizing each other (not retaliation unless using state power).
- General complaints without specific events.
- Allegations below the sourcing floor.

## Override and escalation

The editor can override archive-fit's verdict, but the override goes in writing on the same issue. This isn't ceremony — it preserves the reasoning chain for future cases that look similar.

Out-of-scope cases worth escalating to Bill or the editorial group:

- Abuse mapping is ambiguous after reading the definition twice.
- The event is political but the abuse vs. ordinary-politics line is unclear.
- The story might warrant a new abuse but archive-fit didn't propose one — possibly a doctrine question.

Day-to-day, the editor closes the loop independently.

## Related specs

- [`PIPELINE.md`](../PIPELINE.md) — the end-to-end system view; where editors fit in.
- [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) — owns the inclusion judgment editors review.
- [`ISSUE_TO_ENTRY_SPEC`](./ISSUE_TO_ENTRY_SPEC.md) — produces the PRs editors review.
- [`TAXONOMY_APPLICATION_SPEC`](./TAXONOMY_APPLICATION_SPEC.md) — abuse-mapping rules.
- [`ACTOR_NORMALIZATION_SPEC`](./ACTOR_NORMALIZATION_SPEC.md) — actor naming and aliases.
- [`BUILD_SPEC`](./BUILD_SPEC.md) — what the build enforces structurally.
