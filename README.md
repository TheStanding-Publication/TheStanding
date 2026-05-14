# The Standing

A non-partisan US publication and historical archive that documents authoritarianism, anti-democratic behavior, and corruption — applied to any actor without partisan favor.

The name carries two meanings of "standing": legal standing (the right to be heard, the right to be part of the record) and civic standing (where we stand as a democracy). The publication asks both questions in the daily record.

See [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) for the full project plan, including mission, editorial standard, technical stack, data model, and roadmap. See [`src/standards.md`](./src/standards.md) for the editorial standards page.

## Stack

- **Site generator:** [Eleventy (11ty)](https://www.11ty.dev/)
- **Hosting:** Cloudflare Pages
- **Newsletter:** Buttondown
- **Content store:** this public GitHub repo. Each entry is a Markdown file.
- **Search (later):** [Pagefind](https://pagefind.app/)

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

PROJECT_PLAN.md  # full design document
```

## Contributing

Drafts live on feature branches; merges to `main` publish. See `PROJECT_PLAN.md` § 8 for editorial principles and § 5 for the entry data model.
