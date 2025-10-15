# jira_tool_simple.py
import os
import sys
from typing import Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()

# --- Set this once and you're done ---
# For Jira Cloud: use /rest/api/3 (and JIRA_USERNAME=email, JIRA_PASSWORD=API token)
# For Jira Server/Data Center: usually /rest/api/2 (username/password), possibly with /jira context path.
JIRA_URL = os.environ["JIRA_URL"].rstrip("/")          # e.g. https://jira.company.tld or https://jira.company.tld/jira
API_BASE = f"{JIRA_URL}/rest/api/2"                    # <-- change to /api/3 if you're on Cloud
AUTH = (os.environ["JIRA_USERNAME"], os.environ["JIRA_PASSWORD"])
PAGE_SIZE = int(os.getenv("JIRA_PAGE_SIZE", "100"))
TIMEOUT = int(os.getenv("JIRA_TIMEOUT_SEC", "30"))

DEFAULT_JQL = (
    'project = "NTA TPS SM" '
    'AND issuetype = Incident '
    'AND filter = "32233" '
    'AND status in ("In Progress - 2", "In Progress - 3") '
    'AND "Time to resolution" < remaining("1h") '
    'AND cf[18502] = "TO" '
    'AND status CHANGED AFTER -5d'
)
DEFAULT_FIELDS = "key,summary,status,assignee,priority,watches,updated"

def _raise_for_status(r: requests.Response) -> None:
    if r.status_code >= 400:
        try:
            body = r.json()
        except Exception:
            body = r.text
        raise requests.HTTPError(f"{r.status_code} {r.request.method} {r.url}\nBody: {body}")

# ---------------- Public API ----------------
def fetch_all_issues(jql: str = DEFAULT_JQL, fields: str = DEFAULT_FIELDS) -> List[Dict]:
    """Return ALL matching issues (no file writes)."""
    # get total
    r0 = requests.get(f"{API_BASE}/search",
                      params={"jql": jql, "maxResults": 0},
                      auth=AUTH, headers={"Accept": "application/json"},
                      timeout=TIMEOUT)
    _raise_for_status(r0)
    total = int(r0.json().get("total", 0))
    print(f"Total matches: {total}")

    # paginate
    all_issues: List[Dict] = []
    start = 0
    while start < total:
        r = requests.get(f"{API_BASE}/search",
                         params={"jql": jql, "startAt": start, "maxResults": PAGE_SIZE, "fields": fields},
                         auth=AUTH, headers={"Accept": "application/json"},
                         timeout=TIMEOUT)
        _raise_for_status(r)
        chunk = r.json().get("issues", [])
        all_issues.extend(chunk)
        print(f"Fetched {len(chunk)} (so far {len(all_issues)}/{total})")
        if not chunk:
            break
        start += len(chunk)
    return all_issues

def write_issues_csv(issues: List[Dict], csv_path: str = "jira_results.csv") -> None:
    """Write a compact CSV from previously fetched issues."""
    import csv
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["key","summary","status","assignee_displayName","assignee_id_or_name","priority","watchCount","isWatching"])
        for i in issues:
            f = i.get("fields", {})
            a = f.get("assignee") or {}
            assignee_id = a.get("accountId") or a.get("name") or ""
            status_name = (f.get("status") or {}).get("name", "")
            priority_name = (f.get("priority") or {}).get("name", "")
            watches = f.get("watches") or {}
            w.writerow([
                i.get("key",""),
                f.get("summary","") or "",
                status_name,
                a.get("displayName","Unassigned") if a else "Unassigned",
                assignee_id,
                priority_name,
                int(watches.get("watchCount",0)),
                bool(watches.get("isWatching",False)),
            ])
    print(f"Wrote CSV: {csv_path}")

# -------------- Example main --------------
def main():
    jql = os.getenv("JIRA_JQL", DEFAULT_JQL)
    fields = os.getenv("JIRA_FIELDS", DEFAULT_FIELDS)
    issues = fetch_all_issues(jql, fields)
    print(f"Returned {len(issues)} issues.")
    # write_issues_csv(issues, "jira_results.csv")  # call when you want a file

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
