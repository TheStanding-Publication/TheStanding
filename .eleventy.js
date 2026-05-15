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

    // Allowed values for enumerated fields, declared once for reuse + error messages.
    const ALLOWED_CONFIDENCE = ["confirmed", "well-reported", "developing", "alleged"];
    const ALLOWED_STATUS = ["draft", "published", "corrected", "retracted"];
    const ALLOWED_SOURCE_TIERS = ["primary", "investigative", "secondary"];
    const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

    // Schema validation.
    for (const entry of all) {
      const slug = entry.data.slug || entry.fileSlug;

      // --- Required frontmatter fields ---
      if (!entry.data.headline) {
        throw new Error(`Entry "${slug}": missing required "headline" frontmatter.`);
      }
      if (!entry.data.summary) {
        throw new Error(`Entry "${slug}": missing required "summary" frontmatter.`);
      }
      if (!entry.data.date) {
        throw new Error(`Entry "${slug}": missing required "date" frontmatter.`);
      }

      // --- Date format ---
      // YAML may parse dates as Date objects (when unquoted) or strings (when quoted).
      // Accept both, but if it's a string, require YYYY-MM-DD shape.
      if (typeof entry.data.date === "string" && !DATE_RE.test(entry.data.date)) {
        throw new Error(
          `Entry "${slug}": date "${entry.data.date}" must be in YYYY-MM-DD format.`
        );
      }

      // --- Confidence enum ---
      if (entry.data.confidence && !ALLOWED_CONFIDENCE.includes(entry.data.confidence)) {
        throw new Error(
          `Entry "${slug}": confidence "${entry.data.confidence}" must be one of: ${ALLOWED_CONFIDENCE.join(", ")}.`
        );
      }

      // --- Status enum ---
      if (entry.data.status && !ALLOWED_STATUS.includes(entry.data.status)) {
        throw new Error(
          `Entry "${slug}": status "${entry.data.status}" must be one of: ${ALLOWED_STATUS.join(", ")}.`
        );
      }

      // --- Abuses must exist in the taxonomy ---
      for (const a of entry.data.abuses || []) {
        if (!abuseBySlug.has(a)) {
          throw new Error(
            `Entry "${slug}": unknown abuse "${a}". Add it to taxonomy/abuses.yaml or fix the entry.`
          );
        }
      }

      // --- Episode references must exist ---
      for (const epSlug of entry.data.episodes || []) {
        if (!episodeSlugs.has(epSlug)) {
          throw new Error(
            `Entry "${slug}": references unknown episode "${epSlug}". Add it to src/content/episodes/ or fix the entry.`
          );
        }
      }

      // --- Source-level validation ---
      const sources = entry.data.sources || [];
      for (let i = 0; i < sources.length; i++) {
        const s = sources[i];
        if (!s.url) {
          throw new Error(`Entry "${slug}": source #${i + 1} missing required "url".`);
        }
        if (!s.publisher) {
          throw new Error(`Entry "${slug}": source #${i + 1} missing required "publisher".`);
        }
        if (!s.tier) {
          throw new Error(`Entry "${slug}": source #${i + 1} missing required "tier".`);
        }
        if (!ALLOWED_SOURCE_TIERS.includes(s.tier)) {
          throw new Error(
            `Entry "${slug}": source #${i + 1} tier "${s.tier}" must be one of: ${ALLOWED_SOURCE_TIERS.join(", ")}.`
          );
        }
      }

      // --- Sourcing rule: at least one primary source OR two independent investigative sources ---
      const primaries = sources.filter((s) => s.tier === "primary").length;
      const investigatives = sources.filter((s) => s.tier === "investigative").length;
      if (primaries < 1 && investigatives < 2) {
        throw new Error(
          `Entry "${slug}": insufficient sourcing. Requires at least 1 primary source OR 2 investigative sources.`
        );
      }

      // --- Quote length: editorial standard requires < 15 words ---
      if (entry.data.quote && entry.data.quote.text) {
        const wordCount = entry.data.quote.text.trim().split(/\s+/).filter(Boolean).length;
        if (wordCount >= 15) {
          throw new Error(
            `Entry "${slug}": quote text is ${wordCount} words; editorial standard requires fewer than 15.`
          );
        }
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

  // Feed entries: sorted by archived (publication) date descending — different from
  // the main `entries` collection which sorts by event date. Capped at 30 most
  // recent so the feed stays reasonably sized. Used by /feed.xml for RSS-to-email
  // delivery via Buttondown and for any other feed-reader subscribers.
  eleventyConfig.addCollection("feedEntries", function (collectionApi) {
    const all = collectionApi
      .getFilteredByGlob("src/entries/**/*.md")
      .filter((e) => e.data.status !== "draft");

    return all
      .sort((a, b) => {
        const dateA = new Date(a.data.archived || a.data.date);
        const dateB = new Date(b.data.archived || b.data.date);
        return dateB - dateA;
      })
      .slice(0, 30);
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

  // RFC 3339 / ISO 8601 date formatter for the Atom feed.
  eleventyConfig.addFilter("rfc3339", (d) => {
    if (!d) return new Date().toISOString();
    return new Date(d).toISOString();
  });

  // Returns the most recent archived date across a list of entries, formatted
  // as RFC 3339. Used for the feed's top-level <updated> element.
  eleventyConfig.addFilter("newestEntryDate", (entries) => {
    if (!entries || entries.length === 0) return new Date().toISOString();
    const dates = entries.map((e) => new Date(e.data.archived || e.data.date).getTime());
    return new Date(Math.max(...dates)).toISOString();
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
