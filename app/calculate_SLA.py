import math
import re

WORKDAY_MINUTES = 8*60 + 48      # 528 (8h48m)
WEEK_WORKDAYS   = 6              # <-- Sat–Thu workweek -> yields "1w 4d" for your data
PER_DAY_MS      = WORKDAY_MINUTES * 60 * 1000

def _parse_friendly_to_ms(s: str) -> int:
    h = int(re.search(r'(\d+)\s*h', s).group(1)) if re.search(r'(\d+)\s*h', s) else 0
    m = int(re.search(r'(\d+)\s*m', s).group(1)) if re.search(r'(\d+)\s*m', s) else 0
    return (h*60 + m) * 60 * 1000

def weeks_days_from_sla(sla: dict, include_hours_minutes: bool = False) -> str:
    oc = sla["ongoingCycle"]

    # Preferred: remainingTime.millis
    ms = oc.get("remainingTime", {}).get("millis")
    # Fallback: goal - elapsed
    if ms is None:
        g = oc.get("goalDuration", {}).get("millis")
        e = oc.get("elapsedTime", {}).get("millis")
        if g is not None and e is not None:
            ms = g - e
    # Last resort: parse "friendly"
    if ms is None:
        fr = oc.get("remainingTime", {}).get("friendly")
        if fr:
            ms = _parse_friendly_to_ms(fr)
    if ms is None:
        raise ValueError("Could not determine remaining milliseconds.")

    total_days = ms / PER_DAY_MS
    whole_days = math.floor(total_days)
    weeks = whole_days // WEEK_WORKDAYS
    days  = whole_days %  WEEK_WORKDAYS

    if not include_hours_minutes:
        return f"{weeks}w {days}d"

    rem_minutes = (total_days - whole_days) * WORKDAY_MINUTES
    rh = int(rem_minutes // 60)
    rm = int(round(rem_minutes - rh*60))
    if rm == 60:
        rh += 1; rm = 0
    return f"{weeks}w {days}d {rh}h {rm}m"

# ---- Example with your payload ----
# data = {"id":"644","name":"Time to resolution","_links":{"self":"https://jira.mohaymen.ir/rest/servicedeskapi/request/742858/sla/644"},"completedCycles":[],"ongoingCycle":{"startTime":{"iso8601":"2025-10-15T09:55:04+0330","jira":"2025-10-15T09:55:04.062+0330","friendly":"15/Oct/25 9:55 AM","epochMillis":1760509504062},"breachTime":{"iso8601":"2025-11-10T14:39:43+0330","jira":"2025-11-10T14:39:43.324+0330","friendly":"10/Nov/25 2:39 PM","epochMillis":1762772983324},"breached":False,"paused":False,"withinCalendarHours":True,"goalDuration":{"millis":547200000,"friendly":"152h"},"elapsedTime":{"millis":208301424,"friendly":"57h 51m"},"remainingTime":{"millis":338898576,"friendly":"94h 8m"}}}

# print(weeks_days_from_sla(data))            # -> "1w 4d"  (with WEEK_WORKDAYS = 6)
# print(weeks_days_from_sla(data, True))      # -> "1w 4d 6h 8m"



