import os, requests
from dotenv import load_dotenv 
import json
import re
from datetime import datetime

load_dotenv() 

def convert_duration(duration):
    # Match the pattern: optional minus sign, hours, 'h', optional space, minutes, 'm'
    pattern = r'^(-)?(\d+)h\s*(\d+)m$'
    match = re.match(pattern, duration)
    
    if not match:
        return "Invalid format"
    
    sign = match.group(1) if match.group(1) else ""  # Capture the sign
    hours = int(match.group(2))                     # Extract hours
    minutes = int(match.group(3))                   # Extract minutes
    
    # Calculate days and remaining hours
    days = hours // 24
    remaining_hours = hours % 24
    
    # Build the output string
    result = ""
    if days > 0:
        result += f"{sign}{days}d"
    if remaining_hours > 0 or (days == 0 and minutes == 0):
        result += f"{' ' if result else sign}{remaining_hours}h"
    if minutes > 0:
        result += f"{' ' if result else sign}{minutes}m"
    
    return result or "0h"  # Return "0h" if no duration


def ts_to_epoch(ts: str) -> float | None:
    if not ts:
        return None
    ts = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', ts)
    try:
        return datetime.fromisoformat(ts).timestamp()
    except ValueError:
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(ts, fmt).timestamp()
            except ValueError:
                pass
        return None

def extract_status_changes(histories):
    # print(json.dump(histories))
    """
    histories: the array you showed (issue['changelog']['histories'] or /changelog values)
    returns: list of dicts with when/author/from/to, sorted ascending by time
    # """
    changes = []
    for h in histories or []:
        when = h.get("created")
        who  = (h.get("author") or {}).get("displayName")
        for it in h.get("items", []):
            if it.get("field") == "status":
                    
                changes.append({
                    "when": when,
                    "when_dt": ts_to_epoch(when),
                    "author": who,
                    "from": it.get("fromString"),
                    "to": it.get("toString"),
                })
                # print(json.dumps(changes, indent=2, ensure_ascii=False))
            
    # # sort oldest -> newest
    changes.sort(key=lambda x: x["when_dt"] or datetime.min)
    return changes


def fetch_incidents(notifable: str , max_results: int = 100):
    """
    Basic Auth with user+password (Jira Server/DC; Jira Cloud often DISALLOWS passwords).
    Env needed: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_PASSWORD
    """
    base = os.environ["JIRA_URL"].rstrip("/")
    user = os.environ["JIRA_USERNAME"]
    password = os.environ["JIRA_PASSWORD"]  # <-- password, not API token

    #notify assignee
    if notifable=="assignee":
        jql = (        
             'project = "NTA TPS SM" AND issuetype = Incident '
            'AND filter = "32233" '
            'AND status in ( "In Progress - 2", "In Progress - 3")'
            'AND "Time to resolution" > remaining("4h")'
            'AND labels  in (itsm ,ITSM ,ITSm)'
            'AND assignee != Unassigned' 
        )
    #notify manager
    elif notifable=="manager":
        jql = (        
            'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
            'AND status in ( "In Progress - 2", "In Progress - 3")'
            'AND "Time to resolution" < remaining("1h")'
            'AND labels  in (itsm ,ITSM ,ITSm)'
                
        )
    

    sess = requests.Session()
    sess.auth = (user, password)  # basic auth with password
    sess.headers.update({"Accept": "application/json", "Content-Type": "application/json"})


    resp = sess.post(
        f"{base}/rest/api/2/search",
        json={"jql": jql, "maxResults": max_results,"expand": ["changelog"],
              "fields": ["summary", "status", "updated", "assignee", "reporter", "priority","remaining","customfield_10303", "customfield_17902"]},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    results = []
    for it in data.get("issues", []):
        f = it["fields"]
        
        assignee = f.get("assignee") or {}
        assignee_id = assignee.get("accountId") or assignee.get("name") or ""

        # Extract SLA "Time to resolution"
        sla_field = f.get("customfield_10303", {})

        # print(json.dumps(sla_field, indent=2, ensure_ascii=False))

        histories = (it.get("changelog") or {}).get("histories", [])
        remaining_time_data = sla_field.get("ongoingCycle", {}).get("remainingTime", {})
        friendly_time = remaining_time_data.get("friendly", "N/A")
        
     
    
        results.append({
            "key": it["key"],
            "summary": f.get("summary") or "",
            "status": f["status"]["name"],
            "updated": f.get("updated"),
            "assignee": assignee,
            "accountId": assignee_id,
            "priority": (f.get("priority") or {}).get("name", "Unspecified"),
            "remaining" : f.get("remaining"),
            "SLA": convert_duration(friendly_time) ,
            "NTA TPS CIs": f.get("customfield_17902"),
            "histories": extract_status_changes(histories)
            
        })
    return results

