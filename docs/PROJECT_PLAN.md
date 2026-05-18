# Project Plan — The Standing

*Working draft. Last updated 2026-05-13.*

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

**Automation: GitHub Actions + Cowork scheduled tasks.** GitHub Actions (unlimited minutes for public repos) runs the daily sourcing pipeline at 6:00 AM ET, writes `candidates/YYYY-MM-DD.md` to the repo. Cowork scheduled task drafts the day's issue from the candidates file for Bill's review.

**Secrets management.** API keys, social tokens, etc. live in GitHub Actions secrets and never get committed. Critical because the repo is public.

**Backup/mirror.** Nightly Wayback Machine snapshot of every entry URL. Optional later: IPFS pinning for true permanence.

---

## 5. Data model (each archive entry)

Each entry is a Markdown file under `entries/YYYY/MM/DD/slug.md` with frontmatter:

```yaml
date: 2026-03-15                   # date of the event
archived: 2026-03-16               # date the entry went live (display only)
slug: doj-defies-subpoena          # URL-stable; never changes after publish

headline: "..."                    # one-line factual headline
summary: "..."                     # 1-3 sentence neutral summary

abuses:                            # 1-3 entries from controlled vocab (see taxonomy)
  - voter-suppression
  - gerrymandering
# At build time, parent ideals are auto-derived from the listed abuses.

episodes:                          # optional: link to one or more named compound events
  - 2026-05-12-philadelphia-protest

actors:                            # free-form strings; normalized via aliases.yaml
  - "Stephen Miller (Deputy Chief of Staff)"
  - "U.S. Department of Justice"

jurisdiction: federal              # federal | state:CA | local:NYC:NY | international:UN

confidence: well-reported          # confirmed | well-reported | developing | alleged

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

quote:                             # optional: <15 word quote from primary source
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

- Every entry must have at least one `primary` source OR two independent `investigative` sources.
- Every `abuse` must exist in `taxonomy/abuses.yaml`. New abuses require their own PR.
- Actors are free strings, normalized at build time via `taxonomy/aliases.yaml`. New actors do NOT require a PR — they're just mentioned. Aliases get added only when sprawl is observed.
- Actor pages are auto-generated for any actor appearing in ≥3 entries (threshold configurable). Lower-frequency actors are still indexed in search and visible in the entries that mention them.
- The build emits warnings for probable duplicate actors (Levenshtein distance + abbreviation matching) so they can be reconciled in `aliases.yaml`.
- Slugs are immutable after `status: published`.

### Taxonomy: Ideals → Abuses

Two-level taxonomy. Entries tag specific abuses; the parent ideal is auto-derived. Each ideal has a written explainer page (the norm and why it matters) plus its rolled-up entry list.

1. **Free and fair elections.** voter-suppression, gerrymandering, election-denial, certification-refusal, voter-intimidation, election-worker-intimidation, disinformation-campaigns, post-election-overturning-attempts, alternate-electors, refusal-to-concede.
2. **Rule of law and equal application.** defying-court-orders, selective-prosecution, pardons-for-allies-or-self, politicized-investigations, ignoring-statutory-requirements, selective-non-enforcement.
3. **Separation of powers and independent oversight.** executive-overreach, bypassing-congress, defying-subpoenas, weaponizing-DOJ, IG-firings, watchdog-defunding, obstruction-of-OIG-investigations, retaliation-against-whistleblowers, attacks-on-judicial-independence, lying-to-congress.
4. **Free press.** press-retaliation, prosecution-of-journalists, expulsion-from-public-proceedings, access-restrictions-for-critical-outlets, legal-threats-against-publishers, FCC-or-licensing-as-leverage.
5. **Freedom of speech, assembly, and association.** protester-surveillance, prosecution-of-protected-speech, viewpoint-based-permit-denials, targeting-critics-with-government-power, blacklisting.
6. **Public service over self-dealing.** self-dealing, bribery, undisclosed-financial-conflicts, nepotism, emoluments-violations, pay-to-play, monetizing-office, procurement-irregularities.
7. **Civilian control of armed and uniformed services.** politicization-of-uniformed-services, domestic-deployment-overreach, pardons-for-uniformed-misconduct, retaliation-against-officers-following-law.
8. **Honest government data and scientific integrity.** suppression-of-government-data, politicized-science-appointments, retaliation-against-government-scientists, alteration-of-official-records, censoring-agency-research.
9. **Civil rights and equal protection.** discriminatory-policy, targeting-marginalized-communities, voter-roll-purges, religious-favoritism-in-policy.
10. **Due process.** denial-of-counsel, unlawful-detention, denial-of-hearing, ignoring-habeas, denial-of-due-process-in-immigration-enforcement, extrajudicial-actions.
11. **National sovereignty and foreign influence.** undisclosed-foreign-payments-to-officials, foreign-influence-on-policy, intelligence-irregularities, accepting-foreign-electoral-help.
12. **Accountable use of state force.** excessive-force-by-law-enforcement, deaths-in-custody, no-knock-raid-misuse, militarization-of-policing, shielding-officers-from-prosecution, failure-to-discipline-misconduct, corrections-abuse, violence-in-immigration-enforcement, federal-deployment-against-civilians.

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

## 6. Daily workflow (target state)

1. **6:00 AM ET** — scheduled task runs. Pulls last 24h from RSS, APIs, and watched social accounts.
2. **Filter** — drops anything not matching inclusion criteria via a classifier.
3. **Cluster** — groups stories about the same event together.
4. **Draft** — produces a daily brief: 5–10 items, each with headline + 1–3 sentence summary + links.
5. **Review** — Bill reviews the draft (mechanism TBD), edits, kills, or adds items.
6. **Publish** — approval commits to Git → site rebuilds → newsletter sends.

We won't have this on day one. The phased roadmap below builds toward it.

---

## 7. Roadmap

**Phase 0 — Decisions and scaffolding (this week)**
- Lock platform stack (site host, email service, repo location).
- Settle name and domain.
- Decide review workflow.
- Stand up the Git repo skeleton, Eleventy starter, and Buttondown account.

**Phase 1 — Manual daily issue (week 2–3)**
- Bill (or Bill + Claude in chat) hand-curates the first 10–14 issues.
- Each issue ships to the site and the newsletter.
- We learn what the format actually wants to be and refine the template.

**Phase 2 — Sourcing pipeline (week 4–5)**
- Build the candidate-fetcher: RSS, NewsAPI, GDELT, watched social accounts.
- Output: a daily "candidates.md" file Bill reviews to pick the day's items from.

**Phase 3 — Classifier + draft generator (week 6–7)**
- Add a classifier that scores candidates against inclusion criteria.
- Auto-cluster duplicates and generate first-pass summaries.
- Bill's job shrinks to review-and-approve.

**Phase 4 — Archive features (week 8+)**
- Theme and actor index pages.
- Full-text search.
- Timeline view.
- Cross-reference links between related entries.
- Wayback Machine snapshots, optional IPFS mirror.

**Phase 5 — Growth (post-launch)**
- Reader corrections workflow (PR-based or form-based).
- Citations / "cite this entry" links.
- API for researchers.

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
