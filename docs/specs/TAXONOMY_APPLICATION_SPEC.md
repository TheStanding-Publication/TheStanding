# The Standing: Taxonomy Application

## Purpose

This spec is the **canonical source of truth** for how events are mapped to abuses in The Standing's taxonomy. Other specs defer to it: `NEWS_RESEARCH_SPEC` Step 3 (semantic evaluation), `ARCHIVE_FIT_SPEC` Step 4 (abuse match), and `ISSUE_TO_ENTRY_SPEC` Step 3 (validate-and-correct) all apply this spec's rules rather than restating them.

When the mapping logic changes — what counts as a clean match, how to handle ambiguity, when to use secondary abuses, what the taxonomy-gap path is — the change lands here. All callers fetch this document on next run.

## Inputs

- `taxonomy/ideals.yaml` — the 12 democratic ideals.
- `taxonomy/abuses.yaml` — the 77 (and growing) abuses, each tied to one ideal via the `ideal:` field.
- The candidate event — a story, an issue body, or a source article.

## How callers use this spec

| Caller | Where | What it expects |
|---|---|---|
| `NEWS_RESEARCH_SPEC` | Step 3 (semantic evaluation) | Map 1–5 abuses per story; emit only slugs that exist in the live `abuses.yaml`. |
| `ARCHIVE_FIT_SPEC` | Step 4 (abuse match) | Match per ideal; use the taxonomy-gap path when nothing fits. |
| `ISSUE_TO_ENTRY_SPEC` | Step 3 (validate-and-correct) | Re-derive abuse slugs when the upstream issue used invalid or stale ones. |

A caller never invents slugs, never extends the taxonomy inline, and never silently substitutes a related abuse for one that doesn't fit. The taxonomy-gap path (below) is how that gets handled.

## The Taxonomy Structure

Two levels, with auto-derivation between them.

**Level 1: Democratic Ideals (12 total).** Each is a positive principle (e.g. "Free and fair elections"). Ideals are not assigned to events directly — they're auto-derived at build time from the abuses an entry is tagged with. See `BUILD_SPEC` → auto-derivation.

**Level 2: Abuses (77+).** Each abuse has a `slug`, a `title`, a `description`, and an `ideal` it violates. Authors tag entries with abuse slugs only.

**Key rule:** the parent ideal is auto-derived from the abuse at build time. Tagging both is redundant — and the build will fail if an ideal slug appears where an abuse slug is expected.

## Mapping workflow

### Step 1: Understand what happened

Read the headline, summary, and primary source. Be specific:

- **Who** did it? (Actor — title, agency, organization.)
- **What** did they do? (Specific action — not "behaved badly," but "fired the inspector general.")
- **When** and **where**?
- **How** does it violate democratic norms? (Which ideal does it touch?)

If you can't answer "what specifically happened," you can't tag — and you probably can't archive. Surface to the operator before proceeding.

### Step 2: Identify the primary abuse

Match the event to an abuse's **definition** in `abuses.yaml`, not to a keyword. The slug is a hook; the description is the contract.

The primary abuse is the **core** of what happened — what an unfamiliar reader would say the event was an instance of, in one phrase. Each entry has exactly one primary abuse; it appears first in the `abuses[]` list and feeds the slug generation in `ISSUE_TO_ENTRY_SPEC`.

Worked examples:

- **State election official certifies despite a losing candidate's pressure campaign.** Primary: `election-worker-intimidation`. Not `election-denial` — the official resisted denial; the abuse was directed *at* them.
- **Federal court rules an executive order exceeded constitutional authority.** Primary: `executive-overreach`. The abuse is the order itself, not the ruling.
- **Police use force against protesters during a lawful assembly; injuries result.** Primary: `excessive-force-by-law-enforcement`. Not `freedom-of-assembly-restriction` — the restriction came through force, not through permit denial or a legal barrier.

### Step 3: Add secondary abuses sparingly

Tag a secondary abuse only when the abuse definition clearly applies — not because the event is "related" to it or because the actor is the kind who often commits it. Typical entries map to 1–3 abuses. Most editorial mis-mappings come from over-tagging, not under-tagging.

Worked examples:

- **President fires the IG investigating his agency; DOJ launches an investigation of the fired IG.** Primary: `retaliation-against-whistleblowers`. Secondary: `weaponizing-DOJ` (the politically motivated DOJ investigation), `IG-firings`. All three abuses are independently present.
- **State passes voter-ID law; research shows 3x impact on minority voters.** Primary: `voter-suppression`. Secondary: **none**. Impact data is not the same as explicit targeting; the law's mechanism is what's tagged, not the demographics of who it falls on.

### Step 4: Handle ambiguity and gaps

Two cases the mapper has to recognize.

**Ambiguous fit — multiple abuses could plausibly apply.** Read each candidate definition. Ask: which is the **core** of what happened? Pick that as primary. Add others as secondary only if their definitions independently apply. Err narrow.

**No fit — no existing abuse cleanly describes the event.** This is a **taxonomy-gap signal**, not a discard signal. The taxonomy grows by design when real events expose missing categories.

The handling depends on which caller is mapping:

- **`ARCHIVE_FIT_SPEC` (issue mode):** verdict is `blocked-on-taxonomy`. Archive-fit drafts the new abuse and opens a PR against `taxonomy/abuses.yaml`. Source issue is held until the PR resolves.
- **`NEWS_RESEARCH_SPEC` (Step 3):** pick the closest existing abuse, flag the imperfect fit in the issue body's **Analysis** section. The downstream archive-fit/issue-to-entry will catch the gap and either re-map or open the taxonomy PR.
- **`ISSUE_TO_ENTRY_SPEC` (Step 3):** re-run archive-fit on the issue rather than skip-flagging. Archive-fit owns the taxonomy-gap path.

Never invent a slug. Never apply a wrong-fit slug to avoid the gap path. Stretched abuses poison the archive's analytical value.

## Common over-tagging mistakes

A few patterns to avoid:

- **Tagging the actor, not the abuse.** "A senator lied in a speech" is not `obstruction-of-OIG-investigations` just because the actor is unsympathetic. Tag what was done, not who did it.
- **Tagging political disagreement.** A senator voting against a regulation is not `executive-overreach` — it's ordinary politics. The event itself must be an abuse.
- **Tagging proximity.** An abuse happening in a state does not mean every event from that state is tagged with the abuse. The event itself must match the definition.
- **Splitting one act into two abuses.** Tagging both `voter-suppression` AND `election-denial` when only one applies. Pick the core.
- **Confusing impact with intent.** Disparate impact is noted in sources; the abuse classification is about the act itself.

## Decision sketches (not rules)

These are quick reference patterns — read the abuse definition for the real answer.

- **Voters can't vote** — access blocked by law/policy → `voter-suppression`; election workers pressured → `election-worker-intimidation`; results denied → `election-denial`; certification refused → `certification-refusal`.
- **Police vs. protesters** — force used → `excessive-force-by-law-enforcement`; protesters arrested for lawful speech → `prosecution-of-protected-speech`; permits denied by viewpoint → `viewpoint-based-permit-denials`; surveillance → `protester-surveillance`.
- **Press incidents** — journalist arrested → `prosecution-of-journalists`; outlet retaliated against → `press-retaliation`; press access blocked → `expulsion-from-public-proceedings`; publisher threatened → `legal-threats-against-publishers`.
- **Oversight blocked** — refused to comply → `defying-subpoenas`; watchdog fired → `IG-firings`; investigation obstructed → `obstruction-of-OIG-investigations`; whistleblower retaliated against → `retaliation-against-whistleblowers`.
- **Executive power** — acted beyond authority → `executive-overreach`; bypassed legislature → `bypassing-congress`; defied a court → `defying-court-orders`; improper pardon → `pardons-for-allies-or-self`.
- **Self-dealing** — conflict undisclosed → `undisclosed-financial-conflicts`; family hired → `nepotism`; office monetized → `monetizing-office`; bribe accepted → `bribery`; power used to help an associate → `pay-to-play` + `self-dealing`.

For the complete current list of abuse slugs and definitions, read [`taxonomy/abuses.yaml`](../../taxonomy/abuses.yaml) directly — it is the source of truth, and any list quoted in spec text drifts.

## Key principles

1. **Match definitions, not keywords.** The slug is a hook for storage; the description is the contract.
2. **One primary abuse.** Whatever a reader would call the event in one phrase.
3. **Secondary abuses are evidence-driven, not associative.** Add only if the definition independently applies.
4. **Gaps are signals.** No fit means the taxonomy needs a new abuse, not that the wrong abuse should be force-fit.
5. **Never invent slugs.** Every emitted slug must already exist in the live `abuses.yaml`.
6. **The build auto-derives ideals.** Tagging ideals is redundant and an error — see `BUILD_SPEC`.

## Related specs

- [`ARCHIVE_FIT_SPEC`](./ARCHIVE_FIT_SPEC.md) — owns the inclusion verdict; uses this spec's rules at its Step 4.
- [`NEWS_RESEARCH_SPEC`](./NEWS_RESEARCH_SPEC.md) — uses this spec at Step 3 (semantic evaluation).
- [`ISSUE_TO_ENTRY_SPEC`](./ISSUE_TO_ENTRY_SPEC.md) — uses this spec at Step 3 (validate-and-correct).
- [`BUILD_SPEC`](./BUILD_SPEC.md) — what the build does (and doesn't) enforce about abuses on entries.
- [`taxonomy/abuses.yaml`](../../taxonomy/abuses.yaml) — definitions, source of truth.
- [`taxonomy/ideals.yaml`](../../taxonomy/ideals.yaml) — the 12 ideals.
