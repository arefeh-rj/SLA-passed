import os, requests
from dotenv import load_dotenv 
# import json
# import csv

load_dotenv() 

# BASE = os.environ["JIRA_URL"]
# AUTH = (os.environ["JIRA_USERNAME"], os.environ["JIRA_PASSWORD"])  # <-- same vars you already have

# JQL = (
#     'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
#     'AND status in ( "In Progress - 2", "In Progress - 3")'
#     'AND "Time to resolution" < remaining("1h")'
#     'AND cf[18502] = "TO" '
#     'AND status CHANGED AFTER -5d'
# )

# FIELDS = "key,summary,status,assignee,priority,assignee"
# PAGE_SIZE = 100

# s = requests.Session()
# s.auth = AUTH
# s.headers["Accept"] = "application/json"

# # 1) Get total count
# r0 = s.get(f"{BASE}/rest/api/2/search", params={"jql": JQL, "maxResults": 0})
# r0.raise_for_status()
# total = r0.json()["total"]
# print("Total matches:", total)

# # 2) Collect all issues (paginated)
# all_issues = []
# start = 0
# while start < total:
#     r = s.get(
#         f"{BASE}/rest/api/2/search",
#         params={"jql": JQL, "startAt": start, "maxResults": PAGE_SIZE, "fields": FIELDS},
#         timeout=30,
#     )
#     r.raise_for_status()
#     chunk = r.json().get("issues", [])
#     all_issues.extend(chunk)
#     print(f"Fetched {len(chunk)} (total so far {len(all_issues)}/{total})")
#     if not chunk:
#         break
#     start += len(chunk)

# # 3) Write a compact CSV (one row per issue)
# with open("jira_results.csv", "w", newline="", encoding="utf-8-sig") as fh:
#     w = csv.writer(fh)
#     w.writerow(["key", "summary", "status", "assignee", "priority","assignee_id","isWatching"])
#     for i in all_issues:
#         f = i.get("fields", {})
#         assignee = f.get("assignee") or {}
#         assignee_id = assignee.get("accountId") or assignee.get("name") or ""
#         status_name = (f.get("status") or {}).get("name", "")
#         priority_name = (f.get("priority") or {}).get("name", "")
#         watches = f.get("watches") or {}
#         w.writerow([
#             i.get("key", ""),
#             f.get("summary", "") or "",
#             status_name,
#             assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
#             assignee_id,
#             priority_name,
#             watches.get("watchCount", 0),
#             watches.get("isWatching", False),
#         ])


# # with open("jira_results.json", "w", encoding="utf-8") as fh:
# #     json.dump(all_issues, fh, ensure_ascii=False, indent=2)
# # print("Wrote JSON: jira_results.json")

# print("Wrote CSV: jira_results.csv")

# jira_simple.py
# jira_simple.py
# import os
# import requests
def parse_jsm_sla(val):
    # returns {'remaining_minutes': int|None, 'breached': bool|None, 'state': 'ongoing|completed|missing'}
    if not isinstance(val, dict):
        return {"remaining_minutes": None, "breached": None, "state": "missing"}

    oc = val.get("ongoingCycle") or {}
    if oc:
        rem_ms = (oc.get("remainingTime") or {}).get("millis")
        if rem_ms is not None:
            mins = int(rem_ms // 60000)
            breached = oc.get("breached", mins < 0)
            return {"remaining_minutes": mins, "breached": breached, "state": "ongoing"}

    cycles = val.get("completedCycles") or []
    if cycles:
        last = cycles[-1]
        goal = (last.get("goalDuration") or {}).get("millis")
        elapsed = (last.get("elapsedTime") or {}).get("millis")
        rem_ms = (goal - elapsed) if (goal is not None and elapsed is not None) else None
        mins = None if rem_ms is None else int(rem_ms // 60000)
        return {"remaining_minutes": mins, "breached": last.get("breached"), "state": "completed"}

    return {"remaining_minutes": None, "breached": None, "state": "missing"}


def fetch_incidents(project_key: str, lookback_minutes: int = 15, max_results: int = 100):
    """
    Basic Auth with user+password (Jira Server/DC; Jira Cloud often DISALLOWS passwords).
    Env needed: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_PASSWORD
    """
    base = os.environ["JIRA_URL"].rstrip("/")
    user = os.environ["JIRA_USERNAME"]
    password = os.environ["JIRA_PASSWORD"]  # <-- password, not API token

  
    jql = (
        # f'project = {project_key} '
        # f'AND issuetype = Incident '
        # f'AND status CHANGED AFTER -{lookback_minutes}m '
        # f'ORDER BY updated DESC'
        
        'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
        'AND status in ( "In Progress - 2", "In Progress - 3")'
        'AND "Time to resolution" < remaining("1h")'
        'AND cf[18502] = "TO" '
        'AND status CHANGED AFTER -7d'
    )
    

    sess = requests.Session()
    sess.auth = (user, password)  # basic auth with password
    sess.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    SLA_FIELD_ID = "customfield_19200"

    resp = sess.post(
        f"{base}/rest/api/2/search",
        json={"jql": jql, "maxResults": max_results,
              "fields": ["summary", "status", "updated", "assignee", "reporter", "priority","remaining","customfield_10303"]},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    results = []
    for it in data.get("issues", []):
        f = it["fields"]
        # print(f)
        owner = f.get("assignee") or f.get("reporter") or {}
        assignee = f.get("assignee") or {}
        assignee_id = assignee.get("accountId") or assignee.get("name") or ""

    # Extract SLA "Time to resolution"
        sla_field = f.get("customfield_10303", {})
        
        # Debug: Log the raw SLA field
        # print(f"Issue {it['key']}: SLA field = {sla_field}")
        
        remaining_time_data = sla_field.get("ongoingCycle", {}).get("remainingTime", {})
        millis = remaining_time_data.get("millis", None)
        friendly_time = remaining_time_data.get("friendly", "N/A")
        
        # Convert to days if absolute value >24 hours and millis is valid
        if isinstance(millis, (int, float)) and abs(millis) > 86400000:  # 24 hours = 86,400,000 ms
            days = millis / (1000 * 60 * 60 * 24)  # Convert milliseconds to days
            remaining_time = f"{days:.2f} days"  # Show positive or negative days
        elif isinstance(millis, (int, float)) and millis < 0:
            remaining_time = "Breached"  # Optional: Show "Breached" for negative times
        else:
            remaining_time = friendly_time  # Use friendly format or "N/A"    
    
        results.append({
            "key": it["key"],
            "summary": f.get("summary") or "",
            "status": f["status"]["name"],
            "updated": f.get("updated"),
            "assignee": assignee,
            "accountId": assignee_id,
            "priority": (f.get("priority") or {}).get("name", "Unspecified"),
            "remaining" : f.get("remaining"),
            "customfield_10303": remaining_time 
            
            # "url": f"{base}/browse/{it['key']}",
        })
    return results

