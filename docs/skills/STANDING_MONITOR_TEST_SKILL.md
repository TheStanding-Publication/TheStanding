# The Standing: Monitor Test Skill

## Purpose
Execute the full standing monitor logic (real news search, comprehensive research, taxonomy matching) but output results to a markdown file instead of creating GitHub issues. Allows testing and tweaking without filing fake issues.

## Execution

**Run a test monitoring scan:**

```bash
claude-code run standing-monitor-test-run --articles 10 --output standing-test-results.md
```

Or from this skill:
1. Load ideals and abuses from `/taxonomy/ideals.yaml` and `/taxonomy/abuses.yaml`
2. Search major news outlets for recent stories (NYT, WaPo, NPR, AP, Reuters, BBC)
3. For each story found:
   - Evaluate relevance against taxonomy
   - If relevant: gather comprehensive event data (date, actors, jurisdiction, location, evidence, abuses)
   - Check for duplicates in repo (optional, for reference)
4. Save results to markdown file with:
   - Each story's headline, source, URL
   - Relevance assessment (which ideals/abuses matched)
   - Comprehensive event data gathered
   - Proposed GitHub issue format (for review before publishing)
5. Report summary: stories evaluated, relevant hits, duplicate warnings

## Output Format

```markdown
# Standing Monitor Test Results

**Scan date:** YYYY-MM-DD HH:MM
**News sources:** NYT, WaPo, NPR, AP, Reuters, BBC
**Stories evaluated:** N
**Relevant stories found:** N

---

## Story 1: [Headline]

**Source:** [Outlet name]
**URL:** [URL]
**Date:** [Publication date]

### Relevance Assessment
Matches: [ideal-1], [ideal-2]
Confidence: [high/medium/low]

### Comprehensive Event Data

**Event description:** [What happened]
**Event date:** YYYY-MM-DD
**Jurisdiction:** [federal/state/local/international/private]
**Location:** [City, State or State]
**Actors:** [Named individuals and organizations]
**Abuses:** [Mapped abuse slugs]
**Evidence:**
- Primary: [URL]
- Secondary: [URL]

### Proposed GitHub Issue

[Shows what the issue would look like if published]

---

## Usage Notes

- **Test without creating issues**: Results stay in markdown, nothing commits
- **Iterate on taxonomy matching**: Review relevance assessments, adjust if needed
- **Review comprehensive data**: Check if all required fields are captured correctly
- **Validate actors/evidence**: Verify sources are correct before publishing
- **Check duplicate warnings**: See if similar entries already exist in the repo

## When to Publish

Once you're satisfied with:
1. Relevance matching is correct
2. Event data is comprehensive and accurate
3. No concerning duplicates
4. Proposed issue format looks good

Then run the live monitoring system to create actual GitHub issues.
