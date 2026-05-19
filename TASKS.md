# Tasks

## Active

- [x] ~~**External sourcing workflow**~~ - Public tip/submission process that feeds into GitHub issues (2026-05-18)
  - All tips become GitHub issues (working in public philosophy)
  - General public + journalists as audience
  - Channels: email (tips@thestanding.us) + GitHub issues
  - [x] ~~**Submission process page**~~ - Live at /submit/ with footer link
  - [x] ~~**Review/update GitHub issue template**~~ - Already in place

- [x] ~~**Internal sourcing workflow**~~ - Automated news monitoring (2026-05-18)
  - Single skill: docs/skills/STANDING_MONITOR_SKILL.md (single point of truth)
  - 4x daily scans: 8am, 12pm, 4pm, 8pm (all reference same skill)
  - Monitors: NYT, WaPo, NPR, AP, Reuters, BBC
  - Comprehensive research upfront: event date, actors, jurisdiction, evidence, mapped abuses
  - Duplicate detection: checks open/closed issues before creating
  - Auto-creates GitHub issues with full event information
  - Labels: monitoring-intake, needs-research, [abuse slug]

- [x] ~~**Entry recording workflow**~~ - Automated checks + PR creation (2026-05-18)
  - Single skill: docs/skills/ENTRY_RECORDING_SKILL.md
  - URL validation (live + content integrity via hashing)
  - Actors validation (verified against sources, normalized if in actors.yaml)
  - Location validation (required per jurisdiction)
  - Taxonomy validation (abuses must be valid)
  - Slug format: `issue-{#}-{jurisdiction}-{abuse}` (designed)

## Waiting On

- [x] ~~**Editorial workflow**~~ - Define review/approval process and anti-threshold-creep guidelines (2026-05-18)
  - For monitoring-intake: human review at PR stage only
  - For tips: human review at issue stage AND PR stage
  - Location field integrated throughout
  - Approval checklists provided
  - Broken-windows principle documented

- [x] ~~**Update workflows for location field**~~ - All downstream processes must handle location (2026-05-18)
  - ✓ Integrated into Editorial workflow (location validation required)
  - ✓ Integrated into Daily digest/newsletter (displayed for each entry)
  - TODO: Archive pages (location searchable/filterable — build-time feature, future enhancement)

- [x] ~~**Taxonomy application**~~ - Create guidelines for mapping entries to ideals/abuses, handle ambiguous cases (2026-05-18)
  - Decision trees for common scenarios provided
  - Guidance on handling ambiguity and avoiding over-tagging
  - Auto-derivation rules documented

- [x] ~~**Daily digest/newsletter workflow**~~ - Define assembly and send process for Buttondown newsletter (2026-05-18)
  - Buttondown API integration documented
  - Entry formatting template provided
  - Location field integrated into newsletter display
  - Scheduling (6 AM ET daily) defined
  - Fallback behavior for no-entry days included

- [x] ~~**Actor normalization**~~ - Define when actors.yaml aliases should be consolidated (2026-05-18)
  - Trigger defined: ≥3 entries with name variation
  - Canonical name selection rules provided
  - Special cases documented (name changes, mergers, international names)
  - Audit process (monthly) defined
  - Build system integration documented

## Someday

- [ ] **State-level collections / archive pages** — Per-state browse pages (e.g. `/states/TN/`) listing all entries whose `jurisdiction` is `state` or `local` and whose `location` resolves to that state. Mirrors the existing `/ideals/{slug}/` pattern.
  - **Trigger:** revisit when any single state has ≥10 entries, OR when total state-level entries across the archive reach ≥50 — whichever comes first. (These are placeholders; tighten when we have a feel for the data.)
  - Requires deriving state from the `location` string, or adding an explicit normalized `state` field to entry frontmatter
  - Open question: stop at state level, or also county/city collection pages?

## Done
