# The Standing: Archive Fit

## Purpose

Render a verdict on whether a candidate story belongs in The Standing's
archive. Given either a GitHub issue number or a URL, evaluate the story
against the project's mission, the live taxonomy of ideals and abuses, and
the existing archive — then emit a verdict as a label and an explanatory
comment on the issue.

This is the **single canonical inclusion judgment** for The Standing. It
replaces the in-scope check, abuse-mapping critique, and duplicate
handling that previously lived inside `NEWS_RESEARCH_SPEC` for the
operator-driven modes (`vet-tip` and `url-to-issue`). Those workflows now
delegate to this spec for the fit judgment and act mechanically on the
resulting label.

## Key Principle: Mission, Then Taxonomy, Then Archive

The verdict is built up in a fixed order, and a failure at any earlier
stage short-circuits the later ones:

1. **Mission test** — does this story describe a US event involving
   anti-democratic behavior, abuse of power, or corruption that has
   actually happened (or is imminent)?
2. **Ideal match** — does the event violate at least one of the 12
   democratic ideals in `taxonomy/ideals.yaml`?
3. **Abuse match** — does at least one abuse in `taxonomy/abuses.yaml`
   cleanly describe the violation, per `TAXONOMY_APPLICATION_SPEC`?
4. **Archive duplicate check** — is there an existing entry for the
   **same event** (same date, same location, same actors, same act)?

The order matters. A story that fails the mission test never reaches the
taxonomy. A story that fails the ideal match never reaches the abuse
search. A story with no fitting abuse triggers the taxonomy-gap path
before any archive comparison runs.

## Modes and Inputs

This skill supports two input modes. Internally they share Steps 2–6;
they differ only in how the candidate story is acquired (Step 1).

### Issue mode (default)

Invoked when the operator provides a GitHub issue number. The issue
already exists in `TheStanding-Publication/TheStanding` and carries some
combination of `tip`, `monitoring-intake`, or `needs-research` labels.

- `mode` — `issue`
- `issue_number` — the open issue to evaluate

### URL mode

Invoked when the operator provides a URL with no existing issue. The
skill fetches the URL, extracts the candidate event, and renders a
verdict without creating any issue. If the verdict is `archive-fit`,
the operator's next step is `url-to-issue` (which creates the monitoring
issue mechanically).

- `mode` — `url`
- `source_url` — a single URL on the open web

URL mode produces a **chat verdict only** — no GitHub mutations. Once the
operator records the URL as an issue via `url-to-issue`, that issue is
eligible for issue-mode evaluation.

### Multiple distinct events in a single input

Both modes assume the candidate is **one event**. If the input bundles
more than one distinct event (different date, location, actors, or
specific act), the skill renders **one verdict per event**, not a single
verdict over the bundle:

- **Issue mode:** if the existing issue body conflates two events,
  surface the conflation in the verdict comment, render the verdict for
  the primary event on the existing issue, and recommend that the
  operator open a separate issue per additional event (which will then
  flow through archive-fit independently). Do not silently average the
  verdicts.
- **URL mode:** enumerate the events found in the URL in the chat
  verdict and render an archive-fit verdict for each. Each `archive-fit`
  event becomes its own monitoring issue via `url-to-issue`, mirroring
  the one-issue-per-event rule in `NEWS_RESEARCH_SPEC` Step 6.

Event identity here is the same as in Step 5 (event-level dedup): two
incidents that share a topic or an actor are still two events if any of
date, location, or specific act differs.

## Workflow

### Step 1: Load the candidate story and the live taxonomy

Fetch the taxonomy fresh on every run — never work from memory:

- `https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/ideals.yaml`
  — the 12 democratic ideals.
- `https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/taxonomy/abuses.yaml`
  — every abuse slug currently in the archive.

Load the candidate story:

- **Issue mode:** fetch the issue body, title, and existing labels. If the
  issue already references one or more `abuse-slug:` lines in its
  Mapped abuses section, capture them as the **claimed** abuses — the
  verdict will validate or correct them.
- **URL mode:** fetch the URL with a browser-style User-Agent. If the
  fetch tooling refuses the domain outright (tooling-level block, not a
  paywall), do not attempt to work around it; report the block to the
  operator and stop. If the URL paywalls or fails to resolve, retry once,
  then report and stop. Do not reconstruct the story from search
  snippets.

### Step 2: Mission test

Ask: **is this a US event involving anti-democratic behavior, abuse of
power, or corruption that has actually happened or is imminent?**

The Standing's mission, as recorded in the project: a non-partisan,
documentary archive of US anti-democratic and corruption events, applying
broken-windows doctrine (small breaches go in the record). Mission
failures include — without being limited to — the following:

- **Out of scope:** non-US events, partisan disagreement that does not
  rise to an abuse, civil-society activity, ordinary politics, opinion
  journalism without an underlying event.
- **Not actually happening:** proposals, hypotheticals, contingent
  futures, "could happen" framing. See the actually-happening threshold
  ([[feedback-actually-happening-threshold]]) — archive events that have
  occurred or are imminent; refuse proposals and contingent stories.
- **Allegation without action:** a lawsuit filing whose abusive
  character depends on motive evidence only the plaintiff has produced
  is not yet an abuse (see [[feedback-lawsuit-filings-not-abuses]]). The
  underlying action might be — judge the action, not the filing.

If the story fails the mission test, the verdict is **`not-fit`**. Skip
to Step 6. Do not attempt taxonomy mapping for a story that does not
belong in the archive on mission grounds — the abuse list is not a hook
to drag in out-of-scope events.

### Step 3: Ideal match

For stories that pass the mission test, ask: **which of the 12 ideals in
`ideals.yaml` does this event violate?**

Use the `short_description` field for each ideal as the canonical test,
not the slug. A story may legitimately touch more than one ideal — record
all that apply, but in priority order. The primary ideal is the one whose
violation is the central act of the story.

If no ideal applies, that is a stronger signal than a missing abuse: the
story is probably a mission failure that slipped through Step 2. Return
to Step 2, restate why the story seemed in-scope, and either:

- Reclassify as `not-fit` with reasoning, or
- Surface the case to the operator as a mission-edge story that may
  warrant a doctrine update (do not invent ideals in the verdict).

### Step 4: Abuse match

For each ideal identified in Step 3, ask: **which abuse(s) in
`abuses.yaml` filed under that ideal cleanly describes what happened?**

Apply `TAXONOMY_APPLICATION_SPEC` rigorously:

- Match the event to the abuse **definition**, not to a vague keyword.
- Tag the specific abuse, not the actor's general behavior.
- Use secondary abuses sparingly; typical entry has 1–3.
- Do not invent slugs. Every slug in the verdict must already exist in
  the loaded `abuses.yaml`.

Three possible outcomes:

- **Clean match.** One or more existing abuses describe the event under
  the matched ideal. Record them and proceed to Step 5.
- **Approximate match with stretch.** The closest existing abuse is
  related but does not cleanly fit the definition. Treat as a
  taxonomy-gap candidate (next bullet) rather than papering over with
  the wrong slug — note the closest existing abuse for the operator.
- **Taxonomy gap.** The story matches an ideal but no existing abuse
  fits its definition. **This is not a failure — it is a signal the
  taxonomy itself needs a new entry.** Verdict becomes
  **`blocked-on-taxonomy`**; see Step 5 for the PR-creation contract.

If the issue arrived with claimed abuse slugs (from upstream research)
that no longer fit, surface the mismatch in the verdict comment and
record the corrected slugs.

### Step 5: Archive duplicate check (event-level, strict)

Search `src/entries/` for entries describing the **same event** — same
date, same location, same actors, same act. Use the candidate story's
event date as the primary index; check the YYYY/MM/DD directory and
adjacent days.

**Event identity is strict.** Two stories that share a topic, an actor,
or a kind of abuse are not duplicates if any of date, location, or
specific act differs. The Standing is an archive of events, not of
topics. Examples:

- Two voter-intimidation incidents on different days in different
  counties → **two entries**, not one.
- A press-freedom case in March and another in April involving the same
  agency → **two entries**.
- An IG firing on a given date, separately reported by three outlets
  → **one entry** with all three as sources.

Three possible outcomes:

- **No duplicate.** Proceed to Step 6 with verdict `archive-fit`.
- **Same event, already archived.** Verdict is **`archive-fit-merge`**.
  The comment names the existing entry path (`src/entries/YYYY/MM/DD/<slug>.md`)
  and recommends merging the candidate's sources into the existing entry
  rather than creating a new one. The operator decides whether to merge.
- **Related but distinct event.** Note the precedent in the verdict
  comment as context, but issue `archive-fit`. Related entries are
  archival strength, not a reason to refuse.

### Step 6: Emit the verdict

The verdict is one of four labels, applied to the issue along with an
explanatory comment. In URL mode, the verdict is emitted to chat only —
no labels, no comment, no mutations.

#### Labels

- **`archive-fit`** — passes mission, has at least one ideal and one
  cleanly-fitting existing abuse, no same-event duplicate. Ready to
  proceed through the recording pipeline. (Note: this label is a fit
  verdict only; promotion to `ready-for-entry` is the responsibility of
  the recording skill, not this one.)
- **`archive-fit-merge`** — passes mission, taxonomy, and a same-event
  archive entry exists. Operator decides whether to merge sources into
  the existing entry or file as new.
- **`not-fit`** — fails the mission test. Comment explains which
  threshold failed.
- **`blocked-on-taxonomy`** — passes mission and ideal match, but no
  existing abuse fits cleanly. Comment links the taxonomy PR opened in
  the next step.

These labels are mutually exclusive on a given issue. If the issue
previously carried any of them from an earlier evaluation, clear the
prior label before applying the new one.

#### Comment template

```
## Archive-fit verdict: <label>

**Mission:** <pass | fail — reason>
**Primary ideal:** <ideal-slug> — <one-line reasoning>
**Mapped abuses:** <abuse-slug-1>, <abuse-slug-2> (or "none — taxonomy gap")
**Archive search:** <no same-event match | merge candidate at src/entries/.../slug.md | related precedent at src/entries/.../slug.md>

### Reasoning
<2–4 sentences on why this verdict — what the act was, why the ideal
applies, why the abuse(s) fit (or do not), and any caveats.>

### Operator next step
<one of: "Run url-to-issue / let the entry recorder pick this up." |
"Review the merge candidate and decide." | "Out of scope — close the
issue." | "Taxonomy PR opened at #NN; merge it before re-evaluating.">

---
*Verdict by archive-fit (spec: docs/specs/ARCHIVE_FIT_SPEC.md).*
```

#### Taxonomy-gap branch (verdict = `blocked-on-taxonomy`)

When the verdict is `blocked-on-taxonomy`, do all of the following before
posting the comment:

1. Draft a new abuse entry for `taxonomy/abuses.yaml`. The draft must
   include `slug`, `ideal` (the matching ideal from Step 3), `title`,
   and `description`. Slug is kebab-case and globally unique among
   existing abuses. The description follows the style of existing
   entries — one sentence, definitional, not example-driven.
2. Open a PR against `main` with that single-file change to
   `taxonomy/abuses.yaml`. PR title:
   `taxonomy: add abuse "<title>" under <ideal-slug>`. PR body links
   back to the source issue and quotes the relevant excerpt from the
   candidate story justifying the new abuse.
3. In the verdict comment on the source issue, link the PR number and
   apply the `blocked-on-taxonomy` label. The source issue stays open
   until either the PR merges (re-run the fit check; expect a clean
   `archive-fit` once the new slug exists) or the operator closes the
   PR (the source issue's verdict becomes `not-fit` with reasoning, or
   the operator names a closest existing slug to use).

Do not edit `abuses.yaml` directly on `main`. The PR is the audit trail
and gives the operator a single review surface for taxonomy additions.

### Step 7: Report the run

Return a short summary to the conversation:

- Input mode and identifier (issue number or URL)
- Verdict label
- Primary ideal and abuse mapping
- Any archive precedents found (with paths)
- If `blocked-on-taxonomy`: the PR number and the proposed new slug

## Output Contract

A successful archive-fit run produces:

- **Issue mode:** exactly one of `archive-fit` / `archive-fit-merge` /
  `not-fit` / `blocked-on-taxonomy` on the issue, plus one verdict
  comment. For `blocked-on-taxonomy`, also a PR against
  `taxonomy/abuses.yaml`. No other labels, title changes, body
  rewrites, or pipeline-status mutations (the recording skill owns
  `ready-for-entry`).
- **URL mode:** a chat verdict only, with the same four-way label
  vocabulary used in the reasoning. No GitHub mutations.

What this spec **does not do**:

- Promote tips to `ready-for-entry` — that is `tip-to-issue`'s job after
  this spec returns `archive-fit`.
- Create monitoring issues from URLs — that is `url-to-issue`'s job
  after this spec returns `archive-fit` on a URL.
- Record entries — that is `issue-to-entry`'s job.
- Close issues — operator decision, even on `not-fit` (a `not-fit`
  verdict is editorial; closure is operational).

## Key Principles

1. **Single canonical fit judgment.** All operator-driven inclusion
   decisions flow through this spec. Drift between specs has historically
   caused contradictory verdicts on the same story.
2. **Mission first.** Taxonomy is a downstream filter, not a hook. An
   in-scope event without an abuse is a taxonomy gap; an out-of-scope
   event with an abuse-shaped headline is still not-fit.
3. **Taxonomy is a living artifact.** A gap is a real signal — fix it
   via PR rather than papering over with the closest-fit slug. Stretched
   slugs poison the archive's analytical value.
4. **Event-level deduplication.** The archive tracks events, not topics.
   Two similar but distinct events get two entries.
5. **No silent mutation.** Every verdict is accompanied by a comment
   explaining the reasoning. The operator can disagree and override; the
   reasoning makes that disagreement productive.
6. **Read the spec, not memory.** Scheduled tasks and skills fetch this
   spec from `main` on every run. Changes here propagate to all callers.

## Validation Responsibility

This spec is the **inclusion judgment**. Field-level validity of an
issue (sources still load, taxonomy slugs still exist at process time,
actor names normalize) is the downstream `ISSUE_TO_ENTRY_SPEC`'s
responsibility. Some friction at the recording step is expected and
healthy — articles get retracted, the taxonomy evolves, headlines drift.

Specifically:

- **Do** call the taxonomy gap when no existing abuse fits cleanly. The
  abuse list grows by design.
- **Do** flag near-precedents in the verdict comment even when the
  verdict is plain `archive-fit` — precedent context strengthens the
  archive.
- **Don't** invent abuse slugs to avoid the gap path.
- **Don't** treat a `not-fit` verdict as final. The operator can
  override by re-running with an explicit reasoning override; the spec
  re-evaluates and the verdict comment captures the override rationale.

## How This Spec Is Used

This document is the operational source of truth. It is fetched and
executed by:

- The **`archive-fit`** skill (operator-invocable).
- The **`tip-to-issue`** skill, which now runs archive-fit as its first
  step and acts mechanically on the verdict (promote on `archive-fit`,
  hold on `blocked-on-taxonomy`, close with reasoning on `not-fit`,
  surface merge candidate on `archive-fit-merge`).
- The **`url-to-issue`** skill, which runs archive-fit in URL mode
  before any issue creation. Only `archive-fit` URLs are recorded as
  monitoring issues; the other verdicts produce operator messages.
- The **`standing-tip-vetter`** scheduled task, which drives archive-fit
  across open `tip` issues hourly.

Each caller is a thin wrapper. Changes to this file propagate to all of
them on next invocation.

## Scheduled Task Integration

`standing-tip-vetter` (hourly :15, 1pm–3am local) becomes the scheduled
driver for archive-fit in issue mode. Its prompt is updated to:

```
You are The Standing's archive-fit evaluator.

Fetch and execute the workflow defined in:
https://raw.githubusercontent.com/TheStanding-Publication/TheStanding/main/docs/specs/ARCHIVE_FIT_SPEC.md

Run it in issue mode against every open issue labeled `tip` that does
not already carry one of `archive-fit`, `archive-fit-merge`, `not-fit`,
or `blocked-on-taxonomy`. Skip issues authored by anyone other than the
`thestanding` bot, and skip issues with the `invalid` label.

The spec is the canonical operational source. Follow it exactly.
```

The task prompt stays under ~15 lines. Behavior changes land here, not
in the task prompt — that is the lesson of historical drift between
specs and scheduled-task wrappers.

## Labels Reference

New labels introduced by this spec (operator should pre-create them in
the repo's label set):

- `archive-fit` — passes inclusion judgment.
- `archive-fit-merge` — same-event duplicate found; merge candidate.
- `not-fit` — fails mission test.
- `blocked-on-taxonomy` — passes mission and ideal, no existing abuse.

These are **verdict labels**, distinct from pipeline-status labels
(`tip`, `ready-for-entry`, `invalid`, `needs-human-review`, `watching`). A given issue can
carry one verdict label and one pipeline-status label simultaneously
without contradiction.
