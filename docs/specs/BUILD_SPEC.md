# The Standing: Build Spec

## Purpose

This document is the contract between the entry recording pipeline and the static-site build (`.eleventy.js`). It describes what the build expects from entries, episodes, and taxonomy files; what fields are validated and what happens on validation failure; and what the build derives automatically so authoring specs don't have to redefine these contracts each time.

The source of truth is `.eleventy.js` at the repo root. This spec describes its behavior in prose so other specs can reference it (`see BUILD_SPEC`) without restating the rules.

## Build invocation

```
npm install   # once per environment
npm run build # validates entries and renders /_site
```

Validation runs at build time and **throws on any violation** — there is no soft-fail mode. The `issue-to-entry` skill runs `npm run build` as Step 6 of its workflow; an entry that fails the build cannot be recorded.

## Entry validation

Entries live under `src/entries/YYYY/MM/DD/<slug>.md`. Each entry's YAML frontmatter is validated against the following rules.

### Required fields

- `id` — UUID v4 string. Required, unique across all entries. Format-validated. Generated at entry creation via `python3 -c "import uuid; print(uuid.uuid4())"` or `uuidgen`. **Never reuse, never change.**
- `headline` — non-empty string.
- `summary` — non-empty string.
- `date` — event date. Either a YAML date or a string in `YYYY-MM-DD` format.

### Validated enums

- `status` — when present, must be one of `draft`, `published`, `corrected`, `retracted`. Entries with `status: draft` are excluded from all collections (they don't appear in any page, feed, or backref calculation). `issue-to-entry` writes `published` unconditionally.
- `sources[].tier` — must be one of `primary`, `investigative`, `secondary`.

### Cross-reference validation

- `abuses[]` — every slug must exist in `taxonomy/abuses.yaml`. An unknown abuse fails the build with a pointer to fix.
- `episodes[]` — every slug must reference a file at `src/content/episodes/<slug>.md`. A reference to a non-existent episode fails the build.
- `relationships.follows[]`, `relationships.corrects[]`, `relationships.retracts[]` — every slug must point at an existing entry. Build-time validation prevents stale references after rename or deletion.

### Source-level validation

Each entry in `sources[]` requires `url`, `publisher`, and `tier`. Beyond that:

- **Sourcing floor:** every entry must have at least **1 primary source OR at least 2 investigative sources**. Falls below this floor → build fails.

### Quote constraint

If `quote.text` is present, it must be **fewer than 30 words**. Editorial standard. The build counts whitespace-separated tokens and throws on the boundary (≥30 fails).

### Uniqueness

- `id` — globally unique across all entries.
- `slug` — globally unique. Used as a foreign key by `relationships.*` and as a permalink component.

Duplicates of either fail the build with both filepaths in the error message.

## Episode validation

Episodes live at `src/content/episodes/<slug>.md`. Required:

- `title` — non-empty string.
- `start_date` — episode start date.
- **Body content** — the markdown body must be non-empty. An episode without an editorial overview is just a tag, which defeats the point.

(Episodes do not yet have an `id` field. When the episode workflow lands, episode `id`s should follow the same UUID v4 + uniqueness contract as entries. See TASKS.md → "Episodes editorial workflow.")

## Taxonomy validation

Loaded once at build start from `taxonomy/{ideals,abuses,aliases,sources}.yaml`:

- Every abuse in `abuses.yaml` must reference an `ideal` slug that exists in `ideals.yaml`. A dangling `ideal` reference fails the build before any entries are evaluated.

The taxonomy is *not* validated for completeness or coverage — only for internal consistency.

## What the build derives automatically

These derivations exist so specs don't need to assign or maintain them by hand:

- **Ideal pages from abuses.** Tagging an entry with an abuse automatically lands it on the parent ideal's page (`/ideals/<ideal-slug>/`). Editors never list ideals on entries — only abuses.
- **Actor normalization.** Actor strings on entries are normalized at build time via `taxonomy/aliases.yaml`. A raw `"President Donald J. Trump"` resolves to whatever canonical name the alias entry specifies. Strings with no alias match are slugified from the raw form.
- **Actor pages.** An actor whose entry count is **≥ 3** gets a generated actor page. Below the threshold, the actor appears on entries but has no dedicated page.
- **See-also relationships.** For each entry, the build computes up to 5 related entries scored by: shared abuses (+3 each), shared actors (+2 each), and temporal proximity (+2 within 30 days, +1 within 90, +0.5 within 180). Entries can override with `relationships.see-also-override` — when present, the override list is used verbatim and the score-based derivation is skipped.
- **Backrefs.** When entry A declares `relationships.follows: [b]`, the build records the reverse — entry B knows it has a follower. Same for `corrects` and `retracts`.
- **Feed entries.** `/feed.xml` includes the 30 most-recently-archived entries (sorted by `archived` field, falling back to `date`).

## Permalink shapes

Set by the templates, but worth noting:

- Entries: `/entries/YYYY/MM/DD/<slug>/` (date directories derived from `date` field).
- Ideal pages: `/ideals/<slug>/`.
- Abuse pages: `/ideals/<ideal-slug>/<abuse-slug>/`.
- Actor pages: `/actors/<actor-slug>/` (only when entry count ≥ 3).
- Episode pages: `/episodes/<slug>/`.

## What the build does NOT enforce

Documenting non-contracts is as useful as documenting contracts:

- **No URL liveness check.** The build does not fetch source URLs. URL verification is `issue-to-entry`'s Step 4 (at record time), not the build's job.
- **No content-hash check.** Source content drift is not detected at build time. See TASKS.md → "Source archive snapshot on entry recording" for the planned WayBack-based audit trail.
- **No taxonomy-fit judgment.** The build checks that abuse slugs *exist*; it does not check that they're the *right* abuses for the event. That's `ARCHIVE_FIT_SPEC`'s job.
- **No actor-spelling check.** A name typo'd identically on multiple entries normalizes to the typo, not to the correct spelling. `ACTOR_NORMALIZATION_SPEC` covers when to add an alias to fix this.
- **No editorial-style checks.** Headline neutrality, summary length, factual accuracy — all human-review concerns. The build only enforces the structural shape.

## How other specs reference this

Specs that produce or consume entries should defer to this document rather than re-stating fields. Examples:

- `ISSUE_TO_ENTRY_SPEC` Step 5 (Create Entry File) and Step 6 (Verify Build) — the field list and the build invocation.
- `EDITORIAL_WORKFLOW_SPEC` — what counts as a structurally valid entry.
- `ACTOR_NORMALIZATION_SPEC` — what the build actually does with `aliases.yaml`.
- `TAXONOMY_APPLICATION_SPEC` — the auto-derivation of ideals from abuses.

When the build changes, the change lands in `.eleventy.js` first, then in this spec. Other specs need no update unless the field contract changed.

## Related

- `.eleventy.js` — source of truth.
- `taxonomy/` — ideals, abuses, aliases, sources.
- `ISSUE_TO_ENTRY_SPEC.md` — the producer.
- `ARCHIVE_FIT_SPEC.md` — taxonomy-fit judgment (build does not duplicate).
