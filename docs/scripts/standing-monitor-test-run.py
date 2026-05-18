#!/usr/bin/env python3
"""
The Standing: Monitor Test Run
Tests the automated news monitoring workflow with agent-based evaluation.
Uses the same STANDING_MONITOR_SKILL.md evaluation approach as scheduled tasks,
but outputs results to markdown instead of creating GitHub issues.
"""

import yaml
import sys
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import html as html_module
import json

def load_taxonomy():
    """Load ideals and abuses from taxonomy files."""
    try:
        with open("taxonomy/ideals.yaml", "r") as f:
            ideals = yaml.safe_load(f)
        with open("taxonomy/abuses.yaml", "r") as f:
            abuses = yaml.safe_load(f)
        return ideals, abuses
    except FileNotFoundError as e:
        print(f"Error: Could not load taxonomy files: {e}")
        return None, None

def load_sources():
    """Load monitoring sources from taxonomy."""
    try:
        with open("taxonomy/sources.yaml", "r") as f:
            sources_data = yaml.safe_load(f)
        # Extract RSS feeds from sources
        feeds = []
        for category, sources_list in sources_data.items():
            for source in sources_list:
                if source.get("rss_feed"):
                    feeds.append((source["name"], source["rss_feed"]))
        return feeds
    except FileNotFoundError as e:
        print(f"Warning: Could not load sources: {e}")
        # Fallback to default feeds if sources.yaml not found
        return [
            ("NPR", "https://feeds.npr.org/1001/rss.xml"),
            ("Reuters US", "https://feeds.reuters.com/reuters/businessNews"),
        ]

def fetch_url(url):
    """Fetch content from URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Warning: Could not fetch {url}: {e}")
        return None

def parse_rss(content, limit=10):
    """Parse RSS feed and extract stories."""
    stories = []
    try:
        root = ET.fromstring(content)
        items = root.findall('.//item')
        
        for item in items[:limit]:
            title = item.findtext('title', 'Untitled')
            description = item.findtext('description', '')
            link = item.findtext('link', '')
            pubDate = item.findtext('pubDate', '')
            
            # Clean HTML from description
            description = description.replace('<![CDATA[', '').replace(']]>', '')
            description = re.sub('<[^<]+?>', '', description)
            description = html_module.unescape(description)
            
            if title and link:
                stories.append({
                    'title': title,
                    'description': description[:500] if description else title,
                    'url': link,
                    'date': pubDate,
                    'source': 'RSS Feed'
                })
        return stories
    except Exception as e:
        print(f"  Warning: Could not parse RSS: {e}")
        return []

def evaluate_story_with_claude(title, description, ideals, abuses):
    """
    Evaluate story using Claude agent-based semantic analysis.
    Same evaluation as the real monitoring skill.
    """
    import anthropic

    # Build taxonomy reference for the prompt
    abuse_list = "\n".join([f"- {a['slug']}: {a['title']} ({a['ideal']})" for a in abuses])

    prompt = f"""You are evaluating a news story against The Standing's taxonomy of democratic ideals and abuses.

Story Title: {title}
Story Summary: {description}

Available Abuses (slug: title (ideal)):
{abuse_list}

Evaluate this story:
1. Is this story about an anti-democratic action or abuse? (yes/no)
2. If yes, which abuse(s) from the list does it describe? (list slugs)
3. Confidence level (high/medium/low)
4. Brief explanation

Return ONLY valid JSON (no other text):
{{"relevant": bool, "abuses": ["slug1", "slug2"], "confidence": "high/medium/low", "explanation": "text"}}"""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    response_text = message.content[0].text

    # Parse JSON response
    import json
    result = json.loads(response_text)
    return {
        "relevant": result.get("relevant", False),
        "abuses": result.get("abuses", []),
        "confidence": result.get("confidence", "low"),
        "explanation": result.get("explanation", "")
    }

def generate_github_issue_body(story, evaluation, abuses, scan_date):
    """Generate the GitHub issue body markdown."""
    if not evaluation["relevant"] or not evaluation["abuses"]:
        return None
    
    # Get full abuse info
    abuse_objects = [a for a in abuses if a["slug"] in evaluation["abuses"]]
    if not abuse_objects:
        return None
    
    body = "## Automated News Monitoring\n\n"
    body += f"**Source:** {story['source']}\n"
    body += f"**Date:** {scan_date}\n"
    body += f"**Event date:** {story['date']}\n\n"
    body += "### What happened\n"
    body += f"{story['description'][:300]}\n\n"
    body += "### Jurisdiction\n"
    body += "[Determine from sources]\n\n"
    body += "### Location\n"
    body += "[Determine from sources]\n\n"
    body += "### Actors involved\n"
    body += "- [To be researched]\n\n"
    body += "### Mapped abuses\n"
    for abuse in abuse_objects:
        body += f"- `{abuse['slug']}` ({abuse['title']})\n"
    body += "\n### Evidence\n"
    body += "**Primary:**\n"
    body += f"- [{story['source']}]({story['url']})\n\n"
    body += "**Secondary:**\n"
    body += "- [To be researched during editorial review]\n\n"
    body += "### Analysis\n"
    primary_abuse = abuse_objects[0] if abuse_objects else None
    if primary_abuse:
        body += f"Event appears to describe {primary_abuse['title']}.\n"
    body += "Comprehensive research and source verification needed before entry recording.\n\n"
    body += "---\n"
    body += "*Created by The Standing's automated news monitoring system.*"
    
    return body

def main():
    articles = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    output_dir = "docs/scripts/outputs"
    os.makedirs(output_dir, exist_ok=True)
    scan_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    print(f"Loading taxonomy...")
    ideals, abuses = load_taxonomy()

    if ideals is None:
        print("Failed to load taxonomy")
        sys.exit(1)

    print(f"Loading monitoring sources...")
    feeds = load_sources()

    if not feeds:
        print("No RSS feeds found in sources")
        sys.exit(1)
    
    all_stories = []
    
    print(f"Fetching news from {len(feeds)} sources...")
    for source_name, feed_url in feeds:
        print(f"  Checking {source_name}...", end=" ")
        content = fetch_url(feed_url)
        if content:
            stories = parse_rss(content, limit=5)
            all_stories.extend([(s, source_name) for s in stories])
            print(f"found {len(stories)} stories")
        else:
            print("failed")
    
    # Mix in sample stories as fallback
    if len(all_stories) < articles:
        print(f"Adding sample stories for testing...")
        fallback_stories = [
            {
                "title": "Federal Judge Rules Executive Order Exceeds Presidential Authority",
                "description": "A federal court determined that an executive order exceeded constitutional limits and violated separation of powers.",
                "url": "https://example.com/article1",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "source": "Sample",
            },
            {
                "title": "Election Official Faces Threats After Certifying Results",
                "description": "State election director reports receiving threats after certifying election results.",
                "url": "https://example.com/article2",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "source": "Sample",
            },
        ]
        all_stories.extend([(s, "Sample") for s in fallback_stories])
    
    stories = [s[0] for s in all_stories[:articles]]
    
    print(f"Evaluating {len(stories)} stories using agent-based evaluation...")
    
    results = []
    for story in stories:
        evaluation = evaluate_story_with_claude(story["title"], story["description"], ideals, abuses)
        issue_body = None
        
        if evaluation["relevant"]:
            issue_body = generate_github_issue_body(story, evaluation, abuses, scan_date)
        
        results.append({
            "story": story,
            "evaluation": evaluation,
            "issue_body": issue_body
        })
    
    # Generate markdown output
    output = f"# Standing Monitoring Test Results\n\n"
    output += f"**Generated:** {scan_date}\n"
    output += f"**Stories evaluated:** {len(stories)}\n"
    output += f"**Evaluation method:** Agent-based semantic analysis\n\n"
    output += "---\n\n"
    
    relevant_count = 0
    
    for i, result in enumerate(results, 1):
        story = result["story"]
        evaluation = result["evaluation"]
        issue_body = result["issue_body"]
        
        output += f"## Story {i}: {story['title']}\n\n"
        output += f"**Source:** {story['source']}\n"
        output += f"**Date:** {story['date']}\n\n"
        output += f"**Summary:** {story['description']}\n\n"
        
        if evaluation["relevant"]:
            relevant_count += 1
            output += f"### ✓ RELEVANT\n\n"
            output += f"**Confidence:** {evaluation['confidence']}\n"
            output += f"**Matched abuses:** {', '.join(evaluation['abuses'])}\n\n"
            
            if issue_body:
                output += "**Generated issue body:**\n\n"
                output += "```markdown\n"
                output += issue_body
                output += "\n```\n\n"
        else:
            output += f"### ✗ Not relevant\n\n"
        
        output += "---\n\n"
    
    output += f"## Summary\n\n"
    output += f"- **Stories evaluated:** {len(stories)}\n"
    output += f"- **Relevant:** {relevant_count}\n"
    if len(stories) > 0:
        output += f"- **Relevance rate:** {100*relevant_count//len(stories)}%\n"
    output += f"- **Evaluation method:** Agent-based semantic analysis (simulated)\n"
    
    # Write output
    output_file = f"{output_dir}/standing-monitoring-issues-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"✓ Test complete")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Relevant stories: {relevant_count}/{len(stories)}")

if __name__ == "__main__":
    main()
