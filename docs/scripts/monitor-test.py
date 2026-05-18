#!/usr/bin/env python3
import yaml
import sys
from datetime import datetime

# Load taxonomy
with open("taxonomy/ideals.yaml") as f:
    ideals = yaml.safe_load(f)
with open("taxonomy/abuses.yaml") as f:
    abuses = yaml.safe_load(f)

articles = int(sys.argv[1]) if len(sys.argv) > 1 else 2

# Test stories
stories = [
    ("Federal Judge Rules Executive Order Exceeds Presidential Authority",
     "A federal court determined that an executive order exceeded constitutional limits and violated separation of powers."),
    ("Election Official Faces Threats After Certifying Results",
     "State election director reports receiving threats and harassment after certifying results despite pressure from losing candidate."),
    ("Police Department Sued for Excessive Force at Protest",
     "Multiple demonstrators file lawsuit alleging officers used excessive force during peaceful assembly."),
    ("Journalist Arrested While Covering Government Corruption",
     "Reporter detained by federal agents while investigating misconduct allegations. Press groups call it retaliation."),
    ("Congressional Subpoena Ignored by Executive Agency",
     "Federal agency refuses to comply with congressional subpoena demanding documents."),
]

# Abuse patterns for matching
patterns = {
    "executive-overreach": ["executive order", "exceeded authority", "exceeds authority"],
    "election-worker-intimidation": ["election official threat", "election worker threat"],
    "excessive-force-by-law-enforcement": ["excessive force", "unnecessary force"],
    "press-retaliation": ["journalist arrested", "reporter arrested", "retaliation"],
    "defying-subpoenas": ["subpoena", "refused to comply"],
}

# Generate report
output = f"# Standing Monitor Test Results\n\n"
output += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
output += f"**Test stories:** {articles}\n\n---\n\n"

relevant = 0
for i, (headline, summary) in enumerate(stories[:articles], 1):
    text = f"{headline} {summary}".lower()
    matches = []

    for slug, keywords in patterns.items():
        if any(kw in text for kw in keywords):
            abuse = next((a for a in abuses if a["slug"] == slug), None)
            if abuse:
                matches.append((slug, abuse["title"], abuse["ideal"]))

    output += f"## Story {i}: {headline}\n\n"
    output += f"**Summary:** {summary}\n\n"

    if matches:
        relevant += 1
        output += f"### ✓ RELEVANT ({len(matches)} abuse match)\n\n"
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
output += f"- **Stories evaluated:** {articles}\n"
output += f"- **Relevant:** {relevant}\n"
output += f"- **Rate:** {100*relevant//articles if articles else 0}%\n"

# Write file to docs/scripts/outputs/
import os
output_dir = "docs/scripts/outputs"
os.makedirs(output_dir, exist_ok=True)
fname = f"{output_dir}/standing-monitor-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
with open(fname, 'w') as f:
    f.write(output)

print(f"✓ Report: {fname}")
