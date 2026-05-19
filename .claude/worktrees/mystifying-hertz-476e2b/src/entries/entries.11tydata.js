// Applies to every Markdown file under src/entries/.
// Sets the layout and computes the permalink from the entry's `date` + `slug`.

module.exports = {
  layout: "layouts/entry.njk",
  permalink: function (data) {
    if (!data.date) return false;
    if (!data.slug) {
      throw new Error(
        `Entry ${data.page && data.page.inputPath}: missing required "slug" frontmatter field.`
      );
    }
    const d = new Date(data.date);
    const yyyy = d.getUTCFullYear();
    const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
    const dd = String(d.getUTCDate()).padStart(2, "0");
    return `/entries/${yyyy}/${mm}/${dd}/${data.slug}/`;
  },
  eleventyComputed: {
    title: (data) => data.headline,
  },
};
