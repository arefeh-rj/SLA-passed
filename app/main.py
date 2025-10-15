# main.py
from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user


# Optionally override JQL/fields here, or rely on defaults/env
JQL = (
    'project = "NTA TPS SM" '
    'AND issuetype = Incident '
    'AND status in ("In Progress - 2", "In Progress - 3") '
    'AND status CHANGED AFTER -1d'
)
FIELDS = "key,summary,status,assignee,priority,watches,updated"

def main():
    users = get_user('n.dadkhah')
    print(users)
    # issues = fetch_all_issues(jql=JQL, fields=FIELDS)
    # print(issues)
    # print(f"Fetched {len(issues)} issues")
    # If/when you want a file:
    # write_issues_csv(issues, "jira_results.csv")

if __name__ == "__main__":
    main()
