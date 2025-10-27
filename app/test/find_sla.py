import os, requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.environ["JIRA_URL"].rstrip("/")
USER = os.environ["JIRA_USERNAME"]
PWD  = os.environ["JIRA_PASSWORD"]
# import os, requests
# base = os.environ["JIRA_BASE_URL"].rstrip("/")
# user = os.environ["JIRA_USER_EMAIL"]
# pwd  = os.environ["JIRA_PASSWORD"]

s = requests.Session(); s.auth = (USER, PWD)
r = s.get(f"{BASE}/rest/api/2/field", timeout=30); r.raise_for_status()
for f in r.json():
    print(f"{f['name']:40} -> {f['id']}  |  schema={f.get('schema',{})}")
