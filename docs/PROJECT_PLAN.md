# Project Plan — The Standing

*Working draft. Last updated 2026-05-28.*

A daily newsletter and durable historical archive that tracks US news and events involving authoritarianism, anti-democratic behavior, and corruption — applied without partisan favor.

**Name:** *The Standing.* Carries two meanings — legal standing (the right to be heard, the right to be part of the record) and civic standing (where we stand as a democracy). The publication asks both questions in the daily record.

---

## 1. Mission

Document, in real time and for the historical record, US events that deviate from small-d democratic norms: erosion of checks and balances, abuse of office, weaponization of state power, suppression of dissent or the press, undermining of elections, and public corruption.

**Non-partisan standard.** The same yardstick applies regardless of which party, official, or actor is involved. The publication is not anti-Republican or pro-Democrat (or vice versa) — it is pro-democratic-norm. If a Democratic official does something authoritarian, it goes in the log. If a Republican official does something authoritarian, it goes in the log. Same for state, local, and federal actors, and for non-government actors when relevant.

**Documentary tone.** Factual, sourced, and durable — not polemical. The reader should trust this as a record they can cite years from now, not as opinion journalism.

---

## 2. What gets archived (inclusion criteria)

An item qualifies if it credibly involves one or more of these patterns:

- **Erosion of checks and balances** — defying court orders, refusing oversight, dismantling watchdog institutions, blocking subpoenas, end-runs around constitutional limits.
- **Election integrity issues** — voter suppression, refusal to certify, election denial by officeholders, intimidation of election workers, manipulation of districting beyond the routine.
- **Press freedom and dissent** — retaliation against journalists, prosecution of speech, surveillance of protesters or critics, expulsion of media from public proceedings.
- **Abuse of office / weaponization of power** — using state authority to punish political enemies or reward allies, politicized prosecutions, politicized hiring/firing in nonpartisan roles.
- **Corruption** — self-dealing, bribery, undisclosed financial conflicts, foreign influence, illicit enrichment in office.
- **Anti-democratic rhetoric or planning** — explicit calls to suspend constitutional processes, normalize political violence, or replace democratic institutions with one-party rule.

We track documented events, not vibes. A single recorded instance is enough — there is no requirement that an event be part of a wider pattern before it can be archived. The threshold is whether the event fits a specific abuse in the taxonomy and meets the sourcing standard. (This is the broken-windows view of democratic decline: small accumulating breaches are themselves the pattern, and the archive's value to future readers depends on not filtering them out.)

---

## 3. Sourcing strategy

A wide-net intake feeds a human-curated archive.

- **RSS feeds** from established outlets (AP, Reuters, NYT, WSJ, WaPo, ProPublica, The Guardian US, NPR, Politico, Lawfare, Just Security, state-level investigative outlets).
- **News APIs** — NewsAPI for breadth, GDELT for global event detection and historical comparisons, possibly Common Crawl for back-fills.
- **Social signals** — X (selected accounts: court reporters, beat reporters, legal scholars), Reddit (r/law, r/politics, r/scotus), Bluesky.
- **Official sources** — federal court PACER docket monitors, DOJ press releases, OIG reports, GAO reports, congressional committee feeds.
- **Citizen documentation** — phone video, photographs, and contemporaneous social-media posts capturing events directly. Surfaced via journalist amplification, organized witness platforms, and direct submissions. Critical to broken-windows in practice: most small accumulating breaches never produce an official record, but they often produce a phone video.
- **Manual curation** — Bill adds stories that don't surface via the above, especially state and local items.

Quality > quantity. Every entry must meet the sourcing floor in [editorial standards](/standards/): at least one primary source — court filing, OIG report, transcript, official statement, or verified citizen-captured documentation — or at minimum two independent reputable outlets. The primary tier explicitly includes citizen-captured evidence that meets the verification bar (unedited, contextually clear, corroborated where attribution is absent). Anonymous citizen documentation is acceptable; anonymous institutional sources are not.

---

## 4. Technical stack (locked in 2026-05-12)

**Site host: Cloudflare Pages.** Free tier, unlimited bandwidth, custom domain free, fastest global delivery. The free tier is sustainable because the CDN is Cloudflare's core business.

**Site generator: Eleventy (11ty).** Pure Markdown + Nunjucks templates, no JS framework runtime, minimal dependency tree. Tag pages are native via pagination; actor/theme index pages built from custom collections (a small `.eleventy.js` config). Output is plain HTML — ideal for a long-lived archive. For search later: Pagefind (static-site search, build-time index, tiny client widget — no backend).

**Newsletter: Buttondown ($9/mo).** Markdown-first, indie, no dark patterns. Has a full REST API (create drafts, schedule, publish, manage subscribers) so we can automate publishing later. Also supports RSS-to-email, which means the initial workflow can be as simple as "git push → site rebuilds → Buttondown auto-sends." Exports cleanly if we ever need to migrate.

**Content store: a public GitHub repo.** Every entry is a Markdown file with frontmatter. Drafts live on feature branches; merges to `main` publish. Git history is the public audit trail — every edit, retraction, and correction is timestamped and attributable. Public-from-day-one is a "show your work" signal for a non-partisan watchdog.

**Automation: Cowork scheduled tasks.** A set of Cowork scheduled tasks (`standing-monitor-*`, `standing-news-triage`, `standing-tip-vetter`, `standing-entry-recorder`, `standing-daily-digest`) execute the pipeline end to end. Each task is a thin wrapper that fetches a canonical spec from `docs/specs/` and follows it exactly. See [`PIPELINE.md`](./PIPELINE.md) for the full system view.

**Secrets management.** The bot account's GitHub fine-grained PAT is held outside the repo and rotated periodically. The repo is public; no credentials are committed.

**Backup/mirror.** Nightly Wayback Machine snapshot of every entry URL is a planned addition (see `TASKS.md` → source archive snapshot). Optional later: IPFS pinning for true permanence.

---

## 5. Data model (each archive entry)

Each entry is a Markdown file under `src/entries/YYYY/MM/DD/slug.md` with frontmatter. The build (`.eleventy.js`) validates every entry against the contract documented in [`BUILD_SPEC`](./specs/BUILD_SPEC.md):

```yaml
id: 550e8400-e29b-41d4-a716-446655440000   # UUID v4. Required. Globally unique.
                                           # Stable identifier; never changes.
date: 2026-03-15                   # date of the event (YYYY-MM-DD)
archived: 2026-03-16               # date the entry went live (display only)
slug: doj-defies-subpoena          # URL-stable; never changes after publish

headline: "..."                    # one-line factual headline
summary: "..."                     # 1-3 sentence neutral summary

abuses:                            # 1-3 entries from controlled vocab (see taxonomy).
  - voter-suppression              # Every slug must exist in taxonomy/abuses.yaml.
  - gerrymandering                 # Parent ideals are auto-derived from these at
                                   # build time — do not list ideals on entries.

episodes:                          # optional: link to one or more named compound events.
  - 2026-05-12-philadelphia-protest

actors:                            # free-form strings; normalized via aliases.yaml.
  - "Stephen Miller (Deputy Chief of Staff)"   # The build strips the parenthetical role
  - "U.S. Department of Justice"               # and resolves the bare name through aliases.

jurisdiction: federal              # federal | state | local | international | private-actor
location: "Washington, DC"         # see EDITORIAL_WORKFLOW_SPEC for per-jurisdiction
                                   # location requirements.

sources:
  - url: "https://..."
    publisher: "U.S. District Court SDNY"
    tier: primary                  # primary | investigative | secondary
    title: "Order denying motion to quash"
    accessed: 2026-03-16
  - url: "https://..."
    publisher: "Reuters"
    tier: investigative
    title: "..."
    accessed: 2026-03-16

quote:                             # optional. Build enforces fewer than 30 words.
  text: "..."
  source-index: 0

relationships:
  follows: [prior-slug]            # manual; development in a previously-archived story.
                                   # Build surfaces candidates based on shared actors+abuses.
  corrects: []                     # manual; this entry corrects a prior one.
  retracts: []                     # manual; this entry retracts a prior one.
  see-also-override: []            # rarely needed. see-also is auto-derived at build time
                                   # from (overlapping abuses + overlapping actors + temporal
                                   # proximity). Use this only to pin or exclude specific entries.

corrections:                       # log of in-place edits to this entry
  - date: 2026-03-17
    note: "Fixed spelling of agency name."

status: published                  # draft | published | corrected | retracted
```

**No severity field.** The publication documents facts and sources without ranking. Readers form their own conclusions.

**Schema rules enforced at build time:**

See [`BUILD_SPEC`](./specs/BUILD_SPEC.md) for the authoritative list. In summary:

- Every entry carries a UUID v4 `id`, globally unique across the archive.
- Every entry has at least one `primary` source OR two independent `investigative` sources.
- Every `abuse` slug must exist in `taxonomy/abuses.yaml`. New abuses require their own PR (typically opened by `ARCHIVE_FIT_SPEC` when a candidate story exposes a gap).
- Actors are free strings, normalized at build time via `taxonomy/aliases.yaml`. New actors do NOT require a PR — they're just mentioned. Aliases get added only when sprawl is observed; see [`ACTOR_NORMALIZATION_SPEC`](./specs/ACTOR_NORMALIZATION_SPEC.md).
- Actor pages are auto-generated for any actor appearing in ≥3 entries.
- Slugs are immutable after `status: published`.
- Quote text is fewer than 30 words.

A planned weekly retrospective will flag probable duplicate actors via Levenshtein-style matching and propose aliases — not yet built (see `TASKS.md`).

### Taxonomy: Ideals → Abuses

Two-level taxonomy. Entries tag specific abuses; the parent ideal is auto-derived at build time. Each ideal has a written explainer page (the norm and why it matters) plus its rolled-up entry list.

- The 12 ideals are defined in [`taxonomy/ideals.yaml`](../taxonomy/ideals.yaml).
- The abuses (currently 80, and growing as `ARCHIVE_FIT_SPEC` surfaces taxonomy gaps) are defined in [`taxonomy/abuses.yaml`](../taxonomy/abuses.yaml). Each abuse references its parent ideal via the `ideal:` field.

For the abuse-mapping rules (when to tag what, how to handle ambiguity, the taxonomy-gap path), see [`TAXONOMY_APPLICATION_SPEC`](./specs/TAXONOMY_APPLICATION_SPEC.md).

The taxonomy applies symmetrically to anyone exercising public power — including private actors (contractors, platforms, foreign states) when their actions intersect with these abuses. Type metadata (person, agency, court, legislature, party, company, ngo, foreign-state, individual) is optional and only attached to actors that get promoted into `aliases.yaml`.

### Indexes the build generates

- `/` — front page: most recent entries
- `/entries/YYYY/MM/DD/<slug>/` — individual entry permalinks (immutable after publish)
- `/ideals/` — index of all 12 ideals with their explainers
- `/ideals/<ideal>/` — explainer + every entry whose abuses roll up to this ideal
- `/ideals/<ideal>/<abuse>/` — every entry tagged with this specific abuse, nested under its parent ideal
- `/episodes/` — index of all named compound events (protests, election days, hearings, operations)
- `/episodes/<slug>/` — editorial overview of a compound event + every entry filed against it
- `/actors/<actor-slug>/` — every entry involving this person, agency, or institution (auto-generated at 3+ entry threshold)
- `/timeline/` — chronological view across the whole archive
- `/corrections/` — every correction and retraction the publication has issued

### Episodes (compound events)

When multiple recorded events all happen together as part of one real-world happening — a protest with arrests and press retaliation and surveillance, an election day with intimidation in multiple precincts, a congressional hearing with several officials lying — each is documented as its own entry, and they are also grouped under an **episode**.

An episode is a Markdown file at `src/content/episodes/<slug>.md` with:

- `slug` (URL-stable, immutable after first reference)
- `title` (display name)
- `start_date` and optional `end_date`
- Required editorial overview body — what the compound event was, scale, context, timeline

Entries reference episodes via an optional `episodes:` list in frontmatter. An entry can belong to more than one episode. The build validates every episode reference against existing episode files.

The episode page shows the editorial overview plus a chronologically ordered list of every entry filed against it. Each entry page displays "Part of: [episode title]" linking up to the episode.

URL stability: slugs and structural URLs are immutable after publish. If an abuse ever needs to move to a different parent ideal, the old URL becomes a permanent redirect (Cloudflare Pages `_redirects`). The original URL keeps working forever.

---

## 6. Daily workflow

The pipeline runs end to end as a series of Cowork scheduled tasks against the specs in `docs/specs/`. See [`PIPELINE.md`](./PIPELINE.md) for the diagram, the per-stage cadence, and the labels and tags that move issues from stage to stage.

In short: monitor scans and triage produce `tip` and `[Monitoring]` issues; archive-fit (via `standing-tip-vetter`) renders the inclusion verdict and promotes the worthwhile candidates to `ready-for-entry`; the entry recorder turns each ready issue into an entry PR; editor reviews and merges; the daily digest assembles the day's archived entries and sends to subscribers via Buttondown.

---

## 7. Roadmap

**Phase 0 — Decisions and scaffolding.** ✓ Done. Stack locked; name and domain settled; Git repo, Eleventy build, and Buttondown account live.

**Phase 1 — Manual daily issue.** ✓ Done. Manual entries shipped, format refined.

**Phase 2 — Sourcing pipeline.** ✓ Done in a different shape than originally drafted. Instead of a "candidates.md" file, the live pipeline is a set of agent-driven scheduled tasks (`NEWS_RESEARCH_SPEC`, `NEWS_TRIAGE_SPEC`) that file `[Monitoring]` and `[Tip]` issues directly. See [`PIPELINE.md`](./PIPELINE.md).

**Phase 3 — Classifier + draft generator.** ✓ Done in a different shape. The "classifier" role is owned by [`ARCHIVE_FIT_SPEC`](./specs/ARCHIVE_FIT_SPEC.md), which renders the inclusion verdict per candidate; the "draft" role is owned by [`ISSUE_TO_ENTRY_SPEC`](./specs/ISSUE_TO_ENTRY_SPEC.md), which produces fully-formed entry PRs the editor reviews.

**Phase 4 — Archive features.** ✓ Mostly done. Ideal and abuse index pages, actor pages, episode pages, timeline, corrections, RSS feed, and see-also derivation all ship from the build. Full-text search and Wayback snapshots remain — both tracked in [`TASKS.md`](../TASKS.md).

**Phase 5 — Growth (post-launch).** Open. Reader corrections workflow, citation/cite-this links, API for researchers — all open.

**Current focus.** Hardening and observability — pipeline drift detection, daily summary, auto-merge for high-confidence entry PRs, weekly actor/episode retrospective. See [`TASKS.md`](../TASKS.md) for the live list.

---

## 8. Open decisions (parking lot)

- **Name and domain.** Deferred — we'll brainstorm when ready.
- **Review workflow.** Deferred. Options: email draft, file-in-workspace, web dashboard, chat.
- **Public vs. private repo.** Public enables reader PRs; private allows draft work without leakage. Likely: private "drafts" repo, public "published" repo.
- **Comments / community.** Default: no comments on the site. Reader correspondence via email.
- **Funding model.** Free for now. Decide between donation, paid tier, or grant later.
- **Legal review.** As volume grows, decide when to retain media-law counsel. Defamation risk is real on a corruption beat.

---

## 9. Editorial principles (draft)

For the full editorial standard see [/standards/](src/standards.md). The principles in short:

1. **Document, don't editorialize.** State what happened and link to the primary source. Let the pattern speak.
2. **Cite primary documents whenever possible.** Court filings, OIG reports, transcripts, official statements, and verifiable citizen-captured documentation — not just headlines.
3. **Apply the standard symmetrically.** If a Democrat does it, it's logged. If a Republican does it, it's logged. Same threshold.
4. **Broken windows.** No anti-democratic action is too small to record. The precinct-level incident and the national overturning attempt are documented with the same standards. Small accumulating breaches are themselves the pattern.
5. **Citizen documentation is primary.** Phone video and other first-hand citizen evidence, verified for authenticity, counts as primary source material in the same sense a court filing does. Anonymity for citizen sources is protected; the recording's verification rests on the recording itself.
6. **Correct in public.** Retractions and corrections are themselves archive entries, with the original version preserved and crossed out, not deleted.
7. **No anonymous institutional sources.** The "unnamed senior official said" category is excluded. Citizen documentation from an anonymous source is a different category and acceptable when the recording itself can be verified.
8. **Time-stamp the record.** Entries are dated, archived, and never silently edited.
