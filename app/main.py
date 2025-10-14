from test import fetch_jira_issues,flatten_issue

# JQL = (
#         'project = "NTA TPS SM" AND issuetype = Incident AND filter = "32233" '
#         'AND status in ("In Progress - 2", "In Progress - 3") '
#         'AND "Time to resolution" < remaining("1h") '
#         'AND cf[18502] = "TO" '
#         'AND status CHANGED AFTER -1d'
#     )

# issues = fetch_jira_issues(JQL, fields=FIELDS, page_size=PAGE_SIZE)

# return flatten_issue(issue)
FIELDS = "key,summary,status,assignee,priority"
PAGE_SIZE = 100
TIMEOUT = 30

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
    print( flatten_issue(issues))


# def run(issues: Iterable[Dict], csv_path: str = "jira_results.csv") -> None:
#     """
#     Write a compact CSV with one row per issue.
#     Pass in the raw issues you got from fetch_jira_issues().
#     """
#     fieldnames = ["key", "summary", "status", "assignee", "priority"]
#     with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
#         w = csv.DictWriter(fh, fieldnames=fieldnames)
#         w.writeheader()
#         for issue in issues:
#             w.writerow(flatten_issue(issue))