#!/usr/bin/env python3
"""
The Standing: Monitor Test - URL Version
Test the monitoring system against real RSS feeds or web pages.
Outputs to markdown instead of creating GitHub issues.
"""

import yaml
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

def load_taxonomy():
    """Load ideals and abuses from taxonomy files."""
    with open("taxonomy/ideals.yaml") as f:
        ideals = yaml.safe_load(f)
    with open("taxonomy/abuses.yaml") as f:
        abuses = yaml.safe_load(f)
    return ideals, abuses

def fetch_url(url):
    """Fetch content from URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_rss(content, limit=5):
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

            description = description.replace('<![CDATA[', '').replace(']]>', '')
            import re
            description = re.sub('<[^<]+?>', '', description)

            stories.append({
                'title': title,
                'description': description[:500],
                'url': link,
                'date': pubDate,
                'source': 'RSS Feed'
            })
        return stories
    except Exception as e:
        print(f"Error parsing RSS: {e}")
        return []

def parse_html(content, limit=5):
    """Extract potential stories from HTML page."""
    stories = []
    try:
        import re
        headings = re.findall(r'<h[123][^>]*>([^<]+)</h[123]>', content)
        paragraphs = re.findall(r'<p[^>]*>([^<]+)</p>', content)

        for i, heading in enumerate(headings[:limit]):
            description = paragraphs[i] if i < len(paragraphs) else ''
            import html
            heading = html.unescape(heading)
            description = html.unescape(description)

            stories.append({
                'title': heading.strip()[:200],
                'description': description.strip()[:500],
                'url': '[URL provided]',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Web Page'
            })

        return stories
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return []

def is_rss(content):
    """Check if content looks like RSS."""
    return '<rss' in content.lower() or '<feed' in content.lower()

def evaluate_relevance(headline, summary, abuses):
    """Match story against abuse patterns."""
    text = f"{headline} {summary}".lower()
    matches = []

    patterns = {
        "executive-overreach": ["executive order", "exceeded authority", "exceeds authority", "executive power"],
        "election-worker-intimidation": ["election official", "election worker", "poll worker", "threats"],
        "election-denial": ["election denial", "election fraud"],
        "excessive-force-by-law-enforcement": ["excessive force", "unnecessary force", "police violence"],
        "press-retaliation": ["journalist arrested", "reporter arrested", "press retaliation"],
        "prosecution-of-journalists": ["journalist prosecuted", "reporter prosecuted"],
        "defying-subpoenas": ["subpoena", "refused to comply"],
        "voter-suppression": ["voter suppression", "voting restrictions", "ballot access", "voting rights act", "voting rights"],
        "selective-prosecution": ["selective prosecution", "political prosecution", "irs lawsuit", "weaponization"],
        "nepotism": ["family member", "relative appointed"],
    }

    for slug, keywords in patterns.items():
        if any(kw in text for kw in keywords):
            abuse = next((a for a in abuses if a["slug"] == slug), None)
            if abuse:
                matches.append((slug, abuse["title"], abuse["ideal"]))

    return matches

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 monitor-test-url.py <URL> [limit]")
        print("  URL: RSS feed or web page URL")
        print("  limit: number of stories to test (default: 5)")
        sys.exit(1)

    url = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"Loading taxonomy...")
    abuses = load_taxonomy()[1]

    print(f"Fetching {url}...")
    content = fetch_url(url)
    if not content:
        print("Failed to fetch URL")
        sys.exit(1)

    if is_rss(content):
        print("Detected RSS feed...")
        stories = parse_rss(content, limit)
    else:
        print("Detected HTML page...")
        stories = parse_html(content, limit)

    if not stories:
        print("No stories extracted from URL")
        sys.exit(1)

    print(f"Found {len(stories)} stories, generating report...")

    output = f"# Standing Monitor Test Report\n\n"
    output += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    output += f"**Source URL:** {url}\n"
    output += f"**Stories extracted:** {len(stories)}\n\n---\n\n"

    relevant = 0
    for i, story in enumerate(stories, 1):
        matches = evaluate_relevance(story['title'], story['description'], abuses)

        output += f"## Story {i}: {story['title']}\n\n"
        output += f"**Source:** {story['source']}\n"
        output += f"**URL:** {story['url']}\n"
        output += f"**Date:** {story['date']}\n\n"
        output += f"**Summary:** {story['description']}\n\n"

        if matches:
            relevant += 1
            output += f"### ✓ RELEVANT ({len(matches)} match)\n\n"
            output += f"**Primary ideal:** {matches[0][2]}\n\n"
            output += f"**Matched abuses:**\n"
            for slug, title, ideal in matches:
                output += f"- `{slug}` — {title}\n"
            output += "\n**Research needed:**\n"
            output += "- Verify event date and jurisdiction\n"
            output += "- Identify specific actors/officials\n"
            output += "- Find corroborating sources\n"
            output += "- Determine location\n"
            output += f"- Potential slug: `issue-[#]-[jurisdiction]-{matches[0][0]}`\n\n"
        else:
            output += "### ✗ Not relevant\n\n"

        output += "---\n\n"

    output += f"## Summary\n\n"
    output += f"- **Stories evaluated:** {len(stories)}\n"
    output += f"- **Relevant:** {relevant}\n"
    if len(stories) > 0:
        output += f"- **Relevance rate:** {100*relevant//len(stories)}%\n"

    import os
    output_dir = "docs/scripts/outputs"
    os.makedirs(output_dir, exist_ok=True)
    fname = f"{output_dir}/standing-monitor-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    with open(fname, 'w') as f:
        f.write(output)

    print(f"Report saved to: {fname}")

main()
