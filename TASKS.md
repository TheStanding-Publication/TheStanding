# Tasks

## Active

- [x] ~~**External sourcing workflow**~~ - Public tip/submission process that feeds into GitHub issues (2026-05-18)
  - All tips become GitHub issues (working in public philosophy)
  - General public + journalists as audience
  - Channels: email (tips@thestanding.us) + GitHub issues
  - [x] ~~**Submission process page**~~ - Live at /submit/ with footer link
  - [x] ~~**Review/update GitHub issue template**~~ - Already in place

- [x] ~~**Internal sourcing workflow**~~ - Automated news monitoring (2026-05-18)
  - Single skill: docs/specs/STANDING_MONITOR_SPEC.md (single point of truth)
  - 4x daily scans: 8am, 12pm, 4pm, 8pm (all reference same skill)
  - Monitors: NYT, WaPo, NPR, AP, Reuters, BBC
  - Comprehensive research upfront: event date, actors, jurisdiction, evidence, mapped abuses
  - Duplicate detection: checks open/closed issues before creating
  - Auto-creates GitHub issues with full event information
  - Labels: monitoring-intake, needs-research, [abuse slug]

- [x] ~~**Entry recording workflow**~~ - Automated checks + PR creation (2026-05-18)
  - Single skill: docs/specs/ISSUE_TO_ENTRY_SPEC.md (originally ENTRY_RECORDING_SPEC; the latter was retired 2026-05-28)
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

- [x] ~~**URL-to-issue mode for STANDING_MONITOR_SPEC**~~ — Operator provides a single URL; agent fetches it, searches for supporting coverage, and produces the same intake as a scheduled scan. Documented in STANDING_MONITOR_SPEC.md alongside the scheduled-scan mode. Refuses with reasoning when out of scope; surfaces duplicates to the operator rather than auto-appending. Chat-first invocation. (Implemented.)

- [ ] **Manual-issue-research mode for STANDING_MONITOR_SPEC** — `--issue N` to research an existing GitHub issue (e.g. a human-submitted tip not produced by the monitor itself) and enrich it with comprehensive intake. Less urgent than `--url` because the existing chat workflow can handle tip-issues directly when they come in.
  - Open question: edit issue body in place, or post research as a comment? (Probably comment, to preserve the original.)

- [ ] **Phone / off-desktop submission path** — Submit a URL from a phone or anywhere off the Cowork desktop, and have the workflow run on the desktop's next opportunity. Two candidate designs:
  - **Email intake** to `tips@thestanding.us` — a scheduled task polls the inbox and processes URLs from new emails.
  - **Tip-issue conversion** — submitter files a GitHub issue with a `tip` label via the mobile GitHub app; a scheduled task watches for `tip`-labeled issues and runs the URL workflow against them.
  - Open question: which one fits the editorial flow better? Tip-issue is self-archiving (public timestamp + audit trail); email is faster to submit but disappears from the public record. Likely the tip-issue path wins.

- [ ] **Re-evaluation workflow for already-published entries** — Periodically re-scan the source URLs of recently-published entries to catch retractions, corrections, or substantive updates that arrive after publication. Surfaces the unused `corrected` and `retracted` status values, plus the `relationships.retracts:` and `corrections:` fields.
  - Trigger: probably weekly, against entries published in the last 90 days
  - Source retracted → entry gets `status: retracted`; populate `relationships.retracts:`
  - Source substantively corrected → entry gets `status: corrected`; append an item to `corrections:` with date + note
  - Decisions needed: lookback window, what counts as a "substantive" correction, whether the agent acts unilaterally or only proposes via PR

- [ ] **Retire or rationalize legacy GitHub labels** — Several labels exist in the repo but no longer serve a purpose after the eligibility-by-author and validate-and-correct refactors.
  - `url-validation-hold` — fully dead after PR #20 (the 24h-recheck loop was removed). Delete from the repo.
  - `monitoring-intake` — still applied by STANDING_MONITOR but no skill filters on it anymore (PR #16 switched to author-based eligibility). Keep for human grouping in the GitHub UI, or stop applying?
  - `needs-research` — same situation. Decide and act.

- [ ] **STANDING_MONITOR pre-flight taxonomy validation** — Today the monitor "should" only emit abuse slugs that exist in `taxonomy/abuses.yaml` (per PR #20 guidance), but nothing enforces it — issues #6–#13 all used invented slugs (`voter-dilution`, `electoral-manipulation`, etc.). Before issue creation, the monitor should validate every proposed slug against the live taxonomy and refuse to emit if any are invalid. Would eliminate most of the in-flight corrections ISSUE_TO_ENTRY currently makes.

- [ ] **Episodes editorial workflow** — Entries support an `episodes:` field and the template renders the Part-of line, but no episodes currently exist (the sample episode was removed in PR #45). There's no documented guidance on when an editor creates an episode, how ISSUE_TO_ENTRY should suggest one, or how episodes get retroactively linked when later entries arrive.
  - First obvious case: post-Callais state gerrymanders. The Tennessee entry (issue #6) is one node; once Louisiana v. Callais and other states get entries, they should share an episode like `post-callais-state-gerrymanders`.
  - Decision needed: who creates episodes — editor by hand, or agent suggests at PR time and editor confirms?
  - **Includes episode UUIDs:** when episode support is built out, episodes get a stable `id` (UUID v4) the same way entries do (PR #40), with the same build-time presence/format/uniqueness validation. Deferred from PR #40 because there are zero episodes to apply it to right now — fold it into this work rather than building speculative validation.

- [ ] **Formalize or remove the source-level `note:` field** — On the issue-6 entry, ISSUE_TO_ENTRY added ad-hoc `note:` fields to source items (e.g. *"Returned 403 to default-UA HTTP clients; article verified live"*). The field isn't in the documented schema or in `.eleventy.js` validation. Either:
  - Add to the schema (ISSUE_TO_ENTRY_SPEC Step 5 + `.eleventy.js`) as an allowed-optional field, OR
  - Move that information into the PR body and stop emitting it on the entry.

- [ ] **Define "actor" precisely** — On the issue-6 entry the agent pruned SCOTUS (contextual cause) and Rep. Steve Cohen (target) from the actor list, keeping only entities that *took* the action. The principle isn't documented anywhere. Worth codifying in STANDING_MONITOR (so the monitor produces tighter actor lists upfront) and in editorial guidance, especially for borderline cases — enablers, accomplices, signatories vs. drafters, agencies vs. specific officials, etc.

- [ ] **Distinguish transient from real build failures** — Step 6 of ISSUE_TO_ENTRY currently treats every `npm run build` failure as bad input and skip-flags the issue. But flaky `npm install`, network failures during dependency resolution, or transient CI/infra issues should retry rather than punish a perfectly good entry. Define what counts as transient and add a retry-once policy. Low priority — wait until it actually bites.

- [ ] **PR label discipline** — When the agent applied `gerrymandering` as a label on PR #21, GitHub auto-created the label (it didn't previously exist). There's no defined set of valid PR labels, no policy on whether new abuse-slug labels should be auto-created on first use, and no audit of what labels currently exist vs. what they're used for. Define the canonical label set and the rules for adding new ones. Low priority — wait until it actually bites.

- [x] ~~**Migrate cross-references from slug to id**~~ — Considered 2026-05-19 and **declined**. With build-time validation of relationship slugs in place and slugs already enforced-unique (PR #40), slug-based cross-references in `relationships.*` and `episodes:` are both safe (broken refs fail the build) and human-readable. Migrating them to opaque UUIDs would trade readability for rename-safety we no longer need. The `id` field stays as the canonical identifier; cross-references stay slug-based. Recorded so the decision isn't re-litigated.

- [ ] **Research and split issue-12 by federal agency** — Per the 2026-05-28 event-split audit, issue-12 (federal agencies refuse records to oversight investigation of DOGE data access; GSA officials block physical inspection) bundles records-refusals across multiple federal agencies plus a specific GSA physical-inspection block. Current Washington Post sourcing names GSA specifically but is less specific about which other agencies refused records. Research the underlying oversight investigation and any later reporting that named specific agencies; split into one event per agency refusal plus the GSA-specific block when sourcing supports it.

- [ ] **Research and split issue-89's two STOCK Act fines** — Per the 2026-05-28 event-split audit, issue-89 (Trump misses STOCK Act 45-day deadline; OGE fines him twice) bundles two distinct $200 fines for two separate late filings, but the current Washington Post sourcing does not name which specific late-disclosed trade triggered which fine. Research subsequent reporting (or the underlying OGE record) that names the dates and trades behind each fine; split into one event per fine when sourcing supports it.

## Done
