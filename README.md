# The Standing

A non-partisan US publication and historical archive that documents authoritarianism, anti-democratic behavior, and corruption — applied to any actor without partisan favor.

The name carries two meanings of "standing": legal standing (the right to be heard, the right to be part of the record) and civic standing (where we stand as a democracy). The publication asks both questions in the daily record.

See [`docs/PROJECT_PLAN.md`](./docs/PROJECT_PLAN.md) for the full project plan, including mission, editorial standard, technical stack, data model, and roadmap. See [`src/standards.md`](./src/standards.md) for the editorial standards page. See [`/sources/`](https://thestanding.us/sources/) for the public list of news sources used in automated monitoring.

## Stack

- **Site generator:** [Eleventy (11ty)](https://www.11ty.dev/)
- **Hosting:** Cloudflare Pages
- **Newsletter:** Buttondown
- **Content store:** this public GitHub repo. Each entry is a Markdown file.
- **Search (later):** [Pagefind](https://pagefind.app/)

## Monitoring sources

The Standing uses automated news monitoring to surface relevant stories from a curated, public list of sources. The list includes:

- **National news outlets** — AP, Reuters, NPR, NYT, WaPo, BBC, ProPublica, and others
- **Government sources** — Congressional Record, Federal Register, Supreme Court opinions, GAO reports
- **Civil rights watchdogs** — Brennan Center, Common Cause, Democracy Forward, ACLU
- **Press freedom organizations** — Reporters Without Borders, Committee to Protect Journalists
- **Investigative outlets** — specialized sources focused on democracy accountability

All sources are **public and transparent** — see [`taxonomy/sources.yaml`](./taxonomy/sources.yaml) for the complete list, or visit [thestanding.us/sources/](https://thestanding.us/sources/) for the web version.

## Local development

```bash
npm install
npm run serve        # local dev server with live reload
npm run build        # build to _site/
```

## Repository structure

```
src/
  _data/         # global data — site config, taxonomy loader
  _includes/     # layouts and partials (Nunjucks)
  entries/       # archived entries, organized by date: YYYY/MM/DD/slug.md
  css/           # styles

taxonomy/
  ideals.yaml    # the 12 democratic ideals
  abuses.yaml    # specific abuses, each tied to a parent ideal
  aliases.yaml   # actor-name normalization (built up over time)
  sources.yaml   # curated list of news sources for monitoring

docs/
  PROJECT_PLAN.md           # full design document
  WORKFLOWS_COMPLETED.md    # workflow status and architecture summary
  skills/                   # workflow skill documentation
    NEWS_RESEARCH_SPEC.md
    NEWS_TRIAGE_SPEC.md
    ENTRY_RECORDING_SPEC.md
    EDITORIAL_WORKFLOW_SPEC.md
    TAXONOMY_APPLICATION_SPEC.md
    DAILY_DIGEST_SPEC.md
    ACTOR_NORMALIZATION_SPEC.md
    NEWS_RESEARCH_TEST_SPEC.md
```

## Contributing

Drafts live on feature branches; merges to `main` publish. See `docs/PROJECT_PLAN.md` § 8 for editorial principles and § 5 for the entry data model.
