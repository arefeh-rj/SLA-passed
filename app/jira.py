import os, requests
from dotenv import load_dotenv 
import json
import csv

load_dotenv() 

BASE = os.environ["JIRA_URL"]
AUTH = (os.environ["JIRA_USERNAME"], os.environ["JIRA_PASSWORD"])  # <-- same vars you already have

JQL = (
    'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
    'AND status in ( "In Progress - 2", "In Progress - 3")'
    'AND "Time to resolution" < remaining("1h")'
    'AND cf[18502] = "TO" '
    'AND status CHANGED AFTER -1d'
)

FIELDS = "key,summary,status,assignee,priority"
PAGE_SIZE = 100

s = requests.Session()
s.auth = AUTH
s.headers["Accept"] = "application/json"

# 1) Get total count
r0 = s.get(f"{BASE}/rest/api/2/search", params={"jql": JQL, "maxResults": 0})
r0.raise_for_status()
total = r0.json()["total"]
print("Total matches:", total)

# 2) Collect all issues (paginated)
all_issues = []
start = 0
while start < total:
    r = s.get(
        f"{BASE}/rest/api/2/search",
        params={"jql": JQL, "startAt": start, "maxResults": PAGE_SIZE, "fields": FIELDS},
        timeout=30,
    )
    r.raise_for_status()
    chunk = r.json().get("issues", [])
    all_issues.extend(chunk)
    print(f"Fetched {len(chunk)} (total so far {len(all_issues)}/{total})")
    if not chunk:
        break
    start += len(chunk)

# 3) Write a compact CSV (one row per issue)
with open("jira_results.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["key", "summary", "status", "assignee", "priority"])
    for i in all_issues:
        f = i["fields"]
        w.writerow([
            i["key"],
            f.get("summary", ""),
            (f.get("status") or {}).get("name", ""),
            (f.get("assignee") or {}).get("displayName", "Unassigned"),
            (f.get("priority") or {}).get("name", ""),
        ])
print("Wrote CSV: jira_results.csv")

# # 4) Also write raw JSON (full fields you requested)
# with open("jira_results.json", "w", encoding="utf-8") as fh:
#     json.dump(all_issues, fh, ensure_ascii=False, indent=2)
# print("Wrote JSON: jira_results.json")

