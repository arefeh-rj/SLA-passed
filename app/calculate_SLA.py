import math
import re

WORKDAY_MINUTES = 8*60 + 48  # 528 (Persian workday = 8h48m)
WEEK_WORKDAYS   = 5
PER_DAY_MS      = WORKDAY_MINUTES * 60 * 1000  # 31,680,000

def _parse_friendly_to_ms(s: str) -> int:
    """Fallback: parse strings like '97h 58m' -> ms."""
    h = int(re.search(r'(\d+)\s*h', s).group(1)) if re.search(r'(\d+)\s*h', s) else 0
    m = int(re.search(r'(\d+)\s*m', s).group(1)) if re.search(r'(\d+)\s*m', s) else 0
    return (h*60 + m) * 60 * 1000

def weeks_days_from_sla(sla: dict, include_hours_minutes: bool = False) -> str:
    oc = sla["ongoingCycle"]
    # 1) Preferred: remainingTime.millis
    ms = oc.get("remainingTime", {}).get("millis")
    # 2) Fallback: goal - elapsed
    if ms is None:
        g = oc.get("goalDuration", {}).get("millis")
        e = oc.get("elapsedTime", {}).get("millis")
        if g is not None and e is not None:
            ms = g - e
    # 3) Last resort: parse the friendly string
    if ms is None:
        fr = oc.get("remainingTime", {}).get("friendly")
        if fr:
            ms = _parse_friendly_to_ms(fr)
    if ms is None:
        raise ValueError("Could not determine remaining milliseconds from SLA JSON.")

    total_days = ms / PER_DAY_MS
    whole_days = math.floor(total_days)
    weeks = whole_days // WEEK_WORKDAYS
    days  = whole_days %  WEEK_WORKDAYS

    if not include_hours_minutes:
        return f"{weeks}w {days}d"

    # leftover within the next workday
    rem_minutes = (total_days - whole_days) * WORKDAY_MINUTES
    rh = int(rem_minutes // 60)
    rm = int(round(rem_minutes - rh*60))
    if rm == 60:
        rh += 1; rm = 0
    return f"{weeks}w {days}d {rh}h {rm}m"
