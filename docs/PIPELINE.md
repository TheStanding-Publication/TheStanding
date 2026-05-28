# The Standing: Pipeline Overview

A single-page system view of how a candidate story becomes an archived entry. Each stage names its spec, the skill or scheduled task that executes it, and the labels and tags that move between them. When a stage's behavior changes, the change lands in that stage's spec — this document only describes how the stages compose.

## End-to-end flow

```
                                                   ┌─→ archive-fit-merge ──→ editor
                                                   │   (merge candidate; manual)
                            ┌─ ARCHIVE_FIT ────────┼─→ not-fit ──→ editor closes
                            │  verdict             │
TRIAGE ─→ tip ──→ tip-vetter│                      ├─→ blocked-on-taxonomy
URL-TO-ISSUE ──→ archive-fit│                      │   (taxonomy PR opened;
MONITOR SCAN ─→ ready-for-entry                    │   re-vet after merge)
                            │                      │
                            └─→ archive-fit ──→ tip rewritten to [Monitoring]
                                                   tip → ready-for-entry label flip
                                                                  │
                                                                  ▼
                                                       ENTRY RECORDER ──→ entry PR
                                                                  │
                                                                  ▼
                                                         editorial PR review
                                                                  │
                                                                  ▼
                                                              merge to main
                                                                  │
                                                                  ▼
                                                             daily digest
```

Five intake paths converge on one verdict step (ARCHIVE_FIT), one recorder, one human review gate, and one publication step.

## Stages

### Triage — `NEWS_TRIAGE_SPEC`

Scheduled task `standing-news-triage` (hourly, 10pm–4am MT). Backlog-only, marches **backward** through history one day per run using the coverage ledger (issue #77). Reads headlines only; classifies against the 12 ideals (not the 77 abuses); files thin `[Tip]` issues with the `tip` label.

Output: GitHub issues labelled `tip`, authored by the `thestanding` bot. Nothing verified — these are leads, not records.

### URL-to-issue — `URL_TO_ISSUE_SPEC` (pointer to `NEWS_RESEARCH_SPEC` URL mode)

Operator-invoked. Takes a single URL, runs archive-fit in URL mode for the inclusion verdict, and — only if `archive-fit` — runs the URL-mode research mechanics to produce a `[Monitoring]` issue labelled `ready-for-entry`. Refuses on out-of-scope or blocked-domain. One URL can produce multiple issues when it bundles distinct events.

### Monitor scan — `NEWS_RESEARCH_SPEC` (scheduled-scan mode)

Four scheduled tasks: `standing-monitor-{morning,midday,afternoon,evening}` (3am, 1pm, 4pm, 8pm MT). Each scans the curated source list in `taxonomy/sources.yaml` over the configured time window, runs comprehensive research at intake (actors, jurisdiction, location, evidence, abuse slugs), and files `[Monitoring]` issues labelled `ready-for-entry`. One issue per distinct event.

### Tip vetting — `ARCHIVE_FIT_SPEC` + `standing-tip-vetter` Phase 2

Scheduled task `standing-tip-vetter` (hourly :15, 1pm–3am MT). For one open `tip` issue per run:

1. **Phase 1** — call `ARCHIVE_FIT_SPEC` in issue mode. Verdict is one of `archive-fit`, `archive-fit-merge`, `not-fit`, `blocked-on-taxonomy`, applied as a label with an explanatory comment.
2. **Phase 2** — act mechanically on the verdict:
   - `archive-fit` → fetch and execute `NEWS_RESEARCH_SPEC` URL-mode research mechanics, rewrite the tip body in place to the full `[Monitoring]` template, swap label `tip` → `ready-for-entry`, retitle `[Tip] ...` → `[Monitoring] ...`.
   - `not-fit` → close the issue.
   - `archive-fit-merge` → leave open; editor reviews the named merge target.
   - `blocked-on-taxonomy` → leave open; ARCHIVE_FIT already opened a taxonomy PR. Re-eligible after editor merges (or closes) the PR.

There is no longer a "vet-tip mode" of `NEWS_RESEARCH` — that role was split into `ARCHIVE_FIT_SPEC` (inclusion judgment) plus the mechanical Phase 2 above.

### Entry recording — `ISSUE_TO_ENTRY_SPEC`

Scheduled task `standing-entry-recorder` (every 30 min, 1pm–3am MT) processes one eligible issue per run. Eligibility: open, author=`thestanding`, label=`ready-for-entry`, no `invalid` label, no open PR referencing it.

For each eligible issue:

1. Re-read the issue body, parse the comprehensive research into fields.
2. Validate and correct in flight (re-derive stale taxonomy slugs, normalize fields, update summary to reflect current article state).
3. Re-verify primary sources + one independent corroborator (newsroom two-source rule).
4. Generate the deterministic slug (`issue-{N}-{jurisdiction}-{abuse}`) and write `src/entries/YYYY/MM/DD/<slug>.md` with a fresh UUID v4 `id`.
5. Run `npm run build` (see `BUILD_SPEC`) — must pass.
6. Create branch `entry/<slug>`, commit, push, open PR with `Closes #N` in the body.

Issues that can't be turned into valid entries get the `invalid` label and a skip-flag comment — never auto-closed.

### Editorial PR review — `EDITORIAL_WORKFLOW_SPEC`

Human review gate. For each entry PR, the editor reads archive-fit's verdict comment (already on the source issue) plus the PR's validation summary, then accepts / requests changes / closes. Editorial standards apply at this gate; the inclusion judgment was already settled upstream. See `EDITORIAL_WORKFLOW_SPEC` for the standards.

### Daily digest — `DAILY_DIGEST_SPEC`

Scheduled task `standing-daily-digest` (4:07am MT — currently paused). Assembles entries archived that day into a Buttondown newsletter. Pulls only entries with `status: published` and `archived: TODAY` — overnight merges are the typical input.

## Labels reference

Two categories of labels move issues through the pipeline. They coexist on the same issue without contradiction.

**Pipeline-status labels** — where in the process an issue sits:

| Label | Meaning | Applied by |
|---|---|---|
| `tip` | Unvetted lead from triage | `standing-news-triage` |
| `ready-for-entry` | Fully researched, awaiting recording | monitor scans, url-to-issue, tip-vetter promotion |
| `invalid` | Skip-flagged by recorder; human review needed | `standing-entry-recorder` |

**Verdict labels** — output of `ARCHIVE_FIT_SPEC`. One verdict per issue, mutually exclusive with each other:

| Label | Meaning |
|---|---|
| `archive-fit` | Passes mission, taxonomy, no same-event duplicate |
| `archive-fit-merge` | Same-event entry already exists; merge candidate |
| `not-fit` | Fails the mission test |
| `blocked-on-taxonomy` | Mission passes, no existing abuse fits; taxonomy PR opened |

No other labels are applied during normal operation. Abuse slugs are **not** applied as labels — the mapped abuses live in the issue body. Entry PRs carry no labels.

## Scheduled task cadence (MT)

Schedules respect a peak-usage quiet window (6am–12:59pm for the heavy jobs; 9am–12:59pm for the monitor scans).

| Task | Cron | Purpose |
|---|---|---|
| `standing-monitor-morning` | 3:03 AM | 24h safety-net scan |
| `standing-monitor-midday` | 1:04 PM | 8h delta scan |
| `standing-monitor-afternoon` | 4:08 PM | 5h delta scan |
| `standing-monitor-evening` | 8:01 PM | 5h delta scan |
| `standing-news-triage` | :30 hourly, 10pm–4am | one backlog day per run |
| `standing-tip-vetter` | :15 hourly, 1pm–3am | one tip per run |
| `standing-entry-recorder` | :00 and :30, 1pm–3am | one ready-for-entry issue per run |
| `standing-daily-digest` | 4:07 AM | newsletter assembly (currently paused) |

The scheduled-task wrappers are thin — each fetches its canonical spec and executes it. Behavior changes land in the spec, not in the task prompt.

## Specs referenced

- `NEWS_TRIAGE_SPEC` — headline-level backlog scan.
- `NEWS_RESEARCH_SPEC` — scheduled-scan and URL-to-issue research.
- `URL_TO_ISSUE_SPEC` — pointer document for URL-to-issue mode.
- `ARCHIVE_FIT_SPEC` — canonical inclusion judgment.
- `ISSUE_TO_ENTRY_SPEC` — entry recording (the canonical recording spec).
- `EDITORIAL_WORKFLOW_SPEC` — editorial standards and PR review.
- `DAILY_DIGEST_SPEC` — newsletter assembly.
- `TAXONOMY_APPLICATION_SPEC` — how the taxonomy maps to events.
- `ACTOR_NORMALIZATION_SPEC` — actor aliases and canonicalization.
- `BUILD_SPEC` — what the build expects from entries.
