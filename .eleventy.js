// Eleventy configuration.
//
// Responsibilities:
//   1. Load taxonomy (ideals, abuses, aliases) and make it available as global data.
//   2. Build the `entries` collection from src/entries/, sorted newest first.
//   3. Build derived collections: ideals, abuses, actors — each with attached entries.
//   4. Validate entries against the schema at build time. Fail the build on:
//        - unknown abuses
//        - missing sourcing (no primary OR <2 investigative sources)
//   5. Compute see-also relationships at build time.
//   6. Generate permalinks: /entries/YYYY/MM/DD/slug/, /ideals/<ideal>/<abuse>/, etc.
//   7. Expose Nunjucks filters used by the templates.

const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

// --- Helpers ---

function loadYaml(relPath) {
  const fullPath = path.join(__dirname, relPath);
  return yaml.load(fs.readFileSync(fullPath, "utf8"));
}

function slugify(s) {
  return String(s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

// Normalize an actor string against the aliases.yaml registry.
// Returns { slug, canonical, type } if the actor matches a known registry
// entry, otherwise a derived stub from the raw string.
function normalizeActor(raw, aliases) {
  const stripped = raw.replace(/\s*\(.*?\)\s*$/, "").trim(); // drop parenthetical role
  const lc = stripped.toLowerCase();
  for (const entry of aliases) {
    if (entry.canonical.toLowerCase() === lc) {
      return { slug: entry.slug, canonical: entry.canonical, type: entry.type || null, registered: true };
    }
    for (const alias of entry.aliases || []) {
      if (alias.toLowerCase() === lc) {
        return { slug: entry.slug, canonical: entry.canonical, type: entry.type || null, registered: true };
      }
    }
  }
  return { slug: slugify(stripped), canonical: stripped, type: null, registered: false };
}

// Score how related two entries are. Used for see-also auto-derivation.
function relatednessScore(a, b) {
  if (a === b) return 0;
  let score = 0;
  const aAbuses = new Set(a.data.abuses || []);
  const bAbuses = new Set(b.data.abuses || []);
  for (const x of aAbuses) if (bAbuses.has(x)) score += 3;

  const aActors = new Set((a.data.actors || []).map((x) => slugify(x.replace(/\s*\(.*?\)\s*$/, ""))));
  const bActors = new Set((b.data.actors || []).map((x) => slugify(x.replace(/\s*\(.*?\)\s*$/, ""))));
  for (const x of aActors) if (bActors.has(x)) score += 2;

  // Temporal proximity: full points within 30 days, decaying out to 180 days.
  const dayMs = 24 * 60 * 60 * 1000;
  const days = Math.abs((new Date(a.data.date) - new Date(b.data.date)) / dayMs);
  if (days <= 30) score += 2;
  else if (days <= 90) score += 1;
  else if (days <= 180) score += 0.5;

  return score;
}

module.exports = function (eleventyConfig) {
  // ---- Global data: taxonomy ----
  const ideals = loadYaml("taxonomy/ideals.yaml");
  const abuses = loadYaml("taxonomy/abuses.yaml");
  const aliases = loadYaml("taxonomy/aliases.yaml");

  const idealBySlug = new Map(ideals.map((i) => [i.slug, i]));
  const abuseBySlug = new Map(abuses.map((a) => [a.slug, a]));

  // Validate the taxonomy itself: every abuse references a known ideal.
  for (const abuse of abuses) {
    if (!idealBySlug.has(abuse.ideal)) {
      throw new Error(`abuses.yaml: abuse "${abuse.slug}" references unknown ideal "${abuse.ideal}".`);
    }
  }

  eleventyConfig.addGlobalData("taxonomy", { ideals, abuses, aliases });

  // ---- Passthrough copy ----
  eleventyConfig.addPassthroughCopy({ "src/css": "css" });
  eleventyConfig.addPassthroughCopy({ "src/images": "images" });

  // ---- Collections ----

  // All entries, sorted newest first.
  eleventyConfig.addCollection("entries", function (collectionApi) {
    const all = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    // Pre-load episode slugs for cross-reference validation.
    const episodeSlugs = new Set(
      collectionApi.getFilteredByGlob("src/content/episodes/*.md").map((e) =>
        e.data.slug || path.basename(e.inputPath, ".md")
      )
    );

    // Schema validation.
    for (const entry of all) {
      const slug = entry.data.slug || entry.fileSlug;

      // Abuses must exist in the taxonomy.
      for (const a of entry.data.abuses || []) {
        if (!abuseBySlug.has(a)) {
          throw new Error(`Entry "${slug}": unknown abuse "${a}". Add it to taxonomy/abuses.yaml or fix the entry.`);
        }
      }

      // Episode references must exist.
      for (const epSlug of entry.data.episodes || []) {
        if (!episodeSlugs.has(epSlug)) {
          throw new Error(`Entry "${slug}": references unknown episode "${epSlug}". Add it to src/content/episodes/ or fix the entry.`);
        }
      }

      // Sourcing rule: at least one primary source OR two independent investigative sources.
      const sources = entry.data.sources || [];
      const primaries = sources.filter((s) => s.tier === "primary").length;
      const investigatives = sources.filter((s) => s.tier === "investigative").length;
      if (primaries < 1 && investigatives < 2) {
        throw new Error(
          `Entry "${slug}": insufficient sourcing. Requires at least 1 primary source OR 2 investigative sources.`
        );
      }
    }

    all.sort((a, b) => new Date(b.data.date) - new Date(a.data.date));
    return all;
  });

  // Episodes: named compound real-world happenings that contain multiple entries.
  // Each episode is a Markdown file at src/content/episodes/<slug>.md that renders
  // as its own page. Entries reference episodes via the `episodes:` frontmatter field.
  eleventyConfig.addCollection("episodes", function (collectionApi) {
    const items = collectionApi.getFilteredByGlob("src/content/episodes/*.md");

    // Validate each episode.
    for (const item of items) {
      const fname = path.basename(item.inputPath, ".md");
      const slug = item.data.slug || fname;

      if (!item.data.title) {
        throw new Error(`Episode "${slug}": missing required "title" frontmatter.`);
      }
      if (!item.data.start_date) {
        throw new Error(`Episode "${slug}": missing required "start_date" frontmatter.`);
      }
      // Editorial overview body is required — an episode without overview is just a tag.
      const body = (item.template && item.template.frontMatter && item.template.frontMatter.content) || "";
      if (body.trim().length === 0) {
        throw new Error(`Episode "${slug}": missing required editorial overview body content.`);
      }
    }

    return items.sort((a, b) => new Date(b.data.start_date) - new Date(a.data.start_date));
  });

  // Map: episode slug -> array of entries that reference it, sorted chronologically.
  eleventyConfig.addCollection("entriesByEpisode", function (collectionApi) {
    const entries = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    const map = {};
    for (const entry of entries) {
      for (const epSlug of entry.data.episodes || []) {
        if (!map[epSlug]) map[epSlug] = [];
        map[epSlug].push(entry);
      }
    }
    for (const slug in map) {
      map[slug].sort((a, b) => new Date(a.data.date) - new Date(b.data.date));
    }
    return map;
  });

  // Map: episode slug -> episode object (for entry templates to look up titles).
  eleventyConfig.addCollection("episodeBySlug", function (collectionApi) {
    const items = collectionApi.getFilteredByGlob("src/content/episodes/*.md");
    const map = {};
    for (const item of items) {
      const slug = item.data.slug || path.basename(item.inputPath, ".md");
      map[slug] = item;
    }
    return map;
  });

  // Ideals: each ideal object with its rolled-up entries attached.
  eleventyConfig.addCollection("idealsWithEntries", function (collectionApi) {
    const entries = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    return ideals.map((ideal) => {
      const idealAbuses = abuses.filter((a) => a.ideal === ideal.slug);
      const idealAbuseSlugs = new Set(idealAbuses.map((a) => a.slug));
      const idealEntries = entries
        .filter((e) => (e.data.abuses || []).some((a) => idealAbuseSlugs.has(a)))
        .sort((a, b) => new Date(b.data.date) - new Date(a.data.date));
      return { ...ideal, abuses: idealAbuses, entries: idealEntries };
    });
  });

  // Abuses: each abuse object with its entries and parent ideal attached.
  eleventyConfig.addCollection("abusesWithEntries", function (collectionApi) {
    const entries = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    return abuses.map((abuse) => {
      const abuseEntries = entries
        .filter((e) => (e.data.abuses || []).includes(abuse.slug))
        .sort((a, b) => new Date(b.data.date) - new Date(a.data.date));
      const ideal = idealBySlug.get(abuse.ideal);
      return { ...abuse, ideal, entries: abuseEntries };
    });
  });

  // Actors: normalize via aliases.yaml, count entries, generate pages only for
  // actors meeting the threshold (default 3).
  const ACTOR_PAGE_THRESHOLD = 3;
  eleventyConfig.addCollection("actorsWithEntries", function (collectionApi) {
    const entries = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    const byActor = new Map();
    for (const entry of entries) {
      const seen = new Set();
      for (const raw of entry.data.actors || []) {
        const a = normalizeActor(raw, aliases);
        if (seen.has(a.slug)) continue; // dedupe within an entry
        seen.add(a.slug);
        if (!byActor.has(a.slug)) {
          byActor.set(a.slug, { ...a, entries: [] });
        }
        byActor.get(a.slug).entries.push(entry);
      }
    }
    // Threshold filter, sort.
    return [...byActor.values()]
      .filter((a) => a.entries.length >= ACTOR_PAGE_THRESHOLD)
      .map((a) => ({
        ...a,
        entries: a.entries.sort((x, y) => new Date(y.data.date) - new Date(x.data.date)),
      }))
      .sort((a, b) => b.entries.length - a.entries.length);
  });

  // see-also auto-derivation: attach to each entry at build time.
  // We expose it as a collection of { entry, seeAlso: [...] } pairs so templates can look it up.
  eleventyConfig.addCollection("seeAlsoMap", function (collectionApi) {
    const entries = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    const map = {};
    for (const e of entries) {
      const slug = e.data.slug || e.fileSlug;
      const overrides = (e.data.relationships && e.data.relationships["see-also-override"]) || [];
      if (overrides.length > 0) {
        map[slug] = overrides;
        continue;
      }
      const scored = entries
        .map((o) => ({ o, score: relatednessScore(e, o) }))
        .filter((p) => p.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 5);
      map[slug] = scored.map((p) => p.o.data.slug || p.o.fileSlug);
    }
    return map;
  });

  // Ideal explainers: long-form prose for each ideal, keyed by ideal slug.
  // Source files live under src/content/ideals/<slug>.md with permalink: false
  // (so they don't produce their own pages). We pull their rendered HTML into
  // the ideal page templates.
  eleventyConfig.addCollection("explainersBySlug", function (collectionApi) {
    const items = collectionApi.getFilteredByGlob("src/content/ideals/*.md");
    const map = {};
    for (const item of items) {
      const slug = item.data.slug || path.basename(item.inputPath, ".md");
      map[slug] = item;
    }
    return map;
  });

  // Abuse explainers: same pattern as ideal explainers, but for the specific
  // abuses. Source files live under src/content/abuses/<slug>.md.
  eleventyConfig.addCollection("abuseExplainersBySlug", function (collectionApi) {
    const items = collectionApi.getFilteredByGlob("src/content/abuses/*.md");
    const map = {};
    for (const item of items) {
      const slug = item.data.slug || path.basename(item.inputPath, ".md");
      map[slug] = item;
    }
    return map;
  });

  // ---- Filters ----
  eleventyConfig.addFilter("formatDate", (d) => {
    const dt = new Date(d);
    return dt.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: "UTC",
    });
  });

  eleventyConfig.addFilter("isoDate", (d) => {
    return new Date(d).toISOString().slice(0, 10);
  });

  eleventyConfig.addFilter("slugify", slugify);

  eleventyConfig.addFilter("abuseTitle", (slug) => {
    const a = abuseBySlug.get(slug);
    return a ? a.title : slug;
  });

  eleventyConfig.addFilter("idealForAbuse", (slug) => {
    const a = abuseBySlug.get(slug);
    return a ? idealBySlug.get(a.ideal) : null;
  });

  // Take the first N elements of an array. Nunjucks' built-in `slice` is a
  // chunker, not a head filter, so we add our own.
  eleventyConfig.addFilter("head", (arr, n) => {
    if (!Array.isArray(arr)) return arr;
    return arr.slice(0, n);
  });

  // ---- Markdown ----
  // (Defaults are fine; tighten later if needed.)

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    templateFormats: ["md", "njk", "html"],
  };
};
