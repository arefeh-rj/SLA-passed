from __future__ import annotations

import os
import csv
import requests
from typing import Dict, Iterable, List, Optional
from dotenv import load_dotenv

# -----------------
# Config / Defaults
# -----------------
FIELDS = "key,summary,status,assignee,priority"
PAGE_SIZE = 100
TIMEOUT = 30  # seconds


def _load_env() -> tuple[str, tuple[str, str]]:
    """Load BASE and AUTH from environment (using python-dotenv)."""
    load_dotenv()
    base = os.environ["JIRA_URL"]
    auth = (os.environ["JIRA_USERNAME"], os.environ["JIRA_PASSWORD"])
    return base, auth


def _build_session(auth: tuple[str, str]) -> requests.Session:
    """Create a session with JSON headers and basic auth."""
    s = requests.Session()
    s.auth = auth
    s.headers.update({"Accept": "application/json"})
    return s


# -----------------
# Core functionality
# -----------------
def fetch_jira_issues(
    jql: str,
    fields: str = FIELDS,
    page_size: int = PAGE_SIZE,
    *,
    base_url: Optional[str] = None,
    session: Optional[requests.Session] = None,
) -> List[Dict]:
    """
    Run a JQL search and return all matching issues (raw JSON objects), handling pagination.

    Usage:
        issues = fetch_jira_issues(JQL)

    You can pass your own session/base_url if you need to customize auth or headers.
    """
    # bootstrap env/session if not provided
    if base_url is None or session is None:
        base, auth = _load_env()
        base_url = base_url or base
        session = session or _build_session(auth)

    # 1) Get total count
    r0 = session.get(f"{base_url}/rest/api/2/search", params={"jql": jql, "maxResults": 0}, timeout=TIMEOUT)
    r0.raise_for_status()
    total = int(r0.json().get("total", 0))

    # 2) Collect all issues (paginated)
    all_issues: List[Dict] = []
    start = 0
    while start < total:
        r = session.get(
            f"{base_url}/rest/api/2/search",
            params={"jql": jql, "startAt": start, "maxResults": page_size, "fields": fields},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        chunk = r.json().get("issues", []) or []
        if not chunk:
            break
        all_issues.extend(chunk)
        start += len(chunk)

    return all_issues


def flatten_issue(issue: Dict) -> Dict[str, str]:
    """Extract the fields we care about for CSV writing."""
    f = issue.get("fields", {}) or {}
    return {
        "key": issue.get("key", ""),
        "summary": f.get("summary", "") or "",
        "status": (f.get("status") or {}).get("name", "") or "",
        "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned") or "Unassigned",
        "priority": (f.get("priority") or {}).get("name", "") or "",
    }


def write_issues_csv(issues: Iterable[Dict], csv_path: str = "jira_results.csv") -> None:
    """
    Write a compact CSV with one row per issue.
    Pass in the raw issues you got from fetch_jira_issues().
    """
    fieldnames = ["key", "summary", "status", "assignee", "priority"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for issue in issues:
            w.writerow(flatten_issue(issue))


# -----------------
# Example usage
# -----------------
if __name__ == "__main__":
    JQL = (
        'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
        'AND status in ("In Progress - 2", "In Progress - 3") '
        'AND "Time to resolution" < remaining("1h") '
        'AND cf[18502] = "TO" '
        'AND status CHANGED AFTER -1d'
    )

    issues = fetch_jira_issues(JQL, fields=FIELDS, page_size=PAGE_SIZE)
    # print(issues)
    print(f"Fetched {len(issues)} issues")
    # Only write CSV when/if you want:
    write_issues_csv(issues, "jira_results.csv")
