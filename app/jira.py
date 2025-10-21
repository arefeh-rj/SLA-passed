import os, requests
from dotenv import load_dotenv 
import json
import re

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


def fetch_incidents(project_key: str, lookback_minutes: int = 15, max_results: int = 100):
    """
    Basic Auth with user+password (Jira Server/DC; Jira Cloud often DISALLOWS passwords).
    Env needed: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_PASSWORD
    """
    base = os.environ["JIRA_URL"].rstrip("/")
    user = os.environ["JIRA_USERNAME"]
    password = os.environ["JIRA_PASSWORD"]  # <-- password, not API token

  
    jql = (        
        'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
        'AND status in ( "In Progress - 2", "In Progress - 3")'
        'AND "Time to resolution" < remaining("1h")'
        'AND cf[18502] = "TO" '
        # 'AND status CHANGED AFTER -7d'

        # project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" 
        # AND status in ( "In Progress - 2", "In Progress - 3")
        # AND "Time to resolution" < remaining("1h")
        # AND cf[18502] = "TO"  AND assignee != Unassigned
    )
    

    sess = requests.Session()
    sess.auth = (user, password)  # basic auth with password
    sess.headers.update({"Accept": "application/json", "Content-Type": "application/json"})


    resp = sess.post(
        f"{base}/rest/api/2/search",
        json={"jql": jql, "maxResults": max_results,
              "fields": ["summary", "status", "updated", "assignee", "reporter", "priority","remaining","customfield_10303", "customfield_17902"]},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    results = []
    for it in data.get("issues", []):
        f = it["fields"]
        
        owner = f.get("assignee") or f.get("reporter") or {}
        assignee = f.get("assignee") or {}
        assignee_id = assignee.get("accountId") or assignee.get("name") or ""

        # Extract SLA "Time to resolution"
        sla_field = f.get("customfield_10303", {})

        # print(json.dumps(sla_field, indent=2, ensure_ascii=False))

        
        remaining_time_data = sla_field.get("ongoingCycle", {}).get("remainingTime", {})
        # millis = remaining_time_data.get("millis", None)
        friendly_time = remaining_time_data.get("friendly", "N/A")
        
        # Convert to days if absolute value >24 hours and millis is valid
        # if isinstance(millis, (int, float)) and abs(millis) > 86400000:
        #     days = millis // (1000 * 60 * 60 * 24)
        #     hours = (abs(millis) % (1000 * 60 * 60 * 24)) // (1000 * 60 * 60)
        #     remaining_time = f"{'' if millis < 0 else ''}{int(days)} days {hours}h"  
    
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
            "NTA TPS CIs": f.get("customfield_17902")
            # "millis" : remaining_time
            
        })
    return results

