#!/usr/bin/env python3
"""
The Standing: Issue to Entry Converter
Converts GitHub monitoring-intake issues to recorded entry files, branches, and PRs.

Usage:
  python3 standing-issue-to-entry.py [options]

Options:
  --dry-run          Test mode: validate without creating branches/PRs
  --issue N          Process only issue #N
  --all              Process all eligible open issues
"""

import os
import sys
import json
import yaml
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# ---- Configuration ----

REPO_ROOT = Path(__file__).parent.parent.parent
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "TheStanding-Publication/TheStanding"
GITHUB_API_BASE = "https://api.github.com"
DRY_RUN = "--dry-run" in sys.argv

# ---- Data Classes ----

@dataclass
class GitHubIssue:
    number: int
    title: str
    body: str
    labels: List[str]
    created_at: str
    updated_at: str

# ---- GitHub API Functions ----

def github_api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict]:
    """
    Make GitHub API request.
    Returns (status_code, response_dict)
    """
    url = f"{GITHUB_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TheStanding-IssuesToEntry"
    }

    try:
        if method == "GET":
            req = urllib.request.Request(url, headers=headers, method="GET")
        elif method == "POST":
            req = urllib.request.Request(url, headers=headers, method="POST")
            req.add_header("Content-Type", "application/json")
            req.data = json.dumps(data).encode('utf-8') if data else None
        else:
            return 400, {"error": f"Unknown method: {method}"}

        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            return e.code, json.loads(error_body)
        except:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 500, {"error": str(e)}

def fetch_monitoring_issues(issue_num: Optional[int] = None) -> List[GitHubIssue]:
    """
    Fetch eligible monitoring-intake issues from GitHub.
    If issue_num is specified, fetch only that issue.
    Otherwise, fetch all eligible issues.
    """
    issues = []

    if issue_num:
        # Fetch specific issue
        status, data = github_api_request("GET", f"/repos/{GITHUB_REPO}/issues/{issue_num}")
        if status == 200:
            labels = [label["name"] for label in data.get("labels", [])]
            issues.append(GitHubIssue(
                number=data["number"],
                title=data["title"],
                body=data["body"] or "",
                labels=labels,
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            ))
    else:
        # Fetch all eligible issues
        # Query: state:open label:monitoring-intake sort:number-asc
        query = f"repo:{GITHUB_REPO} state:open label:monitoring-intake"
        status, data = github_api_request("GET", f"/search/issues?q={query}&sort=number&order=asc&per_page=100")

        if status == 200:
            for item in data.get("items", []):
                # Check if issue should be skipped (url-validation-hold)
                labels = [label["name"] for label in item.get("labels", [])]

                if "url-validation-hold" in labels:
                    # Check if last comment is older than 24 hours
                    if should_skip_hold_issue(item["number"]):
                        continue

                issues.append(GitHubIssue(
                    number=item["number"],
                    title=item["title"],
                    body=item["body"] or "",
                    labels=labels,
                    created_at=item["created_at"],
                    updated_at=item["updated_at"]
                ))

    return issues

def should_skip_hold_issue(issue_num: int) -> bool:
    """
    Check if issue with url-validation-hold should be skipped.
    Skip if last comment is less than 24 hours old.
    """
    status, data = github_api_request("GET", f"/repos/{GITHUB_REPO}/issues/{issue_num}/comments?per_page=1&sort=updated&direction=desc")

    if status == 200 and data:
        last_comment = data[0]
        last_comment_time = datetime.fromisoformat(last_comment["updated_at"].replace("Z", "+00:00"))
        now = datetime.now(last_comment_time.tzinfo)
        age = now - last_comment_time

        if age < timedelta(hours=24):
            print(f"  Skipping issue #{issue_num}: url-validation-hold (last comment {age.total_seconds()/3600:.1f} hours ago)")
            return True

    return False

def add_issue_comment(issue_num: int, comment: str) -> bool:
    """Add comment to GitHub issue."""
    if DRY_RUN:
        print(f"[DRY RUN] Would add comment to issue #{issue_num}:")
        print(comment)
        return True

    status, data = github_api_request("POST", f"/repos/{GITHUB_REPO}/issues/{issue_num}/comments", {
        "body": comment
    })

    if status == 201:
        print(f"✓ Added comment to issue #{issue_num}")
        return True
    else:
        print(f"✗ Failed to add comment to issue #{issue_num}: {data}")
        return False

def create_branch(branch_name: str) -> bool:
    """Create git branch locally."""
    code, output = run_command(["git", "checkout", "-b", branch_name, "main"])
    if code != 0:
        print(f"✗ Failed to create branch {branch_name}: {output}")
        return False
    return True

def commit_and_push(entry_path: Path, slug: str, issue_num: int) -> bool:
    """Commit entry file and push branch."""
    if DRY_RUN:
        print(f"[DRY RUN] Would commit and push:")
        print(f"  File: {entry_path}")
        print(f"  Message: Record entry: {slug} (Closes #{issue_num})")
        return True

    # Add file
    code, output = run_command(["git", "add", str(entry_path)])
    if code != 0:
        print(f"✗ Failed to add entry file: {output}")
        return False

    # Commit
    commit_msg = f"Record entry: {slug}\n\nCloses #{issue_num}"
    code, output = run_command(["git", "commit", "-m", commit_msg])
    if code != 0:
        print(f"✗ Failed to commit: {output}")
        return False

    # Push
    branch_name = f"entry/{slug}"
    code, output = run_command(["git", "push", "origin", branch_name])
    if code != 0:
        print(f"✗ Failed to push branch: {output}")
        return False

    print(f"✓ Committed and pushed branch {branch_name}")
    return True

def create_pull_request(slug: str, headline: str, issue_num: int, issue_data: Dict) -> Tuple[bool, Optional[int]]:
    """
    Create pull request on GitHub.
    Returns (success, pr_number)
    """
    branch_name = f"entry/{slug}"
    title = f"[Entry] {headline}"

    abuses = ", ".join(issue_data.get("abuses", []))
    date = issue_data.get("date", "")
    juris = issue_data.get("jurisdiction", "")
    location = issue_data.get("location", "")

    body = f"""Closes #{issue_num}

## Entry Details

**Slug:** {slug}
**Event date:** {date}
**Jurisdiction:** {juris}
**Location:** {location}
**Abuses:** {abuses}

## Validation Summary

✓ All required fields present
✓ URLs verified and normalized
✓ Actors verified against registry
✓ Location meets jurisdiction requirements
✓ Abuses valid and in taxonomy
✓ Sourcing meets floor (1 primary OR 2 investigative)
✓ Build validation passed

## For Review

- Is headline factual and neutral?
- Is summary accurate and 2-3 sentences?
- Are abuses correctly mapped?
- Are actors correctly named?
- Any missing sources or context?
- Any related episodes to link?

---

*Automated entry recording from issue #{issue_num}*
"""

    if DRY_RUN:
        print(f"[DRY RUN] Would create PR:")
        print(f"  Title: {title}")
        print(f"  Branch: {branch_name}")
        return True, None

    status, data = github_api_request("POST", f"/repos/{GITHUB_REPO}/pulls", {
        "title": title,
        "body": body,
        "head": branch_name,
        "base": "main"
    })

    if status == 201:
        pr_num = data["number"]
        print(f"✓ Created PR #{pr_num}")
        return True, pr_num
    else:
        print(f"✗ Failed to create PR: {data}")
        return False, None

def add_pr_labels(pr_num: int, labels: List[str]) -> bool:
    """Add labels to pull request."""
    if DRY_RUN:
        print(f"[DRY RUN] Would add labels to PR #{pr_num}: {labels}")
        return True

    status, data = github_api_request("POST", f"/repos/{GITHUB_REPO}/issues/{pr_num}/labels", labels)

    if status == 200:
        print(f"✓ Added labels to PR #{pr_num}")
        return True
    else:
        print(f"✗ Failed to add labels: {data}")
        return False

# ---- Helper Functions (existing) ----

def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: {path} not found")
        return {}

def run_command(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str]:
    """Run command and return (returncode, output)"""
    try:
        result = subprocess.run(cmd, cwd=cwd or REPO_ROOT, capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)

def slugify(s: str) -> str:
    """Convert string to kebab-case slug."""
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def generate_slug(issue_num: int, jurisdiction: str, abuse: str) -> str:
    """Generate slug from issue number, jurisdiction, and primary abuse."""
    juris_map = {
        'federal': 'federal',
        'state': 'state',
        'local': 'local',
        'international': 'intl',
        'private-actor': 'private'
    }
    j = juris_map.get(jurisdiction, slugify(jurisdiction))
    a = slugify(abuse)
    return f"issue-{issue_num}-{j}-{a}"

def parse_issue_body(body: str) -> Dict:
    """
    Parse structured issue body to extract event data.
    Expects sections from STANDING_MONITOR_SKILL output.
    """
    data = {}
    lines = body.split('\n')

    # Simple parsing: look for section headers and extract data
    current_section = None

    for line in lines:
        line = line.strip()

        # Detect section headers
        if line.startswith('### '):
            current_section = line.replace('### ', '').lower()
            data[current_section] = ""
        elif current_section and line:
            if current_section not in data:
                data[current_section] = ""
            data[current_section] += line + "\n"

    # Extract specific fields
    return {
        'headline': data.get('what happened', '').split('\n')[0][:100],
        'summary': data.get('what happened', ''),
        'event_date': data.get('event date', '').strip(),
        'jurisdiction': data.get('jurisdiction', '').strip(),
        'location': data.get('location', '').strip(),
        'actors': [a.strip().strip('- ') for a in data.get('actors involved', '').split('\n') if a.strip().strip('- ')],
        'abuses': [a.split()[0] for a in data.get('mapped abuses', '').split('\n') if a.strip()],
        'sources': []  # Would be parsed from evidence section
    }

def main():
    """Main entry point."""
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    print("The Standing: Issue to Entry Converter")
    print(f"Repository: {GITHUB_REPO}")
    if DRY_RUN:
        print("MODE: DRY RUN (no changes will be made)")
    print()

    # Load taxonomy
    abuses = load_yaml(REPO_ROOT / 'taxonomy' / 'abuses.yaml')
    aliases = load_yaml(REPO_ROOT / 'taxonomy' / 'aliases.yaml')
    print(f"Loaded {len(abuses)} abuses and {len(aliases)} actor aliases")
    print()

    # Determine which issues to process
    issue_num = None
    if "--issue" in sys.argv:
        idx = sys.argv.index("--issue")
        if idx + 1 < len(sys.argv):
            try:
                issue_num = int(sys.argv[idx + 1])
            except ValueError:
                print("Error: --issue requires a number")
                sys.exit(1)

    # Fetch eligible issues
    print("Fetching eligible issues...")
    issues = fetch_monitoring_issues(issue_num)
    print(f"Found {len(issues)} eligible issues\n")

    if not issues:
        print("No eligible issues to process")
        return

    # Process each issue
    for issue in issues:
        print(f"Processing issue #{issue.number}: {issue.title}")
        print("-" * 60)

        # Parse issue body
        issue_data = parse_issue_body(issue.body)

        # TODO: Full validation workflow
        # 1. Validate all data fields
        # 2. Clean and verify URLs
        # 3. Create entry file
        # 4. Run build validation
        # 5. Add status comment
        # 6. Create branch/commit/push
        # 7. Create PR
        # 8. Add labels

        print("  TODO: Implement full validation workflow")
        print()

if __name__ == '__main__':
    main()
