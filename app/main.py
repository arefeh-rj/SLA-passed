# main.py
from app.jira_notify import fetch_all_issues, write_issues_csv
from db.find_users import get_user
from app.jira import fetch_incidents
from app.splus import send_notification


def main():
   
    users_notif=[]
    #fetch incidents
    incidents = fetch_incidents(project_key="NTA TPS SM", lookback_minutes=60)
    for it in incidents:
        # print(it["key"], "→", it["status"], "|", it["summary"], "|",it['accountId'])
        user = get_user(it['accountId'])
        # print(it)
        #fetch users phone number
        if user is not None:
            users_notif.append({'id':it['accountId'],'phone':user['phone_number'],'summery':it['summary'],'time':it['customfield_10303']})

    print(users_notif)
    # for user in users_notif:
    #     send_notification(user['phone'] , user['summery'])
    

if __name__ == "__main__":
    main()
