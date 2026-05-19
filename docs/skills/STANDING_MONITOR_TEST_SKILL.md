# The Standing: Monitor Test Skill

## Purpose
Execute the full standing monitor logic (real news search, comprehensive research, taxonomy matching) but output results to a markdown file instead of creating GitHub issues. Allows testing and tweaking without filing fake issues.

## Execution

**Run a test monitoring scan:**

```bash
python3 docs/scripts/standing-monitor-test-run.py 10
```

The argument specifies the number of articles to fetch and evaluate (default: 10). Results are automatically saved to `docs/scripts/outputs/standing-monitoring-issues-TIMESTAMP.md`.

**What the script does:**

1. Load ideals and abuses from `/taxonomy/ideals.yaml` and `/taxonomy/abuses.yaml`
2. Load monitoring sources from `/taxonomy/sources.yaml` (the same sources used by the live monitoring system)
3. Fetch recent stories from configured RSS feeds
4. For each story found:
   - Evaluate relevance using Claude agent-based semantic analysis (not pattern matching)
   - If relevant: identify which abuses from the taxonomy it describes
   - Assess confidence level (high/medium/low)
5. Save results to markdown file with:
   - Each story's headline, source, URL, publication date
   - Relevance assessment (which ideals/abuses matched)
   - Confidence level
   - Proposed GitHub issue format (for review before publishing)
6. Report summary: stories evaluated, relevant hits, evaluation method

## Output Format

Results are saved to `docs/scripts/outputs/standing-monitoring-issues-TIMESTAMP.md` with:

```markdown
# Standing Monitoring Test Results

**Generated:** YYYY-MM-DD HH:MM
**Stories evaluated:** N
**Evaluation method:** Agent-based semantic analysis

---

## Story 1: [Headline]

**Source:** [Outlet name]
**Date:** [Publication date]

**Summary:** [Story description]

### ✓ RELEVANT

**Confidence:** high/medium/low
**Matched abuses:** abuse-slug-1, abuse-slug-2

**Generated issue body:**

```markdown
[Full proposed GitHub issue with Jurisdiction, Location, Actors, Mapped abuses, Evidence, Analysis]
```

---

## Story 2: [Headline]
...

---

## Summary

- **Stories evaluated:** N
- **Relevant:** N
- **Relevance rate:** N%
- **Evaluation method:** Agent-based semantic analysis
```

## Usage Notes

- **Test without creating issues**: Results stay in markdown, nothing is filed or published
- **Same sources as production**: Test uses the same `taxonomy/sources.yaml` as the live monitoring system, so you're testing against real sources
- **Agent-based evaluation**: Uses Claude semantic analysis, not pattern matching, to evaluate relevance
- **Review before publishing**: Results include proposed GitHub issue bodies for editorial review before filing
- **Iterate on taxonomy**: If the evaluation seems off on a story, it suggests the taxonomy might need refinement or that Claude's interpretation was reasonable but different from expected
- **No duplicates check**: The test version doesn't check for existing issues (the live version does)

## When to Publish

Once you're satisfied with:
1. Relevance assessments are accurate (agent is evaluating correctly)
2. Abuses are mapped correctly to The Standing's taxonomy
3. Proposed issue format looks good
4. You're confident in the sources

Then run the live monitoring system (`standing-monitor`) to create actual GitHub issues. The live version will:
- Check for duplicates in open/closed issues
- File issues directly to the repository
- Apply appropriate labels
- Trigger editorial workflow
