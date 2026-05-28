# The Standing: Actor Normalization

## Purpose

This spec is the **canonical source of truth** for actor naming and consolidation in the archive. Other specs defer to it: `ISSUE_TO_ENTRY_SPEC` Step 3 (actor filtering and normalization), `EDITORIAL_WORKFLOW_SPEC` (PR review of actors), and `BUILD_SPEC` (build-time alias resolution) all apply this spec's rules rather than restating them.

Actor sprawl is the problem this spec solves: the same person or organization appearing under multiple names ("Trump" / "Donald Trump" / "President Trump") fragments the actor page system. The build resolves variants to a canonical name using [`taxonomy/aliases.yaml`](../../taxonomy/aliases.yaml). This spec defines when an alias goes into that file and what the canonical name should be.

## Inputs

- [`taxonomy/aliases.yaml`](../../taxonomy/aliases.yaml) — the alias registry.
- The actor names appearing on entries — raw, from the issue body's "Actors involved" section.

## How callers use this spec

| Caller | Where | What it expects |
|---|---|---|
| `ISSUE_TO_ENTRY_SPEC` | Step 3 (validate-and-correct) | Filter the actor list to entities that **took the action**; emit names as-found (build will normalize). |
| `EDITORIAL_WORKFLOW_SPEC` | PR review | Spot fragmentation across recent entries; flag actors that need an alias. |
| `BUILD_SPEC` | Build time | Resolve every raw actor string through `aliases.yaml`; generate the actor page using the canonical name. |

Entries are not required to use canonical names — the build handles the lookup. What the build can't do is detect that two different-looking names refer to the same person; that's an editorial judgment call this spec governs.

## Who counts as an actor

Actors are entities that **took the action** the entry describes — the perpetrators of the abuse, not the context, not the targets. This is the filter `ISSUE_TO_ENTRY_SPEC` applies at Step 3.

- **Include:** named individuals who committed the act; the agencies, organizations, or companies whose decision made it possible.
- **Exclude:** a court whose prior ruling enabled the action (context, not actor); an opposition party that protested it (commentary, not action); the target of the action (victim, not actor).

When in doubt, ask: "Did this entity *do* the abuse, or are they here for backstory?" If backstory, mention in the body, not the actor list.

## The alias registry

The registry lives at [`taxonomy/aliases.yaml`](../../taxonomy/aliases.yaml). Each entry has the following shape:

```yaml
- slug: us-doj
  canonical: "U.S. Department of Justice"
  type: agency
  aliases:
    - "DOJ"
    - "Department of Justice"
    - "Justice Department"
    - "USDOJ"
```

Fields:

- **`slug`** — URL-safe identifier for the actor page (`/actors/<slug>/`).
- **`canonical`** — the display name. Used everywhere the actor appears: archive pages, see-also lists, the actor's own page.
- **`type`** *(optional)* — one of `person`, `agency`, `court`, `legislature`, `party`, `company`, `ngo`, `foreign-state`, `individual`. Used by templates for formatting.
- **`aliases`** — list of alternate spellings that should resolve to this canonical entry.
- **`notes`** *(optional)* — editorial context (former names, disambiguation, etc.).

**Matching is case-insensitive but exact-string** after dropping any parenthetical trailing role: `"Donald Trump (President)"` becomes `"Donald Trump"` before the lookup. See `.eleventy.js` → `normalizeActor()` for the precise algorithm.

## When to add an alias

The trigger is **observed fragmentation**: the same actor appears in entries under two or more distinct names. Don't pre-register actors before fragmentation exists — `aliases.yaml` is a reactive registry, not a directory.

In practice, add an alias when both of these are true:

1. The actor has appeared in **3 or more** entries (the threshold at which the build generates an actor page — see `BUILD_SPEC`).
2. **At least two** of those entries use different names for the same actor.

Below the threshold, the actor exists on the entries but has no dedicated page, so fragmentation has no public-facing cost.

## When NOT to add an alias

- **Different people with similar names.** "John Smith" the senator and "John Smith" the activist stay separate. Disambiguate in the entry's actor list (e.g. `"John Smith (NY-12)"` vs `"John Smith (ACLU)"`) — do not collapse via alias.
- **A one-off typo in a single entry.** Fix the typo in the entry, not the registry.
- **A name still in flux.** If a new public figure's commonly-used name is shifting in real time, wait for it to stabilize. Adding an alias now and reversing it later is more disruptive than waiting.

## Choosing the canonical name

The canonical name is what readers see. Prefer the **most recognizable** form a literate reader would use unprompted:

- **People** — full name without title. `"Donald Trump"`, not `"President Trump"` or `"Donald J. Trump"`. Title goes in the entry's parenthetical role, not the canonical.
- **Agencies** — full official name. `"U.S. Department of Justice"`, with `"DOJ"` as an alias.
- **Companies** — common public name. `"Meta"`, with `"Meta Platforms, Inc."` and `"Facebook Inc."` as aliases. Use the legal name only if it's the form most readers would search for.
- **Activist groups / NGOs** — common name. `"ACLU"` can be canonical if that's how it's referred to in headlines; `"American Civil Liberties Union"` then becomes the alias.
- **International figures** — most common English transliteration. `"Vladimir Putin"`, with formal and alternate spellings as aliases.

For an actor who held multiple titles over time (e.g. `"Police Captain"` then `"Police Commissioner"`), keep one canonical (the bare name); the titles live in each entry's actor list as parentheticals.

For an actor whose legal name changed (transition, marriage), use the current legal name as canonical; include the prior name as an alias to keep historical entries discoverable.

## Workflow: adding an alias

1. **Verify the trigger.** Three or more entries; at least two different names for the same actor.
2. **Pick the canonical name** per the rules above.
3. **List the aliases.** Search the archive for every name variant currently in use. Include common abbreviations and any prior names worth preserving for discoverability.
4. **Pick or generate the slug.** Slug is kebab-case, URL-safe, and disambiguating where needed (e.g. `john-smith-ny` if there's a name collision).
5. **Edit [`taxonomy/aliases.yaml`](../../taxonomy/aliases.yaml).** Place the entry in alphabetical order by canonical name; the file is small enough that ordering helps review.
6. **Run `npm run build`.** Confirm no errors (the build resolves all actor strings at load time). Spot-check the actor page renders under the canonical name.
7. **Open a PR.** Title: `aliases: normalize <Canonical Name>`. Body: name the entries that exposed the fragmentation. No editorial approval needed — alias additions are metadata.

## Future: weekly retrospective

A planned scheduled job (see [`TASKS.md`](../../TASKS.md) → "Weekly retrospective: actor aliases + episode grouping") will scan recent entries for actor-name fragmentation and propose aliases automatically. Until that lands, this is a manual editorial pass — typically prompted by spotting variants during PR review.

## Key principles

1. **Reactive, not preemptive.** Aliases are added when fragmentation is observed, not before.
2. **Threshold-gated.** Three entries minimum. Below that there's no actor page and no fragmentation cost.
3. **Recognizability first.** Canonical names are what readers expect, not what's most formal.
4. **One canonical per actor.** No chained aliases, no circular references.
5. **Titles live on entries, not the registry.** The registry has names; the entry has the role they held at the time.

## Related specs

- [`ISSUE_TO_ENTRY_SPEC`](./ISSUE_TO_ENTRY_SPEC.md) Step 3 — filters actors to those who took the action; passes raw names through to the entry.
- [`EDITORIAL_WORKFLOW_SPEC`](./EDITORIAL_WORKFLOW_SPEC.md) — PR review catches fragmentation in practice.
- [`BUILD_SPEC`](./BUILD_SPEC.md) — actor normalization, actor-page threshold, see-also derivation.
- [`taxonomy/aliases.yaml`](../../taxonomy/aliases.yaml) — the registry itself.
